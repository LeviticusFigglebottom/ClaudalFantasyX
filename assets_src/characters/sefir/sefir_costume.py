"""Sefir's costume as procedural cloth panels and one lacquered shell (no bpy), act1_npcs.md §1.3-§1.4 and §1.10.

Same method as Asha's, Rhen's and Toma's (asha_costume, rhen_costume, toma_costume): every garment is a pattern grid
whose rows are ray-cast onto the body field plus a fitting offset, and the grid is also the garment's island in the
2K costume atlas (sefir_textures paints the same charts). Pieces, inner to outer:

1. Under-robe (`ivory_silk`): a closed torso with a high round collar, dropped-shoulder armholes 12 cm below the
   shoulder joints, wrist-length sleeves (tubes down each arm from the shoulder joint) and a gusset under each arm
   (a small torso panel inside the sleeve at rest that fills the armhole when the arm comes up).
2. Full-length loose trousers (`ivory_silk`): a pelvis band and two leg tubes to just above the ankle; they show at
   the over-robe's splits instead of leg.
3. Closed thin-soled slippers (ivory leather): a loft of horizontal slices of the foot field plus a flat sole.
4. The over-robe (`still_blue_silk`): a sleeveless torso to the hips (armholes 13 cm below the shoulder joints,
   a round neckline under the ivory collar) and, from the waist down, **four panels**, never a tube: the front and
   the back are split at the centre to mid-thigh, the sides to 6 cm below the hip joints. Each panel follows its own
   leg (build_asha.skirt_weights) plus a chain of 4 panel bones (build_sefir). The hem sits 1.5 cm off the floor.
   Above a split the two panels share their edge column exactly (one welded seam, the same weights on both sides);
   below it the upper panel's edge laps 5 degrees past the seam, lifted a few millimetres, so a stride opens the
   split instead of tearing a seam. Which panel laps over: the left front over the right at the front, the front
   panels over the back ones at the sides, the left back over the right at the back (art decision).
5. **The half-mantle** (right shoulder only): one stiff lacquered shell from the base of the neck over the shoulder
   to 9 cm above the elbow, and down the chest and the back to mid-ribcage, its front and back edges cut in a curve.
   Built like Toma's pauldron lames (a closed plate: outer face, inner face, edge strip) on its own chart, without the
   chisel pass: slices across a guide curve (neck -> shoulder -> arm), each a fan of rays cast onto the body field
   plus the 25 mm clearance; the edge over the arm flares 4 cm off it. The ~900 Level scales are texture detail
   (sefir_textures, motifs/level_scale.json), never geometry.

The crown is a prop (sefir_props). Vertex colour = wind (R primary, G ripple, B phase, A flutter). `coverage()` says
which body vertices are hidden under clothing (deleted, asha.md §8.1). Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

import rhen_costume as RC
from asha_costume import TAG_CLOTH, Fields, TorsoChart, _panel, cast_last, collar, dir_theta
from asha_mesh import Part, catmull_rom, grid
from toma_costume import _grid_normals, _plate, _shell

# costume atlas islands (u0, v0, u1, v1), the shader's UV convention (v down); sefir_textures paints them
ATLAS = {
    "underrobe": (0.0, 0.0, 0.30, 0.14),
    "collar": (0.30, 0.0, 0.50, 0.04),
    "trousers": (0.30, 0.04, 0.40, 0.10),
    "sleeve_L": (0.0, 0.14, 0.25, 0.24),
    "sleeve_R": (0.25, 0.14, 0.50, 0.24),
    "trouser_leg_L": (0.0, 0.24, 0.20, 0.36),
    "trouser_leg_R": (0.20, 0.24, 0.40, 0.36),
    "slippers": (0.40, 0.24, 0.50, 0.36),
    "robe": (0.0, 0.36, 0.50, 0.56),
    "panel_FL": (0.0, 0.56, 0.125, 1.0),
    "panel_BL": (0.125, 0.56, 0.25, 1.0),
    "panel_BR": (0.25, 0.56, 0.375, 1.0),
    "panel_FR": (0.375, 0.56, 0.50, 1.0),
    "mantle": (0.50, 0.0, 1.0, 0.50),
    "mantle_inner": (0.50, 0.50, 0.75, 0.75),
    "mantle_edge": (0.75, 0.50, 1.0, 0.54),
    "gusset_L": (0.40, 0.04, 0.45, 0.10),
    "gusset_R": (0.45, 0.04, 0.50, 0.10),
    "yoke_L": (0.75, 0.54, 0.875, 0.75),
    "yoke_R": (0.875, 0.54, 1.0, 0.75),
}
UNDER_OFF = 0.004  # m at S = 1: the under-robe over the skin
ROBE_OFF = 0.011  # the over-robe's torso over the under-robe
SKIRT_OFF_TOP = 0.017  # the robe skirt's top edge sits just outside the robe torso's hem (a waist seam) ...
SKIRT_OFF = 0.022  # ... and over the loose trousers below
SKIRT_OFF_RAMP = 0.10  # m over which the skirt's offset grows from the top value to the full one
TROUSER_OFF = 0.009
SLIPPER_OFF = 0.0035
ROBE_TOP_ABOVE_WAIST = 0.015  # m (x S): the skirt panels' top edge (the waist seam)
ROBE_HEM_BELOW_WAIST = 0.05  # m (x S): the robe torso's hem, under the skirt's top
UNDER_HEM_BELOW_WAIST = 0.03
GUSSET_AZIMUTH = (58.0, 122.0)  # deg round the side (0 front, 90 his left side)
GUSSET_BELOW_JOINT = 0.03  # m (x S): the gusset's top, under the shoulder joint
GUSSET_OVERLAP = 0.03  # m (x S) below the armhole's bottom: it laps under the under-robe's side
GUSSET_ROWS = 5
GUSSET_COLS = 9
SKIRT_FLARE = 0.12  # each row at least this x the drop wider than the one above (it bridges the legs)
SKIRT_FOLDS = 14  # fold periods round the whole skirt (GPU QA row 54: 7 at 4 mm read as a rigid cylinder)
SKIRT_FOLD_AMP = 0.016  # x S at the hem (was 0.004)
SKIRT_FOLD_2ND = (2.3, 0.45)  # a second, irregular fold harmonic: its frequency and share of the amplitude
PANEL_COLS = 18  # (was 14) to resolve the folds
PANEL_ROWS = 22
LAP_DEG = 5.0  # below a split, the upper panel's edge laps this far past the seam ...
LAP_LIFT = 0.006  # m (x S) ... and stands this far off the panel it covers ...
LAP_RAMP = 0.06  # m over which the lap grows in below the split top
LAP_EDGE_COLS = 4  # columns over which the lift fades back to the panel's own surface
# (panel, azimuth from, azimuth to, leg). Azimuth 0 = front, +90 = his left.
PANELS = (("FL", 0.0, 90.0, "L"), ("BL", 90.0, 180.0, "L"), ("BR", 180.0, 270.0, "R"), ("FR", 270.0, 360.0, "R"))
# which panel laps over at each seam (azimuth mod 360)
LAPS_OVER = {0.0: "FL", 90.0: "FL", 180.0: "BL", 270.0: "FR"}
# --- the half-mantle -----------------------------------------------------------------------------
MANTLE_COLS = 44  # front edge -> back edge
MANTLE_ROWS = 28  # neck -> arm
MANTLE_FAN = 361  # rays per slice from which the edges and the columns are resampled
MANTLE_LIMS = (132.0, 124.0, 102.0)  # fan half-angles (deg) at the neck, the shoulder joint and the arm end
MANTLE_SMOOTH = 8  # Laplacian passes over the shell grid before each clearance pass
YOKE_NECK_TO = 0.072  # m (x S) from the midline: the yoke's medial edge, under the robe neckline
YOKE_END = 0.07  # m (x S) down the upper arm from the shoulder joint
YOKE_LIMS = (98.0, 100.0, 96.0)
YOKE_OFF = 0.013  # over the under-robe and the sleeve top
YOKE_ROWS = 12
YOKE_COLS = 22
SLIPPER_N = 28
SLIPPER_ROWS = (0.0, 0.010, 0.022, 0.036, 0.052, 0.068)  # x S: slice heights from the floor
SLIPPER_TOP_ABOVE_ANKLE = 0.030  # x S: the slipper's collar, inside the trouser hem


def _wind_rows(n_rows: int, n_cols: int, amp: float, phase0: float = 0.0):
    return [[(amp * t * t, amp * t, (phase0 + i / n_cols * 3.0) % 1.0, 0.3 * amp * t) for i in range(n_cols)]
            for t in np.linspace(0.0, 1.0, n_rows)]


def smooth01(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


# ---------------------------------------------------------------------------------------------
# Torso
# ---------------------------------------------------------------------------------------------
def underrobe_top(lm, chart: TorsoChart, th_deg: np.ndarray, drop: float) -> np.ndarray:
    """A high round neck all round (the stand collar sits on it), dropped-shoulder armholes."""
    S = lm.S
    neck = chart.z_sh + math.radians(58) * chart.k
    arm = float(lm.P("shoulder")[2] - drop * S)
    strap = chart.z_sh + math.radians(30) * chart.k
    return RC._sym_interp(th_deg, [0, 30, 50, 66, 80, 96, 106, 122, 140, 180],
                          [neck, neck, strap, strap - 0.02 * S, arm, arm, strap - 0.02 * S, strap, neck, neck])


def robe_top(lm, chart: TorsoChart, th_deg: np.ndarray, drop: float) -> np.ndarray:
    """The over-robe's round neckline, under the ivory collar, and its deep armholes."""
    S = lm.S
    neck_f = float(lm.P("notch")[2] - 0.035 * S)
    neck = chart.z_sh + math.radians(46) * chart.k
    arm = float(lm.P("shoulder")[2] - drop * S)
    strap = chart.z_sh + math.radians(22) * chart.k
    return RC._sym_interp(th_deg, [0, 20, 38, 56, 76, 92, 108, 128, 150, 180],
                          [neck_f, neck_f + 0.01 * S, neck - 0.01 * S, strap, arm, arm, strap, neck, neck, neck])


