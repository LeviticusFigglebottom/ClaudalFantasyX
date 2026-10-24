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

## Review log
