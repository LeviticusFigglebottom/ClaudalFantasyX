---
id: M2-AUD-07
title: The cutscene sequencer plays @music and @sfx through the Audio autoload
role: cinematics
status: todo
owner_session: ""
depends_on: [M2-AUD-02]
milestone: M2
request-from: audio
---
## Goal
Request from Audio (ADR 0031). The sequencer owns an AudioStreamPlayer for `@music` (at `music_volume_db` −8 dB,
its stand-in setting) and builds one per `@sfx`. Audio routes them by listening (Music and SFX buses; the zone bed
holds while the sequencer's music plays), but a cue that continues after the scene ends (Cutscene A's
`haluna_dawn` into the playable village) can only be handed over cleanly if the sequencer asks Audio.

## Acceptance criteria
- [ ] `_cue_music`: `Audio.play_music(track, fade)` (and `silence`), when the autoload exists; the sequencer's own
  player stays as the fallback for tests without it.
- [ ] `_cue_sfx`: `Audio.play_sfx(id, {"gain": vol})` when sfx.json has the row, else the current file lookup.
- [ ] `music_volume_db` back to 0 (final cues ship at −16 LUFS; the dialogue duck lowers the music under lines).
- [ ] `music_stand_ins` can go: music.json names every slice cue (M2-AUD-03).

## Review log
