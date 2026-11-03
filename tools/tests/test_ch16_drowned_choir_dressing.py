"""The Drowned Choir's dressing (M4-A2P-046; env-art-b; tools/act2/ch16_drowned_choir_dressing.py).

* The walked amphitheatre stands at the greybox's origin; its aisles are open where chapters' relayout walks them
  (no tier block inside the 4 m aisles on the Z axis) and its ways are at the greybox's heights.
* A singer stands on every Mouth block at the sand, turned to the dais; the gap at 8 stays open.
* The files on disk are the generator's.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import drowned_choir as dc  # noqa: E402


def _generator():
    path = ROOT / "tools/act2/ch16_drowned_choir_dressing.py"
    spec = importlib.util.spec_from_file_location("ch16_drowned_choir_dressing", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN = _generator()


class DrownedChoirTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.b = GEN.blocks()
        cls.d = GEN.dressing()

    def test_a_singer_on_every_mouth_facing_the_dais(self) -> None:
        mouths = {k: v for k, v in self.b.items() if k.startswith("Mouth")}
        singers = [p for p in self.d["pieces"] if p["piece"] == "choir_singer"]
        self.assertEqual(len(singers), len(mouths))
        self.assertNotIn("Mouth8", mouths, "the approach's opening")
        for p in singers:
            x, z = p["at"]
            self.assertAlmostEqual(math.hypot(x, z), 44.0, delta=0.05)
            self.assertEqual(p["y"], dc.SAND_Y)
            yaw = math.radians(p["yaw_deg"])
            fwd = (math.sin(yaw), math.cos(yaw))  # the singer's +Z
            self.assertGreater(-(fwd[0] * x + fwd[1] * z) / math.hypot(x, z), 0.99, "faces the dais")

    def test_the_walked_amphitheatre_matches_the_relayout(self) -> None:
        self.assertEqual(self.d["pieces"][0]["piece"], "choir_amphitheatre_walked")
        self.assertEqual(self.d["pieces"][0]["at"], [0.0, 0.0])
        b = self.b
        self.assertAlmostEqual(b["Dais0"]["pos"][1] + b["Dais0"]["size"][1] * 0.5, 0.0, delta=0.01)
        gap = b["SouthGap"]
        self.assertAlmostEqual(gap["pos"][2] - gap["size"][2] * 0.5, dc.SOUTH_GAP_Z[0], delta=0.01)
        self.assertAlmostEqual(gap["pos"][2] + gap["size"][2] * 0.5, dc.SOUTH_GAP_Z[1], delta=0.01)
        self.assertAlmostEqual(gap["size"][0] * 0.5, dc.AISLE_HALF_W, delta=0.01)
        for side, sign in (("BridgeS", 1.0), ("BridgeN", -1.0)):
            br = b[side]
            self.assertAlmostEqual(abs(br["pos"][2]) - br["size"][2] * 0.5, dc.BRIDGE_Z[0], delta=0.01)
            self.assertAlmostEqual(abs(br["pos"][2]) + br["size"][2] * 0.5, dc.BRIDGE_Z[1], delta=0.01)
        ramp = json.loads(GEN.LAYOUT.read_text(encoding="utf-8"))["ramps"][0]
        (ya, za), (yb, zb) = dc.HEAD_RAMP
        self.assertEqual((ramp["from"][1], ramp["from"][2], ramp["to"][1], ramp["to"][2]), (ya, za, yb, zb))

    def test_no_tier_block_in_the_aisles(self) -> None:
        import numpy as np  # noqa: PLC0415

        mb = dc.build_amphitheatre_walked()[0]
        ceramic = mb.materials.index(dc.M_CERAMIC)  # the tiers and the outer face; the ways are paving
        tris = np.asarray(mb.tris)[np.asarray(mb.tri_mat) == ceramic]
        v = np.asarray(mb.pos)[np.unique(tris)]
        r = np.hypot(v[:, 0], v[:, 2])
        tiers = (r > dc.CHANNEL[1] + 0.3) & (r < dc.CHANNEL[1] + 6 * dc.TIER_W + 3.0)
        self.assertFalse(np.any(tiers & (np.abs(v[:, 0]) < dc.AISLE_HALF_W - 0.05)), "ceramic stands in an aisle")

    def test_offerings_at_every_other_singer(self) -> None:
        mouths = [k for k in self.b if k.startswith("Mouth")]
        rings = [p for p in self.d["pieces"] if p["piece"] == "choir_votive_rings"]
        self.assertEqual(len(rings), (len(mouths) + 1) // GEN.VOTIVE_EVERY)
        for p in rings:
            self.assertAlmostEqual(math.hypot(*p["at"]), 44.0 - GEN.VOTIVE_IN_M, delta=0.05)
            self.assertGreater(math.hypot(*p["at"]), dc.CHANNEL[1] + 6 * dc.TIER_W + 3.0, "on the sand, past the face")

    def test_the_files_are_the_generators(self) -> None:
        on_disk = json.loads((GEN.ZONE / "drowned_choir_dressing.json").read_text(encoding="utf-8"))
        self.assertEqual(on_disk, self.d)
        self.assertEqual((GEN.ZONE / GEN.ENV_NAME).read_text(encoding="utf-8"), GEN.environment())
        self.assertEqual((GEN.ZONE / GEN.WATER_NAME).read_text(encoding="utf-8"), GEN.water())


if __name__ == "__main__":
    unittest.main()
