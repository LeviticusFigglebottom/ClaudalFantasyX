extends TestCase
## M2-UI-01: choosing a Swell fill mode on the battle Swell page (BattleMenus.swell_mode_rows,
## SwellModeRows) and the timing-assist accessibility setting (UiSettings.timing_input, applied to
## the input row; SwellInput.assist_floor, every kind), on the sandbox with the frozen capture fixtures.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"

var ctl: BattleController


func before_each() -> void:
	ctl = null


# --- the Swell page's fill modes -----------------------------------------------------------------


func test_a_filling_gauge_still_opens_the_page_with_its_modes() -> void:
	_open_page(&"swell_modes")
	var rows := ctl.hud.commands.top_page().rows
	assert_eq(str(rows[0]["id"]), "lamp_dive")
	assert_false(bool(rows[0]["enabled"]), "the technique waits for a full gauge")
	var ids: Array[String] = []
	for r in rows.slice(1):
		ids.append(str(r["id"]))
		assert_true(bool(r["enabled"]))
	assert_eq(ids, ["swell_mode_ballast", "swell_mode_wake"], "the unlocked modes, in swell.json order")
	assert_eq(str(rows[1]["label"]), tr("SWELL_MODE_BALLAST"))
	assert_eq(str(rows[1]["right"]), tr("HUD_SWELL_MODE_IN_USE"), "Rhen starts in Ballast")
	assert_eq(str(rows[2]["right"]), tr("HUD_COST_FREE"), "choosing another costs no time")
	assert_eq(ctl.hud.commands.top_page().cursor, 1, "the cursor skips the greyed technique")
	_free()


func test_highlighting_a_mode_says_what_it_does_and_previews_no_cost() -> void:
	_open_page(&"swell_modes")
	ctl.hud.commands.select(&"swell_mode_wake")
	var want := tr("HUD_HELP_SWELL_MODE_FMT").format(
		{"mode": tr("SWELL_MODE_WAKE"), "desc": tr("SWELL_MODE_WAKE_DESC")}
	)
	assert_eq(ctl.hud.help_text(), want)
	for s in ctl.hud.timeline.slots:
		assert_false(bool(s["ghost"]), "no ghost chip: a mode change is not a turn")
		assert_false(int(s.get("moved", 0)) != 0, "nobody moves")
	ctl.hud.commands.select(&"swell_mode_ballast")
	assert_true(ctl.hud.help_text().begins_with(tr("SWELL_MODE_BALLAST")), "the mode in use says so")
	_free()


func test_choosing_a_mode_sets_it_for_free_and_the_gauge_then_fills_by_it() -> void:
	_open_page(&"swell_modes")
	var rhen := ctl.engine.find(&"rhen")
	var order := _order()
	ctl.hud.commands.select(&"swell_mode_wake")
	_press(&"ui_accept")
	assert_eq(rhen.swell_mode, &"wake")
	assert_eq(ctl.state, BattleController.STATE_SWELL, "still on the Swell page")
	assert_eq(ctl.current_actor_id(), &"rhen", "still Rhen's turn")
	assert_eq(_order(), order, "no time passed")
	assert_eq(
		ctl.hud.help_text(),
		tr("HUD_SWELL_MODE_SET_FMT").format({"name": tr("CHAR_RHEN"), "mode": tr("SWELL_MODE_WAKE")})
	)
	var rows := ctl.hud.commands.top_page().rows
	assert_eq(str(rows[2]["right"]), tr("HUD_SWELL_MODE_IN_USE"), "the page redraws in place")
	assert_eq(str(rows[1]["right"]), tr("HUD_COST_FREE"))
	assert_eq(ctl.hud.commands.top_page().cursor, 2, "the cursor stays on the chosen row")
	_press(&"ui_cancel")
	assert_eq(ctl.state, BattleController.STATE_COMMAND)
	var root_right := str(ctl.hud.commands.top_page().rows[1]["right"])
	assert_eq(root_right, tr("SWELL_MODE_WAKE"), "the root row names the new mode")
	var before := rhen.swell
	var foe := ctl.engine.find(&"gull_harrier#3")
	assert_true(ctl.act(&"attack", [foe.id]).ok)
	assert_true(rhen.swell > before or foe.hp == foe.max_hp, "Wake fills on damage dealt")
	_free()


