"""Ethren, the Level Saint, Asha's Glimmer Vowbound (M3-CRE-644): docs/kb/art/creatures/vowbound/ethren.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/ethren/build_ethren.py -- --out assets/creatures/ethren/ethren.glb

A winged shrine-figure of lacquer and silk, 3.0 m to the top of his halo. Since the M4-CRB-008 polish: a layered robe
(a red silk under-robe in sixteen hanging folds with an uneven, weighted hem; over it three lacquered panels, parted in
front and overlapping at his sides, lined in red silk; a red lacquer belt with a knot and two silk tails), a two-layer
lacquered mantle over the shoulders, wide hanging sleeves (black silk lined in red, the bag sewn shut in front, the
opening turned back round the wrist) and lacquer hands (three-jointed fingers, a thumb, gilded nails). Under the mantle
the cuirass with its split red breastplate. When he kneels the hips sink furthest and the cloth settles onto itself
(it is skinned by height to `body`, `robe_1` and `robe_2`, the old bells' bones). Black and deep-red lacquer carry the
bulk; gold leaf is only on the edges (panel rims and hems, the mantle's hems, the cuffs, the halo's lip, the screens'
rims, the nails and the veil's border), so he holds palette.json's 5%-of-frame gold budget. His bound light is inside
and shows only at seams (the breastplate's split, deep in the cuffs, the screens' hinge lines) and in the halo:
a thin bowl floating clear of the head, open at its centre, brightest at the hollow and falling off to a lacquer rim.

A still, rigid veil covers the whole face and falls to the chest: its own mesh (`ethren_veil`) on its own bone
(`veil`), which no clip keys, so cinematics can drop it later (Ch20's veil-fall is the characters track's). No face
is modelled. Four folded wings of lacquer screen leaves (two leaves each, hinged with knuckles and a line of light;
each leaf two half-panels at a shallow V, rimmed in gold, worn at the edges to the red ground, fields set in them)
hang close behind him like a closed screen and open only in `ready`, `cast`, `special` and `victory`. A plain copper
ring (laterite toward tortoiseshell, rough, never lit) sits on the left ring finger: the keepsake.

**Built hovering.** The origin is the water point under him and the rest pose floats there: the sole line (the
feet, not modelled under the robe) 0.2 m up, the robe's hem 0.1 m. The stand-in needs no `hover`. Every clip stays
above the water.

Rig (27 figure bones): `root`, `body` (the hips), `spine_0..2`, `neck`, `head`, `veil`, `halo`, `robe_1`, `robe_2` (the
robe's shin and hem), `arm_l0`, `arm_l1`, `hand_l`, `finger_l0` (index and middle), `finger_l1` (ring and little, the
ring's), `arm_r0`, `arm_r1`, `hand_r`, and `wing_{li,lo,ri,ro}_{0,1}` (+x is `l`; `i` the inner pair, `o` the outer;
`_0` the upper leaf, `_1` the lower). M4-CRB-008 adds two unweighted VFX anchors last (29 bones): `vfx_core` (the
breastplate) and `vfx_keepsake` (the ring), and the clips `stop` (Hold the Hour) and `ward` (the lacquer screen);
every clip is played from idle's first frame.

`python3 build_ethren.py --report` prints the triangle count, per-slot counts and per-clip lows (numpy, no export).
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

SEED = 6440
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "lacquer_red_deep": "#7A1712", "gold_leaf": "#D4A437", "gauze_white": "#EBE7DF",
    "laterite": "#A8573A", "tortoiseshell": "#6B3A1E", "glimmer_bound": "#4FB3B0",
}.items()}
RING_COL = ck.mix(PAL["laterite"], PAL["tortoiseshell"], 0.35)  # copper: no copper swatch, the nearest unlit warm metal
SEAM_COL = PAL["glimmer_bound"]  # M4-CRB-008: the light's own colour under its emission (gauze_white read white)
# M4-CRB-008, the battle-camera audit: from the party side he read as a stack of plain cones under a white lampshade
# and a blank white plate. These carry the shrine-figure's craft without a new slot.
VEIL_COLS = 25  # stations across the veil (from 17), for its pleats
VEIL_PLEATS = 6.0  # soft folds across its width
VEIL_PLEAT_M = (0.002, 0.009)  # their depth at the crown band and at the hem
VEIL_SHADE = (0.16, 0.55)  # how far the thin gauze darkens toward the lacquer head behind it (everywhere; over the
# face at most)
# The Act II polish (the Lead's view: a lampshade robe, mannequin arms, a plate halo, door-slab wings): cloth, sleeves,
# hands, a halo of light and screen leaves. `silk` (an eighth slot) gives the cloth a sheen the glossy lacquer cannot.
SILK_BLACK = ck.mix(PAL["lacquer_black"], PAL["lacquer_red_deep"], 0.3)  # an oxblood black, so the sheen shows
FOLD_MEAN = 4.0 / math.pi - 1.0  # fold()'s mean, taken out so folds neither swell nor shrink the robe
ROBE_WAIST, ROBE_TOP = 1.38, 1.40  # the robe's profile is measured from the waist; its cloth starts under the belt
ROBE_R = (0.215, 0.59)  # its half-width at the waist and at the hem
ROBE_FLARE = 1.25  # the flare gathers toward the hem (the cloth's weight)
ROBE_FWD = 0.08  # carried forward at the hem, clear of the folded wings
ROBE_SKIN_Y = (1.22, 0.80, 0.34)  # the hips' cloth, robe_1's, robe_2's: blended between
UNDER_COLS = 48
UNDER_FOLDS = 16
UNDER_FOLD_M = 0.034  # the silk's fold depth at the hem
OVER_FOLDS = 11
OVER_FOLD_M = 0.021
OPEN_DEG = (5.0, 26.0)  # the front opening's half-angle at the belt and at the hem
FRONT_TO_DEG = 118.0  # the front panels reach round to here; the back panel from BACK_DEG
BACK_DEG = (98.0, 262.0)
OVER_HEM = (0.34, 0.28, 0.2)  # the panels' hems: at the front, at the sides, at the back (the back is longest)
BELT = (1.32, 1.43)
BELT_OUT = 0.03
SASH_DEG = 34.0  # the knot at the left hip, toward the front
SASH_TAILS = ((4.0, 0.78, 0.07), (-7.0, 0.66, 0.06))  # (drift in degrees, lowest point, width)
MANTLE_TOP = 2.17
MANTLE_RX = (0.13, 0.47)
MANTLE_RZ = (0.118, 0.225)
MANTLE_DROP = 0.29
MANTLE_UNDER = 1.2  # the black under-layer hangs past the red one
MANTLE_OPEN_DEG = 50.0  # parted at the breast, clear of the veil
MANTLE_COLS = 34
MANTLE_FOLDS = 14
MANTLE_FOLD = 0.024
SLEEVE_FORE = ((0.3, 0.45, 0.108), (0.55, 0.8, 0.118), (0.75, 1.0, 0.124), (0.87, 0.92, 0.122))
SLEEVE_FRONT = ((0.065, 0.55, 0.11), (0.053, 0.3, 0.1), (0.045, 0.2, 0.094), (0.012, 0.03, 0.08), (0.0, 0.0, 0.077))
SLEEVE_BAG = 0.22  # how far the open sleeve hangs under the forearm at the cuff
SLEEVE_SEGS = 20
SLEEVE_FOLDS = 6
SLEEVE_FOLD = 0.07
SLEEVE_CUFF = 0.03  # the opening this far past the wrist, so only the hand shows
PALM_LEN = 0.088
HAND_SCALE = 1.2  # he stands 1.3 times a man: the hands to match (the palm's length is the rig's)
PALM = [(-0.025, 0.027, 0.016), (0.0, 0.029, 0.016), (0.03, 0.037, 0.0155), (0.06, 0.042, 0.0135),
        (0.08, 0.043, 0.0115), (PALM_LEN, 0.04, 0.0095)]  # (along, half-width, half-thickness), before the scale
FINGER_X = (-0.027, -0.009, 0.009, 0.026)  # index .. little, from the thumb's side
FINGER_LEN = ((0.035, 0.022, 0.017), (0.039, 0.024, 0.019), (0.037, 0.023, 0.018), (0.028, 0.018, 0.015))
FINGER_BEND = (7.0, 13.0, 10.0)  # the relaxed curl at each joint
FINGER_SPLAY = (-4.0, 0.0, 4.0, 9.0)
FINGER_R_SCALE = (1.0, 1.02, 0.97, 0.86)
RING_ALONG = 0.017  # the ring past the knuckle
HALO_RINGS = (0.13, 0.145, 0.2, 0.27, 0.34, 0.40, 0.45)  # the hollow's edge .. the rim's start .. the lip
HALO_RIM = 0.40
HALO_GLOW = (0.1, 1.0)  # the lit face's emission at the rim and at the hollow's edge
HALO_SEGS = 40
LEAF_COLS, LEAF_ROWS = 4, 7  # per half-panel
LEAF_ZIG = 0.035  # how far each leaf's middle hinge stands out of its edges (the halves' V)
LEAF_HALF_GAP = 0.012  # the hinge line between the halves (fraction of the width, each side)
LEAF_WEAR_M = 0.03
LEAF_FIELDS = ((0.09, 0.47), (0.53, 0.91))  # two fields per leaf, a rail between (fractions down the leaf)
HINGE_U = (0.25, 0.75)
LEAF_FIELD_IN = ck.mix(PAL["lacquer_red_deep"], PAL["lacquer_black"], 0.45)  # the inner face's fields: a darker red

# ---- the figure (metres, Godot axes, facing +z) -----------------------------------------------
SOLE = 0.2  # the hover: the feet's line under the robe
HEM = 0.1  # the robe's hem
HIP = 1.30
SPINE = [HIP, 1.50, 1.72, 1.95, 2.12]  # body, spine_0, spine_1, spine_2 spans
NECK_TOP = 2.24
HEAD_C = np.array([0.0, 2.33, 0.01])
HEAD_R = (0.105, 0.135, 0.12)
HEAD_TOP = 2.47
CROWN_C = np.array([0.0, 2.425, 0.012])  # the crown cap over the veil's top edge (M4-CRB-008)
CROWN_R = (0.118, 0.06, 0.132)
HALO_C = np.array([0.0, 2.55, -0.235])  # the bowl's rim plane centre, floating clear of the head
HALO_R = 0.45  # 0.9 m across: its top is 3.0 m
HALO_DEPTH = 0.11
HALO_TH = 0.006
GOLD_BAND = 0.014  # the gold rim's width on a face
TH = 0.014  # lacquer plate thickness

# the cuirass: (y, half-width, half-depth, depth centre)
CUIRASS = [(1.30, 0.19, 0.15, 0.0), (1.42, 0.205, 0.16, 0.0), (1.55, 0.225, 0.172, 0.005), (1.70, 0.25, 0.185, 0.01),
           (1.84, 0.265, 0.19, 0.01), (1.95, 0.262, 0.182, 0.0), (2.03, 0.238, 0.16, -0.005), (2.08, 0.19, 0.13, -0.01),
           (2.115, 0.12, 0.095, -0.01), (2.125, 0.09, 0.08, -0.01)]
DEPTH_RATIO = 0.82  # a bell's depth to its width
# the old nested bells' spans: only robe_1's and robe_2's rest positions use them now (the robe is cloth)
BELLS = [(1.38, 0.86, 0.215, 0.26, 0.01), (0.98, 0.48, 0.36, 0.26, 0.02), (0.60, HEM, 0.50, 0.18, 0.08)]
SHOULDER_L = np.array([0.30, 2.02, -0.02])
ELBOW_L = np.array([0.335, 1.645, 0.0])
WRIST_L = np.array([0.255, 1.60, 0.33])
HAND_LEN = 0.21
# the wings: per leaf pair, its hinge (x, z) at the pivot, the leaf's angle off the back plane, width
PIVOT_Y = 2.08
LEAF_TOP = 2.16
LEAF_LEN = 0.98  # each of the two leaves
LEAF_GAP = 0.035
LEAF_W = 0.30
LEAF_TH = 0.012
LEAN_DEG = 6.0  # the folded leaves lean back so they clear the robe's flare
WINGS = {"i": (0.05, -0.27, 35.0), "o": (0.11, -0.33, 30.0)}  # inner pair, outer pair (behind it)
# M4-CRB-008: the VFX anchors (unweighted): `vfx_core` at the breastplate's split, where the light inside shows most
VFX_CORE = np.array([0.0, 1.76, 0.20])

PARTS: dict[str, int] = {}


def count(name: str, mesh: ck.Mesh, before: int) -> None:
    PARTS[name] = PARTS.get(name, 0) + mesh.triangle_count - before


def orient(P: np.ndarray, T: np.ndarray, want: np.ndarray) -> np.ndarray:
    """Flips triangles whose winding disagrees with the per-vertex intended normals `want`."""
    T = np.asarray(T, dtype=np.int64).copy()
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    bad = (fn * want[T].mean(axis=1)).sum(axis=1) < 0
    T[bad] = T[bad][:, ::-1]
    return T


def unit(v) -> np.ndarray:
    v = np.asarray(v, dtype=np.float64)
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)


def put(mesh: ck.Mesh, name: str, P, T, slot: str, color, bones, want=None, **kw) -> None:
    """Adds a part (oriented by `want` when given) and counts it under `name`."""
    P = np.asarray(P, dtype=np.float64)
    T = np.asarray(T, dtype=np.int64)
    if want is not None:
        T = orient(P, T, np.broadcast_to(np.asarray(want, dtype=np.float64), P.shape))
    before = mesh.triangle_count
    ck.finish(mesh, P, T, slot, color, bones, **kw)
    count(name, mesh, before)


def subset(P: np.ndarray, T: np.ndarray, extra=()):
    """The vertices T uses, remapped; `extra` arrays (per vertex) are cut the same way."""
    used = np.unique(T)
    remap = np.full(len(P), -1, dtype=np.int64)
    remap[used] = np.arange(len(used))
    return (P[used], remap[T]) + tuple(np.asarray(e)[used] for e in extra)


# ---------------------------------------------------------------------------------------------
# A slab: a grid surface given its thickness, its border cells and walls in gold
# ---------------------------------------------------------------------------------------------
def slab(G: np.ndarray, N: np.ndarray, th: float, gold: str = "lrtb", wrap: bool = False, open_first: bool = False):
    """`G` (rows, cols, 3) a surface grid whose first and last rows and columns are its border bands, `N` its normals.
    Returns {'face': (P, T, want), 'gold': (P, T, want), 'back': (P, T, want)}: the front face's field, the gold
    (the front face's border bands on the sides in `gold`, 'l' first column, 'r' last, 't' last row, 'b' first, and
    the walls), and the back face. `wrap`: the columns close round (no l/r border or wall). `open_first`: no wall
    along the first row (an edge tucked out of sight: under the belt, the collar or the mantle)."""
    R, C = G.shape[:2]
    front = (G + N * th * 0.5).reshape(-1, 3)
    back = (G - N * th * 0.5).reshape(-1, 3)
    Nf = N.reshape(-1, 3)
    T = ck.grid_tris(R, C, wrap)
    cols = C if wrap else C - 1
    cell_r = np.repeat(np.arange(R - 1), cols * 2)
    cell_c = np.tile(np.repeat(np.arange(cols), 2), R - 1)
    border = np.zeros(len(T), dtype=bool)
    if "b" in gold:
        border |= cell_r == 0
    if "t" in gold:
        border |= cell_r == R - 2
    if not wrap:
        if "l" in gold:
            border |= cell_c == 0
        if "r" in gold:
            border |= cell_c == C - 2
    out = {"face": (front, T[~border], Nf), "back": (back, T, -Nf)}
    # walls round the perimeter, front edge to back edge
    ring = perimeter(R, C, wrap)
    wallP, wallT, wallN = [], [], []
    cen = G.reshape(-1, 3).mean(axis=0)
    if open_first and wrap:
        ring = ring[1:]
    for loop in ring:
        k = len(loop)
        a, b = front[loop], back[loop]
        P = np.vstack([a, b])
        n_seg = k if wrap else k - 1
        tris = []
        for i in range(C - 1 if (open_first and not wrap) else 0, n_seg):
            j = (i + 1) % k
            tris += [(i, j, k + i), (j, k + j, k + i)]
        out_dir = G.reshape(-1, 3)[loop] - cen
        out_dir = out_dir - (out_dir * Nf[loop]).sum(axis=1, keepdims=True) * Nf[loop]
        wallP.append(P)
        wallT.append(np.asarray(tris, dtype=np.int64))
        wallN.append(np.vstack([out_dir, out_dir]))
    gP = [front]
    gT = [T[border]]
    gN = [Nf]
    base = len(front)
    for P, Tw, Nw in zip(wallP, wallT, wallN):
        gP.append(P)
        gT.append(Tw + base)
        gN.append(Nw)
        base += len(P)
    out["gold"] = (np.vstack(gP), np.vstack(gT) if gT else np.zeros((0, 3), dtype=np.int64), np.vstack(gN))
    return out


def perimeter(R: int, C: int, wrap: bool) -> list[list[int]]:
    if wrap:
        return [list(range(C)), [(R - 1) * C + c for c in range(C)]]
    loop = [c for c in range(C)] + [r * C + C - 1 for r in range(1, R)] + \
        [(R - 1) * C + c for c in range(C - 2, -1, -1)] + [r * C for r in range(R - 2, 0, -1)]
    return [loop + [loop[0]]]


def put_slab(mesh: ck.Mesh, name: str, parts: dict, field_slot: str, field_col, back_col, bones,
             back_slot: str | None = None) -> None:
    P, T, W = parts["face"]
    if len(T):
        Ps, Ts, Ws = subset(P, T, (W,))[0:3]
        cols = field_col(Ps) if callable(field_col) else field_col
        put(mesh, name, Ps, Ts, field_slot, cols, bones, want=Ws)
    P, T, W = parts["back"]
    Ps, Ts, Ws = subset(P, T, (W,))[0:3]
    put(mesh, name, Ps, Ts, back_slot or field_slot, back_col, bones, want=Ws)
    P, T, W = parts["gold"]
    if len(T):
        Ps, Ts, Ws = subset(P, T, (W,))[0:3]
        put(mesh, "gold", Ps, Ts, "gold", PAL["gold_leaf"], bones, want=Ws)


def bands(a: float, b: float, n: int, band: float) -> np.ndarray:
    """Stations from a to b: a border band of `band` at each end and n - 1 even steps between."""
    inner = np.linspace(a + band, b - band, n)
    return np.concatenate([[a], inner, [b]])


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def mirror(p) -> np.ndarray:
    return np.asarray(p, dtype=np.float64) * np.array([-1.0, 1.0, 1.0])


def hand_tip(side: float) -> np.ndarray:
    w = WRIST_L if side > 0 else mirror(WRIST_L)
    return w + np.array([0.0, -0.02, HAND_LEN])


def leaf_frame(tag: str):
    """A wing's (pivot, hinge top, down, across, normal) at rest: the leaf's hinge edge leans back LEAN_DEG; across
    runs outward and back at the pair's angle off the back plane; the normal faces out and back."""
    side = 1.0 if tag[0] == "l" else -1.0
    x0, z0, ang = WINGS[tag[1]]
    down = np.array([0.0, -math.cos(math.radians(LEAN_DEG)), -math.sin(math.radians(LEAN_DEG))])
    across = np.array([side * math.cos(math.radians(ang)), 0.0, -math.sin(math.radians(ang))])
    across = unit(across - down * (across @ down))
    normal = unit(np.cross(down, across) * side)
    if normal[2] > 0:
        normal = -normal
    top = np.array([side * x0, LEAF_TOP, z0])
    pivot = top + down * (LEAF_TOP - PIVOT_Y) / math.cos(math.radians(LEAN_DEG))
    return pivot, top, down, across, normal


