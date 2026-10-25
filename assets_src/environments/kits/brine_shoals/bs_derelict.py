"""The derelict's deck: the ground of the `derelict_deck_night` battle arena (M3-ENV-06; the arena contract is
docs/kb/tech/battle_arenas.md). Pure numpy; see bs_common.py.

  arena_derelict_deck   a great trader that grounded on the shoals long ago and settled upright on a bar, its
                        stern broken away: the main deck (sun-silvered planks, bs_timber) laid fore and aft at
                        y = 0 over the battle sandbox's slot layout, beams under it and the dark hold below
                        (seen through the seams, a few missing planks and the open hatch), a bulwark with its
                        cap rail along both sides beyond the slots (one stretch stove in), a raised foredeck
                        with two short ladders, and the tarred hull sides (bs_timber_tar) falling to the sea.

Arena coordinates: the origin is the battle sandbox's slot layout, north -Z (the bow), the BattleCamera stands
over the deck at (0.6, 2.8, 8.4) looking forward, so the bulwarks run beside the fight and never cross the
camera's view of it. Nothing on the main deck rises within FLOOR_CLEAR_M of the slots (SLOTS_XZ below mirrors
battle_sandbox.tscn, as the Haluna arena kit's does; tests/unit/test_battle_arenas.gd checks the real scene).
"""

from __future__ import annotations

import math

import numpy as np

import bs_common as bc
from bs_common import kc

TRI_BUDGET = {"arena_derelict_deck": (60000, 8000)}

SLOTS_XZ = ((2.1, 0.7), (3.0, -1.1), (1.4, 2.0), (-2.4, 0.9), (-3.4, -1.2), (-1.2, -0.6))
FLOOR_Y = 0.0
FLOOR_CLEAR_M = 1.0
HALF_BEAM_M = 7.2  # the bulwark's inner face amidships
PLANKED_HALF_M = 6.86  # the deck planking; the covering board fills out to the bulwark
STERN_Z_M = 12.5  # where the broken stern ends (behind the camera)
FOREDECK_Z_M = -12.5  # the foredeck's break
FOREDECK_Y_M = 1.3
BOW_Z_M = -27.0  # the stem
TAPER_FROM_Z_M = -8.0  # the hull narrows forward of this
PLANK_W_M = 0.2
PLANK_GAP_M = 0.014  # the seams (pitch picked out dark: the hold shows through)
PLANK_T_M = 0.07
BEAM_STEP_M = 1.25
HOLD_Y_M = -1.7  # the hold's floor of bilge and silt
RAIL_Y_M = 1.0  # cap rail top above its deck
STANCHION_STEP_M = 1.3
HULL_FOOT_Y_M = -3.2  # the hull sides run down past the sea (ArenaSea at -2.2)
HATCH = (-0.4, -6.9, 1.3, 1.1, 0.45)  # x, z, half x, half z, coaming height: the main hatch, open
STOVE_IN_Z = (-6.6, -3.4)  # the starboard bulwark stretch the sea stove in (no strakes, no cap rail)
CLEAR_OF_SLOTS_M = 1.6  # missing planks keep at least this far from every slot

DECK = kc.Weathering(moss=0.02, salt=0.55, wet=0.08, erosion=0.6, noise_scale_m=0.9)
RAIL = kc.Weathering(moss=0.03, salt=0.6, wet=0.1, erosion=0.8)
HULL = bc.WRECK


def half_beam(z: float) -> float:
    """The bulwark's inner face at z: full amidships, easing in to the stem forward of TAPER_FROM_Z_M."""
    if z >= TAPER_FROM_Z_M:
        return HALF_BEAM_M
    t = (z - TAPER_FROM_Z_M) / (BOW_Z_M - TAPER_FROM_Z_M)
    return HALF_BEAM_M * math.sqrt(max(0.0, 1.0 - min(t, 1.0) ** 2))


def deck_y(z: float) -> float:
    return FOREDECK_Y_M if z < FOREDECK_Z_M else FLOOR_Y


def near_slot(x: float, z0: float, z1: float, margin: float) -> bool:
    """Does the plank line at x, from z0 to z1, pass within `margin` of a slot?"""
    for sx, sz in SLOTS_XZ:
        dz = 0.0 if z0 <= sz <= z1 else min(abs(sz - z0), abs(sz - z1))
        if math.hypot(x - sx, dz) < margin:
            return True
    return False


