extends TestCase
## Review-sweep-E save fixes (M1-ARC-08 S4 and nits, M1-ARC-10):
##   - the chapter autosave keeps a further-along autosave (ADR 0018 amendment), except in a run
##     New Game started;
##   - a downward (debug) set_chapter requests no autosave unless autosave_on_chapter_regress;
##   - a valid leftover .tmp is reported, restorable and set aside, never silently discarded;
##   - a failed rename keeps the new save's temp file and warns.

const TEST_DIR := "user://test_save_recovery"
const T_OLD := 1792489500
const T_NEW := 1792490000

var finished: Array[Array] = []
var _saved_dir := ""
var _saved_clock: Callable
var _saved_enabled := true
var _saved_regress := false
var _saved_state: GameStateData
var _saved_play_clock := true


func before_each() -> void:
	_saved_dir = SaveSystem.save_dir
	_saved_clock = SaveSystem.clock
	_saved_enabled = SaveSystem.autosave_enabled
	_saved_regress = SaveSystem.autosave_on_chapter_regress
	_saved_state = Game.state
	_saved_play_clock = Game.play_clock_running
	SaveSystem.save_dir = TEST_DIR
	SaveSystem.clock = func() -> int: return T_OLD
	SaveSystem.autosave_enabled = true
	SaveSystem.autosave_on_chapter_regress = false
	SaveSystem.cancel_pending_autosave()
	SaveSystem._new_run = false
	_clear()
	Game.state = GameStateData.new()
	EventBus.autosave_finished.connect(_on_finished)


func _on_finished(reason: StringName, error: int) -> void:
	finished.append([reason, error])


func _state(chapter: int, play_sec: float) -> GameStateData:
	var s := GameStateData.new()
	s.chapter = chapter
	s.play_time_sec = play_sec
	s.location_id = &"ch02/haluna"
	return s


# --- S4: keep the further-along autosave ----------------------------------------------------------


func test_an_older_record_crossing_a_boundary_keeps_the_further_along_autosave() -> void:
	assert_eq(SaveSystem.save_to_slot(SaveSystem.AUTOSAVE_SLOT, _state(6, 9000.0), SaveSystem.REASON_CHAPTER), OK)
	assert_eq(SaveSystem.save_to_slot(3, _state(2, 3000.0)), OK)
	assert_eq(SaveSystem.load_into_game(3), OK)
	Game.set_chapter(3)
	assert_eq(SaveSystem.poll_pending_autosave(), ERR_ALREADY_EXISTS, "slot 0 got further: keep it")
	assert_eq(SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT).chapter, 6, "the further-along run is intact")
	assert_eq(finished, [[SaveSystem.REASON_CHAPTER, ERR_ALREADY_EXISTS]], "reported, not silent")
	_done()


func test_the_same_chapter_with_more_play_time_is_further_along() -> void:
	assert_eq(SaveSystem.save_to_slot(SaveSystem.AUTOSAVE_SLOT, _state(4, 9000.0), SaveSystem.REASON_CHAPTER), OK)
	Game.state = _state(3, 4000.0)
	Game.set_chapter(4)
	assert_eq(SaveSystem.poll_pending_autosave(), ERR_ALREADY_EXISTS)
	assert_eq(SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT).play_time_sec, 9000.0)
	Game.state = _state(3, 9500.0)
	Game.set_chapter(4)
	assert_eq(SaveSystem.poll_pending_autosave(), OK, "past the old run's play time: this run is further along")
	assert_eq(SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT).play_time_sec, 9500.0)
	_done()


func test_overtaking_the_old_autosave_writes_again() -> void:
	assert_eq(SaveSystem.save_to_slot(SaveSystem.AUTOSAVE_SLOT, _state(3, 9000.0), SaveSystem.REASON_CHAPTER), OK)
	Game.state = _state(3, 100.0)
	Game.set_chapter(4)
	assert_eq(SaveSystem.poll_pending_autosave(), OK, "a later chapter is further along")
	assert_eq(SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT).chapter, 4)
	_done()


