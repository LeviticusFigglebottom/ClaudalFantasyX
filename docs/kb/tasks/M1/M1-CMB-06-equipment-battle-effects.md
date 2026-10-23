---
id: M1-CMB-06
title: Equipment on-hit effects, battle item use, and lume/drop rewards in BattleEngine
role: combat
status: review
owner_session: combat-stream-2
reviewer: progression
depends_on: [M1-PRG-02]
milestone: M1
request-from: progression
---
## Goal
Wire the M1-PRG-02 equipment and item APIs into `game/battle/` (Progression may not edit it). Design and data: [docs/kb/design/economy.md](../../design/economy.md).

## What Progression already provides
- `EquipmentEffects.apply_to(c)` is a `party_modifier`, composable with the Lattice: `engine.party_modifier = EquipmentEffects.compose([progress.apply_to, fx.apply_to])`. It already applies piece stats and stat abilities, `always` auto-statuses (duration -1), element guards (affinities), and Unfettered (`break_damage_cap`).
- For everything that needs the engine, it leaves plain data on the combatant: `EquipmentEffects.data_of(c)` (that is, `c.get_meta(&"equipment_effects")`):
  - `attack_elements: Array[StringName]`: elements of the basic Attack, in slot order.
  - `on_hit_statuses: Array[{id, chance, duration}]`: one per status (the highest chance wins).
  - `status_wards: Array[StringName]`: statuses this combatant can't receive.
  - `low_hp_statuses: Array[{id, hp_below_pct, duration}]`: statuses that switch on below an HP threshold.
  - `abilities: Array[StringName]`: every equipped ability (for UI/debug).
- `ItemBattleAction.for_item(db, id)` describes a battle item: `target` (skill target vocabulary), `rank`, `effects`, and `targets_fallen` (revives target KO'd allies only). `can_target(c)`, `resolve_on(c)` (deterministic reference resolution; its `amount` uses the hit convention, positive = damage), `consume(inventory)`, and `ItemBattleAction.usable_items(db, inventory)`.
- `EquipmentEffects.currency_multiplier(cids)` gives the Full Net multiplier (the highest worn by anyone credited).

## Acceptance criteria
- [x] The basic Attack uses `attack_elements` (proposal: the element the target is weakest to, falling back to the first; none means `"none"`). Element skills keep their own element.
- [x] Physical hits roll each `on_hit_statuses` entry on the seeded `rng` after damage, only if the hit landed and the target lives.
- [x] `add_status` refuses statuses in the target's `status_wards` (a party-side immunity; enemies may reuse the mechanism later).
- [x] `low_hp_statuses` switch on when HP drops below `hp_below_pct` of max (checked after damage) and switch off when healed at or above it.
- [x] Item use is a battle action: `use_item(item_id, targets, inventory)` (or similar) validates targets with `ItemBattleAction.can_target`, applies `resolve_on`, consumes one item, ends the turn with `rank`, and emits an `ActionResult`. The timeline preview accepts an item's rank as the candidate action.
- [x] `enemies.json` rows gain `currency` and `drops` (`[{item, chance}]`, item ids from `game/data/items/items.json`). Proposed lume: reef crab 24, lantern-lure eel 20, gull harrier 18, Drownbell about 300. Proposed drops: crab carapace, eel lantern, harrier quill, and the occasional salt_tonic. Add `BattleEngine.currency_award()` (× `currency_multiplier` of the credited party) and seeded drop rolls. The validator should check drop item ids.
- [x] formulas.md gains the item formulas: revive HP = `max(1, floor(max_hp × hp_pct / 100))`, and fixed item damage = `clamp(amount × el_num ÷ el_den, −cap, cap)` (ignores stats, defense, and barriers). Both already live in `ItemBattleAction.revive_hp` / `fixed_damage` with tests. Mirror or move them into `Formulas` as you prefer.
- [x] Tests in `tests/unit/test_battle_*` for each item, and the battle stays deterministic.

## Notes
- If you promote the metadata to a typed `BattleCombatant` field, tell Progression so `EquipmentEffects.apply_to` changes in the same commit.
- Decide whether dispel effects (later) may strip the duration -1 auto-statuses from equipment.

Delivered (combat-stream-2). Rules are in formulas.md § Items, § Equipment in battle, § Rewards; the API is in battle_ctb.md § Timeline API.
- The metadata is **not** promoted to a typed field. The engine reads it through `BattleCombatant.equipment()` (key `EQUIPMENT_META`, and a test asserts it equals `EquipmentEffects.META_KEY`), so `EquipmentEffects.apply_to` needs no change.
- Attack element: the weakest-to element, with ties going to slot order (the hit reports `element`). Strikes roll after the landed physical hit, before the skill's own statuses. Wards live in `add_status`. Low-HP statuses are re-checked after every turn and every swap, and only the equipment's own copy is removed.
- `use_item(item_id, targets, items: BattleItemSource)`. The engine only sees the injectable `BattleItemSource`; `InventoryItemSource` wraps ItemDB plus Inventory. `item_can_target()` adds "revive fells a living Zombie" on top of `ItemBattleAction.can_target`. A revive rejoins at now + a default-rank delay. `preview_item()` is tested against play.
- Rewards: `enemies.json` `currency` 24/20/18 and drops (the material at 50%, Salt Tonic at 10%). `currency_award()` uses the `currency_multiplier` hook; `drop_awards()` is rolled once at victory on the seeded RNG. The validator checks drop items, chances and currency. Drownbell's ~300 lume comes with its encounter data.
- `Formulas.revive_hp` / `item_damage` mirror ItemBattleAction's, and a test keeps them equal.
- **Dispel decision:** equipment "always" statuses are ordinary and may be dispelled (they don't return); low-HP ones return while the condition holds.
- Tests: `test_battle_items.gd` (20), `test_battle_equipment.gd` (15), 3 in `test_formulas.gd`, 2 validator tests. Coverage: battle 99.53%, progression 95.42% (baselines ratcheted).
For Progression: wire `InventoryItemSource` and `currency_multiplier = fx.currency_multiplier` into the sandbox glue (UI stream), and award `drop_awards()` / `currency_award()` into the inventory and wallet after victory.

## Review log
