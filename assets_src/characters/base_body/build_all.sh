#!/usr/bin/env bash
# Rebuild every base-body variant (M1-CHR-01). Blender: $HYMN_BLENDER, `blender` on PATH, or the
# sandbox wrapper from tools/dev/fetch_blender.py. Usage: assets_src/characters/base_body/build_all.sh [variant...]
# Single-threaded, as the rebuild gate runs it (M1-CHR-06, M1-QA-06): build.py exports tangents, and
# Blender's threaded tangent export races, so a default-thread build can commit a variant the gate rejects.
set -euo pipefail
cd "$(dirname "$0")/../../.."
blender="${HYMN_BLENDER:-}"
if [ -z "$blender" ]; then blender="$(command -v blender || true)"; fi
if [ -z "$blender" ]; then blender="$HOME/.cache/hymn/blender-5.0.1+dfsg-5/blender"; fi
variants=("$@")
if [ ${#variants[@]} -eq 0 ]; then variants=(slender athletic heavy); fi
for v in "${variants[@]}"; do
  "$blender" --threads 1 --background --factory-startup --python assets_src/characters/base_body/build.py -- \
    --variant "$v" --out "assets/characters/base_body/base_body_$v.glb" 2>&1 | grep -E "^\[base_body|Error|Traceback" || true
  test -s "assets/characters/base_body/base_body_$v.glb"
done
