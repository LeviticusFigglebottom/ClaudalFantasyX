class_name BattleSetPiece
extends RefCounted
## Set-piece battle rules (M3-CMB-01: Ch8's Fisher Stair, act1_ch08.md §5a; the schema is
## docs/kb/design/set_piece_battles.md, the decision ADR 0039). Static helpers the engine and
## BossMechanics call at fixed points. Headless and Node-free; the only randomness is the engine's
## seeded rng (initial ticks and AI draws, as for any combatant).
##
##   encounters.json "entries": [{id, name_key, side: "party"|"enemy", role: "ward"|"tide"|"guest",
##                 agility, skills, ai, delay_immune?, summon_cap?, joins_at_phase?}]
##                 Scripted timeline entries: no HP (never KO'd), never a target but of a "ward"
##                 skill, never counted for victory or defeat. Each acts on its own turns with its
##                 data AI (EnemyAI rules, charges included). joins_at_phase: off the field until an
##                 enemy enters that phase (the Reach's Surge). summon_cap: its summons add nothing
##                 while that many targetable foes stand.
##   encounters.json "objective": {ward, quota, from_phase?, outcome?}: the battle ends in `outcome`
##                 (victory, or scripted_escape) once the ward has taken `quota` acted turns (since
##                 from_phase began, when set). Felling every foe does not end such a fight. The foes
##                 still standing withdraw (no XP, lume or drops).
##   encounters.json "locked_active": [hero ids], "locked_key": a living locked hero can't be swapped
##                 out (swap_refusal; the menu says locked_key). One in reserve at setup moves in.
##   encounters.json "unavailable": [hero ids], "unavailable_key": left out of the battle at setup.
##   encounters.json "attack_override": {hero id: skill id}: that hero's Attack plays this skill.
##   skills.json   "target": "ward": the opposing (or own) ward entry. From a foe, it lands on the
##                 ward's coverer, or on the actor's provoker, instead (intercepted; "on_cover": the
##                 skill row resolved on them then, e.g. a physical blow for a grip).
##                 "covers": "ward": the user covers the ward until its next turn (Hold the Stair).
##                 "counter": skill id: until its next turn the user answers each landed physical
##                 hit from a foe with that skill on the attacker (Stand Firm).
##                 "withdraws": true: a landed target leaves the field, not felled (Storm-Call).
##                 "spares_tag": tag: never lands on a foe carrying the tag ("rooted" polyps).
##                 "pushes_ward": ranks: after the hits, the opposing ward is pushed back (Breach).
##   enemies.json  phase rows "untargetable", "damage_immune", "spawn_bound" (spawned foes are bound
##                 to the phase's field), "field_rules": [{on: party|enemy|ward, status, duration?}]
##                 (while the phase's field is up, each such combatant gains the status at the start
##                 of its turn: storm_dark's Darkness and the Climb's Slow). "hp_floor_pct" on a row.

const ROLE_WARD := &"ward"
const ROLE_TIDE := &"tide"
const ROLE_GUEST := &"guest"
const ROLES: Array[StringName] = [ROLE_WARD, ROLE_TIDE, ROLE_GUEST]
const SIDE_PARTY := "party"
const TARGET_WARD := "ward"
const RULE_ON_PARTY := "party"
const RULE_ON_ENEMY := "enemy"
const RULE_ON_WARD := "ward"
## swap() refusal for a locked hero (the menu shows the encounter's locked_key).
const FAIL_LOCKED := &"locked"


## `ids` without the heroes encounter row `enc` names "unavailable" (Kerrid is not with the party).
static func available_ids(ids: Array[StringName], enc: Dictionary) -> Array[StringName]:
	var out: Array[StringName] = []
	var gone: Array = enc.get("unavailable", [])
	for cid in ids:
		if not gone.has(String(cid)):
			out.append(cid)
	return out


## Reads encounter row `enc`'s set-piece keys into `engine` (after the party and foes are built).
static func setup(engine: BattleEngine, enc: Dictionary) -> void:
	engine.entries.clear()
	engine.pending_entries.clear()
	engine.field_rules.clear()
	for r: Variant in enc.get("entries", []):
		var row: Dictionary = r
		var c := make_entry(row)
		var phase := str(row.get("joins_at_phase", ""))
		if phase == "":
			engine.entries.append(c)
		else:
			engine.pending_entries.append({"phase": phase, "entry": c})
	engine.objective = (enc.get("objective", {}) as Dictionary).duplicate(true)
	engine.objective_count = 0
	engine.locked_active.clear()
	for cid: Variant in enc.get("locked_active", []):
		engine.locked_active.append(StringName(str(cid)))
	engine.locked_key = str(enc.get("locked_key", ""))
	engine.unavailable.clear()
	for cid: Variant in enc.get("unavailable", []):
		engine.unavailable.append(StringName(str(cid)))
	engine.unavailable_key = str(enc.get("unavailable_key", ""))
	_override_attacks(engine, enc.get("attack_override", {}))
	_seat_locked(engine)


