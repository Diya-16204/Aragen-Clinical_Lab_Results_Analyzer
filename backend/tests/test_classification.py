import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mcp_server.server import classify_lab_result_impl


class ClassificationTests(unittest.TestCase):
    def test_normal_value(self):
        self.assertEqual(classify_lab_result_impl("Glucose", 99, "mg/dL")["status"], "NORMAL")

    def test_warning_value(self):
        self.assertEqual(classify_lab_result_impl("Glucose", 180, "mg/dL")["status"], "WARNING")

    def test_critical_value(self):
        self.assertEqual(classify_lab_result_impl("Hemoglobin", 6.8, "g/dL")["status"], "CRITICAL")

    def test_invalid_unit(self):
        self.assertFalse(classify_lab_result_impl("Glucose", 99, "mmol/L")["found"])

    def test_unknown_test(self):
        self.assertFalse(classify_lab_result_impl("Not a test", 1, "x")["found"])


if __name__ == "__main__":
    unittest.main()
