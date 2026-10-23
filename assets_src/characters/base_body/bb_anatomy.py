"""Anatomy as a signed distance field (M1-CHR-01). Pure numpy, no bpy.

The body surface is a smooth union of simple primitives (ellipsoids, round cones, round boxes)
placed on the landmarks from bb_params. Primitives are grouped into REGIONS (torso, head,
arm_L, hand_L, leg_L, foot_L, ...). The cage builder ray-casts each region separately (so a torso
ring never snaps onto an arm), and the final surface projection uses the union of all regions.

This is the "sculpt" stage of the SPEC §7.3 pipeline: muscle bellies, fat pads and bony
landmarks are primitives whose size is driven by the muscle / mass / femininity sliders.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from bb_params import Landmarks, rot, unit, v3

Arr = np.ndarray
LID_THICKNESS = 0.0019  # lid margin thickness over the globe (m at S = 1)


# ---------------------------------------------------------------------------------------------
# Primitive SDFs, all vectorised over P with shape (n, 3)
# ---------------------------------------------------------------------------------------------
def frame_from(axis: Arr, up_hint: Arr) -> Arr:
    """Rows = local x (along axis), y, z. Used to orient anisotropic primitives."""
    x = unit(axis)
    y = np.cross(up_hint, x)
    if np.linalg.norm(y) < 1e-6:
        y = np.cross(v3(1, 0, 0), x)
    y = unit(y)
    z = np.cross(x, y)
    return np.stack([x, y, z])


def sd_ellipsoid(P: Arr, c: Arr, r: Arr, axes: Arr | None = None) -> Arr:
    q = P - c
    if axes is not None:
        q = q @ axes.T
    k0 = np.linalg.norm(q / r, axis=1)
    k1 = np.linalg.norm(q / (r * r), axis=1)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)


def sd_round_cone(P: Arr, a: Arr, b: Arr, r1: float, r2: float) -> Arr:
    """Inigo Quilez's exact round-cone distance (sphere r1 at a swept to sphere r2 at b)."""
    ba = b - a
    l2 = float(ba @ ba)
    rr = r1 - r2
    a2 = l2 - rr * rr
    il2 = 1.0 / l2
    pa = P - a
    y = pa @ ba
    z = y - l2
    w = pa * l2 - np.outer(y, ba)
    x2 = np.einsum("ij,ij->i", w, w)
    y2 = y * y * l2
    z2 = z * z * l2
    k = np.sign(rr) * rr * rr * x2
    d_b = np.sqrt(x2 + z2) * il2 - r2
    d_a = np.sqrt(x2 + y2) * il2 - r1
    d_m = (np.sqrt(np.maximum(x2 * a2 * il2, 0.0)) + y * rr) * il2 - r1
    return np.where(np.sign(z) * a2 * z2 > k, d_b, np.where(np.sign(y) * a2 * y2 < k, d_a, d_m))


def sd_round_box(P: Arr, c: Arr, half: Arr, radius: float, axes: Arr) -> Arr:
    q = np.abs((P - c) @ axes.T) - half + radius
    outside = np.linalg.norm(np.maximum(q, 0.0), axis=1)
    inside = np.minimum(np.max(q, axis=1), 0.0)
    return outside + inside - radius


def smin(a: Arr, b: Arr, k: float) -> Arr:
    if k <= 0:
        return np.minimum(a, b)
    h = np.maximum(k - np.abs(a - b), 0.0) / k
    return np.minimum(a, b) - h * h * k * 0.25


def smax(a: Arr, b: Arr, k: float) -> Arr:
    return -smin(-a, -b, k)


# ---------------------------------------------------------------------------------------------
# Regions
# ---------------------------------------------------------------------------------------------
@dataclass
class Shape:
    """A primitive distance function with a bounding sphere (for cheap far-field culling)."""

    fn: Callable[[Arr], Arr]
    c: Arr
    R: float
    blend: Callable[[Arr, Arr], Arr] | None = None  # op "blend": fn(P, d_so_far) -> new d


