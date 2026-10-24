---
id: M2-FP-24
title: The Shell Shrine's channel curbs have no collision (Rhen walks through the troughs)
role: cinematics
status: todo
owner_session: ""
depends_on: [M2-ENV-03]
milestone: M2
request-from: cinematics
---
## Goal
Found in the m2-slice playthrough pass on 2026-10-24, after the M2-ENV-03 kit was swapped in. The channels are now real 1 m troughs with raised curbs, but `ShellShrineLevel`'s collision proxies cover only the hall, basins, pools and door. Rhen walks straight through the curbs and the water. The greybox had the same gap; it shows now because the curbs read as solid. In a puzzle room, the water's path is the thing to read, so walking through it undercuts tactical clarity (pillar 4).

Collision can't simply be added as-is. The player controller has no step-up, and the channels cross the room between the spring and the pool, so solid curbs would wall Rhen into pockets. Pick one:
- (a) low curb colliders with walkable crossings (stepping slabs or gaps at fixed points, data-driven in `shell_shrine.json` `room`);
- (b) a small step-up in the field controller (owned by gameplay: open a request task);
- (c) keep walk-through, but make the curbs read as flush inlays (that's an art change for M2-ENV-09).

## Acceptance criteria
- [ ] Rhen can't walk through a curb, or the curbs clearly read as walkable.
- [ ] Every basin, the side sluice and the door can be reached from the spawn in every trial state. A headless reachability test checks this over the room's collision.
- [ ] The S01–S05 shots are unchanged, or re-approved with the reason given.

## Notes

## Review log
