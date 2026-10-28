"""Tests for the Inquisitor Hadric Moll build (M3-CHR-507, assets_src/characters/moll/).

Run: python3 -m unittest tools.tests.test_moll

* Pure-Python checks: the sheet's §1 numbers in moll_params.json; the costume's M1-CHR-14 rules on the charts (the
  jack's and the cuirass's armholes at least 11.5 cm under the shoulder joint, four rows that step out going up); the
  Level emblem (a ring crossed by a bar that runs past it); the props' sizes (§3: a 2.1 m haft, a 22 cm ring of
  2.4 cm stock with a bar 4 cm past it each side; a 0.62 m shield); the echo watch (no black, no spikes, no yellow);
  Toma's builders called without the new arguments still give Toma's pauldron and shield.
* The committed GLBs: budgets and sizes (§7), the mesh names the rig guards use, the Head's 40 shapes, the rig
  extras and their parents, textures (size cap, power of two) and materials (the ember off by default).
* The rules on the shipped mesh (rig_probe reads the GLB, no Blender): the iron and the shield rigid on their bones,
  the pauldrons on their hinges and upper arms, the sandals on the feet, the knees kept under the trousers.
"""
import colorsys
import json
import re
import struct
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "characters" / "moll"
OUT = ROOT / "assets" / "characters" / "moll"
for sub in ("moll", "villagers", "toma", "rhen", "asha", "base_body"):
    sys.path.insert(0, str(ROOT / "assets_src" / "characters" / sub))
sys.path.insert(0, str(ROOT / "tools" / "dev"))

MAX_BYTES = 5 * 1024 * 1024  # ADR 0005 plain-blob cap; hadric_moll.md §7: moll.glb < 5 MiB, every PNG too
LOD1_MAX_BYTES = int(1.5 * 1024 * 1024)  # §7: moll_lod1.glb < 1.5 MB (pipeline.md §14)
LOD0_MAX = 55_000  # §7
LOD1_MAX = 26_000
PAIRED = ["brow_inner_up", "brow_down", "brow_outer_up", "lid_close", "lid_wide", "lid_squint", "cheek_raise",
          "nose_sneer", "mouth_smile", "mouth_frown", "mouth_stretch", "mouth_dimple"]
SINGLE = ["mouth_press", "mouth_pucker", "lip_upper_up", "lip_lower_down", "jaw_open", "jaw_clench"]
VISEMES = ["vis_rest", "vis_aa", "vis_e", "vis_i", "vis_o", "vis_u", "vis_mbp", "vis_fv", "vis_l", "vis_st"]
API = [f"{b}_{s}" for b in PAIRED for s in ("L", "R")] + SINGLE
SHEET_PARAMS = {"height_m": 1.78, "heads_tall": 7.4, "femininity": 0.0}
MESHES = ("Head", "Body", "Costume", "Sleeves", "HairHead", "Iron", "Shield")
EXTRA_BONES = {"DEF-pauldron.L": "DEF-shoulder.L", "DEF-pauldron.R": "DEF-shoulder.R", "DEF-iron": "DEF-hand.R",
               "DEF-shield": "DEF-forearm.L"}


def params() -> dict:
    return json.loads((SRC / "moll_params.json").read_text(encoding="utf-8"))


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

    return bb_donor.fit(bb_params.load_params(path=str(SRC / "moll_params.json"))).lm


class TestParams(unittest.TestCase):
    def test_sheet_numbers(self):
        p = params()
        for key, want in SHEET_PARAMS.items():
            self.assertEqual(p[key], want, key)
        import bb_params

        bb = bb_params.load_params(path=str(SRC / "moll_params.json"))
        self.assertAlmostEqual(bb["height_m"] / bb_params.Landmarks(bb).h, 7.4, places=2)
        self.assertAlmostEqual(p["_skin"]["age"], 0.4)  # §5: the villager age terms at 0.4
        c = p["_costume"]
        self.assertEqual((c["iron_haft_m"], c["iron_haft_diameter_m"], c["iron_ring_m"], c["iron_stock_m"],
                          c["iron_bar_past_m"], c["iron_band_m"]), (2.1, 0.032, 0.22, 0.024, 0.04, 0.08))
        self.assertEqual((c["shield_diameter_m"], c["shield_dome_m"], c["sash_width_m"]), (0.62, 0.06, 0.14))
        self.assertEqual((c["cuirass_rows"], c["pauldron_lames"]), (4, 5))


