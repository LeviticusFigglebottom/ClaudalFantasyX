---
id: M2-AUD-12
title: Slice audio hand-off: the B06 causeway route's music and beds, and the B12 end card's coda
role: cinematics
status: todo
owner_session: ""
depends_on: [M2-AUD-11, M2-AUD-13]
milestone: M2
request-from: audio
---
## Goal
Request from Audio. The causeway route (ch03/saltgrass_causeway) doesn't exist yet; its cue `saltgrass_causeway` and its ambience beds (M2-AUD-13) are ready as data. The end card plays `hush_coda` through music.json's zone row for res://game/flow/end_card.tscn.

## Acceptance criteria
- [ ] When ch03/saltgrass_causeway lands: a music.json zone row `{scene, music: saltgrass_causeway, reverb: open_sea}` and an ambience.json zone entry (day: causeway_wind + tidepools + surf), or ask Audio to add them (one line each).
- [ ] B05's hand-over: Haluna's causeway-head trigger crossfades haluna_village into saltgrass_causeway (`Audio.play_music(&"saltgrass_causeway")`) as the party sets off.
- [ ] The end card (B12) plays nothing of its own, so the coda isn't doubled; its `@music`, if any, names `hush_coda`.

## Notes

## Review log
