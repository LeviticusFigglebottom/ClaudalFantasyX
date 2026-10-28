"""Moll's costume as procedural cloth panels and lacquered shell plates (no bpy), hadric_moll.md §2 and §4.

Same method as Toma's and Liss's (toma_costume, rhen_costume, liss_costume): every garment is a pattern grid whose rows
are ray-cast onto the body field plus a fitting offset, and the grid is also the garment's island in the 2K costume
atlas (moll_textures paints the same charts). Pieces, inner to outer (§4):

1. The under-tunic (undyed cotton, `bone`): its long sleeves are offset shells of the shipped arm skin (build_moll,
   Liss's work-sleeve method: they take the skin's own weights), and its skirt shows below the cuirass to mid-thigh,
   two panels split at the sides (the right split wide: the iron's hand side).
2. The leather jack: a closed torso sheet from the neck to under the waist, its armholes Toma's tunic line (11.5 cm
   below the shoulder joint, M1-CHR-14), riding the torso only.
3. **The cuirass:** four rows of overlapping shell lames, front and back (eight closed plates, toma_costume's plate
   builder), each row a little further out than the one below it so they shingle down the chest: the profile steps.
   Red lacquer, deep at the edges, gold piping on the top row's rim (moll_textures).
4. **The pauldrons:** Toma's five-lame pauldron (toma_costume.pauldron) on each shoulder, **uncut**: the top lame
   carries the Level (a ring crossed by a bar) whole and raised, `emblem_relief`, in place of Toma's chisel scar; the
   right one is the left mirrored.
5. The Inquisitor's sash: white linen, 14 cm, from the right shoulder across the chest to the left hip and back up
   across the back (rhen_costume.bandolier on the costume's outer surface), knotted at the left hip with two tails to
   mid-thigh (toma_costume.sash_tail).
6. Trousers (indigo at 80% value) and shin wraps; 7. Toma's reinforced sandals; 8. leather bracers with a bronze
   edge on both forearms (build_moll pushes them out over the sleeves).

Vertex colour = wind (R primary, G ripple, B phase, A flutter). `coverage()` says which body vertices are hidden under
clothing (deleted, asha.md §8.1): the torso under the jack, the thighs under the trousers down to KEEP_ABOVE_KNEE
above the knee (the knees are kept, M1-CHR-14), the shins under the wraps. Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

import rhen_costume as RC
import toma_costume as TC
from asha_costume import TAG_CLOTH, Fields, TorsoChart, _panel, cast_last, dir_theta, limb_wrap
from asha_mesh import Part, uv_sphere

# costume atlas islands (u0, v0, u1, v1), the shader's UV convention (v down); moll_textures paints them. The five
# pauldron islands are at toma_costume.ATLAS's rects, since toma_costume.pauldron lays its UVs there.
ATLAS = {
    "jack": (0.0, 0.0, 0.5, 0.14),
    "cuirass": (0.0, 0.14, 0.5, 0.40),  # four rows, a quarter of the island's height each
    "lame_edge": TC.ATLAS["lame_edge"],
    "lame_back": TC.ATLAS["lame_back"],
    "top_edge": TC.ATLAS["top_edge"],
    "sash": (0.5, 0.0, 1.0, 0.10),
    "sash_tails": (0.5, 0.10, 0.75, 0.30),
    "knot": (0.75, 0.10, 0.85, 0.16),
    "tunic_skirt": (0.0, 0.40, 0.5, 0.52),
    "sleeves": (0.0, 0.52, 0.5, 0.76),
    "pauldron_top": TC.ATLAS["pauldron_top"],
    "pauldron_lames": TC.ATLAS["pauldron_lames"],
    "trousers": (0.5, 0.78, 0.75, 0.86),
    "trouser_leg_L": (0.0, 0.76, 0.25, 0.94),
    "trouser_leg_R": (0.25, 0.76, 0.5, 0.94),
    "wraps": (0.5, 0.30, 0.75, 0.48),
    "sandals": (0.75, 0.30, 1.0, 0.42),
    "bracers": (0.75, 0.78, 1.0, 0.94),
    "bronze": (0.85, 0.10, 0.95, 0.16),
}
CUIRASS_ROWS_V = 4  # the cuirass island holds one band of v per row
JACK_OFF = 0.009  # m at S = 1: the jack over the skin (and the sleeves' caps, build_moll lays them at 5 mm)
LAME_OFF = 0.018  # the bottom row's plates over the jack
LAME_STEP = 0.004  # each row up sits this much further out (the shingle)
LAME_FLARE = 0.003  # a plate's lower edge flares out this much
SASH_OFF = 0.007  # the sash over what it lies on
SASH_OVER_SHOULDER = (38.0, 34.0)  # degrees of TorsoChart elevation where it crosses the right shoulder, front and
# back: out on the shoulder, clear of the neck
SKIRT_OFF = 0.014  # the tunic's skirt over the trousers
TROUSER_OFF = 0.009
SHIN_WRAP_OFF = 0.0125
SKIRT_FRONT = (-62.0, 74.0)  # degrees: the skirt's front panel (the right split, -62 .. -112, is the iron's side)
SKIRT_BACK = (106.0, 248.0)
CUIRASS_FRONT = (-84.0, 84.0)  # the lames' front and back plates, the jack showing between them under the arms
CUIRASS_BACK = (96.0, 264.0)
CUIRASS_COLS = 22
CUIRASS_PLATE_ROWS = 5
JACK_COLS, JACK_ROWS = 40, 9  # mostly under the lames: the neckline, the armholes and the hem show
SKIRT_COLS, SKIRT_ROWS = 24, 8
KEEP_ABOVE_KNEE = 0.16  # m (at s = 1) of thigh kept above the knee joint under the trousers (M1-CHR-14)
SASH_KNOT_AZ = 88.0  # degrees: the knot at the left hip
SASH_KNOT_DROP = 0.045  # m below the waist
SASH_LAME_BLEND = 0.03  # m: the sash's bed blends from the lames' surface to the jack's over this height


def _signed(th_deg: np.ndarray) -> np.ndarray:
    return ((np.asarray(th_deg, dtype=float) + 180.0) % 360.0) - 180.0


# ---------------------------------------------------------------------------------------------
# The cuirass
# ---------------------------------------------------------------------------------------------
def cuirass_top(lm, th_deg: np.ndarray, params: dict) -> np.ndarray:
    """The top row's upper edge: high over the chest and the shoulder blades, down under the arms to the armhole
    line (cuirass_side_below_shoulder_m, past M1-CHR-14's 11.5 cm)."""
    S = lm.S
    nip = float(lm.P("nipple")[2])
    side = float(lm.P("shoulder")[2]) - float(params["cuirass_side_below_shoulder_m"])  # a clearance: not scaled
    front = nip + float(params["cuirass_top_above_nipple_m"]) * S
    back = front + 0.02 * S
    return RC._sym_interp(th_deg, [0, 40, 64, 80, 90, 100, 116, 140, 180],
                          [front, front - 0.005 * S, front - 0.04 * S, side + 0.01 * S, side, side + 0.01 * S,
                           back - 0.04 * S, back - 0.005 * S, back])


def cuirass_rows(lm, th_deg: np.ndarray, params: dict) -> list[tuple[np.ndarray, np.ndarray]]:
    """(top, bottom) heights of each row, the top row first; neighbours overlap by `lame_overlap` of a row."""
    S = lm.S
    top = cuirass_top(lm, th_deg, params)
    bot = np.full_like(top, float(lm.P("waist")[2]) - float(params["cuirass_bottom_below_waist_m"]) * S)
    n = int(params["cuirass_rows"])
    ov = float(params["lame_overlap"])
    h = (top - bot) / (n - (n - 1) * ov)
    out = []
    for k in range(n):
        t = top - k * h * (1.0 - ov)
        out.append((t, t - h))
    return out


def row_offset(k: int, n: int) -> float:
    """m at S = 1: the offset of row k (0 the top) over the body field; the top row is the outermost."""
    return LAME_OFF + (n - 1 - k) * LAME_STEP


def lame_plate(fields: Fields, chart: TorsoChart, part: Part, th_deg: np.ndarray, top: np.ndarray, bot: np.ndarray,
               off: float, thick: float, rect) -> None:
    """One closed plate over the azimuths th_deg between the heights top and bot: cast on the torso field at `off`,
    its lower edge flared out by LAME_FLARE (toma_costume._plate: the front, the back `thick` inward, the edges)."""
    S = fields.lm.S
    th = np.radians(th_deg)
    nj = CUIRASS_PLATE_ROWS
    P = np.zeros((nj, len(th), 3))
    for j in range(nj):
        t = j / (nj - 1)
        H = top + (bot - top) * t
        O, D = chart.rays(th, H)
        o = off + LAME_FLARE * S * t * t
        r = cast_last(lambda Q, o=o: fields.upper(Q) - o, O, D, 0.4 * S)
        P[j] = O + D * r[:, None]
    N = TC._grid_normals(P, np.array([0.0, chart.y_axis, float(P[..., 2].mean())]))
    N[..., 2] *= 0.3  # the plate's thickness runs into the body, not down the torso
    N /= np.linalg.norm(N, axis=-1, keepdims=True)
    TC._plate(part, P + N * thick, N, thick, rect, ATLAS["lame_back"], ATLAS["lame_edge"])


def cuirass(fields: Fields, chart: TorsoChart, params: dict) -> Part:
    lm = fields.lm
    S = lm.S
    part = Part("Cuirass")
    thick = float(params["lame_thickness_m"])
    n = int(params["cuirass_rows"])
    u0, v0, u1, v1 = ATLAS["cuirass"]
    hv = (v1 - v0) / CUIRASS_ROWS_V
    for half, (a0, a1) in enumerate((CUIRASS_FRONT, CUIRASS_BACK)):
        th_deg = np.linspace(a0, a1, CUIRASS_COLS)
        for k, (top, bot) in enumerate(cuirass_rows(lm, th_deg, params)):
            uh = 0.5 * (u1 - u0)
            rect = (u0 + uh * half, v0 + hv * k, u0 + uh * (half + 1), v0 + hv * (k + 1))
            lame_plate(fields, chart, part, th_deg, top, bot, row_offset(k, n) * S, thick, rect)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part


def cuirass_outer_off(lm, chart: TorsoChart, P: np.ndarray, params: dict) -> np.ndarray:
    """m: the outermost costume layer's offset over the body field at points P (the top lame's outer face over the
    cuirass's span, the jack above it), for the sash to lie on."""
    S = lm.S
    th, H = chart.H_of(P)
    th_deg = np.degrees(th)
    n = int(params["cuirass_rows"])
    top = cuirass_top(lm, th_deg, params)
    bot = float(lm.P("waist")[2]) - float(params["cuirass_bottom_below_waist_m"]) * S
    lames = (row_offset(0, n) + LAME_FLARE) * S + float(params["lame_thickness_m"])
    jack = JACK_OFF * S
    inside = np.clip((top - H) / (SASH_LAME_BLEND * S) + 0.5, 0.0, 1.0) * \
        np.clip((H - bot) / (SASH_LAME_BLEND * S) + 0.5, 0.0, 1.0)
    w = inside * inside * (3.0 - 2.0 * inside)
    return jack + (lames - jack) * w


class _OnCostume:
    """A Fields stand-in for rhen_costume.bandolier: its `upper` field is the costume's outer surface (the body field
    less the outer layer's offset), so a band cast on it with a small offset lies on the lames and the jack."""

    def __init__(self, fields: Fields, chart: TorsoChart, params: dict) -> None:
        self.lm = fields.lm
        self._f, self._c, self._p = fields, chart, params

    def upper(self, Q: np.ndarray) -> np.ndarray:
        return self._f.upper(Q) - cuirass_outer_off(self.lm, self._c, Q, self._p)


# ---------------------------------------------------------------------------------------------
# The pauldrons: Toma's, uncut, the Level whole
# ---------------------------------------------------------------------------------------------
def emblem_mask(params: dict, x: np.ndarray, y: np.ndarray, soft: float = 0.0012) -> np.ndarray:
    """0..1 coverage of the Level on the top lame's chart (x front-back, y medial-lateral, metres from the centre that
    toma_costume puts the scar at): a ring of `emblem_radius_m` (to the stroke's middle), crossed by a bar along x
    (level when he stands) that runs `emblem_bar_past_m` past the ring each side; strokes `emblem_stroke_m` wide."""
    R = float(params["emblem_radius_m"])
    w = 0.5 * float(params["emblem_stroke_m"])
    past = float(params["emblem_bar_past_m"])
    x, y = np.asarray(x, float), np.asarray(y, float)
    ring = np.abs(np.hypot(x, y) - R)
    bar = np.maximum(np.abs(y), np.maximum(np.abs(x) - (R + w + past), 0.0))
    d = np.minimum(ring, bar)
    t = np.clip((w + soft - d) / (2.0 * soft), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def emblem_relief(params: dict, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """toma_costume.pauldron's `relief`: the Level stands out of the top lame (negative depth)."""
    return -float(params["emblem_relief_m"]) * emblem_mask(params, x, y)


PAULDRON_TOP_GRID = (28, 22)  # columns x rows of the top lame: the emblem reads at 1.25 cm a quad
PAULDRON_LAME_GRID = (16, 5)


def mirror_part(part: Part, name: str) -> Part:
    """The part mirrored across x = 0 (the right side from the left), faces rewound to keep them outward."""
    out = Part(name)
    out.V = [np.array([-p[0], p[1], p[2]]) for p in part.V]
    out.C = list(part.C)
    out.T = list(part.T)
    out.F = [tuple(reversed(f)) for f in part.F]
    out.UV = [tuple(reversed(uv)) for uv in part.UV]
    out.M = list(part.M)
    return out


def pauldrons(fields: Fields, params: dict) -> tuple[Part, Part, dict]:
    left, info = TC.pauldron(fields, params, relief=emblem_relief, top_grid=PAULDRON_TOP_GRID,
                             lame_grid=PAULDRON_LAME_GRID)
    left.name = "PauldronL"
    right = mirror_part(left, "PauldronR")
    a, b = info["hinge"]
    m = np.array([-1.0, 1.0, 1.0])
    info["hinge_R"] = (a * m, b * m)
    info["centre_R"] = info["centre"] * m
    return left, right, info


# ---------------------------------------------------------------------------------------------
# Sash
# ---------------------------------------------------------------------------------------------
def sash(fields: Fields, chart: TorsoChart, params: dict, outer: np.ndarray) -> Part:
    """The white sash from the right shoulder to the left hip and back up across the back, the knot at the left hip
    and its two tails to mid-thigh."""
    lm = fields.lm
    S = lm.S
    zs, k = chart.z_sh, chart.k
    nip = float(lm.P("nipple")[2])
    z_w = float(lm.P("waist")[2])
    z_knot = z_w - SASH_KNOT_DROP * S
    path = [(-58.0, zs + math.radians(SASH_OVER_SHOULDER[0]) * k), (-22.0, nip + 0.06 * S), (24.0, z_w + 0.07 * S),
            (62.0, z_knot + 0.01 * S), (SASH_KNOT_AZ, z_knot), (122.0, z_knot + 0.02 * S),
            (176.0, z_w + 0.11 * S), (214.0, nip + 0.04 * S), (244.0, zs - 0.02 * S),
            (268.0, zs + math.radians(SASH_OVER_SHOULDER[1]) * k)]
    width = float(params["sash_width_m"]) * S
    band, _C, _N = RC.bandolier(_OnCostume(fields, chart, params), chart, width, ATLAS["sash"], path, "Sash",
                                SASH_OFF * S)
    part = Part("Sash")
    part._mat = "cloth"
    part.extend(band)
    # the knot at the left hip, and two tails to mid-thigh (toma_costume's, on the costume's outer points)
    th_k = math.radians(SASH_KNOT_AZ)
    dk = np.array([math.sin(th_k), -math.cos(th_k), 0.0])
    r_k = float(TC._outer_radius(np.concatenate([outer, band.varr()]), z_knot, np.array([th_k]), S)[0])
    knot_c = np.array([0.0, 0.01 * S, z_knot]) + dk * (r_k + 0.016 * S)
    kn = Part("SashKnot")
    uv_sphere(kn, knot_c, np.array([0.036, 0.026, 0.032]) * S, 12, 7, "cloth", axis_fwd=dk, uv_rect=ATLAS["knot"],
              tags=TAG_CLOTH)
    kn.C = [(0.0, 0.0, 0.0, 0.0)] * len(kn.V)
    part.extend(kn)
    z1 = float(lm.P("crotch")[2]) - float(params["sash_tail_below_crotch_m"]) * S
    tails = Part("SashTails")
    tails._mat = "cloth"
    allp = np.concatenate([outer, band.varr(), kn.varr()])
    tu0, tv0, tu1, tv1 = ATLAS["sash_tails"]
    for i, (dth, drop) in enumerate(((-9.0, 0.0), (7.0, 0.04))):
        Q = TC.sash_tail(allp, knot_c, i, math.radians(SASH_KNOT_AZ + dth), knot_c[2] - 0.02 * S, z1 + drop * S, S)
        rows_t, cols_t = Q.shape[:2]
        cols = [[(t, t, 0.37 * i + 0.2, 0.25 * t)] * cols_t for t in np.linspace(0, 1, rows_t)]
        ua, ub = tu0 + (tu1 - tu0) * 0.5 * i, tu0 + (tu1 - tu0) * 0.5 * (i + 1)
        TC._shell(tails, Q, lambda j, c, ua=ua, ub=ub: (ua + (ub - ua) * c / (cols_t - 1),
                                                        tv0 + (tv1 - tv0) * j / (rows_t - 1)),
                  False, np.array([0.0, 0.01 * S, float(Q[:, :, 2].mean())]), 0.0012 * S, cols)
    part.tail_first = len(part.V)
    part.extend(tails)
    if len(part.C) < len(part.V):
        part.C = part.C + [(0.0, 0.0, 0.0, 0.0)] * (len(part.V) - len(part.C))
    return part


# ---------------------------------------------------------------------------------------------
def jack_top(lm, chart: TorsoChart, th_deg: np.ndarray) -> np.ndarray:
    """The jack's neckline and armholes: Toma's tunic line (a shallow V, armholes 11.5 cm below the shoulder)."""
    return TC.tunic_top(lm, chart, th_deg)


def build_costume(body, params: dict) -> tuple[dict[str, Part], dict]:
    """Returns ({name: Part}, info): the costume pieces and the anchors build_moll needs."""
    lm = body.lm
    S = lm.S
    fields = Fields(body)
    chart = TorsoChart(lm)
    z_waist = float(lm.P("waist")[2])
    z_crotch = float(lm.P("crotch")[2])
    out: dict[str, Part] = {}
    seed = int(params["seed"])
    # 2. the jack: a closed sheet, the torso only
    th_j = np.linspace(0.0, 360.0, JACK_COLS, endpoint=False)
    out["Jack"] = RC.torso_sheet(fields, chart, "Jack", ATLAS["jack"], th_j, jack_top(lm, chart, th_j),
                                 z_waist - float(params["jack_bottom_below_waist_m"]) * S, JACK_OFF * S, JACK_ROWS,
                                 0.0015 * S, True)
    # 3. the cuirass
    out["Cuirass"] = cuirass(fields, chart, params)
    # 1. the tunic's skirt: two panels to mid-thigh, split at the sides
    z_top = z_waist - 0.01 * S
    z_hem = z_crotch - float(params["tunic_hem_below_crotch_m"]) * S
    skirt = Part("TunicSkirt")
    skirt._mat = "cloth"
    u0, v0, u1, v1 = ATLAS["tunic_skirt"]
    for i, (a0, a1) in enumerate((SKIRT_FRONT, SKIRT_BACK)):
        uh = 0.5 * (u1 - u0)
        p = TC.skirt_open(fields, f"TunicSkirt{i}", (u0 + uh * i, v0, u0 + uh * (i + 1), v1), z_top, z_hem,
                          np.linspace(a0, a1, SKIRT_COLS), SKIRT_OFF * S, SKIRT_ROWS, 0.16, 5, 0.004, seed + i)
        skirt.extend(p)
    out["TunicSkirt"] = skirt
    # 6. trousers: a pelvis band and two legs to mid-shin, gathered into the wraps (Toma's cut)
    an_z = float(lm.side_pt("ankle", "L")[2])
    kn_z = float(lm.side_pt("knee", "L")[2])
    hem_z = an_z + (kn_z - an_z) * float(params["trouser_hem_shin"])
    th_t = np.linspace(0.0, 360.0, 40, endpoint=False)
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
    out["TrouserTop"] = pelvis
    for sd in ("L", "R"):
        path = RC.leg_path(lm, sd, z_crotch + 0.06 * S, hem_z, 13)
        out[f"TrouserLeg{sd}"] = RC.limb_tube(
            fields, f"leg_{sd}", path, lambda t: (0.0075 + 0.012 * math.sin(math.pi * min(t * 1.15, 1.0)) ** 1.2
                                                  + 0.002) * S,
            ATLAS[f"trouser_leg_{sd}"], f"TrouserLeg{sd}", n_around=20, rows=13, back_inset=0.0018 * S,
            wind_amp=0.05)
    w0, w1 = (float(x) for x in params["wrap_span"])
    wraps = Part("Wraps")
    for sd in ("L", "R"):
        an, kn = lm.side_pt("ankle", sd), lm.side_pt("knee", sd)
        wraps.extend(limb_wrap(fields, f"leg_{sd}", an + (kn - an) * w0, an + (kn - an) * w1, SHIN_WRAP_OFF * S,
                               ATLAS["wraps"], f"Wrap{sd}", n_around=18, rows=8))
    out["Wraps"] = wraps
    sandals = Part("Sandals")
    for sd in ("L", "R"):
        sandals.extend(TC.reinforced_sandal(fields, sd, ATLAS["sandals"]))
    out["Sandals"] = sandals
    # 4. the pauldrons
    out["PauldronL"], out["PauldronR"], pinfo = pauldrons(fields, params)
    # 5. the sash, on everything under it
    for p in out.values():
        if not p.C:
            p.C = [(0.0, 0.0, 0.0, 0.0)] * len(p.V)
        elif len(p.C) < len(p.V):
            p.C = p.C + [(0.0, 0.0, 0.0, 0.0)] * (len(p.V) - len(p.C))
    outer = np.concatenate([out[n].varr() for n in ("Jack", "Cuirass", "TunicSkirt", "TrouserTop")])
    if params.get("sash", True):  # M3-CHR-508: the Stillguard soldiers wear no Inquisitor's sash
        out["Sash"] = sash(fields, chart, params, outer)
    info = {"pauldron": pinfo, "z_hem": z_hem, "z_waist": z_waist, "z_crotch": z_crotch}
    return out, info


def coverage(body, params: dict, V: np.ndarray, reg: np.ndarray) -> np.ndarray:
    """True for body vertices hidden under opaque clothing (with a margin), asha.md §8.1: the torso under the jack,
    the thighs under the trousers down to KEEP_ABOVE_KNEE above the knee (M1-CHR-14), the shins under the wraps. The
    arms under the sleeves are build_moll's (the shells' own faces)."""
    lm = body.lm
    S = lm.S
    chart = TorsoChart(lm)
    z_waist = float(lm.P("waist")[2])
    th, H = chart.H_of(V)
    th_deg = np.degrees(th)
    m = 0.025 * S
    torso = reg == "torso"
    jack = torso & (H < jack_top(lm, chart, th_deg) - m) & (V[:, 2] > z_waist - 0.06 * S)
    legs = (reg == "leg_L") | (reg == "leg_R") | torso
    z_keep = max(float(lm.side_pt("knee", sd)[2]) for sd in ("L", "R")) + KEEP_ABOVE_KNEE * S
    lower = legs & (V[:, 2] < z_waist - m) & (V[:, 2] > z_keep)
    shins = np.zeros(len(V), dtype=bool)
    w0, w1 = (float(x) for x in params["wrap_span"])
    for sd in ("L", "R"):
        an, kn = lm.side_pt("ankle", sd), lm.side_pt("knee", sd)
        ax = kn - an
        t = (V - an) @ ax / (ax @ ax)
        shins |= (reg == f"leg_{sd}") & (t > w0 + 0.04) & (t < w1 - 0.02)
    return jack | lower | shins

