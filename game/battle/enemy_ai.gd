class_name EnemyAI
extends RefCounted
## Data-defined enemy behaviour. An enemy's "ai" is an ordered list of rules:
##   {"if": {<condition>: <arg>, ...}, "pick": [{"skill", "target", "weight"}, ...]}
## The first rule whose conditions all hold wins; one option is drawn by weight.
## A rule without "if" always holds (use it last as the default).
## Conditions: self_hp_below_pct:int, turn_mod:[n, r], foe_has_status:String,
##             allies_alive_below:int, field_active:String (a field in BattleEngine.fields),
##             ward_has_status:String (the battle's ward entry has it: a Squall Wing dives a hauled
##             rope; M3-CMB-01), ally_part_broken:bool and ally_struck:bool (M4-A2P-022, BattleParts:
##             a living ally, itself included, has a broken part / has been struck by the party)
## Targets:    random_foe, lowest_hp_foe, highest_hp_foe, self, random_ally, all_foes, all_allies,
##             largest_ally (the living ally with the highest max HP: a boss its adds tend),
##             ward (the battle's ward entry, for a skill whose target is "ward"; M3-CMB-01),
##             broken_ally (the first living ally with a broken part; M4-A2P-022)
## An option whose charge is a part broken on the actor is never picked (BattleParts.silenced).
## turn_mod counts the actor's turns since its current phase began (BossMechanics).
## A Provoked enemy's single-foe skills always target its provoker (formulas.md § Statuses).


static func choose(engine: BattleEngine, actor: BattleCombatant) -> Dictionary:
	for rule: Variant in actor.ai_rules:
		var r: Dictionary = rule
		if _conditions_hold(engine, actor, r.get("if", {}) as Dictionary):
			var option := _weighted_pick(engine.rng, r.get("pick", []) as Array)
			if option.is_empty():
				continue
			var skill_id := StringName(str(option["skill"]))
			if BattleParts.silenced(engine, actor, skill_id):
				continue
			var selector := StringName(str(option.get("target", "random_foe")))
			var targets := select_targets(engine, actor, selector)
			if targets.is_empty():
				continue
			var forced := engine.forced_target(actor, skill_id)
			if forced != null:
				targets = [forced]  # Provoke overrides the selector for single-foe skills
			return {"skill": skill_id, "targets": targets}
	return {}


## The skills the first rule whose conditions hold now could pick (no draw, no targets): what a
## careful player reads off a foe's habits (SimWardGuard; M3-CMB-01). Empty when no rule holds.
static func likely_skills(engine: BattleEngine, actor: BattleCombatant) -> Array[StringName]:
	var out: Array[StringName] = []
	for rule: Variant in actor.ai_rules:
		var r: Dictionary = rule
		if not _conditions_hold(engine, actor, r.get("if", {}) as Dictionary):
			continue
		for o: Variant in r.get("pick", []):
			if int((o as Dictionary).get("weight", 1)) > 0:
				out.append(StringName(str((o as Dictionary).get("skill", ""))))
		break
	return out


static func select_targets(
	engine: BattleEngine, actor: BattleCombatant, selector: StringName
) -> Array[BattleCombatant]:
	var foes := engine.living_foes_of(actor)
	var allies := engine.living_allies_of(actor)
	var out: Array[BattleCombatant] = []
	match selector:
		&"self":
			out.append(actor)
		&"ward":
			var w := engine.ward()
			if w != null:
				out.append(w)
		&"broken_ally":
			var b := BattleParts.broken_ally(engine, actor)
			if b != null:
				out.append(b)
		&"all_foes":
			out = foes
		&"all_allies":
			out = allies
		&"random_foe":
			if not foes.is_empty():
				out.append(foes[engine.rng.randi_range(0, foes.size() - 1)])
		&"largest_ally":
			var big: BattleCombatant = null
			for a in allies:
				if big == null or a.max_hp > big.max_hp:
					big = a
			if big != null:
				out.append(big)
		&"random_ally":
			if not allies.is_empty():
				out.append(allies[engine.rng.randi_range(0, allies.size() - 1)])
		&"lowest_hp_foe", &"highest_hp_foe":
			var best: BattleCombatant = null
			for f in foes:
				if best == null:
					best = f
				elif selector == &"lowest_hp_foe" and f.hp < best.hp:
					best = f
				elif selector == &"highest_hp_foe" and f.hp > best.hp:
					best = f
			if best != null:
				out.append(best)
		_:
			push_error("EnemyAI: unknown target selector '%s'" % selector)
	return out


