"""Tests for the Kite (M3-ENV-725; kite.md).

* Every piece is inside its budget; the planking faces out and the deck up.
* The bound lights (the engine's core, the lanterns) share kit_bound_core, so H09 darkens them with one swap.
* The hull is Dace's: the same length as the frame in Ch17.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import hollowmere  # noqa: E402
import kite  # noqa: E402


class KiteTests(unittest.TestCase):
    def test_inside_budget(self) -> None:
        for name, fn in kite.TARGETS.items():
            with self.subTest(piece=name):
                lod0, lod1 = fn()
                b0, b1 = kite.TRI_BUDGET[name]
                self.assertLessEqual(lod0.triangle_count, b0)
                self.assertLessEqual(lod1.triangle_count, b1)

    def test_the_planking_faces_out_and_the_deck_up(self) -> None:
        mb = kite.build_hull()[0]
        p, t = np.asarray(mb.pos), np.asarray(mb.tris)
        tri = p[t]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        c = tri.mean(axis=1)
        wood = np.asarray(mb.tri_mat) == mb.materials.index(kite.M_TIMBER)
        ok = np.linalg.norm(n, axis=1) > 1e-7
        skin = wood & ok & (c[:, 1] < -0.3) & (np.abs(c[:, 0]) < 5.0) & (np.abs(c[:, 2]) > 0.3)
        self.assertGreater(float(((c[:, 2] * n[:, 2]) > 0)[skin].mean()), 0.97)
        deck = wood & ok & (np.abs(c[:, 1]) < 1e-3)
        self.assertGreater(float((n[deck, 1] > 0).mean()), 0.99)

    def test_the_bound_lights_share_one_material(self) -> None:
        self.assertIn(kite.M_CORE, kite.build_engine()[0].materials)
        self.assertIn(kite.M_CORE, kite.build_hull()[0].materials)

    def test_the_hull_is_daces(self) -> None:
        lo, hi = kite.build_hull()[0].bounds()
        frame_lo, frame_hi = hollowmere.build_dace_hull()[0].bounds()
        self.assertAlmostEqual(float(hi[0] - lo[0]), hollowmere.DACE_LEN + 1.5, delta=0.6)
        self.assertLess(abs(float(hi[2]) - hollowmere.DACE_HALF_BEAM), 0.2)


if __name__ == "__main__":
    unittest.main()
