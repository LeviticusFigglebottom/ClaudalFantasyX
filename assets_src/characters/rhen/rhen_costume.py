"""Rhen's costume as procedural cloth panels (no bpy), rhen.md §3-§4 and §9.

Same method as Asha's (asha_costume): every garment is a pattern grid of (azimuth, height) or
(position along a limb, angle) whose rows are ray-cast from an axis onto the body field plus a
fitting offset, and the grid is also the garment's island in the 2K cloth atlas (the UVs *are* the
flat pattern; rhen_textures draws the masks on the same charts). Pieces, inner to outer:

1. Undershirt: a sleeveless wrap vest (sand cotton), a V at the front, under the jacket.
2. Sea-jacket: short (it ends at the lower ribs), open at the front, a 3 cm stand-up collar, and
   only a **left** sleeve, which runs into the gauntlet; the right armhole is a raw rolled edge.
3. Diving gauntlet: oiled leather from mid-forearm over the wrist to the knuckles (fingerless).
4. Trousers to the knee (canvas): a pelvis band and two loose leg tubes.
5. Belt with a buckle, and the tether coil (8 turns, 18 cm) on the left hip.
6. The lantern strap: a 4 cm leather bandolier over the right shoulder to the left hip.
7. Calf wraps and wrapped sandals.

Opaque pieces get an inset, flipped back layer where an edge shows (the cloth shader culls back
faces). Vertex colour = wind (R primary, G ripple, B phase, A flutter). `coverage()` says which body
vertices are hidden under clothing (those faces are deleted, asha.md §8.1). Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

import bb_anatomy
from asha_costume import TAG_CLOTH, Fields, TorsoChart, _panel, cast_last, dir_theta, limb_wrap
from asha_mesh import Part, catmull_rom, frames_along, grid, tube

# cloth atlas islands (u0, v0, u1, v1) in the shader's UV convention (v down); rhen_textures paints them
ATLAS = {
    "jacket": (0.0, 0.0, 0.5, 0.42),
    "sleeve": (0.5, 0.0, 0.75, 0.42),
    "collar": (0.75, 0.0, 1.0, 0.07),
    "undershirt": (0.75, 0.07, 1.0, 0.30),
    "trousers": (0.0, 0.42, 0.5, 0.58),
    "trouser_leg_L": (0.0, 0.58, 0.25, 0.80),
    "trouser_leg_R": (0.25, 0.58, 0.5, 0.80),
    "gauntlet": (0.5, 0.42, 0.75, 0.60),
    "gauntlet_hand": (0.5, 0.60, 0.75, 0.68),
    "belt": (0.5, 0.68, 0.75, 0.73),
    "strap": (0.5, 0.73, 0.75, 0.80),
    "rope": (0.75, 0.30, 1.0, 0.40),
    "wraps": (0.75, 0.40, 1.0, 0.62),
    "sandals": (0.75, 0.62, 1.0, 0.80),
    "grip": (0.0, 0.80, 0.25, 0.90),
    "lantern_strap": (0.25, 0.80, 0.5, 0.90),
}
JACKET_OFF = 0.0095  # m at S = 1, over the undershirt (0.004)
STRAP_OFF = 0.0175  # over the jacket
COIL_TURN_DEG = 35.0
WRAP_OFF = 0.0055  # calf wraps: clear of the donor calf (the field sits up to a few mm inside the skin)
WRAP_SPAN = (0.03, 0.55)  # ankle -> knee fraction the calf wraps cover


def _wind_rows(n_rows: int, n_cols: int, amp: float, phase0: float = 0.0):
    return [[(amp * t * t, amp * t, (phase0 + i / n_cols * 3.0) % 1.0, 0.3 * amp * t) for i in range(n_cols)]
            for t in np.linspace(0.0, 1.0, n_rows)]


def _sym_interp(th_deg: np.ndarray, xs: list, vs: list) -> np.ndarray:
    """A curve of |azimuth| (front 0 .. back 180), the same on both sides."""
    a = np.abs(((np.asarray(th_deg) + 180.0) % 360.0) - 180.0)
    return np.interp(a, xs, vs)


# ---------------------------------------------------------------------------------------------
# Torso pieces
# ---------------------------------------------------------------------------------------------
def undershirt_top(lm, chart: TorsoChart, th_deg: np.ndarray) -> np.ndarray:
    """A wrap V at the front, armholes cut in under the shoulders, a plain neck at the back."""
    S = lm.S
    neck = chart.z_sh + math.radians(55) * chart.k
    v = float(lm.P("notch")[2] - 0.11 * S)
    arm = float(lm.P("shoulder")[2] - 0.09 * S)
    strap = chart.z_sh + math.radians(20) * chart.k
    return _sym_interp(th_deg, [0, 14, 30, 52, 74, 92, 112, 132, 150, 180],
                       [v, v + 0.04 * S, neck - 0.02 * S, strap, arm, arm, strap, neck, neck, neck])


def jacket_top(lm, chart: TorsoChart, th_deg: np.ndarray, open_deg: float) -> np.ndarray:
    """The jacket's neckline: the lapel edge drops toward the front opening; the collar stands on it."""
    S = lm.S
    neck = chart.z_sh + math.radians(57) * chart.k
    lapel = float(lm.P("notch")[2] - 0.035 * S)
    return _sym_interp(th_deg, [0, open_deg, open_deg + 14, open_deg + 34, 180], [lapel, lapel, neck - 0.012 * S, neck,
                                                                                    neck])


