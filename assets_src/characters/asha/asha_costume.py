"""Asha's costume as procedural cloth panels (no bpy), asha.md §3-§4 and §9.2.

Every garment is a *pattern grid*: a chart of (azimuth around the body axis, height) whose rows are
ray-cast from the body axis onto the body field plus a fitting offset. The chart is also the
garment's UV island in the 2K cloth atlas (so the UVs *are* the flat pattern), and the masks in
asha_textures.py are drawn on the same charts. Pieces (inner to outer):

1. Under-bodice: a wrapped band top under the vest (visible at the back scoop and under the left arm).
2. Inner skirt (cotton lawn, ankle length) and 3. outer wrap-skirt (sea blue, dip-dyed, asymmetric
   hem from mid-calf on the left to the ankle on the right, an A-line with flare folds).
4. Sash: a 12 cm silk band at the waist, knotted on the right hip, two tails to mid-thigh.
5. Vest: black lacquered leather; a high 6 cm collar, cut away at the left shoulder in a halter
   line, covering the right shoulder (which carries the sleeve ring), a deep scoop at the back.
6. Verse-sleeve: gauze on the right arm, from the shoulder seam hanging to the knee (0.95 m),
   one mesh for every verse state (UV.y shoulder 0 -> cuff tip 1; bands on the outer 220 deg).
7. Left-forearm wrap and ankle wraps (linen) and 8. sandals (sole and straps).

Opaque pieces get an inset, flipped back layer (the cloth shader culls back faces) so hems, the
halter edge and the inside of the collar never show a hole. Vertex colour = wind (R primary,
G ripple, B phase, A flutter). `coverage()` says which body vertices are hidden under clothing
(those faces are deleted, asha.md §8.1). Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

import bb_anatomy
from asha_mesh import Part, grid

# cloth atlas islands (u0, v0, u1, v1) in the shader's UV convention (v down)
ATLAS = {
    "skirt_outer": (0.0, 0.0, 0.5, 0.62),
    "skirt_inner": (0.5, 0.0, 0.75, 0.62),
    "vest": (0.0, 0.62, 0.5, 1.0),
    "collar": (0.5, 0.62, 0.75, 0.75),
    "bodice": (0.5, 0.75, 0.75, 1.0),
    "sash": (0.75, 0.0, 1.0, 0.30),
    "sash_tails": (0.75, 0.30, 1.0, 0.60),
    "wraps": (0.75, 0.60, 1.0, 0.80),
    "sandals": (0.75, 0.80, 1.0, 1.0),
}
TAG_CLOTH = 51


def _deg(a: float) -> float:
    return math.radians(a)


def dir_theta(th: np.ndarray) -> np.ndarray:
    """Azimuth 0 = front (-Y), +90 deg = the character's left (+X)."""
    return np.stack([np.sin(th), -np.cos(th), np.zeros_like(th)], axis=-1)


class Fields:
    def __init__(self, body) -> None:
        self.body = body
        lm = body.lm
        self.lm = lm
        self.sh = {sd: lm.side_pt("shoulder", sd) for sd in ("L", "R")}

    def upper(self, P: np.ndarray) -> np.ndarray:
        """Torso and neck plus the shoulder caps of the arms (the vest's fitting surface)."""
        b = self.body
        d = b.regions["torso"].sdf(P)
        for sd in ("L", "R"):
            a = b.regions[f"arm_{sd}"].sdf(P)
            a = np.maximum(a, np.linalg.norm(P - self.sh[sd], axis=1) - 0.075 * self.lm.S)
            d = bb_anatomy.smin(d, a, 0.014 * self.lm.S)
        return d

    def lower(self, P: np.ndarray) -> np.ndarray:
        b = self.body
        d = b.regions["torso"].sdf(P)
        for sd in ("L", "R"):
            d = np.minimum(d, b.regions[f"leg_{sd}"].sdf(P))
        return d

    def region(self, name: str):
        return lambda P: self.body.regions[name].sdf(P)


def cast_last(fn, O: np.ndarray, D: np.ndarray, tmax: float, steps: int = 160) -> np.ndarray:
    """Distance to the farthest exit from fn < 0 along each ray (0 if the ray never enters)."""
    ts = np.linspace(0.0, tmax, steps)
    P = O[:, None, :] + D[:, None, :] * ts[None, :, None]
    d = fn(P.reshape(-1, 3)).reshape(len(O), steps)
    inside = d < 0
    any_in = inside.any(axis=1)
    last = steps - 1 - np.argmax(inside[:, ::-1], axis=1)
    j = np.clip(last, 0, steps - 2)
    lo, hi = ts[j].copy(), ts[j + 1].copy()
    for _ in range(16):
        mid = 0.5 * (lo + hi)
        m_in = fn(O + D * mid[:, None]) < 0
        lo = np.where(m_in, mid, lo)
        hi = np.where(m_in, hi, mid)
    return np.where(any_in, 0.5 * (lo + hi), 0.0)


