---
id: M3-UI-1212
title: Area maps for Act I zones dressed with kits (the map should read the zone's kit collision file)
role: ui
status: review
owner_session: "ui-menus (claude/ui, session_01KGBUwbYgXe9JS6D8jXw6ZG)"
reviewer: cinematics
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
- **2026-10-27, ui-menus: done.**
  - ZoneMapShapes (`greybox_layout`) also reads the layout's `collision_path` file (50182f0e): its blocks are classified as before, and each ramp is drawn as a pad along its from-to run, `width` wide.
  - A shape hint ending in `*` now names a kit's numbered pieces.
  - The walkways, wall-walks and platforms that stand above the map's floor height are hinted as floors and their rails as structures, so nothing reads as a building by height alone:
    - ch08/corrow and ch08/coilspire (with their POIs and bounds moved to the kit frame);
    - ch07/tamsule_bell_galleries;
    - ch09/corrow_night.
  - ch04/brightwater_ferry already reads well (42 deck floors).
  - tools/tests/test_zone_map_pois.py checks the hints against layout and collision blocks; zone_map 21/0.
  - A greybox-only zone draws as before.
  - Note: the layout key is `collision_path` (not `collision`).

## Review log
