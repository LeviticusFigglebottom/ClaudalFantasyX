class_name BossMechanics
extends RefCounted
## Data-driven boss rules for BattleEngine (M2-FP-06, the Drownbell; battle_ctb.md "The
## Drownbell"). Static helpers the engine calls at fixed points; headless, deterministic (any
## randomness goes through engine.rng) and Node-free like the rest of the core.
##
##   enemies.json  "phases": [{id, at_hp_pct, name_key?, prompt_key?, skills?, ai?, affinities?,
##                 stats?, delay_immune?, field?, spawn?: [enemy ids], remove?: [enemy ids]}]
##                 Applied in order, once each, at the end of any turn that leaves the enemy alive
##                 at or below at_hp_pct of its max HP (phase_changed, combatants_joined).
##                 "weak_point": {hits, max_delay, name_key}: while the enemy is charging, landed
##                 physical hits from an attacker whose action delay for that skill is at most
##                 max_delay ticks count; `hits` of them break the charge (charge_broken).
##                 "field": the field a combatant is bound to; it falls when that field clears.
##   skills.json   "charge": {skill, turns}: the user telegraphs `skill`, which fires on its own turn
##                 `turns` acted turns from now (the firing one counted) in place of its AI
##                 (charge_started). The timeline shows it as TurnEntry.intent.
##                 "summon": enemy id: adds one enemy to the field (combatants_joined).
##                 "clears_field": field id: ends that field after the hits; every combatant bound
##                 to it falls (field_cleared). Refused with &"no_field" while the field is down,
##                 except on a Swell finisher ("swell": true, e.g. Ilun's Floodnet, ADR 0027 A2):
##                 that one is never refused and clears the field only when it is up.
##                 "requires_flag": story flag: party members only know the skill when the flag is
##                 in BattleEngine.story_flags (passed in at setup; the engine never reads Game).
##                 "cleanses": [status ids]: after the hits, those statuses are lifted off every
##                 target the skill landed on (M3-C05-02: the Cinder Matron's recrust ends a break).
##   enemies.json  "reactions": [{elements, from_phase?, cleanses?, statuses?: [{id, duration?}]}]:
##                 a landed hit of one of `elements` on this enemy, while its phase is from_phase
##                 (or any phase when unset), lifts `cleanses` off it and adds `statuses` (the
##                 Matron's quench: water or cold re-crusts her). The hit records "reacted": true.
##   encounters.json "party_skills": {hero id: [skill ids]}: skills that hero knows for this fight only
##                 (a tutorial fight teaching one: Ch1's Hullgnaw lends Rhen Kick Off; ADR 0034).
##                 Added at setup after the Lattice and the flag locks, never twice.
##   encounters.json "forbidden_skills": {hero id: {"against_tag": tag, "fail_key": loc key}}
##                 (M3-C06-02: Toma will not strike the Stillguard). That hero's offensive skills (a
##                 physical or magical skill aimed at foes) are refused, with FAIL_FORBIDDEN, on any
##                 foe whose enemies.json "tags" hold the tag; the menus grey them out and say why
##                 with fail_key. Its defensive kit (support, heals, Provoke) is untouched.
##   enemies.json  "tags" and "yield_at_hp_pct": see BattleCombatant (a foe that yields or runs on
##                 its feet instead of falling; the fight is won when every foe is down or gone).
##   Set pieces (M3-CMB-01): scripted entries, ward skills, objectives and the phase keys
##                 untargetable, damage_immune, spawn_bound and field_rules: see BattleSetPiece.

## Stats a phase row may override ("hp", "mp" and "level" never change mid-fight).
const PHASE_STATS: Array[String] = [
	"strength", "magic", "defense", "magic_defense", "agility", "accuracy", "evasion", "luck"
]
const FAIL_NO_FIELD := &"no_field"
const FAIL_FORBIDDEN := &"forbidden"
const OFFENSIVE_KINDS: Array[String] = ["physical", "magical"]
const FOE_TARGETS: Array[String] = ["single_foe", "all_foes"]


