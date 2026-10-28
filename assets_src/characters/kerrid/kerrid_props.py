"""Kerrid's anchor-cleaver (no bpy), kerrid.md §4.1 #11 and §9.

A ship's anchor fluke made into a hauling and breaking tool: a forged iron haft with a tarred-rope grip (room for two
hands, the wrapped left above the right), a straight-backed blade widening to the **fluke**, a broad, slightly spooned
palm 26 cm wide whose tip turns into the **bill**, a blunt hook 9 cm toward the edge side, and the anchor's shackle
**ring** (11 cm, 2 cm stock) hanging on a forged eye at the haft's end (`ring_on`: one switch, for Narrative's open
question on the ring, kerrid.md §12 Q3). Thickness 1.2 cm at the spine and 3 mm at the edge.

The cleaver is built in its own frame: origin on the haft's axis at the right fist's grip point, +x down the haft
toward the blade's tip, +y toward the edge side, +z the blade's normal. build_kerrid places it across the back on its
prop bone (`DEF-cleaver`, under DEF-spine.003: the ring above the left shoulder, the fluke past the right hip, 12 mm or
more off the cape's outer surface) and also writes it alone, unskinned, in this frame (`kerrid_cleaver.glb`) for the
battle actor's hand instance (a BoneAttachment3D on DEF-hand.R: the grip point at the attachment, 1.2 cm out from the
fist's centre line). UVs are on the 1K props atlas (kerrid_textures.cleaver_atlas): the blade's two faces, the haft
and its grip wrap, the ring and the eye. Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_mesh import Part, grid, tube

TAG_PROP = 62
# the 1K props atlas (u0, v0, u1, v1), v down
ATLAS = {"blade_a": (0.0, 0.0, 1.0, 0.36), "blade_b": (0.0, 0.36, 1.0, 0.72), "edge": (0.0, 0.72, 1.0, 0.76),
         "haft": (0.0, 0.78, 0.5, 0.88), "grip": (0.5, 0.78, 1.0, 0.88), "ring": (0.0, 0.90, 0.5, 1.0),
         "eye": (0.5, 0.90, 1.0, 1.0)}
GRIP_R = 0.34  # of the haft's length from the eye: where the right fist closes (the blade end of the grip)
GRIP_L = 0.14  # ... and the left (wrapped) hand above it
HAFT_R = 0.017  # m: the forged haft's radius
WRAP_R = 0.0195  # m: over the tarred-rope grip
STATIONS = 22  # blade sections along its length
ACROSS = 7  # points across one face of a section
FIST_HALF = 0.045  # m: half a closed fist's width along the haft


def outline(cp: dict, s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The blade's back (spine) and edge offsets across the blade (m, +y = the edge side) at s = 0 (the haft) .. 1
    (the tip): a straight back, the edge widening to the fluke's palm, the bill hooking toward the edge at the tip and
    the back curving round to meet it."""
    w0 = float(cp["blade_width_haft_m"])
    wf = float(cp["fluke_width_m"])
    hook = float(cp["bill_hook_m"])
    grow = np.clip(s / 0.82, 0.0, 1.0)
    grow = grow * grow * (3.0 - 2.0 * grow)
    edge = w0 + (wf - w0) * grow
    tip = np.clip((s - 0.86) / 0.14, 0.0, 1.0)
    edge = edge + hook * np.sin(0.5 * math.pi * tip) ** 1.5  # the bill
    back = 0.10 * wf * tip ** 2  # the back rounds over into the tip
    return back, edge


