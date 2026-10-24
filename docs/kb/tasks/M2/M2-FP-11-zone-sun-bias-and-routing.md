---
id: M2-FP-11
title: Undo M2-FP-09's zone-sun shadow bias 3.0 at merge; FlowRouting with two waiters
role: architect
status: review
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-FP-09]
milestone: M2
request-from: "lead"
reviewer: rendering
---
## Goal
These are review-sweep-O's findings on M2-FP-09, whose code is on `claude/first-playable` (7015a03) and isn't merged yet. Do this in the same batch as that merge.

## Acceptance criteria
- [x] **The zone suns go back to bias 1.0.** FP-09 criterion 5 set `face_key_shadow_normal_bias = 3.0` on haluna.tscn and `shadow_normal_bias = 3.0` on first_verse.tscn's sun. That was written before the PC measured it. M1-RND-20's follow-up (docs/kb/qa/gpu/2026-10-23-rnd-18-20-followups.md, character_shading.md "Shadows on characters") found that at Haluna's cascade, 2.5-4.5 only erases the nose shadow, that 1.0 already leaves the smile corner clean, and that **the Haluna sun stays at 1.0**. Remove the Haluna override (or set it to 0), set first_verse's sun back to 1.0, and leave the close-up rule to M2-FP-10 (the dialogue key light, bias 4.5 on a short-range light). Re-run the FP shots that frame faces.
- [x] **FlowRouting with two waiters** (game/flow/flow_routing.gd `when_free`). The change is only "never lost" for a single waiter. If two hand-offs wait on the same busy router, both resume on the same idle frame. The first starts a change and makes the router busy, so SceneRouter drops the second with a warning. Either queue the changes (one at a time, re-checking `is_busy` after each), or prove that no two first-playable latches can wait at once, and add a test for the case.

## Notes (m2-slice, 2026-10-24)
- **Bias.**
  - haluna.tscn no longer sets `face_key_shadow_normal_bias`, so the export's default 0 leaves the mood sun at 1.0. The export's doc now points at the key light.
  - first_verse.tscn's sun is back at 1.0.
  - Close shots key the cast with M2-FP-10's `CutsceneKeyLight` (4.5, 6 m).
  - Tests: `test_haluna_zone` and `test_fp_first_verse` assert both.
  - **No manifest shot frames an FP scene**, so there were no FP shots to re-run. The lavapipe A/B of H05 is in M2-FP-10's notes. The PC's Cutscene A check covers this too.
- **FlowRouting.**
  - `when_free` now queues waiters in call order. Only the front one changes scene, and only when the router is idle, so a second waiter sees the router busy with the first change and waits for it.
  - `reset()` is for tests whose mocked frame never fires again.
  - Test: `test_flow_routing.gd::test_two_waiters_take_turns`.
- Gates: gdlint and gdformat; Godot `--filter=flow_routing` (4), `fp_` (22) and `haluna` (8).

## Review log
