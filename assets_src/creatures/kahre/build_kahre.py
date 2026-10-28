"""Kahre, the Forge-Crowned, Asha's Lightning Vowbound (M3-CRE-640; final pass M3-CRB-008):
docs/kb/art/creatures/vowbound/kahre.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/kahre/build_kahre.py -- --out assets/creatures/kahre/kahre.glb

A towering hornbill-headed beast built like a smith. Heavy muscled shoulders under a hump, forearms thick as a
smith's with tendon and plate relief, that he walks on knuckle-down (three thick curled digits a hand, hooked claws);
a deep chest whose sternum is a forged anvil (the face under his throat worn bright and pocked with hammer scars, the
hardy and pritchel holes at its heel, the horn jutting forward, the waist going down into the keel, a bound-light star
of an old strike on each flank). His hide is dark stone and old iron: charcoal to ash-grey, pitted, cracked, warm as
banked embers down in its cracks and creases, with plated keratin scutes over the back. A massive ridged casque of
worn ivory and brass rides his bill, and a smith's hammer is fused into it (the keepsake, the one part of him that is
an object and not light): an octagonal cross-peen head on an ash handle wrapped in leather, its foot grown over by
the casque. A crest of fine filaments of bound light, running sparks, stands along the back of his neck and over the
hump: rigid geometry that moves only with the neck.

**Grounded.** The origin is the water point under him and he stands on it. Every planted foot is solved onto the
water at every baked frame (`solve_legs`: a two-bone solve per leg in its own plane, the foot kept level), so the
body can rear, lunge and lie down while the feet stay where they stand. Every clip stays above the water.

Rig (24 bones): `root`, `body` (the hips), `chest`, `neck_0..2`, `head`, `jaw`, `arm_l0`, `arm_l1`, `hand_l` and the
right arm, `leg_l0`, `leg_l1`, `foot_l` and the right leg (+x is `l`), `tail_0`, `tail_1`, and two unweighted VFX
anchors: `vfx_core` (the chest's centre, on `chest`) and `vfx_keepsake` (the hammer's head, on `head`).

`python3 build_kahre.py --report` prints the triangle count, per-part counts and per-clip lows (numpy, no export).
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

SEED = 6400
PAL = {k: ck.hexrgb(v) for k, v in {
    "volcanic_stone": "#3A3A3F", "lacquer_black": "#1D1916", "coral_stone_weathered": "#B9AE98", "bone": "#E6DAC0",
    "brass": "#B08D57", "salt_glass": "#BFE6E0", "timber_weathered": "#7E6A55", "sand_cloth": "#C9B48E",
    "deep_teal_shadow": "#0E4A55", "tortoiseshell": "#6B3A1E", "gauze_white": "#EBE7DF", "foam_white": "#EEF6F4",
}.items()}
STONE = PAL["volcanic_stone"]
CHAR = ck.mix(PAL["lacquer_black"], STONE, 0.4)  # charcoal
ASH = PAL["coral_stone_weathered"]
EMBER = ck.mix(PAL["lacquer_black"], PAL["tortoiseshell"], 0.6)  # the warmth banked in the cracks and creases
IRON = ck.mix(STONE, ASH, 0.1)
STEEL = ck.mix(STONE, ASH, 0.55)  # iron worn bright
STEEL_HI = ck.mix(ASH, PAL["gauze_white"], 0.55)
HORN = ck.mix(ck.mix(PAL["lacquer_black"], PAL["tortoiseshell"], 0.35), ck.mix(STONE, ASH, 0.3), 0.5)  # keratin
LEATHER = ck.mix(PAL["tortoiseshell"], PAL["lacquer_black"], 0.4)
IVORY = PAL["bone"]

# ---- the skeleton's rest joints (metres, Godot axes, facing +z; the water at y 0) ---------------
HIP = np.array([0.0, 1.38, -0.42])  # the body bone's head: rearing pitches about the hips
CHEST = np.array([0.0, 1.82, 0.30])
NECK_PATH = ((0.0, 1.98, 0.42), (0.0, 2.26, 0.62), (0.0, 2.50, 0.84), (0.0, 2.62, 1.00))
HEAD_TIP = np.array([0.0, 2.68, 1.42])
JAW_HINGE = np.array([0.0, 2.56, 1.13])
FORE_X, HIND_X = 0.56, 0.42
# (y, z) in each leg's plane: the top joint, the middle, the wrist or ankle, the knuckles or toes
FORE = np.array([(1.92, 0.46), (1.10, 0.28), (0.24, 0.62), (0.06, 0.78)])
HIND = np.array([(1.38, -0.42), (0.78, -0.12), (0.16, -0.50), (0.04, -0.20)])
LEGS = {  # leg: (bones top .. foot, x, joints, parent)
    "fore_l": (("arm_l0", "arm_l1", "hand_l"), FORE_X, FORE, "chest"),
    "fore_r": (("arm_r0", "arm_r1", "hand_r"), -FORE_X, FORE, "chest"),
    "hind_l": (("leg_l0", "leg_l1", "foot_l"), HIND_X, HIND, "body"),
    "hind_r": (("leg_r0", "leg_r1", "foot_r"), -HIND_X, HIND, "body"),
}
TAIL_PTS = np.array([(0.0, 1.46, -0.74), (0.0, 1.32, -0.86), (0.0, 1.12, -0.94)])
VFX_CORE = np.array([0.0, 1.86, 0.42])  # the chest's centre, behind the anvil

# ---- the torso: control rings along the spine (z, centre y, half width, half height above, below) ------
TORSO = (
    (-0.87, 1.48, 0.06, 0.05, 0.05), (-0.82, 1.48, 0.28, 0.25, 0.25), (-0.62, 1.51, 0.43, 0.38, 0.36),
    (-0.32, 1.60, 0.45, 0.44, 0.38), (0.00, 1.74, 0.53, 0.52, 0.46), (0.28, 1.86, 0.60, 0.56, 0.56),
    (0.50, 1.92, 0.55, 0.48, 0.60), (0.68, 1.88, 0.42, 0.36, 0.54), (0.82, 1.80, 0.27, 0.24, 0.42),
    (0.90, 1.74, 0.07, 0.07, 0.10),
)
TORSO_RINGS, TORSO_SEGS = 34, 30

# ---- the head ----------------------------------------------------------------------------------
SKULL_C, SKULL_R = np.array([0.0, 2.67, 1.05]), (0.175, 0.185, 0.22)
EYE_AT = (0.134, 2.725, 1.16)
BILL = ((0.0, 2.64, 1.16), (0.0, 2.64, 1.50), (0.0, 2.50, 1.80), (0.0, 2.24, 1.95))
MANDIBLE = ((0.0, 2.55, 1.15), (0.0, 2.52, 1.45), (0.0, 2.40, 1.72), (0.0, 2.22, 1.90))
CASQUE_Z = (0.86, 1.7)  # the casque runs from the brow to past mid-bill
HAMMER_Z = 1.4  # where the handle is sunk into the casque (in the saddle in front of its hump)
HANDLE_RAKE = 16.0  # degrees back from upright: the head lies along the crest, its face forward and tilted up with
# the horn's sweep (it leads every nose-down swing), its underside resting on the casque's hump behind the handle
HANDLE_VIS = 0.185  # the handle's length out of the casque, to the head's centre
HANDLE_R = 0.052
GROWTH = 0.048  # how far the casque's growth has climbed the handle
HEAD_FACE, HEAD_PEEN = 0.31, -0.34  # along its length from the handle: the face forward, the peen back

# ---- the anvil (the sternum) ---------------------------------------------------------------------
FACE_Y, FACE_T = 1.92, 0.12  # the face's top and thickness
FACE_Z = (0.6, 1.16)
FACE_HW = 0.21
WAIST = ((0.0, 1.84, 0.86), (0.0, 1.36, 0.68))  # top, bottom (in the keel)
ANVIL_HORN = ((0.0, 1.85, 1.2), (0.0, 1.85, 1.42), (0.0, 1.81, 1.64))
STRIKE_AT = (1.60, 0.88)  # (y, z) of the struck star on each flank of the waist
STRIKE_RAYS = 7

TAIL_FEATHERS = ((0.0, 0.62, 70.0), (0.09, 0.58, 55.0), (-0.09, 0.58, -55.0), (0.17, 0.5, 35.0), (-0.17, 0.5, -35.0))
MANE_N = 240  # filaments of running sparks

PARTS: dict[str, int] = {}
SURF: dict[str, np.ndarray] = {}  # displaced rest surfaces the later parts sit on


def count(name: str, mesh: ck.Mesh, before: int) -> None:
    PARTS[name] = PARTS.get(name, 0) + mesh.triangle_count - before


def oriented(P: np.ndarray, T: np.ndarray, centres: np.ndarray) -> np.ndarray:
    """Turns every triangle to face away from the nearest of `centres` (a part's axis points)."""
    T = np.asarray(T, dtype=np.int64).copy()
    c = P[T].mean(axis=1)
    d = np.linalg.norm(c[:, None, :] - centres[None, :, :], axis=2)
    out = c - centres[np.argmin(d, axis=1)]
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    bad = (fn * out).sum(axis=1) < 0
    T[bad] = T[bad][:, ::-1]
    return T


def facing(P: np.ndarray, T: np.ndarray, N: np.ndarray) -> np.ndarray:
    """Winds each triangle to face the mean of its vertices' normals N."""
    T = np.asarray(T, dtype=np.int64).copy()
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    bad = (fn * N[T].mean(axis=1)).sum(axis=1) < 0
    T[bad] = T[bad][:, ::-1]
    return T


def unit(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


# ---------------------------------------------------------------------------------------------
# Sculpting: lofted ring grids, displaced by muscle masses, grooves and stone noise
# ---------------------------------------------------------------------------------------------
class Grid:
    """A closed loft: a (K, S) ring grid along a path, capped to a point at each end. `P`, `N` and `d` (the
    displacement along the normal, + raised) cover the rings first (row-major), then the two caps."""

    def __init__(self, path, half_w, half_h, segs: int, up_hint=(0.0, 1.0, 0.0), squarish: float = 1.0,
                 half_lo=None, mod=None):
        path = np.asarray(path, dtype=np.float64)
        K = len(path)
        hw = np.broadcast_to(np.asarray(half_w, dtype=np.float64), (K,))
        hh = np.broadcast_to(np.asarray(half_h, dtype=np.float64), (K,))
        hl = hh if half_lo is None else np.broadcast_to(np.asarray(half_lo, dtype=np.float64), (K,))
        tan, nrm, bin_ = ck.frames_along(path, up_hint)
        a = np.arange(segs) * (2.0 * math.pi / segs)
        ca, sa = np.cos(a), np.sin(a)
        ca = np.sign(ca) * np.abs(ca) ** squarish
        sa = np.sign(sa) * np.abs(sa) ** squarish
        t = np.linspace(0.0, 1.0, K)
        m = np.ones((K, segs)) if mod is None else mod(t[:, None], a[None, :])
        H = np.where(ca[None] >= 0.0, hh[:, None], hl[:, None]) * ca[None] * m
        W = hw[:, None] * sa[None] * m
        G = path[:, None, :] + H[:, :, None] * nrm[:, None, :] + W[:, :, None] * bin_[:, None, :]
        self.K, self.S, self.path, self.t, self.a = K, segs, path, t, a
        P = np.vstack([G.reshape(-1, 3), path[:1] - tan[:1] * 0.004, path[-1:] + tan[-1:] * 0.004])
        T = ck.grid_tris(K, segs, True)
        s0, s1 = len(P) - 2, len(P) - 1
        caps = [(k, (k + 1) % segs, s0) for k in range(segs)]
        caps += [((K - 1) * segs + k, (K - 1) * segs + (k + 1) % segs, s1) for k in range(segs)]
        self.T = oriented(P, np.vstack([T, np.asarray(caps, dtype=np.int64)]), path)
        self.P = P
        self.N = ck.weld_normals(P, ck.vertex_normals(P, self.T))
        self.d = np.zeros(len(P))

    def sculpt(self, blobs=(), grooves=(), noise: float = 0.0, fine: float = 0.0, seed: int = 0,
               extra=None) -> "Grid":
        """Displaces along the normal: blobs (centre, radii (3,), amount), grooves (a, b, width, depth) along a
        segment, an `extra` (P, N) -> (n,) displacement, and the stone's lumps (`noise`) and pitting (`fine`)."""
        P, N = self.P, self.N
        d = np.zeros(len(P))
        for c, r, amp in blobs:
            d += amp * np.exp(-(((P - np.asarray(c)) / np.asarray(r)) ** 2).sum(axis=1))
        for a, b, w, depth in grooves:
            d -= depth * np.exp(-(seg_dist(P, a, b) / w) ** 2)
        if extra is not None:
            d += extra(P, N)
        if noise:
            d += noise * ck.fbm(P * 4.0, seed)
        if fine:
            d += fine * ck.fbm(P * 12.0, seed + 5)
        self.P = P + N * d[:, None]
        self.d = self.d + d
        self.N = ck.weld_normals(self.P, ck.vertex_normals(self.P, self.T))
        return self

    def uv(self, seam: float = math.pi) -> np.ndarray:
        """A detail coordinate in metres that wraps the part (along its path, and round it from the `seam` angle, where
        the noise may jump: put it where the camera does not look), so the shader's pitting is not smeared."""
        along = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(self.path, axis=0), axis=1))]
        G, _ = self.grid()
        rad = np.linalg.norm(G - self.path[:, None, :], axis=2).mean()
        ang = (self.a - seam) % (2.0 * math.pi)
        U = np.column_stack([np.repeat(along, self.S), np.tile(ang * rad, self.K)])
        return np.vstack([U, [[along[0], math.pi * rad], [along[-1], math.pi * rad]]])

    def grid(self) -> tuple[np.ndarray, np.ndarray]:
        n = self.K * self.S
        return self.P[:n].reshape(self.K, self.S, 3), self.N[:n].reshape(self.K, self.S, 3)

    def at(self, r: float, s: float) -> tuple[np.ndarray, np.ndarray]:
        """The surface point and normal at fractional ring r (0 .. K-1) and segment s (wraps)."""
        G, NG = self.grid()
        r = float(np.clip(r, 0.0, self.K - 1.001))
        r0 = int(math.floor(r))
        fr = r - r0
        s = s % self.S
        s0 = int(math.floor(s))
        fs = s - s0
        s1 = (s0 + 1) % self.S
        p = (G[r0, s0] * (1 - fr) * (1 - fs) + G[r0 + 1, s0] * fr * (1 - fs) + G[r0, s1] * (1 - fr) * fs
             + G[r0 + 1, s1] * fr * fs)
        n = (NG[r0, s0] * (1 - fr) * (1 - fs) + NG[r0 + 1, s0] * fr * (1 - fs) + NG[r0, s1] * (1 - fr) * fs
             + NG[r0 + 1, s1] * fr * fs)
        return p, unit(n)

    def spacing(self, r: float, s: float) -> tuple[float, float]:
        G, _ = self.grid()
        r0 = int(np.clip(r, 0, self.K - 2))
        s0 = int(s) % self.S
        return (float(np.linalg.norm(G[r0 + 1, s0] - G[r0, s0])) + 1e-4,
                float(np.linalg.norm(G[r0, (s0 + 1) % self.S] - G[r0, s0])) + 1e-4)