## A scripted timeline entry from an encounters.json "entries" row (see the class comment).
static func make_entry(row: Dictionary) -> BattleCombatant:
	var stats := {"level": 1, "hp": 1, "agility": int(row.get("agility", 0))}
	var d := {"name_key": row.get("name_key", ""), "stats": stats, "skills": row.get("skills", [])}
	d["ai"] = row.get("ai", [])
	d["delay_immune"] = row.get("delay_immune", false)
	var team := BattleCombatant.TEAM_PARTY if str(row.get("side", "")) == SIDE_PARTY else BattleCombatant.TEAM_ENEMY
	var c := BattleCombatant.from_dict(StringName(str(row.get("id", ""))), team, d)
	c.entry_role = StringName(str(row.get("role", ROLE_WARD)))
	c.summon_cap = int(row.get("summon_cap", -1))
	return c


## Puts every pending entry that joins at `phase_id` on the field, acting a default-rank delay from
## now (time never runs backwards). Returns them.
static func join_for_phase(engine: BattleEngine, phase_id: String) -> Array[BattleCombatant]:
	var joined: Array[BattleCombatant] = []
	for p in engine.pending_entries.duplicate():
		if str(p["phase"]) != phase_id:
			continue
		var c: BattleCombatant = p["entry"]
		c.next_time = engine.now + Formulas.action_delay(c.agility, Formulas.DEFAULT_RANK, c.speed_mult())
		engine.entries.append(c)
		engine.pending_entries.erase(p)
		joined.append(c)
	if not joined.is_empty():
		engine.rebuild_roster()
	return joined


## The battle's ward entry (the Climb), or null.
static func ward(engine: BattleEngine) -> BattleCombatant:
	for e in engine.entries:
		if e.entry_role == ROLE_WARD:
			return e
	return null


## Why `out_id` may not be swapped out now: FAIL_LOCKED for a living locked hero, else &"".
static func swap_refusal(engine: BattleEngine, out_id: StringName) -> StringName:
	var c := engine.find(out_id)
	if c != null and c.is_alive() and engine.locked_active.has(out_id) and engine.party_active.has(c):
		return FAIL_LOCKED
	return &""


## Who takes `sk` from `actor` instead of the ward it aims at: the actor's provoker, else the ward's
## coverer (on the field and standing). Null when the skill is not a ward skill or nobody steps in.
static func interceptor(engine: BattleEngine, actor: BattleCombatant, sk: Dictionary) -> BattleCombatant:
	var w := ward(engine)
	if str(sk.get("target", "")) != TARGET_WARD or w == null or w.team == actor.team:
		return null
	var guards := engine.living_allies_of(w)
	if actor.has_status(&"provoke"):
		for g in guards:
			if g.id == actor.provoker_id:
				return g
	for g in guards:
		if g.id == w.covered_by:
			return g
	return null


## The row a ward skill resolves as on the one who intercepts it ("on_cover"), else the skill itself.
static func cover_row(engine: BattleEngine, sk: Dictionary) -> Dictionary:
	var row := engine.db.skill(StringName(str(sk.get("on_cover", ""))))
	return row if not row.is_empty() else sk


## At the start of `actor`'s acted turn: its cover and counter stance end, and the field rules in
## force add their statuses to it.
static func on_turn_start(engine: BattleEngine, actor: BattleCombatant) -> void:
	for e in engine.entries:
		if e.covered_by == actor.id:
			e.covered_by = &""
	actor.counter_skill = &""
	for f in engine.fields:
		for r: Variant in engine.field_rules.get(f, []):
			var rule: Dictionary = r
			if _rule_applies(str(rule.get("on", "")), actor):
				var sid := StringName(str(rule.get("status", "")))
				var dur := int(rule.get("duration", engine.db.statuses.get(sid, {}).get("default_duration", -1)))
				actor.add_status(sid, dur)


static func _rule_applies(on: String, c: BattleCombatant) -> bool:
	match on:
		RULE_ON_PARTY:
			return c.team == BattleCombatant.TEAM_PARTY and not c.is_entry()
		RULE_ON_ENEMY:
			return c.team == BattleCombatant.TEAM_ENEMY and not c.is_entry()
		RULE_ON_WARD:
			return c.entry_role == ROLE_WARD
	return false


## After `actor`'s acted turn: the objective's ward counts one more turn while the objective runs.
static func on_turn_end(engine: BattleEngine, actor: BattleCombatant) -> void:
	if objective_running(engine) and String(actor.id) == str(engine.objective.get("ward", "")):
		engine.objective_count += 1


## True while the objective counts: the encounter has one and its from_phase (if any) has begun.
static func objective_running(engine: BattleEngine) -> bool:
	if engine.objective.is_empty():
		return false
	var from := str(engine.objective.get("from_phase", ""))
	if from == "":
		return true
	for e in engine.enemies:
		if e.hp > 0 and BossMechanics.phase_id(e) == from:
			return true
	return false


## The outcome the objective has reached, or &"" (quota not met, or no objective).
static func objective_outcome(engine: BattleEngine) -> StringName:
	if engine.objective.is_empty() or engine.objective_count < objective_quota(engine):
		return &""
	return StringName(str(engine.objective.get("outcome", BattleEngine.OUTCOME_VICTORY)))


