extends TestCase
## M1-ARC-12 (QA review-sweep-H; ADR 0018 Amendment 4):
##   - S1 (MUST): while an item table is missing or fails to parse, a load keeps the equipment as
##     saved (no repair) and no save is written over any slot; a broken equipment.json is the case;
##   - a piece whose base the tables do not know is kept in the bag, untouched, and only equipping
##     it is refused;
##   - S2: a write over a newer build's slot keeps a numbered `.newer` copy first.

const TEST_DIR := "user://test_save_item_tables"
const DATA_DIR := "user://test_save_item_tables_data"
const T_SAVED := 1792489500

var _saved_dir := ""
var _saved_clock: Callable
var _saved_enabled := true
var _saved_state: GameStateData
var _saved_play_clock := true


func before_each() -> void:
	_saved_dir = SaveSystem.save_dir
	_saved_clock = SaveSystem.clock
	_saved_enabled = SaveSystem.autosave_enabled
	_saved_state = Game.state
	_saved_play_clock = Game.play_clock_running
	SaveSystem.save_dir = TEST_DIR
	SaveSystem.clock = func() -> int: return T_SAVED
	SaveSystem.autosave_enabled = true
	SaveSystem.cancel_pending_autosave()
	SaveSystem._item_db = null
	_clear(TEST_DIR)
	_clear(DATA_DIR)
	Game.state = GameStateData.new()


## A chapter 6 run: rhen and asha, five pieces, rhen's spare customised, all known to the tables.
func _ch6_state() -> GameStateData:
	var st := GameStateData.new()
	st.chapter = 6
	st.play_time_sec = 21600.0
	st.location_id = &"ch02/haluna"
	st.party_ids = [&"rhen", &"asha"] as Array[StringName]
	var bag := EquipmentBag.new(ItemDB.load_default(), st.equipment)
	assert_true(bag.grant_starting(&"rhen"))
	var spare := bag.add_piece(&"rhen_coral_hooks")
	assert_true(bag.set_slot(spare, 1, &"tide_edge"), "customised")
	assert_true(bag.grant_starting(&"asha"))
	return st


## A copy of the real item tables in DATA_DIR, with `broken` tables replaced by their text (null:
## the file is left out).
func _tables_with(broken: Dictionary) -> ItemDB:
	DirAccess.make_dir_recursive_absolute(DATA_DIR)
	for table in ItemDB.TABLES:
		var text := FileAccess.get_file_as_string("%s/%s.json" % [ItemDB.DATA_DIR, table])
		if broken.has(table):
			if broken[table] == null:
				continue
			text = str(broken[table])
		_write_raw("%s/%s.json" % [DATA_DIR, table], text)
	return ItemDB.load_dir(DATA_DIR)


# --- S1: broken tables never touch a save -------------------------------------------------------------


func test_integrity_problem_names_a_broken_missing_or_empty_table() -> void:
	assert_eq(ItemDB.load_default().integrity_problem(), "", "the shipped tables are sound")
	assert_eq(ItemDB.load_default().load_errors, [] as Array[String])
	assert_eq(_tables_with({}).integrity_problem(), "", "an exact copy is sound")
	var torn := _tables_with({"equipment": '{"rules": {"max_slots": 4'})
	assert_eq(torn.load_errors.size(), 1, "one table failed: %s" % [torn.load_errors])
	assert_true(torn.integrity_problem().contains("equipment.json"), torn.integrity_problem())
	assert_true(torn.equipment.is_empty(), "the torn table reads as empty")
	assert_true(_tables_with({"equipment": null}).integrity_problem().contains("equipment.json"), "a missing table")
	assert_true(_tables_with({"shops": "[1, 2]"}).integrity_problem().contains("shops.json"), "not an object")
	var hollow := _tables_with({"equipment": '{"rules": {}, "equipment": []}'})
	assert_eq(hollow.load_errors, [] as Array[String], "it parses")
	assert_ne(hollow.integrity_problem(), "", "but has no equipment rows to judge a bag by")
	assert_ne(ItemDB.from_tables({}).integrity_problem(), "", "no tables at all")
	_done()


