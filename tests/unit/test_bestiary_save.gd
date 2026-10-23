extends TestCase
## M1-CMB-03: the bestiary in saves (save v5). GameStateData carries it, a v4 save migrates to an
## empty log, SaveShape checks its shape, and the data-tables gate's `bestiary` check closes saving
## while enemies.json is torn, missing or empty (ADR 0018 Amendment 5 pattern).

const TEST_DIR := "user://test_bestiary_save"
const DATA_DIR := "user://test_bestiary_save_data"
const T_SAVED := 1792489500
const TORN := &"torn"
const MISSING := &"missing"
const EMPTY := &"empty"
const BREAKS: Array[StringName] = [TORN, MISSING, EMPTY]
const LOG := {"reef_crab": {"read": true, "defeated": 3}, "retired_foe": {"defeated": 1}}

var _saved_dir := ""
var _saved_clock: Callable
var _saved_enabled := true
var _saved_state: GameStateData


func before_each() -> void:
	_saved_dir = SaveSystem.save_dir
	_saved_clock = SaveSystem.clock
	_saved_enabled = SaveSystem.autosave_enabled
	_saved_state = Game.state
	SaveSystem.save_dir = TEST_DIR
	SaveSystem.clock = func() -> int: return T_SAVED
	SaveSystem.autosave_enabled = true
	SaveSystem._health = null
	_clear(TEST_DIR)
	_clear(DATA_DIR)
	Game.state = GameStateData.new()


func test_state_round_trips_the_log_and_keeps_unknown_ids() -> void:
	var st := GameStateData.new()
	st.bestiary = LOG.duplicate(true)
	var d := st.to_dict()
	assert_eq(d["bestiary"], LOG)
	var back := GameStateData.from_dict(_norm(d))
	assert_eq(back.bestiary, LOG, "JSON float counts come back as ints")
	assert_eq(typeof(back.bestiary["reef_crab"]["defeated"]), TYPE_INT)
	assert_eq(GameStateData.from_dict({}).bestiary, {}, "no log: empty")
	_done()


func test_save_and_load_keep_the_log() -> void:
	var st := GameStateData.new()
	st.party_ids = [&"rhen"] as Array[StringName]
	st.bestiary = LOG.duplicate(true)
	assert_eq(SaveSystem.save_to_slot(1, st), OK)
	var raw: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SaveSystem.slot_path(1)))
	assert_eq(int(raw["version"]), SaveSystem.SAVE_VERSION, "v5 or later")
	var back := SaveSystem.load_from_slot(1)
	assert_true(back != null)
	if back != null:
		assert_eq(back.bestiary, LOG)
		assert_true(Bestiary.new(back.bestiary).is_read(&"reef_crab"))
	_done()


func test_a_v4_save_migrates_to_an_empty_log() -> void:
	var v4 := {"version": 4, "state": {"currency": 5, "party_ids": ["rhen"]}}
	var migrated := SaveSystem.migrate(v4)
	assert_eq(int(migrated["version"]), SaveSystem.SAVE_VERSION)
	assert_eq(migrated["state"]["bestiary"], {})
	var kept := SaveSystem._migrate_v4_to_v5({"version": 4, "state": {"bestiary": LOG}})
	assert_eq(kept["state"]["bestiary"], LOG, "an existing log is not replaced")
	var back: GameStateData = SaveSystem.deserialize(v4)
	assert_true(back != null)
	if back != null:
		assert_eq(back.currency, 5)
		assert_eq(back.bestiary, {})
	_done()


func test_shape_rejects_a_malformed_log() -> void:
	assert_eq(SaveShape.problem({"bestiary": LOG}), "")
	assert_eq(SaveShape.problem({"bestiary": {}}), "")
	assert_eq(SaveShape.problem({"bestiary": {"x": {"read": true, "note": "kept"}}}), "", "other keys are ignored")
	var bad := {
		"bestiary: expected a Dictionary": [],
		"bestiary.x: expected a Dictionary": {"x": 1},
		"bestiary.x.read: expected true or false": {"x": {"read": 1}},
		"bestiary.x.defeated: expected a whole number": {"x": {"defeated": -1}},
		"bestiary.y.defeated: expected a whole number": {"y": {"defeated": 1.5}},
		"bestiary.z.defeated: expected a whole number": {"z": {"defeated": "3"}},
	}
	for want: String in bad:
		var got := SaveShape.problem({"bestiary": bad[want]})
		assert_true(got.begins_with(want), "%s (got %s)" % [want, got])
	_write_raw(SaveSystem.slot_path(2), JSON.stringify({"version": 5, "state": {"bestiary": {"x": {"read": "yes"}}}}))
	assert_eq(SaveSystem.load_from_slot(2), null, "a malformed log reads as corrupt")
	_done()


