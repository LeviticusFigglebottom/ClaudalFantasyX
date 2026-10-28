"""Kerrid's costume as procedural cloth panels (no bpy), kerrid.md §3-§4 and §9.

Same method as Asha's, Rhen's, Toma's and Ysolde's (asha_costume, rhen_costume, toma_costume, ysolde_costume): every
garment is a pattern grid whose rows are ray-cast onto the body field plus a fitting offset, and the grid is also the
garment's island in the 2K costume atlas (kerrid_textures paints the same charts). Pieces, inner to outer (kerrid.md
§4.1); the cape's tiers are kerrid_cape, the anchor-cleaver kerrid_props:

1. **The smock**, heavy hemp, hip length, a round neck. Its body rides the torso only, with Ysolde's dropped armhole
   (`ysolde_costume.robe_top`: 12 cm below the shoulder joint on the side line), and below the waist it is a straight
   column handed over to the legs toward the hem (build_kerrid). **Dropped-shoulder sleeves** (Ysolde's layer 5)
   reach in over the shoulder top, take the arm's weights with a 4 cm gusset blend, and end 3 cm above the elbow
   crease in a rolled cuff, so both forearms show and a 110 degree elbow never folds cloth into the forearm.
2. Wading trousers, loose, tarred canvas: a pelvis band and two leg tubes (Rhen's `limb_tube`) to a hem 9 cm above the
   ankle bone.
3. **Rope sandals**: Asha's sole-and-straps sandal on a plaited rope sole, plus two ankle ties; they take the feet's
   weights (build_kerrid).
4. **The left forearm wrap**: tarred hauling-cloth from under the elbow to the knuckles, 2.5 mm off the skin (its own
   mesh, `Wrap`); the turns are painted (kerrid_textures).
5. The belt: 5 cm of old leather with an iron ring buckle at the front, torso only.
8. **The chest rope**: two horizontal turns at 10 and 16 cm below the collarbones, across the yoke's open front and
   round the body, knotted at the left of the sternum; under the arms it lies on the ribcage 14 cm below the shoulder
   joint, 6 mm off the smock (over the cape at the back: build_kerrid passes the cape's mats as `outer`).
9. **The watch cord** at the right hip: 6 mm faded watch-red, three knots 8 cm apart, 34 cm to mid-thigh; a 1 x 3
   bone pendulum (build_kerrid).

Vertex colour = wind (R primary, G ripple, B phase, A flutter). `coverage()` says which body vertices are hidden
under clothing (deleted, asha.md §8.1): the knees and shins stay under the trousers (M1-CHR-14), and the forearm
under the wrap is cut well inside its ends. Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

import rhen_costume as RC
import toma_costume as TC
import ysolde_costume as YC
from asha_costume import TAG_CLOTH, Fields, TorsoChart, _panel, cast_last, dir_theta, limb_wrap, sandal
from asha_mesh import Part, catmull_rom, tube, uv_sphere

# costume atlas islands (u0, v0, u1, v1), the shader's UV convention (v down); kerrid_textures paints them
ATLAS = {
    "smock": (0.0, 0.0, 0.55, 0.22),
    "smock_skirt": (0.0, 0.22, 0.55, 0.30),
    "sleeve_L": (0.0, 0.30, 0.20, 0.42),
    "sleeve_R": (0.20, 0.30, 0.40, 0.42),
    "cuff_L": (0.40, 0.30, 0.55, 0.36),
    "cuff_R": (0.40, 0.36, 0.55, 0.42),
    "trousers": (0.55, 0.0, 0.80, 0.10),
    "trouser_leg_L": (0.55, 0.10, 0.675, 0.40),
    "trouser_leg_R": (0.675, 0.10, 0.80, 0.40),
    "wrap": (0.80, 0.0, 1.0, 0.25),
    "sandals": (0.80, 0.25, 1.0, 0.40),
    "belt": (0.0, 0.42, 0.40, 0.46),
    "buckle": (0.40, 0.42, 0.45, 0.46),
    "rope": (0.0, 0.46, 0.50, 0.50),
    "cord": (0.50, 0.46, 0.75, 0.50),
    "knot": (0.75, 0.46, 0.80, 0.50),
    "cape_mat": (0.0, 0.50, 0.60, 1.0),
}
SMOCK_OFF = 0.0060  # m at S = 1, heavy hemp over the skin
SMOCK_SKIRT_OFF = 0.010  # over the trousers' pelvis band below the waist
SLEEVE_OFF = (0.014, 0.017)  # at the shoulder and at the cuff
SLEEVE_TOP_T = YC.SLEEVE_TOP_T  # in over the shoulder's top to meet the smock's strap
SLEEVE_MIN_R = 0.055  # m (at s = 1): the dropped shoulder's ease on a heavy man
SLEEVE_ARM_FROM = 0.18  # arm skin is cut under the sleeve from here (the armpit's skin stays)
CUFF_OFF = 0.026  # the rolled cuff over the sleeve's end
TROUSER_OFF = 0.009
SANDAL_TIE_OFF = 0.0035
WRAP_HAND = (0.16, 0.34, 0.52)  # shares of the hand's length the wrap runs over the back of the hand to the knuckles
WRAP_FROM_T = 0.53  # along the arm (0.5 = the elbow): the half-hitch under the elbow
WRAP_CUT_IN = 0.07  # the forearm skin is cut under the wrap from this far past its top edge (the edge stays covered)
BELT_OFF = 0.005
ROPE_DIP_FROM = 0.5  # |sin| of the azimuth (0 front, 1 the side) where a turn starts to dip under the arm
ROPE_DIP_FULL = 0.8  # and where it reaches the underarm line (kerrid.md §4.1 #8: 14 cm below the shoulder joint)
ROPE_OFF_SKIN = 0.008  # under the arms, the rope's surface over the smock (kerrid.md: 6 mm) plus a margin
CORD_ROWS = 16
SMOCK_ROWS = 12
SKIRT_ROWS = 6


def _wind_rows(n_rows: int, n_cols: int, amp: float, phase0: float = 0.0):
    return [[(amp * t * t, amp * t, (phase0 + i / n_cols * 3.0) % 1.0, 0.3 * amp * t) for i in range(n_cols)]
            for t in np.linspace(0.0, 1.0, n_rows)]


def smock_neck(lm, chart: TorsoChart, th_deg: np.ndarray, drop: float) -> np.ndarray:
    """The smock's top: Ysolde's dropped-armhole bodice line with a plain round neck a little lower at the front."""
    S = lm.S
    top = YC.robe_top(lm, chart, th_deg, drop)
    a = np.abs(((np.asarray(th_deg) + 180.0) % 360.0) - 180.0)
    return top - 0.010 * S * np.clip(1.0 - a / 30.0, 0.0, 1.0)


def hem_z(lm, params: dict) -> float:
    return float(lm.side_pt("hip", "L")[2]) - float(params["smock_hem_below_hip_m"]) * lm.S


def smock_skirt(fields: Fields, z_top: float, z_hem: float, outer_min: np.ndarray | None) -> tuple[Part, np.ndarray]:
    """The smock below the waist: a straight closed column (each row at least as wide as the one above, Ysolde's
    ring_radii) over the trousers' pelvis band, to the hip-length hem."""
    lm = fields.lm
    S = lm.S
    rows = SKIRT_ROWS
    z_rows = np.linspace(z_top, z_hem, rows)
    th_ring, R = YC.ring_radii(fields, z_rows)
    th = np.linspace(0.0, 360.0, 36, endpoint=False)
    P = np.zeros((rows, len(th), 3))
    D = dir_theta(np.radians(th))
    for j, z in enumerate(z_rows):
        r = np.interp(th, th_ring, R[j], period=360.0) + SMOCK_SKIRT_OFF * S
        if outer_min is not None:
            r = np.maximum(r, TC._outer_radius(outer_min, z, np.radians(th), S, 0.02) + 0.003 * S)
        O = np.stack([np.zeros(len(th)), np.full(len(th), 0.01 * S), np.full(len(th), z)], axis=-1)
        P[j] = O + D * r[:, None]
    part = Part("SmockSkirt")
    part._mat = "cloth"
    _panel(part, P, ATLAS["smock_skirt"], _wind_rows(rows, len(th), 0.04), True, 0.0018 * S,
           np.array([0.0, 0.01 * S, 0.0]))
    part.grid_P = P
    return part, z_rows


