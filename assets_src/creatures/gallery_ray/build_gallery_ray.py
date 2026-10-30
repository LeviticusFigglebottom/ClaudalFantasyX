"""Gallery ray, Ch11 Sunken Vey (M3-CRE-627): docs/kb/art/creatures/act2/gallery_ray.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/gallery_ray/build_gallery_ray.py -- \
    --out assets/creatures/gallery_ray/gallery_ray.glb

A dusky cave ray of the Vey's flooded corridors, freckled with the salt-glass floors' light: a broad diamond 1.6 m
across with a whip tail 1.1 m long. Its one exaggeration is that it glides through the air between pools, wings
spread, like a flying fish. The back is `cumulus_shadow` mottled toward `lacquer_black` and freckled with
`salt_glass`, the wing margin carries a faint `sea_glow` (its own slot's emission: the ray's own light, not glimmer), the belly is `bone`, the eyes on top are
`lacquer_black`, and the spiracles behind them are dark openings in raised rims.

**The battle read (M3-CRE-645).** A pale flat sheet read as plain at review distance, so the disc has shape: a raised
midline keel with a row of tubercles toward the tail, the pectoral muscle bulging either side of the body and
grooved where it meets it, each eye on a raised socket under a dark brow ridge, the spiracles rimmed, a whip tail with
a dark serrated barb near its root, and a darker trailing edge. The idle curls the wingtips in a wave that runs out
along the wing. The weak point is one small closed mark (ADR 0151): the camera-side (-x) spiracle's valve is shut,
and a small `spawn_wound` lens on it glows (the body slot's emission).

**A flier.** The origin is its hover point (the disc's centre); the battle spec's `hover` (creatures.json, 0.95 m:
below the battle camera, so its back reads) lifts it. The KO drops the root by that hover, so it ends lying flat on the floor (the pool).

Rig (12 bones): root, `body`, the wings `wing_l0`..`wing_l2` and `wing_r0`..`wing_r2` (from the body out to the
tip, each hinging along the ray's length), and the tail `tail_0`..`tail_3`.

`python3 build_gallery_ray.py --report` prints the triangle count and per-clip skinned bounds (numpy, no export).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 6272
PAL = {k: ck.hexrgb(v) for k, v in {
    "salt_glass": "#BFE6E0", "cumulus_shadow": "#8FA7C4", "sea_glow": "#1C6B78", "bone": "#E6DAC0",
    "lacquer_black": "#1D1916", "spawn_wound": "#3FE0C8",
}.items()}
DUSK = ck.mix(PAL["cumulus_shadow"], PAL["lacquer_black"], 0.55)  # the back's darkest mottle and the rosettes

HOVER = 0.95  # below the battle camera (the Act II plan sheet: at head height it was seen edge-on, pale on pale):
# the stand-in spec lifts the origin this far, and the KO drops it this far; its attack banks a wingtip 0.65 m down
SPAN = 0.8  # half the span: 1.6 m across
NOSE_Z, TIP_Z, REAR_Z = 0.5, 0.04, -0.5  # the snout, the wingtips' line, the disc's rear
TAIL_Z = [-0.44, -0.7, -0.96, -1.24, -1.56]  # four tail bones to the whip's end
WING_X = [0.19, 0.44, 0.64, SPAN + 0.02]  # wing_0 .. wing_2 spans, out from the body
SEGS, RINGS = 52, 26  # more vertices across (the midline and the pectorals), fewer along
ACROSS_POW = 1.15  # the across spacing: sin(a) ** this; above 1 puts more vertices near the midline
EYE = np.array([0.065, 0.0, 0.25])
SPIRACLE = np.array([0.072, 0.0, 0.165])
WOUND_SIDE = -1.0  # the camera-side spiracle (-x) carries the weak point
KEEL_Z = (0.34, REAR_Z + 0.03)  # the raised midline keel, front to back
PEC_X, PEC_Z = 0.25, 0.04  # the pectoral muscle's crest either side of the body
BARB_U = (0.2, 0.36)  # the barb's span along the tail (fraction of its length): from its root to its point
MARGIN = 0.84  # the outer band of the disc (fraction of the half-span) that is the margin slot
ROSETTE_SCALE = 6.0  # dusky rosettes per metre over the back
ROSETTE_DARK = 0.7
BACK_DUSK = 0.75  # how far the mottling darkens the back toward DUSK

PARTS: dict[str, tuple[int, int]] = {}


def half_span(z) -> np.ndarray:
    z = np.asarray(z, dtype=np.float64)
    front = SPAN * np.clip((NOSE_Z - z) / (NOSE_Z - TIP_Z), 0.0, 1.0) ** 0.8
    back = SPAN * np.clip((z - REAR_Z) / (TIP_Z - REAR_Z), 0.0, 1.0) ** 1.35
    return np.maximum(np.where(z >= TIP_Z, front, back), 0.012)


def thickness(x, z, top: bool) -> np.ndarray:
    """The disc's height above (or depth below) its mid-plane: a thin wing and a raised body down the middle."""
    s = half_span(z)
    u = np.clip(np.abs(x) / s, 0.0, 1.0)
    along = np.clip((z - REAR_Z) / (NOSE_Z - REAR_Z), 0.0, 1.0)
    body = (0.07 if top else 0.035) * np.exp(-(x / 0.15) ** 2) * np.sin(np.clip(along, 0.02, 1.0) * math.pi) ** 0.6
    wing = (0.03 if top else 0.014) * (1.0 - u ** 2) ** 0.8
    if not top:
        return body + wing
    return body + wing + 0.034 * pectoral(x, z)


