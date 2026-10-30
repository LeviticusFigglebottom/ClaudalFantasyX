extends TestCase
## M2-UI-04: the field menu (FieldMenuModel, FieldMenu): opened from the field with ui_cancel, it
## pauses the tree, opens the bestiary, and sets each hero's Swell fill mode out of battle
## (BattleSwellCarry) on a scratch GameStateData. Also the target info panel's "revealed" for a
## foe the party has already Read (BattleBestiary.knows).

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const ZONE := "res://game/levels/_tests/field/field_test.tscn"
const NAMES := {&"rhen": "CHAR_RHEN", &"asha": "CHAR_ASHA", &"toma": "CHAR_TOMA"}

var menu: FieldMenu
var ctl: BattleController


func before_each() -> void:
	menu = null
	ctl = null


# --- the model -----------------------------------------------------------------------------------


func test_the_root_names_its_rows_and_swell_is_off_without_a_swell_hero() -> void:
	var m := _model([&"rhen"])
	var rows := m.root_rows()
	assert_eq(rows.size(), FieldMenuModel.ROOT_IDS.size(), "a row for each id")
	assert_eq(
		rows.size(),
		12,
		"M2-MNU-01..04 Items, Equip, Lattice, Status, Quit; M2-UI-18 Map; M2-MNU-07 Formation; M3-UI-03 Codex"
	)
	assert_eq(rows[_at(FieldMenuModel.ROW_FORMATION)]["label"], tr("FIELD_MENU_FORMATION"), "M2-MNU-07")
	assert_eq(_at(FieldMenuModel.ROW_FORMATION), _at(FieldMenuModel.ROW_STATUS) + 1, "Formation follows Status")
	assert_eq(rows[_at(FieldMenuModel.ROW_CODEX)]["label"], tr("FIELD_MENU_CODEX"), "M3-UI-03")
	assert_eq(rows[_at(FieldMenuModel.ROW_MAP)]["label"], tr("FIELD_MENU_MAP"), "M2-UI-18")
	assert_eq(rows[_at(FieldMenuModel.ROW_BESTIARY)]["label"], tr("FIELD_MENU_BESTIARY"))
	assert_eq(rows[_at(FieldMenuModel.ROW_SWELL)]["label"], tr("FIELD_MENU_SWELL"))
	assert_eq(rows[_at(FieldMenuModel.ROW_SETTINGS)]["label"], tr("FIELD_MENU_SETTINGS"), "M2-UI-09")
	assert_eq(rows[rows.size() - 1]["label"], tr("FIELD_MENU_CLOSE"), "Close stays last")
	assert_true(rows[_at(FieldMenuModel.ROW_SWELL)]["enabled"])
	assert_eq(m.root_desc(FieldMenuModel.ROW_BESTIARY), tr("FIELD_MENU_BESTIARY_DESC"))
	var nobody := _model([&"no_such_hero"])
	assert_false(nobody.root_rows()[_at(FieldMenuModel.ROW_SWELL)]["enabled"], "no Swell hero: the row is off")
	assert_eq(nobody.root_desc(FieldMenuModel.ROW_SWELL), tr("FIELD_MENU_SWELL_NONE"), "and says why")


func test_hero_rows_show_the_mode_in_use_and_mode_rows_carry_name_and_desc_keys() -> void:
	var m := _model([&"rhen", &"asha", &"rhen"])
	var heroes := m.hero_rows()
	assert_eq(heroes.size(), 2, "each hero once, in party order")
	assert_eq(heroes[0]["label"], tr("CHAR_RHEN"))
	assert_eq(heroes[0]["right"], tr("SWELL_MODE_BALLAST"), "the default mode")
	var rows := m.mode_rows(&"rhen")
	assert_true(rows.size() >= 2)
	for r in rows:
		assert_ne(str(r["name_key"]), "", "a name_key")
		assert_ne(str(r["desc_key"]), "", "a desc_key")
	var page := m.mode_page_rows(&"rhen")
	assert_eq(page[0]["label"], tr("SWELL_MODE_BALLAST"))
	assert_eq(page[0]["right"], tr("HUD_SWELL_MODE_IN_USE"), "the current mode says so in words")
	assert_eq(page[1]["right"], "")
	assert_eq(
		m.mode_desc(&"rhen", &"wake"),
		tr("FIELD_MENU_SWELL_MODE_FMT").format({"mode": tr("SWELL_MODE_WAKE"), "desc": tr("SWELL_MODE_WAKE_DESC")})
	)
	assert_true(m.mode_desc(&"rhen", &"ballast").begins_with(tr("SWELL_MODE_BALLAST")))
	assert_true(m.hero_desc(&"rhen").contains(tr("SWELL_MODE_BALLAST_DESC")))


