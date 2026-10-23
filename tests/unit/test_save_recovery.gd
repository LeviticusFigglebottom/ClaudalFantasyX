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


# --- M1-ARC-11 (QA review-sweep-F on M1-ARC-10) -------------------------------------------------------


## MUST: after a downgrade, a leftover temp file must never replace a newer build's save.
func test_a_temp_never_recovers_over_a_newer_build_slot() -> void:
	var v99 := JSON.stringify({"version": 99, "state": {"chapter": 9}, "meta": {"saved_at": 1}})
	_write_raw(SaveSystem.slot_path(5), v99)
	assert_eq(SaveSystem.slot_info(5)["status"], SaveSystem.STATUS_NEWER)
	for at: int in [1, T_NEW]:
		_write_temp(5, _state(3, 200.0), at)
		var info := SaveSystem.leftover_temp_info(5)
		assert_eq(info["status"], SaveSystem.STATUS_OK, "the temp file itself is readable (saved_at %d)" % at)
		assert_false(info["recoverable"], "but the slot is a newer build's: never older (saved_at %d)" % at)
		assert_eq(SaveSystem.report_leftover_temps(), [] as Array[int], "not advised at startup")
		assert_eq(SaveSystem.recover_temp(5), ERR_FILE_CORRUPT, "recover_temp refuses")
		assert_eq(FileAccess.get_file_as_string(SaveSystem.slot_path(5)), v99, "the v99 save is untouched")
	_done()


func test_a_temp_of_an_older_save_version_never_recovers_over_a_newer_one() -> void:
	assert_eq(SaveSystem.save_to_slot(1, _state(2, 100.0)), OK)
	var v3 := {"version": 3, "state": {"chapter": 5, "play_time_sec": 900.0}, "meta": {"saved_at": T_NEW}}
	_write_raw(SaveSystem.slot_path(1) + SaveSystem.TEMP_SUFFIX, JSON.stringify(v3))
	var info := SaveSystem.leftover_temp_info(1)
	assert_eq(info["status"], SaveSystem.STATUS_OK, "a v3 temp still reads (it migrates)")
	assert_false(info["recoverable"], "a v4 slot is a newer version than the v3 temp, whatever the time")
	assert_eq(SaveSystem.recover_temp(1), ERR_FILE_CORRUPT)
	assert_eq(SaveSystem.load_from_slot(1).chapter, 2)
	_done()


## review-sweep-F nit: whole-second saved_at; a same-second temp file with at least the slot's
## play time is the later write (two quick saves, then a failed rename).
func test_a_same_second_temp_stays_recoverable() -> void:
	assert_eq(SaveSystem.save_to_slot(1, _state(2, 100.0)), OK)
	_write_temp(1, _state(2, 150.0), T_OLD)
	assert_true(SaveSystem.leftover_temp_info(1)["recoverable"], "same second, more play time")
	_write_temp(1, _state(2, 100.0), T_OLD)
	assert_true(SaveSystem.leftover_temp_info(1)["recoverable"], "same second, same play time (nothing lost)")
	_write_temp(1, _state(2, 50.0), T_OLD)
	assert_false(SaveSystem.leftover_temp_info(1)["recoverable"], "same second, less play time: the older one")
	_write_temp(1, _state(2, 150.0), T_OLD)
	assert_eq(SaveSystem.save_to_slot(1, _state(2, 160.0)), OK)
	assert_true(FileAccess.file_exists(SaveSystem.recovered_path(1)), "set aside, not overwritten")
	_done()