func test_the_gate_checks_enemies_json_for_the_log() -> void:
	assert_true(SaveSystem.data_health().tables().has(DataHealth.BESTIARY))
	assert_eq(SaveSystem.data_health().problem_of(DataHealth.BESTIARY), "", "the shipped enemies.json is sound")
	assert_eq(BattleDB.load_default().enemies_problem(), "")
	var st := GameStateData.new()
	st.bestiary = LOG.duplicate(true)
	assert_eq(SaveSystem.save_to_slot(1, st), OK)
	var slot_text := FileAccess.get_file_as_string(SaveSystem.slot_path(1))
	for how in BREAKS:
		SaveSystem.data_health().battle_db = _battle(how)
		var p := SaveSystem.data_health().problem_of(DataHealth.BESTIARY, st)
		assert_ne(p, "", "%s enemies.json: the bestiary check fails" % how)
		assert_true(SaveSystem.data_tables_problem(st).contains("bestiary: "), "%s: the gate names it" % how)
		var back := SaveSystem.load_from_slot(1)
		assert_true(back != null, "%s: the save still loads" % how)
		if back != null:
			assert_eq(back.bestiary, LOG, "%s: the log is loaded exactly as saved" % how)
			assert_eq(SaveSystem.save_to_slot(1, back), ERR_UNCONFIGURED, "%s: saving is refused" % how)
		assert_eq(FileAccess.get_file_as_string(SaveSystem.slot_path(1)), slot_text, "%s: slot untouched" % how)
		SaveSystem._health = null
		assert_eq(SaveSystem.data_tables_problem(st), "", "%s: mended" % how)
	assert_eq(SaveSystem.save_to_slot(1, SaveSystem.load_from_slot(1)), OK, "saves again once mended")
	_done()


func test_only_a_broken_enemies_table_is_a_bestiary_problem() -> void:
	var raw := {"characters": [{"id": "rhen"}], "statuses": [{"id": "poison"}]}
	var hollow := BattleDB.from_tables(raw)
	assert_eq(hollow.integrity_problem(), "", "characters and statuses are fine")
	assert_eq(hollow.enemies_problem(), "the battle tables list no enemies")
	_done()


# --- helpers -------------------------------------------------------------------------------------


## A copy of the battle tables with enemies.json torn, missing or empty.
func _battle(how: StringName) -> BattleDB:
	var dir := "%s/battle_%s" % [DATA_DIR, how]
	DirAccess.make_dir_recursive_absolute(dir)
	for table in BattleDB.TABLES:
		var text := FileAccess.get_file_as_string("%s/%s.json" % [BattleDB.DATA_DIR, table])
		_write_raw("%s/%s.json" % [dir, table], text)
	var path := dir + "/enemies.json"
	if how == TORN:
		_write_raw(path, '{"enemies": [{"id": "reef_crab"')
	elif how == EMPTY:
		_write_raw(path, '{"enemies": []}')
	else:
		DirAccess.remove_absolute(path)
	return BattleDB.load_dir(dir)


func _norm(v: Variant) -> Variant:
	return JSON.parse_string(JSON.stringify(v))


func _write_raw(path: String, text: String) -> void:
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(text)
	f.close()


func _done() -> void:
	SaveSystem.cancel_pending_autosave()
	SaveSystem._health = null
	_clear(TEST_DIR)
	_clear(DATA_DIR)
	SaveSystem.save_dir = _saved_dir
	SaveSystem.clock = _saved_clock
	SaveSystem.autosave_enabled = _saved_enabled
	Game.state = _saved_state


func _clear(dir_path: String) -> void:
	if not DirAccess.dir_exists_absolute(dir_path):
		return
	for sub in DirAccess.get_directories_at(dir_path):
		_clear(dir_path.path_join(sub))
	for f in DirAccess.get_files_at(dir_path):
		DirAccess.remove_absolute(dir_path.path_join(f))
	DirAccess.remove_absolute(dir_path)
