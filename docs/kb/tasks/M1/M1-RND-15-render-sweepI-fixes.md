---
id: M1-RND-15
title: glimmer_bound shot plus rendering follow-ups (review-sweep-I on RND-07/08/11)
role: rendering
status: done
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
- [x] Prewarm stays within SPEC §4.2's 50 ms frame limit for battle transitions (time-slice it); the docs no longer assume Low uses FXAA; Low-TAA foliage ghosting measured with wind on. **Partial:** time-slicing and docs done; the two measurements need the PC GPU (see Notes). **Measured; the 50 ms limit moved to M1-RND-22 (review-sweep-O).**
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
  - **Follow-up (first frame vs steady):**
    - Asha: first ~0.3 s, steady ≤ 10 ms.
    - Undertow merged: first 1.5 s, steady ≤ 111 ms.
    - Undertow lazy: first 0.6 s, but 7 steady frames of 0.1–0.3 s.
    - The router's split_swap wait doesn't enter the bench, which traces frames directly.
    - Details are in the report's follow-up section.
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
- 2026-10-23 environment (review-sweep-K, fresh reviewer): **pending. The PC numbers have not landed.** Keep it in review.
  - **What I checked:**
    - docs/kb/qa/gpu/ on the integration branch has no RND-15 report.
    - In the PC queue file (origin/gpu/m2-rnd-01-undertow, last commit 21f6801), item **2b "M1-RND-15 criterion 4: prewarm worst frame (Low/High/Ultra, ≤50 ms) + Low TAA foliage ghosting, wind on, 30 fps"** is still `todo`, and its branch gpu/rnd-15-prewarm doesn't exist.
    - docs/kb/handoffs/live/pc-gpu.md is still the seeded stub.
  - **Still open:**
    - criterion 4's two measurements;
    - the sweep-J should-fixes S1–S5. S1 (scene_router.gd's non-split profile now counts the prewarm wait) and S3 (the first tick halves the batch) affect how the prewarm number will read, so fix them **before** the PC measures.
  - **Next:** the Lead re-orders the PC queue if prewarm should go before 2a, or splits criterion 4 into a gpu task so the lavapipe-side work can close.
- 2026-10-23 environment (review-sweep-N, fresh reviewer): **criterion 4 is measured and the numbers are sound; the 50 ms limit is not met. Close RND-15 only by splitting that limit out.**
  - **What I read:** `docs/kb/qa/gpu/2026-10-23-rnd-15-prewarm.md`, including the Lead follow-up; `git diff eee8f1f^1 eee8f1f` (shader_prewarm.gd, prewarm_materials.json, the bench tools); scene_router.gd:100-135; and SPEC §4.2 (SPEC.md:110).
  - **Checks:** Godot 1174/0 (includes `shader_prewarm` and `scene_router`). No shot can change, because the prewarm stage is off-screen.
  - **What passes:**
    - **The method.** It traces the spawn frame, which the old `max_frame_ms` missed, and `--pre-scene` removes the one-time first-TAA cost. Cold and warm runs cover every preset.
    - **The diagnosis.** The floor is the stage set-up (about 230–310 ms) plus single-shader compiles (90–430 ms). The slice constants can't move either.
    - **The code.** Lazy entry loading is right. Sweep-J S3 is fixed (shader_prewarm.gd, `_frames_measured > 1`). `_build_entry` keeps the instanced and skipped counts consistent.
    - **Ghosting.** The Low-TAA ghosting measure is reasonable: +30–40 % over static, with no trails. Low keeps TAA.
  - **Verdict on criterion 4:** don't tick it. SPEC §4.2 ("No hitch over 50 ms during battle transitions") is a spec target, so missing it needs a decision, not a tuning pass.
    - The Lead files a task (Systems + Rendering) covering the shader baker on export, a boot-time warm stage, and active-tier-only registration.
    - If release builds can't meet 50 ms even after that, the Lead writes an ADR.
    - Once that task exists, criterion 4 reads "measured; limit moved to <task>", and RND-15 can close.
  - **Should-fix:**
    - **S1: the lazy/batch-2 choice trades one 1.5 s freeze for seven 0.1–0.3 s stutters in Undertow** (the follow-up table). Under a black fade, the single freeze is less visible than repeated stutters. Unless the transition shows motion, I'd revert to batch 12 for Undertow-class scenes. The Lead's call: record it in the follow-up task.
    - **S2: try `ResourceLoader.load_threaded_request` for the registry entries** (shader_prewarm.gd:233, :362). That moves the material load and front-end compile off the main thread. It's the one lever this report didn't measure.
    - **S3: sweep-J S1 is still open in the code** (scene_router.gd:106, :129). With `split_swap` off, `swap_frame_start` is taken before the prewarm wait, so `frames[0]` includes the waited frames. The report is right that the bench doesn't go through the router, but the router's own profile is still skewed. Re-take the timestamp after the wait.
- 2026-10-24 review-sweep-O (environment): **approve with fixes.** Sweep-N's condition is met: the Lead filed **M1-RND-22**, which carries the 50 ms limit, the shader baker or boot-time stage, the router timing fault (sweep-J S1 and sweep-N S3) and an ADR if 50 ms can't be met. So criterion 4 now reads "measured; limit moved to M1-RND-22" and is ticked.
  - **Checks:** Godot `--filter=` scene_router 7/0 failed, shader_prewarm 9/0, water_surface 14/0. scene_router.gd:103-129 still takes `swap_frame_start` before the prewarm wait when `split_swap` is off, as RND-22's criterion 2 says.
  - **Still open, and in no task until now; filed as M1-RND-23:**
    - sweep-J S4: `publishes_water_level` is still a plain export (water_surface.gd:77), so a runtime toggle skips the publisher group;
    - sweep-J S2: the router names GlimmerField and WaterSurface directly;
    - sweep-N S1 and S2: batch 12 against 2 for Undertow-class scenes, and `load_threaded_request`. These are to be measured inside RND-22's GPU run.