def cleaver(cp: dict) -> tuple[Part, dict]:
    """The cleaver in its own frame (see the module doc). Returns (part, key points in that frame)."""
    part = Part("Cleaver")
    haft = float(cp["haft_m"])
    blade = float(cp["blade_m"])
    t_sp, t_ed = float(cp["spine_thick_m"]), float(cp["edge_thick_m"])
    x0 = -GRIP_R * haft  # the eye end of the haft (the grip point is the origin)
    xb = x0 + haft  # where the blade starts
    # --- the blade: closed sections, the top face (+z) then back along the bottom face (-z)
    s = np.linspace(0.0, 1.0, STATIONS)
    back, edge = outline(cp, s)
    secs = []
    for k in range(STATIONS):
        ys = back[k] + (edge[k] - back[k]) * np.linspace(0.0, 1.0, ACROSS)
        frac = (ys - back[k]) / max(edge[k] - back[k], 1e-6)
        th = t_sp + (t_ed - t_sp) * frac ** 0.8
        spoon = 0.006 * math.sin(math.pi * min(max((s[k] - 0.45) / 0.55, 0.0), 1.0)) * np.sin(math.pi * frac)
        x = xb + blade * s[k]
        top = np.stack([np.full(ACROSS, x), ys, 0.5 * th + spoon], axis=1)
        bot = np.stack([np.full(ACROSS, x), ys[::-1], (-0.5 * th + spoon)[::-1]], axis=1)
        secs.append(np.concatenate([top, bot]))
    P = np.array(secs)
    n_c = P.shape[1]
    ua0, va0, ua1, va1 = ATLAS["blade_a"]
    ub0, vb0, ub1, vb1 = ATLAS["blade_b"]

    def uv_blade(j: int, i: int) -> tuple[float, float]:
        u = j / (STATIONS - 1)
        if i < ACROSS:
            return ua0 + (ua1 - ua0) * u, va0 + (va1 - va0) * i / (ACROSS - 1)
        return ub0 + (ub1 - ub0) * u, vb0 + (vb1 - vb0) * (i - ACROSS) / (ACROSS - 1)

    grid(part, P, "cleaver", closed_u=True, tags=TAG_PROP, uv_fn=lambda j, i: uv_blade(j, i % n_c))
    # cap the tip
    c = part.add_v(P[-1].mean(axis=0), tag=TAG_PROP)
    base = len(part.V) - 1 - n_c
    for i in range(n_c):
        part.add_f((base + i, base + (i + 1) % n_c, c), [ATLAS["edge"][:2]] * 3, "cleaver")
    # --- the haft (forged iron) and the tarred-rope grip
    fwd = np.array([0.0, 0.0, 1.0])
    hx = np.linspace(x0, xb + 0.02, 10)
    tube(part, np.stack([hx, np.full(10, 0.025), np.zeros(10)], axis=1), HAFT_R, 10, "cleaver", fwd, ATLAS["haft"],
         tags=TAG_PROP)
    # from 2 cm above the upper (left) hand to the right fist's lower edge: the binding ends clear of the palms
    g0 = (GRIP_L - GRIP_R) * haft - FIST_HALF - float(cp["grip_wrap_above_fist_m"])
    g1 = FIST_HALF
    gx = np.linspace(g0, g1, 12)
    tube(part, np.stack([gx, np.full(12, 0.025), np.zeros(12)], axis=1), WRAP_R, 12, "cleaver", fwd, ATLAS["grip"],
         tags=TAG_PROP)
    # --- the forged eye at the haft's end, and the shackle ring on it (in the blade's plane)
    eye_c = np.array([x0 - 0.014, 0.025, 0.0])
    t = np.linspace(0.0, 2 * math.pi, 13)
    eye = eye_c[None, :] + np.stack([0.014 * np.cos(t), np.zeros_like(t), 0.014 * np.sin(t)], axis=1)
    tube(part, eye, 0.0055, 6, "cleaver", np.array([0.0, 1.0, 0.0]), ATLAS["eye"], tags=TAG_PROP)
    ring_c = None
    if cp.get("ring_on", True):
        ro, rs = float(cp["ring_outer_m"]), float(cp["ring_stock_m"])
        R = 0.5 * (ro - rs)
        ring_c = np.array([x0 - 0.028 - R, 0.025, 0.0])
        t = np.linspace(0.0, 2 * math.pi, 29)
        ring = ring_c[None, :] + np.stack([R * np.cos(t), R * np.sin(t), np.zeros_like(t)], axis=1)
        tube(part, ring, 0.5 * rs, 8, "cleaver", fwd, ATLAS["ring"], tags=TAG_PROP)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    keys = {"grip_r": np.array([0.0, 0.025, 0.0]), "grip_l": np.array([(GRIP_L - GRIP_R) * haft, 0.025, 0.0]),
            "eye": eye_c, "ring": ring_c if ring_c is not None else eye_c, "tip": np.array([xb + blade, 0.0, 0.0]),
            "haft_axis_y": 0.025, "blade_start": xb, "length": float(cp["overall_m"])}
    return part, keys


def frame_from(ring_w: np.ndarray, tip_w: np.ndarray, normal_w: np.ndarray, keys: dict,
               edge_hint: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """(R, t): the rotation (columns = the cleaver frame's x, y, z in world) and translation that put the ring at
    `ring_w` with the blade running toward `tip_w`, its flat facing along `normal_w` (either way), the edge side on
    the side of `edge_hint`."""
    x = tip_w - ring_w
    x /= np.linalg.norm(x)
    z = normal_w - (normal_w @ x) * x
    z /= np.linalg.norm(z)
    y = np.cross(z, x)
    if edge_hint is not None and y @ edge_hint < 0.0:  # a half turn about the blade's axis: still a rotation
        y, z = -y, -z
    R = np.stack([x, y, z], axis=1)
    t = ring_w - R @ keys["ring"]
    return R, t


def place(part: Part, R: np.ndarray, t: np.ndarray) -> Part:
    out = Part(part.name, V=[R @ v + t for v in part.V], F=list(part.F), UV=list(part.UV), M=list(part.M),
               C=list(part.C), T=list(part.T))
    return out
