class_name BattleEngine
extends RefCounted
## Headless, deterministic CTB battle engine. Given the same DB, roster and seed, a battle
## always plays out identically, which is what the balancing simulator and tests rely on.
##
## Flow: setup() -> begin() -> loop { is_party_turn() ? perform()/swap()/escape()
##                                                 : run_enemy_turn() } until outcome != "".
## Time stops between calls: nothing advances while the player is choosing.
## run_enemy_turn() also plays any combatant that is not in control of itself (Berserk or
## Confuse, on either side): is_party_turn() is false for those turns.

signal turn_started(actor: BattleCombatant)
signal action_resolved(result: ActionResult)
signal battle_finished(outcome: StringName)

const OUTCOME_VICTORY := &"victory"
const OUTCOME_DEFEAT := &"defeat"
const OUTCOME_ESCAPED := &"escaped"
const MAX_ACTIVE := 3
## Consecutive turns lost to Stop/Sleep with nobody able to act before the battle is ruled a
## stalemate (only reachable with "until cured" durations on everyone; ends as defeat).
const MAX_CONSECUTIVE_LOST_TURNS := 1000

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
## Optional hook run once on every party combatant (active and reserve) right after setup()
## builds it from characters.json, e.g. `progress.apply_to` to layer Lattice gains on (SPEC §6.4).
## It receives the BattleCombatant and must stay deterministic. Set it before setup().
var party_modifier := Callable()


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


## True when the player chooses the current action: a party member in control of itself.
func is_party_turn() -> bool:
	return is_player_side_turn() and auto_reason(current) == &""


## The current actor is on the party side, whether or not the player controls it.
func is_player_side_turn() -> bool:
	return outcome == &"" and current != null and current.team == BattleCombatant.TEAM_PARTY


## The current actor acts on its own this turn (Berserk or Confuse); run_enemy_turn() plays it.
func is_auto_turn() -> bool:
	return outcome == &"" and current != null and auto_reason(current) != &""


## Why `c` is not in control of itself: &"confuse" (wins if both), &"berserk", or &"" if it is.
static func auto_reason(c: BattleCombatant) -> StringName:
	if c.has_status(&"confuse"):
		return &"confuse"
	if c.has_status(&"berserk"):
		return &"berserk"
	return &""


## Provoke: the combatant `actor` must hit with a single-foe skill, or null if it is free to
## choose. Only skills whose target is "single_foe" are forced; the provoker must be alive and
## on the field. The UI uses this to lock the target cursor; perform() rejects anything else.
func forced_target(actor: BattleCombatant, skill_id: StringName) -> BattleCombatant:
	if actor == null or not actor.has_status(&"provoke"):
		return null
	if String(db.skill(skill_id).get("target", "single_foe")) != "single_foe":
		return null
	return _valid_provoker(actor)


## Timeline for the UI. With `skill_id`, shows the order as if `current` used that skill on
## `target`: its rank, any delay push, and any time statuses it inflicts (assumed to land).
func preview(
	skill_id: StringName = &"", target: BattleCombatant = null, count: int = CtbTimeline.PREVIEW_LENGTH
) -> Array[TurnEntry]:
	if skill_id == &"" or current == null:
		return timeline.predict(count)
	var sk := db.skill(skill_id)
	var changes: Dictionary = {}
	var recipient := current if String(sk.get("target", "")) == "self" else target
	if recipient != null:
		# Reflect is deterministic, so the preview shows where the spell will really land.
		recipient = reflect_recipient(current, recipient, sk)
		for inflict: Variant in sk.get("statuses", []):
			var inf: Dictionary = inflict
			var sid := StringName(str(inf["id"]))
			if CtbTimeline.PREVIEW_STATUSES.has(sid):
				var row: Dictionary = db.statuses.get(sid, {})
				if not changes.has(recipient):
					changes[recipient] = {}
				changes[recipient][sid] = int(inf.get("duration", row.get("default_duration", -1)))
	return timeline.predict(
		count, current, int(sk.get("rank", Formulas.DEFAULT_RANK)), recipient, int(sk.get("delay_ranks", 0)), changes
	)


## Executes `skill_id` for the current actor. Ends the actor's turn on success. Fails with
## &"auto_turn" while the actor is Berserk/Confused (call run_enemy_turn() instead).
func perform(skill_id: StringName, targets: Array[BattleCombatant]) -> ActionResult:
	if outcome != &"" or current == null:
		return ActionResult.failed(&"", skill_id, &"battle_over")
	if is_auto_turn():
		return ActionResult.failed(current.id, skill_id, &"auto_turn")
	return _perform(current, skill_id, targets)


