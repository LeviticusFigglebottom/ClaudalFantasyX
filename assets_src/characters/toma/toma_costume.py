"""Toma's costume as procedural cloth panels and shell plates (no bpy), toma.md §3-§4 and §9.

Same method as Asha's and Rhen's (asha_costume, rhen_costume): every garment is a pattern grid whose
rows are ray-cast onto the body field plus a fitting offset, and the grid is also the garment's
island in the 2K costume atlas (toma_textures paints the same charts). Pieces, inner to outer:

1. Under-tunic (undyed bone cotton), sleeveless, a shallow wrap V at the neck: a closed body to just
   under the sash, then a hip-length skirt that is open at his right side (the slit).
2. Wrapped trousers (faded indigo) to mid-shin, gathered into shin-to-ankle wraps.
3. The indigo sash, 18 cm wide, wrapped three times (three overlapping bands), the knot at the left
   front and two tails to the knee.
4. The leather harness and pauldron strap (5 cm) over the left shoulder, across the chest and under
   the right arm, with bronze buckles.
5. **The pauldron** (toma.md §3, §9): five layered shell lames on the LEFT shoulder, each a curved
   plate 6 mm thick with closed edges, the top lame the largest (32 x 26 cm). The top lame carries
   the **chiselled scar**: `scar_depth` is a field of 40-60 radial, uneven wedge strokes inside a
   ragged circle (11 cm), cut through the red lacquer and its black under-layer into the pale shell.
   The same field displaces the plate (here) and paints the strata (toma_textures, by depth: red ->
   black -> bone), so the layers agree. It is random hand-work by construction: there is no emblem
   in the data, only strokes, and nothing of any shape survives inside the circle (the floor of the
   cut is below the lacquer everywhere inside it).
6. Leather sandals with a reinforced sole: a two-tier sole (outsole and a stitched welt, higher at the
   heel), a heel counter, instep and ankle straps (`reinforced_sandal`, M2-CHR-04).

The lame geometry is a function of toma_params.json only (an ellipsoid shell placed at the left
shoulder joint), so toma_textures can rebuild the scar's chart without the body. Vertex colour =
wind (R primary, G ripple, B phase, A flutter). `coverage()` says which body vertices are hidden
under clothing (deleted, asha.md §8.1). Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

import rhen_costume as RC
from asha_costume import TAG_CLOTH, Fields, TorsoChart, _panel, cast_last, dir_theta, limb_wrap
from asha_mesh import Part, catmull_rom, grid, tube, uv_sphere

# costume atlas islands (u0, v0, u1, v1), the shader's UV convention (v down); toma_textures paints them
ATLAS = {
    "tunic": (0.0, 0.0, 0.5, 0.30),
    "skirt": (0.0, 0.30, 0.5, 0.48),
    "trousers": (0.0, 0.48, 0.5, 0.58),
    "trouser_leg_L": (0.0, 0.58, 0.25, 0.76),
    "trouser_leg_R": (0.25, 0.58, 0.5, 0.76),
    "spear_shaft": (0.0, 0.76, 0.5, 0.80),
    "grip": (0.0, 0.80, 0.25, 0.86),
    "sash": (0.5, 0.0, 1.0, 0.10),
    "sash_tails": (0.5, 0.10, 0.75, 0.30),
    "harness": (0.75, 0.10, 1.0, 0.16),
    "lame_edge": (0.75, 0.16, 1.0, 0.20),
    "lame_back": (0.75, 0.20, 1.0, 0.24),
    "top_edge": (0.75, 0.24, 1.0, 0.27),
    "wraps": (0.5, 0.30, 0.75, 0.48),
    "sandals": (0.75, 0.30, 1.0, 0.42),
    "pauldron_top": (0.5, 0.48, 0.80, 0.78),
    "pauldron_lames": (0.80, 0.48, 1.0, 0.78),
}
TUNIC_OFF = 0.0045  # m, the under-tunic over the skin
SKIRT_OFF = 0.012
SASH_OFF = 0.006  # each wrap over the one under it
HARNESS_OFF = 0.012  # over the tunic
TROUSER_OFF = 0.009
SHIN_WRAP_OFF = 0.0125  # over the trousers' gathered hem
# --- the pauldron (toma.md §3, §9). All lengths in metres (Toma's own size; no body scale) -------
SHELL_RADII = (0.218, 0.170, 0.140)  # ellipsoid (lateral X, front-back Y, up Z) about the shoulder joint
SHELL_TILT_OUT = 0.38  # rad about the front axis: the shell's top leans out over the deltoid
SHELL_TURN_FWD = 0.30  # rad about the vertical: its lateral side turns toward the front
SHELL_E_TOP = -0.25  # rad: the top lame's medial edge, measured from straight up toward his left
LAME_E_CENTRES = (1.36, 1.48, 1.60, 1.72)  # rad, lames 2-5 (before the shell tilt)
LAME_E_HALF = 0.10  # rad, half-height of lames 2-5 (they overlap: centres 0.12 apart)
LAME_W_HALF = (0.98, 0.90, 0.82, 0.74)  # rad, front-back half-sweep of lames 2-5
LAME_SHRINK = 0.036  # each lower lame tucks under the one above it (radius x (1 - k * this))
LAME_FLARE = 0.035  # the lower edge of each lame flares out by this share of the radius
TOP_GRID = (40, 32)  # top lame columns (front-back) x rows (medial-lateral): fine enough for the scar
LAME_GRID = (24, 7)
TOP_TUCK = 0.45
SCAR_ST = (0.30, 0.68)  # the scar's centre on the top lame chart (s front 0 -> back 1, t medial 0 -> lateral 1)
LACQUER_RED_M = 0.0006  # strata: red lacquer, then the black under-layer, then the pale shell
LACQUER_BLACK_M = 0.0003
SCAR_FLOOR_M = 0.0011  # the cut's floor inside the circle: always through both lacquer layers
SCAR_RIM_NOISE = 0.26  # of the radius: the ragged, chipped edge
SCAR_OVERSHOOT = 0.006  # m: how far a stroke may chip past the rim
SCAR_CHIP = 0.14  # of the radius: the small chips along the rim
CLEARANCE = 0.022  # m between the lames and the body field
HARNESS_PATH = [(58.0, 48.0), (22.0, "nip+0.03"), (-25.0, "nip-0.03"), (-62.0, "nip-0.07"), (-100.0, "nip-0.07"),
                (-140.0, "nip-0.04"), (-180.0, "nip+0.00"), (-232.0, "zs-0.05"), (-262.0, 40.0)]


def _wind_rows(n_rows: int, n_cols: int, amp: float, phase0: float = 0.0):
    return [[(amp * t * t, amp * t, (phase0 + i / n_cols * 3.0) % 1.0, 0.3 * amp * t) for i in range(n_cols)]
            for t in np.linspace(0.0, 1.0, n_rows)]


# ---------------------------------------------------------------------------------------------
# The pauldron's shell (body-independent; toma_textures rebuilds the scar chart from it)
# ---------------------------------------------------------------------------------------------
def shell_dir(e: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Unit directions: e from straight up (0) toward his left (+X, pi/2) and on down the arm; w the
    sweep toward the front (-Y, +) or the back (-)."""
    e, w = np.broadcast_arrays(np.asarray(e, float), np.asarray(w, float))
    return np.stack([np.cos(w) * np.sin(e), -np.sin(w), np.cos(w) * np.cos(e)], axis=-1)


