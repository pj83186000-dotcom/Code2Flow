import ast
import sys
import io
import re
import traceback


def classify_value(val):
    if isinstance(val, list):
        if val and all(isinstance(x, (int, float)) for x in val):
            return "array"
        return "list"
    if isinstance(val, dict):
        return "dict"
    if isinstance(val, (set, frozenset)):
        return "set"
    if isinstance(val, (int, float, bool, str)) or val is None:
        return "primitive"
    return "object"


def _safe_repr(val, max_depth=3):
    if max_depth <= 0:
        return "..."
    if val is None or isinstance(val, (bool, int, float, str)):
        return val
    if isinstance(val, (list, tuple)):
        return [_safe_repr(v, max_depth - 1) for v in val]
    if isinstance(val, dict):
        return {str(k): _safe_repr(v, max_depth - 1) for k, v in list(val.items())[:30]}
    if isinstance(val, (set, frozenset)):
        return sorted([_safe_repr(v, max_depth - 1) for v in val], key=str)
    try:
        return repr(val)[:120]
    except Exception:
        return "<object>"


class _Tracer:
    MAX_STEPS = 800
    MAX_LIST_LEN = 64

    def __init__(self, source_lines):
        self.source_lines = source_lines
        self.frames = []
        self._call_stack = []
        self._step = 0
        self._stdout_buf = io.StringIO()
        self._prev_locals = {}

    def __call__(self, frame, event, arg):
        if self._step >= self.MAX_STEPS:
            return None
        if event == "call":
            fn = frame.f_code.co_name
            if fn != "<module>":
                self._call_stack.append(fn)
            return self
        if event == "return":
            if self._call_stack:
                self._call_stack.pop()
            return self
        if event == "line":
            lineno = frame.f_lineno
            line_text = ""
            if 1 <= lineno <= len(self.source_lines):
                line_text = self.source_lines[lineno - 1].rstrip()
            locals_snap = self._snapshot_locals(frame.f_locals)
            changed = self._changed_vars(locals_snap)
            frame_obj = {
                "step": self._step + 1,
                "lineno": lineno,
                "line": line_text,
                "event": "line",
                "scope": frame.f_code.co_name,
                "call_stack": list(self._call_stack),
                "variables": locals_snap,
                "changed": changed,
                "output": self._stdout_buf.getvalue(),
                "highlight": {
                    "indices": self._extract_indices(frame.f_locals),
                    "comparisons": [],
                    "swaps": []
                }
            }
            self.frames.append(frame_obj)
            self._prev_locals = locals_snap
            self._step += 1
            return self
        return self

    def _snapshot_locals(self, raw_locals):
        snap = {}
        for k, v in raw_locals.items():
            if k.startswith("_"):
                continue
            if isinstance(v, list) and len(v) > self.MAX_LIST_LEN:
                snap[k] = {"type": "array", "value": v[:self.MAX_LIST_LEN], "truncated": True}
            else:
                try:
                    snap[k] = {"type": classify_value(v), "value": _safe_repr(v)}
                except Exception:
                    snap[k] = {"type": "object", "value": "?"}
        return snap

    def _changed_vars(self, current):
        changed = []
        for k, v in current.items():
            if k not in self._prev_locals:
                changed.append(k)
            elif self._prev_locals[k] != v:
                changed.append(k)
        return changed

    def _extract_indices(self, raw_locals):
        idx = {}
        pointer_names = {"i", "j", "k", "l", "r", "m", "lo", "hi", "low",
                         "high", "left", "right", "mid", "pivot", "p", "q", "n"}
        for k, v in raw_locals.items():
            if k.startswith("_"):
                continue
            if isinstance(v, int) and k in pointer_names:
                idx[k] = v
        return idx


