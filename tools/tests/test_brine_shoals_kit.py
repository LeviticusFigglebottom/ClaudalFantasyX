"""Tests for the Brine Shoals procedural kit (M3-ENV-02). Run: python3 -m unittest discover -s tools/tests

* Geometry (no Blender needed): every target is inside its budget with an authored LOD1 chain, the
  generators are deterministic, the weathering channels are in [0, 1], and every slot is a `bs_*` slot.
* The ground tiles: mud and channel cells meet at y 0 on every edge, and every channel cell's end
  section is the same, so any sequence of a and b meanders without a seam.
* The burned variants really are burned (char, embers, fewer cloth faces), Liss's crate leaks bound
  light, the barge keeps the brief's proportions and the Order's colours small.
* Committed assets: one .glb per target, each inside its budget, every file under 5 MB, every slot has a
  material, every file has a PROVENANCE row, and the preview layout names only kit pieces.
"""

from __future__ import annotations

import importlib.util
import json
import struct
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "environments" / "kits" / "brine_shoals"
ASSETS = ROOT / "assets" / "environments" / "kits" / "brine_shoals"
LAYOUT = ROOT / "game" / "levels" / "_tests" / "brine_shoals_kit" / "brine_shoals_layout.json"
MAX_BYTES = 5 * 1024 * 1024

sys.path.insert(0, str(SRC))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"brine_shoals_kit_{name}", SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


BUILD = _load("build")
import bs_common as bc  # noqa: E402
import bs_ground as bg  # noqa: E402

TARGETS = BUILD.targets()


def built(name: str) -> list:
    return BUILD.build_target(TARGETS[name][2])


def read_glb(path: Path) -> dict:
    data = path.read_bytes()
    magic, _v, _len = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a glb"
    jlen = struct.unpack("<I", data[12:16])[0]
    return json.loads(data[20:20 + jlen])


class KitGeometryTests(unittest.TestCase):
    def test_every_target_is_inside_its_budget_with_a_lod_chain(self) -> None:
        for name, (key, module, _fn) in TARGETS.items():
            with self.subTest(target=name):
                builders = built(name)
                self.assertEqual([], BUILD.check_budget(module, key, builders))
                self.assertEqual([name, name + "-lod1"], [b.name for b in builders])
                self.assertLess(builders[1].triangle_count, builders[0].triangle_count)

    def test_generators_are_deterministic(self) -> None:
        for name in ("mudflat_patch_a", "camp_tent_burned", "wreck_hull_section", "salvage_pile_burned"):
            with self.subTest(target=name):
                a, b = built(name), built(name)
                for x, y in zip(a, b):
                    self.assertEqual(x.tris, y.tris)
                    self.assertEqual(x.materials, y.materials)
                    np.testing.assert_array_equal(np.asarray(x.pos), np.asarray(y.pos))
                    np.testing.assert_array_equal(np.asarray(x.col), np.asarray(y.col))

    def test_channels_in_range_and_slots_are_the_kits(self) -> None:
        for name in TARGETS:
            for mb in built(name):
                with self.subTest(mesh=mb.name):
                    col = np.asarray(mb.col)
                    self.assertTrue((col >= 0.0).all() and (col <= 1.0).all())
                    uv2 = np.asarray(mb.uv2)
                    self.assertTrue((uv2[:, 0] >= 0.0).all() and (uv2[:, 0] <= 1.0).all())
                    self.assertTrue(all(m.startswith("bs_") for m in mb.materials), mb.materials)
                    self.assertEqual(sorted(set(mb.tri_mat)), list(range(len(mb.materials))), "no unused slots")

    def test_the_flats_are_wet_and_the_wrecks_salted(self) -> None:
        mud = np.asarray(built("mudflat_patch_a")[0].col)
        self.assertGreater(mud[:, 2].mean(), 0.7, "the mud is wet (VC.B), so it carries the sky")
        hull = np.asarray(built("wreck_hull_section")[0].col)
        self.assertGreater(hull[:, 1].max(), 0.5, "the wrecks carry salt (VC.G)")


