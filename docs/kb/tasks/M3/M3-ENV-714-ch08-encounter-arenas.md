---
id: M3-ENV-714
title: "Ch8 encounters: set their `arena` ids to M3-ENV-713's arenas"
role: combat
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

## Notes
- **2026-10-28 (env-art), re-routed to Combat (battle-presentation):** per the Lead (10-28 00:13), battle-presentation
  owns which arena each encounter uses. State at the integration branch:
  - All four wall-head fights still name `wall_head_storm`. Since 8be2adcd (M3-BPR-407), that id plays the final
    seawall arena in its hoist state, so they no longer show the greybox.
  - The three states differ:
    - `seawall_stairhead_storm`: no hoist yet;
    - `seawall_stairhead_hoist`: Liss's hoist rigged, as wave 2 needs (`ch08_hoist_rigged`);
    - `seawall_stairhead_surge`: the breach state, with the Reach's `BossAnchor` on the parapet.
  - All three carry `EntryMarker_ward` for the Fisher Stair. Please map each fight to its state as above.
  - The headland and flue-moth encounters don't exist in encounters.json yet. Point them at `coilspire_headland_path`
    and `coilspire_tier_landing` when they're added.
