"""The banned-terms scan in tools/validate_data.py (SPEC §2; M2-NIT-06). Run: python3 -m unittest discover -s tools/tests
check_banned prefilters each file with one combined regex. These tests pin that it reports exactly what the
original per-line, per-term scan reported, on a small fixture tree with seeded violations."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import validate_data as vd  # noqa: E402


def reference_check_banned(root: Path) -> list[str]:
    """The scan as it was before M2-NIT-06: every term against every line of every scanned file."""
    rep = vd.Report()
    pats = vd.load_banned(root)
    for entry in vd.BANNED_SCAN:
        base = root / entry
        files = [base] if base.is_file() else (sorted(base.rglob("*")) if base.exists() else [])
        for p in files:
            if not p.is_file() or p.suffix not in vd.BANNED_SCAN_EXT:
                continue
            for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                for pat in pats:
                    m = pat.search(line)
                    if m:
                        rep.err(f"{p.relative_to(root)}:{n}: banned term '{m.group(0)}' (SPEC §2)")
    return rep.errors


class BannedScanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="banned_scan_"))
        (self.tmp / "tools").mkdir()
        shutil.copy(ROOT / "tools" / "banned_terms.txt", self.tmp / "tools" / "banned_terms.txt")
        for d in ("game/core", "game/data", "assets_src/x", "docs/kb/story"):
            (self.tmp / d).mkdir(parents=True)
        (self.tmp / "docs/kb/glossary.md").write_text("Undertow: the sea beneath the sea.\n")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def write(self, rel: str, text: str) -> None:
        (self.tmp / rel).write_bytes(text.encode("utf-8"))

    def errors(self) -> list[str]:
        rep = vd.Report()
        vd.check_banned(self.tmp, rep)
        self.assertEqual(rep.errors, reference_check_banned(self.tmp), "the fast scan disagrees with the reference")
        return rep.errors

    def test_clean_tree_is_clean(self) -> None:
        self.write("game/core/ok.gd", "func f() -> void:\n\tpass  # Sinew and Lucas, a pyrefly_count, Spiral\n")
        self.assertEqual(self.errors(), [])

    def test_seeded_terms_in_gd_md_and_json_are_caught(self) -> None:
        self.write("game/core/bad.gd", "extends Node\n# the Zanarkand road\n")
        self.write("docs/kb/story/beat.md", "# Beat\n\nThe aeon wakes.\n")
        self.write("assets_src/x/meta.json", '{"name": "Spira"}\n')
        errs = self.errors()
        self.assertIn("game/core/bad.gd:2: banned term 'Zanarkand' (SPEC §2)", errs)
        self.assertIn("docs/kb/story/beat.md:3: banned term 'aeon' (SPEC §2)", errs)
        self.assertIn("assets_src/x/meta.json:1: banned term 'Spira' (SPEC §2)", errs)
        self.assertEqual(len(errs), 3)

    def test_binary_and_unscanned_extensions_are_ignored(self) -> None:
        for name in ("tex.png", "mesh.glb", "cue.ogg", "clip.wav", "thing.res", "tex.png.import"):
            self.write(f"game/data/{name}", "Spira Zanarkand aeon\n")
        self.write("docs/kb/other.md", "Spira\n")  # outside BANNED_SCAN
        self.assertEqual(self.errors(), [])

    def test_case_flags_whole_words_and_line_numbers(self) -> None:
        self.write("game/data/loc.csv", "keys,en\nA,The AEON of Spira\nB,spira is fine\nC,Aeons\r\nD,x_Spira Spira_x\n"
                   "E,(Spira) and 'Blitzball'—Sin.\n")
        self.assertEqual(self.errors(), [
            "game/data/loc.csv:2: banned term 'Spira' (SPEC §2)",
            "game/data/loc.csv:2: banned term 'AEON' (SPEC §2)",
            "game/data/loc.csv:4: banned term 'Aeons' (SPEC §2)",
            "game/data/loc.csv:6: banned term 'Spira' (SPEC §2)",
            "game/data/loc.csv:6: banned term 'Sin' (SPEC §2)",
            "game/data/loc.csv:6: banned term 'Blitzball' (SPEC §2)",
        ])

    def test_unicode_line_breaks_and_neighbours_agree_with_the_reference(self) -> None:
        self.write("game/data/odd.txt", "éSpira Spiraé\x0cSpira\x85Sin x\tSIN\nfaÿth fayth\n")
        self.write("game/data/bad_utf8.dlg", "")
        (self.tmp / "game/data/bad_utf8.dlg").write_bytes(b"\xff\xfeSpira\n")
        errs = self.errors()
        self.assertIn("game/data/odd.txt:3: banned term 'Spira' (SPEC §2)", errs)
        self.assertIn("game/data/bad_utf8.dlg:1: banned term 'Spira' (SPEC §2)", errs)

    def test_single_file_entry_is_scanned(self) -> None:
        self.write("docs/kb/glossary.md", "Undertow\nBesaid\n")
        self.assertEqual(self.errors(), ["docs/kb/glossary.md:2: banned term 'Besaid' (SPEC §2)"])

    def test_combined_pattern_matches_where_any_term_matches(self) -> None:
        any_pat, pats = vd.banned_any(ROOT), vd.load_banned(ROOT)
        for term, _ in vd.load_banned_terms(ROOT):
            for text in (term, f" {term}.", term.upper(), term.lower(), f"x{term}", f"{term}9", term[:-1]):
                self.assertEqual(bool(any_pat.search(text)), any(p.search(text) for p in pats), text)


if __name__ == "__main__":
    unittest.main()
