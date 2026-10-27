"""Corrow's frame (ADR 0200, M3-C08-1202): env-art's seawall kit (M3-ENV-04/04B) in its own preview frame, and the map
from the old flat greybox (M3-C08-02) into it.

The kit's frame: the walk's centre line is an arc of R = 300 m about (0, 0, +300) (the sea is +Z, south), arc length
s along it (east +), wall-frame z across it (the sea +, inland -); the walk is at y 12.0, the low town at y 1.0, the
sea at y 0.5 (the preview's tide). The Fisher Stair climbs the wall's inner face eastward from its foot at s = -40
(y 1.0) to its head landing at s -18.1 .. -14.5 (y 12.53). Ch8's zone uses this frame as its own.

The greybox was flat: the wall-head walk at z 26..36 (y 0), the parapet and the Watchers at z 38.5, the Fisher Stair
a 34 m slab running north from the walk (z 22 .. -12), the low town north of it, the Bastion west, the mole and the
sea south. `to_kit` places any greybox point in the kit's frame by region (walk, stair, town, Bastion, sea); the
relayout script applies it once, and the zone's layout is then hand-tuned in the kit's frame.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT_SRC = ROOT / "assets_src" / "environments" / "kits" / "corrow"
if str(KIT_SRC) not in sys.path:
    sys.path.insert(0, str(KIT_SRC))

import cw_common as cw  # noqa: E402
import cw_preview_layout as cwl  # noqa: E402
import cw_stair  # noqa: E402
import cw_wall  # noqa: E402

WALK_Y = cw.WALK_Y  # 12.0
TOWN_Y = cw.TOWN_Y  # 1.0
SEA_Y = 0.5  # the preview's tide (CorrowPreview water_height_m)
HEAD_Y = cw.WALK_Y + cw.PARAPET[2]  # 12.9: the parapet's top, where the Watchers' heads stand
HEAD_Z = (cw.PARAPET[0] + cw.PARAPET[1]) * 0.5
STAIR_S = cwl.STAIR_S  # -40: the stair's foot
_steps, LANDING, HEAD_LANDING = cw_stair.layout_steps()  # stair-local x (along the wall from its foot)
STAIR_TOP_Y = cw_stair.HEAD_Y  # 12.53
HOIST_S = cwl.HOIST_HEAD_S  # -16.5

# The greybox -> kit map.
S_SHIFT = -15.0  # greybox x 0 (the stair head) -> s -15 (the kit's head landing, s -18.1 .. -14.5)
GB_WALK_Z = 31.0  # the greybox walk's centre line
GB_STAIR_HEAD_Z = 22.0
GB_STAIR_FOOT_Z = -12.0
GB_STAIR_HALF_W = 4.5
GB_PARAPET_Z = 37.0
BASTION_S_SHIFT = -35.0  # the Bastion (greybox x -65 .. -25) -> s -100 .. -60, on its platform at walk height
BASTION_X = -25.0
MOLE_S = 15.0  # the mole meets the wall at s 15 (greybox x 30)
PIER_Y = 1.2
PIER_Z = (26.0, 52.0)  # wall-frame z of the pier's landward and seaward ends
RAMP_TOP_Z = cw.PARAPET[1]  # the mole's ramp reaches the parapet's sea edge at its top (y 12.9)


def arc(s: float, y: float = 0.0, z: float = 0.0) -> tuple[float, float, float, float]:
    """World (x, y, z) of the wall-frame point and the wall frame's yaw there (deg)."""
    return cwl.arc_pose(s, y, z)


def inner_z(y: float) -> float:
    """The wall's inner face (wall-frame z) at height y."""
    return float(cw_wall.inner_z(y))


