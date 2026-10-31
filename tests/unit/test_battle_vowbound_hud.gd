extends TestCase
## M2-UI-05: the Vowbound on the battle scene (BattleVowboundHud, BattleMenus.call_rows and
## vowbound_root_rows). The caller's Call row and its refusals, the call's and the dismissal's
## timeline previews (pillar 4), the Vowbound's own menu (finisher, Dismiss; no swap, items or
## escape), the party panel and the stage while it is out, and the story flag that binds it.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261024
const ILUN := &"ilun"
const CALL_ROW := &"call_ilun"
const FLAG := &"ch03_ilun_bound"

var ctl: BattleController
var saved_state: GameStateData


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ctl.show_damage_numbers = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)


func test_the_caller_gets_a_call_row_with_its_rank_and_no_one_else_does() -> void:
	_start_fixture()
	_to_turn_of(&"asha")
	var row := _row(CALL_ROW)
	assert_true(bool(row.get("enabled", false)), "Ilun is bound: the call is open")
	assert_eq(row["label"], tr("HUD_CMD_CALL_FMT").format({"name": tr("VOWBOUND_ILUN")}))
	assert_eq(row["right"], tr("HUD_RANK_FMT").format({"rank": 3}), "the call's rank, as the caller pays it")
	assert_eq(_root_ids().find(CALL_ROW), _root_ids().find(BattleMenus.ROW_SKILLS) + 1, "right after Skills")
	_to_turn_of(&"rhen")
	assert_false(_root_ids().has(CALL_ROW), "Rhen calls no Vowbound")
	_free()


func test_other_fixtures_keep_their_root_menus() -> void:
	ctl.start_fixture(BattleFixture.load_fixture(&"swap_menu"))
	_to_turn_of(&"asha")
	for rid in _root_ids():
		assert_false(String(rid).begins_with(BattleMenus.ROW_CALL_PREFIX), "no call row: %s" % rid)
	_free()


func test_highlighting_the_call_previews_the_order_with_ilun_and_names_the_cost() -> void:
	_start_fixture()
	_to_turn_of(&"asha")
	ctl.hud.commands.select(CALL_ROW)
	var expected := ctl.engine.vowbound.preview_call(ctl.engine, ILUN)
	assert_eq(_slot_ids(), _ids(expected).slice(0, _slot_ids().size()), "the timeline shows the order after the call")
	assert_eq(_slot_ids()[0], ILUN, "Ilun takes this turn")
	assert_false(_slot_ids().has(&"asha"), "the party is off the order")
	assert_eq(ctl.hud.help_text(), ctl.menus.call_help(ctl.engine, ILUN))
	assert_true(ctl.hud.help_text().contains(tr("CHAR_ASHA")), "the help names the caller who pays")
	_free()


func test_the_call_stands_the_party_down_and_shows_ilun_alone() -> void:
	_start_fixture()
	_to_turn_of(&"asha")
	ctl.hud.commands.select(CALL_ROW)
	_press(&"ui_accept")
	var vb := ctl.engine.vowbound
	assert_true(vb.is_out())
	assert_eq(ctl.current_actor_id(), ILUN, "Ilun holds the turn")
	assert_eq(ctl.state, BattleController.STATE_COMMAND)
	assert_eq(ctl.menus.display_name(ctl.engine.current), tr("VOWBOUND_ILUN"))
	var rows := ctl.hud.party.rows()
	assert_eq(rows.size(), 1, "the party panel shows the Vowbound alone")
	assert_eq(rows[0].combatant, vb.summon)
	assert_true(rows[0].swell_gauge() != null, "with its own Swell gauge")
	assert_true(ctl.hud.party.note_text().contains(tr("CHAR_RHEN")), "the note names who stood down")
	assert_true(ctl.hud.party.note_text().contains(tr("CHAR_ASHA")))
	assert_true(ctl.stage.has_fighter(ILUN), "Ilun stands in")
	assert_false(ctl.stage.has_fighter(&"asha"), "the party stepped off")
	assert_false(ctl.stage.has_fighter(&"rhen"))
	_free()


