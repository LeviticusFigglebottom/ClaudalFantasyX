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
import functools
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import arenas  # noqa: E402
import kit_common as kc  # noqa: E402

sys.path.append(str(HERE.parent / "pemakar"))  # the Pemakar kit's town layout, read-only (ash_terrace_lanternfall)

OUT_DIR = ROOT / "assets" / "environments" / "arenas"
KIT = "res://assets/environments/kits/haluna/"
VEG = "res://assets/environments/vegetation/"
LOW_SUN_SKY = "res://game/shaders/environment/env_sky_low_sun.gdshader"
WATER_MAT = "res://game/levels/ch02/haluna/haluna_water_material.tres"
WAVES = "res://game/world/water/lagoon_waves.tres"
SALTGRASS_MAT = VEG + "materials/saltgrass.tres"
FAR_LIGHT_SHADER = "res://game/shaders/environment/env_far_lights.gdshader"


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


def tilt_xform(yaw_deg: float, tilt_deg, pos, scale: float = 1.0) -> str:
    """HalunaDresser's placement basis: yaw about Y, then the tilt (x, z degrees) as Basis.from_euler (YXZ)."""
    a, tx, tz = (math.radians(v) for v in (yaw_deg, tilt_deg[0], tilt_deg[1]))
    ry = np.array([[math.cos(a), 0.0, math.sin(a)], [0.0, 1.0, 0.0], [-math.sin(a), 0.0, math.cos(a)]])
    rx = np.array([[1.0, 0.0, 0.0], [0.0, math.cos(tx), -math.sin(tx)], [0.0, math.sin(tx), math.cos(tx)]])
    rz = np.array([[math.cos(tz), -math.sin(tz), 0.0], [math.sin(tz), math.cos(tz), 0.0], [0.0, 0.0, 1.0]])
    m = ry @ rx @ rz * scale
    return _xf(m[:, 0], m[:, 1], m[:, 2], pos)


def _xf(x, y, z, o) -> str:
    vals = [x[0], y[0], z[0], x[1], y[1], z[1], x[2], y[2], z[2], o[0], o[1], o[2]]
    return "Transform3D(" + ", ".join(f"{float(v):.6g}" for v in vals) + ")"


@functools.cache
def _ground_fn(name: str):
    if name == "route":
        return arenas.route_height(kc.Noise3(kc.rng_for("arena_causeway_route_ground", 251)))
    if name == "beach":
        return arenas.beach_height(kc.Noise3(kc.rng_for("arena_tideline_ground", 211)))
    if name == "flats":
        return arenas.flats_height(kc.Noise3(kc.rng_for("arena_causeway_flats", 231)))
    return None


def height(ground: str, x: float, z: float) -> float:
    if ground in ("disc", "deck", "tread", "gallery", "raft"):
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

# ---------------------------------------------------------------------------------------------
# M3-ENV-06: three Act I arenas from the zone kits
# ---------------------------------------------------------------------------------------------
def route_slabs() -> list:
    """The causeway's slabs along arenas.ROUTE_PATH (the kit's own causeway_slab_* pieces, read-only): 2.4 m
    slabs end to end along the line, every ninth one snapped, a few gone far out, each sunk into its bed.
    Marker posts every 20 m beside the line, alternating sides, one leaning and one broken."""
    rng = np.random.default_rng(np.random.SeedSequence([6006, 3]))
    pts = np.asarray(arenas.ROUTE_PATH, float)
    seg = np.hypot(*(pts[1:] - pts[:-1]).T)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    rows = []
    s, k, post = 1.3, 0, 0
    while s < ROUTE_SLAB_LENGTH_M:
        i = min(int(np.searchsorted(cum, s, side="right")) - 1, len(seg) - 1)
        t = (s - cum[i]) / seg[i]
        x, z = pts[i] + (pts[i + 1] - pts[i]) * t
        d = (pts[i + 1] - pts[i]) / seg[i]
        yaw = math.degrees(math.atan2(d[0], d[1])) + float(rng.normal(0.0, 3.0))
        roll = float(rng.random())
        if not (s > 60.0 and roll < 0.07):
            glb = KIT + ("causeway_slab_broken.glb" if k % 9 == 4 else "causeway_slab_flat.glb")
            rows.append((glb, round(float(x), 3), round(float(z), 3), round(yaw, 2), 1.0,
                         round(0.12 + float(rng.uniform(0.0, 0.06)), 3)))
        if s >= 12.0 + 20.0 * post:
            side = 1.0 if post % 2 else -1.0
            px, pz = x - d[1] * 1.15 * side, z + d[0] * 1.15 * side
            name = ("pilgrim_marker_post_leaning.glb" if post == 3 else "pilgrim_marker_post_broken.glb"
                    if post == 5 else "pilgrim_marker_post.glb")
            rows.append((KIT + name, round(float(px), 3), round(float(pz), 3), round(float(rng.uniform(0, 360)), 1),
                         1.0, 0.05))
            post += 1
        s += 2.6 + float(rng.uniform(0.0, 0.08))
        k += 1
    return rows


ROUTE_SLAB_LENGTH_M = 150.0  # beyond this the bed's low ridge carries the line to the islet

