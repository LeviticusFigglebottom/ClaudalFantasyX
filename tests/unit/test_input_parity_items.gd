extends TestCase
## M2-UI-26 (input parity): the Items page (ItemsMenu, the Menus track's M2-MNU-03) opened from the
## field menu, walked with the keyboard, the controller and the mouse through real InputEvents:
## step the bag, change the sort, open the hero picker, use a tonic, back out to the bag and to the
## field menu, which takes the input again on its Items row.

var menu: FieldMenu
var state: GameStateData


func before_each() -> void:
	InputDriver.clear_screen()
	menu = null
	UiSettings.set_shared(UiSettings.new())
	ItemsMenu.session_sort = ItemsMenuModel.SORT_KIND


func test_bag_sort_pick_use_and_back_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var who := d.label()
		state = GameStateData.new()
		state.party_ids = ParityHost.HEROES.duplicate()
		state.inventory = {"salt_tonic": 3, "quiet_tea": 2, "crab_carapace": 7}
		state.party_vitals = {"rhen": {"hp": 100}}
		menu = ParityHost.open_field_menu(state)
		var root := menu.root_page()
		var at := ParityHost.row_of(root, FieldMenuModel.ROW_ITEMS)
		ParityHost.choose(d, root, at)
		var page := menu.child as ItemsMenu
		assert_true(page != null and page.is_open(), "%s: Items opens" % who)
		var bag := page.list_page()
		var tea := ParityHost.row_of(bag, &"quiet_tea")
		ParityHost.move_to(d, bag, tea)
		assert_eq(page.current_item(), &"quiet_tea", "%s: the bag cursor moves" % who)
		assert_eq(page.desc_text(), page.model.desc(&"quiet_tea"), "%s: the item's words follow" % who)
		var sort_before := page.sort_text()
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(page._sort)
		else:
			d.press(&"ui_right")
		assert_ne(page.sort_text(), sort_before, "%s: the sort changes" % who)
		assert_eq(page.current_item(), &"quiet_tea", "%s: on the same item" % who)
		var tonic := ParityHost.row_of(bag, &"salt_tonic")
		ParityHost.choose(d, bag, tonic)
		assert_eq(page.level, ItemsMenu.Level.PICK, "%s: Confirm opens the picker" % who)
		assert_eq(page.item_id, &"salt_tonic")
		var picker := page.picker_page()
		var rhen := ParityHost.row_of(picker, &"rhen")
		ParityHost.choose(d, picker, rhen)
		assert_true(int(state.vitals_of(&"rhen").get("hp", 1 << 20)) > 100, "%s: the tonic heals Rhen" % who)
		assert_eq(page.model.inventory().count(&"salt_tonic"), 2, "%s: one spent" % who)
		assert_eq(page.level, ItemsMenu.Level.PICK, "%s: still picking" % who)
		ParityHost.back(d, picker)
		assert_eq(page.level, ItemsMenu.Level.LIST, "%s: Cancel goes back to the bag" % who)
		assert_eq(page.current_item(), &"salt_tonic", "%s: on the tonic" % who)
		var other := ParityHost.row_of(bag, &"crab_carapace")
		ParityHost.move_to(d, bag, other)
		assert_eq(page.current_item(), &"crab_carapace", "%s: the bag has the input again" % who)
		ParityHost.back(d, bag)
		assert_true(menu.child == null and menu.visible, "%s: Cancel closes the page" % who)
		assert_eq(root.cursor, at, "%s: the field menu is on Items" % who)
		var next := ParityHost.row_of(root, FieldMenuModel.ROW_STATUS)
		ParityHost.move_to(d, root, next)
		assert_eq(root.cursor, next, "%s: the field menu has the input again" % who)
		ParityHost.free_field_menu(menu)
		menu = null
	_done()


func test_the_key_items_view_with_each_device() -> void:
	for kind in InputDriver.KINDS:
		var d := InputDriver.new(kind)
		var who := d.label()
		state = GameStateData.new()
		state.party_ids = ParityHost.HEROES.duplicate()
		state.inventory = {"salt_tonic": 3, "brass_lantern": 1, "kell_wick": 1}
		menu = ParityHost.open_field_menu(state)
		var root := menu.root_page()
		ParityHost.choose(d, root, ParityHost.row_of(root, FieldMenuModel.ROW_ITEMS))
		var page := menu.child as ItemsMenu
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(page.tab_label(ItemsMenuModel.VIEW_KEY))
		else:
			d.press(&"ui_page_down")
		assert_eq(page.model.view, ItemsMenuModel.VIEW_KEY, "%s: the Key Items view" % who)
		var bag := page.list_page()
		var wick := ParityHost.row_of(bag, &"kell_wick")
		ParityHost.choose(d, bag, wick)
		assert_eq(page.current_item(), &"kell_wick", "%s: the cursor moves" % who)
		assert_eq(page.desc_text(), page.model.desc(&"kell_wick"), "%s: its words follow" % who)
		assert_eq(page.level, ItemsMenu.Level.LIST, "%s: nothing to use" % who)
		if kind == InputDriver.Kind.MOUSE:
			InputDriver.click(page.tab_label(ItemsMenuModel.VIEW_BAG))
		else:
			d.press(&"ui_page_up")
		assert_eq(page.model.view, ItemsMenuModel.VIEW_BAG, "%s: back to the bag" % who)
		assert_eq(page.current_item(), &"salt_tonic", "%s: on the bag's first item" % who)
		ParityHost.back(d, bag)
		assert_true(menu.child == null and menu.visible, "%s: Cancel closes the page" % who)
		ParityHost.free_field_menu(menu)
		menu = null
	_done()


func test_the_wheel_steps_the_bag_from_the_rows_and_the_page() -> void:
	state = GameStateData.new()
	state.party_ids = ParityHost.HEROES.duplicate()
	state.inventory = {"salt_tonic": 3, "quiet_tea": 2, "crab_carapace": 7}
	var page := ItemsMenu.create(PartySheet.new(state, ParityHost.HEROES))
	page.pause_tree = false
	ParityHost.scene_root().add_child(page)
	var bag := page.list_page()
	InputDriver.wheel(bag.row_node(0), 1)
	assert_eq(bag.cursor, 1, "the wheel over a row")
	assert_eq(page.desc_text(), page.model.desc(page.current_item()), "the item's words follow")
	ParityHost.wheel_at(page, Vector2(page.size.x - 8.0, page.size.y * 0.5), -1)
	assert_eq(bag.cursor, 0, "the wheel over the page's other side")
	page.get_parent().remove_child(page)
	page.free()
	_done()


func _done() -> void:
	ItemsMenu.session_sort = ItemsMenuModel.SORT_KIND
	UiSettings.set_shared(null)
