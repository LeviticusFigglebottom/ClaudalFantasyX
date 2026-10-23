"""Asha's hair cards (no bpy), asha.md §5 and the hair contract in character_shading.md.

Black, very long hair parted on the left, drawn back into one three-strand side braid that starts
behind the left ear and falls over the front of the left shoulder to the hip:

* **Scalp**: three layers of cards (base, mid, top), rooted inside the hairline and traced over the
  scalp along a flow field toward the braid's gather point G behind the left ear; the part line
  on the left splits the flow. Cards lie in the scalp's tangent plane, lifted per layer.
* **Braid**: three strand tubes woven around a spine (x = A sin(t + phi), depth = B sin 2(t + phi)),
  the spine pushed clear of the body field; three shell clasps; a loose 9 cm tail of cards.
* **Flyaways** (thin, low alpha) at the crown and on the braid, and two uncut face-framing strands
  on the right temple.
* **Comb**: her mother's tortoiseshell comb behind the left ear.

UVs: the 2K atlas (asha_textures.hair_atlas) has 16 strand-clump columns; a card uses one column,
V root (0) -> tip (1). Vertex colour = wind weights (R primary, G secondary, B phase, A flutter;
character_wind.gdshaderinc); scalp cards are pinned (R = 0). Seeded, deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_mesh import Part, arclen, catmull_rom, frames_along, grid, tube

CLUMPS = 16
TAG_HAIR = 41


def hairline_v(lm, P: np.ndarray) -> np.ndarray:
    """Hairline height (head heights above the chin) for points P, by azimuth around the head axis.
    0 = front, +90 = the character's left. The front is 'moderately high' (asha.md §6.1)."""
    yc = lm.P("head_c")[1]
    phi = np.degrees(np.arctan2(P[:, 0], -(P[:, 1] - yc)))
    a = np.abs(phi)
    xs = [0, 30, 50, 66, 76, 84, 96, 112, 135, 160, 180]
    vs = [0.765, 0.752, 0.712, 0.655, 0.60, 0.585, 0.635, 0.50, 0.32, 0.25, 0.24]  # M1-CHR-03: front -0.035 h (donor forehead)
    # M1-CHR-04: a natural hairline is not a clean curve; it wanders by up to ~2.5 mm (cards, the
    # scalp underpaint and the skin maps all read this, so they agree)
    t = np.radians(phi)
    wander = 0.005 * np.sin(7.0 * t + 1.1) + 0.0035 * np.sin(13.0 * t + 2.3) + 0.002 * np.sin(29.0 * t + 0.4)
    return np.interp(a, xs, vs) + wander


def in_hair(lm, P: np.ndarray, margin_h: float = 0.0) -> np.ndarray:
    zc = lm.P("chin")[2]
    v = (P[:, 2] - zc) / lm.h
    return v > hairline_v(lm, P) + margin_h


class Scalp:
    """Projection onto the head field and its normals (head region only, no lids)."""

    def __init__(self, body) -> None:
        self.body = body
        self.reg = body.regions["head"]

    def sdf(self, P: np.ndarray) -> np.ndarray:
        return self.reg.sdf(P)

    def normal(self, P: np.ndarray) -> np.ndarray:
        e = 3e-4
        g = np.zeros_like(P)
        for i in range(3):
            d = np.zeros(3)
            d[i] = e
            g[:, i] = self.sdf(P + d) - self.sdf(P - d)
        return g / np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-12)

    def project(self, P: np.ndarray, lift: float = 0.0, iters: int = 4) -> np.ndarray:
        P = np.atleast_2d(np.asarray(P, dtype=float)).copy()
        for _ in range(iters):
            d = self.sdf(P) - lift
            P = P - self.normal(P) * d[:, None]
        return P


