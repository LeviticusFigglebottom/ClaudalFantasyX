"""Hesk, the Cord-Keeper, Asha's Holy Vowbound (M3-CRE-643): docs/kb/art/creatures/vowbound/hesk.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/hesk/build_hesk.py -- --out assets/creatures/hesk/hesk.glb

A great condor perched on the water, wings half-folded and mantled: the wrists held high over her shoulders, the
inner wing a slate cape, and from each hand eight primaries that are **knotted cords** (twisted gauze_white rope with
one sand_cloth strand), built as geometry. The knots along each cord are keth: clusters spaced like digits, read
from the hand outward (see KETH below), so her outermost cords read 47 and 7. The knots carry the bound light
(emission mask 1.0); the cord between them is faint (0.2). A ruff of short soft cords rings her neck; the head is
bare bone with a small dark hooked beak. Her left talon is drawn up and clutches a keth bundle (the keepsake, an
object: never lit), whose cords hang to 0.1 m over the water.

**Grounded.** The origin is the water point under her. Her right talon is planted and solved onto the water at every
baked frame (`solve_legs`, Kahre's two-bone solve, M3-CRE-640); the body sways, bows and settles over it. The cords,
the bundle and the folded left leg are kept off the water by grounding.grounded where a clip lays them on it.

Rig (25 bones): `root`, `body`, `neck_0..2`, `head`, `wing_l0..2` (humerus, forearm, hand) and the right wing,
`cord_l0`, `cord_l1` (the soft chain every cord of that wing sways on) and the right, `leg_l0`, `leg_l1`, `talon_l`
and the right leg (+x is `l`), `bundle_0`, `bundle_1`, `tail`.

`python3 build_hesk.py --report` prints the triangle count, per-part counts and per-clip lows (numpy, no export).
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

SEED = 6430
PAL = {k: ck.hexrgb(v) for k, v in {
    "overcast_slate": "#6F7E8E", "storm_slate": "#3E4A57", "lacquer_black": "#1D1916", "gauze_white": "#EBE7DF",
    "sand_cloth": "#C9B48E", "faded_teal_cloth": "#5E9A96", "bone": "#E6DAC0", "deep_teal_shadow": "#0E4A55",
}.items()}
SLATE = PAL["overcast_slate"]
DARK = PAL["storm_slate"]
UNDER = ck.mix(PAL["storm_slate"], PAL["lacquer_black"], 0.35)
BEAK = ck.mix(PAL["storm_slate"], PAL["lacquer_black"], 0.6)
CORD_GLOW = 0.2  # the faint light along a cord (emission mask)
KNOT_GLOW = 1.0  # the knots are what shines
RUFF_GLOW = 0.2
EYE_GLOW = 0.55

# ---- the skeleton's rest joints (metres, Godot axes, facing +z; the water at y 0) ----------------
BODY_PIVOT = np.array([0.0, 0.95, -0.12])  # the body bone's head: she bows and sways about it
SPINE = ((0.0, 0.62, -0.52), (0.0, 0.96, -0.38), (0.0, 1.48, -0.02), (0.0, 1.78, 0.18))
NECK_PATH = ((0.0, 1.74, 0.18), (0.0, 1.90, 0.26), (0.0, 2.00, 0.34), (0.0, 2.06, 0.42))
HEAD_TIP = np.array([0.0, 2.04, 0.66])
TAIL_PTS = np.array([(0.0, 0.70, -0.50), (0.0, 0.40, -0.64)])
# the left wing, mantled (the right mirrors it): shoulder, elbow, wrist, the hand's tip
WING = np.array([(0.28, 1.56, 0.02), (0.62, 1.88, -0.16), (0.82, 2.33, 0.0), (0.90, 2.07, 0.04)])
CORD_CHAIN = np.array([(0.88, 2.16, 0.03), (0.95, 1.62, 0.0), (1.02, 1.06, -0.02)])  # cord_l0 head, joint, tail
# legs: (y, z) in each leg's plane: the hip, the heel, the ankle, the toes
LEG_R = np.array([(0.80, -0.10), (0.42, -0.22), (0.10, -0.04), (0.03, 0.18)])
LEG_X = 0.17
LEG_L = np.array([(0.17, 0.80, -0.10), (0.21, 0.56, -0.16), (0.21, 0.44, 0.15), (0.21, 0.40, 0.25)])  # drawn up
BUNDLE = np.array([(0.21, 0.38, 0.25), (0.21, 0.24, 0.25), (0.21, 0.10, 0.25)])

# ---- the body: control rings along the spine (t, half width, half depth) -------------------------
BODY_RINGS = ((0.0, 0.05, 0.05), (0.07, 0.24, 0.2), (0.25, 0.38, 0.34), (0.5, 0.40, 0.36), (0.75, 0.33, 0.29),
              (0.92, 0.21, 0.18), (1.0, 0.13, 0.12))
SKULL_C, SKULL_R = np.array([0.0, 2.09, 0.46]), (0.075, 0.08, 0.11)
EYE_AT = (0.062, 2.115, 0.50)

# ---- the cords --------------------------------------------------------------------------------
N_CORDS = 8
CORD_LEN = (1.05, 1.18, 1.28, 1.30, 1.26, 1.18, 1.08, 1.0)  # leading to trailing (sheet: 1.0-1.3 m)
CORD_FAN = (34.0, 26.0, 18.0, 10.0, 2.0, -7.0, -16.0, -24.0)  # degrees from straight down, + forward
CORD_OUT = 12.0  # degrees the fan leans out from the body
CORD_R = 0.018
CORD_STEP = 0.05  # ring spacing along a cord
CORD_SEGS = 5
STRAND_PITCH = 0.18  # metres per turn of the sand_cloth strand
# keth (the build's own convention, docs/kb/art/creatures/vowbound/hesk.md "The knots"): a number per cord, its digits
# as clusters read from the hand outward, the highest place first. In every place but the units a digit d is d single
# knots (beads); the units digit is one long knot of d turns (2-9), a figure-eight for 1, and a bare gap for 0. The
# two outermost cords of each wing read 47 (the Cantors) and 7 (the houses); the others are her ledger, seeded.
KETH_FIXED = (47, 7)
KETH_START = 0.26  # metres from the hand to the first cluster
KNOT_STEP = 0.045  # bead to bead in a cluster
PLACE_GAP = 0.2  # the gap between two places
TURN_PITCH = 0.021  # a long knot's turn

PARTS: dict[str, int] = {}


def count(name: str, mesh: ck.Mesh, before: int) -> None:
    PARTS[name] = PARTS.get(name, 0) + mesh.triangle_count - before


def unit(v) -> np.ndarray:
    v = np.asarray(v, dtype=np.float64)
    return v / max(float(np.linalg.norm(v)), 1e-12)


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


def loft(path, half_w, half_h, segs: int, up_hint=(0.0, 1.0, 0.0), twist=None, squash: float = 1.0):
    """A closed tube along `path` (K, 3), elliptical section (`half_w` along the frame's side, `half_h` along its up;
    scalars or (K,)), both ends capped to a point. `twist` (K,) turns the section (radians) along the path."""
    path = np.asarray(path, dtype=np.float64)
    K = len(path)
    hw = np.broadcast_to(np.asarray(half_w, dtype=np.float64), (K,))
    hh = np.broadcast_to(np.asarray(half_h, dtype=np.float64), (K,)) * squash
    tw = np.zeros(K) if twist is None else np.asarray(twist, dtype=np.float64)
    tan, nrm, bin_ = ck.frames_along(path, up_hint)
    a = np.arange(segs) * (2.0 * math.pi / segs)
    rings = []
    for k in range(K):
        ca, sa = np.cos(a + tw[k]), np.sin(a + tw[k])
        rings.append(path[k] + hh[k] * np.outer(ca, nrm[k]) + hw[k] * np.outer(sa, bin_[k]))
    P = np.vstack(rings + [path[:1] - tan[:1] * 0.002, path[-1:] + tan[-1:] * 0.002])
    T = ck.grid_tris(K, segs, True)
    s0, s1 = len(P) - 2, len(P) - 1
    caps = [(k, (k + 1) % segs, s0) for k in range(segs)]
    caps += [((K - 1) * segs + k, (K - 1) * segs + (k + 1) % segs, s1) for k in range(segs)]
    T = np.vstack([T, np.asarray(caps, dtype=np.int64)])
    return P, oriented(P, T, path)


def ribbon(points: np.ndarray, widths: np.ndarray, side: np.ndarray, normal: np.ndarray, thick: float):
    """A flat two-faced blade along `points` (K, 3), `widths` across `side`, the faces `thick` apart along `normal`
    (`side` and `normal` (3,) or (K, 3))."""
    K = len(points)
    side = np.broadcast_to(np.asarray(side, dtype=np.float64), (K, 3))
    normal = np.broadcast_to(np.asarray(normal, dtype=np.float64), (K, 3))
    L = points - side * widths[:, None] * 0.5
    R = points + side * widths[:, None] * 0.5
    P = np.vstack([L + normal * thick * 0.5, R + normal * thick * 0.5, L - normal * thick * 0.5,
                   R - normal * thick * 0.5])
    T = []
    for f in (0, 1):
        b = f * 2 * K
        for k in range(K - 1):
            t1 = (b + k, b + K + k, b + k + 1)
            t2 = (b + k + 1, b + K + k, b + K + k + 1)
            T += [t1, t2] if f == 0 else [t1[::-1], t2[::-1]]
    T = np.asarray(T, dtype=np.int64)
    n_mid = normal[K // 2]
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    want = np.where(np.arange(len(T)) < len(T) // 2, 1.0, -1.0)[:, None] * n_mid
    bad = (fn * want).sum(axis=1) < 0
    T[bad] = T[bad][:, ::-1]
    return P, T


def weights(J: list[tuple[int, int]], W: list[tuple[float, float]]):
    """A skin function that ignores P and returns fixed per-vertex joints and weights."""
    Ja, Wa = np.asarray(J, dtype=np.int64), np.asarray(W, dtype=np.float64)
    return lambda P: (Ja, Wa)


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def neck_points() -> np.ndarray:
    return np.asarray(NECK_PATH, dtype=np.float64)


def mirror(p) -> np.ndarray:
    return np.asarray(p, dtype=np.float64) * np.array([-1.0, 1.0, 1.0])


def side_tag(s: float) -> str:
    return "l" if s > 0 else "r"


def wing_joints(s: float) -> np.ndarray:
    return WING if s > 0 else mirror(WING)


def cord_joints(s: float) -> np.ndarray:
    return CORD_CHAIN if s > 0 else mirror(CORD_CHAIN)


def leg_r_joints() -> np.ndarray:
    return np.column_stack([np.full(len(LEG_R), -LEG_X), LEG_R[:, 0], LEG_R[:, 1]])


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    rig.add("body", BODY_PIVOT, SPINE[-1], "root")
    pts = neck_points()
    parent = "body"
    for k in range(3):
        rig.add(f"neck_{k}", pts[k], pts[k + 1], parent)
        parent = f"neck_{k}"
    rig.add("head", pts[3], HEAD_TIP, "neck_2")
    for s in (1.0, -1.0):
        t = side_tag(s)
        w = wing_joints(s)
        rig.add(f"wing_{t}0", w[0], w[1], "body")
        rig.add(f"wing_{t}1", w[1], w[2], f"wing_{t}0")
        rig.add(f"wing_{t}2", w[2], w[3], f"wing_{t}1")
        c = cord_joints(s)
        rig.add(f"cord_{t}0", c[0], c[1], f"wing_{t}2")
        rig.add(f"cord_{t}1", c[1], c[2], f"cord_{t}0")
    j = leg_r_joints()
    rig.add("leg_r0", j[0], j[1], "body")
    rig.add("leg_r1", j[1], j[2], "leg_r0")
    rig.add("talon_r", j[2], j[3], "leg_r1")
    rig.add("leg_l0", LEG_L[0], LEG_L[1], "body")
    rig.add("leg_l1", LEG_L[1], LEG_L[2], "leg_l0")
    rig.add("talon_l", LEG_L[2], LEG_L[3], "leg_l1")
    rig.add("bundle_0", BUNDLE[0], BUNDLE[1], "talon_l")
    rig.add("bundle_1", BUNDLE[1], BUNDLE[2], "bundle_0")
    rig.add("tail", TAIL_PTS[0], TAIL_PTS[1], "body")
    return rig


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def plumage(P: np.ndarray, N: np.ndarray, seed: int, dark: float = 0.0) -> np.ndarray:
    """overcast_slate going to storm_slate over the back and underneath, mottled like layered feathers."""
    mott = ck.smoothstep(-0.3, 0.45, ck.fbm(P * 3.0, seed))
    col = ck.mix(SLATE, DARK, np.clip(0.25 + 0.45 * mott + dark, 0.0, 1.0)[:, None])
    col = ck.mix(col, UNDER, (0.5 * np.clip(-N[:, 1], 0.0, 1.0))[:, None])
    return col


def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    path = ck.bezier(SPINE, 22)
    t = np.linspace(0.0, 1.0, len(path))
    r = np.array(BODY_RINGS)
    hw = np.interp(t, r[:, 0], r[:, 1])
    hd = np.interp(t, r[:, 0], r[:, 2])
    P, T = loft(path, hw, hd, 18, up_hint=(0.0, 0.3, 1.0))
    # the breast swells forward, the back flattens
    fwd = np.clip(P[:, 2] - np.interp(P[:, 1], path[:, 1], path[:, 2]), 0.0, None)
    P[:, 2] += 0.25 * fwd * np.sin(math.pi * np.clip((P[:, 1] - 1.0) / 0.8, 0.0, 1.0))
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    before = mesh.triangle_count
    skin = rig.blend("tail", "body", TAIL_PTS[0], (0.0, 1.1, -0.2))
    ck.finish(mesh, P, T, "plumage", plumage(P, N, SEED), skin, wet=0.1, N=N)
    count("body", mesh, before)


def neck_and_head(mesh: ck.Mesh, rig: ck.Rig) -> None:
    pts = neck_points()
    path = ck.bezier(((0.0, 1.70, 0.14),) + NECK_PATH[1:] + ((0.0, 2.08, 0.46),), 14)
    t = np.linspace(0.0, 1.0, len(path))
    rad = 0.13 * (1.0 - t) ** 1.2 + 0.055
    P, T = loft(path, rad, rad, 12, up_hint=(0.0, 0.0, 1.0))
    chain = rig.chain(["body", "neck_0", "neck_1", "neck_2", "head"],
                      np.vstack([[SPINE[2]], pts, [HEAD_TIP]]))
    k = np.clip((P[:, 1] - 1.8) / 0.25, 0.0, 1.0)  # bare skin above the ruff: bone going to slate
    col = ck.mix(DARK, ck.mix(PAL["bone"], SLATE, 0.45), k[:, None])
    before = mesh.triangle_count
    ck.finish(mesh, P, T, "head", col, chain, wet=0.1)
    count("neck", mesh, before)
    hb = rig.rigid("head")
    before = mesh.triangle_count
    P, T = ck.ellipsoid(SKULL_C, SKULL_R, 9, 14)
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    col = ck.mix(PAL["bone"], SLATE, (0.25 * ck.smoothstep(0.0, 0.1, SKULL_C[2] - P[:, 2]))[:, None])
    ck.finish(mesh, P, T, "head", col, hb, wet=0.15, N=N)
    # the beak: short, hooked, dark; a bone cere at its root
    path = ck.bezier(((0.0, 2.085, 0.53), (0.0, 2.09, 0.60), (0.0, 2.075, 0.655), (0.0, 2.035, 0.665)), 10)
    t = np.linspace(0.0, 1.0, len(path))
    P, T = loft(path, 0.032 * (1.0 - t) ** 0.8 + 0.006, 0.04 * (1.0 - t) ** 0.7 + 0.006, 10)
    k = ck.smoothstep(0.0, 0.3, (P[:, 2] - 0.53) / 0.13)
    ck.finish(mesh, P, T, "head", ck.mix(ck.mix(PAL["bone"], SLATE, 0.5), BEAK, k[:, None]), hb, wet=0.3)
    count("head", mesh, before)
    before = mesh.triangle_count
    for s in (1.0, -1.0):
        c = np.array([s * EYE_AT[0], EYE_AT[1], EYE_AT[2]])
        Pe, Te = ck.ellipsoid(c, (0.016, 0.018, 0.018), 5, 8)
        ck.finish(mesh, Pe, oriented(Pe, Te, c[None]), "eye", PAL["deep_teal_shadow"], hb, wet=1.0,
                  emission=EYE_GLOW)
    count("eyes", mesh, before)


def ruff(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A collar of short soft cords round the neck's base, gauze_white: a soft roll of them, and loose ends curling
    out and down over the shoulders."""
    rng = np.random.default_rng(SEED + 5)
    centre = np.array([0.0, 1.76, 0.17])
    axis = unit((0.0, 1.0, 0.45))
    e1 = np.array([1.0, 0.0, 0.0])
    e2 = np.cross(axis, e1)
    pts = neck_points()
    chain = rig.chain(["body", "neck_0", "neck_1"], np.vstack([[SPINE[2]], pts[:3]]))
    before = mesh.triangle_count
    # the roll: a torus of cord, lumpy where the cords bunch
    K, segs, R0, r0 = 24, 8, 0.15, 0.06
    a = np.arange(K) * 2.0 * math.pi / K
    b = np.arange(segs) * 2.0 * math.pi / segs
    P = []
    for i in range(K):
        radial = math.cos(a[i]) * e1 + math.sin(a[i]) * e2
        rr = r0 * (1.0 + 0.18 * math.sin(3.0 * a[i]) * math.cos(2.0 * a[i]))
        for j in range(segs):
            P.append(centre + radial * (R0 + rr * math.cos(b[j])) + axis * rr * math.sin(b[j]))
    P = np.asarray(P)
    T = []
    for i in range(K):
        for j in range(segs):
            i1, j1 = (i + 1) % K, (j + 1) % segs
            T += [(i * segs + j, i1 * segs + j, i * segs + j1), (i * segs + j1, i1 * segs + j, i1 * segs + j1)]
    ring = np.array([centre + (math.cos(x) * e1 + math.sin(x) * e2) * R0 for x in a])
    T = oriented(P, np.asarray(T, dtype=np.int64), ring)
    ck.finish(mesh, P, T, "ruff", PAL["gauze_white"], chain, wet=0.05, cavity=0.2, emission=RUFF_GLOW)
    # the loose ends
    n = 18
    for i in range(n):
        x = 2.0 * math.pi * (i + 0.5) / n + rng.uniform(-0.1, 0.1)
        radial = math.cos(x) * e1 + math.sin(x) * e2
        base = centre + radial * (R0 + 0.04) - axis * 0.02
        out = unit(radial * 0.7 - axis * 0.7)
        L = 0.13 * rng.uniform(0.8, 1.2)
        path = ck.bezier([base, base + radial * L * 0.6 + axis * 0.01, base + out * L], 5)
        r = np.linspace(0.02, 0.008, 5)
        P, T = loft(path, r, r, 4)
        ck.finish(mesh, P, T, "ruff", PAL["gauze_white"], chain, wet=0.05, emission=RUFF_GLOW)
    count("ruff", mesh, before)


