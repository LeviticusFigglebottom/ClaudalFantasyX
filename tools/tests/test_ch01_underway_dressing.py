"""M3-C01-101: the Underway's kit dressing and its copied grade are generated from env-art's kit and kept in sync."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class UnderwayDressingTest(unittest.TestCase):
    def test_generated_files_are_up_to_date(self):
        run = subprocess.run(
            [sys.executable, str(ROOT / "tools/ch01/ch01_underway_dressing.py"), "--check"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
