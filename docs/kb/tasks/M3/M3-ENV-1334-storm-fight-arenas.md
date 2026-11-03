---
id: M3-ENV-1334
title: "FAST-TRACK (the human, 11-03): the storm fights get storm arenas (a dark storm sky, rain, wet ground, storm light, the Undertow in view)"
role: environment
status: review
owner_session: "env-art-b (claude/env-art-b)"
depends_on: []
reviewer: rendering
milestone: M3
---
## Goal
The human's playtest, 11-03: "the seagull/storm scene doesn't show the actual vortex, and its fights use the normal
backdrop". The lintel-gulls (Ch1 C1-11) are followed by the Rising and two fights, the Scuttlers and the Hullgnaw,
which stood on `oruvel_raft_morning` (a clear noon). Ch8's storm fights stood under a warm low sun with a sun disc.

## Done (tools/act1/storm_arenas.py holds the looks and additions)
- **`oruvel_raft_storm` (new):** env-art's raft table under the `ch01_rising` look, the Undertow (`ch01_arrival`)
  down the battle camera's view, rain 0.35, the deck soaked. For act1-chapters to point `ch01_scuttlers` and
  `ch01_hullgnaw` at (M3-C01-1335).
- **`seawall_stairhead_storm`, `_hoist` (the stair holds, `ch08_storm`) and `_surge` (the Reach, `ch08_reach`), in place.**
- **`coilspire_headland_path` (`ch08_brewing`):** overcast, the first rain, the Undertow at `ch08_seawall`.
- **Wet surfaces:** ArenaRainWet (`game/levels/act1/arena_rain_wet.gd`) gives the arena its own wet copies of its
  materials: the weathering shader's new `rain_wet` uniform (default 0, so nothing else changes), or a darker, glossier
  StandardMaterial3D.
- **Storm light:** a cool key from behind the battle camera, a shadowless rim from the storm's bearing (`StormRim`),
  and the ambient lifted so the party reads.

## Acceptance criteria
- [x] Each storm fight's arena shows a storm sky, rain and the Undertow from the battle camera (self-rendered, viewed).
- [ ] The Ch1 encounters use `oruvel_raft_storm` (act1-chapters, M3-C01-1335).
- [ ] The PC's GPU view of the four arenas.

## Review log
