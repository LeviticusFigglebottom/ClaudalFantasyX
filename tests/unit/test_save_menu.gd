extends TestCase
## M1-ARC-03: the save/load menu. Slot listing (empty, readable, corrupt, newer), save,
## overwrite confirm, load, refusals, and keyboard/controller input on the real view.
## Fixture slots (save_menu_fixtures.json, including a corrupt slot 3) are written to a test
## folder in user:// and removed afterwards.

const TEST_DIR := "user://test_save_menu"
const NEWER_SLOT := 5
const EMPTY_SLOT := 4

var fx: Dictionary
var _saved_dir := ""
var _saved_clock: Callable
var _saved_autosave := true
var _saved_state: GameStateData
var _menus: Array[SaveMenu] = []


func before_each() -> void:
	_saved_dir = SaveSystem.save_dir
	_saved_clock = SaveSystem.clock
	_saved_autosave = SaveSystem.autosave_enabled
	_saved_state = Game.state
	SaveSystem.autosave_enabled = false
	fx = SaveShrineShot.load_fixtures()
	fx["save_dir"] = TEST_DIR
	SaveShrineShot.write_fixtures(fx)
	SaveSystem.clock = func() -> int: return 1792500000
	Game.state = GameStateData.new()
	Game.state.chapter = 5
	Game.state.location_id = &"ch03/shell_shrine"
	Game.state.play_time_sec = 9000.0


func _model(mode: SaveMenuModel.Mode) -> SaveMenuModel:
	var m := SaveMenuModel.new(mode, SaveSystem, SaveMenuModel.default_slot_ids(6))
	m.refresh()
	m.place_initial_cursor()
	return m


func _index_of(m: SaveMenuModel, slot: int) -> int:
	for i in m.slots.size():
		if m.slots[i].slot == slot:
			return i
	return -1


# --- Listing -------------------------------------------------------------------------------------


func test_lists_autosave_then_manual_slots_with_their_status() -> void:
	var m := _model(SaveMenuModel.Mode.SAVE)
	assert_eq(m.slots.size(), 7, "autosave + 6 manual (save_menu.json)")
	assert_eq(m.slots[0].slot, 0)
	assert_true(m.slots[0].is_autosave())
	var expected: Array[StringName] = [&"ok", &"ok", &"ok", &"corrupt", &"empty", &"empty", &"empty"]
	for i in expected.size():
		assert_eq(m.slots[i].status, expected[i], "slot %d" % i)
	assert_eq(m.slots[1].chapter, 2)
	assert_eq(m.slots[1].location_key, "LOCATION_CH02_HALUNA")
	assert_eq(m.slots[1].play_time_sec, 2534.0)
	assert_eq(m.slots[1].saved_at, 1792411260)
	assert_eq(m.slots[0].reason, "chapter_boundary")
	_done()


func test_corrupt_file_is_reported_not_raised() -> void:
	var info := SaveSystem.slot_info(3)
	assert_eq(info["status"], SaveSystem.STATUS_CORRUPT)
	assert_true(int(info["saved_at"]) > 0, "falls back to the file time")
	assert_eq(SaveSystem.load_from_slot(3), null, "unreadable records never load")
	assert_eq(SaveSystem.load_into_game(3), ERR_FILE_CORRUPT)
	assert_eq(Game.state.chapter, 5, "a failed load leaves the live game alone")
	_done()


func test_wrongly_typed_state_counts_as_corrupt() -> void:
	_write_raw(EMPTY_SLOT, JSON.stringify({"version": 2, "state": {"flags": [], "chapter": "two"}}))
	assert_eq(SaveSystem.slot_info(EMPTY_SLOT)["status"], SaveSystem.STATUS_CORRUPT)
	assert_eq(SaveSystem.load_from_slot(EMPTY_SLOT), null)
	_write_raw(EMPTY_SLOT, "[1, 2, 3]")
	assert_eq(SaveSystem.slot_info(EMPTY_SLOT)["status"], SaveSystem.STATUS_CORRUPT)
	_done()


func test_newer_build_save_is_listed_as_newer() -> void:
	_write_raw(NEWER_SLOT, JSON.stringify({"version": SaveSystem.SAVE_VERSION + 1, "state": {}}))
	var m := _model(SaveMenuModel.Mode.LOAD)
	var i := _index_of(m, NEWER_SLOT)
	assert_eq(m.slots[i].status, SaveSystem.STATUS_NEWER)
	assert_false(m.is_usable(i), "cannot load a newer save")
	m.set_cursor(i)
	assert_eq(m.help_key(), "LOAD_HELP_NEWER")
	_done()


