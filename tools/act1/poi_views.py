#!/usr/bin/env python3
"""Field stills at every Act I zone map POI (act1-chapters' playthrough, ADR 0041).

For each POI of the listed zones (game/data/ui/zone_maps.json) this works out the camera the field shows there:
the layout's highest-priority `camera_volumes` row whose box holds the POI (its pos and look_at), else GreyboxZone's
hub orbit at its default yaw (greybox_defaults.json "camera" with the layout's own "camera" over it: orbit_distance
back along +z, orbit_height up, aimed at target_height over the POI). A volume a zone builds in code (Ch04Zone's
copy of ch02/haluna's) is not seen here: those POIs show the orbit.

With --render it draws each view through the zone's shot rig (game/levels/_tests/act1_zones/<rig>.tscn) into OUT,
one PNG per POI, via a copy of the rig in the _preview folder (it ignores itself in git). GODOT names the binary:

    python3 tools/act1/poi_views.py [--zones ch08/coilspire,...] [--render OUT]

Without --render it prints the views as JSON ({rig: {poi: [[pos], [look], fov]}}).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RIGS = {
    "ch04/haluna_wake": "ch04_haluna_wake_shots", "ch04/brightwater_ferry": "ch04_ferry_shots",
    "ch05/pemakar": "ch05_pemakar_shots", "ch05/ashcrown": "ch05_ashcrown_shots",
    "ch06/brine_shoals": "ch06_brine_shoals_shots", "ch07/tamsule": "ch07_tamsule_shots",
    "ch07/tamsule_bell_galleries": "ch07_bell_shots", "ch08/corrow": "ch08_corrow_shots",
    "ch08/coilspire": "ch08_coilspire_shots", "ch09/corrow_night": "ch09_corrow_night_shots",
    "ch10/ossa_fen": "ch10_ossa_fen_shots", "ch10/reedhollow": "ch10_reedhollow_shots",  # M4-A2P-010 (ADR 0205)
    "ch11/sunken_vey": "ch11_sunken_vey_shots", "ch11/lowlight": "ch11_lowlight_shots",  # M4-A2P-011
    "ch12/keth_pass": "ch12_keth_pass_shots", "ch12/quellan": "ch12_quellan_shots",  # M4-A2P-012
    "ch12/cloudloom": "ch12_cloudloom_shots",
}
RIG_DIR = "game/levels/_tests/act1_zones"
PREVIEW = ROOT / RIG_DIR / "_preview"


def poi_y(layout: dict, source: str) -> float:
    """The height of a POI's layout point ('spawn:', 'mark:', 'actor:', 'trigger:'); 0 when it names none."""
    kind, _, key = source.partition(":")
    try:
        if kind == "spawn":
            return float(layout["spawns"][key][1])
        if kind == "mark":
            return float(layout["marks"][key][1])
        if kind == "actor":
            return float(layout["actors"][key]["at"][1])
        if kind == "trigger":
            return float(next(t["at"][1] for t in layout.get("triggers", []) if t["id"] == key))
    except (KeyError, IndexError, StopIteration):
        pass
    return 0.0


def volume_at(layout: dict, p: list) -> dict | None:
    """The highest-priority camera volume whose (axis-aligned) box holds p, else None."""
    hits = [v for v in layout.get("camera_volumes", [])
            if all(abs(p[i] - v["at"][i]) <= v["size"][i] / 2.0 for i in range(3))]
    return max(hits, key=lambda v: int(v.get("priority", 0))) if hits else None


def views(zone: dict, layout: dict, defaults: dict) -> dict:
    """{poi id: [[pos], [look], fov]} for one zone map row."""
    cam = dict(defaults, **layout.get("camera", {}))
    out = {}
    for poi in zone.get("pois", []):
        x, z = poi["at"]
        y = poi_y(layout, poi["source"])
        vol = volume_at(layout, [x, y + 0.5, z])
        if vol is not None:
            out[poi["id"]] = [vol["pos"], vol["look_at"], float(vol.get("fov", cam["fov_deg"]))]
            continue
        out[poi["id"]] = [[x, y + cam["orbit_height"], z + cam["orbit_distance"]], [x, y + cam["target_height"], z],
                          cam["fov_deg"]]
    return out


def all_views(only: list[str] | None = None) -> dict:
    defaults = json.loads((ROOT / "game/data/world/greybox_defaults.json").read_text(encoding="utf-8"))["camera"]
    zones = json.loads((ROOT / "game/data/ui/zone_maps.json").read_text(encoding="utf-8"))["zone_maps"]["zones"]
    out = {}
    for zone in zones:
        if zone["id"] not in RIGS or (only and zone["id"] not in only):
            continue
        layout_path = ROOT / zone["scene"].replace("res://", "").replace(".tscn", "_layout.json")
        layout = json.loads(layout_path.read_text(encoding="utf-8"))
        out[RIGS[zone["id"]]] = views(zone, layout, defaults)
    return out


def render(rig: str, rig_views: dict, out_dir: Path) -> int:
    """Draws rig_views through a copy of the rig; returns how many captured."""
    PREVIEW.mkdir(exist_ok=True)
    (PREVIEW / ".gitignore").write_text("*\n", encoding="utf-8")  # scratch rigs never reach the repo
    text =(ROOT / RIG_DIR / f"{rig}.tscn").read_text(encoding="utf-8")
    body = "views = {\n" + ",\n".join(f'"{k}": {json.dumps(v)}' for k, v in rig_views.items()) + "\n}"
    text = re.sub(r"views = \{.*?\n\}", lambda _m: body, text, flags=re.S)
    (PREVIEW / f"{rig}_poi.tscn").write_text(text, encoding="utf-8")
    shots = [{"id": f"poi_{k}", "scene": f"res://{RIG_DIR}/_preview/{rig}_poi.tscn", "camera": f"Cameras/{k}",
              "resolution": [960, 540], "settle_frames": 24,
              "setup": {"viewport": {"use_taa": False, "screen_space_aa": 1}}} for k in rig_views]
    manifest = PREVIEW / f"{rig}_poi_shots.json"
    manifest.write_text(json.dumps({"shots": shots}), encoding="utf-8")
    godot = os.environ.get("GODOT", "godot")
    r = subprocess.run([godot, "--path", str(ROOT), "--audio-driver", "Dummy", "--rendering-driver", "vulkan",
                        "res://tests/screenshots/capture.tscn", "--", f"--out={out_dir / rig}",
                        f"--manifest=res://{RIG_DIR}/_preview/{manifest.name}"],
                       capture_output=True, text=True, check=False)
    return r.stdout.count("CAPTURE ok")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--zones", default="", help="comma-separated zone ids (default: every Act I zone with a rig)")
    ap.add_argument("--render", default="", help="render each view into this folder")
    args = ap.parse_args(argv)
    found = all_views([z for z in args.zones.split(",") if z] or None)
    if not args.render:
        print(json.dumps(found, indent=1))
        return 0
    out_dir = Path(args.render).resolve()
    for rig, rig_views in found.items():
        print(rig, render(rig, rig_views, out_dir), "/", len(rig_views), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
