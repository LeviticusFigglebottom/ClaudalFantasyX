---
id: M3-AUD-1254
title: "FAST-TRACK request: the storm battle cue (battle_storm) and storm battle beds"
role: audio
status: todo
owner_session: ""
depends_on: []
milestone: M3
reviewer: narrative
request-from: cinematics
---
## Goal
The human's playtest (11-03): the storm's fights play the uplifting standard battle theme. act1-chapters wired every
storm fight to a storm cue (M3-C01-1252; music.json battle `storm_cues`). Ch1's Scuttlers play `battle_storm`, an
INTERIM row that reuses `undertow_rising` with its run pulse.

## Acceptance criteria
- [ ] A composed `battle_storm` cue (original; dread and effort, never heroic: act1_ch01.md's "a pulse added, never
      a heroic one"), replacing the interim row's files in music.json. Any later storm regular names it.
- [ ] Storm battle beds (wind, rain, the wall's roar) in ambience.json `arenas` for `oruvel_raft_storm` and the
      seawall storm arenas (`seawall_stairhead_storm`, `_hoist`, `_surge`), so the battle doesn't carry the field's
      day beds.
- [ ] Optional: confirm `hullgnaw` reads as storm music (it is in `storm_cues`).

## Review log
