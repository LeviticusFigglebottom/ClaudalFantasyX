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
- 2026-10-23 cinematics (review-sweep-D): **approve-with-fixes.** I read game/world/field_camera_director.gd in full and the d85ec04, 9443786 and ebb98ab diffs. I didn't run Godot (the shared CPU); the findings below are from reading the code. tools tests: 247 OK, and dlgc and validate_data are clean. All three ACs are met:
  - `release()` cuts on the returning volume's `force_hard_cut`, even over an explicit blend, and also on the `_return_volume` fallback (field_camera_director.gd:202).
  - Every path I traced fires `blend_finished` exactly once: a cut (`_settle_pending`, :461, emitted at :255–257); a no-move `play_shot` or `release` (`_settle_in_place`, :473); a same-shot replay while it is blending in (a cut ends the blend and lands once; a blend replay lets the running blend fire); a superseded cut (`_activate` clears the pending flag); and `release()` landing on the held shot.
  - Nothing fires synchronously inside `play_shot`/`release`.
  - `@camera release` and `ease=` reach cues.json, dlgc (tools/dlgc.py check_cue reserved kwargs) and validate_data.

  Should-fix:
  - **S1: re-entrancy from an awaiting sequencer.** In `update()`, the blend-landed emit (:250) runs *before* the pose is applied to the camera (:253–254). In Godot 4, a coroutine awaiting `blend_finished` resumes inside that emit. So a sequencer's next `@camera X blend=0` → `play_shot()` runs mid-`update()` and sets `_settle_pending`. Then :255–257 emits `blend_finished(X)` in the same `update()`, before X's pose has ever been evaluated or applied. The sequencer then advances one frame early, on the old frame. That breaks "a cut lands at the end of the update() that first applies it" (field_camera.md contract), and a no-move `release()` from that listener has the same problem. Fix: apply the pose first, then snapshot `var landed := …; var owed := _settle_pending; _settle_pending = false` and emit once at the very end, so a flag set by a re-entrant call waits for the next `update()`. Add a test that awaits in a listener and cuts.
  - **S2: hang paths still open.** (a) `update()` returns early with no target (:230), so `blend_finished` never fires. This is filed as M1-ARC-09, but field_camera.md should name it as a hang condition until ARC-09 lands. (b) A paused tree, or `auto_update=false` with no driver: documented ("needs the director updating"). (c) The director freed mid-await (a zone unload during a cutscene) leaves the coroutine hanging forever. The future sequencer should race `blend_finished` against `tree_exiting`, or the contract should say so. (d) A sequencer that awaits later than the call must check `is_settled()` first (documented; keep it in the sequencer review checklist).
  - S3: `snap()` emits `blend_finished` synchronously (:134–136, through `update(0.0)` and the `was_blending` branch). That is allowed by the doc, but the signal doc comment at :21–26 lists only play_shot/release/volume change. Add "snap() emits before returning".
  - Nit: the `@camera` cue doc says a missing `blend=` is a cut, while `@camera release` without `blend=` blends. This is documented in both tables, but writers will trip on it, so add a one-line example to dialogue_format.md showing both.
