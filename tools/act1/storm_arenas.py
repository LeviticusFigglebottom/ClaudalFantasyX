"""The storm fights' arenas (the human's FAST-TRACK, 2026-11-03; env-art-b): "the seagull/storm scene doesn't show the
actual vortex, and its fights use the normal backdrop". Every fight fought under the Undertow gets a storm arena: a
dark storm sky with no sun disc, cool storm light (a soft key from behind the battle camera, a glimmer rim from the
storm's bearing, the ambient lifted so the party reads), rain on the battle camera, the ground and kit soaked
(ArenaRainWet over the weathering shader's `rain_wet`), and Rendering's UndertowStorm on the sea down the battle
camera's view, with a StormFarPlane so the camera's far plane reaches it.

  oruvel_raft_storm         Ch1 C1-12 on: the Scuttlers and the Hullgnaw after the lintel-gulls cry (preset
                            ch01_arrival). A new arena from env-art's oruvel_raft_morning table (read-only), written
                            here; act1-chapters points the two encounters at it.
  seawall_stairhead_*       Ch8's three wall-head arenas (the stair holds and the Reach), in place: their wrapper
                            (assets_src/environments/kits/corrow/b_seawall_storm.py) takes LOOKS["ch08_storm"]
                            ("ch08_reach" for the surge).
  drowned_choir_storm       Ch16 B09, `ch16_storm_wakes`: the storm waking early over the Choir. A new arena from
                            env-art's drowned_choir_ring table (read-only) under LOOKS["ch16_waking"], the Undertow at
                            ch08_landfall over the ring; act1-chapters points the encounter at it.
  coilspire_headland_path   Ch8's headland fights at 16:00, before the binding: the wall stands on the sea but the
                            storm is not yet overhead, so LOOKS["ch08_brewing"] (overcast, a little rain) and the
                            Undertow at ch08_seawall; written by b_headland_arena.py.

This module holds the looks and the scene additions; each wrapper applies them. Re-run (Ch1's arena):

    python3 tools/act1/storm_arenas.py
"""

from __future__ import annotations

import importlib.util
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STORM_SCRIPT = "res://game/vfx/undertow/undertow_storm.gd"
FAR_SCRIPT = "res://game/levels/act1/storm_far_plane.gd"
WET_SCRIPT = "res://game/levels/act1/arena_rain_wet.gd"
LOW_SUN_SKY = "res://game/shaders/environment/env_sky_low_sun.gdshader"

# The storm sky: the low-sun shader with the sun buried (no disc, halo or warm band) under a near-full deck of
# cloud whose undersides take a little cold light. `bright` lifts the deck toward the horizon on the storm's far side.
_STORM_SKY = {
    "sky_energy": 1.0, "background_energy": 1.0, "horizon_curve": 0.3, "azimuth_power": 1.5,
    "col_band": "#8C9AA6", "band_energy": 0.15, "band_height": 0.05, "mid_strength": 0.0,
    "col_glow": "#B8C4CC", "glow_energy": 0.15, "glow_power": 3.0, "halo_energy": 0.0, "halo_power": 200.0,
    "sun_disc_energy": 0.0, "cloud_softness": 0.3, "cloud_opacity": 1.0, "cloud_height_m": 1400.0,
    "cloud_scale_m": 3800.0, "cloud_stretch": "Vector2(1, 2.0)", "cloud_wind_deg": 135.0, "cloud_sun_energy": 0.35,
    "cloud_horizon_fade": 0.06,
}

