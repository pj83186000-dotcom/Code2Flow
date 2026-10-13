"""
Code2Flow - Multi-Language OOP Analyzer
Parses class hierarchies, inheritance, and composition in JavaScript, Java, and C++.
"""

import re
from typing import Dict, Any, List, Optional
from oop_analyzer import ClassInfo, AttributeInfo, MethodInfo, RelationshipInfo


class MultiLangOOPAnalyzer:
    """Extracts OOP models and UML relationships from JavaScript, Java, and C++ source code."""

    @classmethod
    def analyze(cls, code: str, language: str = "javascript") -> Dict[str, Any]:
        classes: Dict[str, ClassInfo] = {}
        relationships: List[RelationshipInfo] = []
        inheritance_patterns: List[str] = []

        lines = code.splitlines()

        # Regular expressions for class declarations
        # JS: class Dog extends Animal
        # Java: public class Dog extends Animal implements Pet
        # C++: class Dog : public Animal, public Swimmer
        class_regex = re.compile(
            r"class\s+(?P<name>[A-Za-z0-9_$]+)(?:\s*(?:extends|:)\s*(?P<bases>[A-Za-z0-9_$,\s]+))?"
        )

        current_class: Optional[ClassInfo] = None
        current_visibility = "public" if language == "javascript" else "private"

        for idx, line in enumerate(lines):
            trimmed = line.strip()

            # C++ visibility labels
            if language == "cpp":
                if trimmed.startswith("public:"):
                    current_visibility = "public"
                    continue
                elif trimmed.startswith("protected:"):
                    current_visibility = "protected"
                    continue
                elif trimmed.startswith("private:"):
                    current_visibility = "private"
                    continue

            # Check class definition
            c_match = class_regex.search(trimmed)
            if c_match:
                c_name = c_match.group("name")
                current_class = ClassInfo(name=c_name, lineno=idx + 1)
                classes[c_name] = current_class

                bases_str = c_match.group("bases")
                if bases_str:
                    # Clean C++ 'public Animal' or Java 'Animal implements Pet'
                    cleaned_bases = []
                    for b in bases_str.replace("implements", ",").split(","):
                        clean_b = re.sub(r"\b(public|protected|private)\b", "", b).strip()
                        if clean_b:
                            cleaned_bases.append(clean_b)
                            current_class.bases.append(clean_b)
                            relationships.append(RelationshipInfo(
                                rel_type="inheritance",
                                source=c_name,
                                target=clean_b,
                                confidence="certain",
                                details=f"{c_name} extends/inherits {clean_b}"
                            ))

                    if len(cleaned_bases) > 1:
                        inheritance_patterns.append("Multiple Inheritance")
                    elif len(cleaned_bases) == 1:
                        inheritance_patterns.append("Single Inheritance")
                continue

            if not current_class:
                continue

            # Detect Composition: new Engine() or Engine* engine = new Engine()
            inst_match = re.search(r"new\s+([A-Z][A-Za-z0-9_$]*)\s*\(", trimmed)
            if inst_match:
                target_cls = inst_match.group(1)
                if target_cls != current_class.name:
                    relationships.append(RelationshipInfo(
                        rel_type="composition",
                        source=current_class.name,
                        target=target_cls,
                        confidence="certain (instantiated via new)",
                        details=f"{current_class.name} creates and owns instance of {target_cls}"
                    ))

            # Detect Methods
            method_match = cls._match_method(trimmed, language, current_class.name)
            if method_match:
                m_name, m_args, vis = method_match
                if m_name not in [m.name for m in current_class.methods]:
                    current_class.methods.append(MethodInfo(
                        name=m_name,
                        method_type="instance",
                        visibility=vis or current_visibility,
                        args=m_args,
                        lineno=idx + 1
                    ))
                continue

            # Detect Attributes / Fields
            attr_match = cls._match_attribute(trimmed, language)
            if attr_match:
                a_name, a_type, vis = attr_match
                if a_name not in [a.name for a in current_class.instance_attributes]:
                    current_class.instance_attributes.append(AttributeInfo(
                        name=a_name,
                        attr_type="instance",
                        visibility=vis or current_visibility,
                        data_type=a_type,
                        lineno=idx + 1
                    ))

        return {
            "classes": [c.to_dict() for c in classes.values()],
            "relationships": [r.to_dict() for r in relationships],
            "inheritance_patterns": list(set(inheritance_patterns)),
            "call_flows": [],
            "total_classes": len(classes)
        }

    @classmethod
    def _match_method(cls, line: str, language: str, class_name: str) -> Optional[Tuple[str, List[str], str]]:
        if "(" not in line or line.startswith("//"):
            return None

        # JS: constructor(name) or bark(volume)
        if language == "javascript":
            m = re.match(r"(?:async\s+)?([A-Za-z0-9_$]+)\s*\((.*?)\)\s*\{?", line)
            if m:
                name = m.group(1)
                args = [a.strip() for a in m.group(2).split(",") if a.strip()]
                vis = "private" if name.startswith("#") else "public"
                if name not in ("if", "for", "while", "switch", "catch"):
                    return name, args, vis

        # Java / C++
        vis = "public" if "public" in line else ("protected" if "protected" in line else "private")
        m = re.match(r"(?:public|protected|private|static|void|int|double|bool|String|auto)?\s*([A-Za-z0-9_$]+)\s*\((.*?)\)\s*(?:const)?\s*\{?", line)
        if m:
            name = m.group(1)
            args = [a.strip() for a in m.group(2).split(",") if a.strip()]
            if name not in ("if", "for", "while", "switch", "catch"):
                return name, args, vis

        return None

    @classmethod
    def _match_attribute(cls, line: str, language: str) -> Optional[Tuple[str, str, str]]:
        vis = "public" if "public" in line else ("protected" if "protected" in line else "private")
        # JS: this.name = ... or #privateField;
        if language == "javascript":
            m = re.search(r"this\.([A-Za-z0-9_$]+)\s*=", line)
            if m:
                return m.group(1), "var", "public"
            m = re.match(r"#([A-Za-z0-9_$]+)\s*;", line)
            if m:
                return f"#{m.group(1)}", "var", "private"

        # Java / C++: int hp; or String brand;
        m = re.match(r"(?:public|protected|private)?\s*(int|float|double|char|bool|boolean|String|auto|[A-Za-z0-9_$]+)\s+([A-Za-z0-9_$]+)\s*(?:=.*?)?;", line)
        if m:
            t_type = m.group(1)
            name = m.group(2)
            if name not in ("return", "if", "for", "while"):
                return name, t_type, vis

        return None