def pectoral(x, z) -> np.ndarray:
    """0..1: the pectoral muscle's mass on the back, either side of the body, fading out along the wing."""
    x, z = np.asarray(x, dtype=np.float64), np.asarray(z, dtype=np.float64)
    return np.exp(-((np.abs(x) - PEC_X) / 0.1) ** 2 - ((z - PEC_Z) / 0.24) ** 2)


def orient(P: np.ndarray, T: np.ndarray, want) -> np.ndarray:
    T = np.asarray(T, dtype=np.int64).copy()
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    bad = (fn * want(P[T].mean(axis=1))).sum(axis=1) < 0
    T[bad] = T[bad][:, ::-1]
    return T


def mark(name: str, mesh: ck.Mesh, start: int) -> None:
    lo, _hi = PARTS.get(name, (start, start))
    PARTS[name] = (min(lo, start), mesh.count)


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.2, 0))
    rig.add("body", (0, 0, 0), (0, 0, 0.4), "root")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        parent = "body"
        for k in range(3):
            rig.add(f"wing_{tag}{k}", (s * WING_X[k], 0, TIP_Z), (s * WING_X[k + 1], 0, TIP_Z), parent)
            parent = f"wing_{tag}{k}"
    parent = "body"
    for k in range(4):
        rig.add(f"tail_{k}", (0, 0.005, TAIL_Z[k]), (0, 0.005, TAIL_Z[k + 1]), parent)
        parent = f"tail_{k}"
    return rig


