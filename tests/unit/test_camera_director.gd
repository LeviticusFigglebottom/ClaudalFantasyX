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
const SCRIPTED := &"cutscene_h06"
const SCRIPT_BLEND_SEC := 0.5
const AIM_OFFSET := Vector3(0, 1.2, 0)

var zone: Node3D
var director: FieldCameraDirector
var player: FieldController
var events: Array[Dictionary] = []
## Shot ids seen by test coroutines resuming from `await director.blend_finished`.
var resumed: Array[StringName] = []
## What those coroutines saw when they resumed (M1-ARC-07 review-sweep-E S1).
var seen_leaving: Array[bool] = []
var seen_in_tree: Array[bool] = []


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
	assert_true(-cam.global_basis.z.dot(aim) > AIM_TOLERANCE, "he is in frame, so the composition holds")
	_free()


## The PC's GPU QA row 37 (the causeway's C07 at BeforeHarrier): a FIXED shot that would lose the leader entirely turns
## to hold him at the edge (keep_in_frame_fixed_share); one with him in frame is never moved (the test above).
func test_a_fixed_shot_that_would_lose_him_turns_to_hold_him() -> void:
	var shot := (zone.get_node("CameraVolumes/LaneVolume") as CameraVolume).shot
	var from := shot.position
	var aim := shot.look_at
	var behind := from - (aim - from).normalized() * 4.0  # right behind the camera: no authored frame shows him
	var kept := FieldCameraDirector.keep_in_frame(
		from,
		aim,
		behind,
		shot.fov_deg if shot.fov_deg > 0.0 else 37.8,
		float(director.data.get("keep_in_frame_fixed_share", 1.0)),
		float(director.data.get("keep_in_frame_aspect", 1.0))
	)
	assert_true((kept - from).normalized().dot((behind - from).normalized()) > 0.99, "turned to look at him")
	var inside := aim + Vector3(0.3, 0.0, 0.0)
	var same := FieldCameraDirector.keep_in_frame(
		from, aim, inside, 37.8, float(director.data.get("keep_in_frame_fixed_share", 1.0)), 16.0 / 9.0
	)
	assert_true(same.is_equal_approx(aim), "with him in frame the locked aim is untouched")
	_free()


## A cutscene's shot is a composition (an insert on a prop, a reverse with the leader off-frame): the safety net above
## never turns it to him (big20 had O07's name-board insert turn to Rhen across the town).
func test_a_scripted_shot_is_never_turned_to_the_leader() -> void:
	_settle()
	var insert := CameraShot.new()
	insert.id = &"insert"
	insert.position = player.global_position + Vector3(0, 1.6, 6)
	insert.look_at = insert.position + Vector3(0, 0, 4)  # straight away from him
	director.play_shot(insert, 0.0)
	_settle()
	var aim := (insert.look_at - insert.position).normalized()
	assert_true(-director.camera.global_basis.z.dot(aim) > AIM_TOLERANCE, "the insert holds its authored frame")
	director.release(0.0)
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
	assert_true(
		(
			rad_to_deg(fwd.angle_to(authored)) <= shot.max_pan_deg + 0.5
			or cam.is_position_in_frustum(player.global_position + shot.target_offset)
		),
		"never past max_pan_deg, unless that would lose him (then just enough to hold him in frame)"
	)
	_free()


## The Lead's 10-29 walk audit (Coilspire's spiral): keep_in_frame leaves an aim alone while the subject is inside
## share x the frame's half angles (vertical from the fov, horizontal from the aspect), and otherwise turns it exactly
## to that edge, toward him.
func test_keep_in_frame_turns_the_aim_only_as_far_as_it_must() -> void:
	var from := Vector3.ZERO
	var aim := Vector3(0, 0, -10)
	var inside := Vector3(0, 1, -10)  # ~5.7 degrees off
	assert_eq(FieldCameraDirector.keep_in_frame(from, aim, inside, 40.0, 0.7, 16.0 / 9.0), aim, "inside: untouched")
	# on a third across a 16:9 frame (11 degrees right; the horizontal limit is ~16.6 there): an authored composition
	var third := Vector3(10.0 * tan(deg_to_rad(11.0)), 0, -10)
	assert_eq(FieldCameraDirector.keep_in_frame(from, aim, third, 37.8, 0.5, 16.0 / 9.0), aim, "a third stays")
	var above := Vector3(0, 10, -10)  # 45 degrees off; the vertical limit is 40 * 0.5 * 0.7 = 14 degrees
	var kept := FieldCameraDirector.keep_in_frame(from, aim, above, 40.0, 0.7, 16.0 / 9.0)
	var off := rad_to_deg((kept - from).angle_to(above - from))
	assert_between(off, 13.9, 14.1, "turned until he is at the edge of the kept share (%.2f)" % off)
	assert_true((kept - from).y > 0.0, "toward him")
	assert_between((kept - from).length(), 9.99, 10.01, "the aim keeps its distance")
	_free()  # before_each's zone


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


