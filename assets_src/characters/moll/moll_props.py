"""Moll's props (no bpy), hadric_moll.md §3: the brine-iron and the round shield.

* **The brine-iron**: the Order's branding iron on a 2.1 m ash haft (3.2 cm, a red-lacquer band 8 cm long under the
  socket, a bronze ferrule at the foot), carried upright as an office. Its head is the Level forged in iron: a ring
  22 cm across of 2.4 cm square stock, crossed by a bar along its diameter that runs 4 cm past the ring each side, on
  a socket with two rivets. The ring faces forward (the Level reads from the front). It is built upright through the
  right fist's hole and grounded, then turned into the held line (asha_staff.held_frame / to_held, as Asha's staff
  and Toma's spear: the clips pitch the hand to stand it upright again, M2-CHR-515), rigid on DEF-iron under
  DEF-hand.R. One material, `iron`, on its own 1K maps (IRON_ATLAS): the ring's lower third is the ember island,
  whose emission (`ember_dull`) is a material parameter, off by default.
* **The shield**: a Stillguard round shield 0.62 m across, domed 6 cm, on Toma's shield builder (toma_props.shield,
  one smooth field instead of his thirteen scutes, a coarser grid): red lacquer with a bronze rim and boss, the Level
  painted in `bone` (moll_textures). It rides the left forearm's outer side (DEF-shield under DEF-forearm.L), pushed
  out until its back clears the forearm, the hand and the bracer.

Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

import toma_props
from asha_mesh import Part, tube, uv_sphere
from asha_staff import held_frame, to_held

TAG_PROP = 63
# the iron's own 1K atlas (u0, v0, u1, v1): the shaft's islands run along v
IRON_ATLAS = {
    "haft": (0.0, 0.0, 0.5, 1.0),
    "band": (0.5, 0.0, 0.625, 0.5),
    "ferrule": (0.625, 0.0, 0.75, 0.5),
    "socket": (0.75, 0.0, 0.875, 0.5),
    "rivet": (0.875, 0.0, 1.0, 0.5),
    "ring": (0.5, 0.5, 1.0, 0.75),  # v along the ring from its top, round through the bottom (v 0.5 of the island)
    "bar": (0.5, 0.75, 1.0, 0.875),
}
EMBER_SHARE = 1.0 / 3.0  # the ring's lower third shows the heat-tint (moll_textures paints that span of the island)
HAFT_RINGS = 34
HAFT_SIDES = 12
RING_SEGS = 28
SOCKET_M = 0.075  # m: the iron socket over the haft's top
FERRULE_M = 0.06
SHIELD_RINGS = 12  # toma_props.shield's grid for a 0.62 m disc (the default is Toma's 0.92 m)
SHIELD_SEGS = 40
SHIELD_BACK_AT_RIM = toma_props.SHIELD_BACK_DEPTH  # m: the shield's back behind its rim plane at the rim ...
SHIELD_BACK_RISE = 0.03  # ... and how much nearer the rim plane it comes at the centre (toma_props.shield's cone)
SHIELD_UP_TILT = 0.0  # the shield's up runs along the forearm (the bar of its Level is level when the arm hangs)


def iron_radius(params: dict) -> float:
    return 0.5 * float(params["iron_haft_diameter_m"])


def cap_start(part: Part, ids: np.ndarray, centre: np.ndarray, rect) -> None:
    """Close a tube's first ring with a fan (asha_mesh.tube caps only its end)."""
    c = part.add_v(centre, tag=TAG_PROP)
    n = ids.shape[1]
    for i in range(n):
        a, b = int(ids[0, i]), int(ids[0, (i + 1) % n])
        part.add_f((b, a, c), [(rect[0], rect[1])] * 3, "iron")