def _back_layer(part: Part, ids: np.ndarray, inset: float, normal_fn, mat: str, uv_fn, cols=None) -> None:
    """A flipped copy of a grid pushed `inset` inward (thickness), so culled cloth has a back."""
    nj, ni = ids.shape
    P = np.array([[part.V[ids[j, i]] for i in range(ni)] for j in range(nj)])
    N = normal_fn(P.reshape(-1, 3)).reshape(nj, ni, 3)
    Q = P - N * inset
    colors = None if cols is None else [[part.C[ids[j, i]] for i in range(ni)] for j in range(nj)]
    grid(part, Q, mat, colors=colors, tags=TAG_CLOTH, flip=True, uv_fn=uv_fn)
    _ = cols


def _grid_normals(P: np.ndarray, closed: bool) -> np.ndarray:
    du = np.roll(P, -1, axis=1) - np.roll(P, 1, axis=1) if closed else np.gradient(P, axis=1)
    dv = np.gradient(P, axis=0)
    n = np.cross(dv, du)
    return n / np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-12)


def _outward(P: np.ndarray, N: np.ndarray, centre: np.ndarray) -> np.ndarray:
    """Orient a grid's normals away from the body axis: the whole grid flips by the majority sign.
    M1-CHR-13: flipping each vertex by sign(N . q), q horizontal from the axis, flipped vertex by
    vertex along a staircase wherever the normal is near vertical (the top of the shoulder), which
    pushed the inset back layer in and out by its thickness and creased the vest's normals."""
    q = P - centre
    q[..., 2] = 0.0
    s = 1.0 if float(np.sum(N * q)) >= 0.0 else -1.0
    return N * s


def _uvf(rect, nj: int, ni: int, closed: bool):
    u0, v0, u1, v1 = rect
    cols = ni if closed else ni - 1

    def f(j: int, i: int) -> tuple[float, float]:
        return (u0 + (u1 - u0) * i / cols, v0 + (v1 - v0) * j / (nj - 1))

    return f


def _panel(part: Part, P: np.ndarray, rect, colors, closed: bool, back_inset: float | None, centre) -> np.ndarray:
    """Front grid (outward-facing) plus an optional back layer. P[j, i]: rows j top -> bottom."""
    N = _outward(P, _grid_normals(P, closed), centre)
    # make sure the grid's own winding faces outward. M1-CHR-13: grid() winds (j, i), (j, i+1),
    # (j+1, i+1), (j+1, i), whose normal is (b - a) x (d - a); the old test flipped when that already
    # agreed with N, so the front layer faced inward and only the inset back layer was ever seen.
    # Summed over the grid, so one degenerate corner face cannot decide it.
    dU = np.diff(P, axis=1)[:-1]
    dV = np.diff(P, axis=0)[:, :-1]
    flip = bool(np.sum(np.cross(dU, dV) * N[:-1, :-1]) < 0.0)
    uvf = _uvf(rect, P.shape[0], P.shape[1], closed)
    ids = grid(part, P, part._mat, colors=colors, tags=TAG_CLOTH, flip=flip, uv_fn=uvf, closed_u=closed)
    if back_inset:
        Q = P - N * back_inset
        grid(part, Q, part._mat, colors=colors, tags=TAG_CLOTH, flip=not flip, uv_fn=uvf, closed_u=closed)
    return ids


