---
id: M1-ARC-07
title: Camera contract fixes for the cutscene sequencer
role: architect
status: review
owner_session: "worktree-agent-abeb0cfc8970d95d3"
reviewer: cinematics
depends_on: [M1-ARC-05]
milestone: M1
request-from: "cinematics"
---
## Goal
Review-sweep-C (Cinematics) findings on ARC-05.

## Acceptance criteria
- [x] release() honours the volume's force_hard_cut
- [x] A cut emits blend_finished (or a documented cut_finished) so sequencers never hang on blend=0
- [x] `@camera release [blend=] [ease=]` and `ease=` on @camera added to cues.json and dlgc, with the contract documented

## Notes
From review-sweep-C (see the source tasks' Review logs for file:line).

- 2026-10-23 architect: `release()` cuts when the returning volume has `force_hard_cut`, even with an explicit blend (a shot's soft `hard_cut` is still overridden). `blend_finished` now fires once for every transition that lands (cuts at the end of the applying `update()`, no-move play_shot/release on the next `update()`), never synchronously, so `play_shot(); await blend_finished` cannot hang; `is_settled()` added. cues.json: `ease=` on @camera (set `camera_eases`, validated against field_camera.json) and `reserved.camera.release {doc, kwargs: [blend, ease]}`; dlgc limits a reserved command to its kwargs; `DialogueStep.is_camera_release()`. Contract in field_camera.md, cue table in dialogue_format.md. Tests: 6 director, 1 runner, 5 dlgc/validator. Left open (nits, not in AC): `update()` with no target, aim_node miss fallback. Handoff: docs/kb/handoffs/2026-10-23-architect-7.md.

## Review log