## Drops `c`'s skills whose row names a requires_flag that is not in `flags`.
static func lock_skills(c: BattleCombatant, db: BattleDB, flags: Array[StringName]) -> void:
	for sid in c.skills.duplicate():
		var flag := StringName(str(db.skill(sid).get("requires_flag", "")))
		if flag != &"" and not flags.has(flag):
			c.skills.erase(sid)


## Adds encounter row `enc`'s "party_skills" to the party members it names (see the class comment).
## A lent skill keeps its requires_flag (M3-CMB-01: Liss's Haul is lent from Wave 2 on, but only
## once the hoist is rigged).
static func lend_skills(engine: BattleEngine, enc: Dictionary) -> void:
	var lent: Dictionary = enc.get("party_skills", {})
	for c in engine.party_active + engine.party_reserve:
		for sid: Variant in lent.get(String(c.id), []):
			var skill_id := StringName(str(sid))
			if not c.skills.has(skill_id):
				c.skills.append(skill_id)
		lock_skills(c, engine.db, engine.story_flags)


## Sets encounter row `enc`'s "forbidden_skills" on the party members it names (see the class comment).
static func forbid_skills(engine: BattleEngine, enc: Dictionary) -> void:
	var rules: Dictionary = enc.get("forbidden_skills", {})
	for c in engine.party_active + engine.party_reserve:
		var row: Dictionary = rules.get(String(c.id), {})
		if row.is_empty():
			continue
		c.forbidden_tag = StringName(str(row.get("against_tag", "")))
		c.forbidden_key = str(row.get("fail_key", ""))


## True for a skill that wounds: physical or magical, aimed at foes.
static func is_offensive(sk: Dictionary) -> bool:
	return str(sk.get("kind", "")) in OFFENSIVE_KINDS and str(sk.get("target", "single_foe")) in FOE_TARGETS


## True when `actor` may not use skill row `sk` on `target` (its forbidden_tag is on the target).
static func forbids(actor: BattleCombatant, sk: Dictionary, target: BattleCombatant) -> bool:
	if actor == null or target == null or actor.forbidden_tag == &"":
		return false
	return target.tags.has(actor.forbidden_tag) and is_offensive(sk)


## True when `sk` is forbidden to `actor` right now: a single-foe skill with no living foe it may
## hit, or a group skill that would touch a forbidden foe. The menus grey it out; the sim skips it.
static func forbidden_now(engine: BattleEngine, actor: BattleCombatant, sk: Dictionary) -> bool:
	if actor == null or actor.forbidden_tag == &"" or not is_offensive(sk):
		return false
	var foes := engine.living_foes_of(actor)
	var group := str(sk.get("target", "single_foe")) == "all_foes"
	for f in foes:
		var hit := forbids(actor, sk, f)
		if group and hit:
			return true
		if not group and not hit:
			return false
	return not group and not foes.is_empty()


## Why skill row `sk` cannot be used now, or &"" if it can: a field clear with that field down
## (a Swell finisher is a full gauge's payoff, never greyed out by a field).
static func refusal(engine: BattleEngine, sk: Dictionary) -> StringName:
	var f := StringName(str(sk.get("clears_field", "")))
	if f != &"" and not engine.fields.has(f) and not bool(sk.get("swell", false)):
		return FAIL_NO_FIELD
	return &""


## At the start of `actor`'s own acted turn. A charge that fires now returns {skill, targets}
## and ends; otherwise the charge counts down and this returns {} (the AI chooses).
static func charged_choice(engine: BattleEngine, actor: BattleCombatant) -> Dictionary:
	if not actor.is_charging():
		return {}
	if actor.charge_left > 1:
		actor.charge_left -= 1
		return {}
	var skill_id := actor.charge_skill
	var row := actor.charge_row
	actor.clear_charge()
	var targets: Array[BattleCombatant] = []
	match str(row.get("target", "single_foe")):
		BattleSetPiece.TARGET_WARD:
			var w := BattleSetPiece.ward(engine)
			if w != null:
				targets.append(w)
		"all_foes":
			targets = engine.living_foes_of(actor)
		"all_allies":
			targets = engine.living_allies_of(actor)
		"self":
			targets.append(actor)
		_:
			var forced := engine.forced_target(actor, skill_id)
			var pool: Array[BattleCombatant] = []
			for f in engine.living_foes_of(actor) if forced == null else ([forced] as Array[BattleCombatant]):
				if not BattleSetPiece.spares(row, f):
					pool.append(f)
			if not pool.is_empty():
				targets.append(pool[engine.rng.randi_range(0, pool.size() - 1)])
	if targets.is_empty():
		return {}
	return {"skill": skill_id, "targets": targets}


