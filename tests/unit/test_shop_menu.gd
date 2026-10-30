extends TestCase
## M2-UI-06: the shop menu (ShopMenuModel, ShopMenu) over Shop on a scratch GameStateData: buy
## and sell rows priced in lume, every refusal in words, the count, and the view's pause, input
## and close.

const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}

var db: ItemDB
var state: GameStateData
var flags: FlagReader
var menu: ShopMenu


func before_each() -> void:
	db = ItemDB.load_default()
	state = GameStateData.new()
	flags = FlagReader.new()
	flags.values["ch02_met_asha"] = true
	menu = null


# --- the model -----------------------------------------------------------------------------------


func test_the_root_is_buy_sell_leave_and_a_shut_shop_says_why() -> void:
	var m := _model(&"haluna_market")
	assert_eq(m.title(), tr("SHOP_HALUNA_MARKET"))
	var rows := m.root_rows()
	assert_eq(rows.size(), 3)
	assert_eq(rows[0]["label"], tr("SHOP_MENU_BUY"))
	assert_true(rows[0]["enabled"] and rows[1]["enabled"])
	assert_eq(m.root_desc(ShopMenuModel.ROW_BUY), tr("SHOP_MENU_BUY_DESC"))
	var shut := ShopMenuModel.new(db, Shop.new(db, &"haluna_market"), _goods(), FlagReader.new(), NAMES)
	assert_false(shut.root_rows()[0]["enabled"], "shut: no Buy")
	assert_false(shut.root_rows()[1]["enabled"], "and no Sell")
	assert_true(shut.root_rows()[2]["enabled"], "Leave always works")
	assert_eq(shut.root_desc(ShopMenuModel.ROW_BUY), tr("SHOP_ERR_CLOSED"))
	# Act II's heresy (M4-A2P-082): an Order shop refuses heretics with its keeper's line; others keep trading.
	flags.values["ch13_started"] = true
	flags.values["ch15_reached_hollowmere"] = true
	assert_true(_model(&"ansedra_purveyor").root_rows()[0]["enabled"], "the Order's purveyor trades before the trap")
	flags.values[String(ShopMenuModel.HERETIC_FLAG)] = true
	var order := _model(&"ansedra_purveyor")
	assert_eq(order.closed_reason(), ShopMenuModel.ERR_HERETIC)
	assert_false(order.root_rows()[0]["enabled"] or order.root_rows()[1]["enabled"], "no Buy, no Sell for heretics")
	assert_eq(order.root_desc(ShopMenuModel.ROW_BUY), tr("SHOP_ERR_HERETIC"))
	assert_true(_model(&"hollowmere_chandler").root_rows()[0]["enabled"], "a Saltwright keeper still trades")
	var nowhere := _model(&"no_such_shop")
	assert_eq(nowhere.title(), tr("SHOP_MENU_UNKNOWN_TITLE"))
	assert_eq(nowhere.root_desc(ShopMenuModel.ROW_SELL), tr("SHOP_ERR_UNKNOWN_SHOP"))


func test_buy_rows_are_the_stock_with_lume_prices_and_held_counts() -> void:
	state.currency = 30
	var m := _model(&"haluna_market")
	m.party.inventory.add(&"salt_tonic", 2)
	var rows := m.buy_rows()
	var shop := Shop.new(db, &"haluna_market")
	assert_eq(rows.size(), shop.stock(flags).size())
	assert_eq(rows[0]["goods"], &"salt_tonic")
	assert_eq(rows[0]["label"], tr("ITEM_SALT_TONIC"))
	assert_eq(rows[0]["right"], tr("CURRENCY_AMOUNT") % db.price_of(&"salt_tonic"))
	assert_eq(rows[0]["mp"], tr("SHOP_MENU_HELD_FMT").format({"count": 2}))
	assert_eq(rows[0]["right_role"], &"text_disabled", "40 lume with 30 in the purse: refused")
	assert_eq(rows[1]["right_role"], &"text", "Bitterleaf (15) is affordable")
	for r in rows:
		assert_true(r["enabled"], "every row is choosable, so its refusal can be read")
	assert_eq(m.purse_text(), tr("SHOP_MENU_PURSE_FMT").format({"amount": tr("CURRENCY_AMOUNT") % 30}))


