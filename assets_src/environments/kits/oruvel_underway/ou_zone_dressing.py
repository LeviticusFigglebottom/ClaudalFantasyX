"""The Oruvel Underway's zone dressing (M3-ENV-741; ADR 0041, ADR 0200): the drowned-tower kit (M3-ENV-05) laid over
slice-polish's Ch1 greybox (`game/levels/ch01/oruvel_underway/oruvel_underway_layout.json`, M3-C01-02), in the
greybox's own frame, as a ZoneKitDressing layout.

    python3 assets_src/environments/kits/oruvel_underway/ou_zone_dressing.py

Writes assets/environments/zones/ch01/oruvel_underway_dressing.json and the preview
game/levels/_tests/oruvel_underway_zone_dressing/oruvel_underway_dressed.tscn. The zone mounts the JSON with a
`Dressing` child (game/levels/act1/zone_kit_dressing.gd, layout_path = that file).

The greybox lays the tower's three floors side by side at y 0 (the crown, the first bell-room, the galleries with the
gauge room), so each room is dressed as one storey of the tower: its walls in 6 m bays whose inner (gallery) face is
on the greybox wall's inner face, its floor in floor slabs (origin at the top, so a smaller slab is the same slab
scaled) with their tops at y 0. A run of bays is flush at an opening and runs on past a corner, where the crossing
wall hides it. The crown's walls are the broken ones (the top of the tower), Oruvel's hulls hang over it on the
`SurfaceLattice`; the bell-room is sealed (blind bays) with the hinge door on `BellDoor`; the gallery alternates
window and blind bays with its four lamp-columns on their blocks, the coral curtain on `CoralCurtain` (the open
lantern takes both away), the stairwell behind the divers' cord and the current shaft in the gauge room on
`ShaftLight`. Nothing here takes a collider: the greybox's blocks are the collision.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import ou_tower as ot  # noqa: E402  (BAY_W, WALL_T, STOREY, STAIR_W; read-only)

GREYBOX = ROOT / "game" / "levels" / "ch01" / "oruvel_underway" / "oruvel_underway_layout.json"
OUT = ROOT / "assets" / "environments" / "zones" / "ch01" / "oruvel_underway_dressing.json"
PREVIEW = ROOT / "game" / "levels" / "_tests" / "oruvel_underway_zone_dressing" / "oruvel_underway_dressed.tscn"
PREVIEW_SHOTS = ("U01", "U03", "U06", "U07", "U08")
KIT = "res://assets/environments/kits/oruvel_underway/"
SLAB = 6.0  # floor_slab's side at scale 1
HALF_T = ot.WALL_T * 0.5
SURFACE_Y = ot.STOREY * 2.0  # Oruvel's hulls over the crown: the crown is the tower's top storey, 6.4 m under them
TETHER_Y = 0.55  # the tether's clip over the floor (the kit preview's)
CORD_BACK = 0.15  # the divers' cord this far back from the stair's lip, on the floor's side (the kit preview's)

GALLERY_BAYS = ("tower_bay", "tower_bay_solid")
CROWN_BAYS = ("tower_bay_broken", "tower_bay_broken", "tower_bay")


def put(piece: str, x: float, y: float, z: float, yaw: float = 0.0, **kw) -> dict:
    d = {"piece": piece, "at": [round(x, 3), round(z, 3)], "y": round(y, 3), "yaw_deg": round(yaw, 2)}
    d.update(kw)
    return d


def _blocks() -> dict[str, dict]:
    return {b["id"]: b for b in json.loads(GREYBOX.read_text(encoding="utf-8"))["blocks"]}


def wall(face: float, a0: float, a1: float, *, along: str, inside: int, kinds: tuple[str, ...],
         anchor: str = "centre", centres: list[float] | None = None, overrides: dict[int, str] | None = None
         ) -> list[dict]:
    """Bays along a wall whose inner face is the line `face` (z = face for a wall along x, x = face along z), the
    room on the `inside` (+1 or -1) side of it, covering a0..a1: centred (running past both corners), or flush at
    a0 or a1 (an opening) and running past the other end; `centres` places them by hand. The bay's inner face looks
    into the room; `kinds` cycles along the run, `overrides` swaps a bay by its index."""
    length = a1 - a0
    n = max(1, math.ceil(length / ot.BAY_W - 1e-6))
    if centres is None:
        if anchor == "a0":
            centres = [a0 + ot.BAY_W * (k + 0.5) for k in range(n)]
        elif anchor == "a1":
            centres = [a1 - ot.BAY_W * (k + 0.5) for k in range(n)][::-1]
        else:
            mid = (a0 + a1) * 0.5
            centres = [mid + ot.BAY_W * (k - (n - 1) * 0.5) for k in range(n)]
    line = face - inside * HALF_T
    if along == "x":
        yaw = 180.0 if inside > 0 else 0.0
    else:
        yaw = -90.0 if inside > 0 else 90.0
    out = []
    for k, c in enumerate(centres):
        kind = (overrides or {}).get(k, kinds[k % len(kinds)])
        x, z = (c, line) if along == "x" else (line, c)
        out.append(put(kind, x, 0.0, z, yaw))
    return out


def floor(x0: float, x1: float, z0: float, z1: float, side: float = SLAB) -> list[dict]:
    """Floor slabs of `side` metres (floor_slab scaled) from the (x0, z0) corner, the last row and column running on
    under the far walls; tops at y 0."""
    out = []
    nx = max(1, math.ceil((x1 - x0) / side - 1e-6))
    nz = max(1, math.ceil((z1 - z0) / side - 1e-6))
    for i in range(nx):
        for j in range(nz):
            d = put("floor_slab", x0 + side * (i + 0.5), 0.0, z0 + side * (j + 0.5), 90.0 * ((i + j) % 2))
            if abs(side - SLAB) > 1e-6:
                d["scale"] = round(side / SLAB, 4)
            out.append(d)
    return out


def piers(corners: list[tuple[float, float]], centre: tuple[float, float]) -> list[dict]:
    """A corner column at each corner, set out of the room by half a wall, so it stands on the walls' line."""
    return [put("tower_pier", x + math.copysign(HALF_T, x - centre[0]), 0.0, z + math.copysign(HALF_T, z - centre[1]))
            for x, z in corners]


