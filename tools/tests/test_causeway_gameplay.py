"""M2-FP-108: the causeway's gameplay layout and wildlife are generated from env-art's route and kept in sync."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class CausewayGameplayTest(unittest.TestCase):
    def test_generated_files_are_up_to_date(self):
        run = subprocess.run(
            [sys.executable, str(ROOT / "tools/causeway/build_causeway_gameplay.py"), "--check"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
