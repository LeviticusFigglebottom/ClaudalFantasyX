extends TestCase
## M4-A2P-022 (BattleParts): a part broken on the weak point stays broken and silences its gather; a tender's
## restores_part mends it; the tender ignores the party until its keeper is struck.

var engine: BattleEngine
var restored: Array = []


func before_each() -> void:
	engine = BattleEngine.new()
	var active: Array[StringName] = [&"hero"]
	engine.setup(_db(), active, [] as Array[StringName], &"hall", 1)
	engine.part_restored.connect(func(e: BattleCombatant, sid: StringName) -> void: restored.append([e.id, sid]))
	engine.begin()
	restored.clear()


func test_a_broken_charge_breaks_its_part_and_silences_the_gather() -> void:
	var keeper := engine.enemies[0]
	BattleParts.on_charge_broken(keeper, &"ring_burn")
	assert_eq(keeper.broken_parts, [&"ring_burn"] as Array[StringName])
	assert_true(BattleParts.silenced(engine, keeper, &"ring_gather"), "the broken ring can't gather")
	assert_false(BattleParts.silenced(engine, keeper, &"trim"))
	for i in 20:
		var pick := EnemyAI.choose(engine, keeper)
		assert_ne(pick.get("skill", &""), &"ring_gather", "the AI never picks a silenced gather")
	BattleParts.on_charge_broken(keeper, &"not_a_part")
	assert_eq(keeper.broken_parts.size(), 1, "a charge the row doesn't name as a part breaks nothing")


func test_a_weak_point_break_on_a_part_keeps_it_broken() -> void:
	var keeper := engine.enemies[0]
	keeper.charge_skill = &"ring_burn"
	keeper.charge_left = 2
	keeper.charge_row = engine.db.skill(&"ring_burn")
	keeper.weak_hits = 0
	var r := engine.perform(&"jab", [keeper] as Array[BattleCombatant])
	assert_true(r.ok)
	assert_eq(keeper.charge_skill, &"", "the charge is broken")
	assert_true(keeper.broken_parts.has(&"ring_burn"), "and the ring with it")
	assert_true(keeper.struck)


func test_the_tender_mends_the_longest_broken_part() -> void:
	var keeper := engine.enemies[0]
	var tender := engine.enemies[1]
	keeper.broken_parts = [&"ring_burn", &"core_burn"] as Array[StringName]
	var hit := BattleHits.resolve(engine, tender, keeper, engine.db.skill(&"mend"))
	assert_eq(hit["part_restored"], &"ring_burn")
	assert_eq(keeper.broken_parts, [&"core_burn"] as Array[StringName])
	assert_eq(restored, [[keeper.id, &"ring_burn"]], "the stage hears it (part_restored)")
	var none := BattleHits.resolve(engine, tender, tender, engine.db.skill(&"mend"))
	assert_false(none.has("part_restored"), "nothing to mend: no effect")


func test_the_tender_waits_until_its_keeper_is_struck_then_mends_first() -> void:
	var keeper := engine.enemies[0]
	var tender := engine.enemies[1]
	assert_eq(EnemyAI.choose(engine, tender)["skill"], &"tend_idle", "it ignores the party")
	keeper.struck = true
	assert_eq(EnemyAI.choose(engine, tender)["skill"], &"jab", "struck: it fights")
	keeper.broken_parts = [&"ring_burn"] as Array[StringName]
	var pick := EnemyAI.choose(engine, tender)
	assert_eq(pick["skill"], &"mend", "a broken ring comes first")
	assert_eq(pick["targets"], [keeper])


static func _db() -> BattleDB:
	var hero := {
		"level": 5,
		"hp": 4000,
		"mp": 20,
		"strength": 10,
		"magic": 1,
		"defense": 5,
		"magic_defense": 5,
		"agility": 30,
		"accuracy": 0,
		"evasion": 0,
		"luck": 0,
	}
	var foe := hero.duplicate()
	foe["agility"] = 5
	foe["hp"] = 9000
	foe["mp"] = 0
	var keeper_ai := [
		{"if": {"turn_mod": [2, 0]}, "pick": [{"skill": "ring_gather", "target": "self"}]},
		{"pick": [{"skill": "trim", "target": "random_foe"}]},
	]
	var tender_ai := [
		{"if": {"ally_part_broken": true}, "pick": [{"skill": "mend", "target": "broken_ally"}]},
		{"if": {"ally_struck": true}, "pick": [{"skill": "jab", "target": "random_foe"}]},
		{"pick": [{"skill": "tend_idle", "target": "self"}]},
	]
	return (
		BattleDB
		. from_tables(
			{
				"skills":
				[
					{"id": "trim", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100},
					{"id": "jab", "kind": "physical", "power": 1, "rank": 1, "accuracy": 100},
					{
						"id": "ring_gather",
						"kind": "support",
						"rank": 2,
						"target": "self",
						"charge": {"skill": "ring_burn", "turns": 2}
					},
					{"id": "ring_burn", "kind": "magical", "power": 4, "rank": 4, "target": "all_foes", "magic": true},
					{"id": "core_burn", "kind": "magical", "power": 4, "rank": 4, "target": "all_foes", "magic": true},
					{"id": "mend", "kind": "support", "rank": 3, "target": "single_ally", "restores_part": true},
					{"id": "tend_idle", "kind": "support", "rank": 3, "target": "self"},
				],
				"statuses": [],
				"characters": [{"id": "hero", "stats": hero, "skills": ["jab"]}],
				"enemies":
				[
					{
						"id": "keeper",
						"stats": foe,
						"skills": ["trim", "ring_gather"],
						"ai": keeper_ai,
						"parts": ["ring_burn", "core_burn"],
						"weak_point": {"hits": 1, "max_delay": 9999},
					},
					{"id": "tender", "stats": foe, "skills": ["jab", "mend", "tend_idle"], "ai": tender_ai},
				],
				"encounters": [{"id": "hall", "enemies": ["keeper", "tender"]}],
			}
		)
	)
