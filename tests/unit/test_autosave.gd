extends TestCase
## M1-ARC-03: the chapter-boundary autosave. Game.set_chapter -> EventBus.chapter_changed ->
## SaveSystem.autosave -> slot 0. Runs against its own user:// folder, removed afterwards.

const TEST_DIR := "user://test_autosave"
const FIXED_TIME := 1792489500

var finished: Array[Array] = []
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
	SaveSystem.clock = func() -> int: return FIXED_TIME
	SaveSystem.autosave_enabled = true
	_clear()
	Game.state = GameStateData.new()
	Game.state.chapter = 2
	Game.state.location_id = &"ch02/haluna"
	EventBus.autosave_finished.connect(_on_finished)


func _on_finished(reason: StringName, error: int) -> void:
	finished.append([reason, error])


func test_autosave_writes_slot_zero_with_its_reason() -> void:
	assert_eq(SaveSystem.autosave(&"test_reason"), OK)
	var info := SaveSystem.slot_info(SaveSystem.AUTOSAVE_SLOT)
	assert_eq(info["status"], SaveSystem.STATUS_OK)
	assert_eq(info["chapter"], 2)
	assert_eq(info["reason"], "test_reason")
	assert_eq(info["saved_at"], FIXED_TIME)
	assert_eq(info["location_key"], "LOCATION_CH02_HALUNA")
	assert_eq(finished, [[&"test_reason", OK]])
	_done()


func test_chapter_change_autosaves_the_new_chapter() -> void:
	assert_true(Game.set_chapter(3))
	assert_true(SaveSystem.slot_exists(SaveSystem.AUTOSAVE_SLOT), "slot 0 written on the boundary")
	var back := SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT)
	assert_eq(back.chapter, 3)
	assert_eq(back.location_id, &"ch02/haluna")
	assert_eq(SaveSystem.slot_info(SaveSystem.AUTOSAVE_SLOT)["reason"], String(SaveSystem.REASON_CHAPTER))
	assert_eq(finished.size(), 1)
	_done()


func test_same_chapter_is_not_a_boundary() -> void:
	assert_false(Game.set_chapter(2))
	assert_false(SaveSystem.slot_exists(SaveSystem.AUTOSAVE_SLOT))
	assert_eq(finished.size(), 0)
	_done()


func test_disabled_autosave_writes_nothing() -> void:
	SaveSystem.autosave_enabled = false
	Game.set_chapter(4)
	assert_false(SaveSystem.slot_exists(SaveSystem.AUTOSAVE_SLOT))
	assert_eq(finished, [[SaveSystem.REASON_CHAPTER, ERR_UNAVAILABLE]])
	_done()


func test_each_boundary_replaces_the_previous_autosave() -> void:
	Game.set_chapter(3)
	Game.set_chapter(4)
	assert_eq(SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT).chapter, 4)
	assert_eq(finished.size(), 2)
	_done()


func test_writes_are_atomic_and_leave_no_temp_file() -> void:
	SaveSystem.autosave()
	SaveSystem.autosave()
	assert_false(FileAccess.file_exists(SaveSystem.slot_path(0) + SaveSystem.TEMP_SUFFIX))
	var files := DirAccess.get_files_at(TEST_DIR)
	assert_eq(files.size(), 1, "only slot_00.json: %s" % [files])
	_done()


func test_meta_never_changes_the_restored_state() -> void:
	Game.state.currency = 41
	SaveSystem.autosave()
	var raw: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SaveSystem.slot_path(0)))
	assert_true(raw.has("meta"))
	assert_eq(int(raw["version"]), SaveSystem.SAVE_VERSION, "no version change for meta")
	assert_false((raw["state"] as Dictionary).has("meta"), "meta sits beside state, not inside")
	assert_eq(SaveSystem.load_from_slot(0).currency, 41)
	_done()


func _done() -> void:
	EventBus.autosave_finished.disconnect(_on_finished)
	_clear()
	SaveSystem.save_dir = _saved_dir
	SaveSystem.clock = _saved_clock
	SaveSystem.autosave_enabled = _saved_enabled
	Game.state = _saved_state


func _clear() -> void:
	var dir := DirAccess.open(TEST_DIR)
	if dir == null:
		return
	for f in dir.get_files():
		DirAccess.remove_absolute(TEST_DIR.path_join(f))
	DirAccess.remove_absolute(TEST_DIR)
