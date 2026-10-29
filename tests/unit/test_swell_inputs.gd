extends TestCase
## M2-CMB-01: the other heroes' Swell inputs (SwellChant for Asha, SwellBrace for Toma, SwellGlyph
## for Ysolde), the SwellInput factory and scripted results the simulator plays, the key mapping
## (SwellInputKeys, carry_held) and the HUD gate (SwellRingView.draws). Node-free and deterministic: time moves
## only through advance(). Rhen's ring keeps its own tests (test_battle_swell_hud.gd).

const CHANT := {
	"id": "c",
	"kind": "chant",
	"lead_in_sec": 0.5,
	"perfect_sec": 0.05,
	"good_sec": 0.15,
	"max_step_sec": 0.05,
	"notes": [{"button": "up", "at": 0.0}, {"button": "left", "at": 0.5}, {"button": "down", "at": 1.0}],
	"grades": {"perfect": 20, "good": 10, "miss": 0},
}
const BRACE := {
	"id": "b",
	"kind": "brace",
	"lead_in_sec": 0.5,
	"impacts": [0.2, 0.6],
	"counter_at": 1.2,
	"perfect_sec": 0.05,
	"good_sec": 0.15,
	"max_step_sec": 0.05,
	"grades": {"braced": 10, "perfect": 50, "good": 20, "miss": 0},
}
const GLYPH := {
	"id": "g",
	"kind": "glyph",
	"lead_in_sec": 0.5,
	"window_sec": 2.0,
	"swift_sec": 1.0,
	"max_step_sec": 0.05,
	"strokes": ["down", "right", "up"],
	"grades": {"traced": 10, "swift": 30, "miss": 0},
}
const UP := SwellInput.BUTTON_UP
const DOWN := SwellInput.BUTTON_DOWN
const LEFT := SwellInput.BUTTON_LEFT
const RIGHT := SwellInput.BUTTON_RIGHT
const ACCEPT := SwellInput.BUTTON_ACCEPT

# --- the factory and scripted results --------------------------------------------------------


func test_create_builds_each_kind_and_refuses_unknown_ones() -> void:
	assert_true(SwellInput.create({"kind": "timing_ring"}) is SwellTimingRing)
	assert_true(SwellInput.create(CHANT) is SwellChant)
	assert_true(SwellInput.create(BRACE) is SwellBrace)
	assert_true(SwellInput.create(GLYPH) is SwellGlyph)
	assert_eq(SwellInput.create({"kind": "dice"}), null)
	assert_eq(SwellInput.scripted_result({"kind": "dice"}, SwellInput.QUALITY_GOOD), {})
	for row: Dictionary in [CHANT, BRACE, GLYPH]:
		assert_eq(SwellInput.create(row).kind, StringName(str(row["kind"])))


func test_scripted_results_use_each_kinds_grade_names() -> void:
	var good := SwellInput.QUALITY_GOOD
	assert_eq(SwellInput.scripted_result(CHANT, good)["grades"], [&"good", &"good", &"good"] as Array[StringName])
	assert_eq(
		SwellInput.scripted_result(BRACE, SwellInput.QUALITY_PERFECT)["grades"],
		[&"braced", &"braced", &"perfect"] as Array[StringName]
	)
	assert_eq(
		SwellInput.scripted_result(BRACE, SwellInput.QUALITY_MISS)["grades"],
		[&"miss", &"miss", &"miss"] as Array[StringName]
	)
	assert_eq(
		SwellInput.scripted_result(GLYPH, good)["grades"],
		[&"traced", &"traced", &"traced", &"miss"] as Array[StringName]
	)
	assert_eq(
		SwellInput.scripted_result(GLYPH, SwellInput.QUALITY_PERFECT)["grades"],
		[&"traced", &"traced", &"traced", &"swift"] as Array[StringName]
	)
	assert_false(SwellInput.scripted_result(CHANT, good)["cancelled"])


