"""Virel, the Kite-Serpent, Asha's Fire Vowbound (M3-CRE-641): docs/kb/art/creatures/vowbound/virel.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/virel/build_virel.py -- --out assets/creatures/virel/virel.glb

A long ribbon-serpent of sailcloth panels, like a Saltwright signal kite flown alight as a flare. Her body is a chain
of taut panels sewn edge to edge on light timber battens and a spine spar, with bound light running along every seam
(the hems and the cross-seams: flattened bands, their own `seam` slot, all `glimmer_bound`). A kite head with a bowed
crest-spar and seam-ringed eyes leads it; a bridle of three lines meets under her throat, and from that knot hangs
a brass tuning key (the keepsake, the one thing about her that is not light or cloth). Two ribbon streamers trail
from the tail.

**Coiled.** 6.25 m of ribbon (a 0.75 m head and a 5.5 m body) is coiled once round an upright oval loop (1.2 m by
1.36 m) in a plane turned 22 degrees off the battle axis, so the default camera and the low summon camera both see the
sails, not their edges; the tail's pass is 0.55 m deeper than the neck's, so they clear each other. Coiled, she stays
inside the HUD's safe frame on both cameras (the design sheet has the margins).

**Built hovering**, like Ilun: the origin is the water point under her and the rest pose flies with the loop's
centre at 1.7 m, so the stand-in needs no `hover`. Every clip stays above the water.

Rig (16 bones): `root`, `body` (the loop's lowest station), `fore_0..4` (body to neck), `head`, `aft_0..5` (body
to tail), `streamer`, `key`. Each spine bone owns a stretch of the ribbon by arc length, not by distance, because the
coil passes close to itself.

`python3 build_virel.py --report` prints the triangle count, per-slot counts and per-clip lows (numpy, no export).
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

SEED = 6410
PAL = {k: ck.hexrgb(v) for k, v in {
    "sand_cloth": "#C9B48E", "faded_teal_cloth": "#5E9A96", "gauze_white": "#EBE7DF", "timber_weathered": "#7E6A55",
    "brass": "#B08D57", "deep_teal_shadow": "#0E4A55",
}.items()}

# ---- the coil (metres; Godot axes, facing +z) ------------------------------------------------------
PLANE_YAW = 22.0  # the coil's plane, turned off the battle axis toward the summon camera
_PY = math.radians(PLANE_YAW)
E_A = np.array([math.sin(_PY), 0.0, math.cos(_PY)])  # in-plane "forward"
E_N = np.array([math.cos(_PY), 0.0, -math.sin(_PY)])  # the plane's normal: the sails face it
LOOP_C = (0.1, 1.7)  # the loop's centre (a, y)
LOOP_RA, LOOP_RY = 0.6, 0.68  # an upright oval
LOOP_FROM, LOOP_TO = 90.0, 450.0  # degrees, counter-clockwise from the front: one turn, top to top
PITCH = -0.55  # depth (along E_N) per turn, so the tail's pass clears the neck's
A_SHIFT = 0.12  # the whole figure, forward of her mark: the tail keeps clear of the default camera's right edge
HEAD_A, HEAD_Y = (1.5, 0.76), (2.64, 2.56)  # the nose and the back of the head
TAIL = [(-0.42, 2.44), (-0.64, 2.5)]  # out of the loop's top, back and a little up
STATION = 0.5  # spine bone length (arc length per span)

# ---- the sails ---------------------------------------------------------------------------------------
PANEL = 0.4  # seam spacing along the body
W_NECK, W_LOOP, W_TAIL = 0.58, 0.48, 0.16  # full width at the neck, through the loop and at the tail end
HEAD_W = 0.56
SCALLOP = 0.06  # each panel's hem draws in this fraction of the width between seams (kite cells)
BILLOW = 0.05  # each panel bellies out by this fraction of its width
SKIN = 0.005  # half the sailcloth's thickness
NU, NV = 7, 9  # vertices along and across a panel
SEAM_R, SEAM_SQ = 0.016, 0.55  # the seams: flattened bands round the cloth's edges
HEM_R = 0.014
BATTEN_R = 0.009
SPINE_R = 0.012
SPAR_OFF = 0.016  # the frame is lashed on the sail's outer face (the cameras' side); the cloth bellies behind it
BATTEN_OVER = 0.05  # battens stand out past the hems
PATCH_EVERY = 3  # every third panel is a faded-teal Saltwright patch

# ---- the bridle and the key ------------------------------------------------------------------------
BRIDLE_DROP = 0.38  # the bridle knot under the throat
CORD_R = 0.004
KEY_CORD = 0.1
KEY_LEN, KEY_BOW_R = 0.17, 0.045
STREAMER_LEN, STREAMER_W = 0.55, 0.07
STREAMER_DROOP = 1.7  # the streamers hang down and back from the tail (downwind of a flown kite)

PARTS: dict[str, int] = {}


def count(name: str, mesh: ck.Mesh, before: int) -> None:
    PARTS[name] = PARTS.get(name, 0) + mesh.triangle_count - before


def plane(a, y, c) -> np.ndarray:
    a, y, c = (np.asarray(v, dtype=np.float64) for v in (a, y, c))
    return (a[..., None] + A_SHIFT) * E_A + y[..., None] * np.array([0.0, 1.0, 0.0]) + c[..., None] * E_N


# ---------------------------------------------------------------------------------------------
# The spine: a curve from the nose (s = -HEAD_LEN) through the back of the head (s = 0) to the tail end
# ---------------------------------------------------------------------------------------------
def _raw_curve() -> np.ndarray:
    pts = [plane(HEAD_A[0], HEAD_Y[0], 0.0), plane(1.13, 2.63, 0.0), plane(HEAD_A[1], HEAD_Y[1], 0.0)]
    pts.append(plane(0.42, 2.44, 0.0))
    th = np.radians(np.linspace(LOOP_FROM, LOOP_TO, 40))[1:-1]
    turns = (th - math.radians(LOOP_FROM)) / (2.0 * math.pi)
    a = LOOP_C[0] + LOOP_RA * np.cos(th)
    y = LOOP_C[1] + LOOP_RY * np.sin(th)
    for k in range(len(th)):
        pts.append(plane(a[k], y[k], PITCH * turns[k]))
    c_end = PITCH * (LOOP_TO - LOOP_FROM) / 360.0
    for ta, ty in TAIL:
        pts.append(plane(ta, ty, c_end))
    # a Catmull-Rom through the points, sampled densely
    P = np.array(pts)
    P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0.0, 1.0, 24, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2])
    return np.array(out)


class Spine:
    """The arc-length parametrised spine: position, tangent (toward the tail), and the sail's width direction."""

    def __init__(self) -> None:
        raw = _raw_curve()
        d = np.linalg.norm(np.diff(raw, axis=0), axis=1)
        s = np.concatenate([[0.0], np.cumsum(d)])
        # s = 0 at the back of the head: find the raw point nearest it
        back = plane(HEAD_A[1], HEAD_Y[1], 0.0)
        s0 = s[int(np.argmin(np.linalg.norm(raw - back, axis=1)))]
        self.s_raw = s - s0
        self.raw = raw
        self.s_min, self.s_max = float(self.s_raw[0]), float(self.s_raw[-1])
        self.length = self.s_max  # the body behind the head

    def at(self, s) -> np.ndarray:
        s = np.asarray(s, dtype=np.float64)
        return np.stack([np.interp(s, self.s_raw, self.raw[:, k]) for k in range(3)], axis=-1)

    def tangent(self, s) -> np.ndarray:
        h = 0.01
        t = self.at(np.asarray(s) + h) - self.at(np.asarray(s) - h)
        return t / np.linalg.norm(t, axis=-1, keepdims=True)

    def frame(self, s, twist=0.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """(tangent, width, normal) at s; the width lies in the coil's plane, turned `twist` degrees about the
        tangent; the normal is the sail's face (toward +E_N at rest)."""
        t = self.tangent(s)
        w = np.cross(t, E_N)
        w /= np.linalg.norm(w, axis=-1, keepdims=True)
        n = np.cross(w, t)
        tw = np.radians(np.asarray(twist, dtype=np.float64))[..., None]
        w2 = w * np.cos(tw) + n * np.sin(tw)
        n2 = np.cross(w2, t)
        return t, w2, n2


SPINE = Spine()
HEAD_LEN = -SPINE.s_min  # the head's sail, from the back of the head (s = 0) to the nose
N_SPANS = int(round(SPINE.length / STATION))
STATIONS = np.linspace(0.0, SPINE.length, N_SPANS + 1)
BODY_K = int(np.argmin(SPINE.at(STATIONS)[:, 1]))  # the body bone's station: the loop's lowest
FORE = [f"fore_{j}" for j in range(BODY_K)]  # fore_j: station BODY_K - j to BODY_K - j - 1
AFT = [f"aft_{j}" for j in range(N_SPANS - BODY_K)]  # aft_j: station BODY_K + j to BODY_K + j + 1


def width_at(s) -> np.ndarray:
    """The ribbon's full width at s (the head has its own outline)."""
    s = np.asarray(s, dtype=np.float64)
    u = np.clip(s / SPINE.length, 0.0, 1.0)
    w = np.where(u < 0.2, W_NECK + (W_LOOP - W_NECK) * ck.smoothstep(0.0, 0.2, u),
                 W_LOOP + (W_TAIL - W_LOOP) * ck.smoothstep(0.55, 1.0, u))
    hu = np.clip(-s / HEAD_LEN, 0.0, 1.0)  # 0 at the back of the head, 1 at the nose
    head = HEAD_W * (1.0 + 0.12 * np.sin(hu * math.pi * 0.9)) * np.clip(1.0 - hu, 0.0, 1.0) ** 0.55 + 0.02
    return np.where(s < 0.0, np.minimum(head, HEAD_W * 1.15), np.where(s < 0.15, w + (HEAD_W - w) * (1 - s / 0.15), w))


def twist_at(s) -> np.ndarray:
    """A gentle rest twist along the ribbon, so the sails are not all in one plane."""
    s = np.asarray(s, dtype=np.float64)
    return 14.0 * np.sin(s * 0.9 + 0.4)


SEAMS = np.concatenate([[0.0], np.arange(PANEL, SPINE.length - 0.05, PANEL), [SPINE.length]])


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def build_rig() -> ck.Rig:
    rig = ck.Rig()
    rig.add("root", (0, 0, 0), (0, 0.3, 0))
    p = SPINE.at(STATIONS)
    rig.add("body", p[BODY_K], p[BODY_K] + (0, 0.2, 0), "root")
    parent = "body"
    for j, name in enumerate(FORE):
        rig.add(name, p[BODY_K - j], p[BODY_K - j - 1], parent)
        parent = name
    rig.add("head", p[0], SPINE.at(-HEAD_LEN), parent)
    parent = "body"
    for j, name in enumerate(AFT):
        rig.add(name, p[BODY_K + j], p[BODY_K + j + 1], parent)
        parent = name
    tail = p[-1]
    rig.add("streamer", tail, tail + streamer_dir() * STREAMER_LEN, AFT[-1])
    knot = bridle_knot()
    rig.add("key", knot, knot - (0, 0.25, 0), "head")
    return rig


def streamer_dir() -> np.ndarray:
    d = SPINE.tangent(SPINE.length) + np.array([0.0, -STREAMER_DROOP, 0.0])
    return d / np.linalg.norm(d)


def owner(k: int) -> str:
    """The bone that owns span k (station k to k + 1); -1 is the head."""
    if k < 0:
        return "head"
    return FORE[BODY_K - 1 - k] if k < BODY_K else AFT[k - BODY_K]


def skin_s(rig: ck.Rig, s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Weights by arc length: each span's bone, blended 50/50 at each joint across 0.3 of a span."""
    blend = 0.3
    n = len(s)
    J = np.zeros((n, 2), dtype=np.int64)
    W = np.zeros((n, 2))
    for i in range(n):
        si = float(s[i])
        k = -1 if si < 0.0 else min(int(si // STATION), N_SPANS - 1)
        J[i] = rig.index(owner(k))
        W[i] = (1.0, 0.0)
        if k < 0:
            t = 1.0 + si / HEAD_LEN  # 1 at the back of the head
            if t > 1.0 - blend * 0.6:
                w = float(ck.smoothstep(1.0 - blend * 0.6, 1.0, t)) * 0.5
                J[i, 1], W[i] = rig.index(owner(0)), (1.0 - w, w)
            continue
        t = (si - STATIONS[k]) / STATION
        if t < blend:
            w = float(ck.smoothstep(blend, 0.0, t)) * 0.5
            J[i, 1], W[i] = rig.index(owner(k - 1)), (1.0 - w, w)
        elif t > 1.0 - blend and k + 1 < N_SPANS:
            w = float(ck.smoothstep(1.0 - blend, 1.0, t)) * 0.5
            J[i, 1], W[i] = rig.index(owner(k + 1)), (1.0 - w, w)
    # the body station: both halves are the body's children, so no blend is needed there
    return J, W


def fixed(J, W):
    return lambda P: (J, W)


# ---------------------------------------------------------------------------------------------
# Mesh
# ---------------------------------------------------------------------------------------------
def ribbon_point(s, v, bulge=0.0, side=0.0) -> np.ndarray:
    """A point on the sail at arc length s and across-fraction v (-1 .. 1), pushed `bulge` along the normal and
    `side` (the cloth's half thickness, signed) further."""
    s = np.asarray(s, dtype=np.float64)
    _, w, n = SPINE.frame(s, twist_at(s))
    half = 0.5 * width_at(s)
    return SPINE.at(s) + w * (np.asarray(v)[..., None] * half[..., None]) + n * (np.asarray(bulge) + side)[..., None]


def scallop(s) -> np.ndarray:
    """1 at the seams, 1 - SCALLOP mid-panel: the hems draw in between seams."""
    s = np.asarray(s, dtype=np.float64)
    k = np.clip(np.searchsorted(SEAMS, s, side="right") - 1, 0, len(SEAMS) - 2)
    u = (s - SEAMS[k]) / (SEAMS[k + 1] - SEAMS[k])
    return np.where(s < 0.0, 1.0, 1.0 - SCALLOP * np.sin(math.pi * np.clip(u, 0.0, 1.0)))


def panel_u(s) -> np.ndarray:
    s = np.asarray(s, dtype=np.float64)
    k = np.clip(np.searchsorted(SEAMS, s, side="right") - 1, 0, len(SEAMS) - 2)
    return np.clip((s - SEAMS[k]) / (SEAMS[k + 1] - SEAMS[k]), 0.0, 1.0), k


def sail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The panels (and the head's sail) as one closed slab: front and back faces and a thin rim."""
    ss = [np.linspace(-HEAD_LEN + 0.01, 0.0, 10, endpoint=False)]
    for k in range(len(SEAMS) - 1):
        ss.append(np.linspace(SEAMS[k], SEAMS[k + 1], NU, endpoint=False))
    s = np.concatenate(ss + [[SPINE.length]])
    v = np.linspace(-1.0, 1.0, NV)
    S, V = np.meshgrid(s, v, indexing="ij")
    u, pk = panel_u(S)
    bul = -BILLOW * width_at(S) * np.sin(math.pi * u) * np.cos(0.5 * math.pi * V) * (S >= 0.0)
    bul = bul - (S < 0.0) * 0.03 * np.cos(0.5 * math.pi * V) * np.sin(math.pi * np.clip(-S / HEAD_LEN, 0, 1))
    Vs = V * scallop(S)
    rows, cols = S.shape
    faces = []
    for side in (1.0, -1.0):
        P = ribbon_point(S, Vs, bul, side * SKIN).reshape(-1, 3)
        T = ck.grid_tris(rows, cols, False)
        faces.append((P, ck.flip(T) if side > 0 else T))  # grid_tris winds toward -n: the front face is flipped
    P = np.vstack([faces[0][0], faces[1][0]])
    T = np.vstack([faces[0][1], faces[1][1] + rows * cols])
    # the rim: join the two faces round the outline (the hems cover it; it closes the slab edge-on)
    rim = []
    off = rows * cols
    for r in range(rows - 1):
        for c in (0, cols - 1):
            a, b = r * cols + c, (r + 1) * cols + c
            q = [(a, b, b + off), (a, b + off, a + off)]
            rim += q if c == 0 else [x[::-1] for x in q]
    T = np.vstack([T, np.asarray(rim, dtype=np.int64)])
    s_all = np.concatenate([S.reshape(-1), S.reshape(-1)])
    u_all = np.concatenate([u.reshape(-1), u.reshape(-1)])
    v_all = np.concatenate([V.reshape(-1), V.reshape(-1)])
    k_all = np.concatenate([pk.reshape(-1), pk.reshape(-1)])
    # colour: sand_cloth, every third panel a faded-teal patch; paler (light through the cloth) mid-panel, a little
    # darker toward the burning seams; the head is sand_cloth with a teal mask band
    patch = ((k_all % PATCH_EVERY) == 1) & (s_all >= 0.0)
    base = np.where(patch[:, None], PAL["faded_teal_cloth"], PAL["sand_cloth"])
    edge = np.maximum(np.abs(v_all), np.abs(2.0 * u_all - 1.0) * (s_all >= 0.0))
    mott = ck.smoothstep(-0.3, 0.4, ck.fbm(P * 3.0, SEED))
    col = ck.mix(base, PAL["gauze_white"], (0.22 * (1.0 - edge) * (0.6 + 0.4 * mott))[:, None])
    col = ck.mix(col, PAL["timber_weathered"], (0.28 * ck.smoothstep(0.7, 1.0, edge))[:, None])
    hu = np.clip(-s_all / HEAD_LEN, 0.0, 1.0)
    mask = (s_all < 0.0) & (np.abs(v_all + 0.15) < 0.22) & (hu > 0.25)
    col = np.where(mask[:, None], ck.mix(PAL["faded_teal_cloth"], PAL["deep_teal_shadow"], 0.25), col)
    glow = 0.05 + 0.3 * ck.smoothstep(0.75, 1.0, edge)  # the cloth lit through from its seams
    J, W = skin_s(rig, s_all)
    before = mesh.triangle_count
    ck.finish(mesh, P, T, "sail", col, fixed(J, W), wet=0.0, emission=glow)
    count("sail", mesh, before)


def seams(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Bound light along every seam: the two hems (the whole length, round the head) and each cross-seam."""
    before = mesh.triangle_count
    Ps, Ts, ss = [], [], []
    base = 0
    s_hem = np.concatenate([np.linspace(-HEAD_LEN + 0.005, 0.0, 14, endpoint=False),
                            np.linspace(0.0, SPINE.length, int(SPINE.length / 0.05) + 1)])
    for v in (-1.0, 1.0):
        path = ribbon_point(s_hem, v * scallop(s_hem))
        _, _, n = SPINE.frame(s_hem, twist_at(s_hem))
        P, T = _band(path, HEM_R, n)
        Ps.append(P)
        Ts.append(T + base)
        ss.append(_s_for(P, path, s_hem))
        base += len(P)
    for s0 in SEAMS:
        v = np.linspace(-1.0, 1.0, 9)
        sv = np.full(len(v), s0)
        path = ribbon_point(sv, v)
        _, _, n = SPINE.frame(sv, twist_at(sv))
        P, T = _band(path, SEAM_R, n)
        Ps.append(P)
        Ts.append(T + base)
        ss.append(_s_for(P, path, sv))
        base += len(P)
    P = np.vstack(Ps)
    T = np.vstack(Ts)
    s_all = np.concatenate(ss)
    J, W = skin_s(rig, s_all)
    ck.finish(mesh, P, T, "seam", PAL["gauze_white"], fixed(J, W), emission=1.0)
    count("seam", mesh, before)


def _band(path: np.ndarray, r: float, normal: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """A flattened tube along `path`, its flat side facing `normal` (so the band lies on the cloth)."""
    P, T = ck.tube(path, r, 6, cap_start=True, cap_end=True, up_hint=tuple(normal[0]), squash=1.0)
    # flatten along the cloth's normal
    K = len(path)
    segs = 6
    ring = P[:K * segs].reshape(K, segs, 3)
    rel = ring - path[:, None, :]
    along_n = np.einsum("ksj,kj->ks", rel, normal)
    ring = ring - normal[:, None, :] * along_n[..., None] * (1.0 - SEAM_SQ)
    P = P.copy()
    P[:K * segs] = ring.reshape(-1, 3)
    return P, T


def _s_for(P: np.ndarray, path: np.ndarray, s: np.ndarray) -> np.ndarray:
    """Each band vertex's arc length: its ring's (rings run along the path, segs per ring, then the caps)."""
    K = len(path)
    segs = 6
    out = np.repeat(np.asarray(s, dtype=np.float64), segs)
    caps = len(P) - K * segs
    if caps >= 1:
        out = np.concatenate([out, [s[0]]])
    if caps >= 2:
        out = np.concatenate([out, [s[-1]]])
    return out


def spars(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Light timber: a spine spar on the sail's back, a batten across each panel, and the head's bowed crest-spar."""
    before = mesh.triangle_count
    s_sp = np.linspace(-HEAD_LEN * 0.85, SPINE.length - 0.04, int((SPINE.length + HEAD_LEN) / 0.06))
    _, _, n = SPINE.frame(s_sp, twist_at(s_sp))
    path = SPINE.at(s_sp) + n * SPAR_OFF
    P, T = ck.tube(path, SPINE_R, 6, cap_start=True, cap_end=True)
    J, W = skin_s(rig, _s_for(P, path, s_sp))
    col = PAL["timber_weathered"]
    ck.finish(mesh, P, T, "spar", col, fixed(J, W))
    for k in range(len(SEAMS) - 1):
        sm = 0.5 * (SEAMS[k] + SEAMS[k + 1])
        v = np.linspace(-1.0, 1.0, 5)
        sv = np.full(len(v), sm)
        t, w, n = SPINE.frame(sv, twist_at(sv))
        half = 0.5 * width_at(sv) * scallop(sv) + BATTEN_OVER
        path = SPINE.at(sv) + w * (v * half)[:, None] + n * SPAR_OFF
        P, T = ck.tube(path, BATTEN_R, 5, cap_start=True, cap_end=True)
        J, W = skin_s(rig, np.full(len(P), sm))
        ck.finish(mesh, P, T, "spar", col, fixed(J, W))
    # the head: a batten across the cheek and the bowed crest-spar, its ends swept back past the head like a crest
    for sv0 in (-0.3,):
        v = np.linspace(-1.0, 1.0, 5)
        sv = np.full(len(v), sv0)
        t, w, n = SPINE.frame(sv, twist_at(sv))
        half = 0.5 * width_at(sv) + BATTEN_OVER
        path = SPINE.at(sv) + w * (v * half)[:, None] + n * SPAR_OFF
        P, T = ck.tube(path, BATTEN_R, 5)
        ck.finish(mesh, P, T, "spar", col, rig.rigid("head"))
    hb = rig.rigid("head")
    for dz, r in ((0.0, 0.011), (0.05, 0.008), (-0.05, 0.008)):
        P0 = crest_path(dz)
        tt = np.linspace(0.0, 1.0, len(P0))
        P, T = ck.tube(P0, r * (1.0 - 0.6 * tt), 5)
        ck.finish(mesh, P, T, "spar", col, hb)
    count("spar", mesh, before)


def crest_path(dz: float) -> np.ndarray:
    """The bowed spar over the head's upper hem: from the snout, arcing up over the crown and swept back past it."""
    s = np.array([-HEAD_LEN * 0.75, -0.45, -0.18, 0.08, 0.3])
    lift = np.array([0.0, 0.06, 0.1, 0.15, 0.2])
    t, w, n = SPINE.frame(s, twist_at(s))
    up = -w  # the head's upper side
    base = SPINE.at(s) + up * (0.5 * width_at(np.minimum(s, 0.0)))[:, None]
    P = base + up * lift[:, None] + n * dz
    return ck.bezier(P, 18)


def eyes(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Two seam-light rings on the head, one on each face of the cloth (a kite's painted eye, drawn in light)."""
    before = mesh.triangle_count
    s0, v0 = -0.5, -0.38
    t, w, n = SPINE.frame(np.array([s0]), twist_at(np.array([s0])))
    t, w, n = t[0], w[0], n[0]
    c = SPINE.at(s0) + w * v0 * 0.5 * float(width_at(np.array(s0)))
    for side in (1.0, -1.0):
        ph = np.linspace(0.0, 2.0 * math.pi, 17)
        r = 0.045
        path = c + (np.outer(np.cos(ph), t) * 1.3 + np.outer(np.sin(ph), w)) * r + n * side * (SKIN + 0.002)
        P, T = ck.tube(path, 0.009, 5, cap_start=False, cap_end=False, up_hint=tuple(n))
        ck.finish(mesh, P, T, "seam", PAL["gauze_white"], rig.rigid("head"), emission=1.0)
        Pd, Td = ck.ellipsoid(c + n * side * (SKIN + 0.004), (0.02, 0.02, 0.02), 4, 8)  # the pupil
        ck.finish(mesh, Pd, Td, "seam", PAL["gauze_white"], rig.rigid("head"), emission=0.85)
    count("eyes", mesh, before)


def bridle_points() -> list[np.ndarray]:
    """Where the bridle lines leave the head's lower hem (the throat), and the cheek batten's ends."""
    out = []
    for s0 in (-0.55, -0.3, -0.02):
        t, w, n = SPINE.frame(np.array([s0]), twist_at(np.array([s0])))
        out.append(SPINE.at(s0) + w[0] * 0.5 * float(width_at(np.array(s0))) * 0.92)
    return out


def bridle_knot() -> np.ndarray:
    pts = bridle_points()
    return np.mean(pts, axis=0) + np.array([0.0, -BRIDLE_DROP, 0.0])


def bridle(mesh: ck.Mesh, rig: ck.Rig) -> None:
    before = mesh.triangle_count
    knot = bridle_knot()
    hb = rig.rigid("head")
    for p in bridle_points():
        path = np.array([p + (knot - p) * f for f in np.linspace(0.0, 1.0, 5)])
        P, T = ck.tube(path, CORD_R, 4, cap_start=False, cap_end=False)
        ck.finish(mesh, P, T, "cord", PAL["sand_cloth"], hb)
    Pk, Tk = ck.ellipsoid(knot, (0.014, 0.012, 0.014), 4, 6)
    ck.finish(mesh, Pk, Tk, "cord", PAL["sand_cloth"], hb)
    kb = rig.rigid("key")
    path = np.array([knot + (0.0, -f * KEY_CORD, 0.0) for f in np.linspace(0.0, 1.0, 4)])
    P, T = ck.tube(path, CORD_R, 4, cap_start=False, cap_end=False)
    ck.finish(mesh, P, T, "cord", PAL["sand_cloth"], kb)
    count("cord", mesh, before)


def key(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The brass tuning key: a ring bow, a collar, a shaft and a hollow square socket, hanging from the knot."""
    before = mesh.triangle_count
    kb = rig.rigid("key")
    top = bridle_knot() - (0.0, KEY_CORD, 0.0)
    c = top - (0.0, KEY_BOW_R, 0.0)
    ph = np.linspace(0.0, 2.0 * math.pi, 21)
    ring = c + np.column_stack([np.zeros(len(ph)), np.cos(ph) * KEY_BOW_R, np.sin(ph) * KEY_BOW_R * 1.15])
    P, T = ck.tube(ring, 0.011, 6, cap_start=False, cap_end=False, up_hint=(1.0, 0.0, 0.0))
    ck.finish(mesh, P, T, "key", PAL["brass"], kb)
    y0 = c[1] - KEY_BOW_R
    prof = [(0.0, y0 + 0.004), (0.016, y0), (0.016, y0 - 0.018), (0.009, y0 - 0.024), (0.009, y0 - KEY_LEN + 0.03),
            (0.017, y0 - KEY_LEN + 0.026), (0.017, y0 - KEY_LEN), (0.0, y0 - KEY_LEN - 0.002)]
    P, T = ck.lathe(prof, 8)
    P = P + np.array([c[0], 0.0, c[2]])
    ck.finish(mesh, P, T, "key", PAL["brass"], kb)
    count("key", mesh, before)


def streamers(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Two ribbon streamers from the tail end, splayed a little, lit along their middles."""
    before = mesh.triangle_count
    end = SPINE.at(SPINE.length)
    t, w, n = SPINE.frame(np.array([SPINE.length]), twist_at(np.array([SPINE.length])))
    t, w, n = t[0], w[0], n[0]
    sb = rig.rigid("streamer")
    for sgn in (1.0, -1.0):
        k = np.linspace(0.0, 1.0, 10)
        path = end[None] + np.outer(k * STREAMER_LEN, streamer_dir()) + np.outer(sgn * (0.05 + 0.12 * k ** 1.3), w) \
            + np.outer(0.05 * np.sin(k * math.pi * 1.5), n)
        half = STREAMER_W * 0.5 * (1.0 - 0.6 * k)
        Ps = []
        for side in (1.0, -1.0):
            for vv in (-1.0, 0.0, 1.0):
                Ps.append(path + w * (vv * half)[:, None] + n * side * SKIN)
        P = np.vstack(Ps)
        Kn = len(path)
        T = []
        for f in range(2):
            o = f * 3 * Kn
            for i in range(Kn - 1):
                for j in range(2):
                    a, b = o + j * Kn + i, o + (j + 1) * Kn + i
                    q = [(a, b, a + 1), (a + 1, b, b + 1)]
                    T += q if f == 0 else [x[::-1] for x in q]
        mid = np.tile(np.concatenate([np.full(Kn, 0.0), np.full(Kn, 1.0), np.full(Kn, 0.0)]), 2)
        col = ck.mix(PAL["sand_cloth"], PAL["gauze_white"], 0.3)
        ck.finish(mesh, P, np.asarray(T), "sail", col, sb, emission=0.15 + 0.6 * mid)
    count("streamers", mesh, before)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    PARTS.clear()
    mesh = ck.Mesh("virel")
    sail(mesh, rig)
    seams(mesh, rig)
    spars(mesh, rig)
    eyes(mesh, rig)
    bridle(mesh, rig)
    key(mesh, rig)
    streamers(mesh, rig)
    return mesh


# ---------------------------------------------------------------------------------------------
# Posing helpers: rotations about arbitrary axes, as the kit's Euler keys
# ---------------------------------------------------------------------------------------------
def axis_angle(axis, deg: float) -> np.ndarray:
    a = np.asarray(axis, dtype=np.float64)
    a = a / np.linalg.norm(a)
    th = math.radians(deg)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + math.sin(th) * K + (1 - math.cos(th)) * (K @ K)


def to_euler(R: np.ndarray) -> tuple[float, float, float]:
    """(rx, ry, rz) degrees with ck.euler(rx, ry, rz) == R (R = Rz Ry Rx)."""
    ry = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    rx = math.atan2(R[2, 1], R[2, 2])
    rz = math.atan2(R[1, 0], R[0, 0])
    return (math.degrees(rx), math.degrees(ry), math.degrees(rz))


def min_rot(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """The least rotation taking direction a to direction b."""
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    c = float(np.dot(a, b))
    ax = np.cross(a, b)
    s = float(np.linalg.norm(ax))
    if s < 1e-9:
        if c > 0:
            return np.eye(3)
        perp = np.cross(a, E_N if abs(np.dot(a, E_N)) < 0.9 else np.array([0.0, 1.0, 0.0]))
        return axis_angle(perp, 180.0)
    return axis_angle(ax / s, math.degrees(math.atan2(s, c)))


RIG = build_rig()
REST_DIR = {b.name: (np.asarray(b.tail) - np.asarray(b.head)) / np.linalg.norm(np.asarray(b.tail) - np.asarray(b.head))
            for b in RIG.bones}
PARENT = {b.name: b.parent for b in RIG.bones}


def _rest_normal(b: ck.Bone) -> np.ndarray:
    """The sail's face at the middle of the stretch a spine bone owns (E_N for the others)."""
    mid = 0.5 * (np.asarray(b.head) + np.asarray(b.tail))
    if b.name not in FORE + AFT + ["head"]:
        return E_N
    s_near = SPINE.s_raw[int(np.argmin(np.linalg.norm(SPINE.raw - mid, axis=1)))]
    return SPINE.frame(np.array([s_near]), twist_at(np.array([s_near])))[2][0]


REST_NORMAL = {b.name: _rest_normal(b) for b in RIG.bones}
CHAIN = ["head"] + FORE[::-1] + AFT  # nose to tail, for travelling waves
CHAIN_POS = {name: i for i, name in enumerate(CHAIN)}


def local_rot(bend: float = 0.0, twist: float = 0.0, bone: str = "body", sway: float = 0.0) -> np.ndarray:
    """A bone's rotation: `bend` about the coil's normal (in the coil's plane), `twist` about the bone's own rest
    direction (the panels luff), `sway` about the in-plane width (out of the plane)."""
    d = REST_DIR[bone]
    w = np.cross(d, E_N)
    return axis_angle(d, twist) @ axis_angle(E_N, bend) @ axis_angle(w, sway)


def key_rot(c: ck.Clip, bone: str, t: float, R: np.ndarray, loc=(0.0, 0.0, 0.0)) -> None:
    c.key(bone, t, to_euler(R), loc)


def directions_pose(dirs: dict[str, np.ndarray], face: np.ndarray = E_N) -> dict[str, np.ndarray]:
    """Local rotations that lay each named bone along a world direction (parents first), rolled so its sail faces
    `face` as nearly as it can; bones not named keep their parent's turn (a zero local rotation)."""
    world: dict[str, np.ndarray] = {"root": np.eye(3), "body": np.eye(3)}
    out: dict[str, np.ndarray] = {}
    for b in RIG.bones:
        if b.name in ("root", "body"):
            continue
        Gp = world[b.parent]
        if b.name in dirs:
            d = dirs[b.name] / np.linalg.norm(dirs[b.name])
            G = min_rot(REST_DIR[b.name], d)
            n_now = G @ REST_NORMAL[b.name]
            want = face - np.dot(face, d) * d
            n_now = n_now - np.dot(n_now, d) * d
            ang = math.degrees(math.atan2(float(np.dot(np.cross(n_now, want), d)), float(np.dot(n_now, want))))
            G = axis_angle(d, ang) @ G
        else:
            G = Gp
        world[b.name] = G
        out[b.name] = Gp.T @ G
    return out


def chain_curl(deg_fore: float, deg_aft: float, head: float = 0.0) -> dict[str, np.ndarray]:
    """Every fore bone bent `deg_fore`, every aft bone `deg_aft`, the head `head` (about the coil's normal)."""
    out = {n: axis_angle(E_N, deg_fore) for n in FORE}
    out.update({n: axis_angle(E_N, deg_aft) for n in AFT})
    out["head"] = axis_angle(E_N, head)
    return out


# ---------------------------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------------------------
IDLE_SEC = 4.0
READY_SEC = 1.4
ATTACK_SEC = 1.2
ATTACK_CONTACT = 0.5
CAST_SEC = 1.6
CAST_CONTACT = 0.6
HIT_SEC = 0.5
HIT_PEAK = 0.1
DEFEND_SEC = 1.2
KO_SEC = 1.8
VICTORY_SEC = 2.2
RISE_SEC = 2.6
DISMISS_SEC = 1.0
SPECIAL_SEC = 2.4
SPECIAL_CONTACT = 1.4
KO_DROP = 0.2  # the KO settles her this far (the stage then draws her under)
KEY_LAG = 0.12  # the key swings this far behind the head's motion
KEY_HANG = 0.9  # and counter-turns this much of it

SPINE_BONES = FORE + ["head"] + AFT


def pose_keys(c: ck.Clip, t: float, pose: dict[str, np.ndarray], body=(0.0, 0.0, 0.0), body_rot=None,
              root=(0.0, 0.0, 0.0), streamer: float = 0.0) -> None:
    """Keys every spine bone (zero where `pose` leaves it), the body, the root and the streamer at t."""
    for b in SPINE_BONES:
        key_rot(c, b, t, pose.get(b, np.eye(3)))
    key_rot(c, "body", t, np.eye(3) if body_rot is None else body_rot, body)
    c.key("root", t, (0, 0, 0), root)
    key_rot(c, "streamer", t, local_rot(twist=streamer, bone="streamer"))


def blend_pose(a: dict, b: dict, u: float) -> dict:
    """Per bone, the rotation u of the way from a to b (axis-angle interpolation of the relative turn)."""
    out = {}
    for n in set(a) | set(b):
        Ra, Rb = a.get(n, np.eye(3)), b.get(n, np.eye(3))
        Rd = Ra.T @ Rb
        ang = math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(Rd) - 1.0) / 2.0))))
        if ang < 1e-6:
            out[n] = Ra
            continue
        ax = np.array([Rd[2, 1] - Rd[1, 2], Rd[0, 2] - Rd[2, 0], Rd[1, 0] - Rd[0, 1]])
        if np.linalg.norm(ax) < 1e-9:
            out[n] = Ra if u < 0.5 else Rb
            continue
        out[n] = Ra @ axis_angle(ax, ang * u)
    return out


def compose(*poses: dict) -> dict:
    out: dict = {}
    for p in poses:
        for n, R in p.items():
            out[n] = out.get(n, np.eye(3)) @ R
    return out


def wave_pose(t: float, length: float, bend: float, twist: float, cycles: float = 1.0, lag: float = 0.55,
              phase: float = 0.0) -> dict:
    """A travelling wave from the nose to the tail: each bone bends and luffs, a little behind the one before."""
    out = {}
    for name in CHAIN:
        k = CHAIN_POS[name]
        ph = 2.0 * math.pi * cycles * t / length - lag * k + phase
        out[name] = local_rot(bend=bend * math.sin(ph), twist=twist * math.sin(ph + 0.9), bone=name)
    return out


def keyed(c: ck.Clip, poses: list[tuple], step: float = 1.0 / ck.FPS) -> ck.Clip:
    """Keys a clip at every frame from (t, pose, body_loc, root_loc, streamer) keyframes, easing between them with
    the axis-angle blend (so large turns stay clean) plus `extra(t)` waves when given."""
    times = [p[0] for p in poses]
    f = 0
    while True:
        t = min(f * step, c.length)
        i = max(0, min(len(times) - 2, int(np.searchsorted(times, t, side="right") - 1)))
        t0, t1 = times[i], times[i + 1]
        u = 0.0 if t1 <= t0 else float(ck.smoothstep(0.0, 1.0, (t - t0) / (t1 - t0)))
        a, b = poses[i], poses[i + 1]
        pose = blend_pose(a[1], b[1], u)
        body = tuple(np.asarray(a[2]) * (1 - u) + np.asarray(b[2]) * u)
        root = tuple(np.asarray(a[3]) * (1 - u) + np.asarray(b[3]) * u)
        st = a[4] * (1 - u) + b[4] * u
        if len(a) > 5 and a[5] is not None:
            pose = compose(pose, a[5](t))
        pose_keys(c, t, pose, body=body, root=root, streamer=st)
        if t >= c.length:
            break
        f += 1
    return c


def build_idle() -> ck.Clip:
    c = ck.Clip("idle", IDLE_SEC, loop=True)  # a slow undulation down the body, the panels luffing
    frames = int(round(IDLE_SEC * ck.FPS))
    for f in range(frames + 1):
        t = f / ck.FPS
        pose = wave_pose(t, IDLE_SEC, bend=0.9, twist=4.0)
        bob = 0.04 * math.sin(2.0 * math.pi * t / IDLE_SEC + math.pi)
        st = 16.0 * math.sin(2.0 * math.pi * 2.0 * t / IDLE_SEC)
        pose_keys(c, t, pose, body=(0.0, bob, 0.0), streamer=st)
    return c


def build_ready() -> ck.Clip:
    c = ck.Clip("ready", READY_SEC)  # she gathers: the coil draws in and the head rears, then she snaps taut
    gather = chain_curl(2.0, -3.0, head=-12.0)
    taut = chain_curl(-2.0, 2.0, head=4.0)
    return keyed(c, [(0.0, {}, (0, 0, 0), (0, 0, 0), 0.0), (0.5, gather, (0, 0.1, 0), (0, 0, 0), 20.0),
                     (0.95, taut, (0, 0.03, 0), (0, 0, 0), -14.0), (READY_SEC, {}, (0, 0, 0), (0, 0, 0), 0.0)])


def build_attack() -> ck.Clip:
    """The whipping strike: the neck draws back and the head rears; then the whip runs up the neck and the head
    lashes forward and down onto the target at the contact, the body thrown after it."""
    c = ck.Clip("attack", ATTACK_SEC)
    neck = FORE[-3:]
    rear = {n: axis_angle(E_N, -6.0) for n in neck}
    rear["head"] = axis_angle(E_N, -12.0)
    lash = {n: axis_angle(E_N, 7.0) for n in neck}
    lash["head"] = axis_angle(E_N, 18.0)
    follow = {n: axis_angle(E_N, 2.0) for n in neck}
    aft_rear = {n: local_rot(bend=-2.0, twist=10.0, bone=n) for n in AFT}
    aft_lash = {n: local_rot(bend=2.5, twist=-14.0, bone=n) for n in AFT}
    return keyed(c, [(0.0, {}, (0, 0, 0), (0, 0, 0), 0.0),
                     (0.3, compose(rear, aft_rear), (0, 0.04, -0.06), (0, 0, 0), 22.0),
                     (ATTACK_CONTACT, compose(lash, aft_lash), (0, -0.04, 0.16), (0, 0, 0), -26.0),
                     (0.75, compose(follow, {n: local_rot(twist=6.0, bone=n) for n in AFT}), (0, 0, 0.05), (0, 0, 0),
                      12.0),
                     (ATTACK_SEC, {}, (0, 0, 0), (0, 0, 0), 0.0)])


def build_cast() -> ck.Clip:
    """Kite Flare: a gust through the whole kite (the panels turn and flare), the head rears, then three quick jabs
    of the head (the fast multi-hit fire), the first on the contact."""
    c = ck.Clip("cast", CAST_SEC)
    flare = {n: local_rot(twist=12.0 * (1 if CHAIN_POS[n] % 2 else -1), bone=n) for n in SPINE_BONES}
    flare = compose(flare, {n: axis_angle(E_N, -1.5) for n in FORE[-3:]})
    flare["head"] = flare["head"] @ axis_angle(E_N, -10.0)

    def jab(k: float) -> dict:
        out = compose(flare, {n: axis_angle(E_N, 4.5 * k) for n in FORE[-3:]})
        out["head"] = out["head"] @ axis_angle(E_N, 22.0 * k)
        return out

    return keyed(c, [(0.0, {}, (0, 0, 0), (0, 0, 0), 0.0), (0.35, flare, (0, 0.06, -0.03), (0, 0, 0), 24.0),
                     (CAST_CONTACT, jab(1.0), (0, 0.04, 0.08), (0, 0, 0), -20.0),
                     (0.75, flare, (0, 0.06, 0.0), (0, 0, 0), 18.0),
                     (0.88, jab(1.0), (0, 0.04, 0.08), (0, 0, 0), -16.0),
                     (1.02, flare, (0, 0.06, 0.0), (0, 0, 0), 14.0),
                     (1.15, jab(0.8), (0, 0.04, 0.06), (0, 0, 0), -12.0),
                     (CAST_SEC, {}, (0, 0, 0), (0, 0, 0), 0.0)])


def build_hit() -> ck.Clip:
    """Struck: the body jolts back, the head snaps up and back, the panels twist, the tail is whipped; the peak at
    HIT_PEAK."""
    c = ck.Clip("hit", HIT_SEC)
    struck = compose({n: local_rot(bend=-2.5, twist=6.0, bone=n) for n in FORE},
                     {n: local_rot(bend=1.5, twist=-6.0, bone=n) for n in AFT})
    struck["head"] = local_rot(bend=-14.0, twist=6.0, bone="head")
    back = compose({n: local_rot(bend=0.8, twist=-4.0, bone=n) for n in SPINE_BONES})
    return keyed(c, [(0.0, {}, (0, 0, 0), (0, 0, 0), 0.0), (HIT_PEAK, struck, (0, 0.05, -0.04), (0, 0, 0), -24.0),
                     (0.28, back, (0, 0.0, 0.02), (0, 0, 0), 10.0), (HIT_SEC, {}, (0, 0, 0), (0, 0, 0), 0.0)])


def build_defend() -> ck.Clip:
    """The coil draws in tight round her middle, the head tucked down before the loop, held, then opens."""
    c = ck.Clip("defend", DEFEND_SEC)
    tight = chain_curl(5.0, -4.0, head=22.0)
    return keyed(c, [(0.0, {}, (0, 0, 0), (0, 0, 0), 0.0), (0.3, tight, (0, 0.04, -0.03), (0, 0, 0), 8.0),
                     (0.85, tight, (0, 0.04, -0.03), (0, 0, 0), -6.0), (DEFEND_SEC, {}, (0, 0, 0), (0, 0, 0), 0.0)])


def build_ko() -> ck.Clip:
    """The fall: the kite loses its wind. A flinch, then the string goes slack: the head droops, the loop sags, the
    panels luff loose, and she settles KO_DROP and holds (the stage tips her back and draws her under)."""
    c = ck.Clip("ko", KO_SEC)
    flinch = compose({n: local_rot(bend=-2.0, twist=10.0, bone=n) for n in FORE})
    flinch["head"] = local_rot(bend=-12.0, bone="head")
    slack = compose({n: local_rot(bend=2.0, twist=9.0 * (1 if CHAIN_POS[n] % 2 else -1), bone=n) for n in FORE},
                    {n: local_rot(bend=2.5, twist=-11.0 * (1 if CHAIN_POS[n] % 2 else -1), bone=n) for n in AFT})
    slack["head"] = local_rot(bend=34.0, twist=16.0, bone="head")
    return keyed(c, [(0.0, {}, (0, 0, 0), (0, 0, 0), 0.0), (0.2, flinch, (0, 0.04, -0.04), (0, 0, 0), -16.0),
                     (1.05, slack, (0, 0, 0), (0, -0.8 * KO_DROP, 0), 18.0),
                     (1.45, slack, (0, 0, 0), (0, -KO_DROP, 0), 26.0),
                     (KO_SEC, slack, (0, 0, 0), (0, -KO_DROP, 0), 26.0)])


def build_victory() -> ck.Clip:
    """She climbs as a kite climbs in a gust, head high, one long wave down the body, and settles."""
    c = ck.Clip("victory", VICTORY_SEC)
    high = chain_curl(-1.5, 1.0, head=-10.0)

    def gust(t: float) -> dict:
        return wave_pose(t, VICTORY_SEC, bend=1.2, twist=12.0, cycles=1.0, lag=0.7)

    return keyed(c, [(0.0, {}, (0, 0, 0), (0, 0, 0), 0.0, gust), (0.8, high, (0, 0.18, 0), (0, 0, 0), 20.0, gust),
                     (1.5, high, (0, 0.14, 0), (0, 0, 0), -16.0, gust), (VICTORY_SEC, {}, (0, 0, 0), (0, 0, 0), 0.0)])


FURLED = chain_curl(8.0, -8.0, head=28.0)  # furled: the coil wound tight, the head tucked (rise's start, dismiss's end)


def build_rise() -> ck.Clip:
    """The unfurling, in place (the stage lifts her out of the water): from furled tight, the coil opens, the head
    lifts and one wave runs down her length to rest."""
    c = ck.Clip("rise", RISE_SEC)

    def wave(t: float) -> dict:
        k = float(ck.smoothstep(0.9, 1.6, t) * (1.0 - ck.smoothstep(2.0, RISE_SEC, t)))
        return wave_pose(t, RISE_SEC, bend=1.5 * k, twist=14.0 * k, cycles=1.0, lag=0.6)

    return keyed(c, [(0.0, FURLED, (0, 0, 0), (0, 0, 0), 0.0, wave), (0.5, FURLED, (0, 0, 0), (0, 0, 0), 0.0, wave),
                     (1.5, chain_curl(-1.5, 1.0, head=-8.0), (0, 0.05, 0), (0, 0, 0), 22.0, wave),
                     (2.1, chain_curl(0.6, -0.4, head=3.0), (0, 0.0, 0), (0, 0, 0), -10.0, wave),
                     (RISE_SEC, {}, (0, 0, 0), (0, 0, 0), 0.0)])


def build_dismiss() -> ck.Clip:
    """The furling: the head lifts once, then the coil winds tight and the head bows and tucks; it ends furled (the
    stage sinks her)."""
    c = ck.Clip("dismiss", DISMISS_SEC)
    return keyed(c, [(0.0, {}, (0, 0, 0), (0, 0, 0), 0.0),
                     (0.35, chain_curl(-1.0, 0.8, head=-8.0), (0, 0.04, 0), (0, 0, 0), 12.0),
                     (0.8, FURLED, (0, 0, 0), (0, 0, 0), -6.0), (DISMISS_SEC, FURLED, (0, 0, 0), (0, 0, 0), 0.0)])


SPECIAL_ANGLE = 17.0  # Flare Line: the taut line rises this steeply toward the foes
SPECIAL_TAIL = np.array([0.0, 1.05, -0.4])  # and is anchored here, low behind her mark
RELEASE_LIFT = 0.15  # let go, she lifts a little as the line swings back into the coil


def world_dirs(pose: dict) -> dict[str, np.ndarray]:
    """Each spine bone's world direction in `pose` (local turns composed from the body out)."""
    G: dict[str, np.ndarray] = {"root": np.eye(3), "body": np.eye(3)}
    out = {}
    for b in RIG.bones:
        if b.name in ("root", "body"):
            continue
        G[b.name] = G[b.parent] @ pose.get(b.name, np.eye(3))
        out[b.name] = G[b.name] @ REST_DIR[b.name]
    return out


def slerp_dir(a: np.ndarray, b: np.ndarray, u: float) -> np.ndarray:
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    om = math.acos(max(-1.0, min(1.0, float(np.dot(a, b)))))
    if om < 1e-6:
        return b
    if abs(om - math.pi) < 1e-3:  # opposite: turn through the coil's plane
        mid = np.cross(a, E_N)
        mid /= np.linalg.norm(mid)
        return slerp_dir(a, mid, 2 * u) if u < 0.5 else slerp_dir(mid, b, 2 * u - 1)
    return (math.sin((1 - u) * om) * a + math.sin(u * om) * b) / math.sin(om)


def special_line() -> tuple[dict[str, np.ndarray], tuple]:
    """Flare Line's directions: every spine bone along one straight line rising toward the foes (+z), the tail end
    low behind her mark, and the body's offset that puts it there."""
    th = math.radians(SPECIAL_ANGLE)
    d = np.array([0.0, math.sin(th), math.cos(th)])
    dirs = {n: d for n in FORE + ["head"]}
    dirs.update({n: -d for n in AFT})
    aft_len = SPINE.length - STATIONS[BODY_K]
    body_at = SPECIAL_TAIL + d * aft_len
    loc = body_at - SPINE.at(STATIONS[BODY_K])
    return dirs, tuple(float(v) for v in loc)


def build_special() -> ck.Clip:
    """Flare Line: the coil winds in (a held breath), then the whole kite-string is pulled taut in one rising line
    toward the foes and burns end to end (the contact), holds, trembling, and is let go back into the coil. The
    pull and the release turn each bone's direction (not its Euler angles), so the line unrolls cleanly."""
    c = ck.Clip("special", SPECIAL_SEC)
    line, loc = special_line()
    wound = chain_curl(4.0, -3.0, head=12.0)
    wound_dirs = world_dirs(wound)
    rest_dirs = world_dirs({})
    pull0, pull1, let0 = 1.05, SPECIAL_CONTACT, 1.85
    frames = int(round(SPECIAL_SEC * ck.FPS))
    for f in range(frames + 1):
        t = f / ck.FPS
        if t <= 0.75:
            u = float(ck.smoothstep(0.0, 0.75, t))
            pose = blend_pose({}, wound, u)
            body, st = (0.0, 0.08 * u, 0.0), 18.0 * u
        elif t <= pull0:
            pose, body, st = wound, (0.0, 0.08, 0.0), 18.0
        elif t <= let0:
            u = float(ck.smoothstep(pull0, pull1, t))
            pose = directions_pose({n: slerp_dir(wound_dirs[n], line[n], u) for n in line})
            body = tuple(np.array([0.0, 0.08, 0.0]) * (1 - u) + np.asarray(loc) * u)
            st = 18.0 - 48.0 * u
        else:
            u = float(ck.smoothstep(let0, SPECIAL_SEC, t))
            pose = directions_pose({n: slerp_dir(line[n], rest_dirs[n], u) for n in line})
            body = tuple(np.asarray(loc) * (1 - u) + np.array([0.0, RELEASE_LIFT * math.sin(math.pi * u), 0.0]))
            st = -30.0 * (1 - u)
            if u > 0.98:
                pose = {}
        k = float(ck.smoothstep(pull1 - 0.05, pull1 + 0.1, t) * (1.0 - ck.smoothstep(let0 - 0.1, let0, t)))
        if k > 0.0:
            pose = compose(pose, {n: local_rot(twist=5.0 * k * math.sin(2.0 * math.pi * 7.0 * t + 0.8 * CHAIN_POS[n]),
                                               bone=n) for n in SPINE_BONES})
        pose_keys(c, t, pose, body=body, streamer=st)
    return c


def world_turn(c: ck.Clip, t: float, bone: str) -> np.ndarray:
    """The world rotation of `bone` at t in clip c (its parents' turns and its own, composed)."""
    G = np.eye(3)
    chain = []
    b: str | None = bone
    while b is not None:
        chain.append(b)
        b = PARENT[b]
    for name in reversed(chain):
        G = G @ ck.euler(*c.sample(name, t)[0])
    return G


def hang_key(c: ck.Clip) -> ck.Clip:
    """Keys the key so it hangs: its local turn undoes KEY_HANG of its parent's (the head's) world turn, KEY_LAG
    behind."""
    frames = max(int(round(c.length * ck.FPS)), 1)
    for f in range(frames + 1):
        t = min(f / ck.FPS, c.length)
        s = t - KEY_LAG
        s = s % c.length if c.loop else max(s, 0.0)
        G = world_turn(c, s, "head")
        ang = math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(G) - 1.0) / 2.0))))
        if ang < 1e-6:
            c.key("key", t, (0, 0, 0))
            continue
        ax = np.array([G[2, 1] - G[1, 2], G[0, 2] - G[2, 0], G[1, 0] - G[0, 1]])
        R = axis_angle(ax, -KEY_HANG * ang) if np.linalg.norm(ax) > 1e-9 else np.eye(3)
        c.key("key", t, to_euler(R))
    return c


