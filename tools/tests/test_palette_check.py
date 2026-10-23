"""Tests for tools/screenshots/palette_check.py (M1-ENV-01). Run: python3 -m unittest discover -s tools/tests

* Colour maths against the values the art review quoted (Oklab L / C of palette swatches).
* Masks and statistics on synthetic images.
* The committed baselines pass tests/screenshots/palette_checks.json (the sky, chapel, banyan, plank
  and red-budget targets of review-sweep-F), so a re-approval that drifts off the palette fails here.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "screenshots"))
import palette_check as pc  # noqa: E402


def solid(hex_color: str, w: int = 32, h: int = 32) -> np.ndarray:
    return np.tile(pc.hex_to_rgb8(hex_color), (h, w, 1))


class ColourMathTests(unittest.TestCase):
    def test_oklab_matches_review_values(self) -> None:
        # The review quoted sky_zenith_noon +1 #6DAFDC at C 0.094 and cumulus_lit +1 at L 0.90.
        L, C, _h = pc.lch(pc.hex_to_oklab("#6DAFDC"))
        self.assertAlmostEqual(float(C), 0.094, places=3)
        L, C, _h = pc.lch(pc.hex_to_oklab("#E1DFDD"))
        self.assertAlmostEqual(float(L), 0.905, places=2)

    def test_white_and_black(self) -> None:
        self.assertAlmostEqual(float(pc.hex_to_oklab("#FFFFFF")[0]), 1.0, places=3)
        self.assertAlmostEqual(float(pc.hex_to_oklab("#000000")[0]), 0.0, places=6)

    def test_palette_loads_onscreen_columns(self) -> None:
        pal = pc.load_palette()
        self.assertIn("sky_zenith_noon", pal)
        self.assertEqual(set(pal["cumulus_shadow"]), {"-1", "0", "+1"})


class MaskTests(unittest.TestCase):
    def test_red_mask_counts_roof_red_only(self) -> None:
        img = solid("#D27D5C", 10, 10)  # roof_clay +1
        img[:, 5:] = pc.hex_to_rgb8("#6DAFDC")
        cov = pc.coverage(img, pc.load_palette(), 0.08)
        self.assertAlmostEqual(cov["red_hsv"], 0.5)
        self.assertAlmostEqual(cov["swatches"]["roof_clay"], 0.5)

    def test_grey_is_not_red(self) -> None:
        cov = pc.coverage(solid("#A6AAAC"), pc.load_palette(), 0.08)
        self.assertEqual(cov["red_hsv"], 0.0)

    def test_grain_separates_stipple_from_gradient(self) -> None:
        ramp = np.linspace(170, 220, 64)
        smooth = np.repeat(np.tile(ramp[None, :, None], (64, 1, 1)), 3, axis=2).round().astype(np.uint8)
        stipple = smooth.astype(int).copy()
        stipple[::2, ::2] += 8
        stipple = np.clip(stipple, 0, 255).astype(np.uint8)
        self.assertLess(pc.grain(smooth, None), 0.001)
        self.assertGreater(pc.grain(stipple, None), 0.005)

    def test_region_selection_and_near_swatch(self) -> None:
        img = solid("#6DAFDC", 20, 20)
        img[10:] = pc.hex_to_rgb8("#E1DFDD")
        chk = {"kind": "near_swatch", "rect": [0, 0, 20, 20], "select": {"C_min": 0.03},
               "swatch": "sky_zenith_noon", "level": "+1", "max_de": 0.01}
        ok, msg = pc.run_check(chk, img, pc.load_palette())
        self.assertTrue(ok, msg)
        chk["select"] = {"C_max": 0.02}
        ok, _msg = pc.run_check(chk, img, pc.load_palette())
        self.assertFalse(ok)

    def test_empty_selection_fails(self) -> None:
        chk = {"kind": "stat", "rect": [0, 0, 8, 8], "select": {"L_min": 2.0}, "stat": "L_median", "min": 0.0}
        ok, msg = pc.run_check(chk, solid("#808080", 8, 8), pc.load_palette())
        self.assertFalse(ok)
        self.assertIn("selection", msg)


class BaselineTests(unittest.TestCase):
    def test_committed_baselines_meet_palette_checks(self) -> None:
        failures, lines = pc.run_checks(pc.CHECKS, pc.BASELINES)
        self.assertEqual(failures, 0, "\n".join(ln for ln in lines if ln.startswith("FAIL")))


class MutationTests(unittest.TestCase):
    """M1-RND-12 (review-sweep-H): the defects the reviewer injected into H01 now fail the checks."""

    @classmethod
    def setUpClass(cls) -> None:
        import json

        cls.checks = json.loads(pc.CHECKS.read_text(encoding="utf-8"))["checks"]
        cls.img = pc.pngio.read(pc.BASELINES / "haluna_h01_village_from_sea.png")[:, :, :3].copy()
        cls.palette = pc.load_palette()

    def _check(self, name: str) -> dict:
        return next(c for c in self.checks if c["shot"] == "haluna_h01_village_from_sea" and c["name"] == name)

    def test_mostly_grey_zenith_fails(self) -> None:
        chk = self._check("zenith chroma")
        x0, y0, x1, y1 = chk["rect"]
        img = self.img.copy()
        cut = y0 + int((y1 - y0) * 0.9)
        img[y0:cut, x0:x1] = pc.hex_to_rgb8("#A6A8AA")  # C ~0.01: 90 % of the zenith rect greyed
        self.assertTrue(pc.run_check(chk, self.img, self.palette)[0], "baseline passes")
        self.assertFalse(pc.run_check(chk, img, self.palette)[0], "90 % grey zenith")

    def test_cyan_underside_drift_fails(self) -> None:
        chk = self._check("cumulus underside hue")
        x0, y0, x1, y1 = chk["rect"]
        sub = self.img[y0:y1, x0:x1].astype(np.float64)
        m = pc.select(pc.image_oklab(self.img[y0:y1, x0:x1]), chk["select"])
        drift = sub.copy()
        drift[m] = drift[m] * np.array([0.93, 1.0, 0.97])  # pull the undersides towards cyan
        img = self.img.copy()
        img[y0:y1, x0:x1] = np.clip(np.round(drift), 0, 255).astype(np.uint8)
        self.assertTrue(pc.run_check(chk, self.img, self.palette)[0], "baseline passes")
        self.assertFalse(pc.run_check(chk, img, self.palette)[0], "cyan undersides")


if __name__ == "__main__":
    unittest.main()
