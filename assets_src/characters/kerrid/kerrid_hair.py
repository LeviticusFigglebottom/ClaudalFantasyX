"""Kerrid's cropped hair and short beard as card layers (no bpy), kerrid.md §5, on Toma's short-card method.

* **Hair**: grey-black, cropped short like a soldier's (6-10 mm), a squared hairline slightly receding at the temples:
  Toma's hairline, flow and crown whorl (imported from toma_hair, which is also the interface asha_textures reads:
  `hairline_v`, `in_hair`, `_gather`, `_flow_dir`), three lifted layers of single-segment tufts from Toma's own
  `toma_shorthair.png` atlas (referenced, not copied) and about 550 cards in all. A quarter of the cards are grey
  (`hair_grey`), more at the temples.
* **Beard**: short (12-18 mm) and full along the jaw and chin, the cheeks clean above the line. The moustache is
  trimmed off the lip so the mouth shows: the lip band toma_hair keeps clear is raised by `lip_trim_h` head heights.
  About 850 cards with Toma's beard method (`toma_hair.beard_cards`); they go into the Head object and build_kerrid
  gives every card vertex its nearest skin vertex's shape deltas and weights (Toma's beard-in-Head method). Grey about
  35% of the cards, heaviest at the chin (`beard_grey`).

`beard_v` / `in_beard` describe Kerrid's beard region (kerrid_textures paints the beard shadow from them). Toma's
region functions are swapped for Kerrid's only while `beard_cards` runs. Seeded, deterministic; no wind.
"""
from __future__ import annotations

import numpy as np

import toma_hair
from toma_hair import (  # noqa: F401  (the hair interface asha_textures reads)
    EDGE_BAND, SH_SPARSE, STILL, TAG_BEARD, TAG_HAIR, _columns, _emit, _flow_dir, _gather, _roots_inside, _trace,
    hairline_v, in_hair)

LIP_TRIM_H = 0.012  # head heights: default for `lip_trim_h`
TRIM_HALF_W = 1.15  # of the mouth half-width: the trimmed lens's half-width
_TOMA_BEARD_V = toma_hair.beard_v  # Toma's own region (beard_cards swaps the module's name for Kerrid's)


def beard_v(lm, face, P: np.ndarray, lip_trim_h: float = LIP_TRIM_H) -> np.ndarray:
    """Toma's beard region with the band over the upper lip widened by `lip_trim_h`: the moustache stops above the
    lip line, so the mouth shows (kerrid.md §5)."""
    base = _TOMA_BEARD_V(lm, face, P)
    u, v, phi = toma_hair._face_coords(lm, P)
    # M2-CHR-524: Toma's mouth lens, a little wider and raised by the trim (was a steep-edged box: a hard notch)
    trimmed = toma_hair.mouth_clear(lm, face, u, v, phi, TRIM_HALF_W, lip_trim_h)
    return np.minimum(base, -trimmed)


def in_beard(lm, face, P: np.ndarray, margin_h: float = 0.0, lip_trim_h: float = LIP_TRIM_H) -> np.ndarray:
    return beard_v(lm, face, P, lip_trim_h) > margin_h


def beard_cards(lm, face, params: dict, surface, V: np.ndarray, T: np.ndarray) -> toma_hair.Part:
    """toma_hair.beard_cards with Kerrid's region (the trimmed moustache)."""
    trim = float(params.get("lip_trim_h", LIP_TRIM_H))
    saved = toma_hair.beard_v
    toma_hair.beard_v = lambda lm_, face_, P_: beard_v(lm_, face_, P_, trim)  # in_beard reads it too
    try:
        return toma_hair.beard_cards(lm, face, params, surface, V, T)
    finally:
        toma_hair.beard_v = saved


def scalp_cards(lm, params: dict, rng: np.random.Generator, scalp) -> toma_hair.Part:
    """Toma's three-layer cropped scalp, with a quarter of the cards grey (more at the temples)."""
    part = toma_hair.Part("HairScalp")
    G = _gather(lm)
    lo, hi = params["length_m"]
    wlo, whi = params["card_width_m"]
    grey_share = float(params["grey_share"])
    boost = float(params.get("grey_temple_boost", 1.0))

    def flow(P, N):
        return _flow_dir(lm, P, N, G)

    layers = [(0.0008, params["scalp_cards"][0], 0.0008, 0.002),
              (0.0020, params["scalp_cards"][1], 0.0012, 0.008),
              (0.0032, params["scalp_cards"][2], 0.0016, 0.014)]
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    for li, (lift, count, rise, margin) in enumerate(layers):
        roots = _roots_inside(scalp, lm, rng, int(count), margin)
        n = len(roots)
        edge = (roots[:, 2] - zc) / lm.h < hairline_v(lm, roots) + EDGE_BAND
        paths = _trace(scalp, flow, roots, rng.uniform(lo, hi, n), lift, 1, rng.uniform(0.4, 1.0, n) * rise)
        cols = _columns(rng, n, edge, li == 2)
        # grey: a quarter overall, heavier at the temples (azimuth 50-100 degrees either side, low on the head)
        phi = np.degrees(np.arctan2(roots[:, 0], -(roots[:, 1] - yc)))
        temple = np.exp(-((np.abs(phi) - 75.0) / 25.0) ** 2) * np.clip((0.80 - (roots[:, 2] - zc) / lm.h) / 0.2,
                                                                      0.0, 1.0)
        p_grey = np.clip(grey_share * (1.0 + (boost - 1.0) * temple) / (1.0 + 0.25 * (boost - 1.0)), 0.0, 1.0)
        grey = rng.random(n) < p_grey
        mats = np.where(grey, "hair_grey", "hair")
        cols = np.where(grey, rng.choice(SH_SPARSE, n), cols)
        widths = rng.uniform(wlo, whi, n) * (1.0 - 0.1 * li) * np.where(grey, 0.7, 1.0)
        _emit(part, scalp, paths, widths, cols, rng, 0.25, list(mats))
    part.C = [STILL] * len(part.V)
    return part


def build_hair(lm, body, params: dict, scalp) -> dict:
    """`scalp`: asha_hair.MeshScalp on the shipped head (build_kerrid)."""
    return {"HairScalp": scalp_cards(lm, params, np.random.default_rng([int(params["seed"]), 0]), scalp)}
