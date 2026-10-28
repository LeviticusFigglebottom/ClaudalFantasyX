"""Ch4's wake-night zone dressing (M3-ENV-743; ADR 0041, ADR 0200; act1_ch04.md C4-01 to C4-08): Haluna's kit laid
over act1-chapters' greybox `game/levels/ch04/haluna_wake/haluna_wake_layout.json`, in the greybox's own frame, as a
ZoneKitDressing layout. The wake set is M3-ENV-709's (haluna.md §5.1: the lamps lining the way to the Pilgrim's Wake
and ringing it, the feast on the sand, Asha's shell beside Imra's, Ysolde's ink kit, the dark dock), placed on the
greybox's blocks.

    python3 assets_src/environments/kits/haluna/wake_zone_dressing.py

Writes, under assets/environments/zones/ch04/: haluna_wake_dressing.json, the night Environment (a copy of Haluna's
ch02_night one) and the night sea's material (Haluna's water at the ch02_night settings HalunaMood applies); and the
preview game/levels/_tests/haluna_wake_dressing/haluna_wake_dressed.tscn. The zone mounts the JSON with a `Dressing`
child (game/levels/act1/zone_kit_dressing.gd), plus a `Water` WaterSurface at wake_ground.WATER_Y on that material.

The greybox keeps the gameplay: the ground (wake_ground) is level at y 0 inside the rails; each house, the inn, the
stalls and the dock stand on their blocks (the lane houses have no shade deck, so the block's walls are theirs). The
chapel runs 3 m past its block at the back, so it takes a box collider. The wake wall is the kit's 7 m arc with its
gap on the greybox's shell, flanked by coral tidewall runs to the block's ends; the arc bows towards the village, so
the wall pieces collide on their own LOD1 mesh. The story's blocks keep their pieces in step: the lamps and their
lights follow `WallLamps`, `WallLampsLow` and `GrassLamps`, the windows' lights `WindowLit1`..`4`, Asha's shell
`AshaShell`, the ink kit and its lamp `InkLamp`.
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import kit_common as kc  # noqa: E402
import shrine  # noqa: E402  (the chapel's depth; read-only)
import village  # noqa: E402  (LANE_HOUSES; read-only)
import wake_ground as wg  # noqa: E402
import walls  # noqa: E402  (the wake arc; read-only)
import waterfront  # noqa: E402  (DOCK_DECK_Y; read-only)

GREYBOX = ROOT / "game" / "levels" / "ch04" / "haluna_wake" / "haluna_wake_layout.json"
ZONE_DIR = ROOT / "assets" / "environments" / "zones" / "ch04"
OUT = ZONE_DIR / "haluna_wake_dressing.json"
ENV_SRC = ROOT / "game" / "levels" / "ch02" / "haluna" / "haluna_night_environment.tres"
ENV_OUT = ZONE_DIR / "haluna_wake_night_environment.tres"
WATER_SRC = ROOT / "game" / "levels" / "ch02" / "haluna" / "haluna_water_material.tres"
WATER_OUT = ZONE_DIR / "haluna_wake_water_material.tres"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "haluna_wake_dressing" / "haluna_wake_dressed.tscn"
PREVIEW_SHOTS = ("H02", "H04", "H07", "H09", "H12", "H13", "H08", "C01")
KIT = "res://assets/environments/kits/haluna/"
VEG = "res://assets/environments/vegetation/"
NIGHT_TIME_H = 21.5  # HalunaMood's ch02_night
# HalunaMood's ch02_night sea (haluna_mood.gd): the deep colour, the caustics, the absorption scale.
NIGHT_WATER = {"col_deep": "Color(0.0235, 0.102, 0.1686, 1)", "caustic_strength": "0.25", "absorption_scale": "1.0"}
NIGHT_SEA_GLOW = 0.12
NIGHT_GLIMMER = (0.2122, 0.5647, 0.6939, 0.6)
LAMP_COLOR = "#FFB16E"  # the ch04_wake set's warm lights
CLEAR_M = 1.2
SHELL_PROUD_M = 0.01  # a named shell's hinge stands this far out of the wall's face

NOISE = kc.Noise3(kc.rng_for("wake_ground", 231))
_HEIGHT = wg.height(NOISE)


def ground_y(x: float, z: float) -> float:
    return float(_HEIGHT(np.array(x), np.array(z)))


def put(piece: str, x: float, y: float, z: float, yaw: float = 0.0, **kw) -> dict:
    d = {"piece": piece, "at": [round(x, 3), round(z, 3)], "y": round(y, 3), "yaw_deg": round(yaw, 2)}
    d.update(kw)
    return d


def on_ground(piece: str, x: float, z: float, yaw: float = 0.0, dy: float = 0.0, **kw) -> dict:
    return put(piece, x, ground_y(x, z) + dy, z, yaw, **kw)


def palm(kind: str, x: float, z: float, yaw: float, scale: float) -> dict:
    return on_ground(f"palm_coconut_{kind}", x, z, yaw, -0.05, kit_dir=VEG, scale=scale)


def _blocks() -> dict[str, dict]:
    return {b["id"]: b for b in json.loads(GREYBOX.read_text(encoding="utf-8"))["blocks"]}


def lamp_row(a: tuple[float, float], b: tuple[float, float], step: float, block: str, y: float = 0.0) -> list[dict]:
    """Ground lamps from a to b about `step` apart, each turned a little, following `block`."""
    n = max(1, round(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
    return [put("ground_lamp", a[0] + (b[0] - a[0]) * k / n, y, a[1] + (b[1] - a[1]) * k / n, 37.0 * k, block=block)
            for k in range(n + 1)]


def wall_run(a: tuple[float, float], b: tuple[float, float]) -> list[dict]:
    """Tidewall segments (2 m) from a to b, overlapping to fill the run, colliding on their LOD1 (the wall's face)."""
    ln = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, math.ceil(ln / 2.0))
    yaw = math.degrees(math.atan2(-(b[1] - a[1]), b[0] - a[0]))
    out = []
    for k in range(n):
        t = (k + 0.5) / n
        out.append(put("tidewall_straight", a[0] + (b[0] - a[0]) * t, 0.0, a[1] + (b[1] - a[1]) * t, yaw,
                       collide="trimesh", block="WakeWall"))
    return out


