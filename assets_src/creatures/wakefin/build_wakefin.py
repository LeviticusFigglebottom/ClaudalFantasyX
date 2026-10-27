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
SEAM_K = (1, 2)  # the seam band: between these section rows on the right flank (mirrored on the left)
SEAM_Z = (-2.38, 1.36)
# Wounds along the spine: (z, side, half-length), high on the flank either side of the ridge.
WOUNDS = ((1.38, 1, 0.12), (0.95, -1, 0.15), (0.45, 1, 0.17), (-0.15, -1, 0.17), (-0.75, 1, 0.16), (-1.3, -1, 0.14),
          (-1.78, 1, 0.12), (-2.12, -1, 0.09))
WOUND_K = 7  # the section row (from the lateral line) the wounds lie on: 78.75 degrees, beside the ridge

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
    rig.add("root", (0, AXIS_Y, ROOT_Z), (0, AXIS_Y + 0.3, ROOT_Z))
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
    return rig


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
    for z0, s, half in WOUNDS:
        along = np.abs(zv - z0) / half
        win = ck.smoothstep(1.0, 0.55, along) * (side == s)
        slit = np.maximum(slit, win * np.exp(-((ang - WOUND_K) / 0.45) ** 2))
        lip = np.maximum(lip, ck.smoothstep(1.35, 0.6, along) * (side == s) * np.exp(-((ang - WOUND_K) / 1.2) ** 2))
    lip = lip * (1.0 - slit)
    # the gill cover's edge and the mouth's line on the head
    gill = np.exp(-((zv - (1.42 + 0.06 * sav ** 2)) / 0.02) ** 2) * ck.smoothstep(0.85, 0.5, np.abs(sav))
    mouth = np.exp(-((sav + 0.32) / 0.09) ** 2) * ck.smoothstep(1.66, 1.8, zv)
    rough = ck.fbm(P * 7.0, SEED + 1) * 0.004
    disp = rough - 0.02 * slit + 0.008 * lip - 0.008 * gill - 0.006 * mouth
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
    col = ck.mix(col, PAL["spawn_wound"] * 0.65, slit[:, None])
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
    for name, tri_mask, c, e, slot in (("body", ~tri_seam, col, slit, "body"),
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


def blade(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The dorsal blade: rays fanned from its root along the back to its outline, two faces a little apart."""
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
    for side in (1.0, -1.0):
        P = np.column_stack([side * th * 0.5, yy, zz])
        Ts = orient(P, T, lambda c, sd=side: np.tile([sd, 0.0, 0.0], (len(c), 1)))
        start = mesh.count
        ck.finish(mesh, P, Ts, "fin", col, fin_skin(rig), wet=0.85, cavity=0.35 * ray + 0.2 * (1.0 - vv) ** 3)
        mark("fin", mesh, start)


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


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    PARTS.clear()
    mesh = ck.Mesh("wakefin")
    body(mesh, rig)
    bill(mesh, rig)
    eyes(mesh, rig)
    blade(mesh, rig)
    lobe(mesh, rig, True)
    lobe(mesh, rig, False)
    pectorals(mesh, rig)
    small_fins(mesh, rig)
    return mesh


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


def build_attack() -> ck.Clip:
    """The cut: it sinks and coils (0.35 s), drives up out of the water nose-high (0.6 s), and at contact (0.8 s) the
    whole fish is out alongside, rolled over so the blade sweeps flat across the deck, the bill slashing; it falls
    back on its side and settles."""
    c = ck.Clip("attack", ATTACK_SEC)
    for t, y, rx, rz, bend, yaw, fin, bill, head in (
        (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (0, 0, 0), 0.0, 0.0),
        (0.35, -0.22, 6.0, -8.0, 0.0, -40.0, (0, -6, -10), 0.0, 4.0),
        (0.6, 0.8, -14.0, 18.0, -12.0, 15.0, (-4, 6, 8), -6.0, -6.0),
        (ATTACK_CONTACT, 1.15, -4.0, 62.0, 8.0, 30.0, (14, 16, 18), 10.0, -16.0),
        (1.0, 0.7, 6.0, 52.0, 12.0, 0.0, (8, 6, -4), 4.0, 6.0),
        (1.3, -0.12, 4.0, 14.0, 0.0, -10.0, (-2, -3, -4), 0.0, 0.0),
        (ATTACK_SEC, 0.0, 0.0, 0.0, 0.0, 0.0, (0, 0, 0), 0.0, 0.0),
    ):
        c.key("root", t, (rx, 0.0, rz), (0.0, y, 0.0))
        key_spine(c, t, bend, yaw)
        for b, a in zip(FIN, fin):
            c.key(b, t, (0.0, 0.0, a))
        c.key("bill", t, (0.0, bill, 0.0))
        c.key("head", t, (0.0, head, 0.0))
        c.key("pec_l", t, (-0.3 * abs(rz), 0.0, 0.25 * rz))
        c.key("pec_r", t, (-0.3 * abs(rz), 0.0, -0.25 * rz))
        c.key("tail_upper", t, (0.0, -0.8 * yaw, 0.0))
        c.key("tail_lower", t, (0.0, -0.8 * yaw, 0.0))
    return c


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


def build_clips() -> list[ck.Clip]:
    return [build_idle(), build_attack(), build_cast(), build_hit(), build_ko()]


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


def report(rig: ck.Rig, mesh: ck.Mesh, clips: list[ck.Clip]) -> None:
    arrays = mesh.arrays()
    rest = arrays["pos"]
    f0, f1 = PARTS["fin"]
    fin = np.arange(f0, f1)
    base = fin[(rest[fin, 1] - back_y(rest[fin, 2])) < -0.015]
    front = base[rest[base, 2] > 0.0]
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}")
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)}; "
          f"blade top {rest[fin, 1].max():.3f}; its root's front half y {rest[front, 1].min():+.3f}..{rest[front, 1].max():+.3f}")
    for c in ck.with_variety(clips):
        frames = max(int(round(c.length * ck.FPS)), 1)
        lo, hi, disp, top, root_lo, root_hi = np.inf, -np.inf, [], [], np.inf, -np.inf
        for f in range(frames + 1):
            t = min(f / ck.FPS, c.length)
            P = skin(rig, arrays, fk(rig, c, t))
            lo, hi = min(lo, float(P[:, 1].min())), max(hi, float(P[:, 1].max()))
            top.append(float(P[fin, 1].max()))
            root_lo, root_hi = min(root_lo, float(P[front, 1].min())), max(root_hi, float(P[front, 1].max()))
            disp.append(float(np.linalg.norm(P - rest, axis=1).mean()))
        P = skin(rig, arrays, fk(rig, c, c.length))
        peak = int(np.argmax(disp)) / ck.FPS
        print(f"{c.name:7s} {c.length:.2f}s: y {lo:+.3f}..{hi:.3f}; blade top {min(top):.2f}..{max(top):.2f} "
              f"(at {int(np.argmin(top)) / ck.FPS:.2f}s lowest); blade root front {root_lo:+.3f}..{root_hi:+.3f}; "
              f"end y {P[:, 1].min():+.3f}..{P[:, 1].max():.3f}; peak {peak:.2f}s")


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
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "wakefin"})
    print(f"wakefin: {info}")


if __name__ == "__main__":
    main()
