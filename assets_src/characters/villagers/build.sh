#!/usr/bin/env bash
# Rebuild the Haluna villagers (M2-CHR-03) from source: per villager the meshes, rig and blendshapes
# (Blender), then the skin maps (python3 + numpy + Pillow), the Godot materials and the body clips; once, the shared
# villager cloth atlas. Blender: $HYMN_BLENDER, `blender` on PATH, or the tools/dev/fetch_blender.py
# wrapper. Usage: assets_src/characters/villagers/build.sh [npc ...]   (default: every params file)
set -euo pipefail
cd "$(dirname "$0")/../../.."
blender="${HYMN_BLENDER:-}"
if [ -z "$blender" ]; then blender="$(command -v blender || true)"; fi
if [ -z "$blender" ]; then blender="$HOME/.cache/hymn/blender-5.0.1+dfsg-5/blender"; fi
npcs=("$@")
if [ ${#npcs[@]} -eq 0 ]; then
  for f in assets_src/characters/villagers/params/*.json; do npcs+=("$(basename "$f" .json)"); done
fi
bake="$(mktemp -d)"
trap 'rm -rf "$bake"' EXIT
python3 assets_src/characters/villagers/villager_textures.py --cloth
for npc in "${npcs[@]}"; do
  "$blender" --background --factory-startup --threads 4 --python assets_src/characters/villagers/build_villager.py -- \
    --npc "$npc" --bake-dir "$bake/$npc" --report "$bake/$npc.json" 2>&1 | grep -E "^\[villager\]|Error|Traceback" || true
  test -s "assets/characters/villagers/$npc/$npc.glb"
  python3 assets_src/characters/villagers/villager_textures.py --npc "$npc" --bake-dir "$bake/$npc"
  python3 assets_src/characters/villagers/write_materials.py "$npc"
  python3 assets_src/characters/villagers/villager_clips.py "$npc"
  cat "$bake/$npc.json"
done
