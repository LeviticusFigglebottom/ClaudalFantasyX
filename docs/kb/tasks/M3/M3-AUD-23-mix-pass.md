---
id: M3-AUD-23
title: Mix pass across the M3 SFX and music: loudness per bus
role: audio
status: review
reviewer: qa
owner_session: "audio (claude/audio)"
depends_on: [M2-AUD-02]
milestone: M3
request-from: lead
---
## Goal
Many new sets landed (choreography, creatures, menus, stings, beds, Act I cues); check them against each other per bus.

## Acceptance criteria
- [x] Measured per-bus report in mix.md; any outlier fixed at its source and re-rendered; the loudness test green.

## Notes
- 2026-10-24 audio (claude/audio): `tools/audio/mix_report.py` → `docs/kb/audio/mix_report.md` (effective level per
  set and bus, plus blip streams at both paces). Write-up and plan-vs-measured table in mix.md §8. Every set was
  already on plan within its bus, except the dialogue blip stream (−29.3 short-term, 13 LU under the music): now
  voices.json `mix_db` +6, giving −23.3 (VoiceAudio adds it; data_check range-checks it; test_voice_audio covers it).
- Re-run after M2-AUD-14, M3-AUD-19 and M3-AUD-20 merged: the four new cues are at −16.0 to −16.1, the seven page
  sounds at −20.0 to −20.4 (`ui_map_pan` plays at −26 by its row's −6 dB, a quiet repeat by design). No change needed.

## Review log
