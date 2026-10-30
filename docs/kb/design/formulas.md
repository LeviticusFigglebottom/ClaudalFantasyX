# Battle Formulas

**Source of truth.** `game/battle/formulas.gd` mirrors this file exactly, and `tests/unit/test_formulas.gd` has a test per formula with the worked examples below. Change all three in one commit, and get the change reviewed by Progression (SPEC §12.3).

Notation: `floor`, `ceil`, `clamp(x, lo, hi)`. **`round` rounds half away from zero** (Godot `roundi`; 400.5 → 401). `a ÷ b` is integer division truncating toward zero. All stats are non-negative integers. **Damage and healing are computed exactly in integers** (rational multipliers and a single truncating division at the end), so an external simulator reproduces them bit-for-bit.

## Constants

| Name | Value | Meaning |
|---|---|---|
| `DELAY_K` | 1600 | Delay scale |
| `DELAY_OFFSET` | 6 | Keeps low-agility delays finite |
| `DEFAULT_RANK` | 3 | Rank of a standard action; also used for all *predicted* future turns |
| `INITIAL_RANK` | 3 | Rank used for opening ticks |
| `MIN_DELAY` | 1 | No action is free |
| `HASTE_SPEED_MULT` / `SLOW_SPEED_MULT` | 0.5 / 2.0 | Delay multipliers |
| `DEF_K` | 100 | Defense mitigation constant |
| `VARIANCE_MIN_PCT` / `VARIANCE_MAX_PCT` | 92 / 108 | Damage roll range (uniform, integer percent) |
| `CRIT_RATIO` | 2/1 | Critical multiplier |
| `CRIT_BASE_PCT` / `CRIT_MAX_PCT` | 4 / 50 | Crit chance base and ceiling |
| `HIT_MIN_PCT` / `HIT_MAX_PCT` | 5 / 100 | Hit chance bounds |
| `DARKNESS_HIT_MULT` | 0.2 | Darkness penalty on physical hit chance |
| `BARRIER_RATIO` | 1/2 | Protect (physical) / Shell (magical) |
| `STAT_BREAK_MULT` | 0.5 | Power Break / Magic Break (result floored) |
| `DAMAGE_CAP` / `DAMAGE_CAP_BROKEN` | 9999 / 99999 | Per-hit cap; the "Unfettered" equipment ability lifts it |
| `POISON_PCT` / `REGEN_PCT` | 0.10 / 0.08 | Of max HP, at the end of own turn |
| `BERSERK_STR_RATIO` | 3/2 | Berserk strength multiplier (after Power Break, floored) |
| `CONFUSE_ALLY_PCT` | 50 | Chance a Confused unit turns on its own side |
| `REVIVE_MIN_HP` / `PCT` | 1 / 100 | Revive floor; percent base for item and threshold math |
| `DELAY_STACK_DIVISOR` / `DELAY_STACK_MAX_STEPS` | 2 / 16 | Delay diminishing returns |
| `ESCAPE_BASE_PCT`, `ESCAPE_AGI_FACTOR`, `ESCAPE_MIN_PCT`, `ESCAPE_MAX_PCT` | 50, 2, 10, 95 | Escape |
| `OPENING_BASE_PCT`, `OPENING_AGI_FACTOR`, `OPENING_MIN_PCT`, `OPENING_MAX_PCT` | 8, 1, 2, 25 | Preemptive / ambush chance (§ Openings) |
| `OPENING_LEAD_TICKS` | 1 | How far the side caught out waits past the other side's last opening tick |

Element affinity multipliers (as ratios): normal 1/1, weak 3/2, resist 1/2, immune 0/1, absorb −1/1 (heals).

## Time (CTB)

**Base delay**: ticks between turns at rank 1.
```
base_delay(agi) = max(MIN_DELAY, ceil(DELAY_K / (max(agi, 0) + DELAY_OFFSET)))
```
Examples: agi 0 → 267, 10 → 100, 22 → 58, 255 → 7.

**Action delay**: applied after acting; `rank` comes from the skill (1 = very fast, 8 = very slow).
```
action_delay(agi, rank, speed) = max(MIN_DELAY, round(base_delay(agi) × rank × speed))
speed = (Haste ? 0.5 : 1) × (Slow ? 2 : 1)     # Haste and Slow are mutually exclusive in practice
```
Examples: agi 10, rank 3 → 300; with Haste → 150; with Slow → 600; rank 2 → 200.

**Initial ticks**: at battle start; `roll` is uniform in `[0, base_delay(agi)]` from the battle RNG.
```
initial_ticks(agi, roll) = max(0, base_delay(agi) × INITIAL_RANK − roll)
```
Examples: agi 10: roll 0 → 300, roll 100 → 200. A preemptive or ambush opening then moves one side's ticks (§ Openings).

**Turn order**: the lowest `next_time` acts. Ties go to higher agility, then to roster order (party slots first, then enemies in encounter order). After acting: `next_time = now + action_delay(...)`.

**Delay** (skills with `delay_ranks`, and delay items): adds `delay_push` ticks to the target's `next_time`, with diminishing returns so no foe can be held forever. `prior` counts the delays the target already took since its last own turn (acted or lost); acting resets it to 0, and so does rejoining the timeline after a KO or stone (revive, petrify cure, or swapping in for a fallen member). A swap-in that takes over a living member's slot takes over its count too, because it also inherits that slot's delayed `next_time`: a fresh count would let the same slot be pushed back again at full strength. A `delay_immune` enemy (`enemies.json`, for bosses) takes 0 and its count doesn't grow.
```
delay_push(agi, ranks, prior, immune) = immune ? 0 : floor(base_delay(agi) × ranks ÷ 2^min(prior, 16))
```
Examples: agi 10 (base 100), 2 ranks: 200, then 100, then 50 before it acts; 1 rank with prior 3 → 12; immune → 0. The preview applies the same count.

