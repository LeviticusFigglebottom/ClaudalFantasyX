"""The tideline at dusk and the Order's torches (M3-C06-03 items 3 and 6; act1_ch06.md §9.5, B09 "The Burned Lamp").
Pure numpy; see bs_common.py.

  lamp_hole_open      the hole Liss dug in the wet sand for the lamp (block LampHole 0.6 x 0.6): a scooped pit 0.3 m
                      deep, the spoil heaped on its landward side (-X), finger-drags down its walls; 1.2 m across
  lamp_hole_covered   the same patch filled back in: a low mound of fresh-turned sand, darker and wetter than the
                      beach, a hand pressed flat into its top (Liss's, or Rhen's if he dug without asking)
  hand_print          a single hand-print in the wet sand, fingers toward +Z, for the tideline's insert shot
  stillguard_torch    the Stillguard's torch: a 2.2 m iron haft banded in the Order's red lacquer, a brass cup with a
                      pitch-soaked wrap glowing in it (the flames are VFX, as ridge_fire's); origin at its foot

Origins: on the ground at the centre; the sand pieces are square patches whose edges lie flush with it (4 mm proud, so they never z-fight the
flats). Every sand piece is the kit's mud, wet (the tideline's sand is the flats' silt).
"""

from __future__ import annotations

import math

import numpy as np

import bs_common as bc
from bs_common import kc

TRI_BUDGET = {"lamp_hole": (5000, 200), "hand_print": (2400, 60), "stillguard_torch": (1500, 120)}
BUDGET_KEY = {"lamp_hole_open": "lamp_hole", "lamp_hole_covered": "lamp_hole"}

PATCH_R = 0.6
PIT_R = 0.3
PIT_DEPTH = 0.3
RIM_Y = 0.004
WET = kc.Weathering(moss=0.0, salt=0.05, wet=1.0, erosion=0.2, noise_scale_m=0.3)
HAND = ((0.0, 0.0, 0.055, 0.075),  # palm (x, z, half-width, half-length), fingers toward +Z
        (-0.042, 0.11, 0.011, 0.034), (-0.014, 0.125, 0.011, 0.04), (0.014, 0.122, 0.011, 0.038),
        (0.04, 0.105, 0.01, 0.03), (0.07, 0.02, 0.012, 0.03))  # four fingers, the thumb out to +X


def _hand_depth(X, Z, depth: float) -> np.ndarray:
    """A hand pressed into sand: soft ellipses for the palm, fingers and thumb, `depth` deep at their centres."""
    d = np.zeros_like(X)
    for k, (cx, cz, hw, hl) in enumerate(HAND):
        th = 0.6 if k == len(HAND) - 1 else 0.0  # the thumb splays
        dx, dz = X - cx, Z - cz
        u = (dx * math.cos(th) - dz * math.sin(th)) / hw
        v = (dx * math.sin(th) + dz * math.cos(th)) / hl
        d = np.maximum(d, depth * np.clip(1.0 - (u * u + v * v), 0.0, 1.0) ** 0.6)
    return d


def _patch(mb: kc.MeshBuilder, radius: float, cells: int, height, mat: str, rng) -> None:
    """A square heightfield patch 2 x `radius` across (`cells` per side, fine enough for fingers):
    `height(X, Z)` -> Y inside the circle of `radius`, easing to RIM_Y at it and flat beyond (flush with the flats)."""
    v = np.linspace(-radius, radius, cells + 1)
    X, Z = np.meshgrid(v, v)
    R = np.hypot(X, Z)
    fade = 1.0 - kc.smoothstep(radius * 0.75, radius, R)  # every disturbance eases out to the flats at the rim
    Y = RIM_Y + (height(X, Z) - RIM_Y) * fade
    P = np.stack([X, Y, Z], -1)
    wet = np.clip(0.7 + 0.3 * (1.0 - R / radius), 0, 1)
    col = np.stack([np.zeros_like(Y), np.full_like(Y, WET.salt), wet, np.full_like(Y, 0.4)], -1)
    kc.quad_strip(mb, P, mb.material(mat), uv=np.stack([X, Z], -1) / 0.8, col=col,
                  uv2=np.array([0.9, float(rng.random())]), flip=True)


