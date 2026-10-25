"""The Lanternfall terrace's floor: the ground of the `ash_terrace_lanternfall` battle arena (M3-ENV-06; the arena
contract is docs/kb/tech/battle_arenas.md). Pure numpy; see pemakar_common.py.

  arena_ash_tread   a cemetery tread of tier ARENA_TIER widened for the fight: ash soil laid flat (not the kit
                    tread's 2% drainage fall) from under the next tier's wall foot to a front edge beyond the
                    camera's lowest ray, ash heavy on it and a worn band along its front, with soil skirts at its
                    ends and front so an open edge never shows sky.

The arena places the town (pemakar.md §0) around the battle sandbox's slot layout: tier ARENA_TIER's tread is the
arena's y = 0, the wall of the tier above (ARENA_TIER + 1) stands behind the enemy line with its anchor line at
arena z = WALL_Z_M on the arena's axis, and the town's main stair (arc angle 0) climbs beside the fight at arena
x = STAIR_X_M. `town_to_arena` maps the town's coordinates (the kit preview layout's) into the arena's, so the
tiers above, the massif, Ashcrown, the plume and the far lights all keep their places.
"""

from __future__ import annotations

import math

import numpy as np

import pemakar_common as pc
from pemakar_common import kc

TRI_BUDGET = {"arena_ash_tread": (6000, 600)}

ARENA_TIER = 7  # a cemetery tier with two more above it (pemakar_layout.TIER_KINDS)
WALL_Z_M = -4.15  # arena z of the upper tier's anchor line (its coping's front) on the arena's axis
STAIR_X_M = 6.5  # arena x of the main stair (the town's x = 0)
TREAD_HALF_X_M = 16.0
FRONT_Z_M = 5.6  # past the BattleCamera's lowest ray on the floor (about z 3.9)
BACK_INSET_M = 0.4  # the tread runs this far in under the wall's foot
SKIRT_M = 1.2
CELL_M = 0.5


def upper_wall_radius() -> float:
    """Town radius of the upper tier's anchor line (its tread front)."""
    return pc.TOWN_R0_M - pc.TREAD_D_M * (ARENA_TIER + 1)


def origin_radius() -> float:
    """Town radius of the arena's origin (on the arena's axis)."""
    return upper_wall_radius() - WALL_Z_M


def axis_angle() -> float:
    """The town arc angle of the arena's axis: the stair (angle 0) lands at arena x = STAIR_X_M on the wall line."""
    return -math.asin(STAIR_X_M / upper_wall_radius())


def town_to_arena(p) -> np.ndarray:
    """A town point (x, y, z; origin at the town's foot at sea level) in arena coordinates."""
    p = np.asarray(p, float)
    a = axis_angle()
    dx, dz = p[..., 0] - pc.TOWN_CENTRE[0], p[..., 2] - pc.TOWN_CENTRE[1]
    c, s = math.cos(-a), math.sin(-a)
    x = c * dx + s * dz  # the rotation that turns the town angle `a` onto the arena's +Z axis
    z = -s * dx + c * dz
    return np.stack([x, p[..., 1] - float(pc.tier_tread_y(ARENA_TIER)), z - origin_radius()], axis=-1)


def back_z(x) -> np.ndarray:
    """Arena z of the tread's back edge (under the upper wall's battered foot) at arena x."""
    r = upper_wall_radius() + pc.WALL_H_M * math.tan(math.radians(pc.BATTER_DEG)) - BACK_INSET_M
    return np.sqrt(r * r - np.asarray(x, float) ** 2) - origin_radius()


def build_ash_tread(seed: int = 711) -> list[kc.MeshBuilder]:
    out = []
    for lod in (False, True):
        rng = kc.rng_for("arena_ash_tread", seed)
        noise = kc.Noise3(rng)
        mb = kc.MeshBuilder(pc.lod_name("arena_ash_tread", lod))
        cell = CELL_M * (6.0 if lod else 1.0)
        xs = np.linspace(-TREAD_HALF_X_M, TREAD_HALF_X_M, int(2 * TREAD_HALF_X_M / cell) + 1)
        nz = int((FRONT_Z_M - float(back_z(0.0))) / cell) + 1
        rows = []
        for f in np.linspace(0.0, 1.0, nz):  # back -> front, each row following the back edge's arc
            bz = back_z(xs)
            rows.append(np.stack([xs, np.zeros_like(xs), bz + (FRONT_Z_M - bz) * f], axis=-1))
        g = np.asarray(rows, float)
        if not lod:
            g[..., 1] += (noise.fbm(g / 0.9, 3) - 0.5) * 0.016  # trodden flat: a centimetre of relief
        z = g[..., 2]
        path = kc.smoothstep(4.2, 4.6, z) * kc.smoothstep(5.5, 5.1, z)  # the walked band (under the camera)
        breakup = noise.fbm(g / 0.7, 2)
        col = np.stack([0.15 * breakup * kc.smoothstep(-2.0, -3.6, z), np.zeros_like(z), np.zeros_like(z),
                        0.3 + 0.4 * path], axis=-1)
        uv2 = np.stack([np.clip(0.85 + 0.15 * breakup - 0.25 * kc.smoothstep(-2.8, -3.6, z), 0.4, 1.0),
                        np.full(z.shape, float(rng.random()))], axis=-1)
        kc.quad_strip(mb, g, mb.material(pc.M_SOIL), uv=np.stack([g[..., 0], g[..., 2]], axis=-1), col=col, uv2=uv2,
                      flip=True, smooth=not lod)
        # Skirts: the front edge and both ends drop SKIRT_M (the open edges never show sky).
        for edge, flip in ((g[-1], True), (g[:, 0], True), (g[:, -1], False)):
            grid = np.stack([edge, edge - np.array([0.0, SKIRT_M, 0.0])], axis=0)
            kc.quad_strip(mb, grid, mb.material(pc.M_SOIL), uv=np.stack([grid[..., 0] + grid[..., 2], grid[..., 1]],
                                                                       axis=-1),
                          col=(0.0, 0.0, 0.0, 0.5), uv2=(0.6, 0.5), flip=flip, smooth=False)
        pc.ash_pass(mb, 0, noise, 0.6, period_m=2.2, floor=0.45)  # even ash: the fighters read on a pale floor
        cols = np.asarray(mb.col, float)
        pos = np.asarray(mb.pos, float)
        walked = kc.smoothstep(4.2, 4.6, pos[:, 2]) * kc.smoothstep(5.5, 5.1, pos[:, 2])
        cols[:, 1] *= 1.0 - 0.5 * walked
        mb.col = cols.tolist()
        out.append(mb)
    return out


TARGETS = {"arena_ash_tread": build_ash_tread}
