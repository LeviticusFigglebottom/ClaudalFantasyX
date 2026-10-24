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
HAIRLINE_SWING = 0.006  # head heights (M1-CHR-12)
# M1-CHR-12: near the front hairline the hair is drawn up and back before it turns toward the braid
FRONT_LIFT = 1.2  # weight of the up-and-back pull at the hairline
FRONT_LIFT_BAND = 0.12  # head heights above the hairline over which it fades out


def hairline_v(lm, P: np.ndarray) -> np.ndarray:
    """Hairline height (head heights above the chin) for points P, by azimuth around the head axis.
    0 = front, +90 = the character's left. The front is 'moderately high' (asha.md §6.1)."""
    yc = lm.P("head_c")[1]
    phi = np.degrees(np.arctan2(P[:, 0], -(P[:, 1] - yc)))
    a = np.abs(phi)
    xs = [0, 30, 50, 66, 76, 84, 96, 112, 135, 160, 180]
    # M1-CHR-03: front -0.035 h (donor forehead). M1-CHR-07: the temples 0.01-0.02 h lower, so hair
    # frames them; the bare temple skin on the silhouette read as a very high forehead and, lit from
    # behind, as a pinkish streak (review sweep J). The front stays: lowered, a hairline card rooted
    # on the bare forehead and ran down across the brow
    # M1-CHR-12: the front 0.027 h (6 mm) lower and the temple corners a touch lower, so the forehead
    # is not "very tall" (QA-08); the flow now lifts off the front hairline (_flow_dir), which is what
    # used to run a lowered hairline's cards down across the brow
    vs = [0.738, 0.731, 0.689, 0.632, 0.59, 0.585, 0.635, 0.50, 0.32, 0.25, 0.24]
    # M1-CHR-04: a natural hairline is not a clean curve; it wanders by up to ~2.5 mm (cards, the
    # scalp underpaint and the skin maps all read this, so they agree). M1-CHR-12: plus a slow,
    # asymmetric swing (+-1.3 mm), so the arc over the forehead is not even from temple to temple
    t = np.radians(phi)
    wander = 0.005 * np.sin(7.0 * t + 1.1) + 0.0035 * np.sin(13.0 * t + 2.3) + 0.002 * np.sin(29.0 * t + 0.4)
    wander = wander + HAIRLINE_SWING * np.sin(3.0 * t + 0.9)
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
    zc = lm.P("chin")[2]
    v = (P[:, 2] - zc) / lm.h
    lift = np.clip((hairline_v(lm, P) + FRONT_LIFT_BAND - v) / FRONT_LIFT_BAND, 0.0, 1.0) * np.clip(front, 0.0, 1.0)
    d = d + np.outer(FRONT_LIFT * lift, np.array([0.0, 0.6, 1.0]))
    d = d - np.sum(d * N, axis=1, keepdims=True) * N
    return d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)


def _ribbon(part: Part, pts: np.ndarray, nrm: np.ndarray, width: float, slot: int, color_fn, taper: float = 0.45,
            v_range=(0.0, 1.0), mat: str = "hair", u_range=(0.0, 1.0)) -> None:
    """A card along `pts`. `u_range`: the part of the atlas column it samples (the columns feather
    out to nothing at their edges, so a very narrow card wants the dense middle)."""
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
    u0, u1 = (slot + u_range[0]) / CLUMPS, (slot + u_range[1]) / CLUMPS
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
    Gs = scalp.project(G[None, :])[0]  # M1-CHR-14: the gather on the scalp, where the braid root is seated
    for k in range(seg):
        cur = paths[-1]
        N = scalp.normal(cur)
        fdir = _flow_dir(lm, cur, N, G)
        nxt = scalp.project(cur + fdir * step[:, None], lift, iters=3)
        near = np.linalg.norm(nxt - Gs, axis=1) < CARD_STOP_AT_ROOT * s
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
    # M1-CHR-09: the base layer is hidden under the mid layer, the crown clumps and the underpaint,
    # so it is fewer, wider cards (12-20 mm; CHR-04 had 9-16 mm), which pays for the clumps. The
    # chord sag across a 20 mm card on the skull is about 0.6 mm, under the 1.2 mm lift.
    layers = [(0.0012 * s, params["scalp_cards"][0], (0.012, 0.020)),
              (0.0026 * s, params["scalp_cards"][1], (0.007, 0.013)),
              (0.0040 * s, params["scalp_cards"][2], (0.005, 0.010))]
    for li, (lift, count, wr) in enumerate(layers):
        if count == 0:
            continue
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
    crown_clumps(part, scalp, lm, params, rng, G, hc, seg)
    return part


