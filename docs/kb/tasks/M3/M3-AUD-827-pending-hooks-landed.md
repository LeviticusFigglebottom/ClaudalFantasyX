---
id: M3-AUD-827
title: "Switch on the audio rows whose targets have landed (six Act I zone beds, 17 voices)"
role: audio
status: done
reviewer: qa
owner_session: "audio (claude/audio, session_01Wmj8xaLtwcqiS3qwC6PciW)"
depends_on: [M3-AUD-16, M3-AUD-07]
milestone: M3
request-from: audio
---
## Goal
The handover's step 3: a `"pending": true` row means its target isn't on claude/audio yet. Now that the targets
have landed, drop the flag, so validate_data checks the real names.

## Acceptance criteria
- [x] ambience.json: the beds of tamsule, tamsule_bell_galleries, pemakar, ashcrown, brine_shoals and corrow_night are
      live; every one of those scenes exists on this branch.
- [x] voices.json: all 17 Ch4–Ch9 speakers are live; every one is in speakers.json.
- [x] validate_data 0/0; `--filter=field_audio` 19/0, `voice` 12/0, `audio_runtime` 11/0.

## Notes
- Still pending elsewhere, by design: life.json (FieldNpc, WildlifeLayer: claude/creatures) and
  impact_audio.json (BattleImpact: claude/battle-presentation).

## Review log
- 2026-10-29 integration-qa (qa, reviewer): **accepted, done.** Every criterion is ticked, and the checks behind
  them are green on lead/gate-big17 (audio's head included): Godot `--filter=audio` 175/0; tools test_audio_data,
  test_audio_loudness and test_act1_audio_audit 50/0. `tools/audio/act1_audio_audit.py` shows 0 zones, enemies,
  skills, cutscenes and UI items; its 3 remaining items are M3-HER-1163, from a later battle-presentation change.
  This review covers the technical criteria (wired, resolved, loudness, deterministic). How the music and sound
  feel is the human's call at playtest.
