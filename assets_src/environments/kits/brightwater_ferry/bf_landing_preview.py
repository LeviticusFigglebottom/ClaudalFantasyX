"""The landing and boarding gear in the Ch4 ferry zone (M3-ENV-746): act1-chapters' zone and dressing as they are, with
bf_landing's four pieces placed on the four greybox blocks the dressing still keeps (IsletRock, Gangplank, SternGate,
NameBoardWrapped), for env-art to view before act1-chapters adds them to tools/act1/ch04_ferry_dressing.py
(M3-ENV-749 lists the same placements).

    python3 assets_src/environments/kits/brightwater_ferry/bf_landing_preview.py

Writes game/levels/_tests/brightwater_landing/ (landing_dressing.json, landing_preview.tscn with cameras F01, F06).
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


def placements(layout: dict, collision: dict) -> list[dict]:
    """The four pieces on their blocks (the islet's rock and the gangplank's ramp are the zone's collision rows):
    each on its block's walk or foot, following the block (the story's states)."""
    b = {x["id"]: x for x in layout["blocks"] + collision["blocks"]}
    rock, plank = b["IsletRock"], next(r for r in collision["ramps"] if r["id"] == "Gangplank")
    out = [{"piece": "islet_landing", "at": [rock["pos"][0], rock["pos"][2]],
            "y": round(rock["pos"][1] + rock["size"][1] * 0.5, 3), "yaw_deg": 0.0, "block": "IsletRock"},
           {"piece": "gangplank", "at": [plank["from"][0], plank["from"][2]], "y": plank["from"][1], "yaw_deg": 0.0,
            "block": "Gangplank"}]
    for piece, block in (("stern_gate", "SternGate"), ("terrace_name_board_wrapped", "NameBoardWrapped")):
        x = b[block]
        out.append({"piece": piece, "at": [x["pos"][0], x["pos"][2]],
                    "y": round(x["pos"][1] - x["size"][1] * 0.5, 3), "yaw_deg": 0.0, "block": block})
    return out


def main() -> int:
    layout = json.loads((ZONE / "brightwater_ferry_layout.json").read_text(encoding="utf-8"))
    dressing = json.loads((ZONE / "brightwater_ferry_dressing.json").read_text(encoding="utf-8"))
    collision = json.loads((ZONE / "brightwater_ferry_collision.json").read_text(encoding="utf-8"))
    dressing["greybox"]["keep"] = []
    dressing["pieces"] += placements(layout, collision)
    dressing["_about"] = "env-art's preview of M3-ENV-746 on act1-chapters' dressing; generated, not shipped."
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "landing_dressing.json").write_text(json.dumps(dressing, indent=1) + "\n", encoding="utf-8")
    scene = (ZONE / "brightwater_ferry.tscn").read_text(encoding="utf-8")
    scene = scene.replace("res://game/levels/ch04/brightwater_ferry/brightwater_ferry_dressing.json",
                          "res://game/levels/_tests/brightwater_landing/landing_dressing.json")
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
    print(f"PREVIEW {OUT.relative_to(ROOT)} (+{len(placements(layout, collision))} pieces)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
