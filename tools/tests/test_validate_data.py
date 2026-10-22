"""Unit tests for tools/validate_data.py. Run: python3 -m unittest discover -s tools/tests"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        for rel in ("game", "assets", "tools/banned_terms.txt", "docs/kb/glossary.md"):
            src = ROOT / rel
            dst = self.tmp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dst)
            elif src.exists():
                shutil.copy(src, dst)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def errors(self) -> list[str]:
        return vd.run(self.tmp).errors

    def test_repo_data_is_clean(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_undeclared_flag_is_caught(self) -> None:
        (self.tmp / "game" / "core" / "bad.gd").write_text('func f():\n\tGame.set_flag(&"nope_flag")\n')
        self.assertTrue(any("undeclared story flag 'nope_flag'" in e for e in self.errors()))

    def test_dialogue_flag_is_caught(self) -> None:
        (self.tmp / "game" / "data" / "dialogue" / "x.dlg").write_text("<<if $ghost_flag>>\n")
        self.assertTrue(any("ghost_flag" in e for e in self.errors()))

    def test_missing_provenance_is_caught(self) -> None:
        (self.tmp / "assets" / "orphan.txt").write_text("x")
        self.assertTrue(any("orphan.txt: no entry" in e for e in self.errors()))

    def test_banned_term_is_caught(self) -> None:
        (self.tmp / "game" / "data" / "loc" / "extra.csv").write_text("keys,en\nX_TERM,The Blitzball cup\n")
        self.assertTrue(any("banned term" in e for e in self.errors()))

    def test_banned_term_is_whole_word(self) -> None:
        (self.tmp / "game" / "data" / "loc" / "extra.csv").write_text("keys,en\nX_TERM,Sinew and Lucas\n")
        self.assertFalse(any("banned term" in e for e in self.errors()))

    def test_dangling_skill_reference_is_caught(self) -> None:
        p = self.tmp / "game" / "data" / "battle" / "characters.json"
        p.write_text(p.read_text().replace('"quick_hit"', '"no_such_skill"', 1))
        self.assertTrue(any("unknown skill 'no_such_skill'" in e for e in self.errors()))

    def test_missing_loc_key_is_caught(self) -> None:
        p = self.tmp / "game" / "data" / "loc" / "strings.csv"
        p.write_text("\n".join(l for l in p.read_text().splitlines() if not l.startswith("SKILL_EMBER,")) + "\n")
        self.assertTrue(any("SKILL_EMBER" in e for e in self.errors()))


if __name__ == "__main__":
    unittest.main()
