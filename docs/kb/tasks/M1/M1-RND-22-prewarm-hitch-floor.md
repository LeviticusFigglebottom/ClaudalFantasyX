---
id: M1-RND-22
title: Prewarm worst frame is 230-620 ms against SPEC §4.2's 50 ms
role: rendering
status: todo
owner_session: ""
depends_on: [M1-RND-15]
milestone: M1
request-from: "qa"
---
## Goal
From review-sweep-N and the PC's QA-05c GPU verdict (docs/kb/qa/gpu/*qa-05c*).

## Acceptance criteria
- [ ] Remove the floor: keep a warm-up stage alive from boot, and use Godot 4.6's shader baker or pipeline cache if available; or move the compile cost behind loading screens
- [ ] The router timing fault from sweep J is fixed (scene_router.gd ~:106, ~:129)
- [ ] Measure on the GPU (the PC) at Low, High and Ultra; if 50 ms can't be met, write an ADR proposing a SPEC §4.2 clarification (for example, the limit applies after the first visit) for the Lead
- [ ] (Moved from M1-RND-23: RND-15 review-sweep-N S1 and S2.) In the same GPU run, measure **batch 12 against batch 2** (`materials_per_frame`) for Undertow-class scenes, one ~1.5 s freeze under the fade against seven 0.1-0.3 s stutters, and **`ResourceLoader.load_threaded_request`** for the registry entries (shader_prewarm.gd `_stage_next_batch` / `_build_entry`: load the next batch's materials on a thread while the current batch renders). Record the choice and the numbers here.

**Note from M1-RND-23 (scene_router.gd changed under you).** The prewarm wait in `_swap` now loops on the router's generic `swap_holders()` (`hold_swap` / `release_swap`; ShaderPrewarm holds its parent's swap while staging) instead of `ShaderPrewarm.is_staging_under(self)`, and the two zone-global clears became `scene_swapping.emit(scene_path)` (reset by `ShaderGlobals.install`). Criterion 2's timing fault is untouched: with `split_swap` off, `swap_frame_start` is still taken before the wait. Rebase on RND-23 before you edit `_swap`.

## Review log
