#!/usr/bin/env python3
"""Writes tests/fixtures/import/import_probe.glb, the M1-ART-02 post-import test asset.

Pure Python (no Blender), deterministic: the same bytes on every run. tools/tests/test_post_import.py
checks the committed file equals this output. The asset is a small "kit piece" that follows the
ADR 0005 naming: a visible mesh, its `-lod1`, a `-col` collision proxy and a `-noimp` helper, plus a
node that declares itself PLACEHOLDER through glTF node extras (the Haluna kit's convention).
Its .import runs the Haluna kit post-import script, so tests/unit/test_post_import.gd can assert
what the real import pipeline produced (materials, LOD ranges, collision, PLACEHOLDER metadata).

Usage: python3 tests/fixtures/import/build_import_probe.py [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

OUT = Path(__file__).resolve().parent / "import_probe.glb"
PLACEHOLDER_NOTE = "PLACEHOLDER: M1-ART-02 import test fixture, never placed in a level"

# name -> (half extents x, y, z), centre y, material (or None)
PARTS: list[tuple[str, tuple[float, float, float], float, str | None]] = [
    ("probe_post", (0.25, 1.0, 0.25), 1.0, "kit_timber"),
    ("probe_post-lod1", (0.25, 1.0, 0.25), 1.0, "kit_timber"),
    ("probe_post-col", (0.3, 1.0, 0.3), 1.0, None),
    ("probe_marker-noimp", (0.05, 0.05, 0.05), 2.2, None),
    ("probe_slab", (1.0, 0.1, 0.5), 0.1, "kit_lashing"),
]
PLACEHOLDER_PARTS = {"probe_slab"}

# The six faces of a box: normal, then the two in-plane axes (u, v) with u x v = normal.
FACES = [
    ((1, 0, 0), (0, 0, -1), (0, 1, 0)),
    ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
    ((0, 1, 0), (1, 0, 0), (0, 0, -1)),
    ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
    ((0, 0, 1), (1, 0, 0), (0, 1, 0)),
    ((0, 0, -1), (-1, 0, 0), (0, 1, 0)),
]


def box(half: tuple[float, float, float], cy: float) -> tuple[list[float], list[float], list[float], list[int]]:
    pos: list[float] = []
    nrm: list[float] = []
    uv: list[float] = []
    idx: list[int] = []
    for n, u, v in FACES:
        base = len(pos) // 3
        for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            p = [n[i] + su * u[i] + sv * v[i] for i in range(3)]
            pos += [p[0] * half[0], p[1] * half[1] + cy, p[2] * half[2]]
            nrm += [float(c) for c in n]
            uv += [(su + 1) * 0.5, (1 - sv) * 0.5]
        idx += [base, base + 1, base + 2, base, base + 2, base + 3]
    return pos, nrm, uv, idx


def build() -> bytes:
    blob = bytearray()
    views: list[dict] = []
    accessors: list[dict] = []

    def add(data: bytes, target: int) -> int:
        while len(blob) % 4:
            blob.append(0)
        views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(data), "target": target})
        blob.extend(data)
        return len(views) - 1

    def acc(values: list, kind: str, comp: int, fmt: str, target: int, minmax: bool = False) -> int:
        view = add(struct.pack("<%d%s" % (len(values), fmt), *values), target)
        width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3}[kind]
        a: dict = {"bufferView": view, "componentType": comp, "count": len(values) // width, "type": kind}
        if minmax:
            a["min"] = [min(values[i::width]) for i in range(width)]
            a["max"] = [max(values[i::width]) for i in range(width)]
        accessors.append(a)
        return len(accessors) - 1

    materials: list[str] = []
    meshes: list[dict] = []
    nodes: list[dict] = []
    for name, half, cy, mat in PARTS:
        pos, nrm, uv, idx = box(half, cy)
        prim: dict = {
            "attributes": {
                "POSITION": acc(pos, "VEC3", 5126, "f", 34962, True),
                "NORMAL": acc(nrm, "VEC3", 5126, "f", 34962),
                "TEXCOORD_0": acc(uv, "VEC2", 5126, "f", 34962),
            },
            "indices": acc(idx, "SCALAR", 5123, "H", 34963),
        }
        if mat is not None:
            if mat not in materials:
                materials.append(mat)
            prim["material"] = materials.index(mat)
        meshes.append({"name": name, "primitives": [prim]})
        node: dict = {"name": name, "mesh": len(meshes) - 1}
        if name in PLACEHOLDER_PARTS:
            node["extras"] = {"placeholder": PLACEHOLDER_NOTE}
        nodes.append(node)

    gltf = {
        "asset": {"version": "2.0", "generator": "hymn build_import_probe.py (M1-ART-02)"},
        "scene": 0,
        "scenes": [{"name": "Scene", "nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": meshes,
        "materials": [
            {"name": m, "pbrMetallicRoughness": {"baseColorFactor": [0.5, 0.5, 0.5, 1.0], "metallicFactor": 0.0}}
            for m in materials
        ],
        "accessors": accessors,
        "bufferViews": views,
        "buffers": [{"byteLength": len(blob)}],
    }
    js = json.dumps(gltf, separators=(",", ":"), sort_keys=True).encode()
    js += b" " * (-len(js) % 4)
    while len(blob) % 4:
        blob.append(0)
    total = 12 + 8 + len(js) + 8 + len(blob)
    out = struct.pack("<III", 0x46546C67, 2, total)
    out += struct.pack("<II", len(js), 0x4E4F534A) + js
    out += struct.pack("<II", len(blob), 0x004E4942) + bytes(blob)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    args.out.write_bytes(build())
    print(f"wrote {args.out} ({args.out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
