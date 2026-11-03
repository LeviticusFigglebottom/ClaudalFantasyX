extends TestCase
## M3-UI-1251 (the human's playtest FAST-TRACK 5): the field Magic page over a scratch GameStateData and stand-in
## rules (FieldMagicRules from Callables: Asha knows Mend and Chorus Mend, a cast heals a flat amount and spends the
## skill's mp_cost), so these tests pin the page, not combat-systems' formulas (M3-CMB-1252 tests those). The runner
## has no after_each: each test that opens the view frees it itself.

const HEROES: Array[StringName] = [&"rhen", &"asha", &"toma"]
const HEAL := 100

var state: GameStateData
var menu: MagicMenu
var casts := 0


func before_each() -> void:
	state = GameStateData.new()
	state.party_ids = HEROES.duplicate()
	menu = null
	casts = 0


func test_no_rules_no_page_and_no_root_row() -> void:
	var m := MagicMenuModel.new(_sheet(), null)
	assert_false(m.available())
	assert_true(m.spells_of(&"asha").is_empty())
	assert_eq(FieldMagicRules.live("NoSuchFieldCastClass"), null, "a missing class binds nothing")
	var fm := FieldMenuModel.new(state, HEROES.duplicate())
	assert_false(fm.root_ids().has(FieldMenuModel.ROW_MAGIC), "no Magic row before the rules exist")
	fm.has_magic = true
	var ids := fm.root_ids()
	assert_eq(ids[ids.find(FieldMenuModel.ROW_ITEMS) + 1], FieldMenuModel.ROW_MAGIC, "Magic comes after Items")
	assert_true(fm.root_enabled(FieldMenuModel.ROW_MAGIC))


func test_the_casters_say_who_has_field_spells() -> void:
	var m := _model()
	var rows := m.caster_rows()
	assert_eq(rows.size(), HEROES.size())
	assert_eq(rows[1]["label"], tr("CHAR_ASHA"))
	assert_eq(rows[1]["right"], tr("MAGIC_MENU_COUNT_FMT").format({"count": 2}))
	assert_eq(rows[0]["right"], tr("MAGIC_MENU_COUNT_NONE"), "Rhen knows none")
	assert_eq(m.caster_line(&"rhen")["text"], tr("MAGIC_MENU_NO_SPELLS_FMT").format({"name": tr("CHAR_RHEN")}))
	assert_false(m.caster_line(&"rhen")["ok"])
	assert_true(m.caster_line(&"asha")["ok"])


func test_a_spell_shows_its_cost_and_refuses_in_words() -> void:
	state.party_vitals = {"rhen": {"hp": 50}, "asha": {"mp": 2}}
	var m := _model()
	var spells := m.spell_rows(&"asha")
	assert_eq(spells[0]["label"], tr("SKILL_MEND"))
	assert_eq(spells[0]["right"], tr("MAGIC_MENU_COST_FMT").format({"mp": m.spell_cost(&"mend")}))
	assert_eq(m.spell_error(&"asha", &"mend"), &"no_mp", "2 MP is not enough")
	var words := {"caster": tr("CHAR_ASHA"), "mp": m.spell_cost(&"mend"), "spell": tr("SKILL_MEND")}
	assert_eq(m.spell_line(&"asha", &"mend")["text"], tr("MAGIC_MENU_ERR_NO_MP_FMT").format(words))
	assert_eq(m.refusal_text(&"a_new_reason", &"asha", &"mend"), tr("MAGIC_MENU_ERR_GENERIC_FMT").format(words))


