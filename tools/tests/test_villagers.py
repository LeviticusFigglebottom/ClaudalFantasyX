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

# M3-CHR-509..517: the Act I villagers that were capsules (the Haluna trades, the Order clerk, the four barge Reeds,
# the Saltwright girl and two children)
ACT1 = ["shopkeeper", "smith", "innkeeper", "clerk", "reed_a", "reed_b", "reed_c", "reed_d", "wright_girl",
        "wright_child_a", "wright_child_b"]
# M3-CHR-526..539: the named Act I story NPCs, in story order (Ch1 Oruvel, Ch4 the ferry, Ch5 Pemakar and Ashcrown, Ch7
# Tamsule, Ch8-9 Corrow)
NAMED = ["sabe", "scaleman", "skipper_sadi", "ferrymaster", "purser", "elder", "garo", "tender", "ione", "poolkeeper",
         "fenn", "gatekeeper", "hobb", "marra"]
NPCS = ["neme", "osu", "child", "vendor", "reed", "netmender", "fisher", "tavi", "kell"] + ACT1 + NAMED
M2_SEVEN = NPCS[:7]  # M2-CHR-03; tavi and kell are M3-CHR-03 (params opt-ins, per-NPC clips)
REEDS = ["reed_a", "reed_b", "reed_c", "reed_d"]
WRIGHTS = ["wright_girl", "wright_child_a", "wright_child_b"]
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

    def test_act1_villagers_follow_their_briefs(self):
        # M3-CHR-512/516/517: dressed for the trade; M3-CHR-509: the Order's colours, no armour; M3-CHR-510: variants of
        # the chapel Reed (white robe, ochre sash), each distinct
        smith, shop, inn, clerk = (params(n) for n in ("smith", "shopkeeper", "innkeeper", "clerk"))
        self.assertEqual(smith["_costume"]["apron"]["mat"], "cloth_d")
        self.assertTrue(smith["_costume"]["apron"]["over_trousers"])
        self.assertGreater(smith["_costume"]["top"]["cuff_roll_m"], 0.0)  # sleeves rolled
        self.assertLess(smith["_costume"]["top"]["sleeve"], 0.5)
        self.assertIn("cloth_d", smith["_cloth_params"])
        self.assertIn("apron", shop["_costume"])
        self.assertEqual(inn["_hair"]["kind"], "bun")
        self.assertTrue({"top", "skirt", "apron", "sash"} <= set(clerk["_costume"]))
        self.assertGreater(clerk["_costume"]["top"]["sleeve"], 0.9)
        self.assertEqual(clerk["_costume"]["skirt"]["hem"], "ankle")
        reed = params("reed")
        looks = set()
        for n in REEDS:
            with self.subTest(reed=n):
                p = params(n)
                self.assertEqual(p["_costume"]["top"]["mat"], "cloth_a")
                self.assertEqual(p["_costume"]["skirt"]["mat"], "cloth_a")
                self.assertEqual(p["_costume"]["sash"]["mat"], "cloth_c")
                self.assertGreater(min(int(p["_tints"]["cloth_a"][i:i + 2], 16) for i in (1, 3, 5)), 0xC8)  # white (sea-greyed at most)
                self.assertEqual(p["_skin"]["reach_bands"], reed["_skin"]["reach_bands"])  # novices, not sailors
                looks.add((p["height_m"], p["skin_hex"], p["_hair"]["kind"], p["_costume"]["top"]["sleeve"],
                           p["_costume"]["skirt"]["hem"]))
        self.assertEqual(len(looks), len(REEDS))
        skins = [params(n)["skin_hex"] for n in ACT1]
        self.assertEqual(len(set(skins)), len(skins))

    def test_named_npcs_follow_the_beats(self):
        # act1_ch05.md §4: Garo's forearms are bare (burn-scarred) and he wears a leather apron; act1_ch08.md: Hobb's
        # cord and the gatekeeper's colours are watch-red (browner than lacquer red); act1_ch07.md: Ione's reach-bands
        # run to the elbow; Sabe is Oruvel's old diver (the most bands in Ch1)
        garo = params("garo")
        self.assertEqual(garo["_costume"]["apron"]["mat"], "cloth_d")
        self.assertLess(garo["_costume"]["top"]["sleeve"], 0.4)
        watch_red = "#8E3B2E"
        self.assertEqual(params("hobb")["_tints"][params("hobb")["_costume"]["sash"]["mat"]], watch_red)
        self.assertEqual(params("gatekeeper")["_tints"][params("gatekeeper")["_costume"]["sash"]["mat"]], watch_red)
        self.assertGreaterEqual(sum(params("ione")["_skin"]["reach_bands"].values()), 20)
        self.assertGreaterEqual(sum(params("sabe")["_skin"]["reach_bands"].values()), 20)
        self.assertGreater(params("marra")["_skin"]["age"], 0.8)
        self.assertGreater(params("fenn")["_skin"]["age"], 0.9)

    def test_wright_line_marks(self):
        # M3-CHR-511 (act1_npcs.md §2.3): liss_textures' generator with each wright's own seed and placement, on body
        # maps large enough for the strokes; the regions are the generator's own
        sys.path.insert(0, str(ROOT / "assets_src" / "characters" / "liss"))
        import liss_textures

        liss_seed = json.loads((ROOT / "assets_src/characters/liss/liss_params.json").read_text())["_marks"]["seed"]
        seeds = set()
        for n in WRIGHTS:
            with self.subTest(wright=n):
                sk = params(n)["_skin"]
                lm = sk["line_marks"]
                self.assertTrue(set(lm["placement"]) <= set(liss_textures.REGION_ORDER))
                self.assertGreaterEqual(sum(lm["placement"].values()), 1)
                self.assertNotEqual(lm["seed"], liss_seed)
                seeds.add(lm["seed"])
                self.assertGreaterEqual(min(sk["body_size"]), 1024)
                self.assertGreaterEqual(params(n)["_costume"]["top"].get("sleeve", 0.0), 0.0)
                self.assertLessEqual(params(n)["_costume"]["top"].get("sleeve", 0.0), 0.35)  # sleeves pushed up
        self.assertEqual(len(seeds), len(WRIGHTS))
        for n in ("wright_child_a", "wright_child_b"):
            self.assertLess(params(n)["height_m"], 1.4)

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
                "kell": ["press_wick", "trim_wick", "haggle_laugh"],
                # M3-CHR-509..517: the trades' gestures and the Ch6 scripts' calls (villager_story_clips.json)
                "shopkeeper": ["offer_goods"], "smith": ["hammer_strike"], "innkeeper": ["welcome_bow"],
                "clerk": ["heat_iron", "iron_into_water", "hand_over"],
                **{n: ["pole_barge", "bow_from_barge"] for n in REEDS},
                "wright_girl": ["arm_held_out", "kneel_wait", "dig_sand", "flatten_sand", "set_in_hole"],
                "wright_child_a": ["crawl_out", "kneel_wait"], "wright_child_b": ["crawl_out", "kneel_wait"],
                # M3-CHR-526..539: the dialogue's `@anim` calls for the named NPCs, plus a gesture each
                "sabe": ["sit_watch", "shout_lines"], "scaleman": ["weigh_stamp", "nod"],
                "skipper_sadi": ["cast_off", "laugh"], "ferrymaster": ["nod"], "purser": ["offer_goods"],
                "elder": ["give_boat"], "garo": ["fold_boat", "nod", "laugh", "take_boat"],
                "tender": ["open_pavilion", "palms_level", "paint_gilt", "open_chamber", "hand_key"], "ione": ["nod"],
                "poolkeeper": ["chalk_slate"], "fenn": ["feed_fire", "hand_driftwood", "hand_key"],
                "gatekeeper": ["open_gate"], "hobb": ["drill_call"], "marra": ["hold_hands", "look_back"]}
        for npc in NPCS:
            with self.subTest(npc=npc):
                text = villager_clips.out_path(npc).read_text(encoding="utf-8")
                self.assertEqual(villager_clips.clips_for(npc), ["idle", "talk", "walk"] + want.get(npc, []))
                self.assertEqual(text.count('[sub_resource type="Animation"'), 3 + len(want.get(npc, [])))
        self.assertIn("trim_wick", villager_clips.EXTRA_LOOPS)
        for loop in ("pole_barge", "heat_iron", "hammer_strike", "kneel_wait", "arm_held_out"):
            self.assertIn(loop, villager_clips.EXTRA_LOOPS)

    def test_every_script_call_has_its_clip(self):
        # every `@anim <speaker> <clip>` the dialogue makes of an Act I villager (act1_ch06.md: the clerk, the Reeds,
        # the wright children) names a clip in that villager's library
        import villager_clips

        for dlg in (ROOT / "game/data/dialogue").rglob("*.dlg"):
            for line in dlg.read_text(encoding="utf-8").splitlines():
                m = re.match(r"^\s*@anim (\w+) (\w+)", line)
                # `look_at` is CutsceneSequencer's own turn, not a clip
                if m and m.group(1) in ACT1 + NAMED and m.group(2) != "look_at":
                    with self.subTest(call=f"{dlg.name}: {m.group(1)} {m.group(2)}"):
                        self.assertIn(m.group(2), villager_clips.clips_for(m.group(1)))

    def test_story_clips_loop_cleanly(self):
        # a looping story clip's first and last keys are the same pose, so the cycle has no pop
        import villager_clips

        for clip, spec in villager_clips.STORY_SPECS.items():
            if spec.get("loop"):
                with self.subTest(clip=clip):
                    self.assertEqual(spec["keys"][0][1], spec["keys"][-1][1])

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
        self.assertIn("assets_src/characters/villagers/villager_story_clips.json", text)


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


