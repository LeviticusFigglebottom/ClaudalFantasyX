extends TestCase
## M2-MNU-03: the field Items page (ItemsMenuModel, ItemsMenu) over a PartySheet on a scratch
## GameStateData: the bag's words and counts, the three sorts, field use that heals exactly what
## the battle item would (ItemBattleAction.resolve_on) and keeps the saved Swell, every refusal in
## words, all-allies items, and the view's input (ui_*, wheel and mouse). The runner has no
## after_each: each test that opens the view frees it itself (_teardown).

const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]

var state: GameStateData
var menu: ItemsMenu


func before_each() -> void:
	state = GameStateData.new()
	state.party_ids = HEROES.duplicate()
	state.inventory = {"salt_tonic": 3, "quiet_tea": 2, "crab_carapace": 7, "brass_lantern": 1, "ember_pot": 1}
	menu = null
	ItemsMenu.session_sort = ItemsMenuModel.SORT_KIND


# --- the model -----------------------------------------------------------------------------------


func test_rows_are_the_bag_with_names_categories_and_counts() -> void:
	var m := _model()
	var rows := m.rows()
	assert_eq(rows.size(), 4, "the bag leaves the key item to the Key Items view")
	assert_eq(rows[0]["id"], &"salt_tonic", "kind order: consumables first")
	assert_eq(rows[0]["label"], tr("ITEM_SALT_TONIC"))
	assert_eq(rows[0]["mp"], tr("ITEM_CATEGORY_CONSUMABLE"))
	assert_eq(rows[0]["right"], tr("ITEMS_MENU_COUNT_FMT").format({"count": 3}))
	assert_eq(rows[0]["right_role"], &"text", "usable here")
	assert_true(_row(rows, &"brass_lantern").is_empty())
	var pot := _row(rows, &"ember_pot")
	assert_true(pot["enabled"], "a battle-only item is choosable, so the line can say why")
	assert_eq(pot["right_role"], &"text_dim")
	assert_eq(m.desc(&"salt_tonic"), tr("ITEM_SALT_TONIC_DESC"))
	assert_eq(
		m.held_text(&"crab_carapace"),
		tr("ITEMS_MENU_HELD_FMT").format({"category": tr("ITEM_CATEGORY_MATERIAL"), "count": 7})
	)
	for r in rows:
		assert_true(r["enabled"])


func test_the_three_sorts_and_their_words() -> void:
	var m := _model()
	var listing := m.inventory().ids()
	listing.erase(&"brass_lantern")
	assert_eq(m.item_ids(), listing, "by kind is the listing order (ItemDB.sort_rank), key items left out")
	assert_eq(m.sort_text(), tr("ITEMS_MENU_SORT_FMT").format({"sort": tr("ITEMS_MENU_SORT_KIND")}))
	assert_eq(m.next_sort(), ItemsMenuModel.SORT_NAME)
	var names: Array[String] = []
	for iid in m.item_ids():
		names.append(m.item_name(iid))
	var sorted := names.duplicate()
	sorted.sort_custom(func(a: String, b: String) -> bool: return a.naturalnocasecmp_to(b) < 0)
	assert_eq(names, sorted, "by name")
	assert_eq(m.next_sort(), ItemsMenuModel.SORT_COUNT)
	var ids := m.item_ids()
	assert_eq(ids[0], &"crab_carapace", "7 first")
	assert_eq(ids[1], &"salt_tonic", "then 3")
	assert_eq(ids[2], &"quiet_tea", "then 2")
	assert_eq(ids[3], &"ember_pot", "then 1")
	assert_eq(ids.size(), 4, "no key item in any sort")
	assert_eq(m.next_sort(), ItemsMenuModel.SORT_KIND, "wraps")
	assert_eq(m.next_sort(-1), ItemsMenuModel.SORT_COUNT, "and back")


