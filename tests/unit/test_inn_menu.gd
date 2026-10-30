extends TestCase
## M2-UI-06: the inn menu (InnMenuModel, InnMenu): a rest costs the inn's data price and heals the
## party the way a save shrine does (EventBus.party_full_heal_requested -> Game.heal_party), but
## writes no save, emits no save signal and leaves the respawn point alone. Plus the view's pause,
## input and close.

const TEST_DIR := "user://test_inn_menu"

var db: ItemDB
var state: GameStateData
var flags: FlagReader
var healed: Array[StringName] = []
var saves: Array[int] = []
var menu: InnMenu
var _saved_state: GameStateData
var _saved_dir := ""


func before_each() -> void:
	db = ItemDB.load_default()
	state = GameStateData.new()
	flags = FlagReader.new()
	flags.values["ch02_met_asha"] = true
	healed = []
	saves = []
	menu = null


func _heal(source: StringName) -> void:
	healed.append(source)


func _on_saved(slot: int) -> void:
	saves.append(slot)


# --- the model -----------------------------------------------------------------------------------


func test_rows_lines_and_the_price_in_lume() -> void:
	state.currency = 100
	var m := _model()
	var price := Inn.new(db, &"haluna_inn").price()
	assert_eq(m.title(), tr("INN_HALUNA"))
	var rows := m.root_rows()
	assert_eq(rows[0]["label"], tr("INN_MENU_REST"))
	assert_eq(rows[0]["right"], tr("CURRENCY_AMOUNT") % price)
	assert_eq(rows[1]["label"], tr("INN_MENU_LEAVE"))
	var desc := m.row_desc(InnMenuModel.ROW_REST)
	assert_true(desc.contains(tr("INN_HALUNA_DESC")))
	assert_true(desc.contains(tr("INN_MENU_REST_DESC")))
	assert_true(desc.contains(tr("INN_MENU_NO_SAVE")), "the inn says it does not save")
	assert_eq(m.rest_line()["text"], tr("INN_MENU_PREVIEW_FMT").format({"price": m.lume(price)}))
	assert_eq(m.row_desc(InnMenuModel.ROW_LEAVE), tr("INN_MENU_LEAVE_DESC"))


func test_a_rest_pays_and_heals_and_a_poor_party_is_told_why() -> void:
	var price := Inn.new(db, &"haluna_inn").price()
	state.currency = price - 1
	var m := _model()
	var line := m.rest_line()
	assert_false(line["ok"])
	assert_eq(line["text"], tr("INN_ERR_NO_FUNDS_FMT").format({"price": m.lume(price), "purse": m.lume(price - 1)}))
	assert_eq(m.root_rows()[0]["right_role"], &"text_disabled")
	assert_false(m.rest()["ok"])
	assert_eq(healed.size(), 0)
	state.currency = price
	var done := m.rest()
	assert_true(done["ok"])
	assert_eq(done["text"], tr("INN_MENU_RESTED"))
	assert_eq(state.currency, 0)
	assert_eq(healed, [&"haluna_inn"] as Array[StringName])
	var shut := InnMenuModel.new(Inn.new(db, &"haluna_inn"), PartyGoods.from_state(db, state), FlagReader.new(), _heal)
	assert_false(shut.root_rows()[0]["enabled"], "shut until its flag")
	assert_eq(shut.rest_line()["text"], tr("INN_ERR_CLOSED"))


func test_sefir_s_guest_rooms_are_free_and_shut_to_heretics() -> void:
	# Act II screens.md section 5 and heresy.md section 2: a price-0 Order house.
	flags.values["ch13_started"] = true
	state.currency = 0
	var m := InnMenuModel.new(Inn.new(db, &"ansedra_guest"), PartyGoods.from_state(db, state), flags, _heal)
	assert_eq(m.title(), tr("INN_ANSEDRA_GUEST"))
	assert_eq(m.root_rows()[0]["right"], tr("INN_MENU_FREE"), "no lume shown")
	assert_eq(m.rest_line()["text"], tr("INN_MENU_PREVIEW_FREE"))
	assert_true(m.rest()["ok"], "an empty purse rests")
	assert_eq(healed, [&"ansedra_guest"] as Array[StringName])
	flags.values[String(ShopMenuModel.HERETIC_FLAG)] = true
	assert_false(m.root_rows()[0]["enabled"], "outside the Level: the door is shut")
	assert_eq(m.rest_line()["text"], tr("INN_ERR_HERETIC"))
	assert_false(m.rest()["ok"])
	assert_eq(healed.size(), 1, "no second rest")
	var kept := InnMenuModel.new(Inn.new(db, &"hollowmere_inn"), PartyGoods.from_state(db, state), flags, _heal)
	assert_ne(kept.rest_line()["text"], tr("INN_ERR_HERETIC"), "a Saltwright inn still takes them")


