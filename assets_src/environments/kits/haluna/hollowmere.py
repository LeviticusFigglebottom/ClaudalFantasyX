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
  hm_far_flotilla     the rest of the raft-city round the zone: low hull clusters and windmills at 220-460 m.
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
              "hm_signal_lamp": (1500, 150), "dace_hull_frame": (12000, 800), "hm_far_flotilla": (9000, 2500)}

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


def build_lashed_hulls(seed: int = 2301) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("hm_lashed_hulls", seed)
        mb = kc.MeshBuilder("hm_lashed_hulls" + ("-lod1" if lod else ""))
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
        out.append(mb)
    return out


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
        out.append(mb)
    return out


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


TARGETS = {
    "hm_lashed_hulls": build_lashed_hulls,
    "hm_windmill": build_windmill,
    "hm_tide_wheel": build_tide_wheel,
    "hm_signal_lamp": build_signal_lamp,
    "dace_hull_frame": build_dace_hull,
    "hm_far_flotilla": build_far_flotilla,
}
