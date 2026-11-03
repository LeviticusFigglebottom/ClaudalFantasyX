#!/usr/bin/env python3
"""The Drowned Choir at moonrise: dressing, the night water and the grade (M4-A2P-046; env-art-b).

    python3 tools/act2/ch16_drowned_choir_dressing.py

The spec is docs/kb/plan/act2/zones/ch16_drowned_choir.md. chapters relaid the greybox to the kit's shape (M4-A2P-106,
tools/act2/ch15_16_greybox.py): the dais (r 7.5, top y 0), the channel bed at -0.8 bridged north and south, six tiers to
2.15 m at r 21.5, the south gap at sea level and the fifteen `Mouth*` blocks at r 44. So the kit's walked amphitheatre (its aisles, gap, ramp and bridges cut to that layout) sits at
the greybox's origin in its own frame, the greybox keeps the collision (its tier blocks are the kit's tiers, with the
curbs and aisle walls as invisible bounds) and no mark moves. A colossal singer stands on every Mouth block at the
sand, turned to the dais (the gap at 8 is the approach's opening); the white flats run to the horizon; the water is
the colour script's `pale_rim` at night; the moon is the layout's, low in the east.

Writes, under game/levels/ch16/drowned_choir/: drowned_choir_dressing.json, drowned_choir_water_material.tres and
drowned_choir_environment.tres; adds the Water, Tide and Dressing nodes to the scene (once). The LUT is the arena's
`lut_ch16_choir` (assets/environments/arenas/drowned_choir_ring/, env-art's).
"""

from __future__ import annotations

import importlib.util
import json
import math
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
import drowned_choir as dc  # noqa: E402

ZONE = ROOT / "game" / "levels" / "ch16" / "drowned_choir"
RES_ZONE = "res://game/levels/ch16/drowned_choir/"
LAYOUT = ZONE / "drowned_choir_layout.json"
SCENE = ZONE / "drowned_choir.tscn"

WATER_Y = dc.WATER_Y  # the kit's sea over the channel (-0.25); the greybox's Water block lies just under it
FLATS_Y = 0.0  # the kit's flats are built in the Choir's frame, under its sea
# The channel is 0.55 m deep and the dais only 0.25 m over the sea: the lagoon's 10-13 cm swells would lap the flags,
# so the Choir's sea lies still as the Rim's does (Ansedra's zero-amplitude set), only its detail ripples moving.
WAVES_RES = "res://game/levels/ch13/ansedra/ansedra_still_waves.tres"
WATER_NAME = "drowned_choir_water_material.tres"
WATER = {"col_deep": "#2E4C50", "col_scatter_shallow": "#7FB8B4", "col_sss": "#7FB8B4", "absorption_scale": "0.8",
         "caustic_strength": "0.0"}  # the colour script's `pale_rim` look at night (the spec's "#2E4C50, sea-glow 0.1")
SEA_GLOW = 0.1
ENV_NAME = "drowned_choir_environment.tres"
LUT_RES = "res://assets/environments/arenas/drowned_choir_ring/lut_ch16_choir.png"
SKY_SHADER = "res://game/shaders/environment/env_sky_night.gdshader"
SKY = {"col_zenith": "Color(0.0549, 0.0863, 0.149, 1)", "col_horizon": "Color(0.2275, 0.2902, 0.3765, 1)",
       "col_ground": "Color(0.1804, 0.298, 0.3137, 1)", "col_moon": "Color(0.8235, 0.8745, 1, 1)",
       "moon_disc_energy": "10.0", "star_density": "0.1", "star_energy": "2.0"}
FOG = {"color": "Color(0.2275, 0.2902, 0.3529, 1)", "density": 0.003}
FILL = ("Color(0.1647, 0.2275, 0.3059, 1)", 0.25)  # the spec's fill #2A3A4E 0.25
EXPOSURE = 1.1
# The moon is the layout's (low in the east) and only 0.4: from the approach the singers' fronts face away from it.
# A cool rim from the moon's side and a faint sky fill from overhead, both shadowless, so the ceramic reads cold
# white against the night, not black (Act I's row-82 lesson).
FILLS = [
    {"pitch_deg": -10.0, "yaw_deg": 90.0, "color": "#B8C8E8", "energy": 0.3, "specular": 0.2},
    {"pitch_deg": -70.0, "yaw_deg": 0.0, "color": "#5A6E88", "energy": 0.25, "specular": 0.0},
]


def blocks() -> dict:
    g = json.loads(LAYOUT.read_text(encoding="utf-8"))
    return {b["id"]: b for b in g["blocks"]}


def _row(piece: str, x: float, z: float, y: float = 0.0, yaw: float = 0.0, **extra) -> dict:
    return {"piece": piece, "at": [x, z], "y": y, "yaw_deg": yaw, **extra}


def singer_yaw(x: float, z: float) -> float:
    """The singer's front (+Z) turned to the dais from (x, z)."""
    return round(math.degrees(math.atan2(-x, -z)), 3)


