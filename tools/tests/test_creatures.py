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

    def test_defaults_must_be_complete(self) -> None:
        cr = copy.deepcopy(self.creatures)
        del cr["defaults"]["ko"]
        self.assertTrue(any("defaults: missing ko" in x for x in self.errs(creatures=cr)))
        self.assertEqual(vc.creature_errors([], self.enemies, self.skills, lambda p: True),
                         [f"{vc.CREATURES_FILE}: must be an object"])

    def test_two_rows_cannot_share_a_scene(self) -> None:
        cr = copy.deepcopy(self.creatures)
        first = next(iter(cr["creatures"].values()))
        cr["creatures"]["twin"] = dict(first)
        self.assertTrue(any("is also" in x for x in self.errs(creatures=cr)))


class PipelineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = _load(vc.CREATURES_FILE)["creatures"]
        self.jobs = {j["id"]: j for j in _load("tools/dev/blender_builds.json")["jobs"]}

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


if __name__ == "__main__":
    unittest.main()
