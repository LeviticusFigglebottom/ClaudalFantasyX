"""Sefir's hair as card layers (no bpy), act1_npcs.md §1.5 and the hair contract in character_shading.md.

Silver-white, very long, straight and loose, parted at the centre, to mid-back (65 cm from the crown):

* **Scalp**: three lifted layers of strand cards (about 300) rooted inside the hairline and combed back from the
  centre part along `_flow_dir` (sideways off the part, then down and back), on Asha's strand atlas (asha_hair
  columns: full clumps, sparse breakup clumps for the top layer, soft-root hairline clumps for the edge).
* **The fall**: 6 strand groups behind (from behind the ears round the back of the head) and 2 in front (from the
  temples, past the front of the ears, over the collarbones). Every card is a draped strand: it starts on the scalp
  and steps under gravity (with a small backward or forward bias per group), held on the scalp while it lies on it,
  then free, then lying over whatever is under it: `avoid(P)` (the body under its clothes, the half-mantle, from
  build_sefir) is kept at a clearance, so the right-hand groups lie over the mantle instead of through it.
  Each group carries a chain of 5 bones (build_sefir weights the cards to the head at the root and to the chain
  below the point where the strand leaves the scalp; the chains hang from the chest, DEF-spine.003).

Plain loose hair, no sculpted or upswept lock anywhere (act1_npcs.md §1.2, the echo watch). Vertex colour = wind (R
primary, G secondary, B phase, A flutter): scalp cards pinned, the fall free toward its tips; the material's
wind response is 0.1 (his hair barely moves in the wind that moves everyone else's). The interface asha_textures reads
for the scalp paint: `hairline_v`, `in_hair`, `_gather`, `_flow_dir`. Seeded, deterministic.
"""
from __future__ import annotations

import math

import numpy as np

import asha_hair
from asha_hair import ROOT_CAST_H, Scalp, _ribbon  # noqa: F401
from asha_mesh import Part

TAG_HAIR = asha_hair.TAG_HAIR
SLOTS_FULL = asha_hair.SLOTS_FULL
SLOTS_SPARSE = asha_hair.SLOTS_SPARSE
SLOTS_HAIRLINE = asha_hair.SLOTS_HAIRLINE
STILL = (0.0, 0.0, 0.0, 0.0)
# the fall: (azimuth of the group's root round the head, deg: 0 front, + his left; root height in head heights above
# the chin; the group's half-width at the root in deg; the drape's bias: back (+) or forward (-) per metre of drop)
BACK_GROUPS = ((-108.0, 0.74, 14.0, 0.30), (-136.0, 0.80, 15.0, 0.22), (-162.0, 0.84, 14.0, 0.14),
               (162.0, 0.84, 14.0, 0.14), (136.0, 0.80, 15.0, 0.22), (108.0, 0.74, 14.0, 0.30))
FRONT_GROUPS = ((-86.0, 0.74, 7.0, -0.30), (86.0, 0.74, 7.0, -0.30))
FALL_LIFT = (0.0050, 0.0085)  # m at s = 1: inner and outer layer off the scalp (over the scalp cards' 1.2-4 mm)
FALL_CLEAR = 0.010  # m: off the cloth (avoid() already includes the garments' own offsets)
FALL_STEP = 0.022  # m per drape step
FALL_POINTS = 18  # points per fall card after resampling
FALL_WIDTH = (0.012, 0.020)  # m, one fall card
FRONT_WIDTH = (0.008, 0.013)
LEAVE_SDF = 0.004  # m past its lift: the strand has left the scalp
DRAPE_GRID = 1e-5  # m: the drape's state is rounded to this every step (the iteration amplified the last bits that
# numpy's SIMD paths leave in the field and the projections, so hosts disagreed by a micron by the tips)
HEAD_REACH = 0.04  # m: farther than this from the head skin a point is off the head
BIAS_FADE = 0.18  # m of drop over which a group's back/forward bias fades
COHESION = {"b": 0.45, "f": 0.8}  # (GPU QA row 54: was 0.35/0.6; strands floated apart)  # how far a group's strands close up below the head, behind and in front
LATERAL = 0.12  # an outward push off the sides of the head per unit drop (fading with the bias)
BODY_PULL = 0.4  # pull toward the nearest surface under the strand, per unit drop


