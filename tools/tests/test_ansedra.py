"""Tests for Ansedra's pieces and the Warden's arena (M3-ENV-721; ansedra.md).

* The bowl-dome's plinth stands out of the water and its spire tops the dome; the skyline's domes are far (300 m+).
* The pursuit barge's bound flat-engine carries the bound light; its deck sits where the arena's BossAnchor stands.
* The lit skyline's windows face out.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import ansedra  # noqa: E402
import arena_scenes as ar  # noqa: E402


class AnsedraTests(unittest.TestCase):
    def test_the_dome_stands_on_its_island_and_its_spire_tops_it(self) -> None:
        lo, hi = ansedra.build_bowl_dome()[0].bounds()
        self.assertLess(float(lo[1]), 0.0, "the plinth goes into the water")
        self.assertGreater(float(hi[1]), 15.0)

    def test_the_skyline_is_far(self) -> None:
        p = np.asarray(ansedra.build_far_domes()[0].pos)
        self.assertGreater(float(np.hypot(p[:, 0], p[:, 2]).min()), 280.0)

    def test_the_lit_windows_face_out(self) -> None:
        import kit_common as kc

        mb = kc.MeshBuilder("t")
        ansedra._dome(mb, 0.0, 0.0, 1.0, False, np.random.default_rng(1), sides=12, windows=True)
        p, t = np.asarray(mb.pos), np.asarray(mb.tris)
        win = np.asarray(mb.tri_mat) == mb.materials.index(ansedra.M_WINDOW)
        tri = p[t[win]]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        c = tri.mean(axis=1)
        self.assertTrue(np.all(np.einsum("ij,ij->i", n[:, [0, 2]], c[:, [0, 2]]) > 0.0))

    def test_the_engine_is_bound_light(self) -> None:
        mb = ansedra.build_pursuit_barge()[0]
        self.assertIn(ansedra.M_CORE, mb.materials)

    def test_the_boss_anchor_is_on_the_pursuit_barges_deck(self) -> None:
        a = ar.ANSEDRA_ESCAPE
        x, y, z = a["anchors"]["BossAnchor"]
        px, pz = ar.PURSUIT_AT
        deck_y = -0.6 + ansedra.PURSUIT_DECK_Y
        self.assertAlmostEqual(y, deck_y, delta=0.05)
        self.assertLess(abs(z - pz), ansedra.PURSUIT_HALF_BEAM, "inside the beam")
        self.assertLess(abs(x - px), ansedra.PURSUIT_LEN * 0.5)

    def test_the_hall_roofs_face_up(self) -> None:
        for mb in ansedra.build_lacquer_hall():
            p, t = np.asarray(mb.pos), np.asarray(mb.tris)
            tile = np.asarray(mb.tri_mat) == mb.materials.index(ansedra.M_TILE)
            tri = p[t[tile]]
            n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
            area = np.linalg.norm(n, axis=1) > 1e-6
            self.assertTrue(np.all(n[area, 1] > 0.0), "every tile face points up")

    def test_the_basin_floor_is_under_its_still_water(self) -> None:
        lo, hi = ansedra.build_sanctum_basin()[0].bounds()
        self.assertAlmostEqual(float(hi[1]), 0.0, delta=0.02, msg="the rim's top is the floor level")
        self.assertLess(float(lo[1]), -ansedra.BASIN_DEPTH)

    def test_the_court_is_level_and_its_steps_reach_the_water(self) -> None:
        lo, hi = ansedra.build_court_ground()[0].bounds()
        self.assertLess(float(lo[1]), -1.2, "the steps go under the lagoon (-0.6)")
        self.assertGreater(float(hi[2]), ansedra.COURT[1] + 4.0, "the water-gate stands out past the steps")

    def test_inside_budget(self) -> None:
        for name, fn in ansedra.TARGETS.items():
            lod0, lod1 = fn()
            b = ansedra.TRI_BUDGET[ansedra.BUDGET_KEY.get(name, name)]
            with self.subTest(piece=name):
                self.assertLessEqual(lod0.triangle_count, b[0])
                self.assertLessEqual(lod1.triangle_count, b[1])


if __name__ == "__main__":
    unittest.main()
