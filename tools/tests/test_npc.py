"""Field villager data (M3-CRE-613). Run: python3 -m unittest discover -s tools/tests

* tools/validate_npc.py: the committed tuning, zone files and test stage pass; each kind of mistake is caught.
"""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_npc as vn  # noqa: E402

HALUNA = f"{vn.ZONES_DIR}/ch02_haluna.json"


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class CommittedData(unittest.TestCase):
    def test_committed_data_passes(self) -> None:
        self.assertEqual(vn.npc_errors(ROOT), [])

    def test_haluna_places_the_seven_villagers(self) -> None:
        ids = {r["npc_id"] for r in _load(HALUNA)["villagers"]}
        self.assertEqual(ids, {"child", "fisher", "neme", "netmender", "osu", "reed", "vendor",
                               "shopkeeper", "smith", "innkeeper"})


class ZoneMistakes(unittest.TestCase):
    def _errors(self, data: dict, name: str = "ch02_haluna.json") -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(json.dumps(data), encoding="utf-8")
            # Actor scenes and locations resolve against the real repository.
            rel = path.relative_to(Path(tmp))
            orig = vn.ACTOR
            try:
                vn.ACTOR = str(ROOT / orig)
                return vn.zone_errors(Path(tmp), str(rel), vn._location_ids(ROOT), vn._declared_flags(ROOT))
            finally:
                vn.ACTOR = orig

    def _haluna(self) -> dict:
        return copy.deepcopy(_load(HALUNA))

    def test_the_unchanged_file_passes(self) -> None:
        self.assertEqual(self._errors(self._haluna()), [])

    def test_zone_must_name_the_file_and_be_a_location(self) -> None:
        d = self._haluna()
        self.assertTrue(any("does not name the file" in e for e in self._errors(d, "ch03_other.json")))
        d["zone"] = "ch99/nowhere"
        self.assertTrue(any("not a location" in e for e in self._errors(d, "ch99_nowhere.json")))

    def test_unknown_villager_and_duplicates(self) -> None:
        d = self._haluna()
        d["villagers"][0]["npc_id"] = "stranger"
        self.assertTrue(any("no actor scene" in e for e in self._errors(d)))
        d = self._haluna()
        d["villagers"].append(copy.deepcopy(d["villagers"][0]))
        self.assertTrue(any("appears twice" in e for e in self._errors(d)))

    def test_a_worn_actor_must_exist(self) -> None:
        d = self._haluna()
        d["villagers"][0]["actor"] = "stranger"
        self.assertTrue(any("actor 'stranger'" in e for e in self._errors(d)))
        d = self._haluna()
        d["villagers"][0]["npc_id"] = "shop_hand"
        d["villagers"][0]["actor"] = "vendor"
        self.assertEqual(self._errors(d), [], "an id without its own model passes while it wears one")

    def test_chat_partners_must_chat_back(self) -> None:
        d = self._haluna()
        for r in d["villagers"]:
            if r["npc_id"] == "fisher":
                r["chat_with"] = "vendor"
        errs = self._errors(d)
        self.assertTrue(any("does not chat back" in e for e in errs), errs)

    def test_routes_shelters_and_flags(self) -> None:
        d = self._haluna()
        d["villagers"][0]["route"] = [[0, 0, 0]]
        d["villagers"][1]["route"] = [{"at": [0, 0, 0], "activity": "dance"}, [1, 0, 0]]
        d["villagers"][2]["shelter"] = [1, 2]
        d["storm_flag"] = "no_such_flag"
        d["villagers"][3]["attach"] = "child"
        d["villagers"][3]["route"] = [[0, 0, 0], [1, 0, 0]]
        d["villagers"][5]["attach"] = "inside"
        errs = " | ".join(self._errors(d))
        for needle in ("two or more points", "unknown activity", "shelter is not", "not declared", "has no route",
                       "is not one of"):
            self.assertIn(needle, errs)


class TuningMistakes(unittest.TestCase):
    def test_ranges_in_order_and_sections_present(self) -> None:
        data = _load(vn.NPC_FILE)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / vn.NPC_FILE).parent.mkdir(parents=True)
            bad = copy.deepcopy(data)
            bad["defaults"]["glance"]["hold_sec"] = [3.0, 1.0]
            del bad["defaults"]["storm"]["react_sec"]
            (root / vn.NPC_FILE).write_text(json.dumps(bad), encoding="utf-8")
            errs = " | ".join(vn.tuning_errors(root))
        self.assertIn("not in order", errs)
        self.assertIn("lacks react_sec", errs)


if __name__ == "__main__":
    unittest.main()
