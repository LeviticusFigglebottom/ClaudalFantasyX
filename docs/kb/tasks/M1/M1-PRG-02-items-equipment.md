---
id: M1-PRG-02
title: Items, inventory, equipment with ability slots, Customize, shops (data + headless logic)
role: progression
status: done
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
- 2026-10-23 combat (review-sweep-A): **approve with fixes**. The data, the validator (`check_items`, 0 errors), the logic and the tests are solid, and the suite is green. `EquipmentEffects.apply_to` is correct against the engine: stats add once, HP and MP raise both max and current, guards never weaken an affinity, the `always` auto-statuses use −1 (the engine's whole battle), Unfettered sets `break_damage_cap`, and the level stays fixed (ADR 0012). The v2→v3 migration and the float tolerance through `int()` are correct. The heal and cure prices fit the combat numbers: enemy hits are 55–105 against 280–560 HP, so a 200 HP Salt Tonic undoes about two hits. That is close to Mend (230 at rank 3) but costs lume, which is fine.
  - **should-fix** (tempo balance): Drag Net (`items.json:13`, rank 2, delay 2 ranks, 80 lume, sold in Haluna Market from `ch02_met_asha`) strictly dominates Rhen's Undertow Cut (rank 4, delay 2, 8 MP). The user pays 2 × its own base delay and the target loses 2 × its own. Rhen (base delay 58) netting the Reef Crab (115) spends 116 ticks to push it back 230, so one netter can lock any slower foe out of its turns indefinitely. That includes a low-agility boss, limited only by stock and lume. Fix: rank 3 with delay 1, or delay scaled as rank × the user's base delay, or bosses with delay resistance. The sim can check it once items have a policy hook.
  - **should-fix** (API contract for CMB-06): the revive effect sets HP but not `next_time` (`item_battle_action.gd:114-118`). A probe KO'd Asha at t=204, played on to now=519, and used a Relighting Wick through `resolve_on`. `timeline.next_actor()` was then Asha at 204, and the engine's `_advance` would set `now` back to 204, so time runs backwards. Swap-in already avoids this (`_swap_in_time`). Fix: either `resolve_on` takes `now` and sets `next_time = now + action_delay(agility, DEFAULT_RANK)` for a revive, or the docs and the CMB-06 request say the engine must. Also note there that Petrify cures can't target anything (`can_target` needs `is_alive()`; see the CMB-02 review).
  - **should-fix**: nothing in `game/` calls `EquipmentBag.grant_starting`, so for a migrated v2 save whose party has already joined, "heroes receive their starting gear when they next join" never happens. They load with no weapon, even though `weapon` is a required slot. Fix: a post-load step, for example in `PartyGoods.from_state` or the load path, that calls the idempotent `grant_starting` for `party_ids + reserve_ids`, plus a test that runs v2 through `deserialize` to equipped weapons.
  - **nit** (footgun): Godot Callables don't keep a RefCounted alive. `EquipmentEffects.compose` (`equipment_effects.gd:56-61`) silently skips invalid callables, and the engine silently skips an invalid `party_modifier`. A probe passed `EquipmentEffects.new(db, bag).apply_to` without keeping a reference, and the tier-1 gear silently did nothing (`Callable(...).is_valid()` was false). Make `compose` push an error on an invalid callable, and say in the class doc that the caller must hold `fx` and `progress` for the life of the engine setup.
  - **nit**: Ember Pot (150 fixed fire damage, ignores defense, rank 2) beats Rhen's attack on the crab and does 87% of Ysolde's Ember on the eel, at a faster rank. It isn't stocked in the slice, so this is fine for now. Re-check before it reaches a shop, because fixed damage that ignores defense undercuts the role-answer lesson early. Similarly, Coral Hooks' Ember Edge will make Rhen the eel's answer once CMB-06 applies on-hit elements. That is intended customization, but it is worth one line in `balance_targets.md`.
- 2026-10-23 lead: closing on review-sweep-A approve-with-fixes; Drag Net and revive timing were forwarded to M1-CMB-06; the save/gear fixes are in M1-PRG-03.
