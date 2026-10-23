"""Tiny numpy mesh container and builders shared by the Asha part generators (no bpy).

A `Part` is a list of polygons (index tuples) over a vertex array, with one UV per face corner, one
material name per face, optional per-vertex RGBA (wind / hair data) and an optional integer tag per
vertex (used by the blendshape builder to know lashes from brows from teeth). build_asha.py turns
Parts into Blender objects. Everything is deterministic.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

Arr = np.ndarray


@dataclass
class Part:
    name: str
    V: list = field(default_factory=list)  # vertex positions (3,)
    F: list = field(default_factory=list)  # tuples of vertex indices (3 or 4)
    UV: list = field(default_factory=list)  # per face: tuple of (u, v) per corner
    M: list = field(default_factory=list)  # per face: material name
    C: list = field(default_factory=list)  # per vertex RGBA (empty = none)
    T: list = field(default_factory=list)  # per vertex int tag (empty = none)

    def add_v(self, p, color=None, tag: int | None = None) -> int:
        self.V.append(np.asarray(p, dtype=float))
        if color is not None:
            self.C.append(tuple(float(c) for c in color))
        if tag is not None:
            self.T.append(int(tag))
        return len(self.V) - 1

    def add_f(self, idx, uv, mat: str) -> None:
        idx = tuple(int(i) for i in idx)
        assert len(set(idx)) == len(idx), idx
        self.F.append(idx)
        self.UV.append(tuple((float(a), float(b)) for a, b in uv))
        self.M.append(mat)

    def extend(self, other: "Part") -> None:
        off = len(self.V)
        self.V.extend(other.V)
        self.C.extend(other.C)
        self.T.extend(other.T)
        for f, uv, m in zip(other.F, other.UV, other.M):
            self.F.append(tuple(i + off for i in f))
            self.UV.append(uv)
            self.M.append(m)

    def tris(self) -> int:
        return sum(len(f) - 2 for f in self.F)

    def varr(self) -> Arr:
        return np.array(self.V) if self.V else np.zeros((0, 3))


def grid(part: Part, P: Arr, mat: str, uv_rect=(0.0, 0.0, 1.0, 1.0), closed_u: bool = False, colors=None,
         tags=None, flip: bool = False, uv_fn=None) -> Arr:
    """Quad grid from points P[j, i] (rows j along V, columns i along U). Returns vertex ids."""
    nj, ni = P.shape[0], P.shape[1]
    ids = np.zeros((nj, ni), dtype=int)
    for j in range(nj):
        for i in range(ni):
            c = None if colors is None else colors[j][i]
            t = None if tags is None else (tags if isinstance(tags, int) else tags[j][i])
            ids[j, i] = part.add_v(P[j, i], c, t)
    u0, v0, u1, v1 = uv_rect
    cols = ni if closed_u else ni - 1
    for j in range(nj - 1):
        for i in range(cols):
            i2 = (i + 1) % ni
            q = [ids[j, i], ids[j, i2], ids[j + 1, i2], ids[j + 1, i]]
            if uv_fn is not None:
                uv = [uv_fn(j, i), uv_fn(j, i + 1), uv_fn(j + 1, i + 1), uv_fn(j + 1, i)]
            else:
                uv = [(u0 + (u1 - u0) * (ii / cols), v0 + (v1 - v0) * (jj / (nj - 1)))
                      for jj, ii in ((j, i), (j, i + 1), (j + 1, i + 1), (j + 1, i))]
            if flip:
                q, uv = q[::-1], uv[::-1]
            part.add_f(q, uv, mat)
    return ids


def frames_along(C: Arr, up_hint: Arr) -> tuple[Arr, Arr, Arr]:
    """Rotation-minimising frames (tangent, normal, binormal) along a polyline."""
    n = len(C)
    T = np.gradient(C, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
    N = np.zeros_like(C)
    nrm = up_hint - (up_hint @ T[0]) * T[0]
    if np.linalg.norm(nrm) < 1e-6:
        nrm = np.cross(T[0], np.array([1.0, 0.0, 0.0]))
    N[0] = nrm / np.linalg.norm(nrm)
    for k in range(1, n):
        v = N[k - 1] - (N[k - 1] @ T[k]) * T[k]
        N[k] = v / max(np.linalg.norm(v), 1e-12)
    Bn = np.cross(T, N)
    return T, N, Bn


def tube(part: Part, C: Arr, radius, n_around: int, mat: str, up_hint: Arr, uv_rect=(0, 0, 1, 1), colors=None,
         tags=None, cap_end: bool = False, scale_xy=None) -> Arr:
    """Open tube around polyline C (radius scalar or per point). Returns grid ids [len(C), n_around]."""
    T, N, Bn = frames_along(C, up_hint)
    r = np.broadcast_to(np.asarray(radius, dtype=float), (len(C),))
    ang = 2 * math.pi * np.arange(n_around) / n_around
    P = np.zeros((len(C), n_around, 3))
    for k in range(len(C)):
        sx, sy = (1.0, 1.0) if scale_xy is None else scale_xy[k]
        P[k] = C[k] + r[k] * (np.cos(ang)[:, None] * N[k] * sx + np.sin(ang)[:, None] * Bn[k] * sy)
    ids = grid(part, P, mat, uv_rect, closed_u=True, colors=colors, tags=tags)
    if cap_end:
        c = part.add_v(C[-1] + T[-1] * float(r[-1]) * 0.5, None if colors is None else colors[-1][0],
                       None if tags is None else (tags if isinstance(tags, int) else tags[-1][0]))
        for i in range(n_around):
            a, b = ids[-1, i], ids[-1, (i + 1) % n_around]
            part.add_f((a, b, c), [(uv_rect[0], uv_rect[3])] * 3, mat)
    return ids


def uv_sphere(part: Part, c: Arr, r, seg_u: int, seg_v: int, mat: str, axis_fwd=None, uv_rect=(0, 0, 1, 1),
              tags=None) -> None:
    """UV sphere with its pole along `axis_fwd` (default -Y); r scalar or (3,) radii in local frame."""
    r = np.broadcast_to(np.asarray(r, dtype=float), (3,))
    fwd = np.array([0.0, -1.0, 0.0]) if axis_fwd is None else np.asarray(axis_fwd, dtype=float)
    fwd = fwd / np.linalg.norm(fwd)
    up = np.array([0.0, 0.0, 1.0]) if abs(fwd[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    side = np.cross(up, fwd)
    side /= np.linalg.norm(side)
    up = np.cross(fwd, side)
    top = part.add_v(c + fwd * r[1], tag=tags)
    rows = []
    for j in range(1, seg_v):
        th = math.pi * j / seg_v
        row = []
        for i in range(seg_u):
            ph = 2 * math.pi * i / seg_u
            d = side * math.sin(th) * math.cos(ph) * r[0] + up * math.sin(th) * math.sin(ph) * r[2] + fwd * math.cos(th) * r[1]
            row.append(part.add_v(c + d, tag=tags))
        rows.append(row)
    bot = part.add_v(c - fwd * r[1], tag=tags)
    u0, v0, u1, v1 = uv_rect

    def uv(j: int, i: int) -> tuple[float, float]:
        return (u0 + (u1 - u0) * i / seg_u, v0 + (v1 - v0) * j / seg_v)

    for i in range(seg_u):
        i2 = (i + 1) % seg_u
        part.add_f((top, rows[0][i2], rows[0][i]), [uv(0, i), uv(1, i + 1), uv(1, i)], mat)
    for j in range(seg_v - 2):
        for i in range(seg_u):
            i2 = (i + 1) % seg_u
            part.add_f((rows[j][i], rows[j][i2], rows[j + 1][i2], rows[j + 1][i]),
                       [uv(j + 1, i), uv(j + 1, i + 1), uv(j + 2, i + 1), uv(j + 2, i)], mat)
    for i in range(seg_u):
        i2 = (i + 1) % seg_u
        part.add_f((rows[-1][i], rows[-1][i2], bot), [uv(seg_v - 1, i), uv(seg_v - 1, i + 1), uv(seg_v, i)], mat)


def catmull_rom(P: Arr, n: int) -> Arr:
    """Uniform Catmull-Rom through control points, resampled to n points by arc length."""
    P = np.asarray(P, dtype=float)
    ext = np.concatenate([P[:1] * 2 - P[1:2], P, P[-1:] * 2 - P[-2:-1]])
    dense = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for t in np.linspace(0, 1, 24, endpoint=False):
            t2, t3 = t * t, t * t * t
            dense.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                                + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    dense.append(P[-1])
    D = np.array(dense)
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(D, axis=0), axis=1))])
    st = np.linspace(0, s[-1], n)
    return np.stack([np.interp(st, s, D[:, k]) for k in range(D.shape[1])], axis=1)


def arclen(C: Arr) -> Arr:
    return np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))])
