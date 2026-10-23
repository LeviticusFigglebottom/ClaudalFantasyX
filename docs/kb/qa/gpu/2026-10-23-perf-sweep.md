# Perf regression sweep, 2026-10-23 (PC GPU)

Machine: AMD RX 9070 XT, Godot 4.6.3-stable Forward+/Vulkan, Windows 10. Branch `gpu/perf-sweep`, at
`origin/claude/new-session-mj8c3c` 7f4c76b and later (the integration branch as of this run).

**Coverage.** 31 cameras: water ×4, Undertow ×5, Haluna mood ×5, battle sandbox ×1, the Asha stage ×5, character
shading ×6, vegetation ×3, glimmer dusk ×1, save shrine ×1. Every camera ran at Low, Medium, High and Ultra, at
1080p and 1440p: 248 rows in `docs/kb/qa/gpu/perf_baseline.csv`.

**Method.** `tools/gpu_bench/gpu_bench.tscn`, scene variant, the GPU median and p99 over 240 frames after a
120-frame, 3 s warm-up. The sweep ran in two chunks of about 15 minutes with a pause between them, one process at a
time. Load before each chunk: CPU 4 %, memory 60 %, GPU otherwise idle. Report generated with
`python tools/gpu_bench/perf_budget.py docs/kb/qa/gpu/perf_baseline.csv <chunk csvs>`.

**Budgets (SPEC §4.2).**
- Recommended tier (RTX 3060 class): High 1440p, 60 fps, so ≤ 16.7 ms.
- Minimum tier (GTX 1060 class): Low 1080p, 30–60 fps, so ≤ 33.3 ms at 30 fps and 16.7 ms at 60.
- Projection factors from the 9070 XT: 2.3–2.8× for the recommended tier, 4.2–5.0× for the minimum (estimates).
- **OVER:** even the low factor misses. **At risk:** only the high factor does.

## Summary

**Nothing is over budget, and nothing is at risk.** Every scene and camera passes all three checks.

| Check | Worst view | 9070 XT | Projected | Budget |
|---|---|---:|---:|---:|
| High 1440p (recommended) | undertow_test Eye | 5.32 ms | 12.2–14.9 ms | 16.7 |
| Low 1080p (minimum, 60 fps) | haluna_mood H02 | 1.43 ms | 6.0–7.2 ms | 16.7 |
| Medium 1080p (info) | undertow_test Eye | 2.34 ms | – | – |
| Ultra 1440p (info; no SPEC budget) | undertow_test Night | 16.67 ms | – | – |

Notes:
- **The storm dominates High.** The four costliest High views are all Undertow (3.9–5.3 ms). The Eye at 5.3 ms is
  the closest to its RND-10 cap of 6.0 ms on this card. Scenes are measured alone: a real Ch8 frame adds the zone's
  own cost on top of the storm's.
- **Ultra Undertow** (12.8–16.7 ms here) is the 64-step march, and it's expected. Ultra is the screenshot and
  trailer preset.
- **These are test scenes, not vertical-slice frames.** The budget table's "Base" (5–9 ms projected) assumes a full
  zone. Re-run this sweep on the M2 slice zone when it exists. Run the same commands; the CSV columns match.
- **Not covered:** prewarm and transition hitches (M1-RND-15) and CPU-side frame time under game logic. The CSV
  also carries CPU and wall-frame medians.

## Every view

### recommended: High 1440p, 60 fps (budget 16.7 ms; RX 9070 XT x 2.3-2.8)