def torso_sheet(fields: Fields, chart: TorsoChart, name: str, rect, th_deg: np.ndarray, H_top: np.ndarray,
                H_bot: float | np.ndarray, off: float, n_rows: int, back_inset: float | None, closed: bool,
                wind_amp: float = 0.0) -> Part:
    """A torso panel over the given azimuths (open or closed), row 0 at the top edge."""
    part = Part(name)
    part._mat = "cloth"
    lm = fields.lm
    th = np.radians(th_deg)
    H_bot = np.broadcast_to(np.asarray(H_bot, dtype=float), th.shape)
    P = np.zeros((n_rows, len(th), 3))
    fn = lambda Q: fields.upper(Q) - off  # noqa: E731
    for j in range(n_rows):
        t = j / (n_rows - 1)
        H = H_top + (H_bot - H_top) * t
        O, D = chart.rays(th, H)
        r = cast_last(fn, O, D, 0.4 * lm.S)
        P[j] = O + D * r[:, None]
    centre = np.array([0.0, chart.y_axis, 0.0])
    cols = _wind_rows(n_rows, len(th), wind_amp)
    _panel(part, P, rect, cols, closed, back_inset, centre)
    part.grid_P = P
    return part


def stand_collar(fields: Fields, chart: TorsoChart, rect, top_line: np.ndarray, th_deg: np.ndarray,
                 height: float) -> Part:
    """A 3 cm stand-up collar on the jacket's neckline, open at the front, flaring slightly."""
    part = Part("Collar")
    part._mat = "cloth"
    lm = fields.lm
    S = lm.S
    th = np.radians(th_deg)
    rows = 4
    P = np.zeros((rows, len(th), 3))
    O0, D0 = chart.rays(th, top_line)
    base = O0 + D0 * cast_last(lambda Q: fields.upper(Q) - JACKET_OFF * S, O0, D0, 0.4 * S)[:, None]
    nb, sb = lm.P("neck_base"), lm.P("skull_base")
    ax = (sb - nb) / np.linalg.norm(sb - nb)
    for j in range(rows):
        t = 1.0 - j / (rows - 1)  # row 0 = top
        # rise along the neck axis and lean in a little toward the neck, then out at the rim
        q = base + ax * height * t
        c = nb + np.outer((q - nb) @ ax, ax)
        q = q + (c - q) * (0.18 * t)
        P[j] = q
    _panel(part, P, rect, None, False, 0.0025 * S, np.array([0.0, chart.y_axis, 0.0]))
    return part