func test_choosing_the_mode_in_use_changes_nothing() -> void:
	_open_page(&"swell_modes")
	ctl.hud.commands.select(&"swell_mode_ballast")
	_press(&"ui_accept")
	assert_eq(ctl.engine.find(&"rhen").swell_mode, &"ballast")
	assert_eq(ctl.state, BattleController.STATE_SWELL)
	assert_true(ctl.hud.help_text().begins_with(tr("SWELL_MODE_BALLAST")))
	_free()


func test_a_full_gauge_lists_the_technique_ready_and_the_modes_too() -> void:
	_open_page(&"swell_ring")
	var rows := ctl.hud.commands.top_page().rows
	assert_true(bool(rows[0]["enabled"]), "full: Lamp Dive is ready")
	assert_eq(rows.size(), 3)
	assert_eq(ctl.hud.commands.top_page().cursor, 0, "the cursor starts on the technique")
	_free()


func test_a_mode_unlocked_through_play_joins_the_page() -> void:
	_sandbox(&"swell_modes")
	assert_true(ctl.swell.unlock_mode(&"tether"))
	_to_turn_of(&"rhen")
	ctl.hud.commands.select(BattleMenus.ROW_SWELL)
	_press(&"ui_accept")
	var ids: Array[String] = []
	for r in ctl.hud.commands.top_page().rows:
		ids.append(str(r["id"]))
	assert_eq(ids, ["lamp_dive", "swell_mode_ballast", "swell_mode_wake", "swell_mode_tether"])
	_free()


func test_mode_rows_mean_nothing_off_the_swell_page() -> void:
	_sandbox(&"swell_modes")
	_to_turn_of(&"rhen")
	var row := {"id": "swell_mode_wake", BattleMenus.KEY_SWELL_MODE: &"wake"}
	assert_eq(SwellModeRows.mode_of(ctl, row), &"", "the root page is not the Swell page")
	assert_false(SwellModeRows.highlight(ctl, row))
	var called := [false]
	SwellModeRows.pick(ctl, {"id": "attack"}, func() -> void: called[0] = true)
	assert_true(called[0], "any other row goes on as before")
	assert_eq(SwellModeRows.mode_of(null, row), &"")
	_free()


# --- the timing assist ---------------------------------------------------------------------------


func test_the_assist_is_a_setting_that_defaults_off() -> void:
	var s := UiSettings.new()
	assert_eq(s.timing_assist(), &"off")
	assert_eq(s.options(UiSettings.TIMING_ASSIST), ["off", "wide", "auto", "hold"])
	assert_eq(s.timing_assist_tag_key(), "")
	var row := _ring_row()
	assert_eq(s.timing_input(row), row, "off: the row as swell.json has it")


func test_wide_widens_both_windows_and_keeps_them_inside_the_beat() -> void:
	var s := UiSettings.new()
	assert_true(s.set_value(UiSettings.TIMING_ASSIST, "wide"))
	var k := float((s.data["timing_assist"] as Dictionary)["wide"]["window_scale"])
	for row in _ring_rows():
		var out := s.timing_input(row)
		var beat := float(row["beat_sec"])
		var peak := float(row["peak_at"]) * beat
		assert_true(float(out["good_sec"]) > float(row["good_sec"]), "%s: wider good" % row["id"])
		assert_true(float(out["good_sec"]) <= float(row["good_sec"]) * k + 1e-9)
		assert_true(peak - float(out["good_sec"]) >= 0.0, "the early edge stays in the beat")
		assert_true(peak + float(out["good_sec"]) <= beat + 1e-9, "the late edge stays in the beat")
		assert_true(float(out["perfect_sec"]) > float(row["perfect_sec"]), "wider perfect")
		assert_true(float(out["perfect_sec"]) <= float(out["good_sec"]))
		assert_true(float(row["max_step_sec"]) <= float(out["perfect_sec"]), "a frame step still fits a grade")
		assert_eq(float(row["good_sec"]), float(_ring_row()["good_sec"]), "the data row is not touched")
	assert_eq(s.timing_assist_tag_key(), "HUD_SWELL_ASSIST_WIDE")
	var tight := {"kind": "timing_ring", "beat_sec": 1.0, "peak_at": 0.9, "perfect_sec": 0.05, "good_sec": 0.08}
	assert_between(float(s.timing_input(tight)["good_sec"]), 0.1 - 1e-6, 0.1 + 1e-6, "clamped to the late room")


