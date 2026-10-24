extends TestCase
## M2-FP-10: the dialogue-range key light. CutsceneKeyLight on its own (framing rule, engage and
## disengage), then the sequencer keying the cast on a close shot of the fixture scene and handing
## the cast back to the zone sun on release and at the end.

const ZONE := "res://game/levels/_tests/field/field_test.tscn"
const FIXTURE := &"test_cutscene_fixture"
const CLOSE_FOV := 27.0
const EPS := 0.001

var zone: Node3D
var director: FieldCameraDirector
var stage: CutsceneStage
var seq: CutsceneSequencer
var sun: DirectionalLight3D
var asha: Node3D
var face: MeshInstance3D
var cfg: Dictionary = {}
var saved_state: GameStateData


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	cfg = CutsceneSequencer.load_config().get("key_light", {})
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	director = zone.get_node("CameraDirector") as FieldCameraDirector
	director.auto_update = false
	(zone.get_node("Player") as FieldController).set_physics_process(false)
	zone.call("place_at", &"Lane")
	sun = zone.get_node("Sun") as DirectionalLight3D
	stage = _build_stage()
	seq = CutsceneSequencer.new()
	seq.set_process(false)
	seq.instant = true
	zone.add_child(seq)


func _build_stage() -> CutsceneStage:
	var s := CutsceneStage.new()
	s.name = "CutsceneStage"
	s.director_path = ^"../CameraDirector"
	s.player_path = ^"../Player"
	zone.add_child(s)
	var shots := Node.new()
	shots.name = "Shots"
	s.add_child(shots)
	_add_shot(shots, &"wide", Vector3(0, 6, 14), Vector3(0, 1, 0), CameraShot.USE_DEFAULT)
	_add_shot(shots, &"close", Vector3(1, 1.6, 9), Vector3(0, 1.4, 6), CLOSE_FOV)
	var actors := Node3D.new()
	actors.name = "Actors"
	s.add_child(actors)
	asha = Node3D.new()
	asha.name = "asha"
	actors.add_child(asha)
	face = MeshInstance3D.new()
	face.mesh = SphereMesh.new()
	face.layers = 1 | 4
	asha.add_child(face)
	var marks := Node3D.new()
	marks.name = "Marks"
	s.add_child(marks)
	var spot := Marker3D.new()
	spot.name = "spot"
	marks.add_child(spot)
	return s


func _add_shot(folder: Node, id: StringName, pos: Vector3, aim: Vector3, fov: float) -> void:
	var sn := CutsceneShotNode.new()
	sn.name = String(id)
	var shot := CameraShot.new()
	shot.id = id
	shot.position = pos
	shot.look_at = aim
	shot.fov_deg = fov
	sn.shot = shot
	folder.add_child(sn)


func _shot_node(id: StringName) -> CutsceneShotNode:
	return stage.shot_node(id)


# --- CutsceneKeyLight ------------------------------------------------------------------------


func test_close_means_dialogue_or_portrait_framing() -> void:
	var half := float(cfg["close_half_frame_m"])
	assert_true(half > 0.0, "sequencer.json key_light.close_half_frame_m")
	# Haluna's Cutscene A shots: H05 (Asha's face, ~0.4 m) and H06 (over Rhen, ~0.85 m) are close.
	assert_true(CutsceneKeyLight.is_close(Vector3(-0.85, 0.44, 8), Vector3(0.2, 0.95, 7.79), 37.8, cfg), "H05")
	assert_true(CutsceneKeyLight.is_close(Vector3(-0.4, 1.02, 4.5), Vector3(-0.4, 0.45, 8), 27.0, cfg), "H06")
	assert_false(CutsceneKeyLight.is_close(Vector3(120, 8, -5), Vector3(0, 23.4, -8), 53.1, cfg), "H01 is wide")
	assert_false(CutsceneKeyLight.is_close(Vector3.ZERO, Vector3(0, 0, -10), 37.8, cfg), "10 m at 37.8")
	_free()


func test_engage_keys_only_the_cast_and_disengage_restores_everything() -> void:
	var key := CutsceneKeyLight.new(cfg)
	stage.add_child(key)
	var sun_mask := sun.light_cull_mask
	key.engage(sun, stage.cast(), 0.0, 0.0, 1.0)
	var mask := key.layer_mask()
	assert_true(key.visible and key.is_engaged())
	assert_eq(face.layers, mask, "the cast's meshes sit on the key layer only")
	assert_eq(sun.light_cull_mask & mask, 0, "the sun no longer lights the cast")
	assert_eq(sun.light_cull_mask | mask, sun_mask | mask, "the sun's other layers are untouched")
	assert_eq(sun.shadow_caster_mask & mask, mask, "the cast still casts the sun's shadows")
	assert_eq(key.light_cull_mask, mask, "the key lights nothing but the cast")
	assert_eq(key.light_color, sun.light_color, "the sun's colour")
	assert_between(key.light_energy, sun.light_energy - EPS, sun.light_energy + EPS, "the sun's energy")
	assert_between(key.directional_shadow_max_distance, 0.0, float(cfg["shadow_max_distance_m"]) + EPS)
	assert_eq(key.shadow_normal_bias, float(cfg["shadow_normal_bias"]), "character_shading.md's face bias")
	assert_eq(key.sky_mode, DirectionalLight3D.SKY_MODE_LIGHT_ONLY, "no second sun disc in the sky")
	assert_eq(key.light_volumetric_fog_energy, 0.0, "no second sun in the fog")
	_assert_dir(key, -sun.global_basis.z, "aligned to the sun")
	key.disengage()
	assert_false(key.visible or key.is_engaged())
	assert_eq(face.layers, 1 | 4, "the mesh's own layers back")
	assert_eq(sun.light_cull_mask, sun_mask, "the sun's mask back")
	key.free()
	_free()


