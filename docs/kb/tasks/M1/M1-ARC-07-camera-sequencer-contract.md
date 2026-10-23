---
id: M1-ARC-07
title: Camera contract fixes for the cutscene sequencer
role: architect
status: doing
owner_session: "worktree-agent-a35fbca43cd81575b"
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
- 2026-10-23 architect (sweep-D fixes):
  - **S1:** `update()` now applies the pose, then snapshots and clears the landed/owed flags, then emits `blend_finished` last, so a move issued from a handler lands on a later `update()`. Test: `test_a_cut_issued_from_a_blend_finished_await_lands_on_a_later_update` (a real `await`, after both a blend and a cut; it fails on the old code on the blend path).
  - **S2:**
    - (a) Fixed here, which ticks M1-ARC-09's first AC. Without a target, `update()` skips the volumes but evaluates, applies and emits; `aim_point`, orbit and dolly fall back to the shot's `look_at` or `progress_offset`.
    - (b) The paused-tree and `auto_update=false` driving rule is documented on `update()` and in field_camera.md.
    - (c) `_exit_tree` ends a move still in progress and emits the owed `blend_finished`; the sequencer checks `is_inside_tree()` when it resumes.
    - (d) The `is_settled()` check-before-await pattern is in field_camera.md, flagged for the sequencer review checklist.
  - **S3:** the signal doc and field_camera.md state that `snap()` emits synchronously.
  - **Nit:** dialogue_format.md has a shot-cuts / release-blends example.
  - New tests: S1, exit-tree, no-player.
- 2026-10-23 cinematics (review-sweep-E): **approve-with-fixes.** I read field_camera_director.gd in full and the a6a154c and 8f76f62 diffs. I ran `godot --headless res://tests/run_tests.tscn -- --filter=camera_director` (own `XDG_DATA_HOME`): 31 run, 0 failed. I also ran a small Godot 4.6.3 probe of await-on-`_exit_tree` semantics.
  - **Sweep-D S1 is fixed.** `update()` applies the pose, then snapshots `landed`, clears `_settle_pending` and emits last (field_camera_director.gd:287-294). A `play_shot` from a resumed `await` sets its own flag, which the next `update()` emits. The new test covers both the blend and the cut path, and checks the camera pose.
  - **S3 and the dialogue_format nit are fixed.** The signal doc (:21-33) says `snap()` emits synchronously.
  - **No-player update works.** Occupancy is skipped (:264-265). Shots evaluate, apply and land, with fallbacks in `aim_point` (:389-390), `dolly_progress` (:414-415) and the orbit centre (:362).
  - **Should-fix S1: the documented exit-tree guard does not work.** In Godot 4.6.3, a coroutine awaiting a signal emitted from `_exit_tree` resumes synchronously inside the emit, and there **`is_inside_tree()` is still true** (`is_queued_for_deletion()` is false for a plain `remove_child`). I verified this with the probe. field_camera.md:92 and the signal doc (:31-33) tell the sequencer to check `is_inside_tree()` when it resumes. That check passes, so the sequencer carries on and calls `play_shot` on a director that is leaving. If the director was only removed (not freed), the next `blend_finished` never comes, which is the hang sweep-D S2(c) set out to close. Fix: set a `_leaving` flag (exposed as `is_leaving()`) before the emit at :249-255, or emit through `call_deferred`, and document that instead. The exit-tree test (`test_leaving_the_tree_pays_an_owed_blend_finished`) should assert what the resumed coroutine sees.
  - **Should-fix S2:** `_exit_tree` releases the autosave hold (:250) but keeps `_scripted_shot`. A director re-parented mid-cutscene (`remove_child` then `add_child`) is still scripted, but nothing holds the autosave, so a chapter autosave can land mid-shot. Fix: re-take the hold in `_enter_tree` while `_scripted_shot != null`, or clear the scripted state on exit. This is shared with M1-ARC-08.
  - **Nit:** `update()` returns before the landed snapshot when `active_shot == null` (:270-271). That's safe today, because every owed flag implies an active shot, but a one-line comment would stop a later edit from dropping an owed emit.