class MeshScalp:
    """M1-CHR-04: the same interface on the shipped head mesh itself. The anatomy field sits up to
    11 mm off the donor scalp (inside it at the temples, outside at the crown), so cards traced on
    the field sank into the skin in patches (the "blocks and gaps"). `nearest(P)` -> (closest point
    on the head skin, its smoothly interpolated normal) is supplied by the caller (build_asha: a
    BVH over the head triangles), which keeps this module free of bpy. `coarse` (the field Scalp)
    first brings far points (the root candidates, cast from inside the head) near the outer skin:
    from inside, the closest mesh point is often an eye socket or the mouth bag, not the scalp."""

    def __init__(self, nearest, coarse=None) -> None:
        self.nearest = nearest
        self.coarse = coarse

    def _near(self, P: np.ndarray) -> np.ndarray:
        if self.coarse is None:
            return P
        far = np.abs(self.coarse.sdf(P)) > 0.02
        if far.any():
            P = P.copy()
            P[far] = self.coarse.project(P[far])
        return P

    def sdf(self, P: np.ndarray) -> np.ndarray:
        P = np.atleast_2d(np.asarray(P, dtype=float))
        Q, N = self.nearest(P)
        return np.sum((P - Q) * N, axis=1)

    def normal(self, P: np.ndarray) -> np.ndarray:
        return self.nearest(np.atleast_2d(np.asarray(P, dtype=float)))[1]

    def project(self, P: np.ndarray, lift: float = 0.0, iters: int = 2) -> np.ndarray:
        P = self._near(np.atleast_2d(np.asarray(P, dtype=float)).copy())
        for _ in range(max(1, min(iters, 2))):
            Q, N = self.nearest(P)
            P = Q + N * lift
        return P


def _gather(lm) -> np.ndarray:
    if "hair_gather" in lm.pts:  # M1-CHR-03: set by bb_donor on the donor scalp (15 mm off it)
        return lm.pts["hair_gather"]
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    return np.array([lm.head_w * 0.40, yc + 0.30 * lm.h, zc + 0.37 * lm.h])


def _part_x(lm) -> float:
    return lm.head_w * 0.17  # parted on the left (+X)


def _flow_dir(lm, P: np.ndarray, N: np.ndarray, G: np.ndarray) -> np.ndarray:
    """Tangent flow toward the gather point, split at the part line."""
    yc = lm.P("head_c")[1]
    to_g = G - P
    d = to_g / np.maximum(np.linalg.norm(to_g, axis=1, keepdims=True), 1e-9)
    # near the part on the crown, comb away from it first (right of the part sweeps over the top)
    px = _part_x(lm)
    front = np.clip(-(P[:, 1] - yc) / (0.4 * lm.h), -1.0, 1.0)
    near = np.exp(-((P[:, 0] - px) / (0.09 * lm.h)) ** 2) * np.clip(front + 0.5, 0, 1)
    away = np.stack([np.sign(P[:, 0] - px), np.zeros(len(P)), np.zeros(len(P))], axis=1)
    back = np.array([0.0, 1.0, -0.2])
    d = d + away * near[:, None] * 0.5 + back * 0.35
    d = d - np.sum(d * N, axis=1, keepdims=True) * N
    return d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)


def _ribbon(part: Part, pts: np.ndarray, nrm: np.ndarray, width: float, slot: int, color_fn, taper: float = 0.45,
            v_range=(0.0, 1.0), mat: str = "hair") -> None:
    n = len(pts)
    T = np.gradient(pts, axis=0)
    T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
    side = np.cross(T, nrm)
    side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-12)
    P = np.zeros((n, 2, 3))
    cols = []
    for k in range(n):
        w = width * (1.0 - taper * k / (n - 1)) * 0.5
        P[k, 0] = pts[k] - side[k] * w
        P[k, 1] = pts[k] + side[k] * w
        t = k / (n - 1)
        cols.append([color_fn(t), color_fn(t)])
    u0, u1 = slot / CLUMPS, (slot + 1) / CLUMPS
    v0, v1 = v_range
    grid(part, P, mat, colors=cols, tags=TAG_HAIR,
         uv_fn=lambda j, i: (u0 + (u1 - u0) * i, v0 + (v1 - v0) * j / (n - 1)))


# Atlas columns (asha_textures.hair_atlas): 0-11 full clumps, 12-13 sparse breakup clumps (the top
# layer, so the outer surface is strands rather than a sheet), 14-15 hairline clumps whose strands
# start staggered over the first fifth of V (a soft, uneven hairline instead of a drawn edge).
SLOTS_FULL = 12
SLOTS_SPARSE = (12, 13)
SLOTS_HAIRLINE = (14, 15)
# Root candidates are cast from this far (head heights) out of the head centre, then projected: from
# outside the skull the closest scalp point is close to the radial one. M1-CHR-03 cast from 0.2 h,
# inside the head, so the projection slid to the sides and the crown got almost no roots.
ROOT_CAST_H = 0.6