RELEASE_SEC = 3.4  # M3-CRE-647: the held form's release (Ch20), its KO
RELEASE_ANGLE = 38.0  # the release's line climbs this steeply, away from the party (-z)
RELEASE_TAIL = np.array([0.0, 0.7, 1.4])  # the line's tail end as it opens, low in front of her mark
RELEASE_AWAY = np.array([0.0, 1.5, -0.6])  # and where the lift then carries her (metres: up, and back)


def build_release() -> ck.Clip:
    """M3-CRE-647, the held form's KO (vowbound.md, the final fight: giddy and proud). The kite's last flight: the coil
    draws in once, then unrolls into one long line climbing away from the party, a kite on a fresh wind, and holds
    there, the panels luffing and the streamers flying; then the line lifts, up and back, still taut and easy. Her
    string is let go, not cut: it ends flying, not fallen. Like Flare Line, it turns each bone's direction."""
    c = ck.Clip("release", RELEASE_SEC)
    th = math.radians(RELEASE_ANGLE)
    d = np.array([0.0, math.sin(th), -math.cos(th)])
    line = {n: d for n in FORE + ["head"]}
    line.update({n: -d for n in AFT})
    loc = RELEASE_TAIL + d * (SPINE.length - STATIONS[BODY_K]) - SPINE.at(STATIONS[BODY_K])
    gather = chain_curl(2.5, -2.0, head=-8.0)
    gather_dirs = world_dirs(gather)
    open0, open1, lift0 = 0.55, 1.45, 2.0
    frames = int(round(RELEASE_SEC * ck.FPS))
    for f in range(frames + 1):
        t = f / ck.FPS
        if t <= open0:
            u = float(ck.smoothstep(0.0, open0, t))
            pose, body, st = blend_pose({}, gather, u), (0.0, 0.06 * u, 0.0), 14.0 * u
        else:
            u = float(ck.smoothstep(open0, open1, t))
            pose = directions_pose({n: slerp_dir(gather_dirs[n], line[n], u) for n in line})
            body = tuple(np.array([0.0, 0.06, 0.0]) * (1 - u) + loc * u)
            st = 14.0 - 34.0 * u
        k = float(ck.smoothstep(open1 - 0.2, open1 + 0.2, t))  # the luff on the wind, down the line
        if k > 0.0:
            pose = compose(pose, {n: local_rot(twist=4.0 * k * math.sin(2.0 * math.pi * 1.2 * t - 0.6 * CHAIN_POS[n]),
                                               bone=n) for n in SPINE_BONES})
            st += 12.0 * k * math.sin(2.0 * math.pi * 1.5 * t)
        root = RELEASE_AWAY * float(ck.smoothstep(lift0, RELEASE_SEC, t))
        pose_keys(c, t, pose, body=body, root=tuple(float(v) for v in root), streamer=st)
    return c


