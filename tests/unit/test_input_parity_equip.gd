extends TestCase
## M2-UI-26 (input parity): the Equip page (EquipMenu, the Menus track's M2-MNU-02) opened from the
## field menu, walked with the keyboard, the controller and the mouse through real InputEvents:
## choose a hero, step their gear, change hero, open a slot's pieces, back out level by level, and
## the field menu takes the input again on its Equip row.

var menu: FieldMenu


func before_each() -> void:
	menu = null
	UiSettings.set_shared(UiSettings.new())


func test_heroes_gear_pieces_and_back_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var who := d.label()
		menu = ParityHost.open_field_menu(GameStateData.new())
		var root := menu.root_page()
		var at := ParityHost.row_of(root, FieldMenuModel.ROW_EQUIP)
		ParityHost.choose(d, root, at)
		var page := menu.child as EquipMenu
		assert_true(page != null and page.is_open(), "%s: Equip opens" % who)
		assert_eq(page.level, EquipMenu.Level.HEROES)
		var heroes := page.hero_page()
		ParityHost.move_to(d, heroes, 1)
		assert_eq(page.hero, &"asha", "%s: the gear on show follows the hero cursor" % who)
		ParityHost.choose(d, heroes, 0)
		assert_eq(page.level, EquipMenu.Level.GEAR, "%s: Confirm opens the hero's gear" % who)
		assert_eq(page.hero, &"rhen")
		var gear := page.gear_page()
		assert_true(gear.row_count() >= 2, "%s: slots to walk" % who)
		if kind != InputDriver.Kind.MOUSE:
			d.press(&"ui_right")
			assert_eq(page.hero, &"asha", "%s: Right shows the next hero's gear" % who)
			d.press(&"ui_left")
			assert_eq(page.hero, &"rhen", "%s: Left the one before" % who)
		else:
			InputDriver.click(heroes.row_node(1))
			assert_eq(page.hero, &"asha", "%s: a click on another hero opens theirs" % who)
			assert_eq(page.level, EquipMenu.Level.GEAR)
			InputDriver.click(heroes.row_node(0))
			assert_eq(page.hero, &"rhen")
		var slot := _first_slot(gear)
		assert_true(slot >= 0, "%s: a slot row" % who)
		ParityHost.choose(d, gear, slot)
		assert_eq(page.level, EquipMenu.Level.PIECES, "%s: Confirm on a slot lists its pieces" % who)
		var choice := page.choice_page()
		assert_true(choice.visible and choice.row_count() >= 1)
		ParityHost.back(d, choice)
		assert_eq(page.level, EquipMenu.Level.GEAR, "%s: Cancel goes back to the gear" % who)
		assert_eq(gear.cursor, slot, "%s: on the slot it came from" % who)
		var next := posmod(slot + 1, gear.row_count())
		ParityHost.move_to(d, gear, next)
		assert_eq(gear.cursor, next, "%s: the gear has the input again" % who)
		ParityHost.back(d, gear)
		assert_eq(page.level, EquipMenu.Level.HEROES, "%s: and to the heroes" % who)
		ParityHost.back(d, heroes)
		assert_true(menu.child == null and menu.visible, "%s: Cancel closes the page" % who)
		assert_eq(root.cursor, at, "%s: the field menu is on Equip" % who)
		var other := ParityHost.row_of(root, FieldMenuModel.ROW_ITEMS)
		ParityHost.move_to(d, root, other)
		assert_eq(root.cursor, other, "%s: the field menu has the input again" % who)
		ParityHost.free_field_menu(menu)
		menu = null
	_done()


func _first_slot(gear: MenuPage) -> int:
	for i in gear.row_count():
		if StringName(str(gear.rows[i].get("kind", ""))) == EquipMenuModel.KIND_SLOT:
			return i
	return -1


func _done() -> void:
	UiSettings.set_shared(null)
