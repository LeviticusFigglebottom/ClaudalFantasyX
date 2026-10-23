"""Rhen's props (no bpy), rhen.md §3-§4: Dace's diving lantern, the twin reef-hooks and the tether coil.

* **Lantern** (22 cm): a salt-glass globe (14 cm) in a brass frame, a top cap with a carry ring, a
  base, four ribs over the globe and a clip onto the strap. It sits on the right shoulder blade with
  its top above the shoulder line, so it reads as a bulb over one shoulder (rhen.md §2). Unlit by
  default; the light is the scene's (rhen.md §3: an OmniLight3D in dark places).
* **Reef-hooks** x2: 28 cm hooked steel blades on wrapped grips, crossed at the small of the back at
  30 deg each side, the grips past both hips (rhen.md §2). Two-sided flat blades.
* **Tether coil**: an 18 cm coil of rope (8 turns) on the left hip, hanging off the belt.

All rigid (build_rhen weights them to one bone each). UVs: the props are flat-shaded materials
(brass, salt_glass, steel), except the rope and the grips, which sample the cloth atlas. Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_costume import TAG_CLOTH, Fields, cast_last
from asha_mesh import Part, catmull_rom, grid, tube, uv_sphere

TAG_PROP = 61
PINNED = (0.0, 0.0, 0.0, 0.0)


def _pin(part: Part) -> Part:
    part.C = [PINNED] * len(part.V)
    return part


def back_point(fields: Fields, x: float, z: float, off: float) -> np.ndarray:
    """The point on the back (+Y) of the upper body at (x, z), `off` outside the field."""
    S = fields.lm.S
    O = np.array([[x, -0.05 * S, z]])
    D = np.array([[0.0, 1.0, 0.0]])
    fn = lambda Q: np.minimum(fields.upper(Q), fields.lower(Q)) - off  # noqa: E731
    r = cast_last(fn, O, D, 0.5 * S)[0]
    return O[0] + D[0] * r


def lantern(fields: Fields, params: dict) -> tuple[Part, np.ndarray]:
    """Returns the lantern and its globe centre."""
    lm = fields.lm
    S = lm.S
    part = Part("Lantern")
    gr = 0.5 * float(params["lantern_globe_d_m"]) * S
    height = float(params["lantern_height_m"]) * S
    acro = lm.side_pt("acromion", "R")
    x = float(acro[0]) * 0.55
    z = float(acro[2]) + 0.035 * S  # the globe's top stands about 10 cm above the shoulder line
    c = back_point(fields, x, z, 0.02 * S) + np.array([0.0, gr * 0.95, 0.0])
    up = np.array([0.0, 0.0, 1.0])
    uv_sphere(part, c, gr, 24, 14, "salt_glass", axis_fwd=up, tags=TAG_PROP)
    cap_h = (height - 2.0 * gr) * 0.55
    base_h = (height - 2.0 * gr) * 0.45
    # top cap: a short brass cylinder narrowing upward, and a carry ring
    top = c + up * gr * 0.92
    cap = np.array([top, top + up * cap_h * 0.6, top + up * cap_h])
    tube(part, cap, np.array([0.55 * gr, 0.45 * gr, 0.28 * gr]), 16, "brass", np.array([0.0, -1.0, 0.0]),
         cap_end=True, tags=TAG_PROP)
    ring_c = top + up * (cap_h + 0.018 * S)
    ang = np.linspace(0.0, 2 * math.pi, 17)
    ring = np.stack([ring_c + np.array([0.0, math.cos(a), math.sin(a)]) * 0.016 * S for a in ang])
    tube(part, ring, 0.0028 * S, 6, "brass", up, tags=TAG_PROP)
    # base: a wider cup under the globe
    bot = c - up * gr * 0.9
    base = np.array([bot + up * 0.004 * S, bot - up * base_h * 0.5, bot - up * base_h])
    tube(part, base, np.array([0.62 * gr, 0.66 * gr, 0.5 * gr]), 16, "brass", np.array([0.0, -1.0, 0.0]),
         cap_end=True, tags=TAG_PROP)
    # four ribs over the globe, base to cap
    for k in range(4):
        a = math.pi * 0.25 + k * math.pi * 0.5
        d = np.array([math.cos(a), math.sin(a), 0.0])
        pts = np.array([c + (d * math.sin(t) + up * math.cos(t)) * (gr + 0.003 * S)
                        for t in np.linspace(0.12 * math.pi, 0.9 * math.pi, 10)])
        tube(part, pts, 0.0035 * S, 5, "brass", d, tags=TAG_PROP)
    # the clip onto the strap: a brass plate between the base and the back
    clip = np.array([bot - up * base_h * 0.5, bot - up * base_h * 0.5 - np.array([0.0, gr, 0.0])])
    tube(part, clip, 0.006 * S, 6, "brass", up, tags=TAG_PROP)
    return _pin(part), c


def _hook(part: Part, start: np.ndarray, d: np.ndarray, n: np.ndarray, grip_len: float, blade_len: float,
          S: float, grip_rect) -> None:
    """One reef-hook from the grip's butt along `d`; the blade's hook curls toward `n` (in the blade
    plane spanned by d and n), and the blade's flat faces look along cross(d, n)."""
    flat = np.cross(d, n)
    flat /= np.linalg.norm(flat)
    # grip: a wrapped tube with a brass collar at the guard
    g = np.array([start + d * grip_len * t for t in np.linspace(0.0, 1.0, 6)])
    u0, v0, u1, v1 = grip_rect
    tube(part, g, 0.0135 * S, 10, "cloth", n, uv_rect=grip_rect, cap_end=False, tags=TAG_CLOTH)
    tube(part, np.array([start - d * 0.004 * S, start]), 0.0145 * S, 10, "steel", n, cap_end=True, tags=TAG_PROP)
    gd = start + d * grip_len
    tube(part, np.array([gd - d * 0.006 * S, gd + d * 0.006 * S]), 0.017 * S, 10, "brass", n, tags=TAG_PROP)
    # blade spine: straight, then curling 150 deg into the hook
    straight = blade_len * 0.72
    r_hook = 0.032 * S
    pts = [gd + d * straight * t for t in np.linspace(0.0, 1.0, 8)]
    base = gd + d * straight
    centre = base + n * r_hook
    for t in np.linspace(0.0, 1.0, 9)[1:]:
        a = t * math.radians(150.0)
        pts.append(centre - n * r_hook * math.cos(a) + d * r_hook * math.sin(a))
    C = catmull_rom(np.array(pts), 22)
    T = np.gradient(C, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
    side = np.cross(flat, T)  # in the blade plane, across the blade
    side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-12)
    k = np.linspace(0.0, 1.0, len(C))
    w = (0.034 - 0.026 * k ** 1.5) * S  # blade width tapering to the point
    edge = C - side * (w * 0.5)[:, None]  # the cutting edge on the inside of the curl
    back = C + side * (w * 0.5)[:, None]
    th = 0.0022 * S
    for sgn, flip in ((1.0, False), (-1.0, True)):
        P = np.stack([edge + flat * sgn * th * 0.3, C + flat * sgn * th, back + flat * sgn * th], axis=1)
        grid(part, P, "steel", tags=TAG_PROP, flip=flip)
    _ = (u0, v0, u1, v1)


