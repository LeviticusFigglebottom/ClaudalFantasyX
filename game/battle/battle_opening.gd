class_name BattleOpening
extends RefCounted
## Preemptive and ambush openings (SPEC §6.1, M1-CMB-03; formulas.md § Openings). Static rules,
## headless and deterministic: the one roll uses the engine's seeded rng.
##
## An opening is chosen after BattleEngine.setup() and before begin(): set `engine.opening`,
## for live play from choose(engine). begin() rolls every combatant's opening ticks exactly as a
## normal opening does, then apply() pushes the side caught out past the other side's latest
## opening tick, so every favored combatant acts once before any of them. A normal opening
## changes nothing, and nothing rolls unless choose() is called, so tests, capture fixtures and
## the simulator keep their seeds' turn orders.
##
## Encounters may fix the opening with "opening" (encounters.json): one of OPENINGS, or ROLL.
## Without it a scripted fight opens normally and any other fight rolls.

const NORMAL := &"normal"
const PREEMPTIVE := &"preemptive"
const AMBUSH := &"ambush"
## Not an opening: the encounter's "opening" value that asks choose() to roll one.
const ROLL := &"roll"
const OPENINGS: Array[StringName] = [NORMAL, PREEMPTIVE, AMBUSH]
## The encounters.json field.
const KEY := "opening"
## Loc keys the HUD shows for an opening other than normal (none for a normal one).
const CAPTION_KEYS := {PREEMPTIVE: "HUD_OPENING_PREEMPTIVE", AMBUSH: "HUD_OPENING_AMBUSH"}


## What the encounter row asks for: one of OPENINGS, or ROLL. An unknown value opens normally
## (the validator rejects it).
static func setting(encounter: Dictionary) -> StringName:
	var fallback := NORMAL if bool(encounter.get("scripted", false)) else ROLL
	var asked := StringName(str(encounter.get(KEY, fallback)))
	return asked if asked == ROLL or OPENINGS.has(asked) else NORMAL


## The opening for the engine's encounter (call after setup()). A fixed opening uses no rng; a
## rolled one draws once, randi_range(1, 100): preemptive at or below its chance, an ambush
## within the next ambush-chance points, otherwise normal.
static func choose(engine: BattleEngine) -> StringName:
	var asked := setting(engine.db.encounters.get(engine.encounter_id, {}))
	if asked != ROLL:
		return asked
	var party_agi := mean_agility(engine.party_active)
	var enemy_agi := mean_agility(engine.enemies)
	return from_roll(
		engine.rng.randi_range(1, Formulas.PCT),
		Formulas.preemptive_chance(party_agi, enemy_agi),
		Formulas.ambush_chance(party_agi, enemy_agi)
	)


## The opening a roll of 1..100 gives for the two chances.
static func from_roll(roll: int, preemptive_pct: int, ambush_pct: int) -> StringName:
	if roll <= preemptive_pct:
		return PREEMPTIVE
	if roll <= preemptive_pct + ambush_pct:
		return AMBUSH
	return NORMAL


## Pushes the side caught out by Formulas.opening_lead past the favored side's latest opening
## tick. Only living combatants count and move (a fallen member takes no turns). Run by
## BattleEngine.begin() right after the opening ticks are rolled.
static func apply(opening: StringName, party: Array[BattleCombatant], enemies: Array[BattleCombatant]) -> void:
	if opening != PREEMPTIVE and opening != AMBUSH:
		return
	var favored := party if opening == PREEMPTIVE else enemies
	var caught := enemies if opening == PREEMPTIVE else party
	var latest := -1
	for c in favored:
		if c.is_alive():
			latest = maxi(latest, c.next_time)
	if latest < 0:
		return  # nobody on the favored side stands: there is nothing to go first
	var lead := Formulas.opening_lead(latest)
	for c in caught:
		if c.is_alive():
			c.next_time += lead


## Mean agility of the living combatants in `list` (0 when none stands), as for Escape.
static func mean_agility(list: Array[BattleCombatant]) -> float:
	var total := 0
	var n := 0
	for c in list:
		if c.is_alive():
			total += c.agility
			n += 1
	return float(total) / n if n > 0 else 0.0
