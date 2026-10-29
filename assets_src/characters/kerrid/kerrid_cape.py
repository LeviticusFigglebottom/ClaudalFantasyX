"""Kerrid's rain-cape of layered woven palm fibre (no bpy), kerrid.md §2, §4.1 #6, #7, #10 and §9.

Pattern as data (asha.md §9.2). Each tier is a **woven base mat** (an opaque shell with a back layer, on the costume
atlas's `cape_mat` island, material `cape_mat`) with **rows of fibre card strips** hanging from it (material `fibre`,
the hero-owned strand atlas `kerrid_fibre.png` on the hair shader: the sun-bleached tips are its root-to-tip colour).
Rows overlap like thatch, each covering the base of the row below. A strip is two cards: one lying along the mat and
a fin standing out from its centre line at `strip_cross_deg` (70 degrees), so the fringe has depth from every angle;
the fin only stands *out* from the mat, never in toward the body. Placement, lengths, widths and tilts come from one
seed.

* **Tier 1, the yoke**: the shoulder tier, open at the front. Its mat rides the upper torso and the shoulder caps (the
  torso field plus the caps, as Asha's vest), its neck edge at the base of the neck and `yoke_neck_clear_m` (25 mm) or
  more off the neck; the strips over the shoulder drape over the deltoid to 12 cm below the shoulder joint (in the
  A-pose rest they lie along the abducted arm). build_kerrid weights it on DEF-spine.003/.004 and the clavicles only,
  the lowest 5 cm of the strands over the deltoid 50% on the upper arm.
* **Tier 2**: from the shoulder blades to the waist, back only, its edges at the mid-axillary line (`tier2_reach_deg`
  either side of the back), behind the arms' swing plane.
* **Tier 3**: from the waist to the backs of the knees (the hem `tier3_hem_above_floor_m` = 52 cm), **split at the
  centre into two halves** that build_kerrid hands over from the hips to their own leg (Ysolde's panel weights, the
  left/right blend only across the 6 cm centre band) plus three panel bones down each half. Each half's rows are a
  straight column (Ysolde's ring_radii: every row at least as wide as the one above).

Strips near the cleaver's line across the back (`flat_fn`) lie flat (no fin): the blade presses the fibre down, and
the cleaver stays 12 mm off the cape's outer surface (kerrid_props, build_kerrid).

**Wet state** (Ch8 B15 to the Ch9 dawn road): `wet_deltas` is the `cape_wet` shape key: every strip vertex moves down
its strand by `wet_longer_m` x t and in toward the mat by `wet_closer_m` x t (t = 0 at the root, 1 at the tip); the
mats do not move. The scene sets it with the `cape_mat_wet` / `fibre_wet` materials.

Vertex colour = wind (R primary, G ripple, B phase, A flutter): the strands flutter toward the tips. Deterministic.
"""
from __future__ import annotations

import math

import numpy as np

import ysolde_costume as YC
from asha_costume import Fields, TorsoChart, _grid_normals, _outward, _panel, cast_last, dir_theta
from asha_mesh import Part, grid

FIB_COLS = 8  # kerrid_fibre.png: columns of strand bundles, V root (0) -> tip (1)
FIB_INSET = 0.02
SEG = 3  # segments along a card
TIER3_ROWS = 12
YOKE_ROWS = 10
YOKE_TOP_STEPS = 12  # bisection steps on the yoke's neck edge height
TIER2_ROWS = 8
TAG_FIBRE = 43


def mat_rects(rect) -> dict:
    """The cape mats' islands inside the costume atlas's `cape_mat` rect."""
    u0, v0, u1, v1 = rect
    du, dv = u1 - u0, v1 - v0
    return {"yoke": (u0, v0, u1, v0 + 0.40 * dv),
            "tier2": (u0, v0 + 0.40 * dv, u0 + 0.5 * du, v1),
            "tier3_L": (u0 + 0.5 * du, v0 + 0.40 * dv, u0 + 0.75 * du, v1),
            "tier3_R": (u0 + 0.75 * du, v0 + 0.40 * dv, u1, v1)}


