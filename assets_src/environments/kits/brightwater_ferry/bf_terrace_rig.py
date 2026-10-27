"""The *Seventh Terrace*'s rig and its three sail states (M3-ENV-08B; brightwater_ferry.md §7.2). Pure numpy.

The Pemakar **terrace sail**: a battened lug on each mast, seven cloths between the boom, six battens and the yard,
so a set sail reads in stepped bands and a lowered one stacks into terraces on its boom. Tanned cloth.

  terrace_rig            both masts (tapered, caps, partners, cheeks), three shrouds a side to the hull's chain-plates
                         (ratlines on the main), the forestay to the bowsprit, the bobstay and the spring stay: the
                         standing rigging every state shares.
  terrace_sails_set      under sail (Ch1 O13; Ch4 F05, C4-11 to C4-13): the yards hoisted, each sail wind-filled to
                         port (the wind on the starboard quarter), every cloth bellied between its battens; a cloth
                         of the main torn at the leech (its flap hanging), a hole in a cloth of the fore; halyards,
                         sheets, the tack downhauls.
  terrace_sails_furled   moored and crewed (Ch1): the yards lowered onto the booms, the booms amidships, the battens
                         stacked tidy with the cloth in short folds, gaskets round each stack, the lazy-jacks taut.
  terrace_sails_lowered  after the Spar-Wraith (C4-14): nothing holds the lines, so the yards have fallen onto the
                         booms askew, the battens fanned, the cloth in loose deep folds and one great bight of the main
                         over the port rail; the booms swung off to port on slack sheets, the halyards hanging.
  terrace_membrane       Ch4 only, with the set sails: the Spar-Wraith's spawn membrane webbing the main's shrouds
                         (both sides) and the fore's port shrouds, ragged at its edges, and a fringe of membrane
                         hanging from the main yard; its seams in `spawn_wound` (faint; the motes are VFX's).

All in the hull's frame (bf_terrace.terrace_hull), so every state drops onto the same origin.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

import bf_common as bf
import bf_terrace as bt
from bf_common import kc

TRI_BUDGET = {"terrace_rig": (14000, 1400), "terrace_sails_set": (24000, 2400), "terrace_sails_furled": (12000, 1200),
              "terrace_sails_lowered": (14000, 1400), "terrace_membrane": (8000, 800)}
F = bt.FORM
M_CANVAS = "bf_canvas_tan"
M_MEMBRANE = "bf_membrane"
M_WOUND = "bf_spawn_wound"
CLOTHS = 7  # the terrace sail: seven cloths between boom, battens and yard
HOUNDS_FRAC = 0.86
STACK_DY = 0.085  # a stowed sail's spars, one above the next
MEMBRANE_W = kc.Weathering(moss=0.0, salt=0.1, wet=0.9, erosion=0.2)


@dataclass(frozen=True)
class TerraceLug:
    """One battened lug in its mast's plane: (along, height) of tack, clew, throat and peak, `along` aft along the
    boom's line, swung `sheet_deg` off the centre line to port."""

    mast_z: float
    mast_h: float
    mast_r: float
    tack: tuple
    clew: tuple
    throat: tuple
    peak: tuple
    sheet_deg: float
    belly: float


FORE = TerraceLug(bt.FOREMAST_Z, bt.FOREMAST_H, 0.13, (-0.9, 2.45), (3.9, 2.6), (-1.25, 9.4), (3.7, 10.3), 34.0, 0.07)
MAIN = TerraceLug(bt.MAINMAST_Z, bt.MAINMAST_H, 0.15, (-1.1, 2.6), (4.9, 2.8), (-1.55, 12.3), (4.6, 13.2), 30.0, 0.065)
LUGS = (FORE, MAIN)
# The torn cloths (lug, cloth index from the foot): the main's leech torn off a flap, a hole in the fore.
MAIN_TEAR = (4, 0.8)  # cloth, the u where the leech flap tears away
FORE_HOLE = (2, (0.42, 0.58), (0.28, 0.74))  # cloth, u range, height range within the cloth


def aft_dir(lug: TerraceLug, sheet_deg: float | None = None) -> np.ndarray:
    a = math.radians(lug.sheet_deg if sheet_deg is None else sheet_deg)
    return np.array([-math.sin(a), 0.0, math.cos(a)])