CAUSEWAY_ROUTE = {
    "id": "causeway_route_afternoon",
    "sub_frame": "ch03_causeway",
    "ground": "route",
    "ground_glb": KIT + "arena_causeway_route_ground.glb",
    # The route's gameplay grade is lut_ch02_noon (haluna.md §0 `ch03_causeway`; the +200 K is in the key).
    "lut": "res://game/levels/ch02/haluna/lut_ch02_noon.png",
    # haluna.md `ch03_causeway` (14:30, low tide): sun 52 deg / 250 deg, key #FFEAD8 3.0, sky fill #A9DCF2 at
    # 0.6 (the sky's own radiance, as in the zone), exposure 0.65. The zone's cumulus sky.
    "sun": {"elev": 52.0, "az": 250.0, "color": "#FFEAD8", "energy": 3.0},
    "fill": {"color": "#A9DCF2", "energy": 0.6},
    "ambient_sky": 0.6,
    "exposure": 0.65,
    "fog": {"color": "#CFE2EA", "density": 0.0007, "sky_affect": 0.0, "height": 0.0, "height_density": 0.0},
    "sky_shader": "res://game/shaders/environment/env_sky_cumulus.gdshader",
    "sky": {"background_energy": 1.5, "horizon_curve": 0.14,
            "cloud_lattice": ("Texture3D", "res://assets/vfx/undertow/undertow_noise3d.png"),
            "cloud_lattice2": ("Texture2D", "res://assets/vfx/sky/cloud_lattice2.png")},
    "sea": {"y": arenas.ROUTE_WATER_Y, "tide_line_y": arenas.ROUTE_WATER_Y, "sea_glow": 0.0},
    "pieces": route_slabs() + [
        # Coral heads on the flats, a wreck's ribs on a hummock, the shrine on its islet on the horizon.
        (KIT + "coral_boulder_b.glb", 10.5, -8.5, 40.0, 1.0, 0.25),
        (KIT + "coral_boulder_a.glb", 9.2, -10.2, 160.0, 0.9, 0.1),
        (KIT + "coral_boulder_c.glb", 13.5, -15.0, 75.0, 1.0, 0.4),
        (KIT + "coral_boulder_a.glb", -12.5, -12.5, 20.0, 1.1, 0.12),
        (KIT + "coral_boulder_c.glb", -15.5, -14.5, 210.0, 0.9, 0.35),
        (KIT + "coral_boulder_c.glb", 6.0, -29.0, 130.0, 1.2, 0.4),
        (KIT + "coral_boulder_b.glb", -21.0, -38.0, 300.0, 1.2, 0.3),
        (KIT + "coral_boulder_c.glb", 31.0, -48.0, 15.0, 1.1, 0.4),
        (KIT + "coral_boulder_b.glb", 18.0, 2.0, 95.0, 1.0, 0.25),
        (KIT + "wreck_rib.glb", 17.0, -30.0, 65.0, 1.0, 0.12),
        (KIT + "shell_shrine_massing.glb", 97.0, -241.0, 90.0, 1.0, 0.3),
        (VEG + "palm_coconut_c.glb", 84.0, -236.0, 160.0, 1.0, 0.2),
        (VEG + "palm_coconut_a.glb", 106.0, -254.0, 200.0, 0.9, 0.2),
    ],
    "scatters": [
        ("SaltgrassHummocks", "saltgrass_a", (0.0, -18.0), (34.0, 24.0), 2200, 61, (-0.2, 3.0),
         [(-0.2, 0.3, 7.6)]),
        ("SaltgrassBar", "saltgrass_b", (0.0, 1.0), (14.0, 8.0), 700, 67, (-0.2, 3.0), [(-0.2, 0.3, 7.6)]),
        ("SaltgrassIslet", "saltgrass_b", (97.0, -241.0), (24.0, 24.0), 700, 71, (0.2, 6.0), []),
    ],
    "hints": {
        "wide_high": ((-2.0, 8.5, 15.0), (0.0, 0.0, -4.0)),
        "party_side": ((7.0, 1.6, 5.0), (-1.5, 1.2, -0.5)),
        "foe_side": ((-7.5, 1.6, 5.0), (1.5, 1.0, 0.0)),
        "from_the_causeway": ((-5.5, 1.5, -8.0), (1.5, 1.0, 1.0)),
    },
}

BS = "res://assets/environments/kits/brine_shoals/"
NIGHT_SEA = {  # the colour script's validated `night_sea` look (absorption x1.0, deep #061A2B, caustics 0.25)
    "name": "arena_night_sea", "shader": "res://game/shaders/water/water_ocean.gdshader",
    "params": [("col_deep", "#061A2B"), ("col_scatter_shallow", "#1FA3A6"),
               ("absorption_per_m", "Vector3(2, 0.5, 0.42)"), ("absorption_scale", 1.0), ("scatter_energy", 0.25),
               ("caustic_strength", 0.25), ("col_foam", "#EEF6F4"), ("col_sss", "#3FD0C9"),
               ("foam_crest_threshold", 0.62)],
}
DECK_FOREDECK_Y_M = 1.3  # bs_derelict.FOREDECK_Y_M: the raised foredeck of the Brine Shoals kit's deck
DECK_LANTERN = (0.42, 1.88)  # oil_lamp_post's lantern: local x (along its arm), height


def _deck_lamp_posts() -> tuple[list, list]:
    """The salvagers' oil-lamp posts lashed inside the bulwarks (the Haluna kit's oil_lamp_post, read-only),
    their arms reaching inboard, and the lamp at each lantern."""
    posts = ((-7.02, 3.0, 0.0), (7.02, 2.6, 180.0), (-7.02, -4.8, 0.0), (7.02, -7.6, 180.0))
    rows, lamps = [], []
    for x, z, yaw in posts:
        rows.append((KIT + "oil_lamp_post.glb", x, z, yaw, 1.0, 0.0))
        lx = x + DECK_LANTERN[0] * math.cos(math.radians(yaw))
        lamps.append({"at": (lx, DECK_LANTERN[1] - 0.12, z), "flame": True, "shadow": z > 0.0})
    return rows, lamps


DECK_POSTS, DECK_LAMPS = _deck_lamp_posts()

DERELICT_DECK = {
    "id": "derelict_deck_night",
    "sub_frame": "ch04",
    "ground": "deck",
    "ground_glb": BS + "arena_derelict_deck.glb",
    "lut": "res://assets/environments/arenas/derelict_deck_night/lut_ch04_wake.png",
    # Colour script Ch4 (night, practical-keyed): lamp key #FFB16E 1.2 in its pools, fill #2A4A6E 0.2, rim
    # #9DB4D9; exposure 1.10, sea-glow 0.12, lut_ch04_wake. The one DirectionalLight3D is the moon (#9DB4D9 at
    # 0.28, <= 2.5 x the sea-glow, rule 3 (b)); the lamps are the key.
    "sun": {"elev": 34.0, "az": 48.0, "color": "#9DB4D9", "energy": 0.28, "max_distance": 60.0, "moon": True},
    "fill": {"color": "#2A4A6E", "energy": 0.2},
    "exposure": 1.1,
    "glow": (0.6, 0.08, 0.9),
    "fog": {"color": "#22354F", "density": 0.0016, "sky_affect": 0.0, "height": 0.0, "height_density": 0.0},
    "sky_shader": "res://game/shaders/environment/env_sky_night.gdshader",
    "sky": {"col_zenith": "#0B1630", "col_horizon": "#1E2E4E", "col_ground": "#061A2B"},
    "sea": {"y": -2.2, "tide_line_y": -2.2, "sea_glow": 0.12, "material": NIGHT_SEA},
    "pieces": DECK_POSTS + [
        # The mainmast's stump, the salvagers' crates and a pile of stripped fittings on the deck.
        (BS + "wreck_mast_standing.glb", 1.3, -10.0, 25.0, 1.0, 0.0),
        (BS + "crate_stack.glb", -5.7, -6.4, 15.0, 1.0, 0.0),
        (BS + "salvage_pile.glb", 5.0, -10.4, -25.0, 1.0, 0.0),
        (BS + "crate_stack.glb", -3.4, -16.5, 70.0, 0.9, -DECK_FOREDECK_Y_M),
        # Other wrecks on the shoals around, standing out of the glowing sea.
        (BS + "wreck_bow.glb", -36.0, -64.0, 35.0, 1.0, 2.5),
        (BS + "wreck_mast_standing.glb", 27.0, -52.0, 80.0, 1.0, 2.4),
        (BS + "wreck_hull_section.glb", 58.0, -118.0, 150.0, 1.0, 2.3),
        (BS + "wreck_ribs_large.glb", -64.0, -36.0, 120.0, 1.0, 2.3),
        (BS + "wreck_mast_standing.glb", -22.0, -150.0, 300.0, 1.1, 2.4),
        (BS + "wreck_mast_fallen.glb", 40.0, -30.0, 20.0, 1.0, 2.25),
    ],
    "scatters": [],
    "lamp_spec": {"color": "#FFB16E", "energy": 2.2, "range_m": 9.0, "attenuation": 1.0, "flame_radius_m": 0.06,
                  "flame_energy": 8.0},
    "lamps": DECK_LAMPS + [
        {"at": (1.0, 2.7, -9.7), "flame": True},  # a lantern hung on the mast stump
        # Rhen's oil lantern set down on the deck behind the party, under the camera's lowest ray: the warm key
        # on the fighters' faces, throwing their shadows forward along the planks.
        {"at": (0.4, 0.45, 5.0), "flame": True, "energy": 4.0, "range": 12.0, "shadow": True},
        # The salvagers' lamp left on the hatch coaming: a pool on the planks behind the fight, so the fighters
        # stand dark against lit deck.
        {"at": (-0.6, 0.62, -5.75), "flame": True, "energy": 2.6, "range": 8.0},
    ],
    "hints": {
        "wide_high": ((-1.5, 7.5, 13.0), (0.0, 0.3, -2.0)),
        "party_side": ((6.0, 1.7, 4.5), (-1.5, 1.0, -0.5)),
        "foe_side": ((-6.0, 1.7, 4.0), (1.5, 1.0, 0.0)),
        "from_the_foredeck": ((0.5, 3.4, -13.6), (0.0, 0.8, 1.0)),
    },
}