def belt(fields: Fields, z_c: float, width: float, outer: np.ndarray) -> Part:
    """5 cm of old leather over the smock at the waist, an iron ring buckle at the front (kerrid.md §4.1 #5)."""
    lm = fields.lm
    S = lm.S
    part = Part("Belt")
    part._mat = "cloth"
    n = 48
    th = np.radians(np.linspace(0.0, 360.0, n, endpoint=False))
    D = dir_theta(th)
    rows = 3
    P = np.zeros((rows, n, 3))
    for j in range(rows):
        z = z_c + width * (0.5 - j / (rows - 1))
        r = TC._outer_radius(outer, z, th, S, 0.03) + BELT_OFF * S
        O = np.stack([np.zeros(n), np.full(n, 0.01 * S), np.full(n, z)], axis=-1)
        P[j] = O + D * r[:, None]
    _panel(part, P, ATLAS["belt"], None, True, 0.003 * S, np.array([0.0, 0.01 * S, 0.0]))
    # the iron ring buckle at the front: a torus 5.5 cm across, facing forward
    c = P[1, 0] + np.array([0.0, -0.007 * S, 0.0])
    R0, r0 = 0.0245 * S, 0.0042 * S
    t = np.linspace(0.0, 2 * math.pi, 25)
    C = c[None, :] + np.stack([R0 * np.cos(t), np.zeros_like(t), R0 * np.sin(t)], axis=1)
    tube(part, C, r0, 8, "cloth", np.array([0.0, -1.0, 0.0]), ATLAS["buckle"], tags=TAG_CLOTH)
    return part


