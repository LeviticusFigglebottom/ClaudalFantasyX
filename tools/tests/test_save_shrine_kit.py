"""Tests for the save shrine's kit pieces (M3-ENV-101): they fit the save shrine's current Visual.

* The body stays inside the primitives' footprint (r 1.05, 2.9 m) and the Body collider still holds it.
* The core piece is centred on its origin, to sit at Visual/Core (y 1.92) where the GlimmerField holds, and it
  carries the bound light under salt-glass.
* The body leaves room for the core: nothing of it inside the core's radius, and the niche is open toward +Z.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "environments" / "kits" / "haluna"
sys.path.insert(0, str(SRC))

import save_shrine  # noqa: E402

SCENE = ROOT / "game" / "world" / "save_shrine" / "save_shrine.tscn"


class SaveShrineKitTests(unittest.TestCase):
    def test_the_body_fits_the_primitives_footprint(self) -> None:
        for mb in save_shrine.build_shrine():
            lo, hi = mb.bounds()
            self.assertLessEqual(float(np.max(np.hypot(np.asarray(mb.pos)[:, 0], np.asarray(mb.pos)[:, 2]))), 1.05)
            self.assertGreaterEqual(float(lo[1]), -0.001)
            self.assertLessEqual(float(hi[1]), 2.9)

    def test_the_core_sits_where_visual_core_is(self) -> None:
        self.assertIn("transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.92, 0)", SCENE.read_text())
        self.assertAlmostEqual(save_shrine.CORE_Y, 1.92)
        for mb in save_shrine.build_core():
            lo, hi = mb.bounds()
            np.testing.assert_allclose((lo + hi) * 0.5, 0.0, atol=0.01)
            self.assertEqual(sorted(mb.materials), ["kit_bound_core", "kit_salt_glass"])

    def test_nothing_of_the_body_inside_the_core(self) -> None:
        p = np.asarray(save_shrine.build_shrine()[0].pos) - np.array([0.0, save_shrine.CORE_Y, 0.0])
        self.assertGreater(float(np.linalg.norm(p, axis=1).min()), save_shrine.CORE_R)

    def test_the_niche_opens_toward_plus_z(self) -> None:
        mb = save_shrine.build_shrine()[0]
        p = np.asarray(mb.pos)
        nacre = mb.materials.index(save_shrine.M_NACRE)
        tris = np.asarray(mb.tris)[np.asarray(mb.tri_mat) == nacre]
        self.assertLess(float(p[tris.reshape(-1), 2].max()), 0.05, "the shell's inside faces the front")

    def test_inside_budget(self) -> None:
        for name, fn in save_shrine.TARGETS.items():
            lod0, lod1 = fn()
            with self.subTest(piece=name):
                self.assertLessEqual(lod0.triangle_count, save_shrine.TRI_BUDGET[name][0])
                self.assertLessEqual(lod1.triangle_count, save_shrine.TRI_BUDGET[name][1])


if __name__ == "__main__":
    unittest.main()
