"""Nhoa, the Rootlight, Asha's Ice Vowbound (M3-CRE-642): docs/kb/art/creatures/vowbound/nhoa.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/nhoa/build_nhoa.py -- --out assets/creatures/nhoa/nhoa.glb

A tall, slight Kirru-like figure made of motes held in her shape, like silt hanging in deep still water: a heron's long
S-neck carrying a small sleek otter-like head, two crowns of knuckled mangrove root for antlers, long arms with
webbed long-fingered hands, and a robe-like lower body that thins into hanging strands of motes instead of legs. A
carved spiral name-shell hangs on a cord at her throat: the keepsake, the one solid object on her, never lit.

**Motes are geometry, not particles.** Bound light is steady (palette.json `glimmer_bound`: no flicker, no drift, no
shed motes), so every mote is a small flattened bead (a triangular bipyramid, 6 triangles, 2-4 cm) skinned to her
bones: scattered (seeded `default_rng`) through a shell 4-8 cm deep over a dark `abyss_navy` inner body, densest on
the core and thinning toward the hem and the limbs, and strung down the hanging strands. They move only with her.

**Nothing frozen** (ADR 0015): no crystals, frost or icicles. Her cold is the colour of the light (`salt_glass` motes
lit `glimmer_bound` over the dark) and her stillness.

**Built hovering.** The origin is the water point under her and the rest pose floats with the strands' lowest ends
0.15 m above the water, so the stand-in needs no `hover`. Every clip stays above the water.

Rig (28 bones): `root`, `spine_0..2`, `neck_0..3`, `head`, `antler_l0`, `antler_l1` and the right crown (+x is `l`),
`upper_l`, `fore_l`, `hand_l` and the right arm, and three strand chains `strand_l0..2` (front-left), `strand_r0..2`
(front-right), `strand_b0..2` (back), hanging from the robe's hem.

`python3 build_nhoa.py --report` prints the triangle count, per-slot counts and per-clip lows (numpy, no export).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402
import grounding  # noqa: E402

SEED = 6420
PAL = {k: ck.hexrgb(v) for k, v in {
    "abyss_navy": "#061A2B", "salt_glass": "#BFE6E0", "timber_weathered": "#7E6A55", "bone": "#E6DAC0",
    "deep_teal_shadow": "#0E4A55", "tattoo_ink": "#24323A", "sand_cloth": "#C9B48E",
}.items()}

# ---- the skeleton's rest joints (metres, Godot axes, facing +z; the water at y 0) ---------------
SPINE = np.array([(0.0, 0.95, -0.01), (0.0, 1.30, 0.0), (0.0, 1.56, 0.01), (0.0, 1.72, 0.0)])
NECK = np.array([(0.0, 1.70, 0.02), (0.0, 1.95, 0.17), (0.0, 2.18, 0.13), (0.0, 2.35, 0.03), (0.0, 2.45, 0.07)])
HEAD_TIP = np.array([0.0, 2.52, 0.32])
HEAD_C = np.array([0.0, 2.50, 0.15])  # the skull's centre: the head at 2.5 m
HEAD_R = (0.078, 0.078, 0.15)
EYE = np.array([0.058, 2.538, 0.21])
CROWN = np.array([0.045, 2.56, 0.09])  # where each crown of root grows from the skull
ANTLER = np.array([(0.045, 2.56, 0.09), (0.15, 2.86, 0.03), (0.21, 3.16, -0.06)])
ARM = np.array([(0.165, 1.68, 0.0), (0.33, 1.28, -0.03), (0.42, 0.95, 0.1), (0.45, 0.72, 0.18)])  # shoulder .. tip
HEM_Y = 0.75  # the robe's hem, where it thins into strands
STRAND_Y = (HEM_Y, 0.55, 0.35, 0.15)  # the strand chains' joints
STRAND_LOW = 0.15  # the strands' lowest ends over the water
CHAINS = {"l": 60.0, "r": -60.0, "b": 180.0}  # each strand chain's bearing round her (degrees from +z toward +x)
CHAIN_R = 0.22

# torso and robe sections: (y, half width x, half depth z), top to bottom
TORSO = [(1.80, 0.0, 0.0), (1.79, 0.055, 0.05), (1.75, 0.12, 0.085), (1.70, 0.17, 0.1), (1.63, 0.18, 0.11),
         (1.52, 0.16, 0.115), (1.40, 0.13, 0.1), (1.28, 0.115, 0.09), (1.16, 0.135, 0.11), (1.04, 0.165, 0.14),
         (0.92, 0.2, 0.175), (0.83, 0.235, 0.21)]
HEM_R = (0.255, 0.235)
N_STRANDS = 18

# ---- the motes -----------------------------------------------------------------------------------
MOTE_SHELL = {"torso": 0.06, "neck": 0.035, "head": 0.025, "arm": 0.04, "hand": 0.02}  # the shell's depth per part
MOTE_COUNT = {"torso": 620, "neck": 130, "head": 70, "arm": 135, "hand": 40}  # arm and hand counts are per side
MOTE_R = {"torso": (0.012, 0.02), "neck": (0.01, 0.016), "head": (0.007, 0.011), "arm": (0.01, 0.016),
          "hand": (0.007, 0.011)}
MOTE_FLAT = (0.5, 0.3)  # a bead's pole heights (out, in) as fractions of its radius: flattened
MOTE_GLOW = (0.4, 1.0)  # the emission mask per bead: the swarm has depth
STRAND_STEP = 0.024  # beads along a hanging strand
TRAIL_LEN = (0.2, 0.28)  # the strands each hand trails
SHELL_CLEAR = 0.075  # no mote over the name-shell or its cord
EYE_CLEAR = 0.04

# ---- the name-shell -------------------------------------------------------------------------------
SHELL_LEN = 0.09
SHELL_TURNS = 3.0
CORD_S = 0.2  # where the cord rings the neck (a fraction along it)

PARTS: dict[str, int] = {}
BONES: list[str] = []


def count(name: str, mesh: ck.Mesh, before: int) -> None:
    PARTS[name] = PARTS.get(name, 0) + mesh.triangle_count - before


def orient(P: np.ndarray, T: np.ndarray, centres: np.ndarray) -> np.ndarray:
    """Turns each triangle to face away from its `centres` row (a point inside the part under it)."""
    T = np.asarray(T, dtype=np.int64).copy()
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    bad = (fn * (P[T].mean(axis=1) - centres)).sum(axis=1) < 0
    T[bad] = T[bad][:, ::-1]
    return T


def spline(points, n: int) -> np.ndarray:
    """n points on a Catmull-Rom curve through `points` (it passes through every one)."""
    p = np.asarray(points, dtype=np.float64)
    p = np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
    segs = len(points) - 1
    out = []
    for i in range(n):
        u = i / (n - 1) * segs
        k = min(int(u), segs - 1)
        t = u - k
        p0, p1, p2, p3 = p[k], p[k + 1], p[k + 2], p[k + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return np.array(out)


def fixed(J: np.ndarray, W: np.ndarray):
    return lambda P: (J, W)


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def arm_points(s: float) -> np.ndarray:
    return ARM * np.array([s, 1.0, 1.0])


def antler_points(s: float) -> np.ndarray:
    return ANTLER * np.array([s, 1.0, 1.0])


def bearing(deg: float) -> np.ndarray:
    a = math.radians(deg)
    return np.array([math.sin(a), 0.0, math.cos(a)])


def chain_points(tag: str) -> np.ndarray:
    o = bearing(CHAINS[tag])
    return np.array([o * CHAIN_R * (1.0 - 0.1 * k) + (0.0, y, 0.0) for k, y in enumerate(STRAND_Y)])


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    parent = "root"
    for k in range(3):
        rig.add(f"spine_{k}", SPINE[k], SPINE[k + 1], parent)
        parent = f"spine_{k}"
    for k in range(4):
        rig.add(f"neck_{k}", NECK[k], NECK[k + 1], parent)
        parent = f"neck_{k}"
    rig.add("head", NECK[-1], HEAD_TIP, parent)
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        a = antler_points(s)
        rig.add(f"antler_{tag}0", a[0], a[1], "head")
        rig.add(f"antler_{tag}1", a[1], a[2], f"antler_{tag}0")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        p = arm_points(s)
        rig.add(f"upper_{tag}", p[0], p[1], "spine_2")
        rig.add(f"fore_{tag}", p[1], p[2], f"upper_{tag}")
        rig.add(f"hand_{tag}", p[2], p[3], f"fore_{tag}")
    for tag in CHAINS:
        pts = chain_points(tag)
        parent = "spine_0"
        for k in range(3):
            rig.add(f"strand_{tag}{k}", pts[k], pts[k + 1], parent)
            parent = f"strand_{tag}{k}"
    BONES[:] = [b.name for b in rig.bones]
    return rig


def chain_pair(theta_deg: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """For bearings (degrees), the two strand chains either side and the second's weight (linear in bearing)."""
    order = sorted(CHAINS, key=lambda t: CHAINS[t] % 360.0)
    angs = [CHAINS[t] % 360.0 for t in order]
    th = np.asarray(theta_deg, dtype=np.float64) % 360.0
    a_i = np.zeros(len(th), dtype=np.int64)
    b_i = np.zeros(len(th), dtype=np.int64)
    w = np.zeros(len(th))
    for k in range(len(order)):
        a0, a1 = angs[k], angs[(k + 1) % len(order)]
        span = (a1 - a0) % 360.0
        rel = (th - a0) % 360.0
        inside = rel < span
        a_i[inside], b_i[inside], w[inside] = k, (k + 1) % len(order), rel[inside] / span
    return np.array(order)[a_i], np.array(order)[b_i], w


