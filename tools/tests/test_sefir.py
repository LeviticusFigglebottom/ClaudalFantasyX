"""Tests for the Sefir hero build (M3-CHR-02, assets_src/characters/sefir/).

Run: python3 -m unittest tools.tests.test_sefir

* Pure-Python checks: parameters against act1_npcs.md §1.1 / §1.10 (and no asymmetric slider), the face-pose table
  against the shared shape API and the sheet's §1.6 table (all symmetric scalars, blend 0.40 s, no overshoot), the
  committed GLBs (budget, blendshape names, every material has a hero material, the rig extras and their weights),
  textures (size cap, power-of-two), materials (every texture exists; the sefir_eye_still variant), the rig guard
  config, the Level-scale motif data and the mantle's measured gold share.
* Geometry checks without Blender: the over-robe is four panels split as the sheet says (never a tube) with its hem
  1.5 cm off the floor; the torso garments' armholes sit at least 11.5 cm below the shoulder joints; the half-mantle is
  on the right shoulder only.
* Posed checks on the committed GLB (tools/dev/rig_probe.py's skinning): the crown clears the mantle by 30 mm across a
  head pitch of -20 degrees and a yaw of +-40 degrees, and the long hair stays outside the mantle in the rest pose and
  in his clips.
"""
import json
import math
import re
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "characters" / "sefir"
OUT = ROOT / "assets" / "characters" / "sefir"
STAGE = ROOT / "game" / "levels" / "_tests" / "characters" / "sefir"
for sub in ("sefir", "toma", "rhen", "asha", "base_body"):
    sys.path.insert(0, str(ROOT / "assets_src" / "characters" / sub))
sys.path.insert(0, str(ROOT / "tools" / "dev"))

MAX_BYTES = 5 * 1024 * 1024  # ADR 0005 plain-blob cap
LOD0_TARGET = 62_000  # act1_npcs.md §1.9 (ceiling 70k)
LOD1_RANGE = (24_000, 31_000)  # "about 28k"
PAIRED = ["brow_inner_up", "brow_down", "brow_outer_up", "lid_close", "lid_wide", "lid_squint", "cheek_raise",
          "nose_sneer", "mouth_smile", "mouth_frown", "mouth_stretch", "mouth_dimple"]
