"""Tests for the Pell hero build (M3-CHR-506, assets_src/characters/pell/).

Run: python3 -m unittest tools.tests.test_pell

* Pure-Python checks: pell.md §1 and §9's body and Kirru numbers in pell_params.json, and the M1-CHR-14 rule values of
  §4; the face-pose table against the sheet's §6.2 (with its crest column, the 0.25 s onset); the echo watch of §2 and
  §7 (no horn, mane, gold or metal, no blue); the name-shell motif data.
* The committed GLBs: budgets and sizes (§8), the mesh names the rig guards and the battle actor use, the Head's 40
  shapes and the Crest's two keys, the rig extras and their parents, textures (size cap, power of two) and materials;
  the battle actor (LOD1, the blank shell showing).
* The M1-CHR-14 rules on the shipped mesh (rig_probe reads the GLB, no Blender): the staff rides its own prop bone under
  the left hand; the name-shell and its cord ride the neck's base only; the wraps ride the forearms and hands; the
  mantle never rides the neck or head, and its arm band takes the right upper arm; the crest stays outside the head in
  both of its keys (rig_probe applies no morph targets, so this is its `crest_raise` stage pose).
"""
import json
import re
import struct
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "characters" / "pell"
OUT = ROOT / "assets" / "characters" / "pell"
STAGE = ROOT / "game" / "levels" / "_tests" / "characters" / "pell"
BATTLE = ROOT / "game" / "characters" / "heroes" / "pell_battle.tscn"
for sub in ("pell", "ysolde", "toma", "rhen", "asha", "base_body"):
    sys.path.insert(0, str(ROOT / "assets_src" / "characters" / sub))
sys.path.insert(0, str(ROOT / "tools" / "dev"))

MAX_BYTES = 5 * 1024 * 1024  # ADR 0005 plain-blob cap (pell.md §8.2)
LOD1_MAX_BYTES = 1_500_000  # pell.md §8.2 / pipeline.md §14
LOD0_MAX = 62_000  # pell.md §8.1 target (ceiling 70k)
LOD1_MAX = 30_000  # about 28k
STANDARD_BONES = 77  # bb_rig's 75 DEF bones plus the M1-CHR-15 armpit correctives
PAIRED = ["brow_inner_up", "brow_down", "brow_outer_up", "lid_close", "lid_wide", "lid_squint", "cheek_raise",
          "nose_sneer", "mouth_smile", "mouth_frown", "mouth_stretch", "mouth_dimple"]
SINGLE = ["mouth_press", "mouth_pucker", "lip_upper_up", "lip_lower_down", "jaw_open", "jaw_clench"]
VISEMES = ["vis_rest", "vis_aa", "vis_e", "vis_i", "vis_o", "vis_u", "vis_mbp", "vis_fv", "vis_l", "vis_st"]
API = [f"{b}_{s}" for b in PAIRED for s in ("L", "R")] + SINGLE
# pell.md §9: the bb_params block (the look-dev review of M3-CHR-506 took the eyes smaller, 0.85, and the neck thicker,
# 0.55; the head's own shape is `_kirru.otter_head`)
SHEET_PARAMS = {
    "height_m": 2.3, "heads_tall": 8.36, "shoulder_width_heads": 1.55, "chest_width_heads": 1.12,
    "chest_depth_heads": 0.95, "waist_width_heads": 0.95, "hip_width_heads": 1.15, "crotch_height_heads": 4.05,
    "arm_span_ratio": 1.07, "hand_length_heads": 0.95, "foot_length_ratio": 0.17, "neck_length_heads": 0.95,
    "neck_width_ratio": 0.55, "head_width_ratio": 0.52, "femininity": 0.0, "muscle": 0.3, "mass": 0.05,
    "eye_scale": 0.85, "ipd_m": 0.07, "skin_hex": "#3B2B22", "jaw_width": 0.8, "cheekbone_width": 0.92,
    "chin_size": 0.8, "nose_bridge_width": 1.1, "lip_fullness": 0.55, "lip_close": 0.7, "lip_seal": 0.98,
    "lip_lower_fullness": 0.55, "brow_ridge": 0.95, "donor_mix_african": 0.34, "donor_mix_asian": 0.33,
    "donor_mix_caucasian": 0.33,
}
SHEET_KIRRU = {"muzzle_m": 0.055, "nose_pad_width_m": 0.032, "ear_scale": 0.55, "cranium_length": 1.08,
               "eye_fissure_m": 0.032, "eye_roundness": 0.7, "neck_s_deg": [20.0, -15.0], "web_depth": 0.5}
