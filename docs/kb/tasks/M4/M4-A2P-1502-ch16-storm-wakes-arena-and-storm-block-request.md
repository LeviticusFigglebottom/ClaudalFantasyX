---
id: M4-A2P-1502
title: "Ch16 B09: point ch16_storm_wakes at drowned_choir_storm, and give the Choir zone a Storm block for the waking"
role: combat
status: todo
owner_session: ""
depends_on: []
reviewer: environment
milestone: M4
request-from: environment (env-art-b)
---
## Goal
In B09 the storm wakes early over the Drowned Choir. The fight `ch16_storm_wakes` stands on the moonlit
`drowned_choir_ring`, and the zone has nothing for the storm to follow.

env-art-b built `drowned_choir_storm` (tools/act1/storm_arenas.py, the same storm looks as the human's 11-03 FAST-TRACK). It has the ring under a waking-storm sky, rain on the battle camera, a soaked dais, a storm rim and the Undertow over the ring.

## Ask (act1-chapters)
- `encounters.json`: `ch16_storm_wakes.arena` → `drowned_choir_storm`.
- `tools/act2/ch15_16_greybox.py`, the Choir's layout: a non-solid, hidden marker block `Storm` far out to the north (for example (0, 0, −9000)), shown by a `variants` row when `ch16_guard_beaten` is set.
  - Then env-art-b adds the dressing's `storms` row following it (preset `ch08_landfall`, with `StormFarPlane`) and the storm grade, as Ch8's Corrow has.

## Acceptance criteria
- [ ] The fight loads `drowned_choir_storm`; `--filter=battle_arena` passes.
- [ ] The `Storm` block and its variants row are in the Choir's layout; env-art-b is told.

## Review log
- env-art-b (11-03, after merging big47): the first ask is already met. `ch16_storm_wakes` names `drowned_choir_storm`, whose scenes row is now the built arena (the storm table's `pending` is cleared). Only the zone's `Storm` block remains.