| Scene / camera | 9070 XT median (p99) ms | Projected ms | Verdict |
|---|---:|---:|---|
| asha_stage Cameras/Face | 1.50 (1.52) | 3.4-4.2 | ok |
| asha_stage Cameras/Front | 1.33 (1.35) | 3.1-3.7 | ok |
| asha_stage Cameras/Profile | 1.30 (1.32) | 3.0-3.6 | ok |
| asha_stage Cameras/Sleeve | 1.41 (1.43) | 3.2-4.0 | ok |
| asha_stage Cameras/ThreeQuarter | 1.33 (1.35) | 3.1-3.7 | ok |
| battle_sandbox Stage/BattleCamera | 0.88 (0.89) | 2.0-2.5 | ok |
| glimmer_dusk ShotCamera | 1.21 (1.23) | 2.8-3.4 | ok |
| haluna_mood Cameras/H01 | 2.68 (2.75) | 6.2-7.5 | ok |
| haluna_mood Cameras/H02 | 2.77 (2.83) | 6.4-7.8 | ok |
| haluna_mood Cameras/H03 | 2.82 (2.90) | 6.5-7.9 | ok |
| haluna_mood Cameras/H04 | 2.49 (2.57) | 5.7-7.0 | ok |
| haluna_mood Cameras/H07 | 2.36 (2.41) | 5.4-6.6 | ok |
| save_shrine_test FieldCamera | 1.16 (1.17) | 2.7-3.3 | ok |
| shading_test Cameras/Cloth | 1.65 (1.68) | 3.8-4.6 | ok |
| shading_test Cameras/Compare | 1.87 (1.90) | 4.3-5.2 | ok |
| shading_test Cameras/EyeMacro | 1.86 (1.89) | 4.3-5.2 | ok |
| shading_test Cameras/FaceFront | 1.63 (1.65) | 3.8-4.6 | ok |
| shading_test Cameras/HairBack | 1.58 (1.60) | 3.6-4.4 | ok |
| shading_test Cameras/SkinEye | 1.98 (2.01) | 4.6-5.5 | ok |
| undertow_test Cameras/Day | 4.85 (4.89) | 11.2-13.6 | ok |
| undertow_test Cameras/Eye | 5.32 (5.38) | 12.2-14.9 | ok |
| undertow_test Cameras/Horizon | 3.90 (3.94) | 9.0-10.9 | ok |
| undertow_test Cameras/HorizonLow | 3.90 (3.94) | 9.0-10.9 | ok |
| undertow_test Cameras/Night | 4.95 (5.01) | 11.4-13.9 | ok |
| vegetation_test Cameras/Backlit | 1.29 (1.30) | 3.0-3.6 | ok |
| vegetation_test Cameras/FrangipaniClose | 1.73 (1.76) | 4.0-4.9 | ok |
| vegetation_test Cameras/Wide | 1.59 (1.62) | 3.7-4.5 | ok |
| water_test Cameras/Horizon | 1.60 (1.63) | 3.7-4.5 | ok |
| water_test Cameras/Lagoon | 2.07 (2.11) | 4.8-5.8 | ok |
| water_test Cameras/Night | 1.86 (1.90) | 4.3-5.2 | ok |
| water_test Cameras/Shallows | 1.92 (1.95) | 4.4-5.4 | ok |

### minimum: Low 1080p, 30 fps (budget 33.3 ms; RX 9070 XT x 4.2-5.0)

| Scene / camera | 9070 XT median (p99) ms | Projected ms | Verdict |
|---|---:|---:|---|
| asha_stage Cameras/Face | 0.52 (0.52) | 2.2-2.6 | ok |
| asha_stage Cameras/Front | 0.48 (0.49) | 2.0-2.4 | ok |
| asha_stage Cameras/Profile | 0.46 (0.46) | 1.9-2.3 | ok |
| asha_stage Cameras/Sleeve | 0.51 (0.52) | 2.1-2.6 | ok |
| asha_stage Cameras/ThreeQuarter | 0.48 (0.48) | 2.0-2.4 | ok |
| battle_sandbox Stage/BattleCamera | 0.35 (0.36) | 1.5-1.8 | ok |
| glimmer_dusk ShotCamera | 0.40 (0.41) | 1.7-2.0 | ok |
| haluna_mood Cameras/H01 | 1.14 (1.18) | 4.8-5.7 | ok |
| haluna_mood Cameras/H02 | 1.43 (1.49) | 6.0-7.2 | ok |
| haluna_mood Cameras/H03 | 1.31 (1.35) | 5.5-6.5 | ok |
| haluna_mood Cameras/H04 | 1.05 (1.10) | 4.4-5.3 | ok |
| haluna_mood Cameras/H07 | 1.08 (1.12) | 4.5-5.4 | ok |
| save_shrine_test FieldCamera | 0.40 (0.40) | 1.7-2.0 | ok |
| shading_test Cameras/Cloth | 0.57 (0.58) | 2.4-2.8 | ok |
| shading_test Cameras/Compare | 0.68 (0.68) | 2.8-3.4 | ok |
| shading_test Cameras/EyeMacro | 0.66 (0.66) | 2.8-3.3 | ok |
| shading_test Cameras/FaceFront | 0.58 (0.58) | 2.4-2.9 | ok |
| shading_test Cameras/HairBack | 0.55 (0.56) | 2.3-2.8 | ok |
| shading_test Cameras/SkinEye | 0.70 (0.71) | 2.9-3.5 | ok |
| undertow_test Cameras/Day | 1.11 (1.12) | 4.7-5.6 | ok |
| undertow_test Cameras/Eye | 1.38 (1.42) | 5.8-6.9 | ok |
| undertow_test Cameras/Horizon | 1.09 (1.11) | 4.6-5.5 | ok |
| undertow_test Cameras/HorizonLow | 1.09 (1.12) | 4.6-5.5 | ok |
| undertow_test Cameras/Night | 1.24 (1.25) | 5.2-6.2 | ok |
| vegetation_test Cameras/Backlit | 0.46 (0.47) | 1.9-2.3 | ok |
| vegetation_test Cameras/FrangipaniClose | 0.67 (0.69) | 2.8-3.4 | ok |
| vegetation_test Cameras/Wide | 0.60 (0.61) | 2.5-3.0 | ok |
| water_test Cameras/Horizon | 0.62 (0.62) | 2.6-3.1 | ok |
| water_test Cameras/Lagoon | 0.78 (0.78) | 3.3-3.9 | ok |
| water_test Cameras/Night | 0.77 (0.78) | 3.2-3.8 | ok |
| water_test Cameras/Shallows | 0.73 (0.75) | 3.1-3.7 | ok |