def wing_plumage(mesh: ck.Mesh, rig: ck.Rig, s: float) -> None:
    """The inner wing: a covert cape along the arm and the secondaries hanging from it, slate, skinned to the arm."""
    t = side_tag(s)
    w = wing_joints(s)
    chain = rig.chain([f"wing_{t}0", f"wing_{t}1", f"wing_{t}2"], w)
    lead = np.vstack([ck.bezier([w[0], w[0] * 0.5 + w[1] * 0.5 + (0, 0.02, 0.02), w[1]], 6)[:-1],
                      ck.bezier([w[1], w[1] * 0.5 + w[2] * 0.5 + (0, 0.0, 0.05), w[2]], 6)[:-1],
                      ck.bezier([w[2], w[3]], 3)])
    K = len(lead)
    u = np.linspace(0.0, 1.0, K)
    drop = 0.46 * np.sin(math.pi * np.clip(u * 0.9 + 0.1, 0.0, 1.0)) ** 0.6 + 0.08
    down = np.array([s * 0.12, -1.0, -0.08])
    down = unit(down)
    before = mesh.triangle_count
    # the coverts: a thick two-sided cape, the leading edge rounded over the arm
    rows = 4
    grid = np.array([lead + np.outer(drop * (r / (rows - 1)), down) for r in range(rows)])  # (rows, K, 3)
    nrm = np.cross(np.gradient(lead, axis=0), down)
    nrm = nrm / np.linalg.norm(nrm, axis=1, keepdims=True)
    nrm *= np.sign(nrm[:, 0:1] * s + 1e-9)
    thick = 0.05 * (1.0 - np.linspace(0.0, 1.0, rows))[:, None, None] + 0.012
    top = (grid + thick * nrm[None]).reshape(-1, 3)
    bot = (grid - thick * nrm[None]).reshape(-1, 3)
    P = np.vstack([top, bot])
    T = np.vstack([ck.grid_tris(rows, K, False), ck.flip(ck.grid_tris(rows, K, False)) + rows * K])
    # close the lower edge and the two ends
    edge = []
    for k in range(K - 1):
        a, b = (rows - 1) * K + k, (rows - 1) * K + k + 1
        edge += [(a, b, a + rows * K), (b, b + rows * K, a + rows * K)]
    for k in (0, K - 1):
        for r in range(rows - 1):
            a, b = r * K + k, (r + 1) * K + k
            edge += [(a, b, a + rows * K), (b, b + rows * K, a + rows * K)]
    T = np.vstack([T, np.asarray(edge, dtype=np.int64)])
    centres = np.vstack([grid.reshape(-1, 3)])
    T = oriented(P, T, centres)
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    ck.finish(mesh, P, T, "plumage", plumage(P, N, SEED + 20, 0.1), chain, wet=0.1, N=N)
    # the secondaries: broad blades hanging from the cape's edge, overlapping, pale-edged
    n = 11
    for i in range(n):
        f = 0.04 + 0.88 * i / (n - 1)
        k = f * (K - 1)
        k0 = int(k)
        a = lead[k0] + (lead[min(k0 + 1, K - 1)] - lead[k0]) * (k - k0)
        dd = float(np.interp(f, u, drop))
        root = a + down * dd * 0.6
        ln = 0.5 + 0.3 * math.sin(math.pi * min(f * 1.2, 1.0))
        hang = unit(down + np.array([0.0, 0.0, -0.18 - 0.1 * f]))
        pts = ck.bezier([root, root + hang * ln * 0.5 + np.array([s * 0.02, 0.0, 0.0]), root + hang * ln], 6)
        side = unit(np.cross(hang, np.array([s, 0.0, 0.0])))
        normal = unit(np.cross(side, hang)) * s
        g = np.linspace(0.0, 1.0, len(pts))
        width = 0.18 * np.sin(math.pi * np.clip(0.12 + g * 0.88, 0.0, 1.0)) ** 0.4 + 0.012
        Pr, Tr = ribbon(pts, width, side, normal + np.array([s * 0.02 * i, 0.0, 0.0]), 0.012)
        gv = np.tile(g, 4)
        col = ck.mix(DARK, SLATE, (0.6 * ck.smoothstep(0.7, 1.0, gv))[:, None])
        ck.finish(mesh, Pr, Tr, "plumage", col, chain, wet=0.1)
    count("wing plumage", mesh, before)


