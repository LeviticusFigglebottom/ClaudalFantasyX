"""Tests for the Haluna villager builds (M2-CHR-03, assets_src/characters/villagers/).

Run: python3 -m unittest discover -s tools/tests

* Parameters: one params file per villager, every key bb_params knows, the costume pieces on the
  villager cloth materials, a tint for each, a hair style the module knows.
* The committed GLBs: the NPC budget (LOD0 and LOD1 triangles, well under the 5 MB cap), the face
  blendshapes are the shared API (asha.md §6.2: 30 expression shapes and the visemes), every glTF
  material has a material in the villager's own materials folder (the `characters` import rule).
* The pose tables use only the shared API and cover every emotion tag; textures (size cap) and
  materials (every texture they name exists); the import wiring and a Blender job per villager.
"""
import json
import re
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "characters" / "villagers"
OUT = ROOT / "assets" / "characters" / "villagers"
STAGE = ROOT / "game" / "levels" / "_tests" / "characters" / "villagers"
for sub in ("villagers", "toma", "rhen", "asha", "base_body"):
    sys.path.insert(0, str(ROOT / "assets_src" / "characters" / sub))

NPCS = ["neme", "osu", "child", "vendor", "reed", "netmender", "fisher", "tavi", "kell"]
M2_SEVEN = NPCS[:7]  # M2-CHR-03; tavi and kell are M3-CHR-03 (params opt-ins, per-NPC clips)
PROPS = ROOT / "assets" / "characters" / "props" / "wick"
MAX_BYTES = 5 * 1024 * 1024  # ADR 0005 plain-blob cap
GLB_MAX = 3 * 1024 * 1024  # M2-CHR-03: "well under" the cap
LOD0_RANGE = (20_000, 36_000)  # the NPC budget, about 25-35k
LOD1_MAX = 20_000
PAIRED = ["brow_inner_up", "brow_down", "brow_outer_up", "lid_close", "lid_wide", "lid_squint", "cheek_raise",
          "nose_sneer", "mouth_smile", "mouth_frown", "mouth_stretch", "mouth_dimple"]
SINGLE = ["mouth_press", "mouth_pucker", "lip_upper_up", "lip_lower_down", "jaw_open", "jaw_clench"]
VISEMES = ["vis_rest", "vis_aa", "vis_e", "vis_i", "vis_o", "vis_u", "vis_mbp", "vis_fv", "vis_l", "vis_st"]
API = [f"{b}_{s}" for b in PAIRED for s in ("L", "R")] + SINGLE
# what CutsceneSequencer drives on every face (sequencer.json blink and visemes)
SEQUENCER = ["lid_close_L", "lid_close_R", "jaw_open", "vis_aa", "vis_e", "vis_i", "vis_o", "vis_u", "vis_mbp", "vis_fv"]


def params(npc: str) -> dict:
    return json.loads((SRC / "params" / f"{npc}.json").read_text(encoding="utf-8"))


def glb_json(path: Path) -> dict:
    data = path.read_bytes()
    magic, _version, _total = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a GLB"
    length, _kind = struct.unpack("<II", data[12:20])
    return json.loads(data[20:20 + length])