# ---------------------------------------------------------------------------------------------
# Limb pieces
# ---------------------------------------------------------------------------------------------
def limb_tube(fields: Fields, region, path: np.ndarray, off_fn, rect, name: str, n_around: int = 20,
              rows: int = 12, back_inset: float | None = None, wind_amp: float = 0.0, min_r: float = 0.0) -> Part:
    """A tube along `path` (any polyline down a limb), each ring ray-cast from the path onto the
    region field plus `off_fn(t)` (t = 0 at the first ring). `region`: a region name or a field."""
    part = Part(name)
    part._mat = "cloth"
    S = fields.lm.S
    C = catmull_rom(path, rows) if len(path) != rows else path
    T, N, Bn = frames_along(C, np.array([0.0, 0.0, 1.0]))
    ang = 2 * math.pi * np.arange(n_around) / n_around
    base = fields.region(region) if isinstance(region, str) else region
    P = np.zeros((rows, n_around, 3))
    for j in range(rows):
        t = j / (rows - 1)
        D = np.cos(ang)[:, None] * N[j] + np.sin(ang)[:, None] * Bn[j]
        O = np.repeat(C[j][None, :], n_around, axis=0)
        off = off_fn(t)
        r = cast_last(lambda Q, off=off: base(Q) - off, O, D, 0.2 * S)
        r = np.maximum(r, min_r)
        P[j] = O + D * r[:, None]
    _panel(part, P, rect, _wind_rows(rows, n_around, wind_amp, 0.37), True, back_inset, C[0])
    part.grid_P = P
    return part


def arm_path(lm, side: str, t0: float, t1: float, n: int = 14) -> np.ndarray:
    """Points down the arm from the shoulder joint (0) through the elbow (0.5) to the wrist (1)."""
    sh, el, wr = lm.side_pt("shoulder", side), lm.side_pt("elbow", side), lm.side_pt("wrist", side)
    out = []
    for t in np.linspace(t0, t1, n):
        out.append(sh + (el - sh) * (t / 0.5) if t <= 0.5 else el + (wr - el) * ((t - 0.5) / 0.5))
    return np.array(out)


def leg_path(lm, side: str, z0: float, z1: float, n: int = 12) -> np.ndarray:
    hip, kn, an = lm.side_pt("hip", side), lm.side_pt("knee", side), lm.side_pt("ankle", side)
    out = []
    for z in np.linspace(z0, z1, n):
        if z >= kn[2]:
            t = (hip[2] - z) / max(hip[2] - kn[2], 1e-6)
            out.append(hip + (kn - hip) * t)
        else:
            t = (kn[2] - z) / max(kn[2] - an[2], 1e-6)
            out.append(kn + (an - kn) * t)
    return np.array(out)


def gauntlet(fields: Fields, cuff_m: float) -> Part:
    """Oiled-leather fingerless gauntlet on the left forearm and hand, with a flared cuff where the
    sleeve tucks in and brass rivets in two rows (rivets are their own small domes, material brass)."""
    lm = fields.lm
    S = lm.S
    sh, el, wr = lm.side_pt("shoulder", "L"), lm.side_pt("elbow", "L"), lm.side_pt("wrist", "L")
    fore = np.linalg.norm(wr - el)
    t0 = 1.0 - 0.5 * min(cuff_m * S / fore, 0.95)
    path = arm_path(lm, "L", t0, 1.0, 10)
    hand = lm.hands["L"]
    path = np.concatenate([path, [hand.wrist + hand.axis * hand.length * f for f in (0.16, 0.34, 0.5)]])
    reg_arm = fields.region("arm_L")
    reg_hand = fields.region("hand_L")

    def fld(Q: np.ndarray) -> np.ndarray:
        return bb_anatomy.smin(reg_arm(Q), reg_hand(Q), 0.01 * S)

    # the cuff flares at the top (the sleeve end tucks inside it), the leather is snug at the wrist
    part = limb_tube(fields, fld, path, lambda t: (0.0065 - 0.0035 * min(t / 0.3, 1.0)) * S, ATLAS["gauntlet"],
                     "Gauntlet", n_around=20, rows=13, back_inset=0.0025 * S)
    part.name = "Gauntlet"
    # rivets: two rows along the back of the forearm
    riv = Part("Rivets")
    P = part.grid_P
    from asha_mesh import uv_sphere
    for j in (1, 4, 7):
        for i in (3, 7):
            q = P[j, i]
            n = q - path[min(j, len(path) - 1)]
            n /= max(np.linalg.norm(n), 1e-9)
            uv_sphere(riv, q + n * 0.0008 * S, 0.0035 * S, 8, 4, "brass", axis_fwd=n, uv_rect=(0, 0, 0.1, 0.1),
                      tags=TAG_CLOTH)
    part.extend(riv)
    return part


