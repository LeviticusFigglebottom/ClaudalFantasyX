#!/usr/bin/env bash
# Full GPU sweep: every test scene x preset x resolution, plus the Undertow and water breakdowns.
# Usage: GODOT=/path/to/godot tools/gpu_bench/run_sweep.sh <out.csv> [extra gpu_bench args]
# One Godot process per scene/camera so no state leaks between scenes. Windowed, never --headless.
set -euo pipefail
cd "$(dirname "$0")/../.."
csv="$(realpath -m "${1:?usage: run_sweep.sh <out.csv>}")"; shift || true
godot="${GODOT:-godot}"
res="${HYMN_GPU_RES:-1920x1080,2560x1440}"
run() {  # run <label> <scene> <camera> [args...]
  local label="$1" scene="$2" cam="$3"; shift 3
  echo "== $label"
  "$godot" --path . --audio-driver Dummy --disable-vsync res://tools/gpu_bench/gpu_bench.tscn -- \
    --scene="$scene" --camera="$cam" --label="$label:$cam" --res="$res" --csv="$csv" "$@" "${EXTRA[@]}" 2>&1 \
    | grep -E '^GPU_BENCH|ERROR|SCRIPT ERROR' || true
}
EXTRA=("$@")
T=res://game/levels/_tests
for c in Shallows Lagoon Horizon Night; do run water "$T/water/water_test.tscn" "Cameras/$c"; done
for c in Horizon Eye Night; do run undertow "$T/undertow/undertow_test.tscn" "Cameras/$c"; done
for s in glimmer_dusk glimmer_night_held glimmer_release; do run "$s" "$T/glimmer/$s.tscn" ShotCamera; done
for c in Backlit FrangipaniClose Wide; do run vegetation "$T/vegetation/vegetation_test.tscn" "Cameras/$c"; done
for c in SkinEye HairBack Cloth; do run character_shading "$T/character_shading/shading_test.tscn" "Cameras/$c"; done
for c in Slender/Cameras/Front Slender/Cameras/Face Heavy/Cameras/ThreeQuarter; do
  run characters "$T/characters/base_body_test.tscn" "$c"
done
run field_court "$T/field/field_shot_court.tscn" default
run battle_sandbox res://game/battle/scene/battle_sandbox.tscn default
# Feature breakdowns (UndertowBench / WaterBench CONFIGS) at the two budget presets.
for c in Horizon Eye; do
  run undertow_breakdown "$T/undertow/undertow_test.tscn" "Cameras/$c" --variants=undertow --presets=low,high
done
run water_breakdown "$T/water/water_test.tscn" Cameras/Lagoon --variants=water --presets=low,high