func test_a_confirmed_new_run_still_replaces_the_autosave() -> void:
	assert_eq(SaveSystem.save_to_slot(SaveSystem.AUTOSAVE_SLOT, _state(6, 9000.0), SaveSystem.REASON_CHAPTER), OK)
	Game.new_game()
	Game.set_chapter(1)
	assert_eq(SaveSystem.poll_pending_autosave(), OK, "the player confirmed Begin anew (ADR 0018)")
	assert_eq(SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT).chapter, 1)
	assert_false(SaveSystem._new_run, "after its first autosave, the new run is protected like any other")
	_done()


func test_loading_ends_the_new_run_exception() -> void:
	assert_eq(SaveSystem.save_to_slot(SaveSystem.AUTOSAVE_SLOT, _state(6, 9000.0), SaveSystem.REASON_CHAPTER), OK)
	assert_eq(SaveSystem.save_to_slot(3, _state(2, 3000.0)), OK)
	Game.new_game()
	assert_eq(SaveSystem.load_into_game(3), OK)
	Game.set_chapter(3)
	assert_eq(SaveSystem.poll_pending_autosave(), ERR_ALREADY_EXISTS)
	_done()


func test_empty_damaged_and_newer_slot_zero() -> void:
	assert_false(SaveSystem.autosave_is_further_along(_state(1, 0.0)), "empty: nothing to keep")
	_write_raw(SaveSystem.slot_path(SaveSystem.AUTOSAVE_SLOT), "{not json")
	assert_false(SaveSystem.autosave_is_further_along(_state(1, 0.0)), "damaged: nothing to keep")
	_write_raw(SaveSystem.slot_path(SaveSystem.AUTOSAVE_SLOT), JSON.stringify({"version": 999, "state": {}}))
	assert_true(SaveSystem.autosave_is_further_along(_state(1, 0.0)), "a newer build's save: keep it")
	_done()


# --- M1-ARC-10: a downward (debug) set_chapter ------------------------------------------------------


func test_a_downward_set_chapter_requests_no_autosave() -> void:
	Game.state = _state(5, 100.0)
	assert_true(Game.set_chapter(2), "the chapter still moves")
	assert_false(SaveSystem.has_pending_autosave(), "but nothing is written over slot 0")
	assert_eq(Game.state.chapter, 2)
	SaveSystem.autosave_on_chapter_regress = true
	Game.set_chapter(1)
	assert_true(SaveSystem.has_pending_autosave(), "the debug flag allows it")
	assert_eq(SaveSystem.poll_pending_autosave(), OK)
	assert_eq(SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT).chapter, 1)
	_done()


# --- M1-ARC-10: leftover temp files ------------------------------------------------------------------


func test_a_valid_newer_leftover_temp_is_reported_and_recoverable() -> void:
	assert_eq(SaveSystem.save_to_slot(1, _state(2, 100.0)), OK)
	_write_temp(1, _state(3, 200.0), T_NEW)
	var info := SaveSystem.leftover_temp_info(1)
	assert_eq(info["status"], SaveSystem.STATUS_OK)
	assert_eq(info["chapter"], 3)
	assert_true(info["recoverable"], "complete and newer than the slot")
	assert_eq(SaveSystem.report_leftover_temps(), [1] as Array[int], "logged at startup")
	assert_eq(SaveSystem.recover_temp(1), OK)
	assert_eq(SaveSystem.load_from_slot(1).chapter, 3, "the newer write is back")
	assert_true(SaveSystem.leftover_temp_info(1).is_empty(), "and the temp file is gone")
	assert_eq(SaveSystem.recover_temp(1), ERR_FILE_NOT_FOUND)
	_done()


func test_an_older_or_torn_temp_is_not_recoverable() -> void:
	SaveSystem.clock = func() -> int: return T_NEW
	assert_eq(SaveSystem.save_to_slot(1, _state(4, 100.0)), OK)
	_write_temp(1, _state(3, 50.0), T_OLD)
	assert_false(SaveSystem.leftover_temp_info(1)["recoverable"], "older than the slot")
	_write_raw(SaveSystem.slot_path(1) + SaveSystem.TEMP_SUFFIX, '{"version": 4, "sta')
	assert_eq(SaveSystem.leftover_temp_info(1)["status"], SaveSystem.STATUS_CORRUPT, "a torn write")
	assert_eq(SaveSystem.recover_temp(1), ERR_FILE_CORRUPT)
	assert_eq(SaveSystem.report_leftover_temps(), [] as Array[int])
	_done()


