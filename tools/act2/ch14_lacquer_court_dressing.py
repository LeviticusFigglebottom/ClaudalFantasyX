#!/usr/bin/env python3
"""The Lacquer Court at the wedding: dressing, lights and the ch14 grade (M4-A2P-044; env-art-b).

    python3 tools/act2/ch14_lacquer_court_dressing.py

The spec is docs/kb/plan/act2/zones/ch14_lacquer_court.md. Dressed in the greybox's own frame (chapters' M4-C14-02
layout, `ansedra_lacquer_court`): the court's floor, galleries, dais, water-steps and barge deck are the greybox's,
so it keeps the collision and every mark cinematics uses stays where it is (the spec's relayout isn't needed). The
greybox's columns aren't solid; the kit's columns bring their own colliders.

The light is the dusk (`lut_ch14_wedding`, the game's peak contrast) and the ceremony's lamp-stands, each light on its
stand. The lagoon is Ansedra's still mirror at y -1.0 (the ripples are M4-A2P-047's second half).

Writes, under game/levels/ch13/ansedra_lacquer_court/: ansedra_lacquer_court_dressing.json and
court_environment.tres; reuses Ansedra's looks and water; adds the Water, Tide and Dressing nodes to the scene (once).
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parent / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ans = _load("ch13_ansedra_dressing")

ZONE = ROOT / "game" / "levels" / "ch13" / "ansedra_lacquer_court"
RES_ZONE = "res://game/levels/ch13/ansedra_lacquer_court/"
LAYOUT = ZONE / "ansedra_lacquer_court_layout.json"
SCENE = ZONE / "ansedra_lacquer_court.tscn"

BESPOKE = ("court_ground", "court_balustrades", "court_water_steps", "court_colonnade_roofs", "court_water_gate")
WATER_Y = -1.0
BARGE = ("bridal_barge_wedding", 0.65, -0.6, 90.0)  # piece, scale, deck y (the greybox Barge's top), yaw
PURSUIT = ((-26.0, 12.0), WATER_Y, 90.0)  # moored off the court until the trap
HALL_SCALE = 1.25
HALLS = (((0.0, -26.0), 0.0), ((-17.0, -12.0), 90.0), ((17.0, -14.0), -90.0))  # fronts 2 m behind the edge walls
LAMP_STANDS = [(-3.4, 0.8, -20.0), (3.4, 0.8, -20.0)] + [(sx * 10.7, 0.6, z) for sx in (-1.0, 1.0)
                                                          for z in (-18.0, -12.0, -6.0)]
LAMP_COLOR = "#FFB16E"
LAMP_ENERGY = 1.4
LAMP_RANGE_M = 7.0
FLAME_Y = 1.75  # ansedra.FLAME_Y: the flame over the stand's foot
RACK = (-9.0, -23.4, 0.0)
DOMES = ((-45.0, 35.0, 1.0, 0.0), (40.0, 45.0, 0.9, 30.0), (-70.0, -10.0, 1.1, 10.0), (75.0, 5.0, 0.8, 50.0),
         (10.0, 75.0, 1.2, 20.0), (-30.0, -70.0, 1.0, 0.0), (45.0, -62.0, 0.9, 0.0))
LAGOON_CENTRE = (0.0, -10.0)

ENV_NAME = "court_environment.tres"
LUT_RES = "res://assets/environments/arenas/ansedra_lagoon_escape/lut_ch14_wedding.png"
SKY = dict(ans.SKY, col_zenith="Color(0.1804, 0.2039, 0.2824, 1)", col_horizon_sun="Color(0.7216, 0.3529, 0.2275, 1)",
           col_horizon_away="Color(0.2902, 0.2275, 0.2824, 1)", col_ground="Color(0.1608, 0.1412, 0.1569, 1)",
           sky_energy="1.0", col_glow="Color(1, 0.6667, 0.3725, 1)", glow_energy="0.9", glow_power="3.0",
           halo_energy="0.6", halo_power="20.0", sun_disc_energy="2.0", cloud_coverage="0.45",
           col_cloud_lit="Color(0.85, 0.45, 0.3, 1)", col_cloud_shadow="Color(0.22, 0.2, 0.26, 1)")
FOG = {"color": "Color(0.2902, 0.2275, 0.2275, 1)", "density": 0.004, "aerial": 0.5, "sky_affect": 0.3}
EXPOSURE = 1.15  # the spec says 0.90; under the layout's fill (#2e3448 0.5) the court floor went black at 0.9


def blocks() -> dict:
    g = json.loads(LAYOUT.read_text(encoding="utf-8"))
    return {b["id"]: b for b in g["blocks"]}


def _row(piece: str, x: float, z: float, y: float = 0.0, yaw: float = 0.0, **extra) -> dict:
    return {"piece": piece, "at": [x, z], "y": y, "yaw_deg": yaw, **extra}


def dressing() -> dict:
    b = blocks()
    pieces = [_row(p, 0.0, 0.0) for p in BESPOKE]
    pieces += [_row("court_column", v["pos"][0], v["pos"][2], collide=True)
               for k, v in sorted(b.items()) if k.startswith("Column")]
    pieces += [_row("court_gallery", b[k]["pos"][0], b[k]["pos"][2]) for k in ("GalleryW", "GalleryE")]
    pieces.append(_row("wedding_dais", b["Dais"]["pos"][0], b["Dais"]["pos"][2]))
    pieces.append(_row("conclave_gallery", b["ConclaveGallery"]["pos"][0], b["ConclaveGallery"]["pos"][2]))
    pieces += [_row("lacquer_hall", x, z, yaw=yaw, scale=HALL_SCALE) for (x, z), yaw in HALLS]
    pieces += [_row("gilt_lamp_stand", x, z, y=y) for x, y, z in LAMP_STANDS]
    pieces.append(_row("stillguard_rack", RACK[0], RACK[1], yaw=RACK[2]))
    piece, scale, deck_y, yaw = BARGE
    pieces.append(_row(piece, b["Barge"]["pos"][0], b["Barge"]["pos"][2], y=deck_y, yaw=yaw, scale=scale, block="Barge"))
    pieces.append(_row("pursuit_barge", PURSUIT[0][0], PURSUIT[0][1], y=PURSUIT[1], yaw=PURSUIT[2]))
    pieces += [_row("bowl_dome", x, z, y=WATER_Y, yaw=yaw, scale=s) for x, z, s, yaw in DOMES]
    pieces.append(_row("ansedra_far_domes_lit", LAGOON_CENTRE[0], LAGOON_CENTRE[1], y=WATER_Y))
    looks = {slot: ans.RES_ZONE + name for slot, (name, _) in ans.LOOKS.items()}
    looks["kit_order_marble"] = ans.RES_ZONE + ans.MARBLE_NAME
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/act2/ch14_lacquer_court_dressing.py from env-art's Haluna kit (ansedra.py's "
        "court pieces, M4-A2P-044); do not edit by hand. The greybox's frame.",
        "seed": 14,
        "kit_dir": ans.KIT,
        "materials_dir": ans.KIT_MATERIALS,
        "lod1_from_m": 120.0,
        "lod_end_m": 4000.0,
        "lod_margin_m": 2.0,
        "environment": RES_ZONE + ENV_NAME,
        "time_of_day_h": 18.5,
        "greybox": {"hide_all": True, "keep": []},
        "fire_light_color": LAMP_COLOR,
        "fire_lights": [{"at": [x, round(y + FLAME_Y + 0.1, 3), z], "energy": LAMP_ENERGY, "range": LAMP_RANGE_M}
                        for x, y, z in LAMP_STANDS],
        "kit_material_paths": looks,
        "pieces": pieces,
    }


def environment() -> str:
    sky = "\n".join(f"shader_parameter/{k} = {v}" for k, v in SKY.items())
    return f"""[gd_resource type="Environment" load_steps=5 format=3]

