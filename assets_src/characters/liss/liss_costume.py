"""Liss's costume as procedural cloth panels (no bpy), act1_npcs.md §2.2-§2.4 and §2.10.

Same method as Rhen's, Toma's and Ysolde's (rhen_costume, toma_costume, ysolde_costume): every garment is a pattern
grid whose rows are ray-cast onto the body field plus a fitting offset, and the grid is also the garment's island in
the 2K costume atlas (liss_textures paints the same charts). Pieces, inner to outer (§2.4):

1. The work top: light sailcloth, sleeveless, torso only. A wide neckline that drops 5 cm further on her right, so the
   right collarbone and the line-marks up the right side of the neck are bare; the armholes are dropped 12 cm below
   the shoulder joint (the M1-CHR-14 11.5 cm rule plus margin).
2. The copper-mesh work-sleeve and its five-finger glove are built in build_liss from the shipped arm and hand skin
   (an offset shell that takes the skin's own weights); here only the strap that holds it up, across the chest to
   the right armpit and round the back.
3. **The sailcloth coat:** sleeveless, open at the front, short at the front (the lower ribs) and long at the back,
   where it is **two tails**, not a tube (M1-CHR-14): each tail is an open panel behind one leg, from the waist to
   the back of the knee, that follows its own leg below the crotch (build_liss) plus three tail bones. The coat body
   rides the torso only and its armholes are dropped 12 cm too. Five patches are painted (liss_textures).
4. The tool harness: two leather straps crossed front and back (an X), six pouches rigid on them, a brass ring where
   the straps cross on the chest, a vial clipped to the left strap (a bound-light point) and the lamp cell glowing in
   the right chest pouch's slit.
5. Loose canvas trousers to mid-calf (a pelvis band and two leg tubes, an extra row at each knee: she kneels and
   squats).
6. Ankle boots with rope soles: a closed shell over each foot and a short shaft round the ankle, taking the feet's
   weights (build_liss).

Vertex colour = wind (R primary, G ripple, B phase, A flutter). `coverage()` says which body vertices are hidden
under clothing (deleted, asha.md §8.1); as on Asha and Ysolde after M1-CHR-14, the knees and shins under the coat's
tails and the trousers are kept. Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

import rhen_costume as RC
import ysolde_costume as YC
from asha_costume import TAG_CLOTH, Fields, TorsoChart, _panel, cast_last, dir_theta
from asha_mesh import Part, tube, uv_sphere

# costume atlas islands (u0, v0, u1, v1), the shader's UV convention (v down); liss_textures paints them
ATLAS = {
    "top": (0.0, 0.0, 0.40, 0.22),
    "coat": (0.40, 0.0, 1.0, 0.30),
    "tail_L": (0.0, 0.22, 0.20, 0.52),
    "tail_R": (0.20, 0.22, 0.40, 0.52),
    "trousers": (0.40, 0.30, 0.70, 0.40),
    "trouser_leg_L": (0.40, 0.40, 0.55, 0.64),
    "trouser_leg_R": (0.55, 0.40, 0.70, 0.64),
    "strap_a": (0.70, 0.30, 1.0, 0.35),
    "strap_b": (0.70, 0.35, 1.0, 0.40),
    "sleeve_strap": (0.70, 0.40, 1.0, 0.44),
    "pouch": (0.70, 0.44, 0.85, 0.56),
    "brass": (0.85, 0.44, 0.92, 0.50),
    "vial": (0.92, 0.44, 1.0, 0.50),
    "boots": (0.0, 0.52, 0.25, 0.66),
    "boot_shaft": (0.25, 0.52, 0.40, 0.64),
    "sole": (0.40, 0.64, 0.55, 0.68),
}
TOP_OFF = 0.0045  # m at S = 1, over the skin
COAT_OFF = 0.0135  # over the top and the work-sleeve's cap (build_liss lays the cap at 8.5 mm)
TAIL_OFF = 0.019  # the tails, over the trousers' seat
STRAP_OFF = 0.0185  # the harness over the coat
SLEEVE_STRAP_OFF = 0.0105  # the sleeve's strap: over the top, under the coat
TROUSER_OFF = 0.010  # loose canvas
TROUSER_FLARE = 0.010  # m more at the hem
BOOT_OFF = 0.0035
TAIL_ROWS = 16
TAIL_SPAN = (125.0, 178.0)  # degrees from the front: the left tail (the right one mirrors it); the right hip's
# launcher sits in front of -125 (liss_props)
TAIL_TOP_ABOVE_WAIST = 0.015  # m: the tails start under the coat body's back hem
COAT_BACK_HEM_BELOW_WAIST = 0.03
TOP_HEM_BELOW_WAIST = 0.025
KEEP_ABOVE_KNEE = 0.16  # m (at s = 1) of thigh kept above the knee joint under the trousers (M1-CHR-14)
POUCH_M = (0.075, 0.055, 0.030)  # a pouch: along the strap, across it, deep
BUCKLE_RING_M = 0.022  # the brass ring where the straps cross


def _wind_rows(n_rows: int, n_cols: int, amp: float, phase0: float = 0.0):
    return [[(amp * t * t, amp * t, (phase0 + i / n_cols * 3.0) % 1.0, 0.3 * amp * t) for i in range(n_cols)]
            for t in np.linspace(0.0, 1.0, n_rows)]


def _signed(th_deg: np.ndarray) -> np.ndarray:
    return ((np.asarray(th_deg, dtype=float) + 180.0) % 360.0) - 180.0


# ---------------------------------------------------------------------------------------------
# Torso lines (azimuth: 0 the front, + her left, - her right)
# ---------------------------------------------------------------------------------------------
def top_line(lm, chart: TorsoChart, th_deg: np.ndarray, drop: float, right_drop: float) -> np.ndarray:
    """The work top's top edge: a wide neckline, `right_drop` lower over her right collarbone (the line-marks run up
    it), and the armholes `drop` below the shoulder joint on both side lines. The left side holds the strap's height
    over the front and the back of the shoulder (the work-sleeve's cap lies over it)."""
    S = lm.S
    neck = chart.z_sh + math.radians(50) * chart.k
    front = float(lm.P("notch")[2] - 0.03 * S)
    arm = float(lm.P("shoulder")[2] - drop)  # m, not scaled: the 11.5 cm rule is a clearance
    strap = chart.z_sh + math.radians(22) * chart.k
    rd = right_drop * S
    xs = [-180, -150, -128, -112, -98, -88, -76, -64, -50, -30, -14, 0, 18, 34, 52, 66, 80, 92, 104, 118, 132, 150,
          180]
    vs = [neck, neck, neck - 0.02 * S, strap - 0.01 * S, arm + 0.04 * S, arm, arm + 0.04 * S, strap - 0.035 * S,
          front - rd * 0.6, front - rd, front - rd * 0.7, front, front + 0.01 * S, neck - 0.03 * S, strap, strap,
          arm + 0.05 * S, arm, arm + 0.05 * S, strap, neck - 0.02 * S, neck, neck]
    return np.interp(_signed(th_deg), xs, vs)


def coat_line(lm, chart: TorsoChart, th_deg: np.ndarray, drop: float, open_deg: float) -> np.ndarray:
    """The coat's top edge: the lapel drops toward the open front, a plain back neck, the armholes `drop` below the
    shoulder joint (deep: the coat is sleeveless)."""
    S = lm.S
    neck = chart.z_sh + math.radians(56) * chart.k
    lapel = float(lm.P("notch")[2] - 0.06 * S)
    arm = float(lm.P("shoulder")[2] - drop)  # m, not scaled: the 11.5 cm rule is a clearance
    strap = chart.z_sh + math.radians(28) * chart.k
    a = np.abs(_signed(th_deg))
    return np.interp(a, [0, open_deg, open_deg + 14, 50, 66, 80, 92, 104, 118, 134, 150, 180],
                     [lapel, lapel, lapel + 0.05 * S, strap, strap, arm + 0.05 * S, arm, arm + 0.05 * S, strap,
                      neck - 0.015 * S, neck, neck])


def coat_hem(lm, th_deg: np.ndarray, params: dict) -> np.ndarray:
    """Short at the front (the lower ribs), falling round the sides to just under the waist at the back, where the
    tails take over."""
    S = lm.S
    z_w = float(lm.P("waist")[2])
    front = z_w + float(params["coat_front_hem_above_waist_m"]) * S
    back = z_w - COAT_BACK_HEM_BELOW_WAIST * S
    a = np.abs(_signed(th_deg))
    return np.interp(a, [0, 40, 80, 110, 140, 180], [front, front - 0.005 * S, z_w + 0.03 * S, back + 0.01 * S, back,
                                                     back])


def skin_cut_top(lm, chart: TorsoChart, th_deg: np.ndarray, params: dict) -> np.ndarray:
    """Where the torso skin under the top is cut (coverage): the top's own line (the right collarbone stays)."""
    return top_line(lm, chart, th_deg, float(params["top_armhole_drop_m"]), float(params["top_right_neck_drop_m"]))


# ---------------------------------------------------------------------------------------------
# Small solids
# ---------------------------------------------------------------------------------------------
def box(part: Part, c: np.ndarray, ax: np.ndarray, ay: np.ndarray, az: np.ndarray, half, mat: str, rect,
        tags=TAG_CLOTH) -> None:
    """A box at c with unit axes (ax, ay, az) and half extents; each face takes the whole rect."""
    hx, hy, hz = half
    corners = {}
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                corners[(sx, sy, sz)] = c + ax * hx * sx + ay * hy * sy + az * hz * sz
    u0, v0, u1, v1 = rect
    uv = [(u0, v1), (u1, v1), (u1, v0), (u0, v0)]
    faces = [((1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1)), ((-1, 1, -1), (-1, -1, -1), (-1, -1, 1), (-1, 1, 1)),
             ((1, 1, -1), (-1, 1, -1), (-1, 1, 1), (1, 1, 1)), ((-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)),
             ((-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)), ((-1, 1, -1), (1, 1, -1), (1, -1, -1), (-1, -1, -1))]
    for f in faces:
        ids = [part.add_v(corners[k], tag=tags) for k in f]
        part.add_f(ids, uv, mat)


def _frame_on(C: np.ndarray, N: np.ndarray, i: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(along, across, out) at sample i of a strap's centre line."""
    t = C[(i + 1) % len(C)] - C[i - 1]
    n = N[i] / np.linalg.norm(N[i])
    t = t - (t @ n) * n
    t /= np.linalg.norm(t)
    return t, np.cross(n, t), n


# ---------------------------------------------------------------------------------------------
# Coat tails
# ---------------------------------------------------------------------------------------------
def tail(fields: Fields, name: str, rect, th_deg: np.ndarray, z_rows: np.ndarray, ring: tuple, seed: int) -> Part:
    """One open tail panel over the azimuths th_deg (in order) and the rows z_rows: ysolde_costume.panel's column
    (no dents between the legs), heavy sailcloth with one soft fold."""
    return YC.panel(fields, name, rect, th_deg, z_rows, ring, TAIL_OFF * fields.lm.S, seed, fold_amp=0.003)


# ---------------------------------------------------------------------------------------------
# Boots
# ---------------------------------------------------------------------------------------------
def boot(fields: Fields, side: str, params: dict) -> Part:
    """A closed shell over the foot (ysolde_costume.slipper, a touch thicker) and a shaft round the ankle up to
    `boot_height_m`; the rope sole is painted on the foot shell's lowest ring band (liss_textures)."""
    lm = fields.lm
    S = lm.S
    foot = YC.slipper(fields, side, ATLAS["boots"])
    foot.name = f"Boot{side}"
    an = lm.side_pt("ankle", side)
    kn = lm.side_pt("knee", side)
    top = float(params["boot_height_m"]) * S
    z0 = 0.035 * S
    path = np.array([an + (kn - an) * ((z - an[2]) / (kn[2] - an[2])) for z in np.linspace(z0, top, 6)])
    leg = fields.region(f"leg_{side}")
    ft = fields.region(f"foot_{side}")

    def fld(Q: np.ndarray) -> np.ndarray:
        return np.minimum(leg(Q), ft(Q))

    shaft = RC.limb_tube(fields, fld, path, lambda t: (BOOT_OFF + 0.0025 * (1.0 - t)) * S, ATLAS["boot_shaft"],
                         f"BootShaft{side}", n_around=18, rows=6, back_inset=0.002 * S)
    foot.extend(shaft)
    return foot


# ---------------------------------------------------------------------------------------------
def build_costume(body, params: dict) -> tuple[dict[str, Part], dict]:
    """Returns ({name: Part}, info): the opaque costume pieces and the tail and harness data build_liss needs."""
    lm = body.lm
    S = lm.S
    fields = Fields(body)
    chart = TorsoChart(lm)
    z_waist = float(lm.P("waist")[2])
    z_crotch = float(lm.P("crotch")[2])
    hip_z = float(lm.side_pt("hip", "L")[2])
    knee_z = float(lm.side_pt("knee", "L")[2])
    out: dict[str, Part] = {}
    seed = int(params["seed"])
    # 1. the work top: a closed ring
    th_t = np.linspace(0.0, 360.0, 56, endpoint=False)
    out["Top"] = RC.torso_sheet(fields, chart, "Top", ATLAS["top"], th_t,
                                skin_cut_top(lm, chart, th_t, params), z_waist - TOP_HEM_BELOW_WAIST * S,
                                TOP_OFF * S, 12, 0.0015 * S, True)
    # 3a. the coat body, open at the front
    od = float(params["coat_front_opening_deg"])
    th_c = np.linspace(od, 360.0 - od, 54)
    out["Coat"] = RC.torso_sheet(fields, chart, "Coat", ATLAS["coat"], th_c,
                                 coat_line(lm, chart, th_c, float(params["coat_armhole_drop_m"]), od),
                                 coat_hem(lm, th_c, params), COAT_OFF * S, 15, 0.0025 * S, False, wind_amp=0.12)
    # 3b. the two tails, to the back of the knee
    z_top = z_waist + TAIL_TOP_ABOVE_WAIST * S
    z_hem = knee_z + float(params["coat_tail_hem_above_knee_m"]) * S
    z_rows = YC.panel_rows(z_top, z_hem, TAIL_ROWS)
    ring = YC.ring_radii(fields, z_rows)
    gap = 0.5 * float(params["coat_tail_gap_deg"])
    a0, a1 = TAIL_SPAN
    out["TailL"] = tail(fields, "TailL", ATLAS["tail_L"], np.linspace(a0, a1 - gap, 14), z_rows, ring, seed)
    out["TailR"] = tail(fields, "TailR", ATLAS["tail_R"], np.linspace(360.0 - a1 + gap, 360.0 - a0, 14), z_rows, ring,
                        seed + 1)
    # 5. trousers: a pelvis band and two loose legs to mid-calf (an extra row at each knee)
    th_p = np.linspace(0.0, 360.0, 44, endpoint=False)
    pelvis = Part("TrouserTop")
    pelvis._mat = "cloth"
    rows = 8
    P = np.zeros((rows, len(th_p), 3))
    D = dir_theta(np.radians(th_p))
    for j in range(rows):
        z = z_waist + 0.01 * S + (z_crotch + 0.015 * S - z_waist - 0.01 * S) * j / (rows - 1)
        O = np.stack([np.zeros(len(th_p)), np.full(len(th_p), 0.01 * S), np.full(len(th_p), z)], axis=-1)
        r = cast_last(lambda Q: fields.lower(Q) - TROUSER_OFF * S, O, D, 0.5 * S)
        P[j] = O + D * r[:, None]
    _panel(pelvis, P, ATLAS["trousers"], None, True, 0.0018 * S, np.array([0.0, 0.01 * S, 0.0]))
    out["TrouserTop"] = pelvis
    an_z = float(lm.side_pt("ankle", "L")[2])
    hem_z = an_z + float(params["trouser_hem_above_ankle_m"]) * S
    for sd in ("L", "R"):
        kz = float(lm.side_pt("knee", sd)[2])
        # rows crowd a little round the knee (the extra loop of §2.4)
        zs = np.concatenate([np.linspace(z_crotch + 0.06 * S, kz + 0.06 * S, 7), np.linspace(kz + 0.04 * S,
                                                                                               kz - 0.04 * S, 5),
                             np.linspace(kz - 0.06 * S, hem_z, 5)])
        path = RC.leg_path(lm, sd, zs[0], zs[-1], 40)
        idx = np.clip(np.searchsorted(-path[:, 2], -zs), 0, len(path) - 1)
        path = path[idx]
        out[f"TrouserLeg{sd}"] = RC.limb_tube(fields, f"leg_{sd}", path,
                                              lambda t: (TROUSER_OFF + TROUSER_FLARE * t ** 1.6) * S,
                                              ATLAS[f"trouser_leg_{sd}"], f"TrouserLeg{sd}", n_around=22,
                                              rows=len(path), back_inset=0.0018 * S, wind_amp=0.06)
    # 6. boots
    for sd in ("L", "R"):
        out[f"Boot{sd}"] = boot(fields, sd, params)
    # 2. the work-sleeve's strap: from the left shoulder's cap across the chest to the right armpit, and back
    zs_ = chart.z_sh
    k = chart.k
    nip = float(lm.P("nipple")[2])
    arm_z = float(lm.P("shoulder")[2]) - 0.10 * S
    sstrap, _sc, _sn = RC.bandolier(fields, chart, 0.02 * S, ATLAS["sleeve_strap"],
                                    [(62.0, zs_ + math.radians(30) * k), (28.0, nip + 0.05 * S),
                                     (-40.0, nip + 0.02 * S), (-84.0, arm_z), (-120.0, arm_z + 0.01 * S),
                                     (-180.0, nip + 0.05 * S), (-240.0, zs_ + 0.02 * S),
                                     (-290.0, zs_ + math.radians(34) * k)], "SleeveStrap", SLEEVE_STRAP_OFF * S)
    out["SleeveStrap"] = sstrap
    # 4. the harness: two straps crossed front and back
    w = float(params["harness_strap_m"]) * S
    path_a = [(-56.0, zs_ + math.radians(44) * k), (-20.0, nip + 0.035 * S), (30.0, z_waist + 0.05 * S),
              (74.0, z_waist - 0.015 * S), (122.0, z_waist + 0.02 * S), (180.0, nip - 0.01 * S),
              (234.0, zs_ - 0.04 * S), (264.0, zs_ + math.radians(38) * k)]
    path_b = [(-a, h) for a, h in path_a]
    sa, Ca, Na = RC.bandolier(fields, chart, w, ATLAS["strap_a"], path_a, "StrapA", STRAP_OFF * S)
    sb, Cb, Nb = RC.bandolier(fields, chart, w, ATLAS["strap_b"], path_b, "StrapB", (STRAP_OFF + 0.002) * S)
    harness = Part("Harness")
    harness._mat = "cloth"
    harness.extend(sa)
    harness.extend(sb)
    # the brass ring where they cross on the chest (the front sample nearest the other strap)
    d = np.linalg.norm(Ca[:, None, :] - Cb[None, :, :], axis=2)
    front = (Ca[:, 1] < 0.0)[:, None] & (Cb[:, 1] < 0.0)[None, :]
    ia, ib = np.unravel_index(np.argmin(np.where(front, d, np.inf)), d.shape)
    xc = 0.5 * (Ca[ia] + Cb[ib])
    n_x = Na[ia] + Nb[ib]
    n_x /= np.linalg.norm(n_x)
    ring_c = xc + n_x * (0.004 * S + 0.25 * w)
    tt = np.linspace(0.0, 2 * math.pi, 25)
    e1 = np.cross(n_x, np.array([0.0, 0.0, 1.0]))
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(n_x, e1)
    ring_line = ring_c[None, :] + np.outer(np.cos(tt), e1) * BUCKLE_RING_M * S + np.outer(np.sin(tt), e2) * \
        BUCKLE_RING_M * S
    tube(harness, ring_line, 0.0032 * S, 8, "cloth", n_x, ATLAS["brass"], tags=TAG_CLOTH)
    # six pouches: (strap, share of its samples, rotation of the pouch about its out axis)
    pouch_at = [("a", 0.08, 0.0), ("b", 0.12, 0.0), ("a", 0.30, 0.0), ("b", 0.30, 0.0), ("a", 0.62, 0.0),
                ("b", 0.62, 0.0)][:int(params["harness_pouches"])]
    pouches = []
    for which, share, _rot in pouch_at:
        C, N = (Ca, Na) if which == "a" else (Cb, Nb)
        i = int(round(share * (len(C) - 1)))
        t_, s_, n_ = _frame_on(C, N, i)
        c = C[i] + n_ * (0.0025 * S + 0.5 * POUCH_M[2] * S)
        box(harness, c, t_, s_, n_, (0.5 * POUCH_M[0] * S, 0.5 * POUCH_M[1] * S, 0.5 * POUCH_M[2] * S), "cloth",
            ATLAS["pouch"])
        # the flap's brass stud
        uv_sphere(harness, c + n_ * 0.5 * POUCH_M[2] * S + t_ * 0.3 * POUCH_M[0] * S, 0.004 * S, 8, 4, "cloth",
                  axis_fwd=n_, uv_rect=ATLAS["brass"], tags=TAG_CLOTH)
        pouches.append({"centre": c, "along": t_, "across": s_, "out": n_, "strap": which})
    # the lamp cell: the right chest pouch (strap b's first, on her right breast) shows a 6 mm glimmer point through
    # a slit in its face; the vial: a 6 cm glass phial clipped to strap a under the left collarbone, its 5 mm point
    bl = params["bound_light_mm"]
    p0 = pouches[1]
    uv_sphere(harness, p0["centre"] + p0["out"] * (0.5 * POUCH_M[2] * S - 0.0012) - p0["along"] * 0.012 * S,
              0.0005 * float(bl["pouch"]), 8, 5, "glimmer", axis_fwd=p0["out"], tags=TAG_CLOTH)
    i = int(round(0.03 * (len(Ca) - 1)))
    t_, s_, n_ = _frame_on(Ca, Na, i)
    base = Ca[i] + n_ * 0.010 * S
    vial = np.array([base + s_ * 0.0 - np.array([0.0, 0.0, 1.0]) * 0.06 * S * f for f in np.linspace(0.0, 1.0, 6)])
    tube(harness, vial, 0.0065 * S, 10, "cloth", n_, ATLAS["vial"], tags=TAG_CLOTH, cap_end=True)
    uv_sphere(harness, vial[-2], 0.0005 * float(bl["vial"]), 8, 5, "glimmer", axis_fwd=n_, tags=TAG_CLOTH)
    out["Harness"] = harness
    for p in out.values():
        if not p.C:
            p.C = [(0.0, 0.0, 0.0, 0.0)] * len(p.V)
        elif len(p.C) < len(p.V):
            p.C = p.C + [(0.0, 0.0, 0.0, 0.0)] * (len(p.V) - len(p.C))
    info = {"z_rows": z_rows, "hip_z": hip_z, "knee_z": knee_z, "z_waist": z_waist, "z_hem": z_hem,
            "tail_span": TAIL_SPAN, "pouches": pouches}
    return out, info


def coverage(body, params: dict, V: np.ndarray, reg: np.ndarray) -> np.ndarray:
    """True for body vertices hidden under opaque clothing (with a margin), asha.md §8.1: the torso under the top
    (the right collarbone and neck stay), the thighs under the trousers down to KEEP_ABOVE_KNEE above the knee. The
    knees and shins under the tails and trousers, and the feet in the boots, are kept (M1-CHR-14). The left arm and
    hand under the work-sleeve are build_liss's (the shell's own faces)."""
    lm = body.lm
    S = lm.S
    chart = TorsoChart(lm)
    z_waist = float(lm.P("waist")[2])
    th, H = chart.H_of(V)
    th_deg = np.degrees(th)
    m = 0.025 * S
    torso = reg == "torso"
    top = torso & (H < skin_cut_top(lm, chart, th_deg, params) - m) & (V[:, 2] > z_waist - 0.06 * S)
    legs = (reg == "leg_L") | (reg == "leg_R") | torso
    z_keep = max(float(lm.side_pt("knee", sd)[2]) for sd in ("L", "R")) + KEEP_ABOVE_KNEE * S
    lower = legs & (V[:, 2] < z_waist - m) & (V[:, 2] > z_keep)
    return top | lower
