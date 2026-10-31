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
sys.path.append(str(HERE.parent / "brine_shoals"))  # the Brine Shoals arena grounds, read-only (M3-ENV-706)

OUT_DIR = ROOT / "assets" / "environments" / "arenas"
KIT = "res://assets/environments/kits/haluna/"
FLAME_KIT_RADIUS_M = 0.06  # props.build_lamp_flame's radius: an arena scales the kit flame to its lamp_spec's
FLAME_KIT_COLOURS = {"#FFB16E", "#FFA757"}  # the oil flames lamp_flame (kit_lamp_flame_hot) stands in for
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
    if name in ("shoals", "camp"):  # M3-ENV-706: the Brine Shoals kit's arena grounds (bs_arenas.py, read-only)
        import bs_arenas  # noqa: PLC0415

        key, seed, fn = (("arena_shoals_ground", 741, bs_arenas.shoals_height) if name == "shoals"
                         else ("arena_camp_ground", 742, bs_arenas.camp_height))
        return fn(kc.Noise3(kc.rng_for(key, seed)))
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
        # M3-ENV-701 set dressing: the tide's wrack along the beach, gear by the outrigger, an offering at the
        # first pilgrim post.
        (KIT + "tide_debris.glb", 3.5, -9.0, 100.0, 1.0, 0.04),
        (KIT + "tide_debris.glb", 9.0, -30.0, 70.0, 1.0, 0.04),
        (KIT + "tide_debris.glb", 13.0, -62.0, 115.0, 1.1, 0.04),
        (KIT + "net_heap.glb", -11.5, -13.5, 30.0, 1.0, 0.04),
        (KIT + "rope_coil.glb", -6.0, -13.0, 0.0, 1.0, 0.0),
        (KIT + "crate_stack.glb", -13.0, -5.5, 80.0, 1.0, 0.05),
        (KIT + "basket_set.glb", -11.8, -7.6, 20.0, 1.0, 0.02),
        (KIT + "offering_step.glb", 5.2, -21.0, 190.0, 1.0, 0.03),
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

# M3-ENV-701: rows set ON the disc's paving (top y 0) sink by the ground below it (the flats under the disc,
# -1.2 m), i.e. are raised to the slab tops.
DISC_TOP_SINK = -1.2

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
        # M3-ENV-701 set dressing: offerings left at the rim posts (the last pilgrims came this far), a lost
        # net and coils on the paving's edge, the wrack and a stove-in crate stack on the flats.
        (KIT + "offering_step.glb", *arenas.disc_xz(13.3, math.radians(84.0)), 0.0, 1.0, DISC_TOP_SINK),
        (KIT + "offering_step.glb", *arenas.disc_xz(13.4, math.radians(60.0)), -30.0, 1.0, DISC_TOP_SINK),
        (KIT + "net_heap.glb", *arenas.disc_xz(12.8, math.radians(112.0)), 40.0, 0.9, DISC_TOP_SINK),
        (KIT + "rope_coil.glb", *arenas.disc_xz(13.4, math.radians(99.0)), 0.0, 1.0, DISC_TOP_SINK),
        (KIT + "rope_coil.glb", *arenas.disc_xz(12.9, math.radians(40.0)), 0.0, 0.9, DISC_TOP_SINK),
        (KIT + "tide_debris.glb", *arenas.disc_xz(11.5, math.radians(150.0)), 100.0, 0.9, DISC_TOP_SINK - 0.02),
        (KIT + "tide_debris.glb", -7.0, -26.0, 10.0, 1.1, 0.1),
        (KIT + "tide_debris.glb", 9.0, -28.0, 165.0, 1.0, 0.1),
        (KIT + "tide_debris.glb", -20.0, -12.0, 60.0, 1.0, 0.1),
        (KIT + "crate_stack.glb", -15.0, -27.0, 35.0, 1.0, 0.35),
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
# The skyline pieces kept whatever their height. Ashcrown on the rim (300 m up) is the Ashcrown kit's own pieces in
# the town layout (M3-ENV-09B; each names its kit_dir), and at the arena's 650 m their import chain draws LOD1.
PEM_SKYLINE = ("mountain_massif", "ash_plume")


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
        pieces.append({"glb": p.get("kit_dir", PEM) + p["piece"] + ".glb",
                       "at": tuple(round(float(v), 3) for v in at), "yaw": round(p["yaw_deg"] - turn, 3)})
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


PEMAKAR_VOTIVE = "res://assets/environments/kits/pemakar/votive_lamp.glb"
VOTIVE_YAW_SPREAD_DEG = 25.0  # the spouts face the fight, each set down by hand


def _with_votive_lamps(table: dict) -> dict:
    """env-art-b's votive lamps (M3-ENV-1305/1306; b_lanternfall.py's arena(), the same rows in the same order): each
    votive row keeps its light but draws no writer flame, and a kit `votive_lamp` (b_votive.py) stands under it.
    `arena_scenes.py` writes the arena with them, so b_lanternfall.py's write and this one are the same file."""
    votives = {tuple(v["at"]) for v in _terrace_votives()}
    rng = np.random.default_rng(np.random.SeedSequence([6006, 51]))
    lamps, pieces = [], list(table["pieces"])
    for lp in table["lamps"]:
        if tuple(lp["at"]) in votives:
            lp = {**lp, "flame": False}
            x, _, z = lp["at"]
            yaw = round(float(rng.uniform(-VOTIVE_YAW_SPREAD_DEG, VOTIVE_YAW_SPREAD_DEG)), 2)
            # At the grave wall's foot, the floor's edge (the writer's flames stood there): a structure's clearance.
            pieces.append({"glb": PEMAKAR_VOTIVE, "at": (x, 0.0, z), "yaw": yaw, "structure": True})
        lamps.append(lp)
    return {**table, "lamps": lamps, "pieces": pieces}


ASH_TERRACE = _with_votive_lamps(_terrace_arena())


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
    # The sun through 21 m of water arrives soft (M3-ENV-1323, the GPU QA's rows 15 and 40: the windows' light lay on
    # the floor as hard-edged rectangles).
    "sun": {"elev": 42.0, "az": 15.0, "color": water_tinted(CH01_KEY, UW_DEPTH_M), "energy": 3.0, "angular_deg": 9.0,
            "shadow_blur": 4.0},
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


OV = "res://assets/environments/kits/oruvel/"
RAFT_CABIN_Y = arenas.RAFT_CABIN[4]
RAFT_GULL_YAW = -70.0  # the Oruvel kit's rule (oruvel.md §0): every carved gull faces the sea, south-south-east


def _ov():
    """The Oruvel raft-town kit's cabin constants (M3-ENV-07), read-only."""
    sys.path.append(str(HERE.parent / "oruvel"))
    import ov_cabins  # noqa: PLC0415
    import ov_common  # noqa: PLC0415

    return ov_cabins, ov_common


def _rot(x: float, z: float, yaw: float, lx: float, lz: float) -> tuple[float, float]:
    a = math.radians(yaw)
    return round(x + lx * math.cos(a) + lz * math.sin(a), 3), round(z - lx * math.sin(a) + lz * math.cos(a), 3)


def _ov_cabin(kind: str, x: float, z: float, deck_y: float, yaw: float, jitter: float) -> list:
    """An Oruvel cabin standing on a town raft's deck and the open-throat gull on its ridge: a keel-roof's at the
    keel's south end, a patched cabin's on its high back edge."""
    ocab, ocom = _ov()
    rows = [{"glb": OV + kind + ".glb", "at": (x, round(deck_y, 3), z), "yaw": yaw}]
    if kind == "cabin_keelroof":
        length, _beam, depth, eave, sheer = ocab.KEELROOF
        gz = ocab.KEELROOF_GULL_Z if math.cos(math.radians(yaw)) >= 0.0 else -ocab.KEELROOF_GULL_Z
        gx, gzw = _rot(x, z, yaw, 0.0, gz)
        gy = deck_y + ocom.keel_roof_ridge(gz, length, depth, eave, sheer)
    else:
        gx, gzw = _rot(x, z, yaw, -1.85, 0.0)
        gy = deck_y + 3.12
    rows.append({"glb": OV + "lintel_gull_open.glb", "at": (gx, round(gy, 3), gzw), "yaw": RAFT_GULL_YAW + jitter})
    return rows


def _raft_town() -> list:
    """The town beyond the deck, from the Oruvel raft-town kit (M3-ENV-07, read-only): keel-roof and patched cabins
    on the town's rafts (arenas.RAFT_TOWN), each with its open-throat gull facing the sea; net frames, stalls and
    salvage on the rafts; outriggers and cabin hulls moored round; the chandler's cabin raft with its stall; the far
    town past the lagoon."""
    t = arenas.RAFT_TOWN
    sea = arenas.RAFT_SEA_Y

    def mid(k: int) -> tuple[float, float, float]:
        return (t[k][0] + t[k][1]) * 0.5, t[k][4], (t[k][2] + t[k][3]) * 0.5

    rows = []
    for k, kind, dx, yaw, jit in ((0, "cabin_keelroof", 0.4, 12.0, 4.0), (2, "cabin_keelroof", 0.0, 95.0, -5.0),
                                  (3, "cabin_patched", 0.0, 40.0, 6.0), (1, "cabin_patched", -0.8, -15.0, -3.0)):
        x, y, z = mid(k)
        rows += _ov_cabin(kind, x + dx, z, y, yaw, jit)
    ex, ey, ez = mid(4)
    ya, yb, yc, yd = t[0][4], t[1][4], t[2][4], t[3][4]
    rows += [
        {"glb": OV + "net_frame.glb", "at": (ex - 2.0, ey, ez), "yaw": 0.0},
        {"glb": OV + "net_frame.glb", "at": (ex + 1.6, ey, ez + 0.5), "yaw": 0.0},
        {"glb": OV + "stall_awning.glb", "at": (ex + 2.4, ey, ez - 2.6), "yaw": 180.0},
        {"glb": OV + "net_frame.glb", "at": (-16.8, yc, -11.4), "yaw": 90.0},
        {"glb": OV + "salvage_heap.glb", "at": (-22.6, yc, -6.4), "yaw": 25.0},
        {"glb": OV + "net_frame.glb", "at": (-15.6, ya, -22.4), "yaw": 0.0},
        {"glb": OV + "stall_awning.glb", "at": (-4.4, yb, -25.6), "yaw": 170.0},
        {"glb": OV + "salvage_heap.glb", "at": (-22.4, yd, -33.0), "yaw": 15.0},
        {"glb": OV + "salvage_heap.glb", "at": (3.6, t[4][4], -30.0), "yaw": 30.0},
        # Moored round the deck and the town (the kit's hulls run along their local Z: the Haluna outrigger's yaw
        # less 90).
        {"glb": OV + "hull_outrigger.glb", "at": (9.3, sea, 2.5), "yaw": 1.0},
        {"glb": OV + "hull_outrigger.glb", "at": (-9.6, sea, -6.5), "yaw": 6.0},
        {"glb": OV + "hull_outrigger.glb", "at": (-1.0, sea, -28.0), "yaw": 80.0},
        {"glb": OV + "hull_cabin.glb", "at": (-46.0, sea, -27.0), "yaw": 20.0},
        {"glb": OV + "hull_cabin.glb", "at": (30.0, sea, -62.0), "yaw": -40.0},
        {"glb": OV + "town_far.glb", "at": (-34.0, sea, -76.0), "yaw": 8.0},
        {"glb": OV + "town_far.glb", "at": (36.0, sea, -86.0), "yaw": -18.0},
    ]
    # The chandler's cabin raft: a keel-roof cabin along it, its stall facing the bridge from the deck.
    rows += _ov_cabin("cabin_keelroof", -8.4, -16.4, RAFT_CABIN_Y, 90.0, 2.0)
    rows += [{"glb": OV + "stall_awning.glb", "at": (-6.6, RAFT_CABIN_Y, -13.9), "yaw": 100.0},
             {"glb": OV + "salvage_heap.glb", "at": (-11.4, RAFT_CABIN_Y, -13.8), "yaw": 70.0}]
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


