"""Procedural quad cage, Catmull-Clark subdivision and surface projection (M1-CHR-01).

Pure numpy, no bpy. The cage is built as explicit topology:

* torso: one tube of N_TORSO rings, from a tilted crotch ring to the top of the neck, with a
  2x3-cell armhole on each side and the bottom ring split into two leg loops at the crotch;
* legs: tubes from the crotch loop to the ankle, bridged into a hole on top of a foot tube;
* arms: tubes from the armhole to the wrist, then a palm tube whose end is consumed by four
  4-sided finger tubes; the thumb grows from a quad on the radial side of the palm;
* head: bb_head (M1-CHR-02): a landmark-aligned box lattice ray-cast onto the head field, with
  eye and mouth blocks refilled by concentric face loops (orbicularis oculi / oris, nasolabial,
  lid margins, lip lines); the neck enters through a 12x4-cell hole underneath.

Every ring vertex is found by ray-casting from a skeleton axis onto that region's own field, so
the topology is fixed while the shape follows the anatomy. After one Catmull-Clark level the
mesh is projected onto the joined field with tangential relaxation (pinned: lid margins, lip
line, eye sockets and mouth bag).
"""
from __future__ import annotations

import math

import numpy as np

import bb_head
from bb_anatomy import Body
from bb_params import Landmarks, unit, v3

Arr = np.ndarray
N_TORSO = 32
N_LEG = N_TORSO // 2 + 2  # half the torso ring + the crotch vertex = 18
N_ARM = 10
N_FOOT = 12


# ---------------------------------------------------------------------------------------------
# Ray casting
# ---------------------------------------------------------------------------------------------
def cast(body: Body, region: str | None, O: Arr, D: Arr, tmax: float = 0.4, steps: int = 220) -> Arr:
    """First exit of rays O + t D from the region's field (origins are expected inside)."""
    O = np.atleast_2d(O).astype(float)
    D = np.atleast_2d(D).astype(float)
    if len(O) == 1 and len(D) > 1:
        O = np.repeat(O, len(D), axis=0)
    D = D / np.linalg.norm(D, axis=1, keepdims=True)
    n = len(O)
    ts = np.linspace(0.0, tmax, steps)
    pts = O[:, None, :] + D[:, None, :] * ts[None, :, None]
    d = body.sdf(pts.reshape(-1, 3), region).reshape(n, steps)
    out = d > 0
    j = np.argmax(out, axis=1)
    j = np.where(out.any(axis=1), j, steps - 1)
    j = np.maximum(j, 1)
    lo = ts[j - 1].copy()
    hi = ts[j].copy()
    for _ in range(18):
        mid = 0.5 * (lo + hi)
        dm = body.sdf(O + D * mid[:, None], region)
        inside = dm <= 0
        lo = np.where(inside, mid, lo)
        hi = np.where(inside, hi, mid)
    starts_out = d[:, 0] > 0
    t = np.where(starts_out, 0.0, 0.5 * (lo + hi))
    return O + D * t[:, None]


def basis(axis: Arr, ref: Arr) -> tuple[Arr, Arr]:
    a = unit(axis)
    e1 = ref - (ref @ a) * a
    e1 = unit(e1)
    e2 = np.cross(a, e1)
    return e1, e2


def loop_angles(P: Arr, c: Arr, axis: Arr, ref: Arr) -> Arr:
    e1, e2 = basis(axis, ref)
    q = P - c
    return np.unwrap(np.arctan2(q @ e2, q @ e1))


def blend_angles(src: Arr, n: int, s: float) -> Arr:
    """Blend an angle sequence toward a uniform one with the same winding and mean offset."""
    sign = 1.0 if src[-1] - src[0] > 0 else -1.0
    uni = sign * 2 * math.pi * np.arange(n) / n
    off = math.atan2(np.mean(np.sin(src - uni)), np.mean(np.cos(src - uni)))
    uni = uni + off
    # bring uni onto the same unwrapped branch as src, element-wise
    uni = src + np.angle(np.exp(1j * (uni - src)))
    return (1 - s) * src + s * uni


def match_cyclic(ang: Arr, dst: Arr) -> Arr:
    """Reorder the angle set `dst` (cyclic shift, optional reversal) to follow `ang` index by index,
    returned on `ang`'s unwrapped branch. Keeps blended rings from twisting inside out."""
    n = len(ang)
    best = None
    for flip in (False, True):
        dd = dst[::-1] if flip else dst
        for sh in range(n):
            cand = np.roll(dd, -sh)
            diff = np.angle(np.exp(1j * (cand - ang)))
            cost = float(np.sum(diff * diff))
            if best is None or cost < best[0]:
                best = (cost, ang + diff)
    return best[1]


def ring_dirs(axis: Arr, ref: Arr, ang: Arr, elev: float | Arr = 0.0) -> Arr:
    e1, e2 = basis(axis, ref)
    a = unit(axis)
    el = np.broadcast_to(np.asarray(elev, dtype=float), ang.shape)
    return (np.cos(ang)[:, None] * e1 + np.sin(ang)[:, None] * e2) * np.cos(el)[:, None] + np.sin(el)[:, None] * a


