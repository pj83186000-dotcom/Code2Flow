"""
Code2Flow - Control Flow Graph and Flowchart Builder
Constructs a complete control-flow graph (CFG) from Python AST, supporting:
- Variable assignments and I/O (parallelogram)
- if, elif, else branching (diamond)
- for and while loops with break/continue (diamond, loop back-edges)
- nested conditionals and nested loops
- multiple return statements and unreachable code detection
- try/except/else/finally and raise statements
- match-case statements
- function entry/exit points and recursion detection
- standard flowchart shapes: Oval, Rectangle, Diamond, Parallelogram
"""

import ast
from typing import Dict, Any, List, Optional, Set, Tuple
from parser import safe_unparse, SourceParser


class FlowNode:
    """Represents a single node in the flowchart."""
    def __init__(
        self,
        node_id: str,
        label: str,
        shape: str = "rectangle",  # oval, rectangle, diamond, parallelogram
        category: str = "process",  # start, end, process, decision, io_input, io_output, loop_header, return, jump, exception
        lineno: Optional[int] = None,
        end_lineno: Optional[int] = None,
        col_offset: Optional[int] = None,
        scope: str = "global",
        ast_type: str = "Statement",
        details: str = "",
        is_unreachable: bool = False,
        is_recursive: bool = False
    ):
        self.id = node_id
        self.label = label
        self.shape = shape
        self.category = category
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.col_offset = col_offset
        self.scope = scope
        self.ast_type = ast_type
        self.details = details
        self.is_unreachable = is_unreachable
        self.is_recursive = is_recursive
        # Layout coordinates (calculated later)
        self.x: float = 0.0
        self.y: float = 0.0
        self.width: float = 180.0
        self.height: float = 60.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "shape": self.shape,
            "category": self.category,
            "lineno": self.lineno,
            "end_lineno": self.end_lineno,
            "col_offset": self.col_offset,
            "scope": self.scope,
            "ast_type": self.ast_type,
            "details": self.details,
            "is_unreachable": self.is_unreachable,
            "is_recursive": self.is_recursive,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height
        }


class FlowEdge:
    """Represents a directed edge between two flowchart nodes."""
    def __init__(
        self,
        from_id: str,
        to_id: str,
        label: str = "",
        edge_type: str = "normal",  # normal, true, false, loop_back, loop_exit, return, exception, jump
        color: Optional[str] = None
    ):
        self.from_id = from_id
        self.to_id = to_id
        self.label = label
        self.edge_type = edge_type
        self.color = color

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from": self.from_id,
            "to": self.to_id,
            "label": self.label,
            "edge_type": self.edge_type,
            "color": self.color
        }


class LoopContext:
    """Tracks active loop targets for break and continue."""
    def __init__(self, header_id: str, exit_id: str, name: str = "loop"):
        self.header_id = header_id
        self.exit_id = exit_id
        self.name = name


