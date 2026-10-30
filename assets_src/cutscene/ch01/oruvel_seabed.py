#!/usr/bin/env python3
"""Oruvel's seabed under the net pen (M3-CIN-1232, Ch1's dive: U10 looks up, U11 down into the dark).

The UnderwaterRig's post absorbs over the depth buffer's path, so over open water (no floor) it takes its 400 m
path and wipes every transparent in front of it, the sinking motes included. This floor gives U11 a bottom: silt
sand in long current ripples over low dunes, with a scatter of half-buried rock lumps, 40 x 40 m, generated from a
fixed seed (no asset pack, no scan). It sits about 10 m under the surface, where the water takes nearly all of its
colour; what matters is its depth and its broken silhouette.

    python3 assets_src/cutscene/ch01/oruvel_seabed.py [--out assets/cutscene/ch01/oruvel_seabed.glb] [--check]
    blender --background --factory-startup --python assets_src/cutscene/ch01/oruvel_seabed.py -- [same args]

The second form is tools/dev/blender_builds.json's job (its runs start with Blender; Blender's Python has numpy).
The output is the same either way: nothing here uses Blender's API.

--check rebuilds in memory and fails when the committed file differs.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "assets/cutscene/ch01/oruvel_seabed.glb"

SEED = 1232
SIZE_M = 40.0
CELLS = 96
# Sand: long ripples across the current, low dunes under them.
RIPPLE_M = 0.9
RIPPLE_AMP_M = 0.05
DUNE_AMP_M = 0.45
DUNE_OCTAVES = 3
# Rocks: half-buried lumps, rough-edged.
ROCKS = 14
ROCK_RADIUS_M = (0.8, 2.6)
ROCK_HEIGHT_M = (0.4, 1.4)
ROCK_ROUGH = 0.35
SAND_RGB = (0.36, 0.33, 0.27)
ROCK_RGB = (0.16, 0.17, 0.16)


def _value_noise(rng: np.random.Generator, xs: np.ndarray, zs: np.ndarray, cell_m: float) -> np.ndarray:
    """Smooth value noise on a lattice of cell_m, in [-1, 1]."""
    n = int(SIZE_M / cell_m) + 3
    lattice = rng.uniform(-1.0, 1.0, (n, n))
    u = (xs + SIZE_M / 2) / cell_m
    v = (zs + SIZE_M / 2) / cell_m
    i = np.floor(u).astype(int)
    j = np.floor(v).astype(int)
    fu = u - i
    fv = v - j
    su = fu * fu * (3 - 2 * fu)
    sv = fv * fv * (3 - 2 * fv)
    a = lattice[i, j]
    b = lattice[i + 1, j]
    c = lattice[i, j + 1]
    d = lattice[i + 1, j + 1]
    return (a * (1 - su) + b * su) * (1 - sv) + (c * (1 - su) + d * su) * sv


def build() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Positions, normals, colours and triangle indices of the floor."""
    rng = np.random.default_rng(SEED)
    ax = np.linspace(-SIZE_M / 2, SIZE_M / 2, CELLS + 1)
    xs, zs = np.meshgrid(ax, ax, indexing="ij")
    height = np.zeros_like(xs)
    for octave in range(DUNE_OCTAVES):
        height += DUNE_AMP_M / (2**octave) * _value_noise(rng, xs, zs, 12.0 / (2**octave))
    bend = 1.5 * _value_noise(rng, xs, zs, 9.0)
    height += RIPPLE_AMP_M * np.sin(2 * np.pi * (xs * 0.94 + zs * 0.34 + bend) / RIPPLE_M)
    rock = np.zeros_like(xs)
    for _ in range(ROCKS):
        cx, cz = rng.uniform(-SIZE_M / 2 + 3, SIZE_M / 2 - 3, 2)
        r = rng.uniform(*ROCK_RADIUS_M)
        h = rng.uniform(*ROCK_HEIGHT_M)
        d2 = ((xs - cx) ** 2 + (zs - cz) ** 2) / (r * r)
        rough = 1.0 + ROCK_ROUGH * _value_noise(rng, xs, zs, 0.7)
        rock = np.maximum(rock, h * np.clip(1.0 - d2 * rough, 0.0, None) ** 0.6)
    height += rock
    pos = np.stack([xs, height, zs], axis=-1).reshape(-1, 3).astype(np.float32)
    gx, gz = np.gradient(height, ax, ax)
    nrm = np.stack([-gx, np.ones_like(gx), -gz], axis=-1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    nrm = nrm.reshape(-1, 3).astype(np.float32)
    mix = np.clip(rock / 0.25, 0.0, 1.0).reshape(-1, 1)
    col = (np.array(SAND_RGB) * (1 - mix) + np.array(ROCK_RGB) * mix).astype(np.float32)
    col = np.concatenate([col, np.ones((col.shape[0], 1), np.float32)], axis=1)
    idx = []
    w = CELLS + 1
    for i in range(CELLS):
        for j in range(CELLS):
            a, b, c, d = i * w + j, (i + 1) * w + j, i * w + j + 1, (i + 1) * w + j + 1
            idx += [a, c, b, b, c, d]
    return pos, nrm, col, np.array(idx, dtype=np.uint32)


def glb(pos: np.ndarray, nrm: np.ndarray, col: np.ndarray, idx: np.ndarray) -> bytes:
    blobs = [pos.tobytes(), nrm.tobytes(), col.tobytes(), idx.tobytes()]
    views, offset = [], 0
    for i, b in enumerate(blobs):
        views.append({"buffer": 0, "byteOffset": offset, "byteLength": len(b), "target": 34963 if i == 3 else 34962})
        offset += (len(b) + 3) // 4 * 4
    binary = b"".join(b + b"\0" * ((4 - len(b) % 4) % 4) for b in blobs)
    doc = {
        "asset": {"version": "2.0", "generator": "assets_src/cutscene/ch01/oruvel_seabed.py"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"name": "Seabed", "mesh": 0}],
        "meshes": [
            {
                "name": "oruvel_seabed",
                "primitives": [
                    {"attributes": {"POSITION": 0, "NORMAL": 1, "COLOR_0": 2}, "indices": 3, "material": 0}
                ],
            }
        ],
        "materials": [
            {
                "name": "seabed_silt",
                "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0, "roughnessFactor": 1},
            }
        ],
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": views,
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": len(pos),
                "type": "VEC3",
                "min": pos.min(axis=0).tolist(),
                "max": pos.max(axis=0).tolist(),
            },
            {"bufferView": 1, "componentType": 5126, "count": len(nrm), "type": "VEC3"},
            {"bufferView": 2, "componentType": 5126, "count": len(col), "type": "VEC4"},
            {"bufferView": 3, "componentType": 5125, "count": len(idx), "type": "SCALAR"},
        ],
    }
    js = json.dumps(doc, separators=(",", ":"), sort_keys=True).encode()
    js += b" " * ((4 - len(js) % 4) % 4)
    body = struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(binary), 0x004E4942) + binary
    return struct.pack("<III", 0x46546C67, 2, 12 + len(body)) + body


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--check", action="store_true")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    a = ap.parse_args(argv)
    data = glb(*build())
    if a.check:
        ok = a.out.exists() and a.out.read_bytes() == data
        print("oruvel_seabed --check: %s" % ("ok" if ok else "differs (rebuild it)"))
        return 0 if ok else 1
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_bytes(data)
    print("wrote %s (%d bytes)" % (a.out.relative_to(ROOT) if a.out.is_absolute() else a.out, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
