"""Tests for the battle arena kit (M2-ENV-11). Run: python3 -m unittest discover -s tools/tests

* The fighting floor under every battle sandbox slot is flat at y = 0 in both arena grounds (the
  Godot test re-checks it on the scenes, against the slots read from battle_sandbox.tscn).
* The disc is centred on its origin (a standalone kit piece the causeway field zone places too).
* arena_scenes.py reproduces the committed arena scenes byte for byte.
* zone_lut.py: the noon grade is unchanged by the new grades; the sunset grade is magenta-free.
* M3-ENV-06: the three Act I arena grounds (the route's flats in the Haluna kit, the derelict's deck in the
  Brine Shoals kit, the Lanternfall tread in the Pemakar kit) are flat under every slot; the night grades lift
  the black point to night_sky and keep the lamp oranges; the night arenas keep colour script rule 3.
* M3-ENV-06 (the Ch1 pair): the raft deck (Haluna kit) and the Underway gallery's F9 slabs (the Oruvel Underway
  kit's floor_slab where the arena places them) are flat under every slot; structure (walls, piers) keeps 2 m off
  the slots, props 4 m; the downwelling tint takes red first; lut_ch01_raft lifts the cyans and oranges only.
"""

from __future__ import annotations

import colorsys
import json
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_b_arenas import WRAPPED  # noqa: E402

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

    def _assert_floor_by_rays(self, builder, *, open_seams: bool = False) -> None:
        """As the Godot test does it: the highest surface straight down at the slot and on two rings round it
        (a mesh of long planks has no vertices near most slots). `open_seams`: a ray may fall through a plank seam
        into the sea (a raft has no hold under its deck), as the Godot test allows; most rays still hit."""
        pos = np.asarray(builder.pos, float)
        tri = pos[np.asarray(builder.tris, dtype=np.int64)]
        for x, z in ARENAS.SLOTS_XZ:
            pts = [(x, z)] + [(x + r * np.cos(a), z + r * np.sin(a)) for r in (0.5, 1.0)
                              for a in np.linspace(0.0, 2.0 * np.pi, 8, endpoint=False)]
            tops = [t for t in (_top_at(tri, px, pz) for px, pz in pts) if t is not None]
            with self.subTest(slot=(x, z)):
                if open_seams:
                    self.assertGreaterEqual(len(tops), 0.7 * len(pts), "deck round the slot")
                else:
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

    def test_raft_deck_is_flat_under_every_slot(self) -> None:
        self._assert_floor_by_rays(ARENAS.build_raft_deck()[0], open_seams=True)

    def test_underway_gallery_floor_is_flat_under_every_slot(self) -> None:
        # The gallery's floor is the kit's own F9 slabs where the arena places them (rows tagged "floor").
        scenes = _load("arena_scenes")
        tower = _load_kit("oruvel_underway", "ou_tower")
        slab = tower.build_slab()[0]
        pos = np.asarray(slab.pos, float)
        tris = np.asarray(slab.tris, dtype=np.int64)
        floors = [r for r in scenes.UNDERWAY_TOWER["pieces"] if isinstance(r, dict) and r.get("floor")]
        self.assertGreaterEqual(len(floors), 6)
        parts = []
        for r in floors:
            a = np.radians(r["yaw"])
            rot = np.array([[np.cos(a), 0.0, np.sin(a)], [0.0, 1.0, 0.0], [-np.sin(a), 0.0, np.cos(a)]])
            parts.append((pos @ rot.T + np.asarray(r["at"], float))[tris])
        tri = np.concatenate(parts)

        class _Tris:  # the shape _assert_floor_by_rays reads
            def __init__(self, t):
                self.pos = t.reshape(-1, 3)
                self.tris = np.arange(len(self.pos)).reshape(-1, 3)

        self._assert_floor_by_rays(_Tris(tri))

    def test_route_slabs_keep_off_the_floor(self) -> None:
        # The causeway's line passes the fight beyond the floor's clear radius (pieces test below checks each slab).
        pts = np.asarray(ARENAS.ROUTE_PATH, float)
        for x, z in ARENAS.SLOTS_XZ:
            d = ARENAS.seg_distance(np.array([x]), np.array([z]), pts)[0]
            self.assertGreater(d, 4.5)

    def test_generators_are_deterministic(self) -> None:
        for name in ("arena_causeway_arms", "causeway_disc", "arena_causeway_route_ground", "arena_raft_deck"):
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
                if aid in WRAPPED:  # env-art-b writes these through its wrappers; test_b_arenas.py reproduces them
                    continue
                with self.subTest(arena=aid):
                    out = scenes.write_arena(arena)
                    committed = ROOT / "assets" / "environments" / "arenas" / aid / f"{aid}.tscn"
                    self.assertEqual(committed.read_text(encoding="utf-8"), out.read_text(encoding="utf-8"))

    def test_no_prop_stands_on_the_fighting_floor(self) -> None:
        scenes = _load("arena_scenes")
        for aid, arena in scenes.ARENAS.items():
            for row in arena["pieces"]:
                clear = 4.0
                if isinstance(row, dict):  # an explicit placement: only those standing on the floor count
                    glb, (x, y, z) = row["glb"], row["at"]
                    if abs(y - ARENAS.FLOOR_Y) > 0.5 or row.get("floor", False):
                        continue  # (the floor's own tiles: the Underway's F9 slabs, checked above)
                    if row.get("structure", False):
                        clear = ARENAS.FLOOR_CLEAR_M + 1.0  # a building's wall or pier round the floor
                else:
                    glb, x, z = row[:3]
                for sx, sz in ARENAS.SLOTS_XZ:
                    with self.subTest(arena=aid, piece=Path(glb).stem, at=(x, z)):
                        self.assertGreater(np.hypot(x - sx, z - sz), clear)


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

    def test_ch1_arena_lights_keep_out_of_the_volumetric_fog(self) -> None:
        # The Lead's rule (dense FogVolumes: the rig's god rays): every OmniLight3D/SpotLight3D in the two Ch1 arenas
        # sets light_volumetric_fog_energy = 0 (the rig's own lantern takes 0 from underwater.json).
        for aid in ("oruvel_raft_morning", "underway_tower"):
            text = (ROOT / "assets" / "environments" / "arenas" / aid / f"{aid}.tscn").read_text(encoding="utf-8")
            for block in text.split("\n\n"):
                if 'type="OmniLight3D"' in block or 'type="SpotLight3D"' in block:
                    with self.subTest(arena=aid, light=block.splitlines()[0]):
                        self.assertIn("light_volumetric_fog_energy = 0", block)
        self.assertEqual(json.loads((ROOT / "game/data/vfx/underwater.json").read_text())["lantern"]["fog_energy"], 0.0)

    def test_lamps_and_flames_keep_off_the_floor_and_the_view(self) -> None:
        # A lamp's flame is a mesh: none within the clear floor, none low between the camera and the fighters.
        scenes = _load("arena_scenes")
        for aid, arena in scenes.ARENAS.items():
            for lp in arena.get("lamps", []):
                x, y, z = lp["at"]
                for sx, sz in ARENAS.SLOTS_XZ:
                    with self.subTest(arena=aid, lamp=(x, y, z)):
                        self.assertGreater(np.hypot(x - sx, z - sz), ARENAS.FLOOR_CLEAR_M + 1.0)


