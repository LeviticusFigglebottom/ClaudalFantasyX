"""Tests for Ossa Fen's root-walks and Reedhollow's reed walks (M3-ENV-733; ossa_fen.md §1).

* Every piece is inside its budget.
* The walk strips and the platform are level at y 0 over their walking width (act1-chapters' greybox: 3.6 m strips,
  their tops at y 0), with the rails 0.5 m high outside it.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import reedhollow as rh  # noqa: E402


class ReedhollowTests(unittest.TestCase):
    def test_inside_budget(self) -> None:
        for name, fn in rh.TARGETS.items():
            with self.subTest(piece=name):
                lod0, lod1 = fn()
                b0, b1 = rh.TRI_BUDGET[name]
                self.assertLessEqual(lod0.triangle_count, b0)
                self.assertLessEqual(lod1.triangle_count, b1)

    def test_the_walking_tops_are_level_at_zero(self) -> None:
        for name in ("root_walk_6m", "reed_causeway_6m", "reed_platform_6m"):
            mb = rh.TARGETS[name]()[0]  # LOD0: the near mesh the party walks over
            with self.subTest(piece=name):
                p = np.asarray(mb.pos)
                band = (np.abs(p[:, 2]) < rh.HALF_W - 0.3) & (np.abs(p[:, 0]) < 2.5)
                self.assertLess(abs(float(p[band][:, 1].max())), 0.03)

    def test_the_strip_rails_stand_outside_the_walk(self) -> None:
        for name in ("root_walk_6m", "reed_causeway_6m"):
            p = np.asarray(rh.TARGETS[name]()[0].pos)
            high = p[p[:, 1] > 0.3]
            with self.subTest(piece=name):
                self.assertGreater(float(np.abs(high[:, 2]).min()), rh.HALF_W - 0.05)
                self.assertGreater(float(high[:, 1].max()), rh.RAIL_H - 0.1)


if __name__ == "__main__":
    unittest.main()