## Runs the current enemy's AI turn, or the current Berserk/Confused combatant's automatic
## turn on either side. Returns null if the player is in control of the current turn.
func run_enemy_turn() -> ActionResult:
	if outcome != &"" or current == null:
		return null
	if is_auto_turn():
		return _run_auto_turn()
	if current.team != BattleCombatant.TEAM_ENEMY:
		return null
	var choice := EnemyAI.choose(self, current)
	if choice.is_empty():
		var idle := ActionResult.failed(current.id, &"", &"no_valid_action")
		_end_turn(current, Formulas.DEFAULT_RANK)
		return idle
	var actor := current
	var targets: Array[BattleCombatant] = choice["targets"]
	var result := _perform(actor, choice["skill"], targets)
	if not result.ok and current == actor:
		# Bad data (e.g. not enough MP) must never stall a battle: the enemy loses its turn.
		_end_turn(actor, Formulas.DEFAULT_RANK)
	return result


## Where a skill aimed at `target` really lands. Reflect bounces single-target magic (any
## skill with "magic": true aimed at one other combatant) to the living combatant on the
## other side from the reflector with the lowest HP (ties: field order). A bounced spell is
## never bounced again, so Reflect cannot chain.
func reflect_recipient(actor: BattleCombatant, target: BattleCombatant, sk: Dictionary) -> BattleCombatant:
	if target == null or target == actor or not target.has_status(&"reflect"):
		return target
	if not bool(sk.get("magic", false)):
		return target
	if not String(sk.get("target", "single_foe")) in ["single_foe", "single_ally"]:
		return target
	var best: BattleCombatant = null
	for c in living_foes_of(target):
		if best == null or c.hp < best.hp:
			best = c
	return best if best != null else target


func _perform(actor: BattleCombatant, skill_id: StringName, targets: Array[BattleCombatant]) -> ActionResult:
	var sk := db.skill(skill_id)
	if sk.is_empty() or not actor.skills.has(skill_id):
		return ActionResult.failed(actor.id, skill_id, &"unknown_skill")
	var cost := int(sk.get("mp_cost", 0))
	if actor.mp < cost:
		return ActionResult.failed(actor.id, skill_id, &"no_mp")
	if bool(sk.get("magic", false)) and actor.has_status(&"silence"):
		return ActionResult.failed(actor.id, skill_id, &"silenced")
	var valid := _valid_targets(actor, sk, targets)
	if valid.is_empty():
		return ActionResult.failed(actor.id, skill_id, &"no_valid_target")
	var forced := forced_target(actor, skill_id)
	if forced != null and valid[0] != forced:
		return ActionResult.failed(actor.id, skill_id, &"provoked")
	return _execute(actor, skill_id, sk, valid, &"")


## Spends the cost, resolves `sk` on already-validated targets (bouncing off Reflect), and
## ends the actor's turn.
func _execute(
	actor: BattleCombatant, skill_id: StringName, sk: Dictionary, targets: Array[BattleCombatant], auto: StringName
) -> ActionResult:
	actor.mp -= int(sk.get("mp_cost", 0))
	var result := ActionResult.new()
	result.actor_id = actor.id
	result.skill_id = skill_id
	result.auto_reason = auto
	for t in targets:
		var lands := reflect_recipient(actor, t, sk)
		var hit := _resolve_on(actor, lands, sk)
		if lands != t:
			hit["reflected_from"] = t.id
		result.hits.append(hit)
	action_resolved.emit(result)
	_end_turn(actor, int(sk.get("rank", Formulas.DEFAULT_RANK)))
	return result


## Berserk / Confuse: the combatant uses its basic attack on a target the battle RNG picks
## (formulas.md § Statuses). Berserk hits a random foe (the provoker if Provoked); Confuse
## turns on a random ally other than itself with CONFUSE_ALLY_PCT, otherwise a random foe.
func _run_auto_turn() -> ActionResult:
	var actor := current
	var reason := auto_reason(actor)
	var skill_id := basic_attack(actor)
	var pool: Array[BattleCombatant] = []
	if skill_id != &"":
		pool = _auto_pool(actor, reason, skill_id)
	if pool.is_empty():
		var idle := ActionResult.failed(actor.id, skill_id, &"no_valid_action")
		idle.auto_reason = reason
		_end_turn(actor, Formulas.DEFAULT_RANK)
		return idle
	var targets: Array[BattleCombatant] = [pool[rng.randi_range(0, pool.size() - 1)]]
	return _execute(actor, skill_id, db.skill(skill_id), targets, reason)


