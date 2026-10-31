"""M3-C08-02: Ch8's chapter data (game/data/flow/chapters/ch08.json), its tunables
(game/data/flow/ch08_field.json) and the two greybox layouts, beyond what the shared validator reads:
the set piece's battle steps carry the stair meter, the flue trial's keys match the layout's
triggers and blocks, its flags are declared, and the extra layout keys (start_hidden, states_when)
name real blocks, actors, marks and flags.
Run: python3 -m unittest discover -s tools/tests"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import chapter_flow_check as cf  # noqa: E402
import validate_data as vd  # noqa: E402

CHAPTER = ROOT / "game/data/flow/chapters/ch08.json"
FIELD = ROOT / "game/data/flow/ch08_field.json"
CORROW = ROOT / "game/levels/ch08/corrow/corrow_layout.json"
COILSPIRE = ROOT / "game/levels/ch08/coilspire/coilspire_layout.json"
METER = "ch08_stair_groups_up"
SET_PIECE = {"ch08_stair_hold_1", "ch08_stair_hold_2", "ch08_stair_hold_3", "undertows_reach"}


def _json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _block_ids(layout: dict) -> set:
    """The layout's blocks plus its collision file's blocks and ramps (collision_path, ADR 0200; KitCollision)."""
    ids = {b["id"] for b in layout["blocks"]}
    if "collision_path" in layout:
        coll = _json(ROOT / layout["collision_path"].removeprefix("res://"))
        ids |= {b["id"] for b in coll.get("blocks", []) + coll.get("ramps", [])}
    return ids


def _with_collision(layout: dict) -> dict:
    """The layout with its kit collision file's blocks and ramps joined (KitCollision.merge, ADR 0200)."""
    if "collision_path" not in layout:
        return layout
    extra = _json(ROOT / layout["collision_path"].removeprefix("res://"))
    return dict(layout, blocks=layout["blocks"] + extra.get("blocks", []) + extra.get("ramps", []))


def _steps(zone: dict):
    for row in zone.get("arrive", []):
        yield from row.get("steps", [])
    for beat in zone.get("beats", {}).values():
        yield from beat.get("steps", [])