def iron(lm, params: dict) -> Part:
    part = Part("Iron")
    r = iron_radius(params)
    grip, R = held_frame(lm, "R", r)
    up = np.array([0.0, 0.0, 1.0])
    fwd = np.array([0.0, -1.0, 0.0])
    side = np.array([1.0, 0.0, 0.0])
    base = np.array([grip[0], grip[1], 0.006])
    L = float(params["iron_haft_m"])
    # the haft, a little slimmer toward the top
    shaft = np.array([base + up * L * t for t in np.linspace(0.0, 1.0, HAFT_RINGS)])
    rad = r * (1.0 - 0.06 * np.linspace(0.0, 1.0, HAFT_RINGS))
    tube(part, shaft, rad, HAFT_SIDES, "iron", fwd, IRON_ATLAS["haft"], tags=TAG_PROP)
    # the bronze ferrule at the foot, the lacquer band under the socket
    ids = tube(part, np.array([base, base + up * FERRULE_M]), r * 1.12, HAFT_SIDES, "iron", fwd,
               IRON_ATLAS["ferrule"], tags=TAG_PROP)
    cap_start(part, ids, base, IRON_ATLAS["ferrule"])
    band = float(params["iron_band_m"])
    top = base + up * L
    b0 = top - up * (SOCKET_M * 0.7 + band)
    tube(part, np.array([b0, b0 + up * band]), r * 1.06, HAFT_SIDES, "iron", fwd, IRON_ATLAS["band"], tags=TAG_PROP)
    # the socket: an iron collar over the haft's top, tapering into the ring
    s0 = top - up * SOCKET_M * 0.7
    tube(part, np.array([s0, s0 + up * SOCKET_M * 0.6, s0 + up * SOCKET_M]),
         np.array([r * 1.18, r * 1.12, r * 0.8]), 10, "iron", fwd, IRON_ATLAS["socket"], tags=TAG_PROP, cap_end=True)
    for sgn in (-1.0, 1.0):  # two rivets through the socket, side to side
        uv_sphere(part, s0 + up * SOCKET_M * 0.3 + side * sgn * r * 1.18, 0.0045, 6, 4, "iron", axis_fwd=side * sgn,
                  uv_rect=IRON_ATLAS["rivet"], tags=TAG_PROP)
    # the Level: a ring of square stock, its plane facing forward, sitting on the socket
    stock = float(params["iron_stock_m"])
    half = stock / math.sqrt(2.0)  # a 4-sided tube's radius for a square of side `stock`
    Rr = 0.5 * float(params["iron_ring_m"]) - 0.5 * stock  # to the stock's middle
    c = top + up * (SOCKET_M * 0.3 + Rr + 0.5 * stock - 0.004)
    ang = math.pi * 0.5 - 2.0 * math.pi * np.linspace(0.0, 1.0, RING_SEGS + 1)  # from the top, round through the bottom
    ring = np.array([c + (side * math.cos(a) + up * math.sin(a)) * Rr for a in ang])
    tube(part, ring, half, 4, "iron", fwd, IRON_ATLAS["ring"], tags=TAG_PROP)
    past = float(params["iron_bar_past_m"])
    bar = np.array([c + side * x for x in np.linspace(-(Rr + 0.5 * stock + past), Rr + 0.5 * stock + past, 6)])
    ids = tube(part, bar, half, 4, "iron", fwd, IRON_ATLAS["bar"], tags=TAG_PROP, cap_end=True)
    cap_start(part, ids, bar[0], IRON_ATLAS["bar"])
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return to_held(part, grip, R)


def iron_bone(lm, params: dict, length: float) -> tuple[np.ndarray, np.ndarray]:
    """(head, tail) of DEF-iron: from the fist's grip along the held haft, towards its head."""
    grip, R = held_frame(lm, "R", iron_radius(params))
    return grip, grip + R @ np.array([0.0, 0.0, length])


def shield_frame(lm, params: dict, arm: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(centre, out, up) of the shield's rim plane on the left forearm: `out` the forearm's dorsal side, `up` along the
    forearm toward the elbow; pushed out until its back (toma_props.shield's cone: SHIELD_BACK_AT_RIM behind the rim
    plane at the rim, SHIELD_BACK_RISE nearer at the centre) clears every point of `arm` (the left forearm and hand
    skin, the bracer) under its footprint by `shield_forearm_gap_m`."""
    el, wr = lm.side_pt("elbow", "L"), lm.side_pt("wrist", "L")
    ax = (el - wr) / np.linalg.norm(el - wr)
    hand = lm.hands["L"]
    out = hand.dorsal - (hand.dorsal @ ax) * ax
    out /= np.linalg.norm(out)
    up = ax * math.cos(SHIELD_UP_TILT) + np.cross(out, ax) * math.sin(SHIELD_UP_TILT)
    R = 0.5 * float(params["shield_diameter_m"])
    c0 = wr + (el - wr) * 0.5
    q = arm - c0
    h = q @ out
    rr = np.linalg.norm(q - np.outer(h, out), axis=1)
    near = rr < R + 0.01
    back = SHIELD_BACK_AT_RIM - SHIELD_BACK_RISE * (1.0 - np.clip(rr / R, 0.0, 1.0))
    need = float((h[near] + back[near]).max()) + float(params["shield_forearm_gap_m"])
    return c0 + out * need, out, up


def shield(centre: np.ndarray, out: np.ndarray, up: np.ndarray, params: dict) -> Part:
    part = toma_props.shield(centre, out, up, params, rings=SHIELD_RINGS, segs=SHIELD_SEGS)
    part.name = "Shield"
    return part
