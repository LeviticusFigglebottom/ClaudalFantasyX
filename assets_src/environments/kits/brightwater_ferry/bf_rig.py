"""The ferry's rig (M3-ENV-08; brightwater_ferry.md §0, §2). Pure numpy; see bf_common.py.

  ferry_rig   both masts, the Low Reaches lugs (a four-sided sail on each mast, its yard slung steeply aft, its
              foot on a boom; sand cloth in panels with a sea-blue reef band and a few patches), set and filled
              by the trade wind on the starboard beam (the sails belly to port), the shrouds down to the hull's
              chain-plates (ratlines on the mainmast's), the forestay to the bowsprit, the spring stay between
              the mastheads, halyards and sheets, and the lookout's perch on the mainmast.

In the hull's frame (bf_hull.ferry_hull), so it drops onto the same origin.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

import bf_common as bf
from bf_common import kc

TRI_BUDGET = {"ferry_rig": (40000, 4000)}
F = bf.FERRY
PERCH_Y = 11.6  # the lookout's perch, above the main deck
PERCH_R = 0.62
HOUNDS_FRAC = 0.86  # where the shrouds meet the mast
WIND_FROM_DEG = 70.0  # the trade wind, from the east-north-east (the starboard beam)
FIFE_DZ = {bf.FOREMAST_Z: 0.75, bf.MAINMAST_Z: -0.75}  # bf_hull's fife rails (the halyards belay there)


@dataclass(frozen=True)
class Lug:
    """One lug sail in its mast's plane: (along, height) of the tack, clew, throat and peak, `along` measured aft
    along the boom's line, which is swung `sheet_deg` off the centre line to port."""

    mast_z: float
    mast_h: float
    mast_r: float
    tack: tuple
    clew: tuple
    throat: tuple
    peak: tuple
    sheet_deg: float
    belly: float  # camber, as a fraction of the foot


FORE = Lug(bf.FOREMAST_Z, bf.FOREMAST_H, 0.13, (-1.3, 2.95), (5.0, 3.2), (-1.6, 7.0), (5.2, 12.3), 26.0, 0.085)
MAIN = Lug(bf.MAINMAST_Z, bf.MAINMAST_H, 0.15, (-1.4, 2.75), (6.0, 3.05), (-1.9, 8.6), (6.3, 15.3), 21.0, 0.08)
REEF_BAND = (0.15, 0.205)  # the sea-blue band across the sail (fraction of the luff, from the foot)
PANELS = 8


def aft_dir(lug: Lug) -> np.ndarray:
    a = math.radians(lug.sheet_deg)
    return np.array([-math.sin(a), 0.0, math.cos(a)])


def lee_normal(lug: Lug) -> np.ndarray:
    """The sail's normal on its lee side (port, -X): the side it bellies to."""
    n = np.cross(aft_dir(lug), kc.UP)
    return n if n[0] < 0.0 else -n


def sail_point(lug: Lug, along: float, height: float) -> np.ndarray:
    """A point of the sail's plane: aft along the boom's line, up from the main deck, set off the mast to lee."""
    base = np.array([0.0, 0.0, lug.mast_z])
    return base + aft_dir(lug) * along + np.array([0.0, height, 0.0]) + lee_normal(lug) * (lug.mast_r + 0.05)