# ---------------------------------------------------------------------------------------------
# Cage container
# ---------------------------------------------------------------------------------------------
class Cage:
    def __init__(self, body: Body) -> None:
        self.body = body
        self.lm: Landmarks = body.lm
        self._V: list[Arr] = []
        self.vreg: list[str] = []
        self.vpin: list[bool] = []
        self.F: list[tuple[int, int, int, int]] = []
        self.freg: list[str] = []
        self.seams: set[tuple[int, int]] = set()
        self.n = 0
        self.groups: dict[str, list[int]] = {}

    def add(self, P: Arr, reg: str, pin: bool = False) -> Arr:
        P = np.atleast_2d(P)
        idx = np.arange(self.n, self.n + len(P))
        self._V.extend(list(P))
        self.vreg.extend([reg] * len(P))
        self.vpin.extend([pin] * len(P))
        self.n += len(P)
        return idx

    @property
    def V(self) -> Arr:
        return np.array(self._V)

    def set_pos(self, idx: Arr, P: Arr) -> None:
        for i, p in zip(idx, P):
            self._V[int(i)] = p

    def quad(self, a: int, b: int, c: int, d: int, reg: str) -> None:
        q = (int(a), int(b), int(c), int(d))
        assert len(set(q)) == 4, q
        self.F.append(q)
        self.freg.append(reg)

    def bridge(self, A: Arr, B: Arr, reg: str, closed: bool = True) -> None:
        n = len(A)
        assert len(B) == n, (len(A), len(B))
        rng = range(n) if closed else range(n - 1)
        for i in rng:
            j = (i + 1) % n
            self.quad(A[i], A[j], B[j], B[i], reg)

    def seam_loop(self, L: Arr, closed: bool = True) -> None:
        n = len(L)
        for i in range(n if closed else n - 1):
            self.seam(L[i], L[(i + 1) % n])

    def seam(self, a: int, b: int) -> None:
        a, b = int(a), int(b)
        self.seams.add((min(a, b), max(a, b)))

    def fill_grid(self, loop: Arr, a: int, b: int, reg: str, pin: bool = False, bulge: Arr | None = None) -> Arr:
        """Fill a closed loop of 2(a+b) verts with an a x b quad grid (Coons patch)."""
        loop = np.asarray(loop)
        assert len(loop) == 2 * (a + b), (len(loop), a, b)
        V = self.V
        grid = -np.ones((a + 1, b + 1), dtype=int)
        k = 0
        for c in range(b + 1):  # bottom edge, row 0, left to right
            grid[0, c] = loop[k]
            k += 1
        for r in range(1, a + 1):  # right edge, bottom to top
            grid[r, b] = loop[k]
            k += 1
        for c in range(b - 1, -1, -1):  # top edge, right to left
            grid[a, c] = loop[k]
            k += 1
        for r in range(a - 1, 0, -1):  # left edge, top to bottom
            grid[r, 0] = loop[k]
            k += 1
        assert k == len(loop)
        for r in range(1, a):
            for c in range(1, b):
                u, v = c / b, r / a
                P = (
                    (1 - v) * V[grid[0, c]] + v * V[grid[a, c]] + (1 - u) * V[grid[r, 0]] + u * V[grid[r, b]]
                    - ((1 - u) * (1 - v) * V[grid[0, 0]] + u * (1 - v) * V[grid[0, b]]
                       + (1 - u) * v * V[grid[a, 0]] + u * v * V[grid[a, b]])
                )
                if bulge is not None:
                    P = P + bulge * (math.sin(math.pi * u) * math.sin(math.pi * v))
                grid[r, c] = self.add(P, reg, pin)[0]
        for r in range(a):
            for c in range(b):
                self.quad(grid[r, c], grid[r, c + 1], grid[r + 1, c + 1], grid[r + 1, c], reg)
        return grid


# ---------------------------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------------------------
def build_cage(body: Body) -> Cage:
    cg = Cage(body)
    torso = _torso(cg)
    head_hole = bb_head.build_head(cg, cast)
    _neck_to_head(cg, torso, head_hole)
    for side in ("L", "R"):
        wrist_ring = _arm(cg, torso, side)
        _hand(cg, wrist_ring, side)
        ankle_ring = _leg(cg, torso, side)
        _foot(cg, ankle_ring, side)
    return cg


