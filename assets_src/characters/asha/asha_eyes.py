"""Asha's eyes, lashes and brows (no bpy). Contracts: docs/kb/tech/character_shading.md.

* Eyeball, cornea shell, eye-occlusion shell and tear line per eye, each a separate part in
  **eye-local coordinates** (origin at the eyeball centre, Blender -Y = gaze, which glTF turns into
  +Z). build_asha.py places each at the eye centre and parents it to the DEF-eye bone.
* Lash cards (upper and lower) and brow cards in **world coordinates**; they go into the head
  object so the face blendshapes move them with the lids and brows.

All shapes come from bb_face.EyeFrame (the same almond the lids are cut from), so a slider change
re-fits the shells, lashes and lids together.
"""
from __future__ import annotations

import math

import numpy as np

from asha_mesh import Part, grid

IRIS_R = 0.00645  # asha.md §1: 12.9 mm iris
CORNEA_R = 0.0086  # corneal curvature radius (7.8 mm x 1.10)
OCCLUSION_LIFT = 0.0017
TEAR_LIFT = 0.0004
TAG_LASH_UP = {"L": 11, "R": 12}
TAG_LASH_LO = {"L": 13, "R": 14}
TAG_BROW = {"L": 15, "R": 16}


def _sphere_pt(a: float, b: float, radius: float, sgn: float) -> np.ndarray:
    s = math.hypot(a, b)
    if s > 0.985 * radius:
        a, b = a * 0.985 * radius / s, b * 0.985 * radius / s
        s = 0.985 * radius
    return np.array([sgn * a, -math.sqrt(radius * radius - s * s), b])


def eyeball(fr, seg_u: int = 20, seg_v: int = 12) -> Part:
    part = Part(f"Eye{fr.side}")
    R = fr.R
    # pole on -Y (the gaze); the shader parametrises sclera/iris in object space
    top = part.add_v([0.0, -R, 0.0])
    rows = []
    for j in range(1, seg_v):
        th = math.pi * (j / seg_v) ** 1.0
        rows.append([part.add_v([R * math.sin(th) * math.cos(2 * math.pi * i / seg_u), -R * math.cos(th),
                                 R * math.sin(th) * math.sin(2 * math.pi * i / seg_u)]) for i in range(seg_u)])
    bot = part.add_v([0.0, R, 0.0])
    _cap_rings(part, top, rows, bot, "eye", seg_u)
    return part


def _cap_rings(part: Part, top: int, rows, bot: int | None, mat: str, seg_u: int) -> None:
    nv = len(rows) + (1 if bot is not None else 0)

    def uv(j: float, i: float) -> tuple[float, float]:
        return (i / seg_u, j / max(nv, 1))

    for i in range(seg_u):
        i2 = (i + 1) % seg_u
        part.add_f((top, rows[0][i], rows[0][i2]), [uv(0, i), uv(1, i), uv(1, i + 1)], mat)
    for j in range(len(rows) - 1):
        for i in range(seg_u):
            i2 = (i + 1) % seg_u
            part.add_f((rows[j][i], rows[j + 1][i], rows[j + 1][i2], rows[j][i2]),
                       [uv(j + 1, i), uv(j + 2, i), uv(j + 2, i + 1), uv(j + 1, i + 1)], mat)
    if bot is not None:
        for i in range(seg_u):
            i2 = (i + 1) % seg_u
            part.add_f((rows[-1][i], bot, rows[-1][i2]), [uv(nv - 1, i), uv(nv, i), uv(nv - 1, i + 1)], mat)


def cornea(fr, seg_u: int = 24, seg_v: int = 9, max_deg: float = 78.0) -> Part:
    """Front cap 0.2 mm off the globe with the corneal bulge (character_shading.md)."""
    part = Part(f"Cornea{fr.side}")
    R = fr.R
    radius = R + 0.0002
    zl = math.sqrt(max(R * R - IRIS_R * IRIS_R, 0.0))
    zc = zl - math.sqrt(max(CORNEA_R * CORNEA_R - IRIS_R * IRIS_R, 0.0))
    c = np.array([0.0, -zc, 0.0])

    def pt(d: np.ndarray) -> np.ndarray:
        t = radius
        b = float(d @ c)
        disc = b * b - (float(c @ c) - CORNEA_R * CORNEA_R)
        if disc > 0.0:
            tc = b + math.sqrt(disc) + 0.0002
            t = max(t, tc)
        return d * t

    top = part.add_v(pt(np.array([0.0, -1.0, 0.0])))
    rows = []
    for j in range(1, seg_v + 1):
        th = math.radians(max_deg) * j / seg_v
        rows.append([part.add_v(pt(np.array([math.sin(th) * math.cos(2 * math.pi * i / seg_u), -math.cos(th),
                                             math.sin(th) * math.sin(2 * math.pi * i / seg_u)])))
                     for i in range(seg_u)])
    _cap_rings(part, top, rows, None, "cornea", seg_u)
    return part