def body_field(body):
    """The union of the body's regions (the strands drape over all of them)."""
    regs = [body.regions[n].sdf for n in ("torso", "arm_L", "arm_R", "leg_L", "leg_R", "head")]

    def f(P: np.ndarray) -> np.ndarray:
        d = regs[0](P)
        for r in regs[1:]:
            d = np.minimum(d, r(P))
        return d

    return f


def _grad(fn, P: np.ndarray, e: float = 4e-4) -> np.ndarray:
    g = np.zeros_like(P)
    for k in range(3):
        d = np.zeros(3)
        d[k] = e
        g[:, k] = fn(P + d) - fn(P - d)
    return g / np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-12)


def _push_out(fn, P: np.ndarray, clear: float, iters: int = 4) -> np.ndarray:
    Q = P.copy()
    for _ in range(iters):
        d = fn(Q) - clear
        bad = d < 0
        if not bad.any():
            break
        Q[bad] = Q[bad] - _grad(fn, Q[bad]) * d[bad][:, None]
    return Q


class Mat:
    """A mat grid P[j, i] (rows top -> bottom) with outward normals, sampled bilinearly at (row, column) fractions."""

    def __init__(self, P: np.ndarray, centre: np.ndarray) -> None:
        self.P = P
        self.N = _outward(P, _grid_normals(P, False), centre)

    def at(self, fr: float, fc: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        nj, ni = self.P.shape[:2]
        y = fr * (nj - 1)
        j0 = min(int(math.floor(y)), nj - 2)
        a = y - j0
        x = np.clip(fc, 0.0, 1.0) * (ni - 1)
        i0 = np.minimum(np.floor(x).astype(int), ni - 2)
        b = (x - i0)[:, None]

        def bil(G):
            top = G[j0, i0] * (1 - b) + G[j0, i0 + 1] * b
            bot = G[j0 + 1, i0] * (1 - b) + G[j0 + 1, i0 + 1] * b
            return top * (1 - a) + bot * a

        n = bil(self.N)
        return bil(self.P), n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)

    def row_length(self, fr: float) -> float:
        p, _ = self.at(fr, np.linspace(0.0, 1.0, 64))
        return float(np.linalg.norm(np.diff(p, axis=0), axis=1).sum())


# ---------------------------------------------------------------------------------------------
# Mats
# ---------------------------------------------------------------------------------------------
def yoke_mat(fields: Fields, chart: TorsoChart, cp: dict, rect) -> tuple[Part, Mat]:
    """The yoke's base mat over the upper torso and the shoulder caps, open at the front (kerrid.md §4.1 #6)."""
    lm = fields.lm
    S = lm.S
    op = float(cp["yoke_front_open_deg"])
    th_deg = np.linspace(op, 360.0 - op, 46)
    a = np.abs(((th_deg + 180.0) % 360.0) - 180.0)
    neck = chart.z_sh + math.radians(50) * chart.k
    notch = float(lm.P("notch")[2])
    sh_z = float(lm.P("shoulder")[2])
    H_top = neck + 0.0 * a
    H_bot = np.interp(a, [op, 50.0, 78.0, 92.0, 110.0, 140.0, 180.0],
                      [notch - 0.19 * S, notch - 0.15 * S, sh_z + 0.005 * S, sh_z + 0.015 * S, sh_z - 0.02 * S,
                       chart.z_sh - 0.10 * S, chart.z_sh - 0.11 * S])
    clear = float(cp["yoke_neck_clear_m"]) * S + 0.004 * S
    side = np.abs(np.sin(np.radians(th_deg)))
    P = np.zeros((YOKE_ROWS, len(th_deg), 3))
    th = np.radians(th_deg)

    def row_at(H: np.ndarray, t: float) -> np.ndarray:
        # off the neck at the top; standing off the shoulder caps (the yoke's bulk) toward their middle
        off = clear * (1.0 - t) ** 2 + (0.016 + 0.016 * side ** 3 * math.sin(math.pi * min(t * 1.2, 1.0))) * S * (
            1.0 - (1.0 - t) ** 2)
        off = np.maximum(off, 0.014 * S)
        O, D = chart.rays(th, H)
        r = np.array([cast_last(lambda Q, o=o: fields.upper(Q) - o, O[i:i + 1], D[i:i + 1], 0.4 * S)[0]
                      for i, o in enumerate(off)])
        return O + D * r[:, None]

    # the neck edge: each column's top lowered until it sits `yoke_top_below_chin_m` under the chin (no high collar,
    # kerrid.md §4.1 #6); bisection on the chart height, never above the base neck line
    z_top = float(lm.P("chin")[2]) - float(cp["yoke_top_below_chin_m"]) * S
    lo, hi = np.minimum(H_bot, chart.z_sh), H_top.copy()
    for _ in range(YOKE_TOP_STEPS):
        mid = 0.5 * (lo + hi)
        above = row_at(mid, 0.0)[:, 2] > z_top
        hi = np.where(above, mid, hi)
        lo = np.where(above, lo, mid)
    H_top = lo
    for j in range(YOKE_ROWS):
        t = j / (YOKE_ROWS - 1)
        P[j] = row_at(H_top + (H_bot - H_top) * t, t)
    # the neck edge and the row under it: never nearer the neck than `clear` (the torso field includes the neck)
    for j in range(3):
        P[j] = _push_out(fields.body.regions["torso"].sdf, P[j], clear * (1.0 - 0.15 * j))
    part = Part("CapeYoke")
    part._mat = "cape_mat"
    centre = np.array([0.0, chart.y_axis, 0.0])
    _panel(part, P, rect, _wind_rows(YOKE_ROWS, len(th_deg), 0.03), False, 0.002 * S, centre)
    part.grid_P = P
    return part, Mat(P, centre)


