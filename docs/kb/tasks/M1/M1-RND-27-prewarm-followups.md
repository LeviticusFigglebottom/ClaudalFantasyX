---
id: M1-RND-27
title: Prewarm follow-ups (RND-22 criterion 4, the Undertow compute pipeline, ADR 0029's three follow-ups)
role: rendering
status: todo
owner_session: ""
reviewer: environment
depends_on: [M1-RND-22, M2-RND-01]
milestone: M1
request-from: "lead"
---
## Goal
Review-sweep-Q closed M1-RND-22 and accepted ADR 0029 (and ADR 0028). This task carries what they left open. Items 1 and 3 to 5 need the PC GPU.

## Acceptance criteria
- [ ] **RND-22 criterion 4 (moved here unmeasured).** Undertow-class scenes, `materials_per_frame` 12 against 2: one ~1.5 s freeze under the fade against seven 0.1–0.3 s stutters. Record the choice under ADR 0029's hidden-frame limit (1 s). The threaded-load half is answered: `load_threaded_request` crashed Godot on Haluna in 3 of 6 runs (2026-10-24-rnd-22-prewarm.md), so record "rejected" with that reason in shader_prewarm.gd's header.
- [ ] **The Undertow compute pipeline is on the prewarm list** (ADR 0028, "Consequences"). Today it is created on the first frame the storm draws, and prewarm_materials.json has no entry for it. Warm `undertow_body*_compute.glsl` for the active preset (a one-dispatch warm-up, or a `RenderingDevice.compute_pipeline_create` at stage time), and add a test that the registry covers it.
- [ ] **ADR 0029 follow-up 3:** slice the boot warm-up so that no frame is over 1 s. It is 0.53–1.66 s today, and over the limit in 9 of 18 runs.
- [ ] **ADR 0029 follow-ups 1 and 2:** the export shader baker on a release build (this needs export templates on the PC), and a `SceneState` material harvest for Haluna (0.3 s). Measure and record them. If neither can be done yet, say why in the task notes.

## Review log
