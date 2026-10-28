"""Liss's launcher (no bpy), act1_npcs.md §2.3-§2.4 #7 and §2.10.

A boxy hand-cranked launcher slung at her right hip (story sheet: "a boxy shape with a crank handle that reads well
in silhouette"): a copper box 22 cm long (front to back) x 14 cm tall x 12 cm wide with two iron bands, a brass crank
drum and a 10 cm crank on its outer (right) face whose handle points forward, an 18 cm stubby iron barrel forward
with a brass muzzle ring, a sling lug on top and the sight: a brass cup on top holding an 8 mm bound-light point
(`glimmer_bound`, steady). It is a rigid prop on its own bone (`DEF-launcher`, a child of the hips, build_liss),
**2 cm off the thigh at rest** (M1-CHR-14: the box's inner face is laid that far out from the widest point of the
shipped right thigh skin over the box's height), so a stride does not drive the thigh into it.

Materials: `copper`, `brass`, `iron` (metals; write_materials) and `glimmer` (emissive). Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_mesh import Part, tube, uv_sphere

TAG_PROP = 62
BAND_W = 0.012  # m: the iron bands round the box
BAND_PROUD = 0.0025  # m out of the box's faces
DRUM_R = 0.032  # m: the crank drum on the outer face
BARREL_R = (0.026, 0.022)  # m at the box and at the muzzle
DROP_BELOW_HIP = 0.17  # m (at s = 1): the box's centre below the hip joint, slung on the upper thigh: its top
# stays under the hanging right hand's wrist, so the forearm passes over it and the hand rests against its outer face
GAP_MARGIN = 0.0005  # m: placed this much past the gap (the gap is a floor)
FORWARD = 0.035  # m (at s = 1): the box's centre forward of the thigh's mid-line (the tails hang behind it)


def _box(part: Part, c, ax, ay, az, half, mat: str) -> None:
    hx, hy, hz = half
    k = {}
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                k[(sx, sy, sz)] = c + ax * hx * sx + ay * hy * sy + az * hz * sz
    faces = [((1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1)), ((-1, 1, -1), (-1, -1, -1), (-1, -1, 1), (-1, 1, 1)),
             ((1, 1, -1), (-1, 1, -1), (-1, 1, 1), (1, 1, 1)), ((-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)),
             ((-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)), ((-1, 1, -1), (1, 1, -1), (1, -1, -1), (-1, -1, -1))]
    uv = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    for f in faces:
        ids = [part.add_v(k[q], tag=TAG_PROP) for q in f]
        part.add_f(ids, uv, mat)


def _cylinder(part: Part, a: np.ndarray, b: np.ndarray, r0: float, r1: float, n: int, mat: str, up) -> None:
    """A capped cylinder from a to b (radius r0 at a, r1 at b)."""
    C = np.array([a, a + (b - a) * 1e-3, b - (b - a) * 1e-3, b])
    R = np.array([1e-4, r0, r1, 1e-4])
    tube(part, C, R, n, mat, np.asarray(up, dtype=float), tags=TAG_PROP)


def place(lm, thigh_skin: np.ndarray, params: dict) -> dict:
    """The box's frame at rest: centre, axes (fwd = -Y, out = her right = -X, up = +Z) and half extents, its inner
    face `launcher_thigh_gap_m` outside the widest point of the right thigh skin over the box's height."""
    S = lm.S
    L, H, Wd = (float(v) * S for v in params["launcher_box_m"])
    hip = lm.side_pt("hip", "R")
    zc = float(hip[2]) - DROP_BELOW_HIP * S
    band = thigh_skin[np.abs(thigh_skin[:, 2] - zc) < 0.5 * H + 0.01 * S]
    x_out = float(band[:, 0].min())  # her right is -X
    y_mid = float(np.median(band[:, 1]))
    gap = float(params["launcher_thigh_gap_m"])  # m, not scaled: the sheet's 2 cm is a clearance
    centre = np.array([x_out - gap - 0.5 * Wd, y_mid - FORWARD * S, zc])
    frame = {"centre": centre, "fwd": np.array([0.0, -1.0, 0.0]), "out": np.array([-1.0, 0.0, 0.0]),
             "up": np.array([0.0, 0.0, 1.0]), "half": np.array([0.5 * L, 0.5 * Wd, 0.5 * H]), "x_out": x_out}
    # the band's widest point is not always the nearest skin (the thigh bulges past the band's ends): step out
    # until the whole box clears every given skin point by the gap
    for _ in range(8):
        short = gap + GAP_MARGIN - box_gap(thigh_skin, frame)
        if short <= 0.0:
            break
        frame["centre"] = frame["centre"] + frame["out"] * short
    return frame


