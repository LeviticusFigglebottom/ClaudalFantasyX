extends TestCase
## M2-UI-26 (input parity): every hero's Swell input (Rhen's timing ring, Asha's chant, Toma's
## brace, Ysolde's glyph) played to a clean finish, and backed out of, with the keyboard, the
## controller and the mouse (a click for Confirm, a click on the figure's side for a direction, a
## held click for a hold, a right click for Cancel), through real InputEvents (InputDriver).

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const DIRECTION_ACTIONS := {
	SwellInput.BUTTON_UP: &"ui_up",
	SwellInput.BUTTON_DOWN: &"ui_down",
	SwellInput.BUTTON_LEFT: &"ui_left",
	SwellInput.BUTTON_RIGHT: &"ui_right",
}
## Where the mouse clicks for a direction: this far from the figure's centre (past swell_centre_px).
const SIDE_PX := 150.0
## fixture id -> [hero, target base id] (the fixtures each open with that hero's gauge full).
const KINDS := {
	&"swell_ring": [&"rhen", &"gull_harrier"],
	&"swell_chant": [&"asha", &""],
	&"swell_brace": [&"toma", &"gull_harrier"],
	&"swell_glyph": [&"ysolde", &"gull_harrier"],
}

var ctl: BattleController
var settings: UiSettings


func before_each() -> void:
	InputDriver.clear_screen()
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	settings = UiSettings.new()
	ctl.hud.apply_settings(settings)


func test_every_input_plays_clean_with_each_device() -> void:
	for fixture: StringName in KINDS:
		for kind in InputDriver.KINDS:
			var d := InputDriver.new(kind)
			var input := _open(fixture)
			var label := "%s, %s" % [fixture, d.label()]
			_play_clean(d, input)
			assert_true(input.is_done() and not input.cancelled, "%s: the input finished" % label)
			assert_eq(input.raw_misses, 0, "%s: not one step missed" % label)
			assert_ne(ctl.state, BattleController.STATE_SWELL_INPUT, "%s: the technique was unleashed" % label)
			_free()
			before_each()
	_free()


func test_cancel_backs_out_of_every_input_with_each_device() -> void:
	for fixture: StringName in KINDS:
		for kind in InputDriver.KINDS:
			var d := InputDriver.new(kind)
			var input := _open(fixture)
			var label := "%s, %s" % [fixture, d.label()]
			if kind == InputDriver.Kind.MOUSE:
				InputDriver.right_click(ctl.hud.swell_ring)
			else:
				d.press(&"ui_cancel")
			assert_true(input.cancelled, "%s: Cancel backs out before the first step" % label)
			assert_eq(ctl.state, BattleController.STATE_TARGET, "%s: back to the target pick" % label)
			assert_true(ctl.hud.commands.visible, "%s: the menu is back" % label)
			_free()
			before_each()
	_free()


func test_the_click_that_chose_the_target_plays_no_step() -> void:
	# The mouse opens the input with a click: its release lands on the open input and must not
	# count (only a press made while the input is open does).
	var input := _open(&"swell_brace")
	InputDriver.button_at(_centre(), MOUSE_BUTTON_LEFT, false)
	assert_false((input as SwellBrace).holding, "a stray release holds nothing")
	assert_true(input.grades.is_empty())
	_free()


func test_hold_to_confirm_plays_with_a_held_click() -> void:
	# The timing assist "hold" (M2-UI-14): holding the left button in the figure's centre plays a
	# direction input (the chant) by itself, as holding Confirm does.
	settings.set_value(UiSettings.TIMING_ASSIST, "hold")
	var input := _open(&"swell_chant")
	assert_true(input.assist_hold)
	InputDriver.button_at(_centre(), MOUSE_BUTTON_LEFT, true)
	assert_true(input.held, "the held click holds Confirm")
	ctl.tick(input.duration_sec() + 1.0)
	assert_true(input.is_done() and not input.cancelled, "the chant plays itself")
	InputDriver.button_at(_centre(), MOUSE_BUTTON_LEFT, false)
	_free()


# --- helpers --------------------------------------------------------------------------------------


## Opens the fixture's hero's Swell technique on its target, through the menus with key actions
## (the menus' own parity is test_input_parity_battle).
func _open(fixture: StringName) -> SwellInput:
	var hero: StringName = KINDS[fixture][0]
	var target: StringName = KINDS[fixture][1]
	ctl.start_fixture(BattleFixture.load_fixture(fixture))
	var guard := 0
	while ctl.current_actor_id() != hero and guard < CtbTimeline.PREVIEW_LENGTH:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	ctl.hud.commands.select(BattleMenus.ROW_SWELL)
	_act(&"ui_accept")
	_act(&"ui_accept")
	if target != &"":
		ctl.aim_at(target)
	_act(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_SWELL_INPUT, "%s opens" % fixture)
	return ctl.swell_input()


func _play_clean(d: InputDriver, input: SwellInput) -> void:
	if input is SwellBrace:
		var brace := input as SwellBrace
		_down(d, SwellInput.BUTTON_ACCEPT)
		while brace.blows_left() > 0:
			ctl.tick(brace.time_to_peak())
		ctl.tick(brace.time_to_peak())
		_up(d, SwellInput.BUTTON_ACCEPT)
		return
	if input is SwellGlyph:
		ctl.tick(input.lead_in_sec)  # the strokes count once the wind-up is over
	var guard := 0
	while not input.is_done() and guard < 32:
		guard += 1
		if not (input is SwellGlyph):
			ctl.tick(input.time_to_peak())
		var button := SwellInput.BUTTON_ACCEPT
		if input is SwellChant:
			button = (input as SwellChant).expected_button()
		elif input is SwellGlyph:
			button = (input as SwellGlyph).expected_button()
		_down(d, button)
		_up(d, button)


func _down(d: InputDriver, button: StringName) -> void:
	if d.kind == InputDriver.Kind.MOUSE:
		InputDriver.button_at(_point_for(button), MOUSE_BUTTON_LEFT, true)
	else:
		d.hold(_action(button))


func _up(d: InputDriver, button: StringName) -> void:
	if d.kind == InputDriver.Kind.MOUSE:
		InputDriver.button_at(_point_for(button), MOUSE_BUTTON_LEFT, false)
	else:
		d.let_go(_action(button))


func _action(button: StringName) -> StringName:
	return DIRECTION_ACTIONS.get(button, &"ui_accept")


## Where the mouse clicks for `button`: the figure's centre for Confirm, its side for a direction.
func _point_for(button: StringName) -> Vector2:
	return _centre() + SwellRingView.direction(button) * SIDE_PX


func _centre() -> Vector2:
	var view := ctl.hud.swell_ring
	return view.get_global_transform_with_canvas() * view.figure_center()


func _act(action: StringName) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	ctl.handle_input(ev)


func _free() -> void:
	if is_instance_valid(ctl):
		ctl.get_parent().remove_child(ctl)
		ctl.free()
