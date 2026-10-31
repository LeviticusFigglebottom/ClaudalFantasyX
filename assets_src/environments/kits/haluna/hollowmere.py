"""Hollowmere, the Saltwright raft-city (hollowmere.md §1; M3-ENV-723): Ch17's zone pieces. Pure numpy.

Built in the Haluna kit (its import kind and materials), as lowlight.py, ossa_fen.py and ansedra.py. Every piece's
origin is on the water (y 0) unless it says otherwise.

  hm_lashed_hulls     a Hollowmere home: two old double-ended hulls (10 m) lashed side by side under one timber deck
                      (y 0.9), the near hull patched with Lit Age hull plating, a woven-panel deckhouse under thatch,
                      lashing bands round both hulls and the deck beams.
  hm_windmill         a Saltwright windmill on its own float: a four-legged timber mast (9 m), a six-armed rotor of
                      sand-cloth sails on a copper hub facing +Z, and a tail vane; origin at the float's waterline.
  hm_tide_wheel       a tide-wheel between two pontoons: a 3 m paddle wheel on an axle across Z, its frame, and the
                      copper gear housing carrying the Saltwright mark (lowlight.py's), facing +Z.
  hm_signal_lamp      a signal post (3.4 m) with a salt-glass lantern round a bound core: the teal light the
                      Saltwrights put back to work (bible §7). Origin at the post's foot (set it on a deck).
  dace_hull_frame     Dace's unfinished hull on the floating dry-dock (ch17): a pontoon deck (16 x 7 m, top y 0.6),
                      cradle blocks, the keel, stem and sternpost, thirteen ribs, five strakes planked on the near
                      (-Z) side only, staging poles and a walk-board, and his workbench. Nothing on it is finished.
                      Ch17 (M5-A3P-1500, env-art-b): he planked and decked the stern third to live aboard. Its hatch
                      drops to the cabin (his bunk, the ledger on a fold-down desk, the chart wall with Corrow
                      circled, the tool rack), and a doorway in the bulkhead opens on the engine bay's empty bed. The
                      keel wears a Lit Age brass shoe, and the mast stands with one kite wing half-rigged.
  hm_far_flotilla     the rest of the raft-city round the zone: low hull clusters and windmills at 220-460 m.

Ch15's first visit (M4-A2P-045, env-art-b; docs/kb/plan/act2/zones/ch15_hollowmere.md):
  hm_dock_4m          4 m of the floating timber walk along X: a plank deck (top y 0, 3.6 m wide) on two log pontoons
                      0.9 m under it, lashed, with a low rail of lashed poles each side. Origin at the deck's centre.
  hm_dock_4m_open_n, hm_dock_4m_open_s, hm_dock_4m_open_ns  the same without its -Z (north) rail, its +Z (south)
                      rail, or both, where a jetty or a gangway meets the walk.
  pyre_raft           Tobin's pyre-raft: a log raft (3 x 4 m) with a driftwood bier and a folded red cloth on it,
                      unlit (the cutscene lights it). Origin at the waterline.
  hm_ship             the Hollowmere ship that carries the party south: a twin-hulled Saltwright trader (16 m along X)
                      under one deck, Lit Age plating patches, two masts with furled sand-cloth sails. Origin at the
                      waterline.
  hm_supper_table     the side scene's supper on a deck: a low table, four stools, bowls and an oil lamp (lit by the
                      zone). Origin at its foot.
  hm_drydock_berth    an empty floating berth in Dace's row (Ch17, M5-A3P-1500): his dry-dock's pontoon (16 x 7 m,
                      top y 0.6), its cradle blocks waiting for a keel, a pair of shear-legs lashed at the head with
                      a block hanging, and a fender post at the outer (+X, +Z) corner. Origin at the waterline.
  hm_drydock_berth_first  the first berth, where Dace built his first hull (B07): the same, but its fender post's
                      top is worn pale where Tobin sat, an old rope coiled at its foot, and the rotted keel and rib
                      stubs of that first hull lie in the mud under the pontoon's open end.
  hm_dockmaster_house  Aldous Varrow's home (Ch17 B07, B11; HousePlatform1): hm_lashed_hulls with the deckhouse
                      furnished: his table and two benches, a lamp hook over it, a shelf of jars and a rolled chart,
                      a sleeping mat, a net hung on the wall. The table at TABLE_AT; the door as hm_lashed_hulls'.
  hm_oil_lamp         a hanging clay oil lamp on its bracket (the zone puts a real light at its flame). Origin at the
                      bracket's foot.
"""

from __future__ import annotations

import math

import numpy as np

import kit_common as kc
import lowlight

M_TIMBER = "kit_timber"
M_DRIFT = "kit_driftwood"
M_PLATE = "kit_iskarra_bronze"  # the Lit Age hull plating (Iskarran bronze)
M_LASH = "kit_lashing"
M_WOVEN = "kit_woven_panel"
M_THATCH = "kit_thatch"
M_SAIL = "kit_cloth_sand"
M_COPPER = lowlight.M_COPPER
M_GLASS = "kit_salt_glass"
M_CORE = "kit_bound_core"
M_TAR = "kit_interior_dark"

TRI_BUDGET = {"hm_lashed_hulls": (9000, 700), "hm_windmill": (5000, 400), "hm_tide_wheel": (6000, 450),
              "hm_signal_lamp": (1500, 150), "dace_hull_frame": (24000, 1600), "hm_far_flotilla": (9000, 2500),
              "hm_dock_4m": (2500, 200), "hm_dock_4m_open_n": (2500, 200), "hm_dock_4m_open_s": (2500, 200), "hm_dock_4m_open_ns": (2500, 200),
              "pyre_raft": (2500, 320), "hm_ship": (14000, 900), "hm_supper_table": (1500, 150),
              "hm_oil_lamp": (600, 80),
              "hm_drydock_berth": (5000, 400), "hm_dockmaster_house": (11000, 700), "hm_drydock_berth_first": (6500, 500)}

DECK_Y = 0.9
HULL_LEN = 10.0
HULL_HALF_BEAM = 1.3
HULL_GAP = 3.0  # the hulls' centre lines at z = +-HULL_GAP
DOCK_TOP = 0.6
FAR_RANGE = (220.0, 460.0)
WOOD = kc.Weathering(moss=0.05, salt=0.35, wet=0.3, erosion=0.25)


def hull_half_width(x, length: float, half_beam: float) -> np.ndarray:
    """A double-ended hull's half-width at station x (0 amidships): full beam, closing to a point at both ends."""
    u = np.clip(np.abs(np.asarray(x, float)) / (length * 0.5), 0.0, 1.0)
    return half_beam * np.sqrt(np.clip(1.0 - u ** 2.4, 0.0, 1.0))


def _hull(mb, cz: float, lod: bool, *, plated: bool, rng) -> None:
    """One old hull along X at z cz, its sheer at the deck's underside, its keel 1.1 m under the water."""
    wood, gilt = mb.material(M_DRIFT), mb.material(M_TAR)
    n = 9 if lod else 25
    xs = np.linspace(-HULL_LEN * 0.5, HULL_LEN * 0.5, n)
    hw = hull_half_width(xs, HULL_LEN, HULL_HALF_BEAM)
    prof = ((DECK_Y - 0.15, 1.0), (0.2, 0.95), (-0.6, 0.7), (-1.1, 0.0))
    for side in (-1.0, 1.0):
        grid = np.stack([np.stack([xs, np.full(n, y), cz + side * hw * f], -1) for y, f in prof], 1)
        kc.quad_strip(mb, grid, wood, uv=np.stack([grid[..., 0], grid[..., 1]], -1) / 2.0, col=(0, 0.15, 0.2, 0.5),
                      uv2=(0.8, 0.5), flip=side < 0)
    if not lod:  # the tarred waterline band, both sides
        for side in (-1.0, 1.0):
            band = np.stack([xs, np.full(n, 0.05), cz + side * (hull_half_width(xs, HULL_LEN, HULL_HALF_BEAM) * 0.955
                                                                 + 0.01)], -1)
            kc.tube(mb, band[1:-1], 0.035, 4, gilt)
    if plated:  # Lit Age plating riveted over the rot on the outer side, uneven panels
        plate = mb.material(M_PLATE)
        side = -1.0 if cz < 0 else 1.0
        for x in (np.linspace(-3.0, 2.5, 2) if lod else np.linspace(-3.4, 2.8, 5)):
            w = float(rng.uniform(0.5, 0.75))
            y = float(rng.uniform(-0.15, 0.25))
            z = cz + side * (hull_half_width(x, HULL_LEN, HULL_HALF_BEAM) * 0.96 + 0.02)
            kc.rounded_block(mb, (x, y, z), (w, 0.35, 0.02), plate, rot=kc.rot_x(side * 0.12), radius=0.01, seg=1,
                             weather=WOOD, variation=float(rng.random()))


