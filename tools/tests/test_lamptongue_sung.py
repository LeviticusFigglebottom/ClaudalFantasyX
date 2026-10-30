"""assets_src/music/act3/lamptongue.py (M5-A3P-1950, ADR 0208): the verses the Act III score sings are lamptongue.md's,
syllabled by its rules (every vowel sounded: o-an, a-un; ennu is en-nu; vey's y glides), and the Eighth Verse's lines
fit the Letting's notes. A changed verse text or rule fails here before a cue sings it wrong."""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for d in ("tools/audio", "assets_src/music", "assets_src/music/act3"):
    sys.path.insert(0, str(ROOT / d))


def _mod(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


LT = _mod("assets_src/music/act3/lamptongue.py", "lamptongue")
MOTIFS = _mod("assets_src/music/motifs.py", "motifs")


class LamptongueSungTest(unittest.TestCase):
    def test_the_verses_are_the_sheets(self) -> None:
        sheet = (ROOT / "docs/kb/audio/lamptongue.md").read_text()
        for verse, lines in LT.VERSES.items():
            self.assertEqual(len(lines), 4, f"verse {verse}: four lines")
            for line in lines:
                core = line.strip(".,")
                self.assertIn(core.lstrip("."), sheet, f"verse {verse}: '{line}' is lamptongue.md's")
            last = "tash" if verse == 8 else "mir"
            self.assertEqual(LT.words(lines[3]), [last], f"verse {verse} ends on {last}")

    def test_the_sheets_rules(self) -> None:
        self.assertEqual(LT.syllables("oan"), [("o", ""), ("a", "n")], "oan is o-an")
        self.assertEqual(LT.syllables("ennu"), [("e", "n"), ("u", "")], "ennu is en-nu, the n held")
        self.assertEqual(LT.syllables("aun"), [("a", ""), ("u", "n")], "every vowel sounded")
        self.assertEqual(LT.syllables("vey"), [("e", "")], "vey's y glides")
        self.assertEqual(len(LT.syllables("karra")), 2)

    def test_the_eighth_verse_fits_the_letting(self) -> None:
        sung = MOTIFS.letting_verse()
        for notes, text in zip(sung, LT.VERSES[8]):
            syl = LT.line_syllables(text)
            self.assertLessEqual(len(syl), len(notes), f"'{text}': a syllable a note at most")
            self.assertEqual(len(LT.fit(notes, syl)), len(notes))
        self.assertEqual(LT.line_syllables(LT.VERSES[8][3]), [("a", "")], "the held E6 is sung on tash's a")

    def test_no_letter_is_lost(self) -> None:
        for lines in LT.VERSES.values():
            for line in lines:
                for w in LT.words(line):
                    vowels = len(re.findall(r"[aeiou]", w))
                    self.assertEqual(len(LT.syllables(w)), vowels, f"{w}: one syllable a vowel")


if __name__ == "__main__":
    unittest.main()
