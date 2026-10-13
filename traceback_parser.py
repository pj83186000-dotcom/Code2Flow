"""
Code2Flow - Multi-Language Traceback & Error Debugging Engine
Parses Python, JavaScript, Java, and C/C++ stack traces and compiler errors,
maps error locations to flowchart nodes, and provides beginner-friendly guidance.
"""

import re
import os
from typing import Dict, Any, List, Optional, Tuple


EXCEPTION_GUIDE: Dict[str, Dict[str, str]] = {
    # Python Exceptions
    "ZeroDivisionError": {
        "title": "Division by Zero",
        "explanation": "You tried to divide by zero (divide a number by 0), which is mathematically undefined in Python.",
        "suggestion": "Check the divisor variable before dividing, or add a condition: if divisor != 0: ... else: ..."
    },
    "IndexError": {
        "title": "List / Sequence Index Out of Range",
        "explanation": "You tried to access an element at an index that doesn't exist in the list or sequence.",
        "suggestion": "Remember that Python uses 0-based indexing (valid indices are 0 to len-1). Check len(sequence) before indexing."
    },
    "KeyError": {
        "title": "Dictionary Key Not Found",
        "explanation": "The dictionary does not contain the key you requested.",
        "suggestion": "Use dict.get(key, default) or check 'if key in my_dict:' before accessing."
    },
    "TypeError": {
        "title": "Type Mismatch / Incompatible Operation",
        "explanation": "An operation or function call was applied to an object of inappropriate type (e.g. adding string and integer).",
        "suggestion": "Verify variable data types using type() or cast explicitly using int(), str(), or float()."
    },
    "ValueError": {
        "title": "Invalid Value for Type",
        "explanation": "A function received an argument that has the right type but an inappropriate value (e.g. int('hello')).",
        "suggestion": "Validate user input format or use try...except ValueError around conversions."
    },
    "NameError": {
        "title": "Undefined Variable or Name",
        "explanation": "Python encountered an identifier that hasn't been declared or assigned in the current scope.",
        "suggestion": "Check for typos in variable names, or ensure the variable is assigned before being referenced."
    },
    "AttributeError": {
        "title": "Attribute or Method Missing",
        "explanation": "You tried to access an attribute or method that does not exist on this object, or the object is None.",
        "suggestion": "Verify object type, check if the variable was unexpectedly None, and inspect available attributes using dir(obj)."
    },

    # JavaScript Errors
    "ReferenceError": {
        "title": "JS ReferenceError (Undefined Identifier)",
        "explanation": "You referenced a variable that has not been declared with let, const, or var.",
        "suggestion": "Check spelling and ensure the variable is declared in the current or parent scope."
    },
    "NullPointerException": {
        "title": "Java NullPointerException",
        "explanation": "Attempted to access a member or method of an object reference that is currently null.",
        "suggestion": "Ensure the object is instantiated with 'new ClassName()' before calling methods on it."
    },
    "ArrayIndexOutOfBoundsException": {
        "title": "Java Array Index Out Of Bounds",
        "explanation": "Array index accessed is negative or greater than or equal to the size of the array.",
        "suggestion": "Verify loop bounds (e.g. use 'i < array.length' instead of 'i <= array.length')."
    },
    "SegmentationFault": {
        "title": "C/C++ Segmentation Fault",
        "explanation": "Program attempted to access a memory location it does not have permission to read/write (e.g. null or dangling pointer).",
        "suggestion": "Check pointer initialization, array bounds, and ensure pointers are not accessed after free()/delete."
    }
}


class TracebackFrame:
    """Represents a single parsed stack frame from a traceback."""
    def __init__(
        self,
        filename: str,
        lineno: int,
        function: str,
        code_line: str,
        is_user_code: bool = True
    ):
        self.filename = filename
        self.lineno = lineno
        self.function = function
        self.code_line = code_line
        self.is_user_code = is_user_code

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "lineno": self.lineno,
            "function": self.function,
            "code_line": self.code_line,
            "is_user_code": self.is_user_code
        }


