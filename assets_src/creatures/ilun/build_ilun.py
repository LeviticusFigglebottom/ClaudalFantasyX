"""Ilun, the Net-Warden, Asha's Vowbound (M3-CRE-638): docs/kb/art/creatures/vowbound/ilun.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/ilun/build_ilun.py -- --out assets/creatures/ilun/ilun.glb

A vast spectral manta ray with a heron's crest: wings 4.6 m across, swept back to pointed tips, a blunt head with two
rolled cephalic lobes, a whip tail 2.1 m long, and three long heron plumes from the crown. His wing membranes carry a
knotted fishing net drawn in light (flat ribbons and knot beads, its own `net` slot, all `glimmer_bound`), and a
child's glass net-float in a cord net hangs from his tail tip: the keepsake, the one part of him that is not light.

**Built hovering.** The origin is the water point under him and the rest pose floats with the disc's mid-plane at
HOVER_Y (1.35 m), so the stand-in needs no `hover` and the battle's VFX anchors (fractions of battle_sandbox.json's
2.3 m height from the water) land on him: chest on the disc, head just over the crest. Every clip stays above the water.

Rig (16 bones): `root`, `body`, `wing_l0..2` and `wing_r0..2` (+x is `l`), `tail_0..4`, `crest_0`, `crest_1`, `float`.

`python3 build_ilun.py --report` prints the triangle count, per-slot counts and per-clip lows (numpy, no export).
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

SEED = 6380
PAL = {k: ck.hexrgb(v) for k, v in {
    "deep_teal_shadow": "#0E4A55", "lagoon_teal": "#1FA3A6", "salt_glass": "#BFE6E0", "sand_cloth": "#C9B48E",
}.items()}

# ---- planform (metres, Godot axes, facing +z) ------------------------------------------------
HOVER_Y = 1.35  # the disc's mid-plane above the water (the origin)
SPAN = 2.3  # half the wingspan
NOSE_Z = 0.85  # the blunt head
REAR_Z = -1.0  # the rear of the body, where the tail starts
TIP_Z = -0.75  # the wingtips, swept back (falcate)
TE_RISE = 0.62  # the trailing edge's concave sweep forward from the body to mid-wing
TIP_SWEEP = REAR_Z + TE_RISE - TIP_Z  # the trailing edge sweeps back again to meet the tip
LE_POW = 1.25  # the leading edge's sweep (slightly convex)
SHOULDER = 0.18  # the mantle: the wings rise from the body (most at mid-span) ...
DROOP = 0.55  # ... and arch down to the tips, a canopy (a heron mantling), so the near wing shows its back
TOP_CORE, BOT_CORE = 0.20, 0.11  # the body's thickness above and below the mid-plane
TOP_WING, BOT_WING = 0.028, 0.016  # the membrane's at the wing root
SKIN_MIN = 0.003  # the thinnest edge
CORE_W = 0.38  # how far out the body's hump reaches
BLUNT = 0.12  # how blunt the head's front is
ROWS, SEGS = 85, 40  # span stations (odd: one on the midline) and vertices round each section
WING_X = [0.5, 1.15, 1.75, SPAN + 0.02]  # wing_0 .. wing_2 spans, out from the midline
WING_Z = -0.15  # the wing hinges' line
BODY_SLOT_X = 0.62  # triangles wholly beyond this are the membrane slot

# ---- the net -----------------------------------------------------------------------------------
NET_X0 = 0.6  # the net starts this far out
NET_U1 = 0.95  # and ends at this fraction of the half span
NET_INSET = 0.04  # metres in from the leading and trailing edges
NET_CELL = 0.21  # the diamond mesh's side
NET_JITTER = 0.018  # hand-knotted: each knot off its lattice point by up to this
NET_SUB = 5  # points along each strand
NET_W = 0.024  # strand width
NET_OFF = 0.008  # off the membrane
KNOT_R, KNOT_H = 0.022, 0.011  # bead half-width and height

# ---- tail, crest, float ------------------------------------------------------------------------
TAIL_END_Z = -2.05
TAIL_DROP = 0.55  # the tail's tip below the mid-plane: it droops, so the float hangs low under him
TAIL_R0, TAIL_R1 = 0.06, 0.008
CORD = 0.16  # the float's cord
FLOAT_R = 0.095
NET_CORD_R = 0.0045

PARTS: dict[str, int] = {}


# ---------------------------------------------------------------------------------------------
# The surface
# ---------------------------------------------------------------------------------------------
def leading(u):
    return NOSE_Z - (NOSE_Z - TIP_Z) * np.asarray(u, dtype=np.float64) ** LE_POW


def trailing(u):
    u = np.asarray(u, dtype=np.float64)
    return REAR_Z + TE_RISE * (1.0 - (1.0 - u) ** 3) - TIP_SWEEP * u ** 4


def mid(x):
    u = np.clip(np.abs(x) / SPAN, 0.0, 1.0)
    return HOVER_Y + SHOULDER * np.sin(math.pi * u) - DROOP * u ** 2.5


def half_thickness(x, v, top: bool):
    """Above (top) or below the mid-plane at span x and chord fraction v (0 trailing .. 1 leading edge)."""
    x = np.asarray(x, dtype=np.float64)
    u = np.clip(np.abs(x) / SPAN, 0.0, 1.0)
    core = np.exp(-(x / CORE_W) ** 2)
    T = (TOP_CORE if top else BOT_CORE) * core + (TOP_WING if top else BOT_WING) * (1.0 - u) ** 1.2 + SKIN_MIN
    w = np.clip(v, 0.0, 1.0) ** 1.6 * (1.0 - BLUNT * core)
    return T * np.sin(math.pi * w) ** 0.6


def chord_v(x, z):
    u = np.clip(np.abs(x) / SPAN, 0.0, 1.0)
    le, te = leading(u), trailing(u)
    return (z - te) / np.maximum(le - te, 1e-6)


def surface_y(x, z, top: bool):
    return mid(x) + (1.0 if top else -1.0) * half_thickness(x, chord_v(x, z), top)


def surface_normal(x, z, top: bool, h: float = 1e-3):
    dx = (surface_y(x + h, z, top) - surface_y(x - h, z, top)) / (2 * h)
    dz = (surface_y(x, z + h, top) - surface_y(x, z - h, top)) / (2 * h)
    s = 1.0 if top else -1.0
    n = np.stack([-dx * s, np.full_like(dx, s), -dz * s], axis=-1)
    return n / np.linalg.norm(n, axis=-1, keepdims=True)


def orient(P: np.ndarray, T: np.ndarray, want) -> np.ndarray:
    T = np.asarray(T, dtype=np.int64).copy()
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    bad = (fn * want(P[T].mean(axis=1))).sum(axis=1) < 0
    T[bad] = T[bad][:, ::-1]
    return T


def count(name: str, mesh: ck.Mesh, before: int) -> None:
    PARTS[name] = PARTS.get(name, 0) + mesh.triangle_count - before


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def tail_path(n: int = 34) -> np.ndarray:
    y0 = float(mid(0.0))
    return ck.bezier([(0.0, y0 - 0.03, REAR_Z + 0.12), (0.0, y0 - 0.06, -1.35), (0.0, y0 - 0.25, -1.8),
                      (0.0, y0 - TAIL_DROP, TAIL_END_Z)], n)


def crown() -> np.ndarray:
    """The crest's root on the head's crown."""
    z = 0.4
    return np.array([0.0, float(surface_y(np.array(0.0), np.array(z), True)) - 0.01, z])


def tail_points() -> np.ndarray:
    path = tail_path(51)
    return path[::10]  # six points, five spans: tail_0 .. tail_4


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    rig.add("body", (0, HOVER_Y, 0), (0, HOVER_Y, 0.5), "root")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        parent = "body"
        for k in range(3):
            y0, y1 = float(mid(WING_X[k])), float(mid(min(WING_X[k + 1], SPAN)))
            rig.add(f"wing_{tag}{k}", (s * WING_X[k], y0, WING_Z), (s * WING_X[k + 1], y1, WING_Z), parent)
            parent = f"wing_{tag}{k}"
    pts = tail_points()
    parent = "body"
    for k in range(5):
        rig.add(f"tail_{k}", pts[k], pts[k + 1], parent)
        parent = f"tail_{k}"
    c = crown()
    rig.add("crest_0", c, c + (0, 0.38, -0.42), "body")
    rig.add("crest_1", c + (0, 0.38, -0.42), c + (0, 0.3, -1.2), "crest_0")
    tip = pts[-1]
    rig.add("float", tip, tip - (0, 0.3, 0), "tail_4")
    return rig


def wing_skin(rig: ck.Rig):
    """By the distance out from the midline: body, then each wing bone, blended across the span boundaries."""
    body = rig.index("body")
    wings = {s: [rig.index(f"wing_{tag}{k}") for k in range(3)] for s, tag in ((1.0, "l"), (-1.0, "r"))}
    knots = [0.0] + WING_X

    def f(P):
        n = len(P)
        J = np.zeros((n, 2), dtype=np.int64)
        W = np.zeros((n, 2))
        for i in range(n):
            x = float(P[i, 0])
            chain = [body] + wings[1.0 if x >= 0 else -1.0]
            c = min(abs(x), knots[-1] - 1e-6)
            k = int(np.searchsorted(knots, c, side="right") - 1)
            t = (c - knots[k]) / (knots[k + 1] - knots[k])
            J[i] = (chain[k], chain[k])
            W[i] = (1.0, 0.0)
            if k + 1 < len(chain) and t > 0.6:
                w = float(ck.smoothstep(0.6, 1.0, t)) * 0.5
                J[i, 1], W[i] = chain[k + 1], (1.0 - w, w)
            elif k > 0 and t < 0.4:
                w = float(ck.smoothstep(0.4, 0.0, t)) * 0.5
                J[i, 1], W[i] = chain[k - 1], (1.0 - w, w)
        return J, W

    return f


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def shell(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The disc and wings: span stations from tip to tip, each a closed airfoil section; pointed tips."""
    xs = np.linspace(-SPAN * 0.992, SPAN * 0.992, ROWS)
    a = np.arange(SEGS) * (2.0 * math.pi / SEGS)
    v = 0.5 * (np.cos(a) + 1.0)  # 1 at the leading edge (a = 0)
    side = np.sign(np.sin(a))
    X = np.repeat(xs[:, None], SEGS, axis=1)
    u = np.abs(X) / SPAN
    le, te = leading(u), trailing(u)
    Z = te + v[None] * (le - te)
    V = np.broadcast_to(v[None], X.shape)
    S = np.broadcast_to(side[None], X.shape)
    Y = mid(X) + np.where(S > 0, half_thickness(X, V, True), -half_thickness(X, V, False))
    P = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)
    T = ck.grid_tris(ROWS, SEGS, True)
    tips = [(-SPAN, float(mid(SPAN)), TIP_Z), (SPAN, float(mid(SPAN)), TIP_Z)]
    P = np.vstack([P, tips])
    last = (ROWS - 1) * SEGS
    caps = [(k, (k + 1) % SEGS, len(P) - 2) for k in range(SEGS)]
    caps += [(last + k, last + (k + 1) % SEGS, len(P) - 1) for k in range(SEGS)]
    T = np.vstack([T, np.asarray(caps, dtype=np.int64)])

    def outward(c):
        zc = 0.5 * (leading(np.abs(c[:, 0]) / SPAN) + trailing(np.abs(c[:, 0]) / SPAN))
        return np.column_stack([0.05 * c[:, 0], c[:, 1] - mid(c[:, 0]), 0.05 * (c[:, 2] - zc)])

    T = orient(P, T, outward)
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    top = P[:, 1] >= mid(P[:, 0])
    uu = np.clip(np.abs(P[:, 0]) / SPAN, 0.0, 1.0)
    vv = np.clip(chord_v(P[:, 0], P[:, 2]), 0.0, 1.0)
    edge = 1.0 - np.minimum(vv, 1.0 - vv) * 2.0  # 1 at the leading and trailing edges
    thin = ck.smoothstep(0.55, 1.0, np.maximum(edge, uu)) * ck.smoothstep(0.15, 0.4, uu)

    mott = ck.smoothstep(-0.25, 0.4, ck.fbm(P * np.array([1.6, 1.6, 1.6]), SEED))
    back = ck.mix(PAL["deep_teal_shadow"], PAL["lagoon_teal"], (0.06 + 0.22 * mott)[:, None])
    back = ck.mix(back, PAL["lagoon_teal"], (0.45 * ck.smoothstep(0.12, 0.6, uu))[:, None])
    ax = np.abs(P[:, 0])
    chevron = np.exp(-((ax - 0.62) / 0.2) ** 2 - ((P[:, 2] - 0.12 + 0.3 * (ax - 0.45)) / 0.13) ** 2)
    back = ck.mix(back, PAL["salt_glass"], (0.42 * chevron)[:, None])
    belly = ck.mix(PAL["salt_glass"], PAL["lagoon_teal"], 0.35)
    belly = ck.mix(belly, PAL["deep_teal_shadow"], (0.45 * ck.smoothstep(0.5, 0.95, np.maximum(edge, uu)))[:, None])
    col = np.where(top[:, None], back, belly)
    col = ck.mix(col, PAL["salt_glass"], (0.45 * thin * top)[:, None])  # thin margins pale: the light shows through
    glow = np.where(np.abs(P[:, 0]) < BODY_SLOT_X, 0.10, 0.08)
    wet = np.where(top, 0.55, 0.7)
    skin = wing_skin(rig)
    membrane_tri = (np.abs(P[T][:, :, 0]) > BODY_SLOT_X).all(axis=1)
    for name, mask, slot in (("body", ~membrane_tri, "body"), ("membrane", membrane_tri, "membrane")):
        Ts = T[mask]
        used = np.unique(Ts)
        remap = np.full(len(P), -1, dtype=np.int64)
        remap[used] = np.arange(len(used))
        before = mesh.triangle_count
        ck.finish(mesh, P[used], remap[Ts], slot, col[used], skin, wet=wet[used], emission=glow[used], N=N[used])
        count(name, mesh, before)


