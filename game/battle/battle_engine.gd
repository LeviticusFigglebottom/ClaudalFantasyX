class_name BattleEngine
extends RefCounted
## Headless, deterministic CTB battle engine. Given the same DB, roster and seed, a battle
## always plays out identically, which is what the balancing simulator and tests rely on.
##
## Flow: setup() -> begin() -> loop { current is party ? perform()/swap()/escape()
##                                                    : run_enemy_turn() } until outcome != "".
## Time stops between calls: nothing advances while the player is choosing.

signal turn_started(actor: BattleCombatant)
signal action_resolved(result: ActionResult)
signal battle_finished(outcome: StringName)

const OUTCOME_VICTORY := &"victory"
const OUTCOME_DEFEAT := &"defeat"
const OUTCOME_ESCAPED := &"escaped"
const MAX_ACTIVE := 3

var db: BattleDB
var rng := RandomNumberGenerator.new()
var timeline := CtbTimeline.new()
var party_active: Array[BattleCombatant] = []
var party_reserve: Array[BattleCombatant] = []
var enemies: Array[BattleCombatant] = []
var current: BattleCombatant
var now := 0
var outcome: StringName = &""
var encounter_id: StringName = &""
## Scripted fights forbid escape.
var scripted := false


func setup(
	battle_db: BattleDB,
	active_ids: Array[StringName],
	reserve_ids: Array[StringName],
	encounter: StringName,
	rng_seed: int
) -> void:
	db = battle_db
	rng.seed = rng_seed
	encounter_id = encounter
	party_active.clear()
	party_reserve.clear()
	enemies.clear()
	for cid in active_ids:
		party_active.append(_make_party_member(cid))
	for cid in reserve_ids:
		party_reserve.append(_make_party_member(cid))
	assert(party_active.size() <= MAX_ACTIVE, "BattleEngine: too many active party members")
	var enc: Dictionary = db.encounters.get(encounter, {})
	scripted = bool(enc.get("scripted", false))
	var n := 0
	for eid: Variant in enc.get("enemies", []):
		n += 1
		var row: Dictionary = db.enemies[StringName(str(eid))]
		enemies.append(BattleCombatant.from_dict(StringName("%s#%d" % [eid, n]), BattleCombatant.TEAM_ENEMY, row))
	_rebuild_roster()


func begin() -> void:
	for c in _field():
		c.next_time = Formulas.initial_ticks(c.agility, rng.randi_range(0, Formulas.base_delay(c.agility)))
		c.participated = c.team == BattleCombatant.TEAM_PARTY
	_advance()


func is_party_turn() -> bool:
	return outcome == &"" and current != null and current.team == BattleCombatant.TEAM_PARTY


## Timeline for the UI. With `skill_id`, shows the order as if `current` used that skill
## (and, for delay skills, as if `target` were pushed back).
func preview(
	skill_id: StringName = &"", target: BattleCombatant = null, count: int = CtbTimeline.PREVIEW_LENGTH
) -> Array[TurnEntry]:
	if skill_id == &"" or current == null:
		return timeline.predict(count)
	var sk := db.skill(skill_id)
	return timeline.predict(
		count, current, int(sk.get("rank", Formulas.DEFAULT_RANK)), target, int(sk.get("delay_ranks", 0))
	)


## Executes `skill_id` for the current actor. Ends the actor's turn on success.
func perform(skill_id: StringName, targets: Array[BattleCombatant]) -> ActionResult:
	if outcome != &"" or current == null:
		return ActionResult.failed(&"", skill_id, &"battle_over")
	var actor := current
	var sk := db.skill(skill_id)
	if sk.is_empty() or not actor.skills.has(skill_id):
		return ActionResult.failed(actor.id, skill_id, &"unknown_skill")
	var cost := int(sk.get("mp_cost", 0))
	if actor.mp < cost:
		return ActionResult.failed(actor.id, skill_id, &"no_mp")
	if bool(sk.get("magic", false)) and actor.has_status(&"silence"):
		return ActionResult.failed(actor.id, skill_id, &"silenced")
	actor.mp -= cost
	var result := ActionResult.new()
	result.actor_id = actor.id
	result.skill_id = skill_id
	for t in targets:
		if t.is_alive():
			result.hits.append(_resolve_on(actor, t, sk))
	action_resolved.emit(result)
	_end_turn(actor, int(sk.get("rank", Formulas.DEFAULT_RANK)))
	return result


