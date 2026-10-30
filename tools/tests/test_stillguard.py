"""Tests for the Ch6 Stillguard soldiers (M3-CHR-508, assets_src/characters/stillguard/).

Run: python3 -m unittest tools.tests.test_stillguard

* The variant table: six variants, heights 1.70-1.84 m, the helm on three, no sash, Toma's spear's numbers; Moll's
  build stays Moll's (build_moll.MOLL, the sash on by default).
* The committed GLBs, per variant: budgets and sizes (LOD0 <= 45k, LOD1 <= 22k, GLB < 5 MiB), the mesh names the
  rig guards use (the Helm only where the table says), the Head's 40 shapes, the rig extras and their parents, the
  materials (the weathered ones on the shared worn atlases) and textures.
* The rules on the shipped mesh (rig_probe reads the GLB, no Blender): the spear and the shield rigid on their bones,
  the helm rigid on the head, the spear gripped (grips.json), the probe config, the clips.
* M3-CHR-540, Ivo Brannick (the named Stillguard): his table, GLB, materials, the chipped tooth, the clips his
  dialogue calls, the shield-only rig and the wiring.
"""
import json
import re
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets_src" / "characters" / "stillguard"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT / "tools" / "dev"))
sys.path.insert(0, str(ROOT / "assets_src" / "characters" / "asha"))

import sg_table  # noqa: E402

MAX_BYTES = 5 * 1024 * 1024  # ADR 0005 plain-blob cap
LOD0_MAX = 45_000  # M3-CHR-508
LOD1_MAX = 22_000
HEIGHTS = (1.70, 1.84)
HEIGHT_SPREAD = 0.12  # m: the six read as six men in a line
PAIRED = ["brow_inner_up", "brow_down", "brow_outer_up", "lid_close", "lid_wide", "lid_squint", "cheek_raise",
          "nose_sneer", "mouth_smile", "mouth_frown", "mouth_stretch", "mouth_dimple"]
SINGLE = ["mouth_press", "mouth_pucker", "lip_upper_up", "lip_lower_down", "jaw_open", "jaw_clench"]
VISEMES = ["vis_rest", "vis_aa", "vis_e", "vis_i", "vis_o", "vis_u", "vis_mbp", "vis_fv", "vis_l", "vis_st"]
API = [f"{b}_{s}" for b in PAIRED for s in ("L", "R")] + SINGLE
MESHES = ("Head", "Body", "Costume", "Sleeves", "Spear", "Shield")
EXTRA_BONES = {"DEF-pauldron.L": "DEF-shoulder.L", "DEF-pauldron.R": "DEF-shoulder.R", "DEF-spear": "DEF-hand.R",
               "DEF-shield": "DEF-forearm.L"}
PROPOSALS = ("stand_watch_seaward", "shield_up", "level_spear")  # act1_ch06's @anim proposals


def glb_json(path: Path) -> dict:
    data = path.read_bytes()
    magic, _version, _total = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "not a GLB"
    length, _kind = struct.unpack("<II", data[12:20])
    return json.loads(data[20:20 + length])