# ---------------------------------------------------------------------------------------------
# M3-ENV-706: Ch6's two arenas from the Brine Shoals kit (M3-BPR-03's greybox ids)
# ---------------------------------------------------------------------------------------------
SILTED_FLATS = {  # the colour script's validated `silted_flats` look (brine_shoals_water_material.tres's values)
    "name": "arena_silted_flats", "shader": "res://game/shaders/water/water_ocean.gdshader",
    "params": [("col_deep", "#4A5A50"), ("col_scatter_shallow", "#6E7A62"),
               ("absorption_per_m", "Vector3(2, 0.6, 0.546)"), ("absorption_scale", 3.5), ("scatter_energy", 0.25),
               ("caustic_strength", 0.0), ("col_foam", "#EEF6F4"), ("col_sss", "#7A8A6A"),
               ("foam_crest_threshold", 0.95), ("use_foam", "false"), ("use_sss", "false"), ("glint_strength", 0.35)],
}
CH06_LIGHT = {  # color_script.md ch06 (15:30, haze and smoke): sun 35 / 240, key, fill, sky, fog, exposure, sat
    "sub_frame": "ch06",
    "sun": {"elev": 35.0, "az": 240.0, "color": "#FFD5B3", "energy": 2.4},
    "fill": {"color": "#A8B8B0", "energy": 0.55},
    "exposure": 0.7,
    "saturation": 0.9,
    "fog": {"color": "#B8A890", "density": 0.0022, "sky_affect": 0.12, "height": 0.0, "height_density": 0.0},
    "sky": {"col_zenith": "#7FA3C0", "col_horizon_sun": "#E8C9A0", "col_horizon_away": "#D8C8A8",
            "col_mid": "#C8B8A0", "mid_strength": 0.35, "mid_height": 0.1, "mid_width": 0.1,
            "col_ground": "#5A5A50", "col_band": "#E8C090", "band_energy": 0.4, "band_height": 0.05,
            "col_glow": "#FFD5B3", "glow_energy": 1.0, "glow_power": 5.0, "halo_energy": 2.0,
            "col_cloud_lit": "#E8D0B0", "col_cloud_shadow": "#7A7E84", "cloud_coverage": 0.55,
            "cloud_sun_energy": 2.0, "cloud_ambient_energy": 0.8, "cloud_wind_deg": 240.0, "horizon_curve": 0.5,
            "azimuth_power": 1.0},
}
SMOKE_TINT = "#3C3C3A"

SHOALS = {
    "id": "brine_shoals_afternoon",
    **CH06_LIGHT,
    "ground": "shoals",
    "ground_glb": BS + "arena_shoals_ground.glb",
    "lut": "res://assets/environments/arenas/brine_shoals_afternoon/lut_ch06_smoke.png",
    "sea": {"y": -0.15, "tide_line_y": -0.15, "sea_glow": 0.0, "material": SILTED_FLATS},
    "pieces": [
        # The wreck-ridges either side: black hulls stranded on their grit, a fallen mast across the left one.
        (BS + "wreck_bow.glb", -27.0, -26.0, 55.0, 1.0, 0.1),
        (BS + "wreck_mast_fallen.glb", -19.0, -19.0, 20.0, 1.0, 0.05),
        (BS + "wreck_hull_section.glb", 30.0, -36.0, 205.0, 1.0, 0.1),
        (BS + "wreck_ribs_large.glb", 17.0, -22.0, 140.0, 1.0, 0.15),
        (BS + "wreck_mast_standing.glb", 34.0, -42.0, 15.0, 1.0, 0.0),
        # The route goes on north between them: the plank walk, a wrack line, a drowned lamp, chalk on a hull.
        (BS + "plank_walk.glb", 1.5, -16.0, 8.0, 1.0, 0.0),
        (BS + "plank_walk.glb", 2.2, -20.0, 12.0, 1.0, 0.0),
        (BS + "plank_walk.glb", 3.0, -24.0, 6.0, 1.0, 0.0),
        (BS + "tideline_wrack.glb", -12.0, -13.0, 75.0, 1.0, 0.0),
        (BS + "tideline_wrack.glb", 13.5, -10.0, 110.0, 1.0, 0.0),
        (BS + "lamp_burial.glb", -15.0, -6.0, 30.0, 1.0, 0.0),
        # What the raid left strewn across the flats behind the foes (the PC render at 71f19fbc read as bare sand):
        # a skiff stranded on its side, salvage dropped in the run, nets and coils, wet mud patches.
        (BS + "vendor_boat.glb", -21.0, -12.0, 115.0, 1.0, 0.25),
        (BS + "crate_stack.glb", -9.0, -12.5, 30.0, 1.0, 0.05),
        (BS + "salvage_pile.glb", 9.0, -19.0, 200.0, 1.0, 0.1),
        (BS + "mudflat_patch_a.glb", -7.0, -5.0, 20.0, 1.0, 0.0),
        (BS + "mudflat_patch_b.glb", 13.0, -16.0, 70.0, 1.0, 0.0),
        (KIT + "net_heap.glb", 11.5, -12.0, 40.0, 1.0, 0.05),
        (KIT + "tide_debris.glb", -5.0, -9.0, 80.0, 1.0, 0.0),
        (KIT + "tide_debris.glb", 6.0, -9.5, 200.0, 1.0, 0.0),
        (KIT + "rope_coil.glb", 4.0, -14.0, 0.0, 1.0, 0.0),
        (KIT + "cargo_sacks.glb", -12.5, -16.5, 150.0, 1.0, 0.05),
        (BS + "wreck_mast_standing.glb", -32.0, -58.0, 40.0, 0.9, 0.2),
        # Far off: more wrecks out on the flats, and the burning camp's smoke leaning away.
        (BS + "wreck_ribs_large.glb", -60.0, -80.0, 30.0, 1.2, 0.3),
        (BS + "wreck_bow.glb", 52.0, -95.0, 250.0, 1.1, 0.3),
        (BS + "wreck_mast_standing.glb", -8.0, -120.0, 70.0, 1.0, 0.1),
        (BS + "smoke_plume.glb", 26.0, -140.0, 0.0, 1.4, 0.0),
        (BS + "smoke_plume.glb", 36.0, -150.0, 20.0, 1.1, 0.0),
    ],
    "scatters": [],
    "hints": {
        "wide_high": ((-1.5, 8.0, 14.0), (0.0, 0.3, -3.0)),
        "party_side": ((7.0, 1.6, 5.0), (-1.5, 1.0, -0.5)),
        "foe_side": ((-7.5, 1.6, 5.0), (1.5, 1.0, 0.0)),
        "from_the_ridge": ((-14.0, 2.6, -16.0), (2.0, 0.8, 1.0)),
    },
}

CAMP_FIRE_COLOR = "#E0702E"  # ember_orange: the fire's rim (color_script ch06 Rim)
CAMP = {
    "id": "salvage_camp_burning",
    **CH06_LIGHT,
    "ground": "camp",
    "ground_glb": BS + "arena_camp_ground.glb",
    "lut": "res://assets/environments/arenas/salvage_camp_burning/lut_ch06_smoke.png",
    "sea": {"y": -1.3, "tide_line_y": -1.3, "sea_glow": 0.0, "material": SILTED_FLATS},
    "glow": (0.55, 0.06, 1.0),
    "pieces": [
        # The camp burning round the fight: the hulk's tide-wheel collapsing behind the foes, tents gone to
        # frames on the flanks, one still catching, the salvage pile and the vats, the Order's brazier.
        (BS + "tide_wheel_burned.glb", -3.0, -14.5, 20.0, 1.0, 0.0),
        (BS + "camp_tent_burned.glb", -12.0, -9.0, 70.0, 1.0, 0.0),
        (BS + "camp_tent.glb", 11.5, -11.5, -60.0, 1.0, 0.0),
        (BS + "salvage_rack_burned.glb", 6.0, -14.0, 10.0, 1.0, 0.0),
        (BS + "salvage_pile_burned.glb", -9.5, -15.0, 35.0, 1.0, 0.0),
        (BS + "brine_vat_burned.glb", 12.0, -4.0, 0.0, 1.0, 0.0),
        (BS + "brine_vat.glb", 13.5, -6.5, 40.0, 1.0, 0.0),
        (BS + "crate_stack_burned.glb", -12.5, -2.0, 110.0, 1.0, 0.0),
        (BS + "branding_brazier.glb", 9.0, 1.5, 0.0, 1.0, 0.0),
        (BS + "chalk_mark_heavy.glb", -27.0, -26.0, 0.0, 1.0, 0.0),
        # The hulk the camp was built against, beyond, and the smoke over it all.
        (BS + "wreck_hull_section.glb", 2.0, -26.0, 175.0, 1.1, 0.4),
        (BS + "wreck_mast_standing.glb", -6.0, -24.0, 5.0, 1.0, 0.2),
        (BS + "smoke_plume.glb", 2.0, -24.0, 0.0, 1.0, 0.0),
        (BS + "smoke_plume.glb", -12.0, -12.0, 15.0, 0.6, 0.0),
        (BS + "smoke_plume.glb", 12.0, -14.0, -10.0, 0.7, 0.0),
        # Out on the flats: the wreck-ridges the party came over, the channel to the west.
        (BS + "wreck_bow.glb", -45.0, -40.0, 60.0, 1.0, 0.2),
        (BS + "wreck_ribs_large.glb", 40.0, -50.0, 150.0, 1.1, 0.2),
    ],
    "scatters": [],
    "lamp_parent": ".",
    "lamp_name": "FireLight",
    "lamp_spec": {"color": CAMP_FIRE_COLOR, "energy": 2.4, "range_m": 10.0, "attenuation": 1.4,
                  "flame_radius_m": 0.08, "flame_energy": 6.0},
    "lamps": [
        # The fires: the tide-wheel's foot, the burned tent's ash bed, the salvage pile, the brazier.
        {"at": (-3.0, 0.6, -14.0), "flame": False, "energy": 3.2, "range": 12.0},
        {"at": (-12.0, 0.4, -9.0), "flame": False},
        {"at": (-9.5, 0.6, -15.0), "flame": False},
        {"at": (9.0, 1.0, 1.5), "flame": False, "energy": 1.6, "range": 6.0, "shadow": True},
    ],
    "hints": {
        "wide_high": ((-1.5, 8.0, 14.0), (0.0, 0.3, -3.0)),
        "party_side": ((7.0, 1.6, 5.0), (-1.5, 1.0, -0.5)),
        "foe_side": ((-7.5, 1.6, 5.0), (1.5, 1.0, 0.0)),
        "past_the_brazier": ((10.5, 1.4, 4.0), (-2.0, 1.0, -3.0)),
    },
}