class UnderwayTests(unittest.TestCase):
    def test_downwelling_takes_red_first(self) -> None:
        scenes = _load("arena_scenes")
        key = scenes.water_tinted(scenes.CH01_KEY, scenes.UW_DEPTH_M)
        r, g, b = (int(key[i:i + 2], 16) for i in (1, 3, 5))
        self.assertLess(r, g)
        self.assertLess(r, b)
        self.assertEqual(scenes.water_tinted(scenes.CH01_KEY, 0.0), scenes.CH01_KEY)
        self.assertEqual(scenes.UNDERWAY_TOWER["sun"]["color"], key)

    def test_the_rig_sits_on_the_arena_sea_and_the_gallery_keeps_its_far_columns(self) -> None:
        scenes = _load("arena_scenes")
        uw = scenes.UNDERWAY_TOWER
        self.assertGreater(uw["sea"]["y"], 20.0, "the gallery is 22 m down")
        self.assertLess(uw["underwater"]["light_scale"], 1.0, "the in-scatter is scaled down indoors")
        columns = [r for r in uw["pieces"] if Path(r["glb"]).stem == "lamp_column" and abs(r["at"][1]) < 0.01]
        self.assertGreaterEqual(len(columns), 4)
        dropped = {Path(r["glb"]).stem for r in scenes.UW_DROPPED}
        self.assertIn("lamp_column", dropped, "the fight's bay has lost its columns")


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

    def test_ch01_raft_lifts_the_cyans_and_oranges_only(self) -> None:
        lut = _load("zone_lut")
        g = lut.GRADES["ch01_raft"]
        plain = dict(g)
        del plain["band_sat"]
        cols = np.array([colorsys.hsv_to_rgb(h / 360.0, 0.5, 0.7) for h in (30.0, 188.0, 110.0, 270.0)])
        cols = np.vstack([cols, [[0.5, 0.5, 0.5]]])
        a, b = lut.grade(cols, g), lut.grade(cols, plain)
        sat = [colorsys.rgb_to_hsv(*c)[1] for c in a]
        sat0 = [colorsys.rgb_to_hsv(*c)[1] for c in b]
        self.assertGreater(sat[0], sat0[0] * 1.03, "orange")
        self.assertGreater(sat[1], sat0[1] * 1.03, "cyan")
        for k in (2, 3):
            self.assertAlmostEqual(sat[k], sat0[k], places=3)
        np.testing.assert_allclose(a[4], b[4], atol=1e-6)

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
