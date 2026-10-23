extends TestCase
## M1-ARC-08: the chapter autosave is deferred out of Game.set_chapter. It waits for a safe point:
## no autosave hold (a cutscene), no scene change, the tree not paused. The pending request is
## polled by hand here (SaveSystem._process does it on frames after the request).

const TEST_DIR := "user://test_autosave_deferred"
const ZONE := "res://game/levels/_tests/field/field_test.tscn"

var _saved_dir := ""
var _saved_enabled := true
var _saved_state: GameStateData
var _saved_clock := true


func before_each() -> void:
	_saved_dir = SaveSystem.save_dir
	_saved_enabled = SaveSystem.autosave_enabled
	_saved_state = Game.state
	_saved_clock = Game.play_clock_running
	SaveSystem.save_dir = TEST_DIR
	SaveSystem.autosave_enabled = true
	SaveSystem.cancel_pending_autosave()
	_clear()
	Game.state = GameStateData.new()
	Game.state.location_id = &"ch02/haluna"


func test_set_chapter_only_requests_the_autosave() -> void:
	var writes: Array[StringName] = []
	var on_finished := func(r: StringName, _e: int) -> void: writes.append(r)
	EventBus.autosave_finished.connect(on_finished)
	Game.set_chapter(1)
	assert_eq(writes, [] as Array[StringName], "nothing written inside set_chapter")
	assert_true(SaveSystem.has_pending_autosave())
	assert_true(SaveSystem.is_processing(), "SaveSystem polls on the next frames")
	assert_eq(SaveSystem.poll_pending_autosave(), OK)
	assert_eq(writes, [SaveSystem.REASON_CHAPTER] as Array[StringName])
	assert_false(SaveSystem.has_pending_autosave())
	assert_false(SaveSystem.is_processing(), "idle again")
	EventBus.autosave_finished.disconnect(on_finished)
	_done()


func test_a_cutscene_hold_delays_it_and_the_save_shows_the_end_of_the_cutscene() -> void:
	var cutscene := RefCounted.new()
	SaveSystem.hold_autosave(cutscene)
	Game.set_chapter(3)
	Game.set_flag(&"test_flag", true)
	Game.state.location_id = &"ch03/shell_shrine"
	assert_false(SaveSystem.is_safe_point())
	assert_eq(SaveSystem.poll_pending_autosave(), ERR_BUSY)
	assert_false(SaveSystem.slot_exists(SaveSystem.AUTOSAVE_SLOT), "mid-cutscene: no save")
	SaveSystem.release_autosave(cutscene)
	assert_eq(SaveSystem.poll_pending_autosave(), OK)
	var back := SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT)
	assert_eq(back.chapter, 3)
	assert_eq(back.location_id, &"ch03/shell_shrine", "the zone after the cutscene, not before")
	assert_eq(back.flags.get("test_flag"), true)
	_done()


func test_two_boundaries_inside_one_hold_write_once() -> void:
	var cutscene := RefCounted.new()
	SaveSystem.hold_autosave(cutscene)
	SaveSystem.hold_autosave(cutscene)
	Game.set_chapter(1)
	Game.set_chapter(2)
	SaveSystem.release_autosave(cutscene)
	assert_true(SaveSystem.autosave_holders().is_empty(), "holding twice is one hold")
	var writes := [0]
	var on_finished := func(_r: StringName, _e: int) -> void: writes[0] += 1
	EventBus.autosave_finished.connect(on_finished)
	assert_eq(SaveSystem.poll_pending_autosave(), OK)
	assert_eq(SaveSystem.poll_pending_autosave(), ERR_DOES_NOT_EXIST)
	EventBus.autosave_finished.disconnect(on_finished)
	assert_eq(writes[0], 1)
	assert_eq(SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT).chapter, 2)
	_done()


func test_a_freed_holder_never_blocks() -> void:
	var holder := Node.new()
	SaveSystem.hold_autosave(holder)
	assert_eq(SaveSystem.autosave_holders().size(), 1)
	holder.free()
	assert_true(SaveSystem.autosave_holders().is_empty())
	assert_true(SaveSystem.is_safe_point())
	_done()


func test_a_paused_tree_is_not_a_safe_point() -> void:
	var tree := Engine.get_main_loop() as SceneTree
	Game.set_chapter(2)
	tree.paused = true
	assert_eq(SaveSystem.poll_pending_autosave(), ERR_BUSY, "a menu is open")
	tree.paused = false
	assert_eq(SaveSystem.poll_pending_autosave(), OK)
	_done()


func test_new_game_and_load_drop_a_pending_request() -> void:
	Game.set_chapter(4)
	Game.new_game()
	assert_false(SaveSystem.has_pending_autosave(), "the request was for the previous run")
	Game.set_chapter(1)
	var s := GameStateData.new()
	s.chapter = 7
	assert_eq(SaveSystem.save_to_slot(2, s), OK)
	assert_eq(SaveSystem.load_into_game(2), OK)
	assert_false(SaveSystem.has_pending_autosave(), "the request was for the state that was replaced")
	assert_false(SaveSystem.slot_exists(SaveSystem.AUTOSAVE_SLOT))
	_done()


func test_a_scripted_camera_shot_holds_the_autosave() -> void:
	var zone := (load(ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	var director := zone.get_node("CameraDirector") as FieldCameraDirector
	director.auto_update = false
	var shot := CameraShot.new()
	shot.id = &"cutscene_test"
	shot.mode = CameraShot.Mode.FIXED
	shot.position = Vector3(4, 1, 6)
	shot.look_at = Vector3(0, 1, 9)
	director.play_shot(shot, 0.0)
	assert_true(SaveSystem.autosave_holders().has(director))
	Game.set_chapter(5)
	assert_eq(SaveSystem.poll_pending_autosave(), ERR_BUSY, "the cutscene has the camera")
	director.play_shot(shot, 0.0)
	assert_eq(SaveSystem.autosave_holders().size(), 1, "a chained shot is the same hold")
	director.release(0.0)
	assert_true(SaveSystem.autosave_holders().is_empty())
	assert_eq(SaveSystem.poll_pending_autosave(), OK)
	director.play_shot(shot, 0.0)
	zone.get_parent().remove_child(zone)
	assert_true(SaveSystem.autosave_holders().is_empty(), "unloading the zone releases it")
	zone.free()
	_done()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _done() -> void:
	for h in SaveSystem.autosave_holders():
		SaveSystem.release_autosave(h)
	SaveSystem.cancel_pending_autosave()
	_clear()
	SaveSystem.save_dir = _saved_dir
	SaveSystem.autosave_enabled = _saved_enabled
	Game.state = _saved_state
	Game.play_clock_running = _saved_clock


func _clear() -> void:
	var dir := DirAccess.open(TEST_DIR)
	if dir == null:
		return
	for f in dir.get_files():
		DirAccess.remove_absolute(TEST_DIR.path_join(f))
	DirAccess.remove_absolute(TEST_DIR)