# ---------------------------------------------------------------------------------------------
# M3-ENV-713: Ch8's set-piece arena, the wall-head at the Fisher Stair (Corrow kit), in its three states
# ---------------------------------------------------------------------------------------------
CW = "res://assets/environments/kits/corrow/"
CW_LAYOUT = ROOT / "game" / "levels" / "_tests" / "corrow_kit" / "corrow_layout.json"  # the kit preview's, read-only
CW_WALK_Y = 12.0  # cw_common.WALK_Y: the walk's paving, the arena's floor
CW_ARC_R = 300.0  # cw_common.ARC_R_M
# M3-BPR-407: the arena's segment (a segment centre) sits so the Fisher Stair's head lands on the party's right
# (its foot is at s -40, its head landing at s ~ -17.4: x ~ +11 here) with Liss's hoist (s -16.5) beside it.
WALLHEAD_S = -6.0
WALLHEAD_Z = 0.7  # the walk's centre line in the arena: parapet from z -2.3, inner kerb from +3.1 (slots + 1 m clear)
WALLHEAD_RADIUS_M = 170.0  # the preview's wall, town and far pieces kept within this of the arena (the far land always)
WALLHEAD_ALWAYS = ("corrow_far", "coilspire_headland")
WALLHEAD_SKIP = ("watcher_relief",)  # the sea face's carvings: below the parapet, never in a battle frame
CORROW_SKY = {  # game/levels/_tests/corrow_kit/corrow_ch08_environment.tres (the kit's ch08 sky)
    "col_zenith": "#3E4A57", "col_horizon_sun": "#B89A7A", "col_horizon_away": "#5E6670", "col_ground": "#2A3640",
    "sky_energy": 1.9, "horizon_curve": 0.25, "azimuth_power": 2.0, "col_band": "#FFD2A8", "band_energy": 0.5,
    "band_height": 0.04, "mid_strength": 0.0, "col_glow": "#FFE4CE", "glow_energy": 0.8, "glow_power": 6.0,
    "halo_energy": 1.5, "halo_power": 200.0, "sun_disc_energy": 10.0, "col_cloud_lit": "#E8B890",
    "col_cloud_shadow": "#34404C", "cloud_coverage": 0.72, "cloud_softness": 0.22, "cloud_opacity": 0.96,
    "cloud_height_m": 1800.0, "cloud_scale_m": 5000.0, "cloud_stretch": "Vector2(1, 2.5)", "cloud_wind_deg": 135.0,
    "cloud_sun_energy": 2.6, "cloud_ambient_energy": 1.35, "cloud_horizon_fade": 0.08}
CORROW_SEA = {  # the colour script's `storm_grey` look (ch08), the Corrow kit preview's corrow_water_material.tres values
    "name": "arena_storm_grey", "shader": "res://game/shaders/water/water_ocean.gdshader",
    "params": [("col_deep", "#0E4A55"), ("col_scatter_shallow", "#1F7F86"), ("absorption_per_m", "Vector3(2, 0.5, 0.42)"),
               ("absorption_scale", 2.25), ("scatter_energy", 0.14), ("caustic_strength", 0.0), ("col_foam", "#EEF6F4"),
               ("col_sss", "#1F7F86"), ("foam_crest_threshold", 0.5), ("roughness_far", 0.18), ("use_caustics", "false"),
               ("use_ssr", "false"), ("use_sss", "false")]}


def wallhead_pose() -> tuple[float, float, float]:
    """World (x, z) and yaw (deg) of the arena's segment centre on the walk (cw_common.bend_points' arc)."""
    th = WALLHEAD_S / CW_ARC_R
    return CW_ARC_R * math.sin(th), CW_ARC_R - CW_ARC_R * math.cos(th), -math.degrees(th)


def wallhead_from_world(x: float, y: float, z: float, yaw: float) -> tuple[tuple[float, float, float], float]:
    """The Corrow preview's world -> the arena: unbend at the segment, then turn half round so the sea (+Z in the
    world) is behind the enemy line (-Z) and the town is behind the camera (+Z); the walk at y 0."""
    x0, z0, yaw0 = wallhead_pose()
    a = math.radians(-yaw0)
    dx, dz = x - x0, z - z0
    lx, lz = dx * math.cos(a) + dz * math.sin(a), -dx * math.sin(a) + dz * math.cos(a)
    return (round(-lx, 3), round(y - CW_WALK_Y, 3), round(WALLHEAD_Z - lz, 3)), round(yaw - yaw0 + 180.0, 3)


def _wallhead_pieces(hoist: bool) -> list:
    """The kit preview's wall (segments, aprons, the parapet's heads), the stair, the low town and the far land,
    re-based on the arena's segment. Its own segment is the arena's Ground. Liss's hoist only once it is rigged
    (B11: waves 2 and 3, the boss)."""
    rows = []
    for p in json.loads(CW_LAYOUT.read_text(encoding="utf-8"))["pieces"]:
        name = p["piece"]
        if name in WALLHEAD_SKIP or (name == "liss_hoist" and not hoist):
            continue
        at, yaw = wallhead_from_world(p["at"][0], p["y"], p["at"][1], p["yaw_deg"])
        if name not in WALLHEAD_ALWAYS and math.hypot(at[0], at[2]) > WALLHEAD_RADIUS_M:
            continue
        if name == "seawall_curve" and abs(at[0]) < 0.5 and abs(at[2] - WALLHEAD_Z) < 0.5:
            continue  # the Ground
        rows.append({"glb": CW + name + ".glb", "at": at, "yaw": yaw})
    return rows


# The wall-head's own clutter, beyond the slots: the stair-watch's shields stacked by the stair head (party side),
# a rope coil and the salvage the watch dragged up, a lifting basket by the hoist (when rigged).
WALLHEAD_DRESSING = [
    {"glb": CW + "round_shield.glb", "at": (6.4, 0.0, 2.4), "yaw": 20.0},
    {"glb": CW + "round_shield.glb", "at": (7.1, 0.0, 2.1), "yaw": -35.0},
    {"glb": CW + "round_shield.glb", "at": (7.6, 0.0, -1.6), "yaw": 70.0},
    {"glb": KIT + "rope_coil.glb", "at": (-6.2, 0.0, 2.3), "yaw": 0.0},
    {"glb": BS + "crate_stack.glb", "at": (-7.7, 0.0, -1.3), "yaw": 95.0},
    {"glb": KIT + "cargo_sacks.glb", "at": (8.8, 0.0, 0.4), "yaw": 160.0},
]
WALLHEAD_HOIST_DRESSING = [  # by the hoist, on the party's right with the stair head (M3-BPR-407)
    {"glb": CW + "hoist_basket.glb", "at": (8.4, 0.0, -1.7), "yaw": 30.0},
    {"glb": KIT + "rope_coil.glb", "at": (9.4, 0.0, -0.6), "yaw": 40.0},
]
WALLHEAD_ENTRY_WARD = (10.6, 0.0, 2.4)  # EntryMarker_ward: the walk at the stair head, where the Climb arrives
# The kites still up over the wall in the afternoon (they come down on the run back, B08): along the parapet.
WALLHEAD_KITES = [{"glb": CW + "kite_line.glb", "at": (0.0, 0.0, -2.9), "yaw": 180.0, "structure": True}]


def _wallhead_arena(arena_id: str, *, hoist: bool, surge: bool) -> dict:
    """Ch8's stair-head (act1_ch08.md W09-W11; set_piece_battles.md): the waves (B10 `ch08` 16:00, B12 and B14 the
    storm coming in) and the boss (B16, `ch08_surge`: the sun a smear behind the front, near-night)."""
    pieces = WALLHEAD_DRESSING + (WALLHEAD_HOIST_DRESSING if hoist else []) + ([] if surge else WALLHEAD_KITES)
    _x0, _z0, yaw0 = wallhead_pose()
    sun_az = round(70.0 - yaw0, 1)  # the world's 250 deg turned with the arena: over the sea, frame right
    if surge:
        # corrow.md `ch08_surge`: 22 deg / 255 deg behind the front, #FFE4CE at 0.35; ambient #5E6E80 0.6; spray
        # haze thick; the sky closed down.
        light = {"sun": {"elev": 22.0, "az": round(sun_az + 5.0, 1), "color": "#FFE4CE", "energy": 0.35},
                 "fill": {"color": "#5E6E80", "energy": 0.6}, "exposure": 0.95,
                 "fog": {"color": "#5E6670", "light_energy": 0.6, "aerial": 0.6, "density": 0.006, "sky_affect": 0.5,
                         "height": 0.0, "height_density": 0.0},
                 "sky": dict(CORROW_SKY, sky_energy=0.9, cloud_coverage=0.9, sun_disc_energy=0.0, glow_energy=0.2,
                             halo_energy=0.3, band_energy=0.15)}
    else:
        # Colour script ch08 (16:00): sun 30 deg / 250 deg, key #FFE4CE 2.0 (1.4 as the storm comes in for waves 2
        # and 3), ambient the kit's sky-tinted #7A8A9C, fog #5E6670, exposure 0.80.
        key = 1.4 if hoist else 2.0
        light = {"sun": {"elev": 30.0, "az": sun_az, "color": "#FFE4CE", "energy": key},
                 "fill": {"color": "#7A8A9C", "energy": 0.85 if hoist else 1.0}, "exposure": 0.8,
                 "fog": {"color": "#5E6670", "aerial": 0.5, "density": 0.003 if hoist else 0.0022,
                         "sky_affect": 0.3, "height": 0.0, "height_density": 0.0},
                 "sky": dict(CORROW_SKY, cloud_coverage=0.82) if hoist else dict(CORROW_SKY)}
    return {
        "id": arena_id,
        "sub_frame": "ch08_surge" if surge else "ch08",
        "ground": "deck",
        "ground_glb": CW + "seawall_curve.glb",
        "ground_at": (0.0, -CW_WALK_Y, WALLHEAD_Z),
        "ground_yaw": 180.0,
        "lut": f"res://assets/environments/arenas/{arena_id}/lut_ch08_storm.png",
        **light,
        "sky_shader": LOW_SUN_SKY,
        "sea": {"y": -CW_WALK_Y, "tide_line_y": -CW_WALK_Y, "sea_glow": 0.06 if surge else 0.0,
                "material": CORROW_SEA},
        "pieces": pieces + _wallhead_pieces(hoist),
        "scatters": [],
        "hints": {
            "wide_high": ((-1.5, 7.5, 13.5), (0.0, 0.3, -3.0)),
            "party_side": ((5.6, 1.7, 4.5), (-1.5, 1.0, -0.5)),
            "foe_side": ((-5.6, 1.7, 4.0), (1.5, 1.0, 0.0)),
            "along_the_walk": ((-9.5, 1.8, 1.4), (3.0, 1.0, -0.2)),
            "the_storm_wall": ((2.0, 0.7, 5.0), (-3.0, 3.5, -14.0)),
        },
        "anchors": ({"BossAnchor": (-6.0, 0.9, -3.4)} if surge else {}) | {"EntryMarker_ward": WALLHEAD_ENTRY_WARD},
    }


WALLHEAD_STORM = _wallhead_arena("seawall_stairhead_storm", hoist=False, surge=False)
WALLHEAD_HOIST = _wallhead_arena("seawall_stairhead_hoist", hoist=True, surge=False)
WALLHEAD_SURGE = _wallhead_arena("seawall_stairhead_surge", hoist=True, surge=True)


# ---------------------------------------------------------------------------------------------
# M3-ENV-713: the Coilspire headland path's landing (the Coilspire kit; act1_ch08.md B04)
# ---------------------------------------------------------------------------------------------
CS = "res://assets/environments/kits/coilspire/"
CS_LAYOUT = ROOT / "game" / "levels" / "_tests" / "coilspire_kit" / "coilspire_layout.json"  # read-only
CS_BACKDROP = ROOT / "game" / "levels" / "_tests" / "coilspire_kit" / "coilspire_backdrop.json"  # Corrow, read-only
HEADLAND_SPIRE_BEARING = -30.0  # the spire stands back-left of the fight (deg, clockwise from the frame's -Z)
HEADLAND_REPLACED = ("coilspire_ground", "headland_path")  # the arena's own levelled copies stand in for these
HEADLAND_SCRUB_CLEAR_M = 9.0  # scrub this near the landing's centre is left out (the landing is 15 x 11 m)
HEADLAND_SKIP = ("watcher_relief",)


