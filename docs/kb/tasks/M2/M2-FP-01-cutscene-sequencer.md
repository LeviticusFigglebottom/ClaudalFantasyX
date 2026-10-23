---
id: M2-FP-01
title: Cutscene sequencer that plays .dlg cues on a CutsceneStage
role: architect
status: done
owner_session: "session_01ELR13ohWMPrprcpcgLa7UR"
depends_on: [M1-ARC-05, M1-ARC-07]
milestone: M2
request-from: lead
---
## Goal
Play a compiled `.dlg` scene end to end in the game: camera cues through the FieldCameraDirector contract (field_camera.md), waits, actor moves to marks, look-ats, fades, letterbox, music and the dialogue box with choices. First Playable thread (lead request).

## Acceptance criteria
- [x] `CutsceneSequencer.play(scene_id, stage)` runs every cue in cues.json (placeholder presentation allowed for `@anim`, `@face`, `@vfx`).
- [x] `@camera` maps to `play_shot` / `release` exactly as field_camera.md says; `is_leaving()` / `is_instance_valid` checked after every `await blend_finished`.
- [x] Autosave held from first beat to last (`SaveSystem.hold_autosave`); the player is frozen and unfrozen.
- [x] Choices shown with a keyboard/controller menu; lines advance on `ui_accept`.
- [x] Unit tests (instant mode) for camera mapping, waits, marks, events, options, hold release, and an unload mid-move.

## Notes
- Contract for other streams: `game/cutscene/cutscene_stage.gd` (Shots/Actors/Marks folders) and the public API at the top of `cutscene_sequencer.gd`.

## Notes (handoff)
- Ready for review by **cinematics** (staging contract) and **architect** (camera contract): `docs/kb/tech/cutscenes.md`. Placeholders: `@face` recorded only, `@anim` via `CutsceneStage.clip_marks`, `@vfx` CutsceneMotes, music stand-ins in `game/data/cutscene/sequencer.json`. The field interact key (E) also advances lines.

## Review log
- 2026-10-23 architect + cinematics (review-sweep-K, fresh reviewer): **approve.** No blockers. Nits only.
  - **What I read:** the task, handoff first-playable-1, `git diff 2ddca3f^1 2ddca3f -- game/cutscene game/data/cutscene docs/kb/tech/cutscenes.md tests/unit/test_cutscene_sequencer.gd`, field_camera.md "Scripted shots", dialogue_format.md's cue table and `FieldCameraDirector.is_leaving` (field_camera_director.gd:238, 272-279).
  - **Checks:** Godot `--filter=cutscene` 11/0 failed, `--filter=fp_` 15/0 failed. `validate_data` 0/0, `dlgc --check` 0/0, tool tests 400 OK, gdlint and gdformat clean.
  - **Camera contract holds.**
    - `@camera <id>` is `play_shot(shot, blend or 0, ease)`, and `@camera release` is `release(blend or -1, ease)` (cutscene_sequencer.gd:283-296). Both match dialogue_format.md: no `blend=` means a cut, and the release blends.
    - `_land` (:301-309) uses the "check before a late await" form (`is_settled()`, then `await blend_finished`), then checks `is_instance_valid` and `is_leaving()`. The director emits on exit with `_leaving` set first, so the await never hangs. `test_director_leaving_mid_blend_ends_the_cutscene` covers it.
  - **Autosave and player hold.** The hold runs from `_begin` (:180) to `_finish` (:208) and `_exit_tree` (:111). `SaveSystem.release_autosave` is idempotent (save_system.gd:773), so a double release is safe. The player's `accepts_input` is restored on finish, on an abort and on exit.
  - **Cue schema.** Every cue in cues.json is handled. Unknown cues warn.
  - **Nits:**
    - **N1: unhandled kwargs.** `@anim ... loop=` and a target on a non-`look_at` clip (:375-377), and `@vfx form=` (:414-431), are ignored without a warning. cutscenes.md's Cue mapping table doesn't list `loop=` or `form=` as ignored. Add them to the table, or `_warn` once.
    - **N2: instant mode skips the leave check.** `_land` in instant mode (:302-304) calls `snap()` with no `is_leaving()` check after it. That's tests-only, but it means instant tests can't see an abort.
    - **N3: hosts can hang.** `_exit_tree` (:107-112) sets `_aborted`, but `play()` stays suspended on a signal that will never fire, so a host awaiting `play()` never resumes. HalunaStory keeps `busy` true (haluna_story.gd:59, 85). That's harmless while host and sequencer are freed together. Note it in cutscenes.md "Guarantees", because a reparented sequencer would strand its host.
- 2026-10-23 lead: closing on review-sweep-K approve; the should-fixes are in M2-FP-05 (FP), M1-ARC-15 (graphics settings never applied) or the PC queue (QA-05 re-run).
