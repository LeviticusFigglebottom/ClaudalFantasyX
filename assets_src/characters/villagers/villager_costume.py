"""Haluna villagers' clothing as procedural cloth panels (no bpy), M2-CHR-03.

Low Reaches dress for everyday village life (bible §5.1; haluna.md §1: indigo, sea blue and undyed
sand cloth, saturated colour only in small notes): wrapped cotton tops, wrap skirts, knee or shin
trousers, a sash at the waist, head wraps and sandals. Every piece is built with the heroes' shared
helpers (asha_costume charts and skirts, rhen_costume torso sheets and limb tubes, toma_costume's
sash and open skirt) from one params block per villager (`_costume` in params/<npc>.json), so seven
characters come from one module and nothing is copied.

The pattern grids are islands of ONE shared villager cloth atlas (ATLAS, painted by
villager_textures.cloth_atlas in near-neutral undyed tones). Each piece names one of four cloth
materials (`cloth_a`, `cloth_b`, `cloth_c` and `leather`); a villager's write_materials row tints
them (character_cloth `col_albedo`), which is where the colour variants come from.

Pieces (each optional): `top` (a wrap top to the waist or hip: V or round neck, sleeveless or with
sleeves; or an open vest), `skirt` (a closed wrap skirt from the waist, flared over the legs),
`trousers` (a pelvis band and two legs), `apron` (an open front panel over the skirt), `sash`
(asha-like band turns with a knot and tails, toma_costume.sash), `headwrap` (a cloth cap over the
scalp with a rolled edge and a knot at the back; or a narrow headband), `sandals` and `wraps`.
`coverage()` says which body vertices are hidden (deleted, asha.md §8.1). Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

import asha_costume as AC
import rhen_costume as RC
import toma_costume as TC
from asha_costume import TAG_CLOTH, Fields, TorsoChart, _panel, cast_last, dir_theta, limb_wrap
from asha_mesh import Part, uv_sphere

# shared villager cloth atlas islands (u0, v0, u1, v1), the shader's UV convention (v down)
ATLAS = {
    "top": (0.0, 0.0, 0.5, 0.30),
    "sleeve_L": (0.5, 0.0, 0.625, 0.14),
    "sleeve_R": (0.625, 0.0, 0.75, 0.14),
    "skirt": (0.0, 0.30, 0.5, 0.62),
    "apron": (0.5, 0.14, 0.75, 0.36),
    "trousers": (0.75, 0.0, 1.0, 0.10),
    "trouser_leg_L": (0.75, 0.10, 0.875, 0.36),
    "trouser_leg_R": (0.875, 0.10, 1.0, 0.36),
    "sash": (0.5, 0.36, 1.0, 0.46),
    "sash_tails": (0.5, 0.46, 0.75, 0.62),
    "headwrap": (0.0, 0.62, 0.5, 0.84),
    "wrap_edge": (0.0, 0.84, 0.5, 0.90),
    "wrap_knot": (0.75, 0.46, 1.0, 0.54),
    "wraps": (0.75, 0.54, 1.0, 0.70),
    "sandals": (0.5, 0.62, 0.75, 0.76),
    "headband": (0.5, 0.76, 0.75, 0.82),
}
CLOTH_MATS = ("cloth_a", "cloth_b", "cloth_c", "leather")
TOP_OFF = 0.0065  # m at S = 1, over the skin (the donor bust sits up to a few mm outside the field)
SLEEVE_OFF = 0.009
SKIRT_OFF = 0.010
TROUSER_OFF = 0.009
APRON_EXTRA = 0.008  # over the skirt
WRAP_OFF = 0.0055
TOP_MARGIN = 0.012  # m at S = 1: body hidden this far inside the top's neckline and armholes
HEADWRAP_OFF = 0.010  # over the scalp (hair is flattened under the wrap)
HEADWRAP_EDGE = 0.006  # extra roll at the edge
BACK_BULGE = 2.6  # x puff: the hair bundled inside the wrap fills it out behind
# the head wrap's lower edge (head heights above the chin) by azimuth (0 front, 90 the side, 180 the
# back): over the hairline at the front, above the ear at the side, down to the nape behind
WRAP_EDGE = ([0, 30, 55, 75, 95, 112, 132, 155, 180], [0.735, 0.725, 0.69, 0.645, 0.625, 0.56, 0.43, 0.335, 0.30])


def _mat(p: Part, mat: str) -> Part:
    """Re-point a helper's generic `cloth` faces at one of the villager cloth materials."""
    p.M = [mat if m == "cloth" else m for m in p.M]
    return p


