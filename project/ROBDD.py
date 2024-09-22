from functools import lru_cache
from time import time

# Define constants for operators
OP_NOT = 'not'
OP_AND = 'and'
OP_OR = 'or'

class Node:
    _id_counter = 0
    __slots__ = ['var', 'low', 'high', 'id']
    def __init__(self, var, low, high):
        self.var = var
        self.low = low
        self.high = high
        self.id = Node._id_counter
        Node._id_counter += 1

    @classmethod
    def reset_id_counter(cls):
        cls._id_counter = 0

    def is_terminal(self):
        return self.low is None and self.high is None

    def __repr__(self):
        return f"Node({self.var})"
    

def op_not(x, y):
    return '1' if x == '0' else '0'

def op_and(x, y):
    return '1' if x == '1' and y == '1' else '0'

def op_or(x, y):
    return '1' if x == '1' or y == '1' else '0'

class ROBDD:
    __slots__ = ['root', 'variables', 'operation_cache', 'unique_table']
    def __init__(self):
        self.root = None
        self.variables = []
        self.unique_table = {}
        self.operation_cache = {}
        Node.reset_id_counter()

    def clear(self):
        self.root = None
        self.variables = []
        self.operation_cache = {}
        self.unique_table = {}
        Node.reset_id_counter()

    def build(self, expression, variables):
        self.clear()
        self.variables = variables

        time1 = time()
        self.root = self._build_recursive(expression)
        print(f"Build time: {time() - time1:.2f}s")

        time2 = time()
        self.reduce()
        print(f"Reduce time: {time() - time2:.2f}s")
        return self
    
    @lru_cache(maxsize=None, typed=False)
    def _build_recursive(self, expression):
        # Base cases
        if isinstance(expression, str):
            if expression in self.variables:
                return self.mk(expression, self.mk('0', None, None), self.mk('1', None, None))
            elif expression in ('True', 'False'):
                return self.mk('1' if expression == 'True' else '0', None, None)
            else:
                raise ValueError(f"Unknown variable or constant: {expression}")
        
        # Recursive cases
        elif isinstance(expression, tuple):
            op = expression[0]
            if op == 'not':
                sub_node = self._build_recursive(expression[1])
                return self.apply(op_not, sub_node, sub_node)
            elif op in ('and', 'or'):
                result = self._build_recursive(expression[1])
                for sub_expr in expression[2:]:
                    sub_node = self._build_recursive(sub_expr)
                    result = self.apply(op_and if op == 'and' else op_or, result, sub_node)
                return result
            else:
                raise ValueError(f"Unknown operation: {expression}")
        else:
            raise ValueError(f"Invalid expression type: {type(expression)}")

    def mk(self, var, low, high):
        key = (var, id(low), id(high))
        if key not in self.unique_table:
            self.unique_table[key] = Node(var, low, high)
        return self.unique_table[key]

    def apply(self, op, g1, g2):
        def apply_recursive(n1, n2):
            if n1.is_terminal() and n2.is_terminal():
                return self.mk(op(n1.var, n2.var), None, None)
            
            key = (id(n1), id(n2), op)
            if key in self.operation_cache:
                return self.operation_cache[key]
            
            var = min(n1.var, n2.var, key=lambda x: self.variables.index(x) if x in self.variables else float('inf'))
            
            low1, high1 = (n1.low, n1.high) if var == n1.var else (n1, n1)
            low2, high2 = (n2.low, n2.high) if var == n2.var else (n2, n2)

            low = apply_recursive(low1, low2)
            high = apply_recursive(high1, high2)

            result = self.mk(var, low, high)
            self.operation_cache[key] = result
            return result
    
        return apply_recursive(g1, g2)


    def reduce(self):
        self.root = self._reduce_recursive(self.root)
        self._clean_unique_table()

    def _reduce_recursive(self, node):
        if node is None or node.is_terminal():
            return node

        low = self._reduce_recursive(node.low)
        high = self._reduce_recursive(node.high)

        if low == high:
            return low

        if low.is_terminal() and high.is_terminal() and low.var == high.var:
            return low

        return self.mk(node.var, low, high)

    def _clean_unique_table(self):
        new_unique_table = {}
        self._mark_reachable_nodes(self.root, new_unique_table)
        self.unique_table = new_unique_table

    def _mark_reachable_nodes(self, node, new_table):
        if node is None or node in new_table.values():
            return
        if not node.is_terminal():
            key = (node.var, id(node.low), id(node.high))
            new_table[key] = node
            self._mark_reachable_nodes(node.low, new_table)
            self._mark_reachable_nodes(node.high, new_table)

    def __call__(self, var_assignment):
        node = self.root
        get = var_assignment.get
        while not node.is_terminal():
            # extract what the assigned value for the current node is
            if get(node.var):
                node = node.high # go to the high branch if the value is True
            else:
                node = node.low
        return node.var
    
    def find_paths_to_one(self, node, path=None, assignments=None):
        if path is None:
            path = []
        if assignments is None:
            assignments = []
        
        if node is None:
            return assignments

        if node.var == 1:
            # We've reached a terminal 1 node, add this path to assignments
            assignments.append(path)
            return assignments
        elif node.var == 0:
            # We've reached a terminal 0 node, this path doesn't lead to 1
            return assignments
        
        # Recursive case: non-terminal node
        # Follow high branch (var = True)
        self.find_paths_to_one(node.high, path + [(node.var, True)], assignments)
        
        # Follow low branch (var = False)
        self.find_paths_to_one(node.low, path + [(node.var, False)], assignments)
        
        return assignments
    
    def show_ones(self, declared_vars):
        """
        Generate truth table rows for satisfying assignments.
        """
        satisfying_assignments = self.find_paths_to_one(self.root)
        print(f"Number of satisfying assignments: {len(satisfying_assignments)}")
        print("Satisfying assignments:")
        for assignment in satisfying_assignments:
            print(assignment)

        rows = []
        for assignment in satisfying_assignments:
            row = [str(int(assignment.get(var, False))) for var in declared_vars]
            rows.append(" ".join(row))
        
        return rows
    
    def print_robdd(self):
        print("ROBDD:")
        def print_recursive(node, indent=0):
            print("  " * indent + str(node))
            if not node.is_terminal():
                print_recursive(node.low, indent + 1)
                print_recursive(node.high, indent + 1)

        print_recursive(self.root)


if __name__=="__main__":
    test_case_4 = ('or', 'x', 'y', 'z')
    variables_4 = ['x', 'y', "z"]

    #print("Test Case 4:", test_case_4)
    robdd = ROBDD()
    robdd.build(test_case_4, variables_4)
    robdd.show_ones(variables_4)
    robdd.print_robdd()