"""M2-FP-120: game/data/cutscene/glimmer_forms.json is what tools/cutscene/glimmer_forms.py makes."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class GlimmerFormsTest(unittest.TestCase):
    def test_forms_are_current(self):
        r = subprocess.run([sys.executable, str(ROOT / "tools/cutscene/glimmer_forms.py"), "--check"],
                           capture_output=True, text=True, check=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
