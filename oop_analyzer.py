"""
Code2Flow - OOP Analyzer
Performs AST-based static analysis of Object-Oriented Programming constructs:
- Class definitions and hierarchy
- Attributes (class attributes, instance attributes in __init__)
- Methods (instance, classmethod, staticmethod, property, abstractmethod)
- Encapsulation conventions: public, protected (_), private (__)
- Inheritance patterns: Single, Multilevel, Multiple, Hierarchical
- Method overriding and polymorphism
- Composition and Aggregation detection with confidence levels
"""

import ast
from typing import Dict, Any, List, Optional, Set, Tuple
from parser import safe_unparse


class MethodInfo:
    def __init__(
        self,
        name: str,
        method_type: str = "instance",  # instance, class, static, abstract, property
        visibility: str = "public",     # public, protected, private
        args: List[str] = None,
        return_annotation: str = "",
        is_override: bool = False,
        overridden_from: Optional[str] = None,
        lineno: Optional[int] = None
    ):
        self.name = name
        self.method_type = method_type
        self.visibility = visibility
        self.args = args or []
        self.return_annotation = return_annotation
        self.is_override = is_override
        self.overridden_from = overridden_from
        self.lineno = lineno

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "method_type": self.method_type,
            "visibility": self.visibility,
            "args": self.args,
            "return_annotation": self.return_annotation,
            "is_override": self.is_override,
            "overridden_from": self.overridden_from,
            "lineno": self.lineno
        }


class AttributeInfo:
    def __init__(
        self,
        name: str,
        attr_type: str = "instance",  # instance, class
        visibility: str = "public",   # public, protected, private
        data_type: str = "",
        default_val: str = "",
        lineno: Optional[int] = None
    ):
        self.name = name
        self.attr_type = attr_type
        self.visibility = visibility
        self.data_type = data_type
        self.default_val = default_val
        self.lineno = lineno

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "attr_type": self.attr_type,
            "visibility": self.visibility,
            "data_type": self.data_type,
            "default_val": self.default_val,
            "lineno": self.lineno
        }


class RelationshipInfo:
    def __init__(
        self,
        rel_type: str,  # inheritance, composition, aggregation, dependency
        source: str,
        target: str,
        confidence: str = "certain",  # certain, inferred
        details: str = ""
    ):
        self.rel_type = rel_type
        self.source = source
        self.target = target
        self.confidence = confidence
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.rel_type,
            "source": self.source,
            "target": self.target,
            "confidence": self.confidence,
            "details": self.details
        }


class ClassInfo:
    def __init__(self, name: str, lineno: Optional[int] = None):
        self.name = name
        self.lineno = lineno
        self.bases: List[str] = []
        self.is_abstract: bool = False
        self.class_attributes: List[AttributeInfo] = []
        self.instance_attributes: List[AttributeInfo] = []
        self.methods: List[MethodInfo] = []
        self.instantiated_classes: Set[str] = set()
        self.parameter_classes: Set[str] = set()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "lineno": self.lineno,
            "bases": self.bases,
            "is_abstract": self.is_abstract,
            "class_attributes": [a.to_dict() for a in self.class_attributes],
            "instance_attributes": [a.to_dict() for a in self.instance_attributes],
            "methods": [m.to_dict() for m in self.methods]
        }


