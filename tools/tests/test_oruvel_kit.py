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
import ov_storm as STORM  # noqa: E402

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
        storm = {p["piece"] for p in self.LAYOUT["states"]["storm"]["pieces"]}
        storm |= {p["piece"] for p in self.LAYOUT["states"]["rebuilt"]["pieces"]}  # M3-ENV-730, E7's rebuilt state
        self.assertTrue(names | storm <= set(TARGETS), (names | storm) - set(TARGETS))
        self.assertEqual(names | storm, set(TARGETS), "every piece is in the preview (the kit rows at least)")
        self.assertFalse(names & set(STORM.TARGETS), "the storm pieces show only in the storm state")

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
        pieces = json.loads(json.dumps(LAYOUT_GEN.town() + LAYOUT_GEN.kit_row() + LAYOUT_GEN.mooring()))
        self.assertEqual(pieces, self.LAYOUT["pieces"], "run ov_preview_layout.py")
        self.assertEqual(json.loads(json.dumps(LAYOUT_GEN.storm(pieces))), self.LAYOUT["states"]["storm"])
        self.assertEqual(json.loads(json.dumps(LAYOUT_GEN.rigs())), self.LAYOUT["rigs"])
        terrace = json.loads((PREVIEW / "oruvel_seventh_terrace_layout.json").read_text())
        self.assertEqual(terrace["pieces"], json.loads(json.dumps(LAYOUT_GEN.seventh_terrace())), "run ov_preview_layout.py")
        self.assertEqual((PREVIEW / "oruvel_preview.tscn").read_text(), LAYOUT_GEN.tscn(LAYOUT_GEN.SHOTS))
        manifest = json.loads((PREVIEW / "oruvel_preview_shots.json").read_text())
        self.assertEqual(manifest, LAYOUT_GEN.manifest())
        scene = (PREVIEW / "oruvel_preview.tscn").read_text()
        cams = re.findall(r'\[node name="(O\d\d)" type="Camera3D"', scene)
        self.assertEqual(sorted(cams), sorted(self.LAYOUT["shots"]))

    def test_the_seventh_terrace_is_moored_at_the_outer_mooring(self) -> None:
        """M3-ENV-08B: the Brightwater kit's Seventh Terrace (moored and crewed) at oruvel.md's outer mooring, against
        this kit's stage raft, and O07 frames her name-board from the point Ch4's D06 uses (in her frame)."""
        bt = LAYOUT_GEN.bt
        terrace = json.loads((PREVIEW / "oruvel_seventh_terrace_layout.json").read_text())
        self.assertEqual(terrace["kit_dir"], "res://assets/environments/kits/brightwater_ferry/")
        names = {p["piece"] for p in terrace["pieces"]}
        self.assertTrue({"terrace_hull", "terrace_name_board", "terrace_sails_furled", "terrace_moored"} <= names, names)
        self.assertFalse(names & {"terrace_sails_set", "terrace_sails_lowered", "terrace_membrane", "terrace_derelict"},
                         "Ch1: moored and crewed, no Ch4 state")
        hull = next(p for p in terrace["pieces"] if p["piece"] == "terrace_hull")
        self.assertEqual(hull["at"], [-58.0, 8.0], "oruvel.md: the outer mooring at (-58, 8)")
        self.assertAlmostEqual(hull["y"], -bt.WATERLINE_Y, places=3, msg="her waterline on the sea")
        stage = next(p for p in self.LAYOUT["pieces"] if p["piece"] == "raft_deck_small"
                     and p["at"] == [round(-58.0 + bt.STAGE_AT[0], 3), round(8.0 + bt.STAGE_AT[1], 3)])
        self.assertEqual(stage["yaw_deg"], bt.STAGE_YAW)
        self.assertAlmostEqual(bt.STAGE_DECK_ABOVE_SEA, ohl.RAFT_SMALL_Y, places=3, msg="the gangplank lands on its deck")
        board = next(p for p in terrace["pieces"] if p["piece"] == "terrace_name_board")
        o07 = self.LAYOUT["shots"]["O07"]
        rel = np.array(o07["eye"]) - np.array([board["at"][0], board["y"], board["at"][1]])
        np.testing.assert_allclose(rel, np.array(bt.INSERT_EYE) - np.array(bt.NAME_BOARD_AT), atol=1e-3)
        self.assertAlmostEqual(o07["fov"], bt.INSERT_FOV, places=3)

    def test_nothing_shipped_names_the_preview(self) -> None:
        # The two preview writers name their own preview folders; what the zone dressing ships (its JSON and
        # Environment under assets/environments/zones/ch01/) is checked instead.
        shipped = sorted((ROOT / "assets" / "environments" / "zones" / "ch01").glob("oruvel_*"))
        for p in list(SRC.glob("*.py")) + [ROOT / "game" / "data" / "import" / "oruvel_kit.json"] + shipped:
            if p.name in ("ov_preview_layout.py", "ov_zone_dressing.py"):
                continue
            self.assertNotIn("_tests/", p.read_text(encoding="utf-8"), p.name)


