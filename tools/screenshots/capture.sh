#!/usr/bin/env bash
# Render every shot in tests/screenshots/shots.json to tests/screenshots/out/ (ADR 0009).
# Usage: tools/screenshots/capture.sh [--driver vulkan|opengl3] [--shots id1,id2] [--out DIR]
# Finds the software-rendering wrapper at $HYMN_GODOT_RENDER, `godot-render` on PATH, or the
# default tools/dev/fetch_render_deps.py location. Exit 3 when it is absent (callers print SKIP).
# vulkan (default) = Forward+ on Mesa lavapipe; opengl3 = Compatibility on llvmpipe (lower fidelity).
# Each shot renders in its OWN Godot process (isolation): TAA jitter and other engine-global
# state depend on the frame count, so a shared process made every shot depend on the shots
# before it in the manifest. Set HYMN_CAPTURE_SHARED=1 for the old single-process mode.
set -euo pipefail
cd "$(dirname "$0")/../.."

driver=vulkan
user_args=()
shot_list=""
while [ $# -gt 0 ]; do
  case "$1" in
    --driver) driver="$2"; shift 2 ;;
    --shots) shot_list="$2"; shift 2 ;;
    --out) user_args+=("--out=$(realpath -m "$2")"); shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

render="${HYMN_GODOT_RENDER:-}"
if [ -z "$render" ]; then
  render="$(command -v godot-render || true)"
fi
if [ -z "$render" ]; then
  render="$HOME/.cache/hymn/godot-4.6.3+ds-2/godot-render"
fi
if [ ! -x "$render" ]; then
  echo "render wrapper not found (python3 tools/dev/fetch_godot.py && python3 tools/dev/fetch_render_deps.py)"
  exit 3
fi

method=()
if [ "$driver" = "opengl3" ]; then method=(--rendering-method gl_compatibility); fi
log="${TMPDIR:-/tmp}/hymn_capture.log"
start=$(date +%s)
if [ -z "$shot_list" ]; then
  shot_list="$(python3 -c 'import json;print(",".join(s["id"] for s in json.load(open("tests/screenshots/shots.json"))["shots"]))')"
fi
: > "$log"
status=0
run_one() {
  "$render" --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync --rendering-driver "$driver" "${method[@]}" \
    res://tests/screenshots/capture.tscn -- "${user_args[@]}" "--shots=$1" >> "$log" 2>&1
}
# M1-QA-10: a process that exits non-zero (an engine abort at exit, say, after its shot was written)
# is named here, so a gate failure says which shot's process it was.
failed_runs=()
set +e
if [ "${HYMN_CAPTURE_SHARED:-0}" = "1" ]; then
  run_one "$shot_list"
  rc=$?
  if [ $rc -ne 0 ]; then status=$rc; failed_runs+=("$shot_list (exit $rc)"); fi
else
  IFS=',' read -ra ids <<< "$shot_list"
  for id in "${ids[@]}"; do
    run_one "$id"
    rc=$?
    if [ $rc -ne 0 ]; then
      status=$rc
      failed_runs+=("$id (exit $rc)")
      echo "CAPTURE PROCESS EXIT $rc: $id" >> "$log"
    fi
  done
fi
set -e
grep -E "^(Vulkan|OpenGL)|CAPTURE|Capture:|SCRIPT ERROR" "$log" || true
echo "capture wall time: $(( $(date +%s) - start )) s (log: $log)"
if [ ${#failed_runs[@]} -gt 0 ]; then
  echo "capture process(es) exited non-zero: ${failed_runs[*]}"
fi
if grep -q "SCRIPT ERROR" "$log"; then exit 1; fi
exit $status
