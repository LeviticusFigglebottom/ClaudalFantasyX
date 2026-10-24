extends TestCase
## M2-FP-18: blinks and text-driven visemes on CutsceneFace, with sequencer.json's real "blink" and
## "visemes" tables. A synthetic rig (one triangle with Asha's lid and viseme shape names) stands in.

const SHAPES: Array[String] = [
	"lid_close_L",
	"lid_close_R",
	"mouth_smile_L",
	"mouth_smile_R",
	"vis_aa",
	"vis_e",
	"vis_i",
	"vis_o",
	"vis_u",
	"vis_mbp",
	"vis_fv",
	"jaw_open"
]
const EPS := 0.001
const DT := 1.0 / 60.0

var cfg: Dictionary = {}
var actor: Node3D
var mesh: MeshInstance3D


func before_each() -> void:
	cfg = CutsceneSequencer.load_config()
	actor = Node3D.new()
	mesh = MeshInstance3D.new()
	mesh.mesh = _shape_mesh(SHAPES)
	actor.add_child(mesh)


func test_the_viseme_track_follows_the_text() -> void:
	var track := FaceVisemes.track("Mama, fish!", cfg["visemes"])
	var opens: Array[StringName] = []
	var closes: Array[StringName] = []
	for row in track:
		opens.append(row["open"])
		closes.append(row["close"])
	assert_eq(opens, [&"aa", &"aa", &"i"] as Array[StringName], "ma-ma-fi(sh)")
	assert_eq(closes, [&"mbp", &"fv", &"rest"] as Array[StringName], "the lips close for m, then f; sh rests")
	assert_eq(FaceVisemes.track("...", cfg["visemes"]), [] as Array[Dictionary], "no vowels, no syllables")


func test_lip_flap_shows_each_syllable_in_turn() -> void:
	var rig := _rig()
	rig.say("Mama")
	rig.set_mouth_open(true)
	assert_between(_w("vis_aa"), 0.55 - EPS, 0.55 + EPS, "first syllable: aa")
	assert_true(_w("jaw_open") > 0.0)
	rig.set_mouth_open(false)
	assert_between(_w("vis_mbp"), 0.7 - EPS, 0.7 + EPS, "the lips meet for the next m")
	assert_eq(_w("vis_aa"), 0.0)
	rig.set_mouth_open(true)
	assert_between(_w("vis_aa"), 0.55 - EPS, 0.55 + EPS, "second syllable")
	rig.set_mouth_open(false)
	assert_eq(_w("vis_mbp"), 0.0, "the last syllable rests")
	_free()


func test_a_rig_without_viseme_shapes_keeps_the_plain_lip_flap() -> void:
	var bare := Node3D.new()
	var m := MeshInstance3D.new()
	m.mesh = _shape_mesh(["vis_aa", "jaw_open"] as Array[String])
	bare.add_child(m)
	var rig := CutsceneFace.new(bare, cfg["lip_flap"], cfg["visemes"])
	rig.say("Mama")
	assert_eq(rig.viseme_track(), [] as Array[Dictionary], "no track without the shapes")
	rig.set_mouth_open(true)
	var aa := m.get_blend_shape_value(m.find_blend_shape_by_name(&"vis_aa"))
	assert_between(aa, float(cfg["lip_flap"]["vis_aa"]) - EPS, float(cfg["lip_flap"]["vis_aa"]) + EPS)
	bare.free()
	_free()


func test_blinks_come_on_a_seeded_timer_and_close_the_lids() -> void:
	var a := _blink_times(7, 20.0)
	var b := _blink_times(7, 20.0)
	assert_eq(a, b, "the same seed blinks at the same times")
	assert_ne(a, _blink_times(8, 20.0), "another actor blinks at other times")
	var range: Array = cfg["blink"]["interval_s"]
	assert_true(a.size() >= int(20.0 / float(range[1])), "%d blinks in 20 s" % a.size())
	for i in range(1, a.size()):
		var gap := a[i] - a[i - 1]
		assert_true(gap >= float(range[0]) - 0.05, "gap %.2f s within the interval" % gap)
	# The lids reach fully closed mid-blink.
	var rig := _rig()
	rig.blink_now()
	rig.advance(float(cfg["blink"]["close_s"]) + 0.01)
	assert_between(_w("lid_close_L"), 1.0 - EPS, 1.0 + EPS, "closed")
	assert_between(_w("lid_close_R"), 1.0 - EPS, 1.0 + EPS)
	rig.advance(float(cfg["blink"]["hold_s"]) + float(cfg["blink"]["open_s"]) + 0.01)
	assert_eq(_w("lid_close_L"), 0.0, "open again")
	_free()