def houses(b: dict) -> list[dict]:
    out = []
    # Neme's house (south), its door north onto the lane's foot.
    nh = b["NemeHouse"]
    out.append(put("house_lane_b", nh["pos"][0], 0.0, nh["pos"][2], 180.0))
    # The lane's four houses, doors onto the lane; two of them the deeper house, its back run on past the block.
    deep = village.LANE_HOUSES["house_lane_c"][1] - village.LANE_HOUSES["house_lane_a"][1]
    for bid, piece in (("HouseW1", "house_lane_a"), ("HouseE1", "house_lane_c"), ("HouseW2", "house_lane_c"),
                       ("HouseE2", "house_lane_a")):
        h = b[bid]
        side = -1.0 if h["pos"][0] < 0 else 1.0  # the house's side of the lane
        x = h["pos"][0] + (side * deep * 0.5 if piece == "house_lane_c" else 0.0)
        out.append(put(piece, x, 0.0, h["pos"][2], 90.0 if side < 0 else -90.0))
    # The inn (west), shut: the deep house a size up, its door on the lane's path, its yard behind.
    inn = b["Inn"]
    s = 1.15
    front = inn["pos"][0] + inn["size"][0] * 0.5
    out.append(put("house_lane_c", front - village.LANE_HOUSES["house_lane_c"][1] * 0.5 * s, 0.0, inn["pos"][2], 90.0,
                   scale=s))
    out.append(on_ground("woodpile", front - 9.6, inn["pos"][2] + 4.2, 180.0))
    out.append(on_ground("cargo_sacks", front - 1.0, inn["pos"][2] + 4.4, 20.0))
    out.append(on_ground("water_jar", front + 0.45, inn["pos"][2] + 2.5, 0.0))
    # The shut market: the two stall frames with their slatted tables, no cloths.
    for bid, yaw in (("MarketStallA", 180.0), ("MarketStallB", 0.0)):
        st = b[bid]
        out.append(put("market_stall", st["pos"][0], 0.0, st["pos"][2], yaw))
    out.append(on_ground("crate_stack", -21.2, -7.0, 90.0))
    out.append(on_ground("basket_set", -14.6, -2.6, 40.0))
    # The chapel (east): its door and steps on ChapelSteps, the nave run back east.
    ch = b["Chapel"]
    door_x = ch["pos"][0] - ch["size"][0] * 0.5
    out.append(put("order_chapel", door_x + shrine_depth() * 0.5, 0.0, ch["pos"][2], -90.0, collide=True))
    # Yards: pots by the doors, a jar, the laundry between the west houses' backs, a fish rack behind the east ones.
    out.append(on_ground("pot_plants", -3.7, 2.4, 90.0))
    out.append(on_ground("pot_plants", 3.7, -16.4, -90.0))
    out.append(on_ground("water_jar", 3.8, 2.3, 0.0))
    out.append(on_ground("laundry_line", -12.4, -7.0, 90.0))
    out.append(on_ground("fish_drying_rack", 12.6, 1.5, 90.0))
    out.append(on_ground("wayside_offering", -3.4, 6.0, 0.0))
    return out