func test_choosing_a_mode_saves_it_and_a_locked_mode_is_refused() -> void:
	var m := _model([&"rhen"])
	var line := m.choose_mode(&"rhen", &"wake")
	assert_eq(line, tr("FIELD_MENU_SWELL_SET_FMT").format({"name": tr("CHAR_RHEN"), "mode": tr("SWELL_MODE_WAKE")}))
	assert_eq(m.state.swell_mode_of(&"rhen", &"ballast"), &"wake", "saved in the state")
	assert_eq(m.hero_rows()[0]["right"], tr("SWELL_MODE_WAKE"))
	assert_eq(m.choose_mode(&"rhen", &"tether"), "", "not unlocked yet")
	assert_eq(m.state.swell_mode_of(&"rhen", &"ballast"), &"wake", "nothing changed")
	var unlocked := _model([&"rhen"])
	unlocked.state.swell = {"unlocked": ["ballast", "wake", "tether"]}
	assert_eq(unlocked.mode_page_rows(&"rhen").size(), 3, "an unlocked mode is listed")
	assert_ne(unlocked.choose_mode(&"rhen", &"tether"), "")


func test_from_game_uses_the_joined_party_or_the_first_playable_one() -> void:
	var saved := Game.state
	Game.state = GameStateData.new()
	var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_FIELD_BATTLE)
	var expect := FirstPlayableConfig.ids(cfg["active"]) + FirstPlayableConfig.ids(cfg["reserve"])
	var m := FieldMenuModel.from_game()
	assert_eq(m.heroes, expect, "no one joined yet: the first playable's party")
	assert_true(m.state == Game.state, "the live save")
	Game.state.party_ids = [&"asha"] as Array[StringName]
	assert_eq(FieldMenuModel.from_game().heroes, [&"asha"] as Array[StringName])
	assert_eq(FieldMenuModel.from_game().hero_name(&"asha"), tr("CHAR_ASHA"))
	Game.state = saved


# --- the view ------------------------------------------------------------------------------------


func test_it_pauses_the_tree_and_cancel_closes_and_unpauses() -> void:
	_open(true)
	var tree := menu.get_tree()
	assert_true(tree.paused, "the field stops under the menu")
	assert_eq(menu.help_text(), tr("FIELD_MENU_HELP_ROOT"))
	assert_eq(menu.desc_text(), tr("FIELD_MENU_ITEMS_DESC"))
	var closed := [false]
	menu.closed.connect(func() -> void: closed[0] = true)
	assert_true(menu.handle_input(_ev(&"ui_cancel")))
	assert_true(closed[0])
	assert_false(menu.is_open())
	assert_false(tree.paused, "and moves again after")
	assert_false(menu.handle_input(_ev(&"ui_down")), "closed: it takes nothing")
	_free()


func test_the_swell_path_sets_a_mode_and_cancel_walks_back() -> void:
	_open()
	for i in _at(FieldMenuModel.ROW_SWELL):
		assert_true(menu.handle_input(_ev(&"ui_down")))
	assert_eq(menu.desc_text(), tr("FIELD_MENU_SWELL_DESC"))
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.level, FieldMenu.Level.HEROES)
	assert_true(menu.detail_page().visible)
	assert_eq(menu.help_text(), tr("FIELD_MENU_HELP_HEROES"))
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.detail_page().current_row()["id"], &"asha")
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.level, FieldMenu.Level.MODES)
	assert_eq(menu.hero, &"asha")
	assert_eq(menu.detail_page().current_row()["id"], &"ballast", "the cursor starts on the mode in use")
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.desc_text(), menu.model.mode_desc(&"asha", &"wake"), "the highlighted mode's desc_key")
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.model.state.swell_mode_of(&"asha"), &"wake", "saved")
	assert_eq(menu.detail_page().rows[1]["right"], tr("HUD_SWELL_MODE_IN_USE"), "the row says so")
	assert_eq(menu.detail_page().rows[0]["right"], "")
	assert_true(menu.desc_text().contains(tr("SWELL_MODE_WAKE")), "and the line confirms it")
	menu.handle_input(_ev(&"ui_cancel"))
	assert_eq(menu.level, FieldMenu.Level.HEROES)
	assert_eq(menu.detail_page().current_row()["id"], &"asha", "back on the same hero")
	assert_eq(menu.detail_page().current_row()["right"], tr("SWELL_MODE_WAKE"))
	menu.handle_input(_ev(&"ui_cancel"))
	assert_eq(menu.level, FieldMenu.Level.ROOT)
	assert_false(menu.detail_page().visible)
	assert_true(menu.is_open())
	_free()


