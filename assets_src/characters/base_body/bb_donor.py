"""Base body on the MakeHuman hm08 donor topology (M1-CHR-03, ADR 0021). Pure numpy, no bpy.

The donor (vendored CC0 data, read by mpfb_data) supplies **topology, a face and hands with
anatomical knowledge, and hand-made skin weights**. Everything else is ours and drives it through
the existing interfaces (parameters JSON, bb_params.Landmarks, the DEF-* skeleton, the asha.md
§6.2 shape names). The heavy modification, in order:

1. **Macro mix**: the donor's own sex / ethnicity / muscle / weight targets, mixed by our sliders
   (`femininity`, `muscle`, `mass`, `donor_mix_*`).
2. **Proportion warp** (`fit`): a smooth radial-basis warp that carries the donor's joints onto
   our landmarks (SPEC §7.3 head canon from the variant file), with the head, hands and feet
   moved as similarity transforms (their shape kept, placed and scaled to our proportions).
3. **Our body**: torso, arms and legs are projected onto our own anatomy field (bb_anatomy), so
   the body shape is the M1-CHR-01 sculpt on donor quads. Ramps at the neck, wrists and ankles.
4. **Eyes**: each lid margin is re-shaped onto our EyeFrame almond (SPEC §7.3 eyes x1.10, Asha's
   4 degree tilt and canthus), with the lids conformed to our eyeball radius; the socket is tucked
   behind the globe.
5. **Our face sculpt** (`sculpt_face`): the bb_params face sliders (jaw, cheekbones, chin, nose
   bridge and tip, lips, mouth-corner lift, brow ridge) as smooth face-space deformations.

`generate(params)` returns the same keys as bb_cage.generate (V, F, lm, body, reg, freg, seams,
groups) plus the donor's per-corner UVs and weights, so build.py and build_asha.py stay the same
shape. `shape_warp` re-maps any donor-space delta (expression targets) through steps 1-2 and 4.
"""
from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np

import bb_anatomy
import bb_face
import mpfb_data as md
from bb_params import Landmarks, unit, v3

Arr = np.ndarray
ETHNIC = ("african", "asian", "caucasian")
EYE_GAP = 0.0006  # lid margin rest gap over the globe (m, scaled)
LIP_CLOSE = 0.45  # share of the donor's resting lip parting that the face warp closes (param `lip_close`)

# donor weight group -> region (bb_cage names) ------------------------------------------------
FACE_GROUPS = ("brow", "cheek", "chin", "ear", "forehead", "jaw", "lid", "lip", "nose", "teeth", "tongue", "temple",
               "DEF-eye_master", "eye.", "spine.006")
ARM_GROUPS = ("upper_arm", "DEF-upper_arm", "forearm", "DEF-forearm", "DEF-elbow-helper", "DEF-shoulder-helper")
HAND_GROUPS = ("hand", "palm", "f_", "thumb")
LEG_GROUPS = ("thigh", "DEF-thigh", "shin", "DEF-shin", "DEF-knee-helper")
FOOT_GROUPS = ("foot", "toe")
LOWER_FACE = ("jaw", "chin", "lip.B", "teeth.B", "tongue")


def region_of(group: str) -> str | None:
    if group.startswith("mhmask"):
        return None
    side = "L" if group.endswith(".L") or ".L." in group else ("R" if group.endswith(".R") or ".R." in group else "")
    if group.startswith(FACE_GROUPS):
        return "head"
    if group.startswith(HAND_GROUPS):
        return f"hand_{side}"
    if group.startswith(ARM_GROUPS):
        return f"arm_{side}"
    if group.startswith(FOOT_GROUPS):
        return f"foot_{side}"
    if group.startswith(LEG_GROUPS):
        return f"leg_{side}"
    return "torso"  # spine.*, breast, shoulder (clavicle), pelvis and its helpers


def bone_of(group: str) -> list[tuple[str, float]]:
    """Donor weight group -> our game-skeleton DEF bones (bb_rig), with split factors."""
    if group.startswith("mhmask") or group in ("eye.L", "eye.R"):
        return []
    sd = group[-1]
    if group.startswith("DEF-elbow-helper"):
        return [(f"DEF-upper_arm.{sd}.001", 0.5), (f"DEF-forearm.{sd}", 0.5)]
    if group.startswith("DEF-knee-helper"):
        return [(f"DEF-thigh.{sd}.001", 0.5), (f"DEF-shin.{sd}", 0.5)]
    if group.startswith("DEF-shoulder-helper"):
        return [(f"DEF-shoulder.{sd}", 0.5), (f"DEF-upper_arm.{sd}", 0.5)]
    if group.startswith("DEF-pelvis-helper"):
        return [(f"DEF-pelvis.{sd}", 0.5), (f"DEF-thigh.{sd}", 0.5)]
    if group.startswith("toe"):
        return [(f"DEF-toe.{sd}", 1.0)]
    if group.startswith(FACE_GROUPS):
        return [("DEF-spine.006", 1.0)]
    if group.startswith("DEF-"):
        return [(group, 1.0)]
    return [("DEF-" + group, 1.0)]


# ---------------------------------------------------------------------------------------------
# Donor data (cached)
# ---------------------------------------------------------------------------------------------
@dataclass
class Donor:
    mesh: md.DonorMesh
    F: Arr  # (k, 4) skin quads
    T: Arr  # (k, 4) uv ids per corner
    W: dict  # group -> (n_body,) weights
    reg: Arr  # (n_body,) region name per vertex
    lips: Arr  # face ids
    face: Arr
    scalp: Arr
    lower: Arr  # (n_body,) lower-face (jaw) weight for the mouth split
    edges_f: dict = field(default_factory=dict)  # sorted edge -> faces


_CACHE: dict = {}


def donor() -> Donor:
    if "d" in _CACHE:
        return _CACHE["d"]
    m = md.load_obj()
    F, T = m.body()
    W = md.load_weights()
    n = md.N_BODY
    acc: dict[str, Arr] = defaultdict(lambda: np.zeros(n))
    tot = np.zeros(n)
    lower = np.zeros(n)
    for g, w in W.items():
        r = region_of(g)
        if r is None:
            continue
        acc[r] = acc[r] + w
        tot += w
        if g.startswith(LOWER_FACE):
            lower += w
    names = sorted(acc)
    stack = np.stack([acc[k] for k in names])
    reg = np.array(names, dtype=object)[np.argmax(stack, axis=0)]
    lower = lower / np.maximum(acc["head"], 1e-9)
    edges: dict = defaultdict(list)
    for fi, f in enumerate(F):
        for i in range(4):
            a, b = int(f[i]), int(f[(i + 1) % 4])
            edges[(min(a, b), max(a, b))].append(fi)
    d = Donor(m, F, T, W, reg, md.load_face_set("lips_solid"), md.load_face_set("face_solid"),
              md.load_face_set("scalp_solid"), np.clip(lower, 0.0, 1.0), dict(edges))
    _CACHE["d"] = d
    return d


def loops_of(edge_list) -> list[list[int]]:
    """Ordered vertex loops from an unordered set of edges forming closed loops."""
    adj: dict = defaultdict(list)
    for a, b in edge_list:
        adj[a].append(b)
        adj[b].append(a)
    seen: set = set()
    out = []
    for s in sorted(adj):
        if s in seen:
            continue
        loop = [s]
        seen.add(s)
        cur = s
        while True:
            nx = [k for k in adj[cur] if k not in seen]
            if not nx:
                break
            cur = nx[0]
            seen.add(cur)
            loop.append(cur)
        out.append(loop)
    return out


def vermilion(dn: Donor) -> Arr:
    """The red of the lips: MakeHuman's lip face set also holds a ring or two of skin around the
    lips and the inner lip rolling into the mouth. Count face rings outward from the inner lip
    loop; the outer two rings are skin (the white roll and beyond) and are left out."""
    if "verm" in _CACHE:
        return _CACHE["verm"]
    V = dn.mesh.V[:md.N_BODY]
    inl = np.zeros(len(dn.F), bool)
    inl[dn.lips] = True
    bnd = [e for e, fs in dn.edges_f.items() if len(fs) == 2 and inl[fs[0]] != inl[fs[1]]]
    inner = set(min(loops_of(bnd), key=lambda lp: float(np.ptp(V[lp, 0]))))
    adj: dict = defaultdict(list)
    for fs in dn.edges_f.values():
        if len(fs) == 2:
            adj[fs[0]].append(fs[1])
            adj[fs[1]].append(fs[0])
    ring = -np.ones(len(dn.F), int)
    cur = [int(f) for f in dn.lips if any(int(v) in inner for v in dn.F[f])]
    ring[cur] = 0
    r = 0
    while cur:
        nxt = []
        for f in cur:
            for g in adj[f]:
                if inl[g] and ring[g] < 0:
                    ring[g] = r + 1
                    nxt.append(g)
        cur = nxt
        r += 1
    out = np.nonzero(inl & (ring >= 0) & (ring <= ring.max() - 2))[0]
    _CACHE["verm"] = out
    return out


