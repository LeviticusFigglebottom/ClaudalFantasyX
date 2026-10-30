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

The city's walk (M4-A2P-043, env-art-b; docs/kb/plan/act2/zones/ch13_ansedra.md):
  ansedra_causeway_6m one 6 m module of the causeways along Z: white Order-marble deck slabs (top y 0) between low
                      marble kerbs, on three piers to the lagoon bed. Origin at the deck's centre.
  gold_lamp_post      the causeways' lamp-post (bible §5.8) on its own pier in the water: a slender marble shaft, a
                      gilt cage and an unlit salt-glass globe (the Order lights nothing on the water). Origin at the
                      water line under the shaft.
  island_plinth_16m   an island's edge: a paved marble top (y 0) and three steps down into the water all round, the
                      Level line inlaid in gilt across it. Scaled per island (origin the top's centre, so the top stays
                      at y 0).
  mooring_platform    the outer moorings (16 x 16 m, top y 0): a marble landing stage with water-steps and marble
                      bollards on its east and west edges, two punt-pole racks, and the lacquered mooring arch over the
                      north exit. Origin at the platform's top centre.
The Sanctum of the Level (M4-A2P-043; ch13_sanctum.md), in its greybox's frame (the nave 24 x 36 m, floor y 0):
  sanctum_nave_bay    one 6 m bay of the nave along Z: Order-marble walls (inner faces at x +-11.75, 10 m) on a dado,
                      pilasters at the bay's ends, the gilt Level line at eye height, and a segmental marble vault
                      springing at 10 m to a 15 m crown. Origin at the bay's floor centre.
  sanctum_nave_floor  the nave's polished floor (24 x 36 m, top y 0) round the basin's opening (10.8 x 18.8 m), the
                      kneeling band of darker stones round the opening edged in gilt. Origin at the nave's centre.
  sanctum_basin_nave  the basin (10 x 18 m inside): the rim is the kneeling ledge (0.4 m high), the floor salt-glass
                      tiles 1 m under the rim over the bound light (the light that never moves); the scene's still water
                      stands at y 0.3. Origin at the basin's centre on the nave floor.
  sanctum_vestibule   the gatehouse (12 x 12 m, 6 m ceiling) and the nave's south end wall: the lacquered double door
                      shut in the south opening, the doorway into the nave under its gilt Level-line lintel. Origin at
                      the vestibule's floor centre (the nave's south wall stands 6 m to its -Z).
  sanctum_bench       a marble bench (2.4 m) for the vestibule's walls. Origin at its foot, centre.
  sanctum_apse        the nave's north end wall with the apse's arch (10 m wide): a plain marble half-dome over a raised
                      step, the gilt Level line round it at eye height, nothing on it. Origin at the end wall's foot.
  cantor_stand        the Cantor's stand at the binding: a marble post with a gilt-edged slanted top. Origin at its
                      foot.
