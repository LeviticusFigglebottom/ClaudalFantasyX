#!/usr/bin/env python3
"""Hollowmere's first visit, Ch15's dawn: dressing, lamps and the dawn grade (M4-A2P-045; env-art-b).

    python3 tools/act2/ch15_hollowmere_dressing.py

The spec is docs/kb/plan/act2/zones/ch15_hollowmere.md. Dressed in the greybox's own frame (chapters' M4-C15-02
layout, `ch17/hollowmere`): the dock, the jetties and the house platforms are its walk at y 0, so the greybox keeps the
collision and no mark moves. The lagoon stands 0.9 m under the walk (the lashed hulls' deck height), so the homes'
hulls sit at their own waterline and the dock floats on its pontoons.

Dawn (05:40): no sun yet, fog going grey-rose, the first oil lamps warm on the hulls (each light at its lamp's flame),
the signal lamps teal. Act III's dusk grade (ch17) is the same zone later; its variant is Act III's to add.

Writes, under game/levels/ch17/hollowmere/: hollowmere_dressing.json, hollowmere_dawn_environment.tres,
lut_ch15_hollowmere_dawn.png, hollowmere_dawn_water_material.tres; adds the Water, Tide and Dressing nodes to the scene
(once).
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
zl, zone_lut = ans.zl, ans.zone_lut

ZONE = ROOT / "game" / "levels" / "ch17" / "hollowmere"
RES_ZONE = "res://game/levels/ch17/hollowmere/"
LAYOUT = ZONE / "hollowmere_layout.json"
SCENE = ZONE / "hollowmere.tscn"
KIT = ans.KIT

WATER_Y = -0.9  # hollowmere.DECK_Y under the walk
DOCK_MODULE_M = 4.0
RAIL_COVER = 0.5  # a dock module keeps its rail on a side the greybox's rails cover at least this much
JETTY_MODULES = 3
JETTY_SPAN = (-1.8, -15.0)  # from the dock's north edge to the house platform's south edge
HOUSE_YAW = 180.0  # the deckhouse on the platform's north half, its door to the jetty
HOMES = ((4.0, -33.0, 15.0), (20.0, -35.0, -10.0), (36.0, -33.0, 5.0), (52.0, -31.0, 20.0), (60.0, -18.0, 80.0),
         (12.0, -47.0, 0.0), (30.0, -49.0, 30.0), (48.0, -46.0, -20.0), (68.0, -34.0, 10.0), (-8.0, -20.0, 70.0))
WINDMILLS = ((-12.0, -40.0, 30.0), (76.0, -10.0, -60.0), (70.0, -55.0, 10.0), (22.0, -62.0, 180.0), (55.0, 15.0, 200.0))
TIDE_WHEELS = ((4.0, -27.5, 0.0), (20.0, -27.5, 0.0), (36.0, -27.5, 0.0))
SIGNAL_LAMPS = ((7.6, -15.6), (23.6, -15.6), (48.4, -15.6), (-1.0, -1.6))
SIGNAL_COLOR = "#4FB3B0"
OIL_LAMPS = ((12.0, -17.4, 0.0), (28.0, -17.4, 0.0), (44.0, -17.4, 0.0), (16.0, 1.85, 180.0), (40.5, -1.85, 0.0),
             (58.0, 1.85, 180.0))  # x, z, yaw: by the three doors, and on the dock's rails
OIL_COLOR = "#FFB16E"
OIL_ENERGY = 0.9
OIL_RANGE_M = 5.0
LAMP_FLAME = (0.0, 1.55, 0.45)  # hollowmere.LAMP_FLAME
SUPPER_AT = (42.0, 0.95, 0.0)  # by the father's place, against the south rail: the walk from the supper mark to the
#   pyre-raft runs along the north half (z -0.8 to 0), so the table's box (stools at +-0.87 m) stays 0.4 m clear of a body
DACE_AT = (78.0, -24.0, 30.0)  # seen at the zone's edge in Ch15 (Ch17's heart)
FLOTILLA_AT = (25.0, -5.0)

WATER_NAME = "hollowmere_dawn_water_material.tres"
WATER = {"col_deep": "Color(0.1098, 0.2275, 0.2902, 1)", "col_scatter_shallow": "Color(0.3529, 0.5098, 0.5294, 1)",
         "col_sss": "Color(0.3922, 0.5490, 0.5686, 1)", "scatter_energy": "0.1", "caustic_strength": "0.0"}
ENV_NAME = "hollowmere_dawn_environment.tres"
LUT_NAME = "lut_ch15_hollowmere_dawn.png"
LUT_DAWN = {  # colour script ch15 at Hollowmere: grey-rose dawn, the oil lamps' warmth kept, the rest cool and soft
    "saturation": 0.85, "s_curve": 0.35, "toe_hex": "#1C3A4A", "toe_strength": 0.35, "toe_end": 0.34,
    "black_floor": 0.4, "highlight_hex": "#F0D8D0", "highlight_start": 0.7, "highlight_strength": 0.45,
    "warm_deg": (-20.0, 60.0), "warm_sat": 1.1, "cool_sat": 0.9, "cool_hex": "#C8D0D8", "cool_strength": 0.25,
}
SKY = dict(ans.SKY, col_zenith="Color(0.2902, 0.3529, 0.4157, 1)", col_horizon_sun="Color(0.7843, 0.6039, 0.6039, 1)",
           col_horizon_away="Color(0.4157, 0.4784, 0.5255, 1)", col_ground="Color(0.1098, 0.2275, 0.2902, 1)",
           sky_energy="1.0", col_glow="Color(0.94, 0.76, 0.74, 1)", glow_energy="0.4", cloud_coverage="0.8",
           col_cloud_lit="Color(0.8, 0.66, 0.66, 1)", col_cloud_shadow="Color(0.3, 0.36, 0.42, 1)")
FOG = {"color": "Color(0.4784, 0.4706, 0.5098, 1)", "density": 0.018, "aerial": 0.8, "sky_affect": 0.6}
EXPOSURE = 0.9


def r3(v: float) -> float:
    return round(float(v), 3)


def blocks() -> dict:
    g = json.loads(LAYOUT.read_text(encoding="utf-8"))
    return {b["id"]: b for b in g["blocks"]}


def _intervals(b: dict, prefix: str) -> list[tuple[float, float]]:
    out = []
    for k, v in b.items():
        if k.startswith(prefix):
            out.append((v["pos"][0] - v["size"][0] * 0.5, v["pos"][0] + v["size"][0] * 0.5))
    return out


def _covered(lo: float, hi: float, spans: list[tuple[float, float]]) -> float:
    return sum(max(0.0, min(hi, b) - max(lo, a)) for a, b in spans) / (hi - lo)


def dock_rows(b: dict) -> list[dict]:
    d = b["Dock"]
    x0, x1 = d["pos"][0] - d["size"][0] * 0.5, d["pos"][0] + d["size"][0] * 0.5
    n = round((x1 - x0) / DOCK_MODULE_M)
    step = (x1 - x0) / n
    north, south = _intervals(b, "DockRailN"), _intervals(b, "DockRailS")
    rows = []
    for k in range(n):
        lo, hi = x0 + step * k, x0 + step * (k + 1)
        has_n, has_s = _covered(lo, hi, north) >= RAIL_COVER, _covered(lo, hi, south) >= RAIL_COVER
        piece = {(True, True): "hm_dock_4m", (False, True): "hm_dock_4m_open_n", (True, False): "hm_dock_4m_open_s",
                 (False, False): "hm_dock_4m_open_ns"}[(has_n, has_s)]
        rows.append({"piece": piece, "at": [r3((lo + hi) * 0.5), d["pos"][2]], "y": 0.0, "yaw_deg": 0.0,
                     "scale": r3(step / DOCK_MODULE_M)})
    return rows


def jetty_rows(b: dict) -> list[dict]:
    rows = []
    z0, z1 = JETTY_SPAN
    step = (z1 - z0) / JETTY_MODULES
    for k, v in sorted(b.items()):
        if not (k.startswith("Jetty") and k[5:].isdigit()):
            continue
        for m in range(JETTY_MODULES):
            rows.append({"piece": "hm_dock_4m", "at": [v["pos"][0], r3(z0 + step * (m + 0.5))], "y": 0.0,
                         "yaw_deg": 90.0, "scale": r3(abs(step) / DOCK_MODULE_M)})
    return rows


def _row(piece: str, x: float, z: float, y: float = 0.0, yaw: float = 0.0, **extra) -> dict:
    return {"piece": piece, "at": [x, z], "y": y, "yaw_deg": yaw, **extra}


def dressing() -> dict:
    b = blocks()
    pieces = dock_rows(b) + jetty_rows(b)
    pieces += [_row("hm_lashed_hulls", v["pos"][0], v["pos"][2], WATER_Y, HOUSE_YAW)
               for k, v in sorted(b.items()) if k.startswith("HousePlatform") and k[13:].isdigit()]
    pieces += [_row("hm_lashed_hulls", x, z, WATER_Y, yaw) for x, z, yaw in HOMES]
    pieces += [_row("hm_windmill", x, z, WATER_Y, yaw) for x, z, yaw in WINDMILLS]
    pieces += [_row("hm_tide_wheel", x, z, WATER_Y, yaw) for x, z, yaw in TIDE_WHEELS]
    pieces += [_row("hm_signal_lamp", x, z) for x, z in SIGNAL_LAMPS]
    pieces += [_row("hm_oil_lamp", x, z, yaw=yaw) for x, z, yaw in OIL_LAMPS]
    pieces.append(_row("hm_supper_table", SUPPER_AT[0], SUPPER_AT[1], yaw=SUPPER_AT[2], collide=True))
    pieces.append(_row("pyre_raft", b["PyreRaft"]["pos"][0], b["PyreRaft"]["pos"][2], WATER_Y))
    pieces.append(_row("hm_ship", b["Ship"]["pos"][0], b["Ship"]["pos"][2], WATER_Y))
    pieces.append(_row("dace_hull_frame", DACE_AT[0], DACE_AT[1], WATER_Y, DACE_AT[2]))
    pieces.append(_row("hm_far_flotilla", FLOTILLA_AT[0], FLOTILLA_AT[1], WATER_Y))
    lights = [{"at": _flame(x, z, yaw), "energy": OIL_ENERGY, "range": OIL_RANGE_M} for x, z, yaw in OIL_LAMPS]
    lights.append({"at": [SUPPER_AT[0] + 0.15, 0.75, SUPPER_AT[1] - 0.2], "energy": 0.6, "range": 3.5})
    lights += [{"at": [x + 0.55, 3.0, z], "energy": 0.8, "range": 6.0, "color": SIGNAL_COLOR} for x, z in SIGNAL_LAMPS]
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by tools/act2/ch15_hollowmere_dressing.py from env-art's Haluna kit (hollowmere.py and its "
        "M4-A2P-045 pieces); do not edit by hand. The greybox's frame.",
        "seed": 15,
        "kit_dir": KIT,
        "materials_dir": ans.KIT_MATERIALS,
        "lod1_from_m": 120.0,
        "lod_end_m": 4000.0,
        "lod_margin_m": 2.0,
        "environment": RES_ZONE + ENV_NAME,
        "time_of_day_h": 5.67,
        "greybox": {"hide_all": True, "keep": []},
        "fire_light_color": OIL_COLOR,
        "fire_lights": lights,
        "pieces": pieces,
    }


def _flame(x: float, z: float, yaw: float) -> list[float]:
    import math  # noqa: PLC0415

    fx, fy, fz = LAMP_FLAME
    a = math.radians(yaw)
    return [r3(x + fx * math.cos(a) + fz * math.sin(a)), r3(fy), r3(z - fx * math.sin(a) + fz * math.cos(a))]


def water() -> str:
    text = ans.WATER_TEMPLATE.read_text(encoding="utf-8").replace('resource_name = "pemakar_sea"',
                                                                  'resource_name = "hollowmere_dawn_water"')
    lines = text.rstrip("\n").split("\n")
    for key, value in WATER.items():
        idx = [i for i, ln in enumerate(lines) if ln.startswith(f"shader_parameter/{key} = ")]
        assert len(idx) == 1, key
        lines[idx[0]] = f"shader_parameter/{key} = {value}"
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
resource_name = "hollowmere_ch15_dawn"
background_mode = 2
sky = SubResource("Sky")
ambient_light_source = 2
ambient_light_color = Color(0.5412, 0.5882, 0.6275, 1)
ambient_light_energy = 0.6
reflected_light_source = 2
tonemap_mode = 4
tonemap_exposure = {EXPOSURE}
tonemap_agx_white = 12.0
ssr_enabled = true
ssr_max_steps = 48
ssr_fade_in = 0.15
ssr_fade_out = 2.0
ssao_enabled = true
ssao_radius = 1.2
ssao_intensity = 1.2
glow_enabled = true
glow_intensity = 0.6
glow_bloom = 0.04
glow_hdr_threshold = 0.9
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
    '[ext_resource type="Resource" path="res://game/world/water/lagoon_waves.tres" id="5_waves"]\n'
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
layout_path = "{RES_ZONE}hollowmere_dressing.json"
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


def write_lut() -> None:
    zone_lut.GRADES["ch15_hollowmere_dawn"] = dict(LUT_DAWN)
    zone_lut.write_png(ZONE / LUT_NAME, zone_lut.table(False, "ch15_hollowmere_dawn"))
    imp = ZONE / (LUT_NAME + ".import")
    if not imp.exists():
        imp.write_text(ans.LUT_IMPORT.format(res=RES_ZONE + LUT_NAME), encoding="utf-8")


def main() -> None:
    (ZONE / "hollowmere_dressing.json").write_text(json.dumps(dressing(), indent=1) + "\n", encoding="utf-8")
    (ZONE / WATER_NAME).write_text(water(), encoding="utf-8")
    write_lut()
    (ZONE / ENV_NAME).write_text(environment(), encoding="utf-8")
    wire_scene()


if __name__ == "__main__":
    main()
