extends TestCase
## The human's playtest FAST-TRACK (2026-11-03): every status explains how to know it and how to be rid of it.
## StatusHelpModel over the real tables and a scratch flag set; StatusHelpPanel, StatusTipCard and StatusGlyph's
## one line; BattleStatusTips in a sandbox battle (the first-time card and the help key); the Codex's
## Afflictions entries; the Status page's help key. The runner runs no frames and has no after_each.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261103

var flags: Dictionary = {}
var made: Array[Node] = []
var ctl: BattleController
var saved_state: GameStateData


func before_each() -> void:
	flags = {}
	_free_made()
	UiSettings.set_shared(UiSettings.new())
	StatusHelpModel.ensure_action()


func test_every_status_has_its_name_its_words_its_time_and_a_glyph() -> void:
	var m := _model()
	var raw := FileAccess.get_file_as_string(StatusHelpModel.STATUSES_PATH)
	var table: Array = (JSON.parse_string(raw) as Dictionary)["statuses"]
	assert_eq(m.ids().size(), table.size(), "every statuses.json row")
	for sid in m.ids():
		assert_ne(m.name_of(sid), m.name_key(sid), "%s is named" % sid)
		assert_ne(m.desc_of(sid), m.desc_key(sid), "%s says what it does" % sid)
		assert_true(StatusGlyph.has_shape(sid), "%s has its own glyph" % sid)
		var lines := m.removal_lines(sid)
		assert_true(lines.size() >= 3 or m.is_buff(sid) or m.duration_of(sid) > 0, "%s says how it ends" % sid)
		assert_eq(lines[0], m.lasts(sid))
		for line in lines:
			assert_false(line.contains("{"), "%s: no unfilled field in '%s'" % [sid, line])
			assert_false(line.begins_with("STATUS_HELP_"), "%s: '%s' is translated" % [sid, line])
		assert_true(m.body(sid).begins_with(m.desc_of(sid)))
	assert_eq(m.name_of(&"doom"), "Last Tide", "ADR 0202's own names")
	assert_eq(m.name_of(&"shell"), "Tide Ward")


func test_poison_names_its_items_its_shrine_and_that_it_outlasts_the_battle() -> void:
	var m := _model()
	var items := m.cure_items(&"poison")
	var ids := items.map(func(i: Dictionary) -> StringName: return i["id"])
	assert_true(ids.has(&"bitterleaf") and ids.has(&"tidewash_salve"), "items.json's cures: %s" % [ids])
	assert_true(m.is_carried(&"poison") and m.cured_by_shrine(&"poison"), "party_rest.json")
	var lines := m.removal_lines(&"poison")
	assert_true(lines.has(tr("STATUS_HELP_CARRIED")))
	assert_true(lines.has(tr("STATUS_HELP_SHRINE")))
	assert_true(lines.has(tr("STATUS_HELP_LASTS_CURED")), "poison has no set time")
	var cured := tr("STATUS_HELP_ITEMS_FMT").format({"items": tr("ITEM_BITTERLEAF") + ", " + tr("ITEM_TIDEWASH_SALVE")})
	assert_true(lines.has(cured), "%s in %s" % [cured, lines])


func test_a_battle_only_cure_says_so_and_a_timed_status_says_its_turns() -> void:
	var m := _model()
	var sleep := m.removal_lines(&"sleep")
	var salts := tr("STATUS_HELP_IN_BATTLE_FMT").format({"item": tr("ITEM_SMELLING_SALTS")})
	assert_true(sleep[2].contains(salts), "Smelling Salts have no field use: %s" % sleep[2])
	assert_eq(sleep[0], tr("STATUS_HELP_LASTS_TURNS_FMT").format({"turns": 3}), "statuses.json default_duration")
	assert_true(sleep.has(tr("STATUS_HELP_ENDS_WITH_BATTLE")))
	assert_true(sleep.has(tr("STATUS_HELP_NOTE_SLEEP")), "and its own way out")
	var haste := m.removal_lines(&"haste")
	assert_eq(haste[0], tr("STATUS_HELP_LASTS_TURNS_FMT").format({"turns": 4}))
	assert_eq(m.kind_of(&"haste"), tr("STATUS_HELP_KIND_BUFF"))
	assert_eq(m.kind_of(&"poison"), tr("STATUS_HELP_KIND_AILMENT"))
	assert_true(m.removal_lines(&"doom").has(tr("STATUS_HELP_NOTE_DOOM")), "Last Tide says nothing lifts it")
	assert_eq(
		m.lasts(&"doom"), tr("STATUS_HELP_LASTS_DOOM_FMT").format({"turns": 5}), "it counts down, it never wears off"
	)


