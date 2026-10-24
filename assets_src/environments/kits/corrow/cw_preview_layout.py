"""Writes the Corrow seawall preview layout (M3-ENV-04): game/levels/_tests/corrow_kit/corrow_layout.json.

    python3 assets_src/environments/kits/corrow/cw_preview_layout.py

The layout is HalunaDresser's format (hymn-zone-layout/1, no terrain: every piece carries its own "y"),
plus "fire_lights" for CorrowPreview (the beacon). It composes the design notes' key shots (corrow.md §4):
36 seawall segments on the arc (R = 300 m about a centre out at sea, (0, 0, +R)), each with its rip-rap,
four Watchers' heads on the parapet and two sea-face reliefs; the Fisher Stair on the inner face with
Liss's hoist at its head; the low town's ground cells and houses round the lane at the stair foot; the far
ground; the Coilspire headland at the bay's east horn.

Placement on the arc: a piece built bent (cw_common.bend) or a small piece built straight goes at arc
length s with yaw -s / R (Godot's Basis(UP, yaw)), its local offsets (y, z) carried through
cw_common.bend_points. Heights come from the kit's own height functions with each piece's seed, so props
sit on the generated ground. m2-slice copies the pieces it wants (swap-in note in the task file).
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import cw_common as cw  # noqa: E402
import cw_far  # noqa: E402
import cw_stair  # noqa: E402
import cw_town  # noqa: E402
import cw_wall  # noqa: E402
from cw_common import kc  # noqa: E402

OUT = ROOT / "game" / "levels" / "_tests" / "corrow_kit" / "corrow_layout.json"
SEGMENTS = range(-12, 25)  # segment centres at s = 6 + 12 k: the wall runs s -138 .. +294 m into the headland
STAIR_S = -40.0  # the stair's foot (arc length)
HOIST_HEAD_S = -16.5  # the Watcher's head nearest the stair head
HEAD_Z = (cw.PARAPET[0] + cw.PARAPET[1]) * 0.5
HEAD_Y = cw.WALK_Y + cw.PARAPET[2]
RELIEF_ROWS = ((-3.0, 3.0), (3.0, 7.0))  # (offset from the segment centre, origin height on a course joint)
HEADLAND = (318.0, 178.0, -30.0)  # x, z, yaw (deg): its cliffs (+Z local) face the open sea, south-west
CELLS_X = (-84.0, -60.0, -36.0, -12.0, 12.0)
CELLS_Z = (-16.0, -40.0)

NOISE_FAR = kc.Noise3(kc.rng_for("corrow_far", 891))
NOISE_HEAD = kc.Noise3(kc.rng_for("coilspire_headland", 881))
NOISE_CELL = kc.Noise3(kc.rng_for("lowtown_ground", 861))


def arc_pose(s: float, y: float = 0.0, z: float = 0.0) -> tuple[float, float, float, float]:
    """World (x, y, z) of the wall-frame point (s, y, z) and the yaw (deg) of the wall's frame there."""
    p, _theta = cw.bend_points(np.array([s, y, z]))
    return float(p[0]), float(p[1]), float(p[2]), -math.degrees(s / cw.ARC_R_M)


def put_arc(piece: str, s: float, y: float = 0.0, z: float = 0.0, **kw) -> dict:
    x, yy, zz, yaw = arc_pose(s, y, z)
    d = {"piece": piece, "at": [round(x, 3), round(zz, 3)], "y": round(yy, 3), "yaw_deg": round(yaw, 3)}
    d.update(kw)
    return d


def far_y(x: float, z: float) -> float:
    rel = np.array([x, z - cw.ARC_R_M])
    rho = float(np.linalg.norm(rel))
    phi = math.atan2(rel[0], -rel[1])
    return float(cw_far.far_height(NOISE_FAR, np.array(rho), np.array(phi)))


def cell_y(x: float, z: float) -> float | None:
    for cx in CELLS_X:
        for cz in CELLS_Z:
            if abs(x - cx) <= cw_town.HALF and abs(z - cz) <= cw_town.HALF:
                return cw.TOWN_Y + float(cw_town.ground_height(NOISE_CELL, np.array([[x - cx]]), np.array([[z - cz]]))[0, 0])
    return None


def ground_y(x: float, z: float) -> float:
    c = cell_y(x, z)
    return c if c is not None else far_y(x, z)


def wall() -> list[dict]:
    out = []
    for k in SEGMENTS:
        s = 6.0 + 12.0 * k
        out.append(put_arc("seawall_curve", s))
        out.append(put_arc("wall_apron", s))
        for dh in (-4.5, -1.5, 1.5, 4.5):
            out.append(put_arc("watcher_head", s + dh, HEAD_Y, HEAD_Z))
        for ds, y0 in RELIEF_ROWS:
            out.append(put_arc("watcher_relief", s + ds, y0, float(cw_wall.sea_z(y0))))
    return out


def stair() -> list[dict]:
    return [put_arc("fisher_stair", STAIR_S), put_arc("liss_hoist", HOIST_HEAD_S, HEAD_Y, HEAD_Z)]


