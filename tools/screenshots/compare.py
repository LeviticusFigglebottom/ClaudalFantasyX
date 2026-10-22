#!/usr/bin/env python3
"""Screenshot regression (SPEC §5.5) — STUB until M1 rendering work lands.

Intended flow (task M1-QA-01):
  1. `godot --path . --rendering-driver vulkan res://tests/screenshots/capture.tscn` renders
     every shot in tests/screenshots/shots.json to tests/screenshots/out/<shot>.png.
     This needs a GPU runner (headless Godot uses the dummy renderer and draws nothing).
  2. This script compares out/ against tests/screenshots/baselines/ with a per-pixel
     RMSE in linear space and fails if any shot drifts above its threshold.

Today it only validates the manifest and reports which shots lack baselines, so CI has
the job wired in from day one.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / "tests" / "screenshots" / "shots.json"
BASELINES = ROOT / "tests" / "screenshots" / "baselines"


def main() -> int:
    manifest = json.loads(SHOTS.read_text(encoding="utf-8"))
    shots = manifest.get("shots", [])
    for s in shots:
        for key in ("id", "scene", "camera", "threshold_rmse"):
            if key not in s:
                print(f"ERROR shot {s.get('id', '?')}: missing '{key}'")
                return 1
        has = (BASELINES / f"{s['id']}.png").exists()
        print(f"{'ok     ' if has else 'NO BASE'} {s['id']} ({s['scene']})")
    print(f"screenshot regression: STUB, {len(shots)} shot(s) declared; comparison not yet implemented "
          f"(needs GPU runner, see M1-QA-01)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
