extends TestCase
## M3-MNU-02 (SPEC §6.11): the Memories gallery. The data and MemoriesModel (unlocks from the live
## run and the newest readable save, grouped by chapter, locked ones never listed), MemoriesMenu
## driven by ui_* actions, and the title's Memories row (hidden until a memory is remembered, then
## the fifth row, raising the page so its foot stays put).

const TEST_DIR := "user://test_memories"

var menu: MemoriesMenu
var title: TitleMenu
var played: Array[StringName] = []
var _saved_dir := ""
var _saved_state: GameStateData
var _saved_clock := true


func before_each() -> void:
	InputDriver.clear_screen()
	_saved_dir = SaveSystem.save_dir
	_saved_state = Game.state
	_saved_clock = Game.play_clock_running
	SaveSystem.save_dir = TEST_DIR
	_clear()
	Game.state = GameStateData.new()
	UiSettings.set_shared(UiSettings.new())
	played.clear()
	menu = null
	title = null


func _done() -> void:
	if is_instance_valid(menu) and menu.get_parent() != null:
		menu.get_parent().remove_child(menu)
		menu.free()
	if is_instance_valid(title):
		title.get_parent().remove_child(title)
		title.free()
	MemoryReplay.take_gallery_request()
	_clear()
	SaveSystem.save_dir = _saved_dir
	Game.state = _saved_state
	Game.play_clock_running = _saved_clock
	UiSettings.set_shared(null)
	(Engine.get_main_loop() as SceneTree).paused = false


func _clear() -> void:
	for slot in SaveSystem.MAX_SLOT + 1:
		if SaveSystem.slot_exists(slot):
			SaveSystem.delete_slot(slot)
	DirAccess.remove_absolute(TEST_DIR)


func _host() -> Node:
	return ParityHost.scene_root()


func _record(flags: Array[StringName]) -> GameStateData:
	var s := GameStateData.new()
	for f in flags:
		s.flags[String(f)] = true
	return s


func _model(flags: Array[StringName]) -> MemoriesModel:
	var records: Array[GameStateData] = [_record(flags)]
	return MemoriesModel.new(MemoriesModel.load_data(), records)


func _open(m: MemoriesModel, on: StringName = &"") -> MemoriesMenu:
	menu = MemoriesMenu.create(m, on)
	menu.pause_tree = false
	menu.play_memory = func(id: StringName) -> void: played.append(id)
	_host().add_child(menu)
	return menu


func _ev(action: StringName) -> InputEventAction:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	return e


func _open_title() -> TitleMenu:
	title = TitleMenu.new()
	title.save_system = SaveSystem
	_host().add_child(title)
	return title


# --- Data and model ---------------------------------------------------------------------------


func test_the_act_one_memories_are_in_the_data() -> void:
	var m := MemoriesModel.new(MemoriesModel.load_data())
	assert_eq(m.chapters.size(), 17, "the prologue and Ch1 to Ch16 (M5-A3P-1710: Acts I and II)")
	var ids: Array[StringName] = []
	for row in m.memories:
		ids.append(StringName(str(row["id"])))
		assert_ne(tr(str(row["title_key"])), str(row["title_key"]), "%s has a title" % row["id"])
		assert_true(ResourceLoader.exists(str(row["stage"])), "%s: its stage exists" % row["id"])
	for id: StringName in [
		&"prologue_dead_city",
		&"ch01_kell_stall",
		&"ch01_the_rising",
		&"ch01_going_under",
		&"ch02_girl_on_the_beach",
		&"ch02_pila_granddaughter",
		&"ch03_the_first_verse",
		&"ch03_dock_at_night",
		&"ch04_shell_is_set",
		&"ch05_lanternfall_weir",
		&"ch05_kahre",
		&"ch06_barge",
		&"ch07_tavi",
		&"ch07_after_the_bell",
		&"ch08_binding",
		&"ch08_wall_falls",
		&"ch09_the_ebbing",
		&"ch09_the_road_out",
		&"ch10_farewell_tide",
		&"ch11_nhoa",
		&"ch12_hesk",
		&"ch13_ethren",
		&"ch13_the_pact",
		&"ch14_the_vows",
		&"ch14_first_ripple",
		&"ch15_the_shoal",
		&"ch15_current_song",
		&"ch15_let_me_carry_him",
		&"ch16_the_choir",
		&"ch16_swept_away"
	]:
		assert_true(id in ids, "%s is a memory" % id)
	assert_true(bool(m.memory(&"ch03_dock_at_night").get("night", false)), "the dock is at night (data)")
	for c in m.chapters:
		assert_ne(tr(str(c["name_key"])), str(c["name_key"]))
	_done()


