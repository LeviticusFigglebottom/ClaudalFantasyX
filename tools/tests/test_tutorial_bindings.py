"""M2-FP-30: tutorial lines name the player's own binding through an {action} placeholder (InputNames.fill), never a
fixed word or key. Ch1's tether line said "Press interact"; this keeps every tutorial script to the placeholders."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERB = re.compile(r"\b(Press|Hold|Tap|press|hold|tap) (?!\{)(\w+)")
# Story words that follow "hold" in a tutorial's plain sense (hold the stair, hold still), not a control.
NOT_CONTROLS = {"it", "the", "still", "on", "your", "them", "fast"}


class TutorialBindingsTest(unittest.TestCase):
    def test_tutorial_lines_name_bindings_by_action(self):
        bad = []
        for dlg in sorted((ROOT / "game" / "data" / "dialogue").rglob("*_tut_*.dlg")):
            for n, line in enumerate(dlg.read_text(encoding="utf-8").splitlines(), 1):
                if line.lstrip().startswith("//") or "#line:" not in line:
                    continue
                for m in VERB.finditer(line):
                    if m.group(2).lower() not in NOT_CONTROLS:
                        bad.append(f"{dlg.relative_to(ROOT)}:{n}: '{m.group(0)}'")
        self.assertEqual(bad, [], "\n".join(bad))


if __name__ == "__main__":
    unittest.main()
