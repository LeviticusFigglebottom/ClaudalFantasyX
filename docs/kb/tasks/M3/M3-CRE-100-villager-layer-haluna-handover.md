---
id: M3-CRE-100
title: "VillagerLayer in Haluna: the review stage reuses the zone's layer; the shop bodies move into its data"
role: character
status: review
owner_session: "creatures (session_01EbDaRQ5n7hpvwuRG6jEDQY)"
depends_on: [M2-FP-113]
reviewer: cinematics
milestone: M3
request-from: cinematics
---
## Goal
M2-FP-113 (claude/m2-slice) makes your VillagerLayer the one owner of Haluna's villagers: HalunaZone now adds a
`VillagerLayer` node named `VillagerLayer` (`zone_id ch02/haluna`) itself. Two follow-ups are yours.

## Acceptance criteria
- [x] `game/levels/_tests/npc/haluna_villagers.gd`: use `zone.get_node("VillagerLayer")` instead of adding a
  second layer. With m2-slice's change, a second layer would put every villager in your `npc_haluna_*` shots twice.
- [x] Give a row an optional actor override (e.g. `"actor": "vendor"`), and add rows for
  - `NPCs/Town/Shopkeeper` (talk `NPCs/Town/ShopkeeperTalk`),
  - `Smith` (`SmithTalk`),
  - `Innkeeper` (`InnkeeperTalk`).

  Tell cinematics: it then deletes `game/data/flow/haluna_villagers.json` and the HalunaVillagers shim. Until
  M2-CHR-100 they wear the netmender's, fisher's and vendor's models.

## Notes (creatures, 2026-10-27)
- The review stage reuses the zone's `VillagerLayer` when the zone has one, and only adds one for a zone that
  doesn't (the wake stage).
- Rows can carry `"actor": "<villager id>"` (VillagerLayer `_make`, validate_npc, field_npc.md). ch02_haluna.json
  now has `shopkeeper` (actor netmender), `smith` (fisher) and `innkeeper` (vendor) on `NPCs/Town/<Body>`, with
  their `<Body>Talk`.
- **Build timing, so nothing doubles while the shim still exists:** a layer added during its zone's `_ready`
  (Haluna not prebuilt) now builds deferred, after HalunaVillagers.populate, so it adopts the shim's three. In the
  prebuilt path it already built after populate. Tests:
  - test_a_layer_added_in_the_zones_ready_adopts_what_the_zone_places_after;
  - test_a_row_can_wear_another_villagers_model;
  - cinematics' test_haluna_villagers, 7/0 (each villager once).
- **For cinematics:** you can now delete `game/data/flow/haluna_villagers.json` and the HalunaVillagers placement
  shim (keep `end_talks`, which HalunaStory uses). VillagerLayer places the three from then on, the same models.

## Review log