def tris(js: dict) -> int:
    return sum(js["accessors"][p["indices"]]["count"] // 3 for m in js["meshes"] for p in m["primitives"])


def out(v: str) -> Path:
    return ROOT / "assets" / "characters" / sg_table.name(v)


class TestTable(unittest.TestCase):
    def test_six_variants(self):
        vs = sg_table.variants()
        self.assertEqual(len(vs), 6)
        helms = [v for v in vs if sg_table.variant_params(v)["_variant"]["helm"]]
        self.assertEqual(len(helms), 3)
        heights = [sg_table.variant_params(v)["height_m"] for v in vs]
        self.assertTrue(all(HEIGHTS[0] <= h <= HEIGHTS[1] for h in heights), heights)
        self.assertGreaterEqual(max(heights) - min(heights), HEIGHT_SPREAD, heights)
        self.assertEqual(len({sg_table.variant_params(v)["skin_hex"] for v in vs}), 6)
        for v in vs:
            p = sg_table.variant_params(v)
            self.assertFalse(p["_costume"]["sash"])  # no Inquisitor's sash
            self.assertIn(p["_variant"]["hair"], ("crop", "shaved"))
            self.assertEqual((p["_costume"]["spear_length_m"], p["_costume"]["shield_diameter_m"]), (2.1, 0.62))

    def test_dialogue_actors_have_libraries(self):
        """ch06_barge.dlg's `@anim stillguard_a level_spear` and `stillguard_b`: the actor ids are the variants'. The
        other Ch6/Ch8 cues on these actors (walk_torch, kneel_palms_flat, ...) are outside M3-CHR-508's clip set."""
        import hero_clips

        for v in sg_table.variants():
            self.assertEqual(hero_clips.CLIPS[sg_table.name(v)][:2], ["idle", "walk"])
            for clip in PROPOSALS:
                self.assertIn(clip, hero_clips.CLIPS[sg_table.name(v)])
            self.assertTrue((out(v) / "anim" / f"{sg_table.name(v)}_clips.tres").exists())
        for line in (ROOT / "game/data/dialogue/ch06/ch06_barge.dlg").read_text(encoding="utf-8").splitlines():
            m = re.match(r"@anim (stillguard_\w+) (\w+)", line)
            if m and m.group(2) in PROPOSALS:
                self.assertIn(m.group(2), hero_clips.CLIPS[m.group(1)], line)


class TestCommitted(unittest.TestCase):
    def test_glbs(self):
        for v in sg_table.variants():
            n = sg_table.name(v)
            js = glb_json(out(v) / f"{n}.glb")
            self.assertLessEqual(tris(js), LOD0_MAX, n)
            self.assertLessEqual(tris(glb_json(out(v) / f"{n}_lod1.glb")), LOD1_MAX, n)
            self.assertLess((out(v) / f"{n}.glb").stat().st_size, MAX_BYTES, n)
            meshes = {m.get("name") for m in js["meshes"]}
            for mesh in MESHES:
                self.assertIn(mesh, meshes, n)
            self.assertEqual("Helm" in meshes, sg_table.variant_params(v)["_variant"]["helm"], n)
            hair = sg_table.variant_params(v)["_variant"]["hair"] == "crop" and "Helm" not in meshes
            self.assertEqual("HairHead" in meshes, hair, n)
            head = next(m for m in js["meshes"] if m.get("name") == "Head")
            self.assertEqual(head.get("extras", {}).get("targetNames", []), API + VISEMES, n)
            nodes = js["nodes"]
            parent = {c: i for i, nd in enumerate(nodes) for c in nd.get("children", [])}
            idx = {nd.get("name"): i for i, nd in enumerate(nodes)}
            for bone, par in EXTRA_BONES.items():
                self.assertEqual(nodes[parent[idx[bone]]]["name"], par, f"{n} {bone}")

    def test_materials_and_textures(self):
        from PIL import Image

        for v in sg_table.variants():
            n = sg_table.name(v)
            mats = {m["name"] for m in glb_json(out(v) / f"{n}.glb")["materials"]}
            have = {p.stem for p in (out(v) / "materials").glob("*.tres")}
            self.assertEqual(mats - have, set(), n)
            for tres in (out(v) / "materials").glob("*.tres"):
                for path in re.findall(r'path="res://([^"]+)"', tres.read_text(encoding="utf-8")):
                    self.assertTrue((ROOT / path).exists(), f"{n} {tres.name}: {path}")
            cloth = (out(v) / "materials" / "cloth.tres").read_text(encoding="utf-8")
            worn = sg_table.variant_params(v)["_variant"]["weathered"]
            self.assertEqual("stillguard_worn_cloth_albedo.png" in cloth, worn, n)
            self.assertNotIn("emission", (out(v) / "materials" / "spear.tres").read_text(encoding="utf-8"))
            for png in list((out(v) / "textures").glob("*.png")) + list(
                    (ROOT / "assets/characters/stillguard/textures").glob("*.png")):
                self.assertLess(png.stat().st_size, MAX_BYTES, png.name)
                with Image.open(png) as im:
                    w, h = im.size
                self.assertEqual(w & (w - 1), 0, png.name)
                self.assertEqual(h & (h - 1), 0, png.name)


class TestRigRules(unittest.TestCase):
    def test_props_rigid_and_gripped(self):
        import rig_probe

        grips = json.loads((ROOT / "game/data/characters/grips.json").read_text())["skeletons"]
        cfg = json.loads((ROOT / "tools/dev/rig_checks.json").read_text())["heroes"]
        for v in sg_table.variants():
            n = sg_table.name(v)
            rig = rig_probe.Rig(n)
            bones = lambda part: {rig.joint_names[j] for j, w in zip(part.J.ravel(), part.W.ravel())  # noqa: E731
                                  if w > 1e-4}
            self.assertEqual(bones(rig.part("Spear")), {"DEF-spear"}, n)
            self.assertEqual(bones(rig.part("Shield")), {"DEF-shield"}, n)
            helm = rig.part("Helm")
            if helm is not None:
                self.assertEqual(bones(helm), {"DEF-spine.006"}, n)
            self.assertEqual(grips[f"{n}_skeleton"]["bone"], "DEF-spear", n)
            self.assertEqual(cfg[n]["props"], ["Spear", "Shield"], n)
            self.assertNotIn("Spear", cfg[n].get("penetration", {}).get("limits_mm", {}), n)


# ---------------------------------------------------------------------------------------------
# M3-CHR-540: Ivo Brannick, a named Stillguard (stillguard_variants.json `named`), built and wired like a variant
# ---------------------------------------------------------------------------------------------
IVO = "ivo"
IVO_MESHES = ("Head", "Body", "Costume", "Sleeves", "Shield", "HairHead")
IVO_CLIPS = ["idle", "walk", "run", "talk", "hug_lift", "kneel_palms_flat"]
IVO_HEIGHT = (1.78, 1.84)  # m: a broad man, at the squad's tall end
CHIP_MM = (1.0, 4.0)  # the broken tooth: how far its chipped edge sits off its mirror twin
CHIP_VERTS = 30  # and on how few vertices (one tooth's edge)


def dialogue_calls(actor: str) -> set:
    calls = set()
    for dlg in (ROOT / "game/data/dialogue").rglob("*.dlg"):
        if "test" in dlg.parts:
            continue
        calls |= set(re.findall(rf"@anim {actor} ([a-z_]+)", dlg.read_text(encoding="utf-8")))
    return calls


class TestIvo(unittest.TestCase):
    def test_table(self):
        self.assertNotIn(IVO, sg_table.variants())  # the squad stays six
        self.assertEqual(sg_table.named(), [IVO, "officer", "venn"])  # M3-CHR-593: the Ch8 officer; M4-A2P-051
        self.assertEqual(sg_table.name(IVO), IVO)  # his own folder and the dialogue's speaker id
        p = sg_table.variant_params(IVO)
        var = p["_variant"]
        self.assertEqual((var["hair"], var["helm"], var["spear"]), ("crop", False, False))  # face and hair bare
        self.assertGreater(var["broken_tooth"], 0.0)
        self.assertTrue(IVO_HEIGHT[0] <= p["height_m"] <= IVO_HEIGHT[1], p["height_m"])
        squad = [sg_table.variant_params(v) for v in sg_table.variants()]
        self.assertNotIn(p["skin_hex"], {q["skin_hex"] for q in squad})
        self.assertGreaterEqual(p["muscle"], max(q["muscle"] for q in squad if q["shoulder_width_heads"] < 1.9))
        self.assertFalse(p["_costume"]["sash"])
        self.assertEqual(p["_costume"]["shield_diameter_m"], 0.62)

    def test_glb(self):
        js = glb_json(out(IVO) / f"{IVO}.glb")
        self.assertLessEqual(tris(js), LOD0_MAX)
        self.assertLessEqual(tris(glb_json(out(IVO) / f"{IVO}_lod1.glb")), LOD1_MAX)
        self.assertLess((out(IVO) / f"{IVO}.glb").stat().st_size, MAX_BYTES)
        meshes = {m.get("name") for m in js["meshes"]}
        for mesh in IVO_MESHES:
            self.assertIn(mesh, meshes)
        self.assertNotIn("Helm", meshes)
        self.assertNotIn("Spear", meshes)
        head = next(m for m in js["meshes"] if m.get("name") == "Head")
        self.assertEqual(head.get("extras", {}).get("targetNames", []), API + VISEMES)
        nodes = js["nodes"]
        parent = {c: i for i, nd in enumerate(nodes) for c in nd.get("children", [])}
        idx = {nd.get("name"): i for i, nd in enumerate(nodes)}
        self.assertNotIn("DEF-spear", idx)
        for bone, par in EXTRA_BONES.items():
            if bone != "DEF-spear":
                self.assertEqual(nodes[parent[idx[bone]]]["name"], par, bone)

    def test_materials_and_textures(self):
        from PIL import Image

        mats = {m["name"] for m in glb_json(out(IVO) / f"{IVO}.glb")["materials"]}
        have = {p.stem for p in (out(IVO) / "materials").glob("*.tres")}
        self.assertEqual(mats - have, set())
        self.assertFalse({"spear", "steel"} & have)
        for tres in (out(IVO) / "materials").glob("*.tres"):
            for path in re.findall(r'path="res://([^"]+)"', tres.read_text(encoding="utf-8")):
                self.assertTrue((ROOT / path).exists(), f"{tres.name}: {path}")
        self.assertIn("stillguard_worn_cloth_albedo.png", (out(IVO) / "materials/cloth.tres").read_text(encoding="utf-8"))
        for png in (out(IVO) / "textures").glob("*.png"):
            self.assertLess(png.stat().st_size, MAX_BYTES, png.name)
            with Image.open(png) as im:
                w, h = im.size
            self.assertEqual((w & (w - 1), h & (h - 1)), (0, 0), png.name)

    def test_broken_tooth(self):
        """One upper front tooth chipped: the teeth are mirror-symmetric but for a few millimetres on one edge."""
        import numpy as np
        import rig_probe

        teeth = np.vstack([p.P for p in rig_probe.Rig(IVO).prims["Head"] if p.material == "teeth"])
        left, right = teeth[teeth[:, 0] > 1e-4], teeth[teeth[:, 0] < -1e-4] * np.array([-1.0, 1.0, 1.0])
        off = np.sqrt(((left[:, None, :] - right[None, :, :]) ** 2).sum(-1)).min(axis=1) * 1000.0
        self.assertTrue(CHIP_MM[0] <= off.max() <= CHIP_MM[1], off.max())
        self.assertLess(int((off > 0.5).sum()), CHIP_VERTS)

    def test_clips_cover_his_dialogue(self):
        """Every `@anim ivo <clip>` has a clip (look_at is the sequencer's own turn); his library has them all."""
        import hero_clips

        self.assertEqual(hero_clips.CLIPS[IVO], IVO_CLIPS)
        called = dialogue_calls(IVO)
        self.assertTrue(called)
        self.assertEqual(called - set(IVO_CLIPS) - {"look_at"}, set())
        text = hero_clips.out_path(IVO).read_text(encoding="utf-8")
        self.assertEqual(set(re.findall(r'resource_name = &"([a-z_0-9]+)"', text)), set(IVO_CLIPS))

    def test_rig_rules(self):
        import rig_probe

        rig = rig_probe.Rig(IVO)
        part = rig.part("Shield")
        self.assertEqual({rig.joint_names[j] for j, w in zip(part.J.ravel(), part.W.ravel()) if w > 1e-4},
                         {"DEF-shield"})
        cfg = json.loads((ROOT / "tools/dev/rig_checks.json").read_text())["heroes"][IVO]
        self.assertEqual(cfg["props"], ["Shield"])
        grips = json.loads((ROOT / "game/data/characters/grips.json").read_text())["skeletons"]
        self.assertNotIn(f"{IVO}_skeleton", grips)  # no held prop

    def test_wiring(self):
        rules = json.loads((ROOT / "game/data/import/characters.json").read_text(encoding="utf-8"))
        self.assertIn(f"res://assets/characters/{IVO}/", rules["assets"])
        jobs = {j["id"]: j for j in json.loads((ROOT / "tools/dev/blender_builds.json").read_text())["jobs"]}
        self.assertIn(f"assets/characters/{IVO}/*.glb", jobs[IVO]["outputs"])
        speakers = json.loads((ROOT / "game/data/dialogue/speakers.json").read_text(encoding="utf-8"))
        self.assertIn(IVO, {s["id"] for s in speakers["speakers"]})


VENN = "venn"


class TestVenn(unittest.TestCase):
    """M4-A2P-051: Warden Malcor Venn, a named build on the squad's kit: the halberd on the spear's bone, no shield,
    Moll's sash, his own dyes, Moll's battle contract."""

    def test_table(self):
        p = sg_table.variant_params(VENN)
        var = p["_variant"]
        self.assertTrue(var["halberd"])
        self.assertFalse(var["shield"])
        self.assertTrue(p["_costume"]["sash"])  # his own `_costume` over the squad's (sash false)
        self.assertFalse(sg_table.variant_params("a")["_costume"]["sash"])  # the squad unchanged
        self.assertEqual(var["palette"]["linen"], "#B3261E")  # the red sash (lacquer_red)

    def test_committed(self):
        import rig_probe

        rig = rig_probe.Rig(VENN)
        self.assertIsNone(rig.part("Shield"))
        part = rig.part("Spear")
        self.assertEqual({rig.joint_names[j] for j, w in zip(part.J.ravel(), part.W.ravel()) if w > 1e-4},
                         {"DEF-spear"})
        cfg = json.loads((ROOT / "tools/dev/rig_checks.json").read_text())["heroes"][VENN]
        self.assertEqual(cfg["props"], ["Spear"])
        grips = json.loads((ROOT / "game/data/characters/grips.json").read_text())["skeletons"]
        self.assertIn(f"{VENN}_skeleton", grips)
        mats = {f.name for f in (ROOT / "assets/characters" / VENN / "materials").glob("*.tres")}
        self.assertNotIn("shield.tres", mats)
        self.assertIn("spear.tres", mats)
        cloth = (ROOT / "assets/characters" / VENN / "materials/cloth.tres").read_text(encoding="utf-8")
        self.assertIn(f"{VENN}/textures/{VENN}_cloth_albedo.png", cloth)

    def test_wiring(self):
        rules = json.loads((ROOT / "game/data/import/characters.json").read_text(encoding="utf-8"))
        self.assertIn(f"res://assets/characters/{VENN}/", rules["assets"])
        jobs = {j["id"]: j for j in json.loads((ROOT / "tools/dev/blender_builds.json").read_text())["jobs"]}
        self.assertIn(f"assets/characters/{VENN}/*.glb", jobs[VENN]["outputs"])
        self.assertTrue((ROOT / "game/characters/foes/venn_battle.tscn").exists())


class TestMollUnchanged(unittest.TestCase):
    def test_moll_spec(self):
        sys.path.insert(0, str(ROOT / "assets_src" / "characters" / "moll"))
        src = (ROOT / "assets_src/characters/moll/build_moll.py").read_text(encoding="utf-8")
        self.assertIn('MOLL = {"name": "moll", "params": PARAMS, "subdiv_face": True, "hair": True, "prop": None, '
                      '"helm": None}', src)
        costume = (ROOT / "assets_src/characters/moll/moll_costume.py").read_text(encoding="utf-8")
        self.assertIn('params.get("sash", True)', costume)


if __name__ == "__main__":
    unittest.main()
