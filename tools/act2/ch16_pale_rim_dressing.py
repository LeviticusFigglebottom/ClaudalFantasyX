#!/usr/bin/env python3
"""The Pale Rim's wade: dressing, the white water and the rim grade (M4-A2P-046; env-art-b).

    python3 tools/act2/ch16_pale_rim_dressing.py

The spec is docs/kb/plan/act2/zones/ch16_pale_rim.md. Dressed in the greybox's own frame (chapters' M4-C16-02
layout): its sand is the walk at y 0, so the greybox keeps the collision (the haze walls stay invisible bounds) and no
mark moves. The edge of the world goes white: a strip of white sand under ankle-deep water (`pale_rim_strand`), the
kit's flats out to the horizon, the line of cairns south (salt-crusted: a slot swap, not a new mesh), the Cantors'
marker poles, the Hollowmere ship at anchor. The game's lowest contrast.

Writes, under game/levels/ch16/pale_rim/: pale_rim_dressing.json, pale_rim_water_material.tres,
pale_rim_environment.tres, lut_ch16_rim.png and the cairns' slot looks; adds the Water, Tide and Dressing nodes (once).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parent / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ans = _load("ch13_ansedra_dressing")
zl, zone_lut = ans.zl, ans.zone_lut
import drowned_choir as dc  # noqa: E402

ZONE = ROOT / "game" / "levels" / "ch16" / "pale_rim"
RES_ZONE = "res://game/levels/ch16/pale_rim/"
LAYOUT = ZONE / "pale_rim_layout.json"
SCENE = ZONE / "pale_rim.tscn"

WATER_Y = 0.12  # the greybox's Shallows: ankle-deep over the sand
STRAND_AT = (90.0, 0.0)  # the walk's centre (the greybox Sand)
FLATS_Y = round(WATER_Y - dc.WATER_Y, 3)  # the kit's flats in their own frame under the zone's water
POLES = ((0.0, 12.0), (55.0, -12.0), (110.0, 12.0), (165.0, -12.0), (220.0, 12.0), (30.0, -22.0), (140.0, 22.0))
SHIP_YAW = 90.0  # hm_ship lies along X; the greybox Ship along Z
CAIRN_YAWS = (0.0, 40.0, 95.0, 150.0, 200.0, 260.0, 310.0, 20.0)
# The cairns' salt-crusted look (the spec: Haluna shrine stone desaturated, salt): Keth's slots swapped zone-wide
# (only the cairns use them here).
CAIRN_LOOKS = {
    "kit_keth_crag": ("rim_cairn_stone_material.tres", "kit_keth_crag.tres",
                      {"use_salt": "true", "col_tint": "Color(0.93, 0.92, 0.89, 1)"},
                      {"salt_coverage": "Vector2(0.0, 0.3)", "col_paint": "Color(0.9, 0.89, 0.85, 1)",
                       "paint_cover": "0.7"}),  # bleached: a salt-white crust over the dark stone
    "kit_keth_red": ("rim_cairn_cloth_material.tres", "kit_cloth_sand.tres", {}, {}),
    "kit_keth_wool": ("rim_cairn_wool_material.tres", "kit_cloth_sand.tres", {}, {}),
}

# The shallows are 12 cm deep: the lagoon's swells (10-13 cm) would bare the sand in their troughs, so the Rim's water
# lies still (Ansedra's zero-amplitude set), only its detail ripples moving.
WAVES_RES = "res://game/levels/ch13/ansedra/ansedra_still_waves.tres"
LAGOON_WAVES_RES = "res://game/world/water/lagoon_waves.tres"
WATER_NAME = "pale_rim_water_material.tres"
WATER = {"col_deep": "#5E8C90", "col_scatter_shallow": "#7FB8B8", "col_sss": "#BFE6E0", "absorption_scale": "0.8",
         "caustic_strength": "0.3"}  # the colour script's validated `pale_rim` look (water_looks.json)
ENV_NAME = "pale_rim_environment.tres"
LUT_NAME = "lut_ch16_rim.png"
LUT_RIM = {  # colour script ch16 (the Rim): white overcast noon, S-curve 0.25, saturation x0.7, nothing near black
    "saturation": 0.7, "s_curve": 0.25, "toe_hex": "#8A96A0", "toe_strength": 0.4, "toe_end": 0.4,
    "black_floor": 0.8, "highlight_hex": "#FFFFFF", "highlight_start": 0.75, "highlight_strength": 0.5,
}
SKY = dict(ans.SKY, col_zenith="Color(0.8471, 0.8706, 0.8941, 1)", col_horizon_sun="Color(0.949, 0.949, 0.9333, 1)",
           col_horizon_away="Color(0.949, 0.949, 0.9333, 1)", col_ground="Color(0.85, 0.87, 0.87, 1)",
           sky_energy="1.6", cloud_coverage="1.0", col_cloud_lit="Color(0.95, 0.95, 0.94, 1)",
           col_cloud_shadow="Color(0.82, 0.84, 0.86, 1)", glow_energy="0.1", halo_energy="0.05")
FOG = {"color": "Color(0.9098, 0.9255, 0.9255, 1)", "density": 0.012, "aerial": 1.0, "sky_affect": 0.85}
EXPOSURE = 0.7


def blocks() -> dict:
    g = json.loads(LAYOUT.read_text(encoding="utf-8"))
    return {b["id"]: b for b in g["blocks"]}


def _row(piece: str, x: float, z: float, y: float = 0.0, yaw: float = 0.0, **extra) -> dict:
    return {"piece": piece, "at": [x, z], "y": y, "yaw_deg": yaw, **extra}


def dressing() -> dict:
    b = blocks()
    pieces = [_row("pale_rim_strand", *STRAND_AT), _row("pale_rim_flats", STRAND_AT[0], STRAND_AT[1], FLATS_Y)]
    cairns = sorted((k, v) for k, v in b.items() if k.startswith("Cairn"))
    pieces += [_row("cairn", v["pos"][0], v["pos"][2], 0.0, CAIRN_YAWS[i % len(CAIRN_YAWS)])
               for i, (_k, v) in enumerate(cairns)]
    pieces += [_row("rim_marker_pole", x, z, 0.0, 37.0 * k) for k, (x, z) in enumerate(POLES)]
    pieces.append(_row("hm_ship", b["Ship"]["pos"][0], b["Ship"]["pos"][2], WATER_Y, SHIP_YAW))
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/act2/ch16_pale_rim_dressing.py from env-art's Haluna kit (drowned_choir.py and "
        "its M4-A2P-046 pieces; keth.py's cairn; hollowmere.py's ship); do not edit by hand. The greybox's frame.",
        "seed": 16,
        "kit_dir": ans.KIT,
        "materials_dir": ans.KIT_MATERIALS,
        "lod1_from_m": 120.0,
        "lod_end_m": 4000.0,
        "lod_margin_m": 2.0,
        "environment": RES_ZONE + ENV_NAME,
        "time_of_day_h": 12.0,
        "greybox": {"hide_all": True, "keep": []},
        "kit_material_paths": {slot: RES_ZONE + look[0] for slot, look in CAIRN_LOOKS.items()},
        "pieces": pieces,
    }


def _hex(v: str) -> str:
    r, g, b_ = (int(v[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    return f"Color({r:.4f}, {g:.4f}, {b_:.4f}, 1)"


def water() -> str:
    text = ans.WATER_TEMPLATE.read_text(encoding="utf-8").replace('resource_name = "pemakar_sea"',
                                                                  'resource_name = "pale_rim_water"')
    lines = text.rstrip("\n").split("\n")
    for key, value in WATER.items():
        idx = [i for i, ln in enumerate(lines) if ln.startswith(f"shader_parameter/{key} = ")]
        assert len(idx) == 1, key
        lines[idx[0]] = f"shader_parameter/{key} = {_hex(value) if value.startswith('#') else value}"
    return "\n".join(lines) + "\n"


def environment() -> str:
    sky = "\n".join(f"shader_parameter/{k} = {v}" for k, v in SKY.items())
    return f"""[gd_resource type="Environment" load_steps=5 format=3]

