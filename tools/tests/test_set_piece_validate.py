"""Set-piece checks in tools/validate_data.py and the Ch8 suites in targets.json (M3-CMB-01,
docs/kb/design/set_piece_battles.md). Run: python3 -m unittest discover -s tools/tests"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

SKILLS = [
    {"id": "climb"}, {"id": "rise", "summon": "mite"}, {"id": "blow"},
    {"id": "grip", "target": "ward", "delay_ranks": 2, "on_cover": "blow"},
    {"id": "hold", "target": "self", "covers": "ward"},
    {"id": "firm", "target": "self", "counter": "blow"},
    {"id": "call", "target": "single_foe", "withdraws": True, "spares_tag": "rooted"},
    {"id": "breach", "target": "all_foes", "pushes_ward": 3},
]
BOSS = {
    "id": "boss", "hp_floor_pct": 30,
    "phases": [
        {"id": "dark", "at_hp_pct": 60, "field": "dark", "spawn_bound": True, "spawn": ["mite"],
         "field_rules": [{"on": "party", "status": "darkness", "duration": 2}, {"on": "ward", "status": "slow"}]},
        {"id": "breach", "at_hp_pct": 30, "untargetable": True, "damage_immune": True},
    ],
}
MITE = {"id": "mite"}
CLIMB = {"id": "the_climb", "name_key": "K_CLIMB", "side": "party", "role": "ward", "agility": 4,
         "skills": ["climb"], "ai": [{"pick": [{"skill": "climb", "target": "self"}]}]}
SURGE = {"id": "the_surge", "name_key": "K_SURGE", "side": "enemy", "role": "tide", "agility": 10, "delay_immune": True,
         "summon_cap": 2, "joins_at_phase": "breach", "skills": ["rise"],
         "ai": [{"pick": [{"skill": "rise", "target": "self"}]}]}
ENC = {
    "id": "reach", "enemies": ["boss"], "entries": [CLIMB, SURGE],
    "objective": {"ward": "the_climb", "quota": 2, "from_phase": "breach", "outcome": "scripted_escape"},
    "locked_active": ["toma"], "locked_key": "K_LOCK", "unavailable": ["kerrid"], "unavailable_key": "K_GONE",
    "attack_override": {"toma": "firm"},
}
CHARS = {"toma", "kerrid", "liss"}
STATUSES = {"darkness", "slow", "haste"}


def errors(skills=None, enemies=None, encounters=None):
    return vd.set_piece_errors(skills if skills is not None else SKILLS,
                               enemies if enemies is not None else [BOSS, MITE],
                               encounters if encounters is not None else [ENC], CHARS, STATUSES)


class SetPieceValidateTest(unittest.TestCase):
    def test_the_fixture_is_clean(self):
        self.assertEqual(errors(), [])

    def test_the_shipped_tables_are_clean(self):
        rep = vd.run(ROOT)
        self.assertEqual([e for e in rep.errors if "entries" in e or "objective" in e or "set" in e.lower()], [])

    def test_entries_need_a_role_side_pace_and_known_skills(self):
        enc = copy.deepcopy(ENC)
        enc["entries"][0].update({"role": "boss", "side": "middle", "agility": 0, "skills": ["fly"], "bogus": 1})
        errs = errors(encounters=[enc])
        for frag in ("role must be", "side must be", "agility must be", "unknown skill 'fly'", "unknown key 'bogus'"):
            self.assertTrue(any(frag in e for e in errs), frag)

    def test_an_entry_id_must_not_shadow_a_combatant(self):
        enc = copy.deepcopy(ENC)
        enc["entries"][0]["id"] = "toma"
        self.assertTrue(any("must not be a hero or enemy id" in e for e in errors(encounters=[enc])))

    def test_the_objective_names_the_ward_and_a_known_phase(self):
        enc = copy.deepcopy(ENC)
        enc["objective"] = {"ward": "the_surge", "quota": 2}
        self.assertTrue(any("objective.ward" in e for e in errors(encounters=[enc])))
        enc["objective"] = {"ward": "the_climb", "quota": 0, "outcome": "escaped", "from_phase": "nowhere"}
        errs = errors(encounters=[enc])
        for frag in ("quota", "outcome", "from_phase"):
            self.assertTrue(any(f"objective.{frag}" in e for e in errs), frag)

    def test_a_late_entry_joins_at_a_real_phase(self):
        enc = copy.deepcopy(ENC)
        enc["entries"][1]["joins_at_phase"] = "never"
        self.assertTrue(any("joins_at_phase" in e for e in errors(encounters=[enc])))

    def test_party_rules_name_heroes_and_give_a_reason(self):
        enc = copy.deepcopy(ENC)
        enc.update({"locked_active": ["nobody"], "unavailable": ["kerrid"], "attack_override": {"toma": "none"}})
        del enc["unavailable_key"]
        errs = errors(encounters=[enc])
        self.assertTrue(any("locked_active must list hero ids" in e for e in errs))
        self.assertTrue(any("needs unavailable_key" in e for e in errs))
        self.assertTrue(any("attack_override" in e for e in errs))
        enc = copy.deepcopy(ENC)
        enc["unavailable"] = ["toma"]
        self.assertTrue(any("both locked_active and unavailable" in e for e in errors(encounters=[enc])))

    def test_set_piece_skill_keys(self):
        bad = [{"id": "x", "target": "single_foe", "covers": "climb", "counter": "nope", "on_cover": "blow",
                "withdraws": "yes", "spares_tag": "", "pushes_ward": 0}]
        errs = errors(skills=SKILLS + bad)
        for frag in ("covers must be", "counter names unknown", "on_cover only applies", "withdraws must",
                     "spares_tag must", "pushes_ward must"):
            self.assertTrue(any(frag in e for e in errs), frag)

    def test_phase_keys_and_field_rules(self):
        boss = copy.deepcopy(BOSS)
        boss["hp_floor_pct"] = 100
        boss["phases"][0]["field_rules"] = [{"on": "everyone", "status": "darkness"}, {"on": "party", "status": "slow",
                                                                                      "duration": 0}]
        boss["phases"][1]["untargetable"] = "yes"
        boss["phases"][1]["field_rules"] = [{"on": "party", "status": "slow"}]
        errs = errors(enemies=[boss, MITE])
        for frag in ("hp_floor_pct", "a field rule needs on", "duration must", "untargetable must",
                     "field_rules need the phase's field"):
            self.assertTrue(any(frag in e for e in errs), frag)

    def test_the_vocabulary_knows_the_ward(self):
        self.assertIn("ward", vd.SKILL_ONLY_TARGETS)
        self.assertNotIn("ward", vd.SKILL_TARGETS, "items keep their own targets")
        self.assertIn("ward", vd.AI_TARGETS)
        self.assertIn("ward_has_status", vd.AI_CONDITIONS)
        self.assertTrue(vd._ai_arg_ok("ward_has_status", "haste", {"haste"}))
        self.assertFalse(vd._ai_arg_ok("ward_has_status", "glow", {"haste"}))
        self.assertTrue({"untargetable", "damage_immune", "spawn_bound", "field_rules"} <= vd.BOSS_PHASE_KEYS)

    def test_entry_and_rule_keys_reach_the_loc_check(self):
        files = {f"game/data/battle/{t}.json": {t: rows} for t, rows in (
            ("skills", SKILLS), ("enemies", [BOSS, MITE]), ("encounters", [ENC]),
            ("characters", [{"id": c} for c in CHARS]), ("statuses", [{"id": s} for s in STATUSES]))}
        rep = vd.Report()
        keys = vd.check_set_pieces(files, rep)
        self.assertEqual(rep.errors, [])
        self.assertEqual(sorted(keys), ["K_CLIMB", "K_GONE", "K_LOCK", "K_SURGE"])


class Ch8SuitesTest(unittest.TestCase):
    def setUp(self):
        self.suites = {s["id"]: s for s in json.loads((ROOT / "tools/balance/targets.json").read_text())["suites"]}

    def test_the_waves_and_the_reach_carry_the_tasks_bands(self):
        for sid in ("ch08_stair_hold_1", "ch08_stair_hold_2", "ch08_stair_hold_3"):
            self.assertEqual(self.suites[sid]["bands"]["role_answer"], [85, 95], sid)
            self.assertEqual(self.suites[sid]["kind"], "set_piece")
        reach = self.suites["ch08_undertows_reach"]
        self.assertEqual(reach["bands"]["role_answer"], [75, 85])
        self.assertLessEqual(reach["bands"]["naive"][1], 10)
        self.assertEqual(reach["encounter"], "undertows_reach")

    def test_kerrid_is_in_no_ch8_suite_and_the_ward_guard_is_reported(self):
        for sid, s in self.suites.items():
            if sid.startswith("ch08_"):
                self.assertNotIn("kerrid", s["active"] + s["reserve"], sid)
                self.assertIn("ward_guard", s["bands"], sid)
                self.assertIsNone(s["bands"]["ward_guard"], f"{sid}: report only")


if __name__ == "__main__":
    unittest.main()
