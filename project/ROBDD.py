from functools import lru_cache
from typing import List
# Define constants for operators
OP_NOT = 'not'
OP_AND = 'and'
OP_OR = 'or'

def op_not(x:int, y:int) -> int:
    return 1 if not x else 0

def op_and(x:int, y:int):
    return 1 if x and y else 0

def op_or(x:int, y:int):
    return 1 if x or y else 0

OPERATIONS = {
    OP_NOT: op_not,
    OP_AND: op_and,
    OP_OR: op_or
}

class Node:
    __slots__ = ['var', 'low', 'high', 'terminal']

    def __init__(self, var, low, high):
        self.var: int | str = var
        self.low: Node = low
        self.high: Node = high
        self.terminal: bool = var in (0, 1)

    def __repr__(self) -> str:
        return f"Node({self.var})"


class ROBDD:
    __slots__ = ['root', 'variables', 'operation_cache', 'unique_table']

    def __init__(self):
        self.root: Node = None
        self.variables: List[str] = []
        self.unique_table: dict = {}
        self.operation_cache: dict = {}

    def clear(self):
        self.root = None
        self.variables = []
        self.operation_cache = {}
        self.unique_table = {}


    def build(self, expression, variables, reduce=True):
        self.clear()
        self.variables = variables
        self.root = self._build_recursive(expression)
        if reduce: self.reduce()
        return self
    
    @lru_cache(maxsize=None, typed=False)
    def _build_recursive(self, expression):
        # Base cases
        if isinstance(expression, str):
            # if the expression is a varaible then the node is a terminal node
            if expression in self.variables:
                return self.mk(expression, self.mk(0, None, None), self.mk(1, None, None))
            elif expression in ('True', 'False'):
                return self.mk(1 if expression == 'True' else 0, None, None)
            else:
                raise ValueError(f"Unknown variable or constant: {expression}")
        
        # if the expression is a tuple then it is a logical operation with
        # the first element being the operator and the rest being the operands
        op = expression[0]
    
        
        result = self._build_recursive(expression[1])
        if op == 'not':
            return self.apply(op_not, result, result)

        for sub_expr in expression[2:]:
            sub_node = self._build_recursive(sub_expr)
            result = self.apply(OPERATIONS[op], result, sub_node)
        
        return result
    
    def mk(self, var, low, high):
        key = (var, id(low), id(high))
        if key not in self.unique_table:
            self.unique_table[key] = Node(var, low, high)
        return self.unique_table[key]

    def apply(self, op, g1, g2):
        def apply_recursive(n1, n2):
            if n1.terminal and n2.terminal:
                return self.mk(op(n1.var, n2.var), None, None)
            
            key = (id(n1), id(n2), op)
            if key in self.operation_cache:
                return self.operation_cache[key]
            
            # Directly compare variable indices
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

    # TODO:
    @lru_cache(maxsize=None, typed=False)
    def _reduce_recursive(self, node):
        if node is None or node.terminal:
            return node

        low = self._reduce_recursive(node.low)
        high = self._reduce_recursive(node.high)

        if low == high:
            return low

        if low.terminal and high.terminal and low.var == high.var:
            return low

        return self.mk(node.var, low, high)



    def _clean_unique_table(self):
        new_unique_table = {}
        self._mark_reachable_nodes(self.root, new_unique_table)
        self.unique_table = new_unique_table


    # TODO: This is a bit of a hack, we should probably use a proper graph traversal algorithm to mark all reachable nodes
    def _mark_reachable_nodes(self, node, new_table):
        if node is None or node in new_table.values():
            return
        if not node.terminal:
            key = (node.var, id(node.low), id(node.high))
            new_table[key] = node
            self._mark_reachable_nodes(node.low, new_table)
            self._mark_reachable_nodes(node.high, new_table)


    def evaluate(self, var_assignment:dict) -> int:
        """
        Inputs:
            var_assignment: dict, a dictionary with the variable name and the assigned value
        Outputs:
            int, the result of the evaluation of the ROBDD. Either 0 or 1
        """
        node = self.root
        # Create a closure to get the assigned value for a variable
        get = var_assignment.get
        while not node.terminal:
            # extract what the assigned value for the current node is
            if get(node.var):
                node = node.high # go to the high branch if the value is True
            else:
                node = node.low
        
        return node.var
        

    
    def show(self):
        if self.root is None:
            raise ValueError("ROBDD is empty. Build a ROBDD first.")

        print(" ".join(self.variables) + " | Result")
        print("-" * (len(self.variables) * 2 + 8))
        self._show_recursive(self.root, {}, 0)

    def _show_recursive(self, node, assignment, var_index):
        if var_index == len(self.variables):
            # We've assigned all variables, evaluate the ROBDD
            result = self._evaluate(self.root, assignment)
            assignment_str = " ".join(str(int(assignment[var])) for var in self.variables)
            print(f"{assignment_str} | {result}")
            return

        # Assign 0 to the current variable
        assignment[self.variables[var_index]] = False
        self._show_recursive(node, assignment, var_index + 1)

        # Assign 1 to the current variable
        assignment[self.variables[var_index]] = True
        self._show_recursive(node, assignment, var_index + 1)

        # Backtrack
        del assignment[self.variables[var_index]]

    def _evaluate(self, node, assignment):
        while not node.terminal:
            if assignment[node.var]:
                node = node.high
            else:
                node = node.low
        return node.var


    def show_ones(self):
        print(" ".join(self.variables))
        print("-" * (len(self.variables) * 2 - 1))
        self._show_ones_recursive(self.root, {}, 0, debug_level=0)


    def _show_ones_recursive(self, node, assignment, var_index, debug_level=0):