func test_the_preview_and_the_cast_heal_spend_mp_and_save() -> void:
	state.party_vitals = {"rhen": {"hp": 50, "swell": 30, "statuses": ["poison"]}}
	var m := _model()
	var rhen := m.sheet.combatant(&"rhen")
	var asha := m.sheet.combatant(&"asha")
	assert_eq(m.hero_error(&"asha", &"mend", &"toma"), &"full_hp", "Toma is whole")
	var pv := m.preview(&"asha", &"mend", &"rhen")
	assert_true(pv["ok"])
	assert_true(str(pv["text"]).contains(tr("ITEMS_MENU_PREVIEW_HP_FMT").format({"from": 50, "to": 50 + HEAL})))
	var spent := tr("ITEMS_MENU_PREVIEW_MP_FMT").format({"from": asha.mp, "to": asha.mp - m.spell_cost(&"mend")})
	assert_true(str(pv["text"]).contains(spent), "the caster's MP")
	assert_eq(casts, 1, "a preview runs the rules on copies")
	assert_eq(state.vitals_of(&"rhen").get("hp"), 50, "and saves nothing")
	var done := m.cast_on(&"asha", &"mend", &"rhen")
	assert_true(done["ok"])
	assert_true(str(done["text"]).begins_with(tr("CHAR_ASHA")))
	assert_eq(int(state.vitals_of(&"rhen")["hp"]), 50 + HEAL, "the heal is saved")
	assert_eq(state.swell_of(&"rhen"), 30, "Rhen's Swell kept")
	assert_eq(state.statuses_of(&"rhen"), [&"poison"] as Array[StringName], "a carried status kept")
	assert_eq(int(state.vitals_of(&"asha")["mp"]), asha.mp - m.spell_cost(&"mend"), "Asha paid")
	assert_eq(m.sheet.combatant(&"rhen").hp, rhen.hp + HEAL)


func test_an_all_allies_spell_reaches_every_hero_it_helps() -> void:
	state.party_vitals = {"rhen": {"hp": 50}, "toma": {"hp": 60}}
	var m := _model()
	assert_true(m.is_all_allies(&"chorus_mend"))
	assert_eq(m.targets(&"asha", &"chorus_mend", &"asha"), [&"rhen", &"toma"] as Array[StringName], "not whole Asha")
	assert_eq(
		m.pick_title(&"asha", &"chorus_mend"),
		tr("MAGIC_MENU_PICK_ALL_TITLE_FMT").format({"spell": tr("SKILL_CHORUS_MEND"), "caster": tr("CHAR_ASHA")})
	)
	assert_true(m.cast_on(&"asha", &"chorus_mend", &"asha")["ok"])
	assert_eq(int(state.vitals_of(&"rhen")["hp"]), 50 + HEAL)
	assert_eq(int(state.vitals_of(&"toma")["hp"]), 60 + HEAL)
	state.party_vitals.erase("rhen")
	state.party_vitals.erase("toma")
	assert_false(m.cast_on(&"asha", &"chorus_mend", &"asha")["ok"], "nobody hurt: nothing cast")


func test_the_page_walks_caster_spell_hero_and_casts() -> void:
	state.party_vitals = {"rhen": {"hp": 50}}
	_open()
	assert_eq(menu.level, MagicMenu.Level.CASTER)
	assert_eq(menu.help_text(), tr("MAGIC_MENU_HELP_CASTER"))
	menu.accept()
	assert_eq(menu.level, MagicMenu.Level.CASTER, "Rhen has no spell: the page stays")
	assert_false(menu.use_text() == "")
	assert_true(menu.handle_input(_press(&"ui_down")))
	menu.accept()
	assert_eq(menu.level, MagicMenu.Level.SPELL)
	assert_eq(menu.caster, &"asha")
	assert_eq(menu.spell_page().row_count(), 2)
	menu.accept()
	assert_eq(menu.level, MagicMenu.Level.PICK)
	assert_eq(menu.spell, &"mend")
	assert_true(menu.preview_text().contains(tr("CHAR_RHEN")), "the cursor starts on Rhen")
	menu.accept()
	assert_false(menu.is_refused())
	assert_eq(int(state.vitals_of(&"rhen")["hp"]), 50 + HEAL, "cast from the page")
	assert_true(menu.preview_text().begins_with(tr("CHAR_ASHA")), "the receipt stays")
	assert_true(menu.handle_input(_press(&"ui_cancel")))
	assert_eq(menu.level, MagicMenu.Level.SPELL)
	menu.back()
	menu.back()
	assert_false(menu.is_open(), "Cancel from the casters closes")
	_teardown()


