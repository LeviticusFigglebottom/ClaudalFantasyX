"""Oil slug, Ch1 Oruvel Underway (M3-CRE-02): docs/kb/art/creatures/act1/oil_slug.md.

blender --background --factory-startup --python assets_src/creatures/oil_slug/build_oil_slug.py -- \
    --out assets/creatures/oil_slug/oil_slug.glb

A sea slug that feeds on lamp oil leaking from drowned lamps: a long low body with a double row of flame-shaped
frills whose tips glow the warm oil-lamp colour it ate, two curled horns, and a spawn_wound gill rosette near the tail.

M3-CRE-654 (final quality, ADR 0041): the body is one loft on a flat sole with a blunt head, under a smooth mantle
shield (an overhanging rim and a breathing pore) and over a ruffled foot fringe; the horns are a slug's tentacles,
two upper ones on the horn bones with eyes on their tips and two short oral ones under the head; the cerata are
flattened flames, dark at the root and lit at the tip; the weak point is a small closed gill rosette; the skin is
slick, with an oil film's sheen in its colour.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402
import grounding as gr  # noqa: E402

SEED = 3307
PAL = {k: ck.hexrgb(v) for k, v in {
    "sand_wet": "#B59D74", "tortoiseshell": "#6B3A1E", "oil_lamp": "#FFB16E", "ember_orange": "#E0702E",
    "spawn_wound": "#3FE0C8", "dusk_gold": "#F2A64A", "lacquer_black": "#1D1916", "bone": "#E6DAC0",
    "sea_glow": "#1C6B78", "sand_dry": "#EFDDB4",
}.items()}

N = 6
LENGTH = 1.1
# The body loft (M3-CRE-654): stations along the spine, the head running HEAD_EXT past the last joint and the tail
# TAIL_EXT past the first; the sole is flat at SOLE_Y. Profiles are keyed on u (0 the tail joint, 1 the head joint):
# the half-width and the back's height over the floor. A section is widest low (MID of the way up), so the body is an
# arched dome that rounds down to the floor at the head and the tail, not a tube on the spine.
STATIONS = 44
ANGLES = 22
TUBERCLES = 150  # raised skin tubercles over the body, in a net of grooves
HEAD_EXT, TAIL_EXT = 0.08, 0.07
SOLE_Y = 0.015
U_KEYS = [0.0, 0.12, 0.3, 0.5, 0.7, 0.85, 0.93, 1.0]
HALF_W = [0.028, 0.068, 0.1, 0.115, 0.115, 0.105, 0.088, 0.075]
HEIGHT = [0.06, 0.13, 0.205, 0.25, 0.262, 0.235, 0.19, 0.16]
MID = 0.36
MANTLE_Z = (0.17, 0.47)  # the mantle shield's rear and front
FRINGE = 0.04  # how far the foot's fringe reaches past the body (m)
CERATA = 7  # per row (four rows)
ROSETTE_Z = -0.33


def spine_points(n: int) -> np.ndarray:
    z = np.linspace(-LENGTH / 2, LENGTH / 2, n)
    y = 0.13 + 0.02 * np.sin(np.linspace(0, math.pi, n))
    x = 0.04 * np.sin(np.linspace(0, 2 * math.pi, n))
    return np.column_stack([x, y, z])


def build_rig() -> tuple[ck.Rig, np.ndarray]:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.1, 0))
    j = spine_points(N + 1)
    for i in range(N):
        rig.add(f"spine{i}", j[i], j[i + 1], "root" if i == 0 else f"spine{i - 1}")
    head = j[-1]
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        rig.add(f"horn_{tag}", head + np.array([s * 0.06, 0.08, -0.02]), head + np.array([s * 0.1, 0.24, 0.05]),
                f"spine{N - 1}")
    return rig, j


def _centre(n: int) -> tuple[np.ndarray, np.ndarray]:
    """The loft's centre line (the spine, extended straight past both ends) and u at each station."""
    path = spine_points(n)
    back = (path[0] - path[1]) / np.linalg.norm(path[0] - path[1])
    fwd = (path[-1] - path[-2]) / np.linalg.norm(path[-1] - path[-2])
    q = np.cos(np.linspace(0.0, 0.5 * math.pi, 6)[:-1])  # 1 at a tip; rows dense at the rounding
    tail = path[0] + np.outer(q * TAIL_EXT, back)
    head = path[-1] + np.outer(q[::-1] * HEAD_EXT, fwd)
    u = np.concatenate([-q * TAIL_EXT / LENGTH, np.linspace(0.0, 1.0, n), 1.0 + q[::-1] * HEAD_EXT / LENGTH])
    return np.vstack([tail, path, head]), u