LOOKS: dict[str, dict] = {
    # Ch8 in the storm (the stair holds): the canopy's edge, near-night at 16:40, slate and green-grey.
    "ch08_storm": {
        "sky": {**_STORM_SKY, "col_zenith": "#323C45", "col_horizon_sun": "#7E8A90", "col_horizon_away": "#68747C",
                "col_ground": "#1E262C", "col_cloud_lit": "#727E86", "col_cloud_shadow": "#2A333B",
                "cloud_coverage": 0.7, "cloud_ambient_energy": 1.0},
        "sun": {"elev": 42.0, "az": 160.0, "color": "#B7C6D2", "energy": 1.1},
        "fill": {"color": "#7E909E", "energy": 0.85},
        "exposure": 0.95,
        "fog": {"color": "#56626A", "aerial": 0.6, "density": 0.0035, "sky_affect": 0.2, "height": 0.0,
                "height_density": 0.0},
        "rim": {"elev": 14.0, "color": "#9FD4D6", "energy": 0.55},
        "rain": 0.55, "wet": 0.85,
    },
    # The Undertow's Reach: the same storm, the rain eased so the party's turns read (PC row 72), a stronger rim.
    "ch08_reach": {
        "sky": {**_STORM_SKY, "col_zenith": "#2C353E", "col_horizon_sun": "#76848C", "col_horizon_away": "#5E6A72",
                "col_ground": "#1A2228", "col_cloud_lit": "#6A767E", "col_cloud_shadow": "#262E36",
                "cloud_coverage": 0.75, "cloud_ambient_energy": 0.95},
        "sun": {"elev": 45.0, "az": 160.0, "color": "#B7C6D2", "energy": 1.25},
        "fill": {"color": "#8395A3", "energy": 0.95},
        "exposure": 1.0,
        "fog": {"color": "#525E66", "aerial": 0.6, "density": 0.003, "sky_affect": 0.2, "height": 0.0,
                "height_density": 0.0},
        "rim": {"elev": 16.0, "color": "#A6DCDC", "energy": 0.75},
        "rain": 0.35, "wet": 0.9,
    },
    # Ch8's headland at 16:00, before the binding: overcast and darkening, the wall on the sea, the first rain.
    "ch08_brewing": {
        "sky": {**_STORM_SKY, "col_zenith": "#3E4952", "col_horizon_sun": "#949EA2", "col_horizon_away": "#7C878E",
                "col_ground": "#222A31", "col_cloud_lit": "#8A949A", "col_cloud_shadow": "#343D45",
                "cloud_coverage": 0.7, "cloud_ambient_energy": 1.0, "sky_energy": 1.2},
        "sun": {"elev": 38.0, "az": 160.0, "color": "#C9D2D8", "energy": 1.4},
        "fill": {"color": "#7E8E9C", "energy": 0.9},
        "exposure": 0.9,
        "fog": {"color": "#68737A", "aerial": 0.5, "density": 0.0022, "sky_affect": 0.2, "height": 0.0,
                "height_density": 0.0},
        "rim": {"elev": 12.0, "color": "#A8CCD0", "energy": 0.4},
        "rain": 0.2, "wet": 0.45,
    },
    # Ch1 from C1-12: the storm come out of a clear noon over the raft-town, still far off but the sky going grey
    # from the sea; the rain's first bands reach the low hulls.
    "ch01_rising": {
        "sky": {**_STORM_SKY, "col_zenith": "#3A4A58", "col_horizon_sun": "#9AA6AC", "col_horizon_away": "#8392A0",
                "col_ground": "#22303A", "col_cloud_lit": "#8E9AA2", "col_cloud_shadow": "#36424C",
                "cloud_coverage": 0.6, "cloud_ambient_energy": 1.0, "sky_energy": 1.25},
        "sun": {"elev": 55.0, "az": 150.0, "color": "#C4D0DA", "energy": 1.6},
        "fill": {"color": "#7F93A4", "energy": 0.8},
        "exposure": 0.85,
        "fog": {"color": "#748490", "density": 0.0022, "sky_affect": 0.2, "height": 0.0, "height_density": 0.0},
        "rim": {"elev": 12.0, "color": "#A6CCD2", "energy": 0.45},
        "rain": 0.35, "wet": 0.65,
    },
    # Ch16 B09, the storm waking early over the Drowned Choir at moonrise (ch16_storm_wakes): night, the moon gone
    # behind the canopy's edge, the horizon a shade paler than the storm so its mass and wounds stand on it.
    "ch16_waking": {
        "sky": {**_STORM_SKY, "col_zenith": "#121A24", "col_horizon_sun": "#4A5A68", "col_horizon_away": "#36424E",
                "col_ground": "#0E161C", "col_cloud_lit": "#3E4A56", "col_cloud_shadow": "#10161C",
                "cloud_coverage": 0.75, "cloud_ambient_energy": 0.7, "sky_energy": 0.9},
        "sun": {"elev": 30.0, "az": 160.0, "color": "#9FB0C8", "energy": 0.7, "max_distance": 80.0},
        "fill": {"color": "#4A5C70", "energy": 0.6},
        "exposure": 1.15,
        "fog": {"color": "#2E3A46", "density": 0.0025, "sky_affect": 0.2, "height": 0.0, "height_density": 0.0},
        "rim": {"elev": 14.0, "color": "#8FD0D8", "energy": 0.6},
        "rain": 0.4, "wet": 0.8,
    },
}


