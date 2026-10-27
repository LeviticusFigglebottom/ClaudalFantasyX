"""Rhen's props (no bpy), rhen.md §3-§4: Dace's diving lantern and the two reef-hooks.

* **Lantern** (22 cm): a salt-glass globe (14 cm across, material `salt_glass`) in a brass frame
  (base cup, cap, four ribs, a carry ring, a clip to the strap), worn high on the right shoulder
  blade so the globe breaks the shoulder line from the front (rhen.md §2). Unlit by default; the
  Godot side adds the oil-lamp light. Rigid on the chest bone (build_rhen).
* **Reef-hooks** x2: dark-steel blades 28 cm long that curl into a hook, wrapped teal grips, crossed
  in an X at the small of the back, the grips sticking out past both hips at 30 degrees.

~4,000 + ~2,400 triangles. Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_mesh import Part, catmull_rom, frames_along, grid, tube, uv_sphere

TAG_PROP = 62
HOOK_ANGLE_DEG = 34.0  # rhen.md §2: 30 deg each side; a little steeper so the X reads in profile


def _ring(part: Part, c: np.ndarray, ax: np.ndarray, R: float, r: float, mat: str, n: int = 24, m: int = 6,
          uv=(0.0, 0.0, 0.1, 0.1)) -> None:
    e1 = np.cross(ax, [0.0, 0.0, 1.0] if abs(ax[2]) < 0.9 else [1.0, 0.0, 0.0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(ax, e1)
    t = np.linspace(0.0, 2 * math.pi, n + 1)
    C = c + np.outer(np.cos(t), e1) * R + np.outer(np.sin(t), e2) * R
    tube(part, C, r, m, mat, ax, uv, tags=TAG_PROP)


def _lathe(part: Part, c: np.ndarray, ax: np.ndarray, profile: list, mat: str, n: int = 24, uv=(0.0, 0.0, 0.1, 0.1),
           flip: bool = False) -> None:
    """A surface of revolution: profile = [(radius, height along ax), ...] from bottom to top."""
    e1 = np.cross(ax, [1.0, 0.0, 0.0] if abs(ax[0]) < 0.9 else [0.0, 1.0, 0.0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(ax, e1)
    ang = 2 * math.pi * np.arange(n) / n
    P = np.zeros((len(profile), n, 3))
    for j, (r, h) in enumerate(profile):
        P[j] = c + ax * h + (np.outer(np.cos(ang), e1) + np.outer(np.sin(ang), e2)) * r
    grid(part, P[::-1], mat, uv, closed_u=True, tags=TAG_PROP, flip=flip)


def lantern(anchor: np.ndarray, normal: np.ndarray, lm, height: float) -> Part:
    """Hung from the strap point `anchor` (outward `normal`), the globe above it."""
    part = Part("Lantern")
    S = lm.S
    out = normal / np.linalg.norm(normal)
    up = np.array([0.0, 0.0, 1.0])
    up = up - (up @ out) * out
    up /= np.linalg.norm(up)
    globe_r = 0.07 * S * height / 0.22
    # the globe's centre: out from the strap by its radius plus the frame, and lifted so its top
    # clears the shoulder line by a few centimetres
    top_target = float(lm.P("acromion")[2] + 0.11 * S)
    c = anchor + out * (0.8 * globe_r)
    c[2] = max(c[2], top_target - globe_r)
    # glass globe, slightly taller than wide
    uv_sphere(part, c, np.array([globe_r * 0.96, globe_r * 1.04, globe_r * 0.96]), 20, 12, "salt_glass",
              axis_fwd=up, uv_rect=(0.0, 0.0, 1.0, 1.0), tags=TAG_PROP)
    base_h = c - up * globe_r * 0.80
    # base cup and cap (brass, open lathed shells)
    _lathe(part, base_h, up, [(0.40 * globe_r, -0.30 * globe_r), (0.62 * globe_r, -0.20 * globe_r),
                              (0.66 * globe_r, 0.0), (0.62 * globe_r, 0.10 * globe_r), (0.58 * globe_r, 0.14 * globe_r)],
           "brass")
    _lathe(part, base_h, up, [(0.0, -0.31 * globe_r), (0.40 * globe_r, -0.30 * globe_r)], "brass")
    cap_b = c + up * globe_r * 0.80
    _lathe(part, cap_b, up, [(0.55 * globe_r, -0.12 * globe_r), (0.60 * globe_r, 0.0), (0.42 * globe_r, 0.22 * globe_r),
                             (0.18 * globe_r, 0.38 * globe_r), (0.14 * globe_r, 0.48 * globe_r), (0.0, 0.50 * globe_r)],
           "brass")
    # four ribs over the globe, and a band round its middle
    e1 = np.cross(up, out)
    e1 /= np.linalg.norm(e1)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        d = math.cos(a) * e1 + math.sin(a) * out
        pts = []
        for t in np.linspace(-0.82, 0.82, 11):
            ph = t * math.pi / 2
            pts.append(c + up * math.sin(ph) * globe_r * 1.04 + d * math.cos(ph) * globe_r * 1.0)
        tube(part, np.array(pts), 0.0028 * S, 6, "brass", out, (0.0, 0.0, 0.1, 0.1), tags=TAG_PROP)
    _ring(part, c, up, globe_r * 1.0, 0.0030 * S, "brass", n=28)
    # carry ring on the cap and a clip down to the strap
    _ring(part, cap_b + up * (0.50 * globe_r + 0.016 * S), e1, 0.016 * S, 0.0022 * S, "brass", n=16)
    clip = np.array([base_h - up * 0.30 * globe_r, base_h - up * 0.45 * globe_r - out * 0.3 * globe_r,
                     anchor + out * 0.004 * S])
    tube(part, catmull_rom(clip, 8), 0.0035 * S, 6, "brass", e1, (0.0, 0.0, 0.1, 0.1), tags=TAG_PROP)
    part.globe_centre = c
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part


def _blade(part: Part, root: np.ndarray, d: np.ndarray, n_side: np.ndarray, length: float, S: float) -> None:
    """A flat, tapered steel blade from `root` along `d` that curls back into a hook at its end;
    `n_side` is the blade's flat normal."""
    e = np.cross(n_side, d)
    e /= np.linalg.norm(e)
    pts = []
    m = 18
    for k in range(m):
        t = k / (m - 1)
        s = t * length
        curl = max(0.0, (t - 0.68) / 0.32)
        ang = curl * math.pi * 0.95
        R = 0.045 * S
        if curl > 0:
            s0 = 0.68 * length
            p = root + d * (s0 + R * math.sin(ang)) + e * (R * (1 - math.cos(ang)))
        else:
            p = root + d * s
        pts.append(p)
    C = np.array(pts)
    T = np.gradient(C, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    W = np.cross(n_side, T)
    W /= np.linalg.norm(W, axis=1, keepdims=True)
    widths = np.array([0.020, 0.022, 0.021, 0.019, 0.018, 0.017, 0.016, 0.015, 0.014, 0.013, 0.012, 0.011, 0.010,
                       0.009, 0.008, 0.006, 0.004, 0.0015]) * S
    th = 0.0022 * S
    # a lens-shaped section: thick spine, thin edge (4 points round)
    sec = [(0.0, th), (1.0, 0.0), (0.0, -th), (-0.35, 0.0)]
    P = np.zeros((m, len(sec), 3))
    for k in range(m):
        for i, (a, b) in enumerate(sec):
            P[k, i] = C[k] + W[k] * a * widths[k] * 0.5 + n_side * b
    grid(part, P, "steel", (0.0, 0.0, 0.1, 0.1), closed_u=True, tags=TAG_PROP)


def reef_hooks(anchor: np.ndarray, hip_x: float, lm, length: float) -> Part:
    """Two hooks crossed at the small of the back (`anchor`), grips out past both hips."""
    part = Part("ReefHooks")
    for _side, p, _end, _d in reef_hook_parts(anchor, hip_x, lm, length):
        part.extend(p)
    return part


def reef_hook_parts(anchor: np.ndarray, hip_x: float, lm, length: float) -> list:
    """M2-CHR-513: the two hooks as separate parts, each on its own bone so Rhen can draw them:
    [(side, part, grip end, grip -> blade unit direction)], the left-hip grip ("L") first."""
    out = []
    S = lm.S
    back = np.array([0.0, 1.0, 0.0])
    for k, sgn in enumerate((1.0, -1.0)):
        part = Part(f"ReefHook.{'L' if sgn > 0 else 'R'}")
        # the grip end sits past the hip on side sgn, 30 degrees below horizontal toward the centre
        a = math.radians(HOOK_ANGLE_DEG)
        d = np.array([-sgn * math.cos(a), 0.0, math.sin(a)])  # grip -> blade, up and across
        cross = anchor + back * (0.012 * S + 0.008 * S * k)
        grip_end = cross - d * (hip_x + 0.06 * S - abs(cross[0])) / math.cos(a)
        grip_end = grip_end + back * 0.01 * S
        grip_top = grip_end + d * 0.12 * S
        u0, v0, u1, v1 = (0.0, 0.80, 0.25, 0.90)
        tube(part, np.linspace(grip_end, grip_top, 6), 0.0135 * S, 10, "cloth", back, (u0, v0, u1, v1), tags=TAG_PROP,
             cap_end=False)
        # pommel and guard (steel)
        uv_sphere(part, grip_end - d * 0.006 * S, 0.016 * S, 10, 6, "steel", axis_fwd=-d, tags=TAG_PROP)
        _ring(part, grip_top, d, 0.016 * S, 0.004 * S, "steel", n=14)
        _blade(part, grip_top + d * 0.004 * S, d, back, length * S, S)
        part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
        out.append(("L" if sgn > 0 else "R", part, grip_end, d))
    return out
