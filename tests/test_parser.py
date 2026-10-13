"""
Unit tests for SourceParser and AST utilities.
Compatible with Python 3.10 through 3.14+.
"""

import unittest
from parser import SourceParser, safe_unparse


class TestParser(unittest.TestCase):

    def test_empty_code(self):
        tree, err, warnings = SourceParser.validate_and_parse("")
        self.assertIsNone(tree)
        self.assertIsNotNone(err)
        self.assertIn("empty", err.message.lower())

    def test_valid_sequential_code(self):
        code = "x = 10\ny = 20\nprint(x + y)"
        tree, err, warnings = SourceParser.validate_and_parse(code)
        self.assertIsNotNone(tree)
        self.assertIsNone(err)

    def test_syntax_error_detection(self):
        code = "def bad_func(\n    x = 10"
        tree, err, warnings = SourceParser.validate_and_parse(code)
        self.assertIsNone(tree)
        self.assertIsNotNone(err)
        self.assertIn("Syntax Error", err.message)
        self.assertIsNotNone(err.lineno)

    def test_indentation_error(self):
        code = "if True:\nprint('no indent')"
        tree, err, warnings = SourceParser.validate_and_parse(code)
        self.assertIsNone(tree)
        self.assertIsNotNone(err)
        self.assertIn("Indentation Error", err.message)

    def test_io_statement_classification(self):
        code = "x = input('Enter:')\nprint('Output:', x)"
        tree, _, _ = SourceParser.validate_and_parse(code)
        stmt1 = tree.body[0]
        stmt2 = tree.body[1]
        self.assertEqual(SourceParser.classify_statement(stmt1), "io_input")
        self.assertEqual(SourceParser.classify_statement(stmt2), "io_output")

    def test_recursive_call_detection(self):
        code = "def factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n - 1)"
        tree, _, _ = SourceParser.validate_and_parse(code)
        fn_node = tree.body[0]
        ret_stmt = fn_node.body[1]
        is_rec = SourceParser.is_recursive_call("factorial", ret_stmt)
        self.assertTrue(is_rec)


if __name__ == "__main__":
    unittest.main()
