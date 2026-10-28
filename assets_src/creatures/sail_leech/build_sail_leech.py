"""Sail leech, Ch4 the drifting trader (M3-CRE-03): docs/kb/art/creatures/act1/sail_leech.md.

blender --background --factory-startup --python assets_src/creatures/sail_leech/build_sail_leech.py -- \
    --out assets/creatures/sail_leech/sail_leech.glb

Undertow-spawn shaped like a ray that clings to wet canvas: a 1.4 m flexible diamond of wet black carapace, its edge a
frill that ripples like a sail, glowing wound slits along its back, a whip tail and two small glowing eyes. It hangs in
the air (its origin is the hover point: the battle spec's `hover` lifts it).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 4613
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "storm_slate": "#3E4A57", "spawn_wound": "#3FE0C8",
    "deep_teal_shadow": "#0E4A55",
}.items()}

HALF_W = 0.7
HALF_L = 0.5
WING = 3  # bones per wing
# A variant's parameters (the fen leech is longer and ribbon-flat, M3-CRE-628); these values are the sail leech's.
THICK = 0.07  # the body's thickness over its middle (the underside is 0.6 of it)
DOME = 0.04  # the back's camber across the span
FRILL = 0.022  # the edge frill's ripple (the sail-like canvas edge)
FRILL_WAVES = 14.0
SLIT_Z = (0.18, 0.11)  # the first wound slit's z and the step back to the next (four slits)
EYE = (0.09, 0.29, 0.38)  # x, y and z of the eyes
TAIL_Z0, TAIL_STEP = -0.3, 0.3  # the tail bones' first joint and their length
TAIL_PATH = ((0, 0.2, -0.3), (0, 0.18, -0.6), (0.05, 0.12, -0.9), (0.0, 0.1, -1.2))  # the tail's curve
TAIL_R = (0.04, 0.006)  # its radius at the root and the tip
TAIL_CHAIN = ((0, 0.2, -0.3), (0, 0.2, -0.6), (0, 0.2, -0.9), (0, 0.2, -1.2))  # the tail's skinning spans
# The leech's own body and suckers (M3-CRE-654): the sails' resolution, the body's half-width and its top and belly
# heights over its middle, the annulus (one segment's length; three loft stations each), the oral and caudal suckers'
# radii and their segments round.
SAIL_SEGS, SAIL_RINGS = 64, 9
BODY_W = 0.12
BODY_H = (0.075, 0.045)
BODY_ANGLES = 14
ANNULUS = 0.065
ORAL_R = 0.05
SUCKER_R = 0.1
SUCKER_SEGS = 16
BATTENS = 16  # ribs round the sail
DROOP = 0.11  # how far the sail tips hang under the body's line (m)


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.1, 0))
    rig.add("body", (0, 0.2, -0.15), (0, 0.2, 0.25), "root")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        for k in range(WING):
            x0, x1 = s * (0.12 + k * 0.19), s * (0.12 + (k + 1) * 0.19)
            rig.add(f"wing_{tag}{k}", (x0, 0.2, 0.0), (x1, 0.2, 0.0), "body" if k == 0 else f"wing_{tag}{k - 1}")
    for k in range(3):
        rig.add(f"tail{k}", (0, 0.2, TAIL_Z0 - k * TAIL_STEP), (0, 0.2, (TAIL_Z0 - TAIL_STEP) - k * TAIL_STEP),
                "body" if k == 0 else f"tail{k - 1}")
    return rig


def _skin(rig: ck.Rig):
    left = rig.chain([f"wing_l{k}" for k in range(WING)], [(0.12 + k * 0.19, 0.2, 0.0) for k in range(WING + 1)])
    right = rig.chain([f"wing_r{k}" for k in range(WING)], [(-0.12 - k * 0.19, 0.2, 0.0) for k in range(WING + 1)])
    body = rig.index("body")

    def f(P):
        Jl, Wl = left(P)
        Jr, Wr = right(P)
        n = len(P)
        J = np.zeros((n, 2), dtype=np.int64)
        W = np.zeros((n, 2))
        ax = np.abs(P[:, 0])
        for v in range(n):
            if ax[v] < 0.12:
                w = float(ck.smoothstep(0.04, 0.12, ax[v]))
                side = Jl[v, 0] if P[v, 0] >= 0 else Jr[v, 0]
                J[v] = (body, side)
                W[v] = (1.0 - w, w)
            elif P[v, 0] >= 0:
                J[v], W[v] = Jl[v], Wl[v]
            else:
                J[v], W[v] = Jr[v], Wr[v]
        return J, W

    return f


def outline(a: np.ndarray) -> np.ndarray:
    """The ray's outline at angle a (0 = +x wing tip, pi/2 = nose): a diamond with swept, rounded wings."""
    cu, cv = np.cos(a), np.sin(a)
    t = 1.0 / (np.abs(cu) ** 1.6 + (np.abs(cv) * 0.85) ** 1.6) ** (1.0 / 1.6)
    uu, vv = cu * t, cv * t
    x = uu * HALF_W * (1.0 - 0.25 * np.abs(vv))
    z = vv * HALF_L + 0.12 * (1.0 - np.abs(uu)) * (vv > 0) - 0.08 * np.abs(uu) ** 2
    return np.column_stack([x, np.zeros_like(x), z])


