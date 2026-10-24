extends TestCase
## M2-UI-26 (input parity): the Settings hub and its pages (Accessibility, Controls), walked with
## the keyboard, the controller and the mouse through real InputEvents (InputDriver).

var s: UiSettings
var hub: SettingsMenu
var made: Array[Node] = []


func before_each() -> void:
	InputDriver.clear_screen()
	s = UiSettings.new()
	UiSettings.set_shared(s)


func test_hub_page_value_and_back_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		_open_hub()
		_go_to_row(d, SettingsMenu.ROW_ACCESSIBILITY)
		_accept_row(d, hub._list, hub._list.cursor)
		assert_true(hub.page is AccessibilityMenu, "%s: Accessibility opens" % d.label())
		var page := hub.page as AccessibilityMenu
		var row := page.model.current()
		var before := page.value_shown(row)
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(page._page.row_node(page.model.cursor))
		else:
			d.press(&"ui_right")
		assert_ne(page.value_shown(row), before, "%s: a click or Right changes the row's value" % d.label())
		var at := page.model.cursor
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.wheel(page._page.row_node(at), 1)
		else:
			d.press(&"ui_down")
		assert_eq(page.model.cursor, at + 1, "%s: one step down, not two" % d.label())
		_cancel(d, page)
		assert_false(hub.is_page_open(), "%s: Cancel closes the page" % d.label())
		assert_true(hub.is_open(), "%s: and only the page" % d.label())
		assert_eq(hub.current(), SettingsMenu.ROW_ACCESSIBILITY, "%s: the hub cursor stayed" % d.label())
		_cancel(d, hub)
		assert_false(hub.is_open(), "%s: Cancel again closes the hub" % d.label())
		_free()
	_done()


func test_controls_listen_and_back_out_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		_open_hub()
		_go_to_row(d, SettingsMenu.ROW_CONTROLS)
		_accept_row(d, hub._list, hub._list.cursor)
		var page := hub.page as ControlsMenu
		assert_true(page != null, "%s: Controls opens" % d.label())
		var action_row := page.model.row_ids().find(&"ui_up")
		page.model.set_cursor(action_row)
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(page._page.row_node(action_row))
		else:
			d.press(&"ui_accept")
		assert_true(page.model.is_listening(), "%s: an action listens" % d.label())
		_cancel(d, page)
		assert_false(page.model.is_listening(), "%s: Cancel stops listening" % d.label())
		assert_true(hub.is_page_open(), "%s: and does not close the page" % d.label())
		_cancel(d, page)
		assert_false(hub.is_page_open(), "%s: Cancel then closes the page" % d.label())
		_free()
	_done()


func _open_hub() -> void:
	hub = SettingsMenu.new()
	hub.ui_settings = s
	hub.save_path = ""
	var vp := SubViewport.new()
	hub.graphics_viewport = vp
	_add(vp)
	_add(hub)


func _go_to_row(d: InputDriver, row: StringName) -> void:
	var target := hub._rows().map(func(r: Dictionary) -> StringName: return StringName(str(r["id"]))).find(row)
	if d.kind == InputDriver.Kind.MOUSE:
		InputDriver.hover(hub._list.row_node(target))
	else:
		for i in 8:
			if hub.current() == row:
				break
			d.press(&"ui_down")
	assert_eq(hub.current(), row, "%s: reached %s" % [d.label(), row])


func _accept_row(d: InputDriver, page: MenuPage, index: int) -> void:
	if d.kind == InputDriver.Kind.MOUSE:
		InputDriver.click(page.row_node(index))
	else:
		d.press(&"ui_accept")


func _cancel(d: InputDriver, over: Control) -> void:
	if d.kind == InputDriver.Kind.MOUSE:
		InputDriver.right_click(over)
	else:
		d.press(&"ui_cancel")


func _add(n: Node) -> void:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	made.append(n)


func _free() -> void:
	for n in made:
		if is_instance_valid(n) and n.get_parent() != null:
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func _done() -> void:
	_free()
	UiSettings.set_shared(null)
