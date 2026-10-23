# Economy: Items, Equipment, Customize, Shops

Owner: Progression & Economy (M1-PRG-02). Reviewer: Combat (SPEC §12.3). Spec: SPEC §6.5 (equipment customization), §6.6 (towns, shops), and §6.11 (item and key-item menu). Related: [lattice.md](lattice.md) (Facets are items), [formulas.md](formulas.md).

This page covers the currency, the data files, the headless logic, the price curve, the vertical-slice item list, how to add things, and what Combat and UI still have to build.

## Currency: **lume**

**Decision (M1-PRG-02, 2026-10-22).** The currency is **lume** (n., uncountable, rhymes with "loom"; "40 lume", "a lume" for one coin). Code keeps the neutral name `currency` (`GameStateData.currency`, `Wallet`). The display string is the loc key `CURRENCY_NAME`, and amounts use `CURRENCY_AMOUNT` (`%d lume`).

- **In the world.** A lume is a thin disc of pressed lamp-brass, punched through the centre so it can be strung on a cord. The Order mints it, and the name comes from the one light the Order allows: **oil lamps**. Bound glimmer is forbidden, so the Order's money is "lamp money", honest oil-light you can hold. That fits the bible's lamp metaphysics ("her lamp went out"), Rhen's trade (he cuts out pre-Edict brass and sells it), and the quiet irony that the faith's coin is named for light while the faith herds the dead into the sea.
- **Why not the alternatives.** "Shell" collides with the Shell status and the Shell Shrine. A Lamptongue coinage (for example *halish*) would make ordinary prices sound liturgical. "Brass" is generic and also Rhen's salvage material. "Lume" is short, readable on a price tag, and original. It is not on `tools/banned_terms.txt`, and nothing close to the inspiring series' currency is used anywhere.
- **Glossary.** The glossary is the Lead's file. The proposed entry is: `- **lume** (n., uncountable; "a lume" for one coin): the Order-minted currency of Maresh, a holed disc of pressed lamp-brass named for oil-lamp light, the only light the Order allows. *design/economy.md*`. It replaces the "currency: name TBD" line.

## Files

| Path | What it is |
|---|---|
| `game/data/items/items.json` | `rules` (stack caps, currency cap, category order) and every bag item: consumables, materials, Facets, and key items. |
| `game/data/items/equipment.json` | `rules` (max 4 slots, equip slots, required slots), `gear_types` (one weapon and one armor type per character), 20 pieces, and `starting` gear. |
| `game/data/items/abilities.json` | 30 equipment abilities in 9 categories, each with an `effect` block. |
| `game/data/items/customize.json` | One recipe (item costs) per craftable ability. |
| `game/data/items/shops.json` | `rules` (sell ratio) and the two Haluna shops with flag-gated stock. |
| `game/progression/item_db.gd` | `ItemDB`, the read-only tables (`load_default()`, `from_tables()` for fixtures). |
| `game/progression/inventory.gd` | `Inventory`, the bag (wraps `GameStateData.inventory`). |
| `game/progression/equipment_bag.gd` | `EquipmentBag`, the owned pieces and loadouts (wraps `GameStateData.equipment`). |
| `game/progression/customize.gd` | `Customize`, which crafts abilities into empty slots. |
| `game/progression/wallet.gd`, `shop.gd`, `flag_reader.gd`, `party_goods.gd` | The purse, shops, injectable flag reads, and a facade over `GameStateData`. |
| `game/progression/equipment_effects.gd` | `EquipmentEffects`, the battle hook (`party_modifier`). |
| `game/progression/item_battle_action.gd` | `ItemBattleAction`, the battle item-use API for Combat. |
| `tools/validate_data.py` | `check_items` / `items_errors`, run in CI. Tests: `tools/tests/test_items_validate.py`. |

## Data model

### Items (`items.json`)