def _coilspire():
    sys.path.append(str(HERE.parent / "coilspire"))  # the Coilspire kit's frames and its arena landing, read-only
    import cs_arena  # noqa: PLC0415
    import cs_common  # noqa: PLC0415

    return cs_arena, cs_common


def headland_pose() -> tuple[tuple[float, float, float], float]:
    """The landing's centre in Corrow's world (x, y, z) and the turn (deg, clockwise seen from above) that puts the
    spire at HEADLAND_SPIRE_BEARING."""
    ca, cs = _coilspire()
    p, y, _t = ca.landing()
    pw = cs.world_from_headland(float(p[0]), y, float(p[1]))
    sw = cs.world_from_spire(0.0, 0.0, 0.0)
    bearing = math.degrees(math.atan2(sw[0] - pw[0], -(sw[2] - pw[2])))
    return pw, HEADLAND_SPIRE_BEARING - bearing


def headland_from_world(x: float, y: float, z: float, yaw: float) -> tuple[tuple[float, float, float], float]:
    (x0, y0, z0), psi = headland_pose()
    a = math.radians(psi)
    bx, by = x - x0, -(z - z0)  # (east, north)
    rx, ry = bx * math.cos(a) + by * math.sin(a), -bx * math.sin(a) + by * math.cos(a)
    return (round(rx, 3), round(y - y0, 3), round(-ry, 3)), round(yaw - psi, 3)


def _headland_pieces() -> list:
    rows = []
    for path in (CS_LAYOUT, CS_BACKDROP):
        for p in json.loads(path.read_text(encoding="utf-8"))["pieces"]:
            name = p["piece"]
            if name in HEADLAND_REPLACED or name in HEADLAND_SKIP:
                continue
            at, yaw = headland_from_world(p["at"][0], p["y"], p["at"][1], p["yaw_deg"])
            if name.startswith("scrub_clump"):
                if math.hypot(at[0], at[2]) < HEADLAND_SCRUB_CLEAR_M:
                    continue
                at = (at[0], round(_headland_ground_y(p["at"][0], p["at"][1]) + at[1] - p["y"], 3), at[2])
            kit = CS if path == CS_LAYOUT else CW
            rows.append({"glb": kit + name + ".glb", "at": at, "yaw": yaw})
    at, yaw = headland_from_world(*_headland_frame())
    rows.append({"glb": CS + "arena_headland_path.glb", "at": at, "yaw": yaw, "floor": True})
    return rows


def _headland_ground_y(wx: float, wz: float) -> float:
    """The arena ground's height (Corrow's world y) under a world point: the kit's grading with the levelled path
    and the landing (cs_arena), so the scrub stands on the ground the arena has, not the kit's."""
    ca, cs = _coilspire()
    hx, hz, yaw = cs.HEADLAND
    a = math.radians(yaw)
    dx, dz = wx - hx, wz - hz
    lx, lz = dx * math.cos(a) - dz * math.sin(a), dx * math.sin(a) + dz * math.cos(a)  # world_from_headland, inverted
    with ca._Levelled():
        return float(ca._height(np.array([lx]), np.array([lz]), cs.headland_noise())[0])


def _headland_frame() -> tuple[float, float, float, float]:
    """The headland frame's origin in Corrow's world (x, y, z) and its yaw: where the kit's ground and path go."""
    _ca, cs = _coilspire()
    hx, hz, yaw = cs.HEADLAND
    return hx, 0.0, hz, yaw


def _headland_arena() -> dict:
    ground_at, ground_yaw = headland_from_world(*_headland_frame())
    (_x0, _y0, _z0), psi = headland_pose()
    return {
        "id": "coilspire_headland_path",
        "sub_frame": "ch08",
        "ground": "deck",
        "ground_glb": CS + "arena_headland_ground.glb",
        "ground_at": ground_at,
        "ground_yaw": ground_yaw,
        "lut": "res://assets/environments/arenas/coilspire_headland_path/lut_ch08_storm.png",
        # coilspire.md `ch08` on the headland (Corrow's storm sky; the beat sheet's `ch08_day` has no colour-script
        # row yet): sun 30 deg / 250 deg turned with the arena, key #FFE4CE 2.0, ambient #7A8A9C, exposure 0.80.
        "sun": {"elev": 30.0, "az": round((250.0 + psi) % 360.0, 1), "color": "#FFE4CE", "energy": 2.0},
        "fill": {"color": "#7A8A9C", "energy": 1.0},
        "exposure": 0.8,
        "fog": {"color": "#5E6670", "aerial": 0.5, "density": 0.0018, "sky_affect": 0.3, "height": 0.0,
                "height_density": 0.0},
        "sky_shader": LOW_SUN_SKY,
        "sky": dict(CORROW_SKY, cloud_coverage=0.6),
        "sea": {"y": round(-_y0, 3), "tide_line_y": round(-_y0, 3), "sea_glow": 0.0, "material": CORROW_SEA},
        "pieces": _headland_pieces(),
        "scatters": [],
        "hints": {
            "wide_high": ((-1.5, 7.5, 13.5), (0.0, 0.3, -3.0)),
            "party_side": ((5.6, 1.7, 4.5), (-1.5, 1.0, -0.5)),
            "foe_side": ((-5.6, 1.7, 4.0), (1.5, 1.0, 0.0)),
            "to_the_spire": ((4.5, 1.4, 6.5), (-8.0, 8.0, -40.0)),
        },
    }


HEADLAND = _headland_arena()


# ---------------------------------------------------------------------------------------------
# M3-ENV-713: a tier of the Coilspire's well (the Coilspire kit's arena_tier_hall; act1_ch08.md B05's placed fights)
# ---------------------------------------------------------------------------------------------
COILSPIRE_FIRE = "#FFB16E"  # coilspire.md `ch08_coilspire_int`: the braziers' oil fire (~2,900 K)
TIER_HALL_SEA_Y = -48.3  # tier 2 stands 9 m over the spire's base, 39.3 m over the sea


def _tier_hall_arena() -> dict:
    ca, _cs = _coilspire()
    fittings, fires = ca.hall_fittings()
    return {
        "id": "coilspire_tier_landing",
        "sub_frame": "ch08_coilspire_int",
        "ground": "deck",
        "ground_glb": CS + "arena_tier_hall.glb",
        "lut": "res://assets/environments/arenas/coilspire_tier_landing/lut_ch08_coilspire_int.png",
        # coilspire.md `ch08_coilspire_int`: the braziers #FFB16E 2.0, range 8 m; ambient #5A7E78 (bronze_patina,
        # lifted) 2.0, the copper green-cyan; fog #24443F 0.006; exposure 1.5; the sky through the openings at 0.45.
        # The one directional is the afternoon sun down the shaft (ch08: 30 deg is too low to reach the floor; the
        # shaft's light is the crown opening's, steep).
        "sun": {"elev": 64.0, "az": 200.0, "color": "#FFE4CE", "energy": 0.9, "max_distance": 60.0},
        "fill": {"color": "#5A7E78", "energy": 2.0},
        "exposure": 1.5,
        "glow": (0.6, 0.04, 1.0),
        "fog": {"color": "#24443F", "aerial": 0.3, "density": 0.006, "sky_affect": 0.0, "height": 0.0,
                "height_density": 0.0},
        "sky_shader": LOW_SUN_SKY,
        "sky": dict(CORROW_SKY, sky_energy=0.85),
        "sea": {"y": TIER_HALL_SEA_Y, "tide_line_y": TIER_HALL_SEA_Y, "sea_glow": 0.0, "material": CORROW_SEA},
        "pieces": [{"glb": CS + name + ".glb", "at": at, "yaw": yaw, "structure": True} for name, at, yaw in fittings],
        "scatters": [],
        "lamp_spec": {"color": COILSPIRE_FIRE, "energy": 2.0, "range_m": 8.0, "attenuation": 1.2,
                      "flame_radius_m": 0.06, "flame_energy": 6.0},
        "lamps": [{"at": f, "flame": False, "shadow": k == 0} for k, f in enumerate(fires)],
        "hints": {
            "wide_high": ((-1.5, 7.5, 13.5), (0.0, 0.8, -3.0)),
            "party_side": ((5.6, 1.7, 4.5), (-1.5, 1.0, -0.5)),
            "foe_side": ((-5.6, 1.7, 4.0), (1.5, 1.0, 0.0)),
            "up_the_well": ((1.0, 0.8, 4.5), (-1.0, 9.0, -5.0)),
        },
    }


TIER_HALL = _tier_hall_arena()


# ---------------------------------------------------------------------------------------------
# M3-ENV-717: the Avalanche Ram's terrace under the seeping Lit Age wall, Keth Pass (keth.py; keth_pass.md §2)
# ---------------------------------------------------------------------------------------------
def _keth():
    import keth  # noqa: PLC0415

    return keth


KETH_ARENA = {
    "id": "keth_seep_terrace",
    "sub_frame": "ch12",
    "ground": "deck",
    "ground_glb": KIT + "keth_terrace_ground.glb",
    "lut": "res://assets/environments/arenas/keth_seep_terrace/lut_ch12_heights.png",
    # Colour script ch12 (09:00, thin air, hard sun between cloud banks): sun 30 deg / 140 deg, key #FAF6FF 2.8,
    # fill #7FA6DC 0.8, sky #1E5BB8 / #C8D8E8, fog #D0DCE8 thin, exposure 0.65, lut_ch12_heights.
    "sun": {"elev": 30.0, "az": 140.0, "color": "#FAF6FF", "energy": 2.8},
    "fill": {"color": "#7FA6DC", "energy": 0.8},
    "exposure": 0.65,
    "fog": {"color": "#D0DCE8", "aerial": 0.5, "density": 0.0012, "sky_affect": 0.15, "height": 0.0,
            "height_density": 0.0},
    "sky_shader": LOW_SUN_SKY,
    "sky": {"col_zenith": "#1E5BB8", "col_horizon_sun": "#E8EEF5", "col_horizon_away": "#C8D8E8", "col_ground": "#5A6470",
            "sky_energy": 1.6, "horizon_curve": 0.3, "azimuth_power": 1.5, "col_band": "#F4F6FA", "band_energy": 0.2,
            "band_height": 0.05, "mid_strength": 0.0, "col_glow": "#FFFFFF", "glow_energy": 0.6, "glow_power": 6.0,
            "halo_energy": 1.0, "halo_power": 120.0, "sun_disc_energy": 8.0, "col_cloud_lit": "#F6F8FC",
            "col_cloud_shadow": "#8C98A8", "cloud_coverage": 0.45, "cloud_softness": 0.3, "cloud_opacity": 0.85,
            "cloud_height_m": 1400.0, "cloud_scale_m": 3500.0, "cloud_stretch": "Vector2(1, 1.6)",
            "cloud_wind_deg": 300.0, "cloud_sun_energy": 2.0, "cloud_ambient_energy": 1.2, "cloud_horizon_fade": 0.1},
    # No sea on the pass: the arena's Sea (the contract's water publisher) lies far down the valley, out of frame.
    "sea": {"y": -160.0, "tide_line_y": -160.0, "sea_glow": 0.0, "material": CORROW_SEA},
    "pieces": [
        {"glb": KIT + "lit_terrace_wall.glb", "at": (x, 0.0, _keth().WALL_Z), "yaw": 0.0, "structure": True}
        for x in (-12.0, 0.0, 12.0)
    ] + [
        {"glb": KIT + "seep_pool.glb", "at": (_keth().SEEP_POOL_AT[0], 0.0, _keth().SEEP_POOL_AT[1]), "yaw": 20.0},
        {"glb": KIT + "pass_cord.glb", "at": (0.0, 0.0, -4.0), "yaw": 0.0, "structure": True},
        {"glb": KIT + "cairn.glb", "at": (-8.6, 0.0, 3.6), "yaw": 30.0},
        {"glb": KIT + "cairn.glb", "at": (8.8, 0.0, 3.4), "yaw": 200.0},
        {"glb": KIT + "keth_far_ridges.glb", "at": (0.0, -20.0, 0.0), "yaw": 0.0},
    ],
    "scatters": [],
    "hints": {
        "wide_high": ((-1.5, 7.5, 13.5), (0.0, 0.8, -3.0)),
        "party_side": ((5.6, 1.7, 4.5), (-1.5, 1.0, -0.5)),
        "foe_side": ((-5.6, 1.7, 4.0), (1.5, 1.0, 0.0)),
        "under_the_wall": ((3.0, 0.9, 3.5), (-6.0, 4.5, -6.0)),
        "the_pass_below": ((-2.0, 1.6, -3.5), (3.0, -4.0, 20.0)),
    },
    "anchors": {"BossAnchor": (-7.5, 0.0, -3.0)},
}

