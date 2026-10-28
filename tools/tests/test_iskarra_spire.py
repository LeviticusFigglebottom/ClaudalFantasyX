"""Tests for the Iskarra Lamp Spire's crown and its arena (M3-ENV-726; iskarra.md §3).

* Every piece is inside its budget.
* The crown floor is flat at y 0 (+-0.05) within 1 m of every battle slot, and the engine stands behind the enemy
  line, clear of the slots.
* The arena sets the drowned city 112 m below and lights the engine's teal.
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
import iskarra_spire as sp  # noqa: E402

SLOTS_XZ = ((2.1, 0.7), (3.0, -1.1), (1.4, 2.0), (-2.4, 0.9), (-3.4, -1.2), (-1.2, -0.6))


class IskarraSpireTests(unittest.TestCase):
    def test_inside_budget(self) -> None:
        for name, fn in sp.TARGETS.items():
            with self.subTest(piece=name):
                lod0, lod1 = fn()
                b0, b1 = sp.TRI_BUDGET[name]
                self.assertLessEqual(lod0.triangle_count, b0)
                self.assertLessEqual(lod1.triangle_count, b1)

    def test_the_floor_is_flat_round_the_slots(self) -> None:
        mb = sp.build_crown_floor()[0]
        p, t = np.asarray(mb.pos), np.asarray(mb.tris)
        tri = p[t]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        c = tri.mean(axis=1)
        up = n[:, 1] > 0.9 * np.linalg.norm(n, axis=1)
        for sx, sz in SLOTS_XZ:
            with self.subTest(slot=(sx, sz)):
                near = up & (np.hypot(c[:, 0] - sx, c[:, 2] - sz) < 1.0)
                self.assertGreater(int(near.sum()), 0)
                top = tri[near][..., 1].max()
                self.assertLess(abs(float(top)), 0.05)

    def test_the_engine_stands_behind_the_enemy_line(self) -> None:
        ex, ez = sp.ENGINE_AT
        for sx, sz in SLOTS_XZ:
            self.assertGreater(float(np.hypot(ex - sx, ez - sz)), 4.0)
        self.assertLess(ex, min(x for x, _ in SLOTS_XZ))

    def test_the_arena_sets_the_city_below_and_lights_the_engine(self) -> None:
        a = ar.ARENAS["iskarra_spire_crown"]
        self.assertAlmostEqual(a["sea"]["y"], -sp.ELEVATION_M)
        glb, at = a["extra_glbs"][0]
        self.assertTrue(glb.endswith("iskarra_far_towers.glb"))
        self.assertAlmostEqual(at[1], -sp.ELEVATION_M)
        self.assertEqual(a["lamp_spec"]["color"], "#4FB3B0")


    def test_the_engines_shadow_misses_the_slots(self) -> None:
        """The 2 deg afterglow behind the party: the anchor-engine's long shadow runs away from every battle slot (it
        lay across the enemy line with the light behind them)."""
        a = ar.ARENAS["iskarra_spire_crown"]
        az = math.radians(a["sun"]["az"])
        to_sun = np.array([math.sin(az), -math.cos(az)])
        ex, ez = sp.ENGINE_AT
        for sx, sz in SLOTS_XZ:
            with self.subTest(slot=(sx, sz)):
                v = np.array([sx - ex, sz - ez])
                self.assertGreater(float(v @ to_sun), 0.0)  # the slot is on the engine's sunward side

if __name__ == "__main__":
    unittest.main()