def _inside(x, z) -> np.ndarray:
    """Points (span x, chord z) on a wing's membrane where the net may lie."""
    ax = np.abs(x)
    u = ax / SPAN
    return (ax >= NET_X0) & (u <= NET_U1) & (z >= trailing(np.minimum(u, 1.0)) + NET_INSET) & \
        (z <= leading(np.minimum(u, 1.0)) - NET_INSET)


def net_strands(rng: np.random.Generator) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """The net's strands as polylines (K, 2) of (x, z), and its knots (x, z), for both wings."""
    strands: list[np.ndarray] = []
    knots: list[np.ndarray] = []
    d = NET_CELL / math.sqrt(2.0)
    n = int(math.ceil(2.6 / d)) + 2
    for s in (1.0, -1.0):
        idx = range(-n, n + 1)
        K = {}
        for i in idx:
            for j in idx:
                base = np.array([NET_X0 + (i + j) * d, 0.02 + (i - j) * d])
                K[(i, j)] = base + rng.uniform(-NET_JITTER, NET_JITTER, 2)
        for (i, j), p in K.items():
            q = np.array([[s * p[0], p[1]]])
            if _inside(q[:, 0], q[:, 1])[0]:
                knots.append(q[0])
            for nb in ((i + 1, j), (i, j + 1)):
                if nb not in K:
                    continue
                t = np.linspace(0.0, 1.0, NET_SUB)[:, None]
                seg = p[None] * (1 - t) + K[nb][None] * t
                seg[:, 0] *= s
                ok = _inside(seg[:, 0], seg[:, 1])
                run: list[np.ndarray] = []
                for k in range(NET_SUB):
                    if ok[k]:
                        run.append(seg[k])
                    else:
                        if len(run) >= 2:
                            strands.append(np.array(run))
                        run = []
                if len(run) >= 2:
                    strands.append(np.array(run))
    return strands, knots


