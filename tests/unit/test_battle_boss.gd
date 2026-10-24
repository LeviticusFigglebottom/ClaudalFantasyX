extends TestCase
## Boss mechanics (BossMechanics, M2-FP-06): phases, the telegraphed charge (the Drownbell's toll)
## and its timeline preview, the weak point (the rim), summons, fields and flag-locked skills.
## Runs on a small fixture DB, so tuning the real Drownbell never breaks these.

const FLAG := &"bound"

var engine: BattleEngine
var events: Array[String] = []


func before_each() -> void:
	engine = BattleEngine.new()
	events = []


# --- phases --------------------------------------------------------------------------------


func test_phase_applies_at_its_threshold_with_swaps_spawns_and_a_signal() -> void:
	_start([&"fast", &"slow"])
	var bell := _bell()
	bell.hp = bell.max_hp / 2 + 1
	BossMechanics.check_phases(engine)
	assert_eq(bell.phase_index, -1, "above 50% the opening phase holds")
	bell.hp = bell.max_hp / 2
	var now := engine.now
	BossMechanics.check_phases(engine)
	assert_eq(bell.phase_index, 0)
	assert_eq(events, ["phase:bell#1:flood", "joined:polyp#2,polyp#3"])
	assert_eq(bell.skills, [&"slam", &"rouse", &"surge"] as Array[StringName])
	assert_eq(bell.affinity_for(&"fire"), &"weak")
	assert_eq(bell.defense, 7)
	assert_eq(bell.agility, 20)
	assert_false(bell.delay_immune, "the phase lifts the opening delay immunity")
	assert_eq(bell.ai_turn_base, bell.turns_taken)
	assert_true(engine.fields.has(&"flood"))
	assert_eq(engine.enemies.size(), 3)
	for p in engine.enemies.slice(1):
		assert_true(p.is_alive())
		assert_eq(p.field, &"flood")
		assert_eq(p.next_time, now + Formulas.action_delay(p.agility, Formulas.DEFAULT_RANK))
	var ids: Array[StringName] = []
	for e in engine.preview():
		ids.append(e.combatant_id)
	assert_true(ids.has(&"polyp#2") and ids.has(&"polyp#3"), "the spawns are on the timeline at once")
	BossMechanics.check_phases(engine)
	assert_eq(engine.enemies.size(), 3, "a phase applies once")


func test_phase_triggers_from_a_real_hit_at_the_end_of_the_turn() -> void:
	_start([&"slow", &"slow2"])
	_until(func() -> bool: return engine.is_party_turn())
	var bell := _bell()
	bell.hp = bell.max_hp / 2 + 5
	assert_true(engine.perform(&"attack", _one(bell)).ok)
	assert_eq(bell.phase_index, 0)
	assert_true(events.has("phase:bell#1:flood"))


func test_a_killing_blow_skips_the_phase() -> void:
	_start([&"slow", &"slow2"])
	_until(func() -> bool: return engine.is_party_turn())
	_bell().hp = 1
	engine.perform(&"attack", _one(_bell()))
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)
	assert_eq(_bell().phase_index, -1)
	assert_eq(engine.enemies.size(), 1)


func test_phase_remove_fells_the_named_enemies() -> void:
	_start([&"fast", &"slow"])
	BossMechanics.spawn(engine, &"polyp")
	(_bell().phases[0] as Dictionary)["remove"] = ["polyp"]
	(_bell().phases[0] as Dictionary)["spawn"] = []
	_bell().hp = 1
	BossMechanics.check_phases(engine)
	assert_false(engine.enemies[1].is_alive())


# --- the charge (toll) and its telegraph -----------------------------------------------------


func test_gather_telegraphs_the_toll_two_bell_turns_ahead() -> void:
	_start([&"slow", &"slow2"])
	_until(func() -> bool: return _bell().is_charging())
	assert_eq(events.filter(func(e: String) -> bool: return e.begins_with("charge:")), ["charge:bell#1:toll:2"])
	var bell_turns: Array[StringName] = []
	for e in engine.preview():
		if e.combatant_id == &"bell#1":
			bell_turns.append(e.intent)
	assert_eq(bell_turns[0], &"", "the next bell turn is a normal one")
	assert_eq(bell_turns[1], &"toll", "the toll shows on the turn after it")
	assert_eq(bell_turns.count(&"toll"), 1)