def town() -> list[dict]:
    """The low town: ground cells, and houses huddled under the wall: a row along the back lane that runs
    behind the wall (fronts to the wall, 6 m from its foot), the lane that runs north from the stair foot
    lined both sides, and a looser spread behind; each jittered in place and yaw, a and b mixed, none
    overlapping another, the stair or the wall."""
    out = []
    for i, cx in enumerate(CELLS_X):
        for j, cz in enumerate(CELLS_Z):
            out.append({"piece": "lowtown_ground", "at": [cx, cz], "y": cw.TOWN_Y, "yaw_deg": 90.0 * ((i * 3 + j) % 4)})
    rng = kc.rng_for("corrow_preview_town", 8)
    foot_x, _y, _fz, foot_yaw = arc_pose(STAIR_S, 0.0, -cw_stair.WIDTH_M - 4.0)
    lane_x = foot_x - 1.0
    cands = []  # (piece, x, z, yaw)
    # The back lane: houses at local z -13.5 along the wall, fronts (+Z) to the wall.
    s = -100.0
    while s < 40.0:
        if not (STAIR_S - 9.0 < s < STAIR_S + 28.0):
            x, _yy, z, yaw = arc_pose(s, 0.0, -13.5 - rng.uniform(0.0, 1.5))
            cands.append((x, z, yaw + rng.uniform(-6.0, 6.0)))
        s += rng.uniform(6.6, 8.4)
    # The stair-foot lane north, both sides.
    z = -11.0
    while z > -62.0:
        cands.append((lane_x - 6.3 + rng.uniform(-0.6, 0.6), z, 90.0 + rng.uniform(-7.0, 7.0)))
        cands.append((lane_x + 6.5 + rng.uniform(-0.6, 0.6), z - rng.uniform(1.0, 3.0), -90.0 + rng.uniform(-7.0, 7.0)))
        z -= rng.uniform(7.2, 9.0)
    # A looser spread behind the back-lane row.
    for _k in range(26):
        x = rng.uniform(-105.0, 35.0)
        zz = rng.uniform(-62.0, -24.0)
        cands.append((x, zz, 90.0 * rng.integers(0, 4) + rng.uniform(-8.0, 8.0)))
    kept = []
    for k, (x, z, yaw) in enumerate(cands):
        if any((x - kx) ** 2 + (z - kz) ** 2 < 7.6 ** 2 for kx, kz, _y, _p in kept):
            continue
        if abs(x - lane_x) < 3.6 and z > -66.0:
            continue  # keep the lane open
        piece = "lowtown_house_a" if (k + int(x)) % 2 == 0 else "lowtown_house_b"
        kept.append((x, z, yaw, piece))
    for x, z, yaw, piece in kept:
        y = min(ground_y(x + dx, z + dz) for dx in (-2.5, 0.0, 2.5) for dz in (-3.0, 0.0, 3.0))
        out.append({"piece": piece, "at": [round(x, 3), round(z, 3)], "y": round(y - 0.04, 3), "yaw_deg": round(yaw, 2)})
    del foot_yaw
    return out


def headland() -> tuple[list[dict], list[float]]:
    hx, hz, yaw = HEADLAND
    piece = {"piece": "coilspire_headland", "at": [hx, hz], "y": 0.0, "yaw_deg": yaw, "lod1_from_m": 2500.0}
    sx, sz = cw_far.SPIRE_AT
    sy = float(cw_far.headland_height(NOISE_HEAD, np.array(sx), np.array(sz)))
    a = math.radians(yaw)
    wx = hx + sx * math.cos(a) + sz * math.sin(a)
    wz = hz - sx * math.sin(a) + sz * math.cos(a)
    beacon = [round(wx, 3), round(sy + cw_far.SPIRE_H + 1.6, 3), round(wz, 3), 6.0, 60.0]
    return [piece], beacon


def main() -> int:
    head_pieces, beacon = headland()
    pieces = [{"piece": "corrow_far", "at": [0.0, 0.0], "y": 0.0, "yaw_deg": 0.0, "lod1_from_m": 5000.0}]
    pieces += head_pieces + wall() + stair() + town()
    layout = {
        "schema": "hymn-zone-layout/1",
        "zone": "ch08/corrow preview (M3-ENV-04): the kit composed for the design notes' key shots",
        "_about": "Generated by assets_src/environments/kits/corrow/cw_preview_layout.py; do not edit by hand. "
                  "Coordinates: x east, z south (north = -Z), y explicit per piece (no terrain). The seawall's walk "
                  "centre line is an arc of R = 300 m about (0, 0, +300) (concave to the sea); s = 0 is at the origin. "
                  "The stair's foot is at s = -40, Liss's hoist on the head at s = -16.5.",
        "seed": 8,
        "kit_dir": "res://assets/environments/kits/corrow/",
        "materials_dir": "res://assets/environments/kits/corrow/materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 3000.0,
        "lod_margin_m": 2.0,
        "fire_lights": [beacon],
        "fire_light_color": "#E0702E",
        "pieces": pieces,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(layout, indent=1) + "\n", encoding="utf-8")
    print(f"LAYOUT {OUT.relative_to(ROOT)}: {len(pieces)} pieces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