func test_old_versions_list_through_their_migrations() -> void:
	_write_raw(EMPTY_SLOT, JSON.stringify({"version": 0, "coin": 3, "chapter": 1}))
	var info := SaveSystem.slot_info(EMPTY_SLOT)
	assert_eq(info["status"], SaveSystem.STATUS_OK)
	assert_eq(info["chapter"], 1)
	_done()


# --- Saving --------------------------------------------------------------------------------------


func test_save_mode_starts_on_the_first_manual_slot_and_refuses_the_autosave() -> void:
	var m := _model(SaveMenuModel.Mode.SAVE)
	assert_eq(m.cursor, 1, "slot 0 is the autosave")
	m.set_cursor(0)
	assert_eq(m.help_key(), "SAVE_HELP_AUTOSAVE_LOCKED")
	assert_eq(m.accept(), SaveMenuModel.Outcome.REFUSED)
	assert_eq(m.phase, SaveMenuModel.Phase.BROWSE)
	assert_eq(SaveSystem.slot_info(0)["chapter"], 3, "autosave untouched")
	_done()


func test_saving_to_an_empty_slot_writes_at_once() -> void:
	var m := _model(SaveMenuModel.Mode.SAVE)
	m.extra_meta = {"shrine_id": "test_shrine"}
	m.set_cursor(_index_of(m, EMPTY_SLOT))
	assert_eq(m.help_key(), "SAVE_HELP_EMPTY")
	assert_eq(m.accept(), SaveMenuModel.Outcome.SAVED)
	assert_eq(m.phase, SaveMenuModel.Phase.RESULT)
	assert_eq(m.dialog_key, "SAVE_DONE")
	var info := SaveSystem.slot_info(EMPTY_SLOT)
	assert_eq(info["chapter"], 5)
	assert_eq(info["saved_at"], 1792500000)
	var raw: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SaveSystem.slot_path(EMPTY_SLOT)))
	assert_eq((raw["meta"] as Dictionary)["shrine_id"], "test_shrine")
	assert_eq(m.slots[_index_of(m, EMPTY_SLOT)].status, SaveSystem.STATUS_OK, "list refreshed")
	assert_eq(m.accept(), SaveMenuModel.Outcome.CLOSED, "continue closes after a save")
	_done()


func test_overwrite_asks_first_and_keep_it_is_the_default() -> void:
	var m := _model(SaveMenuModel.Mode.SAVE)
	m.set_cursor(_index_of(m, 1))
	assert_eq(m.help_key(), "SAVE_HELP_OVERWRITE")
	assert_eq(m.accept(), SaveMenuModel.Outcome.ASK_OVERWRITE)
	assert_eq(m.phase, SaveMenuModel.Phase.CONFIRM)
	assert_eq(m.dialog_key, "SAVE_CONFIRM_OVERWRITE")
	assert_eq(m.dialog_choices()[m.dialog_cursor], SaveMenuModel.CHOICE_NO)
	assert_eq(m.accept(), SaveMenuModel.Outcome.KEPT)
	assert_eq(m.phase, SaveMenuModel.Phase.BROWSE)
	assert_eq(SaveSystem.slot_info(1)["chapter"], 2, "record kept")
	m.accept()
	assert_eq(m.cancel(), SaveMenuModel.Outcome.KEPT, "cancel also keeps it")
	assert_eq(SaveSystem.slot_info(1)["chapter"], 2)
	_done()


func test_overwrite_yes_replaces_the_record() -> void:
	var m := _model(SaveMenuModel.Mode.SAVE)
	m.set_cursor(_index_of(m, 2))
	m.accept()
	assert_true(m.move(1), "to 'Write over it'")
	assert_eq(m.dialog_choices()[m.dialog_cursor], SaveMenuModel.CHOICE_YES)
	assert_eq(m.accept(), SaveMenuModel.Outcome.SAVED)
	assert_eq(SaveSystem.slot_info(2)["chapter"], 5)
	assert_eq(SaveSystem.slot_info(2)["location_key"], "LOCATION_CH03_SHELL_SHRINE")
	_done()


