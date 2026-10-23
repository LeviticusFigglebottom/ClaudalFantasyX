"""Tests for tools/screenshots/mote_metrics.py and the palette_check mote kinds (M1-RND-17).
Run: python3 -m unittest discover -s tools/tests

* Streaks: an upright comet reads ~0 deg and heads-up; a 45-degree one reads ~45; a round blob is not
  a streak; a comet whose head is at its bottom counts as heads-down.
* Halo: gold light added over a grey background gives a delta hue near the gold's and grows |dab|;
  the halo's chroma beats the grey background's.
* The committed glimmer_dusk baseline reproduces the M1-ART-05 sign-off (hues 87 / 175 / 136 deg).
* palette_check: an advisory check that fails reports "warn" and does not count as a failure.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "screenshots"))
import mote_metrics as mm  # noqa: E402
import palette_check as pc  # noqa: E402
import pngio  # noqa: E402

H, W = 540, 960
GREY = 90


def _canvas() -> np.ndarray:
    return np.full((H, W, 3), GREY, dtype=np.float64)


def _comet(img: np.ndarray, cx: float, cy: float, angle_deg: float, head_up: bool = True, rgb=(255, 255, 255)) -> None:
    """A gaussian streak 24 px long along angle_deg from vertical, brightest at its upper (or lower) end."""
    a = np.radians(angle_deg)
    axis = np.array([-np.cos(a), np.sin(a)])  # (dy, dx), pointing up the screen
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.stack([yy - cy, xx - cx], -1)
    along = d @ axis
    across = d @ np.array([axis[1], -axis[0]])
    t = along if head_up else -along
    prof = np.exp(-(across**2) / 2.0) * np.clip((t + 12.0) / 24.0, 0.0, 1.0) * (np.abs(along) <= 12.0)
    for c in range(3):
        img[..., c] = np.maximum(img[..., c], GREY + (rgb[c] - GREY) * prof)


class StreakTests(unittest.TestCase):
    def test_upright_and_diagonal(self) -> None:
        img = _canvas()
        _comet(img, 100, 100, 0.0)
        _comet(img, 100, 300, 45.0)
        s = mm.streaks(np.clip(np.round(img), 0, 255).astype(np.uint8))
        self.assertEqual(s["count"], 2)
        self.assertAlmostEqual(s["median_deg"], 22.5, delta=4.0)
        self.assertEqual(s["heads_down_count"], 0)

    def test_heads_down_and_round_blobs(self) -> None:
        img = _canvas()
        _comet(img, 100, 100, 0.0, head_up=False)
        yy, xx = np.mgrid[0:H, 0:W]
        dot = np.exp(-((yy - 300) ** 2 + (xx - 100) ** 2) / 18.0)
        img = np.maximum(img, GREY + (255 - GREY) * dot[..., None])
        s = mm.streaks(np.clip(np.round(img), 0, 255).astype(np.uint8))
        self.assertEqual(s["count"], 1, "the round dot is not a streak")
        self.assertEqual(s["heads_down_count"], 1)


class HaloTests(unittest.TestCase):
    def test_gold_added_light_has_gold_delta(self) -> None:
        img = _canvas()
        yy, xx = np.mgrid[0:H, 0:W]
        g = np.exp(-((yy - 100) ** 2 + (xx - 200) ** 2) / 200.0)
        gold = np.array([255, 200, 90], dtype=np.float64)
        img = img + (gold - GREY)[None, None, :] * 0.6 * g[..., None]
        h = mm.halo(np.clip(np.round(img), 0, 255).astype(np.uint8))
        r = h["regions"]["upper_sky"]
        self.assertGreater(r["pixels"], 0)
        self.assertTrue(60.0 <= r["hue"] <= 100.0, r["hue"])
        self.assertGreater(r["dab"], 0.02)
        self.assertGreater(r["chroma"], r["bg_chroma"])

    def test_baseline_reproduces_the_sign_off(self) -> None:
        # The frozen image the 2026-10-23 Art sign-off measured (the pre-RND-17 glimmer_dusk
        # baseline). The live baseline moves on re-approval, so it cannot pin the tool.
        img = pngio.read(ROOT / "tests" / "fixtures" / "mote_metrics" / "glimmer_dusk_signoff_2026-10-23.png")
        h = mm.halo(img)["regions"]
        self.assertAlmostEqual(h["upper_sky"]["hue"], 87.0, delta=3.0)
        self.assertAlmostEqual(h["horizon"]["hue"], 175.0, delta=5.0)
        self.assertAlmostEqual(h["mirror"]["hue"], 136.0, delta=5.0)
        self.assertAlmostEqual(h["upper_sky"]["dab"], 0.039, delta=0.004)


class AdvisoryTests(unittest.TestCase):
    def test_advisory_failure_warns(self) -> None:
        import json
        import tempfile

        img = _canvas().astype(np.uint8)
        with tempfile.TemporaryDirectory() as d:
            pngio.write(Path(d) / "flat.png", img)
            checks = {"checks": [
                {"shot": "flat", "name": "streaks", "kind": "mote_streaks", "advisory": True, "median_deg_max": 25},
                {"shot": "flat", "name": "streaks strict", "kind": "mote_streaks", "median_deg_max": 25},
            ]}
            cp = Path(d) / "checks.json"
            cp.write_text(json.dumps(checks), encoding="utf-8")
            failures, lines = pc.run_checks(cp, Path(d))
        self.assertEqual(failures, 1, "only the strict check fails (no streaks at all)")
        self.assertTrue(lines[0].startswith("warn"))
        self.assertTrue(lines[1].startswith("FAIL"))


if __name__ == "__main__":
    unittest.main()
