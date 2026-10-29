"""Corrow's story pieces, batch A (M3-ENV-707 for act1-chapters' request M3-ENV-1203). Pure numpy; see cw_common.py.

Each fits the greybox block it replaces in game/levels/ch08/corrow/corrow_layout.json (act1-chapters):

  stillguard_barracks  the Stillguard's barracks on the Bastion (block 12 x 3 x 6): a long laterite house, a watch-red
                       door at each end of its +Z front, shuttered windows, a tile roof, a shield rack by the door
  wall_gate            the wall-gate across the walk (block 0.6 x 4 x 6): laterite jambs and lintel, two watch-red
                       timber leaves with iron straps, standing open by a hand's breadth; the walk runs along X
  kite_line            the festival kites over the wall-head (block 80 x 2 x 0.2): cloth diamond kites strung along an
                       80 m line, each with its tail, their strings down to the parapet 12 m below
  kite_line_high       the same, 40 m, flying higher and fewer
  marra_step           Old Marra's doorstep (block 1.5 x 0.3 x 1): a worn stone step, her stool and a net half-mended
  hoist_pins           Liss's hoist pins (block 2 x 0.3 x 0.4): two iron pins and a lashing on a timber cross-bar
  hoist_rope           the rope (block 0.08 x 4 x 0.08), hung from y +2 to -2 about its centre
  hoist_basket         the lifting basket (block 0.8 x 0.6 x 0.8), woven, with its bridle
  trader_boat          the coastal trader that brings the party (block 3.6 x 2.4 x 12): a decked hull, a mast with its
                       sail furled on the yard, cargo bales; bow -Z

Origins: the block's foot centre, except the kite lines (the line's centre) and the hoist pieces (their centre).
"""

from __future__ import annotations

import math

import numpy as np

import cw_common as cw
from cw_common import kc

M_WATCH_RED = "cw_watch_red"
M_KITES = ("cw_kite_ochre", "cw_kite_red", "cw_kite_teal", "cw_kite_white")
M_SAIL = "cw_sail"
M_WICKER = "cw_wicker"
# Haluna slots that reused Haluna pieces bring in (the net heap) -> this kit's own (cw_materials.py).
STORY_RENAME = {"kit_net": "cw_net", "kit_salt_glass": "cw_glass", "kit_woven_panel": M_WICKER}


def _own_slots(mb: kc.MeshBuilder) -> kc.MeshBuilder:
    mb.materials = [STORY_RENAME.get(m, m) for m in mb.materials]
    return mb

TRI_BUDGET = {
    "stillguard_barracks": (14000, 1200),
    "wall_gate": (5000, 400),
    "kite_line": (6000, 600),
    "marra_step": (2500, 200),
    "hoist_pins": (800, 80),
    "hoist_rope": (300, 30),
    "hoist_basket": (1500, 120),
    "trader_boat": (12000, 1000),
    "mole_pier": (40000, 2000),
    "mole_sea_stair": (12000, 600),
    "bastion_platform": (90000, 3000),
}
BUDGET_KEY = {"kite_line_high": "kite_line"}


def _block(mb, c, half, mat, rng, noise, *, rot=None, lod=False, w=cw.TOWN_W):
    kc.rounded_block(mb, c, half, mat, rot=rot, radius=0.04 if not lod else 0.02, seg=1 if lod else 2,
                     noise=None if lod else noise, disp_m=0.02, disp_period_m=0.4, weather=w,
                     variation=float(rng.random()))


