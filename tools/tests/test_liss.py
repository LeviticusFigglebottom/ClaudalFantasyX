"""Tests for the Liss Varrow hero build (M3-CHR-03, assets_src/characters/liss/).

Run: python3 -m unittest tools.tests.test_liss

* Pure-Python checks: every number of act1_npcs.md §2.1 and §2.10 in liss_params.json; the face-pose table against
  the shared shape API and the sheet's §2.6 table (her rest brow_down on every row, the left-sided smile, the sneer
  past 0.3, the fastest blend in the party, the widest grief stretch of any table); the line-mark generator (eleven
  marks, right side only, the eleventh and newest on the cheek, the stroke sizes); the echo watch (no goggles, no
  skirt, no yellow in her cloth atlas).
* The committed GLBs: budgets and sizes, the mesh names the rig guards use, the Head's 40 shapes, the rig extras and
  their parents, textures (size cap, power of two, the 2K body albedo for the arm's marks) and materials.
* The M1-CHR-14 rules on the shipped mesh (rig_probe reads the GLB, no Blender): the coat's back is two tails that
  each follow one leg plus their own bone chain; the torso cloth's armholes are dropped at least 11.5 cm; the
  copper-mesh sleeve and glove ride the left arm's chain and fingers; the launcher sits 2 cm off the thigh on its own
  prop bone; the boots take the feet's weights; the knees and shins under the tails and trousers are kept; the
  beaded tail is a two-strand braid seated on the scalp, checked as a braid by the rig guards.
"""
import colorsys
import json
import struct
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "characters" / "liss"
OUT = ROOT / "assets" / "characters" / "liss"
STAGE = ROOT / "game" / "levels" / "_tests" / "characters" / "liss"
for sub in ("liss", "ysolde", "toma", "rhen", "asha", "base_body"):
    sys.path.insert(0, str(ROOT / "assets_src" / "characters" / sub))
sys.path.insert(0, str(ROOT / "tools" / "dev"))

MAX_BYTES = 5 * 1024 * 1024  # ADR 0005 plain-blob cap
LOD1_MAX_BYTES = int(1.5 * 1024 * 1024)  # pipeline.md §14
LOD0_MAX = 60_000  # act1_npcs.md §2.9 target (ceiling 70k)
LOD1_MAX = 30_000  # about 28k
PAIRED = ["brow_inner_up", "brow_down", "brow_outer_up", "lid_close", "lid_wide", "lid_squint", "cheek_raise",
          "nose_sneer", "mouth_smile", "mouth_frown", "mouth_stretch", "mouth_dimple"]
SINGLE = ["mouth_press", "mouth_pucker", "lip_upper_up", "lip_lower_down", "jaw_open", "jaw_clench"]
VISEMES = ["vis_rest", "vis_aa", "vis_e", "vis_i", "vis_o", "vis_u", "vis_mbp", "vis_fv", "vis_l", "vis_st"]
API = [f"{b}_{s}" for b in PAIRED for s in ("L", "R")] + SINGLE
# act1_npcs.md §2.10: the bb_params block
SHEET_PARAMS = {
    "height_m": 1.56, "heads_tall": 7.0, "shoulder_width_heads": 1.60, "chest_width_heads": 1.20,
    "chest_depth_heads": 0.86, "waist_width_heads": 1.05, "hip_width_heads": 1.32, "crotch_height_heads": 3.4,
    "arm_span_ratio": 1.01, "hand_length_heads": 0.80, "neck_length_heads": 0.40, "neck_width_ratio": 0.5,
    "head_width_ratio": 0.67, "femininity": 0.85, "muscle": 0.55, "mass": 0.12, "breast": 0.25, "eye_scale": 1.10,
    "ipd_m": 0.061, "eye_tilt_deg": 2.0, "jaw_width": 0.92, "cheekbone_height": 0.003, "cheekbone_width": 1.06,
    "chin_size": 0.90, "nose_bridge_width": 0.96, "nose_tip_projection": 0.98, "lip_fullness": 0.75,
    "lip_close": 0.6, "lip_seal": 0.96, "lip_lower_fullness": 0.7, "mouth_corner_lift": 0.0, "brow_ridge": 1.0,
    "donor_mix_african": 0.3, "donor_mix_asian": 0.35, "donor_mix_caucasian": 0.35, "skin_hex": "#A2765A",
}
MESHES = ("Head", "Body", "Costume", "WorkSleeve", "HairHead", "HairTail", "Launcher")
EXTRA_BONES = {"DEF-launcher": "DEF-spine"}
for _root, _par, _n in (("DEF-coat_tail_l", "DEF-thigh.L", 3), ("DEF-coat_tail_r", "DEF-thigh.R", 3),
                        ("DEF-hair_tail", "DEF-spine.006", 6)):
    _chain = [_root] + [f"{_root}.{i:03d}" for i in range(1, _n)]
    EXTRA_BONES[_chain[0]] = _par
    for _a, _b in zip(_chain, _chain[1:]):
        EXTRA_BONES[_b] = _a