def gusset(fields: Fields, chart: TorsoChart, side: str, drop: float) -> Part:
    """The under-robe's gusset (act1_npcs.md §1.4 #1) under one arm: a small panel of ivory silk on the side of the
    torso between the armhole's bottom and the shoulder joint, cast on the torso alone (inside the arm's volume at
    rest, under the sleeve), so it rides the torso and fills the armhole when the arm comes up."""
    lm = fields.lm
    S = lm.S
    part = Part(f"Gusset{side}")
    part._mat = "cloth"
    a0, a1 = GUSSET_AZIMUTH
    th_deg = np.linspace(a0, a1, GUSSET_COLS) if side == "L" else np.linspace(360.0 - a1, 360.0 - a0, GUSSET_COLS)
    th = np.radians(th_deg)
    z_top = float(lm.P("shoulder")[2]) - GUSSET_BELOW_JOINT * S
    z_bot = float(lm.P("shoulder")[2]) - (drop + GUSSET_OVERLAP) * S
    torso = fields.body.regions["torso"]
    P = np.zeros((GUSSET_ROWS, len(th), 3))
    for j in range(GUSSET_ROWS):
        z = z_top + (z_bot - z_top) * j / (GUSSET_ROWS - 1)
        O, D = chart.rays(th, np.full(len(th), z))
        r = cast_last(lambda Q: torso.sdf(Q) - UNDER_OFF * S, O, D, 0.4 * S)
        P[j] = O + D * r[:, None]
    _panel(part, P, ATLAS[f"gusset_{side}"], None, False, 0.0012 * S, np.array([0.0, chart.y_axis, 0.0]))
    return part


