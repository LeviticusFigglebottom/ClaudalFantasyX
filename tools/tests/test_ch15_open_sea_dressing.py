"""M4-A2P-045: Ch15's open-sea dressing (tools/act2/ch15_open_sea_dressing.py; open_sea_zones.py) against the greybox."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "act2"))
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import bridal_barge as bb  # noqa: E402
import ch15_open_sea_dressing as gen  # noqa: E402
import open_sea_zones as oz  # noqa: E402


class Ch15DressingTests(unittest.TestCase):
    def test_committed_dressing_matches_its_generator(self) -> None:
        committed = json.loads((gen.ZONE_DIR / f"{gen.ZONE}_dressing.json").read_text(encoding="utf-8"))
        self.assertEqual(committed, gen.layout(), "re-run tools/act2/ch15_open_sea_dressing.py")

    def test_every_piece_exists(self) -> None:
        lay = gen.layout()
        for p in lay["pieces"]:
            self.assertTrue((ROOT / lay["kit_dir"].removeprefix("res://") / f"{p['piece']}.glb").is_file(), p["piece"])

    def test_the_barge_fits_the_greybox_deck_and_bier(self) -> None:
        bl = oz.blocks()
        f = oz.fitted()
        mb = oz.build_barge()[0]
        lo, hi = mb.bounds()
        deck = bl["Deck"]
        self.assertAlmostEqual(hi[0] - lo[0], deck["size"][2], delta=0.1, msg="the hull is the deck's length")
        self.assertLessEqual(hi[2], abs(bl["RailE"]["pos"][0]) + 0.15, "the hull within the rails")
        self.assertAlmostEqual(f["bier_at"][0], bl["Bier"]["pos"][2] - deck["pos"][2], places=6)

    def test_the_arena_barge_keeps_its_size(self) -> None:
        self.assertEqual((bb.BOW_X, bb.STERN_X, bb.HALF_BEAM), (-8.6, 8.0, 3.75))


if __name__ == "__main__":
    unittest.main()