def _ring_at(outer: np.ndarray, z: float, th: np.ndarray, S: float, off: float, band: float = 0.025) -> np.ndarray:
    return TC._outer_radius(outer, z, th, S, band) + off


def chest_rope(fields: Fields, chart: TorsoChart, params: dict, outer: np.ndarray) -> tuple[Part, list]:
    """Two horizontal turns of 2.2 cm rope round the body over the smock (and the cape at the back), dipping to 14 cm
    below the shoulder joint under each arm; the knot at the left of the sternum. Returns (part, turn centre lines)."""
    lm = fields.lm
    S = lm.S
    part = Part("ChestRope")
    part._mat = "cloth"
    rc = 0.5 * float(params["chest_rope_m"]) * S
    z_cl = float(lm.P("notch")[2])
    sh_z = float(lm.P("shoulder")[2])
    under = sh_z - float(params["chest_rope_underarm_drop_m"]) * S
    n = 72
    th = np.radians(np.linspace(0.0, 360.0, n, endpoint=False))
    D = dir_theta(th)
    lines = []
    u0, v0, u1, v1 = ATLAS["rope"]
    for k, below in enumerate(params["chest_rope_below_clavicle_m"]):
        z_front = z_cl - float(below) * S
        # the turn dips under the arms to the 14 cm line (the lower turn sits that low already)
        t = np.clip((np.abs(np.sin(th)) - ROPE_DIP_FROM) / (ROPE_DIP_FULL - ROPE_DIP_FROM), 0.0, 1.0)
        side = t * t * (3.0 - 2.0 * t)  # the full dip across the whole underarm, easing in toward the front and back
        z = z_front + (np.minimum(z_front, under - 0.05 * S * k) - z_front) * side
        r = np.array([_ring_at(outer, float(zz), np.array([a]), S, rc + float(params["chest_rope_off_m"]) * S)[0]
                      for zz, a in zip(z, th)])
        for _ in range(3):  # a rope pulled tight: no dents round the ring
            r = np.maximum(r, 0.5 * r + 0.25 * (np.roll(r, 1) + np.roll(r, -1)))
        C = np.stack([np.zeros(n), np.full(n, 0.01 * S), z], axis=-1) + D * r[:, None]
        C = np.concatenate([C, C[:1]])
        tube(part, C, rc, 7, "cloth", np.array([0.0, 0.0, 1.0]), (u0, v0 + (v1 - v0) * 0.5 * k, u1,
                                                                v0 + (v1 - v0) * 0.5 * (k + 1)), tags=TAG_CLOTH)
        lines.append(C[:-1])
    # the knot at the left of the sternum, between the turns
    a = math.radians(14.0)
    i0 = int(round(math.degrees(a) / 5.0))
    kc = 0.5 * (lines[0][i0] + lines[1][i0])
    out = dir_theta(np.array([a]))[0]
    uv_sphere(part, kc + out * 1.4 * rc, np.array([1.9, 1.3, 2.6]) * rc, 10, 6, "cloth", axis_fwd=out,
              uv_rect=(u0, v0, u0 + 0.06, v1), tags=TAG_CLOTH)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part, lines


