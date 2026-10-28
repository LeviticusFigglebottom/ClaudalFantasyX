---
id: M2-FP-24
title: The Shell Shrine's channel curbs have no collision (Rhen walks through the troughs)
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M2-ENV-03]
reviewer: lead
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
- [x] Rhen can't walk through a curb, or the curbs clearly read as walkable.
- [x] Every basin, the side sluice and the door can be reached from the spawn in every trial state. A headless reachability test checks this over the room's collision.
- [x] The S01–S05 shots are unchanged, or re-approved with the reason given.

## Notes
- **Done (slice-polish, 2026-10-27), option (a).**
  - `ShrineChannelCurbs` puts a static box the trough's width and height (0.7 × 0.3 m) along each trough, with a
    1.2 m crossing left open at its middle. Shared troughs get theirs once; troughs too short get none.
  - Data is in `game/data/trials/shell_shrine_curbs.json`. It is kept out of shell_shrine.json because that file
    feeds the GI bake's staleness digest.
- **test_shrine_reachability** floods the room's real static collision with Rhen's capsule, overlap done by hand
  (the runner never steps physics, so the space has no broadphase).
  - A capsule can't stand on a curb.
  - From the Entry spawn, the four basins and the charm are in reach with the door shut and open. The exit is in
    reach only once the door sinks.
  - Even with no crossings, nothing is walled off: the troughs never enclose a region. The crossings are a
    shortcut, not a necessity.
- **The shots are unchanged:** colliders draw nothing.
- **The GI digest covers shell_shrine_level.gd,** so the three-line hook makes the bake read stale. Curbs are
  collision only and VoxelGI bakes meshes, so the light can't change, but the PC rebakes rather than anyone
  rewriting the sidecar by hand. RENDER-REQUEST `gi_bake:shell_shrine` is in the slice-polish live log.

## Review log
