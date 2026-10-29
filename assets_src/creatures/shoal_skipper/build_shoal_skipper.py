"""Shoal skipper, Ch6 Brine Shoals (M3-CRE-05): docs/kb/art/creatures/act1/shoal_skipper.md.

blender --background --factory-startup --python assets_src/creatures/shoal_skipper/build_shoal_skipper.py -- \
    --out assets/creatures/shoal_skipper/shoal_skipper.glb

A mudskipper grown to a dog's size on the Brine Shoals' flats: a bulbous head with eyes on top, propped on its front
fins, a tall spined dorsal fin edged deep red, mottled skin crusted with dried salt, a spawn_wound gill.

M3-CRE-654 (final quality, ADR 0041): the body is one loft with a blunt, wide, boxy head whose lower jaw is split from
the upper lip by a dark mouth line (the jaw bone opens it), goggle eyes set in raised sockets on the head top with
lower lids and a gold iris, an operculum crease with the weak point a small closed gill mark behind it, mottled and
speckled wet skin with dry salt crust on the back, fan pectorals with rays planted on the floor, a scalloped dorsal
sail with spines past its membrane, a low second dorsal and a rounded tail fin.
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

SEED = 6101
PAL = {k: ck.hexrgb(v) for k, v in {
    "sand_wet": "#B59D74", "foliage_shadow": "#1E4A3A", "mortar_white": "#E6E1D6", "lacquer_red_deep": "#7A1712",
    "spawn_wound": "#3FE0C8", "lacquer_black": "#1D1916", "tortoiseshell": "#6B3A1E", "sand_dry": "#EFDDB4",
    "dusk_gold": "#F2A64A", "timber_weathered": "#7E6A55",
}.items()}

N = 5
FIN_TIP_Y = 0.016  # the pectoral fin's tip height: its underside on the floor
KO_FIN = 120.0  # the KO: the right fin, the side it lands on, tucks in under its belly (degrees)

# The body loft (M3-CRE-654): stations along the spine from the head (u 0) to the tail (u 1), and a snout that runs
# SNOUT metres ahead of the first joint, rounding to a blunt face whose tip sits SNOUT_DROP under the spine line.
STATIONS = 40
SNOUT_ROWS = 8
SNOUT = 0.09
SNOUT_DROP = 0.035
ANGLES = 24  # around each section, plus four rows at the mouth line
U_KEYS = [0.0, 0.1, 0.2, 0.3, 0.45, 0.6, 0.75, 0.88, 1.0]
HALF_W = [0.15, 0.17, 0.165, 0.145, 0.12, 0.09, 0.06, 0.035, 0.008]  # half-width (m)
TOP = [0.118, 0.13, 0.12, 0.112, 0.1, 0.085, 0.066, 0.045, 0.012]  # spine line to the back (m)
BELLY = [0.1, 0.112, 0.112, 0.105, 0.092, 0.075, 0.056, 0.038, 0.01]  # spine line to the belly (m)
BOX = [2.7, 2.7, 2.5, 2.3, 2.15, 2.05, 2.0, 2.0, 2.0]  # superellipse power: a boxy head, a round tail
MOUTH_A = 2.05  # the mouth line's angle round the section (0 is the back, pi the belly)
MOUTH_END = 0.06  # the mouth corner (u): the jaw hinge
GILL_U = 0.2  # the operculum's crease; the weak point's closed gill mark sits just behind it


def spine(n: int) -> np.ndarray:
    return ck.bezier([(0, 0.3, 0.42), (0, 0.32, 0.15), (0, 0.22, -0.2), (0, 0.08, -0.5)], n)


def build_rig() -> tuple[ck.Rig, np.ndarray]:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.1, 0))
    j = spine(N + 1)
    for i in range(N):
        rig.add(f"spine{i}", j[i], j[i + 1], "root" if i == 0 else f"spine{i - 1}")
    rig.add("jaw", j[0] + np.array([0, -0.08, -0.05]), j[0] + np.array([0, -0.1, 0.12]), "spine0")
    rig.add("dorsal", j[1] + np.array([0, 0.12, 0]), j[3] + np.array([0, 0.2, 0]), "spine1")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        # the fin tip rests on the floor (M3-CRE-632: its tube's underside went 1.6 cm under at y 0.0)
        rig.add(f"fin_{tag}", j[1] + np.array([s * 0.12, -0.1, 0.05]), np.array([s * 0.28, FIN_TIP_Y, 0.3]), "spine1")
        rig.add(f"eye_{tag}", j[0] + np.array([s * 0.07, 0.12, -0.08]), j[0] + np.array([s * 0.08, 0.2, -0.06]),
                "spine0")
    return rig, j


def _angles() -> np.ndarray:
    a = list(np.linspace(0.0, 2.0 * math.pi, ANGLES, endpoint=False))
    for m in (MOUTH_A, 2.0 * math.pi - MOUTH_A):
        a += [m - 0.07, m + 0.07]
    return np.array(sorted(a))


def _section_frames() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """The loft's centre line (the snout ahead of the spine, then the spine), the u of each station (negative on the
    snout), and the frames along it."""
    path = spine(STATIONS)
    fwd = path[0] - path[1]
    fwd /= np.linalg.norm(fwd)
    q = np.cos(np.linspace(0.0, 0.5 * math.pi, SNOUT_ROWS + 1)[:-1])  # 1 at the tip; rows dense at the rounding
    snout = path[0] + np.outer(q * SNOUT, fwd)
    centre = np.vstack([snout, path])
    u = np.concatenate([-q * SNOUT, np.linspace(0.0, 1.0, STATIONS)])
    tan, nrm, bin_ = ck.frames_along(centre)
    return centre, u, nrm, bin_


def body_loft() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """The body: (P, T, u per vertex, angle per vertex)."""
    centre, u, nrm, bin_ = _section_frames()
    ang = _angles()
    sa, ca = np.sin(ang), np.cos(ang)
    rows = []
    for k in range(len(centre)):
        uk = max(u[k], 0.0)
        w, t, b, p = (np.interp(uk, U_KEYS, v) for v in (HALF_W, TOP, BELLY, BOX))
        dy = 0.0
        if u[k] < 0.0:  # the blunt face: a quarter-ellipse round to the tip, which drops to the mouth's height
            cap = max(1.0 - (u[k] / SNOUT) ** 2, 0.0) ** 0.38  # blunt: a superellipse, not a cone
            w, t, b = w * cap, t * cap, b * cap
            dy = -SNOUT_DROP * (1.0 - cap)
        e = 2.0 / p
        x = w * np.sign(sa) * np.abs(sa) ** e
        y = np.where(ca > 0, t, b) * np.sign(ca) * np.abs(ca) ** e + dy
        rows.append(centre[k] + np.outer(y, nrm[k]) + np.outer(x, bin_[k]))
    P = np.vstack(rows)
    T = ck.grid_tris(len(centre), len(ang), True)
    U = np.repeat(u, len(ang))
    A = np.tile(ang, len(centre))
    # outward winding: the sum of face normals against the vectors from the centre line
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    radial = P[T[:, 0]] - np.repeat(centre, len(ang), axis=0)[T[:, 0]]
    if float((fn * radial).sum()) < 0:
        T = ck.flip(T)
    return P, T, U, A


def _eye_centre(rig: ck.Rig, tag: str) -> np.ndarray:
    e = rig.bones[rig.index(f"eye_{tag}")]
    return np.asarray(e.head) + 0.45 * (np.asarray(e.tail) - np.asarray(e.head))


def body(mesh: ck.Mesh, rig: ck.Rig, j: np.ndarray) -> None:
    P, T, U, A = body_loft()
    side = np.minimum(np.abs(A - MOUTH_A), np.abs(A - (2 * math.pi - MOUTH_A)))
    lower = (A > MOUTH_A - 1e-6) & (A < 2 * math.pi - MOUTH_A + 1e-6)
    # sockets: the head top rises round each eye, so the eyes sit in raised cups, not on stalks
    for tag in ("l", "r"):
        c = _eye_centre(rig, tag)
        d2 = ((P[:, 0] - c[0]) ** 2 + (P[:, 2] - c[2]) ** 2) / 0.05 ** 2
        P[:, 1] += 0.03 * np.exp(-d2 * 0.8) * (P[:, 1] > 0.33)
    # cheeks swell over the operculum; the operculum's rear edge is a crease
    nrm = ck.vertex_normals(P, T)
    cheek = np.exp(-((U - 0.12) / 0.07) ** 2) * ck.smoothstep(0.4, 1.2, np.abs(np.sin(A)))
    crease = np.exp(-((U - GILL_U - 0.012 * np.cos(A * 2)) / 0.012) ** 2) * ck.smoothstep(0.5, 1.0, np.abs(np.sin(A)))
    lumps = ck.fbm(P * 18.0, SEED + 5)
    P = P + nrm * (0.012 * cheek - 0.007 * crease + 0.004 * lumps)[:, None]
    mouth = np.exp(-(side / 0.09) ** 2) * ck.smoothstep(MOUTH_END + 0.03, MOUTH_END - 0.01, U)
    lip = np.exp(-((side - 0.16) / 0.07) ** 2) * lower * ck.smoothstep(MOUTH_END + 0.02, MOUTH_END - 0.02, U)
    P = P + nrm * (0.006 * lip - 0.004 * mouth)[:, None]

    top = ck.smoothstep(-0.2, 0.7, np.cos(A))  # 1 on the back, 0 on the belly
    mott = ck.fbm(P * 9.0, SEED)
    spots = ck.smoothstep(0.1, 0.3, ck.value_noise(P * 21.0, SEED + 2))
    speck = ck.smoothstep(0.45, 0.6, ck.value_noise(P * 60.0, SEED + 3))
    col = ck.mix(PAL["sand_wet"], PAL["timber_weathered"], (0.5 * top)[:, None])
    col = ck.mix(col, PAL["foliage_shadow"], (ck.smoothstep(-0.05, 0.35, mott) * 0.55 * (0.4 + 0.6 * top))[:, None])
    col = ck.mix(col, PAL["lacquer_black"], (0.7 * spots * (0.3 + 0.7 * top))[:, None])  # dark blotches on the back and flanks
    col = ck.mix(col, PAL["sand_dry"], (0.8 * speck * (1 - spots))[:, None])  # pale speckles
    belly = 1.0 - ck.smoothstep(-0.65, -0.1, np.cos(A))
    col = ck.mix(col, PAL["sand_dry"] * 0.92, (0.75 * belly)[:, None])
    salt = ck.smoothstep(0.22, 0.42, ck.fbm(P * 6.0, SEED + 1)) * ck.smoothstep(0.3, 0.85, np.cos(A))
    salt *= ck.smoothstep(0.05, 0.25, U)
    col = ck.mix(col, PAL["mortar_white"], (0.75 * salt)[:, None])
    gill = (np.exp(-((U - GILL_U - 0.03) / 0.012) ** 2) * np.exp(-(np.cos(A) / 0.28) ** 2)
            * ck.smoothstep(0.55, 0.9, np.abs(np.sin(A))))
    gill = ck.smoothstep(0.25, 0.8, gill)
    col = ck.mix(col, PAL["lacquer_black"], (0.7 * mouth)[:, None])
    col = ck.mix(col, PAL["sand_dry"] * 0.8, (0.5 * lip)[:, None])
    col = ck.mix(col, PAL["tortoiseshell"], (0.5 * crease)[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.55, gill[:, None])
    wet = np.clip(0.75 - 0.6 * salt + 0.2 * belly, 0.0, 1.0)
    cavity = np.clip(0.9 * mouth + 0.6 * crease + 0.35 * salt + 0.15 * spots, 0.0, 1.0)

    chain = rig.chain([f"spine{i}" for i in range(N)], j)
    ij, i0 = rig.index("jaw"), rig.index("spine0")
    jaw_w = lower * ck.smoothstep(MOUTH_END + 0.02, MOUTH_END - 0.03, U) * ck.smoothstep(0.02, 0.08, side)

    def skin(Q):
        J, W = chain(Q)
        m = jaw_w > 1e-3
        J[m] = (ij, i0)
        W[m] = np.column_stack([jaw_w[m], 1.0 - jaw_w[m]])
        return J, W

    ck.finish(mesh, P, T, "skin", col, skin, wet=wet, cavity=cavity, emission=gill)
    # the mouth's inside: dark, seen when the jaw drops
    Pm, Tm = ck.ellipsoid(j[0] + np.array([0.0, -0.04, -0.02]), (0.1, 0.03, 0.07), 5, 10)
    ck.finish(mesh, Pm, Tm, "skin", PAL["lacquer_black"] * 1.1, i0, wet=1.0, cavity=1.0)


def eyes(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        c = _eye_centre(rig, tag)
        look = np.array([s * 0.75, 0.45, 0.5])
        look /= np.linalg.norm(look)
        Pe, Te = ck.ellipsoid(c, (0.042, 0.042, 0.042), 8, 12)
        d = (Pe - c) / 0.042
        facing = d @ look
        pupil = ck.smoothstep(0.86, 0.9, facing + 0.08 * np.abs(d[:, 1]))  # a level, slightly oval pupil
        iris = ck.smoothstep(0.45, 0.6, facing)
        col = ck.mix(PAL["lacquer_black"], PAL["dusk_gold"] * 0.75, (iris * (1 - pupil))[:, None])
        ck.finish(mesh, Pe, Te, "eye", col, rig.rigid(f"eye_{tag}"), wet=1.0)
        # the lid: a fold of skin round the eyeball, a little behind its widest, square to its look
        x = np.cross(np.array([0.0, 0.0, 1.0]), look)
        x /= np.linalg.norm(x)
        z = np.cross(x, look)
        a = np.linspace(0.0, 2.0 * math.pi, 17)
        ring = c - look * 0.01 + 0.041 * (np.outer(np.cos(a), x) + np.outer(np.sin(a), z))
        Pl, Tl = ck.tube(ring, 0.009, 5, cap_start=False, cap_end=False)
        lower = 0.5 - 0.5 * np.repeat(np.sin(a), 5)  # the lower lid paler
        colm = ck.mix(PAL["timber_weathered"], PAL["sand_wet"], (0.5 * lower)[:, None])
        ck.finish(mesh, Pl, Tl, "skin", colm, rig.rigid(f"eye_{tag}"), wet=0.7, cavity=0.2)


def _sheet(mesh: ck.Mesh, P: np.ndarray, T: np.ndarray, n: np.ndarray, col, bones, gap: float, **kw) -> None:
    """A two-sided membrane: the sheet offset by +-gap along `n` (per vertex or one vector), each face outward."""
    n = np.broadcast_to(np.asarray(n, dtype=np.float64), P.shape)
    ck.finish(mesh, P + n * gap, T, "fin", col, bones, **kw)
    ck.finish(mesh, P - n * gap, ck.flip(T), "fin", col, bones, **kw)


def fins(mesh: ck.Mesh, rig: ck.Rig, j: np.ndarray) -> None:
    # the dorsal sail: a scalloped membrane between spines that run past its edge, dark with pale spots, edged red
    base = spine(40)[9:31]
    nb = len(base)
    h = 0.29 * np.sin(np.linspace(0.25, math.pi - 0.35, nb)) ** 0.8
    every = 3
    scallop = 1.0 - 0.13 * np.sin(np.pi * (np.arange(nb) % every) / every) ** 2
    rows = 4
    P = []
    for r in range(rows):
        f = r / (rows - 1)
        P.append(base + np.column_stack([np.zeros(nb), 0.1 + (h * scallop + 0.02) * f, -0.04 * f * np.ones(nb)]))
    P = np.vstack(P)
    T = ck.grid_tris(rows, nb, False)
    up = np.repeat(np.linspace(0, 1, rows), nb)
    spots = ck.smoothstep(0.25, 0.4, ck.value_noise(P * np.array([1.0, 30.0, 30.0]), SEED + 9))
    col = ck.mix(PAL["tortoiseshell"] * 0.8, PAL["lacquer_black"], (0.4 * (1 - up))[:, None])
    col = ck.mix(col, PAL["sand_dry"] * 0.8, (0.6 * spots * (1 - up))[:, None])
    col = ck.mix(col, PAL["lacquer_red_deep"], ck.smoothstep(0.55, 0.9, up)[:, None])
    _sheet(mesh, P, T, (1.0, 0.0, 0.0), col, rig.rigid("dorsal"), 0.004, wet=0.4, cavity=0.15 * (1 - up))
    for k in range(0, nb, every):
        tip = base[k] + np.array([0.0, 0.1 + h[k] + 0.06, -0.06])
        Ps, Ts = ck.tube(ck.bezier([base[k] + np.array([0, 0.08, 0]), (base[k] + tip) / 2 + np.array([0, 0, 0.01]),
                                    tip], 5), np.array([0.009, 0.008, 0.006, 0.004, 0.0015]), 5)
        ck.finish(mesh, Ps, Ts, "fin", ck.mix(PAL["lacquer_red_deep"], PAL["sand_dry"], 0.15), rig.rigid("dorsal"),
                  wet=0.3)

    chain = rig.chain([f"spine{i}" for i in range(N)], j)
    # the second dorsal: a low ridge-fin along the back towards the tail
    sp = spine(40)
    seg = sp[25:36]
    ns = len(seg)
    t_at = np.interp(np.linspace(25 / 39, 35 / 39, ns), U_KEYS, TOP)
    h2 = 0.065 * np.sin(np.linspace(0.15, math.pi - 0.1, ns))
    P2 = np.vstack([seg + np.column_stack([np.zeros(ns), t_at - 0.01, np.zeros(ns)]),
                    seg + np.column_stack([np.zeros(ns), t_at + h2, -0.02 * np.ones(ns)])])
    T2 = ck.grid_tris(2, ns, False)
    up2 = np.repeat([0.0, 1.0], ns)
    col2 = ck.mix(PAL["tortoiseshell"] * 0.85, PAL["lacquer_red_deep"], (0.8 * up2)[:, None])
    _sheet(mesh, P2, T2, (1.0, 0.0, 0.0), col2, chain, 0.003, wet=0.4)
    # the tail fin: a rounded paddle round the tail's end
    end, tdir = sp[-1], sp[-1] - sp[-4]
    tdir[1] *= 0.4  # the fin runs nearly level off the down-turned tail
    tdir /= np.linalg.norm(tdir)
    upv = np.array([0.0, 1.0, 0.0]) - tdir * tdir[1]
    upv /= np.linalg.norm(upv)
    cols, rows_c = 9, 5
    pts = []
    for r in range(rows_c):
        v = -0.45 + 1.45 * r / (rows_c - 1)  # mostly above the tail's line, clear of the floor
        for c in range(cols):
            a = c / (cols - 1)
            reach = 0.15 * math.sqrt(max(1.0 - v * v * 0.6, 0.0))
            half = 0.02 + 0.075 * math.sin(min(a * 1.15, 1.0) * math.pi * 0.5)
            pts.append(end - tdir * 0.09 + tdir * (0.09 + reach) * a + upv * (half * v))
    P3 = np.array(pts)
    T3 = ck.grid_tris(rows_c, cols, False)
    a3 = np.tile(np.linspace(0, 1, cols), rows_c)
    rays = 0.5 + 0.5 * np.cos(np.repeat(np.linspace(-1, 1, rows_c), cols) * math.pi * 2)
    col3 = ck.mix(PAL["timber_weathered"], PAL["lacquer_black"], (0.4 * rays * a3)[:, None])
    col3 = ck.mix(col3, PAL["lacquer_red_deep"], ck.smoothstep(0.75, 1.0, a3)[:, None] * 0.7)
    _sheet(mesh, P3, T3, (1.0, 0.0, 0.0), col3, chain, 0.003, wet=0.5, cavity=0.25 * rays * a3)

    # pectoral fins: a muscular lobe, then a rayed fan planted on the floor (the "legs" it props on)
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        b = rig.bones[rig.index(f"fin_{tag}")]
        h0, h1 = np.asarray(b.head), np.asarray(b.tail)
        m = h0 + 0.42 * (h1 - h0)
        Pf, Tf = ck.tube(ck.bezier([h0 - np.array([s * 0.03, 0, 0]), (h0 + m) / 2 + np.array([0, 0.015, 0]), m], 6),
                         np.array([0.05, 0.048, 0.044, 0.038, 0.032, 0.028]), 9, squash=0.6)
        ck.finish(mesh, Pf, Tf, "skin", ck.mix(PAL["sand_wet"], PAL["timber_weathered"], 0.4), rig.rigid(f"fin_{tag}"),
                  wet=0.7, cavity=0.1)
        d = (h1 - m) / np.linalg.norm(h1 - m)
        e = np.array([0.0, 0.0, 1.0])
        e = e - d * (e @ d)
        e /= np.linalg.norm(e)
        nf = np.cross(d, e)
        R = np.linalg.norm(h1 - m)
        na, nr = 13, 5
        pts, along, rayv = [], [], []
        for ir in range(nr):
            rr = (ir + 1) / nr
            for ia in range(na):
                a = math.radians(-45.0 + 115.0 * ia / (na - 1))
                tipr = 1.0 - 0.07 * (1.0 - abs(math.cos(ia * math.pi / 2)))  # each ray reaches past the web
                corr = 0.006 * math.cos(ia * math.pi) * rr  # the fan's pleats
                pts.append(m + R * rr * (tipr if ir == nr - 1 else 1.0) * (math.cos(a) * d + math.sin(a) * e)
                           + nf * corr + np.array([0.0, 0.004, 0.0]))
                along.append(rr)
                rayv.append(0.5 + 0.5 * math.cos(ia * math.pi))
        P4 = np.vstack([np.tile(m, (na, 1)), np.array(pts)])
        T4 = ck.grid_tris(nr + 1, na, False)
        al = np.concatenate([np.zeros(na), along])
        rv = np.concatenate([np.zeros(na), rayv])
        col4 = ck.mix(PAL["sand_wet"] * 0.95, PAL["timber_weathered"], (0.5 * rv)[:, None])
        col4 = ck.mix(col4, PAL["sand_dry"] * 0.9, ck.smoothstep(0.75, 1.0, al)[:, None] * 0.6)
        _sheet(mesh, P4, T4, nf, col4, rig.rigid(f"fin_{tag}"), 0.0035, wet=0.6, cavity=0.3 * rv * al)


def build_clips() -> list[ck.Clip]:
    sp = [f"spine{i}" for i in range(N)]
    idle = ck.Clip("idle", 2.0, loop=True)
    # gulping: the jaw drops a little and closes (M3-CRE-654: a positive turn opens it, now that it is the head's
    # own lower jaw)
    idle.wave("jaw", amp_rot=(5.0, 0, 0), base_rot=(5.0, 0, 0), cycles=2)
    idle.wave("dorsal", amp_rot=(0, 0, 6.0), cycles=2)
    for i, b in enumerate(sp):
        idle.wave(b, amp_rot=(0, 4.0, 0), cycles=1, phase=-i * 0.7)
    attack = ck.Clip("attack", 1.0)  # a hop-lunge, the mouth gaping at the bite
    for t, h, fwd, curl in ((0.0, 0, 0, 0), (0.3, 0.0, -0.05, 1.0), (0.5, 0.3, 0.35, -0.5), (0.65, 0.05, 0.5, 0),
                            (1.0, 0, 0, 0)):
        attack.key("root", t, (-15.0 * curl, 0, 0), (0, h, fwd))
        for i, b in enumerate(sp[2:], 2):
            attack.key(b, t, (12.0 * curl, 0, 0))
        attack.key("jaw", t, (22.0 * max(-curl, 0) * 2, 0, 0))
    cast = ck.Clip("cast", 1.3)  # the display: dorsal raised high, fins spread, head up
    for t, s in ((0.0, 0.0), (0.4, 1.0), (0.9, 1.0), (1.3, 0.0)):
        cast.key("dorsal", t, (-20.0 * s, 0, 0), (0, 0.05 * s, 0))
        cast.key("spine0", t, (-15.0 * s, 0, 0))
        cast.key("jaw", t, (14.0 * s, 0, 0))
        cast.key("fin_l", t, (0, 0, 25.0 * s))
        cast.key("fin_r", t, (0, 0, -25.0 * s))
    hit = ck.Clip("hit", 0.5)  # it flips back
    for t, s in ((0.0, 0.0), (0.12, 1.0), (0.5, 0.0)):
        hit.key("root", t, (-20.0 * s, 0, 0), (0, 0.08 * s, -0.12 * s))
    ko = ck.Clip("ko", 1.4)  # it flops onto its side
    for t, s in ((0.0, 0.0), (0.4, 0.6), (0.9, 1.0), (1.4, 1.0)):
        ko.key("root", t, (0, 0, 80.0 * s), (-0.1 * s, -0.02 * s, 0))
        ko.key("dorsal", t, (0, 0, -20.0 * s))
        ko.key("jaw", t, (12.0 * s, 0, 0))  # slack
        ko.key("fin_r", t, (0, 0, -KO_FIN * s))  # M3-CRE-632: the fin it falls on tucks under the belly
    return [idle, attack, cast, hit, ko]


# Kept off the floor (M3-CRE-632, common/grounding.py): the tail rides up over the floor when the head lifts (the
# display, the flip back), and in the KO, which rolls it about a pivot on the floor, the body lifts the least it takes
# to lie on its side.
GROUNDED_LIMBS = [("spine2", 0, 1.0, 30.0, ("cast", "hit", "hit_b", "idle_b")), ("root", gr.LIFT, 1.0, 0.5)]


def export_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    return gr.grounded(rig, mesh, build_clips(), GROUNDED_LIMBS)


def build_mesh(rig: ck.Rig, j: np.ndarray) -> ck.Mesh:
    mesh = ck.Mesh("shoal_skipper")
    body(mesh, rig, j)
    eyes(mesh, rig)
    fins(mesh, rig, j)
    return mesh


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig, j = build_rig()
    mesh = build_mesh(rig, j)
    info = ck.export_creature(mesh, rig, export_clips(rig, mesh), args.out, extras={"hymn_creature": "shoal_skipper"})
    print(f"shoal_skipper: {info}")


if __name__ == "__main__":
    main()
