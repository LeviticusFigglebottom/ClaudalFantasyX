extends TestCase
## Defensive and edge branches of BattleEngine, EnemyAI, CtbTimeline and BattleCombatant:
## calls out of turn, bad data that must never stall a battle, and rare tie-breaks.

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()


func test_calls_after_the_battle_are_refused() -> void:
	_start(&"one")
	assert_eq(engine.xp_awards(), {}, "no XP before a victory")
	engine.enemies[0].hp = 1
	engine.perform(&"attack", _foe())
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)
	var dead: Array[BattleCombatant] = [engine.enemies[0]]
	assert_eq(engine.perform(&"attack", dead).fail_reason, &"battle_over")
	assert_eq(engine.run_enemy_turn(), null)


func test_run_enemy_turn_on_a_player_turn_is_null() -> void:
	_start(&"one")
	assert_true(engine.is_party_turn())
	assert_eq(engine.run_enemy_turn(), null)


func test_unknown_skill_is_refused() -> void:
	_start(&"one")
	assert_eq(engine.perform(&"nonsense", _foe()).fail_reason, &"unknown_skill")


func test_enemy_with_no_valid_action_idles() -> void:
	_start(&"stuck")
	var foe := engine.enemies[0]
	_until_enemy_turn()
	var r := engine.run_enemy_turn()
	assert_eq(r.fail_reason, &"no_valid_action")
	assert_ne(engine.current, foe, "its turn was spent")


func test_enemy_that_cannot_pay_loses_its_turn() -> void:
	_start(&"broke")
	var foe := engine.enemies[0]
	_until_enemy_turn()
	var r := engine.run_enemy_turn()
	assert_eq(r.fail_reason, &"no_mp")
	assert_ne(engine.current, foe)


func test_auto_turn_without_a_basic_attack_idles() -> void:
	_start(&"one")
	var actor := engine.current
	actor.skills = [&"zap"] as Array[StringName]
	actor.add_status(&"berserk", -1)
	assert_eq(engine.basic_attack(actor), &"")
	var r := engine.run_enemy_turn()
	assert_eq(r.fail_reason, &"no_valid_action")
	assert_eq(r.auto_reason, &"berserk")
	assert_ne(engine.current, actor)


func test_target_validation_edges() -> void:
	_start(&"two")
	var actor := engine.current
	var ally := engine.party_active[1] if engine.party_active[0] == actor else engine.party_active[0]
	var mine: Array[BattleCombatant] = [ally]
	assert_eq(engine.perform(&"attack", mine).fail_reason, &"no_valid_target", "single_foe rejects an ally")
	assert_eq(engine.perform(&"brace", mine).fail_reason, &"no_valid_target", "self rejects anyone else")
	var both: Array[BattleCombatant] = [engine.enemies[0], engine.enemies[1]]
	var r := engine.perform(&"attack", both)
	assert_eq(r.hits.size(), 1, "single-target skills keep the first target only")


func test_unknown_skill_kind_resolves_as_nothing() -> void:
	_start(&"one")
	var hp := engine.enemies[0].hp
	var r := engine.perform(&"oddity", _foe())
	assert_true(r.ok)
	assert_eq(engine.enemies[0].hp, hp)


func test_begin_with_nobody_standing_ends_at_once() -> void:
	var active: Array[StringName] = [&"hero"]
	engine.setup(_db(), active, [] as Array[StringName], &"one", 1)
	for c in engine.party_active + engine.enemies:
		c.hp = 0
	engine.begin()
	assert_ne(engine.outcome, &"")
	assert_eq(engine.current, null)


func test_provoke_without_a_provoker_forces_nothing() -> void:
	_start(&"one")
	engine.current.add_status(&"provoke", 3)
	assert_eq(engine.forced_target(engine.current, &"attack"), null)


func test_mean_agility_of_nobody_is_zero() -> void:
	assert_eq(BattleEngine._mean_agility([] as Array[BattleCombatant]), 0.0)


func test_enemy_ai_group_selectors_and_bad_rules() -> void:
	_start(&"two")
	var foe := engine.enemies[0]
	assert_eq(EnemyAI.select_targets(engine, foe, &"all_foes").size(), engine.party_active.size())
	assert_eq(EnemyAI.select_targets(engine, foe, &"all_allies").size(), 2)
	assert_eq(EnemyAI.select_targets(engine, foe, &"sideways").size(), 0, "unknown selector: no targets")
	foe.ai_rules = [
		{"pick": [{"skill": "attack", "weight": 0}]},
		{"pick": [{"skill": "attack", "target": "sideways"}]},
		{"if": {"moon_phase": 3}, "pick": [{"skill": "attack"}]},
	]
	assert_eq(EnemyAI.choose(engine, foe), {}, "zero weights, empty targets and unknown conditions all fall through")


