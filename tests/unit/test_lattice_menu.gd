extends TestCase
## M2-MNU-01: the Lattice page (LatticeMenuModel, LatticeMenu, LatticeBoardView) on the real
## standard board and a scratch GameStateData: the words for every node, costs shown before anything
## is spent and spent exactly as cheapest_path's entry costs say, waking a node with its Facet,
## opening a gate with its Key, every refusal in words, the hero switch, keyboard and mouse input,
## and the refusal while the Lattice tables are broken. The runner has no after_each, so each test
## that opens the page tears it down itself (_teardown).

const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]

var menu: LatticeMenu


func before_each() -> void:
	menu = null


# --- the model: words ------------------------------------------------------------------------------


func test_every_node_kind_is_said_in_words() -> void:
	var m := _model()
	assert_eq(m.heroes(), HEROES, "every hero walks the standard board")
	assert_eq(m.hero(), &"rhen")
	assert_eq(m.position(), &"rhen_start")
	assert_eq(m.title(), tr("LATTICE_STANDARD"))
	var agility := tr("LATTICE_MENU_STAT_FMT").format({"stat": tr("STAT_AGILITY"), "n": 2})
	assert_eq(m.node_title(&"rh_01"), agility)
	assert_true(m.node_gives(&"rh_01").contains(tr("STAT_AGILITY")))
	assert_eq(m.node_title(&"rh_05"), tr("LATTICE_MENU_STAT_FMT").format({"stat": tr("LATTICE_MENU_STAT_HP"), "n": 40}))
	assert_eq(m.node_title(&"rh_03"), tr("SKILL_KICK_OFF"), "an ability node is its skill's name")
	assert_true(m.node_gives(&"rh_03").contains(tr("HUD_KIND_PHYSICAL")), "and says what the skill does")
	assert_eq(m.node_title(&"rh_07"), tr("LATTICE_MENU_GATE_FMT").format({"level": 1}))
	assert_eq(m.node_title(&"rhen_start"), tr("LATTICE_MENU_START_FMT").format({"name": tr("CHAR_RHEN")}))
	assert_eq(
		m.facet_line(&"rh_01"),
		tr("LATTICE_MENU_FACET_LINE_FMT").format({"need": 1, "facet": tr("FACET_SPEED"), "held": 0})
	)
	assert_eq(m.facet_line(&"rhen_start"), "", "a start needs no Facet")
	assert_eq(m.woken_line(&"rhen_start"), tr("LATTICE_MENU_WOKEN_BY_FMT").format({"names": tr("CHAR_RHEN")}))
	assert_eq(m.woken_line(&"rh_01"), tr("LATTICE_MENU_WOKEN_NOBODY"))
	assert_eq(m.woken_line(&"rh_07"), tr("LATTICE_MENU_GATE_SEALED"))
	assert_eq(m.node_state(&"rhen_start"), LatticeMenuModel.STATE_MINE)
	assert_eq(m.node_state(&"asha_start"), LatticeMenuModel.STATE_TRODDEN, "woken by someone else")
	assert_eq(m.node_state(&"rh_01"), LatticeMenuModel.STATE_NEW)
	assert_eq(m.node_state(&"rh_07"), LatticeMenuModel.STATE_GATE_CLOSED)
	assert_eq(m.facets_held_text(), tr("LATTICE_MENU_FACETS_NONE"))
	assert_eq(m.points_text(), tr("LATTICE_MENU_POINTS_FMT").format({"n": 0}))
	assert_eq(m.legend_rows().size(), 6)


func test_every_refusal_code_has_its_own_words() -> void:
	var m := _model()
	for cname: String in LatticeProgress.new().get_script().get_script_constant_map():
		if not cname.begins_with("ERR_"):
			continue
		var code: StringName = LatticeProgress.new().get_script().get_script_constant_map()[cname]
		assert_true(LatticeMenuModel.ERR_KEYS.has(code), "%s has words" % cname)
		var key := str(LatticeMenuModel.ERR_KEYS.get(code, ""))
		assert_ne(tr(key), key, "%s exists in a loc file" % key)
		var ctx := {"cost": 3, "have": 1, "facet": tr("FACET_POWER"), "need": 1, "held": 0}
		assert_false(m.error_text(code, ctx).contains("{"), "%s fills every field" % key)
	for stat: String in LatticeMenuModel.STAT_KEYS:
		var key := str(LatticeMenuModel.STAT_KEYS[stat])
		assert_ne(tr(key), key, key)