func test_corrupt_slot_can_be_written_over_after_a_damage_warning() -> void:
	var m := _model(SaveMenuModel.Mode.SAVE)
	m.set_cursor(_index_of(m, 3))
	assert_true(m.is_usable(m.cursor), "saving over damage is allowed")
	assert_eq(m.help_key(), "SAVE_HELP_CORRUPT")
	assert_eq(m.accept(), SaveMenuModel.Outcome.ASK_OVERWRITE)
	assert_eq(m.dialog_key, "SAVE_CONFIRM_OVERWRITE_CORRUPT")
	m.move(1)
	assert_eq(m.accept(), SaveMenuModel.Outcome.SAVED)
	assert_eq(SaveSystem.slot_info(3)["status"], SaveSystem.STATUS_OK, "repaired by the new record")
	_done()


func test_a_failed_write_reports_and_returns_to_the_list() -> void:
	var m := _model(SaveMenuModel.Mode.SAVE)
	var i := _index_of(m, EMPTY_SLOT)
	m.slots[i].slot = SaveSystem.MAX_SLOT + 1
	m.set_cursor(i)
	assert_eq(m.accept(), SaveMenuModel.Outcome.SAVE_FAILED)
	assert_eq(m.dialog_key, "SAVE_FAILED")
	assert_eq(m.accept(), SaveMenuModel.Outcome.NONE)
	assert_eq(m.phase, SaveMenuModel.Phase.BROWSE, "not closed: choose another slot")
	_done()


# --- Loading -------------------------------------------------------------------------------------


func test_load_mode_starts_on_the_newest_record_and_loads_it() -> void:
	var m := _model(SaveMenuModel.Mode.LOAD)
	assert_eq(m.current().slot, 0, "the autosave is the newest fixture")
	assert_eq(m.help_key(), "LOAD_HELP_READY")
	m.set_cursor(_index_of(m, 2))
	assert_eq(m.accept(), SaveMenuModel.Outcome.LOADED)
	assert_eq(m.phase, SaveMenuModel.Phase.CLOSED)
	assert_eq(Game.state.chapter, 3)
	assert_eq(Game.state.location_id, &"ch03/saltgrass_causeway")
	assert_eq(Game.state.play_time_sec, 6385.0)
	_done()


func test_load_mode_refuses_empty_and_corrupt_slots() -> void:
	var m := _model(SaveMenuModel.Mode.LOAD)
	m.set_cursor(_index_of(m, 3))
	assert_eq(m.help_key(), "LOAD_HELP_CORRUPT")
	assert_eq(m.accept(), SaveMenuModel.Outcome.REFUSED)
	m.set_cursor(_index_of(m, EMPTY_SLOT))
	assert_eq(m.help_key(), "LOAD_HELP_EMPTY")
	assert_eq(m.accept(), SaveMenuModel.Outcome.REFUSED)
	assert_eq(Game.state.chapter, 5, "live game untouched")
	_done()


func test_title_entry_continues_from_the_newest_record() -> void:
	assert_true(TitleSaveEntry.can_continue(SaveSystem))
	assert_eq(TitleSaveEntry.continue_slot(SaveSystem), 0)
	assert_eq(TitleSaveEntry.continue_game(SaveSystem), OK)
	assert_eq(Game.state.location_id, &"ch03/shell_shrine")
	SaveShrineShot.clear_fixtures(fx)
	assert_false(TitleSaveEntry.can_continue(SaveSystem), "no records, no Continue")
	assert_eq(TitleSaveEntry.continue_game(SaveSystem), ERR_FILE_NOT_FOUND)
	_done()


func test_cursor_wraps_and_cancel_closes() -> void:
	var m := _model(SaveMenuModel.Mode.SAVE)
	m.set_cursor(0)
	assert_true(m.move(-1))
	assert_eq(m.cursor, 6, "wraps to the last slot")
	assert_true(m.move(1))
	assert_eq(m.cursor, 0)
	assert_eq(m.cancel(), SaveMenuModel.Outcome.CLOSED)
	assert_false(m.move(1), "closed menus ignore input")
	_done()


# --- The view --------------------------------------------------------------------------------------


func test_rows_show_slot_chapter_location_play_time_and_time() -> void:
	var menu := _open(SaveMenuModel.Mode.SAVE)
	var r := menu.rows()
	assert_eq(r.size(), 7)
	assert_eq(r[0].text_of(&"name"), "Autosave")
	assert_eq(r[1].text_of(&"name"), "Record 1")
	assert_eq(r[1].text_of(&"chapter"), "Chapter 2")
	assert_eq(r[1].text_of(&"location"), "Haluna")
	assert_eq(r[1].text_of(&"play_time"), "0:42:14")
	assert_eq(r[1].text_of(&"stamp"), "2026-10-19  12:01")
	assert_eq(r[3].text_of(&"status"), "This record is damaged and cannot be read.")
	assert_eq(r[3].text_of(&"chapter"), "", "no details for a damaged record")
	assert_eq(r[4].text_of(&"status"), "No record")
	assert_eq(menu.help_text(), "Recording here replaces this record.")
	_done()