# --- M1-ARC-05: scripted shots, aim nodes, snap ---------------------------------------------------


func test_play_shot_suspends_volume_selection_until_release() -> void:
	var started: Array[Dictionary] = []
	var released: Array[Dictionary] = []
	director.scripted_shot_started.connect(func(s: CameraShot, b: float) -> void: started.append({"id": s.id, "b": b}))
	director.scripted_shot_released.connect(
		func(s: CameraShot, b: float) -> void: released.append({"id": s.id, "b": b})
	)
	var shot := _scripted_shot()
	director.play_shot(shot, SCRIPT_BLEND_SEC)
	assert_true(director.is_scripted())
	assert_eq(director.scripted_shot(), shot)
	assert_eq(director.active_shot_id(), SCRIPTED)
	assert_true(director.is_blending(), "blends in from the lane")
	assert_between(director.blend_duration(), SCRIPT_BLEND_SEC - 0.001, SCRIPT_BLEND_SEC + 0.001)
	assert_eq(started, [{"id": SCRIPTED, "b": SCRIPT_BLEND_SEC}] as Array[Dictionary])
	_walk_to(Vector3(0, 0, -5))
	assert_eq(director.active_shot_id(), SCRIPTED, "walking into the court does not take the camera back")
	assert_eq(director.history, [LANE, SCRIPTED] as Array[StringName])
	assert_eq(director.state_snapshot()["volume"], "", "no volume owns a scripted shot")
	assert_true(director.camera.global_position.distance_to(shot.position) < POS_TOLERANCE_M, "settled on it")
	var court := zone.get_node("CameraVolumes/CourtVolume") as CameraVolume
	var court_blend := _volume_blend(court)
	assert_true(director.release(), "released")
	assert_false(director.is_scripted())
	assert_eq(director.active_shot_id(), COURT, "back to the winning volume's shot")
	assert_eq(director.active_volume, court)
	assert_true(director.is_blending(), "with a blend")
	assert_between(director.blend_duration(), court_blend - 0.001, court_blend + 0.001, "the volume's blend")
	assert_eq(released, [{"id": COURT, "b": court_blend}] as Array[Dictionary])
	assert_false(director.release(), "nothing held: no-op")
	_walk_to(Vector3(0, 0, 5))
	assert_eq(director.active_shot_id(), LANE, "volume selection resumed")
	_free()


func test_release_always_blends_unless_told_to_cut() -> void:
	_walk_to(Vector3(0, 0, -20))
	assert_eq(director.active_shot_id(), CAUSEWAY)
	var causeway := zone.get_node("CameraVolumes/CausewayVolume") as CameraVolume
	assert_true(causeway.shot.hard_cut, "the causeway cuts in from the court")
	director.play_shot(_scripted_shot(), 0.0)
	assert_false(director.is_blending(), "explicit 0 cuts")
	assert_eq(events[-1], {"id": SCRIPTED, "cut": true, "blend": 0.0})
	director.release()
	assert_eq(director.active_shot_id(), CAUSEWAY)
	assert_true(director.is_blending(), "release blends even onto a hard-cut shot")
	var want := _volume_blend(causeway)
	assert_between(director.blend_duration(), want - 0.001, want + 0.001, "the volume's resolved blend")
	director.play_shot(_scripted_shot())
	director.release(0.0)
	assert_false(director.is_blending(), "release(0) cuts")
	_free()