def _torso(cg: Cage) -> dict:
    lm, body = cg.lm, cg.body
    S = lm.S
    N = N_TORSO
    th = 2 * math.pi * np.arange(N) / N  # 0 = front (-Y), +90 deg = character's left (+X)
    z_c, z_hp = lm.P("crotch")[2], lm.P("hip")[2]
    z_w, z_nip = lm.P("waist")[2], lm.P("nipple")[2]
    J = lm.P("shoulder")[2]
    z_notch = lm.P("notch")[2]
    up = v3(0, 0, 1)
    ref = v3(0, -1, 0)
    rings: list[Arr] = []
    meta: list[str] = []

    def axis_y(z: float) -> float:  # spine curve: lordosis/kyphosis offsets of the ray origin
        return 0.012 * S * math.sin((z - z_c) / (z_notch - z_c) * math.pi * 1.2)

    def ring_at(zs: Arr | float, elev: float = 0.0, origin_z: float | None = None, scale_y: float = 0.0) -> Arr:
        zs = np.broadcast_to(np.asarray(zs, dtype=float), th.shape)
        if origin_z is not None:
            O = np.stack([np.zeros(N), np.full(N, axis_y(origin_z) + scale_y), np.full(N, origin_z)], axis=1)
        else:
            O = np.stack([np.zeros(N), np.array([axis_y(z) for z in zs]), zs], axis=1)
        D = ring_dirs(up, ref, th, elev)
        return cast(body, "torso", O, D)

    s2 = np.sin(th) ** 2
    z_fb = z_c + 0.058 * S
    z_side = z_hp + 0.03 * S
    rings.append(ring_at(z_fb + (z_side - z_fb) * s2))
    meta.append("crotch")
    rings.append(ring_at(z_hp + 0.012 * S + (z_side + 0.05 * S - z_hp - 0.012 * S) * s2 * 0.3))
    meta.append("hip")
    levels = [
        z_hp + 0.075 * S,
        z_hp + 0.13 * S,
        z_w - 0.03 * S,
        z_w + 0.02 * S,
        z_w + (z_nip - z_w) * 0.4,
        z_w + (z_nip - z_w) * 0.72,
        z_nip,
        (z_nip + J - 0.075 * S) / 2,
    ]
    for z in levels:
        rings.append(ring_at(z))
        meta.append("trunk")
    hole_lo = len(rings)
    for z in (J - 0.082 * S, J - 0.03 * S, J + 0.016 * S):
        rings.append(ring_at(z))
        meta.append("arm")
    rings.append(ring_at(0, elev=math.radians(28), origin_z=J - 0.01 * S, scale_y=0.012 * S))
    meta.append("arm")
    for el in (44, 58):
        rings.append(ring_at(0, elev=math.radians(el), origin_z=J - 0.012 * S, scale_y=0.012 * S))
        meta.append("yoke")
    nb, sb = lm.P("neck_base"), lm.P("skull_base")
    for t in (0.18, 0.5):
        c = nb + (sb - nb) * t
        O = np.repeat(c[None, :], N, axis=0)
        rings.append(cast(body, "torso", O, ring_dirs(unit(sb - nb), ref, th)))
        meta.append("neck")
    idx = [cg.add(r, "torso") for r in rings]
    for k in range(len(idx) - 1):
        for i in range(N):
            j = (i + 1) % N
            in_hole = hole_lo <= k < hole_lo + 3 and (7 <= i < 9 or 23 <= i < 25)
            if in_hole:
                continue
            cg.quad(idx[k][i], idx[k][j], idx[k + 1][j], idx[k + 1][i], "torso")
    for k in range(len(idx) - 1):  # back seam
        cg.seam(idx[k][16], idx[k + 1][16])
    holes = {}
    for side, (i0, i1) in (("L", (7, 9)), ("R", (23, 25))):
        r0, r1, r2, r3 = (idx[hole_lo + q] for q in range(4))
        mid = (i0 + i1) // 2
        loop = [r0[i0], r0[mid], r0[i1], r1[i1], r2[i1], r3[i1], r3[mid], r3[i0], r2[i0], r1[i0]]
        holes[side] = np.array(loop)
        cg.seam_loop(holes[side])
    return {"rings": idx, "holes": holes, "th": th}


def _neck_to_head(cg: Cage, torso: dict, head_hole: Arr) -> None:
    lm, body = cg.lm, cg.body
    S = lm.S
    nb, sb = lm.P("neck_base"), lm.P("skull_base")
    a = unit(sb - nb)
    last = torso["rings"][-1]
    V = cg.V
    ref = v3(0, -1, 0)
    c_top = sb + v3(0, -0.006 * S, 0.0)
    src = loop_angles(V[last], c_top, a, ref)
    dst = loop_angles(V[head_hole], c_top, a, ref)
    # align the head loop to the neck loop (cyclic shift + direction)
    best = None
    n = len(last)
    for flip in (False, True):
        hh = head_hole[::-1] if flip else head_hole
        for sh in range(n):
            cand = np.roll(hh, -sh)
            cost = float(np.sum((V[cand] - V[last]) ** 2))
            if best is None or cost < best[0]:
                best = (cost, cand)
    hole = best[1]
    dst = loop_angles(V[hole], c_top, a, ref)
    dst = src + np.angle(np.exp(1j * (dst - src)))
    # one intermediate ring: angles halfway to the head loop, origin under the skull
    ang = 0.5 * (src + dst)
    c_mid = nb + (sb - nb) * 0.82
    O = np.repeat(c_mid[None, :], n, axis=0)
    mid_pts = cast(body, "torso", O, ring_dirs(a, ref, ang))
    # keep it below the jaw line: blend toward the straight midpoint between the two loops
    mid_pts = 0.5 * mid_pts + 0.25 * (V[last] + V[hole])
    mid = cg.add(mid_pts, "torso")
    cg.bridge(last, mid, "torso")
    cg.bridge(mid, hole, "torso")
    cg.seam(last[16], mid[16])
    cg.seam_loop(hole)
    # back seam continues from the mid ring to the hole vertex closest behind
    V = cg.V
    j = int(np.argmin(np.linalg.norm(V[hole] - V[mid[16]], axis=1)))
    cg.seam(mid[16], hole[j])


