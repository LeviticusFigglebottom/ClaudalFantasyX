class_name SimPolicy
extends RefCounted
## A party-side decision maker for the balancing simulator (M1-CMB-05, SPEC §6.9). Subclasses
## override decide(). Policies only use the engine's public API, never engine.rng, so a
## policy can't change the battle's random stream except through the actions it picks.
## Every turn must end: take_turn() falls back to the basic attack if decide() did not.

## Items used this battle. Items don't exist yet (Progression), so this stays 0; a policy that
## uses one increments it so the report's item column has a hook.
var items_used := 0
## The party's items for this battle (BattleSim sets it from the suite's loadout).
var items: BattleItemSource = BattleItemSource.new()
## Tunables from game/data/battle/sim_policies.json for this policy (may be empty).
var config: Dictionary = {}
## M2-CMB-01: the battle's Swell rules (null: no Swell) and the quality its inputs are played at.
var swell: BattleSwell
var swell_quality: StringName = &""
## Techniques unleashed this battle.
var swells_used := 0
## A ready healing technique waits until an active ally is below this share of max HP (percent;
## BattleSim sets it from sim_policies.json "swell_heal_below_pct").
var swell_heal_below_pct := 100


func policy_name() -> StringName:
	return &"base"


## Called once per battle before begin().
func reset() -> void:
	items_used = 0
	swells_used = 0


## Plays the current party turn. May swap first; must end with an action that ends the turn.
func take_turn(engine: BattleEngine) -> void:
	var actor := engine.current
	var now := engine.now
	if unleash_vowbound(engine) or unleash_swell(engine):
		return
	decide(engine)
	if engine.outcome == &"" and engine.current == actor and engine.now == now and engine.is_party_turn():
		_basic(engine)


## Override: false for a policy that never opens the Swell command (balance_targets.md).
func unleashes_swell() -> bool:
	return true


## Override: choose swaps and one action for engine.current.
func decide(engine: BattleEngine) -> void:
	_basic(engine)


# --- shared helpers ----------------------------------------------------------------------


## A ready Swell goes first (a player rarely sits on a full gauge; naive never opens it, see
## unleashes_swell): the actor's first technique with targets, its input played at swell_quality.
## Single-foe techniques aim at the policy's focus foe (swell_focus; the provoker when Provoked),
## group ones at every foe; a healing one waits for a hurt ally (swell_heal_below_pct; one other
## than the actor for an "all_other_allies" row, M2-CMB-02). True when
## a technique was unleashed.
func unleash_swell(engine: BattleEngine) -> bool:
	var actor := engine.current
	if swell == null or not unleashes_swell() or not swell.is_ready(actor):
		return false
	for tid in swell.techniques(actor):
		var targets := _swell_targets(engine, actor, tid)
		if targets.is_empty():
			continue
		var res := swell.perform(tid, targets, SwellInput.scripted_result(swell.input_for(actor), swell_quality))
		if res.ok:
			swells_used += 1
			return true
	return false


## M2-CMB-05: a called Vowbound's full gauge goes first too, its finisher aimed like a technique
## (_swell_targets; Floodnet hits every foe). Only a policy that opens the Swell row. True if unleashed.
func unleash_vowbound(engine: BattleEngine) -> bool:
	var vb := engine.vowbound
	if not unleashes_swell() or vb.unleash_refusal(engine) != &"":
		return false
	var targets := _swell_targets(engine, engine.current, vb.finisher(engine.current))
	if targets.is_empty() or not vb.unleash(engine, targets).ok:
		return false
	swells_used += 1
	return true


