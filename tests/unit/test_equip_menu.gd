extends TestCase
## M2-MNU-02: the Equip page (EquipMenuModel, EquipMenu) over a PartySheet on a scratch save: the
## gear and ability-slot rows, the stat-delta preview (checked against PartySheet.combatant after
## the real change), equip and unequip refusals in words, Customize (recipe, held, shortfall,
## craft), keyboard and mouse driving, the Net-Rack Forge's stock, and live battles wearing gear
## (BattleVitals.setup). The runner has no after_each: each test tears down with _done().

const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]
const FORGE := &"haluna_forge"
const FORGE_FLAGS: Array[String] = ["ch02_met_asha", "ch03_drownbell_defeated"]
const SEED := 20261024

var db: ItemDB
var state: GameStateData
var sheet: PartySheet
var model: EquipMenuModel
var menu: EquipMenu
var _saved_state: GameStateData


func before_each() -> void:
	db = ItemDB.load_default()
	state = GameStateData.new()
	sheet = PartySheet.new(state, HEROES)
	model = EquipMenuModel.new(sheet)
	menu = null
	_saved_state = Game.state


func _done() -> void:
	if menu != null and is_instance_valid(menu):
		menu.close()
		if menu.get_parent() != null:
			menu.get_parent().remove_child(menu)
		menu.free()
	menu = null
	Game.state = _saved_state
	var tree := Engine.get_main_loop() as SceneTree
	tree.paused = false


# --- the model -----------------------------------------------------------------------------------


func test_opening_grants_missing_starting_gear_once() -> void:
	for cid in HEROES:
		assert_ne(model.worn(cid, ItemDB.SLOT_WEAPON), EquipmentBag.NO_PIECE, "%s has a weapon" % cid)
	var owned := sheet.goods.equipment.uids().size()
	EquipMenuModel.new(sheet)
	assert_eq(sheet.goods.equipment.uids().size(), owned, "idempotent: nothing granted twice")
	_done()


func test_gear_rows_show_each_slot_and_its_ability_slots() -> void:
	var bag := sheet.goods.equipment
	var hooks := bag.add_piece(&"rhen_coral_hooks")
	assert_eq(bag.equip(&"rhen", hooks), EquipmentBag.RESULT_OK)
	var rows := model.gear_rows(&"rhen")
	assert_eq(rows[0]["kind"], EquipMenuModel.KIND_SLOT)
	assert_eq(rows[0]["label"], tr("EQUIP_MENU_SLOT_WEAPON"))
	assert_eq(rows[0]["right"], tr("EQUIP_RHEN_CORAL_HOOKS"))
	assert_eq(rows[1]["kind"], EquipMenuModel.KIND_ABILITY)
	assert_eq(rows[1]["right"], tr("ABILITY_EMBER_EDGE"), "the forge's pre-filled slot")
	assert_eq(rows[2]["ability"], &"", "the second slot is empty")
	assert_eq(rows[2]["right"], tr("EQUIP_MENU_EMPTY_SLOT"))
	assert_eq(rows[2]["label"], tr("EQUIP_MENU_ABILITY_SLOT_FMT").format({"n": 2}))
	assert_eq(rows[3]["label"], tr("EQUIP_MENU_SLOT_ARMOR"))
	assert_eq(rows.size(), 5, "weapon + 2 slots, armor + 1 slot")
	assert_eq(model.gear_desc(rows[1]), tr("ABILITY_EMBER_EDGE_DESC"))
	assert_eq(model.gear_desc(rows[2]), tr("EQUIP_MENU_EMPTY_SLOT_DESC"))
	assert_eq(model.gear_title(&"rhen"), tr("EQUIP_MENU_GEAR_TITLE_FMT").format({"hero": tr("CHAR_RHEN")}))
	_done()


func test_piece_rows_mark_the_worn_one_and_end_with_take_it_off() -> void:
	var spare := sheet.goods.equipment.add_piece(&"rhen_coral_hooks")
	var rows := model.piece_rows(&"rhen", ItemDB.SLOT_WEAPON)
	assert_eq(rows.size(), 3, "salvage hooks, coral hooks, take it off")
	assert_eq(rows[0]["right"], tr("EQUIP_MENU_WORN"))
	assert_eq(rows[1]["uid"], spare)
	assert_eq(rows[1]["right"], "")
	assert_eq(rows[2]["kind"], EquipMenuModel.KIND_REMOVE)
	_done()


