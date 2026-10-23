"""Rhen's costume as procedural cloth panels (no bpy), rhen.md §3-§4 and §9.

Built on Asha's pattern-grid machinery (asha_costume: the torso chart, ray-casting rows onto the
body field plus a fitting offset, inset back layers, the limb wraps and the sandal), so the chart of
every piece is its UV island in Rhen's 2K cloth atlas (rhen_textures.cloth_atlas draws on the same
rectangles). Pieces, inner to outer:

1. Undershirt: a sleeveless wrap vest in sand cotton, tucked into the trousers.
2. Sea-jacket: short (to the lower ribs), open at the front, a 3 cm stand collar, **one sleeve** (the
   left) running long to the wrist; the right side ends at a raw armhole over the shoulder cap.
3. Diving gauntlet: oiled leather over the left forearm and palm (fingerless), brass rivets.
4. Short trousers to the knee: a hip piece and two leg tubes, sand canvas.
5. Belt (leather) and 7. calf wraps (linen) and wrapped sandals (asha_costume.sandal).
6. Lantern strap: a 4 cm leather bandolier from the right shoulder, across the back and the chest
   to the left hip.

Opaque pieces carry an inset, flipped back layer (the cloth shader culls back faces). Vertex colour
= wind (R primary, G ripple, B phase, A flutter): the jacket hem and sleeve move a little, the rest is
pinned. `coverage()` says which body vertices are hidden under clothing (those faces are deleted).
Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_costume import (TAG_CLOTH, Fields, TorsoChart, _panel, cast_last, dir_theta, limb_wrap, sandal, skirt,
                          torso_panel)
from asha_mesh import Part, catmull_rom, uv_sphere

# cloth atlas islands (u0, v0, u1, v1) in the shader's UV convention (v down); rhen_textures paints them
ATLAS = {
    "jacket": (0.0, 0.0, 0.5, 0.40),
    "sleeve": (0.5, 0.0, 0.75, 0.40),
    "collar": (0.75, 0.0, 1.0, 0.08),
    "undershirt": (0.75, 0.08, 1.0, 0.40),
    "trousers_hip": (0.0, 0.40, 0.5, 0.52),
    "trousers_leg": (0.0, 0.52, 0.5, 0.75),
    "gauntlet": (0.5, 0.40, 0.75, 0.56),
    "palm": (0.5, 0.56, 0.75, 0.62),
    "belt": (0.5, 0.62, 0.75, 0.68),
    "strap": (0.5, 0.68, 0.75, 0.76),
    "wraps": (0.75, 0.40, 1.0, 0.64),
    "sandals": (0.75, 0.64, 1.0, 0.76),
    "rope": (0.0, 0.76, 0.25, 0.88),
    "grip": (0.25, 0.76, 0.5, 0.88),
}
PINNED = (0.0, 0.0, 0.0, 0.0)


def _deg(a: float) -> float:
    return math.radians(a)


def open_torso_panel(fields: Fields, chart: TorsoChart, name: str, rect, H_bot: float, H_top_fn, off: float,
                     th0: float, th1: float, n_th: int, n_rows: int, back_inset: float | None, wind=None) -> Part:
    """asha_costume.torso_panel over the azimuth range th0 -> th1 (degrees, increasing through the
    back), open between th1 and th0: the jacket's open front."""
    part = Part(name)
    part._mat = "cloth"
    lm = fields.lm
    th_deg = np.linspace(th0, th1, n_th)
    th = np.radians(th_deg)
    H_top = H_top_fn(th_deg)
    P = np.zeros((n_rows, n_th, 3))
    fn = lambda Q: fields.upper(Q) - off  # noqa: E731
    for j in range(n_rows):
        t = j / (n_rows - 1)
        O, D = chart.rays(th, H_top + (H_bot - H_top) * t)
        P[j] = O + D * cast_last(fn, O, D, 0.4 * lm.S)[:, None]
    cols = None if wind is None else [[wind(j / (n_rows - 1), i / (n_th - 1)) for i in range(n_th)]
                                      for j in range(n_rows)]
    _panel(part, P, rect, cols, False, back_inset, np.array([0.0, chart.y_axis, 0.0]))
    return part


def jacket_top(lm, chart: TorsoChart, gap_deg: float):
    """The jacket's top edge: the collar line round the neck, dropping into the open lapels."""
    neck = chart.z_sh + _deg(56) * chart.k
    lapel = chart.z_sh + _deg(22) * chart.k

    def f(th_deg: np.ndarray) -> np.ndarray:
        a = np.minimum(np.mod(th_deg, 360.0), 360.0 - np.mod(th_deg, 360.0))  # degrees from the front
        t = np.clip((a - gap_deg) / 40.0, 0.0, 1.0)
        return lapel + (neck - lapel) * (t * t * (3 - 2 * t))

    _ = lm
    return f