# ---------------------------------------------------------------------------------------------
# Hairline and flow (the interface asha_textures reads)
# ---------------------------------------------------------------------------------------------
def hairline_v(lm, P: np.ndarray) -> np.ndarray:
    """Hairline height (head heights above the chin) by azimuth (0 front, +90 his left): a full man's hairline, no
    recession (he is ageless), the temples framed, the nape low. Symmetric (act1_npcs.md §1.6: his tell is symmetry)."""
    yc = lm.P("head_c")[1]
    phi = np.degrees(np.arctan2(P[:, 0], -(P[:, 1] - yc)))
    a = np.abs(phi)
    xs = [0, 20, 34, 46, 58, 70, 80, 90, 104, 118, 140, 162, 180]
    vs = [0.735, 0.733, 0.725, 0.712, 0.690, 0.630, 0.570, 0.548, 0.575, 0.47, 0.31, 0.24, 0.23]
    t = np.radians(a)  # |phi|: the wander is mirrored too
    wander = 0.003 * np.sin(9.0 * t + 0.4) + 0.002 * np.sin(17.0 * t + 1.3) + 0.0012 * np.sin(31.0 * t + 0.9)
    return np.interp(a, xs, vs) + wander


def in_hair(lm, P: np.ndarray, margin_h: float = 0.0) -> np.ndarray:
    zc = lm.P("chin")[2]
    v = (P[:, 2] - zc) / lm.h
    return v > hairline_v(lm, P) + margin_h


def _gather(lm) -> np.ndarray:
    """The crown (the flow's reference point: the hair is combed away from the part and down from here)."""
    return lm.P("crown").copy()


def _flow_dir(lm, P: np.ndarray, N: np.ndarray, G: np.ndarray) -> np.ndarray:
    """Off the centre part sideways, back from the forehead, then down at the sides and behind."""
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    v = (P[:, 2] - zc) / lm.h
    top = np.clip((v - 0.80) / 0.15, 0.0, 1.0)
    front = np.clip(-(P[:, 1] - yc) / (0.4 * lm.h), 0.0, 1.0)
    side = np.stack([np.where(P[:, 0] >= 0.0, 1.0, -1.0), np.zeros(len(P)), np.zeros(len(P))], axis=1)
    back = np.array([0.0, 1.0, 0.0])
    down = np.array([0.0, 0.0, -1.0])
    # at the front the hair is drawn back off the forehead, never down over it
    d = side * (0.9 * top + 0.30)[:, None] + back[None, :] * (1.2 * front + 0.25)[:, None] + down[None, :] * (
        (1.0 - 0.7 * top) * (1.0 - 0.85 * front))[:, None]
    d = d - np.sum(d * N, axis=1, keepdims=True) * N
    _ = G
    return d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)


# ---------------------------------------------------------------------------------------------
# Scalp cards
# ---------------------------------------------------------------------------------------------
def _trace(scalp, step_dir, roots: np.ndarray, length: np.ndarray, lift: float, seg: int) -> np.ndarray:
    step = length / seg
    paths = [scalp.project(roots, lift)]
    for _ in range(seg):
        cur = paths[-1]
        N = scalp.normal(cur)
        paths.append(scalp.project(cur + step_dir(cur, N) * step[:, None], lift))
    return np.stack(paths, axis=1)


def _roots_inside(scalp, lm, rng, n: int, margin: float) -> np.ndarray:
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    hc = np.array([0.0, yc, zc + 0.55 * lm.h])
    d_in = rng.normal(size=(n * 6, 3))
    d_in[:, 2] = np.abs(d_in[:, 2]) * 1.2 + 0.05
    d_in /= np.linalg.norm(d_in, axis=1, keepdims=True)
    p_in = scalp.project(hc + d_in * ROOT_CAST_H * lm.h)
    return p_in[in_hair(lm, p_in, margin)][:n]