class TestDialoguePolish(unittest.TestCase):
    """The dialogue-distance polish of the named Act I villagers (M3-CHR-526..539): optional keys whose defaults leave
    every other villager as it was."""

    def test_grey_strands_are_opt_in_and_draw_no_rng(self):
        import numpy as np
        import villager_hair

        w = np.array([0.004, 0.005, 0.006])
        slots = np.array([1, 2, 3])
        mats = ["hair", "hair_grey", "hair"]
        plain = villager_hair.style({"kind": "short"})
        self.assertEqual(plain._grey_strands(w, slots, mats, (0.1, 0.9)), (w, slots, (0.1, 0.9)))
        st = villager_hair.style({"kind": "short", "grey_strands": True, "grey_width_k": 0.5})
        w2, s2, u2 = st._grey_strands(w, slots, mats, (0.1, 0.9))
        self.assertEqual(list(w2), [0.004, 0.0025, 0.006])
        self.assertIn(int(s2[1]), villager_hair.SLOTS_SPARSE)
        self.assertEqual((int(s2[0]), int(s2[2])), (1, 3))
        self.assertEqual(u2, [(0.1, 0.9), villager_hair.GREY_U, (0.1, 0.9)])
        every = villager_hair.style({"kind": "cropped", "grey_strands": "all", "grey_width_k": 0.5})
        w3, s3, u3 = every._grey_strands(w, slots, mats, (0.1, 0.9))
        self.assertEqual(list(w3), list(w * 0.5))
        self.assertTrue(all(int(q) in villager_hair.SLOTS_SPARSE for q in s3))
        self.assertEqual(u3, [villager_hair.GREY_U] * 3)

    def test_cord_knots_and_narrow_tails(self):
        import numpy as np
        import villager_costume as C
        from asha_mesh import Part

        rows, cols = 6, 5

        def sash() -> Part:
            p = Part("Sash")
            for i in range(C.WAIST_KNOT_VERTS):
                p.add_v((0.05 + 0.001 * (i % 3), -0.15, 1.0))
            p.tail_first = len(p.V)
            p.tail_rows = [(0, rows, cols, 1)]
            for j in range(rows):
                for i in range(cols):
                    p.add_v((0.04 + 0.01 * i, -0.16, 0.98 - 0.05 * j))
            return p

        p = sash()
        before = [v.copy() for v in p.V]
        self.assertIsNone(C._cord_shape(p, {"mat": "cloth_a", "width_m": 0.03}, 0.6, 1.0))
        self.assertTrue(all((a == b).all() for a, b in zip(before, p.V)))
        knots = C._cord_shape(p, {"tail_w_k": 0.5, "knot_k": 0.5, "cord_knots": 3}, 0.6, 1.0)
        first = p.tail_first
        width = np.linalg.norm(p.V[first + cols - 1] - p.V[first])
        self.assertAlmostEqual(float(width), 0.02, places=9)
        self.assertEqual(len(knots.V), 3 * (10 * 5 + 2))  # three 10 x 6 knots
        z = sorted({round(float(v[2]), 3) for v in knots.varr()[::52]})
        self.assertEqual(len(knots.varr()[::52]), 3)
        self.assertTrue(all(0.6 < q < 1.0 for q in z))

    @staticmethod
    def _fitted(npc: str):
        import bb_anatomy
        import bb_donor
        import bb_params
        from asha_costume import Fields, TorsoChart

        lm = bb_donor.fit(bb_params.load_params(path=str(SRC / "params" / f"{npc}.json"))).lm
        body = bb_anatomy.Body(lm)
        return lm, body, Fields(body), TorsoChart(lm)

    def test_marras_netting_shawl_and_wrist_cord(self):
        # act1_ch08.md: Marra mends nets in a netting shawl, the one-knot stair-watch cord on her wrist
        import numpy as np
        import villager_costume as C

        cp = params("marra")["_costume"]
        lm, body, fields, chart = self._fitted("marra")
        shawl = C.build_shawl(fields, chart, cp["shawl"])
        self.assertLess(shawl.tris(), 6500)  # twine only, inside the NPC budget
        self.assertGreater(float(body.regions["torso"].sdf(shawl.varr()).min()), 0.004)  # over the top, not in it
        self.assertEqual(set(shawl.M), {cp["shawl"]["mat"]})
        cord = C.build_wrist_cord(fields, cp["wrist_cord"])
        wr = lm.side_pt("wrist", cp["wrist_cord"]["side"])
        self.assertLess(float(np.linalg.norm(cord.varr() - wr, axis=1).max()), 0.07)
        self.assertEqual(cp["wrist_cord"]["mat"], cp["sash"]["mat"])  # the faded watch-red

    def test_wrap_edge_tuck_is_opt_in(self):
        # M3-CHR-539: a head wrap with `edge_off_m` has its edge drawn in to the skin; without it, as before
        import numpy as np
        import villager_costume as C

        hw = dict(params("marra")["_costume"]["headwrap"])
        _lm, body, fields, _chart = self._fitted("marra")
        tucked = C.build_headwrap(fields, hw)["HeadWrap"].varr()
        hw.pop("edge_off_m")
        loose = C.build_headwrap(fields, hw)["HeadWrap"].varr()
        head = body.regions["head"]
        n = 40  # the cap's azimuth samples; its last row (the edge) is the panel's last n vertices of the grid
        rows = 11
        edge_t = tucked[(rows - 1) * n:rows * n]
        edge_l = loose[(rows - 1) * n:rows * n]
        self.assertLess(float(np.median(head.sdf(edge_t))), float(np.median(head.sdf(edge_l))) - 0.004)

    def test_headband_presses_the_hair_under_it(self):
        # M3-CHR-03/528/537: hair at the band's height is drawn inside it; hair well above it is left alone
        import numpy as np
        import villager_costume as C

        _lm, _body, fields, _chart = self._fitted("tavi")
        hw = params("tavi")["_costume"]["headwrap"]
        band = C.build_headwrap(fields, hw)["HeadWrap"]
        B = band.varr()
        lm = _lm
        hc = np.array([0.0, float(lm.P("head_c")[1]) + 0.02 * lm.h, float(lm.P("chin")[2]) + 0.55 * lm.h])
        front = B[np.argmin(B[:, 1])]  # the band's front, on the brow
        out = hc + (front - hc) * 1.15  # a hair vertex outside the band at its height
        above = out + np.array([0.0, 0.0, 0.2])
        P = C.press_under_band(np.stack([out, above]), band, lm, 0.002)
        self.assertLess(float(np.linalg.norm(P[0] - hc)), float(np.linalg.norm(front - hc)))
        self.assertTrue(np.allclose(P[1], above))

    def test_garos_burn_scars_sit_on_his_forearms(self):
        # act1_ch05.md §4: a smith's burn-scarred forearms; the term paints the forearms only and is seeded
        import numpy as np
        import villager_textures as vt

        sk = params("garo")["_skin"]
        lm, _body, _fields, _chart = self._fitted("garo")
        rng = np.random.default_rng(5)
        pts = []
        for sd in ("L", "R"):
            wr, el = lm.side_pt("wrist", sd), lm.side_pt("elbow", sd)
            t = rng.uniform(0.0, 1.0, 4000)[:, None]
            ring = rng.normal(size=(4000, 3)) * 0.02
            pts.append(wr + (el - wr) * t + ring)
        P = np.concatenate(pts + [lm.P("notch")[None, :] + rng.normal(size=(500, 3)) * 0.03])
        col = np.full((len(P), 3), 0.5)
        out = vt._burn_scars(col.copy(), P, lm, sk["burn_scars"], int(sk["seed"]))
        changed = np.abs(out - col).sum(axis=1) > 1e-6
        self.assertGreater(int(changed[:8000].sum()), 100)
        self.assertFalse(changed[8000:].any())  # nothing on the chest
        self.assertTrue(np.array_equal(out, vt._burn_scars(col.copy(), P, lm, sk["burn_scars"], int(sk["seed"]))))

    def test_chalk_and_burn_terms_are_opt_in(self):
        # M3-CHR-532/535: `burn_scars` and `fingertip_chalk` are optional; the villagers without them carry neither
        for npc in NPCS:
            sk = params(npc)["_skin"]
            with self.subTest(npc=npc):
                self.assertEqual("burn_scars" in sk, npc == "garo")
                self.assertEqual("fingertip_chalk" in sk, npc == "poolkeeper")

    def test_hobbs_cord_has_three_knots(self):
        # act1_ch08.md: the three-knot watch-red captain's cord
        self.assertEqual(params("hobb")["_costume"]["sash"]["cord_knots"], 3)