PEM = "res://assets/environments/kits/pemakar/"
PEM_TOWN_Y_MIN_M = 2.0  # town pieces kept: the tiers above the arena's floor (arena y >= this) and the skyline
PEM_LIGHT_RADIUS_M = 30.0
PEM_FAR_MIN_Y_M = 4.0
PEM_FAR_SIZE_RANGE_M = 700.0  # pemakar_kit_preview.gd FAR_SIZE_RANGE_M: far-light radius grows to this distance
PEM_SKYLINE = ("mountain_massif", "ashcrown_silhouette", "ash_plume")


def _terrace_town() -> tuple[list, list, list]:
    """The Pemakar kit preview's town (pemakar_layout.build, read-only) placed round the arena: the two cemetery
    tiers above the floor with their walls, treads, channels, spills, graves, lamps, trees and boats, plus the
    massif, Ashcrown and the plume; the lamps near the fight; the far lights on the massif's bands."""
    import pemakar_arena as pa  # noqa: PLC0415  (the Pemakar kit, read-only)
    import pemakar_layout as pl  # noqa: PLC0415

    town = pl.build()
    turn = math.degrees(pa.axis_angle())
    pieces = []
    for p in town["pieces"]:
        at = pa.town_to_arena(p["at"])
        if at[1] < PEM_TOWN_Y_MIN_M and p["piece"] not in PEM_SKYLINE:
            continue
        pieces.append({"glb": PEM + p["piece"] + ".glb", "at": tuple(round(float(v), 3) for v in at),
                       "yaw": round(p["yaw_deg"] - turn, 3)})
    for p in town["plants"]:
        at = pa.town_to_arena(p["at"])
        if at[1] >= PEM_TOWN_Y_MIN_M:
            pieces.append({"glb": VEG + p["plant"] + ".glb", "at": tuple(round(float(v), 3) for v in at),
                           "yaw": round(p["yaw_deg"] - turn, 3), "scale": p["scale"]})
    for t in town["boats"]["transforms"]:
        at = pa.town_to_arena(t[:3])
        if at[1] >= PEM_TOWN_Y_MIN_M and abs(at[0]) < PEM_LIGHT_RADIUS_M:
            pieces.append({"glb": PEM + "leaf_boat_lit.glb", "at": tuple(round(float(v), 3) for v in at),
                           "yaw": round(math.degrees(t[3]) - turn, 2)})
    lamps = []
    for lt in town["lights"]:
        at = pa.town_to_arena(lt["at"])
        if at[1] >= PEM_TOWN_Y_MIN_M and math.hypot(at[0], at[2]) < PEM_LIGHT_RADIUS_M:
            lamps.append({"at": tuple(float(v) for v in at), "energy": lt["energy"], "range": lt["range"],
                          **({"color": lt["color"]} if lt["color"] != TERRACE_LAMP else {})})
    far = town["far_lights"]
    size0, size1 = far["size_m"]
    points = []
    for p in far["points"]:
        at = pa.town_to_arena(p)
        if at[1] < PEM_FAR_MIN_Y_M or at[2] > 0.0:
            continue
        k = min(math.hypot(p[0], p[2]) / PEM_FAR_SIZE_RANGE_M, 1.0)
        points.append((round(float(at[0]), 2), round(float(at[1]), 2), round(float(at[2]), 2),
                       round(size0 + (size1 - size0) * k, 3)))
    return pieces, lamps, points


TERRACE_LAMP = "#FFA757"  # ch05 lamp key (colour script)
# The floor's own dressing (tier ARENA_TIER's tread, arena y = 0): graves and a lamp at the back-left corner,
# graves right of the stair, and two lamp pillars at the tread's front behind the camera, whose pools light
# the fighters' faces against the dark wall.
TERRACE_FLOOR = [
    (PEM + "grave_stele_a.glb", -7.3, -3.25, 8.0, 1.0, 0.0),
    (PEM + "grave_cairn.glb", -8.7, -2.9, -12.0, 1.0, 0.0),
    (PEM + "grave_stele_b.glb", -10.3, -3.3, 4.0, 1.0, 0.0),
    (PEM + "grave_stele_a.glb", -12.1, -3.0, -20.0, 1.0, 0.0),
    (PEM + "lamp_pillar.glb", -7.7, -2.0, 0.0, 1.0, 0.0),
    (PEM + "grave_stele_a.glb", 9.4, -3.3, -6.0, 1.0, 0.0),
    (PEM + "grave_curb.glb", 11.3, -2.6, 3.0, 1.0, 0.0),
    (PEM + "grave_stele_b.glb", 13.2, -3.2, 10.0, 1.0, 0.0),
    (PEM + "lamp_pillar.glb", 8.1, 0.4, 0.0, 1.0, 0.0),
    (PEM + "lamp_pillar.glb", -5.6, 4.7, 0.0, 1.0, 0.0),
    (PEM + "lamp_pillar.glb", 6.1, 4.5, 0.0, 1.0, 0.0),
]
TERRACE_FLOOR_LAMPS = [
    {"at": (-7.7, 1.35, -2.0), "energy": 3.0, "range": 8.0, "own": True},
    {"at": (8.1, 1.35, 0.4), "energy": 3.0, "range": 7.5, "own": True},
    {"at": (-5.6, 1.55, 4.7), "energy": 5.0, "range": 11.0, "own": True},
    {"at": (6.1, 1.55, 4.5), "energy": 5.0, "range": 11.0, "own": True},
    # The boats on the floor tier's own channel, along its front behind the camera (out of frame): a low warm
    # fill on the fighters' faces.
    {"at": (0.6, 0.5, 6.4), "energy": 3.0, "range": 12.0, "shadow": True, "own": True},
]
TERRACE_VOTIVE_STEP_M = 1.45
TERRACE_VOTIVE_HALF_M = 11.5