# ---------------------------------------------------------------------------------------------
# Torso pieces
# ---------------------------------------------------------------------------------------------
class TorsoChart:
    """(theta, H) -> rays. H is height below the shoulder pivot, and pivot-height + 0.12 m per radian
    of elevation above it, so one chart runs up the chest and over the shoulder to the neck."""

    def __init__(self, lm) -> None:
        self.lm = lm
        S = lm.S
        self.z_sh = float(lm.P("notch")[2] - 0.05 * S)
        self.y_axis = 0.012 * S
        self.k = 0.12 * S

    def rays(self, th: np.ndarray, H: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        th = np.asarray(th, dtype=float)
        H = np.asarray(H, dtype=float)
        e = np.maximum(H - self.z_sh, 0.0) / self.k
        z = np.minimum(H, self.z_sh)
        O = np.stack([np.zeros_like(th), np.full_like(th, self.y_axis), z], axis=-1)
        D = dir_theta(th) * np.cos(e)[..., None] + np.stack([np.zeros_like(e), np.zeros_like(e), np.sin(e)], axis=-1)
        return O, D

    def H_of(self, P: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        q = P - np.array([0.0, self.y_axis, 0.0])
        th = np.arctan2(q[:, 0], -q[:, 1])
        r = np.hypot(q[:, 0], q[:, 1])
        e = np.arctan2(P[:, 2] - self.z_sh, r)
        H = np.where(P[:, 2] <= self.z_sh, P[:, 2], self.z_sh + np.maximum(e, 0.0) * self.k)
        return th, H


VEST_ARMHOLE_DROP = 0.115  # m below the shoulder joint (M1-CHR-14: 0.085 sat at the armpit and wrapped onto the arm)


BODICE_UNDERARM_DROP = 0.045  # m: the bodice's top dips this far under each arm (M1-CHR-14: a lowered arm cut it)
BODICE_UNDERARM_HALF = 40.0  # degrees either side of the side line over which the dip fades


def bodice_top(lm, th_deg: np.ndarray) -> np.ndarray:
    """The under-bodice's top edge: level just above the bust, dipping under the arms."""
    S = lm.S
    side = np.abs(np.mod(np.asarray(th_deg, dtype=float), 180.0) - 90.0)  # 0 on either side line
    w = np.clip(1.0 - side / BODICE_UNDERARM_HALF, 0.0, 1.0)
    w = w * w * (3.0 - 2.0 * w)
    return float(lm.P("nipple")[2] + 0.075 * S) - BODICE_UNDERARM_DROP * S * w


def vest_top(lm, chart: TorsoChart, th_deg: np.ndarray) -> np.ndarray:
    """The vest's top edge: the neckline all round, except the halter cut-away at the left shoulder
    and the deep scoop at the back (asha.md §2.4, §4.1 #5)."""
    S = lm.S
    neck = chart.z_sh + _deg(58) * chart.k
    arm = float(lm.P("shoulder")[2] - VEST_ARMHOLE_DROP * S)
    scoop = float(lm.P("notch")[2] - 0.135 * S)
    xs = [0, 22, 40, 62, 90, 118, 145, 165, 180, 198, 220, 242, 260, 360]
    vs = [neck, neck, chart.z_sh + _deg(32) * chart.k, chart.z_sh + _deg(4) * chart.k, arm, arm + 0.01 * S,
          scoop + 0.02 * S, scoop, scoop, scoop + 0.01 * S, chart.z_sh + _deg(30) * chart.k, neck, neck, neck]
    return np.interp(np.mod(th_deg, 360.0), xs, vs)


def torso_panel(fields: Fields, chart: TorsoChart, name: str, mat: str, rect, H_bot: float, H_top_fn, off: float,
                n_th: int, n_rows: int, back_inset: float | None, wind=None) -> Part:
    part = Part(name)
    part._mat = mat
    lm = fields.lm
    th_deg = np.linspace(0.0, 360.0, n_th, endpoint=False)
    th = np.radians(th_deg)
    H_top = H_top_fn(th_deg)
    P = np.zeros((n_rows, n_th, 3))
    fn = lambda Q: fields.upper(Q) - off  # noqa: E731
    for j in range(n_rows):
        t = j / (n_rows - 1)
        H = H_top + (H_bot - H_top) * t  # row 0 at the top edge
        O, D = chart.rays(th, H)
        r = cast_last(fn, O, D, 0.4 * lm.S)
        P[j] = O + D * r[:, None]
    # relax the columns a little so the edge rows do not crowd
    centre = np.array([0.0, chart.y_axis, 0.0])
    cols = None if wind is None else [[wind(j / (n_rows - 1), i / n_th) for i in range(n_th)] for j in range(n_rows)]
    _panel(part, P, rect, cols, True, back_inset, centre)
    return part


def collar(fields: Fields, rect, height: float, n: int = 48) -> Part:
    """The standing lacquer collar, 6 cm, flaring slightly; inner face and a rim (2.5 mm leather)."""
    part = Part("Collar")
    part._mat = "cloth"
    lm = fields.lm
    S = lm.S
    nb, sb = lm.P("neck_base"), lm.P("skull_base")
    ax = (sb - nb) / np.linalg.norm(sb - nb)
    th = np.radians(np.linspace(0.0, 360.0, n, endpoint=False))
    rows = 5
    P = np.zeros((rows, n, 3))
    base = nb + ax * 0.018 * S
    for j in range(rows):
        t = 1.0 - j / (rows - 1)  # row 0 = top
        c = base + ax * height * t
        D = dir_theta(th)
        O = np.repeat(c[None, :], n, axis=0)
        r = cast_last(lambda Q: fields.body.regions["torso"].sdf(Q) - (0.006 + 0.004 * t) * S, O, D, 0.2 * S)
        P[j] = O + D * r[:, None]
    _panel(part, P, rect, None, True, 0.0025 * S, base)
    return part


# ---------------------------------------------------------------------------------------------
# Skirts and sash
# ---------------------------------------------------------------------------------------------
def convex_radii(r: np.ndarray, D: np.ndarray) -> np.ndarray:
    """M1-CHR-15: the radii along the rays D (unit, horizontal) of the convex hull of the points r * D. A skirt row
    cast below the crotch hugs each leg and pinches to the centre between them (a ray that misses both legs gets
    r = 0); a real skirt spans the gap."""
    Q = D[:, :2] * r[:, None]
    pts = sorted(set(map(tuple, np.round(Q, 12))) | {(0.0, 0.0)})
    if len(pts) < 3:
        return r

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for q in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], q) <= 0:
            lower.pop()
        lower.append(q)
    for q in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], q) <= 0:
            upper.pop()
        upper.append(q)
    H = np.array(lower[:-1] + upper[:-1])
    A, E = H, np.roll(H, -1, axis=0) - H
    out = r.copy()
    for i, d in enumerate(D[:, :2]):
        den = d[0] * (-E[:, 1]) - d[1] * (-E[:, 0])  # solve t d - s e = a
        ok = np.abs(den) > 1e-15
        t = np.where(ok, (A[:, 0] * (-E[:, 1]) - A[:, 1] * (-E[:, 0])) / np.where(ok, den, 1.0), -1.0)
        sp = np.where(ok, (d[0] * A[:, 1] - d[1] * A[:, 0]) / np.where(ok, den, 1.0), -1.0)
        hit = ok & (t > 0.0) & (sp >= -1e-9) & (sp <= 1.0 + 1e-9)
        if hit.any():
            out[i] = max(float(r[i]), float(t[hit].max()))
    return out