# M1-CHR-09: the crown read as a smooth shell (asha_review.md §8.3): every card lay at one of three
# fixed lifts and followed the scalp exactly, so the silhouette was a clean arc and the highlight one
# band. The top layer is now strand clumps: 2-4 narrow cards share a path, gather toward the middle
# of their length (hair clumps where it is combed together), rise off the scalp in an arc of up to a
# few millimetres, and twist a little about their length, so each clump catches its own highlight.
CLUMP_LIFT = 0.0036  # m at s = 1: the clump paths' lift at the root and the tip (the old top layer's 4 mm)
# M1-CHR-12: QA-08 still read the crown as a sleek shell, so the clumps stand further off and more of
# them are loose (CHR-09: rise 0.8-3.7 mm, 18% loose by 5.5 mm)
CLUMP_RISE = (0.0012, 0.0050)  # extra lift at mid-length, m (a few clumps are looser, below)
CLUMP_LOOSE = (0.30, 0.0090)  # share of clumps that stand further off, and their extra rise, m
CLUMP_SPREAD = (0.003, 0.006)  # half-spread of the member cards at the root, m
CLUMP_GATHER = 0.55  # how far the members close up at mid-length (0 = parallel)
CLUMP_TWIST = 0.35  # rad, the most a member card rolls about its length


def crown_clumps(part: Part, scalp, lm, params: dict, rng: np.random.Generator, G: np.ndarray, hc: np.ndarray,
                 seg: int) -> None:
    n = int(params.get("crown_clumps", 0))
    if not n:
        return
    s = lm.h / 0.222
    d_in = rng.normal(size=(n * 6, 3))
    d_in[:, 2] = np.abs(d_in[:, 2]) * 1.2 + 0.1
    d_in /= np.linalg.norm(d_in, axis=1, keepdims=True)
    p_in = scalp.project(hc + d_in * ROOT_CAST_H * lm.h)
    ok = in_hair(lm, p_in, 0.025) & (np.linalg.norm(p_in - G, axis=1) > 0.05 * s)
    roots = p_in[ok][:n]
    length = rng.uniform(0.10, 0.19, len(roots)) * s
    paths, stop = _trace(scalp, lm, roots, length, CLUMP_LIFT * s, G, seg)
    for c in range(len(roots)):
        C = paths[c, : stop[c] + 1]
        if len(C) < 4:
            continue
        N = scalp.normal(C)
        T = np.gradient(C, axis=0)
        T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
        side = np.cross(T, N)
        side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-12)
        t = np.linspace(0.0, 1.0, len(C))
        arc = np.sin(math.pi * t) ** 1.3
        rise = rng.uniform(*CLUMP_RISE) * s
        if rng.random() < CLUMP_LOOSE[0]:
            rise += CLUMP_LOOSE[1] * s * float(rng.uniform(0.6, 1.0))
        k = int(rng.integers(2, 5))
        spread = rng.uniform(*CLUMP_SPREAD) * s
        gather = 1.0 - CLUMP_GATHER * np.sin(math.pi * t)
        for m in range(k):
            f = (m - (k - 1) / 2) / ((k - 1) / 2)  # -1 .. 1 across the clump
            off = f * spread * rng.uniform(0.7, 1.1)
            lift = rise * (1.0 - 0.35 * abs(f)) * rng.uniform(0.75, 1.0) * arc  # a rounded clump
            pts = C + side * (off * gather)[:, None] + N * lift[:, None]
            a = rng.uniform(-CLUMP_TWIST, CLUMP_TWIST) * np.sin(math.pi * t)
            nrm = N * np.cos(a)[:, None] - side * np.sin(a)[:, None]
            slot = int(rng.choice(SLOTS_SPARSE)) if rng.random() < 0.4 else int(rng.integers(SLOTS_FULL))
            ph = float(rng.random())
            _ribbon(part, pts, nrm, float(rng.uniform(0.004, 0.007) * s), slot, lambda t, ph=ph: (0.0, 0.0, ph, 0.0),
                    taper=0.35, v_range=(0.0, 0.85))