# ---------------------------------------------------------------------------------------------
# M3-ENV-716: the Lamp Engine's flooded hall under Lowlight's sanctum (lowlight.py; lowlight.md §2)
# ---------------------------------------------------------------------------------------------
def _lowlight():
    import lowlight  # noqa: PLC0415

    return lowlight


BOUND_TEAL = "#4FB3B0"  # palette glimmer_bound: the Engine's trimmed lamps and the conduits, steady
OVERCAST_LAGOON = {  # the colour script's `overcast_lagoon` look (ch11): the Act I water under a grey sky, muted
    "name": "arena_overcast_lagoon", "shader": "res://game/shaders/water/water_ocean.gdshader",
    "params": [("col_deep", "#0E4A55"), ("col_scatter_shallow", "#1FA3A6"), ("absorption_per_m", "Vector3(2, 0.5, 0.42)"),
               ("absorption_scale", 1.5), ("scatter_energy", 0.1), ("caustic_strength", 0.0), ("col_foam", "#EEF6F4"),
               ("col_sss", "#3FD0C9"), ("foam_crest_threshold", 0.9), ("roughness_far", 0.04), ("use_caustics", "false"),
               ("use_sss", "false"),
               # PC row 86 (10-31): still, sheltered water has no shore foam and no hard sun glints. The sun's GGX glint
               # on the wave facets printed jagged white flakes across the hall's floor water.
               ("use_foam", "false"), ("glint_strength", 0.12), ("glint_min_roughness", 0.2), ("use_ssr", "false")]}


def _lowlight_arena() -> dict:
    ll = _lowlight()
    h = ll.HALL_HALF - 0.6
    lamps = [(x, ll.RAIL_Y + 0.45, -h) for x in (-9.0, -5.4, -1.8, 1.8, 5.4, 9.0)]
    lamps += [(sx * h, ll.RAIL_Y + 0.45, z) for sx in (-1.0, 1.0) for z in (-7.0, -1.0, 5.0)]
    return {
        "id": "lowlight_engine_hall",
        "sub_frame": "ch11",
        "ground": "deck",
        "ground_glb": KIT + "engine_hall.glb",
        "lut": "res://assets/environments/arenas/lowlight_engine_hall/lut_ch11_vey.png",
        # Colour script ch11 (12:30 overcast): key #F3F2FF 1.4 from 65 deg / 200 deg, through the fallen vault bay (the
        # grey shaft); fill #7FA3A8 0.7; fog #8A9A98; exposure 0.75; lut_ch11_vey. Inside, the Engine's twelve trimmed
        # lamps on the rail are the key (lowlight.md §0): bound teal, steady, no flame flicker.
        "sun": {"elev": 65.0, "az": 200.0, "color": "#F3F2FF", "energy": 1.4, "max_distance": 60.0},
        "fill": {"color": "#7FA3A8", "energy": 0.7},
        "exposure": 0.75,
        "fog": {"color": "#8A9A98", "aerial": 0.3, "density": 0.008, "sky_affect": 0.0, "height": 0.0,
                "height_density": 0.0},
        "sky_shader": LOW_SUN_SKY,
        "sky": dict(CORROW_SKY, col_zenith="#7A8896", col_horizon_sun="#A8B4B8", col_horizon_away="#A8B4B8",
                    sky_energy=0.9, sun_disc_energy=0.0, halo_energy=0.0, glow_energy=0.0, cloud_coverage=0.95),
        # The hall's still water over the flooded floor: no wind reaches it (lowlight.md §0).
        "sea": {"y": ll.WATER_Y, "tide_line_y": ll.WATER_Y, "sea_glow": 0.0, "material": OVERCAST_LAGOON,
                "waves": [(20.0, 3.0, 0.004, 0.05), (140.0, 1.7, 0.002, 0.05)]},
        "pieces": [
            {"glb": KIT + "conduit_run.glb", "at": (x, 1.6, -ll.HALL_HALF + 0.05), "yaw": 0.0, "structure": True}
            for x in (-8.0, 8.0)
        ],
        "scatters": [],
        "lamp_spec": {"color": BOUND_TEAL, "energy": 1.6, "range_m": 9.0, "attenuation": 1.0,
                      "flame_radius_m": 0.08, "flame_energy": 3.0},
        "lamps": [{"at": p, "flame": True, "shadow": k == 2} for k, p in enumerate(lamps)],
        "hints": {
            "wide_high": ((-1.5, 7.5, 13.5), (0.0, 0.8, -3.0)),
            "party_side": ((5.6, 1.7, 4.5), (-1.5, 1.0, -0.5)),
            "foe_side": ((-5.6, 1.7, 4.0), (1.5, 1.0, 0.0)),
            "under_the_shaft": ((2.5, 1.2, 4.0), (-3.0, 3.5, -8.0)),
            "the_lamps": ((4.0, 2.4, 2.0), (-6.0, 4.0, -11.0)),
        },
        "anchors": {"BossAnchor": ll.ENGINE_AT},
    }


LOWLIGHT_ARENA = _lowlight_arena()

# The Sunken Vey's conduit court (M4-A2P-041; lowlight.md §5): the galleries' regular fights (ch11_vey_rays,
# ch11_vey_urchins) on the zone's own court, its dressing round it (ch11_lowlight_dressing.py's output, read-only),
# moved so the court's centre is the arena's origin. Ch11's overcast noon outside: the engine hall's grade without
# its lamps, the still lagoon round the court.
VEY_COURT_AT = (38.0, -22.0)  # the greybox Court block's centre (sunken_vey_layout.json)
VEY_DRESSING = Path(__file__).resolve().parents[4] / "game" / "levels" / "ch11" / "sunken_vey" / "sunken_vey_dressing.json"
VEY_PROP_CLEAR_M = 4.0
VEY_STRUCTURE = ("vey_arcade_bay", "ruin_column_broken", "lowlight_nave_bay", "lowlight_nave_bay_broken", "ruin_wall_sunk")


def _vey_pieces() -> list:
    rows = json.loads(VEY_DRESSING.read_text(encoding="utf-8"))["pieces"]
    pieces = []
    for p in rows:
        if p["piece"] == "sunken_vey_court":
            continue  # the ground
        x, z = p["at"][0] - VEY_COURT_AT[0], p["at"][1] - VEY_COURT_AT[1]
        y = float(p.get("y", 0.0))
        row = {"glb": KIT + p["piece"] + ".glb", "at": (round(x, 3), y, round(z, 3)), "yaw": p["yaw_deg"]}
        if "scale" in p:
            row["scale"] = p["scale"]
        if p["piece"] in VEY_STRUCTURE:
            row["structure"] = True
        elif abs(y) < 0.5 and _near_slot(x, z, VEY_PROP_CLEAR_M):
            continue
        pieces.append(row)
    return pieces


def _vey_arena() -> dict:
    return dict(
        LOWLIGHT_ARENA,
        id="sunken_vey_gallery",
        ground_glb=KIT + "sunken_vey_court.glb",
        ground_at=(-VEY_COURT_AT[0], 0.0, -VEY_COURT_AT[1]),
        # Outside under the overcast: no shaft, the key the grey sky's (colour script ch11, 12:30).
        sun={"elev": 65.0, "az": 200.0, "color": "#F3F2FF", "energy": 1.4},
        fog={"color": "#8A9A98", "aerial": 0.4, "density": 0.004, "sky_affect": 0.1, "height": 0.0,
             "height_density": 0.0},
        sea={"y": -0.3, "tide_line_y": -0.3, "sea_glow": 0.0, "material": OVERCAST_LAGOON,
             "waves": [(20.0, 3.0, 0.004, 0.05), (140.0, 1.7, 0.002, 0.05)]},
        pieces=_vey_pieces(),
        lamps=[],
        hints={
            "wide_high": ((-1.5, 7.5, 13.5), (0.0, 0.8, -3.0)),
            "party_side": ((5.6, 1.7, 4.5), (-1.5, 1.0, -0.5)),
            "foe_side": ((-5.6, 1.7, 4.0), (1.5, 1.0, 0.0)),
            "the_galleries": ((3.0, 1.4, 5.0), (-4.0, 1.5, -14.0)),
            "the_lagoon": ((-2.0, 2.2, -2.0), (6.0, -0.3, 20.0)),
        },
        anchors={"BossAnchor": (-5.0, 0.0, -2.5)},
    )


VEY_ARENA = _vey_arena()

# ---------------------------------------------------------------------------------------------
# M3-ENV-718: the Mangrove Drowner's mudbank under the dead tree, Ossa Fen (ossa_fen.py; ossa_fen.md §2)
# ---------------------------------------------------------------------------------------------
def _fen():
    import ossa_fen  # noqa: PLC0415

    return ossa_fen


TANNIN_FEN = {  # the colour script's `tannin_fen` look (ch10): brown-black tea water, its own sigma, caustics off
    "name": "arena_tannin_fen", "shader": "res://game/shaders/water/water_ocean.gdshader",
    "params": [("col_deep", "#3A2A18"), ("col_scatter_shallow", "#4A3A22"), ("absorption_per_m", "Vector3(0.6, 1.4, 4)"),
               ("absorption_scale", 1.0), ("scatter_energy", 0.08), ("caustic_strength", 0.0), ("col_foam", "#C8C4B4"),
               ("col_sss", "#6A4A26"), ("foam_crest_threshold", 0.9), ("roughness_far", 0.06), ("use_caustics", "false"),
               ("use_sss", "false"),
               # PC row 86: a tannin backwater has no surf and no hard glints. The sun's glint off the shallow sheets in
               # the mud's dips read as stark white cut-outs.
               ("use_foam", "false"), ("glint_strength", 0.12), ("glint_min_roughness", 0.2), ("use_ssr", "false")]}