# pell.md §6.2 (a pair is [L, R]) and its crest column
SHEET_FACE = {
    "neutral": {},
    "soft_smile": {"mouth_smile": [0.12, 0.14], "cheek_raise": 0.12, "lid_squint": 0.08},
    "smile": {"mouth_smile": [0.32, 0.37], "cheek_raise": 0.30, "lid_squint": 0.18},
    "laugh": {"mouth_smile": [0.50, 0.58], "cheek_raise": 0.50, "lid_squint": 0.40, "jaw_open": 0.10},
    "worried": {"brow_inner_up": 0.40, "brow_down": 0.15},
    "sad": {"brow_inner_up": 0.40, "lid_close": 0.25, "mouth_frown": 0.20},
    "grief": {"brow_inner_up": 0.75, "brow_down": 0.30, "lid_close": 0.40, "mouth_frown": 0.40, "jaw_clench": 0.15,
              "crest_flat": 0.4},
    "angry": {"brow_down": 0.60, "lid_squint": 0.30, "nose_sneer": 0.25},
    "cold": {"brow_down": 0.20, "lid_close": 0.15, "mouth_press": 0.25},
    "surprised": {"brow_inner_up": 0.35, "brow_outer_up": 0.50, "lid_wide": 0.35},
    "afraid": {"brow_inner_up": 0.60, "lid_wide": 0.45, "mouth_stretch": 0.15},
    "determined": {"brow_down": 0.35, "lid_squint": 0.20, "mouth_press": 0.30},
    "tender": {"brow_inner_up": 0.25, "mouth_smile": [0.10, 0.12], "lid_close": 0.20},
    "guilty": {"brow_inner_up": 0.45, "lid_close": 0.35, "mouth_press": 0.20},
    "exhausted": {"lid_close": 0.40, "brow_inner_up": 0.15},
}
SHEET_CREST = {"neutral": 0.10, "soft_smile": 0.15, "smile": 0.25, "laugh": 0.35, "worried": 0.30, "sad": 0.0,
               "grief": 0.0, "angry": 0.70, "cold": 0.05, "surprised": 0.85, "afraid": 0.90, "determined": 0.55,
               "tender": 0.05, "guilty": 0.0, "exhausted": 0.0}
MESHES = ("Head", "Body", "Costume", "Wraps", "Fur", "Webs", "Crest", "Staff", "NameShell", "NameShellBlank",
          "NameShellCarved")
EXTRA_BONES = {"DEF-staff": "DEF-hand.L", "DEF-armpit.L": "DEF-shoulder.L", "DEF-armpit.R": "DEF-shoulder.R",
               "DEF-mantle_f": "DEF-spine.003", "DEF-mantle_f.001": "DEF-mantle_f",
               "DEF-mantle_b": "DEF-spine.003", "DEF-mantle_b.001": "DEF-mantle_b"}
CREST_CLEAR_M = -0.006  # the crest's deepest point under the head's skin, any key: the roots are set into the fur (as built 4.4 mm)


def params() -> dict:
    return json.loads((SRC / "pell_params.json").read_text(encoding="utf-8"))


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
        for key, want in SHEET_KIRRU.items():
            self.assertEqual(p["_kirru"][key], want, key)
        import bb_params

        bb = bb_params.load_params(path=str(SRC / "pell_params.json"))
        lm = bb_params.Landmarks(bb)
        self.assertAlmostEqual(bb["height_m"] / lm.h, 8.36, places=2)
        pr = p["_proportions"]
        self.assertEqual((pr["idle_sway"], pr["breath"], pr["feet_spacing_shoulders"]), (0.15, 0.8, 0.9))

    def test_m1_chr_14_rules_in_the_parameters(self):
        p = params()
        c, st, sh = p["_costume"], p["_staff"], p["_shell"]
        self.assertGreaterEqual(c["mantle_arm_drop_m"], 0.115)  # §4.1 #1: the arm edge under the shoulder joint
        self.assertGreaterEqual(c["cord_underarm_drop_m"], 0.115)  # §4.1 #2: the cord under the left arm
        self.assertGreaterEqual(sh["cord_clear_m"], 0.01)  # §4.1 #3: the shell's cord off the neck
        self.assertAlmostEqual(st["grip_out_m"], 0.012)  # Toma's spear lesson: 1.2 cm off the grip
        self.assertGreaterEqual(st["grip_clear_m"], 0.05)  # no lashing or node in the grip
        self.assertGreater(st["staff_m"], p["_proportions"]["crest_tip_height_m"])  # it stands above the crest