def flood(dn: Donor, seed_faces: list[int], blocked: Arr) -> Arr:
    """Faces reachable from the seeds across edges, never entering `blocked` faces."""
    adj: dict = defaultdict(list)
    for fs in dn.edges_f.values():
        if len(fs) == 2:
            adj[fs[0]].append(fs[1])
            adj[fs[1]].append(fs[0])
    out = np.zeros(len(dn.F), bool)
    stack = [f for f in seed_faces if not blocked[f]]
    while stack:
        f = stack.pop()
        if out[f]:
            continue
        out[f] = True
        stack.extend(g for g in adj[f] if not out[g] and not blocked[g])
    return out


# ---------------------------------------------------------------------------------------------
# 1. Macro mix
# ---------------------------------------------------------------------------------------------
def _three(x: float) -> dict[str, float]:
    """MakeHuman-style min / average / max factors for a 0..1 slider (average at 0.5)."""
    x = min(max(x, 0.0), 1.0)
    if x < 0.5:
        return {"min": 1.0 - 2.0 * x, "average": 2.0 * x, "max": 0.0}
    return {"min": 0.0, "average": 2.0 - 2.0 * x, "max": 2.0 * x - 1.0}


def macro_terms(params: dict) -> list[tuple[str, float]]:
    fem = float(params["femininity"])
    mix = np.array([float(params[f"donor_mix_{e}"]) for e in ETHNIC])
    mix = mix / max(mix.sum(), 1e-9)
    terms = []
    for e, me in zip(ETHNIC, mix):
        for g, gw in (("female", fem), ("male", 1.0 - fem)):
            if me * gw > 1e-6:
                terms.append((f"macrodetails/{e}-{g}-young.target.gz", float(me * gw)))
    mf = _three(float(params["muscle"]))
    wf = _three(0.5 + (float(params["mass"]) - 0.3))
    for g, gw in (("female", fem), ("male", 1.0 - fem)):
        for mk, mv in mf.items():
            for wk, wv in wf.items():
                w = gw * mv * wv
                if w > 1e-6 and not (mk == "average" and wk == "average"):
                    terms.append((f"macrodetails/universal-{g}-young-{mk}muscle-{wk}weight.target.gz", float(w)))
    return terms


def macro(params: dict) -> Arr:
    dn = donor()
    X = dn.mesh.V.copy()
    for rel, w in macro_terms(params):
        X += w * md.load_target(rel, len(X))
    return X


# ---------------------------------------------------------------------------------------------
# 2. Warps
# ---------------------------------------------------------------------------------------------
class RBF:
    """Polyharmonic (phi(r) = r) warp with an affine part: x -> x + f(x), f(c_i) = d_i exactly."""

    def __init__(self, C: Arr, D: Arr, reg: float = 1e-9) -> None:
        n = len(C)
        K = np.linalg.norm(C[:, None, :] - C[None, :, :], axis=2)
        P = np.hstack([np.ones((n, 1)), C])
        A = np.zeros((n + 4, n + 4))
        A[:n, :n] = K + reg * np.eye(n)
        A[:n, n:] = P
        A[n:, :n] = P.T
        b = np.zeros((n + 4, 3))
        b[:n] = D
        sol = np.linalg.lstsq(A, b, rcond=None)[0]
        self.C, self.w, self.a = C, sol[:n], sol[n:]

    def __call__(self, X: Arr) -> Arr:
        out = np.empty_like(X)
        for s in range(0, len(X), 8192):
            x = X[s:s + 8192]
            K = np.linalg.norm(x[:, None, :] - self.C[None, :, :], axis=2)
            out[s:s + 8192] = x + K @ self.w + np.hstack([np.ones((len(x), 1)), x]) @ self.a
        return out


@dataclass
class Sim:
    """p -> o + s R (p - c)."""
    c: Arr
    o: Arr
    s: float
    R: Arr

    def __call__(self, P: Arr) -> Arr:
        return self.o + self.s * (np.asarray(P) - self.c) @ self.R.T


def frame_rot(a_src: Arr, b_src: Arr, a_dst: Arr, b_dst: Arr) -> Arr:
    """Rotation taking the orthonormal frame (a, b⊥a) of src onto that of dst."""
    def fr(a, b):
        a = unit(a)
        b = unit(b - a * np.dot(a, b))
        return np.stack([a, b, np.cross(a, b)], axis=1)
    return fr(a_dst, b_dst) @ fr(a_src, b_src).T


@dataclass
class Fit:
    lm: Landmarks
    X0: Arr  # donor after the macro mix, all vertices (skin + helpers + joint cubes)
    body_warp: RBF
    head: Sim
    hands: dict
    feet: dict
    eye_warp: RBF | None = None
    margins: dict = field(default_factory=dict)  # side -> ordered margin vertex ids
    sockets: dict = field(default_factory=dict)  # side -> socket face mask
    mouth_faces: Arr | None = None
    commissure: float = 0.0
    lip_line_y: float = 0.0

    part_w: dict = field(default_factory=dict)  # part -> (n_body,) blend weight of its similarity

    def place(self, X: Arr) -> Arr:
        """Body warp for donor skin vertices (index = donor vertex): the smooth warp, with the head,
        hands and feet carried exactly by their similarity transforms."""
        Y = self.body_warp(X)
        n = min(len(X), md.N_BODY)
        sims = {"head": self.head, "hand_L": self.hands["L"], "hand_R": self.hands["R"], "foot_L": self.feet["L"],
                "foot_R": self.feet["R"]}
        for name, w in self.part_w.items():
            Z = sims[name](X[:n])
            Y[:n] = Y[:n] * (1.0 - w[:n, None]) + Z * w[:n, None]
        return Y

    def warp(self, X: Arr) -> Arr:
        Y = self.place(X)
        if self.eye_warp is not None:
            Y = self.eye_warp(Y)
        return Y


def _head_extent(dn: Donor, X: Arr) -> tuple[float, float, Arr]:
    V = X[:md.N_BODY]
    head = dn.reg == "head"
    crown = float(V[head, 2].max())
    El = joint(X, "l-eye")
    front = head & (np.abs(V[:, 0]) < 0.006) & (V[:, 1] < El[1] - 0.02)
    chin_i = np.nonzero(front)[0][np.argmin(V[front, 2])]
    return crown, float(V[chin_i, 2]), V[chin_i]


def joint(X: Arr, name: str) -> Arr:
    dn = donor()
    return X[dn.mesh.group_vertices(f"joint-{name}")].mean(axis=0)


def _sample(ids: Arr, k: int) -> Arr:
    ids = np.asarray(ids)
    if len(ids) <= k:
        return ids
    return ids[np.linspace(0, len(ids) - 1, k).astype(int)]


