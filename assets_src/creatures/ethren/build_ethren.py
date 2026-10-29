"""Ethren, the Level Saint, Asha's Glimmer Vowbound (M3-CRE-644): docs/kb/art/creatures/vowbound/ethren.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/ethren/build_ethren.py -- --out assets/creatures/ethren/ethren.glb

A winged shrine-figure of lacquer, 3.0 m to the top of his halo: a closed armoured robe of three nested lacquer bells
(they telescope into one another when he kneels, so the robe stays rigid), a cuirass with a split red breastplate, layered
pauldrons, armoured sleeves and gauntlets (the only joints that read as human). Black and deep-red lacquer carry the
bulk; gold leaf is only on the edges (panel rims, the bells' hems, the halo's lip, the gauntlets' knuckle ridges and
the veil's border), so he holds palette.json's 5%-of-frame gold budget. His bound light is inside the shell and shows
only at the seams (the breastplate's split, the waist, the bells' joins, the elbows, the wing hinges) and on the
inner face of the bowl-halo behind his head, steady.

A still, rigid veil covers the whole face and falls to the chest: its own mesh (`ethren_veil`) on its own bone
(`veil`), which no clip keys, so cinematics can drop it later (Ch20's veil-fall is the characters track's). No face
is modelled. Four folded wings of flat lacquer leaves (two leaves each, hinged with a seam of light) hang close
behind him like a closed screen and open only in `ready`, `cast`, `special` and `victory`. A plain copper ring
(laterite toward tortoiseshell, rough, never lit) sits on the left ring finger: the keepsake.

**Built hovering.** The origin is the water point under him and the rest pose floats there: the sole line (the
feet, not modelled under the robe) 0.2 m up, the robe's hem 0.1 m. The stand-in needs no `hover`. Every clip stays
above the water.

Rig (27 bones): `root`, `body` (the hips), `spine_0..2`, `neck`, `head`, `veil`, `halo`, `robe_1`, `robe_2` (the
lower two bells), `arm_l0`, `arm_l1`, `hand_l`, `finger_l0` (index and middle), `finger_l1` (ring and little, the
ring's), `arm_r0`, `arm_r1`, `hand_r`, and `wing_{li,lo,ri,ro}_{0,1}` (+x is `l`; `i` the inner pair, `o` the outer;
`_0` the upper leaf, `_1` the lower).

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
    "laterite": "#A8573A", "tortoiseshell": "#6B3A1E",
}.items()}
RING_COL = ck.mix(PAL["laterite"], PAL["tortoiseshell"], 0.35)  # copper: no copper swatch, the nearest unlit warm metal
SEAM_COL = PAL["gauze_white"]

# ---- the figure (metres, Godot axes, facing +z) -----------------------------------------------
SOLE = 0.2  # the hover: the feet's line under the robe
HEM = 0.1  # the robe's hem
HIP = 1.30
SPINE = [HIP, 1.50, 1.72, 1.95, 2.12]  # body, spine_0, spine_1, spine_2 spans
NECK_TOP = 2.24
HEAD_C = np.array([0.0, 2.33, 0.01])
HEAD_R = (0.105, 0.135, 0.12)
HEAD_TOP = 2.47
HALO_C = np.array([0.0, 2.55, -0.20])  # the bowl's rim plane centre
HALO_R = 0.45  # 0.9 m across: its top is 3.0 m
HALO_DEPTH = 0.10
HALO_TH = 0.016
GOLD_BAND = 0.014  # the gold rim's width on a face
TH = 0.014  # lacquer plate thickness

# the cuirass: (y, half-width, half-depth, depth centre)
CUIRASS = [(1.30, 0.19, 0.15, 0.0), (1.42, 0.205, 0.16, 0.0), (1.55, 0.225, 0.172, 0.005), (1.70, 0.25, 0.185, 0.01),
           (1.84, 0.265, 0.19, 0.01), (1.95, 0.262, 0.182, 0.0), (2.03, 0.238, 0.16, -0.005), (2.08, 0.19, 0.13, -0.01),
           (2.115, 0.12, 0.095, -0.01), (2.125, 0.09, 0.08, -0.01)]
DEPTH_RATIO = 0.82  # a bell's depth to its width
# the robe's three nested bells: (top y, bottom y, top half-width, flare per metre, forward shift at the hem)
BELLS = [(1.38, 0.86, 0.215, 0.26, 0.02), (0.98, 0.48, 0.345, 0.26, 0.05), (0.60, HEM, 0.47, 0.22, 0.08)]
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
LEAF_TH = 0.03
LEAN_DEG = 6.0  # the folded leaves lean back so they clear the robe's flare
WINGS = {"i": (0.05, -0.27, 35.0), "o": (0.11, -0.33, 30.0)}  # inner pair, outer pair (behind it)

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
def slab(G: np.ndarray, N: np.ndarray, th: float, gold: str = "lrtb", wrap: bool = False):
    """`G` (rows, cols, 3) a surface grid whose first and last rows and columns are its border bands, `N` its normals.
    Returns {'face': (P, T, want), 'gold': (P, T, want), 'back': (P, T, want)}: the front face's field, the gold
    (the front face's border bands on the sides in `gold`, 'l' first column, 'r' last, 't' last row, 'b' first, and
    the walls), and the back face. `wrap`: the columns close round (no l/r border or wall)."""
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
    for loop in ring:
        k = len(loop)
        a, b = front[loop], back[loop]
        P = np.vstack([a, b])
        n_seg = k if wrap else k - 1
        tris = []
        for i in range(n_seg):
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
    return rig


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
    segs = 36
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
    # the waist: a band of light where the cuirass goes into the first bell
    seam_ring(mesh, CUIRASS, 1.385, 1.415, 0.004, torso_skin(rig))


def seam_strip(mesh: ck.Mesh, rig: ck.Rig, pts, normal, width, bones, name) -> None:
    pts = np.asarray(pts)
    tan = unit(np.gradient(pts, axis=0))
    n = np.broadcast_to(unit(normal), pts.shape)
    side = unit(np.cross(n, tan))
    P = np.vstack([pts - side * width / 2, pts + side * width / 2])
    k = len(pts)
    T = [(i, k + i, i + 1) for i in range(k - 1)] + [(i + 1, k + i, k + i + 1) for i in range(k - 1)]
    put(mesh, name, P, T, "seam", SEAM_COL, bones, want=np.vstack([n, n]), emission=1.0)


def seam_ring(mesh: ck.Mesh, table, y0: float, y1: float, off: float, bones, segs: int = 36) -> None:
    phis = np.arange(segs) * 2.0 * math.pi / segs
    G, N = loft_grid(table, phis, [y0, y1], off)
    put(mesh, "seams", G.reshape(-1, 3), ck.grid_tris(2, segs, True), "seam", SEAM_COL, bones, want=N.reshape(-1, 3),
        emission=1.0)


def bell_table(k: int):
    top, bot, r0, flare, fwd = BELLS[k]
    r1 = r0 + flare * (top - bot)
    return [(bot, r1, r1 * DEPTH_RATIO, fwd), (top, r0, r0 * DEPTH_RATIO, 0.0)]


def robe(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Three nested bells, each a closed lacquer shell with a gold hem; a ring of light closes each join."""
    segs = 32
    phis = np.arange(segs) * 2.0 * math.pi / segs
    bones = [rig.rigid("body"), rig.rigid("robe_1"), rig.rigid("robe_2")]
    cols = [PAL["lacquer_red_deep"], PAL["lacquer_black"], PAL["lacquer_black"]]
    slots = ["lacquer_red", "lacquer", "lacquer"]
    for k in range(3):
        top, bot = BELLS[k][0], BELLS[k][1]
        table = bell_table(k)
        ys = np.concatenate([[bot, bot + GOLD_BAND], np.linspace(bot + 0.06, top, 5)])
        G, N = loft_grid(table, phis, ys)
        # the outer face, its gold hem band, the inner face
        out_P = (G + N * TH * 0.5).reshape(-1, 3)
        in_P = (G - N * TH * 0.5).reshape(-1, 3)
        T = ck.grid_tris(len(ys), segs, True)
        hem = np.arange(len(T)) < 2 * segs
        Ps, Ts, Ws = subset(out_P, T[~hem], (N.reshape(-1, 3),))
        put(mesh, f"robe_{k}", Ps, Ts, slots[k], cols[k], bones[k], want=Ws)
        Ps, Ts, Ws = subset(out_P, T[hem], (N.reshape(-1, 3),))
        put(mesh, "gold", Ps, Ts, "gold", PAL["gold_leaf"], bones[k], want=Ws)
        put(mesh, f"robe_{k}", in_P, T, "lacquer", PAL["lacquer_black"], bones[k], want=-N.reshape(-1, 3))
        # the hem's edge (gold) and the top's edge
        for row, slot, col, em, up in ((0, "gold", PAL["gold_leaf"], 0.0, -1.0), (len(ys) - 1, None, None, 0.0, 1.0)):
            a = out_P[row * segs:(row + 1) * segs]
            b = in_P[row * segs:(row + 1) * segs]
            if slot is None:  # the top: an annulus of light reaching in to the bell above (or the cuirass)
                inner_table = bell_table(k - 1) if k > 0 else CUIRASS
                b = np.array([ell(inner_table, ph, top, 0.004)[0] for ph in phis])
                slot, col, em = "seam", SEAM_COL, 1.0
            P = np.vstack([a, b])
            Tr = [(i, (i + 1) % segs, segs + i) for i in range(segs)] + \
                [((i + 1) % segs, segs + (i + 1) % segs, segs + i) for i in range(segs)]
            put(mesh, "gold" if slot == "gold" else "seams", P, Tr, slot, col, bones[k],
                want=np.tile([0.0, up, 0.0], (len(P), 1)), emission=em)
    # the light inside the shell: a dim floor of bound light under the robe, seen only from below
    Pd, Td = ck.ellipsoid((0.0, 0.2, 0.06), (0.5, 0.004, 0.42), 2, 24)
    put(mesh, "seams", Pd, Td, "seam", SEAM_COL, bones[2], emission=0.5)


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


