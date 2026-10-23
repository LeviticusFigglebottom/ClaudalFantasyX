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

    def test_teeth_sample_their_own_patch_of_the_head_atlas(self):
        """M1-CHR-10: the teeth's colour and occlusion live in an unused corner of the head maps;
        no skin or mouth texel may land in it, and every tooth corner must sample inside it."""
        import numpy as np

        import asha_glb
        import asha_mouth

        js, bin_ = asha_glb.read_glb(OUT / "asha.glb")
        head = asha_glb.mesh_by_name(js, "Head")
        u0, v0, u1, v1 = asha_mouth.TEETH_UV
        for p in head["primitives"]:
            mat = js["materials"][p["material"]]["name"]
            if mat not in ("skin_head", "mouth", "teeth"):
                continue
            uv = asha_glb.accessor(js, bin_, p["attributes"]["TEXCOORD_0"]).astype(np.float64)
            u, v = uv[:, 0], uv[:, 1]  # glTF V runs down the image, as TEETH_UV does
            inside = (u >= u0) & (u <= u1) & (v >= v0) & (v <= v1)
            with self.subTest(material=mat):
                if mat == "teeth":
                    self.assertTrue(inside.all())
                else:
                    self.assertFalse(inside.any())

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

    def test_framing_lock_hangs_at_the_temple_outside_the_orbit(self):
        """M1-CHR-09: the lock was rooted over the brow tail and read as a streak across it."""
        import numpy as np

        import asha_hair

        part = asha_hair.front_strands(self.lm, self.body, self.extra["_hair"], np.random.default_rng([7, 3]))
        V = part.varr()
        self.assertEqual(len(V), self.extra["_hair"]["front_strands"] * self.extra["_hair"]["front_strand_ribbons"]
                         * asha_hair.LOCK_POINTS * 2)
        eye = self.body.face.eyes["R"]
        self.assertTrue((V[:, 0] < eye.E[0] - eye.R).all())  # her right, outside the eye socket
        drop = float(V[:, 2].max() - V[:, 2].min())
        self.assertGreater(drop, 0.06)  # asha.md §5: 6-8 cm
        self.assertLess(drop, 0.09)

    def test_upper_lip_outline_falls_from_the_bow_peaks(self):
        """M1-CHR-09: the contact line rises toward the corners; contact + bow height wobbled."""
        import numpy as np

        import asha_textures as at

        u = np.linspace(-1.0, 1.0, 4001)
        zl = 0.0015 * np.exp(-(((np.abs(u) - 0.8) / 0.12) ** 2))  # a corner hump like the donor's
        taper = np.clip(1.0 - u * u, 0.0, 1.0)
        hu = at.VERM_UP * taper ** 0.6 * (1.0 - at.VERM_DIP * np.exp(-((u / 0.10) ** 2)))
        out = zl + at.monotone_upper(zl, u, hu, np.ones_like(u))
        for sgn in (1.0, -1.0):
            m = (sgn * u >= at.VERM_PEAK_U) & (sgn * u <= at.VERM_CORNER_U)
            z = out[m][:: int(sgn)]
            self.assertTrue((np.diff(z) <= 1e-9).all(), sgn)
        mid = np.abs(u) < at.VERM_PEAK_U
        np.testing.assert_allclose(out[mid], (zl + hu)[mid], atol=1e-4)  # the bow itself is kept

    def test_lashes_are_tapered_clumps_over_a_dark_root_line(self):
        """M1-CHR-10: CHR-07's evenly spaced straight strands read as a comb of thin ticks."""
        import numpy as np

        import asha_textures as at

        h, w = 512, 1024
        a, _sid, _dep = at.lash_clumps(h, w, np.random.default_rng(43))
        upper = slice(4, int(at.LASH_LOWER_U * w) - 4)

        def row(v: float) -> np.ndarray:
            return a[int(v * h), upper] > 0.3

        def runs(on: np.ndarray) -> int:
            return int(np.count_nonzero(np.diff(on.astype(int)) == 1) + on[0])

        self.assertGreater(row(0.04).mean(), 0.7)  # the margin reads as one dark line
        mid = row(0.6)
        self.assertLess(mid.mean(), 0.45)  # out along the lashes there are gaps between clumps
        clumps = at.LASH_CLUMPS[0]
        self.assertGreater(runs(mid), clumps // 2)
        self.assertLess(runs(mid), clumps * 2)  # a few strands per point, not one tick per strand
        self.assertLess(row(0.85).mean(), mid.mean())  # and they taper to their tips

    def test_brow_strokes_fade_before_the_card_edges(self):
        """M1-CHR-10: hairs cut by the card's straight border drew a hard, flat lower edge."""
        import numpy as np

        import asha_textures as at

        alpha, _sid = at.brow_hairs(512, 1024, np.random.default_rng(5))
        cw = 1024 // at.BROW_LAYERS
        for layer in range(at.BROW_LAYERS):
            col = alpha[:, layer * cw:(layer + 1) * cw]
            edge = max(int(cw * 0.01), 1)
            with self.subTest(layer=layer):
                self.assertLess(col[:, :edge].max(), 0.15)  # bottom edge
                self.assertLess(col[:, -edge:].max(), 0.15)  # top edge
                self.assertGreater(col[:, cw // 3:2 * cw // 3].mean(), 3 * col[:, :cw // 8].mean())

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
