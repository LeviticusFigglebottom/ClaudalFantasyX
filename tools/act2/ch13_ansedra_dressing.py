#!/usr/bin/env python3
"""Ansedra's dressing, looks, still water and grade (M4-A2P-043, M4-A2P-047; env-art-b).

    python3 tools/act2/ch13_ansedra_dressing.py

The spec is docs/kb/plan/act2/zones/ch13_ansedra.md. Ansedra is dressed in the greybox's own frame
(chapters' M4-C13-02 layout): its walk surfaces are flat at y 0 and already match the kit's, so the greybox keeps
the collision (its edge walls become the invisible island edges) and no story point moves.

Writes, under game/levels/ch13/ansedra/:
  ansedra_dressing.json          ZoneKitDressing: the island plinths and the mooring platform on their blocks, the
                                 causeways module by module, a gold lamp-post on every lamp block, the bowl-domes on
                                 the dome blocks and on their own islands round the walk, Sefir's and Corran's
                                 houses (lacquer halls), the mooring barges and the skyline ring.
  ansedra_*_material.tres        the zone looks for the kit's flat slots (gilt, red and black lacquer) and the
                                 marble cooled to the Order's white.
  ansedra_still_water_material.tres, ansedra_still_waves.tres
                                 the still mirror (M4-A2P-047): `overcast_lagoon` (absorption x1.5, deep #5E6E80)
                                 with no waves, no detail ripples and no foam, near-zero roughness and a long
                                 screen-space reflection, so the domes stand doubled in the lagoon.
  ansedra_environment.tres, lut_ch13_still.png
                                 the ch13 grade (16:30 overcast; colour script ch13).
and adds the Water, Tide and Dressing nodes to ansedra.tscn (once).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "act1"))
sys.path.insert(0, str(ROOT / "assets_src" / "environments" / "kits" / "haluna"))

import ch05_09_zone_looks as zl  # noqa: E402
import zone_lut  # noqa: E402

ZONE = ROOT / "game" / "levels" / "ch13" / "ansedra"
RES_ZONE = "res://game/levels/ch13/ansedra/"
LAYOUT = ZONE / "ansedra_layout.json"
SCENE = ZONE / "ansedra.tscn"
KIT = "res://assets/environments/kits/haluna/"
KIT_MATERIALS = KIT + "materials/"

# --- the walk ---------------------------------------------------------------------------------------------------
CAUSEWAY_MODULE_M = 6.0
# Each causeway between the island edges it joins: (axis, fixed coordinate, start, end, yaw_deg). The N and Sanctum
# gaps are 32 m, so their five modules are scaled 32/30 (the kerbs then stand at 2.13 m, over the greybox's rails at
# 2.0); the W and E gaps are 24 m, four modules at scale 1.
CAUSEWAYS = {
    "CausewayN": ("z", 0.0, 2.0, -30.0, 0.0),
    "CausewaySanctum": ("z", 0.0, -50.0, -82.0, 0.0),
    "CausewayW": ("x", -40.0, -10.0, -34.0, 90.0),
    "CausewayE": ("x", -40.0, 10.0, 34.0, 90.0),
}
# The islands' plinths, scaled from the 16 m piece to their blocks.
PLINTHS = {"Centre": 20.0, "CorranIsle": 16.0, "ArchiveIsle": 16.0, "SanctumIsle": 24.0}
PLINTH_M = 16.0
# The bowl-domes on the greybox's dome blocks, scaled so the dome's island (radius 6.84 m at 1) covers the block,
# which stays the collision.
DOME_RADIUS_M = 6.84
DOME_BLOCKS = {"SanctumIsleDome": 0.8, "ArchiveIsleDome": 0.53}
# The free-standing domes on their own islands, off the walk (the near skyline): x, z, scale, yaw.
NEAR_DOMES = (
    (-30.0, -8.0, 0.7, 15.0), (31.0, -12.0, 0.8, 40.0), (-24.0, -70.0, 0.75, 70.0), (26.0, -74.0, 0.9, 10.0),
    (-72.0, -62.0, 1.0, 50.0), (74.0, -70.0, 0.9, 25.0), (-40.0, -118.0, 1.1, 5.0), (42.0, -124.0, 0.85, 60.0),
    (-88.0, -18.0, 0.75, 35.0), (92.0, -28.0, 0.7, 80.0), (8.0, -150.0, 1.05, 20.0), (-64.0, 20.0, 0.8, 45.0),
    (66.0, 16.0, 0.75, 30.0),
)
# Sefir's house: one lacquer hall at 0.6 on its block, open to the south (the arrival from the north causeway).
# The hall's origin is its front centre; its depth runs to -Z (11.2 m at 1).
HALL_DEPTH_CENTRE_M = 4.0
SEFIR_HALL = ("SefirHouse", 0.6, 0.0)
# Corran's old house: a plainer hall (timber columns for the lacquer), facing the west causeway's end (+X).
CORRAN_HALL = ("CorranHouse", 0.45, 90.0)
CORRAN_SLOTS = {"kit_lacquer_red": KIT_MATERIALS + "kit_timber.tres"}
# The mooring barges: the bridal barge at 0.55 (its wedding dress: no bier before Ch15), poled along Z beside the moorings' water-steps (the steps reach 10.1 m
# out, so the hulls lie at 12.6 m, clear of them).
BARGES = (("BargeA", -12.6, 10.0, 90.0), ("BargeB", 12.6, 12.0, -90.0))
BARGE_SCALE = 0.55
LAGOON_CENTRE = (0.0, -45.0)

# --- the looks ----------------------------------------------------------------------------------------------------
# kit_gold_leaf: zl.GOLD cooled ~300 K (col_bronze #C9A85A), roughness 0.25, worn only at the edges. Never warm.
GOLD = dict(zl.GOLD, col_bronze=(0.7882, 0.6588, 0.3529), col_worn=(0.5098, 0.4118, 0.2471),
            roughness_bronze=0.25, patina_coverage=(0.0, 0.08), wear_strength=0.35)
LACQUER_RED = zl.lacquer((0.62, 0.14, 0.11))
LACQUER_BLACK = zl.lacquer((0.055, 0.05, 0.05), undercoat=(0.29, 0.07, 0.06))  # oxblood under the chips
LOOKS = {
    "kit_gold_leaf": ("ansedra_gold_leaf_material.tres", GOLD),
    "kit_lacquer_red": ("ansedra_lacquer_red_material.tres", LACQUER_RED),
    "kit_lacquer_black": ("ansedra_lacquer_black_material.tres", LACQUER_BLACK),
}
MARBLE_NAME = "ansedra_order_marble_material.tres"
MARBLE_OVERRIDES = {"col_paint": "Color(0.9098, 0.9098, 0.8863, 1)", "cavity_darken": "0.12"}

# --- the still mirror (M4-A2P-047) ----------------------------------------------------------------------------------
WATER_NAME = "ansedra_still_water_material.tres"
WAVES_NAME = "ansedra_still_waves.tres"
WATER_TEMPLATE = ROOT / "game" / "levels" / "ch05" / "pemakar" / "pemakar_sea_material.tres"
STILL_WATER = {  # overcast_lagoon (colour script: absorption x1.5, sigma 3 / 0.75 / 0.63) with Ansedra's deep; its
    # turquoise scatter is muted toward the deep slate (the lagoon is a grey mirror, airless)
    "col_deep": "Color(0.3686, 0.4314, 0.502, 1)", "col_scatter_shallow": "Color(0.3412, 0.4706, 0.502, 1)",
    "col_sss": "Color(0.4, 0.5098, 0.5373, 1)", "absorption_per_m": "Vector3(2.0, 0.5, 0.42)",
    "absorption_scale": "1.5", "caustic_strength": "0.0", "scatter_energy": "0.08",
}
STILL_ADDED = {  # the mirror: nothing moves the surface, and it reflects far
    "roughness_near": "0.0", "roughness_far": "0.02", "detail_strength": "0.0", "use_foam": "false",
    "use_caustics": "false", "ssr_max_distance_m": "400.0", "ssr_edge_fade": "0.04", "glint_strength": "0.0",
    "time_scale": "0.0", "refraction_strength": "0.0",
}

# --- the ch13 grade -------------------------------------------------------------------------------------------------
LUT_NAME = "lut_ch13_still.png"
LUT_CH13_STILL = {  # colour script ch13: overcast, S-curve 0.35, saturation x0.8, the gold kept cool
    "saturation": 0.8, "s_curve": 0.35, "toe_hex": "#3A4654", "toe_strength": 0.3, "toe_end": 0.34,
    "black_floor": 0.3, "highlight_hex": "#F2F2EE", "highlight_start": 0.72, "highlight_strength": 0.45,
    "warm_deg": (-20.0, 60.0), "warm_sat": 0.9, "cool_sat": 1.0, "cool_hex": "#D8DEE6", "cool_strength": 0.2,
}
ENV_NAME = "ansedra_environment.tres"
SKY = {  # #8A96A4 overhead to #C8C4BA at the horizon, a full grey overcast with a faint brighter patch at the sun
    "col_zenith": "Color(0.5412, 0.5882, 0.6431, 1)", "col_horizon_sun": "Color(0.8392, 0.8235, 0.7843, 1)",
    "col_horizon_away": "Color(0.7843, 0.7686, 0.7294, 1)", "col_ground": "Color(0.4392, 0.4510, 0.4627, 1)",
    "sky_energy": "1.3", "horizon_curve": "0.5", "azimuth_power": "1.0", "col_band": "Color(0.8, 0.79, 0.76, 1)",
    "band_energy": "0.15", "band_height": "0.1", "mid_strength": "0.0", "col_glow": "Color(0.96, 0.95, 0.92, 1)",
    "glow_energy": "0.25", "glow_power": "2.0", "halo_energy": "0.15", "halo_power": "8.0", "sun_disc_energy": "0.0",
    "col_cloud_lit": "Color(0.86, 0.85, 0.82, 1)", "col_cloud_shadow": "Color(0.52, 0.55, 0.59, 1)",
    "cloud_coverage": "0.9", "cloud_softness": "0.6", "cloud_opacity": "0.85", "cloud_height_m": "1400.0",
    "cloud_scale_m": "5000.0", "cloud_stretch": "Vector2(1, 1.6)", "cloud_wind_deg": "250.0",
    "cloud_sun_energy": "0.6", "cloud_ambient_energy": "1.2", "cloud_horizon_fade": "0.15",
}
SKY_SHADER = "res://game/shaders/environment/env_sky_low_sun.gdshader"
FOG = {"color": "Color(0.7216, 0.7216, 0.698, 1)", "density": 0.0035, "aerial": 0.6, "sky_affect": 0.35}
EXPOSURE = 0.75


def r3(v: float) -> float:
    return round(float(v), 3)


def blocks() -> dict:
    g = json.loads(LAYOUT.read_text(encoding="utf-8"))
    return {b["id"]: b for b in g["blocks"]}


def causeway_rows() -> list[dict]:
    rows = []
    for bid, (axis, fixed, start, end, yaw) in CAUSEWAYS.items():
        length = abs(end - start)
        n = round(length / CAUSEWAY_MODULE_M)
        scale = length / (n * CAUSEWAY_MODULE_M)
        step = (end - start) / n
        for k in range(n):
            c = start + step * (k + 0.5)
            at = [fixed, c] if axis == "z" else [c, fixed]
            row = {"piece": "ansedra_causeway_6m", "at": [r3(at[0]), r3(at[1])], "y": 0.0, "yaw_deg": yaw}
            if abs(scale - 1.0) > 1e-6:
                row["scale"] = r3(scale)
            rows.append(row)
    return rows


def lamp_rows(b: dict) -> list[dict]:
    return [{"piece": "gold_lamp_post", "at": [r3(v["pos"][0]), r3(v["pos"][2])], "y": 0.0, "yaw_deg": 0.0}
            for k, v in sorted(b.items()) if k.startswith("Causeway") and "Lamp" in k]


def island_rows(b: dict) -> list[dict]:
    rows = [{"piece": "mooring_platform", "at": [b["Moorings"]["pos"][0], b["Moorings"]["pos"][2]], "y": 0.0,
             "yaw_deg": 0.0}]
    for bid, size in PLINTHS.items():
        rows.append({"piece": "island_plinth_16m", "at": [b[bid]["pos"][0], b[bid]["pos"][2]], "y": 0.0,
                     "yaw_deg": 0.0, **({"scale": r3(size / PLINTH_M)} if size != PLINTH_M else {})})
    return rows


def dome_rows(b: dict) -> list[dict]:
    rows = [{"piece": "bowl_dome", "at": [b[bid]["pos"][0], b[bid]["pos"][2]], "y": 0.0, "yaw_deg": 0.0,
             "scale": s} for bid, s in DOME_BLOCKS.items()]
    rows += [{"piece": "bowl_dome", "at": [x, z], "y": 0.0, "yaw_deg": yaw, "scale": s} for x, z, s, yaw in NEAR_DOMES]
    rows.append({"piece": "ansedra_far_domes", "at": list(LAGOON_CENTRE), "y": 0.0, "yaw_deg": 0.0})
    return rows


def hall_row(b: dict, spec: tuple) -> dict:
    bid, scale, yaw = spec
    x, _, z = b[bid]["pos"]
    back = HALL_DEPTH_CENTRE_M * scale  # the origin is the hall's front: the block's centre lies `back` behind it
    if yaw == 0.0:
        at = [x, z + back]
    else:  # facing +X: its depth runs to -X
        at = [x + back, z]
    return {"piece": "lacquer_hall", "at": [r3(at[0]), r3(at[1])], "y": 0.0, "yaw_deg": yaw, "scale": scale}


def dressing() -> dict:
    b = blocks()
    for bid in ("SefirHouse", "CorranHouse", "ArchiveIsleDome", "SanctumIsleDome", "Moorings"):
        assert bid in b, bid
    pieces = island_rows(b) + causeway_rows() + lamp_rows(b) + dome_rows(b)
    pieces.append(hall_row(b, SEFIR_HALL))
    pieces.append(dict(hall_row(b, CORRAN_HALL), material_paths=dict(CORRAN_SLOTS)))
    for bid, x, z, yaw in BARGES:
        pieces.append({"piece": "bridal_barge_wedding", "at": [x, z], "y": 0.0, "yaw_deg": yaw, "scale": BARGE_SCALE,
                       "block": bid})
    looks = {slot: RES_ZONE + name for slot, (name, _) in LOOKS.items()}
    looks["kit_order_marble"] = RES_ZONE + MARBLE_NAME
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/act2/ch13_ansedra_dressing.py from env-art's Haluna kit (ansedra.py, M3-ENV-721, "
        "and its M4-A2P-043 pieces); do not edit by hand. The greybox's frame.",
        "seed": 13,
        "kit_dir": KIT,
        "materials_dir": KIT_MATERIALS,
        "lod1_from_m": 120.0,
        "lod_end_m": 4000.0,
        "lod_margin_m": 2.0,
        "environment": RES_ZONE + ENV_NAME,
        "time_of_day_h": 16.5,
        "greybox": {"hide_all": True, "keep": []},
        "kit_material_paths": looks,
        "pieces": pieces,
    }


def still_water() -> str:
    text = WATER_TEMPLATE.read_text(encoding="utf-8").replace('resource_name = "pemakar_sea"',
                                                              'resource_name = "ansedra_still_water"')
    lines = text.rstrip("\n").split("\n")
    for key, value in STILL_WATER.items():
        idx = [i for i, ln in enumerate(lines) if ln.startswith(f"shader_parameter/{key} = ")]
        assert len(idx) == 1, key
        lines[idx[0]] = f"shader_parameter/{key} = {value}"
    for key, value in STILL_ADDED.items():
        assert not any(ln.startswith(f"shader_parameter/{key} = ") for ln in lines), key
        lines.append(f"shader_parameter/{key} = {value}")
    return "\n".join(lines) + "\n"


def still_waves() -> str:
    return "\n".join([
        '[gd_resource type="Resource" script_class="WaveSet" load_steps=3 format=3]', "",
        '[ext_resource type="Script" path="res://game/world/water/wave_set.gd" id="1_set"]',
        '[ext_resource type="Script" path="res://game/world/water/wave_component.gd" id="2_comp"]', "",
        '[sub_resource type="Resource" id="Wave_0"]', 'script = ExtResource("2_comp")', "direction_deg = 0.0",
        "wavelength_m = 40.0", "amplitude_m = 0.0", "steepness = 0.0", "phase_rad = 0.0", "",
        "[resource]", 'script = ExtResource("1_set")', 'components = Array[ExtResource("2_comp")]([SubResource("Wave_0")])',
        "amplitude_scale = 0.0", ""])


def environment() -> str:
    sky = "\n".join(f"shader_parameter/{k} = {v}" for k, v in SKY.items())
    return f"""[gd_resource type="Environment" load_steps=5 format=3]