func test_timeline_eligible_and_sim_edges() -> void:
	var a := _mk(&"a", 10)
	var b := _mk(&"b", 10)
	var tl := CtbTimeline.new()
	tl.set_roster([a, b] as Array[BattleCombatant])
	b.hp = 0
	assert_eq(tl.eligible(), [a] as Array[BattleCombatant])
	b.hp = 10
	var ids: Array[StringName] = []
	for e in tl.predict(2):
		ids.append(e.combatant_id)
	assert_eq(ids, [&"a", &"b"] as Array[StringName], "same time and agility: roster order")
	a.add_status(&"haste", -1)
	var entries := tl.predict(3, null, 3, null, 0, {b: {&"poison": -1}})
	assert_eq(entries.size(), 3, "permanent timed statuses and non-time statuses are fine")
	assert_eq(entries[2].combatant_id, &"a", "permanent Haste: a's next turn (150) beats b's (300)")


func test_speed_mult_with_slow_and_both() -> void:
	var c := _mk(&"c", 10)
	c.statuses[&"slow"] = 2
	assert_eq(c.speed_mult(), Formulas.SLOW_SPEED_MULT)
	c.statuses[&"haste"] = 2
	assert_eq(c.speed_mult(), Formulas.SLOW_SPEED_MULT * Formulas.HASTE_SPEED_MULT, "both at once cancel")


# --- helpers -----------------------------------------------------------------------------


func _start(encounter: StringName) -> void:
	var active: Array[StringName] = [&"hero", &"helper"]
	engine.setup(_db(), active, [] as Array[StringName], encounter, 1)
	engine.begin()
	var guard := 0
	while not engine.is_party_turn() and engine.outcome == &"" and guard < 50:
		guard += 1
		engine.run_enemy_turn()


func _until_enemy_turn() -> void:
	var guard := 0
	while engine.is_party_turn() and guard < 20:
		guard += 1
		engine.perform(&"jab", _foe())


func _foe() -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = [engine.living_foes_of(engine.current)[0]]
	return out


static func _mk(cid: StringName, agility: int) -> BattleCombatant:
	var c := BattleCombatant.new()
	c.id = cid
	c.agility = agility
	c.max_hp = 10
	c.hp = 10
	return c


static func _db() -> BattleDB:
	var hero := {
		"level": 5,
		"hp": 400,
		"mp": 20,
		"strength": 10,
		"magic": 10,
		"defense": 5,
		"magic_defense": 5,
		"agility": 30,
		"accuracy": 0,
		"evasion": 0,
		"luck": 0,
	}
	var helper := hero.duplicate()
	helper["agility"] = 25
	var foe := hero.duplicate()
	foe["agility"] = 5
	foe["hp"] = 9000
	foe["mp"] = 0
	var basic := [{"pick": [{"skill": "attack", "target": "random_foe"}]}]
	var never := [{"if": {"self_hp_below_pct": 1}, "pick": [{"skill": "attack"}]}]
	var costly := [{"pick": [{"skill": "zap", "target": "random_foe"}]}]
	var skills := ["attack", "jab", "zap", "brace", "oddity"]
	return (
		BattleDB
		. from_tables(
			{
				"skills":
				[
					{"id": "attack", "kind": "physical", "power": 4, "rank": 3, "accuracy": 100},
					{"id": "jab", "kind": "physical", "power": 1, "rank": 1, "accuracy": 100},
					{"id": "zap", "kind": "magical", "power": 4, "rank": 3, "mp_cost": 5, "magic": true},
					{"id": "brace", "kind": "support", "rank": 2, "target": "self"},
					{"id": "oddity", "kind": "mystery", "rank": 3},
				],
				"statuses": [],
				"characters":
				[{"id": "hero", "stats": hero, "skills": skills}, {"id": "helper", "stats": helper, "skills": skills}],
				"enemies":
				[
					{"id": "plain", "stats": foe, "skills": ["attack"], "ai": basic},
					{"id": "stuck", "stats": foe, "skills": ["attack"], "ai": never},
					{"id": "broke", "stats": foe, "skills": ["zap"], "ai": costly},
				],
				"encounters":
				[
					{"id": "one", "enemies": ["plain"]},
					{"id": "two", "enemies": ["plain", "plain"]},
					{"id": "stuck", "enemies": ["stuck"]},
					{"id": "broke", "enemies": ["broke"]},
				],
			}
		)
	)
