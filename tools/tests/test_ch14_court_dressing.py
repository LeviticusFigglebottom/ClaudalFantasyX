"""M4-A2P-044: Ch14's court dressing (tools/act2/ch14_court_dressing.py; ansedra_zones.build_court) against the greybox."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "act2"))
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import ansedra_zones as az  # noqa: E402
import ch14_court_dressing as gen  # noqa: E402
import vey_zones as vz  # noqa: E402


class Ch14DressingTests(unittest.TestCase):
    def test_committed_dressing_matches_its_generator(self) -> None:
        committed = json.loads((gen.ZONE_DIR / f"{gen.ZONE}_dressing.json").read_text(encoding="utf-8"))
        self.assertEqual(committed, gen.layout(), "re-run tools/act2/ch14_court_dressing.py")

    def test_every_piece_and_resource_exists(self) -> None:
        lay = gen.layout()
        kit = ROOT / lay["kit_dir"].removeprefix("res://")
        for p in lay["pieces"]:
            self.assertTrue((kit / f"{p['piece']}.glb").is_file(), p["piece"])
        for res in (lay["environment"], f"res://game/levels/ch13/{gen.ZONE}/{gen.ZONE}_water_material.tres"):
            self.assertTrue((ROOT / res.removeprefix("res://")).is_file(), res)

    def test_a_lantern_on_every_column_and_the_water_under_the_barge(self) -> None:
        lay = gen._layout()
        cols = [b for b in lay["blocks"] if b["id"].startswith("Column")]
        self.assertEqual(len(az.lantern_points(lay)), len(cols))
        barge = {b["id"]: b for b in lay["blocks"]}["Barge"]
        self.assertLess(gen.WATER_Y, barge["pos"][1] + barge["size"][1] / 2 - 0.2, "the barge's deck over the water")

    def test_the_halls_stand_outside_the_court(self) -> None:
        lay = gen._layout()
        court = {b["id"]: b for b in lay["blocks"]}["Court"]
        for x, z, _yaw in gen.HALLS:
            self.assertFalse(vz._covers(court, x, z, -0.5), f"a hall's front at {x, z} stands in the court")


if __name__ == "__main__":
    unittest.main()
