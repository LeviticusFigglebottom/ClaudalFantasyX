---
id: M2-FP-11
title: Undo M2-FP-09's zone-sun shadow bias 3.0 at merge; FlowRouting with two waiters
role: architect
status: todo
owner_session: ""
depends_on: [M2-FP-09]
milestone: M2
request-from: "lead"
reviewer: rendering
---
## Goal
These are review-sweep-O's findings on M2-FP-09, whose code is on `claude/first-playable` (7015a03) and isn't merged yet. Do this in the same batch as that merge.

## Acceptance criteria
- [ ] **The zone suns go back to bias 1.0.** FP-09 criterion 5 set `face_key_shadow_normal_bias = 3.0` on haluna.tscn and `shadow_normal_bias = 3.0` on first_verse.tscn's sun. That was written before the PC measured it. M1-RND-20's follow-up (docs/kb/qa/gpu/2026-10-23-rnd-18-20-followups.md, character_shading.md "Shadows on characters") found that at Haluna's cascade, 2.5-4.5 only erases the nose shadow, that 1.0 already leaves the smile corner clean, and that **the Haluna sun stays at 1.0**. Remove the Haluna override (or set it to 0), set first_verse's sun back to 1.0, and leave the close-up rule to M2-FP-10 (the dialogue key light, bias 4.5 on a short-range light). Re-run the FP shots that frame faces.
- [ ] **FlowRouting with two waiters** (game/flow/flow_routing.gd `when_free`). The change is only "never lost" for a single waiter. If two hand-offs wait on the same busy router, both resume on the same idle frame. The first starts a change and makes the router busy, so SceneRouter drops the second with a warning. Either queue the changes (one at a time, re-checking `is_busy` after each), or prove that no two first-playable latches can wait at once, and add a test for the case.

## Review log
