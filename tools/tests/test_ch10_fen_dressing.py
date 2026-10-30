"""M4-A2P-040: Ch10's zone dressing (tools/act2/ch10_fen_dressing.py) and ground (fen_zones.py) against the greybox."""

from __future__ import annotations

import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "act2"))
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import ch10_fen_dressing as gen  # noqa: E402
import fen_zones as fz  # noqa: E402
import kit_common as kc  # noqa: E402

ZONES = ("ossa_fen", "reedhollow")
TREES = ("mangrove_tree", "mangrove_tall", "mangrove_low", "mangrove_young")


class FenDressingTests(unittest.TestCase):
    def test_committed_dressing_matches_its_generator(self) -> None:
        for zone in ZONES:
            committed = json.loads((gen.ZONES / zone / f"{zone}_dressing.json").read_text(encoding="utf-8"))
            self.assertEqual(committed, gen.layout(zone), f"{zone}: re-run tools/act2/ch10_fen_dressing.py")

    def test_every_walk_strip_is_tiled_end_to_end(self) -> None:
        for zone, piece in (("ossa_fen", "root_walk_6m"), ("reedhollow", "reed_causeway_6m")):
            lay = gen._layout(zone)
            pieces = [p for p in gen.layout(zone)["pieces"] if p["piece"] == piece]
            for b in gen._strips(lay, ("Walk", "Pocket", "Exit", "Causeway", "Ring")):
                (ax, az), _ = gen._axes(b)
                half = b["size"][0] / 2
                mine = [p for p in pieces if abs((p["at"][0] - b["pos"][0]) * -az + (p["at"][1] - b["pos"][2]) * ax) < 0.01
                        and abs((p["at"][0] - b["pos"][0]) * ax + (p["at"][1] - b["pos"][2]) * az) <= half]
                along = sorted((p["at"][0] - b["pos"][0]) * ax + (p["at"][1] - b["pos"][2]) * az for p in mine)
                self.assertTrue(along, f"{zone} {b['id']} has pieces")
                self.assertAlmostEqual(along[0] - 3.0, -half, delta=0.01, msg=f"{zone} {b['id']} starts at its end")
                self.assertAlmostEqual(along[-1] + 3.0, half, delta=0.01, msg=f"{zone} {b['id']} ends at its end")
                for a, c in zip(along, along[1:]):
                    self.assertLessEqual(c - a, 6.0 + 0.01, f"{zone} {b['id']}: no gap between pieces")

    def test_no_tree_or_reed_stands_on_a_walk(self) -> None:
        for zone in ZONES:
            segs = [s for s in gen._segments(gen._layout(zone)) if s[2] < 5.0]  # the strips (not the lands)
            for p in gen.layout(zone)["pieces"]:
                if p["piece"] in TREES + ("reed_bed",):
                    d = min(gen._seg_dist(tuple(p["at"]), a, b) - hw for a, b, hw in segs)
                    self.assertGreater(d, 1.0, f"{zone} {p['piece']} at {p['at']} is {d:.2f} m off a walk")

    def test_the_ground_is_level_on_the_land_and_under_water_off_it(self) -> None:
        for zone in ZONES:
            h = fz.zone_height(zone, kc.Noise3(kc.rng_for(f"{zone}_ground", 1)))
            lay = gen._layout(zone)
            blocks = {b["id"]: b for b in lay["blocks"]}
            for bid in fz.ZONE_SPEC[zone][0]:
                x0, x1, z0, z1 = fz._rect(blocks[bid])
                for x, z in ((x0 + 0.5, z0 + 0.5), ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - 0.5, z1 - 0.5)):
                    self.assertAlmostEqual(float(h([x], [z])[0]), 0.0, places=6, msg=f"{zone} {bid} level at {x, z}")
            for b in gen._strips(lay, ("Walk", "Pocket", "Exit", "Causeway", "Ring")):
                y = float(h([b["pos"][0]], [b["pos"][2]])[0])
                self.assertLess(y, -0.1, f"{zone} {b['id']}: the walk stands over water (ground {y:.2f})")

    def test_every_spawn_and_mark_has_a_floor_and_no_tree_on_it(self) -> None:
        for zone in ZONES:
            lay = gen._layout(zone)
            pts = [(k, v) for k, v in lay["spawns"].items()] + [(k, v) for k, v in (lay.get("marks") or {}).items()]
            trees = [p for p in gen.layout(zone)["pieces"] if p["piece"] in TREES]
            for name, p in pts:
                near = min(math.hypot(t["at"][0] - p[0], t["at"][1] - p[2]) for t in trees)
                self.assertGreater(near, 1.5, f"{zone} {name}: a tree stands on it")


if __name__ == "__main__":
    unittest.main()