## Probe H-P1 with a broken equipment.json: the load keeps all five pieces as saved, every write is
## refused before it touches a file, and the real tables later see the whole bag again.
func test_a_broken_equipment_table_never_repairs_or_overwrites_a_save() -> void:
	var st := _ch6_state()
	var saved_equipment: Variant = _norm(st.equipment)
	assert_eq(SaveSystem.save_to_slot(1, st), OK, "saved with the real tables")
	assert_eq(SaveSystem.save_to_slot(SaveSystem.AUTOSAVE_SLOT, st, SaveSystem.REASON_CHAPTER), OK)
	var slot_text := FileAccess.get_file_as_string(SaveSystem.slot_path(1))
	var auto_text := FileAccess.get_file_as_string(SaveSystem.slot_path(SaveSystem.AUTOSAVE_SLOT))
	SaveSystem._item_db = _tables_with({"equipment": "{ this is not json"})
	assert_ne(SaveSystem.item_tables_problem(), "", "the guard sees the broken table")
	var back := SaveSystem.load_from_slot(1)
	assert_true(back != null, "the save still loads")
	if back == null:
		_done()
		return
	assert_eq(_norm(back.equipment), saved_equipment, "no piece dropped, none taken off, none granted")
	assert_eq(back.chapter, 6)
	var via_dict: GameStateData = SaveSystem.deserialize(JSON.parse_string(slot_text) as Dictionary)
	assert_eq(_norm(via_dict.equipment), saved_equipment, "deserialize is guarded too")
	assert_eq(SaveSystem.save_to_slot(1, back), ERR_UNCONFIGURED, "a manual save is refused")
	assert_eq(SaveSystem.save_to_slot(2, back), ERR_UNCONFIGURED, "even into an empty slot")
	assert_false(SaveSystem.slot_exists(2))
	assert_false(FileAccess.file_exists(SaveSystem.slot_path(1) + SaveSystem.TEMP_SUFFIX), "no temp written")
	assert_eq(SaveSystem.load_into_game(1), OK)
	assert_eq(SaveSystem.autosave(), ERR_UNCONFIGURED, "the autosave is refused")
	assert_eq(FileAccess.get_file_as_string(SaveSystem.slot_path(1)), slot_text, "slot 1 byte for byte")
	assert_eq(
		FileAccess.get_file_as_string(SaveSystem.slot_path(SaveSystem.AUTOSAVE_SLOT)), auto_text, "slot 0 untouched"
	)
	SaveSystem._item_db = null
	assert_eq(SaveSystem.item_tables_problem(), "", "the real tables again")
	var fixed := SaveSystem.load_from_slot(1)
	assert_eq(_norm(fixed.equipment), saved_equipment, "the whole bag, customised spare included")
	var bag := EquipmentBag.new(ItemDB.load_default(), fixed.equipment)
	assert_eq(bag.uids().size(), 5, "rhen 3, asha 2")
	assert_eq(bag.slots_of(3), [&"ember_edge", &"tide_edge"] as Array[StringName], "the customised slots")
	_done()


## The same guard when the table is missing, or parses but holds no equipment.
func test_a_missing_or_hollow_equipment_table_never_drops_a_piece() -> void:
	var st := _ch6_state()
	var saved_equipment: Variant = _norm(st.equipment)
	assert_eq(SaveSystem.save_to_slot(1, st), OK)
	var text := FileAccess.get_file_as_string(SaveSystem.slot_path(1))
	for broken: Variant in [null, '{"rules": {}, "gear_types": [], "equipment": []}']:
		SaveSystem._item_db = _tables_with({"equipment": broken})
		var back := SaveSystem.load_from_slot(1)
		assert_eq(_norm(back.equipment), saved_equipment, "kept as saved (%s)" % [broken])
		assert_eq(SaveSystem.save_to_slot(1, back), ERR_UNCONFIGURED)
		assert_eq(FileAccess.get_file_as_string(SaveSystem.slot_path(1)), text)
	_done()


# --- unknown pieces are kept ----------------------------------------------------------------------------


## Probe H-P2: an unworn spare whose base was renamed, with its abilities, survives a load, a save
## and another load untouched; a worn one comes off but is kept; neither can be equipped.
func test_unknown_pieces_round_trip_untouched() -> void:
	var st := _ch6_state()
	var spare := {"base": "rhen_retired_hooks", "abilities": ["ember_edge", "old_ability"]}
	var worn := {"base": "asha_retired_staff", "abilities": ["clear_mind"]}
	var owned: Dictionary = st.equipment["owned"]
	owned["10"] = spare.duplicate(true)
	owned["11"] = worn.duplicate(true)
	st.equipment["next_uid"] = 12
	(st.equipment["loadout"]["asha"] as Dictionary)["weapon"] = 11
	assert_eq(SaveSystem.save_to_slot(1, st), OK)
	var back := SaveSystem.load_from_slot(1)
	var bag := EquipmentBag.new(ItemDB.load_default(), back.equipment)
	assert_eq(bag.unknown_uids(), [10, 11] as Array[int], "both kept")
	assert_eq(back.equipment["owned"]["10"], spare, "the spare is untouched, abilities included")
	assert_eq(back.equipment["owned"]["11"], worn, "the worn one is untouched")
	assert_eq(bag.wearer_of(11), &"", "but taken off")
	assert_eq(bag.base_of(bag.equipped(&"asha", ItemDB.SLOT_WEAPON)), &"asha_vigil_staff", "asha is armed again")
	assert_eq(bag.equip(&"asha", 11), EquipmentBag.ERR_UNKNOWN_EQUIPMENT, "equipping is refused")
	assert_false(bag.pieces_for(&"rhen", ItemDB.SLOT_WEAPON).has(10), "and it is never offered")
	assert_eq(bag.loadout_problem(), "")
	assert_eq(SaveSystem.save_to_slot(1, back), OK)
	var again := SaveSystem.load_from_slot(1)
	assert_eq(_norm(again.equipment), _norm(back.equipment), "a second round trip changes nothing")
	assert_eq(again.equipment["owned"]["10"], spare)
	_done()


