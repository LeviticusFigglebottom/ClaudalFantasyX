#!/usr/bin/env bash
# Rebuild Toma (M2-CHR-02) from source: meshes, rig and blendshapes (Blender), then the baked and
# procedural textures (python3 + numpy + Pillow), then the Godot materials.
# Blender: $HYMN_BLENDER, `blender` on PATH, or the tools/dev/fetch_blender.py wrapper.
# Usage: assets_src/characters/toma/build.sh [--skip-textures]
set -euo pipefail
cd "$(dirname "$0")/../../.."
blender="${HYMN_BLENDER:-}"
if [ -z "$blender" ]; then blender="$(command -v blender || true)"; fi
if [ -z "$blender" ]; then blender="$HOME/.cache/hymn/blender-5.0.1+dfsg-5/blender"; fi
bake="$(mktemp -d)"
trap 'rm -rf "$bake"' EXIT
"$blender" --background --factory-startup --threads 4 --python assets_src/characters/toma/build_toma.py -- \
  --out assets/characters/toma/toma.glb --bake-dir "$bake" --report "$bake/report.json" 2>&1 \
  | grep -E "^\[toma\]|Error|Traceback" || true
test -s assets/characters/toma/toma.glb
if [ "${1:-}" != "--skip-textures" ]; then
  python3 assets_src/characters/toma/toma_textures.py --bake-dir "$bake"
fi
python3 assets_src/characters/toma/write_materials.py
cat "$bake/report.json"
