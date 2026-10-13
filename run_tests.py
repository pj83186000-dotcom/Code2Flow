"""
Code2Flow - Test Runner
Executes all unit tests with Python standard library unittest.
Run with: python run_tests.py
"""

import unittest
import sys
import os

if __name__ == "__main__":
    test_dir = os.path.join(os.path.dirname(__file__), "tests")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=test_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)
