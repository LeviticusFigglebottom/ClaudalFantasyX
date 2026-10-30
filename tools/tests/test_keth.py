"""Tests for the Keth Pass, Quellan and Cloudloom kit (M3-ENV-717, M3-ENV-734; keth_pass.md).

* Every piece is inside its budget.
* The Quellan inn's door is open (no wall block across it) and its banner hangs over the door, clear of heads.
* Hesk's dais tops out at the greybox's 0.4 m.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import keth  # noqa: E402


class KethTests(unittest.TestCase):
    def test_inside_budget(self) -> None:
        for name, fn in keth.TARGETS.items():
            with self.subTest(piece=name):
                lod0, lod1 = fn()
                b0, b1 = keth.TRI_BUDGET[name]
                self.assertLessEqual(lod0.triangle_count, b0)
                self.assertLessEqual(lod1.triangle_count, b1)

    def test_the_inn_door_is_open_and_the_banner_clears_it(self) -> None:
        mb = keth.TARGETS["quellan_inn"]()[0]
        p = np.asarray(mb.pos)
        wall = mb.materials.index(keth.M_DRYSTONE)  # the inn's walls are dry stone (M4-A2P-042)
        t = np.asarray(mb.tris)[np.asarray(mb.tri_mat) == wall]
        c = p[t].mean(axis=1)
        in_door = (np.abs(c[:, 0]) < 0.5) & (c[:, 1] < 2.2) & (c[:, 1] > 0.2) & (np.abs(c[:, 2]) < 0.3)
        self.assertFalse(bool(in_door.any()))
        red = mb.materials.index(keth.M_RED)
        banner = p[np.asarray(mb.tris)[np.asarray(mb.tri_mat) == red]]
        self.assertGreater(float(banner[..., 1].min()), 2.2)

    def test_the_dais_is_the_greybox_height(self) -> None:
        p = np.asarray(keth.TARGETS["hesk_dais"]()[0].pos)
        step = p[np.abs(p[:, 0]) > 1.0]  # off the seat
        self.assertAlmostEqual(float(step[:, 1].max()), 0.43, delta=0.05)


if __name__ == "__main__":
    unittest.main()
