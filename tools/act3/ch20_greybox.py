#!/usr/bin/env python3
"""M5-A3P-1011 greybox: Ch20's `ch20/undertow_layers` (act3_ch20.md U00-U08, R1, R2): inside the Undertow, a stair of
floors down the well. The Kite rests on the first floor (U00), then the six memory layers in vowbound.md's order
(Oruvel's market, a Pemakar terrace on lantern-night, a Corrow kitchen, the Tidecup gallery, a drowned Lowlight
gallery, a still Ansedra square) with the two rests between (R1 after the third, R2 after the sixth), and the Cage's
floor round the well (U07-U08).

Each floor is walled and each flight down is railed, so nothing falls into the dark. A veil of bound light closes the
top of each flight until the floor above is done (the layout's "variants"; the flow re-applies them). Writes
game/levels/ch20/undertow_layers/undertow_layers_layout.json.
Usage: python3 tools/act3/ch20_greybox.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "act2"))
from ch10_greybox import box, r3  # noqa: E402
from ch11_greybox import floor, walls  # noqa: E402
from ch15_16_greybox import write  # noqa: E402

COL_DARK = "#2a3440"
COL_VEIL = "#9fe8f0"
COL_KITE = "#7a5a3a"
COL_WELL = "#061018"
GLOW_HELD = "#7fdcff"
HX = 8.0  # a floor's half sizes
HZ = 6.0
GAP = 8.0  # the flight between two floors, along -z
DROP = 3.0  # each floor's fall below the last
RAMP_W = 3.0
WALL_H = 1.2
CAGE_HX = 11.0
CAGE_HZ = 11.0

# The floors top to bottom: (spawn and block id, colour, the flag that opens its flight down, its shots, its marks
# as (id, dx, dz, yaw) from the floor's centre).
FLOORS = [
    ("FirstFloor", "#3a4652", "ch20_started", ["U01", "U02", "U03"],
     [("first_floor", -2.0, -2.0, 180.0), ("engine_socket", 3.0, 1.0, 90.0), ("well_walls", 0.0, -4.0, 0.0)]),
    ("Oruvel", "#8a7458", "ch20_ilun_released", ["U04", "U05", "U06", "U07", "U08"],
     [("market_shapes", -4.0, -2.0, 0.0), ("ilun", 0.0, -3.0, 0.0), ("net_float", 2.0, -1.0, 0.0)]),
    ("Lanternfall", "#5a5070", "ch20_kahre_released", ["U09", "U10", "U11"],
     [("channel_boats", -5.0, 0.0, 90.0), ("kahre", 0.0, -3.0, 0.0), ("smiths_hammer", 2.0, -2.0, 0.0)]),
    ("Kitchen", "#6a5040", "ch20_virel_released", ["U12", "U13", "U14"],
     [("kitchen_shapes", -4.0, -2.0, 0.0), ("virel", 0.0, -3.0, 0.0), ("tuning_key", 2.0, -1.0, 0.0)]),
    ("RestOne", COL_DARK, "ch20_rest_one", ["U15"], []),
    ("Tidecup", "#4a6a5a", "ch20_hesk_released", ["U16", "U17", "U18"],
     [("gallery_faces", -5.0, -3.0, 90.0), ("hesk", 0.0, -3.0, 0.0), ("keth_bundle", 2.0, -1.0, 0.0)]),
    ("Lowlight", "#3a5a6a", "ch20_nhoa_released", ["U19", "U20", "U21", "U22"],
     [("gallery_silt", 0.0, -4.0, 0.0), ("nhoa", 0.0, -3.0, 0.0), ("pell", -2.0, 0.0, 0.0),
      ("ressa_name_shell", 1.0, -1.0, 0.0)]),
    ("Ansedra", "#a8945a", "ch20_ethren_released", ["U23", "U24", "U25", "U26"],
     [("still_square", 0.0, -2.0, 0.0), ("ethren", 0.0, -3.0, 0.0), ("copper_ring", 1.0, -1.0, 0.0),
      ("behind_ysolde", -1.0, 2.0, 0.0)]),
    ("RestTwo", COL_DARK, "ch20_rest_two", ["U27"], []),
]
CAGE_SHOTS = ["U28", "U29", "U30"]

# The layer beats: (beat, floor, the flag that opens it, its fight's party, reserve).
LAYERS = [
    ("ilun", "Oruvel", "ch20_started", ["ysolde", "rhen", "asha"], ["toma", "kerrid", "liss"]),
    ("kahre", "Lanternfall", "ch20_ilun_released", ["kerrid", "rhen", "asha"], ["toma", "ysolde", "liss"]),
    ("virel", "Kitchen", "ch20_kahre_released", ["toma", "rhen", "asha"], ["ysolde", "kerrid", "liss"]),
    ("hesk", "Tidecup", "ch20_rest_one", ["toma", "rhen", "asha"], ["ysolde", "kerrid", "liss"]),
    ("nhoa", "Lowlight", "ch20_hesk_released", ["ysolde", "rhen", "asha"], ["toma", "kerrid", "liss"]),
    ("ethren", "Ansedra", "ch20_nhoa_released", ["ysolde", "rhen", "asha"], ["toma", "kerrid", "liss"]),
]
RESTS = [("rest_one", "RestOne", "ch20_virel_released", "ch20_rest_one"),
         ("rest_two", "RestTwo", "ch20_ethren_released", "ch20_rest_two")]


def centre(n: int) -> tuple[float, float]:
    """Floor n's centre z and its height."""
    return -n * (2 * HZ + GAP), -n * DROP


