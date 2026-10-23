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

- 2026-10-23 PC GPU session (session_01778wbLbDFnRRLTKjnawv3T, branch `gpu/rnd-15-prewarm`): **criterion 4 measured.**
  Report: `docs/kb/qa/gpu/2026-10-23-rnd-15-prewarm.md`.
  - **(a) Prewarm worst frame.** Measured after a field scene, cold and warm, at Low, High and Ultra.
    - It is **still over 50 ms**: ~230 ms (warm) to ~310 ms (cold) for the stage set-up, and 90–430 ms for a single
      Undertow material load (a shader compile).
    - Neither can be fixed with the slice constants. Batch size made no difference to the set-up frame (1–12 all
      measured).
    - Done: materials now load in their batch (lazy entries), the first tick no longer halves the batch (S3), and
      `materials_per_frame` is 2. Undertow's worst frame drops from 1.58 s to 0.62 s (cold).
    - Recommended: export with Godot's shader baker, keep one stage alive from boot, and register active-tier variants
      only.
  - **(b) Low-TAA foliage ghosting, wind on, 30 fps.** Measured: TAA departs from the instant 30–40 % more than its
    static softening (vegetation Wide 0.115 → 0.149, FrangipaniClose 0.113 → 0.158). It shows as soft blades and faint
    double edges, with no long trails. Acceptable for Low; nothing to tune.
  - So both measurements are done. The 50 ms limit itself is **not met**: that needs the shader baker or a boot-time
    stage (Lead / Systems decision), so the checkbox stays unticked.

## Review log
- 2026-10-23 environment (review-sweep-J, fresh reviewer): **approve the lavapipe-side work with should-fixes. Not done:** criterion 4 is still unticked. It needs the PC GPU numbers: the prewarm worst frame against 50 ms, and Low-TAA ghosting with the wind on. Keep the task in review until they land, or have the Lead split them into a gpu task.
  - **What I read:** the task, handoff rendering-2, and `git diff 4d12869^1 4d12869` (scene_router.gd, shader_prewarm.gd, glimmer_field.gd, water_surface.gd, the shader includes, the validator, the tests, shots.json). I viewed `glimmer_bound.png` (see M1-RND-08). I checked that no shader or script reads `hymn_zone_sea_glow` outside `hymn_sea_glow_zone` (grep: only glimmer.gdshaderinc:82-85).
  - **Checks:** Godot `--filter=glimmer_field` 24/0, `water_surface` 13/0, `shader_prewarm` 9/0 and `undertow` 30/0 failed. `validate_data` 0/0, and tool tests 382 OK.
  - **What passes:**
    - The three-state sea-glow (`< 0` hard off wins, glimmer.gdshaderinc:82).
    - `publishes_water_level` defaults to false, and the two test seas opt in.
    - The validator parses the step floor and cap, and MetalFX temporal counts as temporal.
    - The prewarm slicing logic and its test.
  - **Should-fix:**
    - **S1 (scene_router.gd:105, 116-119, 127): the non-split "before" profile now counts the prewarm wait.**
      - With `split_swap` off, `swap_frame_start` is taken before `prewarm_requested`, and `t = swap_frame_start` at :127. The new wait loop sits between them, so `frames[0]` includes up to 120 waited frames.
      - That breaks the M0 comparison the header promises (:100-101).
      - Fix: re-take `swap_frame_start` after the wait, or skip the wait when `split_swap` is off.
    - **S2 (API and layering, Systems to sign off).**
      - The core router now names `GlimmerField` (game/vfx) and `WaterSurface` (game/world) directly (:132-133). That loads their class scripts and shader preloads with the autoload. It also scans its own children for a `ShaderPrewarm` (:116, shader_prewarm.gd:158).
      - Prefer a `scene_swapping` signal, or an EventBus one, that those statics subscribe to, plus a generic hold API like `SaveSystem.hold_autosave` instead of a type scan.
      - Header :4 says "Public API (stable since M0)". Callers can now observe up to 2 s more under the fade, so list the wait and the global resets there.
    - **S3 (shader_prewarm.gd:132, 181-192): the first tick halves the batch on start-up cost.**
      - `start()` stages batch 1 in the same frame it loads scenes and materials and compiles front-ends. The first `tick` therefore measures that frame, which is likely over the 33 ms `slice_budget_ms` on any card.
      - Don't halve on the first tick, or measure from the second, or the self-tuning starts at half the batch for the wrong reason.
    - **S4 (water_surface.gd:77, 102-118): runtime toggles bypass the publisher group.**
      - The group is joined only in `_enter_tree`, so setting `publishes_water_level` after entering skips both the group and the second-publisher warning. test_water_surface.gd:131 does exactly that. `_exit_tree` still clears the global.
      - A second, warned publisher that leaves the tree also zeroes the level the first one owns, for a frame.
      - Make it a setter that joins and leaves the group, and clear only when the group becomes empty.
    - **S5 (the hard off is opt-in per entry).** The router resets to *unset* on every swap (:132), so an off zone must call `set_scene_sea_glow(0)` after each entry. No zone calls it yet: the grep finds none outside glimmer_field.gd. Add "the zone writes its sea-glow (0 = hard off) in `_ready`" to M1-ENV-05's water-level criterion, ideally with a validator check against palette.json's off zones.
  - **Nits:**
    - docs/kb/art/environments/vegetation.md:78 still lists FXAA. It is Art-owned: request it.
    - The prewarm .tres null-uniform noise is still there (acknowledged).
