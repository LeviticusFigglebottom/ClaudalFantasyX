"""Rhen's hair cards (no bpy), rhen.md §5 and the hair contract in character_shading.md.

Short (4-7 cm), wind-ruffled hair, the crown swept forward and to his left; dark brown roots that
bleach to copper over the outer 40% of each strand (the colour is the hair shader's `tip_start`
over the atlas's root-to-tip channel, so the cards only carry V root 0 -> tip 1).

* **Flow**: away from a crown whorl behind the top of the head. Over the top it turns forward and
  to his left (+X); down the sides and the back it falls with gravity toward the nape and ears.
* **Scalp**: a hairline row on the soft-root atlas columns plus three lifted layers of short cards
  traced over the shipped head mesh (asha_hair.MeshScalp) along the flow.
* **Tufts**: short clumps on the crown and at the front whose tips rise off the scalp (ruffled), so
  the silhouette is broken, not a cap.
* **Flyaways**: a few thin, low-alpha strands at the crown and the temples.

It reuses Asha's card machinery (asha_hair: Scalp, MeshScalp, _ribbon, the atlas column layout) and
supplies the same hairline and flow interface asha_textures reads (`hairline_v`, `in_hair`,
`_gather`, `_flow_dir`), so the skin maps paint the scalp under these cards. Vertex colour = wind
(scalp cards pinned at the root, the tips free: rhen.md §5 "wind response 0.25 on the outer layer").
Seeded, deterministic.
"""
from __future__ import annotations

import math

import numpy as np

import asha_hair
from asha_hair import CLUMPS, ROOT_CAST_H, SLOTS_FULL, SLOTS_HAIRLINE, SLOTS_SPARSE, MeshScalp, Scalp, _ribbon  # noqa: F401
from asha_mesh import Part

TAG_HAIR = asha_hair.TAG_HAIR
WIND_OUTER = 0.25  # rhen.md §5: the outer layer's wind response
FRINGE_SPILL = 0.07  # head heights a strand may run past the hairline (the fringe falls ~1.5 cm onto the brow)
FRINGE_STAGGER = (0.2, 1.6)  # each crop card's own share of FRINGE_SPILL: the fringe's ends stagger (liss_review.md)


def hairline_v(lm, P: np.ndarray) -> np.ndarray:
    """Hairline height (head heights above the chin) by azimuth round the head axis (0 = front, +90 =
    his left). A man's hairline: a little lower and squarer at the front than Asha's, slightly
    receded at the temples, short sideburns in front of the ears, and a low nape."""
    yc = lm.P("head_c")[1]
    phi = np.degrees(np.arctan2(P[:, 0], -(P[:, 1] - yc)))
    a = np.abs(phi)
    xs = [0, 22, 38, 52, 64, 74, 82, 92, 104, 118, 140, 162, 180]
    vs = [0.712, 0.710, 0.700, 0.682, 0.640, 0.575, 0.525, 0.585, 0.585, 0.47, 0.30, 0.235, 0.225]
    t = np.radians(phi)
    wander = 0.004 * np.sin(9.0 * t + 0.7) + 0.003 * np.sin(17.0 * t + 1.9) + 0.0015 * np.sin(31.0 * t + 0.2)
    return np.interp(a, xs, vs) + wander


def in_hair(lm, P: np.ndarray, margin_h: float = 0.0) -> np.ndarray:
    zc = lm.P("chin")[2]
    v = (P[:, 2] - zc) / lm.h
    return v > hairline_v(lm, P) + margin_h


def _gather(lm) -> np.ndarray:
    """The crown whorl (the point the flow leaves from). Named after Asha's braid gather so
    asha_textures can call it through the same interface."""
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    return np.array([-0.06 * lm.head_w, yc + 0.20 * lm.h, zc + 1.0 * lm.h])