func test_every_live_input_earns_the_same_bonus_at_each_quality() -> void:
	# formulas.md § Swell: played at good every input earns +45%, played perfectly +90%, all missed 0.
	var cfg := BattleSwell.load_config()
	var want := {SwellInput.QUALITY_MISS: 0, SwellInput.QUALITY_GOOD: 45, SwellInput.QUALITY_PERFECT: 90}
	var kinds: Array[StringName] = []
	for row: Dictionary in cfg["inputs"]:
		if not kinds.has(StringName(str(row["kind"]))):
			kinds.append(StringName(str(row["kind"])))
		for q: StringName in want:
			var got := BattleSwell.bonus_pct(row, SwellInput.scripted_result(row, q))
			assert_eq(got, want[q], "%s at %s" % [row["id"], q])
	# M3-C05-06/M3-C06-05: Kerrid's swing is a brace row and Liss's reel-stop a ring row, so kinds repeat.
	assert_eq(kinds, SwellInput.KINDS, "every kind has an input, first met in kind order")
	for hero: Dictionary in cfg["heroes"]:
		var input := BattleSwell.input_row_of(cfg, StringName(str(hero["id"])))
		assert_true(SwellInput.create(input).duration_sec() <= 5.0, "%s's input stays short" % hero["id"])


func test_the_base_input_does_nothing_on_its_own() -> void:
	var base := SwellInput.new({"lead_in_sec": 0.5, "max_step_sec": 0.1})
	assert_eq(base.press(), &"")
	assert_eq(base.release(), &"")
	assert_eq(base.time_to_peak(), 0.0)
	assert_eq(base.duration_sec(), 0.5)
	assert_eq(base.clamp_step(1.0), 0.1)
	assert_eq(base.buttons_used(), [ACCEPT] as Array[StringName])
	assert_eq(base.scripted_grades(SwellInput.QUALITY_GOOD), [&"good"] as Array[StringName])
	base.advance(-1.0)
	assert_eq(base.elapsed, 0.0, "time never runs backwards")
	assert_true(base.cancel())
	assert_true(base.is_done())
	base.advance(1.0)
	assert_eq(base.elapsed, 0.0, "a finished input stops")
	assert_eq(SwellInput.new().clamp_step(3.0), 3.0, "no cap without max_step_sec")


# --- Asha: the chant -------------------------------------------------------------------------


func test_chant_grades_each_note_by_button_and_timing() -> void:
	var c := SwellChant.new(CHANT)
	assert_eq(c.grade_count(), 3)
	assert_eq(c.buttons_used(), SwellInput.DIRECTIONS)
	assert_eq(c.expected_button(), UP)
	assert_eq(c.press(UP), &"", "before the first window: ignored")
	c.advance(0.5)
	assert_eq(c.time_to_peak(), 0.0)
	assert_eq(c.press(ACCEPT), &"", "accept is not a note")
	assert_eq(c.press(UP), &"perfect")
	assert_eq(c.expected_button(), LEFT)
	c.advance(0.4)
	assert_eq(c.press(LEFT), &"good", "0.1 s early")
	assert_eq(c.press(LEFT), &"", "the next window has not opened")
	c.advance(0.6)
	assert_eq(c.press(UP), &"miss", "the wrong button in the window")
	assert_true(c.is_done())
	assert_eq(c.expected_button(), &"")
	assert_eq(c.result()["grades"], [&"perfect", &"good", &"miss"] as Array[StringName])
	assert_eq(c.press(DOWN), &"", "done")


func test_chant_notes_left_unpressed_are_misses() -> void:
	var c := SwellChant.new(CHANT)
	assert_true(is_equal_approx(c.duration_sec(), 1.65))
	c.advance(0.66)
	assert_eq(c.grades, [&"miss"] as Array[StringName], "the first window closed")
	assert_false(c.cancel(), "no cancel once a note is graded")
	c.advance(1.0)
	assert_true(c.is_done())
	assert_eq(c.grades.size(), 3)
	var fresh := SwellChant.new(CHANT)
	assert_true(fresh.cancel(), "cancel before the first grade")
	assert_eq(fresh.press(UP), &"")
	var empty := SwellChant.new({"kind": "chant"})
	assert_true(empty.is_done(), "no notes, nothing to play")
	assert_eq(empty.note_time(3), 0.0)
	assert_eq(empty.duration_sec(), 0.0)


# --- Toma: the brace -------------------------------------------------------------------------