def fit(params: dict) -> Fit:
    """Donor joints -> our landmarks. Returns the warp and the landmarks with the face, hand and
    foot points taken from the placed donor (so rig, eyes and mouth parts agree with the mesh)."""
    dn = donor()
    lm = Landmarks(params)
    X = macro(params)
    V = X[:md.N_BODY]
    S = lm.S
    # ---- head: similarity (scale to our head height, eyes to our eye depth, chin to our chin) ----
    crown_z, chin_z, chin_p = _head_extent(dn, X)
    s_h = lm.h / (crown_z - chin_z)
    Ed = 0.5 * (joint(X, "l-eye") + joint(X, "r-eye"))
    eye_y = float(lm.P("eye")[1])
    o = np.array([0.0, eye_y, float(lm.P("chin")[2]) + s_h * (Ed[2] - chin_z)])
    head = Sim(Ed * np.array([0.0, 1.0, 1.0]), o, s_h, np.eye(3))
    # ---- hands: wrist -> middle knuckle axis, index-minus-pinky side ----------------------------
    hands = {}
    for sd, mh in (("L", "l"), ("R", "r")):
        hand = lm.hands[sd]
        w_d = joint(X, f"{mh}-hand")
        k_d = joint(X, f"{mh}-finger-3-1")
        side_d = joint(X, f"{mh}-finger-2-1") - joint(X, f"{mh}-finger-5-1")
        R = frame_rot(k_d - w_d, side_d, hand.axis, hand.side)
        s = float(np.linalg.norm(hand.knuckle - hand.wrist) / np.linalg.norm(k_d - w_d))
        hands[sd] = Sim(w_d, hand.wrist, s, R)
    # ---- feet: heel -> toe horizontal axis, scaled to our foot length, ankle onto our ankle --------
    feet = {}
    for sd, mh in (("L", "l"), ("R", "r")):
        fid = np.nonzero(dn.reg == f"foot_{sd}")[0]
        P = V[fid]
        a_d = joint(X, f"{mh}-ankle")
        toe_d = P[np.argmin(P[:, 1])]
        heel_d = P[np.argmax(P[:, 1])]
        ax_d = (toe_d - heel_d) * np.array([1.0, 1.0, 0.0])
        ax = (lm.side_pt("toe_tip", sd) - lm.side_pt("heel_back", sd)) * np.array([1.0, 1.0, 0.0])
        R = frame_rot(ax_d, np.array([0.0, 0.0, 1.0]), ax, np.array([0.0, 0.0, 1.0]))
        s = float(np.linalg.norm(ax) / np.linalg.norm(ax_d))
        feet[sd] = Sim(a_d, lm.side_pt("ankle", sd), s, R)
    # ---- correspondences for the body warp --------------------------------------------------
    C, T = [], []

    def add(src, dst):
        C.append(np.asarray(src, dtype=float))
        T.append(np.asarray(dst, dtype=float))

    for sd, mh in (("L", "l"), ("R", "r")):
        add(joint(X, f"{mh}-shoulder"), lm.side_pt("shoulder", sd))
        add(joint(X, f"{mh}-elbow"), lm.side_pt("elbow", sd))
        add(joint(X, f"{mh}-upper-leg"), lm.side_pt("hip", sd))
        add(joint(X, f"{mh}-knee"), lm.side_pt("knee", sd))
        add(joint(X, f"{mh}-clavicle"), lm.side_pt("clavicle_in", sd))
    z_hp = float(lm.P("hip")[2])
    nb, sb = lm.P("neck_base"), lm.P("skull_base")
    add(joint(X, "pelvis"), v3(0, 0.02 * S, z_hp + 0.01 * S))
    spine_dst = [v3(0, 0.02 * S, z_hp + 0.14 * S), v3(0, 0.012 * S, float(lm.P("waist")[2]) + 0.06 * S),
                 v3(0, 0.01 * S, float(lm.P("nipple")[2]) + 0.01 * S), v3(0, 0.012 * S, float(lm.P("notch")[2]) - 0.03 * S)]
    for k, dst in zip((4, 3, 2, 1), spine_dst):
        add(joint(X, f"spine-{k}"), dst)
    add(joint(X, "neck"), nb + (sb - nb) * 0.4 + v3(0, 0.01 * S, 0))
    head_ids = _sample(np.nonzero(dn.reg == "head")[0], 48)
    for i in head_ids:
        add(V[i], head(V[i]))
    for sd in ("L", "R"):
        for i in _sample(np.nonzero(dn.reg == f"hand_{sd}")[0], 24):
            add(V[i], hands[sd](V[i]))
        for i in _sample(np.nonzero(dn.reg == f"foot_{sd}")[0], 24):
            add(V[i], feet[sd](V[i]))
    C, T = np.array(C), np.array(T)
    body_warp = RBF(C, T - C)
    ft = Fit(lm, X, body_warp, head, hands, feet)
    rows, cols = vertex_adjacency(dn.F, md.N_BODY)
    for name in ("head", "hand_L", "hand_R", "foot_L", "foot_R"):
        m = smooth_scalar((dn.reg == name).astype(float), rows, cols, 4)
        ft.part_w[name] = bb_face.smoothstep(0.15, 0.85, m)
    _override_landmarks(ft, dn)
    _find_eyes_and_mouth(ft, dn)
    _eye_warp(ft, dn)
    return ft


def _override_landmarks(ft: Fit, dn: Donor) -> None:
    """Face, hand and foot points from the placed donor (behind the Landmarks interface)."""
    lm, X = ft.lm, ft.X0
    V = X[:md.N_BODY]
    H = ft.head
    p = lm.pts
    E = H(joint(X, "l-eye"))
    p["eye"] = v3(float(lm.p["ipd_m"]) / 2, E[1], E[2])
    mid = np.abs(V[:, 0]) < 0.003
    head = dn.reg == "head"
    Ed = joint(X, "l-eye")
    # nose tip: the most forward midline point between the mouth and the eyes
    band = head & mid & (V[:, 2] < Ed[2] - 0.01) & (V[:, 2] > Ed[2] - 0.08)
    tip = V[np.nonzero(band)[0][np.argmin(V[band, 1])]]
    p["nose_tip"] = H(tip)
    # brow (glabella): the most forward midline point a little above the eyes
    band = head & mid & (V[:, 2] > Ed[2] + 0.005) & (V[:, 2] < Ed[2] + 0.04)
    p["brow"] = H(V[np.nonzero(band)[0][np.argmin(V[band, 1])]])
    # chin: the front of the chin at the chin height
    _c, _z, chin_p = _head_extent(dn, X)
    p["chin"] = H(chin_p)
    p["ear"] = H(V[_ear_mask(dn)].mean(axis=0))
    for sd in ("L", "R"):
        hand = lm.hands[sd]
        Sm = ft.hands[sd]
        mh = sd.lower()
        names = {"thumb": 1, "f_index": 2, "f_middle": 3, "f_ring": 4, "f_pinky": 5}
        for fg in hand.fingers:
            k = names[fg.name]
            fg.joints = [Sm(joint(X, f"{mh}-finger-{k}-{j}")) for j in (1, 2, 3, 4)]
        hand.knuckle = Sm(joint(X, f"{mh}-finger-3-1"))
    for sd in ("L",):
        Fm = ft.feet[sd]
        fid = np.nonzero(dn.reg == "foot_L")[0]
        P = V[fid]
        toes = np.array([joint(X, f"l-toe-{k}-1") for k in range(1, 6)])
        p["ball"] = Fm(toes.mean(axis=0)) * np.array([1.0, 1.0, 0.0]) + v3(0, 0, 0.012 * lm.S)
        p["toe_tip"] = Fm(P[np.argmin(P[:, 1])]) * np.array([1.0, 1.0, 0.0])
        hb = Fm(P[np.argmax(P[:, 1])])
        p["heel_back"] = v3(hb[0], hb[1], 0.035 * lm.S)
        p["heel"] = v3(hb[0], hb[1] - 0.016 * lm.S, 0.03 * lm.S)


def _ear_mask(dn: Donor, side: str = "L") -> Arr:
    w = np.zeros(md.N_BODY)
    for g, v in dn.W.items():
        if g.startswith(f"ear.{side}"):
            w += v
    return w > 0.5


def _ear_mask_r(dn: Donor) -> Arr:
    return _ear_mask(dn, "R")


def _margin_loop(dn: Donor, V: Arr, E: Arr) -> tuple[list[int], Arr]:
    """The lid margin: the edge loop where the outward-facing lid skin turns into the socket."""
    F = dn.F
    C = V[F].mean(axis=1)
    N = np.cross(V[F[:, 2]] - V[F[:, 0]], V[F[:, 3]] - V[F[:, 1]])
    N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
    d = C - E
    dist = np.linalg.norm(d, axis=1)
    near = dist < 0.024
    inward = near & (np.sum(N * d, axis=1) / np.maximum(dist, 1e-9) < -0.2)
    bnd = [e for e, fs in dn.edges_f.items() if len(fs) == 2 and near[fs[0]] and near[fs[1]]
           and inward[fs[0]] != inward[fs[1]]]
    loops = sorted(loops_of(bnd), key=len, reverse=True)
    loop = loops[0]
    # socket = inward faces enclosed by the loop (flood from an inward face on the loop)
    lv = set(loop)
    seeds = [fi for fi in np.nonzero(inward)[0] if any(int(v) in lv for v in F[fi])]
    socket = flood(dn, seeds, ~inward)
    return loop, socket