def params() -> dict:
    return json.loads((SRC / "liss_params.json").read_text(encoding="utf-8"))


def glb_json(path: Path) -> dict:
    data = path.read_bytes()
    magic, _version, _total = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a GLB"
    length, _kind = struct.unpack("<II", data[12:20])
    return json.loads(data[20:20 + length])


def tris(js: dict) -> int:
    return sum(js["accessors"][p["indices"]]["count"] // 3 for m in js["meshes"] for p in m["primitives"])


def landmarks():
    import bb_donor
    import bb_params

    return bb_donor.fit(bb_params.load_params(path=str(SRC / "liss_params.json"))).lm


class TestParams(unittest.TestCase):
    def test_every_sheet_number_is_in_the_params(self):
        p = params()
        for key, want in SHEET_PARAMS.items():
            self.assertIn(key, p, key)
            self.assertEqual(p[key], want, key)
        import bb_params

        bb = bb_params.load_params(path=str(SRC / "liss_params.json"))
        lm = bb_params.Landmarks(bb)
        self.assertAlmostEqual(bb["height_m"] / lm.h, 7.0, places=2)
        fig = p["_figure"]
        self.assertEqual((fig["lean_deg"], fig["knee_deg"], fig["stance"], fig["head_down_deg"]), (6.0, 9.0, 1.1, 4.0))
        self.assertAlmostEqual(fig["idle_sway"], 1.2)
        self.assertEqual(fig["iris_hex"], "#4E4A2C")
        self.assertAlmostEqual(fig["rest_brow_down"], 0.08)
        self.assertAlmostEqual(fig["blend_in_s"], 0.10)

    def test_m1_chr_14_rules_in_the_parameters(self):
        p = params()
        c, h = p["_costume"], p["_hair"]
        self.assertGreaterEqual(c["top_armhole_drop_m"], 0.115)
        self.assertGreaterEqual(c["coat_armhole_drop_m"], 0.115)
        self.assertAlmostEqual(c["launcher_thigh_gap_m"], 0.02)
        self.assertEqual(c["coat_tail_bones"], 3)
        self.assertEqual(h["tail_bones"], 6)
        self.assertAlmostEqual(h["tail_card_stop_m"], 0.012)
        self.assertEqual(c["launcher_box_m"], [0.22, 0.14, 0.12])
        self.assertEqual(len(h["beads"]), 7)
        kinds = [b[0] for b in h["beads"]]
        self.assertEqual((kinds.count("salt"), kinds.count("green"), kinds.count("amber")), (4, 2, 1))
        self.assertTrue(all(0.008 <= b[1] <= 0.012 for b in h["beads"]))

    def test_armholes_are_dropped_on_the_charts(self):
        """The top's and the coat's armholes sit at least 11.5 cm below the shoulder joint on both side lines."""
        import liss_costume as C
        from asha_costume import TorsoChart

        lm = landmarks()
        chart = TorsoChart(lm)
        c = params()["_costume"]
        sh = float(lm.side_pt("shoulder", "L")[2])
        # the armholes' lowest points: the top's at +92 (her left) and -88 (her right), the coat's at +-92
        top = C.top_line(lm, chart, np.array([92.0, -88.0]), c["top_armhole_drop_m"], c["top_right_neck_drop_m"])
        coat = C.coat_line(lm, chart, np.array([92.0, -92.0]), c["coat_armhole_drop_m"], c["coat_front_opening_deg"])
        for z in np.concatenate([top, coat]):
            self.assertLessEqual(float(z), sh - 0.115 + 1e-6)  # m: the rule is a clearance, not scaled


class TestLineMarks(unittest.TestCase):
    def setUp(self):
        import liss_textures as T

        self.T = T
        m = params()["_marks"]
        self.cfg = m
        self.marks = T.line_marks(m["seed"], m["placement"], tuple(m["length_m"]), m["line_mm"], m["gap_mm"],
                                  m["dot_mm"])

    def test_eleven_marks_placed_as_the_sheet(self):
        self.assertEqual(len(self.marks), 11)
        regions = [m["region"] for m in self.marks]
        self.assertEqual(regions, ["forearm"] * 5 + ["upper_arm"] * 3 + ["collar_neck"] * 2 + ["cheek"])
        self.assertEqual(self.marks[-1]["age"], 0.0)  # the eleventh is the newest, the crispest
        self.assertEqual(self.marks[0]["age"], 1.0)
        for m in self.marks:
            self.assertTrue(0.03 <= m["length"] <= 0.06)
            self.assertAlmostEqual(m["line_m"], 0.0006)
            self.assertAlmostEqual(m["dot_m"], 0.0015)
            bs = sorted({round(p[1], 6) for tr in m["traces"] for p in tr[:1]})
            self.assertTrue(np.allclose(np.diff(bs), 0.0018), bs)  # 0.6 mm lines, 1.2 mm gaps
            self.assertGreaterEqual(len(m["traces"]), 2)

    def test_deterministic_and_importable_by_other_saltwrights(self):
        m = self.cfg
        again = self.T.line_marks(m["seed"], m["placement"], tuple(m["length_m"]))
        self.assertEqual([x["traces"] for x in again], [x["traces"] for x in self.marks])
        other = self.T.line_marks(5, {"forearm": 2, "cheek": 0})
        self.assertEqual(len(other), 2)

    def test_right_side_only(self):
        """Every mark's centre is on her right (-X), and the painter never inks the left."""
        lm = landmarks()
        c = self.T.mark_centres(lm, self.marks)
        starts = self.T.mark_starts(lm, self.marks)
        self.assertTrue((c[:, 0] < -0.01).all(), c[:, 0])
        cheek = c[-1]
        self.assertGreater(float(cheek[2]), float(lm.P("chin")[2]))  # on the face, above the chin
        charts = self.T.liss_charts(lm)
        mirrored = c * np.array([-1.0, 1.0, 1.0])
        self.assertTrue((self.T.paint_marks(starts, lm, self.marks, charts, 11) > 0.2).all())  # each start's dot
        self.assertEqual(float(self.T.paint_marks(mirrored, lm, self.marks, charts, 11).max()), 0.0)
        self.assertEqual(float(self.T.paint_marks(starts * np.array([-1.0, 1.0, 1.0]), lm, self.marks, charts,
                                                  11).max()), 0.0)


class TestFacePoses(unittest.TestCase):
    def setUp(self):
        self.poses = json.loads((STAGE / "liss_face_poses.json").read_text(encoding="utf-8"))

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
        """§2.6: the rest brow_down 0.08 on every row; mouth_smile L = R x 1.3; nose_sneer_L 0.10 once the smile passes
        0.3; 0.10 s with 5% overshoot."""
        self.assertAlmostEqual(self.poses["blend_in_s"], 0.10)
        self.assertEqual(self.poses["rest"], {"brow_down": 0.08})
        self.assertTrue(all(v == 0.05 for v in self.poses["overshoot"].values()))
        em = self.poses["emotions"]
        sheet_brow = {"worried": 0.20, "grief": 0.40, "angry": 0.85, "cold": 0.30, "determined": 0.55}
        for tag, pose in em.items():
            self.assertAlmostEqual(pose["brow_down"], 0.08 + sheet_brow.get(tag, 0.0), places=6, msg=tag)
        for tag in ("soft_smile", "smile", "laugh"):
            l, r = em[tag]["mouth_smile"]
            self.assertAlmostEqual(l / r, 1.3, delta=0.02, msg=tag)
            sneer = em[tag].get("nose_sneer", [0.0, 0.0])
            self.assertEqual(sneer, [0.10, 0.0] if l > 0.3 else [0.0, 0.0], tag)
        self.assertEqual(em["neutral"], {"brow_down": 0.08})
        self.assertEqual(em["cold"]["mouth_smile"], 0.0)
        self.assertEqual(em["grief"]["brow_inner_up"], 1.0)

    def test_grief_is_the_widest_stretch_of_any_table(self):
        mine = self.poses["emotions"]["grief"]["mouth_stretch"]
        for path in (ROOT / "game/levels/_tests/characters").rglob("*_face_poses.json"):
            if path.parent.name == "liss":
                continue
            grief = json.loads(path.read_text(encoding="utf-8")).get("emotions", {}).get("grief", {})
            w = grief.get("mouth_stretch", 0.0)
            w = max(w) if isinstance(w, list) else w
            self.assertGreaterEqual(mine, w, path.name)


class TestEchoWatch(unittest.TestCase):
    """§2.2: no goggles, no yellow, no swirl patterns, trousers not a skirt, one crossed harness."""

    def test_no_goggles_or_skirt_pieces(self):
        import liss_costume as C

        names = " ".join(C.ATLAS).lower()
        for banned in ("goggle", "skirt", "swirl", "belt"):
            self.assertNotIn(banned, names)
        self.assertIn("trouser_leg_L", C.ATLAS)
        self.assertEqual(sum(k.startswith("strap_") for k in C.ATLAS), 2)  # the X: two straps
        js = glb_json(OUT / "liss.glb")
        meshes = " ".join(m.get("name", "") for m in js["meshes"]).lower()
        self.assertNotIn("goggle", meshes)
        self.assertNotIn("skirt", meshes)

    def test_no_yellow_in_the_cloth(self):
        """Saturated yellow (hue 45-65 degrees, saturation over 0.45, value over 0.45) stays under 0.5% of her cloth
        atlas (the brass buckles and the rope soles are dull, not yellow)."""
        from PIL import Image

        im = np.asarray(Image.open(OUT / "textures" / "liss_cloth_albedo.png").convert("RGB").resize((256, 256)))
        hsv = np.array([colorsys.rgb_to_hsv(*(px / 255.0)) for px in im.reshape(-1, 3)])
        yellow = (hsv[:, 0] * 360 > 45) & (hsv[:, 0] * 360 < 65) & (hsv[:, 1] > 0.45) & (hsv[:, 2] > 0.45)
        self.assertLess(float(yellow.mean()), 0.005)


class TestCommitted(unittest.TestCase):
    def test_glbs(self):
        js = glb_json(OUT / "liss.glb")
        self.assertLessEqual(tris(js), LOD0_MAX)
        lod = glb_json(OUT / "liss_lod1.glb")
        self.assertLessEqual(tris(lod), LOD1_MAX)
        self.assertLess((OUT / "liss.glb").stat().st_size, MAX_BYTES)
        self.assertLess((OUT / "liss_lod1.glb").stat().st_size, LOD1_MAX_BYTES)
        meshes = {m.get("name") for m in js["meshes"]}
        for n in MESHES:
            self.assertIn(n, meshes)
        head = next(m for m in js["meshes"] if m.get("name") == "Head")
        self.assertEqual(head.get("extras", {}).get("targetNames", []), API + VISEMES)

    def test_rig_extras(self):
        """§2.10: the coat tails (2 x 3), the hair tail (6) and the launcher's prop bone, after the 75 standard bones
        and M1-CHR-15's two shoulder correctives (DEF-armpit.L/.R, every hero), in their own order."""
        js = glb_json(OUT / "liss.glb")
        nodes = js["nodes"]
        joints = [nodes[i]["name"] for i in js["skins"][0]["joints"]]
        parent = {c: i for i, n in enumerate(nodes) for c in n.get("children", [])}
        idx = {n.get("name"): i for i, n in enumerate(nodes)}
        for name, par in EXTRA_BONES.items():
            self.assertIn(name, joints)
            self.assertEqual(nodes[parent[idx[name]]]["name"], par, name)
        standard = [j for j in joints if j not in EXTRA_BONES]
        self.assertEqual(len(standard), 77)
        self.assertIn("DEF-armpit.L", standard)
        self.assertIn("DEF-armpit.R", standard)
        lod = glb_json(OUT / "liss_lod1.glb")
        lod_std = [lod["nodes"][i]["name"] for i in lod["skins"][0]["joints"]
                   if lod["nodes"][i]["name"] not in EXTRA_BONES]
        self.assertEqual(standard, lod_std)

    def test_materials_and_textures(self):
        from PIL import Image

        js = glb_json(OUT / "liss.glb")
        mats = {m["name"] for m in js["materials"]}
        have = {p.stem for p in (OUT / "materials").glob("*.tres")}
        self.assertEqual(mats - have, set(), "every glTF material has a hero material")
        for want in ("hair", "cloth", "copper_mesh", "copper", "brass", "iron", "glimmer", "bead_salt", "bead_green",
                     "bead_amber"):
            self.assertIn(want, mats)
        for png in (OUT / "textures").glob("*.png"):
            self.assertLess(png.stat().st_size, MAX_BYTES, png.name)
            with Image.open(png) as im:
                w, h = im.size
            self.assertEqual(w & (w - 1), 0, png.name)
            self.assertEqual(h & (h - 1), 0, png.name)
        with Image.open(OUT / "textures" / "liss_body_albedo.png") as im:
            self.assertEqual(im.size, (2048, 2048))  # §2.9: the arm's line-marks need >= 14 px/cm
        import re

        for tres in (OUT / "materials").glob("*.tres"):
            for path in re.findall(r'path="res://([^"]+)"', tres.read_text(encoding="utf-8")):
                self.assertTrue((ROOT / path).exists(), f"{tres.name}: {path}")
        glim = (OUT / "materials" / "glimmer.tres").read_text(encoding="utf-8")
        self.assertIn("emission_enabled = true", glim)  # steady bound light


class TestRigRules(unittest.TestCase):
    """The M1-CHR-14 rules on the shipped GLB (no Blender)."""

    @classmethod
    def setUpClass(cls):
        import rig_probe

        cls.rp = rig_probe
        cls.rig = rig_probe.Rig("liss")
        cls.names = cls.rig.joint_names

    def dominant(self, part) -> np.ndarray:
        return np.array([self.names[part.J[i][int(np.argmax(part.W[i]))]] for i in range(len(part.P))])

    def bones_of(self, part) -> set:
        return {self.names[j] for j, w in zip(part.J.ravel(), part.W.ravel()) if w > 1e-4}

    def test_coat_tails_follow_one_leg_each_with_their_own_chain(self):
        cost = self.rig.part("Costume")
        J, Wt = cost.J, cost.W
        for side, other in (("l", "R"), ("r", "L")):
            chain = {f"DEF-coat_tail_{side}", f"DEF-coat_tail_{side}.001", f"DEF-coat_tail_{side}.002"}
            on = np.array([any(self.names[J[i, k]] in chain and Wt[i, k] > 1e-4 for k in range(4))
                           for i in range(len(cost.P))])
            self.assertGreater(int(on.sum()), 100, side)
            # a tail never takes the other leg (two tails, not a tube)
            leg = {f"DEF-thigh.{other}", f"DEF-thigh.{other}.001", f"DEF-shin.{other}", f"DEF-shin.{other}.001"}
            for i in np.nonzero(on)[0]:
                for k in range(4):
                    if Wt[i, k] > 1e-4:
                        self.assertNotIn(self.names[J[i, k]], leg, f"tail {side} on {self.names[J[i, k]]}")

    def test_sleeve_and_glove_ride_the_left_arm(self):
        sl = self.rig.part("WorkSleeve")
        dom = self.dominant(sl)
        parts = [d.split("-", 1)[1].split(".") for d in dom]
        arm = np.array(["L" in p and (p[0] in ("upper_arm", "forearm", "hand", "palm", "thumb") or p[0].startswith("f_"))
                        for p in parts])
        self.assertGreater(float(arm.mean()), 0.85)
        fingers = {d for d in dom if d.startswith(("DEF-f_", "DEF-thumb"))}
        self.assertTrue(all(".L" in f for f in fingers))
        self.assertGreaterEqual(len(fingers), 10)  # the five-finger glove takes the finger bones
        self.assertFalse(any(".R" in b and "arm" in b for b in self.bones_of(sl)))

    def test_launcher_two_centimetres_off_the_thigh_on_its_bone(self):
        launcher = self.rig.part("Launcher")
        self.assertEqual(self.bones_of(launcher), {"DEF-launcher"})
        box = self.rig.part("Launcher:copper").P
        lo, hi = box.min(axis=0), box.max(axis=0)
        body = self.rig.part("Body")
        dom = self.dominant(body)
        thigh = body.P[np.array([d.startswith("DEF-thigh.R") for d in dom])]
        d = np.linalg.norm(np.maximum(np.maximum(lo - thigh, thigh - hi), 0.0), axis=1)
        self.assertGreaterEqual(float(d.min()), 0.0195)

    def test_boots_take_the_feet_weights(self):
        cost = self.rig.part("Costume")
        low = cost.P[:, 1] < 0.05  # glTF: +Y up; the boot shells
        dom = self.dominant(cost)[low]
        self.assertGreater(int(low.sum()), 200)
        self.assertTrue(all(d.startswith(("DEF-foot", "DEF-toe", "DEF-shin")) for d in dom), set(dom))

    def test_knees_and_shins_are_kept_under_the_long_garments(self):
        body = self.rig.part("Body")
        dom = self.dominant(body)
        knee = float(self.rig.skeleton.g_t["DEF-shin.L"][1])
        for side in ("L", "R"):
            near = (np.abs(body.P[:, 1] - knee) < 0.04) & np.array([d.startswith(f"DEF-shin.{side}") or
                                                                    d.startswith(f"DEF-thigh.{side}") for d in dom])
            self.assertGreater(int(near.sum()), 30, side)

    def test_the_tail_is_a_seated_braid_in_the_guards(self):
        cfg = json.loads((ROOT / "tools/dev/rig_checks.json").read_text())["heroes"]["liss"]
        self.assertEqual(cfg["braid"]["mesh"], "HairTail:hair")
        self.assertEqual(cfg["braid"]["scalp"], ["HairHead:hair", "Head:skin_head"])
        self.assertEqual(cfg["garments"], ["Costume", "WorkSleeve"])
        self.assertEqual(cfg["props"], ["Launcher"])
        tail = self.rig.part("HairTail:hair")
        lab = self.rp.components(tail.F, self.rp.Topology(tail.F, tail.P).weld_id, len(tail.P))
        self.assertEqual(int((np.bincount(lab) >= 300).sum()), 2)  # a two-strand twist
        beads = [pr for pr in self.rig.prims["HairTail"] if pr.material.startswith("bead_")]
        self.assertEqual(sum(len(self.rp.Topology(b.F, b.P).boundary) == 0 for b in beads), len(beads))
        n_beads = sum(int(np.bincount(self.rp.components(b.F, self.rp.Topology(b.F, b.P).weld_id,
                                                         len(b.P))).size) for b in beads)
        self.assertEqual(n_beads, 7)


if __name__ == "__main__":
    unittest.main()