# ---------------------------------------------------------------------------------------------
# Belt, tether coil, strap
# ---------------------------------------------------------------------------------------------
def belt(fields: Fields, z_c: float, width: float, outer: np.ndarray) -> Part:
    part = Part("Belt")
    part._mat = "cloth"
    lm = fields.lm
    S = lm.S
    n = 48
    th = np.radians(np.linspace(0.0, 360.0, n, endpoint=False))
    D = dir_theta(th)
    rows = 3
    P = np.zeros((rows, n, 3))
    for j in range(rows):
        z = z_c + width * (0.5 - j / (rows - 1))
        near = outer[np.abs(outer[:, 2] - z) < 0.025 * S]
        q = near - np.array([0.0, 0.01 * S, 0.0])
        ang = np.arctan2(q[:, 0], -q[:, 1])
        rad = np.hypot(q[:, 0], q[:, 1])
        r = np.zeros(n)
        for i in range(n):
            m = np.abs(np.angle(np.exp(1j * (ang - th[i])))) < 0.2
            r[i] = rad[m].max() if m.any() else 0.13 * S
        r = r + 0.004 * S
        O = np.stack([np.zeros(n), np.full(n, 0.01 * S), np.full(n, z)], axis=-1)
        P[j] = O + D * r[:, None]
    centre = np.array([0.0, 0.01 * S, 0.0])
    _panel(part, P, ATLAS["belt"], None, True, 0.003 * S, centre)
    # a brass buckle at the front: a flat frame of four bars
    bk = Part("Buckle")
    c = P[1, 0] + np.array([0.0, -0.004 * S, 0.0])
    w, h = 0.026 * S, width * 1.15
    corners = [c + np.array([-w, 0, h / 2]), c + np.array([w, 0, h / 2]), c + np.array([w, 0, -h / 2]),
               c + np.array([-w, 0, -h / 2])]
    for k in range(4):
        a, b = corners[k], corners[(k + 1) % 4]
        tube(bk, np.linspace(a, b, 2), 0.0028 * S, 6, "brass", np.array([0.0, -1.0, 0.0]), (0, 0, 0.1, 0.1),
             tags=TAG_CLOTH)
    part.extend(bk)
    return part


