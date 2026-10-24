"""Writes the Oruvel raft-town kit preview (M3-ENV-07): game/levels/_tests/oruvel_kit/.

    python3 assets_src/environments/kits/oruvel/ov_preview_layout.py

Writes three files, all generated (edit this script, not them):
* `oruvel_layout.json`: HalunaDresser's format (hymn-zone-layout/1, no terrain: every piece carries its own "y"),
  the town composed for the design notes' key shots (oruvel.md §0, §4), plus "shots" (each preview camera's eye,
  target, lens) and "anchors" (the swap-in note's points: the dive well, the tether, the counters).
* `oruvel_drowned_layout.json`: the Oruvel Underway kit's crown pieces (its preview layout's tower rows above F12,
  read-only from ou_preview_layout.py) in the same frame, so the drowned city shows under the dive raft.
* `oruvel_preview.tscn`: the HalunaMood rig at the colour script's `ch01` (10:30, sun 58 deg / 120 deg), the sea,
  the tide, both dressers and one HalunaShotCamera per shot.

The frame is the Underway's (oruvel_underway.md §0): x east, z south (north = -Z), the sea surface at y 0; the
Underway's tether drops into the tower's crown at (-9.9, 5.2), and its `hull_keels` (the neighbour raft seen from
below in U01) are at (-3, 11), yaw 70 about their own long axis (local X) = yaw -20 for this kit's hulls (local Z).
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import ov_cabins as ocab  # noqa: E402
import ov_heroes as oh  # noqa: E402
import ov_hulls as ohl  # noqa: E402
import ov_common as oc  # noqa: E402
from ov_common import kc  # noqa: E402

OUT_DIR = ROOT / "game" / "levels" / "_tests" / "oruvel_kit"
RES_DIR = "res://game/levels/_tests/oruvel_kit/"
TETHER = (-9.9, 5.2)  # the Underway's tether into the crown (ou_preview_layout.dressing)
NEIGHBOUR = (-3.0, 11.0, -20.0)  # the Underway's hull_keels, as a raft of this kit
GULL_YAW = -70.0  # the carving's +X to (0.34, 0, 0.94): out to sea, south-south-east
GULL_JITTER = 8.0
DECK_Y = {"raft_deck": ohl.RAFT_DECK_Y, "raft_deck_small": ohl.RAFT_SMALL_Y, "dive_raft": oh.DIVE_DECK_Y,
          "net_pen": ohl.NET_PEN_Y}
DECK_HALF = {"raft_deck": (4.5, 3.5), "raft_deck_small": (3.0, 2.5), "dive_raft": (3.5, 3.0), "net_pen": (6.0, 6.0)}
KIT_ROW_Z = (10.0, -6.0, -24.0)  # front (small pieces), back (hulls and rafts), heroes
KIT_ROW_X0 = 70.0

_rng = kc.rng_for("oruvel_preview_layout", 7)


def put(piece: str, x: float, y: float, z: float, yaw: float = 0.0, **kw) -> dict:
    d = {"piece": piece, "at": [round(x, 3), round(z, 3)], "y": round(y, 3), "yaw_deg": round(yaw, 2)}
    d.update(kw)
    return d


def local(x: float, z: float, yaw: float, lx: float, lz: float) -> tuple[float, float]:
    """World (x, z) of a piece's local (lx, lz), the piece at (x, z) turned `yaw` deg (Godot's Basis(UP, yaw))."""
    a = math.radians(yaw)
    return x + lx * math.cos(a) + lz * math.sin(a), z - lx * math.sin(a) + lz * math.cos(a)


def gull(x: float, y: float, z: float, scale: float = 1.0) -> dict:
    yaw = GULL_YAW + float(_rng.uniform(-GULL_JITTER, GULL_JITTER))
    d = put("lintel_gull_open", x, y, z, yaw)
    if scale != 1.0:
        d["scale"] = scale
    return d


def on_deck(raft: dict, piece: str, lx: float, lz: float, yaw: float = 0.0, **kw) -> dict:
    """A piece standing on a raft's deck at the raft's local (lx, lz), turned `yaw` relative to the raft."""
    x, z = local(raft["at"][0], raft["at"][1], raft["yaw_deg"], lx, lz)
    return put(piece, x, raft["y"] + DECK_Y[raft["piece"]], z, raft["yaw_deg"] + yaw, **kw)


def keelroof_cabin(raft: dict, lx: float, lz: float, yaw: float = 0.0, **kw) -> list[dict]:
    """A keel-roof cabin on a raft and the open-throat gull on its ridge."""
    cab = on_deck(raft, "cabin_keelroof", lx, lz, yaw, **kw)
    L, _B, D, eave, sheer = ocab.KEELROOF
    gz = ocab.KEELROOF_GULL_Z if abs(((cab["yaw_deg"] + 180.0) % 360.0) - 180.0) < 90.0 else -ocab.KEELROOF_GULL_Z
    gx, gzw = local(cab["at"][0], cab["at"][1], cab["yaw_deg"], 0.0, gz)
    return [cab, gull(gx, cab["y"] + oc.keel_roof_ridge(gz, L, D, eave, sheer), gzw)]


def patched_cabin(raft: dict, lx: float, lz: float, yaw: float = 0.0) -> list[dict]:
    cab = on_deck(raft, "cabin_patched", lx, lz, yaw)
    gx, gz = local(cab["at"][0], cab["at"][1], cab["yaw_deg"], -1.85, 0.0)
    return [cab, gull(gx, cab["y"] + 3.12, gz)]


def bridge(a: tuple[float, float], b: tuple[float, float], y: float) -> dict:
    """A plank_bridge centred between two deck-edge points (its 6 m span overlaps the decks when the gap is short)."""
    dx, dz = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dz)
    ux, uz = dx / n, dz / n
    cx, cz = (a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5
    sx, sz = cx - ux * ohl.BRIDGE_SPAN * 0.5, cz - uz * ohl.BRIDGE_SPAN * 0.5
    return put("plank_bridge", sx, y, sz, math.degrees(math.atan2(ux, uz)))


def town() -> list[dict]:
    out: list[dict] = []
    # The dive moorings on the seaward (south) edge: the dive raft over the tether, its neighbour (the Underway's
    # hull_keels), the landing, the scale-hull.
    dive = put("dive_raft", TETHER[0], 0.0, TETHER[1], 0.0)
    neighbour = put("raft_deck_small", NEIGHBOUR[0], 0.0, NEIGHBOUR[1], NEIGHBOUR[2])
    landing = put("raft_deck_small", 1.5, 0.0, -1.0, 0.0)
    gullraft = put("raft_deck_small", -18.5, 0.0, -2.5, 0.0)
    out += [dive, neighbour, landing, gullraft]
    out.append(put("scale_hull", 7.5, 0.0, -1.0, 180.0))
    out += keelroof_cabin(gullraft, 0.0, 0.2, -90.0, materials={"ov_paint_teal": "ov_paint_ochre"})
    out.append(on_deck(neighbour, "salvage_heap", 0.2, -0.6, 90.0))
    out.append(on_deck(neighbour, "net_frame", 2.5, 0.0, 0.0))
    out.append(on_deck(landing, "stall_awning", -1.2, 0.3, 180.0))
    out.append(bridge((-12.2, 2.3), (-16.4, -0.1), oh.DIVE_DECK_Y))
    out.append(bridge((0.0, -3.4), (0.0, -8.6), ohl.RAFT_SMALL_Y))
    # Row A (z about -12): three cabin rafts and their bridges.
    ra = put("raft_deck", -16.5, 0.0, -12.5, 0.0)
    rb = put("raft_deck", -3.0, 0.0, -12.0, 3.0)
    rc = put("raft_deck", 11.0, 0.0, -13.0, -3.0)
    out += [ra, rb, rc]
    out += keelroof_cabin(ra, -2.2, 0.2)
    out += patched_cabin(ra, 2.4, 0.4, 180.0)
    out += keelroof_cabin(rb, -2.0, 0.2, 0.0, materials={"ov_paint_teal": "ov_paint_red"})
    out.append(on_deck(rb, "stall_awning", 2.6, -1.6, 180.0))
    out.append(on_deck(rb, "salvage_heap", 2.4, 1.9, 0.0))
    out += patched_cabin(rc, -2.3, 0.6, 0.0)
    out.append(on_deck(rc, "stall_awning", 2.2, -1.6, 180.0))
    out.append(on_deck(rc, "stall_awning", 2.2, 1.6, 180.0))
    out.append(bridge((-12.0, -12.3), (-7.5, -12.2), ohl.RAFT_DECK_Y))
    out.append(bridge((1.5, -12.6), (6.5, -12.8), ohl.RAFT_DECK_Y))
    out.append(bridge((-18.5, -9.0), (-18.5, -5.0), ohl.RAFT_SMALL_Y))
    # The second mooring (west): Kell's chandlery, its counter facing the walkway raft east of it.
    walk = put("raft_deck", -31.0, 0.0, -14.0, 0.0)
    out += [walk, put("chandlery", -38.5, 0.0, -14.0, 0.0)]
    out.append(gull(-38.5, oh.CHANDLERY_DECK_Y + 2.22 + oh.CHANDLERY_ROOF[2] + 0.08, -14.0 + 0.9))
    out += patched_cabin(walk, 2.4, -1.4, -90.0)
    out.append(on_deck(walk, "net_frame", -1.5, 2.8, 90.0))
    out.append(bridge((-26.5, -13.6), (-21.0, -13.0), ohl.RAFT_DECK_Y))
    # The cookboat lane (z about -21): cookboats and outriggers moored along it.
    out += [put("cookboat", -5.5, 0.0, -21.2, 92.0), put("cookboat", 4.0, 0.0, -20.8, 86.0),
            put("hull_outrigger", -13.5, 0.0, -20.6, 82.0), put("hull_outrigger", 13.0, 0.0, -21.5, 97.0,
                                                                    materials={"ov_hull_paint": "ov_paint_red"})]
    # Row B: the keel-hull at the town's middle (stern west), a raft from row A to its side, the net lanes.
    out.append(put("keel_hull", -16.0, 0.0, -36.0, -90.0))
    kx, kz = local(-16.0, -36.0, -90.0, 0.0, 6.7)
    out.append(gull(kx, oh.KEEL_HULL_RIDGE, kz, 1.35))
    rk = put("raft_deck_small", -16.0, 0.0, -24.5, 0.0)
    out += [rk, bridge((-16.0, -16.2), (-16.0, -21.8), ohl.RAFT_SMALL_Y),
            bridge((-15.5, -27.2), (-15.5, -32.6), ohl.RAFT_SMALL_Y)]
    out.append(on_deck(rk, "salvage_heap", 1.0, 0.4, 20.0))
    rd = put("raft_deck", 3.5, 0.0, -32.5, 0.0)
    out += [rd] + keelroof_cabin(rd, -2.0, 0.0, 0.0, materials={"ov_paint_teal": "ov_paint_white"})
    out += patched_cabin(rd, 2.4, 0.2, 180.0)
    nl1 = put("raft_deck", 19.0, 0.0, -42.0, 90.0)
    nl2 = put("raft_deck", 19.0, 0.0, -51.5, 90.0)
    out += [nl1, nl2, on_deck(nl1, "net_frame", 0.0, -1.5, 90.0), on_deck(nl1, "net_frame", 0.0, 1.5, 90.0),
            on_deck(nl2, "net_frame", 0.0, -1.6, 90.0), on_deck(nl2, "net_frame", 0.0, 1.4, 90.0)]
    out.append(bridge((8.0, -33.0), (14.5, -38.5), ohl.RAFT_DECK_Y))
    out += keelroof_cabin(put("raft_deck_small", -32.0, 0.0, -31.0, 8.0), 0.0, 0.0)
    out.append(put("raft_deck_small", -32.0, 0.0, -31.0, 8.0))
    # The Reefball practice pen on its own at the east edge, a bridge from row A.
    out.append(put("net_pen", 27.5, 0.0, -11.5, 0.0))
    out.append(bridge((15.5, -12.8), (21.5, -12.2), ohl.RAFT_DECK_Y))
    # Single hulls moored round; the town beyond the preview.
    out += [put("hull_cabin", -25.0, 0.0, 8.0, 10.0, materials={"ov_hull_paint": "ov_paint_ochre"}),
            put("hull_cabin", 15.5, 0.0, 6.5, -14.0), put("hull_outrigger", -1.5, 0.0, 4.6, 168.0),
            put("hull_outrigger", -26.5, 0.0, -21.0, 74.0, materials={"ov_hull_paint": "ov_paint_teal"}),
            put("hull_cabin", -44.0, 0.0, -24.0, 4.0, materials={"ov_hull_paint": "ov_paint_white"})]
    out += [put("town_far", -6.0, 0.0, -80.0, 0.0, lod1_from_m=160.0),
            put("town_far", 46.0, 0.0, -72.0, 24.0, lod1_from_m=160.0),
            put("town_far", -58.0, 0.0, -52.0, -36.0, lod1_from_m=160.0)]
    return out


def kit_row() -> list[dict]:
    """O20: every piece on the open water east of the town: the small pieces each on a raft deck in front, the hulls
    and rafts behind, the two biggest heroes at the back."""
    front = ["cabin_keelroof", "cabin_patched", "stall_awning", "lintel_gull_open", "net_frame", "salvage_heap",
             "plank_bridge"]
    back = ["hull_outrigger", "hull_cabin", "raft_deck_small", "dive_raft", "scale_hull", "cookboat", "chandlery"]
    out = []
    for k, name in enumerate(front):
        x = KIT_ROW_X0 + 9.0 * k  # the rafts touch: one long deck
        out.append(put("raft_deck", x, 0.0, KIT_ROW_Z[0], 0.0))
        if name == "lintel_gull_open":
            out.append(put(name, x, ohl.RAFT_DECK_Y, KIT_ROW_Z[0], -90.0, scale=2.5))
        elif name == "plank_bridge":
            out.append(put(name, x - 3.0, ohl.RAFT_DECK_Y, KIT_ROW_Z[0] + 1.5, 90.0))
        else:
            out.append(put(name, x, ohl.RAFT_DECK_Y, KIT_ROW_Z[0], 0.0))
    for k, name in enumerate(back):
        out.append(put(name, KIT_ROW_X0 - 2.0 + 10.0 * k, 0.0, KIT_ROW_Z[1], 0.0))
    out.append(put("keel_hull", KIT_ROW_X0 + 22.0, 0.0, KIT_ROW_Z[2], 90.0))
    out.append(put("net_pen", KIT_ROW_X0 + 52.0, 0.0, KIT_ROW_Z[2], 0.0))
    return out


def drowned() -> list[dict]:
    """The Underway kit's crown (F13 and F14 rows of its preview layout), read-only, in the same frame."""
    sys.path.insert(0, str(HERE.parent / "oruvel_underway"))
    import ou_preview_layout as ol  # noqa: PLC0415

    ol.terrace()  # seats the Underway's ground (its dressing reads it)
    out = []
    for p in ol.tower():
        if p["y"] >= ol.floor_y(13) - 0.01:
            out.append({k: p[k] for k in p})
    return out