def _trace(scalp, lm, roots: np.ndarray, length: np.ndarray, lift: float, G: np.ndarray, seg: int):
    """Paths of `seg` steps over the scalp along the flow field, stopping at the braid's gather."""
    s = lm.h / 0.222
    step = length / seg
    paths = [scalp.project(roots, lift)]
    alive = np.ones(len(roots), dtype=bool)
    stop = np.full(len(roots), seg)
    for k in range(seg):
        cur = paths[-1]
        N = scalp.normal(cur)
        fdir = _flow_dir(lm, cur, N, G)
        nxt = scalp.project(cur + fdir * step[:, None], lift, iters=3)
        near = np.linalg.norm(nxt - G, axis=1) < 0.03 * s
        newly = alive & near
        stop[newly] = k + 1
        alive &= ~near
        nxt = np.where(alive[:, None] | newly[:, None], nxt, cur)
        paths.append(nxt)
    return np.stack(paths, axis=1), stop


def _hairline_roots(scalp, lm, phi: np.ndarray, inside_h) -> np.ndarray:
    """Points on the scalp at azimuths `phi`, `inside_h` (scalar or per point) head heights above the hairline."""
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    hc = np.array([0.0, yc, zc + 0.55 * lm.h])
    d = np.stack([np.sin(phi), -np.cos(phi), np.zeros(len(phi))], axis=1)
    p = scalp.project(hc + d * ROOT_CAST_H * lm.h)
    for _ in range(10):
        v = hairline_v(lm, p) + inside_h
        dz = (zc + v * lm.h) - p[:, 2]
        p = scalp.project(p + np.stack([np.zeros(len(p)), np.zeros(len(p)), dz], axis=1))
    return p


def scalp_cards(lm, body, params: dict, rng: np.random.Generator, scalp=None) -> Part:
    """M1-CHR-04: a hairline row plus three layers, all on the head mesh (MeshScalp).

    * Hairline row: narrow cards rooted just inside the hairline on the soft-root atlas columns,
      so the hairline is a fringe of individual strands over the scalp underpaint, not a line.
    * Base, mid and top layers: narrower cards than M1-CHR-03 (9-16, 7-13, 5-10 mm against
      14-33 mm), more of them, lifted 1.2 / 2.6 / 4.0 mm; the top layer is half sparse clumps."""
    part = Part("HairScalp")
    scalp = scalp or Scalp(body)
    G = _gather(lm)
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    hc = np.array([0.0, yc, zc + 0.55 * lm.h])
    s = lm.h / 0.222
    seg = 8  # ~1.2-2.5 cm steps: the chord sag over the skull stays under the 1.2 mm base lift
    lim = math.pi * 0.86

    def emit(paths, stop, widths, slots, taper, v_range):
        for c in range(len(paths)):
            pts = paths[c, : stop[c] + 1]
            if len(pts) < 4:
                continue
            nrm = scalp.normal(pts)
            ph = float(rng.random())
            _ribbon(part, pts, nrm, float(widths[c]), int(slots[c]), lambda t, ph=ph: (0.0, 0.0, ph, 0.0),
                    taper=taper, v_range=v_range)

    # hairline row: evenly spread round the hairline with jitter, roots from 0.4 mm outside to 1.8 mm inside it
    n_hl = int(params.get("hairline_cards", 0))
    if n_hl:
        phi = np.linspace(-lim, lim, n_hl) + rng.uniform(-0.4, 0.4, n_hl) * (2 * lim / n_hl)
        roots = _hairline_roots(scalp, lm, np.sort(phi), rng.uniform(-0.002, 0.008, n_hl))
        length = rng.uniform(0.06, 0.11, n_hl) * s
        paths, stop = _trace(scalp, lm, roots, length, 0.0010 * s, G, 6)
        emit(paths, stop, rng.uniform(0.005, 0.009, n_hl) * s, rng.choice(SLOTS_HAIRLINE, n_hl), 0.3, (0.0, 0.8))
    layers = [(0.0012 * s, params["scalp_cards"][0], (0.009, 0.016)),
              (0.0026 * s, params["scalp_cards"][1], (0.007, 0.013)),
              (0.0040 * s, params["scalp_cards"][2], (0.005, 0.010))]
    for li, (lift, count, wr) in enumerate(layers):
        # roots: a fifth of the base layer along the hairline (behind the hairline row), the rest inside
        n_line = count // 5 if li == 0 else 0
        d_in = rng.normal(size=(count * 6, 3))
        d_in[:, 2] = np.abs(d_in[:, 2]) * 1.2 + 0.1
        d_in /= np.linalg.norm(d_in, axis=1, keepdims=True)
        p_in = scalp.project(hc + d_in * ROOT_CAST_H * lm.h)
        ok = in_hair(lm, p_in, 0.02) & (np.linalg.norm(p_in - G, axis=1) > 0.04 * s)
        p_in = p_in[ok][: count - n_line]
        if n_line:
            p_line = _hairline_roots(scalp, lm, np.sort(rng.uniform(-lim, lim, n_line)), 0.014)
            roots = np.concatenate([p_line, p_in])
        else:
            roots = p_in
        n = len(roots)
        length = rng.uniform(0.10, 0.19, n) * s
        length[:n_line] *= 1.2
        paths, stop = _trace(scalp, lm, roots, length, lift, G, seg)
        if li == 2:
            slots = np.where(rng.random(n) < 0.5, rng.choice(SLOTS_SPARSE, n), rng.integers(SLOTS_FULL, size=n))
        else:
            slots = rng.integers(SLOTS_FULL, size=n)
        slots[:n_line] = rng.choice(SLOTS_HAIRLINE, n_line)  # the base layer's hairline roots stay soft too
        emit(paths, stop, rng.uniform(*wr, n) * s, slots, 0.35, (0.0, 0.85))
    return part