class TestDialoguePolish2(unittest.TestCase):
    """The second dialogue-range pass (M3-CHR-526/534/538/536/539/519): the tank cut, the feathered hairline and the
    old villagers' brow hairs, each an optional key whose default leaves every other villager as it was."""

    TANK = {"sabe", "ione"}
    FEATHER = {"sabe", "ione", "hobb"}
    BROWS = {"fenn", "marra", "osu", "sabe"}

    def test_opt_ins(self):
        for npc in NPCS:
            p = params(npc)
            with self.subTest(npc=npc):
                self.assertEqual(p["_costume"].get("top", {}).get("armhole_cut") == "tank", npc in self.TANK)
                self.assertEqual("hairline_feather" in p["_hair"], npc in self.FEATHER)
                self.assertEqual("brow_strands" in p["_skin"], npc in self.BROWS)
                self.assertEqual("brow_params" in p["_hair"], npc in self.BROWS)

    def test_tank_cut_puts_straps_over_the_shoulders(self):
        # the default sleeveless line is unchanged without the key; with it, a strap per side crosses the shoulder
        # crest (over the shoulder pivot, inside the acromion) and the panel keeps the default armhole floor
        import numpy as np
        import villager_costume as C

        lm, _body, fields, chart = TestDialoguePolish._fitted("sabe")
        top = dict(params("sabe")["_costume"]["top"])
        th = np.linspace(0.0, 360.0, 52, endpoint=False)
        plain = dict(top)
        plain.pop("armhole_cut")
        self.assertNotIn("TopStrapL", C.build_top(fields, chart, plain))
        tank_line = C.top_line(lm, chart, th, top, fields)
        plain_line = C.top_line(lm, chart, th, plain)
        a = np.abs(((th + 180.0) % 360.0) - 180.0)
        floor = (a >= C.TANK_ARM_FLOOR[0]) & (a <= C.TANK_ARM_FLOOR[1])
        self.assertTrue(np.allclose(tank_line[floor], plain_line[(a >= 76.0) & (a <= 92.0)].min()))
        parts = C.build_top(fields, chart, top)
        for sd, sg in (("L", 1.0), ("R", -1.0)):
            S = parts[f"TopStrap{sd}"].varr()
            self.assertEqual(set(parts[f"TopStrap{sd}"].M), {top["mat"]})
            self.assertGreater(float(S[:, 2].max()), float(lm.P("notch")[2]))  # over the crest, not beside it
            x = S[:, 0] * sg
            self.assertTrue((x > 0.0).all() and (x < float(lm.P("acromion")[0])).all())
            self.assertGreater(float(np.ptp(S[:, 1])), 0.1 * lm.S)  # from the front of the chest to the back
        self.assertEqual(len(C.build_top(fields, chart, top)["Top"].V), len(parts["Top"].V))  # deterministic

    def test_hairline_feather_is_off_for_the_heroes(self):
        import asha_textures as at
        import villager_textures  # noqa: F401  (imports asha_textures the way the villager build does)

        self.assertEqual(at.HAIRLINE_FEATHER, 0.0)

    def test_brow_hairs_follow_the_brow_cards(self):
        import numpy as np
        import villager_textures as vt

        sk = params("sabe")["_skin"]
        lm, body, _fields, _chart = TestDialoguePolish._fitted("sabe")
        face = body.face
        B = vt.brow_frame(face, "L")
        self.assertEqual(B.shape[0], 3)
        self.assertTrue((B[0, :, 1] < B[1, :, 1]).all() and (B[1, :, 1] < B[2, :, 1]).all())  # bottom, centre, top
        rng = np.random.default_rng(3)
        mid = B[1, B.shape[1] // 2]
        y_front = float(lm.P("head_c")[1]) - 0.5 * lm.h
        near = np.stack([mid[0] + rng.normal(0, 0.008, 3000), np.full(3000, y_front), mid[1] + rng.normal(0, 0.004, 3000)],
                        axis=1)
        far = near + np.array([0.0, 0.0, -0.06])  # on the cheek
        P = np.concatenate([near, far])
        col = np.full((len(P), 3), 0.5)
        out = vt._brow_strands(col.copy(), P, face, lm, sk["brow_strands"], int(sk["seed"]))
        changed = np.abs(out - col).sum(axis=1) > 1e-6
        self.assertGreater(int(changed[:3000].sum()), 100)
        self.assertFalse(changed[3000:].any())
        self.assertTrue(np.array_equal(out, vt._brow_strands(col.copy(), P, face, lm, sk["brow_strands"],
                                                             int(sk["seed"]))))

    def test_brow_params_reach_only_the_brow_material(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("villager_write_materials", SRC / "write_materials.py")
        wm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(wm)
        p = params("sabe")
        shader, _std, _tex = wm.tables("sabe", p)
        for k, v in p["_hair"]["brow_params"].items():
            self.assertEqual(shader["brow"][2][k], v)
        plain = dict(p, _hair={k: v for k, v in p["_hair"].items() if k != "brow_params"})
        base, _s, _t = wm.tables("sabe", plain)
        self.assertEqual(base["brow"][2]["alpha_boost"], "1.6")
        self.assertEqual({k: v for k, v in shader.items() if k != "brow"}, {k: v for k, v in base.items() if k != "brow"})


if __name__ == "__main__":
    unittest.main()