def tier2_mat(fields: Fields, chart: TorsoChart, cp: dict, rect) -> tuple[Part, Mat]:
    """Tier 2: the shoulder blades to the waist, back only, to the mid-axillary lines."""
    lm = fields.lm
    S = lm.S
    reach = float(cp["tier2_reach_deg"])
    th_deg = np.linspace(180.0 - reach, 180.0 + reach, 30)
    z_waist = float(lm.P("waist")[2])
    P = np.zeros((TIER2_ROWS, len(th_deg), 3))
    th = np.radians(th_deg)
    for j in range(TIER2_ROWS):
        t = j / (TIER2_ROWS - 1)
        H = np.full(len(th), chart.z_sh - 0.035 * S + (z_waist - 0.01 * S - chart.z_sh + 0.035 * S) * t)
        O, D = chart.rays(th, H)
        r = cast_last(lambda Q: fields.upper(Q) - 0.020 * S, O, D, 0.4 * S)
        P[j] = O + D * r[:, None]
    part = Part("CapeTier2")
    part._mat = "cape_mat"
    centre = np.array([0.0, chart.y_axis, 0.0])
    _panel(part, P, rect, _wind_rows(TIER2_ROWS, len(th_deg), 0.04), False, 0.002 * S, centre)
    part.grid_P = P
    return part, Mat(P, centre)


