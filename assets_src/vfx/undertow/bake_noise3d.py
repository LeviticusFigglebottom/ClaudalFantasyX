"""Bake the Undertow's 3D noise lattice (M1-RND-10) to assets/vfx/undertow/undertow_noise3d.png.

The raymarched body used to hash every lattice corner of its value noise per sample (PCG3D, eight
hashes per lookup, about 180 per march step). This bakes the same hash into a tileable SIZE^3 RGBA8
lattice: texel (x, y, z) holds hymn_pcg3d(uvec3(x, y, z)) (game/shaders/include/common.gdshaderinc)
as R, G, B (its three outputs), and A = hymn_pcg3d(uvec3(x + SIZE, y, z)).x, each scaled to 0..255.
For cells inside [0, SIZE)^3 the baked noise is the shader's own noise (to 8 bits); beyond that it
repeats every SIZE cells. undertow_body.gdshaderinc samples it with one trilinear fetch at a
quintic-remapped coordinate, which is quintic value noise again.

The PNG is a slice atlas for Godot's 3D texture importer: SLICES_X x SLICES_Y slices of SIZE x SIZE,
slice z at column z % SLICES_X, row z // SLICES_X (the importer's order; the unit test checks it).

Usage: python3 assets_src/vfx/undertow/bake_noise3d.py [--out assets/vfx/undertow/undertow_noise3d.png]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "screenshots"))
import pngio  # noqa: E402

SIZE = 64
SLICES_X = 8
SLICES_Y = SIZE // SLICES_X
PCG_MUL = np.uint32(1664525)
PCG_INC = np.uint32(1013904223)
OUT = ROOT / "assets" / "vfx" / "undertow" / "undertow_noise3d.png"


def pcg3d(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """hymn_pcg3d on uint32 arrays (wrapping arithmetic, same order of updates as the shader)."""
    x = x * PCG_MUL + PCG_INC
    y = y * PCG_MUL + PCG_INC
    z = z * PCG_MUL + PCG_INC
    x = x + y * z
    y = y + z * x
    z = z + x * y
    x = x ^ (x >> np.uint32(16))
    y = y ^ (y >> np.uint32(16))
    z = z ^ (z >> np.uint32(16))
    x = x + y * z
    y = y + z * x
    z = z + x * y
    return x, y, z


def to_byte(h: np.ndarray) -> np.ndarray:
    """Hash -> nearest 8-bit level of the shader's float(h) / 4294967295."""
    return np.rint(h.astype(np.float64) / 4294967295.0 * 255.0).astype(np.uint8)


def bake() -> np.ndarray:
    """(SIZE, SIZE, SIZE, 4) uint8 lattice indexed [z, y, x, channel]."""
    with np.errstate(over="ignore"):
        z, y, x = np.meshgrid(*(np.arange(SIZE, dtype=np.uint32),) * 3, indexing="ij")
        r, g, b = pcg3d(x, y, z)
        a, _, _ = pcg3d(x + np.uint32(SIZE), y, z)
    return np.stack([to_byte(r), to_byte(g), to_byte(b), to_byte(a)], axis=-1)


def atlas(lattice: np.ndarray) -> np.ndarray:
    img = np.zeros((SLICES_Y * SIZE, SLICES_X * SIZE, 4), np.uint8)
    for z in range(SIZE):
        row, col = divmod(z, SLICES_X)
        img[row * SIZE : (row + 1) * SIZE, col * SIZE : (col + 1) * SIZE] = lattice[z]
    return img


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    pngio.write(args.out, atlas(bake()))
    print(f"wrote {args.out} ({SIZE}^3 RGBA8, {SLICES_X}x{SLICES_Y} slices)")


if __name__ == "__main__":
    main()
