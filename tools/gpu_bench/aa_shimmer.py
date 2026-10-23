"""Flicker index of an aa_shimmer frame sequence (M1-RND-07).

Usage: python tools/gpu_bench/aa_shimmer.py <dir> [<dir> ...]
       python tools/gpu_bench/aa_shimmer.py --ghost <taa_dir> <ref_dir>
--ghost (M1-RND-15): two runs of the same wind instants (--fixed-fps, no pan), one with TAA and one
without AA. Prints the mean and 99th-percentile linear difference between them over the reference's
busy pixels: the trail TAA leaves behind moving foliage (plus its static softening; compare with a
no-wind pair to separate the two).
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


def ghost(taa_dir: Path, ref_dir: Path) -> tuple[float, float, int]:
    """Mean and p99 linear difference, TAA vs no-AA at the same instants, over the reference's busy pixels."""
    taa = sorted(taa_dir.glob("f*.png"))
    ref = sorted(ref_dir.glob("f*.png"))
    vals = []
    for a, b in zip(taa, ref):
        fa = compare.srgb_to_linear(pngio.read(a)[..., :3])
        fb = compare.srgb_to_linear(pngio.read(b)[..., :3])
        lum = fb.mean(axis=-1)
        edge = np.abs(np.diff(lum, axis=0))[:, :-1] + np.abs(np.diff(lum, axis=1))[:-1, :]
        busy = edge >= np.percentile(edge, BUSY_PERCENTILE)
        vals.append(np.abs(fa - fb).mean(axis=-1)[:-1, :-1][busy])
    v = np.concatenate(vals) if vals else np.zeros(1)
    return float(v.mean()), float(np.percentile(v, 99)), len(vals)


def main() -> None:
    if len(sys.argv) == 4 and sys.argv[1] == "--ghost":
        mean, p99, n = ghost(Path(sys.argv[2]), Path(sys.argv[3]))
        print(f"| {Path(sys.argv[2]).name} vs {Path(sys.argv[3]).name} | {n} | {mean:.5f} | {p99:.5f} |")
        return
    print("| Sequence | frames | flicker, whole frame | flicker, busy (edge) pixels |")
    print("|---|---:|---:|---:|")
    for arg in sys.argv[1:]:
        whole, edge, n = flicker(Path(arg))
        print(f"| {Path(arg).name} | {n} | {whole:.5f} | {edge:.5f} |")


if __name__ == "__main__":
    main()