BRAID_ROOT_SEAT = 0.004  # m at s = 1: the braid's root centre off the skin, inside the scalp cards' lift
BRAID_ROOT_RAMP = 0.07  # m along the braid over which the clearance grows to BRAID_CLEAR
BRAID_CLEAR = 0.024  # m: the braid's clearance from the body below the root
CARD_STOP_AT_ROOT = 0.012  # m at s = 1: scalp cards stop this close to the braid root (CHR-04: 0.03)


def _sdf_grad(fn, P: np.ndarray, e: float = 3e-4) -> np.ndarray:
    g = np.zeros_like(P)
    for i in range(3):
        d = np.zeros(3)
        d[i] = e
        g[:, i] = fn(P + d) - fn(P - d)
    return g / np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-12)


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
    # M1-CHR-14: the root is seated in the hair, not hung beside it. G sits 15 mm off the donor scalp
    # (bb_donor), and the clearance pass below used to push every spine point, the root included,
    # 24 mm off the body (the head is part of it), so the braid floated beside the nape. The root now
    # starts BRAID_ROOT_SEAT off the skin (inside the scalp cards' lift) and the clearance ramps up
    # from that to the full value over the first BRAID_ROOT_RAMP of the braid.
    head = body.regions["head"]
    gh = _sdf_grad(head.sdf, G[None, :])[0]
    root = G - gh * (float(head.sdf(G[None, :])[0]) - BRAID_ROOT_SEAT * s)
    ctrl[0] = root
    C = catmull_rom(ctrl, 400)
    L = arclen(C)
    total = params["braid_length_m"] * s + params["tail_m"] * s
    C = C[L <= total]
    L = L[L <= total]
    # keep it clear of the body (+ the vest on the chest) and the costume
    ramp = np.clip(L / (BRAID_ROOT_RAMP * s), 0.0, 1.0)
    ramp = ramp * ramp * (3.0 - 2.0 * ramp)
    clear = (BRAID_ROOT_SEAT + (BRAID_CLEAR - BRAID_ROOT_SEAT) * ramp) * s
    for _ in range(6):
        d = body.sdf(C)
        g = body.grad(C)
        g /= np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-9)
        push = np.maximum(clear - d, 0.0)
        C = C + g * push[:, None]
        # smooth (the root stays where it is seated)
        C[1:-1] = 0.5 * C[1:-1] + 0.25 * (C[:-2] + C[2:])
        C[0] = root
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


FLY_LIFT = (0.006, 0.016)  # m at s = 1: how far a crown flyaway's tip stands off the hair (M1-CHR-12: was 4-11 mm)
FLY_BRAID_FROM = 30  # braid spine sample (of 200) where the braid's flyaways start: the shoulder


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
            # M1-CHR-09: they stand off the crown by 4-11 mm at the tip (CHR-04: 4 mm), so some of
            # them cross the head's outline and break the clean arc of the silhouette
            up = rng.uniform(FLY_LIFT[0], FLY_LIFT[1]) * s
            pts = np.array([p + tdir * length * t + nrm * up * t ** 1.6 for t in np.linspace(0, 1, 6)])
        else:  # off the braid surface
            # M1-CHR-09: from the shoulder down; nearer the gather one stuck out sideways by the jaw
            k = int(rng.integers(FLY_BRAID_FROM, len(braid_spine_pts) - 5))
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