def watch_cord(fields: Fields, outer: np.ndarray, z_belt: float, params: dict) -> tuple[Part, dict]:
    """The stair-watch captain's cord at the right hip: looped through the belt, 34 cm to mid-thigh, three knots 8 cm
    apart (kerrid.md §3). Returns (part, chain data: first vertex, rows, ring size, centre line)."""
    lm = fields.lm
    S = lm.S
    part = Part("WatchCord")
    part._mat = "cloth"
    rc = 0.5 * float(params["watch_cord_m"]) * S
    a = math.radians(-74.0)  # his right hip, a little forward of the side line
    dd = np.array([math.sin(a), -math.cos(a), 0.0])
    length = float(params["watch_cord_length_m"]) * S
    zs = np.linspace(z_belt + 0.01 * S, z_belt + 0.01 * S - length, CORD_ROWS)
    C = []
    r_prev = None
    for i, z in enumerate(zs):
        rr = float(TC._outer_radius(outer, z, np.array([a]), S, 0.03)[0]) + 0.006 * S + rc
        rr = rr if r_prev is None else max(rr, r_prev - 0.002 * S)  # hangs plumb past the widest point
        r_prev = rr
        C.append(np.array([0.0, 0.01 * S, z]) + dd * rr)
    C = np.array(C)
    first = len(part.V)
    u0, v0, u1, v1 = ATLAS["cord"]
    tube(part, C, rc, 6, "cloth", dd, (u0, v0, u1, v1), tags=TAG_CLOTH)
    rows, ring = CORD_ROWS, 6
    # three overhand knots, 8 cm apart from the lowest (8 mm above the end)
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))])
    gap = float(params["watch_cord_knot_gap_m"]) * S
    ku0, kv0, ku1, kv1 = ATLAS["knot"]
    for k in range(int(params["watch_cord_knots"])):
        at = s[-1] - 0.008 * S - k * gap
        p = np.array([np.interp(at, s, C[:, m]) for m in range(3)])
        uv_sphere(part, p, np.array([2.2, 2.0, 2.6]) * rc, 8, 5, "cloth", axis_fwd=dd, uv_rect=(ku0, kv0, ku1, kv1),
                  tags=TAG_CLOTH)
    # the loop round the belt
    loop = np.array([C[0] + np.array([0.0, 0.0, 0.012 * S]), C[0] + dd * 0.01 * S + np.array([0.0, 0.0, 0.03 * S]),
                     C[0] + np.array([0.0, 0.0, 0.05 * S])])
    tube(part, catmull_rom(loop, 6), rc, 6, "cloth", dd, (u0, v0, u1, v1), tags=TAG_CLOTH)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part, {"first": first, "rows": rows, "ring": ring, "count": len(part.V) - first, "line": C}


def ankle_ties(fields: Fields, side: str, rect) -> Part:
    """Two thin rope ties round the ankle above the sandal (kerrid.md §4.1 #3)."""
    lm = fields.lm
    S = lm.S
    an, kn = lm.side_pt("ankle", side), lm.side_pt("knee", side)
    part = Part(f"Ties{side}")
    for f in (0.0, 0.05):
        a = an + (kn - an) * (f - 0.015)
        b = an + (kn - an) * (f + 0.015)
        part.extend(limb_wrap(fields, f"leg_{side}", a, b, SANDAL_TIE_OFF * S, rect, "tie", n_around=14, rows=2))
    return part


def wrap(fields: Fields, params: dict) -> Part:
    """The left forearm wrap: from the half-hitch under the elbow over the wrist and the back of the hand to the
    knuckles, `wrap_off_m` off the skin (cloth over a scar, not a sleeve)."""
    lm = fields.lm
    S = lm.S
    path = RC.arm_path(lm, "L", WRAP_FROM_T, 1.0, 10)
    hand = lm.hands["L"]
    path = np.concatenate([path, [hand.wrist + hand.axis * hand.length * f for f in WRAP_HAND]])
    reg_arm, reg_hand = fields.region("arm_L"), fields.region("hand_L")
    import bb_anatomy

    def fld(Q: np.ndarray) -> np.ndarray:
        return bb_anatomy.smin(reg_arm(Q), reg_hand(Q), 0.01 * S)

    off = float(params["wrap_off_m"])
    part = RC.limb_tube(fields, fld, path, lambda t: (off + 0.0015 * max(0.0, 1.0 - t / 0.12)) * S, ATLAS["wrap"],
                        "Wrap", n_around=20, rows=16, back_inset=0.0015 * S)
    part.name = "Wrap"
    return part


