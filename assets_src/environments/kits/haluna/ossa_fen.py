"""Ossa Fen, the Kirru mangrove estuary (ossa_fen.md §1-§2; M3-ENV-718): the Mangrove Drowner's arena pieces.
Pure numpy.

Built in the Haluna kit (its import kind and materials directory, as iskarra.py, keth.py and lowlight.py), with
`kit_fen_*` materials. The trees use the vegetation shaders' contract (vegetation_wind.gdshaderinc): COLOR.r sway
weight, .g secondary bob, .b phase, .a flutter; UV2.x occlusion, UV2.y tint. Their leaves are cards cut from the
coastal leaf atlas (veg_common.COASTAL_ATLAS's banyan sprays), tinted grey-green by `kit_fen_leaf`.

  fen_bank_ground     (arena frame) the mudbank in the channels, 120 x 110 m heightfield: a level top at y 0 round
                      the battle floor, shelving into the tannin water (-0.15) and the channels, a low mound under
                      each mangrove; small surface roots on the mud, kept off the slots' floor.
  mangrove_tree       a living mangrove: 12 arched prop-roots from the trunk into the mud, a leaning trunk forking
                      into five boughs, a crown of leaf clusters; origin at the roots' foot (the mud line); 9 m.
  mangrove_dead       the Drowner's tree: a great dead mangrove, its crown bare and bleached, the boughs broken; its
                      prop-roots only on the far side (the creature is the cage on the near side); 14 m.
  reed_bed            slack-water reeds, crossed two-sided blade cards, 1.2-2.1 m, about 6 x 4 m.
  fen_far_mangroves   the far tree-line round the channels: a low canopy band, r 70-110 m.

Nothing green grows on the dead tree (mangrove_drowner.md).
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc

M_MUD = "kit_fen_mud"
M_BARK = "kit_fen_bark"
M_BARK_DEAD = "kit_fen_bark_dead"
M_LEAF = "kit_fen_leaf"
M_REED = "kit_fen_reed"
M_FAR = "kit_fen_canopy_far"

TRI_BUDGET = {"fen_bank_ground": (30000, 2400), "mangrove_tree": (10000, 900), "mangrove_dead": (12000, 900),
              "reed_bed": (3000, 300), "fen_far_mangroves": (4000, 800)}

WATER_Y = -0.15
BANK = (-5.4, 6.8, -4.0, 5.0)  # x0, x1, z0, z1 of the bank's level top: the slots' metre and more
BANK_ROUND = 1.2  # how far the top stays level past its edges before shelving
MANGROVES = ((10.5, -7.0, 20.0, 1.0), (13.5, 2.0, 140.0, 0.9), (-14.0, 1.0, 250.0, 1.1), (3.5, -13.0, 80.0, 1.05),
             (-3.0, -15.5, 300.0, 0.95), (12.0, 10.0, 200.0, 0.85), (-12.5, 10.5, 30.0, 0.9), (20.0, -12.0, 0.0, 1.2),
             (-20.0, -9.0, 160.0, 1.15))  # (x, z, yaw, scale) of the living trees round the bank
DEAD_AT = (-9.5, -7.5)  # the dead tree's foot; it leans over the Drowner
DROWNER_AT = (-8.2, WATER_Y, -3.8)  # the boss anchor: in the water at the dead tree's foot
SPRAY_M = 0.8  # metres covered by a banyan spray cell's height (veg_common.COASTAL_SPRAY_M["banyan"])
SPRAYS = ((0.0, 0.0, 0.5, 0.5), (0.5, 0.0, 1.0, 0.5))  # veg_common.COASTAL_ATLAS banyan_spray_a, _b
MUD = kc.Weathering(moss=0.1, salt=0.0, wet=0.8, erosion=0.3, noise_scale_m=2.0)


# ---------------------------------------------------------------------------------------------
# The bank
# ---------------------------------------------------------------------------------------------
def _bank_distance(X, Z) -> np.ndarray:
    """Distance (m) outside the bank's rounded level top (0 inside)."""
    x0, x1, z0, z1 = BANK
    dx = np.maximum(np.maximum(x0 - X, X - x1), 0.0)
    dz = np.maximum(np.maximum(z0 - Z, Z - z1), 0.0)
    return np.hypot(dx, dz)


