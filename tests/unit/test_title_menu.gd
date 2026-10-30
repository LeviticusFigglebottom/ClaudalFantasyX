extends TestCase
## M1-ARC-06: the minimal title (TitleMenu in boot.tscn) over TitleSaveEntry. Saves go to their
## own user:// folder; the world return records the requested swap instead of changing scene.

const TEST_DIR := "user://test_title_menu"
const BOOT := "res://game/core/boot.tscn"

var swaps: Array[Array] = []
var choices: Array[Array] = []
var wr: WorldReturn
var menu: TitleMenu
var reg: LocationRegistry
var _saved_dir := ""
var _saved_state: GameStateData
var _saved_clock := true


func before_each() -> void:
	_saved_dir = SaveSystem.save_dir
	_saved_state = Game.state
	_saved_clock = Game.play_clock_running
	SaveSystem.save_dir = TEST_DIR
	_clear()
	Game.state = GameStateData.new()
	Game.start_play_clock()
	reg = LocationRegistry.load_default()
	wr = WorldReturn.new()
	wr.registry = reg
	wr.change_scene = func(path: String, spawn: StringName) -> void: swaps.append([path, spawn])
	_host().add_child(wr)


func _open() -> TitleMenu:
	menu = TitleMenu.new()
	menu.save_system = SaveSystem
	menu.world_return = wr
	menu.chosen.connect(func(c: StringName, e: int) -> void: choices.append([c, e]))
	_host().add_child(menu)
	return menu


func _write_record(slot: int, chapter: int) -> void:
	var s := GameStateData.new()
	s.chapter = chapter
	s.location_id = &"field_test"
	s.respawn_location_id = &"field_test"
	s.respawn_spawn = &"Court"
	assert_eq(SaveSystem.save_to_slot(slot, s), OK)


func _action(action: StringName) -> InputEventAction:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	return e


func test_the_title_stops_the_play_clock() -> void:
	_open()
	assert_false(Game.play_clock_running, "time on the title is not play time")
	_done()


func test_without_a_record_only_new_game_is_offered() -> void:
	_open()
	assert_false(menu.model.has_record)
	assert_eq(menu.model.current(), TitleMenuModel.CHOICE_NEW_GAME)
	assert_false(menu.model.is_enabled(TitleMenuModel.CHOICE_CONTINUE))
	assert_false(menu.model.is_enabled(TitleMenuModel.CHOICE_LOAD))
	assert_eq(menu.help_text(), tr(TitleMenuModel.HELP_NO_RECORD_KEY))
	# M1-UI-10: Settings needs no record; the greyed Load and Continue are skipped on the way.
	assert_true(menu.model.move(1))
	assert_eq(menu.model.current(), TitleMenuModel.CHOICE_SETTINGS, "the greyed Load is skipped")
	assert_true(menu.model.move(1))
	assert_eq(menu.model.current(), TitleMenuModel.CHOICE_NEW_GAME, "and Continue, wrapping round")
	assert_eq(menu.choose(TitleMenuModel.CHOICE_CONTINUE), ERR_UNAVAILABLE)
	assert_eq(menu.choose(&""), ERR_UNAVAILABLE)
	assert_false(menu.is_launched())
	_done()


## M3-HER-1167: the zone each choice enters first, for the title to start its loads while it shows: New Game's
## location, and the newest record's location for Continue (read without loading it); nothing for the other rows.
func test_each_choice_names_the_zone_it_enters_first() -> void:
	_open()
	assert_eq(menu.first_zone_of(TitleMenuModel.CHOICE_NEW_GAME), reg.scene_of(reg.new_game_location))
	assert_eq(menu.first_zone_of(TitleMenuModel.CHOICE_CONTINUE), "", "no record, no Continue zone")
	assert_eq(menu.first_zone_of(TitleMenuModel.CHOICE_SETTINGS), "")
	menu.get_parent().remove_child(menu)
	menu.free()
	_write_record(2, 4)
	_open()
	assert_eq(menu.first_zone_of(TitleMenuModel.CHOICE_CONTINUE), reg.scene_of(&"field_test"))
	assert_eq(Game.state.chapter, 0, "the record was only read, not loaded")
	_done()


func test_new_game_starts_fresh_at_the_data_location() -> void:
	Game.state.chapter = 9
	_open()
	assert_true(menu.handle_input(_action(&"ui_accept")))
	assert_eq(Game.state.chapter, 0, "a fresh state")
	assert_true(Game.play_clock_running, "play time starts with the game")
	var to := reg.resolve(reg.new_game_location, reg.new_game_spawn)
	assert_eq(swaps, [[to["scene"], reg.new_game_spawn]] as Array[Array])
	assert_true(menu.is_launched())
	assert_false(menu.handle_input(_action(&"ui_accept")), "one press, one journey")
	assert_eq(menu.choose(TitleMenuModel.CHOICE_NEW_GAME), ERR_UNAVAILABLE)
	assert_eq(swaps.size(), 1)
	_done()


