extends TestCase
## M1-ARC-03: the chapter-boundary autosave. Game.set_chapter -> EventBus.chapter_changed ->
## SaveSystem.request_autosave -> (a later frame, at a safe point) SaveSystem.autosave -> slot 0.
## M1-ARC-08: the write is deferred, so these tests poll the pending request themselves
## (SaveSystem._process does that on real frames). Runs against its own user:// folder.

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
	SaveSystem.cancel_pending_autosave()
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
	assert_false(SaveSystem.slot_exists(SaveSystem.AUTOSAVE_SLOT), "not inside set_chapter")
	assert_true(SaveSystem.has_pending_autosave())
	assert_eq(SaveSystem.poll_pending_autosave(), OK)
	assert_true(SaveSystem.slot_exists(SaveSystem.AUTOSAVE_SLOT), "slot 0 written on the boundary")
	var back := SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT)
	assert_eq(back.chapter, 3)
	assert_eq(back.location_id, &"ch02/haluna")
	assert_eq(SaveSystem.slot_info(SaveSystem.AUTOSAVE_SLOT)["reason"], String(SaveSystem.REASON_CHAPTER))
	assert_eq(finished.size(), 1)
	_done()


func test_same_chapter_is_not_a_boundary() -> void:
	assert_false(Game.set_chapter(2))
	assert_false(SaveSystem.has_pending_autosave())
	assert_eq(SaveSystem.poll_pending_autosave(), ERR_DOES_NOT_EXIST)
	assert_false(SaveSystem.slot_exists(SaveSystem.AUTOSAVE_SLOT))
	assert_eq(finished.size(), 0)
	_done()


func test_disabled_autosave_writes_nothing() -> void:
	SaveSystem.autosave_enabled = false
	Game.set_chapter(4)
	assert_eq(SaveSystem.poll_pending_autosave(), ERR_UNAVAILABLE)
	assert_false(SaveSystem.slot_exists(SaveSystem.AUTOSAVE_SLOT))
	assert_eq(finished, [[SaveSystem.REASON_CHAPTER, ERR_UNAVAILABLE]])
	_done()


func test_each_boundary_replaces_the_previous_autosave() -> void:
	Game.set_chapter(3)
	SaveSystem.poll_pending_autosave()
	Game.set_chapter(4)
	SaveSystem.poll_pending_autosave()
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


## ADR 0121 (the Lead's save pass, 2026-10-30): a chapter autosave continues where the slot says, the zone the
## chapter began in, not at the last shrine (the chapter before). The party, flags and the rest load as they were, and
## Game.state keeps its shrine. A save of another reason keeps its respawn.
func test_a_chapter_autosave_continues_in_the_chapter_s_zone() -> void:
	Game.state.chapter = 4
	Game.state.location_id = &"ch04/haluna_wake"
	Game.state.respawn_location_id = &"ch03/shell_shrine"
	Game.state.respawn_spawn = &"Shrine"
	Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	Game.state.flags = {"ch04_started": true, "ch03_shell_shrine_cleared": true}
	assert_eq(SaveSystem.autosave(SaveSystem.REASON_CHAPTER), OK)
	assert_eq(Game.state.respawn_location_id, &"ch03/shell_shrine", "the game's own state keeps its shrine")
	var back := SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT)
	assert_eq(back.location_id, &"ch04/haluna_wake")
	assert_eq(back.respawn_location_id, &"ch04/haluna_wake", "Continue starts where the chapter began")
	assert_eq(back.party_ids, Game.state.party_ids, "the party as it was")
	assert_eq(back.flags, Game.state.flags, "the flags as they were")
	var reg := LocationRegistry.load_default()
	var wr := WorldReturn.new()
	wr.registry = reg
	assert_eq(str(wr.resolve(back)["scene"]), reg.scene_of(&"ch04/haluna_wake"), "and the slot's label is the truth")
	wr.free()
	assert_eq(SaveSystem.save_to_slot(2, Game.state), OK)
	assert_eq(SaveSystem.load_from_slot(2).respawn_location_id, &"ch03/shell_shrine", "a manual save keeps its respawn")
	_done()


func _done() -> void:
	EventBus.autosave_finished.disconnect(_on_finished)
	SaveSystem.cancel_pending_autosave()
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
