extends TestCase
## M1-ARC-01: FieldController in the field test zone. The player walks with a simulated stick
## (input_override) through the three camera volumes; the latch keeps the walking direction
## across the hard cut onto the causeway; runtime input actions exist.

const ZONE := "res://game/levels/_tests/field/field_test.tscn"
const DT := 1.0 / 60.0
const MAX_STEPS := 1200
const LANE := &"lane_fixed"
const COURT := &"court_pan"
const CAUSEWAY := &"causeway_dolly"

var zone: Node3D
var director: FieldCameraDirector
var player: FieldController


func before_each() -> void:
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	director = zone.get_node("CameraDirector") as FieldCameraDirector
	player = zone.get_node("Player") as FieldController
	director.auto_update = false
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)


func test_runtime_actions_exist() -> void:
	for a in [FieldInput.MOVE_LEFT, FieldInput.MOVE_RIGHT, FieldInput.MOVE_FORWARD, FieldInput.MOVE_BACK]:
		assert_true(InputMap.has_action(a), "%s added from field_input.json" % a)
		assert_false(InputMap.action_get_events(a).is_empty())
	assert_true(InputMap.has_action(FieldInput.INTERACT))
	assert_eq(FieldInput.ensure_actions().size(), 0, "idempotent")
	zone.free()


func test_walking_north_crosses_every_volume_and_latches_across_the_cut() -> void:
	zone.call("place_at", &"Lane")
	assert_eq(director.active_shot_id(), LANE)
	var seen: Array[StringName] = [LANE]
	var latched_on_causeway := false
	var drift_x := 0.0
	# The stick that walks due north under the lane camera. Without the latch, the same stick would
	# veer ~45 degrees once the court's pan camera took over.
	var yaw := director.camera_yaw()
	player.input_override = Vector2(sin(yaw), -cos(yaw))
	assert_true(FieldMotor.world_direction(player.input_override, yaw).distance_to(Vector3.FORWARD) < 0.001)
	for i in MAX_STEPS:
		_step()
		if director.active_shot_id() != seen[-1]:
			seen.append(director.active_shot_id())
			if director.active_shot_id() == CAUSEWAY:
				_step()
				latched_on_causeway = player.motor.latched
		drift_x = maxf(drift_x, absf(player.global_position.x))
		if player.global_position.z < -30.0:
			break
	assert_eq(seen, [LANE, COURT, CAUSEWAY] as Array[StringName], "lane -> court -> causeway")
	assert_true(player.global_position.z < -30.0, "reached the causeway end (z %.1f)" % player.global_position.z)
	assert_true(latched_on_causeway, "input latched across the side-on dolly cut")
	assert_true(drift_x < 1.5, "kept walking north through the cut (max |x| %.2f)" % drift_x)
	assert_true(player.grounded(), "standing on the greybox floor")
	player.input_override = Vector2.ZERO
	_step()
	assert_false(player.motor.latched, "releasing the stick drops the latch")
	zone.free()


func test_frozen_player_ignores_the_stick() -> void:
	zone.call("place_at", &"Court")
	player.accepts_input = false
	player.input_override = Vector2(NAN, NAN)
	var start := player.global_position
	for i in 30:
		_step()
	assert_true(Vector2(player.global_position.x - start.x, player.global_position.z - start.z).length() < 0.01)
	zone.free()


func _step() -> void:
	player.step(DT)
	director.update(DT)


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
