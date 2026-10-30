"""M4-A2P-042: Ch12's zone dressing (tools/act2/ch12_keth_dressing.py) and its greybox-built pieces (keth_zones.py)
against the greybox."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "act2"))
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import ch12_keth_dressing as gen  # noqa: E402
import keth_zones as kz  # noqa: E402
import kit_common as kc  # noqa: E402

ZONES = ("keth_pass", "quellan", "cloudloom")


class Ch12DressingTests(unittest.TestCase):
    def test_committed_dressing_matches_its_generator(self) -> None:
        for zone in ZONES:
            committed = json.loads((gen.ZONES / zone / f"{zone}_dressing.json").read_text(encoding="utf-8"))
            self.assertEqual(committed, gen.layout(zone), f"{zone}: re-run tools/act2/ch12_keth_dressing.py")

    def test_every_piece_and_its_grade_exist(self) -> None:
        for zone in ZONES:
            lay = gen.layout(zone)
            kit = ROOT / lay["kit_dir"].removeprefix("res://")
            for p in lay["pieces"]:
                self.assertTrue((kit / f"{p['piece']}.glb").is_file(), f"{zone}: {p['piece']}.glb")
            self.assertTrue((ROOT / lay["environment"].removeprefix("res://")).is_file())

    def test_the_ground_lies_under_every_walk_and_spawn(self) -> None:
        for zone in ZONES:
            h = kz.zone_height(zone, kc.Noise3(kc.rng_for(f"{zone}_ground", 1)))
            for s in kz.surfaces(zone):
                if s.block is not None:
                    x0, x1, _, _, z0, z1 = kz._box(s.block)
                    pts = [((x0 + x1) / 2, (z0 + z1) / 2), (x0 + 0.4, z0 + 0.4), (x1 - 0.4, z1 - 0.4)]
                else:
                    pts = [tuple((s.a + s.d * f)[[0, 2]]) for f in (0.05, 0.5, 0.95)]
                for x, z in pts:
                    g = float(h(np.array([x]), np.array([z]))[0])
                    want = float(s.height(np.array([x]), np.array([z]))[0])
                    self.assertAlmostEqual(g, want - kz.GROUND_SINK, places=5, msg=f"{zone} at {x, z}")
            lay = kz.layout(zone)
            for name, p in list(lay["spawns"].items()) + list(lay.get("marks", {}).items()):
                g = float(h(np.array([p[0]]), np.array([p[2]]))[0])
                self.assertLess(g, p[1] + 0.05, f"{zone} {name}: no ground over it")
                self.assertGreater(g, p[1] - 0.3, f"{zone} {name}: ground under it")

    def test_cloudloom_hangs_its_keth_over_the_rows_and_keeps_the_aisle(self) -> None:
        lay = gen._layout("cloudloom")
        rows = {round(b["pos"][2], 3) for b in lay["blocks"] if b["id"].startswith("Keth")}
        curtains = [p for p in gen.layout("cloudloom")["pieces"] if p["piece"] == "keth_curtain"]
        self.assertEqual(len(curtains), 2 * len(rows), "two curtains a row")
        aisle = min(abs(b["pos"][0]) for b in lay["blocks"] if b["id"].startswith("Keth")) - 0.5
        for p in curtains:
            self.assertIn(round(p["at"][1], 3), rows)
            self.assertGreater(abs(p["at"][0]) - 3.0, aisle - 1.0, f"a curtain at {p['at']} hangs in the aisle")

    def test_quellan_builds_every_house_and_sets_the_inn_on_its_block(self) -> None:
        lay = gen._layout("quellan")
        houses = [b for b in lay["blocks"] if b["id"].startswith("House")]
        self.assertEqual(sum(1 for b in houses if b["id"].endswith("N")) + sum(1 for b in houses if b["id"].endswith("S")),
                         len(houses))
        inn = {b["id"]: b for b in lay["blocks"]}["Inn"]
        p = next(p for p in gen.layout("quellan")["pieces"] if p["piece"] == "quellan_inn")
        self.assertEqual(p["at"], [inn["pos"][0], kz._box(inn)[5]], "the inn's front on the Inn block's street face")


if __name__ == "__main__":
    unittest.main()
