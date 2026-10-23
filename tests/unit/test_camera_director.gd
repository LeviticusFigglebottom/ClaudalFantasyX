extends TestCase
## M1-ARC-01: FieldCameraDirector over the field test zone (game/levels/_tests/field). The
## player is moved by hand and the director stepped with a fixed dt, so every assertion is
## deterministic: shot sequence, blends vs hard cuts, priority, and the three tracking modes.

const ZONE := "res://game/levels/_tests/field/field_test.tscn"
const DT := 1.0 / 60.0
const STEP_M := 0.25
const SETTLE_SEC := 4.0
const LANE := &"lane_fixed"
const COURT := &"court_pan"
const CAUSEWAY := &"causeway_dolly"
const AIM_TOLERANCE := 0.999
const POS_TOLERANCE_M := 0.01

var zone: Node3D
var director: FieldCameraDirector
var player: FieldController
var events: Array[Dictionary] = []


func before_each() -> void:
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	director = zone.get_node("CameraDirector") as FieldCameraDirector
	player = zone.get_node("Player") as FieldController
	director.auto_update = false
	player.set_physics_process(false)
	director.shot_changed.connect(_on_shot)
	zone.call("place_at", &"Lane")


func _on_shot(shot: CameraShot, hard_cut: bool, blend_sec: float) -> void:
	events.append({"id": shot.id, "cut": hard_cut, "blend": blend_sec})


func test_walk_through_volumes_gives_the_authored_shot_sequence() -> void:
	assert_eq(director.active_shot_id(), LANE, "spawn snaps to the lane shot")
	_walk_to(Vector3(0, 0, -5))
	_walk_to(Vector3(0, 0, -30))
	_walk_to(Vector3(0, 0, -5))
	var ids: Array[StringName] = []
	var cuts: Array[bool] = []
	for e in events:
		ids.append(e["id"])
		cuts.append(e["cut"])
	assert_eq(ids, [COURT, CAUSEWAY, COURT] as Array[StringName])
	assert_eq(cuts, [false, true, false] as Array[bool], "court blends in, causeway cuts in")
	assert_eq(director.history, [LANE, COURT, CAUSEWAY, COURT] as Array[StringName], "spawn snapped to the lane")
	_free()


func test_blend_runs_its_duration_along_the_ease_then_settles() -> void:
	_walk_to(Vector3(0, 0, 1.5), false)
	assert_eq(director.active_shot_id(), COURT)
	assert_true(director.is_blending(), "entering the court starts a blend")
	assert_between(director.blend_duration(), 1.19, 1.21, "court shot blend_sec")
	var weights: Array[float] = [director.blend_weight()]
	var elapsed := 0.0
	while director.is_blending() and elapsed < SETTLE_SEC:
		director.update(DT)
		elapsed += DT
		weights.append(director.blend_weight())
	assert_false(director.is_blending(), "blend finishes")
	assert_between(elapsed, 1.15, 1.25, "blend lasted its duration")
	for i in range(1, weights.size()):
		assert_true(weights[i] >= weights[i - 1], "weight never goes backwards")
	assert_eq(director.blend_weight(), 1.0)
	_free()


func test_ease_curve_shapes_the_weight() -> void:
	var shot := CameraShot.new()
	shot.blend_ease = &"in_out_sine"
	assert_between(director.blend_curve_weight(shot, 0.5), 0.49, 0.51, "sine in-out is symmetric")
	assert_true(director.blend_curve_weight(shot, 0.2) < 0.2, "eases in")
	assert_true(director.blend_curve_weight(shot, 0.8) > 0.8, "eases out")
	shot.blend_ease = &"linear"
	assert_between(director.blend_curve_weight(shot, 0.3), 0.29, 0.31)
	var custom := Curve.new()
	custom.add_point(Vector2(0, 0))
	custom.add_point(Vector2(1, 1))
	shot.blend_curve = custom
	assert_between(director.blend_curve_weight(shot, 0.5), 0.45, 0.55, "a custom Curve wins")
	_free()


func test_hard_cut_has_no_blend() -> void:
	_walk_to(Vector3(0, 0, -11))
	assert_eq(director.active_shot_id(), CAUSEWAY, "priority 1 wins where it overlaps the court")
	assert_false(director.is_blending())
	assert_eq(director.blend_weight(), 1.0)
	assert_eq(events[-1]["blend"], 0.0)
	_free()


func test_equal_priority_goes_to_the_most_recent_volume() -> void:
	var causeway := zone.get_node("CameraVolumes/CausewayVolume") as CameraVolume
	causeway.shot_priority = 0
	_walk_to(Vector3(0, 0, -11))
	assert_eq(director.active_shot_id(), CAUSEWAY, "entered after the court, so it wins the tie")
	_free()


func test_leaving_every_volume_keeps_the_shot() -> void:
	_walk_to(Vector3(0, 0, -5))
	_move(Vector3(15, 0, -5))
	assert_eq(director.state_snapshot()["inside"], 0)
	assert_eq(director.active_shot_id(), COURT)
	_free()


