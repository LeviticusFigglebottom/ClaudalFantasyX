extends TestCase
## M2-MNU-07: the party Formation page (FormationMenuModel, FormationMenu) over a PartySheet on a
## scratch GameStateData: the rows, swaps (active with active reorders, active with reserve trades
## places, an open place takes a hero in), the refusals in words (nobody gathered, an open place
## picked, the active line too small, nobody left standing), the fallen warning, the save
## (party_ids / reserve_ids), and the view's keys, mouse and words. The runner has no after_each:
## each test that opens the view frees it itself (_teardown).

const ACTIVE: Array[StringName] = [&"rhen", &"asha", &"toma"]
const RESERVE: Array[StringName] = [&"ysolde"]
const A := FormationMenuModel.LINE_ACTIVE
const R := FormationMenuModel.LINE_RESERVE

var state: GameStateData
var menu: FormationMenu


func before_each() -> void:
	state = GameStateData.new()
	state.party_ids = ACTIVE.duplicate()
	state.reserve_ids = RESERVE.duplicate()
	menu = null
	UiSettings.set_shared(UiSettings.new())


func _teardown() -> void:
	if menu != null and is_instance_valid(menu):
		menu.close()
		if menu.get_parent() != null:
			menu.get_parent().remove_child(menu)
		menu.free()
	menu = null
	UiSettings.set_shared(null)


func _model() -> FormationMenuModel:
	return FormationMenuModel.new(PartySheet.new(state, ACTIVE + RESERVE), FormationMenuModel.load_rules())


func _open() -> FormationMenu:
	menu = FormationMenu.create(PartySheet.new(state, ACTIVE + RESERVE))
	menu.pause_tree = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(menu)
	return menu


# --- the model -----------------------------------------------------------------------------------


func test_the_active_line_has_the_battle_s_places_and_the_reserve_one_open_place() -> void:
	var m := _model()
	assert_eq(FormationMenuModel.places(), BattleEngine.MAX_ACTIVE, "SPEC §6.1: three active fighters")
	var rows := m.rows(A)
	assert_eq(rows.size(), BattleEngine.MAX_ACTIVE)
	assert_eq(rows[0]["label"], tr("CHAR_RHEN"))
	var v := m.vitals(&"rhen")
	assert_eq(rows[0]["mp"], tr("HUD_HP_FMT").format({"hp": v["hp"], "max": v["max_hp"]}))
	assert_eq(rows[0]["right"], tr("MENUS_MP_FMT").format({"mp": v["mp"], "max": v["max_mp"]}))
	var reserve := m.rows(R)
	assert_eq(reserve.size(), RESERVE.size() + 1, "each reserve hero and one open place")
	assert_eq(reserve[0]["label"], tr("CHAR_YSOLDE"))
	assert_eq(reserve[1]["label"], tr("FORMATION_MENU_OPEN"))
	assert_eq(reserve[1]["hero"], &"")
	assert_eq(m.title(A), tr("FORMATION_MENU_ACTIVE_TITLE_FMT").format({"count": 3, "max": BattleEngine.MAX_ACTIVE}))
	assert_eq(m.place_text(A, 1), tr("FORMATION_MENU_PLACE_ACTIVE_FMT").format({"place": 2, "max": 3}))
	assert_eq(m.min_active, 1, "formation_menu.json rules: a battle needs one")
	_teardown()


func test_active_with_active_reorders_and_saves() -> void:
	var m := _model()
	var p := m.plan(A, 0, A, 2)
	assert_true(bool(p["ok"]))
	assert_eq(p["text"], tr("FORMATION_MENU_PLAN_SWAP_ACTIVE_FMT").format({"a": tr("CHAR_RHEN"), "b": tr("CHAR_TOMA")}))
	assert_eq(state.party_ids, ACTIVE, "a plan changes nothing")
	var done := m.move(A, 0, A, 2)
	assert_true(bool(done["ok"]))
	assert_eq(done["kind"], FormationMenuModel.KIND_SWAP_ACTIVE)
	assert_eq(state.party_ids, [&"toma", &"asha", &"rhen"] as Array[StringName], "saved at once")
	assert_eq(state.reserve_ids, RESERVE)
	_teardown()