SKIRT_OUTER_GRID = (64, 20)  # columns round, rows down (was 56 x 22; the LOD0 budget, asha.md §8.1, holds it here)
UNDERSKIRT_HEM = 0.095  # m (x S) above the floor: just above the ankle (GPU QA row 56: at 0.065 the feet never
# showed in the run, so she seemed to slide)
SKIRT_INNER_GRID = (48, 12)  # (it follows the outer skirt's weights now, so its own density matters less)


def skirt(fields: Fields, name: str, rect, z_top: float, hem_fn, off: float, n_th: int, n_rows: int, folds: int,
          fold_amp: float, flare: float, back_inset: float | None, seed: int,
          convex: tuple[float, float] | None = None) -> Part:
    part = Part(name)
    part._mat = "cloth"
    lm = fields.lm
    S = lm.S
    rng = np.random.default_rng(seed)
    th_deg = np.linspace(0.0, 360.0, n_th, endpoint=False)
    th = np.radians(th_deg)
    hem = hem_fn(th_deg)
    D = dir_theta(th)
    P = np.zeros((n_rows, n_th, 3))
    prev_r = None
    prev_z = None
    phase = rng.uniform(0, 2 * math.pi)
    fn = lambda Q: fields.lower(Q) - off  # noqa: E731
    for j in range(n_rows):
        t = j / (n_rows - 1)
        z = z_top + (hem - z_top) * t ** 0.95
        O = np.stack([np.zeros(n_th), np.full(n_th, 0.01 * S), z], axis=-1)
        r = cast_last(fn, O, D, 0.5 * S)
        if prev_r is not None:
            r = np.maximum(r, prev_r + flare * (prev_z - z))
        if convex:  # M1-CHR-15: below z0, blending in by z1, span the gap between the legs (the skirt panels carry it)
            k = np.clip((convex[0] - z) / max(convex[0] - convex[1], 1e-9), 0.0, 1.0)
            if (k > 0.0).any():
                r = r + (convex_radii(r, D) - r) * (k * k * (3.0 - 2.0 * k))
        prev_r, prev_z = r, z
        amp = fold_amp * S * t ** 1.3
        rr = r * (1.0 + 0) + amp * (np.sin(folds * th + phase) + 0.4 * np.sin(2.3 * folds * th + 1.7 * phase))
        P[j] = O + D * rr[:, None]
    centre = np.array([0.0, 0.01 * S, 0.0])
    cols = [[(t ** 1.2, t, (i / n_th * 3.0) % 1.0, 0.15 * t) for i in range(n_th)] for t in np.linspace(0, 1, n_rows)]
    _panel(part, P, rect, cols, True, back_inset, centre)
    return part


