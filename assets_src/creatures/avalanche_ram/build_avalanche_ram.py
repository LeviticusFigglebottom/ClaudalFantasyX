"""The Avalanche Ram, the Ch12 boss (M3-CRE-624): docs/kb/art/creatures/act2/avalanche_ram.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/avalanche_ram/build_avalanche_ram.py -- \
    --out assets/creatures/avalanche_ram/avalanche_ram.glb

An Ullari woolback that drank where the seep runs and grew: a long-necked, deep-chested pack animal 4 m long with
its head at 3 m. Its undyed fleece (`sand_cloth`, gone grey to `overcast_slate` in the shadows) has matted into
plates of ice and wool and hangs in six heavy frozen chains of locks to the knees, a few uneven `salt_glass`
icicles hanging past their tips, frost under the jaw and ice along the belly. Where the fleece parts the seep's cold
`spawn_wound` light shows through (the weak points). The head is a camelid's (M3-CRE-635): long and narrow, a soft
rounded muzzle in the coat's colour, `laterite` darkened only at the nose and the lips, eyes at the sides under a
soft brow, long upright ears and a woolly cap; the legs are darkened `laterite` too. A faded `lacquer_red`
herd-cord with three knots is still tied round its slim neck. Not horned, not demonic: the Ullari's own animal,
too big.

Rig: root, body (the carrier the legs hang from), spine 5, neck 5, head, jaw, four legs of 3 and six fleece-lock
chains of 2. The legs are posed by a deterministic grid solve in each leg's plane (`solve_leg`), so a planted foot
stays at y 0 while the body moves, and the KO folds them under the body without going through the ground.

Run without Blender (`python3 build_avalanche_ram.py --report`) to print the triangle count and, per clip, the
skinned bounds, the head height, the feet at the end and the peak time (numpy skinning, no export).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 6212
PAL = {k: ck.hexrgb(v) for k, v in {
    "sand_cloth": "#C9B48E", "overcast_slate": "#6F7E8E", "salt_glass": "#BFE6E0", "laterite": "#A8573A",
    "spawn_wound": "#3FE0C8", "glimmer_held": "#7FC6D9", "lacquer_red": "#B3261E", "lacquer_black": "#1D1916",
}.items()}
HIDE = PAL["laterite"] * 0.52  # the muzzle and legs: laterite, darkened
CORD = ck.mix(PAL["lacquer_red"], PAL["sand_cloth"], 0.35)  # the herd-cord's red, faded
# Coordinates this close to 0 are the midline's, snapped to 0 (and -0.0 to 0.0): numpy's SIMD path leaves them at
# +-1e-17 on one host and 0 on another, which moved the head's midline bits between hosts (big14 gate).
MIDLINE_EPS = 1e-9

# The barrel (rump to chest front along z), the spine through it and the neck rising off the chest
BODY_Z = (-1.74, 1.12)
BARREL_U = np.array([0.0, 0.22, 0.5, 0.78, 1.0])
BARREL_CY = np.array([1.52, 1.5, 1.46, 1.46, 1.48])  # the barrel's centre height
BARREL_A = np.array([0.5, 0.56, 0.58, 0.56, 0.48])  # half-width
BARREL_UP = np.array([0.5, 0.54, 0.54, 0.58, 0.5])  # top half-height
BARREL_DN = np.array([0.5, 0.56, 0.62, 0.72, 0.58])  # bottom half-height: the deep chest
BARREL_RINGS = 42
BARREL_SEGS = 40
SPINE = np.array([(0, 1.54, -1.38), (0, 1.54, -0.84), (0, 1.54, -0.3), (0, 1.56, 0.2), (0, 1.6, 0.56), (0, 1.66, 0.84)])
BODY_PIVOT = np.array([0.0, 1.46, -0.3])  # the body bone's head: the KO pitches the body about it
NECK_CTRL = np.array([(0, 1.42, 0.5), (0, 2.2, 0.86), (0, 2.66, 1.1), (0, 2.82, 1.4)])
# (u, radius) knots: thick where it leaves the chest, slim up the throat (M3-CRE-635: a camelid's neck)
NECK_R = ((0.0, 0.2, 0.4, 1.0), (0.36, 0.22, 0.16, 0.13))
NECK_SHAG = 0.75  # the neck's coat, as a share of the body's
NECK_RINGS = 24
NECK_SEGS = 22
# The rig's head points (the head and jaw bones hang off them; unchanged by the M3-CRE-635 re-model)
HEAD_C = np.array([0.0, 2.87, 1.54])
MUZZLE_TIP = np.array([0.0, 2.71, 2.02])
# The head (M3-CRE-635): a camelid's, long and narrow, from the poll to the end of the soft muzzle, its sections as
# (u along it, half-width, height above its axis, depth below it): the cheeks deepest, the muzzle slim and rounded
HEAD_BACK = np.array([0.0, 2.95, 1.35])
NOSE = np.array([0.0, 2.69, 2.05])
HEAD_SEC = np.array([(0.0, 0.1, 0.1, 0.12), (0.1, 0.118, 0.122, 0.16), (0.24, 0.124, 0.118, 0.182),
                     (0.38, 0.112, 0.1, 0.16), (0.54, 0.096, 0.084, 0.118), (0.72, 0.086, 0.078, 0.098),
                     (0.88, 0.09, 0.08, 0.096), (1.0, 0.084, 0.072, 0.088)])
HEAD_ROUND = (0.07, 0.9)  # the poll and the muzzle's end round off before u = 0 and after this u
HEAD_SEGS = 18
EYE_U, EYE_A = 0.3, 64.0  # the eyes: set at the sides (degrees round from the top) under a soft brow
EAR_U = 0.1
JAW_PATH = ((0.0, 2.74, 1.6), (0.0, 2.7, 1.8), (0.0, 2.64, 1.93), (0.0, 2.625, 1.98))
JAW_R = (0.064, 0.058, 0.048, 0.036)
# Icicles (M3-CRE-635: few and uneven, never a row of even spikes): a few per lock chain at strands' tips, two
# clumps under the belly ((barrel u, angle off the bottom, count)) and two under the jaw's beard
LOCK_ICE = (1, 3)
LOCK_ICE_LEN = (0.14, 0.32)
LOCK_ICE_PAST = (0.05, 0.11)  # how far past its strand's tip
BELLY_ICE = ((0.4, 0.2, 2), (0.6, -0.25, 3))
# Legs: (attach, knee, fetlock, toe) per side; the hind leg's stifle forward and hock back
FRONT = ((0.34, 1.14, 0.6), (0.36, 0.72, 0.64), (0.36, 0.22, 0.6), (0.36, 0.0, 0.7))
HIND = ((0.36, 1.18, -1.12), (0.38, 0.86, -0.92), (0.38, 0.5, -1.36), (0.38, 0.0, -1.22))
LEGS = ("fl", "fr", "bl", "br")
LEG_RINGS = 6  # per bone
LEG_SEGS = 10
HOOF_TOP = 0.13
# Six fleece-lock chains (side, barrel u, parent spine bone): shoulder, flank, haunch on each side
LOCKS = ((1.0, 0.76, "spine3"), (1.0, 0.5, "spine2"), (1.0, 0.24, "spine0"),
         (-1.0, 0.76, "spine3"), (-1.0, 0.5, "spine2"), (-1.0, 0.24, "spine0"))
STRANDS = 9  # per chain
BIB = 7  # locks down the chest front
STRAND_TH = (118.0, 152.0)  # where a lock leaves the barrel (degrees from the top)
TIP_Y = (0.56, 0.84)  # to the knees, uneven
LOCK_JOINT_Y = (0.9, 0.6)  # a chain's two bone tails
# The partings (weak points): (u0, th0, u1, th1) on the barrel, th in degrees from the top (+ is the +x side)
PARTINGS = ((0.74, 55.0, 0.69, 100.0), (0.5, 44.0, 0.46, 106.0), (0.24, 50.0, 0.27, 96.0),
            (0.72, -60.0, 0.77, -102.0), (0.47, -42.0, 0.52, -100.0), (0.26, -55.0, 0.21, -92.0),
            (0.81, 10.0, 0.63, -6.0))
PARTING_W = 0.07  # the fleece's groove either side of a parting


# ---------------------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------------------
def finish(mesh: ck.Mesh, P, T, *args, **kw) -> int:
    """ck.finish with the midline snapped to 0 (MIDLINE_EPS), so the build is byte-identical on every host."""
    P = np.asarray(P, dtype=np.float64)
    return ck.finish(mesh, np.where(np.abs(P) < MIDLINE_EPS, 0.0, P) + 0.0, T, *args, **kw)


def leg_joints(name: str) -> np.ndarray:
    pts = np.array(FRONT if name[0] == "f" else HIND, dtype=np.float64)
    if name[1] == "r":
        pts[:, 0] *= -1.0
    return pts


def outward(P: np.ndarray, T: np.ndarray, centre_of) -> np.ndarray:
    """T wound so its faces point away from centre_of(P) (the part's axis), whichever way it was built."""
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    c = P[T].mean(axis=1)
    return T if float((fn * (c - centre_of(c))).sum()) >= 0.0 else ck.flip(T)


def fleece_colour(P: np.ndarray, down: np.ndarray, seed: int) -> tuple:
    """Undyed wool gone grey: sand_cloth where the light falls, overcast_slate in the shadows and the lock furrows,
    and plates of salt_glass ice matted into the lower coat. `down` is 0 on top .. 1 underneath.
    Returns (colour, wet, cavity)."""
    n = ck.fbm(P * 2.2, seed)
    fine = ck.fbm(P * 7.0, seed + 1)
    shade = np.clip(0.18 + 0.55 * down + 0.3 * n + 0.15 * fine, 0.0, 0.85)
    col = ck.mix(PAL["sand_cloth"], PAL["overcast_slate"], shade[:, None])
    ice = ck.smoothstep(0.08, 0.3, ck.fbm(P * 1.3, seed + 2)) * ck.smoothstep(0.35, 0.75, down)
    col = ck.mix(col, PAL["salt_glass"] * 0.94, (0.8 * ice)[:, None])
    wet = 0.5 * ice
    cavity = np.clip(0.25 + 0.35 * down - 0.4 * fine, 0.0, 0.8) * (1.0 - ice)
    return col, wet, cavity


def loop_tube(loop: np.ndarray, radius: float, segs: int) -> tuple[np.ndarray, np.ndarray]:
    """A closed ring of tube round the loop (K, 3): ring k at loop[k], the last joined to the first."""
    K = len(loop)
    tan = np.roll(loop, -1, axis=0) - np.roll(loop, 1, axis=0)
    tan /= np.linalg.norm(tan, axis=1, keepdims=True)
    nrm = loop - loop.mean(axis=0)
    nrm -= (nrm * tan).sum(axis=1, keepdims=True) * tan
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
    bin_ = np.cross(tan, nrm)
    a = np.arange(segs) * (2.0 * math.pi / segs)
    P = np.vstack([loop[k] + radius * (np.outer(np.cos(a), nrm[k]) + np.outer(np.sin(a), bin_[k])) for k in range(K)])
    T = ck.grid_tris(K + 1, segs, True)
    T = np.where(T >= K * segs, T - K * segs, T)  # the last row of bands joins ring K-1 back to ring 0
    return P, outward(P, T, lambda c: _nearest(loop, c))


def _nearest(path: np.ndarray, c: np.ndarray) -> np.ndarray:
    """For each point of c, the nearest point of the polyline's vertices (a tube's axis)."""
    d = np.linalg.norm(c[:, None, :] - path[None, :, :], axis=2)
    return path[np.argmin(d, axis=1)]


def icicle(mesh: ck.Mesh, top: np.ndarray, length: float, radius: float, bones, segs: int = 5,
           lean: tuple = (0.0, 0.0), waist: float = 0.55) -> None:
    """An icicle hanging from `top`: `lean` (x, z degrees) tips it off the vertical, `waist` its girth halfway."""
    prof = [(0.0, 0.03), (radius, 0.0), (radius * waist, -length * 0.45), (0.0, -length)]
    P, T = ck.lathe(prof, segs)
    P = ck.transform(P, ck.euler(lean[0], 0.0, lean[1])) + top
    tip = ck.smoothstep(0.0, -length, P[:, 1] - top[1])
    col = ck.mix(PAL["salt_glass"] * 0.9, PAL["salt_glass"], tip[:, None])
    finish(mesh, P, T, "ice", col, bones, wet=0.8, cavity=0.05)


# ---------------------------------------------------------------------------------------------
# The barrel: a deep-chested body with a shaggy coat, grooved where the fleece parts
# ---------------------------------------------------------------------------------------------
def barrel_base(u: np.ndarray, th: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The skin under the coat at (u along the body, th radians from the top): (P, section normal, down 0..1)."""
    u = np.asarray(u, dtype=np.float64)
    th = np.asarray(th, dtype=np.float64)
    env = np.sin(math.pi * np.clip(u, 0.0, 1.0)) ** 0.32
    a = np.interp(u, BARREL_U, BARREL_A) * env
    up = np.interp(u, BARREL_U, BARREL_UP) * env
    dn = np.interp(u, BARREL_U, BARREL_DN) * env
    c = np.cos(th)
    b = ck.mix(dn, up, ck.smoothstep(-0.25, 0.25, c))
    cy = np.interp(u, BARREL_U, BARREL_CY)
    z = BODY_Z[0] + (BODY_Z[1] - BODY_Z[0]) * u
    P = np.column_stack([a * np.sin(th), cy + b * c, z])
    n = np.column_stack([np.sin(th) / np.maximum(a, 1e-3), c / np.maximum(b, 1e-3), np.zeros_like(u)])
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    down = ck.smoothstep(0.6, -0.9, c)
    return P, n, down


def parting_paths() -> list[np.ndarray]:
    """Each parting as (u, th radians) samples along a jagged line."""
    rng = np.random.default_rng(SEED + 1)
    out = []
    for u0, t0, u1, t1 in PARTINGS:
        s = np.linspace(0.0, 1.0, 26)
        ph = rng.uniform(0.0, 6.0)
        u = u0 + (u1 - u0) * s + 0.012 * np.sin(s * 11.0 + ph) + 0.006 * np.sin(s * 29.0 + 2 * ph)
        th = np.radians(t0 + (t1 - t0) * s) + 0.03 * np.sin(s * 7.0 + ph)
        out.append(np.column_stack([u, th]))
    return out


def groove(Pbase: np.ndarray, paths: list[np.ndarray]) -> np.ndarray:
    """0..1: how far the fleece is parted at each base point (1 on a parting's line)."""
    g = np.zeros(len(Pbase))
    for path in paths:
        q, _, _ = barrel_base(path[:, 0], path[:, 1])
        d = np.min(np.linalg.norm(Pbase[:, None, :] - q[None, :, :], axis=2), axis=1)
        g = np.maximum(g, np.exp(-(d / PARTING_W) ** 2))
    return g


def coat_depth(Pbase: np.ndarray, th: np.ndarray, down: np.ndarray, seed: int) -> np.ndarray:
    """The coat's thickness over the skin: heavy, shaggier underneath, furrowed into vertical locks."""
    # hanging locks: the furrows run down whichever way the coat faces (a function of x and z only)
    furrow = np.abs(np.sin(Pbase[:, 2] * 11.0 + np.abs(Pbase[:, 0]) * 9.0 + 2.2 * ck.fbm(Pbase * 0.9, seed + 3)))
    return 0.07 + 0.05 * ck.fbm(Pbase * 1.8, seed + 4) + (0.03 + 0.04 * down) * furrow


def barrel_surface(u, th, paths, lift: float = 0.0) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """The coat's surface (P, normal, down, groove): `lift` metres above it where the fleece parts."""
    Pb, n, down = barrel_base(u, th)
    g = groove(Pb, paths)
    d = coat_depth(Pb, th, down, SEED) * (1.0 - g) + 0.006 + lift
    P = Pb + n * d[:, None]
    env = np.sin(math.pi * np.clip(u, 0.0, 1.0)) ** 0.32
    P[:, 1] -= 0.09 * ck.smoothstep(-0.1, -0.9, np.cos(th)) * env  # the coat hangs heavy underneath
    return P, n, down, g


def spine_skin(rig: ck.Rig):
    return rig.chain([f"spine{k}" for k in range(5)], SPINE)


def barrel(mesh: ck.Mesh, rig: ck.Rig, paths: list[np.ndarray]) -> None:
    us = np.linspace(0.012, 0.988, BARREL_RINGS)
    ths = np.arange(BARREL_SEGS) * (2.0 * math.pi / BARREL_SEGS)
    U, TH = np.meshgrid(us, ths, indexing="ij")
    P, n, down, g = barrel_surface(U.ravel(), TH.ravel(), paths)
    T = ck.grid_tris(BARREL_RINGS, BARREL_SEGS, True)
    ends = []
    for u, row in ((0.0, 0), (1.0, BARREL_RINGS - 1)):  # pole caps at the rump and the chest front
        pole, _, _ = barrel_base(np.array([u]), np.array([0.0]))
        pole[0, 2] += -0.03 if u == 0.0 else 0.03
        idx = len(P) + len(ends)
        ends.append(pole[0])
        r0 = row * BARREL_SEGS
        ring = [(r0 + s, idx, r0 + (s + 1) % BARREL_SEGS) for s in range(BARREL_SEGS)]
        T = np.vstack([T, np.asarray(ring, dtype=np.int64)])
    P = np.vstack([P, np.asarray(ends)])
    down = np.concatenate([down, [0.3, 0.3]])
    g = np.concatenate([g, [0.0, 0.0]])
    T = outward(P, T, lambda c: np.column_stack([np.zeros(len(c)), np.interp(c[:, 2], BODY_Z, BARREL_CY[[0, -1]]),
                                                 c[:, 2]]))
    col, wet, cav = fleece_colour(P, down, SEED + 10)
    lip = ck.smoothstep(0.25, 0.9, g)  # the parted wool's lips: shadowed, catching the seep's light
    col = ck.mix(col, ck.mix(PAL["overcast_slate"] * 0.7, PAL["glimmer_held"] * 0.75, 0.35), (0.8 * lip)[:, None])
    finish(mesh, P, T, "fleece", col, spine_skin(rig), wet=wet * (1.0 - lip), cavity=np.maximum(cav, 0.5 * lip))


def partings(mesh: ck.Mesh, rig: ck.Rig, paths: list[np.ndarray]) -> None:
    """The weak points: the seep's light in each parting, a strip just proud of the parted coat (a bright core
    between shadowed lips), dimming where the fleece closes over it."""
    for k, path in enumerate(paths):
        rows = len(path)
        P, n, _, _ = barrel_surface(path[:, 0], path[:, 1], paths, lift=0.014)
        tang = np.gradient(P, axis=0)
        side = np.cross(n, tang)
        side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-9)
        width = (0.045 * np.sin(np.linspace(0.12, math.pi - 0.12, rows)) ** 0.6
                 * (1.0 + 0.3 * np.sin(np.arange(rows) * 0.9 + k)))
        S = np.stack([P - side * width[:, None], P + n * 0.006, P + side * width[:, None]], axis=1).reshape(-1, 3)
        N = np.repeat(n, 3, axis=0)
        T = ck.grid_tris(rows, 3, False)
        fn = np.cross(S[T[:, 1]] - S[T[:, 0]], S[T[:, 2]] - S[T[:, 0]])
        T = T if float((fn * N[T[:, 0]]).sum()) > 0.0 else ck.flip(T)
        along = np.column_stack([np.arange(rows) * 0.35, np.full(rows, k * 3.1), np.zeros(rows)])
        closed = ck.smoothstep(0.1, 0.3, ck.fbm(along, SEED + 20))
        glow = np.tile([0.15, 1.0, 0.15], rows) * np.repeat(1.0 - 0.8 * closed, 3)
        col = ck.mix(np.tile(PAL["overcast_slate"] * 0.6, (len(S), 1)), np.tile(PAL["spawn_wound"] * 0.65, (len(S), 1)),
                     glow[:, None])
        finish(mesh, S, T, "fleece", col, spine_skin(rig), cavity=0.0, emission=glow, N=N)


def belly_ice(mesh: ck.Mesh, rig: ck.Rig, paths: list[np.ndarray]) -> None:
    """A few icicles in two uneven clumps under the belly (M3-CRE-635: not a row: a row of even spikes reads as
    teeth)."""
    rng = np.random.default_rng(SEED + 30)
    for u_c, th_c, n in BELLY_ICE:
        for _ in range(n):
            u = u_c + rng.uniform(-0.05, 0.05)
            th = math.pi + th_c + rng.uniform(-0.18, 0.18)
            P, _, _, _ = barrel_surface(np.array([u]), np.array([th]), paths)
            icicle(mesh, P[0] + np.array([0.0, 0.03, 0.0]), rng.uniform(0.05, 0.16), rng.uniform(0.022, 0.04),
                   spine_skin(rig), lean=(rng.uniform(-9.0, 9.0), rng.uniform(-9.0, 9.0)), waist=rng.uniform(0.4, 0.7))


# ---------------------------------------------------------------------------------------------
# Neck, head, the herd-cord
# ---------------------------------------------------------------------------------------------
def neck_path(n: int) -> np.ndarray:
    dense = ck.bezier(NECK_CTRL, 400)
    acc = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(dense, axis=0), axis=1))])
    s = np.linspace(0.0, acc[-1], n)
    return np.column_stack([np.interp(s, acc, dense[:, k]) for k in range(3)])


