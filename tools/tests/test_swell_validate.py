"""Swell checks in tools/validate_data.py (M1-CMB-04, formulas.md § Swell).
Run: python3 -m unittest discover -s tools/tests"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402

RING = {"id": "ring", "kind": "timing_ring", "beats": 3, "lead_in_sec": 0.6, "beat_sec": 0.8, "peak_at": 0.7,
        "perfect_sec": 0.06, "good_sec": 0.15, "max_step_sec": 0.05, "grades": {"perfect": 30, "good": 15, "miss": 0}}


def _mode(mid: str, trigger: str, unlocked: bool = True, **num: int) -> dict:
    row = {"id": mid, "name_key": "K", "desc_key": "K", "trigger": trigger, "starts_unlocked": unlocked}
    row.update(num or {"rate": 100})
    return row


DOC = {"swell": {
    "default_mode": "a",
    "modes": [_mode("a", "damage_taken"), _mode("b", "damage_dealt"), _mode("c", "heal_item", False, flat=20)],
    "inputs": [RING],
    "heroes": [{"id": "rhen", "input": "ring", "techniques": ["dive"]}],
}}
SKILLS = {"dive": {"id": "dive", "swell": True}, "attack": {"id": "attack"}}
CHARS = {"rhen", "asha"}


class SwellValidateTests(unittest.TestCase):
    def errs(self, doc: object, skills: dict | None = None) -> list[str]:
        return vd.swell_errors(doc, SKILLS if skills is None else skills, CHARS)

    def doc(self) -> dict:
        return copy.deepcopy(DOC)

    def test_clean_doc(self) -> None:
        self.assertEqual(self.errs(DOC), [])

    def test_repo_file_is_clean(self) -> None:
        doc = json.loads((ROOT / vd.SWELL_FILE).read_text())
        sk = json.loads((ROOT / "game/data/battle/skills.json").read_text())["skills"]
        chars = json.loads((ROOT / "game/data/battle/characters.json").read_text())["characters"]
        self.assertEqual(vd.swell_errors(doc, {r["id"]: r for r in sk}, {c["id"] for c in chars}), [])

    def test_missing_root(self) -> None:
        self.assertIn("missing top-level object", self.errs({})[0])
        self.assertIn("missing top-level object", self.errs([])[0])

    def test_needs_three_modes(self) -> None:
        d = self.doc()
        d["swell"]["modes"].pop()
        self.assertTrue(any("at least 3 fill modes" in e for e in self.errs(d)))

    def test_mode_fields(self) -> None:
        d = self.doc()
        m = d["swell"]["modes"][1]
        m["trigger"] = "sneezing"
        m["flat"] = 5
        m["starts_unlocked"] = "yes"
        del m["desc_key"]
        d["swell"]["modes"][2]["flat"] = 0
        e = self.errs(d)
        for want in ("trigger must be one of", "exactly one of 'rate' or 'flat'", "starts_unlocked",
                     "missing desc_key", "'flat' must be a positive int"):
            self.assertTrue(any(want in x for x in e), want)

    def test_default_mode_must_exist_and_start_unlocked(self) -> None:
        d = self.doc()
        d["swell"]["default_mode"] = "zzz"
        self.assertTrue(any("is not a mode" in e for e in self.errs(d)))
        d["swell"]["default_mode"] = "c"
        self.assertTrue(any("must start unlocked" in e for e in self.errs(d)))

    def test_input_fields(self) -> None:
        d = self.doc()
        r = d["swell"]["inputs"][0]
        r["beats"] = 0
        r["beat_sec"] = -1
        r["peak_at"] = 1.0
        r["perfect_sec"] = 0.5
        r["grades"] = {"perfect": 30, "good": 15}
        e = self.errs(d)
        for want in ("beats must be a positive int", "'beat_sec' must be a number", "peak_at must be a fraction",
                     "perfect_sec must not exceed good_sec", "grades must give perfect, good and miss"):
            self.assertTrue(any(want in x for x in e), want)
        r["grades"] = {"perfect": -1, "good": 15, "miss": True}
        self.assertTrue(any("grade bonuses must be ints" in x for x in self.errs(d)))
        r["kind"] = "kazoo"
        self.assertTrue(any("kind must be one of" in x for x in self.errs(d)))

    def test_ring_windows_fit_their_beat_and_the_input_stays_short(self) -> None:  # M1-UI-05
        d = self.doc()
        r = d["swell"]["inputs"][0]
        r["peak_at"] = 0.9  # 0.72 + 0.15 = 0.87 > 0.8: a late press would land on the next beat
        self.assertTrue(any("good window ends after its beat" in x for x in self.errs(d)))
        r["peak_at"] = 0.1  # 0.08 - 0.15 < 0: an early press is ignored before the beat opens
        self.assertTrue(any("good window starts before its beat opens" in x for x in self.errs(d)))
        r["peak_at"] = 0.7
        r["beats"] = 6  # 0.6 + 6 x 0.8 = 5.4 s
        self.assertTrue(any("keep it at most" in x for x in self.errs(d)))
        r["beats"] = 3
        self.assertEqual(self.errs(d), [])
        for bad in (None, 0, 0.07, True):
            r["max_step_sec"] = bad
            self.assertTrue(any("max_step_sec must be" in x for x in self.errs(d)), bad)
        r["max_step_sec"] = 0.06  # == perfect_sec is allowed
        self.assertEqual(self.errs(d), [])

    def test_hero_references(self) -> None:
        d = self.doc()
        d["swell"]["heroes"] = [
            {"id": "nobody", "input": "harp", "techniques": ["dive"]},
            {"id": "asha", "input": "ring", "techniques": ["dive", "attack", "ghost"]},
            {"id": "rhen", "input": "ring", "techniques": []},
        ]
        e = self.errs(d)
        for want in ("heroes.nobody: not a character", "unknown input 'harp'", "already belongs to nobody",
                     "'attack' must be a skills.json row with swell: true", "'ghost' is not a skill",
                     "heroes.rhen: needs at least one technique"):
            self.assertTrue(any(want in x for x in e), want)

    def test_an_unlisted_swell_row_is_caught(self) -> None:
        skills = dict(SKILLS, orphan={"id": "orphan", "swell": True})
        self.assertTrue(any("skills.orphan: a Swell row that no hero" in e for e in self.errs(DOC, skills)))

    def test_check_swell_reports_learned_techniques_and_returns_keys(self) -> None:
        files = {
            vd.SWELL_FILE: DOC,
            "game/data/battle/skills.json": {"skills": list(SKILLS.values())},
            "game/data/battle/characters.json": {"characters": [{"id": "rhen", "skills": ["attack", "dive"]},
                                                                {"id": "asha"}]},
            "game/data/battle/enemies.json": {"enemies": [{"id": "crab", "skills": ["attack"]}]},
        }
        rep = vd.Report()
        keys = vd.check_swell(files, rep)
        self.assertTrue(any("skills.dive: a Swell technique is never learned" in e for e in rep.errors))
        self.assertIn("K", keys)
        rep = vd.Report()
        self.assertEqual(vd.check_swell({}, rep), [])
        self.assertTrue(any("missing" in e for e in rep.errors))


if __name__ == "__main__":
    unittest.main()
