#!/usr/bin/env bash
# Rebuild the Ch6 Stillguard soldiers (M3-CHR-508) from source: the shared weathered atlases, then per variant the
# meshes, rig and blendshapes (Blender), the skin maps (python3 + numpy + Pillow), then the Godot materials and the
# body clips.
# Blender: $HYMN_BLENDER, `blender` on PATH, or the tools/dev/fetch_blender.py wrapper.
# Usage: assets_src/characters/stillguard/build.sh [variant ...]   (every variant when none named; `ivo` for Ivo Brannick)
set -euo pipefail
cd "$(dirname "$0")/../../.."
blender="${HYMN_BLENDER:-}"
if [ -z "$blender" ]; then blender="$(command -v blender || true)"; fi
if [ -z "$blender" ]; then blender="$HOME/.cache/hymn/blender-5.0.1+dfsg-5/blender"; fi
variants=("$@")
if [ ${#variants[@]} -eq 0 ]; then variants=(a b c d e f); fi
python3 assets_src/characters/stillguard/sg_textures.py --shared
for v in "${variants[@]}"; do
  bake="$(mktemp -d)"
  "$blender" --background --factory-startup --threads 4 --python assets_src/characters/stillguard/build_stillguard.py \
    -- --variant "$v" --bake-dir "$bake" 2>&1 | grep -E "^\[stillguard|Error|Traceback" || true
  n="stillguard_$v"
  if [ ${#v} -gt 1 ]; then n="$v"; fi  # M3-CHR-540: a named Stillguard (ivo) builds under its own id
  test -s "assets/characters/$n/$n.glb"
  python3 assets_src/characters/stillguard/sg_textures.py --variant "$v" --bake-dir "$bake"
  python3 assets_src/characters/stillguard/write_materials.py --variant "$v"
  python3 assets_src/characters/asha/hero_clips.py --hero "$n"
  rm -rf "$bake"
done
