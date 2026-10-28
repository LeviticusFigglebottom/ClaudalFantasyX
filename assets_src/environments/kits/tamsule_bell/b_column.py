"""The Bell's weeping column (env-art-b, M3-ENV-1321; act1_ch07.md, the drop weeps into the catch pool). Pure numpy.

  weep_column        the unbroken fall from the drop's lowest point to the catch-pool (the contract, tamsule_bell.md §1:
                     radius 0.8 m at the top tapering to 0.6 m, a swimmer fits; bell.py's COLUMN_RADII): a slowly
                     twisting rope of water (a core and a looser sheath that frays toward the foot) from the pool's
                     surface up 0.3 m into the drop, a crown of spray where it lands, and two ripple rings on the
                     pool. Origin at the landing point on the pool's surface; the fall rises +Y. The port stands the
                     same piece under its own Bell.

The slots are the kit's own (`tb_drop_proxy` for the water, `tb_salt_glass` for the spray), so the kit's material set is
unchanged; the zones dress the column with their own steady, lit-from-within water materials by slot
(`tools/act1/ch07_tamsule_bell_dressing.py`, `ch07_tamsule_port_dressing.py`). The water does not animate (the Bell's
light is held, colour rule 2; the drop above it is WaterSphereRig's "tamsule_drop", M3-RND-26).
"""

from __future__ import annotations

import math

import numpy as np

import bell
from tb_common import kc

TRI_BUDGET = {"weep_column": (6000, 600)}
M_WATER = "tb_drop_proxy"
M_SPRAY = "tb_salt_glass"
STILL = kc.Weathering(moss=0.0, salt=0.0, wet=0.0, erosion=0.0)
INTO_DROP_M = 0.3  # the fall's top reaches into the drop, so no seam shows at the weep point
HEIGHT_M = bell.DROP_BOTTOM_Y - bell.POOL_WATER_Y + INTO_DROP_M
SHEATH_GROW = 1.12  # the looser outer skin over the core
SPRAY_SCALE = 3.2  # the crown and ripples, for a fall this wide


def _fall(mb: kc.MeshBuilder, height: float, rng, *, lod: bool, radii_m: tuple[float, float], sides: int,
          wander: float, fray: float) -> None:
    n = max(6, int(height / (2.0 if lod else 0.75)))
    t = np.linspace(0.0, 1.0, n)
    ph = rng.uniform(0.0, 2.0 * math.pi, 2)
    x = wander * np.sin(t * 9.0 + ph[0]) * (1.0 - t) ** 0.5
    z = wander * np.cos(t * 7.0 + ph[1]) * (1.0 - t) ** 0.5
    centers = np.stack([x, t * height, z], axis=-1)
    top, foot = radii_m
    radii = (foot + (top - foot) * t) * (1.0 + fray * (1.0 - t) ** 3) * (1.0 + 0.04 * np.sin(t * 40.0 + ph[0]))
    kc.tube(mb, centers, radii, sides, mb.material(M_WATER), cap_start=False, cap_end=True, weather=STILL)


def _spray(mb: kc.MeshBuilder, rng, *, lod: bool, scale: float) -> None:
    # A crown of droplet sheets thrown out where the fall hits the pool, and two low ripple rings.
    for k in range(5 if lod else 11):
        a = 2.0 * math.pi * k / (5 if lod else 11) + rng.uniform(-0.2, 0.2)
        reach = scale * rng.uniform(0.35, 0.6)
        tip = np.array([math.cos(a) * reach, scale * rng.uniform(0.18, 0.32), math.sin(a) * reach])
        pts = np.array([[0.0, 0.02, 0.0], tip * 0.5 + np.array([0.0, tip[1] * 0.4, 0.0]), tip])
        kc.tube(mb, pts, np.array([0.05, 0.035, 0.008]) * scale, 3 if lod else 5, mb.material(M_SPRAY),
                cap_end=True, weather=STILL)
    for r in ((0.45, 0.6) if not lod else (0.5,)):
        ring = [[math.cos(a) * r * scale, 0.015, math.sin(a) * r * scale] for a in np.linspace(0, 2 * math.pi, 25)]
        kc.tube(mb, np.array(ring), 0.012 * scale, 3, mb.material(M_SPRAY), weather=STILL)


def column(name: str, seed: int, height: float, *, lod: bool = False, spray: float = 1.0) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    mb = kc.MeshBuilder(name + ("-lod1" if lod else ""))
    core = bell.COLUMN_RADII
    _fall(mb, height, rng, lod=lod, radii_m=core, sides=8 if lod else 16, wander=0.05, fray=0.15)
    if not lod:
        sheath = (core[0] * SHEATH_GROW, core[1] * SHEATH_GROW)
        _fall(mb, height, rng, lod=lod, radii_m=sheath, sides=20, wander=0.1, fray=0.45)
    _spray(mb, rng, lod=lod, scale=spray)
    return mb


TARGETS = {
    "weep_column": lambda: [column("weep_column", 781, HEIGHT_M, spray=SPRAY_SCALE),
                            column("weep_column", 781, HEIGHT_M, lod=True, spray=SPRAY_SCALE)],
}
