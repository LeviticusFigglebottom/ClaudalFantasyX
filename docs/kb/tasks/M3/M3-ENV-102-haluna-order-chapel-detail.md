---
id: M3-ENV-102
title: "Request (slice-polish): Haluna's Order chapel reads as a plain white box (H07, the chapel court)"
role: environment
status: review
owner_session: "session_01YbaV2c8yquRHqj6afQYg89 (env-art)"
depends_on: []
milestone: M3
request-from: cinematics
reviewer: cinematics
---
## Goal
ADR 0041 beat audit (self-rendered `haluna_h07_chapel_court`, lavapipe): the court itself is lovely, with the
banyan, its hanging roots, the dappled shade and the offering pot. Against it, `order_chapel` (the layout piece at
(-118, 27.5)) is a flat white cube: plain walls, two slot windows, a red door, a parapet lip, and a small gilt dome
that barely shows. Every Haluna house around it has trim, roof tiles and texture, so the Order's one building reads
as unfinished. H03 and the chapel's villager (B03, "Cantor" in four pieces) frame it.

## Acceptance criteria
- [x] The chapel at the kit's level, as the Order's own building (bible: Stillguard and the Order). Ideas:
      - plaster with weathering and a lime-wash streak, a stepped base;
      - a carved lintel and a bell-cote or a lamp niche over the door;
      - the gilt dome readable from H07's camera.
- [x] Same footprint and door position (the chapel's Interactable and HalunaCollision's box still fit).

- 2026-10-28 (env-art): `order_chapel` (shrine.py), same footprint and door position.
  - A bare coral-stone base course under the marble plinth, as a stepped base.
  - The whitewash weathered: salt and damp low on the walls, the lime-wash streaked.
  - An arched lamp niche over the lintel, with the Level emblem in gold.
  - A bell-cote on the front parapet: two marble piers under an arch, a gilt bell on its yoke.
  - The gilt dome is 1.25x larger, on a taller drum (1.35 m), so it clears the parapet.
  - 6,064 tris (budget 9,000).
  - SELF-RENDERED `haluna_h07_chapel_court`: the bell-cote and the gilt dome read from the court, and the niche shows
    over the red door. An intended drift; re-approve.

## Review log
