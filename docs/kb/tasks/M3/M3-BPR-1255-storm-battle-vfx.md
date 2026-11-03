---
id: M3-BPR-1255
title: "FAST-TRACK request: rain and the storm sky in storm battles"
role: combat
status: todo
owner_session: ""
depends_on: [M3-ENV-1253]
milestone: M3
reviewer: rendering
request-from: cinematics
---
## Goal
The human's playtest (11-03): the storm's fights don't look like the storm. encounters.json now flags them
`storm: true` (M3-C01-1252), and arenas.json `storm` lists the storm arenas. The Lead's split: env-art-b builds the
arena scenes (M3-ENV-1253), battle-presentation the battle VFX and sky.

## Acceptance criteria
- [ ] In a `storm: true` fight the rain reads at the battle camera (the Undertow node's near-field rain follows the
      camera's distance to its eye: check it reads at the battle camera's framing), spray on the deck, and the
      vortex in frame on at least the wide and the boss intro (CameraHints `the_storm_wall` on the seawall arenas).
- [ ] Shots of `ch01_scuttlers`, `ch01_hullgnaw`, `ch08_stair_hold_1` and `undertows_reach`, viewed.

## Review log
