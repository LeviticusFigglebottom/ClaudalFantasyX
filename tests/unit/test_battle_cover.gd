extends TestCase
## M4-A2P-021 (BattleCover): the gallery ray glides out of reach every other turn; the glass skate is buried until it
## has acted once; cover never leaves the party with no foe to strike.

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()


func test_a_glider_is_out_of_reach_every_other_turn() -> void:
	_start(&"ray_and_crab")
	var ray := engine.enemies[0]
	assert_false(ray.untargetable, "up for the first round")
	BattleCover.on_turn_end(engine, ray)
	assert_true(ray.untargetable, "it glides after its turn")
	assert_false(engine.living_foes_of(engine.party_active[0]).has(ray), "no policy or menu may pick it")
	BattleCover.on_turn_end(engine, ray)
	assert_false(ray.untargetable, "and comes back down after the next")


func test_an_ambusher_is_buried_until_it_has_acted() -> void:
	_start(&"skate_and_crab")
	var skate := engine.enemies[0]
	assert_true(skate.untargetable, "buried from the start")
	BattleCover.on_turn_end(engine, skate)
	assert_false(skate.untargetable, "up after its first turn")
	BattleCover.on_turn_end(engine, skate)
	assert_false(skate.untargetable, "and stays up")


func test_cover_never_hides_the_last_foe() -> void:
	_start(&"two_skates")
	assert_false(engine.enemies[0].untargetable, "with every foe buried, the first stays up")
	assert_true(engine.enemies[1].untargetable)
	_start(&"two_rays")
	BattleCover.on_turn_end(engine, engine.enemies[0])
	BattleCover.on_turn_end(engine, engine.enemies[1])
	assert_eq(engine.living_foes_of(engine.party_active[0]).size(), 1, "one ray stays down")


func test_a_covered_foe_comes_up_when_the_visible_one_falls() -> void:
	_start(&"skate_and_crab")
	var skate := engine.enemies[0]
	engine.enemies[1].hp = 0
	BattleCover.keep_one(engine)
	assert_false(skate.untargetable)


func test_cover_never_lifts_a_phases_untargetable() -> void:
	_start(&"ray_and_crab")
	var crab := engine.enemies[1]
	crab.untargetable = true  # a phase row's (the Reach drawn back)
	engine.enemies[0].hp = 0
	BattleCover.keep_one(engine)
	assert_true(crab.untargetable)


func test_a_battle_with_a_glider_still_runs_to_its_end() -> void:
	_start(&"two_rays")
	var guard := 0
	while engine.outcome == &"" and guard < 400:
		guard += 1
		if engine.is_party_turn():
			var foes := engine.living_foes_of(engine.current)
			assert_false(foes.is_empty(), "the party always has a foe to strike")
			engine.perform(&"attack", [foes[0]] as Array[BattleCombatant])
		else:
			engine.run_enemy_turn()
	assert_eq(engine.outcome, BattleEngine.OUTCOME_VICTORY)


func _start(encounter: StringName) -> void:
	engine = BattleEngine.new()
	var active: Array[StringName] = [&"hero"]
	engine.setup(_db(), active, [] as Array[StringName], encounter, 1)
	engine.begin()


static func _db() -> BattleDB:
	var hero := {
		"level": 5,
		"hp": 4000,
		"mp": 20,
		"strength": 20,
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
	foe["hp"] = 300
	foe["mp"] = 0
	foe["strength"] = 1
	var basic := [{"pick": [{"skill": "attack", "target": "random_foe"}]}]
	return (
		BattleDB
		. from_tables(
			{
				"skills": [{"id": "attack", "kind": "physical", "power": 4, "rank": 3, "accuracy": 100}],
				"statuses": [],
				"characters": [{"id": "hero", "stats": hero, "skills": ["attack"]}],
				"enemies":
				[
					{"id": "ray", "stats": foe, "skills": ["attack"], "ai": basic, "glide": true},
					{"id": "skate", "stats": foe, "skills": ["attack"], "ai": basic, "ambush": true},
					{"id": "crab", "stats": foe, "skills": ["attack"], "ai": basic},
				],
				"encounters":
				[
					{"id": "ray_and_crab", "enemies": ["ray", "crab"]},
					{"id": "skate_and_crab", "enemies": ["skate", "crab"]},
					{"id": "two_skates", "enemies": ["skate", "skate"]},
					{"id": "two_rays", "enemies": ["ray", "ray"]},
				],
			}
		)
	)