# --- the model: plans and actions ---------------------------------------------------------------------


func test_walking_costs_what_the_path_says_and_is_refused_without_movement() -> void:
	var m := _model()
	var p := m.plan(&"rh_03")
	assert_false(p["ok"], "no movement points yet")
	assert_eq(p["error"], LatticeProgress.ERR_NO_MOVEMENT)
	assert_eq(p["cost"], 3, "the cost is shown even when refused")
	assert_eq(p["text"], m.error_text(LatticeProgress.ERR_NO_MOVEMENT, {"cost": 3, "have": 0}))
	assert_false(m.act(&"rh_03")["ok"])
	assert_eq(m.position(), &"rhen_start", "nothing moved")
	m.traveler().movement_points = 5
	p = m.plan(&"rh_03")
	assert_true(p["ok"])
	assert_eq(p["action"], LatticeMenuModel.ACT_WALK)
	var path := m.progress().cheapest_path(&"rhen", &"rh_03")
	assert_eq(p["path"], path)
	var expect := 0
	for i in range(1, path.size()):
		expect += m.progress().entry_cost(path[i])
	assert_eq(p["cost"], expect, "the plan's cost is the sum of the path's entry costs")
	assert_eq(p["left"], 5 - expect)
	assert_eq(p["confirm"], tr("LATTICE_MENU_CONFIRM_WALK_FMT").format({"cost": expect}))
	var done := m.act(&"rh_03")
	assert_true(done["ok"])
	assert_eq(m.position(), &"rh_03")
	assert_eq(m.movement_points(), 5 - expect, "spent exactly that")
	var saved: Dictionary = (m.sheet.state.lattice["characters"] as Dictionary)["rhen"]
	assert_eq(saved["position"], "rh_03", "saved")
	assert_eq(saved["movement_points"], 5 - expect)
	var back := m.plan(&"rhen_start")
	assert_true(back["ok"])
	assert_eq(back["cost"], 2, "back over the unwoken nodes: rh_02 and rh_01 cost, the start is free")


func test_waking_a_node_spends_its_facet_and_saves() -> void:
	var m := _model({"facet_speed": 1})
	m.traveler().movement_points = 2
	assert_true(m.act(&"rh_01")["ok"])
	var p := m.plan(&"rh_01")
	assert_true(p["ok"])
	assert_eq(p["action"], LatticeMenuModel.ACT_ACTIVATE)
	assert_eq(p["confirm"], tr("LATTICE_MENU_CONFIRM_WAKE_FMT").format({"need": 1, "facet": tr("FACET_SPEED")}))
	var done := m.act(&"rh_01")
	assert_true(done["ok"])
	assert_true(m.progress().is_activated_by(&"rhen", &"rh_01"))
	assert_eq(m.facets().count(&"facet_speed"), 0, "the Facet is spent from the bag")
	assert_false(m.sheet.state.inventory.has("facet_speed"))
	var saved: Dictionary = (m.sheet.state.lattice["characters"] as Dictionary)["rhen"]
	assert_true((saved["activated"] as Array).has("rh_01"), "saved")
	assert_eq(m.node_state(&"rh_01"), LatticeMenuModel.STATE_MINE)
	assert_eq(m.plan(&"rh_01")["error"], LatticeProgress.ERR_ALREADY_ACTIVATED)
	assert_true(m.act(&"rh_02")["ok"])
	var refused := m.plan(&"rh_02")
	assert_eq(refused["error"], LatticeProgress.ERR_NO_FACET, "no Power Facet")
	assert_eq(
		refused["text"], m.error_text(LatticeProgress.ERR_NO_FACET, {"need": 1, "facet": tr("FACET_POWER"), "held": 0})
	)
	m.show_hero(&"asha")
	assert_eq(m.node_state(&"rh_01"), LatticeMenuModel.STATE_TRODDEN, "Asha sees Rhen's node as trodden")
	assert_eq(m.woken_line(&"rh_01"), tr("LATTICE_MENU_WOKEN_BY_FMT").format({"names": tr("CHAR_RHEN")}))


