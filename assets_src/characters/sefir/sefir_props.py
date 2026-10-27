"""Sefir's bowl-crown (no bpy), act1_npcs.md §1.3 and §1.4 #6.

A gilded shallow bowl, 34 cm across and 6 cm deep, tipped on edge behind the head with its concave face toward the
back of his head (a spherical cap of radius rho = (R^2 + d^2) / 2d, 3 mm thick, with a rolled rim). It is held by a
thin gilt band round the back of the skull at the occiput (over the hair) and a short stem from the band to the
middle of the bowl, so the bowl's rim stands 4 cm off the hair. The concave face is `gilt_hi` (burnished
`gold_leaf_hi`, roughness 0.22: it lights his head from behind in a key-lit shot, reflective, never emissive); the
convex back, the rim, the band and the stem are `gilt` (`gold_leaf`). The crown is rigid on the head: the build
weights it to its prop bone DEF-crown (a child of the head bone, for the boss phases).

`place_crown` puts the bowl from the head's own points (the hair surface behind the head), so it follows the body
parameters. Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_mesh import Part, grid, tube

TAG_PROP = 61
SEG = 40  # round the bowl
RINGS = 8  # centre -> rim
THICK = 0.003  # m, the bowl's wall
RIM_R = 0.0035  # m, the rolled rim's radius
CENTRE_ABOVE_HEAD_C = 0.082  # m: the bowl's centre above the head centre (its lower rim stays clear of the shoulders)
BAND_Z_ABOVE_SKULL_BASE = 0.06  # m: the band round the occiput
BAND_SPAN_DEG = (132.0, 228.0)  # azimuths the band runs over, round the back of the head (0 = front)
BAND_N = 24
STEM_R = 0.004  # m
UV_CONCAVE = (0.0, 0.0, 1.0, 0.5)
UV_CONVEX = (0.0, 0.5, 1.0, 1.0)


def cap_radius(R: float, d: float) -> float:
    return (R * R + d * d) / (2.0 * d)


def bowl_point(R: float, d: float, r: np.ndarray, th: np.ndarray) -> np.ndarray:
    """Local bowl coordinates: x (his left), z (up) in the rim's plane, y = depth behind the rim plane (0 at the rim,
    d at the centre)."""
    rho = cap_radius(R, d)
    rr = r * R
    depth = d - (rho - np.sqrt(np.maximum(rho * rho - rr * rr, 0.0)))
    return np.stack([rr * np.cos(th), depth, rr * np.sin(th)], axis=-1)


def place_crown(lm, params: dict, hair_back_y: float) -> dict:
    """The rim's centre, its plane's normal (+Y, back) and the band's height. `hair_back_y`: how far back the hair's
    surface reaches behind the head (m)."""
    hc = lm.P("head_c")
    rim_c = np.array([0.0, hair_back_y + float(params["hair_gap_m"]), float(hc[2]) + CENTRE_ABOVE_HEAD_C])
    return {"rim_c": rim_c, "axis": np.array([0.0, 1.0, 0.0]),
            "band_z": float(lm.P("skull_base")[2]) + BAND_Z_ABOVE_SKULL_BASE}


def crown(lm, params: dict, place: dict, hair_surface) -> Part:
    """The bowl, its rolled rim, the band and the stem. `hair_surface(P)` projects points onto the hair's outer
    surface behind the head (the band sits on it)."""
    part = Part("Crown")
    R = 0.5 * float(params["diameter_m"])
    d = float(params["depth_m"])
    c = place["rim_c"]
    th = 2 * math.pi * np.arange(SEG) / SEG
    r = np.linspace(0.0, 1.0, RINGS + 1)[1:]
    Rr, Th = np.meshgrid(r, th, indexing="ij")
    inner = bowl_point(R, d, Rr, Th) + c  # the concave face (toward the head)
    outer = bowl_point(R, d, Rr, Th) + c + np.array([0.0, THICK, 0.0])  # the convex back
    # the centre points and the rings as grids (rows centre -> rim, columns round)
    ctr_in = part.add_v(c + np.array([0.0, d, 0.0]), tag=TAG_PROP)

    def uv_disc(rect, rr, tt):
        u0, v0, u1, v1 = rect
        return (u0 + (u1 - u0) * (0.5 + 0.5 * rr * math.cos(tt)), v0 + (v1 - v0) * (0.5 + 0.5 * rr * math.sin(tt)))

    ids_in = grid(part, inner, "gilt_hi", closed_u=True, tags=TAG_PROP,
                  uv_fn=lambda j, i: uv_disc(UV_CONCAVE, r[j], th[i % SEG]), flip=False)
    # wind each face so it looks toward the head (-Y): test one and flip the grid if needed
    a, b, e = (part.V[ids_in[0, 0]], part.V[ids_in[0, 1]], part.V[ids_in[1, 0]])
    first_face = len(part.F) - (RINGS - 1) * SEG
    if np.cross(b - a, e - a)[1] > 0:
        for k in range(first_face, len(part.F)):
            part.F[k] = part.F[k][::-1]
            part.UV[k] = part.UV[k][::-1]
    for i in range(SEG):
        i2 = (i + 1) % SEG
        tri = (ctr_in, int(ids_in[0, i]), int(ids_in[0, i2]))
        p0, p1, p2 = (part.V[k] for k in tri)
        if np.cross(p1 - p0, p2 - p0)[1] > 0:
            tri = (tri[0], tri[2], tri[1])
        part.add_f(tri, [uv_disc(UV_CONCAVE, 0.0, 0.0), uv_disc(UV_CONCAVE, r[0], th[i]),
                         uv_disc(UV_CONCAVE, r[0], th[i2])], "gilt_hi")
    ctr_out = part.add_v(c + np.array([0.0, d + THICK, 0.0]), tag=TAG_PROP)
    n0 = len(part.F)
    ids_out = grid(part, outer, "gilt", closed_u=True, tags=TAG_PROP,
                   uv_fn=lambda j, i: uv_disc(UV_CONVEX, r[j], th[i % SEG]))
    a, b, e = (part.V[ids_out[0, 0]], part.V[ids_out[0, 1]], part.V[ids_out[1, 0]])
    if np.cross(b - a, e - a)[1] < 0:  # the back faces away from the head (+Y)
        for k in range(n0, len(part.F)):
            part.F[k] = part.F[k][::-1]
            part.UV[k] = part.UV[k][::-1]
    for i in range(SEG):
        i2 = (i + 1) % SEG
        tri = (ctr_out, int(ids_out[0, i]), int(ids_out[0, i2]))
        p0, p1, p2 = (part.V[k] for k in tri)
        if np.cross(p1 - p0, p2 - p0)[1] < 0:
            tri = (tri[0], tri[2], tri[1])
        part.add_f(tri, [uv_disc(UV_CONVEX, 0.0, 0.0)] * 3, "gilt")
    # the rolled rim: a tube round the rim joining the two faces
    rim = bowl_point(R, d, np.ones(SEG + 1), np.concatenate([th, th[:1]])) + c + np.array([0.0, 0.5 * THICK, 0.0])
    tube(part, rim[:-1], RIM_R, 8, "gilt", np.array([0.0, 1.0, 0.0]), (0.0, 0.48, 1.0, 0.52), tags=TAG_PROP)
    # close the tube's ring seam: tube() is open along the curve, so bridge its last and first rings
    nb_ring = 8
    last = len(part.V) - nb_ring
    first = last - (SEG - 1) * nb_ring
    for k in range(nb_ring):
        k2 = (k + 1) % nb_ring
        part.add_f((last + k, last + k2, first + k2, first + k), [(0.0, 0.5)] * 4, "gilt")
    # the band round the occiput, on the hair, and the stem to the bowl's middle
    az = np.radians(np.linspace(BAND_SPAN_DEG[0], BAND_SPAN_DEG[1], BAND_N))
    hc = lm.P("head_c")
    probe = np.stack([0.3 * np.sin(az), float(hc[1]) - 0.3 * np.cos(az), np.full(BAND_N, place["band_z"])], axis=1)
    band = hair_surface(probe) + np.array([0.0, 0.0, 0.0])
    w = 0.5 * float(params["band_width_m"])
    tb = float(params["band_thickness_m"])
    out_n = band - np.array([0.0, float(hc[1]), place["band_z"]])
    out_n[:, 2] = 0.0
    out_n /= np.linalg.norm(out_n, axis=1, keepdims=True)
    up = np.array([0.0, 0.0, 1.0])
    ring = []
    for k in range(BAND_N):
        p = band[k] + out_n[k] * 0.5 * tb
        ring.append([p + up * w - out_n[k] * 0.5 * tb, p + up * w + out_n[k] * 0.5 * tb,
                     p - up * w + out_n[k] * 0.5 * tb, p - up * w - out_n[k] * 0.5 * tb])
    B = np.array(ring)  # (along, 4 corners)
    ids = grid(part, B, "gilt", closed_u=True, tags=TAG_PROP, uv_fn=lambda j, i: (0.1 * i, 0.5))
    # wind the band's faces outward from its own centre line
    for k in range(len(part.F) - (BAND_N - 1) * 4, len(part.F)):
        f = part.F[k]
        p0, p1, p2 = (part.V[q] for q in f[:3])
        mid = np.mean([part.V[q] for q in f], axis=0)
        j = int(np.argmin(np.linalg.norm(band - mid, axis=1)))
        if np.cross(p1 - p0, p2 - p0) @ (mid - (band[j] + out_n[j] * 0.5 * tb)) < 0:
            part.F[k] = f[::-1]
            part.UV[k] = part.UV[k][::-1]
    for end in (0, BAND_N - 1):  # cap the band's ends
        q = [int(x) for x in ids[end]]
        if end == 0:
            q = q[::-1]
        part.add_f(tuple(q), [(0.0, 0.5)] * 4, "gilt")
    mid_b = band[BAND_N // 2] + out_n[BAND_N // 2] * tb
    stem_end = c + np.array([0.0, d - 0.002, 0.0])
    stem = np.linspace(mid_b, stem_end, 6)
    tube(part, stem, STEM_R, 8, "gilt", np.array([0.0, 0.0, 1.0]), (0.0, 0.48, 1.0, 0.52), tags=TAG_PROP)
    _ = ids_in
    return part