def tether_coil(fields: Fields, turns: int, diameter: float, outer: np.ndarray, z_belt: float) -> Part:
    """The rope coil on the left hip: `turns` loops of 7 mm rope wound into a flat ring, hung from
    the belt, its axis pointing out from the hip."""
    part = Part("TetherCoil")
    lm = fields.lm
    S = lm.S
    R = 0.5 * diameter
    rope_r = 0.0042 * S
    side = outer[(outer[:, 2] < z_belt) & (outer[:, 2] > z_belt - 0.18 * S)]
    x_out = float(side[:, 0].max()) if len(side) else 0.18 * S
    # rhen.md §2: "the tether coil makes a ring on the left hip" in the front view, so the ring
    # faces forward, turned out from the hip by COIL_TURN_DEG; it hangs from the belt at the side
    a = math.radians(COIL_TURN_DEG)
    ax = np.array([math.sin(a), -math.cos(a), 0.0])
    hip = side[np.argmax(side[:, 0])] if len(side) else np.array([x_out, 0.0, z_belt])
    c = np.array([x_out - 0.15 * R, float(hip[1]) - 0.035 * S, z_belt - R * 0.80]) + ax * (turns * rope_r * 0.5)
    e1 = np.array([0.0, 0.0, 1.0])
    e1 = e1 - (e1 @ ax) * ax
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(ax, e1)
    n = turns * 28
    t = np.linspace(0.0, turns * 2 * math.pi, n)
    # flat-ish wound coil: each turn a little inward and outward (rope stacks across the coil)
    rr = R - rope_r * 1.6 * ((t / (2 * math.pi)) % 3)
    off = rope_r * 1.9 * (t / (2 * math.pi) - turns / 2) * 0.35
    C = c[None, :] + np.outer(np.cos(t) * rr, e1) + np.outer(np.sin(t) * rr, e2) + np.outer(off, ax)
    u0, v0, u1, v1 = ATLAS["rope"]
    tube(part, C, rope_r, 6, "cloth", ax, (u0, v0, u1, v1), tags=TAG_CLOTH)
    # the hanging loop that ties it to the belt
    tie = np.array([c + e1 * (R - rope_r), c + e1 * (R + 0.015 * S),
                    np.array([x_out - 0.15 * R, float(hip[1]) - 0.01 * S, z_belt])])
    tube(part, catmull_rom(tie, 8), rope_r * 0.8, 6, "cloth", ax, (u0, v0, u1, v1), tags=TAG_CLOTH)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part


def bandolier(fields: Fields, chart: TorsoChart, width: float, rect, path_thH: list, name: str,
              off: float) -> tuple[Part, np.ndarray, np.ndarray]:
    """A flat leather band over the torso along a closed path of (azimuth deg, H) chart points."""
    part = Part(name)
    lm = fields.lm
    S = lm.S
    ctrl = np.array([(math.radians(a), h) for a, h in path_thH])
    ctrl[:, 0] = np.unwrap(ctrl[:, 0])
    ext = np.concatenate([ctrl, ctrl[:1] + np.array([2 * math.pi * round((ctrl[-1, 0] - ctrl[0, 0]) / (2 * math.pi)),
                                                     0.0])])
    pts = catmull_rom(ext, 96)
    O, D = chart.rays(pts[:, 0], pts[:, 1])
    fn = lambda Q: fields.upper(Q) - off  # noqa: E731
    C = O + D * cast_last(fn, O, D, 0.4 * S)[:, None]
    T = np.gradient(C, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
    e = 2e-4
    g = np.zeros_like(C)
    for k in range(3):
        d = np.zeros(3)
        d[k] = e
        g[:, k] = fn(C + d) - fn(C - d)
    N = g / np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-12)
    side = np.cross(T, N)
    side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-12)
    P = np.stack([C - side * width / 2, C + side * width / 2], axis=1)
    # push each edge back onto the offset surface (the band hugs the chest and back)
    for k in range(2):
        q = P[:, k]
        for _ in range(3):
            g2 = np.zeros_like(q)
            for a in range(3):
                d = np.zeros(3)
                d[a] = e
                g2[:, a] = fn(q + d) - fn(q - d)
            n2 = g2 / np.maximum(np.linalg.norm(g2, axis=1, keepdims=True), 1e-12)
            q = q - n2 * np.maximum(fn(q), -0.002 * S)[:, None]
        P[:, k] = q
    centre = np.array([0.0, chart.y_axis, 0.0])
    part._mat = "cloth"
    _panel(part, P, rect, None, False, 0.0025 * S, centre)
    return part, C, N


