extends TestCase
## M2-HER-1101: HeroLocomotion, the pure maths behind the real heroes' motion: the turn-rate cap (no
## snapping, frame to frame), the eased turn and the gait blend weights by ground speed.

const DT := 1.0 / 60.0
const EPS := 0.0001

var m: HeroLocomotion


func before_each() -> void:
	m = HeroLocomotion.new()


func test_tuning_comes_from_data() -> void:
	var d := HeroLocomotion.load_data()
	var t := d["turn"] as Dictionary
	assert_between(m.max_rate_rad, deg_to_rad(float(t["max_rate_deg_per_sec"])) - EPS, m.max_rate_rad + EPS)
	assert_true(m.max_rate_rad > 0.0 and m.max_accel_rad > 0.0 and m.settle_gain > 0.0, "turn tuning set")
	assert_true(m.run_clip_mps > m.walk_clip_mps and m.walk_clip_mps > 0.0, "run is faster than walk")


func test_a_reversal_never_turns_more_than_the_cap_in_one_frame() -> void:
	m.reset_yaw(0.0)
	var cap := m.max_rate_rad * DT
	var prev := m.yaw
	for i in 240:
		m.step_yaw(PI, DT)
		var d := absf(angle_difference(prev, m.yaw))
		assert_true(d <= cap + EPS, "frame %d turned %.4f > cap %.4f" % [i, d, cap])
		prev = m.yaw
	assert_between(absf(m.yaw), PI - 0.01, PI + 0.01, "it arrives facing the other way")


func test_the_turn_eases_in_and_out() -> void:
	m.reset_yaw(0.0)
	var steps: Array[float] = []
	var prev := 0.0
	for i in 120:
		m.step_yaw(PI / 2.0, DT)
		steps.append(absf(angle_difference(prev, m.yaw)))
		prev = m.yaw
	assert_true(steps[0] < m.max_rate_rad * DT * 0.5, "the first frame does not whip at full speed")
	var peak := 0.0
	for s in steps:
		peak = maxf(peak, s)
	assert_true(steps[0] < peak, "the turn speeds up")
	var last_moving := 0
	for i in steps.size():
		if steps[i] > 0.0:
			last_moving = i
	assert_true(steps[last_moving] < peak, "and slows before it lands")
	assert_between(m.yaw, PI / 2.0 - EPS, PI / 2.0 + EPS, "it lands on the heading")
	assert_eq(m.yaw_rate, 0.0, "with no turn speed left (no overshoot)")


func test_it_never_overshoots_a_small_turn() -> void:
	m.reset_yaw(0.0)
	for i in 60:
		m.step_yaw(0.05, DT)
		assert_true(m.yaw <= 0.05 + EPS, "frame %d overshot to %.4f" % [i, m.yaw])


func test_turns_take_the_short_way_across_pi() -> void:
	m.reset_yaw(PI - 0.1)
	m.step_yaw(-PI + 0.1, DT)
	m.step_yaw(-PI + 0.1, DT)
	assert_true(m.yaw > PI - 0.1 or m.yaw < -PI + 0.1, "it turns through pi, not back through 0")


func test_blend_weights_follow_ground_speed() -> void:
	_weights(0.0, 1.0, 0.0, 0.0)
	_weights(m.walk_clip_mps, 0.0, 1.0, 0.0)
	_weights(m.run_clip_mps, 0.0, 0.0, 1.0)
	_weights(m.walk_clip_mps * 0.5, 0.5, 0.5, 0.0)
	_weights((m.walk_clip_mps + m.run_clip_mps) * 0.5, 0.0, 0.5, 0.5)
	_weights(m.run_clip_mps * 3.0, 0.0, 0.0, 1.0)
	for i in 50:
		var w := m.weights(float(i) * 0.1)
		assert_between(w[0] + w[1] + w[2], 1.0 - EPS, 1.0 + EPS, "weights sum to 1 at %.1f m/s" % (i * 0.1))


func test_playback_scale_speeds_the_run_up_only_past_its_clip_speed() -> void:
	assert_eq(m.playback_scale(m.walk_clip_mps), 1.0)
	assert_eq(m.playback_scale(m.run_clip_mps), 1.0)
	assert_true(m.playback_scale(m.run_clip_mps * 1.1) > 1.0, "a faster run plays faster")
	assert_eq(m.playback_scale(m.run_clip_mps * 10.0), m.max_playback_scale, "capped")


func test_speed_is_filtered_so_a_stop_rolls_through_the_gait() -> void:
	m.reset_speed(m.run_clip_mps)
	m.step_speed(0.0, DT)
	assert_true(m.speed > 0.0 and m.speed < m.run_clip_mps, "one frame after a stop the gait is still moving")
	for i in 120:
		m.step_speed(0.0, DT)
	assert_true(m.speed < 0.01, "and settles to idle")


func test_teleports_and_move_threshold() -> void:
	assert_true(m.is_teleport(m.teleport_m + 0.1))
	assert_false(m.is_teleport(0.1))
	assert_false(m.is_moving(0.0))
	assert_true(m.is_moving(m.walk_clip_mps))


func _weights(speed: float, idle: float, walk: float, run: float) -> void:
	var w := m.weights(speed)
	var tag := "at %.2f m/s" % speed
	assert_between(w[0], idle - EPS, idle + EPS, "idle " + tag)
	assert_between(w[1], walk - EPS, walk + EPS, "walk " + tag)
	assert_between(w[2], run - EPS, run + EPS, "run " + tag)
