"""The Act II zone pieces in review rows (M3-ENV-732): every Ansedra, Keth, Lowlight and Ossa Fen zone piece that no
arena or zone scene places yet, set out in rows under one plain daylight grade, so the "parts look primitive" audit
can see them rendered before a zone builder stages them. Shape review only: each zone's own light is its sheet's.

    python3 assets_src/environments/kits/haluna/late_kit_rows.py

Writes game/levels/_tests/late_kit_rows/late_kit_rows.tscn (ch05_ashcrown_day's Environment and sun, a plain ground,
the rows, and the cameras listed in SHOTS).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import arena_scenes as ar  # noqa: E402  (sun_xform, yaw_xform, look_xform, hexc; read-only)

OUT = ROOT / "game" / "levels" / "_tests" / "late_kit_rows" / "late_kit_rows.tscn"
KIT = "res://assets/environments/kits/haluna/"
GRADES = ROOT / "assets" / "environments" / "zones" / "ch05" / "ch05_grades.json"
GRADE = "ch05_ashcrown_day"  # an overcast daylight: shapes read, nothing glows

# (piece, x, y, z, yaw) by row: Ansedra z 0, Keth z -80, Lowlight z -160, Ossa Fen z -220.
PIECES = [
    ("lacquer_court_ground", 0.0, 0.0, 0.0, 0.0), ("lacquer_hall", 40.0, 0.0, 0.0, 0.0),
    ("sanctum_basin", 66.0, 1.2, 0.0, 0.0), ("archive_stacks", 86.0, 0.0, 0.0, 0.0),
    ("cloudloom_hall", 0.0, 1.0, -80.0, 0.0), ("quellan_house", 30.0, 0.0, -80.0, 0.0),
    ("woolback_trough", 40.0, 0.0, -80.0, 0.0), ("woven_awning", 46.0, 0.0, -80.0, 0.0),
    ("keth_curtain", 54.0, 4.2, -80.0, 0.0), ("keth_road_switchback", 62.0, 0.2, -80.0, 0.0),
    ("keth_scree_slope", 100.0, 0.1, -70.0, 0.0),
    # M3-ENV-734: Quellan's inn and well, Hesk's dais.
    ("quellan_inn", 140.0, 0.0, -80.0, 0.0), ("quellan_well", 156.0, 0.0, -78.0, 0.0),
    ("hesk_dais", 166.0, 0.0, -80.0, 0.0),
    ("lowlight_nave_bay", 0.0, 0.8, -160.0, 0.0), ("lowlight_nave_bay_broken", 22.0, 0.8, -160.0, 0.0),
    ("lowlight_sanctum", 45.0, 0.7, -160.0, 0.0), ("vey_arcade_bay", 65.0, 4.0, -160.0, 0.0),
    ("strangler_fig", 80.0, 0.5, -160.0, 0.0), ("vey_gallery_bridge", 92.0, 2.0, -160.0, 0.0),
    ("lamp_niche_tier", 100.0, 0.0, -160.0, 0.0), ("conduit_housing", 106.0, 1.0, -160.0, 0.0),
    ("well_shaft", 118.0, 0.0, -160.0, 0.0),
    # M3-ENV-735: a Sunken Vey gallery walk (two lengths, a broken column beside it) and Lowlight's lamp bench.
    ("vey_gallery_walk_6m", 140.0, 2.0, -160.0, 0.0), ("vey_gallery_walk_6m", 146.0, 2.0, -160.0, 0.0),
    ("ruin_column_broken", 143.0, 0.0, -164.2, 0.0), ("lowlight_lamp_bench", 156.0, 0.0, -160.0, 0.0),
    ("kirru_roost", 0.0, 0.6, -220.0, 0.0), ("name_shell_cord", 8.0, 0.5, -220.0, 0.0),
    # M3-ENV-733: the Ch10 walks, a house platform with a roost on it, and the clutch's stone.
    ("root_walk_6m", 18.0, 0.6, -220.0, 0.0), ("reed_causeway_6m", 25.0, 0.6, -220.0, 0.0),
    ("reed_platform_6m", 34.0, 0.6, -220.0, 0.0), ("kirru_roost", 34.0, 0.6, -220.0, 0.0),
    ("clutch_stone", 41.0, 0.0, -220.0, 0.0),
]
# (id, eye, look, fov)
SHOTS = [
    ("A1", (20.0, 9.0, 30.0), (22.0, 2.0, -2.0), 55.0),  # the Lacquer Court's ground and a hall
    ("A2", (76.0, 5.0, 14.0), (78.0, 0.5, 0.0), 50.0),  # the Sanctum basin and the archive stacks
    ("K1", (14.0, 6.0, -56.0), (16.0, 3.0, -82.0), 55.0),  # the Cloudloom hall and a Quellan house
    ("K2", (58.0, 4.0, -66.0), (66.0, 2.0, -84.0), 55.0),  # the trough, awning, curtain and road
    ("K3", (152.0, 4.0, -64.0), (152.0, 2.5, -80.0), 55.0),  # the inn, the well and Hesk's dais
    ("L1", (22.0, 8.0, -138.0), (22.0, 6.0, -162.0), 60.0),  # the nave bays, whole and broken
    ("L2", (88.0, 6.0, -146.0), (92.0, 3.0, -162.0), 60.0),  # the arcade, the fig, the bridge, the niches, the well
    ("L3", (150.0, 4.5, -146.0), (147.0, 1.5, -160.0), 55.0),  # the gallery walk and the lamp bench
    ("F1", (4.0, 2.4, -212.0), (4.0, 1.5, -220.0), 50.0),  # the Kirru roost and a name-shell cord
    ("F2", (30.0, 4.5, -206.0), (29.0, 0.8, -220.0), 55.0),  # the root-walk, the reed causeway, a house, the stone
]


def main() -> int:
    grade = json.loads(GRADES.read_text(encoding="utf-8"))[GRADE]
    sun = grade["sun"]
    ext = [("Environment", grade["environment"], "1_env"),
           ("Script", "res://game/world/camera_shot.gd", "2_shot"),
           ("Script", "res://game/levels/ch02/haluna/haluna_shot_camera.gd", "3_cam")]
    glbs = sorted({p[0] for p in PIECES})
    ext += [("PackedScene", KIT + g + ".glb", f"{4 + k}_{g}") for k, g in enumerate(glbs)]
    lines = ["[gd_scene format=3]", ""]
    lines += [f'[ext_resource type="{t}" path="{p}" id="{i}"]' for t, p, i in ext]
    lines.append("")
    for sid, eye, look, fov in SHOTS:
        lines += [f'[sub_resource type="Resource" id="Shot{sid}"]', 'script = ExtResource("2_shot")', f'id = &"{sid}"',
                  f"position = Vector3({eye[0]:g}, {eye[1]:g}, {eye[2]:g})",
                  f"look_at = Vector3({look[0]:g}, {look[1]:g}, {look[2]:g})", f"fov_deg = {fov:g}", ""]
    lines += ['[sub_resource type="StandardMaterial3D" id="GroundMat"]', "albedo_color = Color(0.54, 0.52, 0.47, 1)",
              "roughness = 0.95", "", '[sub_resource type="PlaneMesh" id="GroundMesh"]',
              'material = SubResource("GroundMat")', "size = Vector2(400, 400)", "",
              '[node name="LateKitRows" type="Node3D"]', "",
              '[node name="WorldEnvironment" type="WorldEnvironment" parent="."]', 'environment = ExtResource("1_env")', "",
              '[node name="Sun" type="DirectionalLight3D" parent="."]',
              f"transform = {ar.sun_xform(-sun['pitch_deg'], 180.0 - sun['yaw_deg'])}",
              f"light_color = {ar.hexc(sun['color'])}", f"light_energy = {sun['energy']}", "shadow_enabled = true",
              "directional_shadow_max_distance = 150.0", "",
              '[node name="Ground" type="MeshInstance3D" parent="."]',
              "transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 60, -0.02, -110)", 'mesh = SubResource("GroundMesh")',
              "", '[node name="Pieces" type="Node3D" parent="."]', ""]
    count: dict[str, int] = {}
    for name, x, y, z, yaw in PIECES:
        rid = f"{4 + glbs.index(name)}_{name}"
        node = "".join(w.title() for w in name.split("_"))
        count[node] = count.get(node, 0) + 1
        node += str(count[node]) if count[node] > 1 else ""
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
