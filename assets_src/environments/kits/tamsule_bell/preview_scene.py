"""Writes the Tamsule Bell kit's preview scene, its ch07 environment and water look, and the preview shot
manifest (M3-ENV-01). Deterministic: the layout below is the only source; rerun after changing it.

    python3 assets_src/environments/kits/tamsule_bell/preview_scene.py

Outputs (game/levels/_tests/tamsule_bell_kit/, Environment-owned):
  tamsule_bell_kit.tscn         the arena composed from the kit around the held drop, the port edge,
                                the river, eight composed cameras (tamsule_bell.md §4, T01-T08)
  tamsule_noon_environment.tres the `ch07` sub-frame: sky, AgX, exposure 0.65, lut_ch07_festival, haze
  tamsule_water_material.tres   the `lagoon_clear` x1.5 water look (colour script ch07 row)
  preview_shots.json            every composed camera as a capture shot (viewing only; at most two are
                                registered in tests/screenshots/shots.json)

The rig is the Haluna kit's HalunaMood (sun from elevation/azimuth, hymn_* globals, held weather clock
for captures), used read-only with the ch07 values. Arena coordinates: origin on the bell axis at the
river datum, north -Z; a ring piece built at azimuth 0 is placed at azimuth a with rotation.y = -a.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import bell  # noqa: E402
import tb_common as tb  # noqa: E402

OUT_DIR = ROOT / "game" / "levels" / "_tests" / "tamsule_bell_kit"
RES_DIR = "res://game/levels/_tests/tamsule_bell_kit/"
KIT = "res://assets/environments/kits/tamsule_bell/"
VEG = "res://assets/environments/vegetation/"
HALUNA_TEX = "res://assets/environments/kits/haluna/textures/"


def vfov(mm: float) -> float:
    return round(math.degrees(2.0 * math.atan(12.0 / mm)), 1)


# ---- Composed shots (tamsule_bell.md §4) ---------------------------------------------------------
def _p(r, az, y):
    v = tb.polar(r, az, y)
    return (round(float(v[0]), 2), round(float(v[1]), 2), round(float(v[2]), 2))


SHOTS = [
    # id, lens mm, position, look_at, note
    ("T01", 24, _p(150.0, 191.0, 2.8), (-9.0, 25.0, 0.0), "the whole Bell from the river mouth, through the south gap"),
    ("T02", 35, _p(35.9, 266.0, 6.8), (0.0, 17.0, -2.0), "west gallery, second tier, looking east and up"),
    ("T03", 24, _p(28.0, 20.0, 0.9), (4.0, 13.0, 4.0), "Oruvel's moorings, under the Bell"),
    ("T04", 35, _p(23.5, 91.0, 3.6), (0.0, 11.0, 3.0), "on the east jetty: the prow and its float-post, the column beyond"),
    ("T05", 18, _p(6.0, 180.0, 0.85), (0.0, 10.45, 0.0), "from the catch-pool up the column"),
    ("T06", 85, _p(95.0, 78.0, 12.0), (13.5, 53.0, -7.5), "the accreted leg at the head joint"),
    ("T07", 100, _p(40.5, 165.5, 11.6), tuple(round(float(x), 2) for x in tb.polar(16.6, 158.0, 35.2)),
     "the bell's waist: ribs, a glass bay, the conduit"),
    ("T08", 35, _p(91.5, 120.0, 3.2), (0.0, 22.0, 0.0), "the east boardwalk: gilded boards, the Bell over the galleries"),
]


# ---- Layout -----------------------------------------------------------------------------------
def layout() -> list[tuple[str, str, tuple, float, float]]:
    """(node name, piece, position, yaw degrees, uniform scale) for every kit instance."""
    rng = np.random.default_rng(np.random.SeedSequence([2026, 1024, 7]))
    out: list[tuple[str, str, tuple, float, float]] = []

    def add(name, piece, pos, yaw=0.0, scale=1.0):
        out.append((name, piece, tuple(round(float(v), 3) for v in pos), round(float(yaw), 3), scale))

    add("Bell", "tamsule_bell", (0, 0, 0))
    add("GoalRing", "goal_ring", (0, 0, 0))
    add("GantryHead", "gantry_head", (0, 0, 0))
    for k in range(6):
        add(f"GantryLeg{k}", "gantry_leg", (0, 0, 0), -60.0 * k)
    add("CatchPool", "catch_pool", (0, 0, 0))
    for az, piece in ((40, "a"), (90, "b"), (140, "a"), (220, "b"), (270, "c"), (320, "a")):
        add(f"Gallery{az:03d}", f"gallery_segment_{piece}", (0, 0, 0), -az)
    add("PlatformEast", "captain_platform", (0, 0, 0), -90.0)
    add("PlatformWest", "captain_platform", (0, 0, 0), -270.0)
    add("OruvelMoorings", "oruvel_moorings", tb.polar(21.0, 35.0, 0.0), -35.0)
    for i, az in enumerate((112, 124, 158, 166, 196, 204, 234, 246, 296, 304, 322, 334)):
        add(f"Mooring{i:02d}", "mooring_post", tb.polar(21.0 + (i % 2) * 0.6, az, 0.0), rng.uniform(0, 360))
    for i, (r, az) in enumerate(((22.8, 118), (22.8, 162), (22.6, 240), (23.0, 300), (22.5, 328))):
        add(f"Boat{i}", "watch_boat", tb.polar(r, az, 0.0), -az + 180.0 + rng.uniform(-4, 4))
    # Boats in the reach: arriving down the north lane, and one in the river mouth for T01's foreground.
    add("BoatLane0", "watch_boat", tb.polar(46.0, 356.0, 0.0), 95.0)
    add("BoatLane1", "watch_boat", tb.polar(58.0, 6.0, 0.0), 80.0)
    add("BoatMouth0", "watch_boat", tb.polar(124.0, 196.5, 0.0), 24.0)
    add("BoatMouth1", "watch_boat", tb.polar(84.0, 176.0, 0.0), -70.0)
    for az in (60, 120, 240, 300):
        add(f"Pennants{az:03d}", "pennant_line", (0, 0, 0), -az)
    # Gilded boards on the east boardwalk, in the foreground of T08 (facing its camera).
    cam8 = tb.polar(91.5, 120.0, 3.2)
    for i, (right, fwd) in enumerate(((1.9, 4.6), (3.4, 9.5))):
        p = cam8 + tb.polar(right, 30.0, 0.0) + tb.polar(fwd, 300.0, 0.0)
        p[1] = 1.6
        n = cam8 - p
        add(f"BoardSign{i}", "signboard_gilded", p, math.degrees(math.atan2(n[0], n[2])) + 15.0 * i)
    for i, az in enumerate((-9.0, 9.0)):
        add(f"LaneSign{i}", "signboard_gilded", tb.polar(31.0, az, 2.4), -az + 180.0)
    # Port edge: two rows of shophouses on piles and a boardwalk in front, on the east, west and north
    # banks of the Bell Reach; open to the sea in the south.
    banks = ((58.0, 132.0), (228.0, 302.0), (326.0, 394.0))
    n = 0
    for a0, a1 in banks:
        for row, (r, step, off) in enumerate(((100.0, 6.4, 0.0), (114.0, 6.0, 3.0), (132.0, 6.6, 1.5))):
            az = a0 + off
            while az <= a1:
                rr = r + rng.uniform(-2.5, 2.5)
                face = (az + 180.0) % 360.0  # the front (+Z) faces the axis
                p = tb.polar(rr, az, 0.0 if row < 2 else 0.6)
                yaw = math.degrees(math.atan2(-p[0], -p[2])) + rng.uniform(-4, 4)
                add(f"House{n:03d}", "shophouse_a" if rng.random() < 0.55 else "shophouse_b", p, yaw,
                    round(float(rng.uniform(0.85, 1.3)), 3))
                n += 1
                az += step + rng.uniform(-0.8, 0.8)
                del face
        az = a0
        while az <= a1:
            p = tb.polar(91.5, az, 0.0)
            add(f"Boardwalk{n:03d}", "boardwalk_8m", p, -az - 90.0 + 180.0)
            n += 1
            az += math.degrees(8.0 / 91.5)
    return out


def palms() -> list[tuple[str, str, tuple, float, float]]:
    rng = np.random.default_rng(np.random.SeedSequence([2026, 1024, 8]))
    out = []
    for i in range(34):
        az = rng.choice([rng.uniform(55, 135), rng.uniform(225, 305), rng.uniform(325, 395)])
        r = rng.uniform(142.0, 190.0)
        p = tb.polar(r, az, 0.8)
        out.append((f"Palm{i:02d}", "palm_coconut_" + "abc"[i % 3], tuple(round(float(v), 3) for v in p),
                    round(float(rng.uniform(0, 360)), 3), round(float(rng.uniform(0.9, 1.25)), 3)))
    return out


# ---- Writers ----------------------------------------------------------------------------------
def color(h: str, a: float = 1.0) -> str:
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    return f"Color({r:.4g}, {g:.4g}, {b:.4g}, {a:g})"


def write_environment(path: Path) -> None:
    path.write_text(f"""[gd_resource type="Environment" load_steps=6 format=3]

