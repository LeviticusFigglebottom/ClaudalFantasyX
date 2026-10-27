---
id: M2-FP-113
title: "Haluna's villagers have one owner: creatures' VillagerLayer (the shop bodies stay a shim until M2-CHR-100)"
role: cinematics
status: review
owner_session: "slice-polish (claude/m2-slice, session_01KZCgTqxhHKjvMCm1dAosvZ)"
depends_on: [M3-CRE-613, M2-FP-102]
reviewer: character
milestone: M2
request-from: lead
---
## Goal
The Lead (big11): creatures' VillagerLayer (M3-CRE-613) and m2-slice's HalunaVillagers (M2-FP-102) both turned
Haluna's stand-ins into villagers. Only one should own them.

## Decision
creatures' **VillagerLayer** owns Haluna's villagers: it is the npc system's owner, and its data does more (routes,
chat partners, work focus, storm shelters).

## Acceptance criteria
- [x] HalunaZone adds one `VillagerLayer` (`zone_id ch02/haluna`) with the WildlifeLayer (`_add_life`, in prebuild
  or `_ready`).
- [x] `HalunaVillagers` and `haluna_villagers.json` are cut down to the three shop bodies VillagerLayer doesn't cover
  (shopkeeper, smith, innkeeper; they wear other villagers' models until M2-CHR-100). `end_talks` ends any
  FieldNpc's talk.
- [x] CutsceneNpcTalk (M2-FP-106) and `freeze_player` (M2-FP-107) work on VillagerLayer's villagers unchanged.
- [x] test_haluna_villagers: every villager exists once, no capsule shows, and there is one VillagerLayer. haluna 57,
  villager 18, npc 10, cutscene 60, swap 15, all 0 failed.
- [ ] creatures (M3-CRE-100):
  - their `haluna_villagers` review stage uses the zone's own VillagerLayer instead of adding a second;
  - their data takes the shop rows, once a row can name its actor.

## Review log