def wing_body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The sails: a thin membrane over the whole outline (its middle hidden in the body), ribbed by battens that
    carry the body's segments out to a ruffled, canvas-pale frilled edge (M3-CRE-654)."""
    segs, rings = SAIL_SEGS, SAIL_RINGS
    ang = np.linspace(0, 2 * math.pi, segs, endpoint=False)
    edge = outline(ang)
    skin = _skin(rig)
    canvas = min(FRILL / 0.022, 1.0)  # how much of the pale canvas edge a variant keeps
    for top in (True, False):
        pts = []
        for k in range(rings + 1):
            r = k / rings
            ring = edge * r
            rim = ck.smoothstep(0.7, 1.0, r)
            frill = FRILL * (np.sin(ang * FRILL_WAVES) + 0.35 * np.sin(ang * FRILL_WAVES * 2.3 + 1.0)) * rim
            dome = DOME * (1.0 - (ring[:, 0] / HALF_W) ** 2)
            droop = -DROOP * ck.smoothstep(0.15, 1.0, np.abs(ring[:, 0]) / HALF_W) ** 1.5
            thick = (THICK * 0.3 * np.sqrt(max(1.0 - r, 0.0)) + 0.003) * (1.0 if top else -0.8)
            ring[:, 1] = 0.2 + dome + droop + frill + thick
            pts.append(ring)
        P = np.vstack(pts)
        P[:segs, 0] = 0.0
        P[:segs, 2] = 0.0
        T = ck.grid_tris(rings + 1, segs, True)
        fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
        want = 1.0 if top else -1.0
        if float((fn[:, 1] * want).sum()) < 0:
            T = ck.flip(T)
        R = np.repeat(np.arange(rings + 1) / rings, segs)
        n = ck.fbm(P * 6.0, SEED + (0 if top else 1))
        # battens: ribs radiating from the body out to the edge, the sail pleated between them
        A = np.tile(ang, rings + 1)
        batten = ck.smoothstep(0.55, 0.95, np.cos(A * BATTENS)) * ck.smoothstep(0.12, 0.3, R)
        batten = batten * (1 - ck.smoothstep(0.88, 0.99, R))
        P[:, 1] += (0.009 if top else -0.004) * batten
        rim = ck.smoothstep(0.82, 0.98, R)
        if top:
            col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], ck.smoothstep(-0.2, 0.4, n)[:, None])
            col = ck.mix(col, PAL["storm_slate"], (0.5 * batten)[:, None])
        else:
            col = np.tile(ck.mix(PAL["storm_slate"], PAL["deep_teal_shadow"], 0.4), (len(P), 1))
            col = ck.mix(col, PAL["lacquer_black"], (0.4 * batten)[:, None])
        col = ck.mix(col, PAL["storm_slate"] * 1.5, (0.85 * canvas * rim)[:, None])  # the canvas-pale frill
        col = ck.mix(col, PAL["lacquer_black"], (canvas * ck.smoothstep(0.97, 1.0, R))[:, None])  # a dark hem
        ck.finish(mesh, P, T, "carapace", col, skin, wet=1.0 - 0.8 * canvas * rim, cavity=0.25 * batten + 0.1)


