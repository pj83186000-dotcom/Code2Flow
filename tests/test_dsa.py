"""
Unit tests for DSAEngine and simulation algorithms.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dsa_visualizer import DSAEngine
from dsa_analyzer import DSAAnalyzer
from parser import SourceParser


class TestDSA(unittest.TestCase):

    def test_bubble_sort_simulation(self):
        arr = [4, 2, 7, 1]
        frames = DSAEngine.bubble_sort(arr)
        self.assertGreater(len(frames), 0)
        first_frame = frames[0]
        last_frame = frames[-1]
        self.assertEqual(first_frame["step"], 1)
        self.assertEqual(last_frame["step"], len(frames))
        self.assertEqual(first_frame["complexity"]["time_worst"], "O(n²)")
        # Final array in state should be sorted
        final_items = [it["val"] for it in last_frame["state"]["items"]]
        self.assertEqual(final_items, sorted(arr))

    def test_binary_search_simulation(self):
        arr = [10, 20, 30, 40, 50]
        frames = DSAEngine.binary_search(arr, 30)
        self.assertGreater(len(frames), 0)
        self.assertTrue(any("FOUND" in f["action"] for f in frames))

    def test_linked_list_reversal(self):
        vals = [1, 2, 3]
        frames = DSAEngine.linked_list_reversal(vals)
        self.assertGreater(len(frames), 0)
        last_frame = frames[-1]
        self.assertIn("complete", last_frame["action"].lower())

    def test_stack_operations(self):
        ops = [("push", 10), ("push", 20), ("pop", None)]
        frames = DSAEngine.stack_operations(ops)
        self.assertEqual(len(frames), 4)  # Init, push, push, pop

    def test_queue_operations(self):
        ops = [("enqueue", "A"), ("dequeue", None)]
        frames = DSAEngine.queue_operations(ops)
        self.assertGreater(len(frames), 0)

    def test_bst_traversal(self):
        vals = [50, 30, 70]
        frames = DSAEngine.bst_traversal(vals, mode="inorder")
        self.assertGreater(len(frames), 0)

    def test_graph_bfs(self):
        frames = DSAEngine.graph_traversal(mode="bfs", start_node="A")
        self.assertGreater(len(frames), 0)

    def test_fibonacci_recursion(self):
        frames = DSAEngine.fibonacci_recursion(3)
        self.assertGreater(len(frames), 0)
        self.assertIn("call_stack", frames[0]["state"])

    def test_dsa_pattern_detection(self):
        code = """def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr) - 1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
"""
        tree, _, _ = SourceParser.validate_and_parse(code)
        detected = DSAAnalyzer.detect_algorithm(tree)
        self.assertTrue(any(d["id"] == "bubble_sort" for d in detected))


if __name__ == "__main__":
    unittest.main()
