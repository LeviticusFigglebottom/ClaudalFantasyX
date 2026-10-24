extends TestCase
## M3-RND-01: the Reefball water sphere. Its shaders declare what the rig sets, its data names palette swatches
## and a row for every preset, and the rig builds the surface, both full-screen passes and the god rays, and
## follows its tier (Low: no refraction, no god rays).

const PALETTE := "res://docs/kb/art/palette.json"
const SHADERS := {
	"res://game/shaders/water/sphere/water_sphere_surface.gdshader":
	["sphere_center", "sphere_radius_m", "ior", "refraction_strength", "use_refraction", "col_tir", "swell_m"],
	"res://game/shaders/water/sphere/water_sphere_post_mul.gdshader": ["sigma", "lens_m", "meniscus_px"],
	"res://game/shaders/water/sphere/water_sphere_post_add.gdshader": ["col_scatter", "col_deep", "light_level"],
}


func test_shaders_declare_what_the_rig_sets() -> void:
	for path: String in SHADERS:
		var sh := load(path) as Shader
		assert_true(sh != null, "%s loads" % path)
		var names := sh.get_shader_uniform_list().map(func(u: Dictionary) -> String: return str(u["name"]))
		for u: String in SHADERS[path]:
			assert_true(names.has(u), "%s declares %s" % [path.get_file(), u])


func test_data_colours_are_palette_swatches_and_every_preset_has_a_row() -> void:
	var data := WaterSphereRig.load_data()
	var swatches := (JSON.parse_string(FileAccess.get_file_as_string(PALETTE)) as Dictionary)["swatches"] as Dictionary
	var names := data["swatches"] as Dictionary
	for key: String in data["colors"]:
		assert_true(names.has(key), "colors.%s names its swatch" % key)
		var hexv := str((swatches[names[key]] as Dictionary)["hex"]).to_upper()
		assert_eq(str(data["colors"][key]).to_upper(), hexv, key)
	var quality := data["quality"] as Dictionary
	for preset in GraphicsSettings.new().preset_ids():
		assert_true(quality.has(preset), "%s has a sphere row" % preset)
	assert_false(bool((quality["low"] as Dictionary)["refraction"]), "Low: a tinted Fresnel shell")


func test_rig_builds_every_part_and_follows_the_tier() -> void:
	var host := Node3D.new()
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	host.add_child(env)
	var rig := WaterSphereRig.new()
	host.add_child(rig)
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(host)
	assert_true(rig.surface != null and rig.post_mul != null and rig.post_add != null and rig.fog != null)
	assert_eq(rig.post_mul_material.render_priority, WaterSphereRig.PRIORITY_MUL)
	assert_true(rig.post_add_material.render_priority > rig.post_mul_material.render_priority, "multiply, then add")
	# The mesh encloses the exact sphere the full-screen passes use (the swell and the facets' sag), by a little.
	var grown := (rig.surface.mesh as SphereMesh).radius - rig.radius_m()
	assert_between(grown, 0.0, 0.5, "the mesh's silhouette encloses the ball")
	assert_true(rig.set_quality("high"))
	assert_true(rig.fog.visible, "High: god rays")
	assert_true(bool(rig.surface_material.get_shader_parameter(&"use_refraction")))
	assert_true(env.environment.volumetric_fog_enabled, "the rig authors fog for its shafts")
	assert_true(rig.set_quality("low"))
	assert_false(rig.fog.visible, "Low: no god rays")
	assert_false(bool(rig.surface_material.get_shader_parameter(&"use_refraction")), "Low: no refraction")
	assert_false(rig.set_quality("nonsense"))
	rig._process(0.0)
	assert_true(
		(rig.post_add_material.get_shader_parameter(&"sphere_center") as Vector3).is_equal_approx(rig.global_position)
	)
	host.free()