func test_field_use_heals_what_resolve_on_says_and_keeps_the_swell() -> void:
	state.party_vitals = {"rhen": {"hp": 100, "swell": 40, "swell_mode": "wake"}}
	var m := _model()
	var expect := m.sheet.combatant(&"rhen")
	ItemBattleAction.for_item(m.db(), &"salt_tonic").resolve_on(expect)
	assert_true(expect.hp > 100 and expect.hp < expect.max_hp, "a partial heal, so HP is still saved")
	var line := m.preview(&"salt_tonic", &"rhen")
	assert_true(line["ok"])
	var change := tr("ITEMS_MENU_PREVIEW_HP_FMT").format({"from": 100, "to": expect.hp})
	assert_eq(line["text"], tr("ITEMS_MENU_PREVIEW_FMT").format({"name": tr("CHAR_RHEN"), "changes": change}))
	assert_eq(state.vitals_of(&"rhen")["hp"], 100, "a preview saves nothing")
	var done := m.use(&"salt_tonic", &"rhen")
	assert_true(done["ok"])
	assert_true(str(done["text"]).contains(change), "the receipt says what it did")
	assert_eq(state.vitals_of(&"rhen")["hp"], expect.hp, "the saved HP is resolve_on's")
	assert_eq(state.swell_of(&"rhen"), 40, "the gauge keeps its points")
	assert_eq(state.swell_mode_of(&"rhen"), &"wake", "and its mode")
	assert_eq(m.inventory().count(&"salt_tonic"), 2, "one used")
	assert_eq(m.sheet.combatant(&"rhen").hp, expect.hp, "and the sheet reads it back")


func test_a_heal_to_full_drops_the_saved_hp_and_mp_tea_restores_mp() -> void:
	state.party_vitals = {"rhen": {"hp": 400, "mp": 1}}
	var m := _model()
	assert_true(m.use(&"salt_tonic", &"rhen")["ok"])
	assert_false(state.vitals_of(&"rhen").has("hp"), "full HP is stored as no value")
	var expect := m.sheet.combatant(&"rhen")
	ItemBattleAction.for_item(m.db(), &"quiet_tea").resolve_on(expect)
	assert_true(m.use(&"quiet_tea", &"rhen")["ok"])
	assert_eq(m.sheet.combatant(&"rhen").mp, expect.mp)


func test_refusals_are_in_words_and_spend_nothing() -> void:
	state.inventory["relighting_wick"] = 1
	state.inventory["quickwater"] = 1
	state.inventory["bitterleaf"] = 1
	state.inventory["facet_power"] = 1
	state.party_vitals = {"asha": {"hp": 0}}
	var m := _model()
	var refusals := {
		&"brass_lantern": ItemsMenuModel.ERR_KEY,
		&"crab_carapace": ItemsMenuModel.ERR_MATERIAL,
		&"facet_power": ItemsMenuModel.ERR_FACET,
		&"ember_pot": ItemsMenuModel.ERR_BATTLE_ONLY,
		&"quickwater": ItemsMenuModel.ERR_BATTLE_ONLY,
	}
	for iid: StringName in refusals:
		assert_eq(m.item_error(iid), refusals[iid], String(iid))
		var line := m.item_line(iid)
		assert_false(line["ok"])
		assert_eq(line["text"], tr(ItemsMenuModel.REFUSAL_KEYS[refusals[iid]]).format({"item": m.item_name(iid)}))
	assert_eq(m.item_line(&"salt_tonic")["text"], tr("ITEMS_MENU_USE_HINT"))
	var heroes := {
		&"rhen": ItemsMenuModel.ERR_FULL_HP,
		&"asha": ItemsMenuModel.ERR_FALLEN,
	}
	for cid: StringName in heroes:
		assert_eq(m.hero_error(&"salt_tonic", cid), heroes[cid], String(cid))
		var r := m.use(&"salt_tonic", cid)
		assert_false(r["ok"])
		var key: String = ItemsMenuModel.REFUSAL_KEYS[heroes[cid]]
		assert_eq(r["text"], tr(key).format({"item": tr("ITEM_SALT_TONIC"), "name": m.sheet.hero_name(cid)}))
	assert_eq(m.hero_error(&"quiet_tea", &"rhen"), ItemsMenuModel.ERR_FULL_MP)
	assert_eq(m.hero_error(&"bitterleaf", &"rhen"), ItemsMenuModel.ERR_NOTHING_TO_CURE)
	assert_eq(m.hero_error(&"relighting_wick", &"rhen"), ItemsMenuModel.ERR_NOT_FALLEN)
	assert_eq(m.inventory().count(&"salt_tonic"), 3, "nothing spent")
	assert_eq(state.vitals_of(&"asha"), {"hp": 0}, "nothing written")