## M2-CMB-05, the call rule (sim_policies.json "call_vowbound"): "at_once" calls the first
## Vowbound the actor may call (vowbound.callable_ids) as soon as it may, and it stays out until it
## falls or the battle ends. "on_field" calls only while a field is up (the flood rises; the
## Drownbell's flood is the model), keeps it out while the field holds, and dismisses
## it on its first turn after the field is gone. "field_up" (M2-FP-17, the flood_call policy) calls
## only while a field is up and never dismisses: it stays out until it falls or the battle ends.
## Unset: never. True if it called or dismissed.
func call_vowbound(engine: BattleEngine) -> bool:
	var rule := StringName(str(config.get("call_vowbound", "")))
	if rule == &"on_field" and engine.fields.is_empty():
		return engine.vowbound.dismiss_refusal(engine) == &"" and engine.dismiss()
	if rule == &"" or (rule == &"field_up" and engine.fields.is_empty()):
		return false
	var ids := engine.vowbound.callable_ids(engine)
	return not ids.is_empty() and engine.summon(ids[0])


func _swell_targets(engine: BattleEngine, actor: BattleCombatant, tid: StringName) -> Array[BattleCombatant]:
	var row := engine.db.skill(tid)
	var foes := engine.living_foes_of(actor)
	var kind := String(row.get("target", "single_foe"))
	# M2-CMB-02: a song for the others waits for one of them to be hurt, not the singer.
	var allies := engine.living_other_allies_of(actor) if kind == "all_other_allies" else engine.living_allies_of(actor)
	match kind:
		"all_foes":
			return foes
		"all_allies", "all_other_allies", "single_ally":
			var hurt: BattleCombatant = null
			for c in allies:
				if (
					c.hp * 100 < c.max_hp * swell_heal_below_pct
					and (hurt == null or c.hp * hurt.max_hp < hurt.hp * c.max_hp)
				):
					hurt = c
			if hurt == null:
				return [] as Array[BattleCombatant]
			return _one(hurt) if kind == "single_ally" else allies
	if foes.is_empty():
		return foes
	var forced := engine.forced_target(actor, tid)
	var focus := forced if forced != null else swell_focus(engine, actor)
	return _one(focus if focus != null else lowest_hp(foes))


## Override: the foe a single-foe technique aims at when nothing forces one (M2-NIT-03), so a
## policy's Swell follows the same target as its other actions. Default: the lowest-HP foe.
func swell_focus(engine: BattleEngine, actor: BattleCombatant) -> BattleCombatant:
	return lowest_hp(engine.living_foes_of(actor))


## Uses the first held item with an effect of `effect_type` that `target` may receive. Counts it.
func use_item_with(engine: BattleEngine, effect_type: StringName, target: BattleCombatant) -> bool:
	for iid in items.usable():
		var action := items.action_for(iid)
		if not BattleEngine.item_can_target(action, target):
			continue
		for eff in action.effects:
			if StringName(str(eff.get("type", ""))) == effect_type:
				if engine.use_item(iid, _one(target), items).ok:
					items_used += 1
					return true
	return false


## Basic attack on the first living foe (the provoker if Provoked). Escapes as a last resort
## so a battle can never stall on a party with nothing usable.
func _basic(engine: BattleEngine) -> void:
	var actor := engine.current
	var sid := engine.basic_attack(actor)
	var foes := engine.living_foes_of(actor)
	if sid != &"" and not foes.is_empty():
		var forced := engine.forced_target(actor, sid)
		if engine.perform(sid, _one(forced if forced != null else foes[0])).ok:
			return
	if not engine.escape() and engine.current == actor and engine.outcome == &"":
		push_error("SimPolicy: %s could not act" % actor.id)


## Uses `skill_id` on `target`, honouring Provoke for single-foe skills. True on success.
static func use(engine: BattleEngine, skill_id: StringName, target: BattleCombatant) -> bool:
	var forced := engine.forced_target(engine.current, skill_id)
	var targets: Array[BattleCombatant] = []
	var kind := String(engine.db.skill(skill_id).get("target", "single_foe"))
	if kind == "all_foes":
		targets = engine.living_foes_of(engine.current)
	elif kind == "all_allies":
		targets = engine.living_allies_of(engine.current)
	elif kind == "all_other_allies":
		targets = engine.living_other_allies_of(engine.current)
	else:
		targets.append(forced if forced != null else target)
	return engine.perform(skill_id, targets).ok


