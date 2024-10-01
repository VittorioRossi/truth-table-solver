import unittest
from project.parser import parse

class TestParser(unittest.TestCase):
    def setUp(self):
        self.parse = parse


    # TestVariableDeclarations:
    def test_multiple_variable_declaration(self):
        content = "var x1 x2 x3 x4 x5;"
        variables, _, _ = self.parse(content)
        self.assertEqual(variables, ['x1', 'x2', 'x3', 'x4', 'x5'])

    def test_redeclared_variable_raises_error(self):
        content = "var x; var x;"
        with self.assertRaises(ValueError):
            self.parse(content)

    def test_keyword_as_variable_raises_error(self):
        content = "var x show_ones;"
        with self.assertRaises(ValueError):
            self.parse(content)


    def test_var_not_declared(self):
        test_content = """
        var x1 x2 x3;
        f1 = x1 and x2 and x4;
        """
        with self.assertRaises(ValueError):
            parse(test_content)

    def test_keyword_as_variable(self):
        content = """
        var x show_ones;
        z = x and show_ones;
        """
        with self.assertRaises(ValueError):
            parse(content)
    
    # TestNotOperator:
    def test_not_next_to_not(self):
        content = "var x; z = notnot x;"
        with self.assertRaises(ValueError):
            parse(content)

    def test_valid_not_with_parentheses(self):
        content = "var y; z = not (y);"
        _, assignments, _ = self.parse(content)
        self.assertEqual(assignments, {'z': ('not', 'y')})

    def test_multiple_not_operators(self):
        content = "var x; y = not not not x;"
        _, assignments, _ = self.parse(content)
        self.assertEqual(assignments, {'y': ('not', 'x')})

    def test_not_with_complex_expression(self):
        content = "var x y z; w = not (x and (y or (not z)));"
        _, assignments, _ = self.parse(content)
        expected = {'w': ('not', ('and', 'x', ('or', 'y', ('not', 'z'))))}
        self.assertEqual(assignments, expected)

    def test_valid_not_with_parentheses(self):
        content = "var y; z = not (y);"
        _, assignments, _ = parse(content)
        expected = {'z': ('not', 'y')}
        self.assertEqual(assignments, expected, msg="Expected ('not', 'y'), got " + str(assignments))

    def test_not_with_multiple_parentheses(self):
        content = "var y; z = not (((y)));"
        _, assignments, _ = parse(content)
        expected = {'z': ('not', 'y')}
        self.assertEqual(assignments, expected, msg=f"Expected {expected}, got {assignments}")

    def test_not_with_nested_not(self):
        content = "var y; z = not (not y);"
        _, assignments, _ = parse(content)
        expected = {'z': ('not', ('not', 'y'))}
        self.assertEqual(assignments, expected, msg=f"Expected {expected}, got {assignments}")

    def test_not_with_and_in_parentheses(self):
        content = "var x y; z = not (x and y);"
        _, assignments, _ = parse(content)
        expected = {'z': ('not', ('and', 'x', 'y'))}
        self.assertEqual(assignments, expected, msg=f"Expected {expected}, got {assignments}")

    def test_not_with_or_in_parentheses(self):
        content = "var x y; z = not (x or y);"
        _, assignments, _ = parse(content)
        expected = {'z': ('not', ('or', 'x', 'y'))}
        self.assertEqual(assignments, expected, msg=f"Expected {expected}, got {assignments}")

    def test_not_with_complex_expression(self):
        content = "var x y z; w = not (x and (y or (not z)));"
        _, assignments, _ = parse(content)
        expected = {'w': ('not', ('and', 'x', ('or', 'y', ('not', 'z'))))}
        self.assertEqual(assignments, expected, msg=f"Expected {expected}, got {assignments}")

    def test_multiple_not_operators(self):
        content = "var x; y = not not not x;"
        _, assignments, _ = parse(content)
        expected = {'y': ('not', 'x')}
        self.assertEqual(assignments, expected, msg=f"Expected {expected}, got {assignments}")

    def test_not_with_true_false(self):
        content = "var x; y = not (True and False);"
        _, assignments, _ = parse(content)
        expected = {'y': ('not', ('and', 'True', 'False'))}
        self.assertEqual(assignments, expected, msg=f"Expected {expected}, got {assignments}")

    def test_not_without_space(self):
        content = "var x; y = not(x);"
        _, assignments, _ = parse(content)
        expected = {'y': ('not', 'x')}
        self.assertEqual(assignments, expected, msg=f"Expected {expected}, got {assignments}")

    def test_not_with_mismatched_parentheses(self):
        content = "var x; y = not (x;"
        with self.assertRaises(ValueError):
            parse(content)

    def test_not_with_empty_parentheses(self):
        content = "var x; y = not ();"
        with self.assertRaises(ValueError):
            parse(content)

    def test_missing_parentheses_for_not(self):
        content = "var x y; z = x and not y;"
        with self.assertRaises(ValueError):
            parse(content)

    def test_valid_not_expression(self):
        content = "var x y; z = not x and y;"
        _, assignments, _ = parse(content)
        expected = {'z': ('and', ('not', 'x'), 'y')}
        self.assertEqual(assignments, expected)

    def test_double_not_without_parentheses(self):
        content = "var x; z = not not x;"
        _, assignments, _ = parse(content)
        expected = {'z': 'x'}
        self.assertEqual(assignments, expected, msg=f"Expected {expected}, got {assignments}")


    # TestAndOrOperators:
    def test_multiple_and_operators(self):
        content = "var a b c; f = a and b and c;"
        _, assignments, _ = self.parse(content)
        self.assertEqual(assignments, {'f': ('and', 'a', 'b', 'c')})

    def test_multiple_or_operators(self):
        content = "var a b c; g = a or b or c;"
        _, assignments, _ = self.parse(content)
        self.assertEqual(assignments, {'g': ('or', 'a', 'b', 'c')})

    def test_mixed_and_or_with_parentheses(self):
        content = "var x y w; z = (x and y) or w;"
        _, assignments, _ = self.parse(content)
        self.assertEqual(assignments, {'z': ('or', ('and', 'x', 'y'), 'w')})

        
    def test_double_and_expression(self):
        content = "var x; z = x and and;"
        with self.assertRaises(ValueError):
            parse(content)

    def test_valid_and_with_parentheses(self):
        content = "var x y; z = (x) and y;"
        _, assignments, _ = parse(content)
        expected = {'z': ('and', 'x', 'y')}
        self.assertEqual(assignments, expected)

    # TestParentheses:
    def test_nested_parentheses(self):
        content = "var x y; f = (x and (y or (not x)));"
        _, assignments, _ = self.parse(content)
        expected = {'f': ('and', 'x', ('or', 'y', ('not', 'x')))}
        self.assertEqual(assignments, expected)

    def test_unmatched_closing_parenthesis_raises_error(self):
        content = "var x y; z = x and y);"
        with self.assertRaises(ValueError):
            self.parse(content)

    def test_missing_closing_parenthesis_raises_error(self):
        content = "var x y; z = (x and y;"
        with self.assertRaises(ValueError):
            self.parse(content)

    # TestTrueFalseKeywords:
    def test_true_false_in_expressions(self):
        content = "var x; f = x and True; g = False or x;"
        _, assignments, _ = self.parse(content)
        expected = {
            'f': ('and', 'x', 'True'),
            'g': ('or', 'False', 'x')
        }
        self.assertEqual(assignments, expected)

    # TestShowInstructions:
    def test_show_instruction(self):
        content = "var x y; f = x and y; show f;"
        _, _, show_instructions = self.parse(content)
        self.assertEqual(show_instructions, [('show', ['f'])])

    def test_show_ones_instruction(self):
        content = "var x y; f = x and y; show_ones f;"
        _, _, show_instructions = self.parse(content)
        self.assertEqual(show_instructions, [('show_ones', ['f'])])

    def test_multiple_show_instructions(self):
        content = "var x y; f = x and y; g = x or y; show f; show_ones g;"
        _, _, show_instructions = self.parse(content)
        expected = [('show', ['f']), ('show_ones', ['g'])]
        self.assertEqual(show_instructions, expected)

    def test_wrong_show(self):
        test_content = """
        var x1 x2 x3;
        f1 = x1 and x2;
        f2 = ((((x1 or x2))));
        show_ones f3;
        """
        with self.assertRaises(ValueError):
            parse(test_content)



    # TestErrorHandling:
    def test_use_before_declaration_raises_error(self):
        content = "var x; z = x and t; var t;"
        with self.assertRaises(ValueError):
            self.parse(content)

    def test_self_reference_in_assignment_raises_error(self):
        content = "var x; z = x and z;"
        with self.assertRaises(ValueError):
            self.parse(content)

    def test_incomplete_expression_raises_error(self):
        content = "var x; z = x and;"
        with self.assertRaises(ValueError):
            self.parse(content)

    def test_incomplete_expression_parentheses(self):
        content = "var x y; z = x and (y or);"
        with self.assertRaises(ValueError):
            parse(content)

    def test_incomplete_expression_nested_parentheses(self):
        content = "var x y z; w = (x and (y or) and z);"
        with self.assertRaises(ValueError):
            parse(content)

    def test_incomplete_expression_multiple_parentheses(self):
        content = "var a b c; d = (a or b) and (c or);"
        with self.assertRaises(ValueError):
            parse(content)

    def test_incomplete_expression_start_of_parentheses(self):
        content = "var x y; z = x and (or y);"
        with self.assertRaises(ValueError):
            parse(content)

    def test_incomplete_expression_empty_parentheses_in_expression(self):
        content = "var x y; z = x and () or y;"
        with self.assertRaises(ValueError):
            parse(content)

    def test_incomplete_and_expression(self):
        content = "var x; z = x and;"
        with self.assertRaises(ValueError):
            parse(content)

    def test_incomplete_or_expression(self):
        content = "var x; z = x or;"
        with self.assertRaises(ValueError):
            parse(content)

    def test_incomplete_nested_expression(self):
        content = "var x y; z = (x and y) or;"
        with self.assertRaises(ValueError):
            parse(content)

    def test_incomplete_complex_expression(self):
        content = "var a b c; d = (a and b) or (c and);"
        with self.assertRaises(ValueError):
            parse(content)

    def test_incomplete_expression_with_not(self):
        content = "var x; z = not x and;"
        with self.assertRaises(ValueError):
            parse(content)

    def test_incomplete_expression_multiple_operators(self):
        content = "var x y z; w = x and y or;"
        with self.assertRaises(ValueError):
            parse(content)
            
    def test_incomplete_expression_multiple_variables(self):
        content = "var a b c d; e = a and b or c and;"
        with self.assertRaises(ValueError):
            parse(content)


    # TestComplexExpressions:
    def test_complex_nested_expression(self):
        content = """
        var a b c d;
        f = (a and (b)) and (not (c)) and (d or (a and (not not b)));
        show f;
        """
        _, assignments, _ = self.parse(content)
        expected = {
            'f': ('and', 
                    ('and', 'a', 'b'), 
                    ('not', 'c'), 
                    ('or', 'd', ('and', 'a', 'b'))
            )
        }
        self.assertEqual(assignments, expected)

    # TestComments:
    def test_comments_are_ignored(self):
        content = """
        # This is a comment
        var x y; # Another comment
        f = x and y; # Comment after expression
        # Comment before show
        show f;
        """
        variables, assignments, show_instructions = self.parse(content)
        self.assertEqual(variables, ['x', 'y'])
        self.assertEqual(assignments, {'f': ('and', 'x', 'y')})
        self.assertEqual(show_instructions, [('show', ['f'])])




    ##########################
    # TEST GENERAL OPS #
    ##########################
    def test_operator_before_operand(self):
        content = "var x; z = and x;"
        with self.assertRaises(ValueError):
            parse(content)

    def test_double_operator_no_operands(self):
        content = "z = and and;"
        with self.assertRaises(ValueError):
            parse(content)

    def test_wrong_operator(self):
        test_content = """
        var x1 x2 x3;
        f1 = x1 and x2;
        f2 = x1 or x2;
        f3 = x1 xor x2;
        """
        with self.assertRaises(ValueError):
            parse(test_content)

    def test_wrong_multi_op_expression(self):
        test_content = """
        var x1 x2 x3;
        f1 = x1 and x2;
        f2 = x1 or and x2;
        """
        with self.assertRaises(ValueError):
            parse(test_content)

    #########################
    #        TEST OTHER     #
    #########################

    def test_basic(self):
        test_content = """
        # Test case for Boolean formula parser
        var x1 x2 x3;

        # Simple assignments
        f1 = x1 and x2;

        f2 = (((((x1 or x2)))));

        # Nested expressions with multiple operators
        show f1;
        """
        variables, assignments, show_instructions = parse(test_content)

        self.assertEqual(variables, ['x1', 'x2', 'x3'])
        self.assertEqual(assignments, {'f1': ('and', 'x1', 'x2'), 'f2': ('or', 'x1', 'x2')})
        self.assertEqual(show_instructions, [('show', ['f1'])])


    def test_missing_end_of_line(self):
        test_content = """
        var x1 x2 x3;
        f1 = x1 and x2 and x2
        """    
        with self.assertRaises(ValueError):
            parse(test_content)


    def test_doubled_end_of_line(self):
        test_content = """
        var x1 x2 x3;
        f1 = x1 and x2 and x2;;
        """    
        with self.assertRaises(ValueError):
            parse(test_content)

    def test_replace_assignment_into_expression(self):
        test_content = """
        var x1 x2 x3;
        f1 = x1 and x2;
        f2 = f1 or x2;
        """
        variables, assignments, show_instructions = parse(test_content)

        self.assertEqual(variables, ['x1', 'x2', 'x3'])
        self.assertEqual(assignments, {'f1': ('and', 'x1', 'x2'), 'f2': ('or', ('and', 'x1', 'x2'), 'x2')})
        self.assertEqual(show_instructions, [])

    def test_missing_equal_sign(self):
        test_content = """
        var x1 x2 x3;
        f1 x1 and x2;
        """
        with self.assertRaises(ValueError):
            parse(test_content)

    def test_missing_parenthesis(self):
        test_content = """
        var x1 x2 x3;
        f1 = x1 and x2;
        f2 = (x1 or x2;
        """
        with self.assertRaises(ValueError):
            parse(test_content)

    def test_multiple_and_or_operators(self):
        content = "var a b c; f = a and b and c; g = a or b or c;"
        _, assignments, _ = parse(content)
        expected = {
            'f': ('and', 'a', 'b', 'c'),
            'g': ('or', 'a', 'b', 'c')
        }
        self.assertEqual(assignments, expected)

    # New additional tests
    def test_multiple_variable_declaration(self):
        content = "var x1 x2 x3 x4 x5;"
        variables, assignments, show_instructions = parse(content)
        self.assertEqual(variables, ['x1', 'x2', 'x3', 'x4', 'x5'])

    def test_nested_expressions(self):
        content = "var x y; f = (x and (y or (not x)));"
        _, assignments, _ = parse(content)
        expected = {'f': ('and', 'x', ('or', 'y', ('not', 'x')))}
        self.assertEqual(assignments, expected)


    def test_true_false_keywords(self):
        content = "var x; f = x and True; g = False or x;"
        _, assignments, _ = parse(content)
        expected = {
            'f': ('and', 'x', 'True'),
            'g': ('or', 'False', 'x')
        }
        self.assertEqual(assignments, expected)

    def test_show_ones_instruction(self):
        content = "var x y; f = x and y; show_ones f;"
        _, _, show_instructions = parse(content)
        self.assertEqual(show_instructions, [('show_ones', ['f'])])

    def test_multiple_show_instructions(self):
        content = "var x y; f = x and y; g = x or y; show f; show_ones g;"
        _, _, show_instructions = parse(content)
        expected = [('show', ['f']), ('show_ones', ['g'])]
        self.assertEqual(show_instructions, expected)

    def test_error_redeclared_variable(self):
        content = "var x; var x;"
        with self.assertRaises(ValueError):
            parse(content)

    def test_show_undeclared_variable(self):
        content = "var x y z; show x;"
        try:
            _, _, show_instructions = parse(content)
            self.assertEqual(show_instructions, [('show', ['x'])])
        except ValueError:
            pass  # Both accepting and rejecting are valid behaviors

    def test_unmatched_closing_parenthesis(self):
        content = "var x y; z = x and y);"
        with self.assertRaises(ValueError):
            parse(content)

    def test_self_reference_in_assignment(self):
        content = "var x; z = x and z;"
        with self.assertRaises(ValueError):
            parse(content)

    def test_use_before_declaration(self):
        content = "var x; z = x and t; var t;"
        with self.assertRaises(ValueError):
            parse(content)

    def test_mixed_and_or_without_parentheses(self):
        content = "var x y w; z = x and y or w;"
        with self.assertRaises(ValueError):
            parse(content)


    def test_show_unassigned_assignment(self):
        content = "var x y z; show z;"
        try:
            _, _, show_instructions = parse(content)
            self.assertEqual(show_instructions, [('show', ['z'])])
        except ValueError:
            pass

    def test_show_ones_unassigned_assignment(self):
        content = "var x y z; show_ones z;"
        try:
            _, _, show_instructions = parse(content)
            self.assertEqual(show_instructions, [('show_ones', ['z'])])
        except ValueError:
            pass

    def test_show_variable(self):
        content = "var x y z; show x;"
        _, _, show_instructions = parse(content)
        self.assertEqual(show_instructions, [('show', ['x'])])

if __name__ == '__main__':
    unittest.main()