SHOT_NAMES = {"O01": "surfacing", "O02": "scale_hull", "O03": "town_loop", "O08": "keel_hull", "O09": "kell_stall",
              "O10": "lintel_gull", "O19": "dive_mooring", "O20": "kit_row"}
SHOTS = {
    # id: eye, target, vFOV (deg), notes; dof (far distance, transition, blur) where the design wants it.
    "O01": {"eye": (-4.5, 0.45, 23.5), "look": (-3.0, 2.2, -20.0), "fov": 37.8},
    "O02": {"eye": (1.7, 2.2, -0.3), "look": (6.4, 1.95, -1.05), "fov": 27.0},
    "O03": {"eye": (0.0, 2.25, -4.4), "look": (-3.0, 2.4, -30.0), "fov": 53.1},
    "O08": {"eye": (-12.5, 2.35, -14.6), "look": (-17.5, 3.6, -36.0), "fov": 37.8},
    "O09": {"eye": (-34.3, 2.05, -13.4), "look": (-36.9, 1.72, -14.0), "fov": 20.9, "dof": (2.9, 2.5, 0.06)},
    "O10": {"eye": (-13.0, 1.95, 2.6), "look": (-15.45, 4.02, -2.3), "fov": 16.1},
    "O19": {"eye": (-15.5, 5.2, 14.5), "look": (-9.9, 0.0, 4.4), "fov": 46.4},
    "O20": {"eye": (KIT_ROW_X0 + 28.0, 7.5, KIT_ROW_Z[0] + 30.0), "look": (KIT_ROW_X0 + 28.0, 0.0, KIT_ROW_Z[1] + 2.0),
            "fov": 53.1},
}


