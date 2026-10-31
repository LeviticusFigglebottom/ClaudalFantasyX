"""Tests for the Undertow's layers and the Cage's arena (M3-ENV-727; undertow_layers.md).

* Every piece is inside its budget.
* The island's floor is flat at y 0 (+-0.05) within 1 m of every battle slot; the held pillars stand behind the enemy
  line, clear of the slots; the arena lights them cyan.
* M5-A3P-1400: act3_ch20's six layers each have their remembered room in the kit, and the arena hangs every room; the
  rooms' only light is held glimmer (no flame, no warm practical: the warm light is the Letting's).
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

    def test_every_layer_has_its_room(self) -> None:
        rooms = {"memory_market", "memory_terrace", "memory_kitchen", "memory_stands", "memory_gallery",
                 "memory_square"}  # U01..U06
        self.assertLessEqual(rooms, set(ul.TARGETS))
        hung = {Path(p["glb"]).stem for p in ar.ARENAS["undertow_cage"]["pieces"]}
        self.assertLessEqual(rooms, hung)

    def test_the_rooms_hold_only_held_light(self) -> None:
        for name in ("memory_terrace", "memory_gallery", "memory_square"):
            with self.subTest(piece=name):
                mb = ul.TARGETS[name]()[0]
                used = {mb.materials[m] for m in set(mb.tri_mat)}
                self.assertFalse({m for m in used if "flame" in m or "lamp_glass_lit" in m}, used)
        self.assertIn(ul.M_HELD, {ul.TARGETS["memory_terrace"]()[0].materials[m]
                                  for m in set(ul.TARGETS["memory_terrace"]()[0].tri_mat)})

    def test_the_rest_landing_is_flat_and_quiet(self) -> None:
        """M5-A3P-1402: the party stands on a flat floor round the landing's middle; one held lamp, no other light."""
        mb = ul.build_landing()[0]
        p, t = np.asarray(mb.pos), np.asarray(mb.tris)
        tri = p[t]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        c = tri.mean(axis=1)
        up = n[:, 1] > 0.9 * np.linalg.norm(n, axis=1)
        mid = up & (np.hypot(c[:, 0], c[:, 2]) < 1.5) & (c[:, 1] < 0.2)
        self.assertGreater(int(mid.sum()), 0)
        self.assertLess(abs(float(tri[mid][..., 1].max())), 0.05)
        used = {mb.materials[m] for m in set(mb.tri_mat)}
        self.assertIn(ul.M_HELD, used)
        self.assertFalse({m for m in used if "flame" in m or "lamp_glass_lit" in m})


if __name__ == "__main__":
    unittest.main()
