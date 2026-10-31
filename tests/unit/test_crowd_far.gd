extends TestCase
## M5-A3P-1809: CrowdFar, distant crowds as flipbooks of baked poses (game/world/npc/crowd_far.gd), on the review
## stage's data (Ch20 U04's remembered Reefball crowd).

const DT := 1.0 / 60.0
const STAGE := "res://game/levels/_tests/npc/held_shapes_reefball.json"

var made: Array[Node] = []


func _crowd() -> CrowdFar:
	var cf := CrowdFar.new()
	cf.auto_build = false
	cf.data_path = STAGE
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(cf)
	made.append(cf)
	return cf


func _done() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func test_a_body_bakes_into_distinct_static_poses() -> void:
	var cf := _crowd()
	var meshes := cf.bake("crowd_man_lean_a", &"cheer", 3)
	assert_eq(meshes.size(), 3, "one mesh a pose")
	assert_true(meshes[0].get_surface_count() > 0, "the body's surfaces are baked")
	var a := meshes[0].get_aabb()
	var b := meshes[1].get_aabb()
	assert_true(a.size.y > 1.0, "a person's height (%.2f m)" % a.size.y)
	assert_false(a.is_equal_approx(b), "the poses differ (the arms pump)")
	for s in meshes[0].get_surface_count():
		assert_eq(meshes[0].surface_get_arrays(s)[Mesh.ARRAY_BONES], null, "no skin left")
	assert_eq(cf.get_child_count(), 0, "the posing actor is freed")
	_done()


func test_the_stage_crowd_shows_each_person_in_one_pose() -> void:
	var cf := _crowd()
	assert_eq(cf.build(), 32, "the stand's 32 held shapes")
	var bodies := {}
	for g in cf.groups:
		bodies[g["body"]] = true
	assert_eq(cf.draw_calls(), bodies.size() * cf.frame_count, "one draw call a body and pose, not one a person")
	var mat := (cf.groups[0]["poses"][0] as MultiMeshInstance3D).material_override as ShaderMaterial
	assert_true(mat != null and mat.shader == NpcSilhouette.SHADER, "the held silhouette")
	var changed := 0
	for f in 120:
		var before := _shown(cf)
		cf.step(DT)
		# (the headless renderer keeps no instance transforms to read back, so the layer's own record is checked)
		for g in cf.groups:
			var shown: PackedInt32Array = g["shown"]
			for i in (g["places"] as Array).size():
				assert_eq(shown[i], cf.pose_of(g, i), "each person shows in its one current pose")
				assert_between(shown[i], 0, cf.frame_count - 1, "a pose that exists")
		if _shown(cf) != before:
			changed += 1
	assert_true(changed > 0, "the poses flip")
	assert_true(_distinct_phases(cf) > 1, "not everyone in step")
	_done()


func test_same_data_same_poses() -> void:
	var a := _crowd()
	var b := _crowd()
	a.build()
	b.build()
	for f in 47:
		a.step(DT)
		b.step(DT)
	assert_eq(_shown(a), _shown(b), "deterministic: ids and deltas only")
	_done()


func _shown(cf: CrowdFar) -> Array:
	var out := []
	for g in cf.groups:
		out.append((g["shown"] as PackedInt32Array).duplicate())
	return out


func _distinct_phases(cf: CrowdFar) -> int:
	var seen := {}
	for g in cf.groups:
		for s in g["shown"] as PackedInt32Array:
			seen[s] = true
	return seen.size()


## In a zone the skinning runs on the WorkerThreadPool and the crowd shows when it's done, the same meshes as at once.
func test_a_threaded_build_matches_the_one_at_once() -> void:
	var a := _crowd()
	var b := _crowd()
	a.build()
	b.build_threaded()
	b.wait_built()
	assert_true(b.is_built() and b.person_count() == 32, "the threaded crowd is placed")
	assert_eq(b.draw_calls(), a.draw_calls(), "the same poses")
	for gi in a.groups.size():
		for f in a.frame_count:
			var ma := ((a.groups[gi]["poses"] as Array)[f] as MultiMeshInstance3D).multimesh.mesh
			var mb := ((b.groups[gi]["poses"] as Array)[f] as MultiMeshInstance3D).multimesh.mesh
			assert_true(ma.get_aabb().is_equal_approx(mb.get_aabb()), "pose %d of %s" % [f, a.groups[gi]["body"]])
	_done()
