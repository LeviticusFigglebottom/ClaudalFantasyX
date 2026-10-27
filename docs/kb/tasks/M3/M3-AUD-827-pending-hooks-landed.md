---
id: M3-AUD-827
title: "Switch on the audio rows whose targets have landed (six Act I zone beds, 17 voices)"
role: audio
status: review
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