## review-sweep-F nit: a second set-aside must not replace the first.
func test_each_set_aside_gets_its_own_file() -> void:
	assert_eq(SaveSystem.save_to_slot(1, _state(2, 100.0)), OK)
	for chapter: int in [3, 4, 5]:
		_write_temp(1, _state(chapter, 200.0 * chapter), T_NEW + chapter)
		assert_eq(SaveSystem.save_to_slot(1, _state(2, 100.0)), OK)
	assert_eq(SaveSystem.recovered_path(1), SaveSystem.slot_path(1) + SaveSystem.RECOVERED_SUFFIX)
	for n: int in [1, 2, 3]:
		var path := SaveSystem.recovered_path(1, n)
		assert_true(FileAccess.file_exists(path), "copy %d kept" % n)
		var kept := JSON.parse_string(FileAccess.get_file_as_string(path)) as Dictionary
		assert_eq(int((kept["state"] as Dictionary)["chapter"]), n + 2, "copy %d holds its own write" % n)
	assert_eq(SaveSystem.free_recovered_path(1), SaveSystem.recovered_path(1, 4))
	_done()


func test_temp_is_newer_rules() -> void:
	var tmp := {"status": SaveSystem.STATUS_OK, "version": 4, "saved_at": 10, "play_time_sec": 5.0}
	var main := {"status": SaveSystem.STATUS_OK, "version": 4, "saved_at": 9, "play_time_sec": 9.0}
	assert_true(SaveSystem.temp_is_newer(tmp, main), "saved later")
	main["saved_at"] = 11
	assert_false(SaveSystem.temp_is_newer(tmp, main), "saved earlier")
	for status: StringName in [SaveSystem.STATUS_EMPTY, SaveSystem.STATUS_CORRUPT]:
		main["status"] = status
		assert_true(SaveSystem.temp_is_newer(tmp, main), "nothing readable to lose: %s" % status)
	main["status"] = SaveSystem.STATUS_NEWER
	main["saved_at"] = 0
	assert_false(SaveSystem.temp_is_newer(tmp, main), "a newer build's slot is never older")
	_done()


# --- M1-ARC-11 rework (QA review-sweep-G) ------------------------------------------------------------


## A chapter `chapter` save wearing `equipment` (rhen in the party), as a file's text.
func _slot_text(chapter: int, play_sec: float, equipment: Dictionary, saved_at: int) -> String:
	var st := _state(chapter, play_sec)
	st.party_ids = [&"rhen"] as Array[StringName]
	var data := SaveSystem.serialize(st)
	(data["state"] as Dictionary)["equipment"] = equipment
	var meta := SaveSystem.make_meta(st, SaveSystem.REASON_CHAPTER)
	meta["saved_at"] = saved_at
	data["meta"] = meta
	return JSON.stringify(data)


func _renamed_weapon() -> Dictionary:
	return {
		"next_uid": 2, "owned": {"1": {"base": "old_reef_hooks", "abilities": []}}, "loadout": {"rhen": {"weapon": 1}}
	}


## Damaged in a way no table change explains: one piece worn in two slots.
func _worn_twice() -> Dictionary:
	var hooks := {"base": "rhen_salvage_hooks", "abilities": []}
	return {"next_uid": 2, "owned": {"1": hooks}, "loadout": {"rhen": {"weapon": 1, "armor": 1}}}


## B1 probe P1: slot 0 at chapter 7 wears a weapon a later equipment.json renamed. It used to read
## as corrupt, so a chapter 2 autosave replaced it with no copy. Now it loads (the weapon is
## repaired) and the further-along rule keeps it.
func test_b1_a_renamed_weapon_never_lets_an_earlier_autosave_replace_slot_zero() -> void:
	var text := _slot_text(7, 99999.0, _renamed_weapon(), T_OLD)
	_write_raw(SaveSystem.slot_path(SaveSystem.AUTOSAVE_SLOT), text)
	assert_eq(SaveSystem.slot_info(SaveSystem.AUTOSAVE_SLOT)["status"], SaveSystem.STATUS_OK, "repairable, not corrupt")
	assert_true(SaveSystem.autosave_is_further_along(_state(2, 100.0)))
	Game.state = _state(1, 100.0)
	Game.set_chapter(2)
	assert_eq(SaveSystem.poll_pending_autosave(), ERR_ALREADY_EXISTS, "the chapter 2 autosave is skipped")
	assert_eq(FileAccess.get_file_as_string(SaveSystem.slot_path(SaveSystem.AUTOSAVE_SLOT)), text, "slot 0 untouched")
	var back := SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT)
	assert_eq(back.chapter, 7)
	var bag := EquipmentBag.new(ItemDB.load_default(), back.equipment)
	assert_eq(bag.base_of(bag.equipped(&"rhen", ItemDB.SLOT_WEAPON)), &"rhen_salvage_hooks", "rhen is armed again")
	_done()