def shrine_depth() -> float:
    """The chapel's nave depth (shrine.build_chapel's d)."""
    import inspect
    return float(inspect.signature(shrine.build_chapel).parameters["d"].default)


def dock(b: dict) -> list[dict]:
    d = b["Dock"]
    x0 = d["pos"][0] - d["size"][0] * 0.5
    out = [put("dock_haluna_short", x0, -waterfront.DOCK_DECK_Y, d["pos"][2], 0.0)]
    # The beach either side of it: the boats drawn up, the nets on their rack, the dock's landward clutter.
    out.append(on_ground("outrigger_7m", 34.5, -9.0, 80.0, 0.12))
    out.append(on_ground("outrigger_7m", 33.6, -30.5, 100.0, 0.12))
    out.append(on_ground("net_rack", 33.0, -14.5, 90.0))
    out.append(on_ground("crate_stack", 28.4, -23.4, 0.0))
    out.append(on_ground("rope_coil", 29.0, -16.9, 0.0))
    return out


def wake(b: dict) -> list[dict]:
    out = []
    ww = b["WakeWall"]
    face_z = ww["pos"][2] + ww["size"][2] * 0.5  # the wall's village face
    asha = b["AshaShell"]
    inset = 0.3  # the arc's village face at its centre is 0.3 m in front of its origin
    gx, gz = asha["pos"][0], face_z - inset
    out.append(put("wakeshell_wall", gx, 0.0, gz, 0.0, collide="trimesh", block="WakeWall"))
    a = walls.WAKE_ARC_M / walls.WAKE_RADIUS_M * 0.5
    ex = math.sin(a) * walls.WAKE_RADIUS_M
    ez = gz + walls.WAKE_RADIUS_M - math.cos(a) * walls.WAKE_RADIUS_M
    x0, x1 = ww["pos"][0] - ww["size"][0] * 0.5, ww["pos"][0] + ww["size"][0] * 0.5
    out += wall_run((x0, ww["pos"][2]), (gx - ex, ez - 0.25))
    out += wall_run((gx + ex, ez - 0.25), (x1, ww["pos"][2]))
    # The two named shells set in the wall at the gap's height: Asha's in the gap (freshly inked, with ch04_shell_set)
    # and Imra's beside it (faded), each on the arc's face and turned with it.
    for blk, mat in (("ImraShell", "kit_wake_shell_faded"), ("AshaShell", "kit_wake_shell_inked")):
        x = b[blk]["pos"][0]
        arc = (x - gx) / walls.WAKE_RADIUS_M
        face = gz + walls.WAKE_RADIUS_M - (walls.WAKE_RADIUS_M - inset) * math.cos(arc)
        d = put("wake_shell_set", x, walls.WAKE_GAP[1], face + SHELL_PROUD_M, -math.degrees(arc),
                materials={"kit_wake_shell": mat})
        if blk == "AshaShell":
            d["block"] = blk
        out.append(d)
    ink = b["InkLamp"]
    out.append(put("ink_kit", ink["pos"][0] - 0.4, 0.02, ink["pos"][2] + 0.35, 0.0, block="InkLamp"))
    out.append(put("ground_lamp", ink["pos"][0], 0.0, ink["pos"][2], 0.0, block="InkLamp"))
    # The lamps: along the wall's foot (the wake's), a few left guttering at dawn (WallLampsLow), the grass line and
    # the lane up to it, the four tables' ends (the village's, gone home with GrassLamps).
    out += lamp_row((x0 + 0.4, face_z + 0.35), (x1 - 0.4, face_z + 0.35), 0.8, "WallLamps")
    out += lamp_row((x0 + 1.5, face_z + 0.55), (x1 - 1.5, face_z + 0.55), 2.6, "WallLampsLow")
    gl = b["GrassLamps"]
    gz0 = gl["pos"][2]
    out += lamp_row((gl["pos"][0] - gl["size"][0] * 0.5, gz0), (gl["pos"][0] + gl["size"][0] * 0.5, gz0), 1.0,
                    "GrassLamps")
    for side in (-2.4, 2.4):
        out += lamp_row((side, -19.0), (side, -28.5), 1.5, "GrassLamps")
    for tid in ("TableVendor", "TableOsu", "TableFisher", "TableNeme"):
        t = b[tid]
        # The feast on the sand where the table is: a mat a size up to the table's length.
        s = round(t["size"][0] / 2.06, 3)
        out.append(put("feast_mat", t["pos"][0], 0.0, t["pos"][2], 0.0, scale=s))
        for dx in (-1.45, 1.45):
            out.append(put("ground_lamp", t["pos"][0] + dx, 0.0, t["pos"][2] - 0.2, 0.0, block="GrassLamps"))
    out.append(put("garland_string", 0.0, 3.0, -25.4, 0.0))
    return out