def _find_eyes_and_mouth(ft: Fit, dn: Donor) -> None:
    X = ft.X0
    V = X[:md.N_BODY]
    for sd, mh in (("L", "l"), ("R", "r")):
        loop, socket = _margin_loop(dn, V, joint(X, f"{mh}-eye"))
        ft.margins[sd] = loop
        ft.sockets[sd] = socket
    # mouth cavity: everything reachable from the inner lip loop without crossing the lips
    inl = np.zeros(len(dn.F), bool)
    inl[dn.lips] = True
    bnd = [e for e, fs in dn.edges_f.items() if len(fs) == 2 and inl[fs[0]] != inl[fs[1]]]
    loops = loops_of(bnd)
    inner = min(loops, key=lambda lp: float(np.ptp(V[lp, 0])))
    iv = set(inner)
    seeds = [fi for fi in range(len(dn.F)) if not inl[fi] and sum(int(v) in iv for v in dn.F[fi]) >= 2]
    ft.mouth_faces = flood(dn, seeds, inl)
    Y = ft.head(V[inner])
    ft.commissure = float(np.abs(Y[:, 0]).max())
    lm = ft.lm
    front = Y[np.abs(Y[:, 0]) < 0.004]
    ft.lip_line_y = float(front[:, 1].min())
    m = front[np.argsort(front[:, 1])[:2]].mean(axis=0) if len(front) >= 2 else Y.mean(axis=0)
    lm.pts["mouth"] = v3(0.0, m[1], m[2])
    lm.mouth_w = 2.0 * ft.commissure
    # subnasale: the deepest midline point between the mouth and the nose tip
    mid = (np.abs(V[:, 0]) < 0.003) & (dn.reg == "head")
    W = ft.head(V)
    band = mid & (W[:, 2] > m[2] + 0.004 * lm.S) & (W[:, 2] < lm.P("nose_tip")[2]) & (W[:, 1] < lm.P("nose_tip")[1] + 0.03)
    if band.any():
        lm.pts["subnasale"] = W[np.nonzero(band)[0][np.argmax(W[band, 1])]]


def _loop_angles(P: Arr, E: Arr, sgn: float) -> Arr:
    a = (P[:, 0] - E[0]) * sgn
    b = P[:, 2] - E[2]
    hw = 0.5 * (a.max() - a.min())
    ac = 0.5 * (a.max() + a.min())
    hh = 0.5 * (b.max() - b.min())
    bc = 0.5 * (b.max() + b.min())
    return np.arctan2((b - bc) / hh, (a - ac) / hw)


def _eye_warp(ft: Fit, dn: Donor, Y: Arr | None = None) -> None:
    """Margins onto our EyeFrame almond; the lid region scaled to our globe; identity farther out."""
    lm = ft.lm
    X = ft.X0
    if Y is None:  # the placed donor skin (or, after the face subdivision, its subdivided positions)
        Y = ft.place(X[:md.N_BODY])
    C, D = [], []
    for sd in ("L", "R"):
        fr = bb_face.EyeFrame(lm, sd)
        loop = ft.margins[sd]
        P = Y[loop]
        Ed = ft.head(joint(X, f"{sd.lower()}-eye"))
        t = _loop_angles(P, Ed, fr.sgn)
        tgt = fr.margin_point(t, lift=EYE_GAP * lm.S)
        C.extend(P)
        D.extend(tgt - P)
        # the globe centre moves to ours; a ring around the eye moves with it, scaled to our fissure
        dw = (np.ptp((P[:, 0] - Ed[0])) + 1e-9)
        k = (2.0 * fr.half_w + fr.inner_extra) / dw
        k = 0.5 * (1.0 + k)  # the surround follows half way: brow and cheek keep the donor's forms
        ang = np.linspace(0, 2 * math.pi, 16, endpoint=False)
        for rr in (0.020, 0.026):
            ring = Ed + np.stack([np.cos(ang) * rr * 1.15, -0.004 * np.ones(16), np.sin(ang) * rr], axis=1) * lm.S
            tgt_r = fr.E + (ring - Ed) * (k if rr < 0.025 else 1.0)
            C.extend(ring)
            D.extend(tgt_r - ring)
        # globe: points on the donor ball move onto ours (radius ratio), behind the margin
        r_d = 0.015 * ft.head.s
        dirs = np.array([[0, -1, 0], [0.5, -0.8, 0.3], [-0.5, -0.8, 0.3], [0.5, -0.8, -0.3], [-0.5, -0.8, -0.3]],
                        dtype=float)
        dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
        gp = Ed + dirs * r_d * 0.8
        C.extend(gp)
        D.extend(fr.E + dirs * fr.R * 0.8 - gp)
    # far field: identity
    hc = lm.P("head_c")
    ang = np.linspace(0, 2 * math.pi, 24, endpoint=False)
    for zz in (-0.06, 0.0, 0.07):
        ring = hc + np.stack([np.cos(ang) * 0.11, np.sin(ang) * 0.13, np.full(24, zz)], axis=1) * lm.S
        C.extend(ring)
        D.extend(np.zeros_like(ring))
    # mouth: the donor rests with the lips a little parted; bring the inner lip edges together
    # (`lip_close` of the gap, LIP_CLOSE by default), the lips' outer border stays where it is
    close = float(lm.p.get("lip_close", LIP_CLOSE))
    inl = np.zeros(len(dn.F), bool)
    inl[dn.lips] = True
    bnd = [e for e, fs in dn.edges_f.items() if len(fs) == 2 and inl[fs[0]] != inl[fs[1]]]
    lps = loops_of(bnd)
    inner = min(lps, key=lambda lp: float(np.ptp(Y[lp, 0])))
    outer = max(lps, key=lambda lp: float(np.ptp(Y[lp, 0])))
    P = Y[inner]
    tgt = P.copy()
    for i, q in enumerate(P):
        near = np.abs(P[:, 0] - q[0]) < 0.003 * lm.S
        zc = 0.5 * (P[near, 2].max() + P[near, 2].min())
        tgt[i, 2] = zc + (q[2] - zc) * (1.0 - close)
    C.extend(P)
    D.extend(tgt - P)
    C.extend(Y[outer])
    D.extend(np.zeros((len(outer), 3)))
    ft.eye_warp = RBF(np.array(C), np.array(D))


# ---------------------------------------------------------------------------------------------
# 3. Our body field; 5. our face sculpt
# ---------------------------------------------------------------------------------------------
def vertex_adjacency(F: Arr, n: int) -> tuple[Arr, Arr]:
    """(rows, cols) of the undirected vertex graph of quad faces."""
    a = np.concatenate([F[:, 0], F[:, 1], F[:, 2], F[:, 3]])
    b = np.concatenate([F[:, 1], F[:, 2], F[:, 3], F[:, 0]])
    e = np.unique(np.sort(np.stack([a, b], axis=1), axis=1), axis=0)
    rows = np.concatenate([e[:, 0], e[:, 1]])
    cols = np.concatenate([e[:, 1], e[:, 0]])
    return rows, cols


def smooth_scalar(x: Arr, rows: Arr, cols: Arr, iters: int) -> Arr:
    n = len(x)
    deg = np.bincount(rows, minlength=n).astype(float)
    for _ in range(iters):
        acc = np.bincount(rows, weights=x[cols], minlength=n)
        x = 0.5 * x + 0.5 * acc / np.maximum(deg, 1)
    return x


def _blur_axis(A: Arr, sigma: float, axis: int) -> Arr:
    r = max(int(math.ceil(2.5 * sigma)), 1)
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    pad = [(0, 0)] * A.ndim
    pad[axis] = (r, r)
    Ap = np.pad(A, pad, mode="edge")
    out = np.zeros_like(A)
    n = A.shape[axis]
    for j, kv in enumerate(k):
        sl = [slice(None)] * A.ndim
        sl[axis] = slice(j, j + n)
        out += kv * Ap[tuple(sl)]
    return out


def _blur(A: Arr, sigma: float) -> Arr:
    for ax in range(3):
        A = _blur_axis(A, sigma, ax)
    return A


