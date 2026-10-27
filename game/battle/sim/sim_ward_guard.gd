class_name SimWardGuard
extends RefCounted
## The ward guard (M3-CMB-01, act1_ch08.md §9 Combat item 9; balance_targets.md): how a player
## protects a set piece's ward (the Climb). Static and read-only but for the action it takes; never
## touches engine.rng. Played first by the `ward_guard` policy and, with sim_policies.json
## "guard_ward": true, by `role_answer` and `smart` (the role answer to a grip is Toma's shield).
##   1. A threat to the ward before the actor's next turn (threat()): a foe whose next turn fires a
##      telegraphed ward skill (its timeline intent), or whose AI would pick a ward skill now. The
##      actor covers the ward with its "covers" skill (Hold the Stair) if nobody covers it, else
##      Provokes a second threat onto itself.
##   2. No Haste on the ward and no field rule on it (storm_dark's Slow would erase it at once): the
##      actor hauls (a ward skill that adds Haste: Liss's Haul).


## Plays the guard's action for the current actor when one applies: only while the objective counts
## (the Reach's Climb matters from the Breach on). True when it acted.
static func act(engine: BattleEngine) -> bool:
	var actor := engine.current
	var w := engine.ward()
	if w == null or w.team != actor.team or not BattleSetPiece.objective_running(engine):
		return false
	var threats := threats_before_next_turn(engine, actor, w)
	if not threats.is_empty():
		var cover := skill_with(engine, actor, "covers")
		if w.covered_by == &"" and cover != &"" and SimPolicy.use(engine, cover, actor):
			return true
		var provoke := provoke_skill(engine, actor)
		for t in threats.slice(1 if w.covered_by != &"" else 0):
			if provoke != &"" and not t.has_status(&"provoke") and SimPolicy.use(engine, provoke, t):
				return true
	var haul := haste_ward_skill(engine, actor)
	if haul != &"" and not w.has_status(&"haste") and not _field_rules_on_ward(engine):
		return SimPolicy.use(engine, haul, w)
	return false


## Foes that will use a ward skill on their next turn, if it comes before `actor`'s next turn, in
## timeline order.
static func threats_before_next_turn(
	engine: BattleEngine, actor: BattleCombatant, w: BattleCombatant
) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = []
	var seen: Array[BattleCombatant] = []
	var first := true
	for entry in engine.preview():
		var c := engine.find(entry.combatant_id)
		if c == actor and first:
			first = false
			continue
		if c == actor:
			break
		if c == null or seen.has(c) or c.team == w.team or c.is_entry():
			continue
		seen.append(c)
		if threat(engine, c, entry, w):
			out.append(c)
	return out


## Whether `c`, on the turn `entry` predicts, aims a ward skill at `w`: its telegraphed intent, or
## (not charging) the skills its AI would pick now (EnemyAI.likely_skills).
static func threat(engine: BattleEngine, c: BattleCombatant, entry: TurnEntry, w: BattleCombatant) -> bool:
	if entry.intent != &"":
		return _bites(engine.db.skill(entry.intent), w)
	if c.is_charging():
		return false
	for sid in EnemyAI.likely_skills(engine, c):
		if _bites(engine.db.skill(sid), w):
			return true
	return false


## A usable skill of `actor` whose row has `key` (e.g. "covers"), or &"".
static func skill_with(engine: BattleEngine, actor: BattleCombatant, key: String) -> StringName:
	for sid in SimPolicy.usable_skills(engine, actor):
		if engine.db.skill(sid).has(key):
			return sid
	return &""


## A usable single-foe skill of `actor` that inflicts Provoke, or &"".
static func provoke_skill(engine: BattleEngine, actor: BattleCombatant) -> StringName:
	return _status_skill(engine, actor, "single_foe", &"provoke")


## A usable ward skill of `actor` that adds Haste (Haul), or &"".
static func haste_ward_skill(engine: BattleEngine, actor: BattleCombatant) -> StringName:
	return _status_skill(engine, actor, BattleSetPiece.TARGET_WARD, &"haste")


static func _status_skill(
	engine: BattleEngine, actor: BattleCombatant, target: String, status: StringName
) -> StringName:
	for sid in SimPolicy.usable_skills(engine, actor):
		var sk := engine.db.skill(sid)
		if str(sk.get("target", "")) != target:
			continue
		for inf: Variant in sk.get("statuses", []):
			if StringName(str((inf as Dictionary).get("id", ""))) == status:
				return sid
	return &""


## A ward skill that would cost the ward something: a delay push, or a status it strips.
static func _bites(sk: Dictionary, w: BattleCombatant) -> bool:
	if str(sk.get("target", "")) != BattleSetPiece.TARGET_WARD:
		return false
	if int(sk.get("delay_ranks", 0)) > 0 and not w.delay_immune:
		return true
	for sid: Variant in sk.get("cleanses", []):
		if w.has_status(StringName(str(sid))):
			return true
	return false


static func _field_rules_on_ward(engine: BattleEngine) -> bool:
	for f in engine.fields:
		for r: Variant in engine.field_rules.get(f, []):
			if str((r as Dictionary).get("on", "")) == BattleSetPiece.RULE_ON_WARD:
				return true
	return false
