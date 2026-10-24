extends TestCase
## M2-FP-08: @face and lines' [emotion] blend face shape keys through CutsceneFace, lip-flap opens
## the mouth, and idle/talk/walk clips play when the rig has them. A synthetic rig stands in for
## Asha: a triangle with her shape-key names and an AnimationPlayer with three empty clips. The
## poses are Asha's own (asha_face_poses.json, through sequencer.json "face_poses").

const ZONE := "res://game/levels/_tests/field/field_test.tscn"
const FIXTURE := &"test_cutscene_fixture"
const SHAPES: Array[String] = [
	"mouth_smile_L",
	"mouth_smile_R",
	"cheek_raise_L",
	"cheek_raise_R",
	"lid_squint_L",
	"lid_squint_R",
	"vis_aa",
	"jaw_open"
]
const CLIPS: Array[StringName] = [&"idle", &"talk", &"walk"]
const EPS := 0.001

var zone: Node3D
var stage: CutsceneStage
var seq: CutsceneSequencer
var asha: Node3D
var mesh: MeshInstance3D
var anims: AnimationPlayer
var saved_state: GameStateData


func before_each() -> void:
	saved_state = Game.state
	Game.state = GameStateData.new()
	zone = (load(ZONE) as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	(zone.get_node("CameraDirector") as FieldCameraDirector).auto_update = false
	(zone.get_node("Player") as FieldController).set_physics_process(false)
	stage = CutsceneStage.new()
	stage.director_path = ^"../CameraDirector"
	stage.player_path = ^"../Player"
	zone.add_child(stage)
	var actors := Node3D.new()
	actors.name = "Actors"
	stage.add_child(actors)
	asha = Node3D.new()
	asha.name = "asha"
	actors.add_child(asha)
	mesh = MeshInstance3D.new()
	mesh.mesh = _shape_mesh()
	asha.add_child(mesh)
	anims = AnimationPlayer.new()
	anims.name = "AnimationPlayer"
	var lib := AnimationLibrary.new()
	for c in CLIPS:
		var a := Animation.new()
		a.length = 1.0
		lib.add_animation(c, a)
	anims.add_animation_library(&"", lib)
	asha.add_child(anims)
	var marks := Node3D.new()
	marks.name = "Marks"
	stage.add_child(marks)
	var spot := Marker3D.new()
	spot.name = "spot"
	marks.add_child(spot)
	spot.position = Vector3(2, 0, 6)
	seq = CutsceneSequencer.new()
	seq.set_process(false)
	zone.add_child(seq)


func test_face_cues_and_line_emotions_blend_the_shape_keys() -> void:
	var rig := CutsceneFace.new(asha, {"vis_aa": 0.55})
	assert_true(rig.has_shapes())
	var poses := _poses()
	rig.blend_to(poses["soft_smile"], 0.0)
	assert_between(rig.weight(&"mouth_smile_L"), 0.35 - EPS, 0.35 + EPS, "soft_smile, left side of the pair")
	assert_between(rig.weight(&"mouth_smile_R"), 0.32 - EPS, 0.32 + EPS, "right side")
	assert_between(rig.weight(&"cheek_raise_R"), 0.15 - EPS, 0.15 + EPS, "a scalar drives both sides")
	rig.blend_to(poses["neutral"], 1.0)
	rig.advance(0.5)
	var mid := rig.weight(&"mouth_smile_L")
	assert_true(mid < 0.35 and mid > 0.08, "halfway through the blend (%s)" % mid)
	rig.advance(0.6)
	assert_between(rig.weight(&"mouth_smile_L"), 0.08 - EPS, 0.08 + EPS, "landed on neutral")
	assert_eq(rig.weight(&"cheek_raise_L"), 0.0, "shapes the new pose leaves out return to 0")
	rig.set_mouth_open(true)
	assert_between(rig.weight(&"vis_aa"), 0.55 - EPS, 0.55 + EPS, "lip-flap opens the mouth")
	rig.set_mouth_open(false)
	assert_eq(rig.weight(&"vis_aa"), 0.0)
	_free()


func test_the_sequencer_drives_face_and_clips_on_a_rig() -> void:
	seq.instant = true
	var clips: Array[StringName] = []
	anims.animation_started.connect(func(n: StringName) -> void: clips.append(n))
	seq.play.call(FIXTURE, stage)
	assert_false(seq.is_playing())
	# The fixture's last face word is `@face asha neutral 0.2`, after `Asha [soft_smile]`.
	assert_between(_w("mouth_smile_L"), 0.08 - EPS, 0.08 + EPS, "@face neutral landed")
	assert_eq(_w("cheek_raise_L"), 0.0)
	assert_eq(StringName(anims.current_animation), &"idle", "after the walk the rig idles")
	assert_true(&"walk" in clips, "the @mark walk played the walk clip: %s" % [clips])
	assert_true(&"talk" in clips, "her line played the talk clip")
	assert_eq(_w("vis_aa"), 0.0, "the mouth is closed at the end")
	_free()


func test_actors_without_shapes_or_poses_are_left_alone() -> void:
	var bare := Node3D.new()
	assert_false(CutsceneFace.new(bare).has_shapes())
	bare.free()
	seq.instant = true
	stage.get_node("Actors/asha").name = "toma"  # no face_poses row for toma
	seq.play.call(FIXTURE, stage)
	assert_false(seq.is_playing(), "plays to the end")
	assert_eq(_w("mouth_smile_L"), 0.0, "no pose table, no face change")
	_free()


func _w(shape: String) -> float:
	return mesh.get_blend_shape_value(mesh.find_blend_shape_by_name(StringName(shape)))


func _poses() -> Dictionary:
	var path := str((CutsceneSequencer.load_config()["face_poses"] as Dictionary)["asha"])
	return (JSON.parse_string(FileAccess.get_file_as_string(path)) as Dictionary)["emotions"]


func _shape_mesh() -> ArrayMesh:
	var am := ArrayMesh.new()
	for n in SHAPES:
		am.add_blend_shape(StringName(n))
	var tri := PackedVector3Array([Vector3.ZERO, Vector3.RIGHT, Vector3.UP])
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = tri
	var shapes := []
	for n in SHAPES:
		var a := []
		a.resize(Mesh.ARRAY_MAX)
		a[Mesh.ARRAY_VERTEX] = tri
		shapes.append(a)
	am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays, shapes)
	return am


func _free() -> void:
	zone.free()
	Game.state = saved_state


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
