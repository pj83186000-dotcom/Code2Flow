"""
Code2Flow - Local SVG Vector Renderer
Renders interactive flowcharts and UML class diagrams as high-resolution SVGs
with modern aesthetics, curved connectors, and zero external binary dependencies.
"""

import html
from typing import Dict, Any, List, Optional


class SVGRenderer:
    """Pure-Python SVG generator for flowcharts and UML class diagrams."""

    @classmethod
    def render_flowchart(cls, graph_data: Dict[str, Any], highlight_node_id: Optional[str] = None) -> str:
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])

        if not nodes:
            return '<svg width="400" height="150" xmlns="http://www.w3.org/2000/svg"><text x="20" y="80" fill="#94a3b8" font-family="sans-serif">No nodes to render</text></svg>'

        # Determine canvas bounds
        min_x = min(n["x"] - n["width"] / 2 for n in nodes)
        max_x = max(n["x"] + n["width"] / 2 for n in nodes)
        min_y = min(n["y"] - n["height"] / 2 for n in nodes)
        max_y = max(n["y"] + n["height"] / 2 for n in nodes)

        padding = 80
        width = max(800.0, max_x - min_x + padding * 2)
        height = max(500.0, max_y - min_y + padding * 2)

        # Shift offset
        offset_x = padding - min_x
        offset_y = padding - min_y

        node_map = {n["id"]: n for n in nodes}

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" width="100%" height="100%" class="code2flow-svg">',
            '<defs>',
            '  <!-- Arrow Markers -->',
            '  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b" />',
            '  </marker>',
            '  <marker id="arrow-true" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#10b981" />',
            '  </marker>',
            '  <marker id="arrow-false" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#ef4444" />',
            '  </marker>',
            '  <marker id="arrow-loop" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            '    <path d="M 0 1 L 10 5 L 0 9 z" fill="#8b5cf6" />',
            '  </marker>',
            '  <filter id="shadow" x="-10%" y="-10%" width="130%" height="130%">',
            '    <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#0f172a" flood-opacity="0.12" />',
            '  </filter>',
            '  <filter id="error-glow" x="-20%" y="-20%" width="140%" height="140%">',
            '    <feDropShadow dx="0" dy="0" stdDeviation="10" flood-color="#ef4444" flood-opacity="0.8" />',
            '  </filter>',
            '</defs>',
            '<style>',
            '  .node-label { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 13px; font-weight: 500; }',
            '  .edge-label { font-family: system-ui, -apple-system, sans-serif; font-size: 11px; font-weight: 600; fill: #475569; }',
            '  .node-shape { transition: all 0.2s ease; cursor: pointer; }',
            '  .node-shape:hover { filter: brightness(1.05); }',
            '</style>'
        ]

        # Draw Edges first so nodes sit on top
        for edge in edges:
            from_n = node_map.get(edge["from"])
            to_n = node_map.get(edge["to"])
            if not from_n or not to_n:
                continue

            x1 = from_n["x"] + offset_x
            y1 = from_n["y"] + offset_y + from_n["height"] / 2
            x2 = to_n["x"] + offset_x
            y2 = to_n["y"] + offset_y - to_n["height"] / 2

            # Edge style & marker
            marker_id = "arrow"
            stroke_color = "#64748b"
            if edge.get("edge_type") == "true" or edge.get("label") == "True":
                marker_id = "arrow-true"
                stroke_color = "#10b981"
            elif edge.get("edge_type") == "false" or edge.get("label") == "False":
                marker_id = "arrow-false"
                stroke_color = "#ef4444"
            elif edge.get("edge_type") == "loop_back":
                marker_id = "arrow-loop"
                stroke_color = "#8b5cf6"

            # Curved path
            if edge.get("edge_type") == "loop_back":
                # Route loop back with a sweep to the left
                ctrl_x = min(x1, x2) - 90
                d = f"M {x1} {y1 - from_n['height']/2} C {ctrl_x} {y1}, {ctrl_x} {y2}, {x2 - to_n['width']/2} {to_n['y'] + offset_y}"
            else:
                ctrl_y = (y1 + y2) / 2
                d = f"M {x1} {y1} C {x1} {ctrl_y}, {x2} {ctrl_y}, {x2} {y2}"

            svg_parts.append(
                f'<path d="{d}" fill="none" stroke="{stroke_color}" stroke-width="2" marker-end="url(#{marker_id})" />'
            )

            # Edge label
            if edge.get("label"):
                lbl_x = (x1 + x2) / 2 + 10
                lbl_y = (y1 + y2) / 2
                lbl_bg = "#ffffff" if edge.get("label") in ["True", "False"] else "none"
                svg_parts.append(
                    f'<rect x="{lbl_x - 14}" y="{lbl_y - 10}" width="28" height="16" rx="4" fill="#f1f5f9" stroke="{stroke_color}" stroke-width="1" />'
                )
                svg_parts.append(
                    f'<text x="{lbl_x}" y="{lbl_y + 2}" text-anchor="middle" class="edge-label">{html.escape(edge["label"])}</text>'
                )

        # Draw Nodes
        for node in nodes:
            x = node["x"] + offset_x
            y = node["y"] + offset_y
            w = node["width"]
            h = node["height"]
            nid = node["id"]
            shape = node.get("shape", "rectangle")
            cat = node.get("category", "process")
            label = node.get("label", "")
            is_highlight = (nid == highlight_node_id)

            # Theme colors
            fill = "#ffffff"
            stroke = "#cbd5e1"
            text_color = "#0f172a"

            if cat == "start" or cat == "end":
                fill = "#ecfdf5"
                stroke = "#10b981"
                text_color = "#065f46"
            elif cat == "decision" or cat == "loop_header":
                fill = "#fffbeb"
                stroke = "#f59e0b"
                text_color = "#92400e"
            elif cat == "io_input" or cat == "io_output":
                fill = "#f5f3ff"
                stroke = "#8b5cf6"
                text_color = "#5b21b6"
            elif cat == "jump":
                fill = "#fff1f2"
                stroke = "#f43f5e"
                text_color = "#9f1239"
            elif cat == "exception":
                fill = "#fdf2f8"
                stroke = "#ec4899"
                text_color = "#831843"
            else:
                fill = "#f8fafc"
                stroke = "#3b82f6"
                text_color = "#1e3a8a"

            filt = 'filter="url(#shadow)"'
            if is_highlight:
                fill = "#fee2e2"
                stroke = "#ef4444"
                text_color = "#991b1b"
                filt = 'filter="url(#error-glow)" stroke-width="3"'

            svg_parts.append(f'<g id="{nid}" class="flow-node-group" data-node-id="{nid}">')

            # Render Shape
            if shape == "oval":
                rx = w / 2
                ry = h / 2
                svg_parts.append(
                    f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="2" {filt} class="node-shape" />'
                )
            elif shape == "diamond":
                points = f"{x},{y - h/2} {x + w/2},{y} {x},{y + h/2} {x - w/2},{y}"
                svg_parts.append(
                    f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="2" {filt} class="node-shape" />'
                )
            elif shape == "parallelogram":
                skew = 18
                points = f"{x - w/2 + skew},{y - h/2} {x + w/2},{y - h/2} {x + w/2 - skew},{y + h/2} {x - w/2},{y + h/2}"
                svg_parts.append(
                    f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="2" {filt} class="node-shape" />'
                )
            else:  # rectangle
                svg_parts.append(
                    f'<rect x="{x - w/2}" y="{y - h/2}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="2" {filt} class="node-shape" />'
                )

            # Node Label (truncated if long)
            escaped_lbl = html.escape(label[:32] + ("..." if len(label) > 32 else ""))
            svg_parts.append(
                f'<text x="{x}" y="{y + 4}" text-anchor="middle" fill="{text_color}" class="node-label">{escaped_lbl}</text>'
            )

            # Line number tag
            if node.get("lineno"):
                svg_parts.append(
                    f'<text x="{x + w/2 - 8}" y="{y - h/2 + 14}" text-anchor="end" font-size="9" fill="#94a3b8" font-family="sans-serif">L{node["lineno"]}</text>'
                )

            svg_parts.append('</g>')

        svg_parts.append('</svg>')
        return "\n".join(svg_parts)