func test_nothing_is_remembered_on_a_fresh_record() -> void:
	var m := _model([])
	assert_false(m.any_unlocked())
	assert_eq(m.chapter_rows(), [] as Array[Dictionary], "no chapter is named yet")
	assert_true(m.record_for(&"prologue_dead_city") == null)
	_done()


func test_unlocks_group_by_chapter_and_count_the_locked_ones() -> void:
	var m := _model([&"prologue_seen", &"ch01_kell_side_scene", &"ch01_hullgnaw_defeated"])
	assert_true(m.any_unlocked())
	var rows := m.chapter_rows()
	assert_eq(rows.size(), 2, "the prologue and Ch1; Ch2 and Ch3 are not named")
	assert_eq(rows[1]["id"], &"ch01")
	assert_eq([rows[1]["found"], rows[1]["total"]], [2, 3])
	var ch1 := m.unlocked_in(&"ch01")
	assert_eq(ch1.size(), 2)
	assert_eq(str(ch1[0]["id"]), "ch01_kell_stall", "file order")
	assert_false(m.is_unlocked(&"ch01_going_under"), "going under is still locked")
	assert_eq(MemoriesModel.count_text(2, 3), "2 of 3")
	assert_eq(MemoriesModel.count_text(2, 3, true), "2 of 3 remembered")
	_done()


func test_the_live_run_and_the_newest_save_both_count() -> void:
	var saved := _record([&"ch02_met_asha"])
	assert_eq(SaveSystem.save_to_slot(1, saved), OK)
	Game.state = _record([&"prologue_seen"])
	var m := MemoriesModel.from_game(SaveSystem)
	assert_eq(m.records.size(), 2, "the live run and the newest save")
	assert_true(m.is_unlocked(&"prologue_dead_city"), "from the live run")
	assert_true(m.is_unlocked(&"ch02_girl_on_the_beach"), "from the save")
	assert_true(m.record_for(&"prologue_dead_city") == Game.state, "a replay plays on the record that saw it")
	assert_false(m.record_for(&"ch02_girl_on_the_beach") == Game.state)
	assert_true(bool(m.record_for(&"ch02_girl_on_the_beach").flags.get("ch02_met_asha", false)))
	assert_false(bool(Game.get_flag(&"ch02_met_asha")), "reading the save loads nothing")
	_done()


# --- The menu ---------------------------------------------------------------------------------


func test_the_menu_lists_remembered_chapters_and_memories_only() -> void:
	_open(_model([&"prologue_seen", &"ch01_kell_side_scene", &"ch01_hullgnaw_defeated", &"ch02_met_asha"]))
	var chapters := menu.chapters_page()
	assert_eq(chapters.row_count(), 3, "Ch3 is not named")
	assert_eq(str(chapters.rows[1]["label"]), tr("MEMORIES_CHAPTER_CH01"))
	assert_eq(str(chapters.rows[1]["right"]), "2 of 3")
	assert_eq(menu.current_chapter(), &"prologue")
	assert_eq(menu.memories_page().row_count(), 1)
	assert_eq(menu.help_text(), tr("MEMORIES_HELP_CHAPTERS"))
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.current_chapter(), &"ch01")
	var list := menu.memories_page()
	assert_eq(list.row_count(), 2, "the locked one is hidden")
	assert_eq(str(list.rows[0]["label"]), tr("MEMORY_CH01_KELL_STALL"))
	assert_eq(list.header_label().text, "2 of 3 remembered")
	assert_eq(menu.current_memory(), &"", "the chapters have the input")
	_done()


