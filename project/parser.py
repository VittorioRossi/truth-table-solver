from pprint import pprint
from project.tokenizer import Tokenizer
from typing import List, Tuple, Any, Dict

def match(token, type, value = None):
    if value is None:
        return token.type == type
    return token.type == type and token.value == value

def match_bool(token):
    return token.type == 'KEYWORD' and token.value in {'True', 'False'}

def end_of_line(token):
    return match(token, 'SPECIAL', ';')

def tokens_to_robdd_input(tokens: List, start_index: int = 0) -> Tuple[Any, int]:
    """
    Parses tokens into ROBDD input format.
    Assumes precedence is always given by parentheses.
    Allows multiple operators within the same parenthesis level.
    Detects and reports errors for incorrect parentheses usage.
    
    Example of valid input: ((x1 or x2) and (not x3)) or x4
    """
    i = start_index
    expression: List = []
    current_term: List = []
    last_operator = None
    expect_operator = False

    def finalize_term():
        nonlocal current_term, expect_operator
        if len(current_term) == 1:
            expression.append(current_term[0])
        elif len(current_term) > 1:
            expression.extend(current_term)
        current_term = []
        expect_operator = True

    while i < len(tokens):
        token = tokens[i]

        if match(token, 'SPECIAL', '('):
            if expect_operator:
                raise ValueError(f"Unexpected opening parenthesis at line {i}. Did you forget an operator?")
            sub_expression, i = tokens_to_robdd_input(tokens, i + 1)
            current_term.append(sub_expression)
            expect_operator = True
        
        elif match(token, 'SPECIAL', ')'):
            finalize_term()
            break
        
        elif match(token, 'KEYWORD', 'not'):
            if expect_operator:
                raise ValueError(f"Unexpected 'not' at line {i}. Did you forget an operator?")
            
            if i + 1 < len(tokens):
                next_token = tokens[i + 1]
                if match(next_token, 'SPECIAL', '('):
                    sub_expression, i = tokens_to_robdd_input(tokens, i + 2)
                    current_term.append(('not', sub_expression))
                elif match(next_token, 'IDENTIFIER'):
                    current_term.append(('not', next_token.value))
                    i += 1
                elif match_bool(next_token):
                    current_term.append(('not', next_token.value))
                    i += 1
                else:
                    raise ValueError(f"Unexpected token after 'not' at line {token.line + 1}, character {token.column+1}")
            else:
                raise ValueError(f"Unexpected end of input after 'not' at line {token.line + 1}, character {token.column+1}")
            expect_operator = True
        
        elif match(token, 'KEYWORD', 'or') or match(token, 'KEYWORD', 'and'):
            if not expect_operator:
                raise ValueError(f"Unexpected operator '{token.value}' at line {token.line + 1}, character {token.column+1}. Did you forget an identifier?")
            if last_operator and last_operator != token.value:
                raise ValueError(f"Unexpected operator '{token.value}' at line {token.line + 1}, character {token.column+1}. Expected '{last_operator}'")
            last_operator = token.value
            expect_operator = False

        elif match(token, 'IDENTIFIER'):
            if expect_operator:
                raise ValueError(f"Unexpected identifier '{token.value}' at line {token.line + 1}, character {token.column+1}. Did you forget an operator?")
            current_term.append(token.value)
            expect_operator = True

        elif match_bool(token):
            if expect_operator:
                raise ValueError(f"Unexpected keyword '{token.value}' at line {token.line + 1}, character {token.column+1}. Did you forget an operator?")
            current_term.append(token.value)
            expect_operator = True
        
        elif match(token, 'SPECIAL', ';'):
            finalize_term()
            break
        
        else:
            raise ValueError(f"Unexpected token {token} at line {token.line + 1}, character {token.column+1}")
        
        i += 1
    
    finalize_term()
    
    if last_operator:
        return (last_operator,) + tuple(expression), i
    elif len(expression) == 1:
        return expression[0], i
    else:
        return tuple(expression), i

def parse_assignment(tokens, current, variables, assignments):
    current_token = tokens[current]
    name = current_token.value
    idx = current + 1
    
    if not match(tokens[idx], 'SPECIAL', '='):
        raise ValueError(f"Expected '=' after identifier at line {current_token.line}, column {current_token.column}")
    
    idx += 1
    expr, idx = tokens_to_robdd_input(tokens, idx)
    

    # Use sets for faster membership testing
    variable_set = set(variables)
    assignment_set = set(assignments.keys())
    keywords = {"and", "or", "not", "True", "False"}

    def replace_and_check(node):
        if isinstance(node, str):
            if node in keywords:
                return node
            if node not in variable_set and node not in assignment_set:
                raise ValueError(f"Variable or identifier {node} in expression for {name} is not declared.")
            return assignments.get(node, node)
        elif isinstance(node, tuple):
            return tuple(replace_and_check(child) for child in node)
        else:
            return node

    # Replace identifiers with their trees and check for undeclared variables in one pass
    expr = replace_and_check(expr)

    assignments[name] = expr
    variables.append(name)  # f0 needs to be treated as a variable

    return idx + 1



def parse(file):
    tokenizer = Tokenizer() # Tokenizer object
    tokens = tokenizer.tokenize(file) # List of tokens

    current = 0 # Index of the current token
    
    
    variables = [] # Set of variable names
    assignments = {} # Dictionary of variable assignments
    show_instructions = {"show":[], "show_ones":[]} # List of show instructions

    while current < len(tokens):
        current_token = tokens[current]
        # if the token is a var we want to get the following tokens until we find a ';'
        if match(current_token, 'KEYWORD', 'var'):
            idx = current + 1 # Skip the 'var' keyword
            while not end_of_line(tokens[idx]):
                if match(tokens[idx], 'IDENTIFIER'):
                    variables.append(tokens[idx].value)
                else:
                    raise ValueError(f"Expected identifier after 'var' at line {current_token.line}, column {current_token.column}")
                idx += 1
            current = idx + 1
        elif match(current_token, 'KEYWORD', 'show') or match(current_token, 'KEYWORD', 'show_ones'):
            show_type = current_token.value
            idx = current + 1
            identifiers = []
            while not end_of_line(tokens[idx]):
                if match(tokens[idx], 'IDENTIFIER'):
                    tok_val = tokens[idx].value
                    if tok_val not in variables and tok_val not in assignments.keys():
                        raise ValueError(f"Identifier {tok_val} in instruction of type \"show\" is not declared")
                    identifiers.append(tok_val)
                else:
                    raise ValueError(f"Expected identifier or variable after 'show' at line {current_token.line}, column {current_token.column}")
                idx += 1
            show_instructions[show_type].extend(identifiers)
            current = idx + 1
        elif match(current_token, 'IDENTIFIER'):
            current = parse_assignment(tokens, current, variables, assignments)
    
    return variables, assignments, show_instructions


if __name__ == "__main__":
    with open('./hw01_instances/random0000.txt', 'r') as file:
        text = file.read()
    text = """# We declare two variables: x and y
var a b c d e f g h i;
# We assign (x xor y) to z
z =  b or ((a or b) and c) and h;
# We show the truth table of z
show z;"""
    variables, assignments, show_instructions = parse(text)
    pprint(variables)
    pprint(assignments)
    pprint(show_instructions)