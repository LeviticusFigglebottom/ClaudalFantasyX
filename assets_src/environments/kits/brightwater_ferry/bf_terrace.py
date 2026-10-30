"""The *Seventh Terrace*, a Pemakar copper coaster (M3-ENV-08B; brightwater_ferry.md §7). Pure numpy; see bf_common.py.

One hero ship for Ch1 (moored and crewed at Oruvel's outer mooring, O07, O13) and Ch4 (the derelict the ferry lies
alongside, C4-11 to C4-14): "build it once" (act1_ch01.md §9). Her hull is the ferry's generator (bf_common.HullForm,
hull_sides, deck_planks, bulwark), so she and the ferry and the drowned read as ships of one sea; her finish is
Pemakar's: black lacquer topsides with a red sheer strake and wale, copper sheathing below the waterline.

  terrace_hull        hull (copper below y COPPER_Y, black lacquer above, the red wale and sheer strake; the red
                      counter planked, framed in a black moulding, copper nail-heads along the wale), flat main
                      deck and poop, covering boards, bulwarks with the two gangways, the open main hatch, the poop's
                      break and ladders, the taffrail, the scuttle, the rudder (its head inside the counter, so nothing
                      crosses the name-board), the stern-lantern post, the bowsprit and stem, windlass and bitts,
                      chain-plates, fife rails, and the name-board's two copper brackets on the transom.
  terrace_wheel       the helm wheel (origin at its axle's centre, the axle along +Z) and its pedestal below, so the
                      zone can turn it ("the wheel turning by itself", C4-11).
  terrace_name_board  the hero name-board (origin at the board's centre on its back face, the carving toward +Z, the
                      long axis X): "Seventh Terrace" in Pemakar terrace script (an original stepped-bar script), red
                      lacquer relief on a black ground in a copper band, a seven-step terrace emblem at each end. The
                      same piece in both chapters; NAME_BOARD_AT places it on the transom.
  terrace_galley      the galley deckhouse (black lacquer boards over a red dado, the door forward, a window a side, an
                      open smoke hatch over the table) with the table and FOUR bowls, the meal half-eaten, the pot and
                      ladle, two benches, the clay stove and its copper pot, the hourglass on its shelf.
  terrace_hold        the hold under the main hatch: the ceiling planking following the hull's sections, the floor,
                      bulkheads, deck beams, the ladder, copper ingots in crossed stacks, crates, and on its shelf the
                      Lit Age lamp-housing Rhen sold her skipper (dead: no glimmer).
  terrace_moored      Ch1's crewed dressing: bow and stern lines and spring to the stage raft (STAGE_AT), the anchor
                      cable forward, rope fenders on the stage side, the gangplank, salvage on deck (crates, a coil, a
                      basket of brass, the lamp-housing before it went below).
  terrace_derelict    Ch4's three-days-drowned dressing: a capsized bucket, a slack sheet across the deck, a spilled
                      coil, the hatch tarpaulin torn and thrown back, a fallen stool by the galley door.
  alongside_gear      in the FERRY's frame (bf_hull's): four rope fenders outside her port bulwark and three boathooks
                      laid across the gap to the derelict's cap rail (the derelict at DERELICT_IN_FERRY). Nothing
                      ties the hulls together (sea-law: never lash a living hull to a drowned one).

The ship's frame: bow to -Z, origin on the centre line at main-deck level amidships, the waterline at y WATERLINE_Y.
Walkable: the main deck at y 0, the poop at y POOP_Y, the hold's floor at HOLD_FLOOR_Y, the galley's floor is the
main deck (WALK lists the boxes for m2-slice's collision).
"""

from __future__ import annotations

import math

import numpy as np

import bf_common as bf
from bf_common import kc

TRI_BUDGET = {"terrace_hull": (40000, 4000), "terrace_wheel": (2500, 300), "terrace_name_board": (8000, 800),
              "terrace_galley": (10000, 1000), "terrace_hold": (10000, 1000), "terrace_moored": (8000, 800),
              "terrace_derelict": (6000, 600), "alongside_gear": (4000, 400)}

# ---------------------------------------------------------------------------------------------
# Her frame (brightwater_ferry.md §7.1)
# ---------------------------------------------------------------------------------------------
WATERLINE_Y = -1.5
COPPER_Y = -1.15  # the sheathing's top: 0.35 m above the waterline
POOP_Z = 5.2
POOP_Y = 1.0
GANGWAY_Z = (0.9, 1.9)
FORM = bf.HullForm(stem_z=-11.0, transom_z=10.0, half_beam=3.0, taper_fwd_z=-4.0, taper_aft_z=5.5, transom_half=2.3,
                   keel_y=-2.2, poop_z=POOP_Z, poop_y=POOP_Y, bow_rise=1.6, sheer_sag=0.36, forefoot_m=2.2,
                   wale_y=COPPER_Y, gangways=(GANGWAY_Z,))
RED_WALE_Y = -0.45
FOREMAST_Z = -6.8
MAINMAST_Z = -0.6
FOREMAST_H = 11.0
MAINMAST_H = 14.0
MAIN_HATCH = (0.0, -3.6, 0.9, 0.8, 0.42)  # x, z, half x, half z, coaming height
HOLD_Z = (-5.4, -1.8)
HOLD_FLOOR_Y = -1.9
HOUSING_SHELF = (-0.1, -1.3, -1.98)  # on the hold's after bulkhead, in view down the hatch
GALLEY = (-1.6, 1.6, 2.4, 5.0, 2.0)  # x0, x1, z0, z1, wall height
GALLEY_DOOR = (-0.42, 0.42, 1.8)
GALLEY_WINDOW_Z = (3.3, 4.1)
GALLEY_WINDOW_Y = (1.05, 1.6)
SMOKE_HATCH = (0.0, 3.85, 0.42, 0.4)  # x, z, half x, half z: open over the table
TABLE = (0.0, 3.85, 0.95, 0.36, 0.76)  # x, z, half x, half z, top height
BOWLS = ((-0.62, 3.68), (-0.2, 4.02), (0.24, 3.7), (0.66, 4.0))  # the crew's four places
WHEEL_AT = (0.0, POOP_Y + 1.02, 7.0)  # the axle's centre
WHEEL_R = 0.56
LADDER_X = 2.15
LADDER_HALF_W = 0.28
STERN_POST = (-1.55, 9.55)
STERN_POST_H = 2.0
WINDLASS_Z = -9.2
BOWSPRIT_X = 0.3
SHROUD_LEAD_M = bf.SHROUD_LEAD_M
# The name-board on the transom: its back face against the brackets, centre height above the main deck.
NAME_BOARD_HALF = (1.3, 0.22)
NAME_BOARD_T = 0.06
NAME_BOARD_AT = (0.0, 0.95, FORM.transom_z + 0.035)
# O07 and D06 (brightwater_ferry.md §7.4): the same eye and target in the ship's frame, so the two inserts match.
INSERT_EYE = (0.6, NAME_BOARD_AT[1] - 0.25, NAME_BOARD_AT[2] + 9.0)
INSERT_TARGET = (0.0, NAME_BOARD_AT[1], NAME_BOARD_AT[2])
INSERT_FOV = 16.1  # 85 mm
# Ch1: the stage raft she lies against at Oruvel (an Oruvel kit raft_deck_small, its long side along her), on her
# starboard side; its deck top in her frame is STAGE_DECK_Y (the Oruvel raft's deck height above the sea, less her
# freeboard).
STAGE_SIDE = 1.0
STAGE_AT = (STAGE_SIDE * 6.67, 1.4)  # x, z of the raft's centre
STAGE_YAW = 0.0
STAGE_HALF = (3.0, 2.5)  # half extents across and along her (the raft's local x and z: its hulls lie along hers)
STAGE_DECK_ABOVE_SEA = 0.70  # ov_hulls.RAFT_SMALL_Y
STAGE_DECK_Y = WATERLINE_Y + STAGE_DECK_ABOVE_SEA
# Ch4: where the derelict lies in the ferry's frame (an oar's length off her port side, both heading north).
GAP_M = 2.4
DERELICT_IN_FERRY = (-(3.4 + 0.22) - GAP_M - (FORM.half_beam + FORM.bulwark_t), bf.WATERLINE_Y - WATERLINE_Y, 1.0)
# Walkable boxes for m2-slice's collision (x0, x1, y_top, z0, z1), ship frame.
WALK = (("main_deck", -2.6, 2.6, 0.0, FORM.stem_z + 1.6, POOP_Z), ("poop", -2.1, 2.1, POOP_Y, POOP_Z, FORM.transom_z - 0.3),
        ("hold_floor", -1.4, 1.4, HOLD_FLOOR_Y, HOLD_Z[0] + 0.1, HOLD_Z[1] - 0.1))

LACQUER_W = kc.Weathering(moss=0.0, salt=0.1, wet=0.1, erosion=0.12)  # lacquer is kept up: little salt or wear
COPPER_W = kc.Weathering(moss=0.0, salt=0.55, wet=0.4, erosion=0.45)
HOLD_W = kc.Weathering(moss=0.0, salt=0.15, wet=0.1, erosion=0.3)