SINGLE = ["mouth_press", "mouth_pucker", "lip_upper_up", "lip_lower_down", "jaw_open", "jaw_clench"]
VISEMES = ["vis_rest", "vis_aa", "vis_e", "vis_i", "vis_o", "vis_u", "vis_mbp", "vis_fv", "vis_l", "vis_st"]
API = [f"{b}_{s}" for b in PAIRED for s in ("L", "R")] + SINGLE
# act1_npcs.md §1.6, the emotion table (all 15, symmetric)
SHEET = {
    "neutral": {"mouth_smile": 0.08},
    "soft_smile": {"mouth_smile": 0.30, "cheek_raise": 0.12, "lid_squint": 0.08},
    "smile": {"mouth_smile": 0.55, "cheek_raise": 0.35, "lid_squint": 0.20},
    "laugh": {"mouth_smile": 0.70, "cheek_raise": 0.50, "jaw_open": 0.18, "lid_squint": 0.35},
    "worried": {"brow_inner_up": 0.25, "mouth_press": 0.15},
    "sad": {"brow_inner_up": 0.35, "lid_close": 0.20, "mouth_smile": 0.05},
    "grief": {"brow_inner_up": 0.60, "lid_close": 0.30, "mouth_frown": 0.20},
    "angry": {"lid_squint": 0.12, "mouth_press": 0.20},
    "cold": {"brow_down": 0.12, "mouth_press": 0.25},
    "surprised": {"brow_outer_up": 0.30, "brow_inner_up": 0.20, "lid_wide": 0.20},
    "afraid": {"brow_inner_up": 0.40, "lid_wide": 0.30},
    "determined": {"brow_down": 0.15, "mouth_press": 0.20, "mouth_smile": 0.05},
    "tender": {"brow_inner_up": 0.22, "mouth_smile": 0.22, "lid_close": 0.18},
    "guilty": {"brow_inner_up": 0.20, "lid_close": 0.20},
    "exhausted": {"lid_close": 0.50, "mouth_smile": 0.20, "brow_inner_up": 0.10},
}
# act1_npcs.md §1.10, the starting values (all of them are in sefir_params.json)
SHEET_PARAMS = {
    "height_m": 1.88, "heads_tall": 7.65, "shoulder_width_heads": 1.75, "chest_width_heads": 1.24,
    "chest_depth_heads": 0.9, "waist_width_heads": 1.10, "hip_width_heads": 1.32, "crotch_height_heads": 3.7,
    "arm_span_ratio": 1.01, "hand_length_heads": 0.82, "neck_length_heads": 0.44, "neck_width_ratio": 0.52,
    "head_width_ratio": 0.64, "femininity": 0.05, "muscle": 0.35, "mass": 0.15, "breast": 0.0, "eye_scale": 1.10,
    "ipd_m": 0.063, "eye_tilt_deg": 1.0, "jaw_width": 0.98, "cheekbone_height": 0.006, "cheekbone_width": 1.05,
    "chin_size": 1.02, "nose_bridge_width": 0.92, "nose_tip_projection": 1.02, "lip_fullness": 0.85,
    "lip_close": 0.6, "lip_seal": 0.96, "lip_lower_fullness": 0.75, "mouth_corner_lift": 0.0005, "brow_ridge": 0.95,
    "donor_mix_african": 0.1, "donor_mix_asian": 0.3, "donor_mix_caucasian": 0.6,
}
EXTRA_BONES = {}
for _p, _leg in (("fl", "L"), ("bl", "L"), ("br", "R"), ("fr", "R")):
    _chain = [f"DEF-robe_{_p}"] + [f"DEF-robe_{_p}.{i:03d}" for i in range(1, 4)]
    EXTRA_BONES[_chain[0]] = f"DEF-thigh.{_leg}"
    for _a, _b in zip(_chain, _chain[1:]):
        EXTRA_BONES[_b] = _a
for _g in [f"b{k}" for k in range(1, 7)] + ["f1", "f2"]:
    _chain = [f"DEF-hair_{_g}"] + [f"DEF-hair_{_g}.{i:03d}" for i in range(1, 5)]
    EXTRA_BONES[_chain[0]] = "DEF-spine.003"
    for _a, _b in zip(_chain, _chain[1:]):
        EXTRA_BONES[_b] = _a
EXTRA_BONES["DEF-mantle"] = "DEF-shoulder.R"
EXTRA_BONES["DEF-crown"] = "DEF-spine.006"


def glb_json(path: Path) -> dict:
    data = path.read_bytes()
    magic, _version, _total = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a GLB"
    length, _kind = struct.unpack("<II", data[12:20])
    return json.loads(data[20:20 + length])