func test_play_shot_defaults_and_chained_shots() -> void:
	var a := _scripted_shot()
	director.play_shot(a)
	assert_between(director.blend_duration(), _default_blend() - 0.001, _default_blend() + 0.001, "default blend")
	var b := _scripted_shot()
	b.id = &"cutscene_reaction"
	b.hard_cut = true
	director.play_shot(b)
	assert_false(director.is_blending(), "the shot's own hard_cut applies when no blend is given")
	assert_eq(director.scripted_shot(), b, "the next scripted shot")
	director.play_shot(a, SCRIPT_BLEND_SEC)
	assert_true(director.is_blending(), "an explicit blend")
	_move(Vector3(15, 0, -5))
	assert_eq(director.state_snapshot()["inside"], 0)
	director.release()
	assert_eq(director.active_shot_id(), LANE, "outside every volume: back to the shot before the script")
	_free()


func test_play_shot_ease_overrides_the_shot_curve() -> void:
	var shot := _scripted_shot()
	shot.blend_ease = &"in_out_cubic"
	director.play_shot(shot, 1.0, &"linear")
	for i in 15:
		director.update(DT)
	assert_between(director.blend_weight(), 0.24, 0.26, "linear at a quarter of the blend")
	director.play_shot(_scripted_shot(), 1.0)
	for i in 15:
		director.update(DT)
	assert_true(director.blend_weight() < 0.2, "the default sine ease again on the next blend")
	_free()


func test_snap_mid_blend_into_the_active_shot_ends_the_blend() -> void:
	var finished: Array[StringName] = []
	director.blend_finished.connect(func(s: CameraShot) -> void: finished.append(s.id))
	var snaps: Array[StringName] = []
	director.snapped.connect(func(s: CameraShot) -> void: snaps.append(s.id))
	_walk_to(Vector3(0, 0, 1.5), false)
	for i in 3:
		director.update(DT)
	assert_eq(director.active_shot_id(), COURT)
	assert_true(director.is_blending() and director.blend_weight() < 0.1, "early in the court blend")
	zone.call("place_at", &"Court")
	assert_eq(director.active_shot_id(), COURT, "same shot")
	assert_false(director.is_blending(), "snap ended the blend")
	assert_eq(director.blend_weight(), 1.0)
	assert_eq(director.blend_duration(), 0.0)
	assert_eq(finished, [COURT] as Array[StringName], "blend_finished fires for the cut-short blend")
	assert_eq(snaps, [COURT] as Array[StringName])
	var settled := director.evaluate((zone.get_node("CameraVolumes/CourtVolume") as CameraVolume).shot, 0.0)
	assert_true(director.camera.global_position.distance_to(settled.origin) < POS_TOLERANCE_M, "on the court frame")
	assert_true(-director.camera.global_basis.z.dot(settled.forward()) > AIM_TOLERANCE, "aim snapped too")
	_free()


func test_snap_while_scripted_stays_on_the_scripted_shot() -> void:
	director.play_shot(_scripted_shot(), SCRIPT_BLEND_SEC)
	zone.call("place_at", &"Causeway")
	assert_eq(director.active_shot_id(), SCRIPTED)
	assert_false(director.is_blending())
	assert_true(director.is_scripted())
	director.release(0.0)
	assert_eq(director.active_shot_id(), CAUSEWAY, "release finds the volume the player was snapped into")
	_free()


func test_fixed_shot_aims_at_its_aim_node() -> void:
	var mark := zone.get_node("Spawns/Court") as Node3D
	var shot := _scripted_shot()
	shot.aim_node = NodePath("Spawns/Court")
	shot.aim_offset = AIM_OFFSET
	director.play_shot(shot, 0.0)
	director.update(DT)
	var want := (mark.global_position + AIM_OFFSET - shot.position).normalized()
	assert_true(-director.camera.global_basis.z.dot(want) > AIM_TOLERANCE, "looks at the mark, not look_at")
	_move(Vector3(1.5, 0, 4))
	assert_true(-director.camera.global_basis.z.dot(want) > AIM_TOLERANCE, "the player moving changes nothing")
	assert_eq(director.state_snapshot()["aim"], "Spawns/Court")
	_free()