func test_auto_makes_every_miss_good_and_presses_can_still_be_perfect() -> void:
	var s := UiSettings.new()
	assert_true(s.set_value(UiSettings.TIMING_ASSIST, "auto"))
	var out := s.timing_input(_ring_row())
	assert_eq(out["assist_floor"], "good")
	assert_eq(float(out["good_sec"]), float(_ring_row()["good_sec"]), "auto leaves the windows alone")
	var ring := SwellTimingRing.new(out)
	ring.advance(ring.time_to_peak())
	assert_eq(ring.press(), SwellTimingRing.GRADE_PERFECT)
	ring.advance(ring.duration_sec())
	assert_eq(ring.grades, [&"perfect", &"good", &"good"] as Array[StringName])


func test_the_battle_ring_plays_the_assisted_row_and_shows_the_tag() -> void:
	_sandbox(&"swell_ring")
	var s := UiSettings.new()
	s.set_value(UiSettings.TIMING_ASSIST, "auto")
	ctl.hud.apply_settings(s)
	assert_eq(ctl.hud.swell_ring.assist_text(), tr("HUD_SWELL_ASSIST_AUTO"))
	_to_turn_of(&"rhen")
	ctl.hud.commands.select(BattleMenus.ROW_SWELL)
	_press(&"ui_accept")
	_press(&"ui_accept")
	ctl.aim_at(&"gull_harrier")
	_press(&"ui_accept")
	var ring := ctl.swell_input()
	assert_eq(ring.assist_floor, SwellInput.QUALITY_GOOD, "the ring was built from the assisted row")
	ctl.tick(ring.duration_sec())
	var good := int((_ring_row()["grades"] as Dictionary)["good"])
	assert_true(ctl.hud.help_history.has(ctl.menus.swell_result_text([&"good", &"good", &"good"], good * 3)))
	s.set_value(UiSettings.TIMING_ASSIST, "off")
	assert_eq(ctl.hud.swell_ring.assist_text(), "", "the tag follows the setting live")
	_free()


func test_every_assist_option_is_documented_with_a_tag() -> void:
	var s := UiSettings.new()
	var assists: Dictionary = s.data["timing_assist"]
	for opt: Variant in s.options(UiSettings.TIMING_ASSIST):
		assert_true(assists.has(str(opt)), "%s has a recipe" % opt)
		var tag := str((assists[str(opt)] as Dictionary).get("tag_key", ""))
		if str(opt) != "off":
			assert_ne(tr(tag), tag, "%s's tag is localized" % opt)


func test_auto_floors_every_input_kind_at_its_played_at_good_result() -> void:  # merged with M2-CMB-01
	var s := UiSettings.new()
	s.set_value(UiSettings.TIMING_ASSIST, "auto")
	var kinds: Array[StringName] = []
	for row: Variant in BattleSwell.load_config().get("inputs", []):
		var plain := row as Dictionary
		var input := SwellInput.create(s.timing_input(plain))
		if not kinds.has(input.kind):
			kinds.append(input.kind)
		input.advance(input.duration_sec() + 1.0)  # the player does nothing at all
		assert_true(input.is_done(), "%s ran out" % plain["id"])
		var good := SwellInput.scripted_result(plain, SwellInput.QUALITY_GOOD)
		assert_eq(input.grades, good[BattleSwell.RESULT_GRADES], "%s: every miss became its good grade" % plain["id"])
		assert_eq(input.raw_misses, input.grade_count(), "%s: the misses as played are still counted" % plain["id"])
		var bonus := BattleSwell.bonus_pct(plain, input.result())
		assert_eq(bonus, BattleSwell.bonus_pct(plain, good), "%s: the played-at-good bonus" % plain["id"])
	assert_eq(kinds.size(), SwellInput.KINDS.size(), "every kind in swell.json is covered")


