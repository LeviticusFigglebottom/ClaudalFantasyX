"""RMSE (linear light, as tools/screenshots/compare.py) between two capture folders, plus diff PNGs.

Usage: python tools/gpu_bench/diff_shots.py <before_dir> <after_dir> [--diff-dir DIR]
Prints a markdown row per PNG present in both folders. Used for M1-RND-10 before/after look checks
on GPU captures; it never reads or writes tests/screenshots/baselines.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "screenshots"))
import compare  # noqa: E402
import pngio  # noqa: E402

# A pixel "changed visibly" when any channel moved by more than this many 8-bit levels.
VISIBLE_LEVELS = 8


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("before", type=Path)
    ap.add_argument("after", type=Path)
    ap.add_argument("--diff-dir", type=Path)
    args = ap.parse_args()
    print(f"| Shot | RMSE | max abs (8-bit) | pixels > {VISIBLE_LEVELS} levels |")
    print("|---|---:|---:|---:|")
    for b in sorted(args.before.glob("*.png")):
        a = args.after / b.name
        if not a.exists():
            continue
        x = pngio.read(b)[..., :3]
        y = pngio.read(a)[..., :3]
        diff = np.abs(x.astype(np.int16) - y.astype(np.int16)).max(axis=-1)
        print(
            f"| {b.stem} | {compare.rmse_linear(x, y):.5f} | {int(diff.max())} | "
            f"{float(np.mean(diff > VISIBLE_LEVELS)):.1%} |"
        )
        if args.diff_dir:
            args.diff_dir.mkdir(parents=True, exist_ok=True)
            pngio.write(args.diff_dir / b.name, compare.diff_image(x, y))


if __name__ == "__main__":
    main()