class TestCostumeCharts(unittest.TestCase):
    def test_armholes_are_dropped(self):
        """M1-CHR-14: the jack's and the cuirass's side lines at least 11.5 cm under the shoulder joint."""
        import moll_costume as C
        from asha_costume import TorsoChart

        lm = landmarks()
        chart = TorsoChart(lm)
        sh = float(lm.side_pt("shoulder", "L")[2])
        sides = np.array([90.0, -90.0])
        for z in np.concatenate([C.jack_top(lm, chart, sides), C.cuirass_top(lm, sides, params()["_costume"])]):
            self.assertLessEqual(float(z), sh - 0.115 + 1e-6)

    def test_rows_overlap_and_step_out_going_up(self):
        import moll_costume as C

        lm = landmarks()
        c = params()["_costume"]
        rows = C.cuirass_rows(lm, np.array([0.0, 180.0]), c)
        self.assertEqual(len(rows), 4)
        for (t0, b0), (t1, b1) in zip(rows, rows[1:]):
            self.assertTrue(np.all(t1 > b0), "neighbouring rows overlap")
            self.assertTrue(np.all(t1 < t0))
        offs = [C.row_offset(k, 4) for k in range(4)]
        self.assertEqual(offs, sorted(offs, reverse=True))  # the top row outermost: the profile steps down

    def test_the_level_is_whole(self):
        """§4 #3: a ring crossed by a bar that runs past it each side (no chisel strokes)."""
        import moll_costume as C

        c = params()["_costume"]
        R = c["emblem_radius_m"]
        m = lambda x, y: float(C.emblem_mask(c, np.array([x]), np.array([y]))[0])  # noqa: E731
        self.assertGreater(m(0.0, R), 0.99)  # the ring, top
        self.assertGreater(m(R, 0.0), 0.99)  # the ring and the bar, side
        self.assertGreater(m(0.0, 0.0), 0.99)  # the bar through the centre
        self.assertGreater(m(R + c["emblem_bar_past_m"] * 0.9, 0.0), 0.99)  # the bar past the ring
        self.assertLess(m(0.5 * R, 0.5 * R), 0.01)  # open inside the ring
        self.assertLess(m(0.0, R + 0.02), 0.01)
        self.assertLess(C.emblem_relief(c, np.array([0.0]), np.array([0.0]))[0], 0.0)  # raised, not cut

    def test_toma_builders_default_to_toma(self):
        """The new optional arguments of toma_costume.pauldron and toma_props.shield default to Toma's own values."""
        import inspect

        import toma_costume
        import toma_props

        sig = inspect.signature(toma_costume.pauldron).parameters
        self.assertIsNone(sig["relief"].default)
        self.assertEqual(sig["top_grid"].default, toma_costume.TOP_GRID)
        self.assertEqual(sig["lame_grid"].default, toma_costume.LAME_GRID)
        sig = inspect.signature(toma_props.shield).parameters
        self.assertEqual((sig["rings"].default, sig["segs"].default), (toma_props.SHIELD_RINGS, toma_props.SHIELD_SEGS))


class TestProps(unittest.TestCase):
    def test_iron_is_held_and_grounded(self):
        import moll_props as MP
        from asha_staff import held_frame

        lm = landmarks()
        c = params()["_costume"]
        iron = MP.iron(lm, c).varr()
        grip, R = held_frame(lm, "R", MP.iron_radius(c))
        up = np.linalg.inv(R) @ (iron - grip).T  # back to the upright build
        P = up.T + grip
        self.assertAlmostEqual(float(P[:, 2].min()), 0.006, places=3)  # its foot on the floor
        top = float(P[:, 2].max())
        self.assertGreater(top, c["iron_haft_m"] + c["iron_ring_m"] * 0.9)  # the Level over the haft
        head = P[P[:, 2] > c["iron_haft_m"] + 0.02]
        self.assertAlmostEqual(float(np.ptp(head[:, 0])), c["iron_ring_m"] + 2 * c["iron_bar_past_m"], delta=0.01)
        self.assertLess(MP.iron(lm, c).tris(), 1700)  # §7: 1.6k