func test_the_vowbounds_menu_has_its_finisher_and_dismiss_and_greys_the_rest() -> void:
	_start_fixture()
	_to_turn_of(&"asha")
	ctl.vow.call_vowbound(ILUN)
	var ids := _root_ids()
	var want: Array[StringName] = [
		BattleMenus.ROW_ATTACK,
		BattleMenus.ROW_UNLEASH,
		BattleMenus.ROW_SKILLS,
		BattleMenus.ROW_DISMISS,
		BattleMenus.ROW_ESCAPE,
		BattleMenus.ROW_SWAP,
	]
	assert_eq(ids, want)
	assert_false(bool(_row(BattleMenus.ROW_ESCAPE)["enabled"]), "no escape while Ilun is out")
	assert_false(bool(_row(BattleMenus.ROW_SWAP)["enabled"]), "no swap while Ilun is out")
	assert_true(bool(_row(BattleMenus.ROW_DISMISS)["enabled"]))
	var net := _row(BattleMenus.ROW_UNLEASH)
	assert_eq(net["label"], tr("SKILL_FLOODNET"))
	assert_false(bool(net["enabled"]), "the gauge is empty")
	assert_eq(net["right"], tr("HUD_VOWBOUND_GAUGE_FMT").format({"pct": 0}), "and the row says how full")
	_free()


func test_a_bag_and_a_call_row_make_a_seven_row_root_that_fits_its_panel() -> void:
	_start_fixture()
	var item_db := ItemDB.load_default()
	var inv := Inventory.new(item_db, {})
	inv.add(&"relighting_wick", 1)
	ctl.items = InventoryItemSource.new(item_db, inv)
	_to_turn_of(&"asha")
	ctl._open_command()  # the bag was set after the menu opened
	var page := ctl.hud.commands.top_page()
	assert_eq(page.rows.size(), 7, "Attack, Swell, Skills, Call, Items, Escape, Swap (M2-UI-03)")
	var last := page.row_rect(page.rows.size() - 1)
	assert_true(last.end.y <= page.size.y, "the last row sits inside the page (%s in %s)" % [last, page.size])
	var foot := HudLayout.rect_of(HudLayout.section(&"commands")).end.y
	assert_eq(page.position.y + page.size.y, foot, "the page grows upward from the same foot")
	ctl.vow.call_vowbound(ILUN)
	assert_false(_root_ids().has(BattleMenus.ROW_ITEMS), "a Vowbound uses no items")
	var r := ctl.use_item_on(&"relighting_wick", [ILUN] as Array[StringName])
	assert_false(r.ok)
	assert_eq(ctl.hud.help_text(), ctl.menus.fail_text(&"vowbound_out", ctl.engine.current))
	_free()


func test_dismiss_previews_the_return_with_the_callers_delay_then_brings_the_party_back() -> void:
	_start_fixture()
	_to_turn_of(&"asha")
	ctl.vow.call_vowbound(ILUN)
	var ilun := ctl.engine.vowbound.summon
	ctl.hud.commands.select(BattleMenus.ROW_DISMISS)
	var expected := ctl.engine.vowbound.preview_dismiss(ctl.engine)
	assert_eq(_slot_ids(), _ids(expected).slice(0, _slot_ids().size()), "the order with the party back")
	assert_true(_slot_ids().has(&"asha"))
	assert_false(_slot_ids().has(ILUN))
	assert_true(ctl.hud.help_text().begins_with(tr("HUD_HELP_DISMISS_FMT").format({"vowbound": tr("VOWBOUND_ILUN")})))
	assert_true(ctl.hud.help_text().contains(tr("CHAR_ASHA")), "and when Asha acts again")
	_press(&"ui_accept")
	assert_false(ctl.engine.vowbound.is_out())
	assert_eq(ctl.hud.party.rows().size(), 2, "the party panel is back")
	assert_eq(ctl.hud.party.note_text(), "")
	assert_true(ctl.stage.has_fighter(&"asha"))
	assert_true(ctl.stage.has_fighter(&"rhen"))
	assert_false(ctl.stage.has_fighter(ILUN))
	var note := ctl.menus.departed_text(ilun, false)
	assert_true(ctl.hud.help_history.has(note), "the next menu says the party returned")
	_free()


