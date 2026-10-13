"""
Unit tests for TracebackParser and debugging engine.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parser import SourceParser
from flowchart_builder import FlowchartBuilder
from traceback_parser import TracebackParser


class TestTraceback(unittest.TestCase):

    def setUp(self):
        self.code = """def divide_numbers(a, b):
    print("Dividing numbers")
    return a / b

x = 10
y = 0
result = divide_numbers(x, y)
print(result)
"""
        tree, _, _ = SourceParser.validate_and_parse(self.code)
        builder = FlowchartBuilder(self.code, tree)
        self.graph, _ = builder.build()

    def test_zero_division_traceback_mapping(self):
        tb_text = """Traceback (most recent call last):
  File "<code2flow>", line 7, in <module>
    result = divide_numbers(x, y)
  File "<code2flow>", line 3, in divide_numbers
    return a / b
ZeroDivisionError: division by zero
"""
        analysis = TracebackParser.parse_and_map(tb_text, self.code, self.graph["nodes"])

        self.assertEqual(analysis.exception_type, "ZeroDivisionError")
        self.assertEqual(analysis.matched_lineno, 3)
        self.assertIsNotNone(analysis.matched_node_id)
        self.assertEqual(analysis.status, "matched")
        self.assertIn("divide by zero", analysis.guide["explanation"].lower())

    def test_out_of_range_line_number(self):
        tb_text = """Traceback (most recent call last):
  File "<code2flow>", line 999, in <module>
    raise RuntimeError("test")
RuntimeError: test
"""
        analysis = TracebackParser.parse_and_map(tb_text, self.code, self.graph["nodes"])
        self.assertIsNone(analysis.matched_node_id)
        self.assertEqual(analysis.status, "unmatched")
        self.assertIn("exceeds", analysis.notes)

    def test_empty_traceback(self):
        analysis = TracebackParser.parse_and_map("", self.code, self.graph["nodes"])
        self.assertEqual(analysis.status, "empty")


if __name__ == "__main__":
    unittest.main()
