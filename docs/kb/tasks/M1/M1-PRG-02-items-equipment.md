---
id: M1-PRG-02
title: Items, inventory, equipment with ability slots, Customize, shops (data + headless logic)
role: progression
status: todo
owner_session: ""
depends_on: [M1-PRG-01]
milestone: M1
request-from: ""
---
## Goal
SPEC §6.5 and the item/shop parts of §6.11, as data and testable logic for the M2 slice.

## Acceptance criteria
- [ ] items.json (consumables, key items, Facets as items), equipment.json (weapons/armor per character, up to 4 slots), abilities catalogue
- [ ] Inventory with stacking and caps; key items
- [ ] Customize: craft abilities into empty slots at item costs
- [ ] Shops with stock per story flag
- [ ] Equipment stat/ability effects exposed through a hook for BattleEngine.party_modifier (no game/battle edits)
- [ ] Validator coverage and tests; save integration (SAVE_VERSION bump + migration)

## Notes
Item-use in battle is Combat's follow-up; expose a clean API.

## Review log
