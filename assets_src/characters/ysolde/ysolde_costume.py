"""Ysolde's costume as procedural cloth panels (no bpy), ysolde.md §2-§4 and §9.

Same method as Asha's, Rhen's and Toma's (asha_costume, rhen_costume, toma_costume): every garment is a pattern grid
whose rows are ray-cast onto the body field plus a fitting offset, and the grid is also the garment's island in the
2K costume atlas (ysolde_textures paints the same charts). Pieces, inner to outer (ysolde.md §4.1):

1. Under-gown, salt-white, sleeveless, a high round neck that shows in the collar's front gap. Torso only; the
   armhole is dropped 12 cm below the shoulder joint (the M1-CHR-14 11.5 cm rule plus margin).
2. Narrow trousers to the ankle (Rhen's `limb_tube` legs on a pelvis band), so a robe split never shows bare leg.
3. Soft closed slippers: a thin shell over each foot, taking the foot's weights (build_ysolde).
4. **The long split robe.** A bodice (torso only, the same dropped armhole) and, from the waist down, **four
   leg-following panels, not a tube** (M1-CHR-14: floor-length tubes clip under linear skinning): front-left,
   front-right and a back sheet whose left and right halves follow their own legs with a blend only across the back
   seam. They are split at both sides (the front panels overlap the back sheet from 6 cm below the hip joint down)
   and at the front left of centre (the front-left panel laps over the front-right one up to mid-thigh), so a stride
   opens them instead of driving a leg through the cloth. The panels hang straight from the hip (each row at least
   as wide as the one above it: a column, no flare) to a hem 9 cm above the floor. Their rows crowd toward the hem
   and the front-left panel's columns toward its front edge, so the gold border gets the texels (ysolde.md §8.2).
5. Dropped-shoulder sleeves, straight, 2 cm off the forearm at the wrist; the left cuff turned back 6 cm to its
   salt-white lining (a second, wider band at the left wrist).
6. **The winged standing collar** (its own mesh, `Collar`): two curved wings round the back of the neck, 13 cm tall
   at the back and 8 cm at the sides, opening forward to an 8 cm gap at the throat, standing off the head skin and
   hair by the clearance in `_costume` (it rides the upper torso; build_ysolde weights it). A closed 2.5 mm plate:
   the lacquered indigo outside, the salt-white inner face that carries the gold border, and the edge strip.
7. The salt-white cord belt, two turns at the waist, the knot at the left hip, two cord ends to mid-thigh with a gold
   bead each (the ends are chains of rig-extra bones, build_ysolde).

Vertex colour = wind (R primary, G ripple, B phase, A flutter). `coverage()` says which body vertices are hidden
under clothing (deleted, asha.md §8.1); as on Asha after M1-CHR-14, the knees and shins under the robe are kept.
Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

import rhen_costume as RC
import toma_costume as TC
from asha_costume import TAG_CLOTH, Fields, TorsoChart, _panel, cast_last, dir_theta
from asha_mesh import Part, tube, uv_sphere

# costume atlas islands (u0, v0, u1, v1), the shader's UV convention (v down); ysolde_textures paints them
ATLAS = {
    "bodice": (0.0, 0.0, 0.60, 0.30),
    "panel_back": (0.0, 0.30, 0.50, 0.62),
    "panel_fl": (0.60, 0.0, 0.80, 0.52),
    "panel_fr": (0.80, 0.0, 1.0, 0.52),
    "sleeve_L": (0.0, 0.62, 0.25, 0.80),
    "sleeve_R": (0.25, 0.62, 0.50, 0.80),
    "cuff": (0.50, 0.52, 0.75, 0.58),
    "collar_out": (0.50, 0.58, 0.75, 0.70),
    "collar_in": (0.75, 0.52, 1.0, 0.70),
    "collar_edge": (0.50, 0.70, 0.75, 0.72),
    "gown": (0.75, 0.70, 1.0, 0.84),
    "trousers": (0.50, 0.72, 0.75, 0.78),
    "trouser_leg_L": (0.50, 0.78, 0.625, 0.92),
    "trouser_leg_R": (0.625, 0.78, 0.75, 0.92),
    "slippers": (0.75, 0.84, 1.0, 0.94),
    "belt": (0.0, 0.80, 0.50, 0.84),
    "bead": (0.0, 0.84, 0.08, 0.88),
}
GOWN_OFF = 0.0045  # m at S = 1, over the skin
ROBE_OFF = 0.0095  # the bodice, over the gown
SLEEVE_OFF = (0.014, 0.020)  # at the shoulder and at the wrist (ysolde.md §4.1 #5: 2 cm off the forearm)
SLEEVE_TOP_T = -0.07  # the sleeve's top ring along the arm (0 = the shoulder joint): in over the shoulder's top to meet
# the bodice's strap (build_ysolde pushes it clear of the chest and back)
SLEEVE_MIN_R = 0.05  # m (at s = 1): the top rings' least radius (the dropped shoulder's ease)
SLEEVE_ARM_FROM = 0.18  # arm skin is cut under the sleeve from here (the armpit's skin stays: a raised arm opens it)
CUFF_OFF = 0.026  # the turned-back cuff, over the sleeve's end
TROUSER_OFF = 0.006  # narrow trousers
PANEL_OFF = {"back": 0.0135, "fr": 0.0165, "fl": 0.0195}  # the laps: front-left over front-right over the back
PANEL_UNDERLAP = 8.0  # degrees an under panel runs on beneath the one over it
PANEL_ROWS = 20
SLIPPER_OFF = 0.003
BELT_OFF = 0.006  # the cord's centre over the robe at the waist (plus its radius)
CORD_ROWS = 14
PANEL_TOP_BELOW_WAIST = 0.01  # m: the panels start just under the waist, lapping the bodice's last 2 cm
BODICE_BELOW_WAIST = 0.03
KEEP_ABOVE_KNEE = 0.16  # m (at s = 1) of thigh kept above the knee joint under the robe (Asha's M1-CHR-14 rule)
# the collar (ysolde.md §2.1, §4.1 #6)
COLLAR_COLS = 44
COLLAR_ROWS = 9
COLLAR_TOP_GAP_DEG = 70.0  # the wings' front edges at the top: the collar opens forward (the chin clears a 40 degree
# head turn)
COLLAR_ROBE_OFF = 0.014  # its base rides the robe's neckline
COLLAR_HAIR = 0.006  # m of hair over the scalp the clearance allows for (the cards lie within 5 mm)
COLLAR_FLARE = 0.0028  # m (at s = 1) each row stands out past the one below it: the wings lean out toward the top


def _wind_rows(n_rows: int, n_cols: int, amp: float, phase0: float = 0.0):
    return [[(amp * t * t, amp * t, (phase0 + i / n_cols * 3.0) % 1.0, 0.3 * amp * t) for i in range(n_cols)]
            for t in np.linspace(0.0, 1.0, n_rows)]


# ---------------------------------------------------------------------------------------------
# Torso lines
# ---------------------------------------------------------------------------------------------
def robe_top(lm, chart: TorsoChart, th_deg: np.ndarray, drop: float) -> np.ndarray:
    """The robe bodice's top edge: a high round neck (a little lower at the front, under the collar's gap) and the
    armhole `drop` below the shoulder joint on each side line (the dropped-shoulder sleeve covers the cap)."""
    S = lm.S
    neck = chart.z_sh + math.radians(55) * chart.k
    front = float(lm.P("notch")[2] - 0.004 * S)
    arm = float(lm.P("shoulder")[2] - drop * S)
    strap = chart.z_sh + math.radians(26) * chart.k
    # the edge holds the strap's height over the front and the back of the shoulder and drops only near the side
    # line (a sleeveless cut there would show the skin between the bodice and the dropped sleeve)
    # and it rises to the collar's base over the top of the shoulder (the collar wings flare away from it)
    return RC._sym_interp(th_deg, [0, 18, 34, 52, 66, 80, 92, 104, 118, 132, 150, 180],
                          [front, front + 0.006 * S, neck - 0.012 * S, neck - 0.02 * S, strap, arm + 0.05 * S, arm,
                           arm + 0.05 * S, strap, neck - 0.02 * S, neck, neck])


def skin_cut_top(lm, chart: TorsoChart, th_deg: np.ndarray, drop: float) -> np.ndarray:
    """Where the torso skin under the bodice is cut (coverage): the sleeveless line, so the skin stays under the
    bodice's shoulder pieces in front of and behind the armhole (the bodice there rides the shoulder cap, and a cut
    edge under it opened as the arm moved)."""
    S = lm.S
    neck = chart.z_sh + math.radians(55) * chart.k
    front = float(lm.P("notch")[2] - 0.004 * S)
    arm = float(lm.P("shoulder")[2] - drop * S)
    strap = chart.z_sh + math.radians(26) * chart.k
    return RC._sym_interp(th_deg, [0, 18, 34, 52, 74, 92, 112, 132, 150, 180],
                          [front, front + 0.006 * S, neck - 0.012 * S, strap, arm, arm, strap, neck, neck, neck])


def gown_top(lm, chart: TorsoChart, th_deg: np.ndarray, drop: float) -> np.ndarray:
    """The under-gown's high round neck (above the robe's at the front, so it shows in the collar gap) and its
    dropped armholes."""
    S = lm.S
    neck = chart.z_sh + math.radians(58) * chart.k
    front = float(lm.P("notch")[2] + 0.010 * S)
    arm = float(lm.P("shoulder")[2] - drop * S)
    strap = chart.z_sh + math.radians(24) * chart.k
    return RC._sym_interp(th_deg, [0, 20, 34, 52, 74, 92, 112, 132, 150, 180],
                          [front, front, neck - 0.010 * S, strap, arm, arm, strap, neck, neck, neck])


def crowded(a: float, b: float, n: int, power: float) -> np.ndarray:
    """n values from a to b, crowded toward a (power > 1)."""
    return a + (b - a) * np.linspace(0.0, 1.0, n) ** power


def bodice_azimuths(front_split: float, n: int = 60) -> np.ndarray:
    """A closed ring of azimuths from the front-left edge round her right and back to it, crowded on both sides of
    the edge (the vertical gold border runs there)."""
    u = np.linspace(0.0, 1.0, n, endpoint=False)
    w = u + 0.10 * np.sin(2 * math.pi * u) / (2 * math.pi) * -2.2  # denser near u = 0 (the edge)
    return (front_split + 360.0 * w) % 360.0


# ---------------------------------------------------------------------------------------------
# The robe's panels
# ---------------------------------------------------------------------------------------------
def panel_rows(z_top: float, z_hem: float, n: int) -> np.ndarray:
    """Row heights from the top to the hem, crowding toward the hem (the hem border's texels, and the hem line)."""
    t = np.linspace(0.0, 1.0, n)
    f = 0.5 * t + 0.5 * (1.0 - (1.0 - t) ** 2.2)
    return z_top + (z_hem - z_top) * f


def ring_radii(fields: Fields, z_rows: np.ndarray, n_th: int = 720) -> tuple[np.ndarray, np.ndarray]:
    """The robe's base radius per row on a dense ring of azimuths (about the waist axis), over the lower body
    field; each row at least as wide as the one above it (a straight column bridging the legs)."""
    lm = fields.lm
    S = lm.S
    th = np.radians(np.linspace(0.0, 360.0, n_th, endpoint=False))
    D = dir_theta(th)
    R = np.zeros((len(z_rows), n_th))
    prev = None
    for j, z in enumerate(z_rows):
        O = np.stack([np.zeros(n_th), np.full(n_th, 0.01 * S), np.full(n_th, z)], axis=-1)
        r = cast_last(fields.lower, O, D, 0.5 * S)
        if prev is not None:
            r = np.maximum(r, prev)
        # smooth round the ring (a column has no dents between the legs)
        for _ in range(6):
            r = np.maximum(r, 0.5 * r + 0.25 * (np.roll(r, 1) + np.roll(r, -1)))
        R[j] = r
        prev = r
    return np.degrees(th), R


def panel(fields: Fields, name: str, rect, th_deg: np.ndarray, z_rows: np.ndarray, ring: tuple, off: float,
          seed: int, fold_amp: float = 0.004) -> Part:
    """One open robe panel over the azimuths th_deg (in order) and the rows z_rows, `off` over the base radius."""
    part = Part(name)
    part._mat = "cloth"
    lm = fields.lm
    S = lm.S
    th_ring, R = ring
    rng = np.random.default_rng(seed)
    phase = rng.uniform(0.0, 2 * math.pi)
    th = np.radians(th_deg)
    D = dir_theta(th)
    P = np.zeros((len(z_rows), len(th), 3))
    for j, z in enumerate(z_rows):
        t = j / (len(z_rows) - 1)
        r = np.interp(np.mod(th_deg, 360.0), th_ring, R[j], period=360.0) + off
        # a few long soft folds, deepening toward the hem (heavy crepe: shallow)
        r = r + fold_amp * S * t ** 1.4 * np.sin(5.0 * th + phase)
        O = np.stack([np.zeros(len(th)), np.full(len(th), 0.01 * S), np.full(len(th), z)], axis=-1)
        P[j] = O + D * r[:, None]
    _panel(part, P, rect, _wind_rows(len(z_rows), len(th), 0.10, 0.1 + 0.3 * (seed % 3)), False, 0.0016 * S,
           np.array([0.0, 0.01 * S, 0.0]))
    part.grid_P = P
    part.grid_th = th_deg
    return part


def panel_spans(front_split: float) -> dict:
    """Azimuth ranges (degrees, in column order) of the panels: the front-left panel from its front edge to the
    left side line; the front-right from the right side line to under the front-left; the back sheet from under the
    left front panel round the back to under the right."""
    u = PANEL_UNDERLAP
    return {"fl": (front_split, 90.0), "fr": (-90.0, front_split + u), "back": (90.0 - u, 270.0 + u)}


# ---------------------------------------------------------------------------------------------
# The collar
# ---------------------------------------------------------------------------------------------
def collar_height(params: dict, a: np.ndarray) -> np.ndarray:
    """The collar's height by |azimuth| from the front (0) to the back (180): 13 cm at the back, 8 cm at the side
    lines, lower toward the wings' front edges (from the front a shallow V of dark round the face)."""
    back, side = float(params["collar_back_m"]), float(params["collar_side_m"])
    return np.interp(np.abs(a), [0.0, 40.0, 64.0, 90.0, 130.0, 180.0],
                     [0.40 * side, 0.55 * side, 0.78 * side, side, 0.5 * (side + back) + 0.01, back])


def collar(fields: Fields, body, params: dict) -> tuple[Part, dict]:
    """The winged standing collar on the robe's neckline, clear of the head skin and the hair (ysolde.md §4.1 #6)."""
    lm = fields.lm
    S = lm.S
    nb, sb = lm.P("neck_base"), lm.P("skull_base")
    ax = (sb - nb) / np.linalg.norm(sb - nb)
    clear = float(params["collar_standoff_m"])
    gap = float(params["collar_front_gap_m"])
    torso = body.regions["torso"].sdf
    head = body.regions["head"].sdf

    def keep_out(Q: np.ndarray) -> np.ndarray:
        return np.minimum(torso(Q) - COLLAR_ROBE_OFF * S, head(Q) - clear - COLLAR_HAIR)

    # the front gap: 8 cm across the throat at the base, the wings' edges swinging back toward the top
    r_throat = float(cast_last(torso, nb[None, :], np.array([[0.0, -1.0, 0.0]]), 0.2 * S)[0]) + COLLAR_ROBE_OFF * S
    a0 = math.degrees(math.asin(min(0.5 * gap / max(r_throat, 1e-3), 0.95)))
    rows, cols = COLLAR_ROWS, COLLAR_COLS
    P = np.zeros((rows, cols, 3))
    prev_r = None
    for j in range(rows):
        s = 1.0 - j / (rows - 1)  # row 0 = the top edge
        a = a0 + (COLLAR_TOP_GAP_DEG - a0) * s ** 1.3
        th_deg = a + (360.0 - 2.0 * a) * np.linspace(0.0, 1.0, cols)
        signed = ((th_deg + 180.0) % 360.0) - 180.0
        h = collar_height(params, signed) * s
        th = np.radians(th_deg)
        d = dir_theta(th)
        d = d - np.outer(d @ ax, ax)
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        O = nb[None, :] + np.outer(h, ax)
        r = cast_last(keep_out, O, d, 0.25 * S)
        P[j] = O + d * r[:, None]
        _ = prev_r
    # flare: no row sits inside the one below it (the wings stand off and lean out a little toward the top)
    rad = np.zeros((rows, cols))
    base_h = np.zeros((rows, cols))
    for j in range(rows):
        q = P[j] - nb
        base_h[j] = q @ ax
        rad[j] = np.linalg.norm(q - np.outer(base_h[j], ax), axis=1)
    for j in range(rows - 2, -1, -1):
        rad[j] = np.maximum(rad[j], rad[j + 1] + COLLAR_FLARE * S)
    for _ in range(3):  # smooth along the wings
        rad[:, 1:-1] = np.maximum(rad[:, 1:-1], 0.5 * rad[:, 1:-1] + 0.25 * (rad[:, :-2] + rad[:, 2:]))
    for j in range(rows):
        q = P[j] - nb
        dirs = q - np.outer(base_h[j], ax)
        dirs /= np.maximum(np.linalg.norm(dirs, axis=1, keepdims=True), 1e-9)
        P[j] = nb + np.outer(base_h[j], ax) + dirs * rad[j][:, None]
    centre = nb + ax * 0.05 * S
    N = np.zeros_like(P)
    du = np.gradient(P, axis=1)
    dv = np.gradient(P, axis=0)
    N = np.cross(dv, du)
    N /= np.maximum(np.linalg.norm(N, axis=-1, keepdims=True), 1e-12)
    out = P - centre
    out = out - (out @ ax)[..., None] * ax
    N = np.where((np.sum(N * out, axis=-1) < 0)[..., None], -N, N)
    part = Part("Collar")
    part._mat = "cloth"
    TC._plate(part, P, N, float(params["collar_thickness_m"]), ATLAS["collar_out"], ATLAS["collar_in"],
              ATLAS["collar_edge"])
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    s_of = np.repeat(np.linspace(1.0, 0.0, rows)[:, None], cols, axis=1)
    return part, {"grid": P, "s": s_of, "axis": ax, "base": nb, "front_gap_deg": a0}


# ---------------------------------------------------------------------------------------------
# Belt, slippers
# ---------------------------------------------------------------------------------------------
def _outer_r(outer: np.ndarray, z: float, th: np.ndarray, S: float, band: float = 0.02) -> np.ndarray:
    return TC._outer_radius(outer, z, th, S, band)


def cord_belt(fields: Fields, outer: np.ndarray, z_belt: float, params: dict, hip_z: float,
              knee_z: float) -> tuple[Part, list]:
    """Two turns of 8 mm salt-white cord at the waist, the knot at the left hip, two cord ends to mid-thigh with a
    gold-leaf bead each. Returns (part, cord_ends): per end the (first vertex, rows, ring size) of its tube and its
    centre line, for the rig's chain weights."""
    lm = fields.lm
    S = lm.S
    part = Part("Belt")
    part._mat = "cloth"
    rc = 0.5 * float(params["belt_cord_m"]) * S
    n = 48
    th = np.radians(np.linspace(0.0, 360.0, n, endpoint=False))
    D = dir_theta(th)
    u0, v0, u1, v1 = ATLAS["belt"]
    for k in range(int(params["belt_turns"])):
        z = z_belt + (k - 0.5) * 2.3 * rc
        r = _outer_r(outer, z, th, S) + BELT_OFF * S * 0.5 + rc + k * 0.4 * rc
        C = np.stack([np.zeros(n), np.full(n, 0.01 * S), np.full(n, z)], axis=-1) + D * r[:, None]
        C = np.concatenate([C, C[:1]])
        tube(part, C, rc, 6, "cloth", np.array([0.0, 0.0, 1.0]), (u0, v0 + (v1 - v0) * 0.5 * k, u1,
                                                                v0 + (v1 - v0) * 0.5 * (k + 1)), tags=TAG_CLOTH)
    # the knot at the left hip
    th_k = math.radians(78.0)
    dk = np.array([math.sin(th_k), -math.cos(th_k), 0.0])
    r_k = float(_outer_r(outer, z_belt, np.array([th_k]), S)[0])
    knot = np.array([0.0, 0.01 * S, z_belt]) + dk * (r_k + 2.6 * rc + BELT_OFF * S * 0.5)
    uv_sphere(part, knot, np.array([1.9, 1.5, 2.2]) * rc * 1.6, 10, 6, "cloth", axis_fwd=dk,
              uv_rect=(u0, v0, u0 + 0.05, v1), tags=TAG_CLOTH)
    ends = []
    z_end = 0.5 * (hip_z + knee_z)
    for k, (dth, drop) in enumerate(((-6.0, 0.0), (7.0, 0.035))):
        a = th_k + math.radians(dth)
        dd = np.array([math.sin(a), -math.cos(a), 0.0])
        zs = np.linspace(knot[2] - 1.5 * rc, z_end - drop * S, CORD_ROWS)
        C = []
        r_prev = None
        for i, z in enumerate(zs):
            rr = float(_outer_r(outer, z, np.array([a]), S, 0.03)[0]) + (0.006 + 0.004 * k) * S + rc
            rr = rr if r_prev is None else max(rr, r_prev - 0.003 * S)  # hangs plumb past the widest point
            r_prev = rr
            sway = np.cross(np.array([0.0, 0.0, 1.0]), dd) * (0.006 * S * math.sin(2.0 * i / CORD_ROWS + k))
            C.append(np.array([0.0, 0.01 * S, z]) + dd * rr + sway)
        C = np.array(C)
        C[0] = knot + (C[1] - knot) * 0.3
        first = len(part.V)
        tube(part, C, rc * 0.9, 6, "cloth", dd, (u0, v0, u1, v1), tags=TAG_CLOTH)
        bead = C[-1] + (C[-1] - C[-2]) / np.linalg.norm(C[-1] - C[-2]) * 0.5 * float(params["belt_bead_m"]) * S
        bu0, bv0, bu1, bv1 = ATLAS["bead"]
        uv_sphere(part, bead, 0.5 * float(params["belt_bead_m"]) * S, 10, 6, "cloth", axis_fwd=dd,
                  uv_rect=(bu0, bv0, bu1, bv1), tags=TAG_CLOTH)
        ends.append({"first": first, "rows": CORD_ROWS, "ring": 6, "count": len(part.V) - first, "line": C})
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    return part, ends


def slipper(fields: Fields, side: str, rect) -> Part:
    """A soft closed slipper: a thin shell cast over the foot along its length, closed at the heel and the toe, the
    sole just under the floor."""
    lm = fields.lm
    S = lm.S
    hb_, tt = lm.side_pt("heel_back", side), lm.side_pt("toe_tip", side)
    fwd = (tt - hb_) / np.linalg.norm(tt - hb_)
    a = hb_ - fwd * 0.012 * S
    a[2] = 0.034 * S
    b = tt + fwd * 0.010 * S
    b[2] = 0.014 * S
    path = np.array([a + (b - a) * t for t in np.linspace(0.0, 1.0, 12)])
    path[:, 2] += 0.010 * S * np.sin(np.linspace(0.0, math.pi, 12)) * 0.6  # the instep's rise
    foot, leg = fields.region(f"foot_{side}"), fields.region(f"leg_{side}")

    def fld(Q: np.ndarray) -> np.ndarray:  # the foot and the ankle above it: the shell never dips into the ankle
        return np.minimum(foot(Q), leg(Q))

    part = RC.limb_tube(fields, fld, path, lambda t: SLIPPER_OFF * S, rect, f"Slipper{side}", n_around=18, rows=12)
    # the sole sits on the floor: nothing goes more than 2 mm under it
    for k, v in enumerate(part.V):
        if v[2] < -0.002:
            part.V[k] = np.array([v[0], v[1], -0.002])
    return part


# ---------------------------------------------------------------------------------------------
def build_costume(body, params: dict) -> tuple[dict[str, Part], dict]:
    """Returns ({name: Part}, info): the opaque costume pieces (the Collar among them, which build_ysolde makes its
    own mesh), and the panel and cord data the rig extras need."""
    lm = body.lm
    S = lm.S
    fields = Fields(body)
    chart = TorsoChart(lm)
    z_waist = float(lm.P("waist")[2])
    z_crotch = float(lm.P("crotch")[2])
    hip_z = float(lm.side_pt("hip", "L")[2])
    knee_z = float(lm.side_pt("knee", "L")[2])
    out: dict[str, Part] = {}
    fs = float(params["front_split_deg"])
    # 1. under-gown
    th_g = np.linspace(0.0, 360.0, 44, endpoint=False)
    out["Gown"] = RC.torso_sheet(fields, chart, "Gown", ATLAS["gown"], th_g,
                                 gown_top(lm, chart, th_g, float(params["gown_armhole_drop_m"])), z_waist,
                                 GOWN_OFF * S, 9, None, True)
    # 4a. robe bodice: closed, the front-left edge (the border's line) at the front split
    th_b = bodice_azimuths(fs)
    out["Bodice"] = RC.torso_sheet(fields, chart, "Bodice", ATLAS["bodice"], th_b,
                                   robe_top(lm, chart, th_b, float(params["sleeve_seam_drop_m"])),
                                   z_waist - BODICE_BELOW_WAIST * S, ROBE_OFF * S, 16, 0.0022 * S, True, wind_amp=0.04)
    # 4b. panels
    z_hem = float(params["robe_hem_above_floor_m"])
    z_rows = panel_rows(z_waist - PANEL_TOP_BELOW_WAIST * S, z_hem, PANEL_ROWS)
    ring = ring_radii(fields, z_rows)
    spans = panel_spans(fs)
    seed = int(params["seed"])
    a, b = spans["fl"]
    out["PanelFL"] = panel(fields, "PanelFL", ATLAS["panel_fl"], crowded(a, b, 22, 1.5), z_rows, ring,
                           PANEL_OFF["fl"] * S, seed)
    a, b = spans["fr"]
    out["PanelFR"] = panel(fields, "PanelFR", ATLAS["panel_fr"], np.linspace(a, b, 24), z_rows, ring,
                           PANEL_OFF["fr"] * S, seed + 1)
    a, b = spans["back"]
    out["PanelBack"] = panel(fields, "PanelBack", ATLAS["panel_back"], np.linspace(a, b, 40), z_rows, ring,
                             PANEL_OFF["back"] * S, seed + 2)
    # 5. sleeves and the left cuff
    for sd in ("L", "R"):
        path = RC.arm_path(lm, sd, SLEEVE_TOP_T, 0.965, 16)
        s0, s1 = SLEEVE_OFF
        out[f"Sleeve{sd}"] = RC.limb_tube(fields, f"arm_{sd}", path, lambda t, s0=s0, s1=s1: (s0 + (s1 - s0) * t) * S,
                                          ATLAS[f"sleeve_{sd}"], f"Sleeve{sd}", n_around=24, rows=16,
                                          back_inset=0.0018 * S, wind_amp=0.05, min_r=SLEEVE_MIN_R * S)
    el, wr = lm.side_pt("elbow", "L"), lm.side_pt("wrist", "L")
    fore = float(np.linalg.norm(wr - el))
    t0 = 0.965 - 0.5 * float(params["cuff_turnback_m"]) * S / fore
    out["Cuff"] = RC.limb_tube(fields, "arm_L", RC.arm_path(lm, "L", t0, 0.972, 5), lambda t: CUFF_OFF * S,
                               ATLAS["cuff"], "Cuff", n_around=24, rows=5, back_inset=0.002 * S)
    # 2. trousers: a pelvis band and two narrow legs to the ankle
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
    _panel(pelvis, P, ATLAS["trousers"], None, True, 0.0015 * S, np.array([0.0, 0.01 * S, 0.0]))
    out["TrouserTop"] = pelvis
    an_z = float(lm.side_pt("ankle", "L")[2])
    for sd in ("L", "R"):
        path = RC.leg_path(lm, sd, z_crotch + 0.06 * S, an_z + 0.004 * S, 14)
        out[f"TrouserLeg{sd}"] = RC.limb_tube(fields, f"leg_{sd}", path,
                                              lambda t: (TROUSER_OFF + 0.002 * math.sin(math.pi * t)) * S,
                                              ATLAS[f"trouser_leg_{sd}"], f"TrouserLeg{sd}", n_around=20, rows=14,
                                              back_inset=0.0015 * S, wind_amp=0.03)
    # 3. slippers
    for sd in ("L", "R"):
        out[f"Slipper{sd}"] = slipper(fields, sd, ATLAS["slippers"])
    # 7. the cord belt over the bodice and the panels' top
    outer = np.concatenate([out[k].varr() for k in ("Bodice", "PanelFL", "PanelFR", "PanelBack")])
    out["Belt"], cord_ends = cord_belt(fields, outer, z_waist - 0.012 * S, params, hip_z, knee_z)
    # 6. the collar
    out["Collar"], cinfo = collar(fields, body, params)
    for p in out.values():
        if not p.C:
            p.C = [(0.0, 0.0, 0.0, 0.0)] * len(p.V)
        elif len(p.C) < len(p.V):
            p.C = p.C + [(0.0, 0.0, 0.0, 0.0)] * (len(p.V) - len(p.C))
    info = {"z_rows": z_rows, "spans": spans, "cord_ends": cord_ends, "collar": cinfo, "hip_z": hip_z,
            "knee_z": knee_z, "z_waist": z_waist, "z_hem": z_hem}
    return out, info


def coverage(body, params: dict, V: np.ndarray, reg: np.ndarray) -> np.ndarray:
    """True for body vertices hidden under opaque clothing (with a margin), asha.md §8.1. The knees and shins stay
    under the robe and the trousers (a stride carries them out through the panels; M1-CHR-14), and the feet stay
    under the slippers."""
    lm = body.lm
    S = lm.S
    chart = TorsoChart(lm)
    z_waist = float(lm.P("waist")[2])
    th, H = chart.H_of(V)
    th_deg = np.degrees(th)
    m = 0.025 * S
    torso = reg == "torso"
    bodice = torso & (H < skin_cut_top(lm, chart, th_deg, float(params["sleeve_seam_drop_m"])) - m)
    sleeves = np.zeros(len(V), dtype=bool)
    for sd in ("L", "R"):
        sh, wr = lm.side_pt("shoulder", sd), lm.side_pt("wrist", sd)
        ax = wr - sh
        t = (V - sh) @ ax / (ax @ ax)
        sleeves |= (reg == f"arm_{sd}") & (t > SLEEVE_ARM_FROM) & (t < 0.90)
    legs = (reg == "leg_L") | (reg == "leg_R") | torso
    z_keep = max(float(lm.side_pt("knee", sd)[2]) for sd in ("L", "R")) + KEEP_ABOVE_KNEE * S
    lower = legs & (V[:, 2] < z_waist - m) & (V[:, 2] > z_keep)
    return bodice | sleeves | lower