func test_a_gate_opens_from_beside_it_with_its_key() -> void:
	var m := _model()
	assert_eq(
		m.plan(&"rh_07")["error"], LatticeProgress.ERR_NO_MOVEMENT, "M2-MNU-10: far away it offers the walk, unpaid"
	)
	assert_eq(m.plan(&"rh_08")["error"], LatticeProgress.ERR_GATE_CLOSED, "no way past a sealed gate")
	m.traveler().movement_points = 6
	assert_true(m.act(&"rh_06")["ok"])
	assert_eq(m.plan(&"rh_07")["error"], LatticeProgress.ERR_NO_FACET, "no Key yet")
	m.facets().add(&"facet_key_1", 1)
	var p := m.plan(&"rh_07")
	assert_true(p["ok"])
	assert_eq(p["action"], LatticeMenuModel.ACT_OPEN)
	assert_true(m.act(&"rh_07")["ok"])
	assert_true(m.progress().is_gate_open(&"rh_07"))
	assert_eq(m.facets().count(&"facet_key_1"), 0)
	assert_true((m.sheet.state.lattice["opened_gates"] as Array).has("rh_07"), "saved")
	assert_eq(m.woken_line(&"rh_07"), tr("LATTICE_MENU_GATE_OPEN"))
	assert_eq(m.plan(&"rh_07")["cost"], 0, "an open gate is free to enter")


## M2-MNU-10: a sealed gate away from the hero offers the walk beside it first (its cost shown), and
## opens on the next Confirm; no new rules (cheapest_path, entry_cost, open_gate_error).
func test_a_far_sealed_gate_offers_the_walk_beside_it_then_opens() -> void:
	var m := _model({"facet_key_1": 1})
	var far := m.plan(&"rh_07")
	assert_false(far["ok"], "no movement points yet")
	assert_eq(far["error"], LatticeProgress.ERR_NO_MOVEMENT)
	assert_eq(far["beside"], &"rh_06", "the only neighbour Rhen can reach")
	assert_eq(far["cost"], 6)
	assert_eq(
		far["text"],
		tr("LATTICE_MENU_GATE_TOO_FAR_FMT").format({"cost": 6, "name": tr("CHAR_RHEN"), "have": 0}),
		"refused in words"
	)
	m.traveler().movement_points = 8
	var p := m.plan(&"rh_07")
	assert_true(p["ok"])
	assert_eq(p["action"], LatticeMenuModel.ACT_WALK, "first the walk")
	var expect: Array[StringName] = []
	var expect_cost := -1
	for nb in m.board().neighbors(&"rh_07"):
		var path := m.progress().cheapest_path(&"rhen", nb)
		if not path.is_empty() and (expect_cost < 0 or m.path_cost(path) < expect_cost):
			expect = path
			expect_cost = m.path_cost(path)
	assert_eq(p["path"], expect, "the cheapest reachable neighbour's cheapest path")
	assert_eq(p["cost"], expect_cost)
	assert_eq(p["left"], 8 - expect_cost)
	var ctx := {"cost": 6, "left": 2, "need": 1, "facet": tr("FACET_KEY_1"), "held": 1}
	assert_eq(
		p["text"],
		tr("LATTICE_MENU_PLAN_GATE_WALK_FMT").format(ctx) + " " + tr("LATTICE_MENU_PLAN_GATE_KEY_FMT").format(ctx)
	)
	assert_eq(p["confirm"], tr("LATTICE_MENU_CONFIRM_GATE_WALK_FMT").format(ctx))
	assert_true(m.act(&"rh_07")["ok"])
	assert_eq(m.position(), &"rh_06", "walked beside the gate")
	assert_eq(m.movement_points(), 2, "spent exactly the walk")
	assert_false(m.progress().is_gate_open(&"rh_07"), "not opened yet")
	assert_eq(m.facets().count(&"facet_key_1"), 1, "the Key is still held")
	assert_eq(m.plan(&"rh_07")["action"], LatticeMenuModel.ACT_OPEN, "then the opening")
	assert_true(m.act(&"rh_07")["ok"])
	assert_true(m.progress().is_gate_open(&"rh_07"))