def build_lashed_hulls(seed: int = 2301, name: str = "hm_lashed_hulls", furnished: bool = False) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
        timber, lash = mb.material(M_TIMBER), mb.material(M_LASH)
        _hull(mb, -HULL_GAP, lod, plated=True, rng=rng)
        _hull(mb, HULL_GAP, lod, plated=False, rng=rng)
        # The deck: cross beams over both hulls, planks along X on them.
        beams = np.linspace(-3.6, 3.6, 4 if lod else 7)
        for x in beams:
            kc.rounded_block(mb, (x, DECK_Y - 0.12, 0.0), (0.1, 0.08, HULL_GAP + 1.0), timber, radius=0.02, seg=1,
                             weather=WOOD)
        if lod:
            kc.rounded_block(mb, (0.0, DECK_Y - 0.02, 0.0), (3.9, 0.02, HULL_GAP + 1.1), timber, radius=0.01, seg=1)
        else:
            for z in np.arange(-HULL_GAP - 1.05, HULL_GAP + 1.06, 0.3):
                x0 = -3.9 + float(rng.uniform(-0.15, 0.15))
                x1 = 3.9 + float(rng.uniform(-0.15, 0.15))
                kc.plank(mb, (x0, DECK_Y - 0.02, z), (x1, DECK_Y - 0.02, z), 0.28, 0.04, timber, weather=WOOD,
                         variation=float(rng.random()))
            # The lashing: rope bands round each hull and its beam, at each beam.
            for x in beams[1:-1]:
                for cz in (-HULL_GAP, HULL_GAP):
                    hw = float(hull_half_width(x, HULL_LEN, HULL_HALF_BEAM))
                    a = np.linspace(0.0, math.pi, 9)
                    loop = np.stack([np.full_like(a, x + 0.14), DECK_Y - 0.2 - np.sin(a) * 0.5,
                                     cz + np.cos(a) * (hw + 0.03)], -1)
                    kc.tube(mb, loop, 0.025, 4, lash)
        # The deckhouse, on the far (+Z) half: woven walls, a thatch gable, its door on -Z.
        hx, hz, hh = 1.8, 1.4, 2.0
        cz = 1.6
        woven, thatch = mb.material(M_WOVEN), mb.material(M_THATCH)
        for (cx, czz, sx, sz) in ((0.0, cz + hz, hx, 0.05), (-hx, cz, 0.05, hz), (hx, cz, 0.05, hz)):
            kc.rounded_block(mb, (cx, DECK_Y + hh * 0.5, czz), (sx, hh * 0.5, sz), woven, radius=0.02, seg=1)
        for sx in (-1.0, 1.0):  # the front wall either side of the door
            kc.rounded_block(mb, (sx * (hx + 0.55) * 0.5, DECK_Y + hh * 0.5, cz - hz), ((hx - 0.55) * 0.5, hh * 0.5,
                             0.05), woven, radius=0.02, seg=1)
        pitch = 0.6
        for s in (-1.0, 1.0):  # the roof's two slopes run along X, falling to the +-Z eaves
            slope_w = (hz + 0.35) / math.cos(pitch)
            kc.rounded_block(mb, (0.0, DECK_Y + hh + math.sin(pitch) * slope_w * 0.5, cz + s * (hz + 0.35) * 0.5),
                             (hx + 0.35, 0.09, slope_w * 0.5), thatch, rot=kc.rot_x(s * pitch), radius=0.03, seg=1)
        for gx in (-hx, hx):  # the gable ends, woven, both faces
            rise = math.tan(pitch) * (hz + 0.05)
            g = np.array([[[gx, DECK_Y + hh, cz - hz], [gx, DECK_Y + hh, cz + hz]],
                          [[gx, DECK_Y + hh + rise, cz], [gx, DECK_Y + hh + rise, cz]]])
            for flip in (False, True):
                kc.quad_strip(mb, g, woven, uv=np.array([[[0, 0], [1, 0]], [[0.5, 1], [0.5, 1]]]), col=(0, 0, 0, 0.3),
                              uv2=(0.8, 0.5), flip=flip, smooth=False)
        if not lod:  # the deck clutter: a coil of line, two crates, a water cask
            a = np.linspace(0.0, 6 * math.pi, 40)
            coil = np.stack([-2.4 + np.cos(a) * 0.3, DECK_Y + 0.03 + a * 0.006, -1.5 + np.sin(a) * 0.3], -1)
            kc.tube(mb, coil, 0.025, 4, lash)
            for (x, z, r) in ((2.9, -1.8, 0.2), (3.1, -1.1, -0.3)):
                kc.rounded_block(mb, (x, DECK_Y + 0.25, z), (0.3, 0.25, 0.3), timber, rot=kc.rot_y(r), radius=0.03,
                                 seg=1, weather=WOOD)
            kc.tube(mb, np.array([[-3.2, DECK_Y, 0.4], [-3.2, DECK_Y + 0.7, 0.4]]), np.array([0.28, 0.28]), 10,
                    mb.material(M_DRIFT), cap_end=True)
        if furnished and not lod:
            _dockmaster_room(mb, (hx, hz, hh, cz), rng)
        out.append(mb)
    return out


TABLE_AT = (0.45, 2.05)  # hm_dockmaster_house's table (x, z) in the piece: the fathers_table mark stands by it


def _dockmaster_room(mb, room: tuple[float, float, float, float], rng) -> None:
    """The dock-master's room inside the deckhouse (Ch17 B07, B11): a woven floor mat, his table and two benches, a
    shelf of jars and a rolled chart, a sleeping mat along the back wall, a net hung on the west wall, and the hook his
    oil lamp hangs from over the table (the zone hangs hm_oil_lamp there and lights it)."""
    hx, hz, hh, cz = room
    timber, drift, lash = mb.material(M_TIMBER), mb.material(M_DRIFT), mb.material(M_LASH)
    woven, clay, sail = mb.material(M_WOVEN), mb.material(M_CLAY), mb.material(M_SAIL)
    kc.rounded_block(mb, (0.0, DECK_Y + 0.012, cz), (hx - 0.15, 0.012, hz - 0.15), woven, radius=0.005, seg=1)
    tx, tz = TABLE_AT
    kc.rounded_block(mb, (tx, DECK_Y + 0.72, tz), (0.55, 0.03, 0.35), timber, radius=0.01, seg=1, weather=WOOD)
    for ox, oz in ((-0.48, -0.28), (0.48, -0.28), (-0.48, 0.28), (0.48, 0.28)):
        kc.tube(mb, np.array([[tx + ox, DECK_Y, tz + oz], [tx + ox, DECK_Y + 0.7, tz + oz]]), 0.03, 4, timber)
    for sz in (-1.0, 1.0):  # the benches either side of it
        bz = tz + sz * 0.62
        kc.rounded_block(mb, (tx, DECK_Y + 0.42, bz), (0.5, 0.025, 0.13), timber, radius=0.01, seg=1, weather=WOOD)
        for ox in (-0.42, 0.42):
            kc.rounded_block(mb, (tx + ox, DECK_Y + 0.2, bz), (0.03, 0.2, 0.1), timber, radius=0.005, seg=1)
    # The lamp hook over the table, from the ridge.
    ridge = DECK_Y + hh + math.tan(0.6) * (hz + 0.05) - 0.1
    kc.tube(mb, np.array([[tx, ridge, cz], [tx, DECK_Y + 1.75, cz], [tx, DECK_Y + 1.7, cz + 0.08]]), 0.012, 3,
            mb.material(M_COPPER))
    # The shelf on the east wall: a board on two brackets, jars and a rolled chart on it.
    sx = hx - 0.2
    kc.rounded_block(mb, (sx, DECK_Y + 1.35, cz), (0.14, 0.02, 0.8), timber, radius=0.005, seg=1, weather=WOOD)
    for z in (cz - 0.6, cz + 0.6):
        kc.tube(mb, np.array([[hx - 0.06, DECK_Y + 1.15, z], [sx - 0.1, DECK_Y + 1.33, z]]), 0.02, 4, timber)
    for k in range(4):
        z = cz - 0.6 + k * 0.32
        r = float(rng.uniform(0.06, 0.09))
        kc.tube(mb, np.array([[sx, DECK_Y + 1.37, z], [sx, DECK_Y + 1.37 + r * 2.2, z]]), np.array([r, r * 0.7]), 7,
                clay, cap_end=True)
    kc.tube(mb, np.array([[sx - 0.02, DECK_Y + 1.42, cz + 0.55], [sx - 0.02, DECK_Y + 1.42, cz + 0.85]]), 0.05, 6, sail,
            cap_start=True, cap_end=True)
    # The sleeping mat and a folded blanket along the back (+Z) wall.
    kc.rounded_block(mb, (-0.6, DECK_Y + 0.06, cz + hz - 0.45), (0.95, 0.05, 0.36), woven, radius=0.03, seg=1)
    kc.rounded_block(mb, (-1.3, DECK_Y + 0.16, cz + hz - 0.45), (0.22, 0.06, 0.3), mb.material(M_CLOTH_RED),
                     radius=0.04, seg=1)
    # A mended net hung on the west wall from three pegs, sagging between them.
    wx = -hx + 0.07
    pegs = [(wx, DECK_Y + 1.6, cz + dz) for dz in (-0.9, 0.0, 0.9)]
    for p in pegs:
        kc.tube(mb, np.array([[-hx + 0.02, p[1], p[2]], [wx + 0.06, p[1], p[2]]]), 0.015, 4, drift)
    rows = []
    for k in range(5):
        y = DECK_Y + 1.6 - k * 0.22
        zs = np.linspace(cz - 0.9, cz + 0.9, 9)
        rows.append(np.stack([np.full_like(zs, wx + 0.02), y - 0.12 * np.sin((zs - cz + 0.9) / 0.9 * math.pi) ** 2
                              * (1.0 - k * 0.15), zs], -1))
    for r in rows:
        kc.tube(mb, r, 0.006, 3, lash)
    for j in range(0, 9, 2):
        kc.tube(mb, np.array([r[j] for r in rows]), 0.006, 3, lash)