class FlowchartBuilder:
    """Constructs control-flow graphs and formats them into JSON, Mermaid, and DOT."""

    def __init__(self, source_code: str, tree: ast.Module):
        self.source_code = source_code
        self.tree = tree
        self.lines = source_code.splitlines()
        self.nodes: Dict[str, FlowNode] = {}
        self.edges: List[FlowEdge] = []
        self._node_counter = 0
        self._loop_stack: List[LoopContext] = []
        self._function_return_targets: Dict[str, str] = {}
        self._current_scope = "global"

    def _next_id(self, prefix: str = "node") -> str:
        self._node_counter += 1
        return f"{prefix}_{self._node_counter}"

    def _add_node(self, node: FlowNode) -> FlowNode:
        self.nodes[node.id] = node
        return node

    def _add_edge(self, from_id: str, to_id: str, label: str = "", edge_type: str = "normal", color: Optional[str] = None):
        if not from_id or not to_id:
            return
        # Avoid duplicate identical edges
        for e in self.edges:
            if e.from_id == from_id and e.to_id == to_id and e.label == label:
                return
        self.edges.append(FlowEdge(from_id, to_id, label=label, edge_type=edge_type, color=color))

    def build(self) -> Tuple[Dict[str, Any], List[str]]:
        """Builds CFG for entire module and all top-level functions."""
        warnings: List[str] = []

        # Start Node
        start_node = self._add_node(FlowNode(
            node_id=self._next_id("start"),
            label="Start",
            shape="oval",
            category="start",
            scope="global",
            details="Program entry point"
        ))

        # End Node
        end_node = self._add_node(FlowNode(
            node_id=self._next_id("end"),
            label="End",
            shape="oval",
            category="end",
            scope="global",
            details="Program normal termination"
        ))

        self._function_return_targets["global"] = end_node.id

        # Separate top-level functions/classes from script statements
        stmts = self.tree.body
        last_exit_nodes = self._process_statement_list(stmts, [start_node.id], warnings)

        for exit_id in last_exit_nodes:
            self._add_edge(exit_id, end_node.id, label="", edge_type="normal")

        # Position nodes with hierarchical layout
        self._calculate_layout()

        graph_dict = {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
            "node_count": len(self.nodes),
            "edge_count": len(self.edges)
        }

        return graph_dict, warnings

    def _process_statement_list(self, stmts: List[ast.stmt], incoming_nodes: List[str], warnings: List[str]) -> List[str]:
        """Processes a linear list of statements and returns outgoing exit node IDs."""
        current_incomers = list(incoming_nodes)

        for idx, stmt in enumerate(stmts):
            if not current_incomers:
                # Code is unreachable
                unreachable_node = self._create_stmt_node(stmt, is_unreachable=True)
                warnings.append(f"Statement at line {getattr(stmt, 'lineno', '?')} appears to be unreachable.")
                # We do not connect unreachable code from current_incomers
                continue

            current_incomers = self._process_single_statement(stmt, current_incomers, warnings)

        return current_incomers

    def _process_single_statement(self, stmt: ast.stmt, incoming_nodes: List[str], warnings: List[str]) -> List[str]:
        """Dispatches statement to handler and returns exit node IDs."""
        if isinstance(stmt, ast.If):
            return self._process_if(stmt, incoming_nodes, warnings)
        elif isinstance(stmt, (ast.For, ast.AsyncFor)):
            return self._process_for(stmt, incoming_nodes, warnings)
        elif isinstance(stmt, ast.While):
            return self._process_while(stmt, incoming_nodes, warnings)
        elif isinstance(stmt, ast.Break):
            return self._process_break(stmt, incoming_nodes, warnings)
        elif isinstance(stmt, ast.Continue):
            return self._process_continue(stmt, incoming_nodes, warnings)
        elif isinstance(stmt, ast.Return):
            return self._process_return(stmt, incoming_nodes, warnings)
        elif isinstance(stmt, (ast.Try, ast.TryStar if hasattr(ast, "TryStar") else ast.Try)):
            return self._process_try(stmt, incoming_nodes, warnings)
        elif isinstance(stmt, ast.Raise):
            return self._process_raise(stmt, incoming_nodes, warnings)
        elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return self._process_function_def(stmt, incoming_nodes, warnings)
        elif isinstance(stmt, ast.ClassDef):
            return self._process_class_def(stmt, incoming_nodes, warnings)
        elif hasattr(ast, "Match") and isinstance(stmt, ast.Match):
            return self._process_match(stmt, incoming_nodes, warnings)
        else:
            # Generic statement (assign, expr, print, input, pass, assert, import, etc.)
            node = self._create_stmt_node(stmt)
            for inc in incoming_nodes:
                self._add_edge(inc, node.id, label="", edge_type="normal")
            return [node.id]

    def _create_stmt_node(self, stmt: ast.stmt, is_unreachable: bool = False) -> FlowNode:
        """Creates a FlowNode for an atomic statement with proper shape and I/O detection."""
        cat = SourceParser.classify_statement(stmt)
        lineno = getattr(stmt, "lineno", None)
        end_lineno = getattr(stmt, "end_lineno", lineno)
        col_offset = getattr(stmt, "col_offset", None)
        code_str = safe_unparse(stmt)

        shape = "rectangle"
        details = f"Line {lineno}: {type(stmt).__name__}"

        if cat == "io_input":
            shape = "parallelogram"
            details = f"Input Operation: {code_str}"
        elif cat == "io_output":
            shape = "parallelogram"
            details = f"Output Operation: {code_str}"
        elif isinstance(stmt, ast.Pass):
            code_str = "pass"
            details = "No operation (pass)"
        elif isinstance(stmt, ast.Assert):
            shape = "diamond"
            cat = "decision"
            code_str = f"assert {safe_unparse(stmt.test)}"
            details = "Assertion check"

        # Check recursion if within function
        is_rec = False
        if self._current_scope != "global":
            is_rec = SourceParser.is_recursive_call(self._current_scope, stmt)
            if is_rec:
                details += " [Recursive Call]"

        node = FlowNode(
            node_id=self._next_id("stmt"),
            label=code_str,
            shape=shape,
            category=cat,
            lineno=lineno,
            end_lineno=end_lineno,
            col_offset=col_offset,
            scope=self._current_scope,
            ast_type=type(stmt).__name__,
            details=details,
            is_unreachable=is_unreachable,
            is_recursive=is_rec
        )
        return self._add_node(node)

    def _process_if(self, stmt: ast.If, incoming_nodes: List[str], warnings: List[str]) -> List[str]:
        """Handles if / elif / else branching."""
        cond_str = safe_unparse(stmt.test)
        lineno = getattr(stmt, "lineno", None)

        decision_node = self._add_node(FlowNode(
            node_id=self._next_id("if"),
            label=f"if {cond_str} ?",
            shape="diamond",
            category="decision",
            lineno=lineno,
            end_lineno=getattr(stmt, "end_lineno", lineno),
            scope=self._current_scope,
            ast_type="If",
            details=f"Conditional Decision: {cond_str}"
        ))

        for inc in incoming_nodes:
            self._add_edge(inc, decision_node.id, label="", edge_type="normal")

        # True branch (then)
        true_exits = self._process_statement_list(stmt.body, [decision_node.id], warnings)
        # Fix label on edge from decision to first node of body
        self._relabel_outgoing_edge(decision_node.id, stmt.body, "True", color="#10b981")

        # False branch (else / elif)
        false_exits: List[str] = []
        if stmt.orelse:
            false_exits = self._process_statement_list(stmt.orelse, [decision_node.id], warnings)
            self._relabel_outgoing_edge(decision_node.id, stmt.orelse, "False", color="#ef4444")
        else:
            # No else clause: decision itself exits on False
            false_exits = [decision_node.id]

        # Combine exits from both branches
        all_exits = list(set(true_exits + false_exits))
        return all_exits

    def _relabel_outgoing_edge(self, from_id: str, target_stmts: List[ast.stmt], label: str, color: Optional[str] = None):
        """Labels the edge originating from from_id that leads into target_stmts."""
        if not target_stmts:
            return
        first_target_lineno = getattr(target_stmts[0], "lineno", None)
        # Search for edge from from_id to a node matching target lineno or created first
        for edge in self.edges:
            if edge.from_id == from_id and (not edge.label or edge.label == ""):
                target_node = self.nodes.get(edge.to_id)
                if target_node and (target_node.lineno == first_target_lineno or first_target_lineno is None):
                    edge.label = label
                    edge.edge_type = "true" if label == "True" else "false"
                    edge.color = color
                    return
        # If no edge matched exactly, find any unlabeled edge from from_id
        for edge in self.edges:
            if edge.from_id == from_id and not edge.label:
                edge.label = label
                edge.edge_type = "true" if label == "True" else "false"
                edge.color = color
                return

    def _process_for(self, stmt: ast.For, incoming_nodes: List[str], warnings: List[str]) -> List[str]:
        """Handles for loops with body, loop back-edge, break, continue, and else."""
        target_str = safe_unparse(stmt.target)
        iter_str = safe_unparse(stmt.iter)
        lineno = getattr(stmt, "lineno", None)

        header_node = self._add_node(FlowNode(
            node_id=self._next_id("for"),
            label=f"for {target_str} in {iter_str}",
            shape="diamond",
            category="loop_header",
            lineno=lineno,
            end_lineno=getattr(stmt, "end_lineno", lineno),
            scope=self._current_scope,
            ast_type="For",
            details=f"For Loop iteration over {iter_str}"
        ))

        for inc in incoming_nodes:
            self._add_edge(inc, header_node.id, label="", edge_type="normal")

        # Join / exit point for this loop
        exit_join_id = self._next_id("loop_exit")
        loop_exit_node = self._add_node(FlowNode(
            node_id=exit_join_id,
            label="Exit Loop",
            shape="rectangle",
            category="process",
            scope=self._current_scope,
            ast_type="LoopExit",
            details="Loop completed or broken"
        ))

        # Push to loop stack
        self._loop_stack.append(LoopContext(header_id=header_node.id, exit_id=loop_exit_node.id, name="for"))

        # Process body
        body_exits = self._process_statement_list(stmt.body, [header_node.id], warnings)
        self._relabel_outgoing_edge(header_node.id, stmt.body, "Loop", color="#06b6d4")

        # Connect normal body exits back to loop header
        for b_exit in body_exits:
            self._add_edge(b_exit, header_node.id, label="Repeat", edge_type="loop_back", color="#8b5cf6")

        # Pop loop context
        self._loop_stack.pop()

        # Connect loop completion (when iterable exhausted)
        if stmt.orelse:
            else_exits = self._process_statement_list(stmt.orelse, [header_node.id], warnings)
            self._relabel_outgoing_edge(header_node.id, stmt.orelse, "Exhausted", color="#f59e0b")
            for e_exit in else_exits:
                self._add_edge(e_exit, loop_exit_node.id, label="", edge_type="normal")
        else:
            self._add_edge(header_node.id, loop_exit_node.id, label="Done", edge_type="loop_exit", color="#64748b")

        return [loop_exit_node.id]

    def _process_while(self, stmt: ast.While, incoming_nodes: List[str], warnings: List[str]) -> List[str]:
        """Handles while loops with condition, body, loop back-edge, break, continue."""
        test_str = safe_unparse(stmt.test)
        lineno = getattr(stmt, "lineno", None)

        header_node = self._add_node(FlowNode(
            node_id=self._next_id("while"),
            label=f"while {test_str} ?",
            shape="diamond",
            category="loop_header",
            lineno=lineno,
            end_lineno=getattr(stmt, "end_lineno", lineno),
            scope=self._current_scope,
            ast_type="While",
            details=f"While Loop Condition: {test_str}"
        ))

        for inc in incoming_nodes:
            self._add_edge(inc, header_node.id, label="", edge_type="normal")

        # Loop exit node
        exit_join_id = self._next_id("while_exit")
        loop_exit_node = self._add_node(FlowNode(
            node_id=exit_join_id,
            label="Exit While",
            shape="rectangle",
            category="process",
            scope=self._current_scope,
            ast_type="WhileExit",
            details="While loop terminated"
        ))

        self._loop_stack.append(LoopContext(header_id=header_node.id, exit_id=loop_exit_node.id, name="while"))

        # Process body
        body_exits = self._process_statement_list(stmt.body, [header_node.id], warnings)
        self._relabel_outgoing_edge(header_node.id, stmt.body, "True", color="#10b981")

        # Back edges
        for b_exit in body_exits:
            self._add_edge(b_exit, header_node.id, label="Repeat", edge_type="loop_back", color="#8b5cf6")

        self._loop_stack.pop()

        if stmt.orelse:
            else_exits = self._process_statement_list(stmt.orelse, [header_node.id], warnings)
            self._relabel_outgoing_edge(header_node.id, stmt.orelse, "False", color="#ef4444")
            for e_exit in else_exits:
                self._add_edge(e_exit, loop_exit_node.id, label="", edge_type="normal")
        else:
            self._add_edge(header_node.id, loop_exit_node.id, label="False", edge_type="loop_exit", color="#ef4444")

        return [loop_exit_node.id]

    def _process_break(self, stmt: ast.Break, incoming_nodes: List[str], warnings: List[str]) -> List[str]:
        lineno = getattr(stmt, "lineno", None)
        break_node = self._add_node(FlowNode(
            node_id=self._next_id("break"),
            label="break",
            shape="rectangle",
            category="jump",
            lineno=lineno,
            scope=self._current_scope,
            ast_type="Break",
            details="Breaks out of nearest enclosing loop"
        ))
        for inc in incoming_nodes:
            self._add_edge(inc, break_node.id, label="", edge_type="normal")

        if self._loop_stack:
            curr_loop = self._loop_stack[-1]
            self._add_edge(break_node.id, curr_loop.exit_id, label="break", edge_type="jump", color="#dc2626")
        else:
            warnings.append(f"'break' outside loop at line {lineno}")

        # Break does not fall through to the next statement in its block
        return []

    def _process_continue(self, stmt: ast.Continue, incoming_nodes: List[str], warnings: List[str]) -> List[str]:
        lineno = getattr(stmt, "lineno", None)
        cont_node = self._add_node(FlowNode(
            node_id=self._next_id("continue"),
            label="continue",
            shape="rectangle",
            category="jump",
            lineno=lineno,
            scope=self._current_scope,
            ast_type="Continue",
            details="Jumps to next iteration of nearest enclosing loop"
        ))
        for inc in incoming_nodes:
            self._add_edge(inc, cont_node.id, label="", edge_type="normal")

        if self._loop_stack:
            curr_loop = self._loop_stack[-1]
            self._add_edge(cont_node.id, curr_loop.header_id, label="continue", edge_type="loop_back", color="#f97316")
        else:
            warnings.append(f"'continue' outside loop at line {lineno}")

        # Continue does not fall through to next statement
        return []

    def _process_return(self, stmt: ast.Return, incoming_nodes: List[str], warnings: List[str]) -> List[str]:
        val_str = safe_unparse(stmt.value) if stmt.value else ""
        label = f"return {val_str}".strip()
        lineno = getattr(stmt, "lineno", None)

        ret_node = self._add_node(FlowNode(
            node_id=self._next_id("return"),
            label=label,
            shape="oval",
            category="return",
            lineno=lineno,
            scope=self._current_scope,
            ast_type="Return",
            details=f"Returns {val_str or 'None'} to caller"
        ))

        for inc in incoming_nodes:
            self._add_edge(inc, ret_node.id, label="", edge_type="normal")

        # Connect directly to function exit or global end
        target_end_id = self._function_return_targets.get(self._current_scope, self._function_return_targets.get("global"))
        if target_end_id:
            self._add_edge(ret_node.id, target_end_id, label="return", edge_type="return", color="#ec4899")

        # Return does not fall through
        return []

    def _process_try(self, stmt: ast.Try, incoming_nodes: List[str], warnings: List[str]) -> List[str]:
        """Handles try / except / else / finally."""
        lineno = getattr(stmt, "lineno", None)
        try_node = self._add_node(FlowNode(
            node_id=self._next_id("try"),
            label="try",
            shape="rectangle",
            category="exception",
            lineno=lineno,
            scope=self._current_scope,
            ast_type="Try",
            details="Try block protected execution"
        ))

        for inc in incoming_nodes:
            self._add_edge(inc, try_node.id, label="", edge_type="normal")

        # Try body
        try_exits = self._process_statement_list(stmt.body, [try_node.id], warnings)

        # Handlers
        handler_exits: List[str] = []
        for handler in stmt.handlers:
            exc_name = safe_unparse(handler.type) if handler.type else "Exception"
            as_name = f" as {handler.name}" if handler.name else ""
            h_lineno = getattr(handler, "lineno", None)

            h_node = self._add_node(FlowNode(
                node_id=self._next_id("except"),
                label=f"except {exc_name}{as_name}",
                shape="diamond",
                category="exception",
                lineno=h_lineno,
                scope=self._current_scope,
                ast_type="ExceptHandler",
                details=f"Catches {exc_name}"
            ))

            # Connect from try_node (or any statement inside try) to handler
            self._add_edge(try_node.id, h_node.id, label=f"on {exc_name}", edge_type="exception", color="#ef4444")
            h_exits = self._process_statement_list(handler.body, [h_node.id], warnings)
            handler_exits.extend(h_exits)

        # Try else block (runs if try succeeded with no exception)
        else_exits: List[str] = []
        if stmt.orelse:
            else_exits = self._process_statement_list(stmt.orelse, try_exits, warnings)
        else:
            else_exits = try_exits

        all_prior_exits = list(set(else_exits + handler_exits))

        # Finally block (runs always)
        if stmt.finalbody:
            fin_node = self._add_node(FlowNode(
                node_id=self._next_id("finally"),
                label="finally",
                shape="rectangle",
                category="exception",
                lineno=getattr(stmt.finalbody[0], "lineno", None),
                scope=self._current_scope,
                ast_type="Finally",
                details="Always executed after try/except"
            ))
            for p_exit in all_prior_exits:
                self._add_edge(p_exit, fin_node.id, label="finally", edge_type="normal")
            return self._process_statement_list(stmt.finalbody, [fin_node.id], warnings)

        return all_prior_exits

    def _process_raise(self, stmt: ast.Raise, incoming_nodes: List[str], warnings: List[str]) -> List[str]:
        exc_str = safe_unparse(stmt.exc) if stmt.exc else "Exception"
        lineno = getattr(stmt, "lineno", None)

        raise_node = self._add_node(FlowNode(
            node_id=self._next_id("raise"),
            label=f"raise {exc_str}",
            shape="rectangle",
            category="exception",
            lineno=lineno,
            scope=self._current_scope,
            ast_type="Raise",
            details=f"Raises {exc_str}"
        ))

        for inc in incoming_nodes:
            self._add_edge(inc, raise_node.id, label="", edge_type="normal")

        # Raise terminates flow unless caught; connect to end or scope exit
        target_end_id = self._function_return_targets.get(self._current_scope, self._function_return_targets.get("global"))
        if target_end_id:
            self._add_edge(raise_node.id, target_end_id, label="unhandled exception", edge_type="exception", color="#ef4444")

        return []

    def _process_match(self, stmt: Any, incoming_nodes: List[str], warnings: List[str]) -> List[str]:
        """Handles match-case (Python 3.10+)."""
        subject_str = safe_unparse(stmt.subject)
        lineno = getattr(stmt, "lineno", None)

        match_node = self._add_node(FlowNode(
            node_id=self._next_id("match"),
            label=f"match {subject_str}",
            shape="diamond",
            category="decision",
            lineno=lineno,
            scope=self._current_scope,
            ast_type="Match",
            details=f"Pattern matching on {subject_str}"
        ))

        for inc in incoming_nodes:
            self._add_edge(inc, match_node.id, label="", edge_type="normal")

        case_exits: List[str] = []
        for case in stmt.cases:
            pattern_str = safe_unparse(case.pattern)
            guard_str = f" if {safe_unparse(case.guard)}" if case.guard else ""
            c_lineno = getattr(case, "lineno", None)

            c_node = self._add_node(FlowNode(
                node_id=self._next_id("case"),
                label=f"case {pattern_str}{guard_str}",
                shape="diamond",
                category="decision",
                lineno=c_lineno,
                scope=self._current_scope,
                ast_type="MatchCase",
                details=f"Pattern: {pattern_str}{guard_str}"
            ))

            self._add_edge(match_node.id, c_node.id, label="", edge_type="normal")
            exits = self._process_statement_list(case.body, [c_node.id], warnings)
            case_exits.extend(exits)

        return list(set(case_exits))

    def _process_function_def(self, stmt: Any, incoming_nodes: List[str], warnings: List[str]) -> List[str]:
        """Visualizes a function definition as an entry point with body and end node."""
        func_name = stmt.name
        args_str = ", ".join(arg.arg for arg in stmt.args.args)
        lineno = getattr(stmt, "lineno", None)

        # Definition node in caller flow
        def_node = self._add_node(FlowNode(
            node_id=self._next_id("def"),
            label=f"def {func_name}({args_str})",
            shape="rectangle",
            category="process",
            lineno=lineno,
            scope=self._current_scope,
            ast_type="FunctionDef",
            details=f"Function definition: {func_name}"
        ))
        for inc in incoming_nodes:
            self._add_edge(inc, def_node.id, label="", edge_type="normal")

        # Function Subgraph Start & End
        old_scope = self._current_scope
        self._current_scope = func_name

        fn_start = self._add_node(FlowNode(
            node_id=self._next_id(f"fn_{func_name}_start"),
            label=f"Entry: {func_name}({args_str})",
            shape="oval",
            category="start",
            scope=func_name,
            details=f"Function entry point for {func_name}"
        ))

        fn_end = self._add_node(FlowNode(
            node_id=self._next_id(f"fn_{func_name}_end"),
            label=f"Exit: {func_name}",
            shape="oval",
            category="end",
            scope=func_name,
            details=f"Function exit for {func_name}"
        ))

        self._function_return_targets[func_name] = fn_end.id

        body_exits = self._process_statement_list(stmt.body, [fn_start.id], warnings)
        for b_exit in body_exits:
            self._add_edge(b_exit, fn_end.id, label="", edge_type="normal")

        self._current_scope = old_scope

        # Def node proceeds to subsequent statements
        return [def_node.id]

    def _process_class_def(self, stmt: ast.ClassDef, incoming_nodes: List[str], warnings: List[str]) -> List[str]:
        """Visualizes class definition node and processes internal methods."""
        class_name = stmt.name
        bases = [safe_unparse(b) for b in stmt.bases]
        bases_str = f"({', '.join(bases)})" if bases else ""
        lineno = getattr(stmt, "lineno", None)

        class_node = self._add_node(FlowNode(
            node_id=self._next_id("class"),
            label=f"class {class_name}{bases_str}",
            shape="rectangle",
            category="process",
            lineno=lineno,
            scope=self._current_scope,
            ast_type="ClassDef",
            details=f"Class definition for {class_name}"
        ))

        for inc in incoming_nodes:
            self._add_edge(inc, class_node.id, label="", edge_type="normal")

        # Process methods inside class
        old_scope = self._current_scope
        for item in stmt.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._current_scope = f"{class_name}.{item.name}"
                fn_start = self._add_node(FlowNode(
                    node_id=self._next_id(f"method_{item.name}_start"),
                    label=f"Method: {class_name}.{item.name}()",
                    shape="oval",
                    category="start",
                    scope=self._current_scope,
                    details=f"Method entry for {class_name}.{item.name}"
                ))
                fn_end = self._add_node(FlowNode(
                    node_id=self._next_id(f"method_{item.name}_end"),
                    label=f"Exit: {class_name}.{item.name}",
                    shape="oval",
                    category="end",
                    scope=self._current_scope,
                    details=f"Method exit"
                ))
                self._function_return_targets[self._current_scope] = fn_end.id
                m_exits = self._process_statement_list(item.body, [fn_start.id], warnings)
                for mx in m_exits:
                    self._add_edge(mx, fn_end.id, label="", edge_type="normal")

        self._current_scope = old_scope
        return [class_node.id]

    # --- Layout Calculation (Sugiyama / Layered DAG layout) ---
    def _calculate_layout(self):
        """Computes layered layout coordinates (x, y) for all nodes."""
        if not self.nodes:
            return

        # Build adjacency
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        in_degree: Dict[str, int] = {nid: 0 for nid in self.nodes}

        for edge in self.edges:
            # Ignore loop_back edges for layering to prevent cycles
            if edge.edge_type != "loop_back":
                adj[edge.from_id].append(edge.to_id)
                in_degree[edge.to_id] = in_degree.get(edge.to_id, 0) + 1

        # Group by scope first
        scopes: Dict[str, List[str]] = {}
        for nid, node in self.nodes.items():
            scopes.setdefault(node.scope, []).append(nid)

        scope_offset_x = 0.0

        for scope_name, node_ids in scopes.items():
            # Longest path layering within scope
            layers: Dict[int, List[str]] = {}
            node_layer: Dict[str, int] = {}

            # Find roots in this scope
            roots = [nid for nid in node_ids if in_degree.get(nid, 0) == 0]
            if not roots:
                roots = [node_ids[0]]

            # BFS/Topological to assign layers
            queue = [(r, 0) for r in roots]
            visited = set()

            while queue:
                curr, layer = queue.pop(0)
                if curr in visited and node_layer.get(curr, 0) >= layer:
                    continue
                visited.add(curr)
                node_layer[curr] = max(node_layer.get(curr, 0), layer)
                for neighbor in adj.get(curr, []):
                    if neighbor in node_ids:
                        queue.append((neighbor, layer + 1))

            # Fill unvisited nodes
            for nid in node_ids:
                if nid not in node_layer:
                    node_layer[nid] = 0

            for nid, lyr in node_layer.items():
                layers.setdefault(lyr, []).append(nid)

            # Assign coordinates
            y_spacing = 110.0
            x_spacing = 240.0
            max_layer_width = 0

            for lyr_idx in sorted(layers.keys()):
                layer_nodes = layers[lyr_idx]
                max_layer_width = max(max_layer_width, len(layer_nodes))
                total_w = len(layer_nodes) * x_spacing
                start_x = scope_offset_x + 300.0 - (total_w / 2.0)

                for idx, nid in enumerate(layer_nodes):
                    node = self.nodes[nid]
                    node.x = start_x + (idx * x_spacing)
                    node.y = 80.0 + (lyr_idx * y_spacing)

                    # Dynamic width based on label length
                    label_len = len(node.label)
                    node.width = max(170.0, min(320.0, label_len * 9.0 + 30.0))
                    node.height = 54.0 if node.shape != "diamond" else 64.0

            scope_offset_x += max(600.0, max_layer_width * x_spacing + 100.0)

    # --- Exporters ---
    def to_mermaid(self) -> str:
        """Generates Mermaid flowchart code."""
        lines = ["flowchart TD"]

        # Define shapes
        for node in self.nodes.values():
            lbl = node.label.replace('"', "'").replace("\n", " ")
            if node.shape == "oval":
                lines.append(f'    {node.id}(["{lbl}"])')
            elif node.shape == "diamond":
                lines.append(f'    {node.id}{{"{lbl}"}}')
            elif node.shape == "parallelogram":
                lines.append(f'    {node.id}[/"{lbl}"/]')
            else:
                lines.append(f'    {node.id}["{lbl}"]')

        # Add edges
        for edge in self.edges:
            lbl = f"|{edge.label}|" if edge.label else ""
            lines.append(f"    {edge.from_id} -->{lbl} {edge.to_id}")

        # Styles
        lines.append("    classDef decision fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e;")
        lines.append("    classDef process fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a8a;")
        lines.append("    classDef terminal fill:#d1fae5,stroke:#059669,stroke-width:2px,color:#065f46;")
        lines.append("    classDef io fill:#f3e8ff,stroke:#7c3aed,stroke-width:2px,color:#5b21b6;")

        return "\n".join(lines)

    def to_dot(self) -> str:
        """Generates Graphviz DOT code."""
        lines = [
            "digraph Code2Flow {",
            "    rankdir=TB;",
            '    node [fontname="Helvetica", fontsize=11, style="filled,rounded"];',
            '    edge [fontname="Helvetica", fontsize=9];'
        ]

        shape_map = {
            "oval": "oval",
            "rectangle": "box",
            "diamond": "diamond",
            "parallelogram": "parallelogram"
        }

        color_map = {
            "start": "#a7f3d0",
            "end": "#fecaca",
            "decision": "#fde68a",
            "loop_header": "#fed7aa",
            "process": "#bfdbfe",
            "io_input": "#e9d5ff",
            "io_output": "#e9d5ff",
            "exception": "#fbcfe8"
        }

        for node in self.nodes.values():
            shp = shape_map.get(node.shape, "box")
            col = color_map.get(node.category, "#e2e8f0")
            lbl = node.label.replace('"', '\\"').replace("\n", "\\n")
            lines.append(f'    {node.id} [label="{lbl}", shape={shp}, fillcolor="{col}"];')

        for edge in self.edges:
            lbl = f'label="{edge.label}"' if edge.label else ""
            col = f'color="{edge.color}"' if edge.color else ""
            attrs = ", ".join(filter(None, [lbl, col]))
            attr_str = f" [{attrs}]" if attrs else ""
            lines.append(f"    {edge.from_id} -> {edge.to_id}{attr_str};")

        lines.append("}")
        return "\n".join(lines)