def _fen_arena() -> dict:
    fen = _fen()
    trees = [{"glb": KIT + "mangrove_tree.glb", "at": (x, 0.0, z), "yaw": yaw, "scale": sc, "structure": True}
             for x, z, yaw, sc in fen.MANGROVES]
    reeds = [{"glb": KIT + "reed_bed.glb", "at": at, "yaw": yaw}
             for at, yaw in (((-10.0, 0.0, 4.0), 20.0), ((9.0, 0.0, -3.0), 110.0), ((5.5, 0.0, -9.5), 60.0),
                             ((-15.5, 0.0, -4.0), 150.0), ((16.0, 0.0, 6.0), 80.0))]
    return {
        "id": "ossa_fen_roots",
        "sub_frame": "ch10",
        "ground": "deck",
        "ground_glb": KIT + "fen_bank_ground.glb",
        "lut": "res://assets/environments/arenas/ossa_fen_roots/lut_ch10_fen.png",
        # Colour script ch10 (18:20 overcast dusk): sun 2 deg / 275 deg, key #FFFEFA 0.9, fill #6F7E8E 0.5, sky
        # #4A5868 / #9A9488, fog #5A6A62 dense, exposure 0.9, lut_ch10_fen.
        "sun": {"elev": 2.0, "az": 275.0, "color": "#FFFEFA", "energy": 0.9, "max_distance": 80.0},
        "fill": {"color": "#6F7E8E", "energy": 0.5},
        "exposure": 0.9,
        "fog": {"color": "#5A6A62", "aerial": 0.5, "density": 0.012, "sky_affect": 0.3, "height": 0.0,
                "height_density": 0.0},
        "sky_shader": LOW_SUN_SKY,
        "sky": dict(CORROW_SKY, col_zenith="#4A5868", col_horizon_sun="#B8AE9C", col_horizon_away="#9A9488",
                    col_ground="#3A3A34", sky_energy=0.9, sun_disc_energy=0.0, halo_energy=0.4, glow_energy=0.3,
                    cloud_coverage=0.85),
        # The slack channels: still tea-dark water, a breath of ripple.
        "sea": {"y": fen.WATER_Y, "tide_line_y": fen.WATER_Y, "sea_glow": 0.0, "material": TANNIN_FEN,
                "waves": [(240.0, 6.0, 0.008, 0.08), (300.0, 2.5, 0.003, 0.05)]},
        "pieces": [
            {"glb": KIT + "mangrove_dead.glb", "at": (fen.DEAD_AT[0], 0.0, fen.DEAD_AT[1]), "yaw": 0.0, "structure": True},
        ] + trees + reeds,
        "extra_glbs": [KIT + "fen_far_mangroves.glb"],  # the far tree-line ring (r 70-110 m), centred on the arena
        "scatters": [],
        "hints": {
            "wide_high": ((-1.5, 7.5, 13.5), (0.0, 0.8, -3.0)),
            "party_side": ((5.6, 1.7, 4.5), (-1.5, 1.0, -0.5)),
            "foe_side": ((-5.6, 1.7, 4.0), (1.5, 1.0, 0.0)),
            "the_dead_crown": ((-1.0, 1.0, 2.5), (-7.0, 11.0, -6.0)),
            "the_channel": ((-2.0, 1.6, -2.0), (2.0, 0.6, 20.0)),
        },
        "anchors": {"BossAnchor": fen.DROWNER_AT},
    }


FEN_ARENA = _fen_arena()

# ---------------------------------------------------------------------------------------------
# M3-ENV-720: the Wakefin on Merel's drifting bridal barge, the open sea at night (bridal_barge.py; open_sea_ch15.md)
# ---------------------------------------------------------------------------------------------
def _bridal():
    import bridal_barge  # noqa: PLC0415

    return bridal_barge


BRIDAL_ARENA = {
    "id": "bridal_barge_night",
    "sub_frame": "ch15",
    "ground": "deck",
    "ground_glb": KIT + "bridal_barge.glb",
    "lut": "res://assets/environments/arenas/bridal_barge_night/lut_ch15_unlamped.png",
    # Colour script ch15 (01:00, unlamped): the moon #D2DFFF 0.25 (rule 3b: <= 2.5 x the sea-glow 0.12), fill
    # #0B1630 0.15, fog #1C3A4A 0.004, exposure 1.10, night_sea, lut_ch15_unlamped. No lamp: nothing warm lights it.
    "sun": {"elev": 38.0, "az": 150.0, "color": "#D2DFFF", "energy": 0.25, "max_distance": 60.0, "moon": True},
    "fill": {"color": "#0B1630", "energy": 0.15},
    "exposure": 1.1,
    "glow": (0.6, 0.08, 0.9),
    "fog": {"color": "#1C3A4A", "density": 0.004, "sky_affect": 0.0, "height": 0.0, "height_density": 0.0},
    "sky_shader": "res://game/shaders/environment/env_sky_night.gdshader",
    "sky": {"col_zenith": "#050A14", "col_horizon": "#0B1630", "col_ground": "#061A2B"},
    "sea": {"y": _bridal().WATERLINE_Y, "tide_line_y": _bridal().WATERLINE_Y, "sea_glow": 0.12, "material": NIGHT_SEA},
    "pieces": [],
    "scatters": [],
    "hints": {
        "wide_high": ((-1.5, 7.5, 13.5), (0.0, 0.8, -3.0)),
        "party_side": ((5.6, 1.7, 4.5), (-1.5, 1.0, -0.5)),
        "foe_side": ((-5.6, 1.7, 4.0), (1.5, 1.0, 0.0)),
        "the_bier": ((3.0, 1.4, 2.8), (6.2, 0.6, 0.0)),
        "the_dark_water": ((-2.0, 0.9, -2.0), (-14.0, -0.6, -6.0)),
    },
    "anchors": {"BossAnchor": (-10.0, _bridal().WATERLINE_Y, -1.5)},
}

# ---------------------------------------------------------------------------------------------
# M3-ENV-721: Warden Malcor Venn's pursuit on Ansedra's lagoon at the wedding's dusk (ansedra.py; ansedra.md §2)
# ---------------------------------------------------------------------------------------------
PURSUIT_AT = (-2.0, -7.6)  # the pursuit barge's waterline centre, alongside behind the enemy line
LACQUER_LAGOON = {  # the colour script's `overcast_lagoon` look under ch14 (deep #2E3448): the still mirror, breaking
    "name": "arena_lacquer_lagoon", "shader": "res://game/shaders/water/water_ocean.gdshader",
    "params": [("col_deep", "#2E3448"), ("col_scatter_shallow", "#3A5A66"), ("absorption_per_m", "Vector3(2, 0.5, 0.42)"),
               ("absorption_scale", 1.5), ("scatter_energy", 0.06), ("caustic_strength", 0.0), ("col_foam", "#E8E4E0"),
               ("col_sss", "#3A5A66"), ("foam_crest_threshold", 0.95), ("roughness_far", 0.02), ("use_caustics", "false"),
               ("use_ssr", "true"), ("use_sss", "false")]}

ANSEDRA_ESCAPE = {
    "id": "ansedra_lagoon_escape",
    "sub_frame": "ch14",
    "ground": "deck",
    "ground_glb": KIT + "bridal_barge.glb",
    "lut": "res://assets/environments/arenas/ansedra_lagoon_escape/lut_ch14_wedding.png",
    # Colour script ch14 (18:30): sun 1 deg / 270 deg, key #FFAA5F 1.4, fill #4A5A78 0.4, sky #2E3448 / #B85A3A, fog
    # #4A3A3A, exposure 0.90, lut_ch14_wedding. The city's windows lit far off; no lamp on the barges.
    # The sun stands at 5 deg here, not the script's 1 deg: at 1 deg the bow rail's shadow (20 m) covered the whole
    # deck and the fighting floor read black (c770380's render).
    "sun": {"elev": 5.0, "az": 270.0, "color": "#FFAA5F", "energy": 1.4, "max_distance": 80.0},
    "fill": {"color": "#4A5A78", "energy": 0.4},
    "exposure": 0.9,
    "glow": (0.5, 0.06, 1.0),
    "fog": {"color": "#4A3A3A", "aerial": 0.5, "density": 0.002, "sky_affect": 0.2, "height": 0.0, "height_density": 0.0},
    "sky_shader": LOW_SUN_SKY,
    "sky": dict(CORROW_SKY, col_zenith="#2E3448", col_horizon_sun="#B85A3A", col_horizon_away="#4A4A5E",
                col_ground="#1E2230", sky_energy=0.9, sun_disc_energy=2.0, halo_energy=0.8, glow_energy=0.6,
                cloud_coverage=0.85, col_cloud_lit="#C8704A", col_cloud_shadow="#3A3A4C"),
    # The lagoon: still, then the escape's first ripples round the barges (low, short waves).
    "sea": {"y": -0.6, "tide_line_y": -0.6, "sea_glow": 0.08, "material": LACQUER_LAGOON,
            "waves": [(200.0, 2.2, 0.02, 0.15), (250.0, 1.3, 0.012, 0.12)]},
    "pieces": [
        {"glb": KIT + "pursuit_barge.glb", "at": (PURSUIT_AT[0], -0.6, PURSUIT_AT[1]), "yaw": 0.0, "structure": True},
        {"glb": KIT + "bowl_dome.glb", "at": (-38.0, -0.6, -62.0), "yaw": 15.0, "scale": 1.6},
        {"glb": KIT + "bowl_dome.glb", "at": (12.0, -0.6, -95.0), "yaw": 40.0, "scale": 2.2},
        {"glb": KIT + "bowl_dome.glb", "at": (-85.0, -0.6, -110.0), "yaw": 70.0, "scale": 1.9},
        {"glb": KIT + "bowl_dome.glb", "at": (58.0, -0.6, -70.0), "yaw": 5.0, "scale": 1.4},
    ],
    "extra_glbs": [KIT + "ansedra_far_domes_lit.glb"],
    "scatters": [],
    "hints": {
        "wide_high": ((-1.5, 7.5, 13.5), (0.0, 0.8, -3.0)),
        "party_side": ((5.6, 1.7, 4.5), (-1.5, 1.0, -0.5)),
        "foe_side": ((-5.6, 1.7, 4.0), (1.5, 1.0, 0.0)),
        "the_engine": ((0.5, 2.0, -2.0), (PURSUIT_AT[0] + 5.0, 1.6, PURSUIT_AT[1])),
        "the_city_watching": ((2.0, 1.2, 3.0), (-20.0, 8.0, -80.0)),
    },
    "anchors": {"BossAnchor": (PURSUIT_AT[0] - 2.5, -0.2, PURSUIT_AT[1] + 0.6)},
}

# ---------------------------------------------------------------------------------------------
# M3-ENV-722: Sefir's Abiding guard in the Drowned Choir at moonrise (drowned_choir.py; pale_rim.md §2)
# ---------------------------------------------------------------------------------------------
def _choir():
    import drowned_choir  # noqa: PLC0415

    return drowned_choir


CHOIR_RING_R = 44.0
CHOIR_SINGERS = 10
PALE_RIM_NIGHT = {  # the colour script's `pale_rim` look (absorption x0.8) at night: the deep darkened under the moon
    "name": "arena_pale_rim_night", "shader": "res://game/shaders/water/water_ocean.gdshader",
    "params": [("col_deep", "#2E4C50"), ("col_scatter_shallow", "#7FB8B4"), ("absorption_per_m", "Vector3(2, 0.5, 0.42)"),
               ("absorption_scale", 0.8), ("scatter_energy", 0.12), ("caustic_strength", 0.0), ("col_foam", "#EEF4F4"),
               ("col_sss", "#7FB8B4"), ("foam_crest_threshold", 0.95), ("roughness_far", 0.04), ("use_caustics", "false"),
               ("use_ssr", "true"), ("use_sss", "false")]}


