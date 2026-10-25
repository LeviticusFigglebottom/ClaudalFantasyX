"""Writes the Oruvel Underway preview layout (M3-ENV-05): game/levels/_tests/oruvel_underway_kit/oruvel_underway_layout.json.

    python3 assets_src/environments/kits/oruvel_underway/ou_preview_layout.py

The layout is HalunaDresser's format (hymn-zone-layout/1, no terrain: every piece carries its own "y"), plus
"shots" for OruvelUnderwayPreview (per camera: where Rhen's lantern hangs and which lighting area the frame is in,
oruvel_underway.md §0). It composes the design notes' key shots (§4):

* the terrace: 11 x 11 cells of 12 m round the tower (the cells under it left out, so the ground stops at its walls),
  the south row the broken lip over the canyon, the apron beyond;
* the tower, 36 x 12 m (6 x 2 bays), F8 (buried) to the broken crown on F14; the lamp gallery on F9-F10 with its east
  wall fallen onto the terrace (the breach) and a sand tongue spilling in; the west bay holds the gauge room (door on
  the gallery) and the stairwell going down, the divers' cord across its lip; the current shaft in the gauge room's
  corner; collapsed floors above the gallery; the bell-room on F13;
* the terrace dressing: the dead ship, coral heads, seagrass, Lit Age fragments and a fallen column by the breach;
* Oruvel's hulls overhead and the tether into the crown; a kit row on the terrace's north side for review (U14).

m2-slice copies the pieces it wants (the swap-in note in docs/kb/tasks/M3/M3-ENV-05-lamp-diver-seafloor.md).
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
import ou_ground as og  # noqa: E402
from ou_common import kc  # noqa: E402

OUT = ROOT / "game" / "levels" / "_tests" / "oruvel_underway_kit" / "oruvel_underway_layout.json"
TERRACE_Y = -22.6  # the silt's datum (oruvel_underway.md §0)
STOREY = 3.2
F1_Y = -48.0
TOWER_X = (-18.0, 18.0)
TOWER_Z = (-6.0, 6.0)
CELLS = [12.0 * k for k in range(-5, 6)]
CROWN_GONE = {(3.0, 6.0), (9.0, -6.0), (-15.0, -6.0)}  # the crown's walls that have fallen entirely


def floor_y(n: int) -> float:
    """Lit Age floors from the street up: F1 at -48 m, 3.2 m a storey (F9 = -22.4, F14 = -6.4)."""
    return round(F1_Y + (n - 1) * STOREY, 3)


F9 = floor_y(9)


def put(piece: str, x: float, y: float, z: float, yaw: float = 0.0, **kw) -> dict:
    d = {"piece": piece, "at": [round(x, 3), round(z, 3)], "y": round(y, 3), "yaw_deg": round(yaw, 2)}
    d.update(kw)
    return d


def ground_y(x: float, z: float) -> float:
    """The silt height at world (x, z) from the cell under it (for seating props on the terrace)."""
    cx = min(CELLS, key=lambda c: abs(c - x))
    cz = min(CELLS, key=lambda c: abs(c - z))
    piece, yaw = CELL_AT.get((cx, cz), (None, 0.0))
    if piece is None:
        return TERRACE_Y
    a = math.radians(yaw)
    dx, dz = x - cx, z - cz
    lx, lz = dx * math.cos(a) - dz * math.sin(a), dx * math.sin(a) + dz * math.cos(a)
    if piece == "seafloor_edge":
        h = og.edge_height(NOISE[piece], np.array(lx), np.array(lz))
    else:
        h = og.seafloor_height(NOISE[piece], np.array(lx), np.array(lz))
    return TERRACE_Y + float(h)


NOISE = {
    "seafloor_patch_a": kc.Noise3(kc.rng_for("seafloor_patch_a", 501)),
    "seafloor_patch_b": kc.Noise3(kc.rng_for("seafloor_patch_b", 502)),
    "seafloor_edge": kc.Noise3(kc.rng_for("seafloor_edge", 503)),
}
CELL_AT: dict[tuple[float, float], tuple[str, float]] = {}


def terrace() -> list[dict]:
    out = [put("seafloor_far", 0.0, TERRACE_Y, 0.0)]
    for i, x in enumerate(CELLS):
        for j, z in enumerate(CELLS):
            if TOWER_X[0] < x < TOWER_X[1] and TOWER_Z[0] < z < TOWER_Z[1]:
                continue  # under the tower: its own floors
            if z == CELLS[-1]:
                piece, yaw = "seafloor_edge", 0.0
            else:
                piece = "seafloor_patch_a" if (i + j) % 2 == 0 else "seafloor_patch_b"
                yaw = 90.0 * ((i * 3 + j * 5) % 4)
            CELL_AT[(x, z)] = (piece, yaw)
            out.append(put(piece, x, TERRACE_Y, z, yaw))
    return out


def tower() -> list[dict]:
    out = []
    rng = np.random.default_rng(np.random.SeedSequence([505, 9]))
    xs_bays = [-15.0, -9.0, -3.0, 3.0, 9.0, 15.0]
    zs_bays = [-3.0, 3.0]
    for n in range(8, 15):
        y = floor_y(n)
        for x in xs_bays:
            for z, yaw in ((TOWER_Z[1], 0.0), (TOWER_Z[0], 180.0)):
                if n == 14:
                    if (x, z) in CROWN_GONE:
                        continue
                    piece = "tower_bay_broken"
                else:
                    piece = "tower_bay_solid" if (n == 8 or (int(x) // 6 + n) % 3 == 0) else "tower_bay"
                out.append(put(piece, x, y, z, yaw))
        for z in zs_bays:
            for x, yaw in ((TOWER_X[1], 90.0), (TOWER_X[0], 270.0)):
                if n in (9, 10) and x > 0 and z > 0:
                    continue  # the breach: the east wall's south bay fell outward onto the terrace
                piece = "tower_bay_broken" if n == 14 else ("tower_bay_solid" if n == 8 else "tower_bay")
                out.append(put(piece, x, y, z, yaw))
        for x in TOWER_X:
            for z in TOWER_Z:
                if n in (9, 10) and x > 0 and z > 0:
                    continue
                if n == 14 and rng.random() < 0.5:
                    continue
                out.append(put("tower_pier", x, y, z))
    # Floors. F9 the gallery (and the gauge room); F10 only over the west bay (the gallery is double height);
    # F11-F13 whole but for the collapsed stack at (3, 3); F14 the crown floor, broken open.
    for n in range(9, 15):
        y = floor_y(n)
        for x in [-15.0, -9.0, -3.0, 3.0, 9.0, 15.0]:
            for z in (-3.0, 3.0):
                if n == 9 and x == -15.0 and z > 0:
                    continue  # the stairwell
                if n == 10 and x > -12.0:
                    continue
                if n in (11, 12, 13) and (x, z) == (3.0, 3.0):
                    out.append(put("floor_slab_broken", x, y, z, 0.0 if n % 2 else 180.0))
                    continue
                if n == 14 and (x, z) in ((3.0, 3.0), (9.0, -3.0)):
                    continue
                if n == 14 and (x, z) == (-3.0, 3.0):
                    out.append(put("floor_slab_broken", x, y, z, 90.0))
                    continue
                out.append(put("floor_slab", x, y, z))
    # The west bay: the gauge room's door on the gallery, the stairwell mouth open, walls over both on F10.
    out.append(put("hinge_door", -12.0, F9, -3.0, 90.0))
    out.append(put("tower_bay_solid", -12.0, floor_y(10), -3.0, 90.0))
    out.append(put("tower_bay_solid", -12.0, floor_y(10), 3.0, 90.0))
    out.append(put("tower_bay_solid", -15.0, F9, 0.0, 180.0))
    out.append(put("stair_flight", -12.15, F9, 3.0, 180.0))
    out.append(put("stair_flight", -18.15, floor_y(8), 3.0, 180.0))
    out.append(put("divers_cord", -12.3, F9, 3.0))
    # The stairwell's walls going down into the podium (F8, F7), dark.
    for n in (7, 8):
        out.append(put("tower_bay_solid", -12.0, floor_y(n), 3.0, 270.0))
        out.append(put("tower_bay_solid", -15.0, floor_y(n), 0.0, 0.0))
    # The gauge room: the wheel, the pipe run on the west wall, the current shaft in its south-west corner.
    out.append(put("gauge_wheel", -15.4, F9, -3.9))
    out.append(put("pipe_run", -17.8, F9, -3.0, 90.0))
    for n in range(9, 15):
        out.append(put("current_shaft", -16.35, floor_y(n), -1.5, 11.0))
    # The gallery: two rows of dead lamp-columns (one fallen), coral curtains across two side bays.
    for x in (-9.0, -3.0, 3.0, 9.0, 15.0):
        for z in (-3.0, 3.0):
            if (x, z) == (3.0, -3.0):
                out.append(put("lamp_column_fallen", x, F9, z, 205.0))
                continue
            out.append(put("lamp_column", x, F9, z, float(rng.uniform(0, 360))))
    # Growth and fallen pieces on the gallery floor.
    out.append(put("coral_head_b", 12.6, F9, -4.4, 40.0, scale=0.8))
    out.append(put("coral_head_b", -6.3, F9, 4.6, 200.0, scale=0.7))
    out.append(put("lit_fragments", 6.0, F9, 1.0, 30.0))
    out.append(put("lit_fragments", -7.5, F9, -1.2, 200.0))
    out.append(put("coral_curtain", -3.0, F9, -5.55))
    out.append(put("coral_curtain", 9.0, F9, 5.55, 180.0))
    out.append(put("pipe_run", 6.0, F9, -5.8, 0.0))
    # The breach: sand spilling in, the fallen wall and its rubble outside.
    out.append(put("sand_drift", 21.0, ground_y(21.0, 3.0) - 0.05, 3.0, 180.0))
    out.append(put("tower_bay_broken", 21.6, ground_y(21.6, 2.6) + 0.12, 2.6, 90.0, tilt_deg=[-84.0, 0.0]))
    out.append(put("tower_bay_broken", 24.2, ground_y(24.2, 6.8) + 0.15, 6.8, 120.0, tilt_deg=[-80.0, 6.0]))
    out.append(put("lit_fragments", 24.5, ground_y(24.5, -0.5), -0.5, 40.0))
    out.append(put("lamp_column_fallen", 22.0, ground_y(22.0, 9.5), 9.5, 150.0))
    # The bell-room on F13, at the west end.
    out.append(put("bell_room", -15.0, floor_y(13), -3.0))
    return out


def dressing() -> list[dict]:
    out = []
    rng = np.random.default_rng(np.random.SeedSequence([505, 11]))
    out.append(put("wreck_ribs", 30.0, ground_y(30.0, 18.0), 18.0, -24.4))
    heads = [("coral_head_a", 35.0, 7.0), ("coral_head_b", 25.5, 10.0), ("coral_head_a", 46.0, 24.0),
             ("coral_head_b", 39.0, -8.0), ("coral_head_a", 27.0, -14.0), ("coral_head_b", 51.0, 5.0),
             ("coral_head_b", 22.5, -6.5), ("coral_head_a", -26.0, 14.0), ("coral_head_b", -30.0, -12.0),
             ("coral_head_a", 8.0, 20.0), ("coral_head_b", -6.0, -18.0)]
    for piece, x, z in heads:
        out.append(put(piece, x, ground_y(x, z) - 0.08, z, float(rng.uniform(0, 360))))
    # The meadow: seagrass patches over the open east of the terrace, clear of the ship and the heads.
    placed = 0
    tries = 0
    for x, z in ((37.5, 13.5), (34.5, 11.0), (38.5, 7.5), (32.0, 14.5), (36.0, 16.5), (40.5, 9.5)):
        out.append(put("seagrass_patch", x, ground_y(x, z), z, float(rng.uniform(0, 360)), scale=1.3))
    while placed < 60 and tries < 800:
        tries += 1
        x, z = float(rng.uniform(24.0, 62.0)), float(rng.uniform(-14.0, 34.0))
        if math.hypot((x - 30.0) * 0.6, z - 18.0) < 5.0:
            continue
        if any(math.hypot(x - hx, z - hz) < 2.6 for _p, hx, hz in heads):
            continue
        out.append(put("seagrass_patch", x, ground_y(x, z), z, float(rng.uniform(0, 360)),
                       scale=round(float(rng.uniform(0.9, 1.6)), 2)))
        placed += 1
    for x, z in ((14.0, 22.0), (-22.0, 20.0), (6.0, -24.0), (34.0, -20.0)):
        out.append(put("lit_fragments", x, ground_y(x, z), z, float(rng.uniform(0, 360))))
    # Oruvel overhead, and the tether into the crown.
    out.append(put("hull_keels", -3.0, 0.0, 11.0, 70.0))
    out.append(put("tether_line", -9.9, floor_y(14) + 0.55, 5.2))
    return out


def kit_row() -> list[dict]:
    """U14: the props and growth pieces in two rows on the terrace's north side."""
    names = [["lamp_column", "lamp_column_fallen", "gauge_wheel", "gauge_wheel_cut", "hinge_door"],
             ["coral_head_a", "coral_head_b", "seagrass_patch", "coral_curtain", "lit_fragments"]]
    out = []
    for row, z in enumerate((-40.0, -47.0)):
        for k, name in enumerate(names[row]):
            x = -12.0 + 6.0 * k + 3.0 * row  # the back row sits in the front row's gaps
            out.append(put(name, x, ground_y(x, z), z, 0.0))
    out.append(put("divers_cord", 16.5, ground_y(16.5, -40.0), -40.0, 90.0))
    out.append(put("diver_lantern", 16.5, ground_y(16.5, -43.0) + 0.25, -43.0))
    return out