## B1 probe P3: a chapter 1 temp beside a chapter 9 slot with a renamed weapon is not recoverable.
func test_b1_a_renamed_weapon_never_lets_an_older_temp_recover_over_the_slot() -> void:
	var text := _slot_text(9, 99999.0, _renamed_weapon(), T_NEW)
	_write_raw(SaveSystem.slot_path(1), text)
	_write_temp(1, _state(1, 10.0), T_OLD)
	assert_false(SaveSystem.leftover_temp_info(1)["recoverable"], "the slot reads, and is newer")
	assert_eq(SaveSystem.recover_temp(1), ERR_FILE_CORRUPT)
	assert_eq(FileAccess.get_file_as_string(SaveSystem.slot_path(1)), text, "slot untouched")
	_done()


## B1(b): a slot that really is corrupt is still replaced by the autosave, but moved to a numbered
## .corrupt copy first, every time.
func test_b1_an_autosave_over_a_corrupt_slot_keeps_a_numbered_copy() -> void:
	var first := _slot_text(7, 99999.0, _worn_twice(), T_OLD)
	_write_raw(SaveSystem.slot_path(SaveSystem.AUTOSAVE_SLOT), first)
	assert_eq(SaveSystem.slot_info(SaveSystem.AUTOSAVE_SLOT)["status"], SaveSystem.STATUS_CORRUPT)
	Game.state = _state(1, 100.0)
	Game.set_chapter(2)
	assert_eq(SaveSystem.poll_pending_autosave(), OK, "a corrupt slot 0 is never further along")
	assert_eq(SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT).chapter, 2)
	var aside := SaveSystem.corrupt_path(SaveSystem.AUTOSAVE_SLOT)
	assert_eq(aside, SaveSystem.slot_path(SaveSystem.AUTOSAVE_SLOT) + SaveSystem.CORRUPT_SUFFIX)
	assert_eq(FileAccess.get_file_as_string(aside), first, "the unreadable save is kept byte for byte")
	var second := "{torn"
	_write_raw(SaveSystem.slot_path(SaveSystem.AUTOSAVE_SLOT), second)
	assert_eq(SaveSystem.save_to_slot(SaveSystem.AUTOSAVE_SLOT, _state(3, 200.0), SaveSystem.REASON_CHAPTER), OK)
	assert_eq(FileAccess.get_file_as_string(aside), first, "the first copy is never replaced")
	assert_eq(FileAccess.get_file_as_string(SaveSystem.corrupt_path(SaveSystem.AUTOSAVE_SLOT, 2)), second)
	assert_eq(
		SaveSystem.free_corrupt_path(SaveSystem.AUTOSAVE_SLOT), SaveSystem.corrupt_path(SaveSystem.AUTOSAVE_SLOT, 3)
	)
	assert_eq(SaveSystem.save_to_slot(SaveSystem.AUTOSAVE_SLOT, _state(3, 300.0)), OK)
	assert_false(
		FileAccess.file_exists(SaveSystem.corrupt_path(SaveSystem.AUTOSAVE_SLOT, 3)), "a readable slot is not copied"
	)
	_done()


func test_b1_recover_temp_over_a_corrupt_slot_keeps_a_copy() -> void:
	var text := _slot_text(9, 99999.0, _worn_twice(), T_NEW)
	_write_raw(SaveSystem.slot_path(1), text)
	_write_temp(1, _state(1, 10.0), T_OLD)
	assert_true(SaveSystem.leftover_temp_info(1)["recoverable"], "nothing readable in the slot")
	assert_eq(SaveSystem.recover_temp(1), OK)
	assert_eq(SaveSystem.load_from_slot(1).chapter, 1)
	assert_eq(FileAccess.get_file_as_string(SaveSystem.corrupt_path(1)), text, "the corrupt slot was moved, not lost")
	_done()


