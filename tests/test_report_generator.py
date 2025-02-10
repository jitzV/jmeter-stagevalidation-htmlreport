import unittest
import pandas as pd
from jmeter_report.report_generator import JMeterReport

class TestJMeterReport(unittest.TestCase):

    def setUp(self):
        self.jtl_file_dir = "test_jtl_files"
        self.jtl_threshold = 10
        self.report = JMeterReport(self.jtl_file_dir, self.jtl_threshold)

    def test_format_duration(self):
        self.assertEqual(self.report.format_duration(3661), "1h 1m")
        self.assertEqual(self.report.format_duration(61), "1m 1s")
        self.assertEqual(self.report.format_duration(59), "59s")

    def test_get_http_code_counts(self):
        data = {'responseCode': ['200', '200', '404']}
        df = pd.DataFrame(data)
        expected_counts = {'200': 2, '404': 1}
        self.assertEqual(self.report.get_http_code_counts(df), expected_counts)

    def test_jmeter_percentile(self):
        data = [1, 2, 3, 4, 5]
        self.assertEqual(self.report.jmeter_percentile(data, 90), 5)
        self.assertEqual(self.report.jmeter_percentile(data, 50), 3)

    def test_is_within_threshold(self):
        self.assertEqual(self.report.is_within_threshold(90, 100, 10), "PASSED")
        self.assertEqual(self.report.is_within_threshold(105, 100, 10), "WARNING")
        self.assertEqual(self.report.is_within_threshold(111, 100, 10), "FAILED")

    def test_validate_metrics(self):
        env_vars = {
            "transaction_tps": "10",
            "transaction_avg": "100",
            "transaction_90P": "200",
            "transaction_99P": "300"
        }
        self.assertTrue(self.report.validate_metrics("transaction", env_vars))
        env_vars.pop("transaction_99P")
        with self.assertRaises(ValueError) as context:
            self.report.validate_metrics("transaction", env_vars)
        self.assertIn("Missing threshold metrics definition for transaction", str(context.exception))

    def test_missing_threshold_metrics(self):
        env_vars = {
            "transaction_tps": "10",
            "transaction_avg": "100",
            "transaction_90P": "200"
        }
        with self.assertRaises(ValueError) as context:
            self.report.validate_metrics("transaction", env_vars)
        self.assertIn("Missing threshold metrics definition for transaction", str(context.exception))

if __name__ == '__main__':
    unittest.main()
