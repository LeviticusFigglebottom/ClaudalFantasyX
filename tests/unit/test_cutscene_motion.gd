extends TestCase
## M2-FP-29 (the human's playtest: cutscene turns snapped, walks started and stopped at full speed):
## CutsceneMotion's eased turns and ramped walks.

const SPEED := 1.3
const ACCEL := 0.4
const DECEL := 0.5


func test_a_turn_eases_in_and_out() -> void:
	assert_eq(CutsceneMotion.eased(0.0, -2.0), 0.0)
	assert_eq(CutsceneMotion.eased(1.0, -2.0), 1.0)
	assert_true(CutsceneMotion.eased(0.1, -2.0) < 0.1, "slow out of the start")
	assert_true(CutsceneMotion.eased(0.9, -2.0) > 0.9, "slow into the end")
	assert_true(is_equal_approx(CutsceneMotion.eased(0.5, -2.0), 0.5), "symmetric")


func test_a_bigger_turn_takes_longer() -> void:
	assert_eq(CutsceneMotion.turn_duration(0.0, 0.25, 0.45), 0.25)
	assert_eq(CutsceneMotion.turn_duration(PI, 0.25, 0.45), 0.45)
	assert_eq(CutsceneMotion.turn_duration(-PI, 0.25, 0.45), 0.45, "either way round")
	assert_true(is_equal_approx(CutsceneMotion.turn_duration(PI / 2.0, 0.25, 0.45), 0.35))


func test_a_long_walk_ramps_up_cruises_and_ramps_down() -> void:
	var dist := 6.0
	var dur := CutsceneMotion.walk_duration(dist, SPEED, ACCEL, DECEL)
	assert_true(is_equal_approx(dur, dist / SPEED + (ACCEL + DECEL) * 0.5), "the ramps cost half their time")
	assert_eq(CutsceneMotion.walk_fraction(0.0, dist, SPEED, ACCEL, DECEL), 0.0)
	assert_true(is_equal_approx(CutsceneMotion.walk_fraction(dur, dist, SPEED, ACCEL, DECEL), 1.0), "arrives")
	var early := CutsceneMotion.walk_fraction(0.1, dist, SPEED, ACCEL, DECEL) * dist
	assert_true(early < SPEED * 0.1 * 0.5, "slower than full speed as it sets off")
	var mid_a := CutsceneMotion.walk_fraction(2.0, dist, SPEED, ACCEL, DECEL) * dist
	var mid_b := CutsceneMotion.walk_fraction(2.1, dist, SPEED, ACCEL, DECEL) * dist
	assert_true(is_equal_approx(mid_b - mid_a, SPEED * 0.1), "full speed in the middle")
	var late := dist - CutsceneMotion.walk_fraction(dur - 0.1, dist, SPEED, ACCEL, DECEL) * dist
	assert_true(late < SPEED * 0.1 * 0.5, "slower than full speed as it settles")


func test_a_short_walk_shortens_its_ramps_and_still_lands() -> void:
	var dist := 0.2
	var r := CutsceneMotion.ramps(dist, SPEED, ACCEL, DECEL)
	assert_true(r.x < ACCEL and r.y < DECEL, "shortened")
	assert_true(is_equal_approx(r.x / r.y, ACCEL / DECEL), "together")
	var dur := CutsceneMotion.walk_duration(dist, SPEED, ACCEL, DECEL)
	assert_true(is_equal_approx(dur, r.x + r.y), "all ramp, no cruise")
	var prev := 0.0
	for i in 21:
		var f := CutsceneMotion.walk_fraction(dur * i / 20.0, dist, SPEED, ACCEL, DECEL)
		assert_true(f >= prev, "never steps back")
		prev = f
	assert_true(is_equal_approx(prev, 1.0), "lands on the mark")


func test_no_distance_is_no_walk() -> void:
	assert_eq(CutsceneMotion.walk_duration(0.0, SPEED, ACCEL, DECEL), 0.0)
	assert_eq(CutsceneMotion.walk_fraction(0.3, 0.0, SPEED, ACCEL, DECEL), 1.0)