# Slots (bf_materials.py writes them; brightwater_ferry.md §7.3).
M_LACQUER = "bf_lacquer_black"
M_LACQUER_SATIN = "bf_lacquer_black_satin"  # the galley's board walls (indoors)
M_LACQUER_RED = "bf_lacquer_red_deep"  # the counter and the galley dado; the strakes and glyphs are bf_lacquer_red
M_COPPER = "bf_copper_sheathing"
M_COPPER_BRIGHT = "bf_copper_bright"
M_CERAMIC = "bf_ceramic"
M_RICE = "bf_rice"


# ---------------------------------------------------------------------------------------------
# Hull
# ---------------------------------------------------------------------------------------------
def hatch_keep_out() -> list[tuple[float, float, float, float]]:
    hx, hz, ax, az, _h = MAIN_HATCH
    return [(hx - ax - 0.12, hx + ax + 0.12, hz - az - 0.12, hz + az + 0.12)]


def _strake(mb: kc.MeshBuilder, rng, y_of, width: float, thick: float, mat: str, z0: float, z1: float, *,
            lod: bool, out: float = 0.03) -> None:
    """A strake (rubbing strake, sheer strake) along both sides at height y_of(z), on the hull's surface."""
    i = mb.material(mat)
    zs = bf.rows_between(z0, z1, 2.0 if lod else 0.8)
    for side in (-1.0, 1.0):
        for a, b in zip(zs[:-1], zs[1:]):
            a, b = float(a), float(b)
            if FORM.in_gangway(0.5 * (a + b)) and y_of(a) > 0.1:
                continue
            ya, yb = float(y_of(a)), float(y_of(b))
            xa = side * (float(FORM.section_x(a, np.array(ya))) + out)
            xb = side * (float(FORM.section_x(b, np.array(yb))) + out)
            kc.plank(mb, (xb, yb, b), (xa, ya, a), width, thick, i, up=(side, 0.0, 0.0), weather=LACQUER_W,
                     variation=float(rng.random()))


def _sheer_strake_y(z: float) -> float:
    """The red sheer strake: just under the planking's top (the cap rail sits on it)."""
    if z >= POOP_Z - 0.05:
        return float(FORM.sheer_y(z)) - 0.14
    return float(FORM.sheer_y(z)) - 0.12


def _transom_banded(mb: kc.MeshBuilder, *, lod: bool) -> None:
    """The flat transom: copper below COPPER_Y, black lacquer to the red wale, and above it the counter in deep red
    lacquer, so the black name-board stands out on it; each band a grid across the section outline, facing aft
    (bf_common._surface picks the winding from the grid)."""
    z = FORM.transom_z
    top = float(FORM.sheer_y(z))
    for y0, y1, mat in ((FORM.keel_y, COPPER_Y, M_COPPER), (COPPER_Y, RED_WALE_Y, M_LACQUER),
                        (RED_WALE_Y, top, M_LACQUER_RED)):
        ys = np.linspace(y0, y1, 3 if lod else 8)
        xs = FORM.section_x(z, ys)
        t = np.linspace(-1.0, 1.0, 3 if lod else 9)
        grid = np.asarray([[[float(x) * float(s), float(y), z] for s in t] for x, y in zip(xs, ys)])
        col = (0.0, 0.45, 0.35, 0.4) if mat == M_COPPER else (0.0, 0.1, 0.05, 0.1)
        bf._surface(mb, grid, mb.material(mat), outward=np.array([0.0, 0.0, 1.0]), uv=grid[..., [0, 1]], col=col,
                    uv2=(0.8, 0.5))
    if not lod:
        _counter_trim(mb)


COUNTER_PLANK_M = 0.24  # the counter's planking, seam to seam


def _counter_trim(mb: kc.MeshBuilder) -> None:
    """The counter's finish (M3-ENV-705: O07 read it as one flat red wall): the planks' seams across it, a black
    lacquer moulding framing it inside its edges, and a row of copper nail-heads along the wale. Everything stands
    proud of the transom by millimetres, behind the name-board's brackets."""
    z = FORM.transom_z
    top = float(FORM.sheer_y(z))
    black, copper = mb.material(M_LACQUER), mb.material(M_COPPER_BRIGHT)
    for y in np.arange(RED_WALE_Y + COUNTER_PLANK_M, top - 0.1, COUNTER_PLANK_M):
        hw = float(FORM.section_x(z, np.array([y]))[0]) - 0.04
        kc.rounded_block(mb, (0.0, float(y), z + 0.003), (hw, 0.006, 0.003), black, radius=0.002, seg=1,
                         weather=LACQUER_W, variation=0.2)
    inset = 0.14
    ys = np.linspace(RED_WALE_Y + inset, top - inset, 9)
    xs = FORM.section_x(z, ys) - inset
    for side in (-1.0, 1.0):  # the moulding's sides follow the section, its top and bottom run straight across
        pts = np.stack([xs * side, ys, np.full_like(ys, z + 0.012)], -1)
        kc.tube(mb, pts, 0.022, 4, black, weather=LACQUER_W)
    for y, x in ((ys[0], xs[0]), (ys[-1], xs[-1])):
        kc.tube(mb, np.array([[-x, y, z + 0.012], [x, y, z + 0.012]]), 0.022, 4, black, weather=LACQUER_W)
    hw = float(FORM.section_x(z, np.array([RED_WALE_Y + 0.05]))[0]) - 0.08
    for x in np.linspace(-hw, hw, 17):
        if abs(x) < 0.2:  # the rudder's stock crosses the transom there
            continue
        kc.rounded_block(mb, (float(x), RED_WALE_Y + 0.06, z + 0.008), (0.014, 0.014, 0.008), copper, radius=0.006,
                         seg=1)


def _hatch(mb: kc.MeshBuilder, rng, *, lod: bool) -> None:
    """The main hatch: a tarred coaming, open, the hatch boards stacked beside it."""
    hx, hz, ax, az, h = MAIN_HATCH
    i_tar = mb.material(bf.M_TAR)
    t = 0.12
    for cx, cz, sx, sz in ((hx, hz - az, ax + t, t), (hx, hz + az, ax + t, t), (hx - ax, hz, t, az), (hx + ax, hz, t, az)):
        kc.rounded_block(mb, (cx, h * 0.5 - 0.1, cz), (sx, h * 0.5 + 0.1, sz), i_tar, radius=0.03, seg=1 if lod else 2,
                         weather=bf.RAIL_W, variation=float(rng.random()))
    if lod:
        return
    # The hatch boards, stacked on the deck to starboard of the coaming.
    i_t = mb.material(bf.M_TIMBER)
    for k in range(5):
        kc.rounded_block(mb, (hx + ax + 0.75, 0.035 + k * 0.062, hz + (k % 2) * 0.03 - 0.015), (0.28, 0.028, az + 0.08),
                         i_t, radius=0.01, seg=1, weather=bf.RAIL_W, variation=float(rng.random()))


def _poop_break(mb: kc.MeshBuilder, rng, noise, *, lod: bool) -> None:
    """The poop's planked front with its ladders either side of the galley, and the breast rails."""
    i_t, i_l = mb.material(bf.M_TIMBER), mb.material(M_LACQUER)
    hw = float(FORM.half_beam_at(POOP_Z))
    z = POOP_Z + 0.04
    n = 1 if lod else 5
    for k in range(n):
        y0 = POOP_Y * k / n
        y1 = POOP_Y * (k + 1) / n - (0.0 if lod else 0.012)
        kc.rounded_block(mb, (0.0, 0.5 * (y0 + y1), z), (hw, 0.5 * (y1 - y0), 0.04), i_l, radius=0.01, seg=1,
                         weather=LACQUER_W, variation=float(rng.random()))
    for lx in (-LADDER_X, LADDER_X):
        for s in (-LADDER_HALF_W, LADDER_HALF_W):
            kc.plank(mb, (lx + s, POOP_Y + 0.08, POOP_Z - 0.02), (lx + s, 0.0, POOP_Z - 0.6), 0.06, 0.15, i_t,
                     up=(1.0, 0.0, 0.0), weather=bf.RAIL_W, variation=float(rng.random()))
        if lod:
            continue
        for k in range(1, 4):
            f = k / 4.0
            kc.plank(mb, (lx - LADDER_HALF_W, POOP_Y * f, POOP_Z - 0.58 * (1.0 - f)),
                     (lx + LADDER_HALF_W, POOP_Y * f, POOP_Z - 0.58 * (1.0 - f)), 0.18, 0.045, mb.material(bf.M_DECK),
                     weather=bf.DECK_W, variation=float(rng.random()), noise=noise)
    top = POOP_Y + bf.RAIL_H
    gx = GALLEY[1] + 0.02
    spans = ((-hw, -LADDER_X - LADDER_HALF_W - 0.05), (-LADDER_X + LADDER_HALF_W + 0.05, -gx),
             (gx, LADDER_X - LADDER_HALF_W - 0.05), (LADDER_X + LADDER_HALF_W + 0.05, hw))
    for x0, x1 in spans:
        if x1 - x0 < 0.1:
            continue
        kc.plank(mb, (x0, top, POOP_Z + 0.08), (x1, top, POOP_Z + 0.08), 0.12, 0.06, i_t, weather=bf.RAIL_W,
                 variation=float(rng.random()))
        for x in np.linspace(x0 + 0.05, x1 - 0.05, max(2, int((x1 - x0) / 0.9) + 1)):
            kc.rounded_block(mb, (float(x), POOP_Y + bf.RAIL_H * 0.5, POOP_Z + 0.08), (0.035, bf.RAIL_H * 0.5, 0.035),
                             i_t, radius=0.01, seg=1)