def causeway(b: dict) -> list[dict]:
    """The causeway head and its line north under the tide: slab pairs (one broken), marker posts every 20 m."""
    cw = b["Causeway"]
    top = cw["pos"][1] + cw["size"][1] * 0.5
    slab_top = 0.32  # causeway_slab_flat's top over its origin
    out = []
    z = -44.5
    k = 0
    while z > cw["pos"][2] - cw["size"][2] * 0.5:
        for x in (-0.66, 0.66):
            broken = (k * 7 + (x > 0)) % 11 == 3
            out.append(put("causeway_slab_broken" if broken else "causeway_slab_flat", x, top - slab_top, z,
                           (k * 13 % 5) - 2.0))
        z -= 2.5
        k += 1
    for z, piece in ((-50.0, "pilgrim_marker_post"), (-70.0, "pilgrim_marker_post_leaning"),
                     (-90.0, "pilgrim_marker_post")):
        out.append(put(piece, 2.3, top - slab_top, z, 90.0))
    for x, z, piece in ((-8.0, -47.0, "coral_boulder_b"), (7.0, -53.0, "coral_boulder_c"),
                        (-11.0, -61.0, "coral_boulder_b"), (12.0, -44.5, "coral_boulder_a")):
        out.append(on_ground(piece, x, z, 40.0 * x))
    return out