def occlusion(fr, n: int = 24, rings: int = 4) -> Part:
    """Shell over the whole opening, 1.7 mm off the globe. U inner (0) -> outer (1) canthus,
    V upper (0) -> lower (1) lid margin."""
    part = Part(f"EyeOcclusion{fr.side}")
    radius = fr.R + OCCLUSION_LIFT
    t = 2 * math.pi * np.arange(n) / n
    a, b = fr.contour(t)
    centre = part.add_v(_sphere_pt(0.0, 0.0, radius, fr.sgn))
    rows = []
    for j in range(1, rings + 1):
        f = 1.08 * j / rings
        rows.append([part.add_v(_sphere_pt(a[i] * f, b[i] * f, radius, fr.sgn)) for i in range(n)])
    span_a = float(np.max(np.abs(a))) * 1.08
    span_b = float(np.max(np.abs(b))) * 1.08

    def uv_of(i: int, f: float) -> tuple[float, float]:
        return (0.5 + 0.5 * f * a[i] / span_a, 0.5 - 0.5 * f * b[i] / span_b)

    for i in range(n):
        i2 = (i + 1) % n
        f = 1.08 / rings
        q = (centre, rows[0][i2], rows[0][i]) if fr.sgn > 0 else (centre, rows[0][i], rows[0][i2])
        uvs = [(0.5, 0.5), uv_of(i2, f), uv_of(i, f)] if fr.sgn > 0 else [(0.5, 0.5), uv_of(i, f), uv_of(i2, f)]
        part.add_f(q, uvs, "eye_occlusion")
    for j in range(rings - 1):
        f0, f1 = 1.08 * (j + 1) / rings, 1.08 * (j + 2) / rings
        for i in range(n):
            i2 = (i + 1) % n
            q = [rows[j][i], rows[j][i2], rows[j + 1][i2], rows[j + 1][i]]
            uvs = [uv_of(i, f0), uv_of(i2, f0), uv_of(i2, f1), uv_of(i, f1)]
            if fr.sgn > 0:
                q, uvs = q[::-1], uvs[::-1]
            part.add_f(q, uvs, "eye_occlusion")
    return part


def tear_line(fr, n: int = 24) -> Part:
    """Strip just inside the lower margin. U along the lid (inner 0 -> outer 1), V lid (0) ->
    eyeball (1)."""
    part = Part(f"TearLine{fr.side}")
    radius = fr.R + TEAR_LIFT
    t = np.linspace(math.pi * 0.98, math.pi * 2.02, n)  # inner canthus -> bottom -> outer canthus
    a, b = fr.contour(t)
    rows = []
    for j in range(3):
        w = 0.0013 * j / 2
        row = []
        for i in range(n):
            s = math.hypot(a[i], b[i])
            k = max(s - w, 0.0) / max(s, 1e-9)
            row.append(part.add_v(_sphere_pt(a[i] * k, b[i] * k, radius, fr.sgn)))
        rows.append(row)
    for j in range(2):
        for i in range(n - 1):
            q = [rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]]
            uvs = [(i / (n - 1), j / 2), ((i + 1) / (n - 1), j / 2), ((i + 1) / (n - 1), (j + 1) / 2),
                   (i / (n - 1), (j + 1) / 2)]
            # face away from the eye centre (toward the viewer)
            p0, p1, p3 = (np.array(part.V[q[0]]), np.array(part.V[q[1]]), np.array(part.V[q[3]]))
            if np.cross(p1 - p0, p3 - p0) @ p0 < 0:
                q, uvs = q[::-1], uvs[::-1]
            part.add_f(q, uvs, "tear_line")
    return part


