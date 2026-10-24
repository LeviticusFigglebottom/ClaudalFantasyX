"""A folder Godot is told to skip (.gdignore) commits no .import files (M2-RND-06).
Run: python3 -m unittest discover -s tools/tests

Godot never imports under a .gdignore, so a committed .import there is an orphan. One came back with a merge
(tests/fixtures/mote_metrics, bde9795) after M1-RND-23 had settled on the .gdignore.
"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GDIGNORE = ".gdignore"
IMPORT_SUFFIX = ".import"


def _tracked() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return out.splitlines()


class GdignoreImportsTest(unittest.TestCase):
    def test_no_import_files_under_a_gdignore(self) -> None:
        files = _tracked()
        ignored = [Path(f).parent for f in files if Path(f).name == GDIGNORE]
        self.assertTrue(ignored, "the repo has .gdignore folders to check")
        orphans = [
            f for f in files if f.endswith(IMPORT_SUFFIX) and any(d in Path(f).parents for d in ignored)
        ]
        self.assertEqual(orphans, [], "a .import under a .gdignore folder is an orphan: delete it")


if __name__ == "__main__":
    unittest.main()
