"""M2-ARC-04: a release export leaves game/levels/_tests/ out (export_presets.cfg exclude_filter), so nothing
the game ships may depend on it. A shipped file (one no release preset excludes) must not name a
res://game/levels/_tests/ path outside a comment, and shipped GDScript must not use a class_name defined under
_tests/. Run: python3 -m unittest discover -s tools/tests"""
import configparser
import fnmatch
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TESTS_PREFIX = "game/levels/_tests/"
TESTS_RES = "res://" + TESTS_PREFIX
SCANNED = {".gd", ".tscn", ".tres", ".json", ".godot", ".cfg", ".gdshader", ".gdshaderinc"}
# Shipped files that may still name a _tests path, and why it cannot break a release.
ALLOWED = {
    "game/data/settings/prewarm_materials.json":
        "the scenes lists are filters (warm a material when that scene loads); nothing is loaded from them",
    "game/data/world/locations.json":
        "the field_test location: only tests and the debug overlay route to it, and rows resolve lazily",
}


def _release_excludes() -> list[list[str]]:
    """The exclude patterns of every preset that leaves _tests out (the release presets)."""
    cfg = configparser.ConfigParser(interpolation=None, strict=False)
    cfg.read(ROOT / "export_presets.cfg", encoding="utf-8")
    out = []
    for section in cfg.sections():
        raw = cfg[section].get("exclude_filter")
        if raw is None:
            continue
        pats = [p.strip() for p in raw.strip('"').split(",") if p.strip()]
        if any(fnmatch.fnmatch(TESTS_PREFIX + "x.gd", p) for p in pats):
            out.append(pats)
    return out


def _shipped_files() -> list[str]:
    files = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    excludes = _release_excludes()
    shipped = []
    for f in files:
        if Path(f).suffix not in SCANNED or f.startswith(TESTS_PREFIX):
            continue
        if all(any(fnmatch.fnmatch(f, p) for p in pats) for pats in excludes):
            continue  # every release preset leaves it out
        shipped.append(f)
    return shipped


def _code(path: str, text: str) -> str:
    """The text without comments (GDScript '#', shader '//'); data files are kept whole."""
    suffix = Path(path).suffix
    if suffix == ".gd":
        return "\n".join(line.split("#", 1)[0] for line in text.splitlines())
    if suffix in {".gdshader", ".gdshaderinc"}:
        return "\n".join(line.split("//", 1)[0] for line in text.splitlines())
    return text


def _tests_classes() -> set[str]:
    names = set()
    for p in (ROOT / TESTS_PREFIX).rglob("*.gd"):
        m = re.search(r"^class_name\s+(\w+)", p.read_text(encoding="utf-8"), re.M)
        if m:
            names.add(m.group(1))
    return names


class ReleaseExcludesTestsTest(unittest.TestCase):
    def test_release_presets_leave_tests_out(self) -> None:
        self.assertTrue(_release_excludes(), "at least one export preset excludes game/levels/_tests/*")

    def test_no_shipped_file_names_a_tests_path(self) -> None:
        bad = []
        for f in _shipped_files():
            if f in ALLOWED:
                continue
            code = _code(f, (ROOT / f).read_text(encoding="utf-8", errors="replace"))
            if TESTS_RES in code:
                bad.append(f)
        self.assertEqual(bad, [], "shipped files that depend on game/levels/_tests/ (move the content out)")

    def test_no_shipped_script_uses_a_tests_class(self) -> None:
        classes = _tests_classes()
        bad = []
        for f in _shipped_files():
            if Path(f).suffix != ".gd":
                continue
            code = _code(f, (ROOT / f).read_text(encoding="utf-8"))
            for c in classes:
                if re.search(r"\b%s\b" % re.escape(c), code):
                    bad.append(f"{f}: {c}")
        self.assertEqual(bad, [], "shipped scripts that use a class defined under game/levels/_tests/")

    def test_the_allowlist_is_still_needed(self) -> None:
        for f in ALLOWED:
            self.assertIn(TESTS_RES, (ROOT / f).read_text(encoding="utf-8"), f"{f}: drop it from ALLOWED")


if __name__ == "__main__":
    unittest.main()