class TestFacePoses(unittest.TestCase):
    def setUp(self):
        self.poses = json.loads((STAGE / "pell_face_poses.json").read_text(encoding="utf-8"))

    def test_every_emotion_with_api_shapes(self):
        tags = {e["id"] for e in json.loads((ROOT / "game/data/dialogue/emotions.json").read_text())["emotions"]}
        self.assertEqual(set(self.poses["emotions"]), tags)
        names = set(PAIRED) | set(SINGLE) | set(API) | {"crest_raise", "crest_flat"}
        for tag, pose in self.poses["emotions"].items():
            for shape, w in pose.items():
                self.assertIn(shape, names, f"{tag}: {shape}")
                for x in (w if isinstance(w, list) else [w]):
                    self.assertTrue(0.0 <= x <= 1.0, f"{tag}: {shape}")

    def test_follows_the_sheet(self):
        """§6.2: the sheet's rows and their crest column; the slower blend and the crest's lead (§6.1)."""
        self.assertAlmostEqual(self.poses["onset_delay_s"], 0.25)
        self.assertEqual(self.poses["overshoot"], {})
        self.assertEqual(self.poses["crest"], SHEET_CREST)
        em = self.poses["emotions"]
        for tag, sheet in SHEET_FACE.items():
            want = dict(sheet, crest_raise=SHEET_CREST[tag])
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
        """The mouth almost never opens (laugh's 0.10 at most); no tear layer (§6.2, §12 carried with its default)."""
        em = self.poses["emotions"]
        for tag, pose in em.items():
            self.assertLessEqual(pose.get("jaw_open", 0.0), 0.10, tag)
        self.assertNotIn("tear", json.dumps(em))


class TestEchoWatch(unittest.TestCase):
    """§2 and §7: no horn, mane, tail, lower garment or footwear piece; no gold, no metal, no blue."""

    def test_no_banned_pieces_or_finishes(self):
        import pell_costume as C

        names = " ".join(C.ATLAS).lower()
        for banned in ("horn", "mane", "tail", "boot", "sandal", "skirt", "trouser", "gold", "metal", "blue"):
            self.assertNotIn(banned, names)
        for path in (OUT / "pell.glb", OUT / "pell_lod1.glb"):
            js = glb_json(path)
            text = " ".join([m.get("name", "") for m in js["meshes"]] + [m["name"] for m in js["materials"]]).lower()
            for banned in ("horn", "mane", "tail", "gold", "metal"):
                self.assertNotIn(banned, text, path.name)
        for tres in (OUT / "materials").glob("*.tres"):
            text = tres.read_text(encoding="utf-8")
            self.assertNotIn("gold", tres.stem)
            m = re.search(r"metallic = ([0-9.]+)", text)
            self.assertTrue(m is None or float(m.group(1)) == 0.0, tres.name)

    def test_the_name_carving_is_data(self):
        """§3: the carved shell's spiral of notches comes from motifs/pell_name.json (long and short notches)."""
        name = json.loads((SRC / "motifs" / "pell_name.json").read_text(encoding="utf-8"))
        self.assertTrue(set(name["sequence"]) <= {"L", "S"})
        self.assertGreater(len(name["sequence"]), 8)