func test_toll_preview_matches_play_including_its_push() -> void:
	_start([&"slow", &"slow2"])
	_bell().max_hp = 100000
	_bell().hp = 100000
	_until(func() -> bool: return _bell().is_charging())
	var predicted := engine.preview()
	var toll_at := -1
	for i in predicted.size():
		if predicted[i].intent == &"toll":
			toll_at = i
	assert_true(toll_at > 0)
	var actual: Array[Array] = [[engine.current.id, engine.now]]
	engine.turn_started.connect(func(c: BattleCombatant) -> void: actual.append([c.id, engine.now]))
	while actual.size() <= toll_at + 4 and engine.outcome == &"":
		_play_one(&"attack")
	for i in range(0, toll_at + 4):
		assert_eq(actual[i][0], predicted[i].combatant_id, "turn %d actor" % i)
		assert_eq(actual[i][1], predicted[i].time, "turn %d time" % i)


func test_toll_fires_on_its_turn_and_pushes_the_party() -> void:
	_start([&"slow", &"slow2"])
	_until(func() -> bool: return _bell().is_charging() and _bell().charge_left == 1 and engine.current == _bell())
	var before: Dictionary = {}
	for c in engine.party_active:
		before[c] = [c.next_time, c.delays_taken]
	var r := engine.run_enemy_turn()
	assert_eq(r.skill_id, &"toll")
	assert_false(_bell().is_charging())
	for c: BattleCombatant in before:
		var push := Formulas.delay_push(c.agility, 2, int(before[c][1]))
		assert_eq(c.next_time, int(before[c][0]) + push)
	for hit in r.hits:
		assert_true(int(hit.get("delay_ticks", 0)) > 0)


func test_fast_strikes_on_the_rim_break_the_charge() -> void:
	_start([&"fast", &"slow"])
	_until(func() -> bool: return _bell().is_charging())
	var tolled := [false]
	engine.action_resolved.connect(func(r: ActionResult) -> void: tolled[0] = tolled[0] or r.skill_id == &"toll")
	var broke: Array[Dictionary] = []
	engine.action_resolved.connect(
		func(r: ActionResult) -> void:
			for h in r.hits:
				if h.has("charge_broken"):
					broke.append(h)
	)
	var guard := 0
	while _bell().is_charging() and guard < 20:
		guard += 1
		if engine.is_party_turn() and engine.current.id == &"fast":
			assert_true(engine.perform(&"quick", _one(_bell())).ok)
		else:
			_play_one(&"attack")
	assert_false(tolled[0], "the rim broke before the toll")
	assert_true(events.has("broken:bell#1:toll"))
	assert_eq(broke.size(), 1)
	assert_eq(broke[0]["charge_broken"], &"toll")
	assert_eq(_bell().weak_hits, 0)
	for e in engine.preview():
		assert_eq(e.intent, &"")


func test_the_breaking_hit_clears_the_toll_from_the_preview() -> void:
	_start([&"fast", &"slow"])
	_until(func() -> bool: return _bell().is_charging())
	_bell().weak_hits = 1
	_until(func() -> bool: return engine.is_party_turn() and engine.current.id == &"fast")
	assert_true(_bell().is_charging())
	assert_true(_intents(engine.preview()).has(&"toll"))
	assert_false(_intents(engine.preview(&"quick", _bell())).has(&"toll"), "quick would break it")
	assert_true(_intents(engine.preview(&"heavy", _bell())).has(&"toll"), "a slow strike would not")


func test_only_low_delay_physical_hits_count_on_the_weak_point() -> void:
	_start([&"fast", &"slow"])
	var bell := _bell()
	var fast := engine.find(&"fast")
	var slow := engine.find(&"slow")
	var quick := engine.db.skill(&"quick")
	assert_false(BossMechanics.counts_on_weak_point(fast, bell, quick), "nothing counts while not charging")
	bell.charge_skill = &"toll"
	bell.charge_left = 2
	assert_true(BossMechanics.counts_on_weak_point(fast, bell, quick))
	assert_true(BossMechanics.counts_on_weak_point(fast, bell, engine.db.skill(&"attack")), "174 ticks <= 200")
	assert_false(BossMechanics.counts_on_weak_point(fast, bell, engine.db.skill(&"heavy")), "290 ticks")
	assert_false(BossMechanics.counts_on_weak_point(slow, bell, engine.db.skill(&"attack")), "300 ticks")
	assert_false(BossMechanics.counts_on_weak_point(fast, bell, engine.db.skill(&"call")), "magic never")
	slow.add_status(&"haste", 3)
	assert_true(BossMechanics.counts_on_weak_point(slow, bell, engine.db.skill(&"attack")), "hasted: 150")