def anchors() -> dict:
    """The swap-in note's points, world frame."""
    return {
        "dive_well": [TETHER[0], oh.DIVE_DECK_Y, TETHER[1]],
        "underway_tether": [TETHER[0], 0.0, TETHER[1]],
        "scale_counter": [round(7.5 - 1.1, 3), 1.4, -1.0],
        "chandlery_counter": [round(-38.5 + 1.62, 3), round(oh.CHANDLERY_DECK_Y + 1.05, 3), -14.0],
        "chandlery_beacon": [-38.5, 4.9, -15.8],
        "keel_hull_meeting_deck": [round(-16.0 + 4.5, 3), oh.KEEL_DECK_Y, -36.0],
        "net_pen_centre": [27.5, ohl.NET_PEN_Y, -11.5],
    }


def tscn(shots: dict) -> str:
    lines = ['[gd_scene load_steps={steps} format=3]', '',
             '[ext_resource type="Script" path="res://game/levels/ch02/haluna/haluna_mood.gd" id="1_rig"]',
             '[ext_resource type="Script" path="res://game/levels/ch02/haluna/weathering_tide.gd" id="2_tide"]',
             '[ext_resource type="Script" path="res://game/levels/ch02/haluna/haluna_dresser.gd" id="3_dresser"]',
             '[ext_resource type="Script" path="res://game/world/water/water_surface.gd" id="4_water"]',
             '[ext_resource type="Script" path="res://game/world/water/wave_set.gd" id="5_set"]',
             '[ext_resource type="Script" path="res://game/world/water/wave_component.gd" id="6_comp"]',
             f'[ext_resource type="Material" path="{RES_DIR}oruvel_water_material.tres" id="7_water_mat"]',
             f'[ext_resource type="Environment" path="{RES_DIR}oruvel_ch01_environment.tres" id="8_env"]',
             '[ext_resource type="Script" path="res://game/levels/ch02/haluna/haluna_shot_camera.gd" id="9_cam"]',
             '[ext_resource type="Script" path="res://game/world/camera_shot.gd" id="10_shot"]', '']
    waves = [("Calm0", 210.0, 9.0, 0.012, 0.3, 0.0), ("Calm1", 250.0, 4.1, 0.006, 0.4, 2.1),
             ("Calm2", 180.0, 2.2, 0.003, 0.4, 4.0)]
    for wid, d, wl, amp, st, ph in waves:
        lines += [f'[sub_resource type="Resource" id="{wid}"]', 'script = ExtResource("6_comp")', f'direction_deg = {d}',
                  f'wavelength_m = {wl}', f'amplitude_m = {amp}', f'steepness = {st}', f'phase_rad = {ph}', '']
    comps = ", ".join(f'SubResource("{w[0]}")' for w in waves)
    lines += ['[sub_resource type="Resource" id="CalmWaves"]', 'script = ExtResource("5_set")',
              f'components = Array[ExtResource("6_comp")]([{comps}])', 'amplitude_scale = 1.0', '']
    for sid, s in shots.items():
        e, t = s["eye"], s["look"]
        lines += [f'[sub_resource type="Resource" id="Shot{sid}"]', 'script = ExtResource("10_shot")', f'id = &"{sid}"',
                  f'position = Vector3({e[0]:g}, {e[1]:g}, {e[2]:g})', f'look_at = Vector3({t[0]:g}, {t[1]:g}, {t[2]:g})',
                  f'fov_deg = {s["fov"]:g}']
        if "dof" in s:
            fd, ft, fb = s["dof"]
            lines += ['dof_far_enabled = true', f'dof_far_distance = {fd:g}', f'dof_far_transition = {ft:g}',
                      f'dof_blur_amount = {fb:g}']
        lines.append('')
    lines += ['[node name="OruvelPreview" type="Node3D" node_paths=PackedStringArray("sun", "tide", "water", '
              '"world_environment", "dresser")]',
              'script = ExtResource("1_rig")', 'sun = NodePath("Sun")', 'tide = NodePath("Tide")', 'water = NodePath("Water")',
              'world_environment = NodePath("WorldEnvironment")', 'dresser = NodePath("Dresser")',
              'sun_elevation_deg = 58.0', 'sun_azimuth_deg = 120.0', 'time_of_day_h = 10.5', 'wind_azimuth_deg = 225.0',
              'wind_speed_m_s = 5.0', 'wind_gust = 0.3', 'water_height_m = 0.0', '',
              '[node name="WorldEnvironment" type="WorldEnvironment" parent="."]', 'environment = ExtResource("8_env")', '',
              '[node name="Sun" type="DirectionalLight3D" parent="."]', 'light_color = Color(1, 0.9373, 0.8824, 1)',
              'light_energy = 3.0', 'shadow_enabled = true', 'shadow_bias = 0.03', 'shadow_normal_bias = 1.0',
              'shadow_blur = 1.2', 'sky_mode = 1', 'directional_shadow_mode = 2', 'directional_shadow_split_1 = 0.04',
              'directional_shadow_split_2 = 0.12', 'directional_shadow_split_3 = 0.35',
              'directional_shadow_max_distance = 300.0', '',
              '[node name="Water" type="Node3D" parent="."]', 'script = ExtResource("4_water")',
              'publishes_water_level = true', 'wave_set = SubResource("CalmWaves")', 'material = ExtResource("7_water_mat")',
              '',
              '[node name="Tide" type="Node" parent="." node_paths=PackedStringArray("water")]',
              'script = ExtResource("2_tide")', 'water = NodePath("../Water")', '',
              '[node name="Dresser" type="Node3D" parent="." node_paths=PackedStringArray("tide")]',
              'script = ExtResource("3_dresser")', f'layout_path = "{RES_DIR}oruvel_layout.json"', 'tide = NodePath("../Tide")',
              '',
              '[node name="Drowned" type="Node3D" parent="." node_paths=PackedStringArray("tide")]',
              'script = ExtResource("3_dresser")', f'layout_path = "{RES_DIR}oruvel_drowned_layout.json"',
              'tide = NodePath("../Tide")', '',
              '[node name="Cameras" type="Node3D" parent="."]', '']
    for sid in shots:
        lines += [f'[node name="{sid}" type="Camera3D" parent="Cameras"]', 'near = 0.05', 'far = 6000.0',
                  'script = ExtResource("9_cam")', f'shot = SubResource("Shot{sid}")', '']
    steps = 1 + 10 + len(waves) + 1 + len(shots)
    return "\n".join(lines).rstrip("\n").replace("{steps}", str(steps)) + "\n"