def disc_skin(rig: ck.Rig):
    """By the distance out from the midline: body, then each wing bone, blended across the last third of a span."""
    body = rig.index("body")
    wings = {s: [rig.index(f"wing_{tag}{k}") for k in range(3)] for s, tag in ((1.0, "l"), (-1.0, "r"))}
    knots = [0.0] + WING_X

    def f(P):
        n = len(P)
        J = np.zeros((n, 2), dtype=np.int64)
        W = np.zeros((n, 2))
        for v in range(n):
            x = float(P[v, 0])
            chain = [body] + wings[1.0 if x >= 0 else -1.0]
            c = min(abs(x), knots[-1] - 1e-6)
            k = int(np.searchsorted(knots, c, side="right") - 1)
            t = (c - knots[k]) / (knots[k + 1] - knots[k])
            J[v] = (chain[k], chain[k])
            W[v] = (1.0, 0.0)
            if k + 1 < len(chain) and t > 0.6:
                w = float(ck.smoothstep(0.6, 1.0, t)) * 0.5
                J[v, 1], W[v] = chain[k + 1], (1.0 - w, w)
            elif k > 0 and t < 0.4:
                w = float(ck.smoothstep(0.4, 0.0, t)) * 0.5
                J[v, 1], W[v] = chain[k - 1], (1.0 - w, w)
        return J, W

    return f


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def disc(mesh: ck.Mesh, rig: ck.Rig) -> None:
    zs = np.linspace(REAR_Z, NOSE_Z, RINGS)
    a = np.arange(SEGS) * (2.0 * math.pi / SEGS)
    s = half_span(zs)
    # angle -> across: sin(a) spaced so the margin gets more vertices than the middle
    X = s[:, None] * np.sign(np.sin(a))[None] * np.abs(np.sin(a))[None] ** ACROSS_POW
    top = np.cos(a)[None] >= 0
    Z = np.repeat(zs[:, None], SEGS, axis=1)
    Y = np.where(top, thickness(X, Z, True), -thickness(X, Z, False)) * np.abs(np.cos(a))[None] ** 0.35
    # the wingtips' curl: a slight upward sweep of the outer wing, and the margin's gentle droop toward the rear
    u = np.clip(np.abs(X) / SPAN, 0.0, 1.0)
    Y = Y + 0.06 * u ** 2.5 - 0.02 * ck.smoothstep(0.0, -0.4, Z) * u
    P = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)
    T = ck.grid_tris(RINGS, SEGS, True)
    P = np.vstack([P, [(0.0, 0.0, REAR_Z - 0.01), (0.0, 0.004, NOSE_Z + 0.012)]])
    caps = [(k, (k + 1) % SEGS, len(P) - 2) for k in range(SEGS)]
    r0 = (RINGS - 1) * SEGS
    caps += [(r0 + k, r0 + (k + 1) % SEGS, len(P) - 1) for k in range(SEGS)]
    T = np.vstack([T, np.asarray(caps, dtype=np.int64)])
    T = orient(P, T, lambda c: np.column_stack([c[:, 0] * 0.15, c[:, 1], np.zeros(len(c))]))
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    top_v = np.concatenate([np.tile(top[0], RINGS), [False, True]])
    uu = np.clip(np.abs(P[:, 0]) / np.maximum(half_span(P[:, 2]), 1e-6), 0.0, 1.0)

    # colour: a dusky slate back (cumulus_shadow mottled toward lacquer_black) freckled with salt-glass, bone belly; eyes'
    # rims and the spiracles. Dusky, not pale: pale on the gallery's pale salt floor it vanished (the Act II plan sheet)
    mott = ck.smoothstep(-0.1, 0.35, ck.fbm(P * np.array([4.0, 4.0, 4.0]), SEED))
    back = ck.mix(PAL["cumulus_shadow"], DUSK, (BACK_DUSK * mott)[:, None])
    # pale freckles over the wings (not the midline): the salt-glass floor's light on the back
    freckle = ck.smoothstep(0.2, 0.45, ck.value_noise(P * np.array([9.0, 9.0, 9.0]), SEED + 3))
    freckle = freckle * ck.smoothstep(0.12, 0.25, np.abs(P[:, 0]))
    back = ck.mix(back, PAL["salt_glass"], (0.85 * freckle)[:, None])
    back = ck.mix(back, PAL["cumulus_shadow"], (0.4 * np.exp(-(P[:, 0] / 0.12) ** 2))[:, None])  # the darker ridge
    # the groove where the pectoral meets the body, shaded darker, and the muscle's crest a little lighter
    pec = pectoral(P[:, 0], P[:, 2])
    groove = np.exp(-((np.abs(P[:, 0]) - 0.13) / 0.05) ** 2) * ck.smoothstep(-0.35, 0.0, P[:, 2]) * \
        ck.smoothstep(0.4, 0.15, P[:, 2])
    back = ck.mix(back, PAL["cumulus_shadow"] * 0.82, (0.55 * groove)[:, None])
    back = ck.mix(back, PAL["salt_glass"], (0.35 * pec)[:, None])
    # the trailing edge and wingtips a shade darker, so the outline reads against a pale floor
    edge = ck.smoothstep(0.86, 1.0, uu) * ck.smoothstep(0.3, -0.1, P[:, 2])
    back = ck.mix(back, PAL["cumulus_shadow"] * 0.8, (0.8 * edge)[:, None])
    # dusky rosettes over the back, so the disc reads at battle distance (pillar 4)
    rosette = ck.smoothstep(0.62, 0.78, ck.value_noise(P * ROSETTE_SCALE, SEED + 11))
    rosette = rosette * ck.smoothstep(0.08, 0.2, np.abs(P[:, 0])) * (1.0 - ck.smoothstep(0.8, 0.95, uu))
    back = ck.mix(back, DUSK, (ROSETTE_DARK * rosette)[:, None])
    col = np.where(top_v[:, None], back, ck.mix(PAL["bone"], PAL["salt_glass"], 0.25))
    spir = np.zeros(len(P))
    for sx in (1.0, -1.0):
        c = SPIRACLE * np.array([sx, 1.0, 1.0])
        spir = np.maximum(spir, np.exp(-(((P[:, 0] - c[0]) / 0.02) ** 2 + ((P[:, 2] - c[2]) / 0.03) ** 2)) * top_v)
    col = ck.mix(col, PAL["cumulus_shadow"] * 0.5, ck.smoothstep(0.3, 0.7, spir)[:, None])  # the sockets, dark
    P = P - N * (0.008 * spir)[:, None]
    margin = ck.smoothstep(MARGIN - 0.06, 0.97, uu) * ck.smoothstep(REAR_Z + 0.02, REAR_Z + 0.12, P[:, 2])
    skin = disc_skin(rig)
    tri_margin = (uu[T] > MARGIN).all(axis=1)
    cav = np.clip(0.8 * spir + 0.5 * groove * top_v, 0, 1)
    for name, mask, emis, slot in (("disc", ~tri_margin, np.zeros(len(P)), "body"),
                                   ("margin", tri_margin, margin, "margin")):
        Ts = T[mask]
        used = np.unique(Ts)
        remap = np.full(len(P), -1, dtype=np.int64)
        remap[used] = np.arange(len(used))
        start = mesh.count
        ck.finish(mesh, P[used], remap[Ts], slot, col[used], skin, wet=0.7, cavity=cav[used],
                  emission=emis[used], N=N[used])
        mark(name, mesh, start)


