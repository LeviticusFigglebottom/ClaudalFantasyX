"""Toma's props (no bpy), toma.md §2, §4 #7-#8 and §9: the tide-shield and the hooked boarding spear.

* **Tide-shield**: a domed disc 0.92 m across and 12 cm deep, slung on his back (rigid on the chest
  bone, build_toma). A polar grid over a paraboloid dome, a 7 cm rim band rolled over the edge to a
  shallower wooden back, and a bronze boss 14 cm across. The 13 scutes are a Voronoi pattern relaxed
  on the disc (`scute_seeds`: seeded random points, Lloyd-relaxed; no real species' layout is
  copied); each scute bulges a few millimetres with a groove along its borders, and toma_textures
  paints the same cells (growth rings, mottling) on the shield's own 2K atlas. UV = the disc's plan.
* **Hooked spear**: an ash shaft (2.10 m overall) grounded at his right side and held in the right
  hand (rigid on DEF-hand.R, like Asha's staff), a steel leaf head with a 12 cm side hook that curls
  back down, a bronze ferrule and collar, and an indigo cord grip binding.

Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_mesh import Part, grid, tube
from asha_staff import held_frame, to_held

TAG_PROP = 62
SHIELD_RINGS = 22
SHIELD_SEGS = 60
SHIELD_BACK_DEPTH = 0.035  # m: the wooden back sits this far in from the rim's front at the edge
SCUTE_BULGE = 0.004  # m
SCUTE_GROOVE = 0.0025  # m
SCUTE_GROOVE_W = 0.012  # m, half-width of the groove along a scute border
BOSS_RINGS = 7
SPEAR_SHAFT_R = 0.016
SPEAR_HEAD_L = 0.26  # blade, socket included
SHIELD_ATLAS_DISC = (0.0, 0.0, 1.0, 1.0)  # the disc fills the square; the back uses the free corner
SHIELD_ATLAS_BACK = (0.0, 0.0, 0.12, 0.12)


def scute_seeds(params: dict, iters: int = 40) -> np.ndarray:
    """13 cell centres (disc coordinates, metres from the centre) inside the scute field (radius R -
    rim): one draw of seeded random points, Lloyd-relaxed on a sample grid of the disc."""
    R = 0.5 * float(params["shield_diameter_m"]) - float(params["shield_rim_m"])
    n = int(params["shield_scutes"])
    rng = np.random.default_rng([int(params["seed"]), 21])
    r = R * np.sqrt(rng.uniform(0.0, 0.85, n))
    a = rng.uniform(0.0, 2 * math.pi, n)
    P = np.stack([r * np.cos(a), r * np.sin(a)], axis=1)
    g = np.linspace(-R, R, 121)
    X, Y = np.meshgrid(g, g)
    S = np.stack([X.ravel(), Y.ravel()], axis=1)
    S = S[np.hypot(S[:, 0], S[:, 1]) < R]
    for _ in range(iters):
        k = np.argmin(((S[:, None, :] - P[None, :, :]) ** 2).sum(axis=2), axis=1)
        for i in range(n):
            m = k == i
            if m.any():
                P[i] = S[m].mean(axis=0)
    return P


def scute_field(seeds: np.ndarray, Q: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(cell index, distance to the cell border in metres, distance to the cell centre) for disc
    points Q (n, 2). The border distance is the bisector distance to the nearest other seed."""
    d2 = ((Q[:, None, :] - seeds[None, :, :]) ** 2).sum(axis=2)
    order = np.argsort(d2, axis=1)
    i1 = order[:, 0]
    p1 = seeds[i1]
    best = np.full(len(Q), np.inf)
    for j in range(1, min(5, len(seeds))):
        p2 = seeds[order[:, j]]
        dvec = p2 - p1
        L = np.maximum(np.linalg.norm(dvec, axis=1), 1e-9)
        mid = 0.5 * (p1 + p2)
        best = np.minimum(best, np.sum((mid - Q) * dvec, axis=1) / L)
    return i1, np.maximum(best, 0.0), np.sqrt(d2[np.arange(len(Q)), i1])


