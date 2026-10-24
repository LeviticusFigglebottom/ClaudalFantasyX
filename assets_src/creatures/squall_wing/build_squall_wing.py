"""Squall wing, Ch8 the seawall (M3-CRE-06): docs/kb/art/creatures/act1/squall_wing.md.

blender --background --factory-startup --python assets_src/creatures/squall_wing/build_squall_wing.py -- \
    --out assets/creatures/squall_wing/squall_wing.glb

Undertow-spawn in the shape of a gull, as if the storm remembered the gull harrier and got it wrong: a gaunt, small
body on wings that are too long and too thin (2.0 m tip to tip), black wet membrane in place of feathers, the
trailing edge scalloped and torn into streamers. The body is a hollow lacquer shell; its tears show the held
spawn_wound light inside (the weak point). No eyes, only two lit slits; a long black beak a little open on the same
light. The talons hang ready for the dive.

It reuses the gull harrier's rig layout, bone names and wing poses (imported from its build module, which is not
edited), and its feather-blade primitive for the streamers. The origin is the hover point (sheet: hover 1.2 m).
The creature faces +z; its right side (-x) faces the battle camera once turned toward the party, so the right wing
carries the worst tears.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "common"))
sys.path.insert(0, str(_HERE.parent / "gull_harrier"))
import build_gull_harrier as gh  # noqa: E402
import creature_kit as ck  # noqa: E402

SEED = 8231
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "storm_slate": "#3E4A57", "deep_teal_shadow": "#0E4A55",
    "spawn_wound": "#3FE0C8",
}.items()}
BLACK = PAL["lacquer_black"]
SHEEN = ck.mix(PAL["lacquer_black"], PAL["storm_slate"], 0.35)  # the wet highlight band along the spars
WOUND = PAL["spawn_wound"]

# The left wing's arm chain (x > 0); the right mirrors it. Longer and thinner than the gull's, on a smaller body.
SHOULDER = (0.06, 0.215, 0.06)
ELBOW = (0.32, 0.285, 0.0)
WRIST = (0.56, 0.32, 0.07)
TIP = (1.0, 0.18, -0.16)
LEAD = (  # the leading edge, by x
    (0.03, 0.212, 0.075), SHOULDER, ELBOW, WRIST, (0.70, 0.305, 0.04), (0.86, 0.255, -0.06), TIP,
)
CHORD = ((0.03, 0.21), (0.32, 0.15), (0.56, 0.12), (0.80, 0.075), (1.0, 0.012))
HIP = (0.035, 0.12, -0.04)
ANKLE = (0.04, 0.07, -0.20)

# The body, a gaunt lofted spindle: (z, centre y, half-width, back height, belly depth).
STATIONS = (
    (-0.34, 0.190, 0.000, 0.000, 0.000),
    (-0.31, 0.190, 0.022, 0.018, 0.020),
    (-0.23, 0.188, 0.048, 0.034, 0.042),
    (-0.12, 0.185, 0.074, 0.050, 0.070),
    (0.00, 0.186, 0.084, 0.058, 0.084),
    (0.10, 0.192, 0.078, 0.058, 0.078),
    (0.18, 0.206, 0.058, 0.048, 0.056),
    (0.24, 0.226, 0.038, 0.038, 0.036),
    (0.30, 0.246, 0.036, 0.036, 0.034),
    (0.34, 0.258, 0.046, 0.046, 0.040),
    (0.38, 0.263, 0.049, 0.049, 0.042),
    (0.42, 0.262, 0.043, 0.043, 0.038),
    (0.45, 0.258, 0.032, 0.032, 0.028),
    (0.47, 0.256, 0.000, 0.000, 0.000),
)
CORE_C = (0.0, 0.186, -0.03)
CORE_R = (0.068, 0.05, 0.19)


def _lead(x):
    xs = [p[0] for p in LEAD]
    return np.column_stack([x, np.interp(x, xs, [p[1] for p in LEAD]), np.interp(x, xs, [p[2] for p in LEAD])])


def _drop_tris(T: np.ndarray, keep_v: np.ndarray) -> np.ndarray:
    return T[keep_v[T].all(axis=1)]


# ---------------------------------------------------------------------------------------------
# Rig: the gull harrier's layout and bone names (its clips' wing poses carry over), no twine
# ---------------------------------------------------------------------------------------------
def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.1, 0))
    rig.add("body", (0, 0.186, 0), (0, 0.186, 0.15), "root")
    rig.add("neck", (0, 0.215, 0.20), (0, 0.25, 0.31), "body")
    rig.add("head", (0, 0.258, 0.32), (0, 0.262, 0.44), "neck")
    rig.add("beak", (0, 0.245, 0.43), (0, 0.235, 0.62), "head")
    rig.add("tail", (0, 0.19, -0.28), (0, 0.19, -0.48), "body")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        m = np.array([s, 1.0, 1.0])
        rig.add(f"shoulder_{tag}", np.multiply(SHOULDER, m), np.multiply(ELBOW, m), "body")
        rig.add(f"elbow_{tag}", np.multiply(ELBOW, m), np.multiply(WRIST, m), f"shoulder_{tag}")
        rig.add(f"wrist_{tag}", np.multiply(WRIST, m), np.multiply(TIP, m), f"elbow_{tag}")
        rig.add(f"leg_{tag}", np.multiply(HIP, m), np.multiply(ANKLE, m), "body")
    return rig


# ---------------------------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------------------------
def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The hollow shell: a lacquer loft with ragged tears through to the lit core."""
    segs = 22
    zs = np.concatenate([np.linspace(-0.34, 0.18, 14), np.linspace(0.21, 0.47, 9)])
    cols = list(zip(*STATIONS))
    a = np.arange(segs) * (2.0 * math.pi / segs)
    s, c = np.sin(a), np.cos(a)
    rows, centre = [], []
    for z in zs:
        cy, rx, top, bot = (float(np.interp(z, cols[0], cols[k])) for k in (1, 2, 3, 4))
        ry = np.where(c >= 0.0, top, bot)
        e = 0.9
        rows.append(np.column_stack([rx * np.sign(s) * np.abs(s) ** e, cy + ry * np.sign(c) * np.abs(c) ** e,
                                     np.full(segs, z)]))
        centre.append(np.tile([0.0, cy, z], (segs, 1)))
    P = np.vstack(rows)
    C = np.vstack(centre)
    T = gh._outward(P, ck.grid_tris(len(zs), segs, True), C)
    radial = P - C
    nrm = radial / np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-9)
    # ridged like a keel and ribs showing through: the storm's idea of feathers
    rib = np.abs(np.sin(P[:, 2] * 70.0)) ** 6 * ck.smoothstep(-0.25, 0.15, P[:, 2]) * (1.0 - ck.smoothstep(0.15, 0.2, P[:, 2]))
    P = P + nrm * (0.004 * rib + ck.fbm(P * 22.0, SEED + 1) * 0.004)[:, None]
    z = P[:, 2]
    # the tears: ragged holes in the torso's flanks and belly, more on the camera side (-x)
    torso = ck.smoothstep(-0.27, -0.18, z) * (1.0 - ck.smoothstep(0.12, 0.2, z))
    flank = 1.0 - 0.5 * ck.smoothstep(0.6, 0.95, nrm[:, 1])
    tear = ck.fbm(np.column_stack([P[:, 0] * 9.0, P[:, 1] * 14.0, z * 7.0]), SEED + 2) * torso * flank
    tear = tear + 0.08 * torso * (P[:, 0] < 0.0)
    cut = 0.11
    tri_tear = tear[T].mean(axis=1)
    T = T[tri_tear < cut]
    edge = ck.smoothstep(0.04, cut, tear)
    col = ck.mix(BLACK, PAL["abyss_navy"], (0.35 * ck.smoothstep(0.0, -0.8, nrm[:, 1]))[:, None])
    col = ck.mix(col, SHEEN, (0.5 * rib)[:, None])
    col = ck.mix(col, WOUND * 0.55, (0.85 * edge)[:, None])
    J_b, J_n, J_h, J_t = (rig.index(n) for n in ("body", "neck", "head", "tail"))

    def bones(Pv):
        zz = Pv[:, 2]
        n = len(Pv)
        J = np.tile([J_b, J_b], (n, 1))
        W = np.tile([1.0, 0.0], (n, 1))
        tail = zz < -0.22
        wt = ck.smoothstep(-0.22, -0.34, zz) * 0.7
        J[tail, 1] = J_t
        W[tail] = np.column_stack([1.0 - wt, wt])[tail]
        neck = (zz >= 0.16) & (zz < 0.30)
        wn = ck.smoothstep(0.16, 0.30, zz)
        J[neck, 1] = J_n
        W[neck] = np.column_stack([1.0 - wn, wn])[neck]
        head = zz >= 0.30
        wh = ck.smoothstep(0.30, 0.36, zz)
        J[head] = (J_n, J_h)
        W[head] = np.column_stack([1.0 - wh, wh])[head]
        return J, W

    ck.finish(mesh, P, T, "shell", col, bones, wet=1.0, cavity=0.3 * rib + 0.3 * edge, emission=edge * 0.9)

    # the held light inside: what the tears show (the weak point)
    Pc, Tc = gh._ellipsoid(CORE_C, CORE_R, 8, 14)
    glow = 0.75 + 0.25 * ck.fbm(Pc * 18.0, SEED + 3)
    ck.finish(mesh, Pc, Tc, "core", ck.mix(PAL["deep_teal_shadow"], WOUND, glow[:, None]), J_b, wet=1.0,
              emission=glow)
    # two lit slits where a gull's eyes would be
    for sx in (1.0, -1.0):
        Pe, Te = gh._ellipsoid((0.0, 0.0, 0.0), (0.006, 0.0045, 0.017), 4, 8)
        Pe = ck.transform(Pe, ck.euler(0.0, sx * 14.0, -sx * 18.0), (sx * 0.044, 0.272, 0.395))
        ck.finish(mesh, Pe, Te, "core", WOUND * 0.8, J_h, emission=1.0)


