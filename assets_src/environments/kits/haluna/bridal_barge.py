"""Merel's bridal barge (open_sea_ch15.md; M3-ENV-720): the Wakefin's arena floor, drifting unlamped. Pure numpy.

Built in the Haluna kit (its import kind and materials), as iskarra.py, keth.py, lowlight.py and ossa_fen.py.

  bridal_barge  (arena frame) a long, low Ansedran barge along X, its bow pointed at -X: the deck level at y 0,
                16 m x 7.5 m (it holds every battle slot's metre); the hull in wedding-red lacquer down to the
                waterline at -0.6 with a gilt sheer band; a low rail (0.35 m) on gilt-capped posts; the stern canopy
                of red bridal cloth on four gilt posts with Tobin's bier under Merel's bridal cloth; at the bow an
                empty lamp hook (wedding barges carry no lamp); the punt poles laid along the rails.

Nothing on it gives light: no lamp, no flame (the colour script's ch15).

  bridal_barge_wedding  the same barge before Ch15 (Ansedra's moorings, the Lacquer Court): the canopy without the bier.
  bridal_barge_sea    the same barge as Ch15's open-sea zone carries it: the canopy and the bier moved SEA_CANOPY_SHIFT
                      along X (mid-deck), so the zone's greybox deck fits it at a smaller scale.
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc

M_HULL = "kit_lacquer_red"
M_GILT = "kit_gold_leaf"
M_DECK = "kit_timber"
M_CLOTH = "kit_keth_red"  # the bridal cloth: a woven red, matte (the keth's red wool)
M_SEAM = "kit_interior_dark"

TRI_BUDGET = {"bridal_barge": (16000, 1200), "bridal_barge_wedding": (16000, 1200), "bridal_barge_sea": (16000, 1200)}
# The Ch15 zone's barge (M4-A2P-045, env-art-b): placed at SEA_SCALE on the greybox deck, its canopy and bier moved
# forward so the bier lands on the greybox's Bier block and the stern stays clear for Kerrid's seat.
SEA_CANOPY_SHIFT = -4.8

BOW_X, STERN_X = -8.6, 8.0
HALF_BEAM = 3.75
WATERLINE_Y = -0.6
RAIL_H = 0.35
CANOPY = ((5.0, 2.5), (7.3, 2.1))  # (x, half-width) of the canopy's two post pairs
BIER_AT = (6.2, 0.0)
SLOTS_METRE = (-4.4, 4.0, -2.2, 3.0)  # x0, x1, z0, z1: the battle slots' floor (battle_arenas.md)
LACQUER = kc.Weathering(moss=0.0, salt=0.15, wet=0.1, erosion=0.1)


def half_beam(x) -> np.ndarray:
    """The deck's half-width at station x: full amidships, tapering to the bow's point and a little at the stern."""
    x = np.asarray(x, float)
    bow = 1.0 - 0.92 * kc.smoothstep(2.5, -BOW_X, -x) ** 1.2
    stern = 1.0 - 0.25 * kc.smoothstep(5.0, STERN_X, x)
    return HALF_BEAM * bow * stern


def build_barge(seed: int = 2001, *, bier: bool = True, name: str = "bridal_barge",
                canopy_shift: float = 0.0) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("bridal_barge", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
        hull, gilt, deck = mb.material(M_HULL), mb.material(M_GILT), mb.material(M_DECK)
        n = 12 if lod else 33
        # The deck, level at y 0: a grid between the stations' rails (the bow's taper is not convex enough for a
        # fan), and its edge strip down to the sheer.
        xs_d = np.linspace(BOW_X, STERN_X, n)
        across = np.linspace(-1.0, 1.0, 5 if lod else 9)
        hw_d = half_beam(xs_d)
        dgrid = np.stack([np.stack([xs_d, np.zeros(n), a * hw_d], -1) for a in across], 1)
        kc.quad_strip(mb, dgrid, deck, uv=dgrid[..., [0, 2]] * 0.5, col=(0.0, 0.1, 0.1, 0.5), uv2=(0.9, 0.5))
        if not lod:  # the plank seams, flush
            for z in np.arange(-HALF_BEAM + 0.2, HALF_BEAM, 0.24):
                xs = np.linspace(BOW_X, STERN_X, 33)
                inside = half_beam(xs) > abs(z) + 0.05
                if inside.sum() < 2:
                    continue
                xa, xb = xs[inside][0], xs[inside][-1]
                grid = np.array([[[xa, 0.002, z - 0.006], [xb, 0.002, z - 0.006]],
                                 [[xa, 0.002, z + 0.006], [xb, 0.002, z + 0.006]]])
                kc.quad_strip(mb, grid, mb.material(M_SEAM), uv=np.zeros((2, 2, 2)), col=(0, 0, 0, 0), uv2=(0.9, 0.5),
                              flip=True, smooth=False)
        # The hull: lofted sections from the sheer down to the keel, each side.
        stations = np.linspace(BOW_X, STERN_X, n)
        hw = half_beam(stations)
        prof = ((0.12, 1.0), (-0.3, 0.96), (WATERLINE_Y - 0.2, 0.74), (WATERLINE_Y - 0.45, 0.0))
        for side in (-1.0, 1.0):
            grid = np.stack([np.stack([stations, np.full(n, y), side * hw * f], -1) for y, f in prof], 1)
            kc.quad_strip(mb, grid, hull, uv=np.stack([grid[..., 0], grid[..., 1]], -1) / 2.0, col=(0, 0.15, 0.2, 0.5),
                          uv2=(0.8, 0.5), flip=side < 0)
            # The gilt sheer band along the hull, and the stern's transom.
            band = np.stack([stations, np.full(n, 0.04), side * (hw + 0.012)], -1)
            kc.tube(mb, band, 0.04, 4 if lod else 6, gilt)
        tz = np.linspace(-1.0, 1.0, 7) * half_beam(STERN_X)
        transom = np.stack([np.stack([np.full(7, STERN_X), np.full(7, y), tz * f], -1) for y, f in prof], 1)
        kc.quad_strip(mb, transom, hull, uv=transom[..., [2, 1]] / 2.0, col=(0, 0.15, 0.2, 0.5), uv2=(0.8, 0.5),
                      flip=True)
        # The low rail: posts every metre with gilt caps, a lacquered top rail; open at the stern for the poler.
        for side in (-1.0, 1.0):
            xs = np.linspace(BOW_X + 0.6, STERN_X - 0.8, 7 if lod else 16)
            top = np.stack([xs, np.full(len(xs), RAIL_H), side * (half_beam(xs) - 0.08)], -1)
            kc.tube(mb, top, 0.035, 4 if lod else 6, hull)
            if not lod:
                for p in top:
                    kc.tube(mb, np.array([[p[0], 0.0, p[2]], [p[0], RAIL_H, p[2]]]), 0.03, 5, hull)
                    kc.rounded_block(mb, p + [0.0, 0.03, 0.0], (0.04, 0.03, 0.04), gilt, radius=0.02, seg=1)
        _canopy(mb, rng, noise, lod, bier=bier, shift=canopy_shift)
        _bow_hook(mb, lod)
        if not lod:  # the punt poles, laid along the rails
            for side, x0 in ((-1.0, -5.0), (1.0, -3.0)):
                z = side * (half_beam(0.0) - 0.35)
                kc.tube(mb, np.array([[x0, 0.04, z], [x0 + 6.5, 0.04, z * 0.98]]), 0.035, 6, deck)
        out.append(mb)
    return out


def _canopy(mb, rng, noise, lod, *, bier: bool = True, shift: float = 0.0) -> None:
    """Four gilt posts, a sagging roof of red bridal cloth with swags, and (with `bier`) Tobin's bier under it; all
    moved `shift` m along X (the Ch15 zone's barge carries them mid-deck)."""
    canopy = tuple((x + shift, w) for x, w in CANOPY)
    gilt, cloth = mb.material(M_GILT), mb.material(M_CLOTH)
    h = 2.4
    corners = [(x, s * w) for x, w in canopy for s in (-1.0, 1.0)]
    for x, z in corners:
        kc.tube(mb, np.array([[x, 0.0, z], [x, h, z]]), 0.05, 4 if lod else 8, gilt, cap_end=True)
    (x0, w0), (x1, w1) = canopy
    nu, nv = (3, 3) if lod else (9, 7)
    u = np.linspace(0.0, 1.0, nu)
    v = np.linspace(-1.0, 1.0, nv)
    U, V = np.meshgrid(u, v, indexing="ij")
    X = x0 + (x1 - x0) * U
    Z = V * (w0 + (w1 - w0) * U)
    Y = h + 0.05 - 0.22 * (1.0 - V ** 2) * np.sin(U * math.pi) ** 0.5
    grid = np.stack([X, Y, Z], -1)
    for flip in (False, True):
        kc.quad_strip(mb, grid, cloth, uv=np.stack([U, V], -1) * 2.0, col=(0, 0, 0, 0.3), uv2=(0.9, 0.5), flip=flip,
                      smooth=not lod)
    if not lod:  # the swags along the long sides, hanging between the posts
        for s in (-1.0, 1.0):
            t = np.linspace(0.0, 1.0, 11)
            top = np.stack([x0 + (x1 - x0) * t, np.full_like(t, h), s * (w0 + (w1 - w0) * t)], -1)
            bot = top + np.stack([np.zeros_like(t), -0.5 * np.sin(t * math.pi), np.zeros_like(t)], -1)
            g = np.stack([top, bot], 1)
            for flip in (False, True):
                kc.quad_strip(mb, g, cloth, uv=np.stack(np.broadcast_arrays(t[:, None], np.array([0.0, 1.0])[None, :]), -1),
                              col=(0, 0, 0, 0.3), uv2=(0.9, 0.5), flip=flip)
    if not bier:
        return
    # The bier: a low timber platform, and Tobin's body under Merel's bridal cloth (the cloth's heightfield over him).
    bx, bz = BIER_AT[0] + shift, BIER_AT[1]
    kc.rounded_block(mb, (bx, 0.2, bz), (1.05, 0.2, 0.45), mb.material(M_DECK), radius=0.03, seg=1)
    nx, nz = (4, 3) if lod else (17, 9)
    xs = np.linspace(-1.15, 1.15, nx)
    zs = np.linspace(-0.6, 0.6, nz)
    Xc, Zc = np.meshgrid(xs, zs, indexing="ij")
    body = 0.2 * np.clip(1.0 - (Xc / 0.95) ** 2, 0.0, 1.0) ** 0.5 * np.clip(1.0 - (Zc / 0.3) ** 2, 0.0, 1.0) ** 0.6
    head = 0.08 * np.clip(1.0 - ((Xc + 0.85) ** 2 + Zc ** 2) / 0.04, 0.0, 1.0)
    drape = np.clip((np.abs(Zc) - 0.45) / 0.15, 0.0, 1.0) * 0.32 + np.clip((np.abs(Xc) - 1.05) / 0.1, 0.0, 1.0) * 0.3
    Y = 0.42 + body + head - drape
    grid = np.stack([bx + Xc, Y, bz + Zc], -1)
    kc.quad_strip(mb, grid, cloth, uv=np.stack([Xc, Zc], -1), col=(0, 0, 0, 0.3), uv2=(0.9, 0.5))


def _bow_hook(mb, lod) -> None:
    """At the bow, a gilt post curling forward into an empty lamp hook: the lamp a wedding barge never carries."""
    gilt = mb.material(M_GILT)
    t = np.linspace(0.0, 1.0, 5 if lod else 13)
    x = BOW_X + 0.7 - 0.5 * t ** 2
    y = 1.9 * t
    kc.tube(mb, np.stack([x, y, np.zeros_like(t)], -1), np.linspace(0.05, 0.03, len(t)), 4 if lod else 7, gilt)
    if not lod:
        a = np.linspace(0.0, 1.6 * math.pi, 11)
        hook = np.stack([x[-1] - 0.12 * np.sin(a), y[-1] - 0.12 + 0.12 * np.cos(a), np.zeros_like(a)], -1)
        kc.tube(mb, hook, 0.012, 5, gilt)


TARGETS = {"bridal_barge": build_barge,
           # M4-A2P-043/044 (env-art-b): the same barge before Ch15, dressed for the wedding (no bier: Tobin lives).
           "bridal_barge_wedding": lambda: build_barge(bier=False, name="bridal_barge_wedding"),
           # M4-A2P-045 (env-art-b): Ch15's barge at sea, its canopy and the bier mid-deck.
           "bridal_barge_sea": lambda: build_barge(name="bridal_barge_sea", canopy_shift=SEA_CANOPY_SHIFT)}
