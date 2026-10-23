extends TestCase
## M1-ARC-08: deep shape validation on load (SaveShape). Malformed data reads as corrupt in the
## menu (slot_info), loads as null (load_from_slot, deserialize) and never touches the live
## Game.state (load_into_game). Includes QA's review-sweep-C probe slot.

const TEST_DIR := "user://test_save_shape"

var saves: Node
var _saved_dir := ""
var _saved_state: GameStateData


func before_each() -> void:
	saves = (load("res://game/core/save_system.gd") as GDScript).new()
	_saved_dir = SaveSystem.save_dir
	_saved_state = Game.state
	SaveSystem.save_dir = TEST_DIR
	_clear()


## A fully populated v4 state, as to_dict writes it.
func _full_state() -> GameStateData:
	var s := GameStateData.new()
	s.flags = {"test_flag": true, "test_counter": 3, "test_text": "x"}
	s.party_ids = [&"rhen", &"asha"] as Array[StringName]
	s.reserve_ids = [&"toma"] as Array[StringName]
	s.inventory = {"potion": 2}
	s.currency = 120
	s.play_time_sec = 61.5
	s.location_id = &"ch02/haluna"
	s.chapter = 2
	s.lattice = {
		"board": "standard",
		"characters":
		{
			"rhen":
			{
				"position": "rh_01",
				"activated": ["rh_01"],
				"movement_points": 0,
				"lattice_points": 1,
				"movement_earned": 2
			}
		},
		"opened_gates": [],
	}
	s.equipment = {
		"next_uid": 3,
		"owned": {"1": {"base": "rhen_salvage_hooks", "abilities": ["", ""]}},
		"loadout": {"rhen": {"weapon": 1}},
	}
	s.party_vitals = {"rhen": {"hp": 10, "statuses": ["poison"]}}
	s.attuned_shrines = [&"haluna"] as Array[StringName]
	s.respawn_location_id = &"ch02/haluna"
	s.respawn_spawn = &"Shrine"
	return s


## The state as it comes back from a JSON file (every number a float).
func _json_state() -> Dictionary:
	return JSON.parse_string(JSON.stringify(_full_state().to_dict())) as Dictionary


func _bad(path: String, value: Variant) -> Dictionary:
	var st := _json_state()
	var keys := path.split(".")
	var d: Dictionary = st
	for i in keys.size() - 1:
		d = d[keys[i]]
	d[keys[keys.size() - 1]] = value
	return st


func test_a_real_state_passes_after_a_json_round_trip() -> void:
	assert_eq(SaveShape.problem(_json_state()), "")
	assert_eq(SaveShape.problem({}), "", "every key is optional")
	assert_true(SaveSystem.state_shape_ok(_json_state()))
	_done()


func test_element_types_are_checked() -> void:
	var cases := {
		"party_ids": [5, {}],
		"reserve_ids": ["ok", null],
		"attuned_shrines": [1.0],
		"location_id": {"a": 1},
		"flags": {"test_flag": [1]},
		"inventory": {"potion": "3"},
		"currency": 1.5,
		"chapter": -1,
		"play_time_sec": "long",
		"lattice.characters": [],
		"lattice.board": 7,
		"lattice.opened_gates": [3],
		"lattice.characters.rhen": "x",
		"lattice.characters.rhen.activated": [1],
		"lattice.characters.rhen.lattice_points": "1",
		"equipment.next_uid": 0,
		"equipment.owned": [],
		"equipment.owned.1": {"base": 4, "abilities": []},
		"equipment.loadout": {"rhen": {"weapon": "1"}},
		"party_vitals.rhen": {"hp": "full"},
		"party_vitals": {"rhen": {"statuses": "poison"}},
		"respawn": {"location_id": 3, "spawn": ""},
	}
	for path: String in cases:
		var p := SaveShape.problem(_bad(path, cases[path]))
		assert_ne(p, "", "%s = %s must be rejected" % [path, cases[path]])
	_done()


func test_problems_name_the_bad_value() -> void:
	assert_eq(SaveShape.problem(_bad("party_ids", ["rhen", 5])), "party_ids[1]: expected a String")
	var p := SaveShape.problem(_bad("equipment.owned", {"one": {"base": "x", "abilities": []}}))
	assert_true(p.contains("equipment.owned") and p.contains("one"), p)
	assert_eq(SaveShape.problem([]), "state: expected a Dictionary")
	_done()


func test_whole_numbers() -> void:
	assert_true(SaveShape.is_whole(3))
	assert_true(SaveShape.is_whole(3.0))
	assert_false(SaveShape.is_whole(2.7))
	assert_false(SaveShape.is_whole(INF))
	assert_false(SaveShape.is_whole(NAN))
	assert_false(SaveShape.is_whole("3"))
	_done()