def net(mesh: ck.Mesh, rig: ck.Rig) -> None:
    rng = np.random.default_rng(SEED)
    strands, knots = net_strands(rng)
    skin = wing_skin(rig)
    for top in (True, False):
        Ps, Ts = [], []
        base = 0
        for st in strands:
            x, z = st[:, 0], st[:, 1]
            n = surface_normal(x, z, top)
            p = np.column_stack([x, surface_y(x, z, top), z]) + n * NET_OFF
            tan = np.gradient(p, axis=0)
            side = np.cross(n, tan)
            side /= np.linalg.norm(side, axis=1, keepdims=True)
            L, R = p - side * NET_W * 0.5, p + side * NET_W * 0.5
            m = len(p)
            Ps.append(np.vstack([L, R]))
            for k in range(m - 1):
                Ts += [(base + k, base + m + k, base + k + 1), (base + k + 1, base + m + k, base + m + k + 1)]
            base += 2 * m
        for q in knots:
            x, z = np.array([q[0]]), np.array([q[1]])
            n = surface_normal(x, z, top)[0]
            c = np.array([q[0], float(surface_y(x, z, top)[0]), q[1]]) + n * NET_OFF
            e1 = np.cross(n, (0.0, 0.0, 1.0))
            e1 /= np.linalg.norm(e1)
            e2 = np.cross(n, e1)
            V = [c + e1 * KNOT_R, c + e2 * KNOT_R, c - e1 * KNOT_R, c - e2 * KNOT_R, c + n * KNOT_H, c - n * KNOT_H * 0.3]
            Ps.append(np.array(V))
            for k in range(4):
                Ts += [(base + k, base + (k + 1) % 4, base + 4), (base + (k + 1) % 4, base + k, base + 5)]
            base += 6
        P = np.vstack(Ps)
        T = np.asarray(Ts, dtype=np.int64)
        up = 1.0 if top else -1.0
        T = orient(P, T, lambda c, up=up: np.column_stack([np.zeros(len(c)), np.full(len(c), up), np.zeros(len(c))]))
        before = mesh.triangle_count
        ck.finish(mesh, P, T, "net", PAL["salt_glass"], skin, wet=0.3, emission=1.0, flat=False)
        count("net", mesh, before)