def seg_dist(P: np.ndarray, a, b) -> np.ndarray:
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    d = b - a
    t = np.clip(((P - a) @ d) / float(d @ d), 0.0, 1.0)
    return np.linalg.norm(P - (a + t[:, None] * d), axis=1)


def sym(items):
    """Blobs or grooves mirrored across x (the two sides of him)."""
    out = []
    for it in items:
        out.append(it)
        if len(it) == 3:
            c, r, amp = it
            out.append(((-c[0], c[1], c[2]), r, amp))
        else:
            a, b, w, depth = it
            out.append(((-a[0], a[1], a[2]), (-b[0], b[1], b[2]), w, depth))
    return out


def concavity(P: np.ndarray, T: np.ndarray, N: np.ndarray) -> np.ndarray:
    """How much each vertex sits in a hollow (the umbrella operator along the normal, per edge length): + concave."""
    e = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]])
    e = np.vstack([e, e[:, ::-1]])
    S = np.zeros_like(P)
    C = np.zeros(len(P))
    L = np.zeros(len(P))
    np.add.at(S, e[:, 0], P[e[:, 1]])
    np.add.at(C, e[:, 0], 1.0)
    np.add.at(L, e[:, 0], np.linalg.norm(P[e[:, 0]] - P[e[:, 1]], axis=1))
    C = np.maximum(C, 1.0)
    lap = S / C[:, None] - P
    return (lap * N).sum(axis=1) / np.maximum(L / C, 1e-4)


def hide(g: Grid, seed: int, ash: float = 0.45, under: float = 0.35):
    """Dark stone and old iron: charcoal to stone grey, mottled, ash in the grain of the upper surfaces and on the
    worn tops of the masses, darker underneath, and ember-warm down in the creases and cracks. Returns (col, cav)."""
    P, N, d = g.P, g.N, g.d
    conc = concavity(P, g.T, N)
    mott = ck.fbm(P * 1.7, seed)
    grain = ck.fbm(P * 6.5, seed + 3)
    col = ck.mix(CHAR, ck.mix(STONE, ASH, 0.32), (0.3 + 0.7 * ck.smoothstep(-0.35, 0.35, mott))[:, None])
    col = ck.mix(col, PAL["tortoiseshell"], 0.07 + 0.06 * ck.smoothstep(0.1, 0.5, -mott)[:, None])  # banked warmth
    col = ck.mix(col, PAL["lacquer_black"], (under * np.clip(-N[:, 1], 0.0, 1.0) ** 1.2)[:, None])
    up = np.clip(N[:, 1], 0.0, 1.0)
    worn = ck.smoothstep(0.01, 0.07, d)
    dusting = ash * up ** 1.4 * ck.smoothstep(-0.2, 0.35, grain) + 0.35 * worn * ck.smoothstep(-0.3, 0.2, grain)
    col = ck.mix(col, ASH, np.clip(dusting, 0.0, 0.65)[:, None])
    cav = np.clip(ck.smoothstep(0.03, 0.3, conc) + 0.8 * ck.smoothstep(-0.004, -0.03, d), 0.0, 1.0)
    col = ck.mix(col, EMBER, (0.75 * cav)[:, None])
    return col, cav * 0.85


def add_grid(mesh: ck.Mesh, g: Grid, slot: str, col, bones, *, wet=0.12, cavity=0.0, emission=0.0,
             seam: float = math.pi) -> None:
    ck.finish(mesh, g.P, g.T, slot, col, bones, wet=wet, cavity=cavity, emission=emission, N=g.N, uv=g.uv(seam))


def strip(mesh: ck.Mesh, pts: np.ndarray, nrm: np.ndarray, width, slot: str, col, bones, *, lift: float = 0.003,
          cavity=1.0, wet=0.1, emission=0.0) -> None:
    """A narrow strip laid on a surface along pts (K, 3) with its normals: a crack, a seam, a scar."""
    K = len(pts)
    p = pts + nrm * lift
    tan = np.gradient(p, axis=0)
    sd = unit(np.cross(nrm, tan))
    w = np.broadcast_to(np.asarray(width, dtype=np.float64), (K,))
    P = np.vstack([p - sd * w[:, None] * 0.5, p + sd * w[:, None] * 0.5])
    N = np.vstack([nrm, nrm])
    T = [(k, K + k, k + 1) for k in range(K - 1)] + [(k + 1, K + k, K + k + 1) for k in range(K - 1)]
    T = facing(P, np.asarray(T, dtype=np.int64), N)
    ck.finish(mesh, P, T, slot, col, bones, wet=wet, cavity=cavity, emission=emission, N=N)


def cracks(mesh: ck.Mesh, g: Grid, bones, rng, n: int, rows, segs, width: float = 0.011,
           step: float = 0.034, steps: int = 6) -> None:
    """Jagged cracks in the stone (a lightning-split pattern), walked over the grid: each a few kinked steps, some
    with a short branch; dark, ember-warm."""
    col = ck.mix(PAL["lacquer_black"], PAL["tortoiseshell"], 0.45)

    def walk(r, s, th, k):
        pts, nrms = [], []
        for _ in range(k):
            p, nn = g.at(r, s)
            pts.append(p)
            nrms.append(nn)
            lr, ls = g.spacing(r, s)
            r += step * math.cos(th) / lr
            s += step * math.sin(th) / ls
            th += float(rng.normal(0.0, 0.6))
        return np.array(pts), np.array(nrms), (r, s, th)

    for _ in range(n):
        r = float(rng.uniform(*rows))
        s = float(rng.uniform(*segs))
        th = float(rng.uniform(0.0, 2.0 * math.pi))
        pts, nrms, _ = walk(r, s, th, steps)
        w = width * np.linspace(1.0, 0.25, len(pts)) * float(rng.uniform(0.7, 1.2))
        strip(mesh, pts, nrms, w, "body", col, bones)
        if rng.uniform() < 0.5:  # a branch from a point part way along, turned off the main line
            j = int(rng.integers(1, steps - 2))
            q = g_nearest(g, pts[j])
            pts2, nrms2, _ = walk(q[0], q[1], th + float(rng.choice([-1.1, 1.1])), 4)
            pts2[0] = pts[j]
            strip(mesh, pts2, nrms2, width * np.linspace(0.6, 0.2, len(pts2)), "body", col, bones)


