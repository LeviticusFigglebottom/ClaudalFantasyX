"""Tests for the Ysolde hero build (M3-CHR-01, assets_src/characters/ysolde/).

Run: python3 -m unittest tools.tests.test_ysolde

* Pure-Python checks: every number of ysolde.md §1 and §9 in ysolde_params.json, the face-pose table against the
  shared shape API and the sheet's §6.2 table (her rest brow on every row, the smile lifting on the left first, the
  0.28 s blend with no overshoot), the committed GLBs (budgets, sizes, the mesh names the rig guards use, the Head's
  40 shapes, the book's `book_fan` shape in both files, the rig extras and their parents), textures (size cap,
  power-of-two) and materials (every texture exists).
* Geometry checks without Blender: the M1-CHR-14 rules in the parameters and charts (dropped armholes, the split
  robe's panels and laps, the hem off the floor, the book off the grip), and the gold script (the Glyph Trace's five
  strokes in the Swell order, brush weights, nothing boxed).
* The collar's head clearance under the clips' head range (rig_probe skinning): at least 25 mm from the head skin and
  the hair at a head turn of +-40 degrees and at a pitch of 20 degrees down and 15 up (each on its own, as the clips
  move the head; a 40 degree turn while looking 20 degrees down brings the jaw to about 17 mm of a wing).
"""
import json
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "characters" / "ysolde"
OUT = ROOT / "assets" / "characters" / "ysolde"
STAGE = ROOT / "game" / "levels" / "_tests" / "characters" / "ysolde"
for sub in ("ysolde", "villagers", "toma", "rhen", "asha", "base_body"):
    sys.path.insert(0, str(ROOT / "assets_src" / "characters" / sub))

MAX_BYTES = 5 * 1024 * 1024  # ADR 0005 plain-blob cap
LOD1_MAX_BYTES = int(1.5 * 1024 * 1024)  # ysolde.md §11
LOD0_MAX = 60_000  # ysolde.md §8.1 target (ceiling 70k)
LOD1_MAX = 30_000  # about 28k
PAIRED = ["brow_inner_up", "brow_down", "brow_outer_up", "lid_close", "lid_wide", "lid_squint", "cheek_raise",
          "nose_sneer", "mouth_smile", "mouth_frown", "mouth_stretch", "mouth_dimple"]
SINGLE = ["mouth_press", "mouth_pucker", "lip_upper_up", "lip_lower_down", "jaw_open", "jaw_clench"]
VISEMES = ["vis_rest", "vis_aa", "vis_e", "vis_i", "vis_o", "vis_u", "vis_mbp", "vis_fv", "vis_l", "vis_st"]
API = [f"{b}_{s}" for b in PAIRED for s in ("L", "R")] + SINGLE
# ysolde.md §9: the bb_params block
SHEET_PARAMS = {
    "height_m": 1.76, "heads_tall": 7.55, "shoulder_width_heads": 1.58, "chest_width_heads": 1.16,
    "chest_depth_heads": 0.86, "waist_width_heads": 1.02, "hip_width_heads": 1.38, "crotch_height_heads": 3.62,
    "arm_span_ratio": 1.01, "hand_length_heads": 0.80, "foot_length_ratio": 0.148, "neck_length_heads": 0.46,
    "neck_width_ratio": 0.48, "head_width_ratio": 0.64, "femininity": 0.95, "muscle": 0.25, "mass": 0.18,
    "breast": 0.32, "arm_abduction_deg": 47.0, "skin_hex": "#B48A72", "eye_scale": 1.10, "ipd_m": 0.061,
    "eye_tilt_deg": 3.0, "canthus_offset_m": 0.001, "jaw_width": 0.92, "cheekbone_height": 0.006,
    "cheekbone_width": 1.06, "chin_size": 1.02, "nose_bridge_width": 0.92, "nose_tip_projection": 1.04,
    "lip_fullness": 0.68, "lip_close": 0.6, "lip_seal": 0.96, "lip_lower_fullness": 0.66, "mouth_corner_lift": -0.0005,
    "brow_ridge": 0.9, "donor_mix_african": 0.15, "donor_mix_asian": 0.6, "donor_mix_caucasian": 0.25,
}
MESHES = ("Head", "Body", "Costume", "Collar", "HairHead", "Book", "InkGuards", "Pin")
EXTRA_BONES = {"DEF-book": "DEF-hand.R"}
for _root, _par in (("DEF-robe_fl", "DEF-thigh.L"), ("DEF-robe_fr", "DEF-thigh.R"), ("DEF-robe_bl", "DEF-thigh.L"),
                    ("DEF-robe_br", "DEF-thigh.R"), ("DEF-cord_a", "DEF-spine"), ("DEF-cord_b", "DEF-spine")):
    _chain = [_root, f"{_root}.001", f"{_root}.002"]
    EXTRA_BONES[_chain[0]] = _par
    for _a, _b in zip(_chain, _chain[1:]):
        EXTRA_BONES[_b] = _a


