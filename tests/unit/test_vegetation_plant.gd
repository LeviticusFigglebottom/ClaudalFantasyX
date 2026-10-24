extends TestCase
## M1-ENV-03: VegetationPlant LOD cross-fade and solid-occluder shelter, plus the foliage shader's
## shelter instance uniform on every tier.

const FOLIAGE_SHADERS: Array[String] = [
	"res://game/shaders/vegetation/vegetation_foliage.gdshader",
	"res://game/shaders/vegetation/vegetation_foliage_low.gdshader",
]


func _plant_with_lods(count: int) -> VegetationPlant:
	var plant := VegetationPlant.new()
	for i in count:
		var mi := MeshInstance3D.new()
		mi.name = "frond-lod%d" % i
		var quad := QuadMesh.new()
		quad.size = Vector2(1.0, 2.0)
		mi.mesh = quad
		mi.position = Vector3(0.0, 1.0, 0.0)
		plant.add_child(mi)
	return plant


func _mesh(plant: VegetationPlant, lod: int) -> MeshInstance3D:
	return plant.get_node("frond-lod%d" % lod) as MeshInstance3D


func test_only_the_last_lod_fades_out() -> void:
	var plant := _plant_with_lods(3)
	plant.lod_end_m = PackedFloat32Array([45.0, 120.0, 400.0])
	plant.lod_fade_m = 6.0
	plant.lod_margin_m = 2.0
	plant.apply()
	# Godot's visibility-range fade alpha-blends, so LOD switches stay hard (no translucent trunks).
	for i in 2:
		var mi := _mesh(plant, i)
		assert_eq(mi.visibility_range_fade_mode, GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED, "LOD%d hard" % i)
		assert_eq(mi.visibility_range_end_margin, 0.0, "LOD%d: the switch is its parent's, not its own end" % i)
	assert_eq(_mesh(plant, 1).visibility_range_begin_margin, 2.0, "the 45 m switch keeps its hysteresis")
	var last := _mesh(plant, 2)
	assert_eq(last.visibility_range_fade_mode, GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF)
	assert_eq(last.visibility_range_begin, 120.0)
	assert_eq(last.visibility_range_begin_margin, 2.0, "the faded LOD crossfades in over 118-122 m")
	assert_eq(last.visibility_range_end, 400.0)
	assert_eq(last.visibility_range_end_margin, 6.0, "fades out over the final cut")
	assert_eq(last.visibility_parent, NodePath(), "the last LOD has no parent")
	plant.free()


func test_each_lod_is_the_visibility_child_of_the_next() -> void:
	var plant := _plant_with_lods(3)
	plant.apply()
	for i in 2:
		var mi := _mesh(plant, i)
		assert_true(mi.get_node_or_null(mi.visibility_parent) == _mesh(plant, i + 1), "LOD%d -> LOD%d" % [i, i + 1])
	plant.force_lod = 1
	plant.apply()
	for i in 3:
		assert_eq(_mesh(plant, i).visibility_parent, NodePath(), "force_lod drops the chain")
	plant.free()


func test_chains_stay_within_their_base_name() -> void:
	var plant := VegetationPlant.new()
	for n: String in ["grass_a", "grass_a-lod1", "grass_b", "grass_b-lod1"]:
		var mi := MeshInstance3D.new()
		mi.name = n
		mi.mesh = QuadMesh.new()
		plant.add_child(mi)
	plant.lod_end_m = PackedFloat32Array([30.0, 60.0])
	plant.apply()
	for base: String in ["grass_a", "grass_b"]:
		var lod0 := plant.get_node(base) as MeshInstance3D
		assert_eq(lod0.get_node(lod0.visibility_parent).name, StringName(base + "-lod1"), base)
	plant.free()


