"""Writes the Brightwater ferry preview layout (M3-ENV-08):
game/levels/_tests/brightwater_ferry_kit/brightwater_ferry_layout.json.

    python3 assets_src/environments/kits/brightwater_ferry/bf_preview_layout.py

The layout is HalunaDresser's format (hymn-zone-layout/1, no terrain: every piece carries its own "y"), plus
"lamps" for BrightwaterFerryPreview: one entry [x, y, z, energy, range, shadow] per deck lantern, the light at the
lantern's flame (bf_props.LANTERN_FLAME below its ring). It composes the design notes' key shots
(brightwater_ferry.md §4): the ferry *Kind Weather* floating with her main deck at y SHIP_Y over the sea at the
datum, bow north, her hull, rig, deckhouse, awning, cargo and skiff all in the ship's frame at her origin; the
passengers' places under the awning and by the rails; eight lanterns; and to the east, on the strait's reef edge,
the drowned hulls on their coral.

m2-slice copies the pieces it wants (swap-in note in the task file); the ship pieces share one origin, so moving the
ferry is one transform.

M3-ENV-08B adds the daylight derelict view (brightwater_ferry.md §7): `brightwater_derelict_preview.tscn` (the
provisional `ch04_derelict` frame on HalunaMood's day mood), the ferry with the *Seventh Terrace* lying an oar's
length off her port side, fenders and boathooks between them, and four layouts, one per dresser, so a shot's setup can
show either sail state: `brightwater_derelict_layout.json` (the ferry, the derelict's hull, wheel, galley, hold, rig,
her three-days-drowned dressing and the alongside gear), `..._sails_set_layout.json` (the set sails and the spawn
membrane), `..._sails_lowered_layout.json` (hidden by default) and `..._name_board_layout.json` (the hero board, which
Rhen takes in C4-14). The night layout above is unchanged by it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import bf_common as bf  # noqa: E402
import bf_deckhouse  # noqa: E402
import bf_hull  # noqa: E402
import bf_props  # noqa: E402
import bf_terrace as bt  # noqa: E402

OUT = ROOT / "game" / "levels" / "_tests" / "brightwater_ferry_kit" / "brightwater_ferry_layout.json"
SHIP_Y = -bf.WATERLINE_Y  # the main deck's height above the sea
SHIP_PIECES = ("ferry_hull", "ferry_rig", "ferry_deckhouse", "ferry_awning", "ferry_cargo", "ferry_skiff")
LAMP_COLOR = "#FFB16E"  # oil_lamp (colour script ch04 key)
LAMP_ENERGY = 1.2  # ch04 lamp key
LAMP_RANGE_M = 7.0
LAMP_ATTENUATION = 1.2
# (name, ring position in the ship's frame, energy multiplier, range multiplier, casts shadows)
LANTERNS = (
    ("awning_fore", (0.0, bf_deckhouse.AWNING_RIDGE_Y - 0.06, -6.0), 1.0, 1.0, False),
    ("awning_aft", (0.0, bf_deckhouse.AWNING_RIDGE_Y - 0.08, -4.3), 1.0, 1.0, True),
    ("awning_port", (-bf_deckhouse.AWNING_SIDE_X, bf_deckhouse.AWNING_SIDE_Y - 0.02, -3.05), 0.9, 0.9, False),
    ("awning_starboard", (bf_deckhouse.AWNING_SIDE_X, bf_deckhouse.AWNING_SIDE_Y - 0.02, -3.05), 0.9, 0.9, False),
    ("deckhouse_door", (0.78, 1.98, bf_deckhouse.Z0 - 0.16), 0.9, 0.85, False),
    ("deckhouse_inside", (0.55, 1.95, 5.7), 0.75, 0.6, False),
    ("stern", bf_hull.stern_lantern_ring(), 1.0, 1.1, True),
    ("fore_fife", (0.62, 0.98 + 0.42, bf.FOREMAST_Z + bf_hull.FIFE_DZ[bf.FOREMAST_Z]), 0.8, 0.9, False),
    ("bow", bf_hull.bow_lantern_ring(), 0.9, 0.9, False),
)
# Passengers' places on the main deck (x, z, yaw deg): under the awning, along the rails, by the cargo.
BUNDLES = ((-1.25, -6.3, 8.0), (1.3, -5.9, 172.0), (-1.2, -4.2, -6.0), (1.25, -4.0, 185.0), (-2.6, -0.2, 90.0),
           (2.55, 2.0, -88.0), (-2.55, 6.0, 92.0))
# The drowned (world x, z, yaw deg), the reef patches under them and along the edge between.
HULKS = (("derelict_hulk_a", 101.0, -11.5, 108.0), ("derelict_hulk_b", -24.6, -238.6, 158.0),
         ("derelict_hulk_b", 301.0, 9.5, 64.0), ("derelict_hulk_a", 217.0, -47.0, -24.0))
REEFS = ((101.0, -12.0, 20.0), (124.0, -2.0, 34.0), (80.0, -20.0, 12.0), (-23.6, -237.6, 70.0), (-4.0, -208.0, 62.0),
         (300.0, 9.0, 28.0), (262.0, -10.0, 18.0), (217.0, -46.0, 24.0), (180.0, -30.0, 10.0), (150.0, -14.0, -10.0),
         (340.0, 22.0, 6.0), (-44.0, -268.0, 74.0))
FAR_LOD_M = 900.0  # the drowned stay LOD0 in the preview's shots (their silhouettes are the read)


def ship(piece: str) -> dict:
    return {"piece": piece, "at": [0.0, 0.0], "y": SHIP_Y, "yaw_deg": 0.0}


def lanterns() -> tuple[list[dict], list[list]]:
    pieces, lamps = [], []
    fx, fy, fz = bf_props.LANTERN_FLAME
    for _name, (x, y, z), e, r, shadow in LANTERNS:
        pieces.append({"piece": "ferry_lantern", "at": [round(x, 3), round(z, 3)], "y": round(SHIP_Y + y, 3),
                       "yaw_deg": 0.0})
        lamps.append([round(x + fx, 3), round(SHIP_Y + y + fy, 3), round(z + fz, 3), round(LAMP_ENERGY * e, 3),
                      round(LAMP_RANGE_M * r, 3), bool(shadow)])
    return pieces, lamps


def main() -> int:
    pieces = [ship(p) for p in SHIP_PIECES]
    lantern_pieces, lamps = lanterns()
    pieces += lantern_pieces
    for x, z, yaw in BUNDLES:
        pieces.append({"piece": "passenger_bundles", "at": [x, z], "y": SHIP_Y, "yaw_deg": yaw})
    for piece, x, z, yaw in HULKS:
        pieces.append({"piece": piece, "at": [x, z], "y": 0.0, "yaw_deg": yaw, "lod1_from_m": FAR_LOD_M})
    for x, z, yaw in REEFS:
        pieces.append({"piece": "reef_awash", "at": [x, z], "y": 0.0, "yaw_deg": yaw, "lod1_from_m": FAR_LOD_M})
    layout = {
        "schema": "hymn-zone-layout/1",
        "zone": "ch04/brightwater_ferry preview (M3-ENV-08): the kit composed for the design notes' key shots",
        "_about": "Generated by assets_src/environments/kits/brightwater_ferry/bf_preview_layout.py; do not edit by hand. "
                  "Coordinates: x east, z south (north = -Z), y explicit per piece (no terrain). The ferry's origin is "
                  f"(0, {SHIP_Y:g}, 0), bow north: every ship piece is placed there. The sea's datum is y 0. `lamps` are "
                  "[x, y, z, energy, range, shadow] (BrightwaterFerryPreview lights them, fog energy 0).",
        "seed": 8,
        "kit_dir": "res://assets/environments/kits/brightwater_ferry/",
        "materials_dir": "res://assets/environments/kits/brightwater_ferry/materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 3000.0,
        "lod_margin_m": 2.0,
        "ship_origin": [0.0, SHIP_Y, 0.0],
        "lamp_color": LAMP_COLOR,
        "lamp_attenuation": LAMP_ATTENUATION,
        "lamps": lamps,
        "pieces": pieces,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(layout, indent=1) + "\n", encoding="utf-8")
    print(f"LAYOUT {OUT.relative_to(ROOT)}: {len(pieces)} pieces, {len(lamps)} lamps")
    return 0


# ---------------------------------------------------------------------------------------------
# M3-ENV-08B: the derelict alongside, by day (the provisional ch04_derelict frame)
# ---------------------------------------------------------------------------------------------
DAY_DIR = OUT.parent
DAY_RES = "res://game/levels/_tests/brightwater_ferry_kit/"
DAY_SCENE = "brightwater_derelict_preview.tscn"
MANIFEST = DAY_DIR / "brightwater_ferry_preview_shots.json"
DERELICT_ORIGIN = (round(bt.DERELICT_IN_FERRY[0], 3), round(SHIP_Y + bt.DERELICT_IN_FERRY[1], 3),
                   round(bt.DERELICT_IN_FERRY[2], 3))
DAY_FERRY_PIECES = ("ferry_hull", "ferry_rig", "ferry_deckhouse", "ferry_awning", "ferry_cargo", "ferry_skiff")
DERELICT_PIECES = ("terrace_hull", "terrace_wheel", "terrace_galley", "terrace_hold", "terrace_rig", "terrace_derelict")
# The provisional ch04_derelict frame (brightwater_ferry.md §7.4): 08:10, the sun low in the east.
DAY_SUN = {"elevation": 15.0, "azimuth": 100.0, "time_h": 8.17, "color": "#FFD9B0", "energy": 2.6}
# Shots in the derelict's frame (eye, target, vFOV); D06 is the O07 insert's point (bf_terrace.INSERT_*).
DAY_SHOTS = {
    "D01": {"frame": "ferry", "eye": (-3.0, 1.6 + 1.6, -5.6), "look": (-8.9, 3.1, 1.2), "fov": 37.8},
    "D02": {"frame": "derelict", "eye": (-1.95, bt.POOP_Y + 1.6, 7.4), "look": (-0.6, 3.6, -6.0), "fov": 53.1},
    "D03": {"frame": "derelict", "eye": (0.15, 1.5, 1.55), "look": (0.0, 0.7, 3.95), "fov": 27.0},
    "D04": {"frame": "derelict", "eye": (-0.3, 1.55, -4.75), "look": (0.1, -1.2, -2.0), "fov": 37.8},
    "D06": {"frame": "derelict", "eye": bt.INSERT_EYE, "look": bt.INSERT_TARGET, "fov": bt.INSERT_FOV},
    "D09": {"frame": "derelict", "eye": (-26.0, -0.1, -18.0), "look": (2.0, 3.0, 2.0), "fov": 37.8},
}
DAY_SHOT_NAMES = {"D01": "gap", "D02": "deck_sails_set", "D03": "galley_bowls", "D04": "hold", "D06": "name_board",
                  "D09": "sails_lowered"}
# D09 shows the state after C4-14: the sails fallen, the membrane gone with the wraith, the board taken.
STATE_LOWERED = {"SailsSet": {"visible": False}, "SailsLowered": {"visible": True}, "NameBoard": {"visible": False}}


def day_eye(shot: dict, key: str) -> list[float]:
    o = (0.0, 0.0, 0.0) if shot["frame"] == "ferry" else DERELICT_ORIGIN
    p = shot[key]
    return [round(o[0] + p[0], 3), round(o[1] + p[1], 3), round(o[2] + p[2], 3)]


def _day_layout(pieces: list[dict], zone: str) -> dict:
    return {
        "schema": "hymn-zone-layout/1",
        "zone": zone,
        "_about": "Generated by assets_src/environments/kits/brightwater_ferry/bf_preview_layout.py; do not edit by hand. "
                  "Same frame as brightwater_ferry_layout.json (the ferry's origin at (0, 1.6, 0), bow north, the sea at y "
                  f"0); the Seventh Terrace's origin is {list(DERELICT_ORIGIN)}, an oar's length off the ferry's port side.",
        "seed": 8,
        "kit_dir": "res://assets/environments/kits/brightwater_ferry/",
        "materials_dir": "res://assets/environments/kits/brightwater_ferry/materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 3000.0,
        "lod_margin_m": 2.0,
        "pieces": pieces,
    }


def derelict_layouts() -> dict[str, dict]:
    ox, oy, oz = DERELICT_ORIGIN

    def at(piece: str, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> dict:
        return {"piece": piece, "at": [round(ox + dx, 3), round(oz + dz, 3)], "y": round(oy + dy, 3), "yaw_deg": 0.0}

    main = [ship(p) for p in DAY_FERRY_PIECES] + [at(p) for p in DERELICT_PIECES]
    main.append(ship("alongside_gear"))
    wx, wy, wz = bt.WHEEL_AT
    main[main.index(at("terrace_wheel"))] = at("terrace_wheel", wx, wy, wz)
    bx, by, bz = bt.NAME_BOARD_AT
    out = {
        "brightwater_derelict_layout.json": _day_layout(
            main, "ch04/brightwater_ferry preview (M3-ENV-08B): the Seventh Terrace alongside the ferry, by day"),
        "brightwater_derelict_sails_set_layout.json": _day_layout(
            [at("terrace_sails_set"), at("terrace_membrane")], "the derelict's set sails and the spawn membrane (C4-11 to C4-13)"),
        "brightwater_derelict_sails_lowered_layout.json": _day_layout(
            [at("terrace_sails_lowered")], "the derelict's sails fallen (C4-14, after the Canticle)"),
        "brightwater_derelict_name_board_layout.json": _day_layout(
            [at("terrace_name_board", bx, by, bz)], "the name-board on her transom (taken in C4-14)"),
    }
    anchors = {"derelict_origin": list(DERELICT_ORIGIN), "name_board": [round(ox + bx, 3), round(oy + by, 3), round(oz + bz, 3)],
               "wheel_axle": [round(ox + wx, 3), round(oy + wy, 3), round(oz + wz, 3)],
               "walk": [[n, round(ox + x0, 3), round(ox + x1, 3), round(oy + y, 3), round(oz + z0, 3), round(oz + z1, 3)]
                        for n, x0, x1, y, z0, z1 in bt.WALK]}
    out["brightwater_derelict_layout.json"]["anchors"] = anchors
    return out


def derelict_tscn() -> str:
    lines = ['[gd_scene load_steps={steps} format=3]', '',
             '[ext_resource type="Script" path="res://game/levels/ch02/haluna/haluna_mood.gd" id="1_rig"]',
             '[ext_resource type="Script" path="res://game/levels/ch02/haluna/weathering_tide.gd" id="2_tide"]',
             '[ext_resource type="Script" path="res://game/levels/ch02/haluna/haluna_dresser.gd" id="3_dresser"]',
             '[ext_resource type="Script" path="res://game/world/water/water_surface.gd" id="4_water"]',
             '[ext_resource type="Script" path="res://game/world/water/wave_set.gd" id="5_set"]',
             '[ext_resource type="Script" path="res://game/world/water/wave_component.gd" id="6_comp"]',
             f'[ext_resource type="Material" path="{DAY_RES}brightwater_derelict_water_material.tres" id="7_water_mat"]',
             f'[ext_resource type="Environment" path="{DAY_RES}brightwater_derelict_environment.tres" id="8_env"]',
             '[ext_resource type="Script" path="res://game/levels/ch02/haluna/haluna_shot_camera.gd" id="9_cam"]',
             '[ext_resource type="Script" path="res://game/world/camera_shot.gd" id="10_shot"]', '']
    waves = [("Swell0", 70.0, 64.0, 0.32, 0.45, 0.0), ("Swell1", 52.0, 33.0, 0.16, 0.55, 1.7),
             ("Swell2", 88.0, 17.0, 0.07, 0.6, 4.1), ("Swell3", 61.0, 8.0, 0.03, 0.6, 2.6)]
    for wid, d, wl, amp, st, ph in waves:
        lines += [f'[sub_resource type="Resource" id="{wid}"]', 'script = ExtResource("6_comp")', f'direction_deg = {d}',
                  f'wavelength_m = {wl}', f'amplitude_m = {amp}', f'steepness = {st}', f'phase_rad = {ph}', '']
    comps = ", ".join(f'SubResource("{w[0]}")' for w in waves)
    lines += ['[sub_resource type="Resource" id="SeaWaves"]', 'script = ExtResource("5_set")',
              f'components = Array[ExtResource("6_comp")]([{comps}])', 'amplitude_scale = 1.0', '']
    for sid, s in DAY_SHOTS.items():
        e, t = day_eye(s, "eye"), day_eye(s, "look")
        lines += [f'[sub_resource type="Resource" id="Shot{sid}"]', 'script = ExtResource("10_shot")', f'id = &"{sid}"',
                  f'position = Vector3({e[0]:g}, {e[1]:g}, {e[2]:g})', f'look_at = Vector3({t[0]:g}, {t[1]:g}, {t[2]:g})',
                  f'fov_deg = {s["fov"]:g}', '']
    sun = Color_hex(DAY_SUN["color"])
    lines += ['[node name="BrightwaterDerelictPreview" type="Node3D" node_paths=PackedStringArray("sun", "tide", "water", '
              '"world_environment", "dresser")]',
              'script = ExtResource("1_rig")', 'sun = NodePath("Sun")', 'tide = NodePath("Tide")', 'water = NodePath("Water")',
              'world_environment = NodePath("WorldEnvironment")', 'dresser = NodePath("Dresser")',
              f'sun_elevation_deg = {DAY_SUN["elevation"]}', f'sun_azimuth_deg = {DAY_SUN["azimuth"]}',
              f'time_of_day_h = {DAY_SUN["time_h"]}', 'wind_azimuth_deg = 250.0', 'wind_speed_m_s = 7.0', 'wind_gust = 0.3',
              'water_height_m = 0.0', '',
              '[node name="WorldEnvironment" type="WorldEnvironment" parent="."]', 'environment = ExtResource("8_env")', '',
              '[node name="Sun" type="DirectionalLight3D" parent="."]', f'light_color = {sun}',
              f'light_energy = {DAY_SUN["energy"]}', 'shadow_enabled = true', 'shadow_bias = 0.03', 'shadow_normal_bias = 1.0',
              'shadow_blur = 1.0', 'sky_mode = 1', 'directional_shadow_mode = 2', 'directional_shadow_split_1 = 0.05',
              'directional_shadow_split_2 = 0.15', 'directional_shadow_split_3 = 0.4',
              'directional_shadow_max_distance = 120.0', '',
              '[node name="Water" type="Node3D" parent="."]', 'script = ExtResource("4_water")',
              'publishes_water_level = true', 'wave_set = SubResource("SeaWaves")', 'material = ExtResource("7_water_mat")', '',
              '[node name="Tide" type="Node" parent="." node_paths=PackedStringArray("water")]',
              'script = ExtResource("2_tide")', 'water = NodePath("../Water")', '']
    for node, layout, visible in (("Dresser", "brightwater_derelict_layout.json", True),
                                  ("SailsSet", "brightwater_derelict_sails_set_layout.json", True),
                                  ("SailsLowered", "brightwater_derelict_sails_lowered_layout.json", False),
                                  ("NameBoard", "brightwater_derelict_name_board_layout.json", True)):
        lines += [f'[node name="{node}" type="Node3D" parent="." node_paths=PackedStringArray("tide")]']
        if not visible:
            lines.append('visible = false')
        lines += ['script = ExtResource("3_dresser")', f'layout_path = "{DAY_RES}{layout}"', 'tide = NodePath("../Tide")', '']
    lines += ['[node name="Cameras" type="Node3D" parent="."]', '']
    for sid in DAY_SHOTS:
        lines += [f'[node name="{sid}" type="Camera3D" parent="Cameras"]', 'near = 0.05', 'far = 6000.0',
                  'script = ExtResource("9_cam")', f'shot = SubResource("Shot{sid}")', '']
    steps = 1 + 10 + len(waves) + 1 + len(DAY_SHOTS)
    return "\n".join(lines).rstrip("\n").replace("{steps}", str(steps)) + "\n"


def Color_hex(h: str) -> str:  # noqa: N802 (the .tscn's Color syntax)
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    return f"Color({r:.4f}, {g:.4f}, {b:.4f}, 1)"


def derelict_manifest_shots() -> list[dict]:
    out = []
    for sid, name in DAY_SHOT_NAMES.items():
        setup: dict = {"globals": {"hymn_wind_time": 40.0}, "viewport": {"use_taa": False, "screen_space_aa": 1}}
        if sid == "D09":
            setup["nodes"] = STATE_LOWERED
        out.append({"id": f"brightwater_{sid.lower()}_{name}", "scene": DAY_RES + DAY_SCENE, "camera": f"Cameras/{sid}",
                    "resolution": [960, 540], "settle_frames": 24, "setup": setup})
    return out


def write_derelict_preview() -> None:
    for name, layout in derelict_layouts().items():
        (DAY_DIR / name).write_text(json.dumps(layout, indent=1) + "\n", encoding="utf-8")
    (DAY_DIR / DAY_SCENE).write_text(derelict_tscn(), encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    keep = [s for s in manifest["shots"] if not s["scene"].endswith(DAY_SCENE)]
    manifest["shots"] = keep + derelict_manifest_shots()
    MANIFEST.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print(f"DERELICT {DAY_SCENE}: {len(DAY_SHOTS)} shots, origin {DERELICT_ORIGIN}")


if __name__ == "__main__":
    code = main()
    write_derelict_preview()
    sys.exit(code)