func test_pan_follow_turns_toward_the_aim_node_not_the_player() -> void:
	var actor := _actor(Vector3(-3, 0, -6))
	var shot := (zone.get_node("CameraVolumes/CourtVolume") as CameraVolume).shot.duplicate() as CameraShot
	shot.aim_node = NodePath(actor.name)
	shot.aim_offset = AIM_OFFSET
	shot.follow_smoothing = 0.0
	var authored := (shot.look_at - shot.position).normalized()
	var to_actor := (actor.global_position + AIM_OFFSET - shot.position).normalized()
	var fwd := director.evaluate(shot, DT).forward()
	assert_true(fwd.angle_to(to_actor) < authored.angle_to(to_actor), "pans toward the actor")
	_move(Vector3(4, 0, -2))
	assert_true(director.evaluate(shot, DT).forward().dot(fwd) > AIM_TOLERANCE, "ignores the player")
	_free()


func test_dolly_tracks_and_aims_at_the_aim_node() -> void:
	var actor := _actor(Vector3(0, 0, -14))
	var shot := (zone.get_node("CameraVolumes/CausewayVolume") as CameraVolume).shot.duplicate() as CameraShot
	shot.aim_node = NodePath(actor.name)
	shot.aim_offset = AIM_OFFSET
	shot.follow_smoothing = 0.0
	var near := director.evaluate(shot, DT)
	actor.global_position = Vector3(0, 0, -32)
	var far := director.evaluate(shot, DT)
	assert_true(far.origin.z < near.origin.z - 10.0, "the dolly follows the actor while the player stays put")
	var to_actor := (actor.global_position + AIM_OFFSET - far.origin).normalized()
	assert_true(far.forward().dot(to_actor) > AIM_TOLERANCE, "aims at the actor")
	_free()


func test_orbit_circles_the_aim_node() -> void:
	var actor := _actor(Vector3(5, 0, -8))
	var shot := CameraShot.new()
	shot.mode = CameraShot.Mode.ORBIT
	shot.aim_node = NodePath(actor.name)
	director.hub_orbit_enabled = true
	var pose := director.evaluate(shot, DT)
	var dist := float((director.data["orbit"] as Dictionary)["distance_m"])
	var flat := Vector2(pose.origin.x - actor.global_position.x, pose.origin.z - actor.global_position.z)
	assert_between(flat.length(), dist - 0.01, dist + 0.01, "orbits the actor")
	_free()


func test_missing_aim_node_falls_back_to_the_player() -> void:
	var shot := CameraShot.new()
	shot.aim_node = NodePath("NoSuchActor")
	assert_eq(director.subject_node(shot), player)
	assert_true(director.aim_point(shot).distance_to(player.global_position + shot.target_offset) < POS_TOLERANCE_M)
	_free()


func test_missing_aim_node_is_loud_once_per_shot() -> void:
	var log := AimErrorLog.new()
	OS.add_logger(log)
	var shot := _scripted_shot()
	shot.aim_node = NodePath("NoSuchActor")
	director.play_shot(shot, 0.0)
	_settle()
	director.subject_node(shot)
	var errors := log.take()
	OS.remove_logger(log)
	assert_eq(errors, 1, "push_error, not a warning, and only once for the shot however often it evaluates")
	assert_eq(director.missing_aim_nodes(), [SCRIPTED] as Array[StringName], "recorded for the overlay and tests")
	var good := _scripted_shot()
	good.id = &"cutscene_reaction"
	good.aim_node = NodePath(_actor(Vector3(0, 0, 9)).name)
	director.play_shot(good, 0.0)
	_settle()
	assert_eq(director.missing_aim_nodes(), [SCRIPTED] as Array[StringName], "a found aim_node is not reported")
	_free()


# --- M1-ARC-07: the sequencer contract ------------------------------------------------------------


func test_release_honours_the_volumes_force_hard_cut() -> void:
	var released: Array[float] = []
	director.scripted_shot_released.connect(func(_s: CameraShot, b: float) -> void: released.append(b))
	var court := zone.get_node("CameraVolumes/CourtVolume") as CameraVolume
	court.force_hard_cut = true
	_walk_to(Vector3(0, 0, -5))
	assert_eq(director.active_shot_id(), COURT)
	director.play_shot(_scripted_shot(), SCRIPT_BLEND_SEC)
	_settle()
	director.release()
	assert_eq(director.active_shot_id(), COURT)
	assert_false(director.is_blending(), "force_hard_cut: the default release cuts")
	assert_eq(events[-1], {"id": COURT, "cut": true, "blend": 0.0})
	director.play_shot(_scripted_shot(), SCRIPT_BLEND_SEC)
	_settle()
	director.release(SCRIPT_BLEND_SEC, &"linear")
	assert_false(director.is_blending(), "force_hard_cut wins over an explicit blend too")
	assert_eq(released, [0.0, 0.0] as Array[float], "released reports the cut")
	_free()


