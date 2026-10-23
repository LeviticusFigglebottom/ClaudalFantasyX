"""Bake the zone sky's 2D cloud lattice (M1-RND-12) to assets/vfx/sky/cloud_lattice2.png.

env_sky_cumulus's height field is 3 octaves of hymn_value_noise2, which hashes four lattice corners
(hymn_hash_cell2 = hymn_pcg2d(uvec2(ivec2(cell))).x) per lookup and runs on every march step, the
empty ones too: on an RX 9070 XT that coarse march alone was ~0.7 ms at High 1440p. This bakes the
same hash for every cell the sky reaches into a SIZE x SIZE 8-bit greyscale lattice, signed: texel
(tx, ty) holds the hash of cell (c(tx), c(ty)) with c(t) = t for t < SIZE / 2 and t - SIZE above, so
with repeat wrapping, cell c sits at texel c mod SIZE and the baked noise equals the shader's hash
(to 8 bits) for |c| < SIZE / 2. The shader reads each octave's four corners with one textureGather
and interpolates in ALU (quintic), so there is no filter-weight quantisation: hardware bilinear only
has 8 sub-texel bits, which would terrace the dome walls the height field extrudes.

Reach: cloud_max_distance_m (60 km) + the march length, over cloud_scale_m (1.7 km), is about 40
cells; the third octave (lacunarity 2.03, rotated) reaches about 165 < SIZE / 2.

Usage: python3 assets_src/vfx/sky/bake_cloud_lattice2.py [--out assets/vfx/sky/cloud_lattice2.png]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "screenshots"))
import pngio  # noqa: E402

SIZE = 512
PCG_MUL = np.uint32(1664525)
PCG_INC = np.uint32(1013904223)
OUT = ROOT / "assets" / "vfx" / "sky" / "cloud_lattice2.png"


def pcg2d(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """hymn_pcg2d on uint32 arrays (wrapping arithmetic, same order of updates as the shader)."""
    x = x * PCG_MUL + PCG_INC
    y = y * PCG_MUL + PCG_INC
    x = x + y * PCG_MUL
    y = y + x * PCG_MUL
    x = x ^ (x >> np.uint32(16))
    y = y ^ (y >> np.uint32(16))
    x = x + y * PCG_MUL
    y = y + x * PCG_MUL
    x = x ^ (x >> np.uint32(16))
    y = y ^ (y >> np.uint32(16))
    return x, y


def cell_of(t: np.ndarray) -> np.ndarray:
    """Signed cell stored at texel t."""
    return np.where(t < SIZE // 2, t, t - SIZE)


def bake() -> np.ndarray:
    """(SIZE, SIZE) uint8 lattice indexed [ty, tx]: the shader's hash of cell (c(tx), c(ty))."""
    with np.errstate(over="ignore"):
        ty, tx = np.meshgrid(np.arange(SIZE), np.arange(SIZE), indexing="ij")
        cx = cell_of(tx).astype(np.int64).astype(np.uint32)
        cy = cell_of(ty).astype(np.int64).astype(np.uint32)
        h, _ = pcg2d(cx, cy)
    return np.rint(h.astype(np.float64) / 4294967295.0 * 255.0).astype(np.uint8)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    pngio.write(args.out, bake())
    print(f"wrote {args.out} ({SIZE}^2 L8, signed cells +-{SIZE // 2})")


if __name__ == "__main__":
    main()
