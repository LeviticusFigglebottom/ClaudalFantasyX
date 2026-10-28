"""A moving boat's wake (M3-ENV-1000; brine_shoals.md §2): the Order's skiffs and the vendor boats leave one, Sefir's
white barge never does (ADR 0017 (a); act1_npcs.md §1.10). Pure numpy; see bs_common.py.

  boat_wake   a 16 m Kelvin wake for a 4-6 m hull, origin at the stern on the waterline, trailing toward -X (the
              bow faces +X, as the kit's boats): two arms opening at the Kelvin half-angle (19.5 degrees), each a
              ribbon widening 0.3 -> 2.2 m, and the churned centre track 0.9 -> 2.6 m wide. 2 cm over the water so
              it never z-fights the surface. For env_boat_wake.gdshader: UV.x across a ribbon (0..1), UV.y along
              the wake (0 at the stern, 1 at its tail), UV2.x 0 on the arms and 1 on the centre track.
"""

from __future__ import annotations

import math

import numpy as np

import bs_common as bc
from bs_common import kc

TRI_BUDGET = {"boat_wake": (600, 80)}

WAKE_LENGTH_M = 16.0
KELVIN_HALF_ANGLE = math.radians(19.47)
WAKE_Y = 0.02
ARM_WIDTH = (0.3, 2.2)
TRACK_WIDTH = (0.9, 2.6)


def _ribbon(mb, spine: np.ndarray, widths: np.ndarray, mat: int, kind: float) -> None:
    """A flat ribbon along an XZ spine (rows), `widths` across it; UV.y runs 0..1 along it."""
    d = np.gradient(spine, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    side = np.stack([-d[:, 2], np.zeros(len(d)), d[:, 0]], axis=-1)
    cols = 3
    across = np.linspace(-0.5, 0.5, cols)
    grid = spine[:, None, :] + side[:, None, :] * (widths[:, None, None] * across[None, :, None])
    t = np.linspace(0.0, 1.0, len(spine))
    uv = np.stack(np.broadcast_arrays(np.linspace(0.0, 1.0, cols)[None, :], t[:, None]), axis=-1)
    kc.quad_strip(mb, grid, mat, uv=uv, col=(1.0, 1.0, 1.0, 1.0), uv2=(kind, 0.0), smooth=False)


def build_wake() -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        mb = kc.MeshBuilder("boat_wake" + (bc.LOD if lod else ""))
        rows = 6 if lod else 17
        t = np.linspace(0.0, 1.0, rows)
        mat = mb.material(bc.M_WAKE)
        for s in (-1.0, 1.0):
            a = KELVIN_HALF_ANGLE * s
            spine = np.stack([-WAKE_LENGTH_M * t * math.cos(a), np.full(rows, WAKE_Y),
                              WAKE_LENGTH_M * t * math.sin(a) + 0.6 * s * (1.0 - t) * (t > 0)], axis=-1)
            spine[0, 2] = 0.55 * s  # the arms leave the hull's quarters
            _ribbon(mb, spine, ARM_WIDTH[0] + (ARM_WIDTH[1] - ARM_WIDTH[0]) * t, mat, 0.0)
        track = np.stack([-WAKE_LENGTH_M * 0.8 * t, np.full(rows, WAKE_Y + 0.004), np.zeros(rows)], axis=-1)
        _ribbon(mb, track, TRACK_WIDTH[0] + (TRACK_WIDTH[1] - TRACK_WIDTH[0]) * t, mat, 1.0)
        out.append(mb)
    return out


TARGETS = {"boat_wake": build_wake}
