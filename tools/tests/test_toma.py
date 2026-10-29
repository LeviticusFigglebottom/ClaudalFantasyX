"""Tests for the Toma hero build (M2-CHR-02, assets_src/characters/toma/).

Run: python3 -m unittest discover -s tools/tests

* Pure-Python checks: parameters against toma.md, the face-pose table against the shared shape API
  and the sheet's §6 table (brows with the 1.15 range), the committed GLBs (budget, blendshape names,
  every material has a hero material, the prop nodes), textures (size cap, power-of-two) and
  materials (every texture exists).
* Geometry checks without Blender: the costume charts fit the atlas, the asymmetric hallmark (the
  pauldron on the LEFT shoulder, the shield on his back, the spear at his right side), the reach-band
  counts, the hair and beard lengths.
* The chiselled scar (toma.md §3): inside its circle the cut goes through both lacquer layers
  everywhere (no lacquer island of any shape survives), and the strokes are radial.
"""
import json
import math
import re
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "characters" / "toma"
OUT = ROOT / "assets" / "characters" / "toma"
STAGE = ROOT / "game" / "levels" / "_tests" / "characters" / "toma"
for sub in ("toma", "rhen", "asha", "base_body"):
    sys.path.insert(0, str(ROOT / "assets_src" / "characters" / sub))

MAX_BYTES = 5 * 1024 * 1024  # ADR 0005 plain-blob cap
LOD0_MAX = 66_000  # toma.md §8 target
LOD1_MAX = 33_000
PAIRED = ["brow_inner_up", "brow_down", "brow_outer_up", "lid_close", "lid_wide", "lid_squint", "cheek_raise",
          "nose_sneer", "mouth_smile", "mouth_frown", "mouth_stretch", "mouth_dimple"]
SINGLE = ["mouth_press", "mouth_pucker", "lip_upper_up", "lip_lower_down", "jaw_open", "jaw_clench"]
VISEMES = ["vis_rest", "vis_aa", "vis_e", "vis_i", "vis_o", "vis_u", "vis_mbp", "vis_fv", "vis_l", "vis_st"]
API = [f"{b}_{s}" for b in PAIRED for s in ("L", "R")] + SINGLE
# toma.md §6, the emotion table (brow weights with the 1.15 range already applied)
SHEET = {
    "smile": {"cheek_raise": 0.55, "lid_squint": 0.35, "mouth_smile": 0.60},
    "grief": {"brow_inner_up": 1.00, "brow_down": 0.45, "lid_squint": 0.45, "mouth_frown": 0.50, "jaw_clench": 0.35},
    "angry": {"brow_down": 0.95, "lid_squint": 0.25, "nose_sneer": 0.20, "jaw_clench": 0.60},
    "guilty": {"brow_inner_up": 0.60, "lid_close": 0.40, "mouth_press": 0.40},
}


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

        p = bb_params.load_params(path=str(SRC / "toma_params.json"))
        lm = bb_params.Landmarks(p)
        self.assertAlmostEqual(p["height_m"], 1.89)  # toma.md §1
        self.assertAlmostEqual(p["height_m"] / lm.h, 7.50, places=2)
        self.assertAlmostEqual(p["ipd_m"], 0.065)
        self.assertEqual(p["skin_hex"], "#8A5A3E")  # skin_toma
        self.assertEqual(p["femininity"], 0.0)
        c = json.loads((SRC / "toma_params.json").read_text())["_costume"]
        self.assertEqual(c["reach_bands"], {"L": 11, "R": 9})  # toma.md §9
        self.assertAlmostEqual(c["shield_diameter_m"], 0.92)
        self.assertAlmostEqual(c["spear_length_m"], 2.10)
        self.assertAlmostEqual(c["sash_width_m"], 0.18)
        self.assertEqual(c["shield_scutes"], 13)
        self.assertEqual(c["pauldron_lames"], 5)

    def test_face_poses_cover_every_emotion_with_api_shapes(self):
        poses = json.loads((STAGE / "toma_face_poses.json").read_text())
        tags = {e["id"] for e in json.loads((ROOT / "game/data/dialogue/emotions.json").read_text())["emotions"]}
        self.assertEqual(set(poses["emotions"]), tags)
        names = set(PAIRED) | set(SINGLE) | set(API)
        for tag, pose in poses["emotions"].items():
            for shape, w in pose.items():
                self.assertIn(shape, names, f"{tag}: {shape}")
                for x in (w if isinstance(w, list) else [w]):
                    self.assertTrue(0.0 <= x <= 1.0, f"{tag}: {shape}")

    def test_face_poses_follow_the_sheet(self):
        """toma.md §6: the table already carries the brows' 1.15 range; smiles read through the
        cheeks and lids (the beard hides the mouth corners); blend 0.22 s."""
        poses = json.loads((STAGE / "toma_face_poses.json").read_text())
        self.assertAlmostEqual(poses["blend_in_s"], 0.22)
        self.assertAlmostEqual(poses["brow_range"], 1.15)
        for tag, want in SHEET.items():
            self.assertEqual(poses["emotions"][tag], want, tag)
        for tag in ("soft_smile", "smile", "laugh"):
            self.assertGreater(poses["emotions"][tag]["cheek_raise"], 0.0, tag)
            self.assertGreater(poses["emotions"][tag]["lid_squint"], 0.0, tag)