def _profile(u: float) -> tuple[float, float, float]:
    """(half-width, the back's height over the floor, round-off) at u: the ends round off as quarter-ellipses."""
    uc = min(max(u, 0.0), 1.0)
    w, t = np.interp(uc, U_KEYS, HALF_W), np.interp(uc, U_KEYS, HEIGHT) - SOLE_Y
    if u < 0.0:
        cap = max(1.0 - (u * LENGTH / TAIL_EXT) ** 2, 0.0) ** 0.5
    elif u > 1.0:
        cap = max(1.0 - ((u - 1.0) * LENGTH / HEAD_EXT) ** 2, 0.0) ** 0.42
    else:
        cap = 1.0
    return w * cap, SOLE_Y + t * cap, cap


def body(mesh: ck.Mesh, rig: ck.Rig, j: np.ndarray) -> None:
    centre, u = _centre(STATIONS)
    ang = np.linspace(0.0, 2 * math.pi, ANGLES, endpoint=False)
    sa, ca = np.sin(ang), np.cos(ang)
    rows = []
    for k in range(len(centre)):
        w, h, _ = _profile(u[k])
        mid = SOLE_Y + MID * (h - SOLE_Y)
        x = w * np.sign(sa) * np.abs(sa) * (1.0 + 0.1 * np.clip(-ca, 0.0, 1.0) ** 2)  # the foot flares a little
        y = mid + np.where(ca > 0, (h - mid) * np.abs(ca) ** 0.65, -(mid - SOLE_Y) * np.abs(ca) ** 0.4)
        rows.append(np.column_stack([centre[k][0] + x, y, np.full(len(ang), centre[k][2])]))
    P = np.vstack(rows)
    T = ck.grid_tris(len(centre), len(ang), True)
    mids = np.repeat(np.column_stack([centre[:, 0], P.reshape(len(centre), len(ang), 3)[:, :, 1].mean(axis=1),
                                      centre[:, 2]]), len(ang), axis=0)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    if float((fn * (P[T[:, 0]] - mids[T[:, 0]])).sum()) < 0:
        T = ck.flip(T)
    U = np.repeat(u, len(ang))
    CA = np.tile(ca, len(centre))
    nrm = ck.vertex_normals(P, T)
    # the skin: tubercles (the nearest of TUBERCLES seeds round the body) swell between grooves
    rng = np.random.default_rng(SEED + 9)
    seeds = P[rng.choice(len(P), TUBERCLES, replace=False)]
    dd = np.linalg.norm(P[:, None, :] - seeds[None], axis=2)
    dd.sort(axis=1)
    net = 1.0 - ck.smoothstep(0.0, 0.012, dd[:, 1] - dd[:, 0])  # 1 in a groove
    upper = ck.smoothstep(-0.35, 0.1, CA)
    P = P + nrm * ((0.003 * (1 - net) - 0.002 * net) * upper + 0.003 * ck.fbm(P * 16.0, SEED + 2))[:, None]
    top = ck.smoothstep(-0.1, 0.6, CA)
    mottle = ck.fbm(P * 14.0, SEED)
    col = ck.mix(PAL["tortoiseshell"], PAL["sand_wet"], (0.25 + 0.45 * top + 0.25 * mottle)[:, None])
    col = ck.mix(col, PAL["lacquer_black"], (0.35 * ck.smoothstep(0.2, 0.45, ck.value_noise(P * 30.0, SEED + 4))
                                              * top)[:, None])  # dark freckles
    flank = np.exp(-((CA + 0.05) / 0.16) ** 2) * ck.smoothstep(-0.02, 0.15, U) * ck.smoothstep(1.08, 0.95, U)
    col = ck.mix(col, PAL["tortoiseshell"] * 0.6, (0.4 * flank)[:, None])  # a dark band along each flank
    foot = 1.0 - ck.smoothstep(-0.75, -0.4, CA)
    col = ck.mix(col, PAL["sand_dry"] * 0.82, (0.6 * foot)[:, None])  # the pale foot below it
    col = ck.mix(col, PAL["tortoiseshell"] * 0.6, (0.2 * net * upper)[:, None])
    col = _sheen(P, col, top)
    mouth = (np.exp(-((CA + 0.55) / 0.15) ** 2) * ck.smoothstep(1.0 + 0.4 * HEAD_EXT / LENGTH, 1.0 + 0.9 * HEAD_EXT
                                                                 / LENGTH, U))
    col = ck.mix(col, PAL["lacquer_black"], (0.8 * mouth)[:, None])
    skin = rig.chain([f"spine{i}" for i in range(N)], j)
    ck.finish(mesh, P, T, "body", col, skin, wet=1.0,
              cavity=np.clip(0.2 * (1 - top) + 0.5 * net * upper + 0.8 * mouth, 0, 1))
    mantle(mesh, skin)
    fringe(mesh, skin)
    rosette(mesh, skin)