def shield_profile(params: dict, r: np.ndarray) -> np.ndarray:
    """Height of the front surface above the rim plane at radius r (m)."""
    R = 0.5 * float(params["shield_diameter_m"])
    H = float(params["shield_dome_m"])
    rim = float(params["shield_rim_m"])
    x = np.clip(r / R, 0.0, 1.0)
    dome = H * (1.0 - x ** 2) ** 1.15
    # the rim band: the dome flattens into a raised lip, then rolls over the edge
    lip = 0.006 * np.exp(-((r - (R - 0.5 * rim)) / (0.35 * rim)) ** 2)
    return dome + lip


def shield(centre: np.ndarray, out: np.ndarray, up: np.ndarray, params: dict, rings: int = SHIELD_RINGS,
           segs: int = SHIELD_SEGS) -> Part:
    """The shield with its rim plane centred at `centre`, the dome bulging toward `out`, `up` its top. M3-CHR-507:
    `rings` and `segs` set the disc's resolution (Moll's smaller, smooth round shield); the defaults are Toma's."""
    part = Part("Shield")
    R = 0.5 * float(params["shield_diameter_m"])
    rim = float(params["shield_rim_m"])
    out = out / np.linalg.norm(out)
    up = up - (up @ out) * out
    up /= np.linalg.norm(up)
    right = np.cross(up, out)
    seeds = scute_seeds(params)
    boss_r = 0.5 * float(params["shield_boss_m"])
    nr, ns = rings, segs
    rr = boss_r * 0.85 + (R - boss_r * 0.85) * (np.linspace(0.0, 1.0, nr) ** 0.9)
    ang = 2 * math.pi * np.arange(ns) / ns
    X = rr[:, None] * np.cos(ang)[None, :]
    Y = rr[:, None] * np.sin(ang)[None, :]
    Q = np.stack([X.ravel(), Y.ravel()], axis=1)
    h = shield_profile(params, np.hypot(Q[:, 0], Q[:, 1]))
    _, border, _ = scute_field(seeds, Q)
    inside = np.hypot(Q[:, 0], Q[:, 1]) < R - rim
    bump = (SCUTE_BULGE * np.clip(border / 0.06, 0.0, 1.0) ** 0.6
            - SCUTE_GROOVE * np.exp(-(border / SCUTE_GROOVE_W) ** 2)) * inside
    h = h + bump
    P = centre + np.outer(Q[:, 0], right) + np.outer(Q[:, 1], up) + np.outer(h, out)
    P = P.reshape(nr, ns, 3)
    u0, v0, u1, v1 = SHIELD_ATLAS_DISC

    def uv_disc(j, i):
        q = Q.reshape(nr, ns, 2)[j, i % ns]
        return (u0 + (u1 - u0) * (0.5 + 0.5 * q[0] / R), v0 + (v1 - v0) * (0.5 - 0.5 * q[1] / R))

    grid(part, P[::-1], "shield", closed_u=True, tags=TAG_PROP, uv_fn=lambda j, i: uv_disc(nr - 1 - j, i))
    # the rim rolled over the edge to the back: a few rings round the lip
    roll = []
    for f in np.linspace(0.0, 1.0, 5)[1:]:
        a = f * math.pi * 0.5
        rad = R + 0.008 * math.sin(a)
        hh = shield_profile(params, np.array([R]))[0] * math.cos(a) - SHIELD_BACK_DEPTH * f ** 1.5
        roll.append(centre + np.outer(rad * np.cos(ang), right) + np.outer(rad * np.sin(ang), up) + out * hh)
    E = np.stack([P[-1]] + roll, axis=0)
    grid(part, E, "shield", closed_u=True, tags=TAG_PROP,
         uv_fn=lambda j, i: (u0 + (u1 - u0) * (0.5 + 0.495 * math.cos(ang[i % ns])),
                             v0 + (v1 - v0) * (0.5 - 0.495 * math.sin(ang[i % ns]))))
    # the wooden back: a shallow cone from the rolled edge to a flat centre, facing his back
    bu0, bv0, bu1, bv1 = SHIELD_ATLAS_BACK
    back_r = np.linspace(R + 0.008, 0.0, 8)
    back = np.stack([centre + np.outer(rb * np.cos(ang), right) + np.outer(rb * np.sin(ang), up)
                     + out * (-SHIELD_BACK_DEPTH + 0.03 * (1.0 - rb / R)) for rb in back_r])
    grid(part, back, "shield", closed_u=True, tags=TAG_PROP, flip=True,
         uv_fn=lambda j, i: (bu0 + (bu1 - bu0) * i / ns, bv0 + (bv1 - bv0) * j / 7))
    # the bronze boss: a low dome with a flange
    top = centre + out * shield_profile(params, np.array([0.0]))[0]
    prof = [(boss_r, -0.004), (boss_r * 0.96, 0.006), (boss_r * 0.80, 0.012), (boss_r * 0.62, 0.030),
            (boss_r * 0.40, 0.042), (boss_r * 0.18, 0.048), (0.0, 0.050)]
    B = np.stack([top + np.outer(rb * np.cos(ang[::2]), right) + np.outer(rb * np.sin(ang[::2]), up) + out * hb
                  for rb, hb in prof])
    grid(part, B, "bronze", (0.0, 0.0, 0.1, 0.1), closed_u=True, tags=TAG_PROP)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part


