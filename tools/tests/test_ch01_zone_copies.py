"""Ch1's zones keep two copies of env-art's kit-preview resources (a shipped zone never reads game/levels/_tests/):
Oruvel's water material and the Underway's ch01 Environment. The generators that wrote them retired when the zones
mounted env-art's own dressings (M3-ENV-740, M3-ENV-742), so this keeps each copy identical to its source."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COPIES = {
    "game/levels/_tests/oruvel_kit/oruvel_water_material.tres": "game/levels/ch01/oruvel/oruvel_water_material.tres",
    "game/levels/_tests/oruvel_underway_kit/oruvel_underway_ch01_environment.tres":
        "game/levels/ch01/oruvel_underway/oruvel_underway_ch01_environment.tres",
}


class Ch01ZoneCopiesTest(unittest.TestCase):
    def test_each_copy_matches_its_source(self) -> None:
        for src, dst in COPIES.items():
            with self.subTest(dst=dst):
                self.assertEqual((ROOT / src).read_bytes(), (ROOT / dst).read_bytes(), f"copy {src} over {dst}")


if __name__ == "__main__":
    unittest.main()