class CorrectedRegion:
    """One region of our anatomy field, offset so its zero set follows the donor surface:
    sdf'(P) = sdf(P) - delta(P), where delta is the field's own distance at the donor's
    vertices, spread over a grid by normalised convolution (fine near the skin, coarse far away)."""

    def __init__(self, base, P: Arr, spacing: float, margin: float = 0.05) -> None:
        self.base = base
        d = base.sdf(P)
        lo = P.min(axis=0) - margin
        hi = P.max(axis=0) + margin
        shape = np.ceil((hi - lo) / spacing).astype(int) + 1
        self.lo, self.h, self.shape = lo, spacing, shape
        g = (P - lo) / spacing
        i0 = np.floor(g).astype(int)
        f = g - i0
        num = np.zeros(shape)
        den = np.zeros(shape)
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * \
                        (f[:, 2] if dz else 1 - f[:, 2])
                    idx = (np.clip(i0[:, 0] + dx, 0, shape[0] - 1), np.clip(i0[:, 1] + dy, 0, shape[1] - 1),
                           np.clip(i0[:, 2] + dz, 0, shape[2] - 1))
                    np.add.at(num, idx, w * d)
                    np.add.at(den, idx, w)
        fine_n, fine_d = _blur(num, 1.0), _blur(den, 1.0)
        coarse_n, coarse_d = _blur(fine_n, 6.0), _blur(fine_d, 6.0)
        fine = fine_n / np.maximum(fine_d, 1e-12)
        coarse = coarse_n / np.maximum(coarse_d, 1e-12)
        t = np.clip(fine_d / 0.05, 0.0, 1.0)
        self.delta = t * fine + (1 - t) * np.where(coarse_d > 1e-9, coarse, 0.0)

    def offset(self, P: Arr) -> Arr:
        g = np.clip((P - self.lo) / self.h, 0, self.shape - 1.0001)
        i0 = np.floor(g).astype(int)
        f = g - i0
        out = np.zeros(len(P))
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * \
                        (f[:, 2] if dz else 1 - f[:, 2])
                    out += w * self.delta[i0[:, 0] + dx, i0[:, 1] + dy, i0[:, 2] + dz]
        return out

    def sdf(self, P: Arr) -> Arr:
        return self.base.sdf(P) - self.offset(P)

    def sdf_no_post(self, P: Arr) -> Arr:
        return self.sdf(P)


def _chain_param(P: Arr, A: Arr) -> tuple[Arr, Arr, Arr]:
    """Nearest point on the polyline A for each P: (t in 0..1 by arc length, axis point, segment dir)."""
    seg = A[1:] - A[:-1]
    L = np.linalg.norm(seg, axis=1)
    cum = np.concatenate([[0.0], np.cumsum(L)])
    best_d = np.full(len(P), np.inf)
    t = np.zeros(len(P))
    C = np.zeros_like(P)
    Dd = np.zeros_like(P)
    for i in range(len(seg)):
        u = np.clip(((P - A[i]) @ seg[i]) / (L[i] ** 2), 0.0, 1.0)
        c = A[i] + u[:, None] * seg[i]
        d = np.linalg.norm(P - c, axis=1)
        m = d < best_d
        best_d[m] = d[m]
        t[m] = (cum[i] + u[m] * L[i]) / cum[-1]
        C[m] = c[m]
        Dd[m] = seg[i] / L[i]
    return t, C, Dd


def girth_fit(body: bb_anatomy.Body, V: Arr, reg: Arr, rows: Arr, cols: Arr, nt: int = 22, nth: int = 16) -> Arr:
    """Our body volumes on the donor's surface: torso, arm and leg cross-sections are scaled,
    at low frequency (nt sections x nth angles, smoothed), so their radius matches our anatomy
    field's (widths, depth, muscle and mass sliders); the donor's surface detail rides on top."""
    lm = body.lm
    S = lm.S
    out = V.copy()
    chains = {}
    zt0, zt1 = float(lm.P("crotch")[2]) + 0.03 * S, float(lm.P("notch")[2]) - 0.01 * S
    zs = np.linspace(zt0, zt1, 12)
    tor = reg == "torso"
    yc = []
    for z in zs:
        band = tor & (np.abs(V[:, 2] - z) < 0.03 * S) & (np.abs(V[:, 0]) < 0.06 * S)
        yc.append(0.5 * (V[band, 1].min() + V[band, 1].max()) if band.sum() > 4 else 0.0)
    chains["torso"] = (np.stack([np.zeros(12), np.array(yc), zs], axis=1), np.array([0.0, -1.0, 0.0]))
    for sd in ("L", "R"):
        sp = lm.side_pt
        chains[f"arm_{sd}"] = (np.stack([sp("shoulder", sd), sp("elbow", sd), sp("wrist", sd)]), np.array([0.0, -1.0, 0.0]))
        chains[f"leg_{sd}"] = (np.stack([sp("hip", sd), sp("knee", sd), sp("ankle", sd)]), np.array([0.0, -1.0, 0.0]))
    for name, (A, ref) in chains.items():
        idx = np.nonzero(reg == name)[0]
        if len(idx) < 50:
            continue
        P = V[idx]
        t, C, Dd = _chain_param(P, A)
        R = P - C
        R -= np.sum(R * Dd, axis=1, keepdims=True) * Dd
        r = np.linalg.norm(R, axis=1)
        e1 = ref - np.sum(ref * Dd, axis=1, keepdims=True) * Dd
        e1 /= np.maximum(np.linalg.norm(e1, axis=1, keepdims=True), 1e-9)
        e2 = np.cross(Dd, e1)
        th = np.arctan2(np.sum(R * e2, axis=1), np.sum(R * e1, axis=1))
        ti = np.clip((t * nt).astype(int), 0, nt - 1)
        hi = ((th + math.pi) / (2 * math.pi) * nth).astype(int) % nth
        ratio = np.ones((nt, nth))
        rd = np.zeros((nt, nth))
        for a in range(nt):
            for b in range(nth):
                m = (ti == a) & (hi == b)
                if m.sum() >= 2:
                    rd[a, b] = np.median(r[m])
        # field radius at each bin centre, along the bin's mean radial direction
        tc = (np.arange(nt) + 0.5) / nt
        thc = (np.arange(nth) + 0.5) / nth * 2 * math.pi - math.pi
        seg = A[1:] - A[:-1]
        L = np.linalg.norm(seg, axis=1)
        cum = np.concatenate([[0.0], np.cumsum(L)]) / L.sum()
        O, Dr, keys = [], [], []
        for a in range(nt):
            i = min(int(np.searchsorted(cum, tc[a]) - 1), len(seg) - 1)
            i = max(i, 0)
            u = (tc[a] - cum[i]) / (cum[i + 1] - cum[i])
            c = A[i] + u * seg[i]
            dd = seg[i] / L[i]
            f1 = ref - np.dot(ref, dd) * dd
            f1 /= np.linalg.norm(f1)
            f2 = np.cross(dd, f1)
            for b in range(nth):
                if rd[a, b] <= 0:
                    continue
                O.append(c)
                Dr.append(np.cos(thc[b]) * f1 + np.sin(thc[b]) * f2)
                keys.append((a, b))
        if keys:
            hit = bb_cage_cast(body, name, np.array(O), np.array(Dr), 0.4 * S)
            rf = np.linalg.norm(hit - np.array(O), axis=1)
            for (a, b), v in zip(keys, rf):
                if v > 0.004 * S:
                    ratio[a, b] = np.clip(v / rd[a, b], 0.7, 2.0)
        # smooth (circular in angle), and fade to 1 at the chain ends (joints with other regions)
        for _ in range(2):
            ratio = (np.roll(ratio, 1, axis=1) + 2 * ratio + np.roll(ratio, -1, axis=1)) / 4
            ratio[1:-1] = (ratio[:-2] + 2 * ratio[1:-1] + ratio[2:]) / 4
        fade = bb_face.smoothstep(0.0, 0.12, tc) * bb_face.smoothstep(1.0, 0.88, tc)
        if name == "torso":
            fade = bb_face.smoothstep(0.0, 0.08, tc) * bb_face.smoothstep(1.0, 0.9, tc)
        ratio = 1.0 + (ratio - 1.0) * fade[:, None]
        # bilinear lookup
        ft_ = np.clip(t * nt - 0.5, 0, nt - 1.0001)
        a0 = np.floor(ft_).astype(int)
        fa = ft_ - a0
        fb_ = (th + math.pi) / (2 * math.pi) * nth - 0.5
        b0 = np.floor(fb_).astype(int)
        fb = fb_ - b0
        k = ((1 - fa) * (1 - fb) * ratio[a0, b0 % nth] + fa * (1 - fb) * ratio[np.minimum(a0 + 1, nt - 1), b0 % nth]
             + (1 - fa) * fb * ratio[a0, (b0 + 1) % nth] + fa * fb * ratio[np.minimum(a0 + 1, nt - 1), (b0 + 1) % nth])
        out[idx] = C + R * k[:, None] + (P - C - R)
    D = out - V
    n = len(V)
    deg = np.bincount(rows, minlength=n).astype(float)
    for _ in range(4):
        D = 0.5 * D + 0.5 * np.stack([np.bincount(rows, weights=D[cols, j], minlength=n) for j in range(3)], axis=1) \
            / np.maximum(deg, 1)[:, None]
    return V + D


