"""The ferry *Kind Weather*'s hull and decks (M3-ENV-08; brightwater_ferry.md §0, §2). Pure numpy; see bf_common.py.

  ferry_hull   the hull (tarred below the red wale, sea-blue topsides, the transom), the flat main deck and the
               poop deck (scrubbed planks over dark seams), covering boards, the bulwark (stanchions, three inner
               strakes, the cap rail) with the two gangways, the poop's break with its ladders and breast rails,
               the taffrail, the main hatch (closed, tarpaulin lashed), the fore hatch (grating over the dark hold),
               the poop scuttle, the rudder and tiller, the stern-lantern post, the bowsprit and stem post, the
               stem-gull (the Haluna kit's lintel-gull generator, read-only, carved at the stem head), the windlass
               and bitts, the chain-plates and the fife rails.

The ship's frame: bow to -Z, the origin on the centre line at main-deck level amidships, the waterline at
y = bf_common.WATERLINE_Y. Every walkable surface is flat: the main deck at y 0 and the poop at y 0.9.
"""

from __future__ import annotations

import math

import numpy as np

import bf_common as bf
import village  # the Haluna kit's lintel-gull (read-only)
from bf_common import kc

TRI_BUDGET = {"ferry_hull": (60000, 6000)}
F = bf.FERRY
LADDER_X = 2.62
LADDER_HALF_W = 0.3
STERN_POST = (0.0, 12.35)  # x, z of the stern-lantern post (the lantern hangs from its crook)
STERN_POST_H = 2.1  # above the poop deck
STERN_CROOK_M = 0.55  # the crook's reach forward
TILLER_M = 3.2
SCUTTLE = (1.45, 11.0, 0.45, 0.4, 0.3)
WINDLASS_Z = -11.9
BOW_CROOK_Z = -11.9  # the bow lantern's crook, on the starboard cap rail
BOW_CROOK_H = 1.0
BOW_CROOK_REACH = (-0.55, -0.35)  # inboard and forward
FIFE_DZ = {bf.FOREMAST_Z: 0.75, bf.MAINMAST_Z: -0.75}  # each mast's fife rail; the main's forward, clear of the door


def hatch_keep_out() -> list[tuple[float, float, float, float]]:
    out = []
    for hx, hz, ax, az, _h in (bf.MAIN_HATCH, bf.FORE_HATCH):
        out.append((hx - ax - 0.12, hx + ax + 0.12, hz - az - 0.12, hz + az + 0.12))
    return out


def stern_lantern_ring() -> tuple[float, float, float]:
    """Where the stern lantern's ring hangs (the crook's tip), in the ship's frame."""
    x, z = STERN_POST
    return (x, bf.POOP_Y + STERN_POST_H - 0.12, z - STERN_CROOK_M)


def _wale(mb: kc.MeshBuilder, rng, *, lod: bool) -> None:
    """The red-lacquered wale (rubbing strake) along each side at the paint line."""
    i = mb.material(bf.M_RED)
    zs = bf.rows_between(F.stem_z + 0.8, F.transom_z - 0.05, 2.0 if lod else 0.9)
    for side in (-1.0, 1.0):
        for a, b in zip(zs[:-1], zs[1:]):
            a, b = float(a), float(b)
            xa = side * (float(F.section_x(a, np.array(F.wale_y))) + 0.03)
            xb = side * (float(F.section_x(b, np.array(F.wale_y))) + 0.03)
            kc.plank(mb, (xb, F.wale_y + 0.02, b), (xa, F.wale_y + 0.02, a), 0.11, 0.07, i, up=(side, 0.0, 0.0),
                     weather=bf.HULL_W, variation=float(rng.random()))