def tier3_halves(fields: Fields, cp: dict, rects: dict, outer: np.ndarray) -> tuple[dict, dict, np.ndarray]:
    """Tier 3: the waist to the backs of the knees, split at the centre into two halves (open panels over the back of
    each leg); each row at least as wide as the one above it, and over the smock's skirt."""
    lm = fields.lm
    S = lm.S
    z_waist = float(lm.P("waist")[2])
    z_hem = float(cp["tier3_hem_above_floor_m"]) * S
    z_rows = YC.panel_rows(z_waist - 0.02 * S, z_hem, TIER3_ROWS)
    th_ring, R = YC.ring_radii(fields, z_rows)
    # clear of the smock's skirt and the trousers under it
    for j, z in enumerate(z_rows):
        near = outer[np.abs(outer[:, 2] - z) < 0.03 * S]
        if len(near):
            q = near - np.array([0.0, 0.01 * S, 0.0])
            ang = np.degrees(np.arctan2(q[:, 0], -q[:, 1])) % 360.0
            rad = np.hypot(q[:, 0], q[:, 1])
            for i, a in enumerate(th_ring):
                m = np.abs(((ang - a + 180.0) % 360.0) - 180.0) < 8.0
                if m.any():
                    R[j, i] = max(R[j, i], float(rad[m].max()) + 0.006 * S - 0.022 * S)
        if j:
            R[j] = np.maximum(R[j], R[j - 1])
    ring = (th_ring, R)
    reach = float(cp["tier3_reach_deg"])
    gap = 0.5 * float(cp["tier3_split_gap_deg"])
    out, mats = {}, {}
    seed = int(cp["seed"])
    for k, (name, a, b) in enumerate((("CapeTier3L", 180.0 - reach, 180.0 - gap), ("CapeTier3R", 180.0 + gap,
                                                                                    180.0 + reach))):
        p = YC.panel(fields, name, rects["tier3_L" if k == 0 else "tier3_R"], np.linspace(a, b, 16), z_rows, ring,
                     0.024 * S, seed + 7 + k, fold_amp=0.002)
        p._mat = "cape_mat"
        p.M = ["cape_mat"] * len(p.M)
        out[name] = p
        mats[name] = Mat(p.grid_P, np.array([0.0, 0.01 * S, 0.0]))
    return out, mats, z_rows


def _wind_rows(n_rows: int, n_cols: int, amp: float, phase0: float = 0.0):
    return [[(amp * t * t, amp * t, (phase0 + i / n_cols * 3.0) % 1.0, 0.3 * amp * t) for i in range(n_cols)]
            for t in np.linspace(0.0, 1.0, n_rows)]


# ---------------------------------------------------------------------------------------------
# Strips
# ---------------------------------------------------------------------------------------------
class Strips:
    """The fibre cards of every tier as one Part, with per-vertex data build_kerrid and the wet shape need."""

    def __init__(self) -> None:
        self.part = Part("CapeFibre")
        self.tier: list[str] = []  # per vertex: "yoke", "tier2", "tier3"
        self.t: list[float] = []  # 0 at the root -> 1 at the tip
        self.tan: list[np.ndarray] = []  # down the strand
        self.nrm: list[np.ndarray] = []  # out from the mat
        self.root: list[np.ndarray] = []
        self.fin_faces: list[int] = []  # face indices of the fins (LOD1 drops most of them)
        self.row_last: list[bool] = []  # per face: on its tier's lowest row (LOD1 keeps those fins: the outline)
        self.n_strips = 0

    def add(self, pts: np.ndarray, nrm: np.ndarray, width: float, col: int, fin: bool, cross_deg: float,
            tier: str, last_row: bool, rng) -> None:
        part = self.part
        n = len(pts)
        T = np.gradient(pts, axis=0)
        T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
        side = np.cross(T, nrm)
        side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-12)
        s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
        s /= max(float(s[-1]), 1e-12)
        flutter = [(0.12 * t * t, 0.12 * t, float(rng.random()), 0.35 * t) for t in s]
        u0 = (col + FIB_INSET) / FIB_COLS
        u1 = (col + 1 - FIB_INSET) / FIB_COLS
        ca = math.cos(math.radians(cross_deg))
        sa = math.sin(math.radians(cross_deg))
        # card A: along the mat, a little wider toward the split tip
        P = np.zeros((n, 2, 3))
        for k in range(n):
            w = 0.5 * width * (1.0 + 0.15 * s[k])
            P[k, 0] = pts[k] - side[k] * w
            P[k, 1] = pts[k] + side[k] * w
        cols = [[flutter[k], flutter[k]] for k in range(n)]
        f0 = len(part.F)
        grid(part, P, "fibre", colors=cols, tags=TAG_FIBRE, uv_fn=lambda j, i: (u0 + (u1 - u0) * i, float(s[j])))
        for k in range(n):
            for _ in range(2):
                self._meta(tier, s[k], T[k], nrm[k], pts[0])
        self.row_last += [last_row] * (len(part.F) - f0)
        if fin:
            # card B: a fin from the centre line out at cross_deg to card A (outward only, never into the body)
            d = side * ca + nrm * sa
            d[:, 2] = np.minimum(d[:, 2], 0.0)  # outward, never up past the root (the yoke's top row over the shoulder)
            d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-12)
            Q = np.zeros((n, 2, 3))
            for k in range(n):
                Q[k, 0] = pts[k]
                Q[k, 1] = pts[k] + d[k] * 0.62 * width * (1.0 + 0.1 * s[k])
            ub0, ub1 = (u1, u0) if rng.random() < 0.5 else (u0, u1)
            f1 = len(part.F)
            grid(part, Q, "fibre", colors=cols, tags=TAG_FIBRE, uv_fn=lambda j, i: (ub0 + (ub1 - ub0) * i, float(s[j])))
            for k in range(n):
                for _ in range(2):
                    self._meta(tier, s[k], T[k], nrm[k], pts[0])
            self.fin_faces += list(range(f1, len(part.F)))
            self.row_last += [last_row] * (len(part.F) - f1)
        self.n_strips += 1

    def _meta(self, tier, t, tan, nrm, root) -> None:
        self.tier.append(tier)
        self.t.append(float(t))
        self.tan.append(tan)
        self.nrm.append(nrm)
        self.root.append(root)


