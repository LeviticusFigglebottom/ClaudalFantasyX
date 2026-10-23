"""Mouth interior (no bpy): upper and lower teeth rows and the tongue, inside the skin's mouth bag.

Each tooth is a small superellipsoid on a parabolic dental arch behind the lips. Lower teeth and the
tongue carry their own tags so `jaw_open` (asha_face_shapes) can swing them with the mandible.
~1,100 triangles. Deterministic.
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


def _superellipsoid(part: Part, c, axes, r, mat: str, tag: int, nu: int = 8, nv: int = 4, e: float = 0.45) -> None:
    rows = []
    top = part.add_v(c + axes[2] * r[2], tag=tag)
    for j in range(1, nv):
        th = math.pi * j / nv
        st, ct = math.sin(th), math.cos(th)
        row = []
        for i in range(nu):
            ph = 2 * math.pi * i / nu
            sp, cp = math.sin(ph), math.cos(ph)
            f = lambda x: math.copysign(abs(x) ** e, x)  # noqa: E731
            p = c + axes[0] * r[0] * f(st) * f(cp) + axes[1] * r[1] * f(st) * f(sp) + axes[2] * r[2] * f(ct)
            row.append(part.add_v(p, tag=tag))
        rows.append(row)
    bot = part.add_v(c - axes[2] * r[2], tag=tag)
    for i in range(nu):
        i2 = (i + 1) % nu
        part.add_f((top, rows[0][i], rows[0][i2]), [(0.5, 0.5)] * 3, mat)
        part.add_f((rows[-1][i], bot, rows[-1][i2]), [(0.5, 0.5)] * 3, mat)
    for j in range(len(rows) - 1):
        for i in range(nu):
            i2 = (i + 1) % nu
            part.add_f((rows[j][i], rows[j + 1][i], rows[j + 1][i2], rows[j][i2]), [(0.5, 0.5)] * 4, mat)


def mouth_interior(lm, lip_line_y: float) -> Part:
    part = Part("MouthInterior")
    s = lm.h / 0.222
    M = lm.P("mouth")
    y_front = lip_line_y + 0.0052 * s  # labial face of the incisors, behind the lips' inner surface
    for row, z_edge, tag, up in ((UPPER, M[2] - 0.0006 * s, TAG_TEETH_UP, True),
                                 (LOWER, M[2] - 0.0016 * s, TAG_TEETH_LO, False)):
        for sgn in (1.0, -1.0):
            x = 0.0
            for (w, hgt, dpt) in row:
                w, hgt, dpt = w * 0.001 * s, hgt * 0.001 * s, dpt * 0.001 * s
                xc = x + w * 0.5
                x += w * 0.92
                # parabolic arch: teeth turn and recede toward the back
                depth = 0.60 * (xc / (0.020 * s)) ** 2 * 0.012 * s
                yc = y_front + depth + dpt * 0.5
                ang = math.atan2(2 * 0.60 * xc / (0.020 * s) ** 2 * 0.012 * s, 1.0)
                fwd = np.array([sgn * math.sin(ang), -math.cos(ang), 0.0])
                side = np.array([math.cos(ang) * sgn, math.sin(ang), 0.0])
                vert = np.array([0.0, 0.0, 1.0 if up else -1.0])
                c = np.array([sgn * xc, yc, z_edge + (hgt * 0.5 if up else -hgt * 0.5)])
                axes = np.stack([side, -fwd, vert])
                _superellipsoid(part, c, axes, np.array([w * 0.5, dpt * 0.5, hgt * 0.5]), "teeth", tag)
    # tongue: a flattened ellipsoid resting behind the lower teeth
    c = np.array([0.0, y_front + 0.022 * s, M[2] - 0.0085 * s])
    axes = np.eye(3)
    _superellipsoid(part, c, axes, np.array([0.019 * s, 0.024 * s, 0.0065 * s]), "tongue", TAG_TONGUE, nu=12, nv=6,
                    e=0.8)
    return part
