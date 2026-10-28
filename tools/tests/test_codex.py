"""M3-UI-03: validate_data's lore codex checks. Run: python3 -m unittest discover -s tools/tests"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_data as vd  # noqa: E402

CATS = [{"id": "world", "name_key": "CW", "desc_key": "CWD"}]
GOOD = {"id": "a", "category": "world", "title_key": "T", "body_key": "B", "unlock": {"flag": "story"}}
FLAGS = {"story", "codex_a_read", "codex_r_read", "codex_r_found"}


def _doc(*entries: dict, cats: list | None = None) -> dict:
    return {"codex": {"categories": CATS if cats is None else cats, "entries": list(entries)}}


class CodexValidateTest(unittest.TestCase):
    def test_good_entries_pass_and_return_their_keys(self) -> None:
        record = {"id": "r", "category": "world", "title_key": "RT", "body_key": "RB", "unlock": {"record": True}}
        errs, keys = vd.codex_errors(_doc(GOOD, record), FLAGS)
        self.assertEqual(errs, [])
        self.assertEqual(keys, ["CW", "CWD", "T", "B", "RT", "RB"])

    def test_unknown_category_duplicate_id_and_bad_unlocks_fail(self) -> None:
        errs, _ = vd.codex_errors(
            _doc(
                dict(GOOD, category="nowhere"),
                GOOD,
                dict(GOOD, id="b", unlock={"when": "later"}),
                dict(GOOD, id="c", unlock={"always": "yes"}),
            ),
            FLAGS | {"codex_b_read", "codex_c_read"},
        )
        self.assertTrue(any("category 'nowhere'" in e for e in errs))
        self.assertTrue(any("duplicate entry id" in e for e in errs))
        self.assertTrue(any("'unlock' must be one of" in e for e in errs))
        self.assertTrue(any("take true" in e for e in errs))

    def test_undeclared_flags_fail_story_read_and_found(self) -> None:
        record = {"id": "r", "category": "world", "title_key": "RT", "body_key": "RB", "unlock": {"record": True}}
        errs, _ = vd.codex_errors(_doc(dict(GOOD, unlock={"flag": "nope"}), record), {"codex_a_read"})
        self.assertTrue(any("'nope' is not declared" in e for e in errs))
        self.assertTrue(any("'codex_r_read' is not declared" in e for e in errs))
        self.assertTrue(any("'codex_r_found' is not declared" in e for e in errs))

    def test_missing_keys_and_duplicate_categories_fail(self) -> None:
        errs, _ = vd.codex_errors(_doc(dict(GOOD, body_key=""), cats=CATS + [{"id": "world"}]), FLAGS)
        self.assertTrue(any("no body_key" in e for e in errs))
        self.assertTrue(any("duplicate category id" in e for e in errs))
        self.assertTrue(any("no name_key" in e for e in errs))

    def test_the_shipped_file_is_clean_and_its_keys_exist(self) -> None:
        root = Path(__file__).resolve().parents[2]
        doc = json.loads((root / vd.CODEX_FILE).read_text(encoding="utf-8"))
        errs, keys = vd.codex_errors(doc, vd.declared_flags_quiet(root))
        self.assertEqual(errs, [])
        loc = vd.load_loc_keys(root, vd.Report())
        self.assertEqual([k for k in keys if k not in loc], [])
        entries = doc["codex"]["entries"]
        self.assertGreaterEqual(len(entries), 32, "the starter set and Act I's entries (Narrative reviews them)")


if __name__ == "__main__":
    unittest.main()