func test_a_full_gauge_unleashes_floodnet_through_the_menu() -> void:
	_start_fixture()
	_to_turn_of(&"asha")
	ctl.vow.call_vowbound(ILUN)
	var ilun := ctl.engine.vowbound.summon
	ilun.swell = Formulas.SWELL_MAX
	ctl.hud.commands.refresh_root(ctl.menus.root_rows(ctl.engine, ctl.items, ctl.swell))
	assert_true(bool(_row(BattleMenus.ROW_UNLEASH)["enabled"]), "full: Floodnet is open")
	ctl.hud.commands.select(BattleMenus.ROW_UNLEASH)
	assert_true(ctl.hud.help_text().contains(tr("HUD_TARGET_ALL_FOES")), "the help describes Floodnet")
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_TARGET)
	assert_eq(ctl.pending_skill(), &"floodnet")
	_press(&"ui_accept")
	assert_eq(ilun.swell, 0, "the gauge emptied")
	assert_true(ctl.hud.help_history.size() > 0)
	assert_ne(ctl.state, BattleController.STATE_TARGET, "the net was cast")
	_free()


func test_floodnet_on_an_empty_gauge_is_refused_in_words() -> void:
	_start_fixture()
	_to_turn_of(&"asha")
	ctl.vow.call_vowbound(ILUN)
	var foes := BattleIds.of(ctl.engine.living_foes_of(ctl.engine.current))
	var r := ctl.act(&"floodnet", foes)
	assert_false(r.ok)
	assert_eq(r.fail_reason, &"swell_not_full")
	assert_eq(ctl.state, BattleController.STATE_COMMAND, "nothing spent")
	assert_eq(ctl.hud.help_text(), ctl.menus.fail_text(&"swell_not_full", ctl.engine.current))
	_free()


func test_a_silenced_caller_sees_the_call_greyed_with_its_reason() -> void:
	ctl.start_fixture(_fixture({"asha": {"statuses": [{"id": "silence", "duration": 9}]}}))
	_to_turn_of(&"asha")
	var row := _row(CALL_ROW)
	assert_false(bool(row["enabled"]))
	assert_eq(row["right"], tr("HUD_CALL_SILENCED"))
	assert_false(ctl.vow.call_vowbound(ILUN), "refused")
	assert_eq(ctl.hud.help_text(), ctl.menus.fail_text(&"silenced", ctl.engine.current))
	_free()