func test_a_vowbound_s_cleanse_is_named_only_once_it_is_bound() -> void:
	var m := _model()
	var before := m.cure_abilities(&"berserk")
	assert_true(before.filter(func(a: Dictionary) -> bool: return a["id"] == &"cord_lift").is_empty(), "Hesk unmet")
	flags[&"ch12_hesk_bound"] = true
	var after := m.cure_abilities(&"berserk")
	var lift := after.filter(func(a: Dictionary) -> bool: return a["id"] == &"cord_lift")
	assert_eq(lift.size(), 1, "Cord Lift once Hesk is bound")
	assert_eq(lift[0]["by"], tr("VOWBOUND_HESK"))
	var line := tr("STATUS_HELP_ABILITIES_FMT").format(
		{"abilities": tr("STATUS_HELP_BY_FMT").format({"skill": tr("SKILL_CORD_LIFT"), "by": tr("VOWBOUND_HESK")})}
	)
	assert_true(m.removal_lines(&"berserk").has(line), "%s" % [m.removal_lines(&"berserk")])
	var foes := m.cure_abilities(&"haste")
	assert_true(
		foes.filter(func(a: Dictionary) -> bool: return a["id"] == &"unravel").is_empty(), "a foe's skill is not a cure"
	)


func test_the_one_line_and_the_order_with_the_bearer_s_statuses_first() -> void:
	var m := _model()
	assert_eq(m.one_line(&"poison"), "%s: %s" % [m.name_of(&"poison"), m.desc_of(&"poison")])
	var order := m.ordered([&"slow", &"poison", &"not_a_status"] as Array[StringName])
	assert_eq(order.slice(0, 2), [&"slow", &"poison"] as Array[StringName])
	assert_eq(order.size(), m.ids().size(), "every status once, the unknown one dropped")


func test_a_chip_explains_itself_on_hover_and_on_a_long_press() -> void:
	StatusHelpModel.set_shared(_model())
	var g := StatusGlyph.with_help(&"poison")
	_add(g)
	assert_eq(g.tooltip_text, _model().one_line(&"poison"), "its hover line")
	assert_eq(g.mouse_filter, Control.MOUSE_FILTER_PASS, "it takes the pointer and passes the click on")
	g.show_callout()
	assert_true(g.callout_shown())
	assert_eq(g.callout_text(), g.help_line)
	g.hide_callout()
	assert_false(g.callout_shown())
	var plain := StatusGlyph.new(&"poison")
	assert_eq(plain.mouse_filter, Control.MOUSE_FILTER_IGNORE, "a plain glyph stays out of the way")
	plain.free()
	StatusHelpModel.set_shared(null)
	_free_made()