def undershirt_top(lm, chart: TorsoChart):
    """A wrap vest: a V at the front, armholes at the sides, a round back neck."""
    S = lm.S
    neck = chart.z_sh + _deg(50) * chart.k
    arm = float(lm.P("shoulder")[2] - 0.085 * S)
    v_front = float(lm.P("nipple")[2] + 0.06 * S)
    xs = [0, 20, 45, 70, 90, 110, 140, 180, 220, 250, 270, 290, 315, 340, 360]
    vs = [v_front, chart.z_sh + _deg(10) * chart.k, chart.z_sh + _deg(40) * chart.k, chart.z_sh, arm, chart.z_sh,
          neck, neck, neck, chart.z_sh, arm, chart.z_sh, chart.z_sh + _deg(40) * chart.k,
          chart.z_sh + _deg(10) * chart.k, v_front]
    return lambda th_deg: np.interp(np.mod(th_deg, 360.0), xs, vs)


def jacket_collar(fields: Fields, rect, height: float, gap_deg: float, n: int = 40) -> Part:
    """The 3 cm stand collar, open at the front like the jacket."""
    part = Part("JacketCollar")
    part._mat = "cloth"
    lm = fields.lm
    S = lm.S
    nb, sb = lm.P("neck_base"), lm.P("skull_base")
    ax = (sb - nb) / np.linalg.norm(sb - nb)
    th = np.radians(np.linspace(gap_deg + 14.0, 360.0 - gap_deg - 14.0, n))
    rows = 4
    P = np.zeros((rows, n, 3))
    base = nb + ax * 0.012 * S
    for j in range(rows):
        t = 1.0 - j / (rows - 1)
        c = base + ax * height * t
        D = dir_theta(th)
        O = np.repeat(c[None, :], n, axis=0)
        r = cast_last(lambda Q: fields.body.regions["torso"].sdf(Q) - (0.008 + 0.005 * t) * S, O, D, 0.2 * S)
        P[j] = O + D * r[:, None]
    _panel(part, P, rect, None, False, 0.002 * S, base)
    return part


def arm_tube(fields: Fields, side: str, name: str, path: np.ndarray, off: float, rect, n_around: int = 24,
             min_r: float = 0.03, wind=None) -> Part:
    """A sleeve along `path` (points shoulder -> wrist), each ring ray-cast onto the arm field + off."""
    part = Part(name)
    part._mat = "cloth"
    lm = fields.lm
    S = lm.S
    fn = lambda Q: fields.body.regions[f"arm_{side}"].sdf(Q) - off  # noqa: E731
    up = np.array([0.0, 0.0, 1.0])
    rings = []
    for k in range(len(path)):
        ax = path[min(k + 1, len(path) - 1)] - path[max(k - 1, 0)]
        ax /= np.linalg.norm(ax)
        e1 = up - (up @ ax) * ax
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(ax, e1)
        ang = 2 * math.pi * np.arange(n_around) / n_around
        D = np.cos(ang)[:, None] * e1 + np.sin(ang)[:, None] * e2
        O = np.repeat(path[k][None, :], n_around, axis=0)
        r = np.maximum(cast_last(fn, O, D, 0.15 * S), min_r * S)
        rings.append(O + D * r[:, None])
    R = np.stack(rings)
    cols = None if wind is None else [[wind(j / (len(path) - 1))] * n_around for j in range(len(path))]
    _panel(part, R, rect, cols, True, 0.002 * S, path[0])
    return part


def band_ring(fields: Fields, name: str, rect, z_top: float, width: float, off: float, n: int = 48) -> Part:
    """A flat band round the hips (the belt) over the lower field."""
    part = skirt(fields, name, rect, z_top, lambda th: np.full_like(th, z_top - width), off, n, 3, 1, 0.0, 0.0,
                 0.0015 * fields.lm.S, 0)
    part.C = [PINNED] * len(part.V)
    return part


