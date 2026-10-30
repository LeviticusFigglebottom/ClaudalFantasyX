extends TestCase
## M2-HER-1101: HeroFieldActor, the real hero body on the field player (and on the cutscene stage's hero
## capsules): the hook hides the capsule and shows the model, the gait blend follows the measured
## speed, the visible yaw never turns faster than the cap (a 180 degree stick reversal through
## FieldController.step) and lands on the facing, teleports snap, play_clip plays over locomotion, and
## the data's clip speeds match the clips' measured foot plant.

const ZONE := "res://game/levels/_tests/field/field_test.tscn"
const DT := 1.0 / 60.0
const EPS := 0.0005
const SETTLE_FRAMES := 90
const UP := Vector2(0, -1)
const DOWN := Vector2(0, 1)

var zone: Node3D
var player: FieldController
var _party_was: Array[StringName] = []


func before_each() -> void:
	_party_was = Game.state.party_ids.duplicate()
	Game.state.party_ids.clear()
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	(zone.get_node("CameraDirector") as FieldCameraDirector).auto_update = false
	player = zone.get_node("Player") as FieldController
	player.set_physics_process(false)
	player.set_process_unhandled_input(false)


func test_the_hook_hides_the_capsule_and_shows_rhen() -> void:
	var body := _body()
	assert_true(body != null, "FieldController._ready attached a hero body")
	if body == null:
		_done()
		return
	assert_eq(body.hero_id, &"rhen", "an empty party leads with field.leader_default")
	assert_false((player.get_node("StandIn") as Node3D).visible, "the capsule stand-in is hidden")
	assert_false((player.get_node("Facing") as Node3D).visible, "the facing nub is hidden")
	assert_true(body.model != null and body.model.is_visible_in_tree(), "the model shows")
	assert_true(body.tree != null and body.tree.active, "its AnimationTree runs")
	assert_eq(HeroFieldActor.attach(player), body, "attach is idempotent")
	assert_eq(player.find_children(String(HeroFieldActor.NAME), "", false, false).size(), 1, "one body")
	_done()


func test_the_body_breathes_standing_and_not_walking() -> void:
	var body := _body()
	var micro := HeroMotion.micro_of(body.model)
	assert_true(micro != null, "the field body carries the idle micro-motion (M2-HER-1104)")
	if micro == null:
		_done()
		return
	body.snap()
	body.advance(DT)
	assert_eq(micro.amount, 1.0, "full micro-motion while standing")
	_drive(body, body.loco.walk_clip_mps)
	assert_eq(micro.amount, 0.0, "faded out while walking")
	_done()


func test_rhen_carries_the_zone_lantern_light_on_his_lantern() -> void:
	var body := _body()
	var light := OmniLight3D.new()
	light.name = "LanternLight"
	player.add_child(light)
	body._carry()
	assert_true(light in body.carried, "the LanternLight is carried")
	assert_true(light.get_parent() is BoneAttachment3D, "it hangs from a bone of the model")
	body.snap()
	for i in 3:
		body.advance(DT)
	var spec := ((HeroFieldActor.field_data()["heroes"] as Dictionary)["rhen"]["carry"] as Array)[0] as Dictionary
	var at: Array = spec["at_model"]
	var want := body.model.global_transform * Vector3(float(at[0]), float(at[1]), float(at[2]))
	assert_true(light.global_position.distance_to(want) < 0.15, "it sits in the lantern glass (idle sways it a little)")
	_done()


func test_the_model_has_the_locomotion_clips() -> void:
	var body := _body()
	for clip: String in (HeroFieldActor.field_data()["locomotion_clips"] as Dictionary).values():
		assert_true(body.tree.has_animation(StringName(clip)), "clip %s exists" % clip)
	_done()


func test_the_feet_sit_on_the_controller_origin_facing_its_forward() -> void:
	var body := _body()
	body.advance(DT)
	assert_true(body.global_position.distance_to(player.global_position) < EPS, "feet on the origin")
	# the model faces +Z, so its +Z must be the controller's forward (-Z of its yaw)
	var model_fwd := body.global_basis.z
	var field_fwd := Basis(Vector3.UP, player.motor.facing_yaw) * Vector3.FORWARD
	assert_true(model_fwd.distance_to(field_fwd) < 0.01, "the model faces the field's forward")
	_done()


