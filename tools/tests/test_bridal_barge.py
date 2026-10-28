"""Tests for Merel's bridal barge (M3-ENV-720; open_sea_ch15.md): the Wakefin's arena floor.

* The deck is level at y 0 over every battle slot's metre (docs/kb/tech/battle_arenas.md), and faces up.
* Nothing on the barge can light it: no flame material, and the bow's lamp hook is empty (the colour script's ch15).
* The near rail stays under the battle camera's rays to the slots; the boss anchor is in the water off the bow.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import bridal_barge as bb  # noqa: E402

SLOTS_XZ = ((2.1, 0.7), (3.0, -1.1), (1.4, 2.0), (-2.4, 0.9), (-3.4, -1.2), (-1.2, -0.6))
CAMERA = np.array([0.6, 2.8, 8.4])
BARGE = bb.build_barge()[0]
TRI = np.asarray(BARGE.pos)[np.asarray(BARGE.tris)]


class BridalBargeTests(unittest.TestCase):
    def test_the_deck_is_level_over_every_slots_metre(self) -> None:
        lo, hi = TRI.min(axis=1), TRI.max(axis=1)
        for sx, sz in SLOTS_XZ:
            for dx, dz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                x, z = sx + dx, sz + dz
                m = (lo[:, 0] <= x) & (hi[:, 0] >= x) & (lo[:, 2] <= z) & (hi[:, 2] >= z) & (hi[:, 1] < 1.0)
                with self.subTest(slot=(sx, sz), off=(dx, dz)):
                    self.assertTrue(m.any())
                    self.assertAlmostEqual(float(hi[m, 1].max()), 0.0, delta=0.05)

    def test_the_deck_faces_up(self) -> None:
        deck = np.asarray(BARGE.tri_mat) == BARGE.materials.index(bb.M_DECK)
        flat = np.abs(TRI.mean(axis=1)[:, 1]) < 0.01
        n = np.cross(TRI[:, 1] - TRI[:, 0], TRI[:, 2] - TRI[:, 0])
        self.assertTrue(np.all(n[deck & flat][:, 1] > 0.0))

    def test_nothing_gives_light(self) -> None:
        for mb in bb.build_barge():
            self.assertFalse(any("flame" in m or "ember" in m or "glow" in m for m in mb.materials), mb.materials)

    def test_the_rail_stays_under_the_cameras_rays(self) -> None:
        p = np.asarray(BARGE.pos)
        rail = p[(p[:, 1] > 0.05) & (p[:, 1] < bb.RAIL_H + 0.1) & (p[:, 2] > 2.5) & (np.abs(p[:, 0]) < 4.5)]
        for sx, sz in SLOTS_XZ:
            foot = np.array([sx, 0.0, sz])
            for r in rail:
                t = (r[2] - foot[2]) / (CAMERA[2] - foot[2])
                if 0.0 < t < 1.0:
                    ray_y = foot[1] + t * (CAMERA[1] - foot[1])
                    ray_x = foot[0] + t * (CAMERA[0] - foot[0])
                    if abs(ray_x - r[0]) < 0.1:
                        self.assertLess(float(r[1]), ray_y, (sx, sz))

    def test_inside_budget(self) -> None:
        lod0, lod1 = bb.build_barge()
        self.assertLessEqual(lod0.triangle_count, bb.TRI_BUDGET["bridal_barge"][0])
        self.assertLessEqual(lod1.triangle_count, bb.TRI_BUDGET["bridal_barge"][1])


if __name__ == "__main__":
    unittest.main()