def sash(fields: Fields, skirt_part: Part, vest_part: Part, rect, rect_tails, width: float, z_c: float,
         seed: int) -> Part:
    part = Part("Sash")
    part._mat = "cloth"
    lm = fields.lm
    S = lm.S
    rng = np.random.default_rng(seed)
    n = 48
    th = np.radians(np.linspace(0.0, 360.0, n, endpoint=False))
    D = dir_theta(th)
    # the band sits over whatever is outermost at the waist (vest hem and skirt top)
    outer = np.concatenate([skirt_part.varr(), vest_part.varr()])
    rows = 3
    P = np.zeros((rows, n, 3))
    for j in range(rows):
        z = z_c + width * (0.5 - j / (rows - 1))
        near = outer[np.abs(outer[:, 2] - z) < 0.025 * S]
        q = near - np.array([0.0, 0.01 * S, 0.0])
        ang = np.arctan2(q[:, 0], -q[:, 1])
        rad = np.hypot(q[:, 0], q[:, 1])
        r = np.zeros(n)
        for i in range(n):
            dif = np.abs(np.angle(np.exp(1j * (ang - th[i]))))
            m = dif < 0.2
            r[i] = rad[m].max() if m.any() else 0.13 * S
        r = r + 0.004 * S
        O = np.stack([np.zeros(n), np.full(n, 0.01 * S), np.full(n, z)], axis=-1)
        P[j] = O + D * r[:, None]
    centre = np.array([0.0, 0.01 * S, 0.0])
    _panel(part, P, rect, [[(0.0, 0.0, 0.0, 0.0)] * n] * rows, True, 0.0012 * S, centre)
    # the knot on the right hip, and two tails to mid-thigh
    th_k = math.radians(258.0)
    dk = np.array([math.sin(th_k), -math.cos(th_k), 0.0])
    i_k = int(round(258.0 / 360.0 * n)) % n
    knot_c = P[1, i_k] + dk * 0.014 * S
    tails = Part("SashTails")
    tails._mat = "cloth"
    for k, (dth, length) in enumerate(((-9.0, 0.34), (7.0, 0.29))):
        thk = math.radians(258.0 + dth)
        dd = np.array([math.sin(thk), -math.cos(thk), 0.0])
        side = np.cross(np.array([0.0, 0.0, 1.0]), dd)
        rows_t = 12
        Q = np.zeros((rows_t, 3, 3))
        for j in range(rows_t):
            t = j / (rows_t - 1)
            z = knot_c[2] - 0.02 * S - length * S * t
            # sit outside the skirt at this height
            near = outer[np.abs(outer[:, 2] - z) < 0.03 * S]
            q = near - np.array([0.0, 0.01 * S, 0.0])
            ang = np.arctan2(q[:, 0], -q[:, 1])
            m = np.abs(np.angle(np.exp(1j * (ang - thk)))) < 0.25
            rad = (np.hypot(q[m, 0], q[m, 1]).max() if m.any() else 0.15 * S) + 0.010 * S + 0.006 * S * k
            c = np.array([0.0, 0.01 * S, z]) + dd * rad
            w = (0.055 - 0.012 * t) * S
            sway = side * (0.010 * S * math.sin(2.2 * t + k))
            for i, f in enumerate((-1.0, 0.0, 1.0)):
                Q[j, i] = c + side * w * f + sway
        cols = [[(t, t, 0.37 * k + 0.2, 0.2 * t)] * 3 for t in np.linspace(0, 1, rows_t)]
        _panel(tails, Q, (rect_tails[0] + (rect_tails[2] - rect_tails[0]) * 0.5 * k, rect_tails[1],
                          rect_tails[0] + (rect_tails[2] - rect_tails[0]) * 0.5 * (k + 1), rect_tails[3]),
               cols, False, 0.0012 * S, np.array([0.0, 0.01 * S, 0.0]))
    # knot: a squashed ball of the same silk
    from asha_mesh import uv_sphere
    kn = Part("SashKnot")
    uv_sphere(kn, knot_c, np.array([0.030, 0.022, 0.026]) * S, 12, 7, "cloth", axis_fwd=dk,
              uv_rect=(rect[0], rect[1], rect[2], rect[1] + 0.05), tags=TAG_CLOTH)
    kn.C = [(0.0, 0.0, 0.0, 0.0)] * len(kn.V)
    part.extend(tails)
    part.extend(kn)
    _ = rng
    return part


