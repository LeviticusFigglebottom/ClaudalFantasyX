"""The Cage (M5-A3P-1851, docs/kb/art/creatures/act3/the_cage.md with the_cage_seats.md): four quarters, each a
`Q<n>Whole` (lit) and `Q<n>Broken` (dark) mesh swapped by its `break_q<n>` phase; the frame never gives off lift
light, and a broken quarter gives off none; the phases are cumulative, so no blow that crosses two leaves a quarter
whole; every founder's seat has its bone.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_tide_matron import _floats, _glb, _lengths  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
GLB = ROOT / "assets/creatures/the_cage/the_cage.glb"
BUDGET = 22000  # the sheet's triangle budget


class TheCageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.js, cls.blob = _glb(GLB)
        cls.row = json.loads((ROOT / "game/data/creatures/creatures.json").read_text(encoding="utf-8"))[
            "creatures"]["the_cage"]

    def _lit(self, mesh: dict) -> bool:
        for prim in mesh["primitives"]:
            if "TEXCOORD_1" in prim["attributes"]:
                if any(v[1] > 0.0 for v in _floats(self.js, self.blob, prim["attributes"]["TEXCOORD_1"])):
                    return True
        return False

    def test_each_quarter_is_lit_whole_and_dark_broken(self) -> None:
        meshes = {m["name"]: m for m in self.js["meshes"]}
        for n in range(1, 5):
            self.assertTrue(self._lit(meshes[f"Q{n}Whole"]), n)
            self.assertFalse(self._lit(meshes[f"Q{n}Broken"]), n)
        self.assertFalse(self._lit(meshes["the_cage"]), "the frame itself gives no light")

    def test_the_breaks_are_cumulative_phases_with_their_clips(self) -> None:
        clips = _lengths(self.js)
        for n in range(1, 5):
            p = self.row["phases"][f"break_q{n}"]
            self.assertIn(p["clip"], clips)
            self.assertEqual(p["hide"], [f"Q{i}Whole" for i in range(1, n + 1)])
            self.assertEqual(p["show"], [f"Q{i}Broken" for i in range(1, n + 1)])
            self.assertEqual(p["hide_after"], [f"FounderQ{i}" for i in range(1, n + 1)])
            self.assertAlmostEqual(clips[p["clip"]], 4.0, delta=0.05)

    def test_every_seat_has_its_bones_and_the_budget_holds(self) -> None:
        bones = {nd.get("name") for nd in self.js["nodes"]}
        for n in range(1, 5):
            for b in ("bay", "seat", "wrist_l", "wrist_r", "ankle_l", "ankle_r", "crown", "clasp", "chain_0"):
                self.assertIn(f"q{n}_{b}", bones)
        tris = sum(self.js["accessors"][p["indices"]]["count"] // 3 for m in self.js["meshes"] for p in m["primitives"])
        self.assertLessEqual(tris, BUDGET)
        scene = (ROOT / "game/creatures/the_cage/the_cage_battle.tscn").read_text(encoding="utf-8")
        for n in range(1, 5):
            self.assertIn(f'[node name="FounderQ{n}"', scene)


if __name__ == "__main__":
    unittest.main()