func test_preview_deltas_match_the_hero_after_equipping() -> void:
	var bag := sheet.goods.equipment
	var hooks := bag.add_piece(&"rhen_coral_hooks")
	var before := sheet.combatant(&"rhen")
	var preview := model.preview_piece(&"rhen", ItemDB.SLOT_WEAPON, hooks)
	assert_eq(bag.equipped(&"rhen", ItemDB.SLOT_WEAPON), model.worn(&"rhen", ItemDB.SLOT_WEAPON))
	assert_ne(bag.equipped(&"rhen", ItemDB.SLOT_WEAPON), hooks, "a preview never equips")
	assert_eq(preview["gained"], [&"ember_edge"] as Array[StringName])
	assert_true((preview["lost"] as Array).is_empty())
	var result := model.choose_piece(&"rhen", ItemDB.SLOT_WEAPON, {"kind": EquipMenuModel.KIND_PIECE, "uid": hooks})
	assert_true(result["ok"])
	assert_eq(
		result["text"],
		tr("EQUIP_MENU_EQUIPPED_FMT").format({"hero": tr("CHAR_RHEN"), "name": tr("EQUIP_RHEN_CORAL_HOOKS")})
	)
	var after := sheet.combatant(&"rhen")
	for row: Dictionary in preview["stats"]:
		var st: StringName = row["stat"]
		assert_eq(row["now"], EquipMenuModel.stat_of(before, st), "%s now" % st)
		assert_eq(row["next"], EquipMenuModel.stat_of(after, st), "%s after" % st)
		assert_eq(row["delta"], row["next"] - row["now"])
	assert_eq(_delta(preview, &"strength"), 1, "the hooks' Strength +1")
	assert_eq(model.delta_text(1), "+1")
	assert_eq(model.delta_text(-2), tr("EQUIP_MENU_DELTA_DOWN_FMT").format({"n": 2}))
	assert_eq(model.delta_text(0), "")
	var back := model.preview_piece(&"rhen", ItemDB.SLOT_WEAPON, bag.pieces_for(&"rhen", ItemDB.SLOT_WEAPON)[0])
	assert_eq(_delta(back, &"strength"), -1, "going back loses it")
	assert_eq(back["lost"], [&"ember_edge"] as Array[StringName])
	assert_eq(model.ability_change_text(back), tr("EQUIP_MENU_LOSES_FMT").format({"list": tr("ABILITY_EMBER_EDGE")}))
	_done()


func test_taking_off_armor_previews_and_works_but_a_weapon_is_refused_in_words() -> void:
	var armor := model.worn(&"rhen", ItemDB.SLOT_ARMOR)
	var remove := {"kind": EquipMenuModel.KIND_REMOVE, "uid": EquipmentBag.NO_PIECE}
	var preview := model.preview_piece(&"rhen", ItemDB.SLOT_ARMOR, EquipmentBag.NO_PIECE)
	assert_eq(_delta(preview, &"hp"), -20, "the Patched Tether's HP +20 goes")
	assert_true(model.piece_line(&"rhen", ItemDB.SLOT_ARMOR, remove)["ok"])
	var weapon_line := model.piece_line(&"rhen", ItemDB.SLOT_WEAPON, remove)
	assert_false(weapon_line["ok"])
	var want := tr("EQUIP_MENU_ERR_SLOT_REQUIRED_FMT").format(
		{"hero": tr("CHAR_RHEN"), "slot": tr("EQUIP_MENU_SLOT_WEAPON")}
	)
	assert_eq(weapon_line["text"], want)
	var refused := model.choose_piece(&"rhen", ItemDB.SLOT_WEAPON, remove)
	assert_false(refused["ok"])
	assert_eq(refused["text"], want)
	var took := model.choose_piece(&"rhen", ItemDB.SLOT_ARMOR, remove)
	assert_true(took["ok"])
	assert_eq(model.worn(&"rhen", ItemDB.SLOT_ARMOR), EquipmentBag.NO_PIECE)
	assert_true(sheet.goods.equipment.has_piece(armor), "it stays in the pack")
	assert_eq(model.gear_rows(&"rhen")[2]["right"], tr("EQUIP_MENU_NOTHING_WORN"))
	_done()


