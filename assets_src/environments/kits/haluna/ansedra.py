"""Ansedra, the holy city (ansedra.md §1; M3-ENV-721): the bowl-domes, the skyline, the Conclave's pursuit barge.
Pure numpy.

Built in the Haluna kit (its import kind and materials), as keth.py, lowlight.py, ossa_fen.py and bridal_barge.py.

  bowl_dome           a bowl-dome on its island (bible §5.8): a white stone plinth standing out of the lagoon (its
                      top 0.6 m over the water at y 0), three tiered red-lacquer drums with gilt bands, the inverted
                      gilded bowl, a thin gilt spire with rings; 20 m to the spire's tip at scale 1. Origin at the
                      plinth's centre on the water.
  bowl_dome_lit       the same at the wedding's night (ch14): its drums' windows lit.
  ansedra_far_domes   the skyline round the lagoon: forty bowl-domes and their islands at 300-700 m, low-poly, on the
                      water (y 0); origin the lagoon's centre.
  ansedra_far_domes_lit  the same skyline at the wedding's dusk (ch14): every drum's windows lit (the city has come out
                      to watch the water move).
  pursuit_barge       the Conclave's pursuit barge along X, its bow at -X: black lacquer with gilt, deck at y 0.4
                      over the water (y 0 = its waterline), a raised poop at the stern for the Warden, and on it the
                      bound flat-engine: a bronze disc on a gimbal, its core bound light (glimmer_bound), that pulls the
                      water level and still. Origin at the waterline amidships.
  lacquer_hall        one hall of the Lacquer Court (12 x 8 m): a white stone plinth, red-lacquer columns with gilt
                      capitals, a three-tier roof (red tile, gilt ridges) after the bible's tiered roofs; open on +Z.
                      Origin at the plinth's front centre on the court (y 0).
  lacquer_court_ground the Lacquer Court's white stone court (40 x 28 m, y 0) on the lagoon, its water-steps down to
                      the water (-0.6) on +Z, and the court's water-gate over the steps' channel: two red posts and a
                      lacquered drop-gate (Merel drops it). Origin at the court's centre.
  sanctum_basin       the Sanctum of the Level's basin (14 x 14 m, 1 m deep): a white marble rim with kneeling steps
                      round it, the floor salt-glass tiles over bound light (the light that never moves); the
                      scene's still water fills it to y -0.1. Origin at the basin's centre on the rim (y 0).
  archive_stacks      one bay of the Lamp Archive: two lacquered ledger cases (6 x 3.2 m) facing across an aisle,
                      the ledgers' spines in rows, a rolling ladder, and the Cantor roll's lectern at the aisle's end.
                      Origin at the aisle's floor centre.
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
M_TILE = "kit_roof_tile"
M_GLASS = "kit_salt_glass"
M_PAPER = "kit_cloth_sand"

TRI_BUDGET = {"bowl_dome": (6000, 400), "ansedra_far_domes": (8000, 3000), "pursuit_barge": (10000, 700),
              "lacquer_hall": (8000, 500), "lacquer_court_ground": (12000, 800), "sanctum_basin": (8000, 500),
              "archive_stacks": (9000, 500)}
BUDGET_KEY = {"ansedra_far_domes_lit": "ansedra_far_domes", "bowl_dome_lit": "bowl_dome"}

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


def build_bowl_dome(seed: int = 2101, *, lit: bool = False) -> list[kc.MeshBuilder]:
    """`lit`: the wedding's night (ch14), the drums' windows lit: the city has come to its windows to watch the water
    move (M4-A2P-044)."""
    out = []
    name = "bowl_dome_lit" if lit else "bowl_dome"
    for lod in (False, True):
        rng = kc.rng_for("bowl_dome", seed)
        mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
        _dome(mb, 0.0, 0.0, 1.0, lod, rng, sides=8 if lod else 24, windows=lit)
        if not lod:
            _dome_detail(mb, rng)
        out.append(mb)
    return out


def _dome_detail(mb, rng) -> None:
    """The near bowl-dome's articulation (M3-ENV-705: c770380's render read the drums as plain stacked cylinders; the
    far skyline keeps _dome alone). Per drum: black lacquer pilasters round it, a dark window between each pair, and
    a black eave on brackets under its gilt band; gilt ribs down the bowl; the plinth's two steps into the water and
    its tide-wet foot."""
    black, gilt, dark, stone = (mb.material(M_BLACK), mb.material(M_GILT), mb.material("kit_interior_dark"),
                                mb.material(M_STONE))
    y = PLINTH_TOP
    for k, (r, h) in enumerate(DRUMS):
        n = 12 if k == 0 else (10 if k == 1 else 8)
        off = float(rng.uniform(0, 1))
        for j in range(n):
            th = 2 * math.pi * (j + off) / n
            d = np.array([math.cos(th), 0.0, math.sin(th)])
            kc.rounded_block(mb, d * (r * 0.985 + 0.06) + [0.0, y + h * 0.45, 0.0], (0.12, h * 0.45, 0.07), black,
                             rot=kc.rot_y(-th), radius=0.02, seg=1)
            tw = 2 * math.pi * (j + off + 0.5) / n  # the window between this pilaster and the next
            dw = np.array([math.cos(tw), 0.0, math.sin(tw)])
            hw = min(0.45, r * math.pi / n * 0.35)
            kc.rounded_block(mb, dw * (r * 0.985 + 0.01) + [0.0, y + h * 0.5, 0.0], (0.04, h * 0.28, hw), dark,
                             rot=kc.rot_y(-tw), radius=0.01, seg=1)
            kc.rounded_block(mb, dw * (r * 0.985 + 0.04) + [0.0, y + h * 0.5 + h * 0.3, 0.0], (0.05, 0.05, hw + 0.08),
                             gilt, rot=kc.rot_y(-tw), radius=0.01, seg=1)  # the window's gilt head
        # The eave under the gilt band, on brackets.
        _revolve(mb, np.array([y + h - 0.32, y + h - 0.25]), np.array([r + 0.42, r + 0.42]), 32, M_BLACK, cap=False)
        _revolve(mb, np.array([y + h - 0.45, y + h - 0.32]), np.array([r + 0.05, r + 0.42]), 32, M_BLACK)
        y += h
    # Gilt ribs down the bowl.
    t = np.linspace(0.0, 1.0, 9)
    for j in range(16):
        th = 2 * math.pi * j / 16
        rr = BOWL[0] * np.sqrt(np.clip(1.0 - t ** 2, 0.0, 1.0)) + 0.05
        pts = np.stack([np.cos(th) * rr, y + BOWL[1] * t, np.sin(th) * rr], -1)
        kc.tube(mb, pts[:-1], 0.06, 4, gilt)
    # The plinth's steps down into the water, and the tide line on its face.
    a = np.linspace(0.0, 2 * math.pi, 8, endpoint=False) + math.pi / 8  # the plinth's own octagon
    for rad, top in ((6.9, PLINTH_TOP - 0.25), (7.4, PLINTH_TOP - 0.5)):
        kc.polygon_prism(mb, np.stack([np.cos(a) * rad, np.sin(a) * rad], -1), -1.0, top, stone,
                         col=(0, 0.2, 0.4, 0.5), uv2=(0.9, 0.5), uv_scale=0.5)


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


# ---------------------------------------------------------------------------------------------
# The Lacquer Court, the Sanctum, the Archive (ansedra.md §1)
# ---------------------------------------------------------------------------------------------
STONE_W = kc.Weathering(moss=0.0, salt=0.1, wet=0.05, erosion=0.15, noise_scale_m=1.0)


def build_lacquer_hall(seed: int = 2104) -> list[kc.MeshBuilder]:
    out = []
    w, d = 12.0, 8.0
    for lod in (False, True):
        rng = kc.rng_for("lacquer_hall", seed)
        mb = kc.MeshBuilder("lacquer_hall" + ("-lod1" if lod else ""))
        stone, red, gilt, tile = mb.material(M_STONE), mb.material(M_LACQUER), mb.material(M_GILT), mb.material(M_TILE)
        kc.rounded_block(mb, (0.0, 0.3, -d * 0.5), (w * 0.5, 0.3, d * 0.5), stone, radius=0.04, seg=1, weather=STONE_W)
        col_h = 4.2
        xs = np.linspace(-w * 0.5 + 0.6, w * 0.5 - 0.6, 3 if lod else 6)
        zs = (-0.6, -d + 0.6)
        for x in xs:
            for z in zs:
                kc.tube(mb, np.array([[x, 0.6, z], [x, 0.6 + col_h, z]]), 0.22, 6 if lod else 12, red, cap_end=True)
                if not lod:
                    kc.rounded_block(mb, (x, 0.6 + col_h - 0.1, z), (0.32, 0.12, 0.32), gilt, radius=0.04, seg=1)
        if not lod:  # the back wall's lacquered panels
            kc.rounded_block(mb, (0.0, 0.6 + col_h * 0.5, -d + 0.4), (w * 0.5 - 0.6, col_h * 0.5, 0.12), red,
                             radius=0.03, seg=1)
        # The three-tier roof: each tier a hip of tile over a gilt-edged eave, smaller and steeper going up.
        y = 0.6 + col_h
        for k, (sw, sd, h) in enumerate(((w * 0.6, d * 0.65, 1.3), (w * 0.42, d * 0.47, 1.2), (w * 0.26, d * 0.3, 1.4))):
            cz = -d * 0.5
            ridge = sw * 0.35
            corners = np.array([[-sw, y, cz - sd], [sw, y, cz - sd], [sw, y, cz + sd], [-sw, y, cz + sd]])
            top = np.array([[-ridge, y + h, cz], [ridge, y + h, cz]])
            for a_, b_, t_ in ((corners[0], corners[1], (top[0], top[1])), (corners[2], corners[3], (top[1], top[0]))):
                grid = np.array([[a_, b_], [t_[0], t_[1]]])
                kc.quad_strip(mb, grid, tile, uv=np.array([[[0, 0], [2, 0]], [[0, 1], [2, 1]]]), col=(0, 0, 0, 0.4),
                              uv2=(0.8, 0.5), flip=True, smooth=False)
            for a_, b_, t_ in ((corners[1], corners[2], top[1]), (corners[3], corners[0], top[0])):
                grid = np.array([[a_, b_], [t_, t_]])
                kc.quad_strip(mb, grid, tile, uv=np.array([[[0, 0], [1, 0]], [[0, 1], [1, 1]]]), col=(0, 0, 0, 0.4),
                              uv2=(0.8, 0.5), flip=True, smooth=False)
            eave = np.concatenate([corners, corners[:1]])
            kc.tube(mb, eave, 0.08, 4, gilt)
            if not lod:
                kc.tube(mb, top, 0.07, 6, gilt)
                for c in corners:  # the upswept gilt eave tips
                    kc.tube(mb, np.array([c, c + np.array([np.sign(c[0]) * 0.4, 0.55, np.sign(c[2] - cz) * 0.4])]),
                            np.array([0.07, 0.02]), 5, gilt)
            if k < 2:  # the drum between tiers
                kc.rounded_block(mb, (0.0, y + h + 0.35, cz), (sw * 0.55, 0.35, sd * 0.55), red, radius=0.03, seg=1)
            y += h + 0.7
        del rng
        out.append(mb)
    return out


COURT = (20.0, 14.0)  # half extents x, z


def build_court_ground(seed: int = 2105) -> list[kc.MeshBuilder]:
    out = []
    hx, hz = COURT
    for lod in (False, True):
        rng = kc.rng_for("lacquer_court_ground", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("lacquer_court_ground" + ("-lod1" if lod else ""))
        stone, red, gilt = mb.material(M_STONE), mb.material(M_LACQUER), mb.material(M_GILT)
        # The court: large white slabs (one plate at LOD1), down into the lagoon on its sides.
        kc.rounded_block(mb, (0.0, -1.2, 0.0), (hx, 1.2, hz), stone, radius=0.05, seg=1, weather=STONE_W)
        if not lod:
            for x in np.arange(-hx, hx - 0.01, 2.5):
                for z in np.arange(-hz, hz - 0.01, 2.5):
                    kc.rounded_block(mb, (x + 1.25, -0.04, z + 1.25), (1.23, 0.04, 1.23), stone, radius=0.01, seg=1,
                                     weather=STONE_W, variation=float(rng.random()))
            # The Level line inlaid in gilt across the court (the Order's sign).
            kc.rounded_block(mb, (0.0, 0.002, 0.0), (hx - 1.0, 0.004, 0.06), gilt, radius=0.002, seg=1)
        # The water-steps on +Z: eight broad steps from the court down into the lagoon.
        for k in range(8):
            y = -0.15 * (k + 1)
            kc.rounded_block(mb, (0.0, y - 0.075, hz + 0.25 + 0.5 * k), (hx * 0.4, 0.075 + 0.02, 0.25), stone,
                             radius=0.02, seg=1, noise=None if lod else noise, disp_m=0.003, weather=STONE_W)
        # The water-gate: two red posts at the steps' foot and the lacquered drop-gate raised between them.
        gz = hz + 4.3
        for sx in (-1.0, 1.0):
            kc.tube(mb, np.array([[sx * hx * 0.42, -1.4, gz], [sx * hx * 0.42, 6.0, gz]]), 0.35, 6 if lod else 12, red,
                    cap_end=True)
            kc.rounded_block(mb, (sx * hx * 0.42, 6.15, gz), (0.5, 0.15, 0.5), gilt, radius=0.05, seg=1)
        kc.rounded_block(mb, (0.0, 6.4, gz), (hx * 0.42 + 0.5, 0.25, 0.3), red, radius=0.05, seg=1)
        kc.rounded_block(mb, (0.0, 4.6, gz), (hx * 0.42 - 0.4, 1.3, 0.12), red, radius=0.03, seg=1)  # the raised gate
        if not lod:
            kc.tube(mb, np.array([[-hx * 0.42 + 0.4, 3.35, gz + 0.13], [hx * 0.42 - 0.4, 3.35, gz + 0.13]]), 0.05, 6, gilt)
        out.append(mb)
    return out


BASIN_HALF = 7.0
BASIN_DEPTH = 1.0


def build_sanctum_basin(seed: int = 2106) -> list[kc.MeshBuilder]:
    out = []
    h = BASIN_HALF
    for lod in (False, True):
        rng = kc.rng_for("sanctum_basin", seed)
        mb = kc.MeshBuilder("sanctum_basin" + ("-lod1" if lod else ""))
        stone, gilt = mb.material(M_STONE), mb.material(M_GILT)
        # The floor: salt-glass tiles over the bound light beneath (the light that never moves).
        kc.rounded_block(mb, (0.0, -BASIN_DEPTH - 0.08, 0.0), (h, 0.06, h), mb.material(M_CORE), radius=0.02, seg=1)
        if lod:
            kc.rounded_block(mb, (0.0, -BASIN_DEPTH, 0.0), (h, 0.02, h), mb.material(M_GLASS), radius=0.01, seg=1)
        else:
            for x in np.arange(-h, h - 0.01, 1.0):
                for z in np.arange(-h, h - 0.01, 1.0):
                    kc.rounded_block(mb, (x + 0.5, -BASIN_DEPTH, z + 0.5), (0.48, 0.02, 0.48), mb.material(M_GLASS),
                                     radius=0.01, seg=1)
        # The rim walls (inside faces down to the floor), the rim's top at y 0, and the kneeling steps outside it.
        for (cx, cz, sx, sz) in ((0.0, -h - 0.3, h + 0.6, 0.3), (0.0, h + 0.3, h + 0.6, 0.3), (-h - 0.3, 0.0, 0.3, h),
                                 (h + 0.3, 0.0, 0.3, h)):
            kc.rounded_block(mb, (cx, -BASIN_DEPTH * 0.5 - 0.05, cz), (sx, BASIN_DEPTH * 0.5 + 0.05, sz), stone,
                             radius=0.03, seg=1, weather=STONE_W)
        for k, (grow, top) in enumerate(((1.2, -0.15), (2.0, -0.3))):
            for (cx, cz, sx, sz) in ((0.0, -h - 0.6 - grow * 0.5, h + 0.6 + grow, grow * 0.5),
                                     (0.0, h + 0.6 + grow * 0.5, h + 0.6 + grow, grow * 0.5),
                                     (-h - 0.6 - grow * 0.5, 0.0, grow * 0.5, h + 0.6),
                                     (h + 0.6 + grow * 0.5, 0.0, grow * 0.5, h + 0.6)):
                kc.rounded_block(mb, (cx, top - 0.075, cz), (sx, 0.075, sz), stone, radius=0.02, seg=1, weather=STONE_W)
        if not lod:  # the gilt Level line round the rim's top
            ring = np.array([[-h - 0.3, -0.025, -h - 0.3], [h + 0.3, -0.025, -h - 0.3], [h + 0.3, -0.025, h + 0.3],
                             [-h - 0.3, -0.025, h + 0.3], [-h - 0.3, -0.025, -h - 0.3]])
            kc.tube(mb, ring, 0.03, 4, gilt)
        del rng
        out.append(mb)
    return out


def build_archive_stacks(seed: int = 2107) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("archive_stacks", seed)
        mb = kc.MeshBuilder("archive_stacks" + ("-lod1" if lod else ""))
        black, red, gilt, paper = mb.material(M_BLACK), mb.material(M_LACQUER), mb.material(M_GILT), mb.material(M_PAPER)
        for sz in (-1.0, 1.0):  # two cases facing across a 2.4 m aisle
            z = sz * 1.6
            kc.rounded_block(mb, (0.0, 1.6, z + sz * 0.2), (3.0, 1.6, 0.25), black, radius=0.02, seg=1)
            kc.rounded_block(mb, (0.0, 3.25, z), (3.1, 0.06, 0.45), red, radius=0.02, seg=1)
            for k in range(5):  # the shelves, and the ledgers' spines in rows
                y = 0.2 + 0.62 * k
                kc.rounded_block(mb, (0.0, y, z), (3.0, 0.025, 0.42), red, radius=0.01, seg=1)
                if lod:
                    kc.rounded_block(mb, (0.0, y + 0.22, z - sz * 0.05), (2.9, 0.2, 0.3), paper, radius=0.01, seg=1)
                    continue
                x = -2.9
                while x < 2.85:
                    t = rng.uniform(0.05, 0.11)
                    hh = rng.uniform(0.32, 0.5)
                    mat = paper if rng.random() < 0.7 else red
                    kc.rounded_block(mb, (x + t * 0.5, y + 0.025 + hh * 0.5, z - sz * 0.05), (t * 0.5 - 0.004, hh * 0.5,
                                     0.3), mat, rot=kc.rot_z(rng.normal(0, 0.03)), radius=0.006, seg=1)
                    x += t + (0.25 if rng.random() < 0.04 else 0.0)
            if not lod:
                kc.tube(mb, np.array([[-3.0, 3.1, z - sz * 0.5], [3.0, 3.1, z - sz * 0.5]]), 0.015, 4, gilt)
        if not lod:  # the rolling ladder against the near case, and the lectern with the Cantor roll
            for sx in (-0.25, 0.25):
                kc.tube(mb, np.array([[1.0 + sx, 0.0, 0.9], [1.0 + sx, 3.1, 1.35]]), 0.025, 5, black)
            for k in range(9):
                t = (k + 0.5) / 9
                kc.tube(mb, np.array([[0.75, 3.1 * t, 0.9 + 0.45 * t], [1.25, 3.1 * t, 0.9 + 0.45 * t]]), 0.015, 4, gilt)
            kc.tube(mb, np.array([[3.6, 0.0, 0.0], [3.6, 1.0, 0.0]]), 0.06, 8, black)
            kc.rounded_block(mb, (3.6, 1.1, 0.0), (0.32, 0.03, 0.25), black, rot=kc.rot_z(0.35), radius=0.01, seg=1)
            kc.rounded_block(mb, (3.6, 1.14, 0.0), (0.28, 0.015, 0.22), paper, rot=kc.rot_z(0.35), radius=0.005, seg=1)
        out.append(mb)
    return out


TARGETS = {
    "bowl_dome": build_bowl_dome,
    "bowl_dome_lit": lambda: build_bowl_dome(lit=True),
    "ansedra_far_domes": build_far_domes,
    "ansedra_far_domes_lit": lambda: build_far_domes(lit=True),
    "pursuit_barge": build_pursuit_barge,
    "lacquer_hall": build_lacquer_hall,
    "lacquer_court_ground": build_court_ground,
    "sanctum_basin": build_sanctum_basin,
    "archive_stacks": build_archive_stacks,
}