def pieces() -> list[dict]:
    b = _blocks()
    out: list[dict] = []
    # The crown (x -8..8, z -2..18): the tower's broken top, open to Oruvel's hulls; the tether down from them.
    out += floor(-8.0, 8.0, -2.0, 18.0, 4.0)
    out += wall(-2.0, -8.0, 8.0, along="x", inside=1, kinds=CROWN_BAYS)
    out += wall(18.0, -8.0, 8.0, along="x", inside=-1, kinds=CROWN_BAYS[1:] + CROWN_BAYS[:1])
    out += wall(-8.0, -2.0, 18.0, along="z", inside=1, kinds=CROWN_BAYS)
    out += wall(8.0, -2.0, 18.0, along="z", inside=-1, kinds=CROWN_BAYS[2:] + CROWN_BAYS[:2])
    out += piers([(-8.0, -2.0), (8.0, -2.0), (-8.0, 18.0), (8.0, 18.0)], (0.0, 8.0))
    lat = b["SurfaceLattice"]
    out.append(put("hull_keels", lat["pos"][0] - 3.0, SURFACE_Y, lat["pos"][2] + 3.0, 70.0, block="SurfaceLattice"))
    ct = b["CrownTether"]
    out.append(put("tether_line", ct["pos"][0], TETHER_Y, ct["pos"][2], 0.0, block="CrownTether"))
    out.append(put("coral_head_a", -6.4, 0.0, 16.2, 40.0))
    out.append(put("coral_head_b", 6.3, 0.0, 9.0, 160.0))
    out.append(put("seagrass_patch", -5.5, 0.0, 9.5, 20.0))
    out.append(put("lit_fragments", 5.6, 0.0, 15.8, 210.0))
    # The first bell-room (x 34..46, z 2..14): sealed, blind bays; the hinge door in the north wall on BellDoor.
    door = b["BellDoor"]
    out += floor(34.0, 46.0, 2.0, 14.0)
    out += wall(2.0, 34.0, 46.0, along="x", inside=1, kinds=("tower_bay_solid",),
                centres=[door["pos"][0] - 2 * ot.BAY_W, door["pos"][0] - ot.BAY_W, door["pos"][0]],
                overrides={2: "hinge_door"})
    out += wall(14.0, 34.0, 46.0, along="x", inside=-1, kinds=("tower_bay_solid",))
    out += wall(34.0, 2.0, 14.0, along="z", inside=1, kinds=("tower_bay_solid",))
    out += wall(46.0, 2.0, 14.0, along="z", inside=-1, kinds=("tower_bay_solid",))
    out += piers([(34.0, 2.0), (46.0, 2.0), (34.0, 14.0), (46.0, 14.0)], (40.0, 8.0))
    bt = b["BellTether"]
    out.append(put("tether_line", bt["pos"][0], TETHER_Y, bt["pos"][2], 0.0, block="BellTether"))
    out.append(put("diver_lantern", 45.0, 0.25, 13.2, 30.0))
    out.append(put("lit_fragments", 35.2, 0.0, 12.6, 100.0))
    # The galleries (x 74..86, z -40..20): window and blind bays, the tin's alcove off the west wall (z -6..-2) behind
    # the coral curtain, open to the gauge room on the east (z -40..-20); the four lamp-columns on their blocks.
    out += floor(74.0, 86.0, -34.0, 20.0)
    out += stairwell(b)
    out += wall(74.0, -2.0, 20.0, along="z", inside=1, kinds=GALLERY_BAYS, anchor="a0")
    out += wall(74.0, -40.0, -6.0, along="z", inside=1, kinds=GALLERY_BAYS, anchor="a1")
    out += wall(86.0, -20.0, 20.0, along="z", inside=-1, kinds=GALLERY_BAYS[::-1], anchor="a0")
    out += wall(20.0, 74.0, 86.0, along="x", inside=-1, kinds=GALLERY_BAYS)
    out += wall(-40.0, 74.0, 100.0, along="x", inside=1, kinds=("tower_bay_solid",))
    out += piers([(74.0, 20.0), (86.0, 20.0), (74.0, -2.0), (74.0, -6.0), (86.0, -20.0), (74.0, -40.0)], (80.0, -10.0))
    for k in range(1, 5):
        lc = b[f"LampColumn{k}"]
        out.append(put("lamp_column", lc["pos"][0], 0.0, lc["pos"][2], 47.0 * k))
    out.append(put("lit_fragments", 74.9, 0.0, -14.0, 300.0))
    out.append(put("lit_fragments", 85.2, 0.0, 9.0, 120.0))
    # The tin's alcove (x 68.5..74, z -6..-2).
    out += floor(68.5, 74.0, -6.75, -1.25, 5.5)
    out += wall(68.5, -6.0, -2.0, along="z", inside=1, kinds=("tower_bay_solid",))
    out += wall(-6.0, 68.5, 74.0, along="x", inside=1, kinds=("tower_bay_solid",), centres=[74.0 - ot.BAY_W * 0.5])
    out += wall(-2.0, 68.5, 74.0, along="x", inside=-1, kinds=("tower_bay_solid",), centres=[74.0 - ot.BAY_W * 0.5])
    cc = b["CoralCurtain"]
    out.append(put("coral_curtain", cc["pos"][0], 0.0, cc["pos"][2], 90.0, scale=round(cc["size"][2] / 3.0, 3),
                   block="CoralCurtain"))
    # The gauge room (x 86..100, z -40..-20): the wheel on GaugeWheel, the pipe run on the east wall, the current
    # shaft in its north-east corner, two storeys of it up into the dark (ShaftLight).
    out += floor(86.0, 100.0, -40.0, -20.0, 5.0)
    out += wall(100.0, -40.0, -20.0, along="z", inside=-1, kinds=("tower_bay_solid",))
    out += wall(-20.0, 86.0, 100.0, along="x", inside=-1, kinds=("tower_bay_solid",), anchor="a0")
    out += piers([(100.0, -20.0), (100.0, -40.0)], (93.0, -30.0))
    gw = b["GaugeWheel"]
    out.append(put("gauge_wheel", gw["pos"][0], 0.0, gw["pos"][2], 90.0, block="GaugeWheel"))
    out.append(put("pipe_run", 99.6, 0.0, -26.0, 90.0))
    sh = b["ShaftLight"]
    for n in range(2):
        out.append(put("current_shaft", sh["pos"][0], ot.STOREY * n, sh["pos"][2], 11.0, block="ShaftLight"))
    out.append(put("lit_fragments", 88.2, 0.0, -38.6, 20.0))
    return out


