import unittest

from utils.report_generator import ReportGenerator


class ReportGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.generator = ReportGenerator()

    def test_summary_identifies_growth_and_new_topics(self):
        trend_data = {
            "Delivery delay": {
                "2024-01-01": 2,
                "2024-01-02": 2,
                "2024-01-03": 4,
                "2024-01-04": 4,
            },
            "New feature": {
                "2024-01-01": 0,
                "2024-01-02": 0,
                "2024-01-03": 2,
                "2024-01-04": 3,
            },
        }

        stats = self.generator.generate_summary_stats(
            trend_data, recent_days=2
        )

        self.assertEqual(stats["total_topics"], 2)
        self.assertEqual(stats["total_mentions"], 17)
        self.assertIn("New feature", stats["new_topics"])
        self.assertEqual(stats["trending_topics"][0]["topic"], "Delivery delay")

    def test_summary_rejects_invalid_window(self):
        with self.assertRaises(ValueError):
            self.generator.generate_summary_stats({}, recent_days=0)

    def test_trend_table_uses_requested_window(self):
        trend_data = {
            "Delivery delay": {
                "2024-01-01": 1,
                "2024-01-02": 3,
                "2024-01-03": 2,
            }
        }

        table = self.generator.generate_trend_table(
            trend_data, "2024-01-03", days=3
        )

        self.assertEqual(table.iloc[0]["Total"], 6)
        self.assertEqual(table.iloc[0]["Trend"], "-")


if __name__ == "__main__":
    unittest.main()