class Ch08FlowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.chapter = _json(CHAPTER)
        cls.field = _json(FIELD)
        cls.flags = vd.declared_flags_quiet(ROOT)
        zones = (("ch08/corrow", CORROW), ("ch08/coilspire", COILSPIRE))
        cls.layouts = {loc: _with_collision(_json(p)) for loc, p in zones}

    def test_every_set_piece_fight_carries_the_stair_meter(self) -> None:
        seen = set()
        for step in _steps(self.chapter["zones"]["ch08/corrow"]):
            if step.get("battle") in SET_PIECE:
                seen.add(step["battle"])
                self.assertEqual(step.get("objective_flag"), METER, step["battle"])
                self.assertEqual(step.get("return_spawn"), "WallHead", step["battle"])
        self.assertEqual(seen, SET_PIECE, "all four fights are in the flow")

    def test_battle_parties_are_the_sim_suites(self) -> None:
        suites = {s["encounter"]: s for s in _json(ROOT / "tools/balance/targets.json")["suites"]
                  if s.get("encounter") in SET_PIECE}
        for step in _steps(self.chapter["zones"]["ch08/corrow"]):
            if step.get("battle") in SET_PIECE:
                suite = suites[step["battle"]]
                self.assertEqual(step["party"], suite["active"], step["battle"])
                self.assertEqual(step["reserve"], suite["reserve"], step["battle"])

    def test_an_undeclared_objective_flag_is_caught(self) -> None:
        c = copy.deepcopy(self.chapter)
        for step in _steps(c["zones"]["ch08/corrow"]):
            if step.get("battle") == "ch08_stair_hold_1":
                step["objective_flag"] = "no_such_meter"
        files = vd.load_json_files(ROOT, vd.Report())
        enc = files["game/data/battle/encounters.json"]
        chars = files["game/data/battle/characters.json"]
        ctx = cf.Context(
            flags=self.flags,
            dialogue={p.stem for p in (ROOT / "game/data/dialogue/compiled").glob("*.json")},
            encounters={r["id"] for r in enc["encounters"]},
            heroes={r["id"] for r in chars["characters"]},
            locations={"ch08/corrow": "", "ch08/coilspire": "", "ch09/corrow_night": "", "ch18/kite": ""},
            layouts=dict(self.layouts, **{"ch09/corrow_night": None}),
            scene_exists=lambda res: True,
        )
        self.assertEqual(cf.chapter_errors(self.chapter, "ch08.json", ctx), [])
        errs = cf.chapter_errors(c, "ch08.json", ctx)
        self.assertTrue(any("no_such_meter" in e for e in errs), errs)

    def test_the_trial_matches_the_layout(self) -> None:
        trial = self.field["trial"]
        layout = self.layouts["ch08/coilspire"]
        blocks = _block_ids(layout)
        flues = {t["payload"]["flue"] for t in layout["triggers"] if "flue" in t.get("payload", {})}
        keys = set()
        for tier in trial["tiers"]:
            keys |= set(tier["keys"])
            self.assertTrue(set(tier["draw"]) <= set(tier["keys"]), tier["id"])
            self.assertTrue(tier["draw"], tier["id"])
            for extra in ("side", "seized"):
                if extra in tier:
                    self.assertIn(tier[extra], tier["keys"], tier["id"])
            self.assertNotIn(tier.get("side"), tier["draw"], "a side flue never draws the flame up")
            self.assertIn("Flame_" + tier["id"], blocks)
            self.assertIn("Gate_" + tier["id"], blocks)
        self.assertEqual(flues, keys, "one interact trigger per flue-key")
        for k in keys:
            self.assertIn("Key_" + k, blocks)
        for key in ("begun_flag", "tiers_flag", "crown_flag", "niche_flag", "seized_flag"):
            self.assertIn(trial[key], self.flags, key)
        self.assertIn(trial["seized_beat"], self.chapter["zones"]["ch08/coilspire"]["beats"])
        self.assertTrue((ROOT / "game/data/dialogue/compiled" / (trial["hint_scene"] + ".json")).is_file())

    def test_extra_layout_keys_name_real_things(self) -> None:
        for loc, layout in self.layouts.items():
            blocks = _block_ids(layout)
            actors = set(layout.get("actors", {}))
            marks = set(layout.get("marks", {}))
            for b in layout.get("start_hidden", []):
                self.assertIn(b, blocks, loc)
            for row in layout.get("states", []) + layout.get("states_when", []):
                for f in row.get("when", {}).get("set", []) + row.get("when", {}).get("unset", []):
                    self.assertIn(f, self.flags, loc)
                if "flag" in row:
                    self.assertIn(row["flag"], self.flags, loc)
                for i in row.get("hide", []) + row.get("show", []):
                    self.assertIn(i, blocks | actors, f"{loc}: {i}")
                for a, m in row.get("place", {}).items():
                    self.assertIn(a, actors, f"{loc}: {a}")
                    self.assertIn(m, marks, f"{loc}: {m}")
            for row in layout.get("lights", []):
                self.assertIn(row["flag"], self.flags, loc)

    def test_mend_names_a_real_encounter(self) -> None:
        enc = {r["id"] for r in _json(ROOT / "game/data/battle/encounters.json")["encounters"]}
        self.assertIn(self.field["mend"]["encounter"], enc)
        self.assertGreater(self.field["mend"]["hp_pct"], 0)

    def test_ch7_hands_off_to_corrow_and_ch8_to_the_strand(self) -> None:
        ch07 = _json(ROOT / "game/data/flow/chapters/ch07.json")
        leave = ch07["zones"]["ch07/tamsule"]["beats"]["leave"]["steps"][-1]
        self.assertEqual(leave, {"go": {"location": "ch08/corrow", "spawn": "Mole"}})
        out = self.chapter["zones"]["ch08/corrow"]["beats"]["cut_rope"]["steps"][-1]
        self.assertEqual(out, {"go": {"location": "ch09/corrow_night", "spawn": "Strand"}})
        files = _json(ROOT / "game/data/flow/chapters.json")["chapters"]["files"]
        names = [Path(f).stem for f in files]
        self.assertEqual(names.index("ch08"), names.index("ch07") + 1, "in story order")


if __name__ == "__main__":
    unittest.main()
