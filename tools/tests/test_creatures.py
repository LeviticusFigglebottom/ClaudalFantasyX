"""Battle creatures (M2-CRE-02/03). Run: python3 -m unittest discover -s tools/tests

* tools/validate_creatures.py: creatures.json rows and enemies.json `model` (good data passes, each kind of
  mistake is caught).
* assets_src/creatures/common/write_materials.py rewrites the committed material resources byte for byte.
* Every creature in creatures.json has a Blender job whose outputs are its GLB and materials, a PROVENANCE row per
  committed file, and a .glb.import that runs the creatures post-import script.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_creatures as vc  # noqa: E402


def _load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _writer():
    spec = importlib.util.spec_from_file_location("write_materials", ROOT / "assets_src/creatures/common/write_materials.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.creatures = _load(vc.CREATURES_FILE)
        self.enemies = _load(vc.ENEMIES_FILE)
        self.skills = _load(vc.SKILLS_FILE)

    def errs(self, creatures=None, enemies=None, exists=lambda p: True) -> list[str]:
        return vc.creature_errors(creatures or self.creatures, enemies or self.enemies, self.skills, exists)

    def test_committed_data_passes(self) -> None:
        real = vc.creature_errors(self.creatures, self.enemies, self.skills,
                                  lambda res: (ROOT / res.removeprefix("res://")).is_file())
        self.assertEqual(real, [])

    def test_a_model_needs_an_existing_scene_with_a_row(self) -> None:
        en = copy.deepcopy(self.enemies)
        en["enemies"][0]["model"] = "res://game/creatures/nobody/nobody_battle.tscn"
        e = self.errs(enemies=en)
        self.assertTrue(any("no game/data/creatures/creatures.json row" in x for x in e), e)
        self.assertTrue(any("does not exist" in x for x in self.errs(enemies=en, exists=lambda p: False)))
        en["enemies"][0]["model"] = "res://elsewhere/x.tscn"
        self.assertTrue(any("must be a res://game/creatures/" in x for x in self.errs(enemies=en)))

    def test_rows_are_checked(self) -> None:
        cr = copy.deepcopy(self.creatures)
        row = cr["creatures"]["drownbell"]  # an enemy uses it, so its phase names are checked too
        row["clip_by_skill"] = {"no_such_skill": "cast"}
        row["stand_in"] = {"tilt": 3}
        row["phases"] = {"no_such_phase": {"clip": "x", "offset_m": [0, 1]}}
        row["break_parts"] = {"toll": {"whole": []}}
        row["oops"] = 1
        e = self.errs(creatures=cr)
        for needle in ("unknown skill 'no_such_skill'", "stand_in: unknown key 'tilt'", "no enemy has a phase",
                       "offset_m: must be [x, y, z]", "break_parts.toll", "unknown key 'oops'"):
            self.assertTrue(any(needle in x for x in e), (needle, e))

    def test_a_creature_no_enemy_uses_yet_may_name_its_own_phases(self) -> None:
        cr = copy.deepcopy(self.creatures)
        cr["creatures"]["cinder_matron"]["phases"] = {"pour": {"clip": "phase_change", "hide": ["Crust"]}}
        self.assertFalse(any("no enemy has a phase" in x for x in self.errs(creatures=cr)))
        cr["creatures"]["cinder_matron"]["phases"]["pour"]["hide"] = "Crust"
        self.assertTrue(any("hide: must be a list" in x for x in self.errs(creatures=cr)))
        cr["creatures"]["cinder_matron"]["phases"]["pour"]["hide"] = ["Crust"]
        cr["creatures"]["cinder_matron"]["phases"]["pour"]["clips"] = {"attack": ""}
        self.assertTrue(any("clips: must map clip names" in x for x in self.errs(creatures=cr)))

    def test_defaults_must_be_complete(self) -> None:
        cr = copy.deepcopy(self.creatures)
        del cr["defaults"]["ko"]
        self.assertTrue(any("defaults: missing ko" in x for x in self.errs(creatures=cr)))
        self.assertEqual(vc.creature_errors([], self.enemies, self.skills, lambda p: True),
                         [f"{vc.CREATURES_FILE}: must be an object"])

    def test_a_vowbound_row_names_a_vowbound_and_no_enemy_model(self) -> None:
        """M3-CRE-638: `vowbound` true makes a row a Vowbound's actor (CreatureModels finds it by id)."""
        vb = _load(vc.VOWBOUND_FILE)

        def errs(cr, en=None) -> list[str]:
            return vc.creature_errors(cr, en or self.enemies, self.skills, lambda p: True, vb)

        self.assertTrue(self.creatures["creatures"]["ilun"]["vowbound"], "Ilun is a Vowbound's actor")
        self.assertEqual(errs(self.creatures), [])
        cr = copy.deepcopy(self.creatures)
        cr["creatures"]["ilun"]["vowbound"] = "yes"
        self.assertTrue(any("ilun.vowbound: must be true or false" in x for x in errs(cr)))
        cr["creatures"]["nobody"] = dict(cr["creatures"].pop("ilun"), vowbound=True)
        self.assertTrue(any("no game/data/battle/vowbound.json row 'nobody'" in x for x in errs(cr)))
        en = copy.deepcopy(self.enemies)
        en["enemies"][0]["model"] = self.creatures["creatures"]["ilun"]["scene"]
        self.assertTrue(any("a Vowbound's scene may not be an enemy's model" in x for x in errs(self.creatures, en)))
        cr = copy.deepcopy(self.creatures)
        cr["creatures"]["ilun"]["vowbound"] = False
        self.assertEqual(errs(cr), [], "false is a plain creature row")

    def test_a_vowbound_may_wait_for_its_game_row(self) -> None:
        """M3-CRE-642: Nhoa is built ahead of her vowbound.json row (Combat's); `vowbound_pending` names the task and
        lets the row be missing, and becomes an error once the row exists."""
        vb = _load(vc.VOWBOUND_FILE)

        def errs(cr, table=vb) -> list[str]:
            return vc.creature_errors(cr, self.enemies, self.skills, lambda p: True, table)

        nhoa = self.creatures["creatures"]["nhoa"]
        self.assertTrue(nhoa["vowbound"])
        self.assertEqual(errs(self.creatures), [])
        cr = copy.deepcopy(self.creatures)
        del cr["creatures"]["nhoa"]["vowbound_pending"]
        self.assertTrue(any("no game/data/battle/vowbound.json row 'nhoa'" in x for x in errs(cr)))
        cr = copy.deepcopy(self.creatures)
        cr["creatures"]["ilun"]["vowbound_pending"] = "M0-X-01"
        self.assertTrue(any("ilun.vowbound_pending: game/data/battle/vowbound.json has the row 'ilun' now" in x
                            for x in errs(cr)))
        cr = copy.deepcopy(self.creatures)
        cr["creatures"]["nhoa"]["vowbound_pending"] = " "
        self.assertTrue(any("nhoa.vowbound_pending: must name the task" in x for x in errs(cr)))
        cr = copy.deepcopy(self.creatures)
        cr["creatures"]["nhoa"]["vowbound"] = False
        self.assertTrue(any("nhoa.vowbound_pending: only on a row with vowbound true" in x for x in errs(cr)))
        cr = copy.deepcopy(self.creatures)
        del cr["creatures"]["nhoa"]["vowbound"]
        self.assertTrue(any("nhoa.vowbound_pending: only on a row with vowbound true" in x for x in errs(cr)))

    def test_a_stand_in_may_give_its_height_and_radius(self) -> None:
        """M3-CRE-640: Kahre has no battle_sandbox.json row, so his creatures.json stand_in gives the height the VFX
        anchors are fractions of, and the ring's radius."""
        st = self.creatures["creatures"]["kahre"]["stand_in"]
        self.assertGreater(st["height"], 3.0)
        self.assertGreater(st["radius"], 0.3)
        cr = copy.deepcopy(self.creatures)
        cr["creatures"]["kahre"]["stand_in"]["height"] = 0
        cr["creatures"]["kahre"]["stand_in"]["radius"] = "wide"
        got = vc.creature_errors(cr, self.enemies, self.skills, lambda p: True)
        self.assertTrue(any("kahre.stand_in.height: must be a number > 0" in x for x in got), got)
        self.assertTrue(any("kahre.stand_in.radius: must be a number > 0" in x for x in got), got)

    def test_a_vowbound_row_may_wait_on_its_combat_row(self) -> None:
        """M3-CRE-644: Ethren's model is built before Combat writes his vowbound.json row; `vowbound_pending` (the task
        that waits on it) excuses the missing row, and is an error once the row exists."""
        vb = _load(vc.VOWBOUND_FILE)

        def errs(cr) -> list[str]:
            return vc.creature_errors(cr, self.enemies, self.skills, lambda p: True, vb)

        self.assertEqual(errs(self.creatures), [])
        cr = copy.deepcopy(self.creatures)
        cr["creatures"]["ethren"].pop("vowbound_pending", None)
        if "ethren" not in {r.get("id") for r in vb["vowbound"]}:
            self.assertTrue(any("no game/data/battle/vowbound.json row 'ethren'" in x for x in errs(cr)))
        cr = copy.deepcopy(self.creatures)
        cr["creatures"]["ilun"]["vowbound_pending"] = "M3-CRE-638"
        self.assertTrue(any("ilun.vowbound_pending" in x for x in errs(cr)))

    def test_two_rows_cannot_share_a_scene(self) -> None:
        cr = copy.deepcopy(self.creatures)
        first = next(iter(cr["creatures"].values()))
        cr["creatures"]["twin"] = dict(first)
        self.assertTrue(any("is also" in x for x in self.errs(creatures=cr)))

    def test_a_held_vowbound_row_is_a_foe_row_with_a_held_release(self) -> None:
        """M3-CRE-647: `<id>_held` is a Vowbound as a foe (no `vowbound` key); its `release` phase holds its clip."""
        vb = _load(vc.VOWBOUND_FILE)
        rows = self.creatures["creatures"]
        for vid in ("ilun", "kahre", "virel", "hesk", "nhoa", "ethren"):
            row = rows[f"{vid}_held"]
            self.assertNotIn("vowbound", row)
            self.assertEqual(row["ko"], "release")
            self.assertEqual(row["phases"]["release"], {"clip": "release", "hold": True})
            self.assertGreater(row["stand_in"]["yaw_deg"], 0.0, "a foe faces the party (the ally's is -90)")
            self.assertEqual(row["scene"], f"res://game/creatures/{vid}/{vid}_held_battle.tscn")
        self.assertEqual(vc.creature_errors(self.creatures, self.enemies, self.skills, lambda p: True, vb), [])
        cr = copy.deepcopy(self.creatures)
        cr["creatures"]["ilun_held"]["phases"]["release"]["hold"] = "yes"
        self.assertTrue(any("release.hold: must be true or false" in x for x in self.errs(creatures=cr)))
        del cr["creatures"]["ilun_held"]["phases"]["release"]["clip"]
        cr["creatures"]["ilun_held"]["phases"]["release"]["hold"] = True
        self.assertTrue(any("release.hold: holds the phase's clip" in x for x in self.errs(creatures=cr)))


