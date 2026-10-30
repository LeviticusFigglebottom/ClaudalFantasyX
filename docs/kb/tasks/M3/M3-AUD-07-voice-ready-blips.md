---
id: M3-AUD-07
title: Voice-ready dialogue audio: the per-speaker blip system as data, with tests
role: audio
status: done
owner_session: "audio (claude/audio; worktree agents for M2-AUD-10, M3-AUD-02, -04, -06, -07)"
reviewer: qa
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
SPEC §16 Q4 default: no voice acting yet, but the architecture must be ready. Today one blip file is pitched per speaker (speakers.json).

## Acceptance criteria
- [x] A per-speaker voice table (blip set, pitch, rate, timbre; a future `vo` path per line id), read by an Audio-side listener on DialogueBox (listen-only; request tasks for any DialogueBox change).
- [x] A per-speaker blip set synthesized (a few timbres), PROVENANCE, tests; a documented path to real VO (line id -> file, falls back to blips).

## Notes
- **Table:** `game/data/audio/voices.json`: a voice for each of the 14 speakers.json ids (blip set of sfx rows,
  pitch, `rate_ms` 55-80, seeded `jitter`, `volume_db` on top of text_box.json's `blip_volume_db`), a `default` for an
  unknown id, and `vo` (`res://assets/audio/vo/{speaker}/{line_id}.ogg`, Voice bus, `suppress_blips`).
- **Timbres:** `assets_src/sfx/voice_blips.py` -> `assets/audio/sfx/voice/blip_{soft,bright,low,breathy,child}_{1..3}.ogg`
  (formant murmurs, three vowels each, -27 LUFS momentary like text_blip; byte-identical on re-render). Rows in
  `game/data/audio/sfx_voice.json` (Voice bus), targets rule `sfx/voice/blip_*.ogg`, a render_all.py job,
  PROVENANCE rows.
- **Runtime:** `game/audio/voice_audio.gd` (VoiceAudio), one per DialogueBox, listen-only. It reads the box's
  public `blips_played` once a frame and plays the voice's blip (one per frame at most, none closer than rate_ms),
  keeps the box's `Blip` player at -80 dB (routing only; dialogue_box.gd is untouched), takes the voice from
  `CutsceneSequencer.line_shown(step)` (speaker, else narrator identity) and falls back to `mouth_flap(speaker)`.
  VO: the step's `voice` field, else the pattern; when the file exists it plays on Voice and the line's blips are
  dropped; a missing file falls back to blips; the next line or a closed box stops it.
- **Request task:** M3-ARC-03 (architect; filed as M3-ARC-01): a `blip(voice)` signal, a `line_started(step)` signal and a switch to
  leave the box's own player out, so the poll and the muting can go.
- **Tests:** `tests/unit/test_voice_audio.gd` (9: speaker coverage vs speakers.json with rows on Voice and files
  present, default fallback, blips per box blip with pitch/level/cycle and the box muted, rate limit and one per
  frame, voice from line then flaps, VO preference with a fixture AudioStreamWAV and fallback, VO paths, VO stop on
  close, the director's per-box listener hearing a real sequencer). `tools/audio/data_check.py` `voice_errors`
  + 2 tests in `tools/tests/test_audio_data.py`.
- Docs: audio_runtime.md "Voices", mix.md §7 "Voices".

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
