extends TestCase
## M1-ARC-06: save v4 (party vitals, attuned shrines, respawn point), the v3 -> v4 migration,
## load_into_game's game_loaded order, and the post-load starting-gear step (M1-PRG-03).

const TEST_DIR := "user://test_save_v4"

var saves: Node
var loaded: Array[Array] = []
var _saved_dir := ""
var _saved_state: GameStateData
var _saved_clock_running := true


func before_each() -> void:
	saves = (load("res://game/core/save_system.gd") as GDScript).new()
	_saved_dir = SaveSystem.save_dir
	_saved_state = Game.state
	_saved_clock_running = Game.play_clock_running
	SaveSystem.save_dir = TEST_DIR
	_clear()


func _v3_state() -> Dictionary:
	return {
		"version": 3,
		"state":
		{
			"chapter": 2,
			"location_id": "ch02/haluna",
			"currency": 40,
			"equipment": {"next_uid": 1, "owned": {}, "loadout": {}},
		},
	}


func test_v3_migrates_to_full_party_no_statuses_and_respawn_at_its_location() -> void:
	var step: Dictionary = saves._migrate_v3_to_v4(_v3_state())
	assert_eq(int(step["version"]), 4)
	var st: Dictionary = step["state"]
	assert_eq(st["party_vitals"], {}, "everyone at full HP/MP, no statuses")
	assert_eq(st["attuned_shrines"], [])
	assert_eq(st["respawn"], {"location_id": "ch02/haluna", "spawn": ""})
	var back: GameStateData = saves.deserialize(_v3_state())
	assert_eq(back.respawn_location_id, &"ch02/haluna")
	assert_eq(back.respawn_spawn, &"")
	assert_eq(back.party_vitals, {})
	assert_eq(back.attuned_shrines, [] as Array[StringName])
	assert_eq(back.currency, 40, "v3 fields survive")
	_done()


func test_v3_without_location_gets_an_empty_respawn_that_resolves_to_the_data_default() -> void:
	var back: GameStateData = saves.deserialize({"version": 3, "state": {"chapter": 1}})
	assert_eq(back.respawn_location_id, &"")
	var reg := LocationRegistry.load_default()
	var wr := WorldReturn.new()
	wr.registry = reg
	var to := wr.resolve(back)
	assert_eq(to[LocationRegistry.KEY_LOCATION], reg.default_location)
	assert_eq(to[LocationRegistry.KEY_SPAWN], reg.spawn_of(reg.default_location))
	wr.free()
	_done()


func test_v3_with_v4_fields_already_present_is_not_overwritten() -> void:
	var d := _v3_state()
	d["state"]["respawn"] = {"location_id": "field_test", "spawn": "Court"}
	d["state"]["attuned_shrines"] = ["save_shrine_test"]
	var back: GameStateData = saves.deserialize(d)
	assert_eq(back.respawn_spawn, &"Court")
	assert_eq(back.attuned_shrines, [&"save_shrine_test"] as Array[StringName])
	_done()


func test_v0_still_migrates_all_the_way() -> void:
	var back: GameStateData = saves.deserialize({"version": 0, "coin": 9, "location_id": "field_test"})
	assert_eq(back.currency, 9)
	assert_eq(back.respawn_location_id, &"field_test")
	assert_eq(back.equipment.get("next_uid"), 1)
	_done()


func test_v4_fields_round_trip_through_json() -> void:
	var s := GameStateData.new()
	s.party_vitals = {"rhen": {"hp": 120, "mp": 3, "statuses": ["poison"]}, "asha": {"statuses": ["zombie"]}}
	s.attuned_shrines = [&"a", &"b"] as Array[StringName]
	s.respawn_location_id = &"field_test"
	s.respawn_spawn = &"Shrine"
	var back: GameStateData = saves.deserialize(JSON.parse_string(JSON.stringify(saves.serialize(s))))
	assert_eq(back.vitals_of(&"rhen"), {"hp": 120, "mp": 3, "statuses": ["poison"]})
	assert_eq(back.statuses_of(&"asha"), [&"zombie"] as Array[StringName])
	assert_eq(typeof(back.vitals_of(&"rhen")["hp"]), TYPE_INT, "JSON floats become ints")
	assert_eq(back.attuned_shrines, [&"a", &"b"] as Array[StringName])
	assert_eq(back.respawn_location_id, &"field_test")
	assert_eq(back.respawn_spawn, &"Shrine")
	_done()