def _body_profile(z: np.ndarray, z0: float, z1: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The body's half-width, top and belly (m) at z, rear z0 to front z1: full through the middle, rounding to the
    oral end and narrowing to the tail; each annulus swells between two grooves."""
    u = (z - z0) / (z1 - z0)
    taper = np.sqrt(np.clip(1.0 - ((u - 0.45) / 0.58) ** 2, 0.0, 1.0)) ** 0.7
    ring = 0.5 + 0.5 * np.cos(2 * math.pi * (z - z1) / ANNULUS)
    swell = 1.0 + 0.14 * ring
    w = (0.03 + (BODY_W - 0.03) * taper) * swell
    t = (0.012 + (BODY_H[0] - 0.012) * taper) * swell
    b = (0.01 + (BODY_H[1] - 0.01) * taper) * swell
    return w, t, b


def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The leech: a flattened, annulated body down the sails' middle, the spawn's wound slits open seams between
    its segments, an oral sucker under the eyes (M3-CRE-654)."""
    z0, z1 = TAIL_Z0, HALF_L + 0.06
    z = np.linspace(z0, z1, int(round((z1 - z0) / (ANNULUS / 3.0))) + 1)  # three stations an annulus
    for zc in (SLIT_Z[0] - k * SLIT_Z[1] for k in range(4)):  # stations on each slit, so each opens crisply
        z = np.concatenate([z, [zc - 0.012, zc, zc + 0.012]])
    z = np.unique(np.clip(z, z0, z1))[::-1]  # front to rear
    w, t, b = _body_profile(z, z0, z1)
    ang = np.linspace(0.0, 2 * math.pi, BODY_ANGLES, endpoint=False)
    sa, ca = np.sin(ang), np.cos(ang)
    rows = []
    for k in range(len(z)):
        dome = DOME
        x = w[k] * np.sign(sa) * np.abs(sa) ** 0.8
        y = 0.2 + dome + np.where(ca > 0, t[k], b[k]) * np.sign(ca) * np.abs(ca) ** 0.8
        rows.append(np.column_stack([x, y, np.full(len(ang), z[k])]))
    P = np.vstack(rows)
    T = ck.grid_tris(len(z), len(ang), True)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    if float((fn[:, 0] * P[T[:, 0], 0]).sum()) < 0:
        T = ck.flip(T)
    Z = P[:, 2]
    CA = np.tile(ca, len(z))
    back = ck.smoothstep(0.0, 0.6, CA)
    groove = ck.smoothstep(0.7, 0.98, np.cos(2 * math.pi * (Z - z1) / ANNULUS + math.pi))
    slits = np.zeros(len(P))
    for k in range(4):
        zc = SLIT_Z[0] - k * SLIT_Z[1]
        slits = np.maximum(slits, np.exp(-((Z - zc) / 0.009) ** 2) * ck.smoothstep(0.3, 0.7, CA))
    slits = ck.smoothstep(0.2, 0.8, slits)
    P[:, 1] -= 0.008 * slits  # the seam is open: sunk under the segments either side
    n = ck.fbm(P * 9.0, SEED + 3)
    col = ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], (0.35 + 0.4 * ck.smoothstep(-0.2, 0.4, n))[:, None])
    col = ck.mix(col, ck.mix(PAL["storm_slate"], PAL["deep_teal_shadow"], 0.4), (1 - back)[:, None] * 0.8)
    crown = ck.smoothstep(0.2, 0.9, 0.5 + 0.5 * np.cos(2 * math.pi * (Z - z1) / ANNULUS)) * back
    col = ck.mix(col, PAL["storm_slate"], (0.3 * crown)[:, None])  # each segment's crown catches the light
    col = ck.mix(col, PAL["lacquer_black"], (0.8 * groove)[:, None])
    stripe = np.exp(-(P[:, 0] / 0.012) ** 2) * back  # a faint dorsal stripe down the segments
    col = ck.mix(col, PAL["storm_slate"], (0.35 * stripe * (1 - groove))[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.55, slits[:, None])
    ck.finish(mesh, P, T, "carapace", col, _skin(rig), wet=1.0, cavity=np.clip(0.55 * groove + 0.15, 0, 1) * (1 - slits),
              emission=slits)
    # the oral sucker: a ribbed cup under the front, open forward and down
    front = np.array([0.0, 0.2 + DOME - 0.01, z1 - 0.01])
    _sucker(mesh, ORAL_R, front, np.array([0.0, -0.55, 1.0]), rig.rigid("body"))
    for s in (-1.0, 1.0):
        Pe, Te = ck.ellipsoid((s * EYE[0], EYE[1], EYE[2]), (0.025, 0.02, 0.025), 5, 8)
        ck.finish(mesh, Pe, Te, "carapace", PAL["spawn_wound"], rig.rigid("body"), wet=1.0, emission=1.0)
        for k in range(2):  # smaller dark eyespots in an arc behind each eye
            c = (s * (EYE[0] + 0.012 + 0.015 * k), EYE[1] - 0.006 - 0.006 * k, EYE[2] - 0.045 - 0.04 * k)
            Ps, Ts = ck.ellipsoid(c, (0.009, 0.006, 0.009), 3, 5)
            ck.finish(mesh, Ps, Ts, "carapace", PAL["lacquer_black"], rig.rigid("body"), wet=1.0, cavity=1.0)


def _sucker(mesh: ck.Mesh, radius: float, centre: np.ndarray, facing: np.ndarray, bone) -> None:
    """A leech's sucker: a muscular disc with a thick rim, its cup ribbed and pale, opening along `facing`."""
    f = facing / np.linalg.norm(facing)
    x = np.cross(np.array([0.0, 1.0, 0.0]) if abs(f[1]) < 0.9 else np.array([1.0, 0.0, 0.0]), f)
    x /= np.linalg.norm(x)
    R = np.column_stack([x, -f, np.cross(x, -f)])  # the lathe's +y is the disc's back
    prof = [(0.0, 0.22), (0.45, 0.17), (0.8, 0.07), (1.0, 0.0), (1.08, 0.12), (0.95, 0.32), (0.55, 0.45), (0.0, 0.5)]
    P, T = ck.lathe([(r * radius, y * radius) for r, y in prof], SUCKER_SEGS)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    if float((fn * (P[T[:, 0]] - P.mean(axis=0))).sum()) < 0:  # outward: the cup's face forward, its back behind
        T = ck.flip(T)
    rib = 0.5 + 0.5 * np.cos(np.tile(np.arange(SUCKER_SEGS) * (2 * math.pi / SUCKER_SEGS), len(prof)) * 7)
    row = np.repeat(np.arange(len(prof)), SUCKER_SEGS)
    inside = row <= 2
    col = np.where(inside[:, None], ck.mix(PAL["storm_slate"], PAL["deep_teal_shadow"], 0.5 + 0.3 * rib[:, None]),
                   ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], 0.4))
    col = np.where((row == 0)[:, None], PAL["lacquer_black"], col)
    P = ck.transform(P, R, centre)
    ck.finish(mesh, P, T, "carapace", col, bone, wet=1.0, cavity=np.where(inside, 0.3 + 0.4 * rib, 0.15))


