"""Flicker index of an aa_shimmer frame sequence (M1-RND-07).

Usage: python tools/gpu_bench/aa_shimmer.py <dir> [<dir> ...]
For each folder of consecutive frames (f00.png ...) from tools/gpu_bench/aa_shimmer.tscn, prints
the mean absolute frame-to-frame difference in linear light over the whole frame and over the
"busy" pixels (top 10% of local contrast: foliage edges, where alpha-test aliasing lives). The
camera moves ~0.2 px per frame, so a perfectly anti-aliased image changes almost nothing; shimmer
shows as a high busy-pixel flicker.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "screenshots"))
import compare  # noqa: E402
import pngio  # noqa: E402

BUSY_PERCENTILE = 90


def flicker(folder: Path) -> tuple[float, float, int]:
    frames = [compare.srgb_to_linear(pngio.read(p)[..., :3]) for p in sorted(folder.glob("f*.png"))]
    lum = [f.mean(axis=-1) for f in frames]
    edge = np.abs(np.diff(lum[0], axis=0))[:, :-1] + np.abs(np.diff(lum[0], axis=1))[:-1, :]
    busy = edge >= np.percentile(edge, BUSY_PERCENTILE)
    diffs = [np.abs(b - a).mean(axis=-1)[:-1, :-1] for a, b in zip(frames, frames[1:])]
    whole = float(np.mean([d.mean() for d in diffs]))
    edge_flicker = float(np.mean([d[busy].mean() for d in diffs]))
    return whole, edge_flicker, len(frames)


def main() -> None:
    print("| Sequence | frames | flicker, whole frame | flicker, busy (edge) pixels |")
    print("|---|---:|---:|---:|")
    for arg in sys.argv[1:]:
        whole, edge, n = flicker(Path(arg))
        print(f"| {Path(arg).name} | {n} | {whole:.5f} | {edge:.5f} |")


if __name__ == "__main__":
    main()
