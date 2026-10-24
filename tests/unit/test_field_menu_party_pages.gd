extends TestCase
## M2-MNU-01..04: the field menu's party rows (Items, Equip, Lattice, Status) open their pages
## (FieldSubmenu over a PartySheet of the menu's state) and hand back on Cancel; Quit asks first,
## with Stay under the cursor, and only then returns to the title (FlowRouting.record captures it).
## PartySheet builds a hero the way a live battle does (base, Lattice, gear, then vitals).

const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}
const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]

var menu: FieldMenu


func before_each() -> void:
	menu = null


func _teardown() -> void:
	FlowRouting.record = Callable()
	if menu != null and is_instance_valid(menu):
		menu.close()
		menu.get_parent().remove_child(menu)
		menu.free()
	menu = null


func test_party_rows_are_off_with_nobody_in_the_party_and_say_why() -> void:
	var m := FieldMenuModel.new(GameStateData.new(), [], NAMES)
	for id in FieldMenuModel.PARTY_ROWS:
		assert_false(m.root_rows()[_at(id)]["enabled"], "%s needs a hero" % id)
		assert_eq(m.root_desc(id), tr("FIELD_MENU_NO_HEROES"))
	assert_true(m.root_rows()[_at(FieldMenuModel.ROW_ITEMS)]["enabled"], "the bag needs nobody")
	var full := FieldMenuModel.new(GameStateData.new(), HEROES, NAMES)
	for id in FieldMenuModel.PARTY_ROWS:
		assert_true(full.root_rows()[_at(id)]["enabled"])
		assert_eq(full.root_desc(id), tr(FieldMenuModel.ROOT_DESC_KEYS[id]))
	_teardown()


func test_each_party_row_opens_its_page_and_cancel_hands_back() -> void:
	_open()
	for id: StringName in FieldMenu.CHILD_PAGES:
		_go_to(id)
		menu.accept()
		var page := menu.child
		assert_true(page != null and page.is_open(), "%s opens its page" % id)
		assert_eq(page.get_script(), FieldMenu.CHILD_PAGES[id])
		assert_false(menu.visible, "the field menu steps aside")
		assert_false(menu.handle_input(_ev(&"ui_down")), "the page takes the input")
		assert_true(page.handle_input(_ev(&"ui_cancel")))
		assert_true(menu.child == null, "closed")
		assert_true(menu.visible)
		assert_eq(menu.root_page().current_row()["id"], id, "the cursor is where it was")
	_teardown()


func test_quit_asks_first_with_stay_under_the_cursor() -> void:
	var went: Array = []
	FlowRouting.record = func(args: Array) -> void: went.append(args)
	_open()
	_go_to(FieldMenuModel.ROW_QUIT)
	assert_eq(menu.desc_text(), tr("FIELD_MENU_QUIT_DESC"))
	menu.accept()
	assert_eq(menu.level, FieldMenu.Level.QUIT)
	assert_eq(menu.detail_page().current_row()["id"], FieldMenuModel.QUIT_STAY, "Stay first")
	assert_eq(menu.help_text(), tr("FIELD_MENU_HELP_QUIT"))
	menu.accept()
	assert_eq(menu.level, FieldMenu.Level.ROOT, "Stay goes back")
	assert_true(menu.is_open())
	menu.accept()
	menu.handle_input(_ev(&"ui_cancel"))
	assert_eq(menu.level, FieldMenu.Level.ROOT, "Cancel goes back too")
	assert_true(went.is_empty(), "nothing quit yet")
	menu.accept()
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.desc_text(), tr("FIELD_MENU_QUIT_WARN"), "the line says what is lost")
	menu.accept()
	assert_false(menu.is_open(), "quitting closes the menu")
	assert_eq(went, [[FieldMenu.TITLE_SCENE]], "and returns to the title")
	_teardown()


func test_party_sheet_builds_a_hero_like_a_battle_does() -> void:
	var state := GameStateData.new()
	var sheet := PartySheet.new(state, HEROES)
	var base := sheet.base_combatant(&"rhen")
	var now := sheet.combatant(&"rhen")
	assert_true(base != null and now != null)
	assert_eq(now.max_hp, base.max_hp, "no Lattice, no gear: the base")
	assert_eq(now.hp, now.max_hp, "no saved vitals: full")
	assert_true(sheet.combatant(&"nobody") == null)
	assert_eq(sheet.hero_name(&"rhen"), tr("CHAR_RHEN"))
	var t := sheet.lattice.traveler(&"rhen")
	assert_true(t != null, "every hero stands on the board")
	var gear_uid := sheet.goods.equipment.add_piece(&"rhen_coral_hooks")
	assert_eq(sheet.goods.equipment.equip(&"rhen", gear_uid), EquipmentBag.RESULT_OK)
	var geared := sheet.combatant(&"rhen")
	var bonus := sheet.effects.stat_bonuses(&"rhen")
	assert_eq(geared.strength, base.strength + int(bonus.get(&"strength", 0)), "worn gear counts")
	state.record_vitals(&"rhen", 1, geared.max_hp, geared.mp, geared.max_mp, [], [])
	assert_eq(sheet.combatant(&"rhen").hp, 1, "the saved HP, applied last")
	assert_true(sheet.save_lattice())
	assert_true((state.lattice.get("characters", {}) as Dictionary).has("rhen"), "written back")
	_teardown()


func _open() -> void:
	menu = (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	menu.pause_tree = false
	menu.configure(FieldMenuModel.new(GameStateData.new(), HEROES, NAMES))
	_root().add_child(menu)


func _go_to(id: StringName) -> void:
	menu.root_page().set_cursor(_at(id), false)
	menu._render()


func _at(row: StringName) -> int:
	return FieldMenuModel.ROOT_IDS.find(row)


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
