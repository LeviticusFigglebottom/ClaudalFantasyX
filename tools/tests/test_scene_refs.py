"""Every res:// path a scene or resource file loads exists. A renamed asset otherwise leaves a scene that still loads,
with the instance silently missing (the First Verse lost its offerings to env-art's shrine_offering rename)."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROOTS = ("game", "assets")
PATH = re.compile(r'path="res://([^"]+)"')


class SceneRefsTest(unittest.TestCase):
    def test_every_loaded_path_exists(self):
        missing = []
        for top in ROOTS:
            for f in (ROOT / top).rglob("*"):
                if f.suffix not in (".tscn", ".tres"):
                    continue
                for m in PATH.finditer(f.read_text(errors="ignore")):
                    if not (ROOT / m.group(1)).exists():
                        missing.append(f"{f.relative_to(ROOT)} -> res://{m.group(1)}")
        self.assertEqual(missing, [], "\n".join(missing))


if __name__ == "__main__":
    unittest.main()