def top_y(x: float, z: float) -> float:
    """The back's height at (x, z) in the rest disc (the wingtips' sweep included)."""
    u = min(abs(x) / SPAN, 1.0)
    return float(thickness(np.array([x]), np.array([z]), True)[0]) + 0.06 * u ** 2.5


def ring(c: np.ndarray, rx: float, rz: float, r: float, n: int = 10) -> tuple[np.ndarray, np.ndarray]:
    """A closed tube loop round an ellipse (rx across, rz along) on the back at c: a raised rim."""
    a = np.linspace(0.0, 2.0 * math.pi, n, endpoint=False)
    path = np.column_stack([c[0] + rx * np.cos(a), np.zeros(n), c[2] + rz * np.sin(a)])
    path[:, 1] = [top_y(px, pz) for px, _, pz in path]
    path = np.vstack([path, path[:1]])
    return ck.tube(path, r, 4, cap_start=False, cap_end=False)


def eyes(mesh: ck.Mesh, rig: ck.Rig) -> None:
    dark = ck.mix(PAL["cumulus_shadow"], PAL["lacquer_black"], 0.55)
    socket_col = ck.mix(PAL["salt_glass"], PAL["cumulus_shadow"], 0.55)
    for sx in (1.0, -1.0):
        c = EYE * np.array([sx, 1.0, 1.0])
        y = top_y(c[0], c[2])
        # the raised socket the eye sits in, and the dark brow ridge arching over its outer side
        Pk, Tk = ck.ellipsoid((c[0], y - 0.004, c[2] - 0.004), (0.034, 0.018, 0.042), 4, 8)
        start = mesh.count
        ck.finish(mesh, Pk, Tk, "body", socket_col, rig.rigid("body"), wet=0.7, cavity=0.2)
        a = np.linspace(-0.35 * math.pi, 0.75 * math.pi, 7)  # from behind the eye, round its outside, to its front
        brow = np.column_stack([c[0] + sx * 0.03 * np.cos(a) - sx * 0.004, y + 0.012 + 0.006 * np.sin(a),
                                c[2] + 0.04 * np.sin(a) - 0.004])
        Pb, Tb = ck.tube(brow, 0.008 * np.sin(np.linspace(0.35, math.pi - 0.35, 7)) + 0.002, 5)
        ck.finish(mesh, Pb, Tb, "body", dark, rig.rigid("body"), wet=0.7, cavity=0.3)
        mark("brows", mesh, start)
        Pe, Te = ck.ellipsoid((c[0], y + 0.016, c[2]), (0.021, 0.017, 0.027), 5, 10)
        start = mesh.count
        ck.finish(mesh, Pe, Te, "eye", PAL["lacquer_black"], rig.rigid("body"), wet=1.0)
        mark("eyes", mesh, start)
        # the spiracle behind the eye: a raised rim round a dark opening
        c = SPIRACLE * np.array([sx, 1.0, 1.0])
        y = top_y(c[0], c[2])
        Pr, Tr = ring(c, 0.019, 0.028, 0.006)
        start = mesh.count
        ck.finish(mesh, Pr, Tr, "body", socket_col, rig.rigid("body"), wet=0.8, cavity=0.3)
        if sx != WOUND_SIDE:
            Ps, Ts = ck.ellipsoid((c[0], y - 0.003, c[2]), (0.015, 0.006, 0.024), 4, 8)
            ck.finish(mesh, Ps, Ts, "body", PAL["lacquer_black"], rig.rigid("body"), wet=1.0, cavity=0.8)
        else:
            # the weak point: this spiracle's valve shut, a small closed lens of light on it
            Pv, Tv = ck.ellipsoid((c[0], y - 0.002, c[2]), (0.016, 0.007, 0.025), 4, 8)
            ck.finish(mesh, Pv, Tv, "body", socket_col * 0.9, rig.rigid("body"), wet=0.9, cavity=0.3)
            Pw, Tw = ck.ellipsoid((c[0], y + 0.004, c[2]), (0.007, 0.004, 0.015), 3, 6)
            ck.finish(mesh, Pw, Tw, "body", PAL["spawn_wound"] * 0.65, rig.rigid("body"), wet=1.0, emission=1.0)
        mark("spiracles", mesh, start)


