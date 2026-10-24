---
id: M2-UI-18
title: A zone map in the field menu (Haluna, the causeway, the Shell Shrine)
role: ui
status: doing
owner_session: "claude/ui"
depends_on: [M2-UI-16]
milestone: M2
request-from: lead
---
## Goal
A map page in the field menu: a schematic of the current zone drawn from data, the player's position and facing, the objective's destination, and points of interest, plus a route strip (Haluna, the Saltgrass Causeway, the Shell Shrine) showing where the party is on the pilgrimage. Original style from palette.json and the theme; no copied UI.

## Acceptance criteria
- [ ] `game/data/ui/zone_maps.json`: per zone, its scene, world bounds and POIs (`at` in world x/z, loc label, kind); Haluna's shapes come from its layout JSON (shore, lanes, houses, pads), so the map follows the town as Environment changes it.
- [ ] A tools test checks each POI's `at` against the node it names in the zone's .tscn.
- [ ] The Map row in the field menu opens it; the player marker, the objective marker (a distinct shape) and POI glyphs by kind; a legend; keyboard, pad and mouse.
- [ ] Tests and shots.

## Review log
