"""The Ch4 ferry zone with cameras (M3-ENV-746): act1-chapters' zone scene as it is (its dressing now places bf_landing's
islet landing, gangplank, stern gate and wrapped name-board: tools/act1/ch04_ferry_dressing.py), plus the layout's F01
and F06 cameras, for env-art to render and view the zone.

    python3 assets_src/environments/kits/brightwater_ferry/bf_landing_preview.py

Writes game/levels/_tests/brightwater_landing/landing_preview.tscn.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ZONE = ROOT / "game" / "levels" / "ch04" / "brightwater_ferry"
OUT = ROOT / "game" / "levels" / "_tests" / "brightwater_landing"
SHOTS = ("F01", "F06")


def main() -> int:
    layout = json.loads((ZONE / "brightwater_ferry_layout.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    scene = (ZONE / "brightwater_ferry.tscn").read_text(encoding="utf-8")
    scene = re.sub(r"^\[gd_scene[^\]]*\]", "[gd_scene format=3]", scene, count=1, flags=re.M)
    shots = layout["shots"]
    ext = ['[ext_resource type="Script" path="res://game/world/camera_shot.gd" id="pv_shot"]',
           '[ext_resource type="Script" path="res://game/levels/ch02/haluna/haluna_shot_camera.gd" id="pv_cam"]']
    subs = []
    for sid in SHOTS:
        s = shots[sid]
        e, la = s["pos"], s["look_at"]
        subs += [f'[sub_resource type="Resource" id="Shot{sid}"]', 'script = ExtResource("pv_shot")', f'id = &"{sid}"',
                 f"position = Vector3({e[0]:g}, {e[1]:g}, {e[2]:g})",
                 f"look_at = Vector3({la[0]:g}, {la[1]:g}, {la[2]:g})", f"fov_deg = {s['fov']:g}", ""]
    head, _, nodes = scene.partition('\n[node name="BrightwaterFerry"')
    cams = ['[node name="PreviewCameras" type="Node3D" parent="."]', ""]
    for sid in SHOTS:
        cams += [f'[node name="{sid}" type="Camera3D" parent="PreviewCameras"]', "near = 0.05", "far = 2000.0",
                 'script = ExtResource("pv_cam")', f'shot = SubResource("Shot{sid}")', ""]
    text = head.rstrip("\n").split("\n")
    first_sub = next((i for i, ln in enumerate(text) if ln.startswith("[sub_resource")), len(text))
    text = text[:first_sub] + ext + [""] + subs + text[first_sub:]
    out = "\n".join(text) + '\n\n[node name="BrightwaterFerry"' + nodes.rstrip("\n") + "\n\n" + "\n".join(cams)
    (OUT / "landing_preview.tscn").write_text(out.rstrip("\n") + "\n", encoding="utf-8")
    print(f"PREVIEW {OUT.relative_to(ROOT)} ({len(SHOTS)} cameras)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