## The regular enemies a player fights in Act I (ADR 0041; encounters.json Ch1-Ch8 and the slice; the bosses are
## creatures-b's). wickfry fights as the glassfry model.
ACT1_REGULARS = ("ashwing", "flue_moth", "gull_harrier", "lantern_eel", "oil_slug", "raid_hound", "reef_crab",
                 "sail_leech", "scuttler", "shoal_skipper", "slag_tortoise", "squall_wing", "stormgull", "tide_crawler",
                 "tower_limpet", "vein_sparker", "wall_polyp", "wallcrab", "glassfry", "wreck_crab")


def model_rows(rows: dict) -> dict:
    """The rows that own a model: a row whose scene lives in game/creatures/<its id>/. A second row on the same model
    (a Vowbound's `<id>_held` foe form, M3-CRE-647) shares that row's GLB, job and materials."""
    return {cid: row for cid, row in rows.items() if row["scene"].split("/")[-2] == cid}


class VfxAnchorShapeTest(unittest.TestCase):
    def test_anchor_keys_and_a_core(self) -> None:
        errs = vc._row_errors("w", {"vfx_anchors": {"wound": "body", "tail": "x"}}, set(), None)
        self.assertTrue(any("unknown anchor 'tail'" in e for e in errs), errs)
        self.assertTrue(any("needs a core" in e for e in errs), errs)
        self.assertTrue(any("must map" in e for e in vc._row_errors("w", {"vfx_anchors": {"core": 3}}, set(), None)))
        self.assertEqual(vc._row_errors("w", {"vfx_anchors": {"core": "body"}}, set(), None), [])


class PipelineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.all_rows = _load(vc.CREATURES_FILE)["creatures"]
        self.rows = model_rows(self.all_rows)
        self.jobs = {j["id"]: j for j in _load("tools/dev/blender_builds.json")["jobs"]}

    def test_every_other_row_shares_a_model_row(self) -> None:
        for cid, row in self.all_rows.items():
            if cid not in self.rows:
                self.assertIn(row["scene"].split("/")[-2], self.rows, cid)

    def test_a_held_block_writes_glimmer_held_and_nothing_else_changes(self) -> None:
        """M3-CRE-647: the held set swaps each emissive slot's glimmer_bound for glimmer_held (same energy); the other
        slots and the plain set are byte-identical to a spec without the block."""
        w = _writer()
        spec = {"slots": {"lit": {"emission_color": "#4FB3B0", "emission_energy": 1.2, "roughness_dry": 0.3},
                          "dull": {"emission_energy": 0.0, "roughness_dry": 0.8}}}
        held = {"emission_from": "#4FB3B0", "emission_to": "#7FC6D9"}
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            for tmp, s in ((Path(a), spec), (Path(b), dict(spec, held=held))):
                (tmp / "assets_src/creatures/x").mkdir(parents=True)
                (tmp / "assets_src/creatures/x/materials.json").write_text(json.dumps(s))
                w.write("x", tmp)
            plain, with_held = Path(a) / "assets/creatures/x", Path(b) / "assets/creatures/x"
            self.assertFalse((plain / "materials_held").exists())
            for slot in ("lit", "dull"):
                self.assertEqual((plain / "materials" / f"{slot}.tres").read_bytes(),
                                 (with_held / "materials" / f"{slot}.tres").read_bytes())
            self.assertEqual((plain / "materials/dull.tres").read_bytes(),
                             (with_held / "materials_held/dull.tres").read_bytes())
            lit = (with_held / "materials_held/lit.tres").read_text()
            self.assertIn("emission_color = Color(0.498039, 0.776471, 0.85098, 1)", lit)
            self.assertIn("emission_energy = 1.2", lit)
        bad = dict(spec["slots"], odd={"emission_color": "#FFFFFF", "emission_energy": 1.0})
        with self.assertRaises(ValueError):
            w.held_slots(bad, held)
        with self.assertRaises(ValueError):
            w.held_slots({"p": {"emission_color": "#4FB3B0", "emission_energy": 1.0, "emission_pulse_hz": 0.5}}, held)

    def test_each_vowbound_has_a_held_set_and_a_release_clip(self) -> None:
        sys.path.insert(0, str(ROOT / "tools" / "tests"))
        from test_post_import import read_glb  # noqa: PLC0415

        for cid in ("ilun", "kahre", "virel", "hesk", "nhoa", "ethren"):
            self.assertIn(f"assets/creatures/{cid}/materials_held/*.tres", self.jobs[f"creature_{cid}"]["outputs"])
            js = read_glb(ROOT / "assets/creatures" / cid / f"{cid}.glb")
            self.assertIn("release", {a["name"] for a in js["animations"]}, cid)
            for m in {m["name"] for m in js["materials"]}:
                self.assertTrue((ROOT / "assets/creatures" / cid / "materials_held" / f"{m}.tres").is_file(), (cid, m))

    def test_vfx_anchors_name_bones_in_the_model(self) -> None:
        """M3-CRE-651: each `vfx_anchors` bone is a joint of the creature's GLB (the one its battle scene instances),
        and every Act I regular (ADR 0041) has a core."""
        import re  # noqa: PLC0415

        sys.path.insert(0, str(ROOT / "tools" / "tests"))
        from test_post_import import read_glb  # noqa: PLC0415

        for cid, row in self.all_rows.items():
            anchors = row.get("vfx_anchors")
            if not anchors:
                continue
            scene = (ROOT / row["scene"].replace("res://", "")).read_text(encoding="utf-8")
            glb = re.search(r'path="res://(assets/creatures/[^"]+\.glb)"', scene)
            self.assertIsNotNone(glb, cid)
            js = read_glb(ROOT / glb.group(1))
            joints = {js["nodes"][i]["name"] for skin in js.get("skins", []) for i in skin["joints"]}
            for name, bone in anchors.items():
                self.assertIn(bone, joints, f"{cid}.vfx_anchors.{name}")
        for cid in ACT1_REGULARS:
            self.assertIn("core", self.all_rows[cid].get("vfx_anchors", {}), cid)

    def test_materials_rebuild_byte_for_byte(self) -> None:
        w = _writer()
        for cid in self.rows:
            with tempfile.TemporaryDirectory() as tmp:
                t = Path(tmp)
                (t / "assets_src/creatures" / cid).mkdir(parents=True)
                (t / "assets_src/creatures" / cid / "materials.json").write_bytes(
                    (ROOT / "assets_src/creatures" / cid / "materials.json").read_bytes())
                for p in w.write(cid, t):
                    committed = ROOT / p.relative_to(t)
                    self.assertEqual(p.read_bytes(), committed.read_bytes(), f"{committed} is stale")

    def test_every_creature_has_its_job_provenance_and_import(self) -> None:
        prov = (ROOT / "assets/PROVENANCE.md").read_text(encoding="utf-8")
        for cid in self.rows:
            job = self.jobs.get(f"creature_{cid}")
            self.assertIsNotNone(job, f"tools/dev/blender_builds.json has no creature_{cid} job")
            self.assertIn(f"assets/creatures/{cid}/*.glb", job["outputs"])
            self.assertIn(f"assets/creatures/{cid}/materials/*.tres", job["outputs"])
            self.assertIn("assets_src/creatures/common/**", job["sources"])
            files = sorted((ROOT / "assets/creatures" / cid).rglob("*"))
            for f in files:
                if f.is_file() and f.suffix != ".import":
                    self.assertIn(f"| {f.relative_to(ROOT).as_posix()} |", prov)
            for glb in (ROOT / "assets/creatures" / cid).glob("*.glb"):
                imp = (glb.parent / (glb.name + ".import")).read_text(encoding="utf-8")
                self.assertIn('import_script/path="res://game/core/import/creatures_post_import.gd"', imp)

    def test_glb_has_the_clip_set_and_vertex_channels(self) -> None:
        sys.path.insert(0, str(ROOT / "tools" / "tests"))
        from test_post_import import read_glb  # noqa: PLC0415

        for cid, row in self.rows.items():
            js = read_glb(ROOT / "assets/creatures" / cid / f"{cid}.glb")
            clips = {a["name"] for a in js.get("animations", [])}
            self.assertTrue({"idle", "hit", "ko", "attack", "cast"} <= clips, (cid, clips))
            for p in (pr for m in js["meshes"] for pr in m["primitives"]):
                self.assertTrue({"COLOR_0", "TEXCOORD_0", "TEXCOORD_1", "JOINTS_0", "WEIGHTS_0"} <= set(p["attributes"]))
            mats = {m["name"] for m in js["materials"]}
            for m in mats:
                self.assertTrue((ROOT / "assets/creatures" / cid / "materials" / f"{m}.tres").is_file(), (cid, m))

    def test_a_ko_ends_on_the_ground(self) -> None:
        """BPR-11 plays a foe's KO once and fades it where it lies, so the KO must end on the floor: a flier's KO drops
        its root by its stand-in `hover` (and only a flier's drops far)."""
        import struct  # noqa: PLC0415

        import numpy as np  # noqa: PLC0415

        sinks_by_design = {"hullgnaw": "it slides back down between the planks (hullgnaw.md)"}
        defaults = _load(vc.CREATURES_FILE)["defaults"]
        for cid, row in self.rows.items():
            raw = (ROOT / "assets/creatures" / cid / f"{cid}.glb").read_bytes()
            jl = struct.unpack_from("<I", raw, 12)[0]
            js, bin_ = json.loads(raw[20:20 + jl]), raw[20 + jl + 8:]
            root = next(i for i, n in enumerate(js["nodes"]) if n.get("name") == "root")
            rest_y = js["nodes"][root].get("translation", [0.0, 0.0, 0.0])[1]
            ko = next(a for a in js["animations"] if a["name"] == "ko")
            dy = 0.0
            for ch in ko["channels"]:
                if ch["target"].get("node") == root and ch["target"]["path"] == "translation":
                    acc = js["accessors"][ko["samplers"][ch["sampler"]]["output"]]
                    bv = js["bufferViews"][acc["bufferView"]]
                    off = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
                    v = np.frombuffer(bin_, dtype=np.float32, count=acc["count"] * 3, offset=off).reshape(-1, 3)
                    dy = float(v[-1, 1]) - rest_y
            hover = float({**defaults["stand_in"], **row.get("stand_in", {})}.get("hover", 0.0))
            if cid in sinks_by_design:
                continue
            if hover > 0.0:
                self.assertAlmostEqual(-dy, hover, delta=0.05, msg=f"{cid}: a flier's KO lands on the floor")
            else:
                self.assertGreater(dy, -0.5, f"{cid}: a grounded creature's KO doesn't sink through the floor")


