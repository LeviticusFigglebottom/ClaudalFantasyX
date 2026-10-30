"""The trader's deck cargo as lashed bales (env-art-b, M3-ENV-1326; the trader_boat ask of M3-ENV-1316). Pure numpy.

  trader_cargo  the four bales on `trader_boat`'s deck (cw_story.build_trader_boat's cargo, which are plain rounded
                boxes in `cw_sail`): each a soft canvas-wrapped bundle a little larger than its box (so the box stays
                inside it), bellied and sagging, lashed by two rope bands round its width and one along its length.
                Placed at the boat's own transform, in the boat's frame (origin at its keel's centre, bow -Z).

Ch7's port and Ch8's Corrow place it over the boat (tools/act1/ch07_tamsule_port_dressing.py, ch08_corrow_dressing.py),
following the boat's block.
"""

from __future__ import annotations

import math

import numpy as np

import cw_common as cw
from cw_common import kc

M_SAIL = "cw_sail"  # cw_story's canvas slot (the zones swap it for their weathered canvas)
TRI_BUDGET = {"trader_cargo": (9000, 600)}
# cw_story.build_trader_boat's cargo: (x, z, s) -> a box centred (x, 1.49 + 0.8 s, z), half extents (s, 0.8 s, 0.9 s)
BALES = ((-0.6, 1.2, 0.5), (0.6, 1.4, 0.45), (0.0, 2.6, 0.55), (-0.5, 3.4, 0.4))
DECK_Y = 1.49
MARGIN_M = 0.09  # past the box's faces: more than the rounding takes off its corners (RADIUS_M (sqrt 3 - 1) / sqrt 3)
RADIUS_M = 0.16
ROPE_R = 0.018
BAND_OUT_M = 0.012  # the lashing's centreline off the canvas


def _band(cx: float, cy: float, a: float, b: float, n: int) -> np.ndarray:
    """A closed loop round a (2a x 2b) rounded rectangle centred (cx, cy): a squircle, so it hugs the bale."""
    t = np.linspace(0.0, 2.0 * math.pi, n, endpoint=True)
    c, s = np.cos(t), np.sin(t)
    p = 6.0
    x = a * np.sign(c) * np.abs(c) ** (2.0 / p)
    y = b * np.sign(s) * np.abs(s) ** (2.0 / p)
    return np.stack([cx + x, cy + y], axis=-1)


def build_trader_cargo(seed: int = 931) -> list:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("trader_cargo", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder("trader_cargo" + (cw.LOD if lod else ""))
        cloth, rope = mb.material(M_SAIL), mb.material(cw.M_ROPE)
        for x, z, s in BALES:
            half = np.array([s, 0.8 * s, 0.9 * s]) + MARGIN_M
            half[1] -= MARGIN_M * 0.5  # sits on the deck: the extra height goes up, not through the planks
            cy = DECK_Y + half[1]
            kc.rounded_block(mb, (x, cy, z), tuple(half), cloth, radius=RADIUS_M, seg=1 if lod else 4,
                             noise=None if lod else noise, disp_m=0.035, disp_period_m=0.35, weather=cw.TOWN_W,
                             variation=float(rng.random()))
            if lod:
                continue
            ax, ay, az = half + BAND_OUT_M
            for dz in (-0.45, 0.45):  # two bands round its width (in x-y), a third along it (in z-y)
                loop = _band(x, cy, ax, ay, 33)
                pts = np.stack([loop[:, 0], loop[:, 1], np.full(len(loop), z + dz * az)], axis=-1)
                kc.tube(mb, pts, ROPE_R, 4, rope, variation=float(rng.random()), u_repeat=3.0)
            loop = _band(z, cy, az, ay, 33)
            pts = np.stack([np.full(len(loop), x + rng.uniform(-0.08, 0.08)), loop[:, 1], loop[:, 0]], axis=-1)
            kc.tube(mb, pts, ROPE_R, 4, rope, variation=float(rng.random()), u_repeat=3.0)
        out.append(mb)
    return out


TARGETS = {"trader_cargo": build_trader_cargo}
