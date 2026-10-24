---
id: M3-AUD-13
title: Tune the placeholder voices of six speakers added after M3-AUD-07
role: audio
status: todo
owner_session: ""
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
- [ ] Each of the six gets a voice chosen for the character (blip set, pitch, rate, jitter), like the other villagers.
- [ ] `python3 tools/validate_data.py` stays 0/0.

## Notes
- Speakers: `game/data/dialogue/speakers.json`; voices: `docs/kb/tech/audio_runtime.md` "Voices".

- 2026-10-24 battle-presentation, at its big7 merge: 17 more speakers from m2-slice's Act I chapters had no row
  (`boatman`, `clerk`, `crowd`, `fenn`, `ferryman`, `ferrymaster`, `garo`, `hobb`, `inquisitor`, `ione`, `marra`,
  `poolkeeper`, `stillguard`, `tavi`, `tender`, `townsfolk`, `wright`). They got the same placeholder rows (voice_soft,
  their `blip_pitch`, the default rate, jitter and volume) and need the same tuning.

## Review log
