extends TestCase
## M1-UI-05: SwellRingClock steps the timing ring on clamped frame time, so one long frame cannot
## skip a beat, and grades a press at the moment it is handled. A fake wall clock keeps it exact.

var _now := 0


func _clock_usec() -> int:
	return _now


func _ring() -> SwellTimingRing:
	return SwellTimingRing.new(BattleSwell.load_config()["inputs"][0])


func _sec(s: float) -> int:
	return int(round(s * SwellRingClock.USEC_PER_SEC))


func _near(actual: float, expected: float, msg: String = "") -> void:
	assert_between(actual, expected - 1e-6, expected + 1e-6, msg)


func test_the_shipped_ring_clamps_a_frame_at_or_under_its_perfect_window() -> void:
	var ring := _ring()
	assert_true(ring.max_step_sec > 0.0, "swell.json sets max_step_sec")
	assert_true(ring.max_step_sec <= ring.perfect_sec, "a hitch never jumps a whole grade")
	assert_eq(ring.clamp_step(10.0), ring.max_step_sec)
	assert_eq(ring.clamp_step(0.01), 0.01)
	ring.max_step_sec = 0.0
	assert_eq(ring.clamp_step(10.0), 10.0, "0 = no limit")


func test_a_long_frame_pauses_the_ring_instead_of_skipping_a_beat() -> void:
	_now = 0
	var ring := _ring()
	var clock := SwellRingClock.new(ring, _clock_usec)
	ring.advance(ring.time_to_peak() - 0.01)  # just before the first peak
	var at := ring.elapsed
	clock.step(ring.beat_sec * 2.0, true)  # a 1.6 s hitch
	assert_eq(ring.grades.size(), 0, "no beat ran out during the hitch")
	_near(ring.elapsed, at + ring.max_step_sec)
	assert_eq(clock.press(false), SwellTimingRing.GRADE_PERFECT, "still a fair press after the hitch")


func test_simulated_time_is_exact() -> void:
	var ring := _ring()
	var clock := SwellRingClock.new(ring, _clock_usec)
	clock.step(ring.duration_sec(), false)
	assert_true(ring.is_done())
	assert_eq(ring.grades, [&"miss", &"miss", &"miss"] as Array[StringName])


func test_a_press_is_graded_at_the_moment_it_is_handled() -> void:
	_now = 0
	var ring := _ring()
	var clock := SwellRingClock.new(ring, _clock_usec)
	var peak := ring.peak_time(0)
	# The last frame ended 0.1 s before the peak (outside the good window if graded there) and
	# the press is handled at the peak: it catches up 0.1 s, clamped to max_step_sec.
	clock.step(peak - 0.1, false)
	_now += _sec(0.1)
	var grade := clock.press()
	_near(ring.elapsed, peak - 0.1 + ring.max_step_sec)
	assert_eq(grade, SwellTimingRing.grade_for(ring.max_step_sec - 0.1, ring.perfect_sec, ring.good_sec))
	assert_ne(grade, SwellTimingRing.GRADE_MISS, "graded nearer the real press than the last frame")


func test_the_next_frame_does_not_count_the_caught_up_time_twice() -> void:
	_now = 0
	var ring := _ring()
	var clock := SwellRingClock.new(ring, _clock_usec)
	clock.step(ring.peak_time(0), false)
	_now += _sec(0.02)
	clock.press()  # catches up 0.02 s, then grades beat 1
	var after_press := ring.elapsed
	_now += _sec(0.01)
	clock.step(0.03, true)  # this frame's delta covers the 0.02 s already caught up
	_near(ring.elapsed, after_press + 0.01)
	clock.step(0.03, true)
	_near(ring.elapsed, after_press + 0.04, "only once")


func test_a_frozen_press_does_not_catch_up() -> void:
	_now = 0
	var ring := _ring()
	var clock := SwellRingClock.new(ring, _clock_usec)
	clock.step(ring.peak_time(0), false)
	_now += _sec(1.0)
	assert_eq(clock.press(false), SwellTimingRing.GRADE_PERFECT)
	_near(ring.elapsed, ring.peak_time(0))


func test_the_default_clock_is_the_engine_clock() -> void:
	var clock := SwellRingClock.new(_ring())
	assert_true(clock.now_usec.is_valid())
	assert_true(int(clock.now_usec.call()) >= 0)
