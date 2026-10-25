"""Tests for the Oruvel Underway procedural kit (M3-ENV-05). Run: python3 -m unittest discover -s tools/tests

* Geometry (no Blender needed): every target is inside its budget with an authored LOD1 chain, the generators are
  deterministic, the weathering channels are in [0, 1] and wet (everything is under water), and every slot is an
  `ou_*` slot with a material.
* The ground tiles: sea-floor cells meet at y 0 on every edge; edge cells' lips and faces are periodic, so a row
  of them joins; the apron's hole is exactly the terrace's extent.
* The story pieces keep the brief: no bound light anywhere (no emissive slot but the stand-in lantern's flame), the
  cord has new knots among the old, the gauge wheel's cut state has lost its rim, the dead ship's frames are tarred
  timber, the floors count to F9 = -22.4 m.
* Committed assets: one .glb per target, each inside its budget, every file under 5 MB, every file has a PROVENANCE
  row, the manifest lists every piece, the preview layout names only kit pieces and every preview camera.
"""

from __future__ import annotations

import importlib.util
import json
import re
import struct
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "environments" / "kits" / "oruvel_underway"
ASSETS = ROOT / "assets" / "environments" / "kits" / "oruvel_underway"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "oruvel_underway_kit"
LAYOUT = PREVIEW / "oruvel_underway_layout.json"
MAX_BYTES = 5 * 1024 * 1024

sys.path.insert(0, str(SRC))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"oruvel_underway_kit_{name}", SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


BUILD = _load("build")
MATS = _load("ou_materials")
LAYOUT_GEN = _load("ou_preview_layout")
import ou_common as oc  # noqa: E402
import ou_ground as og  # noqa: E402

TARGETS = BUILD.targets()
SLOTS = set(MATS.MATERIALS) | set(MATS.STANDARD)


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
        for name in ("seafloor_edge", "lamp_column", "coral_head_a", "wreck_ribs", "divers_cord"):
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
                    self.assertTrue(set(mb.materials) <= SLOTS, set(mb.materials) - SLOTS)
                    self.assertEqual(sorted(set(mb.tri_mat)), list(range(len(mb.materials))), "no unused slots")

    def test_everything_is_under_water(self) -> None:
        for name in ("seafloor_patch_a", "tower_bay", "lamp_column", "wreck_ribs"):
            col = np.asarray(built(name)[0].col)
            self.assertGreater(col[:, 2].mean(), 0.5, f"{name}: wet (VC.B; the shader wets everything under the line)")
            self.assertEqual(float(col[:, 0].max()), 0.0, f"{name}: no moss under the sea (VC.R)")

    def test_no_bound_light_anywhere(self) -> None:
        """Every housing is empty and dark (beat sheet C1-05): only the stand-in lantern's flame emits."""
        emissive = {n for n, spec in MATS.STANDARD.items() if spec.get("emission_enabled") == "true"}
        self.assertEqual(emissive, {"ou_flame"})
        for name in TARGETS:
            if name != "diver_lantern":
                self.assertNotIn("ou_flame", built(name)[0].materials, name)
        self.assertIn("ou_glass_dark", built("lamp_column")[0].materials)


class GroundTileTests(unittest.TestCase):
    EDGE = np.linspace(-og.HALF, og.HALF, 49)

    def test_patch_cells_meet_at_zero_on_every_edge(self) -> None:
        h = og.HALF
        for name, seed in (("seafloor_patch_a", 501), ("seafloor_patch_b", 502)):
            noise = oc.kc.Noise3(oc.kc.rng_for(name, seed))
            for x, z in ((self.EDGE, np.full_like(self.EDGE, -h)), (self.EDGE, np.full_like(self.EDGE, h)),
                         (np.full_like(self.EDGE, -h), self.EDGE), (np.full_like(self.EDGE, h), self.EDGE)):
                np.testing.assert_allclose(og.seafloor_height(noise, x, z), 0.0, atol=1e-9)

    def test_edge_cells_join_in_a_row(self) -> None:
        noise = oc.kc.Noise3(oc.kc.rng_for("seafloor_edge", 503))
        h = og.HALF
        self.assertAlmostEqual(float(og.lip_z(noise, np.array(-h))), float(og.lip_z(noise, np.array(h))), places=9)
        zs = np.linspace(-h, -1.0, 20)
        np.testing.assert_allclose(og.edge_height(noise, np.full_like(zs, -h), zs), 0.0, atol=1e-9)
        np.testing.assert_allclose(og.edge_height(noise, np.full_like(zs, h), zs), 0.0, atol=1e-9)
        np.testing.assert_allclose(og.edge_height(noise, self.EDGE, np.full_like(self.EDGE, -h)), 0.0, atol=1e-9)
        lip = og.lip_z(noise, self.EDGE)
        self.assertTrue(((lip > 0.0) & (lip < h)).all(), "the lip stays inside the cell")

    def test_apron_hole_is_the_terrace(self) -> None:
        self.assertEqual(og.HOLE_HALF, og.HALF * 11)
        far = built("seafloor_far")[0]
        pos = np.asarray(far.pos)
        tris = np.asarray(far.tris)
        cen = pos[tris].mean(axis=1)
        inside = (np.abs(cen[:, 0]) < og.HOLE_HALF) & (np.abs(cen[:, 2]) < og.HOLE_HALF)
        self.assertFalse(inside.any(), "no apron triangle over the terrace")


