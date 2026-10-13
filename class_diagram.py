"""
Code2Flow - Class Diagram Generator
Generates UML representations, Mermaid class diagrams, and Graphviz DOT diagrams
from OOP analysis results.
"""

from typing import Dict, Any, List


class ClassDiagramGenerator:
    """Formats analyzed OOP structure into Mermaid, DOT, and visual diagram models."""

    @staticmethod
    def to_mermaid(oop_data: Dict[str, Any]) -> str:
        """Generates Mermaid classDiagram string."""
        lines = ["classDiagram"]

        classes = oop_data.get("classes", [])
        relationships = oop_data.get("relationships", [])

        # Add classes with attributes and methods
        for c in classes:
            c_name = c["name"]
            lines.append(f"    class {c_name} {{")

            if c.get("is_abstract"):
                lines.append(f"        <<abstract>>")

            # Attributes
            for attr in c.get("class_attributes", []) + c.get("instance_attributes", []):
                vis_sign = "+" if attr["visibility"] == "public" else ("#" if attr["visibility"] == "protected" else "-")
                t_type = attr.get("data_type") or "var"
                lines.append(f"        {vis_sign}{t_type} {attr['name']}")

            # Methods
            for m in c.get("methods", []):
                vis_sign = "+" if m["visibility"] == "public" else ("#" if m["visibility"] == "protected" else "-")
                args_str = ", ".join(m["args"])
                ret_str = f" : {m['return_annotation']}" if m.get("return_annotation") else ""
                lines.append(f"        {vis_sign}{m['name']}({args_str}){ret_str}")

            lines.append("    }")

        # Add relationships
        # Inheritance: Base <|-- Child
        # Composition: Owner *-- Component
        # Aggregation: Owner o-- Component
        for r in relationships:
            rel_type = r["type"]
            source = r["source"]
            target = r["target"]

            if rel_type == "inheritance":
                lines.append(f"    {target} <|-- {source} : inherits")
            elif rel_type == "composition":
                lines.append(f"    {source} *-- {target} : owns")
            elif rel_type == "aggregation":
                lines.append(f"    {source} o-- {target} : uses")

        return "\n".join(lines)

    @staticmethod
    def to_dot(oop_data: Dict[str, Any]) -> str:
        """Generates Graphviz DOT representation of UML class diagram."""
        lines = [
            "digraph UMLClassDiagram {",
            "    rankdir=BT;",
            '    node [fontname="Helvetica", fontsize=10, shape="record", style="filled", fillcolor="#f8fafc"];',
            '    edge [fontname="Helvetica", fontsize=9];'
        ]

        classes = oop_data.get("classes", [])
        relationships = oop_data.get("relationships", [])

        for c in classes:
            c_name = c["name"]
            stereotype = "&lt;&lt;abstract&gt;&gt;\\n" if c.get("is_abstract") else ""

            # Attributes block
            attr_lines = []
            for attr in c.get("class_attributes", []) + c.get("instance_attributes", []):
                sign = "+" if attr["visibility"] == "public" else ("#" if attr["visibility"] == "protected" else "-")
                attr_lines.append(f"{sign} {attr['name']}")

            attrs_str = "\\n".join(attr_lines) if attr_lines else "(none)"

            # Methods block
            method_lines = []
            for m in c.get("methods", []):
                sign = "+" if m["visibility"] == "public" else ("#" if m["visibility"] == "protected" else "-")
                override_tag = " [override]" if m.get("is_override") else ""
                method_lines.append(f"{sign} {m['name']}(){override_tag}")

            methods_str = "\\n".join(method_lines) if method_lines else "(none)"

            label = f"{{{stereotype}{c_name}|{attrs_str}|{methods_str}}}"
            lines.append(f'    "{c_name}" [label="{label}"];')

        for r in relationships:
            rel_type = r["type"]
            source = r["source"]
            target = r["target"]

            if rel_type == "inheritance":
                lines.append(f'    "{source}" -> "{target}" [arrowhead="empty", label="inherits"];')
            elif rel_type == "composition":
                lines.append(f'    "{source}" -> "{target}" [arrowhead="diamond", style="solid", label="composition"];')
            elif rel_type == "aggregation":
                lines.append(f'    "{source}" -> "{target}" [arrowhead="odiamond", style="dashed", label="aggregation"];')

        lines.append("}")
        return "\n".join(lines)
