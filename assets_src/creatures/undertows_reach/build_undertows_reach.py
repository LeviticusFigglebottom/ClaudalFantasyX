"""The Undertow's Reach, the Ch8 boss's near part (M3-CRE-06; final pass M3-CRB-007):
docs/kb/art/creatures/act1/undertows_reach.md and m2-slice's act1_ch08 §5 and §9.

blender --background --factory-startup --python assets_src/creatures/undertows_reach/build_undertows_reach.py -- \
    --out assets/creatures/undertows_reach/undertows_reach.glb

A limb of the storm itself, not a spawn: a tower-thick forearm of black water coming down out of the storm wall behind
the parapet, splaying into a hand of spawn-crust that grips the wall-head. Only the forearm and hand are modelled; the
rest is the PC GPU session's storm.

The forearm is a rope of seven twisting water strands, running in surge folds (foam-pale on their crests, streaked
along the flow, storm-slate stretches in the abyss-navy black); three strands peel off it and rejoin, and at the storm
end it unravels into strands that thin away into the storm. Wreckage is fused into it: two broken masts with iron
bands and splintered ends (one carrying a yard, rope lashing and a drowned lantern), a chain draped from a mast stub,
hull planks, half a ship's wheel, rope wound round the wrist. Two drowned spawn bodies, segmented and ridged, are half
swallowed in it. Two door-sized wounds split it open (ADR 0151): recessed seams with layered, torn lips and the
`spawn_wound` light deep inside; the larger faces the party, turned toward the battle camera's flank (the stand-in's
90 degree yaw shows the battle camera the model's -X side; the review stage's three-quarter view shows +X).

The hand is a broad mass of water under crust plates. Its six digits (six, so it never reads as a man's hand) are
long and jointed: a water core under overlapping crust plates (keeled, worn pale at the edges, chipped at the end),
knuckles swelling at each joint, barnacles, and a hooked crust claw at each tip gouging into the stone.

Three states (phases): the Grip (idle), the Dark (`idle_dark`, the hand lifted and closing), the Breach
(`idle_breach`, drawn back over the sea, gathering).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 8801
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "storm_slate": "#3E4A57", "spawn_wound": "#3FE0C8",
    "deep_teal_shadow": "#0E4A55", "timber_weathered": "#7E6A55", "foam_white": "#EEF6F4", "bone": "#E6DAC0",
    "overcast_slate": "#6F7E8E", "laterite": "#A8573A", "volcanic_stone": "#3A3A3F", "foliage_shadow": "#1E4A3A",
    "coral_stone_weathered": "#B9AE98", "saltgrass": "#B9B26A", "brass": "#B08D57", "bronze_patina": "#5F8A78",
    "salt_glass": "#BFE6E0",
}.items()}

X_AX = np.array([1.0, 0.0, 0.0])
NA = 5  # arm bones, storm end first
WRIST = np.array([0.0, 3.0, -0.6])
# six digits, not five (a storm's grip, not a man's): knuckle x, splay, length, girth
DIGITS = ((-2.1, -0.5, 2.6, 0.62), (-1.3, -0.25, 3.4, 0.8), (-0.4, -0.05, 3.8, 0.9), (0.55, 0.12, 3.5, 0.85),
          (1.45, 0.32, 3.0, 0.75), (2.15, 0.6, 2.2, 0.6))
DIGIT_TIP_Y = 0.45  # the last joint stands over the stone; the claw hooks down from it into the stone
LOBES = 6  # the rope's water strands
PITCH = 7.5  # metres per full twist of the rope
# The wounds (bone-path parameter u, angle phi round the forearm, length, width in metres): phi 0 is +X, pi/2 the
# front (toward the party, over the top), pi the -X flank (the battle camera's side). The first is the larger.
WOUNDS = ((0.64, math.pi / 2 + 0.55, 3.0, 1.35), (0.42, math.pi / 2 - 0.8, 2.4, 1.05))
# The drowned spawn bodies, half swallowed: (u, phi, length, width, height, heading turn in degrees)
SHELLS = ((0.3, math.pi / 2 + 1.1, 2.8, 1.3, 0.85, 20.0), (0.85, math.pi / 2 - 0.65, 2.3, 1.1, 0.75, -35.0))


# ---------------------------------------------------------------------------------------------
# Small helpers (local to this build)
# ---------------------------------------------------------------------------------------------
def g(x, w):
    return np.exp(-(np.asarray(x, dtype=np.float64) / w) ** 2)


def angdiff(a, b):
    return np.angle(np.exp(1j * (np.asarray(a, dtype=np.float64) - b)))


def noise1(x, seed: int):
    x = np.atleast_1d(np.asarray(x, dtype=np.float64))
    return ck.value_noise(np.column_stack([x, np.full(len(x), 0.37 * seed), np.full(len(x), 1.7)]), seed)


def orient(P: np.ndarray, T: np.ndarray, C) -> np.ndarray:
    """Winds T outward: away from the per-vertex centres C, or from one point C."""
    C = np.asarray(C, dtype=np.float64)
    a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
    fn = np.cross(b - a, c - a)
    inner = C if C.ndim == 1 else (C[T[:, 0]] + C[T[:, 1]] + C[T[:, 2]]) / 3.0
    out = (a + b + c) / 3.0 - inner
    if np.sum(np.einsum("ij,ij->i", fn, out) < 0.0) > len(T) / 2:
        return ck.flip(T)
    return T


def loft(rings: list[np.ndarray], cap_start=None, cap_end=None, centres=None):
    """Closed loops (equal vertex counts) joined in order; optional fan caps to a point. Returns P, T, centres."""
    n = len(rings[0])
    P = np.vstack(rings)
    cen = [r.mean(axis=0) for r in rings] if centres is None else list(centres)
    C = np.vstack([np.repeat(np.asarray(c)[None], n, axis=0) for c in cen])
    parts = [orient(P, ck.grid_tris(len(rings), n, True), C)]
    for tip, ring, inner in ((cap_start, 0, 1), (cap_end, len(rings) - 1, len(rings) - 2)):
        if tip is None:
            continue
        idx = len(P)
        P = np.vstack([P, np.asarray(tip, dtype=np.float64)[None]])
        C = np.vstack([C, np.asarray(cen[ring])[None]])
        r0 = ring * n
        cap = np.array([(r0 + q, idx, r0 + (q + 1) % n) for q in range(n)], dtype=np.int64)
        parts.append(orient(P, cap, np.asarray(cen[inner])))
    return P, np.vstack(parts), C


def basis(d: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    d = d / np.linalg.norm(d)
    a = np.array([0.0, 1.0, 0.0]) if abs(d[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
    e1 = np.cross(d, a)
    e1 /= np.linalg.norm(e1)
    return e1, np.cross(d, e1)


def nail(base, d, length, width, bend_dir, bend, sides: int = 4, twist=0.0):
    """A sharp, bent spike (a claw's hook, a leg, a splinter): base polygon, a narrower bent middle, a point."""
    d = d / np.linalg.norm(d)
    e1, e2 = basis(d)
    rows = []
    for t, w, tw in ((-0.012, width, 0.0), (0.55, width * 0.6, twist)):
        c = base + d * length * t + bend_dir * bend * length * max(t, 0.0) ** 2 * 0.6
        a = np.radians(45.0 + tw) + np.arange(sides) * 2.0 * math.pi / sides
        rows.append(c + w * (np.outer(np.cos(a), e1) + np.outer(np.sin(a), e2)))
    tip = base + d * length + bend_dir * bend * length * 0.6
    P = np.vstack(rows + [tip[None]])
    n = sides
    T = []
    for q in range(n):
        q1 = (q + 1) % n
        T += [(q, n + q, q1), (q1, n + q, n + q1), (n + q, 2 * n, n + q1)]
    T = np.asarray(T, dtype=np.int64)
    C = np.vstack([np.repeat(base[None], n, 0), np.repeat((base + d * length * 0.55)[None], n, 0),
                   (base + d * length * 0.9)[None]])
    return P, orient(P, T, C)


def splinter_rings(end, tan, ring, rng, reach: float = 1.0, pinch=(0.12, 0.6)) -> list[np.ndarray]:
    """Two jagged rings past a broken end: each corner runs on as a splinter of its own length."""
    ext = rng.uniform(0.04, 0.3, len(ring)) * reach
    ext[rng.integers(0, len(ring))] = rng.uniform(0.4, 0.6) * reach
    off = ring - end
    r1 = end + off * 0.9 + np.outer(ext * 0.45, tan)
    r2 = end + off * rng.uniform(*pinch, len(ring))[:, None] + np.outer(ext, tan)
    return [r1, r2]


def catmull(pts, n: int) -> np.ndarray:
    """n points on a Catmull-Rom curve through pts, evenly spaced by arclength."""
    pts = np.asarray(pts, dtype=np.float64)
    Q = np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]])
    seg = len(pts) - 1
    dense = []
    for i in range(seg * 40 + 1):
        f = i / 40.0
        k = min(int(f), seg - 1)
        t = f - k
        p0, p1, p2, p3 = Q[k], Q[k + 1], Q[k + 2], Q[k + 3]
        dense.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                            (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    dense = np.array(dense)
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(dense, axis=0), axis=1))])
    q = np.linspace(0.0, s[-1], n)
    return np.column_stack([np.interp(q, s, dense[:, i]) for i in range(3)])


