"""Ambient wildlife (M3-CRE-611; the insects M3-CRE-616). Run: python3 -m unittest discover -s tools/tests

* tools/validate_wildlife.py: the committed kinds, zone files and review stage pass; each kind of mistake is caught.
* assets_src/wildlife/common/write_materials.py rewrites the committed material resources byte for byte.
* Every wildlife asset has a Blender job whose outputs are its GLB and materials, a PROVENANCE row per committed
  file, and a .glb.import that runs the wildlife post-import script.
* The GLBs are unskinned meshes with the vertex channels the wildlife shader reads, within the triangle budget, and
  every glTF material slot has its .tres; the kinds file names meshes that exist in them.
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
sys.path.insert(0, str(ROOT / "tools" / "tests"))
import validate_wildlife as vw  # noqa: E402
from test_post_import import read_glb  # noqa: E402

ANIMALS = ("gull", "shore_crab", "shoal_fish", "insect", "kingfisher", "rim_ray")
# Per mesh: small enough to draw dozens through MultiMesh (docs/kb/art/wildlife.md, Budgets).
MAX_TRIANGLES = 1500
# An insect is a few pixels on screen (M3-CRE-616): about 300 triangles at most.
MAX_INSECT_TRIANGLES = 300
MAX_GLB_BYTES = 256 * 1024


def _load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def _writer():
    spec = importlib.util.spec_from_file_location("wildlife_write_materials",
                                                  ROOT / "assets_src/wildlife/common/write_materials.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.kinds = _load(vw.KINDS_FILE)
        self.zone = _load(f"{vw.WILDLIFE_DIR}/ch02_haluna.json")
        self.budgets = self.kinds["budgets"]
        self.locations = {r["id"] for r in _load(vw.LOCATIONS_FILE)["locations"]}

    def zone_errs(self, doc, where=f"{vw.WILDLIFE_DIR}/ch02_haluna.json") -> list[str]:
        return vw.zone_errors(doc, where, self.budgets, self.locations)

    def test_committed_data_passes(self) -> None:
        self.assertEqual(vw.wildlife_errors(ROOT), [])

    def test_kinds_need_every_tuning_key_and_existing_files(self) -> None:
        exists = lambda res: (ROOT / res[len("res://"):]).is_file()  # noqa: E731
        k = copy.deepcopy(self.kinds)
        del k["kinds"]["crab"]["flee_radius_m"]
        self.assertTrue(any("missing" in e and "flee_radius_m" in e for e in vw.kinds_errors(k, exists)))
        k = copy.deepcopy(self.kinds)
        k["kinds"]["gull"]["material"] = "res://assets/wildlife/gull/materials/nope.tres"
        self.assertTrue(any("material" in e for e in vw.kinds_errors(k, exists)))
        k = copy.deepcopy(self.kinds)
        k["kinds"]["fish"]["speed_mps"] = [0.5, 0.2]
        self.assertTrue(any("speed_mps" in e for e in vw.kinds_errors(k, exists)))
        k = copy.deepcopy(self.kinds)
        k["kinds"]["gull"]["meshes"] = {"flying": "gull_flying"}
        self.assertTrue(any("meshes" in e for e in vw.kinds_errors(k, exists)))

    def test_zone_id_must_name_the_file_and_a_location(self) -> None:
        z = copy.deepcopy(self.zone)
        z["zone"] = "ch02/elsewhere"
        errs = self.zone_errs(z)
        self.assertTrue(any("belongs in ch02_elsewhere.json" in e for e in errs))
        self.assertTrue(any("not a locations.json location" in e for e in errs))

    def test_ground_is_a_node_method_or_physics_alone(self) -> None:
        # the Act I audit (2026-10-29): crabs may follow the zone's collision instead of a terrain method
        z = copy.deepcopy(self.zone)
        z["ground"] = {"physics": True}
        self.assertFalse(any(".ground" in e for e in self.zone_errs(z)))
        z["ground"] = {"physics": True, "node": "Terrain"}
        self.assertTrue(any(".ground" in e for e in self.zone_errs(z)))
        z["ground"] = {"physics": False}
        self.assertTrue(any(".ground" in e for e in self.zone_errs(z)))

    def test_perches_must_be_inside_the_flock(self) -> None:
        z = copy.deepcopy(self.zone)
        z["flocks"][0]["perches"].append([500.0, 2.0, 500.0, 0.0])
        self.assertTrue(any("outside the flock's radius_m" in e for e in self.zone_errs(z)))
        z = copy.deepcopy(self.zone)
        z["flocks"][0]["perched_at_start"] = 99
        self.assertTrue(any("perched_at_start" in e for e in self.zone_errs(z)))

    def test_rows_are_checked(self) -> None:
        z = copy.deepcopy(self.zone)
        z["beaches"][0]["half_extents"] = [0.0, 2.0]
        z["shoals"][0]["count"] = 0
        z["shoals"][1]["id"] = z["shoals"][0]["id"]
        del z["flocks"][1]["radius_m"]
        errs = self.zone_errs(z)
        self.assertTrue(any("half_extents" in e for e in errs))
        self.assertTrue(any("count" in e for e in errs))
        self.assertTrue(any(".id" in e for e in errs))
        self.assertTrue(any("missing ['radius_m']" in e for e in errs))

    def test_budgets_are_enforced(self) -> None:
        z = copy.deepcopy(self.zone)
        z["shoals"][0]["count"] = self.budgets["fish"] + 1
        self.assertTrue(any("over the budget" in e for e in self.zone_errs(z)))


class InsectValidatorTest(unittest.TestCase):
    """M3-CRE-616: the insect kind's two tables, its per-mesh materials, and the zones' swarms."""

    def setUp(self) -> None:
        self.kinds = _load(vw.KINDS_FILE)
        self.zone = _load(f"{vw.WILDLIFE_DIR}/ch05_pemakar.json")
        self.budgets = self.kinds["budgets"]
        self.locations = {r["id"] for r in _load(vw.LOCATIONS_FILE)["locations"]}
        self.exists = lambda res: (ROOT / res[len("res://"):]).is_file()  # noqa: E731

    def zone_errs(self, doc) -> list[str]:
        return vw.zone_errors(doc, f"{vw.WILDLIFE_DIR}/ch05_pemakar.json", self.budgets, self.locations)

    def test_insect_tables_are_checked(self) -> None:
        k = copy.deepcopy(self.kinds)
        del k["kinds"]["insect"]["dragonfly"]["flee_radius_m"]
        self.assertTrue(any("dragonfly: missing" in e and "flee_radius_m" in e for e in vw.kinds_errors(k, self.exists)))
        k = copy.deepcopy(self.kinds)
        k["kinds"]["insect"]["moth"]["jitter_rate"] = [1.0, 2.0]  # read as a plain number
        self.assertTrue(any("moth.jitter_rate" in e for e in vw.kinds_errors(k, self.exists)))
        k = copy.deepcopy(self.kinds)
        k["kinds"]["insect"]["dragonfly"]["dart_m"] = [3.0, 1.0]
        self.assertTrue(any("dragonfly.dart_m" in e for e in vw.kinds_errors(k, self.exists)))
        k = copy.deepcopy(self.kinds)
        k["kinds"]["insect"]["moth"]["wingspan"] = 1.0
        self.assertTrue(any("unknown keys ['wingspan']" in e for e in vw.kinds_errors(k, self.exists)))
        k = copy.deepcopy(self.kinds)
        del k["kinds"]["insect"]["moth"]
        self.assertTrue(any("insect.moth: must be an object" in e for e in vw.kinds_errors(k, self.exists)))

    def test_insect_materials_are_one_per_mesh_and_exist(self) -> None:
        k = copy.deepcopy(self.kinds)
        del k["kinds"]["insect"]["material"]["dragonfly"]
        self.assertTrue(any("one per mesh" in e for e in vw.kinds_errors(k, self.exists)))
        k = copy.deepcopy(self.kinds)
        k["kinds"]["insect"]["material"]["moth"] = "res://assets/wildlife/insect/materials/nope.tres"
        self.assertTrue(any("material.moth" in e for e in vw.kinds_errors(k, self.exists)))

    def test_swarm_rows_are_checked(self) -> None:
        z = copy.deepcopy(self.zone)
        z["swarms"][0]["type"] = "beetle"
        z["swarms"][1]["center"] = [0.0, -24.0]
        z["swarms"][2]["radius_m"] = 0.0
        errs = self.zone_errs(z)
        self.assertTrue(any("swarms[0].type" in e for e in errs))
        self.assertTrue(any("swarms[1].center" in e for e in errs))
        self.assertTrue(any("swarms[2].radius_m" in e for e in errs))
        z = copy.deepcopy(self.zone)
        del z["swarms"][0]["type"]
        self.assertTrue(any("missing ['type']" in e for e in self.zone_errs(z)))

    def test_only_dragonflies_perch_and_inside_their_radius(self) -> None:
        z = copy.deepcopy(self.zone)
        z["swarms"][0]["perches"] = [[0.0, 2.2, -36.0, 0.0]]
        self.assertTrue(any("only a dragonfly patrol perches" in e for e in self.zone_errs(z)))
        z = copy.deepcopy(self.zone)
        z["swarms"][2]["perches"] = [[22.0, 0.5, -31.0, 90.0], [40.0, 0.5, -31.0, 0.0]]
        errs = self.zone_errs(z)
        self.assertTrue(any("perches[1]: outside the swarm's radius_m" in e for e in errs))
        self.assertFalse(any("perches[0]" in e for e in errs))

    def test_the_insect_budget_is_enforced(self) -> None:
        z = copy.deepcopy(self.zone)
        z["swarms"][2]["count"] = self.budgets["insects"]
        self.assertTrue(any("swarms" in e and "over the budget" in e for e in self.zone_errs(z)))
        self.assertEqual(self.budgets["draw_calls"], 10,
                         "ten MultiMeshes: gulls x2, kingfishers x2, crabs, fish, rays, moths, dragonflies, fireflies")

    def test_kingfisher_rows_are_flocks_with_their_own_budget(self) -> None:
        z = copy.deepcopy(self.zone)
        z["kingfishers"] = [{"id": "k", "center": [0.0, 0.0], "radius_m": 5.0, "altitude_m": [0.5, 1.5], "count": 2,
                             "perches": [[0.0, 0.4, 0.0, 0.0], [9.0, 0.4, 0.0, 0.0]]}]
        errs = self.zone_errs(z)
        self.assertTrue(any("kingfishers[0].perches[1]" in e for e in errs), errs)
        z["kingfishers"][0]["perches"].pop()
        z["kingfishers"][0]["count"] = self.budgets["kingfishers"] + 1
        self.assertTrue(any("kingfishers" in e and "over the budget" in e for e in self.zone_errs(z)))
        fen = _load(f"{vw.WILDLIFE_DIR}/ch10_ossa_fen.json")
        self.assertEqual(sum(k["count"] for k in fen["kingfishers"]), self.budgets["kingfishers"])

    def test_a_kingfisher_row_dives_to_water_below_its_perches(self) -> None:
        z = copy.deepcopy(self.zone)
        z["kingfishers"] = [{"id": "k", "center": [0.0, 0.0], "radius_m": 5.0, "altitude_m": [0.5, 1.5], "count": 1,
                             "perches": [[0.0, 0.4, 0.0, 0.0]], "water_y": 0.6}]
        self.assertTrue(any("water_y: must be below every perch" in e for e in self.zone_errs(z)))
        z["kingfishers"][0]["water_y"] = "low"
        self.assertTrue(any("water_y: must be a number" in e for e in self.zone_errs(z)))
        z["kingfishers"][0]["water_y"] = -0.25
        self.assertFalse(any("water_y" in e for e in self.zone_errs(z)))
        fen = _load(f"{vw.WILDLIFE_DIR}/ch10_ossa_fen.json")
        self.assertTrue(all(k.get("water_y") == -0.25 for k in fen["kingfishers"]), "the fen's channels at -0.25")

    def test_herd_rows_and_the_woolback_kind(self) -> None:
        z = copy.deepcopy(self.zone)
        z["herds"] = [{"id": "h", "center": [0.0, 0.0, 0.0], "radius_m": 0.0, "count": 2, "y": "low"}]
        errs = self.zone_errs(z)
        for want in ("herds[0].center", "herds[0].radius_m", "herds[0].y"):
            self.assertTrue(any(want in e for e in errs), (want, errs))
        z["herds"] = [{"id": "h", "center": [0.0, 0.0], "radius_m": 2.0, "count": self.budgets["woolbacks"] + 1}]
        self.assertTrue(any("herds" in e and "over the budget" in e for e in self.zone_errs(z)))
        k = copy.deepcopy(self.kinds)
        k["kinds"]["woolback"]["scene"] = "res://assets/creatures/woolback/woolback.glb"
        self.assertTrue(any("woolback.scene: must be the actor scene" in e for e in vw.kinds_errors(k, self.exists)))
        keth = _load(f"{vw.WILDLIFE_DIR}/ch12_keth_pass.json")
        self.assertEqual([(h["id"], h["count"]) for h in keth["herds"]], [("pass_foot", 2), ("saddle", 3)])

    def test_zone_swarms_as_placed(self) -> None:
        haluna = _load(f"{vw.WILDLIFE_DIR}/ch02_haluna.json")
        self.assertEqual([(s["type"], s["count"]) for s in haluna["swarms"]], [("dragonfly", 4)])
        self.assertEqual(sorted((s["type"], tuple(s["center"]), s["count"]) for s in self.zone["swarms"]), [
            ("dragonfly", (22.0, 1.2, -31.0), 4), ("moth", (0.0, 2.2, -36.0), 5), ("moth", (0.0, 2.2, -24.0), 5)])
        stage = _load(vw.STAGE_FILE)
        self.assertIn("moth", {s["type"] for s in stage["swarms"]}, "the review stage shows the moths")


class PipelineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.jobs = {j["id"]: j for j in _load("tools/dev/blender_builds.json")["jobs"]}
        self.kinds = _load(vw.KINDS_FILE)["kinds"]

    def test_materials_rebuild_byte_for_byte(self) -> None:
        w = _writer()
        for animal in ANIMALS:
            with tempfile.TemporaryDirectory() as tmp:
                t = Path(tmp)
                (t / "assets_src/wildlife" / animal).mkdir(parents=True)
                (t / "assets_src/wildlife" / animal / "materials.json").write_bytes(
                    (ROOT / "assets_src/wildlife" / animal / "materials.json").read_bytes())
                for p in w.write(animal, t):
                    committed = ROOT / p.relative_to(t)
                    self.assertEqual(p.read_bytes(), committed.read_bytes(), f"{committed} is stale")

    def test_every_animal_has_its_job_provenance_and_import(self) -> None:
        prov = (ROOT / "assets/PROVENANCE.md").read_text(encoding="utf-8")
        rules = _load("game/data/import/wildlife.json")
        for animal in ANIMALS:
            job = self.jobs.get(f"wildlife_{animal}")
            self.assertIsNotNone(job, f"tools/dev/blender_builds.json has no wildlife_{animal} job")
            self.assertIn(f"assets/wildlife/{animal}/*.glb", job["outputs"])
            self.assertIn(f"assets/wildlife/{animal}/materials/*.tres", job["outputs"])
            self.assertIn("assets_src/wildlife/common/**", job["sources"])
            self.assertIn("assets_src/creatures/common/creature_kit.py", job["sources"])
            self.assertIn(f"res://assets/wildlife/{animal}/", rules["assets"])
            for f in sorted((ROOT / "assets/wildlife" / animal).rglob("*")):
                if f.is_file() and f.suffix != ".import":
                    self.assertIn(f"| {f.relative_to(ROOT).as_posix()} |", prov)
            for glb in (ROOT / "assets/wildlife" / animal).glob("*.glb"):
                imp = (glb.parent / (glb.name + ".import")).read_text(encoding="utf-8")
                self.assertIn('import_script/path="res://game/core/import/wildlife_post_import.gd"', imp)

    def test_glbs_are_unskinned_meshes_with_the_shader_channels(self) -> None:
        names: dict[str, set[str]] = {}
        for animal in ANIMALS:
            glb = ROOT / "assets/wildlife" / animal / f"{animal}.glb"
            self.assertLess(glb.stat().st_size, MAX_GLB_BYTES, glb)
            js = read_glb(glb)
            self.assertNotIn("skins", js, f"{animal}: wildlife has no rig (MultiMesh + vertex shader)")
            self.assertNotIn("animations", js)
            names[animal] = {n["name"] for n in js["nodes"]}
            for m in js["meshes"]:
                tris = 0
                for p in m["primitives"]:
                    self.assertTrue({"COLOR_0", "TEXCOORD_0", "TEXCOORD_1", "NORMAL"} <= set(p["attributes"]))
                    self.assertNotIn("JOINTS_0", p["attributes"])
                    tris += js["accessors"][p["indices"]]["count"] // 3
                self.assertLessEqual(tris, MAX_INSECT_TRIANGLES if animal == "insect" else MAX_TRIANGLES,
                                     (animal, m["name"], tris))
            for mat in js["materials"]:
                self.assertTrue((ROOT / "assets/wildlife" / animal / "materials" / f"{mat['name']}.tres").is_file())
        for kind in self.kinds.values():
            if "meshes" not in kind:  # a skinned kind (the woolback): an actor scene, not a MultiMesh glb
                continue
            animal = Path(kind["scene"]).stem
            for mesh in kind["meshes"].values():
                self.assertIn(mesh, names[animal], (animal, mesh))

    def test_no_reserved_glimmer_or_wound_colours(self) -> None:
        reserved = {"#3FE0C8", "#7FC6D9", "#4FB3B0"}  # spawn_wound, glimmer_held, glimmer_bound (palette.json)
        for animal in ANIMALS:
            for f in [*(ROOT / "assets_src/wildlife" / animal).glob("*"), *(ROOT / "assets/wildlife" / animal).rglob("*.tres")]:
                text = f.read_text(encoding="utf-8").upper()
                for hexv in reserved:
                    self.assertNotIn(hexv, text, f"{f} uses a reserved light {hexv}")


if __name__ == "__main__":
    unittest.main()