def _planks(mb: kc.MeshBuilder, rng, noise, z_from: float, z_to: float, y_top: float, *, holes: bool) -> None:
    """Deck planks fore and aft between z_from (forward) and z_to, butts staggered, clipped to the hull's
    outline; with `holes`, a few lengths away from the fight are missing (the hold shows)."""
    i_timber = mb.material(bc.M_TIMBER)
    pitch = PLANK_W_M + PLANK_GAP_M
    n = int(PLANKED_HALF_M * 2.0 / pitch)
    x0 = -n * pitch * 0.5 + pitch * 0.5
    for k in range(n):
        x = x0 + k * pitch
        # The plank runs where the outline clears it; forward of the taper the outer planks stop short.
        z_a = z_from
        while z_a < z_to and half_beam(z_a) - 0.34 < abs(x) + PLANK_W_M * 0.5:
            z_a += 0.25
        cuts = [z_a]
        z = z_a + float(rng.uniform(0.6, 6.0))
        while z < z_to - 0.5:
            cuts.append(z)
            z += float(rng.uniform(4.0, 7.0))
        cuts.append(z_to)
        # The broken stern: each plank ends raggedly.
        end = z_to - (float(rng.uniform(0.0, 2.2)) if z_to >= STERN_Z_M else 0.0)
        for a, b in zip(cuts[:-1], cuts[1:]):
            b = min(b, end)
            if b - a < 0.3:
                continue
            roll = float(rng.random())
            if holes and roll < 0.06 and not near_slot(x, a, b, CLEAR_OF_SLOTS_M):
                continue
            dy = float(rng.uniform(-0.004, 0.0))
            ya = y_top - PLANK_T_M * 0.5 + dy
            kc.plank(mb, (x, ya, b - 0.006), (x, ya, a + 0.006), PLANK_W_M, PLANK_T_M, i_timber, weather=DECK,
                     variation=float(rng.random()), noise=noise)


def _beams(mb: kc.MeshBuilder, rng, z_from: float, z_to: float, y_top: float) -> None:
    i_tar = mb.material(bc.M_TAR)
    z = z_from + BEAM_STEP_M * 0.5
    while z < z_to:
        hw = half_beam(z)
        kc.rounded_block(mb, (0.0, y_top - PLANK_T_M - 0.13, z), (hw, 0.13, 0.11), i_tar, radius=0.03, seg=1,
                         weather=HULL, variation=float(rng.random()))
        z += BEAM_STEP_M


def _hold(mb: kc.MeshBuilder, z_from: float, z_to: float) -> None:
    """The hold's floor: dark silt and bilge under the whole deck (what the seams and holes show)."""
    zs = np.linspace(z_from, z_to, 24)
    rows = []
    for z in zs:
        hw = max(half_beam(float(z)), 0.05)
        rows.append([[x, HOLD_Y_M, z] for x in np.linspace(-hw, hw, 5)])
    grid = np.asarray(rows, float)
    kc.quad_strip(mb, grid, mb.material(bc.M_TAR), uv=grid[..., [0, 2]] / 2.0, col=(0.0, 0.3, 0.9, 0.6),
                  uv2=(0.3, 0.5), flip=True, smooth=False)


def _covering_board(mb: kc.MeshBuilder, rng, noise, side: float, z_from: float, z_to: float, y_top: float) -> None:
    """The broad plank along the deck's edge, under the bulwark, following the hull's line."""
    i_timber = mb.material(bc.M_TIMBER)
    zs = np.arange(z_from, z_to + 1e-6, 1.5)
    for a, b in zip(zs[:-1], zs[1:]):
        xa = side * (half_beam(float(a)) - 0.17)
        xb = side * (half_beam(float(b)) - 0.17)
        kc.plank(mb, (xb, y_top - 0.035, float(b)), (xa, y_top - 0.035, float(a)), 0.36, 0.09, i_timber,
                 weather=RAIL, variation=float(rng.random()), noise=noise)


