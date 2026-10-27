"""Kahre, the Forge-Crowned, Asha's Lightning Vowbound (M3-CRE-640): docs/kb/art/creatures/vowbound/kahre.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/kahre/build_kahre.py -- --out assets/creatures/kahre/kahre.glb

A towering hornbill-headed beast built like a smith: heavy forearms he walks on knuckle-down, a shoulder hump, and a
chest that is an anvil (a dark iron plate in the anvil's profile: the face under his throat, the horn jutting forward,
the waist below, with the bound-light star of an old strike on each flank). A mane of zig-zag spark-bolts of bound
light stands along the back of his neck, rigid geometry that moves only with the neck. A smith's cross-peen hammer is
fused into his casque (the keepsake, the one part of him that is not light).

**Grounded.** The origin is the water point under him and he stands on it. Every planted foot is solved onto the
water at every baked frame (`solve_legs`: a two-bone solve per leg in its own plane, the foot kept level), so the
body can rear, lunge and lie down while the feet stay where they stand. Every clip stays above the water.

Rig (22 bones): `root`, `body` (the hips), `chest`, `neck_0..2`, `head`, `jaw`, `arm_l0`, `arm_l1`, `hand_l` and the
right arm, `leg_l0`, `leg_l1`, `foot_l` and the right leg (+x is `l`), `tail_0`, `tail_1`.

`python3 build_kahre.py --report` prints the triangle count, per-slot counts and per-clip lows (numpy, no export).
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
    "volcanic_stone": "#3A3A3F", "storm_slate": "#3E4A57", "lacquer_black": "#1D1916",
    "coral_stone_weathered": "#B9AE98", "bone": "#E6DAC0", "brass": "#B08D57", "salt_glass": "#BFE6E0",
    "timber_weathered": "#7E6A55", "sand_cloth": "#C9B48E", "deep_teal_shadow": "#0E4A55",
}.items()}
HIDE = PAL["volcanic_stone"]
UNDER = ck.mix(PAL["volcanic_stone"], PAL["lacquer_black"], 0.55)
ASH = PAL["coral_stone_weathered"]
IRON = ck.mix(PAL["lacquer_black"], PAL["volcanic_stone"], 0.45)
HAMMER_IRON = ck.mix(PAL["storm_slate"], PAL["lacquer_black"], 0.45)
GLOW = 0.05  # the hide's faint inner light (emission mask)

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

# ---- the torso: control rings along the spine (z, centre y, half width, half height) ------------
TORSO = (
    (-0.84, 1.44, 0.06, 0.05), (-0.78, 1.45, 0.28, 0.26), (-0.56, 1.49, 0.41, 0.40), (-0.22, 1.60, 0.48, 0.47),
    (0.10, 1.76, 0.55, 0.54), (0.36, 1.92, 0.57, 0.55), (0.58, 1.98, 0.48, 0.48), (0.74, 1.92, 0.34, 0.36),
    (0.84, 1.86, 0.15, 0.18), (0.88, 1.84, 0.03, 0.04),
)
HUMP = (0.28, 0.28, 0.12)  # the shoulder hump: (z centre, z half length, extra height)
TORSO_RINGS, TORSO_SEGS = 34, 28

# ---- the head ----------------------------------------------------------------------------------
SKULL_C, SKULL_R = np.array([0.0, 2.66, 1.06]), (0.155, 0.165, 0.20)
EYE_AT = (0.128, 2.71, 1.15)
BILL = ((0.0, 2.64, 1.18), (0.0, 2.64, 1.50), (0.0, 2.50, 1.80), (0.0, 2.24, 1.95))
MANDIBLE = ((0.0, 2.55, 1.15), (0.0, 2.52, 1.45), (0.0, 2.40, 1.72), (0.0, 2.22, 1.90))
CASQUE = ((0.0, 2.80, 1.00), (0.0, 2.86, 1.22), (0.0, 2.84, 1.45), (0.0, 2.93, 1.62))
HANDLE_BASE = np.array([0.0, 2.84, 1.16])
HANDLE_RAKE = 10.0  # degrees back from upright: the face looks forward and leads every nose-down swing
HANDLE_LEN = 0.40
HAMMER_HEAD = (0.48, 0.085, 0.08)  # length (across the handle, in its plane), half height, half width

# ---- the anvil (on the chest) --------------------------------------------------------------------
ANVIL_FACE = (np.array([0.0, 1.86, 0.94]), (0.34, 0.045, 0.21))  # centre, half extents (x, y, z)
ANVIL_WAIST = ((0.0, 1.82, 0.88), (0.0, 1.30, 0.80), (0.30, 0.20), (0.15, 0.13))  # top, bottom, half x/z top, bottom
ANVIL_HORN = ((0.0, 1.86, 1.13), (0.0, 1.82, 1.32), (0.0, 1.75, 1.48))
STRIKE_AT = (1.58, 0.85)  # (y, z) of the struck star on each flank
STRIKE_RAYS = 7

TAIL_FEATHERS = ((0.0, 0.62, 70.0), (0.09, 0.58, 55.0), (-0.09, 0.58, -55.0), (0.17, 0.5, 35.0), (-0.17, 0.5, -35.0))
MANE_ROWS = ((0.0, 0.0), (0.075, 25.0), (-0.075, -25.0))  # (x offset, splay degrees)
MANE_N = 9

PARTS: dict[str, int] = {}


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


def loft(path, half_w, half_h, segs: int, up_hint=(0.0, 1.0, 0.0), squarish: float = 1.0):
    """A closed tube along `path` (K, 3) with an elliptical section: `half_w` along the frame's side, `half_h` along
    its up (scalars or (K,) arrays); both ends capped to a point. `squarish` < 1 squares the section off."""
    path = np.asarray(path, dtype=np.float64)
    K = len(path)
    hw = np.broadcast_to(np.asarray(half_w, dtype=np.float64), (K,))
    hh = np.broadcast_to(np.asarray(half_h, dtype=np.float64), (K,))
    tan, nrm, bin_ = ck.frames_along(path, up_hint)
    a = np.arange(segs) * (2.0 * math.pi / segs)
    ca, sa = np.cos(a), np.sin(a)
    ca = np.sign(ca) * np.abs(ca) ** squarish
    sa = np.sign(sa) * np.abs(sa) ** squarish
    rings = [path[k] + hh[k] * np.outer(ca, nrm[k]) + hw[k] * np.outer(sa, bin_[k]) for k in range(K)]
    P = np.vstack(rings + [path[:1] - tan[:1] * 0.002, path[-1:] + tan[-1:] * 0.002])
    T = ck.grid_tris(K, segs, True)
    s0, s1 = len(P) - 2, len(P) - 1
    caps = [(k, (k + 1) % segs, s0) for k in range(segs)]
    caps += [((K - 1) * segs + k, (K - 1) * segs + (k + 1) % segs, s1) for k in range(segs)]
    T = np.vstack([T, np.asarray(caps, dtype=np.int64)])
    return P, oriented(P, T, path)


def block(centre, half, R=None, rings: int = 8, segs: int = 16, power: float = 0.3):
    """A rounded box (a superellipsoid): `half` extents (x, y, z), turned by R."""
    P, T = ck.ellipsoid((0.0, 0.0, 0.0), (1.0, 1.0, 1.0), rings, segs)
    P = np.sign(P) * np.abs(P) ** power * np.asarray(half, dtype=np.float64)
    if R is not None:
        P = P @ np.asarray(R).T
    P = P + np.asarray(centre, dtype=np.float64)
    return P, oriented(P, T, np.asarray(centre, dtype=np.float64)[None])


def ribbon(points: np.ndarray, widths: np.ndarray, side: np.ndarray, normal: np.ndarray, thick: float):
    """A flat two-faced blade along `points` (K, 3), `widths` across `side`, the faces `thick` apart along `normal`."""
    K = len(points)
    L = points - side * widths[:, None] * 0.5
    R = points + side * widths[:, None] * 0.5
    faces = []
    for s in (1.0, -1.0):
        off = normal * thick * 0.5 * s
        faces.append(np.vstack([L + off, R + off]))
    P = np.vstack(faces)
    T = []
    for f, s in ((0, 1.0), (1, -1.0)):
        b = f * 2 * K
        for k in range(K - 1):
            t1 = (b + k, b + K + k, b + k + 1)
            t2 = (b + k + 1, b + K + k, b + K + k + 1)
            T += [t1, t2] if s > 0 else [t1[::-1], t2[::-1]]
    T = np.asarray(T, dtype=np.int64)
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    want = np.where(np.arange(len(T)) < len(T) // 2, 1.0, -1.0)[:, None] * normal
    bad = (fn * want).sum(axis=1) < 0
    T[bad] = T[bad][:, ::-1]
    return P, T


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
    return rig


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def hide_colour(P: np.ndarray, seed: int) -> np.ndarray:
    """volcanic_stone, darker underneath, mottled, ash-dusted on the upper surfaces."""
    mott = ck.smoothstep(-0.3, 0.4, ck.fbm(P * 2.2, seed))
    col = ck.mix(HIDE, PAL["storm_slate"], (0.35 * mott)[:, None])
    return col


def dust(col: np.ndarray, P: np.ndarray, N: np.ndarray, seed: int, amount: float = 0.25) -> np.ndarray:
    up = np.clip(N[:, 1], 0.0, 1.0)
    grain = ck.smoothstep(-0.1, 0.5, ck.fbm(P * 5.0, seed + 3))
    col = ck.mix(col, UNDER, (0.6 * np.clip(-N[:, 1], 0.0, 1.0))[:, None])
    return ck.mix(col, ASH, (amount * up ** 1.5 * grain)[:, None])


def torso(mesh: ck.Mesh, rig: ck.Rig) -> None:
    c = np.array(TORSO)
    s = np.linspace(0.0, 1.0, TORSO_RINGS)
    u = np.linspace(0.0, 1.0, len(c))
    z = np.interp(s, u, c[:, 0])
    y = np.interp(s, u, c[:, 1])
    hw = np.interp(s, u, c[:, 2])
    hh = np.interp(s, u, c[:, 3])
    path = np.column_stack([np.zeros_like(z), y, z])
    P, T = loft(path, hw, hh, TORSO_SEGS)
    # the shoulder hump: the upper half lifts around the shoulders
    hz, hl, hy = HUMP
    top = np.clip((P[:, 1] - np.interp(P[:, 2], z, y)) / np.maximum(np.interp(P[:, 2], z, hh), 1e-3), 0.0, 1.0)
    P[:, 1] += hy * np.exp(-((P[:, 2] - hz) / hl) ** 2) * top ** 1.5 * (1.0 - np.abs(P[:, 0]) / 0.7).clip(0.0, 1.0)
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    col = dust(hide_colour(P, SEED), P, N, SEED)
    skin = rig.blend("body", "chest", (0.0, 1.55, -0.1), (0.0, 1.85, 0.45))
    before = mesh.triangle_count
    ck.finish(mesh, P, T, "body", col, skin, wet=0.15, emission=GLOW, N=N)
    count("torso", mesh, before)


def neck(mesh: ck.Mesh, rig: ck.Rig) -> None:
    path = ck.bezier(((0.0, 1.80, 0.28),) + NECK_PATH[1:] + ((0.0, 2.68, 1.10),), 26)
    t = np.linspace(0.0, 1.0, len(path))
    hw = 0.36 * (1.0 - t) ** 1.3 + 0.14
    hh = 0.40 * (1.0 - t) ** 1.3 + 0.15
    P, T = loft(path, hw, hh, 20, up_hint=(0.0, 0.6, -0.8))
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    col = dust(hide_colour(P, SEED + 1), P, N, SEED + 1)
    pts = neck_points()
    chain = rig.chain(["chest", "neck_0", "neck_1", "neck_2", "head"],
                      np.vstack([[CHEST], pts, [pts[3] + (0.0, 0.03, 0.2)]]))
    before = mesh.triangle_count
    ck.finish(mesh, P, T, "body", col, chain, wet=0.15, emission=GLOW, N=N)
    count("neck", mesh, before)


def head(mesh: ck.Mesh, rig: ck.Rig) -> None:
    hb = rig.rigid("head")
    before = mesh.triangle_count
    P, T = ck.ellipsoid(SKULL_C, SKULL_R, 10, 18)
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    ck.finish(mesh, P, T, "body", dust(hide_colour(P, SEED + 2), P, N, SEED + 2, 0.15), hb, wet=0.15, emission=GLOW)
    count("skull", mesh, before)
    before = mesh.triangle_count
    for s in (1.0, -1.0):
        Pe, Te = ck.ellipsoid((s * EYE_AT[0], EYE_AT[1], EYE_AT[2]), (0.032, 0.03, 0.032), 6, 10)
        ck.finish(mesh, Pe, Te, "eye", PAL["deep_teal_shadow"], hb, wet=1.0, emission=0.6)
    count("eyes", mesh, before)
    # the bill: long, down-curved, laterally flat; bone going to brass toward the base
    before = mesh.triangle_count
    path = ck.bezier(BILL, 24)
    t = np.linspace(0.0, 1.0, len(path))
    P, T = loft(path, 0.075 * (1.0 - t) ** 0.9 + 0.008, 0.12 * (1.0 - t) ** 0.8 + 0.01, 14)
    k = np.clip((P[:, 2] - BILL[0][2]) / (BILL[-1][2] - BILL[0][2]), 0.0, 1.0)
    col = ck.mix(PAL["brass"], PAL["bone"], ck.smoothstep(0.0, 0.45, k)[:, None])
    col = ck.mix(col, ck.mix(PAL["bone"], PAL["volcanic_stone"], 0.5), ck.smoothstep(0.85, 1.0, k)[:, None])
    ck.finish(mesh, P, T, "beak", col, hb, wet=0.2)
    path = ck.bezier(MANDIBLE, 20)
    t = np.linspace(0.0, 1.0, len(path))
    P, T = loft(path, 0.06 * (1.0 - t) ** 0.9 + 0.007, 0.06 * (1.0 - t) ** 0.8 + 0.008, 12)
    k = np.clip((P[:, 2] - MANDIBLE[0][2]) / (MANDIBLE[-1][2] - MANDIBLE[0][2]), 0.0, 1.0)
    col = ck.mix(PAL["bone"], ck.mix(PAL["bone"], PAL["volcanic_stone"], 0.5), ck.smoothstep(0.85, 1.0, k)[:, None])
    ck.finish(mesh, P, T, "beak", col, rig.rigid("jaw"), wet=0.2)
    # the casque along the bill's top, upturned in front: brass
    path = ck.bezier(CASQUE, 18)
    t = np.linspace(0.0, 1.0, len(path))
    hh = 0.05 + 0.08 * np.sin(math.pi * np.clip(t * 1.15, 0.0, 1.0)) ** 0.7
    P, T = loft(path, 0.055 * (1.0 - 0.6 * t) + 0.01, hh, 14, squarish=0.8)
    tv = np.r_[np.repeat(t, 14), t[0], t[-1]]
    col = ck.mix(PAL["brass"], PAL["bone"], (0.25 * ck.smoothstep(0.7, 1.0, tv))[:, None])
    ck.finish(mesh, P, T, "beak", col, hb, wet=0.2)
    count("bill", mesh, before)


def hammer(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The keepsake: the handle grows out of the casque, raked back; the iron cross-peen head across its top."""
    hb = rig.rigid("head")
    r = math.radians(HANDLE_RAKE)
    up = np.array([0.0, math.cos(r), -math.sin(r)])
    fwd = np.array([0.0, math.sin(r), math.cos(r)])
    top = HANDLE_BASE + up * HANDLE_LEN
    before = mesh.triangle_count
    path = np.array([HANDLE_BASE - up * 0.08 + up * (HANDLE_LEN + 0.1) * f for f in np.linspace(0.0, 1.0, 10)])
    P, T = loft(path, 0.028, 0.034, 10, up_hint=(0.0, 0.0, 1.0))
    ck.finish(mesh, P, T, "hammer", PAL["timber_weathered"], hb, wet=0.1, cavity=0.2)
    for f in (0.12, 0.2, 0.28):  # the cloth wrap where it leaves the casque
        Pw, Tw = ck.ellipsoid(HANDLE_BASE + up * f, (0.038, 0.022, 0.044), 4, 10)
        Pw = (Pw - (HANDLE_BASE + up * f)) @ np.column_stack([(1.0, 0.0, 0.0), up, fwd]).T + (HANDLE_BASE + up * f)
        ck.finish(mesh, Pw, oriented(Pw, Tw, (HANDLE_BASE + up * f)[None]), "hammer", PAL["sand_cloth"], hb,
                  wet=0.1, cavity=0.3)
    L, h, w = HAMMER_HEAD
    R = np.column_stack([np.array([1.0, 0.0, 0.0]), up, fwd])  # local x, y (along the handle), z (the head's length)
    Pb, Tb = block(top + up * 0.0, (w, h, L * 0.36), R, rings=8, segs=16, power=0.25)
    face = top + fwd * (L * 0.36)
    Pf, Tf = block(face + fwd * 0.03, (w * 1.12, h * 1.12, 0.035), R, rings=6, segs=14, power=0.2)  # the face
    peen_c = top - fwd * (L * 0.36 + 0.06)
    Pp, Tp = block(peen_c, (w * 0.8, h * 0.35, 0.08), R, rings=6, segs=12, power=0.45)  # the wedge peen
    for Pq, Tq in ((Pb, Tb), (Pf, Tf), (Pp, Tp)):
        ck.finish(mesh, Pq, Tq, "hammer", HAMMER_IRON, hb, wet=0.1, cavity=0.25)
    count("hammer", mesh, before)