class GroundTileTests(unittest.TestCase):
    EDGE = np.linspace(-bg.HALF, bg.HALF, 97)

    def _edges(self, fn):
        h = bg.HALF
        return [fn(self.EDGE, np.full_like(self.EDGE, z)) for z in (-h, h)] + \
            [fn(np.full_like(self.EDGE, x), self.EDGE) for x in (-h, h)]

    def test_mud_cells_meet_at_zero_on_every_edge(self) -> None:
        for name, seed in (("mudflat_patch_a", 201), ("mudflat_patch_b", 202)):
            noise = bc.kc.Noise3(bc.kc.rng_for(name, seed))
            for e in self._edges(lambda X, Z: bg._mud_height(noise, X, Z)):
                np.testing.assert_allclose(e, 0.0, atol=1e-9)

    def test_channel_cells_join_without_a_seam(self) -> None:
        ends = []
        for name, seed, amp in (("channel_straight_a", 211, bg.CHANNEL_AMP_M), ("channel_straight_b", 212, -bg.CHANNEL_AMP_M)):
            noise = bc.kc.Noise3(bc.kc.rng_for(name, seed))
            h = bg.HALF
            for x in (-h, h):  # the long edges meet the mud cells at 0
                np.testing.assert_allclose(bg.channel_height(noise, np.full_like(self.EDGE, x), self.EDGE, amp), 0.0,
                                           atol=1e-9)
            ends += [bg.channel_height(noise, self.EDGE, np.full_like(self.EDGE, z), amp) for z in (-h, h)]
        for e in ends[1:]:
            np.testing.assert_allclose(e, ends[0], atol=1e-9)

    def test_channel_is_deep_enough_for_the_barge_at_low_water(self) -> None:
        bed = float(bg.channel_profile(np.array(0.0)))
        self.assertLess(bed, bg.WATER_Y - 1.0, "a metre under a 0.5 m draft at low water")
        width = 2.0 * float(np.interp(bg.WATER_Y, bg.channel_profile(np.linspace(0, 9, 400)), np.linspace(0, 9, 400)))
        self.assertGreater(width, 9.0)
        self.assertLess(width, 13.5)

    def test_the_hard_stands_above_the_strand_line(self) -> None:
        top = float(bg.hard_height(None, np.array(0.0), np.array(0.0)))
        self.assertAlmostEqual(top, bg.HARD_TOP_Y, delta=0.01)
        self.assertGreater(top, 0.9, "the high-water strand line (+0.9 m) lies on its flanks")


class CampTests(unittest.TestCase):
    def test_burned_variants_are_charred_with_embers(self) -> None:
        for name in ("camp_tent", "salvage_rack", "salvage_pile"):
            with self.subTest(piece=name):
                burned = built(name + "_burned")[0]
                self.assertIn("bs_char", burned.materials)
                self.assertIn("bs_ember", burned.materials)
                self.assertNotIn("bs_ember", built(name)[0].materials)
        for name in ("crate_stack", "brine_vat"):
            self.assertIn("bs_char", built(name + "_burned")[0].materials, name)

    def test_burned_tent_has_lost_most_of_its_canvas(self) -> None:
        def cloth(mb) -> int:
            ids = {mb.materials.index(m) for m in mb.materials if m.startswith("bs_canvas")}
            return sum(1 for t in mb.tri_mat if t in ids)

        intact = built("camp_tent")[0]
        burned = built("camp_tent_burned")[0]
        finer = (30 * 14) / (14 * 8)  # the burned slopes' grid is this many times denser
        self.assertLess(cloth(burned) / finer, cloth(intact) * 0.6, "most of the burned canvas is gone")

    def test_liss_crate_leaks_bound_light_only_up_close(self) -> None:
        crate, lod = built("liss_crate")
        self.assertIn("bs_glimmer_leak", crate.materials)
        self.assertNotIn("bs_glimmer_leak", lod.materials)

    def test_branding_irons_are_the_orders(self) -> None:
        mb = built("branding_brazier")[0]
        for slot in ("bs_iron_hot", "bs_lacquer_red", "bs_ember"):
            self.assertIn(slot, mb.materials)

    def test_smoke_plume_runs_its_height_in_uv_y(self) -> None:
        for mb in built("smoke_plume"):
            uv = np.asarray(mb.uv)
            self.assertAlmostEqual(float(uv[:, 1].min()), 0.0, delta=1e-6)
            self.assertAlmostEqual(float(uv[:, 1].max()), 1.0, delta=1e-6)
            self.assertEqual(mb.materials, ["bs_smoke"])


