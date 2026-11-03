"""The battle status icons are the generator's output (FAST-TRACK 11-03, M3-BPR-450): one per status, reproducible."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class StatusIconsTest(unittest.TestCase):
    def test_one_icon_per_status_matching_the_generator(self) -> None:
        r = subprocess.run(
            [sys.executable, str(ROOT / "tools/vfx/status_icons.py"), "--check"], capture_output=True, text=True
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        ids = [s["id"] for s in json.loads((ROOT / "game/data/battle/statuses.json").read_text())["statuses"]]
        icons = {p.stem for p in (ROOT / "assets/vfx/battle/status_icons").glob("*.svg")}
        self.assertEqual(set(ids), icons)

    def test_beneficial_is_a_circle_harmful_a_square(self) -> None:
        for s in json.loads((ROOT / "game/data/battle/statuses.json").read_text())["statuses"]:
            text = (ROOT / f"assets/vfx/battle/status_icons/{s['id']}.svg").read_text()
            badge = text.splitlines()[2]
            self.assertTrue(badge.startswith("<circle" if s["category"] == "beneficial" else "<rect"), s["id"])


if __name__ == "__main__":
    unittest.main()