def _hatch(mb: kc.MeshBuilder, rng, noise, *, lod: bool) -> None:
    """The main hatch: a tarred coaming, the hatch boards under a lashed tarpaulin, battens and lashings."""
    hx, hz, ax, az, h = bf.MAIN_HATCH
    i_tar = mb.material(bf.M_TAR)
    t = 0.12
    for cx, cz, sx, sz in ((hx, hz - az, ax + t, t), (hx, hz + az, ax + t, t), (hx - ax, hz, t, az), (hx + ax, hz, t, az)):
        kc.rounded_block(mb, (cx, h * 0.5 - 0.05, cz), (sx, h * 0.5 + 0.05, sz), i_tar, radius=0.03,
                         seg=1 if lod else 2, weather=bf.RAIL_W, variation=float(rng.random()))
    # The tarpaulin: over the boards (a low crown) and down the coaming's sides to just above the deck.
    nu, nv = (5, 4) if lod else (17, 14)
    u = np.linspace(-1.0, 1.0, nu)
    v = np.linspace(-1.0, 1.0, nv)
    U, V = np.meshgrid(u, v)
    ex = ax + t + 0.04
    ez = az + t + 0.04
    # Map the square to the top and the skirts: |u|,|v| < 0.8 is the top; beyond it the cloth falls.
    fx = np.clip(np.abs(U) / 0.8, 0.0, 1.0)
    fz = np.clip(np.abs(V) / 0.8, 0.0, 1.0)
    over = np.maximum(np.abs(U) - 0.8, 0.0) / 0.2
    overz = np.maximum(np.abs(V) - 0.8, 0.0) / 0.2
    drop = np.maximum(over, overz)
    X = hx + np.sign(U) * fx * ex
    Z = hz + np.sign(V) * fz * ez
    Y = h + 0.06 + 0.05 * (1.0 - fx ** 2) * (1.0 - fz ** 2) - drop * (h - 0.06)
    if not lod:
        Y = Y + (noise.fbm(np.stack([X, Y, Z], -1) / 0.25, 2) - 0.5) * 0.025
        X = X + np.sign(U) * 0.02 * drop
        Z = Z + np.sign(V) * 0.02 * drop
    grid = np.stack([X, Y, Z], axis=-1)
    bf.cloth(mb, grid, bf.M_TARP, uv=np.stack([X, Z], -1) * 0.8, noise=noise, variation=0.4)
    if lod:
        return
    # Battens down two opposite sides, and three lashings over the top to the deck.
    i_iron = mb.material(bf.M_IRON)
    for side in (-1.0, 1.0):
        kc.rounded_block(mb, (hx + side * (ex + 0.02), h * 0.5, hz), (0.02, 0.04, ez), i_iron, seg=1, radius=0.008)
    for k in (-0.55, 0.0, 0.55):
        z = hz + k * az
        pts = [(-ex - 0.35, 0.02), (-ex - 0.02, h * 0.55), (-ex + 0.05, h + 0.1), (ex - 0.05, h + 0.1), (ex + 0.02, h * 0.55),
               (ex + 0.35, 0.02)]
        line = np.array([[hx + px, py, z] for px, py in pts])
        kc.tube(mb, line, 0.016, 4, mb.material(bf.M_ROPE), weather=bf.CLOTH_W)


