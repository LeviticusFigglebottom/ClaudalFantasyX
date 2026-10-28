"""Tests for Lowlight's engine hall (M3-ENV-716; lowlight.md §2): the Lamp Engine's arena keeps the battle contract.

* The dais's top is flat at y 0 over every slot's metre (docs/kb/tech/battle_arenas.md), and the hall's water lies
  just under it, over the flooded floor.
* The boss anchor stands off the dais, in the water, on the enemy side.
* Six metres clear above the slots (the vault), and the fallen bay's rubble behind the enemy line.
* Every piece is inside its budget, and nothing is frozen (ADR 0015/0016).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "environments" / "kits" / "haluna"
sys.path.insert(0, str(SRC))

import lowlight  # noqa: E402

SLOTS_XZ = ((2.1, 0.7), (3.0, -1.1), (1.4, 2.0), (-2.4, 0.9), (-3.4, -1.2), (-1.2, -0.6))
HALL = lowlight.build_hall()[0]
POS, TRIS = np.asarray(HALL.pos), np.asarray(HALL.tris)
TRI = POS[TRIS]


def _covering(x: float, z: float) -> np.ndarray:
    """The tops of the triangles whose XZ bounds cover (x, z)."""
    lo, hi = TRI.min(axis=1), TRI.max(axis=1)
    m = (lo[:, 0] <= x) & (hi[:, 0] >= x) & (lo[:, 2] <= z) & (hi[:, 2] >= z)
    return hi[m, 1]


class EngineHallTests(unittest.TestCase):
    def test_the_floor_is_flat_at_zero_over_every_slots_metre(self) -> None:
        for sx, sz in SLOTS_XZ:
            for dx, dz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                with self.subTest(slot=(sx, sz), off=(dx, dz)):
                    tops = _covering(sx + dx, sz + dz)
                    floor = tops[tops < 1.0]
                    self.assertAlmostEqual(float(floor.max()), 0.0, delta=0.05)

    def test_the_water_lies_between_the_flooded_floor_and_the_dais(self) -> None:
        self.assertLess(lowlight.FLOOR_Y, lowlight.WATER_Y)
        self.assertLess(lowlight.WATER_Y, 0.0)
        for _grow, top in lowlight.DAIS_STEPS:
            self.assertLess(top, 0.0)

    def test_the_engine_stands_in_the_water_off_the_dais(self) -> None:
        x, y, z = lowlight.ENGINE_AT
        x0, x1, z0, z1 = lowlight.DAIS
        grow = max(g for g, _t in lowlight.DAIS_STEPS)
        self.assertLess(x, x0 - grow, "past the enemy side's steps")
        self.assertTrue(z0 <= z <= z1)
        self.assertLess(y, lowlight.WATER_Y, "knee-deep")
        tops = _covering(x, z)
        self.assertAlmostEqual(float(tops[tops < 1.0].max()), lowlight.FLOOR_Y, delta=0.05)

    def test_six_metres_clear_over_the_slots(self) -> None:
        lo, hi = TRI.min(axis=1), TRI.max(axis=1)
        for sx, sz in SLOTS_XZ:
            with self.subTest(slot=(sx, sz)):
                m = (lo[:, 0] <= sx) & (hi[:, 0] >= sx) & (lo[:, 2] <= sz) & (hi[:, 2] >= sz) & (lo[:, 1] > 0.1)
                self.assertTrue(m.any(), "the vault over the slot")
                self.assertGreaterEqual(float(lo[m, 1].min()), 6.0)

    def test_the_fallen_bay_and_its_rubble_lie_behind_the_enemy_line(self) -> None:
        x0, x1, z0, z1 = lowlight.FALLEN_BAY
        self.assertLess(z1, min(z for _x, z in SLOTS_XZ) - 3.0)
        rubble = TRI.mean(axis=1)
        low = rubble[(rubble[:, 1] > lowlight.FLOOR_Y) & (rubble[:, 1] < 1.0) & (rubble[:, 2] < z1 + 0.5)
                     & (np.abs(rubble[:, 0]) < lowlight.HALL_HALF - 1.0)]
        self.assertGreater(len(low), 0)

    def test_every_piece_is_inside_its_budget(self) -> None:
        for name, fn in lowlight.TARGETS.items():
            lod0, lod1 = fn()
            budget = lowlight.TRI_BUDGET[lowlight.BUDGET_KEY.get(name, name)]
            with self.subTest(piece=name):
                self.assertLessEqual(lod0.triangle_count, budget[0])
                self.assertLessEqual(lod1.triangle_count, budget[1])
                self.assertLess(lod1.triangle_count, lod0.triangle_count)

    def test_nothing_is_frozen(self) -> None:
        for name, fn in lowlight.TARGETS.items():
            for slot in fn()[0].materials:
                self.assertNotRegex(slot, "ice|frost|snow|frozen")


    def test_the_gallery_walk_is_level_with_its_rails_outside(self) -> None:
        """M3-ENV-735: the Sunken Vey's gallery walk matches act1-chapters' greybox (3.6 m, top at y 0, rails 0.5 m
        at z +-2.0)."""
        p = np.asarray(lowlight.TARGETS["vey_gallery_walk_6m"]()[0].pos)
        band = (np.abs(p[:, 2]) < lowlight.WALK_HALF_W - 0.3) & (np.abs(p[:, 0]) < 2.5)
        self.assertLess(abs(float(p[band][:, 1].max())), 0.03)
        high = p[p[:, 1] > 0.3]
        self.assertGreater(float(np.abs(high[:, 2]).min()), lowlight.WALK_HALF_W - 0.05)
        self.assertAlmostEqual(float(high[:, 1].max()), lowlight.WALK_RAIL_H, delta=0.05)

if __name__ == "__main__":
    unittest.main()