class OOPAnalyzer:
    """Analyzes AST to discover classes, attributes, methods, inheritance, and relationships."""

    @classmethod
    def analyze(cls, tree: ast.Module) -> Dict[str, Any]:
        classes: Dict[str, ClassInfo] = {}

        # 1. First pass: extract all classes, methods, and attributes
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                c_info = cls._extract_class_info(node)
                classes[c_info.name] = c_info

        # 2. Second pass: detect inheritance patterns, method overriding, and polymorphism
        inheritance_types: List[str] = []
        relationships: List[RelationshipInfo] = []

        cls._analyze_inheritance_and_overrides(classes, relationships, inheritance_types)

        # 3. Third pass: detect composition and aggregation
        cls._analyze_relationships(classes, relationships)

        # 4. Method call flow simulation / interaction sequence
        call_flows = cls._extract_call_flows(tree, classes)

        return {
            "classes": [c.to_dict() for c in classes.values()],
            "relationships": [r.to_dict() for r in relationships],
            "inheritance_patterns": list(set(inheritance_types)),
            "call_flows": call_flows,
            "total_classes": len(classes)
        }

    @classmethod
    def _extract_class_info(cls, node: ast.ClassDef) -> ClassInfo:
        info = ClassInfo(name=node.name, lineno=getattr(node, "lineno", None))

        # Base classes
        for base in node.bases:
            base_str = safe_unparse(base)
            info.bases.append(base_str)
            if "ABC" in base_str or "Abstract" in base_str:
                info.is_abstract = True

        seen_inst_attrs: Set[str] = set()

        for item in node.body:
            # Class attributes (Assignments at class level)
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        vis = cls._get_visibility(target.id)
                        info.class_attributes.append(AttributeInfo(
                            name=target.id,
                            attr_type="class",
                            visibility=vis,
                            default_val=safe_unparse(item.value),
                            lineno=getattr(item, "lineno", None)
                        ))
            elif isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    vis = cls._get_visibility(item.target.id)
                    info.class_attributes.append(AttributeInfo(
                        name=item.target.id,
                        attr_type="class",
                        visibility=vis,
                        data_type=safe_unparse(item.annotation),
                        default_val=safe_unparse(item.value) if item.value else "",
                        lineno=getattr(item, "lineno", None)
                    ))

            # Methods
            elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                m_info = cls._extract_method_info(item)
                info.methods.append(m_info)
                if m_info.method_type == "abstract":
                    info.is_abstract = True

                # Inspect __init__ for instance attributes and object instantiations
                if item.name == "__init__":
                    cls._extract_init_details(item, info, seen_inst_attrs)

                # Inspect other methods for instantiations and type hints
                cls._extract_method_interactions(item, info)

        return info

    @classmethod
    def _extract_method_info(cls, node: ast.FunctionDef) -> MethodInfo:
        name = node.name
        vis = cls._get_visibility(name)
        m_type = "instance"

        # Check decorators
        for dec in node.decorator_list:
            dec_str = safe_unparse(dec)
            if "classmethod" in dec_str:
                m_type = "class"
            elif "staticmethod" in dec_str:
                m_type = "static"
            elif "abstractmethod" in dec_str:
                m_type = "abstract"
            elif "property" in dec_str:
                m_type = "property"

        # Parameters
        args_list = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {safe_unparse(arg.annotation)}"
            args_list.append(arg_str)

        ret_annot = safe_unparse(node.returns) if node.returns else ""

        return MethodInfo(
            name=name,
            method_type=m_type,
            visibility=vis,
            args=args_list,
            return_annotation=ret_annot,
            lineno=getattr(node, "lineno", None)
        )

    @classmethod
    def _extract_init_details(cls, node: ast.FunctionDef, c_info: ClassInfo, seen_attrs: Set[str]):
        """Extracts self.attribute assignments and instantiated classes inside __init__."""
        for stmt in ast.walk(node):
            if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
                target = stmt.target if isinstance(stmt, ast.AnnAssign) else (stmt.targets[0] if stmt.targets else None)
                if target and isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                    attr_name = target.attr
                    if attr_name not in seen_attrs:
                        seen_attrs.add(attr_name)
                        vis = cls._get_visibility(attr_name)
                        dtype = safe_unparse(stmt.annotation) if isinstance(stmt, ast.AnnAssign) else ""
                        val = safe_unparse(stmt.value) if getattr(stmt, "value", None) else ""

                        c_info.instance_attributes.append(AttributeInfo(
                            name=attr_name,
                            attr_type="instance",
                            visibility=vis,
                            data_type=dtype,
                            default_val=val,
                            lineno=getattr(stmt, "lineno", None)
                        ))

            # Detect instantiations (self.engine = Engine())
            if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Name):
                func_name = stmt.func.id
                # Heuristic: Uppercase first letter indicates class constructor call
                if func_name[0].isupper() and func_name != c_info.name:
                    c_info.instantiated_classes.add(func_name)

    @classmethod
    def _extract_method_interactions(cls, node: ast.FunctionDef, c_info: ClassInfo):
        for arg in node.args.args:
            if arg.annotation and isinstance(arg.annotation, ast.Name):
                annot_name = arg.annotation.id
                if annot_name[0].isupper() and annot_name != c_info.name:
                    c_info.parameter_classes.add(annot_name)

    @classmethod
    def _analyze_inheritance_and_overrides(
        cls,
        classes: Dict[str, ClassInfo],
        relationships: List[RelationshipInfo],
        patterns: List[str]
    ):
        child_count_map: Dict[str, int] = {}

        for c_name, c_info in classes.items():
            for base_name in c_info.bases:
                relationships.append(RelationshipInfo(
                    rel_type="inheritance",
                    source=c_name,
                    target=base_name,
                    confidence="certain",
                    details=f"{c_name} inherits from {base_name}"
                ))
                child_count_map[base_name] = child_count_map.get(base_name, 0) + 1

                # Check if base class exists in current file
                base_class = classes.get(base_name)
                if base_class:
                    base_methods = {m.name: m for m in base_class.methods}
                    for m in c_info.methods:
                        if m.name in base_methods and m.name != "__init__":
                            m.is_override = True
                            m.overridden_from = base_name

            # Classify inheritance pattern
            if len(c_info.bases) == 1:
                base_name = c_info.bases[0]
                base_class = classes.get(base_name)
                if base_class and base_class.bases:
                    patterns.append("Multilevel Inheritance")
                else:
                    patterns.append("Single Inheritance")
            elif len(c_info.bases) > 1:
                patterns.append("Multiple Inheritance")

        # Check Hierarchical
        for base, count in child_count_map.items():
            if count >= 2:
                patterns.append("Hierarchical Inheritance")

    @classmethod
    def _analyze_relationships(cls, classes: Dict[str, ClassInfo], relationships: List[RelationshipInfo]):
        """Identifies composition vs aggregation based on instantiation vs parameter passing."""
        for c_name, c_info in classes.items():
            # Composition: Class instantiates another class inside its __init__
            for target_class in c_info.instantiated_classes:
                relationships.append(RelationshipInfo(
                    rel_type="composition",
                    source=c_name,
                    target=target_class,
                    confidence="certain (instantiated in __init__)",
                    details=f"{c_name} creates and owns an instance of {target_class}"
                ))

            # Aggregation: Class receives another class as parameter or type annotation
            for target_class in c_info.parameter_classes:
                if target_class not in c_info.instantiated_classes:
                    relationships.append(RelationshipInfo(
                        rel_type="aggregation",
                        source=c_name,
                        target=target_class,
                        confidence="inferred (parameter/type hint)",
                        details=f"{c_name} uses {target_class} without owning its lifecycle"
                    ))

    @classmethod
    def _extract_call_flows(cls, tree: ast.Module, classes: Dict[str, ClassInfo]) -> List[Dict[str, str]]:
        """Extracts top-level or method-level call sequences (e.g. car.start_engine())."""
        flows = []
        for stmt in tree.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call = stmt.value
                if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
                    obj_name = call.func.value.id
                    method_name = call.func.attr
                    flows.append({
                        "object": obj_name,
                        "method": method_name,
                        "call": safe_unparse(call),
                        "description": f"Invokes {method_name}() on {obj_name}"
                    })
        return flows

    @staticmethod
    def _get_visibility(name: str) -> str:
        if name.startswith("__") and not name.endswith("__"):
            return "private"
        elif name.startswith("_") and not name.endswith("__"):
            return "protected"
        return "public"