func test_equip_refusals_are_said_in_words() -> void:
	var asha_staff := sheet.goods.equipment.add_piece(&"asha_bellshell_staff")
	var row := {"kind": EquipMenuModel.KIND_PIECE, "uid": asha_staff}
	var line := model.piece_line(&"rhen", ItemDB.SLOT_WEAPON, row)
	assert_false(line["ok"])
	assert_eq(
		line["text"],
		tr("EQUIP_MENU_ERR_WRONG_CHARACTER_FMT").format(
			{"name": tr("EQUIP_ASHA_BELLSHELL_STAFF"), "hero": tr("CHAR_RHEN")}
		)
	)
	assert_false(model.choose_piece(&"rhen", ItemDB.SLOT_WEAPON, row)["ok"])
	var gone := {"kind": EquipMenuModel.KIND_PIECE, "uid": 999}
	assert_eq(model.piece_line(&"rhen", ItemDB.SLOT_WEAPON, gone)["text"], tr("EQUIP_MENU_ERR_UNKNOWN_PIECE"))
	for err: StringName in EquipMenuModel.EQUIP_REFUSAL_KEYS:
		assert_ne(model.equip_refusal(err, &"rhen", ItemDB.SLOT_WEAPON, EquipmentBag.NO_PIECE), "", "%s in words" % err)
	for err: StringName in EquipMenuModel.CRAFT_REFUSAL_KEYS:
		assert_ne(model.craft_refusal(err, 1, &"tide_edge"), "", "%s in words" % err)
	_done()


func test_customize_lists_recipes_with_held_and_shortfall_then_crafts_for_good() -> void:
	var bag := sheet.goods.equipment
	var inv := sheet.goods.inventory
	var hooks := bag.add_piece(&"rhen_coral_hooks")
	bag.equip(&"rhen", hooks)
	inv.add(&"tide_pearl", 1)
	var rows := model.recipe_rows(hooks, 1)
	assert_eq(rows[0]["ability"], &"tide_edge", "ember edge is already on it")
	assert_eq(rows[0]["right"], tr("EQUIP_MENU_SHORT_FMT").format({"n": 3}))
	assert_eq(rows[0]["right_role"], &"text_disabled")
	var parts := model.recipe_parts(&"tide_edge")
	assert_eq(parts.size(), 1)
	assert_eq(parts[0]["short"], 3)
	assert_eq(
		parts[0]["text"],
		tr("EQUIP_MENU_RECIPE_PART_SHORT_FMT").format(
			{"name": tr("ITEM_TIDE_PEARL"), "count": 4, "held": 1, "short": 3}
		)
	)
	var line := model.recipe_line(hooks, 1, &"tide_edge")
	assert_false(line["ok"])
	var missing := tr("EQUIP_MENU_MISSING_PART_FMT").format({"n": 3, "name": tr("ITEM_TIDE_PEARL")})
	assert_eq(
		line["text"],
		tr("EQUIP_MENU_CRAFT_ERR_MISSING_FMT").format({"ability": tr("ABILITY_TIDE_EDGE"), "items": missing})
	)
	assert_false(model.craft(hooks, 1, &"tide_edge")["ok"])
	assert_eq(inv.count(&"tide_pearl"), 1, "a refused craft spends nothing")
	inv.add(&"tide_pearl", 3)
	assert_eq(model.recipe_rows(hooks, 1)[0]["right"], tr("EQUIP_MENU_READY"))
	assert_eq(model.recipe_rows(hooks, 1)[0]["right_role"], &"heal")
	assert_true(model.recipe_line(hooks, 1, &"tide_edge")["ok"])
	var preview := model.preview_craft(&"rhen", hooks, 1, &"tide_edge")
	assert_eq(preview["gained"], [&"tide_edge"] as Array[StringName])
	assert_eq(bag.slots_of(hooks)[1], &"", "a preview crafts nothing")
	var crafted := model.craft(hooks, 1, &"tide_edge")
	assert_true(crafted["ok"])
	assert_eq(bag.slots_of(hooks)[1], &"tide_edge")
	assert_eq(inv.count(&"tide_pearl"), 0, "the recipe is spent")
	assert_true(model.recipe_rows(hooks, 1).is_empty(), "no empty slot left")
	_done()


