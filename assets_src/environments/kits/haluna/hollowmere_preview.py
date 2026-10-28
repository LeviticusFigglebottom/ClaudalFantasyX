"""The Hollowmere and Kite preview (M3-ENV-731; hollowmere.md, kite.md): the Ch17 raft-city pieces composed round Dace's
unfinished hull under the zone's dusk grade, and the finished Kite moored on a row of its own to the east, so both
kits are seen rendered before act1-chapters (or whoever stages Act III) builds the zone.

    python3 assets_src/environments/kits/haluna/hollowmere_preview.py

Writes game/levels/_tests/hollowmere_kit/hollowmere_preview.tscn (the grade's Environment from ch17_grades.json, its
sun, the lagoon water, the pieces and the shot cameras M01, M02 and K01).
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import arena_scenes as ar  # noqa: E402  (sun_xform, yaw_xform, hexc; read-only)

OUT = ROOT / "game" / "levels" / "_tests" / "hollowmere_kit" / "hollowmere_preview.tscn"
KIT = "res://assets/environments/kits/haluna/"
GRADES = ROOT / "assets" / "environments" / "zones" / "ch17" / "ch17_grades.json"

KITE_AT = (70.0, 1.2, 0.0)  # the Kite's row, east of the city: its deck 1.2 m over the water, the keel under it
# (piece, x, y, z, yaw): the city round the dry-dock at the origin.
PIECES = [
    ("dace_hull_frame", 0.0, 0.0, 0.0, 0.0),
    ("hm_lashed_hulls", -22.0, 0.0, -6.0, 20.0),
    ("hm_lashed_hulls", 18.0, 0.0, -15.0, -35.0),
    ("hm_lashed_hulls", -15.0, 0.0, 21.0, 70.0),
    ("hm_lashed_hulls", 27.0, 0.0, 15.0, 110.0),
    ("hm_lashed_hulls", -36.0, 0.0, 13.0, -10.0),
    ("hm_windmill", -30.0, 0.0, -27.0, 30.0),
    ("hm_windmill", 35.0, 0.0, -3.0, -60.0),
    ("hm_windmill", 7.0, 0.0, 34.0, 180.0),
    ("hm_tide_wheel", 13.0, 0.0, -27.0, 30.0),
    ("hm_signal_lamp", -20.0, 0.9, -4.5, 0.0),
    ("hm_signal_lamp", 16.5, 0.9, -13.0, 0.0),
    ("hm_far_flotilla", 0.0, 0.0, 0.0, 0.0),
    ("kite_hull", *KITE_AT, 0.0),
    ("kite_rig", *KITE_AT, 0.0),
    ("kite_engine", *KITE_AT, 0.0),
    ("kite_engine", *KITE_AT, 180.0),  # the -Z engine: the +Z one turned about the hull's centre
]
# (id, eye, look, fov)
SHOTS = [
    ("M01", (7.0, 2.4, -13.0), (-1.0, 2.0, 0.5), 50.0),  # Dace's hull from the walk-board side: the frame unfinished
    ("M02", (44.0, 7.0, -42.0), (-8.0, 3.0, 8.0), 45.0),  # the raft-city at dusk, the windmills against the sky
    ("K01", (KITE_AT[0] + 14.0, 3.0, KITE_AT[2] - 16.0), (KITE_AT[0], 4.5, KITE_AT[2]), 50.0),  # the Kite, finished
]


def main() -> int:
    grade = json.loads(GRADES.read_text(encoding="utf-8"))["ch17_hollowmere_dusk"]
    sun = grade["sun"]
    ext = [("Environment", grade["environment"], "1_env"),
           ("Script", "res://game/world/camera_shot.gd", "2_shot"),
           ("Script", "res://game/levels/ch02/haluna/haluna_shot_camera.gd", "3_cam"),
           ("Script", "res://game/world/water/water_surface.gd", "4_water"),
           ("Resource", "res://game/world/water/lagoon_waves.tres", "5_waves"),
           ("Material", "res://game/levels/ch02/haluna/haluna_water_material.tres", "6_water_mat")]
    glbs = sorted({p[0] for p in PIECES})
    ext += [("PackedScene", KIT + g + ".glb", f"{7 + k}_{g}") for k, g in enumerate(glbs)]
    lines = ["[gd_scene format=3]", ""]
    lines += [f'[ext_resource type="{t}" path="{p}" id="{i}"]' for t, p, i in ext]
    lines.append("")
    for sid, eye, look, fov in SHOTS:
        lines += [f'[sub_resource type="Resource" id="Shot{sid}"]', 'script = ExtResource("2_shot")', f'id = &"{sid}"',
                  f"position = Vector3({eye[0]:g}, {eye[1]:g}, {eye[2]:g})",
                  f"look_at = Vector3({look[0]:g}, {look[1]:g}, {look[2]:g})", f"fov_deg = {fov:g}", ""]
    lines += ['[node name="HollowmerePreview" type="Node3D"]', "",
              '[node name="WorldEnvironment" type="WorldEnvironment" parent="."]', 'environment = ExtResource("1_env")', "",
              '[node name="Sun" type="DirectionalLight3D" parent="."]',
              f"transform = {ar.sun_xform(-sun['pitch_deg'], 180.0 - sun['yaw_deg'])}",
              f"light_color = {ar.hexc(sun['color'])}", f"light_energy = {sun['energy']}", "shadow_enabled = true",
              "directional_shadow_max_distance = 150.0", "",
              '[node name="Water" type="Node3D" parent="."]', 'script = ExtResource("4_water")',
              "publishes_water_level = true", 'wave_set = ExtResource("5_waves")', 'material = ExtResource("6_water_mat")',
              "", '[node name="Pieces" type="Node3D" parent="."]', ""]
    count: dict[str, int] = {}
    for name, x, y, z, yaw in PIECES:
        k = count[name] = count.get(name, 0) + 1
        rid = f"{7 + glbs.index(name)}_{name}"
        node = "".join(w.title() for w in name.split("_")) + (str(k) if k > 1 else "")
        lines += [f'[node name="{node}" parent="Pieces" instance=ExtResource("{rid}")]',
                  f"transform = {ar.yaw_xform(yaw, (x, y, z))}", ""]
    lines += ['[node name="Cameras" type="Node3D" parent="."]', ""]
    for sid, _eye, _look, _fov in SHOTS:
        lines += [f'[node name="{sid}" type="Camera3D" parent="Cameras"]', "near = 0.1", "far = 2000.0",
                  'script = ExtResource("3_cam")', f'shot = SubResource("Shot{sid}")', ""]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    print(f"PREVIEW {OUT.relative_to(ROOT)} ({len(PIECES)} pieces, {len(SHOTS)} shots)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