def shell_point(e, w, scale: float = 1.0) -> np.ndarray:
    """A point on the shell (about its centre): the ellipsoid, then tilted out over the deltoid and
    turned a little to the front, so the top lame (and the scar on it) faces the hero three-quarter
    camera instead of the sky."""
    d = shell_dir(e, w)
    rx, ry, rz = SHELL_RADII
    r = 1.0 / np.sqrt((d[..., 0] / rx) ** 2 + (d[..., 1] / ry) ** 2 + (d[..., 2] / rz) ** 2)
    p = d * (r * scale)[..., None]
    a, b = SHELL_TILT_OUT, SHELL_TURN_FWD
    x = p[..., 0] * np.cos(a) + p[..., 2] * np.sin(a)
    z = -p[..., 0] * np.sin(a) + p[..., 2] * np.cos(a)
    y = p[..., 1]
    return np.stack([x * np.cos(b) + y * np.sin(b), -x * np.sin(b) + y * np.cos(b), z], axis=-1)


def _arc(fn, a: float, b: float, n: int = 400) -> np.ndarray:
    """Cumulative arc length of the curve fn(x) for x in linspace(a, b, n)."""
    x = np.linspace(a, b, n)
    P = fn(x)
    return x, np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])


def top_lame_ranges(params: dict) -> tuple[tuple[float, float], tuple[float, float]]:
    """(e0, e1), (w0, w1) of the top lame so it measures pauldron_top_m (front-back x medial-lateral)."""
    L_fb, L_ml = (float(x) for x in params["pauldron_top_m"])
    x, s = _arc(lambda e: shell_point(e, np.zeros_like(e)), SHELL_E_TOP, SHELL_E_TOP + 2.5)
    e1 = float(np.interp(L_ml, s, x))
    e_mid = 0.5 * (SHELL_E_TOP + e1)
    x, s = _arc(lambda w: shell_point(np.full_like(w, e_mid), w), 0.0, 1.5)
    wh = float(np.interp(0.5 * L_fb, s, x))
    return (SHELL_E_TOP, e1), (wh, -wh)  # s = 0 at the front edge


def top_lame_point(params: dict, s, t) -> np.ndarray:
    (e0, e1), (w0, w1) = top_lame_ranges(params)
    s, t = np.broadcast_arrays(np.asarray(s, float), np.asarray(t, float))
    # the outer edge (t -> 1) flares a little, like the lower lames
    flare = 1.0 + 0.5 * LAME_FLARE * np.clip((t - 0.7) / 0.3, 0.0, 1.0) ** 2
    # the medial edge tucks down onto the trapezius (the body clearance pass keeps it off the skin)
    tuck = 1.0 - TOP_TUCK * np.clip(1.0 - t / 0.35, 0.0, 1.0) ** 2
    return shell_point(e0 + (e1 - e0) * t, w0 + (w1 - w0) * s, flare * tuck)


def scar_frame(params: dict) -> tuple[np.ndarray, float, float]:
    """The scar centre on the top lame (local, about the shell centre) and the chart's metric scale
    there: metres per unit s and per unit t."""
    s0, t0 = SCAR_ST
    e = 1e-3
    c = top_lame_point(params, s0, t0)
    Ls = float(np.linalg.norm(top_lame_point(params, s0 + e, t0) - top_lame_point(params, s0 - e, t0)) / (2 * e))
    Lt = float(np.linalg.norm(top_lame_point(params, s0, t0 + e) - top_lame_point(params, s0, t0 - e)) / (2 * e))
    return c, Ls, Lt


def scar_strokes(params: dict) -> np.ndarray:
    """The chisel strokes: rows of (x, y, angle, length, width, depth) in metres on the scar's local
    tangent chart. Radial (the angle follows the direction from the centre, give or take 25 degrees),
    uneven in length, width and depth, scattered all over the circle and past its rim."""
    rng = np.random.default_rng([int(params["seed"]), 7])
    n = int(params["scar_strokes"])
    R = float(params["scar_radius_m"])
    rad = R * np.sqrt(rng.uniform(0.0, 0.8, n))
    phi = rng.uniform(0.0, 2 * math.pi, n)
    ang = phi + rng.normal(0.0, math.radians(25.0), n)
    length = rng.uniform(0.010, 0.034, n)
    width = rng.uniform(0.004, 0.009, n)
    depth = rng.uniform(0.0014, 0.0030, n)
    return np.stack([rad * np.cos(phi), rad * np.sin(phi), ang, length, width, depth], axis=1)


