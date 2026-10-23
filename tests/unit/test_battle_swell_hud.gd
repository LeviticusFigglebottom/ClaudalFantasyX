extends TestCase
## M1-CMB-04: the Swell in the battle scene: the party-row gauge, the Swell command and page, and
## Rhen's timing ring driven by simulated ui_* input and tick(), on the sandbox scene with the
## frozen capture fixtures (battle_fixtures.json).

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"

var ctl: BattleController


func before_each() -> void:
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)


func test_only_heroes_with_a_swell_get_a_gauge_and_it_starts_empty() -> void:
	_fixture(&"player_preview")
	var rhen := ctl.hud.party.row_for(&"rhen")
	assert_true(rhen.swell_gauge() != null, "Rhen has a Swell")
	assert_eq(rhen.swell_gauge().shown, 0.0)
	assert_eq(rhen.swell_gauge().glow, 0.0, "no glow until full")
	assert_true(ctl.hud.party.row_for(&"asha").swell_gauge() == null, "no swell.json row, no gauge")
	_to_turn_of(&"rhen")
	assert_false(_row_ids().has(BattleMenus.ROW_SWELL), "no Swell command until the gauge is full")
	_free()


func test_a_full_gauge_glows_pulses_and_puts_swell_on_the_menu() -> void:
	_fixture(&"swell_ring")
	var row := ctl.hud.party.row_for(&"rhen")
	assert_eq(row.swell_gauge().shown, 1.0)
	assert_true(row.swell_gauge().glow > 0.0, "full: framed in gold")
	var before := row.swell_gauge().glow
	row._process(0.4)
	assert_ne(row.swell_gauge().glow, before, "it pulses")
	ctl.hud.party.set_reduced_motion(true)
	ctl.hud.party.refresh()
	assert_eq(row.swell_gauge().glow, 1.0, "reduced motion holds the glow")
	_to_turn_of(&"rhen")
	var rows := ctl.hud.commands.top_page().rows
	assert_eq(StringName(str(rows[1]["id"])), BattleMenus.ROW_SWELL, "right under Attack")
	assert_eq(str(rows[1]["right"]), tr("SWELL_INPUT_TIMING_RING"), "it names the input")
	ctl.hud.commands.select(BattleMenus.ROW_SWELL)
	assert_eq(ctl.hud.help_text(), tr("HUD_HELP_SWELL_FMT").format({"name": tr("CHAR_RHEN")}))
	_free()


func test_three_perfect_flares_unleash_lamp_dive_and_empty_the_gauge() -> void:
	_open_ring()
	var ring := ctl.swell_input()
	assert_true(ctl.hud.swell_ring.is_open())
	assert_false(ctl.hud.commands.visible, "the input has the screen")
	var foe := ctl.engine.find(&"gull_harrier#3")
	var hp := foe.hp
	for i in ring.beats:
		ctl.tick(ring.time_to_peak())
		_press(&"ui_accept")
	assert_ne(ctl.state, BattleController.STATE_SWELL_INPUT)
	assert_false(ctl.hud.swell_ring.is_open())
	assert_true(ctl.engine.find(&"rhen").swell < Formulas.SWELL_MAX, "spent (the foes' turns since may refill it)")
	assert_true(foe.hp < hp, "Lamp Dive landed on the picked foe")
	var expected := ctl.menus.swell_result_text([&"perfect", &"perfect", &"perfect"], 90)
	assert_true(ctl.hud.help_history.has(expected), "the help line said what the input earned: %s" % expected)
	_free()


func test_waiting_out_the_ring_still_strikes_at_base_power() -> void:
	_open_ring()
	ctl.tick(ctl.swell_input().duration_sec())
	assert_ne(ctl.state, BattleController.STATE_SWELL_INPUT)
	assert_true(ctl.engine.find(&"rhen").swell < Formulas.SWELL_MAX)
	assert_true(ctl.hud.help_history.has(ctl.menus.swell_result_text([&"miss", &"miss", &"miss"], 0)))
	_free()


func test_cancel_backs_out_to_the_pick_then_the_swell_page_with_nothing_spent() -> void:
	_open_ring()
	var actor := ctl.current_actor_id()
	_press(&"ui_cancel")
	assert_eq(ctl.state, BattleController.STATE_TARGET, "back to the target pick")
	assert_false(ctl.hud.swell_ring.is_open())
	assert_true(ctl.hud.commands.visible)
	assert_eq(ctl.current_actor_id(), actor, "the turn is still Rhen's")
	assert_eq(ctl.engine.find(&"rhen").swell, Formulas.SWELL_MAX, "the gauge is kept")
	_press(&"ui_cancel")
	assert_eq(ctl.state, BattleController.STATE_SWELL, "back to the Swell page, not Skills")
	_press(&"ui_cancel")
	assert_eq(ctl.state, BattleController.STATE_COMMAND)
	_free()


