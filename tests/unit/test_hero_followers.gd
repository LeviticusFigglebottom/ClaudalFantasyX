extends TestCase
## M2-HER-1102: HeroFieldParty, Asha and Toma on Rhen's trail: followers come from the live party
## (leader excluded, party order), keep their trail spacing and never crowd the leader, catch up after
## a teleport, react to a join, and hide while the stage shows the same hero or a cutscene holds the
## player.

const ZONE := "res://game/levels/_tests/field/field_test.tscn"
const DT := 1.0 / 60.0
const WALK_FRAMES := 240
## Obstacles past the Court kink the trail and the followers sway on it; by now (at the run speed) they have settled.
const RUN_FRAMES := 300
const UP := Vector2(0, -1)
const SLACK_M := 0.35

var zone: Node3D
var player: FieldController
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
	party = player.get_node(NodePath(String(HeroFieldParty.NAME))) as HeroFieldParty
	party.set_physics_process(false)
	party._cfg = party._cfg.duplicate()
	party._cfg["sight_clear_m"] = 0.0  # the trail itself: the step off the camera's line is test_qa_field_camera's
	zone.call("place_at", &"Court")
	party.advance(DT)


func test_followers_come_from_the_party_in_order() -> void:
	assert_eq(party.followers.size(), 2, "two followers")
	assert_eq(_ids(), [&"asha", &"toma"] as Array[StringName], "party order, the leader excluded")
	assert_true(party.body_of(&"asha") != null and party.body_of(&"asha").model != null, "Asha has a body")
	_done()


func test_no_follower_for_a_hero_not_in_the_party() -> void:
	Game.state.party_ids = [&"rhen", &"asha"] as Array[StringName]
	party.advance(DT)
	assert_eq(_ids(), [&"asha"] as Array[StringName])
	assert_true(party.body_of(&"toma") == null, "Toma has not joined")
	Game.state.party_ids.append(&"toma")
	party.advance(DT)
	assert_eq(_ids(), [&"asha", &"toma"] as Array[StringName], "a join adds a follower at once")
	_done()


func test_followers_keep_their_spacing_on_the_trail() -> void:
	var spacing := float(party._cfg["spacing_m"])
	var gap_min := float(party._cfg["min_gap_m"])
	player.input_override = UP
	var closest := INF
	for i in RUN_FRAMES:
		_step()
		closest = minf(closest, _flat(player.global_position, party.followers[0].global_position))
		closest = minf(closest, _flat(party.followers[0].global_position, party.followers[1].global_position))
	assert_true(closest >= gap_min - 0.01, "never nearer than min_gap_m (closest %.2f)" % closest)
	var d0 := _flat(player.global_position, party.followers[0].global_position)
	var d1 := _flat(party.followers[0].global_position, party.followers[1].global_position)
	assert_between(d0, spacing - SLACK_M, spacing + SLACK_M, "Asha a spacing behind Rhen at a run (%.2f)" % d0)
	assert_between(d1, spacing - SLACK_M, spacing + SLACK_M, "Toma a spacing behind Asha (%.2f)" % d1)
	var behind := (party.followers[0].global_position - player.global_position).dot(Vector3.FORWARD)
	assert_true(behind < 0.0, "she is behind him, not beside or ahead")
	assert_true(party.body_of(&"asha").loco.speed > 1.0, "and walks (the gait blend sees her speed)")
	player.input_override = Vector2.ZERO
	for i in WALK_FRAMES:
		_step()
	assert_true(party.body_of(&"asha").loco.speed < 0.05, "she stops when he stops")
	assert_between(
		_flat(player.global_position, party.followers[0].global_position), spacing - SLACK_M, spacing + SLACK_M
	)
	_done()


## Rhen runs, then turns back through his followers: each is pushed off him while it steers for its trail point,
## and the push never adds to its top speed (Ch7's galleries: Asha at 6.9 m/s, a snap to the field guard).
func test_a_follower_pushed_aside_keeps_its_top_speed() -> void:
	var top := float(party._cfg["max_speed_mps"]) * DT + 1e-4
	var fastest := 0.0
	for move: Vector2 in [UP, -UP]:
		player.input_override = move
		for i in RUN_FRAMES / 3:
			var was: Array[Vector3] = []
			for f in party.followers:
				was.append(f.global_position)
			_step()
			for k in party.followers.size():
				fastest = maxf(fastest, _flat(was[k], party.followers[k].global_position))
	assert_true(fastest <= top, "a follower's step is at most max_speed_mps (fastest %.3f m a frame)" % fastest)
	_done()


