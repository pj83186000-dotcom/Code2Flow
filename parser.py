"""
Code2Flow - Python AST Parser and Source Validator
Handles parsing, syntax validation, AST traversal, and node categorization.
Fully compatible with Python 3.10 through Python 3.14+.
"""

import ast
import sys
from typing import Dict, Any, List, Optional, Tuple


class ParseError:
    """Represents a syntax or validation error with contextual details."""
    def __init__(self, message: str, lineno: Optional[int] = None, col_offset: Optional[int] = None, text: Optional[str] = None):
        self.message = message
        self.lineno = lineno
        self.col_offset = col_offset
        self.text = text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "lineno": self.lineno,
            "col_offset": self.col_offset,
            "text": self.text
        }


def safe_unparse(node: ast.AST) -> str:
    """Safely unparse an AST node to source text across Python 3.10-3.14+."""
    try:
        return ast.unparse(node).strip()
    except Exception:
        # Fallback for special or unparseable nodes
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        return type(node).__name__


class SourceParser:
    """Validates and parses Python source code into AST."""

    MAX_CODE_LENGTH = 100_000  # 100KB safety guard for browser/educational demo
    MAX_NESTING_DEPTH = 50

    @classmethod
    def validate_and_parse(cls, source_code: str) -> Tuple[Optional[ast.Module], Optional[ParseError], List[str]]:
        """
        Validates source code and returns (ast_tree, parse_error, warnings).
        """
        warnings: List[str] = []
        if not source_code or not source_code.strip():
            return None, ParseError("Source code is empty. Please enter Python code to visualize."), warnings

        if len(source_code) > cls.MAX_CODE_LENGTH:
            return None, ParseError(f"Source code exceeds maximum allowed size ({cls.MAX_CODE_LENGTH} characters)."), warnings

        # Check line count
        lines = source_code.splitlines()
        if len(lines) > 2000:
            warnings.append(f"Source code has {len(lines)} lines; visualization may be large.")

        try:
            tree = ast.parse(source_code, filename="<code2flow>")
        except IndentationError as e:
            line_content = lines[e.lineno - 1] if e.lineno and e.lineno <= len(lines) else (e.text or "")
            return None, ParseError(
                f"Indentation Error: {e.msg} (Line {e.lineno})",
                lineno=e.lineno,
                col_offset=e.offset,
                text=line_content.strip() if line_content else None
            ), warnings
        except SyntaxError as e:
            line_content = lines[e.lineno - 1] if e.lineno and e.lineno <= len(lines) else (e.text or "")
            return None, ParseError(
                f"Syntax Error: {e.msg} (Line {e.lineno})",
                lineno=e.lineno,
                col_offset=e.offset,
                text=line_content.strip() if line_content else None
            ), warnings
        except Exception as e:
            return None, ParseError(f"Parsing failed: {str(e)}"), warnings

        # Check depth
        depth = cls._compute_max_depth(tree)
        if depth > cls.MAX_NESTING_DEPTH:
            warnings.append(f"AST nesting depth is {depth}, which is very high. Diagram may be deep.")

        return tree, None, warnings

    @classmethod
    def _compute_max_depth(cls, node: ast.AST, current_depth: int = 1) -> int:
        max_d = current_depth
        for child in ast.iter_child_nodes(node):
            d = cls._compute_max_depth(child, current_depth + 1)
            if d > max_d:
                max_d = d
        return max_d

    @staticmethod
    def classify_statement(node: ast.AST) -> str:
        """
        Classifies an AST statement node into flowchart semantic categories:
        - 'start' / 'end'
        - 'io_input': input(...)
        - 'io_output': print(...)
        - 'decision': if, while, for condition
        - 'process': assignments, expressions, operations
        - 'loop_header': for, while
        - 'branch': if/elif
        - 'exception': try/except/raise
        - 'jump': break, continue, return
        """
        if isinstance(node, (ast.If, ast.IfExp)):
            return "decision"
        elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            return "loop_header"
        elif isinstance(node, (ast.Break, ast.Continue)):
            return "jump"
        elif isinstance(node, ast.Return):
            return "return"
        elif isinstance(node, (ast.Try, ast.TryStar if hasattr(ast, "TryStar") else ast.Try)):
            return "try_header"
        elif isinstance(node, ast.Raise):
            return "raise"
        elif isinstance(node, ast.Pass):
            return "process"
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            # Check if right hand side is input()
            val = getattr(node, "value", None)
            if val and isinstance(val, ast.Call) and isinstance(val.func, ast.Name) and val.func.id == "input":
                return "io_input"
            return "process"
        elif isinstance(node, ast.Expr):
            # Check if call is print() or input()
            if isinstance(node.value, ast.Call):
                func = node.value.func
                if isinstance(func, ast.Name):
                    if func.id == "print":
                        return "io_output"
                    elif func.id == "input":
                        return "io_input"
            return "process"
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return "function_def"
        elif isinstance(node, ast.ClassDef):
            return "class_def"
        elif hasattr(ast, "Match") and isinstance(node, ast.Match):
            return "decision"
        return "process"

    @staticmethod
    def is_recursive_call(func_name: str, node: ast.AST) -> bool:
        """Checks if an AST node contains a direct recursive call to func_name."""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name) and child.func.id == func_name:
                    return True
        return False