def stairwell(b: dict) -> list[dict]:
    """The stairwell at the gallery's north end: the flight going down north from behind the divers' cord, the
    floor round it in smaller slabs (the strip to the cord, then each side of the flight to the north wall)."""
    cord = b["KnottedCord"]
    lip = cord["pos"][2]
    x = cord["pos"][0]
    strip = -34.0 - lip  # the floor's last full row ends at z -34; the strip from there to the cord
    out = [put("floor_slab", 74.0 + strip * (k + 0.5), 0.0, -34.0 - strip * 0.5, 0.0, scale=round(strip / SLAB, 4))
           for k in range(round(12.0 / strip))] if strip > 0.01 else []  # none once the cord is on z -34
    side = (cord["size"][0] - ot.STAIR_W) * 0.5 + (cord["pos"][0] - cord["size"][0] * 0.5 - 74.0)  # 74 .. the flight
    s = side / 2.0
    for k in range(2):
        for j in range(2):
            z = lip - s * (j + 0.5)
            out.append(put("floor_slab", 74.0 + s * (k + 0.5), 0.0, z, 0.0, scale=round(s / SLAB, 4)))
            out.append(put("floor_slab", 86.0 - s * (k + 0.5), 0.0, z, 0.0, scale=round(s / SLAB, 4)))
    out.append(put("stair_flight", x, 0.0, lip, 90.0))
    out.append(put("divers_cord", x, 0.0, lip + CORD_BACK, 90.0, block="KnottedCord"))
    # The well a storey down (the kit preview's F8): blind bays each side of the flight and across its foot, the
    # landing's slab, so the opening reads as a stairwell into the dark and not as a hole into the murk.
    hw = ot.STAIR_W * 0.5
    run = 2 * ot.BAY_W
    down = wall(x - hw, lip - run, lip, along="z", inside=1, kinds=("tower_bay_solid",))
    down += wall(x + hw, lip - run, lip, along="z", inside=-1, kinds=("tower_bay_solid",))
    down += wall(lip - run, x - hw, x + hw, along="x", inside=1, kinds=("tower_bay_solid",))
    for d in down:
        d["y"] = -ot.STOREY
    out += down
    land = ot.STAIR_W / SLAB
    out.append(put("floor_slab", x, -ot.STOREY, lip - run + ot.STAIR_W * 0.5, 0.0, scale=round(land, 4)))
    return out