| `category` | Price | Stack | Battle | Notes |
|---|---|---|---|---|
| `consumable` | > 0 | `stack_cap` (99) | optional `battle` block | `field: true` marks menu use outside battle. |
| `material` | > 0 | 99 | none | Customize ingredients and salvage to sell. |
| `facet` | > 0 | 99 | none | `facet` must equal the id and exist in `facets.json`. Every Facet has a row. |
| `key` | **none** | `key_item_cap` (1) | none | Never sold, never spent by Customize, never stocked. |

An item may override the global cap with `stack_cap`. The order of `rules.category_order`, then the row order in the file, is the **listing order** the menus use (`Inventory.ids()`).

`battle` block: `{"target": <skill target>, "rank": 1..8, "effects": [...]}`. Effects run in order:

| `type` | Fields | Does |
|---|---|---|
| `heal_hp` | `amount` | Restores a fixed amount of HP, up to max, through `restore_hp`, so it damages under Zombie. Living targets only. |
| `restore_mp` | `amount` | Restores a fixed amount of MP, up to max. |
| `cure` | `statuses` | Removes the listed statuses. |
| `revive` | `hp_pct` | A KO'd target returns with `max(1, floor(max_hp × hp_pct / 100))` HP. The item targets **only** the fallen (HP 0). A petrified ally is neither alive nor fallen, so no current item reaches them. A Petrify cure is a follow-up for when Combat finalizes Petrify. |
| `add_status` | `status`, `duration` | Like a skill's inflict, but certain to land. |
| `delay` | `ranks` | Adds `base_delay(target.agi) × ranks` ticks to the target's `next_time` (the same rule as a skill's `delay_ranks`). |
| `damage` | `amount`, `element` | Fixed damage that ignores stats, defense and barriers, takes the element ratio of the target's affinity (absorb heals), and is capped at `DAMAGE_CAP`. |

Item effects are fixed numbers, not stat-scaled. That is the genre convention, and it keeps an item's cost readable (pillar 4: "Salt Tonic: 200 HP" is the whole truth). **For Combat:** formulas.md lists "item formulas (Progression)" as unspecified. The two formulas above (revive HP, fixed damage) are the whole set. They are implemented in `ItemBattleAction.revive_hp` / `fixed_damage` and tested in `tests/unit/test_inventory_battle_items.gd`. Please fold them into formulas.md when you wire item use (M1-CMB-06).

### Equipment (`equipment.json`)

