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

## v2: review-sweep-N fixes (branch `gpu/env-03-vegetation-v2`, 2026-10-23)

The first version was reverted on the integration branch. v2 re-applies it (8e10a05) with these fixes.

| Finding | Change |
|---|---|
| B1: ghost trunks in the LOD fade bands | Only the last LOD fades, out over 6 m past 400 m. The 45 m and 120 m switches are hard, with the 2 m hysteresis. Godot's fade alpha-blends the instance; it isn't a dither, so the comment that said it was is gone. |
| S1: float `shelter` with a −1 sentinel | `enum Shelter { AUTO, OPEN, SHELTERED }`. |
| S2: unmasked ray; sun from the first light | The ray has a `shelter_mask` (physics layers, default 1). The sun comes from `hymn_sun_direction` through the new `ShaderGlobals`, a CPU copy of the globals (`global_shader_parameter_get` is editor-only). The four writers now go through `ShaderGlobals.set_value`: the vegetation, water, Undertow and Haluna mood test rigs. The Haluna rig line is a one-line cross-role edit. |
| Auto-detect test; the `.uid` | `test_auto_shelter_probes_toward_the_global_sun_on_the_mask`: a box roof on layer 1 shelters; off the mask, or under a low side sun, it doesn't. The `.uid` is committed. |

### Drift, re-measured (B2)

All three captures are on the GPU capture rig:
- **Base:** `origin/claude/new-session-mj8c3c`, with ENV-03 reverted.
- **v2:** this branch.
- **v2 with TAA:** this branch with the AA swap disabled, so it renders with TAA as the base does. This splits the AA
  change from the plant changes.

| Shot | Base → v2 | Base → v2 with TAA | v2 TAA → FXAA |
|---|---:|---:|---:|
| veg_backlit_fronds | 0.0225 | 0.0000 | 0.0225 |
| veg_beach_wide | 0.0307 | 0.0000 | 0.0307 |
| veg_frangipani_close | 0.0281 | 0.0000 | 0.0281 |
| haluna_h02_tidewall_lane | 0.0124 | – | – |
| haluna_h03_lintel_gull | 0.0000 | – | – |
| haluna_h01, h04, h07 | ≤ 0.0011 | – | – |

- **`veg_*`:** the drift is purely the TAA → FXAA capture. veg_beach_wide fell from 0.0436 (v1) to 0.0307; the
  difference was v1's fade band (B1).
- **`haluna_h03`:** no drift now. v1's 0.0118 was the fade band.
- **`haluna_h02` 0.0124:** one palm, seen through the gap under the right-hand eave (x ≈ 900–960, y ≈ 200–300). v2
  draws it and the base doesn't. v2 is the correct frame.
  - It isn't B1: with the last LOD's begin margin put back to 2 m, the drift stays (0.0116).
  - The palm stands at the 120 m switch. In the base, both LOD1 and LOD2 carry the 2 m hysteresis there, and on a
    still camera neither LOD shows the palm.
  - In v2, LOD2 fades, so Godot reads its margins as fade spans and drops the hysteresis. LOD2 then draws the palm.
- **Finding (not fixed):** the same hysteresis hole may still hide a plant at the 45 m switch from a camera that
  hasn't moved since load. No current shot shows one. If a cutscene shows one, overlap the ranges (LOD *n* ends at
  switch + margin) instead of relying on hysteresis.
- **Re-approval:** baselines not overwritten. Environment and Art re-approve the drifting shots: the three veg_* and
  haluna_h02. haluna_h03 is back to its pre-ENV-03 frame.

### Checks (v2)

- **Run:**
  - gdlint and gdformat on the touched files.
  - Godot tests filtered to `vegetation` (10/0), `haluna` (7/0), `undertow` (30/0) and `water` (24/0). The last
    three because their rigs now write the sun through `ShaderGlobals`.
  - The 8 vegetation and Haluna shots, captured on the GPU.
- **Skipped:**
  - The full suite and the other shots: no other scene uses VegetationPlant.
  - The Undertow and water shots on the GPU: `ShaderGlobals.set_value` writes the same sun value as before.