def build_lamp_hole(seed: int = 741, *, covered: bool = False) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("lamp_hole", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(("lamp_hole_covered" if covered else "lamp_hole_open") + (bc.LOD if lod else ""))

        def height(X, Z):
            R = np.hypot(X, Z)
            n = noise.fbm(np.stack([X * 6.0, np.zeros_like(X), Z * 6.0], -1), 3) - 0.5
            edge = 1.0 - kc.smoothstep(PATCH_R * 0.6, PATCH_R, R)  # the disturbed sand fades into the flats
            if covered:
                mound = 0.06 * np.clip(1.0 - (R / (PIT_R * 1.5)) ** 2, 0.0, 1.0)
                return RIM_Y + mound + n * 0.012 * edge - _hand_depth(X + 0.02, Z + 0.01, 0.018)
            pit = -PIT_DEPTH * np.clip(1.0 - (R / PIT_R) ** 2, 0.0, 1.0) ** 0.8
            drags = 0.015 * np.sin(np.arctan2(Z, X) * 9.0) * kc.smoothstep(PIT_R * 0.4, PIT_R, R) * (R < PIT_R)
            spoil = 0.11 * np.clip(1.0 - np.hypot(X + 0.34, Z * 0.8) / 0.2, 0.0, 1.0) ** 0.7  # landward (-X)
            return RIM_Y + pit + drags + spoil + n * 0.02 * edge

        _patch(mb, PATCH_R, 8 if lod else 48, height, bc.M_MUD, rng)
        out.append(mb)
    return out


def build_hand_print(seed: int = 742) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("hand_print", seed)
        mb = kc.MeshBuilder("hand_print" + (bc.LOD if lod else ""))
        _patch(mb, 0.22, 2 if lod else 32, lambda X, Z: RIM_Y - (0.0 if lod else 1.0) * _hand_depth(X, Z - 0.03, 0.014),
               bc.M_MUD, rng)
        out.append(mb)
    return out


def build_torch(seed: int = 743) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("stillguard_torch", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("stillguard_torch" + (bc.LOD if lod else ""))
        sides = 4 if lod else 7
        kc.tube(mb, np.array([[0.0, 0.0, 0.0], [0.0, 2.0, 0.0]]), np.array([0.022, 0.018]), sides,
                mb.material(bc.M_IRON), weather=bc.CAMP, cap_start=True)
        if not lod:
            for y in (0.9, 1.35, 1.8):  # the Order's red lacquer bands
                kc.tube(mb, np.array([[0.0, y, 0.0], [0.0, y + 0.08, 0.0]]), 0.026, sides, mb.material(bc.M_RED),
                        cap_start=True, cap_end=True)
        # The brass cup, flared, and the pitch-soaked wrap glowing in it.
        kc.tube(mb, np.array([[0.0, 1.98, 0.0], [0.0, 2.08, 0.0], [0.0, 2.2, 0.0]]), np.array([0.03, 0.065, 0.085]),
                6 if lod else 12, mb.material(bc.M_BRASS), cap_start=True)
        kc.rounded_block(mb, (0.0, 2.17, 0.0), (0.06, 0.05, 0.06), mb.material(bc.M_EMBER), radius=0.04,
                         seg=1 if lod else 2, noise=None if lod else noise, disp_m=0.008)
        out.append(mb)
    return out


TARGETS = {
    "lamp_hole_open": lambda: build_lamp_hole(covered=False),
    "lamp_hole_covered": lambda: build_lamp_hole(covered=True),
    "hand_print": build_hand_print,
    "stillguard_torch": build_torch,
}