def strand_skin(rig: ck.Rig, P: np.ndarray, theta_deg: np.ndarray):
    """A strand bead at bearing theta: the chain segment at its height on the two chains either side, blended by
    bearing (each bead is rigid, so the segments need no blend along the strand)."""
    a, b, w = chain_pair(theta_deg)
    seg = np.where(P[:, 1] > STRAND_Y[1], 0, np.where(P[:, 1] > STRAND_Y[2], 1, 2))
    J = np.array([(rig.index(f"strand_{a[i]}{seg[i]}"), rig.index(f"strand_{b[i]}{seg[i]}")) for i in range(len(P))])
    W = np.column_stack([1.0 - w, w])
    return J, W


def torso_skin(rig: ck.Rig):
    spine = rig.chain([f"spine_{k}" for k in range(3)], SPINE)

    def f(P):
        J, W = spine(P)
        J, W = J.copy(), W.copy()
        theta = np.degrees(np.arctan2(P[:, 0], P[:, 2]))
        a, b, wb = chain_pair(theta)
        near = np.where(wb < 0.5, a, b)
        hem = 0.6 * ck.smoothstep(0.95, HEM_Y, P[:, 1])
        for i in np.nonzero(hem > 1e-4)[0]:
            J[i] = (J[i, 0], rig.index(f"strand_{near[i]}0"))
            W[i] = (1.0 - hem[i], hem[i])
        return J, W

    return f


# ---------------------------------------------------------------------------------------------
# The inner body (dark: the deep water the light is held in)
# ---------------------------------------------------------------------------------------------
def strand_bearings() -> np.ndarray:
    rng = np.random.default_rng(SEED + 1)
    return np.degrees(2.0 * math.pi * np.arange(N_STRANDS) / N_STRANDS) + rng.uniform(-4.0, 4.0, N_STRANDS)


def hem_y(theta_deg: np.ndarray) -> np.ndarray:
    """The hem dips where each strand leaves it."""
    th = np.radians(np.asarray(theta_deg, dtype=np.float64))
    dip = np.zeros_like(th)
    for b in np.radians(strand_bearings()):
        d = np.angle(np.exp(1j * (th - b)))
        dip = np.maximum(dip, np.exp(-(d / 0.11) ** 2))
    return HEM_Y + 0.03 - 0.05 * dip


def torso_mesh() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    segs = 22
    ys = np.array([r[0] for r in TORSO])
    rows = []
    fine = np.linspace(0.0, 1.0, 24)
    yk = np.interp(fine, np.linspace(0.0, 1.0, len(ys)), ys)
    rx = np.interp(-yk, -ys, [r[1] for r in TORSO])
    rz = np.interp(-yk, -ys, [r[2] for r in TORSO])
    a = np.arange(segs) * (2.0 * math.pi / segs)
    for y, x, z in zip(yk, rx, rz):
        rows.append(np.column_stack([x * np.sin(a), np.full(segs, y), z * np.cos(a)]))
    hy = hem_y(np.degrees(a))
    rows.append(np.column_stack([HEM_R[0] * np.sin(a), hy, HEM_R[1] * np.cos(a)]))  # the hem
    rows.append(np.column_stack([0.2 * np.sin(a), np.full(segs, HEM_Y + 0.05), 0.18 * np.cos(a)]))  # inside it
    rows.append(np.column_stack([0.0 * a, np.full(segs, HEM_Y + 0.1), 0.0 * a]))
    P = np.vstack(rows)
    T = ck.grid_tris(len(rows), segs, True)
    cy = np.clip(P[:, 1], SPINE[0][1], SPINE[-1][1])
    centres = np.column_stack([np.zeros(len(P)), cy, np.zeros(len(P))])
    inner = len(P) - 2 * segs  # the rows inside the hem face down and in
    centres[inner:] = P[inner:] + (0.0, 0.1, 0.0)
    T = orient(P, T, centres[T].mean(axis=1))
    return P, T, centres


def torso(mesh: ck.Mesh, rig: ck.Rig) -> tuple[np.ndarray, np.ndarray]:
    P, T, _ = torso_mesh()
    before = mesh.triangle_count
    ck.finish(mesh, P, T, "body", PAL["abyss_navy"], torso_skin(rig), wet=0.4)
    count("body", mesh, before)
    return P, T


def neck_path(n: int = 22) -> np.ndarray:
    return spline(NECK, n)


def neck_radius(t) -> np.ndarray:
    return 0.058 - 0.022 * np.asarray(t, dtype=np.float64)


def neck(mesh: ck.Mesh, rig: ck.Rig) -> tuple[np.ndarray, np.ndarray]:
    path = neck_path()
    t = np.linspace(0.0, 1.0, len(path))
    P, T = ck.tube(path, neck_radius(t), 10, cap_start=False, cap_end=False, up_hint=(1.0, 0.0, 0.0))
    before = mesh.triangle_count
    ck.finish(mesh, P, T, "body", PAL["abyss_navy"], rig.chain([f"neck_{k}" for k in range(4)], NECK), wet=0.4)
    count("body", mesh, before)
    return P, T