func test_no_fade_keeps_the_hysteresis_on_every_cut() -> void:
	var plant := _plant_with_lods(2)
	plant.lod_end_m = PackedFloat32Array([45.0, 120.0])
	plant.lod_fade_m = 0.0
	plant.lod_margin_m = 2.0
	plant.apply()
	var l1 := _mesh(plant, 1)
	assert_eq(l1.visibility_range_fade_mode, GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED)
	assert_eq(l1.visibility_range_begin, 45.0)
	assert_eq(l1.visibility_range_begin_margin, 2.0)
	assert_eq(l1.visibility_range_end_margin, 2.0)
	plant.free()


## Godot 4.6's visibility-range check (RendererSceneCull::_visibility_range_check), as
## game/levels/_tests/vegetation/lod_sweep_probe.gd measured it under lavapipe. -1 too far, 1 too close,
## 0 drawn, 2 drawn while fading (it also hands the instance's visibility children through).
## FADE_DISABLED margins are hysteresis: they widen the range of an instance that was drawn last frame
## and narrow it for one that was not. `seen` holds each instance's last state.
static func _range_check(mi: MeshInstance3D, dist: float, seen: Dictionary) -> int:
	var begin_off := -mi.visibility_range_begin_margin
	var end_off := mi.visibility_range_end_margin
	var hard := mi.visibility_range_fade_mode == GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED
	if hard and not bool(seen.get(mi, false)):
		begin_off = -begin_off
		end_off = -end_off
	if mi.visibility_range_end > 0.0 and dist > mi.visibility_range_end + end_off:
		seen[mi] = false
		return -1
	if mi.visibility_range_begin > 0.0 and dist < mi.visibility_range_begin + begin_off:
		seen[mi] = false
		return 1
	seen[mi] = true
	if not hard:
		if mi.visibility_range_end > 0.0 and dist > mi.visibility_range_end - end_off:
			return 2
		if mi.visibility_range_begin > 0.0 and dist < mi.visibility_range_begin - begin_off:
			return 2
	return 0


## One culling pass at `dist`, parents first (Godot culls by dependency depth): per LOD, 0 hidden,
## 1 drawn opaque, 2 drawn fading. A child is culled unchecked unless its parent was too close or fading.
static func _draws(plant: VegetationPlant, lods: int, dist: float, seen: Dictionary) -> Array[int]:
	var drawn: Array[int] = []
	drawn.resize(lods)
	var result := {}
	for i in range(lods - 1, -1, -1):
		var mi := plant.get_node("frond-lod%d" % i) as MeshInstance3D
		var parent := mi.get_node_or_null(mi.visibility_parent) as MeshInstance3D
		if parent != null and not int(result[parent]) in [1, 2]:
			result[mi] = -1
			continue
		result[mi] = _range_check(mi, dist, seen)
		drawn[i] = {0: 1, 2: 2}.get(result[mi], 0)
	return drawn


## M1-ENV-08/09: from a still camera (fresh state), moving in and moving out, every distance draws
## exactly one LOD opaque, or crosses the faded last LOD in over the opaque LOD below it within
## lod_margin_m of that switch. No hole (the old 44-46 m and 118-120 m gaps), no double draw (the old
## 120-122 m band).
func test_a_distance_sweep_draws_exactly_one_lod() -> void:
	for fade: float in [6.0, 0.0]:
		var plant := _plant_with_lods(3)
		plant.lod_end_m = PackedFloat32Array([45.0, 120.0, 400.0])
		plant.lod_margin_m = 2.0
		plant.lod_fade_m = fade
		plant.apply()
		var dists: Array[float] = []
		var d := 0.5
		while d < 390.0:
			dists.append(d)
			d += 0.25
		var bad: Array[String] = []
		var reversed := dists.duplicate()
		reversed.reverse()
		for history: String in ["still", "in", "out"]:
			var seen := {}
			var sweep: Array[float] = reversed if history == "in" else dists
			for x: float in sweep:
				if history == "still":
					seen = {}
				var drawn := _draws(plant, 3, x, seen)
				var opaque := drawn.count(1)
				var fading := drawn.find(2)
				var crossfade := fading == 2 and drawn[1] == 1 and absf(x - 120.0) <= 2.0
				if opaque != 1 or (fading >= 0 and not crossfade):
					bad.append("%s %.2f m: %s" % [history, x, drawn])
		assert_eq(bad.size(), 0, "fade %.0f: %s" % [fade, ", ".join(bad.slice(0, 6))])
		plant.free()


