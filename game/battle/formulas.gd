class_name Formulas
extends RefCounted
## Every battle formula. Mirrors docs/kb/design/formulas.md EXACTLY; change both together
## and update tests/unit/test_formulas.gd. Constants here are the only tunable numbers
## allowed outside data files (they define the formulas themselves).
## Damage and healing use exact integer arithmetic (rational multipliers, one truncating
## division at the end) so an external simulator can reproduce them bit-for-bit.

const DELAY_K := 1600.0
const DELAY_OFFSET := 6.0
const DEFAULT_RANK := 3
const INITIAL_RANK := 3
const MIN_DELAY := 1

const HASTE_SPEED_MULT := 0.5
const SLOW_SPEED_MULT := 2.0

const DEF_K := 100
const VARIANCE_MIN_PCT := 92
const VARIANCE_MAX_PCT := 108
const CRIT_BASE_PCT := 4
const CRIT_MAX_PCT := 50
const HIT_MIN_PCT := 5
const HIT_MAX_PCT := 100
const DARKNESS_HIT_MULT := 0.2
const STAT_BREAK_MULT := 0.5

const DAMAGE_CAP := 9999
const DAMAGE_CAP_BROKEN := 99999

const ESCAPE_BASE_PCT := 50
const ESCAPE_AGI_FACTOR := 2
const ESCAPE_MIN_PCT := 10
const ESCAPE_MAX_PCT := 95

const POISON_PCT := 0.10
const REGEN_PCT := 0.08

## Berserk: strength x3/2 (exact in integers, floored). Confuse: chance a confused unit turns
## on its own side instead of the foe.
const BERSERK_STR_RATIO: Array[int] = [3, 2]
const CONFUSE_ALLY_PCT := 50

## Items (M1-CMB-06): revive HP is a percent of max HP, never below 1.
const REVIVE_MIN_HP := 1
## Delay diminishing returns: each earlier delay since the target's last turn divides the next.
const DELAY_STACK_DIVISOR := 2
const DELAY_STACK_MAX_STEPS := 16
const PCT := 100
## Swell (M1-CMB-04): a gauge holds 0..SWELL_MAX, and a full one unlocks the owner's techniques.
const SWELL_MAX := 100
## Openings (M1-CMB-03): the percent chance of a preemptive opening (an ambush mirrors it) at
## equal mean agility, the points it moves per point of mean agility difference, its bounds, and
## the ticks by which the side caught out waits past the other side's last opening turn.
const OPENING_BASE_PCT := 8
const OPENING_AGI_FACTOR := 1
const OPENING_MIN_PCT := 2
const OPENING_MAX_PCT := 25
const OPENING_LEAD_TICKS := 1