def strap(fields: Fields, chart: TorsoChart, rect, width: float, off: float) -> tuple[Part, np.ndarray]:
    """The lantern strap: a leather bandolier from the right shoulder down the back to the left hip
    and back up across the chest, laid on the torso chart. Returns the part and its back centreline."""
    part = Part("Strap")
    part._mat = "cloth"
    lm = fields.lm
    S = lm.S
    z_w = float(lm.P("waist")[2])
    z_n = float(lm.P("nipple")[2])
    over = chart.z_sh + _deg(38) * chart.k
    # (azimuth deg, chart height): front of the right shoulder, over it, the right shoulder blade, the
    # small of the back, the left hip, the belly and up the chest back to the start (a closed loop)
    ctrl = np.array([[300.0, z_n + 0.07 * S], [272.0, over], [235.0, z_n + 0.03 * S], [180.0, z_n - 0.11 * S],
                     [120.0, z_w - 0.03 * S], [65.0, z_w - 0.02 * S], [10.0, z_n - 0.08 * S], [330.0, z_n + 0.01 * S],
                     [300.0, z_n + 0.07 * S]])
    # walk the azimuth monotonically down through the back (300 -> 272 -> ... -> 10 -> -30 -> -60)
    ctrl[6:, 0] = ctrl[6:, 0] - np.array([0.0, 360.0, 360.0])
    C = catmull_rom(ctrl, 120)
    th = np.radians(C[:, 0])
    fn = lambda Q: np.minimum(fields.upper(Q), fields.lower(Q)) - off  # noqa: E731
    O, D = chart.rays(th, C[:, 1])
    P = O + D * cast_last(fn, O, D, 0.4 * S)[:, None]
    T = np.gradient(P, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
    side = np.cross(T, D)
    side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-12)
    Q = np.stack([P - side * width * 0.5, P + side * width * 0.5], axis=1)
    _panel(part, Q, rect, None, False, 0.003 * S, np.array([0.0, chart.y_axis, 0.0]))
    return part, P


def gauntlet(fields: Fields, rect_cuff, rect_palm, cuff_from_wrist: float) -> tuple[Part, list]:
    """The fingerless diving gauntlet on the left: a cuff over the sleeve's end and the forearm, a palm
    piece to the knuckles. Returns the part and the rivet centres (brass, rhen_props)."""
    lm = fields.lm
    S = lm.S
    el, wr = lm.side_pt("elbow", "L"), lm.side_pt("wrist", "L")
    hand = lm.hands["L"]
    cuff = limb_wrap(fields, "arm_L", wr + (el - wr) * cuff_from_wrist, wr - (el - wr) * 0.02, 0.011 * S, rect_cuff,
                     "GauntletCuff", n_around=24, rows=8)
    palm = limb_wrap(fields, "hand_L", hand.wrist + hand.axis * 0.01 * S,
                     hand.knuckle - hand.axis * 0.004 * S, 0.0025 * S, rect_palm, "GauntletPalm", n_around=20, rows=5)
    part = Part("Gauntlet")
    part.extend(cuff)
    part.extend(palm)
    # rivets: a ring of six round the cuff's top edge, and four on the back of the hand
    ax = (el - wr) / np.linalg.norm(el - wr)
    ref = np.array([0.0, 0.0, 1.0])
    e1 = ref - (ref @ ax) * ax
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(ax, e1)
    rivets = []
    top = wr + (el - wr) * (cuff_from_wrist - 0.06)
    fn = lambda Q: fields.body.regions["arm_L"].sdf(Q) - 0.0125 * S  # noqa: E731
    for k in range(6):
        a = 2 * math.pi * k / 6
        d = math.cos(a) * e1 + math.sin(a) * e2
        r = cast_last(fn, top[None, :], d[None, :], 0.12 * S)[0]
        rivets.append(top + d * r)
    hf = lambda Q: fields.body.regions["hand_L"].sdf(Q) - 0.004 * S  # noqa: E731
    for f in (-0.3, -0.1, 0.1, 0.3):
        c = hand.wrist + hand.axis * 0.45 * (hand.knuckle - hand.wrist) @ hand.axis + hand.side * f * hand.width
        r = cast_last(hf, c[None, :], hand.dorsal[None, :], 0.08 * S)[0]
        rivets.append(c + hand.dorsal * r)
    return part, rivets