def _arm(cg: Cage, torso: dict, side: str) -> Arr:
    lm, body = cg.lm, cg.body
    S = lm.S
    reg = f"arm_{side}"
    hole = torso["holes"][side]
    sh, el, wr = lm.side_pt("shoulder", side), lm.side_pt("elbow", side), lm.side_pt("wrist", side)
    a_up, a_fo = unit(el - sh), unit(wr - el)
    ref = v3(0, 0, 1)
    V = cg.V
    src = loop_angles(V[hole], sh, a_up, ref)
    hand = lm.hands[side]
    # palm design angles around the forearm axis at the wrist
    palm_dirs = _palm_design(hand)
    dst = loop_angles(hand.wrist + palm_dirs, wr, a_fo, ref)
    stations: list[tuple[Arr, Arr, float]] = []  # (centre, axis, s_toward_uniform)
    L_up = float(np.linalg.norm(el - sh))
    L_fo = float(np.linalg.norm(wr - el))
    stations.append((sh + a_up * 0.045 * S, a_up, 0.35))
    for t in (0.28, 0.5, 0.72, 0.88):
        stations.append((sh + a_up * L_up * t, a_up, 1.0))
    stations.append((el, unit(a_up + a_fo), 1.0))
    for t in (0.12, 0.35, 0.6, 0.85):
        stations.append((el + a_fo * L_fo * t, a_fo, 1.0))
    rings = []
    n_st = len(stations)
    uni_prev = None
    for k, (c, ax, s) in enumerate(stations):
        ang_src = loop_angles(V[hole], sh, ax, ref)
        ang = blend_angles(ang_src, N_ARM, s)
        if uni_prev is None and s >= 1.0:
            uni_prev = ang
        if k >= n_st - 3:  # last forearm rings: blend toward the palm design angles
            w = (k - (n_st - 4)) / 3.0
            d2 = match_cyclic(ang, dst)
            ang = (1 - w) * ang + w * d2
        P = cast(body, reg, np.repeat(c[None, :], N_ARM, axis=0), ring_dirs(ax, ref, ang))
        rings.append(cg.add(P, reg))
    _ = src
    cg.bridge(hole, rings[0], reg)
    for k in range(len(rings) - 1):
        cg.bridge(rings[k], rings[k + 1], reg)
    # underside seam: the ring vertex pointing most downward/inward
    Vn = cg.V
    j = int(np.argmin((Vn[rings[3]] - stations[3][0]) @ v3(0, 0, 1)))
    jh = int(np.argmin(np.linalg.norm(Vn[hole] - Vn[rings[0][j]], axis=1)))
    cg.seam(hole[jh], rings[0][j])
    for k in range(len(rings) - 1):
        cg.seam(rings[k][j], rings[k + 1][j])
    cg.groups[f"wrist_{side}"] = rings[-1].tolist()
    return rings[-1]


def _palm_design(hand) -> Arr:
    s = np.array([1.0, 0.5, 0.0, -0.5, -1.0])
    W, T = hand.width, hand.thickness
    dors = [hand.side * x * W * 0.45 + hand.dorsal * T * 0.5 for x in s]
    palm = [hand.side * x * W * 0.45 - hand.dorsal * T * 0.5 for x in s[::-1]]
    return np.array(dors + palm)


def _hand(cg: Cage, wrist_ring: Arr, side: str) -> None:
    lm, body = cg.lm, cg.body
    S = lm.S
    reg = f"hand_{side}"
    hand = lm.hands[side]
    V = cg.V
    design = _palm_design(hand)
    # align the wrist ring to the palm design order (d0..d4, p4..p0)
    target = hand.wrist + design
    best = None
    for flip in (False, True):
        wr = wrist_ring[::-1] if flip else wrist_ring
        for shf in range(N_ARM):
            cand = np.roll(wr, -shf)
            dirs_c = unit_rows(V[cand] - hand.wrist)
            dirs_t = unit_rows(design)
            cost = -float(np.sum(dirs_c * dirs_t))
            if best is None or cost < best[0]:
                best = (cost, cand)
    wr = best[1]
    palm_len = float(np.linalg.norm(hand.knuckle - hand.wrist))
    rings = [wr]
    for t in (0.42, 0.9):
        c = hand.wrist + hand.axis * palm_len * t - hand.dorsal * hand.thickness * 0.05
        P = cast(body, reg, np.repeat(c[None, :], 10, axis=0), design)
        rings.append(cg.add(P, reg))
    # palm faces, leaving the radial quad between ring 0 and 1 open for the thumb
    for k in range(2):
        for i in range(10):
            j = (i + 1) % 10
            if k == 0 and i == 9:
                continue
            cg.quad(rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i], reg)
    knuckle = rings[2]
    d = knuckle[:5]
    p = knuckle[5:][::-1]  # p0..p4
    fingers = {fg.name: fg for fg in hand.fingers}
    for fi, name in enumerate(("f_index", "f_middle", "f_ring", "f_pinky")):
        base = np.array([d[fi], d[fi + 1], p[fi + 1], p[fi]])
        _finger(cg, base, fingers[name], reg, hand)
    for k in range(2):  # palm island cut along the ulnar (pinky-side) edge
        cg.seam(rings[k][4], rings[k + 1][4])
    tb = np.array([rings[0][0], rings[1][0], rings[1][9], rings[0][9]])
    _finger(cg, tb, fingers["thumb"], reg, hand, thumb=True)
    cg.seam_loop(wr)