func test_active_with_reserve_trades_places() -> void:
	var m := _model()
	var p := m.plan(R, 0, A, 1)
	var words := tr("FORMATION_MENU_PLAN_SWAP_IN_OUT_FMT").format({"in": tr("CHAR_YSOLDE"), "out": tr("CHAR_ASHA")})
	assert_eq(p["text"], words)
	assert_eq(m.plan(A, 1, R, 0)["text"], p["text"], "either way round, the same words")
	var done := m.move(A, 1, R, 0)
	assert_true(bool(done["ok"]))
	assert_eq(state.party_ids, [&"rhen", &"ysolde", &"toma"] as Array[StringName])
	assert_eq(state.reserve_ids, [&"asha"] as Array[StringName])
	assert_eq(PartyGoods.joined_members(state).size(), 4, "nobody lost or doubled")
	_teardown()


func test_open_places_take_a_hero_and_the_same_line_keeps() -> void:
	var m := _model()
	var to_reserve := m.move(A, 2, R, 1)
	assert_true(bool(to_reserve["ok"]))
	assert_eq(to_reserve["kind"], FormationMenuModel.KIND_TO_RESERVE)
	assert_eq(state.party_ids, [&"rhen", &"asha"] as Array[StringName])
	assert_eq(state.reserve_ids, [&"ysolde", &"toma"] as Array[StringName])
	assert_eq(m.rows(A).size(), BattleEngine.MAX_ACTIVE, "the third place is open")
	assert_eq(m.rows(A)[2]["label"], tr("FORMATION_MENU_OPEN"))
	var to_active := m.move(R, 0, A, 2)
	assert_eq(to_active["kind"], FormationMenuModel.KIND_TO_ACTIVE)
	assert_eq(to_active["text"], tr("FORMATION_MENU_DONE_TO_ACTIVE_FMT").format({"name": tr("CHAR_YSOLDE")}))
	assert_eq(state.party_ids, [&"rhen", &"asha", &"ysolde"] as Array[StringName])
	var keep := m.move(A, 0, A, 0)
	assert_eq(keep["kind"], FormationMenuModel.KIND_KEEP, "the same spot leaves them be")
	assert_eq(m.move(R, 0, R, 1)["kind"], FormationMenuModel.KIND_KEEP, "an open place in their own line too")
	assert_eq(state.party_ids, [&"rhen", &"asha", &"ysolde"] as Array[StringName])
	_teardown()


func test_refusals_are_in_words() -> void:
	state.party_ids = [&"rhen"] as Array[StringName]
	state.reserve_ids = [&"asha"] as Array[StringName]
	var m := _model()
	var open := m.plan(&"", -1, A, 1)
	assert_false(bool(open["ok"]))
	assert_eq(open["text"], tr("FORMATION_MENU_ERR_OPEN_PLACE"), "an open place cannot be picked")
	var few := m.move(A, 0, R, 1)
	assert_false(bool(few["ok"]))
	assert_eq(few["text"], tr("FORMATION_MENU_ERR_TOO_FEW_FMT").format({"min": 1, "name": tr("CHAR_RHEN")}))
	assert_eq(state.party_ids, [&"rhen"] as Array[StringName], "nothing changed")
	for code: StringName in FormationMenuModel.ERR_KEYS:
		var key := str(FormationMenuModel.ERR_KEYS[code])
		assert_ne(tr(key), key, "%s has words" % code)
	_teardown()


func test_nobody_standing_is_refused_but_a_fallen_hero_may_stand_with_a_warning() -> void:
	state.party_ids = [&"rhen", &"asha"] as Array[StringName]
	state.reserve_ids = [&"toma"] as Array[StringName]
	state.party_vitals = {"rhen": {"hp": 0}, "toma": {"hp": 0}}
	var m := _model()
	assert_true(m.is_fallen(&"rhen"))
	assert_eq(m.rows(A)[0]["label"], tr("FORMATION_MENU_FALLEN_TAG_FMT").format({"name": tr("CHAR_RHEN")}))
	var none := m.move(A, 1, R, 0)
	assert_false(bool(none["ok"]), "Toma (fallen) for Asha would leave nobody standing")
	assert_eq(none["text"], tr("FORMATION_MENU_ERR_NONE_STANDING"))
	var warn := m.plan(A, 0, A, 1)
	assert_true(bool(warn["ok"]), "a fallen hero may stand in the line")
	assert_eq(warn["warn"], tr("FORMATION_MENU_WARN_FALLEN_ONE_FMT").format({"name": tr("CHAR_RHEN")}))
	var pick := m.plan(&"", -1, A, 0)
	assert_eq(pick["warn"], warn["warn"], "picking a fallen hero in the line warns too")
	assert_eq(m.plan(&"", -1, A, 1)["warn"], "", "a standing hero does not")
	_teardown()