func test_a_cut_emits_blend_finished_on_the_next_update() -> void:
	var finished: Array[StringName] = []
	director.blend_finished.connect(func(s: CameraShot) -> void: finished.append(s.id))
	director.play_shot(_scripted_shot(), 0.0)
	assert_eq(finished, [] as Array[StringName], "not synchronously: `play_shot` then `await` cannot miss it")
	assert_false(director.is_settled(), "a blend_finished is owed")
	director.update(DT)
	assert_eq(finished, [SCRIPTED] as Array[StringName], "the cut landed")
	assert_true(director.is_settled())
	_settle()
	assert_eq(finished.size(), 1, "exactly once")
	director.release(0.0)
	director.update(DT)
	assert_eq(finished, [SCRIPTED, LANE] as Array[StringName], "a release cut lands too")
	_free()


func test_a_volume_cut_emits_blend_finished() -> void:
	var finished: Array[StringName] = []
	director.blend_finished.connect(func(s: CameraShot) -> void: finished.append(s.id))
	_walk_to(Vector3(0, 0, -5))
	_walk_to(Vector3(0, 0, -20))
	assert_eq(finished, [COURT, CAUSEWAY] as Array[StringName], "the court blend, then the causeway cut")
	_free()


func test_a_no_move_play_shot_still_settles() -> void:
	var finished: Array[StringName] = []
	director.blend_finished.connect(func(s: CameraShot) -> void: finished.append(s.id))
	var shot := _scripted_shot()
	director.play_shot(shot, SCRIPT_BLEND_SEC)
	_settle()
	assert_eq(finished, [SCRIPTED] as Array[StringName], "the blend in")
	director.play_shot(shot, SCRIPT_BLEND_SEC)
	assert_false(director.is_settled())
	director.update(DT)
	assert_eq(finished, [SCRIPTED, SCRIPTED] as Array[StringName], "re-playing the held shot settles at once")
	assert_eq(director.history, [LANE, SCRIPTED] as Array[StringName], "and is not a new shot")
	_free()


func test_a_cut_onto_the_shot_blending_in_ends_the_blend_once() -> void:
	var finished: Array[StringName] = []
	director.blend_finished.connect(func(s: CameraShot) -> void: finished.append(s.id))
	var shot := _scripted_shot()
	director.play_shot(shot, SCRIPT_BLEND_SEC)
	director.update(DT)
	assert_true(director.is_blending())
	director.play_shot(shot, 0.0)
	assert_false(director.is_blending(), "the cut ends the blend")
	director.update(DT)
	assert_true(director.camera.global_position.distance_to(shot.position) < POS_TOLERANCE_M, "on the shot")
	_settle()
	assert_eq(finished, [SCRIPTED] as Array[StringName], "one landing, not two")
	_free()


func test_a_superseded_cut_does_not_fire() -> void:
	var finished: Array[StringName] = []
	director.blend_finished.connect(func(s: CameraShot) -> void: finished.append(s.id))
	var b := _scripted_shot()
	b.id = &"cutscene_reaction"
	director.play_shot(_scripted_shot(), 0.0)
	director.play_shot(b, SCRIPT_BLEND_SEC)
	director.update(DT)
	assert_eq(finished, [] as Array[StringName], "the cut was replaced before it landed")
	_settle()
	assert_eq(finished, [&"cutscene_reaction"] as Array[StringName], "the blend that replaced it lands")
	_free()