func test_buying_spends_lume_and_the_lines_say_the_cost_or_the_refusal() -> void:
	state.currency = 100
	var m := _model(&"haluna_market")
	var line := m.buy_line(&"salt_tonic", 2)
	assert_true(line["ok"])
	assert_eq(
		line["text"],
		tr("SHOP_MENU_BUY_PREVIEW_FMT").format({"count": 2, "name": tr("ITEM_SALT_TONIC"), "price": m.lume(80)})
	)
	var poor := m.buy_line(&"salt_tonic", 3)
	assert_false(poor["ok"])
	assert_eq(
		poor["text"], tr("SHOP_ERR_NO_FUNDS_FMT").format({"price": m.lume(120), "purse": m.lume(100)}), "the numbers"
	)
	var done := m.buy(&"salt_tonic", 2)
	assert_true(done["ok"])
	assert_eq(state.currency, 20)
	assert_eq(m.party.inventory.count(&"salt_tonic"), 2)
	assert_true(str(done["text"]).contains(m.lume(80)))
	var refused := m.buy(&"salt_tonic", 1)
	assert_false(refused["ok"])
	assert_eq(state.currency, 20, "a refused buy changes nothing")
	assert_eq(
		m.buy_line(&"relighting_wick", 1)["text"],
		tr("SHOP_ERR_NOT_IN_STOCK").format({"name": tr("ITEM_RELIGHTING_WICK")})
	)


func test_a_full_bag_refuses_with_the_room_left_and_max_buy_follows_it() -> void:
	state.currency = 9999
	var m := _model(&"haluna_market")
	var cap := db.cap_of(&"salt_tonic")
	m.party.inventory.add(&"salt_tonic", cap - 2)
	assert_eq(m.max_buy(&"salt_tonic", 99), 2)
	var line := m.buy_line(&"salt_tonic", 3)
	assert_false(line["ok"])
	assert_eq(line["text"], tr("SHOP_ERR_NO_ROOM_FMT").format({"room": 2, "name": tr("ITEM_SALT_TONIC")}))
	assert_eq(m.max_buy(&"rhen_coral_hooks", 99), 99, "pieces take no bag room")


func test_the_forge_sells_pieces_and_names_their_wearer() -> void:
	state.currency = 1000
	var m := _model(&"haluna_forge")
	var price := db.price_of(&"rhen_coral_hooks")
	assert_true(m.goods_desc(&"rhen_coral_hooks").contains(tr("SHOP_MENU_FOR_FMT").format({"name": tr("CHAR_RHEN")})))
	assert_true(m.buy(&"rhen_coral_hooks", 1)["ok"])
	assert_eq(state.currency, 1000 - price)
	assert_eq(m.held(&"rhen_coral_hooks"), 1, "one new piece")


func test_sell_rows_list_the_bag_then_pieces_and_explain_refusals() -> void:
	var m := _model(&"haluna_market")
	m.party.inventory.add(&"salt_tonic", 3)
	m.party.inventory.add(&"brass_lantern", 1)
	m.party.equipment.grant_starting(&"rhen")
	var spare := m.party.equipment.add_piece(&"rhen_coral_hooks")
	var rows := m.sell_rows()
	var by_id := {}
	for r in rows:
		by_id[r["id"]] = r
	var tonic: Dictionary = by_id[&"item:salt_tonic"]
	assert_eq(tonic["right"], m.lume(db.sell_price_of(&"salt_tonic")), "half price, from shops.json rules")
	assert_eq(tonic["mp"], tr("SHOP_MENU_HELD_FMT").format({"count": 3}))
	var lantern: Dictionary = by_id[&"item:brass_lantern"]
	assert_eq(lantern["right"], tr("SHOP_MENU_NO_PRICE"), "a key item has no price")
	assert_eq(
		m.sell_line(lantern, 1)["text"], tr("SHOP_ERR_NOT_SELLABLE_FMT").format({"name": tr("ITEM_BRASS_LANTERN")})
	)
	var worn_uid := m.party.equipment.equipped(&"rhen", ItemDB.SLOT_WEAPON)
	var worn: Dictionary = by_id[StringName("piece:%d" % worn_uid)]
	assert_eq(worn["mp"], tr("CHAR_RHEN"), "who wears it")
	assert_false(m.sell_line(worn, 1)["ok"])
	assert_eq(m.sell_line(worn, 1)["text"], tr("SHOP_ERR_EQUIPPED_FMT").format({"wearer": tr("CHAR_RHEN")}))
	var too_many := m.sell_line(tonic, 4)
	assert_eq(too_many["text"], tr("SHOP_ERR_NOT_ENOUGH_FMT").format({"held": 3, "name": tr("ITEM_SALT_TONIC")}))
	assert_eq(m.max_sell(tonic, 99), 3)
	var spare_row: Dictionary = by_id[StringName("piece:%d" % spare)]
	assert_eq(m.max_sell(spare_row, 99), 1)
	var sold := m.sell(tonic, 2)
	assert_true(sold["ok"])
	assert_eq(state.currency, db.sell_price_of(&"salt_tonic") * 2)
	assert_eq(m.party.inventory.count(&"salt_tonic"), 1)
	assert_true(m.sell(spare_row, 1)["ok"])
	assert_false(m.party.equipment.has_piece(spare), "the spare piece is gone")
	assert_false(m.sell(worn, 1)["ok"], "a worn piece is refused")
	assert_true(m.party.equipment.has_piece(worn_uid))