def unit_rows(A: Arr) -> Arr:
    return A / np.linalg.norm(A, axis=1, keepdims=True)


def _finger(cg: Cage, base: Arr, fg, reg: str, hand, thumb: bool = False) -> None:
    body = cg.body
    J = fg.joints
    V = cg.V
    stations = []
    if thumb:
        stations = [(J[0] + (J[1] - J[0]) * 0.55, 0), (J[1], 1), (J[1] + (J[2] - J[1]) * 0.5, 1), (J[2], 2),
                    (J[2] + (J[3] - J[2]) * 0.55, 2)]
    else:
        stations = [(J[0] + (J[1] - J[0]) * 0.5, 0), (J[1], 1), (J[1] + (J[2] - J[1]) * 0.5, 1), (J[2], 2),
                    (J[2] + (J[3] - J[2]) * 0.55, 2)]
    prev = base
    cg.seam_loop(base)  # each finger is its own UV island: base loop + one palmar-ulnar cut line
    bc = V[base].mean(axis=0)
    first_axis = unit(J[1] - J[0])
    # angles of the base loop corners around the finger axis
    ref = fg.dorsal
    src = loop_angles(V[base], bc, first_axis, ref)
    for k, (c, seg) in enumerate(stations):
        ax = unit(J[seg + 1] - J[seg])
        if 0 < k and stations[k][1] != stations[k - 1][1]:
            ax = unit(J[seg + 1] - J[seg - 1])
        ang = blend_angles(src, 4, min(1.0, 0.5 + 0.5 * k))
        P = cast(body, reg, np.repeat(c[None, :], 4, axis=0), ring_dirs(ax, ref, ang), tmax=0.06, steps=120)
        ring = cg.add(P, reg)
        cg.bridge(prev, ring, reg)
        cg.seam(prev[2], ring[2])
        prev = ring
    cg.quad(prev[0], prev[1], prev[2], prev[3], reg)
    _ = hand


