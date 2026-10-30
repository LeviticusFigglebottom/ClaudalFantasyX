---
id: M3-ARC-1327
title: "Retire HalunaVillagers: its shop rows are gone; the shop villagers wear their own models"
role: architect
status: todo
owner_session: ""
depends_on: [M3-CHR-512]
milestone: M3
request-from: character
reviewer: character
---
## Goal
The Lead decided on 2026-10-30 that named interactable villagers wear their bespoke models. The creatures track deleted
the three shop rows from `game/data/flow/haluna_villagers.json`, with the Lead's authorisation. VillagerLayer's
ch02_haluna.json rows now give the shopkeeper, smith and innkeeper their own M3-CHR-512 models. The file and
`HalunaVillagers.populate` now place nothing. Retire them: delete the file and the populate call in
`haluna_zone.gd`, keep `HalunaVillagers.end_talks` (or move it), and update the doc comments that name them.

## Acceptance criteria
- [ ] The file and the populate call are gone; `end_talks` still works.
- [ ] `tests/integration/test_haluna_villagers.gd` and `tests/unit/test_villager_routines.gd` pass.

## Notes
- One-line request from claude/creatures. Nothing breaks while the empty file stays.

## Review log