# M1-CHR-09: the face-framing lock (asha.md §5: two uncut strands, 6-8 cm, free on the right
# temple). CHR-07 rooted it 4.4-5.3 cm off the midline, right above the brow tail, and laid three
# 4-5 mm ribbons 4 mm off the skin, so from the front it was a dark streak drawn across the brow.
# Now each strand escapes the drawn-back hair at the temple hairline, outside the orbit, and hangs
# as a fan of fine ribbons that leaves the skin as it falls, with uneven tips and skin between them.
LOCK_AZIMUTH = (-53.0, -63.0)  # deg round the head from the front (- = her right): the temple
LOCK_LENGTH = (0.080, 0.065)  # m at s = 1, per strand (asha.md §5: 6-8 cm)
LOCK_OFF_SKIN = (0.0015, 0.0045)  # m, the strand's distance off the skin at the root and from mid-length down
LOCK_FAN = 0.009  # m, the half-spread of a strand's ribbons at the tips (they start together)
LOCK_WIDTH = (0.0022, 0.0036)  # m, one ribbon: a few dozen hairs
LOCK_POINTS = 16
# the dense middle of an atlas column: a 2-4 mm ribbon over the full column was mostly its feathered edges
LOCK_U = (0.25, 0.75)


def front_strands(lm, body, params: dict, rng: np.random.Generator, scalp=None) -> Part:
    """Two uncut face-framing strands on the right temple (asha.md §5), each a fan of fine ribbons."""
    part = Part("HairFront")
    scalp = scalp or Scalp(body)
    s = lm.h / 0.222
    per = int(params.get("front_strand_ribbons", 3))
    for k in range(params["front_strands"]):
        phi = math.radians(LOCK_AZIMUTH[k % len(LOCK_AZIMUTH)])
        root = _hairline_roots(scalp, lm, np.array([phi]), np.array([0.004 + 0.003 * k]))[0]
        n0 = scalp.normal(root[None, :])[0]
        fwd = np.array([0.0, -1.0, 0.0]) - n0 * (-n0[1])  # toward the face, in the skin's tangent plane
        fwd /= np.linalg.norm(fwd)
        down = np.cross(n0, fwd)  # tangent, roughly -z on her right temple
        if down[2] > 0:
            down = -down
        length = LOCK_LENGTH[k % len(LOCK_LENGTH)] * s
        for c in range(per):
            f = (c - (per - 1) / 2) / max((per - 1) / 2, 1)  # -1 .. 1 across the fan
            L = length * rng.uniform(0.78, 1.0)
            fan = (f * LOCK_FAN + rng.normal(0.0, 0.0015)) * s
            ctrl = np.array([
                root + fwd * (0.0006 * f * s),
                root + down * 0.30 * L + fwd * (0.002 * s + 0.25 * fan),
                root + down * 0.65 * L + fwd * (0.003 * s + 0.6 * fan),  # a slight forward S toward the cheek
                root + down * L + fwd * (0.001 * s + fan),
            ])
            pts = catmull_rom(ctrl, LOCK_POINTS)
            t = np.linspace(0.0, 1.0, len(pts))
            gap = (LOCK_OFF_SKIN[0] + (LOCK_OFF_SKIN[1] - LOCK_OFF_SKIN[0]) * smooth01(t / 0.5)) * s
            gap = gap + rng.uniform(0.0, 0.002) * s * t  # the ribbons sit at different depths
            for _ in range(4):  # hang clear of the face: the skin pushes the strand out, never pulls it in
                d = scalp.sdf(pts)
                nrm = scalp.normal(pts)
                pts = pts + nrm * np.maximum(gap - d, 0.0)[:, None]
            nrm = scalp.normal(pts)
            ph = float(rng.random())
            _ribbon(part, pts, nrm, float(rng.uniform(*LOCK_WIDTH) * s), int(rng.integers(SLOTS_FULL)),
                    lambda t, ph=ph: (0.9 * t, 0.6 * t, ph, 0.4 * t), taper=0.45, v_range=(0.0, 0.75),
                    u_range=LOCK_U)
    return part