SHIELD_CLEAR = 0.012  # m between the shield's back and the costume under it
SHIELD_HEAD_CLEAR = 0.035  # m between the shield's back and the head skin (hair cards, a nod back)
SHIELD_TILT = -0.08  # the shield's up axis leans this much toward his front at the top (it rests on the shoulders)
SHIELD_DROP = 0.05  # m: the shield's centre sits this far below nipple height


def place_shield(params: dict, outer: np.ndarray, chest_z: float,
                 head: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(centre, out, up) of the shield on his back: tilted by SHIELD_TILT, its centre SHIELD_DROP
    below the chest line, and pushed back until its wooden back clears every costume vertex
    (`outer`: the pauldron, harness, tunic, sash ...) inside its footprint by SHIELD_CLEAR."""
    R = 0.5 * float(params["shield_diameter_m"])
    up = np.array([0.0, SHIELD_TILT, 1.0])
    up /= np.linalg.norm(up)
    out = np.cross(up, np.array([1.0, 0.0, 0.0]))  # +Y (behind him), tilted with `up`
    out /= np.linalg.norm(out)
    z_c = chest_z - SHIELD_DROP
    c0 = np.array([0.0, 0.0, z_c])
    q = outer - c0
    inplane = q - np.outer(q @ out, out)
    near = np.linalg.norm(inplane, axis=1) < R + 0.01
    need = float((q[near] @ out).max()) + SHIELD_BACK_DEPTH + SHIELD_CLEAR
    if head is not None:
        # M1-CHR-14: the top of the rim also clears the back of the head (and his cropped hair) by SHIELD_HEAD_CLEAR
        qh = head - c0
        near_h = np.linalg.norm(qh - np.outer(qh @ out, out), axis=1) < R + 0.01
        if near_h.any():
            need = max(need, float((qh[near_h] @ out).max()) + SHIELD_BACK_DEPTH + SHIELD_HEAD_CLEAR)
    return c0 + out * need, out, up


def _blade_section(c: np.ndarray, side: np.ndarray, nrm: np.ndarray, w: float, th: float) -> np.ndarray:
    """A lens section: the edges at +-w along `side`, the spine th thick along `nrm`."""
    return np.array([c + side * w, c + nrm * th, c - side * w, c - nrm * th])


def spear_grip(lm) -> np.ndarray:
    """Where the right hand closes on the shaft (the spear's prop bone sits here, build_toma): the fist's hole."""
    return held_frame(lm, "R", SPEAR_SHAFT_R)[0]


def spear_axis(lm) -> np.ndarray:
    """M2-CHR-515: the held shaft's line at rest (through the fist, towards the thumb), towards the blade."""
    return held_frame(lm, "R", SPEAR_SHAFT_R)[1] @ np.array([0.0, 0.0, 1.0])


def spear(lm, params: dict, cord_rect) -> Part:
    """Built upright through the right fist's hole and grounded, the hook facing away from his body (-X), then turned
    into the held line (M2-CHR-515, asha_staff.held_frame: the clips pitch his hand to stand it upright; held on the
    bent arm it stands forward of his feet, so the M1-CHR-14/15 splay and rake are gone)."""
    part = Part("Spear")
    grip, R = held_frame(lm, "R", SPEAR_SHAFT_R)
    L = float(params["spear_length_m"])
    upv = np.array([0.0, 0.0, 1.0])
    base = grip - upv * ((grip[2] - 0.006) / upv[2])
    fwd = np.array([0.0, -1.0, 0.0])
    side = np.array([-1.0, 0.0, 0.0])  # the hook and the blade's flats face out from his right side
    shaft_top = L - SPEAR_HEAD_L + 0.06
    n = 24
    shaft = np.array([base + upv * shaft_top * t for t in np.linspace(0.0, 1.0, n)])
    rad = SPEAR_SHAFT_R * (1.0 - 0.10 * np.linspace(0, 1, n))
    from toma_costume import ATLAS

    tube(part, shaft, rad, 12, "cloth", fwd, ATLAS["spear_shaft"], tags=TAG_PROP)
    # grip binding: indigo cord round the shaft at the hand
    g0, g1 = grip[2] - 0.20, grip[2] + 0.04  # ends just above the fist (it ran 11 cm up into the wrist)
    cord = np.array([base + upv * ((z - base[2]) / upv[2]) for z in np.linspace(g0, g1, 10)])
    tube(part, cord, SPEAR_SHAFT_R * 1.14, 12, "cloth", fwd, cord_rect, tags=TAG_PROP)
    # bronze ferrule at the foot and collar under the head
    tube(part, np.array([base, base + upv * 0.06]), SPEAR_SHAFT_R * 1.12, 12, "bronze", fwd, tags=TAG_PROP)
    col = base + upv * (shaft_top - 0.07)
    tube(part, np.array([col, col + upv * 0.05]), SPEAR_SHAFT_R * 1.18, 12, "bronze", fwd, tags=TAG_PROP)
    # steel socket and leaf blade
    s0 = base + upv * (shaft_top - 0.02)
    tube(part, np.array([s0, s0 + upv * 0.07]), np.array([SPEAR_SHAFT_R * 1.05, SPEAR_SHAFT_R * 0.8]), 10, "steel",
         fwd, tags=TAG_PROP)
    b0 = s0 + upv * 0.07
    blade_l = L - (shaft_top + 0.05)
    m = 12
    secs = []
    for k in range(m):
        t = k / (m - 1)
        w = 0.034 * math.sin(math.pi * min(t * 1.25 + 0.08, 1.0)) ** 0.8 * (1.0 - t) ** 0.25 + 0.002
        secs.append(_blade_section(b0 + upv * blade_l * t, fwd, side, w, 0.0045 * (1.0 - 0.7 * t) + 0.0008))
    grid(part, np.array(secs), "steel", closed_u=True, tags=TAG_PROP)
    # the side hook: out of the socket, then curling back down (a 12 cm boarding hook)
    hook = float(params["spear_hook_m"])
    # a cubic Bezier in (out, up), scaled by the hook length: out and a little up, then down to a point
    ctrl = np.array([(0.10, 0.33), (0.58, 0.58), (1.04, 0.33), (0.92, -0.25)]) * hook
    pts = []
    for t in np.linspace(0.0, 1.0, 10):
        b = ((1 - t) ** 3 * ctrl[0] + 3 * (1 - t) ** 2 * t * ctrl[1] + 3 * (1 - t) * t ** 2 * ctrl[2]
             + t ** 3 * ctrl[3])
        pts.append(s0 + side * b[0] + upv * b[1])
    pts = np.array(pts)
    tube(part, pts, np.linspace(0.0085, 0.0025, len(pts)), 8, "steel", fwd, tags=TAG_PROP)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return to_held(part, grip, R)