def _taffrail(mb: kc.MeshBuilder, rng, *, lod: bool) -> None:
    """The transom's inner face above the poop, the cap rail and the open taffrail on posts."""
    i_t = mb.material(bf.M_TIMBER)
    z = FORM.transom_z - 0.06
    hw = float(FORM.half_beam_at(z)) + 0.02
    top = float(FORM.sheer_y(z))
    rail = float(FORM.rail_y(z))
    kc.rounded_block(mb, (0.0, (POOP_Y + top) * 0.5, z), (hw, (top - POOP_Y) * 0.5, 0.05), mb.material(M_LACQUER),
                     radius=0.015, seg=1, weather=LACQUER_W, variation=float(rng.random()))
    kc.plank(mb, (-hw - 0.08, rail + 0.03, z + 0.03), (hw + 0.08, rail + 0.03, z + 0.03), 0.3, 0.07, i_t,
             weather=bf.RAIL_W, variation=float(rng.random()))
    for x in np.linspace(-hw + 0.1, hw - 0.1, 3 if lod else 7):
        kc.rounded_block(mb, (float(x), (top + rail) * 0.5, z), (0.04, (rail - top) * 0.5, 0.04), i_t, radius=0.01, seg=1)
    if not lod:
        kc.plank(mb, (-hw, (top + rail) * 0.5, z), (hw, (top + rail) * 0.5, z), 0.08, 0.05, i_t, weather=bf.RAIL_W,
                 variation=float(rng.random()))


def _rudder(mb: kc.MeshBuilder, *, lod: bool) -> None:
    """The rudder hung on the transom below the counter (its stock enters the hull at RUDDER_HEAD_Y, so nothing
    crosses the name-board), with its gudgeons."""
    zr = FORM.transom_z + 0.2
    head = -0.35
    kc.rounded_block(mb, (0.0, (FORM.keel_y + head) * 0.5, zr + 0.32), (0.08, (head - FORM.keel_y) * 0.5, 0.42),
                     mb.material(M_COPPER), radius=0.04, seg=1 if lod else 2, weather=COPPER_W, variation=0.4)
    kc.tube(mb, np.array([[0.0, FORM.keel_y + 0.1, zr], [0.0, head + 0.25, zr], [0.0, head + 0.4, FORM.transom_z - 0.05]]),
            0.1, 6 if lod else 10, mb.material(bf.M_TIMBER), weather=bf.RAIL_W, cap_end=True)
    if not lod:
        for y in (-1.8, -1.1, -0.5):
            kc.rounded_block(mb, (0.0, y, FORM.transom_z + 0.1), (0.12, 0.04, 0.13), mb.material(bf.M_IRON), radius=0.01,
                             seg=1)


def _brackets(mb: kc.MeshBuilder, *, lod: bool) -> None:
    """The name-board's two copper brackets on the transom (they stay when the board is taken off)."""
    i = mb.material(M_COPPER_BRIGHT)
    bx, by, bz = NAME_BOARD_AT
    for sx in (-1.0, 1.0):
        x = bx + sx * (NAME_BOARD_HALF[0] - 0.3)
        kc.rounded_block(mb, (x, by - NAME_BOARD_HALF[1] - 0.02, FORM.transom_z + 0.06), (0.05, 0.015, 0.07), i,
                         radius=0.004, seg=1)
        kc.rounded_block(mb, (x, by, FORM.transom_z + 0.016), (0.04, NAME_BOARD_HALF[1] + 0.03, 0.016), i, radius=0.004,
                         seg=1)
        if not lod:
            for y in (by - 0.18, by + 0.18):
                kc.tube(mb, np.array([[x, y, FORM.transom_z + 0.03], [x, y, FORM.transom_z + 0.045]]), 0.014, 6, i,
                        cap_end=True)


def _crook(mb: kc.MeshBuilder, base, height: float, reach, *, lod: bool) -> None:
    i_t = mb.material(bf.M_TIMBER)
    base = np.asarray(base, float)
    top = base + np.array([0.0, height - 0.25, 0.0])
    t = np.linspace(0.0, 1.0, 4 if lod else 9)
    ang = t * math.pi * 0.5
    crook = top[None, :] + np.stack([reach[0] * np.sin(ang), 0.25 * np.sin(ang) - 0.2 * t ** 2, reach[1] * np.sin(ang)], -1)
    kc.tube(mb, np.vstack([[base - np.array([0.0, 0.05, 0.0])], crook]), 0.05, 5 if lod else 8, i_t, weather=bf.RAIL_W,
            cap_end=True)


def _bow(mb: kc.MeshBuilder, rng, noise, *, lod: bool) -> None:
    """The stem post, the bowsprit, a red-lacquered stem cap, the windlass and its bitts."""
    i_t = mb.material(bf.M_TIMBER)
    sz = FORM.stem_z
    head_y = float(FORM.sheer_y(sz + 0.1))
    ys = np.linspace(FORM.keel_y + 0.05, head_y, 3 if lod else 8)
    zs = sz + 0.03 + FORM.forefoot_dz(sz + 0.03, ys)
    stem = np.stack([np.zeros_like(ys), ys, zs], -1)
    stem = np.vstack([stem, [[0.0, head_y + 0.45, sz - 0.18]]])
    kc.tube(mb, stem, 0.15, 5 if lod else 8, mb.material(M_LACQUER), weather=LACQUER_W, cap_end=True)
    # A copper cap on the stem head, and its red-lacquered cheeks.
    kc.tube(mb, np.array([[0.0, head_y + 0.28, sz - 0.1], [0.0, head_y + 0.5, sz - 0.2]]), [0.17, 0.12], 6 if lod else 10,
            mb.material(M_COPPER_BRIGHT), cap_start=True, cap_end=True)
    a = np.array([BOWSPRIT_X, head_y - 0.05, sz + 1.5])
    b = np.array([BOWSPRIT_X, head_y + 0.9, sz - 3.2])
    kc.tube(mb, np.array([a, b]), [0.15, 0.1], 6 if lod else 10, i_t, weather=bf.RAIL_W, noise=None if lod else noise,
            disp_m=0.006, cap_end=True)
    if lod:
        return
    for x in (-0.6, 0.6):
        kc.rounded_block(mb, (x, 0.42, sz + 1.9), (0.11, 0.42, 0.12), i_t, radius=0.03, seg=2, weather=bf.RAIL_W,
                         variation=float(rng.random()))
    for x in (-0.9, 0.9):
        kc.rounded_block(mb, (x, 0.42, WINDLASS_Z), (0.12, 0.42, 0.14), i_t, radius=0.03, seg=2, weather=bf.RAIL_W,
                         variation=float(rng.random()))
    kc.tube(mb, np.array([[-0.8, 0.4, WINDLASS_Z], [0.8, 0.4, WINDLASS_Z]]), 0.15, 10, i_t, weather=bf.RAIL_W,
            cap_start=True, cap_end=True)
    for x in (-0.45, 0.45):
        kc.tube(mb, np.array([[x, 0.4, WINDLASS_Z], [x, 0.4, WINDLASS_Z + 0.001]]), 0.18, 10, mb.material(M_COPPER_BRIGHT),
                cap_start=True, cap_end=True)


def _chain_plates(mb: kc.MeshBuilder, *, lod: bool) -> None:
    """Copper straps down the topsides under each shroud, with the deadeye at the top."""
    i_c = mb.material(M_COPPER_BRIGHT)
    for mz in (FOREMAST_Z, MAINMAST_Z):
        for side in (-1.0, 1.0):
            for p in bf.chain_points(FORM, mz, side):
                z = float(p[2])
                x_lo = side * (float(FORM.section_x(z, np.array(RED_WALE_Y + 0.1))) + 0.04)
                strap = np.array([[x_lo, RED_WALE_Y + 0.1, z], [p[0], p[1] - 0.12, z]])
                if lod:
                    kc.tube(mb, strap, 0.03, 3, i_c)
                    continue
                kc.plank(mb, strap[0], strap[1], 0.07, 0.025, i_c, up=(side, 0.0, 0.0), weather=bf.IRON_W)
                bf.lathe(mb, p - np.array([0.0, 0.07, 0.0]), [(0.06, 0.0), (0.085, 0.03), (0.085, 0.11), (0.06, 0.14)], 8,
                         bf.M_TIMBER, weather=bf.RAIL_W)


def _fife_rails(mb: kc.MeshBuilder, rng, *, lod: bool) -> None:
    i_t = mb.material(bf.M_TIMBER)
    for mz, dz in ((FOREMAST_Z, 0.7), (MAINMAST_Z, -0.7)):
        z = mz + dz
        for x in (-0.55, 0.55):
            kc.rounded_block(mb, (x, 0.4, z), (0.06, 0.4, 0.06), i_t, radius=0.015, seg=1, weather=bf.RAIL_W,
                             variation=float(rng.random()))
        kc.rounded_block(mb, (0.0, 0.78, z), (0.66, 0.04, 0.07), i_t, radius=0.015, seg=1, weather=bf.RAIL_W,
                         variation=float(rng.random()))
        if lod:
            continue
        for x in np.linspace(-0.42, 0.42, 5):
            kc.tube(mb, np.array([[float(x), 0.68, z], [float(x), 0.95, z]]), 0.018, 5, i_t, cap_end=True)