### minimum: Low 1080p, 60 fps (budget 16.7 ms; RX 9070 XT x 4.2-5.0)

| Scene / camera | 9070 XT median (p99) ms | Projected ms | Verdict |
|---|---:|---:|---|
| asha_stage Cameras/Face | 0.52 (0.52) | 2.2-2.6 | ok |
| asha_stage Cameras/Front | 0.48 (0.49) | 2.0-2.4 | ok |
| asha_stage Cameras/Profile | 0.46 (0.46) | 1.9-2.3 | ok |
| asha_stage Cameras/Sleeve | 0.51 (0.52) | 2.1-2.6 | ok |
| asha_stage Cameras/ThreeQuarter | 0.48 (0.48) | 2.0-2.4 | ok |
| battle_sandbox Stage/BattleCamera | 0.35 (0.36) | 1.5-1.8 | ok |
| glimmer_dusk ShotCamera | 0.40 (0.41) | 1.7-2.0 | ok |
| haluna_mood Cameras/H01 | 1.14 (1.18) | 4.8-5.7 | ok |
| haluna_mood Cameras/H02 | 1.43 (1.49) | 6.0-7.2 | ok |
| haluna_mood Cameras/H03 | 1.31 (1.35) | 5.5-6.5 | ok |
| haluna_mood Cameras/H04 | 1.05 (1.10) | 4.4-5.3 | ok |
| haluna_mood Cameras/H07 | 1.08 (1.12) | 4.5-5.4 | ok |
| save_shrine_test FieldCamera | 0.40 (0.40) | 1.7-2.0 | ok |
| shading_test Cameras/Cloth | 0.57 (0.58) | 2.4-2.8 | ok |
| shading_test Cameras/Compare | 0.68 (0.68) | 2.8-3.4 | ok |
| shading_test Cameras/EyeMacro | 0.66 (0.66) | 2.8-3.3 | ok |
| shading_test Cameras/FaceFront | 0.58 (0.58) | 2.4-2.9 | ok |
| shading_test Cameras/HairBack | 0.55 (0.56) | 2.3-2.8 | ok |
| shading_test Cameras/SkinEye | 0.70 (0.71) | 2.9-3.5 | ok |
| undertow_test Cameras/Day | 1.11 (1.12) | 4.7-5.6 | ok |
| undertow_test Cameras/Eye | 1.38 (1.42) | 5.8-6.9 | ok |
| undertow_test Cameras/Horizon | 1.09 (1.11) | 4.6-5.5 | ok |
| undertow_test Cameras/HorizonLow | 1.09 (1.12) | 4.6-5.5 | ok |
| undertow_test Cameras/Night | 1.24 (1.25) | 5.2-6.2 | ok |
| vegetation_test Cameras/Backlit | 0.46 (0.47) | 1.9-2.3 | ok |
| vegetation_test Cameras/FrangipaniClose | 0.67 (0.69) | 2.8-3.4 | ok |
| vegetation_test Cameras/Wide | 0.60 (0.61) | 2.5-3.0 | ok |
| water_test Cameras/Horizon | 0.62 (0.62) | 2.6-3.1 | ok |
| water_test Cameras/Lagoon | 0.78 (0.78) | 3.3-3.9 | ok |
| water_test Cameras/Night | 0.77 (0.78) | 3.2-3.8 | ok |
| water_test Cameras/Shallows | 0.73 (0.75) | 3.1-3.7 | ok |