def neck_joints() -> np.ndarray:
    return neck_path(6)


def neck_skin(rig: ck.Rig):
    pts = np.vstack([SPINE[3][None], neck_joints()])
    return rig.chain(["spine4", "neck0", "neck1", "neck2", "neck3", "neck4"], pts)


def neck(mesh: ck.Mesh, rig: ck.Rig) -> None:
    path = neck_path(NECK_RINGS)
    u = np.linspace(0.0, 1.0, NECK_RINGS)
    rad = np.interp(u, NECK_R[0], NECK_R[1])
    P, T = ck.tube(path, rad, NECK_SEGS, cap_start=True, cap_end=False, squash=0.78)
    centre = np.concatenate([np.repeat(path, NECK_SEGS, axis=0), path[:1]])
    radial = P - centre
    radial /= np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-9)
    down = ck.smoothstep(0.3, -0.8, radial[:, 1])
    th = np.arctan2(radial[:, 0], radial[:, 1])
    along = np.concatenate([np.repeat(u, NECK_SEGS), [0.0]])
    shag = NECK_SHAG * coat_depth(P, th, down, SEED + 40) + 0.06 * down * ck.smoothstep(0.05, 0.3, along)
    P = P + radial * shag[:, None]  # the mane hangs heavier under the throat
    col, wet, cav = fleece_colour(P, down, SEED + 41)
    finish(mesh, P, T, "fleece", col, neck_skin(rig), wet=wet, cavity=cav)