def launcher(lm, frame: dict, params: dict, anchor: np.ndarray | None = None, strap_rect=None) -> Part:
    """The launcher at `frame`; with `anchor` (a point on her right hip, outside the trousers' waistband) its sling:
    two leather straps from the box's top up to the hip, on the same prop bone (`strap_rect`: the leather island
    of the costume atlas, material `cloth`)."""
    S = lm.S
    part = Part("Launcher")
    c, fwd, out, up = frame["centre"], frame["fwd"], frame["out"], frame["up"]
    hl, hw, hh = frame["half"]
    _box(part, c, fwd, out, up, (hl, hw, hh), "copper")
    # two iron bands round the box (front-back at a quarter from each end)
    for f in (-0.55, 0.55):
        _box(part, c + fwd * f * hl, fwd, out, up, (0.5 * BAND_W * S, hw + BAND_PROUD * S, hh + BAND_PROUD * S), "iron")
    # the crank drum and the crank on the outer face; the handle points forward
    face = c + out * hw
    _cylinder(part, face, face + out * 0.018 * S, DRUM_R * S, DRUM_R * S, 16, "brass", up)
    hub = face + out * 0.02 * S
    arm_len = float(params["launcher_crank_m"]) * S
    elbow = hub + fwd * arm_len * 0.92 + up * arm_len * 0.38
    tube(part, np.array([hub, hub + (elbow - hub) * 0.5, elbow]), 0.006 * S, 8, "iron", out, tags=TAG_PROP)
    _cylinder(part, elbow, elbow + out * 0.045 * S, 0.0095 * S, 0.0095 * S, 10, "brass", up)
    # the barrel forward, from the box's front face at its lower middle, and the muzzle ring
    b0 = c + fwd * hl - up * 0.15 * hh
    b1 = b0 + fwd * float(params["launcher_barrel_m"]) * S
    _cylinder(part, b0 - fwd * 0.01 * S, b1, BARREL_R[0] * S, BARREL_R[1] * S, 16, "iron", up)
    tt = np.linspace(0.0, 2 * math.pi, 17)
    e1, e2 = up, np.cross(fwd, up)
    ring = b1[None, :] - fwd * 0.012 * S + np.outer(np.cos(tt), e1) * (BARREL_R[1] + 0.003) * S + \
        np.outer(np.sin(tt), e2) * (BARREL_R[1] + 0.003) * S
    tube(part, ring, 0.004 * S, 8, "brass", fwd, tags=TAG_PROP)
    # the sling lug on top, at the back
    lug = c + up * hh - fwd * 0.6 * hl
    tt = np.linspace(0.0, math.pi, 9)
    arc = lug[None, :] + np.outer(np.cos(tt), fwd) * 0.018 * S + np.outer(np.sin(tt), up) * 0.016 * S
    tube(part, arc, 0.0035 * S, 6, "iron", out, tags=TAG_PROP)
    # the sight: a brass cup on top at the front, the glimmer point in it
    cup = c + up * hh + fwd * 0.55 * hl
    _cylinder(part, cup, cup + up * 0.012 * S, 0.010 * S, 0.012 * S, 12, "brass", fwd)
    r = 0.0005 * float(params["bound_light_mm"]["sight"])
    uv_sphere(part, cup + up * (0.012 * S + 0.5 * r), r, 10, 6, "glimmer", axis_fwd=up, tags=TAG_PROP)
    if anchor is not None:
        for f in (-0.45, 0.45):
            a = c + up * hh + fwd * f * hl + out * 0.25 * hw
            b = anchor + fwd * f * 0.6 * hl
            mid = 0.5 * (a + b) + out * 0.012 * S
            line = np.array([a, 0.5 * (a + mid), mid, 0.5 * (mid + b), b])
            sx = [(1.0, 0.22)] * len(line)  # a flat band: 2.6 cm wide, 5 mm thick
            tube(part, line, 0.013 * S, 6, "cloth", fwd, uv_rect=strap_rect or (0, 0, 1, 1), tags=TAG_PROP,
                 scale_xy=[(s0, s1) for s0, s1 in sx])
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part


def box_gap(P: np.ndarray, frame: dict) -> float:
    """The least distance from points P (the thigh skin) to the launcher's box."""
    q = P - frame["centre"]
    local = np.stack([q @ frame["fwd"], q @ frame["out"], q @ frame["up"]], axis=1)
    d = np.linalg.norm(np.maximum(np.abs(local) - frame["half"], 0.0), axis=1)
    return float(d.min()) if len(d) else float("inf")
