"""Tests for the M1-ART-02 post-import rules. Run: python3 -m unittest discover -s tools/tests

* The import fixture (tests/fixtures/import/import_probe.glb) is reproducible: its generator writes
  the committed bytes, and it carries the -col, -lod1, -noimp and PLACEHOLDER cases the Godot test
  (tests/unit/test_post_import.gd) asserts after the real import.
* Each rules file in game/data/import/ is well formed, names a script that exists, and every
  material it maps by node or by slot exists for the committed assets.
"""

from __future__ import annotations

import importlib.util
import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "import"
RULES_DIR = ROOT / "game" / "data" / "import"
KINDS = {
    "ashcrown_kit", "base_body", "brightwater_ferry_kit", "brine_shoals_kit", "characters", "coilspire_kit",
    "corrow_kit", "creatures", "crowd", "haluna_kit", "oruvel_kit", "oruvel_underway_kit", "pemakar_kit", "shader_test",
    "tamsule_bell_kit", "vegetation", "wildlife",
}


def res(path: str) -> Path:
    return ROOT / path.removeprefix("res://")


def read_glb(path: Path) -> dict:
    data = path.read_bytes()
    magic, _version, _total = struct.unpack_from("<III", data, 0)
    assert magic == 0x46546C67, "not a glb"
    length, _kind = struct.unpack_from("<II", data, 12)
    return json.loads(data[20 : 20 + length])


def load_rules() -> dict[str, dict]:
    return {p.stem: json.loads(p.read_text()) for p in sorted(RULES_DIR.glob("*.json"))}


class FixtureTest(unittest.TestCase):
    def setUp(self) -> None:
        spec = importlib.util.spec_from_file_location("build_import_probe", FIXTURE_DIR / "build_import_probe.py")
        assert spec and spec.loader
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)

    def test_committed_fixture_is_the_generator_output(self) -> None:
        self.assertEqual(self.mod.build(), (FIXTURE_DIR / "import_probe.glb").read_bytes())

    def test_fixture_has_every_case_the_godot_test_needs(self) -> None:
        gltf = read_glb(FIXTURE_DIR / "import_probe.glb")
        names = {n["name"]: n for n in gltf["nodes"]}
        for name in ("probe_post", "probe_post-lod1", "probe_post-col", "probe_marker-noimp", "probe_slab"):
            self.assertIn(name, names)
        self.assertTrue(names["probe_slab"]["extras"]["placeholder"].startswith("PLACEHOLDER: "))
        self.assertEqual(sorted(m["name"] for m in gltf["materials"]), ["kit_lashing", "kit_timber"])

    def test_fixture_import_runs_the_kit_rules(self) -> None:
        text = (FIXTURE_DIR / "import_probe.glb.import").read_text()
        self.assertIn('import_script/path="res://game/core/import/haluna_kit_post_import.gd"', text)


class RulesTest(unittest.TestCase):
    def test_one_rules_file_per_category_with_its_script(self) -> None:
        rules = load_rules()
        self.assertEqual(set(rules), KINDS)
        for kind, r in rules.items():
            with self.subTest(kind=kind):
                self.assertEqual(r["kind"], kind)
                self.assertEqual(r["script"], f"res://game/core/import/{kind}_post_import.gd")
                self.assertTrue(res(r["script"]).is_file())
                self.assertIsInstance(r["generate_lods"], bool)
                for d in list(r["assets"]) + list(r.get("adoption_pending", {})):
                    self.assertTrue(d.endswith("/") and res(d).is_dir(), d)

    def test_mapped_materials_exist(self) -> None:
        for kind, r in load_rules().items():
            mats = r.get("materials", {})
            for node, path in mats.get("by_node", {}).items():
                with self.subTest(kind=kind, node=node):
                    self.assertTrue(res(path).is_file(), path)
            slot_dir = mats.get("slot_dir", "")
            if not slot_dir:
                continue
            for d in r["assets"]:
                folder = res(slot_dir.replace("{asset_dir}", d.rstrip("/")))
                for glb in sorted(res(d).glob("*.glb")):
                    for m in read_glb(glb).get("materials", []):
                        with self.subTest(kind=kind, glb=glb.name, slot=m["name"]):
                            self.assertTrue((folder / f"{m['name']}.tres").is_file())

    def test_lod_tables_increase(self) -> None:
        for kind, r in load_rules().items():
            ends = r.get("lods", {}).get("end_m", [])
            with self.subTest(kind=kind):
                self.assertEqual(ends, sorted(ends))
                self.assertTrue(all(e > 0 for e in ends))


if __name__ == "__main__":
    unittest.main()
