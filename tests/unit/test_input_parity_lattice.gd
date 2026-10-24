extends TestCase
## M2-UI-26 (input parity): the Lattice page (LatticeMenu, the Menus track's M2-MNU-01) opened from
## the field menu, walked with the keyboard, the controller and the mouse through real InputEvents:
## move the cursor over the board (keys and pad: the arrows; mouse: a click on a node), switch the
## hero (keys: Page Up / Down; pad: the shoulders), open the confirm and step back from it, close,
## and the field menu takes the input again. The mouse also drags the board to pan and turns the
## wheel to zoom.

var menu: FieldMenu


func before_each() -> void:
	menu = null
	UiSettings.set_shared(UiSettings.new())


func test_board_confirm_hero_and_back_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var who := d.label()
		menu = ParityHost.open_field_menu(GameStateData.new())
		var root := menu.root_page()
		var at := ParityHost.row_of(root, FieldMenuModel.ROW_LATTICE)
		ParityHost.choose(d, root, at)
		var page := menu.child as LatticeMenu
		assert_true(page != null and page.is_open(), "%s: the Lattice opens" % who)
		assert_eq(page.cursor, &"rhen_start", "%s: on where the hero stands" % who)
		page.model.traveler().movement_points = 3  # a walk the confirm can offer
		var view := page.board_view()
		if kind == InputDriver.Kind.MOUSE:
			ParityHost.click_at(view, view.screen_point(&"rh_01"))
		else:
			d.press(&"ui_right")
		assert_eq(page.cursor, &"rh_01", "%s: the cursor reaches the next node" % who)
		assert_eq(page.side_texts()[3], page.model.node_title(&"rh_01"), "%s: its words follow" % who)
		if kind == InputDriver.Kind.MOUSE:
			ParityHost.click_at(view, view.screen_point(&"rh_01"))
		else:
			d.press(&"ui_accept")
		assert_true(page.is_confirming(), "%s: Confirm (a second click) asks first" % who)
		var confirm := page.confirm_page()
		ParityHost.move_to(d, confirm, 1)
		assert_eq(confirm.cursor, 1, "%s: the confirm's cursor moves" % who)
		ParityHost.move_to(d, confirm, 0)
		ParityHost.back(d, confirm)
		assert_false(page.is_confirming(), "%s: Cancel steps back from the confirm" % who)
		assert_true(page.is_open(), "%s: and leaves the page open" % who)
		assert_eq(page.model.position(), &"rhen_start", "%s: nothing done" % who)
		if kind == InputDriver.Kind.MOUSE:
			ParityHost.click_at(view, view.screen_point(&"rh_01"))
			ParityHost.choose(d, confirm, 1)
			assert_false(page.is_confirming(), "%s: a click on Not now closes the confirm" % who)
		else:
			d.press(&"ui_page_down")
			assert_eq(page.model.hero(), &"asha", "%s: the next hero" % who)
			assert_eq(page.cursor, &"asha_start")
			d.press(&"ui_page_up")
			assert_eq(page.model.hero(), &"rhen", "%s: and back" % who)
		ParityHost.back(d, page)
		assert_true(menu.child == null and menu.visible, "%s: Cancel closes the page" % who)
		assert_eq(root.cursor, at, "%s: the field menu is on Lattice" % who)
		var other := ParityHost.row_of(root, FieldMenuModel.ROW_STATUS)
		ParityHost.move_to(d, root, other)
		assert_eq(root.cursor, other, "%s: the field menu has the input again" % who)
		ParityHost.free_field_menu(menu)
		menu = null
	_done()


func test_the_pad_has_page_up_and_down() -> void:
	assert_true(InputDriver.has_binding(&"ui_page_up", InputDriver.Kind.PAD), "a shoulder for Page Up")
	assert_true(InputDriver.has_binding(&"ui_page_down", InputDriver.Kind.PAD), "and for Page Down")
	_done()


func test_a_drag_pans_the_board_and_does_not_click() -> void:
	var page := _page()
	var view := page.board_view()
	var before := view.pan
	InputDriver.drag(view, Vector2(-120.0, -90.0))
	assert_true(view.pan.x > before.x and view.pan.y >= before.y, "dragging left pans the board right")
	assert_eq(page.cursor, &"rhen_start", "a drag is not a click")
	assert_false(page.is_confirming(), "and opens nothing")
	var panned := view.pan
	InputDriver.drag(view, Vector2(5000.0, 5000.0))
	assert_true(view.pan.x < panned.x, "a drag the other way pans back")
	var far := view.pan
	InputDriver.drag(view, Vector2(5000.0, 5000.0))
	assert_eq(view.pan, far, "held inside the board's bounds")
	page.handle_input(_ev(&"ui_right"))
	assert_eq(page.cursor, &"rh_01")
	_free(page)
	_done()


func test_the_wheel_zooms_the_board_and_a_click_still_finds_its_node() -> void:
	var page := _page()
	var view := page.board_view()
	assert_eq(view.zoom, 1.0)
	InputDriver.wheel(view, 2)
	assert_true(view.zoom < 1.0, "the wheel down zooms out (an overview)")
	var out := view.zoom
	InputDriver.wheel(view, 50)
	assert_true(view.zoom < out and view.zoom >= view.zoom_min(), "down to a floor")
	InputDriver.wheel(view, -100)
	assert_eq(view.zoom, view.zoom_max(), "up to a ceiling")
	InputDriver.wheel(view, 3)
	ParityHost.click_at(view, view.screen_point(&"rh_01"))
	assert_eq(page.cursor, &"rh_01", "a click lands on the node where it is drawn at this zoom")
	assert_eq(view.node_at(view.screen_point(&"rh_02")), &"rh_02")
	_free(page)
	_done()


func _page() -> LatticeMenu:
	var page := LatticeMenu.create(PartySheet.new(GameStateData.new(), ParityHost.HEROES))
	page.pause_tree = false
	ParityHost.scene_root().add_child(page)
	return page


func _free(page: LatticeMenu) -> void:
	page.close()
	page.get_parent().remove_child(page)
	page.free()


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


func _done() -> void:
	UiSettings.set_shared(null)