# ---------------------------------------------------------------------------------------------
# Verse-sleeve
# ---------------------------------------------------------------------------------------------
def verse_sleeve(fields: Fields, length: float, cuff_w: float, n_around: int = 32, n_rings: int = 40) -> Part:
    """Gauze sleeve on the right arm, a hanging bag under the arm that trails to the knee.
    UV.y = arc length along the hanging edge / length (shoulder 0 -> cuff tip 1); UV.x around, with
    the outer face (away from the body, 220 deg) at u in [0.2, 0.81]."""
    part = Part("VerseSleeve")
    lm = fields.lm
    S = lm.S
    sh, el, wr = lm.side_pt("shoulder", "R"), lm.side_pt("elbow", "R"), lm.side_pt("wrist", "R")
    a_up = (el - sh) / np.linalg.norm(el - sh)
    seam = sh + a_up * 0.035 * S + np.array([0.0, 0.0, 0.012 * S])
    path = np.concatenate([np.linspace(seam, el, 16, endpoint=False), np.linspace(el, wr - (wr - el) * 0.06, 24)])
    z_knee = float(lm.side_pt("knee", "R")[2])
    arm_fn = lambda Q: fields.body.regions["arm_R"].sdf(Q) - 0.016 * S  # noqa: E731
    up = np.array([0.0, 0.0, 1.0])
    rings = []
    s_list = np.linspace(0.0, 1.0, n_rings)
    idx = np.linspace(0, len(path) - 1, n_rings)
    for k, s in enumerate(s_list):
        c = path[int(round(idx[k]))]
        i1 = min(int(round(idx[k])) + 1, len(path) - 1)
        i0 = max(int(round(idx[k])) - 1, 0)
        ax = path[i1] - path[i0]
        ax /= np.linalg.norm(ax)
        e1 = up - (up @ ax) * ax
        e1 /= np.linalg.norm(e1)  # "up" around the arm
        e2 = np.cross(ax, e1)  # front/back around the arm
        ang = 2 * math.pi * np.arange(n_around) / n_around  # 0 = top of the arm
        D = np.cos(ang)[:, None] * e1 + np.sin(ang)[:, None] * e2
        O = np.repeat(c[None, :], n_around, axis=0)
        r = cast_last(arm_fn, O, D, 0.15 * S)
        r = np.maximum(r, 0.045 * S)
        P = O + D * r[:, None]
        # the bag: the lower half of the ring drops toward the knee and widens front-back
        down = np.clip(-np.cos(ang), 0.0, 1.0) ** 0.8
        drop_to = c[2] + (z_knee + 0.02 * S - c[2]) * (s ** 1.15)
        drop = np.maximum(c[2] - 0.05 * S - drop_to, 0.0) * smooth(0.06, 0.35, s)
        P[:, 2] -= drop * down
        widen = (cuff_w * 0.5 - 0.05 * S) * smooth(0.1, 1.0, s) * down * np.sin(ang)
        P += np.outer(widen, e2) * 0.6
        # gentle folds
        P += np.outer(0.006 * S * s * np.sin(5 * ang + 3 * s), np.array([1.0, 0.0, 0.0])) * down[:, None]
        rings.append(P)
    R = np.stack(rings)  # (n_rings, n_around, 3)
    # UV.y = height below the shoulder seam (seam 0 -> cuff tip 1): bands stack down the hanging
    # sheet as horizontal stripes (asha.md §3.1) and the S8 dissolve runs from the cuff upward
    z_seam = float(seam[2])
    z_tip = float(R[:, :, 2].min())
    vv = np.clip((z_seam - R[:, :, 2]) / (z_seam - z_tip), 0.0, 1.0)
    cols = [[(s, s, 0.3, 0.8 * s)] * n_around for s in s_list]
    # u = 0 at the top of the arm; the hanging sheets (front and back) and the bottom are u 0.2-0.8
    grid(part, R, "cloth_sleeve", colors=cols, tags=TAG_CLOTH, closed_u=True,
         uv_fn=lambda j, i: (i / n_around, float(vv[j, i % n_around])))
    part.sleeve_length = z_seam - z_tip
    _ = length
    return part


def smooth(e0: float, e1: float, x: float) -> float:
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------------------------------------
# Wraps and sandals
# ---------------------------------------------------------------------------------------------
def limb_wrap(fields: Fields, region: str, a: np.ndarray, b: np.ndarray, off: float, rect, name: str,
              n_around: int = 20, rows: int = 8) -> Part:
    part = Part(name)
    part._mat = "cloth"
    ax = (b - a) / np.linalg.norm(b - a)
    ref = np.array([0.0, 0.0, 1.0]) if abs(ax[2]) < 0.9 else np.array([0.0, -1.0, 0.0])
    e1 = ref - (ref @ ax) * ax
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(ax, e1)
    ang = 2 * math.pi * np.arange(n_around) / n_around
    D = np.cos(ang)[:, None] * e1 + np.sin(ang)[:, None] * e2
    fn = lambda Q: fields.body.regions[region].sdf(Q) - off  # noqa: E731
    P = np.zeros((rows, n_around, 3))
    for j in range(rows):
        c = a + (b - a) * (j / (rows - 1))
        O = np.repeat(c[None, :], n_around, axis=0)
        r = cast_last(fn, O, D, 0.12 * fields.lm.S)
        P[j] = O + D * r[:, None]
    _panel(part, P, rect, None, True, None, a)
    return part