func test_an_empty_slot_file_is_replaced_without_a_copy() -> void:
	_write_raw(SaveSystem.slot_path(1), "")
	assert_eq(SaveSystem.save_to_slot(1, _state(2, 100.0)), OK)
	assert_false(FileAccess.file_exists(SaveSystem.corrupt_path(1)), "nothing to keep")
	_done()


## S2 probe P2: a temp file written by a newer build, beside an ordinary slot, is kept and logged,
## then set aside by the next write; never silently overwritten.
func test_a_newer_build_temp_is_set_aside_not_overwritten() -> void:
	assert_eq(SaveSystem.save_to_slot(1, _state(2, 100.0)), OK)
	var v99 := JSON.stringify({"version": 99, "state": {"chapter": 9}, "meta": {"saved_at": 1}})
	_write_raw(SaveSystem.slot_path(1) + SaveSystem.TEMP_SUFFIX, v99)
	var info := SaveSystem.leftover_temp_info(1)
	assert_eq(info["status"], SaveSystem.STATUS_NEWER)
	assert_false(info["recoverable"], "this build cannot restore it")
	assert_true(info["keep"], "but it is kept")
	assert_eq(SaveSystem.kept_leftover_temps(), [1] as Array[int], "logged at startup")
	assert_eq(SaveSystem.report_leftover_temps(), [] as Array[int], "not advised for recover_temp")
	assert_eq(SaveSystem.save_to_slot(1, _state(2, 150.0)), OK)
	assert_eq(FileAccess.get_file_as_string(SaveSystem.recovered_path(1)), v99, "set aside before the write")
	assert_eq(SaveSystem.load_from_slot(1).play_time_sec, 150.0)
	_done()


## A readable temp beside a newer build's slot cannot be compared either: kept too.
func test_a_temp_beside_a_newer_build_slot_is_kept() -> void:
	_write_raw(SaveSystem.slot_path(5), JSON.stringify({"version": 99, "state": {}}))
	_write_temp(5, _state(3, 200.0), T_NEW)
	assert_true(SaveSystem.leftover_temp_info(5)["keep"])
	SaveSystem.clock = func() -> int: return T_NEW
	assert_eq(SaveSystem.save_to_slot(1, _state(2, 100.0)), OK)
	_write_temp(1, _state(1, 50.0), T_OLD)
	assert_false(SaveSystem.leftover_temp_info(1)["keep"], "older than a readable slot: superseded")
	_done()


func test_temp_worth_keeping_rules() -> void:
	var ok_main := {"status": SaveSystem.STATUS_OK, "version": 4, "saved_at": 9, "play_time_sec": 9.0}
	var newer_main := {"status": SaveSystem.STATUS_NEWER, "version": 99, "saved_at": 0, "play_time_sec": 0.0}
	var tmp := {"status": SaveSystem.STATUS_OK, "version": 4, "saved_at": 1, "play_time_sec": 1.0}
	assert_false(SaveSystem.temp_worth_keeping(tmp, ok_main), "older than a readable slot")
	assert_true(SaveSystem.temp_worth_keeping(tmp, newer_main), "cannot compare with a newer build's slot")
	tmp["saved_at"] = 10
	assert_true(SaveSystem.temp_worth_keeping(tmp, ok_main), "recoverable")
	tmp["status"] = SaveSystem.STATUS_NEWER
	assert_true(SaveSystem.temp_worth_keeping(tmp, ok_main), "a newer build's temp")
	tmp["status"] = SaveSystem.STATUS_CORRUPT
	assert_false(SaveSystem.temp_worth_keeping(tmp, ok_main), "a torn write")
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