def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    rig.add("body", (0, SPINE[0], 0), (0, SPINE[1], 0), "root")
    parent = "body"
    for k in range(3):
        rig.add(f"spine_{k}", (0, SPINE[k + 1], 0), (0, SPINE[k + 2], 0), parent)
        parent = f"spine_{k}"
    rig.add("neck", (0, SPINE[-1], -0.01), (0, NECK_TOP, 0.0), "spine_2")
    rig.add("head", (0, NECK_TOP, 0.0), (0, HEAD_TOP, 0.01), "neck")
    rig.add("veil", (0, 2.30, 0.12), (0, 2.0, 0.2), "head")
    rig.add("halo", tuple(HALO_C), tuple(HALO_C + (0, HALO_R, 0)), "head")
    rig.add("robe_1", (0, BELLS[1][0], 0), (0, BELLS[1][1], 0), "root")
    rig.add("robe_2", (0, BELLS[2][0], 0), (0, BELLS[2][1], 0), "root")
    for side, tag in ((1.0, "l"), (-1.0, "r")):
        s, e, w = (SHOULDER_L, ELBOW_L, WRIST_L) if side > 0 else (mirror(SHOULDER_L), mirror(ELBOW_L), mirror(WRIST_L))
        rig.add(f"arm_{tag}0", s, e, "spine_2")
        rig.add(f"arm_{tag}1", e, w, f"arm_{tag}0")
        knuckle = w + np.array([0.0, -0.008, 0.09])
        rig.add(f"hand_{tag}", w, knuckle, f"arm_{tag}1")
        if tag == "l":
            rig.add("finger_l0", knuckle + (-0.02, 0, 0), hand_tip(1.0) + (-0.02, 0, 0), "hand_l")
            rig.add("finger_l1", knuckle + (0.02, 0, 0), hand_tip(1.0) + (0.02, 0, 0), "hand_l")
    for tag in ("li", "lo", "ri", "ro"):
        pivot, top, down, across, _ = leaf_frame(tag)
        joint = top + down * LEAF_LEN
        rig.add(f"wing_{tag}_0", pivot, joint, "spine_2")
        rig.add(f"wing_{tag}_1", joint + down * LEAF_GAP, joint + down * (LEAF_GAP + LEAF_LEN), f"wing_{tag}_0")
    # M4-CRB-008: the VFX anchors, unweighted (no vertex is skinned to them; added last, so every other bone keeps its
    # index): `vfx_core` at the breastplate on spine_2, `vfx_keepsake` at the copper ring on finger_l1
    rig.add("vfx_core", VFX_CORE, VFX_CORE + (0.0, 0.2, 0.0), "spine_2")
    rc = ring_centre()
    rig.add("vfx_keepsake", rc, rc + (0.0, 0.0, 0.05), "finger_l1")
    return rig


def ring_centre() -> np.ndarray:
    """Where the ring sits: on the left ring finger's first joint, a little past the knuckle."""
    pts, _ = finger_path(1.0, 2)
    return pts[0] + unit(pts[1] - pts[0]) * RING_ALONG


def torso_skin(rig: ck.Rig):
    return rig.chain(["body", "spine_0", "spine_1", "spine_2"], [(0, y, 0) for y in SPINE])


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def section(table, y: float):
    ys = np.array([r[0] for r in table])
    return tuple(float(np.interp(y, ys, np.array([r[k] for r in table]))) for k in (1, 2, 3))


def ell(table, phi, y, off=0.0):
    """A point (and its outward normal) on a loft at angle phi (0 front, + toward +x) and height y, `off` out."""
    rx, rz, zc = section(table, y)
    n = unit(np.array([math.sin(phi) / rx, 0.0, math.cos(phi) / rz]))
    return np.array([rx * math.sin(phi), y, zc + rz * math.cos(phi)]) + n * off, n


def loft_grid(table, phis, ys, off=0.0):
    G = np.zeros((len(ys), len(phis), 3))
    N = np.zeros_like(G)
    for i, y in enumerate(ys):
        for j, ph in enumerate(phis):
            G[i, j], N[i, j] = ell(table, ph, y, off)
    return G, N


