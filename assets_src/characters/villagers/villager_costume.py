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

M3-CHR-509..517 add optional keys whose defaults leave every earlier villager byte-identical: `top.cuff_roll_m` (a
sleeve pushed up and rolled: a thicker band of cloth at its end, the smith and the wrights), `apron.over_trousers`
(an apron with no skirt under it: the smith's and the shopkeeper's over their trousers, `apron.flare` its hang) and
`apron.extra_m` (the apron's offset over what it covers), and a fifth cloth material, `cloth_d` (the smith's leather
apron, the clerk's tabard), tinted like the other three.

M3-CHR-526..539's dialogue polish adds more optional keys, again leaving every other villager byte-identical:
`sash.tail_w_k`, `sash.knot_k` and `sash.cord_knots` (a narrow knotted cord: Hobb's captain's cord),
`headwrap.edge_off_m` (a wrap's or headband's edge drawn in tight to the skin), `headwrap.press_hair` (the hair under
a headband drawn inside it, build_villager), and two pieces: `shawl` (a knotted netting shawl built as twine) and
`wrist_cord` (a cord tied round one wrist).
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
CLOTH_MATS = ("cloth_a", "cloth_b", "cloth_c", "leather", "cloth_d")  # cloth_d: M3-CHR-516 (optional)
TOP_OFF = 0.0065  # m at S = 1, over the skin (the donor bust sits up to a few mm outside the field)
SLEEVE_OFF = 0.009
SKIRT_OFF = 0.010
TROUSER_OFF = 0.009
APRON_EXTRA = 0.008  # over the skirt
APRON_FLARE = 0.16  # an apron over trousers (no skirt to take the flare from) hangs as the default skirt does
CUFF_ROLL_SPAN = 0.14  # of the sleeve's length: the rolled band at a pushed-up sleeve's end (`cuff_roll_m`)
WRAP_OFF = 0.0055
WAIST_KNOT_VERTS = 14 * 7 + 2  # toma_costume.sash's knot: a 14 x 8 uv_sphere, just before the tails
CORD_KNOT_CLEAR = 0.03  # m at S = 1: the lowest cord knot stays this far above the cropped tail's end
CORD_KNOT_SPAN = (0.25, 0.85)
EDGE_CORD_K = 1.4  # a netting shawl's edge cords against its mesh cords
WRIST_CORD_RING = 16  # segments round a wrist cord  # the cord knots' spread down the kept tail (share of its length)
TOP_MARGIN = 0.012  # m at S = 1: body hidden this far inside the top's neckline and armholes
ARMHOLE_DROP = 0.085  # m at S = 1 below the shoulder joint: a sleeveless top's armhole (the M2-CHR-03 default)
# `armhole_cut: "tank"` (M3-CHR-526/534, optional): an ordinary sleeveless top. The default sleeveless line runs from
# the V up to a point at the side of the neck and straight down to the armpit, front and back, with nothing over the
# shoulder: at dialogue range a halter. One torso chart cannot hold a strap over the shoulder (the crest and the
# armpit lie on the same azimuths), so the tank cut is two pieces: the body panel with a scoop neck and the armhole
# floor unchanged, rising at the front and back to a strap foot under each strap, and a strap per side laid over the
# shoulder crest from foot to foot (its own grid, cast over the crest in the side plane).
TANK_STRAP_X = (0.40, 0.60)  # the strap's inner and outer edges, as shares of the acromion's half-width
TANK_STRAP_PSI = (-20.0, 200.0)  # degrees in the side plane from the front (0) over the crest (90) to the back (180)
TANK_STRAP_ROWS = 19  # along the strap
TANK_STRAP_COLS = 4  # across it
TANK_STRAP_LIFT = 0.0015  # m at S = 1 over the panel's offset: where they overlap the strap lies on the panel
TANK_STRAP_ORIGIN_DZ = -0.01  # m at S = 1 off the chart's shoulder pivot height: the casts' centre in the shoulder
TANK_FOOT_ROWS = (6, 2)  # strap rows the panel's foot runs up under (the overlap) at its inner and outer edges
TANK_FOOT_FLARE = 6.0  # degrees inside the front foot where the scoop neck starts down to the V
TANK_SCOOP = 0.15  # how far down toward the V's point the neckline is there (share of the foot's height over it)
TANK_ARM_FLOOR = (76.0, 92.0)  # |azimuth| span of the armhole's floor (the default line's 74-92, as the arm swings)
TANK_COLUMNS = 104  # the panel's azimuth columns (the default top has 52): the feet are a few degrees wide
KEEP_ABOVE_KNEE = 0.16  # m at S = 1 of thigh kept above the knee under a skirt with keep_legs (asha_costume's)
HEADWRAP_OFF = 0.010  # over the scalp (hair is flattened under the wrap)
HEADWRAP_EDGE = 0.006  # extra roll at the edge
PRESS_BINS = 72  # `press_hair`: azimuth bins of the band's height span and inner radius
PRESS_FADE_H = 0.03  # head heights above and below the band over which the hair's pull fades
BAND_TUCK_ROWS = 5  # a headband with `edge_off_m`: rows across it, so its rounded face reads
EDGE_TUCK_ROWS = 2.0  # `edge_off_m`: rows over which a wrap's edge rises from its tuck to the cap's offset
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


def _cord_shape(p: Part, sash: dict, z_cut: float, S: float) -> Part | None:
    """M3-CHR-538 (optional keys; a sash without them is untouched): a narrow sash worn as a cord. `tail_w_k` narrows
    both tails about their centre column, `knot_k` shrinks the waist knot, and `cord_knots` ties that many small
    knots down the front tail (`cord_knot_m` across; spaced over the tail's kept length). Edits `p` in place (the
    tail grids are TC.sash's: per tail and layer, rows x columns, row-major) and returns the knots as a Part to add
    after the tails are cropped (their faces are not in the tails' island, so the crop would keep them anyway)."""
    w_k = float(sash.get("tail_w_k", 1.0))
    k_k = float(sash.get("knot_k", 1.0))
    n_knots = int(sash.get("cord_knots", 0))
    if w_k == 1.0 and k_k == 1.0 and not n_knots:
        return None
    first = p.tail_first
    if k_k != 1.0:
        ids = range(first - WAIST_KNOT_VERTS, first)
        c = np.mean([p.V[i] for i in ids], axis=0)
        for i in ids:
            p.V[i] = c + (np.asarray(p.V[i]) - c) * k_k
    centre_lines = []
    for t0, rows, cols, layers in p.tail_rows:
        mid = cols // 2
        line = np.array([p.V[first + t0 + j * cols + mid] for j in range(rows)])
        side = np.array([np.asarray(p.V[first + t0 + j * cols + cols - 1]) - p.V[first + t0 + j * cols]
                         for j in range(rows)])
        centre_lines.append((line, side))
        for layer in range(layers):
            base = first + t0 + layer * rows * cols
            for j in range(rows):
                c = np.asarray(p.V[base + j * cols + mid])
                for i in range(cols):
                    q = base + j * cols + i
                    p.V[q] = c + (np.asarray(p.V[q]) - c) * w_k
    if not n_knots:
        return None
    line, side = centre_lines[0]
    keep = line[:, 2] > z_cut + CORD_KNOT_CLEAR * S
    kept, side = line[keep], side[keep]
    knots = Part("CordKnots")
    r = float(sash.get("cord_knot_m", 0.016)) * S
    u0, v0, u1, v1 = ATLAS["wrap_knot"]
    seg = np.cumsum(np.r_[0.0, np.linalg.norm(np.diff(kept, axis=0), axis=1)])
    for k in range(n_knots):
        s = seg[-1] * (CORD_KNOT_SPAN[0] + (CORD_KNOT_SPAN[1] - CORD_KNOT_SPAN[0]) * k / max(n_knots - 1, 1))
        c = np.array([np.interp(s, seg, kept[:, a]) for a in range(3)])
        j = min(int(np.searchsorted(seg, s)), len(kept) - 1)
        down = kept[min(j + 1, len(kept) - 1)] - kept[max(j - 1, 0)]
        out_d = np.cross(side[j], down)  # the tail's own face normal there, turned away from the waist axis
        out_d *= np.sign(out_d @ np.array([c[0], c[1] - 0.01 * S, 0.0]))
        out_d /= np.linalg.norm(out_d)
        uv_sphere(knots, c + out_d * 0.3 * r, np.array([0.5, 0.42, 0.62]) * r, 10, 6, "cloth", axis_fwd=out_d,
                  uv_rect=(u0, v0, u1, v1), tags=TAG_CLOTH)
    knots.C = [(0.0, 0.0, 0.0, 0.0)] * len(knots.V)
    return knots


def _pad(p: Part) -> Part:
    if len(p.C) < len(p.V):
        p.C = list(p.C) + [(0.0, 0.0, 0.0, 0.0)] * (len(p.V) - len(p.C))
    return p


# ---------------------------------------------------------------------------------------------
# Lines
# ---------------------------------------------------------------------------------------------
def top_line(lm, chart: TorsoChart, th_deg: np.ndarray, top: dict, fields: Fields | None = None) -> np.ndarray:
    """The top's upper edge: the neckline (V of `neck_v_m` below the notch, or round), plus armholes
    under the shoulders when it is sleeveless (the tank cut needs `fields`: its feet sit under the straps)."""
    S = lm.S
    neck = chart.z_sh + math.radians(55) * chart.k
    v = float(lm.P("notch")[2] - float(top.get("neck_v_m", 0.06)) * S)
    if float(top.get("sleeve", 0.0)) > 0.0:
        return RC._sym_interp(th_deg, [0, 12, 30, 60, 180], [v, v + 0.03 * S, neck - 0.012 * S, neck, neck])
    # `armhole_drop_m` below the shoulder joint (M3-CHR-03: 0.115 as M1-CHR-14's vest and tunic; 0.085 sits at the
    # armpit, where a lowered arm cuts it)
    arm = float(lm.P("shoulder")[2] - float(top.get("armhole_drop_m", ARMHOLE_DROP)) * S)
    if top.get("armhole_cut") == "tank":  # M3-CHR-526/534 (optional): straps on the shoulders, not up the neck
        return _tank_line(fields, chart, th_deg, top, arm, v)
    strap = chart.z_sh + math.radians(24) * chart.k
    return RC._sym_interp(th_deg, [0, 12, 28, 50, 74, 92, 112, 132, 150, 180],
                          [v, v + 0.025 * S, neck - 0.015 * S, strap, arm, arm, strap, neck, neck, neck])


def tank_straps(fields: Fields, chart: TorsoChart, top: dict) -> dict[str, np.ndarray]:
    """The tank cut's strap grids, side -> P[row along (front -> back), column across (inner -> outer)]: rays from a
    centre in the shoulder (at the strap's x) swept in the side plane over the crest, cast onto the fitting surface at
    the panel's offset plus TANK_STRAP_LIFT."""
    lm = fields.lm
    S = lm.S
    off = (float(top.get("off_m", TOP_OFF)) + TANK_STRAP_LIFT) * S
    xs = float(lm.P("acromion")[0]) * np.linspace(TANK_STRAP_X[0], TANK_STRAP_X[1], TANK_STRAP_COLS)
    psi = np.radians(np.linspace(TANK_STRAP_PSI[0], TANK_STRAP_PSI[1], TANK_STRAP_ROWS))
    y0 = float(lm.P("shoulder")[1])
    z0 = chart.z_sh + TANK_STRAP_ORIGIN_DZ * S
    out = {}
    for sd, sg in (("L", 1.0), ("R", -1.0)):
        P = np.zeros((TANK_STRAP_ROWS, TANK_STRAP_COLS, 3))
        for i, x in enumerate(xs):
            O = np.tile(np.array([sg * x, y0, z0]), (TANK_STRAP_ROWS, 1))
            D = np.stack([np.zeros_like(psi), -np.cos(psi), np.sin(psi)], axis=-1)
            r = cast_last(lambda Q: fields.upper(Q) - off, O, D, 0.3 * S)
            P[:, i] = O + D * r[:, None]
        out[sd] = P
    return out


def _tank_line(fields: Fields, chart: TorsoChart, th_deg: np.ndarray, top: dict, arm: float, v: float) -> np.ndarray:
    """The tank cut's panel line by |azimuth|: the V, a scoop up to the front foot under the strap (as high as the
    strap's TANK_FOOT_ROWS-th row, so the strap's end lies over the panel), the armhole's front falling to the default
    floor, and the same at the back, where the line runs on level across the back of the neck."""
    S = fields.lm.S
    P = tank_straps(fields, chart, top)["L"]
    k_in, k_out = TANK_FOOT_ROWS
    f_in, hf_in = (float(q[0]) for q in chart.H_of(P[k_in, :1]))
    f_out, hf_out = (float(q[0]) for q in chart.H_of(P[k_out, -1:]))
    b_in, hb_in = (float(q[0]) for q in chart.H_of(P[-1 - k_in, :1]))
    b_out, hb_out = (float(q[0]) for q in chart.H_of(P[-1 - k_out, -1:]))
    f_in, f_out, b_in, b_out = (math.degrees(a) for a in (f_in, f_out, b_in, b_out))
    lo, hi = TANK_ARM_FLOOR
    xs = [0.0, 12.0, f_in - TANK_FOOT_FLARE, f_in, min(f_out, lo - 1.0), lo, hi, max(b_out, hi + 1.0), b_in, 180.0]
    vs = [v, v + 0.025 * S, hf_in - TANK_SCOOP * (hf_in - v), hf_in, hf_out, arm, arm, hb_out, hb_in, hb_in]
    return RC._sym_interp(th_deg, xs, vs)


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
        tank = top.get("armhole_cut") == "tank"
        th = np.linspace(0.0, 360.0, TANK_COLUMNS if tank else 52, endpoint=False)
        closed = True
    body = RC.torso_sheet(fields, chart, "Top", ATLAS["top"], th, top_line(lm, chart, th, top, fields), hem,
                          float(top.get("off_m", TOP_OFF)) * S, 13, 0.0015 * S, closed,
                          wind_amp=float(top.get("wind", 0.06)))
    out["Top"] = _mat(body, top["mat"])
    if top.get("armhole_cut") == "tank":
        centre = np.array([0.0, chart.y_axis, chart.z_sh])
        for sd, P in tank_straps(fields, chart, top).items():
            strap = Part(f"TopStrap{sd}")
            strap._mat = "cloth"
            AC._panel(strap, P, ATLAS[f"sleeve_{sd}"], None, False, 0.0015 * S, centre)  # a sleeveless top's free island
            out[f"TopStrap{sd}"] = _mat(_pad(strap), top["mat"])
    sleeve = float(top.get("sleeve", 0.0))
    roll = float(top.get("cuff_roll_m", 0.0))
    if roll > 0.0:  # M3-CHR-516: a pushed-up sleeve, rolled: the cloth thickens over the last CUFF_ROLL_SPAN
        def radius(t: float) -> float:
            k = min(max((t - (1.0 - CUFF_ROLL_SPAN)) / CUFF_ROLL_SPAN, 0.0), 1.0)
            return (SLEEVE_OFF + 0.006 * t + roll * math.sin(math.pi * min(k * 1.6, 1.0)) ** 0.5) * S
    else:
        def radius(t: float) -> float:
            return (SLEEVE_OFF + 0.006 * t) * S
    if sleeve > 0.0:
        for sd in ("L", "R"):
            path = RC.arm_path(lm, sd, 0.03, sleeve, 8)
            p = RC.limb_tube(fields, f"arm_{sd}", path, radius, ATLAS[f"sleeve_{sd}"],
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
                      (SKIRT_OFF + float(ap.get("extra_m", APRON_EXTRA))) * S, 10, skirt_flare, 3, 0.002,
                      int(ap.get("seed", 5)))
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
    tuck = float(hw["edge_off_m"]) * S if "edge_off_m" in hw else None

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
    rows = (BAND_TUCK_ROWS if tuck is not None else 3) if band_only else 11
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
        off_j = off
        if tuck is not None:  # M3-CHR-539 (optional `edge_off_m`): the edge drawn in tight to the skin
            # a cap rises from its tucked edge over EDGE_TUCK_ROWS rows; a headband is tight at both edges
            k = math.sin(math.pi * t) if band_only else min(j / EDGE_TUCK_ROWS, 1.0)
            off_j = tuck + (off - tuck) * k
            fold = fold * k
            if band_only:
                roll = roll * k
        r = cast_last(lambda Q: head.sdf(Q) - off_j, O, d, 0.5 * lm.h) + roll + np.maximum(fold, -0.4 * puff) + back
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
# M3-CHR-539 (optional pieces; a villager without them is untouched): a netting shawl and a wrist cord
# ---------------------------------------------------------------------------------------------
SHAWL_OFF = 0.016  # m at S = 1 over the skin: over the top and its folds
SHAWL_TOP = 50.0  # degrees of elevation over the shoulder (TorsoChart): the shawl's upper edge round the neck
# the shawl's lower edge, m below the shoulder pivot by |azimuth| (front 0 .. back 180): short over the shoulders, a
# point down the back, the two ends lying on the chest
SHAWL_DROP = ([0, 30, 60, 90, 120, 150, 180], [0.14, 0.13, 0.08, 0.045, 0.12, 0.22, 0.27])
SHAWL_ROWS = 14
SHAWL_COLS = 64
SHAWL_SOLID_BACK = 0.0015  # m at S = 1: a solid shawl's back-face inset (M4-A2P-050)
SHAWL_SOLID_GRID = (32, 10)  # a solid shawl's columns and rows: plain cloth needs less than the netting's sampling
NET_SIDES = 3  # a twine cord's cross-section
NET_SAMPLES = 2  # samples per sheet row along a cord


def _cord_tube(part: Part, pts: np.ndarray, out: np.ndarray, r: float, rect, mat: str = "cloth") -> None:
    """A thin closed tube of NET_SIDES sides along `pts` (its first side faces `out`), for twine and cords."""
    if len(pts) < 2:
        return
    T = np.gradient(pts, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
    n = out - np.sum(out * T, axis=1, keepdims=True) * T
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    b = np.cross(T, n)
    u0, v0, u1, v1 = rect
    ids = []
    for k in range(len(pts)):
        ring = []
        for a in range(NET_SIDES):
            ang = 2.0 * math.pi * a / NET_SIDES
            ring.append(part.add_v(pts[k] + (n[k] * math.cos(ang) + b[k] * math.sin(ang)) * r, tag=TAG_CLOTH))
        ids.append(ring)
    for k in range(len(pts) - 1):
        for a in range(NET_SIDES):
            a2 = (a + 1) % NET_SIDES
            q = (ids[k][a], ids[k][a2], ids[k + 1][a2], ids[k + 1][a])
            uv = [(u0 + (u1 - u0) * a / NET_SIDES, v0 + (v1 - v0) * k / (len(pts) - 1)),
                  (u0 + (u1 - u0) * (a + 1) / NET_SIDES, v0 + (v1 - v0) * k / (len(pts) - 1)),
                  (u0 + (u1 - u0) * (a + 1) / NET_SIDES, v0 + (v1 - v0) * (k + 1) / (len(pts) - 1)),
                  (u0 + (u1 - u0) * a / NET_SIDES, v0 + (v1 - v0) * (k + 1) / (len(pts) - 1))]
            part.add_f(q, uv, mat)


def build_shawl(fields: Fields, chart: TorsoChart, sh: dict) -> Part:
    """A knotted netting shawl over the shoulders (act1_ch08.md, Marra): a sheet cast over the top from the neck to
    SHAWL_DROP, open at the front by `open_deg`, and built as twine only: two families of diagonal cords make the
    diamond mesh (`mesh_m` across a diamond), with a cord along the neck edge and the hem. `cord_mm` thick."""
    lm = fields.lm
    S = lm.S
    od = float(sh.get("open_deg", 28.0))
    th = np.linspace(od, 360.0 - od, SHAWL_COLS)
    top = np.full(len(th), chart.z_sh + math.radians(SHAWL_TOP) * chart.k)
    bot = chart.z_sh - RC._sym_interp(th, *SHAWL_DROP) * S * float(sh.get("drop_k", 1.0))
    if sh.get("solid"):  # M4-A2P-050 (optional): a cloth shawl (Merel's bridal cloth), the sheet with a back face,
        # on the head wrap's crepe island unless `island` names another
        ths = np.linspace(od, 360.0 - od, SHAWL_SOLID_GRID[0])
        sheet = RC.torso_sheet(fields, chart, "Shawl", ATLAS[sh.get("island", "headwrap")], ths, top[:len(ths)],
                               chart.z_sh - RC._sym_interp(ths, *SHAWL_DROP) * S * float(sh.get("drop_k", 1.0)),
                               float(sh.get("off_m", SHAWL_OFF)) * S, SHAWL_SOLID_GRID[1], SHAWL_SOLID_BACK * S, False,
                               wind_amp=float(sh.get("wind", 0.06)))
        return _mat(sheet, sh["mat"])
    sheet = RC.torso_sheet(fields, chart, "ShawlSheet", ATLAS["wraps"], th, top, bot,
                           float(sh.get("off_m", SHAWL_OFF)) * S, SHAWL_ROWS, None, False)
    P = sheet.grid_P
    centre = np.array([0.0, chart.y_axis, 0.0])
    N = AC._outward(P, AC._grid_normals(P, False), centre)
    r = 0.5e-3 * float(sh.get("cord_mm", 3.0)) * S
    part = Part("Shawl")
    part._mat = "cloth"
    rect = ATLAS["wraps"]

    def sample(ii: np.ndarray, jj: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        i0 = np.clip(np.floor(ii).astype(int), 0, SHAWL_COLS - 2)
        j0 = np.clip(np.floor(jj).astype(int), 0, SHAWL_ROWS - 2)
        fi, fj = (ii - i0)[:, None], (jj - j0)[:, None]

        def bil(A):
            return (A[j0, i0] * (1 - fi) * (1 - fj) + A[j0, i0 + 1] * fi * (1 - fj) + A[j0 + 1, i0] * (1 - fi) * fj
                    + A[j0 + 1, i0 + 1] * fi * fj)

        n = bil(N)
        return bil(P) + n * r, n

    # cell size in grid units: columns per metre along the hem, rows per metre down the back
    span_u = float(np.sum(np.linalg.norm(np.diff(P[SHAWL_ROWS // 2], axis=0), axis=1))) / (SHAWL_COLS - 1)
    span_v = float(np.linalg.norm(P[-1, SHAWL_COLS // 2] - P[0, SHAWL_COLS // 2])) / (SHAWL_ROWS - 1)
    mesh = float(sh.get("mesh_m", 0.05)) * S
    step_i = 0.5 * mesh / span_u  # columns between neighbouring cords of one family along a row
    slope = span_v / span_u  # columns per row for a 45-degree cord
    jj = np.linspace(0.0, SHAWL_ROWS - 1, (SHAWL_ROWS - 1) * NET_SAMPLES + 1)
    starts = np.arange(-slope * (SHAWL_ROWS - 1), SHAWL_COLS - 1 + slope * (SHAWL_ROWS - 1), 2.0 * step_i)
    for sgn in (1.0, -1.0):
        for i0 in starts:
            ii = i0 + sgn * slope * jj
            ok = (ii >= 0.0) & (ii <= SHAWL_COLS - 1)
            if ok.sum() < 2:
                continue
            pts, n = sample(ii[ok], jj[ok])
            _cord_tube(part, pts, n, r, rect)
    for j in (0.0, SHAWL_ROWS - 1.0):
        ii = np.linspace(0.0, SHAWL_COLS - 1, (SHAWL_COLS - 1) + 1)
        pts, n = sample(ii, np.full(len(ii), j))
        _cord_tube(part, pts, n, r * EDGE_CORD_K, rect)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return _mat(part, sh["mat"])


def build_wrist_cord(fields: Fields, wc: dict) -> Part:
    """A cord tied round one wrist with a single knot (act1_ch08.md: Marra's faded watch-red stair-watch cord): a
    ring cast onto the forearm `at` of the way from the wrist to the elbow, `cord_mm` thick, the knot on the back of
    the wrist."""
    lm = fields.lm
    S = lm.S
    sd = wc.get("side", "L")
    wr, el = lm.side_pt("wrist", sd), lm.side_pt("elbow", sd)
    ax = (el - wr) / np.linalg.norm(el - wr)
    c = wr + (el - wr) * float(wc.get("at", 0.05))
    ref = np.array([0.0, 0.0, 1.0]) - ax[2] * ax
    ref /= np.linalg.norm(ref)
    e2 = np.cross(ax, ref)
    n = WRIST_CORD_RING
    a = np.linspace(0.0, 2.0 * math.pi, n + 1)
    D = np.cos(a)[:, None] * ref[None, :] + np.sin(a)[:, None] * e2[None, :]
    r = 0.5e-3 * float(wc.get("cord_mm", 4.0)) * S
    rad = cast_last(fields.region(f"arm_{sd}"), np.repeat(c[None, :], n + 1, axis=0), D, 0.1 * S) + r * 1.2
    pts = c + D * rad[:, None]
    part = Part("WristCord")
    part._mat = "cloth"
    _cord_tube(part, pts, D, r, ATLAS["wrap_knot"])
    k = float(wc.get("knot_m", 0.012)) * S
    i_top = int(np.argmax(D @ ref))  # the back of the wrist faces up in the A-pose
    uv_sphere(part, pts[i_top] + D[i_top] * 0.4 * k, np.array([0.55, 0.45, 0.5]) * k, 8, 5, "cloth",
              axis_fwd=D[i_top], uv_rect=ATLAS["wrap_knot"], tags=TAG_CLOTH)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return _mat(part, wc["mat"])


def press_under_band(H: np.ndarray, band: Part, lm, clear: float) -> np.ndarray:
    """Hair under a headband (optional `headwrap.press_hair`, the clearance in m at S = 1): the band grips the hair, so
    every hair vertex at the band's height, by azimuth, is drawn in radially from the head centre (as build_headwrap
    casts) to `clear` inside the band's inner face; just above and below it the pull fades over PRESS_FADE_H head
    heights, so the hair swells back out over the band instead of passing through it."""
    yc = float(lm.P("head_c")[1])
    zc = float(lm.P("chin")[2])
    hc = np.array([0.0, yc + 0.02 * lm.h, zc + 0.55 * lm.h])
    B = band.varr()
    nb = len(B) // 2  # the band's front layer (its back layer is inset under it)
    Bq = B[:nb] - hc
    bphi = np.arctan2(Bq[:, 0], -Bq[:, 1])
    bins = np.linspace(-math.pi, math.pi, PRESS_BINS + 1)
    idx = np.clip(np.digitize(bphi, bins) - 1, 0, PRESS_BINS - 1)
    lo = np.full(PRESS_BINS, np.inf)
    hi = np.full(PRESS_BINS, -np.inf)
    rin = np.full(PRESS_BINS, np.inf)
    bz = B[:nb, 2]
    br = np.linalg.norm(Bq, axis=1)
    for k in range(PRESS_BINS):
        m = idx == k
        if m.any():
            lo[k], hi[k], rin[k] = bz[m].min(), bz[m].max(), br[m].min()
    Q = H - hc
    phi = np.arctan2(Q[:, 0], -Q[:, 1])
    k = np.clip(np.digitize(phi, bins) - 1, 0, PRESS_BINS - 1)
    ok = np.isfinite(rin[k])
    fade = PRESS_FADE_H * lm.h
    z = H[:, 2]
    w = np.where(ok, np.clip(1.0 - np.maximum(lo[k] - z, z - hi[k]) / fade, 0.0, 1.0), 0.0)
    w = np.where(ok & (z >= lo[k]) & (z <= hi[k]), 1.0, w)
    r = np.linalg.norm(Q, axis=1)
    target = np.where(ok, np.minimum(r, rin[k] - clear), r)
    r_new = r + (target - r) * w
    return hc + Q * (r_new / np.maximum(r, 1e-12))[:, None]


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
    ap = params.get("apron")
    if ap and sk:
        out["Apron"] = build_apron(fields, ap, z_waist - 0.015 * S, float(sk.get("flare", 0.16)))
    elif ap and ap.get("over_trousers"):  # M3-CHR-512/516: an apron straight over the trousers
        out["Apron"] = build_apron(fields, ap, z_waist - 0.015 * S, float(ap.get("flare", APRON_FLARE)))
    sash = params.get("sash")
    if sash:
        # the band sits over the outermost cloth at the waist: never the sleeves (in the A-pose a long
        # sleeve hangs at waist height, and the band would span the arms)
        rings = [p.varr() for k, p in out.items() if not k.startswith("Sleeve")]
        outer = np.concatenate(rings) if rings else lm.P("waist")[None, :]
        z_c = z_waist - 0.01 * S
        p = TC.sash(fields, outer, z_c, float(sash["width_m"]) * S, int(sash.get("turns", 2)), ATLAS["sash"],
                    ATLAS["sash_tails"])
        z_cut = z_c - (0.04 + float(sash.get("tails_m", 0.24))) * S
        knots = _cord_shape(p, sash, z_cut, S)
        p = _crop_tails(p, z_cut)
        if knots is not None:
            p.extend(knots)
        out["Sash"] = _mat(p, sash["mat"])
    if params.get("headwrap"):
        out.update(build_headwrap(fields, params["headwrap"]))
    if params.get("shawl"):  # M3-CHR-539 (optional)
        out["Shawl"] = build_shawl(fields, chart, params["shawl"])
    if params.get("wrist_cord"):  # M3-CHR-539 (optional)
        out["WristCord"] = build_wrist_cord(fields, params["wrist_cord"])
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


def coverage(body, params: dict, V: np.ndarray, reg: np.ndarray, keep_legs: bool = False) -> np.ndarray:
    """True for body vertices hidden under opaque clothing (with a margin), asha.md §8.1. `keep_legs` (M1-CHR-14,
    the `garment_fit` builds): the knees and shins stay under a skirt, so a stride or a reach that carries a leg out
    through the cloth shows a whole leg, not a hole."""
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
        margin = float(top.get("cover_margin_m", TOP_MARGIN))  # M3-CHR-03: deeper armholes want a wider margin
        fit = Fields(body) if top.get("armhole_cut") == "tank" else None
        under = torso & (H < top_line(lm, chart, th_deg, top, fit) - margin * S) & (V[:, 2] > hem + m)
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
        lo = hem + 0.045 * S
        if keep_legs:
            keep = float(sk.get("keep_above_knee_m", KEEP_ABOVE_KNEE))
            lo = max(lo, max(float(lm.side_pt("knee", sd)[2]) for sd in ("L", "R")) + keep * S)
        hidden |= legs & (V[:, 2] < z_waist - 0.02 * S - 0.5 * m) & (V[:, 2] > lo)
    wr = params.get("wraps")
    if wr:
        w0, w1 = (float(x) for x in wr["span"])
        for sd in ("L", "R"):
            an, kn = lm.side_pt("ankle", sd), lm.side_pt("knee", sd)
            ax = kn - an
            t = (V - an) @ ax / (ax @ ax)
            hidden |= (reg == f"leg_{sd}") & (t > w0 + 0.04) & (t < w1 - 0.03)
    return hidden