func test_continue_loads_the_newest_record_and_returns_to_its_respawn() -> void:
	_write_record(2, 4)
	wr.enabled = true
	_open()
	assert_true(menu.model.has_record)
	assert_eq(menu.model.current(), TitleMenuModel.CHOICE_CONTINUE, "the cursor starts on Continue")
	assert_eq(menu.help_text(), tr("TITLE_HELP_CONTINUE"))
	assert_true(menu.model.move(1))
	assert_eq(menu.help_text(), tr("TITLE_HELP_NEW_GAME"))
	assert_true(menu.model.move(-1))
	menu.handle_input(_action(&"ui_accept"))
	assert_eq(choices, [[TitleMenuModel.CHOICE_CONTINUE, OK]] as Array[Array])
	assert_eq(Game.state.chapter, 4)
	assert_true(Game.play_clock_running)
	assert_eq(swaps, [[reg.scene_of(&"field_test"), &"Court"]] as Array[Array], "routed by game_loaded")
	assert_true(menu.is_launched())
	_done()


func test_load_opens_the_load_list_and_cancel_comes_back() -> void:
	_write_record(3, 2)
	_open()
	assert_true(menu.model.set_cursor(TitleMenuModel.CHOICES.find(TitleMenuModel.CHOICE_LOAD)))
	assert_eq(menu.help_text(), tr("TITLE_HELP_LOAD"))
	assert_eq(menu.choose(menu.model.accept()), OK)
	assert_true(menu.is_load_menu_open())
	assert_eq(menu.load_menu.model.mode, SaveMenuModel.Mode.LOAD)
	assert_eq(menu.open_load(), menu.load_menu, "only one list at a time")
	assert_false(menu.handle_input(_action(&"ui_down")), "the list has the input")
	menu.load_menu.handle_input(_action(&"ui_cancel"))
	assert_false(menu.is_load_menu_open())
	assert_false(menu.is_launched())
	assert_false((Engine.get_main_loop() as SceneTree).paused)
	assert_eq(swaps, [] as Array[Array])
	_done()


func test_loading_from_the_list_launches() -> void:
	_write_record(3, 6)
	wr.enabled = true
	_open()
	menu.choose(TitleMenuModel.CHOICE_LOAD)
	menu.load_menu.handle_input(_action(&"ui_accept"))
	assert_eq(Game.state.chapter, 6)
	assert_true(menu.is_launched())
	assert_eq(swaps.size(), 1)
	_done()


func test_a_record_that_breaks_greys_continue_again() -> void:
	_write_record(2, 1)
	_open()
	SaveSystem.delete_slot(2)
	assert_eq(menu.choose(TitleMenuModel.CHOICE_CONTINUE), ERR_FILE_NOT_FOUND)
	assert_false(menu.model.has_record, "refreshed after the failure")
	assert_eq(menu.model.current(), TitleMenuModel.CHOICE_NEW_GAME)
	_done()


func test_new_game_without_a_world_return_reports_it() -> void:
	_open()
	menu.world_return = null
	assert_eq(menu.start_new_game(), ERR_UNCONFIGURED)
	menu.world_return = wr
	wr.registry = LocationRegistry.from_dict({})
	assert_eq(menu.start_new_game(), ERR_DOES_NOT_EXIST)
	assert_false(Game.play_clock_running, "back on the title")
	_done()


func test_new_game_over_an_autosave_asks_first_and_going_back_is_the_default() -> void:
	_write_record(SaveSystem.AUTOSAVE_SLOT, 5)
	_open()
	assert_true(menu.model.needs_new_game_confirm())
	assert_true(menu.model.set_cursor(TitleMenuModel.CHOICES.find(TitleMenuModel.CHOICE_NEW_GAME)))
	assert_true(menu.handle_input(_action(&"ui_accept")))
	assert_true(menu.model.confirming, "asked, not started")
	assert_eq(swaps, [] as Array[Array])
	assert_eq(choices, [] as Array[Array], "no choice is reported until it is answered")
	assert_eq(Game.state.chapter, 0, "the live state is untouched")
	assert_eq(menu.model.current(), TitleMenuModel.CHOICE_CONFIRM_BACK, "Go back is the default")
	assert_eq(menu.help_text(), tr(TitleMenuModel.CONFIRM_HELP_KEY))
	assert_eq(menu.row_labels(), [tr("TITLE_CONFIRM_BACK"), tr("TITLE_CONFIRM_BEGIN")] as Array[String])
	menu.handle_input(_action(&"ui_accept"))
	assert_false(menu.model.confirming)
	assert_eq(menu.model.current(), TitleMenuModel.CHOICE_NEW_GAME, "back on New Game")
	assert_eq(menu.row_labels().size(), TitleMenuModel.CHOICES.size(), "the title rows are back")
	assert_false(menu.is_launched())
	assert_eq(SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT).chapter, 5, "the autosave is kept")
	_done()


func test_cancel_closes_the_new_game_question() -> void:
	_write_record(SaveSystem.AUTOSAVE_SLOT, 5)
	_open()
	menu.choose(TitleMenuModel.CHOICE_NEW_GAME)
	assert_true(menu.model.confirming)
	assert_true(menu.handle_input(_action(&"ui_cancel")))
	assert_false(menu.model.confirming)
	assert_false(menu.handle_input(_action(&"ui_cancel")), "nothing to cancel on the title")
	assert_eq(swaps, [] as Array[Array])
	_done()