def build_dockmaster_house(seed: int = 2310) -> list[kc.MeshBuilder]:
    return build_lashed_hulls(seed, "hm_dockmaster_house", furnished=True)


def _windmill(mb, lod: bool, origin=(0.0, 0.0, 0.0), scale: float = 1.0, *, far: bool = False) -> None:
    ox, oy, oz = origin
    timber, sail, copper = mb.material(M_TIMBER), mb.material(M_SAIL), mb.material(M_COPPER)
    s = scale
    top = np.array([ox, oy + 9.0 * s, oz])
    sides = 3 if far else (4 if lod else 6)
    for dx, dz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        foot = np.array([ox + dx * 1.3 * s, oy + 0.5 * s, oz + dz * 1.3 * s])
        kc.tube(mb, np.stack([foot, top + np.array([dx * 0.25 * s, -0.3 * s, dz * 0.25 * s])]), 0.08 * s, sides, timber)
    if not (lod or far):  # the cross braces, two rings
        for h in (0.35, 0.65):
            ring = []
            for dx, dz in ((-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)):
                r = 1.3 - (1.3 - 0.25) * h
                ring.append([ox + dx * r * s, oy + (0.5 + 8.2 * h) * s, oz + dz * r * s])
            kc.tube(mb, np.array(ring), 0.04 * s, 4, timber)
    hub = top + np.array([0.0, 0.0, 0.5 * s])
    kc.tube(mb, np.stack([top - np.array([0.0, 0.0, 0.4 * s]), hub + np.array([0.0, 0.0, 0.2 * s])]), 0.22 * s,
            sides + 2, copper, cap_start=True, cap_end=True)
    arms = 3 if far else 6
    for k in range(arms):
        ang = k * 2.0 * math.pi / arms + 0.2
        d = np.array([math.cos(ang), math.sin(ang), 0.0])
        kc.tube(mb, np.stack([hub, hub + d * 3.6 * s]), 0.05 * s, 3 if far else 4, timber)
        centre = hub + d * 2.3 * s + np.array([0.0, 0.0, 0.03 * s])
        kc.rounded_block(mb, centre, (1.25 * s, 0.32 * s, 0.015 * s), sail, rot=kc.rot_z(ang), radius=0.005, seg=1)
    if not far:  # the tail vane behind the head
        kc.tube(mb, np.stack([top - np.array([0.0, 0.0, 0.3 * s]), top - np.array([0.0, 0.0, 2.2 * s])]), 0.04 * s, 4,
                timber)
        kc.rounded_block(mb, top - np.array([0.0, -0.1 * s, 2.0 * s]), (0.015 * s, 0.45 * s, 0.5 * s), sail,
                         radius=0.005, seg=1)


def build_windmill(seed: int = 2302) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("hm_windmill" + ("-lod1" if lod else ""))
        # Its float: a square raft of logs, a hand under the water and half a metre over it.
        kc.rounded_block(mb, (0.0, 0.2, 0.0), (1.8, 0.35, 1.8), mb.material(M_DRIFT), radius=0.08, seg=1, weather=WOOD)
        _windmill(mb, lod)
        out.append(mb)
    return out


def build_tide_wheel(seed: int = 2303) -> list[kc.MeshBuilder]:
    out = []
    wheel_r = 1.5
    axle_y = 0.7
    for lod in (False, True):
        mb = kc.MeshBuilder("hm_tide_wheel" + ("-lod1" if lod else ""))
        timber, drift, copper = mb.material(M_TIMBER), mb.material(M_DRIFT), mb.material(M_COPPER)
        sides = 6 if lod else 12
        for z in (-1.7, 1.7):  # the pontoons, logs bound along X
            kc.tube(mb, np.array([[-2.6, 0.0, z], [2.6, 0.0, z]]), 0.45, sides, drift, cap_start=True, cap_end=True)
            kc.rounded_block(mb, (0.0, 0.6, z), (2.4, 0.06, 0.55), timber, radius=0.02, seg=1, weather=WOOD)
        # The frame: posts up from each pontoon to the axle bearings, the axle across Z.
        for z in (-1.7, 1.7):
            for x in (-0.35, 0.35):
                kc.tube(mb, np.array([[x, 0.6, z], [0.0, axle_y + 0.15, z]]), 0.06, 4 if lod else 6, timber)
        kc.tube(mb, np.array([[0.0, axle_y, -1.9], [0.0, axle_y, 1.9]]), 0.09, sides, copper, cap_start=True,
                cap_end=True)
        # The wheel: two rims, spokes, and the paddles between the rims (the low ones dip into the tide).
        n_pad = 6 if lod else 10
        a = np.linspace(0.0, 2.0 * math.pi, 9 if lod else 33)
        for z in (-0.8, 0.8):
            ring = np.stack([np.cos(a) * wheel_r, axle_y + np.sin(a) * wheel_r, np.full_like(a, z)], -1)
            kc.tube(mb, ring, 0.05, 4, timber)
        for k in range(n_pad):
            ang = k * 2.0 * math.pi / n_pad
            d = np.array([math.cos(ang), math.sin(ang), 0.0])
            for z in () if lod else (-0.8, 0.8):
                kc.tube(mb, np.stack([np.array([0.0, axle_y, z]), np.array([0.0, axle_y, z]) + d * wheel_r]), 0.04, 4,
                        timber)
            centre = np.array([0.0, axle_y, 0.0]) + d * (wheel_r - 0.25)
            kc.rounded_block(mb, centre, (0.3, 0.025, 0.82), timber, rot=kc.rot_z(ang), radius=0.01, seg=1,
                             weather=WOOD)
        # The gear housing on the +Z pontoon's deck, its face carrying the Saltwright mark.
        face_z = 2.0
        kc.rounded_block(mb, (0.0, 1.05, face_z - 0.25), (0.45, 0.4, 0.25), copper, radius=0.04, seg=1)
        lowlight._mark(mb, (0.0, 1.05), face_z, lod)
        out.append(mb)
    return out


def _lantern(mb, at, lod: bool) -> None:
    glass, core, copper = mb.material(M_GLASS), mb.material(M_CORE), mb.material(M_COPPER)
    x, y, z = at
    kc.rounded_block(mb, (x, y, z), (0.07, 0.07, 0.07), core, radius=0.03, seg=1 if lod else 2)
    kc.rounded_block(mb, (x, y, z), (0.16, 0.2, 0.16), glass, radius=0.03, seg=1)
    kc.rounded_block(mb, (x, y + 0.24, z), (0.2, 0.04, 0.2), copper, radius=0.02, seg=1)
    kc.rounded_block(mb, (x, y - 0.23, z), (0.18, 0.03, 0.18), copper, radius=0.02, seg=1)