## Runs the current enemy's AI turn. Returns null if it is not an enemy's turn.
func run_enemy_turn() -> ActionResult:
	if outcome != &"" or current == null or current.team != BattleCombatant.TEAM_ENEMY:
		return null
	var choice := EnemyAI.choose(self, current)
	if choice.is_empty():
		var idle := ActionResult.failed(current.id, &"", &"no_valid_action")
		_end_turn(current, Formulas.DEFAULT_RANK)
		return idle
	var actor := current
	var targets: Array[BattleCombatant] = choice["targets"]
	var result := perform(choice["skill"], targets)
	if not result.ok and current == actor:
		# Bad data (e.g. not enough MP) must never stall a battle: the enemy loses its turn.
		_end_turn(actor, Formulas.DEFAULT_RANK)
	return result


## Swaps an active member for a reserve member at no turn cost. The incoming member takes
## over the outgoing member's slot in the timeline (and the current turn, if it was theirs).
func swap(out_id: StringName, in_id: StringName) -> bool:
	if not is_party_turn():
		return false
	var out_idx := _index_of(party_active, out_id)
	var in_idx := _index_of(party_reserve, in_id)
	if out_idx < 0 or in_idx < 0 or not party_reserve[in_idx].is_alive():
		return false
	var leaving := party_active[out_idx]
	var entering := party_reserve[in_idx]
	entering.next_time = leaving.next_time
	entering.participated = true
	party_active[out_idx] = entering
	party_reserve[in_idx] = leaving
	if current == leaving:
		current = entering
	_rebuild_roster()
	turn_started.emit(current)
	return true


## Attempts to flee. A failed attempt costs the actor a default-rank turn.
func escape() -> bool:
	if not is_party_turn() or scripted:
		return false
	var chance := Formulas.escape_chance(_mean_agility(party_active), _mean_agility(enemies))
	if rng.randi_range(1, 100) <= chance:
		_finish(OUTCOME_ESCAPED)
		return true
	_end_turn(current, Formulas.DEFAULT_RANK)
	return false


## XP credit rule (docs/kb/design/formulas.md §XP): every party member who was on the field
## at any point and is alive at victory receives the encounter's full XP. No split.
func xp_awards() -> Dictionary:
	var out: Dictionary = {}
	if outcome != OUTCOME_VICTORY:
		return out
	var total := 0
	for e in enemies:
		total += e.xp_reward
	for c in party_active + party_reserve:
		if c.participated and c.is_alive():
			out[c.id] = total
	return out


func living_foes_of(c: BattleCombatant) -> Array[BattleCombatant]:
	return _living(enemies if c.team == BattleCombatant.TEAM_PARTY else party_active)


func living_allies_of(c: BattleCombatant) -> Array[BattleCombatant]:
	return _living(party_active if c.team == BattleCombatant.TEAM_PARTY else enemies)


func find(cid: StringName) -> BattleCombatant:
	for c in party_active + party_reserve + enemies:
		if c.id == cid:
			return c
	return null


# --- internals ---------------------------------------------------------------------------