#        indent = "  " * debug_level
#        print(f"{indent}Visiting node: {node.var}, var_index: {var_index}")
        
        if node.var == '1':
#            print(f"{indent}Found 1-terminal, printing assignment:")
            self._print_assignments(assignment, var_index)
            return
        if node.var == '0':
#            print(f"{indent}Found 0-terminal, backtracking")
            return

        current_var_index = self.variables.index(node.var)
#        print(f"{indent}Current variable: {node.var}, index: {current_var_index}")

        # Handle skipped variables
        for i in range(var_index, current_var_index):
#            print(f"{indent}Assigning 0 to skipped variable: {self.variables[i]}")
            assignment[self.variables[i]] = 0
        
#        print(f"{indent}Exploring low branch (0) for {node.var}")
        assignment[node.var] = 0
        self._show_ones_recursive(node.low, assignment, current_var_index + 1, debug_level + 1)

        #print(f"{indent}Exploring high branch (1) for {node.var}")
        assignment[node.var] = 1
        self._show_ones_recursive(node.high, assignment, current_var_index + 1, debug_level + 1)

#        print(f"{indent}Backtracking: removing assignments from {var_index} to {current_var_index}")
        for i in range(var_index, current_var_index + 1):
            del assignment[self.variables[i]]

    def _print_assignments(self, assignment, start_index):
        if start_index == len(self.variables):
            print(" ".join(str(int(assignment.get(var, 0))) for var in self.variables))
            return

        assignment[self.variables[start_index]] = 0
        self._print_assignments(assignment, start_index + 1)
        assignment[self.variables[start_index]] = 1
        self._print_assignments(assignment, start_index + 1)
        del assignment[self.variables[start_index]]
    
    def print_robdd(self):
        print("ROBDD Structure:")
        if self.root is None:
            print("Empty ROBDD")
            return

        def print_recursive(node, prefix="", is_left=True):
            if node.var in ('0', '1'):  # Terminal node
                print(f"{prefix}{'└── ' if is_left else '┌── '}[{node.var}]")
                return

            print(f"{prefix}{'└── ' if is_left else '┌── '}{node.var}")

            new_prefix = prefix + ("    " if is_left else "│   ")

            # Print the high branch first (going right in the visualization)
            print_recursive(node.high, new_prefix, False)
            
            # Then print the low branch
            print_recursive(node.low, new_prefix, True)

        print_recursive(self.root, "", True)


def debug_show_ones(expression, variables):
    robdd = ROBDD()
    robdd.build(expression, variables)
    
    print("Non-reduced ROBDD show_ones:")
    robdd.show_ones(use_reduced=False)
    
    print("\nReduced ROBDD show_ones:")
    robdd.show_ones(use_reduced=True)

## Example usage
#expression = ('or', ('and', 'x', ('not', 'y')), ('and', ('and', 'y', 'z'), ('not', 'x')), ('and', 'w', ('not', 'z')))
#variables = ['x', 'y', 'z', 'w']
#
#
#expression = (
#    'or',
#    ('and', 'x1', ('not', 'x2')),
#    ('and', ('or', 'x3', ('not', 'x4')), ('and', 'x5', ('not', 'x6'))),
#    ('or', 
#        ('and', 'x7', ('not', 'x8')),
#        ('and', ('or', 'x9', ('not', 'x10')), ('and', 'x11', ('not', 'x12')))
#    ),
#    ('and', 
#        ('or', 'x13', ('not', 'x14')),
#        ('and', ('or', 'x15', ('not', 'x16')), ('and', 'x17', ('not', 'x18')))
#    ),
#    ('or', 
#        ('and', 'x19', ('not', 'x20')),
#        ('and', ('or', 'x21', ('not', 'x22')), ('and', 'x23', ('not', 'x24')))
#    ),
#    ('and', 
#        ('or', 'x25', ('not', 'x26')),
#        ('and', ('or', 'x27', ('not', 'x28')), ('and', 'x29', ('not', 'x30')))
#    )
#)
#variables = [f'x{i}' for i in range(1, 24)]
#
#
#debug_show_ones(expression, variables)


#if __name__=="__main__":
#    test_case_4 = ('or', 'x', 'y', 'z')
#    variables_4 = ['x', 'y', "z"]
#    expression = (
#        'or',
#        ('and', 'x', ('not', 'y')),
#        ('and', ('and', 'y', 'z'), ('not', 'x')),
#        ('and', 'w', ('not', 'z'))
#    )
#    variables = ['x', 'y', 'z', 'w']
#
#    #print("Test Case 4:", test_case_4)
#    robdd = ROBDD()
#    robdd.build(expression, variables, reduce=False)
#    print()
#    robdd.show_ones()