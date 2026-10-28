"""Tests for Hollowmere's pieces and grade (M3-ENV-723; hollowmere.md).

* Every piece is inside its budget and its LOD1 far under LOD0; the hulls' outer faces point out.
* Dace's hull is unfinished: strakes on the near (-Z) side only.
* The signal lamp carries the bound light; the grade's LUT holds its highlights under 0.92.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "environments" / "kits" / "haluna"
sys.path.insert(0, str(SRC))

import hollowmere  # noqa: E402
import zone_lut  # noqa: E402


class HollowmereTests(unittest.TestCase):
    def test_inside_budget(self) -> None:
        for name, fn in hollowmere.TARGETS.items():
            with self.subTest(piece=name):
                lod0, lod1 = fn()
                b0, b1 = hollowmere.TRI_BUDGET[name]
                self.assertLessEqual(lod0.triangle_count, b0)
                self.assertLessEqual(lod1.triangle_count, b1)

    def test_the_hulls_face_out(self) -> None:
        mb = hollowmere.build_lashed_hulls()[0]
        p, t = np.asarray(mb.pos), np.asarray(mb.tris)
        sel = np.asarray(mb.tri_mat) == mb.materials.index(hollowmere.M_DRIFT)
        tri = p[t[sel]]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        c = tri.mean(axis=1)
        hull = (np.abs(np.abs(c[:, 2]) - hollowmere.HULL_GAP) < hollowmere.HULL_HALF_BEAM + 0.1) & (c[:, 1] < 0.6)
        cz = np.where(c[:, 2] < 0.0, -hollowmere.HULL_GAP, hollowmere.HULL_GAP)
        side = np.abs(n[:, 2]) > np.abs(n[:, 1])
        out = (c[:, 2] - cz) * n[:, 2] > 0.0
        self.assertGreater(float(out[hull & side].mean()), 0.95)

    def test_dace_hull_is_planked_on_one_side_only(self) -> None:
        mb = hollowmere.build_dace_hull()[0]
        p, t = np.asarray(mb.pos), np.asarray(mb.tris)
        c = p[t].mean(axis=1)
        planks = (c[:, 1] > hollowmere.KEEL_Y + 0.1) & (c[:, 1] < hollowmere.SHEER_Y) & (np.abs(c[:, 0]) < 5.0)
        near = planks & (c[:, 2] < -0.8) & (c[:, 2] > -2.2)
        far = planks & (c[:, 2] > 0.8) & (c[:, 2] < 2.2)
        self.assertGreater(int(near.sum()) - int(far.sum()), 300, "the ribs are symmetric; the strakes are not")

    def test_the_signal_lamp_is_bound_light(self) -> None:
        self.assertIn(hollowmere.M_CORE, hollowmere.build_signal_lamp()[0].materials)

    def test_the_act3_grade_holds_its_highlights(self) -> None:
        lut = zone_lut.table(False, "act3_dusk")
        self.assertLessEqual(float(lut.max()), 0.92 * 255 + 1)


if __name__ == "__main__":
    unittest.main()
