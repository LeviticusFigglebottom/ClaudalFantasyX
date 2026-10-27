---
id: M3-UI-1212
title: Area maps for Act I zones dressed with kits (the map should read the zone's kit collision file)
role: ui
status: todo
owner_session: ""
depends_on: []
milestone: M3
request-from: cinematics
---
## Goal
ADR 0200 moves the Act I zones onto env-art's kits: the greybox blocks hide (most are deleted or reduced to story
props), and the walkable shape lives in a generated `<zone>_collision.json` next to the layout (`"collision"` key in
the layout; `blocks` and `ramps` rows, same block schema). `ZoneMapShapes` (`greybox_layout`) reads only the
layout's `blocks`, so the maps of `ch04/brightwater_ferry`, `ch06/brine_shoals`, `ch08/corrow`, `ch09/corrow_night`,
`ch08/coilspire` and (next) `ch07/tamsule_bell_galleries` draw almost nothing.

Proposal: when the layout has a `collision` path, also read its `blocks` (floors by height as now; `ramps` as floors
along their from-to line). act1-chapters keeps the POIs in `zone_maps.json` on their sources (test_zone_map_pois)
and has already moved the ch04 and ch09 rows' POIs, hints and bounds onto the kit layouts.

## Acceptance criteria
- [ ] A kit zone's map shows its walkways, decks and ramps; greybox zones draw as before.

## Review log