def scalp_cards(lm, params: dict, rng: np.random.Generator, scalp) -> Part:
    part = Part("HairScalp")
    G = _gather(lm)
    s = lm.h / 0.222

    def flow(P, N):
        return _flow_dir(lm, P, N, G)

    layers = [(0.0012 * s, params["scalp_cards"][0], (0.012, 0.020), 0.002, False),
              (0.0026 * s, params["scalp_cards"][1], (0.008, 0.014), 0.008, False),
              (0.0040 * s, params["scalp_cards"][2], (0.006, 0.011), 0.014, True)]
    for lift, count, wr, margin, outer in layers:
        roots = _roots_inside(scalp, lm, rng, int(count), margin)
        n = len(roots)
        length = rng.uniform(0.10, 0.17, n) * s
        paths = _trace(scalp, flow, roots, length, lift, 6)
        zc = lm.P("chin")[2]
        edge = (roots[:, 2] - zc) / lm.h < hairline_v(lm, roots) + 0.02
        slots = rng.integers(SLOTS_FULL, size=n)
        if outer:
            slots = np.where(rng.random(n) < 0.5, rng.choice(SLOTS_SPARSE, n), slots)
        slots = np.where(edge, rng.choice(SLOTS_HAIRLINE, n), slots)
        widths = rng.uniform(*wr, n) * s
        for c in range(n):
            pts = paths[c]
            _ribbon(part, pts, scalp.normal(pts), float(widths[c]), int(slots[c]), lambda t: STILL, taper=0.35,
                    v_range=(0.0, 0.85))
    return part


# ---------------------------------------------------------------------------------------------
# The fall
# ---------------------------------------------------------------------------------------------
def _num_grad(fn, P: np.ndarray, e: float = 4e-4) -> np.ndarray:
    g = np.zeros_like(P)
    for k in range(3):
        d = np.zeros(3)
        d[k] = e
        g[:, k] = fn(P + d) - fn(P - d)
    return g / np.maximum(np.linalg.norm(g, axis=1, keepdims=True), 1e-12)


def _grid(P: np.ndarray) -> np.ndarray:
    return np.round(P / DRAPE_GRID) * DRAPE_GRID


def _head_sd(scalp, P: np.ndarray) -> np.ndarray:
    """The scalp's signed distance, large where P is not near the head (a MeshScalp's nearest head point far below
    the jaw says nothing about inside or outside)."""
    sd = scalp.sdf(P)
    if hasattr(scalp, "nearest"):
        Q, _N = scalp.nearest(P)
        sd = np.where(np.linalg.norm(P - Q, axis=1) > HEAD_REACH, 1.0, sd)
    return sd