def _sheen(P: np.ndarray, col: np.ndarray, amount: np.ndarray) -> np.ndarray:
    """An oil film's sheen: thin, swirling bands of a sea colour and gold over the wet skin."""
    swirl = P[:, 2] * 9.0 + 3.0 * ck.fbm(P * 5.0, SEED + 8) + P[:, 0] * 4.0
    band = 0.5 + 0.5 * np.sin(swirl * 2.0)
    col = ck.mix(col, PAL["sea_glow"] * 1.3, (0.4 * ck.smoothstep(0.7, 1.0, band) * amount)[:, None])
    return ck.mix(col, PAL["dusk_gold"] * 0.85, (0.32 * ck.smoothstep(0.7, 1.0, 1 - band) * amount)[:, None])


def _surface_y(z: float) -> tuple[float, float]:
    """The body's top and its spine x at z (rest pose)."""
    path = spine_points(200)
    k = int(np.argmin(np.abs(path[:, 2] - z)))
    u = (path[k, 2] + LENGTH / 2) / LENGTH
    return _profile(u)[1], path[k, 0]


def _skin_y(dx: float, z: float) -> float:
    """The body's upper surface at dx from the spine line, at z (rest pose)."""
    path = spine_points(200)
    k = int(np.argmin(np.abs(path[:, 2] - z)))
    w, h, _ = _profile((path[k, 2] + LENGTH / 2) / LENGTH)
    mid = SOLE_Y + MID * (h - SOLE_Y)
    ca = math.sqrt(max(1.0 - min(abs(dx) / w, 1.0) ** 2, 0.0))
    return mid + (h - mid) * ca ** 0.65


def mantle(mesh: ck.Mesh, skin) -> None:
    """The mantle: a smooth, raised shield over the shoulders, its rim overhanging the body, a breathing pore on its
    right side."""
    z0, z1 = MANTLE_Z
    rows_, segs = 7, 18
    a = np.linspace(0.0, 2 * math.pi, segs, endpoint=False)
    pts = []
    for i in range(rows_ + 1):
        r = i / rows_  # 0 at the crown, 1 at the rim's underside
        rr = min(r / 0.85, 1.0)
        for ak in a:
            tuck = 0.94 if r > 0.85 else 1.0  # the rim's underside tucks back to the skin
            z = 0.5 * (z0 + z1) + 0.5 * (z1 - z0) * math.cos(ak) * math.sin(rr * math.pi / 2) * tuck
            _, xs = _surface_y(z)
            w = np.interp((z + LENGTH / 2) / LENGTH, U_KEYS, HALF_W) * 0.86
            dx = w * math.sin(ak) * math.sin(rr * math.pi / 2) * tuck
            y = _skin_y(dx, z) + (0.016 * math.cos(rr * math.pi / 2) + 0.007 if r <= 0.85 else -0.004)
            pts.append((xs + dx, y, z))
    P = np.array(pts)
    P[:, 1] += 0.003 * ck.fbm(P * 22.0, SEED + 6)  # fine lumps, so it is skin, not a mirror
    T = ck.grid_tris(rows_ + 1, segs, True)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    if float(fn[:, 1].sum()) < 0:
        T = ck.flip(T)
    R = np.repeat(np.arange(rows_ + 1) / rows_, segs)
    col = ck.mix(PAL["tortoiseshell"] * 0.9, PAL["sand_wet"], (0.15 + 0.25 * ck.fbm(P * 9.0, SEED + 5))[:, None])
    col = ck.mix(col, PAL["tortoiseshell"] * 0.5, (0.7 * ck.smoothstep(0.55, 0.85, R))[:, None])  # the rim's lip
    col = _sheen(P, col, np.full(len(P), 0.9))
    pz, (py, px) = 0.5 * (z0 + z1) + 0.04, _surface_y(0.5 * (z0 + z1) + 0.04)
    pore = np.exp(-(((P[:, 0] - (px - 0.1)) / 0.02) ** 2 + ((P[:, 2] - pz) / 0.02) ** 2))
    col = ck.mix(col, PAL["lacquer_black"], pore[:, None])
    ck.finish(mesh, P, T, "body", col, skin, wet=0.65, cavity=np.clip(0.5 * ck.smoothstep(0.6, 0.9, R) + pore, 0, 1))
    del py