def sandal(fields: Fields, side: str, rect) -> Part:
    """A woven-palm sole under the foot and two straps (instep and toe), asha.md §4.1 #8."""
    part = Part(f"Sandal{side}")
    part._mat = "cloth"
    lm = fields.lm
    S = lm.S
    hb, tt = lm.side_pt("heel_back", side), lm.side_pt("toe_tip", side)
    fwd = (tt - hb) / np.linalg.norm(tt - hb)
    lat = np.cross(fwd, np.array([0.0, 0.0, 1.0]))
    fn = fields.region(f"foot_{side}")
    n = 20
    outline = []
    c0 = (hb + tt) * 0.5
    c0[2] = 0.012 * S
    for i in range(n):
        a = 2 * math.pi * i / n
        d = fwd * math.cos(a) + lat * math.sin(a)
        r = cast_last(fn, c0[None, :], d[None, :], 0.18 * S)[0]
        outline.append(c0 + d * (r + 0.004 * S))
    outline = np.array(outline)
    top = outline.copy()
    top[:, 2] = 0.010 * S
    bot = outline.copy()
    bot[:, 2] = -0.001
    P = np.stack([top, bot])
    _panel(part, P, (rect[0], rect[1], rect[2], rect[1] + 0.05), None, True, None, c0)
    # top and bottom caps (fans)
    ct = part.add_v(np.array([c0[0], c0[1], 0.010 * S]), tag=TAG_CLOTH)
    cb = part.add_v(np.array([c0[0], c0[1], -0.001]), tag=TAG_CLOTH)
    base = len(part.V) - 2 - 2 * n
    for i in range(n):
        i2 = (i + 1) % n
        part.add_f((ct, base + i2, base + i), [(rect[0], rect[1] + 0.1)] * 3, "cloth")
        part.add_f((cb, base + n + i, base + n + i2), [(rect[0], rect[1] + 0.1)] * 3, "cloth")
    for u in (0.48, 0.80):
        c = hb + (tt - hb) * u + np.array([0.0, 0.0, 0.02 * S])
        strap = limb_wrap(fields, f"foot_{side}", c - fwd * 0.012 * S, c + fwd * 0.012 * S, 0.0025 * S,
                          (rect[0], rect[1] + 0.1, rect[2], rect[3]), "strap", n_around=16, rows=2)
        part.extend(strap)
    return part


# ---------------------------------------------------------------------------------------------
def build_costume(body, params: dict) -> dict[str, Part]:
    lm = body.lm
    S = lm.S
    fields = Fields(body)
    chart = TorsoChart(lm)
    z_waist = float(lm.P("waist")[2])
    out: dict[str, Part] = {}
    # 1. under-bodice: waist to just above the bust, under the vest
    out["Bodice"] = torso_panel(fields, chart, "Bodice", "cloth", ATLAS["bodice"], z_waist - 0.02 * S,
                                lambda th: bodice_top(lm, th), 0.003 * S, 40, 8,
                                None)
    # 5. vest
    vest_hem = z_waist - 0.035 * S
    out["Vest"] = torso_panel(fields, chart, "Vest", "cloth", ATLAS["vest"], vest_hem,
                              lambda th: vest_top(lm, chart, th), 0.0065 * S, 56, 15, 0.0025 * S)
    out["Collar"] = collar(fields, ATLAS["collar"], float(params["collar_height_m"]) * S)
    # 2-3. skirts: asymmetric hem, high on the left (mid-calf) and low on the right (ankle)
    hl, hr = float(params["hem_left_m"]) * S, float(params["hem_right_m"]) * S

    def hem_outer(th_deg: np.ndarray) -> np.ndarray:
        return 0.5 * (hl + hr) + 0.5 * (hl - hr) * np.sin(np.radians(th_deg))

    # big17 review (stiff faceted panels): denser rings and rows, so the 16 panel chains bend the cloth smoothly
    out["SkirtOuter"] = skirt(fields, "SkirtOuter", ATLAS["skirt_outer"], z_waist - 0.03 * S, hem_outer, 0.008 * S,
                              SKIRT_OUTER_GRID[0], SKIRT_OUTER_GRID[1], 11, 0.012, 0.16, 0.0015 * S, int(params["seed"]))
    out["SkirtInner"] = skirt(fields, "SkirtInner", ATLAS["skirt_inner"], float(lm.P("crotch")[2]) - 0.05 * S,
                              lambda th: np.full_like(th, UNDERSKIRT_HEM * S), 0.004 * S, SKIRT_INNER_GRID[0],
                              SKIRT_INNER_GRID[1], 9, 0.008, 0.13,
                              0.0012 * S, int(params["seed"]) + 1, convex=(z_waist, z_waist - 0.01 * S))
    # 4. sash
    out["Sash"] = sash(fields, out["SkirtOuter"], out["Vest"], ATLAS["sash"], ATLAS["sash_tails"],
                       float(params["sash_width_m"]) * S, z_waist - 0.02 * S, int(params["seed"]) + 2)
    # 6. verse-sleeve
    out["VerseSleeve"] = verse_sleeve(fields, float(params["sleeve_length_m"]) * S,
                                      float(params["sleeve_cuff_width_m"]) * S)
    # 7. wraps
    el, wr = lm.side_pt("elbow", "L"), lm.side_pt("wrist", "L")
    wraps = limb_wrap(fields, "arm_L", wr - (wr - el) * 0.02, wr + (el - wr) * 0.5, 0.0025 * S,
                      (ATLAS["wraps"][0], ATLAS["wraps"][1], ATLAS["wraps"][2], ATLAS["wraps"][1] + 0.1), "WrapArm")
    for sd in ("L", "R"):
        an = lm.side_pt("ankle", sd)
        kn = lm.side_pt("knee", sd)
        ankle = limb_wrap(fields, f"leg_{sd}", an + (kn - an) * 0.02, an + (kn - an) * 0.13, 0.0025 * S,
                          (ATLAS["wraps"][0], ATLAS["wraps"][1] + 0.1, ATLAS["wraps"][2], ATLAS["wraps"][3]),
                          f"WrapAnkle{sd}", rows=4)
        wraps.extend(ankle)
    out["Wraps"] = wraps
    sandals = Part("Sandals")
    for sd in ("L", "R"):
        sandals.extend(sandal(fields, sd, ATLAS["sandals"]))
    out["Sandals"] = sandals
    for p in out.values():
        if not p.C:
            p.C = [(0.0, 0.0, 0.0, 0.0)] * len(p.V)
        elif len(p.C) < len(p.V):
            p.C = p.C + [(0.0, 0.0, 0.0, 0.0)] * (len(p.V) - len(p.C))
    return out


