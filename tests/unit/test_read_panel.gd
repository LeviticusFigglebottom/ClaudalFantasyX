extends TestCase
## M2-UI-02: the Read panel in battle (EnemyPage from BattleRead.reveal, ReadPanel, the battle held
## while it is open) and the opening banner (OpeningBanner), on the sandbox scene with the frozen
## capture fixtures (battle_fixtures.json: read_panel, opening_banner).

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"

var ctl: BattleController


func _free() -> void:
	if ctl != null:
		ctl.get_parent().remove_child(ctl)
		ctl.free()
		ctl = null


# --- EnemyPage: the words ------------------------------------------------------------------------


func test_a_reveal_page_names_every_fact_through_loc_keys() -> void:
	var fx := BattleFixture.load_fixture(&"read_panel")
	var row: Dictionary = fx.db.enemies[&"lantern_eel"]
	var c := BattleCombatant.from_dict(&"lantern_eel#2", BattleCombatant.TEAM_ENEMY, row)
	c.hp -= 50
	c.add_status(&"reflect", 3)
	var page := EnemyPage.new().from_reveal(BattleRead.reveal(c, row), fx.db.statuses)
	assert_eq(page["title"], tr("ENEMY_LANTERN_EEL"))
	assert_eq(page["level"], tr("HUD_READ_LEVEL_FMT").format({"level": c.level}))
	assert_true(str(page["vitals"]).contains("%d / %d" % [c.hp, c.max_hp]), "HP as it stands: %s" % page["vitals"])
	var stats: Array = page["stats"]
	assert_eq(stats.size(), BattleRead.STAT_KEYS.size(), "all eight stats")
	for i in stats.size():
		var key := str(EnemyPage.STAT_KEYS[BattleRead.STAT_KEYS[i]])
		assert_ne(tr(key), key, "%s is localized" % key)
		assert_eq(stats[i][0], tr(key))
	assert_eq(stats[0][1], str(c.strength))
	var aff: Dictionary = {}
	for a: Dictionary in page["affinities"]:
		aff[a["group"]] = a["text"]
		assert_ne(str(a["label"]), str(EnemyPage.AFFINITY_KEYS[a["group"]]), "the group label is localized")
	assert_eq(aff.keys(), ["weak", "resist", "immune", "absorb"], "the four lists, in BattleRead's order")
	assert_eq(aff["weak"], tr("ELEMENT_FIRE"))
	assert_eq(aff["immune"], tr("ELEMENT_LIGHTNING"))
	assert_eq(aff["resist"], tr("HUD_READ_NONE"), "an empty list says so")
	assert_eq(page["delay"], tr("HUD_READ_DELAY_OK"))
	assert_eq(page["statuses"], tr("STATUS_REFLECT"))
	assert_eq(page["lore"], tr("LORE_LANTERN_EEL"))
	assert_eq(page["defeated"], "", "a Read in battle has no defeat count")


## M4-A2P-083: a part broken on the weak point (BattleParts) shows on the Read until it is mended, named by its
## charge skill as the "repaired" float names it.
func test_a_broken_part_reads_until_it_is_mended() -> void:
	var engine := BattleEngine.new()
	var active: Array[StringName] = [&"rhen"]
	engine.setup(BattleDB.load_default(), active, [] as Array[StringName], &"ch11_lamp_engine", 1)
	engine.begin()
	var lamps := engine.enemies[0]
	var row: Dictionary = engine.db.enemies[BattleEngine.enemy_id(lamps)]
	var reveal := BattleRead.reveal(lamps, row)
	assert_true(BattleBestiary.broken_part_keys(engine, lamps.id).is_empty(), "nothing broken yet")
	assert_eq(EnemyPage.new().from_reveal(reveal)["parts"], "", "and no line for it")
	BattleParts.on_charge_broken(lamps, &"lamp_flare")
	var keys := BattleBestiary.broken_part_keys(engine, lamps.id)
	assert_eq(keys, ["SKILL_LAMP_FLARE"] as Array[String])
	reveal["broken_parts"] = keys
	var page := EnemyPage.new().from_reveal(reveal)
	assert_eq(page["parts"], tr("HUD_READ_PARTS_BROKEN_FMT").format({"list": tr("SKILL_LAMP_FLARE")}))
	var view := EnemyPageView.new()
	view.show_page(page)
	assert_true(view.shown_text().has(tr("HUD_READ_PARTS")), "the Read shows the row")
	assert_true(view.shown_text().has(page["parts"]))
	view.free()
	lamps.broken_parts.clear()
	assert_true(BattleBestiary.broken_part_keys(engine, lamps.id).is_empty(), "mended: gone")


