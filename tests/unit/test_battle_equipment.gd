extends TestCase
## M1-CMB-06: equipment effects the engine runs from the combatant's equipment data
## (BattleCombatant.EQUIPMENT_META, written by EquipmentEffects.apply_to): the basic Attack's
## element, status strikes on physical hits, status wards, and low-HP auto-statuses.

var engine: BattleEngine


func before_each() -> void:
	engine = BattleEngine.new()


func test_meta_key_matches_progression() -> void:
	assert_eq(BattleCombatant.EQUIPMENT_META, EquipmentEffects.META_KEY)
	assert_eq(BattleCombatant.new().equipment(), {})


# --- attack element ----------------------------------------------------------------------


func test_attack_takes_the_element_the_target_is_weakest_to() -> void:
	_start({"attack_elements": [&"fire", &"ice"]}, &"icy")
	var r := engine.perform(&"attack", _foe())
	assert_eq(r.hits[0]["element"], &"ice", "weak to ice beats normal fire")


func test_attack_element_ties_go_to_the_first_and_avoid_absorb() -> void:
	_start({"attack_elements": [&"fire", &"ice"]}, &"plain")
	assert_eq(engine.perform(&"attack", _foe()).hits[0]["element"], &"fire", "tie: first in slot order")
	engine = BattleEngine.new()
	_start({"attack_elements": [&"water", &"ice"]}, &"soaker")
	assert_eq(engine.perform(&"attack", _foe()).hits[0]["element"], &"ice", "never the absorbed element if avoidable")


func test_other_skills_and_bare_heroes_keep_their_element() -> void:
	_start({"attack_elements": [&"fire"]}, &"icy")
	assert_eq(engine.perform(&"jab", _foe()).hits[0]["element"], &"none", "only the basic Attack takes it")
	engine = BattleEngine.new()
	_start({}, &"icy")
	assert_eq(engine.perform(&"attack", _foe()).hits[0]["element"], &"none")


func test_attack_element_changes_damage() -> void:
	_start({"attack_elements": [&"ice"]}, &"icy")
	var foe := _foe()[0]
	var hp := foe.hp
	var r := engine.perform(&"attack", _foe())
	var dealt := hp - foe.hp
	assert_eq(dealt, r.hits[0]["amount"])
	assert_true(dealt >= Formulas.damage(8, 10, 5, 10, Formulas.VARIANCE_MIN_PCT, &"weak", false, false, false))


# --- status strikes ----------------------------------------------------------------------


func test_status_strike_lands_after_a_hit() -> void:
	_start({"on_hit_statuses": [{"id": &"poison", "chance": 100, "duration": -1}]}, &"plain")
	var foe := _foe()[0]
	var r := engine.perform(&"attack", _foe())
	assert_true(foe.has_status(&"poison"))
	assert_eq(r.hits[0]["statuses_added"], [&"poison"])


func test_status_strike_only_on_physical_hits_that_land_on_the_living() -> void:
	_start({"on_hit_statuses": [{"id": &"poison", "chance": 100, "duration": -1}]}, &"plain")
	var foe := _foe()[0]
	engine.perform(&"zap", _foe())
	assert_false(foe.has_status(&"poison"), "magic does not strike")
	_to_party_turn()
	foe.hp = 1
	engine.perform(&"attack", _foe())
	assert_false(foe.is_alive())
	assert_eq(foe.statuses, {}, "no strike on a felled target")


func test_status_strike_never_on_a_miss() -> void:
	var misses := 0
	for s in range(1, 60):
		engine = BattleEngine.new()
		_start({"on_hit_statuses": [{"id": &"slow", "chance": 100, "duration": 2}]}, &"dodger", s)
		var foe := _foe()[0]
		var r := engine.perform(&"attack", _foe())
		if not r.hits[0]["hit"]:
			misses += 1
			assert_false(foe.has_status(&"slow"))
	assert_true(misses > 0, "the dodger evades sometimes")


func test_status_strike_chance_rolls_on_the_seed() -> void:
	var a: Array[bool] = []
	var b: Array[bool] = []
	for s in range(1, 30):
		a.append(_strike_lands(s))
		b.append(_strike_lands(s))
	assert_eq(a, b)
	assert_true(a.has(true) and a.has(false), "a 50% strike sometimes lands")


