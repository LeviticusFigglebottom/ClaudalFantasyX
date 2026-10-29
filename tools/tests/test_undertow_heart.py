"""Tests for the Heart of the Undertow and Sefir's arenas (M3-ENV-728; undertow_layers.md §3).

* Every piece is inside its budget.
* The floor of held light is flat at y 0 (+-0.05) within 1 m of every battle slot; the eyewall faces the heart.
* Imra's column stands behind the enemy line, clear of the slots; the held state lights it cyan, the Letting warm.
"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import arena_scenes as ar  # noqa: E402
import undertow_heart as uh  # noqa: E402
import undertow_layers as ul  # noqa: E402


def _tris(mb):
    p, t = np.asarray(mb.pos), np.asarray(mb.tris)
    tri = p[t]
    return tri, np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), tri.mean(axis=1)


class UndertowHeartTests(unittest.TestCase):
    def test_inside_budget(self) -> None:
        for name, fn in uh.TARGETS.items():
            with self.subTest(piece=name):
                lod0, lod1 = fn()
                b0, b1 = uh.TRI_BUDGET[name]
                self.assertLessEqual(lod0.triangle_count, b0)
                self.assertLessEqual(lod1.triangle_count, b1)

    def test_the_floor_is_flat_round_the_slots(self) -> None:
        tri, n, c = _tris(uh.build_floor()[0])
        up = n[:, 1] > 0.9 * np.linalg.norm(n, axis=1)
        for sx, sz in ul.SLOTS_XZ:
            with self.subTest(slot=(sx, sz)):
                near = up & (np.hypot(c[:, 0] - sx, c[:, 2] - sz) < 1.0)
                self.assertGreater(int(near.sum()), 0)
                self.assertLess(abs(float(tri[near][..., 1].max())), 0.05)

    def test_the_eyewall_faces_the_heart(self) -> None:
        mb = uh.build_eyewall()[0]
        _, n, c = _tris(mb)
        wall = np.asarray(mb.tri_mat) == mb.materials.index(uh.M_DARK)
        self.assertTrue(bool(((c[wall][:, 0] * n[wall][:, 0] + c[wall][:, 2] * n[wall][:, 2]) < 0).all()))

    def test_the_column_stands_behind_the_enemy_line(self) -> None:
        cx, cz = uh.COLUMN_AT
        self.assertLess(cx, 0.0)
        self.assertGreater(math.hypot(cx, cz), uh.FLOOR_R)  # out in the water, past the floor's rim
        for sx, sz in ul.SLOTS_XZ:
            self.assertGreater(math.hypot(cx - sx, cz - sz), 4.0)
        self.assertEqual(ar.ARENAS["undertow_heart"]["lamp_spec"]["color"], "#7FC6D9")
        letting = ar.ARENAS["undertow_heart_letting"]
        self.assertEqual(letting["lamp_spec"]["color"], "#FFE9B8")
        self.assertEqual(letting["sun"]["color"], "#FFDCBF")
        self.assertTrue(letting["lut"].endswith("lut_ch21_heart.png"))


if __name__ == "__main__":
    unittest.main()