def wrapped_sandal(fields: Fields, side: str, rect) -> Part:
    """rhen.md §4 #7: a leather sole a little wider than the foot, plus linen strips wound over the
    instep and round the heel up to the calf wraps (clear of the donor skin, like the wraps)."""
    part = Part(f"Sandal{side}")
    part._mat = "cloth"
    lm = fields.lm
    S = lm.S
    hb_, tt = lm.side_pt("heel_back", side), lm.side_pt("toe_tip", side)
    fwd = (tt - hb_) / np.linalg.norm(tt - hb_)
    lat = np.cross(fwd, np.array([0.0, 0.0, 1.0]))
    fn = fields.region(f"foot_{side}")
    n = 24
    c0 = (hb_ + tt) * 0.5
    c0[2] = 0.006 * S
    outline = []
    for i in range(n):
        a = 2 * math.pi * i / n
        d = fwd * math.cos(a) + lat * math.sin(a)
        r = cast_last(fn, c0[None, :], d[None, :], 0.2 * S)[0]
        outline.append(c0 + d * (r + 0.007 * S))
    outline = np.array(outline)
    top = outline.copy()
    top[:, 2] = 0.006 * S
    bot = outline.copy()
    bot[:, 2] = -0.002
    _panel(part, np.stack([top, bot]), (rect[0], rect[1], rect[2], rect[1] + 0.05), None, True, None, c0)
    ct = part.add_v(np.array([c0[0], c0[1], 0.006 * S]), tag=TAG_CLOTH)
    cb = part.add_v(np.array([c0[0], c0[1], -0.002]), tag=TAG_CLOTH)
    base = len(part.V) - 2 - 2 * n
    for i in range(n):
        i2 = (i + 1) % n
        part.add_f((ct, base + i2, base + i), [(rect[0], rect[1] + 0.1)] * 3, "cloth")
        part.add_f((cb, base + n + i, base + n + i2), [(rect[0], rect[1] + 0.1)] * 3, "cloth")
    # strips over the instep (two) and round the ankle into the calf wrap
    for u in (0.52, 0.74):
        c = hb_ + (tt - hb_) * u + np.array([0.0, 0.0, 0.02 * S])
        part.extend(limb_wrap(fields, f"foot_{side}", c - fwd * 0.011 * S, c + fwd * 0.011 * S, WRAP_OFF * S,
                              (rect[0], rect[1] + 0.1, rect[2], rect[3]), "strap", n_around=16, rows=2))
    an = lm.side_pt("ankle", side)
    kn = lm.side_pt("knee", side)
    part.extend(limb_wrap(fields, f"leg_{side}", an - (kn - an) * 0.05, an + (kn - an) * WRAP_SPAN[0], WRAP_OFF * S,
                          (rect[0], rect[1] + 0.1, rect[2], rect[3]), "ankle", n_around=20, rows=3))
    return part


