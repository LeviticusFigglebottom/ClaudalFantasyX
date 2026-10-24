"""M3-MNU-02: validate_data's Memories gallery checks. Run: python3 -m unittest discover -s tools/tests"""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_data as vd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CHAPTERS = [{"id": "ch02", "name_key": "CH2"}]
GOOD = {
    "id": "beach",
    "chapter": "ch02",
    "scene": "ch02_girl_on_the_beach",
    "stage": "res://game/levels/ch02/haluna/haluna.tscn",
    "title_key": "T",
    "unlock_flag": "ch02_met_asha",
}
FLAGS = {"ch02_met_asha", "ch02_heard_pila"}


def _doc(*memories: dict, chapters: list | None = None) -> dict:
    return {"chapters": CHAPTERS if chapters is None else chapters, "memories": list(memories)}


class MemoriesValidateTest(unittest.TestCase):
    def test_good_memories_pass_and_return_their_keys(self) -> None:
        night = dict(GOOD, id="night", night=True, spawn="DockNight", replay_flags={"ch02_heard_pila": False})
        errs, keys = vd.memories_errors(_doc(GOOD, night), FLAGS, ROOT)
        self.assertEqual(errs, [])
        self.assertEqual(keys, ["CH2", "T", "T"])

    def test_a_missing_scene_or_stage_fails(self) -> None:
        errs, _ = vd.memories_errors(
            _doc(dict(GOOD, scene="no_such_scene"), dict(GOOD, id="b", stage="res://nowhere.tscn")), FLAGS, ROOT
        )
        self.assertTrue(any("'no_such_scene' has no compiled dialogue" in e for e in errs))
        self.assertTrue(any("'res://nowhere.tscn' is not a res:// scene" in e for e in errs))

    def test_undeclared_unlock_and_replay_flags_fail(self) -> None:
        errs, _ = vd.memories_errors(
            _doc(dict(GOOD, unlock_flag="nope"), dict(GOOD, id="b", replay_flags={"never": False})), FLAGS, ROOT
        )
        self.assertTrue(any("unlock_flag 'nope' is not declared" in e for e in errs))
        self.assertTrue(any("replay flag 'never' is not declared" in e for e in errs))

    def test_duplicates_unknown_chapters_keys_and_types_fail(self) -> None:
        errs, _ = vd.memories_errors(
            _doc(
                GOOD,
                GOOD,
                dict(GOOD, id="c", chapter="ch99"),
                dict(GOOD, id="d", title_key=""),
                dict(GOOD, id="e", night="yes"),
                dict(GOOD, id="Bad Id"),
                chapters=CHAPTERS + [{"id": "ch02"}],
            ),
            FLAGS,
            ROOT,
        )
        self.assertTrue(any("duplicate memory id" in e for e in errs))
        self.assertTrue(any("duplicate chapter id" in e for e in errs))
        self.assertTrue(any("no name_key" in e for e in errs))
        self.assertTrue(any("chapter 'ch99'" in e for e in errs))
        self.assertTrue(any("no title_key" in e for e in errs))
        self.assertTrue(any("'night' must be a bool" in e for e in errs))
        self.assertTrue(any("id must be snake_case" in e for e in errs))

    def test_an_empty_gallery_fails(self) -> None:
        errs, _ = vd.memories_errors(_doc(), FLAGS, ROOT)
        self.assertTrue(any("non-empty list" in e for e in errs))

    def test_the_shipped_gallery_is_clean_and_checked_by_run(self) -> None:
        doc = json.loads((ROOT / vd.MEMORIES_FILE).read_text(encoding="utf-8"))
        errs, keys = vd.memories_errors(doc, vd.declared_flags_quiet(ROOT), ROOT)
        self.assertEqual(errs, [])
        loc = vd.load_loc_keys(ROOT, vd.Report())
        self.assertEqual([k for k in keys if k not in loc], [])
        broken = copy.deepcopy(doc)
        broken["memories"][0]["unlock_flag"] = "not_a_flag"
        files = {vd.MEMORIES_FILE: broken}
        rep = vd.Report()
        vd.check_memories(ROOT, files, vd.declared_flags_quiet(ROOT), rep)
        self.assertTrue(any("not_a_flag" in e for e in rep.errors))


if __name__ == "__main__":
    unittest.main()
