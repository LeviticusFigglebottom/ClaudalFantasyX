"""Tests for the Coilspire temple procedural kit (M3-ENV-10). Run: python3 -m unittest discover -s tools/tests

* One building: the near spire stands where Corrow's skyline piece stands (Corrow's preview places the headland
  at cs_common.HEADLAND, and its beacon light is this layout's), on the same radius law, with the same flue coils
  and beacon cage as cw_far's `coilspire_headland`, on the same headland rock away from the path.
* Geometry (no Blender needed): every target is inside its budget with an authored LOD1 chain, the generators are
  deterministic, the weathering channels are in [0, 1], and every slot is a `cs_*` slot.
* The trial's plan: four tiers and a crown; landings leave the middle of the well open (the grate is visible from
  the hall); every tier has two to four keys, each on its landing; the first flight never crosses the door or the
  hearth; the crown stair crosses the crown opening above its lintel; flight 4's notch in the crown floor keeps
  clear of the opening; nothing glows that is bound (the only emissives are embers and the beacon).
* The path: from the wall-gate (the walk's level) to the forecourt, never descending, and the ground graded to it.
* Committed assets: one .glb per target inside its budget, every file under 5 MB with a PROVENANCE row, the import
  script is the kit's, every slot has a material, the manifest and the preview layouts name only kit pieces.
"""

from __future__ import annotations

import importlib.util
import json
import math
import struct
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "environments" / "kits" / "coilspire"
ASSETS = ROOT / "assets" / "environments" / "kits" / "coilspire"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "coilspire_kit"
CORROW_LAYOUT = ROOT / "game" / "levels" / "_tests" / "corrow_kit" / "corrow_layout.json"
MAX_BYTES = 5 * 1024 * 1024

sys.path.insert(0, str(SRC))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"coilspire_kit_{name}", SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


BUILD = _load("build")
import cs_common as cs  # noqa: E402
import cs_headland  # noqa: E402
import cs_spire  # noqa: E402

cw_far = cs.cw_far
kc = cs.kc
TARGETS = BUILD.targets()


def built(name: str) -> list:
    return BUILD.build_target(TARGETS[name][2])


def read_glb(path: Path) -> dict:
    data = path.read_bytes()
    magic, _v, _len = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a glb"
    jlen = struct.unpack("<I", data[12:16])[0]
    return json.loads(data[20:20 + jlen])


class OneBuildingTests(unittest.TestCase):
    def test_the_spire_stands_where_corrow_puts_it(self) -> None:
        corrow = json.loads(CORROW_LAYOUT.read_text())
        head = [p for p in corrow["pieces"] if p["piece"] == "coilspire_headland"][0]
        self.assertEqual((head["at"][0], head["at"][1], head["yaw_deg"]), cs.HEADLAND)
        mine = json.loads((PREVIEW / "coilspire_layout.json").read_text())
        np.testing.assert_allclose(mine["fire_lights"][0][:3], corrow["fire_lights"][0][:3], atol=0.01)
        shell = [p for p in mine["pieces"] if p["piece"] == "coilspire_shell"][0]
        np.testing.assert_allclose(shell["at"] + [shell["y"]],
                                   [corrow["fire_lights"][0][0], corrow["fire_lights"][0][2],
                                    corrow["fire_lights"][0][1] - cs.SPIRE_H - 1.6], atol=0.01)

    def test_the_radius_law_is_the_far_pieces(self) -> None:
        far = cw_far.build_headland()[0]
        p = np.asarray(far.pos)
        stone = np.asarray(far.tri_mat) == far.materials.index(cs.cw.M_CARVED)
        idx = np.unique(np.asarray(far.tris)[stone])
        sx, sz = cs.SPIRE_AT
        q = p[idx]
        y = q[:, 1] - cs.SPIRE_BASE_Y
        r = np.hypot(q[:, 0] - sx, q[:, 2] - sz)
        body = (y > 1.0) & (y < cs.SPIRE_H - 1.0)
        # The far tube is displaced up to 0.075 m; the near face follows the same law.
        np.testing.assert_allclose(r[body], cs.outer_r(y[body]), atol=0.09)

    def test_the_coils_and_the_cage_are_the_far_pieces(self) -> None:
        far = cw_far.build_headland()[0]
        p = np.asarray(far.pos)
        cu = np.asarray(far.tri_mat) == far.materials.index(cs.cw.M_COPPER)
        q = p[np.unique(np.asarray(far.tris)[cu])]
        sx, sz = cs.SPIRE_AT
        local = q - np.array([sx, cs.SPIRE_BASE_Y, sz])
        ys = np.linspace(cs.COIL_Y[0], cs.COIL_Y[1], 400)
        line = np.vstack([cs.coil_point(k, ys) for k in range(3)])
        d = np.min(np.linalg.norm(local[:, None, :] - line[None, :, :], axis=-1), axis=1)
        # Every far copper vertex lies on one of the near coils' tubes (radius 0.3 m).
        self.assertLess(float(np.max(np.abs(d - cs.COIL_R))), 0.08)
        self.assertEqual(cs.CAGE, {"bars": 8, "r0": 1.5, "rise": 3.2, "lean": 0.3, "ring_r": 1.8})

    def test_the_ground_is_the_far_rock_away_from_the_path(self) -> None:
        rng = np.random.default_rng(3)
        x = rng.uniform(-120.0, 120.0, 300)
        z = rng.uniform(-85.0, 85.0, 300)
        d, _ = cs.path_distance(x, z)
        far = (d > 6.0) & (np.hypot(x - cs.SPIRE_AT[0], z - cs.SPIRE_AT[1]) > 16.0)
        np.testing.assert_allclose(cs.ground_height(x[far], z[far]), cs.natural_height(x[far], z[far]), atol=1e-9)


