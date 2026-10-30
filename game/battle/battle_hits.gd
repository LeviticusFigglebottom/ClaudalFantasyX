class_name BattleHits
extends RefCounted
## Resolves one skill on one target (formulas.md § Damage, § Statuses, § Equipment), split out of
## BattleEngine (M2-CMB-03). Static and headless: every roll draws on the engine's seeded rng in
## the same order as before the split, so a seed still plays out identically.


## The hit dictionary for `sk` from `actor` landing on `target` (after Reflect):
## {target_id, hit, crit, amount (HP lost; < 0 heals), statuses_added, element}, plus "read" for
## Read, "delay_ticks" when it pushes the target back, "drained" (the HP its user won back, M4-CMB-1001)
## for a drain, "rooted" (own turns it can't be swapped out, M4-A2P-020) for a root, and "absorbed"
## (the HP the target's absorb affinity drank, before the max-HP cap: ADR 0027 A1, the Vowbound
## gauge) when it absorbs.
static func resolve(
	engine: BattleEngine, actor: BattleCombatant, target: BattleCombatant, sk: Dictionary
) -> Dictionary:
	var rng := engine.rng
	var kind := StringName(str(sk.get("kind", "physical")))
	var power := int(sk.get("power", 0))
	var element := engine.attack_element(actor, target, sk)
	var hit := {"target_id": target.id, "hit": true, "crit": false, "amount": 0, "statuses_added": []}
	hit["element"] = element
	var added: Array = []
	match kind:
		&"physical":
			var chance := Formulas.hit_chance(
				int(sk.get("accuracy", 100)), actor.accuracy, target.evasion, actor.has_status(&"darkness")
			)
			if rng.randi_range(1, 100) > chance:
				hit["hit"] = false
				return hit
			var crit := rng.randi_range(1, 100) <= Formulas.crit_chance(actor.luck, target.luck)
			var dmg := Formulas.damage(
				power,
				actor.effective_strength(),
				actor.level,
				target.effective_defense(),
				_variance(rng),
				target.affinity_for(element),
				crit,
				target.has_status(&"protect"),
				actor.break_damage_cap
			)
			hit["crit"] = crit
			_mark_absorbed(hit, dmg)
			hit["amount"] = -target.apply_damage(dmg)
			if dmg > 0:
				target.statuses.erase(&"confuse")  # a physical blow snaps a confused unit out of it
			added.append_array(_roll_on_hit(rng, actor, target))
		&"magical":
			var dmg_m := Formulas.damage(
				power,
				actor.effective_magic(),
				actor.level,
				target.effective_magic_defense(),
				_variance(rng),
				target.affinity_for(element),
				false,
				target.has_status(&"shell"),
				actor.break_damage_cap
			)
			_mark_absorbed(hit, dmg_m)
			hit["amount"] = -target.apply_damage(dmg_m)
		&"heal":
			var amt := Formulas.heal_amount(
				power, actor.effective_magic(), actor.level, _variance(rng), actor.break_damage_cap
			)
			hit["amount"] = -target.restore_hp(amt)  # Zombie: the same amount harms instead
		&"support":
			if BattleRead.is_read(sk):
				hit["read"] = BattleRead.reveal(target, engine.db.enemies.get(BattleEngine.enemy_id(target), {}))
		_:
			push_error("BattleEngine: unknown skill kind '%s'" % kind)
	_drain(actor, hit, sk)
	added.append_array(_inflict(engine, actor, target, sk))
	hit["statuses_added"] = added
	var delay_ranks := int(sk.get("delay_ranks", 0))
	if delay_ranks > 0 and target.is_alive():
		hit["delay_ticks"] = engine.push_delay(target, delay_ranks)
	var root_turns := int(sk.get("root_turns", 0))
	if root_turns > 0 and target.is_alive():  # M4-A2P-020: held by the roots, no swap (a longer hold wins)
		target.rooted_turns = maxi(target.rooted_turns, root_turns)
		hit["rooted"] = target.rooted_turns
	return hit


## M4-CMB-1001: a `drain_pct` skill heals its user by that share of the HP the hit took ("drained" on the hit).
static func _drain(actor: BattleCombatant, hit: Dictionary, sk: Dictionary) -> void:
	var pct := int(sk.get("drain_pct", 0))
	var lost := int(hit["amount"])
	if pct <= 0 or lost <= 0 or not actor.is_alive():
		return
	hit["drained"] = actor.restore_hp(Formulas.drain_heal(lost, pct))


## A negative damage roll is an absorb: record what it drank, even when the target was full.
static func _mark_absorbed(hit: Dictionary, dmg: int) -> void:
	if dmg < 0:
		hit["absorbed"] = -dmg


## The skill's own "statuses" entries: each rolls its chance; a landed Provoke remembers `actor`.
static func _inflict(engine: BattleEngine, actor: BattleCombatant, target: BattleCombatant, sk: Dictionary) -> Array:
	var added: Array = []
	for inflict: Variant in sk.get("statuses", []):
		var inf: Dictionary = inflict
		if engine.rng.randi_range(1, 100) <= int(inf.get("chance", 100)):
			var sid := StringName(str(inf["id"]))
			var row: Dictionary = engine.db.statuses.get(sid, {})
			if target.add_status(sid, int(inf.get("duration", row.get("default_duration", -1)))):
				added.append(sid)
				if sid == &"provoke":
					target.provoker_id = actor.id
	return added


## Equipment status strikes (formulas.md § Equipment): after a landed physical hit on a target
## that still stands, each on_hit_statuses entry rolls its chance on the battle RNG.
static func _roll_on_hit(rng: RandomNumberGenerator, actor: BattleCombatant, target: BattleCombatant) -> Array:
	var out: Array = []
	for entry: Variant in actor.equipment().get("on_hit_statuses", []):
		var e: Dictionary = entry
		if not target.is_alive():
			break
		if rng.randi_range(1, 100) <= int(e["chance"]):
			var sid := StringName(str(e["id"]))
			if target.add_status(sid, int(e["duration"])):
				out.append(sid)
	return out


static func _variance(rng: RandomNumberGenerator) -> int:
	return rng.randi_range(Formulas.VARIANCE_MIN_PCT, Formulas.VARIANCE_MAX_PCT)
