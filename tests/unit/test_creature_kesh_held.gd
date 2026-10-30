extends TestCase
## M5-A3P-1850 (act3_ending H03): Kesh's held form for her Ch21 release fight, as the Ch20 six (act3_roster.md, The
## Vowbound as foes). The same GLB in held light; its KO is `release`, held on its last frame: "She lifts and doesn't
## look at him", her light rising out of the top of the frame.

const ROW: StringName = &"kesh_held"
const HELD_COLOR := Color("#7FC6D9")
const COLOR_EPS := 0.02
const RELEASE_RISE_M := 1.5
const RELEASE_TURN_DEG := 15.0

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			if n.get_parent() != null:
				n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_the_held_row_releases_on_its_ko_and_holds_it() -> void:
	var row := CreatureActor.row_for(ROW)
	assert_eq(str(row.get("ko", "")), "release", "the KO is the release")
	var phase := (row.get("phases", {}) as Dictionary).get("release", {}) as Dictionary
	assert_eq(str(phase.get("clip", "")), "release")
	assert_true(bool(phase.get("hold", false)), "the release holds its last frame")
	assert_false(row.has("vowbound"), "the held form is a foe, not the ally")
	var a := _actor()
	assert_true(a.has_clip(&"release"), "the model has the release")
	a.set_ko(true, 0.0)
	assert_eq(a.current_clip, &"release", "a KO plays the release")
	before_each()


func test_the_held_form_wears_held_light() -> void:
	var a := _actor()
	var seen := 0
	for n: Node in a.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		for s in mi.get_surface_override_material_count():
			var m := mi.get_surface_override_material(s) as ShaderMaterial
			if m == null or m.get_shader_parameter("emission_color") == null:
				continue
			var c: Color = m.get_shader_parameter("emission_color")
			if c.v > 0.05:
				seen += 1
				assert_true(_near(c, HELD_COLOR), "%s's light is held cyan (%s)" % [mi.name, c.to_html(false)])
	assert_true(seen > 0, "some surface is lit (the check is live)")
	before_each()


func test_the_release_lifts_her_out_and_turns_her_face_away() -> void:
	var a := _actor()
	var skel := a.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	var ap := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	var head := skel.find_bone("head")
	ap.play(&"release")
	ap.seek(0.0, true)
	var start := skel.get_bone_global_pose(head)
	ap.seek(ap.get_animation(&"release").length, true)
	var end := skel.get_bone_global_pose(head)
	assert_true(end.origin.y - start.origin.y >= RELEASE_RISE_M, "she rises %.2f m" % (end.origin.y - start.origin.y))
	var turn := rad_to_deg(Vector2(start.basis.z.x, start.basis.z.z).angle_to(Vector2(end.basis.z.x, end.basis.z.z)))
	assert_true(absf(turn) >= RELEASE_TURN_DEG, "her face turns %.0f° away" % turn)
	before_each()


func _near(a: Color, b: Color) -> bool:
	return absf(a.r - b.r) < COLOR_EPS and absf(a.g - b.g) < COLOR_EPS and absf(a.b - b.b) < COLOR_EPS


func _actor() -> CreatureActor:
	var a := (load(str(CreatureActor.row_for(ROW).get("scene", ""))) as PackedScene).instantiate() as CreatureActor
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(a)
	made.append(a)
	return a