def crest(mesh: ck.Mesh, rig: ck.Rig) -> None:
    c = crown()
    plumes = [  # (x splay, rise, length back, droop at the tip, root radius)
        (0.0, 0.42, 1.25, 0.12, 0.026), (0.07, 0.36, 1.12, 0.16, 0.022), (-0.07, 0.36, 1.12, 0.16, 0.022),
        (0.05, 0.16, 0.42, 0.05, 0.014), (-0.05, 0.16, 0.42, 0.05, 0.014),
    ]
    pts = [c, c + (0, 0.38, -0.42), c + (0, 0.3, -1.2)]
    bones = rig.chain(["crest_0", "crest_1"], pts)
    for sx, rise, back, droop, r0 in plumes:
        path = ck.bezier([c + (sx * 0.2, 0.0, 0.0), c + (sx * 0.5, rise * 0.75, -back * 0.15),
                          c + (sx * 1.2, rise, -back * 0.55), c + (sx * 2.0, rise - droop, -back)], 22)
        t = np.linspace(0.0, 1.0, len(path))
        P, T = ck.tube(path, r0 * (1.0 - t) ** 0.8 + 0.003, 6, cap_start=True, cap_end=True, up_hint=(1.0, 0.0, 0.0),
                       squash=0.4)
        k = np.clip(np.einsum("ij,j->i", P - c, (0.0, 0.0, -1.0)) / back, 0.0, 1.0)
        col = ck.mix(PAL["deep_teal_shadow"], PAL["salt_glass"], ck.smoothstep(0.0, 0.35, k)[:, None])
        before = mesh.triangle_count
        ck.finish(mesh, P, T, "crest", col, bones, wet=0.3, emission=0.35 + 0.25 * ck.smoothstep(0.6, 1.0, k))
        count("crest", mesh, before)