def keel(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The raised midline: a low keel from between the eyes to the tail root, with a row of tubercles on its rear."""
    zs = np.linspace(KEEL_Z[0], KEEL_Z[1], 16)
    along = (zs - KEEL_Z[1]) / (KEEL_Z[0] - KEEL_Z[1])
    path = np.column_stack([np.zeros(16), [top_y(0.0, z) - 0.006 for z in zs], zs])
    rad = 0.022 * np.sin(np.clip(along, 0.04, 0.96) * math.pi) ** 0.5
    P, T = ck.tube(path, rad, 6, squash=0.45, up_hint=(1.0, 0.0, 0.0))  # flat across, tall: a keel
    col = ck.mix(ck.mix(PAL["salt_glass"], PAL["cumulus_shadow"], 0.6), PAL["cumulus_shadow"] * 0.8,
                 ck.smoothstep(0.012, 0.03, P[:, 1] - np.interp(-P[:, 2], -zs, path[:, 1]))[:, None])
    start = mesh.count
    ck.finish(mesh, P, T, "body", col, rig.rigid("body"), wet=0.7, cavity=0.15)
    for z in np.linspace(-0.18, KEEL_Z[1] + 0.05, 4):  # low, raked back
        y = top_y(0.0, z) + 0.006
        Pt, Tt = ck.tube(np.array([(0.0, y, z + 0.012), (0.0, y + 0.009, z - 0.006), (0.0, y + 0.014, z - 0.02)]),
                         np.array([0.009, 0.005, 0.0012]), 5, cap_start=False)
        ck.finish(mesh, Pt, Tt, "body", ck.mix(PAL["cumulus_shadow"], PAL["lacquer_black"], 0.4), rig.rigid("body"),
                  wet=0.7, cavity=0.2)
    mark("keel", mesh, start)


def tail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A whip: thick at the root, tapering fast to a thin lash, with dark bands toward the end and a serrated barb on
    its top near the root, pointing back."""
    n = 30
    u = np.linspace(0.0, 1.0, n)
    path = np.array([(0.0, 0.005 - 0.01 * t, z) for t, z in zip(u, np.linspace(REAR_Z + 0.08, TAIL_Z[-1], n))])
    rad = 0.036 * (1.0 - u) ** 2.2 + 0.0025
    P, T = ck.tube(path, rad, 8, cap_start=True, cap_end=True, squash=0.8)
    uu = np.clip((REAR_Z + 0.08 - P[:, 2]) / (REAR_Z + 0.08 - TAIL_Z[-1]), 0.0, 1.0)
    col = ck.mix(ck.mix(PAL["salt_glass"], PAL["cumulus_shadow"], 0.45), PAL["cumulus_shadow"],
                 ck.smoothstep(0.25, 0.6, uu)[:, None])
    bands = (0.5 + 0.5 * np.cos(uu * 2.0 * math.pi * 7.0)) ** 6 * ck.smoothstep(0.42, 0.55, uu)
    col = ck.mix(col, ck.mix(PAL["cumulus_shadow"], PAL["lacquer_black"], 0.5), (0.7 * bands)[:, None])
    pts = np.array([(0.0, 0.005, z) for z in [REAR_Z + 0.08] + TAIL_Z[1:]])
    skin = rig.chain([f"tail_{k}" for k in range(4)], pts)
    start = mesh.count
    ck.finish(mesh, P, T, "body", col, skin, wet=0.7)
    # the barb: a flat blade lying along the top, its edges serrated, darker than the tail
    k0, k1 = (int(round(b * (n - 1))) for b in BARB_U)
    m = 9
    t = np.linspace(0.0, 1.0, m)
    zb = np.interp(t, [0.0, 1.0], [path[k0, 2], path[k1, 2]])
    yb = np.interp(-zb, -path[:, 2], path[:, 1]) + np.interp(-zb, -path[:, 2], rad) * 0.8 + 0.004 + 0.012 * t
    bpath = np.column_stack([np.zeros(m), yb, zb])
    serr = 1.0 + 0.35 * (np.arange(m) % 2)
    brad = (0.012 * (1.0 - t) ** 0.8 + 0.001) * serr
    Pb, Tb = ck.tube(bpath, brad, 6, squash=0.3, up_hint=(1.0, 0.0, 0.0))  # wide across, thin
    ck.finish(mesh, Pb, Tb, "body", ck.mix(PAL["cumulus_shadow"], PAL["lacquer_black"], 0.6), skin, wet=0.9,
              cavity=0.2)
    # the pelvic lobes either side of the tail's root
    for sx in (1.0, -1.0):
        Pp, Tp = ck.ellipsoid((sx * 0.07, -0.006, REAR_Z + 0.03), (0.06, 0.012, 0.07), 4, 8)
        ck.finish(mesh, Pp, Tp, "body", ck.mix(PAL["salt_glass"], PAL["cumulus_shadow"], 0.35), rig.rigid("body"),
                  wet=0.7)
    mark("tail", mesh, start)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("gallery_ray")
    disc(mesh, rig)
    eyes(mesh, rig)
    keel(mesh, rig)
    tail(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 3.0
ATTACK_SEC = 1.2
ATTACK_CONTACT = 0.6
CAST_SEC = 1.6
CAST_CONTACT = 0.9
POOL_Y = -(HOVER - 0.05)  # the cast settles the disc's underside onto the pool (the floor)
HIT_SEC = 0.5
KO_SEC = 2.0
KO_REST = 0.048  # the KO lifts the body by its underside's depth, so it lies on the floor


def wings(c: ck.Clip, t: float, left, right=None) -> None:
    right = left if right is None else right
    for k in range(3):
        c.key(f"wing_l{k}", t, (0, 0, left[k]))
        c.key(f"wing_r{k}", t, (0, 0, -right[k]))


def tail_keys(c: ck.Clip, t: float, ry: float, rx: float = 0.0) -> None:
    for k in range(4):
        c.key(f"tail_{k}", t, (rx * (0.5 + 0.2 * k), ry * (0.6 + 0.3 * k), 0))


def build_idle() -> ck.Clip:
    c = ck.Clip("idle", IDLE_SEC, loop=True)  # a slow undulating glide in place, the tips curling behind the wave
    for k, amp in enumerate((6.0, 10.0, 20.0)):
        c.wave(f"wing_l{k}", amp_rot=(0, 0, amp), cycles=1, phase=-0.9 * k)
        c.wave(f"wing_r{k}", amp_rot=(0, 0, -amp), cycles=1, phase=-0.9 * k)
    c.wave("body", amp_rot=(1.5, 0, 2.5), amp_loc=(0, 0.045, 0), cycles=1, phase=math.pi)
    for k in range(4):
        c.wave(f"tail_{k}", amp_rot=(2.0, 5.0 + 2.0 * k, 0), cycles=1, phase=-0.9 * k - 0.5)
    return c


def build_attack() -> ck.Clip:
    c = ck.Clip("attack", ATTACK_SEC)  # it banks and sweeps its left wing down across the target
    for t, rz, ry, ly, wl, wr, tl in ((0.0, 0, 0, 0, (0, 0, 0), (0, 0, 0), 0),
                                      (0.32, 26.0, 8.0, 0.08, (14.0, 16.0, 18.0), (-4.0, -6.0, -8.0), -10.0),
                                      (0.45, 20.0, 4.0, 0.06, (16.0, 20.0, 24.0), (-2.0, -4.0, -5.0), -12.0),
                                      (ATTACK_CONTACT, -30.0, -16.0, -0.12, (-14.0, -18.0, -10.0), (4.0, 6.0, 8.0),
                                       14.0),
                                      (0.8, -14.0, -8.0, -0.06, (-6.0, -8.0, -6.0), (2.0, 3.0, 4.0), 8.0),
                                      (ATTACK_SEC, 0, 0, 0, (0, 0, 0), (0, 0, 0), 0)):
        c.key("body", t, (0, ry, rz), (0, ly, 0))
        wings(c, t, wl, wr)
        tail_keys(c, t, tl)
    return c


def build_cast() -> ck.Clip:
    c = ck.Clip("cast", CAST_SEC)  # it settles into a pool (the floor) and the water flares with its glow (VFX)
    for t, ly, rx, w, tl in ((0.0, 0.0, 0, (0, 0, 0), 0), (0.45, POOL_Y * 0.8, -6.0, (10.0, 12.0, 14.0), 6.0),
                             (0.72, POOL_Y, 0.0, (-2.0, -3.0, -4.0), 0.0),
                             (CAST_CONTACT, POOL_Y, 0.0, (-3.0, -4.0, -6.0), 0.0),
                             (1.12, POOL_Y + 0.01, -2.0, (0.0, -2.0, -3.0), -4.0),
                             (CAST_SEC, 0.0, 0, (0, 0, 0), 0)):
        c.key("root", t, (rx, 0, 0), (0, ly, 0))
        wings(c, t, w)
        tail_keys(c, t, tl, rx=5.0 if 0.6 < t < 1.2 else 0.0)
    return c


def build_hit() -> ck.Clip:
    c = ck.Clip("hit", HIT_SEC)  # it flips half over and rights itself
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.28, -0.25), (HIT_SEC, 0.0)):
        c.key("body", t, (-8.0 * s, 0, 52.0 * s), (0, 0.07 * s, -0.05 * s))
        wings(c, t, (-6.0 * s, -10.0 * s, -14.0 * s), (12.0 * s, 16.0 * s, 20.0 * s))
        tail_keys(c, t, 14.0 * s, rx=-8.0 * s)
    return c