func test_a_stat_ability_preview_matches_the_crafted_hero() -> void:
	var bag := sheet.goods.equipment
	var hooks := bag.add_piece(&"rhen_coral_hooks")
	bag.equip(&"rhen", hooks)
	for part in Customize.new(db).cost(&"steady_arm"):
		sheet.goods.inventory.add(part["item"], int(part["count"]))
	var preview := model.preview_craft(&"rhen", hooks, 1, &"steady_arm")
	assert_true(model.craft(hooks, 1, &"steady_arm")["ok"])
	var after := sheet.combatant(&"rhen")
	assert_true(_delta(preview, &"strength") > 0, "Steady Arm raises Strength")
	for row: Dictionary in preview["stats"]:
		assert_eq(row["next"], EquipMenuModel.stat_of(after, row["stat"]), "%s after crafting" % row["stat"])
	_done()


func test_every_net_rack_forge_piece_can_be_bought_worn_and_previewed() -> void:
	var flags := FlagReader.new()
	for f in FORGE_FLAGS:
		flags.values[f] = true
	var shop := Shop.new(db, FORGE)
	var stock := shop.stock(flags)
	assert_true(stock.size() >= 6, "the forge sells gear")
	for gid in stock:
		var st := GameStateData.new()
		var s := PartySheet.new(st, HEROES)
		var m := EquipMenuModel.new(s)
		s.goods.wallet.earn(shop.buy_price(gid))
		assert_eq(shop.buy(gid, 1, s.goods, flags), Shop.RESULT_OK, "%s sells" % gid)
		var cid := db.character_of(gid)
		var where := db.slot_of(gid)
		var uid := s.goods.equipment.uids()[-1]
		assert_eq(s.goods.equipment.base_of(uid), gid)
		var row := {}
		for r in m.piece_rows(cid, where):
			if int(r["uid"]) == uid:
				row = r
		assert_false(row.is_empty(), "%s is offered to %s" % [gid, cid])
		assert_true(m.piece_line(cid, where, row)["ok"], "%s can be worn" % gid)
		var preview := m.preview_piece(cid, where, uid)
		var before: Dictionary = s.effects.stat_bonuses(cid)
		assert_true(m.choose_piece(cid, where, row)["ok"])
		var after: Dictionary = s.effects.stat_bonuses(cid)
		var worn_now := s.combatant(cid)
		for stat: Variant in db.equipment_row(gid).get("stats", {}):
			var want := int(after.get(stat, 0)) - int(before.get(stat, 0))
			assert_eq(_delta(preview, StringName(str(stat))), want, "%s %s" % [gid, stat])
		for r: Dictionary in preview["stats"]:
			assert_eq(r["next"], EquipMenuModel.stat_of(worn_now, r["stat"]), "%s %s once worn" % [gid, r["stat"]])
		assert_eq(s.goods.equipment.equipped(cid, where), uid)
	_done()


# --- the view ------------------------------------------------------------------------------------


func test_keys_drive_heroes_gear_pieces_and_cancel_backs_out() -> void:
	var spare := sheet.goods.equipment.add_piece(&"rhen_coral_hooks")
	_open()
	assert_eq(menu.level, EquipMenu.Level.HEROES)
	assert_eq(menu.help_text(), tr("EQUIP_MENU_HELP_HEROES"))
	assert_eq(menu.preview_title(), tr("CHAR_RHEN"))
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.preview_title(), tr("CHAR_ASHA"), "the highlighted hero's stats")
	menu.handle_input(_ev(&"ui_up"))
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.level, EquipMenu.Level.GEAR)
	assert_eq(menu.gear_page().current_row()["kind"], EquipMenuModel.KIND_SLOT)
	menu.handle_input(_ev(&"ui_right"))
	assert_eq(menu.hero, &"asha", "Right: the next hero")
	menu.handle_input(_ev(&"ui_page_up"))
	assert_eq(menu.hero, &"rhen", "Page Up: back")
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.level, EquipMenu.Level.PIECES)
	assert_true(menu.choice_page().visible and not menu.gear_page().visible)
	assert_eq(menu.choice_page().current_row()["right"], tr("EQUIP_MENU_WORN"), "the cursor starts on the worn piece")
	menu.handle_input(_ev(&"ui_down"))
	assert_eq(menu.choice_page().current_row()["uid"], spare)
	assert_eq(menu.preview_title(), tr("EQUIP_RHEN_CORAL_HOOKS"))
	var strength := menu.preview_cells()[EquipMenuModel.STAT_KEYS.keys().find(&"strength")]
	assert_eq(strength["delta"], "+1")
	var at := EquipMenuModel.STAT_KEYS.keys().find(&"strength")
	assert_eq(menu.preview_cell_color(at, "delta"), _role(&"heal"), "a gain in the theme's heal color")
	assert_eq(
		menu.changes_lines(), [tr("EQUIP_MENU_GAINS_FMT").format({"list": tr("ABILITY_EMBER_EDGE")})] as Array[String]
	)
	menu.handle_input(_ev(&"ui_accept"))
	assert_eq(menu.level, EquipMenu.Level.GEAR, "worn: back to the gear")
	assert_eq(sheet.goods.equipment.equipped(&"rhen", ItemDB.SLOT_WEAPON), spare)
	assert_eq(
		menu.status_text(),
		tr("EQUIP_MENU_EQUIPPED_FMT").format({"hero": tr("CHAR_RHEN"), "name": tr("EQUIP_RHEN_CORAL_HOOKS")})
	)
	assert_eq(menu.gear_page().current_row()["right"], tr("EQUIP_RHEN_CORAL_HOOKS"))
	menu.handle_input(_ev(&"ui_cancel"))
	assert_eq(menu.level, EquipMenu.Level.HEROES)
	menu.handle_input(_ev(&"ui_cancel"))
	assert_false(menu.is_open(), "Cancel from the party closes")
	_done()


