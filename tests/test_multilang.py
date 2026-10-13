"""
Unit tests for Multi-Language parsing (JavaScript, Java, C++).
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from multi_language_parser import MultiLangParser
from multi_language_oop import MultiLangOOPAnalyzer
from traceback_parser import TracebackParser


class TestMultiLanguage(unittest.TestCase):

    def test_javascript_flowchart(self):
        js_code = """const x = 10;
if (x > 5) {
    console.log("Greater");
} else {
    console.log("Smaller");
}
"""
        graph, warnings = MultiLangParser.parse_flowchart(js_code, language="javascript")
        self.assertGreater(graph["node_count"], 3)
        categories = [n["category"] for n in graph["nodes"]]
        self.assertIn("decision", categories)
        self.assertIn("io_output", categories)

    def test_java_flowchart(self):
        java_code = """int counter = 0;
while (counter < 5) {
    System.out.println(counter);
    counter++;
}
"""
        graph, warnings = MultiLangParser.parse_flowchart(java_code, language="java")
        categories = [n["category"] for n in graph["nodes"]]
        self.assertIn("loop_header", categories)
        self.assertIn("io_output", categories)

    def test_cpp_flowchart(self):
        cpp_code = """int temp = 25;
if (temp > 20) {
    cout << "Warm" << endl;
}
"""
        graph, warnings = MultiLangParser.parse_flowchart(cpp_code, language="cpp")
        categories = [n["category"] for n in graph["nodes"]]
        self.assertIn("decision", categories)
        self.assertIn("io_output", categories)

    def test_javascript_oop(self):
        js_oop = """class Engine {
    constructor(hp) { this.hp = hp; }
}
class Car extends Vehicle {
    constructor(hp) {
        this.engine = new Engine(hp);
    }
}
"""
        data = MultiLangOOPAnalyzer.analyze(js_oop, language="javascript")
        self.assertEqual(data["total_classes"], 2)
        rels = data["relationships"]
        self.assertTrue(any(r["type"] == "composition" for r in rels))

    def test_java_oop(self):
        java_oop = """class Dog extends Animal {
    public void bark() {}
}
"""
        data = MultiLangOOPAnalyzer.analyze(java_oop, language="java")
        self.assertEqual(data["total_classes"], 1)
        self.assertEqual(data["classes"][0]["bases"], ["Animal"])

    def test_cpp_oop(self):
        cpp_oop = """class Car : public Vehicle {
public:
    int speed;
    void drive();
};
"""
        data = MultiLangOOPAnalyzer.analyze(cpp_oop, language="cpp")
        self.assertEqual(data["total_classes"], 1)
        self.assertEqual(data["classes"][0]["bases"], ["Vehicle"])

    def test_javascript_traceback_mapping(self):
        js_code = """function test() {
    console.log("running");
    let obj = null;
    return obj.prop;
}
test();
"""
        js_trace = """TypeError: Cannot read properties of null (reading 'prop')
    at test (app.js:4:16)
    at app.js:6:1
"""
        graph, _ = MultiLangParser.parse_flowchart(js_code, language="javascript")
        analysis = TracebackParser.parse_and_map(js_trace, js_code, graph["nodes"], language="javascript")
        self.assertEqual(analysis.matched_lineno, 4)
        self.assertEqual(analysis.status, "matched")

    def test_java_traceback_mapping(self):
        java_code = """public class Main {
    public static void main(String[] args) {
        String str = null;
        System.out.println(str.length());
    }
}
"""
        java_trace = """Exception in thread "main" java.lang.NullPointerException
    at Main.main(Main.java:4)
"""
        graph, _ = MultiLangParser.parse_flowchart(java_code, language="java")
        analysis = TracebackParser.parse_and_map(java_trace, java_code, graph["nodes"], language="java")
        self.assertEqual(analysis.matched_lineno, 4)
        self.assertEqual(analysis.status, "matched")


if __name__ == "__main__":
    unittest.main()