func test_an_emotion_change_blinks_once_and_blinks_layer_over_the_pose() -> void:
	var rig := _rig()
	rig.blend_to({"mouth_smile": 0.5, "lid_close": 0.3}, 0.0)
	assert_true(rig.is_blinking(), "a new expression comes with a blink")
	rig.advance(float(cfg["blink"]["close_s"]) + 0.01)
	assert_between(_w("lid_close_L"), 1.0 - EPS, 1.0 + EPS, "the blink wins over the pose's 0.3")
	assert_between(_w("mouth_smile_L"), 0.5 - EPS, 0.5 + EPS, "and leaves the mouth alone")
	rig.advance(1.0)
	assert_between(_w("lid_close_L"), 0.3 - EPS, 0.3 + EPS, "back to the pose's own lids")
	rig.advance(1.0)
	rig.blend_to({"mouth_smile": 0.5, "lid_close": 0.3}, 0.0)
	assert_false(rig.is_blinking(), "the same expression again is not a change")
	_free()


func test_the_sequencer_gives_every_posed_actor_a_blinking_rig_from_the_start() -> void:
	var zone := (load("res://game/levels/_tests/field/field_test.tscn") as PackedScene).instantiate() as Node3D
	_host().add_child(zone)
	(zone.get_node("CameraDirector") as FieldCameraDirector).auto_update = false
	(zone.get_node("Player") as FieldController).set_physics_process(false)
	var stage := CutsceneStage.new()
	stage.director_path = ^"../CameraDirector"
	stage.player_path = ^"../Player"
	zone.add_child(stage)
	var actors := Node3D.new()
	actors.name = "Actors"
	stage.add_child(actors)
	actor.name = "asha"
	actors.add_child(actor)
	var seq := CutsceneSequencer.new()
	seq.set_process(false)
	seq.instant = true
	zone.add_child(seq)
	seq.play.call(&"test_cutscene_fixture", stage)
	var rig := seq._face_rigs.get(&"asha") as CutsceneFace
	assert_true(rig != null, "asha's rig exists")
	var blinked := false
	for i in 600:
		seq.advance(DT)
		blinked = blinked or _w("lid_close_L") > 0.5
	assert_true(blinked, "she blinks within ten seconds")
	actor = null  # freed with the zone
	zone.free()
	_free()


func _rig() -> CutsceneFace:
	var rig := CutsceneFace.new(actor, cfg["lip_flap"], cfg["visemes"])
	rig.configure_blink(cfg["blink"], 1)
	return rig


## When blinks start over `sec` seconds for seed `s`.
func _blink_times(s: int, sec: float) -> Array[float]:
	var rig := CutsceneFace.new(actor, {}, {})
	rig.configure_blink(cfg["blink"], s)
	var out: Array[float] = []
	var t := 0.0
	var was := false
	while t < sec:
		rig.advance(DT)
		t += DT
		if rig.is_blinking() and not was:
			out.append(t)
		was = rig.is_blinking()
	return out


func _w(shape: String) -> float:
	return mesh.get_blend_shape_value(mesh.find_blend_shape_by_name(StringName(shape)))


func _shape_mesh(names: Array[String]) -> ArrayMesh:
	var am := ArrayMesh.new()
	for n in names:
		am.add_blend_shape(StringName(n))
	var tri := PackedVector3Array([Vector3.ZERO, Vector3.RIGHT, Vector3.UP])
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = tri
	var shapes := []
	for _n in names:
		var s := []
		s.resize(Mesh.ARRAY_MAX)
		s[Mesh.ARRAY_VERTEX] = tri
		shapes.append(s)
	am.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays, shapes)
	return am


func _free() -> void:
	if actor != null and is_instance_valid(actor):
		actor.free()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene
