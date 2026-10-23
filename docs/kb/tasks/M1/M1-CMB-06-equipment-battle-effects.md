---
id: M1-CMB-06
title: Equipment on-hit effects, battle item use, and lume/drop rewards in BattleEngine
role: combat
status: todo
owner_session: ""
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
- [ ] The basic Attack uses `attack_elements` (proposal: the element the target is weakest to, falling back to the first; none means `"none"`). Element skills keep their own element.
- [ ] Physical hits roll each `on_hit_statuses` entry on the seeded `rng` after damage, only if the hit landed and the target lives.
- [ ] `add_status` refuses statuses in the target's `status_wards` (a party-side immunity; enemies may reuse the mechanism later).
- [ ] `low_hp_statuses` switch on when HP drops below `hp_below_pct` of max (checked after damage) and switch off when healed at or above it.
- [ ] Item use is a battle action: `use_item(item_id, targets, inventory)` (or similar) validates targets with `ItemBattleAction.can_target`, applies `resolve_on`, consumes one item, ends the turn with `rank`, and emits an `ActionResult`. The timeline preview accepts an item's rank as the candidate action.
- [ ] `enemies.json` rows gain `currency` and `drops` (`[{item, chance}]`, item ids from `game/data/items/items.json`). Proposed lume: reef crab 24, lantern-lure eel 20, gull harrier 18, Drownbell about 300. Proposed drops: crab carapace, eel lantern, harrier quill, and the occasional salt_tonic. Add `BattleEngine.currency_award()` (× `currency_multiplier` of the credited party) and seeded drop rolls. The validator should check drop item ids.
- [ ] formulas.md gains the item formulas: revive HP = `max(1, floor(max_hp × hp_pct / 100))`, and fixed item damage = `clamp(amount × el_num ÷ el_den, −cap, cap)` (ignores stats, defense, and barriers). Both already live in `ItemBattleAction.revive_hp` / `fixed_damage` with tests. Mirror or move them into `Formulas` as you prefer.
- [ ] Tests in `tests/unit/test_battle_*` for each item, and the battle stays deterministic.

## Notes
- If you promote the metadata to a typed `BattleCombatant` field, tell Progression so `EquipmentEffects.apply_to` changes in the same commit.
- Decide whether dispel effects (later) may strip the duration -1 auto-statuses from equipment.

## Review log
