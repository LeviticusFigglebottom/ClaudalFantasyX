extends TestCase
## M4-A2P-025 (BattleCycle): Kesh's six voices in order. Only this turn's voice may be used (the menu greys and says
## why), the cycle moves on at the end of each own turn, and the timeline shows each coming turn's voice.

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()
	var active: Array[StringName] = [&"singer"]
	engine.setup(_db(), active, [] as Array[StringName], &"one", 1)
	engine.begin()


func test_only_this_turns_voice_may_be_used() -> void:
	var singer := engine.find(&"singer")
	_until(singer)
	assert_eq(BattleCycle.skill_at(singer, 0), &"v_water")
	var r := engine.perform(&"v_fire", [engine.enemies[0]] as Array[BattleCombatant])
	assert_eq(r.fail_reason, BattleCycle.FAIL_OUT_OF_CYCLE, "not fire's turn")
	assert_true(engine.perform(&"v_water", [engine.enemies[0]] as Array[BattleCombatant]).ok)
	assert_eq(BattleCycle.skill_at(singer, 0), &"v_fire", "the next element after her turn")


func test_skills_outside_the_cycle_stay_free_and_the_cycle_still_turns() -> void:
	var singer := engine.find(&"singer")
	_until(singer)
	assert_true(engine.perform(&"attack", [engine.enemies[0]] as Array[BattleCombatant]).ok)
	assert_eq(BattleCycle.skill_at(singer, 0), &"v_fire")


func test_the_cycle_wraps() -> void:
	var singer := engine.find(&"singer")
	assert_eq(BattleCycle.skill_at(singer, 2), &"v_ice")
	assert_eq(BattleCycle.skill_at(singer, 3), &"v_water", "back to the first")
	singer.cycle_index = 2
	BattleCycle.advance(singer)
	assert_eq(singer.cycle_index, 0)


func test_the_timeline_shows_each_coming_voice() -> void:
	var singer := engine.find(&"singer")
	var seen: Array[StringName] = []
	for entry in engine.preview(&"", null, 8):
		if entry.combatant_id == singer.id:
			seen.append(entry.intent)
	assert_true(seen.size() >= 3, "she has turns in the window")
	for k in seen.size():
		assert_eq(seen[k], BattleCycle.skill_at(singer, k), "turn %d shows its voice" % k)


func test_the_menu_greys_the_other_voices_and_says_why() -> void:
	var singer := engine.find(&"singer")
	_until(singer)
	var menus := BattleMenus.new()
	assert_eq(menus.skill_help(engine, &"v_fire", -1), menus.fail_text(BattleCycle.FAIL_OUT_OF_CYCLE, singer))
	assert_ne(menus.skill_help(engine, &"v_water", -1), menus.fail_text(BattleCycle.FAIL_OUT_OF_CYCLE, singer))


func _until(c: BattleCombatant) -> void:
	var guard := 0
	while engine.current != c and engine.outcome == &"" and guard < 50:
		guard += 1
		engine.run_enemy_turn()


static func _db() -> BattleDB:
	var hero := {
		"level": 5,
		"hp": 4000,
		"mp": 20,
		"strength": 1,
		"magic": 1,
		"defense": 5,
		"magic_defense": 5,
		"agility": 30,
		"accuracy": 0,
		"evasion": 0,
		"luck": 0,
	}
	var foe := hero.duplicate()
	foe["agility"] = 20
	foe["hp"] = 90000
	foe["mp"] = 0
	var basic := [{"pick": [{"skill": "attack", "target": "random_foe"}]}]
	var voices := ["v_water", "v_fire", "v_ice"]
	var skills := [{"id": "attack", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100}]
	for v: String in voices:
		skills.append({"id": v, "kind": "magical", "power": 1, "rank": 3, "magic": true})
	return (
		BattleDB
		. from_tables(
			{
				"skills": skills,
				"statuses": [],
				"characters": [{"id": "singer", "stats": hero, "skills": ["attack"] + voices, "cycle": voices}],
				"enemies": [{"id": "foe", "stats": foe, "skills": ["attack"], "ai": basic}],
				"encounters": [{"id": "one", "enemies": ["foe"]}],
			}
		)
	)