def build_signal_lamp(seed: int = 2304) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("hm_signal_lamp" + ("-lod1" if lod else ""))
        timber = mb.material(M_TIMBER)
        kc.tube(mb, np.array([[0.0, 0.0, 0.0], [0.0, 3.4, 0.0]]), np.array([0.07, 0.05]), 4 if lod else 8, timber,
                cap_end=True)
        kc.tube(mb, np.array([[0.0, 3.2, 0.0], [0.55, 3.25, 0.0]]), 0.03, 4, timber)
        _lantern(mb, (0.55, 2.9, 0.0), lod)
        if not lod:
            kc.tube(mb, np.array([[0.55, 3.25, 0.0], [0.55, 3.14, 0.0]]), 0.008, 4, mb.material(M_COPPER))
            kc.rounded_block(mb, (0.0, 0.05, 0.0), (0.2, 0.05, 0.2), timber, radius=0.02, seg=1)
        out.append(mb)
    return out


# Dace's hull: a sailing hull of 13 m, keel at y 1.2 on the cradle, sheer at y 3.8.
DACE_LEN = 12.0
DACE_HALF_BEAM = 2.0
KEEL_Y = 1.2
SHEER_Y = 3.8
RIBS = 13
STRAKES = 5
# Ch17's fit-out (M5-A3P-1500): the decked stern from the sternpost to STERN_X, the cabin's sole at SOLE_T of the way
# from keel to sheer, the hatch (x, half-size) on the centre line, and the mast and its kite wing (kite.py's lines).
STERN_X = -2.0
SOLE_T = 0.25
HATCH = (-3.0, 0.42)
DOOR_HALF_W = 0.4
DOOR_H = 1.75
ENGINE_BED_X = (-1.6, 0.4)
MAST_X = 1.0
MAST_H = 11.0


def _rib_point(x: float, t: float) -> tuple[float, float]:
    """A rib's (height, half-width) at fraction t from keel (0) to sheer (1), at station x."""
    hw = float(hull_half_width(x, DACE_LEN + 1.2, DACE_HALF_BEAM))
    return KEEL_Y + (SHEER_Y - KEEL_Y) * t, hw * math.sin(t * math.pi * 0.5) ** 0.6


def build_dace_hull(seed: int = 2305) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("dace_hull_frame", seed)
        mb = kc.MeshBuilder("dace_hull_frame" + ("-lod1" if lod else ""))
        timber, drift, tar = mb.material(M_TIMBER), mb.material(M_DRIFT), mb.material(M_TAR)
        # The floating dry-dock: a pontoon deck, its top at DOCK_TOP, and the cradle blocks under the keel.
        kc.rounded_block(mb, (0.0, DOCK_TOP - 0.5, 0.0), (8.0, 0.5, 3.5), drift, radius=0.06, seg=1, weather=WOOD)
        for x in np.linspace(-4.5, 4.5, 4):
            kc.rounded_block(mb, (x, (DOCK_TOP + KEEL_Y - 0.12) * 0.5, 0.0), (0.3, (KEEL_Y - 0.12 - DOCK_TOP) * 0.5,
                             0.7), tar, radius=0.02, seg=1)
        # The keel, the stem rising at +X and the sternpost at -X.
        sides = 4 if lod else 6
        kc.rounded_block(mb, (0.0, KEEL_Y - 0.06, 0.0), (DACE_LEN * 0.5, 0.12, 0.1), timber, radius=0.02, seg=1)
        t = np.linspace(0.0, 1.0, 5 if lod else 9)
        stem = np.stack([DACE_LEN * 0.5 + 0.9 * t ** 1.6, KEEL_Y + (SHEER_Y + 0.4 - KEEL_Y) * t, np.zeros_like(t)], -1)
        kc.tube(mb, stem, 0.11, sides, timber)
        kc.tube(mb, np.array([[-DACE_LEN * 0.5, KEEL_Y, 0.0], [-DACE_LEN * 0.5 - 0.35, SHEER_Y + 0.2, 0.0]]), 0.11,
                sides, timber)
        # The ribs, keel to sheer on both sides.
        xs = np.linspace(-DACE_LEN * 0.5 + 0.6, DACE_LEN * 0.5 - 0.6, RIBS)
        tt = np.linspace(0.0, 1.0, 4 if lod else 9)
        for x in xs[::2] if lod else xs:
            pts = [(x, *_rib_point(x, float(v))) for v in tt]
            line = np.array([[px, py, -pz] for px, py, pz in pts[::-1]] + [[px, py, pz] for px, py, pz in pts[1:]])
            kc.tube(mb, line, 0.05, 4, timber)
        # The strakes: the lowest five on the near (-Z) side only, board by board between the ribs.
        for k in range(STRAKES):
            v = 0.08 + k * 0.105
            if lod:
                pa = _rib_point(xs[0], v)
                pb = _rib_point(xs[-1], v)
                kc.plank(mb, (xs[0], pa[0], -pa[1] - 0.06), (xs[-1], pb[0], -pb[1] - 0.06), 0.3, 0.04, timber)
                continue
            last = len(xs) - 1 - (STRAKES - k)  # the top strakes stop short: the work in hand
            for i in range(last):
                if xs[i] < STERN_X:
                    continue  # the decked stern is planked whole
                pa, pb = _rib_point(xs[i], v), _rib_point(xs[i + 1], v)
                kc.plank(mb, (xs[i], pa[0], -pa[1] - 0.06), (xs[i + 1], pb[0], -pb[1] - 0.06), 0.3, 0.04, timber,
                         up=(0.0, 0.3, -1.0), weather=WOOD, variation=float(rng.random()))
        # The staging along the near side: poles, a walk-board at 2.3 m, a ladder.
        if not lod:
            for x in np.linspace(-5.0, 5.0, 5):
                kc.tube(mb, np.array([[x, DOCK_TOP, -3.0], [x, 4.2, -3.0]]), 0.05, 5, drift)
            kc.plank(mb, (-5.2, 2.3, -2.8), (5.2, 2.3, -2.8), 0.45, 0.05, timber)
            for sx in (-0.2, 0.2):
                kc.tube(mb, np.array([[5.6 + sx, DOCK_TOP, -3.2], [5.6 + sx, 2.4, -2.95]]), 0.025, 4, drift)
            for k in range(6):
                y = DOCK_TOP + 0.3 * (k + 1)
                z = -3.2 + 0.25 * (y - DOCK_TOP) / 1.8
                kc.tube(mb, np.array([[5.4, y, z], [5.8, y, z]]), 0.018, 4, drift)
            # His workbench on the dock's +Z side, a plank and a rib-mould on it.
            kc.rounded_block(mb, (-2.5, DOCK_TOP + 0.85, 2.8), (1.2, 0.04, 0.35), timber, radius=0.01, seg=1)
            for x in (-3.5, -1.5):
                kc.tube(mb, np.array([[x, DOCK_TOP, 2.8], [x, DOCK_TOP + 0.82, 2.8]]), 0.04, 4, timber)
            kc.plank(mb, (-3.4, DOCK_TOP + 0.92, 2.7), (-1.8, DOCK_TOP + 0.92, 2.75), 0.25, 0.03, timber)
            a = np.linspace(0.2, 1.4, 7)
            mould = np.stack([-2.3 + np.cos(a) * 0.6, np.full_like(a, DOCK_TOP + 0.91), 2.95 - np.sin(a) * 0.4], -1)
            kc.tube(mb, mould, 0.02, 4, drift)
        _dace_stern(mb, lod, rng)
        _dace_rig(mb, lod, rng)
        out.append(mb)
    return out


def _strip(mb, grid: np.ndarray, mat: int, want) -> None:
    """quad_strip turned so its first quad faces `want` (a direction)."""
    n = np.cross(grid[0, 1] - grid[0, 0], grid[1, 0] - grid[0, 0])
    span = np.ptp(grid.reshape(-1, 3), axis=0)
    uv = grid[..., [k for k in range(3) if k != int(np.argmin(span))]]  # the two axes it spans
    kc.quad_strip(mb, grid, mat, uv=uv, col=(0.0, 0.15, 0.2, 0.5), uv2=(0.8, 0.5),
                  flip=bool(np.dot(n, np.asarray(want, float)) < 0.0))


def _deck_strip(mb, mat: int, xa: float, xb: float, za, zb, n: int) -> None:
    """The deck at the sheer between stations xa and xb, from za(x) to zb(x) across: its top, and its underside (the
    cabin's ceiling)."""
    xs = np.linspace(xa, xb, n)
    grid = np.stack([np.stack([xs, np.full(n, SHEER_Y), np.array([f(x) for x in xs])], -1) for f in (za, zb)])
    _strip(mb, grid, mat, (0.0, 1.0, 0.0))
    _strip(mb, grid - np.array([0.0, 0.05, 0.0]), mat, (0.0, -1.0, 0.0))