def _choir_arena() -> dict:
    dc = _choir()
    singers = []
    for k in range(CHOIR_SINGERS):
        th = 2 * math.pi * (k + 0.5) / CHOIR_SINGERS
        x, z = math.cos(th) * CHOIR_RING_R, math.sin(th) * CHOIR_RING_R
        singers.append({"glb": KIT + "choir_singer.glb", "at": (round(x, 3), dc.SAND_Y, round(z, 3)),
                        "yaw": round(math.degrees(math.atan2(-math.cos(th), -math.sin(th))), 3), "structure": True})
    return {
        "id": "drowned_choir_ring",
        "sub_frame": "ch16",
        "ground": "deck",
        "ground_glb": KIT + "choir_amphitheatre.glb",
        "lut": "res://assets/environments/arenas/drowned_choir_ring/lut_ch16_choir.png",
        # pale_rim.md §0 (the Choir at moonrise): the moon low behind the enemy line #D2DFFF 0.35, fill #2A3A4E 0.25,
        # the pale_rim water at night, sea-glow 0.1, exposure 1.1, lut_ch16_choir. The moon stands in the gap between
        # two singers (az 306 bisects one: they stand at 18 + 36k deg) and at 12 deg, so no singer's shadow (24 m tall)
        # and not the tiers' rim falls on the dais: at 9 deg / 320 one lay across the whole party (fca9987's render).
        "sun": {"elev": 12.0, "az": 306.0, "color": "#D2DFFF", "energy": 0.35, "max_distance": 80.0, "moon": True},
        "fill": {"color": "#2A3A4E", "energy": 0.25},
        "exposure": 1.1,
        "glow": (0.5, 0.06, 1.0),
        "fog": {"color": "#3A4A5A", "density": 0.003, "sky_affect": 0.0, "height": 0.0, "height_density": 0.0},
        "sky_shader": "res://game/shaders/environment/env_sky_night.gdshader",
        "sky": {"col_zenith": "#0E1626", "col_horizon": "#3A4A60", "col_ground": "#2E4C50", "moon_disc_energy": 10.0,
                "col_moon": "#D2DFFF"},
        "sea": {"y": dc.WATER_Y, "tide_line_y": dc.WATER_Y, "sea_glow": 0.1, "material": PALE_RIM_NIGHT,
                "waves": [(30.0, 4.0, 0.006, 0.08), (110.0, 2.0, 0.003, 0.05)]},
        "pieces": singers,
        "extra_glbs": [KIT + "pale_rim_flats.glb"],
        "scatters": [],
        "hints": {
            "wide_high": ((-1.5, 7.5, 13.5), (0.0, 0.8, -3.0)),
            "party_side": ((5.6, 1.7, 4.5), (-1.5, 1.0, -0.5)),
            "foe_side": ((-5.6, 1.7, 4.0), (1.5, 1.0, 0.0)),
            "the_mouths": ((1.0, 0.8, 3.0), (-10.0, 22.0, -40.0)),
            "the_ring": ((0.0, 6.0, 12.0), (-20.0, 10.0, -50.0)),
        },
    }


CHOIR_ARENA = _choir_arena()

# ---------------------------------------------------------------------------------------------
# M3-ENV-726: Warden Hesper Oan and Ilsabet Rue on the Iskarra Lamp Spire's crown at nightfall (iskarra_spire.py;
# iskarra.md §3)
# ---------------------------------------------------------------------------------------------
def _spire():
    import iskarra_spire  # noqa: PLC0415

    return iskarra_spire


SPIRE_CROWN = {
    "id": "iskarra_spire_crown",
    "sub_frame": "ch19",
    "ground": "deck",
    "ground_glb": KIT + "spire_crown_floor.glb",
    "lut": "res://assets/environments/arenas/iskarra_spire_crown/lut_ch19_spire.png",
    # Colour script ch19 (the spire climbed into night): the afterglow low in the west #FF9F46 0.7 behind the party,
    # fill #5A7FA8 0.4, the sky #22304E over a #C8763E horizon, the warm fog thin; the anchor-engine's bound teal
    # the only lamp. The drowned city 112 m below. The afterglow is behind the party (+x: az 100 in the arena's frame),
    # so the anchor-engine's long shadow falls away from the slots (az 285 laid it across the enemy line).
    "sun": {"elev": 2.0, "az": 100.0, "color": "#FF9F46", "energy": 0.7, "max_distance": 60.0},
    "fill": {"color": "#5A7FA8", "energy": 0.4},
    "exposure": 1.0,
    "glow": (0.6, 0.08, 1.0),
    "fog": {"color": "#8A6A5A", "aerial": 0.6, "density": 0.0016, "sky_affect": 0.15, "height": 0.0,
            "height_density": 0.0},
    "sky_shader": LOW_SUN_SKY,
    "sky": dict(CORROW_SKY, col_zenith="#22304E", col_horizon_sun="#C8763E", col_horizon_away="#3E4A66",
                col_ground="#1A2232", sky_energy=0.9, sun_disc_energy=0.0, halo_energy=0.7, glow_energy=0.6,
                cloud_coverage=0.3, col_cloud_lit="#E08A5A", col_cloud_shadow="#2E3650"),
    "sea": {"y": -_spire().ELEVATION_M, "tide_line_y": -_spire().ELEVATION_M, "sea_glow": 0.06},
    "pieces": [{"glb": KIT + "anchor_engine.glb", "at": (_spire().ENGINE_AT[0], 0.0, _spire().ENGINE_AT[1]),
                "yaw": 0.0, "structure": True}],
    "extra_glbs": [(KIT + "iskarra_far_towers.glb", (0.0, -_spire().ELEVATION_M, 0.0))],
    "scatters": [],
    "lamp_spec": {"color": "#4FB3B0", "energy": 2.6, "range_m": 14.0, "attenuation": 1.2},
    "lamps": [{"at": (_spire().ENGINE_AT[0], 3.6, _spire().ENGINE_AT[1]), "flame": False, "shadow": True}],
    "hints": {
        "wide_high": ((-1.5, 7.5, 13.5), (0.0, 0.8, -3.0)),
        "party_side": ((5.6, 1.7, 4.5), (-1.5, 1.0, -0.5)),
        "foe_side": ((-5.6, 1.7, 4.0), (1.5, 1.0, 0.0)),
        "the_engine": ((-1.0, 2.0, 2.0), (_spire().ENGINE_AT[0], 3.5, _spire().ENGINE_AT[1])),
        "the_city_below": ((6.0, 2.5, 6.0), (40.0, -90.0, -60.0)),
    },
}


# ---------------------------------------------------------------------------------------------
# M3-ENV-727: the Cage in the Undertow's last remembered room (undertow_layers.py; undertow_layers.md §2)
# ---------------------------------------------------------------------------------------------
HELD_PILLARS = ((-6.5, -4.5), (-4.0, -6.8), (-7.6, -1.0), (-1.3, -7.4))  # round the Cage, behind the enemy line
UNDERTOW_CAGE = {
    "id": "undertow_cage",
    "sub_frame": "ch20",
    "ground": "deck",
    "ground_glb": KIT + "memory_island.glb",
    "lut": "res://assets/environments/arenas/undertow_cage/lut_ch20_abyss.png",
    # Colour script ch20: no sun; key #C4D6FF 0.8 (the motes' cold light from above), fill #061A2B 0.2, fog #0E3A48
    # dense, sky #020610 / #0E2A3A, exposure 1.1, lut_ch20_abyss; the held pillars' cyan the practical light.
    "sun": {"elev": 70.0, "az": 200.0, "color": "#C4D6FF", "energy": 0.8, "max_distance": 60.0, "moon": True},
    "fill": {"color": "#061A2B", "energy": 0.2},
    "exposure": 1.1,
    "glow": (0.7, 0.1, 0.9),
    "fog": {"color": "#0E3A48", "density": 0.02, "sky_affect": 0.6, "height": 0.0, "height_density": 0.0},
    "sky_shader": "res://game/shaders/environment/env_sky_night.gdshader",
    "sky": {"col_zenith": "#020610", "col_horizon": "#0E2A3A", "col_ground": "#020610"},
    "sea": {"y": -60.0, "tide_line_y": -60.0, "sea_glow": 0.15},
    "pieces": [{"glb": KIT + "held_pillar.glb", "at": (x, 0.0, z), "yaw": round(37.0 * k, 1), "structure": True}
               for k, (x, z) in enumerate(HELD_PILLARS)] + [
        {"glb": KIT + "memory_kitchen.glb", "at": (-17.0, -5.0, -22.0), "yaw": 25.0},
        {"glb": KIT + "memory_market.glb", "at": (19.0, 3.5, -27.0), "yaw": -30.0},
        {"glb": KIT + "memory_stands.glb", "at": (-30.0, 7.0, -44.0), "yaw": 40.0},
        {"glb": KIT + "memory_island.glb", "at": (34.0, -12.0, -55.0), "yaw": 10.0, "scale": 0.7},
        # M5-A3P-1400: the rest of act3_ch20's rooms (the second kitchen was a stand-in for them).
        {"glb": KIT + "memory_gallery.glb", "at": (8.0, 12.0, -60.0), "yaw": 160.0, "scale": 0.9},
        {"glb": KIT + "memory_terrace.glb", "at": (-40.0, -9.0, -18.0), "yaw": 70.0},
        {"glb": KIT + "memory_square.glb", "at": (36.0, 9.0, -28.0), "yaw": -55.0},
        {"glb": KIT + "memory_landing.glb", "at": (-14.0, 16.0, -46.0), "yaw": 20.0},  # M5-A3P-1402: a rest
    ],
    "scatters": [],
    "lamp_spec": {"color": "#7FC6D9", "energy": 1.8, "range_m": 8.0, "attenuation": 1.3},
    "lamps": [{"at": (x, 4.0, z), "flame": False, "shadow": k == 0} for k, (x, z) in enumerate(HELD_PILLARS)],
    "hints": {
        "wide_high": ((-1.5, 7.5, 13.5), (0.0, 0.8, -3.0)),
        "party_side": ((5.6, 1.7, 4.5), (-1.5, 1.0, -0.5)),
        "foe_side": ((-5.6, 1.7, 4.0), (1.5, 1.0, 0.0)),
        "the_rooms": ((4.0, 1.5, 6.0), (-17.0, -3.0, -22.0)),
        "the_cage": ((0.5, 1.6, 3.0), (-5.0, 3.0, -5.0)),
    },
}



# ---------------------------------------------------------------------------------------------
# M3-ENV-728: the Heart of the Undertow, Sefir's fight (undertow_heart.py; undertow_layers.md §3). Two states:
# `undertow_heart` (phases 1-2, held: lut_ch20_abyss, the column's cyan) and `undertow_heart_letting` (phase 3, the
# Letting: lut_ch21_heart, the colour script's warm key and rim).
# ---------------------------------------------------------------------------------------------
def _heart():
    import undertow_heart  # noqa: PLC0415

    return undertow_heart