def _terrace_votives() -> list:
    """The mourners' small oil lamps set along the foot of the grave wall behind the enemy line (a flame each,
    every other one with its own light): they wash the wall warm from below, so the fighters stand dark against
    lit stone. The stair's foot is left clear."""
    import pemakar_arena as pa  # noqa: PLC0415

    rng = np.random.default_rng(np.random.SeedSequence([6006, 5]))
    out = []
    x, k = -TERRACE_VOTIVE_HALF_M, 0
    while x < TERRACE_VOTIVE_HALF_M:
        if not pa.STAIR_X_M - 1.6 < x < pa.STAIR_X_M + 1.6:
            z = float(pa.back_z(x)) + pa.BACK_INSET_M + 0.2 + float(rng.uniform(0.0, 0.25))
            out.append({"at": (round(x, 3), 0.1, round(z, 3)), "flame": True, "light": k % 2 == 0, "energy": 1.1,
                        "range": 3.4, "own": True})
            k += 1
        x += TERRACE_VOTIVE_STEP_M + float(rng.uniform(-0.3, 0.3))
    return out


def _terrace_arena() -> dict:
    town_pieces, town_lamps, far = _terrace_town()
    return {
        "id": "ash_terrace_lanternfall",
        "sub_frame": "ch05",
        "ground": "tread",
        "ground_glb": PEM + "arena_ash_tread.glb",
        "lut": "res://assets/environments/arenas/ash_terrace_lanternfall/lut_ch05_lanternfall.png",
        # Colour script Ch5 (festival night, 20:00; pemakar.md `ch05`): lamps #FFA757 1.6 in their pools, sky
        # fill #3A4A6A 0.25, fog #5A3A2E, exposure 1.05, sea-glow 0.08, lut_ch05_lanternfall. The one
        # DirectionalLight3D is the sky fill (as the kit preview's night); the lamps are the key.
        "sun": {"elev": 55.0, "az": 200.0, "color": "#3A4A6A", "energy": 0.25, "max_distance": 60.0},
        "fill": {"color": "#3A4A6A", "energy": 0.25},
        "ambient_sky": 0.6,
        "exposure": 1.05,
        "glow": (0.9, 0.02, 1.0),
        "fog": {"color": "#5A3A2E", "light_energy": 0.15, "aerial": 0.25, "density": 0.0014, "sky_affect": 0.0,
                "height": 0.0, "height_density": 0.0},
        "sky_shader": "res://game/shaders/environment/env_sky_pemakar.gdshader",
        "sky": {"col_zenith": "#101A33", "col_horizon": "#3A2A3A", "sky_energy": 0.55, "glow_energy": 0.0,
                "haze_energy": 0.35, "star_density": 0.045, "star_energy": 1.0},
        # The sea is far below the town (behind the camera): it glows at 0.08 for the camera hints.
        "sea": {"y": -24.8, "tide_line_y": -24.8, "sea_glow": 0.08, "material": NIGHT_SEA},
        "pieces": TERRACE_FLOOR + town_pieces,
        "scatters": [],
        # The town's lamps at three times the kit preview's energy: the battle frame looks into their pools from
        # further off than the kit's shots.
        "lamp_spec": {"color": TERRACE_LAMP, "energy": 1.6, "range_m": 6.0, "attenuation": 1.0, "scale": 3.0,
                      "flame_radius_m": 0.035, "flame_energy": 6.0},
        "lamps": TERRACE_FLOOR_LAMPS + _terrace_votives() + town_lamps,
        "far_lights": {"color": TERRACE_LAMP, "energy": 3.0, "points": far},
        "hints": {
            "wide_high": ((-1.5, 7.5, 13.5), (0.0, 0.8, -3.0)),
            "party_side": ((5.5, 1.7, 5.0), (-1.5, 1.0, -0.5)),
            "foe_side": ((-6.5, 1.7, 4.5), (1.5, 1.0, 0.0)),
            "lanternfall_low": ((-2.0, 0.6, 5.5), (0.5, 2.6, -8.0)),
        },
    }


ASH_TERRACE = _terrace_arena()


# ---------------------------------------------------------------------------------------------
# M3-ENV-06 (second part): the two Ch1 arenas
# ---------------------------------------------------------------------------------------------
OU = "res://assets/environments/kits/oruvel_underway/"
UNDERWATER_DATA = ROOT / "game" / "data" / "vfx" / "underwater.json"
LUT_CH01 = "res://assets/environments/arenas/oruvel_raft_morning/lut_ch01_raft.png"
CH01_KEY = "#FFEFE1"  # colour script ch01 key and fill
CH01_FILL = "#8FC3E0"
# The Underway in arena coordinates: the kit preview's tower (ou_preview_layout, read-only) turned a quarter so its
# lamp gallery (F9) runs north-south, the camera standing in the gallery looking east down it to the breach (kit +X ->
# arena -Z, kit +Z -> arena +X), the gallery's floor at y 0. The east wall (kit x 18) stands at arena z -9.
UW_SHIFT_Z = 9.0
UW_DEPTH_M = 21.0  # water over the gallery's subject (the preview's U04): the sun and the ambient come through it
UW_LIGHT_SCALE = 0.33  # oruvel_underway.md §0 `ch01_underway_int`: in-scatter x0.33, ambient 0.22
UW_AMBIENT = 0.22
UW_LANTERN = (1.5, 1.4, 0.9)  # Rhen's lantern hand: party slot 0 (2.1, 0.7), 0.6 m off its axis towards the foe
UW_PROP_CLEAR_M = 4.0 # props (columns, coral, fragments) of the kit's gallery this near a slot are left out
UW_STRUCTURE = ("tower_bay", "tower_bay_solid", "tower_bay_broken", "tower_pier", "floor_slab", "floor_slab_broken",
                "hinge_door", "stair_flight", "current_shaft", "seafloor_patch_a", "seafloor_patch_b",
                "seafloor_edge", "sand_drift")
UW_SKIP = ("bell_room", "hull_keels", "tether_line")  # above the gallery's storeys, or the crown's


def _hex_lin(h: str) -> np.ndarray:
    c = np.array([int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5)])
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _lin_hex(lin: np.ndarray) -> str:
    c = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * np.power(np.maximum(lin, 0.0), 1.0 / 2.4) - 0.055)
    return "#" + "".join(f"{int(round(float(np.clip(v, 0.0, 1.0)) * 255.0)):02X}" for v in c)


def water_tinted(hex_color: str, metres: float) -> str:
    """A light colour after `metres` of water, with the rig's own transmittance (underwater.json `transmit` over
    `transmit_distance_m`, per channel: red goes first): the downwelling stand-in of the kit preview
    (OruvelUnderwayPreview.tinted), baked for the arena's one depth until the rig does it (M3-RND-24)."""
    data = json.loads(UNDERWATER_DATA.read_text(encoding="utf-8"))
    t = np.maximum(_hex_lin(data["colors"]["transmit"]), 1e-3)
    sigma = -np.log(t) / float(data["optics"]["transmit_distance_m"])
    return _lin_hex(_hex_lin(hex_color) * np.exp(-sigma * metres))