func test_the_live_rest_heals_like_a_shrine_and_writes_no_save() -> void:
	_saved_state = Game.state
	_saved_dir = SaveSystem.save_dir
	SaveSystem.save_dir = TEST_DIR
	Game.state = GameStateData.new()
	Game.set_flag(&"ch02_met_asha", true)
	Game.state.currency = 100
	Game.state.location_id = &"haluna"
	Game.state.respawn_location_id = &"somewhere_else"
	Game.state.party_vitals = {"rhen": {"hp": 12, "mp": 3, "statuses": ["poison"]}, "asha": {"hp": 0}}
	EventBus.game_saved.connect(_on_saved)
	EventBus.party_full_heal_requested.connect(_heal)
	var m := InnMenuModel.from_game(&"haluna_inn")
	assert_true(m.rest()["ok"])
	assert_eq(healed, [&"haluna_inn"] as Array[StringName], "the shrine's own heal request")
	assert_eq(Game.state.party_vitals, {}, "full HP and MP, poison cured, the fallen up again")
	assert_eq(Game.state.currency, 100 - m.inn.price())
	assert_eq(saves.size(), 0, "no game_saved")
	assert_false(DirAccess.dir_exists_absolute(TEST_DIR) and not DirAccess.get_files_at(TEST_DIR).is_empty(), "no file")
	assert_eq(Game.state.respawn_location_id, &"somewhere_else", "an inn is not a respawn point")
	assert_false(bool(Game.get_flag(&"save_shrine_used")), "nor a shrine")
	EventBus.game_saved.disconnect(_on_saved)
	EventBus.party_full_heal_requested.disconnect(_heal)
	SaveSystem.save_dir = _saved_dir
	Game.state = _saved_state


# --- the view ------------------------------------------------------------------------------------


func test_it_pauses_rests_and_cancel_leaves() -> void:
	state.currency = 100
	_open(true)
	var tree := menu.get_tree()
	assert_true(tree.paused)
	assert_eq(menu.title_text(), tr("INN_HALUNA"))
	assert_eq(menu.help_text(), tr("INN_MENU_HELP"))
	assert_eq(menu.root_page().current_row()["id"], InnMenuModel.ROW_REST)
	assert_eq(menu.status_text(), menu.model.rest_line()["text"])
	assert_true(menu.handle_input(_ev(&"ui_accept")))
	assert_eq(healed.size(), 1, "rested once")
	assert_eq(menu.status_text(), tr("INN_MENU_RESTED"))
	assert_eq(menu.root_page().current_row()["id"], InnMenuModel.ROW_LEAVE, "the cursor moves to Leave")
	assert_eq(menu.purse_text(), menu.model.purse_text())
	menu.handle_input(_ev(&"ui_up"))
	assert_eq(menu.status_text(), menu.model.rest_line()["text"], "moving clears the receipt")
	var closed := [false]
	menu.closed.connect(func() -> void: closed[0] = true)
	assert_true(menu.handle_input(_ev(&"ui_cancel")))
	assert_true(closed[0])
	assert_false(tree.paused)
	assert_false(menu.handle_input(_ev(&"ui_accept")))
	_free()


func test_a_refused_rest_is_shown_in_the_danger_color_and_clicks_choose() -> void:
	state.currency = 1
	_open()
	assert_true(menu.status_is_refusal())
	menu.accept()
	assert_eq(healed.size(), 0)
	assert_eq(state.currency, 1)
	menu._on_clicked(1)
	assert_false(menu.is_open(), "a click on Leave leaves")
	_free()
	flags.values.erase("ch02_met_asha")
	_open()
	assert_eq(menu.root_page().current_row()["id"], InnMenuModel.ROW_LEAVE, "shut: the cursor starts on Leave")
	assert_eq(menu.status_text(), tr("INN_ERR_CLOSED"), "and the line says why")
	_free()


# --- helpers -------------------------------------------------------------------------------------


func _model() -> InnMenuModel:
	return InnMenuModel.new(Inn.new(db, &"haluna_inn"), PartyGoods.from_state(db, state), flags, _heal)


func _open(pause: bool = false) -> void:
	menu = (load(InnMenu.SCENE_PATH) as PackedScene).instantiate() as InnMenu
	menu.pause_tree = pause
	menu.configure(_model())
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