def skinned_lowest(glb: Path) -> dict[str, float]:
    """The lowest vertex y (metres) over every baked frame of each clip of a creature GLB, skinned as Godot plays it:
    each clip's channels are sampled at every frame (the kit force-samples them), nodes not keyed keep their rest TRS,
    and a vertex is the weighted sum of its joints' global matrices times their inverse bind matrices."""
    import struct  # noqa: PLC0415

    import numpy as np  # noqa: PLC0415

    raw = glb.read_bytes()
    jl = struct.unpack_from("<I", raw, 12)[0]
    js, bin_ = json.loads(raw[20:20 + jl]), raw[20 + jl + 8:]
    width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
    kinds = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}

    def acc(i: int) -> np.ndarray:
        a = js["accessors"][i]
        bv = js["bufferViews"][a["bufferView"]]
        n = width[a["type"]]
        off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        out = np.frombuffer(bin_, dtype=kinds[a["componentType"]], count=a["count"] * n, offset=off).reshape(-1, n)
        if a.get("normalized"):
            return out.astype(np.float64) / np.iinfo(out.dtype).max
        return out.astype(np.float64) if out.dtype == np.float32 else out.astype(np.int64)

    def trs(t, r, s) -> np.ndarray:
        x, y, z, w = r
        M = np.eye(4)
        M[:3, :3] = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                              [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                              [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]) * np.asarray(s)
        M[:3, 3] = t
        return M

    nodes = js["nodes"]
    parent = {c: i for i, n in enumerate(nodes) for c in n.get("children", [])}
    order = []  # parents before children
    seen: set[int] = set()

    def visit(i: int) -> None:
        if i not in seen:
            if i in parent:
                visit(parent[i])
            seen.add(i)
            order.append(i)

    for i in range(len(nodes)):
        visit(i)
    rest = [[np.array(n.get("translation", [0.0, 0.0, 0.0])), np.array(n.get("rotation", [0.0, 0.0, 0.0, 1.0])),
             np.array(n.get("scale", [1.0, 1.0, 1.0]))] for n in nodes]
    skin = js["skins"][0]
    joints = skin["joints"]
    ibm = acc(skin["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1)
    prims = [p for m in js["meshes"] for p in m["primitives"]]
    P = np.vstack([acc(p["attributes"]["POSITION"]) for p in prims])
    P = np.c_[P, np.ones(len(P))]
    J = np.vstack([acc(p["attributes"]["JOINTS_0"]) for p in prims])
    W = np.vstack([acc(p["attributes"]["WEIGHTS_0"]) for p in prims])
    slot = {"translation": 0, "rotation": 1, "scale": 2}
    out = {}
    for anim in js["animations"]:
        chans = [(c["target"]["node"], slot[c["target"]["path"]], acc(anim["samplers"][c["sampler"]]["output"]))
                 for c in anim["channels"] if c["target"]["path"] in slot]
        frames = max(len(v) for _, _, v in chans)
        low = np.inf
        for f in range(frames):
            local = [list(r) for r in rest]
            for node, k, v in chans:
                local[node][k] = v[min(f, len(v) - 1)]
            G: dict[int, np.ndarray] = {}
            for i in order:
                G[i] = trs(*local[i]) if i not in parent else G[parent[i]] @ trs(*local[i])
            S = np.array([G[j] for j in joints]) @ ibm
            y = sum(W[:, k] * np.einsum("nj,nj->n", S[J[:, k], 1, :], P) for k in range(J.shape[1]))
            low = min(low, float(y.min()))
        out[anim["name"]] = low
    return out


class GroundedClipsTest(unittest.TestCase):
    """M3-CRE-631, M3-CRE-632: every vertex of every baked frame of every clip of every creature in creatures.json
    stays at or above the floor (y 0, 5 mm tolerance), measured from the GLB, not the root bone. A flier is measured
    with its creatures.json `stand_in.hover` added, since the stand-in lifts the model by it in battle (its KO comes
    down by that hover and lands on the floor, test_a_ko_ends_on_the_ground). It skins all of them in about 11 s.

    Only a creature whose design puts it below the floor may be left out (ALLOW, each citing its sheet). A phase's
    creatures.json `offset_m` (the Drownbell sinking into the flood) is the stage's, not the clip's, and isn't added."""

    TOLERANCE = 0.005
    ALLOW = {
        # it rises out of the water between the raft's planks, and its KO slides back down between them
        # (docs/kb/art/creatures/act1/hullgnaw.md)
        "hullgnaw": "rises from the water between the planks",
        # it rises out of the water or sand; as built, its tail is buried and runs along under the ground before the S
        # rises (docs/kb/art/creatures/lantern_eel.md, "Notes for the model")
        "lantern_eel": "its tail is buried",
        # a limb of the storm coming down over the seawall from behind the parapet; its far body is the storm VFX
        # (docs/kb/art/creatures/act1/undertows_reach.md)
        "undertows_reach": "rises from the storm behind the wall",
        # a fish fought from a barge: mostly a fin above the water, it breaches to strike and dives (cast)
        # (docs/kb/art/creatures/act2/wakefin.md)
        "wakefin": "swims below the waterline",
        # it lies half out of the fen's water on a mangrove root, whose ends dip under (y 0 is the water); its KO rolls
        # off the root and sinks (docs/kb/art/creatures/act2/tannin_archer.md; the build's docstring)
        "tannin_archer": "half out of the water on a root",
    }

    def test_clips_stay_above_the_floor(self) -> None:
        data = _load(vc.CREATURES_FILE)
        for cid, row in model_rows(data["creatures"]).items():  # a held row shares its model row's GLB and stand-in
            if cid in self.ALLOW:
                continue
            hover = float({**data["defaults"]["stand_in"], **row.get("stand_in", {})}.get("hover", 0.0))
            for clip, low in skinned_lowest(ROOT / "assets/creatures" / cid / f"{cid}.glb").items():
                with self.subTest(creature=cid, clip=clip):
                    self.assertGreaterEqual(low + hover, -self.TOLERANCE,
                                            f"{cid} {clip}: a vertex goes {-(low + hover):.3f} m under the floor"
                                            + (f" (with its {hover} m hover)" if hover else ""))

    def test_the_allow_list_names_creatures(self) -> None:
        rows = _load(vc.CREATURES_FILE)["creatures"]
        self.assertEqual(sorted(set(self.ALLOW) - set(rows)), [], "an ALLOW entry names no creature")


if __name__ == "__main__":
    unittest.main()
