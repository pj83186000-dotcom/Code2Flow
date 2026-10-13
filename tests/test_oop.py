"""
Unit tests for OOPAnalyzer and ClassDiagramGenerator.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parser import SourceParser
from oop_analyzer import OOPAnalyzer
from class_diagram import ClassDiagramGenerator


class TestOOP(unittest.TestCase):

    def test_single_inheritance_and_overriding(self):
        code = """class Animal:
    def __init__(self, name: str):
        self.name = name
    def speak(self):
        return 'Noise'

class Dog(Animal):
    def speak(self):
        return 'Woof'
"""
        tree, _, _ = SourceParser.validate_and_parse(code)
        oop_data = OOPAnalyzer.analyze(tree)

        self.assertEqual(oop_data["total_classes"], 2)
        dog_class = next(c for c in oop_data["classes"] if c["name"] == "Dog")
        self.assertEqual(dog_class["bases"], ["Animal"])

        # Check method overriding
        speak_method = next(m for m in dog_class["methods"] if m["name"] == "speak")
        self.assertTrue(speak_method["is_override"])
        self.assertEqual(speak_method["overridden_from"], "Animal")

        # Verify inheritance relationship
        rels = oop_data["relationships"]
        self.assertTrue(any(r["type"] == "inheritance" and r["source"] == "Dog" and r["target"] == "Animal" for r in rels))

    def test_composition_detection(self):
        code = """class Engine:
    def __init__(self, hp: int):
        self.hp = hp

class Car:
    def __init__(self):
        self.engine = Engine(150)
"""
        tree, _, _ = SourceParser.validate_and_parse(code)
        oop_data = OOPAnalyzer.analyze(tree)

        rels = oop_data["relationships"]
        comp_rel = next((r for r in rels if r["type"] == "composition"), None)
        self.assertIsNotNone(comp_rel)
        self.assertEqual(comp_rel["source"], "Car")
        self.assertEqual(comp_rel["target"], "Engine")
        self.assertIn("certain", comp_rel["confidence"])

    def test_multiple_inheritance(self):
        code = """class Flyer: pass
class Swimmer: pass
class Duck(Flyer, Swimmer): pass
"""
        tree, _, _ = SourceParser.validate_and_parse(code)
        oop_data = OOPAnalyzer.analyze(tree)
        self.assertIn("Multiple Inheritance", oop_data["inheritance_patterns"])

    def test_mermaid_and_dot_generation(self):
        code = """class Shape:
    def area(self): pass
"""
        tree, _, _ = SourceParser.validate_and_parse(code)
        oop_data = OOPAnalyzer.analyze(tree)
        mermaid = ClassDiagramGenerator.to_mermaid(oop_data)
        dot = ClassDiagramGenerator.to_dot(oop_data)

        self.assertTrue(mermaid.startswith("classDiagram"))
        self.assertTrue(dot.startswith("digraph UMLClassDiagram"))


if __name__ == "__main__":
    unittest.main()