def _fore_hatch(mb: kc.MeshBuilder, rng, *, lod: bool) -> None:
    """The fore hatch: coaming, an open grating of slats, and the dark hold under it."""
    hx, hz, ax, az, h = bf.FORE_HATCH
    i_tar, i_t, i_dark = mb.material(bf.M_TAR), mb.material(bf.M_TIMBER), mb.material(bf.M_DARK)
    t = 0.1
    for cx, cz, sx, sz in ((hx, hz - az, ax + t, t), (hx, hz + az, ax + t, t), (hx - ax, hz, t, az), (hx + ax, hz, t, az)):
        kc.rounded_block(mb, (cx, h * 0.5 - 0.05, cz), (sx, h * 0.5 + 0.05, sz), i_tar, radius=0.025, seg=1,
                         weather=bf.RAIL_W, variation=float(rng.random()))
    # The hold under it: a dark box open at the top (faces inward).
    d = -1.3
    box = [((hx, d, hz), (ax, 0.01, az)), ((hx - ax, (d + h) * 0.5 - 0.1, hz), (0.01, (h - d) * 0.5, az)),
           ((hx + ax, (d + h) * 0.5 - 0.1, hz), (0.01, (h - d) * 0.5, az)),
           ((hx, (d + h) * 0.5 - 0.1, hz - az), (ax, (h - d) * 0.5, 0.01)),
           ((hx, (d + h) * 0.5 - 0.1, hz + az), (ax, (h - d) * 0.5, 0.01))]
    for c, half in box:
        kc.rounded_block(mb, c, half, i_dark, seg=1, radius=0.004)
    if lod:
        kc.rounded_block(mb, (hx, h - 0.02, hz), (ax, 0.02, az), i_t, seg=1, radius=0.005)
        return
    n = 7
    for k in range(n):
        x = hx - ax + (k + 0.5) * 2.0 * ax / n
        kc.plank(mb, (x, h - 0.03, hz + az), (x, h - 0.03, hz - az), 0.06, 0.05, i_t, weather=bf.RAIL_W,
                 variation=float(rng.random()))
    for k in range(n):
        z = hz - az + (k + 0.5) * 2.0 * az / n
        kc.plank(mb, (hx - ax, h - 0.075, z), (hx + ax, h - 0.075, z), 0.05, 0.04, i_t, weather=bf.RAIL_W,
                 variation=float(rng.random()))


def _scuttle(mb: kc.MeshBuilder, rng, *, lod: bool) -> None:
    sx, sz, ax, az, h = SCUTTLE
    y = bf.POOP_Y
    kc.rounded_block(mb, (sx, y + h * 0.5, sz), (ax, h * 0.5, az), mb.material(bf.M_TAR), radius=0.03,
                     seg=1 if lod else 2, weather=bf.RAIL_W, variation=float(rng.random()))
    kc.rounded_block(mb, (sx, y + h + 0.03, sz), (ax + 0.04, 0.03, az + 0.04), mb.material(bf.M_TIMBER), radius=0.015,
                     seg=1, weather=bf.RAIL_W, variation=float(rng.random()))


def _poop_break(mb: kc.MeshBuilder, rng, noise, *, lod: bool) -> None:
    """The poop's planked front, its two ladders and the breast rails between them."""
    i_t = mb.material(bf.M_TIMBER)
    hw = float(F.half_beam_at(bf.POOP_Z))
    z = bf.POOP_Z + 0.04
    n = 1 if lod else 6
    for k in range(n):
        y0 = bf.POOP_Y * k / n
        y1 = bf.POOP_Y * (k + 1) / n - (0.0 if lod else 0.012)
        kc.rounded_block(mb, (0.0, 0.5 * (y0 + y1), z), (hw, 0.5 * (y1 - y0), 0.04), i_t, radius=0.01, seg=1,
                         weather=bf.RAIL_W, variation=float(rng.random()))
    # Ladders: two strings and four treads, from the main deck up to the poop's edge.
    for lx in (-LADDER_X, LADDER_X):
        for s in (-LADDER_HALF_W, LADDER_HALF_W):
            kc.plank(mb, (lx + s, bf.POOP_Y + 0.08, bf.POOP_Z - 0.02), (lx + s, 0.0, bf.POOP_Z - 0.62), 0.06, 0.15, i_t,
                     up=(1.0, 0.0, 0.0), weather=bf.RAIL_W, variation=float(rng.random()))
        if lod:
            continue
        for k in range(1, 4):
            f = k / 4.0
            kc.plank(mb, (lx - LADDER_HALF_W, bf.POOP_Y * f, bf.POOP_Z - 0.6 * (1.0 - f)),
                     (lx + LADDER_HALF_W, bf.POOP_Y * f, bf.POOP_Z - 0.6 * (1.0 - f)), 0.18, 0.045,
                     mb.material(bf.M_DECK), weather=bf.DECK_W, variation=float(rng.random()), noise=noise)
    # Breast rails along the break, open at the ladders.
    top = bf.POOP_Y + bf.RAIL_H
    spans = ((-hw, -LADDER_X - LADDER_HALF_W - 0.05), (-LADDER_X + LADDER_HALF_W + 0.05, LADDER_X - LADDER_HALF_W - 0.05),
             (LADDER_X + LADDER_HALF_W + 0.05, hw))
    for x0, x1 in spans:
        kc.plank(mb, (x0, top, bf.POOP_Z + 0.08), (x1, top, bf.POOP_Z + 0.08), 0.12, 0.06, i_t, weather=bf.RAIL_W,
                 variation=float(rng.random()))
        for x in np.linspace(x0 + 0.05, x1 - 0.05, max(2, int((x1 - x0) / 0.9) + 1)):
            kc.rounded_block(mb, (float(x), bf.POOP_Y + bf.RAIL_H * 0.5, bf.POOP_Z + 0.08), (0.035, bf.RAIL_H * 0.5, 0.035),
                             i_t, radius=0.01, seg=1)
        if not lod:
            kc.plank(mb, (x0, bf.POOP_Y + 0.5, bf.POOP_Z + 0.08), (x1, bf.POOP_Y + 0.5, bf.POOP_Z + 0.08), 0.05, 0.04, i_t,
                     weather=bf.RAIL_W, variation=float(rng.random()))


