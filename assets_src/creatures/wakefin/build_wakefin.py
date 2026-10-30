"""The Wakefin, the Ch15 boss (M3-CRE-626): docs/kb/art/creatures/act2/wakefin.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/wakefin/build_wakefin.py -- \
    --out assets/creatures/wakefin/wakefin.glb

Undertow-spawn drawn by the first wake in four hundred years: a long, black, sail-finned fish 6.0 m from the tail
fork's tips to the bill's point, with a sailfish's shape and its one exaggeration, the dorsal sail grown into a tall
swept blade standing 2.2 m above the water. Wet `lacquer_black` lifted toward `abyss_navy` and `deep_teal_shadow`
(clearcoat-wet), faint sailfish bars on the flanks, the blade's membrane `deep_teal_shadow` low down where the
sea-glow lights it from below. A `sea_glow` seam runs along each flank (its own slot, emission in the sea's own
light, not glimmer), and eight `spawn_wound` wounds run along the spine either side of the blade's root and behind
it to the tail (the weak points, on the body slot's emission mask).

**The waterline.** The battle floor, y 0, is the water's surface. The body hangs below it: the spine axis (the root
bone) sits at y -0.38, the back's own height under the blade's front root, so the waterline falls where the blade
meets the back (measured over the idle: its base row's front half at y -0.02..+0.06). In battle the fish is mostly
that blade; it breaches on the attack.

Rig (20 bones): root (the pivot at the body's centre), head, `spine_0`..`spine_9` (head to tail), `bill`, the
blade's three height bones `fin_0`..`fin_2` (each hinges along the back's line, so the blade leans, curls and flops
without tearing its root), `pec_l`/`pec_r` and `tail_upper`/`tail_lower`.

Run without Blender (`python3 build_wakefin.py --report`) to print the triangle count and, per clip, the skinned
bounds, the blade's top and base, and the peak time (numpy skinning, no export).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
import creature_kit as ck  # noqa: E402

SEED = 6261
PAL = {k: ck.hexrgb(v) for k, v in {
    "lacquer_black": "#1D1916", "abyss_navy": "#061A2B", "deep_teal_shadow": "#0E4A55", "sea_glow": "#1C6B78",
    "spawn_wound": "#3FE0C8", "glimmer_held": "#7FC6D9",
}.items()}
# The body's black: lacquer_black toward abyss_navy, lifted by deep_teal_shadow so it stays on the palette's albedo
# floor (abyss_navy alone is a shade under it).
NAVY = ck.mix(ck.mix(PAL["lacquer_black"], PAL["abyss_navy"], 0.5), PAL["deep_teal_shadow"], 0.14)
BLACK = PAL["lacquer_black"]

AXIS_Y = -0.38  # the spine axis: the back under the blade's front root at the waterline (y 0)
ROOT_Z = 0.2  # the root's pivot: the body's centre of mass
SNOUT_Z = 2.04
TAIL_Z = -2.62  # the peduncle's end, where the lobes leave it
BILL_TIP_Z = 3.0
LOBE_TIP_Z = -3.0  # 6.0 m from the lobes' tips to the bill's point
# Section half-extents along z: dorsal (du), ventral (dv), lateral (w). Deepest under the blade's front.
SEC_Z = [TAIL_Z, -2.4, -2.0, -1.5, -0.9, -0.3, 0.3, 0.9, 1.3, 1.6, 1.82, 1.96, SNOUT_Z]
SEC_DU = [0.065, 0.085, 0.14, 0.22, 0.30, 0.36, 0.385, 0.375, 0.33, 0.25, 0.16, 0.09, 0.04]
SEC_DV = [0.065, 0.085, 0.15, 0.24, 0.33, 0.39, 0.41, 0.385, 0.33, 0.24, 0.15, 0.08, 0.035]
SEC_W = [0.045, 0.06, 0.09, 0.13, 0.165, 0.19, 0.2, 0.19, 0.17, 0.14, 0.1, 0.065, 0.03]
SEGS = 32  # around the body
SPINE_Z = [1.6, 1.15, 0.7, 0.25, -0.2, -0.65, -1.05, -1.45, -1.8, -2.15, -2.48]  # ten bones between them
SPINE = [f"spine_{i}" for i in range(10)]
FIN = ("fin_0", "fin_1", "fin_2")
# The blade's outline (z, y) from its front root up the leading edge to the tip, then down the swept trailing edge
# and back low along the body to its rear root. The tip stands 2.22 m above the water.
FIN_FRONT_Z, FIN_REAR_Z = 1.2, -1.55
FIN_OUTLINE = [(FIN_FRONT_Z, None), (1.08, 0.55), (0.86, 1.15), (0.55, 1.68), (0.18, 2.05), (-0.12, 2.22),
               (-0.3, 2.05), (-0.4, 1.6), (-0.52, 1.1), (-0.72, 0.68), (-1.0, 0.4), (-1.3, 0.24), (FIN_REAR_Z, None)]
FIN_TIP_U = 0.3  # the ray that reaches the tip leaves the back 30% of the way along the root
FIN_J = np.array([(0.0, 0.0, 0.32), (0.0, 0.78, 0.12), (0.0, 1.5, -0.04), (0.0, 2.22, -0.12)])  # the height chain
FIN_RAYS, FIN_ROWS = 46, 12
# M4-CRB-004: the tear line across the blade's top (the close circle's torn tip): a triangle whose centre lies above
# TEAR_Y (plus a ragged wobble along z) belongs to the `BladeTip` mesh; TIP_J is the blade_tip bone (head, tail).
TEAR_Y = 1.74
TIP_J = ((0.0, TEAR_Y, -0.07), (0.0, 2.22, -0.12))
# The sea-glow on the blade where it cuts the water: the first rows of the blade, in the seam slot (the glow it
# stirs, wet on its base; the seam's own light, not glimmer)
FIN_GLOW_ROWS = 2
SEAM_K = (1, 2)  # the seam band: between these section rows on the right flank (mirrored on the left)
SEAM_Z = (-2.38, 1.36)
# Wounds along the spine: (z, side, half-length), high on the flank either side of the ridge. M3-CRE-635: longer and
# wider open seams that wander across the rows (one barely showed in the first render)
WOUNDS = ((1.38, 1, 0.18), (0.95, -1, 0.23), (0.45, 1, 0.27), (-0.15, -1, 0.27), (-0.75, 1, 0.25), (-1.3, -1, 0.21),
          (-1.78, 1, 0.17), (-2.12, -1, 0.12))
WOUND_K = 7  # the section row (from the lateral line) the wounds lie on: 78.75 degrees, beside the ridge
WOUND_W = 0.85  # the open seam's half-width, in section rows (the lips' is 2.6 times it)
WOUND_WANDER = 0.75  # how far a seam wanders off its row, in section rows

PARTS: dict[str, tuple[int, int]] = {}  # part name -> vertex range, for the report


def section(z):
    return np.interp(z, SEC_Z, SEC_DU), np.interp(z, SEC_Z, SEC_DV), np.interp(z, SEC_Z, SEC_W)


def back_y(z) -> np.ndarray:
    return AXIS_Y + np.interp(z, SEC_Z, SEC_DU)


def orient(P: np.ndarray, T: np.ndarray, want) -> np.ndarray:
    """Flips the triangles whose face normal points against want(centroids)."""
    T = np.asarray(T, dtype=np.int64).copy()
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    bad = (fn * want(P[T].mean(axis=1))).sum(axis=1) < 0
    T[bad] = T[bad][:, ::-1]
    return T


def mark(name: str, mesh: ck.Mesh, start: int) -> None:
    lo, hi = PARTS.get(name, (start, start))
    PARTS[name] = (min(lo, start), mesh.count)


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def build_rig() -> ck.Rig:
    rig = ck.Rig()
    # M4-CRB-004: the fish's travel across the water (the intro's long pass, the strikes' reach toward the barge, the
    # close circle, the KO's drift) runs on `breach`, a root at the surface under the body's centre; the body's rise,
    # dive and roll run on `root` under it, so the mesh never moves the spine to travel.
    rig.add("breach", (0, 0.0, ROOT_Z), (0, 0.3, ROOT_Z))
    rig.add("root", (0, AXIS_Y, ROOT_Z), (0, AXIS_Y + 0.3, ROOT_Z), "breach")
    rig.add("head", (0, AXIS_Y, SPINE_Z[0]), (0, AXIS_Y, 1.95), "root")
    rig.add("bill", (0, AXIS_Y + 0.02, 1.95), (0, AXIS_Y + 0.04, BILL_TIP_Z), "head")
    parent = "root"
    for i, name in enumerate(SPINE):
        rig.add(name, (0, AXIS_Y, SPINE_Z[i]), (0, AXIS_Y, SPINE_Z[i + 1]), parent)
        parent = name
    base = FIN_J[0] + np.array([0.0, float(back_y(FIN_J[0][2])), 0.0])
    pts = [base] + [p for p in FIN_J[1:]]
    rig.add("fin_0", pts[0], pts[1], "spine_2")
    rig.add("fin_1", pts[1], pts[2], "fin_0")
    rig.add("fin_2", pts[2], pts[3], "fin_1")
    for side, name in ((1.0, "pec_l"), (-1.0, "pec_r")):
        a, tip = pec_points(side)
        rig.add(name, a, tip, "spine_0")
    root = np.array([0.0, AXIS_Y, -2.5])
    rig.add("tail_upper", root, (0.0, AXIS_Y + 0.9, LOBE_TIP_Z), "spine_9")
    rig.add("tail_lower", root, (0.0, AXIS_Y - 0.85, LOBE_TIP_Z + 0.02), "spine_9")
    # M4-CRB-004: the blade's tip above the tear line rides its own bone (it follows fin_2 until `phase_close` tears it
    # off on the hull and flings it into the sea; the `BladeTip` mesh is then hidden)
    rig.add("blade_tip", TIP_J[0], TIP_J[1], "fin_2")
    # VFX anchors (unweighted): the third spine wound, the centre of mass, the blade's base
    pw, nw = wound_anchor()
    rig.add("vfx_wound", pw, pw + nw * 0.2, "spine_2")
    rig.add("vfx_core", (0.0, AXIS_Y, ROOT_Z), (0.0, AXIS_Y + 0.25, ROOT_Z), "spine_3")
    rig.add("vfx_phase", pts[0], pts[0] + np.array([0.0, 0.25, 0.0]), "fin_0")
    return rig


def wound_anchor() -> tuple[np.ndarray, np.ndarray]:
    """The third spine wound's centre on the body's surface (its row beside the ridge) and its outward normal."""
    z0, side, _half = WOUNDS[2]
    du, _dv, w = (float(v) for v in section(z0))
    a = WOUND_K * 2.0 * math.pi / SEGS
    ca, sa = math.cos(a), math.sin(a)
    p = np.array([side * w * ca ** 0.85, AXIS_Y + du * sa, z0])
    n = np.array([side * ca / max(w, 1e-6), sa / max(du, 1e-6), 0.0])
    return p, n / np.linalg.norm(n)


def body_skin(rig: ck.Rig):
    names = ["head"] + SPINE
    pts = np.array([(0.0, AXIS_Y, z) for z in [SNOUT_Z] + SPINE_Z])
    chain = rig.chain(names, pts)

    def f(P):
        Q = np.column_stack([np.zeros(len(P)), np.full(len(P), AXIS_Y), P[:, 2]])  # by the axis, not the surface
        return chain(Q)

    return f


def pec_points(side: float) -> tuple[np.ndarray, np.ndarray]:
    z = 1.3
    _du, dv, w = (float(v) for v in section(z))
    a = np.array([side * w * 0.82, AXIS_Y - dv * 0.42, z])
    return a, a + np.array([side * 0.3, -0.3, -0.62])


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def ring_z() -> np.ndarray:
    """Rings along the body: finer on the head and round the blade's root."""
    out = [TAIL_Z]
    z = TAIL_Z
    while True:
        step = 0.05 if z < -1.8 else (0.045 if z < 1.25 else 0.03)
        z += step
        if z >= SNOUT_Z - 0.01:
            break
        out.append(z)
    out.append(SNOUT_Z)
    return np.asarray(out)