# --- the flood: spawns, heals, summons, the field and the flag-locked skill --------------------


func test_polyps_heal_the_bell() -> void:
	_start([&"slow", &"slow2"])
	_enter_flood()
	_until(func() -> bool: return engine.current != null and engine.current.field == &"flood")
	_bell().hp = 100
	var r := engine.run_enemy_turn()
	assert_eq(r.skill_id, &"mend")
	assert_eq(r.hits[0]["target_id"], &"bell#1", "largest_ally: the bell, not a polyp")
	assert_eq(_bell().hp, 100 - int(r.hits[0]["amount"]))
	assert_true(_bell().hp > 100)


func test_the_bell_rouses_a_new_polyp_while_the_field_is_up() -> void:
	_start([&"slow", &"slow2"])
	_enter_flood()
	engine.enemies[1].fall()
	events.clear()
	_until(func() -> bool: return engine.current == _bell())
	var now := engine.now
	var r := engine.run_enemy_turn()
	assert_eq(r.skill_id, &"rouse")
	assert_eq(events, ["joined:polyp#4"])
	assert_eq(engine.enemies.size(), 4)
	assert_eq(engine.enemies[3].next_time, now + Formulas.action_delay(10, Formulas.DEFAULT_RANK))


func test_call_needs_its_flag() -> void:
	_start([&"fast", &"slow"])
	assert_false(engine.find(&"fast").skills.has(&"call"), "locked without the story flag")
	assert_true(engine.find(&"fast").skills.has(&"quick"), "unflagged skills stay")
	_until(func() -> bool: return engine.is_party_turn())
	var r := engine.perform(&"call", engine.living_foes_of(engine.current))
	assert_eq(r.fail_reason, &"unknown_skill")


func test_call_is_refused_while_no_field_is_up() -> void:
	engine.story_flags = [FLAG]
	_start([&"fast", &"slow"])
	assert_true(engine.find(&"fast").skills.has(&"call"))
	_until(func() -> bool: return engine.is_party_turn())
	var actor := engine.current
	var mp := actor.mp
	var r := engine.perform(&"call", engine.living_foes_of(actor))
	assert_eq(r.fail_reason, BossMechanics.FAIL_NO_FIELD)
	assert_eq(actor.mp, mp, "a refusal costs nothing")
	assert_eq(engine.current, actor)


func test_call_clears_the_field_and_its_polyps() -> void:
	engine.story_flags = [FLAG]
	_start([&"fast", &"slow"])
	_enter_flood()
	events.clear()
	_until(func() -> bool: return engine.is_party_turn() and engine.current.id == &"fast")
	var r := engine.perform(&"call", engine.living_foes_of(engine.current))
	assert_true(r.ok)
	assert_true(engine.fields.is_empty())
	assert_eq(events, ["cleared:flood:polyp#2,polyp#3"])
	assert_false(engine.enemies[1].is_alive())
	assert_false(engine.enemies[2].is_alive())
	assert_true(_bell().is_alive())
	_until(func() -> bool: return engine.current == _bell())
	assert_eq(engine.run_enemy_turn().skill_id, &"slam", "no field: no more polyps")


func test_turn_mod_counts_from_the_phase_start() -> void:
	_start([&"fast", &"slow"])
	var bell := _bell()
	bell.turns_taken = 5
	bell.ai_turn_base = 5
	assert_true(EnemyAI._conditions_hold(engine, bell, {"turn_mod": [3, 0]}))
	bell.ai_turn_base = 0
	assert_false(EnemyAI._conditions_hold(engine, bell, {"turn_mod": [3, 0]}))
	assert_false(EnemyAI._conditions_hold(engine, bell, {"field_active": "flood"}))
	engine.fields.append(&"flood")
	assert_true(EnemyAI._conditions_hold(engine, bell, {"field_active": "flood"}))


func test_largest_ally_picks_the_biggest_living_ally() -> void:
	_start([&"fast", &"slow"])
	var polyp := BossMechanics.spawn(engine, &"polyp")
	assert_eq(EnemyAI.select_targets(engine, polyp, &"largest_ally"), [_bell()] as Array[BattleCombatant])
	_bell().fall()
	assert_eq(EnemyAI.select_targets(engine, polyp, &"largest_ally"), [polyp] as Array[BattleCombatant])