func test_the_final_cut_draws_only_the_last_lod() -> void:
	var plant := _plant_with_lods(3)
	plant.apply()
	for x: float in [394.5, 400.0, 405.5]:
		var drawn := _draws(plant, 3, x, {})
		assert_eq(drawn, [0, 0, 2] as Array[int], "%.1f m fades the last LOD alone" % x)
	assert_eq(_draws(plant, 3, 406.5, {}), [0, 0, 0] as Array[int], "past the fade nothing draws")
	plant.free()


func test_lod_index_parses_the_suffix() -> void:
	assert_eq(VegetationPlant.lod_index("palm-lod2"), 2)
	assert_eq(VegetationPlant.lod_index("palm"), 0)
	assert_eq(VegetationPlant.lod_index("palm-lodx"), 0)


func test_shelter_reaches_every_mesh_and_probes_from_the_crown() -> void:
	var plant := _plant_with_lods(2)
	plant.shelter = VegetationPlant.Shelter.SHELTERED
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(plant)
	plant.set_shelter(1.0)
	for i in 2:
		assert_eq(_mesh(plant, i).get_instance_shader_parameter(VegetationPlant.SHELTER_PARAM), 1.0)
	assert_between(plant.crown_height(), 2.0 - 1e-3, 2.0 + 1e-3, "a 2 m quad centred at 1 m tops out at 2 m")
	plant.free()


func test_foliage_tiers_declare_the_shelter_uniform() -> void:
	for path in FOLIAGE_SHADERS:
		var src := FileAccess.get_file_as_string(path)
		var body := FileAccess.get_file_as_string("res://game/shaders/vegetation/vegetation_foliage_body.gdshaderinc")
		assert_true(src.contains("vegetation_foliage_body.gdshaderinc"), "%s includes the body" % path)
		assert_true(body.contains("instance uniform float inst_translucency_shelter"), "body declares the shelter")
		assert_true((load(path) as Shader).get_mode() == Shader.MODE_SPATIAL, "%s compiles" % path)


## A 10 x 1 x 10 m box roof on `layer`, its underside `height` m above the origin.
func _roof(layer: int, height: float) -> StaticBody3D:
	var roof := StaticBody3D.new()
	roof.collision_layer = layer
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(10.0, 1.0, 10.0)
	shape.shape = box
	roof.add_child(shape)
	roof.position = Vector3(0.0, height + 0.5, 0.0)
	return roof


func test_auto_shelter_probes_toward_the_global_sun_on_the_mask() -> void:
	var root := (Engine.get_main_loop() as SceneTree).current_scene
	var world := Node3D.new()
	root.add_child(world)
	var plant := _plant_with_lods(1)
	plant.shelter = VegetationPlant.Shelter.OPEN
	world.add_child(plant)
	var roof := _roof(1, 5.0)
	world.add_child(roof)
	var before: Variant = ShaderGlobals.get_value(&"hymn_sun_direction")
	ShaderGlobals.set_value(&"hymn_sun_direction", Vector3.UP)
	assert_eq(plant.sun_direction(), Vector3.UP, "reads the global sun")
	assert_true(plant.is_sheltered(), "a roof over the crown, toward the sun, shelters")
	plant.shelter_mask = 2
	assert_false(plant.is_sheltered(), "a roof off the probe's mask does not")
	plant.shelter_mask = 1
	ShaderGlobals.set_value(&"hymn_sun_direction", Vector3(1.0, 0.2, 0.0).normalized())
	assert_false(plant.is_sheltered(), "a low sun from the side passes under the roof")
	ShaderGlobals.set_value(&"hymn_sun_direction", before)
	world.free()


