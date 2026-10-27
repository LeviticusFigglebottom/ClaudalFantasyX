"""Tannin archer, Ch10 Ossa Fen (M3-CRE-627): docs/kb/art/creatures/act2/tannin_archer.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/tannin_archer/build_tannin_archer.py -- \
    --out assets/creatures/tannin_archer/tannin_archer.glb

An archerfish grown to a dog's length in the tannin-dark water of the fen: a deep-bodied, flat-sided fish 1.1 m from
the tail's edge to the snout, lying half out of the water along a mangrove root, nose up, the mouth upturned and the
eyes large and set forward. Its one exaggeration is its size and the force of its jet (the jet is VFX). The back is
`deep_teal_shadow` going `abyss_navy` (lifted onto the albedo floor), the flanks `sand_cloth` crossed by six
`lacquer_black` bars, the belly `bone`, the eye `dusk_gold` round a black pupil, and the gill slit, the weak point, a
small `spawn_wound` line on the body slot's emission mask. The root it lies on is `timber_weathered` going
`tortoiseshell` where the tannin water has stained it.

y 0 is the fen's water. The root rises out of it along the fish's length (its ends dip under), and the fish's belly
rests on the root's crown.

Rig (10 bones): root (the root prop, never moves), `spine_0` (the head and fore-body, pivoting at the body's centre),
`spine_1`..`spine_4` (to the tail), `tail` (the caudal fin), `jaw`, `pec_l`/`pec_r`.

`python3 build_tannin_archer.py --report` prints the triangle count and per-clip skinned bounds (numpy, no export).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 6271
PAL = {k: ck.hexrgb(v) for k, v in {
    "deep_teal_shadow": "#0E4A55", "abyss_navy": "#061A2B", "sand_cloth": "#C9B48E", "lacquer_black": "#1D1916",
    "bone": "#E6DAC0", "dusk_gold": "#F2A64A", "spawn_wound": "#3FE0C8", "timber_weathered": "#7E6A55",
    "tortoiseshell": "#6B3A1E",
}.items()}
# The back: deep_teal_shadow going abyss_navy; abyss_navy alone is a shade under the albedo floor, so the dark end is
# lifted with deep_teal_shadow.
BACK_DARK = ck.mix(PAL["abyss_navy"], PAL["deep_teal_shadow"], 0.3)
BLACK = PAL["lacquer_black"]

PITCH = 11.0  # nose up, degrees: the fish lies along the root with its head raised to sight
AXIS_Y = 0.355  # the body's axis at its centre (the spine_0 pivot), over the root's crown
# Body stations along the fish's own axis (z forward): dorsal and ventral half-heights, half-width, centre offset.
SEC_Z = [-0.40, -0.34, -0.24, -0.10, 0.04, 0.18, 0.30, 0.40, 0.48, 0.535]
SEC_DU = [0.045, 0.06, 0.115, 0.158, 0.172, 0.165, 0.132, 0.09, 0.048, 0.012]
SEC_DV = [0.045, 0.066, 0.14, 0.198, 0.214, 0.196, 0.152, 0.098, 0.05, 0.012]
SEC_W = [0.024, 0.03, 0.054, 0.074, 0.081, 0.079, 0.069, 0.053, 0.032, 0.008]
SEC_YC = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.006, 0.018, 0.032, 0.042]
SEGS = 28
SPINE_Z = [0.535, 0.0, -0.13, -0.25, -0.34, -0.41]  # spine_0 spans the head to the centre, then four to the tail
SPINE = [f"spine_{i}" for i in range(5)]
BARS_Z = (0.335, 0.205, 0.075, -0.055, -0.18, -0.30)  # the archerfish's six bars, the first through the eye
GILL_Z = 0.265
EYE = np.array([0.048, 0.045, 0.385])  # local, the left eye (x mirrored for the right)
EYE_R = 0.034

PARTS: dict[str, tuple[int, int]] = {}


def place(p) -> np.ndarray:
    """The fish's own frame (axis on y 0, centre at z 0) to the model: pitched nose-up and raised onto the root."""
    p = np.atleast_2d(np.asarray(p, dtype=np.float64))
    return p @ ck.rot_x(-PITCH).T + np.array([0.0, AXIS_Y, 0.0])


