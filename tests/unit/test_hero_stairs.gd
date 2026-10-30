extends TestCase
## M3-ARC-1216: steep stairs (HeroStairFlight, HeroStairs). Rhen climbs a 48° flight and comes down a 60° one along
## their profiles: step by step, never faster than the slope speed, never a snap (HeroMotionGuard), let go onto the
## landing at the far end. Standing still on a flight he doesn't slide; pushing sideways keeps him inside it; walking
## under a flying stair doesn't put him on it; Asha and Toma follow him up the steps. Each test builds its own floors
## and flight beside the field test zone (x = SITE_X), where nothing else stands.

const ZONE := "res://game/levels/_tests/field/field_test.tscn"
const SITE_X := 60.0
const DT := 1.0 / 60.0
## The stick that walks the player toward -Z (the flights climb along -Z), and back.
const UP := Vector2(0, -1)
const DOWN := Vector2(0, 1)
const RIGHT := Vector2(1, 0)
const MAX_FRAMES := 900
const TOL_M := 0.05
## A 48° flight (Ashcrown's flying stair) and a 60° one (its vein stairs): run, rise.
const RUN_48 := 2.4
const RISE_48 := 2.665
const RUN_60 := 1.6
const RISE_60 := 2.771

var zone: Node3D
var player: FieldController
var stairs: HeroStairs
var party: HeroFieldParty
var _party_was: Array[StringName] = []