def surroundings() -> list[dict]:
    """The village going on past the rails (south and west) and the island's palms round it."""
    out = []
    for piece, x, z, yaw in (("house_tile_a", -9.0, 21.0, 180.0), ("house_tile_c", 3.0, 23.5, 170.0),
                             ("storehouse_stilt", 13.0, 20.0, 190.0), ("house_tile_b", -20.0, 19.5, 175.0),
                             ("house_tile_a", -38.0, -2.0, 95.0), ("house_tile_b", -37.5, -16.0, 85.0),
                             ("house_tile_c", -40.0, -30.0, 90.0), ("storehouse_stilt", -36.0, 8.0, 100.0)):
        out.append(on_ground(piece, x, z, yaw))
    for kind, x, z, yaw, s in (("a", -33.0, -38.0, 10.0, 1.2), ("b", -34.5, -24.0, 120.0, 1.1),
                               ("c", -33.5, -9.0, 250.0, 0.9), ("a", -34.0, 3.0, 40.0, 1.25),
                               ("b", -27.0, 17.5, 300.0, 1.15), ("c", -14.0, 17.0, 80.0, 1.0),
                               ("a", 8.5, 17.5, 200.0, 1.3), ("b", 21.0, 18.0, 150.0, 1.05),
                               ("c", 33.0, 9.0, 20.0, 1.2), ("a", 32.5, -38.0, 280.0, 1.3),
                               ("b", -22.0, -44.5, 60.0, 1.1), ("c", 20.5, -45.0, 330.0, 1.2),
                               ("a", -12.0, 6.5, 100.0, 1.1), ("b", 12.5, -21.0, 210.0, 1.0)):
        out.append(palm(kind, x, z, yaw, s))
    return out


def pieces() -> list[dict]:
    b = _blocks()
    return [put("wake_ground", 0.0, 0.0, 0.0, 0.0, lod1_from_m=140.0)] + houses(b) + dock(b) + wake(b) + causeway(b) \
        + surroundings()


def fire_lights(b: dict) -> list[dict]:
    out = []
    for k in range(1, 5):
        w = b[f"WindowLit{k}"]
        inward = 0.4 if w["pos"][0] < 0 else -0.4  # just inside the façade: the door and shutters let it out
        out.append({"at": [w["pos"][0] - inward, 1.5, w["pos"][2]], "energy": 0.9, "range": 4.5,
                    "block": f"WindowLit{k}"})
    face = b["WakeWall"]["pos"][2] + 0.5
    for x in (-6.0, -2.0, 2.0, 6.0):
        out.append({"at": [x, 0.6, face + 0.8], "energy": 1.1, "range": 6.5, "attenuation": 1.3, "block": "WallLamps"})
    for x in (-4.0, 4.0):
        out.append({"at": [x, 0.5, face + 0.8], "energy": 0.45, "range": 4.0, "block": "WallLampsLow"})
    for x, z in ((-6.0, -35.5), (0.0, -35.5), (6.0, -35.5), (-4.0, -31.4), (4.0, -31.4), (0.0, -24.0)):
        out.append({"at": [x, 0.6, z], "energy": 1.0, "range": 6.0, "attenuation": 1.3, "block": "GrassLamps"})
    ink = b["InkLamp"]["pos"]
    out.append({"at": [ink[0], 0.5, ink[2] + 0.3], "energy": 0.6, "range": 3.0, "block": "InkLamp"})
    return out


def layout() -> dict:
    b = _blocks()
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by assets_src/environments/kits/haluna/wake_zone_dressing.py from env-art's Haluna kit "
                  "and M3-ENV-709's wake set, in ch04/haluna_wake's greybox frame (M3-ENV-743); do not edit by hand. "
                  f"The zone's Water goes at y {wg.WATER_Y} on {res(WATER_OUT)}.",
        "seed": 1,
        "kit_dir": KIT,
        "materials_dir": KIT + "materials/",
        "lod1_from_m": 45.0,
        "lod_end_m": 2000.0,
        "lod_margin_m": 2.0,
        "water_y": wg.WATER_Y,
        "time_of_day_h": NIGHT_TIME_H,
        "environment": res(ENV_OUT),
        "fire_light_color": LAMP_COLOR,
        "fire_lights": fire_lights(b),
        "greybox": {"hide_all": True, "keep": []},
        "pieces": pieces(),
    }


def res(p: Path) -> str:
    return "res://" + p.relative_to(ROOT).as_posix()


def clearance_points() -> list[tuple[str, float, float, float]]:
    """(what, x, z, radius) every decor piece must keep clear of: the actors, marks and spawns, and the triggers."""
    d = json.loads(GREYBOX.read_text(encoding="utf-8"))
    pts = []
    for k in ("actors", "marks", "spawns"):
        for name, r in d[k].items():
            p = r.get("at") if isinstance(r, dict) else r
            pts.append((f"{k}:{name}", float(p[0]), float(p[2]), CLEAR_M))
    for t in d["triggers"]:
        pts.append((f"trigger:{t['id']}", float(t["at"][0]), float(t["at"][2]), max(t["size"][0], t["size"][2]) * 0.5))
    return pts