[ext_resource type="Shader" path="{SKY_SHADER}" id="1_sky"]
[ext_resource type="Texture3D" path="{RES_ZONE}{LUT_NAME}" id="2_lut"]

[sub_resource type="ShaderMaterial" id="SkyMat"]
shader = ExtResource("1_sky")
{sky}

[sub_resource type="Sky" id="Sky"]
sky_material = SubResource("SkyMat")
process_mode = 2

[resource]
resource_name = "ansedra_ch13"
background_mode = 2
sky = SubResource("Sky")
ambient_light_source = 2
ambient_light_color = Color(0.5412, 0.5882, 0.6431, 1)
ambient_light_energy = 0.6
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
glow_intensity = 0.25
glow_bloom = 0.02
glow_hdr_threshold = 1.2
fog_enabled = true
fog_light_color = {FOG["color"]}
fog_density = {FOG["density"]}
fog_aerial_perspective = {FOG["aerial"]}
fog_sky_affect = {FOG["sky_affect"]}
adjustment_enabled = true
adjustment_color_correction = ExtResource("2_lut")
"""


LUT_IMPORT = """[remap]

importer="3d_texture"
type="CompressedTexture3D"

[deps]

source_file="{res}"

[params]

compress/mode=0
compress/high_quality=false
compress/lossy_quality=0.7
compress/uastc_level=0
compress/rdo_quality_loss=0.0
compress/hdr_compression=1
compress/channel_pack=0
mipmaps/generate=false
mipmaps/limit=-1
slices/horizontal=32
slices/vertical=1
"""


def write_lut() -> None:
    import numpy as np  # noqa: PLC0415

    zone_lut.GRADES["ch13_still"] = dict(LUT_CH13_STILL)
    table = zone_lut.table(False, "ch13_still")
    zone_lut.write_png(ZONE / LUT_NAME, table)
    imp = ZONE / (LUT_NAME + ".import")
    if not imp.exists():  # Godot fills in the uid and the imported path; the slices are what matter
        imp.write_text(LUT_IMPORT.format(res=RES_ZONE + LUT_NAME), encoding="utf-8")
    del np


SCENE_RES = (
    '[ext_resource type="Script" path="res://game/levels/act1/zone_kit_dressing.gd" id="2_dressing"]\n'
    '[ext_resource type="Script" path="res://game/levels/ch02/haluna/weathering_tide.gd" id="3_tide"]\n'
    '[ext_resource type="Script" path="res://game/world/water/water_surface.gd" id="4_water"]\n'
    f'[ext_resource type="Resource" path="{RES_ZONE}{WAVES_NAME}" id="5_waves"]\n'
    f'[ext_resource type="Material" path="{RES_ZONE}{WATER_NAME}" id="6_sea"]\n')
SCENE_NODES = f"""[node name="Water" type="Node3D" parent="."]
script = ExtResource("4_water")
publishes_water_level = true
wave_set = ExtResource("5_waves")
material = ExtResource("6_sea")