@dataclass
class Prim:
    shape: Shape
    k: float  # blend radius into the region accumulated so far
    op: str = "union"  # union | subtract

    def apply(self, d: Arr, P: Arr) -> Arr:
        """Blend this primitive into the running field `d`. The bounding-sphere distance `dc` is a
        lower bound of the primitive's distance, so wherever dc >= d + k (union) or dc >= k - d
        (subtraction) the primitive provably cannot change `d` and is not evaluated. Exact."""
        dc = np.linalg.norm(P - self.shape.c, axis=1) - self.shape.R
        if self.op == "blend":
            m = dc < 0.0
            if not m.any():
                return d
            out = d.copy()
            out[m] = self.shape.blend(P[m], d[m])
            return out
        if self.op == "union":
            m = dc < d + self.k
        else:
            m = dc < self.k - d
        if not m.any():
            return d
        out = d.copy()
        v = self.shape.fn(P[m])
        if self.op == "union":
            out[m] = smin(d[m], v, self.k)
        else:
            out[m] = smax(d[m], -v, self.k)
        return out


def _apply(d: Arr, pr: Prim, P: Arr) -> Arr:
    return pr.apply(d, P)


@dataclass
class Region:
    name: str
    prims: list[Prim] = field(default_factory=list)
    lo: Arr | None = None
    hi: Arr | None = None
    disp: list[Callable[[Arr], Arr]] = field(default_factory=list)
    post: list[Prim] = field(default_factory=list)  # blended after the displacement (nose)

    def add(self, shape: Shape, k: float, op: str = "union") -> None:
        self.prims.append(Prim(shape, k, op))
        lo, hi = shape.c - shape.R, shape.c + shape.R
        self.lo = lo if self.lo is None else np.minimum(self.lo, lo)
        self.hi = hi if self.hi is None else np.maximum(self.hi, hi)

    def sdf(self, P: Arr) -> Arr:
        # points far outside the region's box get the box distance (a lower bound)
        q = np.maximum(np.maximum(self.lo - P, P - self.hi), 0.0)
        box = np.linalg.norm(q, axis=1)
        near = box < 0.05
        out = box + 0.05
        if near.any():
            Pn = P[near]
            d = np.full(len(Pn), 1e3)
            for pr in self.prims:
                d = _apply(d, pr, Pn)
            for fn in self.disp:
                d = d - fn(Pn)
            for pr in self.post:
                d = _apply(d, pr, Pn)
            out[near] = d
        return out

    def sdf_no_post(self, P: Arr) -> Arr:
        d = np.full(len(P), 1e3)
        for pr in self.prims:
            d = _apply(d, pr, P)
        for fn in self.disp:
            d = d - fn(P)
        return d


class Body:
    """All regions of one body, plus the joined field."""

    def __init__(self, lm: Landmarks) -> None:
        self.lm = lm
        self.regions: dict[str, Region] = {}
        self.k_join = 0.014 * lm.S
        self.k_head_neck = 0.020 * lm.S
        self.post: list[Prim] = []  # applied after the regional union (eyeballs, sockets)
        self.face = None  # bb_face.Face, set by _build_head
        _build_torso(self)
        _build_head(self)
        for side in ("L", "R"):
            _build_arm(self, side)
            _build_hand(self, side)
            _build_leg(self, side)
            _build_foot(self, side)

    def region(self, name: str) -> Region:
        if name not in self.regions:
            self.regions[name] = Region(name)
        return self.regions[name]

    def sdf(self, P: Arr, only: str | None = None) -> Arr:
        if only is not None:
            d = self.regions[only].sdf(P)
            if only == "head":
                for pr in self.post:
                    d = _apply(d, pr, P)
            return d
        d = None
        for name, reg in self.regions.items():
            v = reg.sdf(P)
            if d is None:
                d = v
            elif name == "head":
                # the jaw and skull blend into the neck with a much wider fillet than the limbs:
                # a narrow one leaves a hard shelf under the mandible (review-sweep-B, M1-CHR-01)
                d = smin(d, v, self.k_head_neck)
            else:
                d = smin(d, v, self.k_join)
        for pr in self.post:
            d = _apply(d, pr, P)
        return d

    def grad(self, P: Arr, only: str | None = None, eps: float = 4e-4) -> Arr:
        g = np.zeros_like(P)
        for i in range(3):
            e = np.zeros(3)
            e[i] = eps
            g[:, i] = (self.sdf(P + e, only) - self.sdf(P - e, only)) / (2 * eps)
        return g