static func objective_quota(engine: BattleEngine) -> int:
	return maxi(int(engine.objective.get("quota", 1)), 1)


## The foes still standing pull back (the objective is met): they withdraw, giving nothing.
static func withdraw_standing(engine: BattleEngine) -> void:
	for e in engine.enemies:
		if e.is_alive():
			e.withdraw()


## A landed physical hit of `sk` from `actor` on a combatant in a counter stance is answered at once:
## the stance's skill resolves on the attacker, appended to `result` with "counter_by".
static func counters(engine: BattleEngine, actor: BattleCombatant, sk: Dictionary, result: ActionResult) -> void:
	if str(sk.get("kind", "")) != "physical" or actor.is_entry():
		return
	for hit in result.hits.duplicate():
		var t := engine.find(StringName(str(hit.get("target_id", ""))))
		if t == null or t.counter_skill == &"" or t.team == actor.team or not bool(hit.get("hit", false)):
			continue
		if not t.is_alive() or not actor.is_alive():
			continue
		var back := BattleHits.resolve(engine, t, actor, engine.db.skill(t.counter_skill))
		back["counter_by"] = t.id
		result.hits.append(back)


## After `actor` resolved `sk`: a cover, a counter stance, withdrawals and a ward push.
static func after_action(engine: BattleEngine, actor: BattleCombatant, sk: Dictionary, result: ActionResult) -> void:
	var w := ward(engine)
	if str(sk.get("covers", "")) == TARGET_WARD and w != null and actor.is_alive():
		w.covered_by = actor.id
	if str(sk.get("counter", "")) != "" and actor.is_alive():
		actor.counter_skill = StringName(str(sk["counter"]))
	if bool(sk.get("withdraws", false)):
		for hit in result.hits:
			var t := engine.find(StringName(str(hit.get("target_id", ""))))
			if t != null and t.team != actor.team and t.is_alive() and bool(hit.get("hit", false)):
				t.withdraw()
				hit["withdrawn"] = true
	var ranks := int(sk.get("pushes_ward", 0))
	if ranks > 0 and w != null and w.team != actor.team:
		var push := {"target_id": w.id, "hit": true, "crit": false, "amount": 0, "statuses_added": []}
		push["delay_ticks"] = engine.push_delay(w, ranks)
		result.hits.append(push)


## Whether `actor`'s summon may add a foe: no cap, or fewer targetable foes than its cap stand.
static func may_summon(engine: BattleEngine, actor: BattleCombatant) -> bool:
	if actor.summon_cap < 0:
		return true
	var standing := 0
	for e in engine.enemies:
		if e.is_alive() and not e.untargetable:
			standing += 1
	return standing < actor.summon_cap


## True when `sk` must not land on `t` (its "spares_tag" is on it: Storm-Call leaves the rooted).
static func spares(sk: Dictionary, t: BattleCombatant) -> bool:
	var tag := StringName(str(sk.get("spares_tag", "")))
	return tag != &"" and t.tags.has(tag)


## A phase row's set-piece keys on enemy `e` (BossMechanics._enter_phase), then the entries that
## join at this phase. Returns the entries that joined.
static func enter_phase(engine: BattleEngine, e: BattleCombatant, row: Dictionary) -> Array[BattleCombatant]:
	if row.has("untargetable"):
		e.untargetable = bool(row["untargetable"])
	if row.has("damage_immune"):
		e.damage_immune = bool(row["damage_immune"])
	var f := StringName(str(row.get("field", "")))
	if f != &"" and row.has("field_rules"):
		engine.field_rules[f] = (row["field_rules"] as Array).duplicate(true)
	return join_for_phase(engine, str(row.get("id", "")))


## Hero `c` plays its encounter's attack override in place of "attack" (see the class comment).
static func _override_attacks(engine: BattleEngine, overrides: Dictionary) -> void:
	for c in engine.party_active + engine.party_reserve:
		var sid := StringName(str(overrides.get(String(c.id), "")))
		if sid == &"":
			continue
		var at := c.skills.find(&"attack")
		if c.skills.has(sid):
			c.skills.erase(&"attack")
		elif at >= 0:
			c.skills[at] = sid
		else:
			c.skills.push_front(sid)
		c.attack_skill = sid


## A locked hero set in reserve takes the last active slot held by an unlocked hero.
static func _seat_locked(engine: BattleEngine) -> void:
	for cid in engine.locked_active:
		var r := -1
		for i in engine.party_reserve.size():
			if engine.party_reserve[i].id == cid:
				r = i
		if r < 0:
			continue
		if engine.party_active.size() < BattleEngine.MAX_ACTIVE:
			engine.party_active.append(engine.party_reserve[r])
			engine.party_reserve.remove_at(r)
			continue
		for a in range(engine.party_active.size() - 1, -1, -1):
			if not engine.locked_active.has(engine.party_active[a].id):
				var out := engine.party_active[a]
				engine.party_active[a] = engine.party_reserve[r]
				engine.party_reserve[r] = out
				break