def _leg(cg: Cage, torso: dict, side: str) -> Arr:
    lm, body = cg.lm, cg.body
    S = lm.S
    reg = f"leg_{side}"
    r0 = torso["rings"][0]
    N = N_TORSO
    V = cg.V
    if "crotch_v" not in torso:
        cz = lm.P("crotch") + v3(0, 0.0, -0.002 * S)
        torso["crotch_v"] = int(cg.add(cz, "torso")[0])
    cv = torso["crotch_v"]
    if side == "L":
        top = np.array([r0[i] for i in range(0, N // 2 + 1)] + [cv])
    else:
        top = np.array([r0[i % N] for i in range(N // 2, N + 1)] + [cv])
    hp, kn, an = lm.side_pt("hip", side), lm.side_pt("knee", side), lm.side_pt("ankle", side)
    a_th, a_sh = unit(kn - hp), unit(an - kn)
    ref = v3(0, -1, 0)
    V = cg.V
    c0 = V[top].mean(axis=0)
    z_c = lm.P("crotch")[2]
    L_th = float(np.linalg.norm(kn - hp))
    L_sh = float(np.linalg.norm(an - kn))
    stations: list[tuple[Arr, Arr]] = []
    t0 = (hp[2] - (z_c - 0.035 * S)) / (hp[2] - kn[2])
    for t in (t0, t0 + (1 - t0) * 0.25, t0 + (1 - t0) * 0.5, t0 + (1 - t0) * 0.72, 0.88):
        stations.append((hp + a_th * L_th * t, a_th))
    stations.append((kn, unit(a_th + a_sh)))
    for t in (0.1, 0.27, 0.45, 0.63, 0.8, 0.93):
        stations.append((kn + a_sh * L_sh * t, a_sh))
    src = loop_angles(V[top], c0, a_th, ref)
    rings = []
    for k, (c, ax) in enumerate(stations):
        ang = blend_angles(loop_angles(V[top], c0, ax, ref), N_LEG, min(1.0, 0.5 + 0.25 * k))
        P = cast(body, reg, np.repeat(c[None, :], N_LEG, axis=0), ring_dirs(ax, ref, ang))
        rings.append(cg.add(P, reg))
    _ = src
    cg.bridge(top, rings[0], reg)
    for k in range(len(rings) - 1):
        cg.bridge(rings[k], rings[k + 1], reg)
    cg.seam_loop(top)
    # inner-leg seam: crotch vertex line (index N_LEG - 1 in every ring follows it)
    cg.seam(top[-1], rings[0][-1])
    for k in range(len(rings) - 1):
        cg.seam(rings[k][-1], rings[k + 1][-1])
    cg.groups[f"ankle_{side}"] = rings[-1].tolist()
    return rings[-1]


def _foot(cg: Cage, ankle: Arr, side: str) -> None:
    lm, body = cg.lm, cg.body
    S = lm.S
    reg = f"foot_{side}"
    hb, tt = lm.side_pt("heel_back", side), lm.side_pt("toe_tip", side)
    fwd = unit(tt - hb)
    L = float(np.linalg.norm(tt - hb))
    lat = v3(1, 0, 0) if side == "L" else v3(-1, 0, 0)
    up = v3(0, 0, 1)
    us = [0.035, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.71, 0.82, 0.91, 0.965]
    ang = 2 * math.pi * np.arange(N_FOOT) / N_FOOT
    rings = []
    for u in us:
        c = hb + fwd * L * u + up * (0.018 * S * (1 - u) + 0.006 * S)
        if 0.15 < u < 0.7:
            c = c + up * 0.014 * S * math.sin((u - 0.15) / 0.55 * math.pi)
        e1, e2 = up, unit(np.cross(fwd, up)) if side == "R" else -unit(np.cross(fwd, up))
        D = np.cos(ang)[:, None] * e1 + np.sin(ang)[:, None] * e2
        P = cast(body, reg, np.repeat(c[None, :], N_FOOT, axis=0), D, tmax=0.12, steps=160)
        rings.append(cg.add(P, reg))
    top = [10, 11, 0, 1, 2]
    k0, k1 = 1, 6
    for k in range(len(rings) - 1):
        for i in range(N_FOOT):
            j = (i + 1) % N_FOOT
            if k0 <= k < k1 and i in (10, 11, 0, 1):
                continue
            cg.quad(rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i], reg)
    hole = [rings[k0][i] for i in top]
    hole += [rings[k][2] for k in range(k0 + 1, k1)]
    hole += [rings[k1][i] for i in top[::-1]]
    hole += [rings[k][10] for k in range(k1 - 1, k0, -1)]
    hole = np.array(hole)
    assert len(hole) == N_LEG
    V = cg.V
    best = None
    for flip in (False, True):
        hh = hole[::-1] if flip else hole
        for shf in range(N_LEG):
            cand = np.roll(hh, -shf)
            cost = float(np.sum((V[cand] - V[ankle]) ** 2))
            if best is None or cost < best[0]:
                best = (cost, cand)
    cg.bridge(ankle, best[1], reg)
    cg.seam_loop(best[1])
    cg.seam_loop(ankle)  # the ankle band is its own small island, opened on the inner line
    cg.seam(ankle[-1], best[1][-1])
    # caps (heel and toe), 12-loops as 2x4 grids
    for ring, sgn in ((rings[0], -1.0), (rings[-1], 1.0)):
        loop = np.roll(ring, -5)  # start near the bottom-medial corner
        cg.fill_grid(loop[::-1] if sgn < 0 else loop, 2, 4, reg, bulge=fwd * sgn * 0.006 * S)
    # UV islands: heel cap, toe cap, sole (between the lower-side lines j=4..8) and the upper,
    # which is opened from the front of the ankle hole to the toe cap along the top line j=0
    cg.seam_loop(rings[0])
    cg.seam_loop(rings[-1])
    for k in range(len(rings) - 1):
        cg.seam(rings[k][4], rings[k + 1][4])
        cg.seam(rings[k][8], rings[k + 1][8])
        if k >= k1:
            cg.seam(rings[k][0], rings[k + 1][0])


# ---------------------------------------------------------------------------------------------
# Topology utilities
# ---------------------------------------------------------------------------------------------
def orient_faces(F: Arr, V: Arr) -> Arr:
    """Make winding consistent across the (closed) mesh, outward by signed volume."""
    F = F.copy()
    m = len(F)
    edge_faces: dict[tuple[int, int], list[int]] = {}
    for fi, f in enumerate(F):
        for a in range(4):
            u, v = int(f[a]), int(f[(a + 1) % 4])
            edge_faces.setdefault((min(u, v), max(u, v)), []).append(fi)
    seen = np.zeros(m, dtype=bool)
    for start in range(m):
        if seen[start]:
            continue
        seen[start] = True
        stack = [start]
        while stack:
            fi = stack.pop()
            f = F[fi]
            for a in range(4):
                u, v = int(f[a]), int(f[(a + 1) % 4])
                for g in edge_faces[(min(u, v), max(u, v))]:
                    if g == fi or seen[g]:
                        continue
                    fg = list(F[g])
                    # neighbour must traverse (v, u)
                    same = any(fg[b] == u and fg[(b + 1) % 4] == v for b in range(4))
                    if same:
                        F[g] = F[g][::-1]
                    seen[g] = True
                    stack.append(g)
    vol = 0.0
    for f in F:
        a, b, c, d = V[f]
        vol += np.dot(a, np.cross(b, c)) + np.dot(a, np.cross(c, d))
    if vol < 0:
        F = F[:, ::-1]
    return F


def check_manifold(F: Arr) -> dict:
    counts: dict[tuple[int, int], int] = {}
    for f in F:
        for a in range(len(f)):
            u, v = int(f[a]), int(f[(a + 1) % len(f)])
            k = (min(u, v), max(u, v))
            counts[k] = counts.get(k, 0) + 1
    bad = {k: c for k, c in counts.items() if c != 2}
    return {"edges": len(counts), "non_manifold": len(bad), "examples": list(bad.items())[:8]}


def catmull_clark(V: Arr, F: Arr, vpin: Arr, seams: set, vreg: list[str]) -> tuple[Arr, Arr, Arr, set, list[str]]:
    nv = len(V)
    m = len(F)
    e_of: dict[tuple[int, int], int] = {}
    E: list[tuple[int, int]] = []
    ef: list[list[int]] = []
    fe = np.zeros((m, 4), dtype=int)
    for fi, f in enumerate(F):
        for a in range(4):
            u, v = int(f[a]), int(f[(a + 1) % 4])
            k = (min(u, v), max(u, v))
            if k not in e_of:
                e_of[k] = len(E)
                E.append(k)
                ef.append([])
            ei = e_of[k]
            ef[ei].append(fi)
            fe[fi, a] = ei
    E_arr = np.array(E)
    FP = V[F].mean(axis=1)
    EP = np.zeros((len(E), 3))
    for ei, (u, v) in enumerate(E):
        fs = ef[ei]
        if len(fs) == 2:
            EP[ei] = (V[u] + V[v] + FP[fs[0]] + FP[fs[1]]) / 4
        else:
            EP[ei] = (V[u] + V[v]) / 2
    # vertex points
    Qsum = np.zeros((nv, 3))
    Qn = np.zeros(nv)
    for fi, f in enumerate(F):
        for v in f:
            Qsum[v] += FP[fi]
            Qn[v] += 1
    Rsum = np.zeros((nv, 3))
    Rn = np.zeros(nv)
    mids = (V[E_arr[:, 0]] + V[E_arr[:, 1]]) / 2
    np.add.at(Rsum, E_arr[:, 0], mids)
    np.add.at(Rsum, E_arr[:, 1], mids)
    np.add.at(Rn, E_arr[:, 0], 1)
    np.add.at(Rn, E_arr[:, 1], 1)
    n = Rn
    Q = Qsum / Qn[:, None]
    R = Rsum / Rn[:, None]
    NV = (Q + 2 * R + (n[:, None] - 3) * V) / n[:, None]
    pin = np.asarray(vpin, dtype=bool)
    NV[pin] = V[pin]
    newV = np.concatenate([NV, EP, FP])
    e_pin = pin[E_arr[:, 0]] & pin[E_arr[:, 1]]
    f_pin = pin[F].all(axis=1)
    # keep pinned edge points on the straight line (lid margin / lip line stay exact)
    newV[nv:nv + len(E)][e_pin] = mids[e_pin]
    newV[nv + len(E):][f_pin] = FP[f_pin]
    new_pin = np.concatenate([pin, e_pin, f_pin])
    new_reg = list(vreg) + [vreg[u] for u, _ in E] + [vreg[int(f[0])] for f in F]
    newF = []
    for fi, f in enumerate(F):
        fp = nv + len(E) + fi
        ep = [nv + fe[fi, a] for a in range(4)]
        for a in range(4):
            newF.append((f[a], ep[a], fp, ep[(a + 3) % 4]))
    new_seams = set()
    for (u, v) in seams:
        ei = e_of.get((u, v))
        if ei is None:
            continue
        p = nv + ei
        new_seams.add((min(u, p), max(u, p)))
        new_seams.add((min(v, p), max(v, p)))
    return newV, np.array(newF), new_pin, new_seams, new_reg


def project(body: Body, V: Arr, F: Arr, pin: Arr, iters: int = 14, relax: float = 0.45) -> Arr:
    V = V.copy()
    E = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 3]], F[:, [3, 0]]])
    E = np.unique(np.sort(E, axis=1), axis=0)
    deg = np.zeros(len(V))
    np.add.at(deg, E[:, 0], 1)
    np.add.at(deg, E[:, 1], 1)
    free = ~np.asarray(pin, dtype=bool)

    def newton(P: Arr, steps: int) -> Arr:
        for _ in range(steps):
            d = body.sdf(P)
            g = body.grad(P)
            gn = np.maximum(np.linalg.norm(g, axis=1), 1e-6)
            step = np.clip(d, -0.02, 0.02) / gn
            P = P - (g / gn[:, None]) * step[:, None]
        return P

    for it in range(iters):
        V[free] = newton(V[free], 2)
        acc = np.zeros_like(V)
        np.add.at(acc, E[:, 0], V[E[:, 1]])
        np.add.at(acc, E[:, 1], V[E[:, 0]])
        L = acc / deg[:, None] - V
        g = body.grad(V[free])
        nrm = g / np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-9)
        Lf = L[free]
        Lt = Lf - np.sum(Lf * nrm, axis=1, keepdims=True) * nrm
        lam = relax * (1.0 - 0.5 * it / max(iters - 1, 1))
        V[free] = V[free] + lam * Lt
    V[free] = newton(V[free], 4)
    return V