func test_nothing_changes_before_the_party_gathers() -> void:
	state.party_ids.clear()
	state.reserve_ids.clear()
	var m := FormationMenuModel.new(PartySheet.new(state, ACTIVE + RESERVE))
	assert_false(m.gathered())
	assert_eq(m.active, ACTIVE, "the stand-in: the sheet's heroes, the first places() active")
	assert_eq(m.reserve, RESERVE)
	var p := m.plan(&"", -1, A, 0)
	assert_false(bool(p["ok"]))
	assert_eq(p["text"], tr("FORMATION_MENU_ERR_NOT_GATHERED"))
	assert_false(bool(m.move(A, 0, R, 0)["ok"]))
	assert_true(state.party_ids.is_empty(), "the save is left alone")
	_teardown()


func test_a_broken_save_line_is_read_each_hero_once() -> void:
	state.party_ids = [&"rhen", &"asha", &"rhen", &"toma", &"ysolde"] as Array[StringName]
	state.reserve_ids = [&"asha"] as Array[StringName]
	var m := _model()
	assert_eq(m.active, [&"rhen", &"asha", &"toma"] as Array[StringName])
	assert_eq(m.reserve, [&"ysolde"] as Array[StringName], "past the places, to the reserve")
	_teardown()


# --- the view ------------------------------------------------------------------------------------


## M2-MNU-306: the hero under the cursor shows their role word under the name; an open place shows none.
func test_the_role_word_shows_under_the_name() -> void:
	_open()
	assert_eq(menu.role_text(), tr("ROLE_RHEN"), "Rhen first")
	assert_true(menu.place_line().begins_with(tr("ROLE_RHEN")), "it leads the place line")
	for hid: StringName in ACTIVE + RESERVE:
		assert_ne(menu.sheet.hero_role(hid), "", "%s has a role word" % hid)
	menu.handle_input(_ev(&"ui_right"))
	assert_eq(menu.role_text(), tr("ROLE_YSOLDE"), "the reserve's first")
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.role_text(), "", "an open place has no role")
	_teardown()


func test_keys_pick_then_swap_and_cancel_puts_back() -> void:
	_open()
	assert_eq(menu.focus, A)
	assert_eq(menu.current_hero(), &"rhen")
	assert_eq(menu.help_text(), tr("FORMATION_MENU_HELP"))
	assert_true(menu.list_page(A).is_cursor_shown())
	assert_false(menu.list_page(R).is_cursor_shown(), "only the list with the input shows its cursor")
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.chosen, {"line": A, "index": 0}, "Rhen is picked")
	assert_true(menu.chosen_frame().visible, "and framed")
	assert_eq(menu.chosen_text(), tr("FORMATION_MENU_CHOSEN_FMT").format({"name": tr("CHAR_RHEN")}))
	assert_eq(menu.help_text(), tr("FORMATION_MENU_HELP_PICKED"))
	menu.handle_input(_ev(&"ui_cancel"))
	assert_true(menu.chosen.is_empty(), "Cancel puts him back")
	assert_true(menu.is_open(), "and does not close")
	menu.handle_input(_ev(&"ui_accept"))
	menu.handle_input(_ev(&"ui_right"))
	assert_eq(menu.focus, R, "Right crosses to the reserve")
	assert_eq(menu.current_hero(), &"ysolde")
	assert_eq(
		menu.plan_text(),
		tr("FORMATION_MENU_PLAN_SWAP_IN_OUT_FMT").format({"in": tr("CHAR_YSOLDE"), "out": tr("CHAR_RHEN")})
	)
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(state.party_ids, [&"ysolde", &"asha", &"toma"] as Array[StringName], "saved")
	assert_eq(state.reserve_ids, [&"rhen"] as Array[StringName])
	assert_true(menu.chosen.is_empty())
	assert_eq(menu.current_hero(), &"rhen", "the cursor follows the moved hero")
	assert_eq(menu.list_page(A).rows[0]["label"], tr("CHAR_YSOLDE"), "the rows follow")
	assert_true(menu.plan_text().begins_with(tr("CHAR_YSOLDE")), "the result stays on the line")
	menu.handle_input(_ev(&"ui_left"))
	assert_eq(menu.focus, A)
	assert_eq(menu.plan_text(), menu.model.plan(&"", -1, A, 0)["text"], "moving clears the result")
	menu.handle_input(_ev(&"ui_cancel"))
	assert_false(menu.is_open(), "Cancel with nobody picked closes")
	_teardown()