class TestCommitted(unittest.TestCase):
    def test_glbs(self):
        js = glb_json(OUT / "moll.glb")
        self.assertLessEqual(tris(js), LOD0_MAX)
        self.assertLessEqual(tris(glb_json(OUT / "moll_lod1.glb")), LOD1_MAX)
        self.assertLess((OUT / "moll.glb").stat().st_size, MAX_BYTES)
        self.assertLess((OUT / "moll_lod1.glb").stat().st_size, LOD1_MAX_BYTES)
        meshes = {m.get("name") for m in js["meshes"]}
        for n in MESHES:
            self.assertIn(n, meshes)
        head = next(m for m in js["meshes"] if m.get("name") == "Head")
        self.assertEqual(head.get("extras", {}).get("targetNames", []), API + VISEMES)  # the hero face's 40 shapes

    def test_rig_extras(self):
        js = glb_json(OUT / "moll.glb")
        nodes = js["nodes"]
        joints = [nodes[i]["name"] for i in js["skins"][0]["joints"]]
        parent = {c: i for i, n in enumerate(nodes) for c in n.get("children", [])}
        idx = {n.get("name"): i for i, n in enumerate(nodes)}
        for name, par in EXTRA_BONES.items():
            self.assertIn(name, joints)
            self.assertEqual(nodes[parent[idx[name]]]["name"], par, name)
        self.assertEqual(len([j for j in joints if j not in EXTRA_BONES]), 77)  # 75 standard + the correctives

    def test_materials_and_textures(self):
        from PIL import Image

        js = glb_json(OUT / "moll.glb")
        mats = {m["name"] for m in js["materials"]}
        have = {p.stem for p in (OUT / "materials").glob("*.tres")}
        self.assertEqual(mats - have, set(), "every glTF material has a hero material")
        for want in ("hair", "hair_grey", "cloth", "iron", "shield", "bronze"):
            self.assertIn(want, mats)
        for png in (OUT / "textures").glob("*.png"):
            self.assertLess(png.stat().st_size, MAX_BYTES, png.name)
            with Image.open(png) as im:
                w, h = im.size
            self.assertEqual(w & (w - 1), 0, png.name)
            self.assertEqual(h & (h - 1), 0, png.name)
        for tres in (OUT / "materials").glob("*.tres"):
            for path in re.findall(r'path="res://([^"]+)"', tres.read_text(encoding="utf-8")):
                self.assertTrue((ROOT / path).exists(), f"{tres.name}: {path}")
        iron = (OUT / "materials" / "iron.tres").read_text(encoding="utf-8")
        self.assertIn("emission_energy_multiplier = 0.0", iron)  # §3: the ember is off by default
        self.assertIn("moll_iron_ember.png", iron)

    def test_no_black_and_no_yellow_in_the_cloth(self):
        """§4: nothing black on him (the iron is the iron); §6: no yellow (the gold leaf is a thin piping and the Level,
        under 3% of the atlas), no teal."""
        from PIL import Image

        im = np.asarray(Image.open(OUT / "textures" / "moll_cloth_albedo.png").convert("RGB").resize((256, 256)))
        hsv = np.array([colorsys.rgb_to_hsv(*(px / 255.0)) for px in im.reshape(-1, 3)])
        yellow = (hsv[:, 0] * 360 > 40) & (hsv[:, 0] * 360 < 65) & (hsv[:, 1] > 0.45) & (hsv[:, 2] > 0.45)
        self.assertLess(float(yellow.mean()), 0.03)
        teal = (hsv[:, 0] * 360 > 160) & (hsv[:, 0] * 360 < 200) & (hsv[:, 1] > 0.3) & (hsv[:, 2] > 0.3)
        self.assertLess(float(teal.mean()), 0.005)


class TestRigRules(unittest.TestCase):
    """The rules on the shipped GLB (no Blender)."""

    @classmethod
    def setUpClass(cls):
        import rig_probe

        cls.rp = rig_probe
        cls.rig = rig_probe.Rig("moll")
        cls.names = cls.rig.joint_names

    def bones_of(self, part) -> set:
        return {self.names[j] for j, w in zip(part.J.ravel(), part.W.ravel()) if w > 1e-4}

    def dominant(self, part) -> np.ndarray:
        return np.array([self.names[part.J[i][int(np.argmax(part.W[i]))]] for i in range(len(part.P))])

    def test_props_are_rigid_on_their_bones(self):
        self.assertEqual(self.bones_of(self.rig.part("Iron")), {"DEF-iron"})
        self.assertEqual(self.bones_of(self.rig.part("Shield")), {"DEF-shield"})

    def test_the_iron_is_gripped(self):
        """M2-CHR-515: Moll holds the iron always (grips.json, written by hero_clips)."""
        grips = json.loads((ROOT / "game/data/characters/grips.json").read_text())["skeletons"]
        self.assertEqual(grips["moll_skeleton"]["bone"], "DEF-iron")
        self.assertEqual(grips["moll_skeleton"]["hand"], "DEF-hand.R")
        cfg = json.loads((ROOT / "tools/dev/rig_checks.json").read_text())["heroes"]["moll"]
        self.assertEqual(cfg["props"], ["Iron", "Shield"])
        self.assertEqual(cfg["garments"], ["Costume", "Sleeves"])

    def test_pauldrons_ride_their_hinges(self):
        bones = self.bones_of(self.rig.part("Costume"))
        for sd in ("L", "R"):
            self.assertIn(f"DEF-pauldron.{sd}", bones)

    def test_sandals_take_the_feet_weights(self):
        cost = self.rig.part("Costume")
        low = cost.P[:, 1] < 0.04  # glTF: +Y up; the soles and the straps
        dom = self.dominant(cost)[low]
        self.assertGreater(int(low.sum()), 200)
        self.assertTrue(all(d.startswith(("DEF-foot", "DEF-toe", "DEF-shin")) for d in dom), set(dom))

    def test_knees_are_kept_under_the_trousers(self):
        body = self.rig.part("Body")
        dom = self.dominant(body)
        knee = float(self.rig.skeleton.g_t["DEF-shin.L"][1])
        for side in ("L", "R"):
            near = (np.abs(body.P[:, 1] - knee) < 0.04) & np.array([d.startswith((f"DEF-shin.{side}",
                                                                                  f"DEF-thigh.{side}")) for d in dom])
            self.assertGreater(int(near.sum()), 30, side)


if __name__ == "__main__":
    unittest.main()
