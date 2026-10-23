"""Tests for the Asha hero build (M1-CHR-02, assets_src/characters/asha/).

Run: python3 -m unittest discover -s tools/tests

* Pure-Python checks (always run): parameters, face-pose table vs the shared shape API, the
  committed GLBs (budget, blendshape names, eye nodes on the eye bones, materials, vertex colours)
  and textures (size cap, power-of-two sizes, mipmapped imports).
* Geometry checks without Blender: the part generators' triangle budgets (asha.md §8.1) and the
  blendshape builder (every API shape moves something; lids never enter the eyeball).
"""
import json
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "characters" / "asha"
OUT = ROOT / "assets" / "characters" / "asha"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT / "assets_src" / "characters" / "base_body"))

MAX_BYTES = 5 * 1024 * 1024  # ADR 0005 plain-blob cap
LOD0_MAX = 63_500  # asha.md §8.1 target (ceiling 70k)
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


def tri_count(js: dict, mesh_index: int) -> int:
    n = 0
    for prim in js["meshes"][mesh_index]["primitives"]:
        n += js["accessors"][prim["indices"]]["count"] // 3
    return n


class TestParams(unittest.TestCase):
    def test_params_load_and_match_the_sheet(self):
        import bb_params

        p = bb_params.load_params(path=str(SRC / "asha_params.json"))
        lm = bb_params.Landmarks(p)
        self.assertAlmostEqual(p["height_m"] / lm.h, 7.34, places=2)  # asha.md §1
        self.assertAlmostEqual(lm.eye_r, 0.0132, places=4)  # 12 mm x 1.10, character_shading.md
        self.assertAlmostEqual(lm.mouth_w / lm.head_w, 0.40, places=3)  # asha.md §6.1

    def test_face_pose_table_uses_the_shared_api(self):
        poses = json.loads((ROOT / "game/levels/_tests/characters/asha/asha_face_poses.json").read_text())
        tags = {e["id"] for e in json.loads((ROOT / "game/data/dialogue/emotions.json").read_text())["emotions"]}
        self.assertEqual(set(poses["emotions"]), tags)
        for tag, pose in poses["emotions"].items():
            for shape, w in pose.items():
                if isinstance(w, list):
                    self.assertIn(f"{shape}_L", API, (tag, shape))
                else:
                    self.assertTrue(shape in API or f"{shape}_L" in API, (tag, shape))


class TestCommittedAssets(unittest.TestCase):
    def test_lod0_budget_shapes_and_eyes(self):
        path = OUT / "asha.glb"
        self.assertTrue(path.exists(), path)
        self.assertLess(path.stat().st_size, MAX_BYTES)
        js = glb_json(path)
        total = sum(tri_count(js, i) for i in range(len(js["meshes"])))
        self.assertLessEqual(total, LOD0_MAX)
        self.assertGreaterEqual(total, 40_000)  # SPEC §7.3: 40-70k
        names = {}
        for m in js["meshes"]:
            names[m["name"]] = m.get("extras", {}).get("targetNames", [])
        head = [v for k, v in names.items() if k.startswith("Head")]
        self.assertTrue(head, list(names))
        for shape in API + VISEMES:
            self.assertIn(shape, head[0])
        nodes = js["nodes"]
        by_name = {n["name"]: i for i, n in enumerate(nodes)}
        for sd in ("L", "R"):
            bone = by_name[f"DEF-eye.{sd}"]
            kids = {nodes[c]["name"] for c in nodes[bone].get("children", [])}
            for part in ("Eye", "Cornea", "EyeOcclusion", "TearLine"):
                self.assertIn(f"{part}{sd}", kids)  # separate nodes on the eye bone (character_shading.md)
        mats = {m["name"] for m in js["materials"]}
        for m in ("skin_head", "skin_body", "eye", "cornea", "eye_occlusion", "tear_line", "hair", "cloth",
                  "cloth_sleeve", "lash", "brow"):
            self.assertIn(m, mats)
        # wind weights travel as vertex colour on hair and cloth
        for m in js["meshes"]:
            if m["name"].startswith(("Hair", "Costume", "VerseSleeve")):
                self.assertTrue(all("COLOR_0" in p["attributes"] for p in m["primitives"]), m["name"])

    def test_lod1_is_about_half(self):
        js0 = glb_json(OUT / "asha.glb")
        js1 = glb_json(OUT / "asha_lod1.glb")
        t0 = sum(tri_count(js0, i) for i in range(len(js0["meshes"])))
        t1 = sum(tri_count(js1, i) for i in range(len(js1["meshes"])))
        self.assertLess(t1, 0.6 * t0)
        self.assertGreater(t1, 0.35 * t0)
        self.assertLess((OUT / "asha_lod1.glb").stat().st_size, MAX_BYTES)

    def test_textures_small_power_of_two_and_mipmapped(self):
        from PIL import Image

        tex = sorted((OUT / "textures").glob("*.png"))
        self.assertGreaterEqual(len(tex), 20)
        for p in tex:
            self.assertLess(p.stat().st_size, MAX_BYTES, p.name)
            with Image.open(p) as im:
                w, h = im.size
            self.assertEqual(w & (w - 1), 0, p.name)
            self.assertEqual(h & (h - 1), 0, p.name)
            self.assertLessEqual(max(w, h), 2048, p.name)  # 2K face textures (ADR 0005, no LFS)
            imp = p.with_name(p.name + ".import")
            self.assertTrue(imp.exists(), imp.name)
            self.assertIn("mipmaps/generate=true", imp.read_text(), imp.name)
        with Image.open(OUT / "textures" / "asha_head_albedo.png") as im:
            head = im.size
        self.assertEqual(head, (2048, 2048))


