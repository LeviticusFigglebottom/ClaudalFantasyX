extends TestCase
## M3-C06-02: the two encounter rules the Stillguard Inquisitor needs (act1_ch06.md §5), on a small
## fixture DB so tuning the real fight never breaks these:
##   encounters.json "forbidden_skills": a hero's offensive skills are refused on a tagged foe
##     (Toma will not strike the Stillguard), while his guard and Provoke stay usable;
##   enemies.json "yield_at_hp_pct": a foe that yields (or runs) on its feet instead of falling,
##     and the fight is won once every foe is down or gone. Nobody dies.

const SEED := 11

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()
	engine.setup(_db(), [&"guard", &"hero"] as Array[StringName], [] as Array[StringName], &"raid", SEED)
	engine.begin()


func test_the_rule_is_set_only_on_the_hero_it_names() -> void:
	assert_eq(_c(&"guard").forbidden_tag, &"order")
	assert_eq(_c(&"guard").forbidden_key, "TEST_WILL_NOT_STRIKE")
	assert_eq(_c(&"hero").forbidden_tag, &"")
	assert_eq(_officer().tags, [&"order"] as Array[StringName])
	assert_eq(_beast().tags, [] as Array[StringName])


func test_offensive_skills_are_refused_on_a_tagged_foe_only() -> void:
	var g := _c(&"guard")
	var db := engine.db
	assert_true(BossMechanics.forbids(g, db.skill(&"attack"), _officer()))
	assert_true(BossMechanics.forbids(g, db.skill(&"bolt"), _officer()), "magic wounds too")
	assert_false(BossMechanics.forbids(g, db.skill(&"attack"), _beast()), "an untagged foe is fair")
	assert_false(BossMechanics.forbids(g, db.skill(&"taunt"), _officer()), "Provoke is not a blow")
	assert_false(BossMechanics.forbids(_c(&"hero"), db.skill(&"attack"), _officer()), "only the named hero")
	_to_turn_of(&"guard")
	var res := engine.perform(&"attack", [_officer()] as Array[BattleCombatant])
	assert_false(res.ok)
	assert_eq(res.fail_reason, BossMechanics.FAIL_FORBIDDEN)
	assert_eq(engine.current.id, &"guard", "a refused blow costs no turn")
	assert_eq(_officer().hp, _officer().max_hp)
	assert_true(engine.perform(&"taunt", [_officer()] as Array[BattleCombatant]).ok, "he may still draw them")


func test_a_group_skill_touching_a_tagged_foe_is_refused() -> void:
	_to_turn_of(&"guard")
	var sweep := engine.db.skill(&"sweep")
	assert_true(BossMechanics.forbidden_now(engine, engine.current, sweep))
	var res := engine.perform(&"sweep", engine.living_foes_of(engine.current))
	assert_eq(res.fail_reason, BossMechanics.FAIL_FORBIDDEN)


func test_forbidden_now_greys_a_single_target_skill_only_while_no_fair_foe_stands() -> void:
	var g := _c(&"guard")
	var attack := engine.db.skill(&"attack")
	assert_false(BossMechanics.forbidden_now(engine, g, attack), "the beast is still a fair target")
	_beast().apply_damage(_beast().max_hp)
	assert_true(BossMechanics.forbidden_now(engine, g, attack), "only the officer is left")
	assert_false(BossMechanics.forbidden_now(engine, g, engine.db.skill(&"taunt")))
	assert_false(BossMechanics.forbidden_now(engine, _c(&"hero"), attack))


func test_the_menus_grey_the_blows_and_say_why() -> void:
	_beast().apply_damage(_beast().max_hp)
	_to_turn_of(&"guard")
	var menus := BattleMenus.new()
	var attack_row: Dictionary = menus.root_rows(engine)[0]
	assert_false(bool(attack_row.get("enabled", true)), "Attack is greyed")
	var enabled := {}
	for row in menus.skill_rows(engine):
		enabled[row.get("id")] = bool(row.get("enabled", true))
	assert_false(enabled[&"bolt"])
	assert_true(enabled[&"taunt"], "his guard is all there")
	assert_eq(menus.skill_help(engine, &"attack", -1), "TEST_WILL_NOT_STRIKE")
	assert_eq(menus.fail_text(BossMechanics.FAIL_FORBIDDEN, engine.current), "TEST_WILL_NOT_STRIKE")


func test_a_yielding_foe_leaves_on_its_feet() -> void:
	var o := _officer()
	var lost := o.apply_damage(o.max_hp * 2)
	assert_true(o.yielded)
	assert_false(o.is_alive(), "down for the timeline and the outcome")
	assert_true(o.hp >= 1, "but never dead")
	assert_eq(lost, o.hp - o.max_hp, "the delta is what it really lost")
	assert_false(o.add_status(&"protect", 2), "nothing lands on a foe who has left")