func test_a_fallen_vowbound_is_greyed_as_fallen_and_the_party_returns() -> void:
	_start_fixture()
	_to_turn_of(&"asha")
	ctl.vow.call_vowbound(ILUN)
	var ilun := ctl.engine.vowbound.summon
	ilun.max_hp = 1
	ilun.hp = 1
	ilun.defense = 0
	ilun.evasion = 0
	ctl.act(BattleMenus.ATTACK_SKILL, [ctl.engine.living_foes_of(ilun)[0].id])
	var guard := 0
	while ctl.engine.vowbound.is_out() and ctl.engine.outcome == &"" and guard < 20:
		guard += 1
		ctl.act(BattleMenus.ATTACK_SKILL, [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	assert_false(ctl.engine.vowbound.is_out(), "Ilun fell; the party is back")
	assert_eq(ctl.engine.outcome, &"", "a fall is no defeat")
	assert_true(ctl.hud.help_history.has(ctl.menus.departed_text(ilun, true)), "the fall is said")
	_to_turn_of(&"asha")
	var row := _row(CALL_ROW)
	assert_false(bool(row["enabled"]))
	assert_eq(row["right"], tr("HUD_CALL_FALLEN"))
	_free()


func test_a_battle_with_nothing_bound_has_no_call_row() -> void:
	# Lead decision on M2-UI-05: no greyed "Call · None bound" before Chapter 3.
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma"]
	ctl.start_battle(active, reserve, &"sandbox_reef", SEED)
	_to_turn_of(&"asha")
	for rid in _root_ids():
		assert_false(String(rid).begins_with(BattleMenus.ROW_CALL_PREFIX), "no Call row until bound: %s" % rid)
	assert_true(ctl.engine.vowbound.callable_ids(ctl.engine).is_empty(), "nothing to call")
	_free()


func test_a_live_battle_binds_ilun_from_the_story_flag() -> void:
	ctl.persist_progress = true
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma"]
	ctl.start_battle(active, reserve, &"sandbox_reef", SEED)
	assert_true(ctl.engine.vowbound.known.is_empty(), "the flag is not set yet")
	Game.set_flag(FLAG, true)
	ctl.start_battle(active, reserve, &"sandbox_reef", SEED)
	assert_eq(ctl.engine.vowbound.known, [ILUN] as Array[StringName])
	_free()


func test_bound_ids_follow_each_rows_flag() -> void:
	var rows: Array = [
		{"id": "ilun", "bound_flag": "a"},
		{"id": "kahre", "bound_flag": "b"},
		{"id": "nobody"},
	]
	var got: Array[StringName] = BattleVowboundHud.bound_ids(rows, func(f: StringName) -> bool: return f == &"b")
	assert_eq(got, [&"kahre"] as Array[StringName])
	_free()


## M5-A3P-1705 (act3_ch20 U01-U06): a Vowbound released for good leaves the call list; its bond is not enough.
func test_a_released_vowbound_is_no_longer_bound() -> void:
	var rows: Array = [
		{"id": "ilun", "bound_flag": "a", "released_flag": "a_gone"},
		{"id": "kesh", "bound_flag": "b", "released_flag": "b_gone"},
	]
	var flags := {&"a": true, &"b": true}
	var is_set := func(f: StringName) -> bool: return bool(flags.get(f, false))
	assert_eq(BattleVowboundHud.bound_ids(rows, is_set), [&"ilun", &"kesh"] as Array[StringName])
	flags[&"a_gone"] = true
	assert_eq(BattleVowboundHud.bound_ids(rows, is_set), [&"kesh"] as Array[StringName], "one name left")
	_free()


func test_every_vowbound_refusal_reads_as_words() -> void:
	_start_fixture()
	_to_turn_of(&"asha")
	for r in [&"vowbound_out", &"unknown_vowbound", &"not_bound", &"not_caller", &"vowbound_fallen", &"no_vowbound"]:
		assert_true(BattleMenus.FAIL_REASONS.has(r), "listed: %s" % r)
		assert_ne(ctl.menus.fail_text(r, ctl.engine.current), tr("HUD_FAIL_GENERIC"), "%s has its sentence" % r)
	assert_eq(ctl.menus.call_refusal_word(&"not_your_turn"), tr("HUD_CALL_REFUSED"))
	_free()


func test_the_capture_states_reach_their_screens() -> void:
	ctl.run_script(BattleCaptureScript.SCRIPT_VOWBOUND_CALL)
	assert_eq(ctl.current_actor_id(), &"asha")
	assert_eq(StringName(str(ctl.hud.commands.current_row().get("id", ""))), CALL_ROW)
	ctl.run_script(BattleCaptureScript.SCRIPT_VOWBOUND_OUT)
	assert_eq(ctl.current_actor_id(), ILUN)
	assert_eq(StringName(str(ctl.hud.commands.current_row().get("id", ""))), BattleMenus.ROW_DISMISS)
	assert_true(ctl.engine.vowbound.summon.swell > 0, "the gauge has begun to fill")
	_free()


func _start_fixture() -> void:
	ctl.start_fixture(BattleFixture.load_fixture(&"vowbound_call"))


func _fixture(opening: Dictionary) -> BattleFixture:
	var fx := BattleFixture.load_fixture(&"vowbound_call")
	fx.opening = opening
	return fx


func _to_turn_of(cid: StringName) -> void:
	var guard := 0
	while ctl.engine.outcome == &"" and ctl.current_actor_id() != cid and guard < 30:
		guard += 1
		ctl.act(BattleMenus.ATTACK_SKILL, [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	assert_eq(ctl.current_actor_id(), cid, "reached %s's turn" % cid)


func _root_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for r in ctl.hud.commands.top_page().rows:
		out.append(StringName(str(r.get("id", ""))))
	return out


func _row(rid: StringName) -> Dictionary:
	for r in ctl.hud.commands.top_page().rows:
		if StringName(str(r.get("id", ""))) == rid:
			return r
	fail("no row %s in %s" % [rid, _root_ids()])
	return {}


func _slot_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for s in ctl.hud.timeline.slots:
		out.append(s["id"])
	return out


static func _ids(entries: Array[TurnEntry]) -> Array[StringName]:
	var out: Array[StringName] = []
	for e in entries:
		out.append(e.combatant_id)
	return out


func _press(action: StringName) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	ctl.handle_input(ev)


func _free() -> void:
	Game.state = saved_state
	ctl.get_parent().remove_child(ctl)
	ctl.free()