class KitGeometryTests(unittest.TestCase):
    def test_every_target_is_inside_its_budget_with_a_lod_chain(self) -> None:
        for name, (key, module, _fn) in TARGETS.items():
            with self.subTest(target=name):
                builders = built(name)
                self.assertEqual([], BUILD.check_budget(module, key, builders))
                self.assertEqual([name, name + "-lod1"], [b.name for b in builders])
                self.assertLess(builders[1].triangle_count, builders[0].triangle_count)

    def test_generators_are_deterministic(self) -> None:
        for name in ("coilspire_shell", "coilspire_tiers", "headland_path", "keepers_hut"):
            with self.subTest(target=name):
                a, b = built(name), built(name)
                self.assertEqual(a[0].pos, b[0].pos)
                self.assertEqual(a[0].col, b[0].col)

    def test_channels_in_range_and_slots_are_the_kits(self) -> None:
        for name in TARGETS:
            with self.subTest(target=name):
                for mb in built(name):
                    col = np.asarray(mb.col)
                    self.assertTrue(np.all((col >= 0.0) & (col <= 1.0)))
                    for m in mb.materials:
                        self.assertIn(m, cs.SLOTS)

    def test_nothing_bound_glows(self) -> None:
        emissive = {cs.M_EMBER, cs.M_BEACON}
        for name in TARGETS:
            for mb in built(name):
                glowing = emissive & set(mb.materials)
                if glowing:
                    # wall_lamp: the keepers' lamps on the well's wall burn (env-art-b, the 10-29 audit)
                    self.assertIn(name, {"beacon_basket", "tier_brazier", "keepers_hut", "coilspire_tiers",
                                         "wall_lamp"}, name)


class PlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.flights, self.landings = cs.plan()

    def test_four_tiers_and_a_crown(self) -> None:
        self.assertEqual([ln.tier for ln in self.landings], [2, 3, 4])
        self.assertEqual([f.y1 for f in self.flights], [9.0, 18.0, 27.0, 35.0, cs.GALLERY_Y])
        for f in self.flights:
            self.assertAlmostEqual(f.rise, cs.RISE_M, delta=0.01)

    def test_landings_leave_the_middle_of_the_well_open(self) -> None:
        for ln in self.landings:
            d = cs.dir_of(ln.centre)
            chord = -cs.LANDING_CHORD * float(cs.inner_r(ln.y))
            self.assertGreater(chord, 0.5, "the axis is clear of every landing by half a metre")
            self.assertLess(float(np.dot(np.zeros(3), d)), chord)

    def test_each_tier_has_two_to_four_keys_on_its_landing(self) -> None:
        keys = cs.key_list()
        for tier in (1, 2, 3, 4):
            mine = [k for k in keys if k[0] == tier]
            self.assertTrue(2 <= len(mine) <= 4, (tier, mine))
        for ln in self.landings:
            for _t, a, _y, _k in [k for k in keys if k[0] == ln.tier]:
                self.assertLess(abs(cs.ang_diff(a, ln.centre)), ln.half - 5.0)
        self.assertEqual(len([k for k in keys if k[3] == "side"]), 1, "tier 2's side flue")

    def test_the_first_flight_never_blocks_the_door_or_the_hearth(self) -> None:
        f = self.flights[0]
        for i in range(1, f.count + 1):
            a, top = f.tread(i)
            if abs(cs.ang_diff(a, cs.DOOR_A)) < 16.0:
                self.assertGreater(top, 3.4)
            if abs(cs.ang_diff(a, cs.HEARTH_A)) < 16.0:
                self.assertGreater(top, 1.9)
            for ka in cs.TIER1_KEYS:
                if abs(cs.ang_diff(a, ka)) < 10.0:
                    self.assertGreater(top, 2.5, "a tread over a hall key leaves room for the wheel")

    def test_the_crown_stair_crosses_the_opening_above_its_lintel(self) -> None:
        a_c, hw, _y0, y1 = cs.CROWN_OPEN
        half = math.degrees(hw / float(cs.inner_r(cs.CROWN_Y + 2.0))) + 8.0
        f = self.flights[4]
        for i in range(1, f.count + 1):
            a, top = f.tread(i)
            if abs(cs.ang_diff(a, a_c)) < half:
                self.assertGreater(top - 0.22, y1, (i, a, top))

    def test_flight_fours_notch_keeps_clear_of_the_opening(self) -> None:
        f4 = self.flights[3]
        a_c, hw, _y0, _y1 = cs.CROWN_OPEN
        half = math.degrees(hw / float(cs.inner_r(cs.CROWN_Y)))
        for a in np.linspace(f4.a1, f4.a1 + 120.0, 61):
            self.assertGreater(abs(cs.ang_diff(a, a_c)), half, a)

    def test_slits_and_openings_clear_the_flues(self) -> None:
        for a, hw, y0, y1 in cs_spire.openings():
            if y1 < cs.COIL_Y[0] or y0 > cs.COIL_Y[1]:
                continue
            for y in np.linspace(max(y0, cs.COIL_Y[0]), min(y1, cs.COIL_Y[1]), 6):
                for k in range(3):
                    ca = math.degrees(float(cs.coil_angle(k, y)))
                    half = math.degrees((hw + cs.COIL_R + 0.1) / float(cs.outer_r(y)))
                    self.assertGreater(abs(cs.ang_diff(a, ca)), half, (a, y, k))


class PathTests(unittest.TestCase):
    def test_from_the_gate_to_the_forecourt_never_descending(self) -> None:
        y = cs.PATH.y
        self.assertAlmostEqual(float(y[0]), cs.cw.WALK_Y, places=6)
        self.assertAlmostEqual(float(y[-1]), cs.SPIRE_BASE_Y + cs.FORECOURT_DY, places=6)
        self.assertTrue(np.all(np.diff(y) >= -1e-9))
        end = cs.PATH.xz[-1]
        self.assertLess(math.hypot(end[0] - cs.SPIRE_AT[0], end[1] - cs.SPIRE_AT[1]), 9.0)

    def test_treads_rise_a_step_at_a_time(self) -> None:
        runs = cs_headland.tread_runs()
        tops = np.array([r[2] for r in runs])
        self.assertTrue(np.all(np.diff(tops) >= -1e-9))
        self.assertLessEqual(float(np.max(np.diff(tops))), 2 * cs.STEP_M + 1e-6)
        self.assertLessEqual(max(r[1] - r[0] for r in runs), cs_headland.TREAD_MAX + 0.06)

    def test_the_ground_is_graded_under_the_path(self) -> None:
        s = np.linspace(1.0, cs.PATH.s[-1] - 1.0, 40)
        pts = np.array([cs.PATH.at(v)[0] for v in s])
        clear = np.hypot(pts[:, 0] - cs.SPIRE_AT[0], pts[:, 1] - cs.SPIRE_AT[1]) > 15.0  # the forecourt takes over
        s, pts = s[clear], pts[clear]
        g = cs.ground_height(pts[:, 0], pts[:, 1])
        y = np.interp(s, cs.PATH.s, cs.PATH.y)
        np.testing.assert_allclose(g, y + cs.PATH_BED_DY, atol=0.05)