## After `actor` resolved skill row `sk` (its hits are on `result`): weak-point hits and
## breaks, then a new charge, a summon and a field clear, in that order.
static func after_action(engine: BattleEngine, actor: BattleCombatant, sk: Dictionary, result: ActionResult) -> void:
	for hit in result.hits:
		var t := engine.find(StringName(str(hit.get("target_id", ""))))
		if t == null or not bool(hit.get("hit", false)) or not counts_on_weak_point(actor, t, sk):
			continue
		t.weak_hits += 1
		hit["weak_point_hits"] = t.weak_hits
		if t.weak_hits >= int(t.weak_point.get("hits", 1)):
			var broken := t.charge_skill
			t.clear_charge()
			BattleParts.on_charge_broken(t, broken)  # M4-A2P-022: a declared part stays broken
			hit["charge_broken"] = broken
			engine.charge_broken.emit(t, broken)
	_cleanse_and_react(engine, sk, result)
	var charge: Dictionary = sk.get("charge", {})
	if not charge.is_empty() and actor.is_alive():
		actor.charge_skill = StringName(str(charge.get("skill", "")))
		actor.charge_left = maxi(int(charge.get("turns", 1)), 1)
		actor.charge_row = engine.db.skill(actor.charge_skill)
		actor.weak_hits = 0
		engine.charge_started.emit(actor, actor.charge_skill, actor.charge_left)
	var summon := StringName(str(sk.get("summon", "")))
	if summon != &"" and BattleSetPiece.may_summon(engine, actor):
		var joined: Array[BattleCombatant] = []
		var c := spawn(engine, summon)
		if c != null:
			joined.append(c)
			engine.combatants_joined.emit(joined)
	var cleared := StringName(str(sk.get("clears_field", "")))
	if cleared != &"" and engine.fields.has(cleared):
		clear_field(engine, cleared)
	BattleSetPiece.after_action(engine, actor, sk, result)


## The skill's "cleanses" on every target it landed on, then each target's "reactions" to the
## hit's element (see the class comment).
static func _cleanse_and_react(engine: BattleEngine, sk: Dictionary, result: ActionResult) -> void:
	var lift: Array = sk.get("cleanses", [])
	for hit in result.hits:
		var t := engine.find(StringName(str(hit.get("target_id", ""))))
		if t == null or not bool(hit.get("hit", false)) or not t.is_alive():
			continue
		for sid: Variant in lift:
			t.statuses.erase(StringName(str(sid)))
		var element := str(hit.get("element", ""))
		for r: Variant in t.reactions:
			var row: Dictionary = r
			var from := str(row.get("from_phase", ""))
			if not (row.get("elements", []) as Array).has(element) or (from != "" and phase_id(t) != from):
				continue
			for sid: Variant in row.get("cleanses", []):
				t.statuses.erase(StringName(str(sid)))
			for inf: Variant in row.get("statuses", []):
				var s := StringName(str((inf as Dictionary).get("id", "")))
				var dur := int(
					(inf as Dictionary).get("duration", engine.db.statuses.get(s, {}).get("default_duration", -1))
				)
				t.add_status(s, dur)
			hit["reacted"] = true


## The id of the phase `e` is in (&"" before its first "phases" row).
static func phase_id(e: BattleCombatant) -> String:
	if e.phase_index < 0 or e.phase_index >= e.phases.size():
		return ""
	return str((e.phases[e.phase_index] as Dictionary).get("id", ""))


## Whether a landed hit of `sk` from `actor` counts on `target`'s weak point right now.
static func counts_on_weak_point(actor: BattleCombatant, target: BattleCombatant, sk: Dictionary) -> bool:
	if target.weak_point.is_empty() or not target.is_charging() or actor.team == target.team:
		return false
	if str(sk.get("kind", "")) != "physical":
		return false
	var rank := int(sk.get("rank", Formulas.DEFAULT_RANK))
	return Formulas.action_delay(actor.agility, rank, actor.speed_mult()) <= int(target.weak_point.get("max_delay", 0))


