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
	assert_true(SaveShape.is_whole(float(SaveShape.MAX_WHOLE)), "2^53 is the bound")
	assert_true(SaveShape.is_whole(-float(SaveShape.MAX_WHOLE)))
	assert_false(SaveShape.is_whole(float(SaveShape.MAX_WHOLE) * 2.0), "above 2^53")
	assert_false(SaveShape.is_whole(1e19), "past int64: int() would wrap")
	assert_false(SaveShape.is_whole(SaveShape.MAX_WHOLE + 1), "ints are bounded too")
	_done()


## QA review-sweep-E S1: each of these passed the old check and loaded as -9223372036854775808.
func test_huge_whole_numbers_are_rejected() -> void:
	var cases := {
		"currency": 1e300,
		"chapter": 1e19,
		"inventory.potion": 1e20,
		"party_vitals.rhen.hp": 1e300,
		"lattice.characters.rhen.lattice_points": 1e19,
		"equipment.next_uid": 1e300,
	}
	for path: String in cases:
		var p := SaveShape.problem(_bad(path, cases[path]))
		assert_ne(p, "", "%s = %s must be rejected" % [path, cases[path]])
		assert_true(p.begins_with(path), "names the value: " + p)
	var slot := _json_state()
	slot["currency"] = 1e300
	_write_raw(4, JSON.stringify({"version": SaveSystem.SAVE_VERSION, "state": slot}))
	assert_eq(SaveSystem.slot_info(4)["status"], SaveSystem.STATUS_CORRUPT, "the menu shows it as damaged")
	assert_eq(SaveSystem.load_from_slot(4), null, "it never loads with a negative purse")
	assert_eq(SaveShape.problem(_bad("currency", float(SaveShape.MAX_WHOLE))), "", "the bound itself loads")
	_done()


## QA review-sweep-E S2: EquipmentBag trusts next_uid, the owned keys and the loadout uids.
func test_equipment_uids_must_be_consistent() -> void:
	var piece := {"base": "rhen_salvage_hooks", "abilities": ["", ""]}
	var cases := {
		"next_uid at the top uid would overwrite it": {"next_uid": 1, "owned": {"1": piece}, "loadout": {}},
		"next_uid below the top uid": {"next_uid": 2, "owned": {"1": piece, "5": piece}, "loadout": {}},
		"no next_uid with pieces owned": {"owned": {"1": piece}, "loadout": {}},
		"a zero-padded key": {"next_uid": 9, "owned": {"05": piece}, "loadout": {}},
		"a signed key": {"next_uid": 9, "owned": {"+1": piece}, "loadout": {}},
		"a huge key": {"next_uid": 9, "owned": {"99999999999999999999": piece}, "loadout": {}},
		"a loadout piece that is not owned": {"next_uid": 3, "owned": {"1": piece}, "loadout": {"rhen": {"weapon": 2}}},
	}
	for why: String in cases:
		assert_ne(SaveShape.problem(_bad("equipment", cases[why])), "", why)
	var p := SaveShape.problem(_bad("equipment", cases["next_uid at the top uid would overwrite it"]))
	assert_eq(p, "equipment.next_uid: expected a whole number > 1 (the highest owned uid)")
	var fine := {
		"next_uid": 6.0,
		"owned": {"1": piece, "5": piece},
		"loadout": {"rhen": {"weapon": 5.0, "armor": 0.0}},
	}
	assert_eq(SaveShape.problem(_bad("equipment", fine)), "", "0 is an empty slot; JSON floats are fine")
	assert_eq(SaveShape.problem(_bad("equipment", {"next_uid": 1, "owned": {}, "loadout": {}})), "", "empty bag")
	assert_eq(SaveShape.problem(_bad("equipment", {})), "", "an empty record is filled by EquipmentBag")
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