class MultiLangTracer(_Tracer):
    def __init__(self, source_lines, line_map):
        super().__init__(source_lines)
        self.line_map = line_map

    def __call__(self, frame, event, arg):
        if self._step >= self.MAX_STEPS:
            return None
        if event == "call":
            fn = frame.f_code.co_name
            if fn not in ("<module>", "main"):
                self._call_stack.append(fn)
            return self
        if event == "return":
            if self._call_stack:
                self._call_stack.pop()
            return self
        if event == "line":
            py_lineno = frame.f_lineno
            orig_lineno = self.line_map.get(py_lineno, py_lineno)
            line_text = ""
            if 1 <= orig_lineno <= len(self.source_lines):
                line_text = self.source_lines[orig_lineno - 1].rstrip()
            locals_snap = self._snapshot_locals(frame.f_locals)
            changed = self._changed_vars(locals_snap)
            frame_obj = {
                "step": self._step + 1,
                "lineno": orig_lineno,
                "line": line_text,
                "event": "line",
                "scope": frame.f_code.co_name,
                "call_stack": list(self._call_stack),
                "variables": locals_snap,
                "changed": changed,
                "output": self._stdout_buf.getvalue(),
                "highlight": {
                    "indices": self._extract_indices(frame.f_locals),
                    "comparisons": [],
                    "swaps": []
                }
            }
            self.frames.append(frame_obj)
            self._prev_locals = locals_snap
            self._step += 1
            return self
        return self


def extract_parentheses_content(s):
    start = s.find("(")
    if start == -1:
        return s
    count = 0
    for idx in range(start, len(s)):
        if s[idx] == "(":
            count += 1
        elif s[idx] == ")":
            count -= 1
            if count == 0:
                return s[start + 1:idx]
    return s[start + 1:]


def clean_expr(expr):
    e = expr.strip()
    e = re.sub(r"(\w+)\.length\b", r"len(\1)", e)
    e = re.sub(r"(\w+)\.size\(\)", r"len(\1)", e)
    e = re.sub(r"(\w+)\.getMessage\(\)", r"str(\1)", e)
    e = re.sub(r"(\w+)\.toString\(\)", r"str(\1)", e)
    e = re.sub(r"\btrue\b", "True", e)
    e = re.sub(r"\bfalse\b", "False", e)
    e = re.sub(r"\bnull\b", "None", e)
    e = re.sub(r"&&", " and ", e)
    e = re.sub(r"\|\|", " or ", e)
    e = re.sub(r"!([a-zA-Z_])", r"not \1", e)
    e = re.sub(r"===?", "==", e)
    e = re.sub(r"!==?", "!=", e)

    if '"' in e or "'" in e:
        parts = e.split("+")
        if len(parts) > 1:
            clean_parts = []
            for p in parts:
                p = p.strip()
                if (p.startswith('"') and p.endswith('"')) or (p.startswith("'") and p.endswith("'")):
                    clean_parts.append(p)
                else:
                    clean_parts.append(f"str({p})")
            e = " + ".join(clean_parts)
    return e