def head(mesh: ck.Mesh, rig: ck.Rig) -> None:
    body = rig.rigid("body")
    for s in (1.0, -1.0):
        x = 0.4
        z = float(leading(np.array(x / SPAN))) - 0.035
        y = float(mid(np.array(x))) + 0.02
        Pe, Te = ck.ellipsoid((s * x, y, z), (0.045, 0.04, 0.045), 6, 10)
        before = mesh.triangle_count
        ck.finish(mesh, Pe, Te, "eye", PAL["deep_teal_shadow"], body, wet=1.0, emission=0.55)
        count("eyes", mesh, before)
        # a rolled cephalic lobe at the head's front corner, curled down and in: a scroll, not a horn
        x0 = 0.3
        le = float(leading(np.array(x0 / SPAN)))
        m = float(mid(np.array(x0)))
        path = ck.bezier([(s * x0, m - 0.01, le - 0.08), (s * (x0 + 0.01), m - 0.02, le + 0.08),
                          (s * (x0 - 0.03), m - 0.1, le + 0.15), (s * (x0 - 0.06), m - 0.15, le + 0.07)], 14)
        t = np.linspace(0.0, 1.0, len(path))
        P, T = ck.tube(path, 0.05 * (1.0 - t) + 0.014, 8, cap_start=True, cap_end=True, up_hint=(1.0, 0.0, 0.0),
                       squash=0.55)
        col = ck.mix(PAL["deep_teal_shadow"], PAL["lagoon_teal"], 0.3)
        before = mesh.triangle_count
        ck.finish(mesh, P, T, "body", col, body, wet=0.6, emission=0.10)
        count("lobes", mesh, before)


def tail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    path = tail_path()
    t = np.linspace(0.0, 1.0, len(path))
    P, T = ck.tube(path, TAIL_R0 * (1.0 - t) ** 1.1 + TAIL_R1, 8, cap_start=True, cap_end=True, squash=0.75)
    k = np.clip((REAR_Z - P[:, 2]) / (REAR_Z - TAIL_END_Z), 0.0, 1.0)
    col = ck.mix(PAL["deep_teal_shadow"], PAL["lagoon_teal"], (0.2 + 0.5 * k)[:, None])
    before = mesh.triangle_count
    ck.finish(mesh, P, T, "body", col, rig.chain([f"tail_{i}" for i in range(5)], tail_points()), wet=0.6,
              emission=0.10)
    count("tail", mesh, before)


