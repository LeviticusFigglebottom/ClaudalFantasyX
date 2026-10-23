"""GLB reading and the morph-normal pass for Asha's head (no bpy; numpy only). M1-CHR-07.

Why this exists: CHR-03 exported the face shapes without morph-target normals, because Blender's
exporter writes normals for every shape key or none, and all 40 would push `asha.glb` past the
5 MB cap (ADR 0005). Without normals, a shape that only bunches smooth skin (the cheek raise, the
lid squint, the smile's cheek) shades exactly as at rest, so on screen it all but vanishes. Only
silhouettes and the lid margins move. That was most of the M1-CHR-07 "smile driver gap".

`add_morph_normals` runs after the export. For the chosen shapes on the chosen primitive, it
computes the normal change of the welded surface (area-weighted face normals, welded by position
so UV seams don't crease) and adds it to the exported normal of each split vertex. It drops deltas
under `min_delta` and stores the rest as a sparse accessor (indices + values only). Every other
target keeps no NORMAL, which Godot reads as an unchanged normal. The pass is deterministic: fixed
order, float32 storage, no randomness.

`read_glb`, `accessor` and `head_targets` are shared with tools/tests/test_asha_face_drive.py.
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

import numpy as np

GLB_MAGIC = 0x46546C67
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942
COMPONENTS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
DTYPES = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
FLOAT = 5126
UINT16 = 5123
UINT32 = 5125


def read_glb(path: Path) -> tuple[dict, bytearray]:
    data = Path(path).read_bytes()
    magic, _version, _total = struct.unpack("<III", data[:12])
    if magic != GLB_MAGIC:
        raise ValueError(f"{path}: not a GLB")
    jlen, jkind = struct.unpack("<II", data[12:20])
    if jkind != CHUNK_JSON:
        raise ValueError(f"{path}: first chunk is not JSON")
    js = json.loads(data[20:20 + jlen])
    off = 20 + jlen
    blen, bkind = struct.unpack("<II", data[off:off + 8])
    if bkind != CHUNK_BIN:
        raise ValueError(f"{path}: second chunk is not BIN")
    return js, bytearray(data[off + 8:off + 8 + blen])


def write_glb(path: Path, js: dict, bin_: bytes) -> None:
    jtxt = json.dumps(js, separators=(",", ":")).encode("utf-8")
    jtxt += b" " * (-len(jtxt) % 4)
    b = bytes(bin_) + b"\0" * (-len(bin_) % 4)
    total = 12 + 8 + len(jtxt) + 8 + len(b)
    out = struct.pack("<III", GLB_MAGIC, 2, total) + struct.pack("<II", len(jtxt), CHUNK_JSON) + jtxt
    out += struct.pack("<II", len(b), CHUNK_BIN) + b
    Path(path).write_bytes(out)


def _view(js: dict, bin_: bytes, view: int, byte_offset: int, count: int, ctype: int, ncomp: int) -> np.ndarray:
    bv = js["bufferViews"][view]
    if bv.get("byteStride") and bv["byteStride"] != ncomp * np.dtype(DTYPES[ctype]).itemsize:
        raise ValueError("interleaved buffer views are not supported")
    start = bv.get("byteOffset", 0) + byte_offset
    return np.frombuffer(bin_, dtype=DTYPES[ctype], count=count * ncomp, offset=start)


def accessor(js: dict, bin_: bytes, index: int) -> np.ndarray:
    """Decoded accessor (sparse substitution applied) as (count, ncomp), or (count,) for SCALAR."""
    a = js["accessors"][index]
    n = COMPONENTS[a["type"]]
    if "bufferView" in a:
        arr = _view(js, bin_, a["bufferView"], a.get("byteOffset", 0), a["count"], a["componentType"], n).copy()
    else:
        arr = np.zeros(a["count"] * n, dtype=DTYPES[a["componentType"]])
    arr = arr.reshape(a["count"], n)
    if "sparse" in a:
        s = a["sparse"]
        idx = _view(js, bin_, s["indices"]["bufferView"], s["indices"].get("byteOffset", 0), s["count"],
                    s["indices"]["componentType"], 1)
        val = _view(js, bin_, s["values"]["bufferView"], s["values"].get("byteOffset", 0), s["count"],
                    a["componentType"], n)
        arr[idx.astype(np.int64)] = val.reshape(-1, n)
    return arr if n > 1 else arr[:, 0]


def mesh_by_name(js: dict, name: str) -> dict:
    for m in js["meshes"]:
        if m["name"] == name:
            return m
    raise KeyError(name)


def primitive_by_material(js: dict, mesh: dict, material: str) -> tuple[int, dict]:
    for i, p in enumerate(mesh["primitives"]):
        if js["materials"][p["material"]]["name"] == material:
            return i, p
    raise KeyError(material)


def head_targets(js: dict, bin_: bytes, mesh: str = "Head", material: str = "skin_head") -> dict:
    """{"P": rest positions, "N": rest normals, "F": triangles, "names": [...],
    "D": {name: position delta}, "DN": {name: normal delta or None}} of one primitive."""
    m = mesh_by_name(js, mesh)
    _, p = primitive_by_material(js, m, material)
    names = m.get("extras", {}).get("targetNames", [])
    out = {"P": accessor(js, bin_, p["attributes"]["POSITION"]).astype(np.float64),
           "N": accessor(js, bin_, p["attributes"]["NORMAL"]).astype(np.float64),
           "F": accessor(js, bin_, p["indices"]).astype(np.int64).reshape(-1, 3),
           "names": names, "D": {}, "DN": {}}
    for name, t in zip(names, p.get("targets", [])):
        out["D"][name] = accessor(js, bin_, t["POSITION"]).astype(np.float64)
        out["DN"][name] = accessor(js, bin_, t["NORMAL"]).astype(np.float64) if "NORMAL" in t else None
    return out


def joint_positions(js: dict, bin_: bytes, names: list[str]) -> dict:
    """Bind-pose world positions of skin joints, from the inverse bind matrices."""
    out = {}
    for skin in js.get("skins", []):
        ibm = accessor(js, bin_, skin["inverseBindMatrices"]).reshape(-1, 4, 4)
        for k, node in enumerate(skin["joints"]):
            nm = js["nodes"][node].get("name")
            if nm in names and nm not in out:
                M = np.linalg.inv(ibm[k].astype(np.float64).T)  # glTF matrices are column-major
                out[nm] = M[:3, 3]
    return out


# ---------------------------------------------------------------------------------------------
def weld(P: np.ndarray, quantum: float = 1e-6) -> np.ndarray:
    """Weld id per vertex: vertices at the same position (UV / material splits) share one id."""
    q = np.round(P / quantum).astype(np.int64)
    _, inv = np.unique(q, axis=0, return_inverse=True)
    return inv.reshape(-1)


def welded_normals(P: np.ndarray, F: np.ndarray, wid: np.ndarray) -> np.ndarray:
    """Area-weighted vertex normals over the welded surface, scattered back to split vertices."""
    a, b, c = P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]
    fn = np.cross(b - a, c - a)
    acc = np.zeros((int(wid.max()) + 1, 3))
    for k in range(3):
        np.add.at(acc, wid[F[:, k]], fn)
    ln = np.linalg.norm(acc, axis=1, keepdims=True)
    acc = acc / np.maximum(ln, 1e-20)
    return acc[wid]


def normal_deltas(P: np.ndarray, N: np.ndarray, F: np.ndarray, D: np.ndarray, wid: np.ndarray,
                  base: np.ndarray, min_delta: float) -> np.ndarray:
    """Morph NORMAL delta for one target: the welded surface's normal change, added to the
    exported normal N (which may be custom), renormalised. Deltas under min_delta are zeroed."""
    moved = np.linalg.norm(D, axis=1) > 0
    if not moved.any():
        return np.zeros_like(N)
    dn = welded_normals(P + D, F, wid) - base
    n2 = N + dn
    n2 /= np.maximum(np.linalg.norm(n2, axis=1, keepdims=True), 1e-20)
    out = n2 - N
    out[np.linalg.norm(out, axis=1) < min_delta] = 0.0
    return out


def _append(bin_: bytearray, js: dict, payload: bytes) -> int:
    bin_ += b"\0" * (-len(bin_) % 4)
    js["bufferViews"].append({"buffer": 0, "byteOffset": len(bin_), "byteLength": len(payload)})
    bin_ += payload
    return len(js["bufferViews"]) - 1


def add_sparse_vec3(js: dict, bin_: bytearray, count: int, values: np.ndarray) -> int | None:
    """A sparse VEC3 float accessor (zero base) holding the non-zero rows of `values`."""
    idx = np.nonzero(np.any(values != 0.0, axis=1))[0]
    if len(idx) == 0:
        return None
    big = count > 65535
    iv = _append(bin_, js, idx.astype(np.uint32 if big else np.uint16).tobytes())
    vv = _append(bin_, js, values[idx].astype(np.float32).tobytes())
    js["accessors"].append({
        "componentType": FLOAT, "count": int(count), "type": "VEC3",
        "sparse": {"count": int(len(idx)),
                   "indices": {"bufferView": iv, "componentType": UINT32 if big else UINT16},
                   "values": {"bufferView": vv}},
    })
    return len(js["accessors"]) - 1


def add_morph_normals(path: Path, shapes: list[str], mesh: str = "Head", material: str = "skin_head",
                      min_delta: float = 0.01) -> dict:
    """Rewrite the GLB at `path` in place with NORMAL deltas on the named targets of one primitive.
    Returns {"shapes": n, "values": total sparse rows, "bytes_added": n}."""
    js, bin_ = read_glb(path)
    before = len(bin_)
    m = mesh_by_name(js, mesh)
    _, p = primitive_by_material(js, m, material)
    names = m.get("extras", {}).get("targetNames", [])
    P = accessor(js, bin_, p["attributes"]["POSITION"]).astype(np.float64)
    N = accessor(js, bin_, p["attributes"]["NORMAL"]).astype(np.float64)
    F = accessor(js, bin_, p["indices"]).astype(np.int64).reshape(-1, 3)
    wid = weld(P)
    base = welded_normals(P, F, wid)
    rows = 0
    done = 0
    for name in shapes:
        if name not in names:
            raise KeyError(f"{mesh} has no target {name}")
        t = p["targets"][names.index(name)]
        D = accessor(js, bin_, t["POSITION"]).astype(np.float64)
        dn = normal_deltas(P, N, F, D, wid, base, min_delta)
        acc = add_sparse_vec3(js, bin_, len(P), dn)
        if acc is None:
            continue
        t["NORMAL"] = acc
        rows += js["accessors"][acc]["sparse"]["count"]
        done += 1
    js["buffers"][0]["byteLength"] = len(bin_) + (-len(bin_) % 4)
    write_glb(path, js, bin_)
    return {"shapes": done, "values": rows, "bytes_added": len(bin_) - before}