def drape(scalp, avoid, roots: np.ndarray, lift: np.ndarray, length: np.ndarray, bias: np.ndarray, lm) -> tuple:
    """Draped strands: from each root, steps of FALL_STEP down (with `bias` back/forward per unit drop and a little
    outward from the head axis), held `lift` off the scalp while on it and FALL_CLEAR off `avoid` everywhere.
    Returns (paths (n, FALL_POINTS, 3), arc length at which each strand leaves the scalp)."""
    n = len(roots)
    steps = int(math.ceil(float(length.max()) / FALL_STEP)) + 1
    cur = _grid(scalp.project(roots, 0.0) + scalp.normal(roots) * lift[:, None])
    pts = [cur]
    s = np.zeros(n)
    leave = np.full(n, np.nan)
    for _ in range(steps):
        out = _num_grad(avoid, cur)  # away from the nearest surface under the strand
        out[:, 2] = np.minimum(out[:, 2], 0.0)
        # the bias fades over the first BIAS_FADE m (it only carries the strand past the shoulder); then gravity and a
        # pull toward the body, so the strand lies on what is under it instead of standing off it
        b = bias * np.exp(-s / BIAS_FADE)
        lat = LATERAL * np.exp(-s / BIAS_FADE) * np.sign(cur[:, 0])  # out past the cheeks and the ears
        d = np.stack([lat, b, -np.ones(n)], axis=1) - BODY_PULL * out
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        nxt = cur + d * FALL_STEP
        for _ in range(3):
            sd = _head_sd(scalp, nxt) - lift
            on = sd < 0.0
            if on.any():
                nxt[on] = scalp.project(nxt[on], 0.0) + scalp.normal(nxt[on]) * lift[on, None]
            a = avoid(nxt) - FALL_CLEAR
            hit = a < 0.0
            if hit.any():
                nxt[hit] = nxt[hit] - _num_grad(avoid, nxt[hit]) * a[hit, None]
        # keep the step length (the projections only redirect it)
        dv = nxt - cur
        dv = dv / np.maximum(np.linalg.norm(dv, axis=1, keepdims=True), 1e-12) * FALL_STEP
        nxt = _grid(cur + dv)
        s = s + FALL_STEP
        off_scalp = (_head_sd(scalp, nxt) - lift) > LEAVE_SDF
        leave = np.where(np.isnan(leave) & off_scalp, s, leave)
        cur = nxt
        pts.append(cur)
    P = np.stack(pts, axis=1)
    out = np.zeros((n, FALL_POINTS, 3))
    for c in range(n):
        arc = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(P[c], axis=0), axis=1))])
        st = np.linspace(0.0, float(length[c]), FALL_POINTS)
        out[c] = _grid(np.stack([np.interp(st, arc, P[c, :, k]) for k in range(3)], axis=1))
    leave = np.where(np.isnan(leave), length, leave)
    return out, np.minimum(leave, length)


def _cohere(paths: np.ndarray, avoid, amount: float) -> np.ndarray:
    """Draw a group's strands together below the head (a length of hair hangs as one lock, not as loose strings):
    each strand's offset from the group's mean strand shrinks by up to `amount` over its lower part, then the strands
    are pushed back out to their clearance."""
    n, m = paths.shape[:2]
    t = np.linspace(0.0, 1.0, m)
    f = 1.0 - amount * np.clip((t - 0.15) / 0.45, 0.0, 1.0) ** 2
    mean = paths.mean(axis=0)
    out = mean[None, :, :] + (paths - mean[None, :, :]) * f[None, :, None]
    flat = out.reshape(-1, 3)
    for _ in range(3):
        a = avoid(flat) - FALL_CLEAR
        hit = a < 0.0
        if not hit.any():
            break
        flat[hit] = flat[hit] - _num_grad(avoid, flat[hit]) * a[hit, None]
    out = _grid(flat.reshape(n, m, 3))
    out[:, 0] = paths[:, 0]  # the roots stay where they are
    return out


def _group_roots(scalp, lm, rng, az: float, v: float, half: float, n: int) -> np.ndarray:
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    hc = np.array([0.0, yc, zc + 0.55 * lm.h])
    phi = np.radians(az + np.linspace(-half, half, n) + rng.uniform(-0.3, 0.3, n) * (2 * half / max(n, 1)))
    d = np.stack([np.sin(phi), -np.cos(phi), np.zeros(n)], axis=1)
    p = scalp.project(hc + d * ROOT_CAST_H * lm.h)
    vv = v + rng.uniform(-0.03, 0.03, n)
    for _ in range(8):
        dz = (zc + vv * lm.h) - p[:, 2]
        p = scalp.project(p + np.stack([np.zeros(n), np.zeros(n), dz], axis=1))
    return p