def _taffrail(mb: kc.MeshBuilder, rng, *, lod: bool) -> None:
    """The transom's inner face above the poop (to the planking's top) and the open taffrail on posts above it."""
    i_t = mb.material(bf.M_TIMBER)
    z = F.transom_z - 0.06
    hw = float(F.half_beam_at(z)) + 0.02
    top = float(F.sheer_y(z))
    rail = float(F.rail_y(z))
    kc.rounded_block(mb, (0.0, (bf.POOP_Y + top) * 0.5, z), (hw, (top - bf.POOP_Y) * 0.5, 0.05), i_t, radius=0.015,
                     seg=1, weather=bf.RAIL_W, variation=float(rng.random()))
    kc.plank(mb, (-hw - 0.08, rail + 0.03, z + 0.03), (hw + 0.08, rail + 0.03, z + 0.03), 0.3, 0.07, i_t, weather=bf.RAIL_W,
             variation=float(rng.random()))
    for x in np.linspace(-hw + 0.1, hw - 0.1, 3 if lod else 7):
        kc.rounded_block(mb, (float(x), (top + rail) * 0.5, z), (0.04, (rail - top) * 0.5, 0.04), i_t, radius=0.01, seg=1)
    if not lod:
        kc.plank(mb, (-hw, (top + rail) * 0.5, z), (hw, (top + rail) * 0.5, z), 0.08, 0.05, i_t, weather=bf.RAIL_W,
                 variation=float(rng.random()))


def _rudder(mb: kc.MeshBuilder, rng, noise, *, lod: bool) -> None:
    """The rudder hung outside the transom, its stock through the poop and the long tiller forward."""
    i_tar, i_t, i_iron = mb.material(bf.M_TAR), mb.material(bf.M_TIMBER), mb.material(bf.M_IRON)
    zr = F.transom_z + 0.22
    kc.rounded_block(mb, (0.0, -1.0, zr + 0.35), (0.08, 1.35, 0.45), i_tar, radius=0.04, seg=1 if lod else 2,
                     weather=bf.HULL_W, variation=0.4)
    stock = np.array([[0.0, -0.3, zr], [0.0, bf.POOP_Y + 0.7, zr]])
    kc.tube(mb, stock, 0.11, 6 if lod else 10, i_t, weather=bf.RAIL_W, cap_end=True)
    if not lod:
        for y in (-1.8, -0.9, 0.0):
            kc.rounded_block(mb, (0.0, y, F.transom_z + 0.12), (0.12, 0.04, 0.14), i_iron, radius=0.01, seg=1)
    # The tiller: from the rudder head forward over the transom rail, rising a little to the hand.
    t = np.linspace(0.0, 1.0, 3 if lod else 7)
    head = np.array([0.0, bf.POOP_Y + 0.62, zr])
    pts = head[None, :] + np.stack([np.zeros_like(t), 0.25 * t ** 1.5, -TILLER_M * t], axis=-1)
    kc.tube(mb, pts, np.linspace(0.075, 0.045, len(t)), 5 if lod else 8, i_t, weather=bf.RAIL_W, noise=None if lod else noise,
            disp_m=0.004, cap_end=True)