def braid_spine(lm, body, params: dict) -> np.ndarray:
    s = lm.h / 0.222
    G = _gather(lm)
    zc = lm.P("chin")[2]
    notch = lm.P("notch")
    acro = lm.side_pt("acromion", "L")
    nip = lm.side_pt("nipple", "L")
    ctrl = np.array([
        G,
        G + np.array([0.004, 0.004, -0.05]) * s,
        np.array([acro[0] * 0.62, notch[1] + 0.01 * s, notch[2] + 0.03 * s]),
        np.array([acro[0] * 0.66, notch[1] - 0.05 * s, notch[2] - 0.06 * s]),
        np.array([nip[0] * 0.92, nip[1] - 0.04 * s, nip[2] - 0.05 * s]),
        np.array([nip[0] * 0.95, nip[1] - 0.02 * s, lm.P("waist")[2] - 0.02 * s]),
        np.array([nip[0] * 1.0, nip[1] + 0.0 * s, lm.P("waist")[2] - 0.25 * s]),
    ])
    C = catmull_rom(ctrl, 400)
    L = arclen(C)
    total = params["braid_length_m"] * s + params["tail_m"] * s
    C = C[L <= total]
    # keep it clear of the body (+ the vest on the chest) and the costume
    clear = 0.024 * s
    for _ in range(6):
        d = body.sdf(C)
        g = body.grad(C)
        g /= np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-9)
        push = np.maximum(clear - d, 0.0)
        C = C + g * push[:, None]
        # smooth
        C[1:-1] = 0.5 * C[1:-1] + 0.25 * (C[:-2] + C[2:])
    _ = zc
    return catmull_rom(C, 200)