def fringe(mesh: ck.Mesh, skin) -> None:
    """The foot's fringe: a thin, ruffled skirt round the sole, pale with a dark edge."""
    centre, u = _centre(STATIONS)
    inner, outer = [], []
    side_pts = []
    for sgn in (1.0, -1.0):
        ks = range(len(centre)) if sgn > 0 else range(len(centre) - 1, -1, -1)
        for k in ks:
            w, _, _ = _profile(u[k])
            side_pts.append((centre[k][0] + sgn * w, centre[k][2], sgn, k))
    for x, z, sgn, k in side_pts:
        # outward in the sole's plane: sideways along the flanks, round the ends
        w, _, cap = _profile(u[k])
        ox = sgn * cap
        oz = (1.0 - cap) * (1.0 if u[k] > 0.5 else -1.0)
        ln = math.hypot(ox, oz) or 1.0
        ox, oz = ox / ln, oz / ln
        inner.append((x - ox * 0.02, SOLE_Y + 0.012, z - oz * 0.02))
        ruffle = 0.006 * math.sin(z * 75.0 + (0.0 if sgn > 0 else 1.3))
        outer.append((x + ox * FRINGE, SOLE_Y + 0.006 + ruffle + 0.006, z + oz * FRINGE))
    P = np.vstack([np.array(inner), np.array(outer)])
    n = len(inner)
    T = ck.grid_tris(2, n, True)
    edge = np.concatenate([np.zeros(n), np.ones(n)])
    col = ck.mix(PAL["sand_dry"] * 0.82, PAL["sand_wet"], (0.3 * edge)[:, None])
    col = ck.mix(col, PAL["tortoiseshell"], (0.8 * ck.smoothstep(0.9, 1.0, edge))[:, None])
    for top, off in ((True, 0.002), (False, -0.002)):
        Q = P + np.array([0.0, off, 0.0])
        TT = T
        fn = np.cross(Q[T[:, 1]] - Q[T[:, 0]], Q[T[:, 2]] - Q[T[:, 0]])
        if float(fn[:, 1].sum()) * (1.0 if top else -1.0) < 0:
            TT = ck.flip(T)
        ck.finish(mesh, Q, TT, "body", col, skin, wet=1.0, cavity=0.2 * (1 - edge))


def rosette(mesh: ck.Mesh, skin) -> None:
    """The weak point: a small, closed gill rosette on the back near the tail, its plumes folded in."""
    ytop, xs = _surface_y(ROSETTE_Z)
    c = np.array([xs, ytop - 0.004, ROSETTE_Z])
    for k in range(6):
        a = k * math.pi / 3
        d = np.array([math.sin(a), 0.0, math.cos(a)])
        Pp, Tp = ck.ellipsoid((0.0, 0.0, 0.0), (0.012, 0.014, 0.026), 3, 5)
        Pp = ck.transform(Pp, ck.rot_y(math.degrees(a)) @ ck.rot_x(-35.0), c + d * 0.02 + np.array([0, 0.01, 0]))
        glow = ck.smoothstep(0.0, 0.03, Pp[:, 1] - c[1])
        col = ck.mix(PAL["tortoiseshell"], PAL["spawn_wound"] * 0.6, glow[:, None])
        ck.finish(mesh, Pp, Tp, "body", col, skin, wet=1.0, emission=glow)