class TestCommitted(unittest.TestCase):
    def test_glbs(self):
        js = glb_json(OUT / "pell.glb")
        self.assertLessEqual(tris(js), LOD0_MAX)
        lod = glb_json(OUT / "pell_lod1.glb")
        self.assertLessEqual(tris(lod), LOD1_MAX)
        self.assertGreater(tris(lod), 0.8 * 28_000)  # about 28k: the long fingers and the crest's outline kept
        self.assertLess((OUT / "pell.glb").stat().st_size, MAX_BYTES)
        self.assertLess((OUT / "pell_lod1.glb").stat().st_size, LOD1_MAX_BYTES)
        for doc in (js, lod):
            node_names = {n.get("name") for n in doc["nodes"] if "mesh" in n}
            for n in MESHES:
                self.assertIn(n, node_names)  # the battle actor and PellNameShell find these by name
        head = next(m for m in js["meshes"] if m.get("name") == "Head")
        self.assertEqual(head.get("extras", {}).get("targetNames", []), API + VISEMES)
        crest = next(m for m in js["meshes"] if m.get("name") == "Crest")
        self.assertEqual(crest.get("extras", {}).get("targetNames", []), ["crest_raise", "crest_flat"])
        # the LOD1 has no shape keys: its crest is baked at the battle idle's `battle_raise` (pell.md §10.3), so it
        # stands higher than the LOD0's rest crest
        lc = next(m for m in lod["meshes"] if m.get("name") == "Crest")
        self.assertNotIn("targets", lc["primitives"][0])
        top = js["accessors"][crest["primitives"][0]["attributes"]["POSITION"]]["max"][1]
        lod_top = lod["accessors"][lc["primitives"][0]["attributes"]["POSITION"]]["max"][1]
        self.assertAlmostEqual(params()["_crest"]["battle_raise"], 0.3)
        self.assertGreater(lod_top, top)

    def test_rig_extras(self):
        """§9: the staff's prop bone under the left hand, the armpit correctives, the mantle's two panel chains, after
        the standard bones, in both LODs."""
        js = glb_json(OUT / "pell.glb")
        nodes = js["nodes"]
        joints = [nodes[i]["name"] for i in js["skins"][0]["joints"]]
        par = parents(js)
        for name, want in EXTRA_BONES.items():
            self.assertIn(name, joints)
            self.assertEqual(par[name], want, name)
        self.assertEqual(len(joints), STANDARD_BONES + len(EXTRA_BONES) - 2)  # the armpit pair is in the 77
        lod = glb_json(OUT / "pell_lod1.glb")
        self.assertEqual([lod["nodes"][i]["name"] for i in lod["skins"][0]["joints"]], joints)

    def test_materials_and_textures(self):
        from PIL import Image

        js = glb_json(OUT / "pell.glb")
        mats = {m["name"] for m in js["materials"]}
        have = {p.stem for p in (OUT / "materials").glob("*.tres")}
        self.assertEqual(mats - have, set(), "every glTF material has a hero material")
        for want in ("fur", "whisker", "crest", "cloth", "web", "fur_brow"):
            self.assertIn(want, mats)
        for variant in ("skin_head_wet", "skin_body_wet", "fur_wet", "crest_wet", "skin_head_dialogue"):
            self.assertIn(variant, have)  # §5 the Ch8 storm's wet state and the ADR 0019 dialogue finish
        pngs = sorted((OUT / "textures").glob("*.png"))
        self.assertEqual(len(pngs), 14)
        for png in pngs:
            self.assertLess(png.stat().st_size, MAX_BYTES, png.name)
            with Image.open(png) as im:
                w, h = im.size
            self.assertEqual(w & (w - 1), 0, png.name)
            self.assertEqual(h & (h - 1), 0, png.name)
        for tres in (OUT / "materials").glob("*.tres"):
            for path in re.findall(r'path="res://([^"]+)"', tres.read_text(encoding="utf-8")):
                self.assertTrue((ROOT / path).exists(), f"{tres.name}: {path}")

    def test_battle_actor(self):
        """pipeline.md §14: the LOD1 model with the blank shell showing (PellNameShell's default)."""
        text = BATTLE.read_text(encoding="utf-8")
        self.assertIn('path="res://assets/characters/pell/pell_lod1.glb"', text)
        self.assertIn('metadata/hymn_battle_actor = &"pell"', text)
        self.assertRegex(text, r'\[node name="NameShellCarved" parent="Model/[^"]+"[^\]]*\]\nvisible = false')
        self.assertNotIn('name="NameShellBlank"', text)

    def test_the_stage_shows_one_shell(self):
        text = (STAGE / "pell_stage.tscn").read_text(encoding="utf-8")
        self.assertIn('hide_nodes = Array[StringName]([&"NameShellCarved"])', text)


