"""Kerrid's personal asymmetry: the nose broken flat years before he died (kerrid.md §6.1, §9). No bpy.

The donor face is already flattened and widened by the bb_params sliders (`nose_bridge_width` 1.18,
`nose_tip_projection` 0.88). `nose_break` adds the break itself as a face-space deformation of the head skin: the
bridge displaced `nose_break_m` (3 mm) toward `nose_break_side` ("L" = his left, +X), most at the break a little below
the brow, fading toward the tip and the glabella and to nothing outside the nose. It runs on the Head object's skin
vertices after the midline snap and before the face shapes are built, so every shape keeps the bent bridge.
Deterministic.
"""
from __future__ import annotations

import numpy as np

BREAK_AT = 0.42  # of the way from the brow point down to the nose tip: where the bridge bends
SIGMA_Z = 0.30  # of the brow-to-tip length: the bend's extent up and down the nose
SIGMA_X = 0.020  # m (at s = 1): the bend's extent across the face
FRONT_FROM = 0.22  # head heights in front of the head centre where the bend starts (only the nose moves)
W_MIN = 1e-3  # below this the bend is nothing (3 um at 3 mm)


def nose_weight(P: np.ndarray, lm) -> np.ndarray:
    """0..1 over the nose: 1 at the break on the midline."""
    S = lm.S
    brow, tip = lm.P("brow"), lm.P("nose_tip")
    zb = float(brow[2] + (tip[2] - brow[2]) * BREAK_AT)
    lz = max(float(brow[2] - tip[2]), 1e-3)
    yc = float(lm.P("head_c")[1])
    front = np.clip((yc - FRONT_FROM * lm.h - P[:, 1]) / (0.08 * lm.h), 0.0, 1.0)
    front = front * front * (3.0 - 2.0 * front)
    w = np.exp(-((P[:, 2] - zb) / (SIGMA_Z * lz)) ** 2 - (P[:, 0] / (SIGMA_X * S)) ** 2) * front
    return np.where(w < W_MIN, 0.0, w)  # exact zeros away from the nose: the midline snap stays exact there


def nose_break(P: np.ndarray, lm, kparams: dict) -> np.ndarray:
    """The head skin with the bridge pushed sideways (a pure x shift, so the bridge's profile is unchanged)."""
    d = float(kparams["nose_break_m"]) * lm.S
    sign = 1.0 if str(kparams.get("nose_break_side", "L")).upper() == "L" else -1.0
    out = P.copy()
    out[:, 0] = out[:, 0] + sign * d * nose_weight(P, lm)
    return out
