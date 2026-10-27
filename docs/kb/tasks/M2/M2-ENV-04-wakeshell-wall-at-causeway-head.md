---
id: M2-ENV-04
title: Place the wake-shell wall at the causeway head (B04 stages Osu there on a greybox stand-in)
role: environment
status: done
owner_session: "m2-slice (session_01DQ9tdk8Uatb8Jr6raAkXiC)"
depends_on: [M2-FP-14]
reviewer: environment
milestone: M2
request-from: cinematics
---
## Goal
Request from the m2-slice track (M2-FP-14). The beat sheet puts B04 "Pila's Granddaughter" at "the wake-shell wall at the causeway head" (vertical_slice.md §4, H08). `haluna_layout.json` places `wakeshell_wall` at (30, −196): out on the sand, 75 m past the playable zone's walk rect (z −130) and hidden from the head by the coral tide-wall. So the playable zone can't stage the scene there. M2-FP-14 staged Grandmother Osu at the causeway head, at (−15, 1.53, −121.5) facing the village, on a greybox stand-in: `NPCs/Osu/ShellWall` in `game/levels/ch02/haluna/haluna.tscn`. The stand-in is a 3.2 × 1.9 × 0.5 m box, centred at (−14.55, 1.53, −122.23) and yawed −31°. It has about 50 shells on its village face, a clean-edged gap at shoulder height (local (0.45, 1.35)), and Teyo's shell at local (−0.93, 1.10).

## Acceptance criteria
- [x] A wake-shell wall piece (the kit's `wakeshell_wall`, or a segment of it) stands at the causeway head, in reach of Rhen. Its village face is where the stand-in's is, or the stand-in's numbers are updated to match.
- [x] The gap at shoulder height and a findable "Teyo" shell exist on the piece, as named nodes or documented local positions, so H08 and H08_hand can frame them.
- [x] N-03 is reconciled (it calls the wake-shell wall the Shell Shrine's outer wall), together with the layout's far piece at (30, −196): keep both, or move it.
- [x] Once the piece lands, the m2-slice track removes the stand-in box and shells and re-aims H08 and H08_hand. The tests in `tests/integration/test_haluna_b04.gd` read the wall and the Teyo node by path.

## Notes
- The zone's collision builds a box from each kit piece's bounds, so the piece blocks Rhen like the stand-in does.

## Review log
- **2026-10-27, environment (env-art, session_01YbaV2c8yquRHqj6afQYg89): approved.**
  - **Check run:** `--filter=haluna_b04` is 8 run, 0 failed. It reads the wall and the Teyo node by path.
  - **What was checked:** the wall stands at the causeway head in Rhen's reach, the gap at shoulder height and the
    Teyo shell are named, and N-03 is reconciled. Done.