func test_auto_never_earns_the_glyph_s_swift() -> void:
	var s := UiSettings.new()
	s.set_value(UiSettings.TIMING_ASSIST, "auto")
	var glyph := SwellInput.create(s.timing_input(_row_of(SwellInput.KIND_GLYPH))) as SwellGlyph
	glyph.advance(glyph.lead_in_sec)
	for i in glyph.strokes.size():  # fast, but every stroke wrong
		glyph.press(SwellInput.BUTTON_UP if glyph.strokes[i] != SwellInput.BUTTON_UP else SwellInput.BUTTON_DOWN)
	assert_true(glyph.is_done())
	assert_eq(glyph.grades[-1], SwellInput.GRADE_MISS, "swift asks for a clean trace as played")


func test_wide_keeps_every_kind_within_the_validator_rules() -> void:
	var s := UiSettings.new()
	s.set_value(UiSettings.TIMING_ASSIST, "wide")
	var limits: Dictionary = s.data["timing_assist"]
	for row: Variant in BattleSwell.load_config().get("inputs", []):
		var plain := row as Dictionary
		var out := s.timing_input(plain)
		var id := str(plain["id"])
		match StringName(str(plain["kind"])):
			SwellInput.KIND_GLYPH:
				assert_true(float(out["window_sec"]) > float(plain["window_sec"]), "%s: a longer window" % id)
				var total := float(out["lead_in_sec"]) + float(out["window_sec"])
				assert_true(total <= float(limits["max_duration_sec"]) + 1e-9, "%s stays short" % id)
				assert_true(float(out["swift_sec"]) <= float(out["window_sec"]))
			SwellInput.KIND_CHANT:
				assert_true(float(out["good_sec"]) > float(plain["good_sec"]), "%s: wider" % id)
				var notes: Array = out["notes"]
				for i in range(1, notes.size()):
					var gap := float(notes[i]["at"]) - float(notes[i - 1]["at"])
					assert_true(gap >= 2.0 * float(out["good_sec"]) - 1e-9, "%s: windows never overlap" % id)
			SwellInput.KIND_BRACE:
				assert_true(float(out["good_sec"]) > float(plain["good_sec"]), "%s: wider" % id)
				var last := 0.0
				for t: Variant in out["impacts"]:
					last = maxf(last, float(t))
				assert_true(
					float(out["counter_at"]) - float(out["good_sec"]) > last, "%s: opens after the last blow" % id
				)
			SwellInput.KIND_TIMING_RING:
				assert_true(float(out["good_sec"]) > float(plain["good_sec"]), "%s: wider" % id)
		if out.has("perfect_sec"):
			assert_true(float(out["perfect_sec"]) <= float(out["good_sec"]), "%s: perfect within good" % id)
			assert_true(float(out["max_step_sec"]) <= float(out["perfect_sec"]), "%s: a frame fits a grade" % id)


func _row_of(kind: StringName) -> Dictionary:
	for row: Variant in BattleSwell.load_config().get("inputs", []):
		if StringName(str((row as Dictionary).get("kind", ""))) == kind:
			return row as Dictionary
	return {}


# --- helpers -------------------------------------------------------------------------------------


func _ring_rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for row: Variant in BattleSwell.load_config().get("inputs", []):
		if str((row as Dictionary).get("kind", "")) == "timing_ring":
			out.append(row as Dictionary)
	return out


func _ring_row() -> Dictionary:
	return _ring_rows()[0]


func _sandbox(fixture_id: StringName) -> void:
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.hud.apply_settings(UiSettings.new())
	ctl.start_fixture(BattleFixture.load_fixture(fixture_id))


func _open_page(fixture_id: StringName) -> void:
	_sandbox(fixture_id)
	_to_turn_of(&"rhen")
	ctl.hud.commands.select(BattleMenus.ROW_SWELL)
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_SWELL)


func _to_turn_of(cid: StringName) -> void:
	var guard := 0
	while ctl.current_actor_id() != cid and guard < CtbTimeline.PREVIEW_LENGTH:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])


func _order() -> Array[String]:
	var out: Array[String] = []
	for t in ctl.engine.preview():
		out.append("%s@%d" % [t.combatant_id, t.time])
	return out


func _press(action: StringName) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	ctl.handle_input(ev)


func _free() -> void:
	if ctl != null:
		ctl.get_parent().remove_child(ctl)
		ctl.free()
		ctl = null
