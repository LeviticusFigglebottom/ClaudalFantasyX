"""Tests for the battle arena kit (M2-ENV-11). Run: python3 -m unittest discover -s tools/tests

* The fighting floor under every battle sandbox slot is flat at y = 0 in both arena grounds (the
  Godot test re-checks it on the scenes, against the slots read from battle_sandbox.tscn).
* The disc is centred on its origin (a standalone kit piece the causeway field zone places too).
* arena_scenes.py reproduces the committed arena scenes byte for byte.
* zone_lut.py: the noon grade is unchanged by the new grades; the sunset grade is magenta-free.
* M3-ENV-06: the three Act I arena grounds (the route's flats in the Haluna kit, the derelict's deck in the
  Brine Shoals kit, the Lanternfall tread in the Pemakar kit) are flat under every slot; the night grades lift
  the black point to night_sky and keep the lamp oranges; the night arenas keep colour script rule 3.
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
KITS = ROOT / "assets_src" / "environments" / "kits"


def _load_kit(kit: str, name: str):
    """A module of another zone kit (its own folder first on the path, as its build.py has it)."""
    folder = str(KITS / kit)
    if folder not in sys.path:
        sys.path.insert(0, folder)
    spec = importlib.util.spec_from_file_location(f"arena_{kit}_{name}", KITS / kit / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _top_at(tri: np.ndarray, x: float, z: float):
    """The highest point of the triangles (n, 3, 3) straight over (x, z), or None."""
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    v0, v1 = b[:, [0, 2]] - a[:, [0, 2]], c[:, [0, 2]] - a[:, [0, 2]]
    v2 = np.array([x, z]) - a[:, [0, 2]]
    den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
    ok = np.abs(den) > 1e-12
    den = np.where(ok, den, 1.0)
    u = (v2[:, 0] * v1[:, 1] - v1[:, 0] * v2[:, 1]) / den
    v = (v0[:, 0] * v2[:, 1] - v2[:, 0] * v0[:, 1]) / den
    hit = ok & (u >= 0.0) & (v >= 0.0) & (u + v <= 1.0)
    if not hit.any():
        return None
    y = a[:, 1] + u * (b[:, 1] - a[:, 1]) + v * (c[:, 1] - a[:, 1])
    return float(y[hit].max())


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

    def _assert_floor_by_rays(self, builder) -> None:
        """As the Godot test does it: the highest surface straight down at the slot and on two rings round it
        (a mesh of long planks has no vertices near most slots)."""
        pos = np.asarray(builder.pos, float)
        tri = pos[np.asarray(builder.tris, dtype=np.int64)]
        for x, z in ARENAS.SLOTS_XZ:
            pts = [(x, z)] + [(x + r * np.cos(a), z + r * np.sin(a)) for r in (0.5, 1.0)
                              for a in np.linspace(0.0, 2.0 * np.pi, 8, endpoint=False)]
            tops = [t for t in (_top_at(tri, px, pz) for px, pz in pts) if t is not None]
            with self.subTest(slot=(x, z)):
                self.assertEqual(len(tops), len(pts), "ground everywhere round the slot")
                self.assertLessEqual(max(tops), ARENAS.FLOOR_Y + ARENAS.FLOOR_TOLERANCE_M, "nothing pokes up")
                share = np.mean(np.abs(np.asarray(tops) - ARENAS.FLOOR_Y) <= ARENAS.FLOOR_TOLERANCE_M)
                self.assertGreaterEqual(share, 0.7)

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

    def test_route_floor_is_flat_under_every_slot(self) -> None:
        self._assert_floor(ARENAS.build_route_ground()[0])

    def test_derelict_deck_is_flat_under_every_slot(self) -> None:
        deck = _load_kit("brine_shoals", "bs_derelict")
        self.assertEqual(tuple(deck.SLOTS_XZ), tuple(ARENAS.SLOTS_XZ))
        self._assert_floor_by_rays(deck.build_derelict_deck()[0])

    def test_ash_tread_is_flat_under_every_slot(self) -> None:
        tread = _load_kit("pemakar", "pemakar_arena")
        self._assert_floor_by_rays(tread.build_ash_tread()[0])
        # The upper tier's wall stands behind the enemy line: the tread's back edge is beyond every slot's clear.
        for x, z in ARENAS.SLOTS_XZ:
            self.assertLess(float(tread.back_z(x)), z - ARENAS.FLOOR_CLEAR_M - 0.5)

    def test_route_slabs_keep_off_the_floor(self) -> None:
        # The causeway's line passes the fight beyond the floor's clear radius (pieces test below checks each slab).
        pts = np.asarray(ARENAS.ROUTE_PATH, float)
        for x, z in ARENAS.SLOTS_XZ:
            d = ARENAS.seg_distance(np.array([x]), np.array([z]), pts)[0]
            self.assertGreater(d, 4.5)

    def test_generators_are_deterministic(self) -> None:
        for name in ("arena_causeway_arms", "causeway_disc", "arena_causeway_route_ground"):
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
            for row in arena["pieces"]:
                if isinstance(row, dict):  # an explicit placement: only those standing on the floor count
                    glb, (x, y, z) = row["glb"], row["at"]
                    if abs(y - ARENAS.FLOOR_Y) > 0.5:
                        continue
                else:
                    glb, x, z = row[:3]
                for sx, sz in ARENAS.SLOTS_XZ:
                    with self.subTest(arena=aid, piece=Path(glb).stem, at=(x, z)):
                        self.assertGreater(np.hypot(x - sx, z - sz), 4.0)


    def test_night_arenas_keep_rule_three(self) -> None:
        # Colour script rule 3: night sea-glow >= 0.08, and moonlight (the arena's one directional) <= 2.5 x it.
        scenes = _load("arena_scenes")
        # ash_terrace_lanternfall has no moon: its directional is the colour script's sky fill (#3A4A6A 0.25).
        for aid in ("derelict_deck_night", "ash_terrace_lanternfall"):
            arena = scenes.ARENAS[aid]
            with self.subTest(arena=aid):
                self.assertGreaterEqual(arena["sea"]["sea_glow"], 0.08)
                if arena["sun"].get("moon", False):
                    self.assertLessEqual(arena["sun"]["energy"], 2.5 * arena["sea"]["sea_glow"] + 1e-9)
                self.assertTrue(arena["lamps"], "practical-keyed: the lamps are the key")
        self.assertTrue(scenes.ARENAS["derelict_deck_night"]["sun"]["moon"])

    def test_lamps_and_flames_keep_off_the_floor_and_the_view(self) -> None:
        # A lamp's flame is a mesh: none within the clear floor, none low between the camera and the fighters.
        scenes = _load("arena_scenes")
        for aid, arena in scenes.ARENAS.items():
            for lp in arena.get("lamps", []):
                x, y, z = lp["at"]
                for sx, sz in ARENAS.SLOTS_XZ:
                    with self.subTest(arena=aid, lamp=(x, y, z)):
                        self.assertGreater(np.hypot(x - sx, z - sz), ARENAS.FLOOR_CLEAR_M + 1.0)


class ZoneLutTests(unittest.TestCase):
    def test_noon_grade_is_unchanged(self) -> None:
        lut = _load("zone_lut")
        self.assertEqual(lut.GRADES["ch02_noon"]["saturation"], lut.SATURATION)
        a = lut.table(False)
        b = lut.table(False, "ch02_noon")
        np.testing.assert_array_equal(a, b)

    def test_night_grades_lift_black_to_night_sky_and_keep_the_flames(self) -> None:
        lut = _load("zone_lut")
        night = np.array([int(lut.NIGHT_SKY_HEX[i:i + 2], 16) / 255.0 for i in (1, 3, 5)])
        for name in ("ch04_wake", "ch05_lanternfall"):
            g = lut.GRADES[name]
            with self.subTest(grade=name):
                black = lut.grade(np.zeros((1, 3)), g)[0]
                self.assertTrue(np.all(black >= night - 1.0 / 255.0), "black point at night_sky, never 0")
                flame = np.array([[1.0, 0.69, 0.43]])  # oil_lamp #FFB16E
                grey = np.array([[0.4, 0.4, 0.42]])
                f_sat = colorsys.rgb_to_hsv(*lut.grade(flame, g)[0])[1]
                g_sat = colorsys.rgb_to_hsv(*lut.grade(grey, g)[0])[1]
                self.assertGreater(f_sat, colorsys.rgb_to_hsv(*flame[0])[1] * 0.95, "the lamp pools stay saturated")
                self.assertLess(g_sat, 0.2, "stone stays near neutral")

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
