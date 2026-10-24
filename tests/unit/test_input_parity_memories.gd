extends TestCase
## M2-UI-26 (input parity) for the Memories gallery (MemoriesMenu, M3-MNU-02), opened from the
## title's Memories row and walked with the keyboard, the controller and the mouse through real
## InputEvents: open a chapter, move to a memory, back out to the chapters and to the title (which
## takes the input again), open it again and relive a memory (the change to the replay scene is
## recorded, never made).

const TEST_DIR := "user://test_input_parity_memories"
const REMEMBERED: Array[StringName] = [&"prologue_seen", &"ch01_kell_side_scene", &"ch01_hullgnaw_defeated"]

var title: TitleMenu
var changes: Array[Array] = []
var _saved_dir := ""
var _saved_state: GameStateData


func before_each() -> void:
	InputDriver.clear_screen()
	_saved_dir = SaveSystem.save_dir
	_saved_state = Game.state
	SaveSystem.save_dir = TEST_DIR
	UiSettings.set_shared(UiSettings.new())
	Game.state = GameStateData.new()
	for f in REMEMBERED:
		Game.state.flags[String(f)] = true
	changes.clear()
	FlowRouting.record = func(args: Array) -> void: changes.append(args)


func test_open_a_chapter_back_out_and_relive_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var who := d.label()
		changes.clear()
		_open_title()
		var row := title.model.row_ids().find(TitleMenuModel.CHOICE_MEMORIES)
		assert_eq(row, 4, "%s: the Memories row shows" % who)
		ParityHost.choose(d, title._page, row)
		assert_true(title.is_memories_open(), "%s: the gallery opens" % who)
		var menu := title.memories_menu
		var chapters := menu.chapters_page()
		var list := menu.memories_page()
		ParityHost.choose(d, chapters, 1)
		assert_eq(menu.current_chapter(), &"ch01", "%s: Chapter 1" % who)
		assert_eq(menu.column, MemoriesMenu.Column.MEMORIES, "%s: its memories have the input" % who)
		ParityHost.move_to(d, list, 1)
		assert_eq(menu.current_memory(), &"ch01_the_rising", "%s: the cursor moves to The Rising" % who)
		ParityHost.back(d, menu)
		assert_eq(menu.column, MemoriesMenu.Column.CHAPTERS, "%s: Cancel goes back to the chapters" % who)
		assert_true(menu.is_open())
		ParityHost.back(d, menu)
		assert_false(title.is_memories_open(), "%s: Cancel on the chapters closes" % who)
		assert_eq(title.model.current(), TitleMenuModel.CHOICE_MEMORIES, "%s: on the Memories row" % who)
		var settings_at := title.model.row_ids().find(TitleMenuModel.CHOICE_SETTINGS)
		if kind == InputDriver.Kind.MOUSE:
			ParityHost.move_to(d, title._page, settings_at)
		else:
			d.press(&"ui_up")
		assert_eq(title.model.row_cursor(), settings_at, "%s: the title has the input again" % who)
		ParityHost.choose(d, title._page, row)
		menu = title.memories_menu
		assert_true(menu != null and menu.is_open(), "%s: open again" % who)
		ParityHost.choose(d, menu.chapters_page(), 1)
		ParityHost.choose(d, menu.memories_page(), 1)
		assert_eq(changes, [[MemoryReplay.SCENE_PATH]] as Array[Array], "%s: the replay starts" % who)
		assert_eq(MemoryReplay.pending, &"ch01_the_rising", "%s: of The Rising" % who)
		assert_true(menu.is_launched() and title.is_launched(), "%s: nothing else is taken" % who)
		MemoryReplay.pending = &""
		_close_title()
	_done()


func test_the_wheel_steps_the_chapters_and_the_memories() -> void:
	_open_title()
	var menu := title.open_memories()
	var chapters := menu.chapters_page()
	InputDriver.wheel(chapters.row_node(0), 1)
	assert_eq(menu.current_chapter(), &"ch01", "the wheel over a chapter shows the next")
	InputDriver.wheel(menu.memories_page().row_node(0), 1)
	assert_eq(menu.column, MemoriesMenu.Column.MEMORIES, "the wheel over the memories gives them the input")
	assert_eq(menu.current_memory(), &"ch01_the_rising")
	_close_title()
	_done()


func _open_title() -> void:
	title = TitleMenu.new()
	title.save_system = SaveSystem
	ParityHost.scene_root().add_child(title)


func _close_title() -> void:
	if is_instance_valid(title):
		title.get_parent().remove_child(title)
		title.free()
	title = null


func _done() -> void:
	FlowRouting.record = Callable()
	MemoryReplay.pending = &""
	SaveSystem.save_dir = _saved_dir
	Game.state = _saved_state
	UiSettings.set_shared(null)
	(Engine.get_main_loop() as SceneTree).paused = false