The Lamp Archive's reading room (M4-A2P-043; ch13_lamp_archive.md), in its greybox's frame (20 x 32 m, floor y 0):
  archive_case        one double-faced ledger case (5 x 6 x 1 m, along X), black lacquer with red shelves, the ledgers'
                      cream and red spines in runs on both faces, a gilt Level line along its top. Origin at its foot,
                      centre.
  archive_hall_bay    one 6.4 m bay of the room along Z: the paved floor, cold marble walls (inner faces at +-9.75) to the
                      clerestory band, open clerestory windows (grey daylight is the room's only light) between piers,
                      and a skinned marble vault springing at 9.2 m. Origin at the bay's floor centre.
  archive_end_walls   the room's end walls: the south one with the lacquered door shut behind the party, the north one
                      plain; 32 m apart. Origin at the south wall's foot, centre (the room runs to -Z).
  reading_table       a black-lacquered reading table (2 x 4 m) with ledgers open on it, a reading weight and an unlit
                      oil lamp. Origin at its foot, centre.
  roll_table          the same table with the Cantor roll unrolled along it, its rollers at the ends.
  ledger_stack        a pile of ledgers and rolled lists for the floor by the tables (the days' work). Origin at its foot.
The Lacquer Court at the wedding (M4-A2P-044; ch14_lacquer_court.md), in its greybox's frame: the court 30 x 24 m (z 0
to -24, floor y 0), the water-steps down to the barge's deck (-0.6) on +Z, the lagoon at y -1.0. The bespoke pieces'
origin is the zone's origin, so they are placed at (0, 0):
  court_ground        the court's paving with the Level line across it, the marble terrace round it that carries the
                      halls, and the edge down to the lagoon.
  court_balustrades   the low marble balustrades with gilt coping on the court's edge walls (COURT_WALLS) and the
                      water-steps' side walls.
  court_water_steps   the water-steps from the court (y 0) down to the barge's deck (-0.6) between their walls.
  court_colonnade_roofs  the colonnades' lacquered beams and their lean-to tiled roofs over the court's N, W and E edges.
  court_water_gate    the court's water-gate over the barge channel: two red posts, a lintel and the raised drop-gate.
Placed pieces (origin at their foot):
  court_column        one red-lacquered column (6 m) on a marble base with a gilt capital.
  court_gallery       a guests' gallery (3 x 16 m, 0.6 m high): a marble platform with red benches along it.
  wedding_dais        the dais (8 x 3 m, 0.8 m): marble steps, the red bridal carpet, two gilt standards with red
                      streamers hanging dead still, the offerings (cloth bolts, sealed jars). Origin at its centre.
  conclave_gallery    the Conclave's raised gallery (5 x 3 m, 2 m): lacquered screens, five seats, a gilt canopy.
  gilt_lamp_stand     a gilt lamp-stand with its flame in a bowl (lit for the ceremony: the zone puts a light on it).
  stillguard_rack     the Stillguard's spears racked by the gallery.
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
M_CLOTH_RED = "kit_keth_red"  # the bridal red: a woven, matte red (bridal_barge.py's)
M_JAR = "kit_earthenware"
M_FLAME = "kit_lamp_flame"

TRI_BUDGET = {"bowl_dome": (6000, 400), "ansedra_far_domes": (8000, 3000), "pursuit_barge": (10000, 700),
              "lacquer_hall": (8000, 500), "lacquer_court_ground": (12000, 800), "sanctum_basin": (8000, 500),
              "archive_stacks": (9000, 500), "ansedra_causeway_6m": (3000, 200), "gold_lamp_post": (1500, 200),
              "island_plinth_16m": (8000, 400), "mooring_platform": (9000, 650), "sanctum_nave_bay": (6000, 600),
              "sanctum_nave_floor": (12000, 300), "sanctum_basin_nave": (6000, 300), "sanctum_vestibule": (8000, 600),
              "sanctum_bench": (600, 60), "sanctum_apse": (8000, 900), "cantor_stand": (800, 80),
              "archive_case": (6000, 300), "archive_hall_bay": (6000, 500), "archive_end_walls": (3000, 300),
              "reading_table": (2500, 150), "roll_table": (2500, 200), "ledger_stack": (900, 60),
              "court_ground": (12000, 400), "court_balustrades": (8000, 600), "court_water_steps": (1500, 200),
              "court_colonnade_roofs": (6000, 600), "court_water_gate": (2000, 300), "court_column": (700, 120),
              "court_gallery": (3000, 300), "wedding_dais": (5000, 400), "conclave_gallery": (4000, 300),
              "gilt_lamp_stand": (900, 150), "stillguard_rack": (900, 80)}
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


def _revolve_at(mb, x, z, ys, rs, sides, mat, *, cap=False):
    """_revolve about a vertical axis through (x, z)."""
    pts = np.stack([np.full(len(ys), x), ys, np.full(len(ys), z)], -1)
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


# --- the city's walk (M4-A2P-043) ------------------------------------------------------------------------------
CAUSEWAY_LEN = 6.0
CAUSEWAY_HALF_W = 1.8  # the deck between the kerbs (the greybox's 3.6 m)
KERB = (0.2, 0.5)  # half width, height over the deck
BED_Y = -1.6  # the greybox's lagoon bed (its top)
LAMP_H = 3.2
PLINTH_HALF = 8.0
PLINTH_STEPS = 3
PLINTH_STEP = (0.5, 0.25)  # tread, rise
MOOR_HALF = 8.0
MOOR_EXIT_HALF = 2.2  # the north exit to the causeway (the greybox's gap)
SUBMERGED_WET = 0.3  # each step further under the water darker (wet), so the white stone doesn't glow cyan
MARBLE_W = kc.Weathering(moss=0.0, salt=0.06, wet=0.04, erosion=0.08, noise_scale_m=1.2)


def _paving(mb, rng, hx: float, hz: float, size: float, stone, *, bed: bool = False) -> None:
    """Thin marble slabs, the joints shadowed (top at y 0); with `bed`, over their own bedding slab (a floor with no
    block under it would show the sky through its joints)."""
    if bed:
        kc.rounded_block(mb, (0.0, -0.2, 0.0), (hx, 0.14, hz), stone, radius=0.01, seg=1, weather=MARBLE_W)
    nx, nz = max(1, round(2 * hx / size)), max(1, round(2 * hz / size))
    sx, sz = 2 * hx / nx, 2 * hz / nz
    for i in range(nx):
        for k in range(nz):
            kc.rounded_block(mb, (-hx + sx * (i + 0.5), -0.03, -hz + sz * (k + 0.5)), (sx * 0.5 - 0.01, 0.03, sz * 0.5 - 0.01),
                             stone, radius=0.008, seg=1, weather=MARBLE_W, variation=float(rng.random()))


def build_causeway(seed: int = 2111) -> list[kc.MeshBuilder]:
    out = []
    hl = CAUSEWAY_LEN * 0.5
    hw = CAUSEWAY_HALF_W
    for lod in (False, True):
        rng = kc.rng_for("ansedra_causeway_6m", seed)
        mb = kc.MeshBuilder("ansedra_causeway_6m" + ("-lod1" if lod else ""))
        stone, gilt = mb.material(M_STONE), mb.material(M_GILT)
        kc.rounded_block(mb, (0.0, -0.25, 0.0), (hw + KERB[0] * 2, 0.19, hl), stone, radius=0.03, seg=1,
                         weather=MARBLE_W)  # the deck's bedding beam
        if lod:
            kc.rounded_block(mb, (0.0, -0.03, 0.0), (hw, 0.03, hl), stone, radius=0.01, seg=1, weather=MARBLE_W)
        else:  # slabs laid across the walk, alternate rows offset (a running bond)
            for k in range(6):
                z0 = -hl + k + 0.5
                cuts = [-hw, 0.0, hw] if k % 2 else [-hw, -hw * 0.5, hw * 0.5, hw]
                for a, b in zip(cuts[:-1], cuts[1:]):
                    kc.rounded_block(mb, ((a + b) * 0.5, -0.03, z0), ((b - a) * 0.5 - 0.008, 0.03, 0.492), stone,
                                     radius=0.008, seg=1, weather=MARBLE_W, variation=float(rng.random()))
        for sx in (-1.0, 1.0):  # the kerbs, a gilt fillet along their outer top edge
            kx = sx * (hw + KERB[0])
            kc.rounded_block(mb, (kx, KERB[1] * 0.5 - 0.05, 0.0), (KERB[0], KERB[1] * 0.5 + 0.05, hl - 0.005), stone,
                             radius=0.04, seg=1 if lod else 2, weather=MARBLE_W, variation=float(rng.random()))
            if not lod:
                kc.tube(mb, np.array([[kx + sx * KERB[0], KERB[1] - 0.03, -hl], [kx + sx * KERB[0], KERB[1] - 0.03, hl]]),
                        0.018, 4, gilt)
        for z in ((-hl + 0.5, hl - 0.5) if lod else (-hl + 0.5, 0.0, hl - 0.5)):  # the piers to the bed
            ph = (-0.44 - BED_Y) * 0.5
            kc.rounded_block(mb, (0.0, -0.44 - ph, z), (hw + 0.1, ph, 0.45), stone, radius=0.05, seg=1,
                             weather=kc.Weathering(moss=0.0, salt=0.25, wet=0.3, erosion=0.12, noise_scale_m=0.8),
                             wet_bias=0.2)
        out.append(mb)
    return out


def build_lamp_post(seed: int = 2112) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("gold_lamp_post", seed)
        mb = kc.MeshBuilder("gold_lamp_post" + ("-lod1" if lod else ""))
        stone, gilt, glass = mb.material(M_STONE), mb.material(M_GILT), mb.material(M_GLASS)
        sides = 6 if lod else 12
        # The pier from the bed, a square marble base over the water, the shaft.
        kc.rounded_block(mb, (0.0, (BED_Y + 0.25) * 0.5, 0.0), (0.42, (0.25 - BED_Y) * 0.5, 0.42), stone, radius=0.04,
                         seg=1, weather=kc.Weathering(moss=0.0, salt=0.25, wet=0.3, erosion=0.12), wet_bias=0.2)
        kc.rounded_block(mb, (0.0, 0.33, 0.0), (0.3, 0.08, 0.3), stone, radius=0.03, seg=1, weather=MARBLE_W)
        ys = np.array([0.41, 0.6, 0.7, LAMP_H - 0.55, LAMP_H - 0.45])
        rs = np.array([0.13, 0.1, 0.075, 0.06, 0.09])
        _revolve(mb, ys, rs, sides, M_STONE, cap=True)
        # The gilt cage: a collar, four ribs bowing out round the globe, a cap and a finial.
        y0, y1 = LAMP_H - 0.45, LAMP_H + 0.15
        _revolve(mb, np.array([y0 - 0.04, y0, y0 + 0.04]), np.array([0.1, 0.14, 0.12]), sides, M_GILT)
        if lod:
            _revolve(mb, np.array([y0 + 0.04, (y0 + y1) * 0.5, y1]), np.array([0.12, 0.2, 0.08]), sides, M_GLASS)
        else:
            t = np.linspace(0.0, 1.0, 9)
            yy = y0 + 0.04 + (y1 - y0 - 0.04) * t
            _revolve(mb, yy, 0.05 + 0.15 * np.sin(np.pi * np.clip(t * 1.05, 0, 1)), 16, M_GLASS, cap=True)
            for k in range(4):
                a = k * math.pi * 0.5 + math.pi * 0.25
                r = 0.06 + 0.17 * np.sin(np.pi * t)
                pts = np.stack([np.cos(a) * r, yy, np.sin(a) * r], -1)
                kc.tube(mb, pts, 0.012, 4, gilt)
        _revolve(mb, np.array([y1, y1 + 0.03, y1 + 0.12, y1 + 0.13]), np.array([0.12, 0.13, 0.04, 0.0]), sides, M_GILT)
        kc.tube(mb, np.array([[0.0, y1 + 0.12, 0.0], [0.0, y1 + 0.4, 0.0]]), np.array([0.018, 0.004]), 5, gilt)
        if not lod:  # the Level ring on the shaft (a level line circling it)
            _revolve(mb, np.array([1.55, 1.57, 1.59]), np.array([0.064, 0.072, 0.064]), sides, M_GILT)
        del rng
        out.append(mb)
    return out


def build_island_plinth(seed: int = 2113) -> list[kc.MeshBuilder]:
    out = []
    h = PLINTH_HALF
    tread, rise = PLINTH_STEP
    for lod in (False, True):
        rng = kc.rng_for("island_plinth_16m", seed)
        mb = kc.MeshBuilder("island_plinth_16m" + ("-lod1" if lod else ""))
        stone, gilt = mb.material(M_STONE), mb.material(M_GILT)
        kc.rounded_block(mb, (0.0, -0.45, 0.0), (h, 0.39, h), stone, radius=0.04, seg=1, weather=MARBLE_W)
        if lod:
            kc.rounded_block(mb, (0.0, -0.03, 0.0), (h, 0.03, h), stone, radius=0.01, seg=1, weather=MARBLE_W)
        else:
            _paving(mb, rng, h, h, 2.0, stone)
            kc.rounded_block(mb, (0.0, 0.002, 0.0), (h - 0.6, 0.003, 0.05), gilt, radius=0.002, seg=1)  # the Level line
        wet = kc.Weathering(moss=0.0, salt=0.2, wet=0.2, erosion=0.1, noise_scale_m=1.0)
        for k in range(PLINTH_STEPS):  # the steps down into the lagoon, each a ring of four blocks
            g = h + tread * (k + 1)
            top = -rise * (k + 1)
            hy = 0.5 * (top - BED_Y)
            cy = top - hy
            for (cx, cz, sx, sz) in ((0.0, -g + tread * 0.5, g, tread * 0.5), (0.0, g - tread * 0.5, g, tread * 0.5),
                                     (-g + tread * 0.5, 0.0, tread * 0.5, g - tread), (g - tread * 0.5, 0.0, tread * 0.5, g - tread)):
                kc.rounded_block(mb, (cx, cy, cz), (sx, hy, sz), stone, radius=0.03, seg=1, weather=wet if k else MARBLE_W,
                                 variation=float(rng.random()), wet_bias=SUBMERGED_WET * k)
        out.append(mb)
    return out


def build_mooring_platform(seed: int = 2114) -> list[kc.MeshBuilder]:
    out = []
    h = MOOR_HALF
    for lod in (False, True):
        rng = kc.rng_for("mooring_platform", seed)
        mb = kc.MeshBuilder("mooring_platform" + ("-lod1" if lod else ""))
        stone, gilt, red, black, timber = (mb.material(M_STONE), mb.material(M_GILT), mb.material(M_LACQUER),
                                           mb.material(M_BLACK), mb.material(M_DECK))
        sides = 6 if lod else 12
        kc.rounded_block(mb, (0.0, -0.45, 0.0), (h, 0.39, h), stone, radius=0.04, seg=1, weather=MARBLE_W)
        if lod:
            kc.rounded_block(mb, (0.0, -0.03, 0.0), (h, 0.03, h), stone, radius=0.01, seg=1, weather=MARBLE_W)
        else:
            _paving(mb, rng, h, h, 2.0, stone)
        wet = kc.Weathering(moss=0.0, salt=0.25, wet=0.3, erosion=0.12, noise_scale_m=0.8)
        # The water-steps along the east and west edges, where the barges lie; a plain wall on the south.
        for sx in (-1.0, 1.0):
            for k in range(3):
                top = -0.2 * (k + 1)
                hy = 0.5 * (top - BED_Y)
                kc.rounded_block(mb, (sx * (h + 0.35 + 0.7 * k), top - hy, 0.0), (0.35, hy, h - 1.0), stone, radius=0.03,
                                 seg=1, weather=wet, variation=float(rng.random()), wet_bias=SUBMERGED_WET * (k + 1))
            for z in (-4.5, 0.0, 4.5):  # marble bollards with gilt caps
                kc.tube(mb, np.array([[sx * (h - 0.45), 0.0, z], [sx * (h - 0.45), 0.55, z]]),
                        np.array([0.17, 0.14]), sides, stone, cap_end=True)
                if not lod:
                    _revolve_at(mb, sx * (h - 0.45), z, np.array([0.5, 0.56, 0.62, 0.64]), np.array([0.15, 0.17, 0.1, 0.0]),
                                sides, M_GILT)
        kc.rounded_block(mb, (0.0, (BED_Y - 0.06) * 0.5 - 0.03, h + 0.3), (h + 2.4, (-0.06 - BED_Y) * 0.5, 0.3), stone,
                         radius=0.03, seg=1, weather=wet)
        # The punt-pole racks: two low timber trestles with the poles laid across them, along Z.
        for sx in (-1.0, 1.0):
            rx, rz = sx * (h - 1.7), 5.6
            for dz in (-1.3, 1.3):
                for lx in (-0.35, 0.35):  # a trestle: two splayed legs each side and a cross-bar
                    kc.tube(mb, np.array([[rx + lx * 1.4, 0.0, rz + dz], [rx + lx * 0.5, 0.8, rz + dz]]), 0.045,
                            4 if lod else 6, timber, cap_end=True)
                kc.tube(mb, np.array([[rx - 0.5, 0.82, rz + dz], [rx + 0.5, 0.82, rz + dz]]), 0.06, 4 if lod else 6,
                        timber, cap_end=True, cap_start=True)
            n_poles = 2 if lod else 5
            for k in range(n_poles):
                px = rx - 0.36 + 0.72 * k / max(1, n_poles - 1)
                pz = rz + 0.4 * (float(rng.random()) - 0.5)
                kc.tube(mb, np.array([[px, 0.92, pz - 2.3], [px, 0.92, pz + 2.3]]), 0.035, 4 if lod else 5, timber,
                        cap_end=True, cap_start=True)
        # The mooring arch over the north exit: two red posts, a black tie beam, a gilt-capped red lintel with
        # upswept ends, and the gilt Level plaque between them.
        ax, az, ah = MOOR_EXIT_HALF + 0.45, -h + 0.5, 5.2
        for sx in (-1.0, 1.0):
            kc.rounded_block(mb, (sx * ax, 0.2, az), (0.42, 0.2, 0.42), stone, radius=0.04, seg=1, weather=MARBLE_W)
            kc.tube(mb, np.array([[sx * ax, 0.4, az], [sx * ax, ah, az]]), np.array([0.26, 0.22]), sides, red, cap_end=True)
            if not lod:
                _revolve_at(mb, sx * ax, az, np.array([0.4, 0.46, 0.52]), np.array([0.3, 0.3, 0.26]), sides, M_GILT)
        kc.rounded_block(mb, (0.0, ah - 0.9, az), (ax + 0.3, 0.14, 0.16), black, radius=0.03, seg=1)
        kc.rounded_block(mb, (0.0, ah + 0.2, az), (ax + 0.9, 0.2, 0.3), red, radius=0.04, seg=1)
        kc.rounded_block(mb, (0.0, ah + 0.45, az), (ax + 1.0, 0.05, 0.34), gilt, radius=0.02, seg=1)
        for sx in (-1.0, 1.0):
            kc.tube(mb, np.array([[sx * (ax + 1.0), ah + 0.45, az], [sx * (ax + 1.5), ah + 0.9, az]]),
                    np.array([0.12, 0.03]), 5, gilt)
        kc.rounded_block(mb, (0.0, ah - 0.35, az), (0.7, 0.32, 0.05), gilt, radius=0.02, seg=1)
        if not lod:
            kc.rounded_block(mb, (0.0, ah - 0.35, az + 0.055), (0.55, 0.012, 0.01), black, radius=0.004, seg=1)
        out.append(mb)
    return out


# --- the Sanctum of the Level (M4-A2P-043) ------------------------------------------------------------------------
NAVE_HALF_W = 11.75  # the walls' inner faces (the greybox's walls at +-12, 0.5 m thick)
NAVE_WALL_H = 10.0
NAVE_CROWN = 15.0
NAVE_BAY = 6.0
NAVE_HALF_L = 18.0
BASIN_IN = (5.0, 9.0)  # the basin's inside half extents (x, z): the greybox's ledges stand on its rim
BASIN_RIM = 0.4  # the rim's width and height (the greybox's KneelingLedge blocks)
BASIN_FLOOR_Y = -0.6
KNEEL_BAND = 1.2
EYE_H = 1.6
VEST_HALF = 6.0
VEST_H = 6.0
VEST_DOOR_HALF = 2.2  # the gate (the greybox's GateStep opening)
NAVE_DOOR = (3.0, 5.0)  # the doorway into the nave: half width, height
APSE = (5.0, 8.0)  # the apse's radius and its arch's spring height
APSE_STEP = 0.3
SHELL_COL = (0.0, 0.0, 0.0, 0.2)
SHELL_SKIN_M = 0.3
WALL_OVERLAP_M = 1.0  # the nave walls run past the vault's spring, so no seam lets the sun in


def _shell(mb, grid: np.ndarray, mat: int, inside, *, uv_scale: float = 0.25, skin_m: float = SHELL_SKIN_M) -> None:
    """A (rows, cols, 3) grid as a smooth surface facing `inside` (a point on its lit side), with an outward skin
    `skin_m` behind it."""
    rows, cols = grid.shape[:2]
    u = np.cumsum(np.r_[0.0, np.linalg.norm(np.diff(grid[0], axis=0), axis=-1)])
    v = np.cumsum(np.r_[0.0, np.linalg.norm(np.diff(grid[:, 0], axis=0), axis=-1)])
    uv = np.stack(np.meshgrid(u, v), -1) * uv_scale
    probe = kc.MeshBuilder("probe")
    kc.quad_strip(probe, grid, probe.material(M_STONE), uv=uv, col=SHELL_COL, uv2=(0.8, 0.5))
    n = np.asarray(probe.nrm)[rows * cols // 2 + cols // 2]
    flip = float(np.dot(n, np.asarray(inside, float) - grid[rows // 2, cols // 2])) < 0.0
    kc.quad_strip(mb, grid, mat, uv=uv, col=SHELL_COL, uv2=(0.8, 0.5), flip=flip)
    if skin_m > 0.0:  # the back skin: a single face casts no shadow from behind, so the sun would light the room
        away = grid - np.asarray(inside, float)
        away = away / np.maximum(np.linalg.norm(away, axis=-1, keepdims=True), 1e-6)
        kc.quad_strip(mb, grid + away * skin_m, mat, uv=uv, col=SHELL_COL, uv2=(0.8, 0.5), flip=not flip)


def build_sanctum_nave_bay(seed: int = 2121) -> list[kc.MeshBuilder]:
    out = []
    hb = NAVE_BAY * 0.5
    for lod in (False, True):
        rng = kc.rng_for("sanctum_nave_bay", seed)
        mb = kc.MeshBuilder("sanctum_nave_bay" + ("-lod1" if lod else ""))
        stone, gilt = mb.material(M_STONE), mb.material(M_GILT)
        for sx in (-1.0, 1.0):
            kc.rounded_block(mb, (sx * (NAVE_HALF_W + 0.4), (NAVE_WALL_H + WALL_OVERLAP_M) * 0.5, 0.0),
                             (0.4, (NAVE_WALL_H + WALL_OVERLAP_M) * 0.5, hb),
                             stone, radius=0.02, seg=1, weather=MARBLE_W, variation=float(rng.random()))
            if not lod:
                kc.rounded_block(mb, (sx * (NAVE_HALF_W - 0.06), 0.35, 0.0), (0.06, 0.35, hb), stone, radius=0.02,
                                 seg=1, weather=MARBLE_W)  # the dado
                kc.tube(mb, np.array([[sx * (NAVE_HALF_W - 0.01), EYE_H, -hb], [sx * (NAVE_HALF_W - 0.01), EYE_H, hb]]),
                        0.025, 4, gilt)  # the Level line
                kc.rounded_block(mb, (sx * (NAVE_HALF_W - 0.2), NAVE_WALL_H - 0.2, 0.0), (0.2, 0.2, hb), stone,
                                 radius=0.05, seg=1, weather=MARBLE_W)  # the cornice
            for z in (-hb, hb):  # the pilasters (half of one at each end: the next bay brings the other half)
                kc.rounded_block(mb, (sx * (NAVE_HALF_W - 0.17), NAVE_WALL_H * 0.5, z * 0.97), (0.17, NAVE_WALL_H * 0.5,
                                 0.4 * 0.5 if lod else 0.2), stone, radius=0.03, seg=1, weather=MARBLE_W)
        # The vault: a segmental arc from the cornice (x +-11.75, 10 m) to the crown (15 m).
        rise = NAVE_CROWN - NAVE_WALL_H
        r = (NAVE_HALF_W ** 2 + rise ** 2) / (2 * rise)
        cy = NAVE_CROWN - r
        half_a = math.asin(NAVE_HALF_W / r)
        a = np.linspace(-half_a, half_a, 6 if lod else 18)
        arc = np.stack([r * np.sin(a), cy + r * np.cos(a)], -1)
        grid = np.array([[[x, y, z] for x, y in arc] for z in (-hb, hb)])
        _shell(mb, grid, stone, (0.0, 2.0, 0.0))
        if not lod:  # a flat marble rib over the pilasters at each end
            for z in (-hb + 0.01, hb - 0.01):
                pts = np.array([[x * 0.995, y - 0.08, z] for x, y in arc])
                kc.tube(mb, pts, 0.12, 4, stone)
        out.append(mb)
    return out


def build_sanctum_nave_floor(seed: int = 2122) -> list[kc.MeshBuilder]:
    out = []
    hx, hz = NAVE_HALF_W + 0.25, NAVE_HALF_L
    ox, oz = BASIN_IN[0] + BASIN_RIM, BASIN_IN[1] + BASIN_RIM
    kx, kz = ox + KNEEL_BAND, oz + KNEEL_BAND
    for lod in (False, True):
        rng = kc.rng_for("sanctum_nave_floor", seed)
        mb = kc.MeshBuilder("sanctum_nave_floor" + ("-lod1" if lod else ""))
        stone, gilt = mb.material(M_STONE), mb.material(M_GILT)
        # The floor round the opening as four slabs (the polished field), then the kneeling band inside them; each
        # field on a bedding slab so its joints don't show the dark under the floor.
        for (cx, cz, sx, sz) in ((0.0, -(hz + oz) * 0.5, hx, (hz - oz) * 0.5), (0.0, (hz + oz) * 0.5, hx, (hz - oz) * 0.5),
                                 (-(hx + ox) * 0.5, 0.0, (hx - ox) * 0.5, oz), ((hx + ox) * 0.5, 0.0, (hx - ox) * 0.5, oz)):
            if not lod:
                kc.rounded_block(mb, (cx, -0.4, cz), (sx, 0.1, sz), stone, radius=0.01, seg=1, weather=MARBLE_W)
        for (cx, cz, sx, sz) in ((0.0, -(hz + kz) * 0.5, hx, (hz - kz) * 0.5), (0.0, (hz + kz) * 0.5, hx, (hz - kz) * 0.5),
                                 (-(hx + kx) * 0.5, 0.0, (hx - kx) * 0.5, kz), ((hx + kx) * 0.5, 0.0, (hx - kx) * 0.5, kz)):
            if lod:
                kc.rounded_block(mb, (cx, -0.15, cz), (sx, 0.15, sz), stone, radius=0.01, seg=1, weather=MARBLE_W)
                continue
            nx, nz = max(1, round(2 * sx / 2.0)), max(1, round(2 * sz / 2.0))
            for i in range(nx):
                for k in range(nz):
                    w, d = 2 * sx / nx, 2 * sz / nz
                    kc.rounded_block(mb, (cx - sx + w * (i + 0.5), -0.15, cz - sz + d * (k + 0.5)),
                                     (w * 0.5 - 0.006, 0.15, d * 0.5 - 0.006), stone, radius=0.006, seg=1,
                                     weather=MARBLE_W, variation=float(rng.random()))
        for (cx, cz, sx, sz) in ((0.0, -(oz + kz) * 0.5, kx, KNEEL_BAND * 0.5), (0.0, (oz + kz) * 0.5, kx, KNEEL_BAND * 0.5),
                                 (-(ox + kx) * 0.5, 0.0, KNEEL_BAND * 0.5, oz), ((ox + kx) * 0.5, 0.0, KNEEL_BAND * 0.5, oz)):
            kc.rounded_block(mb, (cx, -0.15, cz), (sx, 0.15, sz), stone, radius=0.01, seg=1,
                             weather=kc.Weathering(moss=0.0, salt=0.0, wet=0.5, erosion=0.2), wet_bias=0.35,
                             variation=0.9)  # the kneeling band: worn darker by the kneelers
        if not lod:
            ring = np.array([[-kx, 0.004, -kz], [kx, 0.004, -kz], [kx, 0.004, kz], [-kx, 0.004, kz], [-kx, 0.004, -kz]])
            kc.tube(mb, ring, 0.02, 4, gilt)
        out.append(mb)
    return out


def build_sanctum_basin_nave(seed: int = 2123) -> list[kc.MeshBuilder]:
    out = []
    ix, iz = BASIN_IN
    for lod in (False, True):
        rng = kc.rng_for("sanctum_basin_nave", seed)
        mb = kc.MeshBuilder("sanctum_basin_nave" + ("-lod1" if lod else ""))
        stone, gilt, glass = mb.material(M_STONE), mb.material(M_GILT), mb.material(M_GLASS)
        kc.rounded_block(mb, (0.0, BASIN_FLOOR_Y - 0.1, 0.0), (ix, 0.06, iz), mb.material(M_CORE), radius=0.02, seg=1)
        if lod:
            kc.rounded_block(mb, (0.0, BASIN_FLOOR_Y, 0.0), (ix, 0.02, iz), glass, radius=0.01, seg=1)
        else:
            for x in np.arange(-ix, ix - 0.01, 1.0):
                for z in np.arange(-iz, iz - 0.01, 1.0):
                    kc.rounded_block(mb, (x + 0.5, BASIN_FLOOR_Y, z + 0.5), (0.48, 0.02, 0.48), glass, radius=0.01,
                                     seg=1)
        y0 = BASIN_FLOOR_Y - 0.16
        hy = (BASIN_RIM - y0) * 0.5
        for (cx, cz, sx, sz) in ((0.0, -iz - BASIN_RIM * 0.5, ix + BASIN_RIM, BASIN_RIM * 0.5),
                                 (0.0, iz + BASIN_RIM * 0.5, ix + BASIN_RIM, BASIN_RIM * 0.5),
                                 (-ix - BASIN_RIM * 0.5, 0.0, BASIN_RIM * 0.5, iz),
                                 (ix + BASIN_RIM * 0.5, 0.0, BASIN_RIM * 0.5, iz)):
            kc.rounded_block(mb, (cx, y0 + hy, cz), (sx, hy, sz), stone, radius=0.04, seg=1 if lod else 2,
                             weather=MARBLE_W, variation=float(rng.random()))
        if not lod:  # the gilt Level line round the rim's inner edge
            e = (ix + 0.02, iz + 0.02)
            ring = np.array([[-e[0], BASIN_RIM - 0.02, -e[1]], [e[0], BASIN_RIM - 0.02, -e[1]],
                             [e[0], BASIN_RIM - 0.02, e[1]], [-e[0], BASIN_RIM - 0.02, e[1]], [-e[0], BASIN_RIM - 0.02, -e[1]]])
            kc.tube(mb, ring, 0.025, 4, gilt)
        out.append(mb)
    return out


def build_sanctum_vestibule(seed: int = 2124) -> list[kc.MeshBuilder]:
    out = []
    h = VEST_HALF
    for lod in (False, True):
        rng = kc.rng_for("sanctum_vestibule", seed)
        mb = kc.MeshBuilder("sanctum_vestibule" + ("-lod1" if lod else ""))
        stone, gilt, red, black = (mb.material(M_STONE), mb.material(M_GILT), mb.material(M_LACQUER),
                                   mb.material(M_BLACK))
        if lod:
            kc.rounded_block(mb, (0.0, -0.15, 0.0), (h, 0.15, h), stone, radius=0.01, seg=1, weather=MARBLE_W)
        else:
            _paving(mb, rng, h, h, 2.0, stone, bed=True)
        kc.rounded_block(mb, (0.0, VEST_H + 0.2, 0.0), (h + 0.5, 0.2, h + 0.25), stone, radius=0.02, seg=1,
                         weather=MARBLE_W)  # the ceiling
        for sx in (-1.0, 1.0):  # the side walls, and the south wall either side of the gate
            kc.rounded_block(mb, (sx * (h + 0.25), VEST_H * 0.5, 0.0), (0.25, VEST_H * 0.5, h), stone, radius=0.02,
                             seg=1, weather=MARBLE_W, variation=float(rng.random()))
            w = (h + 0.5 - VEST_DOOR_HALF) * 0.5
            kc.rounded_block(mb, (sx * (VEST_DOOR_HALF + w), VEST_H * 0.5, h + 0.25), (w, VEST_H * 0.5, 0.25), stone,
                             radius=0.02, seg=1, weather=MARBLE_W)
            # The gate's red frame and the two black-lacquered leaves, shut.
            kc.rounded_block(mb, (sx * (VEST_DOOR_HALF - 0.1), 2.1, h + 0.15), (0.12, 2.1, 0.18), red, radius=0.02, seg=1)
            kc.rounded_block(mb, (sx * VEST_DOOR_HALF * 0.5 - sx * 0.05, 2.0, h + 0.2), (VEST_DOOR_HALF * 0.5 - 0.1, 2.0,
                             0.06), black, radius=0.015, seg=1)
            if not lod:  # gilt studs in rows on each leaf, and a ring pull
                for yy in np.arange(0.5, 3.8, 0.55):
                    for xx in np.linspace(0.35, VEST_DOOR_HALF - 0.45, 3):
                        kc.rounded_block(mb, (sx * xx, yy, h + 0.13), (0.035, 0.035, 0.02), gilt, radius=0.012, seg=1)
                kc.tube(mb, np.array([[sx * 0.3, 1.25, h + 0.12], [sx * 0.3, 1.0, h + 0.1], [sx * 0.42, 0.9, h + 0.1]]),
                        0.02, 5, gilt)
        kc.rounded_block(mb, (0.0, 4.3, h + 0.15), (VEST_DOOR_HALF + 0.05, 0.12, 0.2), red, radius=0.02, seg=1)
        kc.rounded_block(mb, (0.0, (VEST_H + 4.42) * 0.5, h + 0.25), (VEST_DOOR_HALF, (VEST_H - 4.42) * 0.5, 0.25), stone,
                         radius=0.02, seg=1, weather=MARBLE_W)
        # The nave's south end wall (z -6 from here), the doorway through it, and its lintel's Level line.
        dw, dh = NAVE_DOOR
        wz = -h - 0.25
        for sx in (-1.0, 1.0):
            w = (NAVE_HALF_W + 0.8 - dw) * 0.5
            kc.rounded_block(mb, (sx * (dw + w), NAVE_CROWN * 0.5, wz), (w, NAVE_CROWN * 0.5, 0.25), stone, radius=0.02,
                             seg=1, weather=MARBLE_W, variation=float(rng.random()))
        kc.rounded_block(mb, (0.0, (NAVE_CROWN + dh) * 0.5, wz), (dw, (NAVE_CROWN - dh) * 0.5, 0.25), stone,
                         radius=0.02, seg=1, weather=MARBLE_W)
        kc.rounded_block(mb, (0.0, dh + 0.15, wz - 0.3), (dw + 0.4, 0.15, 0.06), stone, radius=0.02, seg=1,
                         weather=MARBLE_W)  # the lintel's face on the nave side
        kc.rounded_block(mb, (0.0, dh + 0.15, wz - 0.37), (dw + 0.2, 0.012, 0.01), gilt, radius=0.004, seg=1)
        out.append(mb)
    return out


def build_sanctum_bench(seed: int = 2125) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("sanctum_bench", seed)
        mb = kc.MeshBuilder("sanctum_bench" + ("-lod1" if lod else ""))
        stone = mb.material(M_STONE)
        kc.rounded_block(mb, (0.0, 0.41, 0.0), (0.26, 0.05, 1.2), stone, radius=0.03, seg=1 if lod else 2,
                         weather=MARBLE_W, variation=float(rng.random()))
        for z in (-0.9, 0.9):
            kc.rounded_block(mb, (0.0, 0.18, z), (0.2, 0.18, 0.12), stone, radius=0.02, seg=1, weather=MARBLE_W)
        out.append(mb)
    return out


def build_sanctum_apse(seed: int = 2126) -> list[kc.MeshBuilder]:
    out = []
    r, spring = APSE
    for lod in (False, True):
        rng = kc.rng_for("sanctum_apse", seed)
        mb = kc.MeshBuilder("sanctum_apse" + ("-lod1" if lod else ""))
        stone, gilt = mb.material(M_STONE), mb.material(M_GILT)
        # The end wall either side of the arch and over it.
        for sx in (-1.0, 1.0):
            w = (NAVE_HALF_W + 0.8 - r) * 0.5
            kc.rounded_block(mb, (sx * (r + w), NAVE_CROWN * 0.5, 0.25), (w, NAVE_CROWN * 0.5, 0.25), stone, radius=0.02,
                             seg=1, weather=MARBLE_W, variation=float(rng.random()))
        kc.rounded_block(mb, (0.0, (NAVE_CROWN + spring + r) * 0.5, 0.25), (r, (NAVE_CROWN - spring - r) * 0.5, 0.25),
                         stone, radius=0.02, seg=1, weather=MARBLE_W)
        # The arch's spandrels: the wall between the round arch and its square frame, one smooth face (the round edge
        # to the square), skinned behind; and the jambs under the spring.
        n_sp = 8 if lod else 24
        a = np.linspace(0.0, math.pi, n_sp)
        rim = np.stack([r * np.cos(a), spring + r * np.sin(a), np.zeros(n_sp)], -1)
        sq = np.stack([np.clip(np.cos(a) * 2.0 * r, -r, r), spring + np.clip(np.sin(a) * 2.0 * r, 0.0, r),
                       np.zeros(n_sp)], -1)
        _shell(mb, np.stack([rim, sq]), stone, (0.0, spring, -200.0), skin_m=0.5)
        # The recess: a raised step, a half-cylinder wall to the spring, and the half-dome over it.
        kc.rounded_block(mb, (0.0, APSE_STEP * 0.5, r * 0.5), (r, APSE_STEP * 0.5, r * 0.5 + 0.01), stone,
                         radius=0.03, seg=1, weather=MARBLE_W)
        cols = 8 if lod else 24
        th = np.linspace(0.0, math.pi, cols)
        wall = np.array([[[r * math.cos(a), y, r * math.sin(a)] for a in th] for y in (APSE_STEP, spring)])
        _shell(mb, wall, stone, (0.0, 2.0, 0.0))
        ph = np.linspace(0.0, math.pi * 0.5, 4 if lod else 10)
        dome = np.array([[[r * math.cos(b) * math.cos(a), spring + r * math.sin(b), r * math.cos(b) * math.sin(a)]
                          for a in th] for b in ph])
        _shell(mb, dome, stone, (0.0, spring - 2.0, 0.0))
        if not lod:  # the Level line round the recess at eye height over the step
            ring = np.array([[(r - 0.02) * math.cos(a), APSE_STEP + EYE_H, (r - 0.02) * math.sin(a)] for a in th])
            kc.tube(mb, ring, 0.025, 4, gilt)
            arch = np.array([[r * math.cos(a), spring + r * math.sin(a), -0.02] for a in np.linspace(0, math.pi, 24)])
            kc.tube(mb, arch, 0.05, 4, gilt)
        out.append(mb)
    return out


def build_cantor_stand(seed: int = 2127) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("cantor_stand", seed)
        mb = kc.MeshBuilder("cantor_stand" + ("-lod1" if lod else ""))
        stone, gilt = mb.material(M_STONE), mb.material(M_GILT)
        kc.rounded_block(mb, (0.0, 0.06, 0.0), (0.3, 0.06, 0.3), stone, radius=0.02, seg=1, weather=MARBLE_W)
        _revolve(mb, np.array([0.12, 0.2, 0.9, 1.0]), np.array([0.14, 0.1, 0.08, 0.12]), 6 if lod else 12, M_STONE)
        kc.rounded_block(mb, (0.0, 1.06, 0.0), (0.26, 0.03, 0.2), stone, rot=kc.rot_x(-0.35), radius=0.01, seg=1,
                         weather=MARBLE_W, variation=float(rng.random()))
        if not lod:
            kc.rounded_block(mb, (0.0, 1.1, -0.17), (0.27, 0.012, 0.012), gilt, rot=kc.rot_x(-0.35), radius=0.004,
                             seg=1)
        out.append(mb)
    return out


# --- the Lamp Archive's reading room (M4-A2P-043) -------------------------------------------------------------------
CASE = (2.5, 6.0, 0.5)  # half length (x), height, half depth (z): the greybox's Stack blocks
SHELVES = 6
HALL_HALF_W = 9.75
HALL_BAY = 6.4
HALL_LEN = 32.0
CLERESTORY = (6.6, 8.4)  # the windows' sill and head
HALL_SPRING = 9.2
HALL_CROWN = 12.5
HALL_DOOR_HALF = 2.2
TABLE = (1.0, 0.9, 2.0)  # half width, height, half length
PAPER_W = kc.Weathering(moss=0.0, salt=0.0, wet=0.0, erosion=0.04, noise_scale_m=0.5)  # indoors: dry, barely worn


def _ledger_run(mb, x0: float, x1: float, y: float, z: float, face: float, h: float, rng, paper: int, red: int) -> None:
    """Ledgers standing on a shelf from x0 to x1, their spines toward `face` (+-1 in z), in runs of a few volumes."""
    x = x0
    while x < x1 - 0.05:
        w = min(x1 - x, 0.25 + 0.5 * float(rng.random()))
        hh = h * (0.7 + 0.3 * float(rng.random()))
        mat = red if rng.random() < 0.35 else paper
        kc.rounded_block(mb, (x + w * 0.5, y + hh * 0.5, z), (w * 0.5 - 0.01, hh * 0.5, 0.15), mat, radius=0.01, seg=1,
                         weather=PAPER_W, variation=float(rng.random()))
        x += w


def build_archive_case(seed: int = 2131) -> list[kc.MeshBuilder]:
    out = []
    hx, height, hz = CASE
    for lod in (False, True):
        rng = kc.rng_for("archive_case", seed)
        mb = kc.MeshBuilder("archive_case" + ("-lod1" if lod else ""))
        black, red, gilt, paper = (mb.material(M_BLACK), mb.material(M_LACQUER), mb.material(M_GILT),
                                   mb.material(M_PAPER))
        kc.rounded_block(mb, (0.0, height * 0.5, 0.0), (hx, height * 0.5, 0.06), black, radius=0.02, seg=1)  # the spine
        for sx in (-1.0, 1.0):  # the ends
            kc.rounded_block(mb, (sx * (hx - 0.06), height * 0.5, 0.0), (0.06, height * 0.5, hz), black, radius=0.02,
                             seg=1)
        kc.rounded_block(mb, (0.0, height - 0.06, 0.0), (hx, 0.06, hz), black, radius=0.02, seg=1)
        kc.rounded_block(mb, (0.0, 0.08, 0.0), (hx, 0.08, hz), black, radius=0.02, seg=1)
        pitch = (height - 0.3) / SHELVES
        for k in range(SHELVES):
            y = 0.16 + pitch * k
            if k:
                kc.rounded_block(mb, (0.0, y, 0.0), (hx - 0.12, 0.025, hz - 0.02), red, radius=0.01, seg=1)
            if lod:
                for face in (-1.0, 1.0):
                    kc.rounded_block(mb, (0.0, y + pitch * 0.4, face * (hz - 0.2)), (hx - 0.14, pitch * 0.38, 0.15),
                                     paper, radius=0.01, seg=1, weather=PAPER_W)
                continue
            for face in (-1.0, 1.0):
                _ledger_run(mb, -hx + 0.14, hx - 0.14, y + 0.025, face * (hz - 0.2), face, pitch * 0.85, rng, paper, red)
        if not lod:
            for face in (-1.0, 1.0):
                kc.tube(mb, np.array([[-hx, height - 0.12, face * (hz + 0.005)], [hx, height - 0.12, face * (hz + 0.005)]]),
                        0.015, 4, gilt)
        out.append(mb)
    return out


def build_archive_hall_bay(seed: int = 2132) -> list[kc.MeshBuilder]:
    out = []
    hb = HALL_BAY * 0.5
    sill, head = CLERESTORY
    for lod in (False, True):
        rng = kc.rng_for("archive_hall_bay", seed)
        mb = kc.MeshBuilder("archive_hall_bay" + ("-lod1" if lod else ""))
        stone, gilt, bronze = mb.material(M_STONE), mb.material(M_GILT), mb.material(M_BRONZE)
        if lod:
            kc.rounded_block(mb, (0.0, -0.15, 0.0), (HALL_HALF_W, 0.15, hb), stone, radius=0.01, seg=1, weather=MARBLE_W)
        else:
            _paving(mb, rng, HALL_HALF_W, hb, 1.6, stone, bed=True)
        for sx in (-1.0, 1.0):
            wx = sx * (HALL_HALF_W + 0.4)
            kc.rounded_block(mb, (wx, sill * 0.5, 0.0), (0.4, sill * 0.5, hb), stone, radius=0.02, seg=1,
                             weather=MARBLE_W, variation=float(rng.random()))
            top = HALL_SPRING + WALL_OVERLAP_M
            kc.rounded_block(mb, (wx, (head + top) * 0.5, 0.0), (0.4, (top - head) * 0.5, hb), stone, radius=0.02, seg=1,
                             weather=MARBLE_W)
            for z in (-hb, hb):  # the piers between the windows (half of one at each end)
                kc.rounded_block(mb, (wx, (sill + head) * 0.5, z * 0.94), (0.4, (head - sill) * 0.5, 0.4 * 0.5 + 0.01),
                                 stone, radius=0.02, seg=1, weather=MARBLE_W)
            if not lod:  # the window's bronze mullions, and the Level line on the sill
                for zm in np.linspace(-hb + 1.6, hb - 1.6, 3):
                    kc.tube(mb, np.array([[wx, sill, zm], [wx, head, zm]]), 0.05, 4, bronze)
                kc.tube(mb, np.array([[sx * (HALL_HALF_W - 0.01), sill - 0.15, -hb], [sx * (HALL_HALF_W - 0.01), sill - 0.15,
                                                                                       hb]]), 0.02, 4, gilt)
        rise = HALL_CROWN - HALL_SPRING
        r = (HALL_HALF_W ** 2 + rise ** 2) / (2 * rise)
        cy = HALL_CROWN - r
        half_a = math.asin(HALL_HALF_W / r)
        a = np.linspace(-half_a, half_a, 6 if lod else 16)
        arc = np.stack([r * np.sin(a), cy + r * np.cos(a)], -1)
        _shell(mb, np.array([[[x, y, z] for x, y in arc] for z in (-hb, hb)]), stone, (0.0, 2.0, 0.0))
        out.append(mb)
    return out


def build_archive_end_walls(seed: int = 2133) -> list[kc.MeshBuilder]:
    out = []
    w = HALL_HALF_W + 0.8
    top = HALL_CROWN + SHELL_SKIN_M
    for lod in (False, True):
        rng = kc.rng_for("archive_end_walls", seed)
        mb = kc.MeshBuilder("archive_end_walls" + ("-lod1" if lod else ""))
        stone, red, black, gilt = (mb.material(M_STONE), mb.material(M_LACQUER), mb.material(M_BLACK),
                                   mb.material(M_GILT))
        kc.rounded_block(mb, (0.0, top * 0.5, -HALL_LEN - 0.25), (w, top * 0.5, 0.25), stone, radius=0.02, seg=1,
                         weather=MARBLE_W)
        d = HALL_DOOR_HALF
        for sx in (-1.0, 1.0):
            kc.rounded_block(mb, (sx * (d + (w - d) * 0.5), top * 0.5, 0.25), ((w - d) * 0.5, top * 0.5, 0.25), stone,
                             radius=0.02, seg=1, weather=MARBLE_W, variation=float(rng.random()))
            kc.rounded_block(mb, (sx * (d - 0.1), 2.1, 0.1), (0.12, 2.1, 0.18), red, radius=0.02, seg=1)
            kc.rounded_block(mb, (sx * (d * 0.5 - 0.05), 2.0, 0.05), (d * 0.5 - 0.1, 2.0, 0.06), black, radius=0.015, seg=1)
            if not lod:
                kc.tube(mb, np.array([[sx * 0.3, 1.25, -0.02], [sx * 0.3, 1.0, -0.04], [sx * 0.42, 0.9, -0.04]]), 0.02, 5,
                        gilt)
        kc.rounded_block(mb, (0.0, 4.3, 0.1), (d + 0.05, 0.12, 0.2), red, radius=0.02, seg=1)
        kc.rounded_block(mb, (0.0, (top + 4.42) * 0.5, 0.25), (d, (top - 4.42) * 0.5, 0.25), stone, radius=0.02, seg=1,
                         weather=MARBLE_W)
        if not lod:
            kc.rounded_block(mb, (0.0, 4.75, -0.01), (d + 0.6, 0.012, 0.01), gilt, radius=0.004, seg=1)
        out.append(mb)
    return out


def _table(mb, lod: bool) -> None:
    hw, h, hl = TABLE
    black = mb.material(M_BLACK)
    kc.rounded_block(mb, (0.0, h - 0.04, 0.0), (hw, 0.04, hl), black, radius=0.015, seg=1)
    for sx in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            kc.rounded_block(mb, (sx * (hw - 0.1), (h - 0.08) * 0.5, sz * (hl - 0.1)), (0.05, (h - 0.08) * 0.5, 0.05),
                             black, radius=0.01, seg=1)
    if not lod:
        kc.rounded_block(mb, (0.0, 0.25, 0.0), (0.03, 0.03, hl - 0.15), black, radius=0.01, seg=1)  # the stretcher


def build_reading_table(seed: int = 2134) -> list[kc.MeshBuilder]:
    out = []
    hw, h, hl = TABLE
    for lod in (False, True):
        rng = kc.rng_for("reading_table", seed)
        mb = kc.MeshBuilder("reading_table" + ("-lod1" if lod else ""))
        paper, red, bronze = mb.material(M_PAPER), mb.material(M_LACQUER), mb.material(M_BRONZE)
        _table(mb, lod)
        for k, z in enumerate(np.linspace(-hl + 0.6, hl - 0.6, 2 if lod else 4)):  # ledgers open side by side
            yaw = 0.15 * (float(rng.random()) - 0.5)
            for side in (-1.0, 1.0):
                kc.rounded_block(mb, (side * 0.22, h + 0.015, z), (0.21, 0.015, 0.3), paper, rot=kc.rot_y(yaw) @
                                 kc.rot_z(side * 0.06), radius=0.005, seg=1, weather=PAPER_W, variation=float(rng.random()))
            kc.rounded_block(mb, (0.0, h + 0.005, z), (0.03, 0.01, 0.31), red, radius=0.004, seg=1)
        if not lod:  # the reading weight on a page, and the unlit oil lamp at the table's head
            kc.rounded_block(mb, (0.25, h + 0.05, -hl + 0.6), (0.06, 0.02, 0.12), bronze, radius=0.01, seg=1)
            _revolve_at(mb, -0.6, hl - 0.3, h + np.array([0.0, 0.03, 0.08, 0.1, 0.14]),
                        np.array([0.06, 0.08, 0.06, 0.02, 0.0]), 10, M_BRONZE)
        out.append(mb)
    return out


def build_roll_table(seed: int = 2135) -> list[kc.MeshBuilder]:
    out = []
    hw, h, hl = TABLE
    for lod in (False, True):
        rng = kc.rng_for("roll_table", seed)
        mb = kc.MeshBuilder("roll_table" + ("-lod1" if lod else ""))
        paper, red, gilt = mb.material(M_PAPER), mb.material(M_LACQUER), mb.material(M_GILT)
        _table(mb, lod)
        kc.rounded_block(mb, (0.0, h + 0.005, 0.0), (0.32, 0.005, hl - 0.35), paper, radius=0.003, seg=1,
                         weather=PAPER_W, variation=float(rng.random()))  # the Cantor roll, unrolled
        for sz in (-1.0, 1.0):  # its rollers, red with gilt ends, the rolled paper round them
            z = sz * (hl - 0.25)
            kc.tube(mb, np.array([[-0.42, h + 0.07, z], [0.42, h + 0.07, z]]), 0.035, 6 if lod else 10, red, cap_end=True,
                    cap_start=True)
            kc.tube(mb, np.array([[-0.33, h + 0.07, z], [0.33, h + 0.07, z]]), 0.06, 6 if lod else 12, paper, cap_end=True,
                    cap_start=True, weather=PAPER_W)
            if not lod:
                for sx in (-1.0, 1.0):
                    kc.tube(mb, np.array([[sx * 0.42, h + 0.07, z], [sx * 0.47, h + 0.07, z]]), 0.045, 8, gilt,
                            cap_end=True, cap_start=True)
        out.append(mb)
    return out


def build_ledger_stack(seed: int = 2136) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("ledger_stack", seed)
        mb = kc.MeshBuilder("ledger_stack" + ("-lod1" if lod else ""))
        paper, red = mb.material(M_PAPER), mb.material(M_LACQUER)
        y = 0.0
        for k in range(3 if lod else 9):
            th = 0.04 + 0.03 * float(rng.random())
            kc.rounded_block(mb, (0.03 * float(rng.random()), y + th * 0.5, 0.03 * float(rng.random())),
                             (0.2, th * 0.5, 0.28), red if k % 3 == 1 else paper, rot=kc.rot_y(0.3 * float(rng.random())),
                             radius=0.006, seg=1, weather=PAPER_W, variation=float(rng.random()))
            y += th
        if not lod:  # two rolled lists against the pile
            for k in range(2):
                kc.tube(mb, np.array([[0.3, 0.05, -0.2 + 0.25 * k], [0.32, 0.05, 0.25 + 0.25 * k]]), 0.05, 8, paper,
                        cap_end=True, cap_start=True, weather=PAPER_W)
        out.append(mb)
    return out


# --- the Lacquer Court at the wedding (M4-A2P-044) ---------------------------------------------------------------
COURT_Z = (0.0, -24.0)  # the court's south (water-steps) and north edges
COURT_HALF_X = 15.0
COURT_WATER_Y = -1.0
COURT_BARGE_DECK = -0.6
# The greybox's edge walls (centre x, centre z, length along x, length along z), 1 m high and 0.5 m thick.
COURT_WALLS = ((0.0, -24.0, 30.0, 0.0), (-9.1, 0.0, 11.8, 0.0), (9.1, 0.0, 11.8, 0.0), (-15.0, -12.0, 0.0, 24.0),
               (15.0, -14.0, 0.0, 20.0), (15.0, -0.5, 0.0, 1.0))
STEPS_HALF_W = 3.0  # between the water-steps' walls (the greybox's, at +-3.25)
STEPS_LEN = 4.0
TERRACE = (27.0, -40.0)  # the terrace's half width and its north edge, round the court for the halls
COLUMN_H = 6.0
GALLERY = (1.5, 0.6, 8.0)  # half width, height, half length
DAIS = (4.0, 0.8, 1.5)
CONCLAVE = (2.5, 2.0, 1.5)
COURT_GATE = (5.0, 18.0)  # the posts' half spacing and the gate's z
FLAME_Y = 1.75  # gilt_lamp_stand's flame over its foot


def build_court_ground_zone(seed: int = 2141) -> list[kc.MeshBuilder]:
    out = []
    z0, z1 = COURT_Z
    hx = COURT_HALF_X
    tx, tz = TERRACE
    for lod in (False, True):
        rng = kc.rng_for("court_ground", seed)
        mb = kc.MeshBuilder("court_ground" + ("-lod1" if lod else ""))
        stone, gilt = mb.material(M_STONE), mb.material(M_GILT)
        cz = (z0 + z1) * 0.5
        hz = (z0 - z1) * 0.5
        if lod:
            kc.rounded_block(mb, (0.0, -0.15, cz), (hx, 0.15, hz), stone, radius=0.01, seg=1, weather=MARBLE_W)
        else:
            nx, nz = 12, 10
            kc.rounded_block(mb, (0.0, -0.25, cz), (hx, 0.2, hz), stone, radius=0.01, seg=1, weather=MARBLE_W)
            for i in range(nx):
                for k in range(nz):
                    w, d = 2 * hx / nx, 2 * hz / nz
                    kc.rounded_block(mb, (-hx + w * (i + 0.5), -0.03, z1 + d * (k + 0.5)), (w * 0.5 - 0.008, 0.03,
                                     d * 0.5 - 0.008), stone, radius=0.006, seg=1, weather=MARBLE_W,
                                     variation=float(rng.random()))
            kc.rounded_block(mb, (0.0, 0.002, cz), (0.05, 0.003, hz - 0.8), gilt, radius=0.002, seg=1)  # the Level line
        # The terrace round the court (N, W, E; the court's south edge is the water): a marble platform to the bed.
        th = (0.0 - (COURT_WATER_Y - 1.2)) * 0.5
        for (cx_, cz_, sx_, sz_) in ((0.0, (z1 + tz) * 0.5, tx, (z1 - tz) * 0.5),
                                     (-(hx + tx) * 0.5, z0 * 0.5 + z1 * 0.5, (tx - hx) * 0.5, hz),
                                     ((hx + tx) * 0.5, z0 * 0.5 + z1 * 0.5, (tx - hx) * 0.5, hz)):
            kc.rounded_block(mb, (cx_, -th, cz_), (sx_, th, sz_), stone, radius=0.04, seg=1, weather=MARBLE_W,
                             variation=float(rng.random()))
        # The court's own south face down into the lagoon, either side of the water-steps.
        for sx in (-1.0, 1.0):
            w = (hx - STEPS_HALF_W) * 0.5
            kc.rounded_block(mb, (sx * (STEPS_HALF_W + w), -th, z0 + 0.25), (w, th, 0.25), stone, radius=0.03, seg=1,
                             weather=kc.Weathering(moss=0.0, salt=0.2, wet=0.25, erosion=0.1), wet_bias=0.2)
        out.append(mb)
    return out


def build_court_balustrades(seed: int = 2142) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("court_balustrades", seed)
        mb = kc.MeshBuilder("court_balustrades" + ("-lod1" if lod else ""))
        stone, gilt = mb.material(M_STONE), mb.material(M_GILT)
        runs = [(cx, cz, lx, lz, 0.0, 1.0) for cx, cz, lx, lz in COURT_WALLS]
        runs += [(sx * (STEPS_HALF_W + 0.25), STEPS_LEN * 0.5, 0.0, STEPS_LEN, -0.5, 1.5) for sx in (-1.0, 1.0)]
        for cx, cz, lx, lz, y0, y1 in runs:
            hx_, hz_ = max(lx, 0.5) * 0.5, max(lz, 0.5) * 0.5
            kc.rounded_block(mb, (cx, (y0 + y1) * 0.5 - 0.06, cz), (hx_, (y1 - y0) * 0.5 - 0.06, hz_), stone, radius=0.03,
                             seg=1, weather=MARBLE_W, variation=float(rng.random()))
            kc.rounded_block(mb, (cx, y1 - 0.06, cz), (hx_ + 0.05, 0.06, hz_ + 0.05), stone, radius=0.03, seg=1,
                             weather=MARBLE_W)  # the coping
            if not lod:
                along = np.array([lx * 0.5, 0.0, lz * 0.5])
                for side in (-1.0, 1.0):
                    off = np.array([0.0 if lx else side * (hx_ + 0.055), 0.0, side * (hz_ + 0.055) if lx else 0.0])
                    c = np.array([cx, y1 - 0.08, cz]) + off
                    kc.tube(mb, np.array([c - along, c + along]), 0.012, 4, gilt)
        out.append(mb)
    return out


def build_court_water_steps(seed: int = 2143) -> list[kc.MeshBuilder]:
    out = []
    n = 6
    for lod in (False, True):
        rng = kc.rng_for("court_water_steps", seed)
        mb = kc.MeshBuilder("court_water_steps" + ("-lod1" if lod else ""))
        stone = mb.material(M_STONE)
        for k in range(n):
            top = COURT_BARGE_DECK * (k + 1) / n
            tread = STEPS_LEN / n
            hy = (top - (COURT_WATER_Y - 1.0)) * 0.5
            kc.rounded_block(mb, (0.0, top - hy, tread * (k + 0.5)), (STEPS_HALF_W, hy, tread * 0.5), stone, radius=0.02,
                             seg=1, weather=kc.Weathering(moss=0.0, salt=0.2, wet=0.3, erosion=0.1),
                             wet_bias=0.08 * k, variation=float(rng.random()))
        out.append(mb)
    return out


def build_court_colonnade_roofs(seed: int = 2144) -> list[kc.MeshBuilder]:
    """Over the N row (x -14..14 at z -23) and the W and E rows (z -21..-3 at x +-14): a lacquered beam on the
    columns' capitals, and a lean-to of tile from it out over the court's edge wall."""
    out = []
    rows = (((-14.0, -23.0), (14.0, -23.0), (0.0, -1.0)), ((-14.0, -21.0), (-14.0, -3.0), (-1.0, 0.0)),
            ((14.0, -21.0), (14.0, -3.0), (1.0, 0.0)))
    for lod in (False, True):
        rng = kc.rng_for("court_colonnade_roofs", seed)
        mb = kc.MeshBuilder("court_colonnade_roofs" + ("-lod1" if lod else ""))
        red, gilt, tile = mb.material(M_LACQUER), mb.material(M_GILT), mb.material(M_TILE)
        for (ax, az), (bx, bz), (ox, oz) in rows:
            a = np.array([ax - abs(oz) * 0.6, COLUMN_H + 0.2, az - abs(ox) * 0.6])
            b = np.array([bx + abs(oz) * 0.6, COLUMN_H + 0.2, bz + abs(ox) * 0.6])
            mid = (a + b) * 0.5
            half = np.abs(b - a) * 0.5 + np.array([0.15, 0.2, 0.15])
            kc.rounded_block(mb, mid, (max(half[0], 0.2), 0.2, max(half[2], 0.2)), red, radius=0.03, seg=1)
            if not lod:
                kc.rounded_block(mb, mid + np.array([0.0, -0.22, 0.0]), (max(half[0], 0.22), 0.02, max(half[2], 0.22)), gilt,
                                 radius=0.01, seg=1)
            out_v = np.array([ox, 0.0, oz])
            lo_edge = 2.8  # the roof's fall over the edge wall, outward
            hi_a, hi_b = a + np.array([0.0, 0.5, 0.0]) - out_v * 0.8, b + np.array([0.0, 0.5, 0.0]) - out_v * 0.8
            lo_a, lo_b = a + out_v * lo_edge + np.array([0.0, -0.5, 0.0]), b + out_v * lo_edge + np.array([0.0, -0.5, 0.0])
            grid = np.array([[hi_a, hi_b], [lo_a, lo_b]])
            L = float(np.linalg.norm(b - a))
            for flip in (False, True):
                kc.quad_strip(mb, grid, tile, uv=np.array([[[0, 0], [L / 2, 0]], [[0, 1.6], [L / 2, 1.6]]]),
                              col=(0, 0, 0, 0.4), uv2=(0.8, 0.5), flip=flip, smooth=False)
            if not lod:  # the gilt ridge along the roof's top and the eave
                kc.tube(mb, np.array([hi_a, hi_b]), 0.06, 5, gilt)
                kc.tube(mb, np.array([lo_a, lo_b]), 0.05, 5, gilt)
        del rng
        out.append(mb)
    return out


def build_court_water_gate(seed: int = 2145) -> list[kc.MeshBuilder]:
    out = []
    gx, gz = COURT_GATE
    for lod in (False, True):
        rng = kc.rng_for("court_water_gate", seed)
        mb = kc.MeshBuilder("court_water_gate" + ("-lod1" if lod else ""))
        red, gilt = mb.material(M_LACQUER), mb.material(M_GILT)
        for sx in (-1.0, 1.0):
            kc.tube(mb, np.array([[sx * gx, COURT_WATER_Y - 1.2, gz], [sx * gx, 6.0, gz]]), 0.35, 6 if lod else 12, red,
                    cap_end=True)
            kc.rounded_block(mb, (sx * gx, 6.15, gz), (0.5, 0.15, 0.5), gilt, radius=0.05, seg=1)
        kc.rounded_block(mb, (0.0, 6.4, gz), (gx + 0.5, 0.25, 0.3), red, radius=0.05, seg=1)
        kc.rounded_block(mb, (0.0, 4.6, gz), (gx - 0.4, 1.3, 0.12), red, radius=0.03, seg=1)  # the raised drop-gate
        if not lod:
            kc.tube(mb, np.array([[-gx + 0.4, 3.35, gz + 0.13], [gx - 0.4, 3.35, gz + 0.13]]), 0.05, 6, gilt)
            for sx in (-1.0, 1.0):
                kc.tube(mb, np.array([[sx * (gx + 0.5), 6.4, gz], [sx * (gx + 1.1), 6.95, gz]]), np.array([0.12, 0.03]), 5,
                        gilt)
        del rng
        out.append(mb)
    return out


def build_court_column(seed: int = 2146) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("court_column", seed)
        mb = kc.MeshBuilder("court_column" + ("-lod1" if lod else ""))
        stone, red = mb.material(M_STONE), mb.material(M_LACQUER)
        kc.rounded_block(mb, (0.0, 0.12, 0.0), (0.36, 0.12, 0.36), stone, radius=0.03, seg=1, weather=MARBLE_W)
        kc.tube(mb, np.array([[0.0, 0.24, 0.0], [0.0, COLUMN_H - 0.35, 0.0]]), np.array([0.26, 0.23]), 8 if lod else 16,
                red, cap_end=True)
        _revolve(mb, np.array([COLUMN_H - 0.4, COLUMN_H - 0.3, COLUMN_H - 0.1, COLUMN_H]),
                 np.array([0.24, 0.3, 0.36, 0.36]), 8 if lod else 16, M_GILT, cap=True)
        if not lod:
            _revolve(mb, np.array([0.24, 0.3, 0.36]), np.array([0.29, 0.3, 0.27]), 16, M_GILT)
        del rng
        out.append(mb)
    return out


def build_court_gallery(seed: int = 2147) -> list[kc.MeshBuilder]:
    out = []
    hw, h, hl = GALLERY
    for lod in (False, True):
        rng = kc.rng_for("court_gallery", seed)
        mb = kc.MeshBuilder("court_gallery" + ("-lod1" if lod else ""))
        stone, red, gilt = mb.material(M_STONE), mb.material(M_LACQUER), mb.material(M_GILT)
        kc.rounded_block(mb, (0.0, h * 0.5, 0.0), (hw, h * 0.5, hl), stone, radius=0.04, seg=1 if lod else 2,
                         weather=MARBLE_W)
        if not lod:
            for sx in (-1.0, 1.0):
                kc.tube(mb, np.array([[sx * (hw + 0.01), h - 0.06, -hl], [sx * (hw + 0.01), h - 0.06, hl]]), 0.015, 4,
                        gilt)
        for z in np.arange(-hl + 1.0, hl - 0.5, 2.5 if lod else 1.6):  # the guests' benches, facing the court
            kc.rounded_block(mb, (0.0, h + 0.42, z), (0.22, 0.04, 0.6), red, radius=0.015, seg=1)
            for dz in (-0.45, 0.45):
                kc.rounded_block(mb, (0.0, h + 0.19, z + dz), (0.18, 0.19, 0.04), red, radius=0.01, seg=1)
        del rng
        out.append(mb)
    return out


def build_wedding_dais(seed: int = 2148) -> list[kc.MeshBuilder]:
    out = []
    hx, h, hz = DAIS
    for lod in (False, True):
        rng = kc.rng_for("wedding_dais", seed)
        mb = kc.MeshBuilder("wedding_dais" + ("-lod1" if lod else ""))
        stone, gilt, red, paper = (mb.material(M_STONE), mb.material(M_GILT), mb.material(M_CLOTH_RED),
                                   mb.material(M_PAPER))
        for k in range(3):  # three marble steps, the top one the dais
            g = 0.3 * (2 - k)
            kc.rounded_block(mb, (0.0, h * (k + 1) / 3 * 0.5, g * 0.5), (hx + g, h * (k + 1) / 3 * 0.5, hz + g * 0.5),
                             stone, radius=0.03, seg=1, weather=MARBLE_W, variation=float(rng.random()))
        kc.rounded_block(mb, (0.0, h + 0.008, 0.0), (1.0, 0.008, hz - 0.1), red, radius=0.004, seg=1)  # the carpet
        kc.rounded_block(mb, (0.0, h * 0.5, hz + 0.6), (1.0, 0.008, 0.6), red, rot=kc.rot_x(-0.95), radius=0.004,
                         seg=1)  # down the steps
        for sx in (-1.0, 1.0):  # two gilt standards, their red streamers hanging dead still
            x = sx * (hx - 0.5)
            kc.tube(mb, np.array([[x, h, -hz + 0.4], [x, h + 3.4, -hz + 0.4]]), 0.05, 6 if lod else 10, gilt,
                    cap_end=True)
            kc.tube(mb, np.array([[x - 0.5, h + 3.3, -hz + 0.4], [x + 0.5, h + 3.3, -hz + 0.4]]), 0.03, 6, gilt,
                    cap_end=True, cap_start=True)
            for dx in (-0.35, 0.0, 0.35):
                kc.rounded_block(mb, (x + dx, h + 2.5, -hz + 0.4), (0.09, 0.8 + 0.1 * dx, 0.006), red, radius=0.003,
                                 seg=1)
        if not lod:  # the offerings: bolts of cloth and sealed jars at the dais's back edge
            for k in range(4):
                kc.tube(mb, np.array([[-2.8 + 0.5 * k, h + 0.12, -hz + 0.35], [-2.8 + 0.5 * k, h + 0.12, -hz + 1.05]]),
                        0.12, 8, red if k % 2 else paper, cap_end=True, cap_start=True)
            for k in range(3):
                _revolve_at(mb, 1.6 + 0.55 * k, -hz + 0.6, h + np.array([0.0, 0.12, 0.32, 0.44, 0.5]),
                            np.array([0.1, 0.17, 0.15, 0.07, 0.08]), 12, M_JAR)
        out.append(mb)
    return out


def build_conclave_gallery(seed: int = 2149) -> list[kc.MeshBuilder]:
    out = []
    hx, h, hz = CONCLAVE
    for lod in (False, True):
        rng = kc.rng_for("conclave_gallery", seed)
        mb = kc.MeshBuilder("conclave_gallery" + ("-lod1" if lod else ""))
        stone, black, red, gilt = (mb.material(M_STONE), mb.material(M_BLACK), mb.material(M_LACQUER),
                                   mb.material(M_GILT))
        kc.rounded_block(mb, (0.0, h * 0.5, 0.0), (hx, h * 0.5, hz), stone, radius=0.04, seg=1, weather=MARBLE_W)
        kc.rounded_block(mb, (0.0, h + 1.2, -hz + 0.08), (hx, 1.2, 0.06), black, radius=0.02, seg=1)  # the back screen
        for sx in (-1.0, 1.0):
            kc.rounded_block(mb, (sx * (hx - 0.08), h + 1.2, -0.3), (0.06, 1.2, hz - 0.3), black, radius=0.02, seg=1)
        for k in range(5):  # the five seats
            x = -hx + 0.5 + k * (2 * hx - 1.0) / 4
            kc.rounded_block(mb, (x, h + 0.25, -hz + 0.6), (0.24, 0.25, 0.24), red, radius=0.02, seg=1)
            kc.rounded_block(mb, (x, h + 0.75, -hz + 0.38), (0.24, 0.3, 0.04), red, radius=0.02, seg=1)
        for sx in (-1.0, 1.0):  # the canopy: four gilt posts and a gilt-edged lacquer roof
            for z in (-hz + 0.1, hz - 0.1):
                kc.tube(mb, np.array([[sx * (hx - 0.1), h, z], [sx * (hx - 0.1), h + 2.8, z]]), 0.05, 6, gilt,
                        cap_end=True)
        kc.rounded_block(mb, (0.0, h + 2.9, 0.0), (hx + 0.2, 0.1, hz + 0.2), red, radius=0.03, seg=1)
        if not lod:
            kc.rounded_block(mb, (0.0, h + 2.78, 0.0), (hx + 0.22, 0.02, hz + 0.22), gilt, radius=0.01, seg=1)
        del rng
        out.append(mb)
    return out


def build_gilt_lamp_stand(seed: int = 2150) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("gilt_lamp_stand", seed)
        mb = kc.MeshBuilder("gilt_lamp_stand" + ("-lod1" if lod else ""))
        gilt = mb.material(M_GILT)
        for k in range(3):  # a tripod foot
            a = k * 2 * math.pi / 3
            kc.tube(mb, np.array([[0.32 * math.cos(a), 0.0, 0.32 * math.sin(a)], [0.0, 0.35, 0.0]]), 0.025, 4, gilt)
        kc.tube(mb, np.array([[0.0, 0.3, 0.0], [0.0, FLAME_Y - 0.15, 0.0]]), 0.03, 6 if lod else 8, gilt)
        _revolve(mb, FLAME_Y - np.array([0.2, 0.15, 0.05, 0.0]), np.array([0.03, 0.12, 0.17, 0.18]), 8 if lod else 14,
                 M_GILT)
        _revolve(mb, FLAME_Y + np.array([-0.04, 0.05, 0.18, 0.3]), np.array([0.09, 0.08, 0.04, 0.0]), 6 if lod else 10,
                 M_FLAME)
        del rng
        out.append(mb)
    return out


def build_stillguard_rack(seed: int = 2151) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("stillguard_rack", seed)
        mb = kc.MeshBuilder("stillguard_rack" + ("-lod1" if lod else ""))
        black, bronze, gilt = mb.material(M_BLACK), mb.material(M_BRONZE), mb.material(M_GILT)
        for dx in (-0.9, 0.9):
            kc.rounded_block(mb, (dx, 0.9, 0.0), (0.05, 0.9, 0.12), black, radius=0.01, seg=1)
        for y in (0.3, 1.5):
            kc.rounded_block(mb, (0.0, y, 0.0), (0.95, 0.04, 0.12), black, radius=0.01, seg=1)
        for k in range(3 if lod else 6):
            x = -0.7 + 1.4 * k / (2 if lod else 5)
            kc.tube(mb, np.array([[x, 0.05, 0.0], [x, 2.6, 0.05]]), 0.018, 4, black)
            if not lod:
                kc.tube(mb, np.array([[x, 2.6, 0.05], [x, 2.85, 0.055]]), np.array([0.04, 0.003]), 4, bronze)
                kc.tube(mb, np.array([[x, 2.55, 0.05], [x, 2.6, 0.05]]), 0.026, 6, gilt)
        del rng
        out.append(mb)
    return out


TARGETS = {
    "bowl_dome": build_bowl_dome,
    "ansedra_far_domes": build_far_domes,
    "ansedra_far_domes_lit": lambda: build_far_domes(lit=True),
    "pursuit_barge": build_pursuit_barge,
    "lacquer_hall": build_lacquer_hall,
    "lacquer_court_ground": build_court_ground,
    "sanctum_basin": build_sanctum_basin,
    "archive_stacks": build_archive_stacks,
    "ansedra_causeway_6m": build_causeway,
    "gold_lamp_post": build_lamp_post,
    "island_plinth_16m": build_island_plinth,
    "mooring_platform": build_mooring_platform,
    "sanctum_nave_bay": build_sanctum_nave_bay,
    "sanctum_nave_floor": build_sanctum_nave_floor,
    "sanctum_basin_nave": build_sanctum_basin_nave,
    "sanctum_vestibule": build_sanctum_vestibule,
    "sanctum_bench": build_sanctum_bench,
    "sanctum_apse": build_sanctum_apse,
    "cantor_stand": build_cantor_stand,
    "archive_case": build_archive_case,
    "archive_hall_bay": build_archive_hall_bay,
    "archive_end_walls": build_archive_end_walls,
    "reading_table": build_reading_table,
    "roll_table": build_roll_table,
    "ledger_stack": build_ledger_stack,
    "court_ground": build_court_ground_zone,
    "court_balustrades": build_court_balustrades,
    "court_water_steps": build_court_water_steps,
    "court_colonnade_roofs": build_court_colonnade_roofs,
    "court_water_gate": build_court_water_gate,
    "court_column": build_court_column,
    "court_gallery": build_court_gallery,
    "wedding_dais": build_wedding_dais,
    "conclave_gallery": build_conclave_gallery,
    "gilt_lamp_stand": build_gilt_lamp_stand,
    "stillguard_rack": build_stillguard_rack,
}
