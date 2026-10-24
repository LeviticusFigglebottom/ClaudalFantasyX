"""Writes the Saltgrass Causeway preview (M2-ENV-10): composed cameras C01-C07 at haluna.md §5.2's lenses and
heights, placed from the zone's layout anchors and its shared height function, plus the preview shot manifest.

    python3 assets_src/environments/kits/haluna/causeway_preview.py

Outputs game/levels/_tests/saltgrass_causeway_kit/causeway_preview.tscn and causeway_preview_shots.json.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
import causeway_zone as cz  # noqa: E402

OUT_DIR = ROOT / "game" / "levels" / "_tests" / "saltgrass_causeway_kit"
LAYOUT = ROOT / "assets" / "environments" / "zones" / "saltgrass_causeway" / "causeway_layout.json"


def vfov(mm: float) -> float:
    """Godot's vertical FOV for a full-frame focal length (haluna.md §5 convention)."""
    return round(2.0 * math.degrees(math.atan(12.0 / mm)), 1)


def shots(field: cz.Field, anchors: dict) -> dict:
    """id -> (camera xz, camera height above ground, look-at xz, look-at height above ground, lens mm)."""
    def nrm(t):
        return np.array([t[1], -t[0]])

    out = {}
    # C01 18 mm, 1.8 m: the head; the path snakes from bottom centre to the islet, small at the right third.
    p, t = cz.point_at(2.0)
    look = np.array(cz.ISLET[:2]) * 0.35 + cz.point_at(70.0)[0] * 0.65
    out["C01"] = (p - t * 6.0, 1.8, look, 1.2, 18)
    # C02 50 mm, 1.5 m, side-on: the party in profile against the lagoon.
    p, t = cz.point_at(44.0)
    out["C02"] = (p + nrm(t) * 9.0, 1.5, p, 1.3, 50)
    # C03 100 mm, 0.3 m: across the first tidepool to the path (the party's feet pass beyond, soft).
    px, pz, r = anchors["tide_pools"][0]
    pool = np.array([px, pz])
    p, _t = cz.point_at(66.0)
    d = (p - pool) / np.linalg.norm(p - pool)
    out["C03"] = (pool - d * (r * 1.3), 0.3, pool + d * (r * 0.4), 0.0, 100)
    # C04 35 mm, 1.2 m: the receding row of marker posts, the broken one in the foreground.
    bp = np.array(anchors["broken_post"])
    p, t = cz.point_at(52.0)
    off = (bp - p) / max(float(np.linalg.norm(bp - p)), 1e-6)
    out["C04"] = (bp - t * 3.0 + off * 0.8, 1.2, cz.point_at(112.0)[0], 1.0, 35)
    # C05 28 mm, 0.8 m: the half-buried Lit Age ring large in frame, its glint, the party small beyond.
    ring = np.array(anchors["lit_age_ring"])
    p, _t = cz.point_at(132.0)
    d = (p - ring) / np.linalg.norm(p - ring)
    out["C05"] = (ring - d * 3.6, 0.8, ring + d * 1.5, 0.7, 28)
    # C06 65 mm, 1.0 m: saltgrass soft in the foreground, the party small mid-ground, the islet beyond.
    p, t = cz.point_at(150.0)
    out["C06"] = (cz.point_at(110.0)[0] - nrm(t) * 16.0, 1.0, np.array(cz.ISLET[:2]) * 0.5 + p * 0.5, 1.2, 65)
    # C07 24 mm, 0.6 m, tilted up 20 degrees: the flier's sky.
    p, t = cz.point_at(90.0)
    out["C07"] = (p, 0.6, p + t * 10.0, 0.6 + 10.0 * math.tan(math.radians(20.0)), 24)
    # C08 35 mm, 1.6 m: arriving at the Drownbell's disc, its paving rings and sunk pool ahead (B10's approach).
    dx, dz, _r = anchors["drownbell_disc"]
    disc = np.array([dx, dz])
    p, t = cz.point_at(cz.DISC_AT_M - cz.DISC_R_M - 9.0)
    out["C08"] = (p, 1.6, disc + t * 2.0, -0.4, 35)
    return out


def main() -> int:
    field = cz.Field()
    anchors = json.loads(LAYOUT.read_text())["anchors"]

    def gy(x: float, z: float) -> float:
        return max(cz._walk_y(field, float(x), float(z)), cz.LOW_WATER_M)

    subs, nodes = [], []
    table = shots(field, anchors)
    for k, (cam, h, look, lh, mm) in table.items():
        cy, ly = gy(cam[0], cam[1]) + h, gy(look[0], look[1]) + lh
        subs.append(f'[sub_resource type="Resource" id="Shot{k}"]\nscript = ExtResource("3_shot")\nid = &"{k}"\n'
                    f"position = Vector3({cam[0]:.2f}, {cy:.2f}, {cam[1]:.2f})\n"
                    f"look_at = Vector3({look[0]:.2f}, {ly:.2f}, {look[1]:.2f})\nfov_deg = {vfov(mm)}\n")
        nodes.append(f'[node name="{k}" type="Camera3D" parent="Cameras"]\nnear = 0.05\nfar = 6000.0\n'
                     f'script = ExtResource("2_cam")\nshot = SubResource("Shot{k}")\n')
    tscn = (f"[gd_scene load_steps={4 + len(table)} format=3]\n\n"
            '[ext_resource type="PackedScene" path="res://assets/environments/zones/saltgrass_causeway/'
            'saltgrass_causeway_dressing.tscn" id="1_zone"]\n'
            '[ext_resource type="Script" path="res://game/levels/ch02/haluna/haluna_shot_camera.gd" id="2_cam"]\n'
            '[ext_resource type="Script" path="res://game/world/camera_shot.gd" id="3_shot"]\n\n'
            + "\n".join(subs)
            + '\n[node name="SaltgrassCauseway" instance=ExtResource("1_zone")]\n\n'
            '[node name="Cameras" type="Node3D" parent="."]\n\n' + "\n".join(nodes))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "causeway_preview.tscn").write_text(tscn, encoding="utf-8")
    base = {"resolution": [960, 540], "settle_frames": 24,
            "setup": {"globals": {"hymn_wind_time": 40.0}, "viewport": {"use_taa": False, "screen_space_aa": 1}}}
    manifest = {"doc": "M2-ENV-10 Saltgrass Causeway preview views C01-C07 (haluna.md §5.2), written by "
                       "assets_src/environments/kits/haluna/causeway_preview.py. Capture with --manifest.",
                "shots": [dict({"id": f"causeway_{k.lower()}",
                                "scene": "res://game/levels/_tests/saltgrass_causeway_kit/causeway_preview.tscn",
                                "camera": f"Cameras/{k}"}, **base) for k in table]}
    (OUT_DIR / "causeway_preview_shots.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print(f"CAUSEWAY preview: {len(table)} cameras -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