**Stop / Sleep**: the affected unit's turns are consumed without acting (`next_time += action_delay(agi, DEFAULT_RANK, speed)`). Durations count down on those lost turns, but **Poison and Regen do not tick on lost turns**. Sleep also ends when the unit takes damage. If every living combatant is losing turns for 1000 consecutive turns (only possible with "until cured" durations everywhere), the battle ends as a defeat. The validator forbids −1 durations for Stop and Sleep in data.

**Haste / Slow on another unit** changes its *future* delays only. Its already-scheduled `next_time` is not rescaled. Self-applied Haste/Slow affects the delay of the very action that applied it, because statuses resolve before the actor's delay.

**Status durations** are measured in the affected unit's *own* turns and tick down at the end of each own turn (−1 = until cured).

**Timeline preview** assumes every future action uses `DEFAULT_RANK`. Timed statuses (Haste, Slow, Stop, Sleep, Doom) count down per simulated own turn exactly as in play, so a 16-turn preview matches actual play whenever every action is rank 3 and nothing new is inflicted. The candidate action's rank, delay push, and any time statuses it inflicts (assumed to land) are applied exactly. A Doomed unit's entries carry its countdown (`TurnEntry.doom`), and no entry follows the one showing 1. A candidate that inflicts Petrify removes its target from the preview. A candidate that would deal HP damage to a **sleeping** target (a physical or magical hit through a non-immune, non-absorbing affinity, a heal on a Zombie, or a damage item) wakes it in the preview, before any status the action adds, exactly as in play (assuming the hit lands). A candidate aimed at a Reflect unit is previewed on the unit it will really bounce to.

**Foe tempo** (M3-CMB-02, ADR 0038; this refines the paragraph above for foes): a foe's predicted turn, or a Berserk/Confused one, uses the rank of the skill its AI will pick (`EnemyAI.predicted_skill`: the first rule that holds, with `turn_mod` counted ahead; of its options, the lowest rank). Party turns stay at `DEFAULT_RANK`. That skill's delay push is applied to every foe of the actor for an all-foes skill, or to the only one left for a single-foe one (assumed to land). No battle RNG is drawn.

## Damage

**Damage**: shared by physical and magical, exact in integers.
```
num = power × (stat + level) × DEF_K × variance_pct
den = (DEF_K + max(def, 0)) × 100
  physical: stat = strength (Power Break: floor(strength × 0.5)), def = defense (0 under Armor Break)
  magical:  stat = magic (Magic Break: floor(magic × 0.5)),       def = magic_defense (0 under Mental Break)
level: heroes = the one fixed hero level (characters.json, 5 for every hero; ADR 0012), never raised in play
       enemies = their data level, a tuning tier
if crit:    num ×= 2                       # physical only
if barrier: den ×= 2                       # Protect vs physical, Shell vs magical
num ×= el_num; den ×= el_den               # element ratio for the target's affinity
final = clamp(num ÷ den, −cap, cap)        # ÷ truncates toward zero: floor for damage, ceil for absorb
cap = 9999, or 99999 with Unfettered
```
Example: power 8, strength 16, level 5, defense 10, variance 100 → 1,680,000 ÷ 11,000 = 152. Crit 305, Protect 76, weak 229, resist 76, immune 0, absorb −152 (heals 152). Exactness check: power 7, stat 5, level 5, def 5, variance 93 → 651,000 ÷ 10,500 = **62** (a float pipeline gives 61).

**Healing**: ignores defense.
```
heal = min(cap, power × (magic + level) × variance_pct ÷ 100)       # magic is Magic-Break-adjusted
```
Examples: power 10, magic 18, level 5: variance 100 → 230; variance 93 → 213.

**Drain (M4-CMB-1001)**: a skill row with `drain_pct` heals its user by that share of the HP the hit took. HP lost
means after the cap and the target's floor; an absorbed or missed hit drains nothing.
```
drained = floor(hp_lost × drain_pct ÷ 100)        # through restore_hp: a Zombie user is harmed instead
```
Example: a hit takes 152 HP at drain_pct 50 → 76; 7 HP at 50 → 3.

**Hero level (ADR 0012).** Growth comes only from the Lattice. Every hero has the same fixed `level` (5), so in hero formulas it is a flat +5 "potency floor" on the attacking stat. The validator rejects heroes with different levels, the Lattice can't add `level`, and `BattleEngine` undoes any `party_modifier` change to it. Enemies keep `level` as a per-enemy tuning tier.

## Accuracy and criticals

```
hit_chance  = clamp(round((skill_accuracy + accuracy − evasion) × (Darkness ? 0.2 : 1)), 5, 100)   # physical only
crit_chance = clamp(CRIT_BASE_PCT + (luck − target_luck) / 2, 0, CRIT_MAX_PCT)                      # integer division (truncates toward zero)
```
Magic always hits (Reflect can redirect it: § Statuses). Rolls are `rng.randi_range(1, 100) ≤ chance`.
Examples: hit (95, 14, 14) → 95; (95, 10, 30) → 75; with Darkness → 19. Crit (18 vs 4) → 11; (4 vs 18) → 0.

## Over time

