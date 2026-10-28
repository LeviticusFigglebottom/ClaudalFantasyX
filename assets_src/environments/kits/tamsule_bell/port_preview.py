"""Writes the Tamsule port kit preview (tamsule.md; M3-C07-04): game/levels/_tests/tamsule_port_kit/tamsule_port_kit.tscn
and its shot manifest. Deterministic: PORT below is the only source; rerun after changing it.

    python3 assets_src/environments/kits/tamsule_bell/port_preview.py

The frame is the ch07/tamsule greybox's (M3-C07-02, tamsule_layout.json): x east, north -Z, the decks' tops at y 0,
the river 1.6 m under them (WATER_Y). Each greybox block is dressed with the kit pieces tamsule.md §0 names, at the
block's place, so act1-chapters can copy the rows into the zone. The Bell's whole ring (tamsule_bell.md, the kit
preview's own layout) stands on its axis at BELL_AT, north of the gantry foot, with the shophouse banks round its
reach; the noon environment and the water look are the Bell kit preview's.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import market  # noqa: E402
import preview_scene as ps  # noqa: E402

OUT_DIR = ROOT / "game" / "levels" / "_tests" / "tamsule_port_kit"
RES_DIR = "res://game/levels/_tests/tamsule_port_kit/"
BELL_RES = "res://game/levels/_tests/tamsule_bell_kit/"
KIT = ps.KIT
CW = "res://assets/environments/kits/corrow/"
WATER_Y = market.WATER_Y  # -1.6
BELL_AT = (0.0, WATER_Y, -75.0)  # the Bell's axis at the river datum (its galleries reach r 41: clear of the port)
BELL_KEEP = ("Bell", "GoalRing", "GantryHead", "GantryLeg", "CatchPool", "Gallery", "Platform", "OruvelMoorings",
             "Mooring", "Boat", "Pennants", "LaneSign", "House", "Boardwalk")
BELL_DROP = ("BoatMouth",)  # the reach preview's river-mouth boats would sit in the port

# (node, piece, x, y, z, yaw deg): one row per piece; the comment names the greybox block it dresses.
PORT = [
    # Quay (0, 20): the barge's landing at the river mouth.
    ("QuayDeckW", "port_deck_8m", -3.5, 0.0, 18.5, 0.0), ("QuayDeckE", "port_deck_8m", 3.5, 0.0, 18.5, 0.0),
    ("QuayEdgeW", "port_deck_8m_rail", -3.5, 0.0, 21.5, 0.0), ("QuayEdgeE", "port_deck_8m_rail", 3.5, 0.0, 21.5, 0.0),
    ("QuayPostW", "mooring_post", -7.6, WATER_Y, 24.8, 0.0), ("QuayPostE", "mooring_post", 7.6, WATER_Y, 24.8, 0.0),
    ("Barge", "watch_boat", -10.5, WATER_Y, 21.0, 90.0),
    ("QuayBridge", "plank_bridge_4m", 0.0, 0.0, 14.0, 90.0),
    # Market (0, 4): deck islands with stalls, boats moored round, bunting across.
    ("MarketDeck0", "port_deck_8m", -8.0, 0.0, 0.5, 0.0), ("MarketDeck1", "port_deck_8m", 0.0, 0.0, 0.5, 0.0),
    ("MarketDeck2", "port_deck_8m", 8.0, 0.0, 0.5, 0.0), ("MarketDeck3", "port_deck_8m", -8.0, 0.0, 7.5, 0.0),
    ("MarketDeck4", "port_deck_8m", 0.0, 0.0, 7.5, 0.0), ("MarketDeck5", "port_deck_8m", 8.0, 0.0, 7.5, 0.0),
    ("StallA", "market_stall", -6.0, 0.0, 6.0, 0.0), ("StallB", "market_stall", 6.0, 0.0, 2.0, 180.0),
    ("StallC", "market_stall", -1.5, 0.0, 9.5, 0.0), ("StallD", "market_stall", 2.5, 0.0, -1.5, 180.0),
    ("StallE", "market_stall", -9.5, 0.0, -1.0, 180.0), ("StallF", "market_stall", 9.0, 0.0, 9.5, 0.0),
    ("MarketBoatW0", "market_boat_a", -13.6, WATER_Y, -0.5, 92.0),
    ("MarketBoatW1", "market_boat_b", -13.4, WATER_Y, 9.0, 86.0),
    ("MarketBoatE0", "market_boat_b", 13.4, WATER_Y, -1.0, 94.0),
    ("MarketBoatS0", "market_boat_a", -5.0, WATER_Y, 12.8, 2.0),
    ("MarketBoatS1", "market_boat_b", 6.0, WATER_Y, 12.6, 178.0),
    ("BuntingMarket0", "bunting_12m", -4.0, 0.0, 4.0, 0.0), ("BuntingMarket1", "bunting_12m", 6.0, 0.0, 4.0, 90.0),
    # Stilt lane (-20, 4): boardwalks, shophouses on both sides with their boards out.
    ("LaneBridge", "plank_bridge_4m", -13.0, 0.0, 4.0, 0.0),
    ("LaneWalk0", "boardwalk_8m", -18.0, WATER_Y, 2.5, 180.0), ("LaneWalk1", "boardwalk_8m", -26.0, WATER_Y, 2.5, 180.0),
    ("LaneWalk2", "boardwalk_8m", -18.0, WATER_Y, 5.5, 0.0), ("LaneWalk3", "boardwalk_8m", -26.0, WATER_Y, 5.5, 0.0),
    ("LaneHouseN0", "shophouse_a", -17.5, WATER_Y, -4.2, 0.0), ("LaneHouseN1", "shophouse_b", -26.0, WATER_Y, -3.8, 0.0),
    ("LaneHouseS0", "shophouse_b", -17.0, WATER_Y, 12.0, 180.0), ("LaneHouseS1", "shophouse_a", -25.5, WATER_Y, 12.4, 180.0),
    ("BuntingLane", "bunting_12m", -22.0, 0.0, 4.0, 0.0),
    # Gantry foot (0, -14): decks under the Bell, the lane boards, bunting.
    ("GantryBridge", "plank_bridge_4m", 0.0, 0.0, -6.0, 90.0),
    ("GantryDeck0", "port_deck_8m", -4.0, 0.0, -11.0, 0.0), ("GantryDeck1", "port_deck_8m", 4.0, 0.0, -11.0, 0.0),
    ("GantryDeck2", "port_deck_8m_rail", -4.0, 0.0, -17.0, 180.0),
    ("GantryDeck3", "port_deck_8m_rail", 4.0, 0.0, -17.0, 180.0),
    ("GantryBoardW", "signboard_gilded", -3.2, 0.0, -18.6, 0.0), ("GantryBoardE", "signboard_gilded", 3.2, 0.0, -18.6, 0.0),
    ("BuntingGantry", "bunting_12m", 0.0, 0.0, -13.0, 0.0),
    # Market boats (14, -12): packed hull to hull, where Tavi runs (TP06, TP07).
    ("BoatBridge", "plank_bridge_4m", 8.5, 0.0, -12.0, 0.0),
    ("PackedBoat0", "market_boat_a", 14.0, WATER_Y, -14.6, 0.0), ("PackedBoat1", "market_boat_a", 14.4, WATER_Y, -12.5, 180.0),
    ("PackedBoat2", "market_boat_b", 13.6, WATER_Y, -10.4, 0.0), ("PackedBoat3", "market_boat_b", 15.0, WATER_Y, -8.6, 180.0),
    ("PackedBoat4", "watch_boat", 18.6, WATER_Y, -16.4, 4.0),
    # Harbour (24, 10): B10's casting off.
    ("HarbourBridge0", "plank_bridge_4m", 14.0, 0.0, 8.0, 0.0), ("HarbourBridge1", "plank_bridge_4m", 18.0, 0.0, 8.0, 0.0),
    ("HarbourDeck0", "port_deck_8m_rail", 24.0, 0.0, 6.0, 270.0), ("HarbourDeck1", "port_deck_8m_rail", 24.0, 0.0, 13.0, 270.0),
    ("HarbourPost0", "mooring_post", 27.6, WATER_Y, 4.5, 0.0), ("HarbourPost1", "mooring_post", 27.6, WATER_Y, 15.5, 0.0),
    ("Trader", "trader_boat", 30.6, WATER_Y, 10.0, 0.0),
]
PORT_KIT = {"trader_boat": CW}

SHOTS = [  # tamsule.md §3
    ("TP01", 24, (0.0, 1.2, 80.0), (0.0, 22.0, -60.0), "the port and the Bell from the river mouth"),
    ("TP02", 35, (3.0, 1.6, 22.0), (-9.0, 0.6, 18.0), "the quay: the barge tying up"),
    ("TP03", 35, (6.0, 1.6, 10.0), (-6.0, 0.8, 0.0), "the floating market"),
    ("TP04", 28, (-14.0, 1.6, 6.0), (-30.0, 2.4, 3.5), "the stilt lane"),
    ("TP05", 24, (0.0, 1.4, -8.0), (0.0, 9.5, -40.0), "the gantry foot, up to the Bell"),
    ("TP06", 35, (4.0, 1.7, -8.0), (16.0, 0.6, -12.0), "across the market boats: Tavi's run"),
    ("TP07", 50, (11.0, 1.6, -12.4), (16.0, 1.5, -12.4), "the two-shot on the boats"),
    ("TP08", 35, (31.0, 2.2, 14.0), (0.0, 6.0, -10.0), "from the trader's stern: Tamsule and the Bell"),
    ("TP09", 65, (31.0, 2.2, 14.0), (BELL_AT[0] + 14.0, 0.5, BELL_AT[2] + 18.0), "the moorings under the Bell"),
]


def pieces() -> list[tuple[str, str, tuple, float, float]]:
    out = [(n, p, (x, y, z), yaw, 1.0) for n, p, x, y, z, yaw in PORT]
    for name, piece, pos, yaw, scale in ps.layout():
        if not name.startswith(BELL_KEEP) or name.startswith(BELL_DROP):
            continue
        at = (round(pos[0] + BELL_AT[0], 3), round(pos[1] + BELL_AT[1], 3), round(pos[2] + BELL_AT[2], 3))
        out.append(("Reach" + name, piece, at, yaw, scale))
    return out


def write_scene(path: Path) -> None:
    rows = pieces()
    ext = [("Script", "res://game/levels/ch02/haluna/haluna_mood.gd", "rig"),
           ("Script", "res://game/levels/ch02/haluna/haluna_shot_camera.gd", "cam"),
           ("Script", "res://game/world/camera_shot.gd", "shot"),
           ("Script", "res://game/world/water/water_surface.gd", "water"),
           ("Resource", "res://game/world/water/lagoon_waves.tres", "waves"),
           ("Material", BELL_RES + "tamsule_water_material.tres", "water_mat"),
           ("Environment", BELL_RES + "tamsule_noon_environment.tres", "env"),
           ("Texture2D", ps.HALUNA_TEX + "sand_albedo.png", "sand")]
    kinds = sorted({r[1] for r in rows})
    ext += [("PackedScene", PORT_KIT.get(k, KIT) + f"{k}.glb", k) for k in kinds]
    ids = {key: f"{i + 1}_{key}" for i, (_t, _p, key) in enumerate(ext)}
    lines = ["[gd_scene format=3]", ""]
    lines += [f'[ext_resource type="{t}" path="{p}" id="{ids[k]}"]' for t, p, k in ext]
    lines.append("")
    for sid, mm, pos, look, _note in SHOTS:
        lines += [f'[sub_resource type="Resource" id="Shot{sid}"]', f'script = ExtResource("{ids["shot"]}")',
                  f'id = &"{sid}"', f"position = {ps.vec3(pos)}", f"look_at = {ps.vec3(look)}",
                  f"fov_deg = {ps.vfov(mm)}", ""]
    lines += ['[sub_resource type="PlaneMesh" id="RiverbedMesh"]', "size = Vector2(2400, 2400)", "",
              '[sub_resource type="StandardMaterial3D" id="RiverbedMat"]', f"albedo_color = {ps.color('#9C8E76')}",
              f'albedo_texture = ExtResource("{ids["sand"]}")', "roughness = 0.95", "uv1_triplanar = true",
              "uv1_scale = Vector3(0.5, 0.5, 0.5)", ""]
    lines += ['[node name="TamsulePortKit" type="Node3D" node_paths=PackedStringArray("sun", "water", '
              '"world_environment")]', f'script = ExtResource("{ids["rig"]}")', 'sun = NodePath("Sun")',
              'water = NodePath("Water")', 'world_environment = NodePath("WorldEnvironment")',
              "sun_elevation_deg = 78.0", "sun_azimuth_deg = 180.0", "time_of_day_h = 12.25",
              "wind_azimuth_deg = 0.0", "wind_speed_m_s = 4.0", "wind_gust = 0.25",
              f"water_height_m = {WATER_Y}", "",
              '[node name="WorldEnvironment" type="WorldEnvironment" parent="."]',
              f'environment = ExtResource("{ids["env"]}")', "",
              '[node name="Sun" type="DirectionalLight3D" parent="."]', f"light_color = {ps.color('#FFF3E7')}",
              "light_energy = 3.2", "shadow_enabled = true", "shadow_bias = 0.03", "shadow_normal_bias = 1.0",
              "shadow_blur = 1.2", "sky_mode = 1", "directional_shadow_mode = 2",
              "directional_shadow_split_1 = 0.05", "directional_shadow_split_2 = 0.15",
              "directional_shadow_split_3 = 0.4", "directional_shadow_max_distance = 400.0", "",
              '[node name="Water" type="Node3D" parent="."]', f"position = Vector3(0, {WATER_Y}, 0)",
              f'script = ExtResource("{ids["water"]}")', "publishes_water_level = true",
              f'wave_set = ExtResource("{ids["waves"]}")', f'material = ExtResource("{ids["water_mat"]}")', "",
              '[node name="Riverbed" type="MeshInstance3D" parent="."]', f"position = Vector3(0, {market.BED_Y}, 0)",
              'mesh = SubResource("RiverbedMesh")', 'surface_material_override/0 = SubResource("RiverbedMat")', "",
              '[node name="Port" type="Node3D" parent="."]', ""]
    for name, piece, pos, yaw, scale in rows:
        lines += [f'[node name="{name}" parent="Port" instance=ExtResource("{ids[piece]}")]', f"position = {ps.vec3(pos)}"]
        if yaw:
            lines.append(f"rotation = Vector3(0, {math.radians(yaw):.6f}, 0)")
        if scale != 1.0:
            lines.append(f"scale = {ps.vec3((scale, scale, scale))}")
        lines.append("")
    lines += ['[node name="Cameras" type="Node3D" parent="."]', ""]
    for sid, _mm, _pos, _look, _note in SHOTS:
        lines += [f'[node name="{sid}" type="Camera3D" parent="Cameras"]', "near = 0.05", "far = 4000.0",
                  f'script = ExtResource("{ids["cam"]}")', f'shot = SubResource("Shot{sid}")', ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_layout(path: Path) -> None:
    """The port's rows as data, for the ch07/tamsule zone (kit_dir per piece, positions in the greybox's frame)."""
    data = {"_about": "Generated by assets_src/environments/kits/tamsule_bell/port_preview.py (tamsule.md §0): the port's "
                      "kit pieces at the ch07/tamsule greybox blocks' places (decks at y 0, the river at y -1.6). "
                      "Copy into the zone's dressing.",
            "pieces": [{"name": n, "piece": p, "kit_dir": PORT_KIT.get(p, KIT), "at": [x, z], "y": y, "yaw_deg": yaw}
                       for n, p, x, y, z, yaw in PORT],
            "bell_axis": list(BELL_AT)}
    path.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    import argparse  # noqa: PLC0415

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(OUT_DIR))
    out = Path(ap.parse_args(argv).out)
    out.mkdir(parents=True, exist_ok=True)
    write_scene(out / "tamsule_port_kit.tscn")
    write_layout(out / "tamsule_port_layout.json")
    print(f"TAMSULE_PORT {len(pieces())} pieces -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
