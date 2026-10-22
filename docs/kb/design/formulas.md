# Battle Formulas

**Source of truth.** `game/battle/formulas.gd` mirrors this file exactly, and `tests/unit/test_formulas.gd` has a test per formula with the worked examples below. Change all three in one commit, and get the change reviewed by Progression (SPEC §12.3).

Notation: `floor`, `ceil`, `round` as usual; `clamp(x, lo, hi)`. All stats are non-negative integers.

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
| `CRIT_MULT` | 2.0 | Critical multiplier |
| `CRIT_BASE_PCT` / `CRIT_MAX_PCT` | 4 / 50 | Crit chance base and ceiling |
| `HIT_MIN_PCT` / `HIT_MAX_PCT` | 5 / 100 | Hit chance bounds |
| `DARKNESS_HIT_MULT` | 0.2 | Darkness penalty on physical hit chance |
| `BARRIER_MULT` | 0.5 | Protect (physical) / Shell (magical) |
| `STAT_BREAK_MULT` | 0.5 | Power Break / Magic Break |
| `DAMAGE_CAP` / `DAMAGE_CAP_BROKEN` | 9999 / 99999 | Per-hit cap; the "Unfettered" equipment ability lifts it |
| `POISON_PCT` / `REGEN_PCT` | 0.10 / 0.08 | Of max HP, at the end of own turn |
| `ESCAPE_BASE_PCT`, `ESCAPE_AGI_FACTOR`, `ESCAPE_MIN_PCT`, `ESCAPE_MAX_PCT` | 50, 2, 10, 95 | Escape |

Element affinity multipliers: normal 1.0, weak 1.5, resist 0.5, immune 0.0, absorb −1.0 (heals).

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
Examples: agi 10: roll 0 → 300, roll 100 → 200. (Ambush and preemptive modifiers come in M1-CMB-03.)

**Turn order**: the lowest `next_time` acts. Ties go to higher agility, then to roster order (party slots first, then enemies in encounter order). After acting: `next_time = now + action_delay(...)`.

**Delay attacks**: a hit with `delay_ranks = n` adds `base_delay(target.agi) × n` to the target's `next_time`.

**Stop / Sleep**: the affected unit's turns are consumed without acting (`next_time += action_delay(agi, DEFAULT_RANK, speed)`). Durations count down on those lost turns. Sleep also ends when the unit takes damage.

**Status durations** are measured in the affected unit's *own* turns and tick down at the end of each own turn (−1 = until cured).

**Timeline preview** assumes every future action uses `DEFAULT_RANK` and that statuses don't expire inside the preview window. The candidate action's rank and delay are applied exactly.

## Damage

**Raw damage**: shared by physical and magical.
```
raw = power × (stat + level) × DEF_K / (DEF_K + max(def, 0)) × variance_pct / 100
  physical: stat = strength (halved by Power Break), def = defense (0 under Armor Break)
  magical:  stat = magic (halved by Magic Break),   def = magic_defense (0 under Mental Break)
```
Example: power 8, strength 16, level 5, defense 10, variance 100 → 8 × 21 × 100/110 = 152.727…

**Final damage**
```
d = raw
if crit:    d ×= CRIT_MULT              # physical only
if barrier: d ×= BARRIER_MULT           # Protect vs physical, Shell vs magical
d ×= element_mult[target affinity for the skill's element]
final = clamp(d ≥ 0 ? floor(d) : ceil(d), −cap, cap)     cap = 9999, or 99999 with Unfettered
```
Examples from raw 152.727: normal 152, crit 305, Protect 76, weak 229, resist 76, immune 0, absorb −152 (heals 152).

**Healing**: ignores defense.
```
heal = min(cap, floor(power × (magic + level) × variance_pct / 100))
```
Example: power 10, magic 18, level 5, variance 100 → 230.

## Accuracy and criticals

```
hit_chance  = clamp(round((skill_accuracy + accuracy − evasion) × (Darkness ? 0.2 : 1)), 5, 100)   # physical only
crit_chance = clamp(CRIT_BASE_PCT + (luck − target_luck) / 2, 0, CRIT_MAX_PCT)                      # integer division (truncates toward zero)
```
Magic always hits (Reflect will come with M1-CMB-02). Rolls are `rng.randi_range(1, 100) ≤ chance`.
Examples: hit (95, 14, 14) → 95; (95, 10, 30) → 75; with Darkness → 19. Crit (18 vs 4) → 11; (4 vs 18) → 0.

## Over time

```
poison = max(1, ceil(max_hp × 0.10))     regen = max(1, ceil(max_hp × 0.08))
```
Both apply at the end of the unit's own turn. Examples: max HP 420 → poison 42, regen 34.

## Escape

```
escape_chance = clamp(50 + round((mean party agi − mean enemy agi) × 2), 10, 95)
```
This uses the living active party and living enemies. A failed attempt costs the actor a `DEFAULT_RANK` turn. Scripted fights forbid escape.

## XP credit rule (SPEC §6.1)

Every party member who was **on the field at any point** in the battle (they started active or swapped in) and is **alive at victory** receives the encounter's **full** XP total, with no split. Reserve members who never entered get nothing. This rewards swapping, which pillar 4 wants: swap a character in for one turn and they earn XP.

## Not yet specified (owned by Combat, tracked in M1 tasks)

Swell gauge fill rates (M1-CMB-04), Reflect, Berserk, Confuse, Doom, Zombie, Petrify, and Provoke behaviour (M1-CMB-02), steal and item formulas (Progression), and Vowbound stat scaling from Asha (M2).
