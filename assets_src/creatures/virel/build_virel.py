"""Virel, the Kite-Serpent, Asha's Fire Vowbound (M3-CRE-641; final pass M3-CRB-008):
docs/kb/art/creatures/vowbound/virel.md.

blender --background --factory-startup --threads 4 --python \
    assets_src/creatures/virel/build_virel.py -- --out assets/creatures/virel/virel.glb

A long ribbon-serpent of sailcloth, like a Saltwright signal kite flown alight as a flare and held still. **Final
pass (M3-CRB-008):** she flies in one open S, never a closed loop: the head raised and leading toward the foes, the
neck bowed back, the body swung forward under it, and the tail streaming out behind and away, trailing two ribbons
and a kite-tail of cloth bows with a tassel. Her body is a run of sailcloth panels, each its own length and cut (a
scalloped upper hem with burnt bites, a pointed flap at the trailing corner of the lower hem), bellied between cane
battens on a spine spar of bamboo with lashings at every crossing, bound round the edge with a hem tape, eyeleted
with brass grommets, weathered, stained and patched (the Saltwright mend). **Fire along every seam:** each cross-seam
is a raised felled seam with a burning core between charred lips, and the hem tapes' stitching smoulders; the cloth
is scorched brown to black for a hand's width either side. The fire is bound light (`glimmer_bound`, steady): the
palette and the chapter beats give her form no warm light, so the warmth is the scorch (see the design sheet).

The head is built like a kite-dragon's: two cheek panels on a cane skull ridge (a wedge, not a cut-out), a cane
brow over a lantern-eye of bound light on each side, a lower jaw panel hung open on its own cane with the light
inside the mouth, cord whiskers with tassels, and the bowed crest-spar swept back with a cloth vane under it. A
bridle of three lines meets under the throat; from its knot hangs the keepsake, a brass tuning key big enough to
read, on its own cord.

**Built hovering**, like Ilun: the origin is the water point under her mark, so the stand-in needs no `hover`.
Every clip stays above the water.

Rig (18 bones): `root`, `body` (the forward swing of the S, mid-body), `fore_0..4` (body to neck), `head`,
`aft_0..5` (body to tail), `streamer`, `key`, and two unweighted VFX anchors: `vfx_core` (on `body`, the ribbon's
middle there) and `vfx_keepsake` (on `key`, the key's bow). Each spine bone owns a stretch of the ribbon by arc
length, not by distance, because the S passes close to itself.

`python3 build_virel.py --report` prints the triangle count, per-part counts and per-clip lows (numpy, no export).
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
    "brass": "#B08D57", "deep_teal_shadow": "#0E4A55", "lacquer_black": "#1D1916", "tortoiseshell": "#6B3A1E",
    "thatch": "#B08A52", "sand_wet": "#B59D74", "salt_glass": "#BFE6E0", "bronze_patina": "#5F8A78",
    "sand_dry": "#EFDDB4", "sea_blue_cloth": "#3C78A8", "indigo_dye": "#2B3A6B",
}.items()}

# ---- the S (metres; Godot axes, facing +z) -------------------------------------------------------------
PLANE_YAW = 22.0  # the S's plane, turned off the battle axis toward the summon camera
_PY = math.radians(PLANE_YAW)
E_A = np.array([math.sin(_PY), 0.0, math.cos(_PY)])  # in-plane "forward"
E_N = np.array([math.cos(_PY), 0.0, -math.sin(_PY)])  # the plane's normal: the sails face it
# The spine's control points (a: forward in the plane, y: up, c: depth along E_N), nose first. The head leads,
# raised; the neck bows back (the S's upper bowl), the body swings forward under it (the lower bowl), and the tail
# streams back low and away from the cameras, rising a little at the end.
CTRL = [
    (3.08, 2.36, 0.00), (2.76, 2.52, 0.00), (2.42, 2.56, 0.00),  # the nose, the brow, the back of the head
    (2.14, 2.42, 0.04), (1.98, 2.06, 0.12), (1.84, 1.62, 0.22), (1.62, 1.30, 0.30), (1.30, 1.18, 0.32),
    (0.98, 1.30, 0.26), (0.76, 1.62, 0.14), (0.56, 1.98, 0.02), (0.32, 2.14, -0.08), (0.06, 2.06, -0.18),
    (-0.16, 1.84, -0.30), (-0.32, 1.60, -0.42), (-0.46, 1.46, -0.56), (-0.58, 1.40, -0.72),
]
A_SHIFT = 0.14  # the whole figure, forward of her mark: the tail keeps clear of the default camera's right edge
HEAD_BACK = 2  # the control point at the back of the head (s = 0)
BODY_K = 5  # the body bone's station: the forward swing of the S (fore_0..4 run from it to the head)

# ---- the sails ---------------------------------------------------------------------------------------
W_NECK, W_MID, W_TAIL = 0.34, 0.38, 0.12  # full width at the neck, mid-body and the tail end
HEAD_LEN_M = 0.74
SKIN = 0.004  # half the sailcloth's thickness
NU = 9  # vertices along a panel
NV = 9  # vertices across
PANEL_MIN, PANEL_MAX = 0.3, 0.44  # panel lengths (shorter toward the tail)
BILLOW = 0.045  # each panel bellies out by this fraction of its width
TAPE_W = 0.022  # the hem tape's width on each face
SEAM_HALF = 0.024  # the felled cross-seams' half width (lips to lips)
SPINE_R = 0.011
BATTEN_R = 0.0075
SPAR_OFF = 0.014  # the frame is lashed on the sail's outer face (the cameras' side); the cloth bellies behind it
BATTEN_OVER = 0.018  # battens stand out past the hems
GROMMET_R = 0.014

# ---- the bridle and the key ------------------------------------------------------------------------
BRIDLE_DROP = 0.26  # the bridle knot under the jaw
CORD_R = 0.0045
KEY_CORD = 0.07
KEY_LEN, KEY_BOW_R = 0.25, 0.058  # the shaft and socket below the bow; the bow's ring radius
STREAMER_LEN = 0.7
STREAMER_DROOP = 1.5  # the tail hangs down and back from the tail end (downwind of a flown kite)

PARTS: dict[str, int] = {}


def count(name: str, mesh: ck.Mesh, before: int) -> None:
    PARTS[name] = PARTS.get(name, 0) + mesh.triangle_count - before


def plane(a, y, c) -> np.ndarray:
    a, y, c = (np.asarray(v, dtype=np.float64) for v in (a, y, c))
    return (a[..., None] + A_SHIFT) * E_A + y[..., None] * np.array([0.0, 1.0, 0.0]) + c[..., None] * E_N


def rng_for(tag: int) -> np.random.Generator:
    return np.random.default_rng(SEED + tag)


# ---------------------------------------------------------------------------------------------
# The spine: a curve from the nose (s = -HEAD_LEN) through the back of the head (s = 0) to the tail end
# ---------------------------------------------------------------------------------------------
def _raw_curve() -> np.ndarray:
    P = np.array([plane(*p) for p in CTRL])
    P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    for i in range(1, len(P) - 2):  # a Catmull-Rom through the points, sampled densely
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0.0, 1.0, 32, endpoint=False):
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
        back = plane(*CTRL[HEAD_BACK])
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
        """(tangent, width, normal) at s; the width lies in the S's plane, turned `twist` degrees about the tangent;
        the normal is the sail's outer face (toward +E_N at rest). +width is the belly hem."""
        t = self.tangent(s)
        w = np.cross(t, E_N)
        w /= np.linalg.norm(w, axis=-1, keepdims=True)
        n = np.cross(w, t)
        tw = np.radians(np.asarray(twist, dtype=np.float64))[..., None]
        w2 = w * np.cos(tw) + n * np.sin(tw)
        n2 = np.cross(w2, t)
        return t, w2, n2


SPINE = Spine()
HEAD_LEN = -SPINE.s_min  # the head, from the back of the head (s = 0) to the nose
N_SPANS = 11  # the spine bones: fore_0..4 and aft_0..5
STATION = SPINE.length / N_SPANS  # spine bone length (arc length per span)
STATIONS = np.linspace(0.0, SPINE.length, N_SPANS + 1)
FORE = [f"fore_{j}" for j in range(BODY_K)]  # fore_j: station BODY_K - j to BODY_K - j - 1
AFT = [f"aft_{j}" for j in range(N_SPANS - BODY_K)]  # aft_j: station BODY_K + j to BODY_K + j + 1


def width_at(s) -> np.ndarray:
    """The ribbon's full width at s (the body; the head has its own build)."""
    s = np.asarray(s, dtype=np.float64)
    u = np.clip(s / SPINE.length, 0.0, 1.0)
    w = np.where(u < 0.35, W_NECK + (W_MID - W_NECK) * ck.smoothstep(0.0, 0.35, u),
                 W_MID + (W_TAIL - W_MID) * ck.smoothstep(0.38, 1.0, u) ** 0.9)
    return w


def twist_at(s) -> np.ndarray:
    """A rest twist along the ribbon, so the sails are not all in one plane: gentle through the S, rolling more as
    the tail streams away (it keeps a face to the cameras as it turns into depth)."""
    s = np.asarray(s, dtype=np.float64)
    return 12.0 * np.sin(s * 1.1 + 0.3) + 14.0 * ck.smoothstep(SPINE.length - 1.6, SPINE.length, s)


# ---------------------------------------------------------------------------------------------
# The panels: each its own length and cut
# ---------------------------------------------------------------------------------------------
def _layout() -> tuple[np.ndarray, np.ndarray, list[dict]]:
    rng = rng_for(1)
    seams = [0.0]
    while True:
        u = seams[-1] / SPINE.length
        ln = rng.uniform(PANEL_MIN, PANEL_MAX) * (1.0 - 0.3 * u)
        if seams[-1] + ln > SPINE.length - 0.18:
            break
        seams.append(seams[-1] + ln)
    seams.append(SPINE.length)
    panels = []
    tones = ["sand_cloth", "tan", "sand_dry", "sand_wet", "tan", "thatch", "sand_cloth"]
    for k in range(len(seams) - 1):
        p = {
            "tone": tones[int(rng.integers(0, len(tones)))],
            "tone_mix": float(rng.uniform(0.3, 0.7)),
            "scallop": float(rng.uniform(-0.06, 0.08)),  # < 0: a kite cell bowed out
            "flap": float(rng.uniform(0.06, 0.13)) if k < len(seams) - 2 else 0.0,
            "flap_at": float(rng.uniform(0.72, 0.86)),
            "bite": (float(rng.uniform(0.15, 0.85)), float(rng.uniform(0.04, 0.09))) if rng.random() < 0.55
            else None,
            "patch": None,
            "stain": int(rng.integers(0, 1000)),  # (drawn to keep the layout's stream; the stains are fbm)
        }
        if rng.random() < 0.4:  # a Saltwright mend: a rectangle of other cloth, sewn on
            u0 = float(rng.uniform(0.12, 0.3))
            v0 = float(rng.uniform(-0.8, -0.1))
            p["patch"] = (u0, u0 + float(rng.uniform(0.38, 0.58)), v0, v0 + float(rng.uniform(0.6, 0.95)),
                          ["faded_teal_cloth", "faded_teal_cloth", "sea_blue_cloth", "gauze_white"][
                              int(rng.integers(0, 4))])
        panels.append(p)
    # each cross-seam is cut on the bias at its own angle (the first, at the head, and the tail's end square), so
    # the panels are trapezoids and rhombs of different shapes, not a run of boxes
    slopes = [0.0]
    for k in range(1, len(seams) - 1):
        half = 0.5 * float(width_at(seams[k]))
        room = 0.55 * min(seams[k] - seams[k - 1], seams[k + 1] - seams[k]) / half
        lo, hi = slopes[-1] - room, slopes[-1] + room
        sl = float(rng.uniform(0.35, 0.8)) * (1.0 if rng.random() < 0.5 else -1.0)
        slopes.append(float(np.clip(sl, max(lo, -0.85), min(hi, 0.85))))
    slopes.append(0.0)
    slopes = np.array(slopes)
    if abs(slopes[-2]) * 0.5 * float(width_at(seams[-2])) > 0.55 * (seams[-1] - seams[-2]):
        slopes[-2] = 0.0
    return np.array(seams), slopes, panels