def fall(lm, params: dict, rng: np.random.Generator, scalp, avoid) -> tuple[Part, list, list]:
    """The fall cards. Returns (part, cards, groups): cards = (first vertex, points, group index, leave fraction)
    per card; groups = (name, chain points (chain_bones + 1, 3)) per group."""
    part = Part("HairBack")
    s = lm.h / 0.222
    L = float(params["length_m"])
    n_back, n_front = (int(x) for x in params["cards_per_group"])
    nb = int(params["chain_bones"])
    crown_z = float(lm.P("crown")[2])
    cards = []
    groups = []
    specs = [("b", g) for g in BACK_GROUPS] + [("f", g) for g in FRONT_GROUPS]
    for gi, (kind, (az, v, half, bias)) in enumerate(specs):
        n = n_back if kind == "b" else n_front
        roots = _group_roots(scalp, lm, rng, az, v, half, n)
        layer = np.arange(n) % 2
        lift = np.array(FALL_LIFT)[layer] * s
        # every strand ends near the same height: 65 cm below the crown at the back, the chest in front
        tip_z = crown_z - L if kind == "b" else float(lm.P("nipple")[2]) + 0.03 * s
        length = (roots[:, 2] - tip_z) * (1.25 if kind == "b" else 1.45) + rng.uniform(-0.02, 0.02, n)
        paths, leave = drape(scalp, avoid, roots, lift, length, np.full(n, bias), lm)
        paths = _cohere(paths, avoid, COHESION[kind])
        # the group's mean strand from where its strands leave the scalp to the tips: the bone chain
        lf = float(np.median(leave / length))
        mean = paths.mean(axis=0)
        arc = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(mean, axis=0), axis=1))])
        st = np.linspace(lf * arc[-1], arc[-1], nb + 1)
        chain = np.stack([np.interp(st, arc, mean[:, k]) for k in range(3)], axis=1)
        side = "L" if az > 0 else "R"
        groups.append((f"DEF-hair_{kind}{gi + 1 if kind == 'b' else gi - len(BACK_GROUPS) + 1}", chain, side))
        wr = FALL_WIDTH if kind == "b" else FRONT_WIDTH
        widths = rng.uniform(*wr, n) * s
        slots = rng.integers(SLOTS_FULL, size=n)
        slots = np.where((layer == 1) & (rng.random(n) < 0.4), rng.choice(SLOTS_SPARSE, n), slots)
        ph = rng.random(n)
        yc = float(lm.P("head_c")[1])
        for c in range(n):
            pts = paths[c]
            out = np.stack([pts[:, 0], pts[:, 1] - yc, np.zeros(len(pts))], axis=1)
            nrm = np.where(np.linalg.norm(out, axis=1, keepdims=True) > 1e-6, out, np.array([[0.0, 1.0, 0.0]]))
            on = _head_sd(scalp, pts) < float(lift[c]) + LEAVE_SDF
            if on.any():  # on the scalp the card lies in its tangent plane
                nrm[on] = scalp.normal(pts[on])
            nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
            first = len(part.V)
            _ribbon(part, pts, nrm, float(widths[c]), int(slots[c]),
                    lambda t, p=float(ph[c]): (0.6 * t * t, 0.4 * t, p, 0.2 * t), taper=0.3)
            cards.append((first, pts, gi, float(leave[c] / length[c])))
    return part, cards, groups


def build_hair(lm, body, params: dict, scalp=None, avoid=None) -> tuple[dict[str, Part], list, list]:
    """`scalp`: MeshScalp on the shipped head (build_sefir), the anatomy field when omitted; `avoid(P)`: signed
    clearance from everything under the fall (body under its clothes, mantle). Returns ({name: Part}, cards, groups)."""
    scalp = scalp or Scalp(body)
    rng = np.random.default_rng([int(params["seed"]), 0])
    out = {"HairScalp": scalp_cards(lm, params, rng, scalp)}
    out["HairScalp"].C = [STILL] * len(out["HairScalp"].V)
    if avoid is None:
        avoid = lambda P: np.full(len(P), 1.0)  # noqa: E731
    back, cards, groups = fall(lm, params, np.random.default_rng([int(params["seed"]), 1]), scalp, avoid)
    out["HairBack"] = back
    return out, cards, groups


def hair_surface(scalp, lift: float):
    """Points projected onto the hair's outer surface (the scalp plus `lift`): the crown's band sits on it."""
    return lambda P: scalp.project(P, lift)
