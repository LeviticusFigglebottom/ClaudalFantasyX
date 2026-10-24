#!/usr/bin/env bash
# A cold first launch of the baked release, checked against ADR 0029 / 0037 (M2-RND-19).
# Usage: GODOT=/path/to/godot tools/gpu_bench/run_cold_launch.sh <preset> [segments] [--export]
# Clears every pipeline cache first: the project's marker and shader caches in user://, and the AMD driver's Vulkan
# cache (it rebuilds itself), so the run sees what a player's first launch sees. Then runs slice_sweep with
# --budget --pipeline-trace on the "Windows Perf" export (a release build bakes its shaders only from a windowed
# export; --export rebuilds it first). Exits 1 if a segment is over budget. Windowed, never --headless; one at a time.
set -euo pipefail
cd "$(dirname "$0")/../.."
preset="${1:?usage: run_cold_launch.sh <preset> [segments] [--export]}"
segments="${2:-launch,title,haluna_beach}"
godot="${GODOT:-godot}"
out="${HYMN_COLD_DIR:-${TMPDIR:-/tmp}/hymn_cold_launch}"
mkdir -p "$out"
exe="$out/hymn_perf.exe"
if [ "${3:-}" = "--export" ] || [ ! -f "$exe" ]; then
  "$godot" --headless --path . --import > /dev/null 2>&1 || true
  "$godot" --path . --export-release "Windows Perf" "$exe" > "$out/export.log" 2>&1
  git checkout -q project.godot  # the export re-saves it
fi
userdata="${APPDATA:-$HOME/.local/share}/Godot/app_userdata/Hymn of the Undertow"
rm -f "$userdata/pipeline_warm.cfg"
rm -rf "$userdata/shader_cache" "$userdata/vulkan"
[ -n "${LOCALAPPDATA:-}" ] && rm -rf "$LOCALAPPDATA/AMD/VkCache"
log="$out/cold_${preset}.log"
rc=0
"$exe" --audio-driver Dummy --disable-vsync -- --preset="$preset" --res=2560x1440 --dwell=2 \
  --segments="$segments" --pipeline-trace --budget > "$log" 2>&1 || rc=$?
grep -E '^SLICE_BUDGET|^SLICE_SWEEP|SLICE_TIMEOUT' "$log" || true
echo "log: $log (exit $rc)"
exit "$rc"
