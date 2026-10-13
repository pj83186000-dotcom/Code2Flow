"""
Unit tests for FlowchartBuilder and control-flow graph construction.
"""

import unittest
import sys
import os

# Add parent directory to sys.path so tests can import modules directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parser import SourceParser
from flowchart_builder import FlowchartBuilder


class TestFlowchart(unittest.TestCase):

    def _build(self, code: str):
        tree, err, _ = SourceParser.validate_and_parse(code)
        self.assertIsNone(err, f"Unexpected parse error: {err.message if err else ''}")
        builder = FlowchartBuilder(code, tree)
        graph, warnings = builder.build()
        return builder, graph, warnings

    def test_sequential_flow(self):
        code = "a = 1\nb = 2\nc = a + b\nprint(c)"
        builder, graph, _ = self._build(code)
        # Should have Start, 3 process nodes, 1 io_output node, End
        self.assertTrue(graph["node_count"] >= 5)
        # Check shapes
        nodes_by_cat = {n["category"]: n for n in graph["nodes"]}
        self.assertIn("start", nodes_by_cat)
        self.assertIn("end", nodes_by_cat)
        self.assertIn("io_output", nodes_by_cat)

    def test_if_else_branching(self):
        code = """x = 10
if x > 5:
    print('Greater')
else:
    print('Smaller')
"""
        builder, graph, _ = self._build(code)
        # Verify decision node exists
        decisions = [n for n in graph["nodes"] if n["category"] == "decision"]
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0]["shape"], "diamond")

        # Verify True and False edges
        edge_labels = [e["label"] for e in graph["edges"]]
        self.assertIn("True", edge_labels)
        self.assertIn("False", edge_labels)

    def test_nested_loops_break_continue(self):
        code = """for i in range(5):
    while True:
        if i == 2:
            continue
        else:
            break
"""
        builder, graph, _ = self._build(code)
        categories = [n["category"] for n in graph["nodes"]]
        self.assertIn("loop_header", categories)
        self.assertIn("jump", categories)

        edge_types = [e["edge_type"] for e in graph["edges"]]
        self.assertIn("loop_back", edge_types)
        self.assertIn("jump", edge_types)

    def test_multiple_returns_and_unreachable_code(self):
        code = """def check_val(x):
    if x > 0:
        return 'positive'
    return 'non-positive'
    print('unreachable code')
"""
        builder, graph, warnings = self._build(code)
        # Unreachable code detection
        self.assertTrue(any("unreachable" in w.lower() for w in warnings))

    def test_try_except_finally(self):
        code = """try:
    val = 10 / 0
except ZeroDivisionError:
    val = 0
finally:
    print('done')
"""
        builder, graph, _ = self._build(code)
        cats = [n["category"] for n in graph["nodes"]]
        self.assertIn("exception", cats)

    def test_mermaid_and_dot_generation(self):
        code = "x = 5\nprint(x)"
        builder, graph, _ = self._build(code)
        mermaid = builder.to_mermaid()
        dot = builder.to_dot()
        self.assertTrue(mermaid.startswith("flowchart TD"))
        self.assertTrue(dot.startswith("digraph Code2Flow"))


if __name__ == "__main__":
    unittest.main()
