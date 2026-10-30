---
id: M3-AUD-24
title: Tune the placeholder voices of six speakers added after M3-AUD-07
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio)"
depends_on: [M3-AUD-07]
milestone: M3
request-from: lead
---
## Goal
`validate_data` requires a `game/data/audio/voices.json` row for every `speakers.json` speaker. m2-slice added
`cook`, `kell`, `osu`, `sabe`, `scaleman` and `skipper_sadi` after claude/audio wrote voices.json, so the big7 merge
failed that check. The Lead's merge added placeholder rows so the gate passes: `voice_soft`, the speaker's
`speakers.json` `blip_pitch` as `pitch`, and the default rate, jitter and volume.

## Acceptance criteria
- [x] Each of the six gets a voice chosen for the character (blip set, pitch, rate, jitter), like the other villagers.
- [x] `python3 tools/validate_data.py` stays 0/0.

## Notes
- 2026-10-24 audio (claude/audio): renumbered from M3-AUD-13 (the id was already claude/audio's battle choreography
  SFX). Voices from the story docs, using the villagers' blip sets:
  - osu, who washes the shells on the wall for tonight: voice_breathy 0.90, 75 ms (quiet, slow);
  - kell, Oruvel's gruff, warm chandler: voice_low 1.15, 70 ms;
  - scaleman, a brisk market weigher: voice_low 0.95, 60 ms;
  - cook, chatty, feeds Rhen on credit: voice_bright 0.90, 55 ms, jitter 0.08;
  - sabe, Ione Sabe, a terse grieving captain: voice_low 1.05, 80 ms, jitter 0.03;
  - skipper_sadi, Sadi Moru, an amiable haggler: voice_bright 1.00, 55 ms.
  validate_data 0/0; test_voice_audio covers every speaker.
- 2026-10-24: the menus track flagged claude/m2-slice's Ch4–Ch9 cast (17 speakers with no voice). They are added as
  `"pending": true` rows: tavi (child), ione (= sabe), poolkeeper, boatman, crowd, garo (the Pemakar smith), tender,
  ferryman, townsfolk, ferrymaster, marra, hobb (the watch captain), fenn (old beacon keeper), stillguard and
  inquisitor (the Order: low, slow, almost no jitter), clerk and wright. data_check skips the speaker-exists check for
  a pending row (VoicePendingTest). With m2-slice's speakers.json swapped in, validate_data reports no voice errors.
  Drop the flags when m2-slice merges.
- Speakers: `game/data/dialogue/speakers.json`; voices: `docs/kb/tech/audio_runtime.md` "Voices".

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
