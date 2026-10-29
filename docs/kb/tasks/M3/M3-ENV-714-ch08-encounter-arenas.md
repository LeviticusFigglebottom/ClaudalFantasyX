---
id: M3-ENV-714
title: "Ch8 encounters: set their `arena` ids to M3-ENV-713's arenas"
role: combat
status: review
owner_session: claude/battle-presentation
depends_on: [M3-ENV-713]
milestone: M3
request-from: environment
reviewer: environment
---
## Goal
For act1-chapters (M3-C08-02 owns the Ch8 encounters in `game/data/battle/encounters.json`). M3-ENV-713 built the
arenas, which are in arenas.json `scenes`; no encounter names them yet.

## Acceptance criteria
- [x] `ch08_stair_hold_1` → `seawall_stairhead_storm`
- [x] `ch08_stair_hold_2`, `ch08_stair_hold_3` → `seawall_stairhead_hoist`
- [x] `undertows_reach` → `seawall_stairhead_surge` (its `BossAnchor` is on the parapet behind the enemy line)
- [x] `ch08_headland_gulls`, `ch08_headland_crabs` → `coilspire_headland_path`
- [x] `ch08_flue_moths` → `coilspire_tier_landing`

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
- **2026-10-28 (env-art-b, which owns the Ch5–Ch9 arenas since the Lead's 10-28 decision), for battle-presentation
  and act1-chapters:** `ch08_headland_gulls`, `ch08_headland_crabs` and `ch08_flue_moths` now exist in
  encounters.json with no `arena`, so they fight on the sandbox's set (Act I inventory, M3-HER-1145). The ids above
  stand: the two headland fights go to `coilspire_headland_path` and the flue moths to `coilspire_tier_landing`. Both
  scenes are in arenas.json `scenes` and render final. The Ch5 repoint is M3-BPR-1305 (`ashcrown_forecourt_day` for
  the four stair fights, `ashcrown_anvil_court` for `ch05_cinder_matron`).

- **2026-10-28 (env-art-b, on the Lead's repeated ask for "the arenas for the remaining Ch5–9 encounters"): done in
  `encounters.json` (only the `arena` fields).** Ch5 stair fights to `ashcrown_forecourt_day`, `ch05_cinder_matron` to
  `ashcrown_anvil_court`, `ch08_stair_hold_1` to `seawall_stairhead_storm`, `_2`/`_3` to `seawall_stairhead_hoist`,
  `undertows_reach` to `seawall_stairhead_surge`, `ch08_headland_*` to `coilspire_headland_path`, `ch08_flue_moths` to
  `coilspire_tier_landing`. The seawall ids take `wall_head_storm`'s staging row (travel 0.85, tempo 1.0).
  `test_battle_arena.gd`'s ACT_ONE table follows (`ch08_` prefix added). battle-presentation: please review or
  re-tune; battle 757 run with only that test failing, now fixed; battle_arena 18/0.
- 2026-10-28, battle-presentation: done at 93de03c3. The headland and flue-moth fights already pointed at their
  arenas.
  - SELF-RENDERED and viewed: battle_ch08_stair_hold (storm state: crawlers and party lit), battle_boss_intro_reach
    and the Reach's fight frame (surge state: the hand grips the wall beside the party, as tuned on hoist).
  - Tests: arena 18/0, ch08_thread 6/0, set_piece 48/0, boss_camera 7/0.