def _crop_tails(p: Part, z_cut: float) -> Part:
    """toma_costume.sash hangs its tails to the knee; a villager's are shorter: drop the tail faces
    (their UVs are in the sash_tails island) wholly below `z_cut`, and the vertices left unused."""
    u0, v0, u1, v1 = ATLAS["sash_tails"]
    V = p.varr()
    keep_f = []
    for f, uv in zip(p.F, p.UV):
        in_tails = all(u0 - 1e-6 <= a <= u1 + 1e-6 and v0 - 1e-6 <= b <= v1 + 1e-6 for a, b in uv)
        keep_f.append(not (in_tails and all(V[i, 2] < z_cut for i in f)))
    used = sorted({i for f, k in zip(p.F, keep_f) if k for i in f})
    remap = {old: new for new, old in enumerate(used)}
    out = Part(p.name)
    out._mat = getattr(p, "_mat", "cloth")
    out.V = [p.V[i] for i in used]
    out.C = [p.C[i] for i in used] if len(p.C) == len(p.V) else []
    out.T = [p.T[i] for i in used] if len(p.T) == len(p.V) else []
    for f, uv, m, k in zip(p.F, p.UV, p.M, keep_f):
        if k:
            out.F.append(tuple(remap[i] for i in f))
            out.UV.append(uv)
            out.M.append(m)
    return out


def _pad(p: Part) -> Part:
    if len(p.C) < len(p.V):
        p.C = list(p.C) + [(0.0, 0.0, 0.0, 0.0)] * (len(p.V) - len(p.C))
    return p


# ---------------------------------------------------------------------------------------------
# Lines
# ---------------------------------------------------------------------------------------------
def top_line(lm, chart: TorsoChart, th_deg: np.ndarray, top: dict) -> np.ndarray:
    """The top's upper edge: the neckline (V of `neck_v_m` below the notch, or round), plus armholes
    under the shoulders when it is sleeveless."""
    S = lm.S
    neck = chart.z_sh + math.radians(55) * chart.k
    v = float(lm.P("notch")[2] - float(top.get("neck_v_m", 0.06)) * S)
    if float(top.get("sleeve", 0.0)) > 0.0:
        return RC._sym_interp(th_deg, [0, 12, 30, 60, 180], [v, v + 0.03 * S, neck - 0.012 * S, neck, neck])
    arm = float(lm.P("shoulder")[2] - 0.085 * S)
    strap = chart.z_sh + math.radians(24) * chart.k
    return RC._sym_interp(th_deg, [0, 12, 28, 50, 74, 92, 112, 132, 150, 180],
                          [v, v + 0.025 * S, neck - 0.015 * S, strap, arm, arm, strap, neck, neck, neck])


def hem_z(lm, where) -> float:
    """A named hem height: waist, hip, thigh, knee, calf, shin, ankle (or metres above the floor)."""
    if not isinstance(where, str):
        return float(where) * lm.S
    z_waist = float(lm.P("waist")[2])
    z_crotch = float(lm.P("crotch")[2])
    kn = float(lm.side_pt("knee", "L")[2])
    an = float(lm.side_pt("ankle", "L")[2])
    return {"waist": z_waist - 0.03 * lm.S, "hip": 0.5 * (z_waist + z_crotch), "thigh": z_crotch - 0.12 * lm.S,
            "knee": kn + 0.03 * lm.S, "calf": an + 0.62 * (kn - an), "shin": an + 0.35 * (kn - an),
            "ankle": an + 0.10 * (kn - an)}[where]