def keth_digits(n: int) -> list[int]:
    return [int(c) for c in str(n)]


def cord_numbers(rng: np.random.Generator) -> list[int]:
    """The number each cord of a wing carries, leading cord first: 47 and 7 on the two outermost, then her ledger."""
    out = list(KETH_FIXED)
    while len(out) < N_CORDS:
        out.append(int(rng.integers(2, 7)) * 10 + int(rng.integers(0, 10)))
    return out


def knot_plan(n: int) -> list[tuple[str, float, int]]:
    """(kind, arc length from the hand, turns) for every knot of the number `n`: beads, a long knot or a
    figure-eight; places nearest the hand first."""
    digits = keth_digits(n)
    out = []
    s = KETH_START
    for i, d in enumerate(digits):
        units = i == len(digits) - 1
        if units:
            if d == 1:
                out.append(("eight", s + 0.03, 1))
            elif d >= 2:
                out.append(("long", s, d))
        else:
            for k in range(d):
                out.append(("bead", s + k * KNOT_STEP, 1))
            s += max(d - 1, 0) * KNOT_STEP
            s += PLACE_GAP
    return out


def place_along(path: np.ndarray, arc: np.ndarray, s: float) -> tuple[np.ndarray, np.ndarray]:
    i = int(np.clip(np.searchsorted(arc, s) - 1, 0, len(path) - 2))
    f = (s - arc[i]) / max(arc[i + 1] - arc[i], 1e-9)
    return path[i] + (path[i + 1] - path[i]) * f, unit(path[i + 1] - path[i])


