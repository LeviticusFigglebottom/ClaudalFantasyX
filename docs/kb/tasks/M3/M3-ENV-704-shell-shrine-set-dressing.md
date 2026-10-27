---
id: M3-ENV-704
title: "Shell Shrine set dressing: place the M3-ENV-701 pieces at the islet and in the hall, then rebake the GI"
role: architect
status: doing
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M3-ENV-701]
milestone: M3
request-from: environment
reviewer: environment
---
## Goal
For slice-polish (`claude/m2-slice`), which owns `game/levels/ch03/shell_shrine/**` and its baked VoxelGI.

The human's playtest said parts of the slice look primitive. In the Shell Shrine (S01–S05) the islet is bare
sand and stepping stones, and the hall has the puzzle and nothing else: no sign anyone has tended it. The Haluna
kit now has the pieces (M3-ENV-701, all in `assets/environments/kits/haluna/`, origins on the ground, front +Z).

## Acceptance criteria
- [ ] **The islet (S01):** an `offering_step` either side of the west steps' foot, facing out to the causeway;
      two `tide_debris` and a `net_heap` on the islet's sand clear of the stepping stones; a `rope_coil` by the
      steps. Keep the S01 frame's read of the door and the steps.
- [ ] **The hall (S02, S03):** an `offering_step` against the wall between each pair of whorl columns on the two
      10 m runs (four in all, on `z = ±8.3`, set back to the wall foot, facing into the hall), clear of the
      channels, basins, pools and grates. Optionally a `shrine_offering` (with its tide-post) either side of the
      entrance inside, if S02's threshold frame takes it.
- [ ] Collision: `none` for `rope_coil`, `tide_debris`, `net_heap`; boxes for the offerings are fine.
- [ ] Rebake the two GI states (`tools/shrine/bake_shrine_gi.tscn`, `tools/shrine/gi_inputs.py --write`) and
      re-approve S01–S05 after viewing them.

## Notes (env-art, 2026-10-27)
- If the shrine would rather take one instanced sub-scene than nodes in `shell_shrine_dressing.tscn`, ask in the
  env-art live log and env-art will build it under `assets/environments/kits/haluna/` from the trial JSON's
  `room` metrics.