def _dace_stern(mb, lod: bool, rng) -> None:
    """Ch17's decked stern: the planking both sides from the sternpost to STERN_X, the deck with its hatch, the cabin's
    sole and bulkhead, and (LOD0) the cabin's fittings and the engine bay's empty bed."""
    timber, tar, drift = mb.material(M_TIMBER), mb.material(M_TAR), mb.material(M_DRIFT)
    stern = -DACE_LEN * 0.5
    nx, nt = (4, 4) if lod else (9, 9)
    xs = np.linspace(stern + 0.05, STERN_X, nx)
    ts = np.linspace(0.0, 1.0, nt)
    for side in (-1.0, 1.0):
        grid = np.array([[[x, _rib_point(x, t)[0], side * (_rib_point(x, t)[1] + 0.04)] for x in xs] for t in ts])
        _strip(mb, grid, timber, (0.0, 0.0, side))
        _strip(mb, grid - np.array([0.0, 0.0, side * 0.05]), timber, (0.0, 0.0, -side))  # the cabin's side
    hw = lambda x: _rib_point(x, 1.0)[1] + 0.04  # noqa: E731 - the sheer's half-width
    hx, hh = HATCH
    n = 3 if lod else 6
    _deck_strip(mb, timber, stern + 0.05, hx - hh, lambda x: -hw(x), hw, n)
    _deck_strip(mb, timber, hx + hh, STERN_X, lambda x: -hw(x), hw, n)
    _deck_strip(mb, timber, hx - hh, hx + hh, lambda x: -hw(x), lambda x: -hh, 2)
    _deck_strip(mb, timber, hx - hh, hx + hh, lambda x: hh, hw, 2)
    sole_y = KEEL_Y + (SHEER_Y - KEEL_Y) * SOLE_T
    sw = lambda x: _rib_point(x, SOLE_T)[1] - 0.02  # noqa: E731 - the sole's half-width
    _deck_strip_y = np.linspace(stern + 0.9, ENGINE_BED_X[1], 4 if lod else 10)
    grid = np.stack([np.stack([_deck_strip_y, np.full_like(_deck_strip_y, sole_y), np.array([s * sw(x) for x in
                                                                                         _deck_strip_y])], -1)
                     for s in (-1.0, 1.0)])
    _strip(mb, grid, timber, (0.0, 1.0, 0.0))
    # The bulkhead at STERN_X, sole to deck, a doorway through it on the centre line.
    # Its two leaves follow the rib out to the planking, keel-side to sheer; both faces (the cabin and the bay).
    bw = _rib_point(STERN_X, 0.7)[1]  # the leaves' half-width at the chart's height
    ts_b = np.linspace(SOLE_T, 1.0, 3 if lod else 7)
    for sz in (-1.0, 1.0):
        grid = np.array([[[STERN_X, _rib_point(STERN_X, t)[0], sz * (_rib_point(STERN_X, t)[1] + 0.04)],
                          [STERN_X, _rib_point(STERN_X, t)[0], sz * DOOR_HALF_W]] for t in ts_b])
        for fx in (-1.0, 1.0):
            _strip(mb, grid + np.array([fx * 0.02, 0.0, 0.0]), timber, (fx, 0.0, 0.0))
    top = sole_y + DOOR_H
    grid = np.array([[[STERN_X, y, -DOOR_HALF_W], [STERN_X, y, DOOR_HALF_W]] for y in (top, SHEER_Y)])
    for fx in (-1.0, 1.0):
        _strip(mb, grid + np.array([fx * 0.02, 0.0, 0.0]), timber, (fx, 0.0, 0.0))
    for sz in (-1.0, 1.0):  # the door posts
        kc.tube(mb, np.array([[STERN_X, sole_y, sz * DOOR_HALF_W], [STERN_X, SHEER_Y, sz * DOOR_HALF_W]]), 0.05, 4,
                timber)
    # The hatch coaming and the ladder down to the sole.
    kc.rounded_block(mb, (hx, SHEER_Y + 0.08, 0.0), (hh + 0.06, 0.08, hh + 0.06), tar, radius=0.02, seg=1)
    # The Lit Age brass shoe along the keel, under it all.
    kc.rounded_block(mb, (0.0, KEEL_Y - 0.15, 0.0), (DACE_LEN * 0.5 - 0.3, 0.04, 0.13), mb.material(M_PLATE),
                     radius=0.02, seg=1, weather=WOOD)
    if lod:
        return
    for sz in (-0.25, 0.25):
        kc.tube(mb, np.array([[hx + hh - 0.1, sole_y, sz], [hx - hh + 0.15, SHEER_Y, sz]]), 0.03, 5, drift)
    for k in range(6):
        f = (k + 0.7) / 6.5
        x = hx + hh - 0.1 + (-2.0 * hh + 0.25) * f
        y = sole_y + (SHEER_Y - sole_y) * f
        kc.tube(mb, np.array([[x, y, -0.25], [x, y, 0.25]]), 0.02, 4, drift)
    # His bunk along the +Z side, aft.
    bx, bz = stern + 1.9, sw(stern + 1.9) - 0.4
    kc.rounded_block(mb, (bx, sole_y + 0.42, bz), (0.85, 0.04, 0.34), timber, radius=0.01, seg=1, weather=WOOD)
    kc.rounded_block(mb, (bx, sole_y + 0.52, bz), (0.8, 0.06, 0.3), mb.material(M_SAIL), radius=0.04, seg=2)
    for x in (bx - 0.8, bx + 0.8):
        kc.tube(mb, np.array([[x, sole_y, bz - 0.3], [x, sole_y + 0.42, bz - 0.3]]), 0.035, 4, timber)
    # The fold-down desk on the -Z side by the bulkhead, the ledger open on it, a stool.
    dx = STERN_X - 0.75
    dz = -(sw(dx) - 0.35)
    kc.rounded_block(mb, (dx, sole_y + 0.76, dz), (0.42, 0.025, 0.24), timber, radius=0.01, seg=1, weather=WOOD)
    kc.tube(mb, np.array([[dx, sole_y + 0.74, dz + 0.2], [dx, sole_y + 0.2, dz - 0.2]]), 0.025, 4, timber)
    kc.rounded_block(mb, (dx, sole_y + 0.8, dz + 0.02), (0.2, 0.012, 0.15), tar, radius=0.006, seg=1)
    for sz in (-0.075, 0.075):  # the two open pages, a little apart at the spine
        kc.rounded_block(mb, (dx + 0.0, sole_y + 0.818, dz + 0.02 + sz), (0.18, 0.006, 0.07), mb.material(M_SAIL),
                         rot=kc.rot_x(-sz * 0.6), radius=0.003, seg=1)
    kc.rounded_block(mb, (dx - 0.05, sole_y + 0.24, dz + 0.45), (0.17, 0.02, 0.17), timber, radius=0.01, seg=1)
    for ox, oz in ((-0.13, -0.13), (0.13, -0.13), (-0.13, 0.13), (0.13, 0.13)):
        kc.tube(mb, np.array([[dx - 0.05 + ox, sole_y, dz + 0.45 + oz], [dx - 0.05 + ox, sole_y + 0.23,
                                                                          dz + 0.45 + oz]]), 0.02, 4, timber)
    # The chart wall: a chart on the bulkhead's +Z leaf (cabin side), Corrow circled in red.
    cx, cz, cy = STERN_X - 0.05, (bw + DOOR_HALF_W) * 0.5, sole_y + 1.25
    kc.rounded_block(mb, (cx, cy, cz), (0.008, 0.38, 0.42), mb.material(M_SAIL), radius=0.004, seg=1)
    a = np.linspace(0.0, 2.0 * math.pi, 13)
    ring = np.stack([np.full_like(a, cx - 0.012), cy - 0.08 + np.sin(a) * 0.07, cz + 0.12 + np.cos(a) * 0.09], -1)
    kc.tube(mb, ring, 0.008, 4, mb.material(M_CLOTH_RED))
    for k in range(5):  # the coast it charts, a few inked lines
        y0 = cy - 0.3 + k * 0.13
        kc.tube(mb, np.array([[cx - 0.01, y0, cz - 0.35], [cx - 0.01, y0 + float(rng.uniform(-0.05, 0.05)),
                                                           cz + 0.35]]), 0.004, 3, tar)
    # The tool rack on the -Z leaf: a batten, his hooks (the make of Rhen's), the tools hung on them.
    tz = -(bw + DOOR_HALF_W) * 0.5
    kc.rounded_block(mb, (STERN_X - 0.06, sole_y + 1.45, tz), (0.025, 0.05, 0.4), timber, radius=0.01, seg=1)
    for k in range(5):
        z = tz - 0.32 + k * 0.16
        hook = np.array([[STERN_X - 0.08, sole_y + 1.45, z], [STERN_X - 0.16, sole_y + 1.43, z],
                         [STERN_X - 0.17, sole_y + 1.36, z]])
        kc.tube(mb, hook, 0.008, 3, mb.material(M_COPPER))
        length = float(rng.uniform(0.3, 0.55))
        kc.tube(mb, np.array([[STERN_X - 0.17, sole_y + 1.36, z], [STERN_X - 0.15, sole_y + 1.36 - length, z]]),
                0.015 if k % 2 else 0.022, 4, timber if k % 2 else mb.material(M_COPPER))
    # The engine bay: two bearers on the sole and the empty bed's half-round chocks, a bronze mounting ring between.
    ea, eb = ENGINE_BED_X
    for sz in (-0.5, 0.5):
        kc.rounded_block(mb, ((ea + eb) * 0.5, sole_y + 0.1, sz), ((eb - ea) * 0.5, 0.1, 0.07), timber, radius=0.01,
                         seg=1, weather=WOOD)
    for x in (ea + 0.3, eb - 0.3):
        a = np.linspace(math.pi, 2.0 * math.pi, 9)
        chock = np.stack([np.full_like(a, x), sole_y + 0.65 + np.sin(a) * 0.45, np.cos(a) * 0.45], -1)
        kc.tube(mb, chock, 0.06, 5, timber)
    a = np.linspace(0.0, 2.0 * math.pi, 17)
    ring = np.stack([np.full_like(a, (ea + eb) * 0.5), sole_y + 0.65 + np.sin(a) * 0.32, np.cos(a) * 0.32], -1)
    kc.tube(mb, ring, 0.03, 5, mb.material(M_PLATE))