def _mir(v: Arr, side: str) -> Arr:
    return v if side == "L" else v * np.array([-1.0, 1.0, 1.0])


def _E(c: Arr, r: Arr, axes: Arr | None = None) -> Shape:
    c = np.asarray(c, dtype=float)
    r = np.asarray(r, dtype=float)
    return Shape(lambda P: sd_ellipsoid(P, c, r, axes), c, float(r.max()))


def _C(a: Arr, b: Arr, r1: float, r2: float) -> Shape:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return Shape(lambda P: sd_round_cone(P, a, b, r1, r2), (a + b) / 2, float(np.linalg.norm(b - a)) / 2 + max(r1, r2))


def _B(c: Arr, half: Arr, radius: float, axes: Arr) -> Shape:
    c = np.asarray(c, dtype=float)
    half = np.asarray(half, dtype=float)
    return Shape(lambda P: sd_round_box(P, c, half, radius, axes), c, float(np.linalg.norm(half)))


def _lerp(a: Arr, b: Arr, t: float) -> Arr:
    return a + (b - a) * t


# ---------------------------------------------------------------------------------------------
# Torso and neck
# ---------------------------------------------------------------------------------------------
def _build_torso(body: Body) -> None:
    lm = body.lm
    p, S, h = lm.p, lm.S, lm.h
    f, m, w = float(p["femininity"]), float(p["muscle"]), float(p["mass"])
    R = body.region("torso")
    z_notch = lm.P("notch")[2]
    z_hip = lm.P("hip")[2]
    z_crotch = lm.P("crotch")[2]
    z_waist = lm.P("waist")[2]
    z_nip = lm.P("nipple")[2]
    cw = float(p["chest_width_heads"]) * h
    cd = float(p["chest_depth_heads"]) * h
    ww = float(p["waist_width_heads"]) * h
    hipw = lm.hip_w
    fat = 1.0 + 0.35 * w
    # ribcage: an egg, narrow at the top
    R.add(_E(v3(0, 0.028 * S, z_nip + 0.035 * S), v3(cw * 0.46, cd * 0.47, 0.19 * S)), 0.0)
    R.add(_E(v3(0, 0.03 * S, z_notch - 0.075 * S), v3(cw * 0.40, cd * 0.36, 0.10 * S)), 0.09 * S)
    # abdomen and waist
    abd_d = (0.172 + 0.02 * (1 - f)) * S * fat
    R.add(_E(v3(0, 0.004 * S, z_waist), v3(ww * 0.5, abd_d * 0.5, 0.15 * S)), 0.14 * S)
    if w > 0.0:
        R.add(_E(v3(0, -0.035 * S, lm.P("navel")[2] + 0.01 * S), v3(ww * 0.42, 0.075 * S * w + 0.02 * S, 0.13 * S)),
              0.06 * S)
    # pelvis, lower belly, glutes
    R.add(_E(v3(0, 0.01 * S, z_hip + 0.03 * S), v3(hipw * 0.44, 0.105 * S * fat, 0.115 * S)), 0.06 * S)
    R.add(_E(v3(0, -0.055 * S, z_crotch + 0.07 * S), v3(0.085 * S, 0.05 * S, 0.06 * S)), 0.04 * S)
    for side in ("L", "R"):
        g = _mir(v3((0.052 + 0.01 * f) * S, (0.05 + 0.008 * f) * S, z_crotch + 0.09 * S), side)
        R.add(_E(g, v3(0.07 * S, (0.058 + 0.01 * f) * S * fat, 0.085 * S)), 0.05 * S)
    # chest: breasts (feminine) or pectorals (muscle)
    for side in ("L", "R"):
        nip = lm.side_pt("nipple", side)
        if float(p["breast"]) > 0.0:
            b = float(p["breast"])
            rb = (0.042 + 0.03 * b) * S
            c = nip + v3(-0.004 * S, (0.03 - 0.006 * b) * S, -0.006 * S)
            R.add(_E(c, v3(rb * 1.08, rb * 0.72, rb * 0.92)), 0.045 * S)
        pec_t = (0.008 + 0.011 * m) * S * (1 - 0.7 * f)
        if pec_t > 0.006 * S:
            # a fan from the sternum toward the armpit, tilted up and out
            c = _mir(v3(0.072 * S, -cd * 0.45 + 0.012 * S, z_nip + 0.04 * S), side)
            fan = frame_from(_mir(v3(0.9, 0.0, 0.42), side), v3(0, -1, 0))
            R.add(_E(c, v3(0.085 * S, 0.055 * S, pec_t), fan), 0.07 * S)
        # scapulae and lats (V-taper grows with muscle)
        sc = _mir(v3(0.07 * S, cd * 0.38, z_notch - 0.1 * S), side)
        R.add(_E(sc, v3(0.075 * S, 0.035 * S, 0.095 * S)), 0.05 * S)
        lat = _mir(v3(cw * 0.37, 0.03 * S, z_notch - 0.19 * S), side)
        R.add(_E(lat, v3((0.035 + 0.035 * m) * S, 0.075 * S, 0.12 * S)), 0.05 * S)
        # trapezius slope and clavicle
        acro = lm.side_pt("acromion", side)
        tr_a = v3(0, 0.032 * S, z_notch + 0.055 * S)
        tr_b = _lerp(tr_a, acro, 0.8) + v3(0, 0.006 * S, -0.012 * S)
        R.add(_C(tr_a, tr_b, (0.026 + 0.01 * m) * S, (0.019 + 0.006 * m) * S), 0.05 * S)
        R.add(_C(lm.side_pt("clavicle_in", side), acro + _mir(v3(-0.03 * S, -0.006 * S, -0.012 * S), side),
                 0.010 * S, 0.010 * S), 0.03 * S)
        # sternocleidomastoid: mastoid to the sternal notch
        mast = _mir(v3(0.042 * S, 0.012 * S, lm.P("chin")[2] + 0.30 * h), side)
        R.add(_C(mast, lm.side_pt("clavicle_in", side) + _mir(v3(-0.008 * S, 0, 0.012 * S), side), 0.012 * S,
                 0.010 * S), 0.03 * S)
    # neck column
    nw = float(p["neck_width_ratio"]) * lm.head_w
    nb, sb = lm.P("neck_base"), lm.P("skull_base")
    R.add(_C(nb + v3(0, 0.01 * S, 0), sb, nw * 0.56, nw * 0.5), 0.05 * S)