## M1-ARC-11 (QA review-sweep-F F1 on M1-ARC-08): the v2->v3 migration ran int() on raw values
## before the shape check: a nested value was a script error (the runner fails the test on one),
## a huge count wrapped and was dropped, and a string was coerced. Every older version is covered,
## because each one runs through the v2 step.
func test_malformed_old_inventories_read_as_corrupt_never_coerced() -> void:
	var inventories: Array = [
		{"potion": {"x": 1}},
		{"potion": 1e20, "ether": 7},
		{"potion": 1, "ether": "7"},
		{"potion": 1.5},
		[1, 2],
		"potion",
	]
	var slot := 1
	for inv: Variant in inventories:
		for version: int in [0, 1, 2]:
			var st := {"inventory": inv, "chapter": 1}
			var data: Dictionary = st.duplicate() if version == 0 else {"version": version, "state": st}
			if version == 0:
				data["version"] = 0
			var why := "v%d inventory %s" % [version, JSON.stringify(inv)]
			assert_eq(saves.deserialize(JSON.parse_string(JSON.stringify(data)) as Dictionary), null, why)
			_write_raw(slot, JSON.stringify(data))
			assert_eq(SaveSystem.slot_info(slot)["status"], SaveSystem.STATUS_CORRUPT, why + " (listing)")
			assert_eq(SaveSystem.load_from_slot(slot), null, why + " (load)")
	var ok := {"version": 2, "state": {"inventory": {"potion": 3.0, "ether": 0.0, "salt": 2}}}
	var back: GameStateData = saves.deserialize(JSON.parse_string(JSON.stringify(ok)) as Dictionary)
	assert_eq(back.inventory, {"potion": 3, "salt": 2}, "whole counts still migrate, and empty stacks drop")
	_done()


## M1-ARC-11 (review-sweep-G S1): a negative count in a v0, v1 or v2 inventory is an empty stack,
## dropped as the v2 -> v3 step always did (v2 never normalized counts); from v3 on it is corrupt.
func test_a_negative_legacy_count_is_dropped_not_corrupt() -> void:
	for version: int in [0, 1, 2]:
		var st := {"inventory": {"potion": -2, "ether": 3.0}, "chapter": 1}
		var data: Dictionary = st.duplicate() if version == 0 else {"version": version, "state": st}
		data["version"] = version
		_write_raw(1, JSON.stringify(data))
		assert_eq(SaveSystem.slot_info(1)["status"], SaveSystem.STATUS_OK, "v%d listing" % version)
		var back := SaveSystem.load_from_slot(1)
		assert_true(back != null, "v%d loads" % version)
		if back != null:
			assert_eq(back.inventory, {"ether": 3}, "v%d: the negative stack is dropped" % version)
	_write_raw(1, JSON.stringify({"version": 3, "state": {"inventory": {"potion": -2}}}))
	assert_eq(SaveSystem.slot_info(1)["status"], SaveSystem.STATUS_CORRUPT, "v3: corrupt")
	_done()


## M1-ARC-11 (review-sweep-F nits on M1-ARC-08 and M1-PRG-03): a piece worn twice is corrupt,
## whatever the item tables say.
func test_a_piece_worn_twice_is_corrupt() -> void:
	var hooks := {"base": "rhen_salvage_hooks", "abilities": ["", ""]}
	var staff := {"base": "asha_vigil_staff", "abilities": []}
	var cases := {
		"one piece worn by two heroes":
		{"next_uid": 3, "owned": {"1": hooks, "2": staff}, "loadout": {"rhen": {"weapon": 1}, "asha": {"weapon": 1}}},
		"one piece in two slots":
		{"next_uid": 2, "owned": {"1": hooks}, "loadout": {"rhen": {"weapon": 1, "armor": 1}}},
		"an unowned piece": {"next_uid": 3, "owned": {"1": hooks}, "loadout": {"rhen": {"weapon": 2}}},
	}
	for why: String in cases:
		var st := _bad("equipment", cases[why])
		assert_eq(saves.deserialize({"version": 4, "state": st}), null, why)
		_write_raw(1, JSON.stringify({"version": 4, "state": st}))
		assert_eq(SaveSystem.slot_info(1)["status"], SaveSystem.STATUS_CORRUPT, why + " (listing)")
		assert_eq(SaveSystem.load_from_slot(1), null, why + " (load)")
	assert_true(
		SaveShape.problem(_bad("equipment", cases["one piece worn by two heroes"])).contains("already worn"),
		"double wear is a shape problem"
	)
	_done()


