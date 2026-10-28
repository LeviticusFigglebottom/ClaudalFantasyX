"""Asha's lantern-staff (no bpy), asha.md §2.1 / §4.1 #10: a dark hardwood shaft 1.95 m long and 3.2 cm
across, held in the right hand and rising 0.32 m above her head; a brass open cage lantern (6 ribs,
16 cm) at the top; five bell-shells on cords under the cage. Rigid on DEF-staff (under DEF-hand.R). ~2,000 triangles.

M2-CHR-515 (M1-QA-09: "the staff isn't gripped"): a shaft held upright with the arm at the side runs through the fist
across the palm, from the thumb side to the little finger, so the fingers can close round it. At rest the hand hangs,
so the staff is built upright and then turned about the grip into that line (`held_frame`, `to_held`): at rest it
points forward through the fist, and the clips pitch the hand (thumb up) to stand it upright again
(hero_clips.staff_hold). Toma's spear is built the same way (toma_props).
"""
from __future__ import annotations

import math

import numpy as np

from asha_mesh import Part, tube, uv_sphere

TAG_STAFF = 61
STAFF_R = 0.016  # m (at s = 1): the shaft's radius at the grip
HOLE_AT = 0.62  # the fist's hole: this far along the hand from the wrist (under the first finger bones)


def held_frame(lm, side: str, r_shaft: float) -> tuple:
    """(grip, R) for a shaft held in the fist: `grip` the hole's centre (palmar of the knuckle line by half the hand's
    thickness and the shaft's radius), R the rotation taking +z (upright) to the hole's line, towards the thumb."""
    hand = lm.hands[side]
    s = hand.side - hand.axis * float(hand.side @ hand.axis)
    s = s / np.linalg.norm(s)
    grip = hand.wrist + hand.axis * hand.length * HOLE_AT - hand.dorsal * (hand.thickness * 0.5 + r_shaft)
    z = np.array([0.0, 0.0, 1.0])
    v = np.cross(z, s)
    c = float(z @ s)
    vx = np.array([[0.0, -v[2], v[1]], [v[2], 0.0, -v[0]], [-v[1], v[0], 0.0]])
    R = np.eye(3) + vx + vx @ vx * (1.0 / (1.0 + c))
    return grip, R


def to_held(part: Part, grip: np.ndarray, R: np.ndarray) -> Part:
    """The part, built upright through `grip`, turned about it into the held line."""
    part.V = [grip + R @ (np.asarray(p, dtype=float) - grip) for p in part.V]
    return part


def staff(lm) -> Part:
    part = Part("Staff")
    S = lm.S
    grip, R = held_frame(lm, "R", STAFF_R * S)
    up = np.array([0.0, 0.0, 1.0])
    base = np.array([grip[0], grip[1], 0.012])
    top_z = float(lm.P("crown")[2]) + 0.32 * S
    L = top_z - base[2]
    e1 = np.array([1.0, 0.0, 0.0])  # the cage's cross-section axes
    e2 = np.array([0.0, 1.0, 0.0])
    down = -up
    fwd = np.array([0.0, -1.0, 0.0])
    shaft = np.array([base + up * L * t for t in np.linspace(0.0, 1.0, 22)])
    rad = STAFF_R * S * (1.0 - 0.12 * np.linspace(0, 1, 22))
    tube(part, shaft, rad, 14, "staff_wood", fwd, tags=TAG_STAFF, cap_end=True)
    # lantern cage: two rings and six ribs, sitting on the shaft's top
    cage_h = 0.16 * S
    c0 = base + up * (L - cage_h)
    for zf, rr in ((0.0, 0.035), (1.0, 0.022)):
        ring = np.array([c0 + up * cage_h * zf + (math.cos(a) * e1 + math.sin(a) * e2) * rr * S
                         for a in np.linspace(0, 2 * math.pi, 17)])
        tube(part, ring, 0.0032 * S, 6, "brass", up, tags=TAG_STAFF)
    for k in range(6):
        a = 2 * math.pi * k / 6
        d = math.cos(a) * e1 + math.sin(a) * e2
        rib = np.array([c0 + up * cage_h * t + d * (0.035 - 0.013 * t + 0.022 * math.sin(math.pi * t)) * S
                        for t in np.linspace(0, 1, 9)])
        tube(part, rib, 0.0025 * S, 5, "brass", d, tags=TAG_STAFF)
    # finial
    uv_sphere(part, c0 + up * (cage_h + 0.012 * S), 0.011 * S, 8, 5, "brass", axis_fwd=up, tags=TAG_STAFF)
    # five bell-shells on cords under the cage
    for k in range(5):
        a = 2 * math.pi * (k + 0.5) / 5
        d = math.cos(a) * e1 + math.sin(a) * e2
        top = c0 + d * 0.030 * S
        drop = (0.05 + 0.012 * (k % 3)) * S
        cord = np.array([top + down * drop * t for t in np.linspace(0, 1, 4)])
        tube(part, cord, 0.0011 * S, 4, "bone", d, tags=TAG_STAFF)
        bell_c = top + down * (drop + 0.010 * S)
        uv_sphere(part, bell_c, np.array([0.009, 0.013, 0.009]) * S, 10, 5, "bone", axis_fwd=down, tags=TAG_STAFF)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return to_held(part, grip, R)


def staff_bone(lm, length: float) -> tuple:
    """(head, tail) of DEF-staff: from the grip along the held shaft, towards its top."""
    grip, R = held_frame(lm, "R", STAFF_R * lm.S)
    return grip, grip + R @ np.array([0.0, 0.0, length])
