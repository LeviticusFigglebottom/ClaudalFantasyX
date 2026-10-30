"""The Lead's FAST-TRACK (2026-10-30): field encounter pacing (tools/act1/encounter_pacing.py) on the real zones and
on a planted zone that fights too often.
Run: python3 -m unittest discover -s tools/tests"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/act1"))
import encounter_pacing as ep  # noqa: E402


class EncounterPacingTest(unittest.TestCase):
    def test_every_zone_gives_the_breather(self):
        rows = ep.zone_rows()
        self.assertGreaterEqual(len(rows), 9, "the Act I and Act II zones with random fights")
        self.assertEqual(ep.errors(rows), [])
        for r in rows:
            self.assertGreater(r["grace_s"], 0.0, r["layout"])

    def test_a_zone_that_fights_too_often_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in (ep.DEFAULTS, ep.MOVEMENT):
                dst = root / rel.relative_to(ROOT)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(rel, dst)
            d = json.loads((root / ep.DEFAULTS.relative_to(ROOT)).read_text())
            d["encounters"]["min_gap_m"] = 0.0
            (root / ep.DEFAULTS.relative_to(ROOT)).write_text(json.dumps(d))
            zone = root / "game/levels/chx/quick/quick_layout.json"
            zone.parent.mkdir(parents=True)
            zone.write_text(json.dumps({"encounters": {"table": [], "min_m": 18, "max_m": 34}}))
            errs = ep.errors(ep.zone_rows(root))
            self.assertEqual(len(errs), 1)
            self.assertIn("quick_layout.json", errs[0])


if __name__ == "__main__":
    unittest.main()
