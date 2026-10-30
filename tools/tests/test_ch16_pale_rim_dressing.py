"""Tests for the Pale Rim's pieces and its dressing generator (M4-A2P-046; env-art-b).

* The strand is the walk: white sand within a few centimetres of y 0 over the greybox's Sand, under the shallows.
* A cairn on every cairn block, salt-crusted by the zone's slot looks; the files on disk are the generator's.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import drowned_choir as dc  # noqa: E402


def _generator():
    path = ROOT / "tools/act2/ch16_pale_rim_dressing.py"
    spec = importlib.util.spec_from_file_location("ch16_pale_rim_dressing", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN = _generator()


class PaleRimTests(unittest.TestCase):
    def test_the_strand_is_the_walk_under_the_shallows(self) -> None:
        b = GEN.blocks()
        sand = b["Sand"]
        pos = np.asarray(dc.build_strand()[0].pos)
        cx = GEN.STRAND_AT[0]
        walk = pos[(np.abs(pos[:, 0] + cx - sand["pos"][0]) < sand["size"][0] * 0.5)
                   & (np.abs(pos[:, 2]) < sand["size"][2] * 0.5 - 1.0)]
        self.assertLess(np.abs(walk[:, 1]).max(), 0.05, "the walk's relief")
        self.assertGreater(GEN.WATER_Y, walk[:, 1].max(), "under the shallows")

    def test_a_salt_crusted_cairn_on_every_block_and_the_files(self) -> None:
        d = GEN.dressing()
        blocks = {(v["pos"][0], v["pos"][2]) for k, v in GEN.blocks().items() if k.startswith("Cairn")}
        self.assertEqual({tuple(p["at"]) for p in d["pieces"] if p["piece"] == "cairn"}, blocks)
        self.assertIn("kit_keth_crag", d["kit_material_paths"])
        self.assertEqual(json.loads((GEN.ZONE / "pale_rim_dressing.json").read_text(encoding="utf-8")), d)
        self.assertEqual((GEN.ZONE / GEN.ENV_NAME).read_text(encoding="utf-8"), GEN.environment())
        self.assertEqual((GEN.ZONE / GEN.WATER_NAME).read_text(encoding="utf-8"), GEN.water())


if __name__ == "__main__":
    unittest.main()
