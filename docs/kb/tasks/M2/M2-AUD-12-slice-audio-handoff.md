---
id: M2-AUD-12
title: Slice audio hand-off: the B06 causeway route's music and beds, and the B12 end card's coda
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-AUD-11, M2-AUD-13]
reviewer: audio
milestone: M2
request-from: audio
---
## Goal
Request from Audio. The causeway route (ch03/saltgrass_causeway) doesn't exist yet; its cue `saltgrass_causeway` and its ambience beds (M2-AUD-13) are ready as data. The end card plays `hush_coda` through music.json's zone row for res://game/flow/end_card.tscn.

## Acceptance criteria
- [x] When ch03/saltgrass_causeway lands: a music.json zone row `{scene, music: saltgrass_causeway, reverb: open_sea}` and an ambience.json zone entry (day: causeway_wind + tidepools + surf), or ask Audio to add them (one line each).
- [x] B05's hand-over: Haluna's causeway-head trigger crossfades haluna_village into saltgrass_causeway (`Audio.play_music(&"saltgrass_causeway")`) as the party sets off.
- [x] The end card (B12) plays nothing of its own, so the coda isn't doubled; its `@music`, if any, names `hush_coda`.

## Notes

## Done (slice-polish, 2026-10-27)
- **Appended rows:**
  - music.json zones: the causeway → `saltgrass_causeway`, reverb `open_sea`;
  - ambience.json zones: day = causeway_wind, tidepools and surf, with wind.
- **B05:** `ch02_low_tide`'s "Go now" ends on `@music saltgrass_causeway fade=4.0`. With M2-AUD-07 that is Audio's
  deck, so the cue rises as they set off and carries into the zone, where the zone row asks for the same cue (a
  no-op).
- **The end card** has no music of its own: its zone row plays `hush_coda`.
- **Checks:** audio 141, causeway 13, haluna 57, dialogue 76, 0 failed; validate_data clean. test_audio_loudness's
  two failures are the known audio ones.

## Review log