func test_a_refused_take_off_is_red_and_changes_nothing() -> void:
	_open()
	menu.accept()  # Rhen's gear
	menu.accept()  # weapons
	var last := menu.choice_page().row_count() - 1
	menu.choice_page().set_cursor(last, false)
	menu._render()
	assert_true(menu.status_is_refusal(), "a weapon can only be swapped")
	var worn := sheet.goods.equipment.equipped(&"rhen", ItemDB.SLOT_WEAPON)
	menu.accept()
	assert_eq(menu.level, EquipMenu.Level.PIECES, "refused: still choosing")
	assert_eq(sheet.goods.equipment.equipped(&"rhen", ItemDB.SLOT_WEAPON), worn)
	_done()


func test_customize_asks_twice_then_crafts_and_a_filled_slot_says_why() -> void:
	var bag := sheet.goods.equipment
	var hooks := bag.add_piece(&"rhen_coral_hooks")
	bag.equip(&"rhen", hooks)
	sheet.goods.inventory.add(&"tide_pearl", 4)
	_open()
	menu.accept()  # Rhen's gear
	menu.handle_input(_ev(&"ui_down"))  # Ember Edge
	menu.accept()
	assert_eq(menu.level, EquipMenu.Level.GEAR, "a filled slot does not open Customize")
	assert_true(menu.status_is_refusal())
	assert_eq(menu.status_text(), model.craft_refusal(Customize.ERR_SLOT_FILLED, hooks, &"ember_edge"))
	menu.handle_input(_ev(&"ui_down"))  # the empty slot
	menu.accept()
	assert_eq(menu.level, EquipMenu.Level.RECIPES)
	assert_eq(menu.help_text(), tr("EQUIP_MENU_HELP_RECIPES"))
	assert_eq(menu.choice_page().current_row()["ability"], &"tide_edge")
	assert_eq(menu.desc_text(), tr("ABILITY_TIDE_EDGE_DESC"), "what the ability does")
	assert_eq(menu.changes_lines()[0], tr("EQUIP_MENU_RECIPE_TITLE"))
	menu.accept()
	assert_eq(menu.status_text(), model.craft_confirm_text(hooks, &"tide_edge"), "asks first")
	assert_eq(bag.slots_of(hooks)[1], &"", "nothing crafted yet")
	menu.accept()
	assert_eq(bag.slots_of(hooks)[1], &"tide_edge", "the second Confirm crafts")
	assert_eq(sheet.goods.inventory.count(&"tide_pearl"), 0)
	assert_eq(menu.level, EquipMenu.Level.GEAR)
	assert_eq(menu.gear_page().current_row()["ability"], &"tide_edge", "the cursor on the new ability")
	_done()


func test_a_short_recipe_is_refused_in_red() -> void:
	var bag := sheet.goods.equipment
	var hooks := bag.add_piece(&"rhen_coral_hooks")
	bag.equip(&"rhen", hooks)
	_open()
	menu.accept()
	menu.handle_input(_ev(&"ui_down"))
	menu.handle_input(_ev(&"ui_down"))
	menu.accept()
	assert_true(menu.status_is_refusal(), "nothing held: the line says what is missing")
	menu.accept()
	assert_eq(bag.slots_of(hooks)[1], &"")
	assert_eq(menu.changes_lines()[1], model.recipe_parts(&"tide_edge")[0]["text"])
	_done()