def head_mesh() -> tuple[np.ndarray, np.ndarray]:
    P, T = ck.ellipsoid((0.0, 0.0, 0.0), (1.0, 1.0, 1.0), 10, 14)
    P = P[:, [0, 2, 1]] * np.array([1.0, 1.0, 1.0])  # poles on z: the long axis runs nose to nape
    T = T[:, ::-1]
    zf = np.clip(P[:, 2], 0.0, 1.0)
    taper = 1.0 - 0.38 * zf ** 2  # the muzzle narrows
    P = P * np.array(HEAD_R) * np.column_stack([taper, taper, np.ones(len(P))])
    P[:, 1] *= np.where(P[:, 1] > 0, 0.9, 1.0)  # a flat crown
    P[:, 1] -= 0.022 * zf ** 2  # the muzzle dips
    return P + HEAD_C, T


def head(mesh: ck.Mesh, rig: ck.Rig) -> tuple[np.ndarray, np.ndarray]:
    P, T = head_mesh()
    T = orient(P, T, np.tile(HEAD_C, (len(T), 1)))
    before = mesh.triangle_count
    ck.finish(mesh, P, T, "body", PAL["abyss_navy"], rig.rigid("head"), wet=0.4)
    count("body", mesh, before)
    for s in (1.0, -1.0):
        Pe, Te = ck.ellipsoid(EYE * (s, 1.0, 1.0), (0.016, 0.014, 0.017), 5, 8)
        before = mesh.triangle_count
        ck.finish(mesh, Pe, Te, "eye", PAL["deep_teal_shadow"], rig.rigid("head"), wet=1.0, emission=0.55)
        count("eye", mesh, before)
    return P, T


def arm_path(s: float, n: int = 16) -> np.ndarray:
    return spline(arm_points(s)[:3], n)


def arm(mesh: ck.Mesh, rig: ck.Rig, s: float, tag: str) -> tuple[np.ndarray, np.ndarray]:
    path = arm_path(s)
    t = np.linspace(0.0, 1.0, len(path))
    P, T = ck.tube(path, 0.048 - 0.02 * t, 8, cap_start=True, cap_end=False)
    before = mesh.triangle_count
    ck.finish(mesh, P, T, "body", PAL["abyss_navy"], rig.chain([f"upper_{tag}", f"fore_{tag}"], arm_points(s)[:3]),
              wet=0.4)
    count("body", mesh, before)
    return P, T


