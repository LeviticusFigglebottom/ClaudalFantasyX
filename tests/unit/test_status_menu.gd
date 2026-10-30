extends TestCase
## M2-MNU-03: the party Status page (StatusMenuModel, StatusMenu) over a PartySheet on a scratch
## GameStateData: the stat split (base + Lattice + gear) adds up to PartySheet.combatant, the gear,
## Swell, Lattice and carried-status words, and the view's input (ui_*, wheel and mouse). The runner
## has no after_each: each test that opens the view frees it itself (_teardown).

const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]

var state: GameStateData
var menu: StatusMenu


func before_each() -> void:
	state = GameStateData.new()
	state.party_ids = HEROES.duplicate()
	state.swell = {"unlocked": ["ballast", "wake"]}
	menu = null


func test_the_split_adds_up_to_the_battle_build() -> void:
	var sheet := _dressed_sheet()
	var m := StatusMenuModel.new(sheet)
	var now := sheet.combatant(&"rhen")
	var base := sheet.base_combatant(&"rhen")
	var rows := m.stat_rows(&"rhen")
	assert_eq(rows.size(), StatusMenuModel.VITAL_STATS.size() + StatusMenuModel.STATS.size())
	var grew_lattice := false
	var grew_gear := false
	for r in rows:
		var stat: StringName = r["id"]
		assert_eq(int(r["total"]), int(now.get(stat)), "%s total is the battle's" % stat)
		assert_eq(int(r["base"]) + int(r["lattice"]) + int(r["gear"]), int(r["total"]), "%s adds up" % stat)
		assert_eq(int(r["base"]), int(base.get(stat)), "%s base is characters.json" % stat)
		assert_eq(r["label"], tr(StatusMenuModel.STAT_KEYS[stat]))
		grew_lattice = grew_lattice or int(r["lattice"]) > 0
		grew_gear = grew_gear or int(r["gear"]) > 0
	assert_true(grew_lattice, "the woken nodes show")
	assert_true(grew_gear, "and the gear")
	var strength := rows[StatusMenuModel.VITAL_STATS.size()]
	assert_eq(strength["id"], &"strength")
	assert_eq(int(strength["gear"]), 4, "Coral-Bitten Hooks +1 and Steady Arm +3")
	assert_eq(m.growth_text(4), tr("STATUS_MENU_PLUS_FMT").format({"amount": 4}))
	assert_eq(m.growth_text(0), tr("STATUS_MENU_ZERO"))


func test_the_page_says_gear_swell_lattice_and_carried_statuses() -> void:
	state.party_vitals = {"rhen": {"hp": 100, "swell": 46, "swell_mode": "wake", "statuses": ["poison"]}}
	var sheet := _dressed_sheet()
	var m := StatusMenuModel.new(sheet)
	var p := m.page(&"rhen")
	assert_eq(p["name"], tr("CHAR_RHEN"))
	assert_eq(p["hp"], 100)
	assert_eq(p["max_hp"], sheet.combatant(&"rhen").max_hp)
	assert_false(p["fallen"])
	var gear: Array = p["gear"]
	assert_eq(gear[0]["slot_label"], tr("STATUS_MENU_WEAPON"))
	assert_eq(gear[0]["name"], tr("EQUIP_RHEN_CORAL_HOOKS"))
	assert_eq(gear[0]["abilities"], tr("ABILITY_EMBER_EDGE") + tr("ITEMS_MENU_LIST_JOIN") + tr("ABILITY_STEADY_ARM"))
	assert_eq(gear[1]["name"], tr("STATUS_MENU_EMPTY_SLOT"), "no armor worn")
	var sw: Dictionary = p["swell"]
	assert_true(sw["has"])
	assert_eq(sw["points"], 46)
	assert_eq(sw["mode"], &"wake")
	assert_eq(sw["text"], tr("STATUS_MENU_SWELL_FMT").format({"mode": tr("SWELL_MODE_WAKE"), "points": 46, "max": 100}))
	var lat: Dictionary = p["lattice"]
	assert_eq(lat["movement"], 3)
	assert_eq(lat["woken"], 2, "the start does not count")
	assert_eq((lat["lines"] as Array)[0], tr("STATUS_MENU_MOVEMENT_FMT").format({"count": 3}))
	assert_eq((lat["lines"] as Array)[1], tr("STATUS_MENU_WOKEN_FMT").format({"count": 2}))
	assert_eq(p["statuses"], [tr("STATUS_POISON")] as Array[String])
	assert_eq(p["status_descs"], ["%s: %s" % [tr("STATUS_POISON"), tr("STATUS_POISON_DESC")]] as Array[String])
	var asha := m.page(&"asha")
	assert_eq(asha["statuses"], [tr("STATUS_MENU_NONE")] as Array[String])
	assert_true((asha["status_descs"] as Array).is_empty(), "nothing carried, nothing to explain")
	assert_eq((asha["swell"] as Dictionary)["mode"], &"ballast", "no saved mode: swell.json's default")
	assert_eq((asha["swell"] as Dictionary)["points"], 0)
	assert_true(m.page(&"nobody").is_empty())