def _flow_dir(lm, P: np.ndarray, N: np.ndarray, G: np.ndarray) -> np.ndarray:
    """Tangent flow away from the whorl: forward and to his left over the top, down at the sides
    and the back."""
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    away = P - G
    away /= np.maximum(np.linalg.norm(away, axis=1, keepdims=True), 1e-9)
    v = (P[:, 2] - zc) / lm.h
    top = np.clip((v - 0.70) / 0.18, 0.0, 1.0)  # 0 on the sides, 1 on the crown
    front = np.clip(-(P[:, 1] - yc) / (0.35 * lm.h), 0.0, 1.0)
    sweep = np.array([0.55, -1.0, 0.0])  # over the crown: forward (-Y) and to his left (+X)
    fringe = np.array([1.0, -0.3, 0.25])  # at the hairline the front lies across the forehead to his left
    down = np.array([0.0, 0.25, -1.0])
    hl = np.clip((hairline_v(lm, P) + 0.09 - v) / 0.09, 0.0, 1.0) * front  # 1 at the front hairline
    d = (away * 0.8 * (1.0 - hl)[:, None] + sweep[None, :] * (top * (0.6 + 0.5 * front) * (1.0 - hl))[:, None]
         + fringe[None, :] * (1.6 * hl)[:, None] + down[None, :] * ((1.0 - top) * (1.0 - hl))[:, None] * 0.9)
    d = d - np.sum(d * N, axis=1, keepdims=True) * N
    return d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)


def _trace(scalp, lm, roots: np.ndarray, length: np.ndarray, lift: float, G: np.ndarray, seg: int,
           rise: np.ndarray | None = None) -> np.ndarray:
    """Paths of `seg` steps along the flow; `rise` (per root, m) lifts the outer part of each path
    off the scalp (the ruffle), growing with the square of the distance along it."""
    return _trace_kept(scalp, lm, roots, length, lift, G, seg, rise)[0]


