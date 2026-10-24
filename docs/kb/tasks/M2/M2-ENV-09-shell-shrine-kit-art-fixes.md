---
id: M2-ENV-09
title: Shell Shrine kit art fixes (fan-shell roof, coral walls, a cool interior, S01 exterior, channel bends)
role: environment
status: todo
owner_session: ""
depends_on: [M2-ENV-03]
milestone: M2
request-from: art
reviewer: rendering
---
## Goal
The Art Director adopted m2-slice's Shell Shrine kit (M2-ENV-03, `assets_src/environments/kits/haluna/shrine_interior.py`)
as the base, with fixes (M2-ENV-03 Review log, 2026-10-24). This task is those fixes. It needs the kit on the
working branch (it is on `claude/m2-slice` at f38edea until the integration branch carries it).

## Acceptance criteria
- [ ] `shrine_roof_fan` reads as tiers of overlapping ribbed stone fan-shells rising to the oculus, with white
      mortar ribs (haluna.md §3.2), not a lumpy dome: S01 viewed.
- [ ] The hall walls are coral-limestone courses (the Haluna pass-1 stone), fresher than the causeway.
- [ ] The interior is cool after the glare (`ch03_shrine_int`: shafts `#FFF1E4`, `#3FD0C9`-tinted bounce at 0.4,
      exposure 0.75): S02's shaft reads, the floor lifts about a stop, measured against the colour script.
- [ ] S01 exterior: leaf-boats on the steps and an offering shelf that read at S01's distance; sea stones and a
      wet algae band at the islet's waterline. (env-art's superseded WIP kit has `leaf_boat`, `offering_shelf`
      and `sea_stones` to salvage.)
- [ ] Channel bend and T-junction modules (salvage `channel_bend`, `channel_t` from the WIP).
- [ ] S01–S05 re-captured and viewed; drift listed with RMSE for re-approval; `verify_blender_builds` identical.

## Review log
