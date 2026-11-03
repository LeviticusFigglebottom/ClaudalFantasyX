class_name BattleSpoils
extends RefCounted
## Victory rewards (formulas.md § XP, § Rewards), split out of BattleEngine (M2-CMB-03). Static
## and headless; the engine keeps the public names (xp_awards, credited_ids, currency_award,
## drop_awards) and stores the drops it rolls once at victory.

## Outcomes that award spoils: a victory, and a set piece's scripted way out (M3-CMB-01). A foe that
## withdrew (BattleCombatant.withdrawn) was not felled and gives nothing.
const SPOILS_OUTCOMES: Array[StringName] = [BattleEngine.OUTCOME_VICTORY, BattleEngine.OUTCOME_SCRIPTED_ESCAPE]


## XP credit rule (docs/kb/design/formulas.md §XP): every party member who was on the field
## at any point and is alive at victory receives the encounter's full XP. No split.
static func xp_awards(engine: BattleEngine) -> Dictionary:
	var out: Dictionary = {}
	if not engine.outcome in SPOILS_OUTCOMES:
		return out
	var total := 0
	for e in engine.enemies:
		total += 0 if e.withdrawn else e.xp_reward
	for c in engine.party_active + engine.party_reserve:
		if c.participated and c.is_alive():
			out[c.id] = total
	return out


## M3-CMB-04 (the human's playtest, 2026-11-03): the party as it leaves the battle, for the saved
## vitals (BattleVitals.send_back), active then reserve. After a won fight (SPOILS_OUTCOMES) each
## member at HP 0 is replaced by a risen copy (risen_copy) at Formulas.victory_rise_hp; everyone
## else, and everyone after an escape, is the battle's own combatant. The battle's combatants are
## never changed, so the XP credit rule (alive at victory) still leaves the fallen out.
static func returning_party(engine: BattleEngine) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = []
	var won := engine.outcome in SPOILS_OUTCOMES
	for c in engine.party_active + engine.party_reserve:
		out.append(risen_copy(c) if won and c.hp <= 0 else c)
	return out


## A detached copy of fallen `c` standing at Formulas.victory_rise_hp, with what the saved vitals
## read kept: max HP, MP, statuses (a KO cleared them), and the Swell gauge and mode.
static func risen_copy(c: BattleCombatant) -> BattleCombatant:
	var r := c.sim_copy()
	r.name_key = c.name_key
	r.level = c.level
	r.hp = Formulas.victory_rise_hp(c.hp)
	r.swell = c.swell
	r.swell_mode = c.swell_mode
	return r


## Battle lume: the sum of every enemy's `currency`, times the engine's currency_multiplier hook
## for the credited party (x1 when unset). 0 unless victorious.
static func currency_award(engine: BattleEngine) -> int:
	if not engine.outcome in SPOILS_OUTCOMES:
		return 0
	var total := 0
	for e in engine.enemies:
		total += 0 if e.withdrawn else int(_row(engine, e).get("currency", 0))
	var mult := 1
	if engine.currency_multiplier.is_valid():
		mult = int(engine.currency_multiplier.call(engine.credited_ids()))
	return total * mult


## Drop rolls, once, at victory: for each enemy in encounter order, each `drops` entry
## {item, chance} rolls randi_range(1, 100) <= chance on the battle RNG for one item.
## Returns item id -> count.
static func roll_drops(engine: BattleEngine) -> Dictionary:
	var drops: Dictionary = {}
	for e in engine.enemies:
		if e.withdrawn:
			continue
		for entry: Variant in _row(engine, e).get("drops", []):
			var d: Dictionary = entry
			if engine.rng.randi_range(1, 100) <= int(d.get("chance", 0)):
				var iid := StringName(str(d["item"]))
				drops[iid] = int(drops.get(iid, 0)) + 1
	return drops


static func _row(engine: BattleEngine, e: BattleCombatant) -> Dictionary:
	return engine.db.enemies.get(BattleEngine.enemy_id(e), {})