func test_keyboard_and_controller_actions_drive_the_menu() -> void:
	var menu := _open(SaveMenuModel.Mode.SAVE)
	var tree := menu.get_tree()
	assert_true(tree.paused, "the field is paused under the menu")
	assert_true(menu.handle_input(_action(&"ui_down")))
	assert_eq(menu.model.current().slot, 2)
	assert_true(menu.handle_input(_action(&"ui_accept")))
	assert_eq(menu.dialog_text(), "Write over Record 2?")
	assert_true(menu.handle_input(_action(&"ui_cancel")))
	assert_eq(menu.dialog_text(), "", "dialog closed")
	assert_eq(SaveSystem.slot_info(2)["chapter"], 3, "kept")
	assert_false(menu.handle_input(_action(&"ui_focus_next")), "other actions pass through")
	var outcomes: Array[SaveMenuModel.Outcome] = []
	menu.closed.connect(func(o: SaveMenuModel.Outcome) -> void: outcomes.append(o))
	assert_true(menu.handle_input(_action(&"ui_cancel")))
	assert_eq(outcomes, [SaveMenuModel.Outcome.CLOSED] as Array[SaveMenuModel.Outcome])
	assert_false(menu.is_open())
	assert_false(tree.paused, "unpaused on close")
	assert_false(menu.handle_input(_action(&"ui_accept")), "closed")
	_done()


func test_saving_through_the_view_emits_saved() -> void:
	var menu := _open(SaveMenuModel.Mode.SAVE)
	var slots: Array[int] = []
	menu.saved.connect(func(s: int) -> void: slots.append(s))
	for i in 3:
		menu.handle_input(_action(&"ui_down"))
	assert_eq(menu.model.current().slot, EMPTY_SLOT)
	menu.handle_input(_action(&"ui_accept"))
	assert_eq(slots, [EMPTY_SLOT] as Array[int])
	assert_eq(menu.dialog_text(), "Your journey is recorded.")
	menu.handle_input(_action(&"ui_accept"))
	assert_false(menu.is_open(), "continue closes")
	_done()


func test_load_view_emits_loaded_and_closes() -> void:
	var menu := _open(SaveMenuModel.Mode.LOAD)
	var slots: Array[int] = []
	menu.loaded.connect(func(s: int) -> void: slots.append(s))
	menu.handle_input(_action(&"ui_accept"))
	assert_eq(slots, [0] as Array[int])
	assert_false(menu.is_open())
	assert_eq(Game.state.chapter, 3)
	_done()


func test_layout_fits_the_panel() -> void:
	var d := SaveMenu.load_data()
	var p := d["panel"] as Dictionary
	var r := d["rows"] as Dictionary
	var n := 1 + int(d["manual_slots"])
	var used := (
		float(p["pad"]) * 2.0
		+ float(p["title_height"])
		+ float(p["subtitle_height"])
		+ float(p["gap"]) * 2.0
		+ float(p["help_height"])
		+ (n - 1) * float(r["pitch"])
		+ float(r["height"])
	)
	assert_true(used <= float((p["rect"] as Array)[3]), "rows fit the panel: %s" % used)
	_done()


func _open(mode: SaveMenuModel.Mode) -> SaveMenu:
	var host := (Engine.get_main_loop() as SceneTree).current_scene
	var menu := SaveMenu.open_in(host, mode, {}, "", SaveSystem)
	menu.animate = false
	menu.set_time_zone_bias(0)
	_menus.append(menu)
	return menu


func _action(action: StringName) -> InputEventAction:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	return e


func _write_raw(slot: int, text: String) -> void:
	DirAccess.make_dir_recursive_absolute(SaveSystem.save_dir)
	var f := FileAccess.open(SaveSystem.slot_path(slot), FileAccess.WRITE)
	f.store_string(text)
	f.close()


func _done() -> void:
	for menu in _menus:
		if is_instance_valid(menu):
			var layer := menu.get_parent()
			layer.get_parent().remove_child(layer)
			layer.free()
	_menus.clear()
	SaveShrineShot.clear_fixtures(fx)
	SaveSystem.save_dir = _saved_dir
	SaveSystem.clock = _saved_clock
	SaveSystem.autosave_enabled = _saved_autosave
	Game.state = _saved_state
