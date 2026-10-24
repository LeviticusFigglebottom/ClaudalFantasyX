"""Tests for the Rhen hero build (M2-CHR-01, assets_src/characters/rhen/).

Run: python3 -m unittest discover -s tools/tests

* Pure-Python checks: parameters against rhen.md, the face-pose table against the shared shape API
  and his crooked smile, the committed GLBs (budget, blendshape names, materials each have a hero
  material, the prop nodes), textures (size cap, power-of-two) and materials (every texture exists).
* Geometry checks without Blender: the costume charts fit the atlas, the asymmetric hallmark (one
  left sleeve, the lantern on the right shoulder blade, the coil on the left hip), hair length.
"""
import json
import re
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "characters" / "rhen"
OUT = ROOT / "assets" / "characters" / "rhen"
STAGE = ROOT / "game" / "levels" / "_tests" / "characters" / "rhen"
for sub in ("rhen", "asha", "base_body"):
    sys.path.insert(0, str(ROOT / "assets_src" / "characters" / sub))

MAX_BYTES = 5 * 1024 * 1024  # ADR 0005 plain-blob cap
LOD0_MAX = 58_500  # rhen.md §8 target
LOD1_MAX = 30_000
PAIRED = ["brow_inner_up", "brow_down", "brow_outer_up", "lid_close", "lid_wide", "lid_squint", "cheek_raise",
          "nose_sneer", "mouth_smile", "mouth_frown", "mouth_stretch", "mouth_dimple"]
SINGLE = ["mouth_press", "mouth_pucker", "lip_upper_up", "lip_lower_down", "jaw_open", "jaw_clench"]
VISEMES = ["vis_rest", "vis_aa", "vis_e", "vis_i", "vis_o", "vis_u", "vis_mbp", "vis_fv", "vis_l", "vis_st"]
API = [f"{b}_{s}" for b in PAIRED for s in ("L", "R")] + SINGLE


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

        p = bb_params.load_params(path=str(SRC / "rhen_params.json"))
        lm = bb_params.Landmarks(p)
        self.assertAlmostEqual(p["height_m"], 1.77)  # rhen.md §1
        self.assertAlmostEqual(p["height_m"] / lm.h, 7.47, places=2)
        self.assertAlmostEqual(p["ipd_m"], 0.064)
        self.assertEqual(p["skin_hex"], "#A87556")  # skin_rhen
        self.assertEqual(p["femininity"], 0.0)

    def test_face_poses_cover_every_emotion_with_api_shapes(self):
        poses = json.loads((STAGE / "rhen_face_poses.json").read_text())
        tags = {e["id"] for e in json.loads((ROOT / "game/data/dialogue/emotions.json").read_text())["emotions"]}
        self.assertEqual(set(poses["emotions"]), tags)
        names = set(PAIRED) | set(SINGLE) | set(API)
        for tag, pose in poses["emotions"].items():
            for shape, w in pose.items():
                self.assertIn(shape, names, f"{tag}: {shape}")
                for x in (w if isinstance(w, list) else [w]):
                    self.assertTrue(0.0 <= x <= 1.0, f"{tag}: {shape}")

    def test_crooked_smile(self):
        """rhen.md §6: mouth_smile R = L x 1.25 and a right dimple with the smile. The sheet's table
        gives soft_smile a 0.1 dimple although its R smile is 0.35 (the prose says 0.3 above 0.3);
        the table is followed and the mismatch is logged in rhen_review.md for Art."""
        poses = json.loads((STAGE / "rhen_face_poses.json").read_text())["emotions"]
        for tag in ("soft_smile", "smile", "laugh"):
            left, right = poses[tag]["mouth_smile"]
            self.assertAlmostEqual(right, min(1.0, left * 1.25), delta=0.0051, msg=tag)
            self.assertGreater(poses[tag]["mouth_dimple_R"], 0.0, tag)
        self.assertEqual(poses["smile"]["mouth_dimple_R"], 0.3)
        self.assertEqual(poses["laugh"]["mouth_dimple_R"], 0.3)