- **Gear types** give each character one weapon type and one armor type, taken from the story sheets: Rhen's **reef-hooks** and tether harness, Asha's **lantern-staff** and bell-shell bangle, Toma's **boarding spear** and **tide-shield**, and Ysolde's **folding lacquer book** and **ink-guards**. A piece belongs to exactly one character through its gear type. Kerrid's anchor-cleaver, Pell's fishing-staff, and Liss's gear are added when Combat adds those characters to `characters.json` (the validator rejects gear for unknown characters).
- **A piece** has `price`, `slots` (0 to `max_slots`, which is 4 per SPEC §6.5), `abilities` (pre-filled, no more than `slots`, each fitting the piece's slot kind), and optional flat `stats` (Lattice stat names).
- **Instances.** Owned equipment lives in `GameStateData.equipment` as individual pieces with uids (`EquipmentBag`). Customize changes one sword, not every copy of that sword. uids count up from 1 and are never reused.
- **Loadout.** Each character has a `weapon` and an `armor` slot. `required_slots: ["weapon"]` means the weapon can be swapped but never removed. `starting` lists every battle character's opening gear. Call `EquipmentBag.grant_starting(id)` when a hero joins (it does nothing the second time).

### Abilities (`abilities.json`)

`equip` lists the slot kinds an ability may sit in. Duplicates on one character **stack** for stat bonuses, merge to the highest chance for status strikes, and take the best value for economy and field abilities.

| Category | Effect fields | Abilities | Applied by |
|---|---|---|---|
| `on_hit_element` | `element` | Ember / Tide / Spark / Rime **Edge** | **Combat** (data on combatant) |
| `status_strike` | `status` (harmful), `chance`, `duration` | Bitter (Poison), Drowse (Sleep), Gloam (Darkness), Drag (Slow) **Edge** | **Combat** (data) |
| `stat_bonus` | `stat`, `amount` | Steady Arm, Clear Mind, Keen Sight, Deep Lungs, Hard Carapace, Still Heart, Light Feet | `EquipmentEffects.apply_to` |
| `element_guard` | `element`, `affinity` | Ember / Tide / Spark / Rime **Guard** (resist) | `apply_to` (never weakens an affinity) |
| `status_ward` | `status` (harmful) | Bitterward, Wakeward, Voiceward, Sightward | **Combat** (data) |
| `auto_status` | `status` (beneficial), `trigger`, `hp_below_pct` for `low_hp` | Standing Guard, Standing Mend (`always`); Low Tide Haste, Low Tide Mend (`low_hp` < 50%) | `always`: `apply_to`; `low_hp`: **Combat** (data) |
| `economy` | `currency_mult` | Full Net (×2 battle lume) | `currency_multiplier()` (battle rewards) |
| `field` | `encounter_rate_pct` | Light Step (50%) | `encounter_rate_pct()` (field) |
| `special` | `break_damage_cap` | Unfettered | `apply_to` (`c.break_damage_cap`) |

### Customize (`customize.json`)

`{"ability": id, "items": [{"item": id, "count": n}]}`. Rules (`Customize.craft_error` explains each refusal): the piece exists; the ability exists, has a recipe, fits the piece's slot kind, and isn't already on that piece; there is an empty slot (the first one, or a given index that is empty); and the party holds every recipe item. Crafting spends the items and is permanent. Key items can't be ingredients.

### Shops (`shops.json`)

- `rules`: `sell_ratio_num / sell_ratio_den` (1/2) and `min_sell_price` (1). Sell price = `max(floor(price × num / den), min)`. The validator enforces `num ≤ den`, so selling never profits.
- A shop has a `kind` (`items` or `equipment`), a `requires_flag` to open, and `stock` rows `{"item", "requires_flag"?}`. Rows appear in data order once their flag is set. Every flag must be declared in `flags.tres`, and the validator checks it.
- **Any shop buys anything sellable**, including unequipped pieces at their base piece's sell price. Crafted abilities add nothing to the price, so customizing is never a way to make money.
- Flags are read through `FlagReader` (injectable). In the game, use `FlagReader.from_access(GameFlagAccess.new())`. In tests, set `reader.values[...]`.

## Logic at a glance

```gdscript
var db := ItemDB.load_default()
var goods := PartyGoods.from_state(db, Game.state)          # wraps inventory/equipment/currency in place
goods.equipment.grant_starting(&"rhen")                      # on join
var shop := Shop.new(db, &"haluna_market")
var flags := FlagReader.from_access(GameFlagAccess.new())
shop.buy_error(&"salt_tonic", 2, goods, flags)              # → &"ok" or an ERR_* to show in the UI
shop.buy(&"salt_tonic", 2, goods, flags)
Customize.new(db).craft(goods.equipment, uid, &"ember_edge", goods.inventory)

# Battle: compose with the Lattice.
var fx := EquipmentEffects.new(db, goods.equipment)
engine.party_modifier = EquipmentEffects.compose([progress.apply_to, fx.apply_to])
```

Every action returns `RESULT_OK` or an `ERR_*` StringName, and every `*_error()` call answers without changing anything, so the UI can always say what an action costs and why it's blocked (pillar 4). Nothing uses randomness. The same inputs always give the same bag, pieces, and combatant.

## Saving

Save version **3** added `GameStateData.equipment` (`{next_uid, owned: {"<uid>": {base, abilities[]}}, loadout: {character: {weapon, armor}}}`). The v2→v3 migration writes an empty bag (heroes get starting gear when they next join) and rewrites inventory counts as whole ints without empty stacks, because JSON numbers load as floats. Items, materials, Facets, and key items all live in `inventory` (item id → count), and lume lives in `currency`. After loading, `Inventory.normalize()` drops ids the catalogue no longer has (with a warning) and clamps stacks to their caps.

## Price curve

Anchors from the M1 sandbox: an early three-enemy fight credits 105 XP. **Proposed battle lume** (for Combat to add to `enemies.json`, see M1-CMB-06): reef crab 24, lantern-lure eel 20, gull harrier 18, so about **60 lume per early fight**, and about 300 for the Drownbell.

| Tier | Price | What it costs in early fights | Rationale |
|---|---|---|---|
| Status cures (Bitterleaf 15, Eyewash 20, Honey 20, Salts 25) | 15–25 | about ⅓ | Cheap enough that a player never skips a cure out of thrift. Status is a lesson, not a tax. |
| Salt Tonic | 40 | about ⅔ | One fight buys one heal plus change. 200 HP is about half of Rhen's 420. |
| Drag Net / Quiet Tea / Ember Pot | 80–110 | about 1½ | Tactical items cost a fight or two, so using one is a decision. |
| Reef Draught, Tidewash Salve | 120–150 | 2–2½ | Post-boss stock for the next chapter. |
| Relighting Wick | 300 | 5 | Revives are precious, but one is affordable before the first real boss of Act I. |
| Tier-1 weapon / armor (2 slots, one ability pre-filled) | 380 / 340 | about 6 | A player finishing the slice (about 6–8 fights plus the boss, about 700 lume) can afford **one or two** upgrades, not all of them. The choice is the point. |
| Tier-2 weapon (3 slots, empty) | 620 | about 10 (at slice income) | Post-Drownbell stock, priced for Ch4 income. Each tier costs about 1.6× the last. |
| 4-slot piece | 1200 | about 20 | The first 4-slot piece (Toma's Reach Tide-Shield) is a goal, not a purchase. |
| Key Facets | 400 / 800 / 1600 / 3200 | — | Doubling per level. Gates should open mostly through battle drops, and buying a Key is the expensive shortcut. |

Rules of thumb for later chapters: (1) each chapter's tier-N gear costs about **six of that chapter's fights**; (2) each tier is about **1.6×** the last; (3) consumables stay at one fight or less for their chapter; (4) materials sell at half price, and **Lit Age Brass** (180, sells for 90) is the "Rhen knows what everything sells for" item from the slice beats. Validate these against the balance simulator (M1-CMB-05) once enemies carry lume and drops.

Customize costs follow the same idea: an element edge costs 4 of its element material, a guard costs 3, a stat ability costs 8–10 common drops, and the strong ones (Standing Guard, Full Net, Unfettered) cost 10–20 rare items, so they are late-game projects.

## The vertical slice (Ch2–3, Haluna)

**Haluna Market** (`haluna_market`, opens on `ch02_met_asha`): Salt Tonic, Bitterleaf, Brine Eyewash, Smelling Salts, Quiet Tea, Drag Net, and the Power, Mind and Speed Facets. After `ch03_drownbell_defeated` (the night barks variant), it adds Reef Draught, Throat Honey, Tidewash Salve, and Relighting Wick.

**The Net-Rack Forge** (`haluna_forge`, opens on `ch02_met_asha`, the slice's "equipment shop"): Coral-Bitten Hooks (Ember Edge), Reefline Harness (Bitterward), Bell-Shell Staff (Clear Mind), Tide-Pearl Bangle (Wakeward), Net-Rack Spear (Steady Arm), and Chiselled Shield (Ember Guard). After the Drownbell: Tidewalker Hooks, Dawnwick Staff, Saltgrass Pike, and the 4-slot Reach Tide-Shield.

**Key items**: the **Brass Lantern** (Rhen's father's; Rhen has it from B01) and the **Glass Net-Float** (the optional B07 pickup that sets `ch03_found_net_float`; World/Narrative should grant the item in the same pickup). **Starting gear**: every hero's 1-slot starter weapon and armor. **Drops** on the causeway (Combat to add): crab carapace, eel lantern, and harrier quill, plus the occasional Salt Tonic. No new story flags were needed.

Haluna's **inn** is not modelled yet (a price and a full heal). It is a one-field shop kind to add when World builds the inn (see UI/World below).

## How to add things

- **An item.** Add a row to `items.json` (unique id, category, `name_key`, `desc_key`, a positive price unless it's a key item, and an optional `battle` block). Append its two loc keys to `strings.csv`. Run `python3 tools/validate_data.py`. Where it sits in the file is its menu position within its category.
- **An equipment piece.** Add a row to `equipment.json` with an existing gear `type`, `slots` ≤ 4, pre-filled `abilities` that fit, and a price. Add the loc keys. To sell it, add a stock row to a shop.
- **An ability.** Add a row to `abilities.json` with a category from the table above and its exact effect fields, plus loc keys and a recipe in `customize.json` (unless it should be find-only). A **new category** also needs `ABILITY_EFFECT_FIELDS` in the validator, handling in `EquipmentEffects` (`apply_to` if the engine supports it today, otherwise `battle_data` plus a Combat request), and tests.
- **A new battle item effect.** Add it to `ITEM_EFFECT_FIELDS` in the validator, to `ItemBattleAction._apply`, and to the table above, and tell Combat.
- **A shop.** Add a row to `shops.json`. Flags must already be declared (append new ones to `flags.tres` with a description).
- **A character.** Add a weapon and an armor `gear_type`, their pieces, and a `starting` entry. The validator fails until every `characters.json` hero has starting gear.

## Gotchas

- **uids and ids are save data.** Renaming an equipment id or ability id after it ships orphans pieces in saves. Add a migration if you must.
- **`apply_to` adds.** As with the Lattice, call the composed modifier once per freshly built combatant.
- **Engine-facing data is metadata.** `game/battle/` is Combat's, so on-hit elements, status strikes, wards, and low-HP statuses travel as `c.get_meta(EquipmentEffects.META_KEY)` (read it with `EquipmentEffects.data_of(c)`). Combat may promote it to a typed `BattleCombatant` field. If so, change `EquipmentEffects.apply_to` in the same commit.
- **"Always" auto-statuses are ordinary statuses** with duration −1. If Combat later adds dispel, decide whether equipment statuses resist it.
- The `test_*` flags are for tests only. Shop data must never use them.

## What remains

### Combat (request task [M1-CMB-06](../tasks/M1/M1-CMB-06-equipment-battle-effects.md)): done, see formulas.md § Items, § Equipment in battle, § Rewards

1. Read `EquipmentEffects.data_of(c)` in `BattleEngine`: `attack_elements` on the basic Attack (suggested: use the element the target is weakest to, otherwise the first), `on_hit_statuses` on physical hits (roll with `rng`, after damage), `status_wards` (immunity in `add_status` for party members), and `low_hp_statuses` (apply when HP falls below the threshold, remove when healed above it).
2. Item use as a battle action: `BattleEngine.use_item(item_id, targets, inventory)` built on `ItemBattleAction` (target validation with `can_target`, `rank` for the delay, consume one item, emit an `ActionResult`), plus the timeline preview for item rank.
3. Battle rewards: `currency` and `drops` on `enemies.json` rows (the proposed lume is above), `BattleEngine.currency_award()` multiplied by `EquipmentEffects.currency_multiplier(credited ids)`, and drop rolls on the seeded `rng`.
4. Fold the item formulas (revive HP, fixed damage) into formulas.md.

### UI

- An item menu (categories in `category_order`, `Inventory.ids_in`), a key-item menu, an equip screen (`EquipmentBag.pieces_for`, stat deltas from `EquipmentEffects.stat_bonuses`), a Customize screen (`Customize.candidates`, `cost`, `shortfall` to grey out what the party is missing), and a shop screen (`Shop.stock`, `buy_error`/`sell_error` messages from `ERR_*`, and the `CURRENCY_AMOUNT` string). Field item use needs persistent party HP/MP, which `GameStateData` doesn't hold yet (Architect).
- World: grant the Glass Net-Float in the B07 pickup, call `grant_starting` when heroes join, and model the inn.