func test_mouse_clicks_choose_a_hero_a_slot_and_a_piece() -> void:
	var spare := sheet.goods.equipment.add_piece(&"toma_net_rack_spear")
	_open()
	menu.hero_page()._on_row_input(_click(), 2)
	assert_eq(menu.level, EquipMenu.Level.GEAR)
	assert_eq(menu.hero, &"toma")
	menu.gear_page()._on_row_input(_click(), 0)
	assert_eq(menu.level, EquipMenu.Level.PIECES)
	menu.choice_page()._on_row_input(_click(), 1)
	assert_eq(sheet.goods.equipment.equipped(&"toma", ItemDB.SLOT_WEAPON), spare)
	menu.hero_page()._on_row_input(_click(), 0)
	assert_eq(menu.hero, &"rhen", "a click on the party goes back to it")
	_done()


# --- battles wear the gear -----------------------------------------------------------------------


func test_a_live_battle_wears_the_saved_gear_and_a_fixture_does_not() -> void:
	var bdb := BattleDB.load_default()
	var goods := PartyGoods.from_state(db, state)
	var hooks := goods.equipment.add_piece(&"rhen_coral_hooks")
	assert_eq(goods.equipment.equip(&"rhen", hooks), EquipmentBag.RESULT_OK)
	var plain := BattleEngine.new()
	BattleVitals.setup(plain, bdb, _plan(), null, false, state)
	var live := BattleEngine.new()
	BattleVitals.setup(live, bdb, _plan(), null, true, state)
	var bonus := EquipmentEffects.new(db, goods.equipment).stat_bonuses(&"rhen")
	var rhen := live.find(&"rhen")
	assert_eq(rhen.strength, plain.find(&"rhen").strength + int(bonus[&"strength"]), "worn gear counts in battle")
	var tether_hp := int(EquipmentEffects.new(db, goods.equipment).stat_bonuses(&"rhen").get(&"hp", 0))
	assert_eq(rhen.max_hp, plain.find(&"rhen").max_hp + tether_hp)
	assert_eq(rhen.hp, rhen.max_hp, "no saved vitals: full, after the gear")
	assert_eq(EquipmentEffects.data_of(rhen)[EquipmentEffects.KEY_ABILITIES], [&"ember_edge"] as Array[StringName])
	assert_true(EquipmentEffects.data_of(plain.find(&"rhen")).is_empty(), "fixtures stay bare")
	_done()


func test_saved_hp_clamps_after_the_gear_and_full_net_doubles_lume() -> void:
	var bdb := BattleDB.load_default()
	var goods := PartyGoods.from_state(db, state)
	goods.ensure_starting_gear(state)
	var weapon := goods.equipment.equipped(&"rhen", ItemDB.SLOT_WEAPON)
	goods.equipment.set_slot(weapon, 0, &"full_net")
	state.party_vitals = {"rhen": {"hp": 9999}}
	var live := BattleEngine.new()
	BattleVitals.setup(live, bdb, _plan(), null, true, state)
	var rhen := live.find(&"rhen")
	assert_eq(rhen.hp, rhen.max_hp, "the vitals run last and clamp to the geared maximum")
	assert_true(live.currency_multiplier.is_valid())
	var want := int(db.ability(&"full_net")["effect"]["currency_mult"])
	assert_eq(int(live.currency_multiplier.call([&"rhen"] as Array[StringName])), want)
	assert_eq(int(live.currency_multiplier.call([&"asha"] as Array[StringName])), EquipmentEffects.NO_CURRENCY_MULT)
	_done()


# --- helpers -------------------------------------------------------------------------------------


func _open() -> void:
	menu = EquipMenu.create(sheet)
	menu.pause_tree = false
	_root().add_child(menu)
	model = menu.model


func _delta(preview: Dictionary, stat: StringName) -> int:
	for row: Dictionary in preview["stats"]:
		if row["stat"] == stat:
			return int(row["delta"])
	return 0


func _plan() -> Dictionary:
	return {
		"active": [&"rhen", &"asha"] as Array[StringName],
		"reserve": [&"toma"] as Array[StringName],
		"encounter": &"sandbox_reef",
		"seed": SEED,
	}


func _role(role: StringName) -> Color:
	return menu.get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root


func _click() -> InputEventMouseButton:
	var ev := InputEventMouseButton.new()
	ev.button_index = MOUSE_BUTTON_LEFT
	ev.pressed = true
	return ev


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
