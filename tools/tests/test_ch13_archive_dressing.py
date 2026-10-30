"""Tests for the Lamp Archive's pieces and its dressing generator (M4-A2P-043; env-art-b).

* The ledger case is the greybox's Stack block (5 x 6 x 1 m), and a case stands on every Stack block; the tables stand
  on theirs.
* The room's floors have bedding under their joints; the bays fill the room from the door wall to the north wall.
* The files on disk are the generator's, and no lamp is lit (the Order's light is daylight).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import ansedra  # noqa: E402


def _generator():
    spec = importlib.util.spec_from_file_location("ch13_archive_dressing", ROOT / "tools/act2/ch13_archive_dressing.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN = _generator()


class ArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.b = GEN.blocks()
        cls.d = GEN.dressing()

    def test_the_case_is_the_stack_block(self) -> None:
        lo, hi = ansedra.build_archive_case()[0].bounds()
        size = self.b["Stack0W"]["size"]
        self.assertAlmostEqual(hi[0] - lo[0], size[0], delta=0.05)
        self.assertAlmostEqual(hi[1], size[1], delta=0.05)
        self.assertLessEqual(hi[2] - lo[2], size[2] + 0.05, "no deeper than the block (its gilt fillets sit proud)")

    def test_a_case_on_every_stack_and_the_tables_on_theirs(self) -> None:
        stacks = {(v["pos"][0], v["pos"][2]) for k, v in self.b.items() if k.startswith("Stack")}
        cases = {tuple(p["at"]) for p in self.d["pieces"] if p["piece"] == "archive_case"}
        self.assertEqual(cases, stacks)
        for bid, piece in GEN.TABLES.items():
            at = [p["at"] for p in self.d["pieces"] if p["piece"] == piece]
            self.assertEqual(at, [[self.b[bid]["pos"][0], self.b[bid]["pos"][2]]], piece)
        lo, hi = ansedra.build_reading_table()[0].bounds()
        self.assertLessEqual(hi[0] - lo[0], self.b["LedgerTable"]["size"][0] + 0.02)

    def test_the_bays_fill_the_room(self) -> None:
        zs = sorted(p["at"][1] for p in self.d["pieces"] if p["piece"] == "archive_hall_bay")
        self.assertAlmostEqual(zs[-1] + ansedra.HALL_BAY * 0.5, 0.0, delta=0.01)
        self.assertAlmostEqual(zs[0] - ansedra.HALL_BAY * 0.5, -ansedra.HALL_LEN, delta=0.01)
        lo, _hi = ansedra.build_archive_hall_bay()[0].bounds()
        self.assertLess(lo[1], -0.3, "a bedding slab under the paving")

    def test_the_file_is_the_generators_and_no_lamp_is_lit(self) -> None:
        on_disk = json.loads((GEN.ZONE / "lamp_archive_dressing.json").read_text(encoding="utf-8"))
        self.assertEqual(on_disk, self.d)
        self.assertNotIn("fire_lights", self.d)
        for name in ("reading_table", "roll_table", "archive_case"):
            mb = ansedra.TARGETS[name]()[0]
            self.assertNotIn(ansedra.M_CORE, mb.materials, name)
            self.assertNotIn(ansedra.M_WINDOW, mb.materials, name)


if __name__ == "__main__":
    unittest.main()
