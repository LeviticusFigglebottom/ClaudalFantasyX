"""Tests for the Old Kerrid hero build (M3-CHR-505, assets_src/characters/kerrid/).

Run: python3 -m unittest tools.tests.test_kerrid

* Pure-Python checks: every number of kerrid.md §9's params table (and the §1/§4 rule values) in kerrid_params.json;
  the face-pose table against the shared shape API and the sheet's §6.2 table (his rest lid_squint on every row, the
  left cheek ahead in the smiles, no overshoot, the 0.30 s blend, no breath and no tear term); the echo watch of §4.2
  (no hat, mask, eyewear or gourd pieces; no gold anywhere).
* The committed GLBs: budgets and sizes (§8), the mesh names the rig guards use, the Head's 40 shapes and the Cape's
  `cape_wet` key, the rig extras and their parents, the VFX sockets, textures (size cap, power of two, the fibre atlas)
  and materials (the rope-burn glow off by default); the battle hand instance `kerrid_cleaver.glb` (unskinned, the grip
  at its origin) and the battle actor that carries it.
* The M1-CHR-14 rules on the shipped mesh (rig_probe reads the GLB, no Blender): the cape's tier 3 is two halves that
  each follow one leg plus their own panel chain, and the yoke never rides the neck or head; the cleaver rides its own
  prop bone only; the wrap rides the left forearm and hand only; the sandals take the feet's weights; the knees and
  shins under the cape tiers are kept.
"""
import json
import re
import struct
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "characters" / "kerrid"
OUT = ROOT / "assets" / "characters" / "kerrid"
STAGE = ROOT / "game" / "levels" / "_tests" / "characters" / "kerrid"
BATTLE = ROOT / "game" / "characters" / "heroes" / "kerrid_battle.tscn"
for sub in ("kerrid", "ysolde", "villagers", "toma", "rhen", "asha", "base_body"):
    sys.path.insert(0, str(ROOT / "assets_src" / "characters" / sub))
sys.path.insert(0, str(ROOT / "tools" / "dev"))

MAX_BYTES = 5 * 1024 * 1024  # ADR 0005 plain-blob cap; kerrid.md §8.2 (as built: 4,957,016 B, the binding limit)
LOD1_MAX_BYTES = 1_500_000  # kerrid.md §8.2 / pipeline.md §14: under 1.5 MB (as built: 1,477,196 B)
LOD0_MAX = 60_000  # kerrid.md §8.1 target (ceiling 70k); as built 57,987
LOD1_MAX = 30_000  # about 28k; as built 28,514
STANDARD_BONES = 75  # bb_rig.build_game_skeleton's DEF bones (as built: no M1-CHR-15 armpit correctives on him)
PAIRED = ["brow_inner_up", "brow_down", "brow_outer_up", "lid_close", "lid_wide", "lid_squint", "cheek_raise",
          "nose_sneer", "mouth_smile", "mouth_frown", "mouth_stretch", "mouth_dimple"]
