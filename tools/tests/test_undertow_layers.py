"""Tests for the Undertow's layers and the Cage's arena (M3-ENV-727; undertow_layers.md).

* Every piece is inside its budget.
* The island's floor is flat at y 0 (+-0.05) within 1 m of every battle slot; the held pillars stand behind the enemy
  line, clear of the slots; the arena lights them cyan.
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
import undertow_layers as ul  # noqa: E402


class UndertowLayersTests(unittest.TestCase):
    def test_inside_budget(self) -> None:
        for name, fn in ul.TARGETS.items():
            with self.subTest(piece=name):
                lod0, lod1 = fn()
                b0, b1 = ul.TRI_BUDGET[name]
                self.assertLessEqual(lod0.triangle_count, b0)
                self.assertLessEqual(lod1.triangle_count, b1)

    def test_the_floor_is_flat_round_the_slots(self) -> None:
        mb = ul.build_island()[0]
        p, t = np.asarray(mb.pos), np.asarray(mb.tris)
        tri = p[t]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        c = tri.mean(axis=1)
        up = n[:, 1] > 0.9 * np.linalg.norm(n, axis=1)
        for sx, sz in ul.SLOTS_XZ:
            with self.subTest(slot=(sx, sz)):
                near = up & (np.hypot(c[:, 0] - sx, c[:, 2] - sz) < 1.0)
                self.assertGreater(int(near.sum()), 0)
                self.assertLess(abs(float(tri[near][..., 1].max())), 0.05)

    def test_the_pillars_stand_behind_the_enemy_line(self) -> None:
        for px, pz in ar.HELD_PILLARS:
            self.assertLess(px, 0.0)
            for sx, sz in ul.SLOTS_XZ:
                self.assertGreater(math.hypot(px - sx, pz - sz), 4.0)
        a = ar.ARENAS["undertow_cage"]
        self.assertEqual(a["lamp_spec"]["color"], "#7FC6D9")
        self.assertEqual(len(a["lamps"]), len(ar.HELD_PILLARS))


if __name__ == "__main__":
    unittest.main()
