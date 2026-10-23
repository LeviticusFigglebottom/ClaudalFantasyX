#!/usr/bin/env bash
# Cold/warm scene-entry hitch matrix (M1-RND-07). Clears ONLY this project's Godot caches
# (user://shader_cache and user://vulkan under app_userdata/<project name>) before each cold run.
# Usage: GODOT=/path/to/godot USERDATA="<app_userdata dir>" tools/gpu_bench/run_prewarm.sh <out.csv> [scene ...]
set -euo pipefail
cd "$(dirname "$0")/../.."
csv="$(realpath -m "${1:?usage: run_prewarm.sh <out.csv> [scenes]}")"
shift
godot="${GODOT:-godot}"
ud="${USERDATA:?set USERDATA to the project app_userdata directory}"

run() {
  "$godot" --path . --audio-driver Dummy --disable-vsync res://tools/gpu_bench/prewarm_bench.tscn -- \
    --scene="$1" --label="$2" --csv="$csv" "${@:3}" 2>&1 | grep -E '^PREWARM_BENCH|SCRIPT ERROR' || true
}

for s in "$@"; do
  rm -rf "$ud/shader_cache" "$ud/vulkan"
  run "$s" cold_no_prewarm
  rm -rf "$ud/shader_cache" "$ud/vulkan"
  run "$s" cold_prewarm --prewarm
  run "$s" warm_no_prewarm
  run "$s" warm_prewarm --prewarm
done