def build_barracks(seed: int = 881, *, w: float = 11.6, d: float = 5.6, wall_h: float = 2.6) -> list[kc.MeshBuilder]:
    import village  # noqa: PLC0415  (the Haluna kit's hip roof, read-only)

    out = []
    for lod in (False, True):
        rng = kc.rng_for("stillguard_barracks", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("stillguard_barracks" + (cw.LOD if lod else ""))
        i_st, i_t, i_red, i_dk, i_ir = (mb.material(cw.M_HOUSE), mb.material(cw.M_TIMBER), mb.material(M_WATCH_RED),
                                         mb.material(cw.M_DARK), mb.material(cw.M_IRON))
        hw, hd = w * 0.5, d * 0.5
        _block(mb, (0, wall_h * 0.5, 0), (hw, wall_h * 0.5, hd), i_st, rng, noise, lod=lod)
        doors = (-hw + 1.4, hw - 1.4)
        for x in doors:
            kc.rounded_block(mb, (x, 1.05, hd + 0.02), (0.55, 1.05, 0.04), i_red, seg=1, radius=0.01)
            if not lod:
                kc.plank(mb, (x - 0.8, 2.2, hd + 0.12), (x + 0.8, 2.2, hd + 0.12), 0.16, 0.14, i_t,
                         variation=float(rng.random()), noise=noise)
                for y in (0.5, 1.6):
                    kc.plank(mb, (x - 0.5, y, hd + 0.07), (x + 0.45, y, hd + 0.07), 0.06, 0.012, i_ir)
        for k in range(4 if not lod else 0):
            x = -hw + 3.2 + k * (w - 6.4) / 3.0
            c = np.array([x, 1.6, hd + 0.03])
            kc.rounded_block(mb, c, (0.4, 0.4, 0.02), i_dk, seg=1, radius=0.004)
            kc.rounded_block(mb, c + [0, 0, 0.03], (0.42, 0.42, 0.02), i_red, seg=1, radius=0.004)
        if not lod:
            # A shield rack by the west door: four round shields, watch-red rims, on a timber rail.
            kc.plank(mb, (doors[0] + 0.9, 1.25, hd + 0.25), (doors[0] + 3.0, 1.25, hd + 0.25), 0.08, 0.08, i_t)
            for k in range(4):
                c = np.array([doors[0] + 1.1 + k * 0.55, 0.85, hd + 0.33])
                a = np.linspace(0.0, 2 * math.pi, 17)
                ring = np.stack([c[0] + np.cos(a) * 0.3, c[1] + np.sin(a) * 0.3, np.full_like(a, c[2])], axis=-1)
                kc.tube(mb, ring, 0.025, 4, i_red)
                kc.tube(mb, np.array([c - [0, 0, 0.02], c + [0, 0, 0.02]]), 0.29, 16, i_t, cap_start=True,
                        cap_end=True, variation=float(rng.random()))
        village.hip_roof(mb, w + 1.0, d + 1.0, wall_h - 0.05, rng, noise, kind="tile", lod=lod)
        out.append(mb)
    return out


def build_wall_gate(seed: int = 882) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("wall_gate", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("wall_gate" + (cw.LOD if lod else ""))
        i_lat, i_red, i_ir = mb.material(cw.M_LATERITE), mb.material(M_WATCH_RED), mb.material(cw.M_IRON)
        for z in (-2.75, 2.75):
            _block(mb, (0.0, 1.9, z), (0.35, 1.9, 0.3), i_lat, rng, noise, lod=lod, w=cw.WALL_W)
        _block(mb, (0.0, 3.85, 0.0), (0.4, 0.3, 3.1), i_lat, rng, noise, lod=lod, w=cw.WALL_W)
        # The two leaves, hung on the jambs, swung a little inland (-X), a gap between them.
        for side, ang in ((-1.0, 0.25), (1.0, -0.22)):
            hinge = np.array([0.0, 0.0, side * 2.42])
            rot = kc.rot_y(ang)
            c = hinge + rot @ np.array([0.0, 1.75, -side * 1.18])
            kc.rounded_block(mb, c, (0.06, 1.7, 1.18), i_red, rot=rot, radius=0.01, seg=1 if lod else 2,
                             noise=None if lod else noise, disp_m=0.003, variation=float(rng.random()))
            if not lod:
                for y in (0.5, 1.75, 3.0):
                    a = hinge + rot @ np.array([0.08, y, 0.0])
                    b = hinge + rot @ np.array([0.08, y, -side * 2.2])
                    kc.plank(mb, a, b, 0.09, 0.015, i_ir, up=rot @ np.array([1.0, 0.0, 0.0]))
        out.append(mb)
    return out


def build_kite_line(seed: int = 883, *, length: float = 80.0, n: int = 26, drop: float = 12.0,
                    name: str = "kite_line") -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        mb = kc.MeshBuilder(name + (cw.LOD if lod else ""))
        rope = mb.material(cw.M_ROPE)
        count = n if not lod else n // 2
        for k in range(count):
            x = -length * 0.5 + (k + 0.5) * length / count + rng.normal(0, 0.6)
            c = np.array([x, rng.normal(0, 0.35), rng.normal(0, 0.06)])
            s = rng.uniform(0.55, 0.85)
            tilt = rng.normal(0, 0.25)
            up = np.array([math.sin(tilt), math.cos(tilt), 0.0])
            side = np.array([math.cos(tilt), -math.sin(tilt), 0.0])
            # A diamond of cloth on two crossed sticks, its long axis up, faced toward the town (-Z) and the sea.
            pts = np.array([c + up * s * 1.2, c + side * s * 0.6, c - up * s * 0.8, c - side * s * 0.6])
            mat = mb.material(M_KITES[int(rng.integers(0, len(M_KITES)))])
            for flip in (False, True):
                base = mb.add_vertices(np.vstack([pts, [c]]), np.tile([0.0, 0.0, -1.0 if flip else 1.0], (5, 1)),
                                       np.array([[0.5, 1], [1, 0.5], [0.5, 0], [0, 0.5], [0.5, 0.5]]),
                                       np.tile([0.9, float(rng.random())], (5, 1)), np.tile([0, 0.1, 0, 0.1], (5, 1)))
                for i in range(4):
                    tri = (base + 4, base + i, base + (i + 1) % 4)
                    mb.add_tri(*(tri if not flip else (tri[0], tri[2], tri[1])), mat)
            if lod:
                continue
            # The tail: a ribbon of the same cloth lifting away downwind (+X).
            t = np.linspace(0.0, 1.0, 6)
            tail = (c - up * s * 0.8)[None, :] + np.stack([t * 1.6, -t * 1.0 + 0.25 * np.sin(t * 6.0 + k),
                                                            np.zeros_like(t)], axis=-1)
            wdt = 0.06 * (1.0 - t * 0.6)
            grid = np.stack([tail - [0, 0, 0] - np.outer(wdt, [0, 1, 0]), tail + np.outer(wdt, [0, 1, 0])], axis=1)
            uv = np.stack([np.tile([0.0, 1.0], (6, 1)), np.tile(t[:, None], (1, 2))], axis=-1)
            for flip in (False, True):
                kc.quad_strip(mb, grid, mat, uv=uv, col=np.array([0.0, 0.1, 0.0, 0.1]), uv2=np.array([0.9, 0.5]),
                              flip=flip)
            # The string, sagging down to the parapet a little upwind.
            ts = np.linspace(0.0, 1.0, 7)
            end = c + np.array([-3.0 + rng.normal(0, 1.0), -drop, rng.normal(0, 0.3)])
            string = c[None, :] * (1 - ts[:, None]) + end[None, :] * ts[:, None]
            string[:, 1] -= 1.2 * np.sin(ts * math.pi)
            kc.tube(mb, string, 0.006, 3, rope, variation=0.5)
        out.append(mb)
    return out


def build_marra_step(seed: int = 884) -> list[kc.MeshBuilder]:
    import dressing  # noqa: PLC0415  (the Haluna kit's net heap, read-only)

    out = []
    for lod in (False, True):
        rng = kc.rng_for("marra_step", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("marra_step" + (cw.LOD if lod else ""))
        _block(mb, (0.0, 0.15, 0.0), (0.75, 0.15, 0.5), mb.material(cw.M_HOUSE), rng, noise, lod=lod)
        if not lod:
            # Her stool, and the net she is mending heaped beside it, one edge drawn up over the stool's rail.
            t = mb.material(cw.M_TIMBER)
            for sx in (-1, 1):
                for sz in (-1, 1):
                    kc.tube(mb, np.array([[0.35 + sx * 0.14, 0.3, sz * 0.14], [0.35 + sx * 0.11, 0.7, sz * 0.11]]),
                            0.02, 4, t, cap_end=True)
            kc.rounded_block(mb, (0.35, 0.72, 0.0), (0.17, 0.03, 0.17), t, radius=0.01, seg=1)
            heap = dressing.build_net_heap()[0]
            mb.merge(heap, np.diag([0.45, 0.5, 0.45]), offset=(-0.3, 0.3, 0.05))
        out.append(_own_slots(mb))
    return out


def build_hoist_pins(seed: int = 885) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("hoist_pins", seed)
        mb = kc.MeshBuilder("hoist_pins" + (cw.LOD if lod else ""))
        kc.plank(mb, (-0.95, 0.0, 0.0), (0.95, 0.0, 0.0), 0.16, 0.14, mb.material(cw.M_TIMBER),
                 variation=float(rng.random()))
        for x in (-0.6, 0.6):
            kc.tube(mb, np.array([[x, -0.15, 0.0], [x, 0.15, 0.0]]), 0.03, 6 if not lod else 4, mb.material(cw.M_IRON),
                    cap_start=True, cap_end=True)
        if not lod:
            a = np.linspace(0.0, 2 * math.pi, 9)
            ring = np.stack([np.zeros_like(a), np.cos(a) * 0.1, np.sin(a) * 0.09], axis=-1)
            kc.tube(mb, ring, 0.015, 4, mb.material(cw.M_ROPE), variation=0.4)
        out.append(mb)
    return out


def build_hoist_rope(seed: int = 886) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("hoist_rope" + (cw.LOD if lod else ""))
        y = np.linspace(2.0, -2.0, 9 if not lod else 2)
        pts = np.stack([0.012 * np.sin(y * 3.0), y, np.zeros_like(y)], axis=-1)
        kc.tube(mb, pts, 0.02, 5 if not lod else 3, mb.material(cw.M_ROPE), variation=0.4, u_repeat=3.0)
        out.append(mb)
    return out


def build_hoist_basket(seed: int = 887) -> list[kc.MeshBuilder]:
    import props  # noqa: PLC0415  (the Haluna kit's lathe, read-only)

    out = []
    for lod in (False, True):
        rng = kc.rng_for("hoist_basket", seed)
        mb = kc.MeshBuilder("hoist_basket" + (cw.LOD if lod else ""))
        props.lathe(mb, [(0.3, -0.3), (0.38, -0.2), (0.4, 0.15), (0.41, 0.2)], M_WICKER, rng,
                    sides=16 if not lod else 6)
        if not lod:
            for a in (0.4, 0.4 + 2 * math.pi / 3, 0.4 + 4 * math.pi / 3):
                kc.tube(mb, np.array([[math.cos(a) * 0.4, 0.2, math.sin(a) * 0.4], [0.0, 0.3, 0.0]]), 0.012, 4,
                        mb.material(cw.M_ROPE))
        out.append(mb)
    return out


TRADER_BALE_MATS = ("cw_kite_ochre", M_WICKER, "cw_kite_red", M_WICKER)


def _bale(mb, c, half, mat_name: str, rng, noise) -> None:
    """A bale or crate of cargo: a soft block bulging under two rope bands (across its length and its width)."""
    c = np.asarray(c, float)
    yaw = float(rng.normal(0.0, 0.12))
    rot = kc.rot_y(yaw)
    kc.rounded_block(mb, c, half, mb.material(mat_name), rot=rot, radius=min(half) * 0.45, seg=3, noise=noise,
                     disp_m=0.04, disp_period_m=0.2, variation=float(rng.random()))
    hx, hy, hz = half
    # Two bands round its length and one round its width, drawn tight just outside the softened corners.
    for ax, frac in (("z", -0.45), ("z", 0.45), ("x", 0.0)):
        a, b = (hx + 0.02, hy + 0.02) if ax == "z" else (hz + 0.02, hy + 0.02)
        k = 0.7  # the band pulls the corners in
        pts = [(a * k, b), (a, b * k), (a, -b * k), (a * k, -b), (-a * k, -b), (-a, -b * k), (-a, b * k), (-a * k, b),
               (a * k, b)]
        if ax == "z":
            ring = np.array([[u, v, frac * hz] for u, v in pts])
        else:
            ring = np.array([[frac * hx, v, u] for u, v in pts])
        kc.tube(mb, ring @ rot.T + c, 0.018, 4, mb.material(cw.M_ROPE), variation=0.3)


def build_trader_boat(seed: int = 888, *, length: float = 11.6, beam: float = 3.4) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("trader_boat", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("trader_boat" + (cw.LOD if lod else ""))
        tm, deck = mb.material(cw.M_TIMBER), mb.material(cw.M_TIMBER)
        half_l = length * 0.5
        T = np.linspace(-1.0, 1.0, 17 if not lod else 7)
        F = np.linspace(0.0, 1.0, 7 if not lod else 3)

        def hull_pt(f, t, side):
            half = beam * 0.5 * (1 - abs(t) ** 2.2) ** 0.6 + 0.03
            y = 0.1 + f * 1.5 + 0.35 * t ** 2
            x = side * half * (0.2 + 0.8 * math.sin(f * math.pi * 0.5))
            return np.array([x, y, t * half_l])

        for side in (-1.0, 1.0):
            grid = np.array([[hull_pt(f, t, side) for t in T] for f in F])
            uv = np.stack(np.meshgrid(T * half_l, F * 1.5), axis=-1)
            for flip in (False, True):
                kc.quad_strip(mb, grid, tm, uv=uv, col=np.array([0.0, 0.5, 0.3, 0.6]),
                              uv2=np.array([0.85 if flip else 1.0, float(rng.random())]), flip=(side > 0) != flip)
            if not lod:
                for f in F[1:]:
                    lap = np.array([hull_pt(f, t, side * 1.01) for t in T])
                    kc.tube(mb, lap, 0.02, 4, tm, weather=cw.TOWN_W, variation=float(rng.random()))
        # The deck at the sheer, the stem post, the mast, the yard with its sail furled, cargo under a tarpaulin.
        kc.rounded_block(mb, (0.0, 1.45, 0.0), (beam * 0.42, 0.04, half_l * 0.86), deck, radius=0.02, seg=1)
        kc.tube(mb, np.array([[0.0, 0.1, -half_l], [0.0, 2.3, -half_l - 0.4]]), 0.09, 5, tm, cap_end=True)
        mast = np.array([0.0, 1.45, -half_l * 0.25])
        kc.tube(mb, np.array([mast, mast + [0, 8.5, 0]]), np.array([0.13, 0.08]), 8 if not lod else 4, tm,
                cap_end=True, variation=0.4)
        yard_y = mast[1] + 7.4
        kc.tube(mb, np.array([[-3.2, yard_y, mast[2]], [3.2, yard_y, mast[2]]]), 0.06, 6 if not lod else 3, tm,
                cap_start=True, cap_end=True)
        if not lod:
            a = np.linspace(-3.0, 3.0, 13)
            furl = np.stack([a, np.full_like(a, yard_y - 0.18) - 0.06 * np.cos(a * 2.0), np.full_like(a, mast[2])],
                            axis=-1)
            kc.tube(mb, furl, 0.16 - 0.02 * np.abs(a) / 3.0, 8, mb.material(M_SAIL), variation=0.5)
            for side in (-1.0, 1.0):
                kc.tube(mb, np.array([mast + [0, 8.3, 0], [side * beam * 0.45, 1.5, mast[2] + 0.3]]), 0.012, 3,
                        mb.material(cw.M_ROPE))
            kc.tube(mb, np.array([mast + [0, 8.3, 0], [0.0, 2.2, -half_l - 0.3]]), 0.012, 3, mb.material(cw.M_ROPE))
            # The cargo (M3-ENV-1316: plain sail-white blocks read as cubes at Act I's near range): cloth-wrapped bales
            # in dyed cloth and wicker crates, each bulging under two rope bands, set down a little askew.
            for k, (x, z, s) in enumerate(((-0.6, 1.2, 0.5), (0.6, 1.4, 0.45), (0.0, 2.6, 0.55), (-0.5, 3.4, 0.4))):
                _bale(mb, (x, 1.49 + s * 0.8, z), (s, s * 0.8, s * 0.9), TRADER_BALE_MATS[k % len(TRADER_BALE_MATS)],
                      rng, noise)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Batch B: the harbour mole and its sea stair, the Bastion (corrow_collision.json's blocks and ramps)
# ---------------------------------------------------------------------------------------------
MOLE_HALF_W = 2.2  # MolePier 4.4 m
MOLE_LEN = 26.0
MOLE_FOOT = -3.2  # below its deck (the pier block is 3.2 m deep)
MOLE_END_H = 2.8  # MoleEnd stands from the foot to 2.8 m over the deck
STAIR_RUN, STAIR_RISE, STAIR_HALF_W = 21.8, 11.7, 2.0  # MoleRamp: the pier's root to the parapet's top
STAIR_TOP_RUN, STAIR_DOWN_RUN, STAIR_DOWN_DROP = 1.2, 2.0, 0.9  # MoleOverParapet, MoleDown
BASTION_HALF = (21.0, 12.25)  # BastionPlatform 42 x 24.5
BASTION_H = 11.0  # the town (y 1) to the walk's height (y 12)
RIM = (1.2, 0.9)  # BastionRim*: thick, high


def _rows(y0: float, y1: float, coarse: bool) -> np.ndarray:
    return np.linspace(y0, y1, max(2, int((y1 - y0) / (0.125 if not coarse else 2.0)) + 1))


def _cols(x0: float, x1: float, coarse: bool) -> np.ndarray:
    return np.linspace(x0, x1, max(2, int((x1 - x0) / (0.6 if not coarse else 6.0)) + 1))


def _battered_face(mb, x0, x1, y0, y1, z_top, batter_deg, rng, noise, *, sea, lod, rot=None, offset=(0, 0, 0)):
    """A coursed face along X at z = z_top at y1, leaning back toward -Z by `batter_deg` (its foot further out
    toward -Z), facing -Z; built in a temp builder and merged with `rot`/`offset` (so it can face any side)."""
    import cw_wall  # noqa: PLC0415

    tan_b = math.tan(math.radians(batter_deg))
    tmp = kc.MeshBuilder("face")
    nrm = kc.normalize(np.array([0.0, tan_b, -1.0]))
    cw_wall._face(tmp, _cols(x0, x1, lod), _rows(y0, y1, lod), lambda y: z_top - (y1 - np.asarray(y, float)) * tan_b,
                  (nrm[1], nrm[2]), rng, noise, mat=tmp.material(cw.M_LATERITE), sea=sea, coarse=lod)
    mb.merge(tmp, rot, offset)


def build_mole_pier(seed: int = 891) -> list[kc.MeshBuilder]:
    """The harbour mole: a coursed laterite pier 4.4 m wide running 26 m out to sea (+Z) from its root at the
    origin (deck top y 0, foot -3.2), a breakwater wall at its head, timber bollards and iron rings, a ladder."""
    import cw_wall  # noqa: PLC0415

    out = []
    for lod in (False, True):
        rng = kc.rng_for("mole_pier", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("mole_pier" + (cw.LOD if lod else ""))
        w = MOLE_HALF_W
        # The long sides (facing -X and +X), and the head's sea face (+Z).
        _battered_face(mb, 0.0, MOLE_LEN, MOLE_FOOT, 0.0, -w, 4.0, rng, noise, sea=True, lod=lod,
                       rot=kc.rot_y(-math.pi * 0.5))  # x' = -z: a face at z=-w becomes x = +w? see below
        _battered_face(mb, -MOLE_LEN, 0.0, MOLE_FOOT, 0.0, -w, 4.0, rng, noise, sea=True, lod=lod,
                       rot=kc.rot_y(math.pi * 0.5))
        _battered_face(mb, -w, w, MOLE_FOOT, MOLE_END_H, -0.0, 3.0, rng, noise, sea=True, lod=lod,
                       rot=kc.rot_y(math.pi), offset=(0.0, 0.0, MOLE_LEN + 0.5))
        # The deck: paving slabs across, the head wall's back face and coping.
        cw_wall._flat(mb, cw_wall._walk_cols(-w, w) if not lod else np.array([-w, w]),
                      cw_wall._walk_rows(0.0, MOLE_LEN) if not lod else np.array([0.0, MOLE_LEN]), 0.0,
                      mb.material(cw.M_PAVING), outward=(0.0, 1.0, 0.0), col=(0.0, 0.5, 0.4, 0.5))
        _block(mb, (0.0, MOLE_END_H * 0.5, MOLE_LEN + 0.25), (w + 0.5, MOLE_END_H * 0.5, 0.25),
               mb.material(cw.M_LATERITE), rng, noise, lod=lod, w=cw.WALL_W)
        _block(mb, (0.0, MOLE_END_H + 0.1, MOLE_LEN + 0.25), (w + 0.6, 0.1, 0.35), mb.material(cw.M_PAVING), rng,
               noise, lod=lod, w=cw.WALL_W)
        if not lod:
            tm, ir = mb.material(cw.M_TIMBER), mb.material(cw.M_IRON)
            for k, z in enumerate(np.arange(3.0, MOLE_LEN - 1.0, 5.0)):
                for side in (-1.0, 1.0):
                    if (k + (side > 0)) % 2:
                        continue
                    p = np.array([side * (w - 0.35), 0.0, z])
                    kc.tube(mb, np.array([p, p + [0, 0.75, 0]]), np.array([0.16, 0.13]), 8, tm, cap_end=True,
                            variation=float(rng.random()))
                    a = np.linspace(0.0, 2 * math.pi, 9)
                    ring = np.stack([np.full_like(a, side * (w + 0.06)), -0.4 + np.sin(a) * 0.09,
                                     z + 2.4 + np.cos(a) * 0.09], axis=-1)
                    kc.tube(mb, ring, 0.014, 4, ir)
            # An iron ladder down the +X side to the water, near the head.
            for dz in (-0.25, 0.25):
                kc.tube(mb, np.array([[w + 0.1, 0.4, MOLE_LEN - 4.0 + dz], [w + 0.1, MOLE_FOOT, MOLE_LEN - 4.0 + dz]]),
                        0.02, 5, ir)
            for y in np.arange(MOLE_FOOT + 0.3, 0.2, 0.3):
                kc.tube(mb, np.array([[w + 0.1, y, MOLE_LEN - 4.25], [w + 0.1, y, MOLE_LEN - 3.75]]), 0.015, 4, ir)
        out.append(mb)
    return out


def build_mole_sea_stair(seed: int = 892) -> list[kc.MeshBuilder]:
    """The sea stair from the mole's root (origin, y 0) up to the parapet's top (rise 11.7 over 21.8 m toward
    -Z), across the parapet's gap (1.2 m) and down 0.9 m onto the walk (2 m): a stone stairway built out
    from the wall's sea face on a solid battered body, with a low parapet each side."""
    out = []
    for lod in (False, True):
        rng = kc.rng_for("mole_sea_stair", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("mole_sea_stair" + (cw.LOD if lod else ""))
        i_lat, i_pave = mb.material(cw.M_LATERITE), mb.material(cw.M_PAVING)
        hw = STAIR_HALF_W
        n = 47
        rise, run = STAIR_RISE / n, STAIR_RUN / n
        if lod:
            # The body as two side wedges and a ramp.
            for sx in (-1.0, 1.0):
                pts = np.array([[0.0, MOLE_FOOT], [0.0, 0.0], [-STAIR_RUN, STAIR_RISE], [-STAIR_RUN, MOLE_FOOT]])
                tmp = kc.MeshBuilder("w")
                kc.polygon_prism(tmp, pts, -0.3, 0.3, tmp.material(cw.M_LATERITE), col=np.array([0.0, 0.5, 0.3, 0.5]),
                                 uv2=np.array([1.0, 0.5]), top=True, bottom=True)
                mb.merge(tmp, kc.rot_z(-math.pi * 0.5) @ kc.rot_y(-math.pi * 0.5), (sx * (hw + 0.3), 0.0, 0.0))
            kc.rounded_block(mb, (0.0, STAIR_RISE * 0.5, -STAIR_RUN * 0.5), (hw, 0.15, STAIR_RUN * 0.5 + 0.2), i_pave,
                             rot=kc.rot_x(math.atan2(STAIR_RISE, STAIR_RUN)), seg=1, radius=0.02)
            out.append(mb)
            continue
        for k in range(n):
            y = (k + 1) * rise
            z = -(k + 0.5) * run
            _block(mb, (0.0, y - 0.12, z), (hw, 0.12 + (0.02 if k else 0.0), run * 0.5 + 0.03), i_pave, rng, noise,
                   w=cw.WALL_W)
        # The body under the flight: a coursed face each side, a sloped soffit fill of rubble masonry.
        for sx, a in ((-1.0, math.pi * 0.5), (1.0, -math.pi * 0.5)):
            for k in range(0, n, 4):
                z0 = -k * run
                top = (k + 1) * rise - 0.24
                _block(mb, (sx * (hw + 0.3), (top + MOLE_FOOT) * 0.5, z0 - run * 2.0),
                       (0.3, (top - MOLE_FOOT) * 0.5, run * 2.0 + 0.02), i_lat, rng, noise, w=cw.WALL_W)
            # The side parapet: a rail of laterite blocks following the flight, 0.6 m over the treads.
            for k in range(0, n, 3):
                y = (k + 1.5) * rise
                _block(mb, (sx * (hw + 0.3), y + 0.3, -(k + 1.5) * run), (0.3, 0.32, run * 1.5 + 0.02), i_lat, rng,
                       noise, w=cw.WALL_W)
            del a
        # Over the parapet's gap and down onto the walk.
        top = STAIR_RISE
        _block(mb, (0.0, top - 0.12, -STAIR_RUN - STAIR_TOP_RUN * 0.5), (hw, 0.12, STAIR_TOP_RUN * 0.5 + 0.02), i_pave,
               rng, noise, w=cw.WALL_W)
        for k in range(4):
            y = top - (k + 1) * STAIR_DOWN_DROP / 4
            z = -STAIR_RUN - STAIR_TOP_RUN - (k + 0.5) * STAIR_DOWN_RUN / 4
            _block(mb, (0.0, y - 0.12, z), (hw, 0.12, STAIR_DOWN_RUN / 8 + 0.02), i_pave, rng, noise, w=cw.WALL_W)
        out.append(mb)
    return out


def build_bastion_platform(seed: int = 893) -> list[kc.MeshBuilder]:
    """The Bastion's raised ground: battered laterite revetments on the town sides (-Z, -X, +X) from the town
    (origin, y 0) to the walk's height (y 11), corner quoins, paving on top, and the low rim wall on those three
    sides; the +Z side meets the wall-head walk."""
    import cw_wall  # noqa: PLC0415

    out = []
    hx, hz = BASTION_HALF
    for lod in (False, True):
        rng = kc.rng_for("bastion_platform", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("bastion_platform" + (cw.LOD if lod else ""))
        top = BASTION_H
        _battered_face(mb, -hx, hx, -0.4, top, -hz, cw.INNER_BATTER_DEG, rng, noise, sea=False, lod=lod)
        _battered_face(mb, -hz, hz, -0.4, top, -hx, cw.INNER_BATTER_DEG, rng, noise, sea=False, lod=lod,
                       rot=kc.rot_y(math.pi * 0.5))
        _battered_face(mb, -hz, hz, -0.4, top, -hx, cw.INNER_BATTER_DEG, rng, noise, sea=False, lod=lod,
                       rot=kc.rot_y(-math.pi * 0.5))
        tan_b = math.tan(math.radians(cw.INNER_BATTER_DEG))
        for sx in (-1.0, 1.0):
            # Quoins: a stepped pier of dressed blocks hides where two battered faces meet.
            for y0 in np.arange(-0.4, top, 1.0 if not lod else top + 0.4):
                spread = (top - y0) * tan_b
                _block(mb, (sx * (hx + spread * 0.6), y0 + 0.5 if not lod else top * 0.5, -hz - spread * 0.6),
                       (0.8, 0.5 if not lod else (top + 0.4) * 0.5, 0.8), mb.material(cw.M_CARVED), rng, noise,
                       lod=lod, w=cw.WALL_W)
        cw_wall._flat(mb, cw_wall._walk_cols(-hx, hx) if not lod else np.array([-hx, hx]),
                      cw_wall._walk_rows(-hz, hz) if not lod else np.array([-hz, hz]), top, mb.material(cw.M_PAVING),
                      outward=(0.0, 1.0, 0.0), col=(0.0, 0.35, 0.1, 0.5))
        th, rh = RIM
        # Rim segments of 6 m: along the -Z edge, and up each side to 0.5 m short of the walk (+Z) edge.
        segs = [((x, top + rh * 0.5, -hz + th * 0.5), (3.0, rh * 0.5, th * 0.5)) for x in np.arange(-hx + 3.0, hx, 6.0)]
        zs = np.linspace(-hz + th, hz - 0.5, 5)
        segs += [((sx * (hx - th * 0.5), top + rh * 0.5, (a + b) * 0.5), (th * 0.5, rh * 0.5, (b - a) * 0.5))
                 for sx in (-1.0, 1.0) for a, b in zip(zs[:-1], zs[1:])]
        for c, half in segs:
            _block(mb, c, half, mb.material(cw.M_LATERITE), rng, noise, lod=lod, w=cw.WALL_W)
        out.append(mb)
    return out


TARGETS = {
    "stillguard_barracks": build_barracks,
    "wall_gate": build_wall_gate,
    "kite_line": build_kite_line,
    "kite_line_high": lambda: build_kite_line(seed=889, length=40.0, n=11, drop=15.0, name="kite_line_high"),
    "marra_step": build_marra_step,
    "hoist_pins": build_hoist_pins,
    "hoist_rope": build_hoist_rope,
    "hoist_basket": build_hoist_basket,
    "trader_boat": build_trader_boat,
    "mole_pier": build_mole_pier,
    "mole_sea_stair": build_mole_sea_stair,
    "bastion_platform": build_bastion_platform,
}