def _uw_layout():
    sys.path.append(str(HERE.parent / "oruvel_underway"))  # the Oruvel Underway kit's preview layout, read-only
    import ou_preview_layout as ol  # noqa: PLC0415

    return ol


def uw_to_arena(x: float, y: float, z: float) -> tuple[float, float, float]:
    """Kit preview coordinates (sea surface y 0, the gallery's floor at F9) -> the arena's."""
    ol = _uw_layout()
    return (round(z, 3), round(y - ol.F9, 3), round(UW_SHIFT_Z - x, 3))


def _near_slot(x: float, z: float, r: float) -> bool:
    return any(math.hypot(x - sx, z - sz) < r for sx, sz in arenas.SLOTS_XZ)


def _underway_pieces() -> tuple[list, list]:
    """The tower's gallery storeys (F8-F12: walls, piers, floors, the west bay's door, stair and shaft), the gallery's
    columns and growth, the breach's spill, and the terrace round it (cells, the dead ship, coral heads, the meadow,
    fragments), placed in the arena. The gallery's props within UW_PROP_CLEAR_M of a slot are left out (the fight's
    bay is the one whose columns are gone). Returns (pieces, the ones left out)."""
    ol = _uw_layout()
    terrace = ol.terrace()  # seats the ground (ground_y) for the dressing
    rows = terrace[1:] + ol.tower() + ol.dressing()
    top = ol.floor_y(12) + 0.01
    pieces, dropped = [], []
    for p in rows:
        if p["piece"] in UW_SKIP or p["y"] > top:
            continue
        x, y, z = uw_to_arena(p["at"][0], p["y"], p["at"][1])
        row = {"glb": OU + p["piece"] + ".glb", "at": (x, y, z), "yaw": round(p["yaw_deg"] + 90.0, 2)}
        if "scale" in p:
            row["scale"] = p["scale"]
        if "tilt_deg" in p:
            row["tilt"] = tuple(p["tilt_deg"])
        if p["piece"] == "floor_slab" and abs(y) < 0.01:
            row["floor"] = True  # the gallery's own floor (F9): the fighting floor
        elif p["piece"] in UW_STRUCTURE:
            row["structure"] = True
        elif abs(y) < 0.5 and _near_slot(x, z, UW_PROP_CLEAR_M):
            dropped.append(row)
            continue
        pieces.append(row)
    return pieces, dropped


UW_PIECES, UW_DROPPED = _underway_pieces()

UNDERWAY_TOWER = {
    "id": "underway_tower",
    "sub_frame": "ch01_underway_int",
    "ground": "gallery",
    # The terrace's apron (its hole round the tower) is the arena's ground; the gallery's floor is the kit's F9 slabs.
    "ground_glb": OU + "seafloor_far.glb",
    "ground_at": uw_to_arena(0.0, -22.6, 0.0),
    "lut": LUT_CH01,
    # oruvel_underway.md §0 `ch01_underway_int` (the lamp gallery): the dive's sun (08:45, 42 deg / 105 deg in the kit,
    # 15 deg here), the ch01 key #FFEFE1 3.0 and fill #8FC3E0 tinted by 21 m of water (the downwelling stand-in), the
    # ambient 0.22, the in-scatter x0.33 (ArenaUnderwater), exposure 0.65, lut_ch01_raft's intent.
    "sun": {"elev": 42.0, "az": 15.0, "color": water_tinted(CH01_KEY, UW_DEPTH_M), "energy": 3.0},
    "fill": {"color": water_tinted(CH01_FILL, UW_DEPTH_M), "energy": UW_AMBIENT},
    "exposure": 0.65,
    "fog": {"color": "#1FA3A6", "density": 0.0, "sky_affect": 0.0, "height": 0.0, "height_density": 0.0},
    "sky": {"col_zenith": "#2E7FD6", "col_horizon_sun": "#A9DCF2", "col_horizon_away": "#A9DCF2",
            "col_mid": "#A9DCF2", "col_ground": "#8FC3E0", "cloud_coverage": 0.0},
    # The lagoon's surface over the tower: the rig's water (Snell window, the waterline test) and the battle's
    # hymn_water_level publisher (everything here is under it, so wet).
    "sea": {"y": round(-_uw_layout().F9, 3), "tide_line_y": round(-_uw_layout().F9, 3), "sea_glow": 0.0},
    "pieces": UW_PIECES,
    "scatters": [],
    "underwater": {
        "light_scale": UW_LIGHT_SCALE,
        # Rhen's oil lantern (the rig hangs its oil-lamp light and halo here): at his shoulder on party slot 0, on
        # the side towards the foe and the lens, as he carries it in the field. No mesh: the battle's Rhen carries
        # the lantern; the presentation track re-targets the rig to his lamp node (M3-RND-25).
        "lantern": UW_LANTERN,
        # Held motes (glimmer_held, the colour script's ch01 energy 1.5) sinking through the gallery beyond the fight.
        "motes": [{"name": "HeldMotes", "at": (-2.6, 2.6, -5.8), "extents": (2.6, 1.6, 2.0), "amount": 0.35,
                   "seed": 106, "sea_direction": (0.0, 0.0, -1.0)}],
    },
    "hints": {
        "wide_high": ((-2.5, 5.2, 9.0), (0.5, 0.0, -3.0)),
        "party_side": ((5.0, 1.7, 4.5), (-1.5, 1.0, -0.5)),
        "foe_side": ((-5.0, 1.7, 4.0), (1.5, 1.0, 0.0)),
        "to_the_low_lights": ((0.5, 1.6, -6.5), (0.0, 1.0, 6.0)),
    },
}


RAFT_HOUSE_RIDGE = (0.0, 6.05, 1.1)  # stilt_house: the middle of its hip roof's ridge (local, measured)
RAFT_HOUSE_DECK = (2.12, 1.1)  # stilt_house: its deck's height and the deck's middle (local z), measured
RAFT_CABIN_Y = arenas.RAFT_CABIN[4]
RAFT_SHED = (2.0, 2.5, 2.3, 2.05)  # the net shed: post half-spacing x, z; the roof's eave height; its ridge above it


def _raft_house(x: float, z: float, deck_y: float, yaw: float, gull: str) -> list:
    """A cabin house (the Haluna kit's stilt_house) with its deck at `deck_y`: on a raft its stilts drop through the
    raft into the hulls, out in the lagoon (deck_y high) it stands on them; and a carved gull on its ridge."""
    a = math.radians(yaw)
    h, mid = RAFT_HOUSE_DECK
    ox, oz = x - mid * math.sin(a), z - mid * math.cos(a)  # the house's origin, so its deck is centred on (x, z)
    y = round(deck_y - h, 3)
    lx, ly, lz = RAFT_HOUSE_RIDGE
    gx, gz = ox + lx * math.cos(a) + lz * math.sin(a), oz - lx * math.sin(a) + lz * math.cos(a)
    return [{"glb": KIT + "stilt_house.glb", "at": (round(ox, 3), y, round(oz, 3)), "yaw": yaw},
            {"glb": KIT + gull + ".glb", "at": (round(gx, 3), round(y + ly, 3), round(gz, 3)), "yaw": yaw + 90.0}]