func test_a_far_gate_says_when_no_key_is_held_or_no_way_reaches_it() -> void:
	var m := _model()
	m.traveler().movement_points = 8
	var p := m.plan(&"rh_07")
	assert_true(p["ok"], "the walk is still offered")
	var ctx := {"need": 1, "facet": tr("FACET_KEY_1"), "held": 0}
	assert_true(
		str(p["text"]).ends_with(tr("LATTICE_MENU_PLAN_GATE_NO_KEY_FMT").format(ctx)), "but says the Key is missing"
	)
	var none := m.plan(&"as_06")
	assert_false(none["ok"], "Asha's gate lies beyond Rhen's sealed gates")
	assert_eq(none["error"], LatticeProgress.ERR_GATE_CLOSED)
	assert_eq(none["text"], tr("LATTICE_MENU_GATE_NO_WAY"))


func test_confirm_on_a_far_gate_walks_then_opens_it() -> void:
	_open({"facet_key_1": 1})
	menu.model.traveler().movement_points = 8
	menu.set_cursor(&"rh_07", false)
	assert_eq(menu.board_view().path, menu.model.progress().cheapest_path(&"rhen", &"rh_06"), "the walk is drawn")
	assert_eq(menu.board_view().tag_text, tr("LATTICE_MENU_TAG_COST_FMT").format({"n": 6}))
	menu.handle_input(_ev(&"ui_accept"))
	assert_true(menu.is_confirming())
	assert_eq(menu.confirm_page().current_row()["label"], tr("LATTICE_MENU_CONFIRM_GATE_WALK_FMT").format({"cost": 6}))
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.model.position(), &"rh_06")
	assert_eq(menu.cursor, &"rh_07", "the cursor stays on the gate")
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(
		menu.confirm_page().current_row()["label"],
		tr("LATTICE_MENU_CONFIRM_OPEN_FMT").format({"need": 1, "facet": tr("FACET_KEY_1")}),
		"the second step opens it"
	)
	menu.handle_input(_ev(&"ui_accept"))
	assert_true(menu.model.progress().is_gate_open(&"rh_07"))
	_teardown()


func test_broken_tables_refuse_and_keep_the_save() -> void:
	var m := _model({"facet_speed": 1})
	m.traveler().movement_points = 3
	m.sheet.state.lattice = {"board": "standard", "characters": {}, "opened_gates": []}
	var before := m.sheet.state.lattice.duplicate(true)
	m.sheet.lattice.rules = LatticeRules.new()  # no Facets, a free step: integrity_problem
	assert_ne(m.broken_problem(), "")
	var p := m.plan(&"rh_01")
	assert_false(p["ok"])
	assert_eq(p["text"], tr("LATTICE_MENU_BROKEN"))
	assert_false(m.act(&"rh_01")["ok"])
	var path: Array[StringName] = [&"rhen_start", &"rh_01"]
	var walked := m.walk(path)
	assert_false(walked["ok"], "the save refused the change")
	assert_true(str(walked["text"]).ends_with(tr("LATTICE_MENU_SAVE_REFUSED")), "and says so")
	assert_eq(m.sheet.state.lattice, before, "saved progress kept as it was")


func test_the_cursor_steps_to_the_nearest_node_that_way() -> void:
	var m := _model()
	assert_eq(m.nearest_in_direction(&"rhen_start", Vector2.RIGHT, 0.42, 2.0), &"rh_01")
	assert_eq(m.nearest_in_direction(&"rhen_start", Vector2.LEFT, 0.42, 2.0), &"rp_01")
	assert_eq(m.nearest_in_direction(&"rh_02", Vector2.UP, 0.42, 2.0), &"rn_01")
	assert_eq(m.nearest_in_direction(&"rhen_start", Vector2.ZERO, 0.42, 2.0), &"rhen_start")


