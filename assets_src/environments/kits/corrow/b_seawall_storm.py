"""Ch8's three wall-head arenas with the Undertow on the sea (env-art-b, M3-ENV-1314). env-art's tables
(`_wallhead_arena` in `assets_src/environments/kits/haluna/arena_scenes.py`, read-only) give each state a
`the_storm_wall` camera hint, but no arena placed the storm, so every wall-head fight (the Reach's included) had an
empty sky over the sea. This writes each table through the same `write_arena`, then adds Rendering's UndertowStorm
down that hint's bearing with a StormFarPlane under it (the battle camera's far plane reaches past it):

  seawall_stairhead_storm, seawall_stairhead_hoist   preset `ch08_seawall` (the daylight wall standing on the sea)
  seawall_stairhead_surge                            preset `ch08_landfall` (the Reach: the canopy's edge, nearer)

It also marks the Fisher Stair for the set piece (M3-CRB-009 ask 4; the Lead, 2026-10-28). The kit's real stair
(cw_stair.py) already stands in the table, its head landing at the party's side by `EntryMarker_ward`. Battle-
presentation's stair meter and the climbers' VFX get two anchors computed from the stair itself:
`StairHead_ward` (where the Climb steps off the head landing onto the walk) and `StairFlight_ward` (five steps down
the top flight, where the next group is seen coming up). A camera hint, `CameraHints/the_stair_head`, looks from
the walk past the party's right over the head landing and down the top flight.

In battle the arena's Sun and WorldEnvironment move to the battle scene (battle_arena_root.gd), so the storm takes no
zone shadow or exposure flash here (the arena's grade is already the storm's); its sea level is the arena's sea.
Re-run after the tables change, instead of `arena_scenes.py`'s own write of these arenas:

    python3 assets_src/environments/kits/corrow/b_seawall_storm.py
"""

from __future__ import annotations

import importlib.util
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STORM_SCRIPT = "res://game/vfx/undertow/undertow_storm.gd"
FAR_SCRIPT = "res://game/levels/act1/storm_far_plane.gd"
PRESETS = {"seawall_stairhead_storm": "ch08_seawall", "seawall_stairhead_hoist": "ch08_seawall",
           "seawall_stairhead_surge": "ch08_landfall"}
HINT = "the_storm_wall"
STAIR_GLB = "fisher_stair.glb"
STAIR_FLIGHT_STEPS_DOWN = 5
# The stair-head hint: eye on the walk past the party's right, looking over the head landing down the top flight
STAIR_HINT_EYE = (5.0, 2.4, -0.6)


def _arena_scenes():
    path = HERE.parent / "haluna" / "arena_scenes.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("arena_scenes_seawall", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def azimuth_deg(table: dict) -> float:
    """The hint's bearing, clockwise from north (-Z), as UndertowStorm.approach_azimuth_deg reads it."""
    (px, _py, pz), (lx, _ly, lz) = table["hints"][HINT]
    return round(math.degrees(math.atan2(lx - px, -(lz - pz))) % 360.0, 2)


def add_storm(text: str, table: dict, preset: str) -> str:
    head = re.match(r"\[gd_scene load_steps=(\d+) format=3\]", text)
    text = text.replace(head.group(0), f"[gd_scene load_steps={int(head.group(1)) + 2} format=3]", 1)
    last = list(re.finditer(r'^\[ext_resource [^\n]*\]$', text, flags=re.M))[-1]
    res = (f'\n[ext_resource type="Script" path="{STORM_SCRIPT}" id="storm_script"]'
           f'\n[ext_resource type="Script" path="{FAR_SCRIPT}" id="storm_far"]')
    text = text[:last.end()] + res + text[last.end():]
    return text.rstrip("\n") + (
        '\n\n[node name="Undertow" type="Node3D" parent="."]\n'
        'script = ExtResource("storm_script")\n'
        f"approach_azimuth_deg = {azimuth_deg(table)}\n"
        f'preset = "{preset}"\n'
        "zone_shadow = false\n"
        "exposure_flash = false\n"
        f"sea_level_y = {table['sea']['y']}\n"
        "sea_level_from_water = false\n"
        '\n[node name="FarPlane" type="Node" parent="Undertow"]\n'
        'script = ExtResource("storm_far")\n')


def stair_marks(table: dict) -> dict[str, tuple[float, float, float]]:
    """StairHead_ward and StairFlight_ward in the arena, from the kit stair's own frame (bent onto the wall's arc as the
    piece is) through the table's placement of it."""
    sys.path.insert(0, str(HERE))
    import cw_common as cw
    import cw_stair
    import numpy as np

    row = next(r for r in table["pieces"] if isinstance(r, dict) and str(r["glb"]).endswith(STAIR_GLB))
    steps, _land, head = cw_stair.layout_steps()
    kz1 = cw.KERB[1]
    hx = (head[0] + head[1]) * 0.5
    x0, x1, top, _r = steps[-STAIR_FLIGHT_STEPS_DOWN]
    local = np.array([[hx, cw.WALK_Y, kz1 + 0.72],
                      [(x0 + x1) * 0.5, top, float(cw_stair.z_face(top)) - cw_stair.WIDTH_M * 0.5]])
    bent, _th = cw.bend_points(local)
    a = math.radians(float(row["yaw"]))
    ox, oy, oz = row["at"]
    out = {}
    for name, (x, y, z) in zip(("StairHead_ward", "StairFlight_ward"), bent):
        out[name] = (round(math.cos(a) * x + math.sin(a) * z + ox, 3), round(y + oy, 3),
                     round(-math.sin(a) * x + math.cos(a) * z + oz, 3))
    return out


def _look_at(eye, target) -> str:
    """A Godot Transform3D (rows) at eye whose -Z looks at target."""
    import numpy as np

    e, t = np.array(eye, float), np.array(target, float)
    z = e - t
    z /= np.linalg.norm(z)
    x = np.cross([0.0, 1.0, 0.0], z)
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    rows = ", ".join(f"{v:.6g}" for v in (x[0], y[0], z[0], x[1], y[1], z[1], x[2], y[2], z[2]))
    return f"Transform3D({rows}, {', '.join(f'{v:g}' for v in e)})"


def add_stair_marks(text: str, table: dict) -> str:
    marks = stair_marks(table)
    out = text.rstrip("\n")
    for name, (x, y, z) in marks.items():
        out += (f'\n\n[node name="{name}" type="Marker3D" parent="."]\n'
                f"transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {x:g}, {y:g}, {z:g})")
    out += ('\n\n[node name="the_stair_head" type="Marker3D" parent="CameraHints"]\n'
            f"transform = {_look_at(STAIR_HINT_EYE, marks['StairFlight_ward'])}")
    return out + "\n"


def main(out_dir: Path | None = None) -> int:
    AS = _arena_scenes()
    if out_dir is not None:  # tools/tests/test_b_arenas.py writes to a scratch dir
        AS.OUT_DIR = out_dir
    for aid, preset in PRESETS.items():
        table = AS.ARENAS[aid]
        path = AS.write_arena(table)
        text = add_stair_marks(add_storm(path.read_text(encoding="utf-8"), table, preset), table)
        path.write_text(text, encoding="utf-8")
        print(f"ARENA {path.name} (+ Undertow {preset} at {azimuth_deg(table)} deg)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