def _raft_town() -> list:
    """The town beyond the deck (the Haluna kit's pieces, read-only): cabin houses on the town's rafts (arenas.RAFT_TOWN),
    two fishing huts out on their stilts, each roof with its carved gull (act1_ch01: carved gulls on every roof); nets,
    racks, awnings, salvage and lamps on the rafts; outriggers moored alongside; the chandler's cabin raft."""
    t = arenas.RAFT_TOWN
    sea = arenas.RAFT_SEA_Y

    def mid(k: int) -> tuple[float, float, float]:
        return (t[k][0] + t[k][1]) * 0.5, t[k][4], (t[k][2] + t[k][3]) * 0.5

    rows = []
    for k, dx, yaw, gull in ((0, 0.6, 12.0, "lintel_gull_a"), (2, 0.0, 95.0, "lintel_gull_c"),
                             (3, 0.0, 40.0, "lintel_gull_b")):
        x, y, z = mid(k)
        rows += _raft_house(x + dx, z, y + 0.05, yaw, gull)
    # A net shed on the fifth raft: four lashed posts under a thatch roof, a gull on its ridge.
    ex, ey, ez = mid(4)
    for px, pz in ((-RAFT_SHED[0], -RAFT_SHED[1]), (RAFT_SHED[0], -RAFT_SHED[1]), (-RAFT_SHED[0], RAFT_SHED[1]),
                   (RAFT_SHED[0], RAFT_SHED[1])):
        rows.append({"glb": KIT + "timber_stilt_post.glb", "at": (ex + px, ey, ez + pz), "yaw": 0.0})
    rows.append({"glb": KIT + "roof_thatch_hip.glb", "at": (ex, ey + RAFT_SHED[2], ez), "yaw": 0.0})
    rows.append({"glb": KIT + "lintel_gull_c.glb", "at": (ex, ey + RAFT_SHED[2] + RAFT_SHED[3], ez), "yaw": 90.0})
    for x, z, yaw, gull in ((-46.0, -27.0, 70.0, "lintel_gull_c"), (30.0, -62.0, -40.0, "lintel_gull_b")):
        rows += _raft_house(x, z, sea + 2.3, yaw, gull)  # out in the lagoon, on their stilts
    yc = t[2][4]
    ya, yb, yd, ye = t[0][4], t[1][4], t[3][4], t[4][4]
    rows += [
        {"glb": KIT + "storehouse_stilt.glb", "at": (mid(1)[0] - 0.8, yb, mid(1)[2] - 1.2), "yaw": -15.0},
        {"glb": KIT + "net_rack.glb", "at": (-16.6, yc, -12.0), "yaw": 0.0},
        {"glb": BS + "crate_stack.glb", "at": (-23.0, yc, -6.0), "yaw": 25.0},
        {"glb": KIT + "net_rack.glb", "at": (-15.4, ya, -22.8), "yaw": 90.0},
        {"glb": KIT + "oil_lamp_post.glb", "at": (-15.0, ya, -19.0), "yaw": 180.0},
        {"glb": KIT + "awning_cloth.glb", "at": (-4.6, yb, -25.0), "yaw": -10.0},
        {"glb": KIT + "fish_drying_rack.glb", "at": (-10.6, yb, -24.6), "yaw": 0.0},
        {"glb": KIT + "basket_set.glb", "at": (-22.0, yd, -32.0), "yaw": 15.0},
        {"glb": BS + "salvage_pile.glb", "at": (3.4, ye, -29.6), "yaw": 30.0},
        {"glb": KIT + "outrigger_7m.glb", "at": (9.3, sea, 2.5), "yaw": 91.0},
        {"glb": KIT + "outrigger_7m.glb", "at": (-9.6, sea, -6.5), "yaw": 96.0},
        {"glb": KIT + "outrigger_7m.glb", "at": (-1.0, sea, -28.0), "yaw": 170.0},
        {"glb": KIT + "outrigger_7m.glb", "at": (9.3, arenas.RAFT_SEA_Y, 2.5), "yaw": 91.0},
        {"glb": KIT + "outrigger_7m.glb", "at": (-9.6, arenas.RAFT_SEA_Y, -6.5), "yaw": 96.0},
        # The chandler's cabin raft: a stall under an awning, a lamp post, jars, baskets and a drying rack.
        {"glb": KIT + "market_stall.glb", "at": (-8.2, RAFT_CABIN_Y, -16.4), "yaw": 0.0},
        {"glb": KIT + "awning_cloth.glb", "at": (-8.2, RAFT_CABIN_Y, -14.3), "yaw": 0.0},
        {"glb": KIT + "oil_lamp_post.glb", "at": (-4.3, RAFT_CABIN_Y, -13.3), "yaw": 180.0},
        {"glb": KIT + "water_jar.glb", "at": (-5.2, RAFT_CABIN_Y, -17.9), "yaw": 30.0},
        {"glb": KIT + "basket_set.glb", "at": (-11.2, RAFT_CABIN_Y, -13.8), "yaw": 70.0},
        {"glb": KIT + "fish_drying_rack.glb", "at": (-11.4, RAFT_CABIN_Y, -17.2), "yaw": 90.0},
    ]
    return rows


RAFT_MORNING = {
    "id": "oruvel_raft_morning",
    "sub_frame": "ch01",
    "ground": "raft",
    "ground_glb": KIT + "arena_raft_deck.glb",
    "lut": LUT_CH01,
    # Colour script ch01 (10:30, the raft-town): sun 58 deg / 120 deg, key #FFEFE1 3.0, fill #8FC3E0 (the sky's own
    # radiance, 0.6), exposure 0.65, saturation x1.12 in lut_ch01_raft; the brightest frame so far. The noon cumulus sky.
    "sun": {"elev": 58.0, "az": 120.0, "color": CH01_KEY, "energy": 3.0},
    "fill": {"color": CH01_FILL, "energy": 0.6},
    "ambient_sky": 0.6,
    "exposure": 0.65,
    "fog": {"color": "#BFDDE8", "density": 0.0008, "sky_affect": 0.0, "height": 0.0, "height_density": 0.0},
    "sky_shader": "res://game/shaders/environment/env_sky_cumulus.gdshader",
    "sky": {"background_energy": 1.5, "horizon_curve": 0.14,
            "cloud_lattice": ("Texture3D", "res://assets/vfx/undertow/undertow_noise3d.png"),
            "cloud_lattice2": ("Texture2D", "res://assets/vfx/sky/cloud_lattice2.png")},
    "sea": {"y": arenas.RAFT_SEA_Y, "tide_line_y": arenas.RAFT_SEA_Y, "sea_glow": 0.0},
    "pieces": [
        # The deck's working clutter, beyond the fight: nets drying, floats, salvage crates, a jar and baskets.
        (KIT + "net_rack.glb", -5.6, -5.8, 90.0, 1.0, 0.0),
        (KIT + "net_float_cluster.glb", -5.7, -7.0, 20.0, 1.0, 0.0),
        (KIT + "oil_lamp_post.glb", -6.0, 3.6, 0.0, 1.0, 0.0),
        (BS + "crate_stack.glb", 5.3, -6.2, 10.0, 0.9, 0.0),
        (KIT + "basket_set.glb", 4.3, -6.9, 40.0, 1.0, 0.0),
        (KIT + "water_jar.glb", 5.6, -4.6, 0.0, 1.0, 0.0),
    ] + _raft_town(),
    "scatters": [],
    "hints": {
        "wide_high": ((-1.5, 7.5, 13.5), (0.0, 0.3, -3.0)),
        "party_side": ((5.6, 1.7, 4.5), (-1.5, 1.0, -0.5)),
        "foe_side": ((-5.6, 1.7, 4.0), (1.5, 1.0, 0.0)),
        "from_the_bridge": ((-4.6, 1.6, -10.2), (1.0, 1.0, 1.0)),
    },
}