def transpile_c_style_to_python(source, language="java"):
    raw_lines = source.splitlines()

    combined_lines = []
    line_origins = []

    buf = ""
    buf_origins = []
    paren_depth = 0

    for idx, r_line in enumerate(raw_lines):
        orig_no = idx + 1
        stripped = r_line.strip()

        in_quote = False
        quote_char = ''
        p_delta = 0
        for ch in stripped:
            if ch in ('"', "'") and not in_quote:
                in_quote = True
                quote_char = ch
            elif in_quote and ch == quote_char:
                in_quote = False
            elif not in_quote:
                if ch == '(':
                    p_delta += 1
                elif ch == ')':
                    p_delta -= 1

        if buf:
            buf += " " + stripped
            buf_origins.append(orig_no)
            paren_depth += p_delta
            if paren_depth <= 0 or stripped.endswith(";") or stripped.endswith("{"):
                combined_lines.append(buf)
                line_origins.append(buf_origins)
                buf = ""
                buf_origins = []
                paren_depth = 0
        else:
            paren_depth = p_delta
            if paren_depth > 0 and not (stripped.endswith(";") or stripped.endswith("{")):
                buf = stripped
                buf_origins = [orig_no]
            else:
                combined_lines.append(stripped)
                line_origins.append([orig_no])
                paren_depth = 0

    out_lines = []
    line_map = {}

    block_stack = []
    current_indent = 0
    main_found = False

    def emit(py_line, orig_no, indent_lvl=None):
        nonlocal current_indent
        if indent_lvl is None:
            indent_lvl = current_indent
        prefix = "    " * max(0, indent_lvl)
        out_lines.append(prefix + py_line if py_line else "")
        line_map[len(out_lines)] = orig_no

    for idx, line in enumerate(combined_lines):
        orig_nos = line_origins[idx]
        orig_no = orig_nos[0] if orig_nos else idx + 1

        if not line:
            emit("", orig_no)
            continue

        if line.startswith("//") or line.startswith("/*") or line.startswith("*"):
            emit(f"# {line}", orig_no)
            continue

        if line.startswith("package ") or line.startswith("import ") or line.startswith("#include") or line.startswith("using namespace"):
            emit(f"# {line}", orig_no)
            continue

        # Class declaration
        if re.match(r"^(?:public\s+|private\s+|protected\s+)?(?:final\s+|abstract\s+)?class\s+\w+", line):
            block_stack.append({'type': 'class', 'orig_line': orig_no})
            continue

        if line == "}":
            if block_stack:
                b = block_stack.pop()
                if b['type'] == 'for' and b.get('step'):
                    emit(b['step'], orig_no, current_indent)
                if b['type'] == 'case':
                    current_indent = max(0, current_indent - 1)
                    if block_stack and block_stack[-1]['type'] == 'switch':
                        block_stack.pop()
                elif b['type'] != 'class':
                    current_indent = max(0, current_indent - 1)
            continue

        if line.startswith("}"):
            if block_stack:
                b = block_stack.pop()
                if b['type'] == 'for' and b.get('step'):
                    emit(b['step'], orig_no, current_indent)
                if b['type'] == 'case':
                    current_indent = max(0, current_indent - 1)
                    if block_stack and block_stack[-1]['type'] == 'switch':
                        block_stack.pop()
                elif b['type'] != 'class':
                    current_indent = max(0, current_indent - 1)
            line = line[1:].strip()

        if line.startswith("try"):
            emit("try:", orig_no)
            if "{" in line or line == "try":
                current_indent += 1
                block_stack.append({'type': 'try', 'orig_line': orig_no})
            continue

        if line.startswith("catch"):
            inside = extract_parentheses_content(line)
            parts = inside.split()
            var_name = parts[-1] if parts else "e"
            emit(f"except Exception as {var_name}:", orig_no)
            if "{" in line:
                current_indent += 1
                block_stack.append({'type': 'catch', 'orig_line': orig_no})
            continue

        if line.startswith("finally"):
            emit("finally:", orig_no)
            if "{" in line or line == "finally":
                current_indent += 1
                block_stack.append({'type': 'finally', 'orig_line': orig_no})
            continue

        if line.startswith("switch"):
            expr = extract_parentheses_content(line)
            emit(f"_switch_val = {clean_expr(expr)}", orig_no)
            block_stack.append({'type': 'switch', 'has_case': False, 'orig_line': orig_no})
            continue

        m_case = re.match(r"^case\s+(.*?):", line)
        if m_case:
            case_val = clean_expr(m_case.group(1))
            if block_stack and block_stack[-1]['type'] == 'case':
                block_stack.pop()
                current_indent = max(0, current_indent - 1)
            sw = next((b for b in reversed(block_stack) if b['type'] == 'switch'), None)
            if sw and not sw['has_case']:
                sw['has_case'] = True
                emit(f"if _switch_val == {case_val}:", orig_no)
            else:
                emit(f"elif _switch_val == {case_val}:", orig_no)
            current_indent += 1
            block_stack.append({'type': 'case', 'orig_line': orig_no})
            continue

        if line.startswith("default:"):
            if block_stack and block_stack[-1]['type'] == 'case':
                block_stack.pop()
                current_indent = max(0, current_indent - 1)
            emit("else:", orig_no)
            current_indent += 1
            block_stack.append({'type': 'case', 'orig_line': orig_no})
            continue

        if line.startswith("throw new") or line.startswith("throw "):
            m_throw = re.search(r"throw\s+new\s+\w+\((.*?)\);?", line)
            if m_throw:
                msg = clean_expr(m_throw.group(1))
                emit(f"raise ValueError({msg})", orig_no)
            else:
                emit("raise ValueError('Error')", orig_no)
            continue

        # Method / Function declaration
        m_method = re.match(
            r"^(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:void|int|boolean|bool|double|float|long|short|char|String|int\[\]|auto|function|def|[\w<>]+)\s+(\w+)\s*\(",
            line
        )
        if m_method and not re.match(r"^(if|while|for|switch|catch|throw)\b", m_method.group(1)):
            mname = m_method.group(1)
            raw_args = extract_parentheses_content(line)
            args_clean = []
            if raw_args:
                for arg_part in raw_args.split(","):
                    arg_part = arg_part.strip()
                    parts = arg_part.split()
                    if parts:
                        clean_arg = parts[-1].replace("[]", "").replace("*", "").replace("&", "")
                        args_clean.append(clean_arg)
            if mname == "main":
                main_found = True
                emit("def main(args=None):", orig_no)
            else:
                emit(f"def {mname}({', '.join(args_clean)}):", orig_no)
            if line.endswith("{"):
                current_indent += 1
                block_stack.append({'type': 'func', 'name': mname, 'orig_line': orig_no})
            continue

        # If
        if line.startswith("if"):
            cond = extract_parentheses_content(line)
            emit(f"if {clean_expr(cond)}:", orig_no)
            if line.endswith("{"):
                current_indent += 1
                block_stack.append({'type': 'if', 'orig_line': orig_no})
            continue

        # Else if
        if line.startswith("else if") or line.startswith("elif"):
            cond = extract_parentheses_content(line)
            emit(f"elif {clean_expr(cond)}:", orig_no)
            if line.endswith("{"):
                current_indent += 1
                block_stack.append({'type': 'elif', 'orig_line': orig_no})
            continue

        # Else
        if line.startswith("else"):
            emit("else:", orig_no)
            if line.endswith("{"):
                current_indent += 1
                block_stack.append({'type': 'else', 'orig_line': orig_no})
            continue

        # While
        if line.startswith("while"):
            cond = extract_parentheses_content(line)
            emit(f"while {clean_expr(cond)}:", orig_no)
            if line.endswith("{"):
                current_indent += 1
                block_stack.append({'type': 'while', 'orig_line': orig_no})
            continue

        # For loop
        if line.startswith("for"):
            inside = extract_parentheses_content(line)
            parts = [p.strip() for p in inside.split(";")]
            if len(parts) == 3:
                init_p, cond_p, step_p = parts
                m_var = re.search(r"(\w+)\s*=\s*(.*)", init_p)
                if m_var:
                    var = m_var.group(1)
                    init_val = clean_expr(m_var.group(2))
                    cond = clean_expr(cond_p)
                    step_raw = step_p
                    if step_raw in (f"{var}++", f"++{var}"):
                        step_py = f"{var} += 1"
                    elif step_raw in (f"{var}--", f"--{var}"):
                        step_py = f"{var} -= 1"
                    else:
                        step_py = clean_expr(step_raw)

                    emit(f"{var} = {init_val}", orig_no)
                    emit(f"while {cond}:", orig_no)
                    if line.endswith("{"):
                        current_indent += 1
                        block_stack.append({'type': 'for', 'var': var, 'step': step_py, 'orig_line': orig_no})
                    continue

        stmt = line.rstrip(";").rstrip("{").strip()

        # Output statements
        if stmt.startswith("System.out.println"):
            arg = extract_parentheses_content(stmt)
            emit(f"print({clean_expr(arg)})", orig_no)
            continue
        if stmt.startswith("System.out.print"):
            arg = extract_parentheses_content(stmt)
            emit(f"print({clean_expr(arg)}, end='')", orig_no)
            continue
        if stmt.startswith("console.log"):
            arg = extract_parentheses_content(stmt)
            emit(f"print({clean_expr(arg)})", orig_no)
            continue
        if "cout <<" in stmt:
            parts = [clean_expr(p) for p in stmt.replace("cout <<", "").split("<<") if p.strip() and p.strip() != "endl"]
            emit(f"print({', '.join(parts)})", orig_no)
            continue
        if stmt.startswith("printf"):
            arg = extract_parentheses_content(stmt)
            parts = arg.split(",", 1)
            if len(parts) > 1:
                emit(f"print({clean_expr(parts[1])})", orig_no)
            else:
                emit(f"print({clean_expr(parts[0])})", orig_no)
            continue

        # Arrays
        m_arr_brace = re.match(r"^(?:(?:final\s+)?(?:int|double|float|boolean|String|char|auto)\s*(?:\[\])?\s*)?(\w+)(?:\[\])?\s*=\s*(?:new\s+\w+\[\]\s*)?\{(.*?)\}$", stmt)
        if m_arr_brace:
            emit(f"{m_arr_brace.group(1)} = [{m_arr_brace.group(2)}]", orig_no)
            continue

        m_arr_sq = re.match(r"^(?:(?:let|const|var)\s+)?(\w+)\s*=\s*\[(.*)\]$", stmt)
        if m_arr_sq:
            emit(f"{m_arr_sq.group(1)} = [{m_arr_sq.group(2)}]", orig_no)
            continue

        # Variables with init
        m_var = re.match(r"^(?:(?:final\s+)?(?:int|double|float|boolean|bool|String|char|long|short|auto)|let|const|var)\s+(\w+)\s*=\s*(.*)$", stmt)
        if m_var:
            emit(f"{m_var.group(1)} = {clean_expr(m_var.group(2))}", orig_no)
            continue

        # Variables without init
        m_novar = re.match(r"^(?:int|double|float|long|short)\s+(\w+)$", stmt)
        if m_novar:
            emit(f"{m_novar.group(1)} = 0", orig_no)
            continue
        m_nobool = re.match(r"^(?:boolean|bool)\s+(\w+)$", stmt)
        if m_nobool:
            emit(f"{m_nobool.group(1)} = False", orig_no)
            continue

        # Increments
        m_inc = re.match(r"^(\w+)\+\+$", stmt) or re.match(r"^\+\+(\w+)$", stmt)
        if m_inc:
            emit(f"{m_inc.group(1)} += 1", orig_no)
            continue
        m_dec = re.match(r"^(\w+)--$", stmt) or re.match(r"^--(\w+)$", stmt)
        if m_dec:
            emit(f"{m_dec.group(1)} -= 1", orig_no)
            continue

        # Returns
        if stmt.startswith("return"):
            emit(f"return {clean_expr(stmt[6:].strip())}", orig_no)
            continue

        # Continue / Break
        if stmt in ("continue", "break"):
            if block_stack and block_stack[-1]['type'] == 'case':
                emit("pass", orig_no)
                continue
            for b in reversed(block_stack):
                if b['type'] == 'for' and b.get('step'):
                    emit(b['step'], orig_no)
                    break
            emit(stmt, orig_no)
            continue

        emit(clean_expr(stmt), orig_no)

    if main_found:
        emit("main()", len(raw_lines))

    return "\n".join(out_lines), line_map


