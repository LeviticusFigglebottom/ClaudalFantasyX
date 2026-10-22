class_name Formulas
extends RefCounted
## Every battle formula. Mirrors docs/kb/design/formulas.md EXACTLY; change both together
## and update tests/unit/test_formulas.gd. Constants here are the only tunable numbers
## allowed outside data files (they define the formulas themselves).

const DELAY_K := 1600.0
const DELAY_OFFSET := 6.0
const DEFAULT_RANK := 3
const INITIAL_RANK := 3
const MIN_DELAY := 1

const HASTE_SPEED_MULT := 0.5
const SLOW_SPEED_MULT := 2.0

const DEF_K := 100.0
const VARIANCE_MIN_PCT := 92
const VARIANCE_MAX_PCT := 108
const CRIT_MULT := 2.0
const CRIT_BASE_PCT := 4
const CRIT_MAX_PCT := 50
const HIT_MIN_PCT := 5
const HIT_MAX_PCT := 100
const DARKNESS_HIT_MULT := 0.2
const BARRIER_MULT := 0.5
const STAT_BREAK_MULT := 0.5

const DAMAGE_CAP := 9999
const DAMAGE_CAP_BROKEN := 99999

const ESCAPE_BASE_PCT := 50
const ESCAPE_AGI_FACTOR := 2
const ESCAPE_MIN_PCT := 10
const ESCAPE_MAX_PCT := 95

const POISON_PCT := 0.10
const REGEN_PCT := 0.08

const ELEMENT_MULT := {
	&"normal": 1.0,
	&"weak": 1.5,
	&"resist": 0.5,
	&"immune": 0.0,
	&"absorb": -1.0,
}


## Ticks between turns at rank 1 for a given agility.
static func base_delay(agility: int) -> int:
	return maxi(MIN_DELAY, ceili(DELAY_K / (float(maxi(agility, 0)) + DELAY_OFFSET)))


## Delay applied after an action: base_delay × rank × speed multiplier, at least MIN_DELAY.
static func action_delay(agility: int, rank: int, speed_mult: float = 1.0) -> int:
	return maxi(MIN_DELAY, roundi(base_delay(agility) * rank * speed_mult))


## Ticks before a combatant's first turn. `roll` is uniform in [0, base_delay(agility)].
static func initial_ticks(agility: int, roll: int) -> int:
	return maxi(0, base_delay(agility) * INITIAL_RANK - roll)


## Shared core of physical and magical damage. `variance_pct` is in [92, 108].
static func raw_damage(power: int, stat: int, level: int, defense: int, variance_pct: int) -> float:
	var mitigation := DEF_K / (DEF_K + float(maxi(defense, 0)))
	return float(power) * float(stat + level) * mitigation * float(variance_pct) / 100.0


## Full damage pipeline. Returns a signed amount: negative means the target is healed
## (absorb). `barrier` is Protect for physical or Shell for magical.
static func final_damage(raw: float, element_affinity: StringName, crit: bool, barrier: bool, break_cap: bool) -> int:
	var d := raw
	if crit:
		d *= CRIT_MULT
	if barrier:
		d *= BARRIER_MULT
	d *= float(ELEMENT_MULT.get(element_affinity, 1.0))
	var cap := DAMAGE_CAP_BROKEN if break_cap else DAMAGE_CAP
	return clampi(floori(d) if d >= 0.0 else ceili(d), -cap, cap)


## Healing ignores defense. `variance_pct` is in [92, 108].
static func heal_amount(power: int, magic: int, level: int, variance_pct: int, break_cap: bool) -> int:
	var cap := DAMAGE_CAP_BROKEN if break_cap else DAMAGE_CAP
	return mini(cap, floori(float(power) * float(magic + level) * float(variance_pct) / 100.0))


## Percent chance for a physical action to hit.
static func hit_chance(skill_accuracy: int, accuracy: int, evasion: int, darkness: bool) -> int:
	var chance := float(skill_accuracy + accuracy - evasion)
	if darkness:
		chance *= DARKNESS_HIT_MULT
	return clampi(roundi(chance), HIT_MIN_PCT, HIT_MAX_PCT)


## Percent chance for a physical hit to be critical.
static func crit_chance(luck: int, target_luck: int) -> int:
	return clampi(CRIT_BASE_PCT + (luck - target_luck) / 2, 0, CRIT_MAX_PCT)


## Effective stat after Break statuses (Power/Magic Break halve; Armor/Mental Break zero).
static func broken_stat(value: int, half_break: bool) -> int:
	return floori(value * STAT_BREAK_MULT) if half_break else value


static func poison_damage(max_hp: int) -> int:
	return maxi(1, ceili(max_hp * POISON_PCT))


static func regen_heal(max_hp: int) -> int:
	return maxi(1, ceili(max_hp * REGEN_PCT))


## Percent chance that an Escape attempt succeeds, from mean agility on each side.
static func escape_chance(party_mean_agility: float, enemy_mean_agility: float) -> int:
	var c := ESCAPE_BASE_PCT + roundi((party_mean_agility - enemy_mean_agility) * ESCAPE_AGI_FACTOR)
	return clampi(c, ESCAPE_MIN_PCT, ESCAPE_MAX_PCT)
