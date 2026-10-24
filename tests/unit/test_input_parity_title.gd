extends TestCase
## M2-UI-26 (input parity): the title screen and its Settings hub, walked with the keyboard, the
## controller and the mouse through real InputEvents (InputDriver).

const TEST_DIR := "user://test_input_parity_title"

var menu: TitleMenu
var _saved_dir := ""


func before_each() -> void:
	_saved_dir = SaveSystem.save_dir
	SaveSystem.save_dir = TEST_DIR
	UiSettings.set_shared(UiSettings.new())


func test_choose_settings_and_back_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		_open()
		var settings_at := menu.model.row_ids().find(TitleMenuModel.CHOICE_SETTINGS)
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.hover(menu._page.row_node(settings_at))
			assert_eq(menu.model.row_cursor(), settings_at, "%s: hover moves the cursor" % d.label())
			InputDriver.click(menu._page.row_node(settings_at))
		else:
			while menu.model.row_cursor() != settings_at:
				var before := menu.model.row_cursor()
				d.press(&"ui_down")
				assert_ne(menu.model.row_cursor(), before, "%s: Down moves" % d.label())
			d.press(&"ui_accept")
		assert_true(menu.is_settings_open(), "%s: Settings opens" % d.label())
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.right_click(menu.settings_menu)
		else:
			d.press(&"ui_cancel")
		assert_false(menu.is_settings_open(), "%s: Cancel backs out" % d.label())
		var at := menu.model.row_cursor()
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.hover(menu._page.row_node(menu.model.row_ids().find(TitleMenuModel.CHOICE_NEW_GAME)))
		else:
			d.press(&"ui_up")
		assert_ne(menu.model.row_cursor(), at, "%s: the title has the input again" % d.label())
		_close()
	_done()


func test_the_wheel_steps_the_title_rows() -> void:
	_open()
	var at := menu.model.row_cursor()
	InputDriver.wheel(menu._page.row_node(at), 1)
	assert_ne(menu.model.row_cursor(), at, "the wheel moves the cursor and the model follows")
	InputDriver.wheel(menu._page.row_node(menu.model.row_cursor()), -1)
	assert_eq(menu.model.row_cursor(), at, "and back")
	_close()
	_done()


func _open() -> void:
	menu = TitleMenu.new()
	menu.save_system = SaveSystem
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(menu)


func _close() -> void:
	if is_instance_valid(menu):
		menu.get_parent().remove_child(menu)
		menu.free()


func _done() -> void:
	SaveSystem.save_dir = _saved_dir
	UiSettings.set_shared(null)
