---
id: M3-ENV-737
title: "Retire the 10 greybox battle-arena scenes under game/battle/arenas/ (request to battle-presentation)"
role: combat
status: review
owner_session: claude/battle-presentation
depends_on: []
milestone: M3
request-from: environment
reviewer: environment
---
## Goal
ADR 0041 (Act I at final quality: no greybox). Every arena id in `game/data/battle/arenas.json` `scenes` now points at
env-art's final scene under `assets/environments/arenas/`. That includes `wall_head_storm`, which plays
`seawall_stairhead_hoist`.

The 10 greybox scenes in `game/battle/arenas/` are dead files:
- no scene, script or data loads them;
- the arena preview shots (`game/levels/_tests/battle_arenas/arena_*.tscn`) load encounters, so they render the final
  arenas;
- `tools/tests/test_choreo_validate.py` only uses a made-up `ghost.tscn` path.

The scenes are `ash_terrace_lanternfall`, `brine_shoals_afternoon`, `causeway_disc_sunset`, `causeway_route_afternoon`,
`derelict_deck_night`, `oruvel_raft_morning`, `salvage_camp_burning`, `tideline_dawn`, `underway_tower` and
`wall_head_storm`.

## Acceptance criteria
- [x] Delete the 10 scenes, with their scripts and resources if nothing else uses them, and drop the ownership row.
- [x] Update the `arenas.json` doc line ("the greybox scenes ... stay for their preview shots").
- [x] Godot `--filter=battle` and `test_choreo_validate` still pass.

## Notes
- 2026-10-28 (env-art): filed from the Lead's ADR 0041 brief ("the 10 game/battle/arenas scenes still reference
  greybox: those first"). The arena data side was already done at big8, M3-ENV-06 and M3-BPR-407.

## Review log
- 2026-10-28, battle-presentation: done at 0fe3ed67. The 10 scenes and `tools/arenas/gen_wall_head_storm.py` are
  removed and the ownership row dropped; the doc lines are updated. Checks: `--filter=battle` 802/0, test_choreo_validate
  and test_placeholder_audit OK. The audit's greybox-path detector stays (it still flags anything put back there).