func test_begin_anew_starts_the_new_run() -> void:
	_write_record(SaveSystem.AUTOSAVE_SLOT, 5)
	_open()
	menu.choose(TitleMenuModel.CHOICE_NEW_GAME)
	assert_true(menu.model.move(1))
	assert_eq(menu.model.current(), TitleMenuModel.CHOICE_CONFIRM_BEGIN)
	assert_eq(menu.choose(menu.model.accept()), OK)
	assert_true(menu.is_launched())
	assert_eq(choices, [[TitleMenuModel.CHOICE_NEW_GAME, OK]] as Array[Array])
	assert_eq(swaps.size(), 1)
	assert_eq(SaveSystem.load_from_slot(SaveSystem.AUTOSAVE_SLOT).chapter, 5, "not written over by New Game")
	_done()


func test_no_question_without_an_autosave_to_lose() -> void:
	_write_record(2, 3)
	_open()
	assert_false(menu.model.needs_new_game_confirm(), "manual records are never touched by a new run")
	assert_eq(menu.choose(TitleMenuModel.CHOICE_NEW_GAME), OK)
	assert_true(menu.is_launched(), "started at once")
	_done()


func test_a_damaged_autosave_is_not_worth_a_question() -> void:
	DirAccess.make_dir_recursive_absolute(TEST_DIR)
	var f := FileAccess.open(SaveSystem.slot_path(SaveSystem.AUTOSAVE_SLOT), FileAccess.WRITE)
	f.store_string("{broken")
	f.close()
	assert_false(TitleSaveEntry.new_game_overwrites_autosave(SaveSystem))
	f = FileAccess.open(SaveSystem.slot_path(SaveSystem.AUTOSAVE_SLOT), FileAccess.WRITE)
	f.store_string(JSON.stringify({"version": SaveSystem.SAVE_VERSION + 1, "state": {}}))
	f.close()
	assert_true(TitleSaveEntry.new_game_overwrites_autosave(SaveSystem), "a newer build's run is still a run")
	_done()


func test_the_question_rows_are_clickable() -> void:
	_write_record(SaveSystem.AUTOSAVE_SLOT, 5)
	_open()
	menu.choose(TitleMenuModel.CHOICE_NEW_GAME)
	assert_true(menu.model.set_cursor(1))
	assert_false(menu.model.set_cursor(2), "only two rows")
	assert_eq(menu.model.row_cursor(), 1)
	assert_false(menu.model.is_enabled(TitleMenuModel.CHOICE_LOAD), "title rows are inactive meanwhile")
	menu.choose(TitleMenuModel.CHOICE_CONFIRM_BACK)
	assert_false(menu.model.is_enabled(TitleMenuModel.CHOICE_CONFIRM_BEGIN), "and the question's after it")
	_done()


func test_title_strings_are_localized() -> void:
	var keys: Array[String] = [TitleMenuModel.HELP_NO_RECORD_KEY, TitleMenuModel.CONFIRM_HELP_KEY]
	for id in TitleMenuModel.CONFIRM_CHOICES:
		keys.append(str(TitleMenuModel.CONFIRM_LABEL_KEYS[id]))
	for id in TitleMenuModel.CHOICES:
		keys.append(str(TitleMenuModel.LABEL_KEYS[id]))
		keys.append(str(TitleMenuModel.HELP_KEYS[id]))
	for k in keys:
		assert_ne(tr(k), k, "%s has a translation" % k)
	_done()


func test_boot_wires_the_title_and_arms_the_world_return() -> void:
	var state := (load(BOOT) as PackedScene).get_state()
	var names: Array[StringName] = []
	for i in state.get_node_count():
		names.append(state.get_node_name(i))
	assert_true(names.has(&"TitleMenu"), "boot.tscn instances the title menu")
	var boot_script := load("res://game/core/boot.gd") as GDScript
	assert_false(SceneRouter.world_return.enabled)
	boot_script.call(&"arm_world_return")
	assert_true(SceneRouter.world_return.enabled, "loads from the title go to the world")
	SceneRouter.world_return.enabled = false
	_done()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _clear() -> void:
	for slot in SaveSystem.MAX_SLOT + 1:
		if SaveSystem.slot_exists(slot):
			SaveSystem.delete_slot(slot)
	DirAccess.remove_absolute(TEST_DIR)


func _done() -> void:
	if is_instance_valid(menu):
		if menu.is_load_menu_open():
			menu.load_menu.handle_input(_action(&"ui_cancel"))
		menu.get_parent().remove_child(menu)
		menu.free()
	if is_instance_valid(wr):
		wr.free()
	(Engine.get_main_loop() as SceneTree).paused = false
	_clear()
	SaveSystem.save_dir = _saved_dir
	Game.state = _saved_state
	Game.play_clock_running = _saved_clock
	swaps.clear()
	choices.clear()