def beak(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Too long and a little open: two black blades with a hook, the light in the gape."""
    ih, ij = rig.index("head"), rig.index("beak")
    s = np.linspace(0.0, 1.0, 10)
    z = 0.43 + 0.20 * s
    y = 0.268 + 0.004 * np.sin(math.pi * s) - 0.016 * s * s
    th = np.radians(np.linspace(30.0, 150.0, 4))
    rc = 0.016
    z = np.concatenate([z, z[-1] + rc * np.sin(th)])
    y = np.concatenate([y, y[-1] - rc * (1.0 - np.cos(th))])
    rad = np.concatenate([np.interp(s, (0.0, 0.4, 1.0), (0.026, 0.017, 0.010)), np.linspace(0.008, 0.002, 4)])
    P, T = gh._tube(np.column_stack([np.zeros(len(z)), y, z]), rad, 8, squash=0.55)
    edge = ck.smoothstep(0.255, 0.246, P[:, 1])
    ck.finish(mesh, P, T, "shell", ck.mix(BLACK, SHEEN, (0.6 * edge)[:, None]), ih, wet=1.0)
    s = np.linspace(0.0, 1.0, 8)
    z = 0.435 + 0.17 * s
    y = 0.245 - 0.022 * s
    P, T = gh._tube(np.column_stack([np.zeros(len(z)), y, z]), np.interp(s, (0.0, 0.7, 1.0), (0.018, 0.009, 0.002)),
                    8, squash=0.7)
    ck.finish(mesh, P, T, "shell", BLACK, ij, wet=1.0)
    # the gape's light
    Pg, Tg = gh._ellipsoid((0.0, 0.252, 0.47), (0.012, 0.008, 0.05), 4, 8)
    ck.finish(mesh, Pg, Tg, "core", WOUND * 0.7, ij, emission=0.9)


def wing(mesh: ck.Mesh, rig: ck.Rig, side: float) -> None:
    tag = "l" if side > 0 else "r"
    parts = []  # (P, T, colour, bone, wet, cavity, emission, uv, N)
    # the membrane: rows back from the leading edge, the trailing edge scalloped and torn
    NX, NV = 34, 9
    x = np.linspace(0.03, 1.0, NX)
    lead = _lead(x)
    chord = np.interp(x, [p[0] for p in CHORD], [p[1] for p in CHORD])
    sweep = 0.35 * ck.smoothstep(0.5, 1.0, x)
    back = np.column_stack([sweep, -0.12 * ck.smoothstep(0.6, 1.0, x), -np.ones(NX)])
    back /= np.linalg.norm(back, axis=1, keepdims=True)
    scallop = np.abs(np.sin(math.pi * (x - 0.03) / 0.115)) ** 0.6
    rag = 0.30 * scallop * ck.smoothstep(0.12, 0.3, x) + 0.18 * ck.fbm(np.column_stack([x * 9.0, x * 3.0, x]), SEED + 11 + int(side > 0))
    v_end = np.clip(1.0 - rag, 0.45, 1.0)
    rows = []
    vv = []
    for k in range(NV):
        v = k / (NV - 1)
        vk = v * v_end
        cup = 0.022 * np.sin(math.pi * vk) * (chord / 0.2)
        rows.append(lead + back * (vk * chord)[:, None] + np.column_stack([np.zeros(NX), cup, np.zeros(NX)]))
        vv.append(vk)
    P = np.vstack(rows)
    V = np.concatenate(vv)
    X = np.tile(x, NV)
    T = ck.grid_tris(NV, NX, False)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    if fn[:, 1].sum() < 0:
        T = ck.flip(T)
    # tears through the membrane, away from the leading edge (the right wing, toward the camera, is worse)
    tear = ck.fbm(np.column_stack([P[:, 0] * 7.0, P[:, 2] * 9.0, P[:, 1] * 3.0]), SEED + (21 if side > 0 else 37))
    tear = tear * ck.smoothstep(0.3, 0.6, V) * ck.smoothstep(0.12, 0.25, X)
    cut = 0.2 if side > 0 else 0.14
    T = T[tear[T].mean(axis=1) < cut]
    edge = ck.smoothstep(max(cut - 0.1, 0.04), cut, tear)
    vein = 1.0 - scallop[np.tile(np.arange(NX), NV)]  # the membrane gathers into ridges between the scallops
    col = ck.mix(BLACK, PAL["abyss_navy"], (0.3 * V)[:, None])
    col = ck.mix(col, SHEEN, (0.45 * ck.smoothstep(0.12, 0.0, V) + 0.25 * vein)[:, None])
    col = ck.mix(col, WOUND * 0.5, (0.8 * edge)[:, None])
    uv = np.column_stack([X * 3.0, V * 0.6])
    for up in (True, False):
        Tw = T if up else ck.flip(T)
        off = np.array([0.0, 0.0018 if up else -0.0018, 0.0])
        parts.append((P + off, Tw, col if up else col * 0.9, "chain", 1.0, 0.35 * vein, edge * 0.8, uv, None))

    # the arm: a thin black spar along the leading edge, out to the tip
    xs = np.linspace(0.02, 1.0, 22)
    path = _lead(xs) + np.array([0.0, 0.004, 0.0])
    Ps, Ts = gh._tube(path, np.interp(xs, (0.02, 0.32, 0.56, 1.0), (0.018, 0.012, 0.010, 0.003)), 7)
    knuckle = np.exp(-((Ps[:, 0] - ELBOW[0]) / 0.02) ** 2) + np.exp(-((Ps[:, 0] - WRIST[0]) / 0.02) ** 2)
    parts.append((Ps, Ts, ck.mix(BLACK, SHEEN, (0.3 + 0.4 * knuckle)[:, None]), "chain", 1.0, 0.2, 0.0, None, None))

    # the hand's streamers: what the storm made of the primaries, long, thin and frayed
    for i, (x0, phi, L, wdt) in enumerate(((0.60, 28.0, 0.30, 0.040), (0.70, 40.0, 0.38, 0.036),
                                           (0.80, 52.0, 0.42, 0.030), (0.90, 66.0, 0.36, 0.024))):
        root = _lead(np.array([x0]))[0] + np.array([0.0, -0.002, -0.02])
        ph = math.radians(phi)
        d = gh._unit((math.sin(ph), -0.18, -math.cos(ph)))
        Pb, Nb, Tb, info = gh.blade(root, d, L, wdt, K=8, lead=0.5, thick=0.002, cup=0.1, tip_start=0.45,
                                    cut=(0.25, 0.4), floor=0.3, ruffle=(0.006, 3.0), wave=(0.01, 1.2),
                                    seed=200 + i + (0 if side > 0 else 10))
        t = info["t"]
        c = ck.mix(BLACK, PAL["abyss_navy"], (0.4 * t)[:, None])
        parts.append((Pb, Tb, c, "wrist", 1.0, 0.2 * (1.0 - t), 0.0, info["uv"], Nb))

    m = np.array([side, 1.0, 1.0])
    chain = rig.chain([f"shoulder_{tag}", f"elbow_{tag}", f"wrist_{tag}"],
                      [np.multiply(p, m) for p in (SHOULDER, ELBOW, WRIST, TIP)])
    for P_, T_, col_, bone, wet, cav, em, uv_, N_ in parts:
        if side < 0:
            P_, N_, T_ = gh._mirror(P_, N_, T_)
        b = chain if bone == "chain" else rig.index(f"{bone}_{tag}")
        slot = "membrane"
        ck.finish(mesh, P_, T_, slot, col_, b, wet=wet, cavity=cav, emission=em, uv=uv_, N=N_)


def tail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Five frayed membrane streamers where a gull's fanned tail would be."""
    it = rig.index("tail")
    for i, (phi, L) in enumerate(((-26.0, 0.30), (-12.0, 0.40), (0.0, 0.46), (13.0, 0.36), (27.0, 0.27))):
        ph = math.radians(phi)
        root = (0.012 * i - 0.024, 0.19, -0.30)
        P, N, T, info = gh.blade(root, (math.sin(ph), -0.05, -math.cos(ph)), L, 0.04, K=7, lead=0.5, thick=0.002,
                                 tip_start=0.4, cut=(0.3, 0.2), floor=0.3, ruffle=(0.005, 3.0), seed=240 + i)
        c = ck.mix(BLACK, PAL["abyss_navy"], (0.35 * info["t"])[:, None])
        ck.finish(mesh, P, T, "membrane", c, it, wet=1.0, uv=info["uv"], N=N)


def legs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Thin black legs and long hooked talons, held ready."""
    for sx, tag in ((1.0, "l"), (-1.0, "r")):
        il = rig.index(f"leg_{tag}")
        m = np.array([sx, 1.0, 1.0])
        a = np.multiply(HIP, m)
        b = np.multiply(ANKLE, m)
        P, T = gh._tube(ck.bezier([a, (a + b) / 2 + (0, -0.01, 0), b], 5), np.linspace(0.011, 0.007, 5), 6)
        ck.finish(mesh, P, T, "shell", BLACK, il, wet=1.0)
        for k, spread in enumerate((-24.0, 0.0, 24.0)):
            d = ck.rot_y(spread * sx) @ gh._unit((0.0, -0.35, -1.0))
            p1 = b + d * 0.06
            claw = ck.bezier([b, p1, p1 + d * 0.035 + (0, -0.02, 0), p1 + d * 0.03 + (0, -0.05, 0.012)], 7)
            P, T = gh._tube(claw, np.linspace(0.006, 0.0012, 7), 5, cap_start=False)
            ck.finish(mesh, P, T, "shell", ck.mix(BLACK, SHEEN, 0.4), il, wet=1.0)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("squall_wing")
    body(mesh, rig)
    beak(mesh, rig)
    wing(mesh, rig, 1.0)
    wing(mesh, rig, -1.0)
    tail(mesh, rig)
    legs(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips: the gull harrier's wing poses, played stiffer (held keys, snaps instead of follow-through)
# ---------------------------------------------------------------------------------------------
HOVER = 1.2  # the sheet's hover height: the KO falls this far
W_UP, W_DOWN, W_GLIDE, W_HALF, W_TUCK, W_FLARE, W_SPREAD = (gh.W_UP, gh.W_DOWN, gh.W_GLIDE, gh.W_HALF, gh.W_TUCK,
                                                           gh.W_FLARE, gh.W_SPREAD)
W_STOOP = ((0, 52, 18), (0, -55, 0), (0, 70, -6))  # folded hard back for the stoop
W_REACH = ((-10, 10, 34), (0, 0, -8), (0, -8, 16))  # thrown up and back over the strike


def build_clips() -> list[ck.Clip]:
    wk = gh._wing_key
    idle = ck.Clip("idle", 1.4, loop=True)
    # a beat that stops dead at the top and the bottom, then a glide with a twitch
    for t, pose, bob, pitch, head in ((0.0, W_UP, 0.0, 0.0, 0.0), (0.14, W_UP, 0.0, 0.0, 0.0),
                                      (0.36, W_DOWN, 0.07, -3.0, 0.0), (0.5, W_DOWN, 0.07, -3.0, 14.0),
                                      (0.8, W_GLIDE, 0.04, -1.0, 14.0), (0.98, W_GLIDE, 0.02, 1.0, -8.0),
                                      (1.18, W_GLIDE, 0.0, 1.0, -8.0), (1.4, W_UP, 0.0, 0.0, 0.0)):
        wk(idle, t, pose)
        idle.key("body", t, (pitch, 0, 0), (0, bob, 0))
        idle.key("neck", t, (-pitch, 0, 0), (0, -0.8 * bob, 0))
        idle.key("head", t, (0, 0, head))  # the head cocks sideways in jerks, listening
        idle.key("tail", t, (-3.0 * pitch, 0, 0))

    attack = ck.Clip("attack", 1.4)  # a steep stoop on a target below it, talons and beak reaching down
    for t, pose, root, bodyr, leg, neck, beak in (
        (0.0, W_GLIDE, (0, 0, 0), (0, 0, 0), 0, 0, 0),
        (0.14, W_DOWN, (0, 0.26, -0.06), (-8, 0, 0), 0, 6, 0),  # the tell: a hard climb, two beats
        (0.28, W_UP, (0, 0.46, -0.10), (-10, 0, 0), 0, 8, 0),
        (0.38, W_UP, (0, 0.50, -0.10), (-4, 0, 0), 0, 0, 0),  # a held beat at the top
        (0.48, W_STOOP, (0, 0.30, 0.10), (52, 0, 0), -40, 10, 10),  # it folds and drops head first
        (0.62, W_STOOP, (0, -0.55, 0.42), (62, 0, 0), -110, 14, 30),  # contact: talons and beak forward and down
        (0.72, W_REACH, (0, -0.72, 0.52), (38, 0, 0), -130, 6, 34),
        (0.86, W_REACH, (0, -0.62, 0.50), (20, 0, 0), -90, 0, 10),
        (1.04, W_DOWN, (0, -0.14, 0.26), (-8, 0, 0), -20, 0, 0),
        (1.2, W_UP, (0, 0.02, 0.06), (-4, 0, 0), -4, 0, 0),
        (1.4, W_GLIDE, (0, 0, 0), (0, 0, 0), 0, 0, 0),
    ):
        wk(attack, t, pose)
        attack.key("root", t, loc=root)
        attack.key("body", t, bodyr)
        attack.key("neck", t, (neck, 0, 0))
        attack.key("beak", t, (beak, 0, 0))
        attack.key("leg_l", t, (leg, 0, 0))
        attack.key("leg_r", t, (leg * 0.92, 0, 0))
        attack.key("tail", t, (-0.3 * bodyr[0], 0, 0))

    cast = ck.Clip("cast", 1.2)  # it spreads and holds, beak wide, and the storm answers (VFX)
    for t, pose, rear, root, beak in (
        (0.0, W_GLIDE, 0, (0, 0, 0), 0),
        (0.3, W_SPREAD, -34, (0, 0.14, -0.06), 40),
        (0.62, W_SPREAD, -34, (0, 0.14, -0.06), 40),  # held stiff, no settle
        (0.8, W_SPREAD, -30, (0, 0.12, -0.05), 34),
        (1.2, W_GLIDE, 0, (0, 0, 0), 0),
    ):
        wk(cast, t, pose)
        cast.key("body", t, (rear, 0, 0))
        cast.key("root", t, loc=root)
        cast.key("neck", t, (0.4 * rear, 0, 0))
        cast.key("beak", t, (beak, 0, 0))
        cast.key("tail", t, (0.6 * rear, 0, 0))
        cast.key("leg_l", t, (0.5 * rear, 0, 0))
        cast.key("leg_r", t, (0.5 * rear, 0, 0))

    hit = ck.Clip("hit", 0.6)
    buckle = ((6, 30, -24), (0, -38, 14), (0, 44, -26))
    flail = ((-6, 0, 46), (0, 0, -8), (0, -4, 18))
    for t, l_pose, r_pose, root, roll, neck in (
        (0.0, W_GLIDE, W_GLIDE, (0, 0, 0), 0, 0),
        (0.06, flail, buckle, (0, -0.10, -0.05), 18, -20),
        (0.26, flail, buckle, (0, -0.24, -0.06), 22, -8),
        (0.42, W_DOWN, W_DOWN, (0, -0.10, -0.02), 6, 0),
        (0.6, W_GLIDE, W_GLIDE, (0, 0, 0), 0, 0),
    ):
        wk(hit, t, l_pose, ("l",))
        wk(hit, t, r_pose, ("r",))
        hit.key("root", t, loc=root)
        hit.key("body", t, (-0.3 * roll, 0, roll))
        hit.key("neck", t, (neck, 0, -0.5 * roll))

    ko = ck.Clip("ko", 1.4)  # the light goes out of it and it falls like a torn kite
    spread = ((0, -6, 30), (0, -6, 0), (0, 14, -36))
    crumple = ((0, 40, -21), (0, -45, 0), (0, 62, -12))
    for t, l_pose, r_pose, drop, bodyr, neck in (
        (0.0, W_GLIDE, W_GLIDE, 0.0, (0, 0, 0), 0),
        (0.14, W_UP, W_UP, -0.04, (-12, 0, 0), -26),
        (0.45, W_HALF, W_UP, 0.22, (16, 0, 24), -10),  # one wing goes slack first: it slews
        (0.8, W_TUCK, W_HALF, 0.75, (30, 0, 40), 12),
        (1.02, W_HALF, crumple, HOVER, (14, 0, 12), 18),
        (1.2, spread, crumple, HOVER, (8, 0, 8), 22),
        (1.4, spread, crumple, HOVER, (8, 0, 8), 22),
    ):
        wk(ko, t, l_pose, ("l",))
        wk(ko, t, r_pose, ("r",))
        ko.key("root", t, loc=(0, -drop, 0))
        ko.key("body", t, bodyr, (0, -0.1 * min(drop / HOVER, 1.0), 0))
        ko.key("neck", t, (neck, 0, 0))
        ko.key("tail", t, (min(drop, 1.0) * 12.0, 0, 0))
    for t, r in ((0.0, 0), (0.14, 24), (0.6, 8), (1.4, 14)):
        ko.key("beak", t, (r, 0, 0))
    return [idle, attack, cast, hit, ko]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "squall_wing"})
    print(f"squall_wing: {info}")


if __name__ == "__main__":
    main()
