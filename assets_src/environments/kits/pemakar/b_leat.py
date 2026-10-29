"""The leat that feeds Pemakar's sea-cut weir (env-art-b, M3-ENV-1307). Pure numpy.

  weir_leat   the stone-lined channel the bottom tier's water takes down the flank to the weir (B05: the terrace
              water's last run to the sea). It comes out of a culvert mouth in tier 0's wall and drops in twelve 2 m
              steps (each a dressed bed between cheek walls, still water on it, a thin spill sheet over its lip) to
              the weir's cut. Origin at the downstream end's bed, centred; it climbs toward -Z. The steps follow the
              flank's mean slope at the weir (0.297), so each step's upstream end sits in the ground and its lip
              stands just clear of it; the cheeks and beds run 0.8 m into the ground.
"""

from __future__ import annotations

import numpy as np

import pemakar_common as pc
from pemakar_common import kc

TRI_BUDGET = {"weir_leat": (6000, 900)}

STEPS = 12
STEP_RUN_M = 2.0
STEP_RISE_M = 0.594
INNER_HALF_M = 0.5
CHEEK_T_M = 0.28
CHEEK_H_M = 0.5  # over the bed
WATER_M = 0.12  # over the bed
BURY_M = 0.8
HEAD_RUN_M = 1.9  # the culvert's basin, from the last step to the wall face
CULVERT_HALF_M = 0.42
CULVERT_H_M = 0.7


def leat(name: str, seed: int, *, lod: bool = False) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(pc.lod_name(name, lod))
    dressed = mb.material(pc.M_DRESSED)
    stone = mb.material(pc.M_STONE)
    seg = 1 if lod else 2
    half_out = INNER_HALF_M + CHEEK_T_M
    for k in range(STEPS + 1):
        head = k == STEPS
        y = k * STEP_RISE_M if not head else (STEPS - 1) * STEP_RISE_M
        z1 = -k * STEP_RUN_M
        z0 = z1 - (HEAD_RUN_M if head else STEP_RUN_M)
        zc, zh = (z0 + z1) * 0.5, (z1 - z0) * 0.5
        # The bed, set into the ground.
        kc.rounded_block(mb, (0.0, y - BURY_M * 0.5, zc), (INNER_HALF_M + 0.02, BURY_M * 0.5, zh + 0.01), dressed,
                         radius=0.03, seg=seg, noise=None if lod else noise, disp_m=0.01, weather=pc.WASHED,
                         variation=float(rng.random()))
        # The cheeks, a course of fitted stones each side.
        for sx in (-1.0, 1.0):
            n = 1 if lod else 2
            for j in range(n):
                a, b = z0 + (z1 - z0) * j / n, z0 + (z1 - z0) * (j + 1) / n
                kc.rounded_block(mb, (sx * (INNER_HALF_M + CHEEK_T_M * 0.5), y + (CHEEK_H_M - BURY_M) * 0.5,
                                      (a + b) * 0.5), (CHEEK_T_M * 0.5, (CHEEK_H_M + BURY_M) * 0.5, (b - a) * 0.5),
                                 stone, rot=kc.rot_y(float(rng.normal(0.0, 0.01))), radius=0.04, seg=seg,
                                 noise=None if lod else noise, disp_m=0.015, weather=pc.OLD,
                                 variation=float(rng.random()))
        # The still water on the step.
        pc.water_plane(mb, -INNER_HALF_M, INNER_HALF_M, z0, z1, y + WATER_M, pc.M_WATER, nx=2, nz=2 if lod else 3)
        if k > 0 and not head:
            # The lip stone and the spill sheet over it to the step below.
            kc.rounded_block(mb, (0.0, y - 0.04, z1 + 0.06), (INNER_HALF_M, 0.06, 0.08), dressed, radius=0.03, seg=1,
                             weather=pc.WASHED)
            top, bot = y + WATER_M - 0.02, y - STEP_RISE_M + WATER_M
            zs = np.array([[z1 + 0.13, z1 + 0.13], [z1 + 0.22, z1 + 0.22]])
            xs = np.array([[-INNER_HALF_M, INNER_HALF_M], [-INNER_HALF_M, INNER_HALF_M]])
            ys = np.array([[top, top], [bot, bot]])
            grid = np.stack([xs, ys, zs], axis=-1)
            kc.quad_strip(mb, grid, mb.material(pc.M_SPILL), uv=np.stack([xs, ys], axis=-1),
                          col=(0.0, 0.0, 1.0, 0.0), uv2=(1.0, 0.5), smooth=False)
    # The culvert mouth in tier 0's wall at the head: a dressed surround round a dark opening.
    zw = -STEPS * STEP_RUN_M - HEAD_RUN_M
    yb = (STEPS - 1) * STEP_RISE_M
    kc.rounded_block(mb, (0.0, yb + CULVERT_H_M * 0.5, zw - 0.05), (CULVERT_HALF_M, CULVERT_H_M * 0.5, 0.06),
                     mb.material(pc.M_DARK), radius=0.01, seg=1)
    for c, h in (((-(CULVERT_HALF_M + 0.12), yb + CULVERT_H_M * 0.5, zw + 0.06), (0.12, CULVERT_H_M * 0.5 + 0.05, 0.12)),
                 (((CULVERT_HALF_M + 0.12), yb + CULVERT_H_M * 0.5, zw + 0.06), (0.12, CULVERT_H_M * 0.5 + 0.05, 0.12)),
                 ((0.0, yb + CULVERT_H_M + 0.12, zw + 0.06), (CULVERT_HALF_M + 0.24, 0.12, 0.14))):
        kc.rounded_block(mb, c, h, dressed, radius=0.03, seg=seg, noise=None if lod else noise, disp_m=0.01,
                         weather=pc.OLD, variation=float(rng.random()))
    if not lod:
        pc.ash_pass(mb, 0, noise, 0.35, period_m=0.5, vertical=0.05)
    return mb


TARGETS = {
    "weir_leat": lambda: [leat("weir_leat", 761), leat("weir_leat", 761, lod=True)],
}