[ext_resource type="Shader" path="{ans.SKY_SHADER}" id="1_sky"]
[ext_resource type="Texture3D" path="{LUT_RES}" id="2_lut"]

[sub_resource type="ShaderMaterial" id="SkyMat"]
shader = ExtResource("1_sky")
{sky}

[sub_resource type="Sky" id="Sky"]
sky_material = SubResource("SkyMat")
process_mode = 2

[resource]
resource_name = "lacquer_court_ch14"
background_mode = 2
sky = SubResource("Sky")
ambient_light_source = 2
ambient_light_color = Color(0.2902, 0.3529, 0.4706, 1)
ambient_light_energy = 0.4
reflected_light_source = 2
tonemap_mode = 4
tonemap_exposure = {EXPOSURE}
tonemap_agx_white = 12.0
ssr_enabled = true
ssr_max_steps = 64
ssr_fade_in = 0.15
ssr_fade_out = 2.0
ssao_enabled = true
ssao_radius = 1.4
ssao_intensity = 1.4
glow_enabled = true
glow_intensity = 0.5
glow_bloom = 0.03
glow_hdr_threshold = 1.0
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
    f'[ext_resource type="Resource" path="{ans.RES_ZONE}{ans.WAVES_NAME}" id="5_waves"]\n'
    f'[ext_resource type="Material" path="{ans.RES_ZONE}{ans.WATER_NAME}" id="6_sea"]\n')
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
layout_path = "{RES_ZONE}ansedra_lacquer_court_dressing.json"
tide = NodePath("../Tide")

"""


def wire_scene() -> None:
    text = SCENE.read_text(encoding="utf-8")
    if 'id="2_dressing"' in text:
        return
    anchor = '[ext_resource type="Script" path="res://game/levels/act1/zone_cast.gd" id="90_cast"]\n'
    cast = '[node name="Cast" type="Node" parent="."]'
    assert text.count(anchor) == 1 and text.count(cast) == 1
    SCENE.write_text(text.replace(anchor, SCENE_RES + anchor).replace(cast, SCENE_NODES + cast), encoding="utf-8")


def main() -> None:
    (ZONE / "ansedra_lacquer_court_dressing.json").write_text(json.dumps(dressing(), indent=1) + "\n", encoding="utf-8")
    (ZONE / ENV_NAME).write_text(environment(), encoding="utf-8")
    wire_scene()


if __name__ == "__main__":
    main()