func test_selling_into_a_full_purse_warns_what_is_lost() -> void:
	var m := _model(&"haluna_market")
	state.currency = m.party.wallet.cap - 5
	m.party.inventory.add(&"salt_tonic", 1)
	var row: Dictionary = m.sell_rows()[0]
	var line := m.sell_line(row, 1)
	assert_true(line["ok"])
	var lost := db.sell_price_of(&"salt_tonic") - 5
	assert_true(str(line["text"]).contains(tr("SHOP_MENU_PURSE_FULL_FMT").format({"lost": m.lume(lost)})))


func test_from_game_wraps_the_live_save() -> void:
	var saved := Game.state
	Game.state = GameStateData.new()
	var m := ShopMenuModel.from_game(&"haluna_market")
	m.party.wallet.earn(7)
	assert_eq(Game.state.currency, 7, "the purse is Game.state's")
	assert_eq(m.closed_reason(), Shop.ERR_CLOSED, "the live flags: ch02_met_asha is not set")
	Game.set_flag(&"ch02_met_asha", true)
	assert_eq(m.closed_reason(), Shop.RESULT_OK)
	Game.state = saved


# --- the view ------------------------------------------------------------------------------------


func test_it_pauses_and_cancel_walks_back_then_leaves() -> void:
	state.currency = 100
	_open(&"haluna_market", true)
	var tree := menu.get_tree()
	assert_true(tree.paused, "the field stops under the shop")
	assert_eq(menu.title_text(), tr("SHOP_HALUNA_MARKET"))
	assert_eq(menu.purse_text(), menu.model.purse_text())
	assert_eq(menu.help_text(), tr("SHOP_MENU_HELP_ROOT"))
	assert_eq(menu.desc_text(), tr("SHOP_MENU_BUY_DESC"))
	assert_true(menu.handle_input(_ev(&"ui_accept")))
	assert_eq(menu.level, ShopMenu.Level.BUY)
	assert_true(menu.detail_page().visible)
	assert_eq(menu.help_text(), tr("SHOP_MENU_HELP_DEAL"))
	var closed := [false]
	menu.closed.connect(func() -> void: closed[0] = true)
	menu.handle_input(_ev(&"ui_cancel"))
	assert_eq(menu.level, ShopMenu.Level.ROOT, "Cancel: back to the root")
	assert_true(menu.is_open())
	menu.handle_input(_ev(&"ui_cancel"))
	assert_true(closed[0], "Cancel at the root leaves")
	assert_false(tree.paused, "and the field moves again")
	assert_false(menu.handle_input(_ev(&"ui_down")), "closed: it takes nothing")
	_free()


func test_buying_through_the_view_with_a_count_and_a_refusal() -> void:
	state.currency = 100
	_open(&"haluna_market")
	menu.accept()  # Buy
	assert_eq(menu.detail_page().current_row()["goods"], &"salt_tonic")
	assert_eq(menu.status_text(), menu.model.buy_line(&"salt_tonic", 1)["text"])
	assert_false(menu.status_is_refusal())
	menu.handle_input(_ev(&"ui_right"))
	assert_eq(menu.count, 2)
	menu.handle_input(_ev(&"ui_right"))
	assert_eq(menu.count, 3)
	assert_true(menu.status_is_refusal(), "120 lume with 100: refused, in the danger color")
	assert_eq(menu.status_text(), tr("SHOP_ERR_NO_FUNDS_FMT").format({"price": "120 lume", "purse": "100 lume"}))
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(state.currency, 100, "a refused buy spends nothing")
	menu.handle_input(_ev(&"ui_left"))
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(state.currency, 20)
	assert_eq(menu.model.party.inventory.count(&"salt_tonic"), 2)
	assert_true(menu.status_text().begins_with(tr("SHOP_MENU_BOUGHT_FMT").split("{")[0]), "the receipt")
	assert_eq(menu.purse_text(), menu.model.purse_text(), "the purse redraws")
	assert_eq(menu.detail_page().current_row()["mp"], tr("SHOP_MENU_HELD_FMT").format({"count": 2}))
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.count, 1, "a new row starts at one")
	assert_eq(menu.desc_text(), tr("ITEM_BITTERLEAF_DESC"))
	menu.handle_input(_ev(&"ui_left"))
	assert_eq(menu.count, menu.model.max_buy(&"bitterleaf", 99), "Left from one wraps to the most")
	_free()


