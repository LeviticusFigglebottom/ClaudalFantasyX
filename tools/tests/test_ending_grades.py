"""Tests for the Ending's grades (M3-ENV-729; colour script `ending_unbinding`, `ending_dock`, `post_credits`).

* Each frame's key, fill, rim and exposure are the colour script's.
* The sea-glow steps down E1-E5 to 0.06 and is exactly 0.0 only at the dock (act3_ending.md §0 rule 4).
* The committed grades table matches the generator.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import ending_grades as eg  # noqa: E402


class EndingGradesTests(unittest.TestCase):
    def test_the_colour_script_values(self) -> None:
        want = {"ending_unbinding": ("#FFDCBF", 0.8, "#0B1630", 0.15, "#FFE9B8", 1.2, 1.15),
                "ending_dock": ("#D2DFFF", 0.25, "#0B1630", 0.1, "#DCE6FF", 0.3, 1.2)}
        for name, (key, ke, fill, fe, rim, re, exp) in want.items():
            g = eg.GRADES[name]
            with self.subTest(frame=name):
                self.assertEqual((g["sun"]["color"], g["sun"]["energy"]), (key, ke))
                self.assertEqual((g["fill"]["color"], g["fill"]["energy"]), (fill, fe))
                self.assertEqual((g["rim"]["color"], g["rim"]["energy"]), (rim, re))
                self.assertEqual(g["exposure"], exp)
        pc = eg.GRADES["post_credits"]
        self.assertEqual((pc["lamp"]["color"], pc["lamp"]["energy"]), ("#FFAE67", 1.4))

    def test_the_sea_glow_steps_down_and_is_dark_only_at_the_dock(self) -> None:
        steps = list(eg.GRADES["ending_unbinding"]["sea_glow_steps"].values())
        self.assertEqual(steps, sorted(steps, reverse=True))
        self.assertEqual(steps[-1], 0.06)
        self.assertEqual(eg.GRADES["ending_dock"]["sea_glow"], 0.0)
        self.assertEqual(eg.GRADES["ending_dock"]["sky"]["moon_disc_energy"], 0.0)  # moonless

    def test_the_committed_table_matches(self) -> None:
        rows = json.loads((eg.OUT / "ending_grades.json").read_text(encoding="utf-8"))
        for name, g in eg.GRADES.items():
            with self.subTest(frame=name):
                self.assertEqual(rows[name]["rim"], g["rim"])
                self.assertEqual(rows[name]["sun"]["color"], g["sun"]["color"])
                self.assertTrue((eg.OUT / f"{name}_environment.tres").is_file())
                self.assertTrue((eg.OUT / f"{g['lut_name']}.png").is_file())


if __name__ == "__main__":
    unittest.main()
