"""Corrow's low town at the stair foot (corrow.md §2). Pure numpy; see cw_common.py.

  lowtown_ground    a 24 x 24 m cell of the fishers' quarter, origin at its centre on the ground (place it at
                    +1.0 m): packed earth with worn cobble patches and puddles in the hollows (VC.B); edges
                    exactly at y 0 so cells tile.
  lowtown_house_a/b fishers' houses: laterite rubble walls (2.6 m) on a plinth course, a door with a timber
                    lintel and a dark interior, shuttered windows, net pegs, and a red clay tile hip roof
                    (the Haluna kit's roof generator, read-only). Front is +Z; origin at the footprint's
                    centre on the ground. 5 x 6 m and 4 x 7 m.
"""

from __future__ import annotations

import math

import numpy as np

import cw_common as cw
import village  # noqa: E402  (the Haluna kit's roof generator, read-only)
from cw_common import bsc, kc

TRI_BUDGET = {"lowtown_ground": (4800, 320), "lowtown_house": (16000, 1400)}
BUDGET_KEY = {"lowtown_house_a": "lowtown_house", "lowtown_house_b": "lowtown_house"}

CELL_M = 24.0
HALF = CELL_M * 0.5
WALL_H = 2.6
WALL_T = 0.5
EAVE_M = 0.7


def _n2(noise: kc.Noise3, X, Z, scale: float, octaves: int = 3, off: float = 0.0):
    p = np.stack([X / scale + off, np.full_like(X, 0.37 + off * 0.1), Z / scale - off], axis=-1)
    return noise.fbm(p, octaves)


def ground_salt(noise: kc.Noise3, X, Z):
    """Drying salt in broad pale patches (8-20 m), so the floor isn't one dark plain from the wall; the base 0.1 at the
    cell edge, where the zone's rotated tiles meet (M3-ENV-1330)."""
    fade = bsc.edge_fade(X, Z, HALF, 4.0)
    patch = kc.smoothstep(0.45, 0.7, _n2(noise, X, Z, 11.0, 3, 29.0))
    return 0.1 + 0.45 * patch * fade


def ground_tracks(noise: kc.Noise3, X, Z):
    """The trodden tracks between the doors, darker (the AO channel) in long soft bands; 0.95 at the cell edge."""
    fade = bsc.edge_fade(X, Z, HALF, 4.0)
    band = kc.smoothstep(0.5, 0.75, _n2(noise, X * 0.45, Z, 9.0, 2, 41.0))
    return 0.95 - 0.32 * band * fade


def ground_height(noise: kc.Noise3, X, Z):
    """Trodden earth: gentle relief (+-3 cm) and shallow hollows that hold puddles; 0 at the cell edge."""
    fade = bsc.edge_fade(X, Z, HALF, 3.0)
    relief = (_n2(noise, X, Z, 6.0, 3) - 0.5) * 0.06 + (_n2(noise, X, Z, 1.8, 2, 3.0) - 0.5) * 0.015
    hollow = kc.smoothstep(0.62, 0.72, _n2(noise, X, Z, 5.0, 3, 17.0))
    return (relief - 0.04 * hollow) * fade