def lee_normal(lug: TerraceLug, sheet_deg: float | None = None) -> np.ndarray:
    n = np.cross(aft_dir(lug, sheet_deg), kc.UP)
    return n if n[0] < 0.0 else -n


def sail_point(lug: TerraceLug, along: float, height: float, sheet_deg: float | None = None) -> np.ndarray:
    base = np.array([0.0, 0.0, lug.mast_z])
    return (base + aft_dir(lug, sheet_deg) * along + np.array([0.0, height, 0.0])
            + lee_normal(lug, sheet_deg) * (lug.mast_r + 0.05))


def sail_surface(lug: TerraceLug, u, v) -> np.ndarray:
    """The set sail at (u along the foot, v up the luff): bilinear between the boom and the yard; each cloth bellies
    to lee between its battens (the scallops), on top of the whole sail's gentle camber."""
    T, C, H, P = (sail_point(lug, *c) for c in (lug.tack, lug.clew, lug.throat, lug.peak))
    u = np.asarray(u, float)[..., None]
    v = np.asarray(v, float)[..., None]
    p = (1.0 - v) * ((1.0 - u) * T + u * C) + v * ((1.0 - u) * H + u * P)
    foot = float(np.linalg.norm(C - T))
    frac = np.clip(v * CLOTHS - np.floor(np.clip(v, 0.0, 0.9999) * CLOTHS), 0.0, 1.0)
    shape = 0.5 * np.sin(np.pi * np.clip(v, 0.0, 1.0)) ** 0.6 + 0.5 * np.sin(np.pi * frac) * (1.0 - 0.3 * v)
    camber = lug.belly * foot * np.clip(np.sin(np.pi * u), 0.0, None) ** 0.85 * shape
    return p + lee_normal(lug) * camber


def yard_line(lug: TerraceLug) -> tuple[np.ndarray, np.ndarray]:
    H = sail_point(lug, *lug.throat)
    P = sail_point(lug, *lug.peak)
    d = kc.normalize(P - H)
    return H - d * 0.3, P + d * 0.25


def batten_length(lug: TerraceLug, k: int) -> tuple[float, float]:
    """(along of the luff end, length) of spar k (0 the boom, CLOTHS the yard) in the sail's plane."""
    v = k / CLOTHS
    la = (1.0 - v) * lug.tack[0] + v * lug.throat[0]
    lh = (1.0 - v) * lug.tack[1] + v * lug.throat[1]
    ra = (1.0 - v) * lug.clew[0] + v * lug.peak[0]
    rh = (1.0 - v) * lug.clew[1] + v * lug.peak[1]
    return la, math.hypot(ra - la, rh - lh)


# ---------------------------------------------------------------------------------------------
# Standing rigging
# ---------------------------------------------------------------------------------------------
def _mast(mb: kc.MeshBuilder, lug: TerraceLug, noise, *, lod: bool) -> None:
    i_t = mb.material(bf.M_TIMBER)
    z = lug.mast_z
    h = np.linspace(-0.4, lug.mast_h, 3 if lod else 8)
    r = lug.mast_r * (1.0 - 0.35 * np.clip(h / lug.mast_h, 0, 1) ** 1.3)
    kc.tube(mb, np.stack([np.zeros_like(h), h, np.full_like(h, z)], -1), r, 6 if lod else 12, i_t, weather=bf.RAIL_W,
            noise=None if lod else noise, disp_m=0.004, cap_end=True)
    bf.lathe(mb, (0.0, lug.mast_h - 0.02, z), [(0.0, 0.0), (0.12, 0.02), (0.12, 0.12), (0.0, 0.16)], 6 if lod else 10,
             bt.M_COPPER_BRIGHT)
    if lod:
        return
    bf.lathe(mb, (0.0, 0.0, z), [(lug.mast_r + 0.14, 0.0), (lug.mast_r + 0.1, 0.12), (lug.mast_r + 0.01, 0.2)], 12,
             bt.M_LACQUER, weather=bt.LACQUER_W)
    yh = lug.mast_h * HOUNDS_FRAC
    for s in (-1.0, 1.0):
        kc.rounded_block(mb, (s * lug.mast_r * 0.75, yh, z), (0.05, 0.25, 0.08), i_t, radius=0.015, seg=1)
    # The halyard's sheave block at the masthead (the halyard itself belongs to the sail states).
    bf.lathe(mb, (0.0, lug.mast_h - 0.6, z - 0.17), [(0.0, 0.0), (0.07, 0.03), (0.07, 0.25), (0.0, 0.3)], 6, bf.M_TIMBER)


