---
id: M3-CHR-591
title: "Request (creatures track): Haluna's shopkeeper, smith and innkeeper wear their own models (ch02_haluna.json `actor`)"
role: character
status: todo
owner_session: ""
depends_on: [M3-CHR-512, M3-CHR-516, M3-CHR-517]
milestone: M3
request-from: character
reviewer: character
---
## Goal
`game/data/world/npc/zones/ch02_haluna.json` (VillagerLayer, the creatures track's) still dresses Haluna's town trio in
other villagers' bodies "until M2-CHR-100": the shopkeeper as `netmender`, the smith as `fisher`, the innkeeper as
`vendor`. Their own models are built (M3-CHR-512, 516, 517): `assets/characters/villagers/{shopkeeper,smith,innkeeper}/`
with `<id>_actor.tscn` and clip libraries (`idle`, `talk`, and `offer_goods`, `hammer_strike`, `welcome_bow`).

## Acceptance criteria
- [ ] Each row's `actor` names its own model (or the key is dropped if the layer defaults to `npc_id`), and its `_note`
      is updated.
- [ ] The Haluna zone's tests still pass; the town trio idles in its own body in a Haluna capture.

## Notes
- Filed 2026-10-29 by the characters track (the named-NPC cast pass, M3-CHR-519). Not ours to edit: VillagerLayer's
  data is the creatures track's (CONSOLIDATED: villagers -> creatures).

## Review log
