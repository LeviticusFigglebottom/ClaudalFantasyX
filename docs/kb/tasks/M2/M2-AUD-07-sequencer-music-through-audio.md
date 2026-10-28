---
id: M2-AUD-07
title: The cutscene sequencer plays @music and @sfx through the Audio autoload
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-AUD-02]
reviewer: audio
milestone: M2
request-from: audio
---
## Goal
Request from Audio (ADR 0031). The sequencer owns an AudioStreamPlayer for `@music` (at `music_volume_db` −8 dB,
its stand-in setting) and builds one per `@sfx`. Audio routes them by listening (Music and SFX buses; the zone bed
holds while the sequencer's music plays), but a cue that continues after the scene ends (Cutscene A's
`haluna_dawn` into the playable village) can only be handed over cleanly if the sequencer asks Audio.

## Acceptance criteria
- [x] `_cue_music`: `Audio.play_music(track, fade)` (and `silence`), when the autoload exists; the sequencer's own
  player stays as the fallback for tests without it.
- [x] `_cue_sfx`: `Audio.play_sfx(id, {"gain": vol})` when sfx.json has the row, else the current file lookup.
- [x] `music_volume_db` back to 0 (final cues ship at −16 LUFS; the dialogue duck lowers the music under lines).
- [ ] `music_stand_ins` can go: music.json names every slice cue (M2-AUD-03).

## Done (slice-polish, 2026-10-27; game/cutscene/cutscene_sound.gd)
- **`@music <cue>`:** a music.json cue goes to `Audio.play_music(cue, fade)`; `silence` stops it when the scene
  handed it over. The sequencer's `music_by_audio` is then true and `music_track` stays "", so `_poll_hooks` doesn't
  hold the deck for its own cue. Any other cue keeps the sequencer's own player: its file, else its stand-in.
- **`@sfx`:** Audio's row (`gain` = vol; `at=` plays it from the place), else the file (M2-FP-118).
- **`music_volume_db`:** 0.
- **`music_stand_ins` stays** for the Act I cues music.json doesn't name yet: corrow_day, coilspire_flues and
  undertow_reach. Every slice cue is in music.json.
- **Checks:** cutscene 66, audio 141, fp_ 29, haluna 57, prologue 7, _thread 34, memory 6, dialogue 76, ch0 67,
  all 0 failed.

## Review log