def sail_surface(lug: Lug, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """The filled sail at (u along the foot, v up the luff), both in [0, 1]: bilinear between the boom and the
    yard, bellied to lee most at mid-height a third of the way aft; the leech hollows a little."""
    T, C, H, P = (sail_point(lug, *c) for c in (lug.tack, lug.clew, lug.throat, lug.peak))
    u = np.asarray(u, float)[..., None]
    v = np.asarray(v, float)[..., None]
    p = (1.0 - v) * ((1.0 - u) * T + u * C) + v * ((1.0 - u) * H + u * P)
    foot = float(np.linalg.norm(C - T))
    camber = lug.belly * foot * np.sin(np.pi * u) ** 0.85 * np.sin(np.pi * np.clip(v, 0.0, 1.0)) ** 0.7
    camber = camber * (1.0 - 0.25 * v) * (1.0 - 0.35 * np.clip(u - 0.6, 0.0, 1.0))
    hollow = 0.04 * foot * np.sin(np.pi * v) * kc.smoothstep(0.85, 1.0, u)
    return p + lee_normal(lug) * camber - aft_dir(lug) * hollow


def yard_line(lug: Lug) -> tuple[np.ndarray, np.ndarray]:
    H = sail_point(lug, *lug.throat)
    P = sail_point(lug, *lug.peak)
    d = kc.normalize(P - H)
    return H - d * 0.35, P + d * 0.3


def _mast(mb: kc.MeshBuilder, lug: Lug, noise, *, lod: bool) -> None:
    i_t = mb.material(bf.M_TIMBER)
    z = lug.mast_z
    h = np.linspace(-0.4, lug.mast_h, 3 if lod else 8)
    r = lug.mast_r * (1.0 - 0.35 * np.clip(h / lug.mast_h, 0, 1) ** 1.3)
    kc.tube(mb, np.stack([np.zeros_like(h), h, np.full_like(h, z)], -1), r, 6 if lod else 12, i_t, weather=bf.RAIL_W,
            noise=None if lod else noise, disp_m=0.004, cap_end=True)
    # The truck (a cap) and the partners' wedged collar at the deck.
    bf.lathe(mb, (0.0, lug.mast_h - 0.02, z), [(0.0, 0.0), (0.12, 0.02), (0.12, 0.12), (0.0, 0.16)], 6 if lod else 10,
             bf.M_TIMBER)
    if not lod:
        bf.lathe(mb, (0.0, 0.0, z), [(lug.mast_r + 0.14, 0.0), (lug.mast_r + 0.1, 0.12), (lug.mast_r + 0.01, 0.2)], 12,
                 bf.M_TAR, weather=bf.RAIL_W)
        # The hounds: a cheek block either side where the shrouds bear.
        yh = lug.mast_h * HOUNDS_FRAC
        for s in (-1.0, 1.0):
            kc.rounded_block(mb, (s * lug.mast_r * 0.75, yh, z), (0.05, 0.25, 0.08), i_t, radius=0.015, seg=1)


def _spars(mb: kc.MeshBuilder, lug: Lug, *, lod: bool) -> None:
    i_t = mb.material(bf.M_TIMBER)
    a, b = yard_line(lug)
    t = np.linspace(0.0, 1.0, 3 if lod else 7)
    yard = a[None, :] + (b - a)[None, :] * t[:, None]
    r = 0.06 + 0.05 * np.sin(np.pi * np.clip(t * 0.9 + 0.05, 0, 1))
    kc.tube(mb, yard, r, 5 if lod else 8, i_t, weather=bf.RAIL_W, cap_start=True, cap_end=True)
    T = sail_point(lug, *lug.tack)
    C = sail_point(lug, *lug.clew)
    d = kc.normalize(C - T)
    boom = np.array([T - d * 0.2, C + d * 0.25])
    kc.tube(mb, boom, [0.075, 0.06], 5 if lod else 8, i_t, weather=bf.RAIL_W, cap_start=True, cap_end=True)
    # The boom's jaws round the mast.
    if not lod:
        jaw = np.array([0.0, lug.tack[1], lug.mast_z])
        kc.tube(mb, np.array([jaw, T - d * 0.2]), 0.05, 6, i_t)


def _sail(mb: kc.MeshBuilder, lug: Lug, rng, noise, *, lod: bool) -> None:
    """The sail in vertical cloths (each its own tone), the reef band in sea-blue, and three patches."""
    nv = 6 if lod else 20
    panels = 2 if lod else PANELS
    bands = ((0.0, REEF_BAND[0], bf.M_CANVAS), (REEF_BAND[0], REEF_BAND[1], bf.M_CANVAS_BLUE), (REEF_BAND[1], 1.0, bf.M_CANVAS))
    for k in range(panels):
        u0, u1 = k / panels, (k + 1) / panels
        var = float(rng.uniform(0.25, 0.75))
        for v0, v1, mat in bands:
            rows = max(2, int(round(nv * (v1 - v0))) + 1)
            cols = 2 if lod else 4
            U, V = np.meshgrid(np.linspace(u0, u1, cols), np.linspace(v0, v1, rows))
            g = sail_surface(lug, U, V)
            bf.cloth(mb, g, mat, uv=np.stack([U * 6.0, V * 10.0], -1), noise=None if lod else noise, variation=var,
                     thick=0.01)
    if lod:
        return
    # Patches: small squares of the same cloth, a shade paler, standing just proud on both faces.
    for _ in range(3):
        cu = float(rng.uniform(0.25, 0.8))
        cv = float(rng.uniform(0.3, 0.8))
        du, dv = float(rng.uniform(0.05, 0.08)), float(rng.uniform(0.04, 0.07))
        U, V = np.meshgrid(np.linspace(cu - du, cu + du, 3), np.linspace(cv - dv, cv + dv, 3))
        g = sail_surface(lug, U, V)
        for off in (0.016, -0.026):  # the lee face, then the windward face
            bf.cloth(mb, g + lee_normal(lug) * off, bf.M_CANVAS, uv=np.stack([U * 6.0, V * 10.0], -1), variation=0.92,
                     thick=0.004)


def _shrouds(mb: kc.MeshBuilder, lug: Lug, *, lod: bool, ratlines: bool) -> None:
    yh = lug.mast_h * HOUNDS_FRAC
    top = np.array([0.0, yh, lug.mast_z])
    for side in (-1.0, 1.0):
        feet = bf.chain_points(F, lug.mast_z, side)
        tops = []
        for p in feet:
            a = top + np.array([side * lug.mast_r * 0.8, 0.0, 0.0])
            tops.append(a)
            bf.rope(mb, p + np.array([0.0, 0.08, 0.0]), a, 0.02 if not lod else 0.035, bf.M_ROPE, segs=1, sides=3 if lod else 5)
        if not ratlines or lod:
            continue
        # Ratlines between the three shrouds, every 0.38 m up to the perch.
        y = 0.4 + float(feet[0][1])
        while y < min(PERCH_Y - 0.3, yh - 0.6):
            pts = []
            for p, a in zip(feet, tops):
                f = (y - p[1]) / (a[1] - p[1])
                pts.append(p + (a - p) * f)
            for p0, p1 in zip(pts[:-1], pts[1:]):
                bf.rope(mb, p0, p1, 0.009, bf.M_ROPE, sag=0.02, segs=2, sides=3)
            y += 0.38


def _stays(mb: kc.MeshBuilder, *, lod: bool) -> None:
    sz = F.stem_z
    head_y = float(F.sheer_y(sz + 0.1))
    sprit_tip = np.array([bf.BOWSPRIT_X, head_y + 0.93, sz - 3.4])
    fore_head = np.array([0.0, FORE.mast_h - 0.3, FORE.mast_z])
    main_head = np.array([0.0, MAIN.mast_h - 0.3, MAIN.mast_z])
    r = 0.025 if not lod else 0.04
    bf.rope(mb, sprit_tip, fore_head, r, bf.M_ROPE, segs=1, sides=3 if lod else 5)
    bf.rope(mb, fore_head, main_head, r * 0.8, bf.M_ROPE, sag=0.15, segs=1 if lod else 6, sides=3 if lod else 4)
    if lod:
        return
    # The bobstay under the bowsprit to the stem.
    bf.rope(mb, sprit_tip, np.array([0.0, F.wale_y + 0.2, sz + 0.05]), 0.02, bf.M_ROPE, segs=1, sides=4)


def _running(mb: kc.MeshBuilder, lug: Lug) -> None:
    """The halyard from the masthead to the yard's sling and down to the fife rail, and the sheet from the boom's
    end to the rail on the lee quarter."""
    a, b = yard_line(lug)
    sling = a + (b - a) * 0.3
    head = np.array([0.0, lug.mast_h - 0.35, lug.mast_z])
    bf.lathe(mb, head + np.array([0.0, -0.15, -0.16]), [(0.0, 0.0), (0.07, 0.03), (0.07, 0.25), (0.0, 0.3)], 6, bf.M_TIMBER)
    bf.rope(mb, head + np.array([0.0, 0.0, -0.18]), sling, 0.016, bf.M_ROPE, segs=1, sides=4)
    bf.rope(mb, head + np.array([0.0, -0.2, 0.18]), np.array([0.3, 0.98, lug.mast_z + FIFE_DZ[lug.mast_z]]), 0.014, bf.M_ROPE, segs=1,
            sides=4)
    C = sail_point(lug, *lug.clew)
    T = sail_point(lug, *lug.tack)
    end = C + kc.normalize(C - T) * 0.15
    z_rail = min(end[2] + 0.6, F.transom_z - 0.5)
    rail = np.array([-(float(F.half_beam_at(z_rail)) + 0.05), float(F.sheer_y(z_rail)) + 0.05, z_rail])
    bf.rope(mb, end, rail, 0.016, bf.M_ROPE, sag=0.05, segs=4, sides=4)
    # The tack's downhaul to the deck by the mast.
    bf.rope(mb, T, np.array([lee_normal(lug)[0] * 0.3, 0.05, lug.mast_z - 0.4]), 0.014, bf.M_ROPE, segs=1, sides=4)


def _perch(mb: kc.MeshBuilder, *, lod: bool) -> None:
    """The lookout's perch: a round top on two crosstrees with a hoop rail on four stanchions."""
    z = MAIN.mast_z
    y = PERCH_Y
    i_t = mb.material(bf.M_TIMBER)
    bf.lathe(mb, (0.0, y - 0.07, z), [(PERCH_R, 0.0), (PERCH_R, 0.07), (0.0, 0.07)], 8 if lod else 16, bf.M_TIMBER)
    bf.lathe(mb, (0.0, y - 0.07, z), [(0.0, 0.0), (PERCH_R, 0.0)], 8 if lod else 16, bf.M_TIMBER)
    for ang in (0.0, math.pi * 0.5):
        d = np.array([math.cos(ang), 0.0, math.sin(ang)]) * (PERCH_R + 0.1)
        kc.rounded_block(mb, (0.0, y - 0.13, z), (abs(d[0]) + 0.05, 0.05, abs(d[2]) + 0.05), i_t, radius=0.015, seg=1)
    if lod:
        return
    ang = np.linspace(0.0, 2.0 * math.pi, 17)
    hoop = np.stack([np.cos(ang) * PERCH_R, np.full_like(ang, y + 0.85), z + np.sin(ang) * PERCH_R], -1)
    kc.tube(mb, hoop, 0.025, 5, i_t, weather=bf.RAIL_W)
    for a in (math.pi * 0.25, math.pi * 0.75, math.pi * 1.25, math.pi * 1.75):
        p = np.array([math.cos(a) * PERCH_R, 0.0, z + math.sin(a) * PERCH_R])
        kc.tube(mb, np.array([p + [0.0, y, 0.0], p + [0.0, y + 0.86, 0.0]]), 0.022, 5, i_t)


def build_ferry_rig(seed: int = 811) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("ferry_rig", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("ferry_rig" + (bf.LOD if lod else ""))
        for lug in (FORE, MAIN):
            _mast(mb, lug, noise, lod=lod)
            _spars(mb, lug, lod=lod)
            _sail(mb, lug, rng, noise, lod=lod)
            _shrouds(mb, lug, lod=lod, ratlines=lug is MAIN)
            if not lod:
                _running(mb, lug)
        _stays(mb, lod=lod)
        _perch(mb, lod=lod)
        out.append(mb)
    return out


TARGETS = {"ferry_rig": build_ferry_rig}