def tris(js: dict) -> int:
    return sum(js["accessors"][p["indices"]]["count"] // 3 for m in js["meshes"] for p in m["primitives"])


class TestParams(unittest.TestCase):
    def test_params_match_the_sheet(self):
        import bb_params

        p = bb_params.load_params(path=str(SRC / "sefir_params.json"))
        lm = bb_params.Landmarks(p)
        for k, v in SHEET_PARAMS.items():
            self.assertAlmostEqual(float(p[k]), v, places=6, msg=k)
        self.assertAlmostEqual(p["height_m"] / lm.h, 7.65, places=2)  # the most elongated in the cast
        self.assertEqual(p["skin_hex"], "#C29C84")  # skin_sefir
        self.assertEqual(p["canthus_offset_m"], 0.0)  # symmetric face: no asymmetric slider anywhere
        extra = json.loads((SRC / "sefir_params.json").read_text())
        c = extra["_costume"]
        self.assertEqual((c["robe_panels"], c["robe_panel_bones"]), (4, 4))
        self.assertAlmostEqual(c["robe_hem_m"], 0.015)
        self.assertAlmostEqual(c["mantle_clearance_m"], 0.025)
        self.assertAlmostEqual(c["mantle_hinge_deg"], 6.0)
        self.assertAlmostEqual(c["mantle_above_elbow_m"], 0.09)
        self.assertAlmostEqual(c["mantle_flare_m"], 0.04)
        self.assertGreaterEqual(c["underrobe_armhole_drop_m"], 0.115)  # M1-CHR-14
        self.assertGreaterEqual(c["robe_armhole_drop_m"], 0.115)
        self.assertEqual(c["robe_left_spring"], {"stiffness": 0.8, "damping": 0.9})
        h = extra["_hair"]
        self.assertAlmostEqual(h["length_m"], 0.65)
        self.assertEqual((h["back_groups"], h["front_groups"], h["chain_bones"]), (6, 2, 5))
        self.assertAlmostEqual(h["stiffness"], 0.85)
        self.assertAlmostEqual(h["wind_response"], 0.1)
        cr = extra["_crown"]
        self.assertAlmostEqual(cr["diameter_m"], 0.34)
        self.assertAlmostEqual(cr["depth_m"], 0.06)
        self.assertAlmostEqual(cr["hair_gap_m"], 0.04)
        self.assertAlmostEqual(cr["mantle_clearance_m"], 0.03)
        f = extra["_face"]
        self.assertEqual(f["freckles"], 0)
        self.assertAlmostEqual(f["blend_in_s"], 0.40)
        self.assertEqual(f["blink_interval_s"], [10.0, 14.0])

    def test_hair_groups_match_the_params(self):
        import sefir_hair

        h = json.loads((SRC / "sefir_params.json").read_text())["_hair"]
        self.assertEqual(len(sefir_hair.BACK_GROUPS), h["back_groups"])
        self.assertEqual(len(sefir_hair.FRONT_GROUPS), h["front_groups"])

    def test_face_poses_cover_every_emotion_symmetrically(self):
        poses = json.loads((STAGE / "sefir_face_poses.json").read_text())
        tags = {e["id"] for e in json.loads((ROOT / "game/data/dialogue/emotions.json").read_text())["emotions"]}
        self.assertEqual(set(poses["emotions"]), tags)
        names = set(PAIRED) | set(SINGLE)
        for tag, pose in poses["emotions"].items():
            for shape, w in pose.items():
                self.assertIn(shape, names, f"{tag}: {shape}")
                # his tell is symmetry: a scalar sets both sides; no [L, R] pair and no _L / _R shape anywhere
                self.assertNotIsInstance(w, list, f"{tag}: {shape}")
                self.assertTrue(0.0 <= w <= 1.0, f"{tag}: {shape}")

    def test_face_poses_follow_the_sheet(self):
        poses = json.loads((STAGE / "sefir_face_poses.json").read_text())
        self.assertAlmostEqual(poses["blend_in_s"], 0.40)  # the slowest in the cast
        self.assertEqual(poses["overshoot"], {})  # no overshoot
        self.assertEqual(poses["emotions"], SHEET)


class TestCommitted(unittest.TestCase):
    def test_glbs(self):
        js = glb_json(OUT / "sefir.glb")
        self.assertLessEqual(tris(js), LOD0_TARGET)
        lo, hi = LOD1_RANGE
        self.assertTrue(lo <= tris(glb_json(OUT / "sefir_lod1.glb")) <= hi)
        for name in ("sefir.glb", "sefir_lod1.glb"):
            self.assertLess((OUT / name).stat().st_size, MAX_BYTES, name)
        nodes = {n.get("name") for n in js["nodes"]}
        for n in ("Head", "Body", "Costume", "Mantle", "HairHead", "HairBack", "Crown", "DEF-eye.L", "DEF-eye.R"):
            self.assertIn(n, nodes)
        head = next(m for m in js["meshes"] if m.get("name") == "Head")
        self.assertEqual(head.get("extras", {}).get("targetNames", []), API + VISEMES)  # all 40 shapes
        lod1 = {n.get("name") for n in glb_json(OUT / "sefir_lod1.glb")["nodes"]}
        for n in ("Crown_lod1", "Mantle_lod1", "HairBack_lod1"):  # the crown disc, the mantle, the front falls
            self.assertIn(n, lod1)

    def test_rig_extras(self):
        """act1_npcs.md §1.10: robe panels 4 x 4 on the thighs, DEF-mantle on DEF-shoulder.R, DEF-crown on the head,
        hair 8 groups x 5 on the chest; after the 75 standard bones in their own order; every extra bone weighted."""
        import numpy as np

        js = glb_json(OUT / "sefir.glb")
        nodes = js["nodes"]
        joints = [nodes[i]["name"] for i in js["skins"][0]["joints"]]
        parent = {c: i for i, n in enumerate(nodes) for c in n.get("children", [])}
        idx = {n.get("name"): i for i, n in enumerate(nodes)}
        for name, par in EXTRA_BONES.items():
            self.assertIn(name, joints)
            self.assertEqual(nodes[parent[idx[name]]]["name"], par, name)
        standard = [j for j in joints if j not in EXTRA_BONES]
        self.assertEqual(len(standard), 75)
        old = glb_json(OUT / "sefir_lod1.glb")
        lod_std = [old["nodes"][i]["name"] for i in old["skins"][0]["joints"]
                   if old["nodes"][i]["name"] not in EXTRA_BONES]
        self.assertEqual(standard, lod_std, "the LOD1 skeleton matches")
        data = (OUT / "sefir.glb").read_bytes()
        jlen = struct.unpack("<I", data[12:16])[0]
        blob = data[20 + jlen + 8:]

        def read(acc_i: int) -> np.ndarray:
            acc = js["accessors"][acc_i]
            view = js["bufferViews"][acc["bufferView"]]
            dt = {5121: np.uint8, 5123: np.uint16, 5126: np.float32}[acc["componentType"]]
            off = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
            arr = np.frombuffer(blob, dtype=dt, count=acc["count"] * 4, offset=off).reshape(-1, 4)
            return arr.astype(float) / (255.0 if dt == np.uint8 else 65535.0) if dt != np.float32 and \
                acc.get("normalized") else arr

        weighted = set()
        for n in nodes:
            if "mesh" not in n or "skin" not in n:
                continue
            for prim in js["meshes"][n["mesh"]]["primitives"]:
                a = prim["attributes"]
                if "JOINTS_0" not in a:
                    continue
                J, W = read(a["JOINTS_0"]), read(a["WEIGHTS_0"])
                weighted |= {joints[int(j)] for j in np.unique(J[W > 1e-3])}
        self.assertEqual(set(EXTRA_BONES) - weighted, set(), "every extra bone has vertices on it")

    def test_every_gltf_material_has_a_hero_material(self):
        mats = {m["name"] for m in glb_json(OUT / "sefir.glb")["materials"]}
        have = {p.stem for p in (OUT / "materials").glob("*.tres")}
        self.assertEqual(mats - have, set())
        stage = (STAGE / "sefir_stage.tscn").read_text()
        for m in mats:
            self.assertIn(f'"{m}": ExtResource("m_{m}")', stage)
        # the Act II tell: the sefir_eye_still pair (a material variant, not a map)
        self.assertTrue({"eye_still", "cornea_still"} <= have)

    def test_material_textures_exist(self):
        for tres in (OUT / "materials").glob("*.tres"):
            for path in re.findall(r'path="res://([^"]+)"', tres.read_text()):
                self.assertTrue((ROOT / path).exists(), f"{tres.name}: {path}")
        hair = (OUT / "materials" / "hair.tres").read_text()
        self.assertIn("shader_parameter/wind_response = 0.1", hair)  # §1.5: 0.1 x the global wind

    def test_textures(self):
        from PIL import Image

        files = sorted((OUT / "textures").glob("*.png"))
        self.assertEqual(len(files), 12)  # head 4, body 4, costume 4
        for f in files:
            self.assertLess(f.stat().st_size, MAX_BYTES, f.name)
            with Image.open(f) as im:
                w, h = im.size
            self.assertEqual(w & (w - 1), 0, f.name)
            self.assertEqual(h & (h - 1), 0, f.name)

    def test_mantle_gold_share_is_the_budget_choice(self):
        """act1_npcs.md §1.4 gold budget: the mantle's gold coverage is lowered (no exception claimed) to 13%, what a
        front waist-up frame allows beside the crown (TestPosed). The clothmask's gold channel over the mantle's island
        is that share (the 1 px blur aside)."""
        import numpy as np
        from PIL import Image

        import sefir_costume as C

        target = json.loads((SRC / "sefir_params.json").read_text())["_costume"]["mantle_gold_coverage"]
        self.assertAlmostEqual(target, 0.13)  # 0.14 until GPU QA row 54's hair left 5.03% gold in the front frame
        with Image.open(OUT / "textures" / "sefir_cloth_clothmask.png") as im:
            m = np.asarray(im.convert("RGBA"), dtype=float) / 255.0
        n = m.shape[0]
        u0, v0, u1, v1 = C.ATLAS["mantle"]
        g = m[int(v0 * n) + 2:int(v1 * n) - 2, int(u0 * n) + 2:int(u1 * n) - 2, 1]
        self.assertAlmostEqual(float(g.mean()), target, delta=0.02)

    def test_rig_guard_config(self):
        cfg = json.loads((ROOT / "tools" / "dev" / "rig_checks.json").read_text())["heroes"]["sefir"]
        self.assertEqual(cfg["garments"], ["Costume", "Mantle", "HairBack"])
        self.assertEqual(cfg["props"], ["Crown"])
        self.assertIsNone(cfg["braid"])

    def test_level_scale_motif_is_vector_data(self):
        motif = json.loads((SRC / "motifs" / "level_scale.json").read_text())
        self.assertAlmostEqual(motif["diameter_mm"], 18.0)  # each scale an 18 mm Level
        for k in ("ring_outer", "bar_width", "bar_length", "rim_width", "row_pitch", "col_pitch"):
            self.assertIn(k, motif)


class TestGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import bb_anatomy
        import bb_params

        import sefir_costume

        cls.params = bb_params.load_params(path=str(SRC / "sefir_params.json"))
        cls.extra = json.loads((SRC / "sefir_params.json").read_text())
        cls.lm = bb_params.Landmarks(cls.params)
        cls.body = bb_anatomy.Body(cls.lm)
        cls.costume, cls.anchors = sefir_costume.build_costume(cls.body, cls.extra["_costume"])

    def test_charts_fit_the_atlas(self):
        import numpy as np

        for name, part in self.costume.items():
            uv = np.array([q for face in part.UV for q in face])
            self.assertTrue(((uv >= -1e-9) & (uv <= 1 + 1e-9)).all(), name)

    def test_robe_is_four_split_panels_not_a_tube(self):
        """§1.4 #4: four panels, each split from its neighbours below the split tops (front and back at mid-thigh,
        the sides 6 cm below the hip joint), welded above them; the hem 1.5 cm off the floor."""
        import numpy as np

        import sefir_costume as C

        panels = self.anchors["panels"]
        self.assertEqual(sorted(panels), ["BL", "BR", "FL", "FR"])
        S = self.lm.S
        splits = C.split_heights(self.lm, self.extra["_costume"])
        z_hip = float(self.lm.side_pt("hip", "L")[2])
        self.assertAlmostEqual(splits[90.0], z_hip - 0.06 * S, places=6)
        self.assertAlmostEqual(splits[0.0], 0.5 * (z_hip + float(self.lm.side_pt("knee", "L")[2])), places=6)
        for name, p in panels.items():
            G = p.grid_P
            self.assertAlmostEqual(float(G[-1, :, 2].min()), self.extra["_costume"]["robe_hem_m"], delta=0.002)
        for seam, z in splits.items():
            over = C.LAPS_OVER[seam]
            under = next(n for n, a0, a1, _l in C.PANELS if n != over and seam in (a0 % 360.0, a1 % 360.0))
            a0o = next(a0 for n, a0, _a1, _l in C.PANELS if n == over) % 360.0
            a0u = next(a0 for n, a0, _a1, _l in C.PANELS if n == under) % 360.0
            eo = panels[over].grid_P[:, 0 if a0o == seam else -1]
            eu = panels[under].grid_P[:, 0 if a0u == seam else -1]
            above = eo[:, 2] >= z
            self.assertTrue(np.array_equal(eo[above], eu[above]), f"welded above the split at {seam}")
            gap = np.linalg.norm(eo[~above] - eu[~above], axis=1)
            self.assertGreater(float(gap[-1]), 0.01, f"the split at {seam} opens toward the hem")

    def test_torso_armholes_and_the_mantle_side(self):
        import sefir_costume as C
        from asha_costume import TorsoChart

        S = self.lm.S
        chart = TorsoChart(self.lm)
        sh_z = float(self.lm.P("shoulder")[2])
        c = self.extra["_costume"]
        for fn, drop in ((C.underrobe_top, c["underrobe_armhole_drop_m"]), (C.robe_top, c["robe_armhole_drop_m"])):
            import numpy as np

            self.assertLessEqual(float(fn(self.lm, chart, np.array([90.0]), drop)[0]), sh_z - 0.115 * S + 1e-9)
        P = self.costume["Mantle"].varr()
        self.assertLess(float(P[:, 0].max()), 0.0, "the half-mantle is on his right shoulder only")
        sh, el = self.lm.side_pt("shoulder", "R"), self.lm.side_pt("elbow", "R")
        ax = (el - sh) / math.dist(el, sh)
        reach = float(((P - sh) @ ax).max())
        self.assertGreater(reach, math.dist(el, sh) - 0.09 * S - 0.05)  # to about 9 cm above the elbow


class TestPosed(unittest.TestCase):
    """The committed GLB, skinned by tools/dev/rig_probe.py (the same linear blend skinning as Godot)."""

    @classmethod
    def setUpClass(cls):
        import rig_probe

        cls.rp = rig_probe
        cls.rig = rig_probe.Rig("sefir")
        cls.crown = cls.rig.part("Crown")
        cls.mantle = cls.rig.part("Mantle")
        cls.hair = cls.rig.part("HairBack")

    def _posed(self, part, turns: dict):
        hc = self.rp.hero_clips
        local = self.rig.skeleton.local_pose({b: hc.qeuler(v) for b, v in turns.items()})
        return self.rig.skin(part, self.rig.skin_matrices(local))

    def test_crown_clears_the_mantle(self):
        """§1.4 #6: at least 30 mm from the mantle at a head pitch of -20 degrees and a yaw of +-40 degrees."""
        import numpy as np

        need = json.loads((SRC / "sefir_params.json").read_text())["_crown"]["mantle_clearance_m"]
        for turn in ((0.0, 0.0, 0.0), (-20.0, 0.0, 0.0), (0.0, 40.0, 0.0), (0.0, -40.0, 0.0), (-20.0, 40.0, 0.0),
                     (-20.0, -40.0, 0.0)):
            C = self._posed(self.crown, {"DEF-spine.006": turn})
            M = self._posed(self.mantle, {"DEF-spine.006": turn})
            idx = self.rp.nearest_index(C, M)[:, 0]
            d = float(np.linalg.norm(C - M[idx], axis=1).min())
            self.assertGreaterEqual(d, need, f"head turn {turn}: {d * 1000:.1f} mm")

    def test_waist_up_frames_stay_inside_the_gold_budget(self):
        """§1.4: a waist-up frame of Sefir alone (16:9, waist to the top of the crown, his idle pose) is at most 5%
        gold: the crown's pixels plus the mantle's pixels x the mantle's gold share. Measured by geometry (flat ids,
        nearest surface wins), in front and at the hero three-quarter."""
        import numpy as np
        from PIL import Image, ImageDraw

        hc = self.rp.hero_clips
        pose = hc.staff_hold(hc.pose_at("idle", 0.0, hc.LENGTHS["idle"], self.rig.skeleton, hc.PERSONA["sefir"]),
                             hc.PERSONA["sefir"])
        local = self.rig.skeleton.local_pose({b: hc.qeuler(v) for b, v in pose.items() if b != "hips"})
        mats = self.rig.skin_matrices(local)
        share = json.loads((SRC / "sefir_params.json").read_text())["_costume"]["mantle_gold_coverage"]
        meshes = []
        for name in self.rig.prims:
            if name.startswith(("Eye", "Cornea", "Tear")):
                continue
            part = self.rig.part(name)
            meshes.append((self.rig.skin(part, mats), part.F, 1 if name == "Crown" else (2 if name == "Mantle" else 3)))
        W, H, y0, y1 = 480, 270, 1.15, 2.0
        for yaw in (0.0, -45.0):
            a = math.radians(yaw)
            fwd = np.array([-math.sin(a), 0.0, -math.cos(a)])
            right = np.array([math.cos(a), 0.0, -math.sin(a)])
            half = (y1 - y0) * W / H / 2
            tri = []
            for P, F, cid in meshes:
                depth = P[F].mean(axis=1) @ fwd
                X = (P @ right + half) / (2 * half) * W
                Y = (y1 - P[:, 1]) / (y1 - y0) * H
                tri += [(float(d), cid, f) for d, f in zip(depth, np.stack([X[F], Y[F]], axis=-1))]
            tri.sort(key=lambda t: -t[0])
            img = Image.new("L", (W, H), 0)
            dr = ImageDraw.Draw(img)
            for _d, cid, f in tri:
                dr.polygon([tuple(map(float, q)) for q in f], fill=cid)
            ids = np.asarray(img)
            gold = float((ids == 1).mean()) + share * float((ids == 2).mean())
            self.assertLessEqual(gold, 0.05, f"yaw {yaw}: {100 * gold:.2f}% gold")

    def test_hair_stays_outside_the_mantle(self):
        """§1.5: the long hair clears the mantle at rest and through his clips (no hair vertex inside the closed
        mantle plate, by its winding number)."""
        import numpy as np

        hc = self.rp.hero_clips
        persona = hc.PERSONA["sefir"]
        sk = self.rig.skeleton
        F = self.mantle.F
        poses = [{}]
        for clip in ("glance", "incline_head", "raise_palm", "talk"):
            L = hc.LENGTHS[clip]
            for t in (0.25 * L, 0.5 * L, 0.75 * L):
                poses.append(hc.staff_hold(hc.pose_at(clip, t, L, sk, persona), persona))
        for k, pose in enumerate(poses):
            turns = {b: v for b, v in pose.items() if b != "hips"}
            H = self._posed(self.hair, turns)
            M = self._posed(self.mantle, turns)
            lo, hi = M.min(axis=0) - 0.01, M.max(axis=0) + 0.01
            near = ((H >= lo) & (H <= hi)).all(axis=1)
            if not near.any():
                continue
            w = np.abs(self.rp.winding_number(H[near], M, F))
            self.assertFalse((w > 0.5).any(), f"pose {k}: {int((w > 0.5).sum())} hair vertices inside the mantle")


if __name__ == "__main__":
    unittest.main()
