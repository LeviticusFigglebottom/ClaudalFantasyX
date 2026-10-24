"""Tests for the battle arena kit (M2-ENV-11). Run: python3 -m unittest discover -s tools/tests

* The fighting floor under every battle sandbox slot is flat at y = 0 in both arena grounds (the
  Godot test re-checks it on the scenes, against the slots read from battle_sandbox.tscn).
* The disc is centred on its origin (a standalone kit piece the causeway field zone places too).
* arena_scenes.py reproduces the committed arena scenes byte for byte.
* zone_lut.py: the noon grade is unchanged by the new grades; the sunset grade is magenta-free.
"""

from __future__ import annotations

import colorsys
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "environments" / "kits" / "haluna"
sys.path.insert(0, str(SRC))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"arena_kit_{name}", SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


ARENAS = _load("arenas")


class ArenaFloorTests(unittest.TestCase):
    def _assert_floor(self, builder, offset=(0.0, 0.0)) -> None:
        for x, z in ARENAS.SLOTS_XZ:
            pos = np.asarray(builder.pos)
            nrm = np.asarray(builder.nrm)
            near = (np.hypot(pos[:, 0] - (x - offset[0]), pos[:, 2] - (z - offset[1])) < ARENAS.FLOOR_CLEAR_M)
            ys = pos[near & (nrm[:, 1] > 0.9), 1]
            with self.subTest(slot=(x, z)):
                self.assertGreater(len(ys), 0)
                self.assertLessEqual(ys.max(), ARENAS.FLOOR_Y + ARENAS.FLOOR_TOLERANCE_M, "nothing pokes up")
                # Paving joints show the bed below; most of the floor is the floor.
                share = np.mean(np.abs(ys - ARENAS.FLOOR_Y) <= ARENAS.FLOOR_TOLERANCE_M)
                self.assertGreaterEqual(share, 0.6)

    def test_beach_floor_is_flat_under_every_slot(self) -> None:
        self._assert_floor(ARENAS.build_tideline_ground()[0])

    def test_disc_floor_is_flat_under_every_slot(self) -> None:
        self._assert_floor(ARENAS.build_causeway_disc()[0], ARENAS.DISC_CENTER)

    def test_disc_is_a_centred_kit_piece(self) -> None:
        lo, hi = ARENAS.build_causeway_disc()[0].bounds()
        self.assertAlmostEqual(float(lo[0] + hi[0]), 0.0, delta=0.3)
        self.assertAlmostEqual(float(lo[2] + hi[2]), 0.0, delta=0.3)
        self.assertLessEqual(float(hi[1]), ARENAS.FLOOR_Y + ARENAS.FLOOR_TOLERANCE_M)
        self.assertLess(float(lo[1]), ARENAS.POOL_FLOOR_Y)

    def test_generators_are_deterministic(self) -> None:
        for name in ("arena_causeway_arms", "causeway_disc"):
            with self.subTest(target=name):
                a, b = ARENAS.TARGETS[name](), ARENAS.TARGETS[name]()
                for x, y in zip(a, b):
                    np.testing.assert_array_equal(np.asarray(x.pos), np.asarray(y.pos))


class ArenaSceneTests(unittest.TestCase):
    def test_scenes_are_reproducible(self) -> None:
        scenes = _load("arena_scenes")
        with tempfile.TemporaryDirectory() as tmp:
            scenes.OUT_DIR = Path(tmp)
            for aid, arena in scenes.ARENAS.items():
                with self.subTest(arena=aid):
                    out = scenes.write_arena(arena)
                    committed = ROOT / "assets" / "environments" / "arenas" / aid / f"{aid}.tscn"
                    self.assertEqual(committed.read_text(encoding="utf-8"), out.read_text(encoding="utf-8"))

    def test_no_prop_stands_on_the_fighting_floor(self) -> None:
        scenes = _load("arena_scenes")
        for aid, arena in scenes.ARENAS.items():
            for glb, x, z, *_rest in arena["pieces"]:
                for sx, sz in ARENAS.SLOTS_XZ:
                    with self.subTest(arena=aid, piece=Path(glb).stem, at=(x, z)):
                        self.assertGreater(np.hypot(x - sx, z - sz), 4.0)


class ZoneLutTests(unittest.TestCase):
    def test_noon_grade_is_unchanged(self) -> None:
        lut = _load("zone_lut")
        self.assertEqual(lut.GRADES["ch02_noon"]["saturation"], lut.SATURATION)
        a = lut.table(False)
        b = lut.table(False, "ch02_noon")
        np.testing.assert_array_equal(a, b)

    def test_sunset_grade_is_magenta_free(self) -> None:
        lut = _load("zone_lut")
        pinks = np.array([colorsys.hsv_to_rgb(h / 360.0, 0.6, 0.8) for h in (300.0, 315.0, 330.0)])
        graded = lut.grade(pinks, lut.GRADES["ch03_sunset"])
        plain = lut.grade(pinks, dict(lut.GRADES["ch03_sunset"], magenta_clip=0.0))
        for g, p in zip(graded, plain):
            sat_g = colorsys.rgb_to_hsv(*g)[1]
            sat_p = colorsys.rgb_to_hsv(*p)[1]
            self.assertLess(sat_g, sat_p, "pink-magenta loses saturation")


if __name__ == "__main__":
    unittest.main()
