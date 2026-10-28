"""Tests for the Pemakar procedural kit (M3-ENV-03). Run: python3 -m unittest discover -s tools/tests

* Geometry (no Blender needed): every target is inside its budget with an authored LOD1 chain, the
  generators are deterministic, the weathering channels are in [0, 1], every slot has a material in the
  kit's material table, and ash (VC.G) lies on the tops while the channel kerbs are wet (VC.B).
* The skyline: the plume runs its height in UV.y and faces outward; the massif rises steadily behind the
  town (no trench from the tier rings' far side) and stays under the kit's own treads.
* The preview layout: the committed JSON is the generator's output, it names only kit pieces, every
  tier's channel ends in a spill and the flow alternates (the boats zig-zag down), and the boats that
  reach the sea float on it, south of the shore.
* Committed assets: one .glb per target, each inside its budget, every file under 5 MB, every slot has a
  material, every file has a PROVENANCE row, and the import kind maps the kit to its own materials.
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
SRC = ROOT / "assets_src" / "environments" / "kits" / "pemakar"
ASSETS = ROOT / "assets" / "environments" / "kits" / "pemakar"
LAYOUT = ROOT / "game" / "levels" / "_tests" / "pemakar_kit" / "pemakar_preview_layout.json"
IMPORT_RULES = ROOT / "game" / "data" / "import" / "pemakar_kit.json"
MAX_BYTES = 5 * 1024 * 1024

sys.path.insert(0, str(SRC))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"pemakar_kit_{name}", SRC / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


BUILD = _load("build")
LAYOUT_GEN = _load("pemakar_layout")
MATS = _load("pemakar_materials")
import pemakar_common as pc  # noqa: E402
import pemakar_skyline as sky  # noqa: E402

TARGETS = BUILD.targets()
SLOTS = set(MATS.MATERIALS) | set(MATS.STANDARD)
_CACHE: dict[str, list] = {}


def built(name: str) -> list:
    if name not in _CACHE:
        _CACHE[name] = TARGETS[name][2]()
    return _CACHE[name]


def read_glb(path: Path) -> dict:
    data = path.read_bytes()
    magic, _v, _len = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a glb"
    jlen = struct.unpack("<I", data[12:16])[0]
    return json.loads(data[20:20 + jlen])


class KitGeometryTests(unittest.TestCase):
    def test_every_target_is_inside_its_budget_with_a_lod_chain(self) -> None:
        self.assertEqual(len(TARGETS), 34)  # M3-ENV-705 flank_rocks + 25 kit pieces + M3-ENV-06's arena_ash_tread + M3-ENV-11's ash_plume_near
        # + M3-ENV-1214's harbour_quay, sea_cut_weir, wake_wall, crown_bell
        # + env-art-b's votive_lamp (M3-ENV-1305) and weir_leat (M3-ENV-1307)
        for name, (key, module, _fn) in TARGETS.items():
            with self.subTest(target=name):
                builders = built(name)
                self.assertEqual([], BUILD.check_budget(module, key, builders))
                self.assertEqual([name, name + "-lod1"], [b.name for b in builders])
                self.assertLess(builders[1].triangle_count, builders[0].triangle_count)

    def test_generators_are_deterministic(self) -> None:
        for name in ("terrace_wall_copper", "grave_stele_b", "smithy", "ash_plume"):
            with self.subTest(target=name):
                a, b = TARGETS[name][2](), TARGETS[name][2]()
                for x, y in zip(a, b):
                    self.assertEqual(x.tris, y.tris)
                    self.assertEqual(x.materials, y.materials)
                    np.testing.assert_array_equal(np.asarray(x.pos), np.asarray(y.pos))
                    np.testing.assert_array_equal(np.asarray(x.col), np.asarray(y.col))

    def test_channels_in_range_and_every_slot_has_a_material(self) -> None:
        for name in TARGETS:
            for mb in built(name):
                with self.subTest(mesh=mb.name):
                    col = np.asarray(mb.col)
                    self.assertTrue((col >= 0.0).all() and (col <= 1.0).all())
                    self.assertTrue(set(mb.materials) <= SLOTS, set(mb.materials) - SLOTS)
                    self.assertEqual(sorted(set(mb.tri_mat)), list(range(len(mb.materials))), "no unused slots")

    def test_ash_lies_on_the_tops_and_the_kerbs_are_wet(self) -> None:
        mb = built("terrace_wall_4m")[0]
        col, nrm = np.asarray(mb.col), np.asarray(mb.nrm)
        up, side = nrm[:, 1] > 0.8, np.abs(nrm[:, 1]) < 0.2
        self.assertGreater(col[up, 1].mean(), col[side, 1].mean() + 0.15, "ash (VC.G) on tops, thin on faces")
        kerb = np.asarray(built("terrace_channel_4m")[0].col)
        self.assertGreater(kerb[:, 2].max(), 0.5, "the channel kerbs are wet (VC.B)")

    def test_lit_pieces_carry_a_flame(self) -> None:
        for name in ("leaf_boat_lit", "lamp_pillar", "grave_stele_a", "grave_stele_b"):
            self.assertIn(pc.M_FLAME, built(name)[0].materials, name)
        self.assertIn(pc.M_FORGE, built("smithy")[0].materials)
        self.assertIn(pc.M_COPPER, built("terrace_wall_copper")[0].materials)
        self.assertNotIn(pc.M_COPPER, built("terrace_wall_4m")[0].materials)


class SkylineTests(unittest.TestCase):
    def test_plume_runs_its_height_in_uv_y_and_faces_out(self) -> None:
        for mb in built("ash_plume"):
            uv = np.asarray(mb.uv)
            self.assertAlmostEqual(float(uv[:, 1].min()), 0.0, delta=1e-6)
            self.assertAlmostEqual(float(uv[:, 1].max()), 1.0, delta=1e-6)
            self.assertEqual(mb.materials, [pc.M_PLUME])
            self.assertTrue(sky._check_plume_winding(mb), mb.name)

    def test_near_plume_refines_the_far_plume(self) -> None:
        # M3-ENV-11: the near plume is the far plume's surface, denser, and hands over to the far plume's LOD0.
        near, near_lod1 = built("ash_plume_near")
        far = built("ash_plume")[0]
        self.assertEqual(near_lod1.pos, far.pos)
        self.assertEqual(near_lod1.tris, far.tris)
        self.assertGreater(near.triangle_count, 5 * far.triangle_count)
        self.assertEqual(near.materials, [pc.M_PLUME])
        self.assertTrue(sky._check_plume_winding(near))
        uv = np.asarray(near.uv)
        self.assertAlmostEqual(float(uv[:, 1].min()), 0.0, delta=1e-6)
        self.assertAlmostEqual(float(uv[:, 1].max()), 1.0, delta=1e-6)
        heads = np.asarray(near.uv2)[:, 0]
        self.assertTrue(0.0 <= heads.min() and heads.max() <= 1.0 and heads.std() > 0.05, "UV2.x carries the heads")
        self.assertTrue(np.all(np.asarray(far.uv2)[:, 0] == 1.0), "the far plume's UV2.x stays 1 (no billow shading)")
        # The same column: the near and far meshes span the same box to within a few metres.
        lo_n, hi_n = near.bounds()
        lo_f, hi_f = far.bounds()
        self.assertLess(float(np.abs(lo_n - lo_f).max()), 12.0)
        self.assertLess(float(np.abs(hi_n - hi_f).max()), 12.0)
        # Softer normals than the far mesh's: from ring to ring they turn far less (the far mesh's facets).
        def turn(mb, rings: int, sides: int) -> float:
            n = np.asarray(mb.nrm[: rings * (sides + 1)]).reshape(rings, sides + 1, 3)
            return float(np.percentile(1.0 - np.sum(n[1:, :-1] * n[:-1, :-1], axis=-1), 90))

        self.assertLess(turn(near, *sky.NEAR_GRID), 0.25 * turn(far, 64, 52))

    def test_massif_rises_behind_the_town(self) -> None:
        noise = pc.kc.Noise3(pc.kc.rng_for("mountain_massif", 801))
        z = np.arange(-115.0, -660.0, -5.0)
        h = sky.massif_height(np.zeros_like(z), z, noise)
        self.assertGreater(float(np.diff(h).min()), -12.0, "no trench across the face behind the town")
        self.assertGreater(float(h[-1]), 250.0)

    def test_massif_stays_under_the_kit_treads(self) -> None:
        noise = pc.kc.Noise3(pc.kc.rng_for("mountain_massif", 801))
        for t in range(pc.TOWN_TIERS):
            r = pc.TOWN_R0_M - pc.TREAD_D_M * (t + 0.5)
            a = np.linspace(-0.25, 0.25, 21)
            x, z = r * np.sin(a) + pc.TOWN_CENTRE[0], r * np.cos(a) + pc.TOWN_CENTRE[1]
            inside = np.abs(x) < 44.0
            h = sky.massif_height(x[inside], z[inside], noise)
            self.assertLess(float(h.max()), float(pc.tier_tread_y(t)) - 1.0, f"tier {t}")


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.layout = json.loads(LAYOUT.read_text())

    def test_committed_layout_is_the_generator_output(self) -> None:
        self.assertEqual(json.loads(json.dumps(LAYOUT_GEN.build())), self.layout)

    def test_layout_names_only_kit_pieces(self) -> None:
        self.assertEqual(self.layout["kit_dir"], "res://assets/environments/kits/pemakar/")
        names = {spec["piece"] for spec in self.layout["pieces"] if "kit_dir" not in spec}
        self.assertTrue(names <= set(TARGETS), names - set(TARGETS))
        self.assertEqual(self.layout["boats"]["piece"], "leaf_boat_lit")
        for spec in self.layout["pieces"]:
            for slot in spec.get("materials", {}).values():
                self.assertIn(slot, SLOTS)

    def test_every_tier_channel_spills_and_the_flow_alternates(self) -> None:
        channels = sorted(self.layout["channels"], key=lambda c: -c["tier"])
        self.assertEqual([c["tier"] for c in channels], list(reversed(range(pc.TOWN_TIERS))))
        flows = [c["flow"] for c in channels]
        self.assertTrue(all(a != b for a, b in zip(flows, flows[1:])), "zig-zag down the mountain")
        spills = sum(1 for p in self.layout["pieces"] if p["piece"].startswith("terrace_spill_"))
        self.assertEqual(spills, pc.TOWN_TIERS)

    def test_lanternfall_counts(self) -> None:
        self.assertGreater(len(self.layout["boats"]["transforms"]), 900, "a thousand leaf-boats")
        self.assertGreater(len(self.layout["far_lights"]["points"]), 2000)
        self.assertEqual(self.layout["lights"][0]["color"], "#FFA757", "the ch05 lamp key")

    def test_sea_boats_float_south_of_the_shore(self) -> None:
        pts = np.asarray(self.layout["sea_lights"]["points"])
        self.assertGreater(len(pts), 100)
        self.assertTrue((pts[:, 2] >= LAYOUT_GEN.SEA_SHORE_Z_M).all())
        self.assertTrue(np.allclose(pts[:, 1], LAYOUT_GEN.SEA_LIGHT_Y_M))

    def test_ashcrown_is_the_ashcrown_kits_building_at_the_rim(self) -> None:
        # M3-ENV-09B: the far temple is the Ashcrown kit's exterior pieces at the kit's origin (the rim point; the
        # kit's y 0 is the rim), with the Ashcrown preview's LOD1 distances; the silhouette is no longer placed.
        kit = ROOT / "assets" / "environments" / "kits" / "ashcrown"
        ac_layout = json.loads((ROOT / "game" / "levels" / "_tests" / "ashcrown_kit" / "ashcrown_layout.json")
                               .read_text())
        ac_lod1 = {p["piece"]: p["lod1_from_m"] for p in ac_layout["pieces"]}
        temple = [p for p in self.layout["pieces"] if "kit_dir" in p]
        self.assertEqual(sorted(p["piece"] for p in temple), sorted(LAYOUT_GEN.ASHCROWN_PIECES))
        rim = [round(float(v), 3) for v in sky.massif_rim_point()]
        for p in temple:
            self.assertEqual(p["kit_dir"], "res://assets/environments/kits/ashcrown/")
            self.assertEqual(p["materials_dir"], p["kit_dir"] + "materials/")
            self.assertTrue((kit / f"{p['piece']}.glb").is_file(), p["piece"])
            self.assertEqual(p["at"], rim)
            self.assertEqual(p["yaw_deg"], 0.0)
            self.assertEqual(p["lod1_from_m"], ac_lod1[p["piece"]], p["piece"])
        self.assertNotIn("ashcrown_silhouette", {p["piece"] for p in self.layout["pieces"]})

    def test_no_shipped_reference_to_the_preview(self) -> None:
        rules = IMPORT_RULES.read_text()
        self.assertNotIn("_tests", rules)
        for p in (ASSETS / "materials").glob("*.tres"):
            self.assertNotIn("game/levels/_tests", p.read_text(), p.name)


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
                lod = 1 if mesh["name"].endswith("-lod1") else 0
                self.assertLessEqual(tris, module.TRI_BUDGET[key][lod], f"{p.name} {mesh['name']}")

    def test_every_file_is_small_and_has_provenance(self) -> None:
        prov = (ROOT / "assets" / "PROVENANCE.md").read_text(encoding="utf-8")
        for p in ASSETS.rglob("*"):
            if p.is_file() and p.suffix != ".import":
                rel = p.relative_to(ROOT).as_posix()
                self.assertLess(p.stat().st_size, MAX_BYTES, rel)
                self.assertIn(f"| {rel} |", prov)

    def test_every_slot_has_a_material_file(self) -> None:
        for p in sorted(ASSETS.glob("*.glb")):
            for m in read_glb(p).get("materials", []):
                self.assertTrue((ASSETS / "materials" / f"{m['name']}.tres").is_file(), f"{p.name}: {m['name']}")

    def test_manifest_matches_targets(self) -> None:
        manifest = json.loads((ASSETS / "kit_manifest.json").read_text())
        self.assertEqual(manifest["kit"], "pemakar")
        self.assertEqual(sorted(manifest["pieces"]), sorted(TARGETS))

    def test_glbs_import_with_the_kit_script(self) -> None:
        rules = json.loads(IMPORT_RULES.read_text())
        self.assertEqual(rules["materials"]["slot_dir"], "res://assets/environments/kits/pemakar/materials/")
        for p in sorted(ASSETS.glob("*.glb")):
            text = Path(str(p) + ".import").read_text()
            self.assertIn(f'import_script/path="{rules["script"]}"', text, p.name)
            self.assertIn("meshes/generate_lods=false", text, p.name)


if __name__ == "__main__":
    unittest.main()


class Ch05GradeTests(unittest.TestCase):
    """M3-C05-03: Ch5's sub-frame grades (pemakar_grades.py): committed, each on its LUT, the suns in the zones'
    convention."""

    def test_the_grades_are_committed_and_point_at_their_luts(self) -> None:
        import json

        zone = Path(__file__).resolve().parents[2] / "assets" / "environments" / "zones" / "ch05"
        rows = json.loads((zone / "ch05_grades.json").read_text())
        for name, lut in (("ch05_harbour_dusk", "lut_ch05_harbour_dusk.png"),
                          ("ch05_ashcrown_day", "lut_ch05_ashcrown.png")):
            with self.subTest(grade=name):
                env = zone.parents[3] / rows[name]["environment"].removeprefix("res://")
                self.assertIn(lut, env.read_text())
                self.assertTrue((zone / lut).exists())
        self.assertAlmostEqual(rows["ch05_ashcrown_day"]["sun"]["yaw_deg"], -45.0, msg="az 225")
        self.assertAlmostEqual(rows["ch05_ashcrown_day"]["sun"]["pitch_deg"], -58.0)