class TestCommitted(unittest.TestCase):
    def test_glbs(self):
        js = glb_json(OUT / "rhen.glb")
        self.assertLessEqual(tris(js), LOD0_MAX)
        self.assertLessEqual(tris(glb_json(OUT / "rhen_lod1.glb")), LOD1_MAX)
        for name in ("rhen.glb", "rhen_lod1.glb"):
            self.assertLess((OUT / name).stat().st_size, MAX_BYTES, name)
        nodes = {n.get("name") for n in js["nodes"]}
        for n in ("Head", "Body", "Costume", "Props", "HairHead", "DEF-eye.L", "DEF-eye.R"):
            self.assertIn(n, nodes)
        head = next(m for m in js["meshes"] if m.get("name") == "Head")
        targets = head.get("extras", {}).get("targetNames", [])
        self.assertEqual(targets, API + VISEMES)

    def test_every_gltf_material_has_a_hero_material(self):
        mats = {m["name"] for m in glb_json(OUT / "rhen.glb")["materials"]}
        have = {p.stem for p in (OUT / "materials").glob("*.tres")}
        self.assertEqual(mats - have, set())
        stage = (STAGE / "rhen_stage.tscn").read_text()
        for m in mats:
            self.assertIn(f'"{m}": ExtResource("m_{m}")', stage)

    def test_material_textures_exist(self):
        for tres in (OUT / "materials").glob("*.tres"):
            for path in re.findall(r'path="res://([^"]+)"', tres.read_text()):
                self.assertTrue((ROOT / path).exists(), f"{tres.name}: {path}")

    def test_textures(self):
        from PIL import Image

        files = sorted((OUT / "textures").glob("*.png"))
        self.assertEqual(len(files), 12)
        for f in files:
            self.assertLess(f.stat().st_size, MAX_BYTES, f.name)
            with Image.open(f) as im:
                w, h = im.size
            self.assertEqual(w & (w - 1), 0, f.name)
            self.assertEqual(h & (h - 1), 0, f.name)


class TestGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import bb_anatomy
        import bb_params

        cls.params = bb_params.load_params(path=str(SRC / "rhen_params.json"))
        cls.extra = json.loads((SRC / "rhen_params.json").read_text())
        cls.lm = bb_params.Landmarks(cls.params)
        cls.body = bb_anatomy.Body(cls.lm)

    def test_costume_charts_and_hallmarks(self):
        import numpy as np

        import rhen_costume
        import rhen_props

        out, anchors = rhen_costume.build_costume(self.body, self.extra["_costume"])
        self.assertLess(sum(p.tris() for p in out.values()), 18_000)
        for name, part in out.items():
            uv = np.array([c for face in part.UV for c in face])
            self.assertTrue(((uv >= -1e-9) & (uv <= 1 + 1e-9)).all(), name)
        # one sleeve, on his left (+X); the coil on the left hip; the lantern high on the right
        self.assertGreater(out["Sleeve"].varr()[:, 0].min(), 0.0)
        self.assertGreater(out["TetherCoil"].varr()[:, 0].mean(), 0.1)
        lan = rhen_props.lantern(anchors["lantern_strap"], anchors["lantern_normal"], self.lm,
                                 self.extra["_costume"]["lantern_height_m"] * self.lm.S)
        V = lan.varr()
        self.assertLess(V[:, 0].mean(), 0.0)  # his right
        self.assertGreater(V[:, 1].mean(), 0.0)  # behind him
        self.assertGreater(V[:, 2].max(), self.lm.P("acromion")[2] + 0.05)  # breaks the shoulder line
        hooks = rhen_props.reef_hooks(anchors["back_small"], anchors["hip_x"], self.lm,
                                      self.extra["_costume"]["hook_length_m"]).varr()
        self.assertGreater(hooks[:, 0].max(), anchors["hip_x"])  # grips past both hips
        self.assertLess(hooks[:, 0].min(), -anchors["hip_x"])

    def test_hair_is_short(self):
        import numpy as np

        import rhen_hair

        hair = rhen_hair.build_hair(self.lm, self.body, self.extra["_hair"])
        self.assertLess(sum(p.tris() for p in hair.values()), 9_000)  # rhen.md §8
        V = np.concatenate([p.varr() for p in hair.values()])
        crown = self.lm.P("crown")
        self.assertLess(float(np.linalg.norm(V - crown, axis=1).max()), 0.20)  # nothing hangs below the ears
        zc = self.lm.P("chin")[2]
        self.assertGreater(float(V[:, 2].min()), zc + 0.15 * self.lm.h)


if __name__ == "__main__":
    unittest.main()