@dataclass
class Subdiv:
    """One Catmull-Clark level on a subset of the faces of a closed quad mesh, as a linear stencil.

    New vertices are [the old vertices (those on selected faces moved by the vertex rule)] +
    [edge points of the selected faces' edges] + [face points of the selected faces]. Selected
    faces become 4 quads; an unselected face that shares a split edge is fan-triangulated through
    the edge point(s), so the mesh stays watertight. `apply(A)` maps any per-vertex attribute
    (positions, deltas, weights) through the same stencil."""
    rows: Arr
    cols: Arr
    vals: Arr
    n_new: int
    faces: list  # new polygons (tuples of 3 or 4 vertex ids)
    parent: Arr  # parent face of each new polygon
    corner_uv: list  # per new polygon: list of (u, v)
    edge_point: dict  # sorted old edge -> new vertex id

    def apply(self, A: Arr) -> Arr:
        A = np.asarray(A, dtype=np.float64)
        flat = A.reshape(len(A), -1)
        out = np.zeros((self.n_new, flat.shape[1]))
        for j in range(flat.shape[1]):
            out[:, j] = np.bincount(self.rows, weights=self.vals * flat[self.cols, j], minlength=self.n_new)
        return out.reshape((self.n_new,) + A.shape[1:])


def subdivide(F: Arr, sel: Arr, uv: Arr, n: int) -> Subdiv:
    F = np.asarray(F)
    nf = len(F)
    e2f: dict = defaultdict(list)
    for fi, f in enumerate(F):
        for i in range(4):
            a, b = int(f[i]), int(f[(i + 1) % 4])
            e2f[(min(a, b), max(a, b))].append(fi)
    sel_edges = sorted({(min(int(f[i]), int(f[(i + 1) % 4])), max(int(f[i]), int(f[(i + 1) % 4])))
                        for f in F[sel] for i in range(4)})
    sel_verts = np.unique(F[sel])
    edge_point = {e: n + k for k, e in enumerate(sel_edges)}
    sel_idx = np.nonzero(sel)[0]
    face_point = {int(fi): n + len(sel_edges) + k for k, fi in enumerate(sel_idx)}
    n_new = n + len(sel_edges) + len(sel_idx)
    R, C, W = [], [], []

    def emit(r, pairs):
        for c, w in pairs:
            R.append(r)
            C.append(c)
            W.append(w)

    def fp_pairs(fi, k=1.0):
        return [(int(v), 0.25 * k) for v in F[fi]]

    # unmoved old vertices
    moved = np.zeros(n, bool)
    moved[sel_verts] = True
    for v in np.nonzero(~moved)[0]:
        emit(int(v), [(int(v), 1.0)])
    # vertex rule (closed manifold: every edge has two faces)
    v2f: dict = defaultdict(list)
    v2e: dict = defaultdict(list)
    for fi, f in enumerate(F):
        for v in f:
            v2f[int(v)].append(fi)
    for e in e2f:
        v2e[e[0]].append(e)
        v2e[e[1]].append(e)
    for v in sel_verts:
        v = int(v)
        fs, es = v2f[v], v2e[v]
        k = len(es)
        pairs = []
        for fi in fs:  # Q / k
            pairs += fp_pairs(fi, 1.0 / (len(fs) * k))
        for a, b in es:  # 2R / k, R = mean of edge midpoints
            pairs += [(a, 1.0 / (len(es) * k)), (b, 1.0 / (len(es) * k))]
        pairs.append((v, (k - 3.0) / k))
        emit(v, pairs)
    for e, r in edge_point.items():
        fa, fb = e2f[e][0], e2f[e][1]
        emit(r, [(e[0], 0.25), (e[1], 0.25)] + fp_pairs(fa, 0.25) + fp_pairs(fb, 0.25))
    for fi, r in face_point.items():
        emit(r, fp_pairs(fi))
    faces, parent, cuv = [], [], []
    for fi in range(nf):
        f = [int(v) for v in F[fi]]
        q = [tuple(uv[fi][i]) for i in range(4)]
        if sel[fi]:
            c = face_point[fi]
            cu = tuple(np.mean(np.array(q), axis=0))
            for i in range(4):
                a, b, pv = f[i], f[(i + 1) % 4], f[(i - 1) % 4]
                eab = edge_point[(min(a, b), max(a, b))]
                epa = edge_point[(min(pv, a), max(pv, a))]
                ua, ub, up = np.array(q[i]), np.array(q[(i + 1) % 4]), np.array(q[(i - 1) % 4])
                faces.append((a, eab, c, epa))
                cuv.append([tuple(ua), tuple((ua + ub) / 2), cu, tuple((ua + up) / 2)])
                parent.append(fi)
            continue
        poly, puv = [], []
        for i in range(4):
            a, b = f[i], f[(i + 1) % 4]
            poly.append(a)
            puv.append(q[i])
            e = (min(a, b), max(a, b))
            if e in edge_point:
                poly.append(edge_point[e])
                puv.append(tuple((np.array(q[i]) + np.array(q[(i + 1) % 4])) / 2))
        if len(poly) == 4:
            faces.append(tuple(poly))
            cuv.append(puv)
            parent.append(fi)
            continue
        s0 = next(k for k, v in enumerate(poly) if v >= n)  # fan from the first edge point
        m = len(poly)
        for k in range(1, m - 1):
            i1, i2 = (s0 + k) % m, (s0 + k + 1) % m
            faces.append((poly[s0], poly[i1], poly[i2]))
            cuv.append([puv[s0], puv[i1], puv[i2]])
            parent.append(fi)
    return Subdiv(np.array(R), np.array(C), np.array(W), n_new, faces, np.array(parent), cuv, edge_point)


def bb_cage_cast(body, region, O, D, tmax):
    import bb_cage

    return bb_cage.cast(body, region, O, D, tmax=tmax, steps=160)


def correct_body(body: bb_anatomy.Body, V: Arr, reg: Arr) -> None:
    """Every region of the anatomy field re-seated on the donor skin (costume, hair and sandals
    ray-cast against these). The head's eyeball and socket primitives are dropped."""
    S = body.lm.S
    body.post = []
    for name in list(body.regions):
        m = reg == name
        if not m.any():
            continue
        fine = name.startswith(("head", "hand", "foot"))
        body.regions[name] = CorrectedRegion(body.regions[name], V[m], (0.0025 if fine else 0.004) * S)


def _grad(fn, P: Arr, eps: float = 3e-4) -> Arr:
    g = np.zeros_like(P)
    for i in range(3):
        e = np.zeros(3)
        e[i] = eps
        g[:, i] = fn(P + e) - fn(P - e)
    return g / np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-12)


def g2(dx: Arr, dz: Arr, sx: float, sz: float) -> Arr:
    return np.exp(-((dx / sx) ** 2) - ((dz / sz) ** 2))


