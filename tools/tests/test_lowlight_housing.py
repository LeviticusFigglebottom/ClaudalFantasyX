"""Tests for Lowlight's conduit housing (M3-ENV-716; lowlight.md L03): the Saltwright housing-mark Liss reads.

The mark is the contract Rhen's lantern shares (Character's request): a circle crossed by three parallel lines over
two round seats, stamped proud of the housing's face.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import lowlight  # noqa: E402


class HousingMarkTests(unittest.TestCase):
    def test_the_mark_stands_proud_of_the_face_at_lod0_only(self) -> None:
        lod0, lod1 = lowlight.build_housing()
        face = 0.26
        p0, p1 = np.asarray(lod0.pos), np.asarray(lod1.pos)
        near = lambda p: (np.hypot(p[:, 0] + 0.14, p[:, 1] - 0.04) < lowlight.MARK_R + 0.01) & (p[:, 2] > face + 0.001)
        self.assertGreater(int(near(p0).sum()), 50, "the stamped circle and lines")
        self.assertEqual(int(near(p1).sum()), 0, "LOD1 is too far to read it")

    def test_the_two_seats_sit_side_by_side_under_the_circle(self) -> None:
        p = np.asarray(lowlight.build_housing()[0].pos)
        y_seat = 0.04 - lowlight.MARK_R - 0.035
        seats = p[(np.abs(p[:, 1] - y_seat) < 0.013) & (p[:, 2] > 0.26 + 0.001) & (np.abs(p[:, 0] + 0.14) < 0.05)]
        self.assertTrue(np.any(seats[:, 0] < -0.15) and np.any(seats[:, 0] > -0.13), "one either side of the axis")

    def test_inside_budget(self) -> None:
        lod0, lod1 = lowlight.build_housing()
        self.assertLessEqual(lod0.triangle_count, lowlight.TRI_BUDGET["conduit_housing"][0])
        self.assertLessEqual(lod1.triangle_count, lowlight.TRI_BUDGET["conduit_housing"][1])


if __name__ == "__main__":
    unittest.main()
