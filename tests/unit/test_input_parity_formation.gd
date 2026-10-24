extends TestCase
## M2-UI-26 (input parity): the Formation page (FormationMenu, M2-MNU-07) opened from the field
## menu, walked with the keyboard, the controller and the mouse through real InputEvents: step the
## active line, cross to the reserve, pick a hero, put them back, pick again and trade places with
## a reserve hero (saved), back out, and the field menu takes the input again on its Formation row.

var menu: FieldMenu
var state: GameStateData


func before_each() -> void:
	InputDriver.clear_screen()
	menu = null
	UiSettings.set_shared(UiSettings.new())


func test_pick_swap_and_back_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var who := d.label()
		state = GameStateData.new()
		state.party_ids = [&"rhen", &"asha"] as Array[StringName]
		state.reserve_ids = [&"toma"] as Array[StringName]
		menu = ParityHost.open_field_menu(state)
		var root := menu.root_page()
		var at := ParityHost.row_of(root, FieldMenuModel.ROW_FORMATION)
		ParityHost.choose(d, root, at)
		var page := menu.child as FormationMenu
		assert_true(page != null and page.is_open(), "%s: Formation opens" % who)
		var line := page.list_page(FormationMenuModel.LINE_ACTIVE)
		var reserve := page.list_page(FormationMenuModel.LINE_RESERVE)
		ParityHost.move_to(d, line, 1)
		assert_eq(page.current_hero(), &"asha", "%s: the active line's cursor moves" % who)
		ParityHost.choose(d, line, 1)
		assert_eq(page.chosen, {"line": FormationMenuModel.LINE_ACTIVE, "index": 1}, "%s: Asha is picked" % who)
		ParityHost.back(d, line)
		assert_true(page.chosen.is_empty() and page.is_open(), "%s: Cancel puts her back" % who)
		ParityHost.choose(d, line, 1)
		if kind == InputDriver.Kind.MOUSE:
			ParityHost.hover_away()
			InputDriver.hover(reserve.row_node(0))
		else:
			d.press(&"ui_right")
		assert_eq(page.focus, FormationMenuModel.LINE_RESERVE, "%s: the reserve has the input" % who)
		if kind != InputDriver.Kind.MOUSE:
			assert_eq(reserve.cursor, 1, "%s: on the same row, the reserve's open place" % who)
			var back_words := tr("FORMATION_MENU_PLAN_TO_RESERVE_FMT").format({"name": tr("CHAR_ASHA")})
			assert_eq(page.plan_text(), back_words, "%s: the line says what Confirm would do" % who)
			ParityHost.move_to(d, reserve, 0)
		assert_eq(page.current_hero(), &"toma")
		assert_false(line.is_cursor_shown(), "%s: one cursor at a time" % who)
		ParityHost.choose(d, reserve, 0)
		assert_eq(state.party_ids, [&"rhen", &"toma"] as Array[StringName], "%s: Toma comes in" % who)
		assert_eq(state.reserve_ids, [&"asha"] as Array[StringName], "%s: Asha steps back" % who)
		if kind == InputDriver.Kind.MOUSE:
			ParityHost.hover_away()
			InputDriver.hover(line.row_node(0))
		else:
			d.press(&"ui_left")
		assert_eq(page.focus, FormationMenuModel.LINE_ACTIVE, "%s: back to the active line" % who)
		ParityHost.back(d, page)
		assert_true(menu.child == null and menu.visible, "%s: Cancel closes the page" % who)
		assert_eq(root.cursor, at, "%s: the field menu is on Formation" % who)
		assert_eq(menu.model.heroes, [&"rhen", &"toma", &"asha"] as Array[StringName], "%s: the order follows" % who)
		var other := ParityHost.row_of(root, FieldMenuModel.ROW_STATUS)
		ParityHost.move_to(d, root, other)
		assert_eq(root.cursor, other, "%s: the field menu has the input again" % who)
		ParityHost.free_field_menu(menu)
		menu = null
	_done()


func test_the_wheel_steps_the_lists_from_the_rows_and_the_page() -> void:
	state = GameStateData.new()
	state.party_ids = ParityHost.HEROES.duplicate()
	var page := FormationMenu.create(PartySheet.new(state, ParityHost.HEROES))
	page.pause_tree = false
	ParityHost.scene_root().add_child(page)
	var line := page.list_page(FormationMenuModel.LINE_ACTIVE)
	InputDriver.wheel(line.row_node(0), 1)
	assert_eq(page.current_hero(), &"asha", "the wheel over a row")
	ParityHost.wheel_at(page, Vector2(page.size.x * 0.5, page.size.y - 8.0), 1)
	assert_eq(page.current_hero(), &"toma", "the wheel over the page")
	var reserve := page.list_page(FormationMenuModel.LINE_RESERVE)
	InputDriver.wheel(reserve.row_node(0), 1)
	assert_eq(page.focus, FormationMenuModel.LINE_RESERVE, "the wheel over the other list gives it the input")
	page.get_parent().remove_child(page)
	page.free()
	_done()


func _done() -> void:
	UiSettings.set_shared(null)
