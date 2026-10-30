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
  kirru_roost         a Kirru roost-lodge (bible §5.5): a barrel of bundled-reed arches and woven reed panels, 5 m long,
                      2.8 m inside (the Kirru stand 2.1-2.4 m), open at its +Z end, on a lashed pole deck 1.2 m over
                      the water on four mangrove-pole legs; origin at the legs' foot centre.
  mangrove_tall, mangrove_low, mangrove_young   the zones' mangrove variants (MANGROVE_VARIANTS), from build_tree
  name_shell_cord     the clutch's name-shells on a cord between two poles at the water's edge, 6 m: each a carved
                      shell token, one scraped blank (an exile's). The living's own: the Kirru keep nothing of their
                      dead (bible §8).

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
M_WEAVE = "kit_woven_panel"
M_LASH = "kit_lashing"
M_SHELL = "kit_nacre"

TRI_BUDGET = {"fen_bank_ground": (30000, 2400), "mangrove_tree": (10000, 900), "mangrove_dead": (12000, 900),
              "reed_bed": (3000, 300), "fen_far_mangroves": (4000, 800), "kirru_roost": (9000, 700),
              "name_shell_cord": (3000, 250), "mangrove_tall": (11000, 900), "mangrove_low": (10000, 900),
              "mangrove_young": (5000, 500)}

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


SLOTS_XZ = ((2.1, 0.7), (3.0, -1.1), (1.4, 2.0), (-2.4, 0.9), (-3.4, -1.2), (-1.2, -0.6))  # battle_arenas.md


def _bank_litter(mb, rng) -> None:
    """The bank top's litter (M3-ENV-705 audit: c990e2c read the battle floor as bare mud): fallen mangrove leaves
    lying flat, twigs, crab holes and shallow mud puddles, all low (under 4 cm) and 1.3 m clear of every slot."""
    x0, x1, z0, z1 = BANK
    leaf, bark, dark = mb.material(M_LEAF), mb.material(M_BARK), mb.material("kit_interior_dark")
    puddle = mb.material("kit_water_spill")

    def clear(x, z, r=1.3):
        return all(math.hypot(x - sx, z - sz) > r for sx, sz in SLOTS_XZ)

    for _ in range(260):  # leaves: small flat two-sided cards
        x, z = rng.uniform(x0, x1), rng.uniform(z0, z1)
        if not clear(x, z):
            continue
        th = rng.uniform(0, math.pi)
        d = np.array([math.cos(th), 0.0, math.sin(th)]) * rng.uniform(0.05, 0.08)
        e = np.array([-d[2], 0.0, d[0]]) * 0.45
        c = np.array([x, 0.006 + rng.uniform(0, 0.006), z])
        g = np.array([[c - d - e, c - d + e], [c + d - e, c + d + e]])
        for f in (False, True):
            kc.quad_strip(mb, g, leaf, uv=np.array([[[0, 0], [1, 0]], [[0, 1], [1, 1]]]), col=(0, 0, 0, 0.5),
                          uv2=(0.9, float(rng.random())), flip=f, smooth=False)
    for _ in range(26):  # twigs lying in the mud
        x, z = rng.uniform(x0, x1), rng.uniform(z0, z1)
        if not clear(x, z, 1.6):
            continue
        th = rng.uniform(0, 2 * math.pi)
        ln = rng.uniform(0.3, 0.9)
        a = np.array([x, 0.015, z])
        b = a + np.array([math.cos(th) * ln, 0.005, math.sin(th) * ln])
        kc.tube(mb, np.array([a, (a + b) * 0.5 + [0.0, 0.006, 0.0], b]), np.array([0.018, 0.013, 0.008]), 4, bark)
    for _ in range(30):  # crab holes: a dark mouth in a low rim of spoil
        x, z = rng.uniform(x0, x1), rng.uniform(z0, z1)
        if not clear(x, z):
            continue
        kc.tube(mb, np.array([[x, 0.0, z], [x, 0.012, z]]), 0.04, 6, dark, cap_end=True)
    for _ in range(9):  # puddles, standing water in the mud's hollows
        x, z = rng.uniform(x0, x1), rng.uniform(z0, z1)
        if not clear(x, z, 2.2):
            continue
        a = np.linspace(0.0, 2 * math.pi, 13)
        rr = rng.uniform(0.4, 1.1) * (1.0 + 0.25 * np.sin(a * 3.0 + rng.uniform(0, 6)))
        ring = np.stack([x + np.cos(a) * rr, np.full_like(a, 0.004), z + np.sin(a) * rr * 0.7], -1)
        centre = np.tile(np.array([[x, 0.004, z]]), (13, 1))
        g = np.stack([centre, ring])
        kc.quad_strip(mb, g, puddle, uv=g[..., [0, 2]], col=(0, 0, 1, 0.2), uv2=(0.9, 0.5), smooth=False,
                      flip=bool(np.cross(ring[1] - ring[0], ring[0] - centre[0])[1] < 0))


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
            _bank_litter(mb, rng)
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


def build_tree(seed: int = 1802, piece: str = "mangrove_tree", height: float = 9.0, roots: int = 12,
               root_r: tuple[float, float] = (1.8, 3.2), trunk_h: float = 5.0, trunk_r: tuple[float, float] = (0.32, 0.24),
               lean: tuple[float, float, float] = (0.35, 0.0, 0.1), boughs: int = 5,
               bough_len: tuple[float, float] = (1.6, 2.4), leaves: int = 16) -> list[kc.MeshBuilder]:
    """A living mangrove (the defaults are the kit's `mangrove_tree`); the zones' system draws its variants from the
    same builder (MANGROVE_VARIANTS), so they share the wind contract and materials."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for(piece, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(piece + ("-lod1" if lod else ""))
        bark = mb.material(M_BARK)
        foot = np.array([0.0, 0.0, 0.0])
        start = mb.vertex_count
        _prop_roots(mb, rng, noise, foot, max(5, roots * 2 // 3) if lod else roots, root_r[0], root_r[1], bark, lod=lod)
        _wind(mb, start, height, sway=False)
        start = mb.vertex_count
        lean_v = np.array(lean)
        trunk = _bezier(foot + [0.0, 1.0, 0.0], foot + [0.15, trunk_h * 0.6, 0.05], foot + lean_v * 4.0 + [0.0, trunk_h, 0.0],
                        4 if lod else 8)
        kc.tube(mb, trunk, np.linspace(trunk_r[0], trunk_r[1], len(trunk)), 5 if lod else 9, bark,
                noise=None if lod else noise, disp_m=0.015, v_scale=1.0 / 1.4, u_repeat=2.0)
        ends: list = []
        for k in range(boughs):
            th = 2 * math.pi * (k + rng.uniform(0.0, 0.6)) / boughs
            d = np.array([math.cos(th), 1.0, math.sin(th)])
            _bough(mb, rng, noise, trunk[-1], d, rng.uniform(bough_len[0], bough_len[1]), 0.16, 1, bark, ends,
                   lod=lod, bare=False)
        _wind(mb, start, height, phase=0.0)
        for k, (e, d) in enumerate(ends):
            _leaf_cluster(mb, rng, e + d * 0.2, 6 if lod else leaves, 1.0 if lod else 0.85, height, phase=k * 0.13)
        out.append(mb)
    return out


# The zones' mangrove system (M4-A2P-040): the kit tree and three variants, so a channel never repeats one tree.
#   mangrove_tall    an old tree, 11 m, a long leaning trunk over a wide root cage, six boughs;
#   mangrove_low     a squat tree, 6.5 m, many short roots, a broad low crown;
#   mangrove_young   a sapling on a few roots, 4 m, three boughs (the edges of the root-mats).
MANGROVE_VARIANTS = {
    "mangrove_tall": dict(seed=1812, height=11.0, roots=14, root_r=(2.2, 3.8), trunk_h=6.8, trunk_r=(0.4, 0.28),
                          lean=(0.55, 0.0, -0.2), boughs=6, bough_len=(2.0, 2.9), leaves=16),
    "mangrove_low": dict(seed=1813, height=6.5, roots=16, root_r=(1.6, 2.6), trunk_h=3.2, trunk_r=(0.34, 0.26),
                         lean=(-0.2, 0.0, 0.25), boughs=6, bough_len=(1.8, 2.6), leaves=14),
    "mangrove_young": dict(seed=1814, height=4.0, roots=7, root_r=(0.9, 1.5), trunk_h=2.2, trunk_r=(0.14, 0.1),
                           lean=(0.15, 0.0, 0.1), boughs=3, bough_len=(0.9, 1.3), leaves=10),
}


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


# ---------------------------------------------------------------------------------------------
# Reedhollow: the roost and the name-shells
# ---------------------------------------------------------------------------------------------
ROOST_DECK_Y = 1.2
ROOST_LEN = 5.0
ROOST_W = 3.0
ROOST_H = 2.8  # inside, over the deck


SNAP_EPS = 1e-9  # coordinates nearer 0 than this are 0 (host determinism)


def build_roost(seed: int = 1806) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("kirru_roost", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("kirru_roost" + ("-lod1" if lod else ""))
        bark, weave, lash = mb.material(M_BARK), mb.material(M_WEAVE), mb.material(M_LASH)
        hw, hl = ROOST_W * 0.5, ROOST_LEN * 0.5
        # Four mangrove-pole legs into the water, braced, and the deck of lashed poles across two bearers.
        for sx in (-1.0, 1.0):
            for sz in (-1.0, 1.0):
                foot = np.array([sx * (hw - 0.2), -0.6, sz * (hl - 0.3)])
                kc.tube(mb, np.stack([foot, foot + [rng.normal(0, 0.03), ROOST_DECK_Y + 0.6, rng.normal(0, 0.03)]]),
                        np.array([0.09, 0.07]), 4 if lod else 7, bark)
            kc.tube(mb, np.array([[sx * (hw - 0.2), ROOST_DECK_Y - 0.08, -hl], [sx * (hw - 0.2), ROOST_DECK_Y - 0.08, hl]]),
                    0.07, 4 if lod else 6, bark)
        if lod:
            kc.rounded_block(mb, (0.0, ROOST_DECK_Y, 0.0), (hw, 0.04, hl), bark, radius=0.02, seg=1)
        else:
            for z in np.arange(-hl + 0.06, hl, 0.12):
                kc.tube(mb, np.array([[-hw - 0.1, ROOST_DECK_Y, z], [hw + 0.1, ROOST_DECK_Y + rng.normal(0, 0.008), z]]),
                        0.055, 5, bark, noise=noise, disp_m=0.004)
            for sx in (-1.0, 1.0):  # lashings where the deck crosses the bearers
                for z in np.arange(-hl + 0.4, hl, 0.9):
                    kc.tube(mb, np.array([[sx * (hw - 0.2), ROOST_DECK_Y - 0.14, z - 0.06],
                                          [sx * (hw - 0.2), ROOST_DECK_Y + 0.06, z + 0.06]]), 0.02, 4, lash)
        # The lodge: bundled-reed arches (a pointed barrel, heron-tall), woven panels between them, open at +Z.
        n_arch = 6 if lod else 11
        zs = np.linspace(-hl + 0.1, hl - 0.25, n_arch)
        t = np.linspace(0.0, 1.0, 7 if lod else 15)
        prof = np.stack([np.cos(t * math.pi) * hw * (1.0 - 0.12 * np.sin(t * math.pi)),
                         ROOST_DECK_Y + ROOST_H * np.sin(t * math.pi) ** 0.8 + 0.25 * np.sin(t * math.pi) ** 6], -1)
        for k, z in enumerate(zs):
            back = 1.0 - 0.18 * kc.smoothstep(-hl + 1.2, -hl, z)  # the back end rounds in
            arch = np.stack([prof[:, 0] * back, ROOST_DECK_Y + (prof[:, 1] - ROOST_DECK_Y) * back,
                             np.full(len(t), z)], -1)
            kc.tube(mb, arch, 0.06, 4 if lod else 6, mb.material(M_REED))
            if k + 1 < len(zs):
                z1 = zs[k + 1]
                back1 = 1.0 - 0.18 * kc.smoothstep(-hl + 1.2, -hl, z1)
                a1 = np.stack([prof[:, 0] * back1, ROOST_DECK_Y + (prof[:, 1] - ROOST_DECK_Y) * back1,
                               np.full(len(t), z1)], -1)
                grid = np.stack([arch, a1], 1) * np.array([0.97, 1.0, 1.0])  # the panel sits just inside the arches
                uv = np.stack(np.broadcast_arrays(t[:, None] * 6.0, np.array([0.0, 1.0])[None, :] * (z1 - z) * 2.0), -1)
                kc.quad_strip(mb, grid, weave, uv=uv, col=(0, 0, 0, 0.3), uv2=(0.9, 0.5))
                kc.quad_strip(mb, grid, weave, uv=uv, col=(0, 0, 0, 0.3), uv2=(0.6, 0.5), flip=True)
        # The closed back: a woven cap.
        back = np.stack([prof[:, 0] * 0.82, ROOST_DECK_Y + (prof[:, 1] - ROOST_DECK_Y) * 0.82, np.full(len(t), -hl + 0.05)], -1)
        mid = np.stack([np.zeros(len(t)), np.full(len(t), ROOST_DECK_Y + 0.05), np.full(len(t), -hl + 0.05)], -1)
        grid = np.stack([back, mid], 1)
        uv = np.stack(np.broadcast_arrays(t[:, None] * 6.0, np.array([0.0, 1.0])[None, :]), -1)
        kc.quad_strip(mb, grid, weave, uv=uv, col=(0, 0, 0, 0.3), uv2=(0.8, 0.5))
        kc.quad_strip(mb, grid, weave, uv=uv, col=(0, 0, 0, 0.3), uv2=(0.8, 0.5), flip=True)
        # The arches' crown is cos(pi/2): 6e-17 on one numpy SIMD path and another on the next (M3-CRE-663). Snapped
        # to 0 (and -0.0 cleared), the build is byte-identical on every host, as the Avalanche Ram's (ADR 0005).
        p = np.asarray(mb.pos, dtype=np.float64)
        mb.pos = (np.where(np.abs(p) < SNAP_EPS, 0.0, p) + 0.0).tolist()
        out.append(mb)
    return out


def build_name_cord(seed: int = 1807) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("name_shell_cord", seed)
        mb = kc.MeshBuilder("name_shell_cord" + ("-lod1" if lod else ""))
        bark, lash, shell = mb.material(M_BARK), mb.material(M_LASH), mb.material(M_SHELL)
        top = 2.2  # Kirru height: the shells hang at a Kirru's eye
        for x in (-3.0, 3.0):
            kc.tube(mb, np.array([[x, -0.5, 0.0], [x + rng.normal(0, 0.04), top + 0.25, 0.0]]), np.array([0.06, 0.045]),
                    4 if lod else 6, bark, cap_end=True)
        t = np.linspace(0.0, 1.0, 9 if lod else 21)
        kc.tube(mb, np.stack([-3.0 + 6.0 * t, top - 0.35 * 4.0 * t * (1.0 - t), np.zeros_like(t)], -1), 0.012,
                3 if lod else 4, lash)
        n = 14
        blank = int(rng.integers(3, n - 3))
        for k in range(n):
            s_ = (k + 0.5 + rng.uniform(-0.2, 0.2)) / n
            x = -3.0 + 6.0 * s_
            y = top - 0.35 * 4.0 * s_ * (1.0 - s_)
            ln = rng.uniform(0.25, 0.45)
            kc.tube(mb, np.array([[x, y, 0.0], [x, y - ln, 0.0]]), 0.005, 3, lash)
            # The shell: a carved scallop token, 9 cm, its face turned to the water (+Z); the scraped one is
            # flat and blank, the others carry their name's ribs.
            c = np.array([x, y - ln - 0.045, 0.0])
            ribs = 0 if (k == blank or lod) else 7
            a = np.linspace(-1.1, 1.1, 4 if lod else 11)
            r = np.linspace(0.0, 1.0, 2 if lod else 4)
            A, R = np.meshgrid(a, r, indexing="ij")
            bump = 0.004 * np.abs(np.sin(A * ribs)) * R if ribs else 0.0 * A
            Xs = c[0] + np.sin(A) * R * 0.05
            Ys = c[1] + 0.04 - np.cos(A) * R * 0.05
            Zs = c[2] + 0.006 * (1.0 - R ** 2) + bump
            grid = np.stack([Xs, Ys, Zs], -1)
            uv = np.stack([A / 2.2 + 0.5, R], -1)
            kc.quad_strip(mb, grid, shell, uv=uv, col=(0, 0, 0, 0.2), uv2=(0.9, 0.5 if k != blank else 0.9))
            if not lod:  # the back (LOD1 draws the face only)
                kc.quad_strip(mb, grid - np.array([0.0, 0.0, 0.004]), shell, uv=uv, col=(0, 0, 0, 0.2), uv2=(0.9, 0.5),
                              flip=True)
        out.append(mb)
    return out


TARGETS = {
    "fen_bank_ground": build_ground,
    "mangrove_tree": build_tree,
    "mangrove_dead": build_dead,
    "reed_bed": build_reeds,
    "fen_far_mangroves": build_far,
    "kirru_roost": build_roost,
    "name_shell_cord": build_name_cord,
    **{name: (lambda name=name: build_tree(piece=name, **MANGROVE_VARIANTS[name])) for name in MANGROVE_VARIANTS},
}
