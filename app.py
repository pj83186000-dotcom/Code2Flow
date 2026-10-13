"""
Code2Flow - Main Application Server (Multi-Language Enabled)
Unified Python 3.10 - 3.14+ web server supporting:
- Python (native AST)
- JavaScript / TypeScript
- Java
- C / C++
Runs on Flask if available, with automatic fallback to built-in http.server.
"""

import sys
import os
import json
import mimetypes
from typing import Dict, Any, Tuple

# Internal modules
from parser import SourceParser
from flowchart_builder import FlowchartBuilder
from multi_language_parser import MultiLangParser
from traceback_parser import TracebackParser
from dsa_visualizer import DSAEngine
from dsa_analyzer import DSAAnalyzer
from oop_analyzer import OOPAnalyzer
from multi_language_oop import MultiLangOOPAnalyzer
from class_diagram import ClassDiagramGenerator
from renderer import SVGRenderer
from exporter import DiagramExporter
from samples import SAMPLES
from code_tracer import CodeTracer


def handle_flowchart_request(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    code = data.get("code", "")
    language = data.get("language", "python").lower()

    if language == "python":
        tree, error, warnings = SourceParser.validate_and_parse(code)
        if error:
            return {"success": False, "error": error.to_dict(), "warnings": warnings}, 400

        builder = FlowchartBuilder(code, tree)
        graph_data, build_warnings = builder.build()
        warnings.extend(build_warnings)

        mermaid_code = builder.to_mermaid()
        dot_code = builder.to_dot()
        svg_code = SVGRenderer.render_flowchart(graph_data)

        return {
            "success": True,
            "graph": graph_data,
            "mermaid": mermaid_code,
            "dot": dot_code,
            "svg": svg_code,
            "warnings": warnings
        }, 200
    else:
        # Multi-language parsing (JavaScript, Java, C++)
        try:
            graph_data, warnings = MultiLangParser.parse_flowchart(code, language=language)
            svg_code = SVGRenderer.render_flowchart(graph_data)
            return {
                "success": True,
                "graph": graph_data,
                "mermaid": "",
                "dot": "",
                "svg": svg_code,
                "warnings": warnings
            }, 200
        except Exception as e:
            return {
                "success": False,
                "error": {"message": f"{language.capitalize()} Parse Error: {str(e)}"},
                "warnings": []
            }, 400


def handle_traceback_request(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    code = data.get("code", "")
    tb_text = data.get("traceback", "")
    flowchart_nodes = data.get("nodes", [])
    language = data.get("language", "python").lower()

    analysis = TracebackParser.parse_and_map(tb_text, code, flowchart_nodes, language=language)
    return {
        "success": True,
        "analysis": analysis.to_dict()
    }, 200


def handle_dsa_request(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    algorithm = data.get("algorithm", "bubble_sort")
    input_val = data.get("input", None)

    try:
        frames = []
        if algorithm == "bubble_sort":
            arr = [int(x.strip()) for x in str(input_val or "64, 34, 25, 12, 22, 11, 90").split(",") if x.strip()]
            frames = DSAEngine.bubble_sort(arr)
        elif algorithm == "selection_sort":
            arr = [int(x.strip()) for x in str(input_val or "29, 10, 14, 37, 13").split(",") if x.strip()]
            frames = DSAEngine.selection_sort(arr)
        elif algorithm == "insertion_sort":
            arr = [int(x.strip()) for x in str(input_val or "12, 11, 13, 5, 6").split(",") if x.strip()]
            frames = DSAEngine.insertion_sort(arr)
        elif algorithm == "merge_sort":
            arr = [int(x.strip()) for x in str(input_val or "38, 27, 43, 3, 9, 82, 10").split(",") if x.strip()]
            frames = DSAEngine.merge_sort(arr)
        elif algorithm == "quick_sort":
            arr = [int(x.strip()) for x in str(input_val or "10, 80, 30, 90, 40, 50, 70").split(",") if x.strip()]
            frames = DSAEngine.quick_sort(arr)
        elif algorithm == "linear_search":
            arr = [10, 20, 80, 30, 60, 50, 110, 100, 130, 170]
            target = int(input_val) if input_val is not None and str(input_val).isdigit() else 110
            frames = DSAEngine.linear_search(arr, target)
        elif algorithm == "binary_search":
            arr = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
            target = int(input_val) if input_val is not None and str(input_val).isdigit() else 23
            frames = DSAEngine.binary_search(arr, target)
        elif algorithm == "linked_list_reversal":
            arr = [int(x.strip()) for x in str(input_val or "1, 2, 3, 4, 5").split(",") if x.strip()]
            frames = DSAEngine.linked_list_reversal(arr)
        elif algorithm in ["bst_inorder", "bst_preorder", "bst_postorder"]:
            arr = [int(x.strip()) for x in str(input_val or "50, 30, 70, 20, 40, 60, 80").split(",") if x.strip()]
            mode = algorithm.split("_")[1]
            frames = DSAEngine.bst_traversal(arr, mode=mode)
        elif algorithm == "graph_bfs":
            frames = DSAEngine.graph_traversal(mode="bfs", start_node=str(input_val or "A").strip().upper())
        elif algorithm == "graph_dfs":
            frames = DSAEngine.graph_traversal(mode="dfs", start_node=str(input_val or "A").strip().upper())
        elif algorithm == "fibonacci":
            n = int(input_val) if input_val is not None and str(input_val).isdigit() else 4
            frames = DSAEngine.fibonacci_recursion(n)
        elif algorithm == "stack_ops":
            ops = [("push", 10), ("push", 20), ("push", 30), ("pop", None), ("push", 40)]
            frames = DSAEngine.stack_operations(ops)
        elif algorithm == "queue_ops":
            ops = [("enqueue", "Task A"), ("enqueue", "Task B"), ("dequeue", None), ("enqueue", "Task C")]
            frames = DSAEngine.queue_operations(ops)
        else:
            return {"success": False, "error": f"Unknown algorithm: {algorithm}"}, 400

        return {"success": True, "frames": frames, "total_steps": len(frames)}, 200
    except Exception as e:
        return {"success": False, "error": f"DSA simulation failed: {str(e)}"}, 400


def handle_dsa_detect_request(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    code = data.get("code", "")
    tree, err, _ = SourceParser.validate_and_parse(code)
    if err:
        return {"success": False, "detected": []}, 200
    detected = DSAAnalyzer.detect_algorithm(tree)
    return {"success": True, "detected": detected}, 200


def handle_oop_request(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    code = data.get("code", "")
    language = data.get("language", "python").lower()

    if language == "python":
        tree, error, warnings = SourceParser.validate_and_parse(code)
        if error:
            return {"success": False, "error": error.to_dict(), "warnings": warnings}, 400
        oop_data = OOPAnalyzer.analyze(tree)
    else:
        # Multi-language OOP
        oop_data = MultiLangOOPAnalyzer.analyze(code, language=language)
        warnings = []

    mermaid_code = ClassDiagramGenerator.to_mermaid(oop_data)
    dot_code = ClassDiagramGenerator.to_dot(oop_data)

    return {
        "success": True,
        "oop_data": oop_data,
        "mermaid": mermaid_code,
        "dot": dot_code,
        "warnings": warnings
    }, 200


def handle_visualize_request(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    source = data.get("code", "")
    language = data.get("language", "auto")
    if not source.strip():
        return {"success": False, "error": {"message": "No code provided."}}, 400
    try:
        result = CodeTracer.trace(source, language=language, timeout_steps=600)
        status_code = 200 if result.get("success") else 400
        return result, status_code
    except Exception as exc:
        return {"success": False, "error": {"message": str(exc)}}, 400


def handle_samples_request() -> Tuple[Dict[str, Any], int]:
    return {"success": True, "samples": SAMPLES}, 200


def handle_export_request(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    export_type = data.get("type", "svg")
    graph = data.get("graph", {})
    highlight_id = data.get("highlight_id", None)
    title = data.get("title", "Flowchart")

    svg_content = SVGRenderer.render_flowchart(graph, highlight_id)
    if export_type == "html":
        content = DiagramExporter.to_standalone_html(title, svg_content, graph)
        mime = "text/html"
    else:
        content = svg_content
        mime = "image/svg+xml"

    return {
        "success": True,
        "content": content,
        "mime": mime
    }, 200


# ------------------ Standalone Python http.server Mode ------------------

def run_builtin_server(port: int = 5000):
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse

    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

    class Code2FlowHandler(BaseHTTPRequestHandler):
        def _send_json(self, data: Dict[str, Any], status: int = 200):
            response_bytes = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(response_bytes)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response_bytes)

        def _serve_file(self, file_path: str):
            if not os.path.isfile(file_path):
                self.send_error(404, "File not found")
                return
            mime, _ = mimetypes.guess_type(file_path)
            mime = mime or "application/octet-stream"
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(500, f"Error reading file: {e}")

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_GET(self):
            parsed = urlparse(self.path)
            path = parsed.path

            if path == "/" or path == "/index.html":
                self._serve_file(os.path.join(static_dir, "index.html"))
            elif path.startswith("/static/"):
                rel_path = path[len("/static/"):]
                self._serve_file(os.path.join(static_dir, rel_path))
            elif path == "/api/samples":
                res, status = handle_samples_request()
                self._send_json(res, status)
            else:
                self._serve_file(os.path.join(static_dir, path.lstrip("/")))

        def do_POST(self):
            parsed = urlparse(self.path)
            path = parsed.path
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"

            try:
                data = json.loads(post_body)
            except Exception:
                data = {}

            if path == "/api/flowchart":
                res, status = handle_flowchart_request(data)
                self._send_json(res, status)
            elif path == "/api/traceback":
                res, status = handle_traceback_request(data)
                self._send_json(res, status)
            elif path == "/api/dsa":
                res, status = handle_dsa_request(data)
                self._send_json(res, status)
            elif path == "/api/dsa/detect":
                res, status = handle_dsa_detect_request(data)
                self._send_json(res, status)
            elif path == "/api/oop":
                res, status = handle_oop_request(data)
                self._send_json(res, status)
            elif path == "/api/export":
                res, status = handle_export_request(data)
                self._send_json(res, status)
            elif path == "/api/visualize":
                res, status = handle_visualize_request(data)
                self._send_json(res, status)
            else:
                self._send_json({"error": "Endpoint not found"}, 404)

        def log_message(self, format, *args):
            pass

    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, Code2FlowHandler)
    print(f"\n=======================================================")
    print(f"  Code2Flow Multi-Language Server is running locally!")
    print(f"  Open in your web browser: http://127.0.0.1:{port}")
    print(f"  Supported Languages: Python, JavaScript, Java, C/C++")
    print(f"  Mode: Zero-dependency built-in Python http.server")
    print(f"  Python version: {sys.version.split()[0]}")
    print(f"=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Code2Flow server...")
        httpd.server_close()


# ------------------ Flask Mode (when available) ------------------

def run_flask_server(port: int = 5000):
    try:
        from flask import Flask, request, jsonify, send_from_directory
    except ImportError:
        run_builtin_server(port)
        return

    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    app = Flask(__name__, static_folder=static_dir)

    @app.route("/")
    def index():
        return send_from_directory(static_dir, "index.html")

    @app.route("/static/<path:filename>")
    def serve_static(filename):
        return send_from_directory(static_dir, filename)

    @app.route("/api/flowchart", methods=["POST"])
    def api_flowchart():
        res, status = handle_flowchart_request(request.get_json(force=True) or {})
        return jsonify(res), status

    @app.route("/api/traceback", methods=["POST"])
    def api_traceback():
        res, status = handle_traceback_request(request.get_json(force=True) or {})
        return jsonify(res), status

    @app.route("/api/dsa", methods=["POST"])
    def api_dsa():
        res, status = handle_dsa_request(request.get_json(force=True) or {})
        return jsonify(res), status

    @app.route("/api/dsa/detect", methods=["POST"])
    def api_dsa_detect():
        res, status = handle_dsa_detect_request(request.get_json(force=True) or {})
        return jsonify(res), status

    @app.route("/api/oop", methods=["POST"])
    def api_oop():
        res, status = handle_oop_request(request.get_json(force=True) or {})
        return jsonify(res), status

    @app.route("/api/samples", methods=["GET"])
    def api_samples():
        res, status = handle_samples_request()
        return jsonify(res), status

    @app.route("/api/visualize", methods=["POST"])
    def api_visualize():
        res, status = handle_visualize_request(request.get_json(force=True) or {})
        return jsonify(res), status

    @app.route("/api/export", methods=["POST"])
    def api_export():
        res, status = handle_export_request(request.get_json(force=True) or {})
        return jsonify(res), status

    print(f"\n=======================================================")
    print(f"  Code2Flow Multi-Language Server is running locally!")
    print(f"  Open in your web browser: http://127.0.0.1:{port}")
    print(f"  Supported Languages: Python, JavaScript, Java, C/C++")
    print(f"  Mode: Flask Application")
    print(f"  Python version: {sys.version.split()[0]}")
    print(f"=======================================================\n")
    app.run(host="127.0.0.1", port=port, debug=False)


if __name__ == "__main__":
    port_arg = 5000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port_arg = int(sys.argv[1])

    try:
        import flask
        run_flask_server(port_arg)
    except ImportError:
        run_builtin_server(port_arg)
