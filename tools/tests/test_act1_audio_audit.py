"""The Act I audio audit runs over the live data and reports every section (M3-AUD-861; ADR 0041).
It is a report, not a gate: the work list it prints is in docs/kb/handoffs/live/audio.md.
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


if __name__ == "__main__":
    unittest.main()