[node name="Tide" type="Node" parent="." node_paths=PackedStringArray("water")]
script = ExtResource("3_tide")
water_height_y = 0.0
water = NodePath("../Water")

[node name="Dressing" type="Node3D" parent="." node_paths=PackedStringArray("tide")]
script = ExtResource("2_dressing")
layout_path = "{RES_ZONE}ansedra_dressing.json"
tide = NodePath("../Tide")

"""


RIPPLES_RES = '[ext_resource type="Script" path="res://game/world/water/ripple_field.gd" id="7_ripples"]\n'
RIPPLES_NODE = """[node name="Ripples" type="Node" parent="." node_paths=PackedStringArray("water")]
script = ExtResource("7_ripples")
water = NodePath("../Water")

"""


def wire_ripples() -> None:
    """The zone's RippleField on its water (M4-A2P-047: Ch14's first ripples), once."""
    text = SCENE.read_text(encoding="utf-8")
    if 'id="7_ripples"' in text:
        return
    anchor = '[ext_resource type="Script" path="res://game/levels/act1/zone_cast.gd" id="90_cast"]\n'
    cast = '[node name="Cast" type="Node" parent="."]'
    assert text.count(anchor) == 1 and text.count(cast) == 1
    SCENE.write_text(text.replace(anchor, RIPPLES_RES + anchor).replace(cast, RIPPLES_NODE + cast), encoding="utf-8")


def wire_scene() -> None:
    """The zone's Water, Tide and Dressing nodes (once), before its Cast."""
    text = SCENE.read_text(encoding="utf-8")
    if 'id="2_dressing"' in text:
        return
    anchor = '[ext_resource type="Script" path="res://game/levels/act1/zone_cast.gd" id="90_cast"]\n'
    cast = '[node name="Cast" type="Node" parent="."]'
    assert text.count(anchor) == 1 and text.count(cast) == 1
    text = text.replace(anchor, SCENE_RES + anchor).replace(cast, SCENE_NODES + cast)
    SCENE.write_text(text, encoding="utf-8")


def main() -> None:
    (ZONE / "ansedra_dressing.json").write_text(json.dumps(dressing(), indent=1) + "\n", encoding="utf-8")
    for name, params in LOOKS.values():
        (ZONE / name).write_text(zl.bronze_material(name.removesuffix(".tres"), params), encoding="utf-8")
    (ZONE / MARBLE_NAME).write_text(zl.copy_material(KIT_MATERIALS + "kit_order_marble.tres",
                                                     MARBLE_NAME.removesuffix(".tres"), MARBLE_OVERRIDES),
                                    encoding="utf-8")
    (ZONE / WATER_NAME).write_text(still_water(), encoding="utf-8")
    (ZONE / WAVES_NAME).write_text(still_waves(), encoding="utf-8")
    write_lut()
    (ZONE / ENV_NAME).write_text(environment(), encoding="utf-8")
    wire_scene()
    wire_ripples()


if __name__ == "__main__":
    main()