func test_no_hero_on_the_board_says_so() -> void:
	var m := LatticeMenuModel.new(PartySheet.new(GameStateData.new(), [&"no_such_hero"]))
	assert_eq(m.hero(), &"")
	assert_eq(m.plan(&"rh_01")["text"], tr("LATTICE_MENU_NO_HEROES"))


# --- the page --------------------------------------------------------------------------------------


func test_keys_move_the_cursor_and_confirm_shows_the_cost_before_walking() -> void:
	_open({})
	menu.model.traveler().movement_points = 3
	assert_eq(menu.cursor, &"rhen_start", "the cursor starts where the hero stands")
	assert_true(menu.handle_input(_ev(&"ui_right")))
	assert_eq(menu.cursor, &"rh_01")
	menu.handle_input(_ev(&"ui_right"))
	assert_eq(menu.cursor, &"rh_02")
	assert_eq(menu.board_view().path, menu.model.progress().cheapest_path(&"rhen", &"rh_02"), "the path is drawn")
	assert_eq(menu.board_view().tag_text, tr("LATTICE_MENU_TAG_COST_FMT").format({"n": 2}))
	assert_eq(menu.plan_text(), tr("LATTICE_MENU_PLAN_WALK_FMT").format({"cost": 2, "left": 1}))
	assert_eq(menu.side_texts()[3], menu.model.node_title(&"rh_02"))
	menu.handle_input(_ev(&"ui_accept"))
	assert_true(menu.is_confirming(), "a confirm before anything is spent")
	assert_eq(menu.confirm_page().current_row()["label"], tr("LATTICE_MENU_CONFIRM_WALK_FMT").format({"cost": 2}))
	assert_eq(menu.model.movement_points(), 3, "nothing spent yet")
	menu.handle_input(_ev(&"ui_cancel"))
	assert_false(menu.is_confirming(), "Cancel steps back from the confirm")
	assert_true(menu.is_open(), "and leaves the page open")
	menu.handle_input(_ev(&"ui_accept"))
	menu.handle_input(_ev(&"ui_down"))
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.model.position(), &"rhen_start", "Not now does nothing")
	menu.handle_input(_ev(&"ui_accept"))
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.model.position(), &"rh_02", "walked")
	assert_eq(menu.model.movement_points(), 1)
	assert_eq(
		menu.status_text(), tr("LATTICE_MENU_DONE_WALK_FMT").format({"name": tr("CHAR_RHEN"), "cost": 2, "left": 1})
	)
	menu.handle_input(_ev(&"ui_cancel"))
	assert_false(menu.is_open(), "Cancel closes the page")
	_teardown()


func test_a_refused_plan_opens_no_confirm_and_says_why() -> void:
	_open({})
	menu.set_cursor(&"rh_03", false)
	menu.handle_input(_ev(&"ui_accept"))
	assert_false(menu.is_confirming())
	assert_eq(menu.status_text(), menu.model.error_text(LatticeProgress.ERR_NO_MOVEMENT, {"cost": 3, "have": 0}))
	assert_false(menu.board_view().path_ok, "the path is drawn as refused")
	menu.set_cursor(&"rh_01")
	assert_eq(menu.status_text(), "", "moving the cursor clears the line")
	_teardown()


func test_page_keys_switch_the_hero() -> void:
	_open({})
	assert_true(menu.handle_input(_ev(&"ui_page_down")))
	assert_eq(menu.model.hero(), &"asha")
	assert_eq(menu.cursor, &"asha_start", "the cursor goes to where she stands")
	assert_eq(menu.side_texts()[1], tr("LATTICE_MENU_POINTS_FMT").format({"n": 0}))
	menu.handle_input(_ev(&"ui_page_up"))
	menu.handle_input(_ev(&"ui_page_up"))
	assert_eq(menu.model.hero(), &"toma", "it wraps")
	_teardown()