def params() -> dict:
    return json.loads((SRC / "ysolde_params.json").read_text(encoding="utf-8"))


def glb_json(path: Path) -> dict:
    data = path.read_bytes()
    magic, _version, _total = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a GLB"
    length, _kind = struct.unpack("<II", data[12:20])
    return json.loads(data[20:20 + length])


def tris(js: dict) -> int:
    return sum(js["accessors"][p["indices"]]["count"] // 3 for m in js["meshes"] for p in m["primitives"])


class TestParams(unittest.TestCase):
    def test_every_sheet_number_is_in_the_params(self):
        p = params()
        for key, want in SHEET_PARAMS.items():
            self.assertIn(key, p, key)
            self.assertEqual(p[key], want, key)
        import bb_params

        bb = bb_params.load_params(path=str(SRC / "ysolde_params.json"))
        lm = bb_params.Landmarks(bb)
        self.assertAlmostEqual(bb["height_m"] / lm.h, 7.55, places=2)
        fig = p["_figure"]
        self.assertEqual(fig["age"], 47)
        self.assertAlmostEqual(fig["age_layer"], 0.4)
        self.assertAlmostEqual(fig["idle_sway"], 0.3)
        self.assertAlmostEqual(fig["rest_brow_outer_up_L"], 0.08)

    def test_m1_chr_14_rules_in_the_parameters(self):
        c = params()["_costume"]
        self.assertGreaterEqual(c["gown_armhole_drop_m"], 0.115)
        self.assertGreaterEqual(c["sleeve_seam_drop_m"], 0.115)
        self.assertAlmostEqual(c["book_grip_offset_m"], 0.012)
        self.assertAlmostEqual(c["robe_hem_above_floor_m"], 0.09)
        self.assertGreaterEqual(c["collar_head_clearance_m"], 0.025)
        self.assertEqual(c["book_panels"], 12)
        self.assertEqual(c["book_panel_m"], [0.24, 0.12, 0.003])
        self.assertAlmostEqual(c["book_fan_deg"], 160.0)
        self.assertAlmostEqual(c["guard_extension_m"], 0.045)

    def test_robe_is_split_into_lapped_panels(self):
        """Four leg-following panels (front-left, front-right, the back's two halves), not a tube: the front-left
        panel's edge is the split left of centre, the front panels end at the side lines and every under panel runs
        on beneath the one over it, the laps stacked outward."""
        import ysolde_costume as C

        fs = params()["_costume"]["front_split_deg"]
        spans = C.panel_spans(fs)
        self.assertEqual(spans["fl"], (fs, 90.0))
        self.assertEqual(spans["fr"][0], -90.0)
        self.assertGreater(spans["fr"][1], fs)
        self.assertLess(spans["back"][0], 90.0)
        self.assertGreater(spans["back"][1], 270.0)
        self.assertLess(C.PANEL_OFF["back"], C.PANEL_OFF["fr"])
        self.assertLess(C.PANEL_OFF["fr"], C.PANEL_OFF["fl"])
        z = C.panel_rows(1.0, 0.09, C.PANEL_ROWS)
        self.assertTrue((abs(z[-1] - 0.09) < 1e-12) and all(a > b for a, b in zip(z, z[1:])))
        self.assertLess(z[-2] - z[-1], z[0] - z[1])  # the rows crowd toward the hem (the border's texels)


class TestFacePoses(unittest.TestCase):
    def setUp(self):
        self.poses = json.loads((STAGE / "ysolde_face_poses.json").read_text(encoding="utf-8"))

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
        """ysolde.md §6.2: the rest brow_outer_up_L 0.08 on every row; the smile lifts on the left first (L = R x 1.2);
        mouth_press in nearly every row; 0.28 s, no overshoot."""
        self.assertAlmostEqual(self.poses["blend_in_s"], 0.28)
        self.assertEqual(self.poses["overshoot"], {})
        self.assertEqual(self.poses["rest"], {"brow_outer_up_L": 0.08})
        em = self.poses["emotions"]
        for tag, pose in em.items():
            l, r = pose["brow_outer_up"]
            self.assertAlmostEqual(l - r, 0.08, places=6, msg=tag)
        for tag in ("soft_smile", "smile", "laugh", "tender"):
            l, r = em[tag]["mouth_smile"]
            self.assertAlmostEqual(l / r, 1.2, delta=0.06, msg=tag)  # the sheet's own pairs (tender 0.15/0.12)
        self.assertGreaterEqual(sum("mouth_press" in p for p in em.values()), 11)
        self.assertEqual(em["neutral"], {"mouth_press": 0.10, "brow_outer_up": [0.08, 0.0]})
        self.assertEqual(em["surprised"]["brow_outer_up"], [0.68, 0.60])
        self.assertEqual(em["grief"]["jaw_clench"], 0.25)
        self.assertEqual(em["cold"], {"brow_down": 0.20, "lid_close": 0.22, "mouth_press": 0.40,
                                      "brow_outer_up": [0.08, 0.0]})


class TestCommitted(unittest.TestCase):
    def test_glbs(self):
        js = glb_json(OUT / "ysolde.glb")
        self.assertLessEqual(tris(js), LOD0_MAX)
        lod = glb_json(OUT / "ysolde_lod1.glb")
        self.assertLessEqual(tris(lod), LOD1_MAX)
        self.assertLess((OUT / "ysolde.glb").stat().st_size, MAX_BYTES)
        self.assertLess((OUT / "ysolde_lod1.glb").stat().st_size, LOD1_MAX_BYTES)
        meshes = {m.get("name") for m in js["meshes"]}
        for n in MESHES:
            self.assertIn(n, meshes)
        head = next(m for m in js["meshes"] if m.get("name") == "Head")
        self.assertEqual(head.get("extras", {}).get("targetNames", []), API + VISEMES)
        for doc in (js, lod):  # the battle actor plays book_fan too: the node keeps the name the clips' track uses
            node = next(n for n in doc["nodes"] if n.get("name") == "Book")
            book = doc["meshes"][node["mesh"]]
            self.assertEqual(book.get("extras", {}).get("targetNames", []), ["book_fan"])

    def test_rig_extras(self):
        """ysolde.md §9: the robe panels' chains (4 x 3), the cord ends (2 x 3) and the book's prop bone, after the 75
        standard bones in their own order."""
        js = glb_json(OUT / "ysolde.glb")
        nodes = js["nodes"]
        joints = [nodes[i]["name"] for i in js["skins"][0]["joints"]]
        parent = {c: i for i, n in enumerate(nodes) for c in n.get("children", [])}
        idx = {n.get("name"): i for i, n in enumerate(nodes)}
        for name, par in EXTRA_BONES.items():
            self.assertIn(name, joints)
            self.assertEqual(nodes[parent[idx[name]]]["name"], par, name)
        standard = [j for j in joints if j not in EXTRA_BONES]
        self.assertEqual(len(standard), 75)
        lod = glb_json(OUT / "ysolde_lod1.glb")
        lod_std = [lod["nodes"][i]["name"] for i in lod["skins"][0]["joints"]
                   if lod["nodes"][i]["name"] not in EXTRA_BONES]
        self.assertEqual(standard, lod_std)

    def test_materials_and_textures(self):
        from PIL import Image

        js = glb_json(OUT / "ysolde.glb")
        mats = {m["name"] for m in js["materials"]}
        have = {p.stem for p in (OUT / "materials").glob("*.tres")}
        self.assertEqual(mats - have, set(), "every glTF material has a hero material")
        for want in ("hair_streak", "hair_grey", "props", "silver", "gold", "cloth"):
            self.assertIn(want, mats)
        for png in (OUT / "textures").glob("*.png"):
            self.assertLess(png.stat().st_size, MAX_BYTES, png.name)
            w, h = Image.open(png).size
            self.assertEqual(w & (w - 1), 0, png.name)
            self.assertEqual(h & (h - 1), 0, png.name)
        import re

        for tres in (OUT / "materials").glob("*.tres"):
            for path in re.findall(r'path="res://([^"]+)"', tres.read_text(encoding="utf-8")):
                self.assertTrue((ROOT / path).exists(), f"{tres.name}: {path}")


class TestScript(unittest.TestCase):
    """ysolde.md §3: the costume glyph is the Glyph Trace written as brush calligraphy, never a constant-width line."""

    def test_trace_is_the_swell_order(self):
        import ysolde_motifs as M

        g = M.glyph("trace")
        self.assertEqual(g["directions"], ["down", "right", "up", "right", "down"])
        self.assertEqual(M.stroke_directions(g), g["directions"])
        self.assertTrue(any(st.get("dry") for st in g["strokes"]), "a dry-brush break")
        self.assertEqual(M.load()["weight_mm"], [0.8, 2.4])
        self.assertEqual(len(M.load()["panels"]), 12)

    def test_strokes_vary_in_weight(self):
        import numpy as np
        import ysolde_motifs as M

        g = M.glyph("trace")
        widths = np.concatenate([M.stroke_samples(st, (0.8 / 22.0, 2.4 / 22.0))[1] for st in g["strokes"]])
        self.assertGreater(widths.max() / widths.min(), 2.5)  # tapered entries, pressure: not a pen line
        cov, _pool = M.tile("trace", 120, 150, 22.0)
        self.assertGreater(cov.mean(), 0.03)
        self.assertEqual(float(cov[0].max()), 0.0)  # nothing boxed or framed: the cell's edge stays clear
        self.assertEqual(float(cov[:, 0].max()), 0.0)


class TestCollarClearance(unittest.TestCase):
    def test_collar_clears_the_head_and_hair_in_the_clips_range(self):
        import numpy as np

        sys.path.insert(0, str(ROOT / "tools" / "dev"))
        import rig_probe

        hc = rig_probe.hero_clips
        rig = rig_probe.Rig("ysolde")
        collar, head, hair = rig.part("Collar"), rig.part("Head:skin_head"), rig.part("HairHead")
        clear = params()["_costume"]["collar_head_clearance_m"]
        for yaw, pitch in ((0, 0), (40, 0), (-40, 0), (0, 20), (0, -15)):
            turn = hc.qeuler((pitch, yaw, 0.0))  # +X pitches the head down, +Y turns it to her left
            local = rig.skeleton.local_pose({"DEF-spine.006": turn})
            mats = rig.skin_matrices(local)
            C = rig.skin(collar, mats)
            for part in (head, hair):
                P = rig.skin(part, mats)
                i = rig_probe._nearest_brute(C, P, 1).ravel()
                d = np.linalg.norm(P[i] - C, axis=1).min()
                self.assertGreaterEqual(float(d), clear, f"{part.name} at yaw {yaw} pitch {pitch}: {d * 1000:.1f} mm")


if __name__ == "__main__":
    unittest.main()
