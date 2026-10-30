"""Moll's hair (no bpy), hadric_moll.md §5: short, cropped in the Order's fashion, dark brown, grey at the temples.

Toma's short-hair method (toma_hair: three lifted layers of single-segment tufts on Toma's short-hair atlas, the
scalp shadow painted through the hairline / flow interface) with Moll's own lengths and card counts from
moll_params.json `_hair`. A man's hairline, slightly receded at the temples, is Toma's too, so the interface the
skin maps read (`hairline_v`, `in_hair`, `_gather`, `_flow_dir`) is toma_hair's, re-exported here.

The grey: each tuft is one card (one face), and a card over the temples takes the `hair_grey` material (the same
cards, the grey colours in write_materials) with a probability that rises from the crown down to the temple
hairline above the ears (`temple_grey` at full), and `grey_elsewhere` across the rest. Seeded, deterministic.
"""
from __future__ import annotations

import numpy as np

import toma_hair
from toma_hair import _flow_dir, _gather  # noqa: F401  (the skin maps' interface; hairline_v and in_hair below)
from asha_mesh import Part

GREY_MAT = "hair_grey"
TEMPLE_AZ = (40.0, 62.0, 118.0, 150.0)  # degrees from the front: the grey fades in, holds, fades out (round the ear)
TEMPLE_V = (0.80, 0.70)  # head heights above the chin: none above the first, full below the second


def smoothstep(e0: float, e1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def temple_weight(lm, P: np.ndarray) -> np.ndarray:
    """0..1: how far a point on the scalp lies in the temple band (both sides)."""
    yc = lm.P("head_c")[1]
    zc = lm.P("chin")[2]
    phi = np.abs(np.degrees(np.arctan2(P[:, 0], -(P[:, 1] - yc))))
    a0, a1, a2, a3 = TEMPLE_AZ
    band = smoothstep(a0, a1, phi) * smoothstep(a3, a2, phi)
    v = (P[:, 2] - zc) / lm.h
    return band * smoothstep(TEMPLE_V[0], TEMPLE_V[1], v)


# M3-CHR-592 (optional `_hair.front_break`, Moll's): Toma's hairline is square across the brow, so the crop ended on a
# straight line there. A broken front: within `width_deg` of the front the hairline moves up and down by up to `amp`
# head heights (two sines across the brow), the cards rooted inside it and the scalp painted to it. configure() sets
# it from the `_hair` table (build_hair, moll_textures.skin); without the key, Toma's hairline (the Stillguard crops).
FRONT_BREAK: dict = {}
FRONT_BREAK_WAVES = ((23.0, 1.7, 0.6), (41.0, 0.3, 0.4))  # (cycles per radian of azimuth, phase, share of amp)


def configure(params: dict) -> None:
    FRONT_BREAK.clear()
    FRONT_BREAK.update(params.get("front_break", {}))


def hairline_v(lm, P: np.ndarray) -> np.ndarray:
    v = toma_hair.hairline_v(lm, P)
    if not FRONT_BREAK:
        return v
    yc = lm.P("head_c")[1]
    phi = np.arctan2(P[:, 0], -(P[:, 1] - yc))
    front = np.exp(-(np.degrees(phi) / float(FRONT_BREAK["width_deg"])) ** 2)
    wave = sum(k * np.sin(f * phi + ph) for f, ph, k in FRONT_BREAK_WAVES)
    return v + float(FRONT_BREAK["amp"]) * front * wave


def in_hair(lm, P: np.ndarray, margin_h: float = 0.0) -> np.ndarray:
    return toma_hair.in_hair(lm, P, margin_h, hairline_v)


def build_hair(lm, body, params: dict, scalp=None) -> dict[str, Part]:
    """Toma's cropped cards with Moll's numbers, the temple cards turned grey."""
    configure(params)
    out = toma_hair.build_hair(lm, body, params, scalp, hairline_v if FRONT_BREAK else None)
    rng = np.random.default_rng([int(params["seed"]), 5])
    for part in out.values():
        V = part.varr()
        cen = np.array([V[list(f)].mean(axis=0) for f in part.F]) if part.F else np.zeros((0, 3))
        p = float(params["grey_elsewhere"]) + (float(params["temple_grey"]) - float(params["grey_elsewhere"])) \
            * temple_weight(lm, cen)
        grey = rng.random(len(part.F)) < p
        part.M = [GREY_MAT if g else m for g, m in zip(grey, part.M)]
    return out