def neck_surface(u: float, ang: np.ndarray, out: float) -> np.ndarray:
    """Points on the neck's coat at fraction u, angle `ang` round it (0 = up), `out` metres proud."""
    path = neck_path(201)
    k = int(round(u * 200))
    tan, nrm, bin_ = ck.frames_along(path)
    r = float(np.interp(u, NECK_R[0], NECK_R[1]))
    radial = np.outer(np.cos(ang), nrm[k]) + 0.78 * np.outer(np.sin(ang), bin_[k])
    unit = radial / np.linalg.norm(radial, axis=1, keepdims=True)
    return path[k] + radial * r + unit * (0.11 * NECK_SHAG + out)


def herd_cord(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The faded red herd-cord, tied round the lower neck, three knots and a frayed end: the small, human detail."""
    ang = np.linspace(0.0, 2.0 * math.pi, 49)[:-1]
    ring = np.vstack([neck_surface(0.34 + 0.035 * math.cos(a), np.array([a]), 0.01) for a in ang])
    P, T = loop_tube(ring, 0.032, 6)
    fade = 0.85 + 0.15 * ck.fbm(P * 9.0, SEED + 50)
    skin = neck_skin(rig)
    finish(mesh, P, T, "hide", CORD * fade[:, None], skin, cavity=0.3)
    for a in (2.2, 2.75, 3.35):  # three knots down the throat side
        c = neck_surface(0.34 + 0.035 * math.cos(a), np.array([a]), 0.03)[0]
        Pk, Tk = ck.ellipsoid(c, (0.055, 0.05, 0.055), 5, 8)
        finish(mesh, Pk, Tk, "hide", CORD * 0.82, skin, cavity=0.4)
    knot = neck_surface(0.34 + 0.035 * math.cos(2.75), np.array([2.75]), 0.05)[0]
    rng = np.random.default_rng(SEED + 51)
    for k in range(3):  # the frayed end, hanging
        sway = np.array([rng.uniform(-0.05, 0.05), 0.0, rng.uniform(0.0, 0.06)])
        length = rng.uniform(0.24, 0.36)
        fp = ck.bezier([knot, knot + np.array([0.0, -length * 0.5, 0.02]) + sway * 0.5,
                        knot + np.array([0.0, -length, 0.0]) + sway], 6)
        Pf, Tf = ck.tube(fp, np.linspace(0.016, 0.005, 6), 5)
        finish(mesh, Pf, Tf, "hide", ck.mix(CORD * 0.9, PAL["sand_cloth"] * 0.85, 0.25), rig.rigid("neck1"),
                  cavity=0.2)


def head_frame() -> tuple[np.ndarray, np.ndarray, float]:
    """The head's axis (poll to nose), the up direction across it and its length."""
    d = NOSE - HEAD_BACK
    length = float(np.linalg.norm(d))
    d = d / length
    up = np.array([0.0, d[2], -d[1]])
    return d, up / np.linalg.norm(up), length


def head_surface(u, a, out: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """Points on the head at u (0 the poll .. 1 the nose) and angle a (radians round the axis, 0 up, + toward +x),
    `out` metres proud of it: (P, the radial direction)."""
    u = np.asarray(u, dtype=np.float64)
    a = np.asarray(a, dtype=np.float64)
    d, up, length = head_frame()
    w, t, b = (np.interp(u, HEAD_SEC[:, 0], HEAD_SEC[:, k]) for k in (1, 2, 3))
    back = np.clip((HEAD_ROUND[0] - u) / HEAD_ROUND[0], 0.0, 1.0)
    front = np.clip((u - HEAD_ROUND[1]) / (1.0 - HEAD_ROUND[1]), 0.0, 1.0)
    rnd = np.sqrt(np.clip(1.0 - np.maximum(back, front) ** 2, 0.0, 1.0))  # the ends round off
    s, c = np.sin(a), np.cos(a)
    x = w * rnd * np.sign(s) * np.abs(s) ** 0.85  # a little flat-sided
    y = ck.mix(b, t, ck.smoothstep(-0.25, 0.25, c)) * rnd * c
    radial = np.outer(x, (1.0, 0.0, 0.0)) + np.outer(y, up)
    unit = radial / np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-9)
    P = HEAD_BACK + np.outer(u * length, d) + radial + unit * out
    return P, unit


def head(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """M3-CRE-635: a camelid's head (the first render read as a duck's: a dark flat bill on a white face). Long and
    narrow, deep at the cheeks, the muzzle soft and round in the coat's colour, darkened laterite only at the nose
    and the lips; the eyes at the sides under a soft brow, long upright ears with a slight droop, the woolly cap."""
    h = rig.rigid("head")
    d, up, length = head_frame()
    us = np.concatenate([[0.012, 0.035], np.linspace(0.07, 0.86, 16), [0.9, 0.93, 0.955, 0.975, 0.99]])
    angs = np.arange(HEAD_SEGS) * (2.0 * math.pi / HEAD_SEGS)
    U, A = (x.ravel() for x in np.meshgrid(us, angs, indexing="ij"))
    P, unit = head_surface(U, A)
    # the soft brow over each eye, and the split of the upper lip at the front
    for s in (-1.0, 1.0):
        da = np.angle(np.exp(1j * (A - s * math.radians(EYE_A - 18.0))))
        P += unit * (0.016 * np.exp(-((U - EYE_U) / 0.06) ** 2 - (da / 0.35) ** 2))[:, None]
    split = ck.smoothstep(0.9, 0.99, U) * np.exp(-(np.sin(A) / 0.12) ** 2) * ck.smoothstep(-0.2, -0.7, np.cos(A))
    P -= np.outer(0.012 * split, d)
    T = ck.grid_tris(len(us), HEAD_SEGS, True)
    ends = []
    for u, row in ((0.0, 0), (1.0, len(us) - 1)):  # pole caps at the poll and the nose
        idx = len(P) + len(ends)
        ends.append(HEAD_BACK + d * length * u)
        r0 = row * HEAD_SEGS
        ring = [(r0 + s, idx, r0 + (s + 1) % HEAD_SEGS) for s in range(HEAD_SEGS)]
        T = np.vstack([T, np.asarray(ring, dtype=np.int64)])
    P = np.vstack([P, np.asarray(ends)])
    U = np.concatenate([U, [0.0, 1.0]])
    A = np.concatenate([A, [0.0, 0.0]])
    T = outward(P, T, lambda c: HEAD_BACK + np.outer(np.clip((c - HEAD_BACK) @ d, 0.0, length), d))
    c = np.cos(A)
    down = 0.15 + 0.45 * ck.smoothstep(0.4, -0.8, c)
    col, _, cav = fleece_colour(P, down, SEED + 60)
    # darkened laterite only at the nose (the muzzle's front, above the lip) and along the lips
    nose = ck.smoothstep(0.93, 0.985, U) * ck.smoothstep(-0.75, -0.2, c) * ck.smoothstep(0.75, 0.2, c)
    lips = ck.smoothstep(0.8, 0.95, U) * ck.smoothstep(-0.75, -0.95, c)
    dark = np.maximum(0.75 * nose, 0.6 * lips)
    col = ck.mix(col, HIDE, (0.85 * dark)[:, None])
    finish(mesh, P, T, "fleece", col, h, cavity=ck.mix(0.6 * cav, 0.2, dark))
    # the woolly cap over the poll and the brow (the face's coat is short; the cap is the wool's)
    rot = np.column_stack([(1.0, 0.0, 0.0), up, d])  # local (x, up, along) to world
    cap_c = HEAD_BACK + d * length * 0.2 + up * 0.085
    cap, Tc = ck.ellipsoid((0.0, 0.0, 0.0), (0.125, 0.085, 0.15), 7, 16)
    cap = cap @ rot.T + cap_c
    curls = np.abs(np.sin(np.arctan2((cap - cap_c) @ np.array([1.0, 0.0, 0.0]), (cap - cap_c) @ d) * 8.0))
    lump = 0.03 * ck.fbm(cap * 5.0, SEED + 61) + 0.022 * curls
    cap = cap + (cap - cap_c) / np.linalg.norm(cap - cap_c, axis=1, keepdims=True) * lump[:, None]
    col, _, cav = fleece_colour(cap, np.full(len(cap), 0.1), SEED + 62)
    finish(mesh, cap, Tc, "fleece", col, h, cavity=cav)
    for s in (-1.0, 1.0):
        # the eye, set into the side of the head, a little forward-looking
        pe, ue = head_surface(np.array([EYE_U]), np.array([s * math.radians(EYE_A)]), -0.012)
        Pe, Te = ck.ellipsoid((0.0, 0.0, 0.0), (0.028, 0.034, 0.042), 5, 8)
        Pe = Pe @ rot.T + pe[0]
        finish(mesh, Pe, Te, "eye", PAL["lacquer_black"], h, wet=1.0)
        # the nostril: a dark slit on the muzzle's front, slanting up and out
        pn, _ = head_surface(np.array([0.975]), np.array([s * 0.55]), -0.004)
        Pn, Tn = ck.ellipsoid((0.0, 0.0, 0.0), (0.011, 0.026, 0.011), 3, 6)
        Pn = ck.transform(Pn, ck.euler(-30.0, 0.0, -s * 35.0)) + pn[0]
        finish(mesh, Pn, Tn, "hide", ck.mix(PAL["lacquer_black"], HIDE, 0.3), h, wet=0.6)
        # the long ear: upright off the poll, flat (its opening forward), the tip drooping a little out and back
        pb, _ = head_surface(np.array([EAR_U]), np.array([s * 0.62]), -0.02)
        b0 = pb[0]
        ep = ck.bezier([b0, b0 + np.array([s * 0.015, 0.15, 0.035]), b0 + np.array([s * 0.04, 0.26, 0.03]),
                        b0 + np.array([s * 0.1, 0.3, 0.0])], 8)
        Pr, Tr = ck.tube(ep, np.array([0.034, 0.046, 0.052, 0.05, 0.045, 0.035, 0.023, 0.008]), 10, cap_start=False,
                         squash=0.6)
        Pr = ep[0] + (Pr - ep[0]) @ ck.rot_y(s * 40.0).T  # the opening turned out, so it shows from the side too
        along = np.concatenate([np.repeat(np.linspace(0.0, 1.0, 8), 10), [1.0]])
        inner = ck.smoothstep(0.0, 0.015, (Pr - np.vstack([np.repeat(ep, 10, axis=0), ep[-1:]])) @ d)
        col, _, cav = fleece_colour(Pr, 0.2 + 0.45 * inner * ck.smoothstep(0.1, 0.3, along), SEED + 63)
        finish(mesh, Pr, Tr, "fleece", col, h, cavity=cav)
    # the lower jaw: slim, the coat's colour under it, the lower lip darkened
    j = rig.rigid("jaw")
    jp = ck.bezier(JAW_PATH, 7)
    Pj, Tj = ck.tube(jp, np.interp(np.linspace(0.0, 1.0, 7), np.linspace(0.0, 1.0, len(JAW_R)), JAW_R), 12,
                     squash=0.88)
    centre = np.vstack([np.repeat(jp, 12, axis=0), jp[:1], jp[-1:]])
    rad = (Pj - centre)[:, 1] / np.maximum(np.linalg.norm(Pj - centre, axis=1), 1e-9)
    along = np.concatenate([np.repeat(np.linspace(0.0, 1.0, 7), 12), [0.0, 1.0]])
    col, _, cav = fleece_colour(Pj, 0.3 + 0.4 * ck.smoothstep(0.2, -0.8, rad), SEED + 64)
    frost = ck.smoothstep(-0.3, -0.8, rad) * ck.smoothstep(0.85, 0.4, along)  # the ice beard: frost under the jaw
    col = ck.mix(col, PAL["salt_glass"] * 0.92, (0.6 * frost)[:, None])
    lip = ck.smoothstep(0.7, 0.95, along) * ck.smoothstep(-0.2, 0.5, rad)
    col = ck.mix(col, HIDE, (0.6 * lip)[:, None])
    finish(mesh, Pj, Tj, "fleece", col, j, wet=0.6 * frost, cavity=ck.mix(0.6 * cav, 0.2, lip))
    # and two short frozen locks at the jaw's back, under the cheek, one icicle (never a row of them)
    rng = np.random.default_rng(SEED + 65)
    for k, (x, z, length) in enumerate(((0.025, 1.61, 0.15), (-0.035, 1.66, 0.1))):
        root = np.array([x, np.interp(z, [p[2] for p in JAW_PATH], [p[1] for p in JAW_PATH]) - 0.03, z])
        tip = root + np.array([rng.uniform(-0.03, 0.03), -length, rng.uniform(-0.04, 0.0)])
        short_lock(mesh, root, tip, j, SEED + 66 + k, r=(0.04, 0.016))
        if k == 0:
            icicle(mesh, tip + np.array([0.0, 0.01, 0.0]), rng.uniform(0.06, 0.1), rng.uniform(0.016, 0.024), j,
                   lean=(rng.uniform(-10.0, 10.0), rng.uniform(-10.0, 10.0)), waist=rng.uniform(0.45, 0.65))


# ---------------------------------------------------------------------------------------------
# Locks: six chains of heavy frozen locks hanging to the knees, plus the throat's mane
# ---------------------------------------------------------------------------------------------
def lock_frame(k: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A chain's bone points (head of a, a's tail, b's tail)."""
    s, u, _ = LOCKS[k]
    P, _, _, _ = barrel_surface(np.array([u]), np.array([math.radians(s * 0.5 * sum(STRAND_TH))]), [])
    a = P[0] + np.array([-s * 0.03, 0.0, 0.0])
    return a, np.array([a[0] + s * 0.05, LOCK_JOINT_Y[0], a[2]]), np.array([a[0] + s * 0.07, LOCK_JOINT_Y[1], a[2]])


def locks(mesh: ck.Mesh, rig: ck.Rig, paths: list[np.ndarray]) -> None:
    rng = np.random.default_rng(SEED + 70)
    ice_rng = np.random.default_rng(SEED + 75)
    for k, (s, u_c, parent) in enumerate(LOCKS):
        a, m, b = lock_frame(k)
        skin = rig.chain([parent, f"lock{k}_a", f"lock{k}_b"], [a + np.array([-s * 0.25, 0.4, 0.0]), a, m, b])
        tips: list[np.ndarray] = []  # each strand's path
        for i in range(STRANDS):
            u = u_c + (i - (STRANDS - 1) / 2) * 0.022 + rng.uniform(-0.006, 0.006)
            th = math.radians(s * (STRAND_TH[0] + (STRAND_TH[1] - STRAND_TH[0]) * ((i * 5) % STRANDS) / (STRANDS - 1)))
            root, n, _, _ = barrel_surface(np.array([u]), np.array([th]), paths)
            root, n = root[0] - n[0] * 0.05, n[0]
            tip = np.array([root[0] + s * rng.uniform(0.02, 0.1), rng.uniform(*TIP_Y),
                            root[2] + rng.uniform(-0.05, 0.05)])
            mid = 0.5 * (root + tip) + np.array([s * rng.uniform(0.04, 0.09), 0.0, 0.0])
            path = ck.bezier([root, root + n * 0.1 + np.array([0.0, -0.08, 0.0]), mid, tip], 7)
            P, T = ck.tube(path, np.linspace(rng.uniform(0.07, 0.09), 0.04, 7), 5, cap_start=False, squash=0.55)
            down = ck.smoothstep(root[1], tip[1], P[:, 1])
            col, wet, cav = fleece_colour(P, 0.45 + 0.4 * down, SEED + 71 + k)
            frost = ck.smoothstep(0.65, 1.0, down)  # frosted, not ice: the icicles are the few below
            col = ck.mix(col, PAL["salt_glass"] * 0.92, (0.45 * frost)[:, None])
            finish(mesh, P, T, "fleece", col, skin, wet=np.maximum(wet, 0.6 * frost), cavity=cav * (1.0 - frost))
            tips.append(path)
        # a few icicles per chain on strands picked at random, of uneven lengths (M3-CRE-635): each sheathes the
        # strand's frozen end and hangs on past its tip, no further than the old tip icicles did (the KO lays the
        # locks' ends on the ground)
        for i in ice_rng.choice(STRANDS, int(ice_rng.integers(LOCK_ICE[0], LOCK_ICE[1] + 1)), replace=False):
            length, past = ice_rng.uniform(*LOCK_ICE_LEN), ice_rng.uniform(*LOCK_ICE_PAST)
            path = tips[i]
            y = path[-1, 1] + length - past
            top = np.array([np.interp(y, path[::-1, 1], path[::-1, 0]), y, np.interp(y, path[::-1, 1], path[::-1, 2])])
            icicle(mesh, top, length, ice_rng.uniform(0.026, 0.036), skin,
                   lean=(ice_rng.uniform(-6.0, 6.0), ice_rng.uniform(-6.0, 6.0)), waist=ice_rng.uniform(0.45, 0.7))


def short_lock(mesh: ck.Mesh, root: np.ndarray, tip: np.ndarray, skin, seed: int, r: tuple = (0.07, 0.025)) -> None:
    """A short frozen lock hanging from root to tip, `r` its radius at the root and the tip, frost at its end."""
    length = float(np.linalg.norm(tip - root))
    path = ck.bezier([root, root + np.array([0.0, -0.4 * length, 0.05]), tip], 6)
    P, T = ck.tube(path, np.linspace(r[0], r[1], 6), 5, cap_start=False, squash=0.55)
    down = ck.smoothstep(root[1], tip[1], P[:, 1])
    col, wet, cav = fleece_colour(P, 0.5 + 0.4 * down, seed)
    frost = ck.smoothstep(0.6, 1.0, down)
    col = ck.mix(col, PAL["salt_glass"] * 0.92, (0.6 * frost)[:, None])
    finish(mesh, P, T, "fleece", col, skin, wet=np.maximum(wet, 0.5 * frost), cavity=cav)


def mane(mesh: ck.Mesh, rig: ck.Rig, paths: list[np.ndarray]) -> None:
    """Short locks hanging off the throat (they ride the neck chain) and the chest's bib (the spine's)."""
    rng = np.random.default_rng(SEED + 80)
    for k in range(8):
        u = 0.12 + 0.08 * k + rng.uniform(-0.02, 0.02)
        root = neck_surface(u, np.array([math.pi + rng.uniform(-0.5, 0.5)]), -0.06)[0]
        length = rng.uniform(0.28, 0.42) * (1.2 - 0.6 * u)
        tip = root + np.array([rng.uniform(-0.05, 0.05), -length, rng.uniform(-0.04, 0.02)])
        short_lock(mesh, root, tip, neck_skin(rig), SEED + 81 + k)
    for k in range(BIB):  # the bib: locks down the chest front, between the forelegs' tops
        th = math.radians(180.0 + (k - (BIB - 1) / 2) * 22.0 + rng.uniform(-5.0, 5.0))
        root, n, _, _ = barrel_surface(np.array([0.93 + rng.uniform(-0.02, 0.02)]), np.array([th]), paths)
        root = root[0] - n[0] * 0.04 + np.array([0.0, 0.25, 0.0])
        tip = np.array([root[0] * 1.2, rng.uniform(*TIP_Y) + 0.08, root[2] + rng.uniform(0.0, 0.08)])
        short_lock(mesh, root, tip, spine_skin(rig), SEED + 95 + k)


def tail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    tp = ck.bezier([(0.0, 1.78, -1.66), (0.0, 1.72, -1.84), (0.0, 1.3, -1.86)], 10)  # a heavy tuft, hanging
    P, T = ck.tube(tp, np.linspace(0.14, 0.07, 10), 9, squash=0.8)
    col, wet, cav = fleece_colour(P, np.linspace(0.3, 0.8, len(P)), SEED + 90)
    finish(mesh, P, T, "fleece", col, rig.rigid("spine0"), wet=wet, cavity=cav)


# ---------------------------------------------------------------------------------------------
# Legs: woolly above the knee, darkened laterite below, a broad soft-padded hoof
# ---------------------------------------------------------------------------------------------
def legs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for name in LEGS:
        j = leg_joints(name)
        foot_top = j[3] + np.array([0.0, HOOF_TOP, -0.03])
        pts = [j[0], j[1], j[2], foot_top]
        path = np.vstack([np.linspace(pts[k], pts[k + 1], LEG_RINGS, endpoint=(k == 2)) for k in range(3)])
        u = np.linspace(0.0, 1.0, len(path))
        rad = np.interp(u, [0.0, 0.3, 0.36, 0.62, 0.68, 0.85, 1.0], [0.2, 0.14, 0.12, 0.085, 0.095, 0.085, 0.1])
        P, T = ck.tube(path, rad, LEG_SEGS, cap_start=True, cap_end=False)
        wool = ck.smoothstep(0.62, 0.9, P[:, 1])
        centre = np.concatenate([np.repeat(path, LEG_SEGS, axis=0), path[:1]])
        radial = P - centre
        radial /= np.maximum(np.linalg.norm(radial, axis=1, keepdims=True), 1e-9)
        P = P + radial * (wool * (0.05 + 0.04 * ck.fbm(P * 3.0, SEED + 100)))[:, None]
        fcol, _, fcav = fleece_colour(P, np.full(len(P), 0.55), SEED + 101)
        hcol = HIDE * (0.9 + 0.15 * ck.fbm(P * 6.0, SEED + 102))[:, None]
        col = ck.mix(hcol, fcol, wool[:, None])
        skin = rig.chain([f"{name}_upper", f"{name}_lower", f"{name}_foot"], j)
        finish(mesh, P, T, "hide", col, skin, cavity=ck.mix(0.25, fcav, wool))
        # the hoof: a broad pad, sole flat on the ground
        prof = [(0.0, HOOF_TOP + 0.02), (0.1, HOOF_TOP), (0.135, 0.06), (0.125, 0.0), (0.0, 0.0)]
        Ph, Th = ck.lathe(prof, 14)
        Ph[:, 2] *= 1.25
        Ph = Ph + np.array([j[3][0], 0.0, j[3][2] - 0.04])
        dark = ck.mix(PAL["laterite"] * 0.45, PAL["lacquer_black"], 0.3)
        finish(mesh, Ph, Th, "hide", dark, rig.rigid(f"{name}_foot"), cavity=0.3)


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    rig.add("body", BODY_PIVOT, BODY_PIVOT + np.array([0.0, 0.3, 0.0]), "root")
    for k in range(5):
        rig.add(f"spine{k}", SPINE[k], SPINE[k + 1], "body" if k == 0 else f"spine{k - 1}")
    nj = neck_joints()
    for k in range(5):
        rig.add(f"neck{k}", nj[k], nj[k + 1], "spine4" if k == 0 else f"neck{k - 1}")
    rig.add("head", nj[5], MUZZLE_TIP, "neck4")
    rig.add("jaw", HEAD_C + np.array([0.0, -0.12, 0.14]), MUZZLE_TIP + np.array([0.0, -0.13, -0.04]), "head")
    for name in LEGS:  # the legs hang from the body, so the spine and neck can move without lifting a foot
        j = leg_joints(name)
        rig.add(f"{name}_upper", j[0], j[1], "body")
        rig.add(f"{name}_lower", j[1], j[2], f"{name}_upper")
        rig.add(f"{name}_foot", j[2], j[3], f"{name}_lower")
    for k, (_s, _u, parent) in enumerate(LOCKS):
        a, m, b = lock_frame(k)
        rig.add(f"lock{k}_a", a, m, parent)
        rig.add(f"lock{k}_b", m, b, f"lock{k}_a")
    return rig


# ---------------------------------------------------------------------------------------------
# Poses: legs solved in their own plane
# ---------------------------------------------------------------------------------------------
def _rot2(v: np.ndarray, deg) -> np.ndarray:
    """(y, z) vectors rotated as ck.rot_x does (positive turns +y toward +z), for an array of angles."""
    r = np.radians(np.asarray(deg, dtype=np.float64))[..., None]
    c, s = np.cos(r), np.sin(r)
    v = np.asarray(v, dtype=np.float64)
    return np.concatenate([c * v[..., :1] - s * v[..., 1:], s * v[..., :1] + c * v[..., 1:]], axis=-1)


# The hoof's outline in its leg's plane, (y, z) from the toe joint at rest: its sole, its widest, its top and the
# pastern's tube where it meets it
HOOF_PTS = ((0.0, -0.196), (0.0, 0.116), (0.06, -0.209), (0.06, 0.129), (HOOF_TOP, -0.165), (HOOF_TOP, 0.085),
            (HOOF_TOP + 0.02, -0.04), (HOOF_TOP, -0.13), (HOOF_TOP, 0.07))
# Clearance over the ground: the knee and the fetlock (their tube radii), and the hoof
CLEAR = {"p1": 0.115, "p2": 0.1, "hoof": 0.0}


def _leg_chain(name: str, body: tuple, A, B, C) -> dict:
    """Joint positions (y, z) and the hoof's lowest y for leg angles A, B, C (arrays) under a body pose
    (rx, (y, z) offset)."""
    j = leg_joints(name)[:, 1:]  # (y, z)
    rx, off = body
    piv = BODY_PIVOT[1:]
    j0 = piv + _rot2(j[0] - piv, rx) + np.asarray(off)
    p1 = j0 + _rot2(j[1] - j[0], rx + A)
    p2 = p1 + _rot2(j[2] - j[1], rx + A + B)
    tot = rx + A + B + C
    p3 = p2 + _rot2(j[3] - j[2], tot)
    hoof = np.min(np.stack([(p3 + _rot2(np.array(h), tot))[..., 0] for h in HOOF_PTS]), axis=0)
    return {"p1": p1, "p2": p2, "p3": p3, "hoof": hoof[..., None]}  # the hoof as (lowest y,)


def solve_leg(name: str, body: tuple, targets: dict, keep_foot: bool = False, prefer=(0.0, 0.0, 0.0),
              around=None, span: float = 12.0) -> tuple:
    """(A, B, C) degrees putting the leg's points at `targets` {point: (y, z)} under the body pose, the knee, the
    fetlock and the hoof above the ground, nearest `prefer` among equally good fits. `keep_foot` holds the hoof
    level (C follows A and B). An exhaustive grid (over everything, or within `span` degrees `around` a pose), then a
    fine one round its best: deterministic."""
    def cost(A, B, C):
        pts = _leg_chain(name, body, A, B, C)
        c = np.zeros(np.shape(A))
        for k, tgt in targets.items():
            c += 400.0 * np.sum((pts[k] - np.asarray(tgt)) ** 2, axis=-1)
        for k, h in CLEAR.items():
            c += 4.0e6 * np.maximum(h - pts[k][..., 0], 0.0) ** 2
        c += 1e-5 * ((A - prefer[0]) ** 2 + (B - prefer[1]) ** 2 + (C - prefer[2]) ** 2)
        return c

    def search(centre, span, step):
        g = [np.arange(c - span, c + span + 1e-9, step) for c in centre]
        if keep_foot:
            A, B = (x.ravel() for x in np.meshgrid(g[0], g[1], indexing="ij"))
            C = -(body[0] + A + B)
        else:
            A, B, C = (x.ravel() for x in np.meshgrid(g[0], g[1], g[2], indexing="ij"))
        k = int(np.argmin(cost(A, B, C)))
        return float(A[k]), float(B[k]), float(C[k])

    best = search((0.0, 0.0, 0.0), 150.0, 3.0) if around is None else search(around, span, max(span / 12.0, 1.0))
    return search(search(best, 1.5, 0.25), 0.3, 0.025)


def rest_foot(name: str) -> np.ndarray:
    return leg_joints(name)[3, 1:]


def planted(name: str, body: tuple, around=None) -> tuple:
    """The leg's angles keeping its hoof where it stands at rest, level, under the body pose."""
    return solve_leg(name, body, {"p3": rest_foot(name)}, keep_foot=True, around=around)


def key_leg(clip: ck.Clip, name: str, t: float, abc: tuple) -> None:
    for seg, deg in zip(("upper", "lower", "foot"), abc):
        clip.key(f"{name}_{seg}", t, (deg, 0.0, 0.0))


def frame_times(length: float) -> list[float]:
    return [min(f / ck.FPS, length) for f in range(int(round(length * ck.FPS)) + 1)]


def key_body_track(clip: ck.Clip, keys: tuple) -> list[tuple]:
    """Keys the body at every frame along `keys` [(t, rx, (y, z))], eased as a clip eases; returns the body pose
    at each frame. Every frame is keyed (the export bakes every frame anyway), so legs solved per frame stay
    planted between the authored keys too."""
    track = ck.Clip("_body", clip.length)
    for t, rx, off in keys:
        track.key("body", t, (rx, 0.0, 0.0), (0.0, off[0], off[1]))
    out = []
    for t in frame_times(clip.length):
        r, loc = track.sample("body", t)
        clip.key("body", t, tuple(r), tuple(loc))
        out.append((t, (float(r[0]), (float(loc[1]), float(loc[2])))))
    return out


def key_locks(clip: ck.Clip, t: float, fwd: float, out: float, bend: float = 0.6) -> None:
    """The six lock chains at a swing: `fwd` degrees (tips back, +), `out` degrees away from the body."""
    for k, (s, _u, _p) in enumerate(LOCKS):
        clip.key(f"lock{k}_a", t, (fwd, 0.0, s * out))
        clip.key(f"lock{k}_b", t, (fwd * bend, 0.0, s * out * bend))


NECK_DOWN = ("neck0", "neck1", "neck2", "neck3", "neck4")


def key_neck(clip: ck.Clip, t: float, degs: tuple, head: float = 0.0, jaw: float = 0.0, yaw: tuple = ()) -> None:
    """Neck bones pitched (+ nose down), the head and the jaw (+ opens); `yaw` a sideways turn per neck bone."""
    for k, d in enumerate(degs):
        clip.key(NECK_DOWN[k], t, (d, yaw[k] if k < len(yaw) else 0.0, 0.0))
    clip.key("head", t, (head, 0.0, 0.0))
    clip.key("jaw", t, (jaw, 0.0, 0.0))


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 4.0
ATTACK_SEC = 1.6
ATTACK_CONTACT = 0.75
STAMP = (0.12, 0.32, 0.44, 0.5)  # the right fore leaves the ground, is up, comes down level, stamps
STAMP_DROP = 0.06  # the hoof's height over the ground when it comes down level (STAMP[2])
CAST_SEC = 1.8
HIT_SEC = 0.6
KO_SEC = 3.8
KO_KNEEL_T, KO_LIE_T = 1.3, 2.6
KNEEL = (14.0, (-0.3, 0.06))  # the KO's kneel: body pitch, (y, z) offset
LIE = (0.0, (-0.5, 0.02))  # lying down: the belly on its folded legs
KO_NECK = (42.0, 25.0, 16.0, 6.0, 0.0)  # the neck laid down, the head resting on the ground
KO_HEAD = -97.0
KO_LOCKS = (4.0, 54.0, -0.38)  # lying: the locks spread out from the body, their ends draped down onto the ground


def build_idle() -> ck.Clip:
    idle = ck.Clip("idle", IDLE_SEC, loop=True)  # the neck sways, it chews, the locks swing
    idle.wave("neck0", amp_rot=(1.5, 2.5, 0.0), cycles=1)
    idle.wave("neck2", amp_rot=(1.2, 3.0, 0.0), cycles=1, phase=0.7)
    idle.wave("neck4", amp_rot=(1.0, 3.5, 0.0), cycles=1, phase=1.4)
    idle.wave("head", amp_rot=(2.0, 2.0, 0.0), cycles=2, phase=0.3)
    idle.wave("jaw", amp_rot=(4.0, 3.0, 0.0), base_rot=(4.0, 0.0, 0.0), cycles=6, steps=8)
    idle.wave("spine2", amp_rot=(0.6, 0.0, 0.0), amp_loc=(0.0, 0.012, 0.0), cycles=2)
    idle.wave("spine3", amp_rot=(-0.8, 0.0, 0.0), cycles=2, phase=0.4)
    for k, (s, u, _p) in enumerate(LOCKS):
        idle.wave(f"lock{k}_a", amp_rot=(2.5, 0.0, s * 1.5), cycles=1, phase=1.0 + u * 3.0)
        idle.wave(f"lock{k}_b", amp_rot=(2.0, 0.0, s * 1.0), cycles=1, phase=1.6 + u * 3.0)
    return idle


def build_attack() -> ck.Clip:
    """The charge: the head drops, a stamp of the right fore, and it drives through (contact at 0.75 s); the feet
    stay planted (the sequencer carries it to its target) and are where they started at the end."""
    attack = ck.Clip("attack", ATTACK_SEC)
    body = key_body_track(attack, ((0.0, 0.0, (0.0, 0.0)), (0.32, -2.0, (0.02, -0.14)), (0.52, 1.0, (-0.02, -0.04)),
                                   (ATTACK_CONTACT, 3.0, (-0.05, 0.3)), (1.05, 1.0, (-0.02, 0.14)),
                                   (ATTACK_SEC, 0.0, (0.0, 0.0))))
    prev: dict = {}
    for t, pose in body:
        for name in LEGS:
            if name == "fr" and STAMP[0] < t < STAMP[2]:
                prev.pop(name, None)  # in the air: the descent is solved afresh
                continue
            above = 0.0
            if name == "fr" and t < STAMP[3]:  # the last few centimetres down, level: the stamp
                above = STAMP_DROP * (STAMP[3] - t) / (STAMP[3] - STAMP[2])
            prev[name] = solve_leg(name, pose, {"p3": rest_foot(name) + np.array([above, 0.0])}, keep_foot=True,
                                   around=prev.get(name))
            key_leg(attack, name, t, prev[name])
    lift = dict(body)[min(dict(body), key=lambda t: abs(t - STAMP[1]))]
    raised = solve_leg("fr", lift, {"p3": rest_foot("fr") + np.array([0.32, 0.18])}, prefer=(-30.0, 50.0, 0.0))
    key_leg(attack, "fr", STAMP[1], raised)
    for t, neck_d, head_d in ((0.0, (0, 0, 0, 0, 0), 0.0), (0.32, (12, 10, 8, 4, 0), -8.0),
                              (0.52, (16, 12, 8, 2, 0), -12.0), (ATTACK_CONTACT, (24, 16, 9, 2, -4), -20.0),
                              (1.05, (12, 8, 4, 0, 0), -8.0), (ATTACK_SEC, (0, 0, 0, 0, 0), 0.0)):
        key_neck(attack, t, neck_d, head_d, jaw=4.0 if 0.0 < t < ATTACK_SEC else 0.0)
    for t, rx in ((0.0, 0.0), (0.32, -1.0), (ATTACK_CONTACT, 1.5), (ATTACK_SEC, 0.0)):
        attack.key("spine2", t, (rx, 0.0, 0.0))
    for t, fwd, out in ((0.0, 0, 0), (0.32, -6, 2), (0.6, 4, 4), (0.88, 16, 8), (1.2, -6, 3), (ATTACK_SEC, 0, 0)):
        key_locks(attack, t, fwd, out)
    return attack


def build_cast() -> ck.Clip:
    """The bellow: the neck rises, the head lifts and the jaw opens wide, the chest rising with it."""
    cast = ck.Clip("cast", CAST_SEC)
    for t, s, jaw in ((0.0, 0.0, 0.0), (0.45, 0.6, 6.0), (0.9, 1.0, 28.0), (1.35, 0.92, 22.0), (CAST_SEC, 0.0, 0.0)):
        key_neck(cast, t, (-20 * s, -14 * s, -8 * s, -4 * s, 0.0), -26.0 * s, jaw)
        cast.key("spine3", t, (-3.0 * s, 0.0, 0.0))
        cast.key("spine4", t, (-4.0 * s, 0.0, 0.0))
    for t, fwd, out in ((0.0, 0, 0), (0.6, 4, 3), (1.1, -3, 5), (CAST_SEC, 0, 0)):
        key_locks(cast, t, fwd, out)
    return cast


def build_hit() -> ck.Clip:
    """M3-CRE-617: it staggers back and the neck whips, peaking at 0.1 s, the locks lagging behind; the body only
    slides (no pitch), so the feet stay on the ground."""
    hit = ck.Clip("hit", HIT_SEC)
    for t, s in ((0.0, 0.0), (0.1, 1.0), (0.24, 0.55), (0.4, 0.2), (HIT_SEC, 0.0)):
        hit.key("body", t, (0.0, 0.0, 0.0), (0.0, 0.0, -0.17 * s))
        hit.key("spine2", t, (-2.0 * s, 0.0, 0.0))
        hit.key("spine4", t, (-5.0 * s, 0.0, 0.0))
    for t, w in ((0.0, 0.0), (0.1, 1.0), (0.22, -0.5), (0.36, 0.2), (HIT_SEC, 0.0)):
        key_neck(hit, t, (-12 * w, -9 * w, -6 * w, -3 * w, 0.0), 10.0 * w, 8.0 * max(w, 0.0), yaw=(3 * w, 3 * w, 2 * w))
    for t, fwd, out in ((0.0, 0, 0), (0.12, -7, 4), (0.26, 5, 2), (HIT_SEC, 0, 0)):
        key_locks(hit, t, fwd, out)
    return hit


def build_ko() -> ck.Clip:
    """It kneels (the fore knees down), then lies down with its legs folded under it, and lays its head down: no
    thrash (pillar 1). The herd-cord, on the lowered neck, is the last thing in frame."""
    ko = ck.Clip("ko", KO_SEC)
    body = key_body_track(ko, ((0.0, 0.0, (0.0, 0.0)), (0.35, 0.0, (-0.04, 0.0)), (KO_KNEEL_T, KNEEL[0], KNEEL[1]),
                               (KO_LIE_T, LIE[0], LIE[1]), (KO_SEC, LIE[0], LIE[1])))
    kneel_fore = {n: solve_leg(n, KNEEL, {"p1": (0.12, leg_joints(n)[1][2] + 0.12),
                                          "p2": (0.1, leg_joints(n)[1][2] - 0.32)}, prefer=(-20.0, 140.0, 20.0))
                  for n in ("fl", "fr")}
    lie = {}
    for n in LEGS:
        j = leg_joints(n)
        if n[0] == "f":  # the fore knees on the ground, the cannons folded back under the chest
            lie[n] = solve_leg(n, LIE, {"p1": (0.12, j[1][2] + 0.16), "p2": (0.1, j[1][2] - 0.28)},
                               prefer=(-20.0, 140.0, 20.0))
        else:  # the hind legs tucked: the stifle forward, the hock and the cannon on the ground
            lie[n] = solve_leg(n, LIE, {"p1": (0.16, j[0][2] + 0.3), "p2": (0.1, j[0][2] - 0.26)},
                               prefer=(-60.0, 120.0, -60.0))
    start: dict = {}
    prev: dict = {}
    for t, pose in body:
        for n in LEGS:
            if t <= 0.35 or (n[0] == "b" and t <= KO_KNEEL_T):  # standing: planted
                prev[n] = planted(n, pose, prev.get(n))
                start[(n, 0.35 if t <= 0.35 else KO_KNEEL_T)] = prev[n]
                key_leg(ko, n, t, prev[n])
                continue
            if t <= KO_KNEEL_T:
                a, b, e = start[(n, 0.35)], kneel_fore[n], (t - 0.35) / (KO_KNEEL_T - 0.35)
            elif t <= KO_LIE_T:
                a = kneel_fore[n] if n[0] == "f" else start[(n, KO_KNEEL_T)]
                b, e = lie[n], (t - KO_KNEEL_T) / (KO_LIE_T - KO_KNEEL_T)
            else:
                a, b, e = lie[n], lie[n], 1.0
            want = tuple(float(x) for x in ck.mix(np.asarray(a), np.asarray(b), float(ck.smoothstep(0.0, 1.0, e))))
            prev[n] = solve_leg(n, pose, {}, prefer=want, around=want, span=40.0)  # the eased fold, off the ground
            key_leg(ko, n, t, prev[n])
    # the neck: steady through the kneel, then lowered until the head rests on the ground, turned a little
    for t, s, yaw in ((0.0, 0.0, 0.0), (0.35, 0.05, 0.0), (KO_KNEEL_T, -0.1, 0.0), (KO_LIE_T, 0.3, 0.3),
                      (3.3, 0.94, 0.9), (KO_SEC, 1.0, 1.0)):
        key_neck(ko, t, tuple(d * s for d in KO_NECK), KO_HEAD * max(s, 0.0) ** 1.5, yaw=(7 * yaw, 6 * yaw, 3 * yaw))
    for t, s in ((0.0, 0.0), (0.35, 0.0), (KO_KNEEL_T, -1.5), (KO_LIE_T, 2.0), (KO_SEC, 2.0)):
        ko.key("spine2", t, (s, 0.0, 0.0))
    # the locks swing with the kneel, then spread out on the ground as it lies down
    for t, fwd, out, bend in ((0.0, 0, 0, 0.6), (0.35, 0, 0, 0.6), (KO_KNEEL_T, -8, 14, 0.6),
                              (KO_LIE_T, *KO_LOCKS), (KO_SEC, *KO_LOCKS)):
        key_locks(ko, t, fwd, out, bend)
    return ko


def build_clips() -> list[ck.Clip]:
    return [build_idle(), build_attack(), build_cast(), build_hit(), build_ko()]


# ---------------------------------------------------------------------------------------------
# A numpy check (no Blender): skinned bounds, head height, feet and peak time per clip
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
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)}")
    for c in ck.with_variety(clips):
        frames = max(int(round(c.length * ck.FPS)), 1)
        lo, disp, peak = np.inf, [], None
        for f in range(frames + 1):
            t = min(f / ck.FPS, c.length)
            P = skin(rig, arrays, fk(rig, c, t))
            lo = min(lo, float(P[:, 1].min()))
            disp.append(float(np.linalg.norm(P - rest, axis=1).mean()))
        end = fk(rig, c, c.length)
        P = skin(rig, arrays, end)
        feet = [round(float((end[f"{n}_foot"][0] @ leg_joints(n)[3] + end[f"{n}_foot"][1])[1]), 3) for n in LEGS]
        head = end["head"][0] @ HEAD_C + end["head"][1]
        peak = int(np.argmax(disp)) / ck.FPS
        print(f"{c.name:7s} {c.length:.2f}s: lowest y over the clip {lo:+.3f}; at the end y {P[:, 1].min():+.3f}.."
              f"{P[:, 1].max():.3f}, head centre y {head[1]:.2f}, feet y {feet}; peak {peak:.2f}s")


def build() -> tuple[ck.Rig, ck.Mesh, list[ck.Clip]]:
    rig = build_rig()
    mesh = ck.Mesh("avalanche_ram")
    paths = parting_paths()
    barrel(mesh, rig, paths)
    partings(mesh, rig, paths)
    belly_ice(mesh, rig, paths)
    neck(mesh, rig)
    herd_cord(mesh, rig)
    head(mesh, rig)
    mane(mesh, rig, paths)
    locks(mesh, rig, paths)
    tail(mesh, rig)
    legs(mesh, rig)
    return rig, mesh, build_clips()


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
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "avalanche_ram"})
    print(f"avalanche_ram: {info}")


if __name__ == "__main__":
    main()
