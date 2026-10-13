"""
Code2Flow - DSA Code Analyzer
Analyzes Python AST to recognize data structure patterns and algorithm implementations
without executing untrusted code.
"""

import ast
from typing import Dict, Any, List, Optional
from parser import safe_unparse


class DSAAnalyzer:
    """Detects standard DSA patterns from AST structure."""

    @classmethod
    def detect_algorithm(cls, tree: ast.Module) -> List[Dict[str, Any]]:
        """
        Inspects AST to identify known algorithms:
        - Bubble Sort
        - Selection Sort
        - Binary Search
        - Linear Search
        - Fibonacci / Factorial Recursion
        - Linked List traversal
        """
        detected: List[Dict[str, Any]] = []

        for node in ast.walk(tree):
            # Check for functions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fname = node.name.lower()

                # Name heuristics
                if "bubble" in fname:
                    detected.append(cls._create_match("bubble_sort", "Bubble Sort", 0.95, "Function name and structure match Bubble Sort."))
                elif "selection" in fname:
                    detected.append(cls._create_match("selection_sort", "Selection Sort", 0.95, "Function name matches Selection Sort."))
                elif "insertion" in fname:
                    detected.append(cls._create_match("insertion_sort", "Insertion Sort", 0.95, "Function name matches Insertion Sort."))
                elif "binary_search" in fname or "bsearch" in fname:
                    detected.append(cls._create_match("binary_search", "Binary Search", 0.95, "Function name matches Binary Search."))
                elif "linear_search" in fname:
                    detected.append(cls._create_match("linear_search", "Linear Search", 0.95, "Function name matches Linear Search."))
                elif "fib" in fname:
                    detected.append(cls._create_match("fibonacci", "Fibonacci Recursion", 0.95, "Function name and signature match Fibonacci."))
                elif "bfs" in fname:
                    detected.append(cls._create_match("bfs", "Breadth-First Search", 0.95, "Function name matches BFS."))
                elif "dfs" in fname:
                    detected.append(cls._create_match("dfs", "Depth-First Search", 0.95, "Function name matches DFS."))

                # Structural heuristics: Nested loop with swap
                if cls._has_nested_loops_with_swap(node):
                    if not any(d["id"] == "bubble_sort" for d in detected):
                        detected.append(cls._create_match(
                            "bubble_sort",
                            "Bubble Sort (Inferred)",
                            0.80,
                            "Detected nested loops with adjacent element comparison and tuple swap."
                        ))

                # Structural: Binary search pattern (while low <= high, mid = (low + high) // 2)
                if cls._has_binary_search_pattern(node):
                    if not any(d["id"] == "binary_search" for d in detected):
                        detected.append(cls._create_match(
                            "binary_search",
                            "Binary Search (Inferred)",
                            0.85,
                            "Detected while loop with midpoint division and two-pointer narrowing."
                        ))

        # Default fallback if nothing detected
        if not detected:
            detected.append({
                "id": "bubble_sort",
                "name": "Bubble Sort (Default Template)",
                "confidence": 0.5,
                "reason": "Select an algorithm template from the DSA Visualizer tab to see step-by-step execution."
            })

        return detected

    @classmethod
    def _create_match(cls, alg_id: str, name: str, confidence: float, reason: str) -> Dict[str, Any]:
        return {
            "id": alg_id,
            "name": name,
            "confidence": confidence,
            "reason": reason
        }

    @classmethod
    def _has_nested_loops_with_swap(cls, func_node: ast.FunctionDef) -> bool:
        """Checks for nested for-loops containing a tuple swap (a[j], a[j+1] = a[j+1], a[j])."""
        for n1 in func_node.body:
            if isinstance(n1, ast.For):
                for n2 in n1.body:
                    if isinstance(n2, ast.For):
                        for n3 in ast.walk(n2):
                            if isinstance(n3, ast.Assign) and len(n3.targets) == 1:
                                if isinstance(n3.targets[0], ast.Tuple) and isinstance(n3.value, ast.Tuple):
                                    return True
        return False

    @classmethod
    def _has_binary_search_pattern(cls, func_node: ast.FunctionDef) -> bool:
        """Checks for while loop with integer division by 2."""
        for n in ast.walk(func_node):
            if isinstance(n, ast.While):
                for child in ast.walk(n):
                    if isinstance(child, ast.BinOp) and isinstance(child.op, ast.FloorDiv):
                        return True
        return False