# ---------------------------------------------------------------------------------------------
# Lashes and brows (world space, into the head object)
# ---------------------------------------------------------------------------------------------
def lashes(fr, thickness: float, upper: bool, n: int = 14) -> Part:
    """A lash ribbon rooted on the lid margin's outer edge, curling out and up (upper) or down.
    UV: U along the lid, V root (0) -> tip (1); the atlas's top half holds the lash strands."""
    part = Part(f"Lash{'Up' if upper else 'Lo'}{fr.side}")
    tag = TAG_LASH_UP[fr.side] if upper else TAG_LASH_LO[fr.side]
    if upper:
        t = np.linspace(math.pi * 0.93, math.pi * 0.03, n)  # inner -> outer
    else:
        t = np.linspace(math.pi * 1.10, math.pi * 1.95, n)
    roots = fr.margin_point(t, thickness * 0.75)
    E = fr.E
    a, b = fr.contour(t)
    L_mid = 0.0098 if upper else 0.0052
    rows = 4
    P = np.zeros((rows + 1, n, 3))
    for i in range(n):
        u = i / (n - 1)
        prof = math.sin(math.pi * (0.12 + 0.82 * u)) ** 0.7  # longest at the outer middle
        length = L_mid * (0.45 + 0.55 * prof) * (1.08 if upper and u > 0.5 else 1.0)
        out = roots[i] - E
        out = out / np.linalg.norm(out)  # radially off the globe
        up = np.array([0.0, 0.0, 1.0 if upper else -1.0])
        lat = np.array([fr.sgn * (a[i] / max(abs(a[i]) + abs(b[i]), 1e-6)), 0.0, 0.0])
        for j in range(rows + 1):
            s = j / rows
            # leave along the radial direction, then curl toward up (or down)
            d = out * (1.0 - 0.55 * s) + up * (0.25 + 0.95 * s) + lat * 0.25 * s
            d /= np.linalg.norm(d)
            if j == 0:
                P[j, i] = roots[i]
            else:
                P[j, i] = P[j - 1, i] + d * length / rows
    v0, v1 = (0.0, 0.5)
    ids = grid(part, P, "lash", uv_fn=lambda j, i: (i / (n - 1), v0 + (v1 - v0) * j / rows), tags=tag)
    _ = ids
    return part


def brow(face, side: str, surface_fn, layers: int = 3, n: int = 16) -> Part:
    """Brow ribbons lying on the skin: natural, fairly straight, thicker at the head, tapering by
    the outer third (asha.md §6.1). V runs medial (0) -> lateral (1) along the brow, U across
    (bottom 0 -> top 1); the atlas's lower half holds short brow hairs drawn along V."""
    part = Part(f"Brow{side}")
    lm = face.lm
    fr = face.eyes[side]
    E = fr.E
    s = lm.h / 0.222
    tag = TAG_BROW[side]
    u = np.linspace(0.0, 1.0, n)
    xs = E[0] + fr.sgn * (-0.0175 * s + 0.044 * s * u)  # 13.5 mm from the midline -> past the orbit rim
    arch = 0.0035 * s * np.sin(np.pi * np.clip(u / 0.72, 0, 1)) * (u < 0.72) + 0.0035 * s * np.cos(
        np.pi * 0.5 * np.clip((u - 0.72) / 0.28, 0, 1)) * (u >= 0.72)
    zc = E[2] + 0.0148 * s + arch - 0.0022 * s * u**2
    thick = (0.0068 * (1 - u) ** 0.8 + 0.0022 * u) * s
    for layer in range(layers):
        lift = 0.0004 + 0.0007 * layer
        shrink = 1.0 - 0.18 * layer
        P = np.zeros((3, n, 3))
        for j, f in enumerate((-0.5, 0.0, 0.5)):
            z = zc + f * thick * shrink + 0.0006 * s * layer
            pts = surface_fn(np.stack([xs, z], axis=1))
            # lift along the surface normal approximated by the forward direction
            P[j] = pts + np.array([0.0, -lift, 0.0])
        # U across (rows j), V along (columns i) -> grid rows are U here
        v_off = 0.5 + 0.5 * (layer / max(layers, 1))
        grid(part, P, "brow", uv_fn=lambda j, i, vo=v_off: (j / 2.0, 0.5 + 0.5 * i / (n - 1)), tags=tag,
             flip=(fr.sgn < 0))
        _ = v_off
    return part