# ---------------------------------------------------------------------------------------------
# Head
# ---------------------------------------------------------------------------------------------
def _spline(xs: list[float], ys: list[float], n: int = 200) -> tuple[Arr, Arr]:
    """Catmull-Rom through control points, densely sampled (for np.interp profiles)."""
    P = np.stack([xs, ys], axis=1).astype(float)
    P = np.concatenate([P[:1] * 2 - P[1:2], P, P[-1:] * 2 - P[-2:-1]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n // (len(P) - 3), endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-2])
    o = np.array(out)
    order = np.argsort(o[:, 0])
    return o[order, 0], o[order, 1]


def _build_head(body: Body) -> None:
    """Head = smooth 'egg' (cranium, lower face, jaw, chin, zygoma) + the bb_face sculpt.

    The sculpt is a heightfield in face space (soft forms, lids, lips) plus primitives blended
    after it (the nose, nostrils subtracted). Ears are separate meshes (bb_ear), rooted into a
    low mound here, because a ray-cast head lattice can't resolve a helix or the gap behind it.
    """
    import bb_face

    lm = body.lm
    p, h, S = lm.p, lm.h, lm.S
    R = body.region("head")
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    face = bb_face.Face(lm)
    body.face = face
    # the lofted head solid (cranium, face planes, jaw line and under-chin in one field)
    R.add(Shape(face.loft.sdf, v3(0, yc, zc + 0.5 * h), 0.62 * h), 0.0)
    # ear root mound (the ear itself is a separate mesh, asha_ears / bb_ear)
    for side in ("L", "R"):
        ec = lm.side_pt("ear", side)
        R.add(_E(ec + _mir(v3(-0.004 * S, 0.004 * S, 0), side), v3(0.010 * S, 0.014 * S, 0.024 * S)), 0.010 * S)
    _ = p
    R.disp.append(face.disp)

    def surface_y(x: float, z: float) -> float:
        """y of the head (egg + heightfield) in front of (x, z): bisection along -Y."""
        lo, hi = yc, yc - 0.6 * h  # lo inside, hi outside
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            dm = R.sdf_no_post(np.array([[x, mid, z]]))[0]
            if dm <= 0:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    for kind, a in face.nose_spec(surface_y):
        if kind == "cone":
            R.post.append(Prim(_C(a["a"], a["b"], a["r1"], a["r2"]), a["k"]))
        else:
            axes = np.eye(3)
            if "rot_x" in a:
                axes = (rot(v3(1, 0, 0), a["rot_x"]) @ axes.T).T
            if "rot_z" in a:
                axes = (rot(v3(0, 0, 1), a["rot_z"]) @ axes.T).T
            op = "subtract" if kind == "hole" else "union"
            R.post.append(Prim(_E(a["c"], a["r"], axes), a["k"], op))
    # lids: a shell around each globe with the almond aperture cut through it, added after the
    # regional union so the lids hug the eyeball (the eyeball itself is a separate mesh)
    r_e = lm.eye_r
    for side in ("L", "R"):
        e = lm.side_pt("eye", side)
        fr = face.eyes[side]
        bl = (lambda fr_: (lambda P, d: fr_.eye_skin(P, d, LID_THICKNESS * S, 0.0009 * S)))(fr)
        body.post.append(Prim(Shape(lambda P: P[:, 0] * 0.0, e, 0.034 * S, bl), 0.0, "blend"))


# ---------------------------------------------------------------------------------------------
# Limbs
# ---------------------------------------------------------------------------------------------
def _build_arm(body: Body, side: str) -> None:
    lm = body.lm
    p, S = lm.p, lm.S
    f, m, w = float(p["femininity"]), float(p["muscle"]), float(p["mass"])
    R = body.region(f"arm_{side}")
    sh, el, wr = lm.side_pt("shoulder", side), lm.side_pt("elbow", side), lm.side_pt("wrist", side)
    a_up = unit(el - sh)
    a_fo = unit(wr - el)
    fat = 1.0 + 0.3 * w
    mus = 1.0 + 0.45 * m - 0.15 * f
    fwd = v3(0, -1, 0)
    up_ax = frame_from(a_up, v3(0, 0, 1))
    fo_ax = frame_from(a_fo, v3(0, 0, 1))
    # deltoid cap over the joint
    R.add(_C(sh + v3(0, 0, 0.012 * S) - a_up * 0.012 * S, sh + a_up * 0.13 * S, 0.047 * S * mus, 0.028 * S), 0.0)
    # humerus sleeve
    R.add(_C(sh + a_up * 0.04 * S, el, 0.039 * S * fat * (1 + 0.25 * m), 0.031 * S * fat * (1 + 0.15 * m)), 0.04 * S)
    # biceps (front) and triceps (back)
    bc = _lerp(sh, el, 0.58) + fwd * 0.012 * S
    R.add(_E(bc, v3(0.085 * S, (0.024 + 0.014 * m) * S, (0.026 + 0.012 * m) * S), up_ax), 0.03 * S)
    tc = _lerp(sh, el, 0.42) - fwd * 0.014 * S
    R.add(_E(tc, v3(0.095 * S, (0.026 + 0.012 * m) * S * fat, (0.028 + 0.01 * m) * S), up_ax), 0.03 * S)
    # elbow
    R.add(_E(el + fwd * -0.006 * S, v3(0.03 * S, 0.03 * S, 0.028 * S), up_ax), 0.03 * S)
    # forearm: flexor/extensor mass near the elbow, flat wrist
    R.add(_C(el, wr, 0.033 * S * fat * mus ** 0.5, 0.022 * S), 0.03 * S)
    fm = _lerp(el, wr, 0.27)
    R.add(_E(fm, v3(0.085 * S, (0.034 + 0.01 * m) * S * fat, (0.028 + 0.008 * m) * S * fat), fo_ax), 0.035 * S)
    hand = lm.hands[side]
    wax = np.stack([hand.axis, hand.side, hand.dorsal])
    R.add(_E(wr - hand.axis * 0.01 * S, v3(0.03 * S, 0.026 * S, 0.018 * S), wax), 0.03 * S)


def _build_hand(body: Body, side: str) -> None:
    lm = body.lm
    S = lm.S
    hand = lm.hands[side]
    R = body.region(f"hand_{side}")
    ax = np.stack([hand.axis, hand.side, hand.dorsal])
    L, W, T = hand.length, hand.width, hand.thickness
    palm_len = float(np.linalg.norm(hand.knuckle - hand.wrist))
    pc = hand.wrist + hand.axis * palm_len * 0.52 - hand.dorsal * T * 0.05
    R.add(_B(pc, v3(palm_len * 0.5, W * 0.47, T * 0.4), T * 0.38, ax), 0.0)
    # thenar and hypothenar pads on the palm side
    th = hand.wrist + hand.axis * palm_len * 0.32 + hand.side * W * 0.24 - hand.dorsal * T * 0.3
    R.add(_E(th, v3(palm_len * 0.30, W * 0.2, T * 0.32), ax), 0.012 * S)
    hy = hand.wrist + hand.axis * palm_len * 0.42 - hand.side * W * 0.3 - hand.dorsal * T * 0.2
    R.add(_E(hy, v3(palm_len * 0.34, W * 0.16, T * 0.3), ax), 0.012 * S)
    for fg in hand.fingers:
        k = 0.01 * S if fg.name == "thumb" else 0.006 * S
        for i in range(3):
            a, b = fg.joints[i], fg.joints[i + 1]
            ra, rb = fg.radius[i], fg.radius[i + 1]
            R.add(_C(a, b, ra, rb), k if i == 0 else 0.002 * S)
    _ = L


def _build_leg(body: Body, side: str) -> None:
    lm = body.lm
    p, S = lm.p, lm.S
    f, m, w = float(p["femininity"]), float(p["muscle"]), float(p["mass"])
    R = body.region(f"leg_{side}")
    hp, kn, an = lm.side_pt("hip", side), lm.side_pt("knee", side), lm.side_pt("ankle", side)
    fat = 1.0 + 0.3 * w
    a_th = unit(kn - hp)
    a_sh = unit(an - kn)
    th_ax = frame_from(a_th, v3(0, -1, 0))
    sh_ax = frame_from(a_sh, v3(0, -1, 0))
    fwd = v3(0, -1, 0)
    lat = _mir(v3(1, 0, 0), side)
    # thigh core
    R.add(_C(hp + v3(0, 0, 0.02 * S) - lat * 0.01 * S, kn, (0.074 + 0.008 * f) * S * fat, 0.05 * S), 0.0)
    # quadriceps (front, vastus bulges above the knee), hamstrings, adductors
    R.add(_E(_lerp(hp, kn, 0.5) + fwd * 0.025 * S, v3(0.19 * S, (0.05 + 0.014 * m) * S, (0.055 + 0.012 * m) * S),
             th_ax), 0.05 * S)
    R.add(_E(_lerp(hp, kn, 0.8) + fwd * 0.02 * S - lat * 0.018 * S, v3(0.07 * S, 0.04 * S, 0.042 * S), th_ax),
          0.03 * S)
    R.add(_E(_lerp(hp, kn, 0.45) - fwd * 0.03 * S, v3(0.18 * S, 0.05 * S * fat, 0.05 * S), th_ax), 0.05 * S)
    R.add(_E(_lerp(hp, kn, 0.2) - lat * 0.035 * S, v3(0.12 * S, 0.045 * S * fat, 0.05 * S), th_ax), 0.05 * S)
    if f > 0.0 or w > 0.0:  # hip / trochanter fat pad
        pad = 0.6 + 0.4 * max(f, w)
        R.add(_E(hp + lat * 0.03 * S + v3(0, 0.01 * S, -0.045 * S), v3(0.045 * S, 0.06 * S, 0.09 * S) * pad), 0.06 * S)
    # knee: patella and condyles
    R.add(_E(kn + fwd * 0.01 * S, v3(0.045 * S, 0.042 * S, 0.05 * S)), 0.03 * S)
    R.add(_E(kn + fwd * 0.042 * S + v3(0, 0, 0.012 * S), v3(0.024 * S, 0.014 * S, 0.028 * S)), 0.02 * S)
    # shin and calf
    R.add(_C(kn, an + v3(0, 0, 0.02 * S), 0.046 * S, 0.029 * S), 0.03 * S)
    calf = _lerp(kn, an, 0.27) - fwd * 0.028 * S
    R.add(_E(calf, v3(0.12 * S, (0.042 + 0.012 * m) * S * fat, (0.046 + 0.012 * m) * S), sh_ax), 0.04 * S)
    R.add(_E(calf - lat * 0.012 * S + v3(0, 0, -0.02 * S), v3(0.1 * S, 0.035 * S, 0.04 * S), sh_ax), 0.03 * S)
    # Achilles and malleoli
    R.add(_C(_lerp(kn, an, 0.6) - fwd * 0.03 * S, an - fwd * 0.03 * S, 0.022 * S, 0.016 * S), 0.03 * S)
    R.add(_E(an + lat * 0.022 * S, v3(0.014 * S, 0.014 * S, 0.016 * S)), 0.015 * S)
    R.add(_E(an - lat * 0.02 * S + v3(0, 0, 0.006 * S), v3(0.014 * S, 0.014 * S, 0.016 * S)), 0.015 * S)


def _build_foot(body: Body, side: str) -> None:
    lm = body.lm
    S = lm.S
    R = body.region(f"foot_{side}")
    an = lm.side_pt("ankle", side)
    hb, ball, tt = lm.side_pt("heel_back", side), lm.side_pt("ball", side), lm.side_pt("toe_tip", side)
    td = _mir(lm.P("toe_dir"), side)
    lat = _mir(v3(1, 0, 0), side)
    ax = np.stack([td, unit(np.cross(v3(0, 0, 1), td)), v3(0, 0, 1)])
    # heel
    R.add(_E(hb + td * 0.035 * S + v3(0, 0, 0.0), v3(0.038 * S, 0.031 * S, 0.035 * S), ax), 0.0)
    # midfoot: arch higher on the medial side
    mid = _lerp(hb, ball, 0.5) + v3(0, 0, 0.012 * S)
    R.add(_B(mid, v3(float(np.linalg.norm(ball - hb)) * 0.45, 0.036 * S, 0.026 * S), 0.022 * S, ax), 0.03 * S)
    R.add(_E(_lerp(hb, ball, 0.45) - lat * 0.012 * S + v3(0, 0, 0.03 * S), v3(0.06 * S, 0.026 * S, 0.026 * S), ax),
          0.03 * S)
    # ankle block joining the leg
    R.add(_E(an + td * 0.012 * S + v3(0, 0, -0.005 * S), v3(0.036 * S, 0.03 * S, 0.034 * S), ax), 0.03 * S)
    # forefoot and toes (a mitten, toes are grooves only at this stage)
    R.add(_B(_lerp(ball, tt, 0.35) + v3(0, 0, -0.004 * S), v3(0.045 * S, 0.044 * S, 0.016 * S), 0.014 * S, ax),
          0.025 * S)
    R.add(_E(ball - lat * 0.018 * S, v3(0.03 * S, 0.026 * S, 0.02 * S), ax), 0.02 * S)
    R.add(_E(tt - td * 0.02 * S - lat * 0.016 * S + v3(0, 0, 0.004 * S), v3(0.022 * S, 0.016 * S, 0.014 * S), ax),
          0.02 * S)