def tail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The tail: the body narrowing to a ringed ribbon, ending in the caudal sucker it clings with (M3-CRE-654)."""
    n = 22
    path = ck.bezier(list(TAIL_PATH), n)
    rad = np.linspace(TAIL_R[0] * 1.25, TAIL_R[0] * 0.75, n)  # a fleshy ribbon all the way to the sucker
    seg_len = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
    ring = 0.5 + 0.5 * np.cos(2 * math.pi * seg_len / (ANNULUS * 0.7))
    P, T = ck.tube(path, rad * (1.0 + 0.12 * ring), 8, squash=1.7, cap_end=False)
    skin = rig.chain(["tail0", "tail1", "tail2"], list(TAIL_CHAIN))
    rr = np.concatenate([np.repeat(ring, 8), [1.0]])[: len(P)]
    col = ck.mix(ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], 0.4), PAL["lacquer_black"], (1 - rr)[:, None] * 0.7)
    ck.finish(mesh, P, T, "carapace", col, skin, wet=1.0, cavity=0.4 * (1 - rr))
    tip = path[-1]
    tdir = (path[-1] - path[-3]) / np.linalg.norm(path[-1] - path[-3])
    _sucker(mesh, SUCKER_R, tip + tdir * SUCKER_R * 0.15, tdir + np.array([0.0, -1.2, 0.0]),
            rig.rigid("tail2"))


def build_mesh(rig: ck.Rig, name: str = "sail_leech") -> ck.Mesh:
    mesh = ck.Mesh(name)
    wing_body(mesh, rig)
    body(mesh, rig)
    tail(mesh, rig)
    return mesh


def build_clips() -> list[ck.Clip]:
    wings = [(f"wing_{t}{k}", 1.0 if t == "l" else -1.0, k) for t in "lr" for k in range(WING)]
    idle = ck.Clip("idle", 2.4, loop=True)
    for b, s, k in wings:
        idle.wave(b, amp_rot=(0.0, 0.0, 9.0 * s), cycles=1, phase=-k * 0.9)
    idle.wave("body", amp_loc=(0.0, 0.05, 0.0), cycles=1, phase=math.pi)
    for k in range(3):
        idle.wave(f"tail{k}", amp_rot=(0.0, 12.0, 0.0), cycles=1, phase=-k * 0.8)

    attack = ck.Clip("attack", 1.3)  # it drops and wraps: the wings fold down over the target
    for t, drop, fold, fwd in ((0.0, 0, 0, 0), (0.45, 0.15, -0.3, 0), (0.7, -0.7, 1.0, 0.5), (0.9, -0.7, 1.0, 0.5),
                                (1.3, 0, 0, 0)):
        attack.key("root", t, (0, 0, 0), (0, drop, fwd))
        for b, s, k in wings:
            attack.key(b, t, (0, 0, -24.0 * fold * s))
    cast = ck.Clip("cast", 1.4)  # it spreads flat and shudders
    for i, t in enumerate(np.linspace(0, 1.4, 15)):
        shud = (0.0 if i in (0, 14) else (3.0 if i % 2 else -3.0))
        env = math.sin(math.pi * t / 1.4)
        for b, s, k in wings:
            cast.key(b, float(t), (shud * env, 0, 6.0 * env * s))
    hit = ck.Clip("hit", 0.5)
    for t, c in ((0.0, 0.0), (0.12, 1.0), (0.5, 0.0)):
        hit.key("root", t, (10.0 * c, 0, 0), (0, -0.1 * c, -0.1 * c))
        for b, s, k in wings:
            hit.key(b, t, (0, 0, -18.0 * c * s))
    ko = ck.Clip("ko", 1.6)  # it falls like a wet sheet to the deck (the hover is about 1.4 m)
    for t, drop, fold in ((0.0, 0, 0), (0.4, 0.2, 0.5), (1.0, 1.25, -0.4), (1.3, 1.36, 0.2), (1.6, 1.38, 0.0)):
        ko.key("root", t, (8.0 * min(t, 1.0), 0, 0), (0, -drop, 0))
        for b, s, k in wings:
            ko.key(b, t, (0, 0, -20.0 * fold * s))
    return [idle, attack, cast, hit, ko]


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    rig = build_rig()
    mesh = build_mesh(rig)
    info = ck.export_creature(mesh, rig, build_clips(), args.out, extras={"hymn_creature": "sail_leech"})
    print(f"sail_leech: {info}")


if __name__ == "__main__":
    main()