func test_the_review_probe_slot_is_corrupt_and_never_loads() -> void:
	var probe := '{"version":3,"state":{"lattice":{"characters":[]},"party_ids":[5,{}],"location_id":{"a":1}}}'
	_write_raw(4, probe)
	assert_eq(SaveSystem.slot_info(4)["status"], SaveSystem.STATUS_CORRUPT)
	assert_eq(SaveSystem.slot_info(4)["location_key"], "", 'no LOCATION_{ "A": 1.0 }')
	assert_eq(SaveSystem.load_from_slot(4), null)
	_done()


func test_a_malformed_slot_leaves_the_live_game_alone() -> void:
	var live := GameStateData.new()
	live.chapter = 6
	Game.state = live
	_write_raw(5, JSON.stringify({"version": 4, "state": _bad("equipment.owned.1", {"base": "x", "abilities": [7]})}))
	assert_eq(SaveSystem.load_into_game(5), ERR_FILE_CORRUPT)
	assert_eq(Game.state, live, "not replaced")
	assert_eq(Game.state.chapter, 6)
	_done()


func test_versions_must_be_whole_numbers() -> void:
	var st := _full_state().to_dict()
	_write_raw(1, JSON.stringify({"version": 2.7, "state": st}))
	assert_eq(SaveSystem.slot_info(1)["status"], SaveSystem.STATUS_CORRUPT, "2.7 is not v2")
	assert_eq(SaveSystem.load_from_slot(1), null)
	_write_raw(2, JSON.stringify({"version": 4.0, "state": st}))
	assert_eq(SaveSystem.slot_info(2)["status"], SaveSystem.STATUS_OK, "JSON writes 4 and reads 4.0")
	_write_raw(3, JSON.stringify({"version": "4", "state": st}))
	assert_eq(SaveSystem.slot_info(3)["status"], SaveSystem.STATUS_CORRUPT)
	assert_eq(SaveSystem.load_from_slot(3), null, "load and listing agree")
	assert_eq(saves.migrate({"version": 1.5, "state": {}}), {})
	_done()


func test_deserialize_rejects_malformed_states_too() -> void:
	assert_eq(saves.deserialize({"version": 4, "state": _bad("party_ids", [1])}), null)
	assert_eq(saves.deserialize({"version": 4, "state": "x"}), null)
	assert_eq(saves.deserialize({"version": 99, "state": {}}), null)
	var back: GameStateData = saves.deserialize({"version": 4, "state": _json_state()})
	assert_true(back != null)
	assert_eq(back.party_ids, [&"rhen", &"asha"] as Array[StringName])
	_done()


func test_a_v2_save_with_float_counts_still_migrates() -> void:
	var v2 := {"version": 2, "state": {"inventory": {"potion": 3.0, "ether": 0.0}, "currency": 5.0}}
	_write_raw(1, JSON.stringify(v2))
	assert_eq(SaveSystem.slot_info(1)["status"], SaveSystem.STATUS_OK)
	var back := SaveSystem.load_from_slot(1)
	assert_eq(back.currency, 5)
	assert_eq(int(back.inventory.get("potion", 0)), 3)
	_done()


func test_load_and_listing_agree_on_every_case() -> void:
	var texts: Array[String] = [
		"",
		"[1]",
		'{"version": 4, "state": null}',
		'{"version": -1, "state": {}}',
		'{"version": 4, "state": {"respawn": {"spawn": []}}}',
		'{"version": 4, "state": {"flags": {"a": null}}}',
	]
	for i in texts.size():
		_write_raw(1, texts[i])
		assert_eq(SaveSystem.slot_info(1)["status"], SaveSystem.STATUS_CORRUPT, "case %d" % i)
		assert_eq(SaveSystem.load_from_slot(1), null, "case %d" % i)
	_done()


func _write_raw(slot: int, text: String) -> void:
	DirAccess.make_dir_recursive_absolute(TEST_DIR)
	var f := FileAccess.open(SaveSystem.slot_path(slot), FileAccess.WRITE)
	f.store_string(text)
	f.close()


func _done() -> void:
	saves.free()
	_clear()
	SaveSystem.save_dir = _saved_dir
	Game.state = _saved_state


func _clear() -> void:
	var dir := DirAccess.open(TEST_DIR)
	if dir == null:
		return
	for f in dir.get_files():
		DirAccess.remove_absolute(TEST_DIR.path_join(f))
	DirAccess.remove_absolute(TEST_DIR)