def _bulwark(mb: kc.MeshBuilder, rng, noise, side: float, z_from: float, z_to: float, y_top: float, *,
             lod: bool) -> None:
    """Stanchions, three inner strakes and the cap rail along one side, the stove-in stretch left open."""
    i_timber = mb.material(bc.M_TIMBER)
    stove = side > 0 and y_top == FLOOR_Y

    def inside(z: float) -> bool:
        return stove and STOVE_IN_Z[0] < z < STOVE_IN_Z[1]

    z = z_from + 0.3
    while z < z_to - 0.2:
        x = side * (half_beam(z) + 0.08)
        top = y_top + RAIL_Y_M
        if inside(z):
            top = y_top + float(rng.uniform(0.25, 0.6))  # snapped stumps
        if lod:
            kc.rounded_block(mb, (x, (y_top + top) * 0.5, z), (0.07, (top - y_top) * 0.5, 0.07), i_timber, seg=1,
                             radius=0.01)
        else:
            kc.tube(mb, np.array([[x, y_top - 0.05, z], [x, top, z]]), 0.075, 4, i_timber, weather=RAIL, noise=noise,
                    disp_m=0.01, variation=float(rng.random()), cap_end=True)
        z += STANCHION_STEP_M
    zs = np.arange(z_from, z_to + 1e-6, 1.0)
    for a, b in zip(zs[:-1], zs[1:]):
        if inside(0.5 * (a + b)):
            continue
        xa = side * (half_beam(float(a)) + 0.18)
        xb = side * (half_beam(float(b)) + 0.18)
        kc.plank(mb, (xb, y_top + RAIL_Y_M + 0.04, float(b)), (xa, y_top + RAIL_Y_M + 0.04, float(a)), 0.26, 0.08,
                 i_timber, weather=RAIL, variation=float(rng.random()), noise=None if lod else noise)
        if lod:
            continue
        for k, h in enumerate((0.16, 0.38, 0.6)):
            if float(rng.random()) < 0.08 * k:  # an upper strake sprung away here and there
                continue
            xa = side * (half_beam(float(a)) + 0.2)
            xb = side * (half_beam(float(b)) + 0.2)
            kc.plank(mb, (xb, y_top + h, float(b)), (xa, y_top + h, float(a)), 0.18, 0.035, i_timber,
                     up=(side, 0.0, 0.0), weather=RAIL, variation=float(rng.random()))


def _hull_side(mb: kc.MeshBuilder, side: float, z_from: float, z_to: float, *, lod: bool) -> None:
    """The tarred hull from the sheer down past the waterline, with a little tumblehome."""
    zs = np.linspace(z_from, z_to, 12 if lod else 48)
    ys = np.linspace(HULL_FOOT_Y_M, 1.0, 4 if lod else 12)
    rows = []
    for z in zs:
        hw = half_beam(float(z)) + 0.3
        sheer = deck_y(float(z)) + RAIL_Y_M + 0.08
        row = []
        for y in ys:
            yy = HULL_FOOT_Y_M + (sheer - HULL_FOOT_Y_M) * (y - HULL_FOOT_Y_M) / (1.0 - HULL_FOOT_Y_M)
            bulge = 0.35 * math.sin(math.pi * (yy - HULL_FOOT_Y_M) / (sheer - HULL_FOOT_Y_M + 1e-6))
            row.append([side * (hw * (0.93 + 0.07 * (yy - HULL_FOOT_Y_M) / 4.0) + bulge * hw / HALF_BEAM_M), yy,
                        float(z)])
        rows.append(row)
    grid = np.asarray(rows, float)
    col = np.stack([np.zeros(grid.shape[:2]), np.full(grid.shape[:2], 0.5), np.full(grid.shape[:2], 0.3),
                    np.full(grid.shape[:2], 0.8)], axis=-1)
    uv = np.stack([grid[..., 2], grid[..., 1]], axis=-1)
    kc.quad_strip(mb, grid, mb.material(bc.M_TAR), uv=uv, col=col, uv2=(0.8, 0.5), flip=side < 0)


def _hatch(mb: kc.MeshBuilder, rng, noise, *, lod: bool) -> None:
    """The open main hatch: a coaming of heavy timbers, two hatch boards still across it, one fallen in."""
    hx, hz, ax, az, h = HATCH
    i_timber = mb.material(bc.M_TIMBER)
    t = 0.12
    sides = ((hx, hz - az, ax + t, t), (hx, hz + az, ax + t, t), (hx - ax, hz, t, az), (hx + ax, hz, t, az))
    for cx, cz, sx, sz in sides:
        kc.rounded_block(mb, (cx, h * 0.5 - 0.05, cz), (sx, h * 0.5 + 0.05, sz), i_timber, radius=0.03,
                         seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.01, weather=RAIL,
                         variation=float(rng.random()))
    if lod:
        return
    for k, z in enumerate((hz - az + 0.35, hz - az + 0.95)):
        kc.plank(mb, (hx + ax + 0.05, h + 0.02, z), (hx - ax - 0.05, h + 0.02, z), 0.5, 0.05, i_timber, weather=DECK,
                 variation=float(rng.random()), noise=noise)
    # One board fallen in, leaning from the coaming down into the hold.
    kc.plank(mb, (hx + 0.4, h - 0.1, hz + az - 0.1), (hx - 0.2, HOLD_Y_M + 0.3, hz + 0.1), 0.5, 0.05, i_timber,
             weather=DECK, variation=0.3, noise=noise)