# ---------------------------------------------------------------------------------------------
# Eye placeholders
# ---------------------------------------------------------------------------------------------
def eye_mesh(lm: Landmarks, side: str, seg: int = 24, rings: int = 16) -> tuple[Arr, Arr, Arr]:
    """UV sphere facing -Y. Returns V, quad/tri faces (padded with -1) and a material id per
    face: 0 sclera, 1 iris, 2 pupil (PLACEHOLDER until the eye shader of M1-RND-04)."""
    E = lm.side_pt("eye", side)
    r = lm.eye_r
    V = [E + v3(0, -r, 0)]
    for i in range(1, rings):
        th = math.pi * i / rings  # 0 at the front pole
        for j in range(seg):
            ph = 2 * math.pi * j / seg
            V.append(E + r * v3(math.sin(th) * math.cos(ph), -math.cos(th), math.sin(th) * math.sin(ph)))
    V.append(E + v3(0, r, 0))
    V = np.array(V)
    F, M = [], []
    iris_t = 0.51  # radians from the front pole: iris ~ 12.9 mm across on a 26 mm globe
    pupil_t = 0.16

    def mat(th: float) -> int:
        return 2 if th < pupil_t else (1 if th < iris_t else 0)

    for j in range(seg):
        F.append((0, 1 + (j + 1) % seg, 1 + j, -1))
        M.append(mat(0.5 * math.pi / rings))
    for i in range(rings - 2):
        th = math.pi * (i + 1.5) / rings
        for j in range(seg):
            a = 1 + i * seg + j
            b = 1 + i * seg + (j + 1) % seg
            F.append((a, b, b + seg, a + seg))
            M.append(mat(th))
    last = len(V) - 1
    base = 1 + (rings - 2) * seg
    for j in range(seg):
        F.append((base + j, base + (j + 1) % seg, last, -1))
        M.append(0)
    F = np.array(F)
    for k, f in enumerate(F):  # wind every face outward
        idx = f[f >= 0]
        a, b, c = V[idx[0]], V[idx[1]], V[idx[2]]
        if np.dot(np.cross(b - a, c - a), V[idx].mean(axis=0) - E) < 0:
            F[k, : len(idx)] = idx[::-1]
    return V, F, np.array(M)