def _crook(mb: kc.MeshBuilder, base, height: float, reach, ring, *, lod: bool) -> None:
    """A lantern crook: a post from `base` up `height`, bending over to reach `reach` (x, z) at its tip, and the
    short iron hook down to the lantern's ring."""
    i_t = mb.material(bf.M_TIMBER)
    base = np.asarray(base, float)
    top = base + np.array([0.0, height - 0.25, 0.0])
    t = np.linspace(0.0, 1.0, 4 if lod else 9)
    ang = t * math.pi * 0.5
    crook = top[None, :] + np.stack([reach[0] * np.sin(ang), 0.25 * np.sin(ang) - 0.2 * t ** 2, reach[1] * np.sin(ang)],
                                    -1)
    pts = np.vstack([[base - np.array([0.0, 0.05, 0.0])], crook])
    kc.tube(mb, pts, 0.05, 5 if lod else 8, i_t, weather=bf.RAIL_W, cap_end=True)
    if not lod:
        kc.tube(mb, np.array([pts[-1], np.asarray(ring, float) + np.array([0.0, 0.04, 0.0])]), 0.012, 4,
                mb.material(bf.M_IRON))


def bow_crook_base() -> np.ndarray:
    z = BOW_CROOK_Z
    return np.array([float(F.half_beam_at(z)) + 0.09, float(F.rail_y(z)) + 0.06, z])


def bow_lantern_ring() -> tuple[float, float, float]:
    """Where the bow lantern's ring hangs (the bow crook's tip), in the ship's frame: inboard over the bow, so the
    lantern lights the stem-gull from behind."""
    b = bow_crook_base()
    return (float(b[0] + BOW_CROOK_REACH[0]), float(b[1] + BOW_CROOK_H - 0.12), float(b[2] + BOW_CROOK_REACH[1]))


def _stern_post(mb: kc.MeshBuilder, *, lod: bool) -> None:
    """The stern-lantern post on the taffrail, with its crook reaching forward over the poop."""
    x, z = STERN_POST
    _crook(mb, (x, bf.POOP_Y, z), STERN_POST_H, (0.0, -STERN_CROOK_M), stern_lantern_ring(), lod=lod)


def _bow_crook(mb: kc.MeshBuilder, *, lod: bool) -> None:
    """The bow lantern's crook on the starboard cap rail."""
    _crook(mb, bow_crook_base(), BOW_CROOK_H, BOW_CROOK_REACH, bow_lantern_ring(), lod=lod)