func test_fixed_shot_holds_its_authored_frame() -> void:
	_settle()
	var shot := (zone.get_node("CameraVolumes/LaneVolume") as CameraVolume).shot
	var cam := director.camera
	assert_true(cam.global_position.distance_to(shot.position) < POS_TOLERANCE_M)
	var aim := (shot.look_at - shot.position).normalized()
	assert_true(-cam.global_basis.z.dot(aim) > AIM_TOLERANCE, "looks at look_at")
	assert_between(cam.fov, 37.7, 37.9)
	_move(Vector3(1.5, 0, 4))
	_settle()
	assert_true(cam.global_position.distance_to(shot.position) < POS_TOLERANCE_M, "player motion moves nothing")
	_free()


func test_pan_follow_turns_toward_the_player_within_its_limit() -> void:
	_walk_to(Vector3(-1, 0, -5.5))
	_settle()
	var shot := (zone.get_node("CameraVolumes/CourtVolume") as CameraVolume).shot
	var cam := director.camera
	assert_true(cam.global_position.distance_to(shot.position) < POS_TOLERANCE_M, "pan keeps its position")
	var authored := (shot.look_at - shot.position).normalized()
	var fwd := -cam.global_basis.z
	var to_player := (player.global_position + shot.target_offset - shot.position).normalized()
	assert_true(fwd.angle_to(to_player) < authored.angle_to(to_player), "aim swings toward the player")
	_move(Vector3(8, 0, 1))
	_settle()
	fwd = -cam.global_basis.z
	assert_true(rad_to_deg(fwd.angle_to(authored)) <= shot.max_pan_deg + 0.5, "never past max_pan_deg")
	_free()


func test_dolly_rides_the_rail_with_the_players_progress() -> void:
	_walk_to(Vector3(0, 0, -14))
	_settle()
	var cam := director.camera
	var z_near := cam.global_position.z
	var x_near := cam.global_position.x
	_walk_to(Vector3(0, 0, -32))
	_settle()
	assert_true(cam.global_position.z < z_near - 10.0, "camera travelled with the player")
	assert_between(x_near, 6.0, 7.5, "on the dolly rail")
	assert_between(cam.global_position.x, 6.0, 7.5, "still on the rail")
	var to_player := (player.global_position + Vector3(0, 1, 0) - cam.global_position).normalized()
	assert_true(-cam.global_basis.z.dot(to_player) > AIM_TOLERANCE, "aims at the player")
	assert_true(cam.attributes is CameraAttributesPractical, "DOF attributes created")
	assert_true((cam.attributes as CameraAttributesPractical).dof_blur_far_enabled)
	_free()


func test_orbit_needs_the_hub_flag() -> void:
	var shot := CameraShot.new()
	shot.mode = CameraShot.Mode.ORBIT
	shot.position = Vector3(0, 2, 5)
	shot.look_at = Vector3.ZERO
	var refused := director.evaluate(shot, DT)
	assert_true(refused.origin.distance_to(shot.position) < POS_TOLERANCE_M, "non-hub zone: treated as pan-follow")
	director.hub_orbit_enabled = true
	var orbit := director.evaluate(shot, DT)
	var dist := float((director.data["orbit"] as Dictionary)["distance_m"])
	var flat := Vector2(orbit.origin.x - player.global_position.x, orbit.origin.z - player.global_position.z)
	assert_between(flat.length(), dist - 0.01, dist + 0.01, "hub zone: orbits the player")
	_free()


func test_interrupted_blend_continues_from_where_the_camera_is() -> void:
	# Shots are shared sub-resources of the cached PackedScene: restore before returning.
	var lane_shot := (zone.get_node("CameraVolumes/LaneVolume") as CameraVolume).shot
	lane_shot.hard_cut = false
	_walk_to(Vector3(0, 0, 1.5), false)
	assert_true(director.is_blending())
	for i in 20:
		director.update(DT)
	var mid := director.current_pose.copy()
	_move(Vector3(0, 0, 2.5))
	assert_eq(director.active_shot_id(), LANE, "back into the lane mid-blend")
	assert_true(director.is_blending(), "a new blend, not a cut")
	assert_true(director.current_pose.origin.distance_to(mid.origin) < 0.2, "starts from the interrupted pose: no pop")
	assert_true(director.current_pose.forward().dot(mid.forward()) > AIM_TOLERANCE)
	_settle()
	assert_eq(director.blend_weight(), 1.0)
	lane_shot.hard_cut = true
	_free()


# --- helpers -------------------------------------------------------------------------------------


func _walk_to(goal: Vector3, finish_blends: bool = true) -> void:
	var p := player.global_position
	while p.distance_to(goal) > STEP_M:
		p = p.move_toward(goal, STEP_M)
		_move(p)
	_move(goal)
	if finish_blends:
		_settle()


func _move(p: Vector3) -> void:
	player.global_position = p
	director.update(DT)


func _settle() -> void:
	var t := 0.0
	while t < SETTLE_SEC:
		director.update(DT)
		t += DT


func _free() -> void:
	zone.free()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