def braid(lm, body, params: dict, rng: np.random.Generator) -> tuple[Part, Part, np.ndarray]:
    part = Part("HairBraid")
    acc = Part("HairClasps")
    s = lm.h / 0.222
    C = braid_spine(lm, body, params)
    L = arclen(C)
    braid_len = params["braid_length_m"] * s
    nb = int(np.searchsorted(L, braid_len))
    Cb = C[: nb + 1]
    Lb = L[: nb + 1]
    T, N, B = frames_along(Cb, np.array([0.0, -1.0, 0.0]))
    # N points roughly forward-ish: orient the weave plane across the body (B lateral)
    n_seg = 120
    idx = np.linspace(0, len(Cb) - 1, n_seg).astype(int)
    r0 = 0.0145 * s  # braid half-width at the top, tapering to the tail
    for k in range(3):
        ph = 2 * math.pi * k / 3
        pts, rad = [], []
        for ii in idx:
            u = Lb[ii] / braid_len
            w = r0 * (1.0 - 0.42 * u)
            t = Lb[ii] / (0.028 * s) * math.pi  # one cross every ~2.8 cm
            off = N[ii] * (0.55 * w * math.sin(t + ph)) + B[ii] * (0.45 * w * math.sin(2 * (t + ph)))
            pts.append(Cb[ii] + off)
            rad.append(w * 0.56)
        pts = np.array(pts)
        # M1-CHR-04: a full clump, and its dense middle only: the atlas columns now feather out to
        # nothing at their edges (no card borders), which on a closed tube would be a bare stripe
        slot = int(rng.integers(SLOTS_FULL))
        cols = [[(0.15 + 0.85 * (j / (n_seg - 1)) ** 2, 0.3 * j / (n_seg - 1), k / 3.0, 0.0)] * 6 for j in range(n_seg)]
        tube(part, pts, np.array(rad), 6, "hair", np.array([0.0, -1.0, 0.0]),
             uv_rect=((slot + 0.2) / CLUMPS, 0.05, (slot + 0.8) / CLUMPS, 0.72), colors=cols, tags=TAG_HAIR)
    # clasps (bone shell bands)
    for cm in params["clasps_m"]:
        ii = int(np.searchsorted(Lb, cm * s))
        ii = min(ii, len(Cb) - 3)
        u = Lb[ii] / braid_len
        w = r0 * (1.0 - 0.42 * u)
        seg = Cb[max(ii - 3, 0): ii + 4]
        tube(acc, catmull_rom(seg, 4), w * 1.12, 10, "bone", np.array([0.0, -1.0, 0.0]), tags=TAG_HAIR)
    # tail: loose cards fanning from the braid end
    end = Cb[-1]
    Tend = T[-1]
    for c in range(30):
        ang = 2 * math.pi * rng.random()
        rad = rng.uniform(0.2, 1.0) * r0 * 0.5
        start = end + (N[-1] * math.cos(ang) + B[-1] * math.sin(ang)) * rad
        length = rng.uniform(0.085, 0.12) * s
        spread = (N[-1] * math.cos(ang) + B[-1] * math.sin(ang)) * rng.uniform(0.05, 0.22)
        pts = np.array([start + (Tend + spread * (t ** 1.5)) * length * t for t in np.linspace(0, 1, 7)])
        nrm = np.tile(np.cross(Tend, B[-1]), (len(pts), 1))
        nrm = np.array([(N[-1] * math.cos(ang) + B[-1] * math.sin(ang))] * len(pts))
        _ribbon(part, pts, nrm, rng.uniform(0.006, 0.011) * s, int(rng.integers(SLOTS_FULL)),
                lambda t, ph=float(rng.random()): (0.6 + 0.4 * t, 0.5 * t, ph, 0.2 * t), taper=0.6)
    return part, acc, Cb


def flyaways(lm, body, params: dict, rng: np.random.Generator, braid_spine_pts: np.ndarray, scalp=None) -> Part:
    part = Part("HairFlyaways")
    scalp = scalp or Scalp(body)
    s = lm.h / 0.222
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    hc = np.array([0.0, yc, zc + 0.55 * lm.h])
    n = params["flyaways"]
    for i in range(n):
        if i < n * 0.6:  # crown: rooted well inside the hairline, lifting off along the hair flow
            for _try in range(40):
                d = rng.normal(size=3)
                d[2] = abs(d[2]) + 0.8
                d[1] = abs(d[1]) * 0.6  # the crown and the back, never over the forehead
                d /= np.linalg.norm(d)
                p = scalp.project((hc + d * ROOT_CAST_H * lm.h)[None, :], 0.006 * s)[0]
                if in_hair(lm, p[None, :], 0.08)[0]:
                    break
            nrm = scalp.normal(p[None, :])[0]
            tdir = _flow_dir(lm, p[None, :], nrm[None, :], _gather(lm))[0] + 0.35 * rng.normal(size=3)
            tdir -= (tdir @ nrm) * nrm
            tdir /= np.linalg.norm(tdir)
            length = rng.uniform(0.03, 0.07) * s
            pts = np.array([p + tdir * length * t + nrm * (0.004 * s) * t * t for t in np.linspace(0, 1, 5)])
        else:  # off the braid surface
            k = int(rng.integers(10, len(braid_spine_pts) - 5))
            c = braid_spine_pts[k]
            tdir = braid_spine_pts[k + 3] - braid_spine_pts[k]
            tdir /= np.linalg.norm(tdir)
            out = np.cross(tdir, rng.normal(size=3))
            out /= np.linalg.norm(out)
            p = c + out * 0.013 * s
            length = rng.uniform(0.03, 0.06) * s
            pts = np.array([p + (tdir * 0.9 + out * 0.4) * length * t for t in np.linspace(0, 1, 5)])
            nrm = out
        nrms = np.tile(nrm, (len(pts), 1))
        _ribbon(part, pts, nrms, rng.uniform(0.0012, 0.0022) * s, int(rng.integers(CLUMPS)),
                lambda t, ph=float(rng.random()): (0.3 * t, 0.3 * t, ph, 0.6 * t), taper=0.3, v_range=(0.3, 1.0))
    return part


