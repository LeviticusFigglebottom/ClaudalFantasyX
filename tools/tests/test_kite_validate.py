"""M3-UI-205: tools/validate_data.py's checks on the Kite's world map (game/data/world/kite.json)."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

DOC = {
    "kite": {
        "open_flag": "kite_flying",
        "columns": ["A", "B"],
        "rows": 2,
        "regions": [{"id": "reach", "name_key": "K", "at": [0.2, 0.8]}],
        "destinations": [
            {"id": "home", "region": "reach", "location_id": "isle", "spawn": "S", "requires_flag": "f", "at": [0.1, 0.9]}
        ],
        "secrets": [
            {"id": "cove", "region": "reach", "location_id": "isle", "spawn": "S", "found_flag": "g", "cell": "B2",
             "at": [0.7, 0.7], "name_key": "C"}
        ],
    }
}
FLAGS = {"kite_flying", "f", "g"}
LOCS = {"isle": {}}


class KiteValidateTest(unittest.TestCase):
    def errs(self, doc: dict, flags: set[str] | None = FLAGS) -> list[str]:
        return vd.kite_errors(doc, flags, LOCS)

    def test_a_good_doc_and_the_shipped_file_pass(self) -> None:
        self.assertEqual(self.errs(DOC), [])
        shipped = json.loads((ROOT / vd.KITE_FILE).read_text(encoding="utf-8"))
        locs = json.loads((ROOT / vd.LOCATIONS_FILE).read_text(encoding="utf-8"))
        known = {r["id"]: r for r in locs["locations"]}
        self.assertEqual(vd.kite_errors(shipped, vd.declared_flags_quiet(ROOT), known), [])

    def test_bad_rows_are_named(self) -> None:
        cases = [
            (("destinations", 0, "region"), "nowhere", "unknown region"),
            (("destinations", 0, "location_id"), "nowhere", "unknown location"),
            (("destinations", 0, "at"), [2, 0], "at must be"),
            (("destinations", 0, "requires_flag"), "undeclared", "is not declared"),
            (("secrets", 0, "cell"), "C1", "is not on the chart"),
            (("secrets", 0, "cell"), "A9", "is not on the chart"),
            (("secrets", 0, "id"), "home", "id used twice"),
        ]
        for (table, i, key), value, says in cases:
            doc = copy.deepcopy(DOC)
            doc["kite"][table][i][key] = value
            self.assertTrue(any(says in e for e in self.errs(doc)), (key, value, self.errs(doc)))
        self.assertTrue(vd.kite_errors({}, FLAGS, LOCS))
        doc = copy.deepcopy(DOC)
        doc["kite"]["columns"] = []
        self.assertTrue(any("columns must" in e for e in self.errs(doc)))
        self.assertEqual(self.errs(DOC, None), [], "None: flags not checked")


if __name__ == "__main__":
    unittest.main()
