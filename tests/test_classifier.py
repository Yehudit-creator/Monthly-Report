
import unittest

from parsing.classifier import identify_report_type


class TestClassifier(unittest.TestCase):

    def test_identifies_report_a(self):
        text = "הפסקה 100% 125% 150%"
        self.assertEqual(identify_report_type(text), "A")

    def test_identifies_report_b(self):
        text = "עבודה לחודש"
        self.assertEqual(identify_report_type(text), "B")

    def test_empty_text_returns_unknown(self):
        text = ""
        self.assertEqual(identify_report_type(text), "UNKNOWN")

    def test_unrelated_text_returns_unknown(self):
        text = "שלום עולם"
        self.assertEqual(identify_report_type(text), "UNKNOWN")

    def test_equal_scores_return_unknown(self):
        text = "הפסקה עבודה לחודש"
        self.assertEqual(identify_report_type(text), "UNKNOWN")


if __name__ == "__main__":
    unittest.main()