def frills(mesh: ck.Mesh, rig: ck.Rig, j: np.ndarray) -> None:
    """The cerata: flattened flames in four rows down the back behind the mantle, dark and wet at the root, the eaten
    lamp-oil glowing at the tip, each leaning out and curling back."""
    rng = np.random.default_rng(SEED + 1)
    path = spine_points(60)
    skin = rig.chain([f"spine{i}" for i in range(N)], j)
    for row, (side, lean) in enumerate(((1.0, 0.9), (-1.0, 0.9), (1.0, 0.35), (-1.0, 0.35))):
        for k in range(CERATA):
            u = 0.06 + 0.58 * (k + 0.5 * (row // 2)) / CERATA
            c = path[int(u * 59)]
            h = (0.08 + 0.1 * math.sin((u + 0.15) * math.pi)) * rng.uniform(0.6, 1.25) * (1.1 if row >= 2 else 0.85)
            off = side * (0.075 if row < 2 else 0.035)
            base = np.array([c[0] + off, _skin_y(off, c[2]) - 0.01, c[2]])
            tip = base + np.array([side * h * lean, h, rng.uniform(-0.03, 0.01) - 0.03])
            m1 = base + (tip - base) * 0.35 + np.array([side * 0.015, 0.0, 0.02])
            m2 = base + (tip - base) * 0.7 + np.array([-side * 0.01, 0.0, -0.025])
            sp = ck.bezier([base, m1, m2, tip], 6)
            Pc, Tc = ck.tube(sp, np.array([0.03, 0.036, 0.032, 0.024, 0.013, 0.004]), 6, squash=0.5,
                             up_hint=(0.0, 0.0, 1.0))
            along = np.concatenate([np.repeat(np.linspace(0, 1, 6), 6), [0.0, 1.0]])[: len(Pc)]
            glow = ck.smoothstep(0.62, 1.0, along)
            root = ck.mix(PAL["lacquer_black"], PAL["tortoiseshell"], 0.6)
            col = ck.mix(root, PAL["ember_orange"] * 0.9, ck.smoothstep(0.2, 0.8, along)[:, None])
            col = ck.mix(col, PAL["oil_lamp"], glow[:, None])
            ck.finish(mesh, Pc, Tc, "frill", col, skin, wet=0.9 - 0.4 * along, emission=glow)


def horns(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The tentacles: two tall upper ones on the horn bones, ringed, with dark eyes on their tips; two short, flat
    oral ones under the head, reaching forward and out."""
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        b = rig.bones[rig.index(f"horn_{tag}")]
        h0, h1 = np.asarray(b.head), np.asarray(b.tail)
        rx, rz = h0[0] - s * 0.012, h0[2] - 0.015
        root = np.array([rx, _skin_y(rx - spine_points(N + 1)[-1][0], rz) - 0.012, rz])  # rooted in the head
        sp = ck.bezier([root, h0 + (h1 - h0) * 0.5 + np.array([s * 0.01, 0, 0.03]), h1], 10)
        P, T = ck.tube(sp, np.linspace(0.024, 0.011, 10), 7, cap_end=False)
        d = np.concatenate([np.repeat(np.linspace(0, 1, 10), 7), [0.0]])
        ring = 0.5 + 0.5 * np.cos(d * math.pi * 14)
        col = ck.mix(PAL["ember_orange"] * 0.85, PAL["tortoiseshell"], (0.45 * ring * (1 - d))[:, None])
        bone = rig.rigid(f"horn_{tag}")
        ck.finish(mesh, P, T, "body", col, bone, wet=1.0, cavity=0.35 * ring * (1 - d))
        tdir = (h1 - sp[-2]) / np.linalg.norm(h1 - sp[-2])
        Pb, Tb = ck.ellipsoid(h1 + tdir * 0.006, (0.016, 0.016, 0.016), 5, 8)
        dd = (Pb - h1) @ tdir / 0.016
        col_b = ck.mix(PAL["ember_orange"] * 0.85, PAL["lacquer_black"], ck.smoothstep(0.1, 0.5, dd)[:, None])
        ck.finish(mesh, Pb, Tb, "body", col_b, bone, wet=1.0)
    head_bone = rig.rigid(f"spine{N - 1}")
    tip = spine_points(N + 1)[-1]
    for s in (1.0, -1.0):
        base = tip + np.array([s * 0.045, -0.06, 0.035])
        sp = ck.bezier([base, base + np.array([s * 0.05, -0.02, 0.05]), base + np.array([s * 0.095, -0.04, 0.075])], 6)
        P, T = ck.tube(sp, np.linspace(0.019, 0.01, 6), 6, squash=0.6)
        P[:, 1] = np.maximum(P[:, 1], SOLE_Y + 0.004)
        ck.finish(mesh, P, T, "body", ck.mix(PAL["ember_orange"] * 0.8, PAL["sand_wet"], 0.4), head_bone, wet=1.0,
                  cavity=0.15)


def build_clips() -> list[ck.Clip]:
    sp = [f"spine{i}" for i in range(N)]
    idle = ck.Clip("idle", 3.2, loop=True)
    for i, b in enumerate(sp):
        idle.wave(b, amp_rot=(1.5, 3.0, 0.0), cycles=1, phase=-i * 0.6)
    idle.wave("horn_l", amp_rot=(8.0, 0.0, 6.0), cycles=2)
    idle.wave("horn_r", amp_rot=(8.0, 0.0, -6.0), cycles=2, phase=0.8)

    attack = ck.Clip("attack", 1.1)
    for t, rear, lunge in ((0.0, 0, 0), (0.35, -1, -0.05), (0.55, 0.6, 0.2), (0.75, 0.3, 0.15), (1.1, 0, 0)):
        for i in range(N // 2, N):
            attack.key(sp[i], t, (14.0 * rear, 0, 0))
        attack.key("root", t, (0, 0, 0), (0, 0, lunge))
        attack.key("horn_l", t, (-25.0 * max(rear, 0) + 20 * max(-rear, 0), 0, 0))
        attack.key("horn_r", t, (-25.0 * max(rear, 0) + 20 * max(-rear, 0), 0, 0))

    cast = ck.Clip("cast", 1.5)
    for t, s in ((0.0, 0.0), (0.6, 1.0), (1.0, 1.0), (1.5, 0.0)):
        for i, b in enumerate(sp):
            cast.key(b, t, (-4.0 * s * (1 if i < N // 2 else -1), 0, 0), (0, 0.03 * s, 0))
        cast.key("horn_l", t, (-20.0 * s, 0, 20.0 * s))
        cast.key("horn_r", t, (-20.0 * s, 0, -20.0 * s))

    hit = ck.Clip("hit", 0.45)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.45, 0.0)):
        # M3-CRE-632: the recoil's offset is the body's, on the chain's first bone (keyed on every bone, it added up
        # along the chain and drove the head 9 cm into the floor)
        for i, b in enumerate(sp):
            hit.key(b, t, (0, 6.0 * s * (1 if i % 2 else -1), 0), (0, -0.01 * s, -0.03 * s) if i == 0 else (0, 0, 0))
        hit.key("horn_l", t, (40.0 * s, 0, 0))
        hit.key("horn_r", t, (40.0 * s, 0, 0))

    ko = ck.Clip("ko", 1.6)
    for t, s in ((0.0, 0.0), (0.8, 0.7), (1.6, 1.0)):
        for i, b in enumerate(sp):
            ko.key(b, t, (0.0, 0, 3.0 * s * (1 if i % 2 else -1)), (0, -0.01 * s, 0))
        ko.key("horn_l", t, (60.0 * s, 0, 10.0 * s))
        ko.key("horn_r", t, (60.0 * s, 0, -10.0 * s))
    return [idle, attack, cast, hit, ko]


# Kept off the floor (M3-CRE-632, common/grounding.py): as the front half strikes down, it bends up at its middle
# the least it takes for the head to strike the floor, not go through it. M3-CRE-654: the body now lies on a flat sole
# its whole length, so what the chain's ripple (the idle's glide, the KO's settle) still presses under the floor is
# taken up by lifting the whole slug the least it takes (millimetres).
GROUNDED_LIMBS = [("spine3", 0, -1.0, 30.0), ("root", gr.LIFT, 1.0, 0.05)]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    return gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig, j = build_rig()
    mesh = ck.Mesh("oil_slug")
    body(mesh, rig, j)
    frills(mesh, rig, j)
    horns(mesh, rig)
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extras={"hymn_creature": "oil_slug"})
    print(f"oil_slug: {info}")


if __name__ == "__main__":
    main()
