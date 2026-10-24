"""Rhen's hair cards (no bpy), rhen.md §5 and the hair contract in character_shading.md.

Short (4-7 cm), wind-ruffled hair: the crown swept forward and to his left (+X), dark brown roots
grading to sun-bleached copper tips (the shader's col_root -> col_tip over the atlas's R channel).

* **Hairline row**: short, narrow cards on the soft-root atlas columns, so the hairline is a fringe of
  strands over the scalp underpaint, not a drawn line (asha_hair's M1-CHR-04 lesson).
* **Three layers** (base, mid, top), rooted inside the hairline and traced over the scalp along a
  flow field that radiates from a crown whorl and turns forward-left over the top. The tips lift off
  the scalp, more in the top layer: short hair stands up where it is cut, which is the ruffle.
* **Flyaways**: a few thin cards standing off the crown, breaking the silhouette.

The module exposes the interface asha_textures.skin_maps reads for the scalp paint (`hairline_v`,
`in_hair`, `_gather`, `_flow_dir`), so the same skin generator paints Rhen's scalp. Cards reuse
asha_hair's ribbon builder and the shared 16-column strand atlas (asha_textures.hair_atlas). Vertex
colour = wind weights (R primary, G secondary, B phase, A flutter): pinned at the root, the outer
layer free at the tip (rhen.md §5: wind response 0.25 on the outer layer). Seeded, deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from asha_hair import CLUMPS, SLOTS_FULL, SLOTS_HAIRLINE, SLOTS_SPARSE, Scalp, _ribbon  # noqa: F401
from asha_mesh import Part

ROOT_CAST_H = 0.6  # head heights: root candidates are cast from outside the skull (asha_hair)
# Layers: (lift at the root, extra lift at the tip, card width range), metres at s = 1. The tips
# stand off the scalp (the cut ends of short hair), the top layer most: that is the ruffle.
LAYERS = ((0.0012, 0.0030, (0.010, 0.016)), (0.0026, 0.0055, (0.007, 0.012)), (0.0040, 0.0090, (0.005, 0.009)))
TOP_WIND = 0.25  # rhen.md §5: outer-layer wind response
SEG = 6  # path steps per card: 7-12 mm each for 4-7 cm hair


def hairline_v(lm, P: np.ndarray) -> np.ndarray:
    """Hairline height (head heights above the chin) by azimuth round the head axis: 0 = front,
    +90 = his left. A young man's hairline: a slightly squarer front than Asha's, the temples a
    touch higher (a shallow temple recession) and a short-cut back of the neck."""
    yc = lm.P("head_c")[1]
    phi = np.degrees(np.arctan2(P[:, 0], -(P[:, 1] - yc)))
    a = np.abs(phi)
    xs = [0, 18, 34, 50, 66, 78, 88, 100, 120, 140, 160, 180]
    vs = [0.772, 0.770, 0.752, 0.71, 0.655, 0.60, 0.585, 0.60, 0.50, 0.37, 0.31, 0.30]
    t = np.radians(phi)
    wander = 0.004 * np.sin(7.0 * t + 0.7) + 0.003 * np.sin(13.0 * t + 1.9) + 0.0015 * np.sin(29.0 * t + 0.2)
    return np.interp(a, xs, vs) + wander


def in_hair(lm, P: np.ndarray, margin_h: float = 0.0) -> np.ndarray:
    zc = lm.P("chin")[2]
    v = (P[:, 2] - zc) / lm.h
    return v > hairline_v(lm, P) + margin_h


def _gather(lm) -> np.ndarray:
    """The crown whorl: the point the hair grows away from (back of the crown, slightly to his right)."""
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    return np.array([-0.04 * lm.h, yc + 0.20 * lm.h, zc + 1.0 * lm.h])


def _flow_dir(lm, P: np.ndarray, N: np.ndarray, G: np.ndarray) -> np.ndarray:
    """Tangent flow: away from the whorl, turned forward and to his left over the top and front,
    and down at the sides and back (short hair falls with gravity where it is not combed)."""
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    away = P - G
    d = away / np.maximum(np.linalg.norm(away, axis=1, keepdims=True), 1e-9)
    v = (P[:, 2] - zc) / lm.h
    top = np.clip((v - 0.72) / 0.2, 0.0, 1.0)  # over the top of the head
    front = np.clip(-(P[:, 1] - yc) / (0.35 * lm.h), 0.0, 1.0)
    sweep = np.array([0.45, -1.0, 0.0])  # forward (-Y) and to his left (+X)
    sweep = sweep / np.linalg.norm(sweep)
    down = np.array([0.0, 0.15, -1.0])
    d = d + sweep * (0.9 * top + 0.6 * front)[:, None] + down * (0.5 * (1.0 - top) * (1.0 - front))[:, None]
    d = d - np.sum(d * N, axis=1, keepdims=True) * N
    return d / np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-9)


def _trace(scalp, lm, roots: np.ndarray, length: np.ndarray, lift: float, G: np.ndarray, seg: int) -> np.ndarray:
    step = length / seg
    paths = [scalp.project(roots, lift)]
    for _ in range(seg):
        cur = paths[-1]
        N = scalp.normal(cur)
        nxt = scalp.project(cur + _flow_dir(lm, cur, N, G) * step[:, None], lift, iters=2)
        paths.append(nxt)
    return np.stack(paths, axis=1)


def _roots_inside(scalp, lm, rng: np.random.Generator, n: int, margin_h: float) -> np.ndarray:
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    hc = np.array([0.0, yc, zc + 0.55 * lm.h])
    d = rng.normal(size=(n * 6, 3))
    d[:, 2] = np.abs(d[:, 2]) * 1.2 + 0.1
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    p = scalp.project(hc + d * ROOT_CAST_H * lm.h)
    return p[in_hair(lm, p, margin_h)][:n]


def _hairline_roots(scalp, lm, phi: np.ndarray, inside_h) -> np.ndarray:
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    hc = np.array([0.0, yc, zc + 0.55 * lm.h])
    d = np.stack([np.sin(phi), -np.cos(phi), np.zeros(len(phi))], axis=1)
    p = scalp.project(hc + d * ROOT_CAST_H * lm.h)
    for _ in range(10):
        dz = (zc + (hairline_v(lm, p) + inside_h) * lm.h) - p[:, 2]
        p = scalp.project(p + np.stack([np.zeros(len(p)), np.zeros(len(p)), dz], axis=1))
    return p


def _emit(part: Part, scalp, paths: np.ndarray, widths, slots, tip_lift, wind: float, rng, v_range) -> None:
    """Cards along `paths`, the tips lifted off the scalp by `tip_lift` (per card) on a t^1.7 ramp."""
    for c in range(len(paths)):
        pts = paths[c]
        nrm = scalp.normal(pts)
        t = np.linspace(0.0, 1.0, len(pts))
        pts = pts + nrm * (float(tip_lift[c]) * t ** 1.7)[:, None]
        ph = float(rng.random())
        _ribbon(part, pts, nrm, float(widths[c]), int(slots[c]),
                lambda t, ph=ph: (wind * t ** 1.5, 0.5 * wind * t, ph, 0.3 * wind * t), taper=0.5, v_range=v_range)


def scalp_cards(lm, params: dict, rng: np.random.Generator, scalp) -> Part:
    part = Part("HairScalp")
    G = _gather(lm)
    s = lm.h / 0.222
    lo, hi = params["length_m"]
    lim = math.pi * 0.92
    n_hl = int(params.get("hairline_cards", 0))
    if n_hl:
        phi = np.linspace(-lim, lim, n_hl) + rng.uniform(-0.4, 0.4, n_hl) * (2 * lim / n_hl)
        roots = _hairline_roots(scalp, lm, np.sort(phi), rng.uniform(-0.001, 0.008, n_hl))
        length = rng.uniform(0.6 * lo, lo, n_hl) * s
        paths = _trace(scalp, lm, roots, length, 0.0010 * s, G, 4)
        _emit(part, scalp, paths, rng.uniform(0.005, 0.009, n_hl) * s, rng.choice(SLOTS_HAIRLINE, n_hl),
              rng.uniform(0.0, 0.002, n_hl) * s, 0.0, rng, (0.0, 0.7))
    for li, ((lift, tip, wr), count) in enumerate(zip(LAYERS, params["layer_cards"])):
        roots = _roots_inside(scalp, lm, rng, int(count), 0.015)
        n = len(roots)
        length = rng.uniform(lo, hi, n) * s
        paths = _trace(scalp, lm, roots, length, lift * s, G, SEG)
        if li == 2:
            slots = np.where(rng.random(n) < 0.5, rng.choice(SLOTS_SPARSE, n), rng.integers(SLOTS_FULL, size=n))
        else:
            slots = rng.integers(SLOTS_FULL, size=n)
        _emit(part, scalp, paths, rng.uniform(*wr, n) * s, slots, rng.uniform(0.4, 1.0, n) * tip * s,
              TOP_WIND if li == 2 else 0.0, rng, (0.0, 0.8))
    return part


def flyaways(lm, params: dict, rng: np.random.Generator, scalp) -> Part:
    part = Part("HairFlyaways")
    s = lm.h / 0.222
    G = _gather(lm)
    roots = _roots_inside(scalp, lm, rng, int(params["flyaways"]), 0.08)
    for p in roots:
        p = scalp.project(p[None, :], 0.006 * s)[0]
        nrm = scalp.normal(p[None, :])[0]
        tdir = _flow_dir(lm, p[None, :], nrm[None, :], G)[0] + 0.4 * rng.normal(size=3)
        tdir -= (tdir @ nrm) * nrm
        tdir /= np.linalg.norm(tdir)
        length = rng.uniform(0.025, 0.05) * s
        up = rng.uniform(0.006, 0.014) * s
        pts = np.array([p + tdir * length * t + nrm * up * t ** 1.4 for t in np.linspace(0, 1, 5)])
        _ribbon(part, pts, np.tile(nrm, (len(pts), 1)), rng.uniform(0.0012, 0.002) * s, int(rng.integers(CLUMPS)),
                lambda t, ph=float(rng.random()): (TOP_WIND * t, 0.3 * t, ph, 0.6 * t), taper=0.3, v_range=(0.3, 1.0))
    return part


def build_hair(lm, body, params: dict, scalp=None) -> dict[str, Part]:
    """`scalp`: the surface the cards sit on (asha_hair.MeshScalp on the shipped head; the anatomy
    field when omitted). One random stream per part."""
    scalp = scalp or Scalp(body)
    seed = int(params["seed"])
    out = {"HairScalp": scalp_cards(lm, params, np.random.default_rng([seed, 0]), scalp),
           "HairFlyaways": flyaways(lm, params, np.random.default_rng([seed, 1]), scalp)}
    for p in out.values():
        p.C = p.C + [(0.0, 0.0, 0.0, 0.0)] * (len(p.V) - len(p.C))
    return out