[ext_resource type="Shader" path="{ans.SKY_SHADER}" id="1_sky"]
[ext_resource type="Texture3D" path="{RES_ZONE}{LUT_NAME}" id="2_lut"]

[sub_resource type="ShaderMaterial" id="SkyMat"]
shader = ExtResource("1_sky")
{sky}

[sub_resource type="Sky" id="Sky"]
sky_material = SubResource("SkyMat")
process_mode = 2

[resource]
resource_name = "pale_rim_ch16"
background_mode = 2
sky = SubResource("Sky")
ambient_light_source = 2
ambient_light_color = Color(0.8471, 0.8706, 0.8941, 1)
ambient_light_energy = 0.9
reflected_light_source = 2
tonemap_mode = 4
tonemap_exposure = {EXPOSURE}
tonemap_agx_white = 12.0
ssr_enabled = true
ssr_max_steps = 48
ssao_enabled = true
ssao_radius = 1.0
ssao_intensity = 0.8
glow_enabled = true
glow_intensity = 0.3
glow_bloom = 0.04
glow_hdr_threshold = 1.2
fog_enabled = true
fog_light_color = {FOG["color"]}
fog_density = {FOG["density"]}
fog_aerial_perspective = {FOG["aerial"]}
fog_sky_affect = {FOG["sky_affect"]}
adjustment_enabled = true
adjustment_color_correction = ExtResource("2_lut")
"""


SCENE_RES = (
    '[ext_resource type="Script" path="res://game/levels/act1/zone_kit_dressing.gd" id="2_dressing"]\n'
    '[ext_resource type="Script" path="res://game/levels/ch02/haluna/weathering_tide.gd" id="3_tide"]\n'
    '[ext_resource type="Script" path="res://game/world/water/water_surface.gd" id="4_water"]\n'
    f'[ext_resource type="Resource" path="{WAVES_RES}" id="5_waves"]\n'
    f'[ext_resource type="Material" path="{RES_ZONE}{WATER_NAME}" id="6_sea"]\n')
SCENE_NODES = f"""[node name="Water" type="Node3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, {WATER_Y}, 0)
script = ExtResource("4_water")
publishes_water_level = true
wave_set = ExtResource("5_waves")
material = ExtResource("6_sea")

[node name="Tide" type="Node" parent="." node_paths=PackedStringArray("water")]
script = ExtResource("3_tide")
water_height_y = {WATER_Y}
water = NodePath("../Water")

[node name="Dressing" type="Node3D" parent="." node_paths=PackedStringArray("tide")]
script = ExtResource("2_dressing")
layout_path = "{RES_ZONE}pale_rim_dressing.json"
tide = NodePath("../Tide")

"""


def wire_scene() -> None:
    text = SCENE.read_text(encoding="utf-8")
    if 'id="2_dressing"' in text:
        if LAGOON_WAVES_RES in text:  # wired before the shallows were stilled
            SCENE.write_text(text.replace(LAGOON_WAVES_RES, WAVES_RES), encoding="utf-8")
        return
    anchor = '[ext_resource type="Script" path="res://game/levels/act1/zone_cast.gd" id="90_cast"]\n'
    cast = '[node name="Cast" type="Node" parent="."]'
    assert text.count(anchor) == 1 and text.count(cast) == 1
    SCENE.write_text(text.replace(anchor, SCENE_RES + anchor).replace(cast, SCENE_NODES + cast), encoding="utf-8")


def write_lut() -> None:
    zone_lut.GRADES["ch16_rim"] = dict(LUT_RIM)
    zone_lut.write_png(ZONE / LUT_NAME, zone_lut.table(False, "ch16_rim"))
    imp = ZONE / (LUT_NAME + ".import")
    if not imp.exists():
        imp.write_text(ans.LUT_IMPORT.format(res=RES_ZONE + LUT_NAME), encoding="utf-8")


def main() -> None:
    (ZONE / "pale_rim_dressing.json").write_text(json.dumps(dressing(), indent=1) + "\n", encoding="utf-8")
    for name, src, overrides, added in CAIRN_LOOKS.values():
        (ZONE / name).write_text(zl.copy_material(ans.KIT_MATERIALS + src, name.removesuffix(".tres"), overrides, added),
                                 encoding="utf-8")
    (ZONE / WATER_NAME).write_text(water(), encoding="utf-8")
    write_lut()
    (ZONE / ENV_NAME).write_text(environment(), encoding="utf-8")
    wire_scene()


if __name__ == "__main__":
    main()