func test_the_bestiary_opens_over_it_and_hands_back_on_cancel() -> void:
	_open(true)
	var tree := menu.get_tree()
	menu.root_page().set_cursor(_at(FieldMenuModel.ROW_BESTIARY), false)  # Down skips the Map row (off here)
	menu.handle_input(_ev(&"ui_accept"))
	var b := menu.bestiary
	assert_true(b != null and b.is_open(), "Bestiary opens BestiaryMenu")
	assert_false(menu.visible, "the field menu steps aside")
	assert_true(b.is_visible_in_tree(), "the bestiary is on show on its own layer")
	assert_false(menu.handle_input(_ev(&"ui_down")), "the bestiary takes the input")
	assert_true(b.handle_input(_ev(&"ui_cancel")))
	assert_true(menu.bestiary == null)
	assert_true(menu.visible)
	assert_true(tree.paused, "still paused: the field menu holds the pause")
	assert_true(menu.handle_input(_ev(&"ui_cancel")))
	assert_false(tree.paused)
	_free()


func test_close_row_and_clicks_choose() -> void:
	_open()
	menu._on_clicked(_at(FieldMenuModel.ROW_CLOSE), FieldMenu.Level.ROOT)
	assert_false(menu.is_open(), "Return to the path closes it")
	_free()
	_open()
	menu._on_clicked(_at(FieldMenuModel.ROW_SWELL), FieldMenu.Level.ROOT)
	assert_eq(menu.level, FieldMenu.Level.HEROES, "a click on Swell opens the heroes")
	menu._on_clicked(0, FieldMenu.Level.HEROES)
	assert_eq(menu.level, FieldMenu.Level.MODES)
	menu._on_clicked(_at(FieldMenuModel.ROW_BESTIARY), FieldMenu.Level.ROOT)
	assert_true(menu.bestiary != null, "a click on the root goes back to it and chooses")
	menu.close()
	assert_true(menu.bestiary == null or not menu.bestiary.is_open(), "closing closes the bestiary too")
	_free()


func test_open_in_brings_its_own_layer_under_the_bestiary_s() -> void:
	var host := Node.new()
	_root().add_child(host)
	var m := FieldMenu.open_in(host, _model([&"rhen"]))
	var layer := m.get_parent() as CanvasLayer
	assert_true(layer != null, "on a CanvasLayer")
	assert_eq(layer.layer, int(FieldMenu.load_data()["canvas_layer"]))
	assert_true(layer.layer < int(BestiaryMenu.load_data()["canvas_layer"]), "the bestiary draws over it")
	m.close()
	m.motion().finish()  # M2-MNU-303: the layer goes once the menu has faded out
	assert_true(layer.is_queued_for_deletion())
	host.get_tree().paused = false
	_root().remove_child(host)
	host.free()


func test_the_field_opens_it_on_cancel_unless_input_is_off() -> void:
	var zone := (load(ZONE) as PackedScene).instantiate() as Node3D
	_root().add_child(zone)
	var player := zone.get_node("Player") as FieldController
	player.set_physics_process(false)
	player.accepts_input = false
	player._unhandled_input(_ev(FieldMenu.OPEN_ACTION))
	assert_eq(_menus_under(player).size(), 0, "a cutscene holds the player: no menu")
	player.accepts_input = true
	player._unhandled_input(_ev(FieldMenu.OPEN_ACTION))
	var found := _menus_under(player)
	assert_eq(found.size(), 1, "Escape opens the field menu")
	assert_true(zone.get_tree().paused)
	found[0].close()
	assert_false(zone.get_tree().paused)
	zone.get_tree().paused = false
	_root().remove_child(zone)
	zone.free()


# --- the target info panel (M2-UI-02 follow-up) --------------------------------------------------