def sculpt_face(lm: Landmarks, V: Arr, head: Arr, N: Arr, lips: Arr, lower: Arr, commissure: float) -> Arr:
    """Our face sculpt pass: the bb_params sliders as smooth face-space deformations. 1.0 / 0.0 =
    the donor's own form. `head` is a 0..1 per-vertex weight, `lips` a 0..1 lip weight."""
    p = lm.p
    h, s = lm.h, lm.h / 0.222
    zc = float(lm.P("chin")[2])
    yc = float(lm.P("head_c")[1])
    x, y, z = V[:, 0], V[:, 1], V[:, 2]
    front = np.clip((yc - 0.02 * h - y) / (0.25 * h), 0.0, 1.0)
    front = front * front * (3 - 2 * front)
    D = np.zeros_like(V)
    M = lm.P("mouth")
    # jaw width: the mandible below the mouth corners, about the midline
    jw = float(p["jaw_width"])
    wj = bb_face.smoothstep(M[2] + 0.02 * s, zc + 0.03 * s, z) * bb_face.smoothstep(0.02 * s, 0.06 * s, np.abs(x))
    D[:, 0] += x * (jw - 1.0) * wj
    # chin: scale about the chin point
    cs = float(p["chin_size"])
    C = lm.P("chin") + v3(0, 0.008 * s, 0.012 * s)
    wc = g2(x - C[0], z - C[2], 0.022 * s, 0.018 * s) * front
    D += (V - C) * (cs - 1.0) * wc[:, None] * np.array([1.0, 0.6, 1.0])
    # cheekbones: forward and outward bump under the outer eye, raised by cheekbone_height
    E = lm.P("eye")
    ch = float(p["cheekbone_height"]) * h
    cw = float(p["cheekbone_width"])
    for sg in (1.0, -1.0):
        wk = g2(x - sg * (E[0] + 0.012 * s), z - (E[2] - 0.022 * s), 0.016 * s, 0.012 * s) * front
        D[:, 2] += ch * wk
        D[:, 0] += sg * 0.002 * s * (cw - 1.0) * wk * 10.0
        D += N * (0.0008 * s * wk * (1.0 + 2.0 * (cw - 1.0)))[:, None]
    # nose bridge width (dorsum between the eyes and the tip) and tip projection
    nt = lm.P("nose_tip")
    bw = float(p["nose_bridge_width"])
    wb = g2(x, z - (E[2] - 0.012 * s), 0.012 * s, 0.016 * s) * front
    D[:, 0] += x * (bw - 1.0) * wb
    tp = float(p["nose_tip_projection"])
    wt = g2(x - nt[0], z - nt[2], 0.010 * s, 0.010 * s) * front
    D[:, 1] += (nt[1] - lm.P("subnasale")[1]) * (tp - 1.0) * wt
    # lips: vermilion volume about the lip line, forward and vertical
    lf = float(p["lip_fullness"])
    wl = lips * front
    D[:, 2] += (z - M[2]) * (lf - 1.0) * 0.6 * wl
    D[:, 1] -= 0.0012 * s * (lf - 1.0) * 2.0 * wl * np.exp(-((z - M[2]) / (0.006 * s)) ** 2)
    # mouth-corner lift: the commissures and the lip ends rise a little
    lift = float(p["mouth_corner_lift"])
    for sg in (1.0, -1.0):
        wm = g2(x - sg * commissure, z - M[2], 0.008 * s, 0.007 * s) * front
        D[:, 2] += lift * wm
    # brow ridge (the donor's = 1.0)
    br = float(p["brow_ridge"])
    for sg in (1.0, -1.0):
        wbr = g2(x - sg * (E[0] - 0.002 * s), z - (E[2] + 0.017 * s), 0.020 * s, 0.008 * s) * front
        D += N * (0.0016 * s * (br - 1.0) * wbr)[:, None]
    return V + D * head[:, None]


def inner_lip_loop(dn: Donor, Y: Arr) -> list[int]:
    """The donor's inner lip loop (the lip set's border toward the mouth), as body vertex ids."""
    inl = np.zeros(len(dn.F), bool)
    inl[dn.lips] = True
    bnd = [e for e, fs in dn.edges_f.items() if len(fs) == 2 and inl[fs[0]] != inl[fs[1]]]
    return min(loops_of(bnd), key=lambda lp: float(np.ptp(Y[lp, 0])))


def lip_rest(lm: Landmarks, dn: Donor, V: Arr, head: Arr, lips: Arr, lower: Arr) -> tuple[Arr, dict]:
    """M1-CHR-04: the lips' rest shape on the final (subdivided) face. Off at the bb_params defaults.

    * `lip_seal`: the lips meet. Around the contact line (the mid-height of the inner lip loop at
      each x) every vertex of the lip roll is squashed toward it in z by a monotone map
      (d -> d * (1 - k * exp(-(d / band)^2)), k < 1, so no surface crosses another), which closes
      the slit that showed the mouth interior and keeps the inner roll behind the contact.
    * `lip_lower_fullness`: the lower lip's forward roll, scaled about the contact plane.

    Also returns per-vertex texture terms for the bake: `lip_contact` (1 on the line where the
    lips meet, 1.2 mm falloff) and `lip_corner` (the contact in the outer quarter: the commissures)."""
    p = lm.p
    seal = float(p.get("lip_seal", 0.0))
    lo_full = float(p.get("lip_lower_fullness", 1.0))
    if seal == 0.0 and lo_full == 1.0:
        return V, {"lip_contact": np.zeros(len(V)), "lip_corner": np.zeros(len(V))}
    s = lm.h / 0.222
    loop = inner_lip_loop(dn, V[:md.N_BODY])
    L = V[loop]
    half = 0.5 * float(np.ptp(L[:, 0]))
    x, y, z = V[:, 0], V[:, 1], V[:, 2]
    # the contact line z(x) and its depth y(x): smooth even polynomials through the inner loop
    # (the loop's own vertices zigzag at the donor's spacing; pinning to them makes the lips wavy)
    u = np.clip(x / half, -1.0, 1.0)
    cz = np.polyfit((L[:, 0] / half) ** 2, L[:, 2], 3)
    cy = np.polyfit((L[:, 0] / half) ** 2, L[:, 1], 3)
    zl = np.polyval(cz, u * u)
    yl = np.polyval(cy, u * u)
    # the lip roll: near the contact, in front of the teeth, inside the mouth width
    width = bb_face.smoothstep(half + 0.003 * s, half - 0.002 * s, np.abs(x))
    depth = bb_face.smoothstep(0.012 * s, 0.004 * s, y - yl)
    w = width * depth * head
    D = np.zeros_like(V)
    dz = z - zl
    if seal:
        band = 0.0035 * s
        D[:, 2] += -dz * seal * np.exp(-((dz / band) ** 2)) * w
    if lo_full != 1.0:  # a wider falloff than the seal's toward the corners: no crease at the commissure
        wl = lips * lower * depth * head * bb_face.smoothstep(half + 0.004 * s, half - 0.010 * s, np.abs(x))
        wl = wl * bb_face.smoothstep(0.0, -0.002 * s, dz)
        D[:, 1] += np.minimum(y - yl, 0.0) * (lo_full - 1.0) * wl
    V = V + D
    wide = bb_face.smoothstep(half + 0.004 * s, half - 0.001 * s, np.abs(x)) * depth * head
    contact = np.exp(-(((V[:, 2] - zl) / (0.0012 * s)) ** 2)) * wide
    corner = contact * bb_face.smoothstep(0.7 * half, 0.95 * half, np.abs(x))
    return V, {"lip_contact": contact, "lip_corner": corner}


# ---------------------------------------------------------------------------------------------
# generate
# ---------------------------------------------------------------------------------------------
def tris_of(F: Arr) -> Arr:
    """Triangles of a padded polygon array (k, 4), where -1 in column 3 marks a triangle."""
    F = np.asarray(F)
    t1 = F[:, [0, 1, 2]]
    q = F[:, 3] >= 0
    t2 = F[q][:, [0, 2, 3]]
    return np.concatenate([t1, t2])


def face_normals_vertex(V: Arr, F: Arr) -> Arr:
    T = tris_of(F)
    fn = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
    N = np.zeros_like(V)
    for k in range(3):
        np.add.at(N, T[:, k], fn)
    return N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)


def poly_adjacency(F: Arr, n: int) -> tuple[Arr, Arr]:
    F = np.asarray(F)
    A, B = [], []
    for i in range(4):
        a, b = F[:, i], F[:, (i + 1) % 4]
        if i == 2:  # a triangle closes 2 -> 0
            b = np.where(F[:, 3] >= 0, F[:, 3], F[:, 0])
        if i == 3:
            ok = F[:, 3] >= 0
            a, b = a[ok], b[ok]
        A.append(a)
        B.append(b)
    a, b = np.concatenate(A), np.concatenate(B)
    e = np.unique(np.sort(np.stack([a, b], axis=1), axis=1), axis=0)
    return np.concatenate([e[:, 0], e[:, 1]]), np.concatenate([e[:, 1], e[:, 0]])


def face_regions(dn: Donor, ft: Fit) -> Arr:
    """Per donor quad: head (face mask and the rest of the head), scalp, mouth (cavity), or the
    body region of its vertices."""
    reg, F = dn.reg, dn.F
    freg = np.array([str(r) for r in reg[F[:, 0]]], dtype=object)
    fhead = np.array([np.mean(reg[f] == "head") > 0.5 for f in F])
    freg[fhead] = "head"
    freg[~fhead & (freg == "head")] = "torso"
    sc = np.zeros(len(F), bool)
    sc[dn.scalp] = True
    freg[fhead & sc] = "scalp"
    freg[fhead & ft.mouth_faces] = "mouth"
    return freg