func test_the_gait_blend_tracks_the_ground_speed() -> void:
	var body := _body()
	body.snap()
	for i in SETTLE_FRAMES:
		body.advance(DT)
	assert_between(body.gait_weights()[HeroLocomotion.IDLE], 1.0 - EPS, 1.0 + EPS, "idle at rest")
	_drive(body, body.loco.walk_clip_mps)
	assert_true(body.gait_weights()[HeroLocomotion.WALK] > 0.95, "walk at the walk clip speed")
	assert_between(
		float(body.tree.get(HeroFieldActor.P_BLEND)), body.loco.walk_clip_mps - 0.05, body.loco.walk_clip_mps + 0.05
	)
	_drive(body, body.loco.run_clip_mps)
	assert_true(body.gait_weights()[HeroLocomotion.RUN] > 0.95, "run at the run clip speed")
	_drive(body, body.loco.run_clip_mps * 1.2)
	assert_true(float(body.tree.get(HeroFieldActor.P_SCALE)) > 1.1, "past the run clip speed the run speeds up")
	_done()


func test_the_tree_animates_the_skeleton() -> void:
	var body := _body()
	var sk := body.model.find_child("Skeleton3D", true, false) as Skeleton3D
	var thigh := sk.find_bone("DEF-thigh.L")
	var poses: Array[Quaternion] = []
	for i in 6:
		body.source.global_position += Vector3(0.0, 0.0, -body.loco.walk_clip_mps * DT * 10.0)
		body.advance(DT * 10.0)
		poses.append(sk.get_bone_pose_rotation(thigh))
	var moved := false
	for q in poses:
		moved = moved or not q.is_equal_approx(poses[0])
	assert_true(moved, "the walking body swings its legs")
	_done()


func test_a_stick_reversal_never_turns_the_body_faster_than_the_cap() -> void:
	var body := _body()
	zone.call("place_at", &"Court")
	body.snap()
	player.input_override = UP
	for i in SETTLE_FRAMES:
		_step(body)
	var cap := body.loco.max_rate_rad * DT
	var prev := body.visible_yaw()
	var worst := 0.0
	player.input_override = DOWN
	for i in SETTLE_FRAMES * 2:
		_step(body)
		worst = maxf(worst, absf(angle_difference(prev, body.visible_yaw())))
		prev = body.visible_yaw()
	assert_true(worst <= cap + EPS, "worst frame %.4f rad <= cap %.4f" % [worst, cap])
	assert_true(worst > 0.0, "it did turn")
	assert_between(absf(angle_difference(body.visible_yaw(), player.motor.facing_yaw)), 0.0, 0.01, "lands on travel")
	player.input_override = Vector2.ZERO
	for i in SETTLE_FRAMES * 2:
		_step(body)
	assert_between(absf(angle_difference(body.visible_yaw(), player.motor.facing_yaw)), 0.0, 0.01, "rests on facing")
	_done()


func test_a_still_body_eases_to_a_cutscene_face() -> void:
	var body := _body()
	body.snap()
	var target := PI / 2.0
	player.rotation.y = target
	player.motor.facing_yaw = target
	body.advance(DT)
	assert_true(absf(angle_difference(body.visible_yaw(), target)) > 0.1, "no snap on _face")
	for i in SETTLE_FRAMES:
		body.advance(DT)
	assert_between(absf(angle_difference(body.visible_yaw(), target)), 0.0, 0.01, "eases onto the facing")
	_done()


func test_a_teleport_snaps_position_yaw_and_gait() -> void:
	var body := _body()
	body.snap()
	player.global_position += Vector3(body.loco.teleport_m * 4.0, 0.0, 0.0)
	player.motor.facing_yaw = 1.0
	body.advance(DT)
	assert_true(body.global_position.distance_to(player.global_position) < EPS, "on the new spot")
	assert_between(body.visible_yaw(), 1.0 - EPS, 1.0 + EPS, "on the new facing at once")
	assert_eq(body.loco.speed, 0.0, "no gait from the jump")
	_done()


