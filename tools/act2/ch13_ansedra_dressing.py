#!/usr/bin/env python3
"""Ch13, Ansedra: env-art's Ansedra kit (ansedra.py, ansedra_zones.py; M3-ENV-721) on the greybox zones `ch13/ansedra`,
`ch13/sanctum` and `ch13/lamp_archive` (M4-A2P-043; ansedra.md §3's swap map; ADR 0200).

The greybox keeps the gameplay (collision, spawns, marks, triggers, the story): every causeway, rail, lamp, house and
wall stays as it is and only its look is swapped. The walks and buildings are built from the same greybox
(ansedra_zones.py), so their stone stands where the collision does.

Writes, per zone (game/levels/ch13/<zone>/):
  <zone>_dressing.json         ZoneKitDressing's layout
  <zone>_environment.tres      the zone's grade: colour script ch13 (16:30 overcast, still air, lut_ch13_still)
  <zone>_water_material.tres   the still mirror (overcast_lagoon under ch13: deep #5E6E80, roughness 0) and
  <zone>_waves.tres            the near-still water (M4-A2P-047's mirror mode replaces both when rendering lands it)
and env-art's preview of each zone (game/levels/_tests/ch13_zones/<zone>_dressed.tscn).

    python3 tools/act2/ch13_ansedra_dressing.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT_SRC = ROOT / "assets_src" / "environments" / "kits" / "haluna"
sys.path.insert(0, str(KIT_SRC))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ansedra_zones as az  # noqa: E402
import arena_scenes as ar  # noqa: E402
import ch10_fen_dressing as fen  # noqa: E402  (the shared helpers: _put, _look_xform)
import ch11_lowlight_dressing as low  # noqa: E402  (the water and wave writers)

KIT = "res://assets/environments/kits/haluna/"
ZONES = ROOT / "game" / "levels" / "ch13"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "ch13_zones"
LUT = "res://assets/environments/zones/ansedra/lut_ch13_still.png"
SEED = 13
NEVER_LOD_M = 5000.0
DATUM_Y = az.WATER_Y
r3 = fen.r3
_put = fen._put

# Colour script ch13: 16:30 overcast, perfectly still air; key #FFF9F2 1.6 from 25 deg / 230 deg (the layout's sun), fill
# #8A96A4 0.6, sky #8A96A4 / #C8C4BA, fog #B8B8B2, exposure 0.75, saturation x0.8 (in the LUT), lut_ch13_still.
CH13 = {
    "sub_frame": "ch13", "lut": LUT, "exposure": 0.75, "fill": {"color": "#8A96A4", "energy": 0.6},
    "fog": {"color": "#B8B8B2", "aerial": 0.4, "density": 0.004, "sky_affect": 0.1, "height": 0.0,
            "height_density": 0.0},
    "sky_shader": ar.LOW_SUN_SKY,
    "sky": dict(ar.CORROW_SKY, col_zenith="#8A96A4", col_horizon_sun="#C8C4BA", col_horizon_away="#C8C4BA",
                col_ground="#6A7280", sky_energy=1.0, sun_disc_energy=0.0, halo_energy=0.2, glow_energy=0.2,
                col_band="#C8C4BA", band_energy=0.0, cloud_coverage=0.97, col_cloud_lit="#D6D4CC",
                col_cloud_shadow="#8A909A", cloud_sun_energy=1.4, cloud_ambient_energy=1.2, col_glow="#E8E6E0"),
}
# The still mirror: the overcast lagoon's absorption under ch13's deep colour, every ripple and foam off, roughness 0.
MIRROR = {"name": "mirror_lagoon", "shader": "res://game/shaders/water/water_ocean.gdshader",
          "params": [("col_deep", "#5E6E80"), ("col_scatter_shallow", "#6E8A92"),
                     ("absorption_per_m", "Vector3(2, 0.5, 0.42)"), ("absorption_scale", 1.5), ("scatter_energy", 0.04),
                     ("caustic_strength", 0.0), ("col_foam", "#E8E4E0"), ("col_sss", "#6E8A92"), ("use_foam", "false"),
                     ("roughness_near", 0.0), ("roughness_far", 0.0), ("detail_strength", 0.0), ("use_caustics", "false"),
                     ("use_ssr", "true"), ("use_sss", "false")]}
STILL_WAVES = [(20.0, 6.0, 0.0008, 0.02)]

# Bowl-domes on their own islands round the walks (x, z, scale): the city of the mirror (ansedra.md §0), out of reach.
CITY_DOMES = [(-26.0, 4.0, 1.0), (26.0, -4.0, 1.15), (-30.0, -16.0, 0.9), (30.0, -22.0, 1.0), (-24.0, -64.0, 1.3),
              (26.0, -62.0, 1.2), (-40.0, -84.0, 1.5), (40.0, -92.0, 1.4), (-58.0, -12.0, 1.6), (60.0, -20.0, 1.5),
              (-22.0, -128.0, 1.8), (18.0, -124.0, 2.0), (-62.0, -60.0, 1.4), (62.0, -58.0, 1.3)]


def _layout(zone: str) -> dict:
    return json.loads((ZONES / zone / f"{zone}_layout.json").read_text(encoding="utf-8"))


def ansedra() -> dict:
    pieces = [_put(n, 0.0, 0.0, 0.0, 0.0, lod1_from_m=NEVER_LOD_M) for n in CITY_PIECES]
    for k, (x, z, s) in enumerate(CITY_DOMES):
        pieces.append(_put("bowl_dome", x, DATUM_Y, z, (k * 37.0) % 360.0, scale=s))
    pieces.append(_put("ansedra_far_domes", 0.0, DATUM_Y, -45.0, 0.0, lod1_from_m=1200.0))
    return {"pieces": pieces}


BOUND_TEAL = ar.BOUND_TEAL
CITY_PIECES = ("ansedra_walks_n", "ansedra_walks_we", "ansedra_buildings", "ansedra_ground")
SANCTUM_PIECES = ("ansedra_sanctum",)
ARCHIVE_PIECES = ("ansedra_archive", "ansedra_archive_stacks_w", "ansedra_archive_stacks_e")


def sanctum() -> dict:
    lay = _layout("sanctum")
    bl = {b["id"]: b for b in lay["blocks"]}
    b = bl["Basin"]
    bx, bz, sx, sz = b["pos"][0], b["pos"][2], b["size"][0], b["size"][2]
    pieces = [_put(n, 0.0, 0.0, 0.0, 0.0, lod1_from_m=NEVER_LOD_M) for n in SANCTUM_PIECES]
    # The light from beneath that never moves: bound teal under the basin's water, steady; dim Order lamps on the nave.
    lights = [{"at": [r3(bx + dx), az.BASIN_FLOOR_Y + 0.25, r3(bz + dz)], "energy": 1.3, "range": 7.5}
              for dx in (-2.5, 2.5) for dz in (-6.0, 0.0, 6.0)]
    lights += [{"at": [x, 3.2, z], "energy": 0.45, "range": 6.0} for x in (-11.2, 11.2) for z in (-40.0, -30.0, -20.0)]
    lights.append({"at": [0.0, 3.0, -6.0], "energy": 0.5, "range": 7.0})
    return {
        "pieces": pieces, "fire_light_color": BOUND_TEAL, "fire_lights": lights,
        # The basin's still water: a perfect mirror that has not stirred in four hundred years.
        "waters": [{"name": "Basin", "pos": [bx, az.STILL_Y, bz], "size": [sx, sz],
                    "material": "res://game/levels/ch13/sanctum/sanctum_water_material.tres",
                    "wave_set": "res://game/levels/ch13/sanctum/sanctum_waves.tres"}],
    }


def lamp_archive() -> dict:
    lay = _layout("lamp_archive")
    bl = {b["id"]: b for b in lay["blocks"]}
    pieces = [_put(n, 0.0, 0.0, 0.0, 0.0, lod1_from_m=NEVER_LOD_M) for n in ARCHIVE_PIECES]
    lights = []
    for tid in ("LedgerTable", "RollTable"):  # a reading lamp's bound light over each table
        t = bl[tid]
        lights.append({"at": [t["pos"][0], 2.4, t["pos"][2]], "energy": 0.9, "range": 5.5, "shadow": tid == "LedgerTable"})
    lights += [{"at": [0.0, 4.5, z], "energy": 0.4, "range": 7.0} for z in (-5.0, -15.0, -27.0)]
    return {"pieces": pieces, "fire_light_color": BOUND_TEAL, "fire_lights": lights}


def layout(zone: str) -> dict:
    body = {"ansedra": ansedra, "sanctum": sanctum, "lamp_archive": lamp_archive}[zone]()
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": f"Generated by tools/act2/ch13_ansedra_dressing.py from env-art's Ansedra kit on ch13/{zone}'s greybox "
                  "(M4-A2P-043; ansedra.md §3). Do not edit by hand.",
        "seed": SEED,
        "kit_dir": KIT,
        "materials_dir": KIT + "materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 1500.0,
        "lod_margin_m": 3.0,
        "greybox": {"hide_all": True, "keep": []},
        "environment": f"res://game/levels/ch13/{zone}/{zone}_environment.tres",
        "time_of_day_h": 16.5,
        **body,
    }


def write_water(zone: str) -> None:
    out = ZONES / zone
    m = MIRROR
    lines = ['[gd_resource type="ShaderMaterial" load_steps=2 format=3]', "",
             f'[ext_resource type="Shader" path="{m["shader"]}" id="1_ocean"]', "", "[resource]",
             f'resource_name = "{m["name"]}"', "render_priority = 0", 'shader = ExtResource("1_ocean")']
    for k, v in m["params"]:
        if isinstance(v, str) and v.startswith("#"):
            c = [int(v[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            v = f"Color({c[0]:.4f}, {c[1]:.4f}, {c[2]:.4f}, 1)"
        lines.append(f"shader_parameter/{k} = {v}")
    (out / f"{zone}_water_material.tres").write_text("\n".join(lines) + "\n", encoding="utf-8")
    saved = ar.LOWLIGHT_ARENA["sea"]["waves"]
    try:
        ar.LOWLIGHT_ARENA["sea"]["waves"] = STILL_WAVES
        low.write_waves(out / f"{zone}_waves.tres")
    finally:
        ar.LOWLIGHT_ARENA["sea"]["waves"] = saved


CAMERAS = {
    "ansedra": [
        ("A01_moorings", (0.0, 2.5, 16.0), (0.0, 6.0, -94.0), 40.0),
        ("Moorings_barges", (-4.0, 1.6, 8.0), (-11.0, 0.5, 13.0), 55.0),
        ("CausewayN_walk", (0.0, 1.7, 1.0), (0.0, 1.5, -30.0), 55.0),
        ("Centre_sefir", (4.0, 1.7, -36.0), (5.0, 3.5, -46.0), 55.0),
        ("CausewayW_corran", (-14.0, 1.7, -40.0), (-44.0, 2.5, -42.0), 55.0),
        ("Archive_dome", (28.0, 1.7, -38.0), (42.0, 6.0, -40.0), 55.0),
        ("Sanctum_approach", (0.0, 1.7, -56.0), (0.0, 7.0, -94.0), 55.0),
        ("Sanctum_door", (0.0, 1.7, -84.5), (0.0, 3.0, -88.6), 60.0),
        ("Mirror_low", (6.0, 0.4, -20.0), (30.0, 4.0, -60.0), 50.0),
        ("Over_city", (40.0, 40.0, 30.0), (0.0, 0.0, -50.0), 55.0),
    ],
    "sanctum": [
        ("Gate_in", (0.0, 1.7, 0.5), (0.0, 2.5, -20.0), 60.0),
        ("S01_basin", (0.0, 1.6, -16.0), (0.0, 0.5, -40.0), 45.0),
        ("Basin_mirror", (-4.0, 0.9, -19.0), (2.0, -0.1, -34.0), 50.0),
        ("Nave_up", (8.0, 1.6, -18.0), (-2.0, 12.0, -34.0), 70.0),
        ("Ethren_place", (3.0, 1.6, -36.0), (0.0, 1.6, -46.0), 55.0),
        ("Corran_side", (9.0, 1.6, -30.0), (6.0, 1.2, -44.0), 55.0),
        ("Back_to_gate", (0.0, 1.7, -43.0), (0.0, 2.0, -8.0), 60.0),
        ("Ledge_close", (-6.2, 1.2, -24.0), (-5.2, 0.2, -30.0), 50.0),
        ("Vestibule", (-4.5, 1.7, -2.0), (3.0, 3.0, -10.0), 60.0),
        ("Over_nave", (10.0, 8.5, -14.0), (-2.0, 0.0, -36.0), 60.0),
    ],
    "lamp_archive": [
        ("R01_reading_room", (0.0, 2.2, -4.0), (0.0, 1.0, -24.0), 50.0),
        ("Door_in", (0.0, 1.7, 0.5), (0.0, 2.0, -16.0), 60.0),
        ("Ledgers", (-0.2, 1.6, -9.5), (-1.5, 0.9, -12.0), 50.0),
        ("Cantor_roll", (3.5, 1.6, -21.5), (1.5, 0.9, -24.0), 50.0),
        ("Stacks_west", (-2.5, 1.7, -8.8), (-7.0, 2.5, -8.8), 55.0),
        ("Stacks_east", (3.0, 1.7, -14.0), (8.0, 2.0, -20.0), 55.0),
        ("Aisle_far", (0.0, 1.7, -30.0), (0.0, 2.0, -2.0), 60.0),
        ("Up_vault", (0.0, 1.6, -16.0), (0.0, 10.0, -20.0), 70.0),
        ("Spines_close", (4.8, 1.6, -9.0), (7.0, 1.6, -11.0), 50.0),
        ("Over_room", (8.5, 7.0, -2.0), (-2.0, 0.0, -20.0), 60.0),
    ],
}
CLS = {"ansedra": "Ansedra", "sanctum": "Sanctum", "lamp_archive": "LampArchive"}
ZONE_NAMES = ("ansedra", "sanctum", "lamp_archive")


def write_preview(zone: str) -> Path:
    if zone != "ansedra":
        return _write_interior_preview(zone)
    lines = ["[gd_scene format=3]", "",
             '[ext_resource type="Script" path="res://game/levels/ch13/ch13_zone.gd" id="1_zone"]',
             '[ext_resource type="Script" path="res://game/levels/act1/zone_kit_dressing.gd" id="2_dressing"]',
             '[ext_resource type="Script" path="res://game/levels/ch02/haluna/weathering_tide.gd" id="3_tide"]',
             '[ext_resource type="Script" path="res://game/world/water/water_surface.gd" id="4_water"]',
             f'[ext_resource type="Resource" path="res://game/levels/ch13/{zone}/{zone}_waves.tres" id="5_waves"]',
             f'[ext_resource type="Material" path="res://game/levels/ch13/{zone}/{zone}_water_material.tres" id="6_mat"]',
             '[ext_resource type="Script" path="res://game/levels/act1/zone_cast.gd" id="7_cast"]', "",
             f'[node name="{CLS[zone]}" type="Node3D"]', 'script = ExtResource("1_zone")', f'location_id = &"ch13/{zone}"',
             f'layout_path = "res://game/levels/ch13/{zone}/{zone}_layout.json"', "",
             '[node name="Cast" type="Node" parent="."]', 'script = ExtResource("7_cast")', "",
             '[node name="Water" type="Node3D" parent="."]',
             f"transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, {DATUM_Y}, 0)", 'script = ExtResource("4_water")',
             "publishes_water_level = true", 'wave_set = ExtResource("5_waves")', 'material = ExtResource("6_mat")', "",
             '[node name="Tide" type="Node" parent="." node_paths=PackedStringArray("water")]',
             'script = ExtResource("3_tide")', f"tide_line_y = {DATUM_Y}", f"water_height_y = {DATUM_Y}",
             'water = NodePath("../Water")', "",
             '[node name="Dressing" type="Node3D" parent="." node_paths=PackedStringArray("tide")]',
             'script = ExtResource("2_dressing")', f'layout_path = "res://game/levels/ch13/{zone}/{zone}_dressing.json"',
             'tide = NodePath("../Tide")', "", '[node name="Cameras" type="Node3D" parent="."]', ""]
    for name, pos, look, fov in CAMERAS[zone]:
        lines += [f'[node name="{name}" type="Camera3D" parent="Cameras"]', f"fov = {fov}", "near = 0.1", "far = 2500.0",
                  f"transform = {fen._look_xform(pos, look)}", ""]
    out = PREVIEW / f"{zone}_dressed.tscn"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    return out


def _write_interior_preview(zone: str) -> Path:
    """An interior zone's preview: no lagoon, so no Water or Tide (the basin's water is the dressing's `waters`)."""
    lines = ["[gd_scene format=3]", "",
             '[ext_resource type="Script" path="res://game/levels/ch13/ch13_zone.gd" id="1_zone"]',
             '[ext_resource type="Script" path="res://game/levels/act1/zone_kit_dressing.gd" id="2_dressing"]',
             '[ext_resource type="Script" path="res://game/levels/act1/zone_cast.gd" id="7_cast"]', "",
             f'[node name="{CLS[zone]}" type="Node3D"]', 'script = ExtResource("1_zone")', f'location_id = &"ch13/{zone}"',
             f'layout_path = "res://game/levels/ch13/{zone}/{zone}_layout.json"', "",
             '[node name="Cast" type="Node" parent="."]', 'script = ExtResource("7_cast")', "",
             '[node name="Dressing" type="Node3D" parent="."]', 'script = ExtResource("2_dressing")',
             f'layout_path = "res://game/levels/ch13/{zone}/{zone}_dressing.json"', "",
             '[node name="Cameras" type="Node3D" parent="."]', ""]
    for name, pos, look, fov in CAMERAS[zone]:
        lines += [f'[node name="{name}" type="Camera3D" parent="Cameras"]', f"fov = {fov}", "near = 0.1", "far = 500.0",
                  f"transform = {fen._look_xform(pos, look)}", ""]
    out = PREVIEW / f"{zone}_dressed.tscn"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    return out


def main() -> int:
    for zone in ZONE_NAMES:
        out = ZONES / zone
        ar.write_environment(dict(CH13), out / f"{zone}_environment.tres")
        if zone != "lamp_archive":  # the lagoon's mirror, and the Sanctum basin's
            write_water(zone)
        lay = layout(zone)
        (out / f"{zone}_dressing.json").write_text(json.dumps(lay, indent=1) + "\n", encoding="utf-8")
        write_preview(zone)
        print(f"DRESSING {zone}: {len(lay['pieces'])} pieces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