def cage_centre() -> tuple[float, float]:
    z, y = centre(len(FLOORS))
    return z - (CAGE_HZ - HZ), y


def undertow_layers() -> dict:
    blocks: list[dict] = []
    ramps: list[dict] = []
    spawns: dict = {}
    marks: dict = {}
    shots: dict = {}
    variants: list[dict] = []
    gap = {"n": (-RAMP_W * 0.5, RAMP_W * 0.5), "s": (-RAMP_W * 0.5, RAMP_W * 0.5)}
    for n, (fid, col, opens, ids, fmarks) in enumerate(FLOORS):
        cz, y = centre(n)
        blocks.append(floor(fid, 0.0, cz, HX, HZ, y, col))
        blocks += walls(fid, 0.0, cz, HX, HZ, y, WALL_H, gap if n else {"n": gap["n"]})
        spawns[fid] = [0.0, y, r3(cz + HZ - 1.5), 180.0]
        for mid, dx, dz, yaw in fmarks:
            marks[mid] = [dx, y, r3(cz + dz), yaw]
        for k, sid in enumerate(ids):  # a shot each from the floor's near corners, alternating sides
            side = -1.0 if k % 2 else 1.0
            shots[sid] = {"pos": [r3(side * (HX - 1.5)), r3(y + 2.0 + 0.4 * k), r3(cz + HZ - 1.0)],
                          "look_at": [0.0, r3(y + 1.0), r3(cz - 2.0)], "fov": 45 if k % 2 else 55}
        # the flight down to the next floor (or the Cage's), railed both sides, veiled at its top
        top_z = cz - HZ
        low_z, low_y = (centre(n + 1)[0] + HZ, y - DROP) if n + 1 < len(FLOORS) else (cage_centre()[0] + CAGE_HZ,
                                                                                         y - DROP)
        ramps.append({"id": f"Flight{n + 1}", "from": [0.0, y, r3(top_z)], "to": [0.0, low_y, r3(low_z)],
                      "width": RAMP_W, "color": col})
        for side in (-1.0, 1.0):
            blocks.append(box(f"Rail{n + 1}{'WE'[side > 0]}", side * (RAMP_W * 0.5 + 0.15), (low_y + y + WALL_H) * 0.5,
                              (top_z + low_z) * 0.5, 0.3, y - low_y + WALL_H, top_z - low_z, color=COL_DARK))
        veil = f"Veil{n + 1}"
        blocks.append(box(veil, 0.0, y + 1.5, top_z - 0.3, RAMP_W, 3.0, 0.3, color=COL_VEIL, emission=GLOW_HELD,
                          emission_energy=0.8))
        variants.append({"when": {"set": [opens]}, "hide": [veil]})
    blocks.append(box("KiteHull", 4.0, 0.9, centre(0)[0] + 1.0, 3.0, 1.8, 7.0, color=COL_KITE))
    # the Cage's floor: four seats of bound light round the well (U07), Toma's line before them (cage_line)
    cz, y = cage_centre()
    blocks.append(floor("CageFloor", 0.0, cz, CAGE_HX, CAGE_HZ, y, COL_DARK))
    blocks += walls("CageFloor", 0.0, cz, CAGE_HX, CAGE_HZ, y, WALL_H, {"s": gap["s"]})
    blocks.append(box("Well", 0.0, y + 0.3, cz, 6.0, 0.6, 6.0, color=COL_WELL, emission=GLOW_HELD, emission_energy=0.4))
    for k, (dx, dz) in enumerate(((0.0, -5.0), (5.0, 0.0), (0.0, 5.0), (-5.0, 0.0))):
        blocks.append(box(f"CageSeat{k + 1}", dx, y + 1.5, cz + dz, 1.2, 3.0, 1.2, color=COL_VEIL, emission=GLOW_HELD,
                          emission_energy=0.6))
    spawns["CageFloor"] = [0.0, y, r3(cz + CAGE_HZ - 1.5), 180.0]
    marks.update({"cage_line": [0.0, y, r3(cz + 7.5), 180.0], "cage_seats": [0.0, y, r3(cz), 0.0],
                  "founders": [0.0, y, r3(cz - 5.0), 0.0]})
    for k, sid in enumerate(CAGE_SHOTS):
        side = -1.0 if k % 2 else 1.0
        shots[sid] = {"pos": [r3(side * 6.0), r3(y + 3.0 + k), r3(cz + CAGE_HZ - 1.0)], "look_at": [0.0, r3(y + 1.0), r3(cz)],
                      "fov": 50}
    triggers = []
    for beat, fid, req, _party, _reserve in LAYERS:
        fz = centre([f[0] for f in FLOORS].index(fid))[0]
        triggers.append({"id": beat, "activation": "touch", "at": [0.0, centre([f[0] for f in FLOORS].index(fid))[1],
                                                                    r3(fz)],
                         "size": [2 * HX - 2.0, 0, 4.0], "requires_flag": req,
                         "blocked_by_flag": f"ch20_{beat}_beaten", "payload": {"beat": beat}, "yaw": 0.0})
    for beat, fid, req, flag in RESTS:
        fz, fy = centre([f[0] for f in FLOORS].index(fid))
        triggers.append({"id": beat, "activation": "touch", "at": [0.0, fy, r3(fz)], "size": [2 * HX - 2.0, 0, 4.0],
                         "requires_flag": req, "blocked_by_flag": flag, "payload": {"beat": beat}, "yaw": 0.0})
    triggers.append({"id": "the_cage", "activation": "touch", "at": [0.0, y, r3(cz + 6.0)], "size": [8.0, 0, 3.0],
                     "requires_flag": "ch20_rest_two", "blocked_by_flag": "ch20_cage_broken",
                     "payload": {"beat": "the_cage"}, "yaw": 0.0})
    return {
        "doc": "M5-A3P-1011 greybox (tools/act3/ch20_greybox.py; do not edit by hand): inside the Undertow, a stair of "
        "floors down the well: the first floor with the Kite (U00), the six memory layers in vowbound.md's order "
        "(Oruvel, Lanternfall, Kitchen, Tidecup, Lowlight, Ansedra) with the rests after the third and the sixth "
        "(RestOne, RestTwo), and the Cage's floor round the well (U07-U08). Each flight down is veiled until the floor "
        "above is done.",
        "sun": {"pitch_deg": -80.0, "yaw_deg": 0.0, "energy": 0.3, "color": "#9fe8f0"},
        "environment": {"background": "#04101a", "ambient_color": "#2a5a70", "ambient_energy": 0.6},
        "block_color": COL_DARK,
        "blocks": blocks,
        "ramps": ramps,
        "spawns": spawns,
        "marks": marks,
        "actors": {},
        "shots": shots,
        "camera_volumes": [],
        "triggers": triggers,
        "variants": variants,
        # M5-A3P-1849: the layers' regulars (act3_roster.md Ch20): the drowned lanterns of the remembered rooms, and the
        # held shoal drifting under one; from the first floor down to the Cage
        "encounters": {"table": [{"encounter": "ch20_layer_lanterns", "weight": 1},
                                 {"encounter": "ch20_layer_shoal", "weight": 1}],
                       "min_m": 70, "max_m": 120, "when": {"set": ["ch20_started"], "unset": ["ch20_cage_broken"]},
                       "seed": 20},
    }


def main() -> None:
    write("ch20", "undertow_layers", undertow_layers())


if __name__ == "__main__":
    main()
