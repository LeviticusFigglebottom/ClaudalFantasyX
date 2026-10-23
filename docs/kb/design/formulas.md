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
- Changing mode keeps the points. `set_mode` takes only unlocked modes; `unlock_mode` is the hook for unlocking through play (SPEC §6.2). The unlock rules and saving the gauge between battles come in later tasks.

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

**Timing assist (M2-UI-01, an accessibility setting; appended by UI, for Combat to confirm).** The `timing_assist` setting (`game/data/ui/accessibility.json`, `UiSettings.timing_input`) changes the input *row* before the ring is built. The grading code and the bonus table stay the same, and no RNG is involved:

| Option | What changes | Rhen's ring |
|---|---|---|
| `off` (default) | nothing | perfect ≤ 0.06 s, good ≤ 0.15 s |
| `wide` | `perfect_sec` and `good_sec` × `window_scale` 1.5, then `good_sec` ≤ min(peak, beat − peak) and `perfect_sec` ≤ `good_sec`, so the window stays inside its beat (validator rule, M1-UI-05) | perfect ≤ 0.09 s, good ≤ 0.225 s (late edge 0.785 s of a 0.8 s beat) |
| `auto` | `assist_grade: "good"`: a miss (an unpressed beat or a mistimed press) counts as good; a press on the peak still earns perfect | all three beats left alone → good ×3, +45%, Lamp Dive power 17 |

`max_step_sec` (0.05) stays ≤ `perfect_sec` under every option, so a long frame still cannot move a press across a whole grade. The worst result with `auto` is +45% and the best is still +90%, so practice is still rewarded.

## Not yet specified (owned by Combat, tracked in M1 tasks)

Swell mode unlock rules and carrying gauges between battles (after M1-CMB-04), equipment abilities that tilt the opening odds, steal formulas, a Petrify cure item, and Vowbound stat scaling from Asha (M2).

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