def _dace_rig(mb, lod: bool, rng) -> None:
    """The mast stepped on the keel and one kite wing half-rigged on the +Z side (kite.py's spars): two of the forward
    sail's three panels bent on, the rest furled along the foot spar; the -Z wing not yet begun."""
    timber, sand, red = mb.material(M_TIMBER), mb.material(M_SAIL), mb.material(M_CLOTH_RED)
    kc.tube(mb, np.array([[MAST_X, KEEL_Y, 0.0], [MAST_X, SHEER_Y + MAST_H, 0.0]]), np.array([0.16, 0.09]),
            6 if lod else 10, timber, cap_end=True)
    head = np.array([MAST_X, SHEER_Y + MAST_H - 0.6, 0.0])
    foot = np.array([MAST_X - 0.4, SHEER_Y + 5.0, 0.0])
    tip = np.array([MAST_X - 2.4, SHEER_Y + 7.8, 8.5])
    for a in (head, foot):
        kc.tube(mb, np.array([a, tip]), 0.06, 4 if lod else 6, timber)
    n = 3
    for k in range(2):  # the two panels bent on, from the mast out
        u0, u1 = k / n, (k + 1) / n
        p0, p1 = head + (tip - head) * u0, head + (tip - head) * u1
        q0, q1 = foot + (tip - foot) * u0, foot + (tip - foot) * u1
        sag = np.array([0.0, -0.1, 0.0]) * (0.6 + 0.4 * float(rng.random()))
        grid = np.array([[p0, p1], [(p0 + q0) * 0.5 + sag, (p1 + q1) * 0.5 + sag], [q0, q1]])
        uv = np.array([[[u0, 0.0], [u1, 0.0]], [[u0, 0.5], [u1, 0.5]], [[u0, 1.0], [u1, 1.0]]]) * 2.0
        for flip in (False, True):
            kc.quad_strip(mb, grid, red if k % 2 else sand, uv=uv, col=(0.0, 0.0, 0.0, 0.3), uv2=(0.9, 0.5),
                          flip=flip, smooth=False)
        if not lod and k > 0:
            kc.tube(mb, np.array([p0, (p0 + q0) * 0.5 + sag, q0]), 0.03, 4, timber)
    # The rest furled: a roll of sailcloth lashed along the foot spar's outer third.
    roll = np.array([foot + (tip - foot) * u for u in (0.68, 0.84, 0.97)])
    kc.tube(mb, roll, np.array([0.13, 0.11, 0.07]), 5 if lod else 8, sand, cap_start=True, cap_end=True)
    if not lod:
        for u in (0.72, 0.86, 0.94):
            c = foot + (tip - foot) * u
            a = np.linspace(0.0, 2.0 * math.pi, 7)
            d = (tip - foot) / np.linalg.norm(tip - foot)
            e1 = np.cross(d, [0.0, 1.0, 0.0])
            e1 /= np.linalg.norm(e1)
            e2 = np.cross(d, e1)
            loop = np.array([c + (e1 * math.cos(t) + e2 * math.sin(t)) * 0.14 for t in a])
            kc.tube(mb, loop, 0.012, 3, mb.material(M_LASH))


def build_far_flotilla(seed: int = 2306) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("hm_far_flotilla", seed)
        mb = kc.MeshBuilder("hm_far_flotilla" + ("-lod1" if lod else ""))
        drift, woven, thatch = mb.material(M_DRIFT), mb.material(M_WOVEN), mb.material(M_THATCH)
        clusters = 14 if lod else 26
        for c in range(clusters):
            ang = (c + float(rng.uniform(-0.3, 0.3))) * 2.0 * math.pi / clusters
            r = float(rng.uniform(*FAR_RANGE))
            cx, cz = math.sin(ang) * r, math.cos(ang) * r
            yaw = float(rng.uniform(0.0, math.pi))
            for k in range(1 if lod else int(rng.integers(2, 5))):  # lashed homes: a deck slab and a house
                ox = cx + float(rng.uniform(-14.0, 14.0))
                oz = cz + float(rng.uniform(-14.0, 14.0))
                kc.rounded_block(mb, (ox, 0.45, oz), (5.0, 0.45, 3.5), drift, rot=kc.rot_y(yaw), radius=0.1, seg=1)
                kc.rounded_block(mb, (ox, 1.9, oz), (2.0, 1.0, 1.5), woven, rot=kc.rot_y(yaw), radius=0.05, seg=1)
                kc.rounded_block(mb, (ox, 3.0, oz), (2.4, 0.18, 1.9), thatch, rot=kc.rot_y(yaw), radius=0.05, seg=1)
            if rng.random() < 0.6:
                _windmill(mb, True, (cx + 6.0, 0.0, cz - 4.0), float(rng.uniform(0.9, 1.3)), far=True)
        out.append(mb)
    return out


# --- Ch15's first visit (M4-A2P-045) ------------------------------------------------------------------------------
DOCK_LEN = 4.0
DOCK_HALF_W = 1.8
DOCK_FREEBOARD = 0.9  # the deck over the water (the lashed hulls' DECK_Y)
M_CLOTH_RED = "kit_keth_red"
M_CLAY = "kit_earthenware"
M_FLAME = "kit_lamp_flame"
LAMP_FLAME = (0.0, 1.55, 0.45)  # hm_oil_lamp's flame from its foot (x, y, z)


def _dock(name: str, rails: tuple[float, ...], seed: int) -> list[kc.MeshBuilder]:
    out = []
    hl = DOCK_LEN * 0.5
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
        timber, drift, lash = mb.material(M_TIMBER), mb.material(M_DRIFT), mb.material(M_LASH)
        for sz in (-1.0, 1.0):  # the pontoon logs, half under the water
            kc.tube(mb, np.array([[-hl, -DOCK_FREEBOARD + 0.05, sz * 1.1], [hl, -DOCK_FREEBOARD + 0.05, sz * 1.1]]),
                    0.32, 6 if lod else 10, drift, weather=WOOD, cap_end=True, cap_start=True)
        for x in np.linspace(-hl + 0.4, hl - 0.4, 2 if lod else 4):  # the cross bearers
            kc.rounded_block(mb, (x, -0.2, 0.0), (0.08, 0.1, DOCK_HALF_W), timber, radius=0.02, seg=1, weather=WOOD)
            kc.tube(mb, np.array([[x, -0.3, -1.1], [x, -DOCK_FREEBOARD + 0.05, -1.1]]), 0.06, 4, timber)
            kc.tube(mb, np.array([[x, -0.3, 1.1], [x, -DOCK_FREEBOARD + 0.05, 1.1]]), 0.06, 4, timber)
        if lod:
            kc.rounded_block(mb, (0.0, -0.03, 0.0), (hl, 0.03, DOCK_HALF_W), timber, radius=0.01, seg=1, weather=WOOD)
        else:
            for z in np.arange(-DOCK_HALF_W + 0.15, DOCK_HALF_W, 0.3):  # planks along X, the walk's grain
                kc.plank(mb, (-hl + 0.01, -0.03, z), (hl - 0.01, -0.03, z), 0.28, 0.05, timber, weather=WOOD,
                         variation=float(rng.random()))
            for x in (-hl + 0.4, hl - 0.4):  # lashing round the pontoons at the bearers
                for sz in (-1.0, 1.0):
                    a = np.linspace(0.0, 2 * math.pi, 9)
                    loop = np.stack([np.full_like(a, x + 0.12), -DOCK_FREEBOARD + 0.05 + np.sin(a) * 0.35,
                                     sz * 1.1 + np.cos(a) * 0.35], -1)
                    kc.tube(mb, loop, 0.022, 4, lash)
        for sz in rails:  # the rails: lashed poles on posts
            z = sz * (DOCK_HALF_W + 0.1)
            for x in (-hl + 0.15, 0.0, hl - 0.15) if not lod else (-hl + 0.15, hl - 0.15):
                kc.tube(mb, np.array([[x, -0.1, z], [x, 0.55, z]]), 0.05, 4 if lod else 6, drift, cap_end=True)
            kc.tube(mb, np.array([[-hl, 0.5, z], [hl, 0.5, z]]), 0.045, 4 if lod else 6, drift, cap_end=True,
                    cap_start=True)
        out.append(mb)
    return out