func test_play_clip_plays_over_locomotion_and_returns() -> void:
	var body := _body()
	assert_true(body.play_clip(&"talk", 0.1), "a looping clip plays")
	assert_eq(body.action, &"talk")
	for i in SETTLE_FRAMES * 4:
		body.advance(DT)
	assert_eq(body.action, &"talk", "a loop stays until the next call")
	assert_true(body.play_clip(&"take_hand"), "a one-shot plays")
	var length := body.tree.get_animation(&"take_hand").length
	for i in int(ceil(length / DT)) + 2:
		body.advance(DT)
	assert_eq(body.action, &"", "a one-shot returns to locomotion when it ends")
	assert_true(body.play_clip(&"take_hand", 0.0, true))
	for i in int(ceil(length / DT)) + 2:
		body.advance(DT)
	assert_eq(body.action, &"take_hand", "held one-shots keep their pose")
	assert_true(body.play_clip(&"walk"), "a locomotion clip returns to the blend")
	assert_eq(body.action, &"")
	assert_false(body.play_clip(&"no_such_clip"), "a missing clip is refused")
	body.anim.play(&"talk")
	body.advance(DT)
	assert_eq(body.action, &"talk", "a play on the model's AnimationPlayer is routed through play_clip")
	assert_false(body.anim.is_playing(), "and the player itself stays still")
	_done()


func test_stage_hero_capsules_get_bodies_and_others_keep_theirs() -> void:
	var stage := CutsceneStage.new()
	stage.name = "CutsceneStage"
	var actors := Node3D.new()
	actors.name = "Actors"
	stage.add_child(actors)
	var toma := _capsule_actor("toma")
	var villager := _capsule_actor("villager")
	var real := Node3D.new()
	real.name = "asha"
	real.add_child(AnimationPlayer.new())
	actors.add_child(toma)
	actors.add_child(villager)
	actors.add_child(real)
	zone.add_child(stage)
	var bodies := HeroFieldActor.attach_stage(stage)
	assert_eq(bodies.size(), 1, "only the hero capsule gets a body")
	assert_false((toma.get_node("StandIn") as Node3D).visible, "the hero capsule hides")
	assert_true((villager.get_node("StandIn") as Node3D).visible, "a villager keeps its capsule")
	assert_true(real.get_node_or_null(NodePath(String(HeroFieldActor.NAME))) == null, "a real model is left alone")
	var body := bodies[0] if not bodies.is_empty() else null
	if body != null:
		toma.global_position += Vector3(0.0, 0.0, -body.loco.walk_clip_mps * DT)
		body.advance(DT)
		assert_true(body.loco.speed > 0.0, "a cutscene move of the actor root walks the body")
		assert_true(body.global_position.distance_to(toma.global_position) < EPS, "the body follows the root")
	_done()


## ADR 0041: an actor that plays a hero under another name (vigil_asha, ysolde_edge) takes that hero's body; one
## whose hero has no model yet (vigil_pell) keeps its capsule.
func test_aliased_stage_actors_get_their_heroes_bodies() -> void:
	assert_eq(HeroFieldActor.hero_of(&"vigil_asha"), &"asha", "a prefix")
	assert_eq(HeroFieldActor.hero_of(&"ysolde_edge"), &"ysolde", "an alias")
	assert_eq(HeroFieldActor.hero_of(&"toma"), &"toma", "a hero id is itself")
	assert_eq(HeroFieldActor.hero_of(&"neme"), &"neme", "anyone else is left as is")
	var stage := CutsceneStage.new()
	stage.name = "CutsceneStage"
	var actors := Node3D.new()
	actors.name = "Actors"
	stage.add_child(actors)
	var vigil := _capsule_actor("vigil_asha")
	var edge := _capsule_actor("ysolde_edge")
	var pell := _capsule_actor("vigil_pell")
	for a in [vigil, edge, pell]:
		actors.add_child(a)
	zone.add_child(stage)
	var bodies := HeroFieldActor.attach_stage(stage)
	var ids: Array[String] = []
	for b in bodies:
		ids.append(String(b.hero_id))
	ids.sort()
	assert_eq(ids, ["asha", "ysolde"] as Array[String], "Asha's vigil and Ysolde at the edge get bodies")
	assert_false((vigil.get_node("StandIn") as Node3D).visible, "the vigil's capsule hides")
	assert_true((pell.get_node("StandIn") as Node3D).visible, "Pell (no model yet) keeps his")
	_done()