func test_it_yields_at_its_threshold_not_before() -> void:
	var o := _officer()
	o.apply_damage(o.max_hp - o.max_hp * 25 / Formulas.PCT - 1)
	assert_false(o.yielded, "above a quarter it fights on")
	o.apply_damage(1)
	assert_true(o.yielded, "at a quarter it yields")
	var hp := o.hp
	o.apply_damage(o.max_hp)
	assert_eq(o.hp, hp, "a yielded foe takes no more")


func test_doom_or_a_field_fall_makes_it_yield_too() -> void:
	var o := _officer()
	o.fall()
	assert_true(o.yielded)
	assert_true(o.hp >= 1)
	var b := _beast()
	b.fall()
	assert_false(b.yielded, "a foe without the rule falls as ever")
	assert_eq(b.hp, 0)


func test_the_fight_is_won_when_every_foe_has_yielded_or_fallen() -> void:
	_officer().apply_damage(_officer().max_hp)
	_beast().apply_damage(_beast().max_hp)
	_to_turn_of(&"hero")
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)
	assert_true(_officer().hp > 0, "the Inquisitor walks away")


func test_a_real_blow_makes_him_yield_and_wins() -> void:
	_beast().apply_damage(_beast().max_hp)
	_officer().hp = 1
	_to_turn_of(&"hero")
	assert_true(engine.perform(&"attack", [_officer()] as Array[BattleCombatant]).ok)
	assert_true(_officer().yielded)
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)


func test_the_sim_guard_takes_a_lawful_action_instead_of_stalling() -> void:
	_beast().apply_damage(_beast().max_hp)
	_to_turn_of(&"guard")
	var guard := engine.current
	var p := SimPolicyNaive.new()
	p.take_turn(engine)
	assert_ne(engine.current, guard, "his turn ended")
	assert_eq(_officer().hp, _officer().max_hp, "and he never struck the officer")
	assert_eq(engine.outcome, &"", "no escape: the fight goes on")
	assert_false(SimPolicy.usable_skills(engine, guard).has(&"attack"))


func test_victory_title_follows_the_encounter() -> void:
	assert_eq(BattleMenus.victory_title_key(engine), "TEST_YIELDS")
	var other := BattleEngine.new()
	other.setup(_db(), [&"hero"] as Array[StringName], [] as Array[StringName], &"plain", SEED)
	assert_eq(BattleMenus.victory_title_key(other), "HUD_VICTORY")


func _to_turn_of(cid: StringName) -> void:
	for _i in 200:
		if engine.outcome != &"" or (engine.is_party_turn() and engine.current.id == cid):
			return
		if engine.is_party_turn():
			engine.perform(&"taunt", [engine.living_foes_of(engine.current)[0]] as Array[BattleCombatant])
		else:
			engine.run_enemy_turn()


func _c(cid: StringName) -> BattleCombatant:
	return engine.find(cid)


func _officer() -> BattleCombatant:
	return engine.enemies[0]


func _beast() -> BattleCombatant:
	return engine.enemies[1]


static func _db() -> BattleDB:
	var stats := {
		"level": 5,
		"hp": 1000,
		"mp": 50,
		"strength": 1,
		"magic": 1,
		"defense": 0,
		"magic_defense": 0,
		"agility": 10,
		"accuracy": 100,
		"evasion": 0,
		"luck": 0,
	}
	var skills: Array = [
		{"id": "attack", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100, "target": "single_foe"},
		{"id": "bolt", "kind": "magical", "power": 1, "rank": 3, "target": "single_foe"},
		{"id": "sweep", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100, "target": "all_foes"},
		{"id": "taunt", "kind": "support", "rank": 2, "target": "single_foe", "statuses": [{"id": "provoke"}]},
		{"id": "nip", "kind": "physical", "power": 0, "rank": 3, "accuracy": 0, "target": "single_foe"},
	]
	var foe := {
		"stats": stats,
		"skills": ["nip"],
		"ai": [{"pick": [{"skill": "nip", "target": "random_foe"}]}],
	}
	var officer := foe.duplicate(true)
	officer["id"] = "officer"
	officer["tags"] = ["order"]
	officer["yield_at_hp_pct"] = 25
	var beast := foe.duplicate(true)
	beast["id"] = "beast"
	return (
		BattleDB
		. from_tables(
			{
				"skills": skills,
				"statuses": [{"id": "protect", "default_duration": 4}, {"id": "provoke", "default_duration": 3}],
				"characters":
				[
					{"id": "guard", "stats": stats, "skills": ["attack", "bolt", "sweep", "taunt"]},
					{"id": "hero", "stats": stats, "skills": ["attack", "taunt"]},
				],
				"enemies": [officer, beast],
				"encounters":
				[
					{
						"id": "raid",
						"scripted": true,
						"victory_key": "TEST_YIELDS",
						"forbidden_skills": {"guard": {"against_tag": "order", "fail_key": "TEST_WILL_NOT_STRIKE"}},
						"enemies": ["officer", "beast"],
					},
					{"id": "plain", "enemies": ["beast"]},
				],
			}
		)
	)
