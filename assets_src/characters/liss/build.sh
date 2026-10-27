#!/usr/bin/env bash
# Rebuild Liss Varrow (M3-CHR-03) from source: meshes, rig and blendshapes (Blender), then the baked and procedural
# textures (python3 + numpy + Pillow), then the Godot materials and the body clips.
# Blender: $HYMN_BLENDER, `blender` on PATH, or the tools/dev/fetch_blender.py wrapper.
# Usage: assets_src/characters/liss/build.sh [--skip-textures]
set -euo pipefail
cd "$(dirname "$0")/../../.."
blender="${HYMN_BLENDER:-}"
if [ -z "$blender" ]; then blender="$(command -v blender || true)"; fi
if [ -z "$blender" ]; then blender="$HOME/.cache/hymn/blender-5.0.1+dfsg-5/blender"; fi
bake="$(mktemp -d)"
trap 'rm -rf "$bake"' EXIT
"$blender" --background --factory-startup --threads 4 --python assets_src/characters/liss/build_liss.py -- \
  --out assets/characters/liss/liss.glb --bake-dir "$bake" --report "$bake/report.json" 2>&1 \
  | grep -E "^\[liss\]|Error|Traceback" || true
test -s assets/characters/liss/liss.glb
if [ "${1:-}" != "--skip-textures" ]; then
  python3 assets_src/characters/liss/liss_textures.py --bake-dir "$bake"
fi
python3 assets_src/characters/liss/write_materials.py
python3 assets_src/characters/asha/hero_clips.py --hero liss
cat "$bake/report.json"