def _bow(mb: kc.MeshBuilder, rng, noise, *, lod: bool) -> None:
    """Stem post, bowsprit, the stem-gull, the windlass and its bitts."""
    i_t, i_tar = mb.material(bf.M_TIMBER), mb.material(bf.M_TAR)
    sz = F.stem_z
    head_y = float(F.sheer_y(sz + 0.1))
    ys = np.linspace(F.keel_y + 0.05, head_y, 3 if lod else 8)
    zs = sz + 0.03 + F.forefoot_dz(sz + 0.03, ys)
    stem = np.stack([np.zeros_like(ys), ys, zs], -1)
    stem = np.vstack([stem, [[0.0, head_y + 0.35, sz - 0.12]]])
    kc.tube(mb, stem, 0.15, 5 if lod else 8, i_tar, weather=bf.HULL_W, cap_end=True)
    a = np.array([bf.BOWSPRIT_X, head_y - 0.05, sz + 1.6])
    b = np.array([bf.BOWSPRIT_X, head_y + 1.0, sz - 3.6])
    kc.tube(mb, np.array([a, b]), [0.17, 0.11], 6 if lod else 10, i_t, weather=bf.RAIL_W, noise=None if lod else noise,
            disp_m=0.006, cap_end=True)
    # The stem-gull: the Haluna lintel-gull (crying), carved larger, facing the sea ahead (-Z) on the stem head.
    gull = village.lintel_gull("stem_gull", "crying", 0.95, 41, lod=lod)
    mb.merge(gull, kc.rot_y(math.pi * 0.5), (0.0, head_y + 0.33, sz + 0.05))
    if lod:
        return
    # Windlass: a barrel between two bitts, the cable led forward to the hawse.
    for x in (-0.95, 0.95):
        kc.rounded_block(mb, (x, 0.45, WINDLASS_Z), (0.12, 0.45, 0.14), i_t, radius=0.03, seg=2, weather=bf.RAIL_W,
                         variation=float(rng.random()))
    kc.tube(mb, np.array([[-0.85, 0.42, WINDLASS_Z], [0.85, 0.42, WINDLASS_Z]]), 0.16, 10, i_t, weather=bf.RAIL_W,
            cap_start=True, cap_end=True)
    for x in (-0.5, 0.5):
        kc.tube(mb, np.array([[x, 0.42, WINDLASS_Z], [x, 0.42, WINDLASS_Z + 0.001]]), 0.19, 10, mb.material(bf.M_IRON),
                cap_start=True, cap_end=True)
    hx = 0.55
    hz = sz + 2.4
    hwx = float(F.half_beam_at(hz)) + 0.1
    cable = np.array([[0.0, 0.55, WINDLASS_Z - 0.1], [0.2, 0.25, (WINDLASS_Z + hz) * 0.5], [hx, 0.35, hz]])
    kc.tube(mb, cable, 0.035, 5, mb.material(bf.M_ROPE), weather=bf.CLOTH_W)
    del hwx


def _chain_plates(mb: kc.MeshBuilder, *, lod: bool) -> None:
    """Iron straps down the topsides under each shroud, with the deadeye at the top."""
    i_iron = mb.material(bf.M_IRON)
    for mz in (bf.FOREMAST_Z, bf.MAINMAST_Z):
        for side in (-1.0, 1.0):
            for p in bf.chain_points(F, mz, side):
                z = float(p[2])
                x_lo = side * (float(F.section_x(z, np.array(F.wale_y + 0.1))) + 0.04)
                strap = np.array([[x_lo, F.wale_y + 0.1, z], [p[0], p[1] - 0.12, z]])
                if lod:
                    kc.tube(mb, strap, 0.03, 3, i_iron)
                    continue
                kc.plank(mb, strap[0], strap[1], 0.07, 0.025, i_iron, up=(side, 0.0, 0.0), weather=bf.IRON_W)
                bf.lathe(mb, p - np.array([0.0, 0.07, 0.0]), [(0.06, 0.0), (0.085, 0.03), (0.085, 0.11), (0.06, 0.14)], 8,
                         bf.M_TIMBER, weather=bf.RAIL_W)


