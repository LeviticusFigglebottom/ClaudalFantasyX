extends TestCase
## M3-C05-02: the two boss hooks the Cinder Matron needs (BossMechanics): a skill's "cleanses"
## (her recrust lifts Armor Break off her) and an enemy's "reactions" (a landed water or ice hit in
## her Pour phase re-crusts her at once). Runs on a small fixture DB, so tuning the real Matron
## never breaks these.

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()
	engine.setup(_db(), [&"hero"] as Array[StringName], [] as Array[StringName], &"forge", 7)
	engine.begin()


func test_a_cleansing_skill_lifts_its_statuses_off_its_target() -> void:
	var m := _matron()
	m.add_status(&"armor_break", 3)
	m.add_status(&"slow", 2)
	var r := ActionResult.new()
	r.hits.append({"target_id": m.id, "hit": true, "element": &"none"})
	BossMechanics.after_action(engine, m, engine.db.skill(&"recrust"), r)
	assert_false(m.has_status(&"armor_break"), "the break is gone")
	assert_true(m.has_status(&"slow"), "only the listed statuses")


func test_water_re_crusts_her_only_in_the_pour() -> void:
	var m := _matron()
	m.add_status(&"armor_break", 3)
	var hit := _hit(m, &"water")
	assert_true(m.has_status(&"armor_break"), "the Crust phase does not react")
	assert_false(hit.has("reacted"))
	m.hp = m.max_hp / 2
	BossMechanics.check_phases(engine)
	assert_eq(BossMechanics.phase_id(m), "pour")
	hit = _hit(m, &"ice")
	assert_true(bool(hit.get("reacted", false)), "cold quenches her")
	assert_false(m.has_status(&"armor_break"), "and closes the crust over the break")
	assert_eq(int(m.statuses.get(&"protect", 0)), 2, "with the row's duration")


func test_other_elements_and_misses_do_not_react() -> void:
	var m := _matron()
	m.hp = m.max_hp / 2
	BossMechanics.check_phases(engine)
	m.add_status(&"armor_break", 3)
	assert_false(_hit(m, &"fire").has("reacted"))
	var r := ActionResult.new()
	r.hits.append({"target_id": m.id, "hit": false, "element": &"water"})
	BossMechanics.after_action(engine, engine.party_active[0], engine.db.skill(&"attack"), r)
	assert_true(m.has_status(&"armor_break"), "a miss quenches nothing")


func test_a_real_water_strike_in_the_pour_reacts() -> void:
	var m := _matron()
	m.hp = m.max_hp / 2
	BossMechanics.check_phases(engine)
	m.add_status(&"armor_break", 3)
	while not engine.is_party_turn():
		engine.run_enemy_turn()
	var res := engine.perform(&"splash", [m] as Array[BattleCombatant])
	assert_true(res.ok)
	assert_true(bool(res.hits[0].get("reacted", false)))
	assert_false(m.has_status(&"armor_break"))


func _hit(m: BattleCombatant, element: StringName) -> Dictionary:
	var r := ActionResult.new()
	r.hits.append({"target_id": m.id, "hit": true, "element": element})
	BossMechanics.after_action(engine, engine.party_active[0], engine.db.skill(&"attack"), r)
	return r.hits[0]


func _matron() -> BattleCombatant:
	return engine.enemies[0]


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
		{"id": "splash", "kind": "magical", "power": 1, "rank": 3, "element": "water", "target": "single_foe"},
		{"id": "recrust", "kind": "support", "rank": 2, "target": "self", "cleanses": ["armor_break"]},
	]
	var matron := {
		"id": "matron",
		"stats": stats,
		"skills": ["attack"],
		"ai": [{"pick": [{"skill": "attack", "target": "random_foe"}]}],
		"reactions":
		[
			{
				"elements": ["water", "ice"],
				"from_phase": "pour",
				"cleanses": ["armor_break"],
				"statuses": [{"id": "protect", "duration": 2}],
			}
		],
		"phases": [{"id": "pour", "at_hp_pct": 50}],
	}
	return (
		BattleDB
		. from_tables(
			{
				"skills": skills,
				"statuses": [{"id": "protect", "default_duration": 4}, {"id": "armor_break", "default_duration": -1}],
				"characters": [{"id": "hero", "stats": stats, "skills": ["attack", "splash"]}],
				"enemies": [matron],
				"encounters": [{"id": "forge", "enemies": ["matron"]}],
			}
		)
	)