## The Lead's Act I pass: every status a fight can leave on a hero says what it does (STATUS_<ID>_DESC).
func test_every_status_has_a_description() -> void:
	var rows: Dictionary = BattleDB.load_default().statuses
	assert_true(rows.size() > 10)
	for sid: Variant in rows:
		var key := str((rows[sid] as Dictionary).get("name_key", "")) + StatusMenuModel.DESC_SUFFIX
		assert_ne(tr(key), key, "%s has a description (%s)" % [sid, key])


func test_a_fallen_hero_says_so() -> void:
	state.party_vitals = {"toma": {"hp": 0}}
	var m := StatusMenuModel.new(PartySheet.new(state, HEROES))
	assert_true(m.page(&"toma")["fallen"])
	assert_eq(m.hero_rows()[2]["right"], tr("STATUS_MENU_FALLEN"))
	assert_eq(m.hero_rows()[0]["right"], "")


func test_kerrid_s_unrisen_line_shows_only_after_the_reveal() -> void:
	var party: Array[StringName] = [&"rhen", &"kerrid"]
	state.party_ids = party.duplicate()
	var m := StatusMenuModel.new(PartySheet.new(state, party))
	assert_eq(m.page(&"kerrid")["note"], "", "no hint before the reveal (kerrid.md section 6)")
	state.flags[&"ch15_kerrid_revealed"] = true
	assert_eq(m.page(&"kerrid")["note"], tr("STATUS_MENU_KERRID_UNRISEN"))
	assert_eq(m.page(&"rhen")["note"], "", "his line only")
	menu = StatusMenu.create(PartySheet.new(state, party))
	_root().add_child(menu)
	menu.show_hero(&"kerrid")
	assert_true(menu.detail_texts().has(tr("STATUS_MENU_KERRID_UNRISEN")), "the page shows it")
	_teardown()


func test_keys_switch_heroes_and_cancel_closes() -> void:
	_open(true)
	var tree := menu.get_tree()
	assert_true(tree.paused)
	assert_eq(menu.hero, &"rhen")
	assert_eq(menu.help_text(), tr("STATUS_MENU_HELP"))
	assert_true(menu.detail_texts().has(tr("CHAR_RHEN")))
	assert_true(menu.detail_texts().has(tr("STAT_MAGIC_DEFENSE")), "the stat table")
	assert_eq(menu.detail_gauges().size(), 3, "HP, MP and Swell")
	assert_true(menu.handle_input(_ev(&"ui_right")))
	assert_eq(menu.hero, &"asha")
	assert_eq(menu.shown_page()["name"], tr("CHAR_ASHA"))
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.hero, &"toma")
	menu.handle_input(_ev(&"ui_page_down"))
	assert_eq(menu.hero, &"rhen", "wraps")
	menu.handle_input(_ev(&"ui_left"))
	assert_eq(menu.hero, &"toma")
	menu.handle_input(_ev(&"ui_page_up"))
	menu.handle_input(_ev(&"ui_up"))
	assert_eq(menu.hero, &"rhen")
	assert_true(menu.handle_input(_ev(&"ui_accept")), "Confirm is taken and does nothing")
	assert_true(menu.handle_input(_ev(&"ui_cancel")))
	assert_false(menu.is_open())
	assert_false(tree.paused)
	_teardown()


func test_the_mouse_hovers_clicks_and_scrolls() -> void:
	_open()
	assert_true(menu.handle_input(_wheel(MOUSE_BUTTON_WHEEL_DOWN)))
	assert_eq(menu.hero, &"asha")
	menu.handle_input(_wheel(MOUSE_BUTTON_WHEEL_UP))
	assert_eq(menu.hero, &"rhen")
	menu.list_page().row_clicked.emit(2)
	assert_eq(menu.hero, &"toma")
	assert_eq(menu.list_page().cursor, 2)
	menu.list_page().row_hovered.emit(1)
	assert_eq(menu.hero, &"asha")
	_teardown()


# --- helpers -------------------------------------------------------------------------------------


## Rhen in Coral-Bitten Hooks with Steady Arm added, two stat nodes woken and 3 points banked.
func _dressed_sheet() -> PartySheet:
	var sheet := PartySheet.new(state, HEROES)
	var bag := sheet.goods.equipment
	var weapon := bag.add_piece(&"rhen_coral_hooks")
	bag.set_slot(weapon, bag.first_empty_slot(weapon), &"steady_arm")
	assert_eq(bag.equip(&"rhen", weapon), EquipmentBag.RESULT_OK)
	var t := sheet.lattice.traveler(&"rhen")
	var woken := 0
	var queue: Array[StringName] = [t.position]
	var seen := {t.position: true}
	while not queue.is_empty() and woken < 2:
		var nid: StringName = queue.pop_front()
		var n := sheet.lattice.board.lattice_node(nid)
		if n != null and n.kind == LatticeNode.KIND_STAT and not t.activated.has(nid):
			t.activated[nid] = true
			woken += 1
		for next in sheet.lattice.board.neighbors(nid):
			if not seen.has(next):
				seen[next] = true
				queue.append(next)
	t.movement_points = 3
	return sheet


func _open(pause: bool = false) -> void:
	state.party_vitals = {"rhen": {"swell": 10}}
	menu = StatusMenu.create(PartySheet.new(state, HEROES))
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
