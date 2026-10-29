"""Localization readiness guard (the Lead's sweep, 2026-10-27; CLAUDE.md §3: every player-facing string goes
through a loc key). Fails on:
- a literal player-facing string in game code or scenes (a `.text`, tooltip or placeholder set to words, a
  set_help("words"), or a row's label/title/desc/text/right given as words);
- a tr("KEY") or TranslationServer.translate("KEY") whose key has no loc row;
- a `const ...KEY... := "KEY"` with no loc row (a key prefix ending in "_" is built on, not looked up).
Test scenes under game/levels/_tests/ are left out. KNOWN lists findings filed with their owner, by
"path:needle"; delete a row when it is fixed.
"""
from __future__ import annotations

import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAME = ROOT / "game"
LOC_DIR = ROOT / "game" / "data" / "loc"
KNOWN: dict[str, str] = {}

WORDS = r'[^"]*[a-z]{2,}[^"]*'
GD_LITERALS = [
    re.compile(r'\.(?:text|tooltip_text|placeholder_text)\s*=\s*"(' + WORDS + ')"'),
    re.compile(r'set_help\(\s*"(' + WORDS + ')"'),
    re.compile(r'"(?:label|title|right|desc|text)"\s*:\s*"(' + WORDS + ')"'),
]
TSCN_LITERAL = re.compile(r'^(?:text|tooltip_text|placeholder_text) = "(' + WORDS + ')"', re.M)
TR_CALL = re.compile(r'\b(?:tr|TranslationServer\.translate)\(\s*"([A-Z][A-Z0-9_]*)"')
KEY_CONST = re.compile(r'^const \w*KEY\w*\s*:?=\s*"([A-Z][A-Z0-9_]*)"', re.M)


def loc_keys() -> set[str]:
    keys: set[str] = set()
    for p in LOC_DIR.glob("*.csv"):
        with p.open(encoding="utf-8", newline="") as f:
            keys.update(row[0] for row in csv.reader(f) if row)
    return keys


def sources(suffix: str) -> list[Path]:
    return [p for p in GAME.rglob(f"*{suffix}") if "_tests" not in p.parts]


def literal_findings() -> list[str]:
    out: list[str] = []
    for p in sources(".gd"):
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            for pat in GD_LITERALS:
                out += [f"{p.relative_to(ROOT)}:{i}: \"{m.group(1)}\"" for m in pat.finditer(line)]
    for p in sources(".tscn"):
        out += [f"{p.relative_to(ROOT)}: \"{m.group(1)}\"" for m in TSCN_LITERAL.finditer(p.read_text(encoding="utf-8"))]
    return [f for f in out if not any(k in f for k in KNOWN)]


def missing_key_findings(keys: set[str]) -> list[str]:
    out: list[str] = []
    for p in sources(".gd"):
        text = p.read_text(encoding="utf-8")
        for pat in (TR_CALL, KEY_CONST):
            for m in pat.finditer(text):
                key = m.group(1)
                if not key.endswith("_") and key not in keys:
                    out.append(f"{p.relative_to(ROOT)}: {key}")
    return [f for f in out if not any(k in f for k in KNOWN)]


class LocReadinessTest(unittest.TestCase):
    def test_no_player_facing_string_is_written_into_code_or_scenes(self) -> None:
        self.assertEqual(literal_findings(), [], "put the words in a loc csv and use the key")

    def test_every_key_the_code_names_has_a_loc_row(self) -> None:
        self.assertEqual(missing_key_findings(loc_keys()), [])

    def test_the_patterns_catch_what_they_should(self) -> None:
        self.assertTrue(GD_LITERALS[0].search('\tlabel.text = "Hello there"'))
        self.assertFalse(GD_LITERALS[0].search('\tlabel.text = tr("HELLO")'))
        self.assertFalse(GD_LITERALS[0].search('\tlabel.text = "%d / %d" % [a, b]'), "no words, no finding")
        self.assertTrue(GD_LITERALS[2].search('{"id": &"go", "label": "Go now"}'))
        self.assertTrue(TSCN_LITERAL.search('text = "Start"\n'))
        self.assertEqual(TR_CALL.findall('tr("SOME_KEY") + TranslationServer.translate("OTHER")'),
                         ["SOME_KEY", "OTHER"])
        self.assertEqual(KEY_CONST.findall('const TITLE_KEY := "A_TITLE"\nconst X := "NOPE"'), ["A_TITLE"])


if __name__ == "__main__":
    unittest.main()