```
poison = max(1, ceil(max_hp × 0.10))     regen = max(1, ceil(max_hp × 0.08))
```
Both apply at the end of the unit's own turn. Examples: max HP 420 → poison 42, regen 34.

## Statuses (M1-CMB-02)

Every status in SPEC §6.8 is implemented. Durations are in the affected unit's own turns (−1 = until cured) unless a rule below says otherwise; defaults live in `statuses.json`. No status here adds a random roll beyond the ones named, and every roll goes through the battle RNG.

**Who is in control.** A unit under **Confuse** or **Berserk** (Confuse wins if both) is *not in control*: its turn is played by the engine (`run_enemy_turn()`, on either side) and the player gets no menu, swap, or escape on that turn. Stop and Sleep come first: a lost turn is lost. The unit uses its **basic attack**: `attack` if it knows it and can pay, otherwise its first affordable `physical` `single_foe` skill in skill-list order. With none, it loses the turn (a default-rank delay).

| Status | Default | Rule |
|---|---|---|
| **Petrify** | −1 (must be −1) | Stone. The unit leaves the timeline, can't be targeted, and **counts as KO** for victory, defeat, swap-in timing and the XP rule (`is_alive()` is false). HP is kept. Petrify clears every other status, and nothing new can be added. It never wears off (stone takes no turns, so the validator forbids a countdown). Only an item whose `cure` lists `petrify` reaches stone; the cured unit rejoins the timeline `action_delay(agi, DEFAULT_RANK, speed)` after now, like a revive. A petrified member can be swapped out like a KO'd one but can't come back in. |
| **Berserk** | −1 | Not in control. Basic attack on a uniformly random living foe, or on the provoker if Provoked. `strength_eff = floor(broken_strength × 3 / 2)`, where `broken_strength` already includes Power Break. Example: 16 → 24; 15 → 22; 16 under Power Break → 8 → 12. |
| **Confuse** | 3 | Not in control. Roll `randi_range(1, 100) ≤ CONFUSE_ALLY_PCT` (50): on success the target is a uniformly random living **ally other than itself**, otherwise a random living foe (if one side is empty, the other). Provoke is ignored. Taking **physical damage** (> 0) ends Confuse; magic does not. |
| **Doom** | 5 (must be ≥ 1) | A countdown. It drops by 1 at the end of each own turn, **lost turns included** (Stop can't stall it), and the unit is KO'd at the end of the turn that showed **1**, after Poison/Regen. So Doom *n* gives exactly *n* more turns. A Doom that fells the last enemy is a victory even on a lost turn. |
| **Zombie** | −1 | HP restoration from **heal skills and Regen** is dealt as damage of the same amount (no defense, no barrier, same cap), and can KO. Ordinary damage and Absorb are unchanged. A revive item may target a **living** Zombie and KOs it outright (§ Items). A KO clears Zombie, so a fallen ex-Zombie revives normally. |
| **Reflect** | 4 | A `magic: true` skill aimed at **one other** unit (`single_foe` or `single_ally`) that has Reflect lands instead on the **living unit with the lowest current HP on the other side from the reflector** (ties: field order, party slots then enemies in encounter order). It is deterministic, so the timeline preview is exact. A bounced spell is never bounced again (no chains), even onto another reflector. Physical skills, self-casts and group skills ignore Reflect. The hit reports `reflected_from`. |
| **Provoke** | 3 | Remembers its provoker (whoever's skill inflicted it). The provoked unit's `single_foe` skills **must** target the provoker: the engine rejects any other target with `provoked` (no MP or time spent), and enemy AI selectors are overridden. Group, ally and self skills are free. It ends early, at once, when the provoker is KO'd, petrified, or leaves the field. Re-provoking replaces the provoker. |

## Items (M1-CMB-06)

`BattleEngine.use_item(item_id, targets, items)` is a battle action like a skill. The item's effects come from `items.json` (`battle` block, run by `ItemBattleAction`). It ends the user's turn with the **item's rank**, consumes exactly one, and costs nothing if refused (`not_your_turn`, `unknown_item`, `no_item`, `no_valid_target`). Items are **fixed numbers**, not stat-scaled. They ignore Silence, Provoke and Reflect.

```
revive_hp(max_hp, hp_pct) = max(REVIVE_MIN_HP, floor(max_hp × hp_pct / 100))
item_damage(amount, aff)  = clamp(amount × el_num ÷ el_den, −DAMAGE_CAP, DAMAGE_CAP)   # ignores stats, defense, barriers
heal_hp / restore_mp      = the item's amount, clamped to max (heal goes through Zombie)
```
Examples: revive 25% of 420 → 105; of 301 → 75; of 3 → 1. Item damage 150 vs normal 150, weak 225, resist (151) 75, immune 0, absorb −150 (heals); 20000 → 9999.

- **Revive** targets only the KO'd (HP 0). The revived unit rejoins the timeline `action_delay(agi, DEFAULT_RANK, speed)` after now, the same rule as a swap-in for a KO'd member. Time never runs backwards.
- **Petrify:** a petrified ally is neither alive nor fallen. Only an item whose `cure` lists `petrify` reaches them (`ItemBattleAction.can_target` / `cures`); none ships yet. The cured unit rejoins `action_delay(agi, DEFAULT_RANK, speed)` after now, the revive rule (`speed` read after all the item's effects).
- **Zombie:** a revive item may target a *living* Zombie ally and KOs them outright (the hit reports `zombie_felled`). Healing items harm a Zombie by their amount.
- **Delay** items use `delay_push` (§ Time: diminishing returns, immunity), applied by the engine, not by `ItemBattleAction`. **add_status** items go through wards and the normal status rules. **Drag Net** is rank 3 (was 2): a 2-rank push for a full Attack-length turn, and a second net before the foe acts pushes half as far.
- **Preview:** `preview_item(item_id, target, items, count)` shows the item's rank, its delay push, the time statuses it adds, a revived ally rejoining, and a target the item downs leaving: a felled Zombie, or a Zombie a heal item KOs (`BattleEngine.item_downs`, which runs the effects in order on a `sim_copy`; items use no RNG, so it is exact). `item_defeats_party` uses the same rule over every target and the whole active party: it is a defeat only when nobody stands afterwards, so a group revive that fells the last Zombie and revives a fallen ally is not one, and a last foe felled first is a victory.
- `Formulas.revive_hp` / `item_damage` mirror `ItemBattleAction.revive_hp` / `fixed_damage` (Progression's reference implementation), and a test keeps them equal.

## Equipment in battle (M1-CMB-06)

`EquipmentEffects.apply_to` (Progression) leaves engine-facing data on each party combatant (`BattleCombatant.equipment()`, metadata key `equipment_effects`). The engine applies it as follows:

| Data | Rule |
|---|---|
| `attack_elements` | The **basic Attack** (`attack`, element `none`) hits with the listed element the target is **weakest to**, comparing element ratios exactly (weak > normal > resist > immune > absorb). Ties go to the first in slot order. Every other skill keeps its own element. The hit reports `element`. |
| `on_hit_statuses` | After a **landed physical hit** (any physical skill), while the target still stands, each `{id, chance, duration}` rolls `randi_range(1, 100) ≤ chance` on the battle RNG, in list order. This happens before the skill's own statuses. |
| `status_wards` | `add_status` refuses a warded status from any source (skills, items, strikes). |
| `low_hp_statuses` | On while `hp × 100 < max_hp × hp_below_pct`, and off once HP is at or above the threshold. The engine re-checks the field after every turn ends and after every swap. It removes only a status the equipment itself switched on, never the same status from a spell. If the status is removed while HP is still low, it comes back at the next check. A KO clears it. |

Equipment "always" auto-statuses are ordinary duration −1 statuses. **Decision:** a future dispel may strip them like any other status. They do not return, but low-HP ones do while the condition holds.

## Rewards (M1-CMB-06)

At victory:
- **Lume:** `currency_award()` = Σ every enemy's `currency` (`enemies.json`, petrified enemies included) × `currency_multiplier(credited_ids())`. The multiplier is a hook, `EquipmentEffects.currency_multiplier` (Full Net ×2), and ×1 when unset.
- **Drops:** `drop_awards()` is rolled **once** when the battle is won, on the battle RNG. For each enemy in encounter order, each `drops` entry `{item, chance}` adds one item when `randi_range(1, 100) ≤ chance`.

Escape and defeat award nothing. Sandbox values: Reef Crab 24 lume (Crab Carapace 50%, Salt Tonic 10%), Lantern Eel 20 (Eel Lantern 50%, Salt Tonic 10%), Gull Harrier 18 (Gull Quill 50%, Salt Tonic 10%), so 62 lume per sandbox win. Drownbell's ~300 lands with its encounter data.

**Paid in play (M2-CMB-07).** A live victory pays exactly these numbers: the lume through `Wallet.earn` (up to `currency_cap`) and each drop through `Inventory.add` (a full stack keeps what fits), in `BattleRewards.pay`. A live battle sets `currency_multiplier` from the party's equipped gear (`BattleVitals.live_gear`), so Full Net doubles in play as it does in the simulator. A new game opens with `starting_currency` lume (items.json `rules`, 100). No formula changed.

## Openings (M1-CMB-03)

SPEC §6.1. A battle opens **normal**, **preemptive** (the party moves first) or **ambush** (the enemies move first). `BattleOpening` (`game/battle/battle_opening.gd`) holds the rules.

**Which opening.** An encounter may fix it with `"opening"` in `encounters.json` (`normal`, `preemptive`, `ambush`, or `roll`). Without the field, a `scripted` fight opens normally and any other fight rolls. A fixed opening draws nothing from the RNG. A rolled one draws **once**, after `setup()` and before the opening ticks, `roll = randi_range(1, 100)` on the battle RNG:
```
preemptive_chance = clamp(8 + round((mean party agi − mean enemy agi) × 1), 2, 25)
ambush_chance     = clamp(8 + round((mean enemy agi − mean party agi) × 1), 2, 25)
roll ≤ preemptive_chance                     → preemptive
roll ≤ preemptive_chance + ambush_chance     → ambush
otherwise                                    → normal
```
The means use the living active party and the living enemies, as for Escape. Only live battles roll (`BattleBestiary.attach`). Tests, capture fixtures and the balance simulator open normally unless they set `engine.opening`, so their seeds keep their turn orders.

**The ticks.** Every combatant first rolls its opening ticks exactly as in § Time (the same draws in the same order). Then the side caught out waits past the favored side:
```
opening_lead = max(latest opening tick on the favored side, 0) + OPENING_LEAD_TICKS
each living combatant on the side caught out: next_time += opening_lead
```
Every favored combatant therefore acts once before any of the other side, and the timeline shows it from the first turn. A fast favored combatant may act twice before the others do. Fallen combatants neither set the lead nor move, and if nobody on the favored side stands the opening changes nothing.

Examples: sandbox party Rhen (agi 22) and Asha (14), mean 18, against Reef Crab (8), Lantern Eel (14) and Gull Harrier (24), mean 15.33: preemptive 8 + round(2.67) = **11%**, ambush 8 + round(−2.67) = **5%**, normal 84%. Equal means give 8% each. A preemptive opening where Asha's opening tick of 240 is the party's latest gives a lead of 241, so a crab whose opening tick is 300 waits until 541.

## Escape

```
escape_chance = clamp(50 + round((mean party agi − mean enemy agi) × 2), 10, 95)
```
This uses the living active party and living enemies. A failed attempt costs the actor a `DEFAULT_RANK` turn. Scripted fights forbid escape.

## XP credit rule (SPEC §6.1)

Every party member who was **on the field at any point** in the battle (they started active or swapped in, even for zero turns) and is **alive at victory** receives the encounter's **full** XP total, with no split. Reserve members who never entered get nothing. Swapping is free, so a player can rotate every reserve through once to share XP. That is deliberate, the same convention the inspiring genre uses: it rewards using the whole party (pillar 4) at the cost of menu time, not battle time.

## Swell (M1-CMB-04)

SPEC §6.2. Each hero with a row in `game/data/battle/swell.json` (`heroes`) has a gauge of `0..SWELL_MAX` (100) and one fill **mode** at a time. A full gauge puts **Swell** on that hero's command menu; a technique empties it. `BattleSwell` (`game/battle/battle_swell.gd`) holds the rules, and the state sits on `BattleCombatant` (`swell`, `swell_mode`). No step adds a random roll.

| Name | Value | Meaning |
|---|---|---|
| `SWELL_MAX` | 100 | Gauge size (formulas.gd) |

**Gain from an HP share**: exact in integers. Any positive amount gives at least 1, and one share gives at most the whole gauge.
```
swell_gain(amount, ref_max_hp, rate) = amount ≤ 0 or rate ≤ 0 ? 0 : clamp(amount × rate ÷ max(ref_max_hp, 1), 1, SWELL_MAX)
swell_fill(value, gain)              = clamp(value + gain, 0, SWELL_MAX)
```
`rate` is points per whole max HP, so a rate of 120 fills the gauge after 100/120 of the reference max HP.

**Modes** (data: `swell.json` `modes`; each has a `trigger` and either a `rate` or `flat` points per event):

| Mode | Trigger | Number | Fills when | Starts |
|---|---|---|---|---|
| **Ballast** | `damage_taken` | rate 120 | the owner loses HP to a hit (`ref` = the owner's max HP) | unlocked (default) |
| **Wake** | `damage_dealt` | rate 50 | the owner's action takes HP from a foe (`ref` = that foe's max HP; skills and damage items) | unlocked |
| **Tether** | `ally_hurt` | rate 60 | another **active, living** party member loses HP to a hit (`ref` = that ally's max HP) | locked |
| **Salve** | `heal_item` | flat 20 | the owner uses an item that restores HP or revives (once per use) | locked |

- Only action hits count (`ActionResult.hits` with `amount > 0`, through `BattleEngine.action_resolved`). A miss or a heal feeds no damage mode, and Poison, Regen and Doom ticks feed none. Reserve members gain nothing. A KO'd owner keeps its points.
- **A technique feeds no gauge**, its own or anyone's.
- Changing mode keeps the points. `set_mode` takes only unlocked modes; `unlock_mode` is the hook for unlocking through play (SPEC §6.2).
- **The gauge carries** (M2-ARC-01, save v6): it ends a won or escaped battle where it stood and starts the next one there, and so does the mode. A defeat carries nothing (play resumes from the last save). A save shrine's rest fills HP and MP but leaves gauges and modes alone: a rest is not a battle.

**Unlocks** (M2-CMB-01; data: `swell.json` `unlocks`). Each rule counts one event, a mode trigger from the table above, every time it happens to a hero with a Swell, and only while that hero uses the rule's `while_mode` when it names one. At its count the rule unlocks its mode for the whole party (`BattleSwell.unlock_mode`, which emits `mode_unlocked`). Counts and unlocks are saved (`GameStateData.swell`). A mode that starts locked must have a rule (validate_data).

| Rule | Unlocks | Counts | While | Count |
|---|---|---|---|---|
| `tether_from_ballast` | **Tether** | a hit that takes HP from the hero (`damage_taken`) | Ballast | 40 |
| `salve_from_items` | **Salve** | the hero uses an item that restores HP or revives (`heal_item`) | any mode | 5 |

Bearing blows yourself teaches you to feel your allies', and five healing items teach the gauge to answer care. The counts are first guesses: tune them against the slice's encounter count once it is playable. **Tether's 40 (M2-NIT-03; it was 12).** The 12 was chosen when only Rhen had a Swell: about 2 counted hits per sandbox fight for a careful player, so about six fights. With all four heroes counting, the same fights give 6 to 7 hits (smart 7.1, role answer 6.6, lowest HP 6.1, measured over 300 seeds), and 12 unlocked Tether in the second fight. 40 restores about six fights (5.6 to 6.6 by policy; a masher, hit 10 times a fight, gets there in four). `ally_hurt` counts once per living active ally with a Swell, as Tether fills.

Examples: Ballast, 95 of 420 HP lost → 27 (27.1 floors). Wake, 152 dealt to a 380 HP foe → 20. Tether, an ally loses 95 of 300 → 19. 1 HP lost at rate 120 on 420 → 1. Gauge 90 + 27 → 100.

**Techniques.** A technique is a `skills.json` row marked `"swell": true` and listed under its hero in `swell.json`. It is not learned, costs no MP, and is otherwise played exactly as its row (targets, Provoke, Reflect, Silence for `magic` rows, rank). `BattleSwell.perform(technique, targets, input_result)` refuses at no cost with `swell_not_full`, `unknown_technique`, `swell_cancelled`, `not_your_turn`, `auto_turn` or `battle_over`. On success the gauge goes to 0 and the turn ends.

**Input bonus.** Each hero's technique takes a short interactive input (SPEC §6.2), and the engine receives only its result, `{cancelled, grades}`:
```
bonus_pct            = Σ grade_bonus[grade] over the first `beats` grades      # unknown grades earn 0
swell_power(p, bonus) = floor(p × (100 + max(bonus, 0)) / 100)
```
The scaled power goes into the normal damage formula (§ Damage).

**Rhen: the timing ring** (`timing_ring`, `SwellTimingRing`). After a 0.6 s lead-in, the lamp flares 3 times, one beat every 0.8 s, peaking at 0.7 of each beat. The whole input lasts at most 3.0 s. The player presses once per flare:

| Grade | Distance from the peak | Bonus |
|---|---|---|
| perfect | ≤ 0.06 s | +30% |
| good | ≤ 0.15 s | +15% |
| miss | further, or no press before the beat ends | 0 |

The first press in a beat is the one that counts, and a press before the beat opens is ignored. The input can be **canceled only before the first grade**, so it cannot be retried until it goes well; canceling costs nothing. **Lamp Dive** (power 12, rank 2, physical, single foe, accuracy 100): perfect ×3 → power 22 (12 × 190 / 100 = 22.8), perfect + good + miss → 17, all miss → 12. From Rhen (strength 16, level 5) on the sandbox Reef Crab (defense 40, 380 HP) at variance 100: a perfect Lamp Dive deals 330, an all-miss one 180, and a plain Attack 120.

**The other heroes' inputs** (M2-CMB-01; `SwellInput` subclasses, Node-free like the ring). Every input shares the ring's rules: one grade per step, a step is never retried, cancel only before the first grade. Each kind has its own grade names. **Played at good, every input earns +45%, and played perfectly +90%** (all missed: 0), so no hero's Swell is worth more for being easier to read (a test checks the live data). Every input lasts at most 5 s (validate_data).

*Asha: the verse chant* (`chant`, `SwellChant`). After a 0.6 s lead-in, five notes follow a phrase of the Hush: up at 0.0 s, up at 0.5, left at 0.9, down at 1.3 and right at 2.0 (after the lead-in; at most 2.75 s in all). Press each note's direction on its note. A press before the note's window opens is ignored, and any other direction in the window is a miss.

| Grade | Distance from the note | Bonus |
|---|---|---|
| perfect | ≤ 0.06 s, right button | +18% |
| good | ≤ 0.15 s, right button | +9% |
| miss | wrong button, or no press before the window closes | 0 |

*Toma: the tide brace* (`brace`, `SwellBrace`). Hold Confirm through three blows (0.4, 1.0 and 1.6 s after a 0.6 s lead-in) and let go on the counter at 2.3 s (at most 3.05 s in all). Letting go early turns the blows still to come into misses and is graded against the counter like any release. A release during the lead-in only lets go and grades nothing, so the tap that chose the technique cannot spoil the brace; the battle HUD also starts the hold when that Confirm is still held as the brace opens (M2-UI-03, from M2-NIT-03).

| Grade | When | Bonus |
|---|---|---|
| braced | a blow lands while Confirm is held | +10% each |
| perfect | released ≤ 0.06 s from the counter | +60% |
| good | released ≤ 0.15 s from the counter | +15% |
| miss | a blow unbraced, or a release further off (or none) | 0 |

*Kerrid: the weighted swing* (`weighted_swing`, a `brace` row, M3-C05-06). One long charge: hold Confirm as the cleaver coils (one blow, graded at 1.1 s after a 0.6 s lead-in) and let go on the count at 2.4 s (at most 3.15 s in all). It is the brace's rules with one blow, so letting go early loses the coil. Grades: braced +30%, perfect +60%, good +15%, so +45% at good and +90% perfect.

*Liss: the reel-stop* (`reel_stop`, a `timing_ring` row, M3-C06-05). Stop three parts reels, one per beat. After a 0.6 s lead-in the beats come every 0.7 s, peaking at 0.65 of each beat (at most 2.7 s in all). The ring's windows and grades apply: perfect +30%, good +15% per reel.

*Ysolde: the glyph trace* (`glyph`, `SwellGlyph`). After a 0.6 s lead-in, trace five strokes in order (down, right, up, right, down) with the directions within 3.0 s. No beat: a stroke counts when it is made. A clean trace finished within 2.0 s of the lead-in earns *swift*.

| Grade | When | Bonus |
|---|---|---|
| traced | the stroke the glyph asks for next | +9% each |
| swift | after the last stroke: no miss, within 2.0 s | +45% |
| miss | a wrong stroke, strokes left when the window closes, or a slow or flawed trace (the swift grade) | 0 |

**Their techniques** (`skills.json`, `"swell": true`, no MP, rank 3):

| Hero | Technique | Row | Played at good | Played perfectly |
|---|---|---|---|---|
| Asha | **Shallows Verse** | heal, power 4, every other active ally (`all_other_allies`: never Asha herself), magic (Silence blocks it) | power 5 | power 7 |
| Toma | **Return Tide** | physical, power 14, one foe, accuracy 100 | power 20 | power 26 |
| Ysolde | **Written Light** | magical, power 10, every foe, no element, magic | power 14 | power 19 |
| Kerrid | **The Long Hold** | physical, power 14, one foe, accuracy 100 (M3-C05-06) | power 20 | power 26 |
| Liss | **Three-Reel Charge** | physical, power 9, every foe, accuracy 100, pushes each foe 1 rank down the timeline, not magic (M3-C06-05) | power 13 | power 17 |

(`swell_power`: 4 × 145 / 100 = 5.8 → 5; 14 × 190 / 100 = 26.6 → 26; 9 × 145 / 100 = 13.05 → 13.) `test_formulas.gd` pins every row of this table against `skills.json`.

**The Verse is a song for the others (M2-CMB-02).** Shallows Verse reaches every living active ally but the singer (target `all_other_allies`). Ballast fills when its owner is nearly down, so a Verse that healed Asha too was a second life for her whenever her gauge filled. Per ally the numbers are unchanged: 92 missed, 115 at good and 161 perfect, against a Chorus Mend's 138 (which still heals Asha). With nobody else standing the Verse has no target: it is refused at no cost, and the Swell page greys it out.

**Shallows Verse against Chorus Mend** (M2-NIT-03; the Verse was power 12). Chorus Mend heals every ally at power 6 for 14 MP and rank 4. From Asha (magic 18, level 5) at variance 100, Chorus Mend heals 138. The Verse heals 92 when missed and 115 at good, both less than a Chorus Mend. Only a perfect chant (161) beats it. At power 12 the Verse healed 391 at good, nearly three Chorus Mends for free, and it was the one Swell a masher could not lose with (balance_report.md, 2026-10-23 M2-NIT-03). The free song saves the 14 MP and a rank, and a well-sung one is the better heal, so the input still decides.

**In the simulator** a suite's `swell` quality plays every input at miss, good or perfect (`SwellInput.scripted_result`); balance_targets.md has the policy rules and balance_report.md the effect (2026-10-23).

**Timing assist (M2-UI-01, an accessibility setting; appended by UI, for Combat to confirm).** The `timing_assist` setting (`game/data/ui/accessibility.json`, `UiSettings.timing_input`) changes the input *row* before the input is built (`SwellInput.create`), for every kind. The grading code and the bonus tables stay the same, and no RNG is involved.

- `off` (the default) changes nothing.
- `wide` multiplies the windows by `window_scale` 1.5, then clamps each kind so it still passes the validator. A clamped window still cannot overlap its neighbour or leave its beat.
- `auto` sets `assist_floor: "good"`. Every kind grades through `SwellInput._record`, so a step that would grade a miss (unpressed, mistimed, a wrong button) records the grade that step earns when played at good (`scripted_grades("good")`).

| Kind | `wide` | `auto` (all steps missed) |
|---|---|---|
| ring (Rhen) | `perfect_sec` 0.09, `good_sec` 0.225, the window kept inside its beat: good ≤ min(peak, beat − peak), late edge 0.785 s of 0.8 | good ×3: +45%, Lamp Dive power 17 |
| chant (Asha) | perfect 0.09; good min(0.225, half the closest note gap 0.4) = 0.2, so the windows never overlap | good ×5: +45% |
| brace (Toma) | perfect 0.09, good 0.225; good stays < `counter_at` − the last impact (0.7) − `edge_margin_sec` 0.01 | braced ×3, then good: +45% |
| glyph (Ysolde) | `window_sec` min(3.0 × 1.5, `max_duration_sec` 5.0 − lead-in 0.6) = 4.4; `swift_sec` stays 2.0 | traced ×5, no swift: +45% |

- Under `auto` the worst result is the "played at good" +45% for every hero, and the best is still +90% (`perfect` and `swift` are never handed out).
- Swift asks for a clean trace *as played* (`raw_misses == 0`), so the assist never earns it.
- `max_step_sec` (0.05) stays within each kind's tightest window under every option.

## Vowbound (M2-CMB-04)

SPEC §6.3: a called Vowbound replaces the whole active party and **grows with its caller's stats** (Asha, the Cantor, for every Vowbound so far). `BattleVowbound` (`game/battle/battle_vowbound.gd`) holds the rules; the rows are `game/data/battle/vowbound.json`. No step adds a random roll. The turn rules are in [battle_ctb.md § Vowbound](battle_ctb.md).

**Stats.** At its first call in a battle, every stat but level is built from the row's `base` and `scale_pct` and the caller's same stat as it stands in battle (Lattice and gear included; the caller's current HP, MP and statuses don't count). Its level is the caller's. It enters at full HP and MP.
```
vowbound_stat(base, caller_stat, scale_pct) = base + caller_stat × scale_pct ÷ 100
```
(Negative inputs count as 0.) `hp` and `mp` scale from the caller's **max** HP and MP.

**The call's cost.** Calling takes no time at once: the Vowbound acts on the caller's turn. But the call is the caller's action, so the caller's end of turn runs at the moment of the call (ADR 0027 A3): Poison and Regen, the status countdown and Doom, exactly once per call. Only its next turn waits: when the party comes back, the caller waits `action_delay(caller agility, call_rank, its speed)` from that moment, and every other member waits the ticks it had left when it stood down. Ilun's `call_rank` is 3 (`DEFAULT_RANK`). Without this cost, a 1 HP Ilun lifted a masher from 8.7% to 28.7% on the sandbox: a free action that soaks an enemy turn. With it, a 1 HP Ilun gives 16.4% (battle_ctb.md § Vowbound has the probe).

Worked example, **Ilun** from Asha at level 5 with no Lattice gains (HP 300, MP 60, STR 6, MAG 18, DEF 6, MDF 14, AGI 14, ACC 8, EVA 10, LCK 12):

| Stat | Base | Scale | Ilun |
|---|---|---|---|
| HP | 60 | 100% | 60 + 300 = **360** |
| MP | 10 | 50% | 10 + 30 = **40** |
| STR | 4 | 50% | 4 + 3 = **7** |
| MAG | 4 | 100% | 4 + 18 = **22** |
| DEF / MDF | 14 / 14 | 100% | **20 / 28** |
| AGI | 4 | 50% | 4 + 7 = **11** |
| ACC / EVA / LCK | 4 / 2 / 4 | 100% / 50% / 100% | **12 / 7 / 16** |

Ilun is a wall, not a hammer (vowbound.md §1: defensive water magic and a tidal shield): a little more HP than Asha but over three times her defense and twice her magic defense, a little more magic than hers, and slow. *Brine Lash* (water, power 10, 4 MP), *Tidal Ward* (Protect and Shell on himself, 6 MP) and Attack. He absorbs water and is weak to lightning, so the sandbox's Reef Crab, which also absorbs water, shrugs off his magic.

**His Swell.** The Vowbound's gauge (`0..SWELL_MAX`) fills from HP **it** loses to hits and from HP it **gains by absorbing** a hit's element (ADR 0027 A1): `swell_gain(amount, its max HP, swell.rate)` on either amount, the same formula as Ballast (§ Swell). For an absorb, the amount is the **rolled** absorb (the hit's `absorbed`, before the max-HP cap), so it counts at full HP too: Ilun is called at full HP, and a gauge fed only by the HP actually restored would leave him filling nothing in the flood. A heal does not count. Ilun's rate is 150, so he fills after losing (or drinking) two thirds of his max HP. Worked example: a water hit rolled at 90 heals him by up to 90 (nothing at full HP) and adds `90 × 150 ÷ 360` = 37 points either way. A full gauge unleashes its finisher (`swell.technique`, *Floodnet*: non-elemental, all foes, power 16, and it clears the flood field, A2), which has no interactive input, costs no MP and empties the gauge. Party gauges never see the Vowbound's hits, and its gauge does not carry between battles. **M2-CMB-06:** HP scale 100% and rate 150 are re-derived on these rules and kept. At them, the Vowbound masher lines measure 38.9% (heroes' Swell off, ceiling 40%) and 46.2% (Swell on, ceiling 50%), and the Drownbell's bands hold with the real call (role_answer 71.0%, smart 85.3%). The m2-slice branch's 60% and 220 were tuned for the HP-restored reading of A1, which was not kept.

## Not yet specified (owned by Combat, tracked in M1 tasks)

Equipment abilities that tilt the opening odds, steal formulas, a Petrify cure item, and Vowbound HP, MP and gauge carried between battles (M2).

## Progression

**Owned by Progression.** `game/progression/progression_formulas.gd` mirrors this section exactly, and `tests/unit/test_lattice_formulas.gd` has a test per formula with the worked examples below. Change all three in one commit and get it reviewed by Combat (SPEC §12.3). The battle `Formulas` class does not change for these. Board rules (move costs, Facets per activation) are data in `game/data/progression/facets.json`. See [lattice.md](lattice.md).

On this page, **movement points** are the Lattice currency spent to walk the board. They are not the battle `mp` stat.

| Name | Value | Meaning |
|---|---|---|
| `LP_BASE` | 30 | Lattice points (LP) for one movement point, early on |
| `LP_GROWTH` | 5 | Extra LP per point after each `LP_STEP` points earned |
| `LP_STEP` | 10 | Movement points earned per threshold step |
| `MOVEMENT_POINT_CAP` | 99 | Most movement points a character can bank |

**LP gain**: a character earns LP equal to the XP the battle credits them under the XP credit rule above. They must have been on the field at some point and be alive at victory.
```
lp_gain(credited_xp) = max(credited_xp, 0)
```
Example: the sandbox reef encounter credits 105 XP, so the character gains 105 LP.

**Threshold**: LP needed for the next movement point. It depends on how many points the character has earned over the whole game (`earned`), not on what they have banked.
```
lp_threshold(earned) = LP_BASE + LP_GROWTH × floor(max(earned, 0) / LP_STEP)
```
Examples: earned 0 → 30, 9 → 30, 10 → 35, 25 → 40.

**Conversion**: after each battle, pooled LP converts into points one at a time. The threshold is re-read after every point, and conversion stops when the bank is full (`room = MOVEMENT_POINT_CAP − banked`).
```
convert_lp(pool, earned, room):
    gained = 0
    while gained < room and pool ≥ lp_threshold(earned + gained):
        pool −= lp_threshold(earned + gained);  gained += 1
    → (gained, pool)
```
Examples: (105, 0, 99) → (3, 15). (70, 9, 99) → (2, 5), because the threshold rises from 30 to 35 after the first point. (29, 0, 99) → (0, 29). (105, 0, 1) → (1, 75). (105, 0, 0) → (0, 105).
LP is never lost: at the cap it keeps pooling and converts once the character spends points.

**Room**
```
movement_room(banked) = max(MOVEMENT_POINT_CAP − banked, 0)
```
Examples: 0 → 99, 98 → 1, 120 → 0.

**Pacing note.** An early three-enemy fight gives about 3 points. The first section's pre-gate area is about 16 nodes per hero, so it takes roughly five or six fights before the first Key Facet matters. This is tuned against the M1 sandbox numbers only; revisit it with the balancing simulator (M1-CMB-05).