def keepsake(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The child's glass net-float on its cord at the tail tip."""
    tip = tail_points()[-1]
    fb = rig.rigid("float")
    c = tip - np.array([0.0, CORD + FLOAT_R, 0.0])
    before = mesh.triangle_count
    Pk, Tk = ck.ellipsoid(tip + (0.0, -0.005, 0.0), (0.016, 0.022, 0.03), 4, 8)  # the cord's wrap on the tail
    ck.finish(mesh, Pk, Tk, "cord", PAL["sand_cloth"], rig.rigid("tail_4"), wet=0.5)
    path = np.array([tip + (0.0, -0.01 - CORD * f, 0.0) for f in np.linspace(0.0, 1.0, 6)])
    P, T = ck.tube(path, 0.005, 5, cap_start=False, cap_end=True, up_hint=(0.0, 0.0, 1.0))
    ck.finish(mesh, P, T, "cord", PAL["sand_cloth"], fb, wet=0.5)
    Pc, Tc = ck.ellipsoid(c + (0.0, FLOAT_R * 0.97, 0.0), (0.022, 0.012, 0.022), 4, 8)  # the collar
    ck.finish(mesh, Pc, Tc, "cord", PAL["sand_cloth"], fb, wet=0.5)
    count("cord", mesh, before)
    before = mesh.triangle_count
    Pg, Tg = ck.ellipsoid(c, (FLOAT_R, FLOAT_R, FLOAT_R), 10, 16)
    ck.finish(mesh, Pg, Tg, "glass", PAL["salt_glass"], fb, wet=1.0)
    count("glass", mesh, before)
    before = mesh.triangle_count
    r = FLOAT_R + 0.004
    th = np.linspace(0.0, math.pi, 14)
    for k in range(6):  # meridians from the collar to the bottom
        ph = k * math.pi / 3.0
        path = c + np.column_stack([r * np.sin(th) * math.cos(ph), r * np.cos(th), r * np.sin(th) * math.sin(ph)])
        P, T = ck.tube(path, NET_CORD_R, 4, cap_start=False, cap_end=False, up_hint=(0.0, 0.0, 1.0))
        ck.finish(mesh, P, T, "cord", PAL["sand_cloth"], fb, wet=0.5)
    for lat in (0.0, 0.8):  # the equator and a ring above it
        ph = np.linspace(0.0, 2.0 * math.pi, 25)
        rr = r * math.cos(lat)
        path = c + np.column_stack([rr * np.cos(ph), np.full(len(ph), r * math.sin(lat)), rr * np.sin(ph)])
        P, T = ck.tube(path, NET_CORD_R, 4, cap_start=False, cap_end=False, up_hint=(0.0, 1.0, 0.0))
        ck.finish(mesh, P, T, "cord", PAL["sand_cloth"], fb, wet=0.5)
    count("cord", mesh, before)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    PARTS.clear()
    mesh = ck.Mesh("ilun")
    shell(mesh, rig)
    net(mesh, rig)
    head(mesh, rig)
    crest(mesh, rig)
    tail(mesh, rig)
    keepsake(mesh, rig)
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
HIT_PEAK = 0.12
DEFEND_SEC = 1.2
KO_SEC = 1.8
VICTORY_SEC = 2.2
RISE_SEC = 2.6
DISMISS_SEC = 1.0
SPECIAL_SEC = 2.4
SPECIAL_CONTACT = 1.45
RELEASE_SEC = 3.3  # M3-CRE-647: the held form's release (Ch20), its KO
RELEASE_AWAY = (0.0, 1.5, -0.45)  # where the release carries him (metres: up, and back away from the party)
FLOAT_LAG = 0.15  # the float swings this far behind the tail's motion
FLOAT_HANG = 0.85  # and counter-turns this much of it (it hangs, not quite plumb)
HANG_BONES = ("root", "body", "tail_0", "tail_1", "tail_2", "tail_3", "tail_4")


def wings(c: ck.Clip, t: float, left, right=None, sweep=(0.0, 0.0)) -> None:
    """Each side's three flap angles (degrees up, about the body's length), and a forward sweep of wing_0 (+ forward)."""
    right = left if right is None else right
    for k in range(3):
        c.key(f"wing_l{k}", t, (0, -sweep[0] if k == 0 else 0.0, left[k]))
        c.key(f"wing_r{k}", t, (0, sweep[1] if k == 0 else 0.0, -right[k]))


def crest_keys(c: ck.Clip, t: float, lift: float) -> None:
    """+ lifts the plumes (about x, the tips going up), - lays them flat."""
    c.key("crest_0", t, (lift, 0, 0))
    c.key("crest_1", t, (lift * 0.6, 0, 0))


def tail_keys(c: ck.Clip, t: float, ry: float = 0.0, rx: float = 0.0) -> None:
    """ry swings the tail sideways; + rx lifts its end."""
    for k in range(5):
        c.key(f"tail_{k}", t, (rx * (0.6 + 0.15 * k), ry * (0.5 + 0.25 * k), 0))


def hang_float(c: ck.Clip) -> ck.Clip:
    """Keys the float so it hangs: it counter-turns the pitch and roll its parents give it, FLOAT_LAG behind."""
    frames = max(int(round(c.length * ck.FPS)), 1)
    for f in range(frames + 1):
        t = min(f / ck.FPS, c.length)
        s = t - FLOAT_LAG
        s = s % c.length if c.loop else max(s, 0.0)
        rx = sum(float(c.sample(b, s)[0][0]) for b in HANG_BONES)
        rz = sum(float(c.sample(b, s)[0][2]) for b in HANG_BONES)
        c.key("float", t, (-FLOAT_HANG * rx, 0, -FLOAT_HANG * rz))
    return c


def build_idle() -> ck.Clip:
    c = ck.Clip("idle", IDLE_SEC, loop=True)  # a slow undulation, hovering in place
    for k, amp in enumerate((8.0, 10.0, 13.0)):
        c.wave(f"wing_l{k}", amp_rot=(0, 0, amp), cycles=1, phase=-0.75 * k)
        c.wave(f"wing_r{k}", amp_rot=(0, 0, -amp), cycles=1, phase=-0.75 * k)
    c.wave("body", amp_rot=(1.5, 0, 0), amp_loc=(0, 0.04, 0), cycles=1, phase=math.pi)
    for k in range(5):
        c.wave(f"tail_{k}", amp_rot=(1.5, 3.0 + 1.5 * k, 0), cycles=1, phase=-0.8 * k - 0.6)
    c.wave("crest_0", amp_rot=(3.0, 0, 0), cycles=1, phase=-1.4)
    c.wave("crest_1", amp_rot=(4.0, 0, 0), cycles=1, phase=-2.0)
    return c


def build_ready() -> ck.Clip:
    c = ck.Clip("ready", READY_SEC)  # he gathers: wings high, a slow down-stroke, back to rest
    for t, ly, rx, w, cr in ((0.0, 0.0, 0.0, (0, 0, 0), 0.0), (0.5, 0.08, -4.0, (20.0, 12.0, 8.0), 14.0),
                             (1.0, 0.02, 2.0, (-7.0, -5.0, -3.0), 8.0), (READY_SEC, 0.0, 0.0, (0, 0, 0), 0.0)):
        c.key("body", t, (rx, 0, 0), (0, ly, 0))
        wings(c, t, w)
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=-rx * 0.5)
    return c