func test_a_revive_raises_the_fallen_and_a_cure_clears_a_carried_status() -> void:
	state.inventory = {"relighting_wick": 1, "bitterleaf": 1}
	state.party_vitals = {"asha": {"hp": 0}, "toma": {"statuses": ["poison"], "swell": 12}}
	var m := _model()
	var asha := m.sheet.combatant(&"asha")
	assert_eq(asha.hp, 0)
	assert_eq(m.hero_error(&"relighting_wick", &"asha"), ItemsMenuModel.RESULT_OK)
	assert_true(m.use(&"relighting_wick", &"asha")["ok"])
	assert_eq(m.sheet.combatant(&"asha").hp, ItemBattleAction.revive_hp(asha.max_hp, 25), "a quarter of her HP")
	assert_eq(m.inventory().count(&"relighting_wick"), 0)
	assert_eq(m.item_error(&"relighting_wick"), ItemsMenuModel.ERR_NONE_LEFT)
	assert_eq(state.statuses_of(&"toma"), [&"poison"] as Array[StringName])
	var line := m.preview(&"bitterleaf", &"toma")
	assert_true(str(line["text"]).contains(tr("ITEMS_MENU_PREVIEW_CURE_FMT").format({"statuses": tr("STATUS_POISON")})))
	assert_true(m.use(&"bitterleaf", &"toma")["ok"])
	assert_eq(state.statuses_of(&"toma").size(), 0, "cured in the save")
	assert_eq(state.swell_of(&"toma"), 12, "the gauge stays")


func test_an_all_allies_item_helps_everyone_it_can() -> void:
	var db := ItemDB.load_default()
	((db.items[&"salt_tonic"] as Dictionary)["battle"] as Dictionary)["target"] = "all_allies"
	state.party_vitals = {"rhen": {"hp": 50}, "asha": {"hp": 0}, "toma": {"hp": 60, "swell": 30}}
	var m := ItemsMenuModel.new(PartySheet.new(state, HEROES, null, db), [&"poison"])
	assert_true(m.is_all_allies(&"salt_tonic"))
	assert_eq(m.pick_title(&"salt_tonic"), tr("ITEMS_MENU_PICK_ALL_TITLE_FMT").format({"item": tr("ITEM_SALT_TONIC")}))
	assert_eq(m.targets(&"salt_tonic", &"asha"), [&"rhen", &"toma"] as Array[StringName], "the fallen are left out")
	var r := m.use(&"salt_tonic", &"asha")
	assert_true(r["ok"])
	assert_eq(state.vitals_of(&"rhen")["hp"], 250)
	assert_eq(state.vitals_of(&"toma")["hp"], 260)
	assert_eq(state.swell_of(&"toma"), 30)
	assert_eq(state.vitals_of(&"asha")["hp"], 0)
	assert_eq(m.inventory().count(&"salt_tonic"), 2, "one item for everyone")
	state.party_vitals = {"asha": {"hp": 0}}
	var none := m.use(&"salt_tonic", &"rhen")
	assert_false(none["ok"])
	assert_eq(none["text"], tr("ITEMS_MENU_ERR_NO_ONE_FMT").format({"item": tr("ITEM_SALT_TONIC")}))


func test_hero_rows_show_hp_and_mp_now() -> void:
	state.party_vitals = {"rhen": {"hp": 120}, "asha": {"hp": 0}}
	var m := _model()
	var rows := m.hero_rows(&"salt_tonic")
	var rhen := m.sheet.combatant(&"rhen")
	assert_eq(rows[0]["mp"], tr("HUD_HP_FMT").format({"hp": 120, "max": rhen.max_hp}))
	assert_eq(rows[0]["right"], tr("MENUS_MP_FMT").format({"mp": rhen.mp, "max": rhen.max_mp}))
	assert_eq(rows[0]["right_role"], &"text")
	assert_eq(rows[1]["label"], tr("CHAR_ASHA") + tr("ITEMS_MENU_FALLEN_TAG"))
	assert_eq(rows[1]["right_role"], &"text_dim", "a tonic does nothing for her")


# --- the view ------------------------------------------------------------------------------------


