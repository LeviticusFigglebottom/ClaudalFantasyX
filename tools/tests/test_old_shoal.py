"""The Old Shoal (M5-A3P-1853, docs/kb/art/creatures/act3/old_shoal.md): the Ch18 secret superboss. It was never part
of the cycle, so no vertex gives light; it plays the sheet's clips, and its KO is `settle` (it goes back to sleep).
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_tide_matron import _floats, _glb, _lengths  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
GLB = ROOT / "assets/creatures/old_shoal/old_shoal.glb"
CLIPS = {"idle": 6.0, "ready": 4.0, "intro": 4.0, "attack": 2.4, "cast": 3.0, "bite": 2.0, "hit": 0.8, "settle": 4.0}


class OldShoalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.js, cls.blob = _glb(GLB)

    def test_no_vertex_gives_light(self) -> None:
        for mesh in self.js["meshes"]:
            for prim in mesh["primitives"]:
                if "TEXCOORD_1" in prim["attributes"]:
                    lit = [v for v in _floats(self.js, self.blob, prim["attributes"]["TEXCOORD_1"]) if v[1] > 0.0]
                    self.assertEqual(lit, [], mesh["name"])
        spec = json.loads((ROOT / "assets_src/creatures/old_shoal/materials.json").read_text(encoding="utf-8"))
        for slot, params in spec["slots"].items():
            self.assertEqual(params.get("emission_energy", 0.0), 0.0, slot)

    def test_it_plays_the_sheets_clips(self) -> None:
        got = _lengths(self.js)
        for name, sec in CLIPS.items():
            self.assertAlmostEqual(got.get(name, -1.0), sec, delta=0.05, msg=name)

    def test_its_ko_is_the_settle_and_it_has_no_wound(self) -> None:
        row = json.loads((ROOT / "game/data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
        self.assertEqual(row["old_shoal"]["ko"], "settle")
        bones = {nd.get("name") for nd in self.js["nodes"]}
        self.assertIn("vfx_core", bones)
        self.assertNotIn("vfx_wound", bones)
        self.assertNotIn("Leviathan".lower(), json.dumps(row["old_shoal"]).lower())


if __name__ == "__main__":
    unittest.main()