# ---------------------------------------------------------------------------------------------
def build_costume(body, params: dict) -> tuple[dict[str, Part], dict]:
    """Returns ({name: Part}, info): the opaque costume pieces (the Wrap among them, which build_kerrid makes its own
    mesh). The chest rope and the watch cord are built later by build_kerrid (they sit over the cape)."""
    lm = body.lm
    S = lm.S
    fields = Fields(body)
    chart = TorsoChart(lm)
    z_waist = float(lm.P("waist")[2])
    z_crotch = float(lm.P("crotch")[2])
    out: dict[str, Part] = {}
    drop = float(params["smock_armhole_drop_m"])
    # 2. trousers: a pelvis band and two loose legs to 9 cm above the ankle
    th_t = np.linspace(0.0, 360.0, 32, endpoint=False)
    pelvis = Part("TrouserTop")
    pelvis._mat = "cloth"
    rows = 7
    P = np.zeros((rows, len(th_t), 3))
    D = dir_theta(np.radians(th_t))
    for j in range(rows):
        z = z_waist + 0.01 * S + (z_crotch + 0.015 * S - z_waist - 0.01 * S) * j / (rows - 1)
        O = np.stack([np.zeros(len(th_t)), np.full(len(th_t), 0.01 * S), np.full(len(th_t), z)], axis=-1)
        r = cast_last(lambda Q: fields.lower(Q) - TROUSER_OFF * S, O, D, 0.5 * S)
        P[j] = O + D * r[:, None]
    _panel(pelvis, P, ATLAS["trousers"], None, True, 0.0018 * S, np.array([0.0, 0.01 * S, 0.0]))
    out["TrouserTop"] = pelvis
    an_z = float(lm.side_pt("ankle", "L")[2])
    hem = an_z + float(params["trouser_hem_above_ankle_m"]) * S
    for sd in ("L", "R"):
        path = RC.leg_path(lm, sd, z_crotch + 0.06 * S, hem, 14)
        out[f"TrouserLeg{sd}"] = RC.limb_tube(
            fields, f"leg_{sd}", path, lambda t: (0.0080 + 0.014 * math.sin(math.pi * min(t * 1.1, 1.0)) ** 1.2) * S,
            ATLAS[f"trouser_leg_{sd}"], f"TrouserLeg{sd}", n_around=22, rows=14, back_inset=0.0018 * S, wind_amp=0.05)
    # 1. the smock: the body to the waist (torso only), the skirt below it, the dropped-shoulder sleeves
    th_s = np.linspace(0.0, 360.0, 36, endpoint=False)
    out["Smock"] = RC.torso_sheet(fields, chart, "Smock", ATLAS["smock"], th_s, smock_neck(lm, chart, th_s, drop),
                                  z_waist - 0.03 * S, SMOCK_OFF * S, SMOCK_ROWS, 0.0018 * S, True, wind_amp=0.03)
    out["SmockSkirt"], skirt_rows = smock_skirt(fields, z_waist + 0.02 * S, hem_z(lm, params),
                                                out["TrouserTop"].varr())
    for sd in ("L", "R"):
        sh, el = lm.side_pt("shoulder", sd), lm.side_pt("elbow", sd)
        upper = float(np.linalg.norm(el - sh))
        t_end = 0.5 * (1.0 - float(params["sleeve_end_above_elbow_m"]) * S / upper)
        path = RC.arm_path(lm, sd, SLEEVE_TOP_T, t_end, 12)
        s0, s1 = SLEEVE_OFF
        out[f"Sleeve{sd}"] = RC.limb_tube(fields, f"arm_{sd}", path, lambda t, s0=s0, s1=s1: (s0 + (s1 - s0) * t) * S,
                                          ATLAS[f"sleeve_{sd}"], f"Sleeve{sd}", n_around=24, rows=12,
                                          back_inset=0.0018 * S, wind_amp=0.03, min_r=SLEEVE_MIN_R * S)
        roll = float(params["sleeve_roll_m"]) * S / upper * 0.5
        out[f"Cuff{sd}"] = RC.limb_tube(fields, f"arm_{sd}", RC.arm_path(lm, sd, t_end - roll, t_end + 0.004, 4),
                                        lambda t: CUFF_OFF * S, ATLAS[f"cuff_{sd}"], f"Cuff{sd}", n_around=24, rows=4,
                                        back_inset=0.002 * S, min_r=0.05 * S)
    # 3. sandals and ankle ties
    for sd in ("L", "R"):
        p = sandal(fields, sd, ATLAS["sandals"])
        p.extend(ankle_ties(fields, sd, ATLAS["sandals"]))
        p.name = f"Sandal{sd}"
        out[f"Sandal{sd}"] = p
    # 5. the belt over the smock
    belt_outer = np.concatenate([out["Smock"].varr(), out["SmockSkirt"].varr()])
    z_belt = z_waist - 0.005 * S
    out["Belt"] = belt(fields, z_belt, float(params["belt_width_m"]) * S, belt_outer)
    # 4. the wrap (its own mesh in build_kerrid)
    out["Wrap"] = wrap(fields, params)
    for p in out.values():
        if not p.C:
            p.C = [(0.0, 0.0, 0.0, 0.0)] * len(p.V)
        elif len(p.C) < len(p.V):
            p.C = p.C + [(0.0, 0.0, 0.0, 0.0)] * (len(p.V) - len(p.C))
    info = {"z_waist": z_waist, "z_crotch": z_crotch, "z_belt": z_belt, "hem_z": hem_z(lm, params),
            "hip_z": float(lm.side_pt("hip", "L")[2]), "skirt_rows": skirt_rows, "chart": chart, "fields": fields}
    return out, info


