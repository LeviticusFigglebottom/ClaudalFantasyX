#!/usr/bin/env bash
# Rebuild the menu portraits in tools/portraits/portraits.json (M2-MNU-301, ADR 0120).
# Usage: tools/portraits/render.sh [--only id1,id2] [--emotions tag1,tag2] [--out DIR]
# Default output: each entry's out_dir (assets/ui/portraits/...). --out writes previews elsewhere.
# Each manifest entry renders in its OWN Godot process (as tools/screenshots/capture.sh does), on the
# software-rendering wrapper at $HYMN_GODOT_RENDER, `godot-render` on PATH, or the default
# tools/dev/fetch_render_deps.py location. Exit 3 when it is absent. A process still running after
# HYMN_PORTRAIT_TIMEOUT seconds (default 900) is killed (its own process group only).
set -euo pipefail
cd "$(dirname "$0")/../.."

only=""
user_args=()
while [ $# -gt 0 ]; do
  case "$1" in
    --only) only="$2"; shift 2 ;;
    --emotions) user_args+=("--emotions=$2"); shift 2 ;;
    --out) user_args+=("--out-dir=$(realpath -m "$2")"); shift 2 ;;
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

if [ -z "$only" ]; then
  only="$(python3 -c 'import json;m=json.load(open("tools/portraits/portraits.json"));print(",".join(e["id"] for k in ("heroes","creatures") for e in m.get(k,[])))')"
fi
log="${TMPDIR:-/tmp}/hymn_portraits.log"
: > "$log"
limit="${HYMN_PORTRAIT_TIMEOUT:-900}"
status=0
IFS=',' read -ra ids <<< "$only"
for id in "${ids[@]}"; do
  set +e
  timeout -k 30 "$limit" "$render" --path . --audio-driver Dummy --fixed-fps 60 --disable-vsync \
    --rendering-driver vulkan res://tools/portraits/portrait_renderer.tscn -- "--only=$id" "${user_args[@]}" >> "$log" 2>&1
  rc=$?
  set -e
  if [ $rc -ne 0 ]; then
    status=$rc
    echo "PORTRAIT PROCESS EXIT $rc: $id" >> "$log"
  fi
done
grep -E "PORTRAIT|Portraits:|SCRIPT ERROR" "$log" || true
echo "log: $log"
if grep -q "SCRIPT ERROR" "$log"; then exit 1; fi
exit $status