## The skill a combatant uses when not in control: "attack" if it knows it, otherwise its
## first affordable physical single-foe skill. &"" if it has none.
func basic_attack(c: BattleCombatant) -> StringName:
	if c.skills.has(&"attack") and int(db.skill(&"attack").get("mp_cost", 0)) <= c.mp:
		return &"attack"
	for sid in c.skills:
		var sk := db.skill(sid)
		if (
			String(sk.get("kind", "")) == "physical"
			and String(sk.get("target", "single_foe")) == "single_foe"
			and int(sk.get("mp_cost", 0)) <= c.mp
		):
			return sid
	return &""


func _auto_pool(actor: BattleCombatant, reason: StringName, skill_id: StringName) -> Array[BattleCombatant]:
	var foes := living_foes_of(actor)
	if reason == &"confuse":
		var allies := living_allies_of(actor)
		allies.erase(actor)
		var turn_on_allies := rng.randi_range(1, 100) <= Formulas.CONFUSE_ALLY_PCT
		if turn_on_allies and not allies.is_empty() or foes.is_empty():
			return allies
		return foes
	var forced := forced_target(actor, skill_id)
	if forced != null:
		var only: Array[BattleCombatant] = [forced]
		return only
	return foes


## Swaps an active member for a reserve member at no turn cost. The incoming member takes
## over a living outgoing member's slot in the timeline (and the current turn, if it was
## theirs). Replacing a KO'd member, the incoming one acts after a default-rank delay from
## now: time never runs backwards (docs/kb/design/battle_ctb.md).
func swap(out_id: StringName, in_id: StringName) -> bool:
	var idx := _swap_indices(out_id, in_id)
	if idx.x < 0:
		return false
	var out_idx := idx.x
	var in_idx := idx.y
	var leaving := party_active[out_idx]
	var entering := party_reserve[in_idx]
	entering.next_time = _swap_in_time(leaving, entering)
	entering.participated = true
	party_active[out_idx] = entering
	party_reserve[in_idx] = leaving
	_rebuild_roster()
	_prune_provoke()
	if current == leaving:
		current = entering
		turn_started.emit(current)
	return true


## The timeline exactly as preview() would show it right after swap(out_id, in_id), using
## the same rule, without changing any state. Empty when swap() would refuse (not a player
## turn, unknown ids, or a fallen reserve). For the Swap menu's timeline chips (pillar 4).
func preview_swap(out_id: StringName, in_id: StringName, count: int = CtbTimeline.PREVIEW_LENGTH) -> Array[TurnEntry]:
	var idx := _swap_indices(out_id, in_id)
	if idx.x < 0:
		return []
	var leaving := party_active[idx.x]
	var entering := party_reserve[idx.y]
	var roster := _field()
	roster[idx.x] = entering  # party slots come first in _field(), in active order
	var tl := CtbTimeline.new()
	tl.set_roster(roster)
	return tl.predict(count, null, Formulas.DEFAULT_RANK, null, 0, {}, {entering: _swap_in_time(leaving, entering)})


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
	if not target.is_alive():
		# A bounce can never pick a fallen unit, but a second hit on a unit felled by the first can.
		hit["hit"] = false
		return hit
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
				_variance(),
				target.affinity_for(element),
				crit,
				target.has_status(&"protect"),
				actor.break_damage_cap
			)
			hit["crit"] = crit
			hit["amount"] = -target.apply_damage(dmg)
			if dmg > 0:
				target.statuses.erase(&"confuse")  # a physical blow snaps a confused unit out of it
		&"magical":
			var dmg_m := Formulas.damage(
				power,
				actor.effective_magic(),
				actor.level,
				target.effective_magic_defense(),
				_variance(),
				target.affinity_for(element),
				false,
				target.has_status(&"shell"),
				actor.break_damage_cap
			)
			hit["amount"] = -target.apply_damage(dmg_m)
		&"heal":
			var amt := Formulas.heal_amount(
				power, actor.effective_magic(), actor.level, _variance(), actor.break_damage_cap
			)
			hit["amount"] = -target.restore_hp(amt)  # Zombie: the same amount harms instead
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
			if target.add_status(sid, int(inf.get("duration", row.get("default_duration", -1)))):
				added.append(sid)
				if sid == &"provoke":
					target.provoker_id = actor.id
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
			actor.restore_hp(Formulas.regen_heal(actor.max_hp))  # Zombie: Regen harms
	actor.tick_statuses()  # Doom may fell the actor here
	actor.turns_taken += 1
	if _check_outcome():
		return
	_advance()