func test_a_click_puts_the_cursor_on_a_node_and_a_second_click_acts() -> void:
	_open({"facet_speed": 1})
	menu.model.traveler().movement_points = 1
	var view := menu.board_view()
	var at := view.screen_point(&"rh_01")
	assert_eq(view.node_at(at), &"rh_01")
	assert_eq(view.node_at(at + Vector2(1000.0, 1000.0)), &"", "nothing far from a node")
	_tap(view, at)
	assert_eq(menu.cursor, &"rh_01")
	assert_false(menu.is_confirming())
	_tap(view, at)
	assert_true(menu.is_confirming(), "the second click on it asks to walk there")
	menu.choose(0)
	assert_eq(menu.model.position(), &"rh_01")
	_tap(view, view.screen_point(&"rh_01"))
	assert_true(menu.is_confirming(), "standing on it, a click asks to wake it")
	assert_eq(
		menu.confirm_page().current_row()["label"],
		tr("LATTICE_MENU_CONFIRM_WAKE_FMT").format({"need": 1, "facet": tr("FACET_SPEED")})
	)
	menu.choose(0)
	assert_true(menu.model.progress().is_activated_by(&"rhen", &"rh_01"))
	assert_eq(menu.sheet.state.inventory.get("facet_speed", 0), 0)
	_teardown()


## Pillar 5 polish: a woken node blooms on the board (none under reduced motion), its Facet cost is on the
## cursor's tag before Confirm, and the drawn path marks which steps cost movement and which are free.
func test_waking_blooms_the_node_and_its_facet_cost_is_on_the_tag() -> void:
	_open({"facet_speed": 1})
	menu.model.traveler().movement_points = 1
	var view := menu.board_view()
	view.reduced_motion = false
	_tap(view, view.screen_point(&"rh_01"))
	_tap(view, view.screen_point(&"rh_01"))
	menu.choose(0)
	assert_false(view.is_waking(), "a walk does not bloom")
	_tap(view, view.screen_point(&"rh_01"))
	assert_eq(view.tag_text, tr("LATTICE_MENU_TAG_FACET_FMT").format({"n": 1, "facet": tr("FACET_SPEED")}))
	_tap(view, view.screen_point(&"rh_01"))
	menu.choose(0)
	assert_true(view.is_waking(), "the woken node blooms")
	assert_eq(view.waking, &"rh_01")
	view.finish_wake()
	assert_false(view.is_waking(), "and settles")
	_teardown()


func test_reduced_motion_wakes_without_a_bloom() -> void:
	_open({"facet_speed": 1})
	var view := menu.board_view()
	view.reduced_motion = true
	view.play_wake(&"rh_01")
	assert_false(view.is_waking())
	_teardown()


func test_the_path_marks_paid_and_free_steps() -> void:
	_open({})
	var view := menu.board_view()
	assert_true(view.is_paid_step(&"rh_01"), "nobody has woken it: the step costs")
	menu.model.progress().traveler(&"rhen").activated[&"rh_01"] = true
	assert_false(view.is_paid_step(&"rh_01"), "woken: the step is free")
	assert_eq(tr("LATTICE_MENU_TAG_COST_FMT").format({"n": 2}), "2 movement", "the tag names its unit")
	_teardown()


## M2-MNU-05: at every text size the side panel's lines, key, status line and confirm never overlap
## and stay inside the panel (they flow by measured height; the key shrinks or hides first).
func test_a_drag_is_readable_while_it_pans_and_ends_on_release() -> void:
	_open({})
	var view := menu.board_view()
	var at := view.screen_point(&"rh_01")
	assert_false(view.is_dragging())
	view._gui_input(_click(at))
	assert_false(view.is_dragging(), "a press alone is not a drag yet")
	var mm := InputEventMouseMotion.new()
	mm.button_mask = MOUSE_BUTTON_MASK_LEFT
	mm.position = at + Vector2(view._num("drag_px") * 4.0, 0.0)
	mm.relative = mm.position - at
	view._gui_input(mm)
	assert_true(view.is_dragging(), "M2-AUD-15: audio can hear a pan by hand")
	var up := _click(mm.position)
	up.pressed = false
	view._gui_input(up)
	assert_false(view.is_dragging(), "the release ends it")
	_teardown()