## With combat-systems' FieldSpell in the project (M3-CMB-05), the live rules drive the page: Asha's Mend heals Rhen
## for what FieldSpell's own preview says, the MP is spent and both are saved. Before that class is merged it passes
## as a no-op (the Magic row is hidden then, which test_no_rules_no_page_and_no_root_row covers).
func test_the_live_field_spell_rules_drive_the_page() -> void:
	var live := FieldMagicRules.live()
	if live == null:
		return
	state.party_vitals = {"rhen": {"hp": 50}}
	var m := MagicMenuModel.new(_sheet(), live, [&"poison", &"petrify", &"zombie"] as Array[StringName])
	assert_true(m.spells_of(&"asha").has(&"mend"), "Asha casts Mend in the field: %s" % [m.spells_of(&"asha")])
	assert_eq(m.hero_error(&"asha", &"mend", &"toma"), &"nothing_to_do", "Toma is whole")
	assert_eq(
		m.refusal_text(&"nothing_to_do", &"asha", &"mend", &"toma"),
		tr("MAGIC_MENU_ERR_NO_EFFECT_FMT").format({"spell": tr("SKILL_MEND"), "name": tr("CHAR_TOMA")})
	)
	var asha_mp := m.sheet.combatant(&"asha").mp
	var pv := m.preview(&"asha", &"mend", &"rhen")
	assert_true(pv["ok"], str(pv["text"]))
	var done := m.cast_on(&"asha", &"mend", &"rhen")
	assert_true(done["ok"])
	assert_true(int(state.vitals_of(&"rhen").get("hp", 0)) > 50, "Rhen is healed in the save")
	assert_eq(int(state.vitals_of(&"asha").get("mp", asha_mp)), asha_mp - m.spell_cost(&"mend"), "Asha paid once")
	assert_eq(str(done["text"]).get_slice(". ", 1), str(pv["text"]), "the receipt is what the preview said")


func _rules() -> FieldMagicRules:
	var usable := func(c: BattleCombatant) -> Array[StringName]:
		var out: Array[StringName] = []
		if c.id == &"asha":
			out.assign([&"mend", &"chorus_mend"])
		return out
	var refusal := func(c: BattleCombatant, sid: StringName, targets: Array[BattleCombatant]) -> StringName:
		var db := BattleDB.load_default()
		if c.hp <= 0:
			return &"caster_fallen"
		if c.mp < int(db.skill(sid).get("mp_cost", 0)):
			return &"no_mp"
		for t in targets:
			if t.hp <= 0:
				return &"target_fallen"
			if t.hp >= t.max_hp:
				return &"full_hp"
		return &""
	var cast := func(c: BattleCombatant, sid: StringName, targets: Array[BattleCombatant]) -> Dictionary:
		casts += 1
		c.mp -= int(BattleDB.load_default().skill(sid).get("mp_cost", 0))
		for t in targets:
			t.restore_hp(HEAL)
		return {"ok": true}
	return FieldMagicRules.new(usable, refusal, cast)


func _sheet() -> PartySheet:
	return PartySheet.new(state, HEROES.duplicate())


func _model() -> MagicMenuModel:
	return MagicMenuModel.new(_sheet(), _rules(), [&"poison", &"petrify", &"zombie"] as Array[StringName])


func _press(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


func _open() -> void:
	var m := _model()
	menu = MagicMenu.create(m.sheet, m)
	menu.pause_tree = false
	_root().add_child(menu)


func _teardown() -> void:
	if menu == null:
		return
	menu.close()
	menu.get_tree().paused = false
	if menu.get_parent() != null:
		menu.get_parent().remove_child(menu)
	menu.free()
	menu = null


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root
