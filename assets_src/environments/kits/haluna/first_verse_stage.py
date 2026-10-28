"""The First Verse's stage (M3-ENV-746; Ch3 `ch03_the_first_verse`, act1_ch03): the final Shell Shrine as a set for
the cutscene, so `game/levels/ch03/first_verse/first_verse.tscn` swaps its CSG shrine, island and flat sea for one
instance of this scene (M3-ENV-745). The cutscene keeps its own sky, sun, cameras and actors.

    python3 assets_src/environments/kits/haluna/first_verse_stage.py

Writes assets/environments/zones/shell_shrine/first_verse_stage.tscn, in the shrine's frame (the hall's centre on
the floor at the origin, the entrance west), which is the stand-in's: its CSG door is west of the origin too. It holds
- `Shrine`: the shrine's dressing (`game/levels/ch03/shell_shrine/shell_shrine_dressing.tscn`: hall, vault, roof,
  islet, steps, walls, portals, columns, the chamber passage);
- `Sea`: the lagoon at the shrine zone's level, with its tide line;
- `Shore`: the islet's set dressing, as the shrine zone has it;
- `Marks`: where the stand-in's marks fall on the real shrine (the steps' treads, the doorway, the pool), named as
  first_verse.tscn names them, for the cutscene's marks to take their positions from.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))

import shrine_interior as si  # noqa: E402  (SHRINE_LAYOUT; read-only)

OUT = ROOT / "assets" / "environments" / "zones" / "shell_shrine" / "first_verse_stage.tscn"
DRESSING = "res://game/levels/ch03/shell_shrine/shell_shrine_dressing.tscn"
KIT = "res://assets/environments/kits/haluna/"
SEA_Y = -2.0  # the shrine zone's sea (shell_shrine.tscn `Sea`)
# The islet's set dressing, as the shrine zone places it: (name, piece, x, y, z, yaw).
SHORE = [
    ("RopeCoil", "rope_coil", -21.6, -1.75, 3.4, 20.0),
    ("TideDebrisN", "tide_debris", -23.6, -1.8, 6.6, 65.0),
    ("TideDebrisS", "tide_debris", -24.0, -1.8, -7.0, 220.0),
    ("NetHeap", "net_heap", -22.8, -1.78, -5.4, -75.0),
    ("OfferingN", "wayside_offering", -13.15, 0.0, 2.7, 90.0),
    ("OfferingS", "wayside_offering", -13.15, 0.0, -2.7, 90.0),
]
POOL_X, POOL_Z = si.SHRINE_LAYOUT["inner_pool"]
POOL_KERB_M = 3.7  # the inner pool's west kerb from its centre
# The real shrine's places for the stand-in's marks (the steps' treads read off shrine_steps: the landing at y 0.06
# to x -15.5, the treads down to -1.1 at x -17).
MARKS = [
    ("asha_start", (-13.6, 0.0, 0.0)),
    ("doorway", (-14.2, 0.0, 0.0)),
    ("threshold_west", (-15.2, 0.06, 0.0)),
    ("steps_rhen", (-16.5, -0.81, -1.1)),
    ("steps_toma", (-16.5, -0.81, 1.2)),
    ("toma_seaward", (-16.5, -0.81, 1.2)),
    ("chamber_pool", (POOL_X - POOL_KERB_M, 0.0, POOL_Z + 0.4)),
    ("ilun_chamber", (POOL_X, 2.0, POOL_Z)),
]


def yaw_xform(yaw: float, at: tuple[float, float, float]) -> str:
    a = math.radians(yaw)
    c, s = round(math.cos(a), 6), round(math.sin(a), 6)
    return f"Transform3D({c:g}, 0, {s:g}, 0, 1, 0, {-s:g}, 0, {c:g}, {at[0]:g}, {at[1]:g}, {at[2]:g})"


def main() -> int:
    pieces = sorted({p[1] for p in SHORE})
    ext = [("PackedScene", DRESSING, "1_shrine"), ("Script", "res://game/world/water/water_surface.gd", "2_water"),
           ("Resource", "res://game/world/water/lagoon_waves.tres", "3_waves"),
           ("Material", "res://game/levels/ch02/haluna/haluna_water_material.tres", "4_water_mat")]
    ext += [("PackedScene", KIT + p + ".glb", f"{5 + k}_{p}") for k, p in enumerate(pieces)]
    lines = [f"[gd_scene load_steps={len(ext) + 1} format=3]", ""]
    lines += [f'[ext_resource type="{t}" path="{p}" id="{i}"]' for t, p, i in ext]
    lines += ["", '[node name="FirstVerseStage" type="Node3D"]', "",
              '[node name="Shrine" parent="." instance=ExtResource("1_shrine")]', "",
              '[node name="Sea" type="Node3D" parent="."]',
              f"transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, {SEA_Y:g}, 0)", 'script = ExtResource("2_water")',
              'wave_set = ExtResource("3_waves")', 'material = ExtResource("4_water_mat")', f"tide_line_y = {SEA_Y:g}",
              "publishes_water_level = true", "", '[node name="Shore" type="Node3D" parent="."]', ""]
    for name, piece, x, y, z, yaw in SHORE:
        lines += [f'[node name="{name}" parent="Shore" instance=ExtResource("{5 + pieces.index(piece)}_{piece}")]',
                  f"transform = {yaw_xform(yaw, (x, y, z))}", ""]
    lines += ['[node name="Marks" type="Node3D" parent="."]', ""]
    for name, at in MARKS:
        lines += [f'[node name="{name}" type="Marker3D" parent="Marks"]', f"transform = {yaw_xform(0.0, at)}", ""]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    print(f"STAGE {OUT.relative_to(ROOT)} ({len(SHORE)} shore pieces, {len(MARKS)} marks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
