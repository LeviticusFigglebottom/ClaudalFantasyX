"""M3-C04-02: the Ch4 data the shared validators don't read yet.
* The two greybox layouts' "states" rows (Ch04Zone): every flag is declared in flags.tres, every id
  they hide or show is a block or a stage actor of that layout, and every actor they place stands on a
  mark of that layout.
* The ferry's random fights can never start on the ferry (ADR 0017 (d)): the layout's encounters run
  only between boarding the derelict and the Spar-Wraith's fall.
* An encounter's turn prompt (BattleBossHud: "turn_prompt_hero" and "turn_prompt_key") names a real
  hero, and comes as a pair.
* Ch4's zone roots count as greybox zones for the validators (their spawns come from the layout).
Run: python3 -m unittest discover -s tools/tests"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import chapter_flow_check as cf  # noqa: E402
import validate_data as vd  # noqa: E402

LAYOUTS = {
    "game/levels/ch04/haluna_wake/haluna_wake.tscn": "game/levels/ch04/haluna_wake/haluna_wake_layout.json",
    "game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn":
        "game/levels/ch04/brightwater_ferry/brightwater_ferry_layout.json",
}


def _json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


class StatesTest(unittest.TestCase):
    def test_every_state_row_names_declared_flags_and_real_ids(self) -> None:
        flags = vd.declared_flags_quiet(ROOT)
        for rel in LAYOUTS.values():
            layout = _json(rel)
            things = {b["id"] for b in layout.get("blocks", [])} | set(layout.get("actors", {}))
            marks = set(layout.get("marks", {}))
            self.assertTrue(layout.get("states"), rel)
            for row in layout["states"]:
                self.assertIn(row["flag"], flags, f"{rel}: undeclared flag {row['flag']}")
                for key in ("hide", "show"):
                    for thing in row.get(key, []):
                        self.assertIn(thing, things, f"{rel}: no block or actor '{thing}'")
                for actor, mark in row.get("place", {}).items():
                    self.assertIn(actor, layout.get("actors", {}), f"{rel}: no actor '{actor}'")
                    self.assertIn(mark, marks, f"{rel}: no mark '{mark}'")

    def test_the_ferry_is_never_attacked(self) -> None:
        enc = _json(LAYOUTS["game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn"])["encounters"]
        self.assertIn("ch04_boarded_derelict", enc["when"]["set"])
        self.assertIn("ch04_spar_wraith_defeated", enc["when"]["unset"])
        chapter = _json("game/data/flow/chapters/ch04.json")
        battles = []
        for zone in chapter["zones"].values():
            for beat in zone.get("beats", {}).values():
                battles += [s["battle"] for s in beat["steps"] if "battle" in s]
        self.assertEqual(sorted(battles), ["ch04_bottle_hermit", "ch04_sail_leeches", "ch04_spar_wraith"])
        self.assertEqual(chapter["zones"]["ch04/haluna_wake"].get("beats", {}).get("battle"), None)


class TurnPromptTest(unittest.TestCase):
    def test_turn_prompts_name_a_hero_and_come_in_pairs(self) -> None:
        heroes = {c["id"] for c in _json("game/data/battle/characters.json")["characters"]}
        rows = [e for e in _json("game/data/battle/encounters.json")["encounters"]
                if "turn_prompt_hero" in e or "turn_prompt_key" in e]
        self.assertTrue(rows, "Ch4's hermit lesson has one")
        for e in rows:
            self.assertIn(e.get("turn_prompt_hero"), heroes, e["id"])
            self.assertTrue(e.get("turn_prompt_key"), e["id"])


class GreyboxZoneTest(unittest.TestCase):
    def test_ch04_roots_resolve_to_their_layouts(self) -> None:
        for scene, layout in LAYOUTS.items():
            text = (ROOT / scene).read_text()
            self.assertEqual(cf.greybox_layout_path(text), "res://" + layout, scene)


if __name__ == "__main__":
    unittest.main()