def bank_height(X, Z, noise: kc.Noise3) -> np.ndarray:
    X, Z = np.asarray(X, float), np.asarray(Z, float)
    n = noise.fbm(np.stack([X / 9.0, np.zeros_like(X), Z / 9.0], -1), 4) - 0.5
    d = _bank_distance(X, Z)
    # The bank shelves into the water past BANK_ROUND, then into the channels; deepest behind the camera (the
    # channel the party came up) and out past the trees.
    h = -0.55 * kc.smoothstep(BANK_ROUND, BANK_ROUND + 3.5, d) - 1.1 * kc.smoothstep(BANK_ROUND + 6.0, 26.0, d)
    h = h - 0.8 * kc.smoothstep(9.0, 20.0, Z) + n * 0.5 * kc.smoothstep(BANK_ROUND, BANK_ROUND + 4.0, d)
    # A low mud mound under each living tree (the roots' footing). The dead tree stands in the water, as the
    # Drowner in its roots does.
    for x, z, _yaw, s in MANGROVES:
        r = np.hypot(X - x, Z - z)
        h = np.maximum(h, -0.05 - 0.25 * kc.smoothstep(2.5 * s, 5.0 * s, r) - 2.0 * kc.smoothstep(5.0 * s, 9.0 * s, r)
                       + n * 0.15)
    return np.where(d <= BANK_ROUND, 0.0, h)


def _axis(lo, hi, f0, f1, fine, coarse_n):
    return np.unique(np.concatenate([np.linspace(lo, f0, coarse_n), np.arange(f0, f1, fine), np.linspace(f1, hi, coarse_n)]))


def _surface_roots(mb, rng, noise) -> None:
    """Small mangrove surface roots crossing the mud: low arcs, never on the slots' floor."""
    x0, x1, z0, z1 = BANK
    k = 0
    while k < 26:
        a = np.array([rng.uniform(x0 - 4.0, x1 + 4.0), 0.0, rng.uniform(z0 - 4.0, z1 + 3.0)])
        inside = (x0 + 1.0 < a[0] < x1 - 1.0) and (z0 + 1.0 < a[2] < z1 - 1.0)
        if inside:
            continue
        th = rng.uniform(0, 2 * math.pi)
        ln = rng.uniform(1.2, 3.0)
        t = np.linspace(0.0, 1.0, 7)
        pts = a + np.stack([np.cos(th) * ln * t, 0.02 + 0.07 * np.sin(t * math.pi), np.sin(th) * ln * t], -1)
        kc.tube(mb, pts, np.linspace(0.045, 0.015, 7), 5, mb.material(M_BARK), noise=noise, disp_m=0.008,
                weather=MUD)
        k += 1