class StormTests(unittest.TestCase):
    """M3-ENV-07B: the storm state. Broken pieces in the intact pieces' frames, soaked, the pen's split a rig that
    composes the pen at rest, the state replacing pieces one for one, Kell's beacon, the storm grade."""

    LAYOUT = json.loads((PREVIEW / "oruvel_layout.json").read_text())

    def test_everything_in_the_storm_is_soaked(self) -> None:
        for name in STORM.TARGETS:
            mb = built(name)[0]
            with self.subTest(target=name):
                wet = np.asarray(mb.col)[:, 2]
                self.assertGreater(float(np.median(wet)), 0.5, "VC.B: the spray and rain are over all of it")

    def test_broken_pieces_keep_their_intact_frames(self) -> None:
        for broken, intact in (("raft_deck_broken", "raft_deck"), ("plank_bridge_broken", "plank_bridge")):
            a, b = built(broken)[0].bounds(), built(intact)[0].bounds()
            with self.subTest(piece=broken):
                np.testing.assert_allclose(a[0][[0, 2]], b[0][[0, 2]], atol=1.6)
                np.testing.assert_allclose(a[1][[0, 2]], b[1][[0, 2]], atol=1.8)
        deck = built("raft_deck_broken")[0]
        top = np.asarray(deck.pos)
        held = top[(top[:, 0] < 0.0) & (top[:, 1] > 0.7) & (top[:, 1] < 1.0)]
        self.assertAlmostEqual(float(np.median(held[:, 1])), ohl.RAFT_DECK_Y, delta=0.06,
                               msg="the part that holds is at the intact deck height")
        p = np.asarray(built("plank_bridge_broken")[0].pos)
        mid = p[np.abs(p[:, 2] - ohl.BRIDGE_SPAN * 0.6) < 0.25]
        self.assertTrue(len(mid) == 0 or float(mid[:, 1].max()) < -0.5, "the bridge is gone at mid-span")
        self.assertLess(float(p[:, 1].min()), STORM.BRIDGE_WATER_Y, "its halves hang into the water")

    def test_the_capsized_hull_is_keel_up_and_awash(self) -> None:
        mb = built("hull_capsized")[0]
        c = centroids(mb)
        mats = np.array([mb.materials[m] for m in mb.tri_mat])
        tar = c[mats == oc.M_TAR]
        self.assertGreater(float(tar[:, 1].max()), 0.15, "its tarred bottom shows above the water")
        self.assertLess(float(tar[:, 1].max()), 0.6, "only just: it is awash")
        self.assertLess(float(c[mats == oc.M_PAINT][:, 1].mean()), 0.0, "its paint is under")

    def test_the_split_sections_compose_the_pen_at_rest(self) -> None:
        pen_lo, pen_hi = built("net_pen")[0].bounds()
        lo, hi = np.full(3, 1e9), np.full(3, -1e9)
        for name, sec in STORM.SPLIT_SECTIONS.items():
            mb = built(name)[0]
            basis, origin = STORM.section_pose(name, 0.0)
            np.testing.assert_allclose(basis, np.eye(3), atol=1e-9)
            np.testing.assert_allclose(origin, sec["hinge"])
            p = np.asarray(mb.pos) + origin
            lo, hi = np.minimum(lo, p.min(axis=0)), np.maximum(hi, p.max(axis=0))
            with self.subTest(section=name):
                self.assertIn(oc.M_NET, mb.materials, "each carries its torn share of the pen net")
        np.testing.assert_allclose(lo[[0, 2]], pen_lo[[0, 2]], atol=0.6)
        np.testing.assert_allclose(hi[[0, 2]], pen_hi[[0, 2]], atol=0.6)

    def test_the_rig_opens_the_sections_apart(self) -> None:
        cen = []
        for name in sorted(STORM.SPLIT_SECTIONS):
            _b, o0 = STORM.section_pose(name, 0.0)
            _b, o1 = STORM.section_pose(name, 1.0)
            self.assertGreater(float(np.dot((o1 - o0)[[0, 2]], o0[[0, 2]])), 0.0, f"{name} drifts outward")
            cen.append(o1)
        rig = self.LAYOUT["rigs"]["net_pen_split"]
        self.assertEqual([s["piece"] for s in rig["sections"]], sorted(STORM.SPLIT_SECTIONS))
        state = {p["piece"]: p for p in self.LAYOUT["states"]["storm"]["pieces"]
                 if p["piece"] in STORM.SPLIT_SECTIONS and abs(p["at"][0] - LAYOUT_GEN.NET_PEN[0]) < 10.0}
        for s in rig["sections"]:
            p = state[s["piece"]]
            want = np.array(s["hinge"]) + np.array(s["open"]["drift"])
            np.testing.assert_allclose([p["at"][0], p["y"], p["at"][1]], want, atol=1e-3)

    def test_the_state_replaces_day_pieces_that_exist(self) -> None:
        day = self.LAYOUT["pieces"]
        for h in self.LAYOUT["states"]["storm"]["hide"]:
            with self.subTest(hide=h):
                self.assertTrue(any(p["piece"] == h["piece"] and p["at"] == h["at"] and p["y"] == h["y"]
                                    for p in day))
        hidden = {h["piece"] for h in self.LAYOUT["states"]["storm"]["hide"]}
        self.assertTrue({"net_pen", "raft_deck", "plank_bridge", "hull_cabin"} <= hidden, hidden)

    def test_kells_beacon_is_on_the_chandlery_roof(self) -> None:
        (lamp,) = self.LAYOUT["storm_lights"]
        anchor = self.LAYOUT["anchors"]["chandlery_beacon"]
        self.assertLess(float(np.linalg.norm(np.array(lamp["at"]) - np.array(anchor))), 1.0)

    def test_the_storm_grade_desaturates_and_slates_the_water(self) -> None:
        lut = _load("ov_zone_lut")
        import colorsys
        for hexc, cut in (("#1FA3A6", 0.5), ("#4A5A2E", 0.5), ("#A9DCF2", 0.75)):
            c = np.array([int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5)])
            o = lut.grade(c[None, :])[0]
            self.assertLess(colorsys.rgb_to_hsv(*o)[1], colorsys.rgb_to_hsv(*c)[1] * cut, hexc)
        red = np.array([0xA8, 0x5F, 0x4C]) / 255
        self.assertGreater(colorsys.rgb_to_hsv(*lut.grade(red[None, :])[0])[1], 0.4, "the paint keeps its colour")
        self.assertGreater(float(lut.grade(np.zeros((1, 3))).min()), 0.0, "no black point at zero")

    def test_the_lut_imports_as_a_3d_texture(self) -> None:
        imp = (ASSETS / "lut_ch01_storm.png.import").read_text()
        self.assertIn('importer="3d_texture"', imp)
        self.assertIn("slices/horizontal=32", imp)
        on_disk = (ASSETS / "lut_ch01_storm.png").read_bytes()
        lut = _load("ov_zone_lut")
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "lut.png"
            lut.main(["--out", str(out)])
            self.assertEqual(out.read_bytes(), on_disk, "run ov_zone_lut.py")


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