def tris(js: dict) -> int:
    return sum(js["accessors"][p["indices"]]["count"] // 3 for m in js["meshes"] for p in m["primitives"])


class TestParams(unittest.TestCase):
    def test_every_villager_has_a_params_file(self):
        self.assertEqual(sorted(p.stem for p in (SRC / "params").glob("*.json")), sorted(NPCS))

    def test_body_keys_are_bb_params_keys(self):
        import bb_params

        for npc in NPCS:
            with self.subTest(npc=npc):
                p = bb_params.load_params(path=str(SRC / "params" / f"{npc}.json"))  # raises on an unknown key
                self.assertGreater(p["height_m"], 1.0)

    def test_costume_uses_the_villager_materials(self):
        import villager_costume as C

        for npc in NPCS:
            with self.subTest(npc=npc):
                ex = params(npc)
                tints = ex["_tints"]
                for name, piece in ex["_costume"].items():
                    mat = piece if isinstance(piece, str) else piece["mat"]
                    self.assertIn(mat, C.CLOTH_MATS, f"{name}")
                    self.assertIn(mat, tints, f"{name} has no tint")
                for mat in tints:
                    self.assertIn(mat, C.CLOTH_MATS)

    def test_hair_styles_are_known(self):
        import villager_hair

        for npc in NPCS:
            with self.subTest(npc=npc):
                hp = params(npc)["_hair"]
                self.assertIn(hp["kind"], ("short", "cropped", "bun", "wrap"))
                st = villager_hair.style(hp)
                self.assertIn(st.table, villager_hair.HAIRLINES.values())

    def test_m3_opt_ins_only_on_the_new_villagers(self):
        # M3-CHR-03: garment_fit changes the build, so the M2 seven never carry it; host_snaps (M1-CHR-14's
        # host-determinism snaps) is on every villager since M2-CHR-11
        for npc in NPCS:
            with self.subTest(npc=npc):
                b = params(npc)["_build"]
                self.assertTrue(b.get("host_snaps"))
                self.assertEqual(bool(b.get("garment_fit")), npc not in M2_SEVEN)

    def test_kell_and_tavi_follow_the_sheet(self):
        # act1_npcs.md §3-§4: Kell is short with a female short crop and nearly bare arms; Tavi has her nose and iris;
        # Tavi's sleeveless top has M1-CHR-14's armhole drop; Kell's skirt is calf length, not ankle
        import villager_hair

        k, t = params("kell"), params("tavi")
        self.assertEqual((k["_hair"]["kind"], k["_hair"]["hairline"]), ("short", "female"))
        self.assertIs(villager_hair.style(k["_hair"]).table, villager_hair.HAIRLINES["female"])
        self.assertEqual(k["_skin"]["reach_bands"], {"L": 2, "R": 1})
        self.assertEqual(k["_costume"]["skirt"]["hem"], "calf")
        self.assertGreater(k["_skin"]["fingertip_oil"], 0.0)
        self.assertEqual(k["nose_bridge_width"], t["nose_bridge_width"])
        self.assertEqual(k["_eyes"]["iris"], t["_eyes"]["iris"])
        self.assertGreaterEqual(t["_costume"]["top"]["armhole_drop_m"], 0.115)
        self.assertNotIn("headwrap", k["_costume"])  # no wrap: she must not read as Osu

    def test_the_child_has_child_proportions(self):
        p = params("child")
        self.assertLess(p["height_m"], 1.4)
        self.assertLess(p["heads_tall"], 6.6)
        self.assertEqual(p["_skin"]["reach_bands"], {"L": 0, "R": 0})

    def test_reach_bands_grow_with_age(self):
        # bible §5.1: one band per voyage survived; the elders carry the most
        bands = {n: sum(params(n)["_skin"]["reach_bands"].values()) for n in NPCS}
        self.assertEqual(max(bands, key=bands.get), "osu")
        self.assertGreater(bands["netmender"], bands["fisher"])

    def test_atlas_islands_fit_and_do_not_overlap(self):
        import villager_costume as C

        rects = list(C.ATLAS.items())
        for name, (u0, v0, u1, v1) in rects:
            self.assertTrue(0.0 <= u0 < u1 <= 1.0 and 0.0 <= v0 < v1 <= 1.0, name)
        for i, (a, ra) in enumerate(rects):
            for b, rb in rects[i + 1:]:
                overlap = min(ra[2], rb[2]) - max(ra[0], rb[0]) > 1e-9 and min(ra[3], rb[3]) - max(ra[1], rb[1]) > 1e-9
                self.assertFalse(overlap, f"{a} overlaps {b}")


class TestCommittedGLBs(unittest.TestCase):
    def test_budget_and_size(self):
        for npc in NPCS:
            with self.subTest(npc=npc):
                lod0 = OUT / npc / f"{npc}.glb"
                lod1 = OUT / npc / f"{npc}_lod1.glb"
                self.assertLess(lod0.stat().st_size, GLB_MAX)
                self.assertLess(lod1.stat().st_size, GLB_MAX)
                n0, n1 = tris(glb_json(lod0)), tris(glb_json(lod1))
                self.assertGreaterEqual(n0, LOD0_RANGE[0])
                self.assertLessEqual(n0, LOD0_RANGE[1])
                self.assertLess(n1, min(LOD1_MAX, n0))

    def test_face_shapes_are_the_shared_api(self):
        for npc in NPCS:
            with self.subTest(npc=npc):
                js = glb_json(OUT / npc / f"{npc}.glb")
                head = next(m for m in js["meshes"] if m["name"] == "Head")
                names = head.get("extras", {}).get("targetNames", [])
                self.assertTrue(set(names) <= set(API) | set(VISEMES), set(names) - set(API) - set(VISEMES))
                for s in SEQUENCER:
                    self.assertIn(s, names)

    def test_every_material_has_a_villager_material(self):
        for npc in NPCS:
            with self.subTest(npc=npc):
                for stem in (npc, f"{npc}_lod1"):
                    js = glb_json(OUT / npc / f"{stem}.glb")
                    for m in js["materials"]:
                        self.assertTrue((OUT / npc / "materials" / f"{m['name']}.tres").exists(), m["name"])

    def test_one_skeleton_with_the_eye_bones(self):
        for npc in NPCS:
            with self.subTest(npc=npc):
                js = glb_json(OUT / npc / f"{npc}.glb")
                self.assertEqual(len(js["skins"]), 1)
                names = {n.get("name") for n in js["nodes"]}
                for b in ("DEF-spine.006", "DEF-eye.L", "DEF-eye.R", "DEF-hand.R"):
                    self.assertIn(b, names)


class TestPoseTables(unittest.TestCase):
    def test_tables_use_the_shared_api_and_cover_every_tag(self):
        tags = [e["id"] for e in json.loads((ROOT / "game/data/dialogue/emotions.json").read_text())["emotions"]]
        for npc in NPCS:
            with self.subTest(npc=npc):
                table = json.loads((STAGE / f"{npc}_face_poses.json").read_text(encoding="utf-8"))
                self.assertEqual(sorted(table["emotions"]), sorted(tags))
                js = glb_json(OUT / npc / f"{npc}.glb")
                head = next(m for m in js["meshes"] if m["name"] == "Head")
                names = set(head["extras"]["targetNames"])
                for tag, pose in table["emotions"].items():
                    for shape, w in pose.items():
                        self.assertTrue(shape in SINGLE or shape in PAIRED, f"{tag}: {shape}")
                        keys = [shape] if shape in SINGLE else [f"{shape}_L", f"{shape}_R"]
                        for k in keys:
                            self.assertIn(k, names, f"{tag}: {k}")
                        for x in (w if isinstance(w, list) else [w]):
                            self.assertTrue(0.0 <= float(x) <= 1.0, f"{tag}: {shape}")

    def test_bark_emotions_have_poses(self):
        # every [emotion] a villager speaks in the slice's scripts has a row (the stage scenes use them)
        speakers = {"Neme": "neme", "Reed": "reed", "Netmender": "netmender", "Fisher": "fisher", "Child": "child",
                    "Vendor": "vendor"}
        for dlg in (ROOT / "game/data/dialogue/ch02").glob("*.dlg"):
            for line in dlg.read_text(encoding="utf-8").splitlines():
                m = re.match(r"^(\w+) \[(\w+)\]:", line)
                if m and m.group(1) in speakers:
                    table = json.loads((STAGE / f"{speakers[m.group(1)]}_face_poses.json").read_text())
                    self.assertIn(m.group(2), table["emotions"], f"{dlg.name}: {line[:40]}")


class TestTexturesAndMaterials(unittest.TestCase):
    def test_textures_under_the_cap(self):
        files = list(OUT.glob("*/textures/*.png")) + list(OUT.glob("textures/*.png"))
        self.assertGreaterEqual(len(files), 4 + 8 * len(NPCS))
        for f in files:
            self.assertLess(f.stat().st_size, MAX_BYTES, f.name)

    def test_material_textures_exist(self):
        for npc in NPCS:
            for tres in (OUT / npc / "materials").glob("*.tres"):
                for m in re.finditer(r'path="res://([^"]+)"', tres.read_text(encoding="utf-8")):
                    with self.subTest(material=f"{npc}/{tres.name}"):
                        self.assertTrue((ROOT / m.group(1)).exists(), m.group(1))

    def test_cloth_tints_are_the_params(self):
        for npc in NPCS:
            with self.subTest(npc=npc):
                for mat in params(npc)["_tints"]:
                    text = (OUT / npc / "materials" / f"{mat}.tres").read_text(encoding="utf-8")
                    self.assertIn("villagers_cloth_albedo.png", text)
                    self.assertIn("shader_parameter/col_albedo", text)


class TestClips(unittest.TestCase):
    def test_clip_libraries_rebuild_byte_for_byte(self):
        import villager_clips

        for npc in NPCS:
            with self.subTest(npc=npc):
                path = villager_clips.out_path(npc)
                self.assertEqual(path.read_text(encoding="utf-8"), villager_clips.build(npc))
                for clip in ("idle", "talk", "walk"):
                    self.assertIn(f'resource_name = &"{clip}"', path.read_text(encoding="utf-8"))

    def test_scene_clips_per_villager(self):
        # M3-CHR-03: Tavi's and Kell's scene clips (act1_npcs.md §3.5, §4.6); the M2 seven keep exactly three
        import villager_clips

        want = {"tavi": ["hand_on_shoulder", "hear_news", "name_rite"],
                "kell": ["press_wick", "trim_wick", "haggle_laugh"]}
        for npc in NPCS:
            with self.subTest(npc=npc):
                text = villager_clips.out_path(npc).read_text(encoding="utf-8")
                self.assertEqual(villager_clips.clips_for(npc), ["idle", "talk", "walk"] + want.get(npc, []))
                self.assertEqual(text.count('[sub_resource type="Animation"'), 3 + len(want.get(npc, [])))
        self.assertIn("trim_wick", villager_clips.EXTRA_LOOPS)

    def test_every_villager_has_a_persona(self):
        for npc in NPCS:
            with self.subTest(npc=npc):
                pers = params(npc)["_persona"]
                self.assertTrue({"sway", "lean", "arms_down"} <= set(pers))


class TestWiring(unittest.TestCase):
    def test_import_rule_and_import_files(self):
        rules = json.loads((ROOT / "game/data/import/characters.json").read_text(encoding="utf-8"))
        for npc in NPCS:
            with self.subTest(npc=npc):
                self.assertIn(f"res://assets/characters/villagers/{npc}/", rules["assets"])
                for stem in (npc, f"{npc}_lod1"):
                    text = (OUT / npc / f"{stem}.glb.import").read_text(encoding="utf-8")
                    self.assertIn('import_script/path="res://game/core/import/characters_post_import.gd"', text)

    def test_a_blender_job_per_villager(self):
        jobs = {j["id"]: j for j in json.loads((ROOT / "tools/dev/blender_builds.json").read_text())["jobs"]}
        for npc in NPCS:
            with self.subTest(npc=npc):
                job = jobs[f"villager_{npc}"]
                self.assertIn("assets_src/characters/asha/**", job["sources"])
                self.assertIn(f"assets/characters/villagers/{npc}/*.glb", job["outputs"])

    def test_actor_scenes_face_minus_z(self):
        # the capsules in haluna.tscn face -Z (their Facing box); glTF characters face +Z
        for npc in NPCS:
            with self.subTest(npc=npc):
                text = (OUT / npc / f"{npc}_actor.tscn").read_text(encoding="utf-8")
                self.assertIn(f'path="res://assets/characters/villagers/{npc}/{npc}.glb"', text)
                self.assertIn("Transform3D(-1, 0, 0, 0, 1, 0, 0, 0, -1, 0, 0, 0)", text)

    def test_provenance_rows(self):
        text = (ROOT / "assets/PROVENANCE.md").read_text(encoding="utf-8")
        for npc in NPCS:
            self.assertIn(f"assets/characters/villagers/{npc}/", text)
        self.assertIn("assets/characters/villagers/textures/", text)
        self.assertIn("assets/characters/props/wick/", text)


class TestWickProps(unittest.TestCase):
    """M3-CHR-03: one wick source (assets_src/characters/props/wick.py) for Kell's hand, her bundle, Rhen's tin and the
    E7 lamp (act1_npcs.md §4.4)."""

    def test_props_job_outputs_and_import(self):
        jobs = {j["id"]: j for j in json.loads((ROOT / "tools/dev/blender_builds.json").read_text())["jobs"]}
        job = jobs["props_wick"]
        self.assertEqual(job["threads"], 4)
        self.assertIn("assets_src/characters/props/wick.py", job["sources"])
        rules = json.loads((ROOT / "game/data/import/characters.json").read_text(encoding="utf-8"))
        self.assertIn("res://assets/characters/props/wick/", rules["assets"])
        for stem in ("wick", "wick_bundle", "trimming_shears"):
            with self.subTest(prop=stem):
                glb = PROPS / f"{stem}.glb"
                self.assertLess(glb.stat().st_size, 512 * 1024)
                js = glb_json(glb)
                self.assertLess(tris(js), 4000)
                for m in js["materials"]:
                    self.assertTrue((PROPS / "materials" / f"{m['name']}.tres").exists(), m["name"])
                self.assertIn("characters_post_import.gd", (PROPS / f"{stem}.glb.import").read_text())

    def test_the_wick_is_nine_centimetres(self):
        import numpy as np

        sys.path.insert(0, str(ROOT / "assets_src" / "characters" / "asha"))
        import asha_glb

        js, bin_ = asha_glb.read_glb(PROPS / "wick.glb")
        P = asha_glb.accessor(js, bin_, js["meshes"][0]["primitives"][0]["attributes"]["POSITION"])
        for prim in js["meshes"][0]["primitives"][1:]:
            P = np.concatenate([P, asha_glb.accessor(js, bin_, prim["attributes"]["POSITION"])])
        ext = P.max(axis=0) - P.min(axis=0)
        self.assertAlmostEqual(float(ext[1]), 0.09, delta=0.002)  # glTF +Y: the length
        self.assertLess(float(max(ext[0], ext[2])), 0.006)  # about 4 mm thick


if __name__ == "__main__":
    unittest.main()