def wrap_edge_v(phi_deg: np.ndarray, lift: float = 0.0) -> np.ndarray:
    a = np.abs(((np.asarray(phi_deg) + 180.0) % 360.0) - 180.0)
    return np.interp(a, *WRAP_EDGE) + lift


# ---------------------------------------------------------------------------------------------
# Pieces
# ---------------------------------------------------------------------------------------------
def build_top(fields: Fields, chart: TorsoChart, top: dict) -> dict[str, Part]:
    lm = fields.lm
    S = lm.S
    out: dict[str, Part] = {}
    hem = hem_z(lm, top.get("hem", "hip"))
    open_deg = float(top.get("open_deg", 0.0))
    if open_deg > 0.0:  # an open vest: from open_deg round the back to -open_deg
        th = np.linspace(open_deg, 360.0 - open_deg, 50)
        closed = False
    else:
        th = np.linspace(0.0, 360.0, 52, endpoint=False)
        closed = True
    body = RC.torso_sheet(fields, chart, "Top", ATLAS["top"], th, top_line(lm, chart, th, top), hem,
                          float(top.get("off_m", TOP_OFF)) * S, 13, 0.0015 * S, closed,
                          wind_amp=float(top.get("wind", 0.06)))
    out["Top"] = _mat(body, top["mat"])
    sleeve = float(top.get("sleeve", 0.0))
    if sleeve > 0.0:
        for sd in ("L", "R"):
            path = RC.arm_path(lm, sd, 0.03, sleeve, 8)
            p = RC.limb_tube(fields, f"arm_{sd}", path, lambda t: (SLEEVE_OFF + 0.006 * t) * S, ATLAS[f"sleeve_{sd}"],
                             f"Sleeve{sd}", n_around=18, rows=8, back_inset=0.0018 * S, wind_amp=0.05,
                             min_r=0.036 * S)
            out[f"Sleeve{sd}"] = _mat(p, top["mat"])
    return out


def build_trousers(fields: Fields, tr: dict) -> dict[str, Part]:
    lm = fields.lm
    S = lm.S
    z_waist = float(lm.P("waist")[2])
    z_crotch = float(lm.P("crotch")[2])
    out: dict[str, Part] = {}
    th_t = np.linspace(0.0, 360.0, 44, endpoint=False)
    pelvis = Part("TrouserTop")
    pelvis._mat = "cloth"
    rows = 7
    P = np.zeros((rows, len(th_t), 3))
    D = dir_theta(np.radians(th_t))
    for j in range(rows):
        z = z_waist + (z_crotch + 0.015 * S - z_waist) * j / (rows - 1)
        O = np.stack([np.zeros(len(th_t)), np.full(len(th_t), 0.01 * S), np.full(len(th_t), z)], axis=-1)
        r = cast_last(lambda Q: fields.lower(Q) - TROUSER_OFF * S, O, D, 0.5 * S)
        P[j] = O + D * r[:, None]
    _panel(pelvis, P, ATLAS["trousers"], None, True, 0.0018 * S, np.array([0.0, 0.01 * S, 0.0]))
    out["TrouserTop"] = _mat(pelvis, tr["mat"])
    hem = hem_z(lm, tr.get("hem", "knee"))
    loose = float(tr.get("loose_m", 0.012))
    for sd in ("L", "R"):
        path = RC.leg_path(lm, sd, z_crotch + 0.06 * S, hem, 12)
        p = RC.limb_tube(fields, f"leg_{sd}", path,
                         lambda t: (0.0075 + loose * math.sin(math.pi * min(t * 1.1, 1.0)) ** 1.2 + 0.002) * S,
                         ATLAS[f"trouser_leg_{sd}"], f"TrouserLeg{sd}", n_around=22, rows=12,
                         back_inset=0.0018 * S, wind_amp=0.06)
        out[f"TrouserLeg{sd}"] = _mat(p, tr["mat"])
    return out


