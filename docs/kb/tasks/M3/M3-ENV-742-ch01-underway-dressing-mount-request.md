---
id: M3-ENV-742
title: "Mount env-art's Underway dressing in ch01/oruvel_underway.tscn (request to slice-polish)"
role: cinematics
status: todo
owner_session: ""
depends_on: [M3-ENV-741]
milestone: M3
request-from: environment
reviewer: environment
priority: high
---
## Goal
ADR 0041: no greybox in Act I. `game/levels/ch01/oruvel_underway/oruvel_underway.tscn` still shows its 36 greybox
blocks. env-art's dressing is ready (M3-ENV-741).

## Acceptance criteria
- [ ] Add a `Dressing` child (`game/levels/act1/zone_kit_dressing.gd`) with
      `layout_path = "res://assets/environments/zones/ch01/oruvel_underway_dressing.json"`. The preview
      `game/levels/_tests/oruvel_underway_zone_dressing/oruvel_underway_dressed.tscn` is the reference.
- [ ] Optional, for the final look: the kit preview's UnderwaterRig and `ch01` Environment
      (`game/levels/_tests/oruvel_underway_kit/`) in place of the layout's stand-in sun, ambient and fog
      (underway_zone.gd's header says the kit brings them).
- [ ] Re-render the zone's shots and view them.

## Review log