def _foredeck_front(mb: kc.MeshBuilder, rng, noise, *, lod: bool) -> None:
    """The foredeck's break: a planked face across the beam with two short ladders up to it."""
    i_timber = mb.material(bc.M_TIMBER)
    hw = half_beam(FOREDECK_Z_M)
    z = FOREDECK_Z_M + 0.04
    n = 9 if not lod else 1
    for k in range(n):
        y0 = FOREDECK_Y_M * k / n
        y1 = FOREDECK_Y_M * (k + 1) / n - (0.012 if not lod else 0.0)
        kc.rounded_block(mb, (0.0, 0.5 * (y0 + y1), z), (hw, 0.5 * (y1 - y0), 0.04), i_timber, radius=0.01, seg=1,
                         weather=RAIL, variation=float(rng.random()))
    if lod:
        return
    for lx in (-4.6, 4.6):
        for s in (-0.38, 0.38):
            kc.plank(mb, (lx + s, FOREDECK_Y_M + 0.1, FOREDECK_Z_M - 0.05), (lx + s, 0.0, FOREDECK_Z_M + 0.75),
                     0.07, 0.16, i_timber, up=(1.0, 0.0, 0.0), weather=RAIL, variation=float(rng.random()))
        for k in range(1, 5):
            f = k / 5.0
            kc.plank(mb, (lx - 0.38, FOREDECK_Y_M * f, FOREDECK_Z_M + 0.75 * (1.0 - f)),
                     (lx + 0.38, FOREDECK_Y_M * f, FOREDECK_Z_M + 0.75 * (1.0 - f)), 0.2, 0.05, i_timber,
                     weather=DECK, variation=float(rng.random()), noise=noise)


def _bowsprit(mb: kc.MeshBuilder, noise, *, lod: bool) -> None:
    """The bowsprit's broken stump over the stem and the stem head."""
    i_tar = mb.material(bc.M_TAR)
    a = np.array([0.0, FOREDECK_Y_M + 0.6, BOW_Z_M + 3.0])
    b = np.array([0.0, FOREDECK_Y_M + 2.0, BOW_Z_M - 3.2])
    kc.tube(mb, np.array([a, b]), [0.2, 0.15], 5 if lod else 8, i_tar, weather=HULL, noise=None if lod else noise,
            disp_m=0.02, cap_end=True)
    kc.tube(mb, np.array([[0.0, HULL_FOOT_Y_M, BOW_Z_M - 0.2], [0.0, FOREDECK_Y_M + 1.4, BOW_Z_M - 0.6]]), 0.22,
            5 if lod else 8, i_tar, weather=HULL, cap_end=True)


def build_derelict_deck(seed: int = 611) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("arena_derelict_deck", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("arena_derelict_deck" + ("-lod1" if lod else ""))
        if lod:
            for z0, z1, y in ((FOREDECK_Z_M, STERN_Z_M, FLOOR_Y), (BOW_Z_M + 0.6, FOREDECK_Z_M, FOREDECK_Y_M)):
                zs = np.linspace(z0, z1, 10)
                grid = np.asarray([[[x, y, z] for x in np.linspace(-half_beam(float(z)), half_beam(float(z)), 3)]
                                   for z in zs], float)
                kc.quad_strip(mb, grid, mb.material(bc.M_TIMBER), uv=grid[..., [0, 2]], col=(0.0, 0.5, 0.05, 0.6),
                              uv2=(1.0, 0.5), flip=True, smooth=False)
        else:
            _hold(mb, BOW_Z_M + 1.0, STERN_Z_M)
            _beams(mb, rng, FOREDECK_Z_M, STERN_Z_M, FLOOR_Y)
            _planks(mb, rng, noise, FOREDECK_Z_M, STERN_Z_M, FLOOR_Y, holes=True)
            _planks(mb, rng, noise, BOW_Z_M + 1.2, FOREDECK_Z_M, FOREDECK_Y_M, holes=False)
        for side in (-1.0, 1.0):
            if not lod:
                _covering_board(mb, rng, noise, side, FOREDECK_Z_M, STERN_Z_M - 0.8, FLOOR_Y)
                _covering_board(mb, rng, noise, side, BOW_Z_M + 2.0, FOREDECK_Z_M, FOREDECK_Y_M)
            _bulwark(mb, rng, noise, side, FOREDECK_Z_M, STERN_Z_M - 1.0, FLOOR_Y, lod=lod)
            _bulwark(mb, rng, noise, side, BOW_Z_M + 1.5, FOREDECK_Z_M, FOREDECK_Y_M, lod=lod)
            _hull_side(mb, side, BOW_Z_M + 0.4, STERN_Z_M - 0.5, lod=lod)
        _hatch(mb, rng, noise, lod=lod)
        _foredeck_front(mb, rng, noise, lod=lod)
        _bowsprit(mb, noise, lod=lod)
        out.append(mb)
    return out


TARGETS = {"arena_derelict_deck": build_derelict_deck}