# ---------------------------------------------------------------------------------------------
def build_costume(body, params: dict) -> tuple[dict[str, Part], dict]:
    """Returns ({name: Part}, anchors) where anchors are the points the props hang from."""
    lm = body.lm
    S = lm.S
    fields = Fields(body)
    chart = TorsoChart(lm)
    z_waist = float(lm.P("waist")[2])
    z_crotch = float(lm.P("crotch")[2])
    out: dict[str, Part] = {}
    # 1. undershirt (closed ring), waist to the V neck and armholes
    th_u = np.linspace(0.0, 360.0, 52, endpoint=False)
    out["Undershirt"] = torso_sheet(fields, chart, "Undershirt", ATLAS["undershirt"], th_u,
                                    undershirt_top(lm, chart, th_u), z_waist - 0.04 * S, 0.004 * S, 12, 0.0015 * S,
                                    True)
    # 2. sea-jacket, open at the front (th = 0), from the lapels to the lower ribs
    open_deg = float(params["front_opening_deg"])
    th_j = np.linspace(open_deg, 360.0 - open_deg, 50)
    top = jacket_top(lm, chart, th_j, open_deg)
    hem = z_waist + 0.07 * S - float(params["jacket_hem_drop_m"]) * S * np.cos(np.radians(th_j)) ** 2
    out["Jacket"] = torso_sheet(fields, chart, "Jacket", ATLAS["jacket"], th_j, top, hem, JACKET_OFF * S, 14,
                                0.0025 * S, False, wind_amp=0.15)
    out["Collar"] = stand_collar(fields, chart, ATLAS["collar"], top, th_j, float(params["collar_height_m"]) * S)
    # the left sleeve: shoulder seam to the wrist, tucked into the gauntlet's cuff
    sleeve_path = arm_path(lm, "L", 0.02, 0.86, 14)
    out["Sleeve"] = limb_tube(fields, "arm_L", sleeve_path,
                              lambda t: (0.010 - 0.004 * t) * S if t > 0.08 else 0.012 * S,
                              ATLAS["sleeve"], "Sleeve", n_around=22, rows=16, back_inset=0.002 * S, wind_amp=0.1,
                              min_r=0.035 * S)
    # 3. gauntlet
    out["Gauntlet"] = gauntlet(fields, float(params["gauntlet_cuff_m"]))
    # 4. trousers: a pelvis band, then two legs from just below the crotch to the knee
    kn_z = float(lm.side_pt("knee", "L")[2])
    hem_z = kn_z + float(params["trouser_hem_above_knee_m"]) * S
    th_t = np.linspace(0.0, 360.0, 48, endpoint=False)
    pelvis = Part("TrouserTop")
    pelvis._mat = "cloth"
    rows = 8
    P = np.zeros((rows, len(th_t), 3))
    D = dir_theta(np.radians(th_t))
    for j in range(rows):
        z = z_waist + 0.01 * S + (z_crotch + 0.015 * S - z_waist - 0.01 * S) * j / (rows - 1)
        O = np.stack([np.zeros(len(th_t)), np.full(len(th_t), 0.01 * S), np.full(len(th_t), z)], axis=-1)
        r = cast_last(lambda Q: fields.lower(Q) - 0.008 * S, O, D, 0.5 * S)
        P[j] = O + D * r[:, None]
    _panel(pelvis, P, ATLAS["trousers"], None, True, 0.0018 * S, np.array([0.0, 0.01 * S, 0.0]))
    out["TrouserTop"] = pelvis
    for sd in ("L", "R"):
        path = leg_path(lm, sd, z_crotch + 0.06 * S, hem_z, 13)
        out[f"TrouserLeg{sd}"] = limb_tube(fields, f"leg_{sd}", path, lambda t: (0.0075 + 0.011 * t ** 1.5) * S,
                                           ATLAS[f"trouser_leg_{sd}"], f"TrouserLeg{sd}", n_around=24, rows=13,
                                           back_inset=0.0018 * S, wind_amp=0.08)
    # 5. belt and tether coil
    lower_v = np.concatenate([out["TrouserTop"].varr(), out["Undershirt"].varr()])
    z_belt = z_waist - 0.005 * S
    out["Belt"] = belt(fields, z_belt, 0.04 * S, lower_v)
    out["TetherCoil"] = tether_coil(fields, int(params["rope_turns"]), float(params["rope_coil_d_m"]) * S,
                                    out["Belt"].varr(), z_belt)
    # 6. lantern strap: over the right shoulder, across the chest to the left hip, round the back
    zs = chart.z_sh
    k = chart.k
    nip = float(lm.P("nipple")[2])
    path = [(-58.0, zs + math.radians(48) * k), (-22.0, nip + 0.03 * S), (30.0, z_waist + 0.07 * S),
            (78.0, z_waist - 0.01 * S), (125.0, z_waist + 0.02 * S), (180.0, nip - 0.02 * S),
            (232.0, zs - 0.05 * S), (262.0, zs + math.radians(40) * k)]
    strap, strap_c, strap_n = bandolier(fields, chart, 0.04 * S, ATLAS["strap"], path, "Strap", STRAP_OFF * S)
    out["Strap"] = strap
    # 7. calf wraps and sandals
    wraps = Part("Wraps")
    for sd in ("L", "R"):
        an = lm.side_pt("ankle", sd)
        kn = lm.side_pt("knee", sd)
        w = limb_wrap(fields, f"leg_{sd}", an + (kn - an) * WRAP_SPAN[0], an + (kn - an) * WRAP_SPAN[1], WRAP_OFF * S,
                      ATLAS["wraps"], f"Wrap{sd}", n_around=20, rows=10)
        wraps.extend(w)
    out["Wraps"] = wraps
    sandals = Part("Sandals")
    for sd in ("L", "R"):
        sandals.extend(wrapped_sandal(fields, sd, ATLAS["sandals"]))
    out["Sandals"] = sandals
    for p in out.values():
        if not p.C:
            p.C = [(0.0, 0.0, 0.0, 0.0)] * len(p.V)
        elif len(p.C) < len(p.V):
            p.C = p.C + [(0.0, 0.0, 0.0, 0.0)] * (len(p.V) - len(p.C))
    # anchors for the props: the strap point on the right shoulder blade, and the small of the back
    back_i = int(np.argmin(np.linalg.norm(strap_c - np.array([-0.14 * S, 0.09 * S, zs - 0.03 * S]), axis=1)))
    jacket_P = out["Jacket"].grid_P
    anchors = {"lantern_strap": strap_c[back_i], "lantern_normal": strap_n[back_i],
               "back_small": np.array([0.0, float(np.max(lower_v[np.abs(lower_v[:, 2] - z_belt) < 0.03 * S][:, 1])),
                                       z_belt + 0.02 * S]),
               "hip_x": float(np.max(np.abs(lower_v[np.abs(lower_v[:, 2] - z_belt) < 0.05 * S][:, 0]))),
               "jacket_hem_z": float(jacket_P[-1, :, 2].mean())}
    return out, anchors