def _shrouds(mb: kc.MeshBuilder, lug: TerraceLug, *, lod: bool, ratlines: bool) -> None:
    yh = lug.mast_h * HOUNDS_FRAC
    top = np.array([0.0, yh, lug.mast_z])
    for side in (-1.0, 1.0):
        feet = bf.chain_points(F, lug.mast_z, side)
        tops = []
        for p in feet:
            a = top + np.array([side * lug.mast_r * 0.8, 0.0, 0.0])
            tops.append(a)
            bf.rope(mb, p + np.array([0.0, 0.08, 0.0]), a, 0.02 if not lod else 0.035, bf.M_ROPE, segs=1,
                    sides=3 if lod else 5)
        if not ratlines or lod:
            continue
        y = 0.4 + float(feet[0][1])
        while y < yh - 1.2:
            pts = []
            for p, a in zip(feet, tops):
                f = (y - p[1]) / (a[1] - p[1])
                pts.append(p + (a - p) * f)
            for p0, p1 in zip(pts[:-1], pts[1:]):
                bf.rope(mb, p0, p1, 0.009, bf.M_ROPE, sag=0.02, segs=2, sides=3)
            y += 0.4


def shroud_line(lug: TerraceLug, side: float, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Foot (at the deadeye) and top (at the hounds) of shroud k on one side."""
    p = bf.chain_points(F, lug.mast_z, side)[k] + np.array([0.0, 0.08, 0.0])
    a = np.array([side * lug.mast_r * 0.8, lug.mast_h * HOUNDS_FRAC, lug.mast_z])
    return p, a


def sprit_tip() -> np.ndarray:
    sz = F.stem_z
    head_y = float(F.sheer_y(sz + 0.1))
    return np.array([bt.BOWSPRIT_X, head_y + 0.84, sz - 3.0])


def _stays(mb: kc.MeshBuilder, *, lod: bool) -> None:
    tip = sprit_tip()
    fore_head = np.array([0.0, FORE.mast_h - 0.3, FORE.mast_z])
    main_head = np.array([0.0, MAIN.mast_h - 0.3, MAIN.mast_z])
    r = 0.025 if not lod else 0.04
    bf.rope(mb, tip, fore_head, r, bf.M_ROPE, segs=1, sides=3 if lod else 5)
    bf.rope(mb, fore_head, main_head, r * 0.8, bf.M_ROPE, sag=0.15, segs=1 if lod else 6, sides=3 if lod else 4)
    if not lod:
        bf.rope(mb, tip, np.array([0.0, bt.RED_WALE_Y + 0.2, F.stem_z + 0.05]), 0.02, bf.M_ROPE, segs=1, sides=4)


def build_rig(seed: int = 9201) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("terrace_rig", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("terrace_rig" + (bf.LOD if lod else ""))
        for lug in LUGS:
            _mast(mb, lug, noise, lod=lod)
            _shrouds(mb, lug, lod=lod, ratlines=lug is MAIN)
        _stays(mb, lod=lod)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Under sail
# ---------------------------------------------------------------------------------------------
def _cloth_grid(lug: TerraceLug, u0: float, u1: float, v0: float, v1: float, nu: int, nv: int) -> tuple:
    U, V = np.meshgrid(np.linspace(u0, u1, nu), np.linspace(v0, v1, nv))
    return sail_surface(lug, U, V), np.stack([U * 6.0, V * 10.0], -1)


def _set_sail(mb: kc.MeshBuilder, lug: TerraceLug, rng, noise, *, lod: bool) -> None:
    nu = 3 if lod else 9
    nv = 2 if lod else 5
    for k in range(CLOTHS):
        v0, v1 = k / CLOTHS, (k + 1) / CLOTHS
        var = float(rng.uniform(0.3, 0.7))
        pieces = [(0.0, 1.0, v0, v1)]
        if not lod and lug is MAIN and k == MAIN_TEAR[0]:
            pieces = [(0.0, MAIN_TEAR[1], v0, v1)]
        if not lod and lug is FORE and k == FORE_HOLE[0]:
            (ua, ub), (fa, fb) = FORE_HOLE[1], FORE_HOLE[2]
            va, vb = v0 + fa * (v1 - v0), v0 + fb * (v1 - v0)
            pieces = [(0.0, ua, v0, v1), (ub, 1.0, v0, v1), (ua, ub, v0, va), (ua, ub, vb, v1)]
        for u0, u1, a, b in pieces:
            cols = max(2, int(round(nu * (u1 - u0))) + 1)
            g, uv = _cloth_grid(lug, u0, u1, a, b, cols, nv)
            bf.cloth(mb, g, M_CANVAS, uv=uv, noise=None if lod else noise, variation=var, thick=0.01)
    if lod:
        return
    # The main's torn leech: the flap hangs from the cloth's foot batten, curling down and to lee.
    if lug is MAIN:
        k, ut = MAIN_TEAR
        v0, v1 = k / CLOTHS, (k + 1) / CLOTHS
        U, W = np.meshgrid(np.linspace(ut, 1.0, 4), np.linspace(0.0, 1.0, 5))
        base = sail_surface(lug, U, np.full_like(U, v0))
        h = (v1 - v0) * (lug.peak[1] - lug.clew[1]) * 0.9
        droop = W[..., None] * h
        g = base + kc.UP * droop * 0.25 + lee_normal(lug) * droop * (0.55 + 0.3 * (U[..., None] - ut) / (1.0 - ut))
        g = g + aft_dir(lug) * droop * 0.35 * np.sin(W[..., None] * 2.0)
        bf.cloth(mb, g, M_CANVAS, uv=np.stack([U * 6.0, W], -1), variation=0.55, thick=0.008)
    # Battens (on the windward face) and the cloths' bolt-rope at the leech.
    i_t = mb.material(bf.M_TIMBER)
    for k in range(1, CLOTHS):
        v = k / CLOTHS
        u = np.linspace(-0.02, 1.03, 8)
        line = sail_surface(lug, u, np.full_like(u, v)) - lee_normal(lug) * 0.03
        kc.tube(mb, line, 0.022, 5, i_t, weather=bf.RAIL_W, cap_start=True, cap_end=True)


def _spars(mb: kc.MeshBuilder, lug: TerraceLug, *, lod: bool) -> None:
    i_t = mb.material(bf.M_TIMBER)
    a, b = yard_line(lug)
    t = np.linspace(0.0, 1.0, 3 if lod else 7)
    kc.tube(mb, a[None, :] + (b - a)[None, :] * t[:, None], 0.06 + 0.045 * np.sin(np.pi * np.clip(t * 0.9 + 0.05, 0, 1)),
            5 if lod else 8, i_t, weather=bf.RAIL_W, cap_start=True, cap_end=True)
    T = sail_point(lug, *lug.tack)
    C = sail_point(lug, *lug.clew)
    d = kc.normalize(C - T)
    kc.tube(mb, np.array([T - d * 0.2, C + d * 0.25]), [0.075, 0.06], 5 if lod else 8, i_t, weather=bf.RAIL_W,
            cap_start=True, cap_end=True)
    if not lod:
        kc.tube(mb, np.array([[0.0, lug.tack[1], lug.mast_z], T - d * 0.2]), 0.05, 6, i_t)


def _running_set(mb: kc.MeshBuilder, lug: TerraceLug) -> None:
    a, b = yard_line(lug)
    sling = a + (b - a) * 0.32
    head = np.array([0.0, lug.mast_h - 0.6, lug.mast_z - 0.17])
    bf.rope(mb, head, sling, 0.016, bf.M_ROPE, segs=1, sides=4)
    bf.rope(mb, head + np.array([0.0, -0.2, 0.34]), np.array([0.3, 0.95, lug.mast_z + (0.7 if lug is FORE else -0.7)]),
            0.014, bf.M_ROPE, segs=1, sides=4)
    C = sail_point(lug, *lug.clew)
    T = sail_point(lug, *lug.tack)
    end = C + kc.normalize(C - T) * 0.15
    z_rail = min(end[2] + 0.8, F.transom_z - 0.6)
    rail = np.array([-(float(F.half_beam_at(z_rail)) + 0.05), float(F.rail_y(z_rail)) + 0.05, z_rail])
    bf.rope(mb, end, rail, 0.016, bf.M_ROPE, sag=0.05, segs=4, sides=4)
    # The batten sheets (a crow's foot from each upper batten's end to the main sheet) on the main.
    for k in (2, 4, 6):
        p = sail_surface(lug, np.array(1.0), np.array(k / CLOTHS)).reshape(3)
        bf.rope(mb, p, end + (p - end) * 0.25, 0.008, bf.M_ROPE, segs=1, sides=3)
    bf.rope(mb, T, np.array([lee_normal(lug)[0] * 0.3, 0.05, lug.mast_z - 0.4]), 0.014, bf.M_ROPE, segs=1, sides=4)


def build_sails_set(seed: int = 9211) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("terrace_sails_set", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("terrace_sails_set" + (bf.LOD if lod else ""))
        for lug in LUGS:
            _spars(mb, lug, lod=lod)
            _set_sail(mb, lug, rng, noise, lod=lod)
            if not lod:
                _running_set(mb, lug)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Stowed: furled (tidy, Ch1) and lowered (fallen, C4-14)
# ---------------------------------------------------------------------------------------------
def stowed_spars(lug: TerraceLug, *, messy: bool, rng, sheet_deg: float) -> list[tuple[np.ndarray, np.ndarray]]:
    """(luff end, leech end) of the boom, the six battens and the yard, stacked on the boom. Tidy: each spar keeps
    its luff at the mast and lies along the boom. Messy: the spars fan and tilt, the yard's peak fallen lowest."""
    ad = aft_dir(lug, sheet_deg)
    lee = lee_normal(lug, sheet_deg)
    base = np.array([0.0, lug.tack[1], lug.mast_z]) + lee * (lug.mast_r + 0.05)
    out = []
    for k in range(CLOTHS + 1):
        la, ln = batten_length(lug, k)
        y = k * STACK_DY
        d = ad.copy()
        drop = 0.0
        if messy and k > 0:
            yaw = math.radians(float(rng.uniform(-9.0, 9.0)) + (6.0 if k == CLOTHS else 0.0))
            d = kc.rot_y(yaw) @ d
            drop = float(rng.uniform(-0.15, 0.25)) + (0.9 if k == CLOTHS else 0.0)
            y += float(rng.uniform(0.0, 0.08)) * k
        a = base + ad * la + np.array([0.0, y, 0.0])
        b = a + d * ln * math.cos(math.asin(min(drop / ln, 0.5))) - np.array([0.0, drop, 0.0])
        out.append((a, b))
    return out


def _stowed(mb: kc.MeshBuilder, lug: TerraceLug, rng, *, lod: bool, messy: bool) -> None:
    sheet = 22.0 if messy else 0.0
    spars = stowed_spars(lug, messy=messy, rng=rng, sheet_deg=sheet)
    lee = lee_normal(lug, sheet)
    i_t = mb.material(bf.M_TIMBER)
    for k, (a, b) in enumerate(spars):
        r = 0.075 if k == 0 else (0.085 if k == CLOTHS else 0.022)
        d = kc.normalize(b - a)
        kc.tube(mb, np.array([a - d * (0.2 if k in (0, CLOTHS) else 0.02), b + d * 0.2]), r, 4 if lod else 7, i_t,
                weather=bf.RAIL_W, cap_start=True, cap_end=True)
    # The cloth between each pair of spars: a fold hanging to alternate sides (short and tidy, or deep and loose;
    # the main's top cloths spill as one great bight over the port rail when it is lowered).
    nu = 3 if lod else 9
    nw = 3 if lod else 6
    for k in range(CLOTHS):
        (a0, b0), (a1, b1) = spars[k], spars[k + 1]
        side = 1.0 if k % 2 == 0 else -1.0
        depth = 0.24 if not messy else float(rng.uniform(0.35, 0.8))
        reach = 0.5 * depth
        if messy and lug is MAIN and k >= CLOTHS - 3:
            # The great bight: out over the port rail and down the topsides.
            depth, reach, side = 2.0 + 0.3 * (k - (CLOTHS - 3)), 3.6 + 0.3 * (k - (CLOTHS - 3)), 1.0
        U, W = np.meshgrid(np.linspace(0.0, 1.0, nu), np.linspace(0.0, 1.0, nw))
        e0 = a0[None, None, :] + (b0 - a0)[None, None, :] * U[..., None]
        e1 = a1[None, None, :] + (b1 - a1)[None, None, :] * U[..., None]
        bell = np.sin(np.pi * W)[..., None] * (0.6 + 0.4 * np.sin(np.pi * U)[..., None])
        g = e0 * (1.0 - W[..., None]) + e1 * W[..., None] + lee * side * reach * bell - kc.UP * depth * bell
        bf.cloth(mb, g, M_CANVAS, uv=np.stack([U * 6.0, W], -1), variation=float(rng.uniform(0.3, 0.7)), thick=0.008)
    if lod:
        return
    a, b = spars[0]
    top_a, top_b = spars[-1]
    if not messy:
        # Gaskets round the stack every metre or so, and the lazy-jacks from the mast down to both sides of it.
        n = max(2, int(np.linalg.norm(b - a) / 1.1))
        for t in np.linspace(0.15, 0.9, n):
            c0 = a + (b - a) * t
            c1 = top_a + (top_b - top_a) * t
            mid = 0.5 * (c0 + c1)
            hh = 0.5 * float(np.linalg.norm(c1 - c0)) + 0.2  # round the folds hanging under the boom too
            ang = np.linspace(0.0, 2.0 * math.pi, 11)
            ring = mid[None, :] - kc.UP * 0.1 + np.outer(np.cos(ang), lee * 0.3) + np.outer(np.sin(ang), kc.UP * hh)
            kc.tube(mb, ring, 0.012, 3, mb.material(bf.M_ROPE))
        top = np.array([0.0, lug.tack[1] + 4.0, lug.mast_z])
        for t in (0.3, 0.65):
            c = a + (b - a) * t + kc.UP * 0.3
            for s in (-1.0, 1.0):
                bf.rope(mb, top, c + lee * s * 0.24, 0.01, bf.M_ROPE, segs=1, sides=3)
        # The halyard taut to the yard's sling; the boom's sheet hauled in to the taffrail.
        head = np.array([0.0, lug.mast_h - 0.6, lug.mast_z - 0.17])
        bf.rope(mb, head, top_a + (top_b - top_a) * 0.3, 0.016, bf.M_ROPE, segs=1, sides=4)
        z_rail = min(b[2] + 0.6, F.transom_z - 0.4)
        bf.rope(mb, b, np.array([0.0, float(F.deck_y(z_rail)) + 0.9, z_rail]), 0.016, bf.M_ROPE, segs=1, sides=4)
    else:
        # The halyard run slack down the mast in a heap at its foot; the sheet slack to the lee rail.
        head = np.array([0.0, lug.mast_h - 0.6, lug.mast_z - 0.17])
        pts = np.array([head, head + np.array([0.08, -4.0, -0.05]), top_a + (top_b - top_a) * 0.3 + np.array([0.0, 0.3, 0.0])])
        kc.tube(mb, pts, 0.016, 4, mb.material(bf.M_ROPE), weather=bf.CLOTH_W)
        bt._coil(mb, (0.45, 0.0, lug.mast_z + 0.45), 0.25, 3, lod=False, spill=0.6)
        z_rail = min(b[2] + 0.8, F.transom_z - 0.6)
        rail = np.array([-(float(F.half_beam_at(z_rail)) + 0.05), float(F.rail_y(z_rail)) + 0.05, z_rail])
        bf.rope(mb, b, rail, 0.016, bf.M_ROPE, sag=0.6, segs=6, sides=4)


def build_sails_furled(seed: int = 9221) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("terrace_sails_furled", seed)
        mb = kc.MeshBuilder("terrace_sails_furled" + (bf.LOD if lod else ""))
        for lug in LUGS:
            _stowed(mb, lug, rng, lod=lod, messy=False)
        out.append(mb)
    return out


def build_sails_lowered(seed: int = 9231) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("terrace_sails_lowered", seed)
        mb = kc.MeshBuilder("terrace_sails_lowered" + (bf.LOD if lod else ""))
        for lug in LUGS:
            _stowed(mb, lug, rng, lod=lod, messy=True)
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# The spawn membrane (Ch4, with the set sails)
# ---------------------------------------------------------------------------------------------
def _web(mb: kc.MeshBuilder, lug: TerraceLug, side: float, k: int, f0: float, f1: float, rng, noise, *,
         lod: bool, k1: int | None = None) -> None:
    """Membrane between shrouds k and k1 (default k + 1) on one side, from f0 to f1 of the way up them, its top and bottom edges
    ragged, bowed outboard a little; a seam or two of spawn_wound across it."""
    p0, a0 = shroud_line(lug, side, k)
    p1, a1 = shroud_line(lug, side, k + 1 if k1 is None else k1)
    nu = 3 if lod else 6
    nv = 3 if lod else 9
    U, V = np.meshgrid(np.linspace(0.0, 1.0, nu), np.linspace(0.0, 1.0, nv))
    rag0 = np.array([float(rng.uniform(-0.06, 0.06)) for _ in range(nu)])
    rag1 = np.array([float(rng.uniform(-0.08, 0.05)) for _ in range(nu)])
    lo = f0 + rag0[None, :] * (1.0 - np.abs(2.0 * U - 1.0))
    hi = f1 + rag1[None, :] * (1.0 - np.abs(2.0 * U - 1.0))
    f = lo + (hi - lo) * V
    s0 = p0[None, None, :] + (a0 - p0)[None, None, :] * f[..., None]
    s1 = p1[None, None, :] + (a1 - p1)[None, None, :] * f[..., None]
    g = s0 * (1.0 - U[..., None]) + s1 * U[..., None]
    g = g + np.array([side, 0.0, 0.0]) * (0.18 * np.sin(np.pi * U) * np.sin(np.pi * V))[..., None]
    if not lod:
        g = g + (noise.fbm(g / 0.6, 2) - 0.5)[..., None] * 0.08 * np.sin(np.pi * U)[..., None]
    bf.cloth(mb, g, M_MEMBRANE, uv=np.stack([U, V], -1), weather=MEMBRANE_W, variation=float(rng.random()), thick=0.006)
    if lod:
        return
    # Seams: one or two lines across the web, standing just proud on both faces.
    for vv in (0.35, 0.7)[: 1 + int(rng.random() < 0.6)]:
        row = int(round(vv * (nv - 1)))
        line = g[row]
        nrm = np.array([side, 0.0, 0.0])
        for off in (0.012, -0.018):
            kc.tube(mb, line + nrm * off, 0.009, 3, mb.material(M_WOUND), weather=MEMBRANE_W)


def build_membrane(seed: int = 9241) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("terrace_membrane", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("terrace_membrane" + (bf.LOD if lod else ""))
        for side in (-1.0, 1.0):
            _web(mb, MAIN, side, 0, 0.18, 0.72, rng, noise, lod=lod, k1=2)
        _web(mb, FORE, -1.0, 0, 0.3, 0.72, rng, noise, lod=lod, k1=2)
        _web(mb, FORE, 1.0, 1, 0.42, 0.66, rng, noise, lod=lod)
        # A fringe of membrane hanging in tatters from the main yard.
        a, b = yard_line(MAIN)
        for t in np.linspace(0.12, 0.88, 4 if lod else 7):
            top = a + (b - a) * float(t)
            ln = float(rng.uniform(0.6, 1.5))
            w = float(rng.uniform(0.18, 0.32))
            along = kc.normalize(b - a)
            U, V = np.meshgrid(np.linspace(-0.5, 0.5, 3), np.linspace(0.0, 1.0, 3 if lod else 6))
            g = (top[None, None, :] + along[None, None, :] * (U * w * (1.0 - 0.6 * V))[..., None]
                 - kc.UP * (V * ln)[..., None] + lee_normal(MAIN) * (0.25 * V ** 2 * ln)[..., None])
            bf.cloth(mb, g - kc.UP * 0.08, M_MEMBRANE, uv=np.stack([U, V], -1), weather=MEMBRANE_W,
                     variation=float(rng.random()), thick=0.006)
        out.append(mb)
    return out


TARGETS = {"terrace_rig": build_rig, "terrace_sails_set": build_sails_set, "terrace_sails_furled": build_sails_furled,
           "terrace_sails_lowered": build_sails_lowered, "terrace_membrane": build_membrane}