## Rational multipliers as [numerator, denominator].
const CRIT_RATIO: Array[int] = [2, 1]
const BARRIER_RATIO: Array[int] = [1, 2]
const ELEMENT_RATIO := {
	&"normal": [1, 1],
	&"weak": [3, 2],
	&"resist": [1, 2],
	&"immune": [0, 1],
	&"absorb": [-1, 1],
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


## Full damage pipeline, exact in integers. Returns a signed amount: negative means the
## target is healed (absorb). `barrier` is Protect for physical or Shell for magical.
## `variance_pct` is in [VARIANCE_MIN_PCT, VARIANCE_MAX_PCT].
static func damage(
	power: int,
	stat: int,
	level: int,
	defense: int,
	variance_pct: int,
	element_affinity: StringName,
	crit: bool,
	barrier: bool,
	break_cap: bool
) -> int:
	var num := power * (stat + level) * DEF_K * variance_pct
	var den := (DEF_K + maxi(defense, 0)) * 100
	if crit:
		num *= CRIT_RATIO[0]
		den *= CRIT_RATIO[1]
	if barrier:
		num *= BARRIER_RATIO[0]
		den *= BARRIER_RATIO[1]
	var el: Array = ELEMENT_RATIO.get(element_affinity, ELEMENT_RATIO[&"normal"])
	num *= int(el[0])
	den *= int(el[1])
	# GDScript integer division truncates toward zero: floor for damage, ceil for absorb.
	var cap := DAMAGE_CAP_BROKEN if break_cap else DAMAGE_CAP
	return clampi(num / den, -cap, cap)


## Healing ignores defense. Exact in integers.
static func heal_amount(power: int, magic: int, level: int, variance_pct: int, break_cap: bool) -> int:
	var cap := DAMAGE_CAP_BROKEN if break_cap else DAMAGE_CAP
	return mini(cap, power * (magic + level) * variance_pct / 100)


## M4-CMB-1001: the HP a drain skill gives back, a share of the HP its hit took. Exact in integers.
static func drain_heal(hp_lost: int, drain_pct: int) -> int:
	return maxi(0, hp_lost) * drain_pct / 100


## Percent chance for a physical action to hit.
static func hit_chance(skill_accuracy: int, accuracy: int, evasion: int, darkness: bool) -> int:
	var chance := float(skill_accuracy + accuracy - evasion)
	if darkness:
		chance *= DARKNESS_HIT_MULT
	return clampi(roundi(chance), HIT_MIN_PCT, HIT_MAX_PCT)


## Percent chance for a physical hit to be critical.
static func crit_chance(luck: int, target_luck: int) -> int:
	return clampi(CRIT_BASE_PCT + (luck - target_luck) / 2, 0, CRIT_MAX_PCT)


## Effective stat after Break statuses (Weakened/Dimmed halve; Sundered/Unmoored zero).
static func broken_stat(value: int, half_break: bool) -> int:
	return floori(value * STAT_BREAK_MULT) if half_break else value


## Ticks a delay effect adds: base_delay × ranks, halved for each delay the target already took
## since its last own turn (DELAY_STACK_DIVISOR per step, at most DELAY_STACK_MAX_STEPS), and 0
## for a delay-immune target.
static func delay_push(agility: int, ranks: int, prior: int, immune: bool = false) -> int:
	if immune or ranks <= 0:
		return 0
	var divisor := 1
	for i in mini(maxi(prior, 0), DELAY_STACK_MAX_STEPS):
		divisor *= DELAY_STACK_DIVISOR
	return base_delay(agility) * ranks / divisor


## HP a revive item restores: max(1, floor(max_hp × hp_pct / 100)).
static func revive_hp(max_hp: int, hp_pct: int) -> int:
	return maxi(REVIVE_MIN_HP, max_hp * hp_pct / PCT)


## Fixed item damage: ignores stats, defense and barriers; takes the element ratio of the
## target's affinity (absorb heals) and the per-hit cap. Signed like damage().
static func item_damage(amount: int, element_affinity: StringName) -> int:
	var el: Array = ELEMENT_RATIO.get(element_affinity, ELEMENT_RATIO[&"normal"])
	return clampi(amount * int(el[0]) / int(el[1]), -DAMAGE_CAP, DAMAGE_CAP)


## True if affinity `a` lets more damage through than `b` (weak > normal > resist > immune >
## absorb), comparing the element ratios exactly.
static func affinity_hurts_more(a: StringName, b: StringName) -> bool:
	var ra: Array = ELEMENT_RATIO.get(a, ELEMENT_RATIO[&"normal"])
	var rb: Array = ELEMENT_RATIO.get(b, ELEMENT_RATIO[&"normal"])
	return int(ra[0]) * int(rb[1]) > int(rb[0]) * int(ra[1])


## Berserk strength, applied after Weakened: floor(strength x 3/2).
static func berserk_strength(value: int) -> int:
	return value * BERSERK_STR_RATIO[0] / BERSERK_STR_RATIO[1]


static func poison_damage(max_hp: int) -> int:
	return maxi(1, ceili(max_hp * POISON_PCT))


static func regen_heal(max_hp: int) -> int:
	return maxi(1, ceili(max_hp * REGEN_PCT))


## Percent chance that an Escape attempt succeeds, from mean agility on each side.
static func escape_chance(party_mean_agility: float, enemy_mean_agility: float) -> int:
	var c := ESCAPE_BASE_PCT + roundi((party_mean_agility - enemy_mean_agility) * ESCAPE_AGI_FACTOR)
	return clampi(c, ESCAPE_MIN_PCT, ESCAPE_MAX_PCT)


## Swell points from an HP share (formulas.md § Swell): `amount` HP lost or dealt against the
## reference max HP, at a mode's `rate` (points per whole max HP, swell.json). Exact in integers;
## any positive amount gives at least 1 and one share at most SWELL_MAX.
static func swell_gain(amount: int, ref_max_hp: int, rate: int) -> int:
	if amount <= 0 or rate <= 0:
		return 0
	return clampi(amount * rate / maxi(ref_max_hp, 1), 1, SWELL_MAX)


## The gauge after gaining `gain` points: clamped to 0..SWELL_MAX.
static func swell_fill(value: int, gain: int) -> int:
	return clampi(value + gain, 0, SWELL_MAX)


## A technique's power after its input: floor(power x (100 + bonus_pct) / 100); a negative bonus
## counts as 0, so a botched input never makes a technique weaker than its base.
static func swell_power(power: int, bonus_pct: int) -> int:
	return power * (PCT + maxi(bonus_pct, 0)) / PCT


## A called Vowbound's stat (formulas.md § Vowbound, M2-CMB-04): its row's base plus its percent of
## the caller's same stat as it stands in battle, floor(caller_stat x scale_pct / 100).
static func vowbound_stat(base: int, caller_stat: int, scale_pct: int) -> int:
	return maxi(base, 0) + maxi(caller_stat, 0) * maxi(scale_pct, 0) / PCT


## Percent chance of a preemptive opening (the party moves first), from the mean agility of the
## living active party and of the enemies (formulas.md § Openings).
static func preemptive_chance(party_mean_agility: float, enemy_mean_agility: float) -> int:
	var c := OPENING_BASE_PCT + roundi((party_mean_agility - enemy_mean_agility) * OPENING_AGI_FACTOR)
	return clampi(c, OPENING_MIN_PCT, OPENING_MAX_PCT)


## Percent chance of an ambush (the enemies move first): the preemptive chance seen from their side.
static func ambush_chance(party_mean_agility: float, enemy_mean_agility: float) -> int:
	return preemptive_chance(enemy_mean_agility, party_mean_agility)


## Ticks added to every opening tick of the side caught out: past the favored side's latest
## opening tick, so each favored combatant acts once before any of them.
static func opening_lead(favored_latest_ticks: int) -> int:
	return maxi(favored_latest_ticks, 0) + OPENING_LEAD_TICKS