class TestGenerators(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import bb_anatomy
        import bb_params

        cls.params = bb_params.load_params(path=str(SRC / "asha_params.json"))
        cls.extra = json.loads((SRC / "asha_params.json").read_text())
        cls.lm = bb_params.Landmarks(cls.params)
        cls.body = bb_anatomy.Body(cls.lm)

    def test_part_budgets(self):
        import asha_costume
        import asha_eyes
        import asha_hair

        costume = asha_costume.build_costume(self.body, self.extra["_costume"])
        self.assertLess(sum(p.tris() for p in costume.values()), 18_200)  # asha.md §8.1 cloth lines
        hair = asha_hair.build_hair(self.lm, self.body, self.extra["_hair"])
        self.assertLess(sum(p.tris() for p in hair.values()), 16_000)
        eyes = 0
        for sd in ("L", "R"):
            fr = self.body.face.eyes[sd]
            for part in (asha_eyes.eyeball(fr), asha_eyes.cornea(fr), asha_eyes.occlusion(fr), asha_eyes.tear_line(fr)):
                eyes += part.tris()
        self.assertLessEqual(eyes, 2_400)
        sl = costume["VerseSleeve"]
        v = [uv[1] for face in sl.UV for uv in face]
        self.assertAlmostEqual(min(v), 0.0)  # UV.y shoulder 0 -> cuff tip 1 (character_shading.md)
        self.assertAlmostEqual(max(v), 1.0)

    def test_every_shape_moves_and_lids_stay_off_the_globe(self):
        import numpy as np

        import asha_face_shapes

        face = self.body.face
        rng = np.random.default_rng(3)
        pts = []
        for sd in ("L", "R"):  # samples on the lid solid around each eye, plus the lower face
            fr = face.eyes[sd]
            d = rng.normal(size=(800, 3))
            d[:, 1] = -np.abs(d[:, 1])
            d /= np.linalg.norm(d, axis=1, keepdims=True)
            pts.append(fr.E + d * (fr.R + 0.0019))
        M = self.lm.P("mouth")
        pts.append(M + rng.uniform(-0.04, 0.04, (3000, 3)) * np.array([1.0, 0.2, 1.0]))
        V = np.concatenate(pts)
        S = asha_face_shapes.build_shapes(face, self.lm, V, np.zeros(len(V), dtype=int))
        for name in API + VISEMES:
            self.assertGreater(float(np.abs(S[name]).max()), 1e-4, name)
        for sd in ("L", "R"):
            fr = face.eyes[sd]
            for name in (f"lid_close_{sd}", f"lid_wide_{sd}", f"lid_squint_{sd}"):
                moved = V + S[name]
                near = np.linalg.norm(V - fr.E, axis=1) < fr.R + 0.003
                r = np.linalg.norm(moved[near] - fr.E, axis=1)
                self.assertGreater(float(r.min()), fr.R, name)


if __name__ == "__main__":
    unittest.main()
