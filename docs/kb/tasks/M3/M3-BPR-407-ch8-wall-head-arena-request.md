---
id: M3-BPR-407
title: "Ch8 battle arena: the wall-head and the Fisher Stair in the storm, with a stair entry marker"
role: env-art
status: todo
owner_session: ""
depends_on: [M3-BPR-406]
milestone: M3
request-from: combat
---
## Goal
Ch8's four set-piece battles (ch08_stair_hold_1..3 and undertows_reach; ADR 0100) have no arena, so they play on the
sandbox. act1_ch08.md describes the place:
- the wall-head arena (B16): the parapet, with the stair going down to the low town;
- storm-dark grading;
- everything off the Reach `spawn_wound` cyan, sideways and down;
- Virel's Flare Line as the one warm frame.

Battle-presentation (M3-BPR-406) needs:
- **An `EntryMarker_ward` node:** a Marker3D at the head of the stair, on the party's side, where the Climb "is".
  The coverer (Toma's Hold the Stair) steps to it to take an intercepted grip, and the camera frames the stair there
  on the Climb's turns.
- **Room for the Reach:** per §5, its limb fills the frame's right side, with 2 small enemy slots beside it.
- **The usual arena contract** (docs/kb/tech/battle_presentation.md, Arenas): slot markers, fog-safe lamps, staging.

Battle-presentation will map the four encounters to a greybox `wall_head_storm` id in the meantime, as with
M3-BPR-01. Reply in your live log, or take the id when the final kit lands.

## Acceptance criteria
- [ ] Arena scene with the slot markers and EntryMarker_ward; PROVENANCE rows; viewed render.
- [ ] battle_arena_wall_head shot (requested via the PC render protocol).

## Review log