func test_the_target_panel_shows_hp_for_a_foe_already_read() -> void:
	_sandbox()
	var eel := ctl.engine.find(&"lantern_eel#2")
	var crab: BattleCombatant = null
	for e in ctl.engine.enemies:
		if BattleEngine.enemy_id(e) != &"lantern_eel":
			crab = e
	assert_false(ctl.bestiary.knows(eel), "not Read yet")
	ctl.bestiary.book.record_read(&"lantern_eel")
	assert_true(ctl.bestiary.knows(eel), "Read: known")
	assert_false(ctl.bestiary.knows(crab), "another kind is not")
	assert_false(ctl.bestiary.knows(ctl.engine.party_active[0]), "the party is never 'known' this way")
	ctl.handle_input(_ev(&"ui_accept"))  # Attack: the target pick
	assert_eq(ctl.state, BattleController.STATE_TARGET)
	var seen := {}
	for i in ctl.engine.enemies.size():
		var picked := ctl.engine.find(ctl.picked_ids()[0])
		var cursor := ctl.hud.target_cursor
		seen[BattleEngine.enemy_id(picked)] = [cursor._info_hp.visible, cursor._info_note.visible]
		ctl.handle_input(_ev(&"ui_right"))
	assert_eq(seen[&"lantern_eel"], [true, false], "a Read foe shows its HP, no 'unknown until Read'")
	assert_eq(seen[BattleEngine.enemy_id(crab)], [false, true], "an unread foe still says HP is unknown")
	_free_ctl()


func test_a_read_this_battle_reveals_the_foe_in_the_target_panel() -> void:
	_sandbox()
	var guard := 0
	while ctl.current_actor_id() != &"ysolde" and guard < CtbTimeline.PREVIEW_LENGTH:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	var eel := ctl.engine.find(&"lantern_eel#2")
	assert_false(ctl.bestiary.knows(eel))
	assert_true(ctl.act(&"read", [eel.id]).ok)
	assert_true(ctl.bestiary.knows(eel), "the Read is logged for the target panel")
	_free_ctl()


# --- helpers -------------------------------------------------------------------------------------


func _at(row: StringName) -> int:
	return FieldMenuModel.ROOT_IDS.find(row)


func test_at_the_largest_text_nothing_on_the_root_overlaps() -> void:
	# The Act I UI pass of 2026-10-30: at 130 % the card names sat on the HP rows and the objective ran into the help.
	var was := UiSettings.shared()
	var big := UiSettings.new()
	big.set_value(UiSettings.TEXT_SCALE, 1.3)
	UiSettings.set_shared(big)
	_open()
	var objective: Label = menu.get(&"_objective")
	var help: Label = menu.get(&"_help")
	var bottom := objective.position.y + objective.get_combined_minimum_size().y
	assert_true(
		bottom <= help.position.y + 0.5, "the objective ends above the help (%s > %s)" % [bottom, help.position.y]
	)
	for card: PartyCard in menu.party_cards():
		if not card.visible:
			continue
		var name_label: Label = card.get(&"_name")
		var hp_head: Label = (card.get(&"_heads") as Array)[0]
		var slot := float((FieldMenu.load_data().get("party", {}) as Dictionary).get("line_height", 0.0)) * 1.3
		assert_true(hp_head.position.y - name_label.position.y >= slot - 0.5, "the name's line grows with the text")
		assert_true(hp_head.position.y + hp_head.size.y <= card.size.y, "the rows stay on the card")
	_free()
	UiSettings.set_shared(was)


func _model(heroes: Array[StringName]) -> FieldMenuModel:
	return FieldMenuModel.new(GameStateData.new(), heroes, NAMES)


func _open(pause: bool = false) -> void:
	menu = (load(FieldMenu.SCENE_PATH) as PackedScene).instantiate() as FieldMenu
	menu.pause_tree = pause
	menu.configure(_model([&"rhen", &"asha", &"toma"]))
	_root().add_child(menu)


func _menus_under(n: Node) -> Array[FieldMenu]:
	var out: Array[FieldMenu] = []
	for child in n.get_children():
		if child is CanvasLayer:
			for m in child.get_children():
				if m is FieldMenu:
					out.append(m as FieldMenu)
	return out


func _sandbox() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	_root().add_child(ctl)
	ctl.hud.apply_settings(UiSettings.new())
	ctl.start_fixture(BattleFixture.load_fixture(&"read_panel"))


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


func _free() -> void:
	if menu != null:
		if menu.get_tree() != null:
			menu.get_tree().paused = false
		for child in menu.get_children():
			if child is CanvasLayer:
				child.free()
		menu.get_parent().remove_child(menu)
		menu.free()
		menu = null


func _free_ctl() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
	ctl = null