func test_the_side_panel_never_overlaps_at_any_text_size() -> void:
	var settings := UiSettings.shared()
	var was: Variant = settings.get_value(UiSettings.TEXT_SCALE)
	for scale: float in [1.0, 1.15, 1.3]:
		settings.set_value(UiSettings.TEXT_SCALE, scale)
		_open({"facet_ability": 1})
		menu.model.traveler().movement_points = 5
		menu.set_cursor(&"rh_05", false)
		_assert_no_overlap("x%s walk plan" % scale)
		menu.set_cursor(&"rh_07", false)
		menu.request_act()
		assert_ne(menu.status_text(), "", "a refusal on the status line")
		_assert_no_overlap("x%s refusal" % scale)
		menu.set_cursor(&"rh_03", false)
		menu.request_act()
		menu.choose(0)
		menu.request_act()
		assert_true(menu.is_confirming(), "walked onto Kick Off the Wall: the wake confirm")
		_assert_no_overlap("x%s confirm" % scale)
		menu.handle_input(_ev(&"ui_cancel"))
		menu.set_cursor(&"rh_02", false)
		menu.request_act()
		menu.choose(0)
		assert_ne(menu.status_text(), "", "a result on the status line")
		_assert_no_overlap("x%s result" % scale)
		_teardown()
	settings.set_value(UiSettings.TEXT_SCALE, was)


func _assert_no_overlap(what: String) -> void:
	var side := HudLayout.rect_of(menu.load_layout().get("side", {}))
	var rects := menu.side_rects()
	assert_true(rects.size() >= 5, "%s: the lines are laid out" % what)
	for i in rects.size():
		assert_true(side.encloses(rects[i]), "%s: %s inside the panel %s" % [what, rects[i], side])
		for j in range(i + 1, rects.size()):
			assert_false(rects[i].intersects(rects[j]), "%s: %s overlaps %s" % [what, rects[i], rects[j]])


## M3-MNU-04: the overview fits every node in the board view, keeps the cursor, the side panel and
## the actions, and toggling back returns to the cursor view on the same node.
func test_the_overview_fits_the_whole_board_and_returns_to_the_cursor() -> void:
	_open({})
	menu.model.traveler().movement_points = 3
	menu.set_cursor(&"rh_02", false)
	var view := menu.board_view()
	var texts := menu.side_texts()
	assert_eq(view.zoom, 1.0)
	assert_eq(menu.overview_button().text, tr("LATTICE_MENU_OVERVIEW_FMT").format({"key": "M"}))
	menu.toggle_overview(false)
	assert_true(menu.is_overview())
	assert_eq(view.zoom, view.fit_zoom(), "the fit zoom")
	assert_true(view.zoom < 1.0 and view.zoom >= view.zoom_min(), "held inside the wheel's range")
	var inside := Rect2(Vector2.ZERO, view.size)
	for nid: StringName in menu.model.board().nodes:
		assert_true(inside.has_point(view.screen_point(nid)), "%s is in view" % nid)
	assert_eq(menu.cursor, &"rh_02", "the cursor stays")
	assert_eq(menu.side_texts(), texts, "and so does its panel")
	assert_eq(menu.overview_button().text, tr("LATTICE_MENU_OVERVIEW_BACK_FMT").format({"key": "M"}))
	var framed := view.pan
	menu.handle_input(_ev(&"ui_right"))
	assert_eq(menu.cursor, &"rh_03")
	assert_eq(view.pan, framed, "the board stays framed as the cursor moves")
	menu.handle_input(_ev(&"ui_accept"))
	assert_true(menu.is_confirming(), "actions work in the overview")
	menu.handle_input(_ev(&"ui_cancel"))
	menu.handle_input(_ev(LatticeMenu.OVERVIEW_ACTION))
	assert_eq(menu.is_overview(), false, "the action toggles it back")
	_teardown()


func test_back_from_the_overview_is_the_cursor_view_on_the_same_node() -> void:
	_open({})
	var view := menu.board_view()
	menu.set_cursor(&"rh_05", false)
	var near_pan := view.pan
	menu.toggle_overview(false)
	menu.toggle_overview(false)
	assert_eq(view.zoom, 1.0)
	assert_eq(view.pan, near_pan, "the same framing as before")
	menu.toggle_overview(false)
	menu.set_cursor(&"rh_01", false)
	menu.toggle_overview(false)
	var fresh := LatticeMenu.create(PartySheet.new(GameStateData.new(), HEROES))
	fresh.pause_tree = false
	_root().add_child(fresh)
	fresh.set_cursor(&"rh_01", false)
	assert_eq(view.pan, fresh.board_view().pan, "back on the node the cursor moved to")
	fresh.close()
	fresh.get_parent().remove_child(fresh)
	fresh.free()
	_teardown()


