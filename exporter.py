"""
Code2Flow - Diagram and Model Exporter
Handles exporting flowcharts, DSA states, and OOP class diagrams into
SVG, Mermaid code, Graphviz DOT code, JSON, and standalone offline HTML.
"""

import json
from typing import Dict, Any, Optional
from renderer import SVGRenderer


class DiagramExporter:
    """Provides file export capabilities for generated diagrams."""

    @staticmethod
    def to_svg(flowchart_data: Dict[str, Any], highlight_id: Optional[str] = None) -> str:
        """Returns raw SVG string."""
        return SVGRenderer.render_flowchart(flowchart_data, highlight_id)

    @staticmethod
    def to_json(data: Any) -> str:
        """Returns formatted JSON string."""
        return json.dumps(data, indent=2)

    @staticmethod
    def to_standalone_html(title: str, svg_content: str, metadata: Dict[str, Any] = None) -> str:
        """Generates a self-contained offline HTML file embedding the SVG and metadata."""
        meta_str = json.dumps(metadata or {}, indent=2)
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Code2Flow - {title}</title>
  <style>
    body {{
      margin: 0;
      padding: 24px;
      background: #0f172a;
      color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
    .header {{ margin-bottom: 20px; text-align: center; }}
    .canvas {{
      background: #ffffff;
      border-radius: 12px;
      box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);
      padding: 20px;
      max-width: 95vw;
      overflow: auto;
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>Code2Flow Export: {title}</h1>
    <p>Generated offline with Python AST & Code2Flow</p>
  </div>
  <div class="canvas">
    {svg_content}
  </div>
  <!-- Embedded Metadata -->
  <script type="application/json" id="diagram-meta">
    {meta_str}
  </script>
</body>
</html>
"""