def scar_depth(params: dict, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Depth of the cut (m, >= 0) at local chart points (x across the lame front-back, y medial ->
    lateral, metres from the scar centre). Inside the ragged circle the floor is below both lacquer
    layers everywhere; the strokes (V-section gouges, deepest mid-length) cut deeper and run out past
    the rim as radial notches."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    R = float(params["scar_radius_m"])
    rng = np.random.default_rng([int(params["seed"]), 8])
    k = np.arange(1, 17)
    amp = rng.uniform(0.2, 1.0, len(k)) / k
    ph = rng.uniform(0.0, 2 * math.pi, len(k))
    th = np.arctan2(y, x)
    rim = R * (1.0 + SCAR_RIM_NOISE * np.sum(amp[:, None] * np.sin(k[:, None] * th.ravel()[None, :] + ph[:, None]),
                                             axis=0).reshape(th.shape) / amp.sum())
    # chipping: small flakes of lacquer broken off along the rim, at random places and of random
    # widths and depths (no regular serration)
    n_ch = 34
    a_ch = rng.uniform(0.0, 2 * math.pi, n_ch)
    w_ch = rng.uniform(0.04, 0.16, n_ch)
    d_ch = rng.uniform(0.25, 1.0, n_ch) * rng.uniform(0.0, 1.0, n_ch) ** 0.5
    chip = np.zeros(th.shape)
    for a, w, dd in zip(a_ch, w_ch, d_ch):
        da = np.abs(np.angle(np.exp(1j * (th - a))))
        chip = np.maximum(chip, dd * np.clip(1.0 - da / w, 0.0, 1.0) ** 1.5)
    rim = rim + R * SCAR_CHIP * chip
    r = np.hypot(x, y)
    # the floor: full inside, a short chipped ramp at the rim
    floor = SCAR_FLOOR_M * np.clip((rim - r) / 0.004 + 0.5, 0.0, 1.0)
    d = floor
    for sx, sy, a, L, W, D in scar_strokes(params):
        ca, sa = math.cos(a), math.sin(a)
        along = (x - sx) * ca + (y - sy) * sa
        across = -(x - sx) * sa + (y - sy) * ca
        t = np.clip(along / (0.5 * L), -1.0, 1.0)
        prof = (1.0 - np.abs(across) / (0.5 * W)) * (np.abs(along) < 0.5 * L)
        cut = D * np.clip(prof, 0.0, 1.0) * (1.0 - t * t) ** 0.35
        d = np.maximum(d, cut)
    # a stroke that runs past the rim only chips it (a notch of a few millimetres, never a ray)
    return np.where(r > rim, d * np.clip((rim + SCAR_OVERSHOOT - r) / SCAR_OVERSHOOT, 0.0, 1.0), d)


def _plate(part: Part, P: np.ndarray, N: np.ndarray, thick: float, rect_front, rect_back, rect_edge,
           stride: int = 1) -> None:
    """A closed plate: the outer grid P[j, i] (normals N point out), the inner surface `thick` inward,
    and the four edge strips."""
    nj, ni = P.shape[:2]
    Q = P - N * thick

    def uvf(rect):
        u0, v0, u1, v1 = rect
        return lambda j, i: (u0 + (u1 - u0) * i / (ni - 1), v0 + (v1 - v0) * j / (nj - 1))

    # winding: outward
    a, b, d = P[0, 0], P[0, 1], P[1, 0]
    flip = np.cross(b - a, d - a) @ N[0, 0] < 0  # an unflipped grid faces cross(du, dv)
    grid(part, P, "cloth", tags=TAG_CLOTH, flip=flip, uv_fn=uvf(rect_front))
    if stride > 1:  # the inner face and the edges at a coarser step (unseen; the GLB size cap)
        keep_j = sorted(set(range(0, nj, stride)) | {nj - 1})
        keep_i = sorted(set(range(0, ni, stride)) | {ni - 1})
        P, Q, N = P[keep_j][:, keep_i], Q[keep_j][:, keep_i], N[keep_j][:, keep_i]
        nj, ni = P.shape[:2]
    grid(part, Q, "cloth", tags=TAG_CLOTH, flip=not flip, uv_fn=uvf(rect_back))
    ring_P = np.concatenate([P[0, :], P[1:, -1], P[-1, -2::-1], P[-2:0:-1, 0]])
    ring_Q = np.concatenate([Q[0, :], Q[1:, -1], Q[-1, -2::-1], Q[-2:0:-1, 0]])
    ring_P = np.concatenate([ring_P, ring_P[:1]])
    ring_Q = np.concatenate([ring_Q, ring_Q[:1]])
    E = np.stack([ring_P, ring_Q], axis=0)
    u0, v0, u1, v1 = rect_edge
    m = E.shape[1]
    # the edge's own winding: outward is away from the plate's middle
    mid = P.reshape(-1, 3).mean(axis=0)
    a, b, d = E[0, 0], E[0, 1], E[1, 0]
    out = (a + b) * 0.5 - mid
    flip_e = np.cross(b - a, d - a) @ out < 0
    grid(part, E, "cloth", tags=TAG_CLOTH, flip=flip_e,
         uv_fn=lambda j, i: (u0 + (u1 - u0) * i / (m - 1), v0 + (v1 - v0) * j))


def _grid_normals(P: np.ndarray, centre: np.ndarray) -> np.ndarray:
    du = np.gradient(P, axis=1)
    dv = np.gradient(P, axis=0)
    n = np.cross(dv, du)
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-12)
    s = np.sign(np.sum(n * (P - centre), axis=-1, keepdims=True))
    s[s == 0] = 1.0
    return n * s