ARENAS = {a["id"]: a for a in (TIDELINE, CAUSEWAY, CAUSEWAY_ROUTE, DERELICT_DECK, ASH_TERRACE, UNDERWAY_TOWER,
                               RAFT_MORNING)}


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


def _value(sc: Scene, v) -> str:
    """A table value as .tscn text: '#RRGGBB' -> Color, (kind, res://path) -> ExtResource, numbers as they are."""
    if isinstance(v, str):
        return hexc(v) if v.startswith("#") else v
    if isinstance(v, tuple):
        return f'ExtResource("{sc.res(v[0], v[1])}")'
    return str(v)


def _xyz(p) -> str:
    return f"Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {p[0]}, {p[1]}, {p[2]})"


def write_arena(a: dict) -> Path:
    sc = Scene()
    script = sc.res("Script", "res://game/world/arenas/battle_arena_root.gd")
    sky_shader = sc.res("Shader", a.get("sky_shader", LOW_SUN_SKY))
    lut = sc.res("Texture3D", a["lut"])
    sky_params = "\n".join(f"shader_parameter/{k} = {_value(sc, v)}" for k, v in sorted(a["sky"].items()))
    sc.sub.append(f'[sub_resource type="ShaderMaterial" id="SkyMat"]\nshader = ExtResource("{sky_shader}")\n'
                  + sky_params)
    sc.sub.append('[sub_resource type="Sky" id="Sky"]\nsky_material = SubResource("SkyMat")\nprocess_mode = 2')
    fog = a["fog"]
    glow = a.get("glow", (0.35, 0.03, 1.2))
    if "ambient_sky" in a:  # the sky's radiance as ambient (the night skies), at this energy
        ambient = ["ambient_light_source = 3", f"ambient_light_energy = {a['ambient_sky']}"]
    else:
        ambient = ["ambient_light_source = 2", f"ambient_light_color = {hexc(a['fill']['color'])}",
                   f"ambient_light_energy = {a['fill']['energy']}"]
    fog_extra = [f"fog_light_energy = {fog['light_energy']}"] if "light_energy" in fog else []
    fog_extra += [f"fog_aerial_perspective = {fog['aerial']}"] if "aerial" in fog else []
    sc.sub.append("\n".join([
        '[sub_resource type="Environment" id="Env"]',
        f'resource_name = "{a["id"]}_{a["sub_frame"]}"',
        "background_mode = 2", 'sky = SubResource("Sky")',
        *ambient, "reflected_light_source = 2",
        "tonemap_mode = 4", f"tonemap_exposure = {a['exposure']}", "tonemap_agx_white = 12.0",
        "ssao_enabled = true", "ssao_radius = 1.2", "ssao_intensity = 1.2",
        "glow_enabled = true", f"glow_intensity = {glow[0]}", f"glow_bloom = {glow[1]}",
        f"glow_hdr_threshold = {glow[2]}",
        "fog_enabled = true", "fog_mode = 0", f"fog_light_color = {hexc(fog['color'])}",
        *fog_extra,
        f"fog_density = {fog['density']}", f"fog_sky_affect = {fog['sky_affect']}",
        f"fog_height = {fog['height']}", f"fog_height_density = {fog['height_density']}",
        "adjustment_enabled = true", f'adjustment_color_correction = ExtResource("{lut}")',
        *([f"adjustment_saturation = {a['saturation']}"] if "saturation" in a else []),
    ]))
    sc.node(a["id"].title().replace("_", ""), "Node3D", None,
            {"script": f'ExtResource("{script}")', "arena_id": f'&"{a["id"]}"', "sub_frame": f'&"{a["sub_frame"]}"'})
    sc.node("WorldEnvironment", "WorldEnvironment", ".", {"environment": 'SubResource("Env")'})
    s = a["sun"]
    sc.node("Sun", "DirectionalLight3D", ".", {
        "transform": sun_xform(s["elev"], s["az"]), "light_color": hexc(s["color"]), "light_energy": s["energy"],
        "shadow_enabled": "true", "shadow_bias": 0.03, "shadow_normal_bias": 1.0, "shadow_blur": 1.0,
        "directional_shadow_mode": 2, "directional_shadow_split_1": 0.06, "directional_shadow_split_2": 0.18,
        "directional_shadow_split_3": 0.45, "directional_shadow_max_distance": s.get("max_distance", 120.0)})
    sea = a["sea"]
    sea_props = {
        "transform": f"Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, {sea['y']}, 0)",
        "script": f'ExtResource("{sc.res("Script", "res://game/world/arenas/arena_sea.gd")}")',
        "wave_set": f'ExtResource("{sc.res("Resource", WAVES)}")'}
    if "material" in sea:  # the arena's own water look: the shared ocean shader with this table's values
        m = sea["material"]
        params = "\n".join(f"shader_parameter/{k} = {_value(sc, v)}" for k, v in m["params"])
        sc.sub.append(f'[sub_resource type="ShaderMaterial" id="SeaMat"]\nresource_name = "{m["name"]}"\n'
                      f'render_priority = 0\nshader = ExtResource("{sc.res("Shader", m["shader"])}")\n' + params)
        sea_props["material"] = 'SubResource("SeaMat")'
    else:
        sea_props["material"] = f'ExtResource("{sc.res("Material", WATER_MAT)}")'
    sea_props.update({"sea_glow_energy": sea["sea_glow"], "tide_line_y": sea["tide_line_y"]})
    sc.node("Sea", "Node3D", ".", sea_props)
    ground_props = {}
    if "ground_at" in a:  # the ground glb placed off the origin (the Underway's terrace apron)
        ground_props["transform"] = _xyz(a["ground_at"])
    sc.node("Ground", None, ".", ground_props, instance=sc.res("PackedScene", a["ground_glb"]))
    if "disc" in a:
        cx, cz = a["disc"]["center"]
        sc.node("Disc", None, ".", {"transform": f"Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {cx}, 0, {cz})"},
                instance=sc.res("PackedScene", a["disc"]["glb"]))
    for k, glb in enumerate(a.get("extra_glbs", [])):
        sc.node(f"Kit{k}", None, ".", {}, instance=sc.res("PackedScene", glb))
    sc.node("Dressing", "Node3D", ".", {})
    counts: dict[str, int] = {}
    for row in a["pieces"]:
        tilt = None
        if isinstance(row, dict):  # an explicit placement: {"glb", "at": (x, y, z), "yaw", "scale", "tilt"}
            glb, (x, y, z), yaw, scale = row["glb"], row["at"], row["yaw"], row.get("scale", 1.0)
            tilt = row.get("tilt")
        else:  # (glb, x, z, yaw_deg, scale, sink_m): standing on the arena's ground
            glb, x, z, yaw, scale, sink = row
            y = height(a["ground"], float(x), float(z)) - sink
        stem = Path(glb).stem
        counts[stem] = counts.get(stem, 0) + 1
        pos = (float(x), round(float(y), 3), float(z))
        xf = yaw_xform(yaw, pos, scale) if tilt is None else tilt_xform(yaw, tilt, pos, scale)
        sc.node(f"{stem}_{counts[stem]}", None, "Dressing", {"transform": xf}, instance=sc.res("PackedScene", glb))
    if a["scatters"]:
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
    _write_lamps(sc, a)
    _write_far_lights(sc, a)
    _write_underwater(sc, a)
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


