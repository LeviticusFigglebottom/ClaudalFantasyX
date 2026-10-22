#!/usr/bin/env bash
# Render every shot in tests/screenshots/shots.json to tests/screenshots/out/ (ADR 0009).
# Usage: tools/screenshots/capture.sh [--driver vulkan|opengl3] [--shots id1,id2] [--out DIR]
# Finds the software-rendering wrapper at $HYMN_GODOT_RENDER, `godot-render` on PATH, or the
# default tools/dev/fetch_render_deps.py location. Exit 3 when it is absent (callers print SKIP).
# vulkan (default) = Forward+ on Mesa lavapipe; opengl3 = Compatibility on llvmpipe (lower fidelity).
set -euo pipefail
cd "$(dirname "$0")/../.."

driver=vulkan
user_args=()
while [ $# -gt 0 ]; do
  case "$1" in
    --driver) driver="$2"; shift 2 ;;
    --shots) user_args+=("--shots=$2"); shift 2 ;;
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
set +e
"$render" --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync --rendering-driver "$driver" "${method[@]}" \
  res://tests/screenshots/capture.tscn -- "${user_args[@]}" > "$log" 2>&1
status=$?
set -e
grep -E "^(Vulkan|OpenGL)|CAPTURE|Capture:|SCRIPT ERROR" "$log" || true
echo "capture wall time: $(( $(date +%s) - start )) s (log: $log)"
if grep -q "SCRIPT ERROR" "$log"; then exit 1; fi
exit $status