func test_a_cut_issued_from_a_blend_finished_await_lands_on_a_later_update() -> void:
	var finished: Array[StringName] = []
	director.blend_finished.connect(func(s: CameraShot) -> void: finished.append(s.id))
	var a := _scripted_shot()
	var b := _scripted_shot()
	b.id = &"cutscene_reaction"
	b.position = Vector3(-4, 1.0, 6)
	for first_blend: float in [SCRIPT_BLEND_SEC, 0.0]:
		finished.clear()
		resumed.clear()
		director.play_shot(a, first_blend)
		_sequencer_then_cut(b)
		var elapsed := 0.0
		while resumed.is_empty() and elapsed < SETTLE_SEC:
			director.update(DT)
			elapsed += DT
		var how := "after a %s" % ("blend" if first_blend > 0.0 else "cut")
		assert_eq(resumed, [SCRIPTED] as Array[StringName], "the sequencer resumed inside the emit " + how)
		assert_eq(finished, [SCRIPTED] as Array[StringName], "its cut does not land in the same update " + how)
		assert_false(director.is_settled(), "the cut is owed " + how)
		assert_true(director.camera.global_position.distance_to(a.position) < POS_TOLERANCE_M, "a's pose " + how)
		director.update(DT)
		assert_eq(finished, [SCRIPTED, &"cutscene_reaction"] as Array[StringName], "lands next update " + how)
		assert_true(director.camera.global_position.distance_to(b.position) < POS_TOLERANCE_M, "b's pose " + how)
	_free()


func test_leaving_the_tree_pays_an_owed_blend_finished() -> void:
	resumed.clear()
	director.play_shot(_scripted_shot(), SCRIPT_BLEND_SEC)
	director.update(DT)
	assert_true(director.is_blending())
	_await_landing()
	assert_false(director.is_leaving(), "in the tree and not leaving")
	_host().remove_child(zone)
	assert_eq(resumed, [SCRIPTED] as Array[StringName], "the awaiting coroutine resumed instead of hanging")
	assert_eq(seen_leaving, [true] as Array[bool], "inside the _exit_tree emit, is_leaving() is already true")
	assert_eq(
		seen_in_tree, [true] as Array[bool], "while Godot still reports is_inside_tree() (why it is not the guard)"
	)
	assert_true(director.is_settled())
	assert_true(director.is_leaving(), "out of the tree")
	_host().add_child(zone)
	assert_false(director.is_leaving(), "re-entering clears it")
	_free()


func test_the_autosave_hold_follows_the_scripted_shot_across_a_reparent() -> void:
	var saves := _host().get_node(^"/root/SaveSystem")
	var held := func() -> bool: return director in (saves.call(&"autosave_holders") as Array[Object])
	director.play_shot(_scripted_shot(), 0.0)
	assert_true(held.call(), "play_shot holds the autosave")
	director.update(DT)
	assert_true(director.is_settled(), "the cut has landed: nothing is owed (review-sweep-F F1 is the owed case)")
	_host().remove_child(zone)
	assert_false(held.call(), "an unloading zone never blocks the save")
	assert_true(director.is_scripted(), "the shot is still held")
	_host().add_child(zone)
	assert_true(held.call(), "re-entering with the shot held takes the hold back")
	director.release(0.0)
	assert_false(held.call(), "release drops it")
	_host().remove_child(zone)
	_host().add_child(zone)
	assert_false(held.call(), "no shot held, no hold on re-entry")
	_host().remove_child(zone)
	director.play_shot(_scripted_shot(), 0.0)
	assert_false(held.call(), "out of the tree, play_shot does not hold yet")
	_host().add_child(zone)
	assert_true(held.call(), "it holds once the director is back in a tree")
	director.release(0.0)
	_free()


## M1-ARC-07 review-sweep-F F1: a reparent with an owed blend wakes the sequencer, which stops on
## is_leaving() (the documented pattern) and never calls release(). The director must not take the
## hold back on re-entry, or every chapter autosave would wait until the zone is freed.
func test_a_reparent_mid_move_drops_the_scripted_shot_and_its_hold() -> void:
	var saves := _host().get_node(^"/root/SaveSystem")
	var holders := func() -> Array[Object]: return saves.call(&"autosave_holders") as Array[Object]
	resumed.clear()
	seen_leaving.clear()
	var shot := _scripted_shot()
	director.play_shot(shot, SCRIPT_BLEND_SEC)
	director.update(DT)
	assert_true(director.is_blending(), "a move is in progress")
	_sequencer_stopping_on_leave()
	_host().remove_child(zone)
	assert_eq(resumed, [SCRIPTED] as Array[StringName], "the sequencer woke inside _exit_tree")
	assert_eq(seen_leaving, [true] as Array[bool], "and stopped on is_leaving()")
	assert_false(director.is_scripted(), "paying the owed emit dropped the scripted shot")
	_host().add_child(zone)
	assert_false(director in holders.call(), "re-entry does not take the hold back")
	assert_true(holders.call().is_empty(), "nothing holds the autosave")
	assert_false(director.release(0.0), "nothing is left to release")
	assert_eq(director.active_shot, shot, "the camera stays where it was until volumes pick again")
	director.update(DT)
	assert_eq(director.active_shot_id(), LANE, "volume selection resumes on the next update")
	_free()