func test_keys_open_a_chapter_relive_a_memory_and_back_out() -> void:
	_open(_model([&"prologue_seen", &"ch01_kell_side_scene", &"ch01_hullgnaw_defeated"]))
	menu.handle_input(_ev(&"ui_down"))
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.column, MemoriesMenu.Column.MEMORIES)
	assert_eq(menu.help_text(), tr("MEMORIES_HELP_MEMORIES"))
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.current_memory(), &"ch01_the_rising")
	menu.handle_input(_ev(&"ui_left"))
	assert_eq(menu.column, MemoriesMenu.Column.CHAPTERS, "Left goes back to the chapters")
	menu.handle_input(_ev(&"ui_right"))
	assert_eq(menu.current_memory(), &"ch01_the_rising", "back into the same chapter, where it was")
	menu.handle_input(_ev(&"ui_cancel"))
	assert_true(menu.is_open() and menu.column == MemoriesMenu.Column.CHAPTERS, "Cancel: the chapters")
	menu.handle_input(_ev(&"ui_accept"))
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(played, [&"ch01_the_rising"] as Array[StringName], "Confirm relives it")
	assert_true(menu.is_launched())
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(played.size(), 1, "once")
	_done()


func test_cancel_on_the_chapters_closes() -> void:
	_open(_model([&"prologue_seen"]))
	menu.handle_input(_ev(&"ui_cancel"))
	assert_false(menu.is_open())
	_done()


func test_the_menu_opens_on_the_memory_just_replayed() -> void:
	_open(_model([&"prologue_seen", &"ch01_kell_side_scene", &"ch01_hullgnaw_defeated"]), &"ch01_the_rising")
	assert_eq(menu.current_chapter(), &"ch01")
	assert_eq(menu.current_memory(), &"ch01_the_rising")
	_done()


func test_a_locked_memory_cannot_be_chosen() -> void:
	_open(_model([&"prologue_seen"]))
	assert_false(menu.choose(&"ch03_dock_at_night"))
	assert_eq(played, [] as Array[StringName])
	_done()


# --- The title row ------------------------------------------------------------------------------


func test_the_title_has_no_memories_row_until_one_is_remembered() -> void:
	_open_title()
	assert_false(title.model.has_memories)
	assert_eq(title.model.row_ids(), TitleMenuModel.CHOICES, "the four rows")
	var four_y := title._page.position.y + title._page.size.y
	_host().remove_child(title)
	title.free()
	Game.state = _record([&"prologue_seen"])
	_open_title()
	assert_true(title.model.has_memories)
	var ids := title.model.row_ids()
	assert_eq(ids.size(), 5)
	assert_eq(ids[4], TitleMenuModel.CHOICE_MEMORIES, "after Settings")
	assert_eq(title.row_labels()[4], tr("TITLE_MEMORIES"))
	assert_true(is_equal_approx(title._page.position.y + title._page.size.y, four_y), "the page grew upward")
	assert_eq(title.model.row_ids().find(TitleMenuModel.CHOICE_SETTINGS), 3, "Settings keeps its index")
	_done()


func test_a_saved_record_shows_the_row_too() -> void:
	assert_eq(SaveSystem.save_to_slot(SaveSystem.AUTOSAVE_SLOT, _record([&"ch02_met_asha"])), OK)
	_open_title()
	assert_true(title.model.has_memories, "the newest save remembers the beach")
	_done()


func test_choosing_memories_opens_the_gallery_and_cancel_returns() -> void:
	Game.state = _record([&"prologue_seen"])
	_open_title()
	while title.model.current() != TitleMenuModel.CHOICE_MEMORIES:
		title.handle_input(_ev(&"ui_down"))
	assert_eq(title.help_text(), tr("TITLE_HELP_MEMORIES"))
	title.handle_input(_ev(&"ui_accept"))
	assert_true(title.is_memories_open())
	assert_false(title.handle_input(_ev(&"ui_up")), "the title waits while the gallery is open")
	assert_false((Engine.get_main_loop() as SceneTree).paused, "the title does not pause for it")
	title.memories_menu.handle_input(_ev(&"ui_cancel"))
	assert_false(title.is_memories_open())
	assert_eq(title.model.current(), TitleMenuModel.CHOICE_MEMORIES, "back on the row")
	_done()


func test_title_memories_strings_are_localized() -> void:
	for k: String in [
		str(TitleMenuModel.LABEL_KEYS[TitleMenuModel.CHOICE_MEMORIES]),
		str(TitleMenuModel.HELP_KEYS[TitleMenuModel.CHOICE_MEMORIES]),
		"MEMORIES_TITLE",
		"MEMORIES_HELP_CHAPTERS",
		"MEMORIES_HELP_MEMORIES"
	]:
		assert_ne(tr(k), k, "%s has a translation" % k)
	_done()