def shots() -> dict:
    """Per preview camera: Rhen's lantern (the rig's lantern_target) and the lighting area (§0: open, interior,
    deep). Call after terrace(), which seats the ground."""
    return {
        "U01": {"lantern": [-9.9, -5.4, 5.3], "area": "open", "depth_m": 5.5},
        "U04": {"lantern": [11.2, -21.2, 1.4], "area": "interior", "depth_m": 21.0},
        "U06": {"lantern": [-11.9, -20.95, 3.85], "area": "deep", "depth_m": 22.0},
        "U07": {"lantern": [-13.77, -21.2, -2.73], "area": "deep", "depth_m": 21.5},
        "U12": {"lantern": [36.6, -21.75, 9.6], "area": "open", "depth_m": 21.0},
        "U13": {"lantern": [34.3, -21.95, 23.3], "area": "open", "depth_m": 21.0},
        "U14": {"lantern": [16.5, round(ground_y(16.5, -43.0) + 1.4, 3), -42.0], "area": "open", "depth_m": 21.0},
    }


def main() -> int:
    pieces = terrace() + tower() + dressing() + kit_row()
    cams = shots()
    layout = {
        "schema": "hymn-zone-layout/1",
        "zone": "ch01/oruvel_underway preview (M3-ENV-05): the kit composed for the design notes' key shots",
        "_about": "Generated by assets_src/environments/kits/oruvel_underway/ou_preview_layout.py; do not edit by hand. "
                  "Coordinates: x east, z south (north = -Z), y explicit per piece (the sea surface at y 0). The tower "
                  "stands on x -18..18, z -6..6; the terrace's silt datum is y -22.6; floors F9 (the gallery) -22.4 to "
                  "F14 (the crown) -6.4.",
        "seed": 5,
        "kit_dir": "res://assets/environments/kits/oruvel_underway/",
        "materials_dir": "res://assets/environments/kits/oruvel_underway/materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 3000.0,
        "lod_margin_m": 2.0,
        "shots": cams,
        "pieces": pieces,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(layout, indent=1) + "\n", encoding="utf-8")
    print(f"LAYOUT {OUT.relative_to(ROOT)}: {len(pieces)} pieces, {len(cams)} shots")
    return 0


if __name__ == "__main__":
    sys.exit(main())