func before_each() -> void:
	_party_was = Game.state.party_ids.duplicate()
	Game.state.party_ids = [&"rhen", &"asha", &"toma"] as Array[StringName]
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	(zone.get_node("CameraDirector") as FieldCameraDirector).auto_update = false
	player = zone.get_node("Player") as FieldController
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)
	stairs = player.get_node(NodePath(String(HeroStairs.NAME))) as HeroStairs
	stairs.set_physics_process(false)
	party = player.get_node(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
	party.set_physics_process(false)


func test_the_flight_profile_steps_and_from_row_builds_it() -> void:
	var f := HeroStairFlight.from_row({"id": "Flying", "foot": [0, 0, 0], "head": [0, RISE_48, -RUN_48], "width_m": 2})
	zone.add_child(f)
	assert_between(f.angle_deg(), 47.5, 48.5, "a 48° flight")
	assert_eq(f.steps(), roundi(RISE_48 / float(f.tuning["step_rise_m"])))
	assert_between(f.forward().dot(Vector3.FORWARD), 0.999, 1.001, "it climbs along -Z")
	var prev := -1.0
	var flat := 0
	var n := 400
	for i in n + 1:
		var h := f.height_at_run(RUN_48 * i / n)
		assert_true(h >= prev - 1e-6, "never down on the way up")
		if absf(h - prev) < 1e-6:
			flat += 1
		prev = h
	assert_between(prev, RISE_48 - 1e-4, RISE_48 + 1e-4, "the head at the top")
	var tread := 1.0 - float(f.tuning["riser_share"])
	assert_true(flat > n * tread * 0.75, "treads hold flat between the risers (%d of %d samples)" % [flat, n])
	f.free()
	_done()  # before_each's zone: left in the tree, it broke ~30 later tests (big13, 9f98ccf6)


func test_rhen_climbs_a_48_degree_flight_step_by_step() -> void:
	var f := _rig(RUN_48, RISE_48, 2.0)
	_place(Vector3(SITE_X, 0.0, 1.0))
	var track := _walk(UP, func() -> bool: return player.global_position.z < -RUN_48 - 1.0)
	assert_between(player.global_position.y, RISE_48 - TOL_M, RISE_48 + TOL_M, "up on the landing")
	assert_true(stairs.flight == null, "let go onto the landing")
	_assert_smooth(track, f, "climb")
	var ys: Array[float] = []
	for t in track:
		ys.append(t.origin.y)
	for i in range(1, ys.size()):
		assert_true(ys[i] >= ys[i - 1] - 1e-3, "never slips back down on the way up (frame %d)" % i)
	_done()


## The Lead's 10-29 walk audit: a full stick is a stair run (slope_run_speed_mps), so a long flight isn't a minute's
## crawl; holding walk keeps the slow climb (slope_speed_mps). Each holds its own speed along the slope.
func test_a_run_climbs_faster_than_a_walk() -> void:
	var f := _rig(RUN_48, RISE_48, 2.0)
	var frames := {}
	for walk: bool in [true, false]:
		_place(Vector3(SITE_X, 0.0, 1.0))
		player.walk_override = walk
		var track := _walk(UP, func() -> bool: return player.global_position.z < -RUN_48 - 1.0)
		_assert_smooth(track, f, "walk" if walk else "run")
		frames[walk] = track.size()
	player.walk_override = false
	var walk_s := float(stairs.tuning["slope_speed_mps"])
	var run_s := float(stairs.tuning["slope_run_speed_mps"])
	assert_true(run_s > walk_s, "the stair run is faster than the walk")
	assert_true(
		int(frames[false]) < int(frames[true]) * 0.75,
		"running up takes fewer frames (%d) than walking (%d)" % [frames[false], frames[true]]
	)
	_done()


func test_rhen_comes_down_a_60_degree_flight() -> void:
	var f := _rig(RUN_60, RISE_60, 1.6)
	_place(Vector3(SITE_X, RISE_60 + 0.02, -RUN_60 - 1.0))
	var track := _walk(DOWN, func() -> bool: return player.global_position.z > 1.0)
	assert_between(player.global_position.y, -TOL_M, TOL_M, "down on the lower floor")
	_assert_smooth(track, f, "descent")
	_done()


func test_standing_still_on_a_flight_does_not_slide() -> void:
	_rig(RUN_60, RISE_60, 1.6)
	_place(Vector3(SITE_X, 0.0, 0.8))
	_walk(UP, func() -> bool: return stairs.flight != null and stairs.along > RUN_60 * 0.5)
	player.input_override = Vector2.ZERO
	for i in 60:
		_step()
	var at := player.global_position
	for i in 120:
		_step()
	assert_true(player.global_position.distance_to(at) < 1e-4, "still is still on a 60° flight")
	assert_true(stairs.flight != null, "and still on it")
	_done()


func test_pushing_sideways_keeps_him_on_the_flight() -> void:
	var f := _rig(RUN_48, RISE_48, 1.6)
	_place(Vector3(SITE_X, 0.0, 0.8))
	_walk(UP, func() -> bool: return stairs.flight != null and stairs.along > RUN_48 * 0.4)
	player.input_override = RIGHT
	for i in 120:
		_step()
	var half := f.width_m * 0.5 - float(stairs.tuning["side_margin_m"])
	assert_between(f.local_of(player.global_position).x, half - TOL_M, half + TOL_M, "held inside the edge")
	assert_true(stairs.flight != null, "still on the flight")
	_done()


func test_walking_under_a_flying_stair_does_not_climb_it() -> void:
	var f := _rig(RUN_48, RISE_48, 2.0, false)
	_place(Vector3(SITE_X - 3.0, 0.0, -RUN_48 * 0.5))  # beside it, then across under it, 1.3 m below its steps
	player.input_override = RIGHT
	for i in 90:
		_step()
		assert_true(stairs.flight == null, "not on the flight above him")
	assert_between(player.global_position.y, -TOL_M, TOL_M, "on the floor under it")
	assert_true(player.global_position.x > SITE_X + f.width_m * 0.5, "and out the other side")
	f.free()
	_done()


func test_asha_and_toma_follow_him_up_the_steps() -> void:
	var f := _rig(RUN_48, RISE_48, 2.0)
	_place(Vector3(SITE_X, 0.0, 2.5))
	var guard := HeroMotionGuard.load_data()
	var tracks: Array = [[] as Array[Transform3D], [] as Array[Transform3D]]
	var on_steps := 0
	player.input_override = UP
	for i in MAX_FRAMES:
		_step()
		for k in party.followers.size():
			var fp := party.followers[k].global_position
			(tracks[k] as Array[Transform3D]).append(party.body_of(_ids()[k]).global_transform)
			if f.covers(fp):
				on_steps += 1
				var want := HeroStairs.height_at(zone, fp)
				assert_between(fp.y, want - 0.12, want + 0.12, "follower %d on the steps" % k)
		if player.global_position.z < -RUN_48 - 3.0:
			break
	assert_true(on_steps > 30, "they did climb the flight (%d follower-frames on it)" % on_steps)
	for k in party.followers.size():
		var snaps := HeroMotionGuard.snaps_only(
			HeroMotionGuard.transform_snaps(tracks[k] as Array[Transform3D], DT, guard["transform"])
		)
		assert_true(snaps.is_empty(), "follower %d never snaps on the stairs (%d)" % [k, snaps.size()])
	_done()


## A lower floor (top at 0, z > 0), an upper landing (top at `rise`, past the head), the flight from (SITE_X, 0, 0)
## up along -Z, and (when `block`) a solid box over its footprint up to its top, as a zone's blocking collision.
func _rig(run: float, rise: float, width: float, block: bool = true) -> HeroStairFlight:
	_box(Vector3(SITE_X, -0.5, 6.0), Vector3(8.0, 1.0, 12.0))
	_box(Vector3(SITE_X, rise - 0.5, -run - 4.0), Vector3(8.0, 1.0, 8.0))
	if block:
		_box(Vector3(SITE_X, rise * 0.5, -run * 0.5), Vector3(width, rise, run))
	else:
		_box(Vector3(SITE_X, -0.5, -run * 0.5), Vector3(8.0, 1.0, run + 1.0))  # an open floor under it
	var f := HeroStairFlight.from_row(
		{"id": "Flight", "foot": [SITE_X, 0.0, 0.0], "head": [SITE_X, rise, -run], "width_m": width}
	)
	zone.add_child(f)
	return f


## A static box of `size` centred at `at`, placed before it enters the tree (moved later, it waits for a physics step).
func _box(at: Vector3, size: Vector3) -> void:
	var body := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	body.add_child(shape)
	body.position = at
	zone.add_child(body)


func _place(at: Vector3) -> void:
	player.global_position = at
	player.velocity = Vector3.ZERO
	player.motor.facing_yaw = 0.0
	party.catch_up()


## Walks with `stick` until `done` holds (or MAX_FRAMES); returns the player's transforms, one per frame.
func _walk(stick: Vector2, done: Callable) -> Array[Transform3D]:
	var out: Array[Transform3D] = []
	player.input_override = stick
	for i in MAX_FRAMES:
		_step()
		out.append(_body().global_transform)  # the visible body (the controller's root turns at once by design)
		if done.call():
			break
	assert_true(done.call(), "got there in %d frames" % MAX_FRAMES)
	return out


func _step() -> void:
	player.step(DT)
	stairs.advance(DT)
	_body().advance(DT)
	party.advance(DT)
	for f in party.followers:
		(f.get_node(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor).advance(DT)


## No snap (HeroMotionGuard) and never faster than the slope speed along the flight.
func _assert_smooth(track: Array[Transform3D], f: HeroStairFlight, what: String) -> void:
	var guard := HeroMotionGuard.load_data()
	var snaps := HeroMotionGuard.snaps_only(HeroMotionGuard.transform_snaps(track, DT, guard["transform"]))
	for s in snaps:
		print("  %s frame %d: %s %.1f" % [what, s["frame"], s["kind"], s["value"]])
	assert_true(snaps.is_empty(), "the %s never snaps (%d)" % [what, snaps.size()])
	var cap := float(stairs.tuning["slope_speed_mps" if player.walk_override else "slope_run_speed_mps"])
	var path := 0.0
	var frames := 0
	for i in range(1, track.size()):
		var a := track[i - 1].origin
		var b := track[i].origin
		if f.covers(a) and f.covers(b):
			path += a.distance_to(b)
			frames += 1
	assert_true(frames > 0, "the %s crossed the flight" % what)
	var mean := path / maxf(frames * DT, DT)
	assert_true(mean <= cap * 1.15, "%s: %.2f m/s along the flight on average (slope speed %.2f)" % [what, mean, cap])


func _body() -> HeroFieldActor:
	return player.get_node(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor


func _ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for f in party.followers:
		out.append(StringName(f.get_meta(&"hero_id")))
	return out


func _done() -> void:
	zone.free()
	Game.state.party_ids = _party_was


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
