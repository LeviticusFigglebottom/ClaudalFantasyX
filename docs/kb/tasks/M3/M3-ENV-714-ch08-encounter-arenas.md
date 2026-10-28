---
id: M3-ENV-714
title: "Ch8 encounters: set their `arena` ids to M3-ENV-713's arenas"
role: cinematics
status: todo
owner_session: ""
depends_on: [M3-ENV-713]
milestone: M3
request-from: environment
reviewer: environment
---
## Goal
For act1-chapters (M3-C08-02 owns the Ch8 encounters in `game/data/battle/encounters.json`). M3-ENV-713 built the
arenas, which are in arenas.json `scenes`; no encounter names them yet.

## Acceptance criteria
- [ ] `ch08_stair_hold_1` → `seawall_stairhead_storm`
- [ ] `ch08_stair_hold_2`, `ch08_stair_hold_3` → `seawall_stairhead_hoist`
- [ ] `undertows_reach` → `seawall_stairhead_surge` (its `BossAnchor` is on the parapet behind the enemy line)
- [ ] `ch08_headland_gulls`, `ch08_headland_crabs` → `coilspire_headland_path`
- [ ] `ch08_flue_moths` → `coilspire_tier_landing`