class BargeTests(unittest.TestCase):
    def test_proportions_and_draft(self) -> None:
        mb = built("white_barge")[0]
        lo, hi = mb.bounds()
        self.assertAlmostEqual(float(hi[0] - lo[0]), 12.0, delta=0.4)
        self.assertAlmostEqual(float(hi[2] - lo[2]), 3.4, delta=0.3)
        self.assertAlmostEqual(float(lo[1]), -0.51, delta=0.05, msg="draft 0.5 m below the waterline origin")

    def test_order_colours_stay_small(self) -> None:
        mb = built("white_barge")[0]
        pos = np.asarray(mb.pos)
        tris = np.asarray(mb.tris)
        area = 0.5 * np.linalg.norm(np.cross(pos[tris[:, 1]] - pos[tris[:, 0]], pos[tris[:, 2]] - pos[tris[:, 0]]), axis=1)
        by_slot = {m: float(area[np.asarray(mb.tri_mat) == i].sum()) for i, m in enumerate(mb.materials)}
        self.assertLess(by_slot["bs_gold"], 0.01 * by_slot["bs_barge_white"], "gold is a finial, not a surface")
        self.assertLess(by_slot["bs_lacquer_red"], 0.08 * by_slot["bs_barge_white"], "red is a sheer line")


class WakeTests(unittest.TestCase):
    """M3-ENV-1000: moving boats leave a Kelvin wake; Sefir's barge never carries one (ADR 0017 (a))."""

    def test_wake_lies_flat_just_over_the_water_behind_the_stern(self) -> None:
        for mb in built("boat_wake"):
            lo, hi = mb.bounds()
            self.assertEqual(mb.materials, ["bs_wake"])
            self.assertGreater(float(lo[1]), 0.0, "over the surface, never z-fighting it")
            self.assertLess(float(hi[1]), 0.05)
            self.assertLess(float(hi[0]), 0.1, "trails aft (-X) of the stern origin")
            self.assertAlmostEqual(float(-lo[0]), 16.0, delta=1.0)

    def test_arms_open_at_the_kelvin_angle(self) -> None:
        mb = built("boat_wake")[0]
        lo, hi = mb.bounds()
        half_angle = np.degrees(np.arctan2(float(hi[2]), float(-lo[0])))
        self.assertAlmostEqual(half_angle, 19.5 + 2.0, delta=3.0, msg="the arms' centre at 19.5 deg plus their width")

    def test_uv_runs_along_the_wake(self) -> None:
        for mb in built("boat_wake"):
            uv = np.asarray(mb.uv)
            self.assertAlmostEqual(float(uv[:, 1].min()), 0.0, delta=1e-6)
            self.assertAlmostEqual(float(uv[:, 1].max()), 1.0, delta=1e-6)
            self.assertEqual(sorted(set(np.asarray(mb.uv2)[:, 0].round(3))), [0.0, 1.0], "arms 0, centre track 1")

    def test_the_barge_has_no_wake(self) -> None:
        for mb in built("white_barge"):
            self.assertNotIn("bs_wake", mb.materials)


class TidelineTests(unittest.TestCase):
    """M3-C06-03: B09's diggable patch (two states) and hand-print, and the Stillguard's torch."""

    def _y_at(self, mb, x: float, z: float) -> float:
        p = np.asarray(mb.pos)
        return float(p[np.argmin(np.hypot(p[:, 0] - x, p[:, 2] - z)), 1])

    def test_the_patches_lie_flush_with_the_flats_at_their_edges(self) -> None:
        for name in ("lamp_hole_open", "lamp_hole_covered", "hand_print"):
            mb = built(name)[0]
            lo, hi = mb.bounds()
            with self.subTest(piece=name):
                for x, z in ((lo[0], lo[2]), (hi[0], hi[2]), (lo[0], hi[2]), (hi[0], lo[2])):
                    self.assertAlmostEqual(self._y_at(mb, x, z), 0.004, delta=1e-4)

    def test_the_hole_is_open_and_the_cover_closes_it(self) -> None:
        self.assertLess(self._y_at(built("lamp_hole_open")[0], 0.0, 0.0), -0.25, "a pit for the lamp")
        self.assertGreater(self._y_at(built("lamp_hole_covered")[0], 0.0, 0.25), 0.004, "filled back, mounded")

    def test_the_hand_is_pressed_into_the_sand(self) -> None:
        mb = built("hand_print")[0]
        self.assertLess(self._y_at(mb, 0.0, 0.03), -0.008, "the palm")
        self.assertLess(self._y_at(mb, -0.014, 0.155), -0.004, "a finger")
        self.assertAlmostEqual(self._y_at(mb, 0.15, -0.15), 0.004, delta=1e-4, msg="clear sand beside it")

    def test_the_torch_wears_the_orders_colours(self) -> None:
        mb = built("stillguard_torch")[0]
        for slot in ("bs_iron", "bs_lacquer_red", "bs_brass", "bs_ember"):
            self.assertIn(slot, mb.materials)
        self.assertAlmostEqual(float(mb.bounds()[0][1]), 0.0, delta=1e-6, msg="origin at the foot")


