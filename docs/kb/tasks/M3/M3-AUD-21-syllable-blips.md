---
id: M3-AUD-21
title: Dialogue blips per syllable, resting on the reveal's comma and full-stop pauses
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
The UI track's text reveal now pauses on commas and full stops, and M2-CHR-10's lip sync moves per syllable; the blips should follow syllables, not letters.

## Acceptance criteria
- [x] VoiceAudio blips once per syllable (data-driven), silent through reveal pauses; tests.

## Notes
- 2026-10-24 audio (claude/audio): `voices.json` `pace: syllable` (new default). VoiceAudio blips on the box's
  mouth_flap opening (once per vowel group), the edge the lip sync uses; the reveal's punctuation pauses (claude/ui
  M2-UI-27 `_times`) pace it, so the blips rest with the text. Narration (without narration_blip), skipped reveals and
  sung lines stay silent; `rate_ms` still applies. `pace: letter` keeps per-letter blips. Works on claude/audio's box
  (which has the same mouth_flap) and on claude/ui's. data_check checks `pace`.
- Tests: test_voice_audio.gd (+2: one blip per vowel group, 13 for "That's a very big spear for a very small
  conversation."; silent through a pause, a skip and narration), VoicePaceTest. Godot `--filter=audio` green.

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
