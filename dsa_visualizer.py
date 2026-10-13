"""
Code2Flow - DSA Visualization Engine
Explicit, safe instrumented step-by-step execution simulation for:
- Sorting: Bubble, Selection, Insertion, Merge, Quick, Heap sort
- Searching: Linear Search, Binary Search
- Linked Lists: Singly linked list, Doubly linked list, Reversal
- Stacks, Queues, Circular Queues, Deques
- Trees: BST insertion, search, Traversals (Inorder, Preorder, Postorder), AVL Tree rotations
- Heaps & Priority Queues
- Graphs: BFS, DFS, Dijkstra's algorithm, Cycle Detection
- Recursion: Fibonacci recursion tree, Factorial call stack
- Two-Pointer & Sliding Window
- Hash Table (Bucket chaining)
- Trie (Prefix tree)
- Union-Find (Disjoint Set)
"""

import math
from typing import Dict, Any, List, Optional, Tuple


class StepFrame:
    """Represents a single atomic visual step in algorithm execution."""
    def __init__(
        self,
        step: int,
        total_steps: int,
        action: str,
        code_line: str,
        data_type: str,
        state: Dict[str, Any],
        variables: Dict[str, Any],
        complexity: Dict[str, str]
    ):
        self.step = step
        self.total_steps = total_steps
        self.action = action
        self.code_line = code_line
        self.data_type = data_type
        self.state = state
        self.variables = variables
        self.complexity = complexity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "total_steps": self.total_steps,
            "action": self.action,
            "code_line": self.code_line,
            "data_type": self.data_type,
            "state": self.state,
            "variables": self.variables,
            "complexity": self.complexity
        }