## M1-ARC-11 (QA review-sweep-G B1): what only the item tables make wrong (a later equipment.json
## renames or removes a base, or moves a gear type to another hero or slot) is repaired on load:
## the piece comes off into the bag, and the weapon slot is refilled. The save lists as OK and
## loads; it is never corrupt. M1-ARC-12: a piece whose base is unknown is kept too, unworn.
func test_a_loadout_the_tables_no_longer_fit_is_repaired_on_load() -> void:
	var hooks := {"base": "rhen_salvage_hooks", "abilities": ["", ""]}
	var coral := {"base": "rhen_coral_hooks", "abilities": []}
	var tether := {"base": "rhen_patched_tether", "abilities": []}
	var staff := {"base": "asha_vigil_staff", "abilities": []}
	var unknown := {"base": "old_reef_hooks", "abilities": []}
	# [equipment, rhen's weapon base after load, is uid 1 still owned]
	var cases := {
		"another hero's piece (a re-assigned weapon)":
		[{"next_uid": 2, "owned": {"1": staff}, "loadout": {"rhen": {"weapon": 1}}}, &"rhen_salvage_hooks", true],
		"a weapon in the armor slot":
		[{"next_uid": 2, "owned": {"1": hooks}, "loadout": {"rhen": {"armor": 1}}}, &"rhen_salvage_hooks", true],
		"a renamed base":
		[{"next_uid": 2, "owned": {"1": unknown}, "loadout": {"rhen": {"weapon": 1}}}, &"rhen_salvage_hooks", true],
		"a renamed base with a spare that fits":
		[
			{"next_uid": 3, "owned": {"1": unknown, "2": coral}, "loadout": {"rhen": {"weapon": 1}}},
			&"rhen_coral_hooks",
			true
		],
	}
	for why: String in cases:
		var row: Array = cases[why]
		var st := _bad("equipment", row[0])
		st["party_ids"] = ["rhen"]
		st["reserve_ids"] = []
		_write_raw(1, JSON.stringify({"version": 4, "state": st}))
		assert_eq(SaveSystem.slot_info(1)["status"], SaveSystem.STATUS_OK, why + " (listing)")
		for loaded: GameStateData in [
			SaveSystem.load_from_slot(1), saves.deserialize({"version": 4, "state": st.duplicate(true)})
		]:
			assert_true(loaded != null, why + " loads")
			if loaded == null:
				continue
			var bag := EquipmentBag.new(ItemDB.load_default(), loaded.equipment)
			assert_eq(bag.base_of(bag.equipped(&"rhen", &"weapon")), row[1], why + ": the weapon slot is refilled")
			assert_eq(bag.has_piece(1), row[2], why + ": kept in the bag, even when unknown")
			assert_eq(bag.loadout_problem(), "", why + ": the loadout is one equip() could make")
	var fine := {
		"next_uid": 10,
		"owned": {"1": hooks, "2": tether, "3": staff, "9": unknown},
		"loadout": {"rhen": {"weapon": 1, "armor": 2}, "asha": {"weapon": 3, "armor": 0}},
	}
	var back: GameStateData = saves.deserialize({"version": 4, "state": _bad("equipment", fine)})
	assert_true(back != null, "a valid loadout loads")
	assert_eq(back.equipment["loadout"]["rhen"], {"weapon": 1, "armor": 2}, "a fitting loadout is untouched")
	assert_eq(back.equipment["owned"]["9"], unknown, "an unworn piece of unknown gear is kept as saved")
	_done()


func test_loadout_problem_names_the_slot() -> void:
	var db := ItemDB.load_default()
	var bag := EquipmentBag.new(db)
	var hooks := bag.add_piece(&"rhen_salvage_hooks")
	assert_eq(bag.equip(&"rhen", hooks), EquipmentBag.RESULT_OK)
	assert_eq(bag.loadout_problem(), "", "made by equip()")
	bag.data["loadout"]["asha"] = {"weapon": hooks}
	assert_true(bag.loadout_problem().contains("is already worn at"), bag.loadout_problem())
	bag.data["loadout"].erase("rhen")
	assert_true(bag.loadout_problem().contains("loadout.asha.weapon"), bag.loadout_problem())
	assert_true(bag.loadout_problem().contains(String(EquipmentBag.ERR_WRONG_CHARACTER)), bag.loadout_problem())
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
