extends TestCase
## M1-ARC-01: FieldMotor, the pure camera-relative movement logic, including the input latch
## that keeps stick directions stable across camera cuts until the stick is released.

const DT := 1.0 / 60.0
const UP := Vector2(0, -1)
const RIGHT := Vector2(1, 0)
const EPS := 0.001
const STEPS_TO_TOP_SPEED := 120

var m: FieldMotor


func before_each() -> void:
	m = FieldMotor.new()


func test_tuning_comes_from_data() -> void:
	var d := FieldInput.load_json(FieldMotor.DATA_PATH)
	assert_eq(m.run_speed, float(d["run_speed_mps"]))
	assert_eq(m.walk_speed, float(d["walk_speed_mps"]))
	assert_true(m.run_speed > m.walk_speed and m.walk_speed > 0.0)
	assert_true(m.deadzone > 0.0 and m.deadzone < 1.0)


func test_stick_maps_relative_to_the_camera_yaw() -> void:
	_near(FieldMotor.world_direction(UP, 0.0), Vector3.FORWARD, "yaw 0: up is -Z")
	_near(FieldMotor.world_direction(RIGHT, 0.0), Vector3.RIGHT, "yaw 0: right is +X")
	_near(FieldMotor.world_direction(UP, PI / 2.0), Vector3.LEFT, "camera turned left: up is -X")
	_near(FieldMotor.world_direction(UP, PI), Vector3.BACK, "reversed camera: up is +Z")
	var cam := Basis(Vector3.UP, 0.7) * Basis(Vector3.RIGHT, -0.4)
	assert_between(FieldMotor.yaw_of_basis(cam), 0.7 - EPS, 0.7 + EPS, "pitch does not change yaw")


func test_latch_holds_the_old_reference_across_a_cut_until_release() -> void:
	m.step(UP, 0.0, DT)
	m.on_camera_change(true)
	assert_true(m.latched, "a cut while the stick is held latches")
	m.step(UP, PI, DT)
	assert_eq(m.reference_yaw, 0.0, "the new camera's yaw is ignored while latched")
	_near(FieldMotor.world_direction(UP, m.reference_yaw), Vector3.FORWARD, "still walking the same way")
	m.step(Vector2.ZERO, PI, DT)
	assert_false(m.latched, "releasing the stick drops the latch")
	m.step(UP, PI, DT)
	assert_eq(m.reference_yaw, PI, "the next press follows the new camera")


func test_cut_with_the_stick_released_does_not_latch() -> void:
	m.step(Vector2.ZERO, 0.0, DT)
	m.on_camera_change(true)
	assert_false(m.latched)


func test_turning_the_stick_far_releases_the_latch() -> void:
	m.step(UP, 0.0, DT)
	m.on_camera_change(true)
	m.step(UP.rotated(deg_to_rad(30.0)), PI, DT)
	assert_true(m.latched, "a small correction keeps the latch")
	m.step(RIGHT, PI, DT)
	assert_false(m.latched, "a 90 degree turn (> release_on_turn_deg) re-reads the camera")
	assert_eq(m.reference_yaw, PI)


func test_blend_latch_can_be_turned_off() -> void:
	m.latch_on_blend = false
	m.step(UP, 0.0, DT)
	m.on_camera_change(false)
	assert_false(m.latched)
	m.on_camera_change(true)
	assert_true(m.latched, "cuts still latch")


func test_acceleration_speed_and_facing() -> void:
	var v := m.step(UP, 0.0, DT)
	assert_true(v.length() <= m.acceleration * DT + EPS, "accelerates, no instant top speed")
	for i in STEPS_TO_TOP_SPEED:
		v = m.step(UP, 0.0, DT)
	assert_between(v.length(), m.run_speed - EPS, m.run_speed + EPS, "full stick runs")
	assert_between(m.facing_yaw, -EPS, EPS, "faces the way it walks")
	for i in STEPS_TO_TOP_SPEED:
		v = m.step(UP * (m.walk_run_threshold * 0.9), 0.0, DT)
	assert_between(v.length(), m.walk_speed - EPS, m.walk_speed + EPS, "a light stick walks")
	for i in STEPS_TO_TOP_SPEED:
		v = m.step(Vector2.ZERO, 0.0, DT)
	assert_eq(v, Vector3.ZERO, "stops when released")
	for i in STEPS_TO_TOP_SPEED:
		m.step(RIGHT, 0.0, DT)
	assert_between(m.facing_yaw, -PI / 2.0 - EPS, -PI / 2.0 + EPS, "turns to face +X")


func test_deadzone_is_no_input() -> void:
	var v := m.step(UP * (m.deadzone * 0.5), 0.0, DT)
	assert_eq(v, Vector3.ZERO)


func test_relatch_drops_the_latch_and_reads_the_given_camera() -> void:
	m.step(UP, 0.0, DT)
	m.on_camera_change(true)
	assert_true(m.latched)
	m.relatch(PI)
	assert_false(m.latched, "relatch drops the latch")
	assert_eq(m.reference_yaw, PI)
	m.step(UP, PI, DT)
	_near(FieldMotor.world_direction(UP, m.reference_yaw), Vector3.BACK, "up maps to the visible camera")


func _near(a: Vector3, b: Vector3, msg: String) -> void:
	assert_true(a.distance_to(b) < EPS, "%s: %s vs %s" % [msg, a, b])