func test_the_panel_opens_on_the_bearer_and_pages_through_every_status() -> void:
	var p := StatusHelpPanel.new(_model())
	_add(p)
	p.open([&"poison", &"slow"] as Array[StringName], "Rhen", &"", false)
	assert_true(p.is_open())
	assert_eq(p.current_status(), &"poison", "the bearer's first status")
	var text := p.shown_text()
	assert_true(text.has(tr("STATUS_HELP_ON_FMT").format({"name": "Rhen"})), "marked as on Rhen")
	assert_true(text.has(_model().desc_of(&"poison")))
	assert_true(text.has(tr("STATUS_HELP_SHRINE")), "how to be rid of it")
	assert_true(p.handle_input(_press(&"ui_down")))
	assert_eq(p.current_status(), &"slow")
	p.move(-2)
	assert_eq(p.current_status(), p.order.back(), "it wraps")
	assert_false(p.shown_text().has(tr("STATUS_HELP_ON_FMT").format({"name": "Rhen"})), "not on Rhen")
	assert_true(p.handle_input(_press(&"ui_cancel")))
	assert_false(p.is_open())
	p.open([] as Array[StringName], "", &"regen", false)
	assert_eq(p.current_status(), &"regen", "a focus opens on that status")
	assert_true(p.handle_input(_press(StatusHelpPanel.ACTION)), "the help key closes it again")
	assert_false(p.is_open())
	_free_made()


func test_the_first_time_a_status_lands_its_card_shows_once_and_holds_the_battle() -> void:
	_start()
	var tips := _tips()
	tips.live = true
	var rhen := ctl.engine.find(&"rhen")
	rhen.add_status(&"poison", -1)
	ctl.state_changed.emit(BattleController.STATE_COMMAND)
	assert_true(tips.card.is_open(), "the card waits for the party's command, then shows")
	assert_eq(tips.card.status, &"poison")
	assert_true(Game.get_flag(&"status_poison_met"), "met when shown")
	assert_true(ctl.hud.holds_battle(), "the battle waits while it shows")
	var text := tips.card.shown_text()
	assert_eq(
		text[0], tr("STATUS_TIP_TITLE_FMT").format({"name": tr("STATUS_POISON"), "hero": ctl.menus.display_name(rhen)})
	)
	assert_eq(text[1], tips.model.body(&"poison"))
	assert_true(tips.handle_input(_press(&"ui_accept")))
	assert_false(tips.card.is_open())
	assert_false(ctl.hud.holds_battle())
	ctl.state_changed.emit(BattleController.STATE_COMMAND)
	assert_false(tips.card.is_open(), "once per save")
	_free_battle()


func test_the_card_s_help_key_opens_the_panel_and_tips_off_still_open_the_codex() -> void:
	_start()
	var tips := _tips()
	tips.live = true
	ctl.engine.find(&"asha").add_status(&"haste", 4)
	ctl.state_changed.emit(BattleController.STATE_COMMAND)
	assert_eq(
		tips.card.shown_text()[0],
		tr("STATUS_TIP_BUFF_TITLE_FMT").format(
			{"name": tr("STATUS_HASTE"), "hero": ctl.menus.display_name(ctl.engine.find(&"asha"))}
		)
	)
	assert_true(tips.handle_input(_press(StatusHelpPanel.ACTION)))
	assert_true(tips.panel.is_open(), "every status, on Haste")
	assert_eq(tips.panel.current_status(), &"haste")
	tips.panel.close()
	UiSettings.shared().set_value(UiSettings.TUTORIAL_TIPS, false)
	ctl.engine.find(&"toma").add_status(&"slow", 4)
	ctl.state_changed.emit(BattleController.STATE_COMMAND)
	assert_false(tips.card.is_open(), "tips off: no card")
	assert_true(Game.get_flag(&"status_slow_met"), "but the Codex entry opens")
	_free_battle()


func test_a_capture_or_a_fixture_never_teaches() -> void:
	_start()
	var tips := _tips()
	assert_false(tips.live, "persist_progress is off in tests")
	ctl.engine.find(&"rhen").add_status(&"poison", -1)
	ctl.state_changed.emit(BattleController.STATE_COMMAND)
	assert_false(tips.card.is_open())
	assert_false(Game.get_flag(&"status_poison_met"))
	_free_battle()