HEART_HINTS = {
    "wide_high": ((-1.5, 7.5, 13.5), (0.0, 0.8, -3.0)),
    "party_side": ((5.6, 1.7, 4.5), (-1.5, 1.0, -0.5)),
    "foe_side": ((-5.6, 1.7, 4.0), (1.5, 1.0, 0.0)),
    "the_column": ((3.0, 1.2, 6.0), (_heart().COLUMN_AT[0], 12.0, _heart().COLUMN_AT[1])),
    "the_eyewall": ((-2.0, 1.6, 4.0), (60.0, 40.0, -140.0)),
}
UNDERTOW_HEART = {
    "id": "undertow_heart",
    "sub_frame": "ch21",
    "ground": "deck",
    "ground_glb": KIT + "heart_floor.glb",
    "lut": "res://assets/environments/arenas/undertow_heart/lut_ch20_abyss.png",
    # Colour script ch21, phases 1-2 (held): no sun; the motes' cold key from above #C4D6FF 0.8, fill #0E4A55 0.3,
    # sky #020610 / #061A2B, fog #0E2A3A, exposure 1.05, lut_ch20_abyss; Imra's column the practical light, cyan.
    "sun": {"elev": 70.0, "az": 200.0, "color": "#C4D6FF", "energy": 0.8, "max_distance": 60.0, "moon": True},
    "fill": {"color": "#0E4A55", "energy": 0.3},
    "exposure": 1.05,
    "glow": (0.7, 0.1, 0.9),
    "fog": {"color": "#0E2A3A", "density": 0.008, "sky_affect": 0.5, "height": 0.0, "height_density": 0.0},
    "sky_shader": "res://game/shaders/environment/env_sky_night.gdshader",
    "sky": {"col_zenith": "#020610", "col_horizon": "#061A2B", "col_ground": "#020610"},
    "sea": {"y": _heart().WATER_Y, "tide_line_y": _heart().WATER_Y, "sea_glow": 0.15},
    "pieces": [{"glb": KIT + "heart_column.glb", "at": (_heart().COLUMN_AT[0], 0.0, _heart().COLUMN_AT[1]),
                "yaw": 0.0, "structure": True}],
    "extra_glbs": [KIT + "heart_eyewall.glb"],
    "scatters": [],
    "lamp_spec": {"color": "#7FC6D9", "energy": 3.0, "range_m": 18.0, "attenuation": 1.1},
    "lamps": [{"at": (_heart().COLUMN_AT[0], 3.0, _heart().COLUMN_AT[1]), "flame": False, "shadow": True}],
    "hints": HEART_HINTS,
}
# Phase 3, the Letting: the colour script's warm key #FFDCBF 1.2 from the column's side, the rim #FFE9B8 2.0 its
# lamp; lut_ch21_heart.
UNDERTOW_HEART_LETTING = dict(
    UNDERTOW_HEART, id="undertow_heart_letting",
    lut="res://assets/environments/arenas/undertow_heart_letting/lut_ch21_heart.png",
    sun={"elev": 35.0, "az": 140.0, "color": "#FFDCBF", "energy": 1.2, "max_distance": 60.0},
    lamp_spec={"color": "#FFE9B8", "energy": 2.0, "range_m": 22.0, "attenuation": 1.0},
    sky={"col_zenith": "#061A2B", "col_horizon": "#3A3428", "col_ground": "#020610"},
)

ARENAS = {a["id"]: a for a in (TIDELINE, CAUSEWAY, CAUSEWAY_ROUTE, DERELICT_DECK, ASH_TERRACE, UNDERWAY_TOWER,
                               RAFT_MORNING, SHOALS, CAMP, WALLHEAD_STORM, WALLHEAD_HOIST, WALLHEAD_SURGE, HEADLAND, TIER_HALL, KETH_ARENA,
                               LOWLIGHT_ARENA, VEY_ARENA, FEN_ARENA, BRIDAL_ARENA, ANSEDRA_ESCAPE, CHOIR_ARENA,
                               SPIRE_CROWN, UNDERTOW_CAGE, UNDERTOW_HEART, UNDERTOW_HEART_LETTING)}


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


def _env_props(sc: Scene, a: dict, name: str) -> list[str]:
    """The arena's (or a zone grade's) sky as sub-resources in `sc`, and its Environment's property lines."""
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
    return [
        f'resource_name = "{name}"',
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
    ]


def write_environment(a: dict, out: Path) -> Path:
    """A zone grade's Environment as a standalone .tres (the same sky, fog, tonemap and LUT as an arena's)."""
    sc = Scene()
    props = _env_props(sc, a, a["sub_frame"])
    lines = [f"[gd_resource type=\"Environment\" load_steps={len(sc.ext) + len(sc.sub) + 1} format=3]", ""]
    lines += [f'[ext_resource type="{kind}" path="{path}" id="{rid}"]' for path, (kind, rid) in sc.ext.items()]
    lines += [""] + [s + "\n" for s in sc.sub] + ["[resource]"] + props
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def write_arena(a: dict) -> Path:
    sc = Scene()
    script = sc.res("Script", "res://game/world/arenas/battle_arena_root.gd")
    props = _env_props(sc, a, f"{a['id']}_{a['sub_frame']}")
    sc.sub.append("\n".join(['[sub_resource type="Environment" id="Env"]', *props]))
    sc.node(a["id"].title().replace("_", ""), "Node3D", None,
            {"script": f'ExtResource("{script}")', "arena_id": f'&"{a["id"]}"', "sub_frame": f'&"{a["sub_frame"]}"'})
    sc.node("WorldEnvironment", "WorldEnvironment", ".", {"environment": 'SubResource("Env")'})
    s = a["sun"]
    sc.node("Sun", "DirectionalLight3D", ".", {
        "transform": sun_xform(s["elev"], s["az"]), "light_color": hexc(s["color"]), "light_energy": s["energy"],
        "shadow_enabled": "true", "shadow_bias": 0.03, "shadow_normal_bias": 1.0, "shadow_blur": 1.0,
        "directional_shadow_mode": 2, "directional_shadow_split_1": 0.06, "directional_shadow_split_2": 0.18,
        "directional_shadow_split_3": 0.45, "directional_shadow_max_distance": s.get("max_distance", 120.0),
        # M3-ENV-1323: an underwater sun's light is diffused by the water above: soft-edged pools, not hard panes.
        **({"light_angular_distance": s["angular_deg"], "shadow_blur": s["shadow_blur"]} if "angular_deg" in s else {})})
    sea = a["sea"]
    sea_props = {
        "transform": f"Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, {sea['y']}, 0)",
        "script": f'ExtResource("{sc.res("Script", "res://game/world/arenas/arena_sea.gd")}")'}
    if "waves" not in sea:
        sea_props["wave_set"] = f'ExtResource("{sc.res("Resource", WAVES)}")'
    else:  # M3-ENV-716: an arena's own still water (an interior), [(direction_deg, wavelength_m, amplitude_m, steepness)]
        comp = sc.res("Script", "res://game/world/water/wave_component.gd")
        ids = []
        for k, (d, wl, amp, st) in enumerate(sea["waves"]):
            sc.sub.append(f'[sub_resource type="Resource" id="SeaWave{k}"]\nscript = ExtResource("{comp}")\n'
                          f"direction_deg = {d}\nwavelength_m = {wl}\namplitude_m = {amp}\nsteepness = {st}")
            ids.append(f'SubResource("SeaWave{k}")')
        sc.sub.append(f'[sub_resource type="Resource" id="SeaWaves"]\n'
                      f'script = ExtResource("{sc.res("Script", "res://game/world/water/wave_set.gd")}")\n'
                      f'components = Array[ExtResource("{comp}")]([{", ".join(ids)}])\namplitude_scale = 1.0')
        sea_props["wave_set"] = 'SubResource("SeaWaves")'
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
    if "ground_at" in a:  # the ground glb placed off the origin (the Underway's terrace apron), turned (the wall-head)
        ground_props["transform"] = (yaw_xform(a["ground_yaw"], a["ground_at"]) if "ground_yaw" in a
                                     else _xyz(a["ground_at"]))
    sc.node("Ground", None, ".", ground_props, instance=sc.res("PackedScene", a["ground_glb"]))
    if "disc" in a:
        cx, cz = a["disc"]["center"]
        sc.node("Disc", None, ".", {"transform": f"Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {cx}, 0, {cz})"},
                instance=sc.res("PackedScene", a["disc"]["glb"]))
    for k, glb in enumerate(a.get("extra_glbs", [])):
        if isinstance(glb, tuple):  # M3-ENV-726: (glb, (x, y, z)), a backdrop set off the origin (the city below)
            glb, at = glb
            sc.node(f"Kit{k}", None, ".", {"transform": _xyz(at)}, instance=sc.res("PackedScene", glb))
            continue
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
    flame, flame_r = None, spec.get("flame_radius_m", FLAME_KIT_RADIUS_M)
    if any(lp.get("flame", False) for lp in lamps):
        if spec["color"].upper() in FLAME_KIT_COLOURS:
            flame = sc.res("PackedScene", KIT + "lamp_flame.glb")
        else:  # a flame the kit has no piece for yet (Lowlight's bound light, Act II): the emissive bead
            sc.sub.append("\n".join([
                '[sub_resource type="StandardMaterial3D" id="FlameMat"]', "shading_mode = 0",
                f"albedo_color = {hexc(spec['color'])}", "emission_enabled = true", f"emission = {hexc(spec['color'])}",
                f"emission_energy_multiplier = {spec['flame_energy']}"]))
            sc.sub.append("\n".join([
                '[sub_resource type="SphereMesh" id="FlameMesh"]', 'material = SubResource("FlameMat")',
                f"radius = {flame_r}", f"height = {round(flame_r * 2.4, 4)}", "radial_segments = 12", "rings = 6"]))
    # `lamp_parent` "." with a `lamp_name` writes the lights at the arena's root under that name (the burning
    # camp's FireLight<k>, M3-BPR-03's contract), else they go under a Lamps node as Lamp<k>.
    parent, name = a.get("lamp_parent", "Lamps"), a.get("lamp_name", "Lamp")
    if parent == "Lamps":
        sc.node("Lamps", "Node3D", ".", {})
    scale = spec.get("scale", 1.0)  # the arena's lamp scale (a mood's lamp_scale)
    for k, lp in enumerate(lamps):
        at = tuple(round(float(v), 3) for v in lp["at"])
        energy = round(lp.get("energy", spec["energy"]) * (1.0 if lp.get("own", False) else scale), 3)
        props = {"transform": _xyz(at), "light_color": hexc(lp.get("color", spec["color"])),
                 "light_energy": energy, "omni_range": lp.get("range", spec["range_m"]),
                 "omni_attenuation": spec["attenuation"],
                 # Never light the volumetric fog: an arena can host a dense FogVolume (a boss's god rays, the
                 # Reefball's shafts, the underwater rig's), and a lamp at the default 1.0 bands it bright
                 # (the Lead's fog-lamp rule; docs/kb/tech/battle_arenas.md).
                 "light_volumetric_fog_energy": 0.0}
        if lp.get("shadow", False):
            props["shadow_enabled"] = "true"
            props["shadow_bias"] = 0.05
        if lp.get("light", True):  # a votive's flame alone (`light` false) has no light of its own
            sc.node(f"{name}{k}", "OmniLight3D", parent, props)
        if lp.get("flame", False) and flame is None:
            sc.node(f"Flame{k}", "MeshInstance3D", parent, {"transform": _xyz(at), "cast_shadow": 0,
                                                             "mesh": 'SubResource("FlameMesh")'})
        elif lp.get("flame", False):
            # The kit's flame (M3-ENV-746), its base a little under the lamp's point so the flame stands on it.
            s = flame_r / FLAME_KIT_RADIUS_M
            base = (at[0], round(at[1] - flame_r * 1.2, 4), at[2])
            sc.node(f"Flame{k}", None, parent, {"transform": f"Transform3D({s:g}, 0, 0, 0, {s:g}, 0, 0, 0, {s:g}, "
                                                                f"{base[0]:g}, {base[1]:g}, {base[2]:g})"},
                    instance=flame)


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
