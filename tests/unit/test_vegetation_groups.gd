extends TestCase
## M1-ENV-05: Environment's vegetation joins the vegetation_detail groups (graphics_presets.json
## vegetation_groups) so the presets reach it: plant LOD meshes scale their ranges, grass scatters thin
## and may drop shadows, and small foliage (vines) may drop shadows on Low. Low then High round-trips.

const VEG_SCENE := "res://game/levels/_tests/vegetation/vegetation_test.tscn"

var _nodes: Array[Node] = []


func _add(n: Node) -> Node:
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(n)
	_nodes.append(n)
	return n


func _done() -> void:
	for n in _nodes:
		if is_instance_valid(n):
			n.free()
	_nodes.clear()


func _lod() -> StringName:
	return GraphicsSettings.vegetation_group(GraphicsSettings.VEG_GROUP_LOD)


func _mm() -> StringName:
	return GraphicsSettings.vegetation_group(GraphicsSettings.VEG_GROUP_MULTIMESH)


func _small() -> StringName:
	return GraphicsSettings.vegetation_group(GraphicsSettings.VEG_GROUP_SMALL_SHADOWS)


func test_group_names_come_from_the_presets_data() -> void:
	var groups := GraphicsSettings.new().data["vegetation_groups"] as Dictionary
	assert_eq(String(_lod()), str(groups["lod"]))
	assert_eq(String(_mm()), str(groups["multimesh"]))
	assert_eq(String(_small()), str(groups["small_shadows"]))
	assert_eq(GraphicsSettings.vegetation_group("nonsense"), &"")
	_done()


func test_the_vegetation_test_scene_is_tagged() -> void:
	var scene := _add((load(VEG_SCENE) as PackedScene).instantiate())
	var palm := scene.get_node("Plants/PalmA")
	var palm_meshes := palm.find_children("*", "MeshInstance3D", true, false)
	assert_false(palm_meshes.is_empty())
	for mi: Node in palm_meshes:
		if (mi as MeshInstance3D).visible:
			assert_true(mi.is_in_group(_lod()), "%s scales its LOD range" % mi.name)
			assert_false(mi.is_in_group(_small()), "a palm keeps its shadows")
	for mi: Node in scene.get_node("Plants/BeachVine1").find_children("*", "MeshInstance3D", true, false):
		assert_true(mi.is_in_group(_small()), "vines are small foliage")
	var grass := scene.get_node("Ground/SaltgrassTall")
	assert_true(grass.is_in_group(_mm()), "grass thins with vegetation_detail")
	assert_true(grass.is_in_group(_small()), "and may drop its shadows")
	_done()


func test_low_then_high_round_trips_on_the_tagged_scene() -> void:
	var scene := _add((load(VEG_SCENE) as PackedScene).instantiate())
	var grass := scene.get_node("Ground/SaltgrassTall") as MultiMeshInstance3D
	var vine := (
		scene.get_node("Plants/BeachVine1").find_children("*", "MeshInstance3D", true, false)[0] as MeshInstance3D
	)
	var palm_lod0: MeshInstance3D = null
	for mi: Node in scene.get_node("Plants/PalmA").find_children("*", "MeshInstance3D", true, false):
		if VegetationPlant.lod_index(mi.name) == 0:
			palm_lod0 = mi as MeshInstance3D
	var authored_end := palm_lod0.visibility_range_end
	var authored_shadow := vine.cast_shadow
	var gs := GraphicsSettings.new()
	var vp := scene.get_viewport()
	GraphicsSettings.execute(_group_ops(gs.plan("low")), vp, null)
	var low := gs.data["levels"]["vegetation_detail"]["low"] as Dictionary
	assert_between(
		palm_lod0.visibility_range_end, authored_end * float(low["visibility_scale"]) - 0.01, authored_end * 0.61, "Low"
	)
	assert_eq(grass.multimesh.visible_instance_count, roundi(grass.multimesh.instance_count * 0.5), "half the grass")
	assert_eq(vine.cast_shadow, GeometryInstance3D.SHADOW_CASTING_SETTING_OFF, "vine shadows off")
	GraphicsSettings.execute(_group_ops(gs.plan("high")), vp, null)
	assert_between(palm_lod0.visibility_range_end, authored_end - 0.01, authored_end + 0.01, "High restores")
	assert_eq(grass.multimesh.visible_instance_count, -1)
	assert_eq(vine.cast_shadow, authored_shadow)
	_done()


func test_the_haluna_dresser_tags_its_vegetation() -> void:
	var dresser := HalunaDresser.new()
	dresser.layout = HalunaDresser._load_json(dresser.layout_path)
	var spec := (dresser.layout["scatter"] as Array)[0] as Dictionary
	var kinds := dresser.layout["plant_kinds"] as Dictionary
	assert_true(bool((kinds["beach_vine_patch"] as Dictionary).get("small_foliage", false)), "vines are small foliage")
	assert_false(bool((kinds["palm_coconut_a"] as Dictionary).get("small_foliage", false)), "palms are not")
	dresser._scatter(spec)
	var mmi := dresser.get_child(0) as MultiMeshInstance3D
	assert_true(mmi.is_in_group(_mm()) and mmi.is_in_group(_small()), "the scatter is tagged")
	assert_true(mmi.is_in_group(_lod()), "and scales its authored visibility range")
	dresser._place_plant({"plant": "beach_vine_patch", "at": [0.0, 0.0]})
	var vine := dresser.get_child(1) as VegetationPlant
	assert_true(vine.small_foliage)
	dresser.free()
	_done()


func _group_ops(ops: Array[Dictionary]) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for op in ops:
		if op["target"] == GraphicsSettings.TARGET_GROUP:
			out.append(op)
	return out