def smooth01(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def comb(lm, body, scalp=None) -> Part:
    """Her mother's tortoiseshell comb, set into the hair behind the left ear (asha.md §4.1 #9)."""
    part = Part("HairComb")
    s = lm.h / 0.222
    G = _gather(lm)
    scalp = scalp or Scalp(body)
    c = G + np.array([-0.006, -0.026, 0.040]) * s
    # M1-CHR-07: seated in the hair (the top card layer is lifted 4 mm), not floating 10 mm off the
    # scalp, where it read as a pale card above the ear (review sweep J)
    c = scalp.project(c[None, :], 0.0045 * s)[0]
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


# M1-CHR-12: fine wisps at the front hairline (baby hairs and a few escaped strands), so the hairline
# is broken by individual hairs instead of being one hard, even arc (QA-08)
WISP_AZIMUTH = 72.0  # deg either side of the front
WISP_LENGTH = (0.006, 0.020)  # m at s = 1
WISP_LIFT = (0.0004, 0.0025)  # m: how far the tip stands off the skin
WISP_WIDTH = (0.0012, 0.0020)  # m


def hairline_wisps(lm, body, params: dict, rng: np.random.Generator, scalp=None) -> Part:
    part = Part("HairWisps")
    n = int(params.get("hairline_wisps", 0))
    if not n:
        return part
    scalp = scalp or Scalp(body)
    s = lm.h / 0.222
    G = _gather(lm)
    phi = np.radians(rng.uniform(-WISP_AZIMUTH, WISP_AZIMUTH, n))
    roots = _hairline_roots(scalp, lm, phi, rng.uniform(0.002, 0.016, n))
    for i in range(n):
        p = roots[i]
        nrm = scalp.normal(p[None, :])[0]
        # out of the hair mass and down over the hairline onto the skin, fanning sideways
        down = np.array([0.0, 0.0, -1.0]) - nrm * (-nrm[2])
        tdir = down / max(np.linalg.norm(down), 1e-9) + 0.7 * rng.normal(size=3) - 0.3 * _flow_dir(
            lm, p[None, :], nrm[None, :], G)[0]
        tdir -= (tdir @ nrm) * nrm
        tdir /= np.linalg.norm(tdir)
        length = rng.uniform(*WISP_LENGTH) * s
        up = rng.uniform(*WISP_LIFT) * s
        curl = rng.normal(size=3) * 0.3
        pts = np.array([p + nrm * 0.0006 * s + (tdir + curl * t) * length * t + nrm * up * t ** 1.8
                        for t in np.linspace(0, 1, 6)])
        _ribbon(part, pts, np.tile(nrm, (len(pts), 1)), float(rng.uniform(*WISP_WIDTH) * s),
                int(rng.choice(SLOTS_SPARSE)), lambda t, ph=float(rng.random()): (0.0, 0.0, ph, 0.0), taper=0.5,
                v_range=(0.15, 0.9), u_range=(0.3, 0.7))
    return part


def build_hair(lm, body, params: dict, scalp=None) -> dict[str, Part]:
    """`scalp`: what the scalp cards, flyaways, front strands and comb sit on (MeshScalp on the
    shipped head in build_asha; the anatomy field when omitted)."""
    # M1-CHR-09: one random stream per part, so re-laying the scalp cards no longer reshuffles the
    # braid, the flyaways and the lock (CHR-07's lower temple moved a flyaway onto the jaw that way)
    seed = int(params["seed"])
    out = {"HairScalp": scalp_cards(lm, body, params, np.random.default_rng([seed, 0]), scalp)}
    br, clasps, spine = braid(lm, body, params, np.random.default_rng([seed, 1]))
    out["HairBraid"] = br
    out["HairClasps"] = clasps
    out["HairFlyaways"] = flyaways(lm, body, params, np.random.default_rng([seed, 2]), spine, scalp)
    out["HairFront"] = front_strands(lm, body, params, np.random.default_rng([seed, 3]), scalp)
    out["HairComb"] = comb(lm, body, scalp)
    out["HairScalp"].extend(hairline_wisps(lm, body, params, np.random.default_rng([seed, 4]), scalp))
    for p in out.values():  # wind colours everywhere (accessories are pinned)
        p.C = p.C + [(0.0, 0.0, 0.0, 0.0)] * (len(p.V) - len(p.C))
    return out