def build_ground(seed: int = 1801) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("fen_bank_ground", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("fen_bank_ground" + ("-lod1" if lod else ""))
        if lod:
            xs, zs = np.linspace(-60.0, 60.0, 33), np.linspace(-60.0, 50.0, 31)
        else:
            xs = _axis(-60.0, 60.0, -24.0, 24.0, 0.75, 10)
            zs = _axis(-60.0, 50.0, -22.0, 16.0, 0.75, 10)
        X, Z = np.meshgrid(xs, zs)
        Y = bank_height(X, Z, noise)
        P = np.stack([X, Y, Z], -1)
        brk = noise.fbm(P / 2.0, 2)
        col = np.stack([np.zeros_like(Y), np.full_like(Y, 0.1), np.clip(0.9 - Y * -0.5, 0, 1), 0.4 + 0.4 * brk], -1)
        kc.quad_strip(mb, P, mb.material(M_MUD), uv=np.stack([X, Z], -1) / 3.0, col=col, uv2=np.array([0.9, 0.5]),
                      flip=True)
        if not lod:
            _surface_roots(mb, rng, noise)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# The trees
# ---------------------------------------------------------------------------------------------
def _wind(mb: kc.MeshBuilder, start: int, height_m: float, *, sway: bool = True, phase: float = 0.0,
          flutter: float = 0.0, occlusion: float = 1.0, tint: float = 0.5) -> None:
    """Writes the vegetation shaders' wind weights and occlusion into the vertices added since `start`."""
    p = np.asarray(mb.pos[start:])
    if len(p) == 0:
        return
    w = np.clip(p[:, 1] / height_m, 0.0, 1.0) ** 1.5 if sway else np.zeros(len(p))
    col = np.stack([w, w * 0.8, np.full(len(p), phase % 1.0), np.full(len(p), flutter)], -1)
    mb.col[start:] = col.tolist()
    mb.uv2[start:] = [[occlusion, tint]] * len(p)


def _bezier(a, b, c, n):
    t = np.linspace(0.0, 1.0, n)[:, None]
    return (1 - t) ** 2 * a + 2 * (1 - t) * t * b + t ** 2 * c


def _prop_roots(mb, rng, noise, trunk_foot, n, r0, r1, mat, *, lod: bool, arc: tuple[float, float] = (0.0, 2 * math.pi),
                height=(1.2, 2.4)) -> None:
    """Arched prop-roots: each leaves the trunk at 1.2-2.4 m and arches out and down into the mud at r0-r1."""
    for k in range(n):
        th = arc[0] + (arc[1] - arc[0]) * (k + rng.uniform(0.2, 0.8)) / n
        dirv = np.array([math.cos(th), 0.0, math.sin(th)])
        top = trunk_foot + np.array([0.0, rng.uniform(*height), 0.0]) + dirv * 0.25
        foot = trunk_foot + dirv * rng.uniform(r0, r1) + np.array([0.0, -0.35, 0.0])
        knee = top + dirv * (np.linalg.norm(foot - top) * 0.55) + np.array([0.0, rng.uniform(0.3, 0.7), 0.0])
        pts = _bezier(top, knee, foot, 5 if lod else 11)
        radii = np.linspace(rng.uniform(0.1, 0.14), rng.uniform(0.05, 0.08), len(pts))
        kc.tube(mb, pts, radii, 4 if lod else 7, mat, noise=None if lod else noise, disp_m=0.01, v_scale=1.0 / 1.4,
                u_repeat=2.0)


def _bough(mb, rng, noise, start, direction, length, radius, depth, mat, ends, *, lod: bool, bare: bool) -> None:
    """A bough and its forks, recursively; the twig ends are collected in `ends`."""
    d = kc.normalize(direction + rng.normal(0.0, 0.18, 3) * np.array([1.0, 0.4, 1.0]))
    n = 3 if lod else 6
    mid = start + d * length * 0.5 + rng.normal(0.0, length * 0.06, 3)
    end = start + d * length
    pts = _bezier(start, mid, end, n)
    kc.tube(mb, pts, np.linspace(radius, radius * 0.62, n), 4 if lod else (6 if depth < 2 else 4), mat,
            noise=None if (lod or depth > 1) else noise, disp_m=0.01, v_scale=1.0 / 1.4, u_repeat=2.0)
    if depth >= (2 if lod else 3) or radius < 0.035:
        ends.append((end, d))
        return
    for _k in range(2 if bare or lod else 3):
        nd = d + rng.normal(0.0, 0.55, 3) * np.array([1.0, 0.5, 1.0]) + np.array([0.0, 0.15, 0.0])
        _bough(mb, rng, noise, end, nd, length * rng.uniform(0.55, 0.75), radius * 0.62, depth + 1, mat, ends,
               lod=lod, bare=bare)


def _leaf_cluster(mb, rng, centre, n: int, radius: float, height_m: float, *, phase: float) -> None:
    """A clump of leaf cards (banyan sprays from the coastal atlas) round a twig end, facing out and up."""
    mat = mb.material(M_LEAF)
    for _k in range(n):
        u = kc.normalize(rng.normal(0.0, 1.0, 3) * np.array([1.0, 0.55, 1.0]) + np.array([0.0, 0.35, 0.0]))
        c = centre + u * radius * rng.uniform(0.35, 1.0)
        rect = SPRAYS[int(rng.integers(0, 2))]
        h = SPRAY_M * rng.uniform(0.85, 1.15)
        w = h * (rect[2] - rect[0]) / (rect[3] - rect[1])
        side = kc.normalize(np.cross(u, np.array([0.0, 1.0, 0.0])) + rng.normal(0.0, 0.2, 3))
        up = kc.normalize(np.cross(side, u) * 0.6 + u * 0.4)
        grid = np.array([[c - side * w * 0.5, c + side * w * 0.5],
                         [c - side * w * 0.5 + up * h, c + side * w * 0.5 + up * h]])
        uv = np.array([[[rect[0], rect[3]], [rect[2], rect[3]]], [[rect[0], rect[1]], [rect[2], rect[1]]]])
        start = mb.vertex_count
        kc.quad_strip(mb, grid, mat, uv=uv, col=(0, 0, 0, 0), uv2=(1.0, 0.5), smooth=False)
        occ = 0.55 + 0.45 * float(np.clip(np.dot(u, [0.0, 1.0, 0.0]) * 0.5 + 0.5, 0.0, 1.0))
        _wind(mb, start, height_m, phase=phase + rng.uniform(0.0, 0.3), flutter=0.7, occlusion=occ,
              tint=float(rng.random()))


def build_tree(seed: int = 1802) -> list[kc.MeshBuilder]:
    out = []
    height = 9.0
    for lod in (False, True):
        rng = kc.rng_for("mangrove_tree", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("mangrove_tree" + ("-lod1" if lod else ""))
        bark = mb.material(M_BARK)
        foot = np.array([0.0, 0.0, 0.0])
        start = mb.vertex_count
        _prop_roots(mb, rng, noise, foot, 8 if lod else 12, 1.8, 3.2, bark, lod=lod)
        _wind(mb, start, height, sway=False)
        start = mb.vertex_count
        lean = np.array([0.35, 0.0, 0.1])
        trunk = _bezier(foot + [0.0, 1.0, 0.0], foot + [0.15, 3.0, 0.05], foot + lean * 4.0 + [0.0, 5.0, 0.0],
                        4 if lod else 8)
        kc.tube(mb, trunk, np.linspace(0.32, 0.24, len(trunk)), 5 if lod else 9, bark, noise=None if lod else noise,
                disp_m=0.015, v_scale=1.0 / 1.4, u_repeat=2.0)
        ends: list = []
        for k in range(5):
            th = 2 * math.pi * (k + rng.uniform(0.0, 0.6)) / 5
            d = np.array([math.cos(th), 1.0, math.sin(th)])
            _bough(mb, rng, noise, trunk[-1], d, rng.uniform(1.6, 2.4), 0.16, 1, bark, ends, lod=lod, bare=False)
        _wind(mb, start, height, phase=0.0)
        for k, (e, d) in enumerate(ends):
            _leaf_cluster(mb, rng, e + d * 0.2, 6 if lod else 16, 1.0 if lod else 0.85, height, phase=k * 0.13)
        out.append(mb)
    return out


def build_dead(seed: int = 1803) -> list[kc.MeshBuilder]:
    """Leans toward the Drowner (it sits at the tree's foot on that side); prop-roots only on the far half."""
    out = []
    height = 14.0
    for lod in (False, True):
        rng = kc.rng_for("mangrove_dead", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("mangrove_dead" + ("-lod1" if lod else ""))
        bark = mb.material(M_BARK_DEAD)
        foot = np.array([0.0, 0.0, 0.0])
        lean = kc.normalize(np.array([DROWNER_AT[0] - DEAD_AT[0], 0.0, DROWNER_AT[2] - DEAD_AT[1]]))  # placed at yaw 0
        start = mb.vertex_count
        # Roots on the far side only (away from the lean): the near side is the creature's.
        far = math.atan2(-lean[2], -lean[0])
        _prop_roots(mb, rng, noise, foot, 7 if lod else 14, 2.4, 4.6, bark, lod=lod, arc=(far - 1.6, far + 1.6),
                    height=(1.8, 3.4))
        trunk = _bezier(foot + [0.0, 1.6, 0.0], foot + lean * 1.2 + [0.0, 4.5, 0.0], foot + lean * 3.4 + [0.0, 8.5, 0.0],
                        5 if lod else 10)
        kc.tube(mb, trunk, np.linspace(0.62, 0.42, len(trunk)), 6 if lod else 11, bark, noise=None if lod else noise,
                disp_m=0.03, v_scale=1.0 / 1.4, u_repeat=2.0)
        ends: list = []
        for k in range(6):
            th = 2 * math.pi * (k + rng.uniform(0.0, 0.5)) / 6
            d = np.array([math.cos(th) * 1.1, 0.8, math.sin(th) * 1.1]) + lean * 0.5
            ln = rng.uniform(2.6, 3.6) * (0.55 if k == 2 else 1.0)  # one bough broken short
            _bough(mb, rng, noise, trunk[-1], d, ln, 0.26, 1, bark, ends, lod=lod, bare=True)
        # Bare twig ends: thin spurs, no leaves.
        if not lod:
            for e, d in ends:
                kc.tube(mb, np.stack([e, e + kc.normalize(d + rng.normal(0, 0.4, 3)) * rng.uniform(0.4, 0.9)]),
                        np.array([0.025, 0.008]), 3, bark)
        _wind(mb, start, height, phase=0.4)  # a bare crown still moves a little in the dusk air
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Reeds and the far tree-line
# ---------------------------------------------------------------------------------------------
def build_reeds(seed: int = 1804) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("reed_bed", seed)
        mb = kc.MeshBuilder("reed_bed" + ("-lod1" if lod else ""))
        mat = mb.material(M_REED)
        for _k in range(40 if lod else 260):
            c = np.array([rng.normal(0.0, 1.5), WATER_Y - 0.2, rng.normal(0.0, 1.0)])
            h = rng.uniform(1.2, 2.1)
            yaw = rng.uniform(0, math.pi)
            d = np.array([math.cos(yaw), 0.0, math.sin(yaw)]) * (0.05 if not lod else 0.25)
            lean = np.array([rng.normal(0, 0.2), 0.0, rng.normal(0, 0.2)])
            grid = np.array([[c - d, c + d], [c - d * 0.2 + [0, h, 0] + lean, c + d * 0.2 + [0, h, 0] + lean]])
            start = mb.vertex_count
            kc.quad_strip(mb, grid, mat, uv=np.array([[[0, 0], [1, 0]], [[0, 1], [1, 1]]]), col=(0, 0, 0, 0),
                          uv2=(1.0, 0.5), smooth=False)
            _wind(mb, start, 2.0, phase=float(rng.random()), flutter=0.2, tint=float(rng.random()))
        out.append(mb)
    return out


def build_far(seed: int = 1805) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("fen_far_mangroves", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("fen_far_mangroves" + ("-lod1" if lod else ""))
        a = np.linspace(0.0, 2 * math.pi, (64 if lod else 180) + 1)
        rs = np.array([70.0, 72.0, 85.0, 110.0])
        A, R = np.meshgrid(a, rs)
        n = noise.fbm(np.stack([np.cos(A) * 9.0, R / 40.0, np.sin(A) * 9.0], -1), 4)
        top = 7.0 + 9.0 * n  # the canopy's crown line, 7-16 m
        Y = np.stack([np.full_like(top[0], -1.0), top[1], top[2] + 2.0, top[3] + 3.0])  # a skirt into the water
        grid = np.stack([R * np.sin(A), Y, -R * np.cos(A)], -1)
        col = np.zeros(Y.shape + (4,))
        kc.quad_strip(mb, grid, mb.material(M_FAR), uv=np.stack([A * 50.0, Y / 10.0], -1), col=col,
                      uv2=np.array([1.0, 0.5]), flip=False)
        out.append(mb)
    return out


TARGETS = {
    "fen_bank_ground": build_ground,
    "mangrove_tree": build_tree,
    "mangrove_dead": build_dead,
    "reed_bed": build_reeds,
    "fen_far_mangroves": build_far,
}
