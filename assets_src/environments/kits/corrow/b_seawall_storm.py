"""Ch8's three wall-head arenas with the Undertow on the sea (env-art-b, M3-ENV-1314). env-art's tables
(`_wallhead_arena` in `assets_src/environments/kits/haluna/arena_scenes.py`, read-only) give each state a
`the_storm_wall` camera hint, but no arena placed the storm, so every wall-head fight (the Reach's included) had an
empty sky over the sea. This writes each table through the same `write_arena`, then adds Rendering's UndertowStorm
down that hint's bearing with a StormFarPlane under it (the battle camera's far plane reaches past it):

  seawall_stairhead_storm, seawall_stairhead_hoist   preset `ch08_seawall` (the daylight wall standing on the sea)
  seawall_stairhead_surge                            preset `ch08_landfall` (the Reach: the canopy's edge, nearer)

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


def main(out_dir: Path | None = None) -> int:
    AS = _arena_scenes()
    if out_dir is not None:  # tools/tests/test_b_arenas.py writes to a scratch dir
        AS.OUT_DIR = out_dir
    for aid, preset in PRESETS.items():
        table = AS.ARENAS[aid]
        path = AS.write_arena(table)
        path.write_text(add_storm(path.read_text(encoding="utf-8"), table, preset), encoding="utf-8")
        print(f"ARENA {path.name} (+ Undertow {preset} at {azimuth_deg(table)} deg)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
