extends TestCase
## M1-CMB-04: Rhen's Swell input, the lantern-flicker timing ring (SwellTimingRing). Node-free
## input logic, driven here exactly as the HUD drives it: advance(), press(), cancel().

const CFG := {
	"beats": 3,
	"lead_in_sec": 0.5,
	"beat_sec": 1.0,
	"peak_at": 0.5,
	"perfect_sec": 0.05,
	"good_sec": 0.2,
}

var ring: SwellTimingRing


func before_each() -> void:
	ring = SwellTimingRing.new(CFG)


func test_grades_by_distance_from_the_peak() -> void:
	assert_eq(SwellTimingRing.grade_for(0.0, 0.05, 0.2), SwellTimingRing.GRADE_PERFECT)
	assert_eq(SwellTimingRing.grade_for(-0.05, 0.05, 0.2), SwellTimingRing.GRADE_PERFECT, "early counts the same")
	assert_eq(SwellTimingRing.grade_for(0.1, 0.05, 0.2), SwellTimingRing.GRADE_GOOD)
	assert_eq(SwellTimingRing.grade_for(-0.2, 0.05, 0.2), SwellTimingRing.GRADE_GOOD)
	assert_eq(SwellTimingRing.grade_for(0.21, 0.05, 0.2), SwellTimingRing.GRADE_MISS)


func test_three_presses_on_the_peaks_are_perfect() -> void:
	for i in 3:
		ring.advance(ring.time_to_peak())
		assert_eq(ring.press(), SwellTimingRing.GRADE_PERFECT, "beat %d" % i)
	assert_true(ring.is_done(), "done on the last press, without waiting out the beat")
	var r := ring.result()
	assert_false(bool(r[BattleSwell.RESULT_CANCELLED]))
	assert_eq(r[BattleSwell.RESULT_GRADES], [&"perfect", &"perfect", &"perfect"] as Array[StringName])


func test_a_press_before_the_beat_opens_is_ignored() -> void:
	ring.advance(0.2)
	assert_eq(ring.press(), &"", "still in the lead-in")
	assert_true(ring.grades.is_empty())
	ring.advance(ring.time_to_peak())
	assert_eq(ring.press(), SwellTimingRing.GRADE_PERFECT)
	assert_eq(ring.press(), &"", "one press per beat: beat 2 has not opened")
	assert_eq(ring.grades.size(), 1)


func test_an_unpressed_beat_is_a_miss_and_late_presses_grade_down() -> void:
	ring.advance(ring.beat_start(1) + 0.01)
	assert_eq(ring.grades, [&"miss"] as Array[StringName], "beat 1 ran out")
	ring.advance(ring.time_to_peak() + 0.1)
	assert_eq(ring.press(), SwellTimingRing.GRADE_GOOD, "0.1 s late")
	ring.advance(ring.time_to_peak() + 0.4)
	assert_eq(ring.press(), SwellTimingRing.GRADE_MISS, "0.4 s late still uses the beat")
	assert_true(ring.is_done())
	assert_eq(ring.press(), &"", "done")


func test_waiting_it_out_misses_every_beat_in_the_ring_s_length() -> void:
	assert_eq(ring.duration_sec(), 3.5)
	ring.advance(-1.0)
	assert_eq(ring.elapsed, 0.0, "time never runs backwards")
	ring.advance(ring.duration_sec())
	assert_true(ring.is_done())
	assert_eq(ring.grades, [&"miss", &"miss", &"miss"] as Array[StringName])
	ring.advance(10.0)
	assert_eq(ring.elapsed, ring.duration_sec(), "a finished ring stands still")
	assert_eq(ring.current_beat(), 3)


func test_cancel_only_before_the_first_grade() -> void:
	ring.advance(ring.time_to_peak())
	ring.press()
	assert_false(ring.cancel(), "no retrying an input that started badly")
	assert_false(ring.cancelled)
	var fresh := SwellTimingRing.new(CFG)
	assert_true(fresh.cancel())
	assert_true(fresh.is_done())
	assert_true(bool(fresh.result()[BattleSwell.RESULT_CANCELLED]))
	assert_false(fresh.cancel(), "already out")


func test_defaults_and_the_live_ring_is_short() -> void:
	var bare := SwellTimingRing.new()
	assert_eq(bare.beats, 1)
	assert_eq(SwellTimingRing.new({"beats": 0}).beats, 1, "at least one beat")
	var live := SwellTimingRing.new(BattleSwell.new(BattleSwell.load_config()).inputs[&"timing_ring"])
	assert_true(live.duration_sec() <= 3.5, "SPEC §6.2: short (%.2f s)" % live.duration_sec())
	assert_true(live.perfect_sec < live.good_sec)
	assert_true(live.peak_at > 0.0 and live.peak_at < 1.0)


func test_the_timing_assist_turns_misses_into_its_grade_and_nothing_else() -> void:  # M2-UI-01
	var cfg := CFG.duplicate()
	cfg["assist_floor"] = "good"
	ring = SwellTimingRing.new(cfg)
	assert_eq(ring.assist_floor, SwellInput.QUALITY_GOOD)
	ring.advance(ring.beat_start(1) + 0.01)
	assert_eq(ring.grades, [&"good"] as Array[StringName], "a beat that runs out counts as good")
	ring.advance(ring.time_to_peak())
	assert_eq(ring.press(), SwellTimingRing.GRADE_PERFECT, "a press on the peak still earns perfect")
	ring.advance(ring.time_to_peak() + 0.4)
	assert_eq(ring.press(), SwellTimingRing.GRADE_GOOD, "a mistimed press counts as good too")
	assert_true(ring.is_done())


func test_no_assist_by_default() -> void:
	assert_eq(ring.assist_floor, &"")
	ring.advance(ring.duration_sec())
	assert_eq(ring.grades, [&"miss", &"miss", &"miss"] as Array[StringName])
