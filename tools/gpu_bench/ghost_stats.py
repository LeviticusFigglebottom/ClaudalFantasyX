"""Ghosting stats for tools/gpu_bench/ghost_check (M1-RND-10 follow-up).

Usage: python tools/gpu_bench/ghost_stats.py <ghost_root> [--configs final,static] [--reference reference]
<ghost_root> holds, from ghost_check, <config>_moving/ and <config>_converged/ per config, and the
common ground truth <reference>/ (--config=reference --mode=converged --converge=128). For every saved
frame it prints the linear-light RMSE (tools/screenshots/compare.py) of each config's moving frame and
of its at-rest (converged) frame against the reference, over the whole frame, the storm (above the
horizon) and a band around the silhouette that extends past its trailing (disoccluded) edge.
Ghosting shows as "moving" error above "at rest" error, concentrated in the silhouette band.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "screenshots"))
import compare  # noqa: E402
import pngio  # noqa: E402

# ghost_check's rois.json is in the project's base viewport size (canvas_items stretch).
BASE_W = 1920.0
BASE_H = 1080.0
# Band around the silhouette (image px): margin on every side, plus extra on the trailing side.
ROI_MARGIN = 48
ROI_TRAIL = 200
# Fraction of the image height above which the Horizon view shows only sky and storm.
STORM_ROWS = 0.5


def regions(img: np.ndarray, roi: list[float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    h, w = img.shape[:2]
    x, y, rw, rh = roi
    sx, sy = w / BASE_W, h / BASE_H
    # The camera pans right, so the silhouette moves left and its right side is disoccluded.
    x0 = max(0, int(x * sx) - ROI_MARGIN)
    x1 = min(w, int((x + rw) * sx) + ROI_MARGIN + ROI_TRAIL)
    y0 = max(0, int(y * sy) - ROI_MARGIN)
    y1 = min(h, int((y + rh) * sy) + ROI_MARGIN)
    return img, img[: int(h * STORM_ROWS)], img[y0:y1, x0:x1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--configs", default="final,static")
    ap.add_argument("--reference", default="reference")
    args = ap.parse_args()
    columns = [f"{c}_{m}" for c in args.configs.split(",") for m in ("moving", "converged")]
    rois = json.loads((args.root / f"{columns[0]}" / "rois.json").read_text())
    print("Each cell: RMSE vs the reference, full / storm / silhouette band.\n")
    print("| Frame | " + " | ".join(columns) + " |")
    print("|---|" + "---|" * len(columns))
    totals = {c: [] for c in columns}
    for frame in sorted(rois, key=int):
        name = f"f{int(frame):02d}.png"
        ref = regions(pngio.read(args.root / args.reference / name)[..., :3], rois[frame])
        cells = []
        for col in columns:
            img = regions(pngio.read(args.root / col / name)[..., :3], rois[frame])
            vals = [compare.rmse_linear(a, b) for a, b in zip(img, ref)]
            totals[col].append(vals)
            cells.append(" / ".join(f"{v:.4f}" for v in vals))
        print(f"| {frame} | " + " | ".join(cells) + " |")
    means = [" / ".join(f"{v:.4f}" for v in np.mean(totals[c], axis=0)) for c in columns]
    print("| **mean** | " + " | ".join(f"**{m}**" for m in means) + " |")


if __name__ == "__main__":
    main()
