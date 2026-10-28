---
id: M3-BPR-1305
title: "Request (combat): Ch5's Ashcrown fights onto their day arenas (ashcrown_forecourt_day, ashcrown_anvil_court)"
role: combat
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: environment
---
## Goal
Every Ch5 encounter plays on `ash_terrace_lanternfall` (Pemakar's terrace at night), but the stair fights are on
Ashcrown's pilgrim stair by day (act1_ch05.md B07) and the Cinder Matron is in Ashcrown's anvil court (B09, 13:40).
env-art-b built both arenas from the Ashcrown kit (`assets_src/environments/kits/ashcrown/b_arenas.py`; ids in
`arenas.json` `scenes`, previews and shots `battle_arena_ashcrown_forecourt_day`, `battle_arena_ashcrown_anvil_court`,
in `test_battle_arenas`). The anvil court has a `BossAnchor` on enemy slot 0.

Ask (encounters.json is battle-presentation's):
- `ch05_stair_tortoises`, `ch05_stair_ashwings`, `ch05_stair_tortoise_sparker`, `ch05_stair_tortoise_ashwing` →
  `"arena": "ashcrown_forecourt_day"`;
- `ch05_cinder_matron` → `"arena": "ashcrown_anvil_court"`, and re-render the Matron's intro and phase shots.

## Acceptance criteria
- [ ] The five rows repointed; the boss intro viewed on the court.

## Review log
