---
id: M3-CRE-100
title: "VillagerLayer in Haluna: the review stage reuses the zone's layer; the shop bodies move into its data"
role: character
status: todo
owner_session: ""
depends_on: [M2-FP-113]
reviewer: cinematics
milestone: M3
request-from: cinematics
---
## Goal
M2-FP-113 (claude/m2-slice) makes your VillagerLayer the one owner of Haluna's villagers: HalunaZone now adds a
`VillagerLayer` node named `VillagerLayer` (`zone_id ch02/haluna`) itself. Two follow-ups are yours.

## Acceptance criteria
- [ ] `game/levels/_tests/npc/haluna_villagers.gd`: use `zone.get_node("VillagerLayer")` instead of adding a
  second layer. With m2-slice's change, a second layer would put every villager in your `npc_haluna_*` shots twice.
- [ ] Give a row an optional actor override (e.g. `"actor": "vendor"`), and add rows for
  - `NPCs/Town/Shopkeeper` (talk `NPCs/Town/ShopkeeperTalk`),
  - `Smith` (`SmithTalk`),
  - `Innkeeper` (`InnkeeperTalk`).

  Tell cinematics: it then deletes `game/data/flow/haluna_villagers.json` and the HalunaVillagers shim. Until
  M2-CHR-100 they wear the netmender's, fisher's and vendor's models.

## Review log