def build_over_cape(body, params: dict, outer_front: np.ndarray, outer_back: np.ndarray, z_belt: float,
                    belt_outer: np.ndarray) -> tuple[dict[str, Part], dict]:
    """The pieces that lie over the cape's mats: the chest rope (its outer = the smock in front and under the arms, the
    cape mats at the back) and the watch cord (over the belt and the smock's skirt)."""
    fields = Fields(body)
    chart = TorsoChart(body.lm)
    out = {}
    outer = np.concatenate([outer_front, outer_back])
    out["ChestRope"], lines = chest_rope(fields, chart, params, outer)
    out["WatchCord"], cord = watch_cord(fields, belt_outer, z_belt, params)
    return out, {"rope_lines": lines, "cord": cord}


def coverage(body, params: dict, V: np.ndarray, reg: np.ndarray) -> np.ndarray:
    """True for body vertices hidden under opaque clothing (with a margin), asha.md §8.1. The knees and shins stay
    under the trousers, the armpit skin under the dropped sleeve's mouth, the hand and knuckles under the wrap."""
    lm = body.lm
    S = lm.S
    chart = TorsoChart(lm)
    z_waist = float(lm.P("waist")[2])
    th, H = chart.H_of(V)
    th_deg = np.degrees(th)
    m = 0.025 * S
    torso = reg == "torso"
    drop = float(params["smock_armhole_drop_m"])
    smock = torso & (H < YC.skin_cut_top(lm, chart, th_deg, drop) - m)
    sleeves = np.zeros(len(V), dtype=bool)
    for sd in ("L", "R"):
        sh, el, wr = lm.side_pt("shoulder", sd), lm.side_pt("elbow", sd), lm.side_pt("wrist", sd)
        ax = wr - sh
        t = (V - sh) @ ax / (ax @ ax)
        upper = float(np.linalg.norm(el - sh))
        t_end = 0.5 * (1.0 - float(params["sleeve_end_above_elbow_m"]) * S / upper)
        sleeves |= (reg == f"arm_{sd}") & (t > SLEEVE_ARM_FROM) & (t < t_end - 0.06)
    sh, wr = lm.side_pt("shoulder", "L"), lm.side_pt("wrist", "L")
    ax = wr - sh
    t = (V - sh) @ ax / (ax @ ax)
    wrapped = (reg == "arm_L") & (t > WRAP_FROM_T + WRAP_CUT_IN) & (t < 0.95)
    legs = (reg == "leg_L") | (reg == "leg_R") | torso
    z_keep = max(float(lm.side_pt("knee", sd)[2]) for sd in ("L", "R")) + YC.KEEP_ABOVE_KNEE * S
    lower = legs & (V[:, 2] < z_waist - m) & (V[:, 2] > z_keep)
    return smock | sleeves | wrapped | lower