SINGLE = ["mouth_press", "mouth_pucker", "lip_upper_up", "lip_lower_down", "jaw_open", "jaw_clench"]
VISEMES = ["vis_rest", "vis_aa", "vis_e", "vis_i", "vis_o", "vis_u", "vis_mbp", "vis_fv", "vis_l", "vis_st"]
API = [f"{b}_{s}" for b in PAIRED for s in ("L", "R")] + SINGLE
# kerrid.md §9: the bb_params block
SHEET_PARAMS = {
    "height_m": 1.86, "heads_tall": 7.41, "shoulder_width_heads": 2.15, "chest_width_heads": 1.45,
    "chest_depth_heads": 1.20, "waist_width_heads": 1.50, "hip_width_heads": 1.55, "crotch_height_heads": 3.45,
    "arm_span_ratio": 1.03, "hand_length_heads": 0.84, "foot_length_ratio": 0.152, "neck_length_heads": 0.38,
    "neck_width_ratio": 0.62, "head_width_ratio": 0.70, "femininity": 0.0, "muscle": 0.60, "mass": 0.45,
    "breast": 0.0, "arm_abduction_deg": 47.0, "skin_hex": "#9A6C50", "eye_scale": 1.10, "ipd_m": 0.066,
    "eye_tilt_deg": 0.0, "canthus_offset_m": 0.0, "jaw_width": 1.02, "cheekbone_height": 0.002,
    "cheekbone_width": 1.08, "chin_size": 1.05, "nose_bridge_width": 1.18, "nose_tip_projection": 0.88,
    "lip_fullness": 0.70, "lip_close": 0.6, "lip_seal": 0.96, "lip_lower_fullness": 0.70, "mouth_corner_lift": -0.001,
    "brow_ridge": 1.12, "donor_mix_african": 0.30, "donor_mix_asian": 0.40, "donor_mix_caucasian": 0.30,
}
# kerrid.md §6.2, before the rest squint is added (a pair is [L, R])
SHEET_FACE = {
    "neutral": {},
    "soft_smile": {"cheek_raise": [0.18, 0.12], "lid_squint": 0.12, "mouth_smile": 0.12},
    "smile": {"cheek_raise": [0.45, 0.35], "lid_squint": 0.35, "mouth_smile": 0.40},
    "laugh": {"cheek_raise": [0.65, 0.55], "lid_squint": 0.55, "mouth_smile": 0.60, "jaw_open": 0.18},
    "worried": {"brow_inner_up": 0.35, "brow_down": 0.30},
    "sad": {"brow_inner_up": 0.45, "lid_close": 0.20, "mouth_frown": 0.15},
    "grief": {"brow_inner_up": 0.80, "brow_down": 0.45, "lid_squint": 0.40, "mouth_frown": 0.35, "jaw_clench": 0.45},
    "angry": {"brow_down": 0.80, "lid_squint": 0.30, "jaw_clench": 0.55, "nose_sneer": 0.10},
    "cold": {"brow_down": 0.30, "mouth_press": 0.35},
    "surprised": {"brow_outer_up": 0.45, "brow_inner_up": 0.30, "lid_wide": 0.25},
    "afraid": {"brow_inner_up": 0.60, "lid_wide": 0.35},
    "determined": {"brow_down": 0.45, "lid_squint": 0.25, "jaw_clench": 0.40},
    "tender": {"brow_inner_up": 0.25, "cheek_raise": [0.12, 0.08], "lid_close": 0.18},
    "guilty": {"brow_inner_up": 0.50, "lid_close": 0.35, "jaw_clench": 0.20},
    "exhausted": {"lid_close": 0.35, "brow_inner_up": 0.15},
}
REST_SQUINT = [0.15, 0.10]  # kerrid.md §6.1: the left eye squints a little more
MESHES = ("Head", "Body", "Burns", "Costume", "Wrap", "Cape", "HairHead", "Cleaver")
EXTRA_BONES = {"DEF-cleaver": "DEF-spine.003"}
for _root, _par, _n in (("DEF-cape_l", "DEF-thigh.L", 3), ("DEF-cape_r", "DEF-thigh.R", 3),
                        ("DEF-cord", "DEF-spine", 3)):
    _chain = [_root] + [f"{_root}.{i:03d}" for i in range(1, _n)]
    EXTRA_BONES[_chain[0]] = _par
    for _a, _b in zip(_chain, _chain[1:]):
        EXTRA_BONES[_b] = _a
SOCKETS = {f"VFX-burn.{s}.{i}": f"DEF-forearm.{s}" for s in ("L", "R") for i in range(1, 7)}
SOCKETS.update({"VFX-palm.L": "DEF-hand.L", "VFX-palm.R": "DEF-hand.R"})


def params() -> dict:
    return json.loads((SRC / "kerrid_params.json").read_text(encoding="utf-8"))


def glb_json(path: Path) -> dict:
    data = path.read_bytes()
    magic, _version, _total = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a GLB"
    length, _kind = struct.unpack("<II", data[12:20])
    return json.loads(data[20:20 + length])


