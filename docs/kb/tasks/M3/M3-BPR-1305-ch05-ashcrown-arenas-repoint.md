---
id: M3-BPR-1305
title: "Request (combat): Ch5's Ashcrown fights onto their day arenas (ashcrown_forecourt_day, ashcrown_anvil_court)"
role: combat
status: review
owner_session: claude/battle-presentation
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
- [x] The five rows repointed; the boss intro viewed on the court.

## Review log
- 2026-10-28, battle-presentation: done. The four stair fights play on ashcrown_forecourt_day and the Cinder Matron on
  ashcrown_anvil_court.
  - SELF-RENDERED battle_boss_intro_matron on the court: her hero shot, the whole figure in the forge light. Viewed.
  - test_battle_arena's spot check follows; arena 18/0, boss_intro 21/0, boss_camera 6/0.
