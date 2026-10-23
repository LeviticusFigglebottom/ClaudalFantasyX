#!/usr/bin/env python3
"""Sculpt preview: sphere-traces the head signed-distance field directly (dev tool, numpy only).

    python3 assets_src/characters/asha/sdf_preview.py out.png [--params asha] [--views 0,35,90]
            [--size 320] [--fov 14] [--dist 0.75]

This shows the full-resolution sculpt the normal/cavity bake sees, before the mesh samples it.
Clay shading with a warm key, cool fill and rim; eyeballs tinted (sclera, iris, pupil). It is a
fast look-dev aid, not a review render: reviews are Godot Forward+ captures (tools/screenshots).
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "base_body"))
sys.path.insert(0, str(HERE))

import bb_anatomy  # noqa: E402
import bb_params  # noqa: E402


def load_body(params_name: str) -> bb_anatomy.Body:
    if params_name.endswith(".json"):
        p = bb_params.load_params(path=params_name)
    elif (HERE / f"{params_name}_params.json").exists():
        p = bb_params.load_params(path=str(HERE / f"{params_name}_params.json"))
    else:
        p = bb_params.load_params(params_name)
    return bb_anatomy.Body(bb_params.Landmarks(p))


def head_sdf(body: bb_anatomy.Body, P: np.ndarray, with_eyes: bool = True) -> np.ndarray:
    d = body.regions["head"].sdf(P)
    t = body.regions["torso"].sdf(P)
    d = bb_anatomy.smin(t, d, body.k_head_neck)
    for pr in body.post:
        d = pr.apply(d, P)
    if with_eyes:
        for side in ("L", "R"):
            E = body.lm.side_pt("eye", side)
            d = np.minimum(d, np.linalg.norm(P - E, axis=1) - body.lm.eye_r)
    return d


LOOK = {  # name -> (landmark, x offset in h, z offset in h)
    "face": ("eye", None, -0.095),
    "eye": ("eye", 1.0, 0.0),
    "nose": ("nose_tip", 0.0, 0.0),
    "mouth": ("mouth", 0.0, 0.02),
    "ear": ("ear", 1.0, 0.0),
}


def render(body, yaw_deg: float, size: int, fov: float, dist: float, pitch_deg: float = 0.0,
           look: str = "face") -> np.ndarray:
    lm = body.lm
    name, xs_, dz = LOOK[look]
    P0 = lm.P(name)
    target = np.array([0.0 if xs_ is None else P0[0] * xs_, lm.P("eye")[1] if look == "face" else P0[1],
                       P0[2] + dz * lm.h])
    yaw, pitch = math.radians(yaw_deg), math.radians(pitch_deg)
    # yaw 0 = camera in front (-Y) looking +Y; positive yaw orbits toward the character's left (+X)
    fwd = np.array([-math.sin(yaw) * math.cos(pitch), math.cos(yaw) * math.cos(pitch), -math.sin(pitch)])
    eye = target - fwd * dist
    right = np.cross(fwd, np.array([0.0, 0.0, 1.0]))
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    th = math.tan(math.radians(fov) / 2)
    ys, xs = np.mgrid[0:size, 0:size]
    u = (xs + 0.5) / size * 2 - 1
    v = 1 - (ys + 0.5) / size * 2
    D = fwd[None, :] + (u.reshape(-1, 1) * th) * right[None, :] + (v.reshape(-1, 1) * th) * up[None, :]
    D /= np.linalg.norm(D, axis=1, keepdims=True)
    n = len(D)
    t = np.full(n, dist - 0.2)
    alive = np.ones(n, dtype=bool)
    hit = np.zeros(n, dtype=bool)
    for _ in range(90):
        idx = np.nonzero(alive)[0]
        if len(idx) == 0:
            break
        P = eye + D[idx] * t[idx, None]
        d = head_sdf(body, P)
        done = d < 2e-5
        hit[idx[done]] = True
        alive[idx[done]] = False
        t[idx] += np.maximum(d * 0.8, 1e-5) * (~done)
        far = t[idx] > dist + 0.3
        alive[idx[far]] = False
    P = eye + D * t[:, None]
    img = np.zeros((n, 3))
    bg = np.array([0.20, 0.21, 0.23])
    img[:] = bg
    hp = P[hit]
    eps = 2e-4
    g = np.zeros_like(hp)
    for i in range(3):
        e = np.zeros(3)
        e[i] = eps
        g[:, i] = head_sdf(body, hp + e) - head_sdf(body, hp - e)
    N = g / np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-12)
    key = np.array([-0.55, -0.6, 0.58])
    key /= np.linalg.norm(key)
    fill = np.array([0.7, -0.5, 0.1])
    fill /= np.linalg.norm(fill)
    rim = np.array([0.6, 0.75, 0.3])
    rim /= np.linalg.norm(rim)
    albedo = np.array([0.72, 0.52, 0.42])
    col = np.tile(albedo, (len(hp), 1))
    # eyes: points on the eyeball spheres
    r_e = lm.eye_r
    for side in ("L", "R"):
        E = lm.side_pt("eye", side)
        q = hp - E
        on = np.abs(np.linalg.norm(q, axis=1) - r_e) < 2e-4
        ang = np.degrees(np.arccos(np.clip(-q[:, 1] / np.maximum(np.linalg.norm(q, axis=1), 1e-9), -1, 1)))
        col[on] = np.array([0.8, 0.77, 0.72])
        col[on & (ang < 29)] = np.array([0.25, 0.15, 0.09])
        col[on & (ang < 11)] = np.array([0.02, 0.02, 0.02])
    nk = np.clip(N @ key, 0, 1)
    wrap = np.clip((N @ key + 0.25) / 1.25, 0, 1)
    shade = 0.85 * (0.7 * nk + 0.3 * wrap)[:, None] * np.array([1.0, 0.93, 0.85])
    shade += 0.22 * np.clip(N @ fill, 0, 1)[:, None] * np.array([0.8, 0.88, 1.0])
    shade += 0.35 * np.clip(N @ rim, 0, 1)[:, None] ** 2 * np.array([1.0, 0.85, 0.6])
    shade += 0.08
    V = -D[hit]
    Hk = (V + key) / np.linalg.norm(V + key, axis=1, keepdims=True)
    spec = 0.12 * np.clip(np.sum(N * Hk, axis=1), 0, 1) ** 40
    img[hit] = col * shade + spec[:, None]
    img = np.clip(img, 0, 1) ** (1 / 2.2)
    return (img.reshape(size, size, 3) * 255).astype(np.uint8)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--params", default="asha")
    ap.add_argument("--views", default="0,35,90")
    ap.add_argument("--size", type=int, default=320)
    ap.add_argument("--fov", type=float, default=22.0)
    ap.add_argument("--dist", type=float, default=0.75)
    ap.add_argument("--pitch", type=float, default=0.0)
    ap.add_argument("--look", default="face", choices=sorted(LOOK))
    args = ap.parse_args()
    body = load_body(args.params)
    tiles = [render(body, float(y), args.size, args.fov, args.dist, args.pitch, args.look)
             for y in args.views.split(",")]
    Image.fromarray(np.concatenate(tiles, axis=1)).save(args.out)


if __name__ == "__main__":
    main()