func test_selling_through_the_view_and_an_empty_bag() -> void:
	_open(&"haluna_market")
	menu.handle_input(_ev(&"ui_down"))
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.level, ShopMenu.Level.SELL)
	assert_eq(menu.detail_page().row_count(), 0)
	assert_eq(menu.desc_text(), tr("SHOP_MENU_SELL_EMPTY"))
	menu.handle_input(_ev(&"ui_accept"))  # nothing to sell: nothing happens
	assert_true(menu.is_open())
	menu.back()
	menu.model.party.inventory.add(&"bitterleaf", 2)
	menu.accept()
	assert_eq(menu.detail_page().row_count(), 1)
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(state.currency, db.sell_price_of(&"bitterleaf"))
	assert_eq(menu.model.party.inventory.count(&"bitterleaf"), 1)
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.detail_page().row_count(), 0, "the last one sold: the row goes")
	assert_true(menu.status_text().begins_with(tr("SHOP_MENU_SOLD_FMT").split("{")[0]), "the receipt stays")
	_free()


func test_a_shut_shop_starts_on_leave_and_clicks_choose() -> void:
	flags.values.erase("ch02_met_asha")
	_open(&"haluna_market")
	assert_eq(menu.root_page().current_row()["id"], ShopMenuModel.ROW_LEAVE, "Buy and Sell are off")
	assert_eq(menu.desc_text(), tr("SHOP_MENU_LEAVE_DESC"))
	menu._on_clicked(2, ShopMenu.Level.ROOT)
	assert_false(menu.is_open(), "a click on Leave leaves")
	_free()
	flags.values["ch02_met_asha"] = true
	_open(&"haluna_market")
	menu._on_clicked(0, ShopMenu.Level.ROOT)
	assert_eq(menu.level, ShopMenu.Level.BUY, "a click on Buy opens the stock")
	menu._on_clicked(0, ShopMenu.Level.ROOT)
	assert_eq(menu.level, ShopMenu.Level.BUY, "a click on the root goes back to it and chooses")
	_free()


func test_open_in_brings_its_own_layer() -> void:
	var host := Node.new()
	_root().add_child(host)
	var m := ShopMenu.open_in(host, _model(&"haluna_market"))
	var layer := m.get_parent() as CanvasLayer
	assert_true(layer != null, "on a CanvasLayer")
	assert_eq(layer.layer, int(TownMenu.load_data(ShopMenu.SECTION)["canvas_layer"]))
	assert_true(host.get_tree().paused)
	m.close()
	assert_false(host.get_tree().paused)
	assert_false(layer.is_queued_for_deletion(), "it fades out first (MenuMotion)")
	m.motion().finish()
	assert_true(layer.is_queued_for_deletion())
	_root().remove_child(host)
	host.free()


# --- helpers -------------------------------------------------------------------------------------


func _goods() -> PartyGoods:
	return PartyGoods.from_state(db, state)


func _model(shop_id: StringName) -> ShopMenuModel:
	return ShopMenuModel.new(db, Shop.new(db, shop_id), _goods(), flags, NAMES)


func _open(shop_id: StringName, pause: bool = false) -> void:
	menu = (load(ShopMenu.SCENE_PATH) as PackedScene).instantiate() as ShopMenu
	menu.pause_tree = pause
	menu.configure(_model(shop_id))
	_root().add_child(menu)


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


func _free() -> void:
	if menu == null:
		return
	if menu.is_inside_tree():
		menu.get_tree().paused = false
		menu.get_parent().remove_child(menu)
	menu.free()
	menu = null