# ---------------------------------------------------------------------------------------------
# Whole-mesh generation
# ---------------------------------------------------------------------------------------------
def generate(params: dict, subdiv: int = 1, log=print) -> dict:
    """params -> final body mesh (numpy). Returns V, F (quads), seams, pins, landmarks, body."""
    import time

    t0 = time.time()
    lm = Landmarks(params)
    body = Body(lm)
    cg = build_cage(body)
    V0 = cg.V
    F0 = orient_faces(np.array(cg.F), V0)
    man = check_manifold(F0)
    log(f"cage: {len(V0)} verts, {len(F0)} quads, non-manifold edges {man['non_manifold']} "
        f"({time.time() - t0:.1f}s)")
    if man["non_manifold"]:
        log(f"  examples: {man['examples']}")
    # drop lattice points that ended up inside removed cells
    used = np.unique(F0)
    remap = -np.ones(len(V0), dtype=int)
    remap[used] = np.arange(len(used))
    V0 = V0[used]
    F0 = remap[F0]
    pin = np.array(cg.vpin)[used]
    reg = [cg.vreg[i] for i in used]
    seams = {(min(remap[a], remap[b]), max(remap[a], remap[b])) for a, b in cg.seams if remap[a] >= 0 and remap[b] >= 0}
    def _remap(v):
        if v and isinstance(v[0], list):
            return [_remap(x) for x in v]
        return [int(remap[i]) for i in v if remap[i] >= 0]

    groups = {k: _remap(v) for k, v in cg.groups.items()}
    cg.groups = groups
    V, F = V0, F0
    for _ in range(subdiv):
        V, F, pin, seams, reg = catmull_clark(V, F, pin, seams, reg)
    log(f"subdivided: {len(V)} verts, {len(F)} quads ({time.time() - t0:.1f}s)")
    V = project(body, V, F, pin)
    V[:, 2] = np.maximum(V[:, 2], 0.0)  # soles stand exactly on the ground plane
    log(f"projected ({time.time() - t0:.1f}s)")
    return {"V": V, "F": F, "pin": pin, "seams": seams, "lm": lm, "body": body, "cage_V": V0, "cage_F": F0,
            "groups": cg.groups, "n_cage_v": len(V0), "reg": reg}