func test_the_help_key_in_the_command_menu_explains_the_acting_hero() -> void:
	_start()
	var tips := _tips()
	var actor := ctl.engine.current
	assert_eq(actor.team, BattleCombatant.TEAM_PARTY, "the sandbox opens on a hero")
	actor.add_status(&"silence", 4)
	assert_true(tips.handle_input(_press(StatusHelpPanel.ACTION)))
	assert_true(tips.panel.is_open())
	assert_eq(tips.panel.current_status(), &"silence")
	assert_eq(tips.panel.bearer_name, ctl.menus.display_name(actor))
	assert_true(ctl.hud.holds_battle())
	_free_battle()


func test_the_codex_afflictions_open_as_they_are_met_with_the_whole_help() -> void:
	StatusHelpModel.set_shared(_model())
	var codex := CodexModel.new(
		{}, func(f: StringName) -> bool: return flags.get(f, false), func(f: StringName) -> void: flags[f] = true
	)
	var cat := codex.categories().filter(func(c: Dictionary) -> bool: return c["id"] == &"afflictions")
	assert_eq(cat.size(), 1, "the Afflictions section")
	assert_eq(int(cat[0]["total"]), _model().ids().size(), "one entry per status")
	assert_true(codex.entries_in(&"afflictions").is_empty(), "none met yet")
	flags[&"status_poison_met"] = true
	var shown := codex.entries_in(&"afflictions")
	assert_eq(shown.size(), 1)
	assert_eq(shown[0]["id"], &"affliction_poison")
	assert_eq(codex.title(&"affliction_poison"), tr("STATUS_POISON"))
	assert_eq(codex.body(&"affliction_poison"), _model().body(&"poison"), "its page is the status help")
	StatusHelpModel.set_shared(null)


func test_the_status_page_s_help_key_opens_the_hero_s_statuses() -> void:
	var state := GameStateData.new()
	state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	state.party_vitals = {"rhen": {"hp": 100, "statuses": ["poison"]}}
	var menu := StatusMenu.create(PartySheet.new(state, state.party_ids))
	_add(menu)
	assert_true(menu.help_text().contains(InputNames.first_name(StatusHelpPanel.ACTION)), "the page names the key")
	assert_true(menu.handle_input(_press(StatusHelpPanel.ACTION)))
	var p := menu.status_help()
	assert_true(p != null and p.is_open())
	assert_eq(p.current_status(), &"poison", "Rhen's carried poison first")
	assert_true(menu.handle_input(_press(&"ui_cancel")), "Cancel closes the panel, not the page")
	assert_false(p.is_open())
	assert_true(menu.is_open())
	menu.close()
	menu.get_tree().paused = false
	_free_made()


func _model() -> StatusHelpModel:
	var m := StatusHelpModel.from_game()
	var fresh := StatusHelpModel.new({}, func(f: StringName) -> bool: return flags.get(f, false))
	fresh.rows = m.rows
	fresh.item_rows = m.item_rows
	fresh.skills = m.skills
	fresh.sources = m.sources
	fresh.carried = m.carried
	fresh.shrine_cures = m.shrine_cures
	fresh.notes = m.notes
	fresh.lasts_keys = m.lasts_keys
	return fresh


func _press(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


func _tips() -> BattleStatusTips:
	return ctl.hud.get_node(NodePath(BattleStatusTips.NODE_NAME)) as BattleStatusTips


func _start() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ctl.show_damage_numbers = false
	_root().add_child(ctl)
	ctl.start_battle([&"rhen", &"asha", &"toma"] as Array[StringName], [] as Array[StringName], &"sandbox_reef", SEED)
	ctl.stage.choreo.live = false
	while ctl.engine.current.team != BattleCombatant.TEAM_PARTY and ctl.engine.outcome == &"":
		ctl.tick(1.0)


func _free_battle() -> void:
	Game.state = saved_state
	ctl.get_tree().paused = false
	ctl.get_parent().remove_child(ctl)
	ctl.free()
	UiSettings.set_shared(null)


func _add(n: Node) -> void:
	made.append(n)
	_root().add_child(n)


func _free_made() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func _root() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.current_scene if tree.current_scene != null else tree.root
