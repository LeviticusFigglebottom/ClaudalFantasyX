extends TestCase
## ADR 0111 amendment 4: a transition's prewarm stages the zone's runtime materials and scenes as ResidentLoads loads
## them (PrewarmZoneFeed), and the router waits on that staging as on a load. Without the feed a prewarm is no
## loader (-1), as amendment 2 has it.

const TEST_MATERIAL := "res://game/shaders/test/prewarm_test_material.tres"


func test_resident_loads_hands_the_zone_s_materials_and_scenes_over_once() -> void:
	var rl := ResidentLoads.new()
	var mat := load(TEST_MATERIAL) as Material
	var packed := _scene_with(mat)
	rl.set(&"_prewarm_queue", [mat, packed] as Array[Resource])
	assert_true(rl.prewarm_pending())
	assert_eq(rl.take_prewarm(1), [mat] as Array[Resource], "in load order, a frame's worth at a time")
	assert_eq(rl.take_prewarm(5), [packed] as Array[Resource])
	assert_true(rl.take_prewarm(5).is_empty(), "each only once")
	assert_false(rl.prewarm_pending(), "nothing left: the prewarm may clear its stage")
	rl.free()


func test_a_prewarm_counts_as_a_loader_only_while_it_feeds() -> void:
	var idle := _Holder.new(-1)
	var feeding := _Holder.new(7)
	assert_eq(SceneRouter.swap_progress([idle] as Array[Object]), -1, "-1: not loading, the frame cap only")
	assert_eq(SceneRouter.swap_progress([idle, feeding] as Array[Object]), 7, "a feeding prewarm's draws are work")


func test_the_feed_runs_only_for_a_transition_with_the_registry_on() -> void:
	var on := {"zone_loads": true, "zone_loads_per_frame": 3}
	assert_true(ResidentLoads.shared() != null, "the router's ResidentLoads is installed")
	assert_eq(PrewarmZoneFeed.for_transition({}, "res://x.tscn", false), null, "the registry off: no feed")
	assert_eq(PrewarmZoneFeed.for_transition(on, "res://x.tscn", true), null, "a boot run: no feed")
	assert_eq(PrewarmZoneFeed.for_transition(on, "", false), null, "no scene: no feed")
	var feed := PrewarmZoneFeed.for_transition(on, "res://x.tscn", false)
	assert_true(feed != null)
	if feed != null:
		assert_eq(feed.per_frame(), 3)


func test_a_pulled_scene_and_material_become_pending_draws() -> void:
	var prewarm := (load(ShaderPrewarm.SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	var mat := load(TEST_MATERIAL) as Material
	var rl := ResidentLoads.shared()
	var was: Array = (rl.get(&"_prewarm_queue") as Array).duplicate()
	rl.set(&"_prewarm_queue", [mat, _scene_with(mat)] as Array[Resource])
	var feed := PrewarmZoneFeed.for_transition({"zone_loads": true, "zone_loads_per_frame": 4}, "res://x.tscn", false)
	var added := feed.pull(prewarm, 64)
	assert_eq(added, 2, "the material on the quad, and the scene's mesh with its material")
	var pending: Array = prewarm.get(&"_pending")
	assert_true(pending[0] is Dictionary and str((pending[0] as Dictionary)["path"]) == TEST_MATERIAL)
	assert_true(pending[1] is Array, "the scene's [material, mesh, multimesh] pair")
	assert_eq(feed.pull(prewarm, 64), 0, "nothing more until the next loads land")
	rl.set(&"_prewarm_queue", was as Array[Resource])
	prewarm.free()


static func _scene_with(mat: Material) -> PackedScene:
	var mi := MeshInstance3D.new()
	var box := BoxMesh.new()
	mi.mesh = box
	mi.material_override = mat
	var packed := PackedScene.new()
	packed.pack(mi)
	mi.free()
	return packed


class _Holder:
	extends RefCounted
	var _p := 0

	func _init(p: int) -> void:
		_p = p

	func swap_wait_progress() -> int:
		return _p