def generate(params: dict, log=print, subdiv_face: bool = False) -> dict:
    """params -> the donor-topology body (numpy). Keys as bb_cage.generate (F is a padded (k, 4)
    polygon array, -1 marking triangles), plus `uv` (per face corner), `weights` ({DEF bone:
    (n,)}), `lower` (jaw weight), `lip_w`, `fit`, `subdiv`. `subdiv_face` adds one Catmull-Clark
    level on the face mask, lips and ears (the hero head)."""
    import time

    t0 = time.time()
    dn = donor()
    ft = fit(params)
    lm = ft.lm
    body = bb_anatomy.Body(lm)
    log(f"donor fit: {len(ft.X0)} donor verts ({time.time() - t0:.1f}s)")
    n = md.N_BODY
    F = dn.F.copy()
    V = ft.place(ft.X0[:n])
    uv = dn.mesh.VT[dn.T]
    reg = dn.reg.astype(object).copy()
    freg = face_regions(dn, ft)
    Wd: dict[str, Arr] = defaultdict(lambda: np.zeros(n))
    for g, wv in dn.W.items():
        for bone, k in bone_of(g):
            Wd[bone] = Wd[bone] + wv * k
    lipv = np.zeros(n)
    vf = np.zeros(len(F))
    vf[vermilion(dn)] = 1.0  # per vertex: the share of its faces that are vermilion (0.5 on the border)
    lipv = np.bincount(F.ravel(), weights=np.repeat(vf, 4), minlength=n) / np.maximum(np.bincount(F.ravel(), minlength=n), 1)
    lower = dn.lower.copy()
    sock = np.zeros(n)
    marg = np.zeros(n)
    for sd in ("L", "R"):
        sock[np.unique(F[ft.sockets[sd]])] = 1.0
        marg[ft.margins[sd]] = 1.0
    sock[marg > 0] = 0.0
    ear = _ear_mask(dn) | _ear_mask_r(dn)
    sub = None
    fsock = ft.sockets["L"] | ft.sockets["R"]  # per face: eye socket (behind the globe)
    fface = np.zeros(len(F), bool)  # per face: the face mask (MakeHuman's face and lips sets)
    fface[dn.face] = True
    fface[dn.lips] = True
    if subdiv_face:
        fset = np.zeros(len(F), bool)
        fset[dn.face] = True
        fset[dn.lips] = True
        fset &= ~np.array([ear[f].all() for f in F])  # ears stay at the donor density (budget)
        sel = fset & np.isin(freg, ["head", "mouth"]) & ~np.isin(np.arange(len(F)), np.nonzero(ft.mouth_faces)[0])
        sub = subdivide(F, sel, uv, n)
        V = sub.apply(V)
        lipv, lower = sub.apply(lipv), sub.apply(lower)
        sock = (sub.apply(sock) > 0.999).astype(float)
        marg = (sub.apply(marg) > 0.999).astype(float)
        Wd = defaultdict(lambda: np.zeros(sub.n_new), {k: sub.apply(v) for k, v in Wd.items()})
        new_reg = np.empty(sub.n_new, dtype=object)
        new_reg[:n] = reg
        for e, r in sub.edge_point.items():
            new_reg[r] = reg[e[0]] if reg[e[0]] == reg[e[1]] else "head" if "head" in (reg[e[0]], reg[e[1]]) else reg[e[0]]
        for k, fi in enumerate(np.nonzero(sel)[0]):
            new_reg[n + len(sub.edge_point) + k] = reg[F[fi][0]] if np.all(reg[F[fi]] == reg[F[fi][0]]) else "head"
        reg = new_reg
        Fp = -np.ones((len(sub.faces), 4), dtype=np.int64)
        UVp = np.zeros((len(sub.faces), 4, 2))
        for i, (f, q) in enumerate(zip(sub.faces, sub.corner_uv)):
            Fp[i, :len(f)] = f
            UVp[i, :len(f)] = q
        freg = freg[sub.parent]
        fsock, fface = fsock[sub.parent], fface[sub.parent]
        F, uv = Fp, UVp
        log(f"face subdivided: {int(sel.sum())} quads -> {sub.n_new} verts, {len(F)} polygons ({time.time() - t0:.1f}s)")
        n = sub.n_new
    if sub is not None:  # the subdivision rounds the lid margins inward: re-aim the eye warp on them
        _eye_warp(ft, dn, V[:md.N_BODY])
    V = ft.eye_warp(V)
    rows, cols = poly_adjacency(F, n)
    V = girth_fit(body, V, reg, rows, cols)
    log(f"girth fitted to the anatomy field ({time.time() - t0:.1f}s)")
    head_w = (reg == "head").astype(float)
    head_w = np.clip(smooth_scalar(head_w, rows, cols, 4) * 2.0 - 1.0, 0.0, 1.0)
    # the lip set's rings run on past the commissures onto the cheek: the red stops at the corners
    c = ft.commissure
    lipv = lipv * bb_face.smoothstep(c + 0.0025 * lm.S, c - 0.0005 * lm.S, np.abs(V[:, 0]))
    lips_s = smooth_scalar(lipv, rows, cols, 1)
    N = face_normals_vertex(V, F)
    V = sculpt_face(lm, V, head_w, N, lips_s, lower, ft.commissure)
    V, lip_terms = lip_rest(lm, dn, V, head_w, lips_s, lower)
    V = seat_eyes(lm, V, sock > 0, marg > 0)
    V[:, 2] = np.maximum(V[:, 2], 0.0)
    correct_body(body, V, reg)
    # the braid's gather point behind the left ear, 15 mm off the donor scalp (asha_hair._gather)
    yc, zc = float(lm.P("head_c")[1]), float(lm.P("chin")[2])
    G = np.array([[lm.head_w * 0.40, yc + 0.30 * lm.h, zc + 0.37 * lm.h]])
    for _ in range(4):
        G = G - _grad(body.regions["head"].sdf, G) * body.regions["head"].sdf(G)[:, None]
    lm.pts["hair_gather"] = (G + _grad(body.regions["head"].sdf, G) * 0.015 * lm.S)[0]
    log(f"anatomy field re-seated on the donor skin ({time.time() - t0:.1f}s)")
    # vertex regions follow the faces (a head vertex is one used only by head-type faces)
    hf = np.isin(freg, ["head", "scalp", "mouth"])
    vhead = np.zeros(n, bool)
    vbody = np.zeros(n, bool)
    vhead[np.unique(F[hf][F[hf] >= 0])] = True
    vbody[np.unique(F[~hf][F[~hf] >= 0])] = True
    reg = reg.astype(object)
    reg[vhead & ~vbody] = "head"
    reg[(reg == "head") & vbody] = "torso"
    groups = {"lip_line": [], "margin": list(np.nonzero(marg > 0)[0])}
    mix = np.array([float(params[f"donor_mix_{e}"]) for e in ETHNIC])
    mix = mix / max(mix.sum(), 1e-9)
    base = ft.place(ft.X0[:md.N_BODY])
    base = ft.eye_warp(sub.apply(base) if sub is not None else base)

    def unit_delta(unit: str) -> Arr:
        """A donor expression unit (CC0 target, the ethnic mix of ours) carried through our macro,
        placement, subdivision and eye warp: the re-targeted shape delta on the final vertices."""
        Dl = sum(w * md.load_target(f"expression/units/{e}/{unit}.target.gz") for e, w in zip(ETHNIC, mix) if w > 0)
        A = ft.place(ft.X0[:md.N_BODY] + Dl)
        A = ft.eye_warp(sub.apply(A) if sub is not None else A)
        return A - base

    log(f"donor body: {n} verts, {len(F)} polygons ({time.time() - t0:.1f}s)")
    return {"V": V, "F": F, "pin": np.zeros(n, bool), "seams": set(), "lm": lm, "body": body, "cage_V": V,
            "cage_F": F, "groups": groups, "n_cage_v": n, "reg": list(reg), "freg": freg, "uv": uv,
            "weights": dict(Wd), "lower": lower, "lip_w": lipv, "socket": sock > 0, "fit": ft, "subdiv": sub,
            **lip_terms,
            "face_socket": fsock, "face_mask": fface & ~fsock & (freg == "head"),
            "unit_delta": unit_delta}


def seat_eyes(lm: Landmarks, V: Arr, sock: Arr, marg: Arr) -> Arr:
    """Socket vertices tucked inside the globe; the outer lid skin kept a gap off it."""
    V = V.copy()
    for sd in ("L", "R"):
        fr = bb_face.EyeFrame(lm, sd)
        q = V - fr.E
        r = np.linalg.norm(q, axis=1)
        mine = r < 0.03 * lm.S
        s_idx = np.nonzero(sock & mine)[0]
        V[s_idx] = fr.E + q[s_idx] / np.maximum(r[s_idx, None], 1e-9) * np.minimum(r[s_idx, None], 0.9 * fr.R)
        gap = fr.R + EYE_GAP * lm.S
        o_idx = np.nonzero(mine & ~sock & (r < gap) & (q[:, 1] < 0.3 * fr.R))[0]
        V[o_idx] = fr.E + q[o_idx] / np.maximum(r[o_idx, None], 1e-9) * gap
    return V