def front_strands(lm, body, params: dict, rng: np.random.Generator, scalp=None) -> Part:
    """Two uncut face-framing strands on the right temple (asha.md §5)."""
    part = Part("HairFront")
    scalp = scalp or Scalp(body)
    s = lm.h / 0.222
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    for k in range(params["front_strands"]):
        x = -lm.head_w * (0.30 + 0.06 * k)
        root = scalp.project(np.array([[x, yc - 0.30 * lm.h, zc + (0.72 - 0.03 * k) * lm.h]]), 0.004 * s)[0]
        for c in range(3):
            ctrl = np.array([
                root + np.array([0.003 * c, 0.0, 0.0]) * s,
                root + np.array([-0.008 - 0.002 * c, -0.010, -0.030]) * s,
                root + np.array([-0.012 - 0.003 * c, -0.012, -0.065]) * s,
                root + np.array([-0.010 - 0.004 * c, -0.008, -0.095 - 0.01 * k]) * s,
            ])
            pts = catmull_rom(ctrl, 12)
            # keep clear of the face
            for _ in range(3):
                d = scalp.sdf(pts)
                nrm = scalp.normal(pts)
                pts = pts + nrm * np.maximum(0.004 * s - d, 0.0)[:, None]
            nrm = scalp.normal(pts)
            _ribbon(part, pts, nrm, rng.uniform(0.006, 0.010) * s, int(rng.integers(CLUMPS)),
                    lambda t, ph=float(rng.random()): (0.9 * t, 0.6 * t, ph, 0.4 * t), taper=0.55)
    return part


def comb(lm, body, scalp=None) -> Part:
    """Her mother's tortoiseshell comb, set into the hair behind the left ear (asha.md §4.1 #9)."""
    part = Part("HairComb")
    s = lm.h / 0.222
    G = _gather(lm)
    scalp = scalp or Scalp(body)
    c = G + np.array([-0.006, -0.026, 0.040]) * s
    c = scalp.project(c[None, :], 0.010 * s)[0]
    nrm = scalp.normal(c[None, :])[0]
    up = np.array([0.0, 0.0, 1.0])
    side = np.cross(nrm, up)
    side /= np.linalg.norm(side)
    up = np.cross(side, nrm)
    nu, nv = 10, 3
    P = np.zeros((nv + 1, nu + 1, 3))
    for j in range(nv + 1):
        for i in range(nu + 1):
            a = (i / nu - 0.5) * 1.2
            P[j, i] = c + side * math.sin(a) * 0.026 * s + up * (j / nv - 0.5) * 0.016 * s + nrm * (math.cos(a) - 1) * 0.012 * s
    grid(part, P, "tortoiseshell", tags=TAG_HAIR)
    back = P - nrm * 0.0025 * s
    grid(part, back, "tortoiseshell", tags=TAG_HAIR, flip=True)
    return part


def build_hair(lm, body, params: dict, scalp=None) -> dict[str, Part]:
    """`scalp`: what the scalp cards, flyaways, front strands and comb sit on (MeshScalp on the
    shipped head in build_asha; the anatomy field when omitted)."""
    rng = np.random.default_rng(int(params["seed"]))
    out = {"HairScalp": scalp_cards(lm, body, params, rng, scalp)}
    br, clasps, spine = braid(lm, body, params, rng)
    out["HairBraid"] = br
    out["HairClasps"] = clasps
    out["HairFlyaways"] = flyaways(lm, body, params, rng, spine, scalp)
    out["HairFront"] = front_strands(lm, body, params, rng, scalp)
    out["HairComb"] = comb(lm, body, scalp)
    for p in out.values():  # wind colours everywhere (accessories are pinned)
        p.C = p.C + [(0.0, 0.0, 0.0, 0.0)] * (len(p.V) - len(p.C))
    return out
