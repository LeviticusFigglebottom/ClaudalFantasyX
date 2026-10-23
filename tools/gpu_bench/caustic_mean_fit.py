"""Fit the mean of the procedural caustic pattern against line width (M1-RND-08).

game/shaders/water/water_caustics.gdshaderinc subtracts hymn_caustic_mean(width, layers) so caustics
only redistribute light. This is a numpy replica of hymn_caustic() (same PCG2D cell hash, quintic
value noise, animated Worley edge, warps, union/product combination and modulation) that samples it
over random positions and times at the widths the water shader produces for 0.25-8 m of water, and
prints the least-squares line to paste into HYMN_CAUSTIC_MEAN{1,2}_{A,B}.

Usage: python tools/gpu_bench/caustic_mean_fit.py [--samples 400000]
Keep it in step with the include: any change to the pattern needs a refit.
"""

from __future__ import annotations

import argparse

import numpy as np

PCG_MUL = np.uint32(1664525)
PCG_INC = np.uint32(1013904223)
TAU = 6.283185307179586
ROT2 = np.array([[0.8, -0.6], [0.6, 0.8]])  # HYMN_FBM_ROT2 = mat2(vec2(0.8, 0.6), vec2(-0.6, 0.8))
# Water shader defaults (water_surface_body.gdshaderinc): width + blur * depth * (1 + depth / falloff).
WIDTH, BLUR, FALLOFF = 0.06, 0.02, 6.0
DEPTHS_M = [0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0]
# water_caustics.gdshaderinc constants.
JITTER, WARP, WARP_FINE, WARP_FINE_SCALE = 0.42, 0.9, 0.35, 1.7
L2_SCALE, L2_OFFSET, WARP2_OFFSET = 1.618, (13.7, 7.3), 31.7
UNION, KNOT = 0.6, 2.0
MOD_SCALE, MOD_OFFSET, MOD = 0.13, (7.1, -3.3), 0.5
WIDTH_SCALE, WIDTH_OFFSET, WIDTH_VAR = 0.21, (-4.7, 9.9), 0.4


def pcg2d(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    with np.errstate(over="ignore"):
        x = x * PCG_MUL + PCG_INC
        y = y * PCG_MUL + PCG_INC
        x = x + y * PCG_MUL
        y = y + x * PCG_MUL
        x ^= x >> np.uint32(16)
        y ^= y >> np.uint32(16)
        x = x + y * PCG_MUL
        y = y + x * PCG_MUL
        x ^= x >> np.uint32(16)
        y ^= y >> np.uint32(16)
    return x, y


def hash_cell22(cx: np.ndarray, cy: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x, y = pcg2d(cx.astype(np.int64).astype(np.uint32), cy.astype(np.int64).astype(np.uint32))
    return x.astype(np.float64) / 4294967295.0, y.astype(np.float64) / 4294967295.0


def value_noise2(px: np.ndarray, py: np.ndarray) -> np.ndarray:
    ix, iy = np.floor(px), np.floor(py)
    fx, fy = px - ix, py - iy
    ux = fx**3 * (fx * (fx * 6 - 15) + 10)
    uy = fy**3 * (fy * (fy * 6 - 15) + 10)
    n00 = hash_cell22(ix, iy)[0]
    n10 = hash_cell22(ix + 1, iy)[0]
    n01 = hash_cell22(ix, iy + 1)[0]
    n11 = hash_cell22(ix + 1, iy + 1)[0]
    return n00 + (n10 - n00) * ux + (n01 - n00) * uy + (n00 - n10 - n01 + n11) * ux * uy


def edge(px: np.ndarray, py: np.ndarray, t: np.ndarray) -> np.ndarray:
    cx, cy = np.floor(px), np.floor(py)
    fx, fy = px - cx, py - cy
    f1 = np.full(px.shape, 8.0)
    f2 = np.full(px.shape, 8.0)
    for oy in (-1, 0, 1):
        for ox in (-1, 0, 1):
            hx, hy = hash_cell22(cx + ox, cy + oy)
            a = TAU * hx + t * (0.6 + 0.8 * hy)
            d = (ox + 0.5 + JITTER * np.cos(a) - fx) ** 2 + (oy + 0.5 + JITTER * np.sin(a) - fy) ** 2
            f2 = np.where(d < f1, f1, np.where(d < f2, d, f2))
            f1 = np.minimum(f1, d)
    return np.sqrt(f2) - np.sqrt(f1)


def smoothstep(e0: float, e1: np.ndarray, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def warp(px: np.ndarray, py: np.ndarray, t: np.ndarray, ofs: float) -> tuple[np.ndarray, np.ndarray]:
    cx = value_noise2(px * 0.5 + t * 0.1 + ofs, py * 0.5 + t * 0.1 + ofs)
    cy = value_noise2(px * 0.5 - t * 0.1 + 5.2 + ofs, py * 0.5 - t * 0.1 + 5.2 + ofs)
    qx, qy = px * WARP_FINE_SCALE, py * WARP_FINE_SCALE
    fx = value_noise2(qx + t * 0.17 + ofs + 2.3, qy + t * 0.17 + ofs + 2.3)
    fy = value_noise2(qx - t * 0.17 + 8.1 + ofs, qy - t * 0.17 + 8.1 + ofs)
    return px + WARP * (cx - 0.5) + WARP_FINE * (fx - 0.5), py + WARP * (cy - 0.5) + WARP_FINE * (fy - 0.5)


def caustic(px: np.ndarray, py: np.ndarray, t: np.ndarray, width: float, layers: int) -> np.ndarray:
    m = value_noise2(px * MOD_SCALE + MOD_OFFSET[0], py * MOD_SCALE + MOD_OFFSET[1])
    w = width * (
        1 - WIDTH_VAR + 2 * WIDTH_VAR * value_noise2(px * WIDTH_SCALE + WIDTH_OFFSET[0], py * WIDTH_SCALE + WIDTH_OFFSET[1])
    )
    ax, ay = warp(px, py, t, 0.0)
    l1 = (1 - smoothstep(0.0, w, edge(ax, ay, t))) ** 2
    c = l1
    if layers > 1:
        q = ROT2 @ np.stack([px, py]) * L2_SCALE
        bx, by = warp(q[0] + L2_OFFSET[0], q[1] + L2_OFFSET[1], t * 1.3, WARP2_OFFSET)
        l2 = (1 - smoothstep(0.0, w * L2_SCALE, edge(bx, by, t * 1.3))) ** 2
        c = UNION * np.maximum(l1, l2) + KNOT * l1 * l2
    return c * (1 - MOD + 2 * MOD * m)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=400000)
    args = ap.parse_args()
    rng = np.random.default_rng(1)
    widths = [WIDTH + BLUR * d * (1 + d / FALLOFF) for d in DEPTHS_M]
    for layers in (2, 1):
        means = []
        for w in widths:
            px, py, t = (rng.uniform(0, 400, args.samples) for _ in range(3))
            means.append(float(caustic(px, py, t, w, layers).mean()))
        b, a = np.polyfit(widths, means, 1)
        err = max(abs(a + b * w - m) for w, m in zip(widths, means))
        print(f"HYMN_CAUSTIC_MEAN{layers}_A {a:.4f}  HYMN_CAUSTIC_MEAN{layers}_B {b:.4f}  (max error {err:.4f})")


if __name__ == "__main__":
    main()
