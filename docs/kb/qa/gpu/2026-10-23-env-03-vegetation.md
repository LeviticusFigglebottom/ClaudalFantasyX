# M1-ENV-03 vegetation follow-ups, judged on the GPU (2026-10-23)

Machine: RX 9070 XT, Godot 4.6.3. Branch `gpu/env-03-vegetation`. This is an Environment task, routed to the PC GPU
session by the Lead.

| Criterion | Change | Measured |
|---|---|---|
| Plants under eaves glow | The instance uniform `inst_translucency_shelter` (foliage body) turns `translucency_shadow_floor` off. `VegetationPlant.shelter` is AUTO by default: a ray from 80 % of the plant's height toward the sun; a hit means sheltered. 0 or 1 by hand. | `tools/gpu_bench/eave_glow.tscn`, a roof 1 m above a frangipani's crown. Auto-detected. The glow removed under the roof: mean 0.013, p99 0.23, max 0.37 linear luminance. The first probe started at 2 m and mis-flagged a sunlit palm whose trunk passes under a house; it now starts at the crown. |
| Capture under FXAA, threshold 0.008 | `vegetation_test.gd` swaps TAA for FXAA under `capture.tscn` and restores it on exit, as `water_test_rig.gd` does. The three `veg_*` shots drop their 0.018 thresholds (default 0.008). | Two shot orders on the GPU: RMSE 0.00009 / 0 / 0. TAA was already order-independent on this GPU; lavapipe's TAA history is what needed 0.018. |
| LOD fade | `VegetationPlant.lod_fade_m` 6 m: `VISIBILITY_RANGE_FADE_SELF`, with the incoming LOD starting at switch + fade so the fades overlap. The last LOD fades out at 400 m. `lod_fade_m` 0 is the old hard switch. | Cost: Wide High 1440p 1.56 → 1.60 ms, Backlit unchanged. `tools/gpu_bench/lod_pop.tscn` (camera sweep, or a switch-distance sweep at a fixed camera): the LOD0 → 1 change at 45 m is only 0.84/255 mean, so the visible pop is the final 400 m cut against the sky, which now fades. |
| Overdraw budget | `gpu_bench --debug-draw=overdraw` | Layers per pixel (1080p High): Wide mean 1.64 / p99 11.9; Backlit 0.50 / 4.6; FrangipaniClose 4.36 / 11.9. Budget in vegetation.md: wide ≤ 2.5 / p99 ≤ 12, close-up ≤ 5 / 14. The hot spots are the near salt-grass clumps (8–16 layers). |
| PLACEHOLDER | `docs/kb/art/environments/vegetation_placeholders.md` lists every asset pending Art sign-off; vegetation.md points to it. | – |
| Wind flutter cap | Recorded in vegetation.md: 0.02 m at 3.5 Hz on TAA presets. Raise it only with a ghosting re-measure. | Ghosting at 30 fps on Low (RND-15): +30–40 % over TAA's static softening, no trails. |

## Drift (GPU capture rig, before → after; lavapipe baselines not overwritten)

| Shot | RMSE | Why |
|---|---:|---|
| veg_backlit_fronds | 0.0225 | TAA → FXAA capture |
| veg_frangipani_close | 0.0285 | TAA → FXAA capture |
| veg_beach_wide | 0.0436 | TAA → FXAA capture |
| haluna_h02_tidewall_lane | 0.0124 | a palm in the 45–51 m fade band (with the fade off: 0.0000) |
| haluna_h03_lintel_gull | 0.0118 | the same |
| haluna_h01, h04, h07 | ≤ 0.0007 | – |

## Checks

- **Run:** gdlint and gdformat on the touched files; the Godot tests filtered to `vegetation_plant` (5/0, new) and
  `graphics_settings` (24/0); validate_data; taskboard.
- **Skipped:** the full suite (outside the diff) and the other shots (their scenes don't use VegetationPlant or the
  foliage shader).