def pauldron(fields: Fields, params: dict, relief=None, top_grid: tuple = TOP_GRID,
             lame_grid: tuple = LAME_GRID) -> tuple[Part, dict]:
    """The five lames on the left shoulder; returns (part, info) where info holds the shell centre.
    M3-CHR-507 (Moll's two whole pauldrons): `relief(params, x, y)` replaces the chisel's `scar_depth` on the top
    lame (same chart and sign: + cuts in, - stands out), and `top_grid` / `lame_grid` set the plates' resolution;
    the defaults are Toma's, so his pauldron is unchanged."""
    lm = fields.lm
    part = Part("Pauldron")
    thick = float(params["pauldron_thickness_m"])
    C = lm.side_pt("shoulder", "L") + np.array([0.0, 0.0, float(params["pauldron_lift_m"])])
    # lames 2-5 first (under), then the top lame
    n_lames = int(params["pauldron_lames"])
    u0, v0, u1, v1 = ATLAS["pauldron_lames"]
    grids = []
    for k in range(n_lames - 1):
        ec, wh = LAME_E_CENTRES[k], LAME_W_HALF[k]
        ni, nj = lame_grid
        s = np.linspace(0.0, 1.0, ni)
        t = np.linspace(0.0, 1.0, nj)
        S, T = np.meshgrid(s, t)
        e = ec - LAME_E_HALF + 2 * LAME_E_HALF * T
        w = wh - 2 * wh * S
        scale = (1.0 - LAME_SHRINK * (k + 1)) * (1.0 + LAME_FLARE * T ** 1.5)
        P = shell_point(e, w, scale)
        hv = (v1 - v0) / (n_lames - 1)
        grids.append((P, (u0, v0 + hv * k, u1, v0 + hv * (k + 1))))
    s0, t0 = SCAR_ST
    ni, nj = top_grid
    S, T = np.meshgrid(np.linspace(0.0, 1.0, ni), np.linspace(0.0, 1.0, nj))
    P_top = top_lame_point(params, S, T)
    N_top = _grid_normals(P_top, np.zeros(3))
    # the chisel pass: displace the top lame inward by the cut's depth
    _c, Ls, Lt = scar_frame(params)
    depth = (relief or scar_depth)(params, (S - s0) * Ls, (T - t0) * Lt)
    P_top = P_top - N_top * depth[..., None]
    # clear the body: where a plate comes within CLEARANCE of the skin field (the trapezius under the
    # top lame's medial edge), lift it out along the shell normal by a smoothed deficit, so the
    # plate bends over the body instead of cutting into it
    fn = lambda Q: np.minimum(fields.upper(Q), fields.body.regions["arm_L"].sdf(Q))  # noqa: E731
    lifted = []
    for P in [g[0] for g in grids] + [P_top]:
        N = _grid_normals(P, np.zeros(3))
        Q = P + C
        for _ in range(4):
            dfc = np.maximum(CLEARANCE - fn(Q.reshape(-1, 3)).reshape(P.shape[:2]), 0.0)
            for _ in range(6):  # blur the deficit over the grid (edges clamp)
                pad = np.pad(dfc, 1, mode="edge")
                dfc = np.maximum(dfc, (pad[:-2, 1:-1] + pad[2:, 1:-1] + pad[1:-1, :-2] + pad[1:-1, 2:]) * 0.25 * 0.9)
            Q = Q + N * dfc[..., None]
        lifted.append(Q)
    for (P, rect), Q in zip(grids, lifted[:-1]):
        _plate(part, Q, _grid_normals(P, np.zeros(3)), thick, rect, ATLAS["lame_back"], ATLAS["lame_edge"])
    _plate(part, lifted[-1], N_top, thick, ATLAS["pauldron_top"], ATLAS["lame_back"], ATLAS["top_edge"], 3)
    part.C = [(0.0, 0.0, 0.0, 0.0)] * len(part.V)
    # the strap hinge (toma.md §9: one bone, a 6 degree hinge): the middle of the top lame's medial
    # edge, where the harness strap holds it; the bone points across the lame to its lateral edge
    top = lifted[-1]
    mid = top.shape[1] // 2
    return part, {"centre": C, "top_outer": top, "hinge": (top[0, mid], top[-1, mid])}


# ---------------------------------------------------------------------------------------------
# Tunic, skirt, sash
# ---------------------------------------------------------------------------------------------
TUNIC_ARMHOLE_DROP = 0.115  # m below the shoulder joint (M1-CHR-14: 0.085 sat at the armpit; a lowered arm cut it)


def tunic_top(lm, chart: TorsoChart, th_deg: np.ndarray) -> np.ndarray:
    """A shallow wrap V at the front, armholes under both shoulders (sleeveless), a plain neck behind."""
    S = lm.S
    neck = chart.z_sh + math.radians(55) * chart.k
    v = float(lm.P("notch")[2] - 0.06 * S)
    arm = float(lm.P("shoulder")[2] - TUNIC_ARMHOLE_DROP * S)
    strap = chart.z_sh + math.radians(24) * chart.k
    return RC._sym_interp(th_deg, [0, 12, 28, 50, 74, 92, 112, 132, 150, 180],
                          [v, v + 0.025 * S, neck - 0.015 * S, strap, arm, arm, strap, neck, neck, neck])


def skirt_open(fields: Fields, name: str, rect, z_top: float, z_hem: float, th_deg: np.ndarray, off: float,
               n_rows: int, flare: float, folds: int, fold_amp: float, seed: int) -> Part:
    """A skirt panel over the azimuths th_deg (open between the ends), cast on the hips and legs; each
    row at least `flare` x the drop wider than the one above (so it bridges the legs)."""
    part = Part(name)
    part._mat = "cloth"
    lm = fields.lm
    S = lm.S
    rng = np.random.default_rng(seed)
    th = np.radians(th_deg)
    D = dir_theta(th)
    P = np.zeros((n_rows, len(th), 3))
    prev_r = prev_z = None
    phase = rng.uniform(0, 2 * math.pi)
    fn = lambda Q: fields.lower(Q) - off  # noqa: E731
    for j in range(n_rows):
        t = j / (n_rows - 1)
        z = z_top + (z_hem - z_top) * t
        O = np.stack([np.zeros(len(th)), np.full(len(th), 0.01 * S), np.full(len(th), z)], axis=-1)
        r = cast_last(fn, O, D, 0.5 * S)
        if prev_r is not None:
            r = np.maximum(r, prev_r + flare * (prev_z - z))
        prev_r, prev_z = r, z
        rr = r + fold_amp * S * t ** 1.3 * np.sin(folds * th + phase)
        P[j] = O + D * rr[:, None]
    _panel(part, P, rect, _wind_rows(n_rows, len(th), 0.12, 0.2), False, 0.0018 * S, np.array([0.0, 0.01 * S, 0.0]))
    part.grid_P = P
    return part