def _write_lamps(sc: Scene, a: dict) -> None:
    """Practical lights (`lamps`: oil lamps, the festival's lamps): an OmniLight3D each, plus a small emissive
    flame where the lamp's kit piece has none of its own. They are tier 1 of the night value order."""
    lamps = a.get("lamps")
    if not lamps:
        return
    spec = a["lamp_spec"]
    if any(lp.get("flame", False) for lp in lamps):
        sc.sub.append("\n".join([
            '[sub_resource type="StandardMaterial3D" id="FlameMat"]', "shading_mode = 0",
            f"albedo_color = {hexc(spec['color'])}", "emission_enabled = true", f"emission = {hexc(spec['color'])}",
            f"emission_energy_multiplier = {spec['flame_energy']}"]))
        r = spec["flame_radius_m"]
        sc.sub.append("\n".join([
            '[sub_resource type="SphereMesh" id="FlameMesh"]', 'material = SubResource("FlameMat")',
            f"radius = {r}", f"height = {round(r * 2.4, 4)}", "radial_segments = 12", "rings = 6"]))
    sc.node("Lamps", "Node3D", ".", {})
    scale = spec.get("scale", 1.0)  # the arena's lamp scale (a mood's lamp_scale)
    for k, lp in enumerate(lamps):
        at = tuple(round(float(v), 3) for v in lp["at"])
        energy = round(lp.get("energy", spec["energy"]) * (1.0 if lp.get("own", False) else scale), 3)
        props = {"transform": _xyz(at), "light_color": hexc(lp.get("color", spec["color"])),
                 "light_energy": energy, "omni_range": lp.get("range", spec["range_m"]),
                 "omni_attenuation": spec["attenuation"]}
        if "fog_energy" in spec:  # the Lead's rule near a dense FogVolume (the rig's god rays): 0
            props["light_volumetric_fog_energy"] = spec["fog_energy"]
        if lp.get("shadow", False):
            props["shadow_enabled"] = "true"
            props["shadow_bias"] = 0.05
        if lp.get("light", True):  # a votive's flame alone (`light` false) has no light of its own
            sc.node(f"Lamp{k}", "OmniLight3D", "Lamps", props)
        if lp.get("flame", False):
            sc.node(f"Flame{k}", "MeshInstance3D", "Lamps", {"transform": _xyz(at), "cast_shadow": 0,
                                                             "mesh": 'SubResource("FlameMesh")'})


def _write_far_lights(sc: Scene, a: dict) -> None:
    """Lights too small to model at their range (the festival's boats on the far terrace bands): one MultiMesh
    of camera-facing quads (env_far_lights.gdshader); an instance's scale is its radius."""
    far = a.get("far_lights")
    if not far:
        return
    shader = sc.res("Shader", FAR_LIGHT_SHADER)
    sc.sub.append("\n".join([
        '[sub_resource type="ShaderMaterial" id="FarLightMat"]', f'shader = ExtResource("{shader}")',
        f"shader_parameter/col_light = {hexc(far['color'])}", f"shader_parameter/energy = {far['energy']}"]))
    sc.sub.append('[sub_resource type="QuadMesh" id="FarLightQuad"]\nmaterial = SubResource("FarLightMat")\n'
                  "size = Vector2(2, 2)")
    buf: list[float] = []
    for x, y, z, r in far["points"]:
        buf += [r, 0.0, 0.0, x, 0.0, r, 0.0, y, 0.0, 0.0, r, z]
    sc.sub.append("\n".join([
        '[sub_resource type="MultiMesh" id="FarLightSet"]', "transform_format = 1",
        f"instance_count = {len(far['points'])}", 'mesh = SubResource("FarLightQuad")',
        "buffer = PackedFloat32Array(" + ", ".join(f"{float(v):.6g}" for v in buf) + ")"]))
    sc.node("FarLights", "MultiMeshInstance3D", ".", {"cast_shadow": 0, "multimesh": 'SubResource("FarLightSet")'})


UNDERWATER_RIG = "res://game/world/arenas/arena_underwater.gd"
GLIMMER_FIELD = "res://game/vfx/glimmer/glimmer_field.gd"


def _write_underwater(sc: Scene, a: dict) -> None:
    """An arena under the sea (`underwater`): `Lantern`, where Rhen's lantern hangs (a bare Node3D: the rig hangs its
    oil-lamp light on it), the underwater look (ArenaUnderwater: the rig with the arena's in-scatter scale) on the
    arena's Sea, and held glimmer fields at their own colour-script energy (not the scene's hymn_glimmer gate, which
    a day scene keeps shut)."""
    uw = a.get("underwater")
    if not uw:
        return
    sc.node("Lantern", "Node3D", ".", {"transform": _xyz(uw["lantern"])})
    field = sc.res("Script", GLIMMER_FIELD)
    for m in uw.get("motes", []):
        ex, sd = m["extents"], m["sea_direction"]
        sc.node(m["name"], "Node3D", ".", {
            "transform": _xyz(m["at"]), "script": f'ExtResource("{field}")', "mode": 0,
            "emission_extents_m": f"Vector3({ex[0]}, {ex[1]}, {ex[2]})", "amount_multiplier": m["amount"],
            "sea_direction": f"Vector3({sd[0]}, {sd[1]}, {sd[2]})", "water_height_m": a["sea"]["y"],
            "follow_scene_intensity": "false", "use_fixed_seed": "true", "fixed_seed": m["seed"]})
    sc.node("Underwater", "Node3D", ".", {
        "script": f'ExtResource("{sc.res("Script", UNDERWATER_RIG)}")', "water": 'NodePath("../Sea")',
        "lantern_target": 'NodePath("../Lantern")', "light_scale": uw["light_scale"]},
        node_paths=("water", "lantern_target"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--arena", action="append", choices=sorted(ARENAS))
    args = ap.parse_args(argv)
    for aid in args.arena or sorted(ARENAS):
        print(f"ARENA {write_arena(ARENAS[aid]).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