def cuirass(mesh: ck.Mesh, rig: ck.Rig) -> None:
    segs = 28
    phis = np.arange(segs) * 2.0 * math.pi / segs
    ys = np.concatenate([np.linspace(1.30, 1.84, 9), [1.95, 2.03, 2.08, 2.115, 2.125]])
    G, N = loft_grid(CUIRASS, phis, ys)
    P = G.reshape(-1, 3)
    T = ck.grid_tris(len(ys), segs, True)
    top = np.array([0.0, 2.13, -0.01])
    P = np.vstack([P, top])
    last = (len(ys) - 1) * segs
    T = np.vstack([T, [(last + k, last + (k + 1) % segs, len(P) - 1) for k in range(segs)]])
    want = np.vstack([N.reshape(-1, 3), [(0, 1, 0)]])
    put(mesh, "cuirass", P, T, "lacquer", PAL["lacquer_black"], torso_skin(rig), want=want)
    # the split breastplate: two red halves, gold on every edge but the split, the bound light in the split
    for side in (1.0, -1.0):
        ph0, ph1 = math.radians(2.6), math.radians(62.0)
        phis = bands(ph0, ph1, 9, GOLD_BAND / 0.24)
        ys = bands(1.50, 1.99, 10, GOLD_BAND)
        G, N = loft_grid(CUIRASS, side * phis, ys, off=0.012)
        parts = slab(G, N, TH, gold="rtb" if side > 0 else "rtb")
        put_slab(mesh, "breastplate", parts, "lacquer_red", PAL["lacquer_red_deep"], PAL["lacquer_red_deep"],
                 torso_skin(rig))
    seam_strip(mesh, rig, [ell(CUIRASS, 0.0, y, 0.006)[0] for y in np.linspace(1.50, 1.99, 8)], (0, 0, 1), 0.016,
               torso_skin(rig), "seams")


def seam_strip(mesh: ck.Mesh, rig: ck.Rig, pts, normal, width, bones, name, slot: str = "seam", col=None,
               em: float = 1.0) -> None:
    pts = np.asarray(pts)
    tan = unit(np.gradient(pts, axis=0))
    n = np.broadcast_to(unit(normal), pts.shape)
    side = unit(np.cross(n, tan))
    P = np.vstack([pts - side * width / 2, pts + side * width / 2])
    k = len(pts)
    T = [(i, k + i, i + 1) for i in range(k - 1)] + [(i + 1, k + i, k + i + 1) for i in range(k - 1)]
    put(mesh, name, P, T, slot, SEAM_COL if col is None else col, bones, want=np.vstack([n, n]), emission=em)


# ---- cloth (the Act II polish): shared helpers ------------------------------------------------
def fold(theta):
    """A hanging fold across angle theta: round crests (theta = 0 mod 2 pi), sharp creases between (theta = pi),
    zero mean. Range about -1.27 .. 0.73."""
    return 2.0 * np.abs(np.cos(np.asarray(theta) * 0.5)) - 1.0 - FOLD_MEAN


def grid_normals(G: np.ndarray, out_ref: np.ndarray, wrap: bool = False) -> np.ndarray:
    """Per-vertex normals of a (rows, cols, 3) grid from its own tangents, turned to agree with `out_ref`."""
    dv = np.gradient(G, axis=0)
    du = (np.roll(G, -1, axis=1) - np.roll(G, 1, axis=1)) if wrap else np.gradient(G, axis=1)
    n = unit(np.cross(du, dv))
    n[(n * out_ref).sum(axis=-1) < 0] *= -1.0
    return n


def trim_back(parts: dict, rows: int, keep: int) -> dict:
    """Keeps a slab's back face (a lining) only in its last `keep` rows of cells: the rest is never seen."""
    P, T, W = parts["back"]
    per = len(T) // (rows - 1)
    return dict(parts, back=(P, T[(rows - 1 - keep) * per:], W))


def emit_slab(mesh: ck.Mesh, name: str, parts: dict, face, back, bones, cav=None) -> None:
    """A slab() with per-vertex (grid-order) colours and cavity: face/back are (slot, colour (3,) or (R*C, 3)).
    `bones` is a function of position (the robe's, the mantle's and the sleeves' skins all are)."""
    for key, (slot, col), c in (("face", face, cav), ("back", back, None)):
        P, T, W = parts[key]
        if not len(T):
            continue
        col = np.asarray(col, dtype=np.float64)
        extra = (W, col if col.ndim == 2 else np.broadcast_to(col, P.shape),
                 np.zeros(len(P)) if c is None else np.asarray(c, dtype=np.float64))
        Ps, Ts, Ws, Cs, Ks = subset(P, T, extra)
        put(mesh, name, Ps, Ts, slot, Cs, bones, want=Ws, cavity=Ks)
    P, T, W = parts["gold"]
    if len(T):
        Ps, Ts, Ws = subset(P, T, (W,))
        put(mesh, "gold", Ps, Ts, "gold", PAL["gold_leaf"], bones, want=Ws)


# ---- the robe ---------------------------------------------------------------------------------
def robe_u(y):
    """0 at the waist, 1 at the under-robe's hem line."""
    return np.clip((ROBE_WAIST - np.asarray(y, dtype=np.float64)) / (ROBE_WAIST - HEM), 0.0, 1.1)


def robe_point(phi, y, off):
    """A point on the robe's base surface (an ellipse per height, flaring toward the hem and carried forward a
    little so the back stays clear of the folded wings) at angle phi (0 front, + toward +x), pushed `off` out."""
    phi = np.asarray(phi, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64) * np.ones_like(phi)
    u = robe_u(y)
    rx = ROBE_R[0] + (ROBE_R[1] - ROBE_R[0]) * u ** ROBE_FLARE
    rz = rx * DEPTH_RATIO
    n = unit(np.stack([np.sin(phi) / rx, np.zeros_like(phi), np.cos(phi) / rz], axis=-1))
    p = np.stack([rx * np.sin(phi), y, ROBE_FWD * u + rz * np.cos(phi)], axis=-1)
    return p + n * np.asarray(off)[..., None]


def robe_out(phi, y) -> np.ndarray:
    """The robe surface's outward direction (for orienting normals)."""
    return robe_point(phi, y, 0.01) - robe_point(phi, y, 0.0)


def under_fold(phi, y):
    """The under-robe's folds (metres out, and the fold's phase value): 16 round-crested folds growing from the
    waist to the hem, drifting a little so they do not hang ruler-straight, their depth varying round the robe."""
    u = robe_u(y)
    g = fold(UNDER_FOLDS * phi + 0.45 * np.sin(3.0 * phi + 1.7) + 0.5 * (1.0 - u))
    return UNDER_FOLD_M * u ** 0.9 * (1.0 + 0.25 * np.sin(5.0 * phi + 0.8)) * g, g


def over_fold(phi, y):
    """The lacquered over-robe's folds: fewer and stiffer than the silk's."""
    u = robe_u(y)
    g = fold(OVER_FOLDS * phi + 0.35 * np.sin(2.0 * phi + 0.4) + 0.3 * (1.0 - u))
    return OVER_FOLD_M * u ** 0.9 * (1.0 + 0.2 * np.sin(4.0 * phi + 2.3)) * g, g


def over_base(y):
    """How far out the over-robe's base sits: clear of the silk's deepest crest plus its own deepest crease."""
    u = robe_u(y) ** 0.9
    return 0.92 * 1.25 * UNDER_FOLD_M * u + 1.27 * 1.2 * OVER_FOLD_M * u + 0.008


def robe_skin(rig: ck.Rig):
    """The robe is skinned by height: the hips (`body`) above, `robe_1` at mid-shin, `robe_2` at the hem. When he
    kneels the hips sink furthest, so the cloth settles down onto itself (the old bells' telescope, as cloth)."""
    ib, i1, i2 = rig.index("body"), rig.index("robe_1"), rig.index("robe_2")
    y0, y1, y2 = ROBE_SKIN_Y

    def f(P):
        y = P[:, 1]
        upper = y >= y1
        t = np.where(upper, ck.smoothstep(y0, y1, y), ck.smoothstep(y1, y2, y))
        J = np.where(upper[:, None], np.array([ib, i1]), np.array([i1, i2])).astype(np.int64)
        return J, np.column_stack([1.0 - t, t])

    return f


