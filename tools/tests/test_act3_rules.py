"""The Act III dialogue rules on the production scripts (M5-A3P-1000, ADR 0207): every .dlg under
game/data/dialogue/ch17..ch29 and ending/ obeys tools/act3_rules.py, with flags from flags.tres only.
Run: python3 -m unittest tools.tests.test_act3_rules"""
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import act3_rules  # noqa: E402

DIALOGUE = ROOT / "game" / "data" / "dialogue"


def act3_files() -> list[Path]:
    dirs = sorted(d for d in DIALOGUE.iterdir() if d.is_dir() and (d.name == "ending" or d.name[:2] == "ch"))
    return sorted(
        p for d in dirs if d.name == "ending" or (d.name[2:].isdigit() and int(d.name[2:]) >= 17) for p in d.glob("*.dlg")
    )


class Act3RulesTest(unittest.TestCase):
    def test_the_production_scripts_obey_the_act3_rules(self) -> None:
        files = act3_files()
        self.assertTrue(files, "there are Act III scripts")
        flags = act3_rules.declared_flags(ROOT)
        errors: list[str] = []
        for f in files:
            errors += act3_rules.letterbox_errors(f) + act3_rules.light_errors(f) + act3_rules.act3_errors(f, flags)
        self.assertEqual(errors, [])

    def test_a_planted_bad_ch17_scene_trips_every_rule(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "ch17" / "ch17_bad.dlg"
            f.parent.mkdir()
            f.write_text(textwrap.dedent("""\
                title: ch17_bad
                ---
                @letterbox on
                @vfx glimmer_lift at=x count=1 motion=spiral_up
                Dace [neutral]: Son. #line:ch17_bad_001
                Rhen [neutral]: A revenant. #line:ch17_bad_002
                <<set $ch17_not_a_flag = true>>
                ==="""), encoding="utf-8")
            errors = act3_rules.letterbox_errors(f) + act3_rules.light_errors(f) + act3_rules.act3_errors(f, set())
        joined = "\n".join(errors)
        for needle in ("letterbox", "nothing rises", "Dace's voice", "revenant", "ch17_not_a_flag"):
            self.assertIn(needle, joined)


if __name__ == "__main__":
    unittest.main()
