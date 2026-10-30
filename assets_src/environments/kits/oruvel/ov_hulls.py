"""Oruvel's hulls, rafts, bridges and the net-pen hull (oruvel.md §2). Pure numpy; see ov_common.py.

  hull_outrigger   6.5 m outrigger canoe, 0.8 m beam, a float log on two curved booms 2.2 m out to +X; origin at
                   the waterline amidships
  hull_cabin       10 m open cabin hull, 2.6 m beam, 1.2 m deep, side benches, a mast step; origin at the waterline
  raft_deck        9 x 7 m planked deck on three 11 m hulls (bows north), deck top +0.80, fascia, cleats, a float
                   log along each long side; origin at the deck's middle at the waterline
  raft_deck_small  6 x 5 m on two 8 m hulls and four lashed barrels, deck top +0.70
  plank_bridge     6 m span along +Z between deck edges at local y 0 (both ends), 1.1 m wide: sagging stringers,
                   planks lashed across, a rope handrail, lashings wrapped hard round the stringer ends, two stays
  hull_lashed      the run's low hull (C1-12/13): a 3.2 m open skiff, 1.3 m beam, thrown up across the plank bridge
                   by the swell and lashed there, keel on the planks at y 0 (origin under its middle), listing; two
                   lashing lines out to the cut points (lashing_a 2.5 m along +X, lashing_b 6 m along +X and 1.5 m
                   along +Z), each made off round a stake
  net_pen          the Reefball practice pen and Hullgnaw's arena: a 12 m square of 1.4 m walkways on float logs
                   round a 9.2 m pool, the pen net hung from the walkways into the water, a practice net between
                   two posts on the north side; deck top +0.60, origin at the pool's middle at the waterline
"""

from __future__ import annotations

import math

import numpy as np

import ov_common as oc

kc = oc.kc

TRI_BUDGET = {
    "hull_outrigger": (4500, 300),
    "hull_cabin": (5500, 300),
    "raft_deck": (18000, 900),
    "raft_deck_small": (12000, 600),
    "raft_deck_tucked": (18000, 900),
    "raft_deck_small_tucked": (12000, 600),
    "raft_deck_square": (20000, 1000),
    "plank_bridge": (5000, 200),
    "net_pen": (16000, 800),
    "hull_lashed": (4500, 300),
}

RAFT_DECK_Y = 0.80
SQUARE_RAFT_M = 10.0
RAFT_SMALL_Y = 0.70
TUCK_INSET_M = 0.2  # a tucked raft's hulls end this far inside its deck's ends
TUCK_SHEER_M = 0.12
TUCK_CLEAR_M = 0.06  # and their highest point stays this far under the deck line (the planks are 0.05 thick)
NET_PEN_Y = 0.60
BRIDGE_SPAN = 6.0
BRIDGE_W = 1.1