func test_no_player_still_applies_shots_and_lands() -> void:
	var finished: Array[StringName] = []
	director.blend_finished.connect(func(s: CameraShot) -> void: finished.append(s.id))
	director.target = null
	var shot := _scripted_shot()
	director.play_shot(shot, SCRIPT_BLEND_SEC)
	_settle()
	assert_eq(finished, [SCRIPTED] as Array[StringName], "the blend lands without a player")
	assert_true(director.camera.global_position.distance_to(shot.position) < POS_TOLERANCE_M, "pose applied")
	var court := (zone.get_node("CameraVolumes/CourtVolume") as CameraVolume).shot.duplicate() as CameraShot
	court.follow_smoothing = 0.0
	var pan := director.evaluate(court, DT)
	assert_true(pan.forward().dot((court.look_at - court.position).normalized()) > AIM_TOLERANCE, "pans at look_at")
	var dolly := (zone.get_node("CameraVolumes/CausewayVolume") as CameraVolume).shot
	assert_eq(director.dolly_progress(dolly), clampf(dolly.progress_offset, 0.0, 1.0), "dolly holds its offset")
	director.release(0.0)
	director.update(DT)
	assert_eq(director.active_shot_id(), LANE, "release hands back to the lane")
	assert_eq(finished, [SCRIPTED, LANE] as Array[StringName])
	_free()


# --- helpers -------------------------------------------------------------------------------------


## A sequencer step: await the landing, then cut to `next` from inside the emit.
func _sequencer_then_cut(next: CameraShot) -> void:
	await director.blend_finished
	resumed.append(director.active_shot_id())
	director.play_shot(next, 0.0)


## The documented sequencer pattern (field_camera.md): stop when the director is leaving.
func _sequencer_stopping_on_leave() -> void:
	await director.blend_finished
	resumed.append(director.active_shot_id())
	seen_leaving.append(director.is_leaving())
	if not is_instance_valid(director) or director.is_leaving():
		return
	director.release(0.0)


func _await_landing() -> void:
	await director.blend_finished
	resumed.append(director.active_shot_id())
	seen_leaving.append(director.is_leaving())
	seen_in_tree.append(director.is_inside_tree())


## Counts FieldCameraDirector's missing-aim_node errors reported through the engine log.
class AimErrorLog:
	extends Logger
	var count := 0
	var _mutex := Mutex.new()

	func _log_error(
		_function: String,
		_file: String,
		_line: int,
		code: String,
		rationale: String,
		_editor_notify: bool,
		error_type: int,
		_script_backtraces: Array[ScriptBacktrace]
	) -> void:
		if error_type == Logger.ERROR_TYPE_ERROR and ("%s %s" % [code, rationale]).contains("aim_node"):
			_mutex.lock()
			count += 1
			_mutex.unlock()

	func take() -> int:
		_mutex.lock()
		var n := count
		count = 0
		_mutex.unlock()
		return n


func _scripted_shot() -> CameraShot:
	var s := CameraShot.new()
	s.id = SCRIPTED
	s.mode = CameraShot.Mode.FIXED
	s.position = Vector3(4, 1.0, 6)
	s.look_at = Vector3(0, 1.0, 9)
	return s


func _actor(at: Vector3) -> Node3D:
	var a := Marker3D.new()
	a.name = "TestActor"
	zone.add_child(a)
	a.global_position = at
	return a


func _default_blend() -> float:
	return float(director.data["default_blend_sec"])


func _volume_blend(v: CameraVolume) -> float:
	if v.blend_sec_override >= 0.0:
		return v.blend_sec_override
	return v.shot.blend_sec if v.shot.blend_sec >= 0.0 else _default_blend()


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