def build_skirt(fields: Fields, sk: dict, z_top: float, name: str = "Skirt", rect=None, off=SKIRT_OFF) -> Part:
    lm = fields.lm
    S = lm.S
    hem = hem_z(lm, sk.get("hem", "ankle"))
    p = AC.skirt(fields, name, rect or ATLAS["skirt"], z_top, lambda th: np.full_like(th, hem), off * S, 52,
                 int(sk.get("rows", 16)), int(sk.get("folds", 9)), float(sk.get("fold_amp", 0.008)),
                 float(sk.get("flare", 0.16)), 0.0015 * S, int(sk.get("seed", 3)))
    return _mat(p, sk["mat"])


def build_apron(fields: Fields, ap: dict, z_top: float, skirt_flare: float) -> Part:
    lm = fields.lm
    S = lm.S
    half = float(ap.get("half_deg", 50.0))
    th = np.linspace(-half, half, 22)
    p = TC.skirt_open(fields, "Apron", ATLAS["apron"], z_top, hem_z(lm, ap.get("hem", "knee")), th,
                      (SKIRT_OFF + APRON_EXTRA) * S, 10, skirt_flare, 3, 0.002, int(ap.get("seed", 5)))
    return _mat(p, ap["mat"])


def build_headwrap(fields: Fields, hw: dict) -> dict[str, Part]:
    """A cloth cap over the scalp: rows from the rolled lower edge (WRAP_EDGE) up to the crown, cast
    from the head centre onto the head field plus HEADWRAP_OFF, with soft folds; a knot of the same
    cloth at the back. `band_only`: just the rolled edge (a headband)."""
    lm = fields.lm
    S = lm.S
    body = fields.body
    head = body.regions["head"]
    yc = float(lm.P("head_c")[1])
    zc = float(lm.P("chin")[2])
    hc = np.array([0.0, yc + 0.02 * lm.h, zc + 0.55 * lm.h])
    n = 40
    phi = np.radians(np.linspace(0.0, 360.0, n, endpoint=False))
    lift = float(hw.get("edge_lift", 0.0))
    ev = wrap_edge_v(np.degrees(phi), lift)
    band_only = bool(hw.get("band_only", False))
    rng = np.random.default_rng(int(hw.get("seed", 9)))
    phase = rng.uniform(0, 2 * math.pi, 3)
    off = float(hw.get("off_m", HEADWRAP_OFF)) * S
    puff = float(hw.get("puff_m", 0.010)) * S

    def edge_dirs(v_line: np.ndarray) -> np.ndarray:
        # direction from hc to the scalp point at height v_line on azimuth phi (iterated on the field)
        d = np.stack([np.sin(phi), -np.cos(phi), np.zeros(n)], axis=1)
        z = zc + v_line * lm.h
        for _ in range(6):
            r = cast_last(lambda Q: head.sdf(Q) - off, np.repeat(hc[None, :], n, axis=0), d, 0.5 * lm.h)
            q = hc + d * r[:, None]
            d = d + np.outer(z - q[:, 2], [0.0, 0.0, 1.0]) / (0.25 * lm.h)
            d /= np.linalg.norm(d, axis=1, keepdims=True)
        return d

    d_edge = edge_dirs(ev)
    out: dict[str, Part] = {}
    mat = hw["mat"]
    up = np.array([0.0, 0.25, 1.0])
    up /= np.linalg.norm(up)
    rows = 3 if band_only else 11
    width_band = float(hw.get("band_m", 0.035)) * S
    P = np.zeros((rows, n, 3))
    for j in range(rows):
        t = j / (rows - 1)
        if band_only:
            d = edge_dirs(ev + (width_band / lm.h) * t)
        else:
            a = 0.92 * t ** 0.9
            d = d_edge * (1 - a) + up * a
            d /= np.linalg.norm(d, axis=1, keepdims=True)
        O = np.repeat(hc[None, :], n, axis=0)
        roll = HEADWRAP_EDGE * S * math.sin(math.pi * min(j / 2.0, 1.0)) if not band_only else 0.004 * S
        fold = 0.0 if band_only else puff * (0.35 + 0.65 * t) * (
            0.6 * np.sin(5 * phi + phase[0] + 2.0 * t) + 0.4 * np.sin(9 * phi + phase[1] - 3.0 * t))
        back = 0.0 if band_only else puff * BACK_BULGE * np.clip(np.cos(phi - math.pi), 0, 1) ** 2 * math.sin(math.pi * t ** 0.8)
        r = cast_last(lambda Q: head.sdf(Q) - off, O, d, 0.5 * lm.h) + roll + np.maximum(fold, -0.4 * puff) + back
        P[j] = O + d * r[:, None]
    cap = Part("HeadWrap")
    cap._mat = "cloth"
    rect = ATLAS["headband"] if band_only else ATLAS["headwrap"]
    # rows run from the edge (row 0) up: flip so the panel's row 0 is the top like the others
    _panel(cap, P[::-1].copy(), rect, None, True, 0.002 * S if band_only else None, hc)
    if not band_only:
        # close the crown with a fan to its centre
        top = P[-1]
        c_id = cap.add_v(top.mean(axis=0) + up * 0.004 * S, tag=TAG_CLOTH)
        ring = list(range(0, n))  # row 0 of the flipped grid is the crown ring (the first n vertices)
        u0, v0, u1, v1 = rect
        for i in range(n):
            a, b = ring[i], ring[(i + 1) % n]
            pa, pb, pc = cap.V[a], cap.V[b], cap.V[c_id]
            outward = np.cross(pb - pa, pc - pa) @ ((pa + pb + pc) / 3.0 - hc) > 0
            f = (a, b, c_id) if outward else (b, a, c_id)
            cap.add_f(f, [(u0 + (u1 - u0) * i / n, v0), (u0 + (u1 - u0) * (i + 1) / n, v0), (0.5 * (u0 + u1), v0)],
                      "cloth")
        # the knot: two squashed lobes and a short tail at the back, low on the crown
        i_back = n // 2
        kc = P[int(rows * 0.35), i_back]
        kd = (kc - hc) / np.linalg.norm(kc - hc)
        kn = Part("WrapKnot")
        ks = float(hw.get("knot_m", 0.032)) * S
        for dx in (-0.6, 0.6):
            side = np.cross(np.array([0.0, 0.0, 1.0]), kd)
            side /= np.linalg.norm(side)
            uv_sphere(kn, kc + side * dx * ks + kd * 0.4 * ks, np.array([0.75, 0.55, 0.6]) * ks, 10, 6, "cloth",
                      axis_fwd=kd, uv_rect=ATLAS["wrap_knot"], tags=TAG_CLOTH)
        cap.extend(kn)
    out["HeadWrap"] = _mat(_pad(cap), mat)
    return out