def place1(p) -> tuple:
    return tuple(float(v) for v in place(p)[0])


def section(z):
    return (np.interp(z, SEC_Z, SEC_DU), np.interp(z, SEC_Z, SEC_DV), np.interp(z, SEC_Z, SEC_W),
            np.interp(z, SEC_Z, SEC_YC))


def orient(P: np.ndarray, T: np.ndarray, want) -> np.ndarray:
    """Flips the triangles whose face normal points against want(centroids)."""
    T = np.asarray(T, dtype=np.int64).copy()
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    bad = (fn * want(P[T].mean(axis=1))).sum(axis=1) < 0
    T[bad] = T[bad][:, ::-1]
    return T


def mark(name: str, mesh: ck.Mesh, start: int) -> None:
    lo, _hi = PARTS.get(name, (start, start))
    PARTS[name] = (min(lo, start), mesh.count)


def two_sided(mesh: ck.Mesh, P, T, slot, col, bones, n_hint, **kw) -> None:
    """A thin membrane: two copies a hair apart, each facing out along +-n_hint."""
    P = np.asarray(P, dtype=np.float64)
    n = np.asarray(n_hint, dtype=np.float64)
    for s in (1.0, -1.0):
        Ts = orient(P, T, lambda c, s=s: np.broadcast_to(s * n, c.shape))
        ck.finish(mesh, P + s * 0.0025 * n, Ts, slot, col, bones, **kw)


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.2, 0))
    rig.add("spine_0", place1((0, 0, SPINE_Z[1])), place1((0, 0, SPINE_Z[0])), "root")
    parent = "spine_0"
    for i in range(1, 5):
        rig.add(SPINE[i], place1((0, 0, SPINE_Z[i])), place1((0, 0, SPINE_Z[i + 1])), parent)
        parent = SPINE[i]
    rig.add("tail", place1((0, 0, -0.39)), place1((0, 0, -0.55)), "spine_4")
    rig.add("jaw", place1((0, -0.012, 0.445)), place1((0, 0.03, 0.555)), "spine_0")
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        rig.add(f"pec_{tag}", place1((s * 0.062, -0.07, 0.25)), place1((s * 0.13, -0.1, 0.13)), "spine_0")
    return rig