func _resolve_on(actor: BattleCombatant, target: BattleCombatant, sk: Dictionary) -> Dictionary:
	var kind := StringName(str(sk.get("kind", "physical")))
	var power := int(sk.get("power", 0))
	var element := StringName(str(sk.get("element", "none")))
	var hit := {"target_id": target.id, "hit": true, "crit": false, "amount": 0, "statuses_added": []}
	match kind:
		&"physical":
			var chance := Formulas.hit_chance(
				int(sk.get("accuracy", 100)), actor.accuracy, target.evasion, actor.has_status(&"darkness")
			)
			if rng.randi_range(1, 100) > chance:
				hit["hit"] = false
				return hit
			var crit := rng.randi_range(1, 100) <= Formulas.crit_chance(actor.luck, target.luck)
			var raw := Formulas.raw_damage(
				power, actor.effective_strength(), actor.level, target.effective_defense(), _variance()
			)
			var dmg := Formulas.final_damage(
				raw, target.affinity_for(element), crit, target.has_status(&"protect"), actor.break_damage_cap
			)
			hit["crit"] = crit
			hit["amount"] = -target.apply_damage(dmg)
		&"magical":
			var raw_m := Formulas.raw_damage(
				power, actor.effective_magic(), actor.level, target.effective_magic_defense(), _variance()
			)
			var dmg_m := Formulas.final_damage(
				raw_m, target.affinity_for(element), false, target.has_status(&"shell"), actor.break_damage_cap
			)
			hit["amount"] = -target.apply_damage(dmg_m)
		&"heal":
			var amt := Formulas.heal_amount(
				power, actor.effective_magic(), actor.level, _variance(), actor.break_damage_cap
			)
			hit["amount"] = -target.apply_damage(-amt)
		&"support":
			pass
		_:
			push_error("BattleEngine: unknown skill kind '%s'" % kind)
	var added: Array = []
	for inflict: Variant in sk.get("statuses", []):
		var inf: Dictionary = inflict
		if rng.randi_range(1, 100) <= int(inf.get("chance", 100)):
			var sid := StringName(str(inf["id"]))
			var row: Dictionary = db.statuses.get(sid, {})
			target.add_status(sid, int(inf.get("duration", row.get("default_duration", -1))))
			added.append(sid)
	hit["statuses_added"] = added
	var delay_ranks := int(sk.get("delay_ranks", 0))
	if delay_ranks > 0 and target.is_alive():
		target.next_time += Formulas.base_delay(target.agility) * delay_ranks
	return hit


func _variance() -> int:
	return rng.randi_range(Formulas.VARIANCE_MIN_PCT, Formulas.VARIANCE_MAX_PCT)


func _end_turn(actor: BattleCombatant, rank: int) -> void:
	actor.next_time = now + Formulas.action_delay(actor.agility, rank, actor.speed_mult())
	if actor.is_alive():
		if actor.has_status(&"poison"):
			actor.apply_damage(Formulas.poison_damage(actor.max_hp))
		if actor.has_status(&"regen"):
			actor.apply_damage(-Formulas.regen_heal(actor.max_hp))
	actor.tick_statuses()
	actor.turns_taken += 1
	if _check_outcome():
		return
	_advance()


func _advance() -> void:
	current = null
	while outcome == &"":
		var actor := timeline.next_actor()
		if actor == null:
			_check_outcome()
			return
		now = actor.next_time
		if actor.has_status(&"stop") or actor.has_status(&"sleep"):
			# The turn is lost; statuses still count down so Stop/Sleep wear off.
			actor.next_time = now + Formulas.action_delay(actor.agility, Formulas.DEFAULT_RANK, actor.speed_mult())
			actor.tick_statuses()
			continue
		current = actor
		turn_started.emit(actor)
		return


func _check_outcome() -> bool:
	if _living(enemies).is_empty():
		_finish(OUTCOME_VICTORY)
	elif _living(party_active).is_empty():
		_finish(OUTCOME_DEFEAT)
	return outcome != &""


func _finish(result: StringName) -> void:
	outcome = result
	current = null
	battle_finished.emit(result)


func _field() -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = []
	out.append_array(party_active)
	out.append_array(enemies)
	return out


func _rebuild_roster() -> void:
	timeline.set_roster(_field())


func _make_party_member(cid: StringName) -> BattleCombatant:
	return BattleCombatant.from_dict(cid, BattleCombatant.TEAM_PARTY, db.characters[cid])


static func _living(list: Array[BattleCombatant]) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = []
	for c in list:
		if c.is_alive():
			out.append(c)
	return out


static func _index_of(list: Array[BattleCombatant], cid: StringName) -> int:
	for i in list.size():
		if list[i].id == cid:
			return i
	return -1


static func _mean_agility(list: Array[BattleCombatant]) -> float:
	var alive := _living(list)
	if alive.is_empty():
		return 0.0
	var total := 0
	for c in alive:
		total += c.agility
	return float(total) / alive.size()