def anvil(mesh: ck.Mesh, rig: ck.Rig) -> None:
    cb = rig.rigid("chest")
    before = mesh.triangle_count
    c, half = ANVIL_FACE
    P, T = block(c, half, rings=10, segs=20, power=0.22)
    edge = ck.smoothstep(0.75, 1.0, np.maximum(np.abs(P[:, 0] - c[0]) / half[0], np.abs(P[:, 2] - c[2]) / half[2]))
    col = ck.mix(IRON, PAL["brass"], (0.55 * edge * (P[:, 1] > c[1] - 0.01))[:, None])
    ck.finish(mesh, P, T, "anvil", col, cb, wet=0.1, cavity=0.2)
    (y0, z0), (y1, z1) = (ANVIL_WAIST[0][1], ANVIL_WAIST[0][2]), (ANVIL_WAIST[1][1], ANVIL_WAIST[1][2])
    path = np.column_stack([np.zeros(12), np.linspace(y0, y1, 12), np.linspace(z0, z1, 12)])
    t = np.linspace(0.0, 1.0, 12)
    waist = 1.0 - 0.35 * np.sin(math.pi * t)  # pinched in the middle, like an anvil's waist
    hw = (ANVIL_WAIST[2][0] * (1.0 - t) + ANVIL_WAIST[3][0] * t) * waist
    hd = (ANVIL_WAIST[2][1] * (1.0 - t) + ANVIL_WAIST[3][1] * t) * waist
    P, T = loft(path, hw, hd, 20, up_hint=(0.0, 0.0, 1.0), squarish=0.45)
    ck.finish(mesh, P, T, "anvil", IRON, cb, wet=0.1, cavity=0.2)
    path = ck.bezier(ANVIL_HORN, 14)
    t = np.linspace(0.0, 1.0, len(path))
    P, T = loft(path, 0.13 * (1.0 - t) ** 1.2 + 0.012, 0.075 * (1.0 - t) ** 1.1 + 0.01, 14)
    col = ck.mix(IRON, PAL["brass"], ck.smoothstep(0.8, 1.0, (P[:, 2] - ANVIL_HORN[0][2]) / 0.35)[:, None] * 0.6)
    ck.finish(mesh, P, T, "anvil", col, cb, wet=0.1, cavity=0.2)
    count("anvil", mesh, before)
    # the struck star on each flank of the waist: a boss and jagged crack lines, raised, bound light
    rng = np.random.default_rng(SEED + 7)
    before = mesh.triangle_count
    y, z = STRIKE_AT
    tt = (y0 - y) / (y0 - y1)
    half_x = float((ANVIL_WAIST[2][0] * (1.0 - tt) + ANVIL_WAIST[3][0] * tt) * (1.0 - 0.35 * math.sin(math.pi * tt)))
    for s in (1.0, -1.0):
        n = np.array([s, 0.0, 0.0])
        c = np.array([s * (half_x + 0.006), y, z])
        Pb, Tb = ck.ellipsoid(c, (0.012, 0.028, 0.028), 4, 8)
        ck.finish(mesh, Pb, oriented(Pb, Tb, c[None]), "strike", PAL["salt_glass"], cb, emission=1.0)
        for k in range(STRIKE_RAYS):
            a = 2.0 * math.pi * k / STRIKE_RAYS + rng.uniform(-0.25, 0.25)
            ln = rng.uniform(0.09, 0.2)
            d = np.array([0.0, math.sin(a), math.cos(a)])
            perp = np.array([0.0, -d[2], d[1]])
            pts = np.array([c + d * ln * f + perp * (0.012 * ((-1) ** j) if 0 < j < 4 else 0.0)
                            for j, f in enumerate(np.linspace(0.15, 1.0, 5))])
            w = np.linspace(0.016, 0.003, len(pts))
            Pr, Tr = ribbon(pts, w, perp, n, 0.006)
            ck.finish(mesh, Pr, Tr, "strike", PAL["salt_glass"], cb, emission=1.0)
    count("strike", mesh, before)


