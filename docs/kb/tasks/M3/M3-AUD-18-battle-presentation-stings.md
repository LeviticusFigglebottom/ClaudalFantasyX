---
id: M3-AUD-18
title: Stings on battle-presentation's announcements (tide-line stinger, bark, boss intro)
role: audio
status: review
reviewer: qa
owner_session: "audio (claude/audio)"
depends_on: [M2-AUD-04]
milestone: M3
request-from: battle-presentation
---
## Goal
battle-presentation (claude/battle-presentation) announces the tide-line stinger, the bark and the boss title card on
`EventBus.dialogue_event`; each should have its sting.

## Acceptance criteria
- [x] Synthesized stings for `battle_stinger`, `battle_bark` and `boss_intro` (the Drownbell its own), soft versions
  for reduced audio, PROVENANCE rows, byte-reproducible renders.
- [x] Data-driven (battle_stings.json), checked by validate_data; the boss card dips the battle music.
- [x] Tests (Godot and tools).

## Notes
- 2026-10-24 audio (claude/audio): `assets_src/sfx/battle_stings.py` → `sfx/battle/sting_{tideline,bark,boss,
  boss_soft,boss_bell,boss_bell_soft}.ogg` (−18, −22, −16, −17, −16, −17 LUFS momentary; `--determinism`
  identical). `game/audio/sting_audio.gd` (StingAudio) on the director, fed by EventBus.dialogue_event;
  `game/data/audio/battle_stings.json`; mix.json duck `boss_intro` (Music −5 dB, held 3.5 s).
- The events reach claude/audio only when claude/battle-presentation merges; until then nothing fires them (no
  pending flag needed: the signal already exists on EventBus).
- Checks: validate_data, test_audio_data (35 OK), Godot `--filter=sting` (5/0) and `--filter=audio` (74/0), gdlint,
  gdformat.

## Review log
