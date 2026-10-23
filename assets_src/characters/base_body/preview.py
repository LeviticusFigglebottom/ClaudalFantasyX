#!/usr/bin/env python3
"""Quick software preview of a base-body mesh dump (dev tool, not part of the asset build).

    python3 assets_src/characters/base_body/preview.py <mesh.npz> <out.png> [--views front,q34,side,back]
                                                       [--zoom head] [--size 360]

Renders an orthographic, flat-lit grey clay with a z-buffer and wireframe overlay option.
The .npz comes from `build.py ... --dump-npz <path>` (keys V, F). Reference renders for review
are Godot's (tools/screenshots); this exists to iterate on proportions in seconds.
"""
from __future__ import annotations

import argparse
import math

import numpy as np
from PIL import Image


def rot_z(deg: float) -> np.ndarray:
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def render(V: np.ndarray, T: np.ndarray, yaw: float, size: int, box: tuple, wire: bool) -> np.ndarray:
    """Camera looks along +Y (at the character's front when yaw = 0)."""
    R = rot_z(yaw)
    P = V @ R.T
    x0, x1, z0, z1 = box
    W = size
    Hh = int(size * (z1 - z0) / (x1 - x0))
    sx = (P[:, 0] - x0) / (x1 - x0) * (W - 1)
    sy = (z1 - P[:, 2]) / (z1 - z0) * (Hh - 1)
    depth = P[:, 1]
    img = np.full((Hh, W), 0.0)
    zb = np.full((Hh, W), np.inf)
    a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
    fn = np.cross(b - a, c - a)
    vn = np.zeros_like(P)
    for q in range(3):
        np.add.at(vn, T[:, q], fn)
    vn /= np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-12)
    L1 = np.array([-0.45, -0.75, 0.5])
    L1 /= np.linalg.norm(L1)
    vshade = 0.12 + 0.68 * np.clip(vn @ L1, 0, 1) + 0.2 * np.clip(-vn[:, 1], 0, 1)
    for ti in range(len(T)):
        i, j, k = T[ti]
        xs = np.array([sx[i], sx[j], sx[k]])
        ys = np.array([sy[i], sy[j], sy[k]])
        xmin, xmax = int(max(math.floor(xs.min()), 0)), int(min(math.ceil(xs.max()), W - 1))
        ymin, ymax = int(max(math.floor(ys.min()), 0)), int(min(math.ceil(ys.max()), Hh - 1))
        if xmin > xmax or ymin > ymax:
            continue
        gx, gy = np.meshgrid(np.arange(xmin, xmax + 1), np.arange(ymin, ymax + 1))
        d = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
        if abs(d) < 1e-12:
            continue
        w0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / d
        w1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / d
        w2 = 1 - w0 - w1
        m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not m.any():
            continue
        z = w0 * depth[i] + w1 * depth[j] + w2 * depth[k]
        sub = zb[ymin:ymax + 1, xmin:xmax + 1]
        upd = m & (z < sub)
        sub[upd] = z[upd]
        val = w0 * vshade[i] + w1 * vshade[j] + w2 * vshade[k]
        if wire:
            e = np.minimum(np.minimum(w0, w1), w2)
            val = np.where(e < 0.06, val * 0.55, val)
        img[ymin:ymax + 1, xmin:xmax + 1][upd] = val[upd]
    bg = np.isinf(zb)
    out = np.clip(img, 0, 1)
    out[bg] = 0.32
    return (out * 255).astype(np.uint8)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("npz")
    ap.add_argument("out")
    ap.add_argument("--views", default="0,45,90,180")
    ap.add_argument("--zoom", default="body", choices=["body", "head", "face", "hand", "torso", "foot"])
    ap.add_argument("--size", type=int, default=300)
    ap.add_argument("--wire", action="store_true")
    args = ap.parse_args()
    data = np.load(args.npz)
    V, F = data["V"], data["F"]
    if F.shape[1] == 4:
        T = np.concatenate([F[:, [0, 1, 2]], F[:, [0, 2, 3]]])
    else:
        T = F
    if "EV" in data:
        off = len(V)
        V = np.concatenate([V, data["EV"]])
        T = np.concatenate([T, data["ET"] + off])
    zmax = V[:, 2].max()
    if args.zoom == "body":
        half = zmax * 0.32
        box = (-half, half, -0.02, zmax + 0.02)
    elif args.zoom == "head":
        hh = zmax / 7.3
        box = (-0.75 * hh, 0.75 * hh, zmax - 1.3 * hh, zmax + 0.05 * hh)
    elif args.zoom == "face":
        hh = zmax / 7.3
        box = (-0.42 * hh, 0.42 * hh, zmax - 1.04 * hh, zmax - 0.2 * hh)
    elif args.zoom == "torso":
        hh = zmax / 7.3
        box = (-1.6 * hh, 1.6 * hh, zmax - 4.4 * hh, zmax - 0.8 * hh)
    elif args.zoom == "foot":
        box = (-0.25, 0.25, -0.01, 0.25)
    else:
        idx = np.argmax(V[:, 0])
        c = V[idx]
        box = (c[0] - 0.22, c[0] + 0.05, c[2] - 0.12, c[2] + 0.15)
    tiles = [render(V, T, float(y), args.size, box, args.wire) for y in args.views.split(",")]
    Image.fromarray(np.concatenate(tiles, axis=1)).save(args.out)


if __name__ == "__main__":
    main()
