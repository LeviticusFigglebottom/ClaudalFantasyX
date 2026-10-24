class_name EnemyAI
extends RefCounted
## Data-defined enemy behaviour. An enemy's "ai" is an ordered list of rules:
##   {"if": {<condition>: <arg>, ...}, "pick": [{"skill", "target", "weight"}, ...]}
## The first rule whose conditions all hold wins; one option is drawn by weight.
## A rule without "if" always holds (use it last as the default).
## Conditions: self_hp_below_pct:int, turn_mod:[n, r], foe_has_status:String,
##             allies_alive_below:int, field_active:String (a field in BattleEngine.fields),
##             foes_all_absorb:String (every living foe absorbs that element: M2-FP-17, the
##             Drownbell's answer to a lone Ilun drinking its flood)
## Targets:    random_foe, lowest_hp_foe, highest_hp_foe, self, random_ally, all_foes, all_allies,
##             largest_ally (the living ally with the highest max HP: a boss its adds tend)
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
			var selector := StringName(str(option.get("target", "random_foe")))
			var targets := select_targets(engine, actor, selector)
			if targets.is_empty():
				continue
			var forced := engine.forced_target(actor, skill_id)
			if forced != null:
				targets = [forced]  # Provoke overrides the selector for single-foe skills
			return {"skill": skill_id, "targets": targets}
	return {}


static func select_targets(
	engine: BattleEngine, actor: BattleCombatant, selector: StringName
) -> Array[BattleCombatant]:
	var foes := engine.living_foes_of(actor)
	var allies := engine.living_allies_of(actor)
	var out: Array[BattleCombatant] = []
	match selector:
		&"self":
			out.append(actor)
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


static func _conditions_hold(engine: BattleEngine, actor: BattleCombatant, cond: Dictionary) -> bool:
	for key: Variant in cond:
		if not _holds(engine, actor, StringName(str(key)), cond[key]):
			return false
	return true


static func _holds(engine: BattleEngine, actor: BattleCombatant, key: StringName, arg: Variant) -> bool:
	var ok := true
	match key:
		&"self_hp_below_pct":
			ok = actor.hp * 100 < actor.max_hp * int(arg)
		&"turn_mod":
			var a: Array = arg
			ok = int(a[0]) > 0 and (actor.turns_taken - actor.ai_turn_base) % int(a[0]) == int(a[1])
		&"foe_has_status":
			ok = false
			for f in engine.living_foes_of(actor):
				if f.has_status(StringName(str(arg))):
					ok = true
		&"allies_alive_below":
			ok = engine.living_allies_of(actor).size() < int(arg)
		&"field_active":
			ok = engine.fields.has(StringName(str(arg)))
		&"foes_all_absorb":
			var foes := engine.living_foes_of(actor)
			ok = not foes.is_empty()
			for f in foes:
				if f.affinity_for(StringName(str(arg))) != &"absorb":
					ok = false
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