def stair_y(u: float) -> float:
    """The stair's tread height at stair-local x u (0 at the foot): two flights, a landing, the head landing."""
    if u <= 0.0:
        return TOWN_Y
    if u < LANDING[0]:
        return TOWN_Y + (cw_stair.LANDING_Y - TOWN_Y) * u / LANDING[0]
    if u < LANDING[1]:
        return cw_stair.LANDING_Y
    if u < HEAD_LANDING[0]:
        return cw_stair.LANDING_Y + (STAIR_TOP_Y - cw_stair.LANDING_Y) * (u - LANDING[1]) / (HEAD_LANDING[0] - LANDING[1])
    return STAIR_TOP_Y


def stair_z(y: float) -> float:
    """The middle of the stair's treads (wall-frame z) at height y: 1.45 m in from the inner face."""
    return inner_z(y) - 1.45


def region(x: float, z: float) -> str:
    if z > GB_PARAPET_Z + 1.5:
        return "sea"
    if x < BASTION_X and z < GB_WALK_Z - 5.0:
        return "bastion"
    if z >= GB_STAIR_HEAD_Z + 2.0:
        return "walk"
    if z >= GB_STAIR_FOOT_Z and abs(x) <= GB_STAIR_HALF_W:
        return "stair"
    return "town"


def mole_y(zl: float) -> float:
    """The pier's top, then the ramp up the sea face to the parapet's top."""
    if zl >= PIER_Z[0]:
        return PIER_Y
    if zl <= RAMP_TOP_Z:
        return HEAD_Y
    return PIER_Y + (HEAD_Y - PIER_Y) * (PIER_Z[0] - zl) / (PIER_Z[0] - RAMP_TOP_Z)


def to_kit(x: float, y: float, z: float, yaw: float = 0.0) -> tuple[float, float, float, float]:
    """A greybox point and facing (deg) in the kit's frame. `y` is the greybox height above its floor."""
    r = region(x, z)
    if r == "town":
        fx, _fy, fz, _a = arc(STAIR_S, TOWN_Y, stair_z(TOWN_Y))  # the stair's foot
        return fx + x, TOWN_Y + y, fz + (z - GB_STAIR_FOOT_Z) - 1.5, yaw
    if r == "stair":
        u = HEAD_LANDING[0] * (z - GB_STAIR_FOOT_Z) / (GB_STAIR_HEAD_Z - GB_STAIR_FOOT_Z) if z < GB_STAIR_HEAD_Z \
            else HEAD_LANDING[0] + (HEAD_LANDING[1] - HEAD_LANDING[0]) * min(1.0, (z - GB_STAIR_HEAD_Z) / 2.0)
        ys = stair_y(u)
        wx, wy, wz, a = arc(STAIR_S + u, ys + y, stair_z(ys) - 0.4 * x)
        return wx, wy, wz, yaw + 90.0 + a  # greybox "down the stair" (yaw 0, north) is west along the wall
    if r == "bastion":
        wx, wy, wz, a = arc(x + BASTION_S_SHIFT, WALK_Y + y, -3.8 - (GB_WALK_Z - 5.0 - z) * 0.8)
        return wx, wy, wz, yaw + a
    if r == "sea":
        zl = cw_wall.sea_z(SEA_Y).item() + 1.0 + (z - (GB_PARAPET_Z + 3.0)) * 0.95
        on_mole = abs(x - (MOLE_S - S_SHIFT)) <= 3.0
        h = mole_y(zl) if on_mole else (SEA_Y if zl > 14.0 else TOWN_Y)
        wx, wy, wz, a = arc(x + S_SHIFT, h + y, zl)
        return wx, wy, wz, yaw + a
    zl = max(-2.2, min(2.7, (z - GB_WALK_Z) * 0.5))
    wx, wy, wz, a = arc(x + S_SHIFT, WALK_Y + y, zl)
    return wx, wy, wz, yaw + a


def r3(v: float) -> float:
    return round(float(v), 3)


def yaw_norm(a: float) -> float:
    a = math.fmod(a, 360.0)
    return round(a + 360.0 if a <= -180.0 else (a - 360.0 if a > 180.0 else a), 2)