[ext_resource type="Shader" path="res://game/shaders/environment/env_sky_cumulus.gdshader" id="1_sky"]
[ext_resource type="Texture3D" path="{KIT}lut_ch07_festival.png" id="2_lut"]
[ext_resource type="Texture3D" path="res://assets/vfx/undertow/undertow_noise3d.png" id="3_lattice"]
[ext_resource type="Texture2D" path="res://assets/vfx/sky/cloud_lattice2.png" id="4_lattice2"]

[sub_resource type="ShaderMaterial" id="SkyMat"]
shader = ExtResource("1_sky")
shader_parameter/col_zenith = {color("#2E7FD6")}
shader_parameter/col_horizon = {color("#B8E4F5")}
shader_parameter/background_energy = 1.3
shader_parameter/horizon_curve = 0.14
shader_parameter/cloud_coverage = 0.5
shader_parameter/cloud_coverage_overhead = 0.1
shader_parameter/cloud_lattice = ExtResource("3_lattice")
shader_parameter/cloud_lattice2 = ExtResource("4_lattice2")

[sub_resource type="Sky" id="Sky"]
sky_material = SubResource("SkyMat")
process_mode = 2

[resource]
resource_name = "tamsule_ch07_noon"
background_mode = 2
sky = SubResource("Sky")
ambient_light_source = 3
ambient_light_energy = 0.7
reflected_light_source = 2
tonemap_mode = 4
tonemap_exposure = 0.65
tonemap_agx_white = 12.0
ssao_enabled = true
ssao_radius = 1.6
ssao_intensity = 1.4
sdfgi_enabled = false
glow_enabled = true
glow_intensity = 0.35
glow_bloom = 0.03
glow_hdr_threshold = 1.2
fog_enabled = true
fog_mode = 1
fog_light_color = {color("#D8ECF2")}
fog_density = 0.0012
fog_aerial_perspective = 0.35
fog_sky_affect = 0.0
fog_depth_begin = 60.0
fog_depth_end = 900.0
adjustment_enabled = true
adjustment_color_correction = ExtResource("2_lut")
""", encoding="utf-8")


def write_water(path: Path) -> None:
    # The colour script's ch07 water: lagoon_clear, absorption x1.5, deep #0E4A55 (as haluna_water).
    path.write_text("""[gd_resource type="ShaderMaterial" load_steps=2 format=3]