class GradeTests(unittest.TestCase):
    """M3-C06-03 item 7: the Ch6 sub-frames' Environments, LUTs and sun rows."""

    def test_the_grades_are_committed_and_point_at_their_luts(self) -> None:
        zone = ROOT / "assets" / "environments" / "zones" / "brine_shoals"
        rows = json.loads((zone / "ch06_grades.json").read_text())
        for name in ("ch06_hold", "ch06_dusk", "ch06_dawn"):
            with self.subTest(grade=name):
                env = ROOT / rows[name]["environment"].removeprefix("res://")
                self.assertTrue(env.exists())
                text = env.read_text()
                self.assertIn(f"lut_ch06_{name.removeprefix('ch06_')}.png", text)
                self.assertIn('[gd_resource type="Environment"', text)

    def test_sun_rows_follow_the_layouts_own_convention(self) -> None:
        grades = _load("bs_grades")
        layout = json.loads((ROOT / "game" / "levels" / "ch06" / "brine_shoals" / "brine_shoals_layout.json").read_text())
        self.assertAlmostEqual(grades.sun_yaw(240.0), float(layout["sun"]["yaw_deg"]), msg="ch06's own sun, az 240")
        self.assertAlmostEqual(grades.sun_yaw(75.0), 105.0)
        self.assertAlmostEqual(grades.sun_yaw(280.0), -100.0)

    def test_the_smoke_lut_is_unchanged_by_the_sub_frames(self) -> None:
        lut = _load("bs_zone_lut")
        self.assertEqual(lut.GRADES["smoke"]["saturation"], 0.90)
        self.assertEqual(lut.GRADES["smoke"]["toe_hex"], "#0E4A55")


class CommittedAssetTests(unittest.TestCase):
    def test_one_glb_per_target_inside_its_budget(self) -> None:
        glbs = sorted(ASSETS.glob("*.glb"))
        self.assertEqual(sorted(p.stem for p in glbs), sorted(TARGETS))
        for p in glbs:
            key, module, _fn = TARGETS[p.stem]
            for mesh in read_glb(p)["meshes"]:
                tris = 0
                gltf = read_glb(p)
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

    def test_every_slot_has_a_material(self) -> None:
        for p in sorted(ASSETS.glob("*.glb")):
            for m in read_glb(p).get("materials", []):
                self.assertTrue((ASSETS / "materials" / f"{m['name']}.tres").is_file(), f"{p.name}: {m['name']}")

    def test_manifest_matches_targets(self) -> None:
        manifest = json.loads((ASSETS / "kit_manifest.json").read_text())
        self.assertEqual(manifest["kit"], "brine_shoals")
        self.assertEqual(sorted(manifest["pieces"]), sorted(TARGETS))

    def test_preview_layout_names_only_kit_pieces(self) -> None:
        layout = json.loads(LAYOUT.read_text())
        self.assertEqual(layout["kit_dir"], "res://assets/environments/kits/brine_shoals/")
        for spec in layout["pieces"]:
            self.assertIn(spec["piece"], TARGETS, spec)
            self.assertIn("y", spec, "no terrain in the preview: every piece carries its height")
        self.assertTrue(layout["fire_lights"])


if __name__ == "__main__":
    unittest.main()
