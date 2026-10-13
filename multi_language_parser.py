"""
Code2Flow - Multi-Language AST & Control Flow Parser
Parses JavaScript, C/C++, and Java into unified Flowchart Control Flow Graphs (CFG).
Compatible with Python 3.10-3.14+ with zero external dependencies.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from flowchart_builder import FlowNode, FlowEdge


class MultiLangParser:
    """Parses C-style syntax languages (JavaScript, Java, C/C++) into CFG flowchart graphs."""

    @classmethod
    def parse_flowchart(cls, code: str, language: str = "javascript") -> Tuple[Dict[str, Any], List[str]]:
        warnings: List[str] = []
        if not code or not code.strip():
            raise ValueError(f"{language.capitalize()} source code is empty.")

        lines = code.splitlines()
        nodes: Dict[str, FlowNode] = {}
        edges: List[FlowEdge] = []
        node_counter = 0

        def next_id(prefix="node"):
            nonlocal node_counter
            node_counter += 1
            return f"{prefix}_{node_counter}"

        # Start and End nodes
        start_node = FlowNode(
            node_id=next_id("start"),
            label=f"Start ({language.capitalize()})",
            shape="oval",
            category="start",
            scope="global",
            details=f"{language.capitalize()} Program entry point"
        )
        nodes[start_node.id] = start_node

        end_node = FlowNode(
            node_id=next_id("end"),
            label="End",
            shape="oval",
            category="end",
            scope="global",
            details="Program termination"
        )
        nodes[end_node.id] = end_node

        # Clean comments while tracking lines
        cleaned_lines = cls._strip_comments(lines)

        # Build blocks and statements
        prev_nodes = [start_node.id]
        loop_stack = []

        i = 0
        while i < len(cleaned_lines):
            raw_line = cleaned_lines[i].strip()
            line_no = i + 1

            if not raw_line or raw_line == "{" or raw_line == "}":
                i += 1
                continue

            # Detect Input / Output
            is_io, io_type, io_label = cls._detect_io(raw_line, language)
            if is_io:
                node = FlowNode(
                    node_id=next_id("io"),
                    label=io_label,
                    shape="parallelogram",
                    category="io_output" if io_type == "output" else "io_input",
                    lineno=line_no,
                    details=f"Line {line_no}: {io_type.capitalize()} operation"
                )
                nodes[node.id] = node
                for p in prev_nodes:
                    edges.append(FlowEdge(p, node.id))
                prev_nodes = [node.id]
                i += 1
                continue

            # Detect If condition
            if_match = re.match(r"^if\s*\((.*)\)", raw_line)
            if if_match:
                cond_expr = if_match.group(1).strip()
                dec_node = FlowNode(
                    node_id=next_id("if"),
                    label=f"if ({cond_expr}) ?",
                    shape="diamond",
                    category="decision",
                    lineno=line_no,
                    details=f"Line {line_no}: Decision condition"
                )
                nodes[dec_node.id] = dec_node
                for p in prev_nodes:
                    edges.append(FlowEdge(p, dec_node.id))

                # Collect body of if
                body_lines, else_lines, next_i = cls._extract_if_else_blocks(cleaned_lines, i)
                i = next_i

                # Process True branch
                true_exits = cls._process_block_statements(body_lines, [dec_node.id], nodes, edges, next_id, language, "True")
                # Fix edge label
                cls._label_first_edge(edges, dec_node.id, "True", "#10b981")

                # Process False branch
                if else_lines:
                    false_exits = cls._process_block_statements(else_lines, [dec_node.id], nodes, edges, next_id, language, "False")
                    cls._label_first_edge(edges, dec_node.id, "False", "#ef4444")
                    prev_nodes = list(set(true_exits + false_exits))
                else:
                    edges.append(FlowEdge(dec_node.id, end_node.id, label="False", edge_type="false", color="#ef4444"))
                    prev_nodes = true_exits
                continue

            # Detect While loop
            while_match = re.match(r"^while\s*\((.*)\)", raw_line)
            if while_match:
                cond_expr = while_match.group(1).strip()
                loop_node = FlowNode(
                    node_id=next_id("while"),
                    label=f"while ({cond_expr}) ?",
                    shape="diamond",
                    category="loop_header",
                    lineno=line_no,
                    details=f"Line {line_no}: While loop condition"
                )
                nodes[loop_node.id] = loop_node
                for p in prev_nodes:
                    edges.append(FlowEdge(p, loop_node.id))

                body_lines, next_i = cls._extract_block(cleaned_lines, i)
                i = next_i

                body_exits = cls._process_block_statements(body_lines, [loop_node.id], nodes, edges, next_id, language, "Loop")
                cls._label_first_edge(edges, loop_node.id, "Loop", "#06b6d4")

                # Loop back
                for be in body_exits:
                    edges.append(FlowEdge(be, loop_node.id, label="Repeat", edge_type="loop_back", color="#8b5cf6"))

                # Exit loop
                exit_node = FlowNode(
                    node_id=next_id("exit"),
                    label="Exit While",
                    shape="rectangle",
                    category="process",
                    lineno=line_no,
                    details="While loop terminated"
                )
                nodes[exit_node.id] = exit_node
                edges.append(FlowEdge(loop_node.id, exit_node.id, label="False", edge_type="false", color="#ef4444"))
                prev_nodes = [exit_node.id]
                continue

            # Detect For loop
            for_match = re.match(r"^for\s*\((.*)\)", raw_line)
            if for_match:
                for_expr = for_match.group(1).strip()
                for_node = FlowNode(
                    node_id=next_id("for"),
                    label=f"for ({for_expr})",
                    shape="diamond",
                    category="loop_header",
                    lineno=line_no,
                    details=f"Line {line_no}: For loop iteration"
                )
                nodes[for_node.id] = for_node
                for p in prev_nodes:
                    edges.append(FlowEdge(p, for_node.id))

                body_lines, next_i = cls._extract_block(cleaned_lines, i)
                i = next_i

                body_exits = cls._process_block_statements(body_lines, [for_node.id], nodes, edges, next_id, language, "Loop")
                cls._label_first_edge(edges, for_node.id, "Loop", "#06b6d4")

                for be in body_exits:
                    edges.append(FlowEdge(be, for_node.id, label="Next", edge_type="loop_back", color="#8b5cf6"))

                exit_node = FlowNode(
                    node_id=next_id("for_exit"),
                    label="Exit For",
                    shape="rectangle",
                    category="process",
                    lineno=line_no,
                    details="For loop finished"
                )
                nodes[exit_node.id] = exit_node
                edges.append(FlowEdge(for_node.id, exit_node.id, label="Done", edge_type="loop_exit", color="#64748b"))
                prev_nodes = [exit_node.id]
                continue

            # Detect Return
            if raw_line.startswith("return"):
                ret_node = FlowNode(
                    node_id=next_id("return"),
                    label=raw_line.rstrip(";"),
                    shape="oval",
                    category="return",
                    lineno=line_no,
                    details=f"Line {line_no}: Return statement"
                )
                nodes[ret_node.id] = ret_node
                for p in prev_nodes:
                    edges.append(FlowEdge(p, ret_node.id))
                edges.append(FlowEdge(ret_node.id, end_node.id, label="return", edge_type="return", color="#ec4899"))
                prev_nodes = []
                i += 1
                continue

            # Detect Function definition
            fn_match = cls._match_function(raw_line, language)
            if fn_match:
                fn_name = fn_match
                fn_node = FlowNode(
                    node_id=next_id("fn"),
                    label=f"function {fn_name}()",
                    shape="rectangle",
                    category="process",
                    lineno=line_no,
                    details=f"Line {line_no}: Function definition {fn_name}"
                )
                nodes[fn_node.id] = fn_node
                for p in prev_nodes:
                    edges.append(FlowEdge(p, fn_node.id))
                prev_nodes = [fn_node.id]
                i += 1
                continue

            # Generic Statement / Variable Assignment
            clean_stmt = raw_line.rstrip(";")
            stmt_node = FlowNode(
                node_id=next_id("stmt"),
                label=clean_stmt,
                shape="rectangle",
                category="process",
                lineno=line_no,
                details=f"Line {line_no}: Statement"
            )
            nodes[stmt_node.id] = stmt_node
            for p in prev_nodes:
                edges.append(FlowEdge(p, stmt_node.id))
            prev_nodes = [stmt_node.id]
            i += 1

        # Connect remaining open exits to End
        for p in prev_nodes:
            edges.append(FlowEdge(p, end_node.id))

        # Hierarchical Layout
        cls._calculate_layout(nodes, edges)

        graph_dict = {
            "nodes": [n.to_dict() for n in nodes.values()],
            "edges": [e.to_dict() for e in edges],
            "node_count": len(nodes),
            "edge_count": len(edges)
        }

        return graph_dict, warnings

    @classmethod
    def _strip_comments(cls, lines: List[str]) -> List[str]:
        cleaned = []
        in_block_comment = False
        for l in lines:
            trimmed = l.strip()
            if in_block_comment:
                if "*/" in trimmed:
                    in_block_comment = False
                    cleaned.append(trimmed.split("*/", 1)[1])
                else:
                    cleaned.append("")
                continue
            if "/*" in trimmed:
                if "*/" in trimmed:
                    # Single line block comment
                    cleaned.append(re.sub(r"/\*.*?\*/", "", trimmed))
                else:
                    in_block_comment = True
                    cleaned.append(trimmed.split("/*", 1)[0])
                continue
            if "//" in trimmed:
                cleaned.append(trimmed.split("//", 1)[0])
            else:
                cleaned.append(trimmed)
        return cleaned

    @classmethod
    def _detect_io(cls, line: str, language: str) -> Tuple[bool, str, str]:
        # JavaScript
        if "console.log" in line or "console.error" in line or "console.warn" in line:
            return True, "output", line.rstrip(";")
        if "prompt(" in line or "readline(" in line:
            return True, "input", line.rstrip(";")

        # C / C++
        if "printf(" in line or "cout <<" in line or "puts(" in line:
            return True, "output", line.rstrip(";")
        if "scanf(" in line or "cin >>" in line or "getline(" in line:
            return True, "input", line.rstrip(";")

        # Java
        if "System.out.print" in line or "System.out.println" in line:
            return True, "output", line.rstrip(";")
        if "Scanner" in line or ".readLine(" in line or ".nextInt(" in line:
            return True, "input", line.rstrip(";")

        return False, "", ""

    @classmethod
    def _match_function(cls, line: str, language: str) -> Optional[str]:
        # JS: function foo(...) or const foo = (...) =>
        m = re.match(r"(?:async\s+)?function\s+([A-Za-z0-9_$]+)", line)
        if m:
            return m.group(1)
        m = re.match(r"(?:const|let|var)\s+([A-Za-z0-9_$]+)\s*=\s*(?:function|\(.*?\)\s*=>)", line)
        if m:
            return m.group(1)

        # C / C++ / Java: returnType functionName(...)
        m = re.match(r"(?:public|private|protected|static|void|int|float|double|char|bool|boolean|String|auto)\s+([A-Za-z0-9_$]+)\s*\(", line)
        if m:
            name = m.group(1)
            if name not in ("if", "for", "while", "switch", "catch"):
                return name
        return None

    @classmethod
    def _extract_block(cls, lines: List[str], start_idx: int) -> Tuple[List[Tuple[int, str]], int]:
        block: List[Tuple[int, str]] = []
        i = start_idx
        bracket_count = 0
        started = False

        while i < len(lines):
            line = lines[i]
            if "{" in line:
                bracket_count += line.count("{")
                started = True
            if "}" in line:
                bracket_count -= line.count("}")

            if i > start_idx:
                block.append((i + 1, line))

            if started and bracket_count <= 0:
                return block, i + 1

            if not started and ";" in line:
                # Single statement block without braces
                return [(i + 1, line)], i + 1

            i += 1
        return block, i

    @classmethod
    def _extract_if_else_blocks(cls, lines: List[str], start_idx: int) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]], int]:
        if_block, next_i = cls._extract_block(lines, start_idx)
        else_block: List[Tuple[int, str]] = []

        if next_i < len(lines):
            chk = lines[next_i].strip()
            if chk.startswith("else"):
                else_block, next_i = cls._extract_block(lines, next_i)

        return if_block, else_block, next_i

    @classmethod
    def _process_block_statements(
        cls,
        line_tuples: List[Tuple[int, str]],
        incoming_nodes: List[str],
        nodes: Dict[str, FlowNode],
        edges: List[FlowEdge],
        next_id,
        language: str,
        first_label: str = ""
    ) -> List[str]:
        current_incomers = list(incoming_nodes)
        for line_no, raw_line in line_tuples:
            trimmed = raw_line.strip().strip("{").strip("}").strip()
            if not trimmed:
                continue

            is_io, io_type, io_label = cls._detect_io(trimmed, language)
            shape = "parallelogram" if is_io else "rectangle"
            cat = ("io_output" if io_type == "output" else "io_input") if is_io else "process"

            node = FlowNode(
                node_id=next_id("blk_stmt"),
                label=trimmed.rstrip(";"),
                shape=shape,
                category=cat,
                lineno=line_no,
                details=f"Line {line_no}: Statement inside block"
            )
            nodes[node.id] = node
            for inc in current_incomers:
                lbl = first_label if inc in incoming_nodes and first_label else ""
                edges.append(FlowEdge(inc, node.id, label=lbl))
            first_label = ""
            current_incomers = [node.id]

        return current_incomers

    @classmethod
    def _label_first_edge(cls, edges: List[FlowEdge], from_id: str, label: str, color: str):
        for e in edges:
            if e.from_id == from_id and not e.label:
                e.label = label
                e.color = color
                return

    @classmethod
    def _calculate_layout(cls, nodes: Dict[str, FlowNode], edges: List[FlowEdge]):
        """Layered topological layout computation."""
        if not nodes:
            return
        node_list = list(nodes.values())
        y_spacing = 100.0
        for idx, node in enumerate(node_list):
            node.x = 350.0
            node.y = 80.0 + (idx * y_spacing)
            node.width = max(180.0, min(320.0, len(node.label) * 9.0 + 30.0))
            node.height = 54.0 if node.shape != "diamond" else 64.0