func test_no_cancel_once_a_flare_is_struck() -> void:
	_open_ring()
	var ring := ctl.swell_input()
	assert_eq(ctl.hud.swell_ring.hint_text(), tr("HUD_SWELL_RING_HINT"))
	ctl.tick(ring.time_to_peak())
	_press(&"ui_accept")
	assert_eq(ctl.hud.swell_ring.hint_text(), tr("HUD_SWELL_RING_HINT_LOCKED"), "the hint drops Cancel")
	assert_true(ctl.handle_input(_ev(&"ui_cancel")), "consumed")
	assert_eq(ctl.state, BattleController.STATE_SWELL_INPUT, "no retrying a started input")
	assert_false(ctl.handle_input(_ev(&"ui_left")), "other input is not the ring's")
	_free()


func test_unleash_refusals_explain_themselves() -> void:
	_fixture(&"player_preview")
	_to_turn_of(&"rhen")
	var foe: Array[StringName] = [ctl.engine.living_foes_of(ctl.engine.current)[0].id]
	var r := ctl.unleash(&"lamp_dive", foe, {"cancelled": false, "grades": []})
	assert_eq(r.fail_reason, BattleSwell.FAIL_NOT_FULL)
	assert_eq(ctl.state, BattleController.STATE_COMMAND)
	assert_eq(ctl.hud.help_text(), ctl.menus.fail_text(BattleSwell.FAIL_NOT_FULL, ctl.engine.current))
	assert_false(ctl.hud.help_text().contains("{"), "formatted")
	ctl.engine.outcome = BattleEngine.OUTCOME_ESCAPED  # nobody's turn any more
	assert_eq(ctl.unleash(&"lamp_dive", foe, {}).fail_reason, &"not_your_turn")
	_free()


func test_the_technique_page_previews_its_input_and_its_turn() -> void:
	_fixture(&"swell_ring")
	_to_turn_of(&"rhen")
	ctl.hud.commands.select(BattleMenus.ROW_SWELL)
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_SWELL)
	assert_eq(ctl.hud.commands.page_id(), BattleMenus.PAGE_SWELL)
	assert_eq(_row_ids(), [&"lamp_dive"] as Array[StringName])
	assert_true(ctl.hud.help_text().begins_with(tr("SWELL_INPUT_TIMING_RING_HELP")), ctl.hud.help_text())
	var preview := ctl.engine.preview(
		&"lamp_dive", ctl.default_targets(&"lamp_dive")[0], CtbTimeline.PREVIEW_LENGTH - 1
	)
	var ghost := 0
	for s in ctl.hud.timeline.slots:
		if bool(s["ghost"]):
			ghost = int(s["slot"])
	assert_true(ghost > 0, "the ghost chip shows when Rhen acts again (rank 2)")
	assert_true(preview.size() > 0)
	_free()


func test_the_capture_script_freezes_the_ring_mid_beat() -> void:
	ctl.run_script(BattleController.SCRIPT_SWELL_RING)
	assert_eq(ctl.state, BattleController.STATE_SWELL_INPUT)
	var ring := ctl.swell_input()
	assert_eq(ring.grades, [&"perfect"] as Array[StringName])
	assert_false(ctl.swell_input_live)
	var at := ring.elapsed
	ctl.tick(1.0)
	assert_eq(ring.elapsed, at, "frozen for the capture")
	assert_true(ctl.hud.swell_ring.closing_radius() > HudLayout.num(HudLayout.section(&"swell_ring"), "lamp_radius"))
	_free()


func test_ring_view_brightness_and_closing_radius_follow_the_beat() -> void:
	var view := ctl.hud.swell_ring
	var m := HudLayout.section(&"swell_ring")
	assert_eq(view.brightness(), 0.0, "nothing open")
	assert_eq(view.closing_radius(), HudLayout.num(m, "ring_radius"))
	view.reduced_motion = true
	var ring := SwellTimingRing.new(BattleSwell.load_config()["inputs"][0])
	view.open(ring, "Lamp Dive", "hint")
	assert_eq(view.closing_radius(), HudLayout.num(m, "ring_radius"), "outer edge in the lead-in")
	var dim := view.brightness()
	ring.advance(ring.time_to_peak())
	assert_eq(view.brightness(), 1.0, "brightest at the peak (no flicker with reduced motion)")
	assert_true(dim < 1.0)
	assert_eq(view.closing_radius(), HudLayout.num(m, "lamp_radius"), "the ring meets the lamp at the peak")
	view.reduced_motion = false
	assert_true(view.brightness() <= 1.0)
	view.close()
	assert_false(view.is_open())
	_free()


# --- helpers ------------------------------------------------------------------------------


func _fixture(fid: StringName) -> void:
	ctl.start_fixture(BattleFixture.load_fixture(fid))


## Swell -> Lamp Dive -> the Gull Harrier -> the ring opens.
func _open_ring() -> void:
	_fixture(&"swell_ring")
	_to_turn_of(&"rhen")
	ctl.hud.commands.select(BattleMenus.ROW_SWELL)
	_press(&"ui_accept")
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_TARGET)
	ctl.aim_at(&"gull_harrier")
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_SWELL_INPUT)


func _to_turn_of(cid: StringName) -> void:
	var guard := 0
	while ctl.current_actor_id() != cid and guard < CtbTimeline.PREVIEW_LENGTH:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])


func _row_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for r in ctl.hud.commands.top_page().rows:
		out.append(StringName(str(r["id"])))
	return out


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


func _press(action: StringName) -> void:
	ctl.handle_input(_ev(action))


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