func _advance() -> void:
	current = null
	_prune_provoke()
	var lost_turns := 0
	while outcome == &"":
		var actor := timeline.next_actor()
		if actor == null:
			_check_outcome()
			return
		now = actor.next_time
		if actor.has_status(&"stop") or actor.has_status(&"sleep"):
			# The turn is lost; statuses still count down so Stop/Sleep wear off.
			actor.next_time = now + Formulas.action_delay(actor.agility, Formulas.DEFAULT_RANK, actor.speed_mult())
			if actor.tick_statuses() and _check_outcome():  # Doom counts lost turns too
				return
			_prune_provoke()
			lost_turns += 1
			if lost_turns >= MAX_CONSECUTIVE_LOST_TURNS:
				push_error("BattleEngine: nobody can act (permanent Stop/Sleep); ruling a defeat")
				_finish(OUTCOME_DEFEAT)
			continue
		current = actor
		turn_started.emit(actor)
		return


## Petrified combatants count as KO here: is_alive() is false for stone.
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


## Filters `targets` to those `sk` may legally hit: alive, deduplicated, on the side its
## "target" field names, and exactly one for single-target skills.
func _valid_targets(actor: BattleCombatant, sk: Dictionary, targets: Array[BattleCombatant]) -> Array[BattleCombatant]:
	var kind := String(sk.get("target", "single_foe"))
	var out: Array[BattleCombatant] = []
	for t in targets:
		if t == null or not t.is_alive() or out.has(t):
			continue
		var is_foe := t.team != actor.team
		match kind:
			"single_foe", "all_foes":
				if not is_foe:
					continue
			"single_ally", "all_allies":
				if is_foe or not party_active.has(t) and t.team == BattleCombatant.TEAM_PARTY:
					continue
			"self":
				if t != actor:
					continue
		out.append(t)
	if kind in ["single_foe", "single_ally", "self"] and out.size() > 1:
		out.resize(1)
	return out


## Combatants whose provoker fell or left the field lose Provoke at once.
func _prune_provoke() -> void:
	for c in _field():
		if c.has_status(&"provoke") and _valid_provoker(c) == null:
			c.statuses.erase(&"provoke")
			c.provoker_id = &""


func _valid_provoker(c: BattleCombatant) -> BattleCombatant:
	if c.provoker_id == &"":
		return null
	for p in _field():
		if p.id == c.provoker_id:
			return p if p.is_alive() else null
	return null


## (active index, reserve index) for a legal swap, or (-1, -1) when swap() must refuse.
func _swap_indices(out_id: StringName, in_id: StringName) -> Vector2i:
	if not is_party_turn():
		return Vector2i(-1, -1)
	var out_idx := _index_of(party_active, out_id)
	var in_idx := _index_of(party_reserve, in_id)
	if out_idx < 0 or in_idx < 0 or not party_reserve[in_idx].is_alive():
		return Vector2i(-1, -1)
	return Vector2i(out_idx, in_idx)


## The swap rule (docs/kb/design/battle_ctb.md): a living leaver hands over its slot (never
## earlier than now); a fallen one makes the entrant wait a default-rank delay from now.
func _swap_in_time(leaving: BattleCombatant, entering: BattleCombatant) -> int:
	if leaving.is_alive():
		return maxi(leaving.next_time, now)
	return now + Formulas.action_delay(entering.agility, Formulas.DEFAULT_RANK, entering.speed_mult())


func _rebuild_roster() -> void:
	timeline.set_roster(_field())


## Hero `level` is the fixed value from characters.json (ADR 0012): growth comes only from
## Lattice stats, so a modifier that touches `level` is undone.
func _make_party_member(cid: StringName) -> BattleCombatant:
	var c := BattleCombatant.from_dict(cid, BattleCombatant.TEAM_PARTY, db.characters[cid])
	var fixed_level := c.level
	if party_modifier.is_valid():
		party_modifier.call(c)
		if c.level != fixed_level:
			push_error("BattleEngine: party_modifier changed %s's level; hero level is fixed (ADR 0012)" % cid)
			c.level = fixed_level
	return c


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