[ext_resource type="Shader" path="res://game/shaders/water/water_ocean.gdshader" id="1_ocean"]

[resource]
resource_name = "tamsule_water"
render_priority = 0
shader = ExtResource("1_ocean")
shader_parameter/col_deep = Color(0.0549, 0.2902, 0.3333, 1)
shader_parameter/col_scatter_shallow = Color(0.1216, 0.6392, 0.651, 1)
shader_parameter/absorption_per_m = Vector3(2.0, 0.5, 0.42)
shader_parameter/absorption_scale = 1.5
shader_parameter/scatter_energy = 0.25
shader_parameter/caustic_strength = 1.6
shader_parameter/col_foam = Color(0.933, 0.965, 0.957, 1)
shader_parameter/col_sss = Color(0.247, 0.816, 0.788, 1)
shader_parameter/foam_crest_threshold = 0.75
""", encoding="utf-8")


def vec3(v) -> str:
    return "Vector3(" + ", ".join(f"{float(x):g}" for x in v) + ")"


def write_scene(path: Path) -> None:
    pieces = layout()
    trees = palms()
    ext = [
        ("Script", "res://game/levels/ch02/haluna/haluna_mood.gd", "rig"),
        ("Script", "res://game/levels/ch02/haluna/haluna_shot_camera.gd", "cam"),
        ("Script", "res://game/world/camera_shot.gd", "shot"),
        ("Script", "res://game/world/water/water_surface.gd", "water"),
        ("Resource", "res://game/world/water/lagoon_waves.tres", "waves"),
        ("Material", RES_DIR + "tamsule_water_material.tres", "water_mat"),
        ("Environment", RES_DIR + "tamsule_noon_environment.tres", "env"),
        ("Texture2D", HALUNA_TEX + "sand_albedo.png", "sand"),
        ("Script", "res://game/world/water/sphere/water_sphere_rig.gd", "drop"),
    ]
    kinds = sorted({p[1] for p in pieces})
    ext += [("PackedScene", KIT + f"{k}.glb", k) for k in kinds]
    ext += [("PackedScene", VEG + f"{k}.glb", k) for k in sorted({t[1] for t in trees})]
    ext.append(("PackedScene", KIT + "weep_column.glb", "weep_column"))  # env-art-b's (b_column.py), M3-RND-26
    ids = {key: f"{i + 1}_{key}" for i, (_t, _p, key) in enumerate(ext)}
    lines = ["[gd_scene format=3]", ""]
    lines += [f'[ext_resource type="{t}" path="{p}" id="{ids[k]}"]' for t, p, k in ext]
    lines.append("")
    for sid, mm, pos, look, _note in SHOTS:
        lines += [f'[sub_resource type="Resource" id="Shot{sid}"]', 'script = ExtResource("%s")' % ids["shot"],
                  f'id = &"{sid}"', f"position = {vec3(pos)}", f"look_at = {vec3(look)}", f"fov_deg = {vfov(mm)}", ""]
    lines += ['[sub_resource type="PlaneMesh" id="RiverbedMesh"]', "size = Vector2(2400, 2400)", "",
              '[sub_resource type="StandardMaterial3D" id="RiverbedMat"]', f"albedo_color = {color('#9C8E76')}",
              f'albedo_texture = ExtResource("{ids["sand"]}")', "roughness = 0.95", "uv1_triplanar = true",
              "uv1_scale = Vector3(0.5, 0.5, 0.5)", "",
              '[sub_resource type="BoxMesh" id="BankMesh"]', "size = Vector3(400, 6, 700)", "",
              '[sub_resource type="BoxMesh" id="NorthBankMesh"]', "size = Vector3(300, 6, 500)", "",
              '[sub_resource type="StandardMaterial3D" id="BankMat"]', f"albedo_color = {color('#B4A37E')}",
              f'albedo_texture = ExtResource("{ids["sand"]}")', "roughness = 0.95", "uv1_triplanar = true",
              "uv1_scale = Vector3(0.25, 0.25, 0.25)", "",
              '[sub_resource type="CylinderMesh" id="PoolWaterMesh"]', "top_radius = 12.02", "bottom_radius = 12.02",
              "height = 0.002", "radial_segments = 96", "rings = 1", "cap_bottom = false", ""]
    lines += ['[node name="TamsuleBellKit" type="Node3D" node_paths=PackedStringArray("sun", "water", '
              '"world_environment")]', f'script = ExtResource("{ids["rig"]}")', 'sun = NodePath("Sun")',
              'water = NodePath("Water")', 'world_environment = NodePath("WorldEnvironment")',
              "sun_elevation_deg = 78.0", "sun_azimuth_deg = 180.0", "time_of_day_h = 12.25",
              "wind_azimuth_deg = 0.0", "wind_speed_m_s = 4.0", "wind_gust = 0.25", "",
              '[node name="WorldEnvironment" type="WorldEnvironment" parent="."]',
              f'environment = ExtResource("{ids["env"]}")', "",
              '[node name="Sun" type="DirectionalLight3D" parent="."]', f"light_color = {color('#FFF3E7')}",
              "light_energy = 3.2", "shadow_enabled = true", "shadow_bias = 0.03", "shadow_normal_bias = 1.0",
              "shadow_blur = 1.2", "sky_mode = 1", "directional_shadow_mode = 2",
              "directional_shadow_split_1 = 0.05", "directional_shadow_split_2 = 0.15",
              "directional_shadow_split_3 = 0.4", "directional_shadow_max_distance = 500.0", "",
              '[node name="Water" type="Node3D" parent="."]', f'script = ExtResource("{ids["water"]}")',
              "publishes_water_level = true", f'wave_set = ExtResource("{ids["waves"]}")',
              f'material = ExtResource("{ids["water_mat"]}")', "",
              '[node name="PoolWater" type="Node3D" parent="."]', "position = Vector3(0, 0.35, 0)",
              f'script = ExtResource("{ids["water"]}")', f'wave_set = ExtResource("{ids["waves"]}")',
              f'material = ExtResource("{ids["water_mat"]}")', 'surface_mesh = SubResource("PoolWaterMesh")', "",
              '[node name="Riverbed" type="MeshInstance3D" parent="."]', "position = Vector3(0, -3.5, 0)",
              'mesh = SubResource("RiverbedMesh")', 'surface_material_override/0 = SubResource("RiverbedMat")', ""]
    for name, pos, mesh in (("BankEast", (325, -2.2, -190), "BankMesh"), ("BankWest", (-325, -2.2, -190), "BankMesh"),
                            ("BankNorth", (0, -2.2, -390), "NorthBankMesh")):
        lines += [f'[node name="{name}" type="MeshInstance3D" parent="."]', f"position = {vec3(pos)}",
                  f'mesh = SubResource("{mesh}")', 'surface_material_override/0 = SubResource("BankMat")', ""]
    lines += ['[node name="Arena" type="Node3D" parent="."]', ""]
    for name, piece, pos, yaw, scale in pieces:
        lines += [f'[node name="{name}" parent="Arena" instance=ExtResource("{ids[piece]}")]',
                  f"position = {vec3(pos)}"]
        if yaw:
            lines.append(f"rotation = Vector3(0, {math.radians(yaw):.6f}, 0)")
        if scale != 1.0:
            lines.append(f"scale = {vec3((scale, scale, scale))}")
        lines.append("")
    lines += ['[node name="Palms" type="Node3D" parent="."]', ""]
    for name, piece, pos, yaw, scale in trees:
        lines += [f'[node name="{name}" parent="Palms" instance=ExtResource("{ids[piece]}")]',
                  f"position = {vec3(pos)}", f"rotation = Vector3(0, {math.radians(yaw):.6f}, 0)",
                  f"scale = {vec3((scale, scale, scale))}", ""]
    # The water-drop contract (tamsule_bell.md §1): the anchor, the drop (WaterSphereRig's "tamsule_drop", M3-RND-26),
    # and two markers.
    lines += ['[node name="SphereAnchor" type="Marker3D" parent="."]', f"position = {vec3(bell.DROP_CENTER)}",
              "gizmo_extents = 14.0", "",
              '[node name="Drop" type="Node3D" parent="SphereAnchor"]', f'script = ExtResource("{ids["drop"]}")',
              'profile = "tamsule_drop"', "",
              f'[node name="WeepColumn" parent="SphereAnchor" instance=ExtResource("{ids["weep_column"]}")]',
              f"position = Vector3(0, {bell.POOL_WATER_Y - bell.DROP_CENTER[1]:g}, 0)", "",
              '[node name="ColumnAnchor" type="Marker3D" parent="."]', f"position = Vector3(0, {bell.DROP_BOTTOM_Y:g}, 0)",
              "", '[node name="GoalRingAnchor" type="Marker3D" parent="."]',
              f"position = Vector3(0, {bell.DROP_TOP_Y:g}, 0)", "", '[node name="Cameras" type="Node3D" parent="."]', ""]
    for sid, _mm, _pos, _look, _note in SHOTS:
        lines += [f'[node name="{sid}" type="Camera3D" parent="Cameras"]', "near = 0.05", "far = 4000.0",
                  f'script = ExtResource("{ids["cam"]}")', f'shot = SubResource("Shot{sid}")', ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_manifest(path: Path) -> None:
    shots = []
    for sid, mm, _pos, _look, note in SHOTS:
        shots.append({"id": f"tamsule_{sid.lower()}", "scene": RES_DIR + "tamsule_bell_kit.tscn",
                      "camera": f"Cameras/{sid}", "_note": f"{sid}, {mm} mm: {note}"})
    data = {
        "_about": "M3-ENV-01 preview shots of the Tamsule Bell kit (tamsule_bell.md §4), for viewing; generated by "
                  "assets_src/environments/kits/tamsule_bell/preview_scene.py. Capture with "
                  "tests/screenshots/capture.tscn -- --manifest=res://game/levels/_tests/tamsule_bell_kit/"
                  "preview_shots.json --out=<dir> --shots=<ids>.",
        "defaults": {"camera": "default", "resolution": [960, 540], "settle_frames": 24, "seed": 1,
                     "threshold_rmse": 0.008,
                     "setup": {"globals": {"hymn_wind_time": 40.0},
                               "viewport": {"use_taa": False, "screen_space_aa": 1}}},
        "shots": shots,
    }
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    import argparse  # noqa: PLC0415

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(OUT_DIR), help="output folder (the tests write a copy elsewhere)")
    out = Path(ap.parse_args(argv).out)
    out.mkdir(parents=True, exist_ok=True)
    write_environment(out / "tamsule_noon_environment.tres")
    write_water(out / "tamsule_water_material.tres")
    write_scene(out / "tamsule_bell_kit.tscn")
    write_manifest(out / "preview_shots.json")
    print(f"PREVIEW {len(layout())} kit instances, {len(SHOTS)} cameras -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