func test_damaged_v4_fields_are_rejected_or_cleaned() -> void:
	assert_false(SaveSystem.state_shape_ok({"party_vitals": []}))
	assert_false(SaveSystem.state_shape_ok({"respawn": "x"}))
	assert_false(SaveSystem.state_shape_ok({"attuned_shrines": {}}))
	var back := GameStateData.from_dict(
		{"party_vitals": {"rhen": "full", "asha": {"hp": -5, "mp": "x", "statuses": []}, "toma": {}}}
	)
	assert_eq(back.party_vitals, {"asha": {"hp": 0}}, "bad entries dropped, HP clamped at 0")
	var dup := GameStateData.from_dict({"attuned_shrines": ["a", "a"], "respawn": 3})
	assert_eq(dup.attuned_shrines, [&"a"] as Array[StringName])
	assert_eq(dup.respawn_location_id, &"")
	_done()


func test_load_into_game_emits_game_loaded_after_the_state_is_live() -> void:
	var s := GameStateData.new()
	s.chapter = 5
	assert_eq(SaveSystem.save_to_slot(2, s), OK)
	EventBus.game_loaded.connect(_on_loaded)
	assert_true(SaveSystem.load_from_slot(2) != null)
	assert_eq(loaded.size(), 0, "a plain read does not announce a load")
	assert_eq(SaveSystem.load_into_game(2), OK)
	assert_eq(loaded, [[2, 5]], "listeners see the loaded state")
	EventBus.game_loaded.disconnect(_on_loaded)
	_done()


func _on_loaded(slot: int) -> void:
	loaded.append([slot, Game.state.chapter])


func test_migrated_v2_save_with_joined_heroes_loads_with_their_weapons() -> void:
	var v2 := {"version": 2, "state": {"party_ids": ["rhen", "asha"], "reserve_ids": ["toma", "rhen"]}}
	var back: GameStateData = saves.deserialize(v2)
	var db := ItemDB.load_default()
	var bag := PartyGoods.from_state(db, back).equipment
	for cid: StringName in [&"rhen", &"asha", &"toma"]:
		assert_ne(bag.equipped(cid, ItemDB.SLOT_WEAPON), EquipmentBag.NO_PIECE, "%s has a weapon" % cid)
	assert_eq(bag.uids().size(), 6, "each hero got their weapon and armor once")
	var again: GameStateData = saves.deserialize(saves.serialize(back))
	assert_eq(PartyGoods.from_state(db, again).equipment.uids().size(), 6, "a second load adds nothing")
	_done()


func test_load_from_slot_fills_a_missing_required_slot() -> void:
	var s := GameStateData.new()
	s.party_ids = [&"rhen"] as Array[StringName]
	s.equipment = {"next_uid": 1, "owned": {}, "loadout": {"rhen": {}}}
	assert_eq(SaveSystem.save_to_slot(4, s), OK)
	var back := SaveSystem.load_from_slot(4)
	var bag := PartyGoods.from_state(ItemDB.load_default(), back).equipment
	assert_ne(bag.equipped(&"rhen", ItemDB.SLOT_WEAPON), EquipmentBag.NO_PIECE)
	assert_eq(bag.equipped(&"rhen", ItemDB.SLOT_ARMOR), EquipmentBag.NO_PIECE, "optional slots stay empty")
	_done()


func test_unjoined_heroes_get_nothing_on_load() -> void:
	var back: GameStateData = saves.deserialize({"version": 4, "state": {}})
	assert_eq(back.equipment.get("owned", {}), {})
	_done()


func _clear() -> void:
	for slot in SaveSystem.MAX_SLOT + 1:
		if SaveSystem.slot_exists(slot):
			SaveSystem.delete_slot(slot)
	DirAccess.remove_absolute(TEST_DIR)


func _done() -> void:
	_clear()
	SaveSystem.save_dir = _saved_dir
	Game.state = _saved_state
	Game.play_clock_running = _saved_clock_running
	loaded.clear()
	saves.free()
