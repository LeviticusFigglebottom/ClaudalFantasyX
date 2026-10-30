"""The Act I audio audit runs over the live data and reports every section (M3-AUD-861; ADR 0041). Since M3-AUD-864
it is also a gate: any open item (a silent, missing, borrowed or placeholder sound on the Act I path) fails here.
Run: python3 -m unittest discover -s tools/tests"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("act1_audio_audit", ROOT / "tools/audio/act1_audio_audit.py")
audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit)


class Act1AudioAuditTest(unittest.TestCase):
    def test_every_section_runs_and_returns_strings(self) -> None:
        for name, fn in audit.SECTIONS:
            items = fn()
            self.assertIsInstance(items, list, name)
            self.assertTrue(all(isinstance(i, str) for i in items), name)

    def test_it_covers_the_prologue_and_every_act1_chapter(self) -> None:
        scenes = audit.act1_scenes()
        for d in audit.ACT1_DIRS:
            self.assertTrue(any(f"/levels/{d}/" in s for s in scenes), d)
        self.assertFalse(any(s.endswith("_dressing.tscn") for s in scenes))

    def test_act1_has_no_silent_missing_or_placeholder_sound(self) -> None:
        for name, fn in audit.SECTIONS:
            open_items = [i for i in fn() if i not in audit.BY_DESIGN]
            self.assertEqual(open_items, [], f"Act I audio audit, {name}: run python3 tools/audio/act1_audio_audit.py")

    def test_a_row_is_checked_down_to_its_files(self) -> None:
        rows = {"ok": {"files": ["res://assets/audio/sfx/ui_confirm.ogg"]}, "gone": {"files": ["res://nowhere.ogg"]},
                "empty": {"files": []}}
        self.assertEqual(audit._row_problem(rows, "ok"), "")
        self.assertIn("missing", audit._row_problem(rows, "gone"))
        self.assertIn("names no file", audit._row_problem(rows, "empty"))
        self.assertIn("no sfx row", audit._row_problem(rows, "absent"))

    def test_the_act2_scope_reports_without_touching_the_act1_gate(self) -> None:
        try:
            audit.set_act(2)
            self.assertTrue(all(s.startswith("res://game/levels/ch1") for s in audit.act1_scenes()))
            for name, fn in audit.SECTIONS:
                self.assertIsInstance(fn(), list, name)
        finally:
            audit.set_act(1)
        self.assertTrue(any("/levels/prologue/" in s for s in audit.act1_scenes()), "back on Act I")


if __name__ == "__main__":
    unittest.main()
