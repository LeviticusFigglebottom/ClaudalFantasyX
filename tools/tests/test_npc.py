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


CROWD_ZONE = f"{vn.ZONES_DIR}/ch06_brine_shoals.json"


class Crowd(unittest.TestCase):
    """M3-CRE-659 (ADR 0152): the crowd roster, its zone rows, the variety rule and the generator."""

    def setUp(self) -> None:
        self.crowd = _load(vn.CROWD_FILE)
        self.people = {p["id"]: p for p in self.crowd["people"]}

    def _zone_errors(self, data: dict, people: dict | None = None, name: str = "ch06_brine_shoals.json") -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(json.dumps(data), encoding="utf-8")
            orig = vn.CROWD_ACTOR
            try:
                vn.CROWD_ACTOR = str(ROOT / orig)
                return vn.zone_errors(Path(tmp), name, vn._location_ids(ROOT), vn._declared_flags(ROOT),
                                      people if people is not None else self.people)
            finally:
                vn.CROWD_ACTOR = orig

    def _crowd_errors(self, crowd: dict) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in (vn.CROWD_FILE, vn.PALETTE_FILE):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / vn.CROWD_FILE).write_text(json.dumps(crowd), encoding="utf-8")
            (root / vn.PALETTE_FILE).write_text((ROOT / vn.PALETTE_FILE).read_text(encoding="utf-8"), encoding="utf-8")
            (root / vn.ZONES_DIR).mkdir(parents=True, exist_ok=True)
            for f in (ROOT / vn.ZONES_DIR).glob("*.json"):
                (root / vn.ZONES_DIR / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
            orig = vn.CROWD_ACTOR
            try:
                vn.CROWD_ACTOR = str(ROOT / orig)
                return vn.crowd_errors(root, vn._location_ids(ROOT))
            finally:
                vn.CROWD_ACTOR = orig

    def test_the_committed_roster_and_rows_pass(self) -> None:
        self.assertEqual(vn.crowd_errors(ROOT, vn._location_ids(ROOT)), [])

    def test_every_listed_capsule_is_a_person(self) -> None:
        """The task's inventory (Haluna's own villagers excepted) plus Tamsule's board-caller, a person
        (ch07_bark_board.dlg), and the six wrights who stand for Brine Shoals' `wrights` group."""
        by_zone: dict[str, set[str]] = {}
        for p in self.crowd["people"]:
            by_zone.setdefault(p["zone"], set()).add(p["stage_actor"])
        self.assertEqual(by_zone["ch07/tamsule"], {"board", "boatman", "child", "fisher", "netmender",
                                                   "trader_boatman", "vendor"})
        self.assertEqual(by_zone["ch05/pemakar"], {"boat_fisher", "boat_seller", "ferryman_mate", "folder", "folder_2",
                                                   "forge_child", "grave_child", "lacquerer", "sweeper", "weir_child"})
        self.assertEqual(sum(p["stage_actor"] == "wrights" for p in self.crowd["people"]),
                         self.crowd["groups"]["brine_shoals_wrights"]["people"])
        self.assertNotIn("ch04/haluna_wake", by_zone, "Haluna's own villagers keep their M2-CHR-03 bodies")
        self.assertEqual(len(self.crowd["people"]), 56)

    def test_crowd_rows_must_match_their_person(self) -> None:
        data = copy.deepcopy(_load(CROWD_ZONE))
        self.assertEqual(self._zone_errors(data), [])
        data["villagers"][0]["crowd"] = "nobody"
        data["villagers"][1]["stand_in"] = "CutsceneStage/Actors/clerk_b"
        data["villagers"][2]["offset"] = [1, 2]
        data["villagers"][3]["attach"] = "beside"
        data["villagers"][3]["offset"] = [0, 0, 0]
        errs = " | ".join(self._zone_errors(data))
        for needle in ("is not a person", "stands at stage actor", "offset is not", "inside its stand-in"):
            self.assertIn(needle, errs)
        errs = " | ".join(self._zone_errors(copy.deepcopy(_load(CROWD_ZONE)), name="ch07_tamsule.json"))
        self.assertIn("does not name the file", errs)

    def test_a_crowd_person_must_stand_in_the_rows_zone(self) -> None:
        data = copy.deepcopy(_load(CROWD_ZONE))
        people = copy.deepcopy(self.people)
        people[data["villagers"][0]["crowd"]]["zone"] = "ch07/tamsule"
        self.assertTrue(any("stands in 'ch07/tamsule'" in e for e in self._zone_errors(data, people)))

    def test_roster_mistakes_are_caught(self) -> None:
        bad = copy.deepcopy(self.crowd)
        ps = bad["people"]
        ps[0]["tints"]["cloth_a"] = "#00FF00"  # no palette mix makes pure green
        ps[1]["tints"].pop("hair")
        ps[2]["body"] = "crowd_nobody"
        ps[3]["age_band"] = "elder"
        ps[4]["work"] = "juggle"
        ps[5]["zone"] = "ch99/nowhere"
        ps.append(copy.deepcopy(ps[6]))
        ghost = copy.deepcopy(ps[7])
        ghost["id"] = "ghost_person"  # no zone row places it
        ps.append(ghost)
        errs = " | ".join(self._crowd_errors(bad))
        for needle in ("is not a palette swatch", "tints must be exactly", "is not planned", "age_band 'elder'",
                       "not a crowd work clip", "is not a location", "id appears twice", "zone rows"):
            self.assertIn(needle, errs)

    def test_palette_mixes_pass_and_others_fail(self) -> None:
        sw = vn.tint_swatches(ROOT)
        self.assertLessEqual(vn.mix_distance((0x2B, 0x3A, 0x6B), sw), vn.TINT_TOLERANCE, "indigo_dye itself")
        mid = tuple((a + b) / 2 for a, b in zip((0x2B, 0x3A, 0x6B), (0xC9, 0xB4, 0x8E)))
        self.assertLessEqual(vn.mix_distance(mid, sw), vn.TINT_TOLERANCE, "half indigo, half sand cloth")
        self.assertGreater(vn.mix_distance((0, 255, 0), sw), vn.TINT_TOLERANCE)

    def test_variety(self) -> None:
        """No two people in one zone share a body, and a body repeats only across zones, in tints at least
        VARIETY_MIN apart."""
        people = self.crowd["people"]
        self.assertEqual(vn.variety_errors(people), [])
        zones: dict[str, list[str]] = {}
        for p in people:
            zones.setdefault(p["zone"], []).append(p["body"])
        for zone, bodies in zones.items():
            self.assertEqual(len(bodies), len(set(bodies)), f"{zone} repeats a body")
        clone = copy.deepcopy(people)
        same_zone = [p for p in clone if p["zone"] == "ch05/pemakar"]
        same_zone[1]["body"] = same_zone[0]["body"]
        self.assertTrue(any("both wear" in e for e in vn.variety_errors(clone)))
        clone = copy.deepcopy(people)
        a = next(p for p in clone if p["zone"] == "ch08/corrow")
        b = next(p for p in clone if p["zone"] == "ch07/tamsule" and p["age_band"] == "adult")
        b["body"], b["tints"] = a["body"], dict(a["tints"])
        self.assertTrue(any("near-identical tints" in e for e in vn.variety_errors(clone)))

    def test_the_generator_output_is_committed(self) -> None:
        sys.path.insert(0, str(ROOT / "assets_src" / "crowd"))
        import gen_crowd

        files, roster = gen_crowd.generate()
        for name, text in files.items():
            self.assertEqual((ROOT / "assets_src" / "crowd" / "params" / name).read_text(encoding="utf-8"), text, name)
        self.assertEqual((ROOT / vn.CROWD_FILE).read_text(encoding="utf-8"), roster)

    def test_bodies_span_ages_builds_and_hair_and_are_new_faces(self) -> None:
        sys.path.insert(0, str(ROOT / "assets_src" / "crowd"))
        import gen_crowd

        ranges = gen_crowd.load_json(gen_crowd.RANGES)
        params = {p.stem: json.loads(p.read_text(encoding="utf-8"))
                  for p in sorted((ROOT / "assets_src" / "crowd" / "params").glob("*.json"))}
        plan = self.crowd["bodies"]
        self.assertGreaterEqual(len(params), 18)
        self.assertEqual(set(params), set(plan))
        bands = [b["age_band"] for b in plan.values()]
        self.assertGreaterEqual(bands.count("child"), 3)
        self.assertGreaterEqual(bands.count("elder"), 2)
        for sex in ("male", "female"):
            builds = {b["build"] for b in plan.values() if b["age_band"] == "adult" and b["sex"] == sex
                      and b["kit"] != "robe"}
            self.assertEqual(builds, {"lean", "medium", "heavy"}, sex)
        kinds = {p["_hair"]["kind"] for p in params.values()}
        self.assertEqual(kinds, {"short", "cropped", "bun", "wrap"}, "every villager_hair kind")
        scale = gen_crowd.face_scale(ranges)
        need = ranges["face"]["face_min_distance"]
        for name, h in gen_crowd.haluna_faces().items():
            for bid, p in params.items():
                self.assertGreaterEqual(gen_crowd.face_distance(p, h, scale), need, f"{bid} is too near {name}")
        for bid, p in params.items():
            for other, q in params.items():
                if bid < other and plan[bid]["age_band"] == plan[other]["age_band"]:
                    self.assertGreaterEqual(gen_crowd.face_distance(p, q, scale), need, f"{bid} vs {other}")
            self.assertEqual(p["_work"], sorted({q["work"] for q in self.crowd["people"]
                                                 if q["body"] == bid and q["work"]}), bid)

    def test_crowd_imports_with_its_rules_and_ships_lod1_only(self) -> None:
        rules = _load("game/data/import/crowd.json")
        for bid in self.crowd["bodies"]:
            d = ROOT / "assets" / "crowd" / bid
            self.assertIn(f"res://assets/crowd/{bid}/", rules["assets"])
            self.assertEqual(sorted(p.name for p in d.glob("*.glb")), [f"{bid}.glb"], f"{bid}: one LOD1 GLB")
            imp = (d / f"{bid}.glb.import").read_text(encoding="utf-8")
            self.assertIn('import_script/path="res://game/core/import/crowd_post_import.gd"', imp)
            self.assertTrue((d / "anim" / f"{bid}_clips.tres").exists())
            size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file() and f.suffix != ".import")
            self.assertLess(size, 3_000_000, f"{bid}: {size} bytes")


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
