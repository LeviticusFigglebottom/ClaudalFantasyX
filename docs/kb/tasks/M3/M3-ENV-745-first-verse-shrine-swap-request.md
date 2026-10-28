---
id: M3-ENV-745
title: "FAST-TRACK: Ch3's First Verse stages on CSG primitives; stage it on the final Shell Shrine (request to slice-polish)"
role: cinematics
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: environment
reviewer: environment
priority: high
---
## Goal
ADR 0041: the M2 slice is played as final. `game/levels/ch03/first_verse/first_verse.tscn` (the
`ch03_the_first_verse` cutscene, shot `slice_verse_steps`) builds the Shell Shrine from CSG primitives:
- the island, a flat cylinder;
- the dome, platform, floor and pool cut;
- the door, the two steps, the two pillars and the lintel;
- the sea, a flat PlaneMesh.

The heroes are real; everything they stand on is a primitive.

env-art's Shell Shrine is final and in the game: `game/levels/ch03/shell_shrine/shell_shrine_dressing.tscn` (the
hall, vault, roof fan, islet, steps, curved walls, the entrance and door portals, the whorl columns). Its renders
are approved (`shrine_s01_approach` … `s05`).

## Acceptance criteria
- [ ] Replace `Island`, `Shrine` (the CSGCombiner3D and its children) and `Sea` with an instance of
      `shell_shrine_dressing.tscn` and a `WaterSurface` (`lagoon_waves.tres`, `haluna_water_material.tres`), as the
      shrine's shot rig `game/levels/_tests/shell_shrine/shell_shrine_shots.tscn` mounts them; or stage the scene in
      `shell_shrine.tscn` itself.
- [ ] Re-place the marks. The real shrine is about 2.5x the stand-in, with its west entrance at x ≈ -14.2:
  - the entrance portal is at x ≈ -14.2 (the hall's west wall);
  - the hall floor's top is y 0;
  - `shrine_steps` runs down west from x -14.9 (top 0.15) to x -20.7 (-1.75).

  So, roughly:

  | Mark | Stand-in | Real shrine |
  |---|---|---|
  | `doorway` | -5.4 | ≈ -14.2 |
  | `threshold_west` | -6.2 | ≈ -15.2, on the top step |
  | `steps_rhen`, `steps_toma` | -7.2 | ≈ -17.5, y on that step's tread |
  | `asha_start` | -5.6 | ≈ -13.8, on the floor |

  Take `chamber_pool` and `ilun_chamber` from the hall's pool. `drownbell_arena`, `drownbell` and `causeway` are
  off-stage and unchanged.
- [ ] Re-render `slice_verse_steps` and view it.

## Notes
- 2026-10-28 (env-art): found by a primitive-mesh sweep of the Prologue–Ch4 scenes for ADR 0041. The other hits
  are the Prologue city (M3-ENV-739) and the player stand-in capsules in `haluna.tscn` and `shell_shrine.tscn`
  (replaced by the heroes at run time).

## Review log
