"""Tests for Ossa Fen (M3-ENV-718; ossa_fen.md §2): the Mangrove Drowner's arena keeps the battle contract.

* The bank's top is flat at y 0 over every slot's metre (docs/kb/tech/battle_arenas.md), and the water lies just
  under it; the surface roots stay off the slots' floor.
* The boss anchor stands in the water at the dead tree's foot, on the enemy side, and the dead tree's roots leave
  that side open.
* The trees keep the vegetation wind contract (roots never sway), the dead tree carries no leaves, and every piece is
  inside its budget.
"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "environments" / "kits" / "haluna"
sys.path.insert(0, str(SRC))

import kit_common as kc  # noqa: E402
import ossa_fen  # noqa: E402

SLOTS_XZ = ((2.1, 0.7), (3.0, -1.1), (1.4, 2.0), (-2.4, 0.9), (-3.4, -1.2), (-1.2, -0.6))
GROUND = ossa_fen.build_ground()[0]


class FenBankTests(unittest.TestCase):
    def test_the_bank_is_flat_at_zero_over_every_slots_metre(self) -> None:
        noise = kc.Noise3(kc.rng_for("fen_bank_ground", 1801))
        for sx, sz in SLOTS_XZ:
            for dx, dz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                with self.subTest(slot=(sx, sz), off=(dx, dz)):
                    h = float(ossa_fen.bank_height(np.array([sx + dx]), np.array([sz + dz]), noise)[0])
                    self.assertAlmostEqual(h, 0.0, delta=0.05)

    def test_no_surface_root_on_the_slots_floor(self) -> None:
        pos, tris = np.asarray(GROUND.pos), np.asarray(GROUND.tris)
        bark = GROUND.materials.index(ossa_fen.M_BARK)
        cen = pos[tris[np.asarray(GROUND.tri_mat) == bark]].mean(axis=1)
        for sx, sz in SLOTS_XZ:
            with self.subTest(slot=(sx, sz)):
                self.assertGreater(float(np.hypot(cen[:, 0] - sx, cen[:, 2] - sz).min()), 1.0)

    def test_the_water_lies_just_under_the_bank(self) -> None:
        self.assertLess(ossa_fen.WATER_Y, 0.0)
        self.assertGreater(ossa_fen.WATER_Y, -0.3)


class DrownerTests(unittest.TestCase):
    def test_the_anchor_is_in_the_water_on_the_enemy_side(self) -> None:
        x, y, z = ossa_fen.DROWNER_AT
        self.assertLess(x, min(sx for sx, _z in SLOTS_XZ) - 2.0)
        self.assertAlmostEqual(y, ossa_fen.WATER_Y)
        noise = kc.Noise3(kc.rng_for("fen_bank_ground", 1801))
        self.assertLess(float(ossa_fen.bank_height(np.array([x]), np.array([z]), noise)[0]), ossa_fen.WATER_Y)

    def test_the_dead_trees_roots_leave_the_drowners_side_open(self) -> None:
        dead = ossa_fen.build_dead()[0]
        p = np.asarray(dead.pos)
        low = p[p[:, 1] < 1.0]  # the roots' feet, in the dead tree's frame
        x, _y, z = ossa_fen.DROWNER_AT
        toward = np.array([x - ossa_fen.DEAD_AT[0], z - ossa_fen.DEAD_AT[1]])
        toward /= np.linalg.norm(toward)
        self.assertLess(float((low[:, [0, 2]] @ toward).max()), 1.0, "no root reaches toward the Drowner")

    def test_the_dead_tree_is_bare(self) -> None:
        for mb in ossa_fen.build_dead():
            self.assertEqual(mb.materials, [ossa_fen.M_BARK_DEAD])


class TreeTests(unittest.TestCase):
    def test_roots_never_sway_and_crowns_do(self) -> None:
        mb = ossa_fen.build_tree()[0]
        p, c = np.asarray(mb.pos), np.asarray(mb.col)
        self.assertTrue(np.all(c[p[:, 1] < 0.0, 0] == 0.0), "the prop-roots' feet in the mud")
        self.assertGreater(float(c[p[:, 1] > 7.0, 0].min()), 0.5, "the crown sways")

    def test_leaf_cards_sample_the_banyan_sprays(self) -> None:
        mb = ossa_fen.build_tree()[0]
        leaf = mb.materials.index(ossa_fen.M_LEAF)
        tris = np.asarray(mb.tris)[np.asarray(mb.tri_mat) == leaf]
        uv = np.asarray(mb.uv)[tris.reshape(-1)]
        self.assertLessEqual(float(uv[:, 1].max()), 0.5 + 1e-6, "inside the atlas's banyan spray cells")

    def test_every_piece_is_inside_its_budget(self) -> None:
        for name, fn in ossa_fen.TARGETS.items():
            lod0, lod1 = fn()
            with self.subTest(piece=name):
                self.assertLessEqual(lod0.triangle_count, ossa_fen.TRI_BUDGET[name][0])
                self.assertLessEqual(lod1.triangle_count, ossa_fen.TRI_BUDGET[name][1])
                self.assertLess(lod1.triangle_count, lod0.triangle_count)


if __name__ == "__main__":
    unittest.main()