func test_delay_immunity_and_no_statuses_read_plainly() -> void:
	var row := {"id": "warden", "name_key": "", "stats": {"hp": 10}, "delay_immune": true}
	var c := BattleCombatant.from_dict(&"warden", BattleCombatant.TEAM_ENEMY, row)
	var page := EnemyPage.new().from_reveal(BattleRead.reveal(c, row))
	assert_eq(page["title"], "warden", "no name key: the id")
	assert_eq(page["delay"], tr("HUD_READ_DELAY_IMMUNE"))
	assert_eq(page["statuses"], tr("HUD_READ_NONE"))
	assert_eq(page["lore"], "")


func test_a_book_page_is_the_row_at_full_strength_with_its_count() -> void:
	var fx := BattleFixture.load_fixture(&"read_panel")
	var page := EnemyPage.new().from_row(&"reef_crab", fx.db.enemies[&"reef_crab"], 3)
	assert_true(page["read"])
	assert_eq(
		page["vitals"], "%s · %s" % [tr("BESTIARY_HP_FMT").format({"hp": 380}), tr("BESTIARY_MP_FMT").format({"mp": 0})]
	)
	assert_eq(page["statuses"], "", "no statuses outside battle")
	assert_eq(page["defeated"], tr("BESTIARY_DEFEATED_FMT").format({"n": 3}))
	assert_eq(page["lore"], tr("LORE_REEF_CRAB"))
	var unread := EnemyPage.new().name_only(fx.db.enemies[&"reef_crab"], 2)
	assert_false(unread["read"])
	assert_eq(unread["title"], tr("ENEMY_REEF_CRAB"))
	assert_true(
		(unread["stats"] as Array).is_empty() and (unread["affinities"] as Array).is_empty(), "name and count only"
	)
	assert_eq(unread["defeated"], tr("BESTIARY_DEFEATED_FMT").format({"n": 2}))


# --- the panel in battle -------------------------------------------------------------------------


func test_a_read_opens_the_panel_on_the_foe_as_it_stands() -> void:
	_sandbox()
	assert_true(ctl.hud.get_node_or_null(^"ReadPanel") == null, "not built until a Read lands (HUD build budget)")
	_read_the_eel()
	var panel := ctl.hud.read_panel()
	assert_true(panel.is_open())
	assert_true(ctl.hud.holds_battle())
	assert_eq(panel.page()["title"], tr("ENEMY_LANTERN_EEL"))
	assert_eq(panel.page()["statuses"], tr("STATUS_REFLECT"), "the eel's Reflect, from the fixture")
	var shown := panel.shown_text()
	assert_true(shown.has(tr("LORE_LANTERN_EEL")), "lore on screen")
	assert_true(shown.has(tr("HUD_READ_CLOSE_HINT")), "how to close it")
	assert_true(shown.has(tr("STAT_MAGIC_DEFENSE")), "the stats on screen")
	_free()


func test_the_battle_waits_while_the_panel_is_open_and_goes_on_after_confirm() -> void:
	_sandbox()
	ctl.pacing_scale = 1.0  # real holds, so there is something to wait on
	_read_the_eel()
	ctl.stage.choreo.finish()  # M2-BPR-01: the panel opens on the Read's contact beat
	assert_true(ctl.is_waiting(), "the post-action hold is pending")
	var state := ctl.state
	var order := _order()
	ctl.tick(60.0)
	assert_true(ctl.is_waiting(), "a minute later the battle still waits for the reader")
	assert_eq(ctl.state, state)
	assert_eq(_order(), order, "no time passed: the order is as the Read left it")
	assert_false(ctl.handle_input(_ev(&"ui_accept")), "the controller is busy: the panel takes the press")
	assert_true(ctl.hud.read_panel().handle_input(_ev(&"ui_accept")))
	assert_false(ctl.hud.read_panel().is_open(), "confirm closes it")
	assert_false(ctl.hud.holds_battle())
	for i in 4:  # the hold, then the next turn's own waits
		ctl.tick(60.0)
	assert_ne(_order(), order, "then the battle goes on")
	_free()


func test_cancel_closes_it_and_other_menu_actions_are_swallowed() -> void:
	_sandbox()
	_read_the_eel()
	var panel := ctl.hud.read_panel()
	assert_true(panel.handle_input(_ev(&"ui_down")), "modal: the menu below does not move")
	assert_true(panel.is_open())
	var key := InputEventKey.new()
	key.keycode = KEY_F5
	key.pressed = true
	assert_false(panel.handle_input(key), "a debug key passes")
	assert_true(panel.handle_input(_ev(&"ui_cancel")))
	assert_false(panel.is_open())
	assert_false(panel.handle_input(_ev(&"ui_accept")), "closed: it takes nothing")
	_free()


func test_a_click_closes_it() -> void:
	_sandbox()
	_read_the_eel()
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	ctl.hud.read_panel()._on_click(click)
	assert_false(ctl.hud.read_panel().is_open())
	_free()


