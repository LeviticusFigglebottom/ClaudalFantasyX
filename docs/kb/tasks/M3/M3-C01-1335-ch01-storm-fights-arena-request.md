---
id: M3-C01-1335
title: "FAST-TRACK (the human, 11-03): point ch01_scuttlers and ch01_hullgnaw at the storm arena oruvel_raft_storm"
role: combat
status: todo
owner_session: ""
depends_on: [M3-ENV-1334]
reviewer: environment
milestone: M3
request-from: environment (env-art-b)
---
## Goal
Both Ch1 raft fights come after the lintel-gulls cry and the storm is up (`ch01.json`: gulls → set_storm → the
Rising → scuttlers → net_pen → hullgnaw), but they stand on `oruvel_raft_morning`, a clear noon. env-art-b built
`oruvel_raft_storm` (M3-ENV-1334): the same raft deck under a storm sky, rain, the Undertow at `ch01_arrival` in view.

## Ask (act1-chapters: `game/data/battle/encounters.json`)
- `ch01_scuttlers.arena` and `ch01_hullgnaw.arena` → `oruvel_raft_storm`.
- `tests/unit/test_battle_arena.gd` maps both to it.
- **Audio** (the FAST-TRACK's storm music): the arena id is `oruvel_raft_storm`; the Ch8 storm arena ids are unchanged
  (`seawall_stairhead_storm`, `_hoist`, `_surge`, `coilspire_headland_path`).

## Acceptance criteria
- [ ] Both fights load `oruvel_raft_storm`; `--filter=battle_arena` passes.

## Review log