# ---------------------------------------------------------------------------------------------
def build_costume(body, params: dict) -> dict[str, Part]:
    lm = body.lm
    S = lm.S
    fields = Fields(body)
    chart = TorsoChart(lm)
    z_waist = float(lm.P("waist")[2])
    out: dict[str, Part] = {}
    if params.get("top"):
        out.update(build_top(fields, chart, params["top"]))
    if params.get("trousers"):
        out.update(build_trousers(fields, params["trousers"]))
    sk = params.get("skirt")
    if sk:
        out["Skirt"] = build_skirt(fields, sk, z_waist - 0.02 * S)
    if params.get("apron") and sk:
        out["Apron"] = build_apron(fields, params["apron"], z_waist - 0.015 * S, float(sk.get("flare", 0.16)))
    sash = params.get("sash")
    if sash:
        # the band sits over the outermost cloth at the waist: never the sleeves (in the A-pose a long
        # sleeve hangs at waist height, and the band would span the arms)
        rings = [p.varr() for k, p in out.items() if not k.startswith("Sleeve")]
        outer = np.concatenate(rings) if rings else lm.P("waist")[None, :]
        z_c = z_waist - 0.01 * S
        p = TC.sash(fields, outer, z_c, float(sash["width_m"]) * S, int(sash.get("turns", 2)), ATLAS["sash"],
                    ATLAS["sash_tails"])
        out["Sash"] = _mat(_crop_tails(p, z_c - (0.04 + float(sash.get("tails_m", 0.24))) * S), sash["mat"])
    if params.get("headwrap"):
        out.update(build_headwrap(fields, params["headwrap"]))
    wr = params.get("wraps")
    if wr:
        wraps = Part("Wraps")
        w0, w1 = (float(x) for x in wr["span"])
        for sd in ("L", "R"):
            an, kn = lm.side_pt("ankle", sd), lm.side_pt("knee", sd)
            wraps.extend(limb_wrap(fields, f"leg_{sd}", an + (kn - an) * w0, an + (kn - an) * w1,
                                   float(wr.get("off_m", WRAP_OFF)) * S, ATLAS["wraps"], f"Wrap{sd}", n_around=18,
                                   rows=6))
        out["Wraps"] = _mat(wraps, wr["mat"])
    if params.get("sandals"):
        sandals = Part("Sandals")
        for sd in ("L", "R"):
            sandals.extend(AC.sandal(fields, sd, ATLAS["sandals"]))
        out["Sandals"] = _mat(sandals, params["sandals"])
    for p in out.values():
        _pad(p)
    return out


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
    legs = (reg == "leg_L") | (reg == "leg_R") | torso
    hidden = np.zeros(len(V), dtype=bool)
    top = params.get("top")
    if top:
        hem = hem_z(lm, top.get("hem", "hip"))
        under = torso & (H < top_line(lm, chart, th_deg, top) - TOP_MARGIN * S) & (V[:, 2] > hem + m)
        od = float(top.get("open_deg", 0.0))
        if od > 0.0:
            a = np.abs(((th_deg + 180.0) % 360.0) - 180.0)
            under &= a > od + 14.0
        hidden |= under
        sl = float(top.get("sleeve", 0.0))
        if sl > 0.0:
            for sd in ("L", "R"):
                sh, wr = lm.side_pt("shoulder", sd), lm.side_pt("wrist", sd)
                el = lm.side_pt("elbow", sd)
                # arm parameter as arm_path: 0 shoulder, 0.5 elbow, 1 wrist
                t_up = (V - sh) @ (el - sh) / ((el - sh) @ (el - sh)) * 0.5
                t_lo = 0.5 + (V - el) @ (wr - el) / ((wr - el) @ (wr - el)) * 0.5
                t = np.where(t_up <= 0.5, t_up, t_lo)
                hidden |= (reg == f"arm_{sd}") & (t > -0.10) & (t < sl - 0.05)
    tr = params.get("trousers")
    if tr:
        hem = hem_z(lm, tr.get("hem", "knee"))
        hidden |= legs & (V[:, 2] < z_waist) & (V[:, 2] > hem + 0.03 * S)
    sk = params.get("skirt")
    if sk:
        hem = hem_z(lm, sk.get("hem", "ankle"))
        hidden |= legs & (V[:, 2] < z_waist - 0.02 * S - 0.5 * m) & (V[:, 2] > hem + 0.045 * S)
    wr = params.get("wraps")
    if wr:
        w0, w1 = (float(x) for x in wr["span"])
        for sd in ("L", "R"):
            an, kn = lm.side_pt("ankle", sd), lm.side_pt("knee", sd)
            ax = kn - an
            t = (V - an) @ ax / (ax @ ax)
            hidden |= (reg == f"leg_{sd}") & (t > w0 + 0.04) & (t < w1 - 0.03)
    return hidden