def build_costume(body, params: dict) -> dict[str, Part]:
    lm = body.lm
    S = lm.S
    fields = Fields(body)
    chart = TorsoChart(lm)
    z_waist = float(lm.P("waist")[2])
    z_crotch = float(lm.P("crotch")[2])
    gap = float(params["jacket_front_gap_deg"])
    out: dict[str, Part] = {}
    out["Undershirt"] = torso_panel(fields, chart, "Undershirt", "cloth", ATLAS["undershirt"], z_waist - 0.035 * S,
                                    undershirt_top(lm, chart), 0.003 * S, 56, 12, None)
    hem = float(lm.P("nipple")[2] - float(params["jacket_hem_below_nipple_m"]) * S)

    def jwind(t: float, u: float) -> tuple:
        return (0.25 * t ** 2, 0.2 * t, (u * 3.0) % 1.0, 0.1 * t)

    out["Jacket"] = open_torso_panel(fields, chart, "Jacket", ATLAS["jacket"], hem, jacket_top(lm, chart, gap),
                                     0.0095 * S, gap, 360.0 - gap, 56, 14, 0.0025 * S, jwind)
    out["JacketCollar"] = jacket_collar(fields, ATLAS["collar"], float(params["collar_height_m"]) * S, gap)
    sh, el, wr = lm.side_pt("shoulder", "L"), lm.side_pt("elbow", "L"), lm.side_pt("wrist", "L")
    a_up = (el - sh) / np.linalg.norm(el - sh)
    start = sh - a_up * 0.01 * S + np.array([0.0, 0.0, 0.01 * S])
    end = wr + (el - wr) * float(params["sleeve_end_from_wrist"])
    path = np.concatenate([np.linspace(start, el, 10, endpoint=False), np.linspace(el, end, 10)])
    out["JacketSleeve"] = arm_tube(fields, "L", "JacketSleeve", path, 0.0075 * S, ATLAS["sleeve"],
                                   wind=lambda t: (0.12 * t, 0.15 * t, 0.4, 0.05 * t))
    g, rivets = gauntlet(fields, ATLAS["gauntlet"], ATLAS["palm"], float(params["gauntlet_cuff_from_wrist"]))
    out["Gauntlet"] = g
    out["TrousersHip"] = skirt(fields, "TrousersHip", ATLAS["trousers_hip"], z_waist + 0.012 * S,
                               lambda th: np.full_like(th, z_crotch + 0.004 * S), 0.006 * S, 48, 8, 1, 0.0, 0.0,
                               0.0015 * S, int(params["seed"]))
    out["TrousersHip"].C = [PINNED] * len(out["TrousersHip"].V)
    legs = Part("TrousersLegs")
    for sd in ("L", "R"):
        hp, kn = lm.side_pt("hip", sd), lm.side_pt("knee", sd)
        t0 = (hp[2] - (z_crotch + 0.035 * S)) / (hp[2] - kn[2])
        a = hp + (kn - hp) * t0
        b = kn + (kn - hp) * 0.06
        legs.extend(limb_wrap(fields, f"leg_{sd}", a, b, 0.008 * S, ATLAS["trousers_leg"], f"TrouserLeg{sd}",
                              n_around=24, rows=10))
    out["TrousersLegs"] = legs
    out["Belt"] = band_ring(fields, "Belt", ATLAS["belt"], z_waist + 0.008 * S, 0.042 * S, 0.0115 * S)
    st, st_path = strap(fields, chart, ATLAS["strap"], 0.04 * S, 0.0165 * S)
    out["Strap"] = st
    wraps = Part("Wraps")
    for sd in ("L", "R"):
        an, kn = lm.side_pt("ankle", sd), lm.side_pt("knee", sd)
        wraps.extend(limb_wrap(fields, f"leg_{sd}", an + (kn - an) * 0.03, an + (kn - an) * 0.52, 0.0035 * S,
                               ATLAS["wraps"], f"CalfWrap{sd}", n_around=20, rows=10))
    out["Wraps"] = wraps
    sandals = Part("Sandals")
    for sd in ("L", "R"):
        sandals.extend(sandal(fields, sd, ATLAS["sandals"]))
    out["Sandals"] = sandals
    for p in out.values():
        if not p.C:
            p.C = [PINNED] * len(p.V)
        elif len(p.C) < len(p.V):
            p.C = p.C + [PINNED] * (len(p.V) - len(p.C))
    out["_rivets"] = rivets  # type: ignore[assignment]
    out["_strap_path"] = st_path  # type: ignore[assignment]
    return out


def rivet_part(centres: list, S: float) -> Part:
    part = Part("Rivets")
    for c in centres:
        uv_sphere(part, np.asarray(c), 0.0032 * S, 6, 4, "brass", tags=TAG_CLOTH)
    part.C = [PINNED] * len(part.V)
    return part


def coverage(body, params: dict, V: np.ndarray, reg: np.ndarray) -> np.ndarray:
    """True for body vertices hidden under opaque clothing (with a margin), rhen.md §8."""
    lm = body.lm
    S = lm.S
    m = 0.03 * S
    z_crotch = float(lm.P("crotch")[2])
    z_nip = float(lm.P("nipple")[2])
    torso = (reg == "torso") & (V[:, 2] > z_crotch + 0.03 * S) & (V[:, 2] < z_nip - 0.02 * S)
    legs = np.zeros(len(V), bool)
    for sd in ("L", "R"):
        kn = lm.side_pt("knee", sd)
        legs |= (reg == f"leg_{sd}") & (V[:, 2] < z_crotch - m) & (V[:, 2] > kn[2] + m)
    sh, wr = lm.side_pt("shoulder", "L"), lm.side_pt("wrist", "L")
    ax = (wr - sh) / np.linalg.norm(wr - sh)
    t = (V - sh) @ ax / np.linalg.norm(wr - sh)
    arm = (reg == "arm_L") & (t > 0.12) & (t < 0.93)
    _ = params
    return torso | legs | arm
