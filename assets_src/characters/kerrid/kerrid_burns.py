"""The rope-burns (no bpy), kerrid.md §3: Kerrid's death-wounds from the stair's hand-line.

A spiral scar from the heel of each palm to the elbow, as a rope runs when it is held while it slides: `burn_turns`
(3) turns per forearm, the band `burn_width_m` (2.2-3.0 cm, varying along it) wide with ragged edges, plus the palm
burn across the four finger pads and the heel of the hand. One generator, used twice:

* kerrid_textures paints it into the body maps (the albedo lifted and desaturated, the raised glossy relief in the
  normal map and the ORM roughness, and the `burn_glow` emission mask), and
* build_kerrid puts the VFX sockets on it (six per forearm along the spiral, one per palm: kerrid.md §9).

`age` (0 = Kerrid's: never healed, sharp edges; 1 = an old healed scar, soft and narrower) lets the same generator
draw the healed rope scars a Corrow fisher might carry. Deterministic (noise from fixed seeds).
"""
from __future__ import annotations

import math

import numpy as np

PHASE0 = {"L": 0.4, "R": 2.1}  # rad: where each spiral starts round the forearm at the palm heel
DIR = {"L": 1.0, "R": -1.0}  # the rope ran the same way down both hands: mirrored turns
FOREARM_R = 0.075  # m (at s = 1): radial reach of the forearm region
PALM_HEEL = (0.0, 0.32)  # shares of the hand's length: the heel of the hand
PALM_PADS = (0.58, 1.05)  # ... and the finger pads


def forearm_coords(lm, P: np.ndarray, side: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """(d, ang, near, L): distance up the forearm from the wrist (m), the angle round it, a mask of points on the
    forearm, and the forearm's length."""
    el, wr = lm.side_pt("elbow", side), lm.side_pt("wrist", side)
    L = float(np.linalg.norm(el - wr))
    ax = (el - wr) / L
    d = (P - wr) @ ax
    radial = P - wr - np.outer(d, ax)
    ref = np.array([0.0, 0.0, 1.0]) - ax[2] * ax
    ref /= np.linalg.norm(ref)
    ang = np.arctan2(radial @ np.cross(ax, ref), radial @ ref)
    near = (np.linalg.norm(radial, axis=1) < FOREARM_R * lm.S) & (d > -0.02 * lm.S) & (d < 1.02 * L)
    return d, ang, near, L


def _noise(x: np.ndarray, y: np.ndarray, seed: int) -> np.ndarray:
    """A cheap smooth deterministic noise in [-1, 1] (sums of seeded sines)."""
    rng = np.random.default_rng(seed)
    out = np.zeros_like(x)
    for k in range(5):
        fx, fy, ph = rng.uniform(20.0, 90.0), rng.uniform(1.0, 4.0), rng.uniform(0.0, 2 * math.pi)
        out += np.sin(fx * x + np.round(fy) * y + ph) / (k + 1)
    return out / 2.3


def spiral_band(lm, P: np.ndarray, side: str, kparams: dict, age: float = 0.0) -> np.ndarray:
    """0..1 coverage of the forearm spiral at the points P."""
    turns = float(kparams["burn_turns"])
    w0, w1 = (float(v) * lm.S for v in kparams["burn_width_m"])
    d, ang, near, L = forearm_coords(lm, P, side)
    pitch = L / turns
    phase = DIR[side] * ang - PHASE0[side]
    # distance along the arm to the nearest turn's centre line
    dd = (d - pitch * phase / (2 * math.pi)) % pitch
    dd = np.minimum(dd, pitch - dd)
    u = np.clip(d / L, 0.0, 1.0)
    width = w0 + (w1 - w0) * (0.5 + 0.5 * np.sin(2 * math.pi * 1.7 * u + 0.6))
    width = width * (1.0 - 0.35 * age)
    rag = (0.18 + 0.1 * age) * width * _noise(d / lm.S, ang, 71 + (side == "R"))
    half = 0.5 * width / math.cos(math.atan(pitch / (2 * math.pi * 0.04 * lm.S))) + rag
    soft = (0.0008 + 0.006 * age) * lm.S
    m = np.clip((half - dd) / soft + 0.5, 0.0, 1.0)
    return m * near * (d < 0.97 * L)


def palm_band(lm, P: np.ndarray, side: str, age: float = 0.0) -> np.ndarray:
    """0..1 coverage of the palm burn (the heel of the hand and the finger pads, on the palm side)."""
    h = lm.hands[side]
    q = P - h.wrist
    a = (q @ h.axis) / h.length
    b = (q @ h.side) / (0.5 * h.width)
    c = (q @ h.dorsal) / h.thickness
    palm = np.clip(-c * 3.0, 0.0, 1.0)
    across = np.clip((1.15 - np.abs(b)) * 4.0, 0.0, 1.0)
    rag = 0.05 * _noise(a * 6.0, b * 3.0, 83 + (side == "R"))
    zone = np.maximum(np.clip((PALM_HEEL[1] + rag - a) * 18.0, 0.0, 1.0) * np.clip((a + 0.06) * 18.0, 0.0, 1.0),
                      np.clip((a - PALM_PADS[0] - rag) * 18.0, 0.0, 1.0) * np.clip((PALM_PADS[1] - a) * 18.0, 0.0, 1.0))
    return zone * palm * across * (1.0 - 0.4 * age) * (np.abs(c) < 1.6)


def burn_mask(lm, P: np.ndarray, kparams: dict, age: float = 0.0) -> np.ndarray:
    out = np.zeros(len(P))
    for sd in ("L", "R"):
        out = np.maximum(out, spiral_band(lm, P, sd, kparams, age))
        out = np.maximum(out, palm_band(lm, P, sd, age))
    return out


def socket_points(lm, side: str, kparams: dict, n: int = 6) -> list[np.ndarray]:
    """`n` points on the spiral's centre line over the forearm (VFX-burn.<side>.1 .. n, wrist to elbow), on the skin
    surface radius (the body's arm field is not needed: a socket is an anchor, not a surface point)."""
    turns = float(kparams["burn_turns"])
    el, wr = lm.side_pt("elbow", side), lm.side_pt("wrist", side)
    L = float(np.linalg.norm(el - wr))
    ax = (el - wr) / L
    ref = np.array([0.0, 0.0, 1.0]) - ax[2] * ax
    ref /= np.linalg.norm(ref)
    e2 = np.cross(ax, ref)
    pitch = L / turns
    out = []
    for k in range(n):
        d = L * (0.08 + 0.84 * k / max(n - 1, 1))
        phase = 2 * math.pi * d / pitch
        ang = (phase + PHASE0[side]) * DIR[side]
        r = (0.030 + 0.012 * d / L) * lm.S
        out.append(wr + ax * d + (ref * math.cos(ang) + e2 * math.sin(ang)) * r)
    return out


def palm_point(lm, side: str) -> np.ndarray:
    h = lm.hands[side]
    return h.wrist + h.axis * (0.45 * h.length) - h.dorsal * (0.55 * h.thickness)
