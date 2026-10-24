"""Band checks in tools/balance/sim.py (M1-CMB-07: the ease ceiling for smart).
Run: python3 -m unittest discover -s tools/tests"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "balance"))
import sim  # noqa: E402

SUITE = {
    "id": "s", "chapter": "c", "encounter": "e", "loadout": "l",
    "bands": {"smart": [85, 100], "naive": [5, 15]},
    "mean_turns_min": {"smart": 16},
    "p90_turns_max": 40,
}


def result(policy: str, win_pct: float, mean_turns: float, p90: int = 20) -> dict:
    return {"policy": policy, "n": 100, "wins": int(win_pct), "win_pct": win_pct, "timeouts": 0,
            "mean_turns": mean_turns, "p90_turns": p90, "mean_party_ko": 0.0, "mean_items": 0.0}


class EaseCeilingTest(unittest.TestCase):
    def rows(self, *results: dict) -> dict:
        return {r["policy"]: r for r in sim.summary_rows(SUITE, list(results))}

    def test_a_full_win_rate_that_got_faster_is_out_of_band(self):
        rows = self.rows(result("smart", 100.0, 15.9))
        self.assertFalse(rows["smart"]["in_band"])

    def test_at_or_above_the_floor_is_in_band(self):
        self.assertTrue(self.rows(result("smart", 100.0, 16.0))["smart"]["in_band"])
        self.assertTrue(self.rows(result("smart", 100.0, 18.1))["smart"]["in_band"])

    def test_the_win_band_still_applies(self):
        self.assertFalse(self.rows(result("smart", 80.0, 18.0))["smart"]["in_band"])

    def test_policies_without_a_floor_ignore_turns(self):
        self.assertTrue(self.rows(result("naive", 10.0, 3.0))["naive"]["in_band"])

    def test_band_text_names_the_floor(self):
        rows = self.rows(result("smart", 100.0, 18.0), result("naive", 10.0, 17.0))
        self.assertEqual(rows["smart"]["band"], "85–100%, ≥ 16 mean turns")
        self.assertEqual(rows["naive"]["band"], "5–15%")
        self.assertEqual(sim.band_text(None, 14.5), "report only, ≥ 14.5 mean turns")

    def test_the_shipped_targets_floor_smart_in_both_sandbox_suites(self):
        suites = {s["id"]: s for s in sim.load_targets()}
        for sid in ("sandbox_reef", "sandbox_reef_tier1"):
            floor = sim.turns_floor(suites[sid], "smart")
            self.assertIsNotNone(floor, sid)
            self.assertGreater(floor, 0)
            self.assertIsNone(sim.turns_floor(suites[sid], "naive"))



class SwellColumnTest(unittest.TestCase):
    """M2-CMB-01: a suite's Swell quality, the --swell override and the report's Swell columns."""

    def test_suite_swell_defaults_off_and_the_override_wins(self):
        self.assertEqual(sim.suite_swell(SUITE), "off")
        self.assertEqual(sim.suite_swell(dict(SUITE, swell="good")), "good")
        self.assertEqual(sim.suite_swell(dict(SUITE, swell="good"), "perfect"), "perfect")

    def test_rows_and_markdown_carry_swell(self):
        r = dict(result("smart", 100.0, 18.0), mean_swells=0.554)
        row = sim.summary_rows(dict(SUITE, swell="good"), [r])[0]
        self.assertEqual((row["swell"], row["mean_swells"]), ("good", 0.55))
        md = sim.markdown([row], [dict(SUITE, swell="good")], 10, "2026-10-23")
        self.assertIn("| Swell | Policy |", md)
        self.assertIn("| good | smart | 100.0 |", md)
        self.assertIn("| 0.55 |", md)
        self.assertIn("| l | good | (all) | pending |", md)

    def test_the_shipped_suites_play_swell_at_good(self):
        for s in sim.load_targets():
            self.assertIn(sim.suite_swell(s), sim.SWELL_QUALITIES, s["id"])
            # M2-CMB-05: the Vowbound line was accepted on a probe with no hero Swell (balance_targets.md);
            # M2-CMB-06 adds its Swell-on twin (`_good`), at good like every other suite.
            off = s.get("kind") == "vowbound" and not s["id"].endswith("_good")
            self.assertEqual(s.get("swell"), "off" if off else "good", s["id"])


if __name__ == "__main__":
    unittest.main()