def build_clips() -> list[ck.Clip]:
    clips = [build_idle(), build_ready(), build_attack(), build_cast(), build_hit(), build_defend(), build_ko(),
             build_victory(), build_rise(), build_dismiss(), build_special(), build_release()]
    return [hang_key(c) for c in clips]


# ---------------------------------------------------------------------------------------------
# A numpy check (no Blender)
# ---------------------------------------------------------------------------------------------
def report(rig: ck.Rig, mesh: ck.Mesh, clips: list[ck.Clip]) -> None:
    rest = mesh.arrays()["pos"]
    print(f"triangles: {mesh.triangle_count}; vertices {mesh.count}; bones {len(rig.bones)}; "
          f"body length {SPINE.length:.2f} m + head {HEAD_LEN:.2f} m; spans {N_SPANS}")
    print("parts: " + ", ".join(f"{k} {v}" for k, v in PARTS.items()))
    print(f"rest bounds: min {np.round(rest.min(axis=0), 3)}, max {np.round(rest.max(axis=0), 3)}")
    poser = grounding.Poser(rig, mesh)
    for c in ck.with_variety(clips):
        lows = grounding.lowest(poser, c)
        highs, disp, zmin, zmax = [], [], [], []
        for t in grounding.frame_times(c):
            P = poser.vertices(poser.matrices(grounding.pose_at(c, poser.names, t)))
            highs.append(float(P[:, 1].max()))
            zmin.append(float(P[:, 2].min()))
            zmax.append(float(P[:, 2].max()))
            disp.append(float(np.linalg.norm(P - rest, axis=1).mean()))
        print(f"{c.name:8s} {c.length:.2f}s: y {min(lows):+.3f}..{max(highs):.3f}; z {min(zmin):+.2f}..{max(zmax):.2f}; "
              f"peak {int(np.argmax(disp)) / ck.FPS:.2f}s")


def build() -> tuple[ck.Rig, ck.Mesh, list[ck.Clip]]:
    return RIG, build_mesh(RIG), build_clips()


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
    info = ck.export_creature(mesh, rig, clips, args.out, extras={"hymn_creature": "virel"})
    print(f"virel: {info}")


if __name__ == "__main__":
    main()