func test_keys_move_sort_use_and_go_back() -> void:
	state.party_vitals = {"rhen": {"hp": 100, "swell": 20}}
	_open(true)
	var tree := menu.get_tree()
	assert_true(tree.paused, "the field stops under the page")
	assert_eq(menu.current_item(), &"salt_tonic")
	assert_eq(menu.help_text(), tr("ITEMS_MENU_HELP"))
	assert_eq(menu.desc_text(), tr("ITEM_SALT_TONIC_DESC"))
	assert_true(menu.handle_input(_ev(&"ui_down")))
	assert_eq(menu.current_item(), &"quiet_tea")
	assert_true(menu.handle_input(_ev(&"ui_right")))
	assert_eq(menu.model.sort, ItemsMenuModel.SORT_NAME)
	assert_eq(menu.current_item(), &"quiet_tea", "the cursor keeps its item through a sort")
	assert_eq(menu.sort_text(), menu.model.sort_text())
	assert_eq(ItemsMenu.session_sort, ItemsMenuModel.SORT_NAME, "remembered for the session")
	menu.handle_input(_ev(&"ui_left"))
	assert_eq(menu.model.sort, ItemsMenuModel.SORT_KIND)
	menu.handle_input(_ev(&"ui_up"))
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.level, ItemsMenu.Level.PICK)
	assert_true(menu.picker_page().visible)
	assert_eq(menu.help_text(), tr("ITEMS_MENU_HELP_PICK"))
	assert_eq(menu.picker_gauges().size(), HEROES.size() * 2, "an HP and an MP gauge per hero")
	assert_eq(menu.preview_text(), menu.model.preview(&"salt_tonic", &"rhen")["text"])
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(state.swell_of(&"rhen"), 20)
	assert_eq(state.vitals_of(&"rhen")["hp"], 300)
	assert_true(menu.preview_text().begins_with(tr("ITEMS_MENU_USED_FMT").get_slice("{", 0)), "the receipt")
	assert_eq(menu.level, ItemsMenu.Level.PICK, "stays for a second one")
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.preview_text(), menu.model.preview(&"salt_tonic", &"asha")["text"], "the cursor clears it")
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.model.inventory().count(&"salt_tonic"), 2, "a refused use spends nothing")
	menu.handle_input(_ev(&"ui_cancel"))
	assert_eq(menu.level, ItemsMenu.Level.LIST)
	assert_true(menu.handle_input(_ev(&"ui_cancel")))
	assert_false(menu.is_open())
	assert_false(tree.paused)
	_teardown()


func test_a_refused_item_does_not_open_the_picker_and_the_last_one_closes_it() -> void:
	state.inventory = {"salt_tonic": 1, "crab_carapace": 1}
	state.party_vitals = {"toma": {"hp": 10}}
	_open()
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.current_item(), &"crab_carapace")
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.level, ItemsMenu.Level.LIST, "a material opens nothing")
	assert_eq(menu.use_text(), menu.model.item_line(&"crab_carapace")["text"])
	menu.handle_input(_ev(&"ui_up"))
	menu.handle_input(_ev(&"ui_accept"))
	menu.handle_input(_ev(&"ui_down"))
	menu.handle_input(_ev(&"ui_down"))
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(state.vitals_of(&"toma")["hp"], 210)
	assert_eq(menu.level, ItemsMenu.Level.LIST, "the last tonic is gone: back to the bag")
	assert_eq(menu.list_page().row_count(), 1)
	assert_eq(menu.current_item(), &"crab_carapace")
	assert_true(menu.use_text().contains(tr("ITEM_SALT_TONIC")), "the receipt stays on the line")
	_teardown()


func test_the_mouse_hovers_clicks_scrolls_and_sorts() -> void:
	state.party_vitals = {"rhen": {"hp": 100}}
	_open()
	assert_true(menu.handle_input(_wheel(MOUSE_BUTTON_WHEEL_DOWN)))
	assert_eq(menu.current_item(), &"quiet_tea")
	menu.handle_input(_wheel(MOUSE_BUTTON_WHEEL_UP))
	assert_eq(menu.current_item(), &"salt_tonic")
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	menu._on_sort_input(click)
	assert_eq(menu.model.sort, ItemsMenuModel.SORT_NAME, "a click on the sort line changes it")
	menu._on_sort_input(click)
	menu._on_sort_input(click)
	var at := _index_of(&"salt_tonic")
	menu._on_clicked(at, ItemsMenu.Level.LIST)
	assert_eq(menu.level, ItemsMenu.Level.PICK, "a click on a tonic opens the picker")
	menu._on_clicked(0, ItemsMenu.Level.PICK)
	assert_eq(state.vitals_of(&"rhen")["hp"], 300, "a click on Rhen uses it")
	menu._on_clicked(_index_of(&"quiet_tea"), ItemsMenu.Level.LIST)
	assert_eq(menu.current_item(), &"quiet_tea", "a click on the bag goes back to it")
	assert_eq(menu.level, ItemsMenu.Level.PICK, "and chooses: Quiet Tea's picker")
	_teardown()


# --- the Key Items view (M3-MNU-03) ---------------------------------------------------------------