def dressing() -> dict:
    b = blocks()
    pieces = [_row("choir_amphitheatre_walked", 0.0, 0.0), _row("pale_rim_flats", 0.0, 0.0, FLATS_Y)]
    mouths = sorted((k, v) for k, v in b.items() if k.startswith("Mouth"))
    pieces += [_row("choir_singer", round(v["pos"][0], 3), round(v["pos"][2], 3), dc.SAND_Y,
                    singer_yaw(v["pos"][0], v["pos"][2])) for _k, v in mouths]
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/act2/ch16_drowned_choir_dressing.py from env-art's Haluna kit (drowned_choir.py); "
        "do not edit by hand. The greybox's frame (chapters' M4-A2P-106 relayout).",
        "seed": 1616,
        "kit_dir": ans.KIT,
        "materials_dir": ans.KIT_MATERIALS,
        "lod1_from_m": 120.0,
        "lod_end_m": 4000.0,
        "lod_margin_m": 2.0,
        "environment": RES_ZONE + ENV_NAME,
        "time_of_day_h": 21.0,
        "greybox": {"hide_all": True, "keep": []},
        "fill_lights": [dict(f) for f in FILLS],
        "pieces": pieces,
    }


def _hex(v: str) -> str:
    r, g, b_ = (int(v[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    return f"Color({r:.4f}, {g:.4f}, {b_:.4f}, 1)"


def water() -> str:
    text = ans.WATER_TEMPLATE.read_text(encoding="utf-8").replace('resource_name = "pemakar_sea"',
                                                                  'resource_name = "drowned_choir_water"')
    lines = text.rstrip("\n").split("\n")
    for key, value in WATER.items():
        idx = [i for i, ln in enumerate(lines) if ln.startswith(f"shader_parameter/{key} = ")]
        assert len(idx) == 1, key
        lines[idx[0]] = f"shader_parameter/{key} = {_hex(value) if value.startswith('#') else value}"
    return "\n".join(lines) + "\n"


def environment() -> str:
    sky = "\n".join(f"shader_parameter/{k} = {v}" for k, v in SKY.items())
    return f"""[gd_resource type="Environment" load_steps=5 format=3]

[ext_resource type="Shader" path="{SKY_SHADER}" id="1_sky"]
[ext_resource type="Texture3D" path="{LUT_RES}" id="2_lut"]

[sub_resource type="ShaderMaterial" id="SkyMat"]
shader = ExtResource("1_sky")
{sky}

[sub_resource type="Sky" id="Sky"]
sky_material = SubResource("SkyMat")
radiance_size = 1

[resource]
resource_name = "drowned_choir_ch16"
background_mode = 2
sky = SubResource("Sky")
ambient_light_source = 2
ambient_light_color = {FILL[0]}
ambient_light_energy = {FILL[1]}
reflected_light_source = 2
tonemap_mode = 4
tonemap_exposure = {EXPOSURE}
tonemap_agx_white = 12.0
ssr_enabled = true
ssr_max_steps = 48
ssr_fade_in = 0.2
ssr_fade_out = 2.0
ssao_enabled = true
ssao_radius = 1.2
ssao_intensity = 1.0
glow_enabled = true
glow_intensity = 0.5
glow_bloom = 0.06
glow_hdr_threshold = 1.0
fog_enabled = true
fog_light_color = {FOG["color"]}
fog_density = {FOG["density"]}
fog_sky_affect = 0.0
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
sea_glow_energy = {SEA_GLOW}
wave_set = ExtResource("5_waves")
material = ExtResource("6_sea")

[node name="Tide" type="Node" parent="." node_paths=PackedStringArray("water")]
script = ExtResource("3_tide")
water_height_y = {WATER_Y}
water = NodePath("../Water")

[node name="Dressing" type="Node3D" parent="." node_paths=PackedStringArray("tide")]
script = ExtResource("2_dressing")
layout_path = "{RES_ZONE}drowned_choir_dressing.json"
tide = NodePath("../Tide")

"""


def wire_scene() -> None:
    text = SCENE.read_text(encoding="utf-8")
    if 'id="2_dressing"' in text:
        return
    anchor = '[ext_resource type="Script" path="res://game/levels/act1/zone_cast.gd" id="90_cast"]\n'
    cast = '[node name="Cast" type="Node" parent="."]'
    assert text.count(anchor) == 1 and text.count(cast) == 1
    head = text.split("\n", 1)[0]
    if "load_steps=" in head:
        n = int(head.split("load_steps=")[1].split()[0])
        text = text.replace(head, head.replace(f"load_steps={n}", f"load_steps={n + 5}"), 1)
    SCENE.write_text(text.replace(anchor, SCENE_RES + anchor).replace(cast, SCENE_NODES + cast), encoding="utf-8")


def main() -> None:
    (ZONE / "drowned_choir_dressing.json").write_text(json.dumps(dressing(), indent=1) + "\n", encoding="utf-8")
    (ZONE / WATER_NAME).write_text(water(), encoding="utf-8")
    (ZONE / ENV_NAME).write_text(environment(), encoding="utf-8")
    wire_scene()


if __name__ == "__main__":
    main()
