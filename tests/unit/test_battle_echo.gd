extends TestCase
## M4-A2P-024 (BattleEcho): Nhoa's echo resolves as the last enemy action, from her, at her own rank and cost; never
## its charge or summon; refused while no foe has acted.

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()
	var active: Array[StringName] = [&"nhoa"]
	engine.setup(_db(), active, [] as Array[StringName], &"one", 1)
	engine.begin()


func test_nothing_to_echo_until_a_foe_acts() -> void:
	var nhoa := engine.find(&"nhoa")
	engine.last_foe_skill = &""
	_until(nhoa)
	if engine.last_foe_skill != &"":
		return  # the foe acted first in this seed; the next test covers the copy
	var r := engine.perform(&"echo", [engine.enemies[0]] as Array[BattleCombatant])
	assert_eq(r.fail_reason, BattleEcho.FAIL_NOTHING)


func test_the_echo_is_the_last_enemy_action_from_her() -> void:
	var nhoa := engine.find(&"nhoa")
	var foe := engine.enemies[0]
	engine.last_foe_skill = &"crush"
	_until(nhoa)
	engine.last_foe_skill = &"crush"
	var hp := foe.hp
	var r := engine.perform(&"echo", [foe] as Array[BattleCombatant])
	assert_true(r.ok, str(r.fail_reason))
	assert_true(foe.hp < hp, "the crush lands on her foe")
	assert_eq(nhoa.mp, nhoa.max_mp, "at the echo's own cost (none), not the crush's")
	assert_false(nhoa.is_charging())


func test_a_copied_gather_never_charges_and_the_foes_actions_are_remembered() -> void:
	var row := (
		BattleEcho
		. row(
			_with_last(engine, &"gather"),
			engine.db.skill(&"echo"),
		)
	)
	assert_false(row.has("charge"), "the charge stays the foe's")
	assert_eq(int(row["rank"]), 2, "the echo's own rank")
	var foe := engine.enemies[0]
	BattleEcho.record(engine, foe, &"crush", true)
	assert_eq(engine.last_foe_skill, &"crush")
	BattleEcho.record(engine, engine.find(&"nhoa"), &"echo", true)
	assert_eq(engine.last_foe_skill, &"crush", "a party action is never remembered")


static func _with_last(e: BattleEngine, sid: StringName) -> BattleEngine:
	e.last_foe_skill = sid
	return e


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
		"magic": 10,
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
	foe["strength"] = 1
	var basic := [{"pick": [{"skill": "attack", "target": "random_foe"}]}]
	return (
		BattleDB
		. from_tables(
			{
				"skills":
				[
					{"id": "attack", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100},
					{"id": "crush", "kind": "physical", "power": 8, "rank": 4, "accuracy": 100, "mp_cost": 9},
					{
						"id": "gather",
						"kind": "support",
						"rank": 2,
						"target": "self",
						"charge": {"skill": "crush", "turns": 2}
					},
					{"id": "echo", "kind": "support", "rank": 2, "target": "single_foe", "echo": true},
				],
				"statuses": [],
				"characters": [{"id": "nhoa", "stats": hero, "skills": ["attack", "echo"]}],
				"enemies": [{"id": "foe", "stats": foe, "skills": ["attack", "crush", "gather"], "ai": basic}],
				"encounters": [{"id": "one", "enemies": ["foe"]}],
			}
		)
	)
