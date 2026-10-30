extends TestCase
## M4-A2P-023 (BattleParts): a foe only one hero may act on (Malcor Venn's flat-engine: Liss breaks it), and a phase
## that comes when that foe is down (Venn boards on the break).

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()
	var active: Array[StringName] = [&"rhen", &"liss"]
	engine.setup(_db(), active, [] as Array[StringName], &"barge", 1)
	engine.begin()


func test_only_the_answering_hero_may_strike_the_part() -> void:
	var rhen := engine.find(&"rhen")
	var liss := engine.find(&"liss")
	var part := engine.enemies[1]
	assert_false(engine.living_foes_of(rhen).has(part), "Rhen can't reach the engine")
	assert_true(engine.living_foes_of(liss).has(part), "Liss can")
	assert_eq(engine.living_foes_of(rhen).size(), 1, "Venn is still Rhen's")


func test_a_group_skill_passes_over_the_part_and_a_single_one_is_refused() -> void:
	var rhen := engine.find(&"rhen")
	var part := engine.enemies[1]
	_until(rhen)
	var r := engine.perform(&"sweep", [engine.enemies[0], part] as Array[BattleCombatant])
	assert_true(r.ok, "the sweep isn't refused")
	for hit in r.hits:
		assert_ne(StringName(str(hit["target_id"])), part.id, "it passes over the engine")
	assert_eq(part.hp, part.max_hp)
	_until(rhen)
	assert_false(engine.perform(&"strike", [part] as Array[BattleCombatant]).ok, "a single strike can't pick it")


func test_breaking_the_part_brings_the_phase_whatever_the_hp() -> void:
	var venn := engine.enemies[0]
	var part := engine.enemies[1]
	assert_eq(venn.phase_index, -1)
	part.hp = 0
	BossMechanics.check_phases(engine)
	assert_eq(venn.phases[venn.phase_index]["id"], "boarded", "he boards on the break at full HP")
	assert_true(BattleParts.is_down(engine, &"flat_engine"))


func _until(c: BattleCombatant) -> void:
	var guard := 0
	while engine.current != c and engine.outcome == &"" and guard < 50:
		guard += 1
		if engine.is_party_turn():
			engine.perform(&"strike", [engine.enemies[0]] as Array[BattleCombatant])
		else:
			engine.run_enemy_turn()


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
	foe["strength"] = 1
	var basic := [{"pick": [{"skill": "strike", "target": "random_foe"}]}]
	var skills := ["strike", "sweep"]
	return (
		BattleDB
		. from_tables(
			{
				"skills":
				[
					{"id": "strike", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100},
					{"id": "sweep", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100, "target": "all_foes"},
				],
				"statuses": [],
				"characters":
				[{"id": "rhen", "stats": hero, "skills": skills}, {"id": "liss", "stats": hero, "skills": skills}],
				"enemies":
				[
					{
						"id": "venn",
						"stats": foe,
						"skills": ["strike"],
						"ai": basic,
						"phases": [{"id": "boarded", "at_hp_pct": 50, "when_down": "flat_engine"}],
					},
					{"id": "flat_engine", "stats": foe, "skills": ["strike"], "ai": basic, "answered_by": "liss"},
				],
				"encounters": [{"id": "barge", "enemies": ["venn", "flat_engine"]}],
			}
		)
	)