SEAMS, SLOPES, PANELS = _layout()
U_SAMPLES = np.array([0.0, 0.1, 0.22, 0.36, 0.5, 0.64, 0.76, 0.86, 0.94])  # along a panel (dense at the flap)


def seam_line(k, v) -> np.ndarray:
    """The arc length of cross-seam k at the across-fraction v (each seam cut on the bias)."""
    k = np.asarray(k, dtype=np.int64)
    return SEAMS[k] + SLOPES[k] * np.asarray(v, dtype=np.float64) * 0.5 * width_at(SEAMS[k])


def s_of(k, u, v) -> np.ndarray:
    """The arc length of the point u (0 .. 1) of the way across panel k from its seam to the next, at v."""
    a = seam_line(k, v)
    return a + np.asarray(u, dtype=np.float64) * (seam_line(np.asarray(k) + 1, v) - a)


def panel_at(s, v) -> tuple[np.ndarray, np.ndarray]:
    """(u, k): the panel a point (s, v) lies in and how far across it, between its two bias-cut seams."""
    s = np.asarray(s, dtype=np.float64)
    v = np.broadcast_to(np.asarray(v, dtype=np.float64), s.shape)
    sf, vf = s.ravel(), v.ravel()
    L = SEAMS[:, None] + SLOPES[:, None] * vf[None] * 0.5 * width_at(SEAMS)[:, None]
    k = np.clip(np.sum(L <= sf[None] + 1e-12, axis=0) - 1, 0, len(SEAMS) - 2)
    i = np.arange(len(sf))
    a, b = L[k, i], L[k + 1, i]
    u = np.clip((sf - a) / np.maximum(b - a, 1e-9), 0.0, 1.0)
    return u.reshape(s.shape), k.reshape(s.shape)


def panel_span(k, v) -> np.ndarray:
    """Panel k's length (m) along the ribbon at v."""
    return seam_line(np.asarray(k) + 1, v) - seam_line(k, v)


