from project.parser import parse
from project.ROBDD import ROBDD

def test_robdd():
    with open('./hw01_instances/ag10_00.txt') as f:
        file_content = f.read()

    variables, assignments, show_instructions = parse("var x y; z = y and x;show z;")
    # Assume 'file_content' contains the input text
    print(assignments)
    robdd = ROBDD()
    for var_name, expression in assignments.items():
        robdd.build(expression, variables)

        print(var_name)
        print(robdd.root)

def test_robdd_reduction(expression, variables):
    robdd = ROBDD()
    result = robdd.build(expression, variables)
    print(f"Expression: {expression}")
    print(f"Reduced ROBDD: {result.root}")
    print()

def test_robdd_reduction_test_cases():
    # Test Case 1: (a AND b) OR (NOT a AND c)
    test_case_1 = ('or', ('and', 'a', 'b'), ('and', ('not', 'a'), 'c'))
    variables_1 = ['a', 'b', 'c']

    # Test Case 2: (a OR b) AND (b OR c) AND (c OR a)
    test_case_2 = ('and', ('or', 'a', 'b'), ('and', ('or', 'b', 'c'), ('or', 'c', 'a')))
    variables_2 = ['a', 'b', 'c']

    # Test Case 3: (w AND x) OR (NOT y AND z) OR (w AND NOT z)
    test_case_3 = ('or', ('and', 'w', 'x'), ('or', ('and', ('not', 'y'), 'z'), ('and', 'w', ('not', 'z'))))
    variables_3 = ['w', 'x', 'y', 'z']

    #test xor
    test_case_4 = ('and', ('or', 'x', 'y', ('not', ('and', 'x', 'y'))))
    variables_4 = ['x', 'y']


    # Run the tests
    print("Test Case 1:")
    test_robdd_reduction(test_case_1, variables_1)

    print("Test Case 2:")
    test_robdd_reduction(test_case_2, variables_2)

    print("Test Case 3:")
    test_robdd_reduction(test_case_3, variables_3)

    print("Test Case 4:")
    test_robdd_reduction(test_case_4, variables_4)

if __name__ == "__main__":
    test_robdd_reduction_test_cases()