def resample(path: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Points at arclength fractions q (0..1) along a polyline."""
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
    return np.column_stack([np.interp(np.asarray(q) * s[-1], s, path[:, i]) for i in range(3)])


def tangents(path: np.ndarray) -> np.ndarray:
    t = np.gradient(path, axis=0)
    return t / np.linalg.norm(t, axis=1, keepdims=True)


def barnacle(mesh: ck.Mesh, p, n, rho: float, rng, skin, wet: float = 0.4) -> None:
    """One barnacle: a six-sided cone, its rim notched, its mouth a black pit."""
    n = n / np.linalg.norm(n)
    e1, e2 = basis(n)
    h = rho * rng.uniform(0.6, 1.0)
    a = rng.uniform(0, 2 * math.pi) + np.arange(6) * math.pi / 3
    base = p - n * rho * 0.25 + rho * (np.outer(np.cos(a), e1) + np.outer(np.sin(a), e2))
    rim = p + n * h + 0.5 * rho * (np.outer(np.cos(a + 0.5), e1) + np.outer(np.sin(a + 0.5), e2))
    pit = p + n * h * 0.45
    Pb = np.vstack([base, rim, pit[None]])
    Tb = [(i, (i + 1) % 6, 6 + i) for i in range(6)] + [((i + 1) % 6, 6 + (i + 1) % 6, 6 + i) for i in range(6)]
    Tb += [(6 + i, 6 + (i + 1) % 6, 12) for i in range(6)]
    Tb = orient(Pb, np.asarray(Tb, dtype=np.int64), p - n * rho)
    shell = ck.mix(PAL["coral_stone_weathered"] * 0.62, PAL["bone"] * 0.72, rng.uniform(0, 0.5))
    col = np.vstack([np.repeat((shell * 0.6)[None], 6, 0), np.repeat(shell[None], 6, 0), PAL["lacquer_black"][None]])
    cav = np.concatenate([np.full(6, 0.55), np.full(6, 0.1), [1.0]])
    ck.finish(mesh, Pb, Tb, "crust", col, skin, wet=wet, cavity=cav, flat=True)


# ---------------------------------------------------------------------------------------------
# The forearm's centreline, measured: the bones' curve, run on back into the storm and down into the palm
# ---------------------------------------------------------------------------------------------
def arm_path(n: int) -> np.ndarray:
    return ck.bezier([(0.6, 15.0, -10.0), (0.3, 13.5, -3.0), (0.0, 8.0, -1.0), WRIST], n)  # over the top


_NB = 2001
_B = arm_path(_NB)
_T0 = (_B[1] - _B[0]) / np.linalg.norm(_B[1] - _B[0])
_T1 = (_B[-1] - _B[-2]) / np.linalg.norm(_B[-1] - _B[-2])
EXT_DOWN = 0.9
_NPRE = 600
# before the bones' curve the limb turns up into the storm as a narrowing, twisting spout (kept compact: the
# boss-intro camera fits the model's bounds)
_Q2 = _B[0] - _T0 * 2.0
_PRE = ck.bezier([_Q2 + np.array([0.4, 3.4, -1.0]), _Q2 + np.array([0.2, 1.0, -0.7]), _Q2, _B[0]], _NPRE + 1)[:-1]
_PC = np.vstack([_PRE, _B, _B[-1] + np.outer(np.linspace(0.0, EXT_DOWN, 101)[1:], _T1)])
_PS = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(_PC, axis=0), axis=1))])
_PT = tangents(_PC)
LEN = float(_PS[-1])
S_BONE0 = float(_PS[_NPRE])
S_WRIST = float(_PS[_NPRE + _NB - 1])
_BU = np.linspace(0.0, 1.0, _NB)


def s_of_u(u):
    return np.interp(u, _BU, _PS[_NPRE:_NPRE + _NB])


def u_of_s(s):
    return np.interp(s, _PS[_NPRE:_NPRE + _NB], _BU)


def frame(s) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """(centre, tangent toward the hand, front (d), side) at arclength(s) s; vectorised over s."""
    s = np.atleast_1d(np.asarray(s, dtype=np.float64))
    c = np.column_stack([np.interp(s, _PS, _PC[:, i]) for i in range(3)])
    t = np.column_stack([np.interp(s, _PS, _PT[:, i]) for i in range(3)])
    t /= np.linalg.norm(t, axis=1, keepdims=True)
    d = np.cross(t, X_AX)
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    side = np.cross(d, t)
    return c, t, d, side


def radius(s):
    s = np.asarray(s, dtype=np.float64)
    u = u_of_s(s)
    r = 1.5 - 0.25 * np.sin(u * math.pi) + 0.25 * ck.smoothstep(0.8, 1.0, u)
    r = r * (1.0 + 0.2 * ck.smoothstep(S_BONE0, S_BONE0 - 6.0, s))  # thicker where it comes out of the storm
    return r * (0.12 + 0.88 * ck.smoothstep(0.0, 4.5, s) ** 0.8)  # and narrowing to a spout up into the storm


def section(s):
    """The section's side and front scales: wider side to side and flatter toward the wrist."""
    w = ck.smoothstep(S_WRIST - 3.0, S_WRIST, np.asarray(s, dtype=np.float64))
    return 1.0 + 0.2 * w, 1.0 - 0.15 * w


def twist(s):
    s = np.asarray(s, dtype=np.float64)
    return 2.0 * math.pi * s / PITCH + 0.35 * np.sin(s * 0.27) - 2.5 * ck.smoothstep(4.5, 0.0, s) ** 1.5


def surface(s: float, phi: float, lift: float = 0.0) -> tuple[np.ndarray, np.ndarray, int]:
    """A rest-surface point of the forearm (undisplaced, plus `lift` outward), its outward direction, its arm bone."""
    c, _t, d, side = frame(s)
    sx, sy = section(s)
    out = math.cos(phi) * side[0] + math.sin(phi) * d[0]
    r = float(radius(s))
    p = c[0] + r * (sx * math.cos(phi) * side[0] + sy * math.sin(phi) * d[0]) + out * lift
    return p, out / np.linalg.norm(out), arm_bone(float(u_of_s(s)))


def arm_bone(u: float) -> str:
    return f"arm{min(NA - 1, max(0, int(u * NA)))}"


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def digit_pts(i: int) -> np.ndarray:
    """Four joints from knuckle to tip: up and over the wall-head's lip, then down to the stone."""
    x, splay, ln, _ = DIGITS[i]
    k = np.array([x * 1.15, 2.1 - 0.15 * abs(x), 0.5 - 0.3 * abs(x)])
    d = np.array([math.sin(splay), 0.0, math.cos(splay)])
    j1 = k + d * ln * 0.36 + np.array([0, 0.45, 0])
    j2 = j1 + d * ln * 0.34 + np.array([0, -0.5, 0])
    tip = j2 + d * ln * 0.22 + np.array([0, -2.0, 0])
    tip[1] = DIGIT_TIP_Y
    return np.array([k, j1, j2, tip])


def wound_point(k: int) -> tuple[np.ndarray, np.ndarray, str]:
    u, phi, _ln, _w = WOUNDS[k]
    s = float(s_of_u(u))
    p, out, bone = surface(s, phi)
    return p - out * 0.15, out, bone


def build_rig() -> tuple[ck.Rig, np.ndarray]:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.5, 0))
    ja = arm_path(NA + 1)
    for i in range(NA):
        rig.add(f"arm{i}", ja[i], ja[i + 1], "root" if i == 0 else f"arm{i - 1}")
    rig.add("hand", WRIST, WRIST + np.array([0, -0.6, 0.9]), f"arm{NA - 1}")
    for i in range(len(DIGITS)):
        j = digit_pts(i)
        for s in range(3):
            rig.add(f"digit{i}_{s}", j[s], j[s + 1], "hand" if s == 0 else f"digit{i}_{s - 1}")
    # VFX anchors (unweighted): the larger wound, the forearm's centre of mass, the wrist where the grip breaks
    pw, nw, bw = wound_point(0)
    rig.add("vfx_wound", pw, pw + nw * 0.4, bw)
    cc = frame(s_of_u(0.5))[0][0]
    rig.add("vfx_core", cc, cc + np.array([0.0, 0.5, 0.0]), "arm2")
    rig.add("vfx_phase", WRIST, WRIST + np.array([0.0, 0.0, 0.5]), "hand")
    return rig, ja


def arm_skin(rig: ck.Rig, ja: np.ndarray):
    """The forearm on the arm chain, its last span (into the palm) on the hand."""
    return rig.chain([f"arm{i}" for i in range(NA)] + ["hand"], np.vstack([ja, (WRIST + _T1 * EXT_DOWN)[None]]))


# ---------------------------------------------------------------------------------------------
# Water colour
# ---------------------------------------------------------------------------------------------
def water_color(P, flow, across_a, across_r, seed: int, crest=0.0, groove=0.0):
    """Black storm-water: abyss-navy to lacquer black, pale storm-slate stretches, streaks running with the flow
    (noise stretched along it), deep-teal depth, foam-pale crests. `flow` is metres along the flow; `across_a` an
    angle round the strand bundle and `across_r` its radius (the streaks wrap without a seam)."""
    n = len(P)
    big = ck.fbm(P * 0.16, seed)
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.3, 0.3, big)[:, None])
    region = ck.smoothstep(-0.05, 0.3, ck.fbm(P * 0.1 + 3.1, seed + 1))
    col = ck.mix(col, PAL["storm_slate"] * 1.1, (0.75 * region)[:, None])
    ca, sa = np.cos(across_a) * across_r, np.sin(across_a) * across_r
    q1 = np.column_stack([ca * 2.6, sa * 2.6, np.asarray(flow) * 0.1])
    q2 = np.column_stack([ca * 6.0, sa * 6.0, np.asarray(flow) * 0.22 + 7.0])
    streak = ck.smoothstep(0.15, 0.65, ck.value_noise(q1, seed + 2))
    fine = ck.smoothstep(0.3, 0.75, ck.value_noise(q2, seed + 3))
    col = ck.mix(col, PAL["storm_slate"] * 1.45, (0.6 * streak)[:, None])
    col = ck.mix(col, PAL["overcast_slate"], (0.55 * fine * (0.3 + 0.7 * streak))[:, None])
    depth = ck.smoothstep(0.1, 0.5, ck.fbm(P * 0.45, seed + 4))
    col = ck.mix(col, PAL["deep_teal_shadow"] * 0.75, (0.3 * depth)[:, None])
    col = ck.mix(col, PAL["abyss_navy"] * 0.7, (0.75 * np.broadcast_to(groove, (n,)))[:, None])
    froth = ck.smoothstep(-0.1, 0.35, ck.fbm(P * np.array([2.4, 2.4, 2.4]), seed + 5))
    foam = np.clip(np.broadcast_to(crest, (n,)) * froth, 0.0, 1.0)
    col = ck.mix(col, PAL["foam_white"] * 0.8, (0.85 * foam)[:, None])
    return col, foam


# ---------------------------------------------------------------------------------------------
# The forearm
# ---------------------------------------------------------------------------------------------
NR, NS = 70, 36


def ring_positions() -> np.ndarray:
    s = np.linspace(0.0, LEN, 4001)
    dens = 1.0 + sum(2.4 * g(s - float(s_of_u(w[0])), 0.55 * w[2] + 0.5) for w in WOUNDS)
    dens = dens + 0.6 * g(s - S_WRIST, 2.0)
    dens = dens * np.where(s < S_BONE0, 0.45, 1.0)
    cdf = np.concatenate([[0.0], np.cumsum(0.5 * (dens[1:] + dens[:-1]) * np.diff(s))])
    return np.interp(np.linspace(0.0, cdf[-1], NR), cdf, s)


def phi_positions() -> np.ndarray:
    """Round the forearm: denser on the front (where the wounds are and where both cameras look)."""
    p = np.linspace(0.0, 2.0 * math.pi, 4001)
    dens = 1.0 + 0.6 * g(angdiff(p, math.pi / 2), 1.2)
    dens = dens + sum(2.2 * g(angdiff(p, w[1]), 0.5 * w[3] / 1.5 + 0.12) for w in WOUNDS)
    cdf = np.concatenate([[0.0], np.cumsum(0.5 * (dens[1:] + dens[:-1]) * np.diff(p))])
    return np.interp(np.linspace(0.0, cdf[-1], NS + 1)[:-1], cdf, p)


def wound_fields(S, PH, R):
    """(open, core, lip, spill, depth) of the two wounds at forearm coordinates."""
    n = len(S)
    opn, core, lip, spill, recess, rim, tear = (np.zeros(n) for _ in range(7))
    for k, (u, phi0, ln, wd) in enumerate(WOUNDS):
        s0 = float(s_of_u(u))
        a = (S - s0) / (0.5 * ln)
        b = angdiff(PH, phi0) * R / (0.5 * wd)
        b = b - 0.22 * np.sin(a * 2.3 + k)  # a slight S along its length
        inside = np.abs(a) < 1.0
        lens = np.clip(1.0 - a * a, 0.0, 1.0) ** 0.55
        jag = 0.8 + 0.2 * noise1(a * 6.0 + 13.0 * k, SEED + 60 + k) - 0.22 * np.maximum(
            noise1(a * 17.0 + 5.0 * k, SEED + 62 + k), 0.0)
        hw = lens * jag + 1e-3
        d = np.abs(b) / hw
        o = ck.smoothstep(1.0, 0.82, d) * inside
        opn = np.maximum(opn, o)
        core = np.maximum(core, ck.smoothstep(0.42, 0.03, d) * (lens > 0.2))
        ln_w = np.sqrt(lens)
        lp = (np.exp(-((d - 1.17) / 0.2) ** 2) + 0.55 * np.exp(-((d - 1.75) / 0.28) ** 2)) * ln_w
        lip = np.maximum(lip, lp)
        tear = np.maximum(tear, np.exp(-((d - 1.05) / 0.12) ** 2) * ln_w)
        spill = np.maximum(spill, np.exp(-(np.maximum(np.abs(b) - hw, 0.0) / 1.4) ** 2) * ln_w *
                           ck.smoothstep(1.4, 0.9, np.abs(a)))
        rec = -(0.55 * np.sqrt(np.clip(1.0 - d * d, 0.0, 1.0)) + 0.06) * o
        folds = 0.06 * np.sin(a * 13.0 + b * 1.7 + k) * o * (1.0 - ck.smoothstep(0.7, 0.08, d))
        dip = -0.05 * np.exp(-((d - 1.45) / 0.12) ** 2) * ln_w
        recess = np.minimum(recess, rec + folds)
        rim = rim + np.where(o > 0.0, 0.0, 0.3 * lp + dip)
    return opn, core, lip, spill, recess + rim, tear


