"""Warden Malcor Venn's halberd (no bpy), M4-A2P-051 (act2_ch14.md B09: "a heavy halberd, disciplined"): Toma's spear
construction (toma_props.spear: built upright through the right fist's hole and grounded, then turned into the held
line, M2-CHR-515) with a halberd's head: an ash shaft with the cord grip, the bronze ferrule and collar, a steel socket
with long langets, a crescent axe blade on the side away from his body, a short back spike opposite it and a narrow
top spike. The shaft and cord are `cloth` faces on Toma's atlas (build_stillguard moves them onto the brine-iron's
maps, as it does the spear's); the metal is `steel`, the fittings `bronze`. Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_mesh import Part, grid, tube
from asha_staff import held_frame, to_held
from toma_props import SPEAR_SHAFT_R, TAG_PROP, _blade_section

HEAD_L = 0.42  # m: the socket, the axe and the top spike over the shaft's end
LANGET_L = 0.10  # m: the socket's langets down the shaft
BLADE_H = 0.20  # m: the axe blade's height along the shaft
BLADE_REACH = (0.05, 0.11)  # m: the edge's reach out from the shaft at its tips, plus the bulge at its middle
BLADE_HORN = 0.04  # m: how far the blade's tips stand off the shaft (the crescent's horns)
BLADE_THICK = 0.005  # m: the blade's spine at the shaft, thinning to the edge
SPIKE_BACK = 0.10  # m: the back spike's length
SPIKE_TOP_W = 0.018  # m: the top spike's half-width at its widest


def halberd(lm, params: dict, cord_rect) -> Part:
    """`params`: `halberd_length_m` overall; `cord_rect` the grip binding's atlas rectangle (as Toma's spear)."""
    part = Part("Halberd")
    grip, R = held_frame(lm, "R", SPEAR_SHAFT_R)
    L = float(params["halberd_length_m"])
    upv = np.array([0.0, 0.0, 1.0])
    base = grip - upv * ((grip[2] - 0.006) / upv[2])
    fwd = np.array([0.0, -1.0, 0.0])
    side = np.array([-1.0, 0.0, 0.0])  # the axe faces out from his right side, as the spear's hook
    shaft_top = L - HEAD_L + 0.06
    n = 26
    shaft = np.array([base + upv * shaft_top * t for t in np.linspace(0.0, 1.0, n)])
    rad = SPEAR_SHAFT_R * (1.0 - 0.06 * np.linspace(0, 1, n))
    from toma_costume import ATLAS

    tube(part, shaft, rad, 12, "cloth", fwd, ATLAS["spear_shaft"], tags=TAG_PROP)
    g0, g1 = grip[2] - 0.20, grip[2] + 0.04  # the cord grip at the fist
    cord = np.array([base + upv * ((z - base[2]) / upv[2]) for z in np.linspace(g0, g1, 10)])
    tube(part, cord, SPEAR_SHAFT_R * 1.14, 12, "cloth", fwd, cord_rect, tags=TAG_PROP)
    tube(part, np.array([base, base + upv * 0.07]), SPEAR_SHAFT_R * 1.14, 12, "bronze", fwd, tags=TAG_PROP)
    s0 = base + upv * (shaft_top - 0.02)
    col = s0 - upv * (LANGET_L + 0.05)
    tube(part, np.array([col, col + upv * 0.05]), SPEAR_SHAFT_R * 1.2, 12, "bronze", fwd, tags=TAG_PROP)
    # the socket and its langets: a steel sleeve over the shaft's last LANGET_L, then the head's core
    tube(part, np.array([s0 - upv * LANGET_L, s0 + upv * 0.22]), np.array([SPEAR_SHAFT_R * 1.08, SPEAR_SHAFT_R * 0.9]),
         10, "steel", fwd, tags=TAG_PROP)
    # the axe: horizontal lens sections up the blade; the tips stand off the shaft (the horns), the middle bulges
    m = 12
    secs = []
    for k in range(m):
        t = k / (m - 1)
        bulge = math.sin(math.pi * t)
        inner = SPEAR_SHAFT_R + BLADE_HORN * (1.0 - bulge) ** 2
        outer = SPEAR_SHAFT_R + BLADE_REACH[0] + BLADE_REACH[1] * bulge ** 0.7
        c = s0 + upv * (0.01 + BLADE_H * t) + side * (0.5 * (inner + outer))
        secs.append(_blade_section(c, side, fwd, 0.5 * (outer - inner), BLADE_THICK * (0.6 + 0.4 * bulge)))
    grid(part, np.array(secs), "steel", closed_u=True, tags=TAG_PROP)
    # the back spike, opposite the axe, drooping a little
    b = s0 + upv * 0.12
    spike = np.array([b - side * SPIKE_BACK * t - upv * 0.03 * t * t for t in np.linspace(0.0, 1.0, 8)])
    tube(part, spike, np.linspace(0.010, 0.0015, len(spike)), 8, "steel", fwd, tags=TAG_PROP)
    # the top spike: a narrow leaf from the socket's top to the halberd's full length
    t0 = s0 + upv * 0.22
    top_l = L - (shaft_top - 0.02 + 0.22)
    secs = []
    for k in range(m):
        t = k / (m - 1)
        w = SPIKE_TOP_W * math.sin(math.pi * min(t * 1.4 + 0.1, 1.0)) ** 0.8 * (1.0 - t) ** 0.3 + 0.0015
        secs.append(_blade_section(t0 + upv * top_l * t, fwd, side, w, 0.0045 * (1.0 - 0.7 * t) + 0.0008))
    grid(part, np.array(secs), "steel", closed_u=True, tags=TAG_PROP)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return to_held(part, grip, R)