def mane(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Zig-zag spark-bolts along the back of the neck and over the hump: flat blades in the neck's plane."""
    rng = np.random.default_rng(SEED)
    crest = ck.bezier(((0.0, 2.80, 0.98), (0.0, 2.66, 0.75), (0.0, 2.48, 0.50), (0.0, 2.44, 0.20)), 64)
    pts = neck_points()
    chain = rig.chain(["chest", "neck_0", "neck_1", "neck_2", "head"],
                      np.vstack([[CHEST], pts, [pts[3] + (0.0, 0.03, 0.2)]]))
    before = mesh.triangle_count
    for x0, splay in MANE_ROWS:
        n = MANE_N if x0 == 0.0 else MANE_N - 1
        for i in range(n):
            u = (i + (0.0 if x0 == 0.0 else 0.5)) / (MANE_N - 1)
            k = min(int(round(u * 63)), 63)
            base = crest[k] + np.array([x0, -0.03, 0.0])
            tan = crest[min(k + 1, 63)] - crest[max(k - 1, 0)]
            tan /= np.linalg.norm(tan)
            out = np.cross(tan, (1.0, 0.0, 0.0))  # away from the neck, up and back
            out = out if out[1] > 0 else -out
            out = out * 0.75 + tan * 0.35  # swept back along the crest
            out /= np.linalg.norm(out)
            side = np.cross(out, (1.0, 0.0, 0.0))
            R = ck.rot_z(-splay)  # the side rows splay outward
            out = R @ out
            side = R @ (side / np.linalg.norm(side))
            length = 0.3 + 0.32 * math.sin(math.pi * min(u * 1.2, 1.0)) ** 0.8 + rng.uniform(-0.03, 0.03)
            if x0 != 0.0:
                length *= 0.78
            normal = np.cross(out, side)
            f = np.linspace(0.0, 1.0, 6)
            kink = np.array([0.0, 1.0, -1.0, 1.0, -0.6, 0.0]) * 0.16 * length
            kink = kink + rng.uniform(-0.02, 0.02, 6) * length * np.array([0, 1, 1, 1, 1, 0])
            P = base + np.outer(f * length, out) + np.outer(kink, side)
            w = 0.08 * (1.0 - f) ** 0.9 + 0.008
            Pr, Tr = ribbon(P, w, side, normal, 0.01)
            tip = np.clip(((Pr - base) @ out) / length, 0.0, 1.0)
            ck.finish(mesh, Pr, Tr, "mane", PAL["salt_glass"], chain, wet=0.1, emission=0.75 + 0.25 * tip)
    count("mane", mesh, before)


def limb(mesh: ck.Mesh, rig: ck.Rig, leg: str) -> None:
    bones, _x, _J, _p = LEGS[leg]
    j = leg_joints(leg)
    fore = leg.startswith("fore")
    path = np.vstack([ck.bezier([j[0], j[0] * 0.5 + j[1] * 0.5 + (0, 0, 0.04 if not fore else -0.03), j[1]], 10)[:-1],
                      ck.bezier([j[1], j[1] * 0.5 + j[2] * 0.5 + (0, 0, -0.03 if not fore else 0.03), j[2]], 10)])
    t = np.linspace(0.0, 1.0, len(path))
    r0, r1, r2 = (0.27, 0.17, 0.13) if fore else (0.3, 0.15, 0.1)
    rad = np.interp(t, (0.0, 0.5, 1.0), (r0, r1, r2))
    P, T = loft(path, rad, rad * 1.08, 14, up_hint=(1.0, 0.0, 0.0))
    N = ck.weld_normals(P, ck.vertex_normals(P, T))
    col = dust(hide_colour(P, SEED + 11), P, N, SEED + 11, 0.3 if fore else 0.15)
    before = mesh.triangle_count
    ck.finish(mesh, P, T, "body", col, rig.chain(list(bones[:2]), j[:3]), wet=0.15, emission=GLOW, N=N)
    count("limbs", mesh, before)
    fb = rig.rigid(bones[2])
    before = mesh.triangle_count
    x = float(j[0, 0])
    if fore:
        # the fist, knuckles down: a heavy block with three knuckle plates and short claws in front
        c = np.array([x, 0.15, 0.69])
        Pf, Tf = block(c, (0.15, 0.15, 0.16), rings=10, segs=16, power=0.55)
        Nf = ck.weld_normals(Pf, ck.vertex_normals(Pf, Tf))
        ck.finish(mesh, Pf, Tf, "body", dust(hide_colour(Pf, SEED + 12), Pf, Nf, SEED + 12, 0.3), fb, wet=0.15,
                  emission=GLOW, N=Nf)
        for k in (-1, 0, 1):
            kc = np.array([x + k * 0.085, 0.07, 0.81])
            Pk, Tk = ck.ellipsoid(kc, (0.045, 0.07, 0.05), 5, 8)
            ck.finish(mesh, Pk, oriented(Pk, Tk, kc[None]), "beak", ck.mix(PAL["bone"], ASH, 0.5), fb, cavity=0.3)
            claw = ck.bezier([(x + k * 0.085, 0.055, 0.85), (x + k * 0.085, 0.04, 0.91), (x + k * 0.085, 0.012, 0.93)],
                             6)
            Pc, Tc = loft(claw, np.linspace(0.022, 0.004, 6), np.linspace(0.02, 0.004, 6), 6)
            ck.finish(mesh, Pc, Tc, "beak", PAL["bone"], fb, wet=0.2)
    else:
        # the hornbill's foot: a pad under the ankle, three toes forward and one back, claws
        c = np.array([x, 0.075, -0.46])
        Pf, Tf = ck.ellipsoid(c, (0.1, 0.075, 0.12), 8, 12)
        ck.finish(mesh, Pf, Tf, "body", hide_colour(Pf, SEED + 13), fb, wet=0.15, emission=GLOW)
        for ang, ln in ((-28.0, 0.32), (0.0, 0.38), (28.0, 0.32), (180.0, 0.14)):
            d = ck.rot_y(ang) @ np.array([0.0, 0.0, 1.0])
            toe = np.array([c + d * ln * f + (0.0, -0.02 * f, 0.0) for f in np.linspace(0.0, 1.0, 8)])
            r = np.linspace(0.05, 0.025, 8)
            toe[:, 1] = np.maximum(toe[:, 1], r * 1.0 + 0.0)
            Pt, Tt = loft(toe, r, r, 8)
            ck.finish(mesh, Pt, Tt, "body", ck.mix(UNDER, ASH, 0.15), fb, wet=0.15, cavity=0.2)
            tip = toe[-1]
            claw = ck.bezier([tip, tip + d * 0.05 + (0, 0.0, 0), tip + d * 0.08 + (0, -0.015, 0)], 5)
            claw[:, 1] = np.maximum(claw[:, 1], 0.006)
            Pc, Tc = loft(claw, np.linspace(0.02, 0.004, 5), np.linspace(0.018, 0.004, 5), 6)
            ck.finish(mesh, Pc, Tc, "beak", PAL["bone"], fb, wet=0.2)
    count("feet", mesh, before)


def tail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Five long hornbill tail feathers from the rump, hanging down behind him (so they stay inside the frame's
    right edge at the default camera), fanned, banded pale near the tips."""
    chain = rig.chain(["tail_0", "tail_1"], TAIL_PTS)
    before = mesh.triangle_count
    for sx, ln, roll in TAIL_FEATHERS:
        a = TAIL_PTS[0] + (sx * 0.3, 0.0, 0.04)
        pts = ck.bezier([a, a + (sx * 0.5, -0.1, -0.1), a + (sx * 0.8, -0.32 * ln / 0.6, -0.16),
                         a + (sx * 0.9, -ln, -0.14)], 10)
        f = np.linspace(0.0, 1.0, len(pts))
        w = 0.11 * np.sin(math.pi * np.clip(0.15 + f * 0.9, 0.0, 1.0)) ** 0.5 + 0.01
        tan = np.gradient(pts, axis=0)
        tan /= np.linalg.norm(tan, axis=1, keepdims=True)
        m = len(pts) // 2
        side = np.cross(tan[m], (0.0, 1.0, 0.0))
        side /= np.linalg.norm(side)
        r = math.radians(roll)  # turned about the feather's own length, so the fan shows from the side
        side = side * math.cos(r) + np.cross(tan[m], side) * math.sin(r)
        normal = np.cross(side, tan[m])
        P, T = ribbon(pts, w, side, normal, 0.012)
        band = np.exp(-((np.tile(f, 4) - 0.8) / 0.07) ** 2)
        col = ck.mix(HIDE, PAL["bone"], (0.85 * band)[:, None])
        ck.finish(mesh, P, T, "body", col, chain, wet=0.1, emission=GLOW)
    count("tail", mesh, before)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    PARTS.clear()
    mesh = ck.Mesh("kahre")
    torso(mesh, rig)
    neck(mesh, rig)
    head(mesh, rig)
    hammer(mesh, rig)
    anvil(mesh, rig)
    mane(mesh, rig)
    for leg in LEGS:
        limb(mesh, rig, leg)
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
BLOW = dict(body=(20.0, 0.0, 0.0), lift=-0.4, slide=0.12, chest=10.0, neck=(35.0, 30.0, 15.0), head=20.0, tail=-8.0)


def build_special() -> ck.Clip:
    """Last Strike: he rears with the hammer high over his back, holds, then the whole body comes down into one
    overhead blow, the forearms planting and the hammer's face landing on the water in front of him."""
    c = ck.Clip("special", SPECIAL_SEC)
    for t, kw in ((0.0, {}), (0.9, REAR), (1.25, dict(REAR, head=-34.0, neck=(-9.0, -14.0, -16.0))),
                  (SPECIAL_CONTACT, BLOW), (1.95, dict(BLOW, head=17.0, lift=-0.37)), (SPECIAL_SEC, {})):
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


def authored_clips() -> list[ck.Clip]:
    return [build_idle(), build_ready(), build_attack(), build_cast(), build_hit(), build_hit("hit_b", -1.0, 1.35),
            build_defend(), build_ko(), build_victory(), build_rise(), build_dismiss(), build_special(),
            build_idle_b()]


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
