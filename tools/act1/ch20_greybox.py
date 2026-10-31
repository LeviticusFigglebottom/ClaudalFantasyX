#!/usr/bin/env python3
"""Ch20 "The Undertow" greybox (M5-A3P-1011; act3_ch20.md §2 U00-U08): ch20/undertow_layers, the story layer over
env-art's Undertow kit (assets_src/environments/kits/haluna/undertow_layers.py: memory_island and the six memory rooms).

The well's top (WellTop: the Kite in the eye, U00), then six layers going down and away, each a memory_island with its
room standing on it (U01 the Oruvel market, U02 the Pemakar terrace, U03 the Corrow kitchen, U04 the Reefball stands,
U05 the drowned gallery, U06 the still gold square), a landing after the third and after the sixth (R1, R2), and the
founders' floor (the Cage, U07-U08) at the bottom of the well. Each layer has its own spawn (Layer1..Layer6, Rest1,
Rest2, Cage); the flow places the party from one to the next after each release, so the descent is cut, not walked.
Collision only under the kit's pieces; the Cage's floor is a greybox round. This writes the layout and the zone scene.

x is east, north is -Z.

    python3 tools/act1/ch20_greybox.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ch10_greybox import box  # noqa: E402
from ch11_greybox import floor  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
ZONE = ROOT / "game" / "levels" / "ch20" / "undertow_layers"
KIT = "res://assets/environments/kits/haluna/"
DROP, STEP = 12.0, 36.0  # each layer is this much lower and further north than the last
LAYERS = [("ilun", "memory_market"), ("kahre", "memory_terrace"), ("virel", "memory_kitchen"),
          ("hesk", "memory_stands"), ("nhoa", "memory_gallery"), ("ethren", "memory_square")]
# Each layer's anchors (vfx and look_at targets the scenes name), as offsets from the island's centre
ANCHORS = {"ilun": {"market_shapes": (0, 1.0, -2), "kell_stall": (-3, 1.0, -1), "ilun": (0, 1.5, -3.5),
                    "net_float": (0.5, 1.0, -3)},
           "kahre": {"channel_boats": (0, 0.5, -2.5), "kahre": (0, 1.5, -3.5), "smiths_hammer": (0.5, 1.0, -3)},
           "virel": {"kitchen_shapes": (0, 1.0, -2), "virel": (0, 1.5, -3.5), "tuning_key": (0.5, 1.0, -3)},
           "hesk": {"gallery_faces": (0, 2.0, -3), "hesk": (0, 2.0, -3.5), "keth_bundle": (0.5, 1.0, -3)},
           "nhoa": {"gallery_silt": (0, 3.0, -2), "nhoa": (0, 1.5, -3.5), "ressa_name_shell": (0.5, 1.0, -3)},
           "ethren": {"still_square": (0, 0.2, -2), "ethren": (0, 1.5, -3.5), "copper_ring": (0.5, 1.0, -3),
                      "behind_ysolde": (-1.2, 0.0, 1.6)}}
SHOTS = {"ilun": ("U04", "U05", "U06", "U07", "U08"), "kahre": ("U09", "U10", "U11"),
         "virel": ("U12", "U13", "U14"), "hesk": ("U16", "U17", "U18"), "nhoa": ("U19", "U20", "U21", "U22"),
         "ethren": ("U23", "U24", "U25", "U26")}
SHOT_FRAMES = [((7.0, 3.0, 7.0), (0.0, 1.5, -2.0), 50), ((2.0, 1.8, 2.5), (0.0, 1.5, -3.5), 35),
               ((-5.0, 2.0, 4.0), (0.0, 1.2, -2.0), 45), ((1.5, 1.4, -0.5), (0.5, 1.0, -3.0), 30),
               ((0.0, 4.0, 8.0), (0.0, 1.0, -3.0), 45)]


def centre(k: int) -> tuple[float, float, float]:
    """Layer k (1..6; 7 is the Cage) at the bottom of its drop."""
    return (0.0, -DROP * k, -STEP * k)


def rest(after: int) -> tuple[float, float, float]:
    x, y, z = centre(after)
    return (14.0, y - 4.0, z - 14.0)


def add(a: tuple, b: tuple) -> list[float]:
    return [round(a[0] + b[0], 3), round(a[1] + b[1], 3), round(a[2] + b[2], 3)]


def layout() -> dict:
    blocks = [box("WellTop", 0.0, -0.25, 0.0, 10.0, 0.5, 10.0, visible=False)]
    spawns = {"WellTop": [0.0, 0.0, 2.0, 0.0]}
    marks = {"well_walls": [0.0, -6.0, -6.0, 0.0], "engine_socket": [1.5, 0.0, -1.0, 90.0],
             "first_floor": add(centre(1), (0, 0, 3)) + [0.0], "well_down": add(centre(7), (0, -20, 0)) + [0.0]}
    shots = {"U01": {"pos": [0.0, 4.0, 8.0], "look_at": [0.0, -8.0, -8.0], "fov": 55},
             "U02": {"pos": [3.0, 1.6, 1.0], "look_at": [1.5, 0.8, -1.0], "fov": 35},
             "U03": {"pos": add(centre(1), (4, 4, 8)), "look_at": add(centre(1), (0, 1, 3)), "fov": 50}}
    triggers = []
    prev = "ch20_started"
    for k, (v, room) in enumerate(LAYERS, 1):
        c = centre(k)
        blocks.append(box(f"Island{k}", c[0], c[1] - 0.25, c[2], 12.0, 0.5, 12.0, visible=False))
        spawns[f"Layer{k}"] = add(c, (0, 0, 4.5)) + [0.0]
        for a, off in ANCHORS[v].items():
            marks[a] = add(c, off) + [0.0]
        for sid, (pos, look, fov) in zip(SHOTS[v], SHOT_FRAMES):
            shots[sid] = {"pos": add(c, pos), "look_at": add(c, look), "fov": fov}
        triggers.append({"id": f"ch20_{v}", "activation": "touch", "at": add(c, (0, 0, 0.5)), "size": [4.0, 0, 1.0],
                         "requires_flag": prev, "blocked_by_flag": f"ch20_{v}_fought",
                         "payload": {"beat": f"ch20_{v}"}})
        prev = f"ch20_{v}_released"
    for n, after in ((1, 3), (2, 6)):
        r = rest(after)
        blocks.append(box(f"Rest{n}", r[0], r[1] - 0.25, r[2], 8.0, 0.5, 8.0, visible=False))
        spawns[f"Rest{n}"] = add(r, (0, 0, 2)) + [0.0]
    shots["U15"] = {"pos": add(rest(3), (5, 2.5, 5)), "look_at": add(rest(3), (0, 1, 0)), "fov": 45}
    shots["U27"] = {"pos": add(rest(6), (2, 1.6, 2.5)), "look_at": add(rest(6), (0, 1.2, 0)), "fov": 35}
    marks["sleeve"] = add(rest(6), (0.3, 1.2, 0)) + [0.0]
    cage = centre(7)
    blocks.append(floor("CageFloor", cage[0], cage[2], 10.0, 10.0, cage[1], "#4a5058"))
    spawns["Cage"] = add(cage, (0, 0, 8)) + [0.0]
    marks.update({"cage_seats": add(cage, (0, 1.5, -6)) + [0.0], "cage_line": add(cage, (0, 0, 2)) + [0.0],
                  "founders": add(cage, (0, 1.2, -5)) + [0.0]})
    shots.update({"U28": {"pos": add(cage, (6, 4, 10)), "look_at": add(cage, (0, 1.5, -4)), "fov": 50},
                  "U29": {"pos": add(cage, (2, 1.7, -1)), "look_at": add(cage, (0, 1.4, -5)), "fov": 35},
                  "U30": {"pos": add(cage, (0, 3, 2)), "look_at": add(cage, (0, -20, 0)), "fov": 50}})
    triggers.append({"id": "ch20_cage", "activation": "touch", "at": add(cage, (0, 0, 4)), "size": [4.0, 0, 1.0],
                     "requires_flag": "ch20_ethren_released", "blocked_by_flag": "ch20_cage_broken",
                     "payload": {"beat": "ch20_cage"}})
    return {
        "doc": "M5-A3P-1011 greybox (tools/act1/ch20_greybox.py; do not edit by hand): the Undertow's layers on env-art's "
        "Undertow kit (memory_island and the six memory rooms, instanced by the zone scene): the well's top (U00), six "
        "layers down and away, a landing after the third and the sixth (R1, R2), the founders' floor (the Cage). "
        "Collision only under the kit; the Cage's floor is greybox. Each layer's anchors are the marks its scenes name.",
        "sun": {"pitch_deg": -70.0, "yaw_deg": 0.0, "energy": 0.35, "color": "#7fd0d8"},  # held cyan from above
        "environment": {"background": "#081620", "ambient_color": "#2a5060", "ambient_energy": 0.45},
        "block_color": "#4a5058",
        "blocks": blocks,
        "spawns": spawns,
        "marks": marks,
        "actors": {},
        "shots": shots,
        "camera_volumes": [],
        "triggers": triggers,
    }


def scene() -> str:
    """The zone scene: Ch20Zone over the kit's memory_island under each layer, landing and the well's top, and each
    layer's room on its island."""
    pieces = ["memory_island"] + [room for _, room in LAYERS]
    ext = ['[ext_resource type="Script" path="res://game/levels/ch20/ch20_zone.gd" id="1_zone"]',
           '[ext_resource type="Script" path="res://game/levels/act1/zone_cast.gd" id="90_cast"]']
    ext += [f'[ext_resource type="PackedScene" path="{KIT}{p}.glb" id="p_{p}"]' for p in pieces]
    nodes = ['[node name="UndertowLayers" type="Node3D"]', 'script = ExtResource("1_zone")',
             'location_id = &"ch20/undertow_layers"',
             'layout_path = "res://game/levels/ch20/undertow_layers/undertow_layers_layout.json"',
             'hold_field_path = "res://game/data/flow/act3_field.json"', "", '[node name="Kit" type="Node3D" parent="."]']
    places = [(f"Layer{k}", centre(k), room) for k, (_, room) in enumerate(LAYERS, 1)]
    places += [("Rest1", rest(3), None), ("Rest2", rest(6), None)]
    for name, (x, y, z), room in places:
        nodes += ["", f'[node name="{name}Island" parent="Kit" instance=ExtResource("p_memory_island")]',
                  f"transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {x}, {y}, {z})"]
        if room:
            nodes += ["", f'[node name="{name}Room" parent="Kit" instance=ExtResource("p_{room}")]',
                      f"transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {x}, {y}, {z})"]
    nodes += ["", '[node name="Cast" type="Node" parent="."]', 'script = ExtResource("90_cast")']
    return "[gd_scene format=3]\n\n" + "\n".join(ext) + "\n\n" + "\n".join(nodes) + "\n"


def main() -> None:
    ZONE.mkdir(parents=True, exist_ok=True)
    (ZONE / "undertow_layers_layout.json").write_text(json.dumps(layout(), indent=1) + "\n", encoding="utf-8")
    (ZONE / "undertow_layers.tscn").write_text(scene(), encoding="utf-8")


if __name__ == "__main__":
    main()
