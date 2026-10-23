#!/usr/bin/env bash
# Undertow cameras x presets x resolutions (M1-RND-10 before/after runs).
# Usage: GODOT=/path/to/godot tools/gpu_bench/run_undertow.sh <out.csv> <label> [extra gpu_bench args]
set -euo pipefail
cd "$(dirname "$0")/../.."
csv="$(realpath -m "${1:?usage: run_undertow.sh <out.csv> <label>}")"
label="${2:?label}"; shift 2
godot="${GODOT:-godot}"
for c in Horizon Eye Night; do
  "$godot" --path . --audio-driver Dummy --disable-vsync res://tools/gpu_bench/gpu_bench.tscn -- \
    --scene=res://game/levels/_tests/undertow/undertow_test.tscn --camera="Cameras/$c" --label="$label:Cameras/$c" \
    --res="${HYMN_GPU_RES:-1920x1080,2560x1440}" --presets="${HYMN_GPU_PRESETS:-low,medium,high,ultra}" \
    --csv="$csv" "$@" 2>&1 | grep -E '^GPU_BENCH .*(low|medium|high|ultra) ' || true
done