func test_feet_on_the_floor() -> void:
	for i in 30:
		_step()
	for f in party.followers:
		assert_between(
			f.global_position.y, player.global_position.y - 0.05, player.global_position.y + 0.05, "on the ground"
		)
	_done()


func test_a_teleport_catches_the_followers_up() -> void:
	zone.call("place_at", &"Causeway")
	party.advance(DT)
	var spacing := float(party._cfg["spacing_m"])
	for i in party.followers.size():
		var d := _flat(player.global_position, party.followers[i].global_position)
		assert_between(d, (i + 1) * spacing - 0.05, (i + 1) * spacing + 0.05, "follower %d put on the new trail" % i)
		assert_eq(party.body_of(_ids()[i]).loco.speed, 0.0, "with no gait from the jump")
	_done()


func test_hidden_while_the_stage_shows_the_same_hero() -> void:
	var stage := CutsceneStage.new()
	stage.name = "CutsceneStage"
	var actors := Node3D.new()
	actors.name = "Actors"
	stage.add_child(actors)
	var asha := Node3D.new()
	asha.name = "asha"
	actors.add_child(asha)
	zone.add_child(stage)
	party.rescan()
	party.advance(DT)
	assert_false(party.followers[0].visible, "no double Asha while the stage shows her")
	assert_true(party.followers[1].visible, "Toma still follows")
	asha.visible = false
	party.advance(DT)
	assert_true(party.followers[0].visible, "back when the stage hides her")
	_done()


func test_hidden_while_a_cutscene_holds_the_player() -> void:
	var seq := CutsceneSequencer.new()
	zone.add_child(seq)
	party.rescan()
	seq._playing = true
	party.advance(DT)
	for f in party.followers:
		assert_false(f.visible, "hidden during the cutscene")
	seq._playing = false
	party.advance(DT)
	for f in party.followers:
		assert_true(f.visible, "back after it")
	_done()


## M3-HER-1227: a cached sequencer freed in play (a scene's, or tools/act1/cutscene_stills') is skipped, not cast. A
## freed cast is a script error that aborts should_hide(), so the playing sequencer after it would never be seen.
func test_a_freed_cached_sequencer_is_skipped() -> void:
	var gone := CutsceneSequencer.new()
	zone.add_child(gone)
	var seq := CutsceneSequencer.new()
	zone.add_child(seq)
	party.rescan()
	assert_eq(party._sequencers.size(), 2, "both cached")
	gone.free()
	seq._playing = true
	assert_true(party.should_hide(), "the live sequencer behind the freed one still holds the player")
	party.advance(DT)
	for f in party.followers:
		assert_false(f.visible, "hidden during the cutscene")
	seq._playing = false
	assert_false(party.should_hide(), "and not after it")
	_done()


func test_followers_turn_to_face_who_rhen_talks_to() -> void:
	for i in 30:
		_step()
	var speaker := Interactable.new()
	zone.add_child(speaker)
	speaker.global_position = player.global_position + Vector3(4.0, 0.0, 0.0)  # off to his right
	player.interacted.emit(speaker)
	var guard := HeroMotionGuard.load_data()
	var dt := HeroMotionGuard.frame_sec(guard)
	var tracks: Array = [[] as Array[Transform3D], [] as Array[Transform3D]]
	for i in 90:
		_step()
		for k in party.followers.size():
			(tracks[k] as Array[Transform3D]).append(party.body_of(_ids()[k]).global_transform)
	for k in party.followers.size():
		var f := party.followers[k]
		var want := HeroLocomotion.yaw_of(speaker.global_position - f.global_position)
		var shown := party.body_of(_ids()[k]).visible_yaw()
		assert_between(absf(angle_difference(shown, want)), 0.0, deg_to_rad(5.0), "%s faces the speaker" % _ids()[k])
		var snaps := HeroMotionGuard.transform_snaps(tracks[k] as Array[Transform3D], dt, guard["transform"])
		assert_true(snaps.is_empty(), "%s turns to it without a snap" % _ids()[k])
	player.input_override = UP
	for i in 60:
		_step()
	var asha := party.body_of(&"asha")
	assert_true(asha.loco.speed > 0.5, "she walks on with him")
	var heading := HeroLocomotion.yaw_of(player.global_position - party.followers[0].global_position)
	assert_between(absf(angle_difference(asha.visible_yaw(), heading)), 0.0, deg_to_rad(30.0), "facing her walk again")
	_done()