def under_robe(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The silk under-robe: deep red, 16 folds, an uneven hem a little longer behind, a black silk hem band and a
    thin gold edge. It shows at the front opening and under the lacquered panels."""
    C = UNDER_COLS
    phis = np.arange(C) * 2.0 * math.pi / C
    hem = HEM + 0.016 - 0.012 * (1.0 - np.cos(phis)) * 0.5 + 0.01 * fold(UNDER_FOLDS * phis + 0.45 * np.sin(
        3.0 * phis + 1.7))
    Y = np.array([np.linspace(ROBE_TOP, h + 0.07, 9).tolist() + [h + 0.062, h + 0.012, h] for h in hem]).T
    Phi = np.broadcast_to(phis, Y.shape)
    d, g = under_fold(Phi, Y)
    lip = np.zeros_like(Y)
    lip[-3:] = 0.004  # the rolled hem: its weight shows as a lip
    G = robe_point(Phi, Y, d + lip)
    parts = trim_back(slab(G, grid_normals(G, robe_out(Phi, Y), wrap=True), 0.008, gold="t", wrap=True,
                           open_first=True), len(Y), 3)
    band = np.zeros(Y.shape, dtype=bool)
    band[-3:] = True
    col = np.where(band.reshape(-1, 1), SILK_BLACK, PAL["lacquer_red_deep"])
    cav = (np.clip(-g * 1.1, 0.0, 1.0) * np.clip(robe_u(Y) * 1.6, 0.0, 1.0) * 0.85).reshape(-1)
    emit_slab(mesh, "under_robe", parts, ("silk", col), ("silk", PAL["lacquer_red_deep"]), robe_skin(rig), cav=cav)


def over_panel(mesh: ck.Mesh, rig: ck.Rig, phi_of, hem_of, cols: int, lift: float) -> None:
    """One lacquered over-robe panel: `phi_of(y)` its (from, to) angles at a height, `hem_of(phi)` its hem. Gold
    rims down both edges and along the hem, following the folds; lined in red silk."""
    R = 10
    Y = np.zeros((R, cols))
    Phi = np.zeros((R, cols))
    lo0, hi0 = phi_of(ROBE_TOP)
    for j, uu in enumerate(np.linspace(0.0, 1.0, cols)):
        h = hem_of(lo0 + (hi0 - lo0) * uu)
        Y[:, j] = np.concatenate([np.linspace(ROBE_TOP, h + 0.016, R - 1), [h]])
    for i in range(R):
        for j in range(cols):
            lo, hi = phi_of(Y[i, j])
            r = float(np.hypot(*robe_point(np.array([0.5 * (lo + hi)]), np.array([Y[i, j]]), 0.0)[0, [0, 2]]))
            band = GOLD_BAND / max(0.15, r)
            uu = (j - 1) / (cols - 3)
            Phi[i, j] = lo if j == 0 else hi if j == cols - 1 else lo + band + (hi - lo - 2.0 * band) * uu
    d, g = over_fold(Phi, Y)
    G = robe_point(Phi, Y, over_base(Y) + lift + d)
    parts = trim_back(slab(G, grid_normals(G, robe_out(Phi, Y)), TH, gold="lrt", open_first=True), R, 3)
    cav = (np.clip(-g, 0.0, 1.0) * np.clip(robe_u(Y) * 1.5, 0.0, 1.0) * 0.7).reshape(-1)
    emit_slab(mesh, "over_robe", parts, ("lacquer", PAL["lacquer_black"]), ("silk", PAL["lacquer_red_deep"]),
              robe_skin(rig), cav=cav)


def over_robe(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Three lacquered panels over the silk: two in front (parted from the belt, the opening widening to the hem)
    and one behind, a little longer, overlapped by the front pair at his sides."""
    a0, a1 = (math.radians(a) for a in OPEN_DEG)
    side = math.radians(FRONT_TO_DEG)
    back0, back1 = (math.radians(a) for a in BACK_DEG)

    def opening(y):
        return a0 + (a1 - a0) * float(robe_u(y)) ** 0.8

    def front_hem(phi):
        return OVER_HEM[0] + (OVER_HEM[1] - OVER_HEM[0]) * min(1.0, abs(phi) / side) ** 1.5 + 0.01 * float(
            fold(OVER_FOLDS * phi))

    def back_hem(phi):
        k = 0.5 * (1.0 - math.cos(phi))  # 1 at the back
        return OVER_HEM[1] + (OVER_HEM[2] - OVER_HEM[1]) * k + 0.01 * float(fold(OVER_FOLDS * phi))

    over_panel(mesh, rig, lambda y: (opening(y), side), front_hem, 20, 0.006)
    over_panel(mesh, rig, lambda y: (-side, -opening(y)), front_hem, 20, 0.006)
    over_panel(mesh, rig, lambda y: (back0, back1), back_hem, 28, 0.0)


def belt(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A red lacquer belt over the robe's top, gold-edged; a knot at the left hip and two silk tails hanging from
    it over the front panel, skinned with the robe."""
    segs = 40
    phis = np.arange(segs) * 2.0 * math.pi / segs
    ys = bands(BELT[0], BELT[1], 2, GOLD_BAND * 0.8)
    Phi, Y = np.meshgrid(phis, ys)
    G = robe_point(Phi, Y, np.full(Y.shape, BELT_OUT))
    parts = slab(G, grid_normals(G, robe_out(Phi, Y), wrap=True), 0.012, gold="tb", wrap=True)
    put_slab(mesh, "belt", parts, "lacquer_red", PAL["lacquer_red_deep"], PAL["lacquer_red_deep"], rig.rigid("body"))
    ph = math.radians(SASH_DEG)
    knot = robe_point(np.array([ph]), np.array([0.5 * (BELT[0] + BELT[1])]), np.array([BELT_OUT + 0.018]))[0]
    Pk, Tk = ck.ellipsoid(knot, (0.042, 0.036, 0.03), 4, 10)
    put(mesh, "belt", Pk, Tk, "lacquer_red", PAL["lacquer_red_deep"], rig.rigid("body"))
    # the tails: silk ribbons from the knot, outside the panel (its base and its folds' reach), turning as they hang
    for k, (dph, low, w) in enumerate(SASH_TAILS):
        ys = np.concatenate([np.linspace(knot[1] - 0.03, low + 0.012, 9), [low]])  # a thin gold tip
        G = np.zeros((len(ys), 3, 3))
        for i, y in enumerate(ys):
            t = (knot[1] - y) / (knot[1] - low)
            phc = ph + math.radians(dph) * t + 0.04 * math.sin(t * 5.0 + k)
            off = np.array([over_base(y) + 0.006 + OVER_FOLD_M * float(robe_u(y)) ** 0.9 + 0.014])
            c = robe_point(np.array([phc]), np.array([y]), off)[0]
            tang = unit(robe_point(np.array([phc + 0.01]), np.array([y]), off)[0] - c)
            n_out = unit(robe_out(np.array([phc]), np.array([y]))[0])
            tw = 0.3 * math.sin(t * 3.0 + k * 1.3)
            across = unit(tang * math.cos(tw) + n_out * math.sin(tw))
            G[i] = [c - across * w * 0.5, c, c + across * w * 0.5]
        ref = robe_out(np.full(G.shape[:2], ph), G[..., 1])
        parts = slab(G, grid_normals(G, ref), 0.005, gold="t")
        emit_slab(mesh, "belt", parts, ("silk", PAL["lacquer_red_deep"]), ("silk", SILK_BLACK), robe_skin(rig))


def robe(mesh: ck.Mesh, rig: ck.Rig) -> None:
    under_robe(mesh, rig)
    over_robe(mesh, rig)
    belt(mesh, rig)
    # the light inside the shell: a dim floor of bound light under the robe, seen only from below
    Pd, Td = ck.ellipsoid((0.0, 0.2, 0.06), (0.5, 0.004, 0.42), 2, 24)
    put(mesh, "seams", Pd, Td, "seam", SEAM_COL, rig.rigid("robe_2"), emission=0.5)


def tube_part(mesh, name, path, radius, segs, slot, col, bones, cap=True, squash=1.0, up=(0.0, 1.0, 0.0), em=0.0):
    P, T = ck.tube(path, radius, segs, cap_start=cap, cap_end=cap, up_hint=up, squash=squash)
    put(mesh, name, P, T, slot, col, bones, emission=em)


def ring_at(center, axis, radius, tube_r, segs=20, tsegs=6):
    axis = unit(axis)
    ref = unit(np.cross(axis, (0.0, 0.0, 1.0) if abs(axis[2]) < 0.9 else (1.0, 0.0, 0.0)))
    other = np.cross(axis, ref)
    a = np.arange(segs + 1) * 2.0 * math.pi / segs
    path = center + radius * (np.outer(np.cos(a), ref) + np.outer(np.sin(a), other))
    return ck.tube(path, tube_r, tsegs, cap_start=False, cap_end=False, up_hint=axis)


def arm_points(side: float):
    return (SHOULDER_L, ELBOW_L, WRIST_L) if side > 0 else (mirror(SHOULDER_L), mirror(ELBOW_L), mirror(WRIST_L))


def sleeve_skin(rig: ck.Rig, tag: str, s, e, w):
    """Positional: the upper sleeve on the upper arm (its top shared with the chest, under the mantle), the
    forearm and the hanging bag on the forearm, blended across the elbow."""
    isp, i0, i1 = rig.index("spine_2"), rig.index(f"arm_{tag}0"), rig.index(f"arm_{tag}1")
    up_dir, fw_dir = unit(s - e), unit(w - e)
    L1 = float(np.linalg.norm(s - e))

    def f(P):
        u1 = (P - e) @ up_dir
        u2 = (P - e) @ fw_dir
        w1 = ck.smoothstep(-0.04, 0.06, u2 - u1)
        wsp = 0.35 * ck.smoothstep(L1 - 0.12, L1, u1)
        top = wsp > 1e-3
        J = np.where(top[:, None], np.array([isp, i0]), np.array([i0, i1])).astype(np.int64)
        W = np.where(top[:, None], np.column_stack([wsp, 1.0 - wsp]), np.column_stack([1.0 - w1, w1]))
        return J, W

    return f


def sleeve(mesh: ck.Mesh, rig: ck.Rig, side: float, tag: str) -> None:
    """A wide hanging sleeve: close at the shoulder (under the mantle), widening down the arm; under the forearm it
    hangs in a deep bag, sewn shut in front and rounded up to the opening round the wrist, six soft folds round
    it. Black silk outside, red silk inside; the opening turned back in a red band and edged in gold, so the lining
    shows round the hand."""
    s, e, w = arm_points(side)
    d1, d2 = e - s, w - e
    u2 = unit(d2)
    cuff = w + u2 * SLEEVE_CUFF
    stations = [(s + d1 * t, 0.0, r) for t, r in ((0.0, 0.082), (0.3, 0.087), (0.6, 0.092), (0.86, 0.096))]
    stations.append((e + u2 * 0.05, 0.0, 0.1))
    for t, bag, r in SLEEVE_FORE:  # along the forearm: how far the bag hangs (of SLEEVE_BAG) and the radius
        stations.append((e + (cuff - e) * t, bag, r))
    for back, bag, r in SLEEVE_FRONT:  # the sewn front, rounding up to the opening (metres back from it)
        stations.append((cuff - u2 * back, bag, r))
    path = np.array([p for p, _, _ in stations])
    fpar = np.array([b for _, b, _ in stations])
    r0 = np.array([r for _, _, r in stations])
    tan, nrm, bin_ = ck.frames_along(path, up_hint=(side, 0.0, 0.0))
    segs = SLEEVE_SEGS
    a = np.arange(segs) * 2.0 * math.pi / segs
    K = len(path)
    G = np.zeros((K, segs, 3))
    cav = np.zeros((K, segs))
    arc = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
    arc /= arc[-1]
    for k in range(K):
        down = np.array([0.0, -1.0, 0.0]) - tan[k] * (-tan[k][1])
        down = unit(down) if np.linalg.norm(down) > 0.3 else down * 0.0
        dirs = np.outer(np.cos(a), nrm[k]) + np.outer(np.sin(a), bin_[k])
        g = fold(SLEEVE_FOLDS * a + 1.3 * arc[k] + 0.6 * side)
        amp = SLEEVE_FOLD * ck.smoothstep(0.2, 0.75, arc[k]) * (0.4 + 0.6 * min(1.0, fpar[k] * 1.5 + 0.3))
        r = r0[k] * (1.0 + amp * g)
        bag = SLEEVE_BAG * fpar[k] * np.clip(dirs @ down, 0.0, 1.0) ** 1.4
        G[k] = path[k] + dirs * r[:, None] + down * bag[:, None]
        cav[k] = np.clip(-g, 0.0, 1.0) * ck.smoothstep(0.25, 1.0, arc[k]) * 0.75
    # normals from the surface itself, out from the arm's axis
    N = grid_normals(G, G - path[:, None, :], wrap=True)
    parts = trim_back(slab(G, N, 0.008, gold="t", wrap=True, open_first=True), K, 7)
    col = np.tile(SILK_BLACK, (K, segs, 1))
    col[-3:] = PAL["lacquer_red_deep"]  # the turned-back lining
    emit_slab(mesh, "sleeves", parts, ("silk", col.reshape(-1, 3)), ("silk", PAL["lacquer_red_deep"]),
              sleeve_skin(rig, tag, s, e, w), cav=cav.reshape(-1))
    # the bound light where the hand leaves the sleeve, deep in the cuff
    P, T = ring_at(w - u2 * 0.004, u2, 0.033, 0.0045, 16, 4)
    put(mesh, "seams", P, T, "seam", SEAM_COL, rig.rigid(f"arm_{tag}1"), emission=1.0)


def hand_frame(side: float):
    """The hand's (wrist, forward, across toward the little finger, up out of the back of the hand)."""
    w = arm_points(side)[2]
    fwd = unit(np.array([0.0, -0.008, 0.09]))
    across = np.array([side, 0.0, 0.0])
    return w, fwd, across, unit(np.cross(fwd, across)) * side


def finger_path(side: float, f: int) -> tuple[np.ndarray, np.ndarray]:
    """One finger (0 index .. 3 little) at rest, relaxed: its axis points (knuckle, mid, joint, mid, joint, mid,
    tip) and radii, each joint a little proud (the knuckles' read)."""
    w, fwd, across, up = hand_frame(side)
    base = w + fwd * PALM_LEN + across * FINGER_X[f] * HAND_SCALE + up * -0.002
    yaw = math.radians(FINGER_SPLAY[f])
    d = unit(fwd * math.cos(yaw) + across * math.sin(yaw))
    pts = [base]
    pitch = 0.0
    for k, (ln, bend) in enumerate(zip(FINGER_LEN[f], FINGER_BEND)):
        pitch += math.radians(bend)
        dk = unit(d * math.cos(pitch) - up * math.sin(pitch))
        pts.append(pts[-1] + dk * ln * 0.5 * HAND_SCALE)
        pts.append(pts[-1] + dk * ln * 0.5 * HAND_SCALE)
    sc = FINGER_R_SCALE[f] * HAND_SCALE
    rad = np.array([0.0102, 0.0090, 0.0094, 0.0084, 0.0087, 0.0077, 0.0062]) * sc
    return np.array(pts), rad


def nail(mesh: ck.Mesh, a: np.ndarray, b: np.ndarray, r: float, bones) -> None:
    """A small gilded nail over the last joint from a to b (the finger's tip), on its back."""
    T = unit(b - a)
    U = unit(np.array([0.0, 1.0, 0.0]) - T * T[1])
    S = np.cross(T, U)
    c = a + (b - a) * 0.62
    L = float(np.linalg.norm(b - a)) * 0.34
    G = np.array([[c + T * s + (U * math.cos(t) + S * math.sin(t)) * (r + 0.0008) for t in np.radians([-55, 0, 55])]
                  for s in np.linspace(-L, L, 3)])
    put(mesh, "hands", G.reshape(-1, 3), ck.grid_tris(3, 3, False), "gold", PAL["gold_leaf"], bones,
        want=np.broadcast_to(U, (9, 3)))


def hand(mesh: ck.Mesh, rig: ck.Rig, side: float, tag: str) -> None:
    """A lacquer hand, held level, palm down: a palm lofted from the wrist (inside the cuff) to the knuckles, four
    three-jointed fingers relaxed in a slight curl, a thumb, gilded nails. The left hand's ring and little fingers
    ride `finger_l1` (the ring's), its index and middle `finger_l0`."""
    w, fwd, across, up = hand_frame(side)
    hb = rig.rigid(f"hand_{tag}")
    segs = 12
    a = np.arange(segs) * 2.0 * math.pi / segs
    ca, sa = np.cos(a), np.sin(a)
    sx = np.sign(ca) * np.abs(ca) ** 0.55
    sy = np.sign(sa) * np.abs(sa) ** 0.7
    rows = []
    for s_, hw, ht in PALM:
        c = w + fwd * s_ - up * 0.006 * max(0.0, s_) / PALM_LEN
        rows.append(c + np.outer(sx * hw * HAND_SCALE, across) + np.outer(sy * ht * HAND_SCALE, up))
    P = np.vstack(rows)
    T = ck.flip(ck.grid_tris(len(PALM), segs, True))
    end = len(P)
    P = np.vstack([P, w + fwd * (PALM[-1][0] + 0.002) - up * 0.006])
    last = (len(PALM) - 1) * segs
    T = np.vstack([T, [(last + k, last + (k + 1) % segs, end) for k in range(segs)]])
    want = np.vstack([np.vstack([np.outer(sx, across) + np.outer(sy, up)] * len(PALM)), fwd[None]])
    put(mesh, "hands", P, T, "lacquer", PAL["lacquer_black"], hb, want=want)
    for f in range(4):
        pts, rad = finger_path(side, f)
        bones = (rig.rigid("finger_l0") if f < 2 else rig.rigid("finger_l1")) if tag == "l" else hb
        P, T = ck.tube(pts, rad, 6, cap_start=False, cap_end=True, up_hint=tuple(up), squash=0.84)
        put(mesh, "hands", P, T, "lacquer", PAL["lacquer_black"], bones)
        nail(mesh, pts[-3], pts[-1], float(rad[-2]) * 0.84, bones)
        if tag == "l" and f == 2:  # the copper ring on the ring finger, past the knuckle
            P, T = ring_at(ring_centre(), pts[1] - pts[0], float(rad[1]) + 0.0022, 0.0028, 18, 6)
            put(mesh, "ring", P, T, "ring", RING_COL, bones)
    # the thumb, from the heel of the hand, forward and in, two joints
    base = w + fwd * 0.03 - across * 0.028 * HAND_SCALE - up * 0.008
    d = unit(fwd * 0.8 - across * 0.5 - up * 0.25)
    pts = [base]
    for ln, bend in ((0.034 * HAND_SCALE, 8.0), (0.027 * HAND_SCALE, 14.0)):
        d = unit(d * math.cos(math.radians(bend)) - up * math.sin(math.radians(bend)) + across * 0.05)
        pts += [pts[-1] + d * ln * 0.5, pts[-1] + d * ln]
    pts = np.array(pts)
    rad = np.array([0.0125, 0.0112, 0.0108, 0.0096, 0.0074]) * HAND_SCALE
    P, T = ck.tube(pts, rad, 6, cap_start=False, cap_end=True, up_hint=tuple(up), squash=0.86)
    put(mesh, "hands", P, T, "lacquer", PAL["lacquer_black"], hb)
    nail(mesh, pts[-3], pts[-1], float(rad[-2]) * 0.86, hb)


def mantle_point(phi, v, off):
    """The shoulder mantle at angle phi and drop v (0 at the collar, 1 at the outer layer's hem): it rises over
    the collar, spreads out over the shoulders (the sleeves' tops are under it) and falls."""
    phi = np.asarray(phi, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    vc = np.minimum(v, 1.0)
    over = np.maximum(v - 1.0, 0.0)
    rx = MANTLE_RX[0] + (MANTLE_RX[1] - MANTLE_RX[0]) * (1.0 - (1.0 - vc) ** 2.2) + 0.10 * over
    rz = MANTLE_RZ[0] + (MANTLE_RZ[1] - MANTLE_RZ[0]) * vc ** 0.7 + 0.05 * over
    front = np.minimum(np.abs(phi), 2.0 * math.pi - np.abs(phi))
    drop = MANTLE_DROP - 0.05 * ck.smoothstep(1.4, 0.9, front)
    y = MANTLE_TOP - drop * (vc ** 1.25 + 1.25 * over)
    n = unit(np.stack([np.sin(phi) / rx, np.zeros_like(phi) + 0.3 * vc, np.cos(phi) / rz], axis=-1))
    g = fold(MANTLE_FOLDS * phi + 0.4 * np.sin(3.0 * phi))
    p = np.stack([rx * np.sin(phi), y, -0.01 + rz * np.cos(phi)], axis=-1)
    return p + n * (MANTLE_FOLD * vc ** 1.3 * g + off)[..., None], g * vc


def mantle(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Two layers of lacquered cloth over the shoulders, parted at the breast: the red one over a longer black one,
    each with a gold hem and gold front edges. The shoulders and the sleeves' tops are under them, so no joint
    shows; their sides go a little with the arms."""
    isp, il, ir = rig.index("spine_2"), rig.index("arm_l0"), rig.index("arm_r0")

    def skin(P):
        x = P[:, 0]
        wa = 0.4 * ck.smoothstep(0.28, 0.45, np.abs(x))
        J = np.column_stack([np.full(len(P), isp), np.where(x > 0, il, ir)]).astype(np.int64)
        return J, np.column_stack([1.0 - wa, wa])

    op = math.radians(MANTLE_OPEN_DEG)
    C = MANTLE_COLS
    for vmax, off, slot, col in ((MANTLE_UNDER, 0.0, "lacquer", PAL["lacquer_black"]),
                                 (1.0, 0.009, "lacquer_red", PAL["lacquer_red_deep"])):
        vs = np.concatenate([np.linspace(0.0, vmax - 0.05, 6), [vmax - 0.03, vmax]])
        Phi = np.zeros((len(vs), C))
        for i, v in enumerate(vs):
            rx = float(mantle_point(np.array([op]), np.array([v]), np.array([0.0]))[0][0, 0]) / math.sin(op)
            band = GOLD_BAND / rx
            Phi[i] = np.concatenate([[op], np.linspace(op + band, 2.0 * math.pi - op - band, C - 2),
                                     [2.0 * math.pi - op]])
        V = np.broadcast_to(vs[:, None], Phi.shape)
        G, g = mantle_point(Phi, V, np.full(Phi.shape, off))
        ref = G - np.array([0.0, 2.0, -0.01])
        parts = trim_back(slab(G, grid_normals(G, ref), 0.01, gold="lrt", open_first=True), len(vs), 3)
        cav = (np.clip(-g, 0.0, 1.0) * 0.7).reshape(-1)
        emit_slab(mesh, "mantle", parts, (slot, col), ("silk", SILK_BLACK), skin, cav=cav)


def collar_and_head(mesh: ck.Mesh, rig: ck.Rig) -> None:
    neck_skin = rig.blend("spine_2", "neck", (0, 2.08, 0), (0, 2.2, 0))
    table = [(2.06, 0.115, 0.1, -0.01), (2.21, 0.125, 0.115, -0.005)]
    segs = 28
    phis = np.arange(segs) * 2.0 * math.pi / segs
    G, N = loft_grid(table, phis, [2.06, 2.12, 2.21])
    put(mesh, "collar", (G + N * 0.006).reshape(-1, 3), ck.grid_tris(3, segs, True), "lacquer",
        PAL["lacquer_black"], neck_skin, want=N.reshape(-1, 3))
    put(mesh, "collar", (G - N * 0.006).reshape(-1, 3), ck.grid_tris(3, segs, True), "lacquer",
        PAL["lacquer_black"], neck_skin, want=-N.reshape(-1, 3))
    P, T = ring_at(np.array([0.0, 2.21, -0.005]), (0, 1, 0), 0.121, 0.007, 24, 5)
    put(mesh, "gold", P, T, "gold", PAL["gold_leaf"], rig.rigid("neck"))
    Pn, Tn = ck.lathe([(0.075, 2.12), (0.07, 2.2), (0.065, 2.26)], 14)
    put(mesh, "collar", Pn, Tn, "lacquer", PAL["lacquer_black"], rig.rigid("neck"))
    Ph, Th = ck.ellipsoid(HEAD_C, HEAD_R, 8, 14)
    put(mesh, "head", Ph, Th, "lacquer", PAL["lacquer_black"], rig.rigid("head"))
    # M4-CRB-008: a red lacquer crown capping the head over the veil's top edge; up close the bare crown of the head
    # stood out of the veil's open top, and the veil read as a lampshade set on a ball
    Pc, Tc = ck.ellipsoid(CROWN_C, CROWN_R, 6, 16)
    put(mesh, "head", Pc, Tc, "lacquer_red", PAL["lacquer_red_deep"], rig.rigid("head"))


VEIL = [(1.92, 0.25, 0.275, 0.03), (2.05, 0.215, 0.24, 0.025), (2.17, 0.165, 0.205, 0.02),
        (2.30, 0.132, 0.16, 0.016), (2.36, 0.122, 0.142, 0.013), (2.41, 0.108, 0.122, 0.012)]


def veil_spread(y: float) -> float:
    """How far round the head the veil reaches at height y (radians each side of the front)."""
    return math.radians(float(np.interp(y, [1.92, 2.0, 2.1, 2.2, 2.41], [58.0, 66.0, 84.0, 112.0, 118.0])))


def veil(rig: ck.Rig) -> ck.Mesh:
    """The veil: its own mesh on its own bone, so cinematics can drop it. Gauze, faintly lit from behind, a gold
    border at its hem."""
    m = ck.Mesh("ethren_veil")
    ys = bands(1.92, 2.41, 10, GOLD_BAND)
    u = np.linspace(-1.0, 1.0, VEIL_COLS)
    G = np.zeros((len(ys), len(u), 3))
    N = np.zeros_like(G)
    shade = np.zeros((len(ys), len(u)))
    for i, y in enumerate(ys):
        sp = veil_spread(y)
        hang = (2.41 - y) / (2.41 - 1.92)  # 0 at the crown band, 1 at the hem
        depth = VEIL_PLEAT_M[0] + (VEIL_PLEAT_M[1] - VEIL_PLEAT_M[0]) * hang
        for j, uv in enumerate(u):
            # M4-CRB-008: soft pleats (the gauze hangs, it is not a turned shade), and the face behind it shows dark
            # through the thin gauze over the head, fading out below the chin and toward the sides
            G[i, j], N[i, j] = ell(VEIL, uv * sp, y, depth * math.cos(uv * math.pi * VEIL_PLEATS))
            shade[i, j] = math.exp(-(uv / 0.42) ** 2) * ck.smoothstep(2.02, 2.2, y) * ck.smoothstep(2.42, 2.36, y)
    parts = slab(G, N, 0.006, gold="b")
    dark = VEIL_SHADE[0] + (VEIL_SHADE[1] - VEIL_SHADE[0]) * shade.reshape(-1)
    cols = np.array([ck.mix(PAL["gauze_white"], PAL["lacquer_black"], k) for k in dark])
    vb = rig.rigid("veil")
    P, T, W = parts["face"]
    Ps, Ts, Ws, Cs = subset(P, T, (W, cols))
    put(m, "veil", Ps, Ts, "veil", Cs, vb, want=Ws, emission=1.0)
    P, T, W = parts["back"]
    Ps, Ts, Ws = subset(P, T, (W,))
    put(m, "veil", Ps, Ts, "veil", PAL["gauze_white"], vb, want=Ws, emission=1.0)
    P, T, W = parts["gold"]
    Ps, Ts, Ws = subset(P, T, (W,))
    put(m, "veil_gold", Ps, Ts, "gold", PAL["gold_leaf"], vb, want=Ws)
    return m


def halo_z(r):
    """The bowl's depth at radius r: its lip nearest the head, its hollow centre deepest."""
    return HALO_C[2] - HALO_DEPTH * (1.0 - (np.asarray(r) / HALO_R) ** 2)


def halo(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A thin bowl of bound light floating behind the head, clear of it: open at its centre (the crown shows
    through), its lit face brightest at the hollow's edge and falling off toward a red lacquer rim and the gold
    lip. The back is black lacquer."""
    hb = rig.rigid("halo")
    segs = HALO_SEGS
    a = np.arange(segs) * 2.0 * math.pi / segs
    rs = np.array(HALO_RINGS)
    G = np.zeros((len(rs), segs, 3))
    N = np.zeros_like(G)
    for i, r in enumerate(rs):
        dz = 2.0 * HALO_DEPTH * r / HALO_R ** 2  # the bowl's slope: its inner normal leans in
        G[i] = np.column_stack([HALO_C[0] + r * np.cos(a), HALO_C[1] + r * np.sin(a), np.full(segs, halo_z(r))])
        N[i] = unit(np.column_stack([-dz * np.cos(a), -dz * np.sin(a), np.ones(segs)]))
    lit = rs <= HALO_RIM + 1e-6
    rho = np.clip((rs - rs[0]) / (HALO_RIM - rs[0]), 0.0, 1.0)
    glow = HALO_GLOW[1] + (HALO_GLOW[0] - HALO_GLOW[1]) * rho ** 0.6  # bright at the hollow, falling off outward
    nl = int(lit.sum())
    T = ck.grid_tris(nl, segs, True)
    cols = np.repeat([ck.mix(SEAM_COL, PAL["lacquer_black"], 0.85 * k ** 1.1) for k in rho[:nl]], segs, axis=0)
    put(mesh, "halo", (G[:nl] + N[:nl] * 0.001).reshape(-1, 3), T, "halo", cols, hb, want=N[:nl].reshape(-1, 3),
        emission=np.repeat(glow[:nl], segs))
    Tr = ck.grid_tris(len(rs) - nl + 1, segs, True)
    put(mesh, "halo", (G[nl - 1:] + N[nl - 1:] * 0.001).reshape(-1, 3), Tr, "lacquer_red", PAL["lacquer_red_deep"],
        hb, want=N[nl - 1:].reshape(-1, 3))
    put(mesh, "halo", (G - N * HALO_TH).reshape(-1, 3), ck.grid_tris(len(rs), segs, True), "lacquer",
        PAL["lacquer_black"], hb, want=-N.reshape(-1, 3))
    # the hollow's edge: a wall of light between the faces
    Pw = np.vstack([G[0] + N[0] * 0.001, G[0] - N[0] * HALO_TH])
    Tw = ck.grid_tris(2, segs, True)
    put(mesh, "halo", Pw, Tw, "halo", SEAM_COL, hb, want=np.vstack([-(G[0] - HALO_C) * (1, 1, 0)] * 2),
        emission=1.0)
    P, T = ring_at(np.array([HALO_C[0], HALO_C[1], halo_z(HALO_R)]), (0, 0, 1), HALO_R, 0.009, 40, 4)
    put(mesh, "gold", P, T, "gold", PAL["gold_leaf"], hb)


def leaf_surface(tag: str, lower: bool):
    """One leaf's surface as a function of (u across 0..1, v down 0..LEAF_LEN): a lacquer screen leaf of two
    half-panels hinged down its middle and set at a shallow V (a folding screen's zigzag, so one half catches the
    light and the other does not), its free end cusped. Returns f(u, v) -> (point, normal)."""
    pivot, top, down, across, normal = leaf_frame(tag)
    start = top + down * ((LEAF_LEN + LEAF_GAP) if lower else 0.0)

    def f(u, v):
        fv = v / LEAF_LEN
        width = LEAF_W * ((1.0 - 0.14 * fv) if lower else 1.0)
        point = 1.0 - (2.0 * u - 1.0) ** 2
        if lower:
            off = v + (0.09 * point * ck.smoothstep(0.82, 1.0, fv) if fv > 0.82 else 0.0)
        else:
            off = v - (0.11 * point * ck.smoothstep(0.18, 0.0, fv) if fv < 0.18 else 0.0)
        ridge = 1.0 - abs(2.0 * u - 1.0)
        p = start + down * off + across * (u * width) + normal * LEAF_ZIG * ridge
        n = unit(normal + across * (2.0 * LEAF_ZIG / width) * (1.0 if u > 0.5 else -1.0))
        return p, n

    return f


def leaf_wear(P: np.ndarray, d_edge: np.ndarray, seed: int) -> np.ndarray:
    """How worn the black lacquer is (0..1): at the leaf's edges and corners, broken by noise, the red under it
    shows through (the lacquer's own wear: black over a red ground)."""
    n = 0.5 + 0.5 * ck.fbm(P * 26.0, seed, 3) * 1.6
    return np.clip(ck.smoothstep(LEAF_WEAR_M, 0.0, d_edge) * n, 0.0, 1.0) * 0.5


def leaf_field(mesh: ck.Mesh, f, u0: float, u1: float, v0: float, v1: float, sgn: float, slot: str, col,
               bone: int) -> None:
    """A field set into a half-panel: hard-edged, its border sunk (cavity), just proud of the face (sgn: which)."""
    uu = np.linspace(u0, u1, 4)
    vv = np.array([v0, v0 + 0.012, v1 - 0.012, v1])
    Pf = np.zeros((4, 4, 3))
    Nf = np.zeros_like(Pf)
    for i, v in enumerate(vv):
        for j, u in enumerate(uu):
            p, n = f(u, v)
            Pf[i, j] = p + n * sgn * (LEAF_TH * 0.5 + 0.0025)
            Nf[i, j] = n * sgn
    ring_ = np.ones((4, 4))
    ring_[1:3, 1:3] = 0.0
    put(mesh, "wings", Pf.reshape(-1, 3), ck.grid_tris(4, 4, False), slot, col, bone, want=Nf.reshape(-1, 3),
        cavity=ring_.reshape(-1) * 0.85)


def wings(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Four wings of two leaves each, a folding screen of lacquer. Each leaf is two half-panels at a shallow V,
    each rimmed in gold; the outer faces black lacquer worn to its red ground at the edges, a red field set in each;
    the inner faces red, two darker red fields in each half between a rail, and the bound light in the hinge line down
    the middle. The leaves are joined by hinge knuckles with the light in that line too."""
    for wi, tag in enumerate(("li", "lo", "ri", "ro")):
        pivot, top, down, across, normal = leaf_frame(tag)
        for lower in (False, True):
            f = leaf_surface(tag, lower)
            bone = rig.rigid(f"wing_{tag}_{1 if lower else 0}")
            for h0, h1, rim in ((0.0, 0.5 - LEAF_HALF_GAP, "ltb"), (0.5 + LEAF_HALF_GAP, 1.0, "rtb")):
                us = bands(h0, h1, LEAF_COLS - 3, GOLD_BAND / LEAF_W)
                vs = bands(0.0, LEAF_LEN, LEAF_ROWS - 3, GOLD_BAND)
                G = np.zeros((len(vs), len(us), 3))
                N = np.zeros_like(G)
                dE = np.zeros((len(vs), len(us)))
                for i, v in enumerate(vs):
                    width = LEAF_W * ((1.0 - 0.14 * v / LEAF_LEN) if lower else 1.0)
                    for j, u in enumerate(us):
                        G[i, j], N[i, j] = f(u, v)
                        dE[i, j] = min((u - h0) * width, (h1 - u) * width, v, LEAF_LEN - v)
                parts = slab(G, N, LEAF_TH, gold=rim)  # no gold down the hinge between the halves
                wear = leaf_wear(G.reshape(-1, 3), dE.reshape(-1), SEED + 31 * wi + (7 if lower else 0))
                face = np.array([ck.mix(PAL["lacquer_black"], PAL["lacquer_red_deep"], k) for k in wear])
                emit_slab(mesh, "wings", parts, ("lacquer", face), ("lacquer_red", PAL["lacquer_red_deep"]), bone,
                          cav=wear * 0.3)
                m = (h1 - h0) * 0.2
                leaf_field(mesh, f, h0 + m, h1 - m, 0.08 * LEAF_LEN, 0.92 * LEAF_LEN, 1.0, "lacquer_red",
                           PAL["lacquer_red_deep"], bone)
                for v0, v1 in LEAF_FIELDS:
                    leaf_field(mesh, f, h0 + m, h1 - m, v0 * LEAF_LEN, v1 * LEAF_LEN, -1.0, "lacquer_red",
                               LEAF_FIELD_IN, bone)
            # the light in the hinge line between the halves, on the inner face
            vs = np.linspace(0.03, 0.97, 6) * LEAF_LEN
            pts = [f(0.5, v)[0] - f(0.5, v)[1] * (LEAF_TH * 0.5 - 0.002) for v in vs]
            seam_strip(mesh, rig, pts, -normal, 0.006, bone, "seams")
        # the hinge between the leaves: knuckles taken alternately by the two leaves, the light in the line
        joint = top + down * (LEAF_LEN + LEAF_GAP * 0.5)
        for k, u in enumerate(HINGE_U):
            c = joint + across * LEAF_W * u + normal * LEAF_ZIG * (1.0 - abs(2.0 * u - 1.0))
            path = np.array([c - across * 0.028, c, c + across * 0.028])
            P, T = ck.tube(path, 0.015, 8, up_hint=tuple(normal))
            put(mesh, "wings", P, T, "lacquer", PAL["lacquer_black"], rig.rigid(f"wing_{tag}_{k % 2}"))
        path = np.array([joint + across * LEAF_W * u + normal * LEAF_ZIG * (1.0 - abs(2.0 * u - 1.0))
                         for u in (0.03, 0.5, 0.97)])
        tube_part(mesh, "seams", path, 0.006, 6, "seam", SEAM_COL, rig.rigid(f"wing_{tag}_0"), up=tuple(normal),
                  em=1.0)
        # the leaf's hanging hinge at the yoke: a knuckle and a bead of light
        path = np.array([pivot - across * 0.03, pivot + across * 0.03])
        P, T = ck.tube(path, 0.02, 8, up_hint=tuple(normal))
        put(mesh, "wings", P, T, "lacquer", PAL["lacquer_black"], rig.rigid(f"wing_{tag}_0"))
        Pb, Tb = ck.ellipsoid(pivot + normal * 0.012, (0.012, 0.012, 0.012), 3, 6)
        put(mesh, "seams", Pb, Tb, "seam", SEAM_COL, rig.rigid(f"wing_{tag}_0"), emission=1.0)
    # the yoke the wings hang from, across the upper back
    path = np.array([[x, PIVOT_Y + 0.01, -0.2 - 0.05 * (1.0 - abs(x) / 0.2)] for x in np.linspace(-0.2, 0.2, 7)])
    tube_part(mesh, "wings", path, 0.035, 10, "lacquer", PAL["lacquer_black"], rig.rigid("spine_2"), squash=0.7)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    PARTS.clear()
    mesh = ck.Mesh("ethren")
    cuirass(mesh, rig)
    robe(mesh, rig)
    mantle(mesh, rig)
    for side, tag in ((1.0, "l"), (-1.0, "r")):
        sleeve(mesh, rig, side, tag)
        hand(mesh, rig, side, tag)
    collar_and_head(mesh, rig)
    halo(mesh, rig)
    wings(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 4.0
IDLE_RISE = 0.005  # half of the 1 cm rise and fall
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
IDLE_B_SEC = 1.6
KNEEL = 0.45  # how far the hips sink when he kneels; the robe settles onto itself
KNEEL_R1, KNEEL_R2 = 0.24, 0.04  # the lower bells' share of it
BONES_AT_REST = ("root", "body", "spine_0", "spine_1", "spine_2", "neck", "head", "halo", "robe_1", "robe_2",
                 "arm_l0", "arm_l1", "hand_l", "finger_l0", "finger_l1", "arm_r0", "arm_r1", "hand_r")


def wing_pose(c: ck.Clip, t: float, spread=(0.0, 0.0), turn=(0.0, 0.0), fold=(0.0, 0.0), lift=(0.0, 0.0),
              hoist: float = 0.0) -> None:
    """The wings: `spread` fans each pair out (degrees about the pivot's forward axis; inner, outer), `turn` swings it
    round the vertical (+ forward), `fold` bends the lower leaf at its hinge (+ forward), `lift` raises the leaf's
    free end back (about x); `hoist` slides the closed wings up his back (metres), so they stay off the water as he
    kneels."""
    for k, pair in enumerate(("i", "o")):
        for side, tag in ((1.0, "l"), (-1.0, "r")):
            c.key(f"wing_{tag}{pair}_0", t, (-lift[k], side * turn[k], side * spread[k]), (0.0, hoist, 0.0))
            c.key(f"wing_{tag}{pair}_1", t, (-fold[k], 0.0, 0.0))


def arm_pose(c: ck.Clip, t: float, tag: str, upper=(0.0, 0.0, 0.0), fore=(0.0, 0.0, 0.0), hand=(0.0, 0.0, 0.0),
             mirror_side: bool = True) -> None:
    """Rotations (degrees about the rest axes) of one arm; given for the left and mirrored for the right."""
    f = np.array([1.0, -1.0, -1.0]) if (tag == "r" and mirror_side) else np.ones(3)
    c.key(f"arm_{tag}0", t, tuple(np.asarray(upper) * f))
    c.key(f"arm_{tag}1", t, tuple(np.asarray(fore) * f))
    c.key(f"hand_{tag}", t, tuple(np.asarray(hand) * f))


def both_arms(c: ck.Clip, t: float, upper=(0.0, 0.0, 0.0), fore=(0.0, 0.0, 0.0), hand=(0.0, 0.0, 0.0)) -> None:
    for tag in ("l", "r"):
        arm_pose(c, t, tag, upper, fore, hand)


def torso(c: ck.Clip, t: float, bow: float = 0.0, lean: float = 0.0, head: float = 0.0, y: float = 0.0,
          z: float = 0.0, roll: float = 0.0) -> None:
    """`bow` + forward (spread over the spine), `lean` the hips' pitch, `head` its own bow, `y`/`z` the hips' shift."""
    c.key("body", t, (lean, 0.0, roll * 0.4), (0.0, y, z))
    for k in range(3):
        c.key(f"spine_{k}", t, (bow / 3.0, 0.0, roll * 0.2))
    c.key("neck", t, (head * 0.4, 0.0, 0.0))
    c.key("head", t, (head * 0.6, 0.0, 0.0))


def kneel(c: ck.Clip, t: float, f: float) -> None:
    """f of the way down: the hips sink KNEEL and the robe's shin and hem bones part of it, so the cloth settles."""
    c.key("robe_1", t, (0, 0, 0), (0.0, -KNEEL_R1 * f, 0.02 * f))
    c.key("robe_2", t, (0, 0, 0), (0.0, -KNEEL_R2 * f, 0.0))


def still(c: ck.Clip) -> ck.Clip:
    """Keys every unkeyed figure bone at rest at both ends, so a clip blends from a defined pose."""
    for b in BONES_AT_REST:
        if b not in c.keys:
            c.key(b, 0.0)
            c.key(b, c.length)
    for tag in ("li", "lo", "ri", "ro"):
        for k in (0, 1):
            if f"wing_{tag}_{k}" not in c.keys:
                c.key(f"wing_{tag}_{k}", 0.0)
                c.key(f"wing_{tag}_{k}", c.length)
    return c


def build_idle() -> ck.Clip:
    c = ck.Clip("idle", IDLE_SEC, loop=True)  # almost nothing: a 1 cm rise and fall; the veil, wings and hands still
    c.wave("root", amp_loc=(0, IDLE_RISE, 0), cycles=1, phase=0.0, steps=16)
    return still(c)


def build_idle_b() -> ck.Clip:
    """The fidget, authored (the kit's would be the cast at 0.3, which opens the wings): the hands settle a degree
    lower and level again, and the head dips a degree. Nothing else."""
    c = ck.Clip("idle_b", IDLE_B_SEC)
    for t, h, hd in ((0.0, 0.0, 0.0), (0.7, 2.5, 1.5), (IDLE_B_SEC, 0.0, 0.0)):
        both_arms(c, t, upper=(-h * 0.4, 0, 0), fore=(h * 0.6, 0, 0), hand=(-h * 0.4, 0, 0))
        torso(c, t, head=hd)
    return still(c)


def build_ready() -> ck.Clip:
    c = ck.Clip("ready", READY_SEC)  # the wings open a little; the hands lift level; the halo as it is
    for t, sp, tn, hands in ((0.0, (0, 0), (0, 0), 0.0), (0.55, (14.0, 24.0), (-16.0, -24.0), 1.0),
                             (0.95, (12.0, 21.0), (-14.0, -21.0), 1.0), (READY_SEC, (0, 0), (0, 0), 0.0)):
        wing_pose(c, t, spread=sp, turn=tn, lift=(sp[0] * 0.3, sp[1] * 0.3))
        both_arms(c, t, upper=(-6.0 * hands, 0, 4.0 * hands), fore=(-4.0 * hands, 0, 0), hand=(4.0 * hands, 0, 0))
        torso(c, t, bow=-1.5 * hands, head=1.0 * hands)
    return still(c)


def build_attack() -> ck.Clip:
    """The level press: the right hand rises, palm out to the foes, then presses down. No weapon. In place."""
    c = ck.Clip("attack", ATTACK_SEC)
    for t, up, fo, hd, bow in ((0.0, (0, 0, 0), (0, 0, 0), (0, 0, 0), 0.0),
                               (0.32, (-62.0, 0.0, -8.0), (-62.0, 0.0, 0.0), (-78.0, 0.0, 0.0), -3.0),
                               (0.42, (-66.0, 0.0, -8.0), (-60.0, 0.0, 0.0), (-80.0, 0.0, 0.0), -3.5),
                               (ATTACK_CONTACT, (-30.0, 0.0, -6.0), (-6.0, 0.0, 0.0), (18.0, 0.0, 0.0), 4.0),
                               (0.8, (-24.0, 0.0, -4.0), (-4.0, 0.0, 0.0), (14.0, 0.0, 0.0), 3.0),
                               (ATTACK_SEC, (0, 0, 0), (0, 0, 0), (0, 0, 0), 0.0)):
        arm_pose(c, t, "r", up, fo, hd)
        torso(c, t, bow=bow, head=bow * 0.5)
    return still(c)


def build_cast() -> ck.Clip:
    """Slow and Stop: both hands spread level, palms down, smoothing the water flat; the wings part as he does it."""
    c = ck.Clip("cast", CAST_SEC)
    for t, sw, dn, sp, hd in ((0.0, 0.0, 0.0, (0, 0), 0.0), (0.45, -8.0, -10.0, (10.0, 16.0), 2.0),
                              (CAST_CONTACT, 42.0, 6.0, (18.0, 28.0), -3.0), (1.15, 44.0, 6.0, (17.0, 27.0), -3.0),
                              (CAST_SEC, 0.0, 0.0, (0, 0), 0.0)):
        # sw swings the forearms out round the elbow (level), dn presses them down (+) or lifts them (-)
        both_arms(c, t, upper=(-dn * 0.5, 0.0, sw * 0.35), fore=(dn, sw, 0.0), hand=(-dn * 0.4, 0.0, 0.0))
        wing_pose(c, t, spread=sp, turn=(-sp[0], -sp[1]), lift=(sp[0] * 0.3, sp[1] * 0.3))
        torso(c, t, bow=hd, head=hd * 0.5)
    return still(c)


def build_hit(name: str = "hit", side: float = 1.0, amp: float = 1.0) -> ck.Clip:
    """A small, stiff recoil: the whole figure tips back a few degrees and back 4 cm, the hands jolt; the veil and
    the halo move only with the head. hit_b is authored: the roll to the other side, heavier."""
    c = ck.Clip(name, HIT_SEC)
    for t, s in ((0.0, 0.0), (HIT_PEAK, amp), (0.28, -0.2 * amp), (HIT_SEC, 0.0)):
        torso(c, t, bow=-5.0 * s, lean=-2.5 * s, head=-3.0 * s, z=-0.045 * s, roll=3.0 * s * side)
        both_arms(c, t, upper=(5.0 * s, 0, 0), fore=(-4.0 * s, 0, 0))
        wing_pose(c, t, lift=(3.0 * s, 3.0 * s))  # the screen swings back a little (and its foot stays off the water)
    return still(c)


def build_defend() -> ck.Clip:
    """The wings close in front of him: each pair swings forward round the vertical and the lower leaves fold in."""
    c = ck.Clip("defend", DEFEND_SEC)
    closed = ((12.0, 18.0), (80.0, 70.0), (0.0, 0.0))
    for t, (sp, tn, fd), ar in ((0.0, ((0, 0), (0, 0), (0, 0)), 0.0), (0.3, closed, 1.0), (0.85, closed, 1.0),
                                (DEFEND_SEC, ((0, 0), (0, 0), (0, 0)), 0.0)):
        wing_pose(c, t, spread=sp, turn=tn, fold=fd)
        both_arms(c, t, upper=(-10.0 * ar, 0, -6.0 * ar), fore=(-20.0 * ar, -24.0 * ar, 0), hand=(10.0 * ar, 0, 0))
        torso(c, t, bow=4.0 * ar, head=6.0 * ar)
    return still(c)


def ko_keys(c: ck.Clip, t: float, f: float, droop: float = 1.0, tip: float = 1.0) -> None:
    """f of the way into the kneel: the hips down, the robe settled, the head bowed, the hands lowered, the wings
    folded down and the halo tipped."""
    torso(c, t, bow=14.0 * f, head=16.0 * f, y=-KNEEL * f, z=0.03 * f)
    kneel(c, t, f)
    both_arms(c, t, upper=(14.0 * f, 0, -4.0 * f), fore=(28.0 * f, 0, 0), hand=(18.0 * f, 0, 0))
    if droop >= 1.0:  # the fall: the closed screen slumps, its leaves sliding apart and down
        wing_pose(c, t, spread=(40.0 * f, 48.0 * f), lift=(6.0 * f, 8.0 * f), fold=(10.0 * f, 12.0 * f))
    else:  # the bow (rise, dismiss): the wings stay closed and ride up his back
        wing_pose(c, t, spread=(10.0 * f, 14.0 * f), lift=(3.0 * f, 4.0 * f), hoist=0.3 * f)
    c.key("halo", t, (10.0 * f * tip, 0.0, 9.0 * f * tip))


def build_ko() -> ck.Clip:
    c = ck.Clip("ko", KO_SEC)  # a flinch, then he kneels; the wings fold down, the halo tips
    torso(c, 0.0)
    kneel(c, 0.0, 0.0)
    both_arms(c, 0.0)
    wing_pose(c, 0.0)
    c.key("halo", 0.0)
    torso(c, 0.18, bow=-4.0, head=-3.0, z=-0.03)
    for t, f in ((1.0, 0.75), (1.45, 1.0), (KO_SEC, 1.0)):
        ko_keys(c, t, f)
    return still(c)


def build_victory() -> ck.Clip:
    c = ck.Clip("victory", VICTORY_SEC)  # wings fully open, the hands lowered, utterly still at the end
    for t, sp, hands in ((0.0, (0, 0), 0.0), (0.9, (36.0, 57.0), 1.0), (1.4, (34.0, 54.0), 1.0),
                         (VICTORY_SEC, (34.0, 54.0), 1.0)):
        wing_pose(c, t, spread=sp, turn=(-sp[0] * 0.9, -sp[1] * 0.8), lift=(sp[0] * 0.25, sp[1] * 0.2))
        both_arms(c, t, upper=(16.0 * hands, 0, 6.0 * hands), fore=(40.0 * hands, 0, 0), hand=(10.0 * hands, 0, 0))
        torso(c, t, bow=-2.0 * hands, head=-2.0 * hands)
    return still(c)


def build_rise() -> ck.Clip:
    c = ck.Clip("rise", RISE_SEC)  # from kneeling, wings closed, he stands (in place: the stage lifts him)
    for t, f in ((0.0, 1.0), (0.5, 1.0), (1.9, 0.08), (RISE_SEC, 0.0)):
        ko_keys(c, t, f, droop=0.4, tip=0.0)
    c.key("halo", 0.0)
    c.key("halo", RISE_SEC)
    return still(c)


def build_dismiss() -> ck.Clip:
    c = ck.Clip("dismiss", DISMISS_SEC)  # he kneels again; it ends kneeling (the stage sinks him)
    for t, f in ((0.0, 0.0), (0.2, 0.0), (0.85, 1.0), (DISMISS_SEC, 1.0)):
        ko_keys(c, t, f, droop=0.4, tip=0.0)
    c.key("halo", 0.0)
    c.key("halo", DISMISS_SEC)
    return still(c)


def build_special() -> ck.Clip:
    """Still Water: the wings flung fully open, both hands raised, then pressed down at the contact, where everything
    on the field stops (the VFX's and the battle's own stop). After it he holds, utterly still."""
    c = ck.Clip("special", SPECIAL_SEC)
    for t, sp, up, fo, hd, bow in ((0.0, (0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), 0.0),
                                   (0.95, (36.0, 57.0), (-22.0, 0, 26.0), (-50.0, 30.0, 0), (-20.0, 0, 0), -4.0),
                                   (1.2, (37.0, 58.0), (-24.0, 0, 28.0), (-54.0, 32.0, 0), (-22.0, 0, 0), -4.5),
                                   (SPECIAL_CONTACT, (36.0, 57.0), (8.0, 0, 18.0), (6.0, 18.0, 0), (22.0, 0, 0), 5.0),
                                   (2.05, (36.0, 57.0), (8.0, 0, 18.0), (6.0, 18.0, 0), (22.0, 0, 0), 5.0),
                                   (SPECIAL_SEC, (0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), 0.0)):
        wing_pose(c, t, spread=sp, turn=(-sp[0] * 0.9, -sp[1] * 0.8), lift=(sp[0] * 0.25, sp[1] * 0.2))
        both_arms(c, t, upper=up, fore=fo, hand=hd)
        torso(c, t, bow=bow, head=bow)
    return still(c)


RELEASE_SEC = 3.5  # M3-CRE-647: the held form's release (Ch20), its KO
RELEASE_AWAY = (0.0, 1.4, -0.5)  # where the release carries him (metres: up, and back away from the party)


def build_release() -> ck.Clip:
    """M3-CRE-647, the held form's KO (vowbound.md, the final fight: the widow's goodbye; the ring is the last thing
    to fade). The screen of wings opens all the way, slowly, for the only time not as a rite; his left hand comes
    forward and up, open, the plain copper ring toward her, and holds there; then he rises, up and back, the wings
    open and the head lifted a little, the ringed hand still held out last, nearest her. The veil is not keyed (its
    fall is the cinematic's)."""
    c = ck.Clip("release", RELEASE_SEC)
    for t, sp, reach, hd, bow in ((0.0, (0, 0), 0.0, 0.0, 0.0), (0.8, (24.0, 38.0), 0.5, -1.0, -1.0),
                                  (1.5, (36.0, 57.0), 1.0, -2.0, -2.0), (2.1, (37.0, 58.0), 1.0, -2.0, -2.5),
                                  (2.8, (34.0, 54.0), 1.0, -4.0, -3.0), (RELEASE_SEC, (33.0, 52.0), 1.0, -5.0, -3.0)):
        wing_pose(c, t, spread=sp, turn=(-sp[0] * 0.9, -sp[1] * 0.8), lift=(sp[0] * 0.25, sp[1] * 0.2))
        arm_pose(c, t, "l", upper=(-40.0 * reach, 0.0, 8.0 * reach), fore=(35.0 * reach, 0.0, 0.0),
                 hand=(-10.0 * reach, 0.0, 0.0))  # the ringed hand held out at chest height, toward her
        arm_pose(c, t, "r", upper=(10.0 * reach, 0.0, 6.0 * reach), fore=(16.0 * reach, 0.0, 0.0),
                 hand=(6.0 * reach, 0.0, 0.0))
        torso(c, t, bow=bow, head=hd)
    lx, ly, lz = RELEASE_AWAY
    for t, k in ((0.0, 0.0), (2.1, 0.0), (2.8, 0.4), (RELEASE_SEC, 1.0)):
        c.key("root", t, (0.0, 0.0, 0.0), (lx * k, ly * k, lz * k))
    return still(c)


# M4-CRB-008 (the Act II move pass, docs/kb/plan/act2/bosses/ethren.md §4): one clip per skill on the design sheet.
STOP_SEC, STOP_CONTACT = 1.6, 0.9
STOP_HELD = (0.45, 0.7)  # Hold the Hour: the hand is out and perfectly still through this
STOP_OUT = dict(upper=(-45.0, 0.0, -4.0), fore=(20.0, 0.0, 0.0), hand=(-60.0, 0.0, 0.0))  # the ringed hand held out,
# palm toward the foe, fingers up, at the height of his breast
STOP_CURL = 82.0  # the fingers close at the contact (degrees at each finger group)
WARD_SEC, WARD_CONTACT = 1.6, 0.8


def build_stop() -> ck.Clip:
    """Hold the Hour (Stop on one foe): his left hand, the ringed one, comes up and out, palm toward the foe, and is
    held there perfectly still; nothing else of him moves. At the contact the hand closes, slowly, as if on the
    hour itself (the foe's idle freezes there, presentation); held shut, then it lowers back to the level rest."""
    c = ck.Clip("stop", STOP_SEC)
    out = {k: np.asarray(v) for k, v in STOP_OUT.items()}
    shut = dict(upper=out["upper"] + (-2.0, 0.0, 0.0), fore=out["fore"], hand=out["hand"] + (6.0, 0.0, 0.0))
    for t, pose, curl in ((0.0, None, 0.0), (STOP_HELD[0], out, 0.0), (STOP_HELD[1], out, 0.0),
                          (STOP_CONTACT, shut, 1.0), (1.25, shut, 1.0), (STOP_SEC, None, 0.0)):
        if pose is None:
            arm_pose(c, t, "l")
        else:
            arm_pose(c, t, "l", pose["upper"], pose["fore"], pose["hand"])
        c.key("finger_l0", t, (STOP_CURL * curl, 0.0, 0.0))
        c.key("finger_l1", t, (STOP_CURL * 1.08 * curl, 0.0, 0.0))
    return still(c)


def build_ward() -> ck.Clip:
    """The lacquer screen (the mass ward on every ally): his hands draw in to his breast and the closed wings part;
    then the four leaves swing out and forward round the party's side like a folding screen set down around them,
    and at the contact his arms open wide, palms out, holding it there (a pale gold-edged pane at each ally, VFX);
    held, then the wings fold back behind him."""
    c = ck.Clip("ward", WARD_SEC)
    # (spread, turn, lift, fold) per pair (inner, outer); + lift swings a leaf's free end forward, so the screen
    # curves round in front of the party's side rather than fanning flat behind him as `victory` does
    rest = ((0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0))
    gather = ((8.0, 12.0), (-6.0, -8.0), (3.0, 4.0), (0.0, 0.0))
    swung = ((26.0, 40.0), (24.0, 16.0), (24.0, 30.0), (-8.0, -8.0))
    set_down = ((30.0, 46.0), (30.0, 20.0), (30.0, 36.0), (-10.0, -10.0))
    settle = ((29.0, 45.0), (29.0, 19.0), (29.0, 35.0), (-10.0, -10.0))
    for t, (sp, tn, lf, fd), ar, open_ in ((0.0, rest, 0.0, 0.0), (0.3, gather, 1.0, 0.0), (0.6, swung, 0.6, 0.6),
                                           (WARD_CONTACT, set_down, 0.0, 1.0), (1.15, settle, 0.0, 1.0),
                                           (WARD_SEC, rest, 0.0, 0.0)):
        wing_pose(c, t, spread=sp, turn=tn, lift=lf, fold=fd)
        both_arms(c, t, upper=(-24.0 * ar - 26.0 * open_, 0.0, -8.0 * ar + 36.0 * open_),
                  fore=(-36.0 * ar - 6.0 * open_, -28.0 * ar + 30.0 * open_, 0.0),
                  hand=(10.0 * ar - 30.0 * open_, 0.0, 0.0))
        torso(c, t, bow=2.0 * ar - 2.0 * open_, head=2.0 * ar - 1.0 * open_)
    return still(c)


def idle_first(idle: ck.Clip) -> dict:
    """Idle's first frame as a pose ({bone: (rot, loc)}): every other clip is authored from rest and played from it
    (ck.in_pose), so each one starts (and the one-shots that come back end) exactly where the idle starts."""
    return {b: tuple(np.asarray(v, float) for v in idle.sample(b, 0.0)) for b in idle.keys}


def build_clips() -> list[ck.Clip]:
    """Every clip played from idle's first frame (M4-CRB-008, as Nhoa's M4-CRB-006)."""
    idle = build_idle()
    start = idle_first(idle)
    authored = [build_ready(), build_attack(), build_cast(), build_hit(), build_hit("hit_b", -1.0, ck.HIT_B["amp"]),
                build_defend(), build_ko(), build_victory(), build_rise(), build_dismiss(), build_special(),
                build_idle_b(), build_release(), build_stop(), build_ward()]
    return [idle] + [ck.in_pose(c, c.name, start) for c in authored]


# ---------------------------------------------------------------------------------------------
# A numpy check (no Blender)
# ---------------------------------------------------------------------------------------------
def report(rig: ck.Rig, meshes: list[ck.Mesh], clips: list[ck.Clip]) -> None:
    rest = np.concatenate([m.arrays()["pos"] for m in meshes])
    print(f"triangles: {sum(m.triangle_count for m in meshes)}; vertices {sum(m.count for m in meshes)}; "
          f"bones {len(rig.bones)}")
    print("parts: " + ", ".join(f"{k} {v}" for k, v in PARTS.items()))
    slots: dict[str, int] = {}
    for m in meshes:
        a = m.arrays()
        for i, name in enumerate(m.materials):
            slots[name] = slots.get(name, 0) + int((a["tri_mat"] == i).sum())
    print("slots: " + ", ".join(f"{k} {v}" for k, v in slots.items()))
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)}")
    poser = grounding.Poser(rig, meshes)
    for c in ck.with_variety(clips):
        lows, highs, disp = [], [], []
        for t in grounding.frame_times(c):
            P = poser.vertices(poser.matrices(grounding.pose_at(c, poser.names, t)))
            lows.append(float(P[:, 1].min()))
            highs.append(float(P[:, 1].max()))
            disp.append(float(np.linalg.norm(P - rest, axis=1).mean()))
        print(f"{c.name:8s} {c.length:.2f}s: y {min(lows):+.3f}..{max(highs):.3f}; "
              f"peak {int(np.argmax(disp)) / ck.FPS:.2f}s")


def build() -> tuple[ck.Rig, list[ck.Mesh], list[ck.Clip]]:
    """The rig, the meshes (the figure and the veil) and the clips."""
    rig = build_rig()
    mesh = build_mesh(rig)
    return rig, [mesh, veil(rig)], build_clips()


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true", help="print the triangle count and the clip checks; no export")
    args = ap.parse_args(argv)
    rig, meshes, clips = build()
    if args.report or not args.out:
        report(rig, meshes, clips)
        return
    info = ck.export_creature(meshes[0], rig, clips, args.out, extra_meshes=meshes[1:],
                              extras={"hymn_creature": "ethren"})
    print(f"ethren: {info}")


if __name__ == "__main__":
    main()