def tris(js: dict) -> int:
    return sum(js["accessors"][p["indices"]]["count"] // 3 for m in js["meshes"] for p in m["primitives"])


def parents(js: dict) -> dict:
    nodes = js["nodes"]
    return {nodes[c]["name"]: nodes[i]["name"] for i, n in enumerate(nodes) for c in n.get("children", [])}


class TestParams(unittest.TestCase):
    def test_every_sheet_number_is_in_the_params(self):
        p = params()
        for key, want in SHEET_PARAMS.items():
            self.assertIn(key, p, key)
            self.assertEqual(p[key], want, key)
        import bb_params

        bb = bb_params.load_params(path=str(SRC / "kerrid_params.json"))
        lm = bb_params.Landmarks(bb)
        self.assertAlmostEqual(bb["height_m"] / lm.h, 7.41, places=2)
        k = p["_kerrid"]
        self.assertEqual((k["nose_break_m"], k["nose_break_side"]), (0.003, "L"))
        self.assertAlmostEqual(k["skin_desaturate"], 0.06)
        self.assertEqual(k["burn_turns"], 3)
        self.assertEqual(k["burn_width_m"], [0.022, 0.03])
        self.assertAlmostEqual(k["hunch_deg"], 8.0)
        self.assertEqual(k["lid_squint_rest"], REST_SQUINT)
        self.assertEqual(k["burn_glow_default"], 0.0)  # §6.1: no glow before Ch10

    def test_m1_chr_14_rules_in_the_parameters(self):
        p = params()
        c, cape, cl = p["_costume"], p["_cape"], p["_cleaver"]
        self.assertGreaterEqual(c["smock_armhole_drop_m"], 0.115)  # §4.1 #1: 12 cm
        self.assertGreaterEqual(c["chest_rope_underarm_drop_m"], 0.115)  # §4.1 #8: 14 cm
        self.assertAlmostEqual(c["chest_rope_off_m"], 0.006)
        self.assertAlmostEqual(c["wrap_off_m"], 0.0025)
        self.assertAlmostEqual(c["trouser_hem_above_ankle_m"], 0.09)
        self.assertAlmostEqual(c["sleeve_end_above_elbow_m"], 0.03)
        self.assertEqual((c["watch_cord_knots"], c["watch_cord_bones"]), (3, 3))
        self.assertGreaterEqual(cape["yoke_neck_clear_m"], 0.025)
        self.assertGreaterEqual(cape["yoke_below_jaw_m"], 0.04)
        self.assertAlmostEqual(cape["yoke_hang_below_shoulder_m"], 0.12)
        self.assertAlmostEqual(cape["tier3_hem_above_floor_m"], 0.52)
        self.assertAlmostEqual(cape["tier3_centre_band_m"], 0.06)
        self.assertEqual(cape["panel_bones"], 3)
        self.assertEqual((cape["wet_longer_m"], cape["wet_closer_m"]), (0.03, 0.015))
        self.assertAlmostEqual(cl["grip_out_m"], 0.012)  # Toma's spear lesson
        self.assertGreaterEqual(cl["cape_clear_m"], 0.012)
        self.assertAlmostEqual(cl["grip_wrap_above_fist_m"], 0.02)
        self.assertEqual((cl["ring_outer_m"], cl["ring_stock_m"]), (0.11, 0.02))
        self.assertEqual((cl["fluke_width_m"], cl["bill_hook_m"]), (0.26, 0.09))
        # the sheet's 1.30 m blade reached the back of the right knee across the back; the build ships 1.00 m (the
        # widths unchanged) with the reason in its _about (kerrid_review.md)
        self.assertAlmostEqual(cl["overall_m"], cl["haft_m"] + cl["blade_m"])
        self.assertAlmostEqual(cl["overall_m"], 1.0)


class TestFacePoses(unittest.TestCase):
    def setUp(self):
        self.poses = json.loads((STAGE / "kerrid_face_poses.json").read_text(encoding="utf-8"))

    def test_every_emotion_with_api_shapes(self):
        tags = {e["id"] for e in json.loads((ROOT / "game/data/dialogue/emotions.json").read_text())["emotions"]}
        self.assertEqual(set(self.poses["emotions"]), tags)
        names = set(PAIRED) | set(SINGLE) | set(API)
        for tag, pose in self.poses["emotions"].items():
            for shape, w in pose.items():
                self.assertIn(shape, names, f"{tag}: {shape}")
                for x in (w if isinstance(w, list) else [w]):
                    self.assertTrue(0.0 <= x <= 1.0, f"{tag}: {shape}")

    def test_follows_the_sheet(self):
        """§6.1/§6.2: the sheet's rows with the rest lid_squint [0.15, 0.10] added to every one; 0.30 s, no
        overshoot."""
        self.assertAlmostEqual(self.poses["blend_in_s"], 0.30)
        self.assertEqual(self.poses["rest"], {"lid_squint": REST_SQUINT})
        self.assertEqual(self.poses["overshoot"], {})
        em = self.poses["emotions"]
        for tag, sheet in SHEET_FACE.items():
            want = {k: v for k, v in sheet.items() if k != "lid_squint"}
            sq = float(sheet.get("lid_squint", 0.0))
            want["lid_squint"] = [sq + REST_SQUINT[0], sq + REST_SQUINT[1]]
            self.assertEqual(set(em[tag]), set(want), tag)
            for shape, w in want.items():
                got = em[tag][shape]
                if isinstance(w, list):
                    self.assertEqual(len(got), 2, f"{tag}: {shape}")
                    for a, b in zip(got, w):
                        self.assertAlmostEqual(a, b, places=6, msg=f"{tag}: {shape}")
                else:
                    self.assertAlmostEqual(got, w, places=6, msg=f"{tag}: {shape}")

    def test_his_tells(self):
        """The left cheek leads every smile (toward the broken side); no breath, sigh or tear terms (§6.2, §12)."""
        em = self.poses["emotions"]
        for tag in ("soft_smile", "smile", "laugh", "tender"):
            l, r = em[tag]["cheek_raise"]
            self.assertGreater(l, r, tag)
        text = json.dumps(em)
        for banned in ("breath", "sigh", "tear"):
            self.assertNotIn(banned, text)
        for tag in ("grief", "angry", "determined", "guilty"):
            self.assertGreater(em[tag]["jaw_clench"], 0.0, tag)  # the feeling is in the jaw


class TestEchoWatch(unittest.TestCase):
    """§4.2: no hat, mask, high collar, eyewear or gourd; no gold anywhere (§7)."""

    def test_no_banned_pieces_or_gold(self):
        import kerrid_costume as C

        names = " ".join(C.ATLAS).lower()
        for banned in ("hat", "mask", "goggle", "glasses", "gourd", "collar", "gold"):
            self.assertNotIn(banned, names)
        for path in (OUT / "kerrid.glb", OUT / "kerrid_lod1.glb"):
            js = glb_json(path)
            text = " ".join([m.get("name", "") for m in js["meshes"]] + [m["name"] for m in js["materials"]]).lower()
            for banned in ("hat", "mask", "goggle", "gourd", "gold"):
                self.assertNotIn(banned, text, path.name)
        for tres in (OUT / "materials").glob("*.tres"):
            self.assertNotIn("gold", tres.stem)


class TestCommitted(unittest.TestCase):
    def test_glbs(self):
        js = glb_json(OUT / "kerrid.glb")
        self.assertLessEqual(tris(js), LOD0_MAX)
        lod = glb_json(OUT / "kerrid_lod1.glb")
        self.assertLessEqual(tris(lod), LOD1_MAX)
        self.assertLess((OUT / "kerrid.glb").stat().st_size, MAX_BYTES)
        self.assertLess((OUT / "kerrid_lod1.glb").stat().st_size, LOD1_MAX_BYTES)
        meshes = {m.get("name") for m in js["meshes"]}
        for n in MESHES:
            if n != "Burns":  # the glow shell's mesh data keeps Body's name; its node is Burns
                self.assertIn(n, meshes)
        node_names = {n.get("name") for n in js["nodes"] if "mesh" in n}
        for n in MESHES:
            self.assertIn(n, node_names)
        lod_nodes = {n.get("name") for n in lod["nodes"] if "mesh" in n}
        for n in ("Cape", "Cleaver", "Burns"):
            self.assertIn(n, lod_nodes)  # the battle actor hides this Cleaver by name
        head = next(m for m in js["meshes"] if m.get("name") == "Head")
        self.assertEqual(head.get("extras", {}).get("targetNames", []), API + VISEMES)
        cape = next(m for m in js["meshes"] if m.get("name") == "Cape")
        self.assertEqual(cape.get("extras", {}).get("targetNames", []), ["cape_wet"])  # §4.1 #10

    def test_rig_extras_and_sockets(self):
        """§9: the cape's tier-3 halves (2 x 3), the watch cord (3) and the cleaver's prop bone, after the 75 standard
        bones, in both LODs; the VFX sockets are empties on the forearms and hands, not joints."""
        js = glb_json(OUT / "kerrid.glb")
        nodes = js["nodes"]
        joints = [nodes[i]["name"] for i in js["skins"][0]["joints"]]
        par = parents(js)
        for name, want in EXTRA_BONES.items():
            self.assertIn(name, joints)
            self.assertEqual(par[name], want, name)
        standard = [j for j in joints if j not in EXTRA_BONES]
        self.assertEqual(len(standard), STANDARD_BONES)
        self.assertEqual(len(joints), STANDARD_BONES + len(EXTRA_BONES))  # 85
        lod = glb_json(OUT / "kerrid_lod1.glb")
        self.assertEqual([lod["nodes"][i]["name"] for i in lod["skins"][0]["joints"]], joints)
        for name, want in SOCKETS.items():
            self.assertNotIn(name, joints)
            self.assertEqual(par.get(name), want, name)

    def test_materials_and_textures(self):
        from PIL import Image

        js = glb_json(OUT / "kerrid.glb")
        mats = {m["name"] for m in js["materials"]}
        have = {p.stem for p in (OUT / "materials").glob("*.tres")}
        self.assertEqual(mats - have, set(), "every glTF material has a hero material")
        for want in ("cape_mat", "fibre", "cleaver", "cloth", "hair", "hair_grey", "beard", "beard_grey", "burn_glow"):
            self.assertIn(want, mats)
        for variant in ("cape_mat_wet", "fibre_wet", "skin_head_dialogue"):
            self.assertIn(variant, have)  # §4.1 #10 (the wet cape) and the ADR 0019 dialogue finish
        pngs = sorted((OUT / "textures").glob("*.png"))
        self.assertEqual(len(pngs), 17)
        for png in pngs:
            self.assertLess(png.stat().st_size, MAX_BYTES, png.name)
            with Image.open(png) as im:
                w, h = im.size
            self.assertEqual(w & (w - 1), 0, png.name)
            self.assertEqual(h & (h - 1), 0, png.name)
        with Image.open(OUT / "textures" / "kerrid_fibre.png") as im:
            self.assertEqual((im.size, im.mode), ((2048, 2048), "RGBA"))  # §8.2: the strand atlas with alpha
        with Image.open(OUT / "textures" / "kerrid_body_albedo.png") as im:
            self.assertEqual(im.size, (2048, 2048))  # §8.2: the rope-burn spiral needs >= 10 px/cm on the forearms
        for tres in (OUT / "materials").glob("*.tres"):
            for path in re.findall(r'path="res://([^"]+)"', tres.read_text(encoding="utf-8")):
                self.assertTrue((ROOT / path).exists(), f"{tres.name}: {path}")
        glow = (OUT / "materials" / "burn_glow.tres").read_text(encoding="utf-8")
        self.assertIn("emission_enabled = true", glow)
        self.assertRegex(glow, r"emission_energy_multiplier = 0(\.0+)?\n")  # off by default (Ch5-Ch9)

    def test_cleaver_hand_instance(self):
        """§9 Battle actor: the cleaver alone, unskinned, in its own frame with the right fist's grip point at the
        origin (+X down the haft to the tip, the ring end behind the grip)."""
        js = glb_json(OUT / "kerrid_cleaver.glb")
        self.assertEqual([n["name"] for n in js["nodes"]], ["CleaverHand"])
        self.assertNotIn("skins", js)
        self.assertEqual([m["name"] for m in js["materials"]], ["cleaver"])
        node = js["nodes"][0]
        self.assertEqual(node.get("translation", [0.0, 0.0, 0.0]), [0.0, 0.0, 0.0])
        acc = js["accessors"][js["meshes"][0]["primitives"][0]["attributes"]["POSITION"]]
        lo, hi = np.array(acc["min"]), np.array(acc["max"])
        self.assertTrue((lo < 0.0).all() and (hi > 0.0).all())  # the origin is inside the haft's box
        cl = params()["_cleaver"]
        self.assertGreater(float(hi[0]), cl["blade_m"])  # the tip, a blade's length down +X from the grip
        self.assertLess(float(lo[0]), 0.0)  # the haft's end and the ring behind the fist
        self.assertAlmostEqual(float(hi[1] - lo[1]), cl["ring_stock_m"] * 2, delta=0.005)  # thinnest across Y
        self.assertLessEqual(tris(js), 2_400)  # §8.1

    def test_battle_actor(self):
        """§9: the LOD1 model, its back cleaver hidden, the hand instance on a BoneAttachment3D to DEF-hand.R."""
        text = BATTLE.read_text(encoding="utf-8")
        self.assertIn('path="res://assets/characters/kerrid/kerrid_lod1.glb"', text)
        self.assertIn('path="res://assets/characters/kerrid/kerrid_cleaver.glb"', text)
        self.assertIn('metadata/hymn_battle_actor = &"kerrid"', text)
        self.assertRegex(text, r'\[node name="Cleaver" parent="Model/[^"]+"[^\]]*\]\nvisible = false')
        self.assertRegex(text, r'type="BoneAttachment3D"[^\]]*\]\nbone_name = "DEF-hand.R"')


class TestRigRules(unittest.TestCase):
    """The M1-CHR-14 rules on the shipped GLB (no Blender)."""

    @classmethod
    def setUpClass(cls):
        import rig_probe

        cls.rp = rig_probe
        cls.rig = rig_probe.Rig("kerrid")
        cls.names = cls.rig.joint_names

    def dominant(self, part) -> np.ndarray:
        return np.array([self.names[part.J[i][int(np.argmax(part.W[i]))]] for i in range(len(part.P))])

    def bones_of(self, part) -> set:
        return {self.names[j] for j, w in zip(part.J.ravel(), part.W.ravel()) if w > 1e-4}

    def test_cape_halves_follow_one_leg_each_with_their_own_chain(self):
        cape = self.rig.part("Cape")
        J, Wt = cape.J, cape.W
        # §4.1 #7: the left/right blend lives only in the 6 cm centre band (plus the strands' 5 mm sway off the mat)
        band = params()["_cape"]["tier3_centre_band_m"] / 2 + 0.005
        for side, other in (("l", "R"), ("r", "L")):
            chain = {f"DEF-cape_{side}", f"DEF-cape_{side}.001", f"DEF-cape_{side}.002"}
            on = np.array([any(self.names[J[i, k]] in chain and Wt[i, k] > 1e-4 for k in range(J.shape[1]))
                           for i in range(len(cape.P))])
            self.assertGreater(int(on.sum()), 100, side)
            # outside the band a half never takes the other leg (two halves, not a tube)
            leg = {f"DEF-thigh.{other}", f"DEF-thigh.{other}.001", f"DEF-shin.{other}", f"DEF-shin.{other}.001",
                   f"DEF-cape_{'r' if side == 'l' else 'l'}"}
            for i in np.nonzero(on & (np.abs(cape.P[:, 0]) > band))[0]:
                for k in range(J.shape[1]):
                    if Wt[i, k] > 1e-4:
                        self.assertNotIn(self.names[J[i, k]], leg, f"half {side} on {self.names[J[i, k]]}")

    def test_the_yoke_never_rides_the_neck_or_head(self):
        bones = self.bones_of(self.rig.part("Cape"))
        for b in ("DEF-spine.005", "DEF-spine.006"):
            self.assertNotIn(b, bones)

    def test_cleaver_rides_its_prop_bone_only(self):
        self.assertEqual(self.bones_of(self.rig.part("Cleaver")), {"DEF-cleaver"})

    def test_wrap_rides_the_left_forearm_and_hand(self):
        bones = self.bones_of(self.rig.part("Wrap"))
        self.assertIn("DEF-forearm.L", bones)
        self.assertIn("DEF-hand.L", bones)
        self.assertFalse(any(b.endswith(".R") for b in bones), bones)
        dom = self.dominant(self.rig.part("Wrap"))
        self.assertGreater(float(np.mean([d.startswith(("DEF-forearm.L", "DEF-hand.L")) for d in dom])), 0.75)

    def test_sandals_take_the_feet_weights(self):
        cost = self.rig.part("Costume")
        low = cost.P[:, 1] < 0.05  # glTF: +Y up; the rope soles and their ties
        dom = self.dominant(cost)[low]
        self.assertGreater(int(low.sum()), 200)
        self.assertTrue(all(d.startswith(("DEF-foot", "DEF-toe")) for d in dom), set(dom))

    def test_knees_and_shins_are_kept_under_the_cape(self):
        body = self.rig.part("Body")
        dom = self.dominant(body)
        knee = float(self.rig.skeleton.g_t["DEF-shin.L"][1])
        for side in ("L", "R"):
            near = (np.abs(body.P[:, 1] - knee) < 0.04) & np.array([d.startswith(f"DEF-shin.{side}") or
                                                                    d.startswith(f"DEF-thigh.{side}") for d in dom])
            self.assertGreater(int(near.sum()), 30, side)

    def test_the_guards_config(self):
        cfg = json.loads((ROOT / "tools/dev/rig_checks.json").read_text())["heroes"]["kerrid"]
        self.assertEqual(cfg["garments"], ["Costume", "Wrap"])
        self.assertEqual(cfg["props"], ["Cleaver"])
        self.assertEqual(cfg["hidden_props"], {"Cleaver": "battle"})  # the battle actor hides the back cleaver


if __name__ == "__main__":
    unittest.main()