class TestRigRules(unittest.TestCase):
    """The M1-CHR-14 rules on the shipped GLB (no Blender)."""

    @classmethod
    def setUpClass(cls):
        import rig_probe

        cls.rig = rig_probe.Rig("pell")
        cls.names = cls.rig.joint_names

    def bones_of(self, part) -> set:
        return {self.names[j] for j, w in zip(part.J.ravel(), part.W.ravel()) if w > 1e-4}

    def test_the_staff_rides_its_prop_bone_under_the_left_hand(self):
        self.assertEqual(self.bones_of(self.rig.part("Staff")), {"DEF-staff"})

    def test_the_shell_and_its_cord_ride_the_neck_base(self):
        for name in ("NameShell", "NameShellBlank", "NameShellCarved"):
            self.assertEqual(self.bones_of(self.rig.part(name)), {"DEF-spine.004"}, name)

    def test_the_wraps_ride_the_forearms_and_hands(self):
        bones = self.bones_of(self.rig.part("Wraps"))
        self.assertTrue(all(b.startswith(("DEF-forearm", "DEF-hand")) for b in bones), bones)
        for side in "LR":
            self.assertIn(f"DEF-forearm.{side}", bones)

    def test_the_mantle_spares_the_neck_and_takes_the_right_arm(self):
        bones = self.bones_of(self.rig.part("Costume"))
        for b in ("DEF-spine.005", "DEF-spine.006"):
            self.assertNotIn(b, bones)
        self.assertIn("DEF-upper_arm.R", bones)  # §4.1 #1: the arm band
        self.assertNotIn("DEF-upper_arm.L", bones)  # the left arm is bare (the cord passes under it)

    def test_the_girdle_panels_each_follow_one_thigh(self):
        """pell.md §4.2's fallback (look-dev review): the girdle's four panels are split, so no vertex takes both
        thighs (nothing tube-like below the hips, M1-CHR-14), and its hem rides the thighs."""
        cost = self.rig.part("Costume")
        low = (cost.P[:, 1] < 1.08) & (cost.P[:, 1] > 0.5)  # under the belt, above the ankle cord
        self.assertGreater(int(low.sum()), 100)
        for i in np.nonzero(low)[0]:
            on = {self.names[j] for j, w in zip(cost.J[i], cost.W[i]) if w > 1e-4}
            self.assertFalse(any(b.endswith(".L") for b in on) and any(b.endswith(".R") for b in on), on)
        hem = low & (cost.P[:, 1] < float(np.percentile(cost.P[low, 1], 20)))
        for i in np.nonzero(hem)[0]:
            dom = self.names[cost.J[i][int(np.argmax(cost.W[i]))]]
            self.assertTrue(dom.startswith("DEF-thigh"), dom)

    def test_the_crest_rides_the_head(self):
        """The Crest is skinned rigidly to the head bone (it was once exported unskinned and floated in the clips)."""
        self.assertEqual(self.bones_of(self.rig.part("Crest")), {"DEF-spine.006"})

    def test_the_crest_stays_outside_the_head_in_both_keys(self):
        import asha_glb
        import rig_probe

        js, bin_ = asha_glb.read_glb(OUT / "pell.glb")
        crest = asha_glb.mesh_by_name(js, "Crest")["primitives"]
        head = self.rig.part("Head:skin_head")
        surf = rig_probe.Surface(rig_probe.Topology(head.F, head.P), head.P)
        for key in (None, 0, 1):  # rest, crest_raise, crest_flat
            for prim in crest:
                P = asha_glb.accessor(js, bin_, prim["attributes"]["POSITION"]).astype(float)
                if key is not None:
                    P = P + asha_glb.accessor(js, bin_, prim["targets"][key]["POSITION"]).astype(float)
                hit = surf.query(P)
                inside = (hit.sd < CREST_CLEAR_M) & (hit.facing > 0.8)  # past an open boundary is not inside
                self.assertFalse(bool(inside.any()), f"crest key {key}: {float(hit.sd.min()):.4f} m")

    def test_the_guards_config(self):
        cfg = json.loads((ROOT / "tools/dev/rig_checks.json").read_text())["heroes"]["pell"]
        self.assertEqual(cfg["garments"], ["Costume", "Wraps", "Crest"])
        self.assertEqual(cfg["props"], ["Staff", "NameShell", "NameShellBlank", "NameShellCarved"])


if __name__ == "__main__":
    unittest.main()