func test_the_key_view_lists_key_items_with_their_words_and_no_use() -> void:
	state.inventory["kell_wick"] = 1
	var m := _model()
	assert_eq(m.view, ItemsMenuModel.VIEW_BAG)
	assert_eq(m.view_label(ItemsMenuModel.VIEW_KEY), tr("ITEMS_MENU_VIEW_KEY"))
	assert_eq(m.next_view(), ItemsMenuModel.VIEW_KEY)
	assert_eq(m.item_ids(), m.inventory().ids_in(ItemDB.CATEGORY_KEY), "key items in data order")
	assert_eq(m.item_ids(), [&"brass_lantern", &"kell_wick"] as Array[StringName])
	m.next_sort()
	assert_eq(m.item_ids(), [&"brass_lantern", &"kell_wick"] as Array[StringName], "the sort is the bag's")
	var rows := m.rows()
	assert_eq(rows[0]["label"], tr("ITEM_BRASS_LANTERN"))
	assert_eq(rows[0]["right"], "")
	assert_eq(m.desc(&"kell_wick"), tr("ITEM_KELL_WICK_DESC"))
	var line := m.item_line(&"kell_wick")
	assert_eq(line["text"], tr("ITEMS_MENU_KEY_NOTE"), "kept, not refused")
	assert_true(line["ok"])
	assert_eq(m.item_error(&"kell_wick"), ItemsMenuModel.ERR_KEY, "and never used")
	assert_eq(m.next_view(), ItemsMenuModel.VIEW_BAG, "wraps")
	m.inventory().remove(&"brass_lantern", 1)
	m.inventory().remove(&"kell_wick", 1)
	m.view = ItemsMenuModel.VIEW_KEY
	assert_eq(m.rows().size(), 0)
	assert_eq(m.empty_text(), tr("ITEMS_MENU_KEY_EMPTY"))


func test_page_keys_and_tabs_switch_the_view_and_confirm_uses_nothing() -> void:
	state.inventory["kell_wick"] = 1
	_open()
	assert_eq(menu.tab_label(ItemsMenuModel.VIEW_BAG).text, tr("ITEMS_MENU_VIEW_BAG"))
	assert_true(menu.handle_input(_ev(&"ui_page_down")))
	assert_eq(menu.model.view, ItemsMenuModel.VIEW_KEY)
	assert_eq(menu.current_item(), &"brass_lantern", "the cursor starts at the top")
	assert_eq(menu.help_text(), tr("ITEMS_MENU_HELP_KEY"))
	assert_eq(menu.desc_text(), tr("ITEM_BRASS_LANTERN_DESC"))
	assert_eq(menu.use_text(), tr("ITEMS_MENU_KEY_NOTE"))
	assert_false(menu.sort_text() != "" and menu._sort.visible, "no sort line on the key view")
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.current_item(), &"kell_wick")
	menu.handle_input(_ev(&"ui_right"))
	assert_eq(menu.model.sort, ItemsMenuModel.SORT_KIND, "Left and Right sort only the bag")
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.level, ItemsMenu.Level.LIST, "Confirm on a key item opens nothing")
	assert_eq(menu.model.inventory().count(&"kell_wick"), 1)
	menu.handle_input(_ev(&"ui_page_up"))
	assert_eq(menu.model.view, ItemsMenuModel.VIEW_BAG)
	assert_eq(menu.help_text(), tr("ITEMS_MENU_HELP"))
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	menu._on_tab_input(click, ItemsMenuModel.VIEW_KEY)
	assert_eq(menu.model.view, ItemsMenuModel.VIEW_KEY, "a click on a tab shows it")
	menu.handle_input(_ev(&"ui_cancel"))
	assert_false(menu.is_open(), "Cancel closes from either view")
	_teardown()


# --- helpers -------------------------------------------------------------------------------------


func _model() -> ItemsMenuModel:
	return ItemsMenuModel.new(PartySheet.new(state, HEROES), [&"poison", &"petrify", &"zombie"])


func _row(rows: Array[Dictionary], id: StringName) -> Dictionary:
	for r in rows:
		if r["id"] == id:
			return r
	return {}


func _index_of(id: StringName) -> int:
	for i in menu.list_page().row_count():
		if menu.list_page().rows[i]["id"] == id:
			return i
	return -1


func _open(pause: bool = false) -> void:
	menu = ItemsMenu.create(PartySheet.new(state, HEROES))
	menu.pause_tree = pause
	_root().add_child(menu)


func _teardown() -> void:
	if menu == null:
		return
	menu.close()
	menu.get_tree().paused = false
	menu.get_parent().remove_child(menu)
	menu.free()
	menu = null
	ItemsMenu.session_sort = ItemsMenuModel.SORT_KIND


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


func _wheel(button: MouseButton) -> InputEventMouseButton:
	var ev := InputEventMouseButton.new()
	ev.button_index = button
	ev.pressed = true
	return ev