def drape(root: np.ndarray, n0: np.ndarray, length: float, fn, clear: float, flare: float, hem_z: float | None,
          along: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """A strand's centre line from `root`: SEG steps down the surface (gravity in the tangent plane, a little flare
    out), each kept `clear` off the body field `fn`; it never goes below `hem_z`. `along`: a preferred direction
    (the yoke's strands over the shoulder follow the arm). Returns (points, outward normals)."""
    step = length / SEG
    pts = [root]
    nrms = [n0]
    g = np.array([0.0, 0.0, -1.0])
    p = root
    n = n0
    for _ in range(SEG):
        d = g - (g @ n) * n
        if along is not None:
            d = d + 0.8 * (along - (along @ n) * n)
        if np.linalg.norm(d) < 1e-3:
            d = np.array([n[0], n[1], 0.0])
        d = d / np.linalg.norm(d) + flare * n
        d[2] = min(d[2], 0.0)  # a strand hangs: never above its root (a shoulder-top normal points up)
        d /= np.linalg.norm(d)
        q = p + d * step
        if hem_z is not None and q[2] < hem_z:
            q[2] = hem_z
        q = _push_out(fn, q[None, :], clear)[0]
        gn = _grad(fn, q[None, :])[0]
        n = gn if np.isfinite(gn).all() and np.linalg.norm(gn) > 0.5 else n
        pts.append(q)
        nrms.append(n)
        p = q
    return np.array(pts), np.array(nrms)


def strip_rows(strips: Strips, mat: Mat, rows: list, cp: dict, rng, fn, clear: float, tier: str, flat_fn,
               hem_z: float | None = None, along_fn=None, lift: float = 0.004) -> None:
    """Rows of strips on `mat`: rows = [(row fraction, (length lo, hi), flare)], spaced 6-10 per 10 cm."""
    S = 1.0
    lo_n, hi_n = cp["strips_per_10cm"]
    wlo, whi = cp["strip_width_m"]
    cross = float(cp["strip_cross_deg"])
    for ri, (fr, (llo, lhi), flare) in enumerate(rows):
        L = mat.row_length(fr)
        cs = []
        c = rng.uniform(0.0, 0.5) * 0.1 / hi_n
        while c < L:
            cs.append(c / L)
            c += 0.1 / rng.uniform(lo_n, hi_n) * S
        cs = np.array(cs)
        roots, nrm = mat.at(fr, cs)
        for k in range(len(cs)):
            r0 = roots[k] + nrm[k] * lift
            length = rng.uniform(llo, lhi)
            along = along_fn(r0) if along_fn is not None else None
            pts, ns = drape(r0, nrm[k], length, fn, clear, flare, hem_z, along)
            col = int(rng.integers(0, FIB_COLS))
            fin = not flat_fn(r0)
            strips.add(pts, ns, rng.uniform(wlo, whi), col, fin, cross + rng.uniform(-8.0, 8.0), tier,
                       ri == len(rows) - 1, rng)


def build_cape(body, cp: dict, rect, smock_outer: np.ndarray, flat_fn=None) -> tuple[dict, Strips, dict]:
    """Returns ({mat name: Part}, strips, info). `flat_fn(p) -> bool`: no fin at a root near the cleaver's line."""
    lm = body.lm
    S = lm.S
    fields = Fields(body)
    chart = TorsoChart(lm)
    rects = mat_rects(rect)
    flat_fn = flat_fn or (lambda p: False)
    fn = body_field(body)
    rng = np.random.default_rng([int(cp["seed"]), 1])
    mats: dict[str, Part] = {}
    mats["CapeYoke"], m_yoke = yoke_mat(fields, chart, cp, rects["yoke"])
    mats["CapeTier2"], m_t2 = tier2_mat(fields, chart, cp, rects["tier2"])
    t3, m_t3, z_rows = tier3_halves(fields, cp, rects, smock_outer)
    mats.update(t3)
    strips = Strips()
    sh = {sd: lm.side_pt("shoulder", sd) for sd in ("L", "R")}
    el = {sd: lm.side_pt("elbow", sd) for sd in ("L", "R")}
    neck_clear = float(cp["yoke_neck_clear_m"]) * S

    def along_arm(p: np.ndarray) -> np.ndarray | None:
        sd = "L" if p[0] > 0 else "R"
        ax = el[sd] - sh[sd]
        ax /= np.linalg.norm(ax)
        lateral = (abs(p[0]) - (abs(sh[sd][0]) - 0.07 * S)) / (0.06 * S)
        if lateral <= 0.0:
            return None
        return ax * min(lateral, 1.0)

    hang = float(cp["yoke_hang_below_shoulder_m"]) * S
    # yoke: the neck edge row clears the neck by the mat's own standoff (the strands sit outside it)
    strip_rows(strips, m_yoke, [(0.0, (0.10, 0.15), 0.25), (0.33, (0.13, 0.19), 0.30), (0.62, (0.15, 0.21), 0.35),
                                (0.92, (hang + 0.06, hang + 0.10), 0.35)],
               cp, rng, fn, 0.024 * S, "yoke", flat_fn, along_fn=along_arm)
    strip_rows(strips, m_t2, [(0.0, (0.16, 0.22), 0.20), (0.34, (0.17, 0.23), 0.22), (0.68, (0.18, 0.24), 0.22)],
               cp, rng, fn, 0.022 * S, "tier2", flat_fn)
    hem = float(cp["tier3_hem_above_floor_m"]) * S
    for name, m in m_t3.items():
        strip_rows(strips, m, [(0.0, (0.16, 0.22), 0.15), (0.28, (0.17, 0.23), 0.15), (0.55, (0.16, 0.22), 0.15),
                               (0.80, (0.12, 0.16), 0.12)],
                   cp, rng, fn, 0.024 * S, "tier3", flat_fn, hem_z=hem + 0.004 * S)
    p = strips.part
    p.C = p.C + [(0.0, 0.0, 0.0, 0.0)] * (len(p.V) - len(p.C))
    for m in mats.values():
        if len(m.C) < len(m.V):
            m.C = m.C + [(0.0, 0.0, 0.0, 0.0)] * (len(m.V) - len(m.C))
    info = {"tier3_rows": z_rows, "tier3_mats": m_t3, "yoke": m_yoke, "tier2": m_t2, "neck_clear": neck_clear,
            "hem_z": hem}
    return mats, strips, info


def wet_deltas(strips: Strips, cp: dict, S: float) -> np.ndarray:
    """The `cape_wet` shape on the strips: down the strand by wet_longer x t, in toward the mat by wet_closer x t."""
    t = np.array(strips.t)[:, None]
    tan = np.array(strips.tan)
    nrm = np.array(strips.nrm)
    return t * (float(cp["wet_longer_m"]) * S * tan - float(cp["wet_closer_m"]) * S * nrm)