def build_attack() -> ck.Clip:
    c = ck.Clip("attack", ATTACK_SEC)  # the brine lash: he banks, lifts his left wing and sweeps it forward and down
    for t, rx, ry, rz, ly, wl, wr, sw, cr in (
            (0.0, 0, 0, 0, 0, (0, 0, 0), (0, 0, 0), 0.0, 0.0),
            (0.32, -6.0, -6.0, 16.0, 0.1, (28.0, 18.0, 12.0), (-4.0, -4.0, -2.0), -8.0, 12.0),
            (0.42, -5.0, -5.0, 14.0, 0.1, (30.0, 20.0, 14.0), (-4.0, -4.0, -3.0), -10.0, 12.0),
            (ATTACK_CONTACT, 6.0, 12.0, -6.0, -0.04, (-7.0, -6.0, -4.0), (6.0, 4.0, 2.0), 22.0, -4.0),
            (0.78, 3.0, 6.0, -3.0, -0.02, (-3.0, -3.0, -2.0), (3.0, 2.0, 1.0), 10.0, 0.0),
            (ATTACK_SEC, 0, 0, 0, 0, (0, 0, 0), (0, 0, 0), 0.0, 0.0)):
        c.key("body", t, (rx, ry, rz), (0, ly, 0))
        wings(c, t, wl, wr, sweep=(sw, 0.0))
        crest_keys(c, t, cr)
        tail_keys(c, t, ry=-ry * 0.8, rx=rx * 0.4)
    return c


def build_cast() -> ck.Clip:
    c = ck.Clip("cast", CAST_SEC)  # the tidal ward: the wings spread and curl forward round his front, a shield
    for t, rx, ly, w, sw, cr in ((0.0, 0, 0, (0, 0, 0), 0.0, 0.0),
                                 (0.4, -8.0, 0.12, (18.0, 8.0, 4.0), 6.0, 16.0),
                                 (CAST_CONTACT, -10.0, 0.15, (10.0, -12.0, -20.0), 24.0, 18.0),
                                 (1.15, -9.0, 0.14, (9.0, -12.0, -20.0), 22.0, 16.0),
                                 (CAST_SEC, 0, 0, (0, 0, 0), 0.0, 0.0)):
        c.key("body", t, (rx, 0, 0), (0, ly, 0))
        wings(c, t, w, sweep=(sw, sw))
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=-rx * 0.6)
    return c


def build_hit(name: str = "hit", side: float = 1.0, amp: float = 1.0) -> ck.Clip:
    """Pushed back and pitched nose up, wings flinching up, crest snapped back, rolled a little to `side`.
    The kit's mirrored hit_b would flip the wings' flinch down, so hit_b is authored: the roll to the other side,
    heavier (the kit's HIT_B amp)."""
    c = ck.Clip(name, HIT_SEC)
    near, far = (12.0, 10.0, 8.0), (15.0, 12.0, 9.0)
    for t, s in ((0.0, 0.0), (HIT_PEAK, amp), (0.3, -0.25 * amp), (HIT_SEC, 0.0)):
        c.key("body", t, (-11.0 * s, 0, 4.0 * s * side), (0, 0.04 * s, -0.08 * s))
        lw, rw = (near, far) if side > 0 else (far, near)
        wings(c, t, tuple(v * s for v in lw), tuple(v * s for v in rw))
        crest_keys(c, t, -10.0 * s)
        tail_keys(c, t, ry=4.0 * s * side, rx=6.0 * s)
    return c


def build_defend() -> ck.Clip:
    c = ck.Clip("defend", DEFEND_SEC)  # the wings fold forward over his front and hold, then open
    for t, rx, ly, w, sw, cr in ((0.0, 0, 0, (0, 0, 0), 0.0, 0.0),
                                 (0.3, -4.0, -0.06, (6.0, -16.0, -24.0), 26.0, -6.0),
                                 (0.85, -4.0, -0.06, (6.0, -16.0, -24.0), 26.0, -6.0),
                                 (DEFEND_SEC, 0, 0, (0, 0, 0), 0.0, 0.0)):
        c.key("body", t, (rx, 0, 0), (0, ly, 0))
        wings(c, t, w, sweep=(sw, sw))
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=-rx * 0.6)
    return c


def build_ko() -> ck.Clip:
    c = ck.Clip("ko", KO_SEC)  # the fall: a flinch, then he tips back, folds his wings up and back, and settles
    for t, rx, ly, w, sw, cr, tl in ((0.0, 0, 0, (0, 0, 0), 0.0, 0.0, 0.0),
                                     (0.2, -8.0, 0.03, (10.0, 8.0, 6.0), 0.0, -8.0, 3.0),
                                     (1.0, -20.0, -0.08, (30.0, 26.0, 18.0), -14.0, -14.0, 12.0),
                                     (1.45, -24.0, -0.12, (36.0, 30.0, 22.0), -18.0, -16.0, 16.0),
                                     (KO_SEC, -24.0, -0.12, (36.0, 30.0, 22.0), -18.0, -16.0, 16.0)):
        c.key("root", t, (0, 0, 0), (0, ly, 0))
        c.key("body", t, (rx, 0, 0))
        wings(c, t, w, sweep=(sw, sw))
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=tl)
    return c