class StoryPieceTests(unittest.TestCase):
    def test_the_cord_has_new_knots_among_the_old(self) -> None:
        mb = built("divers_cord")[0]
        counts = {m: sum(1 for t in mb.tri_mat if mb.materials[t] == m) for m in ("ou_cord_old", "ou_cord_new")}
        self.assertGreater(counts["ou_cord_new"], 0)
        self.assertLess(counts["ou_cord_new"], counts["ou_cord_old"], "a quarter new, most of them old")

    def test_the_cut_wheel_has_lost_its_rim(self) -> None:
        whole, cut = built("gauge_wheel")[0], built("gauge_wheel_cut")[0]
        r_whole = np.linalg.norm(np.asarray(whole.pos)[:, :2] - [0.0, 1.6], axis=1).max()
        self.assertGreater(r_whole, 1.0, "teeth past the 0.95 m rim")
        brass = [i for i, m in enumerate(cut.materials) if m in ("ou_brass", "ou_patina")]
        pos = np.asarray(cut.pos)
        tris = np.asarray(cut.tris)
        cen = pos[tris].mean(axis=1)
        cen_r = np.linalg.norm(cen[:, :2] - [0.0, 1.6], axis=1)
        in_wheel = (np.abs(cen[:, 2]) < 0.12) & (cen[:, 1] > 0.5)  # the wheel's plane, above the plinth
        metal = np.isin(np.asarray(cut.tri_mat), brass) & in_wheel
        self.assertLess(float(cen_r[metal].max()), 0.85, "no brass beyond the spoke stubs")

    def test_the_dead_ship_is_tarred_timber_with_a_reef(self) -> None:
        mb = built("wreck_ribs")[0]
        self.assertEqual(mb.materials[0], "ou_timber_tar")
        self.assertTrue(any(m.startswith("ou_coral") for m in mb.materials))
        lo, hi = mb.bounds()
        self.assertGreater(float(hi[0] - lo[0]), 14.0, "about 15 m long")
        self.assertGreater(float(hi[1]), 2.0, "frames arch well out of the sand")

    def test_floors_count_to_the_ninth(self) -> None:
        self.assertAlmostEqual(LAYOUT_GEN.floor_y(9), -22.4)
        self.assertAlmostEqual(LAYOUT_GEN.floor_y(14), -6.4)

    def test_reef_colours_are_palette_derived_and_in_range(self) -> None:
        for name in ("ou_coral_bone", "ou_coral_ochre", "ou_coral_rose", "ou_coral_teal", "ou_sponge"):
            paint = MATS.MATERIALS[name]["params"]["col_paint"]
            rgb = [float(v) for v in re.findall(r"[\d.]+", paint)[:3]]
            self.assertTrue(all(0.11 < c < 0.93 for c in rgb), f"{name} inside the albedo floor/ceiling: {rgb}")


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

    def test_every_slot_has_a_material_and_the_import_script(self) -> None:
        for p in sorted(ASSETS.glob("*.glb")):
            for m in read_glb(p).get("materials", []):
                self.assertTrue((ASSETS / "materials" / f"{m['name']}.tres").is_file(), f"{p.name}: {m['name']}")
            imp = p.with_name(p.name + ".import")
            self.assertTrue(imp.is_file(), imp.name)
            self.assertIn('import_script/path="res://game/core/import/oruvel_underway_kit_post_import.gd"',
                          imp.read_text())

    def test_manifest_matches_targets(self) -> None:
        manifest = json.loads((ASSETS / "kit_manifest.json").read_text())
        self.assertEqual(manifest["kit"], "oruvel_underway")
        self.assertEqual(sorted(manifest["pieces"]), sorted(TARGETS))

    def test_preview_layout_names_only_kit_pieces_and_every_camera(self) -> None:
        layout = json.loads(LAYOUT.read_text())
        self.assertEqual(layout["kit_dir"], "res://assets/environments/kits/oruvel_underway/")
        for spec in layout["pieces"]:
            self.assertIn(spec["piece"], TARGETS, spec)
            self.assertIn("y", spec, "no terrain in the preview: every piece carries its height")
        scene = (PREVIEW / "oruvel_underway_preview.tscn").read_text()
        cams = re.findall(r'\[node name="(U\d\d)" type="Camera3D"', scene)
        self.assertEqual(sorted(cams), sorted(layout["shots"]))
        for entry in layout["shots"].values():
            self.assertIn(entry["area"], ("open", "interior", "deep"))
            self.assertEqual(len(entry["lantern"]), 3)


if __name__ == "__main__":
    unittest.main()