## M3-HER-1225: Sefir has no stepping walk, only walk_glide; his row maps walk and run to it (`clips`), so his stage
## actor (Ch6's reed bank) takes his model and glides when a cutscene walks him, instead of standing as a capsule.
func test_sefir_s_stage_actor_takes_his_body_and_glides() -> void:
	assert_eq(HeroFieldActor.clips_of(&"sefir").get("walk"), "walk_glide", "his walk is his glide")
	assert_eq(
		HeroFieldActor.clips_of(&"rhen").get("walk"), HeroFieldActor.clips_of(&"asha").get("walk"), "others keep theirs"
	)
	var stage := CutsceneStage.new()
	stage.name = "CutsceneStage"
	var actors := Node3D.new()
	actors.name = "Actors"
	stage.add_child(actors)
	var sefir := _capsule_actor("sefir")
	actors.add_child(sefir)
	zone.add_child(stage)
	var bodies := HeroFieldActor.attach_stage(stage)
	assert_eq(bodies.size(), 1, "Sefir gets a body")
	if not bodies.is_empty():
		var body := bodies[0]
		assert_false((sefir.get_node("StandIn") as Node3D).visible, "his capsule hides")
		assert_true(body.tree != null and body.tree.has_animation(&"walk_glide"), "his tree has his glide")
		for i in SETTLE_FRAMES:
			sefir.global_position += Vector3(0.0, 0.0, -body.loco.walk_clip_mps * DT)
			body.advance(DT)
		assert_true(body.loco.speed > 0.0, "a cutscene walk moves him on his glide")
	_done()


## The speeds the body actually uses (locomotion.json's once M2-CHR-12 is in, else hero_motion.json's)
## against HeroClipGait's own measure of whichever clips the model has.
func test_the_clip_speeds_match_the_measured_foot_plant() -> void:
	var f := HeroFieldActor.field_data()
	for id: String in (f["heroes"] as Dictionary).keys():
		if HeroFieldActor.scene_path(StringName(id)) == "":
			continue  # a hero whose model has not reached this branch yet (it gets no body until it does)
		var row := (f["heroes"] as Dictionary)[id] as Dictionary
		var speeds := HeroFieldActor.gait_speeds(StringName(id))
		var cfg := HeroFieldActor.measure_config(StringName(id))
		var tol := float(cfg["measure_tolerance"])
		var m := (load(str(row["scene"])) as PackedScene).instantiate()
		var has_new := (m.find_child("AnimationPlayer", true, false) as AnimationPlayer).has_animation(&"walk_start")
		assert_eq(str(speeds["source"]) == "locomotion", has_new, "%s: locomotion.json speeds with its clips" % id)
		var clips := HeroFieldActor.clips_of(StringName(id))  # a hero's own clips (Sefir glides on walk_glide)
		for k: String in ["walk", "run"]:
			var measured := HeroClipGait.clip_speed(m, StringName(str(clips.get(k, k))), cfg)
			var data_mps := float(speeds["%s_clip_mps" % k])
			assert_true(measured > 0.0, "%s %s measured" % [id, k])
			assert_between(
				data_mps,
				measured * (1.0 - tol),
				measured * (1.0 + tol),
				"%s %s (%s): data %.2f vs %.2f" % [id, k, speeds["source"], data_mps, measured]
			)
		m.free()
	_done()


func _drive(body: HeroFieldActor, speed: float) -> void:
	var src := body.source
	for i in SETTLE_FRAMES:
		src.global_position += Vector3(0.0, 0.0, -speed * DT)
		body.advance(DT)


func _step(body: HeroFieldActor) -> void:
	player.step(DT)
	body.advance(DT)


func _capsule_actor(id: String) -> Node3D:
	var a := Node3D.new()
	a.name = id
	var mi := MeshInstance3D.new()
	mi.name = "StandIn"
	mi.mesh = CapsuleMesh.new()
	a.add_child(mi)
	return a


func _body() -> HeroFieldActor:
	var b := player.get_node_or_null(NodePath(String(HeroFieldActor.NAME))) as HeroFieldActor
	if b != null:
		b.set_process(false)
	return b


func _done() -> void:
	zone.free()
	Game.state.party_ids = _party_was


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