## The skill row `actor` will use `ahead` own turns from now, for the timeline's prediction (pillar 4:
## the order shows when a foe really acts, and whom its delay pushes back). The first rule whose
## conditions hold now (turn_mod counted `ahead` turns on) decides; of its options, the one with the
## lowest rank (the soonest the foe can come back; the first on a tie). A Berserk/Confused foe uses its
## basic attack. {} when no rule holds (the engine's idle turn, a standard one). Draws nothing from the
## battle RNG: a prediction never changes the battle.
static func predicted_skill(engine: BattleEngine, actor: BattleCombatant, ahead: int) -> Dictionary:
	if BattleEngine.auto_reason(actor) != &"":
		return engine.db.skill(engine.basic_attack(actor))
	for rule: Variant in actor.ai_rules:
		var r: Dictionary = rule
		if not _conditions_hold(engine, actor, r.get("if", {}) as Dictionary, ahead):
			continue
		var best: Dictionary = {}
		for o: Variant in r.get("pick", []) as Array:
			var opt: Dictionary = o
			var sid := StringName(str(opt["skill"]))
			var row := engine.db.skill(sid)
			if int(opt.get("weight", 1)) <= 0 or row.is_empty() or BattleParts.silenced(engine, actor, sid):
				continue
			if best.is_empty() or _rank(row) < _rank(best):
				best = row
		if not best.is_empty():
			return best
	return {}


## The rank of the action predicted_skill() names.
static func predicted_rank(engine: BattleEngine, actor: BattleCombatant, ahead: int) -> int:
	var row := predicted_skill(engine, actor, ahead)
	return _rank(row) if not row.is_empty() else Formulas.DEFAULT_RANK


static func _rank(row: Dictionary) -> int:
	return int(row.get("rank", Formulas.DEFAULT_RANK))


static func _conditions_hold(engine: BattleEngine, actor: BattleCombatant, cond: Dictionary, ahead: int = 0) -> bool:
	for key: Variant in cond:
		if not _holds(engine, actor, StringName(str(key)), cond[key], ahead):
			return false
	return true


static func _holds(engine: BattleEngine, actor: BattleCombatant, key: StringName, arg: Variant, ahead: int = 0) -> bool:
	var ok := true
	match key:
		&"self_hp_below_pct":
			ok = actor.hp * 100 < actor.max_hp * int(arg)
		&"turn_mod":
			var a: Array = arg
			ok = int(a[0]) > 0 and (actor.turns_taken + ahead - actor.ai_turn_base) % int(a[0]) == int(a[1])
		&"foe_has_status":
			ok = false
			for f in engine.living_foes_of(actor):
				if f.has_status(StringName(str(arg))):
					ok = true
		&"allies_alive_below":
			ok = engine.living_allies_of(actor).size() < int(arg)
		&"field_active":
			ok = engine.fields.has(StringName(str(arg)))
		&"ward_has_status":
			var w := engine.ward()
			ok = w != null and w.has_status(StringName(str(arg)))
		&"ally_part_broken":
			ok = (BattleParts.broken_ally(engine, actor) != null) == bool(arg)
		&"ally_struck":
			ok = BattleParts.ally_struck(engine, actor) == bool(arg)
		_:
			push_error("EnemyAI: unknown condition '%s'" % key)
			ok = false
	return ok


static func _weighted_pick(rng: RandomNumberGenerator, options: Array) -> Dictionary:
	var total := 0
	for o: Variant in options:
		total += int((o as Dictionary).get("weight", 1))
	if total <= 0:
		return {}
	var roll := rng.randi_range(1, total)
	for o: Variant in options:
		roll -= int((o as Dictionary).get("weight", 1))
		if roll <= 0:
			return o
	return {}
