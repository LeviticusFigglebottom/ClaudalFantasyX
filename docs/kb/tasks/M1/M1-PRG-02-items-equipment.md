---
id: M1-PRG-02
title: Items, inventory, equipment with ability slots, Customize, shops (data + headless logic)
role: progression
status: review
owner_session: progression-stream-2
reviewer: combat
depends_on: [M1-PRG-01]
milestone: M1
request-from: ""
---
## Goal
SPEC §6.5 and the item/shop parts of §6.11, as data and testable logic for the M2 slice.

## Acceptance criteria
- [x] items.json (consumables, key items, Facets as items), equipment.json (weapons/armor per character, up to 4 slots), abilities catalogue
- [x] Inventory with stacking and caps; key items
- [x] Customize: craft abilities into empty slots at item costs
- [x] Shops with stock per story flag
- [x] Equipment stat/ability effects exposed through a hook for BattleEngine.party_modifier (no game/battle edits)
- [x] Validator coverage and tests; save integration (SAVE_VERSION bump + migration)

## Notes
Item-use in battle is Combat's follow-up; expose a clean API.

Done (progression-stream-2): data in `game/data/items/`, logic in `game/progression/` (ItemDB, Inventory,
EquipmentBag, Customize, Wallet, Shop, FlagReader, PartyGoods, EquipmentEffects, ItemBattleAction), save v3,
validator `check_items`, design doc [economy.md](../../design/economy.md). Currency is **lume**. Engine-side work
is requested in [M1-CMB-06](M1-CMB-06-equipment-battle-effects.md).

## Review log