def night_water() -> str:
    text = WATER_SRC.read_text(encoding="utf-8")
    for k, v in NIGHT_WATER.items():
        text, n = re.subn(rf"^shader_parameter/{k} = .*$", f"shader_parameter/{k} = {v}", text, flags=re.M)
        if n != 1:
            raise SystemExit(f"{WATER_SRC.name}: no single {k} row")
    return text.replace('resource_name = "haluna_water"', 'resource_name = "haluna_wake_night_water"')


def write_preview() -> None:
    """The zone as act1-chapters' .tscn has it (its script and greybox layout), with the Water and this Dressing
    mounted and the zone's own shot cameras: env-art's render rig for the swap, until the zone mounts it."""
    shots = json.loads(GREYBOX.read_text(encoding="utf-8"))["shots"]
    lines = ["[gd_scene format=3]", "",
             '[ext_resource type="Script" path="res://game/levels/ch04/ch04_zone.gd" id="1_zone"]',
             '[ext_resource type="Script" path="res://game/levels/act1/zone_kit_dressing.gd" id="2_dressing"]',
             '[ext_resource type="Script" path="res://game/world/water/water_surface.gd" id="3_water"]',
             '[ext_resource type="Resource" path="res://game/world/water/lagoon_waves.tres" id="4_waves"]',
             f'[ext_resource type="Material" path="{res(WATER_OUT)}" id="5_water_mat"]',
             '[ext_resource type="Script" path="res://game/world/camera_shot.gd" id="6_shot"]',
             '[ext_resource type="Script" path="res://game/levels/ch02/haluna/haluna_shot_camera.gd" id="7_cam"]', ""]
    for sid in PREVIEW_SHOTS:
        sh = shots[sid]
        e, la = sh["pos"], sh["look_at"]
        lines += [f'[sub_resource type="Resource" id="Shot{sid}"]', 'script = ExtResource("6_shot")', f'id = &"{sid}"',
                  f"position = Vector3({e[0]:g}, {e[1]:g}, {e[2]:g})", f"look_at = Vector3({la[0]:g}, {la[1]:g}, {la[2]:g})",
                  f"fov_deg = {sh['fov']:g}", ""]
    lines += ['[node name="HalunaWake" type="Node3D"]', 'script = ExtResource("1_zone")',
              'location_id = &"ch04/haluna_wake"',
              'layout_path = "res://game/levels/ch04/haluna_wake/haluna_wake_layout.json"', "",
              '[node name="Water" type="Node3D" parent="."]',
              f"transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, {wg.WATER_Y}, 0)", 'script = ExtResource("3_water")',
              "publishes_water_level = true", 'wave_set = ExtResource("4_waves")', 'material = ExtResource("5_water_mat")',
              f"sea_glow_energy = {NIGHT_SEA_GLOW}", "",
              '[node name="Dressing" type="Node3D" parent="."]', 'script = ExtResource("2_dressing")',
              f'layout_path = "{res(OUT)}"', "", '[node name="Cameras" type="Node3D" parent="."]', ""]
    for sid in PREVIEW_SHOTS:
        lines += [f'[node name="{sid}" type="Camera3D" parent="Cameras"]', "near = 0.05", "far = 2000.0",
                  'script = ExtResource("7_cam")', f'shot = SubResource("Shot{sid}")', ""]
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")


def main() -> int:
    ZONE_DIR.mkdir(parents=True, exist_ok=True)
    ENV_OUT.write_bytes(ENV_SRC.read_bytes())
    WATER_OUT.write_text(night_water(), encoding="utf-8")
    OUT.write_text(json.dumps(layout(), indent=1) + "\n", encoding="utf-8")
    write_preview()
    print(f"DRESSING {OUT.relative_to(ROOT)} ({len(layout()['pieces'])} pieces, {len(layout()['fire_lights'])} lights)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