def _sub_deck_holed(mb: kc.MeshBuilder, z_from: float, z_to: float, y: float) -> None:
    """The dark caulking under the main deck's planks, open over the main hatch (the hold shows through)."""
    _hx, hz, ax, az, _h = MAIN_HATCH
    z0, z1 = hz - az, hz + az
    for a, b in ((z_from, z0), (z1, z_to)):
        bf.sub_deck(mb, FORM, a, b, y, bf.M_TAR)
    for side in (-1.0, 1.0):
        zs = bf.rows_between(z0, z1, 0.8)
        rows = []
        for z in zs:
            hw = max(float(FORM.half_beam_at(float(z))) - 0.05, ax + 0.1)
            xa, xb = (ax, hw) if side > 0 else (-hw, -ax)
            rows.append([[x, y, float(z)] for x in np.linspace(xa, xb, 2)])
        grid = np.asarray(rows, float)
        bf._surface(mb, grid, mb.material(bf.M_TAR), outward=kc.UP, uv=grid[..., [0, 2]], col=(0.0, 0.2, 0.0, 0.3),
                    uv2=(0.4, 0.5), smooth=False)


def build_hull(seed: int = 9101) -> list[kc.MeshBuilder]:
    out = []
    f = FORM
    for lod in (False, True):
        rng = kc.rng_for("terrace_hull", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("terrace_hull" + (bf.LOD if lod else ""))
        bf.hull_sides(mb, f, lod=lod, tar=M_COPPER, paint=M_LACQUER, noise=noise, weather=LACQUER_W)
        _transom_banded(mb, lod=lod)
        _strake(mb, rng, lambda z: RED_WALE_Y, 0.13, 0.07, bf.M_RED, f.stem_z + 0.7, f.transom_z - 0.05, lod=lod)
        _strake(mb, rng, _sheer_strake_y, 0.2, 0.045, bf.M_RED, f.stem_z + 1.2, f.transom_z - 0.05, lod=lod,
                out=0.012)
        keep = hatch_keep_out()
        if lod:
            for z0, z1, y in ((f.stem_z + 1.0, POOP_Z, 0.0), (POOP_Z, f.transom_z - 0.1, POOP_Y)):
                zs = bf.rows_between(z0, z1, 2.0)
                grid = np.asarray([[[x, y, float(z)] for x in np.linspace(-float(f.half_beam_at(float(z))),
                                                                        float(f.half_beam_at(float(z))), 3)] for z in zs])
                kc.quad_strip(mb, grid, mb.material(bf.M_DECK), uv=grid[..., [0, 2]], col=(0.0, 0.3, 0.0, 0.4),
                              uv2=(1.0, 0.5), flip=True, smooth=False)
        else:
            _sub_deck_holed(mb, f.stem_z + 0.8, POOP_Z, -bf.PLANK_T_M - 0.005)
            bf.sub_deck(mb, f, POOP_Z, f.transom_z - 0.05, POOP_Y - bf.PLANK_T_M - 0.005, bf.M_TAR)
            bf.deck_planks(mb, f, rng, noise, f.stem_z + 1.0, POOP_Z, 0.0, mat=bf.M_DECK, keep_out=keep)
            bf.deck_planks(mb, f, rng, noise, POOP_Z + 0.08, f.transom_z - 0.1, POOP_Y, mat=bf.M_DECK)
            for side in (-1.0, 1.0):
                bf.covering_board(mb, f, rng, noise, side, f.stem_z + 1.6, POOP_Z - 0.05, mat=bf.M_TIMBER)
                bf.covering_board(mb, f, rng, noise, side, POOP_Z + 0.05, f.transom_z - 0.1, mat=bf.M_TIMBER)
        for side in (-1.0, 1.0):
            bf.bulwark(mb, f, rng, noise, side, f.stem_z + 1.3, POOP_Z - 0.02, lod=lod, timber=bf.M_TIMBER,
                       lining=M_LACQUER, weather=LACQUER_W)
            bf.bulwark(mb, f, rng, noise, side, POOP_Z + 0.02, f.transom_z - 0.12, lod=lod, timber=bf.M_TIMBER,
                       lining=M_LACQUER, weather=LACQUER_W)
        _poop_break(mb, rng, noise, lod=lod)
        _taffrail(mb, rng, lod=lod)
        _hatch(mb, rng, lod=lod)
        _rudder(mb, lod=lod)
        _brackets(mb, lod=lod)
        _crook(mb, (STERN_POST[0], POOP_Y, STERN_POST[1]), STERN_POST_H, (0.0, -0.5), lod=lod)
        _bow(mb, rng, noise, lod=lod)
        _chain_plates(mb, lod=lod)
        _fife_rails(mb, rng, lod=lod)
        if not lod:
            # The poop scuttle, starboard of the wheel.
            kc.rounded_block(mb, (1.2, POOP_Y + 0.15, 8.3), (0.4, 0.15, 0.36), mb.material(bf.M_TAR), radius=0.03, seg=2,
                             weather=bf.RAIL_W, variation=0.3)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# The wheel (its own piece, so the zone can turn it)
# ---------------------------------------------------------------------------------------------
def build_wheel(seed: int = 9111) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("terrace_wheel", seed)
        mb = kc.MeshBuilder("terrace_wheel" + (bf.LOD if lod else ""))
        i_t = mb.material(bf.M_TIMBER)
        n = 8
        ang = np.linspace(0.0, 2.0 * math.pi, (12 if lod else 33))
        rim = np.stack([np.cos(ang) * WHEEL_R, np.sin(ang) * WHEEL_R, np.zeros_like(ang)], -1)
        kc.tube(mb, rim, 0.035, 4 if lod else 6, i_t, weather=bf.RAIL_W)
        for k in range(n):
            a = 2.0 * math.pi * k / n
            d = np.array([math.cos(a), math.sin(a), 0.0])
            kc.tube(mb, np.array([d * 0.08, d * (WHEEL_R + (0.0 if lod else 0.2))]), [0.03, 0.022], 4 if lod else 6, i_t,
                    weather=bf.RAIL_W, cap_end=True)
        bf.lathe(mb, (0.0, 0.0, -0.1), [(0.0, 0.0), (0.1, 0.0), (0.12, 0.05), (0.12, 0.15), (0.1, 0.2), (0.0, 0.2)],
                 6 if lod else 12, M_COPPER_BRIGHT, axis=(0.0, 0.0, 1.0))
        # The pedestal and its box, standing on the poop (below the axle).
        drop = WHEEL_AT[1] - POOP_Y
        kc.rounded_block(mb, (0.0, -drop * 0.5 - 0.05, -0.32), (0.22, drop * 0.5 - 0.05, 0.26), mb.material(M_LACQUER),
                         radius=0.02, seg=1 if lod else 2, weather=LACQUER_W, variation=float(rng.random()))
        kc.tube(mb, np.array([[0.0, 0.0, -0.06], [0.0, 0.0, -0.3]]), 0.05, 6, mb.material(M_COPPER_BRIGHT), cap_end=True)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# The name-board: Pemakar terrace script (an original stepped-bar script; brightwater_ferry.md §7)
# ---------------------------------------------------------------------------------------------
# Each glyph is a little terraced hill on a 1 x 1 cell: a base line, then a stepped profile (the height of each
# terrace, left to right, in quarters of the cell) drawn as level bars joined by risers, and 0-2 marks (dots) above
# it. The first word is "seventh" (the numeral, a stair of seven treads, and its ordinal sign), the second
# "terrace" (the terrace sign twice, and its ending). An original script: no letter of any real alphabet.
GLYPHS: dict[str, tuple] = {
    "seven": ((1, 1, 2, 2, 3, 3, 4), ()),
    "ordinal": ((3, 2, 1), ((0.18, 1.0),)),
    "terrace_a": ((1, 2, 3, 2, 1), ()),
    "terrace_b": ((1, 3, 3, 1), ((0.5, 1.0),)),
    "ending": ((2, 1, 2), ((0.2, 1.0), (0.8, 1.0))),
}
NAME_WORDS = (("seven", "ordinal"), ("terrace_a", "terrace_b", "ending"))
GLYPH_W = 0.2
GLYPH_H = 0.26
GLYPH_GAP = 0.065
WORD_GAP = 0.2
BAR_W = 0.034
RELIEF = 0.016


def name_glyph_cells() -> list[tuple[str, float]]:
    """(glyph, x of its cell's left edge) across the board, centred."""
    widths = []
    for word in NAME_WORDS:
        widths.append(len(word) * GLYPH_W + (len(word) - 1) * GLYPH_GAP)
    total = sum(widths) + WORD_GAP * (len(NAME_WORDS) - 1)
    x = -total * 0.5
    out = []
    for word, w in zip(NAME_WORDS, widths):
        for k, g in enumerate(word):
            out.append((g, x + k * (GLYPH_W + GLYPH_GAP)))
        x += w + WORD_GAP
    return out


def _relief_bar(mb: kc.MeshBuilder, x0: float, y0: float, x1: float, y1: float, z: float, mat: int, *, lod: bool,
                rng) -> None:
    c = ((x0 + x1) * 0.5, (y0 + y1) * 0.5, z + RELIEF * 0.5)
    half = (max((x1 - x0) * 0.5, BAR_W * 0.5), max((y1 - y0) * 0.5, BAR_W * 0.5), RELIEF * 0.5 + 0.002)
    kc.rounded_block(mb, c, half, mat, radius=0.005, seg=1 if lod else 2, weather=LACQUER_W,
                     variation=float(rng.random()))


def _glyph(mb: kc.MeshBuilder, name: str, x_left: float, y_bottom: float, z: float, mat: int, *, lod: bool, rng) -> None:
    """One glyph: the base line, the stepped profile (bars and risers) and its marks, all in relief."""
    profile, marks = GLYPHS[name]
    hb = BAR_W * 0.5
    top_h = GLYPH_H - BAR_W * 2.2  # the marks sit above the highest terrace
    n = len(profile)
    _relief_bar(mb, x_left - hb, y_bottom, x_left + GLYPH_W + hb, y_bottom + BAR_W, z, mat, lod=lod, rng=rng)
    heights = [0] + list(profile) + [0]
    for k, h in enumerate(profile):
        y = y_bottom + h / 4.0 * top_h
        x0, x1 = x_left + GLYPH_W * k / n, x_left + GLYPH_W * (k + 1) / n
        _relief_bar(mb, x0 - hb, y, x1 + hb, y + BAR_W, z, mat, lod=lod, rng=rng)
    for k in range(n + 1):
        a, b = heights[k], heights[k + 1]
        if a == b:
            continue
        x = x_left + GLYPH_W * k / n
        y0 = y_bottom + min(a, b) / 4.0 * top_h
        y1 = y_bottom + max(a, b) / 4.0 * top_h + BAR_W
        _relief_bar(mb, x - hb, y0, x + hb, y1, z, mat, lod=lod, rng=rng)
    for mx, my in marks:
        cx = x_left + mx * GLYPH_W
        cy = y_bottom + GLYPH_H - BAR_W * 0.6 * my
        _relief_bar(mb, cx - hb, cy - hb, cx + hb, cy + hb, z, mat, lod=lod, rng=rng)


def _emblem(mb: kc.MeshBuilder, cx: float, y_bottom: float, z: float, mat: int, *, lod: bool, rng) -> None:
    """The seven-step terrace emblem: seven stepped layers, the topmost (the seventh terrace) a little proud."""
    w0, step_h = 0.3, 0.036
    for k in range(7):
        w = w0 * (1.0 - k / 7.5)
        y0 = y_bottom + k * step_h
        proud = RELIEF * (1.6 if k == 6 else 1.0)
        c = (cx, y0 + step_h * 0.45, z + proud * 0.5)
        kc.rounded_block(mb, c, (w * 0.5, step_h * 0.45, proud * 0.5 + 0.002), mat, radius=0.004, seg=1 if lod else 2,
                         weather=LACQUER_W, variation=float(rng.random()))


def build_name_board(seed: int = 9121) -> list[kc.MeshBuilder]:
    out = []
    hx, hy = NAME_BOARD_HALF
    t = NAME_BOARD_T
    for lod in (False, True):
        rng = kc.rng_for("terrace_name_board", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("terrace_name_board" + (bf.LOD if lod else ""))
        i_blk, i_red, i_cu = mb.material(M_LACQUER), mb.material(bf.M_RED), mb.material(M_COPPER_BRIGHT)
        # The board: one plank of black lacquer, its ends cut in a single step (a terrace) top and bottom.
        kc.rounded_block(mb, (0.0, 0.0, t * 0.5), (hx - 0.06, hy, t * 0.5), i_blk, radius=0.012, seg=1 if lod else 3,
                         noise=None if lod else noise, disp_m=0.0015, weather=LACQUER_W, variation=0.3)
        for sx in (-1.0, 1.0):
            kc.rounded_block(mb, (sx * (hx - 0.03), 0.0, t * 0.5), (0.03, hy - 0.05, t * 0.5), i_blk, radius=0.01, seg=1,
                             weather=LACQUER_W, variation=0.4)
        # The copper band round the face (top, bottom and the two end steps), standing just proud.
        zf = t
        band = 0.022
        for y in (hy - band * 0.5, -hy + band * 0.5):
            kc.rounded_block(mb, (0.0, y, zf + 0.004), (hx - 0.07, band * 0.5, 0.005), i_cu, radius=0.002, seg=1)
        for sx in (-1.0, 1.0):
            kc.rounded_block(mb, (sx * (hx - 0.075), 0.0, zf + 0.004), (band * 0.5, hy - band, 0.005), i_cu, radius=0.002,
                             seg=1)
        # A carved inner fillet in red lacquer (a thin proud line inside the band).
        if not lod:
            for y in (hy - 0.05, -hy + 0.05):
                kc.rounded_block(mb, (0.0, y, zf + 0.003), (hx - 0.13, 0.006, 0.004), i_red, radius=0.002, seg=1)
        # The name in terrace script, and the emblem at each end.
        y_bottom = -GLYPH_H * 0.5
        if lod:
            # At 70 m the carving is a red line of text: one band per word and the two emblems as plain blocks.
            cells = name_glyph_cells()
            k = 0
            for word in NAME_WORDS:
                x0, x1 = cells[k][1], cells[k + len(word) - 1][1] + GLYPH_W
                _relief_bar(mb, x0, y_bottom, x1, y_bottom + GLYPH_H * 0.6, zf, i_red, lod=True, rng=rng)
                k += len(word)
            for sx in (-1.0, 1.0):
                _relief_bar(mb, sx * (hx - 0.3) - 0.14, -0.13, sx * (hx - 0.3) + 0.14, -0.13 + 0.2, zf, i_red, lod=True,
                            rng=rng)
            out.append(mb)
            continue
        for g, x_left in name_glyph_cells():
            _glyph(mb, g, x_left, y_bottom, zf, i_red, lod=lod, rng=rng)
        dot_x = name_glyph_cells()[len(NAME_WORDS[0]) - 1][1] + GLYPH_W + WORD_GAP * 0.5
        kc.rounded_block(mb, (dot_x, 0.0, zf + RELIEF * 0.5), (0.02, 0.02, RELIEF * 0.5 + 0.002), i_red, radius=0.006,
                         seg=1 if lod else 2)
        for sx in (-1.0, 1.0):
            _emblem(mb, sx * (hx - 0.3), -0.13, zf, i_red, lod=lod, rng=rng)
        # Nail heads at the brackets.
        if not lod:
            for sx in (-1.0, 1.0):
                for y in (-0.18, 0.18):
                    kc.tube(mb, np.array([[sx * (hx - 0.3), y, zf], [sx * (hx - 0.3), y, zf + 0.01]]), 0.012, 6, i_cu,
                            cap_end=True)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# The galley
# ---------------------------------------------------------------------------------------------
def _board_wall(mb: kc.MeshBuilder, rng, axis: str, fixed: float, a0: float, a1: float, holes, height: float, *,
                lod: bool) -> None:
    """A wall of vertical lacquered boards (a red dado below) along `axis` ('x' or 'z') at `fixed`, from a0 to a1,
    with rectangular `holes` (a0, a1, y0, y1) left open. Thick enough to read from both sides."""
    t = 0.05
    i_blk, i_red = mb.material(M_LACQUER_SATIN), mb.material(M_LACQUER_RED)
    step = 0.9 if lod else 0.16
    n = max(1, int(math.ceil((a1 - a0) / step)))
    dado = 0.7
    for k in range(n):
        u0 = a0 + (a1 - a0) * k / n
        u1 = a0 + (a1 - a0) * (k + 1) / n - (0.0 if lod else 0.008)
        uc = 0.5 * (u0 + u1)
        spans = [(0.0, height)]
        for h0, h1, y0, y1 in holes:
            if h0 < uc < h1:
                nxt = []
                for s0, s1 in spans:
                    if s1 <= y0 or s0 >= y1:
                        nxt.append((s0, s1))
                        continue
                    if s0 < y0:
                        nxt.append((s0, y0))
                    if s1 > y1:
                        nxt.append((y1, s1))
                spans = nxt
        for s0, s1 in spans:
            for y0, y1, mat in ((s0, min(s1, dado), i_red), (max(s0, dado), s1, i_blk)):
                if y1 - y0 < 0.02:
                    continue
                if axis == "x":
                    c, half = (uc, 0.5 * (y0 + y1), fixed), (0.5 * (u1 - u0), 0.5 * (y1 - y0), t)
                else:
                    c, half = (fixed, 0.5 * (y0 + y1), uc), (t, 0.5 * (y1 - y0), 0.5 * (u1 - u0))
                kc.rounded_block(mb, c, half, mat, radius=0.006, seg=1, weather=LACQUER_W, variation=float(rng.random()))


def _bowl(mb: kc.MeshBuilder, rng, x: float, z: float, y: float, eaten: float, *, lod: bool) -> None:
    """An earthenware bowl with its rice (`eaten` of it gone) and a spoon left in it."""
    bf.lathe(mb, (x, y, z), [(0.0, 0.0), (0.04, 0.0), (0.05, 0.01), (0.075, 0.04), (0.085, 0.07), (0.08, 0.072),
                             (0.07, 0.045), (0.0, 0.035)], 8 if lod else 14, bf.M_CLAY, weather=bf.RAIL_W,
             variation=float(rng.random()))
    if lod:
        return
    h = 0.02 + 0.035 * (1.0 - eaten)
    bf.lathe(mb, (x, y + 0.035, z), [(0.0, h), (0.03, h * 0.9), (0.065 - 0.02 * eaten, 0.012), (0.0, 0.012)], 10, M_RICE,
             weather=kc.FRESH, variation=0.5)
    a = float(rng.uniform(0.0, 2.0 * math.pi))
    d = np.array([math.cos(a), 0.0, math.sin(a)])
    kc.tube(mb, np.array([[x, y + 0.06, z] + d * 0.02, [x, y + 0.11, z] + d * 0.15]), 0.006, 4, mb.material(bf.M_TIMBER),
            cap_end=True)


def build_galley(seed: int = 9131) -> list[kc.MeshBuilder]:
    out = []
    x0, x1, z0, z1, h = GALLEY
    for lod in (False, True):
        rng = kc.rng_for("terrace_galley", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("terrace_galley" + (bf.LOD if lod else ""))
        dx0, dx1, dh = GALLEY_DOOR
        wy0, wy1 = GALLEY_WINDOW_Y
        _board_wall(mb, rng, "x", z0, x0, x1, ((dx0, dx1, -0.1, dh),), h, lod=lod)
        _board_wall(mb, rng, "x", z1, x0, x1, (), h, lod=lod)
        for x in (x0, x1):
            _board_wall(mb, rng, "z", x, z0, z1, ((GALLEY_WINDOW_Z[0], GALLEY_WINDOW_Z[1], wy0, wy1),), h, lod=lod)
        i_t = mb.material(bf.M_TIMBER)
        # Corner posts and the door's frame (oiled timber).
        for cx in (x0, x1):
            for cz in (z0, z1):
                kc.rounded_block(mb, (cx, h * 0.5, cz), (0.07, h * 0.5 + 0.02, 0.07), i_t, radius=0.015, seg=1,
                                 weather=bf.RAIL_W, variation=float(rng.random()))
        for x in (dx0, dx1):
            kc.rounded_block(mb, (x, dh * 0.5, z0), (0.04, dh * 0.5, 0.07), i_t, radius=0.01, seg=1)
        kc.rounded_block(mb, (0.0, dh + 0.04, z0), (dx1 + 0.04, 0.04, 0.07), i_t, radius=0.01, seg=1)
        # The roof: planks across, a low camber, open over the table (the smoke hatch) with its coaming and the
        # hatch cover propped open on it.
        sx, sz, sax, saz = SMOKE_HATCH
        n = 4 if lod else 18
        for k in range(n):
            za = z0 - 0.12 + (z1 - z0 + 0.24) * k / n
            zb = z0 - 0.12 + (z1 - z0 + 0.24) * (k + 1) / n - (0.0 if lod else 0.01)
            zc = 0.5 * (za + zb)
            spans = [(x0 - 0.12, x1 + 0.12)]
            if sz - saz < zc < sz + saz:
                spans = [(x0 - 0.12, sx - sax), (sx + sax, x1 + 0.12)]
            for xa, xb in spans:
                for xs in ((xa, 0.5 * (xa + xb)), (0.5 * (xa + xb), xb)):
                    xm = 0.5 * (xs[0] + xs[1])
                    y = h + 0.1 * (1.0 - (xm / (x1 + 0.12)) ** 2)
                    kc.rounded_block(mb, (xm, y, zc), (0.5 * (xs[1] - xs[0]), 0.03, 0.5 * (zb - za)), i_t, radius=0.008,
                                     seg=1, weather=bf.RAIL_W, variation=float(rng.random()))
        yh = h + 0.12
        for cx, cz, hx_, hz_ in ((sx, sz - saz, sax + 0.05, 0.04), (sx, sz + saz, sax + 0.05, 0.04),
                                 (sx - sax, sz, 0.04, saz), (sx + sax, sz, 0.04, saz)):
            kc.rounded_block(mb, (cx, yh + 0.06, cz), (hx_, 0.08, hz_), mb.material(bf.M_TAR), radius=0.01, seg=1)
        kc.rounded_block(mb, (sx + 0.08, yh + 0.03, sz + saz + 0.5), (sax + 0.04, 0.025, saz + 0.04), i_t,
                         rot=kc.rot_y(0.12), radius=0.01, seg=1, weather=bf.RAIL_W, variation=0.5)
        # The table (athwartships) and the benches fore and aft of it.
        tx, tz, tax, taz, th = TABLE
        kc.rounded_block(mb, (tx, th - 0.025, tz), (tax, 0.025, taz), i_t, radius=0.01, seg=1 if lod else 2,
                         weather=bf.RAIL_W, variation=0.3, noise=None if lod else noise, disp_m=0.002)
        for lx in ((-tax + 0.1, tax - 0.1) if not lod else ()):
            for lz in (-taz + 0.08, taz - 0.08):
                kc.rounded_block(mb, (tx + lx, (th - 0.05) * 0.5, tz + lz), (0.035, (th - 0.05) * 0.5, 0.035), i_t,
                                 radius=0.008, seg=1)
        for bz in (tz - taz - 0.3, tz + taz + 0.3):
            kc.rounded_block(mb, (tx, 0.43, bz), (tax, 0.025, 0.14), i_t, radius=0.008, seg=1, weather=bf.RAIL_W,
                             variation=float(rng.random()))
            for lx in ((-tax + 0.12, tax - 0.12) if not lod else ()):
                kc.rounded_block(mb, (tx + lx, 0.2, bz), (0.03, 0.2, 0.1), i_t, radius=0.006, seg=1)
        if lod:
            out.append(mb)
            continue
        # The four bowls, the meal half-eaten; the pot and its ladle in the middle.
        for k, (bx, bz) in enumerate(BOWLS):
            _bowl(mb, rng, bx, bz, th, (0.35, 0.6, 0.2, 0.5)[k], lod=lod)
        bf.lathe(mb, (0.05, th, tz + 0.03), [(0.0, 0.0), (0.1, 0.0), (0.13, 0.04), (0.14, 0.12), (0.13, 0.15), (0.0, 0.15)],
                 8 if lod else 16, M_COPPER_BRIGHT, weather=bf.IRON_W)
        if not lod:
            bf.lathe(mb, (0.05, th + 0.095, tz + 0.03), [(0.0, 0.0), (0.12, 0.0), (0.0, 0.0)], 12, M_RICE)
            kc.tube(mb, np.array([[0.05, th + 0.08, tz + 0.03], [0.12, th + 0.2, tz - 0.1], [0.2, th + 0.27, tz - 0.16]]),
                    0.01, 4, mb.material(bf.M_TIMBER), cap_end=True)
        # The clay stove in the after starboard corner with its copper pot, and the hourglass on a shelf (port wall).
        kc.rounded_block(mb, (x1 - 0.42, 0.38, z1 - 0.38), (0.34, 0.38, 0.32), mb.material(bf.M_CLAY), radius=0.04,
                         seg=1 if lod else 2, weather=bf.RAIL_W, variation=0.6)
        kc.rounded_block(mb, (x1 - 0.42, 0.42, z1 - 0.69), (0.14, 0.12, 0.02), mb.material(bf.M_DARK), radius=0.01, seg=1)
        bf.lathe(mb, (x1 - 0.42, 0.76, z1 - 0.38), [(0.0, 0.0), (0.14, 0.0), (0.17, 0.08), (0.16, 0.2), (0.0, 0.2)],
                 8 if lod else 14, M_COPPER_BRIGHT, weather=bf.IRON_W)
        kc.rounded_block(mb, (x0 + 0.12, 1.25, 4.35), (0.09, 0.02, 0.32), i_t, radius=0.005, seg=1)
        if not lod:
            hg = (x0 + 0.13, 1.27, 4.45)
            for dy, r in ((0.0, 0.05), (0.2, 0.05)):
                kc.rounded_block(mb, (hg[0], hg[1] + dy + 0.01, hg[2]), (0.055, 0.008, 0.055), i_t, radius=0.003, seg=1)
            bf.lathe(mb, (hg[0], hg[1] + 0.02, hg[2]), [(0.03, 0.0), (0.042, 0.04), (0.008, 0.09), (0.042, 0.14),
                                                       (0.03, 0.18)], 8, M_CERAMIC)
            for dx in (-0.045, 0.045):
                kc.tube(mb, np.array([[hg[0] + dx, hg[1], hg[2]], [hg[0] + dx, hg[1] + 0.2, hg[2]]]), 0.006, 4, i_t)
            # The lamp hook over the table (the lamp is gone), and pots on pegs.
            kc.tube(mb, np.array([[0.0, h - 0.02, tz - 0.55], [0.0, h - 0.3, tz - 0.55], [0.05, h - 0.36, tz - 0.55]]),
                    0.008, 4, mb.material(bf.M_IRON))
            for k, zz in enumerate((3.0, 3.35)):
                bf.lathe(mb, (x1 - 0.14, 1.2 - 0.12 * k, zz), [(0.0, 0.0), (0.09, 0.0), (0.1, 0.1), (0.0, 0.1)], 10,
                         M_COPPER_BRIGHT, axis=(-1.0, 0.0, 0.0))
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# The hold
# ---------------------------------------------------------------------------------------------
def _hold_x(z: float, y) -> np.ndarray:
    """The hold's ceiling planking: the hull's section, 0.14 m inboard."""
    return np.maximum(FORM.section_x(z, np.asarray(y, float)) - FORM.bulwark_t - 0.14, 0.2)


def build_hold(seed: int = 9141) -> list[kc.MeshBuilder]:
    out = []
    za, zb = HOLD_Z
    yb, yt = HOLD_FLOOR_Y, -bf.PLANK_T_M - 0.01
    for lod in (False, True):
        rng = kc.rng_for("terrace_hold", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("terrace_hold" + (bf.LOD if lod else ""))
        i_tar, i_t = mb.material(bf.M_TAR), mb.material(bf.M_TIMBER)
        zs = bf.rows_between(za, zb, 1.2 if lod else 0.4)
        ys = np.linspace(yb, yt, 3 if lod else 7)
        for side in (-1.0, 1.0):
            grid = np.asarray([[[side * float(_hold_x(float(z), y)), float(y), float(z)] for y in ys] for z in zs])
            bf._surface(mb, grid, i_tar, outward=np.array([-side, 0.0, 0.0]), uv=grid[..., [2, 1]],
                        col=(0.0, 0.15, 0.1, 0.3), uv2=(0.55, 0.5))
        # The floor (ceiling boards over the floors) and the two bulkheads.
        fw = float(_hold_x(0.5 * (za + zb), yb + 0.02))
        n = 3 if lod else 13
        for k in range(n):
            x = -fw + (k + 0.5) * 2.0 * fw / n
            kc.plank(mb, (x, yb, zb), (x, yb, za), 2.0 * fw / n - 0.012, 0.05, i_t, weather=HOLD_W,
                     variation=float(rng.random()), noise=None if lod else noise)
        for z, s in ((za, 1.0), (zb, -1.0)):
            yy = np.linspace(yb - 0.02, yt, 3 if lod else 6)
            xs = _hold_x(z, yy) + 0.02
            pts = [np.array([-x, y, z]) for x, y in zip(xs[::-1], yy[::-1])] + [np.array([x, y, z]) for x, y in zip(xs, yy)]
            c = np.mean(pts, axis=0)
            base = mb.add_vertices(np.vstack([pts, c[None]]), np.tile([0.0, 0.0, s], (len(pts) + 1, 1)),
                                   np.asarray([[p[0], p[1]] for p in pts] + [[c[0], c[1]]]), (0.5, 0.5), (0.0, 0.1, 0.1, 0.3))
            m = len(pts)
            for k in range(m - 1):
                if s > 0:
                    mb.add_tri(base + k, base + k + 1, base + m, i_tar)
                else:
                    mb.add_tri(base + k, base + m, base + k + 1, i_tar)
        # Deck beams overhead (across, every 0.9 m) and the ceiling between them (dark), open at the hatch.
        _hx, hz, ax, az, _h = MAIN_HATCH
        for z in np.arange(za + 0.3, zb, 0.9):
            if hz - az - 0.15 < z < hz + az + 0.15:
                continue  # the hatch opening: its carlins carry the deck instead
            hw = float(_hold_x(float(z), yt - 0.1))
            kc.rounded_block(mb, (0.0, yt - 0.09, float(z)), (hw, 0.08, 0.08), i_t, radius=0.01, seg=1, weather=HOLD_W,
                             variation=float(rng.random()))
        # The ladder down from the hatch's fore coaming.
        lz0, lz1 = hz - az + 0.15, hz - az + 0.75
        for sx in (-0.26, 0.26):
            kc.plank(mb, (sx, -0.02, lz0), (sx, yb, lz1), 0.06, 0.12, i_t, up=(1.0, 0.0, 0.0), weather=HOLD_W)
        if not lod:
            for k in range(1, 7):
                f = k / 7.0
                kc.plank(mb, (-0.26, -0.02 + (yb + 0.02) * f, lz0 + (lz1 - lz0) * f),
                         (0.26, -0.02 + (yb + 0.02) * f, lz0 + (lz1 - lz0) * f), 0.08, 0.035, i_t, weather=HOLD_W)
        # Copper ingots in crossed stacks, both sides of the ladder's foot; crates aft.
        i_cu = mb.material(M_COPPER_BRIGHT)
        for cx, cz, layers in ((-0.85, -4.75, 5), (0.85, -4.75, 4), (-0.8, -2.4, 3)):
            for layer in range(layers):
                along_x = layer % 2 == 0
                for k in range(3 if lod else 4):
                    o = (k - 1.5) * 0.15
                    c = (cx + (0.0 if along_x else o), yb + 0.025 + 0.05 + layer * 0.07, cz + (o if along_x else 0.0))
                    half = (0.28, 0.03, 0.06) if along_x else (0.06, 0.03, 0.28)
                    kc.rounded_block(mb, c, half, i_cu, radius=0.012, seg=1, weather=COPPER_W,
                                     variation=float(rng.random()))
        for cx, cz, hh in ((0.75, -2.3, 0.32), (0.95, -2.75, 0.26), (0.7, -2.55, 0.22)):
            kc.rounded_block(mb, (cx, yb + 0.025 + hh + (0.64 if cz == -2.55 else 0.0), cz), (0.3, hh, 0.26), i_t,
                             radius=0.02, seg=1 if lod else 2, weather=HOLD_W, variation=float(rng.random()))
        # The shelf on the port side forward, with the lamp-housing Rhen sold her skipper: a dead Lit Age housing,
        # white ceramic, a brass rim and an empty glass port (no glimmer).
        shelf = HOUSING_SHELF
        kc.rounded_block(mb, shelf, (0.45, 0.025, 0.2), i_t, radius=0.006, seg=1)
        for sx in (-0.38, 0.38):
            kc.rounded_block(mb, (shelf[0] + sx, shelf[1] - 0.12, zb - 0.06), (0.025, 0.1, 0.06), i_t, radius=0.004, seg=1)
        hc = (shelf[0] + 0.1, shelf[1] + 0.025, shelf[2])
        bf.lathe(mb, hc, [(0.0, 0.0), (0.13, 0.0), (0.16, 0.06), (0.17, 0.2), (0.14, 0.32), (0.08, 0.36), (0.0, 0.37)],
                 8 if lod else 16, M_CERAMIC, weather=kc.DROWNED, variation=0.4)
        bf.lathe(mb, (hc[0], hc[1] + 0.16, hc[2]), [(0.175, -0.012), (0.18, 0.0), (0.175, 0.012)], 8 if lod else 16,
                 bf.M_BRASS)
        if not lod:
            kc.tube(mb, np.array([[hc[0] + 0.15, hc[1] + 0.2, hc[2]], [hc[0] + 0.18, hc[1] + 0.2, hc[2]]]), 0.06, 10,
                    mb.material(bf.M_DARK), cap_end=True)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Dressings
# ---------------------------------------------------------------------------------------------
def _fender(mb: kc.MeshBuilder, top, bottom_y: float, out_dir: float, *, lod: bool) -> None:
    """A rope fender hung on its lanyard from `top` (on a cap rail), the fender against the topsides below."""
    top = np.asarray(top, float)
    fx = top[0] + out_dir * 0.18
    bf.lathe(mb, (fx, bottom_y, top[2]), [(0.0, 0.0), (0.09, 0.02), (0.12, 0.1), (0.12, 0.42), (0.09, 0.5), (0.0, 0.52)],
             6 if lod else 10, bf.M_ROPE, weather=bf.CLOTH_W)
    if not lod:
        bf.rope(mb, top, (fx, bottom_y + 0.52, top[2]), 0.012, bf.M_ROPE, segs=2, sides=4)


def _crate(mb: kc.MeshBuilder, rng, c, half, yaw: float, *, lod: bool) -> None:
    kc.rounded_block(mb, c, half, mb.material(bf.M_TIMBER), rot=kc.rot_y(yaw), radius=0.02, seg=1 if lod else 2,
                     weather=bf.RAIL_W, variation=float(rng.random()))


def _coil(mb: kc.MeshBuilder, c, r: float, turns: int, *, lod: bool, spill: float = 0.0) -> None:
    """A coil of rope flat on the deck; `spill` drags the outer turns out into a loose tail."""
    c = np.asarray(c, float)
    t = np.linspace(0.0, turns * 2.0 * math.pi, turns * (6 if lod else 14) + 1)
    rr = r * (0.55 + 0.45 * t / t[-1])
    pts = np.stack([c[0] + rr * np.cos(t), c[1] + 0.02 + 0.012 * t / (2.0 * math.pi), c[2] + rr * np.sin(t)], -1)
    if spill > 0.0:
        f = np.clip((t / t[-1] - 0.7) / 0.3, 0.0, 1.0)
        pts[:, 0] += spill * f ** 2
        pts[:, 1] = np.where(f > 0, c[1] + 0.02, pts[:, 1])
    kc.tube(mb, pts, 0.016, 4, mb.material(bf.M_ROPE), weather=bf.CLOTH_W)


def build_moored(seed: int = 9151) -> list[kc.MeshBuilder]:
    out = []
    s = STAGE_SIDE
    sx, sz = STAGE_AT
    for lod in (False, True):
        rng = kc.rng_for("terrace_moored", seed)
        mb = kc.MeshBuilder("terrace_moored" + (bf.LOD if lod else ""))
        edge = sx - s * STAGE_HALF[0]  # the stage's near edge
        y_st = STAGE_DECK_Y + 0.05
        # Bow and stern lines and the springs to the stage's corners; the anchor cable forward into the sea.
        lines = (((s * 0.6, 0.85, FORM.stem_z + 1.9), (edge + s * 0.3, y_st, sz - STAGE_HALF[1] + 0.2), 0.25),
                 ((s * 1.5, POOP_Y + 0.85, 8.8), (edge + s * 0.3, y_st, sz + STAGE_HALF[1] - 0.2), 0.25),
                 ((s * 0.6, 0.85, FORM.stem_z + 1.9), (edge + s * 0.4, y_st, sz + 0.8), 0.12),
                 ((s * 1.5, POOP_Y + 0.85, 8.8), (edge + s * 0.4, y_st, sz - 0.6), 0.12),
                 ((0.2, 0.45, FORM.stem_z + 1.2), (0.6, WATERLINE_Y - 0.3, FORM.stem_z - 7.0), 0.5))
        for a, b, sag in lines:
            bf.rope(mb, a, b, 0.024 if not lod else 0.04, bf.M_ROPE, sag=sag, segs=2 if lod else 10, sides=3 if lod else 5)
        # Rope fenders between her topsides and the stage.
        for z in (-0.6, 0.4, 2.4, 3.4):
            top = (s * (float(FORM.half_beam_at(z)) + 0.12), float(FORM.rail_y(z)) + 0.05, z)
            _fender(mb, top, WATERLINE_Y + 0.2, s, lod=lod)
        # The gangplank from the gangway's sill down to the stage.
        gz = 0.5 * (GANGWAY_Z[0] + GANGWAY_Z[1])
        x_sill = s * (float(FORM.half_beam_at(gz)) + 0.05)
        a = np.array([x_sill - s * 0.5, 0.03, gz])
        b = np.array([edge + s * 1.1, y_st + 0.02, gz])
        i_t = mb.material(bf.M_TIMBER)
        for dz in (-0.17, 0.0, 0.17):
            kc.plank(mb, a + [0.0, 0.0, dz], b + [0.0, 0.0, dz], 0.16, 0.05, i_t, weather=bf.RAIL_W,
                     variation=float(rng.random()))
        if not lod:
            n = 6
            for k in range(1, n):
                p = a + (b - a) * k / n
                kc.plank(mb, p + [0.0, 0.035, -0.26], p + [0.0, 0.035, 0.26], 0.04, 0.025, i_t, up=kc.UP)
        # Salvage on deck by the hatch: crates, a basket of brass fittings, a coil, the lamp-housing in its crate.
        _crate(mb, rng, (-1.75, 0.3, -3.3), (0.36, 0.3, 0.3), 0.08, lod=lod)
        _crate(mb, rng, (-1.75, 0.82, -3.25), (0.3, 0.22, 0.26), -0.12, lod=lod)
        _crate(mb, rng, (1.85, 0.26, -2.2), (0.32, 0.26, 0.28), 0.2, lod=lod)
        bf.lathe(mb, (-1.7, 0.0, -2.35), [(0.0, 0.0), (0.2, 0.0), (0.24, 0.08), (0.26, 0.3), (0.0, 0.3)], 7 if lod else 14,
                 bf.M_BASKET, weather=bf.CLOTH_W, variation=0.6)
        if not lod:
            for k in range(6):
                a_ = k * 1.05
                kc.tube(mb, np.array([[-1.7 + 0.12 * math.cos(a_), 0.28, -2.35 + 0.12 * math.sin(a_)],
                                      [-1.7 + 0.15 * math.cos(a_ + 0.5), 0.36, -2.35 + 0.15 * math.sin(a_ + 0.5)]]),
                        0.03, 6, mb.material(bf.M_BRASS), cap_start=True, cap_end=True)
            _coil(mb, (1.6, 0.0, -5.4), 0.32, 5, lod=lod)
        # The lamp-housing, unpacked on the hatch boards (in Ch4 it is below, on the hold's shelf).
        hc = (1.85, 0.52, -2.2)
        bf.lathe(mb, hc, [(0.0, 0.0), (0.13, 0.0), (0.16, 0.06), (0.17, 0.2), (0.14, 0.32), (0.08, 0.36), (0.0, 0.37)],
                 8 if lod else 16, M_CERAMIC, weather=kc.DROWNED, variation=0.4)
        out.append(mb)
    return out


def build_derelict(seed: int = 9161) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("terrace_derelict", seed)
        mb = kc.MeshBuilder("terrace_derelict" + (bf.LOD if lod else ""))
        # A capsized bucket, rolled against the starboard bulwark.
        bf.lathe(mb, (2.35, 0.17, -2.0), [(0.0, -0.17), (0.15, -0.17), (0.17, 0.17), (0.0, 0.17)], 8 if lod else 14,
                 bf.M_TIMBER, axis=(0.3, 0.0, 1.0), weather=bf.RAIL_W)
        # The main sheet's slack fall across the deck, from the fife rail to the port bulwark.
        pts = np.array([[0.5, 0.75, MAINMAST_Z - 0.7], [0.2, 0.03, MAINMAST_Z - 1.4], [-0.8, 0.02, MAINMAST_Z - 2.0],
                        [-1.9, 0.02, MAINMAST_Z - 1.7], [-2.6, 0.5, MAINMAST_Z - 1.3]])
        kc.tube(mb, pts, 0.02, 4, mb.material(bf.M_ROPE), weather=bf.CLOTH_W)
        # A coil spilled by the sea, and the stool fallen by the galley door.
        _coil(mb, (-1.6, 0.0, -6.0), 0.3, 4, lod=lod, spill=1.2)
        i_t = mb.material(bf.M_TIMBER)
        rot = kc.rot_z(math.pi * 0.5) @ kc.rot_y(0.4)
        kc.rounded_block(mb, (1.05, 0.2, GALLEY[2] - 0.6), (0.2, 0.025, 0.2), i_t, rot=rot, radius=0.006, seg=1)
        if not lod:
            for dz in (-0.14, 0.14):
                for dy in (-0.14, 0.14):
                    a = np.array([1.05, 0.2, GALLEY[2] - 0.6]) + rot @ np.array([0.0, 0.02, 0.0]) + np.array([0.0, dy, dz])
                    kc.tube(mb, np.array([a, a + rot @ np.array([0.0, 0.42, 0.0])]), 0.02, 4, i_t, cap_end=True)
        # The hatch boards' tarpaulin, torn and thrown back over the starboard coaming.
        hx, hz, ax, az, h = MAIN_HATCH
        nu, nv = (3, 3) if lod else (9, 7)
        U, V = np.meshgrid(np.linspace(0.0, 1.0, nu), np.linspace(-1.0, 1.0, nv))
        X = hx + ax + 0.1 + U * 1.1
        Y = h + 0.02 - U ** 1.5 * (h - 0.02) + 0.04 * np.sin(V * 3.0 + U * 4.0)
        Z = hz + V * (az + 0.05) * (1.0 - 0.25 * U)
        bf.cloth(mb, np.stack([X, Y, Z], -1), bf.M_TARP, uv=np.stack([X, Z], -1), variation=0.3)
        del rng
        out.append(mb)
    return out


def build_alongside(seed: int = 9171) -> list[kc.MeshBuilder]:
    """In the ferry's frame: her port-side fenders and three boathooks laid across to the derelict's cap rail."""
    out = []
    ferry = bf.FERRY
    dx, dy, dz = DERELICT_IN_FERRY
    for lod in (False, True):
        rng = kc.rng_for("alongside_gear", seed)
        mb = kc.MeshBuilder("alongside_gear" + (bf.LOD if lod else ""))
        for z in (-5.2, -2.0, 1.4, 4.4):
            top = (-(float(ferry.half_beam_at(z)) + 0.12), float(ferry.rail_y(z)) + 0.05, z)
            _fender(mb, top, bf.WATERLINE_Y + 0.25, -1.0, lod=lod)
        i_t, i_iron = mb.material(bf.M_TIMBER), mb.material(bf.M_IRON)
        for z in (-3.6, -0.4, 3.0):
            zt = z - dz  # in her frame
            far = np.array([dx + float(FORM.half_beam_at(zt)) + 0.09, dy + float(FORM.rail_y(zt)) + 0.07, z])
            near = np.array([-(float(ferry.half_beam_at(z)) + 0.09), float(ferry.rail_y(z)) + 0.07, z])
            d = kc.normalize(near - far)
            butt = near + d * 1.0
            kc.tube(mb, np.array([far - d * 0.15, butt]), 0.028, 4 if lod else 7, i_t, weather=bf.RAIL_W,
                    cap_start=True, cap_end=True, variation=float(rng.random()))
            # The iron hook over her rail: a point along the pole and a tine bent down over her cap rail.
            hook = np.array([far - d * 0.12, far - d * 0.32, far - d * 0.4 + np.array([0.0, -0.08, 0.0])])
            kc.tube(mb, hook, 0.018, 4 if lod else 6, i_iron, cap_end=True)
        out.append(mb)
    return out


TARGETS = {"terrace_hull": build_hull, "terrace_wheel": build_wheel, "terrace_name_board": build_name_board,
           "terrace_galley": build_galley, "terrace_hold": build_hold, "terrace_moored": build_moored,
           "terrace_derelict": build_derelict, "alongside_gear": build_alongside}
