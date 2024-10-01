import unittest
from io import StringIO
import sys
from project.ROBDD import ROBDD

class TestROBDD(unittest.TestCase):

    def setUp(self):
        self.robdd = ROBDD()
        self.captured_output = StringIO()
        sys.stdout = self.captured_output

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def assert_output(self, expected_output):
        self.assertEqual(self.captured_output.getvalue().strip(), expected_output.strip())

    def test_simple_or(self):
        self.robdd.build(('or', 'x', 'y'), ['x', 'y'])
        self.robdd.show()
        expected_output = """
        x y | Result
        -------------
        0 0 | 0
        0 1 | 1
        1 0 | 1
        1 1 | 1
        """
        self.assert_output(expected_output)

    def test_complex_expression(self):
        expr = ('and', ('or', 'a', 'b'), ('not', ('and', 'c', 'd')))
        self.robdd.build(expr, ['a', 'b', 'c', 'd'])
        self.robdd.show()
        # Add expected output here

    def test_all_variables_true(self):
        expr = ('and', 'x', 'y', 'z')
        self.robdd.build(expr, ['x', 'y', 'z'])
        self.robdd.show_ones()
        expected_output = """
        x y z
        -----
        1 1 1
        """
        self.assert_output(expected_output)

    def test_always_true(self):
        self.robdd.build('True', [])
        self.robdd.show()
        expected_output = """
        Result
        ------
        1
        """
        self.assert_output(expected_output)

    def test_always_false(self):
        self.robdd.build('False', [])
        self.robdd.show()
        expected_output = """
        Result
        ------
        0
        """
        self.assert_output(expected_output)

    def test_single_variable(self):
        self.robdd.build('x', ['x'])
        self.robdd.show()
        expected_output = """
        x | Result
        ---------
        0 | 0
        1 | 1
        """
        self.assert_output(expected_output)

    def test_many_variables(self):
        vars = [f'x{i}' for i in range(10)]
        expr = ('or',) + tuple(vars)
        self.robdd.build(expr, vars)
        self.robdd.show_ones()
        # Check that the output has 2^10 - 1 lines (all combinations except all False)

    def test_nested_not(self):
        expr = ('not', ('not', ('not', 'x')))
        self.robdd.build(expr, ['x'])
        self.robdd.show()
        expected_output = """
        x | Result
        ---------
        0 | 1
        1 | 0
        """
        self.assert_output(expected_output)

    def test_xor(self):
        expr = ('or', ('and', 'x', ('not', 'y')), ('and', ('not', 'x'), 'y'))
        self.robdd.build(expr, ['x', 'y'])
        self.robdd.show()
        expected_output = """
        x y | Result
        -------------
        0 0 | 0
        0 1 | 1
        1 0 | 1
        1 1 | 0
        """
        self.assert_output(expected_output)

    def test_empty_robdd(self):
        with self.assertRaises(ValueError):
            self.robdd.show()

    def test_large_expression(self):
        vars = [f'x{i}' for i in range(20)]
        expr = ('and', ('or',) + tuple(vars[:10]), ('or',) + tuple(vars[10:]))
        self.robdd.build(expr, vars)
        self.robdd.show_ones()
        # Check that the output is not empty and has the correct format

    def test_all_operators(self):
        expr = ('or', ('and', 'a', 'b'), ('not', 'c'), ('or', 'd', 'e'))
        self.robdd.build(expr, ['a', 'b', 'c', 'd', 'e'])
        self.robdd.show()
        # Add expected output here

    def test_redundant_variables(self):
        expr = ('or', 'x', 'x')
        self.robdd.build(expr, ['x', 'y'])  # 'y' is redundant
        self.robdd.show()
        expected_output = """
        x y | Result
        -------------
        0 0 | 0
        0 1 | 0
        1 0 | 1
        1 1 | 1
        """
        self.assert_output(expected_output)

    def test_constant_in_expression(self):
        expr = ('and', 'x', 'True', ('or', 'y', 'False'))
        self.robdd.build(expr, ['x', 'y'])
        self.robdd.show()
        # Add expected output here

    def test_show_ones_all_false(self):
        expr = ('and', 'x', ('not', 'x'))
        self.robdd.build(expr, ['x'])
        self.robdd.show_ones()
        expected_output = """
        x
        -
        """
        self.assert_output(expected_output)

if __name__ == '__main__':
    unittest.main()