# ---------------------------------------------------------------------------------------------
# The robe skirt: four leg-following panels
# ---------------------------------------------------------------------------------------------
def split_heights(lm, params: dict) -> dict:
    """Seam azimuth -> the height of its split's top (above it the two panels are one welded seam)."""
    S = lm.S
    z_hip = float(lm.side_pt("hip", "L")[2])
    z_knee = float(lm.side_pt("knee", "L")[2])
    mid_thigh = 0.5 * (z_hip + z_knee)
    side = z_hip - float(params["robe_side_split_below_hip_m"]) * S
    return {0.0: mid_thigh, 90.0: side, 180.0: mid_thigh, 270.0: side}


def _skirt_radius(fields: Fields, th: np.ndarray, z: float, off: float) -> np.ndarray:
    S = fields.lm.S
    O = np.stack([np.zeros(len(th)), np.full(len(th), 0.01 * S), np.full(len(th), z)], axis=-1)
    return cast_last(lambda Q: fields.lower(Q) - off, O, dir_theta(th), 0.5 * S)


def robe_panels(fields: Fields, params: dict, z_top: float, seed: int) -> dict[str, Part]:
    """The four panels. Each Part carries `grid_P` (rows top -> hem, columns from its start azimuth), `seam_z`
    (the split tops at its start and end edges) and `leg`."""
    lm = fields.lm
    S = lm.S
    rng = np.random.default_rng(seed)
    phase = float(rng.uniform(0.0, 2 * math.pi))
    z_hem = float(params["robe_hem_m"])
    splits = split_heights(lm, params)
    zs = np.array([z_top + (z_hem - z_top) * (j / (PANEL_ROWS - 1)) for j in range(PANEL_ROWS)])
    grids = {}
    lap_cols = {}
    for name, a0, a1, leg in PANELS:
        s0, s1 = splits[a0 % 360.0], splits[a1 % 360.0]
        over0, over1 = LAPS_OVER[a0 % 360.0] == name, LAPS_OVER[a1 % 360.0] == name
        P = np.zeros((PANEL_ROWS, PANEL_COLS, 3))
        prev_r = None
        lifts = np.zeros((PANEL_ROWS, PANEL_COLS))
        for j, z in enumerate(zs):
            lap0 = LAP_DEG * smooth01((s0 - z) / (LAP_RAMP * S)) if over0 else 0.0
            lap1 = LAP_DEG * smooth01((s1 - z) / (LAP_RAMP * S)) if over1 else 0.0
            th_deg = np.linspace(a0 - lap0, a1 + lap1, PANEL_COLS)
            th = np.radians(th_deg)
            t = j / (PANEL_ROWS - 1)
            off = (SKIRT_OFF_TOP + (SKIRT_OFF - SKIRT_OFF_TOP) * smooth01((z_top - z) / (SKIRT_OFF_RAMP * S))) * S
            r = _skirt_radius(fields, th, z, off)
            if prev_r is not None:
                r = np.maximum(r, prev_r + SKIRT_FLARE * (zs[j - 1] - z))
            prev_r = r
            rr = r + SKIRT_FOLD_AMP * S * t ** 1.1 * (np.sin(SKIRT_FOLDS * th + phase)
                                                     + SKIRT_FOLD_2ND[1] * np.sin(SKIRT_FOLD_2ND[0] * SKIRT_FOLDS * th
                                                                                   + 1.7 * phase))
            ramp = np.zeros(PANEL_COLS)
            if lap0 > 0.0:
                ramp = np.maximum(ramp, smooth01(1.0 - np.arange(PANEL_COLS) / LAP_EDGE_COLS) * lap0 / LAP_DEG)
            if lap1 > 0.0:
                ramp = np.maximum(ramp, smooth01(1.0 - np.arange(PANEL_COLS)[::-1] / LAP_EDGE_COLS) * lap1 / LAP_DEG)
            lifts[j] = LAP_LIFT * S * ramp
            O = np.stack([np.zeros(PANEL_COLS), np.full(PANEL_COLS, 0.01 * S), np.full(PANEL_COLS, z)], axis=-1)
            P[j] = O + dir_theta(th) * (rr + lifts[j])[:, None]
        grids[name] = P
        lap_cols[name] = (s0, s1, leg)
    # above a split the two panels share the seam column exactly (one welded seam)
    for seam, zsplit in splits.items():
        over = LAPS_OVER[seam]
        under = next(n for n, a0, a1, _l in PANELS if n != over and seam in (a0 % 360.0, a1 % 360.0))
        o_col = 0 if next(a0 for n, a0, _a1, _l in PANELS if n == over) % 360.0 == seam else -1
        u_col = 0 if next(a0 for n, a0, _a1, _l in PANELS if n == under) % 360.0 == seam else -1
        above = zs >= zsplit - 1e-9
        grids[under][above, u_col] = grids[over][above, o_col]
    out = {}
    for name, a0, a1, leg in PANELS:
        part = Part(f"Panel{name}")
        part._mat = "cloth"
        P = grids[name]
        _panel(part, P, ATLAS[f"panel_{name}"], _wind_rows(PANEL_ROWS, PANEL_COLS, 0.10, 0.3 * a0 / 90.0), False,
               0.0015 * S, np.array([0.0, 0.01 * S, 0.0]))
        part.grid_P = P
        part.seam_z = lap_cols[name][:2]
        part.leg = leg
        out[name] = part
    return out


