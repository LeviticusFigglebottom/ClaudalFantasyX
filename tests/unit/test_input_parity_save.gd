extends TestCase
## M2-UI-26 (input parity): the save menu, walked with the keyboard, the controller and the mouse
## through real InputEvents (InputDriver): move over the slots, open the overwrite question on a
## used slot, move its choice, back out of it, then close. Fixture slots in their own folder.

const TEST_DIR := "user://test_input_parity_save"

var fx: Dictionary
var menu: SaveMenu
var _saved_dir := ""
var _saved_clock: Callable
var _saved_autosave := true
var _saved_state: GameStateData


func before_each() -> void:
	InputDriver.clear_screen()
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
	UiSettings.set_shared(UiSettings.new())


func test_browse_question_and_close_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		_open()
		var m := menu.model
		var used := _first_used_after(m.cursor)
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.hover(menu.rows()[used])
			assert_eq(m.cursor, used, "mouse: hover moves the cursor")
			InputDriver.wheel(menu.rows()[used], 1)
			assert_eq(m.cursor, used + 1, "mouse: the wheel steps it")
			InputDriver.wheel(menu.rows()[used + 1], -1)
			InputDriver.click(menu.rows()[used])
		else:
			while m.cursor != used:
				d.press(&"ui_down")
			d.press(&"ui_accept")
		assert_eq(m.phase, SaveMenuModel.Phase.CONFIRM, "%s: a used slot asks first" % d.label())
		assert_eq(m.dialog_cursor, 0, "%s: Keep it is first" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.hover(menu._choices.row_node(1))
		else:
			d.press(&"ui_right")
		assert_eq(m.dialog_cursor, 1, "%s: the choice moves" % d.label())
		_cancel(d)
		assert_eq(m.phase, SaveMenuModel.Phase.BROWSE, "%s: Cancel keeps the record" % d.label())
		_cancel(d)
		assert_false(menu.is_open(), "%s: Cancel closes" % d.label())
		_free()
	_done()


func _first_used_after(from: int) -> int:
	for i in range(from + 1, menu.model.slots.size() - 1):
		if menu.model.slots[i].status == &"ok":
			return i
	return from


func _cancel(d: InputDriver) -> void:
	if d.kind == InputDriver.Kind.MOUSE:
		InputDriver.right_click(menu.rows()[0])
	else:
		d.press(&"ui_cancel")


func _open() -> void:
	var host := (Engine.get_main_loop() as SceneTree).current_scene
	menu = SaveMenu.open_in(host, SaveMenuModel.Mode.SAVE, {}, "", SaveSystem)
	menu.animate = false
	menu.set_time_zone_bias(0)


func _free() -> void:
	if is_instance_valid(menu):
		var layer := menu.get_parent()
		layer.get_parent().remove_child(layer)
		layer.free()


func _done() -> void:
	_free()
	SaveShrineShot.clear_fixtures(fx)
	SaveSystem.save_dir = _saved_dir
	SaveSystem.clock = _saved_clock
	SaveSystem.autosave_enabled = _saved_autosave
	Game.state = _saved_state
	UiSettings.set_shared(null)