def frame_of(tan: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    a = np.array([1.0, 0.0, 0.0]) if abs(tan[0]) < 0.9 else np.array([0.0, 0.0, 1.0])
    n = unit(np.cross(tan, a))
    return n, np.cross(tan, n)


def cord_skin(rig: ck.Rig, t: str, g: np.ndarray, hand_end: float):
    """Joints and weights by the fraction `g` along a cord: the hand at its root, cord_<t>0 down to the middle,
    cord_<t>1 beyond, blended across each change."""
    ih, i0, i1 = rig.index(f"wing_{t}2"), rig.index(f"cord_{t}0"), rig.index(f"cord_{t}1")
    J, W = [], []
    for x in g:
        if x < hand_end:
            w = float(ck.smoothstep(0.0, hand_end, x))
            J.append((ih, i0))
            W.append((1.0 - w, w))
        elif x < 0.42:
            J.append((i0, i1))
            W.append((1.0, 0.0))
        else:
            w = float(ck.smoothstep(0.42, 0.7, x))
            J.append((i0, i1))
            W.append((1.0 - w, w))
    return J, W


def cords(mesh: ck.Mesh, rig: ck.Rig, s: float) -> None:
    """Eight knotted cord primaries per wing, hanging from the hand in a fan (leading cord forward)."""
    t = side_tag(s)
    w = wing_joints(s)
    rng = np.random.default_rng(SEED + (1 if s > 0 else 2))
    numbers = cord_numbers(rng)
    for i in range(N_CORDS):
        f = i / (N_CORDS - 1)
        root = w[2] + (w[3] - w[2]) * (0.35 + 0.65 * (1.0 - f)) + np.array([0.0, 0.0, 0.03 - 0.06 * f])
        fan = math.radians(CORD_FAN[i])
        out = math.radians(CORD_OUT + 4.0 * (1.0 - f))
        d = unit(np.array([s * math.sin(out), -math.cos(fan) * math.cos(out), math.sin(fan)]))
        L = CORD_LEN[i]
        bow = np.array([s * 0.05, 0.0, -0.03])
        path = ck.bezier([root, root + d * L * 0.5 + bow, root + d * L], max(int(L / CORD_STEP), 8))
        arc = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
        g = arc / arc[-1]
        twist = 2.0 * math.pi * arc / STRAND_PITCH * 0.5  # the two-lobed section turns once per half pitch
        rad = CORD_R * (1.0 - 0.35 * ck.smoothstep(0.85, 1.0, g))
        P, T = loft(path, rad, rad * 0.78, CORD_SEGS, up_hint=(0.0, 0.0, 1.0), twist=twist)
        # the sand_cloth strand: a helical stripe round the white rope
        K = len(path)
        a = np.tile(np.arange(CORD_SEGS) * 2.0 * math.pi / CORD_SEGS, K) + np.repeat(twist, CORD_SEGS)
        stripe = ck.smoothstep(0.55, 0.85, np.cos(a))
        stripe = np.r_[stripe, 0.0, 0.0]
        col = ck.mix(PAL["gauze_white"], PAL["sand_cloth"], stripe[:, None])
        gv = np.r_[np.repeat(g, CORD_SEGS), 0.0, 1.0]
        J, W = cord_skin(rig, t, gv, 0.12)
        before = mesh.triangle_count
        ck.finish(mesh, P, T, "cord", col, weights(J, W), wet=0.05, cavity=0.15, emission=CORD_GLOW)
        count("cords", mesh, before)
        before = mesh.triangle_count
        for kind, sk, turns in knot_plan(numbers[i]):
            knot(mesh, rig, t, path, arc, kind, sk, turns)
        count("knots", mesh, before)


def knot(mesh: ck.Mesh, rig: ck.Rig, t: str, path: np.ndarray, arc: np.ndarray, kind: str, s: float,
         turns: int) -> None:
    c, tan = place_along(path, arc, s)
    n, b = frame_of(tan)
    R = np.column_stack([n, tan, b])  # the knot's local y runs along the cord
    if kind == "bead":
        P, T = ck.ellipsoid((0.0, 0.0, 0.0), (0.033, 0.03, 0.033), 3, 6)
        P = P @ R.T + c
        T = oriented(P, T, c[None])
        span = (s, s)
    elif kind == "eight":
        parts = []
        for k, sgn in ((0, 1.0), (1, -1.0)):
            q = c + tan * (k * 0.036 - 0.018) + n * 0.01 * sgn
            Pq, Tq = ck.ellipsoid((0.0, 0.0, 0.0), (0.026, 0.024, 0.03), 3, 6)
            Pq = Pq @ ck.rot_y(35.0 * sgn).T @ R.T + q
            parts.append((Pq, oriented(Pq, Tq, q[None])))
        P = np.vstack([parts[0][0], parts[1][0]])
        T = np.vstack([parts[0][1], parts[1][1] + len(parts[0][0])])
        span = (s - 0.018, s + 0.018)
    else:  # a long knot: the cord wound round itself `turns` times, a sleeve with a ridge per turn
        L = turns * TURN_PITCH
        k = 2 * turns + 1
        u = np.linspace(0.0, 1.0, k)
        pts = np.array([place_along(path, arc, s + L * x)[0] for x in u])
        ridge = np.where(np.arange(k) % 2 == 1, 1.0, 0.55)
        ridge[0] = ridge[-1] = 0.6
        r = (CORD_R + 0.014) * ridge
        P, T = loft(pts, r, r, 5, up_hint=n)
        span = (s, s + L)
    g = np.full(len(P), 0.5 * (span[0] + span[1]) / arc[-1])
    J, W = cord_skin(rig, t, g, 0.12)
    ck.finish(mesh, P, T, "cord", PAL["gauze_white"], weights(J, W), wet=0.05, emission=KNOT_GLOW)


def legs(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for leg, J in (("r", leg_r_joints()), ("l", LEG_L)):
        b0, b1, bt = f"leg_{leg}0", f"leg_{leg}1", f"talon_{leg}"
        before = mesh.triangle_count
        # the feathered thigh ("trousers"), slate, into the body
        path = ck.bezier([J[0] + (0, 0.06, 0.04), J[0] * 0.5 + J[1] * 0.5 + (0, 0, 0.05), J[1]], 8)
        g = np.linspace(0.0, 1.0, len(path))
        P, T = loft(path, 0.12 * (1.0 - g) + 0.06, 0.13 * (1.0 - g) + 0.06, 10, up_hint=(1.0, 0.0, 0.0))
        N = ck.weld_normals(P, ck.vertex_normals(P, T))
        ck.finish(mesh, P, T, "plumage", plumage(P, N, SEED + 30, 0.2), rig.blend(b0, b1, J[0], J[1]), wet=0.1, N=N)
        # the bare tarsus, grey bone
        path = ck.bezier([J[1], J[1] * 0.5 + J[2] * 0.5, J[2]], 6)
        P, T = loft(path, 0.04, 0.044, 8, up_hint=(1.0, 0.0, 0.0))
        skin_col = ck.mix(PAL["bone"], DARK, 0.55)
        ck.finish(mesh, P, T, "head", skin_col, rig.blend(b1, bt, J[1] + (J[2] - J[1]) * 0.7, J[2]), wet=0.2)
        count("legs", mesh, before)
        before = mesh.triangle_count
        tb = rig.rigid(bt)
        x = float(J[2][0])
        if leg == "r":  # planted: three toes forward, one back, flat on the water
            c = np.array([x, 0.05, J[2][2] + 0.02])
            Pf, Tf = ck.ellipsoid(c, (0.06, 0.045, 0.07), 5, 8)
            ck.finish(mesh, Pf, Tf, "head", skin_col, tb, wet=0.2)
            for ang, ln in ((-24.0, 0.2), (0.0, 0.25), (24.0, 0.2), (180.0, 0.09)):
                d = ck.rot_y(ang) @ np.array([0.0, 0.0, 1.0])
                toe = np.array([c + d * ln * f + (0.0, -0.02 * f, 0.0) for f in np.linspace(0.0, 1.0, 6)])
                r = np.linspace(0.028, 0.016, 6)
                toe[:, 1] = np.maximum(toe[:, 1], r)
                Pt, Tt = loft(toe, r, r, 6)
                ck.finish(mesh, Pt, Tt, "head", skin_col, tb, wet=0.2)
                tip = toe[-1]
                claw = ck.bezier([tip, tip + d * 0.035, tip + d * 0.055 + (0, -0.012, 0)], 4)
                claw[:, 1] = np.maximum(claw[:, 1], 0.006)
                Pc, Tc = loft(claw, np.linspace(0.013, 0.003, 4), np.linspace(0.013, 0.003, 4), 5)
                ck.finish(mesh, Pc, Tc, "head", BEAK, tb, wet=0.3)
        else:  # drawn up: the toes closed round the bundle's binding
            top = BUNDLE[0]
            for ang in (-40.0, 0.0, 40.0, 180.0):
                d = ck.rot_y(ang) @ np.array([0.0, 0.0, 1.0])
                ring = [top + (0.0, 0.03, 0.0) + d * 0.05 * math.sin(a) + np.array([0.0, 0.05 * math.cos(a), 0.0])
                        - (0.0, 0.05, 0.0) for a in np.linspace(0.0, 2.2, 6)]
                ring = np.asarray(ring) * 1.0
                ring[0] = J[2] + (0.0, -0.02, 0.0) + d * 0.02
                Pt, Tt = loft(ring, np.linspace(0.026, 0.014, 6), np.linspace(0.026, 0.014, 6), 6)
                ck.finish(mesh, Pt, Tt, "head", skin_col, tb, wet=0.2)
                Pc, Tc = ck.ellipsoid(ring[-1], (0.012, 0.012, 0.012), 3, 5)
                ck.finish(mesh, Pc, oriented(Pc, Tc, ring[-1][None]), "head", BEAK, tb, wet=0.3)
        count("feet", mesh, before)


def bundle(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The keepsake: a keth bundle, a dozen cords of sand_cloth and faded_teal_cloth bound at the top, hanging from
    her left talon to 0.1 m over the water. An object: no light."""
    rng = np.random.default_rng(SEED + 9)
    top = BUNDLE[0]
    chain = rig.chain(["talon_l", "bundle_0", "bundle_1"], np.vstack([[LEG_L[2]], BUNDLE]))
    before = mesh.triangle_count
    path = np.array([top + (0.0, 0.02, 0.0), top - (0.0, 0.06, 0.0)])
    path = ck.bezier(path, 4)
    P, T = loft(path, 0.032, 0.032, 10, up_hint=(0.0, 0.0, 1.0))
    ck.finish(mesh, P, T, "bundle", PAL["sand_cloth"], chain, wet=0.05, cavity=0.3)
    n = 9
    for i in range(n):
        a = 2.0 * math.pi * i / n + rng.uniform(-0.2, 0.2)
        rr = 0.02 + 0.01 * (i % 2)
        root = top + np.array([math.cos(a) * rr, -0.05, math.sin(a) * rr])
        bottom_y = BUNDLE[2][1] + rng.uniform(0.0, 0.05)
        end = np.array([root[0] + math.cos(a) * 0.05, bottom_y, root[2] + math.sin(a) * 0.05])
        pts = ck.bezier([root, root * 0.5 + end * 0.5 + (math.cos(a) * 0.02, 0.0, math.sin(a) * 0.02), end], 5)
        P, T = loft(pts, 0.007, 0.007, 4)
        col = PAL["sand_cloth"] if i % 3 else PAL["faded_teal_cloth"]
        ck.finish(mesh, P, T, "bundle", col, chain, wet=0.05, cavity=0.3)
        for k in range(1):
            q = pts[int(rng.integers(1, 4))]
            Pk, Tk = ck.ellipsoid(q, (0.013, 0.014, 0.013), 3, 5)
            ck.finish(mesh, Pk, oriented(Pk, Tk, q[None]), "bundle", col, chain, cavity=0.4)
    count("bundle", mesh, before)


def tail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A short fan of tail feathers under the rump, hanging, so she keeps inside the frame's right edge."""
    tb = rig.blend("body", "tail", TAIL_PTS[0], TAIL_PTS[1])
    before = mesh.triangle_count
    for sx in (-0.6, -0.2, 0.2, 0.6):
        a = TAIL_PTS[0] + (sx * 0.14, 0.0, 0.03)
        pts = ck.bezier([a, a + (sx * 0.06, -0.12, -0.08), a + (sx * 0.1, -0.3, -0.14)], 5)
        hang = unit(pts[-1] - pts[0])
        side = unit(np.cross(hang, (0.0, 1.0, 0.0)) + np.array([0.0, 0.0, 0.0]))
        if abs(side[0]) < 0.5:
            side = np.array([1.0, 0.0, 0.0])
        normal = unit(np.cross(side, hang))
        g = np.linspace(0.0, 1.0, len(pts))
        P, T = ribbon(pts, 0.11 * np.sin(math.pi * np.clip(0.2 + g * 0.8, 0.0, 1.0)) ** 0.4 + 0.02, side, normal,
                      0.012)
        ck.finish(mesh, P, T, "plumage", DARK, tb, wet=0.1)
    count("tail", mesh, before)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    PARTS.clear()
    mesh = ck.Mesh("hesk")
    body(mesh, rig)
    neck_and_head(mesh, rig)
    ruff(mesh, rig)
    for s in (1.0, -1.0):
        wing_plumage(mesh, rig, s)
        cords(mesh, rig, s)
    legs(mesh, rig)
    bundle(mesh, rig)
    tail(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# The right talon: planted and solved onto the water at every frame (Kahre's solve, M3-CRE-640)
# ---------------------------------------------------------------------------------------------
def _ang(v) -> float:
    return math.degrees(math.atan2(v[1], v[0]))


def _euler_of(R: np.ndarray) -> tuple[float, float, float]:
    """(rx, ry, rz) degrees with R = rot_z(rz) @ rot_y(ry) @ rot_x(rx) (creature_kit.euler)."""
    ry = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    rx = math.atan2(R[2, 1], R[2, 2])
    rz = math.atan2(R[1, 0], R[0, 0])
    return math.degrees(rx), math.degrees(ry), math.degrees(rz)


def _solve2(hip, knee, ankle, target) -> tuple[float, float]:
    """The (upper, lower) rx that put `ankle` on `target`, all (z, y) in the parent's rest frame; the joint bends
    the way it does at rest."""
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


SCRATCH = ("tgt_", "free_")
LEG_R_BONES = ("leg_r0", "leg_r1", "talon_r")


def solve_legs(clip: ck.Clip, poser: grounding.Poser) -> ck.Clip:
    """`clip` with the right leg keyed at every baked frame: the solve that puts the ankle on its target (the rest
    ankle plus the `tgt_r` offset) with the foot level. The scratch tracks are dropped."""
    out = ck.Clip(clip.name, clip.length, loop=clip.loop)
    for b, ks in clip.keys.items():
        if b not in LEG_R_BONES and not b.startswith(SCRATCH):
            out.keys[b] = list(ks)
    j = leg_r_joints()
    for t in grounding.frame_times(clip):
        pose = grounding.pose_at(clip, poser.names, t)
        mats = poser.matrices(pose)
        tgt_rot, tgt_off = clip.sample("tgt_r", t)
        Mp = mats[poser.rig.index("body")]
        target = j[2] + np.asarray(tgt_off)
        local = np.linalg.solve(Mp, np.append(target, 1.0))[:3]
        ru, rl = _solve2(j[0, 1:][::-1], j[1, 1:][::-1], j[2, 1:][::-1], local[1:][::-1])
        Rw = Mp[:3, :3] @ ck.euler(ru, 0.0, 0.0) @ ck.euler(rl, 0.0, 0.0)
        rf = _euler_of(Rw.T @ ck.euler(float(tgt_rot[0]), 0.0, 0.0))
        for b, rot in zip(LEG_R_BONES, (np.array([ru, 0.0, 0.0]), np.array([rl, 0.0, 0.0]), np.array(rf))):
            out.key(b, t, tuple(float(v) for v in rot), (0.0, 0.0, 0.0))
    return out


# ---------------------------------------------------------------------------------------------
# Wing poses: each bone aimed in the body's frame (its direction, and the way its feathers or its fan face)
# ---------------------------------------------------------------------------------------------
WING_BONES = ("0", "1", "2")
CORD_BONES = ("0", "1")


def _frame(d, f) -> np.ndarray:
    d = unit(d)
    f = np.asarray(f, dtype=np.float64)
    f = unit(f - float(f @ d) * d)
    return np.column_stack([d, f, np.cross(d, f)])


def _rest_dirs(s: float) -> list[tuple[np.ndarray, np.ndarray]]:
    w, c = wing_joints(s), cord_joints(s)
    down, fwd = np.array([0.0, -1.0, 0.0]), np.array([0.0, 0.0, 1.0])
    return [(w[1] - w[0], down), (w[2] - w[1], down), (w[3] - w[2], fwd), (c[1] - c[0], fwd), (c[2] - c[1], fwd)]


# Left wing, body frame; (direction, feather facing) for humerus, forearm, hand, cord_0, cord_1. None keeps rest.
WING_POSES = {
    "rest": None,
    "fold": [((0.30, 0.42, -0.55), (0.2, -1.0, -0.4)), ((0.05, 0.55, 0.45), (0.25, -1.0, 0.0)),
             ((0.12, -1.0, -0.2), (0.0, -0.15, 1.0)), ((0.12, -1.0, -0.12), (0.0, -0.1, 1.0)),
             ((0.08, -1.0, -0.15), (0.0, -0.1, 1.0))],
    "half": [((0.75, 0.80, -0.25), (0.0, -1.0, -0.5)), ((0.75, 0.70, 0.25), (0.0, -1.0, -0.4)),
             ((0.75, -0.8, 0.05), (0.0, 0.0, 1.0)), ((0.55, -1.0, 0.0), (0.0, 0.0, 1.0)),
             ((0.35, -1.0, -0.05), (0.0, 0.0, 1.0))],
    "wide": [((1.0, 0.45, -0.15), (0.0, -1.0, -0.6)), ((1.0, 0.30, 0.15), (0.0, -1.0, -0.6)),
             ((1.0, -0.55, 0.0), (0.0, 0.0, 1.0)), ((0.7, -1.0, 0.0), (0.0, 0.0, 1.0)),
             ((0.3, -1.0, 0.0), (0.0, 0.0, 1.0))],
    "full": [((1.0, 0.18, -0.10), (0.0, -1.0, -0.7)), ((1.0, 0.12, 0.08), (0.0, -1.0, -0.7)),
             ((1.0, -0.15, 0.0), (0.0, 0.0, 1.0)), ((0.8, -1.0, 0.0), (0.0, 0.0, 1.0)),
             ((0.3, -1.0, 0.0), (0.0, 0.0, 1.0))],
    "raised": [((0.8, 0.75, -0.10), (0.0, -1.0, -0.7)), ((1.0, 0.45, 0.08), (0.0, -1.0, -0.7)),
               ((1.0, 0.25, 0.0), (0.0, 0.0, 1.0)), ((1.0, -0.8, 0.0), (0.0, 0.0, 1.0)),
               ((0.5, -1.0, 0.0), (0.0, 0.0, 1.0))],
    "forward": [((0.55, 0.45, 0.65), (0.0, -1.0, 0.2)), ((0.25, 0.10, 1.0), (0.0, -1.0, 0.0)),
                ((0.15, -0.55, 1.0), (-1.0, 0.0, 0.0)), ((0.1, -0.9, 0.7), (-1.0, 0.0, 0.0)),
                ((0.0, -1.0, 0.25), (-1.0, 0.0, 0.0))],
    "mantle": [((0.45, 0.55, 0.35), (0.0, -1.0, 0.3)), ((0.05, 0.45, 1.0), (0.3, -1.0, 0.0)),
               ((-0.05, -1.0, 0.4), (-0.3, 0.0, 1.0)), ((-0.08, -1.0, 0.15), (-0.3, 0.0, 1.0)),
               ((-0.05, -1.0, 0.05), (-0.3, 0.0, 1.0))],
    "down": [((1.0, -0.3, 0.1), (0.0, -0.3, -1.0)), ((1.0, -0.5, 0.35), (0.0, -0.3, -1.0)),
             ((0.7, -0.8, 0.7), (0.0, 0.0, 1.0)), ((0.3, -1.0, 0.8), (0.0, 0.0, 1.0)),
             ((0.05, -1.0, 0.9), (0.0, 0.0, 1.0))],
    "flat": [((1.0, -0.45, -0.20), (0.0, -0.4, -1.0)), ((1.0, -0.35, 0.05), (0.0, -0.4, -1.0)),
             ((0.7, -0.2, 0.6), (0.0, 0.0, 1.0)), ((0.4, -0.1, 1.0), (0.0, 0.0, 1.0)),
             ((0.15, -0.05, 1.0), (0.0, 0.0, 1.0))],
}
# The open poses cup forward, a condor's display: added to every bone direction's forward (z) component. Without it
# the near wing's trailing cords cross the default battle camera's right safe edge (the Vowbound slot is 1.1 m from
# it); with it every frame keeps inside (docs/kb/art/creatures/vowbound/hesk.md "Framing").
WING_SWEEP = {"half": 0.2, "wide": 0.35, "full": 0.35, "raised": 0.35, "flat": 0.3}


def wing_euler(name: str, s: float) -> list[np.ndarray]:
    """The local Euler keys (humerus, forearm, hand, cord_0, cord_1) that put one wing in pose `name`."""
    spec = WING_POSES[name]
    if spec is None:
        return [np.zeros(3) for _ in range(5)]
    rest = _rest_dirs(s)
    flip = np.array([s, 1.0, 1.0])
    sweep = np.array([0.0, 0.0, WING_SWEEP.get(name, 0.0)])
    out, parent = [], np.eye(3)
    for (d0, f0), (d1, f1) in zip(rest, spec):
        Rw = _frame(np.asarray(d1) * flip + sweep, np.asarray(f1) * flip) @ _frame(d0, f0).T
        out.append(np.array(_euler_of(parent.T @ Rw)))
        parent = Rw
    return out


EULER_CACHE: dict[tuple[str, float], list[np.ndarray]] = {}


def wings(c: ck.Clip, t: float, pose_l: str, pose_r: str | None = None, mix_to: str | None = None, u: float = 0.0,
          sway=(0.0, 0.0)) -> None:
    """Keys both wings at `t`: pose_l on the left, pose_r (default the same) on the right, each blended `u` of the way
    to `mix_to`; `sway` (degrees) adds a lag to cord_0 and cord_1 about the hand's forward axis."""
    for s, name in ((1.0, pose_l), (-1.0, pose_r or pose_l)):
        e = EULER_CACHE.setdefault((name, s), wing_euler(name, s))
        if mix_to is not None:
            e2 = EULER_CACHE.setdefault((mix_to, s), wing_euler(mix_to, s))
            e = [ck.mix(a, b, u) for a, b in zip(e, e2)]
        tg = side_tag(s)
        for k, b in enumerate(WING_BONES):
            c.key(f"wing_{tg}{b}", t, tuple(float(v) for v in e[k]))
        for k, b in enumerate(CORD_BONES):
            r = e[3 + k] + np.array([sway[k], 0.0, 0.0])
            c.key(f"cord_{tg}{b}", t, tuple(float(v) for v in r))


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
IDLE_B_SEC = 1.2


def pose(c: ck.Clip, t: float, body=(0.0, 0.0, 0.0), lift: float = 0.0, slide: float = 0.0,
         neck=(0.0, 0.0, 0.0), head: float = 0.0, turn: float = 0.0, tail: float = 0.0, grip: float = 0.0,
         bundle=(0.0, 0.0)) -> None:
    """One key of the body. body (rx, ry, rz) about the pivot (+rx: bows forward), lift/slide (m), neck (rx per
    bone), head (rx, + down), turn (ry over the neck), tail (+ lifts), grip (the held talon closes, degrees),
    bundle (rx of bundle_0, bundle_1: its swing)."""
    c.key("body", t, body, (0.0, lift, slide))
    for k in range(3):
        c.key(f"neck_{k}", t, (neck[k], turn / 3.0, 0.0))
    c.key("head", t, (head, 0.0, 0.0))
    c.key("tail", t, (-tail, 0.0, 0.0))
    c.key("leg_l0", t, (-grip * 0.4, 0.0, 0.0))
    c.key("leg_l1", t, (grip * 0.3, 0.0, 0.0))
    c.key("talon_l", t, (grip, 0.0, 0.0))
    c.key("bundle_0", t, (bundle[0], 0.0, 0.0))
    c.key("bundle_1", t, (bundle[1], 0.0, 0.0))


def foot(c: ck.Clip, t: float, dy: float = 0.0, dz: float = 0.0, pitch: float = 0.0) -> None:
    c.key("tgt_r", t, (pitch, 0.0, 0.0), (0.0, dy, dz))


def build_idle() -> ck.Clip:
    c = ck.Clip("idle", IDLE_SEC, loop=True)  # perched: her weight rocks on the talon, the cords sway, she looks about
    c.wave("body", amp_rot=(1.2, 0.0, 1.6), amp_loc=(0.0, 0.015, 0.0), cycles=1, phase=0.0)
    for k in range(3):
        c.wave(f"neck_{k}", amp_rot=(1.5, 3.0, 0.0), cycles=1, phase=-0.5 * k - 0.7)
    c.wave("head", amp_rot=(-3.0, 4.0, 0.0), cycles=1, phase=-2.2)
    c.wave("tail", amp_rot=(2.0, 0.0, 0.0), cycles=2, phase=0.3)
    c.wave("talon_l", amp_rot=(3.0, 0.0, 0.0), cycles=1, phase=1.2)
    c.wave("bundle_0", amp_rot=(2.5, 0.0, 2.0), cycles=1, phase=0.6)
    c.wave("bundle_1", amp_rot=(3.0, 0.0, 2.5), cycles=1, phase=-0.2)
    for s in (1.0, -1.0):
        tg = side_tag(s)
        c.wave(f"wing_{tg}0", amp_rot=(1.0, 0.0, 1.2 * s), cycles=1, phase=0.4)
        c.wave(f"cord_{tg}0", amp_rot=(2.5, 0.0, 1.5 * s), cycles=1, phase=-0.4 + (0.3 if s < 0 else 0.0))
        c.wave(f"cord_{tg}1", amp_rot=(3.5, 0.0, 2.0 * s), cycles=1, phase=-1.1 + (0.3 if s < 0 else 0.0))
    foot(c, 0.0)
    foot(c, IDLE_SEC)
    return c


def build_ready() -> ck.Clip:
    c = ck.Clip("ready", READY_SEC)  # the wings half open, the cords lift, the head raised
    for t, kw in ((0.0, {}), (0.45, dict(body=(-4.0, 0.0, 0.0), lift=0.04, neck=(-6.0, -4.0, -3.0), head=-8.0)),
                  (0.9, dict(body=(-3.0, 0.0, 0.0), lift=0.03, neck=(-5.0, -4.0, -3.0), head=-6.0, grip=6.0)),
                  (READY_SEC, {})):
        pose(c, t, **kw)
    wings(c, 0.0, "rest")
    wings(c, 0.45, "half", sway=(-6.0, -10.0))
    wings(c, 0.7, "half", sway=(4.0, 8.0))
    wings(c, 0.95, "half", mix_to="rest", u=0.3)
    wings(c, READY_SEC, "rest")
    foot(c, 0.0)
    foot(c, READY_SEC)
    return c


def build_attack() -> ck.Clip:
    """The wing-buffet: she draws the near (left) wing back and high, then swings it forward at the foes, the cords
    lashing behind the hand."""
    c = ck.Clip("attack", ATTACK_SEC)
    for t, kw in ((0.0, {}),
                  (0.32, dict(body=(-6.0, 12.0, -4.0), lift=0.03, neck=(-4.0, -4.0, -2.0), head=-6.0, turn=-6.0)),
                  (ATTACK_CONTACT, dict(body=(10.0, -14.0, 3.0), lift=-0.03, neck=(6.0, 6.0, 4.0), head=4.0,
                                        turn=12.0)),
                  (0.8, dict(body=(6.0, -8.0, 2.0), neck=(4.0, 4.0, 2.0), head=2.0, turn=8.0)), (ATTACK_SEC, {})):
        pose(c, t, **kw)
    wings(c, 0.0, "rest")
    wings(c, 0.32, "wide", "half", sway=(-10.0, -16.0))
    wings(c, ATTACK_CONTACT, "forward", "half", sway=(18.0, 24.0))
    wings(c, 0.72, "forward", "half", mix_to="rest", u=0.2, sway=(-6.0, -10.0))
    wings(c, ATTACK_SEC, "rest")
    foot(c, 0.0)
    foot(c, ATTACK_SEC)
    return c


def build_cast() -> ck.Clip:
    c = ck.Clip("cast", CAST_SEC)  # the holy light: the wings spread wide and held, the head raised, the knots lit
    held = dict(body=(-6.0, 0.0, 0.0), lift=0.05, neck=(-8.0, -6.0, -4.0), head=-10.0, tail=4.0)
    for t, kw in ((0.0, {}), (0.5, held), (CAST_CONTACT, dict(held, body=(-2.0, 0.0, 0.0), head=-4.0)),
                  (1.2, held), (CAST_SEC, {})):
        pose(c, t, **kw)
    wings(c, 0.0, "rest")
    wings(c, 0.5, "wide", sway=(-6.0, -10.0))
    wings(c, CAST_CONTACT, "wide", sway=(4.0, 6.0))
    wings(c, 1.2, "wide")
    wings(c, CAST_SEC, "rest")
    foot(c, 0.0)
    foot(c, CAST_SEC)
    return c


def build_hit(name: str = "hit", side: float = 1.0, amp: float = 1.0) -> ck.Clip:
    """A flinch: the head drawn down into the ruff, the body rocked back, the wings jerked in. hit_b is authored (the
    other side, heavier): the kit's scaled copy would push the solved talon through the water."""
    c = ck.Clip(name, HIT_SEC)
    for t, s in ((0.0, 0.0), (HIT_PEAK, amp), (0.26, -0.2 * amp), (HIT_SEC, 0.0)):
        pose(c, t, body=(-6.0 * s, 0.0, 4.0 * s * side), lift=-0.03 * s, slide=-0.04 * s,
             neck=(14.0 * s, 10.0 * s, -6.0 * s), head=12.0 * s, turn=-6.0 * s * side, grip=8.0 * s,
             bundle=(-8.0 * s, -6.0 * s))
    wings(c, 0.0, "rest")
    wings(c, HIT_PEAK, "rest", mix_to="fold", u=0.35 * amp, sway=(-8.0 * amp, -12.0 * amp))
    wings(c, 0.26, "rest", sway=(4.0 * amp, 6.0 * amp))
    wings(c, HIT_SEC, "rest")
    foot(c, 0.0)
    foot(c, HIT_SEC)
    return c


def build_defend() -> ck.Clip:
    c = ck.Clip("defend", DEFEND_SEC)  # the wings mantled forward round her, the head low behind them
    held = dict(body=(6.0, 0.0, 0.0), lift=-0.06, neck=(10.0, 8.0, 4.0), head=10.0, grip=6.0)
    for t, kw in ((0.0, {}), (0.3, held), (0.85, held), (DEFEND_SEC, {})):
        pose(c, t, **kw)
    wings(c, 0.0, "rest")
    wings(c, 0.3, "mantle", sway=(4.0, 6.0))
    wings(c, 0.85, "mantle")
    wings(c, DEFEND_SEC, "rest")
    foot(c, 0.0)
    foot(c, DEFEND_SEC)
    return c


KO_DOWN = dict(body=(14.0, 0.0, 4.0), lift=-0.5, slide=0.05, neck=(26.0, 22.0, 16.0), head=20.0, tail=-6.0,
               grip=-20.0, bundle=(-70.0, -10.0))


def build_ko() -> ck.Clip:
    c = ck.Clip("ko", KO_SEC)  # she settles onto the water, the wings spread flat on it, the head bowed
    for t, kw in ((0.0, {}), (0.25, dict(body=(-5.0, 0.0, 0.0), lift=0.02, neck=(-4.0, -4.0, -2.0), head=-6.0)),
                  (0.9, dict(body=(6.0, 0.0, 2.0), lift=-0.4, neck=(10.0, 10.0, 6.0), head=8.0, grip=-8.0,
                             bundle=(-30.0, 0.0))),
                  (1.45, KO_DOWN), (KO_SEC, KO_DOWN)):
        pose(c, t, **kw)
    wings(c, 0.0, "rest")
    wings(c, 0.25, "half")
    wings(c, 0.9, "down")
    wings(c, 1.45, "flat")
    wings(c, KO_SEC, "flat")
    foot(c, 0.0)
    foot(c, KO_SEC)
    return c


def build_victory() -> ck.Clip:
    c = ck.Clip("victory", VICTORY_SEC)  # the full span, the cords raised, held; then folded back to rest
    held = dict(body=(-8.0, 0.0, 0.0), lift=0.06, neck=(-6.0, -6.0, -6.0), head=-10.0, tail=6.0)
    for t, kw in ((0.0, {}), (0.7, held), (1.6, dict(held, head=-6.0)), (VICTORY_SEC, {})):
        pose(c, t, **kw)
    wings(c, 0.0, "rest")
    wings(c, 0.45, "half", sway=(-6.0, -8.0))
    wings(c, 0.8, "raised")
    wings(c, 1.6, "raised", sway=(3.0, 5.0))
    wings(c, 1.9, "half", sway=(-4.0, -6.0))
    wings(c, VICTORY_SEC, "rest")
    foot(c, 0.0)
    foot(c, VICTORY_SEC)
    return c


RISE_START = dict(body=(16.0, 0.0, 0.0), lift=-0.34, neck=(22.0, 18.0, 12.0), head=18.0, tail=-6.0, grip=-6.0)


def build_rise() -> ck.Clip:
    c = ck.Clip("rise", RISE_SEC)  # from hunched and folded she lifts her head, opens her wings and stands
    for t, kw in ((0.0, RISE_START), (0.4, RISE_START),
                  (1.2, dict(body=(6.0, 0.0, 0.0), lift=-0.14, neck=(8.0, 6.0, 4.0), head=6.0)),
                  (1.8, dict(body=(-4.0, 0.0, 0.0), lift=0.03, neck=(-4.0, -4.0, -4.0), head=-8.0)),
                  (RISE_SEC, {})):
        pose(c, t, **kw)
    wings(c, 0.0, "fold")
    wings(c, 0.4, "fold")
    wings(c, 1.3, "half", sway=(-6.0, -10.0))
    wings(c, 1.8, "half", mix_to="rest", u=0.4, sway=(4.0, 6.0))
    wings(c, RISE_SEC, "rest")
    foot(c, 0.0)
    foot(c, RISE_SEC)
    return c


DISMISS_END = dict(body=(14.0, 0.0, 0.0), lift=-0.3, neck=(20.0, 16.0, 10.0), head=16.0, tail=-6.0, grip=-4.0)


def build_dismiss() -> ck.Clip:
    c = ck.Clip("dismiss", DISMISS_SEC)  # she folds and hunches down; it ends folded
    for t, kw in ((0.0, {}), (0.3, dict(body=(-2.0, 0.0, 0.0), neck=(-3.0, -3.0, -3.0), head=-4.0)),
                  (0.8, DISMISS_END), (DISMISS_SEC, DISMISS_END)):
        pose(c, t, **kw)
    wings(c, 0.0, "rest")
    wings(c, 0.8, "fold")
    wings(c, DISMISS_SEC, "fold")
    foot(c, 0.0)
    foot(c, DISMISS_SEC)
    return c


def build_special() -> ck.Clip:
    """Pass-Cord: she spreads to the full span and holds it, then sweeps both wings down and forward at once; the
    line of shining knots (battle VFX) runs across the field from the contact."""
    c = ck.Clip("special", SPECIAL_SEC)
    spread = dict(body=(-10.0, 0.0, 0.0), lift=0.06, neck=(-8.0, -6.0, -6.0), head=-10.0, tail=6.0)
    sweep = dict(body=(16.0, 0.0, 0.0), lift=-0.08, slide=0.06, neck=(10.0, 10.0, 6.0), head=8.0, tail=-4.0)
    for t, kw in ((0.0, {}), (0.8, spread), (1.15, dict(spread, body=(-12.0, 0.0, 0.0))),
                  (SPECIAL_CONTACT, sweep), (1.85, dict(sweep, body=(12.0, 0.0, 0.0))), (SPECIAL_SEC, {})):
        pose(c, t, **kw)
    wings(c, 0.0, "rest")
    wings(c, 0.4, "half", sway=(-6.0, -10.0))
    wings(c, 0.8, "full")
    wings(c, 1.15, "full", mix_to="raised", u=0.5, sway=(-4.0, -6.0))
    wings(c, SPECIAL_CONTACT, "down", sway=(16.0, 22.0))
    wings(c, 1.85, "half", sway=(-6.0, -8.0))
    wings(c, SPECIAL_SEC, "rest")
    foot(c, 0.0)
    foot(c, SPECIAL_SEC)
    return c


def build_idle_b() -> ck.Clip:
    c = ck.Clip("idle_b", IDLE_B_SEC)  # the fidget: a rouse of the wings, the cords shaken out, the bundle gripped
    for t, kw in ((0.0, {}), (0.3, dict(neck=(-2.0, -2.0, -2.0), head=-4.0, turn=8.0, grip=8.0)),
                  (0.7, dict(neck=(-1.0, -1.0, -1.0), head=-2.0, turn=-6.0, grip=4.0)), (IDLE_B_SEC, {})):
        pose(c, t, **kw)
    wings(c, 0.0, "rest")
    wings(c, 0.3, "rest", mix_to="half", u=0.3, sway=(-6.0, -10.0))
    wings(c, 0.55, "rest", sway=(6.0, 10.0))
    wings(c, 0.8, "rest", sway=(-3.0, -5.0))
    wings(c, IDLE_B_SEC, "rest")
    foot(c, 0.0)
    foot(c, IDLE_B_SEC)
    return c


RELEASE_SEC = 3.4  # M3-CRE-647: the held form's release (Ch20), its KO
RELEASE_AWAY = (0.0, 1.5, -0.5)  # where the release carries her (metres: up, and back away from the party)
RELEASE_HIGH = dict(body=(-10.0, 0.0, 0.0), lift=0.06, neck=(-8.0, -6.0, -6.0), head=-12.0, tail=6.0, grip=6.0)


def build_release() -> ck.Clip:
    """M3-CRE-647, the held form's KO (vowbound.md, the final fight: the believer who told the truth). She opens to
    her full span, the knotted cords spread to be read, the head raised, and holds there; then one slow down-stroke
    and she lifts off the water, up and back, gliding on the open wings, the keth bundle still held: at peace."""
    c = ck.Clip("release", RELEASE_SEC)
    for t, kw in ((0.0, {}), (0.5, dict(RELEASE_HIGH, body=(-4.0, 0.0, 0.0), lift=0.03, head=-6.0)),
                  (1.0, RELEASE_HIGH), (1.8, dict(RELEASE_HIGH, head=-14.0)),
                  (2.5, dict(RELEASE_HIGH, body=(-4.0, 0.0, 0.0), head=-6.0, tail=2.0)),
                  (RELEASE_SEC, dict(RELEASE_HIGH, body=(-6.0, 0.0, 0.0), head=-4.0, tail=4.0))):
        pose(c, t, **kw)
    wings(c, 0.0, "rest")
    wings(c, 0.5, "half", sway=(-6.0, -10.0))
    wings(c, 1.0, "full")
    wings(c, 1.8, "full", mix_to="raised", u=0.5, sway=(-3.0, -5.0))
    wings(c, 2.5, "down", sway=(12.0, 16.0))
    wings(c, RELEASE_SEC, "full", sway=(-2.0, -4.0))
    lx, ly, lz = RELEASE_AWAY
    for t, k in ((0.0, 0.0), (1.8, 0.0), (2.5, 0.4), (RELEASE_SEC, 1.0)):
        c.key("root", t, (0.0, 0.0, 0.0), (lx * k, ly * k, lz * k))
        hang = 0.08 * min(k / 0.4, 1.0)  # the planted talon comes up off the water with her
        foot(c, t, ly * k + hang, lz * k - hang * 0.5, 20.0 * hang / 0.08)
    return c


def authored_clips() -> list[ck.Clip]:
    return [build_idle(), build_ready(), build_attack(), build_cast(), build_hit(), build_hit("hit_b", -1.0, 1.35),
            build_defend(), build_ko(), build_victory(), build_rise(), build_dismiss(), build_special(),
            build_idle_b(), build_release()]


# Kept off the water where a clip lays them on it: the cords (lifted about the hand's chain), the bundle and the
# held left leg (in the KO).
GROUNDED_LIMBS = [
    ("cord_l1", 2, 1.0, 80.0), ("cord_r1", 2, -1.0, 80.0),
    ("cord_l0", 2, 1.0, 60.0), ("cord_r0", 2, -1.0, 60.0),
    ("bundle_0", 0, -1.0, 90.0),
    ("leg_l0", 0, -1.0, 40.0),
]


def build_clips(rig: ck.Rig, mesh: ck.Mesh) -> list[ck.Clip]:
    poser = grounding.Poser(rig, mesh)
    solved = [solve_legs(c, poser) for c in authored_clips()]
    return grounding.grounded(rig, mesh, solved, GROUNDED_LIMBS)


# ---------------------------------------------------------------------------------------------
# A numpy check (no Blender)
# ---------------------------------------------------------------------------------------------
def report(rig: ck.Rig, mesh: ck.Mesh, clips: list[ck.Clip]) -> None:
    rest = mesh.arrays()["pos"]
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}")
    print("parts: " + ", ".join(f"{k} {v}" for k, v in PARTS.items()))
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)}")
    rng = np.random.default_rng(SEED + 1)
    print("keth, leading cord first: " + ", ".join(str(n) for n in cord_numbers(rng)))
    poser = grounding.Poser(rig, mesh)
    for c in ck.with_variety(clips):
        lows = grounding.lowest(poser, c)
        highs, disp, span = [], [], []
        for t in grounding.frame_times(c):
            P = poser.vertices(poser.matrices(grounding.pose_at(c, poser.names, t)))
            highs.append(float(P[:, 1].max()))
            span.append(float(P[:, 0].max() - P[:, 0].min()))
            disp.append(float(np.linalg.norm(P - rest, axis=1).mean()))
        print(f"{c.name:8s} {c.length:.2f}s: y {min(lows):+.3f}..{max(highs):.3f}; span {min(span):.2f}.."
              f"{max(span):.2f}; peak {int(np.argmax(disp)) / ck.FPS:.2f}s")


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
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "hesk"})
    print(f"hesk: {info}")


if __name__ == "__main__":
    main()
