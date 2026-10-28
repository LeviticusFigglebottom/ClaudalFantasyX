---
id: M3-ENV-1319
title: Every Ch5–Ch9 encounter fights on its final arena
role: environment
status: review
owner_session: "env-art-b (session_01F3vrUNt6trAMrjeYavaDNC)"
depends_on: [M3-ENV-1303, M3-ENV-1312]
milestone: M3
reviewer: battle-presentation
---
## Notes (2026-10-28, env-art-b)
- `encounters.json` arena fields: Ch5 to the Ashcrown arenas, Ch8's wall-head fights to the seawall's three states,
  and the headland and flue fights to Coilspire's two arenas (they had none). Ch6 was already final, and Ch7 and Ch9
  have no encounters. The seawall ids take `wall_head_storm`'s staging row. `test_battle_arena.gd` follows.
- Godot `--filter=battle` 757 run (the one failure was the pinned table, now updated), `battle_arena` 18/0.
  Self-rendered battle_boss_intro_matron, battle_boss_intro_reach and battle_ch08_stair_hold.

## Review log