def coverage(body, params: dict, V: np.ndarray, reg: np.ndarray) -> np.ndarray:
    """True for body vertices hidden under opaque clothing (with a margin), asha.md §8.1."""
    lm = body.lm
    S = lm.S
    chart = TorsoChart(lm)
    z_waist = float(lm.P("waist")[2])
    th, H = chart.H_of(V)
    th_deg = np.degrees(th)
    m = 0.025 * S
    torso = reg == "torso"
    shirt = torso & (H > z_waist - 0.04 * S) & (H < undershirt_top(lm, chart, th_deg) - m)
    open_deg = float(params["front_opening_deg"])
    a = np.abs(((th_deg + 180.0) % 360.0) - 180.0)
    jacket = torso & (a > open_deg + 12.0) & (H > z_waist + 0.07 * S + m) & (
        H < jacket_top(lm, chart, th_deg, open_deg) - m)
    sh, el, wr = lm.side_pt("shoulder", "L"), lm.side_pt("elbow", "L"), lm.side_pt("wrist", "L")
    ax = wr - sh
    t = (V - sh) @ ax / (ax @ ax)
    sleeve = (reg == "arm_L") & (t > 0.12) & (t < 0.93)
    kn_z = float(lm.side_pt("knee", "L")[2]) + float(params["trouser_hem_above_knee_m"]) * S
    legs = (reg == "leg_L") | (reg == "leg_R") | torso
    trousers = legs & (V[:, 2] < z_waist - m * 0.5) & (V[:, 2] > kn_z + 0.035 * S)
    calves = np.zeros(len(V), dtype=bool)
    for sd in ("L", "R"):
        an, kn = lm.side_pt("ankle", sd), lm.side_pt("knee", sd)
        ax = kn - an
        t = (V - an) @ ax / (ax @ ax)
        calves |= (reg == f"leg_{sd}") & (t > WRAP_SPAN[0] + 0.04) & (t < WRAP_SPAN[1] - 0.04)
    return shirt | jacket | sleeve | trousers | calves
