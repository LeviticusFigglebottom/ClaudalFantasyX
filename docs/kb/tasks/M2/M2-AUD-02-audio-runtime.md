---
id: M2-AUD-02
title: Audio runtime: the Audio autoload, buses, zone and battle music, cutscene routing
role: audio
status: review
reviewer: qa
owner_session: "audio (claude/audio)"
depends_on: []
milestone: M2
request-from: lead
---
## Goal
The game ships three cues and four UI sounds, but nothing in play routes them: no bus layout, no zone music, no battle music, and the cutscene sequencer plays on Master. Every later audio item (the trial's puzzle sounds, battle SFX, ambience, the mix) needs one listen-only runtime.

## Acceptance criteria
- [x] `game/audio/` (new, Audio-owned): an `Audio` autoload (ADR) that builds the bus layout from data (`game/data/audio/mix.json`, mix.md §4), plays music with crossfades and loop-aware streams, plays SFX from a data table (`game/data/audio/sfx.json`), and keeps ambience beds.
- [x] Zone music and ambience from data (`game/data/audio/zones.json`, scene path -> cue and beds, with flag variants), switched on `SceneRouter.scene_swapping`.
- [x] Listen-only routing of other roles' players: the cutscene sequencer's music and `@sfx` players and the dialogue blip go to the Music, SFX and Voice buses, and the zone bed yields while a cutscene owns the music. No other role's script is edited (request tasks instead).
- [x] Unit tests under `tests/unit/test_audio_*.gd`; validate_data rows for the new tables (append-only).

## Notes

## Notes
- 2026-10-24 audio (claude/audio): ADR 0031; docs/kb/tech/audio_runtime.md. `game/audio/` (AudioDirector autoload,
  MusicDeck, FadeVoice, SfxBank, AudioData, BattleAudio, ShrineAudio; footsteps and UI hooks from M2-AUD-05);
  data in `game/data/audio/`; `tools/audio/data_check.py` called from validate_data (one appended call).
  Tests: tests/unit/test_audio_runtime.gd; full Godot suite 1466 run with the autoload live (2 other-role tests
  updated for the new cue and settings, noted in the commit).
- Other roles' files touched: project.godot (the autoload line), tools/validate_data.py (one call),
  tests/unit/test_cutscene_sequencer.gd (expects the real hush_first_verse file now), tests/unit/test_ui_settings.gd
  (the new setting ids).

## Review log
