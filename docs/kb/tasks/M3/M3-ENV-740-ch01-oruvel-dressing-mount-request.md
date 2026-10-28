---
id: M3-ENV-740
title: "Mount env-art's Oruvel dressing in ch01/oruvel.tscn (request to slice-polish)"
role: cinematics
status: todo
owner_session: ""
depends_on: [M3-ENV-738]
milestone: M3
request-from: environment
reviewer: environment
priority: high
---
## Goal
ADR 0041: no greybox in Act I. `game/levels/ch01/oruvel/oruvel.tscn` still shows its 27 greybox blocks. env-art's
dressing is ready (M3-ENV-738).

## Acceptance criteria
- [ ] Add a `Dressing` child (`game/levels/act1/zone_kit_dressing.gd`) with
      `layout_path = "res://assets/environments/zones/ch01/oruvel_dressing.json"`, as
      `game/levels/ch04/brightwater_ferry/brightwater_ferry.tscn` has it. The preview
      `game/levels/_tests/oruvel_zone_dressing/oruvel_dressed.tscn` is the reference.
- [ ] A `WaterSurface` at y -0.8 (the raft decks' draught) and the `Tide` weathering node, as the preview has them.
- [ ] Check the *Seventh Terrace* deck: the `SeventhTerrace` greybox block's top is 1.5 m, the ferry's walkable deck
      0.25 m. Either drop the block's top to the deck or keep the party off its edge.
- [ ] Re-render the zone's shots and view them.

## Review log