func test_a_new_battle_or_the_result_screen_closes_it() -> void:
	_sandbox()
	_read_the_eel()
	ctl.hud.set_combat_ui_visible(false)
	assert_false(ctl.hud.read_panel().is_open(), "the result screen")
	_read_the_eel()
	assert_true(ctl.hud.read_panel().is_open())
	ctl.start_fixture(BattleFixture.load_fixture(&"read_panel"))
	assert_false(ctl.hud.read_panel().is_open(), "a new battle (Retry)")
	_free()


func test_the_panel_leaves_the_timeline_uncovered() -> void:  # pillar 4
	var panel := HudLayout.rect_of(HudLayout.section(&"read_panel"))
	var timeline := HudLayout.rect_of(HudLayout.section(&"timeline"))
	assert_false(panel.intersects(timeline), "%s vs %s" % [panel, timeline])
	var banner := HudLayout.rect_of(HudLayout.section(&"opening_banner"))
	assert_false(banner.intersects(timeline))
	assert_false(banner.intersects(HudLayout.rect_of(HudLayout.section(&"help_line"))), "under the help line")


# --- the opening banner --------------------------------------------------------------------------


func test_an_ambush_shows_its_banner_and_a_normal_opening_builds_none() -> void:
	_sandbox(&"player_preview")
	assert_true(ctl.hud.get_node_or_null(^"OpeningBanner") == null, "a normal opening builds no banner")
	ctl.start_fixture(BattleFixture.load_fixture(&"opening_banner"))
	assert_eq(ctl.engine.opening, BattleOpening.AMBUSH, "the fixture's opening")
	var banner := ctl.hud.opening_banner()
	assert_true(banner.is_showing())
	assert_eq(banner.title_text(), tr("HUD_OPENING_AMBUSH_TITLE"))
	assert_eq(banner.caption_text(), "%s %s" % [tr("HUD_OPENING_AMBUSH"), tr("HUD_OPENING_AMBUSH_EFFECT")])
	assert_eq(banner.rule_role(), &"danger", "the foes act first")
	assert_eq(banner.mouse_filter, Control.MOUSE_FILTER_IGNORE, "it never takes input")
	var floats := ctl.hud.get_node(^"DamageLayer")
	assert_true(banner.get_index() < floats.get_index(), "drawn under the floating numbers and the panels")
	_free()


func test_a_preemptive_banner_uses_the_party_s_shape_and_words() -> void:
	_sandbox(&"player_preview")
	var banner := ctl.hud.opening_banner()
	banner.show_opening(BattleOpening.PREEMPTIVE, false)
	assert_eq(banner.title_text(), tr("HUD_OPENING_PREEMPTIVE_TITLE"))
	assert_true(banner.caption_text().ends_with(tr("HUD_OPENING_PREEMPTIVE_EFFECT")))
	assert_eq(banner.rule_role(), &"focus")
	banner.show_opening(BattleOpening.NORMAL)
	assert_false(banner.is_showing(), "normal: nothing")
	_free()


func test_the_banner_fades_in_and_reduced_motion_drops_the_rise() -> void:
	_sandbox(&"player_preview")
	var banner := ctl.hud.opening_banner()
	var rest := HudLayout.rect_of(HudLayout.section(&"opening_banner")).position.y
	banner.show_opening(BattleOpening.AMBUSH, true)
	assert_eq(banner.modulate.a, 0.0, "it fades in")
	assert_eq(banner.position.y, rest + HudLayout.num(HudLayout.section(&"opening_banner"), "rise_px"))
	var s := UiSettings.new()
	s.set_value(UiSettings.REDUCED_MOTION, true)
	ctl.hud.apply_settings(s)
	banner.show_opening(BattleOpening.AMBUSH, true)
	assert_eq(banner.position.y, rest, "reduced motion: no rise")
	assert_eq(banner.modulate.a, 0.0, "the fade stays")
	_free()


# --- helpers -------------------------------------------------------------------------------------


func _sandbox(fixture_id: StringName = &"read_panel") -> void:
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.hud.apply_settings(UiSettings.new())
	ctl.start_fixture(BattleFixture.load_fixture(fixture_id))


## Ysolde (quick in this fixture) Reads the reflecting Lantern Eel through the menus.
func _read_the_eel() -> void:
	var guard := 0
	while ctl.current_actor_id() != &"ysolde" and guard < CtbTimeline.PREVIEW_LENGTH:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	var eel := ctl.engine.find(&"lantern_eel#2")
	assert_true(ctl.act(&"read", [eel.id]).ok, "Ysolde reads the eel")


func _order() -> Array[String]:
	var out: Array[String] = []
	for t in ctl.engine.preview():
		out.append("%s@%d" % [t.combatant_id, t.time])
	out.append(String(ctl.current_actor_id()))
	return out


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