def outline(s, v) -> np.ndarray:
    """The across-fraction v (-1 upper hem .. +1 belly hem) scaled to the panel's cut: the upper hem scalloped and
    bitten (burnt), the belly hem scalloped and drawn out to a pointed flap at its trailing corner."""
    s = np.asarray(s, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    u, k = panel_at(s, v)
    sc = np.array([PANELS[i]["scallop"] for i in np.atleast_1d(k).ravel()]).reshape(np.shape(k))
    fl = np.array([PANELS[i]["flap"] for i in np.atleast_1d(k).ravel()]).reshape(np.shape(k))
    fa = np.array([PANELS[i]["flap_at"] for i in np.atleast_1d(k).ravel()]).reshape(np.shape(k))
    base = 1.0 - sc * np.sin(math.pi * u)
    flap = fl * ck.smoothstep(0.15, fa, u) * (1.0 - ck.smoothstep(fa, 1.0, u)) ** 1.5 / np.maximum(
        width_at(s) * 0.5, 0.05)
    bite = np.zeros_like(u)
    for i, p in enumerate(PANELS):
        if p["bite"] is None:
            continue
        bu, bd = p["bite"]
        bite = bite + (k == i) * bd * np.exp(-((u - bu) / 0.09) ** 2)
    up = base * (1.0 - bite)
    down = base + flap
    return np.where(v < 0.0, v * up, v * down)


def ribbon_point(s, v, bulge=0.0, side=0.0) -> np.ndarray:
    """A point on the sail at arc length s and outline fraction v, pushed `bulge` along the normal and `side` (the
    cloth's half thickness, signed) further."""
    s = np.asarray(s, dtype=np.float64)
    _, w, n = SPINE.frame(s, twist_at(s))
    half = 0.5 * width_at(s)
    return SPINE.at(s) + w * (np.asarray(v)[..., None] * half[..., None]) + n * (np.asarray(bulge) + side)[..., None]


def billow(s, v) -> np.ndarray:
    """The cloth bellies behind the frame between battens, with soft tension wrinkles from the batten ends."""
    s = np.asarray(s, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    u, k = panel_at(s, v)
    wd = width_at(s)
    belly = -BILLOW * wd * np.sin(math.pi * u) * np.cos(0.5 * math.pi * np.clip(v, -1, 1))
    # the batten at mid-panel holds the cloth to the frame: a shallow trough along it
    belly = belly * (0.55 + 0.45 * ck.smoothstep(0.0, 0.22, np.abs(u - 0.5)))
    wr = 0.0035 * np.sin(2.0 * math.pi * (2.2 * u + 1.6 * np.abs(v)) + k * 1.7) * np.sin(math.pi * u) \
        * ck.smoothstep(0.15, 0.7, np.abs(v))
    return belly - wr


# ---------------------------------------------------------------------------------------------
# Rig
# ---------------------------------------------------------------------------------------------
def head_frame() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """The head's local frame: origin at the back of the head, f toward the nose, u up, z toward the cameras."""
    o = SPINE.at(0.0)
    nose = SPINE.at(-HEAD_LEN)
    f = nose - o
    f /= np.linalg.norm(f)
    z = E_N - np.dot(E_N, f) * f
    z /= np.linalg.norm(z)
    u = np.cross(f, z)
    return o, f, u, z


def head_pt(x, y, z) -> np.ndarray:
    o, f, u, zz = head_frame()
    x, y, z = (np.asarray(v, dtype=np.float64) for v in (x, y, z))
    return o + x[..., None] * f + y[..., None] * u + z[..., None] * zz


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
    core = SPINE.at(STATIONS[BODY_K])
    rig.add("vfx_core", core, core + (0, 0.2, 0), "body")
    kc = key_bow_centre()
    rig.add("vfx_keepsake", kc, kc - (0, 0.15, 0), "key")
    return rig


def streamer_dir() -> np.ndarray:
    t = SPINE.tangent(SPINE.length)
    t = t - 0.7 * np.dot(t, E_N) * E_N  # the tail hangs back and down, not off into the distance
    d = t + np.array([0.0, -STREAMER_DROOP, 0.0])
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
    return J, W


def fixed(J, W):
    return lambda P: (J, W)


def s_of_head(P: np.ndarray) -> np.ndarray:
    """A head-part vertex's arc length (its distance forward of the back of the head, negated), so the head's rear
    blends into the neck as the ribbon does."""
    o, f, _, _ = head_frame()
    return np.minimum(-((P - o) @ f), 0.0)


# ---------------------------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------------------------
TAN = ck.mix(PAL["sand_cloth"], PAL["tortoiseshell"], 0.42)  # tanned sailcloth (bark-tanned, as old sails are)


def scorch_color(base: np.ndarray, char: np.ndarray) -> np.ndarray:
    """Cloth scorched by the seam fire: toasted to tortoiseshell, then to char at the seam."""
    c = ck.mix(base, PAL["tortoiseshell"], (ck.smoothstep(0.0, 0.55, char) * 0.85)[:, None])
    return ck.mix(c, PAL["lacquer_black"], (ck.smoothstep(0.5, 1.0, char) * 0.9)[:, None])


def two_faced(P_front: np.ndarray, P_back: np.ndarray, T: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """A front sheet and its back sheet (wound the other way), as one vertex list."""
    return np.vstack([P_front, P_back]), np.vstack([T, ck.flip(T) + len(P_front)])


def winding_out(P: np.ndarray, T: np.ndarray, out: np.ndarray) -> np.ndarray:
    """T wound so its faces point along `out` (a direction, or one per vertex) on average."""
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    o = np.broadcast_to(np.asarray(out, dtype=np.float64), P.shape)
    d = np.einsum("ij,ij->i", fn, o[T[:, 0]])
    return T if d.sum() >= 0.0 else ck.flip(T)


# ---------------------------------------------------------------------------------------------
# Mesh: the body's sail
# ---------------------------------------------------------------------------------------------
def body_samples(v: float = 0.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Arc lengths along the line at across-fraction v, panel by panel (u, the panel's k), to the tail's end."""
    ks = np.concatenate([np.repeat(np.arange(len(SEAMS) - 1), len(U_SAMPLES)), [len(SEAMS) - 2]])
    us = np.concatenate([np.tile(U_SAMPLES, len(SEAMS) - 1), [1.0]])
    s = s_of(ks, us, np.full(len(ks), v))
    s[0] = max(s[0], 0.003)
    return s, us, ks


def sail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The panels as one cloth slab (front and back faces and a thin rim), coloured panel by panel."""
    before = mesh.triangle_count
    _, u_row, k_row = body_samples()
    v = np.linspace(-1.0, 1.0, NV)
    U, V = np.meshgrid(u_row, v, indexing="ij")
    pk = np.repeat(k_row[:, None], NV, axis=1)
    S = s_of(pk, U, V)
    S[0] = np.maximum(S[0], 0.003)
    u = U
    Vo = outline(S, V)
    bul = billow(S, V)
    rows, cols = S.shape
    faces = []
    for side in (1.0, -1.0):
        P = ribbon_point(S, Vo, bul, side * SKIN).reshape(-1, 3)
        T = ck.grid_tris(rows, cols, False)
        faces.append((P, ck.flip(T) if side > 0 else T))  # grid_tris winds toward -n: the front face is flipped
    P = np.vstack([faces[0][0], faces[1][0]])
    T = np.vstack([faces[0][1], faces[1][1] + rows * cols])
    rim = []
    off = rows * cols
    for r in range(rows - 1):
        for c in (0, cols - 1):
            a, b = r * cols + c, (r + 1) * cols + c
            q = [(a, b, b + off), (a, b + off, a + off)]
            rim += q if c == 0 else [x[::-1] for x in q]
    T = np.vstack([T, np.asarray(rim, dtype=np.int64)])
    s_all = np.tile(S.reshape(-1), 2)
    u_all = np.tile(u.reshape(-1), 2)
    v_all = np.tile(V.reshape(-1), 2)
    k_all = np.tile(pk.reshape(-1), 2)
    col, glow, cav = cloth_colour(P, s_all, u_all, v_all, k_all)
    J, W = skin_s(rig, s_all)
    uv = np.column_stack([s_all * 0.6, v_all * 0.5 * width_at(s_all) * 0.6])
    ck.finish(mesh, P, T, "sail", col, fixed(J, W), cavity=cav, emission=glow, uv=uv)
    count("sail", mesh, before)


def mends(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The Saltwright mends: a rectangle of other cloth (faded teal, sea blue or new white) sewn over a worn place
    on the outer face, its stitched border darker, its corners a little lifted."""
    before = mesh.triangle_count
    for k, p in enumerate(PANELS):
        pt = p["patch"]
        if pt is None:
            continue
        a = np.linspace(0.0, 1.0, 5)
        A, B = np.meshgrid(a, a, indexing="ij")
        U = pt[0] + (pt[1] - pt[0]) * A
        V = pt[2] + (pt[3] - pt[2]) * B
        S = s_of(np.full(U.shape, k), U, V)
        edge = np.minimum(np.minimum(A, 1 - A), np.minimum(B, 1 - B))
        lift = 0.0028 + 0.002 * (edge < 0.01) * ((A < 0.01) | (A > 0.99)) * ((B < 0.01) | (B > 0.99))
        P = ribbon_point(S, outline(S, V), billow(S, V), SKIN + lift).reshape(-1, 3)
        _, _, n = SPINE.frame(S.reshape(-1), twist_at(S.reshape(-1)))
        T = winding_out(P, ck.grid_tris(5, 5, False), n)
        tone = PAL[pt[4]]
        c = ck.mix(tone, PAL["sand_cloth"], 0.3 if pt[4] != "gauze_white" else 0.45)
        c = c * (1.0 + 0.06 * ck.fbm(P * 6.0, SEED + 50 + k))[:, None]
        border = ck.smoothstep(0.2, 0.0, edge.reshape(-1))
        c = ck.mix(c, PAL["timber_weathered"], (0.5 * border)[:, None])
        J, W = skin_s(rig, S.reshape(-1))
        ck.finish(mesh, P, T, "sail", np.clip(c, PAL["lacquer_black"], PAL["gauze_white"]), fixed(J, W),
                  cavity=0.4 * border)
    count("mends", mesh, before)


def cloth_colour(P, s, u, v, k):
    """Sailcloth: each panel its own bolt (sand, bark-tanned, paler or darker, a little thatch-yellow), sun-faded
    along the upper hem, grimed toward the belly, tide-line stains (the mends are their own cloth: mends());
    scorched for a hand's width either side of every seam and charred at it; the cloth by the seams lit faintly
    through from the fire."""
    n = len(P)
    base = np.zeros((n, 3))
    for i, p in enumerate(PANELS):
        m = k == i
        tone = TAN if p["tone"] == "tan" else PAL[p["tone"]]
        base[m] = ck.mix(PAL["sand_cloth"], tone, p["tone_mix"])
    mott = ck.fbm(P * 4.0, SEED)
    base = base * (1.0 + 0.07 * mott)[:, None]
    base = ck.mix(base, PAL["sand_dry"], (0.25 * ck.smoothstep(-0.3, -1.0, v))[:, None])  # sun-faded upper hem
    base = ck.mix(base, PAL["sand_wet"], (0.35 * ck.smoothstep(0.2, 1.0, v))[:, None])  # grime toward the belly
    st = ck.fbm(P * 2.3 + 11.0, SEED + 5)
    ring = ck.smoothstep(0.05, 0.0, np.abs(st - 0.12)) * 0.5 + ck.smoothstep(0.12, 0.3, st) * 0.18
    base = ck.mix(base, PAL["timber_weathered"], ring[:, None])  # water stains with a tide line
    # scorch: distance (m) to the nearest cross-seam and to the hem
    seg = panel_span(k, v)
    d_seam = np.minimum(u, 1.0 - u) * seg
    d_seam = np.where(s < 0.02, s, d_seam)
    half = 0.5 * width_at(s)
    d_hem = (1.0 - np.abs(v)) * half
    rag = 0.018 * ck.fbm(P * 9.0, SEED + 9)
    char = np.maximum(ck.smoothstep(0.095, 0.0, d_seam + rag), 0.55 * ck.smoothstep(0.04, 0.0, d_hem + 0.6 * rag))
    col = scorch_color(base, char)
    col = np.clip(col, PAL["lacquer_black"], PAL["gauze_white"])
    glow = 0.12 * ck.smoothstep(0.8, 1.0, char)
    cav = 0.35 * ck.smoothstep(0.5, 1.0, char)
    return col, glow, cav


def seams(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Fire along every cross-seam: a raised felled seam with a thin burning core, an ember-lit ring of charred cloth
    either side of it and black lips beyond, on both faces. The core's width and heat wander along the seam (beads
    of ember and dimmer stretches), held still: bound light, no flicker."""
    before = mesh.triangle_count
    Ps, Ts, ss, cols, ems, cavs = [], [], [], [], [], []
    base = 0
    for si in range(len(SEAMS) - 2):
        for side in (1.0, -1.0):
            # the outer face (the cameras') in full: lips, ember ring and core; the back face plainer
            if side > 0:
                offs = np.array([-1.0, -0.42, -0.1, 0.1, 0.42, 1.0])
                lift = np.array([0.0010, 0.0022, 0.0028, 0.0028, 0.0022, 0.0010])
                v = np.linspace(-1.0, 1.0, 11)
            else:
                offs = np.array([-1.0, 0.0, 1.0])
                lift = np.array([0.0010, 0.0024, 0.0010])
                v = np.linspace(-1.0, 1.0, 7)
            sl = seam_line(np.full(len(v), si + 1), v)  # the seam, cut on the bias
            p0 = ribbon_point(sl, outline(sl, v))
            hot = ck.smoothstep(-0.3, 0.35, ck.fbm(p0 * 7.0, SEED + 40 + si))
            rows = []
            for j, o in enumerate(offs):
                ds = o * SEAM_HALF * ((0.6 + 0.8 * hot) if abs(o) < 0.2 else 1.0)
                sv = sl + ds
                rows.append(ribbon_point(sv, outline(sl, v), billow(sv, v), side * (SKIN + lift[j])))
            P = np.vstack(rows)
            T = ck.grid_tris(len(offs), len(v), False)
            _, _, n = SPINE.frame(np.tile(sl, len(offs)), twist_at(np.tile(sl, len(offs))))
            T = winding_out(P, T, n * side)
            Ps.append(P)
            Ts.append(T + base)
            ss.append(np.tile(sl, len(offs)))
            ring = np.abs(offs)
            core = np.repeat(ring < 0.2, len(v)) if side > 0 else np.repeat(ring < 0.5, len(v))
            ember = np.repeat((ring > 0.2) & (ring < 0.6), len(v))
            h = np.tile(hot, len(offs))
            c = np.where(core[:, None], ck.mix(PAL["deep_teal_shadow"], PAL["salt_glass"], (0.35 + 0.5 * h)[:, None]),
                         np.where(ember[:, None], ck.mix(PAL["tortoiseshell"], PAL["lacquer_black"], 0.45),
                                  PAL["lacquer_black"]))
            cols.append(c)
            ems.append(np.where(core, 0.32 + 0.68 * h, np.where(ember, 0.06 + 0.16 * h, 0.0)))
            cavs.append(np.where(core, 0.0, 0.5))
            base += len(P)
    P = np.vstack(Ps)
    T = np.vstack(Ts)
    J, W = skin_s(rig, np.concatenate(ss))
    ck.finish(mesh, P, T, "seam", np.vstack(cols), fixed(J, W), emission=np.concatenate(ems),
              cavity=np.concatenate(cavs))
    count("seams", mesh, before)


def hem_tapes(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Both hems bound with a folded tape (darker cloth, scorched where it crosses a seam); its stitching smoulders
    in patches."""
    before = mesh.triangle_count
    sec = [(1.0, 1.0, 0.0018), (0.0, -0.1, 0.0), (-1.0, 1.0, 0.0018)]
    Ps, Ts, ss, cols, ems = [], [], [], [], []
    base = 0
    for hem in (-1.0, 1.0):
        s, _, _ = body_samples(hem)
        half = 0.5 * width_at(s)
        rows = []
        for face, inset, lift in sec:
            vo = outline(s, np.full(len(s), hem))
            vin = vo - hem * inset * TAPE_W / half
            side = face * (SKIN + lift) if face != 0.0 else 0.0
            rows.append(ribbon_point(s, vin, billow(s, np.full(len(s), hem)), side))
        P = np.vstack(rows)
        T = ck.grid_tris(len(sec), len(s), False)
        _, w, _ = SPINE.frame(np.tile(s, len(sec)), twist_at(np.tile(s, len(sec))))
        T = winding_out(P, T, w * hem)
        Ps.append(P)
        Ts.append(T + base)
        s_all = np.tile(s, len(sec))
        ss.append(s_all)
        u, k = panel_at(s_all, hem)
        d_seam = np.minimum(u, 1.0 - u) * panel_span(k, hem)
        char = ck.smoothstep(0.06, 0.0, d_seam + 0.012 * ck.fbm(P * 9.0, SEED + 21))
        tape = ck.mix(PAL["sand_wet"], PAL["timber_weathered"], (0.45 + 0.2 * ck.fbm(P * 5.0, SEED + 22))[:, None])
        cols.append(scorch_color(tape, char))
        stitch = np.repeat(np.array([1.0, 0.0, 1.0]), len(s))
        smoulder = ck.smoothstep(0.12, 0.35, ck.fbm(P * 3.0, SEED + 23))
        ems.append(stitch * 0.4 * smoulder + 0.15 * char)
        base += len(P)
    P = np.vstack(Ps)
    J, W = skin_s(rig, np.concatenate(ss))
    ck.finish(mesh, P, np.vstack(Ts), "sail", np.vstack(cols), fixed(J, W), emission=np.concatenate(ems),
              cavity=0.15)
    count("tapes", mesh, before)


def cane(path: np.ndarray, r, segs: int, node_every: float, seed: int, tone=None) -> tuple:
    """A length of cane (bamboo): a tube with swollen nodes and a node ring of darker colour; the colour wanders
    from thatch-gold to weathered timber. Returns (P, T, colour, cavity)."""
    d = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))])
    ph = (d / node_every + seed * 0.37) % 1.0
    node = np.exp(-((ph - 0.5) / 0.06) ** 2)
    rr = np.broadcast_to(np.asarray(r, dtype=np.float64), d.shape) * (1.0 + 0.22 * node)
    P, T = ck.tube(path, rr, segs)
    node_v = np.concatenate([np.repeat(node, segs), [node[0], node[-1]]])
    tone = PAL["thatch"] if tone is None else tone
    c = ck.mix(tone, PAL["timber_weathered"], (0.35 + 0.35 * ck.fbm(P * 6.0, SEED + seed)).clip(0, 1)[:, None])
    c = ck.mix(c, PAL["tortoiseshell"], (0.55 * node_v)[:, None])
    return P, T, c, 0.3 * node_v


def spars(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The frame: a bamboo spine spar on the sail's outer face, a bowed batten across every panel standing past
    both hems, cord lashings where they cross, scorched where the frame crosses a burning seam."""
    before = mesh.triangle_count
    s_sp = np.linspace(0.02, SPINE.length - 0.03, int(SPINE.length / 0.06))
    path = ribbon_point(s_sp, np.zeros(len(s_sp)), billow(s_sp, np.zeros(len(s_sp))) * 0.3, SPAR_OFF)
    r = SPINE_R * (1.0 - 0.45 * ck.smoothstep(0.4 * SPINE.length, SPINE.length, s_sp))
    P, T, c, cav = cane(path, r, 5, 0.27, 1)
    s_v = np.concatenate([np.repeat(s_sp, 5), [s_sp[0], s_sp[-1]]])
    u, k = panel_at(s_v, 0.0)
    char = ck.smoothstep(0.05, 0.0, np.minimum(u, 1.0 - u) * panel_span(k, 0.0))
    J, W = skin_s(rig, s_v)
    ck.finish(mesh, P, T, "spar", scorch_color(c, char), fixed(J, W), cavity=cav)
    lash_s = []
    for i in range(len(SEAMS) - 1):
        sm = float(s_of(i, 0.5, 0.0))
        if SEAMS[i + 1] - SEAMS[i] < 0.2:
            continue
        v = np.linspace(-1.0, 1.0, 7)
        sv = s_of(np.full(len(v), i), 0.5, v)  # the batten runs mid-panel, between the bias-cut seams
        vo = outline(sv, v)
        half = 0.5 * width_at(sv)
        vo = vo + np.sign(v) * BATTEN_OVER / half
        bow = 0.012 * np.cos(0.5 * math.pi * v)
        path = ribbon_point(sv, vo, bow, SPAR_OFF + BATTEN_R + SPINE_R * 0.4)
        P, T, c, cav = cane(path, BATTEN_R, 5, 0.22, 10 + i)
        J, W = skin_s(rig, np.concatenate([np.repeat(sv, 5), [sv[0], sv[-1]]]))
        ck.finish(mesh, P, T, "spar", c, fixed(J, W), cavity=cav)
        lash_s.append(sm)
    count("spars", mesh, before)
    before = mesh.triangle_count
    # lashings: a cord wrapped over each crossing (a squat cross of two wraps)
    for sm in lash_s:
        t, w, n = (a[0] for a in SPINE.frame(np.array([sm]), twist_at(np.array([sm]))))
        c0 = ribbon_point(np.array([sm]), np.array([0.0]), np.array([0.0]), SPAR_OFF + BATTEN_R)[0]
        for ax in (t + w,):
            ax = ax / np.linalg.norm(ax)
            Pe, Te = ck.ellipsoid((0, 0, 0), (0.008, 0.026, 0.013), 3, 5)
            R = np.column_stack([np.cross(ax, n), ax, n])
            Pe = Pe @ R.T + c0 + n * 0.004
            J, W = skin_s(rig, np.full(len(Pe), sm))
            ck.finish(mesh, Pe, Te, "cord", ck.mix(PAL["sand_cloth"], PAL["timber_weathered"], 0.35), fixed(J, W),
                      cavity=0.3)
    count("lashings", mesh, before)


def grommets(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Brass eyelets in the hem tape at each batten's ends, where the batten is tied through; tarnished, worn
    bright on the rim."""
    before = mesh.triangle_count
    segs = 7
    for i in range(len(SEAMS) - 1):
        if SEAMS[i + 1] - SEAMS[i] < 0.2:
            continue
        for hem in (-1.0,):
            sm = float(s_of(i, 0.5 + 0.12 * hem, hem))
            sv = np.array([sm])
            half = 0.5 * float(width_at(sv)[0])
            vo = float(outline(sv, np.array([hem]))[0]) - hem * 0.55 * TAPE_W / half
            t, w, n = (a[0] for a in SPINE.frame(sv, twist_at(sv)))
            c0 = ribbon_point(sv, np.array([vo]), billow(sv, np.array([hem])), SKIN + 0.0025)[0]
            a = np.arange(segs) * 2.0 * math.pi / segs
            ring = []
            for rad, lift in ((GROMMET_R * 0.55, -0.001), (GROMMET_R * 0.75, 0.0022), (GROMMET_R, 0.0)):
                ring.append(c0 + rad * (np.outer(np.cos(a), t) + np.outer(np.sin(a), w)) + n * lift)
            P = np.vstack(ring)
            T = winding_out(P, ck.grid_tris(3, segs, True), n)
            col = np.vstack([np.tile(ck.mix(PAL["brass"], PAL["bronze_patina"], 0.45), (segs, 1)),
                             np.tile(ck.mix(PAL["brass"], PAL["sand_dry"], 0.3), (segs, 1)),
                             np.tile(PAL["brass"], (segs, 1))])
            J, W = skin_s(rig, np.full(len(P), sm))
            ck.finish(mesh, P, T, "key", col, fixed(J, W), cavity=np.repeat([0.6, 0.0, 0.2], segs))
    count("grommets", mesh, before)


# ---------------------------------------------------------------------------------------------
# Mesh: the head (a kite-dragon's: cloth on a cane frame)
# ---------------------------------------------------------------------------------------------
TOP = np.array([(0.0, 0.17), (0.1, 0.22), (0.25, 0.285), (0.4, 0.235), (0.52, 0.18), (0.64, 0.115), (0.74, 0.06)])
BOT = np.array([(0.0, -0.17), (0.1, -0.178), (0.2, -0.16), (0.29, -0.1), (0.42, -0.06), (0.58, -0.035),
                (0.74, -0.005)])
JT = np.array([(0.1, -0.18), (0.28, -0.152), (0.46, -0.13), (0.62, -0.112)])
JB = np.array([(0.1, -0.205), (0.28, -0.262), (0.46, -0.24), (0.62, -0.128)])
EYE = (0.4, 0.115)
CREST = np.array([(0.56, 0.17), (0.4, 0.3), (0.16, 0.37), (-0.12, 0.37), (-0.38, 0.31), (-0.56, 0.22)])


def _prof(tab: np.ndarray, x) -> np.ndarray:
    return np.interp(np.asarray(x, dtype=np.float64), tab[:, 0], tab[:, 1])


def spread(x) -> np.ndarray:
    """How far the cheek's lower edge stands out from the head's mid-plane (a wedge, widest at the cheek)."""
    x = np.asarray(x, dtype=np.float64)
    return 0.014 + 0.095 * ck.smoothstep(0.0, 0.2, x) * (1.0 - 0.6 * ck.smoothstep(0.3, 0.74, x))


def cheek_xyz(x, h, side: float, inner: float = 0.0) -> np.ndarray:
    """A point on a cheek panel: x forward from the back of the head, h 0 (the lower edge) .. 1 (the skull ridge)."""
    x = np.asarray(x, dtype=np.float64)
    h = np.asarray(h, dtype=np.float64)
    y = _prof(BOT, x) + (_prof(TOP, x) - _prof(BOT, x)) * h
    z = spread(x) * np.clip(1.0 - h, 0.0, 1.0) ** 1.3 + 0.008 + 0.012 * np.sin(math.pi * h) * np.sin(math.pi * np.clip(x / 0.74, 0, 1))
    return head_pt(x, y, side * (z - inner))


def head_cloth(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Two cheek panels meeting on the skull ridge, each a double layer (the inner face dark, lit faintly from the
    fire inside the head); the lower jaw hung open below on its own V of cloth; the palate and the jaw's floor dark
    and glowing (the light in the mouth); a faded-teal vane under the crest-spar."""
    before = mesh.triangle_count
    X = np.linspace(0.0, 0.74, 13)
    H = np.linspace(0.0, 1.0, 7)
    XX, HH = np.meshgrid(X, H, indexing="ij")
    hb = rig.index("head")
    for side in (1.0, -1.0):
        Po = cheek_xyz(XX, HH, side).reshape(-1, 3)
        Pi = cheek_xyz(XX, HH, side, inner=0.004).reshape(-1, 3)
        T = ck.grid_tris(len(X), len(H), False)
        o, f, u, z = head_frame()
        T = winding_out(Po, T, z * side)
        P = np.vstack([Po, Pi])
        TT = np.vstack([T, ck.flip(T) + len(Po)])
        xs = np.tile(XX.reshape(-1), 2)
        hs = np.tile(HH.reshape(-1), 2)
        inner = np.repeat([0.0, 1.0], len(Po))
        # cheek: sand cloth, a darker mask band through the eye (a painted kite face), scorched at the mouth seam
        # and the neck seam
        base = ck.mix(PAL["sand_cloth"], PAL["sand_dry"], (0.25 + 0.15 * ck.fbm(P * 5.0, SEED + 31))[:, None])
        # the painted face (a kite-maker's): a teal ring round the eye, a dark stroke sweeping back from it over
        # the cheek, a pale muzzle, a darker crown
        yy = _prof(BOT, xs) + (_prof(TOP, xs) - _prof(BOT, xs)) * hs
        er = np.sqrt((xs - EYE[0]) ** 2 + ((yy - EYE[1]) * 1.3) ** 2)
        ring = ck.smoothstep(0.115, 0.095, er) * ck.smoothstep(0.05, 0.07, er)
        stroke_y = EYE[1] + 0.02 - 0.25 * (EYE[0] - xs)
        stroke = ck.smoothstep(0.03, 0.012, np.abs(yy - stroke_y)) * ck.smoothstep(EYE[0] - 0.02, EYE[0] - 0.08, xs) \
            * ck.smoothstep(0.02, 0.1, xs)
        base = ck.mix(base, PAL["sand_dry"], (0.45 * ck.smoothstep(0.45, 0.7, xs) * ck.smoothstep(0.5, 0.1, hs))[:, None])
        base = ck.mix(base, TAN, (0.55 * ck.smoothstep(0.75, 0.95, hs))[:, None])
        base = ck.mix(base, ck.mix(PAL["faded_teal_cloth"], PAL["deep_teal_shadow"], 0.25), (0.9 * ring)[:, None])
        base = ck.mix(base, ck.mix(PAL["tortoiseshell"], PAL["lacquer_black"], 0.4), (0.85 * stroke)[:, None])
        char = np.maximum(ck.smoothstep(0.06, 0.0, xs - 0.0), ck.smoothstep(0.12, 0.0, hs) * ck.smoothstep(0.24, 0.34, xs))
        char = np.maximum(char, ck.smoothstep(0.035, 0.0, np.abs(xs - 0.2)) * 0.8)
        col = scorch_color(base, char + 0.1 * ck.fbm(P * 8.0, SEED + 32))
        col = np.where(inner[:, None] > 0.5, ck.mix(PAL["tortoiseshell"], PAL["lacquer_black"], 0.5), col)
        glow = np.where(inner > 0.5, 0.16, 0.18 * ck.smoothstep(0.6, 1.0, char))
        J, W = skin_s(rig, s_of_head(P))
        ck.finish(mesh, P, TT, "sail", np.clip(col, PAL["lacquer_black"], PAL["gauze_white"]), fixed(J, W),
                  emission=glow, cavity=0.25 * inner, uv=np.column_stack([xs * 0.6, hs * 0.2]))
        # the lower jaw: a V of cloth, the keel below, the lip above
        JX = np.linspace(0.1, 0.62, 10)
        JH = np.linspace(0.0, 1.0, 4)
        JXX, JHH = np.meshgrid(JX, JH, indexing="ij")
        y = _prof(JB, JXX) + (_prof(JT, JXX) - _prof(JB, JXX)) * JHH
        jsp = 0.012 + 0.07 * (1.0 - ck.smoothstep(0.32, 0.66, JXX))
        Po = head_pt(JXX, y, side * (jsp * JHH + 0.005)).reshape(-1, 3)
        Pi = head_pt(JXX, y, side * (jsp * JHH + 0.001)).reshape(-1, 3)
        T = winding_out(Po, ck.grid_tris(len(JX), len(JH), False), z * side - u * 0.5)
        P = np.vstack([Po, Pi])
        TT = np.vstack([T, ck.flip(T) + len(Po)])
        jh = np.tile(JHH.reshape(-1), 2)
        inner = np.repeat([0.0, 1.0], len(Po))
        c = ck.mix(PAL["sand_cloth"], PAL["sand_wet"], (0.35 + 0.2 * ck.fbm(P * 6.0, SEED + 33))[:, None])
        c = scorch_color(c, ck.smoothstep(0.55, 1.0, jh))
        c = np.where(inner[:, None] > 0.5, ck.mix(PAL["tortoiseshell"], PAL["lacquer_black"], 0.4), c)
        ck.finish(mesh, P, TT, "sail", c, hb, emission=np.where(inner > 0.5, 0.3, 0.12 * jh))
    # the palate and the jaw's floor, inside the mouth: dark, glowing toward the throat
    for tab, lift, face in ((BOT, 0.012, -1.0), (JT, -0.012, 1.0)):
        MX = np.linspace(0.24 if tab is BOT else 0.12, 0.7 if tab is BOT else 0.6, 8)
        MZ = np.linspace(-1.0, 1.0, 5)
        MXX, MZZ = np.meshgrid(MX, MZ, indexing="ij")
        wide = spread(MXX) if tab is BOT else 0.012 + 0.07 * (1.0 - ck.smoothstep(0.32, 0.66, MXX))
        P = head_pt(MXX, _prof(tab, MXX) + lift * (1.0 - 0.5 * np.abs(MZZ)), MZZ * wide).reshape(-1, 3)
        o, f, u, z = head_frame()
        T = winding_out(P, ck.grid_tris(len(MX), len(MZ), False), u * face)
        xs = MXX.reshape(-1)
        deep = ck.smoothstep(0.7, 0.24, xs)
        c = ck.mix(PAL["tortoiseshell"], PAL["lacquer_black"], (0.3 + 0.4 * (1.0 - deep))[:, None])
        ck.finish(mesh, P, T, "sail", c, hb, emission=0.2 + 0.45 * deep, cavity=0.3)
    count("head", mesh, before)


def crest_vane(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A faded-teal pennant hung from the crest-spar and swept back past the head, its free edge scalloped and burnt
    (it never touches the head: the wind holds it off)."""
    before = mesh.triangle_count
    X = np.linspace(0.46, -0.52, 12)
    H = np.linspace(0.0, 1.0, 4)
    XX, HH = np.meshgrid(X, H, indexing="ij")
    top = _prof(CREST[::-1], XX) - 0.004
    room = np.where(XX >= 0.0, top - _prof(TOP, np.clip(XX, 0.0, 0.74)) - 0.012, 0.12)
    depth = np.minimum(0.075 * (0.7 + 0.3 * np.abs(np.sin(3.3 * math.pi * XX))), room)
    depth = depth * (1.0 - 0.45 * ck.smoothstep(-0.1, -0.52, XX))
    y = top - depth * (1.0 - HH)
    o, f, u, z = head_frame()
    lob = 0.008 * np.sin(math.pi * (1.0 - HH)) * np.sin(3.0 * math.pi * XX)
    Pf = head_pt(XX, y, lob + 0.003).reshape(-1, 3)
    Pb = head_pt(XX, y, lob - 0.003).reshape(-1, 3)
    T = winding_out(Pf, ck.grid_tris(len(X), len(H), False), z)
    P, TT = two_faced(Pf, Pb, T)
    hs = np.tile(HH.reshape(-1), 2)
    c = ck.mix(PAL["faded_teal_cloth"], PAL["sand_cloth"], (0.2 + 0.2 * ck.fbm(P * 5.0, SEED + 41))[:, None])
    stripe = ck.smoothstep(0.08, 0.0, np.abs(hs - 0.55))
    c = ck.mix(c, PAL["sand_dry"], (0.4 * stripe)[:, None])
    char = ck.smoothstep(0.3, 0.0, hs) * 0.9
    c = scorch_color(c, char)
    J, W = skin_s(rig, s_of_head(P))
    ck.finish(mesh, P, TT, "sail", c, fixed(J, W), emission=0.25 * ck.smoothstep(0.6, 1.0, char))
    count("vane", mesh, before)


def cheek_frills(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A fan of kite cells at the back of each cheek: five cane ribs from a hub, cloth between them with a scalloped
    burnt edge, swept back over the neck and turned out toward the cameras' side (a fan kite's frill)."""
    before = mesh.triangle_count
    o, f, u, z = head_frame()
    ribs = np.radians([105.0, 132.0, 160.0, 188.0, 214.0])  # from up-back round to down-back
    lens = np.array([0.25, 0.33, 0.37, 0.32, 0.24])
    for side in (1.0, -1.0):
        hub = head_pt(np.array(0.07), np.array(0.02), np.array(side * (spread(0.07) * 0.6 + 0.035)))
        out = z * side
        dirs = []
        for a_, ln in zip(ribs, lens):
            d = math.cos(a_) * f + math.sin(a_) * u
            d = d * math.cos(math.radians(24.0)) + out * math.sin(math.radians(24.0))
            dirs.append(d / np.linalg.norm(d) * ln)
        # the cloth between ribs: per cell a small fan grid (radial 4 x angular 4)
        Ps, Ts, ks, cell_i = [], [], [], []
        base = 0
        for i in range(len(dirs) - 1):
            R = np.linspace(0.0, 1.0, 4)
            Aa = np.linspace(0.0, 1.0, 4)
            RR, AA = np.meshgrid(R, Aa, indexing="ij")
            dvec = dirs[i][None, None] * (1 - AA)[..., None] + dirs[i + 1][None, None] * AA[..., None]
            scal = 1.0 - 0.16 * np.sin(math.pi * AA) * RR ** 3  # the edge scalloped between the ribs
            pts = hub + dvec * (RR * scal)[..., None]
            Pf = pts.reshape(-1, 3) + out * 0.002
            Pb = pts.reshape(-1, 3) - out * 0.002
            T = winding_out(Pf, ck.grid_tris(4, 4, False), out)
            P, TT = two_faced(Pf, Pb, T)
            Ps.append(P)
            Ts.append(TT + base)
            ks.append(np.tile(RR.reshape(-1), 2))
            cell_i.append(np.full(len(P), i))
            base += len(P)
        P = np.vstack(Ps)
        rr = np.concatenate(ks)
        ci = np.concatenate(cell_i)
        c = np.where((ci % 2 == 0)[:, None], ck.mix(PAL["sand_cloth"], PAL["sand_dry"], 0.3),
                     ck.mix(PAL["faded_teal_cloth"], PAL["sand_cloth"], 0.3))
        char = ck.smoothstep(0.7, 1.0, rr) * 0.95
        c = scorch_color(np.broadcast_to(c, (len(P), 3)).copy(), char)
        J, W = skin_s(rig, s_of_head(P))
        ck.finish(mesh, P, np.vstack(Ts), "sail", c, fixed(J, W), emission=0.08 + 0.4 * ck.smoothstep(0.75, 1.0, rr))
        for i, d in enumerate(dirs):
            path = hub + np.outer(np.linspace(0.0, 1.04, 5), d) + out * 0.006
            Pc, Tc, cc, cav = cane(path, 0.0055 * np.linspace(1.0, 0.6, 5), 4, 0.12, 80 + i)
            J, W = skin_s(rig, s_of_head(Pc))
            ck.finish(mesh, Pc, Tc, "spar", cc, fixed(J, W), cavity=cav)
    count("frills", mesh, before)


def head_frame_canes(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The head's cane: the skull ridge, the bowed crest-spar (two rods) swept back from it, a cheek batten and a
    brow cane over each eye, the jaw's keel cane; cord lashings where they meet."""
    before = mesh.triangle_count
    X = np.linspace(0.74, 0.0, 14)
    paths = [(head_pt(X, _prof(TOP, X) + 0.006, np.zeros_like(X)), 0.0105, 0.2)]
    for dz, r in ((0.0, 0.0095), (0.035, 0.0065)):
        P0 = head_pt(CREST[:, 0], CREST[:, 1], np.full(len(CREST), dz))
        paths.append((ck.bezier(P0, 16), r * np.linspace(1.0, 0.55, 16), 0.24))
    for side in (1.0, -1.0):
        H = np.linspace(0.0, 1.0, 6)
        paths.append((cheek_xyz(np.full(6, 0.2), H, side, inner=-0.009), 0.0075, 0.2))
        th = np.linspace(0.15, math.pi - 0.15, 9)
        bx = EYE[0] + 0.1 * np.cos(th)
        by = EYE[1] + 0.035 + 0.075 * np.sin(th)
        h = (by - _prof(BOT, bx)) / (_prof(TOP, bx) - _prof(BOT, bx))
        paths.append((cheek_xyz(bx, h, side, inner=-0.01), 0.0068, 0.15))
        JX = np.linspace(0.1, 0.62, 9)
        paths.append((head_pt(JX, _prof(JB, JX) - 0.004, np.full(len(JX), side * 0.006)), 0.006, 0.18))
    for i, (path, r, node) in enumerate(paths):
        P, T, c, cav = cane(path, r, 5, node, 60 + i)
        J, W = skin_s(rig, s_of_head(P))
        ck.finish(mesh, P, T, "spar", c, fixed(J, W), cavity=cav)
    count("head_canes", mesh, before)


def head_seams(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Fire on the head's seams: along each lip (the cheek's mouth edge and the jaw's), at the neck and down the
    cheek seam under the batten."""
    before = mesh.triangle_count
    hb = rig.index("head")
    o, f, u, z = head_frame()
    lines = []
    for side in (1.0, -1.0):
        X = np.linspace(0.27, 0.73, 11)
        lines.append((cheek_xyz(X, np.full(len(X), 0.03), side, inner=-0.003), side, True))
        JX = np.linspace(0.16, 0.61, 10)
        jsp = 0.012 + 0.07 * (1.0 - ck.smoothstep(0.32, 0.66, JX))
        lines.append((head_pt(JX, _prof(JT, JX) - 0.006, side * (jsp + 0.008)), side, True))
        H = np.linspace(0.04, 0.96, 9)
        lines.append((cheek_xyz(np.full(len(H), 0.025), H, side, inner=-0.003), side, False))
        lines.append((cheek_xyz(np.full(len(H), 0.2), H, side, inner=-0.003), side, False))
    for path, side, lip in lines:
        K = len(path)
        tan = np.gradient(path, axis=0)
        tan /= np.linalg.norm(tan, axis=1, keepdims=True)
        out = z * side
        across = np.cross(out, tan)
        across /= np.linalg.norm(across, axis=1, keepdims=True)
        wob = 0.7 + 0.6 * (0.5 + 0.5 * np.sin(np.arange(K) * 1.9 + side))
        hw = 0.011
        rows = [path + across * (o_ * hw * (wob[:, None] if abs(o_) < 0.5 else 1.0)) + out * l
                for o_, l in ((-1.0, 0.0), (-0.35, 0.002), (0.35, 0.002), (1.0, 0.0))]
        P = np.vstack(rows)
        T = winding_out(P, ck.grid_tris(4, K, False), out)
        core = np.repeat([0.0, 1.0, 1.0, 0.0], K)
        c = np.where(core[:, None] > 0.5, ck.mix(PAL["salt_glass"], PAL["gauze_white"], 0.4), PAL["lacquer_black"])
        em = np.where(core > 0.5, 0.7 + 0.3 * np.tile(wob - 0.7, 4) / 0.6, 0.08)
        J, W = skin_s(rig, s_of_head(P))
        ck.finish(mesh, P, T, "seam", c, fixed(J, W), emission=em, cavity=0.3 * (1 - core))
    count("head_seams", mesh, before)


def eyes(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A lantern-eye on each cheek: a ribbed paper bulb lit from inside by her bound light (her soul-light, so
    `glimmer_bound`), its ribs darker, a dark pupil at its crown (the gaze, a little forward), set in a ring of
    cane lashed to the cheek."""
    before = mesh.triangle_count
    hb = rig.index("head")
    o, f, u, z = head_frame()
    prof = [(0.0, -0.004), (0.046, 0.0), (0.056, 0.014), (0.053, 0.028), (0.04, 0.039), (0.02, 0.046), (0.0, 0.048)]
    segs = 12
    for side in (1.0, -1.0):
        h = (EYE[1] - _prof(BOT, EYE[0])) / (_prof(TOP, EYE[0]) - _prof(BOT, EYE[0]))
        c0 = cheek_xyz(np.array([EYE[0]]), np.array([h]), side)[0]
        dx = cheek_xyz(np.array([EYE[0] + 0.01]), np.array([h]), side)[0] - c0
        dh = cheek_xyz(np.array([EYE[0]]), np.array([h + 0.02]), side)[0] - c0
        nrm = np.cross(dx, dh) * side
        nrm /= np.linalg.norm(nrm)
        if np.dot(nrm, z * side) < 0:
            nrm = -nrm
        nrm = nrm + f * 0.3  # the eye looks a little forward
        nrm /= np.linalg.norm(nrm)
        P, T = ck.lathe(prof, segs)
        ax_x = f - np.dot(f, nrm) * nrm
        ax_x /= np.linalg.norm(ax_x)
        ax_z = np.cross(ax_x, nrm)
        local = P.copy()
        local[:, 0] *= 1.12  # a little long, like an eye
        P = c0 + np.outer(local[:, 0], ax_x) + np.outer(local[:, 1], nrm) + np.outer(local[:, 2], ax_z)
        T = winding_out(P, T, P - c0)
        hgt = local[:, 1] / 0.048
        rib = np.tile(np.arange(segs) % 2, len(prof)).astype(np.float64) * (1.0 - ck.smoothstep(0.75, 0.95, hgt))
        pupil = ck.smoothstep(0.9, 1.0, hgt)
        c = ck.mix(PAL["salt_glass"], PAL["gauze_white"], (0.35 * hgt)[:, None])
        c = ck.mix(c, PAL["tortoiseshell"], (0.55 * rib)[:, None])
        c = ck.mix(c, PAL["deep_teal_shadow"], (0.9 * pupil)[:, None])
        em = (0.5 + 0.45 * ck.smoothstep(0.2, 0.8, hgt)) * (1.0 - 0.45 * rib) * (1.0 - 0.85 * pupil)
        ck.finish(mesh, P, T, "seam", c, hb, emission=em)
        th = np.linspace(0.0, 2.0 * math.pi, 13)
        ringp = c0 + 0.062 * (np.outer(np.cos(th) * 1.12, ax_x) + np.outer(np.sin(th), ax_z)) + nrm * 0.004
        Pc, Tc, cc, cav = cane(ringp, 0.0075, 4, 0.1, 90)
        ck.finish(mesh, Pc, Tc, "spar", ck.mix(cc, PAL["tortoiseshell"], 0.3), hb, cavity=cav)
    count("eyes", mesh, before)


def nose_scroll(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """A curl of cane at the snout's tip, rolled up and back like a fern's head: the kite-maker's flourish."""
    before = mesh.triangle_count
    hb = rig.index("head")
    th = np.linspace(0.0, 1.5 * math.pi, 14)
    rad = 0.055 * (1.0 - 0.55 * th / th[-1])
    x = 0.74 + rad * np.sin(th)
    y = 0.05 + 0.055 - rad * np.cos(th)
    P0 = head_pt(x, y, np.zeros_like(x))
    P, T, c, cav = cane(P0, np.linspace(0.009, 0.005, len(P0)), 5, 0.06, 95)
    ck.finish(mesh, P, T, "spar", c, hb, cavity=cav)
    count("nose", mesh, before)


def whiskers(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """Cord whiskers from the snout, streaming back along the head and past it on the wind, each ending in a
    tassel."""
    before = mesh.triangle_count
    hb = rig.index("head")
    K = 22
    for side in (1.0, -1.0):
        ctrl = np.array([(0.72, 0.03, 0.03), (0.86, 0.06, 0.1), (0.6, -0.06, 0.2), (0.32, -0.2, 0.22),
                         (0.18, -0.4, 0.2), (0.0, -0.46, 0.16)])
        ctrl[:, 2] *= side
        path = ck.bezier(head_pt(ctrl[:, 0], ctrl[:, 1], ctrl[:, 2]), K)
        r = np.linspace(0.009, 0.004, K)
        P, T = ck.tube(path, r, 5)
        twist = np.repeat(np.arange(K) % 2, 5)
        c = ck.mix(PAL["sand_cloth"], PAL["timber_weathered"], (0.3 + 0.2 * np.concatenate([twist, [0, 0]]))[:, None])
        J, W = skin_s(rig, s_of_head(P))
        ck.finish(mesh, P, T, "cord", c, fixed(J, W), cavity=0.2)
        tip = path[-1]
        tprof = [(0.0, 0.012), (0.009, 0.006), (0.013, -0.02), (0.016, -0.055), (0.0, -0.06)]
        Pt, Tt = ck.lathe(tprof, 6)
        Pt = Pt + tip
        J, W = skin_s(rig, s_of_head(Pt))
        ck.finish(mesh, Pt, Tt, "cord", ck.mix(PAL["faded_teal_cloth"], PAL["sand_cloth"], 0.3), fixed(J, W),
                  cavity=0.3)
    count("whiskers", mesh, before)


def flames(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The fire, held still: little clusters of flame tongues licking off the upper hem where each burning seam
    meets it (smaller ones on the belly hem and along the upper hem between seams), every tongue curling and
    leaning back toward the tail as a flare's flames stream downwind. Each is a thin double-faced blade, broad at
    its root and brightest there; they move only as her body moves (bound light: no flicker, no drift)."""
    before = mesh.triangle_count
    rng = rng_for(7)
    sites = []
    for k in range(1, len(SEAMS) - 1):
        sites.append((float(seam_line(k, -1.0)), -1.0, rng.uniform(0.08, 0.12), 3))
        if rng.random() < 0.45:
            sites.append((float(seam_line(k, 1.0)), 1.0, rng.uniform(0.05, 0.07), 1))
    for i in range(len(SEAMS) - 1):
        if rng.random() < 0.5:
            sites.append((float(s_of(i, rng.uniform(0.35, 0.65), -1.0)), -1.0, rng.uniform(0.04, 0.06), 1))
    Ps, Ts, ss, cols, ems = [], [], [], [], []
    base = 0
    K = 4
    k = np.linspace(0.0, 1.0, K)
    up = np.array([0.0, 1.0, 0.0])
    for s0, hem, ln0, n_t in sites:
        if s0 > SPINE.length - 0.3:
            continue
        for j in range(n_t):
            ds = (0.0, -0.028, 0.03)[j]
            sv = np.array([s0 + ds])
            t, w, n = (a[0] for a in SPINE.frame(sv, twist_at(sv)))
            root = ribbon_point(sv, outline(sv, np.array([hem * 0.96])), billow(sv, np.array([hem])))[0]
            out = w * hem
            ln = ln0 * (1.0, 0.62, 0.5)[j] * (1.0 - 0.35 * s0 / SPINE.length)
            d = 0.6 * out + 0.75 * t + 0.25 * up
            d /= np.linalg.norm(d)
            side = np.cross(n, d)
            side /= np.linalg.norm(side)
            curl = float(rng.uniform(0.25, 0.5)) * (1.0 if rng.random() < 0.5 else -1.0)
            spine = root + np.outer(k * ln, d) + np.outer(curl * ln * np.sin(math.pi * k) * k, side) \
                + np.outer(0.25 * ln * k ** 2, t)
            half = ln * 0.3 * np.sin(math.pi * np.clip(0.18 + 0.82 * k, 0, 1)) ** 0.6 * (1.0 - k) ** 0.45
            rows = [spine + side * (a_ * half)[:, None] for a_ in (-1.0, 0.0, 1.0)]
            Pf = np.vstack([rows[0] + n * 0.002, rows[1] + n * 0.005, rows[2] + n * 0.002])
            Pb = np.vstack([rows[0] - n * 0.002, rows[1] - n * 0.005, rows[2] - n * 0.002])
            T = winding_out(Pf, ck.grid_tris(3, K, False), n)
            P, TT = two_faced(Pf, Pb, T)
            Ps.append(P)
            Ts.append(TT + base)
            ss.append(np.full(len(P), s0))
            kk = np.tile(np.tile(k, 3), 2)
            core = np.tile(np.repeat([0.0, 1.0, 0.0], K), 2)
            cols.append(ck.mix(ck.mix(PAL["salt_glass"], PAL["gauze_white"], 0.6), PAL["salt_glass"],
                               (0.7 * kk)[:, None]))
            ems.append((1.0 - 0.55 * kk ** 1.5) * (0.75 + 0.25 * core))
            base += len(P)
    P = np.vstack(Ps)
    J, W = skin_s(rig, np.concatenate(ss))
    ck.finish(mesh, P, np.vstack(Ts), "seam", np.vstack(cols), fixed(J, W), emission=np.concatenate(ems))
    count("flames", mesh, before)


# ---------------------------------------------------------------------------------------------
# Mesh: the bridle and the key
# ---------------------------------------------------------------------------------------------
def bridle_points() -> list[np.ndarray]:
    """Where the bridle lines leave the head: two on the jaw's keel and one on the throat (the neck's belly hem)."""
    out = [head_pt(np.array(0.22), _prof(JB, 0.22) - 0.004, np.array(0.0)),
           head_pt(np.array(0.47), _prof(JB, 0.47) - 0.004, np.array(0.0))]
    s0 = np.array([0.22])
    out.append(ribbon_point(s0, outline(s0, np.array([1.0])))[0])
    return out


def bridle_knot() -> np.ndarray:
    pts = bridle_points()
    return np.mean(pts, axis=0) + np.array([0.0, -BRIDLE_DROP, 0.0])


def key_top() -> np.ndarray:
    return bridle_knot() - np.array([0.0, KEY_CORD, 0.0])


def key_bow_centre() -> np.ndarray:
    return key_top() - np.array([0.0, KEY_BOW_R + 0.006, 0.0])


def bridle(mesh: ck.Mesh, rig: ck.Rig) -> None:
    before = mesh.triangle_count
    knot = bridle_knot()
    hb = rig.rigid("head")
    for p in bridle_points():
        mid = 0.5 * (p + knot) + np.array([0.0, -0.015, 0.0])  # a little slack
        path = ck.bezier([p, mid, knot], 6)
        P, T = ck.tube(path, CORD_R, 4, cap_start=False, cap_end=False)
        ck.finish(mesh, P, T, "cord", ck.mix(PAL["sand_cloth"], PAL["timber_weathered"], 0.25), hb)
    Pk, Tk = ck.ellipsoid(knot, (0.016, 0.014, 0.016), 4, 6)
    ck.finish(mesh, Pk, Tk, "cord", ck.mix(PAL["sand_cloth"], PAL["timber_weathered"], 0.4), hb, cavity=0.4)
    kb = rig.rigid("key")
    top = key_top()
    path = np.array([knot + (top - knot) * f for f in np.linspace(0.0, 1.0, 4)])
    P, T = ck.tube(path, CORD_R * 0.9, 4, cap_start=False, cap_end=False)
    ck.finish(mesh, P, T, "cord", ck.mix(PAL["sand_cloth"], PAL["timber_weathered"], 0.4), kb)
    # the cord's loop through the bow
    c = key_bow_centre()
    a = np.linspace(-0.6, 0.6 + math.pi, 9)
    loop = top + np.outer(0.012 * np.sin(a), E_N) + np.outer(-0.013 * (1 - np.cos(a)) + 0.004, np.array([0, 1.0, 0]))
    P, T = ck.tube(loop, CORD_R * 0.9, 4)
    ck.finish(mesh, P, T, "cord", ck.mix(PAL["sand_cloth"], PAL["timber_weathered"], 0.4), kb)
    count("cord", mesh, before)


def key(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """The brass tuning key, the keepsake: a ring bow with a bead at its crown, a collar, a turned shaft with two
    scored bands, and a square socket with a dark hollow at its end; tarnished in the hollows, worn bright on the
    bow's rim and the collar's edges (the glint). It faces the cameras."""
    before = mesh.triangle_count
    kb = rig.rigid("key")
    c = key_bow_centre()
    up = np.array([0.0, 1.0, 0.0])
    side = E_A  # the bow's plane is (up, E_A): it faces E_N, the cameras
    nrm = E_N
    # the bow: a torus, its section a little flattened (a cast ring)
    segs, ring = 20, 7
    th = np.linspace(0.0, 2.0 * math.pi, segs, endpoint=False)
    ph = np.linspace(0.0, 2.0 * math.pi, ring, endpoint=False)
    rows = []
    for t in th:
        radial = math.cos(t) * up + math.sin(t) * side
        rows.append(c + KEY_BOW_R * radial + 0.011 * np.outer(np.cos(ph), radial) + 0.0075 * np.outer(np.sin(ph), nrm))
    P = np.vstack(rows)
    T = []
    for i in range(segs):  # both loops wrap
        i1 = (i + 1) % segs
        for j in range(ring):
            j1 = (j + 1) % ring
            a, b, d, e = i * ring + j, i * ring + j1, i1 * ring + j, i1 * ring + j1
            T += [(a, d, b), (b, d, e)]
    out = np.repeat(np.array([math.cos(t) * up + math.sin(t) * side for t in th]), ring, axis=0)
    T = winding_out(P, np.asarray(T), P - (c + KEY_BOW_R * out))
    outer = np.einsum("ij,ij->i", P - c, out) / KEY_BOW_R  # >1 on the outer rim
    face = np.abs(np.einsum("ij,j->i", P - c, nrm)) / 0.0075
    bright = ck.smoothstep(1.05, 1.17, outer) * 0.6 + ck.smoothstep(0.6, 1.0, face) * 0.25
    col = ck.mix(PAL["brass"], PAL["sand_dry"], (0.15 + bright)[:, None])
    col = ck.mix(col, PAL["bronze_patina"], (0.35 * ck.smoothstep(0.95, 0.85, outer))[:, None])
    ck.finish(mesh, P, T, "key", col, kb, cavity=0.4 * ck.smoothstep(0.95, 0.85, outer))
    # a bead at the bow's crown, where the cord's loop passes
    Pb, Tb = ck.ellipsoid(c + up * (KEY_BOW_R + 0.004), (0.009, 0.012, 0.012), 4, 8)
    ck.finish(mesh, Pb, Tb, "key", ck.mix(PAL["brass"], PAL["sand_dry"], 0.4), kb)
    # collar, shaft, socket: one turned profile below the bow (y down from the bow's foot)
    y0 = c[1] - KEY_BOW_R - 0.006
    prof = [(0.0, 0.004), (0.012, 0.004), (0.017, -0.004), (0.02, -0.012), (0.016, -0.02), (0.0095, -0.026),
            (0.0095, -0.08), (0.0115, -0.084), (0.0115, -0.09), (0.0095, -0.094), (0.0095, -0.14),
            (0.0115, -0.144), (0.0115, -0.15), (0.0095, -0.154), (0.009, -KEY_LEN + 0.07),
            (0.014, -KEY_LEN + 0.062)]
    P, T = ck.lathe([(r, y0 + y) for r, y in prof], 10)
    P = P + np.array([c[0], 0.0, c[2]])
    yy = P[:, 1] - y0
    band = ((yy < -0.083) & (yy > -0.095)) | ((yy < -0.143) & (yy > -0.155))
    rad = np.linalg.norm((P - np.array([c[0], 0, c[2]]))[:, [0, 2]], axis=1)
    col = ck.mix(PAL["brass"], PAL["sand_dry"], (0.15 + 0.4 * ck.smoothstep(0.015, 0.02, rad))[:, None])
    col = ck.mix(col, PAL["bronze_patina"], (0.5 * band)[:, None])
    ck.finish(mesh, P, T, "key", col, kb, cavity=0.5 * band)
    # the socket: a square tube (flat-shaded), its end hollow and dark
    sy0, sy1 = y0 - KEY_LEN + 0.062, y0 - KEY_LEN
    hw = 0.016
    sq = [(-hw, -hw), (hw, -hw), (hw, hw), (-hw, hw)]
    ax_a = side
    ax_b = nrm
    corners = []
    for y in (sy0, sy1):
        for a_, b_ in sq:
            corners.append(np.array([c[0], y, c[2]]) + a_ * ax_a + b_ * ax_b)
    inner = []
    for a_, b_ in sq:
        inner.append(np.array([c[0], sy1 + 0.002, c[2]]) + 0.55 * (a_ * ax_a + b_ * ax_b))
    Pq = np.vstack(corners + inner)
    Tq = []
    for i in range(4):
        i1 = (i + 1) % 4
        Tq += [(i, 4 + i, i1), (i1, 4 + i, 4 + i1)]  # the sides
        Tq += [(4 + i, 8 + i, 4 + i1), (4 + i1, 8 + i, 8 + i1)]  # the end's rim
    Tq += [(8, 9, 10), (8, 10, 11)]  # the hollow
    Tq = np.asarray(Tq)
    ctr = np.array([c[0], 0.5 * (sy0 + sy1), c[2]])
    Tq = np.vstack([winding_out(Pq, Tq[:16], Pq - ctr), winding_out(Pq, Tq[16:], -up)])
    cq = np.vstack([np.tile(ck.mix(PAL["brass"], PAL["sand_dry"], 0.2), (8, 1)), np.tile(PAL["lacquer_black"], (4, 1))])
    ck.finish(mesh, Pq, Tq, "key", cq, kb, flat=True, cavity=np.concatenate([np.zeros(8), np.ones(4)]))
    count("key", mesh, before)


# ---------------------------------------------------------------------------------------------
# Mesh: the tail
# ---------------------------------------------------------------------------------------------
def tail(mesh: ck.Mesh, rig: ck.Rig) -> None:
    """From the tail end: two ribbon streamers, forked at their ends, and between them a kite-tail: a cord with
    three cloth bows tied along it and a tassel at its end. Rigid on the streamer bone."""
    before = mesh.triangle_count
    end = SPINE.at(SPINE.length)
    t, w, n = (a[0] for a in SPINE.frame(np.array([SPINE.length]), twist_at(np.array([SPINE.length]))))
    sb = rig.rigid("streamer")
    d = streamer_dir()
    sideways = np.cross(d, E_N)
    sideways /= np.linalg.norm(sideways)
    face = np.cross(sideways, d)
    for sgn, ln, wid, tone in ((1.0, 0.86, 0.1, "faded_teal_cloth"), (-1.0, 0.7, 0.088, "sand_cloth")):
        K = 12
        k = np.linspace(0.0, 1.0, K)
        path = end[None] + np.outer(k * ln, d) + np.outer(sgn * (0.05 + 0.1 * k ** 1.2), sideways) \
            + np.outer(0.05 * np.sin(k * math.pi * 1.6 + sgn), face)
        half = wid * 0.5 * (1.0 - 0.35 * k)
        fork = ck.smoothstep(0.82, 1.0, k)  # the end cut in a swallowtail
        Ps = []
        for vv in (-1.0, -0.5, 0.0, 0.5, 1.0):
            notch = (1.0 - abs(vv)) * 0.09 * fork
            Ps.append(path + sideways * (vv * half)[:, None] - np.outer(notch * ln, d) * 0.6)
        front = np.vstack(Ps) + face * 0.0025
        back = np.vstack(Ps) - face * 0.0025
        T = winding_out(front, ck.grid_tris(5, K, False), face)
        P, TT = two_faced(front, back, T)
        kk = np.tile(np.tile(k, 5), 2)
        vv = np.tile(np.repeat([-1.0, -0.5, 0.0, 0.5, 1.0], K), 2)
        c = ck.mix(PAL[tone], PAL["sand_cloth"], 0.25)
        c = ck.mix(c, PAL["sand_dry"], (0.3 * ck.smoothstep(0.3, 0.0, np.abs(vv)))[:, None])
        c = scorch_color(np.broadcast_to(c, (len(P), 3)).copy(), ck.smoothstep(0.75, 1.0, kk) * 0.8
                         + ck.smoothstep(0.08, 0.0, kk) * 0.7)
        em = 0.1 + 0.35 * ck.smoothstep(0.35, 0.0, np.abs(vv)) * ck.smoothstep(0.0, 0.3, kk) * (1 - kk)
        ck.finish(mesh, P, TT, "sail", c, sb, emission=em)
    # the kite-tail: a cord with three bows and a tassel
    K = 14
    k = np.linspace(0.0, 1.0, K)
    L = 0.95
    path = end[None] + np.outer(k * L, d) + np.outer(0.04 * np.sin(k * math.pi * 2.2), sideways) \
        + np.outer(0.03 * np.sin(k * math.pi * 1.3), face) - n * 0.01
    P, T = ck.tube(path, 0.006, 4)
    ck.finish(mesh, P, T, "cord", ck.mix(PAL["sand_cloth"], PAL["timber_weathered"], 0.35), sb)
    for i, kb_ in enumerate((0.3, 0.55, 0.78)):
        c0 = end + d * (kb_ * L) + sideways * 0.04 * math.sin(kb_ * math.pi * 2.2) + face * 0.03 * math.sin(
            kb_ * math.pi * 1.3)
        size = 0.1 - 0.014 * i
        tone = ["sea_blue_cloth", "faded_teal_cloth", "sand_cloth"][i]
        for sgn in (1.0, -1.0):
            # one wing of the bow: a pinched triangle of cloth, gathered at the knot
            g = np.linspace(0.0, 1.0, 4)
            a = np.linspace(-1.0, 1.0, 3)
            G, A = np.meshgrid(g, a, indexing="ij")
            spread_ = size * 0.55 * G ** 0.7
            pts = c0 + np.multiply.outer(sgn * G * size, sideways) + np.multiply.outer(A * spread_, d) \
                + np.multiply.outer(0.012 * np.sin(math.pi * G) * (1 - A ** 2), face)
            Pf = pts.reshape(-1, 3) + face * 0.002
            Pb = pts.reshape(-1, 3) - face * 0.002
            T = winding_out(Pf, ck.grid_tris(4, 3, False), face)
            P, TT = two_faced(Pf, Pb, T)
            gg = np.tile(G.reshape(-1), 2)
            c = ck.mix(PAL[tone], PAL["sand_cloth"], 0.3)
            c = scorch_color(np.broadcast_to(c, (len(P), 3)).copy(), ck.smoothstep(0.8, 1.0, gg) * 0.7)
            ck.finish(mesh, P, TT, "sail", c, sb, emission=0.12 * ck.smoothstep(0.8, 1.0, gg))
        Pk, Tk = ck.ellipsoid(c0, (0.012, 0.012, 0.012), 3, 6)
        ck.finish(mesh, Pk, Tk, "cord", ck.mix(PAL["sand_cloth"], PAL["timber_weathered"], 0.45), sb, cavity=0.3)
    tip = path[-1]
    tprof = [(0.0, 0.02), (0.017, 0.011), (0.025, -0.04), (0.034, -0.11), (0.0, -0.12)]
    Pt, Tt = ck.lathe(tprof, 7)
    Pt = Pt + tip
    ck.finish(mesh, Pt, Tt, "cord", ck.mix(PAL["faded_teal_cloth"], PAL["deep_teal_shadow"], 0.25), sb, cavity=0.3)
    count("tail", mesh, before)


def build_mesh(rig: ck.Rig) -> ck.Mesh:
    PARTS.clear()
    mesh = ck.Mesh("virel")
    sail(mesh, rig)
    mends(mesh, rig)
    seams(mesh, rig)
    hem_tapes(mesh, rig)
    spars(mesh, rig)
    grommets(mesh, rig)
    head_cloth(mesh, rig)
    crest_vane(mesh, rig)
    cheek_frills(mesh, rig)
    head_frame_canes(mesh, rig)
    head_seams(mesh, rig)
    eyes(mesh, rig)
    nose_scroll(mesh, rig)
    whiskers(mesh, rig)
    flames(mesh, rig)
    bridle(mesh, rig)
    key(mesh, rig)
    tail(mesh, rig)
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
    """A bone's rotation: `bend` about the S's normal (in the S's plane), `twist` about the bone's own rest
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
    """Every fore bone bent `deg_fore`, every aft bone `deg_aft`, the head `head` (about the S's normal)."""
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


IDLE_BEND, IDLE_SWAY, IDLE_LUFF = 1.9, 1.4, 4.5  # degrees per bone: in the plane, out of it, and about the bone
IDLE_LAG = 0.62  # radians of phase per bone, nose to tail: about one wavelength along her


def build_idle() -> ck.Clip:
    """Riding the wind: a travelling wave runs down her from the nose to the tail (each spine bone bends in the S's
    plane and sways out of it a beat behind the bone before, growing toward the tail), the panels luff twice a
    cycle, she bobs and the streamers flutter."""
    c = ck.Clip("idle", IDLE_SEC, loop=True)
    frames = int(round(IDLE_SEC * ck.FPS))
    last = len(CHAIN) - 1
    for f in range(frames + 1):
        t = f / ck.FPS
        pose = {}
        for name in CHAIN:
            k = CHAIN_POS[name]
            ph = 2.0 * math.pi * t / IDLE_SEC - IDLE_LAG * k
            amp = (1.0 + 0.6 * k / last) * (0.6 if name == "head" else 1.0)
            pose[name] = local_rot(bend=IDLE_BEND * amp * math.sin(ph), twist=IDLE_LUFF * amp * math.sin(2.0 * ph + 0.9),
                                   bone=name, sway=IDLE_SWAY * amp * math.sin(ph - 1.2))
        bob = 0.04 * math.sin(2.0 * math.pi * t / IDLE_SEC + math.pi)
        st = 16.0 * math.sin(2.0 * math.pi * 2.0 * t / IDLE_SEC)
        pose_keys(c, t, pose, body=(0.0, bob, 0.0), streamer=st)
    return c


def build_ready() -> ck.Clip:
    c = ck.Clip("ready", READY_SEC)  # she gathers: the S draws in and the head rears, then she snaps taut
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
    aft_rear = {n: local_rot(bend=-0.8, twist=5.0, bone=n) for n in AFT}
    aft_lash = {n: local_rot(bend=1.0, twist=-6.0, bone=n) for n in AFT}
    return keyed(c, [(0.0, {}, (0, 0, 0), (0, 0, 0), 0.0),
                     (0.3, compose(rear, aft_rear), (0, 0.04, -0.02), (0, 0, 0), 12.0),
                     (ATTACK_CONTACT, compose(lash, aft_lash), (0, -0.04, 0.16), (0, 0, 0), -14.0),
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
    """The S draws in tight, the head tucked down before her body, held, then opens."""
    c = ck.Clip("defend", DEFEND_SEC)
    tight = chain_curl(5.0, 3.0, head=22.0)
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
    high = chain_curl(-1.5, 0.5, head=-10.0)

    def gust(t: float) -> dict:
        return wave_pose(t, VICTORY_SEC, bend=0.9, twist=8.0, cycles=1.0, lag=0.7)

    return keyed(c, [(0.0, {}, (0, 0, 0), (0, 0, 0), 0.0, gust), (0.8, high, (0, 0.18, 0), (0, 0, 0), 20.0, gust),
                     (1.5, high, (0, 0.14, 0), (0, 0, 0), -16.0, gust), (VICTORY_SEC, {}, (0, 0, 0), (0, 0, 0), 0.0)])


FURLED = chain_curl(8.0, 4.0, head=30.0)  # furled: the S wound tight, the head tucked (rise's start, dismiss's end)


def build_rise() -> ck.Clip:
    """The unfurling, in place (the stage lifts her out of the water): from furled tight, the S opens, the head
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
    """The furling: the head lifts once, then the S winds tight and the head bows and tucks; it ends furled (the
    stage sinks her)."""
    c = ck.Clip("dismiss", DISMISS_SEC)
    return keyed(c, [(0.0, {}, (0, 0, 0), (0, 0, 0), 0.0),
                     (0.35, chain_curl(-1.0, 0.8, head=-8.0), (0, 0.04, 0), (0, 0, 0), 12.0),
                     (0.8, FURLED, (0, 0, 0), (0, 0, 0), -6.0), (DISMISS_SEC, FURLED, (0, 0, 0), (0, 0, 0), 0.0)])


SPECIAL_ANGLE = 17.0  # Flare Line: the taut line rises this steeply toward the foes
SPECIAL_TAIL = np.array([0.0, 1.05, -0.2])  # and is anchored here, low behind her mark
RELEASE_LIFT = 0.15  # let go, she lifts a little as the line swings back into the S


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
    if abs(om - math.pi) < 1e-3:  # opposite: turn through the S's plane
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
    """Flare Line: the S winds in (a held breath: the head rears back over her, the tail curls under), then the whole kite-string is pulled taut in one rising line
    toward the foes and burns end to end (the contact), holds, trembling, and is let go back into the S. The
    pull and the release turn each bone's direction (not its Euler angles), so the line unrolls cleanly."""
    c = ck.Clip("special", SPECIAL_SEC)
    line, loc = special_line()
    wound = chain_curl(-9.0, 9.0, head=10.0)  # the S drawn in: the head rears back over her, the tail curls under
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
            st = 18.0 - 30.0 * u
        else:
            u = float(ck.smoothstep(let0, SPECIAL_SEC, t))
            pose = directions_pose({n: slerp_dir(line[n], rest_dirs[n], u) for n in line})
            body = tuple(np.asarray(loc) * (1 - u) + np.array([0.0, RELEASE_LIFT * math.sin(math.pi * u), 0.0]))
            st = -12.0 * (1 - u)
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


TAIL_HANG = 0.6  # the kite-tail at the tail's end undoes this much of its parent's turn: it hangs on its string
TAIL_LAG = 0.1


def hang_tail(c: ck.Clip) -> ck.Clip:
    """Keys the streamer bone so the kite-tail hangs: its own keyed flutter, turned back by TAIL_HANG of the tail
    end's world turn, TAIL_LAG behind (M3-CRB-008: it no longer swings out with every turn of the tail)."""
    own = ck.Clip("_own", c.length, loop=c.loop)
    own.keys["streamer"] = list(c.keys.get("streamer", []))
    c.keys["streamer"] = []
    frames = max(int(round(c.length * ck.FPS)), 1)
    for f in range(frames + 1):
        t = min(f / ck.FPS, c.length)
        s = t - TAIL_LAG
        s = s % c.length if c.loop else max(s, 0.0)
        G = world_turn(c, s, AFT[-1])
        L = ck.euler(*own.sample("streamer", t)[0])
        ang = math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(G) - 1.0) / 2.0))))
        ax = np.array([G[2, 1] - G[1, 2], G[0, 2] - G[2, 0], G[1, 0] - G[0, 1]])
        R = axis_angle(ax, -TAIL_HANG * ang) if ang > 1e-6 and np.linalg.norm(ax) > 1e-9 else np.eye(3)
        c.key("streamer", t, to_euler(R @ L))
    return c


RELEASE_SEC = 3.4  # M3-CRE-647: the held form's release (Ch20), its KO
RELEASE_ANGLE = 38.0  # the release's line climbs this steeply, away from the party (-z)
RELEASE_TAIL = np.array([0.0, 0.7, 1.4])  # the line's tail end as it opens, low in front of her mark
RELEASE_AWAY = np.array([0.0, 1.5, -0.6])  # and where the lift then carries her (metres: up, and back)


def build_release() -> ck.Clip:
    """M3-CRE-647, the held form's KO (vowbound.md, the final fight: giddy and proud). The kite's last flight: the S
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
    # the release flies its tail on the wind (no hang): its line climbs away with the tail end low in front
    return [hang_key(c) if c.name == "release" else hang_tail(hang_key(c)) for c in clips]


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
