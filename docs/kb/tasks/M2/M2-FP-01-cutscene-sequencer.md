---
id: M2-FP-01
title: Cutscene sequencer that plays .dlg cues on a CutsceneStage
role: architect
status: review
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