def build_ground(name: str = "lowtown_ground", seed: int = 861) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for(name, seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(name + (cw.LOD if lod else ""))
        n = 41 if not lod else 13
        xs = np.linspace(-HALF, HALF, n)
        i_earth = mb.material(cw.M_EARTH)
        bsc.heightfield(mb, xs, xs, lambda X, Z: ground_height(noise, X, Z), i_earth,
                        wet=lambda X, Z, Y: np.clip((-Y - 0.012) / 0.02, 0, 1) * 0.9 + 0.1,
                        salt=lambda X, Z, Y: ground_salt(noise, X, Z),
                        ao=lambda X, Z, Y: ground_tracks(noise, X, Z), erosion=0.4, variation=float(rng.random()))
        # No per-triangle cobble (M3-ENV-1330: its patches broke along the grid's triangles and stopped dead at the
        # rotated tiles' edges). The earth carries the town's wear in its vertex colour instead.
        out.append(mb)
    return out


# ---------------------------------------------------------------------------------------------
# Houses
# ---------------------------------------------------------------------------------------------
HOUSES = {"lowtown_house_a": (5.0, 6.0, 871), "lowtown_house_b": (4.0, 7.0, 872)}


def _wall(mb: kc.MeshBuilder, a, b, y0: float, y1: float, mat: int, rng, noise, *, t: float = WALL_T,
          lod: bool = False) -> None:
    """A rubble wall from a to b (x, z) between heights y0 and y1, its centre line on a-b."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    mid = (a + b) * 0.5
    ln = float(np.linalg.norm(b - a))
    if ln < 0.05:
        return
    yaw = math.atan2(-(b - a)[1], (b - a)[0])
    kc.rounded_block(mb, (mid[0], (y0 + y1) * 0.5, mid[1]), (ln * 0.5, (y1 - y0) * 0.5, t * 0.5), mat,
                     rot=kc.rot_y(yaw), radius=0.04 if not lod else 0.02, seg=1 if lod else 3,
                     noise=None if lod else noise, disp_m=0.035, disp_period_m=0.4, weather=cw.TOWN_W,
                     variation=float(rng.random()))


def house(name: str, w: float, d: float, seed: int, *, lod: bool) -> kc.MeshBuilder:
    rng = kc.rng_for(name, seed)
    noise = kc.Noise3(rng)
    mb = kc.MeshBuilder(name + (cw.LOD if lod else ""))
    i_st, i_t, i_dk, i_ir = (mb.material(cw.M_HOUSE), mb.material(cw.M_TIMBER), mb.material(cw.M_DARK),
                             mb.material(cw.M_IRON))
    hw, hd = w * 0.5, d * 0.5
    if lod:
        kc.rounded_block(mb, (0, WALL_H * 0.5, 0), (hw, WALL_H * 0.5, hd), i_st, seg=1, radius=0.05)
        kc.rounded_block(mb, (-0.6, 1.0, hd + 0.005), (0.5, 1.0, 0.01), i_dk, seg=1, radius=0.005)
        village.hip_roof(mb, w + 2 * EAVE_M, d + 2 * EAVE_M, WALL_H - 0.05, rng, noise, kind="tile", lod=True)
        return mb
    # Plinth course and walls; the front (+Z) wall is split round the door.
    kc.rounded_block(mb, (0, 0.15, 0), (hw + 0.08, 0.2, hd + 0.08), i_st, radius=0.05, seg=2, noise=noise,
                     disp_m=0.03, disp_period_m=0.5, weather=cw.TOWN_W)
    door_c = -hw * 0.35
    door_w, door_h = 1.0, 2.0
    corners = [(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)]
    _wall(mb, (-hw - WALL_T * 0.5, -hd), (hw + WALL_T * 0.5, -hd), 0.3, WALL_H, i_st, rng, noise)
    _wall(mb, (hw, -hd + WALL_T * 0.5), (hw, hd - WALL_T * 0.5), 0.3, WALL_H, i_st, rng, noise)
    _wall(mb, (-hw, -hd + WALL_T * 0.5), (-hw, hd - WALL_T * 0.5), 0.3, WALL_H, i_st, rng, noise)
    _wall(mb, (-hw - WALL_T * 0.5, hd), (door_c - door_w * 0.5, hd), 0.3, WALL_H, i_st, rng, noise)
    _wall(mb, (door_c + door_w * 0.5, hd), (hw + WALL_T * 0.5, hd), 0.3, WALL_H, i_st, rng, noise)
    _wall(mb, (door_c - door_w * 0.5, hd), (door_c + door_w * 0.5, hd), door_h + 0.12, WALL_H, i_st, rng, noise)
    del corners
    # The dark interior seen through the door, the threshold, the timber lintel and a half-open leaf.
    kc.rounded_block(mb, (door_c, 1.2, hd - 0.6), (door_w * 0.5 + 0.1, 1.0, 0.3), i_dk, seg=1, radius=0.01)
    kc.rounded_block(mb, (door_c, 0.33, hd + 0.05), (door_w * 0.5 + 0.06, 0.04, 0.2), i_st, seg=1, radius=0.02)
    kc.plank(mb, (door_c - door_w * 0.5 - 0.2, door_h + 0.06, hd + 0.18), (door_c + door_w * 0.5 + 0.2, door_h + 0.06,
             hd + 0.18), 0.16, 0.14, i_t, variation=float(rng.random()), noise=noise)
    hinge = np.array([door_c - door_w * 0.5 + 0.04, hd - 0.1])
    leaf = hinge + np.array([math.cos(-1.0), -math.sin(-1.0)]) * 0.0 + np.array([0.55, -0.62])
    kc.rounded_block(mb, ((hinge[0] + leaf[0]) * 0.5, 1.05, (hinge[1] + leaf[1]) * 0.5), (0.43, 0.95, 0.03), i_t,
                     rot=kc.rot_y(math.atan2(-(leaf - hinge)[1], (leaf - hinge)[0])), seg=1, radius=0.01,
                     variation=float(rng.random()))
    # Windows: a dark opening with a sill and lintel, one shutter shut, one propped.
    wins = [((hw * 0.45, hd), 1), ((0.0, -hd), -1), ((hw, 0.2 * d), 1)]
    for k, ((cx, cz), out) in enumerate(wins):
        on_side = abs(abs(cx) - hw) < 1e-6
        nrm = np.array([out, 0.0, 0.0]) if on_side else np.array([0.0, 0.0, out])
        along = np.array([0.0, 0.0, 1.0]) if on_side else np.array([1.0, 0.0, 0.0])
        c = np.array([cx, 1.55, cz]) + nrm * (WALL_T * 0.5 + 0.005)
        yaw = 0.0 if not on_side else math.pi * 0.5
        kc.rounded_block(mb, c, (0.38, 0.42, 0.012), i_dk, rot=kc.rot_y(yaw), seg=1, radius=0.004)
        for dy, th in ((-0.48, 0.07), (0.48, 0.09)):
            kc.plank(mb, c - along * 0.55 + [0, dy, 0] + nrm * 0.04, c + along * 0.55 + [0, dy, 0] + nrm * 0.04, 0.16, th,
                     i_t, variation=float(rng.random()), noise=noise)
        if k % 2 == 0:
            kc.rounded_block(mb, c + nrm * 0.03, (0.36, 0.4, 0.025), i_t, rot=kc.rot_y(yaw), seg=1, radius=0.006,
                             variation=float(rng.random()))
        else:
            sh = c + nrm * 0.25 + np.array([0.0, 0.25, 0.0])
            kc.rounded_block(mb, sh, (0.36, 0.3, 0.025), i_t, rot=kc.rot_y(yaw) @ kc.rot_x(-0.7 * (1 if not on_side else 0)),
                             seg=1, radius=0.006, variation=float(rng.random()))
    # Net pegs along the front, iron.
    for k in range(4):
        x = hw * 0.15 + k * 0.4
        if x > hw - 0.3:
            break
        base = np.array([x, 2.2, hd + WALL_T * 0.5])
        kc.tube(mb, np.array([base, base + [0.0, 0.03, 0.18]]), 0.018, 5, i_ir, cap_end=True)
    village.hip_roof(mb, w + 2 * EAVE_M, d + 2 * EAVE_M, WALL_H - 0.05, rng, noise, kind="tile")
    return mb


def build_house(name: str) -> list[kc.MeshBuilder]:
    w, d, seed = HOUSES[name]
    return [house(name, w, d, seed, lod=False), house(name, w, d, seed, lod=True)]


TARGETS = {
    "lowtown_ground": build_ground,
    "lowtown_house_a": lambda: build_house("lowtown_house_a"),
    "lowtown_house_b": lambda: build_house("lowtown_house_b"),
}
