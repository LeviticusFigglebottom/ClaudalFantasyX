extends TestCase
## M4-A2P-020: a skill row's `root_turns` holds its target in the roots. While rooted_turns > 0 a hero on the field
## can't be swapped out (BattleEngine.FAIL_ROOTED), and the swap menu says why. It counts down at the end of each of the
## hero's own turns. The root crab's Root Drag is the first user.

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()
	var active: Array[StringName] = [&"hero"]
	var reserve: Array[StringName] = [&"spare"]
	engine.setup(_db(), active, reserve, &"one", 1)
	engine.begin()


func test_a_rooted_hero_cannot_be_swapped_out() -> void:
	var hero := engine.party_active[0]
	var hit := BattleHits.resolve(engine, engine.enemies[0], hero, engine.db.skill(&"root_grab"))
	assert_eq(int(hit["rooted"]), 2)
	assert_eq(hero.rooted_turns, 2)
	assert_eq(engine.swap_refusal(&"hero"), BattleEngine.FAIL_ROOTED)
	_until(hero)
	assert_false(engine.swap(&"hero", &"spare"), "the roots hold")
	assert_eq(engine.preview_swap(&"hero", &"spare"), [] as Array[TurnEntry], "no preview for a refused swap")
	assert_eq(engine.party_active[0], hero)


func test_the_hold_counts_down_on_the_heros_own_turns() -> void:
	var hero := engine.party_active[0]
	hero.rooted_turns = 2
	hero.tick_statuses()
	assert_eq(hero.rooted_turns, 1)
	hero.tick_statuses()
	assert_eq(hero.rooted_turns, 0)
	hero.tick_statuses()
	assert_eq(hero.rooted_turns, 0, "never below zero")
	assert_eq(engine.swap_refusal(&"hero"), &"")
	_until(hero)
	assert_true(engine.swap(&"hero", &"spare"), "free again")


func test_a_longer_hold_wins_and_a_fallen_hero_is_never_held() -> void:
	var hero := engine.party_active[0]
	hero.rooted_turns = 3
	BattleHits.resolve(engine, engine.enemies[0], hero, engine.db.skill(&"root_grab"))
	assert_eq(hero.rooted_turns, 3, "a shorter root doesn't cut a longer one")
	hero.hp = 0
	assert_eq(engine.swap_refusal(&"hero"), &"", "the fallen are swapped freely")


func test_the_swap_menu_says_the_roots_hold_them() -> void:
	var hero := engine.party_active[0]
	var menus := BattleMenus.new()
	assert_eq(menus.swap_lock_text(engine, &"hero"), "", "a free hero has no lock line")
	hero.rooted_turns = 1
	var why := menus.swap_lock_text(engine, &"hero")
	assert_true(why.contains(tr("HUD_SWAP_ROOTED")), "Pillar 4: the swap row says why (%s)" % why)


func _until(c: BattleCombatant) -> void:
	var guard := 0
	while engine.current != c and engine.outcome == &"" and guard < 50:
		guard += 1
		if engine.is_party_turn():
			engine.perform(&"attack", [engine.enemies[0]] as Array[BattleCombatant])
		else:
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
	foe["agility"] = 5
	foe["hp"] = 9000
	foe["mp"] = 0
	var basic := [{"pick": [{"skill": "attack", "target": "random_foe"}]}]
	return (
		BattleDB
		. from_tables(
			{
				"skills":
				[
					{"id": "attack", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100},
					{"id": "root_grab", "kind": "physical", "power": 1, "rank": 3, "accuracy": 100, "root_turns": 2},
				],
				"statuses": [],
				"characters":
				[
					{"id": "hero", "stats": hero, "skills": ["attack"]},
					{"id": "spare", "stats": hero, "skills": ["attack"]}
				],
				"enemies": [{"id": "crab", "stats": foe, "skills": ["attack", "root_grab"], "ai": basic}],
				"encounters": [{"id": "one", "enemies": ["crab"]}],
			}
		)
	)