def styled(table: dict, look: str, **extra) -> dict:
    """`table` (an arena_scenes table) under the storm look: its sky, light, fill, exposure and fog replaced. The
    look's sky is the low-sun shader's; a night table's `ambient_sky` gives way to the look's fill."""
    lk = LOOKS[look]
    out = {k: v for k, v in table.items() if k != "ambient_sky"}
    out.update({"sky_shader": LOW_SUN_SKY, "sky": dict(lk["sky"]), "sun": dict(lk["sun"]), "fill": dict(lk["fill"]),
                "exposure": lk["exposure"], "fog": dict(lk["fog"])})
    out.update(extra)
    return out


def azimuth_deg(eye, target) -> float:
    """A hint's bearing, clockwise from north (-Z), as UndertowStorm.approach_azimuth_deg reads it."""
    (px, _py, pz), (lx, _ly, lz) = eye, target
    return round(math.degrees(math.atan2(lx - px, -(lz - pz))) % 360.0, 2)


def _bump_steps(text: str, n: int) -> str:
    head = re.match(r"\[gd_scene load_steps=(\d+) format=3\]", text)
    return text.replace(head.group(0), f"[gd_scene load_steps={int(head.group(1)) + n} format=3]", 1)


def _add_ext(text: str, kind: str, path: str, rid: str) -> str:
    if f'id="{rid}"' in text:
        return text
    last = list(re.finditer(r"^\[ext_resource [^\n]*\]$", text, flags=re.M))[-1]
    text = text[:last.end()] + f'\n[ext_resource type="{kind}" path="{path}" id="{rid}"]' + text[last.end():]
    return _bump_steps(text, 1)


def add_storm(text: str, *, azimuth: float, preset: str, sea_y: float, rain: float | None) -> str:
    """Rendering's UndertowStorm down `azimuth` with a StormFarPlane under it. The arena's Sun and WorldEnvironment
    move to the battle scene, so the storm takes no zone shadow or exposure flash (the grade is already the storm's).
    `rain`: the rain on the battle camera (None: the preset's distance falloff)."""
    text = _add_ext(text, "Script", STORM_SCRIPT, "storm_script")
    text = _add_ext(text, "Script", FAR_SCRIPT, "storm_far")
    rain_line = f"rain_amount = {rain}\n" if rain is not None else ""
    return text.rstrip("\n") + (
        '\n\n[node name="Undertow" type="Node3D" parent="."]\n'
        'script = ExtResource("storm_script")\n'
        f"approach_azimuth_deg = {azimuth}\n"
        f'preset = "{preset}"\n'
        f"{rain_line}"
        "zone_shadow = false\n"
        "exposure_flash = false\n"
        f"sea_level_y = {sea_y}\n"
        "sea_level_from_water = false\n"
        '\n[node name="FarPlane" type="Node" parent="Undertow"]\n'
        'script = ExtResource("storm_far")\n')


def _dir_xform(elev_deg: float, az_deg: float) -> str:
    """A DirectionalLight3D whose -Z points from (elevation, azimuth clockwise from north = -Z)."""
    el, az = math.radians(elev_deg), math.radians(az_deg)
    z = (math.sin(az) * math.cos(el), math.sin(el), -math.cos(az) * math.cos(el))
    x = (z[2], 0.0, -z[0])
    n = math.hypot(x[0], x[2])
    x = (x[0] / n, 0.0, x[2] / n)
    y = (z[1] * x[2] - z[2] * x[1], z[2] * x[0] - z[0] * x[2], z[0] * x[1] - z[1] * x[0])
    rows = ", ".join(f"{v:.6g}" for v in (x[0], y[0], z[0], x[1], y[1], z[1], x[2], y[2], z[2]))
    return f"Transform3D({rows}, 0, 30, 0)"


def _color(h: str) -> str:
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    return f"Color({r:.4g}, {g:.4g}, {b:.4g}, 1)"


def add_rim(text: str, look: str, azimuth: float) -> str:
    """The storm's glimmer as a shadowless rim from its bearing (it stays in the arena in battle; only Sun moves)."""
    rim = LOOKS[look]["rim"]
    return text.rstrip("\n") + (
        '\n\n[node name="StormRim" type="DirectionalLight3D" parent="."]\n'
        f"transform = {_dir_xform(rim['elev'], azimuth)}\n"
        f"light_color = {_color(rim['color'])}\n"
        f"light_energy = {rim['energy']}\n"
        "light_specular = 0.0\n"
        "shadow_enabled = false\n")


