---
id: M1-RND-15
title: glimmer_bound shot plus rendering follow-ups (review-sweep-I on RND-07/08/11)
role: rendering
status: review
reviewer: environment
owner_session: "worktree-agent-a94256e372f018240"
depends_on: [M1-RND-08, M1-RND-07, M1-RND-11]
milestone: M1
request-from: "environment"
---
## Goal
From the review-sweep-I entries (file:line references there).

## Acceptance criteria
- [x] glimmer_bound added to shots.json, rendered on lavapipe, inspected and approved (closes M1-RND-08's missing criterion)
- [x] A material's own sea-glow cannot override a zone value of 0 (Ending dark sea); the sea-glow and water-level globals reset on zone change; publishes_water_level defaults to false (rivers and pools opt in)
- [x] Undertow: the march-steps floor matches the shader's range; the step cap is parsed, not copied; a missing undertow.json is an error; the FSR2 cutscene workaround is filed as a task
- [ ] Prewarm stays within SPEC §4.2's 50 ms frame limit for battle transitions (time-slice it); the docs no longer assume Low uses FXAA; Low-TAA foliage ghosting measured with wind on. **Partial:** time-slicing and docs done; the two measurements need the PC GPU (see Notes)
- [x] Stale shader comments fixed

## Notes
- 2026-10-23 rendering (worktree-agent-a94256e372f018240). Commits on `worktree-agent-a94256e372f018240`, not pushed.
- **glimmer_bound** (RND-08 B1): moved from the pending manifest into shots.json after `glimmer_release`. No capture setup was needed: the carrier moves by `delta`, which `--fixed-fps 60` makes deterministic. Inspected and approved (details in M1-RND-08 Notes). RND-08 is back in review. The anti-solar NaN fix was also confirmed on lavapipe: no disc, anti-solar mean 0.109.
- **Sea-glow hard off** (RND-08 S1). `hymn_zone_sea_glow` now has three states: > 0 zone energy, 0 unset (materials decide), < 0 hard off (`hymn_sea_glow_zone` returns 0 before it looks at the material). `GlimmerField.set_scene_sea_glow(0)` writes the hard off (`SEA_GLOW_ZONE_OFF`); `clear_scene_sea_glow()` unsets. A test checks that no water, storm-sea or overlay shader reads the global raw. The project default stays 0, so no existing shot changes. palette.json, glimmer.json and test_palette_rules.py are untouched; the Ending's E4 0.07 / E5 0.06 still pass as authored (tested).
- **Global resets** (S2). `SceneRouter._swap` calls `GlimmerField.clear_scene_sea_glow()` and `WaterSurface.clear_water_level()` just before `change_scene_to_node`. A publishing WaterSurface also resets the level in `_exit_tree`. **Cross-role edit:** game/core/scene_router.gd is Systems-owned. The change is two calls plus the prewarm wait below, public API unchanged; Systems should glance at it in review.
- **One publisher** (S3). `publishes_water_level` defaults to false; the seas in water_test and undertow_test opt in; a second publisher in the tree warns. Haluna's sea (Environment-owned) is requested in M1-ENV-05 (criterion added). No shader reads `hymn_water_level` yet, so nothing renders differently.
- **Undertow validator** (RND-11 S1-S3). The `march_steps` floor (4) comes from the uniform's `hint_range`, and the default cap (48) from the include's `#ifndef`, both parsed. A missing undertow.json is an error, and non-object tiers / quality / shaders / noise are reported instead of crashing. Nit: `viewport_is_temporal` also accepts MetalFX temporal. FSR2 cutscene workaround (S4): filed as **M1-RND-16**.
- **Prewarm time-slicing** (RND-07 S1). Draws are built at start and enter the stage `materials_per_frame` (12) per frame; the batch halves after any frame over `slice_budget_ms` (33). The stage clears `frames_to_render` frames after the last batch. SceneRouter waits while `ShaderPrewarm.is_staging_under(self)` (at most 120 frames) and records `prewarm_wait_frames`. The 12/33 values are a starting point. **Outstanding (PC GPU):** re-run `tools/gpu_bench/run_prewarm.sh` and report the worst transition frame against 50 ms (it was 121-150 ms unsliced), then tune the two values. Nit: `match_viewport()` runs on every `start()` and each transition spawns a fresh warmup, so an AA change mid-session is picked up on the next transition. The null-uniform noise in the generated prewarm .tres files is not addressed (harmless).
- **Docs.** character_shading.md keeps alpha scissor on Low, which runs TAA now: it is cheaper, stable at 30 fps, and holds with AA off. undertow.md:125 now gives the real reasons Low has no jitter. glimmer.md has the current sea-glow signatures and lists which inputs stay world-space for a local-space field. water.md documents the three-state global and the resets. architecture.md item 6 covers the sliced prewarm.
- **Outstanding (PC GPU):** Low-TAA foliage ghosting with the wind **on**, at a 30 fps cap (`tools/gpu_bench/aa_shimmer` with the wind running, plus a trail metric). This cannot be measured on lavapipe. It is the last open part of criterion 4, together with the prewarm worst frame.
- Not done here: RND-08 S5 (Art sign-off on caustics, halo chroma and noon crests) belongs to M1-ART-04 / Art.

## Review log
