extends TestCase
## Engine rules against a small fixture DB, so tests do not break when real data is tuned.

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()


func test_party_acts_first_when_faster() -> void:
	_start(&"dummies")
	assert_true(engine.is_party_turn())


func test_swap_costs_no_time_and_inherits_slot() -> void:
	_start(&"dummies")
	var leaving := engine.current
	var slot := leaving.next_time
	var now := engine.now
	assert_true(engine.swap(leaving.id, &"bench"))
	assert_eq(engine.current.id, &"bench")
	assert_eq(engine.current.next_time, slot)
	assert_eq(engine.now, now)
	assert_true(engine.party_reserve.has(leaving))
	assert_true(engine.current.participated)
	assert_eq(engine.preview()[0].combatant_id, &"bench")


func test_swap_rejects_unknown_members() -> void:
	_start(&"dummies")
	assert_false(engine.swap(&"nobody", &"bench"))
	assert_false(engine.swap(engine.current.id, &"nobody"))


func test_silence_blocks_magic_without_ending_turn() -> void:
	_start(&"dummies")
	var actor := engine.current
	actor.add_status(&"silence", 2)
	var r := engine.perform(&"zap", _first_foe())
	assert_false(r.ok)
	assert_eq(r.fail_reason, &"silenced")
	assert_eq(engine.current, actor)


func test_not_enough_mp() -> void:
	_start(&"dummies")
	engine.current.mp = 0
	var r := engine.perform(&"zap", _first_foe())
	assert_eq(r.fail_reason, &"no_mp")


func test_rank_sets_next_delay() -> void:
	_start(&"sturdy")
	var actor := engine.current
	var now := engine.now
	engine.perform(&"jab", _first_foe())
	assert_eq(actor.next_time, now + Formulas.action_delay(actor.agility, 1))


func test_delay_skill_pushes_target_back() -> void:
	_start(&"sturdy")
	var target := _first_foe()[0]
	var before := target.next_time
	var r := engine.perform(&"delay_hit", _first_foe())
	assert_true(r.hits[0]["hit"])
	assert_eq(target.next_time, before + Formulas.base_delay(target.agility) * 2)


func test_haste_applies_before_own_delay() -> void:
	_start(&"sturdy")
	var actor := engine.current
	var now := engine.now
	var me: Array[BattleCombatant] = [actor]
	engine.perform(&"quicken", me)
	assert_true(actor.has_status(&"haste"))
	assert_eq(actor.next_time, now + Formulas.action_delay(actor.agility, 3, Formulas.HASTE_SPEED_MULT))


func test_poison_ticks_at_end_of_own_turn() -> void:
	_start(&"sturdy")
	var actor := engine.current
	actor.add_status(&"poison", -1)
	var hp := actor.hp
	engine.perform(&"jab", _first_foe())
	assert_eq(actor.hp, hp - Formulas.poison_damage(actor.max_hp))


func test_victory_awards_xp_to_participants_only() -> void:
	_start(&"dummies")
	_auto_play(200)
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)
	var xp := engine.xp_awards()
	assert_eq(xp.get(&"hero", 0), 20)
	assert_eq(xp.get(&"helper", 0), 20)
	assert_false(xp.has(&"bench"), "reserve that never entered earns nothing")


func test_escape_forbidden_in_scripted_fight() -> void:
	_start(&"scripted")
	assert_false(engine.escape())
	assert_eq(engine.outcome, &"")


func test_same_seed_same_battle() -> void:
	_start(&"dummies", 99)
	var a := _auto_play(200)
	engine = BattleEngine.new()
	_start(&"dummies", 99)
	var b := _auto_play(200)
	assert_eq(a, b)


func test_enemy_ai_turn_mod_rule() -> void:
	_start(&"sturdy")
	var foe := _first_foe()[0]
	foe.turns_taken = 1
	var choice := EnemyAI.choose(engine, foe)
	assert_eq(choice["skill"], &"jab", "turn_mod [2, 1] rule fires on odd turns")
	foe.turns_taken = 2
	choice = EnemyAI.choose(engine, foe)
	assert_eq(choice["skill"], &"attack")


# --- helpers -----------------------------------------------------------------------------