def build_ko() -> ck.Clip:
    c = ck.Clip("ko", KO_SEC)  # it falters, slides down into the water and lies flat
    for t, rloc, rx, rz, w, tl in ((0.0, (0, 0, 0), 0, 0, (0, 0, 0), 0),
                                   (0.25, (0, 0.05, 0), -6.0, -18.0, (14.0, 18.0, 22.0), 10.0),
                                   (0.85, (0, -0.75, 0.18), 12.0, 8.0, (10.0, 14.0, 16.0), -8.0),
                                   (1.35, (0, -HOVER, 0.34), 2.0, 0.0, (-2.0, -3.0, -4.0), 4.0),
                                   (KO_SEC, (0, -HOVER, 0.36), 0.0, 0.0, (-1.0, -1.5, -2.0), 0.0)):
        c.key("root", t, (rx, 0, rz), rloc)
        c.key("body", t, (0, 0, 0), (0, KO_REST if t >= 1.35 else 0.0, 0))
        wings(c, t, w)
        tail_keys(c, t, tl)
    return c


def build_clips() -> list[ck.Clip]:
    return [build_idle(), build_attack(), build_cast(), build_hit(), build_ko()]


# ---------------------------------------------------------------------------------------------
# A numpy check (no Blender): skinned bounds and the peak time per clip
# ---------------------------------------------------------------------------------------------
def fk(rig: ck.Rig, clip: ck.Clip, t: float) -> dict:
    """Each bone's pose as (R, offset) in rest space: p -> R p + offset (the export's convention)."""
    out: dict = {}
    for b in rig.bones:
        rdeg, loc = clip.sample(b.name, t)
        W = ck.euler(*rdeg)
        h = np.asarray(b.head)
        tl = h + loc - W @ h
        if b.parent:
            Rp, tp = out[b.parent]
            out[b.name] = (Rp @ W, Rp @ tl + tp)
        else:
            out[b.name] = (W, tl)
    return out