def build_hull_outrigger(seed: int = 701) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("hull_outrigger", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("hull_outrigger" + (oc.LOD if lod else ""))
        h = oc.hull("h", 6.5, 0.8, 0.55, rng, noise, waterline=-0.32, lod=lod, sheer=0.22, open_top=True,
                    frames=False)
        oc.place(mb, h, 0.0, 0.32, 0.0)
        timber = mb.material(oc.M_TIMBER)
        rope = mb.material(oc.M_ROPE)
        # Two booms arching out to the float on +X, the float a log with tapered ends.
        for zb in (-1.1, 0.9):
            s = np.linspace(0.0, 1.0, 3 if lod else 7)
            pts = np.stack([-0.45 + 2.65 * s, 0.38 + 0.18 * np.sin(math.pi * s) - 0.25 * s ** 3, np.full_like(s, zb)],
                           axis=-1)
            kc.tube(mb, pts, 0.045, 4 if lod else 6, timber, weather=oc.SPRAY, cap_start=True, cap_end=True,
                    variation=float(rng.random()))
            if not lod:
                oc.lashing(mb, (0.36, 0.42, zb), (0.0, 0.0, 1.0), 0.05, rope, turns=3)
                oc.lashing(mb, (2.15, 0.2, zb), (0.0, 0.0, 1.0), 0.05, rope, turns=3)
                kc.tube(mb, np.array([[2.15, 0.2, zb], [2.2, 0.05, zb]]), 0.03, 5, timber, cap_end=True)
        zs = np.linspace(-2.2, 2.2, 4 if lod else 9)
        r = 0.11 * np.sqrt(np.clip(1 - (zs / 2.3) ** 4, 0.05, 1))
        kc.tube(mb, np.stack([np.full_like(zs, 2.2), np.full_like(zs, 0.02), zs], axis=-1), r, 5 if lod else 8, timber,
                weather=oc.SPRAY, noise=None if lod else noise, disp_m=0.01, cap_start=True, cap_end=True)
        if not lod:
            # A paddle across the thwarts and a coil of line.
            kc.plank(mb, (-0.3, 0.42, -0.6), (0.25, 0.44, 1.0), 0.06, 0.03, timber, variation=0.4)
            kc.rounded_block(mb, (0.27, 0.43, 1.1), (0.08, 0.012, 0.2), timber, rot=kc.rot_y(0.33), radius=0.01,
                             seg=1)
            oc.coil(mb, (0.0, 0.0, 1.8), 0.14, rope, turns=4, rope_r=0.012)
        out.append(mb)
    return out


def build_hull_cabin(seed: int = 702) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("hull_cabin", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("hull_cabin" + (oc.LOD if lod else ""))
        h = oc.hull("h", 10.0, 2.6, 1.2, rng, noise, waterline=-0.55, lod=lod, sheer=0.32, open_top=True)
        oc.place(mb, h, 0.0, 0.55, 0.0)
        if not lod:
            timber = mb.material(oc.M_TIMBER)
            oc.hull_deck(mb, 10.0, 2.6, 0.55 - 0.85, rng, noise, inset=0.35, z_clip=(-3.2, 3.6))
            for sgn in (-1.0, 1.0):  # side benches
                kc.plank(mb, (sgn * 0.95, 0.12, -2.0), (sgn * 0.95, 0.12, 2.6), 0.3, 0.05, timber, variation=0.5,
                         noise=noise, seg=2)
            kc.rounded_block(mb, (0.0, -0.18, -1.6), (0.18, 0.12, 0.18), timber, radius=0.02, seg=1)  # mast step
            oc.coil(mb, (0.5, -0.27, 2.9), 0.2, mb.material(oc.M_ROPE), turns=5)
            oc.basket(mb, (-0.5, -0.27, 3.0), 0.2, 0.25, rng)
        out.append(mb)
    return out


LASHED_LINES = (((0.55, 0.5, 0.25), (2.5, 0.05, 0.0)), ((0.35, 0.62, 1.3), (6.0, 0.05, 1.5)))
LASHED_LIST_DEG = 7.0


def build_hull_lashed(seed: int = 707) -> list[kc.MeshBuilder]:
    """The run's low hull, lashed across the bridge (see the module docstring)."""
    out = []
    roll = math.radians(LASHED_LIST_DEG)
    for lod in (False, True):
        rng = kc.rng_for("hull_lashed", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("hull_lashed" + (oc.LOD if lod else ""))
        h = oc.hull("h", 3.2, 1.3, 0.6, rng, noise, waterline=-0.3, lod=lod, sheer=0.18, open_top=True,
                    frames=not lod, paint=oc.M_PAINT_TEAL, wear=0.3)
        mb.merge(h, kc.rot_z(roll), (0.0, 0.6, 0.0))
        rope = mb.material(oc.M_ROPE)
        timber = mb.material(oc.M_TIMBER)
        for a, b in LASHED_LINES:
            if lod:
                kc.tube(mb, np.array([a, b], float), 0.02, 3, rope)
                continue
            oc.rope(mb, a, b, 0.12, 0.016, rope, n=10)
            stake_top = np.asarray(b, float) + np.array([0.0, 0.3, 0.0])
            village_post(mb, np.asarray(b, float) - np.array([0.0, 0.1, 0.0]), stake_top, 0.045, rng, noise, sides=6)
            oc.lashing(mb, b, (0.0, 1.0, 0.0), 0.045, rope, turns=3)
        if not lod:
            # A bailer and an oar in the bilge, a coil of the cut line's spare.
            kc.plank(mb, (-0.3, 0.2, -1.1), (0.25, 0.24, 1.0), 0.07, 0.03, timber, variation=0.6)
            oc.coil(mb, (0.15, 0.12, -0.6), 0.13, rope, turns=4, rope_r=0.012)
        del rng
        out.append(mb)
    return out


def _float_log(mb: kc.MeshBuilder, rng, noise, x: float, z0: float, z1: float, y: float, *, lod: bool,
               along_x: bool = False, n: int = 2) -> None:
    """A bound float of logs (n side by side) with coir lashings every 1.5 m."""
    timber, rope = mb.material(oc.M_TIMBER), mb.material(oc.M_ROPE)
    ts = np.linspace(z0, z1, 4 if lod else 12)
    offs = [(k - (n - 1) * 0.5) * 0.32 for k in range(n)]
    for dx in offs:
        if along_x:
            pts = np.stack([ts, y + 0.02 * np.sin(ts * 1.3 + dx * 9.0), np.full_like(ts, x + dx)], axis=-1)
        else:
            pts = np.stack([np.full_like(ts, x + dx), y + 0.02 * np.sin(ts * 1.3 + dx * 9.0), ts], axis=-1)
        kc.tube(mb, pts, 0.16, 5 if lod else 8, timber, noise=None if lod else noise, disp_m=0.015, cap_start=True,
                cap_end=True, variation=float(rng.random()), weather=oc.SPRAY)
    if lod:
        return
    half = abs(offs[0]) + 0.2
    for t in np.arange(z0 + 0.6, z1 - 0.3, 1.5):
        ring = np.array([[-half, 0.0], [0.0, 0.2], [half, 0.0], [0.0, -0.2], [-half, 0.0]])
        if along_x:
            pts = np.stack([np.full(5, t), y + ring[:, 1], x + ring[:, 0]], axis=-1)
        else:
            pts = np.stack([x + ring[:, 0], y + ring[:, 1], np.full(5, t)], axis=-1)
        kc.tube(mb, pts, 0.022, 4, rope, variation=float(rng.random()))


def _cleat(mb: kc.MeshBuilder, at, rng, noise) -> None:
    """A short bollard post at a deck corner, a few turns of rope on it."""
    at = np.asarray(at, float)
    village_post(mb, at - np.array([0.0, 0.25, 0.0]), at + np.array([0.0, 0.42, 0.0]), 0.075, rng, noise)


def village_post(mb, base, top, radius, rng, noise, sides: int = 7) -> None:
    oc.village.post(mb, base, top, radius, rng, noise, sides=sides, weather=oc.SUN)


def raft(name: str, w: float, d: float, deck_y: float, hulls, rng, noise, *, lod: bool, barrels=(),
         floats: bool = True, along_x: bool = False, tucked: bool = False) -> kc.MeshBuilder:
    """A deck w (x) by d (z) at deck_y on `hulls` [(x, length, beam, depth, paint), ...] (bows north) lashed under
    its bearers; float logs along the long sides, cleats at the corners, fascia boards.

    `tucked` keeps every hull inside the deck's length and under its planks (stems included), for rafts lashed edge
    to edge: an untucked raft's bows run past its deck and rise through the next raft's planks."""
    mb = kc.MeshBuilder(name)
    timber, rope = mb.material(oc.M_TIMBER), mb.material(oc.M_ROPE)
    x0, x1, z0, z1 = -w * 0.5, w * 0.5, -d * 0.5, d * 0.5
    oc.deck(mb, x0, x1, z0, z1, deck_y, rng, noise, along_x=along_x, lod=lod, missing_p=0.015)
    gun = deck_y - 0.21  # the hulls' gunwales just under the bearers
    for hx, length, beam, depth, paint in hulls:
        sheer = 0.25 + 0.1 * float(rng.random())
        if tucked:
            length, sheer = min(length, d - TUCK_INSET_M * 2.0), min(sheer, TUCK_SHEER_M)
        h = oc.hull("h", length, beam, depth, rng, noise, waterline=-gun, lod=lod, paint=paint,
                    sheer=sheer, open_top=True, frames=False)
        g = gun
        if tucked:  # the stems' tops under the planks' underside
            g = min(gun, deck_y - TUCK_CLEAR_M - float(np.asarray(h.pos)[:, 1].max()))
        oc.place(mb, h, hx, g, float(rng.uniform(-0.4, 0.4)))
        if not lod:
            nb = max(2, int((z1 - z0) / 1.2) + 1)
            for zb in np.linspace(z0 + 0.15, z1 - 0.15, nb)[::2]:
                oc.cross_lash(mb, (hx, g + 0.07, zb), 0.17, rope)
    if not lod:
        for xx in (x0 - 0.03, x1 + 0.03):
            kc.plank(mb, (xx, deck_y - 0.12, z0), (xx, deck_y - 0.12, z1), 0.2, 0.05, timber, up=(1.0, 0.0, 0.0),
                     variation=float(rng.random()), noise=noise, seg=3)
        for zz in (z0 - 0.03, z1 + 0.03):
            kc.plank(mb, (x0, deck_y - 0.12, zz), (x1, deck_y - 0.12, zz), 0.2, 0.05, timber, up=(0.0, 0.0, 1.0),
                     variation=float(rng.random()), noise=noise, seg=3)
        for cx, cz in ((x0 + 0.2, z0 + 0.2), (x1 - 0.2, z0 + 0.2), (x0 + 0.2, z1 - 0.2), (x1 - 0.2, z1 - 0.2)):
            _cleat(mb, (cx, deck_y, cz), rng, noise)
            oc.lashing(mb, (cx, deck_y + 0.22, cz), (0.0, 1.0, 0.0), 0.075, rope, turns=3)
        # Rope fenders hanging over the long sides.
        for xx in (x0 - 0.1, x1 + 0.1):
            for zz in np.linspace(z0 + 1.0, z1 - 1.0, 3):
                oc.lashing(mb, (xx, deck_y - 0.35, zz), (0.0, 0.0, 1.0), 0.08, rope, turns=5, rope_r=0.03,
                           pitch=0.05)
                kc.tube(mb, np.array([[xx, deck_y - 0.27, zz], [xx * 0.99, deck_y, zz]]), 0.012, 4, rope)
    if floats:
        for xx in (x0 - 0.35, x1 + 0.35):
            _float_log(mb, rng, noise, xx, z0 + 0.3, z1 - 0.3, 0.12, lod=lod)
    for bx, bz in barrels:
        oc.barrel(mb, (bx - 0.45, -0.1, bz), 0.32, 0.9, rng, lying=True, lod=lod)
        if not lod:
            oc.lashing(mb, (bx, 0.22, bz), (1.0, 0.0, 0.0), 0.33, rope, turns=2, pitch=0.3)
    return mb


def build_raft_deck(seed: int = 703, piece: str = "raft_deck", tucked: bool = False) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for(piece, seed)
        noise = kc.Noise3(rng)
        hulls = [(-3.0, 11.0, 2.3, 1.15, oc.M_PAINT), (0.0, 11.4, 2.4, 1.2, oc.M_PAINT_RED),
                 (3.0, 10.6, 2.2, 1.1, oc.M_PAINT_WHITE)]
        mb = raft(piece + (oc.LOD if lod else ""), 9.0, 7.0, RAFT_DECK_Y, hulls, rng, noise, lod=lod, tucked=tucked)
        out.append(mb)
    return out


# A square raft (10 x 10 m, tucked) for a square mooring: the 9 x 7 m raft scaled to cover one overreached its block by
# 2.4 m on each long side, over the hull moored alongside (the scale booth's; cloud-qa pass 6).
def build_raft_deck_square(seed: int = 706) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("raft_deck_square", seed)
        noise = kc.Noise3(rng)
        hulls = [(-3.4, 11.0, 2.3, 1.15, oc.M_PAINT), (0.0, 11.4, 2.4, 1.2, oc.M_PAINT_RED),
                 (3.4, 10.6, 2.2, 1.1, oc.M_PAINT_WHITE)]
        out.append(raft("raft_deck_square" + (oc.LOD if lod else ""), SQUARE_RAFT_M, SQUARE_RAFT_M, RAFT_DECK_Y, hulls,
                        rng, noise, lod=lod, tucked=True))
    return out


# The commons' rafts, lashed edge to edge (ov_zone_dressing): the same decks with their hulls tucked under them.
def build_raft_deck_tucked() -> list[kc.MeshBuilder]:
    return build_raft_deck(piece="raft_deck_tucked", tucked=True)


def build_raft_deck_small_tucked() -> list[kc.MeshBuilder]:
    return build_raft_deck_small(piece="raft_deck_small_tucked", tucked=True)


def build_raft_deck_small(seed: int = 704, piece: str = "raft_deck_small", tucked: bool = False) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for(piece, seed)
        noise = kc.Noise3(rng)
        hulls = [(-1.55, 8.0, 2.0, 1.0, oc.M_PAINT_OCHRE), (1.55, 7.6, 1.9, 0.95, oc.M_PAINT_TEAL)]
        mb = raft(piece + (oc.LOD if lod else ""), 6.0, 5.0, RAFT_SMALL_Y, hulls, rng, noise, lod=lod,
                  barrels=[(-2.7, -2.2), (2.7, -2.2), (-2.7, 2.2), (2.7, 2.2)], floats=False, tucked=tucked)
        out.append(mb)
    return out


def build_plank_bridge(seed: int = 705) -> list[kc.MeshBuilder]:
    """Built along +Z from z 0 to z SPAN at y 0 (the deck tops at both ends)."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("plank_bridge", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("plank_bridge" + (oc.LOD if lod else ""))
        timber, rope, tar = mb.material(oc.M_TIMBER), mb.material(oc.M_ROPE), mb.material(oc.M_ROPE_TAR)
        L, hw, sag = BRIDGE_SPAN, BRIDGE_W * 0.5, 0.15

        def at(s: float, off: float, dy: float = 0.0) -> tuple[float, float, float]:
            return (off, -4.0 * sag * s * (1.0 - s) + dy, s * L)

        for off in (-hw + 0.1, hw - 0.1):
            kc.plank(mb, at(-0.04, off, -0.1), at(1.04, off, -0.1), 0.1, 0.12, timber, variation=float(rng.random()),
                     noise=None if lod else noise, sag_m=sag, seg=1 if lod else 8)
        if lod:
            kc.plank(mb, at(0.0, 0.0, -0.03), at(1.0, 0.0, -0.03), 2 * hw, 0.04, timber, sag_m=sag, seg=3)
            out.append(mb)
            continue
        n = 18
        for k in range(n):
            if k == 11:
                continue  # one plank gone
            s = (k + 0.5) / n
            kc.plank(mb, at(s, -hw, -0.02), at(s, hw, -0.02), L / n - 0.04, 0.04, timber, variation=float(rng.random()),
                     noise=noise)
            if k % 3 == 1:
                for off in (-hw + 0.1, hw - 0.1):
                    oc.lashing(mb, at(s, off, -0.06), (0.0, 0.0, 1.0), 0.06, rope, turns=2, pitch=0.03)
        # The hard lashings at each end: the stringers bound to a cleat beam on the deck edge.
        for s in (0.0, 1.0):
            p = np.asarray(at(s, 0.0, -0.1))
            kc.plank(mb, p + np.array([-hw - 0.15, 0.0, 0.0]), p + np.array([hw + 0.15, 0.0, 0.0]), 0.14, 0.12, timber,
                     up=(0.0, 1.0, 0.0), variation=float(rng.random()), noise=noise)
            for off in (-hw + 0.1, hw - 0.1):
                oc.lashing(mb, np.asarray(at(s, off, -0.1)), (1.0, 0.0, 1.0 if s == 0.0 else -1.0), 0.09, rope, turns=5,
                           pitch=0.028, rope_r=0.018)
        # Handrail posts and the rope rail along +X; two tarred stays from mid-span down to the decks.
        posts = (0.06, 0.5, 0.94)
        for s in posts:
            p = np.asarray(at(s, hw + 0.04))
            village_post(mb, p - np.array([0.0, 0.18, 0.0]), p + np.array([0.0, 0.95, 0.0]), 0.042, rng, noise, 6)
        for s0, s1 in zip(posts[:-1], posts[1:]):
            oc.rope(mb, np.asarray(at(s0, hw + 0.04, 0.9)), np.asarray(at(s1, hw + 0.04, 0.9)), 0.07, 0.018, rope)
        mid = np.asarray(at(0.5, 0.0, -0.12))
        for s, sgn in ((0.0, -1.0), (1.0, 1.0)):
            for off in (-hw, hw):
                oc.rope(mb, mid + np.array([off, 0.0, 0.0]), np.asarray(at(s, off * 1.3, -0.08)) +
                        np.array([0.0, 0.0, sgn * 0.3]), 0.01, 0.013, tar, n=4)
        out.append(mb)
    return out


def build_net_pen(seed: int = 706) -> list[kc.MeshBuilder]:
    out = []
    outer, walk = 12.0, 1.4
    half = outer * 0.5
    inner = half - walk
    for lod in (False, True):
        rng = kc.rng_for("net_pen", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("net_pen" + (oc.LOD if lod else ""))
        rope = mb.material(oc.M_ROPE)
        y = NET_PEN_Y
        # Four walkways (north and south run the full width; east and west between them).
        strips = [(-half, half, -half, -inner, True), (-half, half, inner, half, True),
                  (-half, -inner, -inner, inner, False), (inner, half, -inner, inner, False)]
        for x0, x1, z0, z1, ax in strips:
            oc.deck(mb, x0, x1, z0, z1, y, rng, noise, along_x=not ax, lod=lod, missing_p=0.02)
            # Floats under each walkway: three logs bound along it.
            if ax:
                _float_log(mb, rng, noise, (z0 + z1) * 0.5, x0 + 0.3, x1 - 0.3, 0.1, lod=lod, along_x=True, n=3)
            else:
                _float_log(mb, rng, noise, (x0 + x1) * 0.5, z0 - 0.4, z1 + 0.4, 0.1, lod=lod, n=3)
        if not lod:
            # The pen net: hung from the inner edges of the walkways down into the water (it reads in clear water).
            for a, b, side in (((-inner, y - 0.1, -inner), (inner, y - 0.1, -inner), (0, 0, 1)),
                               ((inner, y - 0.1, inner), (-inner, y - 0.1, inner), (0, 0, -1)),
                               ((-inner, y - 0.1, inner), (-inner, y - 0.1, -inner), (1, 0, 0)),
                               ((inner, y - 0.1, -inner), (inner, y - 0.1, inner), (-1, 0, 0))):
                oc.net(mb, a, b, 2.4, 0.05, nu=10, nv=5, side=side, belly=0.35)
            # Corner posts, and the practice net between the two north posts.
            for cx, cz in ((-inner, -inner), (inner, -inner), (-inner, inner), (inner, inner)):
                village_post(mb, (cx, y - 0.3, cz), (cx, y + (2.4 if cz < 0 else 1.2), cz), 0.08, rng, noise)
            oc.rope(mb, (-inner, y + 2.3, -inner), (inner, y + 2.3, -inner), 0.12, 0.02, rope, n=12)
            oc.net(mb, (-inner, y + 2.28, -inner), (inner, y + 2.28, -inner), 2.2, 0.12, nu=12, nv=6, noise=noise,
                   side=(0.0, 0.0, 1.0), belly=0.25)
            oc.rope(mb, (-inner, y + 1.1, inner), (inner, y + 1.1, inner), 0.1, 0.018, rope, n=12)
            # A short ladder into the pool on the south walkway, and floats on the head-rope.
            timber = mb.material(oc.M_TIMBER)
            for x in (-0.25, 0.25):
                kc.plank(mb, (x, -0.9, inner - 0.15), (x, y + 0.4, inner + 0.02), 0.05, 0.05, timber, variation=0.3)
            for k in range(4):
                yy = -0.6 + k * 0.33
                kc.plank(mb, (-0.25, yy, inner - 0.12 + 0.02 * k), (0.25, yy, inner - 0.12 + 0.02 * k), 0.04, 0.04,
                         timber, variation=0.5)
            glass = mb.material(oc.M_GLASS)
            for k in range(9):
                fx = -inner + (k + 0.5) * (2 * inner / 9)
                fy = y + 2.3 - 4.0 * 0.12 * ((fx + inner) / (2 * inner)) * (1 - (fx + inner) / (2 * inner)) - 0.06
                oc.lathe(mb, [(0.0, -0.06), (0.05, -0.04), (0.06, 0.0), (0.05, 0.04), (0.0, 0.06)], glass, sides=8,
                         at=(fx, fy, -inner + 0.03))
        else:
            for cx, cz in ((-inner, -inner), (inner, -inner)):
                kc.tube(mb, np.array([[cx, y, cz], [cx, y + 2.4, cz]]), 0.08, 4, mb.material(oc.M_TIMBER))
        out.append(mb)
    return out


TARGETS = {
    "hull_outrigger": build_hull_outrigger,
    "hull_cabin": build_hull_cabin,
    "raft_deck": build_raft_deck,
    "raft_deck_small": build_raft_deck_small,
    "raft_deck_tucked": build_raft_deck_tucked,
    "raft_deck_square": build_raft_deck_square,
    "raft_deck_small_tucked": build_raft_deck_small_tucked,
    "plank_bridge": build_plank_bridge,
    "net_pen": build_net_pen,
    "hull_lashed": build_hull_lashed,
}
