---
id: M2-CHR-100
title: "Three Haluna villagers of their own: the shopkeeper, the smith and the innkeeper"
role: character
status: todo
owner_session: ""
depends_on: [M2-CHR-03]
reviewer: cinematics
milestone: M2
request-from: cinematics
---
## Goal
The human's playtest called Haluna's villagers placeholders. M2-FP-102 now gives every villager body a FieldNpc
with an M2-CHR-03 actor (`game/data/flow/haluna_villagers.json`), but the three shop NPCs in `NPCs/Town` have no
model of their own: the shopkeeper wears the netmender's, the smith the fisher's and the innkeeper the vendor's
(`stand_in_for`). In a village this small a repeated face reads as a placeholder.

## Acceptance criteria
- [ ] Shopkeeper, smith and innkeeper actors on the villager path (pipeline.md §15), each with `idle`, `talk` and
  `walk` clips like the M2-CHR-03 seven, under `assets/characters/villagers/<id>/<id>_actor.tscn`, with PROVENANCE
  rows.
- [ ] Tell cinematics (slice-polish): it swaps the three `actor` paths in haluna_villagers.json and drops
  `stand_in_for`.

## Notes
- Where they stand: the shopkeeper by the market (-35.5, 1.75, -0.6), the smith near the dock road (-12, 0.86, 50),
  the innkeeper by the inn (-30, 1.8, 58.5). Each turns to Rhen and plays `talk` during its bark.

## Review log
