"""Asha's ears (no bpy): a parametric shell with helix rim, scapha, antihelix, concha and tragus.

Built in an ear plane (p = backward along the head side, q = up, h = outward relief), as concentric
rings from the concha floor (r = 0) to the helix rim (r = 1), then folded over the rim into a thin
back surface. The root (the front edge, p ~ 0) is buried in the head side, so there is no gap behind
the attachment. The plane is turned out from the head by `PROTRUSION_DEG` at the back. ~580
triangles per ear. Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_mesh import Part, catmull_rom

TAG_EAR = {"L": 21, "R": 22}
PROTRUSION_DEG = 17.0
# outline in mm (p back, q up), from the top of the attachment around the back to the lobe
OUTLINE_MM = [(3.0, 22.0), (10.0, 29.5), (19.0, 28.0), (25.5, 19.0), (28.0, 6.0), (26.5, -6.0), (22.0, -17.0),
              (15.5, -26.0), (8.5, -29.0), (4.0, -25.0), (2.0, -17.5), (0.5, -12.0), (-0.5, 0.0), (0.5, 12.0)]
CONCHA_MM = (9.5, -3.5)


def _relief(r: np.ndarray, root: np.ndarray, s: float) -> np.ndarray:
    """Outward relief (m) at ring radius r (0 concha floor .. 1 rim); root = 1 on the attached side."""
    g = lambda x, c, w: np.exp(-(((x - c) / w) ** 2))  # noqa: E731
    h = np.zeros_like(r)
    h += -0.0068 * np.clip(1.0 - r / 0.42, 0.0, 1.0) ** 1.6  # concha bowl
    h += 0.0026 * g(r, 0.56, 0.09)  # antihelix ridge
    h += 0.0004 * g(r, 0.76, 0.06)  # scapha (the groove floor between ridges)
    h += 0.0038 * g(r, 0.93, 0.06)  # helix rim
    h -= 0.0010 * g(r, 1.0, 0.03)  # the rim curls toward the head at the very edge
    return h * s * (1.0 - 0.9 * root)


def ear(lm, side: str, n_ang: int = 24, n_front: int = 9, n_back: int = 4) -> Part:
    part = Part(f"Ear{side}")
    tag = TAG_EAR[side]
    s = lm.h / 0.222
    sgn = 1.0 if side == "L" else -1.0
    root_pt = lm.side_pt("ear", side)
    pts = np.array(OUTLINE_MM + [OUTLINE_MM[0]]) * 0.001 * s
    outline = catmull_rom(pts, n_ang + 1)[:-1]
    c = np.array(CONCHA_MM) * 0.001 * s
    ang = np.arctan2(outline[:, 1] - c[1], outline[:, 0] - c[0])
    # the attached side faces forward (p < concha p): fade the relief out there
    root = np.clip((c[0] - outline[:, 0]) / (c[0] + 0.001), 0.0, 1.0) ** 0.7
    rot = math.radians(PROTRUSION_DEG)

    def to_world(p: np.ndarray, q: np.ndarray, hh: np.ndarray) -> np.ndarray:
        # ear plane: p along +Y (back), q along +Z, relief along +X (outward, mirrored); the plane
        # turns out about the vertical root axis so the back of the ear stands off the head
        lat = hh + p * math.sin(rot)
        back = p * math.cos(rot)
        return np.stack([root_pt[0] + sgn * lat, root_pt[1] + back, root_pt[2] + q], axis=-1)

    rings = []
    for j in range(n_front + 1):
        r = 0.06 + 0.94 * j / n_front
        p = c[0] + r * (outline[:, 0] - c[0])
        q = c[1] + r * (outline[:, 1] - c[1])
        hh = _relief(np.full(n_ang, r), root, s)
        # tragus: a small flap in front of the concha
        trag = 0.0022 * s * np.exp(-((ang - math.pi * 0.97) / 0.35) ** 2) * np.exp(-((r - 0.55) / 0.2) ** 2)
        rings.append(to_world(p, q, hh + trag))
    for j in range(1, n_back + 1):
        r = 1.0 - 0.55 * j / n_back
        p = c[0] + r * (outline[:, 0] - c[0])
        q = c[1] + r * (outline[:, 1] - c[1])
        hh = -0.0016 * s * np.ones(n_ang) - 0.004 * s * (1.0 - r) + 0.0024 * s * (j == 1)
        rings.append(to_world(p, q, hh * (1.0 - 0.9 * root)))
    ids = [[part.add_v(P, tag=tag) for P in ring] for ring in rings]
    nr = len(rings)
    for j in range(nr - 1):
        for i in range(n_ang):
            i2 = (i + 1) % n_ang
            q = [ids[j][i], ids[j][i2], ids[j + 1][i2], ids[j + 1][i]]
            uv = [(i / n_ang, j / (nr - 1)), ((i + 1) / n_ang, j / (nr - 1)), ((i + 1) / n_ang, (j + 1) / (nr - 1)),
                  (i / n_ang, (j + 1) / (nr - 1))]
            if sgn < 0:
                q, uv = q[::-1], uv[::-1]
            part.add_f(q, uv, "skin_head")
    # cap the concha floor
    cfl = part.add_v(to_world(np.array([c[0]]), np.array([c[1]]), np.array([-0.0072 * s]))[0], tag=tag)
    for i in range(n_ang):
        i2 = (i + 1) % n_ang
        q = [cfl, ids[0][i2], ids[0][i]]
        if sgn < 0:
            q = q[::-1]
        part.add_f(q, [(0.5, 0.0)] * 3, "skin_head")
    part.seam_rings = [ids[n_front]]  # cut front from back along the rim for UVs
    return part
