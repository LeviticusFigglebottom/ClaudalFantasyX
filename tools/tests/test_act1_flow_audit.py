"""act1-chapters (the Lead's flow and pacing pass, 2026-10-29): tools/act1/flow_audit.py finds no Act I flag that is
read but never set, none read before the chapter that sets it, and no flow group or trigger that can never run."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "act1"))
import flow_audit


class Act1FlowAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.out = flow_audit.Audit(ROOT).run()

    def test_every_flag_act1_reads_is_set_somewhere(self) -> None:
        self.assertEqual(self.out["never_set"], {})

    def test_no_flag_is_read_before_its_chapter_sets_it(self) -> None:
        self.assertEqual(self.out["late"], [])

    def test_every_beat_arrive_row_and_trigger_can_run(self) -> None:
        self.assertEqual(self.out["unreachable"], [])

    def test_every_act1_zone_is_reached(self) -> None:
        self.assertEqual(self.out["zones"], [])

    def test_a_flag_nothing_sets_is_caught(self) -> None:
        audit = flow_audit.Audit(ROOT)
        zid, chapter = next((z, c) for c, d in audit.chapters.items() for z in d["zones"])
        audit.chapters[chapter]["zones"][zid].setdefault("beats", {})["probe"] = {
            "when": {"set": ["probe_flag_nothing_sets"]}, "steps": []}
        out = audit.run()
        self.assertIn("probe_flag_nothing_sets", out["never_set"])
        self.assertIn(f"{zid} beat:probe", out["unreachable"])


if __name__ == "__main__":
    unittest.main()