def body_skin(rig: ck.Rig):
    pts = place(np.array([(0.0, 0.0, z) for z in SPINE_Z]))
    return rig.chain(SPINE, pts)


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    zs = np.concatenate([np.linspace(-0.40, 0.30, 34), np.linspace(0.315, 0.535, 14)])
    K = len(zs)
    du, dv, w, yc = section(zs)
    a = np.arange(SEGS) * (2.0 * math.pi / SEGS)
    ca, sa = np.cos(a), np.sin(a)
    X = np.sign(ca) * np.abs(ca) ** 0.8  # a flat side: the archerfish is compressed
    L = np.zeros((K, SEGS, 3))
    L[..., 0] = w[:, None] * X[None]
    L[..., 1] = yc[:, None] + np.where(sa[None] >= 0, du[:, None], dv[:, None]) * sa[None]
    L[..., 2] = zs[:, None]
    L = L.reshape(-1, 3)
    T = ck.grid_tris(K, SEGS, True)
    L = np.vstack([L, [(0.0, 0.0, -0.405), (0.0, SEC_YC[-1], 0.545)]])
    caps = [(s, (s + 1) % SEGS, len(L) - 2) for s in range(SEGS)]
    r0 = (K - 1) * SEGS
    caps += [(r0 + s, r0 + (s + 1) % SEGS, len(L) - 1) for s in range(SEGS)]
    T = np.vstack([T, np.asarray(caps, dtype=np.int64)])
    zv = L[:, 2]
    sav = np.concatenate([np.tile(sa, K), [0.0, 0.0]])
    T = orient(L, T, lambda c: c - np.column_stack([np.zeros(len(c)), np.interp(c[:, 2], SEC_Z, SEC_YC),
                                                    np.clip(c[:, 2], -0.40, 0.535)]))
    # the gill cover's edge (the weak point: a thin slit), the mouth's line, a faint lateral line
    edge = GILL_Z + 0.035 * sav ** 2
    gill = np.exp(-((zv - edge) / 0.011) ** 2) * ck.smoothstep(0.75, 0.45, np.abs(sav))
    mouth = np.exp(-((L[:, 1] - np.interp(zv, SEC_Z, SEC_YC) + 0.004) / 0.006) ** 2) * ck.smoothstep(0.45, 0.52, zv)
    N = ck.weld_normals(L, ck.vertex_normals(L, T))
    L = L + N * (ck.fbm(L * 9.0, SEED) * 0.002 - 0.005 * gill - 0.004 * mouth)[:, None]

    # colour: dark back, sand flanks with six black bars, bone belly
    back = ck.smoothstep(0.35, 0.85, sav)
    col = ck.mix(PAL["sand_cloth"], PAL["deep_teal_shadow"], ck.smoothstep(0.2, 0.55, sav)[:, None])
    col = ck.mix(col, BACK_DARK, back[:, None])
    belly = ck.smoothstep(-0.35, -0.8, sav)
    col = ck.mix(col, PAL["bone"], (0.85 * belly)[:, None])
    bar = np.zeros(len(L))
    for k, z0 in enumerate(BARS_Z):
        half = 0.022 if k else 0.016
        lean = 0.02 * sav  # the bars lean back a little toward the belly
        wob = 0.006 * ck.fbm(L * 14.0, SEED + 3 + k)
        band = ck.smoothstep(half + 0.006, half - 0.004, np.abs(zv - z0 + lean + wob))
        reach = ck.smoothstep(-0.45, -0.15, sav)  # down from the back to below the mid-flank
        bar = np.maximum(bar, band * reach)
    col = ck.mix(col, BLACK, (0.92 * bar)[:, None])
    col = ck.mix(col, BLACK, (0.6 * mouth)[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.65, gill[:, None])
    wet = 0.85 - 0.25 * back
    start = mesh.count
    ck.finish(mesh, place(L), T, "body", col, body_skin(rig), wet=wet, cavity=np.clip(0.7 * gill + 0.5 * mouth, 0, 1),
              emission=gill, N=N @ ck.rot_x(-PITCH).T)
    mark("body", mesh, start)


def jaw_and_eyes(mesh: ck.Mesh, rig: ck.Rig) -> None:
    # the lower jaw: an upturned wedge under the snout, its tip just past the upper lip
    Pj, Tj = ck.ellipsoid((0.0, 0.0, 0.0), (0.028, 0.016, 0.058), 6, 12)
    Pj = Pj @ ck.rot_x(-14.0).T + np.array([0.0, 0.016, 0.5])
    ck.finish(mesh, place(Pj), Tj, "body", ck.mix(PAL["bone"], PAL["sand_cloth"], 0.4), rig.rigid("jaw"), wet=0.8)
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        c = EYE * np.array([s, 1.0, 1.0])
        Pe, Te = ck.ellipsoid((0, 0, 0), (EYE_R, EYE_R, EYE_R * 0.9), 8, 14)
        # the pupil looks forward and out: it is the cap facing (s 0.55, 0.15, 0.82)
        look = np.array([s * 0.55, 0.15, 0.82])
        look /= np.linalg.norm(look)
        d = (Pe / np.linalg.norm(Pe, axis=1, keepdims=True)) @ look
        pupil = ck.smoothstep(0.8, 0.86, d)
        iris = ck.smoothstep(0.05, 0.2, d)
        col = ck.mix(ck.mix(PAL["sand_cloth"], PAL["dusk_gold"], iris[:, None]), BLACK, pupil[:, None])
        ck.finish(mesh, place(Pe + c), Te, "eye", col, rig.rigid("spine_0"), wet=1.0)


def fins(mesh: ck.Mesh, rig: ck.Rig) -> None:
    skin = body_skin(rig)
    side = np.array([1.0, 0.0, 0.0]) @ ck.rot_x(-PITCH).T
    # the dorsal fin: set far back, spiny in front, its soft rear lobe reaching back over the tail
    n = 18
    zb = np.linspace(-0.04, -0.31, n)
    du, dv, _w, yc = section(zb)
    u = np.linspace(0.0, 1.0, n)
    h = 0.05 + 0.075 * np.sin(np.clip(u * 1.2, 0, 1) * math.pi * 0.9) + 0.03 * u
    base = np.column_stack([np.zeros(n), yc + du - 0.006, zb])
    top = base + np.column_stack([np.zeros(n), h, -0.05 - 0.07 * u])
    for which, (b, t) in (("dorsal", (base, top)),):
        P = np.vstack([b, (b + t) / 2, t])
        T = ck.grid_tris(3, n, False)
        tip = np.concatenate([np.zeros(n), np.full(n, 0.5), np.ones(n)])
        col = ck.mix(ck.mix(BACK_DARK, PAL["deep_teal_shadow"], 0.4), BLACK, (0.6 * tip)[:, None])
        start = mesh.count
        two_sided(mesh, place(P), T, "fin", col, skin, side, wet=0.7, cavity=0.15)
        mark(which, mesh, start)
    # the anal fin: under it, mirroring the dorsal's lobe, sand going black at the edge
    zb = np.linspace(-0.01, -0.33, n)
    du, dv, _w, yc = section(zb)
    h = 0.05 + 0.08 * np.sin(np.clip(u * 1.15, 0, 1) * math.pi * 0.9)
    base = np.column_stack([np.zeros(n), yc - dv + 0.006, zb])
    bot = base + np.column_stack([np.zeros(n), -h, -0.04 - 0.08 * u])
    P = np.vstack([base, (base + bot) / 2, bot])
    T = ck.grid_tris(3, n, False)
    edge = np.concatenate([np.zeros(n), np.full(n, 0.5), np.ones(n)])
    col = ck.mix(PAL["sand_cloth"], BLACK, (0.15 + 0.75 * edge)[:, None])
    start = mesh.count
    two_sided(mesh, place(P), T, "fin", col, skin, side, wet=0.8, cavity=0.15)
    mark("anal", mesh, start)
    # the caudal fin: a broad, slightly rounded fan
    m = 13
    ang = np.linspace(-1.0, 1.0, m)
    root = np.column_stack([np.zeros(m), ang * 0.038, np.full(m, -0.385)])
    rim = np.column_stack([np.zeros(m), ang * 0.15, -0.545 + 0.02 * (1 - ang ** 2)])
    P = np.vstack([root, root * 0.45 + rim * 0.55, rim])
    T = ck.grid_tris(3, m, False)
    edge = np.concatenate([np.zeros(m), np.full(m, 0.5), np.ones(m)])
    col = ck.mix(ck.mix(PAL["sand_cloth"], PAL["deep_teal_shadow"], 0.5), BLACK, (0.2 + 0.6 * edge)[:, None])
    start = mesh.count
    two_sided(mesh, place(P), T, "fin", col, rig.blend("spine_4", "tail", place1((0, 0, -0.37)),
                                                         place1((0, 0, -0.42))), side, wet=0.8, cavity=0.1)
    mark("tail", mesh, start)
    # the pectorals: small clear-edged fans behind the gill
    for s, tag in ((1.0, "l"), (-1.0, "r")):
        b = rig.bones[rig.index(f"pec_{tag}")]
        h0, h1 = np.asarray(b.head), np.asarray(b.tail)
        spread = np.array([0.0, -0.04, 0.0]) @ ck.rot_x(-PITCH).T
        out = np.array([s * 0.012, 0.0, 0.0])
        base = h0[None] + np.linspace(-0.25, 0.25, 5)[:, None] * spread[None]
        rim = ck.bezier([h1 - spread * 0.6, h1 + spread * 0.3 + out, h1 + spread * 1.1], 5)
        P = np.vstack([base, rim])
        T = ck.grid_tris(2, 5, False)
        col = ck.mix(PAL["sand_cloth"], PAL["bone"], 0.3)
        nrm = np.cross(h1 - h0, spread)
        start = mesh.count
        two_sided(mesh, P, T, "fin", np.tile(col, (len(P), 1)), rig.rigid(f"pec_{tag}"), nrm / np.linalg.norm(nrm),
                  wet=0.8)
        mark(f"pec_{tag}", mesh, start)


def mangrove_root(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The root it lies on: out of the water behind it, arching under its belly, down into the water ahead."""
    path = ck.bezier([(0.1, -0.03, -0.72), (0.02, 0.17, -0.3), (-0.01, 0.15, 0.2), (-0.12, -0.03, 0.66)], 26)
    u = np.linspace(0, 1, len(path))
    rad = 0.058 + 0.012 * np.sin(u * math.pi) + 0.006 * np.sin(u * 23.0)
    P, T = ck.tube(path, rad, 12, cap_start=True, cap_end=True, squash=0.85)
    bark = ck.fbm(P * 18.0, SEED + 9)
    col = ck.mix(PAL["timber_weathered"], PAL["tortoiseshell"], ck.smoothstep(0.08, -0.02, P[:, 1])[:, None])
    col = ck.mix(col, PAL["tortoiseshell"], (0.35 * ck.smoothstep(0.0, 0.4, bark))[:, None])
    wet = ck.smoothstep(0.1, 0.0, P[:, 1])
    start = mesh.count
    ck.finish(mesh, P, T, "root", col, rig.rigid("root"), wet=wet, cavity=0.3 * ck.smoothstep(0.0, 0.5, bark))
    # a knee: a short side-shoot rising off the root beside the tail
    knee = ck.bezier([(0.05, 0.12, -0.42), (0.16, 0.2, -0.5), (0.24, 0.12, -0.6), (0.3, -0.03, -0.62)], 10)
    Pk, Tk = ck.tube(knee, np.linspace(0.035, 0.028, len(knee)), 8, squash=0.9)
    colk = ck.mix(PAL["timber_weathered"], PAL["tortoiseshell"], ck.smoothstep(0.08, -0.02, Pk[:, 1])[:, None])
    ck.finish(mesh, Pk, Tk, "root", colk, rig.rigid("root"), wet=ck.smoothstep(0.1, 0.0, Pk[:, 1]), cavity=0.2)
    mark("root", mesh, start)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    mesh = ck.Mesh("tannin_archer")
    body(mesh, rig)
    jaw_and_eyes(mesh, rig)
    fins(mesh, rig)
    mangrove_root(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 2.4
ATTACK_SEC = 1.2
ATTACK_CONTACT = 0.55
CAST_SEC = 1.8
CAST_CONTACT = 0.9
HIT_SEC = 0.5
KO_SEC = 1.8


def build_idle() -> ck.Clip:
    c = ck.Clip("idle", IDLE_SEC, loop=True)  # it holds on the root, sculling, the head tracking a target
    c.wave("pec_l", amp_rot=(0, 24.0, 0), cycles=2)
    c.wave("pec_r", amp_rot=(0, -24.0, 0), cycles=2)
    c.wave("spine_0", amp_rot=(1.5, 3.5, 0), cycles=1, phase=0.4)
    for i, b in enumerate(SPINE[2:], 2):
        c.wave(b, amp_rot=(0, 2.0 + 1.5 * i, 0), cycles=2, phase=-0.8 * i)
    c.wave("tail", amp_rot=(0, 8.0, 0), cycles=2, phase=-4.0)
    c.wave("jaw", amp_rot=(2.0, 0, 0), base_rot=(2.0, 0, 0), cycles=2)
    return c


def build_attack() -> ck.Clip:
    c = ck.Clip("attack", ATTACK_SEC)  # it rises off the root, sights along its mouth, and spits
    for t, rx, ly, lz, jaw, pec, tail in ((0.0, 0, 0, 0, 0, 0, 0), (0.3, -10.0, 0.05, 0.0, 0, 28.0, -6.0),
                                          (0.47, -12.0, 0.06, 0.01, 0, 30.0, -4.0),
                                          (ATTACK_CONTACT, -9.0, 0.055, -0.025, 14.0, 34.0, 10.0),
                                          (0.68, -7.0, 0.04, -0.035, 5.0, 20.0, 4.0), (ATTACK_SEC, 0, 0, 0, 0, 0, 0)):
        c.key("spine_0", t, (rx, 0, 0), (0, ly, lz))
        c.key("jaw", t, (jaw, 0, 0))
        c.key("pec_l", t, (0, pec, 0))
        c.key("pec_r", t, (0, -pec, 0))
        c.key("tail", t, (0, tail, 0))
        c.key("spine_3", t, (0, tail * 0.5, 0))
    return c


def build_cast() -> ck.Clip:
    c = ck.Clip("cast", CAST_SEC)  # the long aimed jet at the back row: nose high, held, the jaw open
    for t, rx, ry, ly, jaw in ((0.0, 0, 0, 0, 0), (0.45, -19.0, 1.0, 0.08, 0), (0.75, -21.0, -1.0, 0.085, 6.0),
                               (CAST_CONTACT, -20.0, 1.0, 0.085, 13.0), (1.15, -21.0, -1.0, 0.085, 12.0),
                               (1.35, -15.0, 0.0, 0.06, 3.0), (CAST_SEC, 0, 0, 0, 0)):
        c.key("spine_0", t, (rx, ry, 0), (0, ly, -0.02 if 0.8 < t < 1.3 else 0.0))
        c.key("jaw", t, (jaw, 0, 0))
        pec = 30.0 if 0.3 < t < 1.4 else 0.0
        c.key("pec_l", t, (0, pec, 0))
        c.key("pec_r", t, (0, -pec, 0))
        c.key("tail", t, (0, 6.0 if 0.8 < t < 1.3 else 0.0, 0))
    return c


def build_hit() -> ck.Clip:
    c = ck.Clip("hit", HIT_SEC)  # it flinches, rolling away, and its tail slaps the water
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.24, 0.45), (HIT_SEC, 0.0)):
        c.key("spine_0", t, (5.0 * s, -4.0 * s, 15.0 * s), (0, 0.035 * s, -0.04 * s))
        c.key("spine_3", t, (0, 10.0 * s, 0))
        c.key("spine_4", t, (0, 12.0 * s, 0))
        c.key("tail", t, (0, 22.0 * s, 0))
        c.key("jaw", t, (8.0 * s, 0, 0))
        c.key("pec_l", t, (0, 30.0 * s, 0))
        c.key("pec_r", t, (0, -30.0 * s, 0))
    return c


KO_ROLL = -88.0
KO_OFF = (0.3, -0.255, 0.02)


def build_ko() -> ck.Clip:
    c = ck.Clip("ko", KO_SEC)  # it jerks, rolls off the root onto its side and settles into the water
    for t, rx, rz, loc, tail, pec in ((0.0, 0, 0, (0, 0, 0), 0, 0), (0.22, -7.0, 8.0, (0, 0.04, 0), 18.0, 25.0),
                                      (0.6, 2.0, -45.0, (0.14, -0.02, 0.01), -10.0, 0.0),
                                      (1.0, 9.0, KO_ROLL + 4.0, (KO_OFF[0], KO_OFF[1] + 0.02, KO_OFF[2]), 6.0, -10.0),
                                      (1.35, PITCH, KO_ROLL, KO_OFF, 0.0, -14.0), (KO_SEC, PITCH, KO_ROLL, KO_OFF, 0.0,
                                                                                  -14.0)):
        c.key("spine_0", t, (rx, 0, rz), loc)
        c.key("tail", t, (0, tail, 0))
        c.key("spine_4", t, (0, tail * 0.4, 0))
        c.key("pec_l", t, (0, pec, 0))
        c.key("pec_r", t, (0, -pec, 0))
        c.key("jaw", t, (10.0 if t >= 1.0 else 0.0, 0, 0))
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
    fish = np.arange(0, PARTS["root"][0])
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}")
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)}; "
          f"fish y {rest[fish, 1].min():.3f}..{rest[fish, 1].max():.3f}")
    for c in ck.with_variety(clips):
        frames = max(int(round(c.length * ck.FPS)), 1)
        lo, hi, disp = np.inf, -np.inf, []
        for f in range(frames + 1):
            P = skin(rig, arrays, fk(rig, c, min(f / ck.FPS, c.length)))
            lo, hi = min(lo, float(P[fish, 1].min())), max(hi, float(P[fish, 1].max()))
            disp.append(float(np.linalg.norm(P - rest, axis=1).mean()))
        P = skin(rig, arrays, fk(rig, c, c.length))
        print(f"{c.name:7s} {c.length:.2f}s: fish y {lo:+.3f}..{hi:.3f}; end fish y {P[fish, 1].min():+.3f}.."
              f"{P[fish, 1].max():.3f}; peak {int(np.argmax(disp)) / ck.FPS:.2f}s")


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
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "tannin_archer"})
    print(f"tannin_archer: {info}")


if __name__ == "__main__":
    main()