def manifest() -> dict:
    """The capture manifest for every preview view (only the ones in tests/screenshots/shots.json are baselines)."""
    shots = []
    for sid, name in SHOT_NAMES.items():
        shots.append({"id": f"oruvel_{sid.lower()}_{name}", "scene": RES_DIR + "oruvel_preview.tscn",
                      "camera": f"Cameras/{sid}", "resolution": [960, 540], "settle_frames": 24,
                      "setup": {"globals": {"hymn_wind_time": 40.0},
                                "viewport": {"use_taa": False, "screen_space_aa": 1}}})
    return {"doc": "M3-ENV-07 Oruvel raft-town preview views (docs/kb/art/environments/oruvel.md section 4). Generated "
                   "by assets_src/environments/kits/oruvel/ov_preview_layout.py. Only the views named in "
                   "tests/screenshots/shots.json are registered baselines; capture the rest with --manifest.",
            "shots": shots}


def layout(pieces: list[dict], kit: str, zone: str, about: str, **extra) -> dict:
    d = {
        "schema": "hymn-zone-layout/1",
        "zone": zone,
        "_about": about,
        "seed": 1,
        "kit_dir": f"res://assets/environments/kits/{kit}/",
        "materials_dir": f"res://assets/environments/kits/{kit}/materials/",
        "lod1_from_m": 70.0,
        "lod_end_m": 3000.0,
        "lod_margin_m": 2.0,
        "pieces": pieces,
    }
    d.update(extra)
    return d


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pieces = town() + kit_row()
    shots = {k: {"eye": list(v["eye"]), "look": list(v["look"]), "fov": v["fov"]} for k, v in SHOTS.items()}
    main_layout = layout(
        pieces, "oruvel", "ch01/oruvel preview (M3-ENV-07): the raft-town kit composed for the design notes' key shots",
        "Generated by assets_src/environments/kits/oruvel/ov_preview_layout.py; do not edit by hand. Coordinates: the "
        "Oruvel Underway's frame (x east, z south, north = -Z, the sea surface at y 0); every piece carries its own y "
        "(no terrain). The dive raft's well is over the Underway's tether at (-9.9, 5.2); the neighbour raft at "
        "(-3, 11) is the Underway's hull_keels. The kit row (O20) is on the open water east of the town (x 70+).",
        shots=shots, anchors=anchors())
    (OUT_DIR / "oruvel_layout.json").write_text(json.dumps(main_layout, indent=1) + "\n", encoding="utf-8")
    crown = drowned()
    drowned_layout = layout(
        crown, "oruvel_underway", "ch01/oruvel preview (M3-ENV-07): the drowned tower's crown under the dive raft",
        "Generated by assets_src/environments/kits/oruvel/ov_preview_layout.py from the Oruvel Underway kit's preview "
        "layout (ou_preview_layout.tower(), the rows at and above F13), read-only; same frame as oruvel_layout.json.")
    (OUT_DIR / "oruvel_drowned_layout.json").write_text(json.dumps(drowned_layout, indent=1) + "\n", encoding="utf-8")
    (OUT_DIR / "oruvel_preview.tscn").write_text(tscn(SHOTS), encoding="utf-8")
    (OUT_DIR / "oruvel_preview_shots.json").write_text(json.dumps(manifest(), indent=1) + "\n", encoding="utf-8")
    print(f"LAYOUT {len(pieces)} pieces, {len(crown)} crown pieces, {len(SHOTS)} shots -> {OUT_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
