"""Tests for Hollowmere's Ch15 pieces and its dressing generator (M4-A2P-045; env-art-b).

* The dock's modules cover the greybox Dock end to end, keep a rail only where the greybox has one (the jetties'
  mouths and the ship's gangway stay open), and the jetties run from the dock's edge to the house platforms.
* The walk floats at the lashed hulls' deck height over the lagoon; the dock's deck is at y 0.
* Every oil lamp carries its light at its flame; the files on disk are the generator's.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import hollowmere  # noqa: E402


def _generator():
    path = ROOT / "tools/act2/ch15_hollowmere_dressing.py"
    spec = importlib.util.spec_from_file_location("ch15_hollowmere_dressing", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN = _generator()


class HollowmereTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.b = GEN.blocks()
        cls.d = GEN.dressing()

    def test_the_dock_covers_the_greybox_dock_with_rails_where_it_has_them(self) -> None:
        rows = [p for p in self.d["pieces"] if p["piece"].startswith("hm_dock_4m") and p["yaw_deg"] == 0.0]
        dock = self.b["Dock"]
        x0, x1 = dock["pos"][0] - dock["size"][0] * 0.5, dock["pos"][0] + dock["size"][0] * 0.5
        spans = sorted((r["at"][0] - 2.0 * r["scale"], r["at"][0] + 2.0 * r["scale"]) for r in rows)
        self.assertAlmostEqual(spans[0][0], x0, delta=0.01)
        self.assertAlmostEqual(spans[-1][1], x1, delta=0.01)
        north, south = GEN._intervals(self.b, "DockRailN"), GEN._intervals(self.b, "DockRailS")
        for r, (lo, hi) in zip(sorted(rows, key=lambda r: r["at"][0]), spans):
            self.assertEqual("open_n" not in r["piece"] and "open_ns" not in r["piece"],
                             GEN._covered(lo, hi, north) >= GEN.RAIL_COVER, r)
        gang = [r for r in rows if 26.0 < r["at"][0] < 34.0]
        self.assertTrue(all("open_s" in r["piece"] or "open_ns" in r["piece"] for r in gang), "the gangway is open")

    def test_the_walk_floats_at_the_hulls_deck(self) -> None:
        self.assertAlmostEqual(-GEN.WATER_Y, hollowmere.DECK_Y, delta=0.001)
        mb = hollowmere.build_dock()[0]
        lo, hi = mb.bounds()
        timber = mb.materials.index(hollowmere.M_TIMBER)
        import numpy as np  # noqa: PLC0415

        tris = np.asarray(mb.tris).reshape(-1, 3)
        top = np.asarray(mb.pos)[np.unique(tris[np.asarray(mb.tri_mat) == timber])][:, 1].max()
        self.assertAlmostEqual(top, 0.0, delta=0.03, msg="the deck at y 0")
        self.assertLess(lo[1], GEN.WATER_Y, "the pontoons in the water")

    def test_every_oil_lamp_carries_its_light(self) -> None:
        oil = [l for l in self.d["fire_lights"] if "color" not in l]
        self.assertEqual(len(oil), len(GEN.OIL_LAMPS) + 1, "the lamps and the supper's")
        for (x, z, yaw), light in zip(GEN.OIL_LAMPS, oil):
            self.assertEqual(light["at"], GEN._flame(x, z, yaw))

    def test_the_files_are_the_generators(self) -> None:
        on_disk = json.loads((GEN.ZONE / "hollowmere_dressing.json").read_text(encoding="utf-8"))
        self.assertEqual(on_disk, self.d)
        self.assertEqual((GEN.ZONE / GEN.ENV_NAME).read_text(encoding="utf-8"), GEN.environment())
        self.assertEqual((GEN.ZONE / GEN.WATER_NAME).read_text(encoding="utf-8"), GEN.water())


if __name__ == "__main__":
    unittest.main()