class CommittedAssetTests(unittest.TestCase):
    def test_one_glb_per_target_inside_its_budget(self) -> None:
        glbs = sorted(ASSETS.glob("*.glb"))
        self.assertEqual(sorted(p.stem for p in glbs), sorted(TARGETS))
        for p in glbs:
            key, module, _fn = TARGETS[p.stem]
            gltf = read_glb(p)
            for mesh in gltf["meshes"]:
                tris = 0
                for prim in mesh["primitives"]:
                    tris += gltf["accessors"][prim["indices"]]["count"] // 3
                    self.assertIn("COLOR_0", prim["attributes"])
                    self.assertIn("TEXCOORD_1", prim["attributes"])
                lod = 1 if mesh["name"].endswith("-lod1") else 0
                self.assertLessEqual(tris, module.TRI_BUDGET[key][lod], f"{p.name} {mesh['name']}")

    def test_every_file_is_small_and_has_provenance(self) -> None:
        prov = (ROOT / "assets" / "PROVENANCE.md").read_text(encoding="utf-8")
        for p in ASSETS.rglob("*"):
            if p.is_file() and p.suffix != ".import":
                rel = p.relative_to(ROOT).as_posix()
                self.assertLess(p.stat().st_size, MAX_BYTES, rel)
                self.assertIn(f"| {rel} |", prov)

    def test_glb_imports_use_the_kit_post_import(self) -> None:
        for p in sorted(ASSETS.glob("*.glb")):
            imp = p.with_name(p.name + ".import")
            self.assertTrue(imp.is_file(), imp.name)
            self.assertIn('import_script/path="res://game/core/import/coilspire_kit_post_import.gd"', imp.read_text())

    def test_every_slot_has_a_material(self) -> None:
        for p in sorted(ASSETS.glob("*.glb")):
            for m in read_glb(p).get("materials", []):
                self.assertTrue((ASSETS / "materials" / f"{m['name']}.tres").is_file(), f"{p.name}: {m['name']}")

    def test_manifest_matches_targets(self) -> None:
        manifest = json.loads((ASSETS / "kit_manifest.json").read_text())
        self.assertEqual(manifest["kit"], "coilspire")
        self.assertEqual(sorted(manifest["pieces"]), sorted(TARGETS))

    def test_preview_layouts_name_only_kit_pieces(self) -> None:
        layout = json.loads((PREVIEW / "coilspire_layout.json").read_text())
        self.assertEqual(layout["kit_dir"], "res://assets/environments/kits/coilspire/")
        for spec in layout["pieces"]:
            self.assertIn(spec["piece"], TARGETS, spec)
            self.assertIn("y", spec, "no terrain in the preview: every piece carries its height")
        self.assertEqual(len(layout["fire_lights"]), 1, "the beacon")
        self.assertEqual(len(layout["hearth_lights"]), 4 + 2, "four braziers, the keeping flame, the grate")
        back = json.loads((PREVIEW / "coilspire_backdrop.json").read_text())
        corrow = {p.stem for p in (ROOT / "assets" / "environments" / "kits" / "corrow").glob("*.glb")}
        pieces = {s["piece"] for s in back["pieces"]}
        self.assertTrue(pieces <= corrow)
        self.assertNotIn("coilspire_headland", pieces, "this kit replaces Corrow's far headland")


if __name__ == "__main__":
    unittest.main()
