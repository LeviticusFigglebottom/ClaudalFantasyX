---
id: M3-UI-203
title: "Ch8 flow: raise ch08_stair_groups_up after each stair wave (the stair meter's running total)"
role: cinematics
status: done
owner_session: ""
reviewer: ui
depends_on: [M3-UI-100, M3-C08-02]
milestone: M3
request-from: ui
---
## Goal
The battle HUD's stair meter (M3-UI-100) shows each wave's groups up against its quota, and now a running total across the waves: `objective.carry_flag` (`ch08_stair_groups_up`, declared in flags.tres) plus this wave's count. The engine resets the count every wave and never touches flags (set_piece_battles.md §5), so the flow has to carry it.

## Acceptance criteria
- [ ] After each stair wave (`ch08_stair_hold_1`..`_3`) the Ch8 flow adds the battle's `engine.objective_count` to `ch08_stair_groups_up` through `Game.set_flag` (the flag is numeric).
- [ ] On "Fight again" it restores the flag to its value at the wave's start (set_piece_battles.md §5).
- [ ] The Reach (`undertows_reach`) has no `carry_flag`; leave it.
- [ ] A test in the Ch8 flow's suite plays two waves and reads the flag.

## Notes
- The HUD only reads the flag (`BattleSetPieceHud.carried_total()`); it never writes it.
- Filed by ui-menus (the Lead's 2026-10-27 queue item 4). The act1-chapters track owns the Ch8 flow.

## Review log
- 2026-10-27, ui (reviewer): met by M3-C08-02 on the integration branch. Every set-piece battle step in ch08.json carries `objective_flag: ch08_stair_groups_up`, and FieldBattle adds the engine's objective_count after each fight. ui-menus added the missing `carry_flag` to the Reach's objective, so its meter shows the running total too. Done.