func test_a_wheel_turn_leaves_the_overview_and_reduced_motion_snaps() -> void:
	var settings := UiSettings.shared()
	var was: Variant = settings.get_value(UiSettings.REDUCED_MOTION)
	settings.set_value(UiSettings.REDUCED_MOTION, true)
	_open({})
	var view := menu.board_view()
	menu.toggle_overview()  # animated if it could be: reduced motion snaps
	assert_eq(view.zoom, view.fit_zoom(), "no tween: already there")
	var wheel := InputEventMouseButton.new()
	wheel.button_index = MOUSE_BUTTON_WHEEL_UP
	wheel.pressed = true
	wheel.position = view.size * 0.5
	view._gui_input(wheel)
	assert_false(menu.is_overview(), "the player took the camera")
	assert_eq(menu.overview_button().text, tr("LATTICE_MENU_OVERVIEW_FMT").format({"key": "M"}))
	_teardown()
	settings.set_value(UiSettings.REDUCED_MOTION, was)


func test_the_overview_names_who_woke_each_node() -> void:
	var m := _model({"facet_speed": 1})
	m.traveler().movement_points = 1
	m.act(&"rh_01")
	m.act(&"rh_01")
	assert_eq(m.woken_initials(&"rh_01"), tr("CHAR_RHEN").left(1))
	assert_eq(m.woken_initials(&"rh_02"), "", "nobody woke it")
	assert_eq(m.woken_initials(&"asha_start"), tr("CHAR_ASHA").left(1), "a start is its owner's")
	assert_true(InputMap.has_action(LatticeMenu.OVERVIEW_ACTION) or _ensured(), "the action exists")


## The overview's name tags: one per hero, the hero on show framed in gold, none overlapping (tags on a
## shared node stack); initials that would touch a tag are left off in _draw_overview_words.
func test_the_overview_tags_name_every_hero_apart() -> void:
	_open({})
	menu.toggle_overview(false)
	var tags := menu.board_view().overview_tags()
	assert_eq(tags.size(), menu.model.heroes().size())
	var gold := 0
	for i in tags.size():
		gold += (
			1
			if (tags[i]["edge"] as Color).is_equal_approx(
				menu.get_theme_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE)
			)
			else 0
		)
		for j in range(i + 1, tags.size()):
			assert_false(
				(tags[i]["box"] as Rect2).intersects(tags[j]["box"] as Rect2),
				"%s and %s apart" % [tags[i]["text"], tags[j]["text"]]
			)
	assert_eq(gold, 1, "only the hero on show in gold")
	_teardown()


func _ensured() -> bool:
	LatticeMenu.ensure_action()
	return InputMap.has_action(LatticeMenu.OVERVIEW_ACTION)


func _model(facets: Dictionary = {}) -> LatticeMenuModel:
	var state := GameStateData.new()
	state.inventory = facets.duplicate()
	return LatticeMenuModel.new(PartySheet.new(state, HEROES))


func _open(facets: Dictionary) -> void:
	var state := GameStateData.new()
	state.inventory = facets.duplicate()
	menu = LatticeMenu.create(PartySheet.new(state, HEROES))
	menu.pause_tree = false
	_root().add_child(menu)


func _teardown() -> void:
	if menu != null and is_instance_valid(menu):
		menu.close()
		menu.get_parent().remove_child(menu)
		menu.free()
	menu = null


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


## A click on the board: press and release (a click acts on release, so a press can become a drag).
func _tap(view: LatticeBoardView, at: Vector2) -> void:
	var ev := _click(at)
	view._gui_input(ev)
	ev = ev.duplicate() as InputEventMouseButton
	ev.pressed = false
	view._gui_input(ev)


func _click(at: Vector2) -> InputEventMouseButton:
	var ev := InputEventMouseButton.new()
	ev.button_index = MOUSE_BUTTON_LEFT
	ev.pressed = true
	ev.position = at
	return ev