func test_ysolde_follows_when_she_joins() -> void:
	Game.state.party_ids = [&"rhen", &"ysolde", &"toma"] as Array[StringName]
	party.advance(DT)
	assert_eq(_ids(), [&"ysolde", &"toma"] as Array[StringName], "Ysolde follows in party order")
	var body := party.body_of(&"ysolde")
	assert_true(body != null and body.model != null, "on her own model")
	player.input_override = UP
	for i in 120:
		_step()
	assert_true(body.loco.speed > 1.0, "and walks after him")
	_done()


func test_followers_never_stand_inside_a_wall_in_the_lane() -> void:
	zone.call("place_at", &"Lane")
	party.advance(DT)
	var sticks: Array[Vector2] = [
		Vector2(-0.7, -0.7), UP, Vector2(0.7, -0.7), UP, Vector2(-0.7, 0.7), Vector2(0.7, 0.7)
	]
	for stick in sticks:
		player.input_override = stick
		for i in 40:
			_step()
			for f in party.followers:
				assert_false(_inside_wall(f.global_position), "%s clear of the walls" % f.get_meta(&"hero_id"))
	_done()


func test_arriving_with_his_back_to_a_wall_puts_no_one_in_it() -> void:
	zone.call("place_at", &"Lane")
	player.global_position = Vector3(-2.4, 0.0, 8.0)  # a step off the tide wall (x = -3.2), his back to it
	player.motor.facing_yaw = -PI * 0.5
	player.rotation.y = player.motor.facing_yaw
	party.catch_up()
	for f in party.followers:
		assert_false(_inside_wall(f.global_position), "%s is not put in the wall" % f.get_meta(&"hero_id"))
	_done()


## The PC's GPU QA row 37 (the causeway's spawns): a camera right behind the arrival never gets a follower laid out
## in its foreground; every one stands at least camera_near_m (flat) from the lens.
func test_no_follower_is_laid_out_in_front_of_the_lens() -> void:
	zone.call("place_at", &"Court")
	var cam := Camera3D.new()
	zone.add_child(cam)
	var back := Basis(Vector3.UP, player.motor.facing_yaw) * Vector3.BACK  # his trail runs this way
	cam.global_position = player.global_position + back * 1.5 + Vector3.UP * 1.6
	cam.current = true
	party.catch_up()
	var near := float(party._cfg["camera_near_m"])
	for f in party.followers:
		var d := Vector2(f.global_position.x - cam.global_position.x, f.global_position.z - cam.global_position.z)
		assert_true(d.length() >= near - 1e-3, "%s stands %.2f m from the lens" % [f.get_meta(&"hero_id"), d.length()])
	for i in 120:  # standing there, they don't walk back into the foreground (they flank him instead)
		_step()
	for f in party.followers:
		var d := Vector2(f.global_position.x - cam.global_position.x, f.global_position.z - cam.global_position.z)
		assert_true(d.length() >= near - 0.05, "%s still %.2f m from the lens" % [f.get_meta(&"hero_id"), d.length()])
	_done()


## True when a follower's body (a 0.25 m sphere at its waist) overlaps a static collider.
func _inside_wall(at: Vector3) -> bool:
	var q := PhysicsShapeQueryParameters3D.new()
	var ball := SphereShape3D.new()
	ball.radius = 0.25
	q.shape = ball
	q.transform = Transform3D(Basis.IDENTITY, at + Vector3.UP * 0.9)
	q.exclude = [player.get_rid()]
	return not player.get_world_3d().direct_space_state.intersect_shape(q, 1).is_empty()


func _step() -> void:
	player.step(DT)
	party.advance(DT)
	for f in party.followers:
		var b := f.get_node(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
		b.advance(DT)


func _ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for f in party.followers:
		out.append(StringName(f.get_meta(&"hero_id")))
	return out


static func _flat(a: Vector3, b: Vector3) -> float:
	return Vector2(a.x - b.x, a.z - b.z).length()


func _done() -> void:
	zone.free()
	Game.state.party_ids = _party_was


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