def _fife_rails(mb: kc.MeshBuilder, rng, *, lod: bool) -> None:
    """A pin rail aft of each mast (the halyards belay there)."""
    i_t = mb.material(bf.M_TIMBER)
    for mz in (bf.FOREMAST_Z, bf.MAINMAST_Z):
        z = mz + FIFE_DZ[mz]
        for x in (-0.6, 0.6):
            kc.rounded_block(mb, (x, 0.42, z), (0.06, 0.42, 0.06), i_t, radius=0.015, seg=1, weather=bf.RAIL_W,
                             variation=float(rng.random()))
        kc.rounded_block(mb, (0.0, 0.8, z), (0.72, 0.04, 0.07), i_t, radius=0.015, seg=1, weather=bf.RAIL_W,
                         variation=float(rng.random()))
        if lod:
            continue
        for x in np.linspace(-0.45, 0.45, 5):
            kc.tube(mb, np.array([[float(x), 0.7, z], [float(x), 0.98, z]]), 0.018, 5, i_t, cap_end=True)


def build_ferry_hull(seed: int = 801) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("ferry_hull", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("ferry_hull" + (bf.LOD if lod else ""))
        bf.hull_sides(mb, F, lod=lod, tar=bf.M_TAR, paint=bf.M_BLUE, noise=noise)
        bf.transom(mb, F, bf.M_BLUE, lod=lod)
        _wale(mb, rng, lod=lod)
        keep = hatch_keep_out()
        if lod:
            for z0, z1, y in ((F.stem_z + 1.0, bf.POOP_Z, 0.0), (bf.POOP_Z, F.transom_z - 0.1, bf.POOP_Y)):
                zs = bf.rows_between(z0, z1, 2.0)
                grid = np.asarray([[[x, y, float(z)] for x in np.linspace(-float(F.half_beam_at(float(z))),
                                                                        float(F.half_beam_at(float(z))), 3)] for z in zs])
                kc.quad_strip(mb, grid, mb.material(bf.M_DECK), uv=grid[..., [0, 2]], col=(0.0, 0.3, 0.0, 0.4),
                              uv2=(1.0, 0.5), flip=True, smooth=False)
        else:
            bf.sub_deck(mb, F, F.stem_z + 0.8, bf.POOP_Z, -bf.PLANK_T_M - 0.005, bf.M_TAR)
            bf.sub_deck(mb, F, bf.POOP_Z, F.transom_z - 0.05, bf.POOP_Y - bf.PLANK_T_M - 0.005, bf.M_TAR)
            bf.deck_planks(mb, F, rng, noise, F.stem_z + 1.0, bf.POOP_Z, 0.0, mat=bf.M_DECK, keep_out=keep)
            bf.deck_planks(mb, F, rng, noise, bf.POOP_Z + 0.08, F.transom_z - 0.1, bf.POOP_Y, mat=bf.M_DECK)
            for side in (-1.0, 1.0):
                bf.covering_board(mb, F, rng, noise, side, F.stem_z + 1.6, bf.POOP_Z - 0.05, mat=bf.M_TIMBER)
                bf.covering_board(mb, F, rng, noise, side, bf.POOP_Z + 0.05, F.transom_z - 0.1, mat=bf.M_TIMBER)
        for side in (-1.0, 1.0):
            bf.bulwark(mb, F, rng, noise, side, F.stem_z + 1.3, bf.POOP_Z - 0.02, lod=lod, timber=bf.M_TIMBER,
                       lining=bf.M_TIMBER)
            bf.bulwark(mb, F, rng, noise, side, bf.POOP_Z + 0.02, F.transom_z - 0.12, lod=lod, timber=bf.M_TIMBER,
                       lining=bf.M_TIMBER)
        _poop_break(mb, rng, noise, lod=lod)
        _taffrail(mb, rng, lod=lod)
        _hatch(mb, rng, noise, lod=lod)
        _fore_hatch(mb, rng, lod=lod)
        _scuttle(mb, rng, lod=lod)
        _rudder(mb, rng, noise, lod=lod)
        _stern_post(mb, lod=lod)
        _bow_crook(mb, lod=lod)
        _bow(mb, rng, noise, lod=lod)
        _chain_plates(mb, lod=lod)
        _fife_rails(mb, rng, lod=lod)
        out.append(mb)
    return out


TARGETS = {"ferry_hull": build_ferry_hull}