class TracebackAnalysis:
    """Parsed result of a traceback or compiler error."""
    def __init__(
        self,
        exception_type: str,
        exception_message: str,
        frames: List[TracebackFrame],
        matched_node_id: Optional[str] = None,
        matched_lineno: Optional[int] = None,
        context_lines: Optional[List[Dict[str, Any]]] = None,
        guide: Optional[Dict[str, str]] = None,
        status: str = "success",
        notes: str = ""
    ):
        self.exception_type = exception_type
        self.exception_message = exception_message
        self.frames = frames
        self.matched_node_id = matched_node_id
        self.matched_lineno = matched_lineno
        self.context_lines = context_lines or []
        self.guide = guide
        self.status = status
        self.notes = notes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
            "frames": [f.to_dict() for f in self.frames],
            "matched_node_id": self.matched_node_id,
            "matched_lineno": self.matched_lineno,
            "context_lines": self.context_lines,
            "guide": self.guide,
            "status": self.status,
            "notes": self.notes
        }


class TracebackParser:
    """Multi-language traceback and error parser (Python, JS, Java, C/C++)."""

    # Python: File "...", line 12, in func
    PY_FRAME_REGEX = re.compile(r'File "(?P<file>[^"]+)", line (?P<line>\d+)(?:, in (?P<func>.+))?')

    # JavaScript: at func (file.js:14:5) or at file.js:14:5
    JS_FRAME_REGEX = re.compile(r'at\s+(?:(?P<func>[^\s(]+)\s+\()?(?P<file>[^:()]+):(?P<line>\d+):(?P<col>\d+)\)?')

    # Java: at package.Class.method(Class.java:14)
    JAVA_FRAME_REGEX = re.compile(r'at\s+(?P<func>[A-Za-z0-9_$.]+)\((?P<file>[A-Za-z0-9_]+(?:\.java)?):(?P<line>\d+)\)')

    # C/C++: main.cpp:14:5: error: ...
    CPP_ERROR_REGEX = re.compile(r'(?P<file>[A-Za-z0-9_./\\-]+\.(?:c|cpp|cc|h|hpp)):(?P<line>\d+):(?P<col>\d+)?:?\s*(?:error|warning)?:\s*(?P<msg>.*)')

    @classmethod
    def parse_and_map(
        cls,
        traceback_text: str,
        source_code: str,
        flowchart_nodes: List[Dict[str, Any]],
        language: str = "python"
    ) -> TracebackAnalysis:
        if not traceback_text or not traceback_text.strip():
            return TracebackAnalysis(
                exception_type="None",
                exception_message="No traceback provided.",
                frames=[],
                status="empty",
                notes="Paste an error or traceback to locate the offending node."
            )

        tb_lines = traceback_text.strip().splitlines()
        frames: List[TracebackFrame] = []
        exception_type = "Error"
        exception_message = ""

        # Check C/C++ compiler error format first
        for line in tb_lines:
            cpp_match = cls.CPP_ERROR_REGEX.search(line)
            if cpp_match:
                exception_type = "CompilerError"
                exception_message = cpp_match.group("msg") or "C/C++ compilation error"
                frames.append(TracebackFrame(
                    filename=cpp_match.group("file"),
                    lineno=int(cpp_match.group("line")),
                    function="<source>",
                    code_line="",
                    is_user_code=True
                ))

        # Check Python frames
        if not frames:
            i = 0
            while i < len(tb_lines):
                line = tb_lines[i].strip()
                py_m = cls.PY_FRAME_REGEX.search(line)
                if py_m:
                    fn = py_m.group("file")
                    ln = int(py_m.group("line"))
                    func = py_m.group("func") or "<module>"
                    code_snippet = ""
                    if i + 1 < len(tb_lines) and not tb_lines[i + 1].strip().startswith("File "):
                        code_snippet = tb_lines[i + 1].strip()
                        i += 1
                    frames.append(TracebackFrame(
                        filename=fn,
                        lineno=ln,
                        function=func,
                        code_line=code_snippet,
                        is_user_code="site-packages" not in fn and "/lib/" not in fn
                    ))
                else:
                    # Exception name line
                    exc_m = re.match(r"^([A-Za-z0-9_]+(?:Error|Exception)?):?\s*(.*)$", line)
                    if exc_m:
                        exception_type = exc_m.group(1)
                        exception_message = exc_m.group(2)
                i += 1

        # Check JavaScript frames
        if not frames:
            for line in tb_lines:
                js_m = cls.JS_FRAME_REGEX.search(line)
                if js_m:
                    frames.append(TracebackFrame(
                        filename=js_m.group("file"),
                        lineno=int(js_m.group("line")),
                        function=js_m.group("func") or "<anonymous>",
                        code_line="",
                        is_user_code=True
                    ))
                elif "Error:" in line or "Exception:" in line:
                    parts = line.split(":", 1)
                    exception_type = parts[0].strip()
                    exception_message = parts[1].strip() if len(parts) > 1 else ""

        # Check Java frames
        if not frames:
            for line in tb_lines:
                java_m = cls.JAVA_FRAME_REGEX.search(line)
                if java_m:
                    frames.append(TracebackFrame(
                        filename=java_m.group("file"),
                        lineno=int(java_m.group("line")),
                        function=java_m.group("func"),
                        code_line="",
                        is_user_code=True
                    ))
                elif "Exception in thread" in line or "Exception:" in line:
                    m = re.search(r"([A-Za-z0-9_]+Exception)(?::\s*(.*))?", line)
                    if m:
                        exception_type = m.group(1)
                        exception_message = m.group(2) or ""

        # Innermost frame (Python prints caller-first callee-last; JS and Java print callee-first)
        target_frame = None
        search_frames = frames if language in ("javascript", "java") else list(reversed(frames))
        for f in search_frames:
            if f.is_user_code:
                target_frame = f
                break
        if not target_frame and frames:
            target_frame = search_frames[0]

        target_lineno = target_frame.lineno if target_frame else None
        source_lines = source_code.splitlines()
        matched_node_id = None
        notes = ""

        if target_lineno is not None:
            matched_node_id, notes = cls._match_node_by_line(target_lineno, flowchart_nodes, len(source_lines))
        else:
            notes = "Could not parse a stack frame line number."

        # Source context
        context_lines = []
        if target_lineno is not None and 1 <= target_lineno <= len(source_lines):
            start = max(1, target_lineno - 3)
            end = min(len(source_lines), target_lineno + 3)
            for idx in range(start, end + 1):
                context_lines.append({
                    "lineno": idx,
                    "code": source_lines[idx - 1],
                    "is_error": (idx == target_lineno)
                })

        guide = EXCEPTION_GUIDE.get(exception_type, {
            "title": exception_type,
            "explanation": f"A runtime {exception_type} was reported during execution.",
            "suggestion": "Check argument types, variable bounds, and ensure statements are guarded."
        })

        return TracebackAnalysis(
            exception_type=exception_type,
            exception_message=exception_message,
            frames=frames,
            matched_node_id=matched_node_id,
            matched_lineno=target_lineno,
            context_lines=context_lines,
            guide=guide,
            status="matched" if matched_node_id else "unmatched",
            notes=notes
        )

    @classmethod
    def _match_node_by_line(
        cls,
        target_lineno: int,
        flowchart_nodes: List[Dict[str, Any]],
        total_source_lines: int
    ) -> Tuple[Optional[str], str]:
        if target_lineno > total_source_lines:
            return None, f"Line {target_lineno} exceeds source length ({total_source_lines} lines)."

        # 1. Exact match
        for n in flowchart_nodes:
            if n.get("lineno") == target_lineno:
                return n["id"], f"Direct match at line {target_lineno}."

        # 2. Span match
        for n in flowchart_nodes:
            if n.get("lineno") and n.get("end_lineno") and n["lineno"] <= target_lineno <= n["end_lineno"]:
                return n["id"], f"Located within block at lines {n['lineno']}-{n['end_lineno']}."

        # 3. Nearest preceding node
        candidates = [n for n in flowchart_nodes if n.get("lineno") and 0 <= target_lineno - n["lineno"] <= 3]
        if candidates:
            candidates.sort(key=lambda n: target_lineno - n["lineno"])
            return candidates[0]["id"], f"Matched nearest node at line {candidates[0]['lineno']}."

        return None, f"No flowchart node matched line {target_lineno}."
