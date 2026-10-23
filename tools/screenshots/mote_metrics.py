"""Released-mote halo and streak metrics (M1-RND-17), the method of the M1-ART-05 sign-off.

Used by palette_check.py (check kinds "mote_halo" and "mote_streaks"); also runnable:
    python tools/screenshots/mote_metrics.py <png> [--box x0,y0,x1,y1]

* Background: per-row 30th percentile of linear sRGB over every pixel outside the figure box (the
  sky and the mirror are uniform along a row).
* rel = (pixel luminance - background luminance) / background luminance, Rec.709 weights.
  Inner halo: 0.6 < rel <= 2.0. Coverage: rel > 0.10. Core: rel > 2.0.
* Halo delta: mean of (pixel Oklab - background Oklab) a, b over the inner-halo pixels of a region
  (rows y0..y1): its hue (degrees) and length. Also the median pixel chroma under the halo against
  the median background chroma there.
* Streaks: 8-connected blobs of rel > 0.35 with >= 12 px; luminance-weighted PCA; elongation
  sqrt(l1 / l2) >= 2 kept. Angle from screen vertical; heads-down when the brightest pixel lies more
  than 1 px below the centroid along the streak axis.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette_check as pc  # noqa: E402
import pngio  # noqa: E402

REC709 = np.array([0.2126, 0.7152, 0.0722])
BG_PERCENTILE = 30
INNER_MIN, INNER_MAX = 0.6, 2.0
COVER_MIN = 0.10
CORE_MIN = 2.0
STREAK_REL = 0.35
STREAK_MIN_PX = 12
STREAK_MIN_ELONGATION = 2.0
HEADS_DOWN_PX = 1.0
DEFAULT_BOX = (445, 200, 515, 470)
REGIONS = {"upper_sky": (0, 180), "horizon": (250, 360), "mirror": (365, 540)}


def _rel_and_background(img: np.ndarray, box: tuple[int, int, int, int]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    lin = pc.srgb8_to_linear(img[..., :3])
    h, w = lin.shape[:2]
    x0, y0, x1, y1 = box
    outside = np.ones((h, w), dtype=bool)
    outside[y0:y1, x0:x1] = False
    bg = np.zeros((h, 3))
    for y in range(h):
        row = lin[y][outside[y]]
        bg[y] = np.percentile(row, BG_PERCENTILE, axis=0)
    lum = lin @ REC709
    bg_lum = np.maximum(bg @ REC709, 1e-6)
    rel = (lum - bg_lum[:, None]) / bg_lum[:, None]
    return lin, bg, rel


def halo(img: np.ndarray, box: tuple[int, int, int, int] = DEFAULT_BOX) -> dict:
    """Per-region inner-halo delta (hue, |dab|), chroma under the halo vs background, coverage, core chroma."""
    lin, bg, rel = _rel_and_background(img, box)
    lab = pc.linear_to_oklab(lin)
    bg_lab = pc.linear_to_oklab(bg)
    inner = (rel > INNER_MIN) & (rel <= INNER_MAX)
    out: dict = {"coverage": float(np.mean(rel > COVER_MIN)), "regions": {}}
    core = rel > CORE_MIN
    out["core_chroma"] = float(np.median(np.hypot(lab[..., 1], lab[..., 2])[core])) if core.any() else 0.0
    for name, (y0, y1) in REGIONS.items():
        m = inner[y0:y1]
        if not m.any():
            out["regions"][name] = {"pixels": 0}
            continue
        d = lab[y0:y1][m] - np.repeat(bg_lab[y0:y1, None, :], m.shape[1], axis=1)[m]
        da, db = float(d[:, 1].mean()), float(d[:, 2].mean())
        pix_c = np.hypot(lab[y0:y1][m][:, 1], lab[y0:y1][m][:, 2])
        bg_rows = np.repeat(bg_lab[y0:y1, None, :], m.shape[1], axis=1)[m]
        out["regions"][name] = {
            "pixels": int(m.sum()),
            "hue": float(np.degrees(np.arctan2(db, da)) % 360.0),
            "dab": float(np.hypot(da, db)),
            "chroma": float(np.median(pix_c)),
            "bg_chroma": float(np.median(np.hypot(bg_rows[:, 1], bg_rows[:, 2]))),
        }
    return out


def _blobs(mask: np.ndarray) -> list[np.ndarray]:
    """8-connected components of mask as (N, 2) arrays of (y, x)."""
    seen = np.zeros(mask.shape, dtype=bool)
    h, w = mask.shape
    out = []
    for y, x in zip(*np.nonzero(mask)):
        if seen[y, x]:
            continue
        seen[y, x] = True
        q = deque([(y, x)])
        px = []
        while q:
            cy, cx = q.popleft()
            px.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        q.append((ny, nx))
        out.append(np.array(px))
    return out


def streaks(img: np.ndarray, box: tuple[int, int, int, int] = DEFAULT_BOX) -> dict:
    """Angles (degrees from vertical) of the elongated streak blobs and how many are heads-down."""
    lin, _bg, rel = _rel_and_background(img, box)
    lum = lin @ REC709
    angles = []
    heads_down = 0
    for px in _blobs(rel > STREAK_REL):
        if len(px) < STREAK_MIN_PX:
            continue
        wgt = lum[px[:, 0], px[:, 1]]
        c = (px * wgt[:, None]).sum(0) / wgt.sum()
        d = px - c
        cov = (d * wgt[:, None]).T @ d / wgt.sum()
        evals, evecs = np.linalg.eigh(cov)
        if evals[0] <= 1e-9 or np.sqrt(evals[1] / evals[0]) < STREAK_MIN_ELONGATION:
            continue
        axis = evecs[:, 1]  # (dy, dx)
        if axis[0] > 0:
            axis = -axis  # point up the screen
        angles.append(float(np.degrees(np.arccos(min(1.0, abs(axis[0]))))))
        bright = px[int(np.argmax(wgt))] - c
        if float(bright @ axis) < -HEADS_DOWN_PX:
            heads_down += 1
    a = np.array(angles) if angles else np.zeros(0)
    n = len(a)
    return {
        "count": n,
        "median_deg": float(np.median(a)) if n else 0.0,
        "within_30": float(np.mean(a <= 30.0)) if n else 0.0,
        "beyond_60": float(np.mean(a > 60.0)) if n else 0.0,
        "heads_down": heads_down / n if n else 0.0,
        "heads_down_count": heads_down,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("png")
    ap.add_argument("--box", default=",".join(str(v) for v in DEFAULT_BOX))
    a = ap.parse_args(argv)
    box = tuple(int(v) for v in a.box.split(","))
    img = pngio.read(a.png)
    print(json.dumps({"halo": halo(img, box), "streaks": streaks(img, box)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
