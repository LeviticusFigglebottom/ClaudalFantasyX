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


## The human's playtest: the hero took the stick ~0.3 s before the fade cleared. While SceneRouter's fade covers any
## of the screen, the device stick reads nothing; once it is clear, it moves him.
func test_the_stick_waits_for_the_fade_to_clear() -> void:
	player.input_override = Vector2(NAN, NAN)
	var fade := SceneRouter.get(&"_fade_rect") as ColorRect
	var was := fade.color
	Input.action_press(FieldInput.MOVE_FORWARD)
	fade.color = Color(0, 0, 0, 0.2)
	assert_false(player.screen_clear(), "a fade still on the screen")
	assert_eq(player.current_stick(), Vector2.ZERO, "no stick under the fade")
	fade.color = Color(0, 0, 0, 0)
	assert_true(player.screen_clear())
	assert_true(player.current_stick().length() > 0.5, "the stick once the screen is clear")
	Input.action_release(FieldInput.MOVE_FORWARD)
	fade.color = was
	zone.free()


func test_teleport_snap_relatches_input_to_the_visible_camera() -> void:
	# M1-ARC-05: a snap is a cut to a camera the player has not seen yet; keeping the old latch would
	# map the stick to the lane camera while the causeway's side-on dolly is on screen.
	zone.call("place_at", &"Lane")
	var lane_yaw := director.camera_yaw()
	player.input_override = Vector2(0, -1)
	_step()
	zone.call("place_at", &"Causeway")
	assert_eq(director.active_shot_id(), CAUSEWAY)
	assert_false(player.motor.latched, "no latch to the camera that left the screen")
	assert_true(absf(angle_difference(director.camera_yaw(), lane_yaw)) > 0.5, "the cameras really differ")
	_step()
	assert_between(player.motor.reference_yaw, director.camera_yaw() - 0.001, director.camera_yaw() + 0.001)
	assert_false(player.motor.latched)
	zone.free()


func test_a_walk_in_cut_still_latches() -> void:
	zone.call("place_at", &"Court")
	player.input_override = Vector2(0, -1)
	_step()
	director.play_shot(director.active_shot.duplicate() as CameraShot, 0.0)
	assert_true(player.motor.latched, "a cut while the stick is held still latches (only snaps re-read)")
	zone.free()


func _step() -> void:
	player.step(DT)
	director.update(DT)


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
