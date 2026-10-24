"""Tests for the Oruvel raft-town procedural kit (M3-ENV-07). Run: python3 -m unittest discover -s tools/tests

* Geometry (no Blender needed): every target is inside its budget with an authored LOD1 chain, the generators are
  deterministic, the weathering channels are in [0, 1] with no moss anywhere (nothing grows on a raft), and every slot
  is an `ov_*` slot with a material.
* The brief: no emissive slot at all (every lamp is out at 10:30); every hull has its tar below the boot line and its
  paint above, in the one overridable paint slot; the open-throat gull's carving faces outward and its throat holes
  are dark; the dive raft's well is open and centred on the origin; the bridge's ends sit at deck height.
* The preview agrees with the Underway: the dive raft's well is over the Underway's tether, the neighbour raft sits
  where the Underway's hull_keels are; every gull faces the sea; the generated files are current.
* Committed assets: one .glb per target, each inside its budget, every file under 5 MB with a PROVENANCE row, the
  import script on every .glb, the manifest lists every piece.
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
SRC = ROOT / "assets_src" / "environments" / "kits" / "oruvel"
ASSETS = ROOT / "assets" / "environments" / "kits" / "oruvel"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "oruvel_kit"
UNDERWAY_LAYOUT = ROOT / "game" / "levels" / "_tests" / "oruvel_underway_kit" / "oruvel_underway_layout.json"
MAX_BYTES = 5 * 1024 * 1024

sys.path.insert(0, str(SRC))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"oruvel_kit_{name}", SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


BUILD = _load("build")
MATS = _load("ov_materials")
LAYOUT_GEN = _load("ov_preview_layout")
import ov_cabins as ocab  # noqa: E402
import ov_common as oc  # noqa: E402
import ov_heroes as oh  # noqa: E402
import ov_hulls as ohl  # noqa: E402

TARGETS = BUILD.targets()
SLOTS = set(MATS.MATERIALS) | set(MATS.STANDARD)
_CACHE: dict[str, list] = {}


def built(name: str) -> list:
    if name not in _CACHE:
        _CACHE[name] = BUILD.build_target(TARGETS[name][2])
    return _CACHE[name]


def read_glb(path: Path) -> dict:
    data = path.read_bytes()
    magic, _v, _len = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a glb"
    jlen = struct.unpack("<I", data[12:16])[0]
    return json.loads(data[20:20 + jlen])


def centroids(mb) -> np.ndarray:
    p = np.asarray(mb.pos)
    return p[np.asarray(mb.tris)].mean(axis=1)


class KitGeometryTests(unittest.TestCase):
    def test_every_target_is_inside_its_budget_with_a_lod_chain(self) -> None:
        for name, (key, module, _fn) in TARGETS.items():
            with self.subTest(target=name):
                builders = built(name)
                self.assertEqual([], BUILD.check_budget(module, key, builders))
                self.assertEqual([name, name + "-lod1"], [b.name for b in builders])
                self.assertLess(builders[1].triangle_count, builders[0].triangle_count)

    def test_generators_are_deterministic(self) -> None:
        for name in ("raft_deck", "cabin_keelroof", "dive_raft", "lintel_gull_open"):
            with self.subTest(target=name):
                a, b = BUILD.build_target(TARGETS[name][2]), built(name)
                for x, y in zip(a, b):
                    self.assertEqual(x.tris, y.tris)
                    self.assertEqual(x.materials, y.materials)
                    np.testing.assert_array_equal(np.asarray(x.pos), np.asarray(y.pos))
                    np.testing.assert_array_equal(np.asarray(x.col), np.asarray(y.col))

    def test_channels_in_range_no_moss_and_slots_are_the_kits(self) -> None:
        for name in TARGETS:
            for mb in built(name):
                with self.subTest(mesh=mb.name):
                    col = np.asarray(mb.col)
                    self.assertTrue((col >= 0.0).all() and (col <= 1.0).all())
                    self.assertLess(float(col[:, 0].max()), 1e-6, "no moss on a raft (VC.R)")
                    uv2 = np.asarray(mb.uv2)
                    self.assertTrue((uv2[:, 0] >= 0.0).all() and (uv2[:, 0] <= 1.0).all())
                    self.assertTrue(set(mb.materials) <= SLOTS, set(mb.materials) - SLOTS)
                    self.assertEqual(sorted(set(mb.tri_mat)), list(range(len(mb.materials))), "no unused slots")


class BriefTests(unittest.TestCase):
    def test_nothing_emits(self) -> None:
        """Every lamp in the town is out at 10:30 (oruvel.md §3): no emissive slot, lanterns are glass and brass."""
        emissive = {n for n, spec in MATS.STANDARD.items() if spec.get("emission_enabled") == "true"}
        self.assertEqual(emissive, set())
        self.assertIn("ov_glass", built("chandlery")[0].materials)

    def test_hulls_are_tarred_below_and_painted_above(self) -> None:
        h = oc.hull("h", 10.0, 2.6, 1.2, oc.kc.rng_for("t", 1), oc.kc.Noise3(oc.kc.rng_for("t", 1)), waterline=-0.55)
        c = centroids(h)
        mats = np.array([h.materials[m] for m in h.tri_mat])
        self.assertLess(float(c[mats == oc.M_TAR][:, 1].mean()), -0.55, "tar below the waterline")
        self.assertGreater(float(c[mats == oc.M_PAINT][:, 1].mean()), -0.55, "paint above it")
        self.assertIn(oc.M_PAINT, MATS.MATERIALS, "the overridable colourway has a material")
        for slot in oc.PAINTS:
            self.assertIn(slot, MATS.MATERIALS, slot)

    def test_the_gull_faces_outward_with_a_dark_open_throat(self) -> None:
        mb = built("lintel_gull_open")[0]
        self.assertGreater(ocab._signed_volume(mb, 0, mb.triangle_count), 0.0, "the carving's faces point outward")
        self.assertIn(oc.M_DARK, mb.materials, "the bored throat reads dark")
        dark = [k for k, m in enumerate(mb.tri_mat) if mb.materials[m] == oc.M_DARK]
        c = centroids(mb)[dark]
        s = ocab.GULL_LEN / 0.72
        self.assertGreater(float(c[:, 0].max()), 0.33 * s, "a hole between the mandibles")
        self.assertLess(float(c[:, 0].min()), 0.27 * s, "and the wind-hole at the nape")

    def test_the_dive_well_is_open_over_the_origin(self) -> None:
        mb = built("dive_raft")[0]
        c = centroids(mb)
        timber = mb.materials.index(oc.M_TIMBER)
        deck = (np.asarray(mb.tri_mat) == timber) & (np.abs(c[:, 1] - oh.DIVE_DECK_Y) < 0.05)
        w = oh.DIVE_WELL - 0.05
        in_well = deck & (np.abs(c[:, 0]) < w) & (np.abs(c[:, 2]) < w)
        self.assertFalse(in_well.any(), "no plank across the dive well")
        self.assertTrue((deck & (np.abs(c[:, 0]) > 1.0)).any(), "the deck is there round it")

    def test_bridge_ends_at_deck_height(self) -> None:
        mb = built("plank_bridge")[0]
        p = np.asarray(mb.pos)
        ends = p[(p[:, 2] < 0.3) | (p[:, 2] > ohl.BRIDGE_SPAN - 0.3)]
        self.assertLess(abs(float(ends[:, 1].min()) + 0.17), 0.1, "the end beams rest just under the deck tops")
        mid = p[np.abs(p[:, 2] - ohl.BRIDGE_SPAN * 0.5) < 0.2]
        self.assertLess(float(np.median(mid[:, 1])), float(np.median(ends[:, 1])), "it sags in the middle")


class PreviewTests(unittest.TestCase):
    LAYOUT = json.loads((PREVIEW / "oruvel_layout.json").read_text())

    def test_layout_names_only_kit_pieces(self) -> None:
        self.assertEqual(self.LAYOUT["kit_dir"], "res://assets/environments/kits/oruvel/")
        names = {p["piece"] for p in self.LAYOUT["pieces"]}
        self.assertTrue(names <= set(TARGETS), names - set(TARGETS))
        self.assertEqual(names, set(TARGETS), "every piece is in the preview (the kit row at least)")

    def test_dive_raft_over_the_underways_tether_and_neighbour(self) -> None:
        under = json.loads(UNDERWAY_LAYOUT.read_text())
        tether = next(p for p in under["pieces"] if p["piece"] == "tether_line")
        keels = next(p for p in under["pieces"] if p["piece"] == "hull_keels")
        dive = [p for p in self.LAYOUT["pieces"] if p["piece"] == "dive_raft"][0]
        self.assertEqual(dive["at"], tether["at"], "the dive well is over the Underway's tether")
        nb = [p for p in self.LAYOUT["pieces"] if p["piece"] == "raft_deck_small" and p["at"] == keels["at"]]
        self.assertEqual(len(nb), 1, "the neighbour raft is where the Underway's hull_keels are")
        self.assertAlmostEqual(nb[0]["yaw_deg"], keels["yaw_deg"] - 90.0, places=3, msg="hulls along the same line")

    def test_every_town_gull_faces_the_sea(self) -> None:
        for p in self.LAYOUT["pieces"]:
            if p["piece"] != "lintel_gull_open" or p["at"][0] >= LAYOUT_GEN.KIT_ROW_X0 - 5.0:
                continue
            self.assertLessEqual(abs(p["yaw_deg"] - LAYOUT_GEN.GULL_YAW), LAYOUT_GEN.GULL_JITTER + 1e-6, p)

    def test_generated_files_are_current(self) -> None:
        LAYOUT_GEN._rng = oc.kc.rng_for("oruvel_preview_layout", 7)  # the generator's own seed, from the start
        pieces = json.loads(json.dumps(LAYOUT_GEN.town() + LAYOUT_GEN.kit_row()))
        self.assertEqual(pieces, self.LAYOUT["pieces"], "run ov_preview_layout.py")
        self.assertEqual((PREVIEW / "oruvel_preview.tscn").read_text(), LAYOUT_GEN.tscn(LAYOUT_GEN.SHOTS))
        manifest = json.loads((PREVIEW / "oruvel_preview_shots.json").read_text())
        self.assertEqual(manifest, LAYOUT_GEN.manifest())
        scene = (PREVIEW / "oruvel_preview.tscn").read_text()
        cams = re.findall(r'\[node name="(O\d\d)" type="Camera3D"', scene)
        self.assertEqual(sorted(cams), sorted(self.LAYOUT["shots"]))

    def test_nothing_shipped_names_the_preview(self) -> None:
        for p in list(SRC.glob("*.py")) + [ROOT / "game" / "data" / "import" / "oruvel_kit.json"]:
            if p.name == "ov_preview_layout.py":
                continue
            self.assertNotIn("_tests/", p.read_text(encoding="utf-8"), p.name)


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
            self.assertIn('import_script/path="res://game/core/import/oruvel_kit_post_import.gd"', imp.read_text())

    def test_manifest_matches_targets(self) -> None:
        manifest = json.loads((ASSETS / "kit_manifest.json").read_text())
        self.assertEqual(manifest["kit"], "oruvel")
        self.assertEqual(sorted(manifest["pieces"]), sorted(TARGETS))


if __name__ == "__main__":
    unittest.main()
