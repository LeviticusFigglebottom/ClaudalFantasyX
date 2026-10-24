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
6. Leather sandals with a reinforced sole (rhen_costume.wrapped_sandal).

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


def pauldron(fields: Fields, params: dict) -> tuple[Part, dict]:
    """The five lames on the left shoulder; returns (part, info) where info holds the shell centre."""
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
        ni, nj = LAME_GRID
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
    ni, nj = TOP_GRID
    S, T = np.meshgrid(np.linspace(0.0, 1.0, ni), np.linspace(0.0, 1.0, nj))
    P_top = top_lame_point(params, S, T)
    N_top = _grid_normals(P_top, np.zeros(3))
    # the chisel pass: displace the top lame inward by the cut's depth
    _c, Ls, Lt = scar_frame(params)
    depth = scar_depth(params, (S - s0) * Ls, (T - t0) * Lt)
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
    return part, {"centre": C, "top_outer": lifted[-1]}


# ---------------------------------------------------------------------------------------------
# Tunic, skirt, sash
# ---------------------------------------------------------------------------------------------
def tunic_top(lm, chart: TorsoChart, th_deg: np.ndarray) -> np.ndarray:
    """A shallow wrap V at the front, armholes under both shoulders (sleeveless), a plain neck behind."""
    S = lm.S
    neck = chart.z_sh + math.radians(55) * chart.k
    v = float(lm.P("notch")[2] - 0.06 * S)
    arm = float(lm.P("shoulder")[2] - 0.085 * S)
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
    for k, (dth, drop) in enumerate(((-7.0, 0.0), (8.0, 0.05))):
        thk = math.radians(32.0 + dth)
        dd = np.array([math.sin(thk), -math.cos(thk), 0.0])
        side = np.cross(np.array([0.0, 0.0, 1.0]), dd)
        rows_t = 14
        Q = np.zeros((rows_t, 3, 3))
        z0 = knot_c[2] - 0.02 * S
        z1 = kn_z + 0.02 * S + drop * S
        for j in range(rows_t):
            t = j / (rows_t - 1)
            z = z0 + (z1 - z0) * t
            rad = float(_outer_radius(outer, z, np.array([thk]), S, 0.03)[0]) + (0.012 + 0.006 * k) * S
            c = np.array([0.0, 0.01 * S, z]) + dd * rad
            w = (0.046 - 0.008 * t) * S
            sway = side * (0.012 * S * math.sin(2.0 * t + 1.3 * k))
            for i, f in enumerate((-1.0, 0.0, 1.0)):
                Q[j, i] = c + side * w * f + sway
        cols = [[(t, t, 0.37 * k + 0.2, 0.25 * t)] * 3 for t in np.linspace(0, 1, rows_t)]
        tu0, tv0, tu1, tv1 = rect_tails
        _panel(tails, Q, (tu0 + (tu1 - tu0) * 0.5 * k, tv0, tu0 + (tu1 - tu0) * 0.5 * (k + 1), tv1), cols, False,
               0.0012 * S, np.array([0.0, 0.01 * S, 0.0]))
    part.extend(tails)
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
        sandals.extend(RC.wrapped_sandal(fields, sd, ATLAS["sandals"]))
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
    anchors = {"back_y": float(upper[:, 1].max()), "pauldron_centre": pinfo["centre"],
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