func test_brace_held_through_the_blows_and_released_on_the_counter() -> void:
	var b := SwellBrace.new(BRACE)
	assert_eq(b.grade_count(), 3)
	assert_eq(b.buttons_used(), [ACCEPT] as Array[StringName])
	assert_eq(b.press(UP), &"", "other buttons are ignored")
	assert_false(b.holding)
	assert_eq(b.press(), &"", "starting the hold earns nothing")
	assert_true(b.holding)
	assert_true(is_equal_approx(b.time_to_peak(), 0.7), "to the first blow")
	b.advance(0.75)
	assert_eq(b.grades, [&"braced"] as Array[StringName])
	b.advance(0.4)
	assert_eq(b.blows_left(), 0)
	assert_true(is_equal_approx(b.time_to_peak(), 0.55), "then to the counter")
	b.advance(0.57)
	assert_eq(b.release(UP), &"", "only accept lets go")
	assert_eq(b.release(), &"perfect", "0.02 s past the counter")
	assert_eq(b.result()["grades"], [&"braced", &"braced", &"perfect"] as Array[StringName])
	assert_eq(b.release(), &"", "done")
	assert_true(is_equal_approx(b.duration_sec(), 1.85))


func test_brace_an_unbraced_blow_an_early_release_and_no_release_are_misses() -> void:
	var b := SwellBrace.new(BRACE)
	assert_eq(b.release(), &"", "no hold to let go of")
	b.advance(0.75)
	assert_eq(b.grades, [&"miss"] as Array[StringName], "the first blow landed unbraced")
	b.press()
	b.advance(0.2)
	assert_eq(b.release(), &"miss", "let go before the second blow")
	assert_eq(b.grades, [&"miss", &"miss", &"miss"] as Array[StringName], "the blow to come is a miss too")
	var late := SwellBrace.new(BRACE)
	late.press()
	late.advance(1.0)
	late.advance(1.0)
	assert_true(late.is_done())
	assert_eq(late.grades, [&"braced", &"braced", &"miss"] as Array[StringName], "never let go")
	var good := SwellBrace.new(BRACE)
	good.press()
	good.advance(1.6)
	assert_eq(good.release(), &"good", "0.1 s before the counter")


# --- Ysolde: the glyph -----------------------------------------------------------------------


func test_glyph_a_clean_quick_trace_earns_swift() -> void:
	var g := SwellGlyph.new(GLYPH)
	assert_eq(g.grade_count(), 4)
	assert_eq(g.buttons_used(), SwellInput.DIRECTIONS)
	assert_eq(g.press(DOWN), &"", "strokes before the lead-in ends are ignored")
	g.advance(0.5)
	assert_eq(g.expected_button(), DOWN)
	assert_eq(g.press(ACCEPT), &"", "accept is not a stroke")
	assert_eq(g.press(DOWN), &"traced")
	g.advance(0.3)
	assert_eq(g.press(RIGHT), &"traced")
	assert_true(is_equal_approx(g.time_to_peak(), 0.7), "time left for swift")
	assert_eq(g.press(UP), &"traced")
	assert_true(g.is_done())
	assert_eq(g.expected_button(), &"")
	assert_eq(g.result()["grades"], [&"traced", &"traced", &"traced", &"swift"] as Array[StringName])
	assert_eq(g.press(DOWN), &"", "done")
	assert_eq(g.duration_sec(), 2.5)


func test_glyph_a_slow_or_wrong_trace_misses_swift_and_the_window_closes() -> void:
	var slow := SwellGlyph.new(GLYPH)
	slow.advance(0.5)
	slow.press(DOWN)
	slow.press(RIGHT)
	slow.advance(1.2)
	slow.press(UP)
	assert_eq(slow.grades, [&"traced", &"traced", &"traced", &"miss"] as Array[StringName], "after swift_sec")
	var wrong := SwellGlyph.new(GLYPH)
	wrong.advance(0.5)
	assert_eq(wrong.press(UP), &"miss", "not the stroke the glyph asks for")
	assert_false(wrong.cancel(), "no cancel once a stroke is made")
	assert_eq(wrong.expected_button(), RIGHT, "the trace moves on")
	wrong.press(RIGHT)
	wrong.press(UP)
	assert_eq(wrong.grades.back(), &"miss", "a miss anywhere costs swift")
	var timeout := SwellGlyph.new(GLYPH)
	timeout.advance(0.5)
	timeout.press(DOWN)
	timeout.advance(2.1)
	assert_true(timeout.is_done())
	assert_eq(timeout.grades, [&"traced", &"miss", &"miss", &"miss"] as Array[StringName])


