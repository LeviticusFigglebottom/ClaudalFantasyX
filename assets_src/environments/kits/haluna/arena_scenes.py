"""Writes the battle arena scenes (M2-ENV-11; contract: docs/kb/tech/battle_arenas.md) from the tables below.

    python3 assets_src/environments/kits/haluna/arena_scenes.py            # both arenas
    python3 assets_src/environments/kits/haluna/arena_scenes.py --arena tideline_dawn

Output: assets/environments/arenas/<arena_id>/<arena_id>.tscn. Every placement's height comes from the
same terrain functions that built the ground (arenas.py), so a prop always sits on the ground it was
placed on and a terrain change carries the dressing with it. Lighting values are the colour script's
(sub-frames `ch02` dawn and `ch03_boss`, color_script.md / haluna.md §0); sky colours are inputs.

Coordinates are the battle's: origin at the sandbox's slot layout, north -Z, east +X, the BattleCamera
looking north from (0.6, 2.8, 8.4). Nothing is placed between that camera and the slots.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import arenas  # noqa: E402
import kit_common as kc  # noqa: E402

OUT_DIR = ROOT / "assets" / "environments" / "arenas"
KIT = "res://assets/environments/kits/haluna/"
VEG = "res://assets/environments/vegetation/"
LOW_SUN_SKY = "res://game/shaders/environment/env_sky_low_sun.gdshader"
WATER_MAT = "res://game/levels/ch02/haluna/haluna_water_material.tres"
WAVES = "res://game/world/water/lagoon_waves.tres"
SALTGRASS_MAT = VEG + "materials/saltgrass.tres"


def hexc(h: str) -> str:
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    return f"Color({r:.4g}, {g:.4g}, {b:.4g}, 1)"


def sun_xform(elev_deg: float, az_deg: float, height_m: float = 30.0) -> str:
    """A DirectionalLight3D whose -Z points from the sun (elevation, azimuth clockwise from north = -Z)."""
    el, az = math.radians(elev_deg), math.radians(az_deg)
    z = np.array([math.sin(az) * math.cos(el), math.sin(el), -math.cos(az) * math.cos(el)])
    x = np.cross([0.0, 1.0, 0.0], z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    return _xf(x, y, z, (0.0, height_m, 0.0))


def look_xform(eye, target) -> str:
    eye, target = np.asarray(eye, float), np.asarray(target, float)
    z = eye - target
    z /= np.linalg.norm(z)
    x = np.cross([0.0, 1.0, 0.0], z)
    x /= np.linalg.norm(x)
    return _xf(x, np.cross(z, x), z, eye)


def yaw_xform(yaw_deg: float, pos, scale: float = 1.0) -> str:
    a = math.radians(yaw_deg)
    c, s = math.cos(a) * scale, math.sin(a) * scale
    return _xf((c, 0.0, -s), (0.0, scale, 0.0), (s, 0.0, c), pos)


def _xf(x, y, z, o) -> str:
    vals = [x[0], y[0], z[0], x[1], y[1], z[1], x[2], y[2], z[2], o[0], o[1], o[2]]
    return "Transform3D(" + ", ".join(f"{float(v):.6g}" for v in vals) + ")"


def _ground_fn(name: str):
    if name == "beach":
        return arenas.beach_height(kc.Noise3(kc.rng_for("arena_tideline_ground", 211)))
    if name == "flats":
        return arenas.flats_height(kc.Noise3(kc.rng_for("arena_causeway_flats", 231)))
    return None


def height(ground: str, x: float, z: float) -> float:
    if ground == "disc":
        return arenas.FLOOR_Y
    fn = _ground_fn(ground)
    return float(fn(np.array([[x]]), np.array([[z]]))[0, 0])


# ---------------------------------------------------------------------------------------------
# The arenas
# ---------------------------------------------------------------------------------------------
# Piece rows: (glb, x, z, yaw_deg, scale, sink_m). Palms lean along their local +X (seaward when yaw ~0).
TIDELINE = {
    "id": "tideline_dawn",
    "sub_frame": "ch02",
    "ground": "beach",
    "ground_glb": KIT + "arena_tideline_ground.glb",
    "lut": "res://assets/environments/arenas/tideline_dawn/lut_ch02_dawn.png",
    # Colour script Ch2 (06:20): sun 6 deg / 95 deg, key #FFB87B 2.4, fill #7FA6CC 0.5, exposure 0.75,
    # sky #4E7FB8 / #F6C9A0, fog albedo #E9C9A8, sea-glow 0.04.
    "sun": {"elev": 6.0, "az": 95.0, "color": "#FFB87B", "energy": 2.4},
    "fill": {"color": "#7FA6CC", "energy": 0.5},
    "exposure": 0.75,
    "fog": {"color": "#E9C9A8", "density": 0.0016, "sky_affect": 0.08, "height": 0.0, "height_density": 0.0},
    "sky": {"col_zenith": "#4E7FB8", "col_horizon_sun": "#F6C9A0", "col_horizon_away": "#E2CDBE",
            "col_mid": "#F0D2B4", "mid_strength": 0.35, "mid_height": 0.08, "mid_width": 0.1,
            "col_ground": "#4C6878", "col_band": "#FFD2A0", "band_energy": 0.8, "band_height": 0.05,
            "col_glow": "#FFD3A0", "glow_energy": 1.4, "glow_power": 5.0, "halo_energy": 3.0,
            "col_cloud_lit": "#FFCFA2", "col_cloud_shadow": "#8A93B4", "cloud_coverage": 0.46,
            "cloud_sun_energy": 2.4, "cloud_ambient_energy": 0.8, "cloud_wind_deg": 200.0, "horizon_curve": 0.55,
            "azimuth_power": 1.0},
    "sea": {"y": -0.4, "tide_line_y": 0.0, "sea_glow": 0.04},
    "pieces": [
        # The dune line, frame left: palms leaning to the sea, an outrigger pulled up above the wrack.
        (VEG + "palm_coconut_b.glb", -12.0, -7.0, 8.0, 0.95, 0.15),
        (VEG + "palm_coconut_a.glb", -17.0, -16.0, -12.0, 1.1, 0.15),
        (VEG + "palm_coconut_c.glb", -10.5, -24.0, 18.0, 0.9, 0.15),
        (VEG + "palm_coconut_a.glb", -22.0, -30.0, 4.0, 1.2, 0.15),
        (VEG + "palm_coconut_b.glb", -14.0, -40.0, -6.0, 1.0, 0.15),
        (VEG + "palm_coconut_c.glb", -26.0, -11.0, 22.0, 1.05, 0.15),
        (VEG + "palm_coconut_a.glb", -8.0, -60.0, 10.0, 0.95, 0.15),
        (VEG + "palm_coconut_c.glb", -4.0, -78.0, -15.0, 1.0, 0.15),
        (VEG + "palm_coconut_b.glb", 2.0, -98.0, 12.0, 1.1, 0.15),
        (VEG + "palm_coconut_a.glb", 10.0, -104.0, -8.0, 1.0, 0.15),
        (VEG + "palm_coconut_c.glb", -6.0, -106.0, 25.0, 1.15, 0.15),
        (KIT + "outrigger_7m.glb", -7.5, -9.0, 72.0, 1.0, 0.1),
        (KIT + "fish_drying_rack.glb", -16.0, -20.0, 95.0, 1.0, 0.1),
        (VEG + "beach_vine_patch.glb", -9.0, -2.0, 30.0, 1.2, 0.02),
        (VEG + "beach_vine_patch.glb", -11.0, -11.0, 150.0, 1.0, 0.02),
        # Home over the dune: the tide-wall and two roofs (Haluna is behind the dune to the west).
        (KIT + "tidewall_straight.glb", -30.0, -14.0, 90.0, 1.0, 0.05),
        (KIT + "tidewall_straight.glb", -30.2, -16.0, 88.0, 1.0, 0.05),
        (KIT + "tidewall_windgap.glb", -30.4, -18.0, 91.0, 1.0, 0.05),
        (KIT + "tidewall_straight.glb", -30.5, -20.0, 89.0, 1.0, 0.05),
        (KIT + "tidewall_straight.glb", -30.6, -22.0, 92.0, 1.0, 0.05),
        (KIT + "house_tile_a.glb", -38.0, -18.0, 95.0, 1.0, 0.05),
        (KIT + "house_tile_b.glb", -40.0, -30.0, 80.0, 1.0, 0.05),
        # The beach north to the causeway head: pilgrim posts, the path that does not come back.
        (KIT + "pilgrim_marker_post.glb", 6.0, -22.0, 10.0, 1.0, 0.0),
        (KIT + "pilgrim_marker_post_leaning.glb", 8.0, -40.0, -20.0, 1.0, 0.0),
        (KIT + "pilgrim_marker_post.glb", 10.5, -58.0, 5.0, 1.0, 0.0),
        (KIT + "pilgrim_marker_post_broken.glb", 12.0, -76.0, 40.0, 1.0, 0.0),
        # The waterline: a half-buried wreck, coral heads in the shallows, the headland's rocks.
        (KIT + "wreck_rib.glb", 5.0, -16.0, 30.0, 1.0, 0.12),
        (KIT + "coral_boulder_b.glb", 12.0, -12.0, 40.0, 1.0, 0.2),
        (KIT + "coral_boulder_a.glb", 9.0, -14.0, 0.0, 1.0, 0.1),
        (KIT + "coral_boulder_a.glb", 9.8, -15.2, 120.0, 0.8, 0.1),
        (KIT + "coral_boulder_c.glb", 19.0, -30.0, 70.0, 1.0, 0.3),
        (KIT + "coral_boulder_c.glb", 16.0, -96.0, 10.0, 1.2, 0.4),
        (KIT + "coral_boulder_c.glb", 20.0, -100.0, 200.0, 1.0, 0.4),
        (KIT + "coral_boulder_b.glb", 12.0, -90.0, 90.0, 1.1, 0.3),
    ],
    # (name, mesh_node, center (x, z), half extents, count, seed, height range, keep_clear [(x, z, r)])
    "scatters": [
        ("SaltgrassDune", "saltgrass_a", (-19.0, -24.0), (11.0, 34.0), 1800, 31, (0.75, 9.0), [(-1.0, 0.5, 7.5)]),
        ("SaltgrassToe", "saltgrass_b", (-9.0, -8.0), (4.0, 14.0), 320, 37, (0.3, 9.0), [(-1.0, 0.5, 7.5)]),
        ("SaltgrassHeadland", "saltgrass_a", (4.0, -100.0), (26.0, 14.0), 900, 41, (2.0, 20.0), []),
    ],
    "hints": {
        "wide_high": ((-1.5, 7.5, 14.0), (0.0, 0.5, -2.0)),
        "party_side": ((7.0, 1.7, 5.5), (-1.0, 1.0, -0.5)),
        "foe_side": ((-7.5, 1.7, 5.0), (1.5, 1.0, 0.0)),
        "dawn_reverse": ((-2.0, 1.4, -9.0), (1.5, 1.0, 1.0)),
    },
}

CAUSEWAY = {
    "id": "causeway_disc_sunset",
    "sub_frame": "ch03_boss",
    "ground": "flats",
    "ground_glb": KIT + "arena_causeway_flats.glb",
    "lut": "res://assets/environments/arenas/causeway_disc_sunset/lut_ch03_sunset.png",
    # Colour script ch03_boss phase 1 (18:15): sun 2 deg / 270 deg, key #FF9F46 (~2,500 K) 2.0, afterglow
    # fill #5A7FA8 0.35, exposure 0.80, sea-glow 0.04. Ember, not gold: the sky leans red-orange at the
    # horizon and indigo overhead, magenta-free.
    "sun": {"elev": 2.0, "az": 270.0, "color": "#FF9F46", "energy": 2.0},
    "fill": {"color": "#5A7FA8", "energy": 0.35},
    "exposure": 0.8,
    "fog": {"color": "#B07A5E", "density": 0.0016, "sky_affect": 0.05, "height": 0.0, "height_density": 0.0},
    "sky": {"col_zenith": "#263A5E", "col_mid": "#B48A58", "mid_strength": 0.7, "mid_height": 0.1,
            "mid_width": 0.1, "col_horizon_sun": "#E2682A", "col_horizon_away": "#5A6468",
            "col_ground": "#22303C", "col_band": "#FF7A2C", "band_energy": 1.2, "band_height": 0.035,
            "col_glow": "#FF7C36", "glow_energy": 1.8, "glow_power": 4.0, "halo_energy": 4.0,
            "col_cloud_lit": "#FF7A32", "col_cloud_shadow": "#394257", "cloud_coverage": 0.46,
            "cloud_sun_energy": 2.4, "cloud_ambient_energy": 0.6, "cloud_wind_deg": 250.0, "horizon_curve": 0.32,
            "azimuth_power": 1.2},
    "sea": {"y": -0.7, "tide_line_y": -0.7, "sea_glow": 0.04},
    "disc": {"glb": KIT + "causeway_disc.glb", "center": arenas.DISC_CENTER},
    "extra_glbs": [KIT + "arena_causeway_arms.glb"],
    "pieces": [
        # The rim: gate posts where the shrine arm leaves, one broken post on the west rim.
        (KIT + "pilgrim_marker_post.glb", *arenas.disc_xz(14.4, math.radians(60.0)), 15.0, 1.0, 0.0),
        (KIT + "pilgrim_marker_post_leaning.glb", *arenas.disc_xz(14.4, math.radians(77.0)), 200.0, 1.0, 0.0),
        (KIT + "pilgrim_marker_post.glb", *arenas.disc_xz(14.5, math.radians(18.0)), -30.0, 1.0, 0.0),
        (KIT + "pilgrim_marker_post_broken.glb", *arenas.disc_xz(14.4, math.radians(152.0)), 120.0, 1.0, 0.0),
        # The flats: coral heads, a wreck on a hummock, the shrine on its islet on the horizon.
        (KIT + "coral_boulder_c.glb", -19.0, -6.0, 30.0, 1.0, 0.35),
        (KIT + "coral_boulder_b.glb", 18.0, -8.0, 110.0, 1.0, 0.25),
        (KIT + "coral_boulder_b.glb", -23.0, -20.0, 250.0, 1.2, 0.25),
        (KIT + "coral_boulder_a.glb", 22.0, -28.0, 60.0, 1.0, 0.15),
        (KIT + "coral_boulder_c.glb", -34.0, -48.0, 160.0, 1.3, 0.4),
        (KIT + "coral_boulder_c.glb", 30.0, -60.0, 15.0, 1.1, 0.4),
        (KIT + "wreck_rib.glb", -27.0, -33.0, 65.0, 1.0, 0.12),
        (KIT + "shell_shrine_massing.glb", 97.0, -241.0, 90.0, 1.0, 0.3),
        (VEG + "palm_coconut_c.glb", 84.0, -236.0, 160.0, 1.0, 0.2),
        (VEG + "palm_coconut_a.glb", 106.0, -254.0, 200.0, 0.9, 0.2),
    ],
    "scatters": [
        ("SaltgrassHummocks", "saltgrass_a", (0.0, -26.0), (36.0, 26.0), 1600, 53, (-0.12, 3.0), []),
        ("SaltgrassIslet", "saltgrass_b", (97.0, -241.0), (24.0, 24.0), 700, 59, (0.2, 6.0), []),
    ],
    "hints": {
        "wide_high": ((-2.0, 8.5, 15.0), (0.0, 0.0, -4.0)),
        "party_side": ((7.0, 1.6, 5.0), (-1.5, 1.2, -0.5)),
        "foe_side": ((-7.5, 1.6, 5.0), (1.5, 1.0, 0.0)),
        "into_the_sun": ((6.0, 1.2, -3.0), (-6.0, 1.5, 1.0)),
    },
    "anchors": {
        "BossAnchor": (arenas.DISC_CENTER[0], arenas.POOL_FLOOR_Y, arenas.DISC_CENTER[1]),
        "FloodAnchor": (0.0, -0.7, 0.0),
    },
}

ARENAS = {a["id"]: a for a in (TIDELINE, CAUSEWAY)}


# ---------------------------------------------------------------------------------------------
# Writer
# ---------------------------------------------------------------------------------------------
class Scene:
    def __init__(self) -> None:
        self.ext: dict[str, tuple[str, str]] = {}
        self.sub: list[str] = []
        self.nodes: list[str] = []

    def res(self, kind: str, path: str) -> str:
        if path not in self.ext:
            self.ext[path] = (kind, f"{len(self.ext) + 1}_r")
        return self.ext[path][1]

    def node(self, name: str, kind: str | None, parent: str | None, props: dict, instance: str | None = None,
             node_paths: tuple[str, ...] = ()) -> None:
        head = f'[node name="{name}"'
        if kind:
            head += f' type="{kind}"'
        if parent is not None:
            head += f' parent="{parent}"'
        if node_paths:
            head += ' node_paths=PackedStringArray(' + ", ".join(f'"{n}"' for n in node_paths) + ")"
        if instance:
            head += f' instance=ExtResource("{instance}")'
        lines = [head + "]"] + [f"{k} = {v}" for k, v in props.items()]
        self.nodes.append("\n".join(lines))

    def text(self) -> str:
        n = len(self.ext) + len(self.sub) + 1
        out = [f"[gd_scene load_steps={n} format=3]", ""]
        for path, (kind, rid) in self.ext.items():
            out.append(f'[ext_resource type="{kind}" path="{path}" id="{rid}"]')
        out.append("")
        out += [s + "\n" for s in self.sub]
        out += [s + "\n" for s in self.nodes]
        return "\n".join(out).rstrip() + "\n"


def write_arena(a: dict) -> Path:
    sc = Scene()
    script = sc.res("Script", "res://game/world/arenas/battle_arena_root.gd")
    sky_shader = sc.res("Shader", LOW_SUN_SKY)
    lut = sc.res("Texture3D", a["lut"])
    sky_params = "\n".join(
        f"shader_parameter/{k} = {hexc(v) if isinstance(v, str) else v}" for k, v in sorted(a["sky"].items()))
    sc.sub.append(f'[sub_resource type="ShaderMaterial" id="SkyMat"]\nshader = ExtResource("{sky_shader}")\n'
                  + sky_params)
    sc.sub.append('[sub_resource type="Sky" id="Sky"]\nsky_material = SubResource("SkyMat")\nprocess_mode = 2')
    fog = a["fog"]
    sc.sub.append("\n".join([
        '[sub_resource type="Environment" id="Env"]',
        f'resource_name = "{a["id"]}_{a["sub_frame"]}"',
        "background_mode = 2", 'sky = SubResource("Sky")',
        "ambient_light_source = 2", f"ambient_light_color = {hexc(a['fill']['color'])}",
        f"ambient_light_energy = {a['fill']['energy']}", "reflected_light_source = 2",
        "tonemap_mode = 4", f"tonemap_exposure = {a['exposure']}", "tonemap_agx_white = 12.0",
        "ssao_enabled = true", "ssao_radius = 1.2", "ssao_intensity = 1.2",
        "glow_enabled = true", "glow_intensity = 0.35", "glow_bloom = 0.03", "glow_hdr_threshold = 1.2",
        "fog_enabled = true", "fog_mode = 0", f"fog_light_color = {hexc(fog['color'])}",
        f"fog_density = {fog['density']}", f"fog_sky_affect = {fog['sky_affect']}",
        f"fog_height = {fog['height']}", f"fog_height_density = {fog['height_density']}",
        "adjustment_enabled = true", f'adjustment_color_correction = ExtResource("{lut}")',
    ]))
    sc.node(a["id"].title().replace("_", ""), "Node3D", None,
            {"script": f'ExtResource("{script}")', "arena_id": f'&"{a["id"]}"', "sub_frame": f'&"{a["sub_frame"]}"'})
    sc.node("WorldEnvironment", "WorldEnvironment", ".", {"environment": 'SubResource("Env")'})
    s = a["sun"]
    sc.node("Sun", "DirectionalLight3D", ".", {
        "transform": sun_xform(s["elev"], s["az"]), "light_color": hexc(s["color"]), "light_energy": s["energy"],
        "shadow_enabled": "true", "shadow_bias": 0.03, "shadow_normal_bias": 1.0, "shadow_blur": 1.0,
        "directional_shadow_mode": 2, "directional_shadow_split_1": 0.06, "directional_shadow_split_2": 0.18,
        "directional_shadow_split_3": 0.45, "directional_shadow_max_distance": 120.0})
    sea = a["sea"]
    sc.node("Sea", "Node3D", ".", {
        "transform": f"Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, {sea['y']}, 0)",
        "script": f'ExtResource("{sc.res("Script", "res://game/world/arenas/arena_sea.gd")}")',
        "wave_set": f'ExtResource("{sc.res("Resource", WAVES)}")',
        "material": f'ExtResource("{sc.res("Material", WATER_MAT)}")',
        "sea_glow_energy": sea["sea_glow"], "tide_line_y": sea["tide_line_y"]})
    sc.node("Ground", None, ".", {}, instance=sc.res("PackedScene", a["ground_glb"]))
    if "disc" in a:
        cx, cz = a["disc"]["center"]
        sc.node("Disc", None, ".", {"transform": f"Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {cx}, 0, {cz})"},
                instance=sc.res("PackedScene", a["disc"]["glb"]))
    for k, glb in enumerate(a.get("extra_glbs", [])):
        sc.node(f"Kit{k}", None, ".", {}, instance=sc.res("PackedScene", glb))
    sc.node("Dressing", "Node3D", ".", {})
    counts: dict[str, int] = {}
    for glb, x, z, yaw, scale, sink in a["pieces"]:
        stem = Path(glb).stem
        counts[stem] = counts.get(stem, 0) + 1
        y = height(a["ground"], float(x), float(z)) - sink
        sc.node(f"{stem}_{counts[stem]}", None, "Dressing",
                {"transform": yaw_xform(yaw, (float(x), round(y, 3), float(z)), scale)},
                instance=sc.res("PackedScene", glb))
    scatter = sc.res("Script", "res://game/world/vegetation/vegetation_scatter.gd")
    grass = sc.res("PackedScene", VEG + "saltgrass_clumps.glb")
    grass_mat = sc.res("Material", SALTGRASS_MAT)
    for name, mesh, (cx, cz), (hx, hz), count, seed, (h0, h1), clear in a["scatters"]:
        keep = ", ".join(f"Vector3({x - cx}, {z - cz}, {r})" for x, z, r in clear)
        sc.node(name, "MultiMeshInstance3D", "Dressing", {
            "transform": f"Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {cx}, 0, {cz})",
            "script": f'ExtResource("{scatter}")', "source_scene": f'ExtResource("{grass}")',
            "mesh_node": f'&"{mesh}"', "material": f'ExtResource("{grass_mat}")', "count": count,
            "half_extents_m": f"Vector2({hx}, {hz})", "seed_value": seed, "sea_side_falloff": 0.0,
            "patch_frequency": 0.09, "keep_clear": f"Array[Vector3]([{keep}])",
            "ground": 'NodePath("../../Ground")', "height_min_m": h0, "height_max_m": h1}, node_paths=("ground",))
    sc.node("CameraHints", "Node3D", ".", {})
    for name, (eye, target) in a["hints"].items():
        sc.node(name, "Marker3D", "CameraHints", {"transform": look_xform(eye, target)})
    for name, pos in a.get("anchors", {}).items():
        sc.node(name, "Marker3D", ".", {"transform": f"Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {pos[0]}, {pos[1]}, "
                                                     f"{pos[2]})"})
    out = OUT_DIR / a["id"] / f"{a['id']}.tscn"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(sc.text(), encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--arena", action="append", choices=sorted(ARENAS))
    args = ap.parse_args(argv)
    for aid in args.arena or sorted(ARENAS):
        print(f"ARENA {write_arena(ARENAS[aid]).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