KEEP_ABOVE_KNEE = 0.16  # m (at s = 1) of thigh kept above the knee joint under the skirts
SKIRT_CUT_BELOW_WAIST = 0.08  # m (at s = 1): the body under the skirts is cut only above this far below the waist


def z_keep_top(lm) -> float:
    """Height of the cut edge of the hidden thighs under the skirts (coverage)."""
    return max(float(lm.side_pt("knee", sd)[2]) for sd in ("L", "R")) + KEEP_ABOVE_KNEE * lm.S


def coverage(body, params: dict, V: np.ndarray, reg: np.ndarray, under_skirt: bool = False) -> np.ndarray:
    """True for body vertices hidden under opaque clothing (with a margin), asha.md §8.1. With `under_skirt`, the
    body kept under the skirts instead (M1-CHR-15: the skirt panels tent away from the legs, so the legs and hips
    below the panels' pivot stay whole; build_asha decimates them, as nothing sees them through the cloth)."""
    lm = body.lm
    S = lm.S
    chart = TorsoChart(lm)
    z_waist = float(lm.P("waist")[2])
    th, H = chart.H_of(V)
    th_deg = np.degrees(th)
    m = 0.03 * S
    torso = reg == "torso"
    vest = torso & (H > z_waist - 0.035 * S + m) & (H < vest_top(lm, chart, th_deg) - m)
    bodice = torso & (V[:, 2] > z_waist - 0.02 * S + m) & (V[:, 2] < bodice_top(lm, th_deg) - m)
    hl, hr = float(params["hem_left_m"]) * S, float(params["hem_right_m"]) * S
    hem = 0.5 * (hl + hr) + 0.5 * (hl - hr) * np.sin(th)
    legs = (reg == "leg_L") | (reg == "leg_R") | torso
    # M1-CHR-14: the knees and shins stay under the skirts (a stride or a kneel carries them out through the
    # cloth, and a deleted shin left a floating foot); only the thighs and hips are cut
    z_keep = z_keep_top(lm)
    lo = np.maximum(np.maximum(hem, 0.065 * S) + 0.045 * S, z_keep)
    skirt = legs & (V[:, 2] < z_waist - 0.03 * S - m * 0.5) & (V[:, 2] > lo)
    # M1-CHR-15: only the band above the skirt panels' pivot is cut (a cut edge below it showed through the open hem
    # when a panel tented away from a raised thigh)
    cut = skirt & (V[:, 2] > z_waist - SKIRT_CUT_BELOW_WAIST * S)
    if under_skirt:
        return skirt & ~cut & ~(vest | bodice)
    return vest | bodice | cut
