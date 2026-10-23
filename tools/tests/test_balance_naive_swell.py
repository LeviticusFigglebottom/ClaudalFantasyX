"""The report-only naive_swell policy (M2-NIT-03): every suite reports it with no band, next to naive.
Run: python3 -m unittest discover -s tools/tests"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "balance"))
import sim  # noqa: E402


class NaiveSwellTest(unittest.TestCase):
    def test_every_shipped_suite_reports_naive_swell_without_a_band(self):
        for suite in sim.load_targets():
            bands = suite["bands"]
            self.assertIn("naive_swell", bands, suite["id"])
            self.assertIsNone(bands["naive_swell"], f"{suite['id']}: naive_swell is report only")
            order = list(bands)
            self.assertEqual(order.index("naive_swell"), order.index("naive") + 1,
                             f"{suite['id']}: naive_swell sits next to naive in the report")

    def test_a_report_only_row_is_never_out_of_band(self):
        suite = {"id": "s", "chapter": "c", "encounter": "e", "bands": {"naive_swell": None}, "p90_turns_max": 40}
        res = {"policy": "naive_swell", "n": 10, "wins": 9, "win_pct": 90.0, "timeouts": 0, "mean_turns": 5.0,
               "p90_turns": 20, "mean_party_ko": 0.0, "mean_items": 0.0}
        row = sim.summary_rows(suite, [res])[0]
        self.assertTrue(row["in_band"])
        self.assertEqual(row["band"], "report only")


if __name__ == "__main__":
    unittest.main()