def reef_hooks(fields: Fields, params: dict, grip_rect) -> Part:
    lm = fields.lm
    S = lm.S
    part = Part("ReefHooks")
    z = float(lm.P("waist")[2]) - 0.035 * S
    c = back_point(fields, 0.0, z, 0.03 * S)
    a = math.radians(float(params["hook_angle_deg"]))
    blade = float(params["hook_blade_m"]) * S
    grip = 0.12 * S
    total = grip + blade * 0.85
    for k, sx in enumerate((1.0, -1.0)):
        # the grip at one hip, the blade rising across the back to the other side
        d = np.array([-sx * math.cos(a), 0.0, math.sin(a)])
        start = c - d * total * 0.5 + np.array([0.0, 0.012 * S * (k - 0.5) * 2.0, 0.0])
        n = np.array([0.0, 0.0, 1.0]) - d * d[2]  # the hook curls upward (away from the body's axis)
        n /= np.linalg.norm(n)
        _hook(part, start, d, n, grip, blade, S, grip_rect)
    return _pin(part)


def rope_coil(fields: Fields, params: dict, rect) -> Part:
    """The tether coil hanging on the left hip: `rope_turns` loops, slightly offset, in the YZ plane."""
    lm = fields.lm
    S = lm.S
    part = Part("RopeCoil")
    z = float(lm.P("waist")[2]) - 0.075 * S
    O = np.array([[0.0, 0.01 * S, z]])
    D = np.array([[1.0, 0.0, 0.0]])
    r = cast_last(lambda Q: fields.lower(Q) - 0.018 * S, O, D, 0.5 * S)[0]
    R = 0.5 * float(params["rope_coil_diameter_m"]) * S - 0.008 * S
    rope_r = 0.0058 * S
    turns = int(params["rope_turns"])
    rng = np.random.default_rng(int(params["seed"]) + 5)
    for t in range(turns):
        x = r + rope_r + t * rope_r * 0.55
        rr = R * (1.0 + 0.04 * (t - turns / 2) / turns) + rng.uniform(-0.003, 0.003) * S
        centre = np.array([x, 0.01 * S + rng.uniform(-0.004, 0.004) * S, z - 0.03 * S])
        ang = np.linspace(0.0, 2 * math.pi, 29)
        sag = 0.012 * S
        ring = np.stack([centre + np.array([0.0, math.cos(q) * rr, math.sin(q) * rr - sag * (1 - math.sin(q)) * 0.5])
                         for q in ang])
        u0, v0, u1, v1 = rect
        tube(part, ring, rope_r, 6, "cloth", np.array([1.0, 0.0, 0.0]),
             uv_rect=(u0, v0 + (v1 - v0) * t / turns, u1, v0 + (v1 - v0) * (t + 1) / turns), tags=TAG_CLOTH)
    return _pin(part)