func test_a_refusal_shows_in_danger_and_keeps_the_pick() -> void:
	state.party_ids = [&"rhen"] as Array[StringName]
	state.reserve_ids = [&"asha"] as Array[StringName]
	_open()
	menu.handle_input(_ev(&"ui_down"))
	menu.handle_input(_ev(&"ui_accept"))
	assert_true(menu.chosen.is_empty(), "an open place cannot be picked")
	assert_true(menu.plan_refused())
	assert_true(menu.is_refused(), "M2-AUD-15: audio can hear the refusal")
	assert_eq(menu.plan_text(), tr("FORMATION_MENU_ERR_OPEN_PLACE"))
	menu.handle_input(_ev(&"ui_up"))
	menu.handle_input(_ev(&"ui_accept"))
	menu.handle_input(_ev(&"ui_page_down"))
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.current_hero(), &"", "the reserve's open place")
	assert_true(menu.plan_refused(), "the plan already says no")
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.plan_text(), tr("FORMATION_MENU_ERR_TOO_FEW_FMT").format({"min": 1, "name": tr("CHAR_RHEN")}))
	assert_eq(menu.chosen, {"line": A, "index": 0}, "Rhen is still picked")
	assert_eq(state.party_ids, [&"rhen"] as Array[StringName])
	_teardown()


func test_the_mouse_hovers_either_list_and_clicks_to_move() -> void:
	_open()
	var reserve := menu.list_page(R)
	menu._on_hovered(0, R)
	assert_eq(menu.focus, R, "a hover over the reserve gives it the input")
	assert_true(reserve.is_cursor_shown())
	assert_false(menu.list_page(A).is_cursor_shown())
	menu._on_clicked(0, R)
	assert_eq(menu.chosen, {"line": R, "index": 0}, "a click picks")
	menu._on_clicked(2, A)
	assert_eq(state.party_ids, [&"rhen", &"asha", &"ysolde"] as Array[StringName], "a second click moves")
	assert_eq(state.reserve_ids, [&"toma"] as Array[StringName])
	_teardown()


func test_gauges_and_the_fallen_warning_show() -> void:
	state.party_vitals = {"asha": {"hp": 0}}
	_open()
	assert_eq(menu.row_gauges().size(), (ACTIVE.size() + RESERVE.size()) * 2, "HP and MP for each hero")
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.current_hero(), &"asha")
	assert_eq(menu.warn_text(), tr("FORMATION_MENU_WARN_FALLEN_ONE_FMT").format({"name": tr("CHAR_ASHA")}))
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.warn_text(), "")
	_teardown()


func test_the_detail_never_runs_past_the_panel_at_any_text_size() -> void:
	state.party_vitals = {"asha": {"hp": 0}, "rhen": {"hp": 0}}
	for scale: float in [1.0, 1.15, 1.3]:
		UiSettings.shared().set_value(UiSettings.TEXT_SCALE, scale)
		_open()
		menu.handle_input(_ev(&"ui_accept"))
		menu.handle_input(_ev(&"ui_down"))
		var pm: Dictionary = menu.load_layout().get("panel", {})
		var help_top := HudLayout.rect_of(pm).end.y - HudLayout.num(pm, "pad") - HudLayout.num(pm, "help_height")
		var y := 0.0
		for l: Label in [menu._name, menu._place, menu._chosen_line, menu._plan, menu._warn]:
			if not l.visible:
				continue
			assert_true(l.position.y >= y - 0.5, "%.2f: %s stacks under the line above" % [scale, l.text])
			y = l.position.y + l.size.y
		assert_true(y <= help_top + 0.5, "%.2f: the detail ends above the help line (%.1f)" % [scale, y])
		_teardown()
		UiSettings.set_shared(UiSettings.new())
	_teardown()


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