def hand_frame(s: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """The hand's wrist, its length axis u, its splay axis v (fingers fan along it) and its palm normal n (inward)."""
    p = arm_points(s)
    w = p[2]
    u = p[3] - p[2]
    u /= np.linalg.norm(u)
    v = np.cross((1.0, 0.0, 0.0), u)
    v /= np.linalg.norm(v)
    n = np.cross(u, v) * -s
    return w, u, v, n / np.linalg.norm(n)


FINGERS = ((-0.03, -0.2, 0.13), (-0.01, -0.07, 0.155), (0.01, 0.06, 0.16), (0.03, 0.19, 0.135))  # (v at the base,
# splay, length)


def finger_paths(s: float) -> list[np.ndarray]:
    w, u, v, n = hand_frame(s)
    base = w + u * 0.085
    out = []
    for dv, splay, length in FINGERS:
        d = u + v * splay
        d /= np.linalg.norm(d)
        p0 = base + v * dv
        out.append(ck.bezier([p0, p0 + d * length * 0.5, p0 + d * length + n * 0.025], 6))
    return out


def hand(mesh: ck.Mesh, rig: ck.Rig, s: float, tag: str) -> list[tuple[np.ndarray, np.ndarray]]:
    w, u, v, n = hand_frame(s)
    bone = rig.rigid(f"hand_{tag}")
    surfaces = []
    Pp, Tp = ck.ellipsoid((0.0, 0.0, 0.0), (0.042, 0.05, 0.016), 4, 8)  # the palm: y along u, x along v, z along n
    R = np.column_stack([v, u, n])
    Pp = Pp @ R.T + w + u * 0.05
    Tp = orient(Pp, Tp, np.tile(w + u * 0.05, (len(Tp), 1)))
    before = mesh.triangle_count
    ck.finish(mesh, Pp, Tp, "body", PAL["abyss_navy"], bone, wet=0.4)
    surfaces.append((Pp, Tp))
    paths = finger_paths(s)
    for path in paths:
        t = np.linspace(0.0, 1.0, len(path))
        P, T = ck.tube(path, 0.009 - 0.005 * t, 5, cap_start=False, cap_end=True, up_hint=tuple(n))
        ck.finish(mesh, P, T, "body", PAL["abyss_navy"], bone, wet=0.4)
        surfaces.append((P, T))
    for a, b in zip(paths, paths[1:]):  # the webs, to just past halfway along the fingers, both faces
        k = 4
        P = np.vstack([a[:k], b[:k]])
        T = np.array([(i, k + i, i + 1) for i in range(k - 1)] + [(i + 1, k + i, k + i + 1) for i in range(k - 1)])
        ck.finish(mesh, P, T, "body", PAL["abyss_navy"], bone, wet=0.4)
        ck.finish(mesh, P, ck.flip(T), "body", PAL["abyss_navy"], bone, wet=0.4)
    count("body", mesh, before)
    return surfaces


# ---------------------------------------------------------------------------------------------
# Antlers: two crowns of knuckled mangrove root
# ---------------------------------------------------------------------------------------------
def antler_tines(s: float) -> list[tuple[np.ndarray, float, float]]:
    """(path, root radius, tip radius) per tine of one crown."""
    rng = np.random.default_rng(SEED + (7 if s > 0 else 11))
    c = CROWN * (s, 1.0, 1.0)
    m = s
    main = ck.bezier([c, c + (m * 0.05, 0.14, -0.01), c + (m * 0.13, 0.38, -0.06), c + (m * 0.17, 0.62, -0.15)], 16)

    def at(t: float) -> np.ndarray:
        return main[int(round(t * (len(main) - 1)))]

    tines = [(main, 0.026, 0.006)]
    for t0, d1, d2, d3, r0 in ((0.3, (0.08, 0.03, 0.04), (0.18, 0.1, 0.06), (0.26, 0.22, 0.05), 0.016),
                               (0.55, (0.0, 0.08, 0.06), (0.0, 0.16, 0.1), (0.02, 0.25, 0.1), 0.013),
                               (0.72, (0.06, 0.05, -0.03), (0.13, 0.1, -0.07), (0.17, 0.17, -0.11), 0.012)):
        p0 = at(t0)
        tines.append((ck.bezier([p0, p0 + np.multiply(d1, (m, 1, 1)), p0 + np.multiply(d2, (m, 1, 1)),
                                 p0 + np.multiply(d3, (m, 1, 1))], 10), r0, 0.005))
    a = tines[1][0]
    p0 = a[6]
    tines.append((ck.bezier([p0, p0 + (m * 0.0, 0.06, 0.0), p0 + (m * 0.03, 0.12, -0.01)], 7), 0.009, 0.004))
    out = []
    for path, r0, r1 in tines:  # uneven, like a root: a small wander off the curve
        wob = rng.normal(0.0, 0.006, path.shape)
        wob[0] = 0.0
        out.append((path + wob, r0, r1))
    return out


def antlers(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        rng = np.random.default_rng(SEED + (13 if s > 0 else 17))
        skin = rig.chain([f"antler_{tag}0", f"antler_{tag}1"], antler_points(s))
        for path, r0, r1 in antler_tines(s):
            t = np.linspace(0.0, 1.0, len(path))
            r = r0 * (1.0 - t) + r1 * t
            for tk in np.arange(0.15, 0.95, 0.24) + rng.uniform(-0.05, 0.05, 4):  # the knuckles
                r = r * (1.0 + 0.3 * np.exp(-((t - tk) / 0.05) ** 2))
            P, T = ck.tube(path, r, 6, cap_start=True, cap_end=True)
            tip = np.clip((P[:, 1] - CROWN[1]) / (ANTLER[-1][1] - CROWN[1]), 0.0, 1.0)
            col = ck.mix(PAL["timber_weathered"], PAL["bone"], ck.smoothstep(0.45, 1.0, tip)[:, None])
            before = mesh.triangle_count
            ck.finish(mesh, P, T, "antler", col, skin, wet=0.3, cavity=0.2,
                      emission=0.25 * ck.smoothstep(0.72, 1.0, tip))
            count("antler", mesh, before)


# ---------------------------------------------------------------------------------------------
# The name-shell on its cord
# ---------------------------------------------------------------------------------------------
def cord_ring() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The cord's loop round the neck: its centre, the neck's direction there, and its front point."""
    path = neck_path(101)
    k = int(CORD_S * 100)
    c = path[k]
    d = path[k + 1] - path[k - 1]
    d /= np.linalg.norm(d)
    front = np.array([0.0, 0.0, 1.0]) - d * d[2]
    front /= np.linalg.norm(front)
    return c, d, c + front * (float(neck_radius(CORD_S)) + 0.005)


def shell_centre() -> np.ndarray:
    _, _, f = cord_ring()
    return f + (0.0, -0.035 - SHELL_LEN * 0.55, 0.025)


def name_shell(mesh: ck.Mesh, rig: ck.Rig) -> None:
    bone = rig.rigid("neck_0")
    c, d, front = cord_ring()
    e1 = np.cross(d, (1.0, 0.0, 0.0))
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(d, e1)
    r = float(neck_radius(CORD_S)) + 0.005
    a = np.linspace(0.0, 2.0 * math.pi, 21)
    loop = c + r * (np.outer(np.cos(a), e1) + np.outer(np.sin(a), e2))
    before = mesh.triangle_count
    P, T = ck.tube(loop, 0.004, 5, cap_start=False, cap_end=False)
    ck.finish(mesh, P, T, "shell", PAL["sand_cloth"], bone, wet=0.5)
    top = shell_centre() + (0.0, SHELL_LEN * 0.55, 0.0)
    drop = ck.bezier([front, front + (0.0, -0.02, 0.012), top], 5)
    P, T = ck.tube(drop, 0.0035, 5, cap_start=True, cap_end=True)
    ck.finish(mesh, P, T, "shell", PAL["sand_cloth"], bone, wet=0.5)
    count("cord", mesh, before)
    # the shell: a whorl coiling down to its apex, the aperture at the top by the cord; the carving is dark lines
    # along the whorl and across it (tattoo_ink), the rest bone
    n, segs = 30, 7
    t = np.linspace(0.0, 1.0, n)
    phi = 2.0 * math.pi * SHELL_TURNS * t
    R = 0.003 + 0.02 * t ** 1.2
    h = -SHELL_LEN * 0.8 * (1.0 - t)
    path = np.column_stack([R * np.cos(phi), h, R * np.sin(phi)])
    P, T = ck.tube(path, 0.002 + 0.016 * t ** 1.1, segs, cap_start=True, cap_end=True)
    P = P @ ck.rot_x(12.0).T + shell_centre() + (0.0, SHELL_LEN * 0.35, 0.0)
    ring = np.minimum(np.arange(len(P)) // segs, n - 1)
    around = np.arange(len(P)) % segs
    ink = np.isin(around, (1, 4)) | (ring % 6 == 3)
    ink[n * segs:] = False
    col = np.where(ink[:, None], PAL["tattoo_ink"], PAL["bone"])
    before = mesh.triangle_count
    ck.finish(mesh, P, T, "shell", col, bone, wet=0.3, cavity=np.where(ink, 0.8, 0.1))
    count("shell", mesh, before)


# ---------------------------------------------------------------------------------------------
# The motes
# ---------------------------------------------------------------------------------------------
def bead(c: np.ndarray, nrm: np.ndarray, r: float, phi: float) -> tuple[np.ndarray, np.ndarray]:
    """A flattened triangular bipyramid at c, its poles on nrm."""
    e1 = np.cross(nrm, (0.0, 1.0, 0.0) if abs(nrm[1]) < 0.9 else (1.0, 0.0, 0.0))
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(nrm, e1)
    V = [c + r * (math.cos(phi + k * 2.0 * math.pi / 3.0) * e1 + math.sin(phi + k * 2.0 * math.pi / 3.0) * e2)
         for k in range(3)]
    V += [c + nrm * r * MOTE_FLAT[0], c - nrm * r * MOTE_FLAT[1]]
    T = [(k, (k + 1) % 3, 3) for k in range(3)] + [((k + 1) % 3, k, 4) for k in range(3)]
    return np.array(V), np.array(T)


class Motes:
    """Gathers beads (centres, normals, radii, the skin of each) and adds them as one `motes` part."""

    def __init__(self) -> None:
        self.c: list[np.ndarray] = []
        self.n: list[np.ndarray] = []
        self.r: list[np.ndarray] = []
        self.J: list[np.ndarray] = []
        self.W: list[np.ndarray] = []

    def add(self, c, n, r, J, W) -> None:
        self.c.append(np.atleast_2d(c))
        self.n.append(np.atleast_2d(n))
        self.r.append(np.atleast_1d(r))
        self.J.append(np.atleast_2d(J))
        self.W.append(np.atleast_2d(W))

    def finish(self, mesh: ck.Mesh) -> int:
        rng = np.random.default_rng(SEED + 3)
        C, N, R = np.vstack(self.c), np.vstack(self.n), np.concatenate(self.r)
        J, W = np.vstack(self.J), np.vstack(self.W)
        Ps, Ts = [], []
        for i in range(len(C)):
            V, T = bead(C[i], N[i], float(R[i]), float(rng.uniform(0.0, 2.0 * math.pi)))
            Ps.append(V)
            Ts.append(T + 5 * i)
        P, T = np.vstack(Ps), np.vstack(Ts)
        T = orient(P, T, np.repeat(C, 6, axis=0))
        glow = np.repeat(rng.uniform(*MOTE_GLOW, len(C)), 5)
        before = mesh.triangle_count
        ck.finish(mesh, P, T, "motes", PAL["salt_glass"], fixed(np.repeat(J, 5, axis=0), np.repeat(W, 5, axis=0)),
                  wet=0.3, emission=glow)
        count("motes", mesh, before)
        return len(C)


def clear_of_keepsake(p: np.ndarray) -> np.ndarray:
    """False where a mote would cover the name-shell, its cord or an eye."""
    c, _, front = cord_ring()
    ok = np.linalg.norm(p - shell_centre(), axis=1) > SHELL_CLEAR
    ok &= np.linalg.norm(p - front, axis=1) > SHELL_CLEAR * 0.6
    for s in (1.0, -1.0):
        ok &= np.linalg.norm(p - EYE * (s, 1.0, 1.0), axis=1) > EYE_CLEAR
    return ok


def scatter(motes: Motes, rng: np.random.Generator, P: np.ndarray, T: np.ndarray, skin, part: str, n: int,
            density=None) -> None:
    """n beads on the surface (P, T), area-weighted (times `density` at each triangle's centre), each pushed out along
    the surface normal into the part's shell (more of them near the surface), skinned as the surface point is."""
    a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
    fn = np.cross(b - a, c - a)
    area = 0.5 * np.linalg.norm(fn, axis=1)
    w = area * (density((a + b + c) / 3.0) if density is not None else 1.0)
    w = w / w.sum()
    got = 0
    while got < n:
        k = rng.choice(len(T), size=n - got, p=w)
        u, v = rng.random(n - got), rng.random(n - got)
        flip = u + v > 1.0
        u[flip], v[flip] = 1.0 - u[flip], 1.0 - v[flip]
        base = a[k] + (b[k] - a[k]) * u[:, None] + (c[k] - a[k]) * v[:, None]
        nrm = fn[k] / np.maximum(np.linalg.norm(fn[k], axis=1, keepdims=True), 1e-12)
        depth = MOTE_SHELL[part] * rng.random(n - got) ** 1.6
        pos = base + nrm * depth[:, None]
        keep = clear_of_keepsake(pos)
        if not keep.any():
            continue
        r = rng.uniform(*MOTE_R[part], int(keep.sum()))
        J, W = skin(base[keep])
        motes.add(pos[keep], nrm[keep], r, J, W)
        got += int(keep.sum())


def strand_beads(motes: Motes, rng: np.random.Generator, rig: ck.Rig) -> None:
    """The hanging strands: beads strung from the hem down to their ends, the lowest at STRAND_LOW."""
    bear = strand_bearings()
    ends = STRAND_LOW + 0.2 * rng.random(N_STRANDS) ** 1.5
    ends[np.argmin(ends)] = STRAND_LOW
    for th, y1 in zip(bear, ends):
        o = bearing(float(th))
        top = np.array([HEM_R[0] * o[0], float(hem_y(np.array([th]))[0]) + 0.01, HEM_R[1] * o[2]]) * (0.95, 1, 0.95)
        side = np.cross((0.0, 1.0, 0.0), o)
        length = top[1] - y1
        k = int(length / STRAND_STEP)
        t = np.linspace(0.0, 1.0, k + 1)
        rr = 0.016 - 0.007 * t
        y = top[1] - t * (top[1] - (y1 + rr[-1]))
        sway = 0.012 * np.sin(math.pi * t * 1.5 + float(rng.uniform(0.0, 6.0)))
        C = np.column_stack([top[0] * (1.0 - 0.18 * t), y, top[2] * (1.0 - 0.18 * t)]) + np.outer(sway, side)
        C[1:-1] += rng.normal(0.0, 0.003, (k - 1, 3)) * (1.0, 0.3, 1.0)
        J, W = strand_skin(rig, C, np.full(len(C), th))
        motes.add(C, np.tile(o, (len(C), 1)), rr, J, W)


def hand_trails(motes: Motes, rng: np.random.Generator, rig: ck.Rig) -> None:
    """Three short strands each hand trails from the heel of the palm."""
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        w, u, v, n = hand_frame(s)
        bone = rig.index(f"hand_{tag}")
        for dv in (-0.025, 0.0, 0.025):
            top = w + u * 0.03 + v * dv - n * 0.01
            length = float(rng.uniform(*TRAIL_LEN))
            k = int(length / (STRAND_STEP * 0.85))
            t = np.linspace(0.0, 1.0, k + 1)[1:]
            C = top + np.outer(t * length, (0.0, -1.0, 0.0)) + np.outer(t * 0.03, -n)
            C += rng.normal(0.0, 0.003, C.shape)
            m = len(C)
            motes.add(C, np.tile(-n, (m, 1)), 0.011 - 0.004 * t, np.tile((bone, bone), (m, 1)), np.tile((1.0, 0.0), (m, 1)))


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    PARTS.clear()
    mesh = ck.Mesh("nhoa")
    rng = np.random.default_rng(SEED)
    motes = Motes()
    Pt, Tt = torso(mesh, rig)
    scatter(motes, rng, Pt, Tt, torso_skin(rig), "torso", MOTE_COUNT["torso"],
            density=lambda c: (0.45 + 0.55 * ck.smoothstep(HEM_Y, 1.25, c[:, 1])) * (c[:, 1] < 1.79))
    Pn, Tn = neck(mesh, rig)
    scatter(motes, rng, Pn, Tn, rig.chain([f"neck_{k}" for k in range(4)], NECK), "neck", MOTE_COUNT["neck"])
    Ph, Th = head(mesh, rig)
    head_bone = rig.index("head")
    scatter(motes, rng, Ph, Th, lambda P: (np.tile((head_bone, head_bone), (len(P), 1)), np.tile((1.0, 0.0), (len(P), 1))),
            "head", MOTE_COUNT["head"])
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        Pa, Ta = arm(mesh, rig, s, tag)
        scatter(motes, rng, Pa, Ta, rig.chain([f"upper_{tag}", f"fore_{tag}"], arm_points(s)[:3]), "arm",
                MOTE_COUNT["arm"], density=lambda c, s=s: 0.5 + 0.5 * ck.smoothstep(0.8, 1.5, c[:, 1]))
        surf = hand(mesh, rig, s, tag)
        Ph2 = np.vstack([p for p, _ in surf])
        Th2 = np.vstack([t + sum(len(p) for p, _ in surf[:i]) for i, (_, t) in enumerate(surf)])
        hb = rig.index(f"hand_{tag}")
        scatter(motes, rng, Ph2, Th2, lambda P, hb=hb: (np.tile((hb, hb), (len(P), 1)), np.tile((1.0, 0.0), (len(P), 1))),
                "hand", MOTE_COUNT["hand"])
    strand_beads(motes, rng, rig)
    hand_trails(motes, rng, rig)
    PARTS["beads"] = motes.finish(mesh)
    antlers(mesh, rig)
    name_shell(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 4.0
READY_SEC = 1.4
ATTACK_SEC = 1.2
ATTACK_CONTACT = 0.55
CAST_SEC = 1.6
CAST_CONTACT = 0.8
HIT_SEC = 0.5
HIT_PEAK = 0.1
DEFEND_SEC = 1.2
KO_SEC = 1.8
VICTORY_SEC = 2.2
RISE_SEC = 2.6
DISMISS_SEC = 1.0
SPECIAL_SEC = 2.4
SPECIAL_CONTACT = 1.45


def to_euler(R: np.ndarray) -> tuple[float, float, float]:
    """The kit's euler (R = Rz Ry Rx, fixed axes) of a rotation matrix, in degrees."""
    b = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    a = math.atan2(R[2, 1], R[2, 2])
    c = math.atan2(R[1, 0], R[0, 0])
    return math.degrees(a), math.degrees(b), math.degrees(c)


def axis_angle(axis, deg: float) -> np.ndarray:
    k = np.asarray(axis, dtype=np.float64)
    k = k / np.linalg.norm(k)
    a = math.radians(deg)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


def swing(direction, deg: float) -> tuple[float, float, float]:
    """The turn that swings a hanging bone's end `deg` toward the horizontal `direction`."""
    d = np.asarray(direction, dtype=np.float64)
    if abs(deg) < 1e-9 or np.linalg.norm(d) < 1e-9:
        return 0.0, 0.0, 0.0
    return to_euler(axis_angle(np.cross((0.0, -1.0, 0.0), d), deg))


def strands(out=(0.0, 0.0, 0.0), fwd=(0.0, 0.0, 0.0), side=(0.0, 0.0, 0.0), chain: dict | None = None) -> dict:
    """The strand chains' pose: per segment (root to end) swung `out` (away from her), `fwd` (+z) and `side` (+x),
    in degrees; `chain` adds per-chain (out, fwd, side) triples of per-segment degrees."""
    pose = {}
    for tag, th in CHAINS.items():
        o = bearing(th)
        extra = (chain or {}).get(tag, ((0, 0, 0), (0, 0, 0), (0, 0, 0)))
        for k in range(3):
            D = o * (out[k] + extra[0][k]) + np.array([0.0, 0.0, 1.0]) * (fwd[k] + extra[1][k]) \
                + np.array([1.0, 0.0, 0.0]) * (side[k] + extra[2][k])
            pose[f"strand_{tag}{k}"] = (swing(D, float(np.linalg.norm(D))), (0.0, 0.0, 0.0))
    return pose


def arms(upper=(0.0, 0.0, 0.0), fore=(0.0, 0.0, 0.0), hand=(0.0, 0.0, 0.0), right=None) -> dict:
    """Both arms: the left as given, the right mirrored (or its own triple of triples, given for the left side's
    sense, and mirrored)."""
    pose = {}
    for tag, (u, f, h) in (("l", (upper, fore, hand)), ("r", right or (upper, fore, hand))):
        m = (1.0, -1.0, -1.0) if tag == "r" else (1.0, 1.0, 1.0)
        pose[f"upper_{tag}"] = (tuple(np.multiply(u, m)), (0.0, 0.0, 0.0))
        pose[f"fore_{tag}"] = (tuple(np.multiply(f, m)), (0.0, 0.0, 0.0))
        pose[f"hand_{tag}"] = (tuple(np.multiply(h, m)), (0.0, 0.0, 0.0))
    return pose


def body(spine=(0.0, 0.0, 0.0), neck=(0.0, 0.0, 0.0, 0.0), head=0.0, twist=0.0, roll=0.0, lift=0.0, back=0.0,
         antler=0.0) -> dict:
    """The trunk: `spine` (spine_0..2 bow, + forward), `neck` (neck_0..3 bow), `head` (+ nods down), `twist` (+ turns
    her left shoulder back, about y) and `roll` (about z) spread over spine_1 and spine_2, the root's `lift` and `back`
    (metres), and `antler` (+ lifts the crowns, tips back and out)."""
    pose = {"root": ((0.0, 0.0, 0.0), (0.0, lift, -back))}
    for k in range(3):
        share = 0.0 if k == 0 else 0.5
        pose[f"spine_{k}"] = ((spine[k], twist * share, roll * share), (0.0, 0.0, 0.0))
    for k in range(4):
        pose[f"neck_{k}"] = ((neck[k], 0.0, 0.0), (0.0, 0.0, 0.0))
    pose["head"] = ((head, 0.0, 0.0), (0.0, 0.0, 0.0))
    for tag, s in (("l", 1.0), ("r", -1.0)):
        pose[f"antler_{tag}0"] = ((-antler, 0.0, -0.5 * s * antler), (0.0, 0.0, 0.0))
        pose[f"antler_{tag}1"] = ((-0.6 * antler, 0.0, 0.0), (0.0, 0.0, 0.0))
    return pose


def merge(*poses: dict) -> dict:
    out: dict = {}
    for p in poses:
        out.update(p)
    return out


def keyp(c: ck.Clip, t: float, pose: dict) -> None:
    """Keys every bone at t: as `pose` gives it, else at rest."""
    for b in BONES:
        rot, loc = pose.get(b, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
        c.key(b, t, rot, loc)


REST: dict = {}
CROSSED = arms(upper=(-55.0, -38.0, 6.0), fore=(-62.0, -30.0, 0.0), hand=(0.0, 0.0, -10.0))  # before her chest
FOLDED = merge(body(spine=(0.0, 14.0, 10.0), neck=(12.0, 16.0, 10.0, 0.0), head=-12.0, lift=-0.08), CROSSED,
               strands(out=(-10.0, -12.0, -8.0)))  # bowed and folded in (rise's start, dismiss's end)


def build_idle() -> ck.Clip:
    c = ck.Clip("idle", IDLE_SEC, loop=True)  # the strands sway in a slow current; the neck sways; the hands drift
    for tag, ph in (("l", 0.0), ("r", 2.1), ("b", 4.2)):
        for k in range(3):
            c.wave(f"strand_{tag}{k}", amp_rot=(3.0 + 1.0 * k, 0.0, 2.5 + 1.0 * k), cycles=1, phase=ph - 0.7 * k)
    c.wave("root", amp_loc=(0.0, 0.015, 0.0), cycles=1, phase=0.0)
    c.wave("spine_1", amp_rot=(1.0, 0.0, 0.8), cycles=1, phase=0.6)
    for k in range(4):
        c.wave(f"neck_{k}", amp_rot=(1.6, 0.0, 1.4), cycles=1, phase=-0.5 * k)
    c.wave("head", amp_rot=(-2.0, 0.0, -2.5), cycles=1, phase=-2.0)
    for tag, s in (("l", 1.0), ("r", -1.0)):
        ph = 0.0 if s > 0 else math.pi * 0.7
        c.wave(f"upper_{tag}", amp_rot=(4.0, 0.0, 2.0 * s), cycles=1, phase=ph)
        c.wave(f"fore_{tag}", amp_rot=(-5.0, 0.0, 0.0), cycles=1, phase=ph - 0.6)
        c.wave(f"hand_{tag}", amp_rot=(0.0, 6.0 * s, 4.0 * s), cycles=1, phase=ph - 1.2)
    return c


def build_ready() -> ck.Clip:
    c = ck.Clip("ready", READY_SEC)  # she lifts her head and spreads her hands; the strands gather in
    up = merge(body(spine=(0.0, -2.0, -2.0), neck=(-3.0, -2.0, -2.0, -2.0), head=-8.0, lift=0.04, antler=6.0),
               arms(upper=(-14.0, 0.0, 26.0), fore=(-28.0, 0.0, 6.0), hand=(0.0, 30.0, 12.0)),
               strands(out=(-14.0, -10.0, -6.0)))
    keyp(c, 0.0, REST)
    keyp(c, 0.5, up)
    keyp(c, 0.95, up)
    keyp(c, READY_SEC, REST)
    return c


def build_attack() -> ck.Clip:
    c = ck.Clip("attack", ATTACK_SEC)  # a sweeping open-handed strike with the near (left) hand, the strands trailing
    wind = merge(body(spine=(0.0, -4.0, -4.0), neck=(0.0, -4.0, -4.0, 0.0), head=-6.0, twist=24.0),
                 arms(upper=(-40.0, 70.0, 20.0), fore=(-35.0, 0.0, 0.0), hand=(0.0, 0.0, 0.0),
                      right=((-10.0, 0.0, 12.0), (-20.0, 0.0, 0.0), (0.0, 0.0, 0.0))),
                 strands(side=(-6.0, -4.0, -2.0), fwd=(-4.0, -3.0, -2.0)))
    strike = merge(body(spine=(0.0, 8.0, 6.0), neck=(4.0, 6.0, 2.0, 0.0), head=-2.0, twist=-22.0),
                   arms(upper=(-82.0, -24.0, 6.0), fore=(-6.0, 0.0, 0.0), hand=(0.0, 0.0, -8.0),
                        right=((8.0, 0.0, 14.0), (-10.0, 0.0, 0.0), (0.0, 0.0, 0.0))),
                   strands(side=(10.0, 8.0, 6.0), fwd=(4.0, 3.0, 2.0)))
    follow = merge(body(spine=(0.0, 6.0, 4.0), neck=(2.0, 4.0, 2.0, 0.0), twist=-28.0),
                   arms(upper=(-70.0, -48.0, 2.0), fore=(-12.0, 0.0, 0.0), hand=(0.0, 0.0, -6.0),
                        right=((6.0, 0.0, 12.0), (-8.0, 0.0, 0.0), (0.0, 0.0, 0.0))),
                   strands(side=(-8.0, -12.0, -14.0), fwd=(6.0, 8.0, 8.0)))
    keyp(c, 0.0, REST)
    keyp(c, 0.32, wind)
    keyp(c, ATTACK_CONTACT, strike)
    keyp(c, 0.78, follow)
    keyp(c, ATTACK_SEC, REST)
    return c


def build_cast() -> ck.Clip:
    c = ck.Clip("cast", CAST_SEC)  # the ice: both hands drawn up, then pushed forward; the strands stream forward
    drawn = merge(body(spine=(0.0, -4.0, -4.0), neck=(-2.0, -4.0, -4.0, -2.0), head=-6.0, lift=0.03),
                  arms(upper=(-38.0, -14.0, 14.0), fore=(-98.0, -10.0, 0.0), hand=(-20.0, 0.0, 0.0)),
                  strands(fwd=(-8.0, -6.0, -4.0), out=(-6.0, -4.0, -2.0)))
    pushed = merge(body(spine=(0.0, 7.0, 5.0), neck=(4.0, 4.0, 0.0, 0.0), head=-4.0, lift=0.02),
                   arms(upper=(-84.0, -10.0, 4.0), fore=(-8.0, 0.0, 0.0), hand=(-30.0, 0.0, 0.0)),
                   strands(fwd=(20.0, 16.0, 12.0), out=(6.0, 4.0, 2.0)))
    keyp(c, 0.0, REST)
    keyp(c, 0.42, drawn)
    keyp(c, CAST_CONTACT, pushed)
    keyp(c, 1.12, pushed)
    keyp(c, CAST_SEC, REST)
    return c


def hit_pose(s: float, side: float) -> dict:
    """The blow's peak: the neck snaps back, she rocks back and rolls to `side`, the strands scatter outward."""
    near, far = (6.0 + 10.0, 4.0 + 8.0)
    return merge(body(spine=(0.0, -5.0 * s, -4.0 * s), neck=(-5.0 * s, -5.0 * s, -4.0 * s, -2.0 * s), head=-3.0 * s,
                      roll=3.0 * s * side, back=0.02 * s, antler=-20.0 * s),
                 arms(upper=(-6.0 * s, 0.0, (near if side > 0 else far) * s), fore=(-12.0 * s, 0.0, 0.0),
                      right=((-6.0 * s, 0.0, (far if side > 0 else near) * s), (-12.0 * s, 0.0, 0.0), (0, 0, 0))),
                 strands(out=(16.0 * s, 12.0 * s, 10.0 * s),
                         chain={"b": ((-10.0 * s, -8.0 * s, -7.0 * s), (0, 0, 0), (0, 0, 0))}))  # the back ones less


def build_hit(name: str = "hit", side: float = 1.0, amp: float = 1.0) -> ck.Clip:
    """The hit, and hit_b authored (rolled to the other side, the kit's HIT_B amp): the kit's mirror would flip the
    arms' sideways turns without swapping them."""
    c = ck.Clip(name, HIT_SEC)
    keyp(c, 0.0, REST)
    keyp(c, HIT_PEAK, hit_pose(amp, side))
    keyp(c, 0.26, hit_pose(-0.25 * amp, side))
    keyp(c, HIT_SEC, REST)
    return c


def build_defend() -> ck.Clip:
    c = ck.Clip("defend", DEFEND_SEC)  # the arms cross before her and the strands wrap round her front
    guard = merge(body(spine=(0.0, 6.0, 6.0), neck=(4.0, 6.0, 4.0, 2.0), head=4.0, lift=0.02), CROSSED,
                  strands(fwd=(18.0, 14.0, 10.0), out=(-10.0, -10.0, -8.0), chain={"b": ((0, 0, 0), (12, 8, 6),
                                                                                       (0, 0, 0))}))
    keyp(c, 0.0, REST)
    keyp(c, 0.3, guard)
    keyp(c, 0.85, guard)
    keyp(c, DEFEND_SEC, REST)
    return c


def build_ko() -> ck.Clip:
    c = ck.Clip("ko", KO_SEC)  # she bows her neck and folds in on herself; the strands hang straight down
    down = merge(body(spine=(0.0, 18.0, 12.0), neck=(14.0, 18.0, 12.0, 0.0), head=-8.0, lift=-0.1, antler=-6.0),
                 arms(upper=(-18.0, -12.0, -4.0), fore=(-26.0, -10.0, 0.0), hand=(0.0, 0.0, -10.0)))
    keyp(c, 0.0, REST)
    keyp(c, 0.2, hit_pose(0.6, 1.0))
    keyp(c, 1.0, merge(down, body(spine=(0.0, 15.0, 10.0), neck=(12.0, 16.0, 10.0, 0.0), head=-10.0, lift=-0.08)))
    keyp(c, 1.45, down)
    keyp(c, KO_SEC, down)
    return c


def build_victory() -> ck.Clip:
    c = ck.Clip("victory", VICTORY_SEC)  # she straightens to her full height and the antlers lift
    tall = merge(body(spine=(0.0, -2.0, -2.0), neck=(-3.0, 2.0, 0.0, -2.0), head=-6.0, lift=0.06, antler=10.0),
                 arms(upper=(-8.0, 0.0, 20.0), fore=(-12.0, 0.0, 4.0), hand=(0.0, 36.0, 8.0)),
                 strands(out=(-4.0, -3.0, -2.0)))
    keyp(c, 0.0, REST)
    keyp(c, 0.8, tall)
    keyp(c, 1.6, tall)
    keyp(c, VICTORY_SEC, REST)
    return c


def build_rise() -> ck.Clip:
    c = ck.Clip("rise", RISE_SEC)  # from folded low she unfolds upward, the strands last
    keyp(c, 0.0, FOLDED)
    keyp(c, 0.45, FOLDED)
    keyp(c, 1.45, merge(body(spine=(0.0, -2.0, -2.0), neck=(-2.0, -4.0, -6.0, -4.0), head=-8.0, lift=0.02,
                             antler=-4.0),
                        arms(upper=(-10.0, 0.0, 18.0), fore=(-20.0, 0.0, 4.0), hand=(0.0, 24.0, 8.0)),
                        strands(out=(-10.0, -12.0, -8.0))))
    keyp(c, 2.15, merge(arms(upper=(-4.0, 0.0, 6.0), fore=(-8.0, 0.0, 0.0)), strands(out=(4.0, 3.0, 2.0))))
    keyp(c, RISE_SEC, REST)
    return c


def build_dismiss() -> ck.Clip:
    c = ck.Clip("dismiss", DISMISS_SEC)  # she folds back down, neck bowed; ends folded
    keyp(c, 0.0, REST)
    keyp(c, 0.3, merge(body(neck=(-2.0, -4.0, -4.0, -2.0), head=-6.0, lift=0.02),
                       arms(upper=(-6.0, 0.0, 10.0), fore=(-10.0, 0.0, 0.0))))
    keyp(c, 0.8, FOLDED)
    keyp(c, DISMISS_SEC, FOLDED)
    return c


def build_special() -> ck.Clip:
    """Farewell-Tide: she gathers, lifts her arms high, and the strands are drawn up into a column round her (the
    battle VFX's rising column takes over at the contact), then lets them down."""
    c = ck.Clip("special", SPECIAL_SEC)
    gather = merge(body(spine=(0.0, 8.0, 6.0), neck=(6.0, 8.0, 6.0, 2.0), head=6.0, lift=-0.04), CROSSED,
                   strands(out=(-10.0, -10.0, -6.0)))
    raised = merge(body(spine=(0.0, -3.0, -3.0), neck=(-3.0, -2.0, -2.0, -2.0), head=-8.0, lift=0.08, antler=-4.0),
                   arms(upper=(-150.0, 0.0, 16.0), fore=(-14.0, 0.0, -6.0), hand=(-10.0, 0.0, -10.0)),
                   strands(out=(70.0, 40.0, 20.0)))
    column = merge(body(spine=(0.0, -3.0, -4.0), neck=(-3.0, -3.0, -3.0, -3.0), head=-10.0, lift=0.1, antler=-6.0),
                   arms(upper=(-166.0, 0.0, 8.0), fore=(-8.0, 0.0, -4.0), hand=(-6.0, 0.0, -6.0)),
                   strands(out=(122.0, 38.0, 14.0)))
    keyp(c, 0.0, REST)
    keyp(c, 0.5, gather)
    keyp(c, 1.15, raised)
    keyp(c, SPECIAL_CONTACT, column)
    keyp(c, 1.85, column)
    keyp(c, SPECIAL_SEC, REST)
    return c


RELEASE_SEC = 3.4  # M3-CRE-647: the held form's release (Ch20), its KO
RELEASE_UP, RELEASE_BACK = 1.5, 0.5  # where the release carries her (metres: up, and back away from the party)


def release_open(lift: float, back: float, strand_up: float, reach: float) -> dict:
    """Opened to the light: tall, the face lifted, the arms raised and open, the strands drawn up `strand_up`."""
    return merge(body(spine=(0.0, -3.0, -3.0), neck=(-3.0, -3.0, -4.0, -3.0), head=-12.0, lift=lift, back=back,
                      antler=8.0),
                 arms(upper=(-reach, 0.0, 24.0), fore=(-12.0, 0.0, -4.0), hand=(-6.0, 28.0, 0.0)),
                 strands(out=(strand_up, 0.31 * strand_up, 0.12 * strand_up)))


def build_release() -> ck.Clip:
    """M3-CRE-647, the held form's KO (vowbound.md, the final fight: Pell turns his back and sings). She straightens
    and opens her hands, and the hanging strands of motes lift and stream upward round her, the only time her motes
    rise (her Farewell-Tide's column, made real); she holds there, face lifted, then she rises with them, up and
    back, open and unhurried."""
    c = ck.Clip("release", RELEASE_SEC)
    keyp(c, 0.0, REST)
    keyp(c, 0.6, merge(body(spine=(0.0, -2.0, -2.0), neck=(-2.0, -2.0, -3.0, -2.0), head=-8.0, lift=0.04, antler=6.0),
                       arms(upper=(-20.0, 0.0, 30.0), fore=(-20.0, 0.0, 4.0), hand=(0.0, 30.0, 10.0)),
                       strands(out=(24.0, 12.0, 6.0))))
    keyp(c, 1.3, release_open(0.1, 0.0, 92.0, 118.0))
    keyp(c, 1.9, release_open(0.12, 0.0, 100.0, 124.0))
    keyp(c, 2.6, release_open(0.12 + 0.4 * RELEASE_UP, 0.4 * RELEASE_BACK, 118.0, 130.0))
    keyp(c, RELEASE_SEC, release_open(0.12 + RELEASE_UP, RELEASE_BACK, 124.0, 132.0))
    return c


def build_clips() -> list[ck.Clip]:
    return [build_idle(), build_ready(), build_attack(), build_cast(), build_hit(),
            build_hit("hit_b", -1.0, ck.HIT_B["amp"]), build_defend(), build_ko(), build_victory(), build_rise(),
            build_dismiss(), build_special(), build_release()]


# ---------------------------------------------------------------------------------------------
# A numpy check (no Blender)
# ---------------------------------------------------------------------------------------------
def report(rig: ck.Rig, mesh: ck.Mesh, clips: list[ck.Clip]) -> None:
    rest = mesh.arrays()["pos"]
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}")
    print("parts: " + ", ".join(f"{k} {v}" for k, v in PARTS.items()))
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)}")
    poser = grounding.Poser(rig, mesh)
    for c in ck.with_variety(clips):
        lows = grounding.lowest(poser, c)
        highs, disp = [], []
        for t in grounding.frame_times(c):
            P = poser.vertices(poser.matrices(grounding.pose_at(c, poser.names, t)))
            highs.append(float(P[:, 1].max()))
            disp.append(float(np.linalg.norm(P - rest, axis=1).mean()))
        print(f"{c.name:8s} {c.length:.2f}s: y {min(lows):+.3f}..{max(highs):.3f}; peak {int(np.argmax(disp)) / ck.FPS:.2f}s")


def build() -> tuple[ck.Rig, ck.Mesh, list[ck.Clip]]:
    rig = build_rig()
    return rig, build_mesh(rig), build_clips()


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true", help="print the triangle count and the clip checks; no export")
    args = ap.parse_args(argv)
    rig, mesh, clips = build()
    if args.report or not args.out:
        report(rig, mesh, clips)
        return
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "nhoa"})
    print(f"nhoa: {info}")


if __name__ == "__main__":
    main()
