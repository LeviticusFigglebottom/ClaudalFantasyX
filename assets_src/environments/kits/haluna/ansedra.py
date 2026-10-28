"""Ansedra, the holy city (ansedra.md §1; M3-ENV-721): the bowl-domes, the skyline, the Conclave's pursuit barge.
Pure numpy.

Built in the Haluna kit (its import kind and materials), as keth.py, lowlight.py, ossa_fen.py and bridal_barge.py.

  bowl_dome           a bowl-dome on its island (bible §5.8): a white stone plinth standing out of the lagoon (its
                      top 0.6 m over the water at y 0), three tiered red-lacquer drums with gilt bands, the inverted
                      gilded bowl, a thin gilt spire with rings; 20 m to the spire's tip at scale 1. Origin at the
                      plinth's centre on the water.
  ansedra_far_domes   the skyline round the lagoon: forty bowl-domes and their islands at 300-700 m, low-poly, on the
                      water (y 0); origin the lagoon's centre.
  ansedra_far_domes_lit  the same skyline at the wedding's dusk (ch14): every drum's windows lit (the city has come out
                      to watch the water move).
  pursuit_barge       the Conclave's pursuit barge along X, its bow at -X: black lacquer with gilt, deck at y 0.4
                      over the water (y 0 = its waterline), a raised poop at the stern for the Warden, and on it the
                      bound flat-engine: a bronze disc on a gimbal, its core bound light (glimmer_bound), that pulls the
                      water level and still. Origin at the waterline amidships.
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc

M_STONE = "kit_order_marble"
M_LACQUER = "kit_lacquer_red"
M_BLACK = "kit_lacquer_black"
M_GILT = "kit_gold_leaf"
M_BRONZE = "kit_iskarra_bronze"
M_CORE = "kit_bound_core"
M_WINDOW = "kit_window_lit"
M_DECK = "kit_timber"

TRI_BUDGET = {"bowl_dome": (6000, 400), "ansedra_far_domes": (8000, 3000), "pursuit_barge": (10000, 700)}
BUDGET_KEY = {"ansedra_far_domes_lit": "ansedra_far_domes"}

PLINTH_TOP = 0.6
DRUMS = ((4.6, 2.6), (3.8, 2.4), (3.1, 2.2))  # (radius, height) of the three tiers, bottom up
BOWL = (3.4, 3.2)  # radius, height
SPIRE = 7.5
PURSUIT_DECK_Y = 0.4
PURSUIT_LEN = 14.0
PURSUIT_HALF_BEAM = 2.3
ENGINE_AT = (5.0, 1.6)  # x, deck height of the flat-engine's hub over the poop


def _revolve(mb, ys, rs, sides, mat, *, cap=False):
    """A surface of revolution about Y: radius rs[i] at height ys[i]."""
    pts = np.stack([np.zeros(len(ys)), ys, np.zeros(len(ys))], -1)
    kc.tube(mb, pts, np.maximum(rs, 0.002), sides, mb.material(mat), cap_end=cap, u_repeat=2.0, v_scale=0.5,
            first_normal=(1.0, 0.0, 0.0))


def _dome(mb, x, z, scale, lod, rng, *, sides, windows: bool, island: bool = True) -> None:
    """One bowl-dome at (x, z), placed into mb (its own frame offset)."""
    s = scale
    o = np.array([x, 0.0, z])
    start = mb.vertex_count
    if island:
        n_isl = 8
        a = np.linspace(0.0, 2 * math.pi, n_isl, endpoint=False) + math.pi / n_isl
        outline = np.stack([np.cos(a) * 6.4 * s, np.sin(a) * 6.4 * s], -1)
        kc.polygon_prism(mb, outline, -1.5 * s, PLINTH_TOP * s, mb.material(M_STONE), col=(0, 0.2, 0.2, 0.5),
                         uv2=(0.9, 0.5), uv_scale=0.5)
    y = PLINTH_TOP * s
    for k, (r, h) in enumerate(DRUMS):
        _revolve(mb, np.array([y, y + h * s]), np.array([r, r * 0.97]) * s, sides, M_LACQUER, cap=True)
        if not lod:  # the gilt band at each drum's top, and a step ring at its foot
            _revolve(mb, np.array([y + h * s - 0.25 * s, y + h * s]), np.array([r + 0.12, r + 0.12]) * s, sides, M_GILT)
        if windows and k < 2:
            n_w = max(6, int(r * 2.2))
            for j in range(n_w):
                th = 2 * math.pi * (j + 0.5) / n_w
                d = np.array([math.cos(th), 0.0, math.sin(th)])
                side = np.array([-d[2], 0.0, d[0]]) * 0.2 * s
                c = d * (r * 0.97 * s + 0.03) + np.array([0.0, y + h * s * 0.5, 0.0])
                up = np.array([0.0, 0.45 * s, 0.0])
                grid = np.array([[c - side - up, c + side - up], [c - side + up, c + side + up]])
                kc.quad_strip(mb, grid, mb.material(M_WINDOW), uv=np.array([[[0, 0], [1, 0]], [[0, 1], [1, 1]]]),
                              col=(0, 0, 0, 0), uv2=(1.0, 0.5), flip=True, smooth=False)
        y += h * s
    # The inverted gilded bowl, and the spire with its rings.
    t = np.linspace(0.0, 1.0, 4 if lod else 9)
    _revolve(mb, y + BOWL[1] * s * t, BOWL[0] * s * np.sqrt(np.clip(1.0 - t ** 2, 0.0, 1.0)) + 0.01, sides, M_GILT)
    top = y + BOWL[1] * s
    _revolve(mb, np.array([top - 0.1, top + SPIRE * s]), np.array([0.22, 0.03]) * s, max(4, sides // 2), M_GILT)
    if not lod:
        for f in (0.25, 0.45, 0.62):
            _revolve(mb, np.array([top + SPIRE * s * f, top + SPIRE * s * f + 0.12 * s]),
                     np.array([0.32, 0.32]) * s * (1.0 - f), 8, M_GILT)
    # Move what this dome added to (x, z).
    p = np.asarray(mb.pos)
    p[start:] += o
    mb.pos = p.tolist()


def build_bowl_dome(seed: int = 2101) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("bowl_dome", seed)
        mb = kc.MeshBuilder("bowl_dome" + ("-lod1" if lod else ""))
        _dome(mb, 0.0, 0.0, 1.0, lod, rng, sides=8 if lod else 24, windows=False)
        out.append(mb)
    return out


def build_far_domes(seed: int = 2102, *, lit: bool = False) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("ansedra_far_domes", seed)
        mb = kc.MeshBuilder(("ansedra_far_domes_lit" if lit else "ansedra_far_domes") + ("-lod1" if lod else ""))
        n = 40
        for k in range(n):
            th = 2 * math.pi * (k + rng.uniform(0.0, 0.6)) / n
            r = rng.uniform(300.0, 700.0)
            sc = rng.uniform(1.2, 2.6)
            _dome(mb, math.cos(th) * r, math.sin(th) * r, sc, True, rng, sides=4 if lod else 7, windows=lit and not lod,
                  island=not lod)
        out.append(mb)
    return out


def _pursuit_half_beam(x):
    x = np.asarray(x, float)
    t = (x + PURSUIT_LEN * 0.5) / PURSUIT_LEN
    return PURSUIT_HALF_BEAM * (1.0 - 0.9 * kc.smoothstep(0.3, 0.0, t) ** 1.2) * (1.0 - 0.2 * kc.smoothstep(0.85, 1.0, t))


def build_pursuit_barge(seed: int = 2103) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("pursuit_barge", seed)
        mb = kc.MeshBuilder("pursuit_barge" + ("-lod1" if lod else ""))
        black, gilt, deck = mb.material(M_BLACK), mb.material(M_GILT), mb.material(M_DECK)
        n = 10 if lod else 25
        xs = np.linspace(-PURSUIT_LEN * 0.5, PURSUIT_LEN * 0.5, n)
        hw = _pursuit_half_beam(xs)
        # The deck at y 0.4, the poop raised to 1.2 over the last third.
        poop = kc.smoothstep(2.4, 2.9, xs) * 0.8
        across = np.linspace(-1.0, 1.0, 5)
        dgrid = np.stack([np.stack([xs, PURSUIT_DECK_Y + poop, a * hw], -1) for a in across], 1)
        kc.quad_strip(mb, dgrid, deck, uv=dgrid[..., [0, 2]] * 0.5, col=(0, 0.1, 0.1, 0.5), uv2=(0.9, 0.5))
        prof = ((0.15, 1.0), (-0.3, 0.92), (-0.7, 0.6), (-0.9, 0.0))
        for side in (-1.0, 1.0):
            grid = np.stack([np.stack([xs, np.where(f == 1.0, PURSUIT_DECK_Y + poop + y, y), side * hw * f], -1)
                             for y, f in prof], 1)
            kc.quad_strip(mb, grid, black, uv=grid[..., [0, 1]] / 2.0, col=(0, 0.1, 0.1, 0.5), uv2=(0.8, 0.5),
                          flip=side < 0)
            kc.tube(mb, np.stack([xs, PURSUIT_DECK_Y + poop + 0.1, side * (hw + 0.01)], -1), 0.035, 4 if lod else 6,
                    gilt)
        tz = np.linspace(-1.0, 1.0, 5) * _pursuit_half_beam(PURSUIT_LEN * 0.5)
        tr = np.stack([np.stack([np.full(5, PURSUIT_LEN * 0.5), np.full(5, y if f < 1.0 else PURSUIT_DECK_Y + 0.95),
                                 tz * f], -1) for y, f in prof], 1)
        kc.quad_strip(mb, tr, black, uv=tr[..., [2, 1]] / 2.0, col=(0, 0.1, 0.1, 0.5), uv2=(0.8, 0.5), flip=True)
        # The bow's gilt Level-line finial (the Order's sign), and the poop's rail.
        kc.tube(mb, np.array([[-PURSUIT_LEN * 0.5 + 0.2, PURSUIT_DECK_Y, 0.0],
                              [-PURSUIT_LEN * 0.5 - 0.3, PURSUIT_DECK_Y + 1.6, 0.0]]), 0.06, 4 if lod else 8, gilt)
        kc.rounded_block(mb, (-PURSUIT_LEN * 0.5 - 0.3, PURSUIT_DECK_Y + 1.6, 0.0), (0.04, 0.04, 0.5), gilt,
                         radius=0.02, seg=1)
        if not lod:
            for side in (-1.0, 1.0):
                xr = np.linspace(2.9, PURSUIT_LEN * 0.5 - 0.3, 6)
                top = np.stack([xr, np.full(6, PURSUIT_DECK_Y + 0.8 + 0.9), side * (_pursuit_half_beam(xr) - 0.1)], -1)
                kc.tube(mb, top, 0.03, 6, black)
                for p in top:
                    kc.tube(mb, np.array([p - [0, 0.9, 0], p]), 0.025, 5, black)
        # The bound flat-engine on the poop: a bronze disc on a gimbal ring, its bound core lit, braced to the deck.
        ex, ey = ENGINE_AT
        hub = np.array([ex, PURSUIT_DECK_Y + 0.8 + ey, 0.0])
        kc.tube(mb, np.array([[ex, PURSUIT_DECK_Y + 0.8, 0.0], hub - [0, 0.5, 0]]), 0.12, 4 if lod else 8,
                mb.material(M_BRONZE))
        a = np.linspace(0.0, 2 * math.pi, 9 if lod else 33)
        ring = np.stack([np.cos(a) * 1.25, np.zeros_like(a), np.sin(a) * 1.25], -1) + hub
        kc.tube(mb, ring, 0.07, 4 if lod else 6, mb.material(M_BRONZE))
        kc.tube(mb, np.array([hub - [0, 0.06, 0], hub + [0, 0.06, 0]]), 1.1, 8 if lod else 24, mb.material(M_BRONZE),
                cap_start=True, cap_end=True)
        kc.rounded_block(mb, hub + [0, 0.14, 0], (0.22, 0.12, 0.22), mb.material(M_CORE), radius=0.12,
                         seg=1 if lod else 2)
        if not lod:
            for k in range(8):  # the disc's radial vanes, bound light along their channels
                th = 2 * math.pi * k / 8
                d = np.array([math.cos(th), 0.0, math.sin(th)])
                kc.tube(mb, np.array([hub + d * 0.3 + [0, 0.07, 0], hub + d * 1.0 + [0, 0.07, 0]]), 0.018, 4,
                        mb.material(M_CORE))
        del rng
        out.append(mb)
    return out


TARGETS = {
    "bowl_dome": build_bowl_dome,
    "ansedra_far_domes": build_far_domes,
    "ansedra_far_domes_lit": lambda: build_far_domes(lit=True),
    "pursuit_barge": build_pursuit_barge,
}