def g_nearest(g: Grid, p: np.ndarray) -> tuple[float, float]:
    G, _ = g.grid()
    i = int(np.argmin(np.linalg.norm(G.reshape(-1, 3) - p, axis=1)))
    return float(i // g.S), float(i % g.S)


def block(centre, half, R=None, rings: int = 8, segs: int = 16, power: float = 0.3):
    """A rounded box (a superellipsoid): `half` extents (x, y, z), turned by R."""
    P, T = ck.ellipsoid((0.0, 0.0, 0.0), (1.0, 1.0, 1.0), rings, segs)
    P = np.sign(P) * np.abs(P) ** power * np.asarray(half, dtype=np.float64)
    if R is not None:
        P = P @ np.asarray(R).T
    P = P + np.asarray(centre, dtype=np.float64)
    return P, oriented(P, T, np.asarray(centre, dtype=np.float64)[None])


def frame(up, fwd) -> np.ndarray:
    """Columns (side, up, fwd): a part's local axes from its up and a forward hint."""
    up = unit(up)
    side = unit(np.cross(up, fwd))
    return np.column_stack([side, up, np.cross(side, up)])


def plate(mesh: ck.Mesh, at, n, fwd, half, bones, rng, *, lift: float = 1.0, curve: float = 1.6) -> None:
    """A keratin scute laid on a surface point `at` (normal `n`), shingled toward the tail: a curved sheet with a low
    keel whose front and side edges sink into the hide and whose rear (free) edge stands proud over a lip; dark horn,
    worn pale along the free edge and dusted with ash on top. 24 triangles."""
    w, h, ln = half
    X, Z = (a.ravel() for a in np.meshgrid(np.linspace(-1.0, 1.0, 5), np.linspace(-1.0, 1.0, 3)))  # Z -1: the rear
    Y = h * (0.9 + 0.7 * lift * np.clip(-Z, 0.0, 1.0) + 0.35 * (1.0 - np.abs(X)) ** 2) - curve * h * X ** 2 \
        - 2.4 * h * np.clip(Z, 0.0, 1.0) ** 2
    top = np.column_stack([X * w, Y, Z * ln])
    rear = top[:5]
    lip = np.vstack([rear, rear * np.array([1.0, 0.0, 1.0]) + np.array([0.0, -1.5 * h, 0.04 * ln])])
    P = np.vstack([top, lip])
    T = np.vstack([ck.grid_tris(3, 5, False), ck.grid_tris(2, 5, False) + 15])
    hint = np.vstack([np.tile([0.0, 1.0, 0.0], (15, 1)), np.tile([0.0, 0.0, -1.0], (10, 1))])
    R = frame(n, fwd)
    P = P @ R.T + np.asarray(at, dtype=np.float64)
    T = facing(P, T, hint @ R.T)
    N = ck.vertex_normals(P, T)
    rim = ck.smoothstep(0.5, 1.0, np.maximum(np.abs(np.r_[X, X[:5], X[:5]]), np.abs(np.r_[Z, -np.ones(10)])))
    free = np.r_[ck.smoothstep(-0.6, -1.0, Z), np.full(5, 1.0), np.zeros(5)]
    col = ck.mix(ck.mix(HORN, CHAR, 0.35), ck.mix(HORN, STONE, 0.5), float(rng.uniform(0.0, 0.6)))
    col = ck.mix(col, ck.mix(HORN, ASH, 0.4), (0.4 * free)[:, None])  # the free edge, worn
    cav = np.r_[0.25 * (1.0 - free[:15]) * rim[:15], np.full(5, 0.1), np.ones(5)]
    ck.finish(mesh, P, T, "body", col, bones, wet=0.1, cavity=cav, N=N)


def armour_plate(mesh: ck.Mesh, g: Grid, r: float, s: float, half, bones, rng) -> None:
    """A forearm scute laid onto g's own surface around ring r and segment s (so its outline never meets the hide in
    a ragged line): a domed sheet that stands proudest at its rear (wrist) edge, then all round a clean bevelled lip,
    a little raised and worn pale, turning down over the hide to just under it, its foot a dark seam (cavity 1).
    `half` = (thickness, along) in metres; across, it spans two of g's segments each side of s, rounded to a whole
    segment, so its columns land on the hide's own vertices and it never chords under a bulge. 64 triangles."""
    h, ln = half
    s = float(round(s))
    hr, hs = ln / g.spacing(r, s)[0], 2.0  # the half extents in rings and segments
    X, Z = (a.ravel() for a in np.meshgrid(np.linspace(-1.0, 1.0, 5), np.linspace(-1.0, 1.0, 3)))  # Z -1: the rear
    ring = [0, 1, 2, 3, 4, 9, 14, 13, 12, 11, 10, 5]  # the top grid's outline, in order

    def lift(x, z):
        return h * (0.85 + 0.3 * (1.0 - x * x) + 0.8 * np.clip(-z, 0.0, 1.0))

    def on(x, z, up):  # the outline rounded: the ends bowed
        p, n = g.at(r - z * hr * (1.0 + 0.16 * (1.0 - x * x)), s + x * hs)
        return p + n * up

    top = np.array([on(x, z, lift(x, z)) for x, z in zip(X, Z)])
    xo, zo = X[ring], Z[ring]
    lip = np.array([on(x * 1.07, z * 1.1, lift(x, z) + 0.22 * h) for x, z in zip(xo, zo)])
    foot = np.array([on(x * 1.16, z * 1.22, -0.004) for x, z in zip(xo, zo)])
    m = len(ring)
    P = np.vstack([top, top[ring], lip, foot])  # the outline doubled, so the bevel keeps a crisp edge
    e, li, fo = 15, 15 + m, 15 + 2 * m
    band = []
    for k in range(m):
        k1 = (k + 1) % m
        for a0, a1, b0, b1 in ((e + k, e + k1, li + k, li + k1), (li + k, li + k1, fo + k, fo + k1)):
            band += [(a0, b0, a1), (a1, b0, b1)]
    T = np.vstack([ck.grid_tris(3, 5, False), np.asarray(band, dtype=np.int64)])
    T = oriented(P, T, g.at(r, s)[0][None] - g.at(r, s)[1][None] * 0.15)
    N = ck.vertex_normals(P, T)
    free = np.r_[ck.smoothstep(-0.4, -1.0, Z), ck.smoothstep(-0.4, -1.0, zo), ck.smoothstep(-0.4, -1.0, zo),
                 np.zeros(m)]
    col = ck.mix(ck.mix(HORN, CHAR, 0.35), ck.mix(HORN, STONE, 0.5), float(rng.uniform(0.0, 0.6)))
    col = np.tile(col, (len(P), 1))
    col = ck.mix(col, ck.mix(HORN, ASH, 0.4), (0.4 * free)[:, None])  # the free edge, worn
    col[li:fo] = ck.mix(col[li:fo], ck.mix(HORN, ASH, 0.55), 0.6)  # the lip, worn pale all round
    col[fo:] = ck.mix(PAL["lacquer_black"], PAL["tortoiseshell"], 0.25)  # the seam under it
    cav = np.r_[np.full(15 + m, 0.1), np.zeros(m), np.ones(m)]
    ck.finish(mesh, P, T, "body", col, bones, wet=0.1, cavity=cav, N=N)


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def neck_points() -> np.ndarray:
    return ck.bezier(NECK_PATH, 31)[::10]  # four points, three spans: neck_0 .. neck_2


def leg_joints(leg: str) -> np.ndarray:
    _, x, J, _ = LEGS[leg]
    return np.column_stack([np.full(len(J), x), J[:, 0], J[:, 1]])


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    rig.add("body", HIP, (0.0, 1.75, 0.2), "root")
    rig.add("chest", CHEST, (0.0, 2.05, 0.7), "body")
    pts = neck_points()
    parent = "chest"
    for k in range(3):
        rig.add(f"neck_{k}", pts[k], pts[k + 1], parent)
        parent = f"neck_{k}"
    rig.add("head", pts[3], HEAD_TIP, "neck_2")
    rig.add("jaw", JAW_HINGE, MANDIBLE[-1], "head")
    for leg, (bones, _x, _J, parent) in LEGS.items():
        j = leg_joints(leg)
        p = parent
        for k, b in enumerate(bones):
            rig.add(b, j[k], j[k + 1], p)
            p = b
    rig.add("tail_0", TAIL_PTS[0], TAIL_PTS[1], "body")
    rig.add("tail_1", TAIL_PTS[1], TAIL_PTS[2], "tail_0")
    # M3-CRB-008: the VFX anchors, unweighted (no vertex is skinned to them)
    rig.add("vfx_core", VFX_CORE, VFX_CORE + (0.0, 0.2, 0.0), "chest")
    hc = hammer_centre()
    rig.add("vfx_keepsake", hc, hc + (0.0, 0.15, 0.0), "head")
    return rig


# ---------------------------------------------------------------------------------------------
# The head's measures (the casque sits on the bill and the skull; the hammer stands in the casque)
# ---------------------------------------------------------------------------------------------
def _bill_profile(n: int = 200):
    path = ck.bezier(BILL, n)
    t = np.linspace(0.0, 1.0, n)
    return path, 0.078 * (1.0 - t) ** 0.9 + 0.008, 0.125 * (1.0 - t) ** 0.8 + 0.01


def casque_floor(z):
    """The top of the skull and bill under the casque at z."""
    z = np.asarray(z, dtype=np.float64)
    path, _hw, hh = _bill_profile()
    bill = np.interp(z, path[:, 2], path[:, 1] + hh, left=-1.0, right=-1.0)
    skull = SKULL_C[1] + SKULL_R[1] * np.sqrt(np.clip(1.0 - ((z - SKULL_C[2]) / SKULL_R[2]) ** 2, 0.0, 1.0))
    return np.maximum(bill, skull)


def casque_shape(t):
    """The casque along its length (t 0 at the brow .. 1 at its tip): (z, bottom, top, half width). It rises from
    the brow to a tall keel over the bill, and its front sweeps up off the bill into an upturned horn."""
    t = np.asarray(t, dtype=np.float64)
    z = CASQUE_Z[0] + (CASQUE_Z[1] - CASQUE_Z[0]) * t
    floor = casque_floor(z) - 0.03
    top = floor + 0.035 + 0.2 * t ** 0.75 + 0.15 * ck.smoothstep(0.5, 1.0, t) ** 1.5
    bottom = floor + (top - floor) * 0.86 * ck.smoothstep(0.8, 1.0, t)
    hw = (0.035 + 0.04 * np.sin(math.pi * np.clip(0.12 + 0.8 * t, 0.0, 1.0))) \
        * (1.0 - 0.6 * ck.smoothstep(0.82, 1.0, t)) + 0.008
    return z, bottom, top, hw


def casque_ridges(a):
    """Where the casque's flanks are grooved along its length (1 in a groove), by the angle round it."""
    return (0.5 + 0.5 * np.cos(5.0 * np.asarray(a, dtype=np.float64))) ** 4


def casque_bands(t):
    """Where its growth lines cross it (1 on a line), along its length."""
    return (0.5 + 0.5 * np.cos(2.0 * math.pi * 6.5 * np.asarray(t, dtype=np.float64))) ** 8


def casque_top(z) -> float:
    t = (z - CASQUE_Z[0]) / (CASQUE_Z[1] - CASQUE_Z[0])
    return float(casque_shape(t)[2])


def hammer_axes():
    r = math.radians(HANDLE_RAKE)
    up = np.array([0.0, math.cos(r), -math.sin(r)])
    fwd = np.array([0.0, math.sin(r), math.cos(r)])
    base = np.array([0.0, casque_top(HAMMER_Z), HAMMER_Z])
    return base, up, fwd


def hammer_centre() -> np.ndarray:
    base, up, _ = hammer_axes()
    return base + up * HANDLE_VIS


def ribbon(points: np.ndarray, widths: np.ndarray, side: np.ndarray, normal: np.ndarray, thick: float):
    """A flat two-faced blade along `points` (K, 3), `widths` across `side` (one vector or (K, 3)), the faces `thick`
    apart along `normal`. Returns (P, T, N)."""
    K = len(points)
    side = np.broadcast_to(np.asarray(side, dtype=np.float64), (K, 3))
    nk = np.broadcast_to(np.asarray(normal, dtype=np.float64), (K, 3))
    L = points - side * widths[:, None] * 0.5
    R = points + side * widths[:, None] * 0.5
    P = np.vstack([L + nk * thick * 0.5, R + nk * thick * 0.5, L - nk * thick * 0.5, R - nk * thick * 0.5])
    T = []
    for f in (0, 1):
        b = f * 2 * K
        for k in range(K - 1):
            T += [(b + k, b + K + k, b + k + 1), (b + k + 1, b + K + k, b + K + k + 1)]
    T = np.asarray(T, dtype=np.int64)
    N = np.vstack([nk, nk, -nk, -nk])
    return P, facing(P, T, N), N


def smooth_table(table, n: int) -> np.ndarray:
    """The rows of `table` (control rows) resampled to n rows, smoothly (a Gaussian-smoothed polyline)."""
    c = np.asarray(table, dtype=np.float64)
    u = np.linspace(0.0, 1.0, len(c))
    fine = np.linspace(0.0, 1.0, 400)
    sig = 400.0 / len(c) * 0.45
    k = np.exp(-0.5 * (np.arange(-60, 61) / sig) ** 2)
    k /= k.sum()
    out = []
    for j in range(c.shape[1]):
        col = np.interp(fine, u, c[:, j])
        pad = np.concatenate([np.full(60, col[0]), col, np.full(60, col[-1])])
        sm = np.convolve(pad, k, mode="same")[60:-60]
        out.append(np.interp(np.linspace(0.0, 1.0, n), fine, sm))
    return np.column_stack(out)


def surf_side(g: Grid, y: float, z: float, side: float) -> np.ndarray:
    """The point of g's surface at height y and depth z on one side (the sign of x)."""
    G, _ = g.grid()
    Q = G.reshape(-1, 3)
    cost = (Q[:, 1] - y) ** 2 + (Q[:, 2] - z) ** 2 + np.where(Q[:, 0] * side > 0, 0.0, 99.0)
    return Q[int(np.argmin(cost))]


def surf_top(g: Grid, x: float, z: float) -> tuple[np.ndarray, np.ndarray]:
    """The upper surface of g over (x, z) (its four nearest upward vertices, weighted), and its normal."""
    G, NG = g.grid()
    Q, NQ = G.reshape(-1, 3), NG.reshape(-1, 3)
    dist = np.hypot(Q[:, 0] - x, Q[:, 2] - z) + np.where(NQ[:, 1] > 0.05, 0.0, 9.0)
    near = np.argsort(dist)[:4]
    wt = 1.0 / (dist[near] + 1e-3)
    wt /= wt.sum()
    return (Q[near] * wt[:, None]).sum(axis=0), unit((NQ[near] * wt[:, None]).sum(axis=0))


# ---------------------------------------------------------------------------------------------
# Mesh: the torso, neck and head
# ---------------------------------------------------------------------------------------------
def torso_skin(rig: ck.Rig):
    return rig.blend("body", "chest", (0.0, 1.55, -0.1), (0.0, 1.85, 0.45))


def torso(mesh: ck.Mesh, rig: ck.Rig) -> Grid:
    c = smooth_table(TORSO, TORSO_RINGS)
    path = np.column_stack([np.zeros(len(c)), c[:, 1], c[:, 0]])
    g = Grid(path, c[:, 2], c[:, 3], TORSO_SEGS, half_lo=c[:, 4])
    grooves = []
    for s in (1.0, -1.0):
        for k in range(4):  # the ribs under the hide
            z0 = -0.12 + 0.14 * k
            a, b = surf_side(g, 2.02 - 0.02 * k, z0 - 0.04, s), surf_side(g, 1.42, z0 + 0.08, s)
            grooves.append((a, b, 0.026, 0.016))
        grooves.append((surf_side(g, 2.30, -0.08, s), surf_side(g, 1.98, -0.02, s), 0.03, 0.03))  # behind the scapula
        grooves.append((surf_side(g, 1.42, 0.30, s), surf_side(g, 1.26, 0.58, s), 0.04, 0.02))  # under the pectoral
        grooves.append((surf_side(g, 1.78, -0.42, s), surf_side(g, 1.32, -0.36, s), 0.04, 0.025))  # the haunch's front
    grooves.append(((0.0, 2.05, -0.82), (0.0, 2.47, 0.0), 0.045, 0.025))  # the spine's furrow
    blobs = [((0.0, 2.40, 0.2), (0.42, 0.24, 0.38), 0.16), ((0.0, 1.10, -0.25), (0.36, 0.12, 0.32), -0.06)]
    blobs += sym([
        ((0.22, 2.32, 0.46), (0.16, 0.18, 0.24), 0.05),  # trapezius, up into the neck
        ((0.56, 2.0, 0.42), (0.22, 0.3, 0.28), 0.12),  # the shoulder's mass
        ((0.40, 2.24, 0.12), (0.13, 0.22, 0.17), 0.07),  # scapula
        ((0.27, 1.52, 0.66), (0.16, 0.17, 0.15), 0.05),  # pectoral
        ((0.36, 1.62, -0.56), (0.18, 0.20, 0.22), 0.07),  # haunch
        ((0.47, 1.70, -0.20), (0.10, 0.14, 0.30), 0.025),  # the flank
    ])
    g.sculpt(blobs, grooves, noise=0.022, fine=0.008, seed=SEED,
             extra=lambda P, N: 0.012 * ck.fbm(P * 7.5, SEED + 9))  # the stone's lumps
    col, cav = hide(g, SEED)
    skin = torso_skin(rig)
    before = mesh.triangle_count
    add_grid(mesh, g, "body", col, skin, cavity=cav)
    count("torso", mesh, before)
    SURF["torso"] = g.P
    rng = np.random.default_rng(SEED + 21)
    before = mesh.triangle_count
    S = TORSO_SEGS
    for lo, hi in ((0.1, 0.38), (0.62, 0.9)):
        cracks(mesh, g, skin, rng, 8, (5, TORSO_RINGS - 6), (S * lo, S * hi))
    count("cracks", mesh, before)
    before = mesh.triangle_count
    for x, z0, half in ((0.0, 0.04, (0.105, 0.032, 0.1)), (0.18, -0.03, (0.1, 0.03, 0.1)),
                        (0.35, 0.04, (0.09, 0.026, 0.09))):
        for sx in ((1.0,) if x == 0.0 else (1.0, -1.0)):
            for z in np.arange(z0, -0.8, -0.14):
                at, n = surf_top(g, sx * x, z)
                if n[1] > 0.35:
                    plate(mesh, at, n, (0.0, 0.0, 1.0), half, skin, rng)
    count("plates", mesh, before)
    return g


def neck_chain(rig: ck.Rig):
    pts = neck_points()
    return rig.chain(["chest", "neck_0", "neck_1", "neck_2", "head"],
                     np.vstack([[CHEST], pts, [pts[3] + (0.0, 0.03, 0.2)]]))


def neck(mesh: ck.Mesh, rig: ck.Rig) -> Grid:
    path = ck.bezier(((0.0, 1.80, 0.28),) + NECK_PATH[1:] + ((0.0, 2.68, 1.10),), 24)
    t = np.linspace(0.0, 1.0, len(path))
    hw = 0.28 * (1.0 - t) ** 1.4 + 0.115
    hh = 0.33 * (1.0 - t) ** 1.4 + 0.125
    g = Grid(path, hw, hh, 20, up_hint=(0.0, 0.6, -0.8))
    _tan, nrm, _ = ck.frames_along(path, (0.0, 0.6, -0.8))
    grooves, blobs = [], []
    for tt in (0.34, 0.44, 0.54, 0.64, 0.74, 0.84):  # the throat's folds
        k = int(round(tt * (len(path) - 1)))
        p = path[k] - nrm[k] * hh[k]
        grooves.append(((-0.22, p[1], p[2]), (0.22, p[1], p[2]), 0.02, 0.022))
    for tt, amp in ((0.55, 0.05), (0.78, 0.04)):  # the nape's muscle, up into the skull
        k = int(round(tt * (len(path) - 1)))
        blobs.append((path[k] + nrm[k] * hh[k] * 0.8, (0.14, 0.12, 0.16), amp))
    for tt in (0.25, 0.45, 0.65):  # the cords down each side of the neck
        k = int(round(tt * (len(path) - 1)))
        blobs += sym([((hw[k] * 0.85, path[k][1] - 0.04, path[k][2] + 0.04), (0.06, 0.16, 0.1), 0.04)])
    g.sculpt(blobs, grooves, noise=0.016, fine=0.006, seed=SEED + 1,
             extra=lambda P, N: 0.01 * ck.fbm(P * 7.5, SEED + 10))
    col, cav = hide(g, SEED + 1)
    chain = neck_chain(rig)
    before = mesh.triangle_count
    add_grid(mesh, g, "body", col, chain, cavity=cav)
    count("neck", mesh, before)
    SURF["neck"] = g.P
    rng = np.random.default_rng(SEED + 23)
    before = mesh.triangle_count
    for lo, hi in ((0.12, 0.36), (0.64, 0.88)):
        cracks(mesh, g, chain, rng, 3, (3, 17), (20 * lo, 20 * hi), width=0.009)
    count("cracks", mesh, before)
    return g


def head(mesh: ck.Mesh, rig: ck.Rig) -> None:
    hb = rig.rigid("head")
    before = mesh.triangle_count
    zs = np.linspace(SKULL_C[2] - SKULL_R[2], SKULL_C[2] + SKULL_R[2], 12)
    u = (zs - SKULL_C[2]) / SKULL_R[2]
    prof = np.sqrt(np.clip(1.0 - u ** 2, 0.0, 1.0)) ** 0.9
    path = np.column_stack([np.zeros(12), np.full(12, SKULL_C[1]), zs])
    g = Grid(path, SKULL_R[0] * prof + 0.004, SKULL_R[1] * prof + 0.004, 16)
    g.sculpt(sym([((0.11, 2.79, 1.17), (0.055, 0.03, 0.08), 0.035),  # the brow over each eye
                  ((0.13, 2.60, 1.09), (0.05, 0.06, 0.08), 0.02),  # the cheek
                  ((EYE_AT[0] + 0.02, EYE_AT[1], EYE_AT[2]), (0.035, 0.032, 0.042), -0.025)]),  # the socket
             noise=0.006, fine=0.003, seed=SEED + 2)
    col, cav = hide(g, SEED + 2, ash=0.18)
    add_grid(mesh, g, "body", col, hb, cavity=cav)
    count("skull", mesh, before)
    before = mesh.triangle_count
    for s in (1.0, -1.0):
        c = np.array([s * EYE_AT[0], EYE_AT[1], EYE_AT[2]])
        Pe, Te = ck.ellipsoid(c, (0.033, 0.029, 0.034), 5, 8)
        ck.finish(mesh, Pe, Te, "eye", PAL["deep_teal_shadow"], hb, wet=1.0, emission=0.6)
        for k, ph in enumerate(np.linspace(-0.9, 0.9, 5)):  # a ground hornbill's heavy lashes over the eye
            b = c + np.array([s * 0.014, 0.034 * math.cos(ph) + 0.004, 0.036 * math.sin(ph)])
            d = unit(np.array([s * 0.7, 0.75 + 0.2 * math.cos(ph), 0.35 * math.sin(ph) - 0.2]))
            pts = np.array([b, b + d * 0.025, b + d * (0.045 + 0.006 * (k % 2))])
            side = unit(np.cross(d, (s, 0.0, 0.0)))
            Pl, Tl, Nl = ribbon(pts, np.array([0.009, 0.006, 0.001]), side, unit(np.cross(side, d)), 0.002)
            ck.finish(mesh, Pl, Tl, "body", PAL["lacquer_black"], hb, wet=0.2, N=Nl)
    count("eyes", mesh, before)
    before = mesh.triangle_count
    path, _hw, _hh = _bill_profile(18)
    t = np.linspace(0.0, 1.0, len(path))
    bw = 0.078 * (1.0 - t) ** 0.9 + 0.008
    bh = 0.125 * (1.0 - t) ** 0.8 + 0.01

    def culmen(tt, a):  # a ridge along the top, a keen cutting edge along the bottom
        return 1.0 + 0.1 * np.clip(np.cos(a), 0.0, 1.0) ** 10 + 0.06 * np.clip(-np.cos(a), 0.0, 1.0) ** 14

    g = Grid(path, bw, bh, 12, squarish=0.85, mod=culmen)
    g.sculpt(noise=0.002, fine=0.0015, seed=SEED + 4)
    k = np.clip((g.P[:, 2] - BILL[0][2]) / (BILL[-1][2] - BILL[0][2]), 0.0, 1.0)
    streak = ck.fbm(g.P * np.array([30.0, 30.0, 3.0]), SEED + 31)
    col = ck.mix(HORN, IVORY, ck.smoothstep(0.15, 0.5, k + 0.08 * streak)[:, None])
    col = ck.mix(col, ck.mix(IVORY, HORN, 0.6), (ck.smoothstep(0.82, 1.0, k) * 0.8)[:, None])  # the worn tip
    col = ck.mix(col, ASH, (0.2 * ck.smoothstep(0.1, 0.5, streak))[:, None])
    ck.finish(mesh, g.P, g.T, "beak", col, hb, wet=0.25, cavity=np.clip(concavity(g.P, g.T, g.N) * 2, 0, 0.6), N=g.N)
    path = ck.bezier(MANDIBLE, 14)
    t = np.linspace(0.0, 1.0, len(path))
    g = Grid(path, 0.062 * (1.0 - t) ** 0.9 + 0.007, 0.062 * (1.0 - t) ** 0.8 + 0.008, 10, squarish=0.85)
    g.sculpt(noise=0.002, seed=SEED + 5)
    k = np.clip((g.P[:, 2] - MANDIBLE[0][2]) / (MANDIBLE[-1][2] - MANDIBLE[0][2]), 0.0, 1.0)
    col = ck.mix(HORN, IVORY, ck.smoothstep(0.1, 0.45, k)[:, None])
    col = ck.mix(col, ck.mix(IVORY, HORN, 0.6), (ck.smoothstep(0.82, 1.0, k) * 0.8)[:, None])
    ck.finish(mesh, g.P, g.T, "beak", col, rig.rigid("jaw"), wet=0.25, N=g.N)
    count("bill", mesh, before)
    casque(mesh, rig)


def casque(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Massive and sculpted: a tall, laterally flat helmet along the bill, its front upturned, ridged along its
    flanks and banded across with growth lines; worn ivory over brass."""
    hb = rig.rigid("head")
    K = 26
    t = np.linspace(0.0, 1.0, K)
    z, bottom, top, hw = casque_shape(t)
    path = np.column_stack([np.zeros(K), (bottom + top) * 0.5, z])
    H = top - bottom

    def sculpted(tt, a):
        flank = np.abs(np.sin(a))
        ridges = 1.0 - 0.12 * casque_ridges(a) * flank
        bands = 1.0 - 0.06 * casque_bands(tt)
        return (1.0 + 0.3 * np.clip(-np.cos(a), 0.0, 1.0)) * ridges * bands

    g = Grid(path, hw, H * 0.5, 20, squarish=0.7, mod=sculpted)
    g.sculpt(noise=0.004, fine=0.002, seed=SEED + 6)
    conc = concavity(g.P, g.T, g.N)
    top = ck.smoothstep(0.35, 0.85, g.N[:, 1])
    wear = ck.smoothstep(0.0, 0.45, ck.fbm(g.P * 7.0, SEED + 33))
    col = ck.mix(ck.mix(PAL["brass"], HORN, 0.25), PAL["brass"], ck.smoothstep(-0.3, 0.3, g.N[:, 1])[:, None])
    col = ck.mix(col, IVORY, np.clip(0.85 * top + 0.35 * wear, 0.0, 1.0)[:, None])
    col = ck.mix(col, ck.mix(PAL["brass"], HORN, 0.75), ck.smoothstep(0.01, 0.12, conc)[:, None])
    tv = np.r_[np.repeat(g.t, g.S), 0.0, 1.0]
    av = np.r_[np.tile(g.a, g.K), 0.0, 0.0]
    groove = np.clip(0.8 * casque_ridges(av) * np.abs(np.sin(av)) + 0.9 * casque_bands(tv), 0.0, 1.0)
    col = ck.mix(col, ck.mix(PAL["brass"], HORN, 0.8), (0.6 * groove * (1.0 - 0.6 * top))[:, None])
    streak = ck.fbm(g.P * np.array([40.0, 40.0, 4.0]), SEED + 35)  # the grain of the horn, along its length
    col = ck.mix(col, ck.mix(PAL["brass"], HORN, 0.5), (0.35 * ck.smoothstep(0.05, 0.4, streak))[:, None])
    front = ck.smoothstep(0.9, 1.0, (g.P[:, 2] - CASQUE_Z[0]) / (CASQUE_Z[1] - CASQUE_Z[0]))
    col = ck.mix(col, IVORY, (0.5 * front)[:, None])
    before = mesh.triangle_count
    ck.finish(mesh, g.P, g.T, "beak", col, hb, wet=0.3, cavity=np.clip(conc * 3.0, 0.0, 0.8), N=g.N)
    count("casque", mesh, before)


def hammer(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The keepsake, fused into the casque: the handle is sunk into it at a slant, the casque's keratin has grown up
    round the handle's lower half in layered ridges (growth lines, split by a crack where it grew), a leather wrap
    over the worn ash above that, and the octagonal forged head lies along the crest, face forward, its underside
    resting on the casque's hump, its face worn bright."""
    hb = rig.rigid("head")
    base, up, fwd = hammer_axes()
    side = np.array([1.0, 0.0, 0.0])
    centre = hammer_centre()
    before = mesh.triangle_count
    # the handle: thick, worn ash, from deep in the casque up through the head's eye
    K = 8
    path = np.array([base + up * f for f in np.linspace(-0.1, HANDLE_VIS + 0.09, K)])
    t = np.linspace(0.0, 1.0, K)
    r = HANDLE_R * (1.0 - 0.08 * ck.smoothstep(0.6, 0.8, t))
    g = Grid(path, r, r * 0.88, 10, up_hint=(0.0, 0.0, 1.0))
    g.sculpt(noise=0.002, seed=SEED + 41)
    grain = ck.fbm(g.P * np.array([70.0, 5.0, 70.0]), SEED + 43)
    col = ck.mix(PAL["timber_weathered"], ck.mix(PAL["timber_weathered"], PAL["lacquer_black"], 0.45),
                 ck.smoothstep(-0.1, 0.4, grain)[:, None])
    col = ck.mix(col, ck.mix(PAL["timber_weathered"], PAL["sand_cloth"], 0.4),  # worn pale where it is gripped
                 (0.5 * ck.smoothstep(0.1, 0.6, -grain))[:, None])
    ck.finish(mesh, g.P, g.T, "hammer", col, hb, wet=0.05, cavity=0.15, N=g.N)
    count("handle", mesh, before)
    # the leather wrap, wound over the handle between the growth and the head
    before = mesh.triangle_count
    n_steps, turns, h0, h1 = 22, 2.6, GROWTH - 0.004, HANDLE_VIS - 0.098
    ph = np.linspace(0.0, 2.0 * math.pi * turns, n_steps)
    h = np.linspace(h0, h1, n_steps)
    rad = np.full(n_steps, HANDLE_R * 1.05)
    radial = np.outer(np.cos(ph), side) * 1.0 + np.outer(np.sin(ph), fwd) * 0.88
    axis = base + np.outer(h, up)
    rows = [axis + radial * (rad + dr)[:, None] + up * dh
            for dr, dh in ((-0.002, -0.011), (0.005, -0.008), (0.005, 0.009), (-0.002, 0.012))]
    P = np.stack(rows, axis=1).reshape(-1, 3)
    T = ck.grid_tris(n_steps, 4, False)
    Nn = np.repeat(radial, 4, axis=0) + np.tile(np.array([[-1.0], [0.0], [0.0], [1.0]]), (n_steps, 1)) * up * 0.6
    T = facing(P, T, Nn)
    worn = ck.smoothstep(0.0, 0.5, ck.fbm(P * 40.0, SEED + 45))
    col = ck.mix(LEATHER, ck.mix(LEATHER, PAL["sand_cloth"], 0.35), worn[:, None])
    ck.finish(mesh, P, T, "hammer", col, hb, wet=0.1, cavity=np.tile([0.6, 0.0, 0.0, 0.6], n_steps))
    count("leather", mesh, before)
    # the growth: the casque's keratin grown up round the handle's foot in three layered ridges, each a shelf whose
    # lip overhangs the one below and wanders round it (higher on one side, as growth lines do), flaring into the
    # casque's flanks (long along the crest, flat across it like the casque), split up its front by a crack where
    # the growth tore round the wood
    before = mesh.triangle_count
    K, S, top = 16, 14, GROWTH
    path = np.array([base + up * f for f in np.linspace(-0.05, top, K)])
    t = np.linspace(0.0, 1.0, K)
    layers = 3.0
    rc = HANDLE_R * 1.04 + 0.075 * (1.0 - t) ** 1.7
    rc[-1] = HANDLE_R * 1.0
    crack_a = 0.35  # round from the front

    def layer(tt, a):  # where in its growth layer a point is (0 at a layer's foot .. 1 at its lip)
        return (tt * layers + 0.22 * np.sin(2.0 * a + 0.7) + 0.12 * np.sin(3.0 * a + 2.0)) % 1.0

    def crack(a, w):
        return np.exp(-(((a - crack_a + math.pi) % (2 * math.pi) - math.pi) / w) ** 2)

    def grown(tt, a):
        u = layer(tt, a)
        shelf = 0.14 * ck.smoothstep(0.5, 0.92, u) * (1.0 - ck.smoothstep(0.93, 1.0, u))  # each ridge's lip
        climb = 1.0 + 0.12 * np.cos(a - 1.2) * tt  # it has climbed further up one side
        return (1.0 + shelf * (1.0 - ck.smoothstep(0.85, 1.0, tt))) * (1.0 - 0.3 * crack(a, 0.14)) * climb

    flat = np.minimum(rc * 0.82, casque_shape((HAMMER_Z - CASQUE_Z[0]) / (CASQUE_Z[1] - CASQUE_Z[0]))[3] * 0.92)
    g = Grid(path, np.maximum(flat, HANDLE_R * 1.0), rc * 1.3, S, up_hint=tuple(fwd), mod=grown)
    g.sculpt(noise=0.006, fine=0.003, seed=SEED + 47)
    conc = concavity(g.P, g.T, g.N)
    k = np.clip((g.P - base) @ up / top, 0.0, 1.0)
    av = np.r_[np.tile(g.a, K), 0.0, 0.0]
    tv = np.r_[np.repeat(t, S), 0.0, 1.0]
    uv_ = layer(tv, av)
    split = crack(av, 0.09) * (1.0 - 0.5 * tv)
    col = ck.mix(PAL["brass"], IVORY, (0.35 + 0.45 * k)[:, None])  # the casque's ivory over brass, paler new growth
    col = ck.mix(col, ck.mix(PAL["brass"], HORN, 0.8), (0.75 * ck.smoothstep(0.35, 0.6, uv_)
                                                       * (1.0 - ck.smoothstep(0.6, 0.9, uv_)))[:, None])  # under a lip
    col = ck.mix(col, ck.mix(PAL["brass"], HORN, 0.7), ck.smoothstep(0.02, 0.2, conc)[:, None])
    col = ck.mix(col, ck.mix(PAL["lacquer_black"], PAL["tortoiseshell"], 0.4), (0.9 * split)[:, None])  # the crack
    cav = np.clip(0.2 + 2.5 * np.clip(conc, 0.0, None) + split, 0.0, 1.0)
    ck.finish(mesh, g.P, g.T, "beak", col, hb, wet=0.3, cavity=cav, N=g.N)
    count("collar", mesh, before)
    # the head: an octagonal forged bar, the face end chamfered and slightly domed, the peen a cross wedge
    before = mesh.triangle_count
    stations = (  # (along, half up, half side)
        (HEAD_PEEN, 0.01, 0.088), (HEAD_PEEN + 0.035, 0.038, 0.092), (HEAD_PEEN + 0.12, 0.08, 0.095),
        (-0.13, 0.097, 0.097), (0.0, 0.1, 0.1), (0.13, 0.095, 0.095), (0.2, 0.082, 0.082), (0.25, 0.09, 0.09),
        (HEAD_FACE - 0.035, 0.104, 0.104), (HEAD_FACE - 0.014, 0.104, 0.104), (HEAD_FACE, 0.087, 0.087),
        (HEAD_FACE + 0.01, 0.045, 0.045),
    )
    a = np.arange(8) * (2.0 * math.pi / 8) + math.pi / 8
    oc = 1.0 / math.cos(math.pi / 8)
    rows, along = [], []
    for s, hu, hs in stations:
        rows.append(centre + fwd * s + np.outer(np.cos(a) * hu * oc, up) + np.outer(np.sin(a) * hs * oc, side))
        along.append(np.full(8, s))
    P = np.vstack(rows + [(centre + fwd * HEAD_PEEN)[None], (centre + fwd * (HEAD_FACE + 0.012))[None]])
    along = np.concatenate(along + [[HEAD_PEEN], [HEAD_FACE + 0.012]])
    nS = len(stations)
    T = ck.grid_tris(nS, 8, True)
    caps = [(k, (k + 1) % 8, len(P) - 2) for k in range(8)] + \
        [((nS - 1) * 8 + k, (nS - 1) * 8 + (k + 1) % 8, len(P) - 1) for k in range(8)]
    T = np.vstack([T, np.asarray(caps, dtype=np.int64)])
    T = oriented(P, T, centre + np.outer(np.linspace(HEAD_PEEN, HEAD_FACE, 20), fwd))
    rust = ck.smoothstep(0.1, 0.5, ck.fbm(P * 18.0, SEED + 49))
    col = ck.mix(IRON, ck.mix(IRON, PAL["tortoiseshell"], 0.5), (0.5 * rust)[:, None])
    face = ck.smoothstep(HEAD_FACE - 0.035, HEAD_FACE - 0.01, along)
    col = ck.mix(col, STEEL_HI, (0.85 * face)[:, None])
    col = ck.mix(col, STEEL, (0.7 * ck.smoothstep(HEAD_PEEN + 0.05, HEAD_PEEN, along))[:, None])
    ck.finish(mesh, P, T, "hammer", col, hb, wet=0.2 * face, cavity=0.1, flat=True)
    for k in range(8):  # the chamfers' worn edges catch the light
        ang = a[k]
        e = np.outer(np.full(5, math.cos(ang)), up) + np.outer(np.full(5, math.sin(ang)), side)
        s_ = np.linspace(-0.12, 0.24, 5)
        hu = np.interp(s_, [st[0] for st in stations], [st[1] for st in stations]) * oc
        pts = centre + np.outer(s_, fwd) + e * hu[:, None]
        strip(mesh, pts, e, 0.007, "hammer", STEEL, hb, lift=0.0015, cavity=0.0, wet=0.2)
    top = centre + up * 0.101  # the wedge in the eye, the handle's end grain on top
    Pw, Tw = block(top + up * 0.006, (0.026, 0.009, 0.048), frame(up, fwd), rings=4, segs=8, power=0.35)
    ck.finish(mesh, Pw, Tw, "hammer", ck.mix(PAL["timber_weathered"], PAL["lacquer_black"], 0.3), hb, cavity=0.3)
    count("hammer_head", mesh, before)


def anvil(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The sternum is a forged anvil: the face under his throat (worn bright, pocked with hammer scars, the hardy
    and pritchel holes at its heel), the step and the horn jutting forward, and the waist going down into the keel,
    with the bound-light star of an old strike on each flank."""
    cb = rig.rigid("chest")
    rng = np.random.default_rng(SEED + 51)
    before = mesh.triangle_count
    K = 12
    z = np.linspace(FACE_Z[0], FACE_Z[1], K)
    path = np.column_stack([np.zeros(K), np.full(K, FACE_Y - FACE_T * 0.5), z])
    g = Grid(path, FACE_HW, FACE_T * 0.5, 20, squarish=0.16)
    g.sculpt(noise=0.0025, seed=SEED + 52)
    P, N = g.P, g.N
    topf = ck.smoothstep(0.6, 0.95, N[:, 1])
    centre = 1.0 - np.clip(np.maximum(np.abs(P[:, 0]) / FACE_HW, np.abs(P[:, 2] - z.mean()) / 0.25), 0.0, 1.0)
    col = ck.mix(IRON, PAL["brass"], (0.35 * ck.smoothstep(0.2, 0.6, N[:, 1]) * (1.0 - topf))[:, None])
    col = ck.mix(col, ck.mix(STEEL, STEEL_HI, ck.smoothstep(0.0, 0.6, centre)[:, None]), topf[:, None])
    rust = ck.smoothstep(0.15, 0.5, ck.fbm(P * 14.0, SEED + 54)) * (1.0 - topf)
    col = ck.mix(col, ck.mix(IRON, PAL["tortoiseshell"], 0.6), (0.55 * rust)[:, None])
    ck.finish(mesh, P, g.T, "anvil", col, cb, wet=0.6 * topf, cavity=0.3 * (1.0 - topf), N=N)
    # the step (the table) before the horn
    Ps, Ts = block((0.0, FACE_Y - 0.085, FACE_Z[1] + 0.04), (0.13, 0.055, 0.055), rings=6, segs=12, power=0.3)
    ck.finish(mesh, Ps, Ts, "anvil", ck.mix(IRON, STEEL, 0.3), cb, wet=0.2, cavity=0.2)
    # the horn
    path = ck.bezier(ANVIL_HORN, 12)
    t = np.linspace(0.0, 1.0, len(path))
    g = Grid(path, 0.115 * (1.0 - t) ** 1.15 + 0.01, 0.08 * (1.0 - t) ** 1.05 + 0.009, 12)
    k = (g.P[:, 2] - ANVIL_HORN[0][2]) / (ANVIL_HORN[-1][2] - ANVIL_HORN[0][2])
    col = ck.mix(IRON, PAL["brass"], (0.7 * ck.smoothstep(0.7, 1.0, k))[:, None])
    col = ck.mix(col, STEEL, (0.4 * ck.smoothstep(0.4, 0.95, g.N[:, 1]) * ck.smoothstep(0.1, 0.7, k))[:, None])
    ck.finish(mesh, g.P, g.T, "anvil", col, cb, wet=0.3, cavity=0.1, N=g.N)
    # the waist: pinched, then flaring to its feet in the keel
    K = 10
    path = ck.bezier((WAIST[0], (0.0, 1.56, 0.84), WAIST[1]), K)
    t = np.linspace(0.0, 1.0, K)
    pinch = 1.0 - 0.34 * np.sin(math.pi * np.clip(t * 1.25, 0, 1)) ** 1.3
    g = Grid(path, (0.17 + 0.03 * t) * pinch, (0.25 + 0.02 * t) * pinch, 14, up_hint=(0.0, 0.0, 1.0), squarish=0.4)
    g.sculpt(noise=0.004, seed=SEED + 55)
    rust = ck.smoothstep(0.1, 0.5, ck.fbm(g.P * 12.0, SEED + 56))
    col = ck.mix(IRON, ck.mix(IRON, PAL["tortoiseshell"], 0.55), (0.6 * rust)[:, None])
    ck.finish(mesh, g.P, g.T, "anvil", col, cb, wet=0.1, cavity=np.clip(concavity(g.P, g.T, g.N) * 3, 0, 0.6), N=g.N)
    waist = g
    # the hardy hole (square) and the pritchel hole (round) at the heel, and the scars of old blows on the face
    yt = FACE_Y + 0.0015
    up = np.array([0.0, 1.0, 0.0])
    for cx, cz, shape in ((0.065, FACE_Z[0] + 0.12, 4), (-0.07, FACE_Z[0] + 0.12, 10)):
        r = 0.032 if shape == 4 else 0.017
        ang = np.arange(shape) * 2.0 * math.pi / shape + (math.pi / 4 if shape == 4 else 0.0)
        ring = np.column_stack([cx + r * np.cos(ang), np.full(shape, yt), cz + r * np.sin(ang)])
        rim = np.column_stack([cx + r * 1.35 * np.cos(ang), np.full(shape, yt - 0.0005), cz + r * 1.35 * np.sin(ang)])
        P = np.vstack([ring, rim, [[cx, yt, cz]]])
        T = [(i, (i + 1) % shape, 2 * shape) for i in range(shape)]
        T += [(shape + i, shape + (i + 1) % shape, i) for i in range(shape)]
        T += [((i + 1) % shape, i, shape + (i + 1) % shape) for i in range(shape)]
        Nu = np.tile(up, (len(P), 1))
        T = facing(P, np.asarray(T, dtype=np.int64), Nu)
        col = np.vstack([np.tile(PAL["lacquer_black"], (shape, 1)), np.tile(IRON, (shape, 1)), [PAL["lacquer_black"]]])
        ck.finish(mesh, P, T, "anvil", col, cb, cavity=np.r_[np.ones(shape), np.full(shape, 0.4), 1.0], N=Nu)
    for _ in range(16):
        cx = float(rng.uniform(-0.14, 0.14))
        cz = float(rng.uniform(FACE_Z[0] + 0.2, FACE_Z[1] - 0.04))
        r = float(rng.uniform(0.008, 0.02))
        sq = float(rng.uniform(0.4, 1.0))
        ang = np.arange(7) * 2.0 * math.pi / 7 + float(rng.uniform(0, 1))
        rr = r * (1.0 + 0.25 * np.sin(3 * ang))
        P = np.vstack([[[cx, yt + 0.0003, cz]],
                       np.column_stack([cx + rr * np.cos(ang), np.full(7, yt + 0.0003), cz + sq * rr * np.sin(ang)])])
        Nu = np.tile(up, (8, 1))
        T = facing(P, np.asarray([(0, i + 1, (i + 1) % 7 + 1) for i in range(7)], dtype=np.int64), Nu)
        dark = rng.uniform() < 0.6
        c = ck.mix(IRON, STEEL, 0.3) if dark else PAL["gauze_white"]
        ck.finish(mesh, P, T, "anvil", c, cb, wet=0.0 if dark else 0.7, cavity=0.6 if dark else 0.0, N=Nu)
    count("anvil", mesh, before)
    # the struck star on each flank of the waist: a boss and jagged crack lines, raised, bound light
    before = mesh.triangle_count
    y, zc = STRIKE_AT
    G, NG = waist.grid()
    Q, NQ = G.reshape(-1, 3), NG.reshape(-1, 3)
    for s in (1.0, -1.0):
        i = int(np.argmin((Q[:, 1] - y) ** 2 + (Q[:, 2] - zc) ** 2 + np.where(Q[:, 0] * s > 0, 0.0, 9.0)
                          - 0.5 * np.abs(Q[:, 0])))
        n = NQ[i]
        c = Q[i] + n * 0.004
        Pb, Tb = ck.ellipsoid(c, (0.022, 0.022, 0.022), 3, 6)
        ck.finish(mesh, Pb, oriented(Pb, Tb, c[None]), "strike", PAL["salt_glass"], cb, emission=1.0)
        e1 = unit(np.cross(n, (0.0, 0.0, 1.0)))
        e2 = np.cross(n, e1)
        for k in range(STRIKE_RAYS):
            a = 2.0 * math.pi * k / STRIKE_RAYS + rng.uniform(-0.25, 0.25)
            ln = rng.uniform(0.1, 0.2)
            d = e1 * math.cos(a) + e2 * math.sin(a)
            perp = np.cross(n, d)
            pts = np.array([c + d * ln * f + perp * (0.01 * ((-1) ** j) if 0 < j < 4 else 0.0)
                            for j, f in enumerate(np.linspace(0.15, 1.0, 4))])
            Pr, Tr, Nr = ribbon(pts, np.linspace(0.014, 0.003, len(pts)), perp, n, 0.006)
            ck.finish(mesh, Pr, Tr, "strike", PAL["salt_glass"], cb, emission=1.0, N=Nr)
    count("strike", mesh, before)


# ---------------------------------------------------------------------------------------------
# Mesh: the mane of running sparks
# ---------------------------------------------------------------------------------------------
MANE_CREST = ((0.0, 2.84, 0.97), (0.0, 2.64, 0.74), (0.0, 2.50, 0.42), (0.0, 2.52, 0.02))


def mane(mesh: ck.Mesh, rig: ck.Rig, surfaces: list[Grid]) -> None:
    """A crest of fine filaments of bound light standing along the back of his neck and over the hump: each a thin
    blade kinked twice (a spark's zig-zag), swept back, longest at mid-neck and down the middle, shorter and lower to
    the sides (three layers), brightest at the tips. Each filament is rigid on the bone under its root."""
    rng = np.random.default_rng(SEED + 61)
    Q = np.vstack([g.P for g in surfaces])
    NQ = np.vstack([g.N for g in surfaces])
    crest = ck.bezier(MANE_CREST, 80)
    chain = neck_chain(rig)
    before = mesh.triangle_count
    us = np.sort(rng.uniform(0.0, 1.0, MANE_N))
    for i, u in enumerate(us):
        layer = i % 3  # 0: the long middle, 1 and 2: the shorter flanks
        xo = float(rng.normal(0.0, 0.025)) if layer == 0 else float(rng.choice([-1.0, 1.0]) * rng.uniform(0.04, 0.13))
        k = min(int(u * 79), 78)
        zc, back = crest[k][2], unit(crest[k + 1] - crest[k])
        dist = np.hypot(Q[:, 0] - xo, Q[:, 2] - zc) + np.where(NQ[:, 1] > 0.4, 0.0, 9.0)
        near = np.argsort(dist)[:4]  # the upper surface under (xo, zc): its four nearest vertices, weighted
        wt = 1.0 / (dist[near] + 1e-3)
        wt /= wt.sum()
        n = unit((NQ[near] * wt[:, None]).sum(axis=0))
        root = (Q[near] * wt[:, None]).sum(axis=0) - n * 0.012
        base = 0.36 + 0.4 * math.sin(math.pi * min(u * 1.15, 1.0)) ** 0.8
        L = base * (1.0 - 1.9 * abs(xo)) * float(rng.uniform(0.65, 1.15)) * (1.0 if layer == 0 else 0.8)
        d = unit(n + 0.65 * back + np.array([xo * 3.5, 0.0, 0.0]))
        face = unit(np.array([1.0, 0.0, 0.0]) - d * d[0])  # the blade faces the side (the battle camera)
        side = np.cross(face, d)
        kink = 0.07 * L * float(rng.choice([-1.0, 1.0]))
        if layer == 0:  # the long middle: two kinks
            pts = np.array([root, root + d * L * 0.36 + side * kink, root + d * L * 0.68 - side * kink * 0.8,
                            root + d * L + back * L * 0.08 + side * kink * 0.3])
            w = np.array([0.028, 0.02, 0.011, 0.002]) * float(rng.uniform(0.8, 1.2))
        else:  # the flanks: one
            pts = np.array([root, root + d * L * 0.5 + side * kink, root + d * L + back * L * 0.06 - side * kink * 0.4])
            w = np.array([0.024, 0.013, 0.002]) * float(rng.uniform(0.8, 1.2))
        P, T, N = ribbon(pts, w, side, face, 0.002)
        f = np.tile(np.linspace(0.0, 1.0, len(pts)), 4)
        col = ck.mix(PAL["salt_glass"], PAL["foam_white"], ck.smoothstep(0.4, 1.0, f)[:, None])
        J0, W0 = chain(root[None])
        ck.finish(mesh, P, T, "mane", col, lambda X, J0=J0, W0=W0: (np.tile(J0, (len(X), 1)), np.tile(W0, (len(X), 1))),
                  wet=0.1, emission=0.7 + 0.3 * f, N=N)
    count("mane", mesh, before)


# ---------------------------------------------------------------------------------------------
# Mesh: the limbs
# ---------------------------------------------------------------------------------------------
def on(g: Grid, t: float, a: float) -> np.ndarray:
    """g's surface at fraction t along its path and angle a round it (0 along the frame's normal)."""
    return g.at(t * (g.K - 1), a / (2.0 * math.pi) * g.S)[0]


def fore_limb(mesh: ck.Mesh, rig: ck.Rig, leg: str) -> None:
    """The arm a smith would envy: a heavy shoulder and upper arm, a bony elbow, and a forearm swelling below it
    (extensors and flexors parted by a groove), tendons standing out toward the wrist, keratin scutes down its front."""
    bones, x, _J, _p = LEGS[leg]
    j = leg_joints(leg)
    s = 1.0 if x > 0 else -1.0
    top = j[0] + (-0.07 * s, 0.02, -0.02)
    path = np.vstack([ck.bezier([top, (top + j[1]) * 0.5 + (0, 0, -0.03), j[1]], 12)[:-1],
                      ck.bezier([j[1], (j[1] + j[2]) * 0.5 + (0, 0, 0.035), j[2] + (0.0, 0.05, -0.02)], 13)])
    t = np.linspace(0.0, 1.0, len(path))
    r = np.interp(t, (0.0, 0.06, 0.12, 0.28, 0.44, 0.5, 0.6, 0.7, 0.86, 1.0),
                  (0.14, 0.2, 0.235, 0.215, 0.165, 0.16, 0.225, 0.215, 0.15, 0.13))

    def tendons(tt, a):
        return 1.0 + 0.07 * np.clip(np.cos(5.0 * a + 0.3), 0.0, 1.0) ** 6 * ck.smoothstep(0.74, 0.88, tt) \
            * ck.smoothstep(1.0, 0.93, tt)

    g = Grid(path, r * 1.05, r * 0.95, 16, up_hint=(1.0, 0.0, 0.0), mod=tendons)
    out = 0.0 if s > 0 else math.pi  # the outer side's angle
    front, rear = math.pi / 2, 3 * math.pi / 2
    blobs = [
        (on(g, 0.16, out), (0.12, 0.26, 0.16), 0.06),  # the deltoid, down the arm
        (on(g, 0.1, front), (0.12, 0.2, 0.12), 0.035),
        (on(g, 0.24, front), (0.11, 0.2, 0.1), 0.05),  # biceps
        (on(g, 0.26, rear), (0.12, 0.24, 0.11), 0.075),  # triceps
        (on(g, 0.5, rear), (0.07, 0.08, 0.07), 0.055),  # the elbow's point
        (on(g, 0.63, (out + front) * 0.5), (0.08, 0.2, 0.08), 0.05),  # extensors
        (on(g, 0.63, rear + (0.5 if s > 0 else -0.5)), (0.08, 0.2, 0.08), 0.05),  # flexors
    ]
    grooves = [(on(g, 0.55, front - 0.2 * s), on(g, 0.82, front - 0.2 * s), 0.022, 0.014),
               (on(g, 0.36, out), on(g, 0.46, out + 0.4 * s), 0.03, 0.02)]
    g.sculpt(blobs, grooves, noise=0.01, fine=0.004, seed=SEED + 11 + int(s))
    col, cav = hide(g, SEED + 11, ash=0.3)
    skin = rig.chain(list(bones[:2]), j[:3])
    before = mesh.triangle_count
    add_grid(mesh, g, "body", col, skin, cavity=cav, seam=out + math.pi)
    count("limbs", mesh, before)
    rng = np.random.default_rng(SEED + 13 + int(s))
    before = mesh.triangle_count
    S = g.S
    lo = (out / (2 * math.pi) * S - S * 0.3) % S
    cracks(mesh, g, skin, rng, 5, (2, g.K - 4), (lo, lo + S * 0.6), width=0.01)
    count("cracks", mesh, before)
    before = mesh.triangle_count
    a_pl = front - s * 0.6
    for tt, half in ((0.63, (0.022, 0.085)), (0.74, (0.021, 0.082)), (0.85, (0.02, 0.075))):
        armour_plate(mesh, g, tt * (g.K - 1), a_pl / (2 * math.pi) * S, half, skin, rng)
    count("plates", mesh, before)
    # Polish 2: the wrist cuff. Where the forearm runs into the back of the hand the two surfaces met in a ragged
    # line; a thick roll of hide folds now wraps the wrist below the last scute, its upper edge tucked under the
    # forearm's hide and its lower lip turned down over the hand, so the joint reads as a fold, not a seam.
    before = mesh.triangle_count
    tc = np.array([0.88, 0.91, 0.97, 1.0])
    pc = np.column_stack([np.interp(tc, t, path[:, i]) for i in range(3)])
    rc = np.interp(tc, t, r) * np.array([0.97, 1.07, 1.07, 0.92]) + np.array([0.0, 0.028, 0.024, 0.0])

    def folds(tt, a):  # the hide bunched in four lobes round the wrist, creased between them
        return 1.0 + (0.12 * np.clip(np.cos(4.0 * a + 0.7 * s), 0.0, 1.0) ** 2 - 0.05 * np.cos(9.0 * a + 0.3)) \
            * np.sin(math.pi * np.clip(tt * 1.2, 0.0, 1.0))

    gc = Grid(pc, rc * 1.05, rc * 0.95, 10, up_hint=(1.0, 0.0, 0.0), mod=folds)
    gc.sculpt(noise=0.006, fine=0.003, seed=SEED + 19 + int(s))
    colc, cavc = hide(gc, SEED + 19, ash=0.3)
    lip = np.r_[np.repeat(gc.t, gc.S), 0.0, 1.0]
    cavc = np.clip(cavc + 0.5 * ck.smoothstep(0.75, 1.0, lip) + 0.35 * ck.smoothstep(0.25, 0.0, lip), 0.0, 1.0)
    add_grid(mesh, gc, "body", colc, skin, cavity=cavc, seam=out + math.pi)
    count("cuffs", mesh, before)


def fore_hand(mesh: ck.Mesh, rig: ck.Rig, leg: str) -> None:
    """The fist he walks on: a broad back of the hand, three thick digits curled forward and down with knuckle plates,
    a heavy hooked claw on each resting on the water ahead, and a short thumb on the inside."""
    bones, x, _J, _p = LEGS[leg]
    s = 1.0 if x > 0 else -1.0
    fb = rig.rigid(bones[2])
    rng = np.random.default_rng(SEED + 15 + int(s))
    before = mesh.triangle_count
    path = ck.bezier([(x, 0.4, 0.59), (x, 0.26, 0.645), (x, 0.13, 0.745)], 7)
    t = np.linspace(0.0, 1.0, len(path))
    g = Grid(path, 0.125 + 0.05 * t ** 0.8, 0.11 - 0.02 * t, 12, up_hint=(0.0, 0.0, 1.0), squarish=0.8)
    g.sculpt(noise=0.008, fine=0.003, seed=SEED + 16)
    g.P[:, 1] = np.maximum(g.P[:, 1], 0.0)
    col, cav = hide(g, SEED + 16, ash=0.3)
    add_grid(mesh, g, "body", col, fb, cavity=cav)
    for o in (-0.095, 0.0, 0.095):
        xo = x + o + s * 0.01
        dp = ck.bezier([(xo, 0.165, 0.72), (xo, 0.16, 0.83), (xo, 0.11, 0.895), (xo, 0.058, 0.905)], 7)
        tt = np.linspace(0.0, 1.0, len(dp))
        knuckles = 0.12 * np.exp(-((tt - 0.3) / 0.12) ** 2) + 0.08 * np.exp(-((tt - 0.75) / 0.1) ** 2)
        rd = (0.058 - 0.014 * tt) * (1.0 + knuckles)
        gd = Grid(dp, rd, rd * 0.92, 7)
        gd.sculpt(noise=0.005, seed=SEED + 17)
        gd.P[:, 1] = np.maximum(gd.P[:, 1], 0.0)
        cold, cavd = hide(gd, SEED + 17, ash=0.25)
        add_grid(mesh, gd, "body", cold, fb, cavity=cavd)
        p, n = gd.at(0.32 * (gd.K - 1), 0.0)  # the knuckle plate on top
        plate(mesh, p, n, (0.0, 0.3, 1.0), (0.05, 0.016, 0.045), fb, rng, lift=0.6)
        b = dp[-1] + (0.0, 0.0, 0.018)
        cp = ck.bezier([b, b + (0.0, 0.0, 0.07), b + (0.0, -0.05, 0.1), (xo, 0.004, b[2] + 0.095)], 6)
        ct = np.linspace(0.0, 1.0, 6)
        gc = Grid(cp, 0.022 * (1.0 - ct) + 0.003, 0.032 * (1.0 - ct) + 0.003, 5, up_hint=(1.0, 0.0, 0.0))
        gc.P[:, 1] = np.maximum(gc.P[:, 1], 0.002)
        kk = np.clip((gc.P - b) @ np.array([0.0, -0.5, 0.86]) / 0.08, 0.0, 1.0)
        col = ck.mix(HORN, IVORY, ck.smoothstep(0.1, 0.8, kk)[:, None])
        ck.finish(mesh, gc.P, gc.T, "beak", col, fb, wet=0.25, N=gc.N)
    tp = ck.bezier([(x - s * 0.13, 0.26, 0.64), (x - s * 0.19, 0.17, 0.70), (x - s * 0.2, 0.07, 0.74)], 5)
    gt = Grid(tp, np.linspace(0.05, 0.035, 5), np.linspace(0.045, 0.032, 5), 6)
    gt.P[:, 1] = np.maximum(gt.P[:, 1], 0.0)
    colt, cavt = hide(gt, SEED + 18)
    add_grid(mesh, gt, "body", colt, fb, cavity=cavt)
    count("hands", mesh, before)


def hind_limb(mesh: ck.Mesh, rig: ck.Rig, leg: str) -> None:
    """A heavy haunch and thigh (quadriceps before, hamstrings behind), a lean shank with a calf, and a bird's
    scaled tarsus, scutes down its front."""
    bones, x, _J, _p = LEGS[leg]
    j = leg_joints(leg)
    s = 1.0 if x > 0 else -1.0
    top = j[0] + (0.0, 0.06, -0.02)
    path = np.vstack([ck.bezier([top, (top + j[1]) * 0.5 + (0, 0, 0.04), j[1]], 11)[:-1],
                      ck.bezier([j[1], (j[1] + j[2]) * 0.5 + (0, 0, -0.03), j[2] + (0.0, 0.03, 0.0)], 11)])
    t = np.linspace(0.0, 1.0, len(path))
    r = np.interp(t, (0.0, 0.08, 0.2, 0.42, 0.5, 0.6, 0.78, 1.0), (0.17, 0.28, 0.27, 0.18, 0.15, 0.14, 0.095, 0.08))
    g = Grid(path, r * 1.08, r * 0.95, 12, up_hint=(1.0, 0.0, 0.0))
    front, rear = math.pi / 2, 3 * math.pi / 2
    out = 0.0 if s > 0 else math.pi
    blobs = [(on(g, 0.28, front), (0.12, 0.2, 0.1), 0.05), (on(g, 0.3, rear), (0.12, 0.22, 0.1), 0.05),
             (on(g, 0.15, out), (0.14, 0.16, 0.16), 0.04), (on(g, 0.62, rear), (0.06, 0.12, 0.06), 0.035),
             (on(g, 0.5, front), (0.06, 0.06, 0.06), 0.03)]
    g.sculpt(blobs, [(on(g, 0.75, rear), on(g, 0.97, rear), 0.02, -0.012)], noise=0.009, fine=0.004,
             seed=SEED + 21 + int(s))
    col, cav = hide(g, SEED + 21, ash=0.18)
    skin = rig.chain(list(bones[:2]), j[:3])
    before = mesh.triangle_count
    add_grid(mesh, g, "body", col, skin, cavity=cav, seam=out + math.pi)
    count("limbs", mesh, before)
    rng = np.random.default_rng(SEED + 23 + int(s))
    before = mesh.triangle_count
    lo = (out / (2 * math.pi) * g.S - g.S * 0.25) % g.S
    cracks(mesh, g, skin, rng, 3, (1, 10), (lo, lo + g.S * 0.5), width=0.01)
    count("cracks", mesh, before)
    before = mesh.triangle_count
    for tt in (0.74, 0.83, 0.92):
        p, n = g.at(tt * (g.K - 1), front / (2 * math.pi) * g.S)
        k = int(round(tt * (g.K - 1)))
        plate(mesh, p, n, -(path[min(k + 1, g.K - 1)] - path[max(k - 1, 0)]), (0.06, 0.014, 0.04), skin, rng,
              lift=0.5, curve=2.4)
    count("plates", mesh, before)


def hind_foot(mesh: ck.Mesh, rig: ck.Rig, leg: str) -> None:
    """The hornbill's foot: a heavy pad under the ankle, three scaled toes forward and one back, hooked claws."""
    bones, x, _J, _p = LEGS[leg]
    fb = rig.rigid(bones[2])
    c = np.array([x, 0.075, -0.47])
    before = mesh.triangle_count
    Pf, Tf = ck.ellipsoid(c, (0.11, 0.08, 0.13), 6, 10)
    Pf[:, 1] = np.maximum(Pf[:, 1], 0.0)
    Nf = ck.weld_normals(Pf, ck.vertex_normals(Pf, Tf))
    ck.finish(mesh, Pf, Tf, "body", ck.mix(CHAR, PAL["lacquer_black"], 0.3), fb, wet=0.15, cavity=0.2, N=Nf)
    for ang, ln in ((-28.0, 0.34), (0.0, 0.4), (28.0, 0.34), (180.0, 0.16)):
        d = ck.rot_y(ang) @ np.array([0.0, 0.0, 1.0])
        toe = np.array([c + d * (0.04 + ln * f) + (0.0, -0.02 * f, 0.0) for f in np.linspace(0.0, 1.0, 7)])
        tt = np.linspace(0.0, 1.0, 7)
        rr = (0.052 - 0.024 * tt) * (1.0 + 0.12 * np.abs(np.sin(math.pi * 2.5 * tt)))  # the toe's pads
        toe[:, 1] = np.maximum(toe[:, 1], rr)
        g = Grid(toe, rr, rr * 0.9, 6)
        g.P[:, 1] = np.maximum(g.P[:, 1], 0.0)
        band = 0.5 + 0.5 * np.cos(2.0 * math.pi * 4.5 * ((g.P - c) @ d) / ln)
        col = ck.mix(ck.mix(CHAR, ASH, 0.12), HORN, (0.6 * band)[:, None])
        col = ck.mix(col, PAL["lacquer_black"], (0.5 * np.clip(-g.N[:, 1], 0, 1))[:, None])
        ck.finish(mesh, g.P, g.T, "body", col, fb, wet=0.15, cavity=0.35 * (1.0 - band), N=g.N)
        tip = toe[-1] + d * 0.012
        claw = ck.bezier([tip, tip + d * 0.05, tip + d * 0.085 + (0.0, -0.02, 0.0)], 5)
        claw[:, 1] = np.maximum(claw[:, 1], 0.006)
        gc = Grid(claw, np.linspace(0.02, 0.003, 5), np.linspace(0.024, 0.004, 5), 5)
        gc.P[:, 1] = np.maximum(gc.P[:, 1], 0.002)
        ck.finish(mesh, gc.P, gc.T, "beak", ck.mix(HORN, IVORY, 0.6), fb, wet=0.25, N=gc.N)
    count("feet", mesh, before)


def tail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Five long hornbill tail feathers from the rump, hanging down behind him (so they stay inside the frame's
    right edge at the default camera), fanned, each with a raised shaft, a fringed vane, ash barring and a pale band
    near the tip."""
    chain = rig.chain(["tail_0", "tail_1"], TAIL_PTS)
    before = mesh.triangle_count
    for sx, ln, roll in TAIL_FEATHERS:
        a = TAIL_PTS[0] + (sx * 0.3, 0.0, 0.04)
        pts = ck.bezier([a, a + (sx * 0.5, -0.1, -0.1), a + (sx * 0.8, -0.32 * ln / 0.6, -0.16),
                         a + (sx * 0.9, -ln, -0.14)], 12)
        K = len(pts)
        f = np.linspace(0.0, 1.0, K)
        w = 0.12 * np.sin(math.pi * np.clip(0.15 + f * 0.9, 0.0, 1.0)) ** 0.5 + 0.01
        w = w * (1.0 - 0.12 * (np.arange(K) % 2) * ck.smoothstep(0.3, 0.5, f))  # fringed: barbs parting
        tan = np.gradient(pts, axis=0)
        tan /= np.linalg.norm(tan, axis=1, keepdims=True)
        m = K // 2
        side = unit(np.cross(tan[m], (0.0, 1.0, 0.0)))
        r = math.radians(roll)  # turned about the feather's own length, so the fan shows from the side
        side = side * math.cos(r) + np.cross(tan[m], side) * math.sin(r)
        normal = unit(np.cross(side, tan[m]))
        L = pts - side * w[:, None] * 0.5
        R = pts + side * w[:, None] * 0.5
        rach = 0.012 * (1.0 - f)[:, None] + 0.003
        P = np.vstack([L, pts + normal * rach, R, L, pts - normal * rach * 0.6, R])
        T = []
        for face, sgn in ((0, 1.0), (3, -1.0)):
            for k in range(K - 1):
                for c0 in (0, 1):
                    a0, a1 = (face + c0) * K + k, (face + c0 + 1) * K + k
                    T += [(a0, a1, a0 + 1), (a0 + 1, a1, a1 + 1)]
        N = np.vstack([np.tile(normal, (3 * K, 1)), np.tile(-normal, (3 * K, 1))])
        T = facing(P, np.asarray(T, dtype=np.int64), N)
        ff = np.tile(f, 6)
        mid = np.tile(np.r_[np.zeros(K), np.ones(K), np.zeros(K)], 2)
        bars = 0.5 + 0.5 * np.cos(2.0 * math.pi * 6.0 * ff + sx * 9.0)
        col = ck.mix(CHAR, ck.mix(CHAR, ASH, 0.45), (0.5 * bars * ck.smoothstep(0.1, 0.6, ff))[:, None])
        col = ck.mix(col, ck.mix(CHAR, ASH, 0.5), (0.6 * np.exp(-((ff - 0.8) / 0.06) ** 2))[:, None])
        col = ck.mix(col, ck.mix(CHAR, ASH, 0.3), (0.5 * mid)[:, None])
        ck.finish(mesh, P, T, "body", col, chain, wet=0.1, cavity=0.2 * (1.0 - mid), N=N)
    count("tail", mesh, before)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    PARTS.clear()
    mesh = ck.Mesh("kahre")
    gt = torso(mesh, rig)
    gn = neck(mesh, rig)
    head(mesh, rig)
    hammer(mesh, rig)
    anvil(mesh, rig)
    mane(mesh, rig, [gt, gn])
    for leg in LEGS:
        if leg.startswith("fore"):
            fore_limb(mesh, rig, leg)
            fore_hand(mesh, rig, leg)
        else:
            hind_limb(mesh, rig, leg)
            hind_foot(mesh, rig, leg)
    tail(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Legs: every planted foot solved onto its target at every frame
# ---------------------------------------------------------------------------------------------
def _ang(v) -> float:
    """The angle of (z, y) in the leg's plane, degrees: rx = +a turns it by -a (creature_kit's euler)."""
    return math.degrees(math.atan2(v[1], v[0]))


def _euler_of(R: np.ndarray) -> tuple[float, float, float]:
    """(rx, ry, rz) degrees with R = rot_z(rz) @ rot_y(ry) @ rot_x(rx) (creature_kit.euler)."""
    ry = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    rx = math.atan2(R[2, 1], R[2, 2])
    rz = math.atan2(R[1, 0], R[0, 0])
    return math.degrees(rx), math.degrees(ry), math.degrees(rz)


def _solve2(hip, knee, ankle, target) -> tuple[float, float]:
    """The (upper, lower) rx that put `ankle` on `target`, all (z, y) in the parent's rest frame; the joint bends
    the way it does at rest. Out of reach, the leg points at the target, as straight as it goes."""
    a = float(np.linalg.norm(knee - hip))
    b = float(np.linalg.norm(ankle - knee))
    D = target - hip
    d = float(np.clip(np.linalg.norm(D), abs(a - b) + 1e-4, a + b - 1e-4))
    beta = math.atan2(D[1], D[0])
    alpha = math.acos(max(-1.0, min(1.0, (a * a + d * d - b * b) / (2.0 * a * d))))
    bend = np.sign((knee - hip)[0] * (ankle - knee)[1] - (knee - hip)[1] * (ankle - knee)[0])
    best = None
    for sgn in (1.0, -1.0):
        tu = beta + sgn * alpha
        kd = hip + a * np.array([math.cos(tu), math.sin(tu)])
        lower = hip + D / max(float(np.linalg.norm(D)), 1e-9) * d - kd
        tl = math.atan2(lower[1], lower[0])
        cr = math.cos(tu) * math.sin(tl) - math.sin(tu) * math.cos(tl)
        if best is None or np.sign(cr) == bend:
            best = (tu, tl)
            if np.sign(cr) == bend:
                break
    tu, tl = best
    ru = _ang(knee - hip) - math.degrees(tu)
    rl = _ang(ankle - knee) - ru - math.degrees(tl)
    return ru, rl


SCRATCH = ("tgt_", "free_")  # authoring tracks: a foot's target offset (loc) and how free it is (loc x: 0 planted)


def solve_legs(rig: ck.Rig, clip: ck.Clip, poser: grounding.Poser) -> ck.Clip:
    """`clip` with each leg keyed at every baked frame: the authored leg keys (its free pose) blended with the solve
    that puts the wrist or ankle on its target (the rest joint plus the `tgt_<leg>` offset) with the foot level, by
    1 - `free_<leg>`. The scratch tracks are dropped."""
    leg_bones = {b for bones, *_ in LEGS.values() for b in bones}
    out = ck.Clip(clip.name, clip.length, loop=clip.loop)
    for b, ks in clip.keys.items():
        if b not in leg_bones and not b.startswith(SCRATCH):
            out.keys[b] = list(ks)
    for t in grounding.frame_times(clip):
        pose = grounding.pose_at(clip, poser.names, t)
        mats = poser.matrices(pose)
        for leg, (bones, _x, _J, parent) in LEGS.items():
            j = leg_joints(leg)
            free = float(np.clip(clip.sample(f"free_{leg}", t)[1][0], 0.0, 1.0))
            tgt_rot, tgt_off = clip.sample(f"tgt_{leg}", t)
            Mp = mats[rig.index(parent)]
            target = j[2] + np.asarray(tgt_off)
            local = np.linalg.solve(Mp, np.append(target, 1.0))[:3]
            ru, rl = _solve2(j[0, 1:][::-1], j[1, 1:][::-1], j[2, 1:][::-1], local[1:][::-1])
            Rw = Mp[:3, :3] @ ck.euler(ru, 0.0, 0.0) @ ck.euler(rl, 0.0, 0.0)
            rf = _euler_of(Rw.T @ ck.euler(float(tgt_rot[0]), 0.0, 0.0))
            fk = [np.asarray(pose[b][0], dtype=np.float64) for b in bones]
            ik = [np.array([ru, 0.0, 0.0]), np.array([rl, 0.0, 0.0]), np.array(rf)]
            for b, f, s in zip(bones, fk, ik):
                rot = ck.mix(s, f, free)
                out.key(b, t, tuple(float(v) for v in rot), pose[b][1])
    return out


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
KO_SEC = 2.0
VICTORY_SEC = 2.2
RISE_SEC = 2.6
DISMISS_SEC = 1.0
SPECIAL_SEC = 2.8
SPECIAL_CONTACT = 1.55
IDLE_B_SEC = 1.2
RELEASE_SEC = 3.4  # M3-CRE-647: the held form's release (Ch20), its KO
RELEASE_AWAY = (0.0, 1.5, -0.5)  # where the release carries him (metres: up, and back away from the party)


def pose(c: ck.Clip, t: float, body=(0.0, 0.0, 0.0), lift: float = 0.0, slide: float = 0.0, chest: float = 0.0,
         neck=(0.0, 0.0, 0.0), head: float = 0.0, jaw: float = 0.0, tail: float = 0.0, roll: float = 0.0,
         turn: float = 0.0) -> None:
    """One key of the upper body. body (rx, ry, rz) about the hips (+rx: nose down), lift/slide the hips (m, up and
    forward), chest (rx), neck (rx per bone), head (rx), jaw (+ opens), tail (+ lifts), roll/turn spread over the
    neck (rz, ry)."""
    c.key("body", t, body, (0.0, lift, slide))
    c.key("chest", t, (chest, 0.0, roll * 0.4))
    for k in range(3):
        c.key(f"neck_{k}", t, (neck[k], turn / 3.0, roll / 3.0))
    c.key("head", t, (head, 0.0, 0.0))
    c.key("jaw", t, (jaw, 0.0, 0.0))
    c.key("tail_0", t, (-tail, 0.0, 0.0))
    c.key("tail_1", t, (-tail * 0.6, 0.0, 0.0))


def foot(c: ck.Clip, leg: str, t: float, dy: float = 0.0, dz: float = 0.0, pitch: float = 0.0, free: float = 0.0,
         fk=None) -> None:
    """A foot's target offset from its rest wrist or ankle (dy up, dz forward), its pitch (+: toes down) and how free
    it is (1: the leg plays `fk`, (upper, lower, foot) rx, instead of the solve)."""
    c.key(f"tgt_{leg}", t, (pitch, 0.0, 0.0), (0.0, dy, dz))
    c.key(f"free_{leg}", t, (0.0, 0.0, 0.0), (free, 0.0, 0.0))
    if fk is not None or free > 0.0:
        u, lo, f = fk if fk is not None else (0.0, 0.0, 0.0)
        bones = LEGS[leg][0]
        c.key(bones[0], t, (u, 0.0, 0.0))
        c.key(bones[1], t, (lo, 0.0, 0.0))
        c.key(bones[2], t, (f, 0.0, 0.0))


def planted(c: ck.Clip, *times: float) -> None:
    for leg in LEGS:
        for t in times:
            foot(c, leg, t)


def build_idle() -> ck.Clip:
    c = ck.Clip("idle", IDLE_SEC, loop=True)  # heavy breathing, the head swinging a little, the weight shifting
    c.wave("body", amp_rot=(1.2, 0.0, 0.8), amp_loc=(0.0, 0.025, 0.0), cycles=1, phase=0.0)
    c.wave("chest", amp_rot=(-2.0, 0.0, 0.0), cycles=2, phase=0.5)
    for k in range(3):
        c.wave(f"neck_{k}", amp_rot=(2.0, 2.5, 0.0), cycles=1, phase=-0.6 * k - 0.8)
    c.wave("head", amp_rot=(-2.5, 3.0, 0.0), cycles=1, phase=-2.4)
    c.wave("jaw", amp_rot=(1.5, 0.0, 0.0), base_rot=(1.5, 0.0, 0.0), cycles=2, phase=1.0)
    c.wave("tail_0", amp_rot=(2.0, 4.0, 0.0), cycles=1, phase=-0.5)
    c.wave("tail_1", amp_rot=(3.0, 6.0, 0.0), cycles=1, phase=-1.1)
    planted(c, 0.0, IDLE_SEC)
    return c


def build_ready() -> ck.Clip:
    c = ck.Clip("ready", READY_SEC)  # he squares up: head up, one stamp of the left fist, the bill clacks
    for t, kw in ((0.0, {}), (0.4, dict(body=(-4.0, 0.0, -2.0), lift=0.05, neck=(-6.0, -4.0, -2.0), head=-6.0,
                                       jaw=10.0)),
                  (0.62, dict(body=(-2.0, 0.0, -1.0), lift=0.03, neck=(-4.0, -3.0, -1.0), head=-4.0, jaw=12.0)),
                  (0.72, dict(body=(3.0, 0.0, 1.0), lift=-0.04, neck=(4.0, 3.0, 2.0), head=6.0, jaw=0.0)),
                  (1.0, dict(body=(1.0, 0.0, 0.0), neck=(1.0, 1.0, 0.0), head=2.0)), (READY_SEC, {})):
        pose(c, t, **kw)
    planted(c, 0.0, READY_SEC)
    for leg in ("fore_r", "hind_l", "hind_r"):
        foot(c, leg, 0.6)
    for t, dy, dz in ((0.2, 0.0, 0.0), (0.45, 0.28, 0.08), (0.7, 0.0, 0.1), (READY_SEC, 0.0, 0.1)):
        foot(c, "fore_l", t, dy, dz)
    return c


def build_attack() -> ck.Clip:
    c = ck.Clip("attack", ATTACK_SEC)  # the casque strike: draw back and up, then the head drives forward and down
    for t, kw in ((0.0, {}),
                  (0.3, dict(body=(-6.0, 0.0, 0.0), lift=0.04, slide=-0.08, chest=-4.0, neck=(-14.0, -18.0, -16.0),
                             head=-20.0, jaw=6.0, tail=6.0)),
                  (0.4, dict(body=(-5.0, 0.0, 0.0), lift=0.04, slide=-0.08, chest=-4.0, neck=(-15.0, -20.0, -18.0),
                             head=-24.0, jaw=4.0, tail=6.0)),
                  (ATTACK_CONTACT, dict(body=(8.0, 0.0, 0.0), lift=-0.06, slide=0.16, chest=6.0,
                                        neck=(16.0, 18.0, 14.0), head=38.0, tail=-4.0)),
                  (0.75, dict(body=(6.0, 0.0, 0.0), lift=-0.05, slide=0.12, chest=4.0, neck=(12.0, 12.0, 10.0),
                              head=26.0, tail=-3.0)),
                  (ATTACK_SEC, {})):
        pose(c, t, **kw)
    planted(c, 0.0, ATTACK_SEC)
    return c


def build_cast() -> ck.Clip:
    c = ck.Clip("cast", CAST_SEC)  # Forge Bolt: the head to the sky, bill open, then thrust at the foes
    for t, kw in ((0.0, {}),
                  (0.45, dict(body=(-8.0, 0.0, 0.0), lift=0.06, chest=-6.0, neck=(-12.0, -18.0, -22.0), head=-40.0,
                              jaw=22.0, tail=8.0)),
                  (0.6, dict(body=(-8.0, 0.0, 0.0), lift=0.06, chest=-6.0, neck=(-12.0, -18.0, -22.0), head=-42.0,
                             jaw=24.0, tail=8.0)),
                  (CAST_CONTACT, dict(body=(5.0, 0.0, 0.0), lift=-0.03, slide=0.08, chest=4.0, neck=(10.0, 8.0, 4.0),
                                      head=8.0, jaw=26.0, tail=-2.0)),
                  (1.1, dict(body=(4.0, 0.0, 0.0), lift=-0.02, slide=0.06, chest=3.0, neck=(8.0, 6.0, 3.0), head=6.0,
                             jaw=10.0)),
                  (CAST_SEC, {})):
        pose(c, t, **kw)
    planted(c, 0.0, CAST_SEC)
    return c


def build_hit(name: str = "hit", side: float = 1.0, amp: float = 1.0) -> ck.Clip:
    """Rocked back on his haunches, the head snapped up and back, the bill opening; rolled a little to `side`.
    hit_b is authored (the other side, heavier): the kit's scaled copy would push the solved feet through the water."""
    c = ck.Clip(name, HIT_SEC)
    for t, s in ((0.0, 0.0), (HIT_PEAK, amp), (0.26, -0.2 * amp), (HIT_SEC, 0.0)):
        pose(c, t, body=(-7.0 * s, 0.0, 3.0 * s * side), lift=0.02 * s, slide=-0.06 * s, chest=-4.0 * s,
             neck=(-6.0 * s, -8.0 * s, -10.0 * s), head=-14.0 * s, jaw=14.0 * max(s, 0.0), tail=8.0 * s,
             roll=4.0 * s * side)
    planted(c, 0.0, HIT_SEC)
    return c


def build_defend() -> ck.Clip:
    c = ck.Clip("defend", DEFEND_SEC)  # he braces: low, the head pulled in over the anvil, casque forward
    held = dict(body=(5.0, 0.0, 0.0), lift=-0.12, chest=4.0, neck=(14.0, 4.0, -12.0), head=34.0, tail=-4.0)
    for t, kw in ((0.0, {}), (0.3, held), (0.85, held), (DEFEND_SEC, {})):
        pose(c, t, **kw)
    planted(c, 0.0, DEFEND_SEC)
    return c


KO_DOWN = dict(body=(3.0, 0.0, 6.0), lift=-0.8, slide=0.0, chest=4.0, neck=(30.0, 26.0, 8.0), head=24.0, tail=4.0,
               roll=4.0)
KO_LEGS = {  # the folded legs at rest on the water: (dy, dz, pitch)
    "fore_l": (0.06, 0.12, 0.0), "fore_r": (0.06, 0.12, 0.0), "hind_l": (0.0, -0.1, 0.0), "hind_r": (0.0, -0.1, 0.0),
}


def build_ko() -> ck.Clip:
    c = ck.Clip("ko", KO_SEC)  # setting the tools down: the legs fold, he lies down, the hammer laid on the water
    for t, kw in ((0.0, {}),
                  (0.25, dict(body=(-5.0, 0.0, 0.0), lift=0.02, neck=(-4.0, -6.0, -6.0), head=-10.0, jaw=8.0)),
                  (0.9, dict(body=(2.0, 0.0, 3.0), lift=-0.4, chest=2.0, neck=(8.0, 8.0, 4.0), head=6.0, roll=2.0)),
                  (1.6, KO_DOWN), (KO_SEC, KO_DOWN)):
        pose(c, t, **kw)
    planted(c, 0.0, 0.25)
    for leg, (dy, dz, pitch) in KO_LEGS.items():
        foot(c, leg, 1.2, dy * 0.5, dz * 0.5, pitch * 0.5)
        foot(c, leg, 1.6, dy, dz, pitch)
        foot(c, leg, KO_SEC, dy, dz, pitch)
    return c


def build_victory() -> ck.Clip:
    c = ck.Clip("victory", VICTORY_SEC)  # a short rear, both fists down together, the head high, the bill clacking
    for t, kw in ((0.0, {}),
                  (0.6, dict(body=(-14.0, 0.0, 0.0), lift=0.06, chest=-6.0, neck=(-8.0, -10.0, -10.0), head=-20.0,
                             jaw=14.0, tail=10.0)),
                  (1.0, dict(body=(4.0, 0.0, 0.0), lift=-0.06, chest=4.0, neck=(2.0, -2.0, -6.0), head=-10.0, jaw=0.0)),
                  (1.3, dict(body=(0.0, 0.0, 0.0), neck=(-4.0, -6.0, -8.0), head=-18.0, jaw=16.0)),
                  (1.5, dict(neck=(-4.0, -6.0, -8.0), head=-18.0, jaw=0.0)),
                  (1.7, dict(neck=(-4.0, -6.0, -8.0), head=-16.0, jaw=14.0)),
                  (VICTORY_SEC, {})):
        pose(c, t, **kw)
    planted(c, 0.0, VICTORY_SEC)
    for leg in ("fore_l", "fore_r"):
        for t, dy, dz in ((0.2, 0.0, 0.0), (0.6, 0.3, 0.06), (0.95, 0.0, 0.05), (VICTORY_SEC, 0.0, 0.05)):
            foot(c, leg, t, dy, dz)
    return c


RISE_START = dict(body=(10.0, 0.0, 0.0), lift=-0.38, chest=6.0, neck=(18.0, 16.0, 8.0), head=20.0, tail=-8.0)


def build_rise() -> ck.Clip:
    c = ck.Clip("rise", RISE_SEC)  # stepping up out of the water as the stage lifts him: left fist, right fist, up
    for t, kw in ((0.0, RISE_START), (0.5, RISE_START),
                  (1.0, dict(body=(4.0, 0.0, -3.0), lift=-0.22, chest=3.0, neck=(10.0, 8.0, 4.0), head=10.0,
                             roll=-3.0)),
                  (1.5, dict(body=(0.0, 0.0, 3.0), lift=-0.08, neck=(2.0, 0.0, -2.0), head=0.0, roll=3.0)),
                  (2.0, dict(body=(-3.0, 0.0, 0.0), lift=0.03, neck=(-4.0, -4.0, -4.0), head=-8.0, jaw=8.0)),
                  (RISE_SEC, {})):
        pose(c, t, **kw)
    for leg in LEGS:
        foot(c, leg, 0.0, 0.0, -0.12 if leg.startswith("fore") else 0.0)
        foot(c, leg, RISE_SEC)
    foot(c, "fore_l", 0.5, 0.0, -0.12)
    foot(c, "fore_l", 0.8, 0.3, 0.05)
    foot(c, "fore_l", 1.05, 0.0, 0.0)
    foot(c, "fore_r", 1.0, 0.0, -0.12)
    foot(c, "fore_r", 1.3, 0.3, 0.05)
    foot(c, "fore_r", 1.55, 0.0, 0.0)
    return c


DISMISS_END = dict(body=(8.0, 0.0, 0.0), lift=-0.18, chest=6.0, neck=(22.0, 20.0, 12.0), head=26.0, tail=-8.0)


def build_dismiss() -> ck.Clip:
    c = ck.Clip("dismiss", DISMISS_SEC)  # he bows his head and sets the hammer down; it ends bowed
    for t, kw in ((0.0, {}), (0.3, dict(body=(-2.0, 0.0, 0.0), neck=(-3.0, -3.0, -3.0), head=-6.0)),
                  (0.8, DISMISS_END), (DISMISS_SEC, DISMISS_END)):
        pose(c, t, **kw)
    planted(c, 0.0, DISMISS_SEC)
    return c


REAR = dict(body=(-18.0, 0.0, 0.0), lift=0.04, chest=-6.0, neck=(-8.0, -12.0, -14.0), head=-30.0, jaw=10.0,
            tail=10.0)
ARMS_UP = (-40.0, -70.0, 30.0)  # the forearms drawn up under him as he rears: (upper, lower, foot) rx
# M3-CRB-008 polish: the hammer now lies along the casque, so the blow comes down 6.5 cm less to land its face
# on the water (not through it)
BLOW = dict(body=(20.0, 0.0, 0.0), lift=-0.245, slide=0.12, chest=10.0, neck=(35.0, 30.0, 15.0), head=20.0, tail=-8.0)


def build_special() -> ck.Clip:
    """Last Strike: he rears with the hammer high over his back, holds, then the whole body comes down into one
    overhead blow, the forearms planting and the hammer's face landing on the water in front of him."""
    c = ck.Clip("special", SPECIAL_SEC)
    for t, kw in ((0.0, {}), (0.9, REAR), (1.25, dict(REAR, head=-34.0, neck=(-9.0, -14.0, -16.0))),
                  (SPECIAL_CONTACT, BLOW), (1.95, dict(BLOW, head=17.0, lift=-0.215)), (SPECIAL_SEC, {})):
        pose(c, t, **kw)
    for leg in ("hind_l", "hind_r"):
        for t in (0.0, SPECIAL_SEC):
            foot(c, leg, t)
    for leg in ("fore_l", "fore_r"):
        foot(c, leg, 0.0)
        foot(c, leg, 0.3, 0.0, 0.0, 0.0, 0.0)
        foot(c, leg, 0.75, 0.0, 0.0, 0.0, 1.0, ARMS_UP)
        foot(c, leg, 1.25, 0.0, 0.0, 0.0, 1.0, ARMS_UP)
        foot(c, leg, 1.45, 0.14, 0.16, 0.0, 0.0, (0.0, 0.0, 0.0))
        foot(c, leg, SPECIAL_CONTACT, 0.0, 0.18)
        foot(c, leg, 1.95, 0.0, 0.18)
        foot(c, leg, SPECIAL_SEC, 0.0, 0.0)
    return c


def build_idle_b() -> ck.Clip:
    c = ck.Clip("idle_b", IDLE_B_SEC)  # the fidget: a shake of the head and the mane, one clack of the bill
    for t, kw in ((0.0, {}), (0.25, dict(neck=(-2.0, -2.0, -3.0), head=-4.0, turn=10.0, roll=5.0, jaw=6.0)),
                  (0.45, dict(neck=(-2.0, -2.0, -3.0), head=-4.0, turn=-10.0, roll=-5.0, jaw=0.0)),
                  (0.65, dict(neck=(-1.0, -1.0, -2.0), head=-3.0, turn=6.0, roll=3.0, jaw=9.0)),
                  (0.8, dict(head=-2.0, jaw=0.0)), (IDLE_B_SEC, {})):
        pose(c, t, **kw)
    planted(c, 0.0, IDLE_B_SEC)
    return c


RELEASE_TALL = dict(body=(-14.0, 0.0, 0.0), lift=0.1, chest=-6.0, neck=(-8.0, -10.0, -12.0), head=-24.0, jaw=4.0,
                    tail=10.0)
RELEASE_EASED = dict(body=(-6.0, 0.0, 0.0), lift=0.04, chest=-2.0, neck=(0.0, 0.0, -2.0), head=-4.0, tail=2.0)


def build_release() -> ck.Clip:
    """M3-CRE-647, the held form's KO (vowbound.md, the final fight: "It's like setting the tools down"). He draws
    himself up to his full height, the casque and its hammer raised to the sky, and holds there; then the weight goes
    out of him, the head settles, and he lifts off the water, up and back, the legs hanging easy: relieved, not felled.
    The feet stay solved: planted until the lift, then carried with him."""
    c = ck.Clip("release", RELEASE_SEC)
    for t, kw in ((0.0, {}), (0.6, dict(RELEASE_TALL, body=(-11.0, 0.0, 0.0), lift=0.07, head=-16.0, jaw=8.0)),
                  (1.2, RELEASE_TALL), (1.8, dict(RELEASE_TALL, head=-22.0)), (2.5, dict(RELEASE_EASED, jaw=2.0)),
                  (RELEASE_SEC, RELEASE_EASED)):
        pose(c, t, **kw)
    lx, ly, lz = RELEASE_AWAY
    for t, k in ((0.0, 0.0), (1.8, 0.0), (2.6, 0.45), (RELEASE_SEC, 1.0)):
        c.key("root", t, (0.0, 0.0, 0.0), (lx * k, ly * k, lz * k))
        hang = 0.1 * min(k / 0.45, 1.0)  # the feet come up off the water a little as he goes: hanging, not standing
        for leg in LEGS:
            foot(c, leg, t, ly * k + hang, lz * k + (0.06 if leg.startswith("fore") else -0.04) * hang / 0.1,
                 12.0 * hang / 0.1)
    return c


def authored_clips() -> list[ck.Clip]:
    return [build_idle(), build_ready(), build_attack(), build_cast(), build_hit(), build_hit("hit_b", -1.0, 1.35),
            build_defend(), build_ko(), build_victory(), build_rise(), build_dismiss(), build_special(),
            build_idle_b(), build_release()]


def build_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    poser = grounding.Poser(rig, mesh)
    return [solve_legs(rig, c, poser) for c in authored_clips()]


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
    mesh = build_mesh(rig)
    return rig, mesh, build_clips(rig, mesh)


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
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "kahre"})
    print(f"kahre: {info}")


if __name__ == "__main__":
    main()
