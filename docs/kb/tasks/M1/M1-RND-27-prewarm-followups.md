---
id: M1-RND-27
title: Prewarm follow-ups (RND-22 criterion 4, the Undertow compute pipeline, ADR 0029's three follow-ups)
role: rendering
status: review
owner_session: "session_01UFcBRsk9M9EKtxJKdBU2mB (PC GPU)"
reviewer: environment
depends_on: [M1-RND-22, M2-RND-01]
milestone: M1
request-from: "lead"
---
## Goal
Review-sweep-Q closed M1-RND-22 and accepted ADR 0029 (and ADR 0028). This task carries what they left open. Items 1 and 3 to 5 need the PC GPU.

## Acceptance criteria
- [x] **RND-22 criterion 4 (moved here unmeasured).** Undertow-class scenes, `materials_per_frame` 12 against 2: one ~1.5 s freeze under the fade against seven 0.1–0.3 s stutters. Record the choice under ADR 0029's hidden-frame limit (1 s). The threaded-load half is answered: `load_threaded_request` crashed Godot on Haluna in 3 of 6 runs (2026-10-24-rnd-22-prewarm.md), so record "rejected" with that reason in shader_prewarm.gd's header.
- [x] **The Undertow compute pipeline is on the prewarm list** (ADR 0028, "Consequences"). Today it is created on the first frame the storm draws, and prewarm_materials.json has no entry for it. Warm `undertow_body*_compute.glsl` for the active preset (a one-dispatch warm-up, or a `RenderingDevice.compute_pipeline_create` at stage time), and add a test that the registry covers it.
- [x] **ADR 0029 follow-up 3:** slice the boot warm-up so that no frame is over 1 s. It is 0.53–1.66 s today, and over the limit in 9 of 18 runs.
- [ ] **ADR 0029 follow-ups 1 and 2:** the export shader baker on a release build (this needs export templates on the PC), and a `SceneState` material harvest for Haluna (0.3 s). Measure and record them. If neither can be done yet, say why in the task notes.

## Notes (PC GPU, session_01UFcBRsk9M9EKtxJKdBU2mB, 2026-10-24)
Report: `docs/kb/qa/gpu/2026-10-24-rnd-27-prewarm.md`. Branch `gpu/adr-0029-prewarm-followups`.
- **Boot warm-up (follow-up 3): every frame is under 1 s.**
  - Worst frame, cold: 0.86–0.89 s on Low, High and Ultra (was 1.06–1.20 s). Warm: 0.47–0.66 s (was ~0.75 s).
    That's 12 of 12 runs, plus a final-code check.
  - The old worst frame was the stage's first frame: the process's first 3D render, with TAA and the upscaler.
    A boot run now brings its stage up plain and turns those on one a frame.
  - Resident shaders load in their batch, so the spawn frame went from about 0.1 s to 3 ms.
  - The remaining 0.86 s is the renderer's own first-use pipelines, so the margin is thin: 11 %. The export baker
    is the real fix.
- **Undertow compute pipeline (criterion 2): done.**
  - The registry's body entries carry `compute_twin`. On a tier that marches in compute (Medium, High), the stage
    warms `undertow_body*_compute.glsl` through `UndertowBodyEffect.warm_pipeline` and skips the spatial body,
    which never draws there.
  - The effect reuses the warm pipeline. The storm transition's `start()` went from 177 to 6–9 ms.
- **`materials_per_frame` (criterion 1): 2 is kept.** Measured on the storm scene: 2 gives a worst frame of 127 ms
  over 15 frames, and 12 gives 133–142 ms over 6. The old 1.5 s is gone. Threaded loads are recorded as rejected in
  the header.
- **SceneState harvest (follow-up 2): done, and it found the real Haluna cost.** The cost wasn't instancing: three
  primitive meshes on the save shrine built their StandardMaterial3D shaders in `start()`, about 75 ms each.
  - Their materials are now read without building them, and every harvested draw is built in its batch.
  - Haluna's `start()` went from 664 to 353 ms cold, and from 506 to 270 ms warm.
- **Export baker (follow-up 1): not done.** There are no export templates on the PC. It needs a template install,
  a large official download; I'm asking the Lead or the human for a go-ahead.
- **Tests.** 3 new in `test_shader_prewarm.gd`; the prewarm filter is 14/0, and the full suite 1384/0.

## Review log
