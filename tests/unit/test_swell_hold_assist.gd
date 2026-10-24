extends TestCase
## M2-UI-14: the timing assist "hold" (hold to confirm). Each kind's input built from the assisted
## row (UiSettings.timing_input) plays every step at Good while Confirm is held, finishes on its
## own, never earns Swift, and hands the steps back when Confirm is let go. Driven through
## SwellInputKeys and SwellRingClock like the battle, with a frozen clock.

var s: UiSettings


func before_each() -> void:
	s = UiSettings.new()
	s.set_value(UiSettings.TIMING_ASSIST, "hold")


func test_the_option_marks_the_row_and_has_its_tag() -> void:
	var row := s.timing_input(_row(&"rhen"))
	assert_true(bool(row["assist_hold"]))
	assert_eq(row["assist_floor"], "good")
	assert_eq(s.timing_assist_tag_key(), "HUD_SWELL_ASSIST_HOLD")
	assert_ne(tr("HUD_SWELL_ASSIST_HOLD"), "HUD_SWELL_ASSIST_HOLD")
	var off := UiSettings.new()
	assert_false(off.timing_input(_row(&"rhen")).has("assist_hold"), "only the hold option sets it")


func test_holding_confirm_plays_every_kind_at_good() -> void:
	for hero: StringName in [&"rhen", &"asha", &"toma", &"ysolde"]:
		var input := SwellInput.create(s.timing_input(_row(hero)))
		var clock := _clock(input)
		assert_true(SwellInputKeys.feed(_ev(&"ui_accept", true), clock, false), "%s takes Confirm" % hero)
		assert_true(input.held)
		input.advance(input.duration_sec() + 1.0)
		assert_true(input.is_done(), "%s finishes by itself" % hero)
		var want := input.scripted_grades(SwellInput.QUALITY_GOOD)
		assert_eq(input.grades, want, "%s plays at Good" % hero)


func test_letting_go_hands_the_steps_back() -> void:
	var chant := SwellInput.create(s.timing_input(_row(&"asha"))) as SwellChant
	var clock := _clock(chant)
	SwellInputKeys.feed(_ev(&"ui_accept", true), clock, false)
	clock.step(chant.note_time(0) + chant.good_sec + 0.01, false)
	assert_eq(chant.grades, [&"good"] as Array[StringName], "held: the first note plays itself")
	SwellInputKeys.feed(_ev(&"ui_accept", false), clock, false)
	assert_false(chant.held)
	clock.step(chant.note_time(1) - chant.elapsed + chant.good_sec + 0.01, false)
	assert_eq(chant.grades[-1], SwellInput.GRADE_MISS, "let go: a note left alone is a miss again")
	clock.step(chant.note_time(2) - chant.elapsed, false)
	SwellInputKeys.feed(_ev(&"ui_" + String(chant.expected_button()), true), clock, false)
	assert_eq(chant.grades[-1], SwellInput.GRADE_PERFECT, "and the player can sing by hand")


func test_the_glyph_never_earns_swift_from_the_hold() -> void:
	var glyph := SwellInput.create(s.timing_input(_row(&"ysolde"))) as SwellGlyph
	var clock := _clock(glyph)
	SwellInputKeys.feed(_ev(&"ui_accept", true), clock, false)
	glyph.advance(glyph.duration_sec() + 1.0)
	assert_eq(glyph.grades[-1], SwellInput.GRADE_MISS, "Swift needs a clean trace by hand")


func test_an_accept_held_from_the_menu_starts_holding_any_kind() -> void:
	var held := func(action: StringName) -> bool: return action == &"ui_accept"
	var ring := SwellInput.create(s.timing_input(_row(&"rhen")))
	assert_true(SwellInputKeys.carry_held(_clock(ring), held))
	assert_true(ring.held)
	var plain := SwellInput.create(UiSettings.new().timing_input(_row(&"rhen")))
	assert_false(SwellInputKeys.carry_held(_clock(plain), held), "no hold assist: the ring ignores it")
	assert_false(plain.held)


func test_without_the_hold_assist_confirm_is_not_taken_by_a_direction_input() -> void:
	var chant := SwellInput.create(UiSettings.new().timing_input(_row(&"asha")))
	assert_false(SwellInputKeys.feed(_ev(&"ui_accept", true), _clock(chant), false))


func _row(hero: StringName) -> Dictionary:
	return BattleSwell.input_row_of(BattleSwell.load_config(), hero)


func _clock(input: SwellInput) -> SwellRingClock:
	return SwellRingClock.new(input, func() -> int: return 0)


func _ev(action: StringName, pressed: bool) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = pressed
	return ev