class TestCommitted(unittest.TestCase):
    def test_glbs(self):
        js = glb_json(OUT / "toma.glb")
        self.assertLessEqual(tris(js), LOD0_MAX)
        self.assertLessEqual(tris(glb_json(OUT / "toma_lod1.glb")), LOD1_MAX)
        for name in ("toma.glb", "toma_lod1.glb"):
            self.assertLess((OUT / name).stat().st_size, MAX_BYTES, name)
        nodes = {n.get("name") for n in js["nodes"]}
        for n in ("Head", "Body", "Costume", "Props", "HairHead", "DEF-eye.L", "DEF-eye.R"):
            self.assertIn(n, nodes)
        head = next(m for m in js["meshes"] if m.get("name") == "Head")
        targets = head.get("extras", {}).get("targetNames", [])
        self.assertEqual(targets, API + VISEMES)
        head_mats = {js["materials"][p["material"]]["name"] for p in head["primitives"]}
        self.assertTrue({"beard", "beard_grey"} <= head_mats, "the beard rides the Head's shapes")

    def test_rig_extras(self):
        """toma.md §9 (M2-CHR-04): the sash-tail chains (2 x 4), the pauldron hinge, the shield and the spear
        prop bone are extra DEF-* joints with the right parents, after the 75 standard bones in their own order,
        and vertices are weighted to each of them."""
        js = glb_json(OUT / "toma.glb")
        nodes = js["nodes"]
        joints = [nodes[i]["name"] for i in js["skins"][0]["joints"]]
        parent = {c: i for i, n in enumerate(nodes) for c in n.get("children", [])}
        idx = {n.get("name"): i for i, n in enumerate(nodes)}
        want = {"DEF-pauldron": "DEF-shoulder.L", "DEF-shield": "DEF-spine.003", "DEF-spear": "DEF-hand.R",
                # M1-CHR-15: the shoulder correctives (every hero)
                "DEF-armpit.L": "DEF-shoulder.L", "DEF-armpit.R": "DEF-shoulder.R"}
        for root in ("DEF-sash_tail_a", "DEF-sash_tail_b"):
            chain = [root] + [f"{root}.{i:03d}" for i in range(1, 4)]
            want[chain[0]] = "DEF-spine"
            for a, b in zip(chain, chain[1:]):
                want[b] = a
        for name, par in want.items():
            self.assertIn(name, joints)
            self.assertEqual(nodes[parent[idx[name]]]["name"], par, name)
        standard = [j for j in joints if j not in want]
        self.assertEqual(len(standard), 75)
        old = glb_json(OUT / "toma_lod1.glb")
        lod_std = [old["nodes"][i]["name"] for i in old["skins"][0]["joints"] if old["nodes"][i]["name"] not in want]
        self.assertEqual(standard, lod_std, "the LOD1 skeleton matches")
        # every extra bone carries weights in the LOD0 file
        import numpy as np

        data = (OUT / "toma.glb").read_bytes()
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
        self.assertEqual(set(want) - weighted, set(), "every extra bone has vertices on it")

    def test_every_gltf_material_has_a_hero_material(self):
        mats = {m["name"] for m in glb_json(OUT / "toma.glb")["materials"]}
        have = {p.stem for p in (OUT / "materials").glob("*.tres")}
        self.assertEqual(mats - have, set())
        stage = (STAGE / "toma_stage.tscn").read_text()
        for m in mats:
            self.assertIn(f'"{m}": ExtResource("m_{m}")', stage)

    def test_material_textures_exist(self):
        for tres in (OUT / "materials").glob("*.tres"):
            for path in re.findall(r'path="res://([^"]+)"', tres.read_text()):
                self.assertTrue((ROOT / path).exists(), f"{tres.name}: {path}")

    def test_textures(self):
        from PIL import Image

        files = sorted((OUT / "textures").glob("*.png"))
        self.assertEqual(len(files), 17)  # M2-CHR-04: + toma_shorthair.png
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

        cls.params = bb_params.load_params(path=str(SRC / "toma_params.json"))
        cls.extra = json.loads((SRC / "toma_params.json").read_text())
        cls.lm = bb_params.Landmarks(cls.params)
        cls.body = bb_anatomy.Body(cls.lm)

    def test_costume_charts_and_hallmarks(self):
        import numpy as np

        import toma_costume
        import toma_props

        c = self.extra["_costume"]
        out, anchors = toma_costume.build_costume(self.body, c)
        self.assertLess(sum(p.tris() for p in out.values()), 22_000)
        for name, part in out.items():
            uv = np.array([q for face in part.UV for q in face])
            self.assertTrue(((uv >= -1e-9) & (uv <= 1 + 1e-9)).all(), name)
        # the pauldron on his left shoulder (+X), above and outside the shoulder line
        P = out["Pauldron"].varr()
        self.assertGreater(P[:, 0].min(), 0.05)
        self.assertGreater(P[:, 2].max(), self.lm.P("acromion")[2] + 0.06)
        self.assertGreater(P[:, 0].max(), self.lm.P("acromion")[0] + 0.10)
        # the sash knot at the left front
        knot = out["Sash"].varr()
        self.assertGreater(float(knot[:, 0].max()), 0.1)
        # the shield behind him, wider than his shoulders; the spear at his right side, 2.10 m
        allv = np.concatenate([p.varr() for p in out.values()])
        centre, o, u = toma_props.place_shield(c, allv, anchors["chest_z"])
        sh = toma_props.shield(centre, o, u, c).varr()
        self.assertGreater(float(sh[:, 1].min()), 0.0)
        self.assertGreater(float(sh[:, 0].max() - sh[:, 0].min()), 0.9)
        sp = toma_props.spear(self.lm, c, toma_costume.ATLAS["grip"]).varr()
        self.assertLess(float(sp[:, 0].max()), 0.0)
        along = sp @ toma_props.spear_axis(self.lm)  # M2-CHR-515: built through the fist, along the held line
        self.assertAlmostEqual(float(along.max() - along.min()), c["spear_length_m"], delta=0.03)

    def test_scutes_are_thirteen_cells_in_the_disc(self):
        import numpy as np

        import toma_props

        c = self.extra["_costume"]
        seeds = toma_props.scute_seeds(c)
        self.assertEqual(len(seeds), 13)
        R = 0.5 * c["shield_diameter_m"] - c["shield_rim_m"]
        self.assertTrue((np.hypot(seeds[:, 0], seeds[:, 1]) < R).all())

    def test_scar_has_no_surviving_lacquer_inside(self):
        """toma.md §3: no trace of the emblem may remain. Inside the circle (bar the chipped rim) the
        cut is below both lacquer layers at every point, so no red or black island of any shape is
        left; the strokes run radially (within 60 degrees of the direction from the centre)."""
        import numpy as np

        import toma_costume as C

        c = self.extra["_costume"]
        R = c["scar_radius_m"]
        g = np.linspace(-R, R, 241)
        X, Y = np.meshgrid(g, g)
        inside = np.hypot(X, Y) < R * (1.0 - C.SCAR_RIM_NOISE) - 0.004
        d = C.scar_depth(c, X, Y)
        self.assertGreater(float(d[inside].min()), C.LACQUER_RED_M + C.LACQUER_BLACK_M)
        strokes = C.scar_strokes(c)
        self.assertTrue(40 <= len(strokes) <= 60)
        radial = np.arctan2(strokes[:, 1], strokes[:, 0])
        off = np.abs(np.angle(np.exp(1j * (strokes[:, 2] - radial))))
        off = np.minimum(off, math.pi - off)
        self.assertLess(float(np.median(off)), math.radians(30))

    def test_hair_and_beard_are_short(self):
        import numpy as np

        import toma_hair

        hair = toma_hair.build_hair(self.lm, self.body, self.extra["_hair"])
        n = sum(p.tris() for p in hair.values())
        self.assertLess(n, 8_000)  # toma.md §8 (hair and beard cards)
        V = np.concatenate([p.varr() for p in hair.values()])
        crown = self.lm.P("crown")
        self.assertLess(float(np.linalg.norm(V - crown, axis=1).max()), 0.17)
        lo, hi = self.extra["_hair"]["length_m"]
        self.assertLessEqual(hi, 0.013)
        blo, bhi = self.extra["_beard"]["length_m"]
        self.assertTrue(0.010 <= blo and bhi <= 0.016)


if __name__ == "__main__":
    unittest.main()