def build_dock() -> list[kc.MeshBuilder]:
    return _dock("hm_dock_4m", (-1.0, 1.0), 2311)


def build_dock_open_n() -> list[kc.MeshBuilder]:
    return _dock("hm_dock_4m_open_n", (1.0,), 2311)


def build_dock_open_s() -> list[kc.MeshBuilder]:
    return _dock("hm_dock_4m_open_s", (-1.0,), 2311)


def build_dock_open_ns() -> list[kc.MeshBuilder]:
    return _dock("hm_dock_4m_open_ns", (), 2311)


def build_pyre_raft(seed: int = 2312) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("pyre_raft", seed)
        mb = kc.MeshBuilder("pyre_raft" + ("-lod1" if lod else ""))
        drift, lash, red = mb.material(M_DRIFT), mb.material(M_LASH), mb.material(M_CLOTH_RED)
        for k in range(4 if lod else 7):  # the logs along Z
            x = -1.35 + 2.7 * k / (3 if lod else 6)
            kc.tube(mb, np.array([[x, 0.05, -2.0 - 0.1 * float(rng.random())], [x, 0.05, 2.0 + 0.1 * float(rng.random())]]),
                    0.2, 6 if lod else 9, drift, weather=WOOD, cap_end=True, cap_start=True)
        if not lod:
            for z in (-1.5, 1.5):
                kc.tube(mb, np.array([[-1.6, 0.27, z], [1.6, 0.27, z]]), 0.06, 6, drift, cap_end=True, cap_start=True)
                kc.tube(mb, np.array([[-1.5, 0.12, z + 0.1], [1.5, 0.12, z + 0.1]]), 0.025, 4, lash)
        # The bier: driftwood stacked crosswise, the folded red cloth on it.
        for layer in range(3 if lod else 5):
            y = 0.35 + 0.12 * layer
            for k in range(3):
                if layer % 2:
                    kc.tube(mb, np.array([[-0.6, y, -0.8 + 0.8 * k], [0.6, y, -0.8 + 0.8 * k]]), 0.06, 5, drift,
                            cap_end=True, cap_start=True)
                else:
                    kc.tube(mb, np.array([[-0.5 + 0.5 * k, y, -1.0], [-0.5 + 0.5 * k, y, 1.0]]), 0.06, 5, drift,
                            cap_end=True, cap_start=True)
        top = 0.35 + 0.12 * (3 if lod else 5)
        kc.rounded_block(mb, (0.0, top + 0.04, 0.2), (0.4, 0.04, 0.3), red, radius=0.02, seg=1,
                         weather=kc.Weathering(moss=0.0, salt=0.0, wet=0.0, erosion=0.05))
        out.append(mb)
    return out


SHIP_LEN = 16.0
SHIP_HULL_Z = 1.7
SHIP_DECK_Y = 1.6


def build_ship(seed: int = 2313) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("hm_ship", seed)
        mb = kc.MeshBuilder("hm_ship" + ("-lod1" if lod else ""))
        timber, lash, sail, plate = (mb.material(M_TIMBER), mb.material(M_LASH), mb.material(M_SAIL),
                                     mb.material(M_PLATE))
        n = 9 if lod else 21
        xs = np.linspace(-SHIP_LEN * 0.5, SHIP_LEN * 0.5, n)
        for cz in (-SHIP_HULL_Z, SHIP_HULL_Z):  # two slender hulls, double-ended
            hw = np.array([float(hull_half_width(x, SHIP_LEN, 0.8)) for x in xs])
            rows = []
            for k, x in enumerate(xs):
                ring = []
                for a in np.linspace(0.0, math.pi, 5 if lod else 9):
                    ring.append([x, SHIP_DECK_Y - 0.15 - math.sin(a) * (SHIP_DECK_Y + 0.4) * (0.3 + 0.7 * hw[k] / 0.8),
                                 cz + math.cos(a) * hw[k]])
                rows.append(ring)
            kc.quad_strip(mb, np.array(rows), timber, uv=np.zeros((n, 5 if lod else 9, 2)), col=(0.05, 0.3, 0.3, 0.25),
                          uv2=(0.7, 0.5), flip=False)
            kc.quad_strip(mb, np.array(rows), timber, uv=np.zeros((n, 5 if lod else 9, 2)), col=(0.05, 0.3, 0.3, 0.25),
                          uv2=(0.7, 0.5), flip=True)
            if not lod:  # Lit Age plating patches on the hulls' outboard sides
                for x in (-4.0, 1.5, 5.0):
                    kc.rounded_block(mb, (x, 0.5, cz + np.sign(cz) * 0.62), (0.8 + 0.3 * float(rng.random()), 0.35,
                                     0.02), plate, radius=0.01, seg=1)
        # The deck across both hulls, and its lashing beams.
        if lod:
            kc.rounded_block(mb, (0.0, SHIP_DECK_Y, 0.0), (SHIP_LEN * 0.36, 0.05, SHIP_HULL_Z + 0.6), timber, radius=0.01,
                             seg=1, weather=WOOD)
        else:
            for z in np.arange(-SHIP_HULL_Z - 0.55, SHIP_HULL_Z + 0.56, 0.3):
                kc.plank(mb, (-SHIP_LEN * 0.36, SHIP_DECK_Y, z), (SHIP_LEN * 0.36, SHIP_DECK_Y, z), 0.28, 0.05, timber,
                         weather=WOOD, variation=float(rng.random()))
            for x in np.linspace(-SHIP_LEN * 0.36, SHIP_LEN * 0.36, 6):
                kc.tube(mb, np.array([[x, SHIP_DECK_Y - 0.1, -SHIP_HULL_Z - 0.5], [x, SHIP_DECK_Y - 0.1, SHIP_HULL_Z + 0.5]]),
                        0.04, 4, lash)
        for mx, h in ((-2.5, 9.0), (3.5, 7.0)):  # two masts, their sails furled on the yards
            kc.tube(mb, np.array([[mx, SHIP_DECK_Y, 0.0], [mx, SHIP_DECK_Y + h, 0.0]]), np.array([0.12, 0.07]),
                    6 if lod else 10, timber, cap_end=True)
            yard_y = SHIP_DECK_Y + h * 0.82
            kc.tube(mb, np.array([[mx, yard_y, -2.6], [mx, yard_y, 2.6]]), 0.06, 6, timber, cap_end=True, cap_start=True)
            kc.tube(mb, np.array([[mx + 0.1, yard_y - 0.12, -2.4], [mx + 0.1, yard_y - 0.16, 0.0],
                                  [mx + 0.1, yard_y - 0.12, 2.4]]),
                    np.array([0.14, 0.2, 0.14]), 6 if lod else 10, sail, cap_end=True, cap_start=True)
            if not lod:  # the stays
                for sz in (-1.0, 1.0):
                    kc.tube(mb, np.array([[mx, SHIP_DECK_Y + h * 0.95, 0.0], [mx, SHIP_DECK_Y, sz * (SHIP_HULL_Z + 0.4)]]),
                            0.012, 3, lash)
        out.append(mb)
    return out