def detect_code_language(source, hint="auto"):
    if hint and hint.lower() in ("python", "java", "javascript", "cpp"):
        # Auto-correct if obvious mismatch
        if hint.lower() == "python":
            if any(k in source for k in ["public class", "System.out", "public static void", "String[] args", "boolean isPrime"]):
                return "java"
            if any(k in source for k in ["console.log", "function ", "const ", "let "]) and "def " not in source:
                return "javascript"
            if any(k in source for k in ["#include", "std::", "cout <<", "int main()"]):
                return "cpp"
        return hint.lower()
    if any(k in source for k in ["public class", "System.out", "public static void", "String[] args", "boolean isPrime"]):
        return "java"
    if any(k in source for k in ["console.log", "function ", "const ", "let "]):
        return "javascript"
    if any(k in source for k in ["#include", "std::", "cout <<", "int main()"]):
        return "cpp"
    return "python"


def _post_process(frames):
    for idx, frame in enumerate(frames):
        if idx == 0:
            continue
        prev = frames[idx - 1]
        for var, info in frame["variables"].items():
            if info["type"] != "array":
                continue
            if var not in prev["variables"]:
                continue
            prev_info = prev["variables"][var]
            if prev_info["type"] != "array":
                continue
            a, b = prev_info["value"], info["value"]
            if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
                diffs = [i for i in range(len(a)) if a[i] != b[i]]
                if len(diffs) == 2:
                    i1, i2 = diffs
                    if a[i1] == b[i2] and a[i2] == b[i1]:
                        frame["highlight"]["swaps"].append({"var": var, "i": i1, "j": i2})
    return frames


