extends TestCase
## M2-UI-26 (input parity): the Status page (StatusMenu, the Menus track's M2-MNU-03) opened from
## the field menu, walked with the keyboard, the controller and the mouse through real InputEvents:
## change the hero (the page follows), back out, and the field menu takes the input again.

var menu: FieldMenu


func before_each() -> void:
	InputDriver.clear_screen()
	menu = null
	UiSettings.set_shared(UiSettings.new())


func test_heroes_and_back_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var who := d.label()
		menu = ParityHost.open_field_menu(GameStateData.new())
		var root := menu.root_page()
		var at := ParityHost.row_of(root, FieldMenuModel.ROW_STATUS)
		ParityHost.choose(d, root, at)
		var page := menu.child as StatusMenu
		assert_true(page != null and page.is_open(), "%s: Status opens" % who)
		assert_eq(page.hero, &"rhen")
		var list := page.list_page()
		ParityHost.move_to(d, list, 1)
		assert_eq(page.hero, &"asha", "%s: the next hero is on show" % who)
		assert_eq(page.shown_page()["name"], tr("CHAR_ASHA"))
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(list.row_node(2))
		else:
			d.press(&"ui_right")
		assert_eq(page.hero, &"toma", "%s: Right (or a click) shows the next" % who)
		if kind != InputDriver.Kind.MOUSE:
			d.press(&"ui_left")
			assert_eq(page.hero, &"asha", "%s: Left shows the one before" % who)
		ParityHost.back(d, page)
		assert_true(menu.child == null and menu.visible, "%s: Cancel closes the page" % who)
		assert_eq(root.cursor, at, "%s: the field menu is on Status" % who)
		var other := ParityHost.row_of(root, FieldMenuModel.ROW_ITEMS)
		ParityHost.move_to(d, root, other)
		assert_eq(root.cursor, other, "%s: the field menu has the input again" % who)
		ParityHost.free_field_menu(menu)
		menu = null
	_done()


func test_the_wheel_steps_the_heroes_from_the_list_and_the_page() -> void:
	var page := StatusMenu.create(PartySheet.new(GameStateData.new(), ParityHost.HEROES))
	page.pause_tree = false
	ParityHost.scene_root().add_child(page)
	InputDriver.wheel(page.list_page().row_node(0), 1)
	assert_eq(page.hero, &"asha", "the wheel over the list")
	ParityHost.wheel_at(page, Vector2(page.size.x - 8.0, page.size.y * 0.5), 1)
	assert_eq(page.hero, &"toma", "the wheel over the hero's page")
	page.get_parent().remove_child(page)
	page.free()
	_done()


func _done() -> void:
	UiSettings.set_shared(null)
