"""Mouth interior (no bpy): upper and lower teeth rows and the tongue, inside the skin's mouth bag.

Each tooth is a small superellipsoid on a parabolic dental arch behind the lips. Lower teeth and the
tongue carry their own tags so `jaw_open` (asha_face_shapes) can swing them with the mandible.
~2,000 triangles (M1-CHR-11). Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_mesh import Part

TAG_TEETH_UP = 31
TAG_TEETH_LO = 32
TAG_TONGUE = 33
# per side, from the midline: (crown width mm, crown height mm, depth mm)
UPPER = [(8.6, 10.0, 6.4), (6.6, 8.8, 5.8), (7.6, 9.6, 7.4), (7.0, 8.0, 8.8), (6.6, 7.4, 9.0)]
LOWER = [(5.4, 8.6, 5.6), (5.9, 8.6, 5.9), (6.9, 9.6, 7.0), (7.0, 8.2, 7.8), (7.0, 7.6, 8.4)]
# M1-CHR-10: the teeth sample a patch in an unused corner of the head atlas (u0, v0, u1, v1 in the
# Part / glTF convention, V down the image like the lash and brow UVs: the bottom-right corner),
# where asha_textures.teeth_patch paints their colour and occlusion. U runs along the arch (front
# incisor -> last tooth), V from the biting edge (v0) to the gum (v1). With a single UV the teeth
# took the full sky fill inside the mouth and read as a blue-grey slab in grief.
TEETH_UV = (0.84, 0.84, 0.98, 0.98)
TEETH_UV_INSET = 0.004  # keeps the samples off the patch border (mip bleed)
# M1-CHR-11, grief's "faceted gold-brass strip" (QA-05c fault 3). The teeth overlapped by 8% (pitch
# 0.92 of a width) into one continuous band, and at 8 x 4 segments with a boxy exponent (0.45) the
# labial faces were a few flat panels with hard edges. Now each crown is narrower than its slot on
# the same arch, so the rows break into teeth; the visible ones (the incisors and canines,
# TOOTH_FINE per side) are rounder and finer. +864 triangles.
TOOTH_PITCH = 0.92  # slot / crown width (unchanged: the arch must stay inside the mouth bag)
TOOTH_WIDTH = 0.86  # crown width / crown table width: a 0.06-width gap (about 0.5 mm) between neighbours
TOOTH_FINE = 3
TOOTH_FINE_NU, TOOTH_FINE_NV = 12, 6
TOOTH_ROUND = 0.62  # superellipsoid exponent of the fine teeth (1 = an ellipsoid, 0.45 = boxy)
TOOTH_U_SPAN = 0.45  # half of each tooth's U cell its side-to-side extent covers (teeth_patch's gaps)


def _superellipsoid(part: Part, c, axes, r, mat: str, tag: int, nu: int = 8, nv: int = 4, e: float = 0.45,
                    uv_of=None) -> None:
    """uv_of(ct, cx) -> (u, v) per face corner from its height on the +axes[2] axis (ct = 1 at the
    top pole, -1 at the bottom) and its side on the axes[0] axis (cx = -1 .. 1; 0 at the poles);
    None puts every corner at (0.5, 0.5)."""
    uv_of = uv_of or (lambda ct, cx: (0.5, 0.5))
    f = lambda x: math.copysign(abs(x) ** e, x)  # noqa: E731
    rows = []
    top = part.add_v(c + axes[2] * r[2], tag=tag)
    for j in range(1, nv):
        th = math.pi * j / nv
        st, ct = math.sin(th), math.cos(th)
        row = []
        for i in range(nu):
            ph = 2 * math.pi * i / nu
            sp, cp = math.sin(ph), math.cos(ph)
            p = c + axes[0] * r[0] * f(st) * f(cp) + axes[1] * r[1] * f(st) * f(sp) + axes[2] * r[2] * f(ct)
            row.append(part.add_v(p, tag=tag))
        rows.append(row)
    bot = part.add_v(c - axes[2] * r[2], tag=tag)
    def uv(j: int, i: int) -> tuple[float, float]:  # j = 0 top pole .. nv bottom pole
        th = math.pi * j / nv
        return uv_of(math.cos(th), f(math.sin(th)) * f(math.cos(2 * math.pi * i / nu)))

    for i in range(nu):
        i2 = (i + 1) % nu
        part.add_f((top, rows[0][i], rows[0][i2]), [uv(0, i), uv(1, i), uv(1, i2)], mat)
        part.add_f((rows[-1][i], bot, rows[-1][i2]), [uv(nv - 1, i), uv(nv, i), uv(nv - 1, i2)], mat)
    for j in range(len(rows) - 1):
        for i in range(nu):
            i2 = (i + 1) % nu
            part.add_f((rows[j][i], rows[j + 1][i], rows[j + 1][i2], rows[j][i2]),
                       [uv(j + 1, i), uv(j + 2, i), uv(j + 2, i2), uv(j + 1, i2)], mat)


def teeth_uv(a: float, b: float) -> tuple[float, float]:
    """TEETH_UV patch coordinates of arch position a (0 front .. 1 back) and height b (0 biting
    edge .. 1 gum). +axes[2] of a tooth points to its gum, so its top pole is b = 1."""
    u0, v0, u1, v1 = TEETH_UV
    m = TEETH_UV_INSET
    return (u0 + m + (u1 - u0 - 2 * m) * a, v0 + m + (v1 - v0 - 2 * m) * b)


def mouth_interior(lm, lip_line_y: float) -> Part:
    part = Part("MouthInterior")
    s = lm.h / 0.222
    M = lm.P("mouth")
    y_front = lip_line_y + 0.0052 * s  # labial face of the incisors, behind the lips' inner surface
    for row, z_edge, tag, up in ((UPPER, M[2] - 0.0006 * s, TAG_TEETH_UP, True),
                                 (LOWER, M[2] - 0.0016 * s, TAG_TEETH_LO, False)):
        for sgn in (1.0, -1.0):
            x = 0.0
            for k, (w, hgt, dpt) in enumerate(row):
                w, hgt, dpt = w * 0.001 * s, hgt * 0.001 * s, dpt * 0.001 * s
                xc = x + w * 0.5
                x += w * TOOTH_PITCH
                # parabolic arch: teeth turn and recede toward the back
                depth = 0.60 * (xc / (0.020 * s)) ** 2 * 0.012 * s
                yc = y_front + depth + dpt * 0.5
                ang = math.atan2(2 * 0.60 * xc / (0.020 * s) ** 2 * 0.012 * s, 1.0)
                fwd = np.array([sgn * math.sin(ang), -math.cos(ang), 0.0])
                side = np.array([math.cos(ang) * sgn, math.sin(ang), 0.0])
                vert = np.array([0.0, 0.0, 1.0 if up else -1.0])
                c = np.array([sgn * xc, yc, z_edge + (hgt * 0.5 if up else -hgt * 0.5)])
                axes = np.stack([side, -fwd, vert])
                # M1-CHR-11: U runs across each tooth too (its own fifth of the patch), so teeth_patch
                # can shade the gaps between them; the visible front teeth are rounder and finer
                front = k < TOOTH_FINE
                nu, nv, e = (TOOTH_FINE_NU, TOOTH_FINE_NV, TOOTH_ROUND) if front else (8, 4, 0.45)
                _superellipsoid(part, c, axes, np.array([w * 0.5 * TOOTH_WIDTH, dpt * 0.5, hgt * 0.5]), "teeth", tag,
                                nu=nu, nv=nv, e=e,
                                uv_of=lambda ct, cx, k=k, n=len(row): teeth_uv((k + 0.5 + TOOTH_U_SPAN * cx) / n,
                                                                              0.5 * (1.0 + ct)))
    # tongue: a flattened ellipsoid resting behind the lower teeth
    c = np.array([0.0, y_front + 0.022 * s, M[2] - 0.0085 * s])
    axes = np.eye(3)
    _superellipsoid(part, c, axes, np.array([0.019 * s, 0.024 * s, 0.0065 * s]), "tongue", TAG_TONGUE, nu=12, nv=6,
                    e=0.8)
    return part
