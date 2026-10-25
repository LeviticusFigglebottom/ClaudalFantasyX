"""Ysolde's props (no bpy), ysolde.md §3 and §4.1 #8-#11: the folding lacquer book, the ink-guards, the Level-pin
and the wedding ring.

* **The book**: an accordion of 12 lacquered panels (24 x 12 cm, 3 mm thick), shut into a 24 x 12 x 4 cm block held
  in the right hand. Its broad face sits on the palm side **1.2 cm proud of the palm surface** (the probe's
  `prop_in_body` stays clear outside the grip bones; Asha's staff lesson). One mesh with one shape, `book_fan`
  (`book_fan_points`): 0 shut, 1 fanned into a 160 degree arc of radius 24 cm about the corner the hand holds, the
  panels standing on edge in a fan with their gold script facing out. It rides the prop bone `DEF-book` under
  `DEF-hand.R` (build_ysolde). Panels 1-11 carry a Lamptongue glyph each, panel 12 (out when shut) the Glyph Trace
  (ysolde_textures, from motifs/glyphs.json).
* **The ink-guards**: four curved sheaths on the left index, middle, ring and little fingers (the thumb is bare),
  each over the distal phalanx and 4.5 cm past the fingertip in a downward (palmar) curve of radius 6 cm, tapering
  from 1.2 cm wide at the nail to a blunt 1.5 mm point. The back of each is lacquer with a gold hairline down its
  spine (the `props` atlas), the palm side bare silver (`silver`). Each is rigid on its finger's distal bone.
* **The Level-pin**: a 16 cm silver pin through the knot from front-left to back-right, rising 20 degrees toward the
  back; its head is the Order's Level, a 3 cm ring crossed by one bar. Head-rigid.
* **The ring**: a plain gold band on the right ring finger (a proposal to Narrative, ysolde.md §12 Q1). Rigid on the
  finger's first bone.

Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_mesh import Part, grid, tube

TAG_PROP = 62
# props atlas islands (u0, v0, u1, v1), v down; ysolde_textures paints them
PANEL_FACE = (0.0, 0.0, 0.625, 0.47)  # 4 x 6 cells: rows 0-2 the panels' fronts, rows 3-5 their backs
PANEL_GRID = (4, 6)
PANEL_EDGE = (0.625, 0.0, 0.75, 0.05)
GUARD = (0.625, 0.05, 1.0, 0.15)
BOOK_GAP = 0.00036  # m between the shut panels (the silk hinges' thickness)
BOOK_START = 0.02  # m along the hand from the wrist to the book's near end
GUARD_AROUND = 10
GUARD_ROWS = 12
GUARD_FINGERS = ("f_index", "f_middle", "f_ring", "f_pinky")
GUARD_START = 0.1  # of the distal phalanx, from its joint, where the sheath begins
GUARD_CLEAR = 0.0012  # m over the finger's radius
RING_AROUND = 12
RING_TUBE = 4


def panel_cell(k: int, back: bool) -> tuple[float, float, float, float]:
    cols, rows = PANEL_GRID
    u0, v0, u1, v1 = PANEL_FACE
    cw, ch = (u1 - u0) / cols, (v1 - v0) / rows
    r = k // cols + (rows // 2 if back else 0)
    c = k % cols
    return (u0 + c * cw, v0 + r * ch, u0 + (c + 1) * cw, v0 + (r + 1) * ch)


def book_frame(lm, params: dict, hand_skin: np.ndarray | None = None) -> dict:
    """The shut book's frame in the right hand (bind pose): `x` along the hand (the panels' 24 cm), `y` toward the
    thumb (their 12 cm), `z` out of the palm (the stack), and `o` the corner the hand holds (the fan's pivot): the
    near end, the thumb side, on the face toward the palm. With `hand_skin` (the hand's skin vertices) the face sits
    `book_grip_offset_m` past the farthest skin under the book's footprint (palm or curled fingers), so the gap is
    measured on the mesh, not on the landmark hand's thickness."""
    hand = lm.hands["R"]
    x = hand.axis / np.linalg.norm(hand.axis)
    z = -hand.dorsal / np.linalg.norm(hand.dorsal)
    y = np.cross(z, x)
    if y @ hand.side < 0:
        y = -y
    palm = hand.wrist + x * hand.length * 0.30 + z * hand.thickness * 0.5
    L, W, _T = (float(v) for v in params["book_panel_m"])
    o = palm + z * float(params["book_grip_offset_m"]) + x * (BOOK_START - hand.length * 0.30) + y * 0.5 * W
    if hand_skin is not None and len(hand_skin):
        q = hand_skin - o
        a, b = q @ x, q @ y
        under = (a > -0.01) & (a < L + 0.01) & (b < 0.01) & (b > -W - 0.01)
        if under.any():
            o = o + z * (float((q[under] @ z).max()) + float(params["book_grip_offset_m"]))
    return {"x": x, "y": y, "z": z, "o": o, "palm": palm}


def _box(part: Part, c0: np.ndarray, ex: np.ndarray, ey: np.ndarray, ez: np.ndarray, uv_front, uv_back) -> list:
    """A closed box from corner c0 spanning ex, ey, ez (8 corners, 6 quads, outward winding). The face along +ez
    (front) and -ez (back) take their cells; the four edges the shared edge island. Returns the vertex ids."""
    ids = [part.add_v(c0 + a * ex + b * ey + c * ez, tag=TAG_PROP) for c in (0, 1) for b in (0, 1) for a in (0, 1)]

    def rect_uv(r):
        u0, v0, u1, v1 = r
        return [(u0, v1), (u1, v1), (u1, v0), (u0, v0)]

    e = rect_uv(PANEL_EDGE)
    centre = c0 + 0.5 * (ex + ey + ez)
    # corner index = a + 2 b + 4 c: the +ez face, the -ez face, then the four edges
    for q, uv in (((4, 5, 7, 6), rect_uv(uv_front)), ((0, 2, 3, 1), rect_uv(uv_back)), ((0, 1, 5, 4), e),
                  ((2, 6, 7, 3), e), ((0, 4, 6, 2), e), ((1, 3, 7, 5), e)):
        pts = [part.V[ids[i]] for i in q]
        if np.cross(pts[1] - pts[0], pts[2] - pts[0]) @ (np.mean(pts, axis=0) - centre) < 0:
            q, uv = q[::-1], uv[::-1]
        part.add_f([ids[i] for i in q], uv, "props")
    return ids


def book(lm, params: dict, hand_skin: np.ndarray | None = None) -> tuple[Part, np.ndarray, dict]:
    """The shut book and its `book_fan` target positions (one row per vertex)."""
    f = book_frame(lm, params, hand_skin)
    x, y, z, o = f["x"], f["y"], f["z"], f["o"]
    L, W, T = (float(v) for v in params["book_panel_m"])
    n = int(params["book_panels"])
    fan = math.radians(float(params["book_fan_deg"]))
    part = Part("Book")
    fan_pts = []
    for k in range(n):
        dz = k * (T + BOOK_GAP)
        c0 = o + z * dz - y * W  # the panel's corner at the pivot's far side
        first = len(part.V)
        _box(part, c0, x * L, y * W, z * T, panel_cell(k, False), panel_cell(k, True))
        # the fan: each panel turns about the pivot (the held corner) by its share of the arc, about the stack axis
        ang = -0.5 * fan + fan * k / max(n - 1, 1)
        ca, sa = math.cos(ang), math.sin(ang)
        for v in part.V[first:]:
            q = v - o
            a, b, c = q @ x, q @ y, q @ z
            a2, b2 = ca * a - sa * b, sa * a + ca * b
            fan_pts.append(o + x * a2 + y * b2 + z * c)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    centre = o + x * 0.5 * L - y * 0.5 * W + z * 0.5 * n * (T + BOOK_GAP)
    return part, np.array(fan_pts), {**f, "centre": centre}


def _section(c: np.ndarray, side: np.ndarray, up: np.ndarray, hw: float, hh: float) -> np.ndarray:
    a = 2 * math.pi * np.arange(GUARD_AROUND) / GUARD_AROUND
    return c + np.outer(np.cos(a) * hw, side) + np.outer(np.sin(a) * hh, up)


def ink_guard(finger, params: dict) -> Part:
    """One sheath: over the distal phalanx, then 4.5 cm on past the tip in a palmar curve, tapering to a point."""
    j2, tip = finger.joints[2], finger.joints[3]
    d0 = (tip - j2) / np.linalg.norm(tip - j2)
    up = finger.dorsal - (finger.dorsal @ d0) * d0
    up /= np.linalg.norm(up)
    side = np.cross(d0, up)
    ext = float(params["guard_extension_m"])
    R = float(params["guard_curve_radius_m"])
    w0 = 0.5 * float(params["guard_width_m"])
    w1 = 0.5 * float(params["guard_point_m"])
    r_tip = float(finger.radius[3]) + GUARD_CLEAR
    r_mid = float(finger.radius[2]) + GUARD_CLEAR
    start = j2 + (tip - j2) * GUARD_START
    L_on = float(np.linalg.norm(tip - start))
    rows = []
    n_on = 4
    for i in range(n_on):
        t = i / (n_on - 1)
        c = start + (tip - start) * t
        hh = r_mid + (r_tip - r_mid) * t
        rows.append(_section(c, side, up, max(w0, hh), hh))
    for i in range(1, GUARD_ROWS - n_on + 1):
        s = ext * i / (GUARD_ROWS - n_on)
        th = s / R
        c = tip + d0 * (R * math.sin(th)) - up * (R * (1.0 - math.cos(th)))
        tang = d0 * math.cos(th) - up * math.sin(th)
        nup = np.cross(side, tang)
        k = s / ext
        hw = w0 + (w1 - w0) * k ** 0.8
        hh = (r_tip + (w1 - r_tip) * k ** 0.7) * (1.0 - 0.45 * k)  # the point flattens a little as it tapers
        rows.append(_section(c, side, nup, max(hw, w1), max(hh, 0.6 * w1)))
    P = np.array(rows)
    part = Part("Guard")
    u0, v0, u1, v1 = GUARD
    ids = grid(part, P, "props", tags=TAG_PROP, closed_u=True,
               uv_fn=lambda j, i: (u0 + (u1 - u0) * j / (len(rows) - 1), v0 + (v1 - v0) * i / GUARD_AROUND))
    # the open root end inward round the finger is unseen (inside the sheath's mouth); cap the point
    tipc = part.add_v(P[-1].mean(axis=0) + (P[-1].mean(axis=0) - P[-2].mean(axis=0)) * 0.6, tag=TAG_PROP)
    for i in range(GUARD_AROUND):
        a, b = ids[-1, i], ids[-1, (i + 1) % GUARD_AROUND]
        part.add_f((a, b, tipc), [(u1, v0)] * 3, "props")
    # winding outward: an unflipped grid faces cross(du, dv); flip every face if it points in
    mid = len(rows) // 2
    pa, pb, pc = P[mid, 0], P[mid, 1], P[mid + 1, 0]
    if np.cross(pb - pa, pc - pa) @ (pa - P[mid].mean(axis=0)) < 0:
        part.F = [f[::-1] for f in part.F]
        part.UV = [uv[::-1] for uv in part.UV]
    # the palm side is bare silver, the back lacquer with the gold spine (props atlas)
    centre_line = P.mean(axis=1)
    for fi, f in enumerate(part.F):
        cen = np.mean([part.V[i] for i in f], axis=0)
        row = min(int(np.argmin(np.linalg.norm(centre_line - cen, axis=1))), len(rows) - 1)
        nrm_up = up if row < n_on else np.cross(side, P[min(row + 1, len(rows) - 1)].mean(axis=0) -
                                                    P[max(row - 1, 0)].mean(axis=0))
        nrm_up = nrm_up / max(np.linalg.norm(nrm_up), 1e-12)
        if (cen - centre_line[row]) @ nrm_up < -0.25 * np.linalg.norm(cen - centre_line[row]):
            part.M[fi] = "silver"
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    _ = L_on
    return part


def ink_guards(lm, params: dict) -> list[tuple[Part, str]]:
    """(part, distal bone) per guarded finger of the left hand."""
    hand = lm.hands["L"]
    fingers = {fg.name: fg for fg in hand.fingers}
    return [(ink_guard(fingers[nm], params), f"DEF-{nm}.03.L") for nm in GUARD_FINGERS]


def _torus(part: Part, c: np.ndarray, axis: np.ndarray, R: float, r: float, n: int, m: int, mat: str) -> None:
    axis = axis / np.linalg.norm(axis)
    e1 = np.cross(axis, np.array([0.0, 0.0, 1.0]) if abs(axis[2]) < 0.9 else np.array([1.0, 0.0, 0.0]))
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(axis, e1)
    P = np.zeros((n, m, 3))
    for i in range(n):
        a = 2 * math.pi * i / n
        d = math.cos(a) * e1 + math.sin(a) * e2
        for j in range(m):
            b = 2 * math.pi * j / m
            P[i, j] = c + d * (R + r * math.cos(b)) + axis * (r * math.sin(b))
    ids = np.zeros((n, m), dtype=int)
    for i in range(n):
        for j in range(m):
            ids[i, j] = part.add_v(P[i, j], tag=TAG_PROP)
    for i in range(n):
        for j in range(m):
            q = [ids[i, j], ids[(i + 1) % n, j], ids[(i + 1) % n, (j + 1) % m], ids[i, (j + 1) % m]]
            a, b, cc = P[i, j], P[(i + 1) % n, j], P[(i + 1) % n, (j + 1) % m]
            out = P[i, j] - (c + (P[i, j] - c - axis * ((P[i, j] - c) @ axis)) / max(
                np.linalg.norm(P[i, j] - c - axis * ((P[i, j] - c) @ axis)), 1e-12) * R)
            if np.cross(b - a, cc - a) @ out < 0:
                q = q[::-1]
            part.add_f(q, [(0.0, 0.0)] * 4, mat)


def ring(lm, params: dict) -> tuple[Part, str]:
    """The plain gold band on the right ring finger's first phalanx."""
    hand = lm.hands["R"]
    fg = {f.name: f for f in hand.fingers}["f_ring"]
    a, b = fg.joints[0], fg.joints[1]
    c = a + (b - a) * 0.45
    part = Part("Ring")
    r_f = float(fg.radius[0] * 0.55 + fg.radius[1] * 0.45)
    _torus(part, c, b - a, r_f + 0.0012, 0.0011, RING_AROUND, RING_TUBE, "gold")
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part, "DEF-f_ring.01.R"


def level_pin(params: dict, knot: dict) -> Part:
    """The Level-pin through the knot: front-left to back-right, rising toward the back."""
    c, up = knot["centre"], knot["up"]
    rise = math.radians(float(params["pin_rise_deg"]))
    h = np.array([-1.0, 1.0, 0.0]) / math.sqrt(2.0)  # toward her back-right
    d = h * math.cos(rise) + np.array([0.0, 0.0, 1.0]) * math.sin(rise)
    L = float(params["pin_length_m"])
    ring_d = float(params["pin_ring_m"])
    a = c - d * 0.42 * L + up * 0.01
    b = c + d * 0.58 * L + up * 0.01
    part = Part("Pin")
    C = np.array([a + (b - a) * t for t in np.linspace(0.0, 1.0, 8)])
    rad = np.linspace(0.0021, 0.0009, 8)
    tube(part, C, rad, 8, "silver", up, (0.0, 0.0, 0.1, 0.1), tags=TAG_PROP, cap_end=True)
    # the Level: a ring crossed by one bar, standing at the pin's front end
    rc = a - d * 0.5 * ring_d
    axis = np.cross(d, np.array([0.0, 0.0, 1.0]))
    axis /= np.linalg.norm(axis)
    _torus(part, rc, axis, 0.5 * ring_d - 0.0016, 0.0016, 16, 6, "silver")
    bar = np.cross(axis, d)
    bar /= np.linalg.norm(bar)
    tube(part, np.array([rc - bar * 0.5 * ring_d * 0.92, rc + bar * 0.5 * ring_d * 0.92]), 0.0013, 6, "silver", d,
         (0.0, 0.0, 0.1, 0.1), tags=TAG_PROP)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part