def build_supper_table(seed: int = 2314) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("hm_supper_table", seed)
        mb = kc.MeshBuilder("hm_supper_table" + ("-lod1" if lod else ""))
        timber, drift = mb.material(M_TIMBER), mb.material(M_DRIFT)
        kc.rounded_block(mb, (0.0, 0.5, 0.0), (0.7, 0.04, 0.4), timber, radius=0.02, seg=1, weather=WOOD)
        for sx in (-1.0, 1.0):
            for sz in (-1.0, 1.0):
                kc.tube(mb, np.array([[sx * 0.6, 0.0, sz * 0.32], [sx * 0.6, 0.47, sz * 0.32]]), 0.035, 4, drift)
        for sx, sz in ((-0.4, -0.75), (0.4, -0.75), (-0.4, 0.75), (0.4, 0.75)):  # stools
            kc.tube(mb, np.array([[sx, 0.0, sz], [sx, 0.33, sz]]), np.array([0.12, 0.1]), 5 if lod else 8, drift,
                    cap_end=True)
        if not lod:  # bowls and the oil lamp (the zone lights it)
            for k, (bx, bz) in enumerate(((-0.4, -0.15), (0.0, 0.18), (0.4, -0.12))):
                _revolve_bowl(mb, bx, 0.54, bz, 0.09 + 0.02 * k)
            _revolve_bowl(mb, 0.15, 0.54, -0.2, 0.06)
            kc.tube(mb, np.array([[0.15, 0.57, -0.2], [0.15, 0.68, -0.2]]), np.array([0.025, 0.0]), 6,
                    mb.material(M_FLAME))
        del rng
        out.append(mb)
    return out


def _revolve_bowl(mb, x: float, y: float, z: float, r: float) -> None:
    ys = y + np.array([0.0, 0.01, 0.04, 0.06])
    rs = np.array([r * 0.4, r * 0.7, r * 0.95, r])
    pts = np.stack([np.full(4, x), ys, np.full(4, z)], -1)
    kc.tube(mb, pts, rs, 10, mb.material(M_CLAY), u_repeat=1.0, first_normal=(1.0, 0.0, 0.0))


def build_oil_lamp(seed: int = 2315) -> list[kc.MeshBuilder]:
    out = []
    fx, fy, fz = LAMP_FLAME
    for lod in (False, True):
        rng = kc.rng_for("hm_oil_lamp", seed)
        mb = kc.MeshBuilder("hm_oil_lamp" + ("-lod1" if lod else ""))
        drift, lash = mb.material(M_DRIFT), mb.material(M_LASH)
        kc.tube(mb, np.array([[0.0, 0.0, 0.0], [0.0, fy + 0.45, 0.0], [0.0, fy + 0.45, fz]]), 0.03, 4, drift)
        kc.tube(mb, np.array([[fx, fy + 0.45, fz], [fx, fy + 0.12, fz]]), 0.008, 3, lash)  # its hanging cord
        pts = np.stack([np.full(4, fx), fy + np.array([-0.08, -0.04, 0.02, 0.06]), np.full(4, fz)], -1)
        kc.tube(mb, pts, np.array([0.03, 0.08, 0.07, 0.04]), 6 if lod else 10, mb.material(M_CLAY), cap_start=True)
        kc.tube(mb, np.array([[fx, fy + 0.06, fz], [fx, fy + 0.14, fz]]), np.array([0.02, 0.0]), 5,
                mb.material(M_FLAME))
        del rng
        out.append(mb)
    return out


POST_AT = (7.4, 3.1)  # the fender post at the pontoon's outer corner (x, z)
POST_TOP = 1.75
KEEL_MUD_Y = -0.75  # the first hull's keel in the shallows off the pontoon, its rib stubs breaking the water


def _berth(name: str, first: bool, seed: int) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
        timber, drift, tar, lash = mb.material(M_TIMBER), mb.material(M_DRIFT), mb.material(M_TAR), mb.material(M_LASH)
        # The pontoon (Dace's dry-dock's) and the cradle blocks down its centre line, waiting for a keel.
        kc.rounded_block(mb, (0.0, DOCK_TOP - 0.5, 0.0), (8.0, 0.5, 3.5), drift, radius=0.06, seg=1, weather=WOOD,
                         variation=float(rng.random()))
        if not lod:
            for z in np.arange(-3.3, 3.31, 0.55):  # deck seams
                kc.tube(mb, np.array([[-7.9, DOCK_TOP + 0.005, z], [7.9, DOCK_TOP + 0.005, z]]), 0.01, 3, tar)
        for x in np.linspace(-4.5, 4.5, 4):
            h = 0.35 + float(rng.uniform(-0.05, 0.05))
            kc.rounded_block(mb, (x, DOCK_TOP + h * 0.5, 0.0), (0.3, h * 0.5, 0.7), tar, radius=0.02, seg=1)
        # The shear-legs: two poles from the deck's edges, lashed where they cross over the centre line, a block hung.
        head = np.array([-1.0, 6.2, 0.0])
        for sz in (-1.0, 1.0):
            kc.tube(mb, np.array([[-1.0, DOCK_TOP, sz * 3.2], head + [0.0, 0.3, -sz * 0.25]]), np.array([0.11, 0.08]),
                    5 if lod else 7, drift, cap_end=True)
        kc.tube(mb, np.array([head + [0.0, 0.1, 0.0], [-1.0, 3.6, 0.0]]), 0.015, 3, lash)
        kc.rounded_block(mb, (-1.0, 3.45, 0.0), (0.09, 0.15, 0.06), timber, radius=0.03, seg=1)
        if not lod:
            a = np.linspace(0.0, 2.0 * math.pi, 9)
            kc.tube(mb, np.stack([np.full_like(a, -1.0) + np.cos(a) * 0.14, head[1] + np.sin(a) * 0.14,
                                  np.zeros_like(a)], -1), 0.022, 4, lash)
            kc.tube(mb, np.array([head + [0.0, 0.2, 0.0], [-6.5, DOCK_TOP, 0.0]]), 0.012, 3, lash)  # the back-stay
        # The fender post at the outer corner, its foot in the water beside the pontoon.
        px, pz = POST_AT
        kc.tube(mb, np.array([[px, -1.2, pz], [px, POST_TOP, pz]]), np.array([0.16, 0.14]), 6 if lod else 9, drift,
                cap_end=True, weather=WOOD)
        if first:
            # Tobin's post: its top worn pale and smooth where he sat, an old rope coiled at its foot.
            kc.rounded_block(mb, (px, POST_TOP + 0.01, pz), (0.13, 0.025, 0.13), mb.material(M_SAIL), radius=0.02,
                             seg=1 if lod else 2)
            if not lod:
                for k in range(4):
                    a = np.linspace(0.0, 2.0 * math.pi, 13)
                    r = 0.32 - k * 0.05
                    kc.tube(mb, np.stack([px - 0.6 + np.cos(a) * r, np.full_like(a, DOCK_TOP + 0.03 + k * 0.03),
                                          pz - 0.4 + np.sin(a) * r], -1), 0.025, 4, lash)
            # The first hull's rotted keel in the mud off the pontoon's open (-X) end, rib stubs standing from it.
            kc.tube(mb, np.array([[-8.5, KEEL_MUD_Y, 0.3], [-14.0, KEEL_MUD_Y - 0.15, -0.4]]), 0.12, 5 if lod else 7, tar)
            for k in range(2 if lod else 6):
                x = -9.0 - k * 0.9
                lean = float(rng.uniform(-0.25, 0.25))
                for sz in (-1.0, 1.0):
                    kc.tube(mb, np.array([[x, KEEL_MUD_Y, sz * 0.15], [x + lean, KEEL_MUD_Y + float(rng.uniform(0.4, 0.9)),
                                                                   sz * (0.6 + float(rng.uniform(0.0, 0.3)))]]),
                            np.array([0.06, 0.035]), 4, tar)
        out.append(mb)
    return out


def build_drydock_berth(seed: int = 2401) -> list[kc.MeshBuilder]:
    return _berth("hm_drydock_berth", False, seed)


def build_drydock_berth_first(seed: int = 2402) -> list[kc.MeshBuilder]:
    return _berth("hm_drydock_berth_first", True, seed)


TARGETS = {
    "hm_lashed_hulls": build_lashed_hulls,
    "hm_windmill": build_windmill,
    "hm_tide_wheel": build_tide_wheel,
    "hm_signal_lamp": build_signal_lamp,
    "dace_hull_frame": build_dace_hull,
    "hm_far_flotilla": build_far_flotilla,
    "hm_dock_4m": build_dock,
    "hm_dock_4m_open_n": build_dock_open_n,
    "hm_dock_4m_open_s": build_dock_open_s,
    "hm_dock_4m_open_ns": build_dock_open_ns,
    "pyre_raft": build_pyre_raft,
    "hm_ship": build_ship,
    "hm_supper_table": build_supper_table,
    "hm_oil_lamp": build_oil_lamp,
    "hm_drydock_berth": build_drydock_berth,
    "hm_dockmaster_house": build_dockmaster_house,
    "hm_drydock_berth_first": build_drydock_berth_first,
}
