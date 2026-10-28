---
id: M3-ENV-713
title: "Ch8's battle arenas: the wall-head at the Fisher Stair (storm, hoist, surge), the headland path, a Coilspire tier"
role: environment
status: review
owner_session: "env-art (session_01YbaV2c8yquRHqj6afQYg89)"
depends_on: [M3-ENV-04, M3-ENV-04B, M3-ENV-10, M3-CMB-01, M3-C08-02]
milestone: M3
reviewer: battle-presentation
---
## Goal
Every Ch8 encounter (the set-piece's three waves, the Undertow's Reach, the headland's two fights, Coilspire's flue
moths) had no arena and fought on the battle sandbox's greybox: the last "missing Act I arenas" of the Lead's queue.

## Acceptance criteria
- [x] `seawall_stairhead_storm`, `_hoist`, `_surge` (Corrow kit, re-based from the kit preview): the walk at y 0,
      the Watchers behind the enemy line, the stair to the party's right, Liss's hoist from wave 2, `BossAnchor` for
      the Reach in the surge.
- [x] `coilspire_headland_path`: the Coilspire kit's `arena_headland_ground` / `arena_headland_path` (`cs_arena.py`):
      a levelled, flagged landing at the path's mid-point, the spire 55 m back-left.
- [x] `coilspire_tier_landing`: the Coilspire kit's `arena_tier_hall`, a tier of the well as a cut-away set.
- [x] arenas.json scenes; `test_battle_arenas` (floor and camera line) 10/0 with all five; `test_arenas`,
      `test_fog_lamps`, `test_coilspire_kit` OK; Coilspire full rebuild (older pieces identical); validate_data.
- [x] Preview fixtures and shots `battle_arena_<id>` for the PC.
- [ ] encounters.json `arena` ids (request M3-ENV-714 to act1-chapters).
- [ ] PC renders viewed and approved.

## Notes
Docs: `docs/kb/tech/battle_arenas.md` (three new sections).

## Review log