func test_shot_overrides_turn_and_scale_the_key() -> void:
	var key := CutsceneKeyLight.new(cfg)
	stage.add_child(key)
	key.engage(sun, stage.cast(), 90.0, 0.0, 0.5)
	assert_between(key.light_energy, sun.light_energy * 0.5 - EPS, sun.light_energy * 0.5 + EPS, "energy scale")
	_assert_dir(key, Basis(Vector3.UP, PI / 2.0) * -sun.global_basis.z, "yaw about world up")
	var down := -sun.global_basis.z
	key.engage(sun, stage.cast(), 0.0, 10.0, 1.0)
	assert_true((-key.global_basis.z).y > down.y, "positive pitch lowers the key toward the horizon")
	assert_eq(face.layers, key.layer_mask(), "re-engaging keeps the cast keyed")
	key.disengage()
	assert_eq(face.layers, 1 | 4, "and still restores the original layers")
	key.free()
	_free()


## The PC's FP-10 check: the key's layer must not be UndertowHalfRes.BODY_LAYER (layer 20), which the
## main camera culls, or a close shot in a storm zone would hide the cast. Checked against the class
## itself once it is in the project.
func test_the_key_layer_is_not_the_undertow_body_layer() -> void:
	var key := CutsceneKeyLight.new(cfg)
	assert_ne(key.layer_mask(), 1 << 19, "layer 20 is UndertowHalfRes.BODY_LAYER")
	for row: Dictionary in ProjectSettings.get_global_class_list():
		if str(row.get("class", "")) == "UndertowHalfRes":
			var body := int((load(str(row["path"])) as Script).get_script_constant_map().get("BODY_LAYER", 0))
			assert_eq(key.layer_mask() & body, 0, "the key layer and the storm's body layer differ")
	key.free()
	_free()


func test_stage_finds_the_zone_sun_and_the_cast() -> void:
	assert_eq(stage.sun(), sun, "the first shadow-casting DirectionalLight3D beside the stage")
	var cast := stage.cast()
	assert_true(asha in cast, "the actors")
	assert_true(zone.get_node("Player") in cast, "and the player")
	_free()


# --- the sequencer ---------------------------------------------------------------------------


func test_close_shot_keys_the_cast_and_release_and_end_hand_it_back() -> void:
	var sun_mask := sun.light_cull_mask
	var seen := {}
	seq.cue_played.connect(
		func(c: StringName, _a: Array, _k: Dictionary) -> void:
			# The cue after `@camera close` is `@mark`; after `@camera release` the next cue is `@fade`.
			if c == &"mark" or c == &"fade":
				seen[String(c) + str(seen.size())] = (
					seq.key_light() != null and face.layers == seq.key_light().layer_mask()
				)
	)
	await seq.play(FIXTURE, stage)
	assert_eq(seen.get("fade0"), false, "the opening fade is on the wide shot: no key")
	assert_eq(seen.get("mark1"), true, "the close shot keyed the cast")
	assert_eq(seen.get("fade2"), false, "release handed the cast back to the sun")
	assert_eq(seq.key_light(), null)
	assert_eq(face.layers, 1 | 4)
	assert_eq(sun.light_cull_mask, sun_mask)
	_free()


func test_shot_data_forces_the_key_on_or_off() -> void:
	_shot_node(&"close").key_light = CutsceneShotNode.KeyLight.OFF
	_shot_node(&"wide").key_light = CutsceneShotNode.KeyLight.ON
	var keyed: Array[bool] = []
	seq.cue_played.connect(
		func(c: StringName, _a: Array, _k: Dictionary) -> void:
			if c == &"mark" or c == &"fade":
				keyed.append(seq.key_light() != null)
	)
	await seq.play(FIXTURE, stage)
	assert_eq(keyed, [true, false, false] as Array[bool], "wide forced on, close forced off, released")
	_free()


func test_no_sun_is_a_soft_failure() -> void:
	sun.shadow_enabled = false
	await seq.play(FIXTURE, stage)
	assert_true(seq.warnings.any(func(w: String) -> bool: return w.contains("no sun")), str(seq.warnings))
	assert_eq(face.layers, 1 | 4, "nothing moved")
	_free()


func test_leaving_the_tree_mid_scene_restores_the_cast() -> void:
	seq.instant = false
	var sun_mask := sun.light_cull_mask
	_start()
	var frames := 0
	while seq.key_light() == null and seq.is_playing() and frames < 600:
		if seq.overlay.box.visible:
			seq.overlay.box.skip_reveal()
			seq.overlay.box.advance_requested.emit()
		director.update(1.0 / 30.0)
		seq.advance(1.0 / 30.0)
		frames += 1
	assert_true(seq.key_light() != null, "reached the close shot")
	zone.remove_child(seq)
	assert_eq(face.layers, 1 | 4, "the cast's layers back")
	assert_eq(sun.light_cull_mask, sun_mask, "the sun's mask back")
	seq.free()
	_free()


## Starts a real-time play without awaiting it (the runner is synchronous; see test_cutscene_sequencer).
func _start() -> void:
	await seq.play(FIXTURE, stage)


func _assert_dir(key: DirectionalLight3D, want: Vector3, msg: String) -> void:
	assert_between((-key.global_basis.z).angle_to(want), 0.0, 0.01, msg)


func _free() -> void:
	if zone != null:
		zone.free()
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