def arms(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for side, tag in ((1.0, "l"), (-1.0, "r")):
        s, e, w = (SHOULDER_L, ELBOW_L, WRIST_L) if side > 0 else (mirror(SHOULDER_L), mirror(ELBOW_L), mirror(WRIST_L))
        a0, a1 = rig.rigid(f"arm_{tag}0"), rig.rigid(f"arm_{tag}1")
        up_path = np.array([s + (0, 0.03, 0) + (e - s) * t for t in np.linspace(0.0, 1.0, 6)])
        tube_part(mesh, "arms", up_path, np.linspace(0.078, 0.066, 6), 14, "lacquer", PAL["lacquer_black"], a0)
        fore = np.array([e + (w - e) * t for t in np.linspace(0.04, 1.0, 6)])
        tube_part(mesh, "arms", fore, np.linspace(0.068, 0.056, 6), 14, "lacquer_red", PAL["lacquer_red_deep"], a1)
        P, T = ring_at(e, w - s, 0.07, 0.0065)  # the elbow's seam
        put(mesh, "seams", P, T, "seam", SEAM_COL, rig.blend(f"arm_{tag}0", f"arm_{tag}1", s, w), emission=1.0)
        P, T = ring_at(w - unit(w - e) * 0.012, w - e, 0.058, 0.0075)  # the gold cuff
        put(mesh, "gold", P, T, "gold", PAL["gold_leaf"], a1)
        pauldron(mesh, rig, side, tag, s)
        gauntlet(mesh, rig, side, tag, w)


def pauldron(mesh: ck.Mesh, rig: ck.Rig, side: float, tag: str, s: np.ndarray) -> None:
    """Three lames over the shoulder, each a red band round the arm's axis (outer side), gold-edged at the bottom."""
    axis = unit(np.array([side * 0.25, -1.0, 0.0]))
    outward = unit(np.array([side * 1.0, 0.25, 0.0]))
    fwd = np.cross(axis, outward) * side
    origin = s + np.array([side * -0.02, 0.10, 0.0])
    for k in range(3):
        s0, s1 = 0.03 + 0.075 * k, 0.12 + 0.075 * k
        r0, r1 = 0.13 + 0.012 * k, 0.15 + 0.016 * k
        al = bands(-math.radians(118), math.radians(118), 8, GOLD_BAND / 0.15)
        ss = bands(s0, s1, 2, GOLD_BAND)
        G = np.zeros((len(ss), len(al), 3))
        N = np.zeros_like(G)
        for i, sv in enumerate(ss):
            r = r0 + (r1 - r0) * (sv - s0) / (s1 - s0)
            for j, a in enumerate(al):
                d = outward * math.cos(a) + fwd * math.sin(a)
                G[i, j] = origin + axis * sv + d * r
                N[i, j] = unit(d - axis * 0.35)
        parts = slab(G, N, TH, gold="b")
        put_slab(mesh, "pauldrons", parts, "lacquer_red" if k != 1 else "lacquer",
                 PAL["lacquer_red_deep"] if k != 1 else PAL["lacquer_black"], PAL["lacquer_black"],
                 rig.rigid(f"arm_{tag}0"))
    cap, Tc = ck.ellipsoid(origin + axis * 0.035, (0.13, 0.06, 0.13), 6, 16)
    put(mesh, "pauldrons", cap, Tc, "lacquer_red", PAL["lacquer_red_deep"], rig.rigid(f"arm_{tag}0"))


def gauntlet(mesh: ck.Mesh, rig: ck.Rig, side: float, tag: str, w: np.ndarray) -> None:
    hand = rig.rigid(f"hand_{tag}")
    back, Tb = ck.ellipsoid(w + (0.0, 0.0, 0.055), (0.048, 0.022, 0.06), 6, 12)
    put(mesh, "hands", back, Tb, "lacquer", PAL["lacquer_black"], hand)
    knuckle_y = w[1] - 0.006
    zk = w[2] + 0.1
    # fingers from the thumb's side (toward the midline) out: index, middle, ring, little
    xs = [-0.027, -0.009, 0.009, 0.026]
    lens = [0.105, 0.115, 0.108, 0.088]
    for f in range(4):
        x = w[0] + side * xs[f]
        base = np.array([x, knuckle_y, zk])
        path = ck.bezier([base, base + (0, -0.006, lens[f] * 0.5), base + (0, -0.02, lens[f])], 6)
        if tag == "l":
            bones = rig.rigid("finger_l0") if f < 2 else rig.rigid("finger_l1")
        else:
            bones = hand
        tube_part(mesh, "hands", path, np.linspace(0.0105, 0.0085, 6), 5, "lacquer", PAL["lacquer_black"], bones,
                  squash=0.8, up=(0.0, 1.0, 0.0))
        if tag == "l" and f == 2:  # the copper ring on the ring finger, past the knuckle
            P, T = ring_at(base + (0, -0.0015, 0.026), path[2] - path[0], 0.0122, 0.0032, 18, 6)
            put(mesh, "ring", P, T, "ring", RING_COL, bones)
    thumb = np.array([w[0] - side * 0.04, w[1] - 0.01, w[2] + 0.04])
    path = ck.bezier([thumb, thumb + (-side * 0.02, -0.012, 0.035), thumb + (-side * 0.015, -0.02, 0.07)], 5)
    tube_part(mesh, "hands", path, np.linspace(0.012, 0.009, 5), 7, "lacquer", PAL["lacquer_black"], hand)
    # the gold ridge across the knuckles
    path = np.array([[w[0] + side * x, knuckle_y + 0.012, zk - 0.004] for x in np.linspace(-0.036, 0.035, 6)])
    tube_part(mesh, "gold", path, 0.0055, 6, "gold", PAL["gold_leaf"], hand, up=(0.0, 0.0, 1.0))


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
    P, T = ring_at(np.array([0.0, 2.21, -0.005]), (0, 1, 0), 0.121, 0.007, 28, 6)
    put(mesh, "gold", P, T, "gold", PAL["gold_leaf"], rig.rigid("neck"))
    Pn, Tn = ck.lathe([(0.075, 2.12), (0.07, 2.2), (0.065, 2.26)], 14)
    put(mesh, "collar", Pn, Tn, "lacquer", PAL["lacquer_black"], rig.rigid("neck"))
    Ph, Th = ck.ellipsoid(HEAD_C, HEAD_R, 8, 14)
    put(mesh, "head", Ph, Th, "lacquer", PAL["lacquer_black"], rig.rigid("head"))
    # the crown band the veil hangs from
    P, T = ring_at(np.array([0.0, 2.40, 0.012]), (0, 1, 0.08), 0.1, 0.011, 24, 6)
    put(mesh, "head", P, T, "lacquer_red", PAL["lacquer_red_deep"], rig.rigid("head"))


VEIL = [(1.92, 0.235, 0.30, 0.03), (2.05, 0.205, 0.255, 0.025), (2.17, 0.165, 0.205, 0.02),
        (2.30, 0.132, 0.16, 0.016), (2.36, 0.122, 0.142, 0.013), (2.41, 0.108, 0.122, 0.012)]


def veil_spread(y: float) -> float:
    """How far round the head the veil reaches at height y (radians each side of the front)."""
    return math.radians(float(np.interp(y, [1.92, 2.0, 2.1, 2.2, 2.41], [58.0, 66.0, 84.0, 112.0, 118.0])))


def veil(rig: ck.Rig) -> ck.Mesh:
    """The veil: its own mesh on its own bone, so cinematics can drop it. Gauze, faintly lit from behind, a gold
    border at its hem."""
    m = ck.Mesh("ethren_veil")
    ys = bands(1.92, 2.41, 10, GOLD_BAND)
    u = np.linspace(-1.0, 1.0, 17)
    G = np.zeros((len(ys), len(u), 3))
    N = np.zeros_like(G)
    for i, y in enumerate(ys):
        sp = veil_spread(y)
        for j, uv in enumerate(u):
            G[i, j], N[i, j] = ell(VEIL, uv * sp, y)
    parts = slab(G, N, 0.006, gold="b")
    vb = rig.rigid("veil")
    P, T, W = parts["face"]
    Ps, Ts, Ws = subset(P, T, (W,))
    put(m, "veil", Ps, Ts, "veil", PAL["gauze_white"], vb, want=Ws, emission=1.0)
    P, T, W = parts["back"]
    Ps, Ts, Ws = subset(P, T, (W,))
    put(m, "veil", Ps, Ts, "veil", PAL["gauze_white"], vb, want=Ws, emission=1.0)
    P, T, W = parts["gold"]
    Ps, Ts, Ws = subset(P, T, (W,))
    put(m, "veil_gold", Ps, Ts, "gold", PAL["gold_leaf"], vb, want=Ws)
    return m


def halo(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A shallow bowl behind the head, concave toward it: the inner face lit, the back lacquer, the lip gold."""
    hb = rig.rigid("halo")
    rings, segs = 6, 32
    rho = np.linspace(0.0, HALO_R, rings)
    a = np.arange(segs) * 2.0 * math.pi / segs
    pts, nrm = [], []
    for r in rho:
        z = HALO_C[2] - HALO_DEPTH * (1.0 - (r / HALO_R) ** 2)
        dz = 2.0 * HALO_DEPTH * r / HALO_R ** 2  # the bowl's slope: its inner normal leans in
        for t in a:
            pts.append([HALO_C[0] + r * math.cos(t), HALO_C[1] + r * math.sin(t), z])
            nrm.append(unit([-dz * math.cos(t), -dz * math.sin(t), 1.0]))
    G = np.array(pts)
    N = np.array(nrm)
    T = ck.grid_tris(rings, segs, True)
    put(mesh, "halo", G + N * 0.002, T, "halo", SEAM_COL, hb, want=N, emission=1.0)
    put(mesh, "halo", G - N * HALO_TH, T, "lacquer", PAL["lacquer_black"], hb, want=-N)
    P, T = ring_at(HALO_C, (0, 0, 1), HALO_R, 0.013, 48, 6)
    put(mesh, "gold", P, T, "gold", PAL["gold_leaf"], hb)


def leaf_outline(lower: bool) -> tuple[np.ndarray, np.ndarray]:
    """(across, down) stations of one leaf: straight sides, a cusped point at its free end (the top of the upper
    leaf, the bottom of the lower), the lower leaf narrowing a little."""
    us = bands(0.0, 1.0, 4, GOLD_BAND / LEAF_W)
    vs = bands(0.0, LEAF_LEN, 6, GOLD_BAND)
    return us, vs


def leaf(rig: ck.Rig, tag: str, lower: bool):
    pivot, top, down, across, normal = leaf_frame(tag)
    us, vs = leaf_outline(lower)
    start = top + down * ((LEAF_LEN + LEAF_GAP) if lower else 0.0)
    G = np.zeros((len(vs), len(us), 3))
    for i, v in enumerate(vs):
        f = v / LEAF_LEN  # 0 at the leaf's top, 1 at its bottom
        width = LEAF_W * ((1.0 - 0.14 * f) if lower else 1.0)
        # the free end's cusp: the leaf's middle reaches further than its edges (an ogee point)
        for j, u in enumerate(us):
            point = 1.0 - (2.0 * u - 1.0) ** 2  # 1 mid-leaf, 0 at the edges
            if lower:
                dv = 0.09 * point * ck.smoothstep(0.82, 1.0, f) if f > 0.82 else 0.0
                off = v + dv
            else:
                dv = 0.11 * point * ck.smoothstep(0.18, 0.0, f) if f < 0.18 else 0.0
                off = v - dv
            G[i, j] = start + down * off + across * (u * width)
    N = np.broadcast_to(normal, G.shape).copy()
    return G, N


def wings(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for tag in ("li", "lo", "ri", "ro"):
        for lower in (False, True):
            G, N = leaf(rig, tag, lower)
            parts = slab(G, N, LEAF_TH)
            bone = rig.rigid(f"wing_{tag}_{1 if lower else 0}")
            # the outer face black with a red field inset; the inner face red
            pivot, top, down, across, normal = leaf_frame(tag)

            def field(Ps, top=top, down=down, across=across, lower=lower):
                rel = Ps - top
                u = (rel @ across) / LEAF_W
                v = (rel @ down) - ((LEAF_LEN + LEAF_GAP) if lower else 0.0)
                inset = (u > 0.16) & (u < 0.84) & (v > 0.16) & (v < LEAF_LEN - 0.16)
                return np.where(inset[:, None], PAL["lacquer_red_deep"], PAL["lacquer_black"])

            put_slab(mesh, "wings", parts, "lacquer", field, PAL["lacquer_red_deep"], bone, back_slot="lacquer_red")
        # the hinge between the leaves: a bar of light; the pivot's boss
        pivot, top, down, across, normal = leaf_frame(tag)
        joint = top + down * (LEAF_LEN + LEAF_GAP * 0.5)
        path = np.array([joint + across * LEAF_W * u for u in np.linspace(0.03, 0.97, 5)])
        tube_part(mesh, "seams", path, 0.011, 6, "seam", SEAM_COL, rig.rigid(f"wing_{tag}_0"), up=tuple(normal),
                  em=1.0)
        Pb, Tb = ck.ellipsoid(pivot + normal * 0.01, (0.03, 0.03, 0.03), 4, 8)
        put(mesh, "seams", Pb, Tb, "seam", SEAM_COL, rig.rigid(f"wing_{tag}_0"), emission=1.0)
    # the yoke the wings hang from, across the upper back
    path = np.array([[x, PIVOT_Y + 0.01, -0.2 - 0.05 * (1.0 - abs(x) / 0.2)] for x in np.linspace(-0.2, 0.2, 7)])
    tube_part(mesh, "wings", path, 0.035, 10, "lacquer", PAL["lacquer_black"], rig.rigid("spine_2"), squash=0.7)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    PARTS.clear()
    mesh = ck.Mesh("ethren")
    cuirass(mesh, rig)
    robe(mesh, rig)
    arms(mesh, rig)
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
KNEEL = 0.45  # how far the hips sink when he kneels; the bells telescope
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
    """f of the way down: the hips sink KNEEL and the two lower bells part of it, so the robe telescopes."""
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
        wing_pose(c, t, lift=(2.0 * s, 2.0 * s))
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
    """f of the way into the kneel: the hips down, the bells telescoped, the head bowed, the hands lowered, the wings
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


def build_clips() -> list[ck.Clip]:
    return [build_idle(), build_ready(), build_attack(), build_cast(), build_hit(),
            build_hit("hit_b", -1.0, ck.HIT_B["amp"]), build_defend(), build_ko(), build_victory(), build_rise(),
            build_dismiss(), build_special(), build_idle_b(), build_release()]


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
