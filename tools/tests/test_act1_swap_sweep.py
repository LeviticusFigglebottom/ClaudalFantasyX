"""tools/loading/act1_swap_sweep.py (ADR 0042 §4): its targets and how it reads the probe."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "loading"))

import act1_swap_sweep as sweep  # noqa: E402


class Act1SwapSweepTest(unittest.TestCase):
    def test_targets_cover_every_act1_zone_the_title_and_a_battle(self) -> None:
        t = sweep.targets()
        zones = json.loads(sweep.SCENE_LOADS.read_text())["scene_loads"]["scenes"]
        for z in zones:
            self.assertIn(z, t)
        self.assertIn("res://game/core/boot.tscn", t)
        self.assertIn("res://game/battle/scene/battle_sandbox.tscn", t)
        self.assertEqual(len(t), len(set(t)))
        self.assertIn("battle:ch01_hullgnaw", t, "the Act I field battles")
        self.assertNotIn("battle:ch10_", " ".join(t))
        for path in (x for x in t if not x.startswith(sweep.BATTLE_PREFIX)):
            self.assertTrue((ROOT / path.removeprefix("res://")).exists(), path)

    def test_a_probe_line_is_read_and_judged(self) -> None:
        out = "noise\n%s%s\n" % (sweep.PROBE_TAG, json.dumps({"covered": True, "max_frame_ms": 1200.0}))
        r = sweep.row("z", sweep.parse_stats(out))
        self.assertTrue(r["ok"])
        self.assertIn("OVER", sweep.fmt(r), "over budget is reported, not failed")
        uncovered = sweep.row("z", {"covered": False, "max_frame_ms": 10.0})
        self.assertFalse(uncovered["ok"])
        self.assertFalse(sweep.row("z", sweep.parse_stats("no stats")).get("ok"))
        self.assertIsNone(sweep.parse_stats(sweep.PROBE_TAG + "{broken"))


if __name__ == "__main__":
    unittest.main()