def shell_bulge(S, PH, R):
    """Water piled round the half-swallowed spawn bodies."""
    out = np.zeros(len(S))
    for u, phi0, ln, wd, _h, _turn in SHELLS:
        s0 = float(s_of_u(u))
        out = np.maximum(out, g(S - s0, 0.65 * ln) * g(angdiff(PH, phi0) * R, 0.75 * wd))
    return out


def forearm(mesh: ck.Mesh, rig: ck.Rig, ja: np.ndarray) -> dict:
    s_r = ring_positions()
    phi = phi_positions()
    C, _Tn, D, SD = frame(s_r)
    rad = radius(s_r)
    sx, sy = section(s_r)
    S = np.repeat(s_r, NS)
    PH = np.tile(phi, NR)
    cph, sph = np.cos(PH), np.sin(PH)
    R = np.repeat(rad, NS)
    centre = np.repeat(C, NS, axis=0)
    Dv = np.repeat(D, NS, axis=0)
    Sv = np.repeat(SD, NS, axis=0)
    out = cph[:, None] * Sv + sph[:, None] * Dv
    P0 = centre + R[:, None] * (np.repeat(sx, NS)[:, None] * cph[:, None] * Sv +
                                np.repeat(sy, NS)[:, None] * sph[:, None] * Dv)
    # the rope: seven strands twisting down the limb, grooves between them; each strand its own girth
    rel = PH - twist(S)
    lobe_x = 0.5 * LOBES * rel
    hump = np.abs(np.cos(lobe_x)) ** 0.5
    lobe_id = np.mod(np.floor((rel + math.pi / LOBES) / (2.0 * math.pi / LOBES)), LOBES)
    girth = 0.8 + 0.4 * (noise1(lobe_id * 3.3 + S * 0.12, SEED + 1) * 0.5 + 0.5)
    storm = ck.smoothstep(S_BONE0 + 4.0, 0.0, S)
    palm = ck.smoothstep(S_WRIST - 1.0, LEN, S)
    torn = ck.smoothstep(4.2, 0.0, S)  # the spout up into the storm, mist-pale
    rope = R * (0.2 + 0.08 * storm + 0.1 * torn) * (hump * girth - 0.62) * (1.0 - 0.6 * palm)
    # surge folds: crests running down the limb across the strands, a slow rise and a steep front toward the hand
    q = S / 1.9 - 2.0 * PH / (2.0 * math.pi) + 1.1 * ck.fbm(P0 * 0.3, SEED + 2)
    fr = q - np.floor(q)
    crest = ck.smoothstep(0.4, 0.82, fr) * ck.smoothstep(1.0, 0.87, fr)
    patchy = ck.smoothstep(-0.2, 0.25, ck.fbm(P0 * 0.35, SEED + 3))
    fold = 0.22 * crest * patchy * (0.25 + 0.75 * hump)
    swell = 0.24 * ck.fbm(P0 * 0.4, SEED + 4) * (1.2 - 0.4 * palm)
    opn, core, lip, spill, depth, tear = wound_fields(S, PH, R)
    calm = 1.0 - np.clip(opn + 0.7 * lip, 0.0, 1.0)  # the wound's lips are torn crust, not running water
    bulge = shell_bulge(S, PH, R)
    disp = (rope + fold + swell) * calm + depth + 0.28 * bulge
    P = P0 + out * disp[:, None]
    T = orient(P, ck.grid_tris(NR, NS, True), centre)
    # caps: the storm end (inside the unravelling strands) and the end inside the palm
    nv = len(P)
    P = np.vstack([P, C[0][None], C[-1][None]])
    P[nv] = C[0] - _Tn[0] * 0.35  # the spout's tip
    cap0 = np.array([(q2, nv, (q2 + 1) % NS) for q2 in range(NS)], dtype=np.int64)
    r1 = (NR - 1) * NS
    cap1 = np.array([(r1 + q2, r1 + (q2 + 1) % NS, nv + 1) for q2 in range(NS)], dtype=np.int64)
    T = np.vstack([T, orient(P, cap0, C[1]), orient(P, cap1, C[-2])])
    # colour
    groove = (1.0 - hump) ** 2 * calm
    col, foam = water_color(P0, S, rel, R, SEED + 10,
                            crest=(crest * patchy * hump * 1.6 + 0.5 * bulge + 0.6 * torn * hump) * calm,
                            groove=groove * 0.8)
    col = ck.mix(col, PAL["storm_slate"] * 1.15, (0.3 * hump * girth * calm * (1 - foam))[:, None])
    col = ck.mix(col, PAL["overcast_slate"] * 1.15, (0.7 * torn ** 1.3 * (0.5 + 0.5 * hump))[:, None])
    # the wounds: bruised water round them, layered lips of torn crust, dark wet flesh, the light deep inside
    col = ck.mix(col, PAL["abyss_navy"] * 0.8, (0.6 * spill * (1 - opn))[:, None])
    col = ck.mix(col, PAL["lacquer_black"], (0.8 * lip * (1 - opn))[:, None])
    col = ck.mix(col, PAL["storm_slate"] * 1.6, (0.75 * np.clip((lip - 0.5) * 2.0, 0, 1) * (1 - opn))[:, None])
    col = ck.mix(col, PAL["overcast_slate"] * 1.1, (0.75 * tear * (1 - opn))[:, None])
    # flesh strands across the split, the light coming up between them
    strands = 0.5 + 0.5 * np.sin(S * 11.0 + 2.5 * ck.fbm(P0 * 1.5, SEED + 16))
    fib = (0.25 + 0.75 * ck.smoothstep(-0.25, 0.3, ck.fbm(P0 * np.array([11.0, 4.0, 11.0]), SEED + 15))) * (
        0.35 + 0.65 * strands)
    col = ck.mix(col, PAL["deep_teal_shadow"] * 0.25, opn[:, None])
    col = ck.mix(col, PAL["deep_teal_shadow"] * 0.9, (opn * strands * (1 - core))[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.9 * (0.4 + 0.6 * fib[:, None]), ck.smoothstep(0.25, 0.9, core)[:, None])
    emission = np.clip(0.05 * opn + 0.95 * ck.smoothstep(0.15, 0.9, core) * fib + 0.06 * tear, 0.0, 1.0)
    cav = np.clip(0.1 + 0.65 * groove + 0.8 * np.clip(opn - core, 0, 1) + 0.25 * spill, 0.0, 1.0)
    cav = np.concatenate([cav, [1.0, 1.0]])
    col = np.vstack([col, col[:1], col[-1:]])
    emission = np.concatenate([emission, [0.0, 0.0]])
    skin = arm_skin(rig, ja)
    wet = np.concatenate([np.clip(1.0 - 0.5 * foam - 0.45 * torn, 0.3, 1.0), [1.0, 1.0]])
    ck.finish(mesh, P, T, "water", col, skin, wet=wet, cavity=cav, emission=emission)
    return {"skin": skin}


def strand(mesh: ck.Mesh, path: np.ndarray, rad: np.ndarray, segs: int, skin, seed: int, crest_scale: float = 1.0,
           cap_end: bool = True, foam_tip: float = 0.0) -> None:
    """One water strand along a path: twisted, streaked, foam on its crests and (optionally) its thinning end."""
    P, T = ck.tube(path, rad, segs, cap_start=False, cap_end=cap_end)
    K = len(path)
    f = np.concatenate([np.repeat(np.linspace(0, 1, K), segs), [1.0] * (len(P) - K * segs)])
    a = np.concatenate([np.tile(np.arange(segs) * 2 * math.pi / segs, K), [0.0] * (len(P) - K * segs)])
    ln = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
    fl = np.concatenate([np.repeat(ln, segs), [ln[-1]] * (len(P) - K * segs)])
    tw = a + fl * 1.1
    crest = ck.smoothstep(0.6, 0.95, np.sin(fl * 2.2 + 0.8 * np.sin(tw)) * 0.5 + 0.5) * crest_scale
    c = path[np.minimum((np.arange(len(P)) // segs), K - 1)]
    outn = P - c
    outn /= np.maximum(np.linalg.norm(outn, axis=1, keepdims=True), 1e-9)
    rr = np.concatenate([np.repeat(rad, segs), [0.0] * (len(P) - K * segs)])
    P = P + outn * (0.12 * rr * np.cos(2.0 * tw) + 0.1 * rr * ck.fbm(P * 1.2, seed))[:, None]
    col, foam = water_color(P, fl, tw, np.maximum(rr, 0.05), seed, crest=crest + foam_tip * f ** 2,
                            groove=0.3 * (1 - np.abs(np.cos(tw))))
    ck.finish(mesh, P, T, "water", col, skin, wet=1.0, cavity=0.15 + 0.3 * (1 - foam))


def loose_strands(mesh: ck.Mesh, rig: ck.Rig, bd: dict) -> None:
    """Strands peeling off the rope and rejoining it."""
    rng = np.random.default_rng(SEED + 20)
    for k, (u0, u1, lobe, lift) in enumerate(((0.04, 0.3, 1, 0.75), (0.1, 0.33, 4, 0.55), (0.74, 0.97, 2, 0.6))):
        s = np.linspace(float(s_of_u(u0)), float(s_of_u(u1)), 18)
        f = np.linspace(0.0, 1.0, 18)
        c, _t, d, side = frame(s)
        sx, sy = section(s)
        ph = twist(s) + 2.0 * math.pi * lobe / LOBES
        out = np.cos(ph)[:, None] * side + np.sin(ph)[:, None] * d
        r = radius(s)
        lf = lift * np.sin(math.pi * f) ** 1.4
        path = c + (r * 0.93)[:, None] * (sx * np.cos(ph))[:, None] * side + (r * 0.93)[:, None] * (
            sy * np.sin(ph))[:, None] * d + out * lf[:, None]
        rad = 0.46 * (1.0 - 0.3 * np.sin(math.pi * f)) * (0.9 + 0.2 * rng.random())
        strand(mesh, path, rad, 6, bd["skin"], SEED + 21 + k, cap_end=False)


# ---------------------------------------------------------------------------------------------
# The hand
# ---------------------------------------------------------------------------------------------
PALM_C = np.array([0.0, 2.15, -0.15])
PALM_R = np.array([2.75, 1.0, 1.6])


def cr_eval(arr: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Catmull-Rom through the rows of arr (K, d) at fractional row indices x (n,)."""
    arr = np.asarray(arr, dtype=np.float64)
    K = len(arr)
    Q = np.vstack([2 * arr[0] - arr[1], arr, 2 * arr[-1] - arr[-2]])
    k = np.clip(np.floor(x).astype(np.int64), 0, K - 2)
    t = (x - k)[:, None]
    p0, p1, p2, p3 = Q[k], Q[k + 1], Q[k + 2], Q[k + 3]
    return 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                  (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)


def crust_plate(mesh: ck.Mesh, path: np.ndarray, dorsal: np.ndarray, side: np.ndarray, rad: np.ndarray,
                arc: float, thick: float, skin, rng, wet: float = 0.55, na: int = 8) -> np.ndarray:
    """A curved crust plate lying over a part: a domed shell over `dorsal`, lofted along `path` (K rings, refined
    to half as many again), keeled down the middle, its leading edge flared up, its side edges notched and its
    trailing edge serrated. The broad face is one smooth-shaded surface (its normals its own); the rim is a separate
    wall tucked down into the part beneath, so the plate's edge stays crisp while its face reads as curved, crusted
    shell. Wetness pools in the growth grooves and the low ground, the crests and the worn rim are dry and rough.
    Returns the plate's top points at the K input rings (for barnacles and spurs)."""
    K = len(path)
    lumps = rng.normal(0.0, 1.0, (K, na))
    chip = rng.uniform(0.0, 0.12, na) + 0.26 * (np.arange(na) % 2) * rng.uniform(0.4, 1.0, na)  # serrated
    seed_tone, seed_salt = int(rng.integers(0, 10000)), int(rng.integers(0, 10000))
    Ko, Na = (3 * K - 1) // 2, na + 2
    x = np.linspace(0.0, K - 1.0, Ko)
    u = x / (K - 1.0)
    pth, dor, sid = cr_eval(path, x), cr_eval(dorsal, x), cr_eval(side, x)
    dor /= np.linalg.norm(dor, axis=1, keepdims=True)
    sid /= np.linalg.norm(sid, axis=1, keepdims=True)
    tan = tangents(pth)
    rd = np.interp(x, np.arange(K), rad)
    v = np.linspace(-1.0, 1.0, Na)
    U, V = np.repeat(u, Na), np.tile(v, Ko)
    notch = (np.arange(Ko) % 2 == 1) & (np.arange(Ko) > 0) & (np.arange(Ko) < Ko - 1)
    TH = V * arc * (1.0 - 0.07 * np.repeat(notch, Na) * (np.abs(V) > 0.99))  # the side edge, notched
    # smooth lumps: the drawn lump grid sampled bilinearly
    li = np.clip(U * (K - 1), 0, K - 1.0001)
    lj = np.clip((V + 1.0) * 0.5 * (na - 1), 0, na - 1.0001)
    i0, j0 = li.astype(np.int64), lj.astype(np.int64)
    fi, fj = li - i0, lj - j0
    lump = ((1 - fi) * (1 - fj) * lumps[i0, j0] + fi * (1 - fj) * lumps[i0 + 1, j0] +
            (1 - fi) * fj * lumps[i0, j0 + 1] + fi * fj * lumps[i0 + 1, j0 + 1])
    RD = np.repeat(rd, Na)
    flare = 1.0 + 0.1 * ck.smoothstep(0.25, 0.0, U)
    dome = 0.8 * thick * (1.0 - V ** 2) * (0.2 + 0.8 * np.sin(math.pi * np.clip(U, 0.0, 1.0)))
    keel = thick * 1.1 * g(TH, 0.38) * (1.0 - 0.4 * U)
    growth = 0.5 + 0.5 * np.sin(U * 2.0 * math.pi * 3.5 + 0.7)
    ridge = 0.22 * thick * growth ** 2
    roll = 0.6 * thick * ck.smoothstep(0.7, 1.0, np.abs(V))  # the face rolls over into the rim
    ro = RD * flare + 0.68 * thick + dome + keel + ridge + 0.14 * thick * lump - roll
    ri = RD * flare * 0.9  # the rim wall tucks down into the part beneath
    cj = np.clip(np.round(lj).astype(np.int64), 0, na - 1)
    sh = -chip[cj] * ck.smoothstep(0.7, 1.0, U) * RD  # the chipped trailing edge
    D = np.cos(TH)[:, None] * np.repeat(dor, Na, axis=0) + np.sin(TH)[:, None] * np.repeat(sid, Na, axis=0)
    TN = np.repeat(tan, Na, axis=0)
    PC = np.repeat(pth, Na, axis=0)
    Po = PC + ro[:, None] * D + sh[:, None] * TN
    Pi = PC + ri[:, None] * D + sh[:, None] * TN
    To = orient(Po, ck.grid_tris(Ko, Na, False), PC)
    No = ck.vertex_normals(Po, To)
    # the rim: four walls from the face's boundary down to the tucked inner edge, shaded on their own
    loops = [np.arange(Ko) * Na, np.arange(Ko) * Na + Na - 1, np.arange(Na), (Ko - 1) * Na + np.arange(Na)]
    mid = pth[Ko // 2] + dor[Ko // 2] * rd[Ko // 2] * 0.5
    wP, wT, wN, wB, wI = [], [], [], [], []
    base = len(Po)
    for w, lp in enumerate(loops):
        Pw = np.vstack([Po[lp], Pi[lp]])
        Cw = np.vstack([PC[lp] + D[lp] * RD[lp, None] * 0.5] * 2) if w < 2 else mid
        Tw = orient(Pw, ck.grid_tris(2, len(lp), False), Cw)
        wN.append(ck.vertex_normals(Pw, Tw))
        wT.append(Tw + base)
        wP.append(Pw)
        wB.append(np.concatenate([np.zeros(len(lp)), np.ones(len(lp))]))
        wI.append(np.concatenate([lp, lp]))
        base += len(Pw)
    P = np.vstack([Po] + wP)
    T = np.vstack([To] + wT)
    N = np.vstack([No] + wN)
    src = np.concatenate([np.arange(len(Po))] + wI)  # the face vertex each vertex belongs to
    wall = np.concatenate([np.zeros(len(Po))] + [np.ones(len(p)) for p in wP])
    deep = np.concatenate([np.zeros(len(Po))] + wB)  # 1 at the wall's tucked foot
    Us, Vs, gs = U[src], V[src], growth[src]
    endf = np.maximum(ck.smoothstep(0.75, 1.0, Us), ck.smoothstep(0.15, 0.0, Us))
    keelm = g(TH[src], 0.3)
    rimm = np.maximum(ck.smoothstep(0.8, 1.0, np.abs(Vs)), endf * ck.smoothstep(0.5, 1.0, np.abs(Vs) + endf))
    lowl = ck.smoothstep(0.3, -0.8, lump[src]) * (1 - wall)  # the low ground between the lumps
    n1 = ck.fbm(P * 2.2, seed_tone)
    mott = ck.fbm(P * 6.5, seed_tone + 7)  # granular mottle, finer than the tone
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.25, 0.3, n1)[:, None])
    face = 1 - wall
    col = ck.mix(col, PAL["storm_slate"], (0.35 * face)[:, None])  # a dull crusted slate, not lacquer
    col = ck.mix(col, PAL["storm_slate"] * 1.25, (0.5 * ck.smoothstep(0.55, 0.95, gs) * face)[:, None])  # growth bands
    # granular two-tone mottle: pale crusted grains and black pits
    col = ck.mix(col, PAL["storm_slate"] * 1.35, (0.6 * ck.smoothstep(0.02, 0.3, mott) * face)[:, None])
    col = ck.mix(col, PAL["lacquer_black"] * 0.7, (0.6 * ck.smoothstep(-0.08, -0.3, mott) * face)[:, None])
    col = ck.mix(col, PAL["storm_slate"] * 1.7, (0.6 * keelm + 0.6 * rimm * face)[:, None])
    col = ck.mix(col, PAL["overcast_slate"] * 1.2, (0.8 * endf * face)[:, None])
    salt = ck.smoothstep(-0.08, 0.3, ck.fbm(P * 4.0, seed_salt))
    salt = np.maximum(salt, 0.9 * ck.smoothstep(0.5, 0.0, gs) * ck.smoothstep(-0.05, 0.25, mott))  # salt in grooves
    col = ck.mix(col, PAL["coral_stone_weathered"] * 0.95, (0.8 * salt * face * (1 - keelm))[:, None])
    # the broken rim: pale, worn shell at the lip, darkening down to the wet foot
    col = ck.mix(col, ck.mix(PAL["storm_slate"] * 1.5, PAL["overcast_slate"], 0.4), (wall * (1 - deep))[:, None])
    col = ck.mix(col, PAL["lacquer_black"] * 0.8, (wall * deep)[:, None])
    cav = np.clip(0.1 + 0.4 * (1 - gs) * (1 - wall) + 0.35 * lowl + 0.25 * ck.smoothstep(0.0, 0.4, -mott)
                  + 0.8 * wall * deep, 0, 1)
    damp = np.clip(0.55 * (1 - gs) + 0.6 * lowl + 0.4 * ck.smoothstep(0.1, -0.3, mott), 0.0, 1.0)
    wv = wet * (0.25 + 0.9 * damp) - 0.35 * endf - 0.35 * keelm - 0.3 * salt - 0.3 * rimm
    wv = np.where(wall > 0, 0.1 + 0.8 * deep, wv)
    ck.finish(mesh, P, T, "crust", col, skin, wet=np.clip(wv, 0.05, 1.0), cavity=cav, N=N)
    xi = np.round(np.arange(K) * (Ko - 1) / (K - 1.0)).astype(np.int64)
    return Po[xi * Na + Na // 2]


def palm(mesh: ck.Mesh, rig: ck.Rig, bd: dict) -> None:
    """The palm: a broad mass of water, its strands fanning from the wrist into the knuckles, under crust plates."""
    rng = np.random.default_rng(SEED + 40)
    prof = []
    for i in range(13):
        th = math.pi * i / 12
        prof.append((math.sin(th), math.cos(th)))
    P, T = ck.lathe(prof, 30)
    U = P.copy()
    P = P * PALM_R + PALM_C
    P[:, 1] -= 0.25 * ck.smoothstep(0.0, -1.0, U[:, 1]) * (1 - np.abs(U[:, 0]))  # a flatter underside
    P[:, 2] -= 0.35 * U[:, 0] ** 2 * ck.smoothstep(-0.3, 0.6, U[:, 2])  # the front follows the knuckles' arc
    top = ck.smoothstep(-0.1, 0.5, U[:, 1])
    ridge = np.zeros(len(P))
    knk = np.zeros(len(P))
    wtop = WRIST + np.array([0.0, 0.1, 0.0])
    for i in range(len(DIGITS)):
        k = digit_pts(i)[0]
        a, b = wtop[[0, 2]], k[[0, 2]]
        d = b - a
        t = np.clip(((P[:, [0, 2]] - a) @ d) / float(d @ d), 0.0, 1.0)
        dist = np.linalg.norm(P[:, [0, 2]] - (a + t[:, None] * d), axis=1)
        ridge = np.maximum(ridge, g(dist, 0.3) * ck.smoothstep(0.05, 0.4, t))
        knk = np.maximum(knk, g(np.linalg.norm(P - k, axis=1), 0.6))
    lump = ck.fbm(P * 0.9, SEED + 41)
    nrm = (P - PALM_C) / PALM_R
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
    P = P + nrm * (0.14 * ridge * top + 0.18 * knk + 0.08 * lump)[:, None]
    T = orient(P, T, PALM_C)
    flow = np.linalg.norm(P - wtop, axis=1)
    col, _foam = water_color(P, flow, np.arctan2(P[:, 0], P[:, 2] - 1.0), 1.5, SEED + 42,
                             crest=0.6 * ck.smoothstep(0.3, 0.9, ridge) * top, groove=0.6 * (1 - ridge) * top)
    under = ck.smoothstep(0.0, -0.7, U[:, 1])
    col = ck.mix(col, PAL["storm_slate"] * 0.9, (0.4 * under)[:, None])
    skin = bd["skin"]
    ck.finish(mesh, P, T, "water", col, skin, wet=1.0, cavity=0.15 + 0.45 * (1 - ridge) * top)
    # crust plates down the back of the hand, one over each strand that runs to a knuckle
    for i in range(len(DIGITS)):
        k = digit_pts(i)[0]
        a = wtop + (k - wtop) * 0.22
        b = k + np.array([0.0, 0.25, -0.15])
        path = ck.bezier([a, (a + b) * 0.5 + np.array([0.0, 0.35, 0.0]), b], 5)
        path[:, 1] += 0.05
        t = tangents(path)
        side = np.cross(t, np.array([0.0, 1.0, 0.0]))
        side /= np.linalg.norm(side, axis=1, keepdims=True)
        dorsal = np.cross(side, t)
        dorsal *= np.sign(dorsal[:, 1:2])
        rad = np.linspace(0.32, 0.42, 5) * (0.8 + 0.4 * DIGITS[i][3])
        pc = path - dorsal * rad[:, None] * 0.8
        tops = crust_plate(mesh, pc, dorsal, side, rad, 1.25, 0.09, skin, rng)
        for p in tops[1:4:2]:
            if rng.random() < 0.7:
                barnacle(mesh, p + rng.normal(0, 0.06, 3), dorsal[2], rng.uniform(0.07, 0.12), rng, skin)


def digit(mesh: ck.Mesh, rig: ck.Rig, i: int) -> None:
    """A long jointed digit: a water core swelling at each knuckle, crust plates over each phalanx, a hooked claw."""
    rng = np.random.default_rng(SEED + 100 + i)
    x, splay, ln, girth = DIGITS[i]
    j = digit_pts(i)
    root = j[0] - np.array([0.0, 0.0, 0.7])
    K = 30
    path = catmull([root, j[0], j[1], j[2], j[3]], K)
    tan = tangents(path)
    side0 = np.array([math.cos(splay), 0.0, -math.sin(splay)])
    dorsal = np.cross(tan, side0)
    dorsal /= np.linalg.norm(dorsal, axis=1, keepdims=True)
    side = np.cross(dorsal, tan)
    sl = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
    f = sl / sl[-1]
    sj = [float(sl[int(np.argmin(np.linalg.norm(path - jp, axis=1)))]) for jp in j]  # arclength at each joint
    r = 0.62 * girth * 1.15 * (1.0 - 0.58 * f ** 1.1)
    knuckle = sum(g(sl - sj[q], 0.32) * (0.2 if q else 0.12) for q in range(3))
    pinch = sum(g(sl - 0.5 * (sj[q] + sj[q + 1]), 0.4) for q in range(3))
    r = r * (1.0 + knuckle - 0.08 * pinch)
    segs = 16
    a = np.arange(segs) * 2.0 * math.pi / segs
    rings = []
    for k in range(K):
        sec = np.outer(np.cos(a) * 0.88, dorsal[k]) + np.outer(np.sin(a), side[k])
        rings.append(path[k] + r[k] * sec)
    P = np.vstack(rings)
    A = np.tile(a, K)
    SL = np.repeat(sl, segs)
    ventral = ck.smoothstep(0.2, -0.7, np.cos(A))
    crease = sum(g(SL - sj[q], 0.08) for q in range(1, 3)) * ventral
    c = np.repeat(path, segs, axis=0)
    outn = (P - c) / np.linalg.norm(P - c, axis=1, keepdims=True)
    rel = A - SL * 1.4
    hump3 = np.abs(np.cos(1.5 * rel)) ** 0.5
    RR = np.repeat(r, segs)
    P = P + outn * (0.05 * ck.fbm(P * 1.6, SEED + 110 + i) - 0.07 * crease + 0.12 * RR * (hump3 - 0.6) +
                    0.03 * np.sin(SL * 9.0 + A * 2.0) * ventral)[:, None]
    tipc = path[-1] + tan[-1] * r[-1] * 0.5
    P, T, _C = loft([P[k * segs:(k + 1) * segs] for k in range(K)], cap_end=tipc, centres=list(path))
    skin = rig.chain([f"digit{i}_{s}" for s in range(3)], j)
    A = np.concatenate([A, [0.0]])
    SL = np.concatenate([SL, [sl[-1]]])
    vent = ck.smoothstep(0.2, -0.7, np.cos(A))
    crs = np.concatenate([crease, [0.0]])
    h3 = np.concatenate([hump3, [1.0]])
    col, foam = water_color(P, SL, A - SL * 1.4, 0.4, SEED + 120 + i,
                            crest=0.5 * h3 * ck.smoothstep(0.3, 0.9, np.sin(SL * 3.0 + A)),
                            groove=np.clip(0.8 * crs + 0.7 * (1 - h3) ** 2, 0, 1))
    col = ck.mix(col, PAL["storm_slate"] * 1.1, (0.35 * vent * (1 - crs))[:, None])
    ck.finish(mesh, P, T, "water", col, skin, wet=1.0, cavity=np.clip(0.15 + 0.85 * crs, 0, 1))
    # crust plates, one over each phalanx and a short one over the knuckle, overlapping toward the tip
    spans = [(sj[0] - 0.35, sj[1] + 0.12), (sj[1] - 0.1, sj[2] + 0.1), (sj[2] - 0.08, sj[3] - 0.1)]
    for q, (s0, s1) in enumerate(spans):
        qs = np.linspace(s0, s1, 7)
        pp = np.column_stack([np.interp(qs, sl, path[:, n]) for n in range(3)])
        dd = np.column_stack([np.interp(qs, sl, dorsal[:, n]) for n in range(3)])
        ss = np.column_stack([np.interp(qs, sl, side[:, n]) for n in range(3)])
        rr = np.interp(qs, sl, r) * np.linspace(1.04, 0.92, 7)
        thick = 0.09 + 0.03 * girth
        tops = crust_plate(mesh, pp, dd, ss, rr, 1.75 - 0.1 * q, thick, skin, rng, na=10)
        for k in (2, 4) if q < 2 else (3,):  # spurs along the keel, leaning toward the tip
            tn = pp[min(k + 1, 6)] - pp[k]
            tn /= np.linalg.norm(tn)
            Ps, Ts = nail(tops[k] - dd[k] * 0.05, dd[k] + tn * 0.9, (0.22 + 0.1 * girth) * (1.0 - 0.2 * q),
                          0.07 + 0.03 * girth, tn, 0.5)
            worn = np.array([0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 1.0])[:, None]  # pale toward the point
            colsp = ck.mix(PAL["lacquer_black"], PAL["overcast_slate"] * 1.1, worn)
            ck.finish(mesh, Ps, Ts, "crust", colsp, skin, wet=0.4, cavity=0.2, flat=True)
        for k in rng.choice(np.arange(1, 6), size=int(rng.integers(1, 3)), replace=False):
            off = (rng.normal(0, 0.06, 3) + ss[k] * rng.uniform(-0.25, 0.25)) * rr[k] * 2.0
            barnacle(mesh, tops[k] + off, dd[k], rng.uniform(0.06, 0.12), rng, skin)
    # the claw: crust, hooked back under toward the palm, its point gouged into the stone
    dvec = np.array([math.sin(splay), 0.0, math.cos(splay)])
    base = path[-1] - tan[-1] * r[-1] * 0.5
    nc = 8
    cp = catmull([base, base + np.array([0, -0.38, 0]) + dvec * 0.2, base + np.array([0, -0.7, 0]) + dvec * 0.02,
                  base + np.array([0, -0.8, 0]) - dvec * 0.38], nc)
    cr = np.linspace(0.8, 0.04, nc) * r[-1] * 1.55
    ct = tangents(cp)
    cs = np.cross(ct, side0)
    cs /= np.linalg.norm(cs, axis=1, keepdims=True)
    rings = []
    for k in range(nc):
        e2 = np.cross(cs[k], ct[k])
        ang = np.array([0.0, 1.0, 2.0, 3.14, 4.28, 5.28])
        prof = np.array([1.0, 0.8, 0.6, 0.5, 0.6, 0.8])  # a keeled, flattened claw section
        rings.append(cp[k] + cr[k] * (np.outer(np.cos(ang) * prof * 1.2, cs[k]) +
                                      np.outer(np.sin(ang) * prof, e2)))
    Pc, Tc, _cc = loft(rings, cap_end=cp[-1] + ct[-1] * 0.08, centres=list(cp))
    t = np.concatenate([np.repeat(np.linspace(0, 1, nc), 6), [1.0]])
    colc = ck.mix(PAL["lacquer_black"], PAL["storm_slate"] * 1.2, ck.smoothstep(0.2, 0.7, t)[:, None])
    colc = ck.mix(colc, PAL["bone"] * 0.62, ck.smoothstep(0.65, 1.0, t)[:, None])
    ck.finish(mesh, Pc, Tc, "crust", colc, rig.rigid(f"digit{i}_2"), wet=np.clip(0.9 - 0.6 * t, 0.2, 1),
              cavity=0.3 * (1 - t), flat=True)


# ---------------------------------------------------------------------------------------------
# Wreckage and the drowned spawn
# ---------------------------------------------------------------------------------------------
def timber_col(P, col_id, endness, rng, salt_up: float = 0.3):
    grain = noise1(col_id * 3.7 + rng.uniform(0, 50), SEED + 70) * 0.5 + 0.5
    col = ck.mix(PAL["timber_weathered"] * 0.28, PAL["timber_weathered"] * 0.46, grain[:, None])
    salt = ck.smoothstep(0.15, 0.45, ck.fbm(P * 3.0, int(rng.integers(0, 10000))))
    col = ck.mix(col, PAL["bone"] * 0.6, (salt_up * salt)[:, None])
    slime = ck.smoothstep(0.1, 0.4, ck.fbm(P * 1.3, int(rng.integers(0, 10000))))
    col = ck.mix(col, PAL["foliage_shadow"] * 0.9, (0.35 * slime)[:, None])
    return ck.mix(col, PAL["bone"] * 0.62, (0.85 * endness)[:, None]), grain


def spar(mesh: ck.Mesh, a, b, r0: float, r1: float, bone, rng, bands=(), splinter_a: bool = True,
         splinter_b: bool = True, sides: int = 8) -> None:
    """A squared-off (octagonal) spar from a to b, iron-banded, splintered at its broken ends."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    ax = (b - a) / np.linalg.norm(b - a)
    e1, e2 = basis(ax)
    n = 7
    rings = []
    ang = np.arange(sides) * 2 * math.pi / sides + math.pi / sides
    for k in range(n):
        f = k / (n - 1)
        rr = (r0 + (r1 - r0) * f) * (1.0 + rng.normal(0, 0.03, sides))
        c = a + (b - a) * f
        rings.append(c + rr[:, None] * (np.outer(np.cos(ang), e1) + np.outer(np.sin(ang), e2)))
    pre = splinter_rings(a, -ax, rings[0], rng)[::-1] if splinter_a else []
    post = splinter_rings(b, ax, rings[-1], rng) if splinter_b else []
    allr = pre + rings + post
    P, T, _c = loft(allr, cap_start=a - ax * (0.05 if splinter_a else -0.0),
                    cap_end=b + ax * (0.05 if splinter_b else 0.0))
    nl = len(allr)
    endv = [1.0, 0.7] if splinter_a else []
    endv = endv + [0.0] * n + ([0.7, 1.0] if splinter_b else [])
    endv[len(pre)] = max(endv[len(pre)], 0.35 if splinter_a else 0.0)
    endv[len(pre) + n - 1] = max(endv[len(pre) + n - 1], 0.35 if splinter_b else 0.0)
    endness = np.concatenate([np.repeat(endv, sides), [1.0 if splinter_a else 0.0, 1.0 if splinter_b else 0.0]])
    col_id = np.concatenate([np.tile(np.arange(sides), nl), [0, 0]])
    col, grain = timber_col(P, col_id, endness, rng)
    ck.finish(mesh, P, T, "wreck", col, bone, wet=np.clip(0.85 - 0.6 * endness, 0.15, 1.0),
              cavity=0.2 + 0.3 * (1 - grain) * (1 - endness), flat=True)
    for f in bands:  # iron bands, rust-bled
        c = a + (b - a) * f
        rr = (r0 + (r1 - r0) * f) * 1.1
        rings = [c + ax * dz + rr * (np.outer(np.cos(ang), e1) + np.outer(np.sin(ang), e2)) for dz in (-0.08, 0.08)]
        Pb, Tb, _cb = loft(rings, centres=[c - ax * 0.08, c + ax * 0.08])
        colb = ck.mix(PAL["volcanic_stone"] * 0.75, PAL["laterite"] * 0.6,
                      ck.smoothstep(-0.2, 0.3, ck.fbm(Pb * 6.0, SEED + 77))[:, None])
        ck.finish(mesh, Pb, Tb, "wreck", colb, bone, wet=0.4, cavity=0.35, flat=True)


def plank(mesh: ck.Mesh, c, along, across, ln: float, bone, rng) -> None:
    """A hull plank, broken off at both ends."""
    along = along / np.linalg.norm(along)
    across = across - along * float(across @ along)
    across /= np.linalg.norm(across)
    nrm = np.cross(along, across)
    hw, ht = 0.22, 0.08
    rings = []
    for z in np.linspace(-ln / 2, ln / 2, 4):
        ch = rng.uniform(0.008, 0.02)
        sag = 0.04 * (2 * z / ln) ** 2
        loop = [(ht, hw - ch), (ht - ch, hw), (-ht, hw), (-ht, -hw), (ht - ch, -hw), (ht, -hw + ch)]
        rings.append(np.array([c + along * z + nrm * (rv - sag) + across * wv for rv, wv in loop]))
    pre = splinter_rings(c - along * ln / 2, -along, rings[0], rng, 0.7, (0.5, 0.95))[::-1]
    post = splinter_rings(c + along * ln / 2, along, rings[-1], rng, 0.7, (0.5, 0.95))
    allr = pre + rings + post
    P, T, _c = loft(allr, cap_start=c - along * (ln / 2 + 0.03), cap_end=c + along * (ln / 2 + 0.03))
    endness = np.concatenate([np.repeat([1.0, 0.7, 0.2, 0.0, 0.0, 0.2, 0.7, 1.0], 6), [1.0, 1.0]])
    col_id = np.concatenate([np.tile(np.arange(6), len(allr)), [0, 0]])
    col, _grain = timber_col(P, col_id, endness, rng, salt_up=0.4)
    ck.finish(mesh, P, T, "wreck", col, bone, wet=np.clip(0.7 - 0.5 * endness, 0.1, 1), cavity=0.25, flat=True)
    for off in (-0.08, 0.08):  # nail heads
        for z in (-ln * 0.3, ln * 0.3):
            sp = c + along * z + nrm * (ht + 0.01) + across * off
            Pn, Tn = nail(sp - nrm * 0.02, nrm, 0.05, 0.025, along, 0.0)
            ck.finish(mesh, Pn, Tn, "wreck", PAL["laterite"] * 0.5, bone, wet=0.3, cavity=0.3, flat=True)


def rope(mesh: ck.Mesh, path: np.ndarray, r: float, bone) -> None:
    """Hemp rope, its lay showing as twisted bands."""
    segs = 5
    P, T = ck.tube(path, r, segs, cap_start=True, cap_end=True)
    K = len(path)
    ln = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
    a = np.concatenate([np.tile(np.arange(segs) * 2 * math.pi / segs, K), [0.0, 0.0]])
    fl = np.concatenate([np.repeat(ln, segs), [0.0, ln[-1]]])
    lay = 0.5 + 0.5 * np.sin(3.0 * a + fl / r * 1.2)
    col = ck.mix(PAL["timber_weathered"] * 0.35, PAL["saltgrass"] * 0.42, lay[:, None])
    ck.finish(mesh, P, T, "wreck", col, bone, wet=0.9, cavity=0.3 * (1 - lay))


def chain(mesh: ck.Mesh, path: np.ndarray, bone, link: float = 0.6) -> None:
    """Iron chain along a path: links turning a quarter each, rust over black iron."""
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
    n = int(s[-1] / (link * 0.78))
    for k in range(n):
        sk = (k + 0.5) * s[-1] / n
        c = np.array([np.interp(sk, s, path[:, i]) for i in range(3)])
        t = np.array([np.interp(sk, s, np.gradient(path, axis=0)[:, i]) for i in range(3)])
        t /= np.linalg.norm(t)
        e1, e2 = basis(t)
        if k % 2:
            e1, e2 = e2, e1
        # a stadium-shaped centre line, a four-sided section
        loop = []
        for q in range(6):
            th = q * 2 * math.pi / 6
            loop.append(c + t * (link * 0.5 * math.cos(th)) + e1 * (link * 0.3 * math.sin(th)))
        loop = np.array(loop)
        tt = tangents(np.vstack([loop[-1:], loop, loop[:1]]))[1:-1]
        rings = []
        wr = link * 0.09
        for q in range(6):
            side = np.cross(tt[q], e2)
            rings.append(loop[q] + wr * np.array([side, e2, -side, -e2]))
        P = np.vstack(rings)
        T = []
        for q in range(6):
            q1 = (q + 1) % 6
            for m in range(4):
                m1 = (m + 1) % 4
                a, b, cc, d = q * 4 + m, q * 4 + m1, q1 * 4 + m, q1 * 4 + m1
                T += [(a, cc, b), (b, cc, d)]
        T = np.asarray(T, dtype=np.int64)
        cen = np.repeat(loop, 4, axis=0)
        T = orient(P, T, cen)
        colr = ck.mix(PAL["volcanic_stone"] * 0.6, PAL["laterite"] * 0.55, 0.35 + 0.4 * ((k * 7919) % 5) / 5)
        ck.finish(mesh, P, T, "wreck", colr, bone, wet=0.6, cavity=0.3, flat=True)


def lantern(mesh: ck.Mesh, top, bone) -> None:
    """A drowned deck lantern: a hexagonal case of tarnished brass, its glass clouded, its lamp long out."""
    up = np.array([0.0, 1.0, 0.0])
    R = ck.rot_z(18.0) @ ck.rot_x(-12.0)
    a = np.arange(6) * math.pi / 3

    def hexring(y, r):
        return np.array([top + R @ np.array([r * math.cos(t), y, r * math.sin(t)]) for t in a])

    rings = [hexring(-0.08, 0.04), hexring(-0.16, 0.2), hexring(-0.22, 0.24), hexring(-0.27, 0.2),
             hexring(-0.62, 0.2), hexring(-0.66, 0.25), hexring(-0.72, 0.25), hexring(-0.75, 0.12)]
    P, T, _c = loft(rings, cap_start=top + R @ np.array([0, -0.02, 0]), cap_end=top + R @ np.array([0, -0.77, 0]))
    row = np.concatenate([np.repeat(np.arange(len(rings)), 6), [0, len(rings) - 1]])
    glass = (row == 4) | (row == 3)
    metal = ck.mix(PAL["brass"] * 0.45, PAL["bronze_patina"] * 0.6, 0.55)
    col = np.where(glass[:, None], (PAL["salt_glass"] * 0.32)[None], metal[None])
    ck.finish(mesh, P, T, "wreck", col, bone, wet=0.8, cavity=0.25, flat=True)
    for t in a:  # the case's corner posts
        p0 = top + R @ np.array([0.21 * math.cos(t), -0.25, 0.21 * math.sin(t)])
        Pp, Tp = nail(p0, R @ -up, 0.42, 0.018, R @ up, 0.0)
        ck.finish(mesh, Pp, Tp, "wreck", metal * 0.8, bone, wet=0.6, cavity=0.2, flat=True)


def wheel(mesh: ck.Mesh, c, axis, ref, bone, rng) -> None:
    """Half a ship's wheel: hub, a broken rim, turned spokes with handles past the rim (two snapped short)."""
    axis = axis / np.linalg.norm(axis)
    e1 = ref - axis * float(ref @ axis)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(axis, e1)
    rr = 0.78
    # the rim: a squared section, broken off at both ends of its arc
    th = np.linspace(-0.35, 3.75, 16)
    rings = []
    for t in th:
        p = c + rr * (math.cos(t) * e1 + math.sin(t) * e2)
        radial = math.cos(t) * e1 + math.sin(t) * e2
        rings.append(np.array([p + radial * 0.06 + axis * 0.05, p - radial * 0.06 + axis * 0.05,
                               p - radial * 0.06 - axis * 0.05, p + radial * 0.06 - axis * 0.05]))
    P, T, _cc = loft(rings, cap_start=rings[0].mean(0), cap_end=rings[-1].mean(0),
                     centres=[r.mean(0) for r in rings])
    col_id = np.concatenate([np.tile(np.arange(4), len(rings)), [0, 0]])
    endness = np.concatenate([np.repeat([1.0] + [0.0] * 14 + [1.0], 4), [1.0, 1.0]])
    col, _g = timber_col(P, col_id, endness, rng, salt_up=0.5)
    ck.finish(mesh, P, T, "wreck", col, bone, wet=0.7, cavity=0.2, flat=True)
    # the hub and its iron boss
    hub = [c + axis * dz + 0.15 * (np.outer(np.cos(np.arange(8) * math.pi / 4), e1) +
                                   np.outer(np.sin(np.arange(8) * math.pi / 4), e2)) for dz in (-0.14, 0.14)]
    Ph, Th, _ch = loft(hub, cap_start=c - axis * 0.14, cap_end=c + axis * 0.2)
    ck.finish(mesh, Ph, Th, "wreck", PAL["volcanic_stone"] * 0.7, bone, wet=0.5, cavity=0.3, flat=True)
    for k in range(8):
        t = k * math.pi / 4 + 0.2
        radial = math.cos(t) * e1 + math.sin(t) * e2
        on_rim = -0.35 <= (t if t < 4.5 else t - 2 * math.pi) <= 3.75
        ln = (rr + 0.32) if on_rim else rng.uniform(0.3, 0.55)
        sp = c + radial * ln * np.linspace(0.15 / ln, 1.0, 6)[:, None]
        rad = np.array([0.045, 0.05, 0.04, 0.045, 0.06, 0.035]) if on_rim else np.full(6, 0.045)
        Ps, Ts = ck.tube(sp, rad, 5)
        endness = np.zeros(len(Ps)) if on_rim else np.concatenate([np.zeros(len(Ps) - 6), np.ones(6)])
        cols, _g2 = timber_col(Ps, np.arange(len(Ps)) % 5, endness, rng, salt_up=0.5)
        ck.finish(mesh, Ps, Ts, "wreck", cols, bone, wet=0.7, cavity=0.2, flat=True)


def wreckage(mesh: ck.Mesh, rig: ck.Rig) -> None:
    rng = np.random.default_rng(SEED + 200)
    # mast A: driven through the top of the arch, its long end broken off, its short end iron-banded under a cap
    sa = float(s_of_u(0.24))
    ca = frame(sa)[0][0]
    da = np.array([1.0, 0.42, 0.22])
    da /= np.linalg.norm(da)
    bone_a = rig.rigid(arm_bone(0.24))
    spar(mesh, ca - da * 2.9, ca + da * 4.0, 0.42, 0.32, bone_a, rng, bands=(0.07, 0.14, 0.62), splinter_a=False)
    stub = ca - da * 2.9
    capc = stub - da * 0.12
    e1, e2 = basis(da)
    Pc, Tc = ck.lathe([(0.0, 0.22), (0.52, 0.22), (0.55, 0.0), (0.52, -0.22), (0.0, -0.22)], 8)
    Rm = np.column_stack([e1, da, e2])
    Pc = Pc @ Rm.T + capc
    Tc = orient(Pc, Tc, capc)
    ck.finish(mesh, Pc, Tc, "wreck", ck.mix(PAL["timber_weathered"] * 0.3, PAL["foliage_shadow"], 0.3), bone_a,
              wet=0.8, cavity=0.3, flat=True)
    # the chain hangs from the stub's cap and drapes down over the arm
    s_low = float(s_of_u(0.36))
    p_low, out_low, _b = surface(s_low, math.pi + 0.35, 0.25)
    mid = 0.5 * (stub + p_low) + np.array([0.0, -1.6, 0.0])
    chain(mesh, ck.bezier([stub - da * 0.1, mid, p_low], 40), bone_a)
    # mast B with its yard: through the arm lower down, its yard lashed across it, the lantern hanging from the yard
    sb = float(s_of_u(0.5))
    cb = frame(sb)[0][0]
    db = np.array([-1.0, 0.55, -0.25])
    db /= np.linalg.norm(db)
    bone_b = rig.rigid(arm_bone(0.5))
    spar(mesh, cb - db * 2.4, cb + db * 3.8, 0.36, 0.28, bone_b, rng, bands=(0.18, 0.7))
    yc = cb + db * 2.9
    yd = np.array([0.15, 0.25, 1.0])
    yd = yd - db * float(yd @ db)
    yd /= np.linalg.norm(yd)
    spar(mesh, yc - yd * 2.2 + db * 0.32, yc + yd * 1.9 + db * 0.32, 0.2, 0.15, bone_b, rng, sides=6)
    # rope lashing at the crossing and a loose end hanging
    e1, e2 = basis(db)
    lash = np.array([yc + db * (0.12 + 0.05 * k / 18) + 0.3 * (math.cos(k * 1.1) * e1 + math.sin(k * 1.1) * e2)
                     for k in range(19)])
    rope(mesh, lash, 0.045, bone_b)
    lt = yc + yd * 1.25 + db * 0.25
    hang = np.array([lt + np.array([0.02 * math.sin(k), -0.13 * k, 0.03 * k]) for k in range(7)])
    rope(mesh, hang, 0.03, bone_b)
    lantern(mesh, hang[-1], bone_b)
    loose = ck.bezier([yc - yd * 1.3 + db * 0.25, yc - yd * 1.4 + np.array([0, -1.2, 0.3]),
                       yc - yd * 1.1 + np.array([0.2, -2.1, 0.1])], 9)
    rope(mesh, loose, 0.035, bone_b)
    # half a ship's wheel, sunk in the -X flank where the battle camera sees it
    sw = float(s_of_u(0.53))
    pw, ow, bw = surface(sw, math.pi + 0.25, 0.05)
    tw = frame(sw)[1][0]
    wheel(mesh, pw, ow + tw * 0.35, tw, rig.rigid(bw), rng)
    # hull planks fused into the flank near the wrist, and two more by the upper spawn body
    for u, ph, rot, ln in ((0.76, 0.35, 0.4, 2.6), (0.73, 0.75, 1.2, 1.8), (0.18, math.pi - 0.2, -0.3, 2.4)):
        s = float(s_of_u(u))
        p, o, b = surface(s, ph, 0.02)
        t = frame(s)[1][0]
        along = t * math.cos(rot) + np.cross(o, t) * math.sin(rot)
        plank(mesh, p, along + o * 0.35, np.cross(o, along), ln, rig.rigid(b), rng)
    # rope wound round the wrist, a turn and a half, sunk into the water here and there
    sr = S_WRIST - 1.6
    pts = []
    for k in range(28):
        f = k / 27
        s = sr - 0.9 * f
        ph = 1.2 + 3.0 * math.pi * f
        p, o, _b = surface(s, ph, 0.04 * math.sin(f * 17.0) + 0.05)
        pts.append(p)
    rope(mesh, np.array(pts), 0.07, rig.rigid("arm4"))


def spawn_shell(mesh: ck.Mesh, rig: ck.Rig, k: int) -> None:
    """A drowned spawn body, half swallowed: a segmented carapace (seven overlapping tergites, a keel, pleural
    spines), a blunt head shield with dead milky eyes and hooked mandibles, legs curled against the water."""
    u, phi, ln, wd, ht, turn = SHELLS[k]
    rng = np.random.default_rng(SEED + 300 + k)
    s = float(s_of_u(u))
    pc, up, bname = surface(s, phi, -0.2 * ht)
    t = frame(s)[1][0]
    fwd = t - up * float(t @ up)
    fwd /= np.linalg.norm(fwd)
    a = math.radians(turn)
    fwd = fwd * math.cos(a) + np.cross(up, fwd) * math.sin(a)
    side = np.cross(up, fwd)
    bone = rig.rigid(bname)
    nseg = 7
    xs = np.linspace(-0.5 * ln, 0.42 * ln, nseg + 1)
    na = 10
    th = np.arange(na) * 2 * math.pi / na
    rings, info = [], []

    def env(x):
        f = (x + 0.5 * ln) / ln
        return (np.clip(1.0 - (2 * f - 1.1) ** 2, 0.02, 1.0)) ** 0.45

    for q in range(nseg):
        x0, x1 = xs[q], xs[q + 1]
        for xf, sc, lipv in ((0.0, 1.08, 1.0), (0.45, 1.0, 0.0), (0.92, 0.9, 0.0)):
            x = x0 + (x1 - x0) * xf
            e = float(env(x)) * sc
            yv = np.where(np.sin(th) > 0, ht * np.sin(th), 0.3 * ht * np.sin(th))
            keel = 0.07 * ht * g(np.cos(th), 0.2) * (np.sin(th) > 0)
            pleura = 0.12 * wd * g(np.sin(th) - 0.05, 0.25) * np.sign(np.cos(th))
            loc = np.column_stack([np.cos(th) * 0.5 * wd * e + pleura * e, (yv + keel) * e, np.full(na, x)])
            rings.append(pc + loc[:, 0:1] * side + loc[:, 1:2] * up + loc[:, 2:3] * fwd)
            info.append(np.column_stack([np.full(na, lipv), np.full(na, xf), np.sin(th)]))
    # the head shield
    for x, sc in ((0.45 * ln, 0.75), (0.5 * ln, 0.5)):
        e = float(env(0.42 * ln)) * sc
        yv = np.where(np.sin(th) > 0, ht * np.sin(th), 0.3 * ht * np.sin(th))
        loc = np.column_stack([np.cos(th) * 0.5 * wd * e, yv * e * 0.8, np.full(na, x)])
        rings.append(pc + loc[:, 0:1] * side + loc[:, 1:2] * up + loc[:, 2:3] * fwd)
        info.append(np.column_stack([np.zeros(na), np.full(na, 0.5), np.sin(th)]))
    P, T, _c = loft(rings, cap_start=pc - fwd * 0.55 * ln, cap_end=pc + fwd * 0.53 * ln + up * 0.05)
    inf = np.vstack(info + [np.zeros((2, 3))])
    lipv, xf, sn = inf.T
    n1 = ck.fbm(P * 2.0, SEED + 310 + k)
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.2, 0.3, n1)[:, None])
    col = ck.mix(col, PAL["storm_slate"] * 1.3, (0.6 * lipv * (sn > 0))[:, None])
    keelm = g(np.abs(sn - 1.0), 0.1)
    col = ck.mix(col, PAL["storm_slate"] * 1.1, (0.45 * keelm)[:, None])
    salt = ck.smoothstep(0.25, 0.5, ck.fbm(P * 4.0, SEED + 320 + k)) * (sn > 0.3)
    col = ck.mix(col, PAL["coral_stone_weathered"] * 0.5, (0.35 * salt)[:, None])
    cav = np.clip(0.15 + 0.7 * (xf > 0.8) + 0.3 * (sn < 0), 0, 1)
    ck.finish(mesh, P, T, "crust", col, bone, wet=1.0, cavity=cav)
    # pleural spines down each side of each tergite
    for q in range(nseg):
        x = xs[q] + 0.1 * (xs[q + 1] - xs[q])
        e = float(env(x))
        for sg in (-1.0, 1.0):
            b0 = pc + side * sg * (0.5 * wd + 0.08 * wd) * e + up * 0.05 * ht + fwd * x
            Ps, Ts = nail(b0, side * sg - up * 0.5 - fwd * 0.3, 0.18 * e + 0.05, 0.035, -up, 0.4)
            ck.finish(mesh, Ps, Ts, "crust", PAL["storm_slate"] * 0.9, bone, wet=0.8, cavity=0.2, flat=True)
    # the head: dead milky eyes, hooked mandibles
    hc = pc + fwd * 0.47 * ln
    for sg in (-1.0, 1.0):
        ec = hc + side * sg * 0.18 * wd + up * 0.2 * ht
        Pe, Te = ck.ellipsoid(ec, (0.07, 0.06, 0.07), 4, 6)
        ck.finish(mesh, Pe, Te, "crust", PAL["overcast_slate"] * 0.95, bone, wet=1.0, cavity=0.1)
        Pm, Tm = nail(hc + side * sg * 0.12 * wd + fwd * 0.06 * ln, fwd - side * sg * 0.3 - up * 0.3, 0.32, 0.04,
                      -side * sg, 0.9)
        ck.finish(mesh, Pm, Tm, "crust", PAL["bone"] * 0.55, bone, wet=0.7, cavity=0.2, flat=True)
    # legs curled against the water, two joints each
    for q in (1, 3, 5):
        for sg in (-1.0, 1.0):
            x = xs[q]
            e = float(env(x))
            b0 = pc + side * sg * 0.45 * wd * e + fwd * x
            knee = b0 + side * sg * 0.35 + up * 0.22 + fwd * rng.uniform(-0.1, 0.15)
            Pa, Ta = nail(b0, knee - b0, float(np.linalg.norm(knee - b0)) * 1.05, 0.045, up, 0.2)
            ck.finish(mesh, Pa, Ta, "crust", PAL["lacquer_black"], bone, wet=0.9, cavity=0.2, flat=True)
            foot = knee + side * sg * 0.25 - up * 0.45 - fwd * 0.1
            Pb, Tb = nail(knee, foot - knee, float(np.linalg.norm(foot - knee)), 0.035, -side * sg, 0.6)
            ck.finish(mesh, Pb, Tb, "crust", PAL["storm_slate"] * 0.8, bone, wet=0.9, cavity=0.2, flat=True)


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
def build_clips() -> list[ck.Clip]:
    arm = [f"arm{i}" for i in range(NA)]
    dg = [[f"digit{i}_{s}" for s in range(3)] for i in range(len(DIGITS))]

    def curl(clip: ck.Clip, t: float, amt: float) -> None:
        for i, chain_ in enumerate(dg):
            for s, b in enumerate(chain_):
                clip.key(b, t, (amt * (14.0 + 6.0 * s), 0, 0))

    idle = ck.Clip("idle", 3.2, loop=True)  # the Grip: the water surges, the fingers squeeze in turn
    for i, b in enumerate(arm):
        idle.wave(b, amp_rot=(1.2, 0.8, 1.0), cycles=1, phase=-i * 0.8)
    for i, chain_ in enumerate(dg):
        idle.wave(chain_[1], amp_rot=(4.0, 0, 0), cycles=1, phase=i * 1.1)
    # ready: the grip eases off the stone, the fingers flex and the claws lift, the limb surging faster; a loop
    ready = ck.Clip("ready", 2.0, loop=True)
    for i, b in enumerate(arm):
        ready.wave(b, amp_rot=(1.6, 1.0, 1.3), cycles=2, phase=-i * 0.9)
    ready.wave("hand", amp_rot=(2.0, 0.0, 0.0), amp_loc=(0.0, 0.08, 0.0), base_rot=(-7.0, 0.0, 0.0),
               base_loc=(0.0, 0.35, 0.0), cycles=1)
    for i, chain_ in enumerate(dg):
        for s, b in enumerate(chain_):
            ready.wave(b, amp_rot=(5.0, 0.0, 0.0), base_rot=(-4.0 - 3.0 * s, 0.0, 0.0), cycles=2, phase=i * 0.7 + s)
    attack = ck.Clip("attack", 2.0)  # Crust Slam: the hand lifts off the wall-head and comes down
    for t, lift in ((0.0, 0.0), (0.7, 1.0), (1.0, 1.0), (1.2, -0.15), (1.5, 0.0), (2.0, 0.0)):
        attack.key("hand", t, (-38.0 * lift, 0, 0), (0, 1.4 * lift, -0.4 * lift))
        attack.key(arm[-1], t, (-10.0 * lift, 0, 0))
        curl(attack, t, -1.0 * lift)
    cast = ck.Clip("cast", 2.4)  # Undertow Pull / Close the Hand: the fingers rake back toward the sea and close
    for t, s in ((0.0, 0.0), (0.6, -0.4), (1.3, 1.0), (1.8, 1.0), (2.4, 0.0)):
        curl(cast, t, 2.2 * s)
        cast.key("hand", t, (10.0 * max(s, 0), 0, 0), (0, 0.2 * max(-s, 0), -0.5 * max(s, 0)))
        cast.key(arm[-2], t, (-4.0 * s, 0, 0))
    hit = ck.Clip("hit", 0.8)  # a shudder runs up the limb
    for t, s in ((0.0, 0.0), (0.12, 1.0), (0.3, -0.6), (0.5, 0.3), (0.8, 0.0)):  # M3-CRE-617: thrown back harder
        hit.key("hand", t, (18.0 * s, 0, 6.0 * s), (0.0, 0.25 * s, -0.3 * s))
        hit.key(arm[-2], t, (-4.0 * s, 0, -5.0 * s))
        hit.key(arm[-3], t, (-2.0 * s, 0, -2.5 * s))
    ko = ck.Clip("ko", 2.6)  # it lets go and is drawn back up into the storm
    for t, s in ((0.0, 0.0), (0.8, 0.4), (1.8, 1.0), (2.6, 1.0)):
        ko.key("root", t, (-12.0 * s, 0, 0), (0, 3.0 * s, -5.0 * s))
        curl(ko, t, -0.6 * s)
    # intro: it comes down out of the storm over the parapet, the hand open, slams its grip onto the wall-head (the
    # limb whipping after it), clenches, and settles into the Grip on idle's first frame
    intro = ck.Clip("intro", 2.8)
    for t, (ly, lz, pitch, hand_r, hand_y, open_, whip) in (
            (0.0, (11.0, -7.5, -14.0, -40.0, 0.6, -1.3, 0.0)), (0.55, (8.0, -5.0, -10.0, -44.0, 0.8, -1.4, 1.0)),
            (1.05, (2.6, -1.4, -3.0, -30.0, 0.5, -1.2, 0.6)), (1.32, (-0.25, 0.1, 0.5, 6.0, -0.1, 0.5, -0.8)),
            (1.55, (0.25, -0.05, 0.0, -3.0, 0.1, 0.9, 0.5)), (1.85, (-0.05, 0.0, 0.0, 2.0, 0.0, 0.7, -0.25)),
            (2.25, (0.0, 0.0, 0.0, 0.0, 0.0, 0.4, 0.0))):
        intro.key("root", t, (pitch, 0.0, 0.0), (0.0, ly, lz))
        intro.key("hand", t, (hand_r, 0.0, 0.0), (0.0, hand_y, 0.0))
        for i, b in enumerate(arm):
            w = (i + 1) / NA
            intro.key(b, t, (5.0 * whip * w, 0.0, 2.0 * whip * math.sin(i)))
        curl(intro, t, open_)
    for b in sorted(set(intro.keys) | set(idle.keys)):  # end on idle's first frame
        r, loc = idle.sample(b, 0.0)
        intro.key(b, 2.8, tuple(r), tuple(loc))
    # the Dark: the hand lifts off the stone and hangs over the wall-head, closing slowly
    dark_pose = {"hand": ((-22.0, 0, 0), (0, 1.1, -0.2)), arm[-1]: ((-6.0, 0, 0), (0, 0, 0))}
    phase_dark = ck.Clip("phase_dark", 2.0)
    for t, s in ((0.0, 0.0), (1.4, 1.0), (2.0, 1.0)):
        for b, (r, l) in dark_pose.items():
            phase_dark.key(b, t, tuple(np.array(r) * s), tuple(np.array(l) * s))
        curl(phase_dark, t, 0.8 * s)
    idle_dark = ck.Clip("idle_dark", 4.0, loop=True)
    for b, (r, l) in dark_pose.items():
        idle_dark.key(b, 0.0, r, l)
        idle_dark.key(b, 2.0, tuple(np.array(r) + [3.0, 0, 0]), tuple(np.array(l) + [0, -0.1, 0]))
        idle_dark.key(b, 4.0, r, l)
    for t, s in ((0.0, 0.8), (2.0, 1.2), (4.0, 0.8)):
        curl(idle_dark, t, s)
    for i, b in enumerate(arm[:-1]):
        idle_dark.wave(b, amp_rot=(1.0, 0.6, 0.8), cycles=1, phase=-i * 0.8)
    # the Breach: it lets go and draws back over the sea, the hand raised and open, gathering
    # (M3-CRB-013: 2.6 m back, not 4.5: further out it left the battle camera's frame for the whole phase)
    breach_pose = {"root": ((-10.0, 0, 0), (0, 1.0, -2.6)), "hand": ((-55.0, 0, 0), (0, 0.6, 0))}
    phase_breach = ck.Clip("phase_breach", 3.0)
    for t, s in ((0.0, 0.0), (0.6, 0.15), (2.4, 1.0), (3.0, 1.0)):
        for b, (r, l) in breach_pose.items():
            phase_breach.key(b, t, tuple(np.array(r) * s), tuple(np.array(l) * s))
        curl(phase_breach, t, -1.1 * s)
    idle_breach = ck.Clip("idle_breach", 4.0, loop=True)
    for t, s in ((0.0, 0.0), (2.0, 1.0), (4.0, 0.0)):
        for b, (r, l) in breach_pose.items():
            idle_breach.key(b, t, tuple(np.array(r) + [-3.0 * s, 0, 0]), tuple(np.array(l) + [0, 0.25 * s, 0]))
        curl(idle_breach, t, -1.1 + 0.25 * s)

    # The strikes again from each phase's pose (creatures.json `phases.<id>.clips`), so a Dark or Breach skill plays
    # from where the hand is rather than snapping back to the Grip.
    def held(pose: dict, curl_amt: float):
        def build(c: ck.Clip) -> None:
            for b, (r, l) in pose.items():
                c.key(b, 0.0, r, l)
            curl(c, 0.0, curl_amt)
        return build

    dark_full = ck.pose_of(held(dark_pose, 0.8))
    breach_full = ck.pose_of(held(breach_pose, -1.1))

    # One clip per skill (M3-CRB-013: each move reads as its own at battle distance).
    # Undertow Pull: the fingers spread and dig into the stone, then the whole hand drags back toward the sea (the
    # pull lands at 1.35 s), the claws raking, and eases back onto the Grip.
    pull = ck.Clip("undertow_pull", 2.4)
    for t, spread, dig, drag in ((0.0, 0.0, 0.0, 0.0), (0.5, 1.0, 0.0, 0.0), (0.9, 0.3, 1.0, 0.0),
                                 (1.35, 0.0, 1.0, 1.0), (1.75, 0.0, 0.8, 0.9), (2.4, 0.0, 0.0, 0.0)):
        pull.key("hand", t, (6.0 * dig + 6.0 * drag, 0.0, 0.0), (0.0, -0.05 * dig + 0.1 * spread, -1.1 * drag))
        pull.key(arm[-1], t, (-4.0 * spread + 7.0 * drag, 0.0, 0.0))
        pull.key(arm[-2], t, (5.0 * drag, 0.0, 0.0))
        curl(pull, t, -1.0 * spread + 0.6 * dig + 0.8 * drag)
    # Close the Hand (the two-turn telegraph): the hand rises off the stone toward the stair, opens, then closes
    # slowly and only half way, trembling; it has not struck yet.
    warn = ck.Clip("close_the_hand", 2.4)
    for t, lift, close in ((0.0, 0.0, 0.0), (0.6, 1.0, -0.8), (1.4, 1.0, 0.85), (1.6, 0.95, 0.7), (1.8, 1.0, 0.95),
                           (2.0, 0.95, 0.75), (2.4, 0.0, 0.0)):
        warn.key("hand", t, (-14.0 * lift, 0.0, 0.0), (0.0, 0.5 * lift, 0.2 * lift))
        warn.key(arm[-1], t, (-5.0 * lift, 0.0, 0.0))
        curl(warn, t, close)
    # The hand closes (on the stair): it rises high and wide open, then clamps down into a fist at 1.15 s, shudders and
    # lets go.
    clamp = ck.Clip("hand_closes", 2.2)
    for t, rot, y, z, c, a1 in ((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), (0.7, -30.0, 1.6, -0.2, -1.3, -10.0),
                                (0.95, -24.0, 1.3, -0.1, -1.2, -8.0), (1.15, 8.0, -0.1, 0.35, 2.4, 2.0),
                                (1.25, 5.0, 0.05, 0.3, 2.3, 1.0), (1.45, 7.0, -0.03, 0.33, 2.2, 1.5),
                                (1.65, 5.0, 0.0, 0.3, 2.2, 1.0), (2.2, 0.0, 0.0, 0.0, 0.0, 0.0)):
        clamp.key("hand", t, (rot, 0.0, 0.0), (0.0, y, z))
        clamp.key(arm[-1], t, (a1, 0.0, 0.0))
        curl(clamp, t, c)
    # Breach (gathering, from the Breach stance over the sea): it draws further back and higher, the fingers wide, the
    # limb trembling with what it holds.
    gather = ck.Clip("breach_gather", 2.6)
    for t, s, shake in ((0.0, 0.0, 0.0), (0.8, 1.0, 0.0), (1.2, 1.0, 1.0), (1.5, 1.0, -1.0), (1.8, 1.0, 1.0),
                        (2.1, 1.0, -0.6), (2.6, 0.0, 0.0)):
        gather.key("root", t, (-4.0 * s, 0.0, 1.2 * shake), (0.0, 0.6 * s, -0.8 * s))
        gather.key("hand", t, (-15.0 * s + 3.0 * shake, 0.0, 0.0), (0.0, 0.3 * s, 0.0))
        curl(gather, t, -0.5 * s)
    # Breach (the strike): it coils back, then hurls the whole limb down onto the wall-head like a breaking wave (1.2 s),
    # rebounds and draws back over the sea.
    crash = ck.Clip("breach", 2.6)
    for t, rr, y, z, h, c in ((0.0, 0.0, 0.0, 0.0, 0.0, 0.0), (0.6, -6.0, 0.8, -1.0, -20.0, -0.4),
                              (1.0, 4.0, -0.4, 1.4, 20.0, 0.2), (1.2, 10.0, -1.0, 2.6, 50.0, 0.8),
                              (1.5, 8.0, -0.8, 2.2, 40.0, 0.9), (2.6, 0.0, 0.0, 0.0, 0.0, 0.0)):
        crash.key("root", t, (rr, 0.0, 0.0), (0.0, y, z))
        crash.key("hand", t, (h, 0.0, 0.0))
        curl(crash, t, c)

    variants = [ck.in_pose(c, f"{c.name}_dark", dark_full) for c in (attack, cast, hit, pull)]
    variants += [ck.in_pose(c, f"{c.name}_breach", breach_full) for c in (attack, cast, pull)]
    variants += [ck.in_pose(gather, "breach_gather", breach_full), ck.in_pose(crash, "breach", breach_full)]
    return [idle, ready, intro, attack, cast, hit, ko, phase_dark, idle_dark, phase_breach, idle_breach, pull, warn,
            clamp] + variants


def build_mesh(rig: ck.Rig, ja: np.ndarray) -> ck.Mesh:
    mesh = ck.Mesh("undertows_reach")
    bd = forearm(mesh, rig, ja)
    loose_strands(mesh, rig, bd)
    palm(mesh, rig, bd)
    for i in range(len(DIGITS)):
        digit(mesh, rig, i)
    wreckage(mesh, rig)
    for k in range(len(SHELLS)):
        spawn_shell(mesh, rig, k)
    return mesh


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig, ja = build_rig()
    mesh = build_mesh(rig, ja)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "undertows_reach"})
    print(f"undertows_reach: {info}")


if __name__ == "__main__":
    main()