class DSAEngine:
    """Generates step-by-step visualization frames for supported DSA algorithms."""

    # ------------------ SORTING ALGORITHMS ------------------

    @staticmethod
    def bubble_sort(arr: List[int]) -> List[Dict[str, Any]]:
        a = list(arr)
        n = len(a)
        frames_data: List[Dict[str, Any]] = []

        complexity = {
            "time_best": "O(n)",
            "time_avg": "O(n²)",
            "time_worst": "O(n²)",
            "space": "O(1)",
            "explanation": "Iteratively compares adjacent elements and swaps them if out of order. With n elements, requires up to n-1 passes."
        }

        def record(act: str, line: str, comp_idx: Tuple[int, int] = (-1, -1), swap: bool = False, sorted_idx: Set[int] = None, vars_dict: Dict = None):
            sorted_set = sorted_idx or set()
            items = []
            for idx, val in enumerate(a):
                st = "default"
                if idx in sorted_set:
                    st = "sorted"
                elif idx in comp_idx:
                    st = "swapping" if swap else "comparing"
                items.append({"index": idx, "val": val, "state": st})
            frames_data.append({
                "action": act,
                "code_line": line,
                "data_type": "array",
                "state": {"items": items},
                "variables": vars_dict or {},
                "complexity": complexity
            })

        record("Initial array state.", "bubble_sort(arr)", sorted_idx=set())

        sorted_indices = set()
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                record(
                    f"Comparing arr[{j}] ({a[j]}) and arr[{j+1}] ({a[j+1]}).",
                    "if arr[j] > arr[j + 1]:",
                    comp_idx=(j, j + 1),
                    sorted_idx=sorted_indices,
                    vars_dict={"pass": i + 1, "j": j, "arr[j]": a[j], "arr[j+1]": a[j+1]}
                )
                if a[j] > a[j + 1]:
                    a[j], a[j + 1] = a[j + 1], a[j]
                    swapped = True
                    record(
                        f"Swapped {a[j+1]} and {a[j]} since {a[j+1]} > {a[j]}.",
                        "arr[j], arr[j + 1] = arr[j + 1], arr[j]",
                        comp_idx=(j, j + 1),
                        swap=True,
                        sorted_idx=sorted_indices,
                        vars_dict={"pass": i + 1, "swapped": True}
                    )
            sorted_indices.add(n - i - 1)
            record(f"Element at index {n - i - 1} is now in its final sorted position.", "pass_complete", sorted_idx=sorted_indices)
            if not swapped:
                record("No swaps occurred in this pass. Array is fully sorted early!", "break", sorted_idx=set(range(n)))
                break

        sorted_indices = set(range(n))
        record("Sorting complete! All elements ordered.", "return arr", sorted_idx=sorted_indices)

        # Set step and total_steps
        total = len(frames_data)
        for idx, f in enumerate(frames_data):
            f["step"] = idx + 1
            f["total_steps"] = total
        return frames_data

    @staticmethod
    def selection_sort(arr: List[int]) -> List[Dict[str, Any]]:
        a = list(arr)
        n = len(a)
        frames_data: List[Dict[str, Any]] = []

        complexity = {
            "time_best": "O(n²)",
            "time_avg": "O(n²)",
            "time_worst": "O(n²)",
            "space": "O(1)",
            "explanation": "Finds the minimum element from the unsorted segment and swaps it with the first unsorted element."
        }

        def record(act: str, line: str, comp_idx: Tuple[int, int] = (-1, -1), min_idx: int = -1, sorted_idx: Set[int] = None, vars_dict: Dict = None):
            sorted_set = sorted_idx or set()
            items = []
            for idx, val in enumerate(a):
                st = "default"
                if idx in sorted_set:
                    st = "sorted"
                elif idx == min_idx:
                    st = "min_pointer"
                elif idx in comp_idx:
                    st = "comparing"
                items.append({"index": idx, "val": val, "state": st})
            frames_data.append({
                "action": act,
                "code_line": line,
                "data_type": "array",
                "state": {"items": items},
                "variables": vars_dict or {},
                "complexity": complexity
            })

        sorted_indices = set()
        record("Initial array state.", "selection_sort(arr)", sorted_idx=sorted_indices)

        for i in range(n):
            min_i = i
            record(f"Pass {i+1}: Assume current element arr[{i}] ({a[i]}) is minimum.", "min_idx = i", min_idx=min_i, sorted_idx=sorted_indices)
            for j in range(i + 1, n):
                record(
                    f"Comparing arr[{j}] ({a[j]}) with current min arr[{min_i}] ({a[min_i]}).",
                    "if arr[j] < arr[min_idx]:",
                    comp_idx=(j, min_i),
                    min_idx=min_i,
                    sorted_idx=sorted_indices,
                    vars_dict={"i": i, "j": j, "min_idx": min_i}
                )
                if a[j] < a[min_i]:
                    min_i = j
                    record(f"Found new minimum: arr[{min_i}] ({a[min_i]}).", "min_idx = j", min_idx=min_i, sorted_idx=sorted_indices)

            if min_i != i:
                a[i], a[min_i] = a[min_i], a[i]
                record(f"Swapped arr[{i}] ({a[min_i]}) with minimum arr[{min_i}] ({a[i]}).", "arr[i], arr[min_idx] = arr[min_idx], arr[i]", sorted_idx=sorted_indices)
            sorted_indices.add(i)
            record(f"Index {i} placed into sorted partition.", "partition_updated", sorted_idx=sorted_indices)

        record("Selection sort completed.", "return arr", sorted_idx=set(range(n)))
        total = len(frames_data)
        for idx, f in enumerate(frames_data):
            f["step"] = idx + 1
            f["total_steps"] = total
        return frames_data

    @staticmethod
    def insertion_sort(arr: List[int]) -> List[Dict[str, Any]]:
        a = list(arr)
        n = len(a)
        frames_data: List[Dict[str, Any]] = []

        complexity = {
            "time_best": "O(n)",
            "time_avg": "O(n²)",
            "time_worst": "O(n²)",
            "space": "O(1)",
            "explanation": "Builds the sorted array one item at a time by inserting each element into its proper position."
        }

        def record(act: str, line: str, key_idx: int = -1, comp_idx: int = -1, sorted_idx: Set[int] = None, vars_dict: Dict = None):
            sorted_set = sorted_idx or set()
            items = []
            for idx, val in enumerate(a):
                st = "default"
                if idx == key_idx:
                    st = "key"
                elif idx == comp_idx:
                    st = "comparing"
                elif idx in sorted_set:
                    st = "sorted"
                items.append({"index": idx, "val": val, "state": st})
            frames_data.append({
                "action": act,
                "code_line": line,
                "data_type": "array",
                "state": {"items": items},
                "variables": vars_dict or {},
                "complexity": complexity
            })

        sorted_indices = {0}
        record("Start with first element arr[0] trivially sorted.", "insertion_sort(arr)", sorted_idx=sorted_indices)

        for i in range(1, n):
            key = a[i]
            j = i - 1
            record(f"Pick key = arr[{i}] ({key}) to insert into sorted left partition.", "key = arr[i]", key_idx=i, sorted_idx=sorted_indices, vars_dict={"key": key, "i": i})

            while j >= 0 and a[j] > key:
                record(f"arr[{j}] ({a[j]}) > key ({key}), shifting arr[{j}] right to index {j+1}.", "arr[j + 1] = arr[j]", key_idx=i, comp_idx=j, sorted_idx=sorted_indices)
                a[j + 1] = a[j]
                j -= 1

            a[j + 1] = key
            sorted_indices.add(i)
            record(f"Inserted key ({key}) at position {j + 1}.", "arr[j + 1] = key", sorted_idx=sorted_indices)

        record("Insertion sort finished.", "return arr", sorted_idx=set(range(n)))
        total = len(frames_data)
        for idx, f in enumerate(frames_data):
            f["step"] = idx + 1
            f["total_steps"] = total
        return frames_data

    @staticmethod
    def merge_sort(arr: List[int]) -> List[Dict[str, Any]]:
        a = list(arr)
        frames_data: List[Dict[str, Any]] = []

        complexity = {
            "time_best": "O(n log n)",
            "time_avg": "O(n log n)",
            "time_worst": "O(n log n)",
            "space": "O(n)",
            "explanation": "Divide-and-conquer algorithm that recursively divides array into halves and merges sorted sub-arrays."
        }

        def record(act: str, line: str, l: int = -1, r: int = -1, vars_dict: Dict = None):
            items = []
            for idx, val in enumerate(a):
                st = "default"
                if l <= idx <= r and l != -1:
                    st = "active_subarray"
                items.append({"index": idx, "val": val, "state": st})
            frames_data.append({
                "action": act,
                "code_line": line,
                "data_type": "array",
                "state": {"items": items},
                "variables": vars_dict or {},
                "complexity": complexity
            })

        record("Initial array before Merge Sort.", "merge_sort(arr)", 0, len(a) - 1)

        def merge(left: int, mid: int, right: int):
            left_copy = a[left:mid + 1]
            right_copy = a[mid + 1:right + 1]
            record(f"Merging sub-arrays: {left_copy} and {right_copy}.", "merge(left, mid, right)", left, right)

            i = j = 0
            k = left
            while i < len(left_copy) and j < len(right_copy):
                if left_copy[i] <= right_copy[j]:
                    a[k] = left_copy[i]
                    i += 1
                else:
                    a[k] = right_copy[j]
                    j += 1
                k += 1

            while i < len(left_copy):
                a[k] = left_copy[i]
                i += 1
                k += 1

            while j < len(right_copy):
                a[k] = right_copy[j]
                j += 1
                k += 1

            record(f"Merged result for span [{left}..{right}]: {a[left:right+1]}.", "sub_array_merged", left, right)

        def sort_helper(left: int, right: int):
            if left >= right:
                return
            mid = (left + right) // 2
            record(f"Splitting span [{left}..{right}] at mid={mid}.", "mid = (left + right) // 2", left, right, {"left": left, "mid": mid, "right": right})
            sort_helper(left, mid)
            sort_helper(mid + 1, right)
            merge(left, mid, right)

        sort_helper(0, len(a) - 1)
        record("Merge sort completed.", "return arr", 0, len(a) - 1)

        total = len(frames_data)
        for idx, f in enumerate(frames_data):
            f["step"] = idx + 1
            f["total_steps"] = total
        return frames_data

    @staticmethod
    def quick_sort(arr: List[int]) -> List[Dict[str, Any]]:
        a = list(arr)
        frames_data: List[Dict[str, Any]] = []

        complexity = {
            "time_best": "O(n log n)",
            "time_avg": "O(n log n)",
            "time_worst": "O(n²)",
            "space": "O(log n)",
            "explanation": "Selects a pivot element and partitions the array such that elements smaller than pivot go left, greater go right."
        }

        def record(act: str, line: str, pivot_idx: int = -1, low: int = -1, high: int = -1, sorted_idx: Set[int] = None):
            items = []
            for idx, val in enumerate(a):
                st = "default"
                if sorted_idx and idx in sorted_idx:
                    st = "sorted"
                elif idx == pivot_idx:
                    st = "pivot"
                elif low <= idx <= high and low != -1:
                    st = "active_subarray"
                items.append({"index": idx, "val": val, "state": st})
            frames_data.append({
                "action": act,
                "code_line": line,
                "data_type": "array",
                "state": {"items": items},
                "variables": {"low": low, "high": high, "pivot_idx": pivot_idx},
                "complexity": complexity
            })

        sorted_set = set()
        record("Initial array before Quick Sort.", "quick_sort(arr, 0, n - 1)", -1, 0, len(a) - 1)

        def partition(low: int, high: int) -> int:
            pivot = a[high]
            record(f"Selected pivot = {pivot} at index {high}.", "pivot = arr[high]", pivot_idx=high, low=low, high=high)
            i = low - 1
            for j in range(low, high):
                if a[j] < pivot:
                    i += 1
                    a[i], a[j] = a[j], a[i]
                    record(f"Swapped arr[{i}] and arr[{j}] since {a[i]} < pivot ({pivot}).", "arr[i], arr[j] = arr[j], arr[i]", pivot_idx=high, low=low, high=high)
            a[i + 1], a[high] = a[high], a[i + 1]
            p_pos = i + 1
            sorted_set.add(p_pos)
            record(f"Placed pivot {pivot} at partition boundary index {p_pos}.", "arr[i+1], arr[high] = arr[high], arr[i+1]", pivot_idx=p_pos, low=low, high=high, sorted_idx=sorted_set)
            return p_pos

        def qs(low: int, high: int):
            if low < high:
                pi = partition(low, high)
                qs(low, pi - 1)
                qs(pi + 1, high)
            elif low == high:
                sorted_set.add(low)

        qs(0, len(a) - 1)
        record("Quick sort finished.", "return arr", sorted_idx=set(range(len(a))))

        total = len(frames_data)
        for idx, f in enumerate(frames_data):
            f["step"] = idx + 1
            f["total_steps"] = total
        return frames_data

    # ------------------ SEARCHING ALGORITHMS ------------------

    @staticmethod
    def linear_search(arr: List[int], target: int) -> List[Dict[str, Any]]:
        frames_data: List[Dict[str, Any]] = []
        complexity = {
            "time_best": "O(1)",
            "time_avg": "O(n)",
            "time_worst": "O(n)",
            "space": "O(1)",
            "explanation": "Sequentially inspects each element until target is found or end of list is reached."
        }

        def record(act: str, line: str, curr_idx: int = -1, found: bool = False):
            items = []
            for idx, val in enumerate(arr):
                st = "default"
                if idx == curr_idx:
                    st = "found" if found else "current_search"
                elif idx < curr_idx:
                    st = "checked"
                items.append({"index": idx, "val": val, "state": st})
            frames_data.append({
                "action": act,
                "code_line": line,
                "data_type": "array",
                "state": {"items": items},
                "variables": {"target": target, "current_index": curr_idx},
                "complexity": complexity
            })

        record(f"Starting Linear Search for target = {target}.", "linear_search(arr, target)", -1)

        found = False
        for idx, val in enumerate(arr):
            record(f"Checking arr[{idx}] ({val}) against target ({target}).", "if arr[i] == target:", curr_idx=idx)
            if val == target:
                record(f"Target {target} FOUND at index {idx}!", "return i", curr_idx=idx, found=True)
                found = True
                break

        if not found:
            record(f"Target {target} NOT FOUND in entire array.", "return -1", -1)

        total = len(frames_data)
        for idx, f in enumerate(frames_data):
            f["step"] = idx + 1
            f["total_steps"] = total
        return frames_data

    @staticmethod
    def binary_search(arr: List[int], target: int) -> List[Dict[str, Any]]:
        a = sorted(arr)  # Binary search requires sorted array
        frames_data: List[Dict[str, Any]] = []

        complexity = {
            "time_best": "O(1)",
            "time_avg": "O(log n)",
            "time_worst": "O(log n)",
            "space": "O(1)",
            "explanation": "Halves search interval each step. If target < mid, narrow to left half; else right half."
        }

        def record(act: str, line: str, low: int, mid: int, high: int, found: bool = False):
            items = []
            for idx, val in enumerate(a):
                st = "inactive"
                if low <= idx <= high:
                    st = "default"
                if idx == mid:
                    st = "found" if found else "mid"
                items.append({"index": idx, "val": val, "state": st})
            frames_data.append({
                "action": act,
                "code_line": line,
                "data_type": "array",
                "state": {"items": items},
                "variables": {"target": target, "low": low, "mid": mid, "high": high},
                "complexity": complexity
            })

        low, high = 0, len(a) - 1
        record(f"Initial binary search interval [0..{high}] for target={target}.", "binary_search(arr, target)", low, -1, high)

        found = False
        while low <= high:
            mid = (low + high) // 2
            record(f"Calculated mid = ({low} + {high}) // 2 = {mid}. arr[{mid}] = {a[mid]}.", "mid = (low + high) // 2", low, mid, high)
            if a[mid] == target:
                record(f"Target {target} FOUND at index {mid}!", "return mid", low, mid, high, found=True)
                found = True
                break
            elif a[mid] < target:
                record(f"arr[{mid}] ({a[mid]}) < target ({target}). Target must be in right half.", "low = mid + 1", low, mid, high)
                low = mid + 1
            else:
                record(f"arr[{mid}] ({a[mid]}) > target ({target}). Target must be in left half.", "high = mid - 1", low, mid, high)
                high = mid - 1

        if not found:
            record(f"low > high. Target {target} is NOT present in array.", "return -1", low, -1, high)

        total = len(frames_data)
        for idx, f in enumerate(frames_data):
            f["step"] = idx + 1
            f["total_steps"] = total
        return frames_data

    # ------------------ LINKED LISTS ------------------

    @staticmethod
    def linked_list_reversal(values: List[int]) -> List[Dict[str, Any]]:
        frames_data: List[Dict[str, Any]] = []
        complexity = {
            "time_best": "O(n)",
            "time_avg": "O(n)",
            "time_worst": "O(n)",
            "space": "O(1)",
            "explanation": "Iteratively reverses pointers in-place using three pointers: prev, curr, and next_node."
        }

        # Current pointer states
        def record(act: str, line: str, nodes_state: List[Dict[str, Any]], prev_v: Any, curr_v: Any, next_v: Any):
            frames_data.append({
                "action": act,
                "code_line": line,
                "data_type": "linked_list",
                "state": {"nodes": nodes_state},
                "variables": {"prev": prev_v, "curr": curr_v, "next": next_v},
                "complexity": complexity
            })

        # Initial nodes
        nodes = [{"id": f"node_{i}", "val": v, "next": f"node_{i+1}" if i < len(values)-1 else None} for i, v in enumerate(values)]
        record("Initial singly linked list.", "reverse_list(head)", list(nodes), None, values[0] if values else None, None)

        prev_id = None
        curr_idx = 0

        while curr_idx < len(values):
            curr_id = f"node_{curr_idx}"
            next_id = f"node_{curr_idx + 1}" if curr_idx < len(values) - 1 else None

            record(
                f"Preserve next pointer: next_node = curr.next ({values[curr_idx+1] if curr_idx < len(values)-1 else 'None'}).",
                "next_node = curr.next",
                list(nodes),
                values[curr_idx-1] if curr_idx > 0 else None,
                values[curr_idx],
                values[curr_idx+1] if curr_idx < len(values)-1 else None
            )

            # Reverse pointer
            nodes[curr_idx]["next"] = prev_id
            record(
                f"Reverse pointer: curr.next = prev (points to {values[curr_idx-1] if curr_idx > 0 else 'None'}).",
                "curr.next = prev",
                list(nodes),
                values[curr_idx-1] if curr_idx > 0 else None,
                values[curr_idx],
                values[curr_idx+1] if curr_idx < len(values)-1 else None
            )

            # Move prev and curr
            prev_id = curr_id
            curr_idx += 1
            record(
                "Advance pointers: prev = curr; curr = next_node.",
                "prev, curr = curr, next_node",
                list(nodes),
                values[curr_idx-1],
                values[curr_idx] if curr_idx < len(values) else None,
                None
            )

        record("List reversal complete! prev is new head.", "return prev", list(nodes), values[-1] if values else None, None, None)

        total = len(frames_data)
        for idx, f in enumerate(frames_data):
            f["step"] = idx + 1
            f["total_steps"] = total
        return frames_data

    # ------------------ STACK & QUEUE ------------------

    @staticmethod
    def stack_operations(operations: List[Tuple[str, Any]]) -> List[Dict[str, Any]]:
        frames_data: List[Dict[str, Any]] = []
        stack: List[Any] = []
        complexity = {
            "time_best": "O(1)",
            "time_avg": "O(1)",
            "time_worst": "O(1)",
            "space": "O(n)",
            "explanation": "LIFO (Last-In First-Out). Push and pop operate in O(1) at the top of stack."
        }

        def record(act: str, line: str, top_val: Any = None):
            frames_data.append({
                "action": act,
                "code_line": line,
                "data_type": "stack_queue",
                "state": {
                    "structure": "stack",
                    "items": list(stack),
                    "top": top_val
                },
                "variables": {"size": len(stack), "top": top_val},
                "complexity": complexity
            })

        record("Initialized empty stack.", "stack = []", None)

        for op, val in operations:
            if op == "push":
                stack.append(val)
                record(f"Pushed {val} onto top of stack.", f"stack.append({val})", val)
            elif op == "pop":
                if stack:
                    popped = stack.pop()
                    record(f"Popped {popped} from top of stack.", "val = stack.pop()", stack[-1] if stack else None)
                else:
                    record("Stack underflow: Cannot pop from empty stack!", "# StackUnderflow", None)

        total = len(frames_data)
        for idx, f in enumerate(frames_data):
            f["step"] = idx + 1
            f["total_steps"] = total
        return frames_data

    @staticmethod
    def queue_operations(operations: List[Tuple[str, Any]]) -> List[Dict[str, Any]]:
        frames_data: List[Dict[str, Any]] = []
        queue: List[Any] = []
        complexity = {
            "time_best": "O(1)",
            "time_avg": "O(1)",
            "time_worst": "O(1)",
            "space": "O(n)",
            "explanation": "FIFO (First-In First-Out). Enqueue at rear, dequeue from front."
        }

        def record(act: str, line: str):
            frames_data.append({
                "action": act,
                "code_line": line,
                "data_type": "stack_queue",
                "state": {
                    "structure": "queue",
                    "items": list(queue),
                    "front": queue[0] if queue else None,
                    "rear": queue[-1] if queue else None
                },
                "variables": {"size": len(queue), "front": queue[0] if queue else None, "rear": queue[-1] if queue else None},
                "complexity": complexity
            })

        record("Initialized empty queue.", "queue = deque()", )

        for op, val in operations:
            if op == "enqueue":
                queue.append(val)
                record(f"Enqueued {val} at rear of queue.", f"queue.append({val})")
            elif op == "dequeue":
                if queue:
                    dequeued = queue.pop(0)
                    record(f"Dequeued {dequeued} from front of queue.", "val = queue.popleft()")
                else:
                    record("Queue underflow: queue is empty!", "# QueueUnderflow")

        total = len(frames_data)
        for idx, f in enumerate(frames_data):
            f["step"] = idx + 1
            f["total_steps"] = total
        return frames_data

    # ------------------ BINARY TREE & BST ------------------

    @staticmethod
    def bst_traversal(values: List[int], mode: str = "inorder") -> List[Dict[str, Any]]:
        frames_data: List[Dict[str, Any]] = []
        complexity = {
            "time_best": "O(n)",
            "time_avg": "O(n)",
            "time_worst": "O(n)",
            "space": "O(h)",
            "explanation": f"Tree traversal visits each node once. Inorder produces sorted order for BST. Height h determines stack space."
        }

        # Build BST
        class BSTNode:
            def __init__(self, val: int, nid: str):
                self.val = val
                self.id = nid
                self.left = None
                self.right = None
                self.x = 0
                self.y = 0

        root = None
        counter = 0

        def insert(node: Optional[BSTNode], val: int) -> BSTNode:
            nonlocal counter
            if not node:
                counter += 1
                return BSTNode(val, f"node_{counter}")
            if val < node.val:
                node.left = insert(node.left, val)
            else:
                node.right = insert(node.right, val)
            return node

        for v in values:
            root = insert(root, v)

        # Calculate coordinates for visualization
        def assign_coords(node: Optional[BSTNode], x: float, y: float, spread: float):
            if not node:
                return
            node.x = x
            node.y = y
            if node.left:
                assign_coords(node.left, x - spread, y + 60, spread / 2.0)
            if node.right:
                assign_coords(node.right, x + spread, y + 60, spread / 2.0)

        assign_coords(root, 300, 40, 120)

        # Serialize tree snapshot
        def get_tree_snapshot(active_id: Optional[str], visited_ids: Set[str]) -> Dict[str, Any]:
            nodes_list = []
            edges_list = []

            def collect(node: Optional[BSTNode]):
                if not node:
                    return
                st = "default"
                if node.id == active_id:
                    st = "active"
                elif node.id in visited_ids:
                    st = "visited"
                nodes_list.append({"id": node.id, "val": node.val, "x": node.x, "y": node.y, "state": st})
                if node.left:
                    edges_list.append({"from": node.id, "to": node.left.id, "side": "L"})
                    collect(node.left)
                if node.right:
                    edges_list.append({"from": node.id, "to": node.right.id, "side": "R"})
                    collect(node.right)

            collect(root)
            return {"nodes": nodes_list, "edges": edges_list}

        visited: Set[str] = set()
        traversal_order: List[int] = []

        def record(act: str, line: str, active_id: Optional[str] = None):
            frames_data.append({
                "action": act,
                "code_line": line,
                "data_type": "tree",
                "state": get_tree_snapshot(active_id, visited),
                "variables": {"traversed": list(traversal_order)},
                "complexity": complexity
            })

        record(f"Constructed BST from input values: {values}. Starting {mode} traversal.", f"traverse_{mode}(root)", None)

        def inorder(node: Optional[BSTNode]):
            if not node:
                return
            record(f"Visit left subtree of node {node.val}.", "inorder(node.left)", node.id)
            inorder(node.left)

            record(f"Process node {node.val}.", f"print({node.val})", node.id)
            visited.add(node.id)
            traversal_order.append(node.val)
            record(f"Appended {node.val} to traversal result: {traversal_order}.", "result.append(node.val)", node.id)

            record(f"Visit right subtree of node {node.val}.", "inorder(node.right)", node.id)
            inorder(node.right)

        def preorder(node: Optional[BSTNode]):
            if not node:
                return
            record(f"Process node {node.val}.", f"print({node.val})", node.id)
            visited.add(node.id)
            traversal_order.append(node.val)

            record(f"Visit left subtree of node {node.val}.", "preorder(node.left)", node.id)
            preorder(node.left)

            record(f"Visit right subtree of node {node.val}.", "preorder(node.right)", node.id)
            preorder(node.right)

        def postorder(node: Optional[BSTNode]):
            if not node:
                return
            record(f"Visit left subtree of node {node.val}.", "postorder(node.left)", node.id)
            postorder(node.left)

            record(f"Visit right subtree of node {node.val}.", "postorder(node.right)", node.id)
            postorder(node.right)

            record(f"Process node {node.val}.", f"print({node.val})", node.id)
            visited.add(node.id)
            traversal_order.append(node.val)

        if mode == "preorder":
            preorder(root)
        elif mode == "postorder":
            postorder(root)
        else:
            inorder(root)

        record(f"{mode.capitalize()} traversal finished! Output: {traversal_order}.", "return result", None)

        total = len(frames_data)
        for idx, f in enumerate(frames_data):
            f["step"] = idx + 1
            f["total_steps"] = total
        return frames_data

    # ------------------ GRAPHS (BFS / DFS / DIJKSTRA) ------------------

    @staticmethod
    def graph_traversal(mode: str = "bfs", start_node: str = "A") -> List[Dict[str, Any]]:
        frames_data: List[Dict[str, Any]] = []

        # Sample graph definition
        graph = {
            "A": ["B", "C"],
            "B": ["A", "D", "E"],
            "C": ["A", "F"],
            "D": ["B"],
            "E": ["B", "F"],
            "F": ["C", "E"]
        }

        node_positions = {
            "A": (200, 60),
            "B": (100, 160),
            "C": (300, 160),
            "D": (50, 260),
            "E": (160, 260),
            "F": (300, 260)
        }

        complexity = {
            "time_best": "O(V + E)",
            "time_avg": "O(V + E)",
            "time_worst": "O(V + E)",
            "space": "O(V)",
            "explanation": "Visits all vertices V and edges E using queue (BFS) or stack/recursion (DFS)."
        }

        def record(act: str, line: str, curr_v: Optional[str], visited_set: Set[str], queue_list: List[str], active_edge: Tuple[str, str] = None):
            nodes_info = []
            for n_id, pos in node_positions.items():
                st = "default"
                if n_id == curr_v:
                    st = "current"
                elif n_id in visited_set:
                    st = "visited"
                elif n_id in queue_list:
                    st = "queued"
                nodes_info.append({"id": n_id, "x": pos[0], "y": pos[1], "state": st})

            edges_info = []
            seen_edges = set()
            for u, neighbors in graph.items():
                for v in neighbors:
                    edge_key = tuple(sorted([u, v]))
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        is_active = (active_edge and ((u == active_edge[0] and v == active_edge[1]) or (v == active_edge[0] and u == active_edge[1])))
                        edges_info.append({"from": u, "to": v, "is_active": is_active})

            frames_data.append({
                "action": act,
                "code_line": line,
                "data_type": "graph",
                "state": {"nodes": nodes_info, "edges": edges_info},
                "variables": {"current": curr_v, "visited": sorted(list(visited_set)), "queue_or_stack": list(queue_list)},
                "complexity": complexity
            })

        visited: Set[str] = set()

        if mode == "bfs":
            queue = [start_node]
            visited.add(start_node)
            record(f"Starting BFS from node {start_node}. Enqueue {start_node}.", "queue.append(start)", start_node, visited, queue)

            while queue:
                u = queue.pop(0)
                record(f"Dequeued node {u}.", "u = queue.popleft()", u, visited, queue)
                for v in graph.get(u, []):
                    record(f"Checking edge ({u} - {v}).", "for v in graph[u]:", u, visited, queue, active_edge=(u, v))
                    if v not in visited:
                        visited.add(v)
                        queue.append(v)
                        record(f"Node {v} unvisited. Marked visited and enqueued.", "queue.append(v)", u, visited, queue)

            record("BFS traversal completed.", "return visited", None, visited, [])
        else:
            # DFS
            stack = [start_node]
            record(f"Starting DFS from node {start_node}. Push {start_node} onto stack.", "stack.append(start)", start_node, visited, stack)

            while stack:
                u = stack.pop()
                if u not in visited:
                    visited.add(u)
                    record(f"Popped and visited node {u}.", "visited.add(u)", u, visited, stack)
                    for v in reversed(graph.get(u, [])):
                        if v not in visited:
                            stack.append(v)
                            record(f"Pushed unvisited neighbor {v} onto stack.", "stack.append(v)", u, visited, stack, active_edge=(u, v))

            record("DFS traversal completed.", "return visited", None, visited, [])

        total = len(frames_data)
        for idx, f in enumerate(frames_data):
            f["step"] = idx + 1
            f["total_steps"] = total
        return frames_data

    # ------------------ RECURSION (FIBONACCI & FACTORIAL) ------------------

    @staticmethod
    def fibonacci_recursion(n: int = 4) -> List[Dict[str, Any]]:
        n = min(n, 5)  # Cap for clarity
        frames_data: List[Dict[str, Any]] = []

        complexity = {
            "time_best": "O(2ⁿ)",
            "time_avg": "O(2ⁿ)",
            "time_worst": "O(2ⁿ)",
            "space": "O(n)",
            "explanation": "Naïve recursion creates an exponential call tree with 2ⁿ calls and O(n) call-stack depth."
        }

        call_stack: List[str] = []

        def record(act: str, line: str, curr_call: str, result: Optional[int] = None):
            frames_data.append({
                "action": act,
                "code_line": line,
                "data_type": "recursion",
                "state": {"call_stack": list(call_stack)},
                "variables": {"current_call": curr_call, "result": result},
                "complexity": complexity
            })

        def fib(k: int) -> int:
            call_label = f"fib({k})"
            call_stack.append(call_label)
            record(f"Call {call_label} pushed to call stack.", f"fib({k})", call_label)

            if k <= 1:
                res = k
                record(f"Base case reached: {call_label} returns {res}.", f"return {k}", call_label, res)
                call_stack.pop()
                return res

            record(f"{call_label} recursively calls fib({k-1}).", f"fib({k-1}) + fib({k-2})", call_label)
            res1 = fib(k - 1)

            record(f"{call_label} recursively calls fib({k-2}).", f"fib({k-2})", call_label)
            res2 = fib(k - 2)

            res = res1 + res2
            record(f"{call_label} sums results: {res1} + {res2} = {res}.", f"return {res}", call_label, res)
            call_stack.pop()
            return res

        final_res = fib(n)
        record(f"Fibonacci recursion complete! fib({n}) = {final_res}.", "return final_result", f"fib({n})", final_res)

        total = len(frames_data)
        for idx, f in enumerate(frames_data):
            f["step"] = idx + 1
            f["total_steps"] = total
        return frames_data