def _outer_radius(outer: np.ndarray, z: float, th: np.ndarray, S: float, band: float = 0.025) -> np.ndarray:
    near = outer[np.abs(outer[:, 2] - z) < band * S]
    q = near - np.array([0.0, 0.01 * S, 0.0])
    ang = np.arctan2(q[:, 0], -q[:, 1])
    rad = np.hypot(q[:, 0], q[:, 1])
    r = np.zeros(len(th))
    for i in range(len(th)):
        m = np.abs(np.angle(np.exp(1j * (ang - th[i])))) < 0.2
        r[i] = rad[m].max() if m.any() else 0.15 * S
    return r


def sash(fields: Fields, outer: np.ndarray, z_c: float, width: float, turns: int, rect, rect_tails) -> Part:
    """The indigo sash: `turns` overlapping bands (each a third of the width lower and a little further
    out than the one under it, so the wraps read as layers), the knot at the left front and two tails
    that fall to the knee."""
    part = Part("Sash")
    part._mat = "cloth"
    lm = fields.lm
    S = lm.S
    n = 56
    th = np.radians(np.linspace(0.0, 360.0, n, endpoint=False))
    D = dir_theta(th)
    band_w = width / turns * 1.35
    u0, v0, u1, v1 = rect
    rows = 4
    for k in range(turns):
        top = z_c + 0.5 * width - k * (width - band_w) / max(turns - 1, 1)
        P = np.zeros((rows, n, 3))
        for j in range(rows):
            z = top - band_w * j / (rows - 1)
            r = _outer_radius(outer, z, th, S) + (0.004 + SASH_OFF * k) * S
            # a slight bulge mid-band (the cloth is wrapped tight at its edges)
            r = r + 0.002 * S * math.sin(math.pi * j / (rows - 1))
            O = np.stack([np.zeros(n), np.full(n, 0.01 * S), np.full(n, z)], axis=-1)
            P[j] = O + D * r[:, None]
        hv = (v1 - v0) / turns
        _panel(part, P, (u0, v0 + hv * k, u1, v0 + hv * (k + 1)), [[(0.0, 0.0, 0.0, 0.0)] * n] * rows, True,
               0.0012 * S, np.array([0.0, 0.01 * S, 0.0]))
        outer = np.concatenate([outer, P.reshape(-1, 3)])
    # the knot at the left front, and two tails to the knee
    th_k = math.radians(32.0)
    dk = np.array([math.sin(th_k), -math.cos(th_k), 0.0])
    z_k = z_c - 0.02 * S
    r_k = float(_outer_radius(outer, z_k, np.array([th_k]), S)[0])
    knot_c = np.array([0.0, 0.01 * S, z_k]) + dk * (r_k + 0.018 * S)
    kn = Part("SashKnot")
    uv_sphere(kn, knot_c, np.array([0.042, 0.030, 0.036]) * S, 14, 8, "cloth", axis_fwd=dk,
              uv_rect=(u0, v0, u0 + 0.15, v1), tags=TAG_CLOTH)
    kn.C = [(0.0, 0.0, 0.0, 0.0)] * len(kn.V)
    part.extend(kn)
    kn_z = float(lm.side_pt("knee", "L")[2])
    tails = Part("SashTails")
    tails._mat = "cloth"
    tails.tail_rows = []  # per tail: (first vertex, rows, columns, layers) for the rig's chain weights
    for k, (dth, drop) in enumerate(((-7.0, 0.0), (8.0, 0.05))):
        Q = sash_tail(outer, knot_c, k, math.radians(32.0 + dth), knot_c[2] - 0.02 * S,
                      kn_z + 0.02 * S + drop * S, S)
        rows_t, cols_t = Q.shape[:2]
        cols = [[(t, t, 0.37 * k + 0.2, 0.25 * t)] * cols_t for t in np.linspace(0, 1, rows_t)]
        tu0, tv0, tu1, tv1 = rect_tails
        first = len(tails.V)
        ua, ub = tu0 + (tu1 - tu0) * 0.5 * k, tu0 + (tu1 - tu0) * 0.5 * (k + 1)
        # faces away from the waist axis at the tail's own height (its own winding test, _shell)
        _shell(tails, Q, lambda j, i, ua=ua, ub=ub: (ua + (ub - ua) * i / (cols_t - 1), tv0 + (tv1 - tv0) * j / (rows_t - 1)),
               False, np.array([0.0, 0.01 * S, float(Q[:, :, 2].mean())]), 0.0012 * S, cols)
        tails.tail_rows.append((first, rows_t, cols_t, (len(tails.V) - first) // (rows_t * cols_t)))
    part.tail_first = len(part.V)
    part.tail_rows = tails.tail_rows
    part.extend(tails)
    return part


# M2-CHR-04: the tails hang and fold (M2-CHR-02 had two flat three-column strips that followed the
# body like boards). Gathered narrow under the knot, they open to their full width within a fifth
# of their length, fall plumb once they pass the widest point under them (cloth does not follow a
# surface back inward), and carry a few soft folds whose depth grows toward the hem; a slow S-sway,
# a little twist, and a slanted cut hem.
TAIL_ROWS = 18
TAIL_COLS = 11
TAIL_HALF_W = 0.046  # x S: half the tail's width when open (a 9 cm tail of the 18 cm sash)
TAIL_GATHER = 0.42  # width share right under the knot
TAIL_OPEN_T = 0.22  # the length share over which it opens
TAIL_FOLDS = 1.6  # fold periods across the width (three ridges)
TAIL_FOLD_KNOT = 0.012  # x S: the fold depth where it is gathered under the knot ...
TAIL_FOLD_HEM = 0.010  # ... and at the hem
TAIL_SLANT = 0.035  # x S: the hem's cut, from one edge to the other
TAIL_CLEAR = 0.012  # x S: over the costume under it (the second tail another half of this)


def sash_tail(outer: np.ndarray, knot_c: np.ndarray, k: int, thk: float, z0: float, z1: float, S: float) -> np.ndarray:
    """One tail's grid P[row (knot -> hem), column (edge -> edge)]."""
    dd = np.array([math.sin(thk), -math.cos(thk), 0.0])
    side0 = np.cross(np.array([0.0, 0.0, 1.0]), dd)
    Q = np.zeros((TAIL_ROWS, TAIL_COLS, 3))
    f = np.linspace(-1.0, 1.0, TAIL_COLS)
    r_prev = None
    phase = 0.9 + 1.7 * k
    for j in range(TAIL_ROWS):
        t = j / (TAIL_ROWS - 1)
        z = z0 + (z1 - z0) * t
        r_body = float(_outer_radius(outer, z, np.array([thk]), S, 0.03)[0]) + (TAIL_CLEAR * (1.0 + 0.5 * k)) * S
        # plumb below the widest point: never pulled back in by more than a little slack per row
        r = r_body if r_prev is None else max(r_body, r_prev - 0.004 * S)
        r_prev = r
        c = np.array([0.0, 0.01 * S, z]) + dd * r
        open_ = TAIL_GATHER + (1.0 - TAIL_GATHER) * float(np.clip(t / TAIL_OPEN_T, 0.0, 1.0)) ** 0.7
        w = TAIL_HALF_W * S * open_ * (1.0 - 0.10 * t)
        tw = 0.22 * math.sin(1.6 * t + 0.8 * k)  # twist about the vertical, rad
        side = side0 * math.cos(tw) + dd * math.sin(tw)
        out = np.cross(side, np.array([0.0, 0.0, 1.0]))
        out *= np.sign(out @ dd)
        sway = side0 * (0.014 * S * math.sin(2.2 * t + 1.3 * k))
        gathered = 1.0 - float(np.clip(t / TAIL_OPEN_T, 0.0, 1.0))
        amp = S * (TAIL_FOLD_KNOT * gathered + TAIL_FOLD_HEM * float(np.clip((t - 0.15) / 0.85, 0.0, 1.0)) ** 0.8)
        fold = amp * np.sin(2.0 * math.pi * TAIL_FOLDS * 0.5 * (f + 1.0) + phase + 0.9 * t)
        # the folds take up width: the edges come in a little where the folds are deep
        squeeze = 1.0 - 0.08 * amp / (0.01 * S)
        hem = TAIL_SLANT * S * 0.5 * (f + 1.0) * t ** 4  # only the last rows slant
        for i in range(TAIL_COLS):
            Q[j, i] = c + side * (w * f[i] * squeeze) + out * (fold[i] + 0.004 * S * (1.0 - f[i] ** 2)) + sway
            Q[j, i, 2] += hem[i] * (1.0 if k == 0 else -1.0)
    return Q


# ---------------------------------------------------------------------------------------------
# Sandals (toma.md §4 #6: leather with a reinforced sole). M2-CHR-04: his own; M2-CHR-02 borrowed
# Rhen's thin 8 mm sole, which barely showed past the foot.
# ---------------------------------------------------------------------------------------------
SOLE_N = 32  # outline samples round the foot
SOLE_SLICES = (0.006, 0.014, 0.022, 0.030)  # x S: heights of the foot slices whose widest is the outline
SOLE_OUT = 0.011  # x S: the outsole's edge past the foot outline
WELT_OUT = 0.008  # x S: the stitched welt above it, stepped in
SOLE_H = 0.009  # x S: the outsole's top (the bottom sits 2 mm under the floor, as Rhen's)
WELT_H = (0.018, 0.013)  # x S: the welt's top at the heel and at the toe (a thicker heel)
COUNTER_H = 0.028  # x S: the heel counter's height over the welt
COUNTER_OFF = 0.003  # x S: off the skin
STRAP_U = (0.50, 0.72)  # instep straps, heel -> toe share
STRAP_HALF = 0.012  # x S: half a strap's width
# the sandal's sub-islands in ATLAS["sandals"] (v shares): sole edge, welt edge, caps, heel counter, straps
SANDAL_V = {"sole": (0.0, 0.25), "welt": (0.25, 0.42), "cap": (0.45, 0.5), "counter": (0.55, 0.72),
            "strap": (0.75, 1.0)}


def _sub(rect, key: str) -> tuple:
    u0, v0, u1, v1 = rect
    a, b = SANDAL_V[key]
    return (u0, v0 + (v1 - v0) * a, u1, v0 + (v1 - v0) * b)


def _shell(part: Part, P: np.ndarray, uv_fn, closed: bool, centre: np.ndarray, back_inset: float | None = None,
           colors=None):
    """A grid whose faces point away from `centre` (plus an optional back layer `back_inset` inward).
    The winding test is local: an unflipped asha_mesh.grid faces cross(du, dv)."""
    N = _grid_normals(P, centre)
    a, b, d = P[0, 0], P[0, 1], P[1, 0]
    flip = bool(np.cross(b - a, d - a) @ N[0, 0] < 0)
    ids = grid(part, P, part._mat, colors=colors, tags=TAG_CLOTH, flip=flip, uv_fn=uv_fn, closed_u=closed)
    if back_inset:
        grid(part, P - N * back_inset, part._mat, colors=colors, tags=TAG_CLOTH, flip=not flip, uv_fn=uv_fn,
             closed_u=closed)
    return ids


def reinforced_sandal(fields: Fields, side: str, rect) -> Part:
    """A thick leather sole in two tiers (the outsole, then a stitched welt stepped in on top of it,
    higher at the heel), a stiff heel counter cupping the heel, two broad instep straps and an ankle
    strap under the shin wraps."""
    part = Part(f"Sandal{side}")
    part._mat = "cloth"
    lm = fields.lm
    S = lm.S
    hb_, tt = lm.side_pt("heel_back", side), lm.side_pt("toe_tip", side)
    fwd = (tt - hb_) / np.linalg.norm(tt - hb_)
    lat = np.cross(fwd, np.array([0.0, 0.0, 1.0]))
    fn = fields.region(f"foot_{side}")
    c0 = (hb_ + tt) * 0.5
    c0[2] = 0.006 * S
    a = 2 * math.pi * np.arange(SOLE_N) / SOLE_N
    D = np.cos(a)[:, None] * fwd[None, :] + np.sin(a)[:, None] * lat[None, :]
    # the outline is the widest of a few slices up the foot: the donor's sole is rounded, so a slice at
    # the floor alone (Rhen's) falls inside the foot's silhouette and the sole hides under it
    r = np.max([cast_last(fn, np.repeat(np.array([[c0[0], c0[1], z * S]]), SOLE_N, axis=0), D, 0.2 * S)
                for z in SOLE_SLICES], axis=0)
    base = c0[None, :] + D * r[:, None]
    toe_share = 0.5 + 0.5 * np.cos(a)  # 1 at the toe, 0 at the heel
    h_welt = (WELT_H[1] * toe_share + WELT_H[0] * (1.0 - toe_share)) * S

    def ring(out: float, z) -> np.ndarray:
        P = base + D * (out * S)
        P[:, 2] = z
        return P

    welt_top = ring(WELT_OUT, h_welt)
    rows = np.stack([welt_top, ring(WELT_OUT, SOLE_H * S + 0.0005 * S), ring(SOLE_OUT, SOLE_H * S),
                     ring(SOLE_OUT, -0.002)])
    # the welt and the sole edge are one ring grid (the ledge between them is its middle row); the
    # welt's rows sample the welt island, the sole's rows the sole island
    wv, sv = _sub(rect, "welt"), _sub(rect, "sole")
    vs = [wv[1], wv[3], sv[1], sv[3]]
    ids = _shell(part, rows, lambda j, i: (rect[0] + (rect[2] - rect[0]) * i / SOLE_N, vs[j]), True, c0)
    cu, cv0, _cu1, cv1 = _sub(rect, "cap")
    cap_uv = (cu + 0.01, 0.5 * (cv0 + cv1))
    ct = part.add_v(np.array([c0[0], c0[1], float(h_welt.mean())]), tag=TAG_CLOTH)
    cb = part.add_v(np.array([c0[0], c0[1], -0.002]), tag=TAG_CLOTH)
    top, bot = ids[0], ids[-1]
    for i in range(SOLE_N):
        i2 = (i + 1) % SOLE_N
        tri_t = (ct, int(top[i2]), int(top[i]))
        tri_b = (cb, int(bot[i]), int(bot[i2]))
        # wind the caps up (top) and down (bottom)
        for tri, want in ((tri_t, 1.0), (tri_b, -1.0)):
            p0, p1, p2 = (part.V[j] for j in tri)
            if np.cross(p1 - p0, p2 - p0)[2] * want < 0:
                tri = (tri[0], tri[2], tri[1])
            part.add_f(tri, [cap_uv] * 3, "cloth")
    # heel counter: the back half of the outline, cast again at its own heights
    back = np.nonzero(np.cos(a) < -0.15)[0]
    back = back[np.argsort((a[back] - math.pi / 2) % (2 * math.pi))]  # one run round the heel
    zc = [float(h_welt[back].mean()) + COUNTER_H * S, float(h_welt[back].mean()) - 0.001 * S]
    Pc = np.zeros((2, len(back), 3))
    for j, z in enumerate(zc):
        cc = np.array([c0[0], c0[1], z])
        rr = cast_last(fn, np.repeat(cc[None, :], len(back), axis=0), D[back], 0.2 * S)
        Pc[j] = cc[None, :] + D[back] * (rr + COUNTER_OFF * S)[:, None]
    cr = _sub(rect, "counter")
    _shell(part, Pc, lambda j, i: (cr[0] + (cr[2] - cr[0]) * i / (len(back) - 1), cr[1] + (cr[3] - cr[1]) * j), False,
           np.array([c0[0], c0[1], zc[0]]), 0.0015 * S)
    # straps over the instep and round the ankle (under the shin wraps)
    strap = _sub(rect, "strap")
    for u in STRAP_U:
        c = hb_ + (tt - hb_) * u + np.array([0.0, 0.0, 0.02 * S])
        part.extend(limb_wrap(fields, f"foot_{side}", c - fwd * STRAP_HALF * S, c + fwd * STRAP_HALF * S,
                              RC.WRAP_OFF * S, strap, "strap", n_around=16, rows=2))
    an = lm.side_pt("ankle", side)
    kn = lm.side_pt("knee", side)
    part.extend(limb_wrap(fields, f"leg_{side}", an - (kn - an) * 0.06, an + (kn - an) * 0.03, RC.WRAP_OFF * S,
                          strap, "ankle", n_around=20, rows=3))
    return part


def _resolve(lm, chart: TorsoChart, h) -> float:
    if isinstance(h, str):
        base, off = h[:-5], float(h[-5:])
        z = float(lm.P("nipple")[2]) if base == "nip" else chart.z_sh
        return z + off * lm.S
    return chart.z_sh + math.radians(float(h)) * chart.k


def harness(fields: Fields, chart: TorsoChart, width: float) -> tuple[Part, np.ndarray, np.ndarray]:
    lm = fields.lm
    path = [(a, _resolve(lm, chart, h)) for a, h in HARNESS_PATH]
    part, C, N = RC.bandolier(fields, chart, width * lm.S, ATLAS["harness"], path, "Harness", HARNESS_OFF * lm.S)
    # bronze buckles: one on the chest, one between the shoulder blades
    S = lm.S
    bk = Part("Buckles")
    for target in (np.array([0.02, -0.2, float(lm.P("nipple")[2]) + 0.0]), np.array([-0.02, 0.2, chart.z_sh - 0.12])):
        i = int(np.argmin(np.linalg.norm(C - target, axis=1)))
        c = C[i] + N[i] * 0.004 * S
        T = C[min(i + 1, len(C) - 1)] - C[max(i - 1, 0)]
        T /= np.linalg.norm(T)
        side = np.cross(N[i], T)
        w, h = 0.034 * S, width * S * 1.25
        corners = [c + side * h / 2 - T * w / 2, c + side * h / 2 + T * w / 2, c - side * h / 2 + T * w / 2,
                   c - side * h / 2 - T * w / 2]
        for k in range(4):
            a, b = corners[k], corners[(k + 1) % 4]
            tube(bk, np.linspace(a, b, 2), 0.0034 * S, 6, "bronze", N[i], (0, 0, 0.1, 0.1), tags=TAG_CLOTH)
        tube(bk, np.linspace(c - side * h * 0.45, c + side * h * 0.45, 2), 0.0022 * S, 6, "bronze", N[i],
             (0, 0, 0.1, 0.1), tags=TAG_CLOTH)
    bk.C = [(0.0, 0.0, 0.0, 0.0)] * len(bk.V)
    part.extend(bk)
    return part, C, N


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
    sash_w = float(params["sash_width_m"])
    z_sash = z_waist - 0.01 * S
    # 1. under-tunic: a closed body from the neck to under the sash, then the slit skirt
    th_u = np.linspace(0.0, 360.0, 56, endpoint=False)
    out["Tunic"] = RC.torso_sheet(fields, chart, "Tunic", ATLAS["tunic"], th_u, tunic_top(lm, chart, th_u),
                                  z_sash - 0.35 * sash_w, TUNIC_OFF * S, 14, 0.0015 * S, True)
    slit = float(params["tunic_slit_deg"])
    th_s = np.linspace(-90.0 + slit / 2, 270.0 - slit / 2, 54)
    z_hem = z_crotch - float(params["tunic_hem_below_crotch_m"]) * S
    out["Skirt"] = skirt_open(fields, "Skirt", ATLAS["skirt"], z_sash + 0.3 * sash_w, z_hem, th_s, SKIRT_OFF * S, 12,
                              0.20, 9, 0.006, int(params["seed"]))
    # 2. trousers: a pelvis band and two legs to mid-shin, gathered at the hem into the wraps
    an_z = float(lm.side_pt("ankle", "L")[2])
    kn_z = float(lm.side_pt("knee", "L")[2])
    hem_z = an_z + (kn_z - an_z) * float(params["trouser_hem_shin"])
    th_t = np.linspace(0.0, 360.0, 48, endpoint=False)
    pelvis = Part("TrouserTop")
    pelvis._mat = "cloth"
    rows = 8
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
        path = RC.leg_path(lm, sd, z_crotch + 0.06 * S, hem_z, 14)
        out[f"TrouserLeg{sd}"] = RC.limb_tube(
            fields, f"leg_{sd}", path, lambda t: (0.0075 + 0.016 * math.sin(math.pi * min(t * 1.15, 1.0)) ** 1.2
                                                  + 0.002) * S,
            ATLAS[f"trouser_leg_{sd}"], f"TrouserLeg{sd}", n_around=24, rows=14, back_inset=0.0018 * S,
            wind_amp=0.06)
    # shin-to-ankle wraps over the gathered hem
    w0, w1 = (float(x) for x in params["wrap_span"])
    wraps = Part("Wraps")
    for sd in ("L", "R"):
        an, kn = lm.side_pt("ankle", sd), lm.side_pt("knee", sd)
        wraps.extend(limb_wrap(fields, f"leg_{sd}", an + (kn - an) * w0, an + (kn - an) * w1, SHIN_WRAP_OFF * S,
                               ATLAS["wraps"], f"Wrap{sd}", n_around=22, rows=10))
    out["Wraps"] = wraps
    sandals = Part("Sandals")
    for sd in ("L", "R"):
        sandals.extend(reinforced_sandal(fields, sd, ATLAS["sandals"]))
    out["Sandals"] = sandals
    # 3. sash over the tunic and the skirt top
    outer = np.concatenate([out["Tunic"].varr(), out["Skirt"].varr(), out["TrouserTop"].varr()])
    out["Sash"] = sash(fields, outer, z_sash, sash_w * S, int(params["sash_turns"]), ATLAS["sash"],
                       ATLAS["sash_tails"])
    # 4. harness
    out["Harness"], strap_c, strap_n = harness(fields, chart, float(params["harness_width_m"]))
    # 5. pauldron
    out["Pauldron"], pinfo = pauldron(fields, params)
    for p in out.values():
        if not p.C:
            p.C = [(0.0, 0.0, 0.0, 0.0)] * len(p.V)
        elif len(p.C) < len(p.V):
            p.C = p.C + [(0.0, 0.0, 0.0, 0.0)] * (len(p.V) - len(p.C))
    allv = np.concatenate([p.varr() for p in out.values()])
    upper = allv[(allv[:, 2] > float(lm.P("nipple")[2]) - 0.25 * S) & (allv[:, 2] < chart.z_sh + 0.25)]
    anchors = {"back_y": float(upper[:, 1].max()), "pauldron_centre": pinfo["centre"], "pauldron_hinge": pinfo["hinge"],
               "chest_z": float(lm.P("nipple")[2]), "hip_x": float(np.abs(out["Skirt"].varr()[:, 0]).max())}
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
    tunic = torso & (H < tunic_top(lm, chart, th_deg) - m)
    kn_z = float(lm.side_pt("knee", "L")[2])
    an_z = float(lm.side_pt("ankle", "L")[2])
    hem_z = an_z + (kn_z - an_z) * float(params["trouser_hem_shin"])
    legs = (reg == "leg_L") | (reg == "leg_R") | torso
    trousers = legs & (V[:, 2] < z_waist) & (V[:, 2] > hem_z + 0.02 * S)
    shins = np.zeros(len(V), dtype=bool)
    w0, w1 = (float(x) for x in params["wrap_span"])
    for sd in ("L", "R"):
        an, kn = lm.side_pt("ankle", sd), lm.side_pt("knee", sd)
        ax = kn - an
        t = (V - an) @ ax / (ax @ ax)
        shins |= (reg == f"leg_{sd}") & (t > w0 + 0.04) & (t < w1 + 0.02)
    return tunic | trousers | shins