def add_rain_wet(text: str, look: str) -> str:
    """ArenaRainWet, last, so it soaks the slot looks KitSlotSwaps put on first."""
    text = _add_ext(text, "Script", WET_SCRIPT, "rain_wet")
    return text.rstrip("\n") + (
        '\n\n[node name="RainWet" type="Node" parent="."]\n'
        'script = ExtResource("rain_wet")\n'
        f"amount = {LOOKS[look]['wet']}\n")


def dress(text: str, look: str, *, azimuth: float, preset: str, sea_y: float) -> str:
    """Every storm addition but the wetting (which the wrapper adds after its slot swaps)."""
    text = add_storm(text, azimuth=azimuth, preset=preset, sea_y=sea_y, rain=LOOKS[look]["rain"])
    return add_rim(text, look, azimuth)


def _arena_scenes():
    path = ROOT / "assets_src" / "environments" / "kits" / "haluna" / "arena_scenes.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("arena_scenes_storm", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Ch1: the storm comes from the sea, past the foes' side of the deck (the battle camera looks down -Z).
CH01_ID = "oruvel_raft_storm"
CH01_BASE = "oruvel_raft_morning"
CH01_AZIMUTH = 340.0
CH01_LUT = "res://assets/environments/kits/oruvel/lut_ch01_storm.png"
# The lagoon's tropical water under a storm sky reads sunny: the Ch8 arenas' storm-grey sea, a shade darker
CH01_SEA_MATERIAL = {"name": "arena_storm_grey_ch01", "shader": "res://game/shaders/water/water_ocean.gdshader",
                     "params": [["col_deep", "#0B3340"], ["col_scatter_shallow", "#1A5E68"],
                                ["absorption_per_m", "Vector3(2, 0.5, 0.42)"], ["absorption_scale", 2.25],
                                ["scatter_energy", 0.1], ["caustic_strength", 0.0], ["col_foam", "#DDE6E6"],
                                ["col_sss", "#1A5E68"], ["foam_crest_threshold", 0.5], ["roughness_far", 0.2],
                                ["use_caustics", "false"], ["use_ssr", "false"], ["use_sss", "false"]]}


# Ch16: the storm over the ring behind the enemy line (the battle camera looks down -Z), between two singers.
CH16_ID = "drowned_choir_storm"
CH16_AZIMUTH = 0.0
# The Choir's sea lies only 0.25 m under the dais. With the storm's sea level at the arena's, the storm's own sea
# surfaces drew through the dais and the fighters as a black-and-white speckle (lavapipe, viewed: hiding the storm or
# lowering its sea clears it). Its sea sits under the arena's water instead, hidden by it; the wall is kilometres out.
CH16_STORM_SEA_Y = -1.5


def main(out_dir: Path | None = None) -> int:
    AS = _arena_scenes()
    if out_dir is not None:  # tools/tests/test_b_arenas.py writes to a scratch dir
        AS.OUT_DIR = out_dir
    base = AS.ARENAS[CH01_BASE]
    table = styled(base, "ch01_rising", id=CH01_ID, lut=CH01_LUT, sub_frame="ch01_storm",
                   sea={**base["sea"], "material": CH01_SEA_MATERIAL})
    path = AS.write_arena(table)
    text = dress(path.read_text(encoding="utf-8"), "ch01_rising", azimuth=CH01_AZIMUTH, preset="ch01_arrival",
                 sea_y=table["sea"]["y"])
    path.write_text(add_rain_wet(text, "ch01_rising"), encoding="utf-8")
    print(f"ARENA {path.name} (storm look ch01_rising, Undertow ch01_arrival at {CH01_AZIMUTH} deg)")
    base = AS.CHOIR_ARENA
    table = styled(base, "ch16_waking", id=CH16_ID, sub_frame="ch16_storm")
    path = AS.write_arena(table)
    text = dress(path.read_text(encoding="utf-8"), "ch16_waking", azimuth=CH16_AZIMUTH, preset="ch08_landfall",
                 sea_y=CH16_STORM_SEA_Y)
    path.write_text(add_rain_wet(text, "ch16_waking"), encoding="utf-8")
    print(f"ARENA {path.name} (storm look ch16_waking, Undertow ch08_landfall at {CH16_AZIMUTH} deg)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