# ---------------------------------------------------------------------------------------------
# The half-mantle (right shoulder)
# ---------------------------------------------------------------------------------------------
def shell_guide(lm, side: str, neck_to: float, end_m: float, n: int) -> tuple[np.ndarray, float]:
    """A guide curve (inside the body) from the side of the neck over the shoulder joint and `end_m` down the upper
    arm, and the t of the shoulder joint on it."""
    S = lm.S
    sgn = 1.0 if side == "L" else -1.0
    sh, el = lm.side_pt("shoulder", side), lm.side_pt("elbow", side)
    nb = lm.P("neck_base")
    medial = np.array([sgn * neck_to * S, float(nb[1]) + 0.01 * S, float(sh[2]) + 0.035 * S])
    mid = np.array([0.5 * (medial[0] + sh[0]), medial[1], float(sh[2]) + 0.025 * S])
    ax = (el - sh) / float(np.linalg.norm(el - sh))
    a = sh + ax * end_m
    C = catmull_rom(np.array([medial, mid, sh, 0.5 * (sh + a), a]), n)
    t_sh = float(np.argmin(np.linalg.norm(C - sh, axis=1)) / (n - 1))
    return C, t_sh


def shoulder_shell(fields: Fields, side: str, neck_to: float, end_m: float, lims_deg: tuple, off: float,
                   n_rows: int, n_cols: int, smooth_passes: int = 6) -> tuple[np.ndarray, np.ndarray, float]:
    """A smooth shell over one shoulder on its own chart G[row (neck -> arm), col (front -> back)]: slices across the
    guide curve, each a fan of rays cast onto the body field (upper body and that arm) plus `off`. The fan's
    half-angle runs through lims_deg = (at the neck, at the shoulder joint, at the arm end), so the front and back
    edges are smooth curves. Returns (G, outward normals, t of the shoulder joint)."""
    lm = fields.lm
    S = lm.S
    C, t_sh = shell_guide(lm, side, neck_to, end_m, n_rows)
    T = np.gradient(C, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    up = np.array([0.0, 0.0, 1.0])
    arm = fields.body.regions[f"arm_{side}"]
    fn = lambda Q: np.minimum(fields.upper(Q), arm.sdf(Q)) - off  # noqa: E731
    rows = []
    a, b, c = lims_deg
    for j in range(n_rows):
        t = j / (n_rows - 1)
        n1 = up - (up @ T[j]) * T[j]
        n1 /= np.linalg.norm(n1)
        n2 = np.cross(T[j], n1)
        if n2[1] < 0:  # columns run front (-Y) -> back (+Y) on both sides
            n2 = -n2
        if t <= t_sh:
            lim = a + (b - a) * smooth01(t / max(t_sh, 1e-6))
        else:
            lim = b + (c - b) * smooth01((t - t_sh) / max(1.0 - t_sh, 1e-6))
        phi = np.linspace(-math.radians(lim), math.radians(lim), MANTLE_FAN)
        D = np.cos(phi)[:, None] * n1[None, :] + np.sin(phi)[:, None] * n2[None, :]
        O = np.repeat(C[j][None, :], MANTLE_FAN, axis=0)
        r = cast_last(fn, O, D, 0.45 * S)
        rows.append(_resample(O + D * r[:, None], n_cols))
    G = np.stack(rows)
    centre = C.mean(axis=0) - np.array([0.0, 0.0, 0.1 * S])
    for _ in range(2):
        G = _laplace(G, smooth_passes, keep_edges=False)
        # the clearance pass (as toma_costume.pauldron): lift wherever the smoothed shell came inside the offset
        N = _grid_normals(G, centre)
        for _ in range(4):
            dfc = np.maximum(-fn(G.reshape(-1, 3)).reshape(G.shape[:2]), 0.0)
            for _ in range(6):
                pad = np.pad(dfc, 1, mode="edge")
                dfc = np.maximum(dfc, (pad[:-2, 1:-1] + pad[2:, 1:-1] + pad[1:-1, :-2] + pad[1:-1, 2:]) * 0.25 * 0.9)
            G = G + N * dfc[..., None]
    return G, _grid_normals(G, centre), t_sh


def _resample(P: np.ndarray, n: int) -> np.ndarray:
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    st = np.linspace(0.0, s[-1], n)
    return np.stack([np.interp(st, s, P[:, k]) for k in range(3)], axis=1)


def _laplace(P: np.ndarray, passes: int, keep_edges: bool = True) -> np.ndarray:
    P = P.copy()
    for _ in range(passes):
        Q = P.copy()
        Q[1:-1, 1:-1] = 0.5 * P[1:-1, 1:-1] + 0.125 * (P[:-2, 1:-1] + P[2:, 1:-1] + P[1:-1, :-2] + P[1:-1, 2:])
        if not keep_edges:  # the edge rows and columns smooth along themselves only
            Q[0, 1:-1] = 0.5 * P[0, 1:-1] + 0.25 * (P[0, :-2] + P[0, 2:])
            Q[-1, 1:-1] = 0.5 * P[-1, 1:-1] + 0.25 * (P[-1, :-2] + P[-1, 2:])
            Q[1:-1, 0] = 0.5 * P[1:-1, 0] + 0.25 * (P[:-2, 0] + P[2:, 0])
            Q[1:-1, -1] = 0.5 * P[1:-1, -1] + 0.25 * (P[:-2, -1] + P[2:, -1])
        P = Q
    return P


def mantle(fields: Fields, params: dict) -> tuple[Part, dict]:
    """The half-mantle as a closed plate; returns (part, info): info holds the chart (outer grid), the t of the
    shoulder joint and the hinge bone's head and tail."""
    lm = fields.lm
    S = lm.S
    clear = float(params["mantle_clearance_m"]) * S
    thick = float(params["mantle_thickness_m"]) * S
    flare = float(params["mantle_flare_m"]) * S
    sh, el = lm.side_pt("shoulder", "R"), lm.side_pt("elbow", "R")
    end_m = float(np.linalg.norm(el - sh)) - float(params["mantle_above_elbow_m"]) * S
    G, N, t_sh = shoulder_shell(fields, "R", float(params["mantle_neck_to_m"]), end_m, MANTLE_LIMS, clear + thick,
                                MANTLE_ROWS, MANTLE_COLS, MANTLE_SMOOTH)
    # the flare: the edge over the arm (the last rows) and the arm-side front and back edges stand off the arm
    tt = np.linspace(0.0, 1.0, MANTLE_ROWS)
    arm_w = smooth01((tt - 0.72) / 0.28)
    side = np.abs(np.linspace(-1.0, 1.0, MANTLE_COLS))
    edge_w = smooth01((side - 0.7) / 0.3)
    w = np.maximum(arm_w[:, None] * np.ones(MANTLE_COLS)[None, :],
                   edge_w[None, :] * smooth01((tt - t_sh) / max(1.0 - t_sh, 1e-6))[:, None])
    G = G + N * (flare * w ** 1.6)[..., None]
    part = Part("Mantle")
    _plate(part, G, N, thick, ATLAS["mantle"], ATLAS["mantle_inner"], ATLAS["mantle_edge"], 2)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    mid = MANTLE_COLS // 2
    hinge = (G[0, mid] - N[0, mid] * (clear + thick), lm.side_pt("acromion", "R"))
    return part, {"grid": G, "normals": N, "t_sh": t_sh, "hinge": hinge, "rows": MANTLE_ROWS, "cols": MANTLE_COLS}


def yoke(fields: Fields, side: str) -> Part:
    """The over-robe's dropped-shoulder yoke: a shell of the robe's blue over the top of the shoulder, from its
    neckline to past the shoulder joint, lapping over the robe's top edge and the sleeve's top."""
    lm = fields.lm
    S = lm.S
    G, _N, _t = shoulder_shell(fields, side, YOKE_NECK_TO, YOKE_END * S, YOKE_LIMS, YOKE_OFF * S, YOKE_ROWS,
                               YOKE_COLS, 4)
    part = Part(f"Yoke{side}")
    part._mat = "cloth"
    u0, v0, u1, v1 = ATLAS[f"yoke_{side}"]
    nj, ni = G.shape[:2]
    _shell(part, G, lambda j, i: (u0 + (u1 - u0) * i / (ni - 1), v0 + (v1 - v0) * j / (nj - 1)), False,
           lm.side_pt("shoulder", side) - np.array([0.0, 0.0, 0.08 * S]), 0.0015 * S)
    part.grid_P = G
    return part


HAIR_BODY_OFF = 0.024  # m (x S): the fall lies this far off the body field (over the robe and its yoke) ...
HAIR_MANTLE_OFF = 0.004  # ... and this far off the mantle's outer face (plus the fall's own clearance)


def make_avoid(fields: Fields, minfo: dict):
    """avoid(P): signed clearance (m) from what the hair falls over: the body field under its clothes and the
    half-mantle's outer face (signed by the mantle's outward normal near it)."""
    S = fields.lm.S
    G = minfo["grid"].reshape(-1, 3)
    N = minfo["normals"].reshape(-1, 3)
    arm_l, arm_r = fields.body.regions["arm_L"], fields.body.regions["arm_R"]

    def avoid(P: np.ndarray) -> np.ndarray:
        P = np.atleast_2d(P)
        d = np.minimum(fields.upper(P), np.minimum(arm_l.sdf(P), arm_r.sdf(P))) - HAIR_BODY_OFF * S
        k = np.zeros(len(P), dtype=int)
        dist = np.zeros(len(P))
        for a in range(0, len(P), 256):
            q = P[a:a + 256]
            d2 = ((q[:, None, :] - G[None, :, :]) ** 2).sum(axis=2)
            k[a:a + 256] = np.argmin(d2, axis=1)
            dist[a:a + 256] = np.sqrt(d2[np.arange(len(q)), k[a:a + 256]])
        sd = np.sum((P - G[k]) * N[k], axis=1) - HAIR_MANTLE_OFF * S
        sd = np.where(dist < 0.06 * S, sd, 1.0)
        return np.minimum(d, sd)

    return avoid


def mantle_row_t(part: Part, info: dict) -> np.ndarray:
    """Per mantle vertex, the guide parameter t (0 neck .. 1 arm) of its nearest outer-grid row."""
    G = info["grid"]
    P = part.varr()
    flat = G.reshape(-1, 3)
    out = np.zeros(len(P))
    for a in range(0, len(P), 512):
        q = P[a:a + 512]
        k = np.argmin(((q[:, None, :] - flat[None, :, :]) ** 2).sum(axis=2), axis=1)
        out[a:a + 512] = (k // G.shape[1]) / (G.shape[0] - 1)
    return out


# ---------------------------------------------------------------------------------------------
# Slippers
# ---------------------------------------------------------------------------------------------
def slipper(fields: Fields, side: str, rect) -> Part:
    """A closed thin-soled slipper: horizontal slices of the foot field, offset, lofted, with a flat sole fan."""
    part = Part(f"Slipper{side}")
    part._mat = "cloth"
    lm = fields.lm
    S = lm.S
    hb, tt = lm.side_pt("heel_back", side), lm.side_pt("toe_tip", side)
    an = lm.side_pt("ankle", side)
    fwd = (tt - hb) / np.linalg.norm(tt - hb)
    fwd[2] = 0.0
    fwd /= np.linalg.norm(fwd)
    lat = np.cross(fwd, np.array([0.0, 0.0, 1.0]))
    fn = lambda Q: np.minimum(fields.region(f"foot_{side}")(Q), fields.region(f"leg_{side}")(Q)) - SLIPPER_OFF * S  # noqa: E731
    a = 2 * math.pi * np.arange(SLIPPER_N) / SLIPPER_N
    D = np.cos(a)[:, None] * fwd[None, :] + np.sin(a)[:, None] * lat[None, :]
    z_top = float(an[2]) + SLIPPER_TOP_ABOVE_ANKLE * S
    heights = [h * S for h in SLIPPER_ROWS if h * S < z_top] + [z_top]
    heights = heights[::-1]  # row 0 = the collar
    rows = []
    c_mid = (hb + tt) * 0.5
    for z in heights:
        w = smooth01((z - 0.03 * S) / (z_top - 0.03 * S))
        c = c_mid + (an - c_mid) * w
        O = np.repeat(np.array([[c[0], c[1], max(z, 0.003 * S)]]), SLIPPER_N, axis=0)
        r = cast_last(fn, O, D, 0.2 * S)
        r = np.maximum(r, 0.02 * S)
        P = O + D * r[:, None]
        P[:, 2] = max(z, -0.002)
        rows.append(P)
    R = np.stack(rows)
    R[-1, :, 2] = -0.002  # the sole's edge sits just under the floor
    ids = _panel(part, R, rect, [[(0.0, 0.0, 0.0, 0.0)] * SLIPPER_N] * len(R), True, 0.0012 * S,
                 np.array([c_mid[0], c_mid[1], 0.0]))
    cb = part.add_v(np.array([c_mid[0], c_mid[1], -0.002]), color=(0.0, 0.0, 0.0, 0.0), tag=TAG_CLOTH)
    bot = ids[-1]
    u0, v0, u1, v1 = rect
    for i in range(SLIPPER_N):
        i2 = (i + 1) % SLIPPER_N
        tri = (cb, int(bot[i]), int(bot[i2]))
        p0, p1, p2 = (part.V[k] for k in tri)
        if np.cross(p1 - p0, p2 - p0)[2] > 0:  # the sole faces down
            tri = (tri[0], tri[2], tri[1])
        part.add_f(tri, [(u0 + 0.01, v1 - 0.01)] * 3, "cloth")
    return part


# ---------------------------------------------------------------------------------------------
def build_costume(body, params: dict) -> tuple[dict[str, Part], dict]:
    """Returns ({name: Part}, anchors). The mantle is its own entry ("Mantle"), a separate glTF object."""
    lm = body.lm
    S = lm.S
    fields = Fields(body)
    chart = TorsoChart(lm)
    z_waist = float(lm.P("waist")[2])
    z_crotch = float(lm.P("crotch")[2])
    out: dict[str, Part] = {}
    # 1. under-robe: torso, high collar, sleeves
    th_u = np.linspace(0.0, 360.0, 44, endpoint=False)
    out["Underrobe"] = RC.torso_sheet(fields, chart, "Underrobe", ATLAS["underrobe"], th_u,
                                      underrobe_top(lm, chart, th_u, float(params["underrobe_armhole_drop_m"])),
                                      z_waist - UNDER_HEM_BELOW_WAIST * S, UNDER_OFF * S, 10, 0.0015 * S, True)
    out["Collar"] = collar(fields, ATLAS["collar"], float(params["collar_height_m"]) * S, n=40)
    for sd in ("L", "R"):
        out[f"Gusset{sd}"] = gusset(fields, chart, sd, float(params["underrobe_armhole_drop_m"]))
    for sd in ("L", "R"):
        path = RC.arm_path(lm, sd, 0.02, float(params["sleeve_end"]), 14)
        out[f"Sleeve{sd}"] = RC.limb_tube(fields, f"arm_{sd}", path,
                                          lambda t: (0.010 - 0.003 * t) * S if t > 0.08 else 0.012 * S,
                                          ATLAS[f"sleeve_{sd}"], f"Sleeve{sd}", n_around=20, rows=14,
                                          back_inset=0.0018 * S, wind_amp=0.05, min_r=0.033 * S)
    # 2. trousers: a pelvis band and two loose legs to just above the ankle (hidden under the robe but at the splits)
    th_t = np.linspace(0.0, 360.0, 36, endpoint=False)
    pelvis = Part("TrouserTop")
    pelvis._mat = "cloth"
    n_r = 6
    P = np.zeros((n_r, len(th_t), 3))
    D = dir_theta(np.radians(th_t))
    for j in range(n_r):
        z = z_waist - 0.01 * S + (z_crotch + 0.015 * S - z_waist + 0.01 * S) * j / (n_r - 1)
        O = np.stack([np.zeros(len(th_t)), np.full(len(th_t), 0.01 * S), np.full(len(th_t), z)], axis=-1)
        r = cast_last(lambda Q: fields.lower(Q) - TROUSER_OFF * S, O, D, 0.5 * S)
        P[j] = O + D * r[:, None]
    _panel(pelvis, P, ATLAS["trousers"], None, True, None, np.array([0.0, 0.01 * S, 0.0]))
    out["TrouserTop"] = pelvis
    an_z = float(lm.side_pt("ankle", "L")[2])
    hem_z = an_z + float(params["trouser_hem_above_ankle_m"]) * S
    for sd in ("L", "R"):
        path = RC.leg_path(lm, sd, z_crotch + 0.06 * S, hem_z, 12)
        out[f"TrouserLeg{sd}"] = RC.limb_tube(
            fields, f"leg_{sd}", path, lambda t: (0.009 + 0.010 * math.sin(math.pi * min(t * 1.1, 1.0)) ** 1.2) * S,
            ATLAS[f"trouser_leg_{sd}"], f"TrouserLeg{sd}", n_around=18, rows=12, back_inset=0.0015 * S,
            wind_amp=0.05)
    # 3. slippers
    sl = Part("Slippers")
    for sd in ("L", "R"):
        sl.extend(slipper(fields, sd, ATLAS["slippers"]))
    out["Slippers"] = sl
    # 4. the over-robe: torso to the hips, then the four panels from the waist seam
    th_r = np.linspace(0.0, 360.0, 48, endpoint=False)
    out["Robe"] = RC.torso_sheet(fields, chart, "Robe", ATLAS["robe"], th_r,
                                 robe_top(lm, chart, th_r, float(params["robe_armhole_drop_m"])),
                                 z_waist - ROBE_HEM_BELOW_WAIST * S, ROBE_OFF * S, 12, 0.0018 * S, True,
                                 wind_amp=0.04)
    panels = robe_panels(fields, params, z_waist + ROBE_TOP_ABOVE_WAIST * S, int(params["seed"]))
    for name, p in panels.items():
        out[f"Panel{name}"] = p
    for sd in ("L", "R"):
        out[f"Yoke{sd}"] = yoke(fields, sd)
    # 5. the half-mantle
    out["Mantle"], minfo = mantle(fields, params)
    for p in out.values():
        if not p.C:
            p.C = [(0.0, 0.0, 0.0, 0.0)] * len(p.V)
        elif len(p.C) < len(p.V):
            p.C = p.C + [(0.0, 0.0, 0.0, 0.0)] * (len(p.V) - len(p.C))
    anchors = {"mantle": minfo, "panels": panels, "z_top": z_waist + ROBE_TOP_ABOVE_WAIST * S,
               "splits": split_heights(lm, params)}
    return out, anchors


SHOULDER_CAP = 0.10  # m (x S): torso skin this close to a shoulder joint is under the yoke and the sleeve's top


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
    under = torso & (H < underrobe_top(lm, chart, th_deg, float(params["underrobe_armhole_drop_m"])) - m)
    sleeves = np.zeros(len(V), dtype=bool)
    end = float(params["sleeve_end"])
    for sd in ("L", "R"):
        sh, el, wr = lm.side_pt("shoulder", sd), lm.side_pt("elbow", sd), lm.side_pt("wrist", sd)
        # the arm's chart parameter as RC.arm_path lays it: shoulder 0, elbow 0.5, wrist 1
        a1, a2 = el - sh, wr - el
        t1 = np.clip((V - sh) @ a1 / (a1 @ a1), 0.0, 1.0) * 0.5
        t2 = 0.5 + np.clip((V - el) @ a2 / (a2 @ a2), 0.0, 1.0) * 0.5
        t = np.where((V - el) @ a2 > 0, t2, t1)
        # the whole arm under the sleeve (its top sits under the yoke), and the torso round the shoulder joint, which
        # the yoke and the sleeve's top cover (kept, it passed through the cloth as the arm came down)
        sleeves |= (reg == f"arm_{sd}") & (t < end - 0.04)
        sleeves |= torso & (np.linalg.norm(V - sh, axis=1) < SHOULDER_CAP * S)
    # under the gussets
    a = np.abs(((th_deg + 180.0) % 360.0) - 180.0)
    z_top = float(lm.P("shoulder")[2]) - GUSSET_BELOW_JOINT * S
    z_bot = float(lm.P("shoulder")[2]) - (float(params["underrobe_armhole_drop_m"]) + GUSSET_OVERLAP) * S
    sleeves |= torso & (a > GUSSET_AZIMUTH[0] + 4.0) & (a < GUSSET_AZIMUTH[1] - 4.0) & (V[:, 2] < z_top - 0.01 * S) & (
        V[:, 2] > z_bot + 0.01 * S)
    legs = (reg == "leg_L") | (reg == "leg_R") | torso
    an_z = float(lm.side_pt("ankle", "L")[2])
    hem_z = an_z + float(params["trouser_hem_above_ankle_m"]) * S
    trousers = legs & (V[:, 2] < z_waist - m * 0.5) & (V[:, 2] > hem_z + 0.005 * S)
    feet = ((reg == "foot_L") | (reg == "foot_R") | (reg == "leg_L") | (reg == "leg_R")) & (
        V[:, 2] < an_z + (SLIPPER_TOP_ABOVE_ANKLE - 0.012) * S)
    return under | sleeves | trousers | feet