def layout() -> dict:
    return {
        "schema": "ZoneKitDressing (game/levels/act1/zone_kit_dressing.gd; ADR 0200)",
        "_about": "Generated by assets_src/environments/kits/oruvel_underway/ou_zone_dressing.py from env-art's "
                  "drowned-tower kit (M3-ENV-05), in ch01/oruvel_underway's greybox frame (M3-ENV-741); do not edit by "
                  "hand. The zone keeps its own murk (the layout's sun, environment and fog).",
        "seed": 1,
        "kit_dir": KIT,
        "materials_dir": KIT + "materials/",
        "lod1_from_m": 40.0,
        "lod_end_m": 400.0,
        "lod_margin_m": 2.0,
        "greybox": {"hide_all": True, "keep": []},
        "pieces": pieces(),
    }


def clearance_points() -> list[tuple[str, float, float, float]]:
    """(what, x, z, radius) every decor piece must keep clear of (nothing here takes a collider; kept for the test)."""
    d = json.loads(GREYBOX.read_text(encoding="utf-8"))
    pts = [(f"spawns:{k}", float(v[0]), float(v[2]), 1.2) for k, v in d["spawns"].items()]
    pts += [(f"marks:{k}", float(v[0]), float(v[2]), 1.2) for k, v in d["marks"].items()]
    for t in d["triggers"]:
        pts.append((f"trigger:{t['id']}", float(t["at"][0]), float(t["at"][2]), max(t["size"][0], t["size"][2]) * 0.5))
    return pts


def write_preview() -> None:
    """The zone as slice-polish's .tscn has it (its script and greybox layout), with this Dressing mounted and the
    zone's own shot cameras: env-art's render rig for the swap, until the zone mounts it."""
    shots = json.loads(GREYBOX.read_text(encoding="utf-8"))["shots"]
    lines = ["[gd_scene format=3]", "",
             '[ext_resource type="Script" path="res://game/levels/ch01/oruvel_underway/underway_zone.gd" id="1_zone"]',
             '[ext_resource type="Script" path="res://game/levels/act1/zone_kit_dressing.gd" id="2_dressing"]',
             '[ext_resource type="Script" path="res://game/world/camera_shot.gd" id="3_shot"]',
             '[ext_resource type="Script" path="res://game/levels/ch02/haluna/haluna_shot_camera.gd" id="4_cam"]', ""]
    for sid in PREVIEW_SHOTS:
        sh = shots[sid]
        e, la = sh["pos"], sh["look_at"]
        lines += [f'[sub_resource type="Resource" id="Shot{sid}"]', 'script = ExtResource("3_shot")', f'id = &"{sid}"',
                  f"position = Vector3({e[0]:g}, {e[1]:g}, {e[2]:g})", f"look_at = Vector3({la[0]:g}, {la[1]:g}, {la[2]:g})",
                  f"fov_deg = {sh['fov']:g}", ""]
    lines += ['[node name="OruvelUnderway" type="Node3D"]', 'script = ExtResource("1_zone")',
              'location_id = &"ch01/oruvel_underway"',
              'layout_path = "res://game/levels/ch01/oruvel_underway/oruvel_underway_layout.json"', "",
              '[node name="Dressing" type="Node3D" parent="."]', 'script = ExtResource("2_dressing")',
              f'layout_path = "res://{OUT.relative_to(ROOT).as_posix()}"', "",
              '[node name="Cameras" type="Node3D" parent="."]', ""]
    for sid in PREVIEW_SHOTS:
        lines += [f'[node name="{sid}" type="Camera3D" parent="Cameras"]', "near = 0.05", "far = 400.0",
                  'script = ExtResource("4_cam")', f'shot = SubResource("Shot{sid}")', ""]
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(layout(), indent=1) + "\n", encoding="utf-8")
    write_preview()
    print(f"DRESSING {OUT.relative_to(ROOT)} ({len(layout()['pieces'])} pieces)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