# --- key mapping and the HUD gate ------------------------------------------------------------


func test_keys_reach_only_the_buttons_an_input_uses() -> void:
	var chant := SwellChant.new(CHANT)
	var clock := SwellRingClock.new(chant, func() -> int: return 0)
	clock.step(0.5, false)
	assert_false(SwellInputKeys.feed(_ev(&"ui_accept"), clock, false), "the chant does not use accept")
	assert_true(SwellInputKeys.feed(_ev(&"ui_up"), clock, false))
	assert_eq(chant.grades, [&"perfect"] as Array[StringName])
	assert_false(SwellInputKeys.feed(_ev(&"ui_page_up"), clock, false), "not an input action")
	var brace := SwellBrace.new(BRACE)
	var hold := SwellRingClock.new(brace, func() -> int: return 0)
	assert_false(SwellInputKeys.feed(_ev(&"ui_left"), hold, false), "the brace does not use directions")
	assert_true(SwellInputKeys.feed(_ev(&"ui_accept"), hold, false))
	assert_true(brace.holding)
	hold.step(1.72, false)
	assert_true(SwellInputKeys.feed(_ev(&"ui_accept", false), hold, false), "letting go is handled")
	assert_eq(brace.grades, [&"braced", &"braced", &"perfect"] as Array[StringName])
	var glyph := SwellGlyph.new(GLYPH)
	assert_true(SwellInputKeys.feed(_ev(&"ui_cancel"), SwellRingClock.new(glyph, func() -> int: return 0), false))
	assert_true(glyph.cancelled)


func test_the_hud_draws_every_kind() -> void:
	# M2-UI-03 gave the chant, brace and glyph their panels.
	for kind in ["timing_ring", "chant", "brace", "glyph"]:
		assert_true(SwellRingView.draws({"kind": kind}), kind)
	assert_false(SwellRingView.draws({"kind": ""}))
	for cid: StringName in [&"rhen", &"asha", &"toma", &"ysolde"]:
		assert_true(SwellRingView.draws_hero(cid), String(cid))
	assert_false(SwellRingView.draws_hero(&"nobody"))


func test_brace_a_release_in_the_lead_in_only_lets_go() -> void:
	# M2-UI-03 (from M2-NIT-03): the tap that chose the technique cannot spoil the brace.
	var b := SwellBrace.new(BRACE)
	b.press()
	b.advance(0.1)
	assert_eq(b.release(), &"", "nothing is graded in the lead-in")
	assert_false(b.holding)
	assert_true(b.grades.is_empty())
	b.press()
	assert_true(b.holding, "pressing again holds again")
	b.advance(0.65)
	assert_eq(b.grades, [&"braced"] as Array[StringName])


func test_an_accept_still_held_starts_the_brace() -> void:
	var held := func(action: StringName) -> bool: return action == &"ui_accept"
	var free := func(_action: StringName) -> bool: return false
	var brace := SwellBrace.new(BRACE)
	assert_true(SwellInputKeys.carry_held(SwellRingClock.new(brace, func() -> int: return 0), held))
	assert_true(brace.holding)
	var other := SwellBrace.new(BRACE)
	assert_false(SwellInputKeys.carry_held(SwellRingClock.new(other, func() -> int: return 0), free))
	assert_false(other.holding, "nothing held, nothing carried")
	var chant := SwellChant.new(CHANT)
	assert_false(SwellInputKeys.carry_held(SwellRingClock.new(chant, func() -> int: return 0), held))
	assert_true(chant.grades.is_empty(), "only a hold-and-release input takes the held accept")


# --- helpers --------------------------------------------------------------------------------


static func _ev(action: StringName, pressed: bool = true) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = pressed
	return ev
