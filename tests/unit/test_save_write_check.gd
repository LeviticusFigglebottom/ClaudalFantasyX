extends TestCase
## M1-ARC-08: a failed write never replaces a good save. SaveSystem.store_text is replaced with a
## writer that fails (or silently writes short), the way a full disk or a quota error would; the
## slot must keep its previous save, the temp file must be gone and game_saved must not fire.

const TEST_DIR := "user://test_save_write_check"

var saved_slots: Array[int] = []
var _saved_dir := ""
var _saved_store: Callable


func before_each() -> void:
	_saved_dir = SaveSystem.save_dir
	_saved_store = SaveSystem.store_text
	SaveSystem.save_dir = TEST_DIR
	_clear()
	EventBus.game_saved.connect(_on_saved)


func _on_saved(slot: int) -> void:
	saved_slots.append(slot)


func _state(chapter: int) -> GameStateData:
	var s := GameStateData.new()
	s.chapter = chapter
	s.currency = chapter * 10
	return s


## Writes the first half of the text and reports failure, like store_string on a full disk.
static func _fail_half(f: FileAccess, text: String) -> bool:
	f.store_string(text.substr(0, text.length() >> 1))
	return false


## Writes the first half and claims success: only the read-back can catch it.
static func _short_but_ok(f: FileAccess, text: String) -> bool:
	f.store_string(text.substr(0, text.length() >> 1))
	return true


func test_a_good_write_still_saves() -> void:
	assert_eq(SaveSystem.save_to_slot(1, _state(2)), OK)
	assert_eq(SaveSystem.load_from_slot(1).chapter, 2)
	assert_eq(saved_slots, [1] as Array[int])
	assert_false(FileAccess.file_exists(SaveSystem.slot_path(1) + SaveSystem.TEMP_SUFFIX))
	_done()


func test_a_reported_write_failure_keeps_the_old_save() -> void:
	assert_eq(SaveSystem.save_to_slot(1, _state(2)), OK)
	var before := FileAccess.get_file_as_string(SaveSystem.slot_path(1))
	SaveSystem.store_text = _fail_half
	assert_eq(SaveSystem.save_to_slot(1, _state(7)), ERR_FILE_CANT_WRITE)
	assert_eq(FileAccess.get_file_as_string(SaveSystem.slot_path(1)), before, "byte for byte the old save")
	assert_eq(SaveSystem.load_from_slot(1).chapter, 2)
	assert_eq(SaveSystem.slot_info(1)["status"], SaveSystem.STATUS_OK)
	assert_false(FileAccess.file_exists(SaveSystem.slot_path(1) + SaveSystem.TEMP_SUFFIX), "temp file removed")
	assert_eq(saved_slots, [1] as Array[int], "no game_saved for the failed write")
	_done()


func test_a_silent_short_write_is_caught_by_the_read_back() -> void:
	assert_eq(SaveSystem.save_to_slot(2, _state(3)), OK)
	SaveSystem.store_text = _short_but_ok
	assert_eq(SaveSystem.save_to_slot(2, _state(8)), ERR_FILE_CANT_WRITE)
	assert_eq(SaveSystem.load_from_slot(2).chapter, 3, "the truncated temp never replaced it")
	assert_false(FileAccess.file_exists(SaveSystem.slot_path(2) + SaveSystem.TEMP_SUFFIX))
	_done()


func test_a_failed_first_write_leaves_the_slot_empty() -> void:
	SaveSystem.store_text = _fail_half
	assert_eq(SaveSystem.save_to_slot(3, _state(1)), ERR_FILE_CANT_WRITE)
	assert_false(SaveSystem.slot_exists(3))
	assert_eq(SaveSystem.slot_info(3)["status"], SaveSystem.STATUS_EMPTY)
	assert_eq(DirAccess.get_files_at(TEST_DIR).size(), 0, "nothing left behind")
	_done()


func test_a_failed_autosave_reports_and_keeps_slot_zero() -> void:
	var saved_state := Game.state
	var saved_enabled := SaveSystem.autosave_enabled
	SaveSystem.autosave_enabled = true
	Game.state = _state(4)
	assert_eq(SaveSystem.autosave(), OK)
	Game.state = _state(5)
	SaveSystem.store_text = _fail_half
	var reports: Array[int] = []
	var on_finished := func(_r: StringName, e: int) -> void: reports.append(e)
	EventBus.autosave_finished.connect(on_finished)
	assert_eq(SaveSystem.autosave(), ERR_FILE_CANT_WRITE)
	EventBus.autosave_finished.disconnect(on_finished)
	assert_eq(reports, [ERR_FILE_CANT_WRITE] as Array[int])
	assert_eq(SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT).chapter, 4)
	Game.state = saved_state
	SaveSystem.autosave_enabled = saved_enabled
	_done()


func test_the_default_writer_is_store_string() -> void:
	var f := FileAccess.open("user://test_save_write_check_probe.txt", FileAccess.WRITE)
	assert_true(bool(SaveSystem.store_text.call(f, "probe")))
	f.close()
	assert_eq(FileAccess.get_file_as_string("user://test_save_write_check_probe.txt"), "probe")
	DirAccess.remove_absolute("user://test_save_write_check_probe.txt")
	_done()


func _done() -> void:
	EventBus.game_saved.disconnect(_on_saved)
	SaveSystem.store_text = _saved_store
	_clear()
	SaveSystem.save_dir = _saved_dir
	saved_slots.clear()


func _clear() -> void:
	var dir := DirAccess.open(TEST_DIR)
	if dir == null:
		return
	for f in dir.get_files():
		DirAccess.remove_absolute(TEST_DIR.path_join(f))
	DirAccess.remove_absolute(TEST_DIR)