func test_a_charged_skill_finds_targets_by_its_row() -> void:
	_start([&"fast", &"slow"])
	var bell := _bell()
	bell.charge_skill = &"slam"
	bell.charge_row = engine.db.skill(&"slam")
	bell.charge_left = 2
	var marked := 0
	for e in engine.preview():
		marked += 1 if e.intent == &"slam" else 0
	assert_eq(marked, 1, "a single-target charge shows too (and pushes nobody)")
	assert_eq(BossMechanics.charged_choice(engine, bell), {}, "counting down: the AI chooses")
	var single := BossMechanics.charged_choice(engine, bell)
	assert_eq(single["skill"], &"slam")
	assert_eq((single["targets"] as Array).size(), 1)
	assert_false(bell.is_charging())
	var slow := engine.find(&"slow")
	bell.add_status(&"provoke", 3)
	bell.provoker_id = slow.id
	_charge(bell, &"slam", {"target": "single_foe"})
	assert_eq(BossMechanics.charged_choice(engine, bell)["targets"], [slow])
	_charge(bell, &"gather", {"target": "self"})
	assert_eq(BossMechanics.charged_choice(engine, bell)["targets"], [bell])
	_charge(bell, &"mend", {"target": "all_allies"})
	assert_eq(BossMechanics.charged_choice(engine, bell)["targets"], [bell])
	for c in engine.party_active:
		c.hp = 0
	bell.statuses.clear()
	_charge(bell, &"slam", {"target": "single_foe"})
	assert_eq(BossMechanics.charged_choice(engine, bell), {}, "nobody to hit")


func test_an_unknown_spawn_is_refused() -> void:
	_start([&"fast", &"slow"])
	assert_eq(BossMechanics.spawn(engine, &"nobody"), null)
	assert_eq(engine.enemies.size(), 1)


func test_same_seed_same_boss_fight() -> void:
	var a := _scripted_log(9)
	var b := _scripted_log(9)
	assert_eq(a, b)
	assert_true(a.size() > 10)


# --- helpers -------------------------------------------------------------------------------


func _scripted_log(rng_seed: int) -> Array[String]:
	engine = BattleEngine.new()
	engine.story_flags = [FLAG]
	_start([&"fast", &"slow"], rng_seed)
	var log: Array[String] = []
	engine.action_resolved.connect(
		func(r: ActionResult) -> void: log.append("%s %s %d" % [r.actor_id, r.skill_id, engine.now])
	)
	var n := 0
	while engine.outcome == &"" and n < 200:
		n += 1
		if engine.is_party_turn():
			var foes := engine.living_foes_of(engine.current)
			if not engine.fields.is_empty() and engine.current.skills.has(&"call"):
				engine.perform(&"call", foes)
			else:
				engine.perform(&"quick", [foes[0]] as Array[BattleCombatant])
		else:
			engine.run_enemy_turn()
	return log


func _start(active: Array[StringName], rng_seed: int = 3) -> void:
	engine.setup(_db(), active, [], &"boss", rng_seed)
	engine.phase_changed.connect(
		func(e: BattleCombatant, p: StringName) -> void: events.append("phase:%s:%s" % [e.id, p])
	)
	engine.combatants_joined.connect(
		func(added: Array[BattleCombatant]) -> void: events.append("joined:" + _ids(added))
	)
	engine.charge_started.connect(
		func(c: BattleCombatant, s: StringName, t: int) -> void: events.append("charge:%s:%s:%d" % [c.id, s, t])
	)
	engine.charge_broken.connect(
		func(c: BattleCombatant, s: StringName) -> void: events.append("broken:%s:%s" % [c.id, s])
	)
	engine.field_cleared.connect(
		func(f: StringName, fallen: Array[BattleCombatant]) -> void: events.append("cleared:%s:%s" % [f, _ids(fallen)])
	)
	engine.begin()


## Plays turns (party: attack the bell) until `done` holds. Fails the test if it never does.
func _until(done: Callable) -> void:
	var guard := 0
	while not done.call() and engine.outcome == &"" and guard < 100:
		guard += 1
		_play_one(&"attack")
	assert_true(done.call(), "condition never reached")


func _play_one(party_skill: StringName) -> void:
	if engine.is_party_turn():
		engine.perform(party_skill, _one(_bell()))
	else:
		engine.run_enemy_turn()


func _enter_flood() -> void:
	_bell().hp = _bell().max_hp / 2
	BossMechanics.check_phases(engine)
	assert_eq(_bell().phase_index, 0)


func _bell() -> BattleCombatant:
	return engine.enemies[0]


