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


func test_lod_switches_cross_fade() -> void:
	var plant := _plant_with_lods(3)
	plant.lod_end_m = PackedFloat32Array([45.0, 120.0, 400.0])
	plant.lod_fade_m = 6.0
	plant.apply()
	var l0 := _mesh(plant, 0)
	var l1 := _mesh(plant, 1)
	assert_eq(l0.visibility_range_fade_mode, GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF)
	assert_eq(l0.visibility_range_end, 45.0)
	assert_eq(l0.visibility_range_end_margin, 6.0)
	# The incoming LOD fades in over [begin - margin, begin] = [45, 51], the outgoing out over [45, 51].
	assert_eq(l1.visibility_range_begin, 51.0)
	assert_eq(l1.visibility_range_begin - l1.visibility_range_begin_margin, l0.visibility_range_end, "fades overlap")
	plant.free()


func test_hard_switch_keeps_the_old_hysteresis() -> void:
	var plant := _plant_with_lods(2)
	plant.lod_end_m = PackedFloat32Array([45.0, 120.0])
	plant.lod_fade_m = 0.0
	plant.lod_margin_m = 2.0
	plant.apply()
	var l1 := _mesh(plant, 1)
	assert_eq(l1.visibility_range_fade_mode, GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED)
	assert_eq(l1.visibility_range_begin, 45.0)
	assert_eq(l1.visibility_range_begin_margin, 2.0)
	plant.free()


func test_lod_index_parses_the_suffix() -> void:
	assert_eq(VegetationPlant.lod_index("palm-lod2"), 2)
	assert_eq(VegetationPlant.lod_index("palm"), 0)
	assert_eq(VegetationPlant.lod_index("palm-lodx"), 0)


func test_shelter_reaches_every_mesh_and_probes_from_the_crown() -> void:
	var plant := _plant_with_lods(2)
	plant.shelter = 1.0
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