def build_victory() -> ck.Clip:
    c = ck.Clip("victory", VICTORY_SEC)  # he rises with the wings high and the crest up, one slow full stroke
    for t, rx, ly, w, cr in ((0.0, 0, 0, (0, 0, 0), 0.0), (0.8, -6.0, 0.25, (24.0, 14.0, 10.0), 18.0),
                             (1.45, 2.0, 0.2, (-10.0, -8.0, -5.0), 14.0), (VICTORY_SEC, 0, 0, (0, 0, 0), 0.0)):
        c.key("body", t, (rx, 0, 0), (0, ly, 0))
        wings(c, t, w)
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=-rx * 0.6)
    return c


FOLDED = (68.0, 40.0, 26.0)  # the wings closed up over his back like a shell (rise's start, dismiss's end)


def build_rise() -> ck.Clip:
    c = ck.Clip("rise", RISE_SEC)  # the unfurling, in place (the stage lifts him out of the water)
    for t, rx, w, sw, cr in ((0.0, -14.0, FOLDED, -10.0, -14.0), (0.5, -12.0, FOLDED, -10.0, -14.0),
                             (1.4, -4.0, (22.0, 12.0, 8.0), 0.0, 14.0), (2.0, 2.0, (-7.0, -5.0, -3.0), 0.0, 8.0),
                             (RISE_SEC, 0, (0, 0, 0), 0.0, 0.0)):
        c.key("body", t, (rx, 0, 0))
        wings(c, t, w, sweep=(sw, sw))
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=-rx * 0.5)
    return c


def build_dismiss() -> ck.Clip:
    c = ck.Clip("dismiss", DISMISS_SEC)  # the folding: wings close over his back, crest down, nose dips; ends folded
    for t, rx, w, sw, cr in ((0.0, 0, (0, 0, 0), 0.0, 0.0), (0.35, -4.0, (14.0, 8.0, 6.0), 0.0, 6.0),
                             (0.8, 10.0, FOLDED, -10.0, -14.0), (DISMISS_SEC, 12.0, FOLDED, -10.0, -14.0)):
        c.key("body", t, (rx, 0, 0))
        wings(c, t, w, sweep=(sw, sw))
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=-rx * 0.3)
    return c


def build_special() -> ck.Clip:
    c = ck.Clip("special", SPECIAL_SEC)  # Floodnet: wings flung wide and high, a held breath, the great sweep down
    for t, rx, ly, w, sw, cr in ((0.0, 0, 0, (0, 0, 0), 0.0, 0.0),
                                 (0.9, -8.0, 0.3, (34.0, 18.0, 12.0), -6.0, 20.0),
                                 (1.15, -9.0, 0.32, (36.0, 20.0, 13.0), -6.0, 20.0),
                                 (SPECIAL_CONTACT, 6.0, 0.0, (-17.0, -10.0, -5.0), 8.0, 4.0),
                                 (1.8, 5.0, 0.0, (-15.0, -9.0, -5.0), 6.0, 4.0),
                                 (SPECIAL_SEC, 0, 0, (0, 0, 0), 0.0, 0.0)):
        c.key("body", t, (rx, 0, 0), (0, ly, 0))
        wings(c, t, w, sweep=(sw, sw))
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=-rx * 0.6)
    return c


def build_release() -> ck.Clip:
    """M3-CRE-647, the held form's KO (vowbound.md, the final fight: the first release, gentle). He opens one last
    time, wings wide and the crest raised, hovers there a breath, then one slow stroke carries him up and back,
    away from the party, level and unhurried: at peace, not fallen."""
    c = ck.Clip("release", RELEASE_SEC)
    lx, ly, lz = RELEASE_AWAY
    for t, up, back, rx, w, cr, tl in ((0.0, 0.0, 0.0, 0.0, (0, 0, 0), 0.0, 0.0),
                                       (0.7, 0.08, 0.0, -5.0, (20.0, 12.0, 8.0), 14.0, -2.0),
                                       (1.3, 0.2, 0.0, -7.0, (14.0, 9.0, 6.0), 24.0, -4.0),
                                       (1.85, 0.24, 0.02, -7.0, (15.0, 10.0, 7.0), 24.0, -4.0),
                                       (2.5, 0.75, 0.4, -9.0, (-6.0, -4.0, -2.0), 16.0, -6.0),
                                       (RELEASE_SEC, 1.0, 1.0, -6.0, (12.0, 7.0, 4.0), 16.0, -5.0)):
        c.key("root", t, (0, 0, 0), (lx * back, ly * up, lz * back))
        c.key("body", t, (rx, 0, 0))
        wings(c, t, w)
        crest_keys(c, t, cr)
        tail_keys(c, t, rx=tl)
    return c


def build_clips() -> list[ck.Clip]:
    clips = [build_idle(), build_ready(), build_attack(), build_cast(), build_hit(),
             build_hit("hit_b", -1.0, ck.HIT_B["amp"]), build_defend(), build_ko(),
             build_victory(), build_rise(), build_dismiss(), build_special(), build_release()]
    return [hang_float(c) for c in clips]


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
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "ilun"})
    print(f"ilun: {info}")


if __name__ == "__main__":
    main()
