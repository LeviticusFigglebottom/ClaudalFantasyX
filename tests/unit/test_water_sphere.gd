extends TestCase
## M3-RND-01: the Reefball water sphere. Its shaders declare what the rig sets, its data names palette swatches
## and a row for every preset, and the rig builds the surface, both full-screen passes and the god rays, and
## follows its tier (Low: no refraction, no god rays; caustics on every tier, M3-RND-04).

const PALETTE := "res://docs/kb/art/palette.json"
const SHADERS := {
	"res://game/shaders/water/sphere/water_sphere_surface.gdshader":
	["sphere_center", "sphere_radius_m", "ior", "refraction_strength", "use_refraction", "col_tir", "swell_m"],
	"res://game/shaders/water/sphere/water_sphere_post_mul.gdshader":
	[
		"sigma",
		"lens_m",
		"meniscus_px",
		"use_caustics",
		"sun_dir",
		"caustic_strength",
		"caustic_scale_per_m",
		"caustic_speed",
		"caustic_width",
		"caustic_blur_per_m",
		"caustic_fade_in_m",
		"caustic_falloff_m",
		"caustic_view_fade_m",
		"caustic_wall_soft_m",
	],
	"res://game/shaders/water/sphere/water_sphere_post_add.gdshader":
	["col_scatter", "col_deep", "light_level", "sea_glow_energy", "sea_glow_strength"],
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
	assert_true(bool(rig.post_mul_material.get_shader_parameter(&"use_caustics")), "High: caustics")
	for key in WaterSphereRig.CAUSTIC_KEYS:
		assert_eq(
			float(rig.post_mul_material.get_shader_parameter(StringName("caustic_" + key))),
			float((WaterSphereRig.load_data()["caustics"] as Dictionary)[key]),
			"caustic_%s from the data" % key
		)
	assert_true(env.environment.volumetric_fog_enabled, "the rig authors fog for its shafts")
	assert_true(rig.set_quality("low"))
	assert_false(rig.fog.visible, "Low: no god rays")
	assert_false(bool(rig.surface_material.get_shader_parameter(&"use_refraction")), "Low: no refraction")
	assert_true(bool(rig.post_mul_material.get_shader_parameter(&"use_caustics")), "Low keeps the caustics (no cost)")
	assert_false(rig.set_quality("nonsense"))
	rig._process(0.0)
	assert_true(
		(rig.post_add_material.get_shader_parameter(&"sphere_center") as Vector3).is_equal_approx(rig.global_position)
	)
	host.free()


## M3-RND-05: the night match. The ball's water column carries the sea-glow (colour script rule 3: >= 0.08 at
## night), the rig passes its own energy on, and the arena's lamps don't light the fog: a lamp's volumetric fog
## energy lit the god-ray FogVolume into bright green bands (as Rhen's lantern, tech/underwater.md).
func test_the_night_match_glows_and_its_lamps_leave_the_fog_alone() -> void:
	var scene := (load("res://game/levels/_tests/reefball/reefball_night_test.tscn") as PackedScene).instantiate()
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(scene)
	var rig := scene.get_node("Sphere") as WaterSphereRig
	assert_between(rig.sea_glow_energy, 0.08, 0.15, "rule 3: a night frame's sea-glow")
	assert_eq(float(rig.post_add_material.get_shader_parameter(&"sea_glow_energy")), rig.sea_glow_energy)
	assert_eq(
		float(rig.post_add_material.get_shader_parameter(&"sea_glow_strength")),
		float((WaterSphereRig.load_data()["optics"] as Dictionary)["sea_glow_strength"])
	)
	rig.sea_glow_energy = 0.1
	assert_eq(float(rig.post_add_material.get_shader_parameter(&"sea_glow_energy")), 0.1, "set at runtime too")
	var lamps := scene.get_node("Lamps").find_children("*", "Light3D", true, false)
	assert_true(lamps.size() > 0, "the arena is lamp-keyed")
	for l: Light3D in lamps:
		assert_eq(l.light_volumetric_fog_energy, 0.0, "%s leaves the ball's fog alone" % l.name)
	scene.free()


## M3-RND-26: the Tamsule Bell's held drop is the "tamsule_drop" profile: the contract's flattened spheroid
## (tamsule_bell.md §1, 14.0 x 11.5 m), perfectly still (no swell, a steady web), its colours palette swatches, its
## light thrown under it, and every pass flattened alike; the base ball stays as it was. Both Ch7 zones place it.
func test_the_tamsule_drop_profile() -> void:
	var base := WaterSphereRig.load_data()
	assert_eq(WaterSphereRig.profile_data(""), base, "no profile: the Reefball arena's ball")
	var row := (base["profiles"] as Dictionary)["tamsule_drop"] as Dictionary
	var swatches := (JSON.parse_string(FileAccess.get_file_as_string(PALETTE)) as Dictionary)["swatches"] as Dictionary
	for key: String in row["colors"]:
		var name := str((row["swatches"] as Dictionary)[key])
		assert_eq(str(row["colors"][key]).to_upper(), str((swatches[name] as Dictionary)["hex"]).to_upper(), key)
	var host := Node3D.new()
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	host.add_child(env)
	var rig := WaterSphereRig.new()
	rig.profile = "tamsule_drop"
	host.add_child(rig)
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(host)
	assert_eq(rig.radius_m(), 14.0)
	assert_eq(rig.semi_axis_y_m(), 11.5)
	var mesh := rig.surface.mesh as SphereMesh
	assert_between(mesh.height * 0.5 - rig.semi_axis_y_m(), 0.0, 0.5, "the mesh encloses the flattened drop")
	assert_true(rig.fog.size.is_equal_approx(Vector3(28.0, 23.0, 28.0)), "the shafts fill the drop")
	for m: ShaderMaterial in [rig.surface_material, rig.post_mul_material, rig.post_add_material]:
		assert_between(float(m.get_shader_parameter(&"sphere_flatten")), 11.5 / 14.0 - 1e-5, 11.5 / 14.0 + 1e-5)
	assert_eq(float(rig.surface_material.get_shader_parameter(&"swell_m")), 0.0, "still at rest")
	assert_eq(float(rig.post_mul_material.get_shader_parameter(&"caustic_speed")), 0.0, "a steady web")
	assert_true(float(rig.post_add_material.get_shader_parameter(&"under_strength")) > 0.0, "light under the drop")
	assert_eq(float(rig.post_add_material.get_shader_parameter(&"sea_glow_strength")), 0.0, "bound, not sea-glow")
	assert_true(float(rig.post_add_material.get_shader_parameter(&"bound_glow_energy")) > 0.0, "its bound light")
	host.free()
	for zone: String in ["tamsule_bell_galleries", "tamsule"]:
		var path := "res://game/levels/ch07/%s/%s_dressing.json" % [zone, zone]
		var drops := (JSON.parse_string(FileAccess.get_file_as_string(path)) as Dictionary).get("drops", []) as Array
		assert_eq(drops.size(), 1, "%s holds the drop" % zone)
		assert_eq(str((drops[0] as Dictionary)["profile"]), "tamsule_drop")