## Mean expected damage of `skill_id` from `actor` on `target`: the real formula at mean
## variance, without crits, times the hit chance. 0 for non-damaging skills and for single-target
## magic the target would Reflect. Deterministic: no RNG.
static func expected_damage(
	engine: BattleEngine, actor: BattleCombatant, skill_id: StringName, target: BattleCombatant
) -> float:
	var sk := engine.db.skill(skill_id)
	var kind := String(sk.get("kind", ""))
	if not kind in ["physical", "magical"]:
		return 0.0
	if engine.reflect_recipient(actor, target, sk) != target:
		return 0.0
	var power := int(sk.get("power", 0))
	var element := StringName(str(sk.get("element", "none")))
	var mean_var := (Formulas.VARIANCE_MIN_PCT + Formulas.VARIANCE_MAX_PCT) / 2
	if kind == "physical":
		var hit := Formulas.hit_chance(
			int(sk.get("accuracy", 100)), actor.accuracy, target.evasion, actor.has_status(&"darkness")
		)
		var dmg := Formulas.damage(
			power,
			actor.effective_strength(),
			actor.level,
			target.effective_defense(),
			mean_var,
			target.affinity_for(element),
			false,
			target.has_status(&"protect"),
			actor.break_damage_cap
		)
		return dmg * hit / 100.0
	return float(
		Formulas.damage(
			power,
			actor.effective_magic(),
			actor.level,
			target.effective_magic_defense(),
			mean_var,
			target.affinity_for(element),
			false,
			target.has_status(&"shell"),
			actor.break_damage_cap
		)
	)


## The affordable damaging skill with the best expected damage per rank (damage per unit
## of time, the CTB currency) on `target`. Group skills count every living foe.
static func best_damage_skill(engine: BattleEngine, actor: BattleCombatant, target: BattleCombatant) -> StringName:
	var best := &""
	var best_rate := -1.0
	for sid in usable_skills(engine, actor):
		var sk := engine.db.skill(sid)
		var total := 0.0
		if String(sk.get("target", "single_foe")) == "all_foes":
			for f in engine.living_foes_of(actor):
				total += expected_damage(engine, actor, sid, f)
		elif String(sk.get("target", "single_foe")) == "single_foe":
			total = expected_damage(engine, actor, sid, target)
		var rate := total / maxi(int(sk.get("rank", Formulas.DEFAULT_RANK)), 1)
		if total > 0.0 and rate > best_rate:
			best = sid
			best_rate = rate
	return best if best != &"" else engine.basic_attack(actor)


## Skills `actor` can pay for and isn't blocked from (Silence, a field clear with no field up).
static func usable_skills(engine: BattleEngine, actor: BattleCombatant) -> Array[StringName]:
	var out: Array[StringName] = []
	for sid in actor.skills:
		var sk := engine.db.skill(sid)
		if sk.is_empty() or int(sk.get("mp_cost", 0)) > actor.mp:
			continue
		if bool(sk.get("magic", false)) and actor.has_status(&"silence"):
			continue
		if BossMechanics.refusal(engine, sk) != &"":
			continue
		out.append(sid)
	return out


## A usable skill that inflicts a Break `target` lacks, or &"".
static func break_skill(engine: BattleEngine, actor: BattleCombatant, target: BattleCombatant) -> StringName:
	for sid in usable_skills(engine, actor):
		var sk := engine.db.skill(sid)
		if String(sk.get("target", "single_foe")) != "single_foe":
			continue
		for inf: Variant in sk.get("statuses", []):
			var status := StringName(str((inf as Dictionary).get("id", "")))
			if String(status).ends_with("_break") and not target.has_status(status):
				return sid
	return &""


## The party member whose niche answers this enemy (enemies.json "role_answer"), or &"".
static func role_answer(engine: BattleEngine, foe: BattleCombatant) -> StringName:
	var row: Dictionary = engine.db.enemies.get(StringName(String(foe.id).get_slice("#", 0)), {})
	return StringName(str(row.get("role_answer", "")))


static func lowest_hp(list: Array[BattleCombatant]) -> BattleCombatant:
	var best: BattleCombatant = null
	for c in list:
		if best == null or c.hp < best.hp:
			best = c
	return best


static func _one(c: BattleCombatant) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = [c]
	return out
