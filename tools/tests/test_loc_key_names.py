"""Controller and keyboard prompt audit (ui-menus, 2026-10-27): no player-facing string hard-codes a key or a
pad button; bindings are named through {action} placeholders (InputNames.fill), so they follow rebinding and
the last device used. Device-neutral action words (Confirm, Cancel, Up and Down) are fine.
Run: python3 -m unittest discover -s tools/tests"""
import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# "Press F", "hold E", "(Escape)", "Tab", "Enter", "Space"... a key named in the text.
KEY_NAME = re.compile(
    r"\b(?:[Pp]ress|[Hh]old)\s+(?:[A-Z]\b|F\d+\b)|\((?:Escape|Esc|Tab|Enter|Space|Shift|Ctrl)\)"
    r"|\b(?:Tab|Enter|Spacebar|Space bar|Backspace)\b"
)
# Known gaps with their own task (the controls page's "(Escape: cancel)" lines name the hard-wired listen cancel
# and do not match).
ALLOWED = {
    "DLG_CH01_TUT_003": "M2-FP-30 (cinematics): the Ch1 tutorial lines move to {action} names",
}


def _rows():
    for path in sorted((ROOT / "game" / "data" / "loc").glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as f:
            for row in csv.reader(f):
                if len(row) >= 2 and row[0] != "keys":
                    yield path.name, row[0], row[1]


class LocKeyNamesTest(unittest.TestCase):
    def test_no_string_hard_codes_a_key(self) -> None:
        bad = [
            f"{name}: {key}: {text[:80]}" for name, key, text in _rows() if key not in ALLOWED and KEY_NAME.search(text)
        ]
        self.assertEqual(bad, [], "name bindings with {action} placeholders (InputNames.fill)")

    def test_the_allow_list_is_still_needed(self) -> None:
        texts = {key: text for _, key, text in _rows()}
        stale = [k for k in ALLOWED if k not in texts or not KEY_NAME.search(texts[k])]
        self.assertEqual(stale, [], "drop allow-list rows once their strings are fixed")


if __name__ == "__main__":
    unittest.main()
