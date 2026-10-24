---
id: M1-RND-22
title: Prewarm worst frame is 230-620 ms against SPEC §4.2's 50 ms
role: rendering
status: review
reviewer: environment
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU, branch gpu/m1-rnd-22-prewarm)"
depends_on: [M1-RND-15]
milestone: M1
request-from: "qa"
---
## Goal
From review-sweep-N and the PC's QA-05c GPU verdict (docs/kb/qa/gpu/*qa-05c*).

## Acceptance criteria
- [x] Remove the floor: keep a warm-up stage alive from boot, and use Godot 4.6's shader baker or pipeline cache if available; or move the compile cost behind loading screens. **Done via the last option:** resident shaders are compiled at boot, other presets' tier variants are filtered out, and the test material is gone. A stage kept alive was measured and gave nothing. The shader baker needs export templates and is a follow-up (ADR 0029).
- [x] The router timing fault from sweep J is fixed (scene_router.gd ~:106, ~:129): `SceneRouter.frame0_start`, tested.
- [x] Measure on the GPU (the PC) at Low, High and Ultra; if 50 ms can't be met, write an ADR proposing a SPEC §4.2 clarification (for example, the limit applies after the first visit) for the Lead. Battle transitions: 34–46 ms on every preset (before 308–371). Zone and storm entries behind the fade: 142–312 ms. **ADR 0029** (proposed) defines visible versus hidden frames.
- [ ] (Moved from M1-RND-23: RND-15 review-sweep-N S1 and S2.) In the same GPU run, measure **batch 12 against batch 2** (`materials_per_frame`) for Undertow-class scenes, one ~1.5 s freeze under the fade against seven 0.1-0.3 s stutters, and **`ResourceLoader.load_threaded_request`** for the registry entries (shader_prewarm.gd `_stage_next_batch` / `_build_entry`: load the next batch's materials on a thread while the current batch renders). Record the choice and the numbers here. **(Still open after the PC pass: the PC branch predates this criterion. Lead, 2026-10-24.)**

## Notes (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB, 2026-10-24)
Report: `docs/kb/qa/gpu/2026-10-24-rnd-22-prewarm.md`.
- **The floor was:**
  - a test material registered for every transition (118 ms);
  - other presets' tier variants (75 ms each);
  - shader variants compiling on first draw.
  It was not the stage set-up.
- **Fixed by:** the registry `preset_tier` filter, the resident boot warm-up, and the FSR2 stage size (it also
  removes a pre-existing FFX error spam).
- **Tried and reverted:** a threaded harvest and threaded loads both crashed Godot on Haluna. A persistent stage
  gave nothing.
- **Follow-ups (ADR 0029):** the export shader baker; a SceneState harvest for big zones; slicing the boot
  warm-up.

**Note from M1-RND-23 (scene_router.gd changed under you).** The prewarm wait in `_swap` now loops on the router's generic `swap_holders()` (`hold_swap` / `release_swap`; ShaderPrewarm holds its parent's swap while staging) instead of `ShaderPrewarm.is_staging_under(self)`, and the two zone-global clears became `scene_swapping.emit(scene_path)` (reset by `ShaderGlobals.install`). Criterion 2's timing fault is untouched: with `split_swap` off, `swap_frame_start` is still taken before the wait. Rebase on RND-23 before you edit `_swap`.

## Review log