## For the preview: `sk` from `actor` landing on `target` would be the weak point's breaking hit.
static func would_break(actor: BattleCombatant, target: BattleCombatant, sk: Dictionary) -> bool:
	if not counts_on_weak_point(actor, target, sk):
		return false
	return target.weak_hits + 1 >= int(target.weak_point.get("hits", 1))


## Ends field `field_id`: every living combatant bound to it falls. Emits field_cleared.
static func clear_field(engine: BattleEngine, field_id: StringName) -> Array[BattleCombatant]:
	engine.fields.erase(field_id)
	engine.field_rules.erase(field_id)
	var fallen: Array[BattleCombatant] = []
	for e in engine.enemies:
		if e.is_alive() and e.field == field_id:
			e.fall()
			fallen.append(e)
	engine.field_cleared.emit(field_id, fallen)
	return fallen


## Adds a fresh `eid` (enemies.json) to the field. It first acts a default-rank delay from now
## (time never runs backwards). Ids keep counting past the opening lineup ("spawn_polyp#4").
static func spawn(engine: BattleEngine, eid: StringName) -> BattleCombatant:
	var row: Dictionary = engine.db.enemies.get(eid, {})
	if row.is_empty():
		push_error("BossMechanics: unknown enemy '%s'" % eid)
		return null
	var cid := StringName("%s#%d" % [eid, engine.enemies.size() + 1])
	var c := BattleCombatant.from_dict(cid, BattleCombatant.TEAM_ENEMY, row)
	c.next_time = engine.now + Formulas.action_delay(c.agility, Formulas.DEFAULT_RANK, c.speed_mult())
	engine.enemies.append(c)
	engine.rebuild_roster()
	return c


## Applies every phase whose threshold a living enemy has crossed (end of each acted turn).
static func check_phases(engine: BattleEngine) -> void:
	for e in engine.enemies.duplicate():
		while e.is_alive() and e.phase_index + 1 < e.phases.size():
			var row: Dictionary = e.phases[e.phase_index + 1]
			if e.hp * Formulas.PCT > e.max_hp * int(row.get("at_hp_pct", 0)):
				break
			_enter_phase(engine, e, e.phase_index + 1)


static func _enter_phase(engine: BattleEngine, e: BattleCombatant, index: int) -> void:
	var row: Dictionary = e.phases[index]
	e.phase_index = index
	e.ai_turn_base = e.turns_taken
	e.clear_charge()
	if row.has("skills"):
		e.skills.clear()
		for s: Variant in row["skills"]:
			e.skills.append(StringName(str(s)))
	if row.has("ai"):
		e.ai_rules = (row["ai"] as Array).duplicate(true)
	if row.has("affinities"):
		e.affinities.clear()
		for k: Variant in row["affinities"] as Dictionary:
			e.affinities[StringName(str(k))] = StringName(str(row["affinities"][k]))
	if row.has("delay_immune"):
		e.delay_immune = bool(row["delay_immune"])
	var stats: Dictionary = row.get("stats", {})
	for k: String in PHASE_STATS:
		if stats.has(k):
			e.set(k, int(stats[k]))
	var f := StringName(str(row.get("field", "")))
	if f != &"" and not engine.fields.has(f):
		engine.fields.append(f)
	for other in engine.enemies:
		if other.is_alive() and (row.get("remove", []) as Array).has(String(other.id).get_slice("#", 0)):
			other.fall()
	var joined: Array[BattleCombatant] = []
	for eid: Variant in row.get("spawn", []):
		var c := spawn(engine, StringName(str(eid)))
		if c != null:
			joined.append(c)
			c.field = f if bool(row.get("spawn_bound", false)) else c.field
	joined.append_array(BattleSetPiece.enter_phase(engine, e, row))
	engine.phase_changed.emit(e, StringName(str(row.get("id", ""))))
	if not joined.is_empty():
		engine.combatants_joined.emit(joined)
