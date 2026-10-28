"""Pemakar's mourners' votive lamp (env-art-b, M3-ENV-1305; act1_final_inventory M3-HER-1141). Pure numpy.

  votive_lamp   the small oil lamp the mourners set along the grave wall on Lanternfall night: a hand-thrown
                laterite-clay saucer 15 cm across with a pinched spout, dark oil in the bowl, a fibre wick laid in
                the spout and its teardrop flame, a frangipani flower at its foot on the odd ones. Origin at the
                saucer's foot, the spout toward +Z. It replaces the arena writer's sphere flames on
                `ash_terrace_lanternfall` (the writer's light stays: `flame` false on those rows).
"""

from __future__ import annotations

import math

import numpy as np

import pemakar_common as pc
from pemakar_common import kc

TRI_BUDGET = {"votive_lamp": (900, 160)}

SAUCER_R_M = 0.075
SAUCER_H_M = 0.038
OIL_Y_M = 0.026
SPOUT_M = 0.03
CLAY = kc.Weathering(moss=0.0, salt=0.0, wet=0.1, erosion=0.25, noise_scale_m=0.05)
STILL = kc.Weathering(moss=0, salt=0, wet=0, erosion=0)


def votive(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    rng = kc.rng_for(name, seed)
    sides = 8 if lod else 14
    # The saucer: a lathed wall from the foot ring out to the lip, its rim a touch uneven (thrown by hand).
    t = np.linspace(0.0, 1.0, 3 if lod else 5)
    centers = np.outer(t, [0.0, SAUCER_H_M, 0.0])
    radii = SAUCER_R_M * (0.62 + 0.38 * np.sin(t * math.pi * 0.5)) * (1.0 + 0.02 * rng.standard_normal(len(t)))
    kc.tube(mb, centers, radii, sides, mb.material(pc.M_BRICK), cap_start=True, weather=CLAY)
    # The pinched spout at +Z, and the oil's dark surface inside the lip.
    kc.rounded_block(mb, (0.0, SAUCER_H_M - 0.008, SAUCER_R_M + SPOUT_M * 0.3), (0.016, 0.008, SPOUT_M * 0.6),
                     mb.material(pc.M_BRICK), seg=1, radius=0.006)
    oil = np.array([[0.0, OIL_Y_M - 0.002, 0.0], [0.0, OIL_Y_M, 0.0]])
    kc.tube(mb, oil, SAUCER_R_M * 0.9, sides, mb.material(pc.M_SOOT), cap_end=True, weather=STILL)
    # The wick laid along the spout, its tip up, and the flame on it.
    tip = np.array([0.0, SAUCER_H_M + 0.004, SAUCER_R_M + SPOUT_M * 0.55])
    kc.tube(mb, np.array([[0.0, OIL_Y_M, SAUCER_R_M * 0.4], tip]), 0.0035, 4, mb.material(pc.M_TIMBER),
            weather=STILL)
    pc.flame(mb, tip, 0.055, 0.011, sides=4 if lod else 6)
    if not lod and seed % 2:
        # a frangipani flower at the foot (the offering)
        kc.rounded_block(mb, (-0.07, 0.008, -0.06), (0.022, 0.008, 0.022), mb.material(pc.M_FLOWER), seg=1,
                         radius=0.008)
    return mb


TARGETS = {
    "votive_lamp": lambda: [votive("votive_lamp", 751), votive("votive_lamp", 751, lod=True)],
}
