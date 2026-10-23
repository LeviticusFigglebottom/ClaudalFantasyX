#!/usr/bin/env bash
# Screenshot capture on a real GPU with the official Godot build (Windows/macOS/Linux, no lavapipe
# wrapper). Same isolation as tools/screenshots/capture.sh: one Godot process per shot.
# Usage: GODOT=/path/to/godot tools/gpu_bench/capture_gpu.sh <out_dir> [id1,id2,...]
# Then: python tools/screenshots/compare.py --out <out_dir>   (never --update-baselines from a GPU run)
set -euo pipefail
cd "$(dirname "$0")/../.."
out="$(realpath -m "${1:?usage: capture_gpu.sh <out_dir> [ids]}")"
godot="${GODOT:-godot}"
ids="${2:-$(python -c "import json;print(','.join(s['id'] for s in json.load(open('tests/screenshots/shots.json'))['shots']))")}"
mkdir -p "$out"
IFS=',' read -ra shots <<< "$ids"
for id in "${shots[@]}"; do
  "$godot" --path . --audio-driver Dummy --fixed-fps 60 res://tests/screenshots/capture.tscn -- \
    --shots="$id" --out="$out" 2>&1 | grep -E '^CAPTURE|ERROR' || true
  [ -f "$out/capture_report.json" ] && mv "$out/capture_report.json" "$out/capture_report_$id.json"
done
