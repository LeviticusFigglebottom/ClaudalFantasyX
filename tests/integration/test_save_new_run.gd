extends TestCase
## M1-ARC-08 integration: title -> New Game -> a chapter boundary inside a cutscene -> the
## autosave. Covers the four robustness rules together: New Game asks before a new run can
## replace the previous run's autosave, the boundary is saved only after the cutscene lets go,
## a failed write keeps the previous autosave, and a damaged slot never reaches Continue.

const TEST_DIR := "user://test_save_new_run"
const ZONE := "res://game/levels/_tests/field/field_test.tscn"

var swaps: Array[Array] = []
var wr: WorldReturn
var menu: TitleMenu
var zone: Node3D
var _saved_dir := ""
var _saved_state: GameStateData
var _saved_clock := true
var _saved_enabled := true
var _saved_store: Callable


func before_each() -> void:
	_saved_dir = SaveSystem.save_dir
	_saved_state = Game.state
	_saved_clock = Game.play_clock_running
	_saved_enabled = SaveSystem.autosave_enabled
	_saved_store = SaveSystem.store_text
	SaveSystem.save_dir = TEST_DIR
	SaveSystem.autosave_enabled = true
	SaveSystem.cancel_pending_autosave()
	_clear()
	wr = WorldReturn.new()
	wr.registry = LocationRegistry.load_default()
	wr.change_scene = func(path: String, spawn: StringName) -> void: swaps.append([path, spawn])
	_host().add_child(wr)


## The previous run: chapter 6, autosaved at its last boundary.
func _previous_run() -> void:
	var s := GameStateData.new()
	s.chapter = 6
	s.location_id = &"field_test"
	s.respawn_location_id = &"field_test"
	s.play_time_sec = 9000.0
	assert_eq(SaveSystem.save_to_slot(SaveSystem.AUTOSAVE_SLOT, s, SaveSystem.REASON_CHAPTER), OK)


func _open_title() -> void:
	menu = TitleMenu.new()
	menu.save_system = SaveSystem
	menu.world_return = wr
	_host().add_child(menu)


func _cutscene_director() -> FieldCameraDirector:
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	var director := zone.get_node("CameraDirector") as FieldCameraDirector
	director.auto_update = false
	return director


func _shot() -> CameraShot:
	var shot := CameraShot.new()
	shot.id = &"cutscene_new_run"
	shot.mode = CameraShot.Mode.FIXED
	shot.position = Vector3(4, 1, 6)
	shot.look_at = Vector3(0, 1, 9)
	return shot


func test_a_confirmed_new_run_replaces_the_autosave_only_after_its_first_cutscene() -> void:
	_previous_run()
	_open_title()
	menu.choose(TitleMenuModel.CHOICE_NEW_GAME)
	assert_true(menu.model.confirming, "the previous run's autosave is at risk: ask")
	menu.choose(TitleMenuModel.CHOICE_CONFIRM_BEGIN)
	assert_true(menu.is_launched())
	assert_eq(Game.state.chapter, 0)
	assert_eq(SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT).chapter, 6, "New Game itself writes nothing")
	var director := _cutscene_director()
	director.play_shot(_shot(), 0.0)
	Game.set_chapter(1)
	Game.state.location_id = &"ch02/haluna"
	assert_eq(SaveSystem.poll_pending_autosave(), ERR_BUSY)
	assert_eq(SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT).chapter, 6, "not mid-cutscene")
	director.release(0.0)
	assert_eq(SaveSystem.poll_pending_autosave(), OK)
	var back := SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT)
	assert_eq(back.chapter, 1, "the new run's autosave")
	assert_eq(back.location_id, &"ch02/haluna", "as the cutscene left it")
	assert_eq(TitleSaveEntry.continue_slot(SaveSystem), SaveSystem.AUTOSAVE_SLOT)
	_done()


func test_going_back_keeps_the_previous_run_continuable() -> void:
	_previous_run()
	_open_title()
	menu.choose(TitleMenuModel.CHOICE_NEW_GAME)
	menu.choose(menu.model.accept())
	assert_false(menu.is_launched())
	assert_eq(menu.choose(TitleMenuModel.CHOICE_CONTINUE), OK)
	assert_eq(Game.state.chapter, 6)
	_done()


func test_a_failed_boundary_write_keeps_the_previous_autosave() -> void:
	_previous_run()
	Game.new_game()
	Game.set_chapter(1)
	SaveSystem.store_text = func(f: FileAccess, text: String) -> bool:
		f.store_string(text.substr(0, 16))
		return false
	assert_eq(SaveSystem.poll_pending_autosave(), ERR_FILE_CANT_WRITE)
	SaveSystem.store_text = _saved_store
	assert_eq(SaveSystem.slot_info(SaveSystem.AUTOSAVE_SLOT)["status"], SaveSystem.STATUS_OK)
	assert_eq(SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT).chapter, 6)
	_done()


func test_a_malformed_record_is_skipped_by_continue() -> void:
	_previous_run()
	DirAccess.make_dir_recursive_absolute(TEST_DIR)
	var f := FileAccess.open(SaveSystem.slot_path(1), FileAccess.WRITE)
	f.store_string(JSON.stringify({"version": 4, "state": {"chapter": 9, "party_ids": [5]}}))
	f.close()
	assert_eq(TitleSaveEntry.continue_slot(SaveSystem), SaveSystem.AUTOSAVE_SLOT, "slot 1 is damaged")
	assert_eq(SaveSystem.load_into_game(1), ERR_FILE_CORRUPT)
	_done()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _done() -> void:
	if is_instance_valid(menu):
		menu.get_parent().remove_child(menu)
		menu.free()
	if is_instance_valid(zone):
		zone.get_parent().remove_child(zone)
		zone.free()
	if is_instance_valid(wr):
		wr.free()
	for h in SaveSystem.autosave_holders():
		SaveSystem.release_autosave(h)
	SaveSystem.cancel_pending_autosave()
	SaveSystem.store_text = _saved_store
	_clear()
	SaveSystem.save_dir = _saved_dir
	SaveSystem.autosave_enabled = _saved_enabled
	Game.state = _saved_state
	Game.play_clock_running = _saved_clock
	swaps.clear()


func _clear() -> void:
	var dir := DirAccess.open(TEST_DIR)
	if dir == null:
		return
	for f in dir.get_files():
		DirAccess.remove_absolute(TEST_DIR.path_join(f))
	DirAccess.remove_absolute(TEST_DIR)