## M1-ENV-09: AUTO plants listen for a new sun and re-probe on the next physics frame.
func test_auto_shelter_reprobes_when_the_sun_moves() -> void:
	var tree := Engine.get_main_loop() as SceneTree
	var world := Node3D.new()
	tree.current_scene.add_child(world)
	world.add_child(_roof(1, 5.0))
	var before: Variant = ShaderGlobals.get_value(&"hymn_sun_direction")
	ShaderGlobals.set_value(&"hymn_sun_direction", Vector3(1.0, 0.2, 0.0).normalized())
	var plant := _plant_with_lods(1)
	world.add_child(plant)
	assert_true(plant.is_in_group(ShaderGlobals.LISTENERS_GROUP), "AUTO listens for the sun")
	assert_true(tree.physics_frame.is_connected(plant.probe_shelter), "and probes once placed")
	plant.probe_shelter()
	assert_eq(_mesh(plant, 0).get_instance_shader_parameter(VegetationPlant.SHELTER_PARAM), 0.0, "a low sun: open")
	tree.physics_frame.disconnect(plant.probe_shelter)
	ShaderGlobals.set_value(&"hymn_sun_direction", Vector3(1.0, 0.2, 0.001).normalized())
	assert_false(tree.physics_frame.is_connected(plant.probe_shelter), "a sub-degree nudge does not re-probe")
	ShaderGlobals.set_value(&"hymn_sun_direction", Vector3.UP)
	assert_true(tree.physics_frame.is_connected(plant.probe_shelter), "the noon sun re-probes")
	ShaderGlobals.set_value(&"hymn_sun_direction", Vector3(0.0, 1.0, 0.1).normalized())
	plant.probe_shelter()
	assert_eq(_mesh(plant, 0).get_instance_shader_parameter(VegetationPlant.SHELTER_PARAM), 1.0, "under the roof")
	ShaderGlobals.set_value(&"hymn_sun_direction", before)
	world.free()


## M1-ENV-09: a scene that restores the sun through ShaderGlobals.reset leaves no stale copy, and an
## unwritten global reads its project.godot default.
func test_shader_globals_reset_restores_the_project_default() -> void:
	var before: Variant = ShaderGlobals.get_value(&"hymn_sun_direction")
	var declared: Variant = (ProjectSettings.get_setting("shader_globals/hymn_sun_direction") as Dictionary)["value"]
	assert_eq(ShaderGlobals.default_value(&"hymn_sun_direction"), declared)
	ShaderGlobals.set_value(&"hymn_sun_direction", Vector3(0.0, 0.5, 0.5).normalized())
	ShaderGlobals.reset(&"hymn_sun_direction")
	assert_eq(ShaderGlobals.get_value(&"hymn_sun_direction"), declared, "reset reads back the default")
	assert_eq(ShaderGlobals.get_value(&"no_such_global", 7), 7, "an undeclared global falls back")
	assert_eq(ShaderGlobals.default_value(&"no_such_global"), null)
	ShaderGlobals.set_value(&"hymn_sun_direction", before)


func test_the_vegetation_test_scene_does_not_leave_its_sun_behind() -> void:
	var before: Variant = ShaderGlobals.get_value(&"hymn_sun_direction")
	var scene := (load("res://game/levels/_tests/vegetation/vegetation_test.tscn") as PackedScene).instantiate()
	var root := (Engine.get_main_loop() as SceneTree).current_scene
	root.add_child(scene)
	var pinned: Variant = ShaderGlobals.get_value(&"hymn_sun_direction")
	assert_true((pinned as Vector3).y < 0.999, "the scene pins its low sun %s" % [pinned])
	root.remove_child(scene)
	scene.free()
	assert_eq(ShaderGlobals.get_value(&"hymn_sun_direction"), ShaderGlobals.default_value(&"hymn_sun_direction"))
	ShaderGlobals.set_value(&"hymn_sun_direction", before)