# --- S2: a newer build's slot is copied before a write -------------------------------------------------


func test_a_confirmed_save_over_a_newer_build_slot_keeps_a_numbered_copy() -> void:
	var v99 := JSON.stringify({"version": 99, "state": {"chapter": 9}, "meta": {"saved_at": 1}})
	_write_raw(SaveSystem.slot_path(5), v99)
	assert_eq(SaveSystem.slot_info(5)["status"], SaveSystem.STATUS_NEWER)
	assert_eq(SaveSystem.save_to_slot(5, _ch6_state()), OK, "the player confirmed the overwrite")
	assert_eq(SaveSystem.newer_path(5), SaveSystem.slot_path(5) + SaveSystem.NEWER_SUFFIX)
	assert_eq(FileAccess.get_file_as_string(SaveSystem.newer_path(5)), v99, "the newer run is kept byte for byte")
	assert_eq(SaveSystem.load_from_slot(5).chapter, 6)
	assert_false(FileAccess.file_exists(SaveSystem.corrupt_path(5)), "it is not called corrupt")
	var v100 := JSON.stringify({"version": 100, "state": {}})
	_write_raw(SaveSystem.slot_path(5), v100)
	assert_eq(SaveSystem.save_to_slot(5, _ch6_state()), OK)
	assert_eq(FileAccess.get_file_as_string(SaveSystem.newer_path(5)), v99, "the first copy is never replaced")
	assert_eq(FileAccess.get_file_as_string(SaveSystem.newer_path(5, 2)), v100)
	assert_eq(SaveSystem.free_newer_path(5), SaveSystem.newer_path(5, 3))
	assert_eq(SaveSystem.save_to_slot(5, _ch6_state()), OK)
	assert_false(FileAccess.file_exists(SaveSystem.newer_path(5, 3)), "a readable slot is not copied")
	_done()


func test_a_new_run_autosave_over_a_newer_build_slot_zero_keeps_a_copy() -> void:
	var v99 := JSON.stringify({"version": 99, "state": {"chapter": 9}})
	_write_raw(SaveSystem.slot_path(SaveSystem.AUTOSAVE_SLOT), v99)
	Game.state = _ch6_state()
	SaveSystem._new_run = true
	SaveSystem.request_autosave()
	assert_eq(SaveSystem.poll_pending_autosave(), OK, "New Game confirmed replacing slot 0")
	assert_eq(FileAccess.get_file_as_string(SaveSystem.newer_path(SaveSystem.AUTOSAVE_SLOT)), v99)
	_done()


# --- helpers ---------------------------------------------------------------------------------------------


## A value as it reads back from a save file (JSON numbers are floats).
func _norm(v: Variant) -> Variant:
	return JSON.parse_string(JSON.stringify(v))


func _write_raw(path: String, text: String) -> void:
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(text)
	f.close()


func _done() -> void:
	SaveSystem.cancel_pending_autosave()
	SaveSystem._new_run = false
	SaveSystem._item_db = null
	_clear(TEST_DIR)
	_clear(DATA_DIR)
	SaveSystem.save_dir = _saved_dir
	SaveSystem.clock = _saved_clock
	SaveSystem.autosave_enabled = _saved_enabled
	Game.state = _saved_state
	Game.play_clock_running = _saved_play_clock


func _clear(dir_path: String) -> void:
	if not DirAccess.dir_exists_absolute(dir_path):
		return
	for f in DirAccess.get_files_at(dir_path):
		DirAccess.remove_absolute(dir_path.path_join(f))
	DirAccess.remove_absolute(dir_path)