def body(mesh: ck.Mesh, rig: ck.Rig) -> None:
    zs = ring_z()
    K = len(zs)
    du, dv, w = section(zs)
    a = np.arange(SEGS) * (2.0 * math.pi / SEGS)
    ca, sa = np.cos(a), np.sin(a)
    X = np.sign(ca) * np.abs(ca) ** 0.85
    ext = np.where(sa[None] >= 0, du[:, None], dv[:, None]) * sa[None]
    P = np.zeros((K, SEGS, 3))
    P[..., 0] = w[:, None] * X[None]
    P[..., 1] = AXIS_Y + ext
    P[..., 2] = zs[:, None]
    P = P.reshape(-1, 3)
    T = ck.grid_tris(K, SEGS, True)
    zv = np.repeat(zs, SEGS)
    sav = np.tile(sa, K)
    kv = np.tile(np.arange(SEGS), K)
    side = np.sign(np.tile(ca, K) + 1e-9)
    # caps: the peduncle's end (hidden in the lobes' root) and the snout's point (the bill grows from it)
    P = np.vstack([P, [(0.0, AXIS_Y, TAIL_Z - 0.03), (0.0, AXIS_Y + 0.005, SNOUT_Z + 0.02)]])
    caps = [(s, (s + 1) % SEGS, len(P) - 2) for s in range(SEGS)]
    r0 = (K - 1) * SEGS
    caps += [(r0 + s, r0 + (s + 1) % SEGS, len(P) - 1) for s in range(SEGS)]
    T = np.vstack([T, np.asarray(caps, dtype=np.int64)])
    zv = np.concatenate([zv, [TAIL_Z - 0.03, SNOUT_Z + 0.02]])
    sav, kv, side = (np.concatenate([v, [0.0, 0.0]]) for v in (sav, kv, side))
    axis = lambda c: c - np.column_stack([np.zeros(len(c)), np.full(len(c), AXIS_Y), np.clip(c[:, 2], TAIL_Z, SNOUT_Z)])  # noqa: E731
    T = orient(P, T, axis)
    N = ck.weld_normals(P, ck.vertex_normals(P, T))

    # wounds along the spine: slits on the row beside the ridge, their lips raised
    ang = np.where(side > 0, kv, (SEGS // 2 - kv) % SEGS)  # the row index measured from the lateral line, per side
    ang = np.where(ang > SEGS // 2, ang - SEGS, ang).astype(np.float64)
    slit = np.zeros(len(P))
    lip = np.zeros(len(P))
    for i, (z0, s, half) in enumerate(WOUNDS):
        along = (zv - z0) / half
        row = WOUND_K + WOUND_WANDER * np.sin(along * 2.6 + i * 1.7)  # a torn seam, not a cut line
        win = ck.smoothstep(1.0, 0.6, np.abs(along)) * (side == s)
        slit = np.maximum(slit, win * np.exp(-((ang - row) / WOUND_W) ** 2))
        lip = np.maximum(lip, ck.smoothstep(1.4, 0.6, np.abs(along)) * (side == s)
                         * np.exp(-((ang - row) / (2.6 * WOUND_W)) ** 2))
    lip = lip * (1.0 - slit)
    # the gill cover's edge and the mouth's line on the head
    gill = np.exp(-((zv - (1.42 + 0.06 * sav ** 2)) / 0.02) ** 2) * ck.smoothstep(0.85, 0.5, np.abs(sav))
    mouth = np.exp(-((sav + 0.32) / 0.09) ** 2) * ck.smoothstep(1.66, 1.8, zv)
    rough = ck.fbm(P * 7.0, SEED + 1) * 0.004
    disp = rough - 0.03 * slit + 0.012 * lip - 0.008 * gill - 0.006 * mouth
    P = P + N * disp[:, None]

    # colour: the back lacquer black, the flanks and belly lifted toward navy, faint sailfish bars on the flanks
    up = ck.smoothstep(-0.6, 0.85, sav)
    col = ck.mix(NAVY, BLACK, up[:, None])
    flank = ck.smoothstep(0.75, 0.15, np.abs(sav)) * ck.smoothstep(-1.9, -1.2, zv) * ck.smoothstep(1.4, 1.0, zv)
    bars = ck.smoothstep(0.55, 0.95, np.sin(zv * 2 * math.pi / 0.3 + 0.8 * ck.fbm(P * 2.0, SEED + 2))) * flank
    col = ck.mix(col, PAL["deep_teal_shadow"] * 0.55 + NAVY * 0.45, (0.45 * bars)[:, None])
    belly = ck.smoothstep(-0.55, -0.9, sav)
    col = ck.mix(col, PAL["deep_teal_shadow"] * 0.45 + NAVY * 0.55, (0.5 * belly)[:, None])
    col = ck.mix(col, BLACK, (0.6 * gill + 0.7 * mouth)[:, None])
    col = ck.mix(col, BLACK * 0.5 + PAL["glimmer_held"] * 0.1 + NAVY * 0.4, (0.6 * lip)[:, None])
    col = ck.mix(col, PAL["spawn_wound"] * 0.8, slit[:, None])
    wet = np.full(len(P), 1.0)
    cavity = np.clip(0.8 * slit + 0.35 * lip + 0.6 * gill + 0.5 * mouth, 0.0, 1.0)

    # the sea-glow seam: one band of the body's quads along each flank, in its own slot
    seam_k = np.isin(kv, SEAM_K) | np.isin(kv, [SEGS // 2 - k for k in SEAM_K])
    in_z = (zv >= SEAM_Z[0]) & (zv <= SEAM_Z[1])
    tri_seam = (seam_k & in_z)[T].all(axis=1)
    # a band is the quads whose four corners sit on the seam's two rows (on one side)
    tri_seam &= (side[T] == side[T][:, :1]).all(axis=1)
    taper = ck.smoothstep(SEAM_Z[0], SEAM_Z[0] + 0.5, zv) * ck.smoothstep(SEAM_Z[1], SEAM_Z[1] - 0.35, zv)
    seam_col = ck.mix(PAL["deep_teal_shadow"], PAL["sea_glow"], (0.4 + 0.6 * taper)[:, None])
    skin = body_skin(rig)
    glow = np.clip(slit + 0.2 * lip, 0.0, 1.0)  # the seams' light, spilling a little onto their lips
    for name, tri_mask, c, e, slot in (("body", ~tri_seam, col, glow, "body"),
                                      ("seam", tri_seam, seam_col, 0.25 + 0.75 * taper, "seam")):
        Ts = T[tri_mask]
        used = np.unique(Ts)
        remap = np.full(len(P), -1, dtype=np.int64)
        remap[used] = np.arange(len(used))
        start = mesh.count
        ee = np.broadcast_to(np.asarray(e, dtype=np.float64), (len(P),))[used]
        ck.finish(mesh, P[used], remap[Ts], slot, c[used], skin, wet=wet[used], cavity=cavity[used], emission=ee,
                  N=N[used])
        mark(name, mesh, start)


def bill(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The bill: a long round spear from the upper jaw, a little lifted at its point."""
    n = 26
    u = np.linspace(0.0, 1.0, n)
    z = 1.86 + (BILL_TIP_Z - 1.86) * u
    path = np.column_stack([np.zeros(n), AXIS_Y + 0.012 + 0.03 * u ** 2, z])
    r = 0.052 * (1.0 - u) ** 0.85 + 0.004
    P, T = ck.tube(path, r, 10, cap_start=False, cap_end=True, up_hint=(0.0, 1.0, 0.0), squash=0.85)
    uu = np.concatenate([np.repeat(u, 10), [1.0]])
    col = ck.mix(BLACK, NAVY, (0.35 * ck.smoothstep(0.1, 0.9, uu))[:, None])
    start = mesh.count
    ck.finish(mesh, P, T, "body", col, rig.blend("head", "bill", (0, AXIS_Y, 1.95), (0, AXIS_Y, 2.12)), wet=0.9,
              cavity=0.1)
    mark("bill", mesh, start)


def eyes(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for side in (1.0, -1.0):
        z = 1.72
        _du, _dv, w = (float(v) for v in section(z))
        c = np.array([side * (w - 0.022), AXIS_Y + 0.045, z])
        P, T = ck.ellipsoid((0, 0, 0), (1.0, 1.0, 1.0), 6, 12)
        cosp = P[:, 1].copy()
        R = np.array([[0.0, side, 0.0], [-side, 0.0, 0.0], [0.0, 0.0, 1.0]])  # +y to the side
        P = P * 0.05 @ R.T + c
        iris = ck.smoothstep(0.55, 0.72, cosp)
        pupil = ck.smoothstep(0.84, 0.9, cosp)
        col = ck.mix(BLACK, PAL["deep_teal_shadow"], (0.7 * iris)[:, None])
        col = ck.mix(col, BLACK, pupil[:, None])
        start = mesh.count
        ck.finish(mesh, P, T, "eye", col, rig.rigid("head"), wet=1.0)
        mark("eye", mesh, start)


def outline() -> np.ndarray:
    """The blade's outline as a dense polyline (z, y), front root to rear root (Catmull-Rom through the points)."""
    pts = np.array([(z, float(back_y(z)) - 0.02 if y is None else y) for z, y in FIN_OUTLINE])
    ext = np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]])
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        for t in np.linspace(0.0, 1.0, 24, endpoint=False):
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-1])
    return np.asarray(out)


def fin_skin(rig: ck.Rig):
    """The blade: by height along its chain (fin_0 low, fin_1, fin_2 at the tip), and near its root on the spine
    bone under it, so the root never leaves the back."""
    chain = rig.chain(list(FIN), np.vstack([[0.0, float(back_y(FIN_J[0][2])), FIN_J[0][2]], FIN_J[1:]]))
    spine = body_skin(rig)

    def f(P):
        J, W = chain(np.column_stack([np.zeros(len(P)), P[:, 1], np.full(len(P), FIN_J[1][2])]))  # by height
        Js, _Ws = spine(P)
        h = P[:, 1] - back_y(P[:, 2])
        s = ck.smoothstep(0.02, 0.4, h)
        low = h < 0.4
        J = J.copy()
        W = W.copy()
        J[low] = np.column_stack([Js[low, 0], np.full(int(low.sum()), rig.index("fin_0"))])
        W[low] = np.column_stack([1.0 - s[low], s[low]])
        return J, W

    return f


def subset(T: np.ndarray, mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The vertices the masked triangles use, and those triangles re-indexed onto them."""
    Ts = T[mask]
    used = np.unique(Ts)
    remap = np.full(int(T.max()) + 1, -1, dtype=np.int64)
    remap[used] = np.arange(len(used))
    return used, remap[Ts]


def tear_y(z) -> np.ndarray:
    """The torn tip's line: TEAR_Y with a ragged wobble along the blade."""
    return TEAR_Y + 0.05 * np.sin(np.asarray(z) * 29.0) + 0.035 * np.sin(np.asarray(z) * 61.0 + 1.3)


def blade(mesh: ck.Mesh, rig: ck.Rig, tip: ck.Mesh | None = None) -> None:
    """The dorsal blade: rays fanned from its root along the back to its outline, two faces a little apart.
    M4-CRB-004: its first row is wet with the sea-glow it stirs (seam slot), and its top above the tear line is the
    `tip` mesh on the blade_tip bone (the close circle tears it off)."""
    ol = outline()
    seg = np.linalg.norm(np.diff(ol, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)]) / seg.sum()
    tip_s = float(s[np.argmax(ol[:, 1])])
    u = np.linspace(0.0, 1.0, FIN_RAYS)
    su = np.where(u <= FIN_TIP_U, u / FIN_TIP_U * tip_s, tip_s + (u - FIN_TIP_U) / (1 - FIN_TIP_U) * (1 - tip_s))
    edge = np.column_stack([np.interp(su, s, ol[:, 0]), np.interp(su, s, ol[:, 1])])
    bz = FIN_FRONT_Z + (FIN_REAR_Z - FIN_FRONT_Z) * u
    base = np.column_stack([bz, back_y(bz) - 0.02])
    # a soft scallop between the rays, deeper on the trailing edge, and one old notch near the tip
    sc = 1.0 - 0.035 * np.abs(np.sin(math.pi * u * (FIN_RAYS - 1) / 2.0)) * (0.4 + 0.6 * u)
    notch = 1.0 - 0.07 * np.exp(-((u - 0.4) / 0.018) ** 2)
    edge = base + (edge - base) * (sc * notch)[:, None]
    v = np.linspace(0.0, 1.0, FIN_ROWS)
    grid = base[:, None, :] + (edge - base)[:, None, :] * (v ** 0.9)[None, :, None]  # (rays, rows, (z, y))
    zz, yy = grid[..., 0].reshape(-1), grid[..., 1].reshape(-1)
    uu, vv = np.repeat(u, FIN_ROWS), np.tile(v, FIN_RAYS)
    height = yy - back_y(zz)
    ray = ck.smoothstep(0.55, 1.0, np.abs(np.cos(math.pi * uu * (FIN_RAYS - 1) / 2.0))) * (1.0 - 0.6 * vv)
    th = 0.03 * (1.0 - vv) ** 1.5 + 0.004 + 0.004 * ray
    # membrane: deep teal low down, where the sea-glow lights it from below, to black at the top; rays black
    lit = ck.smoothstep(1.3, 0.1, height)
    col = ck.mix(BLACK, PAL["deep_teal_shadow"] * 0.7 + NAVY * 0.3, (0.75 * lit)[:, None])
    col = ck.mix(col, BLACK, (0.7 * ray)[:, None])
    edge_band = ck.smoothstep(0.9, 1.0, vv)
    col = ck.mix(col, NAVY, (0.4 * edge_band)[:, None])
    T = ck.grid_tris(FIN_RAYS, FIN_ROWS, False)
    row = np.tile(np.arange(FIN_ROWS), FIN_RAYS)
    glow = ck.smoothstep(float(v[FIN_GLOW_ROWS - 1]), 0.0, vv)  # 1 at the waterline, 0 a row up
    glow_col = ck.mix(PAL["deep_teal_shadow"] * 0.6 + NAVY * 0.4, PAL["sea_glow"], (0.75 * glow)[:, None])
    cav = 0.35 * ray + 0.2 * (1.0 - vv) ** 3
    skin = fin_skin(rig)
    for side in (1.0, -1.0):
        P = np.column_stack([side * th * 0.5, yy, zz])
        Ts = orient(P, T, lambda c, sd=side: np.tile([sd, 0.0, 0.0], (len(c), 1)))
        cen = P[Ts].mean(axis=1)
        is_tip = (cen[:, 1] > tear_y(cen[:, 2])) if tip is not None else np.zeros(len(Ts), dtype=bool)
        is_glow = (row[Ts].max(axis=1) <= FIN_GLOW_ROWS - 1) & ~is_tip
        for part, m, mask, slot, c, e, bones in (
            ("fin", mesh, ~is_tip & ~is_glow, "fin", col, 0.0, skin),
            ("fin_glow", mesh, is_glow, "seam", glow_col, 0.6 * glow, skin),
            ("fin_tip", tip, is_tip, "fin", col, 0.0, None),
        ):
            if m is None or not mask.any():
                continue
            used, Tm = subset(Ts, mask)
            ee = np.broadcast_to(np.asarray(e, dtype=np.float64), (len(P),))[used]
            start = m.count
            ck.finish(m, P[used], Tm, slot, c[used], bones if bones is not None else rig.rigid("blade_tip"),
                      wet=0.85, cavity=cav[used], emission=ee)
            if m is mesh:
                mark("fin", m, start)


def lobe(mesh: ck.Mesh, rig: ck.Rig, upper: bool) -> None:
    """A tail lobe: a swept sickle, a flattened tube thinning to its tip."""
    sgn = 1.0 if upper else -1.0
    root = np.array([0.0, AXIS_Y, -2.5])
    tip = np.array([0.0, AXIS_Y + sgn * (0.92 if upper else 0.86), LOBE_TIP_Z + (0.0 if upper else 0.02)])
    path = ck.bezier([root, root + (0.0, sgn * 0.22, -0.12), tip + (0.0, -sgn * 0.3, 0.22), tip], 14)
    u = np.linspace(0.0, 1.0, 14)
    chord = 0.13 * (1.0 - u) ** 0.7 + 0.008
    chord[0] = 0.07
    P, T = ck.tube(path, chord, 10, cap_start=True, cap_end=True, up_hint=(0.0, 0.0, -1.0), squash=0.11)
    uu = np.concatenate([np.repeat(u, 10), [0.0, 1.0]])
    col = ck.mix(BLACK, NAVY, (0.4 * ck.smoothstep(0.3, 1.0, uu))[:, None])
    name = "tail_upper" if upper else "tail_lower"
    start = mesh.count
    ck.finish(mesh, P, T, "fin", col, rig.blend("spine_9", name, root, root + (0.0, sgn * 0.18, -0.1)), wet=0.9,
              cavity=0.15 * (1 - uu))
    mark("lobe", mesh, start)


def pectorals(mesh: ck.Mesh, rig: ck.Rig) -> None:
    for side, name in ((1.0, "pec_l"), (-1.0, "pec_r")):
        a, tip = pec_points(side)
        path = ck.bezier([a, a + (side * 0.12, -0.04, -0.12), tip + (side * -0.04, 0.1, 0.2), tip], 10)
        u = np.linspace(0.0, 1.0, 10)
        chord = 0.075 * (1.0 - u) ** 0.6 + 0.006
        P, T = ck.tube(path, chord, 8, cap_start=True, cap_end=True, up_hint=(0.0, 1.0, 0.0), squash=0.14)
        uu = np.concatenate([np.repeat(u, 8), [0.0, 1.0]])
        col = ck.mix(BLACK, NAVY, (0.3 * uu)[:, None])
        start = mesh.count
        ck.finish(mesh, P, T, "fin", col, rig.blend("spine_0", name, a, a + (tip - a) * 0.25), wet=0.9)
        mark("pec", mesh, start)
        # the long thin pelvic ray below it
        b = np.array([side * 0.05, AXIS_Y - float(section(1.12)[1]) * 0.95, 1.12])
        path = ck.bezier([b, b + (side * 0.04, -0.2, -0.08), b + (side * 0.07, -0.42, -0.3)], 8)
        P, T = ck.tube(path, np.linspace(0.016, 0.004, 8), 5, cap_start=False, cap_end=True)
        start = mesh.count
        ck.finish(mesh, P, T, "fin", BLACK, body_skin(rig), wet=0.9)
        mark("pec", mesh, start)


def small_fins(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The anal fin under the rear body and the small second dorsal before the tail."""
    for z0, z1, h, up in ((-0.95, -1.75, 0.34, False), (-2.02, -2.28, 0.12, True)):
        n, rows = 10, 4
        u = np.linspace(0.0, 1.0, n)
        z = z0 + (z1 - z0) * u
        du, dv, _w = section(z)
        y0 = AXIS_Y + (du - 0.01 if up else -(dv - 0.01))
        hh = h * np.sin(np.clip(u * 1.25, 0, 1) * math.pi * 0.5) * (1.0 - 0.75 * u ** 2) + 0.02
        v = np.linspace(0.0, 1.0, rows)
        sg = 1.0 if up else -1.0
        zz = (z[:, None] - 0.12 * v[None] * (0.4 + u[:, None])).reshape(-1)
        yy = (y0[:, None] + sg * hh[:, None] * v[None]).reshape(-1)
        T = ck.grid_tris(n, rows, False)
        for side in (1.0, -1.0):
            P = np.column_stack([np.full(len(zz), side * 0.005), yy, zz])
            Ts = orient(P, T, lambda c, sd=side: np.tile([sd, 0.0, 0.0], (len(c), 1)))
            start = mesh.count
            ck.finish(mesh, P, Ts, "fin", BLACK, body_skin(rig), wet=0.9)
            mark("small_fin", mesh, start)


def build_mesh(rig: ck.Rig) -> tuple[ck.Mesh, ck.Mesh]:
    """The fish and, as its own node, the blade's torn-off tip (`BladeTip`, hidden after `phase_close`)."""
    PARTS.clear()
    mesh = ck.Mesh("wakefin")
    tip = ck.Mesh("BladeTip")
    body(mesh, rig)
    bill(mesh, rig)
    eyes(mesh, rig)
    blade(mesh, rig, tip)
    lobe(mesh, rig, True)
    lobe(mesh, rig, False)
    pectorals(mesh, rig)
    small_fins(mesh, rig)
    return mesh, tip


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 4.0
ATTACK_SEC = 1.6
ATTACK_CONTACT = 0.8
CAST_SEC = 2.0
CAST_RISE = 1.5  # the cast's contact: it comes up under the target
HIT_SEC = 0.5
KO_SEC = 3.2
# The KO's last pose: rolled belly-up 165 degrees and floated up the 0.38 m to lie at the surface, drifted 0.9 m
# away; the blade flopped flat out over the water (its curl lifts the tip), the upper lobe laid flat the same way.
KO_ROLL = 165.0
KO_RISE = 0.4
KO_DRIFT = -0.9
KO_FIN = (-84.0, -4.0, 10.0)
KO_LOBES = (-82.0, -40.0)
KO_AWAY = 1.0  # M4-CRB-004: it drifts this far out from the barge (+x) as it dies


def sway(clip: ck.Clip, bone: str, fn) -> None:
    """Keys fn(t) -> (rot, loc) at every baked frame, so a sum of waves plays as authored."""
    n = int(round(clip.length * ck.FPS))
    for f in range(n + 1):
        t = clip.length * f / n
        r, l = fn(t)
        clip.key(bone, t, r, l)


def build_idle() -> ck.Clip:
    """It circles: the body banks and yaws into the turn and back, a swimming wave runs down the spine to the tail,
    the blade leans against the bank and its top curls (the cut), and it surfaces a little twice a loop."""
    c = ck.Clip("idle", IDLE_SEC, loop=True)
    w = 2.0 * math.pi / IDLE_SEC
    sway(c, "root", lambda t: ((1.5 * math.sin(2 * w * t + 1.0), 5.0 * math.sin(w * t), 6.0 * math.sin(w * t + 0.4)),
                               (0.0, 0.03 + 0.03 * math.sin(2 * w * t), 0.0)))
    for i, b in enumerate(SPINE):
        amp = 1.2 + 2.6 * i / 9
        sway(c, b, lambda t, a=amp, k=i: ((0.0, a * math.sin(2 * w * t - 0.55 * k), 0.0), (0.0, 0.0, 0.0)))
    sway(c, "head", lambda t: ((0.0, -1.5 * math.sin(2 * w * t + 0.5), 0.0), (0.0, 0.0, 0.0)))
    sway(c, "bill", lambda t: ((0.6 * math.sin(2 * w * t), 0.0, 0.0), (0.0, 0.0, 0.0)))
    sway(c, "fin_0", lambda t: ((0.0, 0.0, -4.0 * math.sin(w * t + 0.1)), (0.0, 0.0, 0.0)))
    sway(c, "fin_1", lambda t: ((1.5 * math.sin(2 * w * t - 0.8), 0.0, -3.0 * math.sin(w * t - 0.4)), (0.0, 0.0, 0.0)))
    sway(c, "fin_2", lambda t: ((2.5 * math.sin(2 * w * t - 1.4), 0.0, -4.5 * math.sin(w * t - 0.9)), (0.0, 0.0, 0.0)))
    for b, s in (("pec_l", 1.0), ("pec_r", -1.0)):
        sway(c, b, lambda t, sg=s: ((4.0 * math.sin(2 * w * t), 0.0, sg * 5.0 * math.sin(2 * w * t + 0.6)),
                                    (0.0, 0.0, 0.0)))
    for b in ("tail_upper", "tail_lower"):
        sway(c, b, lambda t: ((0.0, 4.0 * math.sin(2 * w * t - 5.8), 0.0), (0.0, 0.0, 0.0)))
    return c


def key_spine(c: ck.Clip, t: float, bend: float = 0.0, yaw: float = 0.0) -> None:
    """The body: `bend` arches it (positive arches the back, nose and tail down), `yaw` curls it to one side; each
    is the total over the ten spine bones, spread down the spine with more toward the tail."""
    f = 0.4 + 0.6 * np.arange(len(SPINE)) / (len(SPINE) - 1)
    f = f / f.sum()
    for i, b in enumerate(SPINE):
        c.key(b, t, (-bend * f[i], yaw * f[i], 0.0))


def build_cast() -> ck.Clip:
    """The dive: it lifts its head and the blade flares (0.35 s), then noses down and goes under, the blade folding
    back as it goes (the fin is under by 0.85 s), turns below, and rises steeply (1.5 s), the blade flaring as it
    comes up; then it settles back to the circle."""
    c = ck.Clip("cast", CAST_SEC)
    for t, y, rx, bend, fin, pec in (
        (0.0, 0.0, 0.0, 0.0, (0, 0, 0), 0.0),
        (0.35, 0.12, -9.0, -12.0, (5, 6, 6), -10.0),
        (0.85, -2.3, 30.0, 20.0, (-14, -34, -30), 25.0),
        (1.15, -2.45, 8.0, 0.0, (-14, -34, -30), 25.0),
        (CAST_RISE, 0.45, -20.0, -18.0, (8, 10, 8), -12.0),
        (1.75, 0.08, -4.0, -6.0, (3, 3, 2), -3.0),
        (CAST_SEC, 0.0, 0.0, 0.0, (0, 0, 0), 0.0),
    ):
        c.key("root", t, (rx, 0.0, 0.0), (0.0, y, 0.0))
        key_spine(c, t, bend, 0.0)
        for b, a in zip(FIN, fin):
            c.key(b, t, (a, 0.0, 0.0))
        c.key("pec_l", t, (pec, 0.0, 0.0))
        c.key("pec_r", t, (pec, 0.0, 0.0))
        c.key("head", t, (-0.5 * rx, 0.0, 0.0))
    return c


def build_hit() -> ck.Clip:
    """The blade jerks over and the body rolls away from the blow, peaking at 0.1 s; a kink runs down the spine."""
    c = ck.Clip("hit", HIT_SEC)
    for t, k in ((0.0, 0.0), (0.1, 1.0), (0.24, -0.4), (0.38, 0.12), (HIT_SEC, 0.0)):
        c.key("root", t, (-3.0 * k, 0.0, -14.0 * k), (0.0, -0.06 * k, 0.0))
        for i, b in enumerate(SPINE):
            c.key(b, t, (0.0, (5.0 if i < 4 else -3.0) * k, 0.0))
        c.key("fin_0", t, (0.0, 0.0, 12.0 * k))
        c.key("fin_1", t, (-4.0 * k, 0.0, 9.0 * k))
        c.key("fin_2", t, (-6.0 * k, 0.0, 12.0 * k))
        c.key("head", t, (-4.0 * k, -6.0 * k, 0.0))
        c.key("pec_l", t, (-15.0 * k, 0.0, 10.0 * k))
        c.key("pec_r", t, (-15.0 * k, 0.0, -10.0 * k))
    return c


def build_ko() -> ck.Clip:
    """It jerks once, the blade flops over flat, it rolls belly-up and floats up to lie at the surface, drifting
    away from the barge; no thrash (pillar 1)."""
    c = ck.Clip("ko", KO_SEC)
    for t, s, rise, drift in ((0.0, 0.0, 0.0, 0.0), (0.25, -0.06, -0.05, 0.0), (0.7, 0.12, 0.0, -0.1),
                              (1.6, 0.7, 0.28, -0.45), (2.4, 0.97, KO_RISE, -0.75), (KO_SEC, 1.0, KO_RISE, KO_DRIFT)):
        c.key("root", t, (2.0 * s, -6.0 * s, KO_ROLL * s), (0.0, rise, drift))
        c.key("breach", t, ZERO3, (KO_AWAY * s, 0.0, 0.0))  # M4-CRB-004: the drift away from the barge
    for t, s in ((0.0, 0.0), (0.25, -0.12), (0.6, 0.35), (1.5, 0.92), (KO_SEC, 1.0)):
        for b, a in zip(FIN, KO_FIN):
            c.key(b, t, (0.0, 0.0, a * s))
        c.key("tail_upper", t, (0.0, 0.0, KO_LOBES[0] * s))
        c.key("tail_lower", t, (0.0, 0.0, KO_LOBES[1] * s))
        c.key("pec_l", t, (10.0 * s, 0.0, -35.0 * s))
        c.key("pec_r", t, (10.0 * s, 0.0, 35.0 * s))
    for t, s in ((0.0, 0.0), (0.25, 1.0), (0.6, -0.4), (1.2, 0.3), (KO_SEC, 0.25)):
        key_spine(c, t, 0.0, 25.0 * s)
        c.key("head", t, (6.0 * max(s, 0.0), 0.0, 0.0))
    return c


# M4-CRB-004 (the Act II move pass, ADR 0041 §3, docs/kb/plan/act2/bosses/wakefin.md §4): every clip is authored as
# offsets from the rest pose by `beats` and played from its phase's idle first frame (ck.in_pose), so each one starts
# and ends exactly where its idle starts. In the build's frame the bill is +z (toward the party, along the hull) and
# the barge lies off its -x flank, the flank the battle camera sees (STAGE_POS and STAGE_YAW below).
#
# A beat is (t, {channel: value}); a channel left out of a beat is 0 (rest). The channels:
#   bx, bz   the breach bone's travel across the water (m; -x toward the barge, +z along it)
#   y        the body's rise (+) or dive (-) on root (m)
#   rx ry rz root's pitch (- nose up), turn (- bill toward the barge) and roll (+ blade over toward the barge), deg
#   bend     the spine's arch (+ arches the back, nose and tail down); yaw its curl (+ tail toward the barge), deg
#   fin      the blade's lean (fin_0..2 about z, + toward the barge); fold its rake (fin_0..2 about x, - back), deg
#   head     (pitch, turn) of the head; bill its turn; pec the pectorals' sweep; tail the lobes' turn, lobe their spread
ZERO3 = (0.0, 0.0, 0.0)


def beats(name: str, length: float, rows, loop: bool = False) -> ck.Clip:
    """A clip keyed from beats (see above); every channel is keyed at every beat, so each eases from beat to beat."""
    c = ck.Clip(name, length, loop=loop)
    for t, v in rows:
        def g(k, d=0.0, v=v):
            return v.get(k, d)

        c.key("breach", t, ZERO3, (g("bx"), 0.0, g("bz")))
        c.key("root", t, (g("rx"), g("ry"), g("rz")), (0.0, g("y"), 0.0))
        key_spine(c, t, g("bend"), g("yaw"))
        for b, lean, fold in zip(FIN, g("fin", ZERO3), g("fold", ZERO3)):
            c.key(b, t, (fold, 0.0, lean))
        hp, hy = g("head", (0.0, 0.0))
        c.key("head", t, (hp, hy, 0.0))
        c.key("bill", t, (0.0, g("bill"), 0.0))
        c.key("pec_l", t, (g("pec"), 0.0, 0.0))
        c.key("pec_r", t, (g("pec"), 0.0, 0.0))
        c.key("tail_upper", t, (-g("lobe"), g("tail"), 0.0))
        c.key("tail_lower", t, (g("lobe"), g("tail"), 0.0))
    return c


# Where the build expects to be staged (docs/kb/art/creatures/act2/wakefin.md, "Staging"): in the water off the
# barge's far beam toward the bow, broadside to the battle camera and inside its frame (bridal_barge_night, whose sea
# is at y -0.6). tools/tests/test_wakefin.py skins every clip here and holds it off the hull.
STAGE_POS = (-5.0, -0.6, -6.5)
STAGE_YAW = 90.0
# The close circle (phase `close_circle`): half the stand-off from the barge, a little higher, the blade raised.
CLOSE = {"bx": -1.2, "y": 0.05, "fold": (2.0, 3.0, 2.0)}
INTRO_SEC = 3.0
READY_SEC = 1.6
IDLE_B_SEC = 1.6
DIVE_SEC, DIVE_CONTACT = 2.6, 1.0
RISE_SEC, RISE_CONTACT = 1.8, 0.85
WASH_SEC, WASH_CONTACT = 1.6, 0.75
STAB_SEC, STAB_CONTACT = 1.4, 0.7
PHASE_SEC, PHASE_CONTACT = 2.0, 0.85


def build_intro() -> ck.Clip:
    """The blade rises out of flat water far off down its line, turns away on the circle, then comes in on one long
    pass, banking, and settles into the circle (3.0 s; the boss intro camera holds 2.4 s)."""
    return beats("intro", INTRO_SEC, (
        (0.0, {"bz": -4.2, "bx": 0.6, "y": -2.5, "rx": -6.0, "ry": 28.0, "fold": (-30.0, -34.0, -30.0), "pec": 20.0}),
        (0.7, {"bz": -3.6, "bx": 0.55, "y": -1.3, "rx": -10.0, "ry": 30.0, "fold": (-12.0, -16.0, -12.0), "pec": 10.0,
               "yaw": 10.0}),
        (1.4, {"bz": -2.6, "bx": 0.3, "y": -0.3, "rx": -3.0, "ry": 26.0, "rz": -8.0, "yaw": 22.0, "fin": (-4, -3, -4),
               "tail": -8.0}),
        (2.1, {"bz": -1.1, "bx": -0.1, "y": -0.04, "ry": -16.0, "rz": 12.0, "yaw": -22.0, "fin": (6, 5, 6),
               "tail": 12.0}),
        (2.6, {"bz": -0.15, "y": 0.02, "ry": -4.0, "rz": 3.0, "yaw": -5.0, "fin": (1, 1, 1)}),
        (INTRO_SEC, {}),
    ))


def build_idle_b() -> ck.Clip:
    """The fidget: the blade dips and folds back as it rolls under a swell, then rises and flares."""
    return beats("idle_b", IDLE_B_SEC, (
        (0.0, {}),
        (0.55, {"y": -0.32, "rx": 3.0, "rz": -4.0, "fold": (-6.0, -12.0, -10.0)}),
        (1.05, {"y": 0.08, "rx": -2.0, "rz": 2.0, "fold": (4.0, 6.0, 6.0)}),
        (IDLE_B_SEC, {}),
    ))


def build_ready() -> ck.Clip:
    """Between its turns: it slows, rides higher and turns its blade's flat to the party, standing it tall, while a
    slow swell rocks it (a loop)."""
    c = ck.Clip("ready", READY_SEC, loop=True)
    w = 2.0 * math.pi / READY_SEC
    sway(c, "breach", lambda t: (ZERO3, ZERO3))
    sway(c, "root", lambda t: ((-2.0 + 1.0 * math.sin(w * t), 10.0, 2.5 * math.sin(w * t + 0.6)),
                               (0.0, 0.1 + 0.03 * math.sin(w * t), 0.0)))
    for i, b in enumerate(SPINE):
        sway(c, b, lambda t, k=i: ((0.0, 1.2 * math.sin(w * t - 0.5 * k), 0.0), ZERO3))
    for i, b in enumerate(FIN):
        sway(c, b, lambda t, k=i: ((4.0 + 1.5 * math.sin(w * t - 0.6 * k), 0.0, -2.0 * math.sin(w * t + 0.4 * k)),
                                   ZERO3))
    sway(c, "head", lambda t: ((-3.0, -4.0, 0.0), ZERO3))
    sway(c, "bill", lambda t: (ZERO3, ZERO3))
    for b in ("pec_l", "pec_r"):
        sway(c, b, lambda t: ((-12.0 + 3.0 * math.sin(w * t), 0.0, 0.0), ZERO3))
    for b in ("tail_upper", "tail_lower"):
        sway(c, b, lambda t: ((0.0, 3.0 * math.sin(w * t - 1.0), 0.0), ZERO3))
    return c


def build_attack() -> ck.Clip:
    """Fin Cut (`attack`, contact 0.8 s): the blade folds back low and the body coils away with its tail cocked
    (0-0.55 s, the wind-up; the seam brightens along its path), then it drives up out of the water alongside, rolling
    over so the blade sweeps flat across toward the deck at contact, the bill slashing; it falls back on its side and
    settles."""
    return beats("attack", ATTACK_SEC, (
        (0.0, {}),
        (0.3, {"bx": 0.2, "y": -0.3, "rx": 6.0, "rz": -8.0, "yaw": -30.0, "fold": (-6.0, -10.0, -8.0), "tail": 20.0,
               "head": (4.0, 0.0)}),
        (0.55, {"bx": 0.3, "y": -0.45, "rx": 9.0, "rz": -12.0, "yaw": -38.0, "fin": (0, -4, -6),
                "fold": (-8.0, -14.0, -12.0), "tail": 26.0, "pec": 15.0, "head": (5.0, 0.0)}),
        (0.68, {"bx": -0.1, "y": 1.1, "rx": -22.0, "rz": 26.0, "bend": -12.0, "yaw": 12.0, "fin": (-4, 6, 8),
                "bill": -6.0, "head": (-6.0, 0.0), "tail": -10.0, "pec": -15.0}),
        (ATTACK_CONTACT, {"bx": -0.5, "y": 2.15, "rx": -6.0, "rz": 44.0, "bend": 8.0, "yaw": 28.0,
                          "fin": (14, 16, 18), "bill": 10.0, "head": (-16.0, 0.0), "tail": -22.0, "pec": -20.0}),
        (1.0, {"bx": -0.45, "y": 1.45, "rx": 4.0, "rz": 52.0, "bend": 12.0, "yaw": 4.0, "fin": (8, 6, -4),
               "bill": 4.0, "tail": -4.0, "pec": -10.0}),
        (1.25, {"bx": -0.25, "y": -0.25, "rx": 3.0, "rz": 28.0, "yaw": -10.0, "fin": (-2, -3, -4), "tail": 8.0}),
        (1.45, {"bx": -0.05, "y": -0.05, "rz": 4.0, "yaw": -2.0}),
        (ATTACK_SEC, {}),
    ))


def build_dive() -> ck.Clip:
    """Sound Dive (`dive`, the charge; contact 1.0 s, when it is under): it lifts its head and stands the blade tall
    (0-0.5 s, the telegraph), then noses down and sinks until only the blade's top cuts the water, and holds there
    gliding (the blade stays in view: it is evasive, never gone), then rises back into the circle."""
    under = {"y": -1.2, "fold": (-4.0, -6.0, -6.0), "pec": 20.0}
    return beats("dive", DIVE_SEC, (
        (0.0, {}),
        (0.25, {"y": 0.12, "rx": -8.0, "fold": (5.0, 6.0, 6.0), "pec": -10.0, "head": (-4.0, 0.0)}),
        (0.5, {"y": 0.16, "rx": -10.0, "fold": (6.0, 8.0, 8.0), "pec": -12.0, "head": (-5.0, 0.0)}),
        (0.85, {"y": -1.0, "rx": 12.0, "bend": 8.0, "fold": (-6.0, -10.0, -10.0), "pec": 25.0}),
        (DIVE_CONTACT, dict(under, rx=4.0)),
        (1.6, dict(under, y=-1.25, ry=-4.0, yaw=6.0)),
        (2.0, dict(under, ry=2.0, yaw=-4.0)),
        (2.35, {"y": -0.3, "rx": -4.0, "fold": (2.0, 2.0, 2.0)}),
        (DIVE_SEC, {}),
    ))


def build_rise_strike() -> ck.Clip:
    """Wakefin Rise (`rise_strike`, contact 0.85 s): the blade folds and sinks to its top, sliding in toward the barge's
    side where the ring of sea-glow opens (0-0.7 s), then the whole fish bursts straight up out of the ring, bill
    first, and topples back away from the barge into the sea."""
    return beats("rise_strike", RISE_SEC, (
        (0.0, {}),
        (0.25, {"bx": -0.2, "y": -0.4, "rx": 8.0, "fold": (-4.0, -8.0, -6.0), "pec": 15.0}),
        (0.6, {"bx": -0.6, "y": -1.05, "rx": 10.0, "fold": (-6.0, -10.0, -8.0), "pec": 25.0}),
        (0.7, {"bx": -0.75, "y": -1.2, "rx": -24.0, "bend": -6.0, "fold": (-4.0, -8.0, -6.0)}),
        (RISE_CONTACT, {"bx": -0.85, "y": 1.9, "rx": -76.0, "bend": -6.0, "fold": (6.0, 8.0, 6.0), "head": (-10.0, 0.0),
                        "pec": -25.0, "tail": 10.0}),
        (1.05, {"bx": -0.8, "y": 1.7, "rx": -68.0, "rz": -20.0, "fold": (2.0, 2.0, 0.0), "pec": -15.0,
                "tail": -10.0}),
        (1.4, {"bx": -0.5, "y": -0.6, "rx": -18.0, "rz": -55.0, "fin": (-10, -8, -6), "tail": 6.0}),
        (1.6, {"bx": -0.15, "y": -0.15, "rx": -4.0, "rz": -10.0}),
        (RISE_SEC, {}),
    ))


def build_wake_wash() -> ck.Clip:
    """Wake Wash (`wake_wash`, contact 0.75 s): it turns hard away from the barge with its tail lobes high out of the
    water and cocked (0-0.6 s), then whips the tail across and slaps it down, throwing its wake at the deck."""
    return beats("wake_wash", WASH_SEC, (
        (0.0, {}),
        (0.3, {"y": 0.15, "ry": 30.0, "rz": -12.0, "bend": -16.0, "yaw": -20.0, "tail": -12.0, "lobe": 10.0}),
        (0.6, {"y": 0.3, "ry": 40.0, "rz": -10.0, "bend": -26.0, "yaw": -32.0, "tail": -18.0, "lobe": 16.0,
               "fin": (-4, -4, -4)}),
        (WASH_CONTACT, {"y": 0.0, "ry": 28.0, "rz": 8.0, "bend": 14.0, "yaw": 44.0, "tail": 30.0, "lobe": 4.0,
                        "fin": (4, 4, 6)}),
        (0.95, {"ry": 20.0, "rz": 4.0, "bend": 4.0, "yaw": 20.0, "tail": 10.0}),
        (1.3, {"ry": 6.0, "yaw": -4.0, "tail": -4.0}),
        (WASH_SEC, {}),
    ))


def build_bill_strike() -> ck.Clip:
    """Bill Strike (`bill_strike_close`, the close circle's bow stab, contact 0.7 s): it rears up beside the bow, bill
    raised high and turned in (0-0.55 s), then stabs it down and in over the rail, and drops back."""
    return beats("bill_strike_close", STAB_SEC, (
        (0.0, {}),
        (0.3, {"y": 0.7, "rx": -24.0, "ry": -12.0, "bend": -6.0, "head": (-10.0, 0.0), "pec": -15.0}),
        (0.55, {"bx": 0.15, "y": 1.3, "rx": -40.0, "ry": -16.0, "bend": -10.0, "head": (-16.0, 0.0), "pec": -20.0,
                "fold": (4.0, 6.0, 6.0)}),
        (STAB_CONTACT, {"bx": -0.2, "bz": 0.5, "y": 1.85, "rx": 10.0, "ry": -22.0, "head": (6.0, 0.0), "bill": -4.0,
                        "pec": 10.0}),
        (0.9, {"bx": -0.15, "bz": 0.4, "y": 1.2, "rx": 8.0, "ry": -16.0, "rz": -8.0}),
        (1.15, {"bx": -0.05, "bz": 0.1, "y": 0.1, "rx": 1.0, "ry": -4.0}),
        (STAB_SEC, {}),
    ))


def build_hit_b() -> ck.Clip:
    """The other hit: the blade snaps back and the body rolls toward the barge and is shoved under, peaking at 0.1 s
    (authored, not the mirrored hit)."""
    rows = []
    for t, k in ((0.0, 0.0), (0.1, 1.0), (0.25, -0.35), (0.38, 0.1), (HIT_SEC, 0.0)):
        rows.append((t, {"y": -0.12 * k, "rx": 4.0 * k, "rz": 12.0 * k, "yaw": -14.0 * k,
                         "fold": (-8.0 * k, -12.0 * k, -14.0 * k), "fin": (-6.0 * k, -4.0 * k, -6.0 * k),
                         "head": (5.0 * k, 6.0 * k), "pec": 18.0 * k}))
    return beats("hit_b", HIT_SEC, rows)


def build_phase_close(end: dict) -> ck.Clip:
    """Close circle (`phase_close`, contact 0.85 s, the ram): it turns in and surges at the barge, rolls its blade
    away and slams its flank into the hull (the barge's rock is staging's), the blade's tip tearing off on the rail
    and flung out into the sea; it rebounds and settles into the tight circle. `end` is the close idle's first frame
    as offsets from the wide idle's, keyed last."""
    c = beats("phase_close", PHASE_SEC, (
        (0.0, {}),
        (0.35, {"bx": -0.3, "y": -0.1, "ry": -24.0, "rz": -10.0, "yaw": -12.0, "tail": 14.0}),
        (0.7, {"bx": -2.3, "y": 0.1, "ry": -6.0, "rz": -18.0, "yaw": 10.0, "fin": (-6, -6, -8), "tail": -10.0}),
        (PHASE_CONTACT, {"bx": -2.55, "y": 0.18, "ry": 4.0, "rz": -24.0, "yaw": 18.0, "fin": (-10, -14, -18),
                         "head": (0.0, 10.0), "tail": -16.0}),
        (1.1, {"bx": -1.9, "y": -0.1, "ry": 6.0, "rz": 6.0, "yaw": -8.0, "fin": (4, 6, 8), "tail": 8.0}),
        (1.5, {"bx": -1.3, "ry": 2.0, "rz": -2.0}),
    ))
    # the torn tip rides the blade to the ram, then is flung up and out over the far water and falls in
    for t, r, l in ((0.0, ZERO3, ZERO3), (PHASE_CONTACT, ZERO3, ZERO3), (1.0, (0, 0, -60), (0.5, 0.5, 0.0)),
                    (1.3, (0, 0, -150), (1.3, -0.6, 0.0)), (1.55, (0, 0, -200), (1.6, -2.6, 0.0)),
                    (PHASE_SEC, (0, 0, -220), (1.7, -3.4, 0.0))):
        c.key("blade_tip", t, r, l)
    for b, (r, l) in end.items():
        c.key(b, PHASE_SEC, tuple(r), tuple(l))
    return c


def first_frame(clip: ck.Clip) -> dict:
    return {b: tuple(np.asarray(v, float) for v in clip.sample(b, 0.0)) for b in clip.keys}


def build_clips() -> list[ck.Clip]:
    idle = build_idle()
    idle0 = first_frame(idle)
    close_pose = first_frame(beats("_close", 1.0, ((0.0, CLOSE),)))
    # the tight circle: the wide idle a little stronger (it banks harder), half the stand-off from the barge
    idle_close = ck.in_pose(ck.varied(idle, "idle_close", amp=1.3), "idle_close", close_pose)
    close0 = first_frame(idle_close)
    zero = (np.zeros(3), np.zeros(3))
    end = {b: tuple(np.asarray(close0[b][k]) - np.asarray(idle0.get(b, zero)[k]) for k in (0, 1)) for b in close0}
    ready = build_ready()
    strikes = [build_attack(), build_cast(), build_dive(), build_rise_strike(), build_wake_wash(), build_hit(),
               build_hit_b(), build_ko()]
    out = [idle, ck.in_pose(build_idle_b(), "idle_b", idle0), ready, ck.in_pose(build_intro(), "intro", idle0)]
    out += [ck.in_pose(c, c.name, idle0) for c in strikes]
    out += [ck.in_pose(build_phase_close(end), "phase_close", idle0), idle_close,
            ck.in_pose(ready, "ready_close", close_pose)]
    out += [ck.in_pose(c, f"{c.name}_close", close0) for c in strikes]
    out += [ck.in_pose(build_bill_strike(), "bill_strike_close", close0)]
    return out


# creatures.json's `phases.close_circle.clips` and `contact` (tools/tests/test_wakefin.py)
CLOSE_CLIPS = {"attack": "attack_close", "cast": "cast_close", "dive": "dive_close", "rise_strike": "rise_strike_close",
               "wake_wash": "wake_wash_close", "hit": "hit_close", "hit_b": "hit_b_close", "ready": "ready_close",
               "ko": "ko_close"}
CONTACT = {"attack": ATTACK_CONTACT, "cast": CAST_RISE, "dive": DIVE_CONTACT, "rise_strike": RISE_CONTACT,
           "wake_wash": WASH_CONTACT, "bill_strike_close": STAB_CONTACT, "phase_close": PHASE_CONTACT}


# ---------------------------------------------------------------------------------------------
# A numpy check (no Blender): skinned bounds, the blade's top and root, and the peak time per clip
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


def barge_grid(cell: float = 0.1) -> tuple[np.ndarray, np.ndarray, float]:
    """The bridal barge (M3-ENV-720) as a height field over cells `cell` m wide in x, z (arena space): (its highest
    point per cell, -inf off the barge; the grid's (x, z) origin; cell). For the staging check: a body over the barge
    stays BARGE_CLEAR m above it, so nothing passes through the hull, the rail or the deck."""
    root = Path(__file__).resolve().parents[2] / "environments" / "kits" / "haluna"
    sys.path.insert(0, str(root))
    import bridal_barge as bb  # noqa: PLC0415

    pts = []
    for mb in bb.build_barge():
        P = np.asarray(mb.pos)
        T = np.asarray(mb.tris)
        # each triangle sampled on a 6 x 6 barycentric lattice, so long planks fill every cell they cross
        u, v = np.meshgrid(np.linspace(0.0, 1.0, 6), np.linspace(0.0, 1.0, 6))
        keep = (u + v) <= 1.0
        u, v = u[keep], v[keep]
        A, B, C = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
        pts.append((A[:, None] * (1 - u - v)[None, :, None] + B[:, None] * u[None, :, None]
                    + C[:, None] * v[None, :, None]).reshape(-1, 3))
    S = np.vstack(pts)
    origin = S[:, [0, 2]].min(axis=0) - cell
    ij = np.floor((S[:, [0, 2]] - origin) / cell).astype(int)
    grid = np.full(tuple(ij.max(axis=0) + 2), -np.inf)
    np.maximum.at(grid, (ij[:, 0], ij[:, 1]), S[:, 1])
    return grid, origin, cell


BARGE_CLEAR = 0.3  # m: the design sheet's "the sweep stays above the deck by at least 0.3 m", over the rail too


def staged(P: np.ndarray) -> np.ndarray:
    """Build-space points placed at the staging (STAGE_POS, turned STAGE_YAW about y as FighterStandIn turns it)."""
    a = math.radians(STAGE_YAW)
    R = np.array([[math.cos(a), 0.0, math.sin(a)], [0.0, 1.0, 0.0], [-math.sin(a), 0.0, math.cos(a)]])
    return P @ R.T + np.asarray(STAGE_POS)


def barge_overlap(P: np.ndarray, barge: tuple) -> float:
    """How far (m) the deepest staged point lies inside the barge's clearance (-inf: never over the barge)."""
    grid, origin, cell = barge
    W = staged(P)
    ij = np.floor((W[:, [0, 2]] - origin) / cell).astype(int)
    ok = (ij[:, 0] >= 0) & (ij[:, 1] >= 0) & (ij[:, 0] < grid.shape[0]) & (ij[:, 1] < grid.shape[1])
    top = np.full(len(W), -np.inf)
    top[ok] = grid[ij[ok, 0], ij[ok, 1]]
    over = np.isfinite(top)
    return float((top[over] + BARGE_CLEAR - W[over, 1]).max()) if over.any() else -np.inf


def merged(*meshes: ck.Mesh) -> dict:
    out = meshes[0].arrays()
    for m in meshes[1:]:
        a = m.arrays()
        for k in ("pos", "joints", "weights"):
            out[k] = np.concatenate([out[k], a[k]])
    return out


def report(rig: ck.Rig, meshes: tuple[ck.Mesh, ck.Mesh], clips: list[ck.Clip]) -> None:
    """Per clip: its bounds, the blade's top, its peak, how far its first and last frames are from its phase's idle
    first frame, and how close it comes to the barge at the staging (negative: clear by that much)."""
    mesh, tip = meshes
    arrays = merged(mesh, tip)
    rest = arrays["pos"]
    f0, f1 = PARTS["fin"]
    fin = np.concatenate([np.arange(f0, f1), np.arange(mesh.count, mesh.count + tip.count)])
    print(f"triangles: {mesh.triangle_count + tip.triangle_count} (tip {tip.triangle_count}); "
          f"vertices {mesh.count + tip.count}; bones {len(rig.bones)}")
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)}; "
          f"blade top {rest[fin, 1].max():.3f}")
    barge = barge_grid()
    by = {c.name: c for c in clips}
    for c in ck.with_variety(clips):
        frames = max(int(round(c.length * ck.FPS)), 1)
        lo, hi, disp, top, near = np.inf, -np.inf, [], [], -np.inf
        for f in range(frames + 1):
            t = min(f / ck.FPS, c.length)
            P = skin(rig, arrays, fk(rig, c, t))
            lo, hi = min(lo, float(P[:, 1].min())), max(hi, float(P[:, 1].max()))
            top.append(float(P[fin, 1].max()))
            disp.append(float(np.linalg.norm(P - rest, axis=1).mean()))
            near = max(near, barge_overlap(P, barge))
        idle = by["idle_close"] if c.name.endswith("_close") else by["idle"]
        ends = [max(float(np.abs(np.asarray(c.sample(b, t)[k]) - np.asarray(idle.sample(b, 0.0)[k])).max())
                    for b in idle.keys for k in (0, 1)) for t in (0.0, c.length)]
        peak = int(np.argmax(disp)) / ck.FPS
        print(f"{c.name:18s} {c.length:.2f}s: y {lo:+.2f}..{hi:.2f}; blade top {min(top):.2f}..{max(top):.2f}; "
              f"peak {peak:.2f}s; off its idle's first frame {ends[0]:.3f}/{ends[1]:.3f}; barge {near:+.2f} m")


def build() -> tuple[ck.Rig, tuple[ck.Mesh, ck.Mesh], list[ck.Clip]]:
    rig = build_rig()
    return rig, build_mesh(rig), build_clips()


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--report", action="store_true", help="print the triangle count and the clip checks; no export")
    args = ap.parse_args(argv)
    rig, (mesh, tip), clips = build()
    if args.report or not args.out:
        report(rig, (mesh, tip), clips)
        return
    info = ck.export_creature(mesh, rig, clips, args.out, extra_meshes=[tip], extras={"hymn_creature": "wakefin"})
    print(f"wakefin: {info}")


if __name__ == "__main__":
    main()