def _trace_kept(scalp, lm, roots: np.ndarray, length: np.ndarray, lift: float, G: np.ndarray, seg: int,
                rise: np.ndarray | None = None, spill: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """_trace, plus how many points each path keeps: a path ends where it would pass the hairline by more than its
    own `spill` (head heights at the front; default FRINGE_SPILL), so the fringe's ends stagger instead of piling up
    on one line (liss_review.md: the hard fringe edge)."""
    spill = np.full(len(roots), FRINGE_SPILL) if spill is None else spill
    keep = np.full(len(roots), seg + 1)
    step = length / seg
    paths = [scalp.project(roots, lift)]
    for k in range(seg):
        cur = paths[-1]
        N = scalp.normal(cur)
        nxt = scalp.project(cur + _flow_dir(lm, cur, N, G) * step[:, None], lift, iters=3)
        # short hair stops at the hairline: a strand never runs more than ~1 cm onto bare skin
        yc = lm.P("head_c")[1]
        front = np.clip(-(nxt[:, 1] - yc) / (0.3 * lm.h), 0.0, 1.0) ** 2  # the spill is for the fringe only
        zc = lm.P("chin")[2]
        ok = (nxt[:, 2] - zc) / lm.h > hairline_v(lm, nxt) - spill * front - 0.01
        nxt = np.where(ok[:, None], nxt, cur)
        stopped = ~ok & (keep > k + 1)
        keep[stopped] = k + 1
        paths.append(nxt)
    out = np.stack(paths, axis=1)
    if rise is not None:
        t = (np.arange(seg + 1) / seg) ** 2
        N = scalp.normal(out.reshape(-1, 3)).reshape(out.shape)
        out = out + N * (rise[:, None] * t[None, :])[..., None]
    return out, keep


def _emit_kept(part: Part, scalp, paths: np.ndarray, keep: np.ndarray, widths, slots, rng, taper: float, v_range,
               wind: float, twist: float = 0.0) -> None:
    """_emit for the paths that keep at least two points, each cut where it stopped (its V range cut with it)."""
    for c in range(len(paths)):
        k = int(keep[c])
        if k < 2:
            rng.random()  # keep the stream aligned whether or not a card is emitted
            continue
        _emit(part, scalp, paths[c:c + 1, :k], widths[c:c + 1], slots[c:c + 1], rng, taper,
              (v_range[0], v_range[0] + (v_range[1] - v_range[0]) * (k - 1) / (paths.shape[1] - 1)), wind, twist)


def _roots_inside(scalp, lm, rng, n: int, margin: float, G: np.ndarray) -> np.ndarray:
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    hc = np.array([0.0, yc, zc + 0.55 * lm.h])
    d_in = rng.normal(size=(n * 6, 3))
    d_in[:, 2] = np.abs(d_in[:, 2]) * 1.2 + 0.05
    d_in /= np.linalg.norm(d_in, axis=1, keepdims=True)
    p_in = scalp.project(hc + d_in * ROOT_CAST_H * lm.h)
    ok = in_hair(lm, p_in, margin)
    return p_in[ok][:n]


def _hairline_roots(scalp, lm, phi: np.ndarray, inside_h) -> np.ndarray:
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


def _emit(part: Part, scalp, paths: np.ndarray, widths, slots, rng, taper: float, v_range, wind: float,
          twist: float = 0.0) -> None:
    for c in range(len(paths)):
        pts = paths[c]
        nrm = scalp.normal(pts)
        if twist:
            T = np.gradient(pts, axis=0)
            T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
            side = np.cross(T, nrm)
            a = rng.uniform(-twist, twist) * np.linspace(0.0, 1.0, len(pts))
            nrm = nrm * np.cos(a)[:, None] - side * np.sin(a)[:, None]
        ph = float(rng.random())
        _ribbon(part, pts, nrm, float(widths[c]), int(slots[c]),
                lambda t, ph=ph: (wind * t * t, 0.5 * wind * t, ph, 0.3 * wind * t), taper=taper, v_range=v_range)


def scalp_cards(lm, params: dict, rng: np.random.Generator, scalp) -> Part:
    part = Part("HairScalp")
    G = _gather(lm)
    s = lm.h / 0.222
    lo, hi = params["length_m"]
    seg = 6
    lim = math.pi * 0.97
    n_hl = int(params.get("hairline_cards", 0))
    if n_hl:
        phi = np.linspace(-lim, lim, n_hl) + rng.uniform(-0.4, 0.4, n_hl) * (2 * lim / n_hl)
        roots = _hairline_roots(scalp, lm, np.sort(phi), rng.uniform(-0.001, 0.007, n_hl))
        length = rng.uniform(0.6 * lo, lo, n_hl) * s
        paths, keep = _trace_kept(scalp, lm, roots, length, 0.0009 * s, G, 4, rng.uniform(0.0, 0.002, n_hl) * s,
                                  rng.uniform(*FRINGE_STAGGER, n_hl) * FRINGE_SPILL)
        _emit_kept(part, scalp, paths, keep, rng.uniform(0.004, 0.007, n_hl) * s, rng.choice(SLOTS_HAIRLINE, n_hl),
                   rng, 0.3, (0.0, 0.75), 0.0)
    layers = [(0.0012 * s, params["scalp_cards"][0], (0.010, 0.017), 0.002, 0.0),
              (0.0026 * s, params["scalp_cards"][1], (0.007, 0.012), 0.004, 0.5 * WIND_OUTER),
              (0.0042 * s, params["scalp_cards"][2], (0.005, 0.009), 0.007, WIND_OUTER)]
    for li, (lift, count, wr, rise, wind) in enumerate(layers):
        if not count:
            continue
        roots = _roots_inside(scalp, lm, rng, count, 0.012 + 0.01 * li, G)
        n = len(roots)
        length = rng.uniform(lo, hi, n) * s
        paths, keep = _trace_kept(scalp, lm, roots, length, lift, G, seg, rng.uniform(0.3, 1.0, n) * rise * s,
                                  rng.uniform(*FRINGE_STAGGER, n) * FRINGE_SPILL)
        if li == 2:
            slots = np.where(rng.random(n) < 0.5, rng.choice(SLOTS_SPARSE, n), rng.integers(SLOTS_FULL, size=n))
        else:
            slots = rng.integers(SLOTS_FULL, size=n)
        _emit_kept(part, scalp, paths, keep, rng.uniform(*wr, n) * s, slots, rng, 0.4, (0.0, 0.85), wind, 0.25 * li)
    return part


def tufts(lm, params: dict, rng: np.random.Generator, scalp) -> Part:
    """Ruffled clumps on the crown and at the front: 2-4 cards that share a path, gather toward the
    tip (cut hair clumps at the ends) and stand off the scalp, more at the front where the sweep
    lifts it."""
    part = Part("HairTufts")
    n = int(params.get("tufts", 0))
    if not n:
        return part
    G = _gather(lm)
    s = lm.h / 0.222
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    lo, hi = params["length_m"]
    roots = _roots_inside(scalp, lm, rng, n * 3, 0.03, G)
    v = (roots[:, 2] - zc) / lm.h
    keep = v > 0.70  # the crown and the top of the front
    roots = roots[keep][:n]
    m = len(roots)
    front = np.clip(-(roots[:, 1] - yc) / (0.3 * lm.h), 0.0, 1.0)
    length = rng.uniform(0.9 * lo, 1.1 * hi, m) * s
    rise = (0.004 + 0.008 * front) * rng.uniform(0.6, 1.2, m) * s
    paths = _trace(scalp, lm, roots, length, 0.0045 * s, G, 6, rise)
    for c in range(m):
        C = paths[c]
        N = scalp.normal(C)
        T = np.gradient(C, axis=0)
        T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
        side = np.cross(T, N)
        side /= np.maximum(np.linalg.norm(side, axis=1, keepdims=True), 1e-12)
        t = np.linspace(0.0, 1.0, len(C))
        k = int(rng.integers(2, 5))
        spread = rng.uniform(0.0025, 0.005) * s
        gather = 1.0 - 0.6 * t
        for j in range(k):
            f = (j - (k - 1) / 2) / max((k - 1) / 2, 1)
            pts = C + side * (f * spread * gather)[:, None] + N * (0.0012 * s * (1 - abs(f)) * np.sin(math.pi * t))[:, None]
            a = rng.uniform(-0.4, 0.4) * t
            nrm = N * np.cos(a)[:, None] - side * np.sin(a)[:, None]
            slot = int(rng.choice(SLOTS_SPARSE)) if rng.random() < 0.4 else int(rng.integers(SLOTS_FULL))
            ph = float(rng.random())
            _ribbon(part, pts, nrm, float(rng.uniform(0.0035, 0.006) * s), slot,
                    lambda t, ph=ph: (WIND_OUTER * t * t, 0.5 * WIND_OUTER * t, ph, 0.4 * WIND_OUTER * t),
                    taper=0.6, v_range=(0.05, 0.9))
    return part


def flyaways(lm, params: dict, rng: np.random.Generator, scalp) -> Part:
    part = Part("HairFlyaways")
    n = int(params.get("flyaways", 0))
    if not n:
        return part
    G = _gather(lm)
    s = lm.h / 0.222
    lo, hi = params["length_m"]
    roots = _roots_inside(scalp, lm, rng, n, 0.04, G)
    m = len(roots)
    paths = _trace(scalp, lm, roots, rng.uniform(lo, 1.2 * hi, m) * s, 0.005 * s, G, 5,
                   rng.uniform(0.006, 0.014, m) * s)
    for c in range(m):
        ph = float(rng.random())
        _ribbon(part, paths[c], scalp.normal(paths[c]), float(rng.uniform(0.0012, 0.002) * s),
                int(rng.choice(SLOTS_SPARSE)), lambda t, ph=ph: (WIND_OUTER * t, WIND_OUTER * t, ph, 0.5 * t),
                taper=0.5, v_range=(0.1, 0.95), u_range=(0.3, 0.7))
    return part


def build_hair(lm, body, params: dict, scalp=None) -> dict[str, Part]:
    """`scalp`: MeshScalp on the shipped head (build_rhen); the anatomy field when omitted."""
    scalp = scalp or Scalp(body)
    seed = int(params["seed"])
    out = {"HairScalp": scalp_cards(lm, params, np.random.default_rng([seed, 0]), scalp),
           "HairTufts": tufts(lm, params, np.random.default_rng([seed, 1]), scalp),
           "HairFlyaways": flyaways(lm, params, np.random.default_rng([seed, 2]), scalp)}
    for p in out.values():
        p.C = p.C + [(0.0, 0.0, 0.0, 0.0)] * (len(p.V) - len(p.C))
    return out