func test_a_temp_beside_a_missing_or_corrupt_slot_is_recoverable() -> void:
	_write_temp(2, _state(3, 200.0), T_OLD)
	assert_true(SaveSystem.leftover_temp_info(2)["recoverable"], "no slot at all")
	_write_raw(SaveSystem.slot_path(2), "{broken")
	assert_true(SaveSystem.leftover_temp_info(2)["recoverable"], "a damaged slot")
	_done()


func test_the_next_save_sets_a_recoverable_temp_aside() -> void:
	assert_eq(SaveSystem.save_to_slot(1, _state(2, 100.0)), OK)
	_write_temp(1, _state(3, 200.0), T_NEW)
	assert_eq(SaveSystem.save_to_slot(1, _state(2, 150.0)), OK)
	var aside := SaveSystem.slot_path(1) + SaveSystem.RECOVERED_SUFFIX
	assert_true(FileAccess.file_exists(aside), "never silently discarded")
	var kept := JSON.parse_string(FileAccess.get_file_as_string(aside)) as Dictionary
	assert_eq(int((kept["state"] as Dictionary)["chapter"]), 3)
	assert_eq(SaveSystem.load_from_slot(1).play_time_sec, 150.0, "the new save is written")
	assert_false(FileAccess.file_exists(SaveSystem.slot_path(1) + SaveSystem.TEMP_SUFFIX))
	_done()


func test_a_failed_rename_keeps_the_new_save_for_recovery() -> void:
	# A directory where the slot file should be makes the rename fail.
	DirAccess.make_dir_recursive_absolute(SaveSystem.slot_path(5).path_join("blocker"))
	assert_ne(SaveSystem.save_to_slot(5, _state(2, 100.0)), OK)
	var tmp := SaveSystem.slot_path(5) + SaveSystem.TEMP_SUFFIX
	assert_true(FileAccess.file_exists(tmp), "the checked write is kept")
	var back := JSON.parse_string(FileAccess.get_file_as_string(tmp)) as Dictionary
	assert_eq(int((back["state"] as Dictionary)["chapter"]), 2)
	DirAccess.remove_absolute(SaveSystem.slot_path(5).path_join("blocker"))
	DirAccess.remove_absolute(SaveSystem.slot_path(5))
	assert_true(SaveSystem.leftover_temp_info(5)["recoverable"])
	assert_eq(SaveSystem.recover_temp(5), OK)
	assert_eq(SaveSystem.load_from_slot(5).chapter, 2)
	_done()


# --- helpers ---------------------------------------------------------------------------------------


func _write_temp(slot: int, st: GameStateData, saved_at: int) -> void:
	var data := SaveSystem.serialize(st)
	var meta := SaveSystem.make_meta(st, SaveSystem.REASON_MANUAL)
	meta["saved_at"] = saved_at
	data["meta"] = meta
	_write_raw(SaveSystem.slot_path(slot) + SaveSystem.TEMP_SUFFIX, JSON.stringify(data))


func _write_raw(path: String, text: String) -> void:
	DirAccess.make_dir_recursive_absolute(TEST_DIR)
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(text)
	f.close()


func _done() -> void:
	EventBus.autosave_finished.disconnect(_on_finished)
	SaveSystem.cancel_pending_autosave()
	SaveSystem._new_run = false
	_clear()
	SaveSystem.save_dir = _saved_dir
	SaveSystem.clock = _saved_clock
	SaveSystem.autosave_enabled = _saved_enabled
	SaveSystem.autosave_on_chapter_regress = _saved_regress
	Game.state = _saved_state
	Game.play_clock_running = _saved_play_clock


func _clear() -> void:
	var dir := DirAccess.open(TEST_DIR)
	if dir == null:
		return
	for d in dir.get_directories():
		for f in DirAccess.get_files_at(TEST_DIR.path_join(d)):
			DirAccess.remove_absolute(TEST_DIR.path_join(d).path_join(f))
		for sub in DirAccess.get_directories_at(TEST_DIR.path_join(d)):
			DirAccess.remove_absolute(TEST_DIR.path_join(d).path_join(sub))
		DirAccess.remove_absolute(TEST_DIR.path_join(d))
	for f in dir.get_files():
		DirAccess.remove_absolute(TEST_DIR.path_join(f))
	DirAccess.remove_absolute(TEST_DIR)
