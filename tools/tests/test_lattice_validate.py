"""Lattice and Facet checks in tools/validate_data.py. Run: python3 -m unittest discover -s tools/tests"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

BOARD = "game/data/progression/lattice_standard.json"
FACETS = "game/data/progression/facets.json"


class LatticeValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        for rel in ("game", "assets", "tools/banned_terms.txt", "docs/kb/glossary.md"):
            src, dst = ROOT / rel, self.tmp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dst)
            elif src.exists():
                shutil.copy(src, dst)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def load(self, rel: str) -> dict:
        return json.loads((self.tmp / rel).read_text(encoding="utf-8"))

    def save(self, rel: str, doc: dict) -> None:
        (self.tmp / rel).write_text(json.dumps(doc), encoding="utf-8")

    def node(self, doc: dict, nid: str) -> dict:
        return next(n for n in doc["nodes"] if n["id"] == nid)

    def errors(self) -> list[str]:
        return vd.run(self.tmp).errors

    def assert_error(self, needle: str) -> None:
        errs = self.errors()
        self.assertTrue(any(needle in e for e in errs), f"no error containing {needle!r} in {errs}")

    def test_repo_lattice_is_clean(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_dangling_edge(self) -> None:
        b = self.load(BOARD)
        b["edges"].append(["rh_01", "nowhere"])
        self.save(BOARD, b)
        self.assert_error("dangling edge [rh_01, nowhere]")

    def test_unreachable_node(self) -> None:
        b = self.load(BOARD)
        b["nodes"].append({"id": "island", "type": "stat", "stat": "luck", "value": 1, "x": 40, "y": 40})
        self.save(BOARD, b)
        self.assert_error("unreachable from rhen's start")

    def test_unknown_skill(self) -> None:
        b = self.load(BOARD)
        self.node(b, "rh_03")["skill"] = "no_such_skill"
        self.save(BOARD, b)
        self.assert_error("unknown skill 'no_such_skill'")

    def test_invalid_stat_name(self) -> None:
        b = self.load(BOARD)
        self.node(b, "rh_01")["stat"] = "level"
        self.save(BOARD, b)
        self.assert_error("unknown stat 'level'")

    def test_gate_needs_level(self) -> None:
        b = self.load(BOARD)
        del self.node(b, "rh_07")["gate_level"]
        self.save(BOARD, b)
        self.assert_error("gate needs a gate_level")

    def test_gate_level_above_max(self) -> None:
        b = self.load(BOARD)
        self.node(b, "rh_07")["gate_level"] = 9
        self.save(BOARD, b)
        self.assert_error("gate needs a gate_level in 1..4")

    def test_duplicate_coordinates(self) -> None:
        b = self.load(BOARD)
        self.node(b, "rh_01").update({"x": 0, "y": 0})
        self.save(BOARD, b)
        self.assert_error("duplicate coordinates (0, 0)")

    def test_field_on_wrong_node_type(self) -> None:
        b = self.load(BOARD)
        self.node(b, "rh_07")["skill"] = "attack"
        self.save(BOARD, b)
        self.assert_error("field 'skill' does not belong on a gate node")

    def test_start_for_unknown_character(self) -> None:
        b = self.load(BOARD)
        self.node(b, "rhen_start")["character"] = "nobody"
        self.save(BOARD, b)
        self.assert_error("start for unknown character 'nobody'")

    def test_missing_board_loc_key(self) -> None:
        b = self.load(BOARD)
        b["board"]["name_key"] = "LATTICE_MISSING"
        self.save(BOARD, b)
        self.assert_error("LATTICE_MISSING")

    def test_facets_need_every_type(self) -> None:
        f = self.load(FACETS)
        f["facets"] = [x for x in f["facets"] if x["type"] != "fortune"]
        self.save(FACETS, f)
        self.assert_error("no facet of type 'fortune'")
        self.assert_error("no facet activates stat 'luck'")

    def test_facet_stat_claimed_twice(self) -> None:
        f = self.load(FACETS)
        f["facets"][0]["stats"].append("magic")
        self.save(FACETS, f)
        self.assert_error("stat 'magic' is already activated by 'facet_power'")

    def test_key_facet_for_every_gate_level(self) -> None:
        f = self.load(FACETS)
        f["facets"] = [x for x in f["facets"] if x.get("level") != 2]
        self.save(FACETS, f)
        self.assert_error("no key facet for gate level 2")

    def test_rules_must_be_complete(self) -> None:
        f = self.load(FACETS)
        del f["rules"]["move_cost"]
        f["rules"]["teleport"] = 1
        self.save(FACETS, f)
        self.assert_error("rules.move_cost must be a non-negative int")
        self.assert_error("unknown rule 'teleport'")


if __name__ == "__main__":
    unittest.main()
