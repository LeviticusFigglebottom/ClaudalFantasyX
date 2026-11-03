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

## Notes
- act1-chapters' lavapipe stills (11-03, @ ce4bcb6d): `battle_ch08_stair_hold`, `battle_arena_seawall_stairhead_storm`
  and `_hoist` show the storm clouds and faint rain, but **not the wall itself**: the frame is the parapet over a calm,
  bright sea (the Undertow's azimuth 345 deg is in front, so it is distance, size or the camera's pitch).
  `_surge` (the Reach) reads: rain, dark sky, the hand. `battle_arena_oruvel_raft_morning` is the sunny raft (the
  interim for `oruvel_raft_storm`).

## Review log