static func _charge(c: BattleCombatant, skill_id: StringName, row: Dictionary) -> void:
	c.charge_skill = skill_id
	c.charge_row = row
	c.charge_left = 1


static func _one(c: BattleCombatant) -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = [c]
	return out


static func _ids(list: Array[BattleCombatant]) -> String:
	var parts: PackedStringArray = []
	for c in list:
		parts.append(String(c.id))
	return ",".join(parts)


static func _intents(entries: Array[TurnEntry]) -> Array[StringName]:
	var out: Array[StringName] = []
	for e in entries:
		out.append(e.intent)
	return out


static func _hero(agility: int) -> Dictionary:
	var stats := {
		"level": 5,
		"hp": 999,
		"mp": 50,
		"strength": 10,
		"magic": 10,
		"defense": 0,
		"magic_defense": 0,
		"agility": agility,
		"accuracy": 50,
		"evasion": 0,
		"luck": 0,
	}
	return {"stats": stats, "skills": ["attack", "quick", "heavy", "call"]}


static func _db() -> BattleDB:
	var hit := {"kind": "physical", "power": 2, "accuracy": 100, "element": "none", "target": "single_foe"}
	var skills: Array = [
		hit.merged({"id": "attack", "rank": 3}, true),
		hit.merged({"id": "quick", "rank": 2}, true),
		hit.merged({"id": "heavy", "rank": 5}, true),
		hit.merged({"id": "slam", "rank": 3, "power": 1}, true),
		{"id": "gather", "kind": "support", "rank": 3, "target": "self", "charge": {"skill": "toll", "turns": 2}},
		hit.merged({"id": "toll", "rank": 3, "power": 1, "target": "all_foes", "delay_ranks": 2}, true),
		{"id": "rouse", "kind": "support", "rank": 3, "target": "self", "summon": "polyp"},
		{"id": "surge", "kind": "magical", "power": 1, "rank": 3, "target": "all_foes", "magic": true},
		{"id": "mend", "kind": "heal", "power": 5, "rank": 3, "target": "single_ally", "magic": true},
		{
			"id": "call",
			"kind": "magical",
			"power": 1,
			"rank": 3,
			"target": "all_foes",
			"mp_cost": 5,
			"magic": true,
			"requires_flag": "bound",
			"clears_field": "flood",
		},
	]
	var bell_stats := {
		"level": 5,
		"hp": 1000,
		"mp": 0,
		"strength": 1,
		"magic": 1,
		"defense": 0,
		"magic_defense": 0,
		"agility": 12,
		"accuracy": 100,
		"evasion": 0,
		"luck": 0,
	}
	var flood := {
		"id": "flood",
		"at_hp_pct": 50,
		"skills": ["slam", "rouse", "surge"],
		"field": "flood",
		"spawn": ["polyp", "polyp"],
		"affinities": {"fire": "weak"},
		"stats": {"defense": 7, "agility": 20},
		"delay_immune": false,
		"ai":
		[
			{"if": {"field_active": "flood", "allies_alive_below": 3}, "pick": [{"skill": "rouse", "target": "self"}]},
			{"pick": [{"skill": "slam", "target": "random_foe"}]},
		],
	}
	var bell := {
		"id": "bell",
		"stats": bell_stats,
		"delay_immune": true,
		"skills": ["slam", "gather", "toll"],
		"weak_point": {"hits": 2, "max_delay": 200},
		"phases": [flood],
		"ai":
		[
			{"if": {"turn_mod": [3, 0]}, "pick": [{"skill": "gather", "target": "self"}]},
			{"pick": [{"skill": "slam", "target": "random_foe"}]},
		],
	}
	var polyp_stats := bell_stats.merged({"hp": 50, "magic": 10, "level": 4, "agility": 10}, true)
	var polyp := {
		"id": "polyp",
		"stats": polyp_stats,
		"field": "flood",
		"skills": ["mend"],
		"ai": [{"pick": [{"skill": "mend", "target": "largest_ally"}]}],
	}
	return (
		BattleDB
		. from_tables(
			{
				"skills": skills,
				"statuses": [{"id": "haste", "default_duration": 4}],
				"characters":
				[
					_hero(22).merged({"id": "fast"}),
					_hero(10).merged({"id": "slow"}),
					_hero(11).merged({"id": "slow2"}),
				],
				"enemies": [bell, polyp],
				"encounters": [{"id": "boss", "enemies": ["bell"]}],
			}
		)
	)