# --- wards -------------------------------------------------------------------------------


func test_ward_blocks_the_status_from_any_source() -> void:
	_start({"status_wards": [&"poison"]}, &"venomous")
	var hero := engine.find(&"hero")
	assert_true(hero.is_warded(&"poison"))
	assert_false(hero.add_status(&"poison", -1))
	assert_true(hero.add_status(&"slow", 2), "other statuses still land")
	for i in 20:
		if engine.outcome != &"":
			break
		_step()
	assert_false(hero.has_status(&"poison"), "the venomous foe's 100% poison never sticks")


# --- low-HP auto-statuses ----------------------------------------------------------------


func test_low_hp_status_switches_on_below_and_off_when_healed() -> void:
	_start({"low_hp_statuses": [{"id": &"haste", "hp_below_pct": 50, "duration": -1}]}, &"plain")
	var hero := engine.find(&"hero")
	hero.hp = 149  # 149 x 100 < 300 x 50
	_end_a_turn()
	assert_true(hero.has_status(&"haste"))
	assert_eq(hero.low_hp_owned, [&"haste"] as Array[StringName])
	hero.hp = 150  # at the threshold counts as healed
	_end_a_turn()
	assert_false(hero.has_status(&"haste"))
	assert_eq(hero.low_hp_owned, [] as Array[StringName])


func test_low_hp_status_leaves_the_same_status_from_elsewhere() -> void:
	_start({"low_hp_statuses": [{"id": &"haste", "hp_below_pct": 50, "duration": -1}]}, &"plain")
	var hero := engine.find(&"hero")
	hero.add_status(&"haste", 4)
	hero.hp = 100
	_end_a_turn()
	hero.hp = 300
	_end_a_turn()
	assert_true(hero.has_status(&"haste"), "a cast Haste is not the equipment's to remove")


func test_low_hp_status_returns_if_removed_and_clears_on_ko() -> void:
	_start({"low_hp_statuses": [{"id": &"regen", "hp_below_pct": 50, "duration": -1}]}, &"plain")
	var hero := engine.find(&"hero")
	hero.hp = 100
	hero.sync_low_hp()
	hero.statuses.erase(&"regen")  # e.g. a future dispel
	hero.sync_low_hp()
	assert_true(hero.has_status(&"regen"), "still below the threshold: it comes back")
	assert_eq(hero.low_hp_owned.count(&"regen"), 1)
	hero.apply_damage(9999)
	hero.sync_low_hp()
	assert_eq(hero.low_hp_owned, [] as Array[StringName])


func test_low_hp_checked_on_swap_in() -> void:
	_start({"low_hp_statuses": [{"id": &"haste", "hp_below_pct": 50, "duration": -1}]}, &"plain")
	var bench := engine.find(&"bench")
	bench.hp = 10
	assert_true(engine.swap(engine.current.id, &"bench"))
	assert_true(bench.has_status(&"haste"))


# --- real equipment ----------------------------------------------------------------------


func test_real_equipment_effects_drive_the_engine() -> void:
	var idb := ItemDB.load_default()
	var bag := EquipmentBag.new(idb)
	var hooks := bag.add_piece(&"rhen_coral_hooks")  # Ember Edge
	bag.equip(&"rhen", hooks)
	var harness := bag.add_piece(&"rhen_reefline_harness")  # Bitterward
	bag.equip(&"rhen", harness)
	var fx := EquipmentEffects.new(idb, bag)
	engine.party_modifier = fx.apply_to
	var active: Array[StringName] = [&"rhen", &"asha"]
	engine.setup(BattleDB.load_default(), active, [] as Array[StringName], &"sandbox_reef", 2)
	var rhen := engine.find(&"rhen")
	assert_true(rhen.is_warded(&"poison"))
	var eel := engine.enemies[1]
	assert_eq(engine.attack_element(rhen, eel, engine.db.skill(&"attack")), &"fire", "the eel is weak to fire")
	var crab := engine.enemies[0]
	assert_eq(engine.attack_element(rhen, crab, engine.db.skill(&"attack")), &"fire", "only one element: it is used")
	assert_eq(engine.attack_element(engine.find(&"asha"), eel, engine.db.skill(&"attack")), &"none")