def _detect_structures(frames, source):
    hints = []
    src_lower = source.lower()
    array_vars = set()
    for frame in frames:
        for var, info in frame["variables"].items():
            if info["type"] == "array" and isinstance(info.get("value"), list):
                if len(info["value"]) > 0 and all(isinstance(x, (int, float)) for x in info["value"]):
                    array_vars.add(var)
    if array_vars:
        hints.append("array")
    if any(k in src_lower for k in ["sort", "swap", "bubble", "insertion", "selection", "merge", "quick", "heap"]):
        hints.append("sorting")
    if any(k in src_lower for k in ["search", "find", "binary", "linear", "target"]):
        hints.append("searching")
    if any(k in src_lower for k in ["tree", "node", "left", "right", "root", "bst"]):
        hints.append("tree")
    if any(k in src_lower for k in ["graph", "adjacen", "bfs", "dfs", "visited", "neighbor"]):
        hints.append("graph")
    if any(k in src_lower for k in ["stack", "push", "pop", "queue", "enqueue", "dequeue"]):
        hints.append("stack_queue")
    if any(k in src_lower for k in ["linked", "head", "tail"]):
        hints.append("linked_list")
    if any(k in src_lower for k in ["fibonacci", "fib", "factorial", "recurse", "recursive"]):
        hints.append("recursion")
    if any(k in src_lower for k in ["matrix", "grid", "board", "dp"]):
        hints.append("matrix")
    return list(dict.fromkeys(hints))