func _start(encounter: StringName, rng_seed: int = 1) -> void:
	var active: Array[StringName] = [&"hero", &"helper"]
	var reserve: Array[StringName] = [&"bench"]
	engine.setup(_fixture_db(), active, reserve, encounter, rng_seed)
	engine.begin()
	var guard := 0
	while not engine.is_party_turn() and engine.outcome == &"" and guard < 50:
		engine.run_enemy_turn()
		guard += 1


func _first_foe() -> Array[BattleCombatant]:
	var foes := engine.living_foes_of(engine.current)
	var out: Array[BattleCombatant] = [foes[0]]
	return out


## Party always attacks the first living foe. Returns a compact action log.
func _auto_play(max_actions: int) -> Array[String]:
	var entries: Array[String] = []
	var n := 0
	while engine.outcome == &"" and n < max_actions:
		n += 1
		if engine.is_party_turn():
			var actor := engine.current.id
			var r := engine.perform(&"attack", _first_foe())
			entries.append("%s:%s" % [actor, str(r.hits.map(func(h: Dictionary) -> int: return h["amount"]))])
		else:
			var r2 := engine.run_enemy_turn()
			entries.append("%s:%s" % [r2.actor_id, r2.skill_id])
	entries.append(String(engine.outcome))
	return entries


static func _fixture_db() -> BattleDB:
	var hero_stats := {
		"level": 5,
		"hp": 300,
		"mp": 10,
		"strength": 30,
		"magic": 10,
		"defense": 10,
		"magic_defense": 10,
		"agility": 20,
		"accuracy": 50,
		"evasion": 0,
		"luck": 0
	}
	var helper_stats := hero_stats.duplicate()
	helper_stats["agility"] = 15
	var bench_stats := hero_stats.duplicate()
	bench_stats["agility"] = 30
	var skills := [&"attack", &"zap", &"jab", &"delay_hit", &"quicken"]
	var foe_stats := {
		"level": 1,
		"hp": 40,
		"mp": 0,
		"strength": 5,
		"magic": 1,
		"defense": 0,
		"magic_defense": 0,
		"agility": 1,
		"accuracy": 0,
		"evasion": 0,
		"luck": 0
	}
	var sturdy_stats := foe_stats.duplicate()
	sturdy_stats["hp"] = 9000
	var basic_ai := [{"pick": [{"skill": "attack", "target": "random_foe"}]}]
	var sturdy_ai := [
		{"if": {"turn_mod": [2, 1]}, "pick": [{"skill": "jab", "target": "random_foe"}]},
		{"pick": [{"skill": "attack", "target": "random_foe"}]},
	]
	return (
		BattleDB
		. from_tables(
			{
				"skills":
				[
					{"id": "attack", "kind": "physical", "power": 8, "rank": 3, "accuracy": 100},
					{"id": "jab", "kind": "physical", "power": 2, "rank": 1, "accuracy": 100},
					{"id": "delay_hit", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100, "delay_ranks": 2},
					{"id": "zap", "kind": "magical", "power": 8, "rank": 3, "mp_cost": 5, "magic": true},
					{
						"id": "quicken",
						"kind": "support",
						"rank": 3,
						"magic": true,
						"statuses": [{"id": "haste", "chance": 100, "duration": 4}]
					},
				],
				"statuses": [{"id": "haste", "default_duration": 4}],
				"characters":
				[
					{"id": "hero", "stats": hero_stats, "skills": skills},
					{"id": "helper", "stats": helper_stats, "skills": skills},
					{"id": "bench", "stats": bench_stats, "skills": skills},
				],
				"enemies":
				[
					{"id": "dummy", "stats": foe_stats, "skills": ["attack"], "ai": basic_ai, "xp": 10},
					{"id": "sturdy", "stats": sturdy_stats, "skills": ["attack", "jab"], "ai": sturdy_ai, "xp": 1},
				],
				"encounters":
				[
					{"id": "dummies", "enemies": ["dummy", "dummy"]},
					{"id": "sturdy", "enemies": ["sturdy"]},
					{"id": "scripted", "enemies": ["sturdy"], "scripted": true},
				],
			}
		)
	)