def skin(rig: ck.Rig, arrays: dict, pose: dict) -> np.ndarray:
    P, J, W = arrays["pos"], arrays["joints"], arrays["weights"]
    Rs = np.stack([pose[b.name][0] for b in rig.bones])
    ts = np.stack([pose[b.name][1] for b in rig.bones])
    out = np.zeros_like(P)
    for k in range(2):
        out += W[:, k:k + 1] * (np.einsum("nij,nj->ni", Rs[J[:, k]], P) + ts[J[:, k]])
    return out


def report(rig: ck.Rig, mesh: ck.Mesh, clips: list[ck.Clip]) -> None:
    arrays = mesh.arrays()
    rest = arrays["pos"]
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}")
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)} (+ hover {HOVER})")
    for c in ck.with_variety(clips):
        frames = max(int(round(c.length * ck.FPS)), 1)
        lo, hi, disp = np.inf, -np.inf, []
        for f in range(frames + 1):
            P = skin(rig, arrays, fk(rig, c, min(f / ck.FPS, c.length))) + np.array([0, HOVER, 0])
            lo, hi = min(lo, float(P[:, 1].min())), max(hi, float(P[:, 1].max()))
            disp.append(float(np.linalg.norm(P - rest - np.array([0, HOVER, 0]), axis=1).mean()))
        P = skin(rig, arrays, fk(rig, c, c.length)) + np.array([0, HOVER, 0])
        print(f"{c.name:7s} {c.length:.2f}s: y on stage {lo:+.3f}..{hi:.3f}; end {P[:, 1].min():+.3f}.."
              f"{P[:, 1].max():.3f}; peak {int(np.argmax(disp)) / ck.FPS:.2f}s")


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
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "gallery_ray"})
    print(f"gallery_ray: {info}")


if __name__ == "__main__":
    main()