# --- helpers -----------------------------------------------------------------------------


func _strike_lands(rng_seed: int) -> bool:
	engine = BattleEngine.new()
	_start({"on_hit_statuses": [{"id": &"slow", "chance": 50, "duration": 2}]}, &"plain", rng_seed)
	var foe := _foe()[0]
	engine.perform(&"attack", _foe())
	return foe.has_status(&"slow")


## Ends the current turn with a harmless jab so the engine re-checks HP thresholds.
func _end_a_turn() -> void:
	_to_party_turn()
	engine.perform(&"jab", _foe())


func _step() -> void:
	if engine.is_party_turn():
		engine.perform(&"jab", _foe())
	else:
		engine.run_enemy_turn()


func _start(equipment: Dictionary, encounter: StringName, rng_seed: int = 1) -> void:
	engine.party_modifier = func(c: BattleCombatant) -> void: c.set_meta(BattleCombatant.EQUIPMENT_META, equipment)
	var active: Array[StringName] = [&"hero", &"helper"]
	var reserve: Array[StringName] = [&"bench"]
	engine.setup(_db(), active, reserve, encounter, rng_seed)
	engine.begin()
	_to_party_turn()


func _to_party_turn() -> void:
	var guard := 0
	while not engine.is_party_turn() and engine.outcome == &"" and guard < 50:
		guard += 1
		engine.run_enemy_turn()


func _foe() -> Array[BattleCombatant]:
	var out: Array[BattleCombatant] = [engine.living_foes_of(engine.current)[0]]
	return out


static func _db() -> BattleDB:
	var hero := {
		"level": 5,
		"hp": 300,
		"mp": 40,
		"strength": 10,
		"magic": 10,
		"defense": 10,
		"magic_defense": 10,
		"agility": 30,
		"accuracy": 0,
		"evasion": 0,
		"luck": 0,
	}
	var helper := hero.duplicate()
	helper["agility"] = 20
	var foe := hero.duplicate()
	foe["agility"] = 4
	foe["hp"] = 9000
	foe["strength"] = 1
	var dodgy := foe.duplicate()
	dodgy["evasion"] = 60
	var ai := [{"pick": [{"skill": "attack", "target": "random_foe"}]}]
	var venom_ai := [{"pick": [{"skill": "venom", "target": "random_foe"}]}]
	var skills := ["attack", "jab", "zap"]
	return (
		BattleDB
		. from_tables(
			{
				"skills":
				[
					{"id": "attack", "kind": "physical", "power": 8, "rank": 3, "accuracy": 100, "element": "none"},
					{"id": "jab", "kind": "physical", "power": 1, "rank": 1, "accuracy": 100},
					{"id": "zap", "kind": "magical", "power": 2, "rank": 3, "magic": true},
					{
						"id": "venom",
						"kind": "support",
						"rank": 3,
						"statuses": [{"id": "poison", "chance": 100, "duration": -1}],
					},
				],
				"statuses": [],
				"characters":
				[
					{"id": "hero", "stats": hero, "skills": skills},
					{"id": "helper", "stats": helper, "skills": skills},
					{"id": "bench", "stats": hero, "skills": skills},
				],
				"enemies":
				[
					{"id": "plain", "stats": foe, "skills": ["attack"], "ai": ai},
					{"id": "icy", "stats": foe, "skills": ["attack"], "ai": ai, "affinities": {"ice": "weak"}},
					{"id": "soaker", "stats": foe, "skills": ["attack"], "ai": ai, "affinities": {"water": "absorb"}},
					{"id": "dodger", "stats": dodgy, "skills": ["attack"], "ai": ai},
					{"id": "venomous", "stats": foe, "skills": ["venom"], "ai": venom_ai},
				],
				"encounters":
				[
					{"id": "plain", "enemies": ["plain"]},
					{"id": "icy", "enemies": ["icy"]},
					{"id": "soaker", "enemies": ["soaker"]},
					{"id": "dodger", "enemies": ["dodger"]},
					{"id": "venomous", "enemies": ["venomous"]},
				],
			}
		)
	)