class CodeTracer:
    @staticmethod
    def trace(source, language="auto", timeout_steps=800):
        lang = detect_code_language(source, language)
        lines = source.splitlines()

        if lang == "python":
            try:
                tree = ast.parse(source)
            except SyntaxError as exc:
                return {
                    "success": False,
                    "error": {"message": f"Python Syntax Error (Line {exc.lineno}): {exc.msg}", "lineno": exc.lineno},
                    "frames": [],
                    "total_steps": 0,
                    "detected_structures": [],
                    "language": "python"
                }
            tracer = _Tracer(lines)
            try:
                code_obj = compile(tree, "<code2flow>", "exec")
            except Exception as exc:
                return {
                    "success": False,
                    "error": {"message": f"Compile Error: {str(exc)}"},
                    "frames": [],
                    "total_steps": 0,
                    "detected_structures": [],
                    "language": "python"
                }
        else:
            line_map = {}
            try:
                py_code, line_map = transpile_c_style_to_python(source, lang)
                tree = ast.parse(py_code)
                code_obj = compile(tree, "<code2flow>", "exec")
                tracer = MultiLangTracer(lines, line_map)
            except SyntaxError as exc:
                orig_err_line = line_map.get(exc.lineno, exc.lineno) if line_map else exc.lineno
                return {
                    "success": False,
                    "error": {"message": f"{lang.upper()} Syntax Error (Line {orig_err_line}): {exc.msg}", "lineno": orig_err_line},
                    "frames": [],
                    "total_steps": 0,
                    "detected_structures": [],
                    "language": lang
                }
            except Exception as exc:
                return {
                    "success": False,
                    "error": {"message": f"{lang.upper()} Parse Error: {str(exc)}"},
                    "frames": [],
                    "total_steps": 0,
                    "detected_structures": [],
                    "language": lang
                }

        tracer.MAX_STEPS = timeout_steps
        old_stdout = sys.stdout
        sys.stdout = tracer._stdout_buf
        error_info = None
        try:
            glb = {}
            sys.settrace(tracer)
            exec(code_obj, glb)  # noqa: S102
        except Exception as exc:
            tb_lines = traceback.format_exc().splitlines()
            error_info = {
                "message": str(exc),
                "type": type(exc).__name__,
                "traceback": tb_lines[-5:]
            }
        finally:
            sys.settrace(None)
            sys.stdout = old_stdout

        frames = _post_process(tracer.frames)
        detected = _detect_structures(frames, source)
        return {
            "success": True,
            "error": error_info,
            "frames": frames,
            "total_steps": len(frames),
            "detected_structures": detected,
            "stdout": tracer._stdout_buf.getvalue(),
            "language": lang
        }
