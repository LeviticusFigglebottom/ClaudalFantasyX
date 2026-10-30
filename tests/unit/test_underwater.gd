extends TestCase
## M2-RND-02: the underwater look. Its shaders compile, its data names palette swatches and a quality row
## for every preset's tier, the rig builds every part and follows the tier (the Low fallback drops the
## waves, the god rays and the snow), switches off whole, and authors volumetric fog only where it is
## wanted. M2-RND-09 (Art's fixes): the lagoon swatches and a per-look deep, night sea-glow in the column,
## the lantern's own warm halo, glimmer path compensation for a camera underwater, and a waterline camera.

const PALETTE := "res://docs/kb/art/palette.json"
const SHADERS := {
	"res://game/shaders/water/underwater_post_mul.gdshader":
	["sigma", "water_rest_y", "use_waves", "lens_m", "meniscus_px"],
	"res://game/shaders/water/underwater_post_add.gdshader":
	[
		"col_scatter",
		"col_deep",
		"camera_light_weight",
		"col_sea_glow",
		"sea_glow_energy",
		"lamp_color",
		"lamp_absorption"
	],
	"res://game/shaders/water/water_underside.gdshader":
	["col_window", "col_tir", "ior", "sun_disc", "tir_gain", "lens_m", "sea_glow_energy"],
	"res://game/shaders/glimmer/glimmer_motes_draw.gdshader":
	["uw_comp_lift", "uw_comp_held", "uw_sigma", "uw_max_gain"],
	"res://game/shaders/water/underwater_shafts.gdshader": ["density", "shaft_scale_m", "water_rest_y"],
}


class ShaderErrorLog:
	extends Logger
	var count := 0
	var _mutex := Mutex.new()

	func _log_error(
		_function: String,
		_file: String,
		_line: int,
		code: String,
		rationale: String,
		_editor_notify: bool,
		error_type: int,
		_script_backtraces: Array[ScriptBacktrace]
	) -> void:
		var text := "%s %s" % [code, rationale]
		if error_type == Logger.ERROR_TYPE_SHADER or text.contains("Shader compilation failed"):
			_mutex.lock()
			count += 1
			_mutex.unlock()


func test_shaders_compile() -> void:
	var shader_log := ShaderErrorLog.new()
	OS.add_logger(shader_log)
	for path: String in SHADERS:
		var sh := load(path) as Shader
		var names: Array = sh.get_shader_uniform_list().map(func(u: Dictionary) -> String: return str(u["name"]))
		assert_true(names.size() > 0, "%s compiled to no uniforms (shader error?)" % path)
		for u: String in SHADERS[path]:
			assert_true(names.has(u), "%s lacks %s" % [path.get_file(), u])
	OS.remove_logger(shader_log)
	assert_eq(shader_log.count, 0, "shader compiler errors")


func test_data_colours_are_palette_swatches_and_every_preset_has_a_row() -> void:
	var data := UnderwaterRig.load_data()
	var swatches := (JSON.parse_string(FileAccess.get_file_as_string(PALETTE)) as Dictionary)["swatches"] as Dictionary
	var colors := data["colors"] as Dictionary
	var names := data["swatches"] as Dictionary
	for key: String in colors:
		assert_true(names.has(key), "colors.%s names its swatch" % key)
		assert_eq(str(colors[key]).to_upper(), str((swatches[names[key]] as Dictionary)["hex"]).to_upper(), key)
	var quality := data["quality"] as Dictionary
	for preset in GraphicsSettings.new().preset_ids():
		var tier := GraphicsSettings.preset_tier(preset, "underwater")
		assert_ne(tier, "", "%s has an underwater tier" % preset)
		assert_true(quality.has(tier), "%s -> %s is a quality row" % [preset, tier])
	assert_false(bool((quality["low"] as Dictionary)["god_rays"]), "Low: no volumetric god rays")
	assert_eq(str((quality["low"] as Dictionary)["post"]), UnderwaterRig.POST_SIMPLE, "Low: the simple post")
	var optics := data["optics"] as Dictionary
	assert_between(rad_to_deg(asin(1.0 / float(optics["ior"]))), 48.0, 49.0, "a 48.6 degree Snell window")


func test_rig_builds_every_part_and_follows_the_tier() -> void:
	var host := _scene()
	var rig := host.get_node("Rig") as UnderwaterRig
	assert_true(rig.post_mul != null and rig.post_add != null, "both post passes")
	assert_eq(rig.post_mul_material.render_priority, UnderwaterRig.PRIORITY_MUL)
	assert_true(rig.post_add_material.render_priority > rig.post_mul_material.render_priority, "multiply, then add")
	assert_true(rig.lantern != null and rig.lantern.get_parent() == host.get_node("Lamp"), "the lantern on its target")
	assert_true(rig.fog != null and rig.snow != null and rig.underside != null)
	assert_true(rig.set_quality("high"))
	assert_true(rig.fog.visible, "High: god rays")
	assert_true(bool(rig.post_mul_material.get_shader_parameter(&"use_waves")))
	assert_true(rig.lantern.shadow_enabled)
	assert_true(rig.set_quality("low"))
	assert_false(rig.fog.visible, "Low: no god rays")
	assert_false(bool(rig.post_mul_material.get_shader_parameter(&"use_waves")), "Low: a flat surface")
	assert_false(rig.snow.emitting, "Low: no snow")
	assert_false(rig.lantern.shadow_enabled)
	assert_false(rig.set_quality("nonsense"), "an unknown preset changes nothing")
	assert_eq(rig.get_quality(), "low")
	host.free()


## The lantern's bounce-pass refresh is deferred through the rig (the Lead, 10-29: underwater_rig.gd:401 handed a freed
## root to a deferred static call 2-12 times a run). A rig freed before the flush drops the call; a rig out of any scene
## refreshes nothing.
func test_the_lantern_s_bounce_refresh_is_bound_to_the_rig() -> void:
	var host := _scene()
	var rig := host.get_node("Rig") as UnderwaterRig
	rig.call(&"_refresh_bounce_passes")  # in its scene: refreshes under the scene root
	var call := Callable(rig, &"_refresh_bounce_passes")
	host.free()  # the zone left before the deferred call ran
	assert_false(call.is_valid(), "the queued call dies with the rig, so the flush skips it")
	var orphan := UnderwaterRig.new()
	orphan.call(&"_refresh_bounce_passes")  # no scene root: nothing to refresh, no error
	orphan.free()


func test_rig_switches_off_whole_and_authors_fog_only_for_god_rays() -> void:
	var host := _scene()
	var rig := host.get_node("Rig") as UnderwaterRig
	var env := (host.get_node("Env") as WorldEnvironment).environment
	rig.set_quality("high")
	assert_true(env.volumetric_fog_enabled, "High: the rig authors fog for its shafts")
	assert_eq(env.volumetric_fog_density, 0.0, "with no global density: only the shafts show")
	rig.set_quality("medium")
	assert_false(env.volumetric_fog_enabled, "Medium has no god rays, so no fog pass")
	rig.set_quality("high")
	rig.active = false
	for part: Node3D in [rig.post_mul, rig.post_add, rig.underside, rig.fog, rig.lantern]:
		assert_false(part.visible, "%s off" % part.name)
	assert_false(env.volumetric_fog_enabled)
	host.free()


func test_graphics_runtime_sets_the_rig_tier() -> void:
	var host := _scene()
	var rig := host.get_node("Rig") as UnderwaterRig
	rig.set_quality("high")
	assert_true(GraphicsRuntime.apply_system_tiers(host, "low") >= 1)
	assert_eq(rig.get_quality(), "low")
	host.free()


func test_art_swatches_and_the_night_sea_look() -> void:
	var data := UnderwaterRig.load_data()
	var swatches := (JSON.parse_string(FileAccess.get_file_as_string(PALETTE)) as Dictionary)["swatches"] as Dictionary
	var names := data["swatches"] as Dictionary
	for key: String in ["scatter", "transmit"]:
		assert_eq(str(names[key]), "lagoon_teal", "%s is the lagoon's water (M2-ART-02)" % key)
	for key: String in ["deep", "tir"]:
		assert_eq(str(names[key]), "deep_teal_shadow", "%s: deep_teal_shadow, not sea_glow by day" % key)
	var night := (data["looks"] as Dictionary)["night_sea"] as Dictionary
	assert_eq(str((night["swatches"] as Dictionary)["deep"]), "abyss_navy")
	assert_eq(str(night["deep"]).to_upper(), str((swatches["abyss_navy"] as Dictionary)["hex"]).to_upper())
	var host := _scene()
	var rig := host.get_node("Rig") as UnderwaterRig
	var teal := Color(str((swatches["deep_teal_shadow"] as Dictionary)["hex"]))
	var navy := Color(str((swatches["abyss_navy"] as Dictionary)["hex"]))
	assert_true(
		(rig.post_add_material.get_shader_parameter(&"col_deep") as Color).is_equal_approx(teal), "Act I default"
	)
	rig.look = "night_sea"
	assert_true((rig.post_add_material.get_shader_parameter(&"col_deep") as Color).is_equal_approx(navy), "night_sea")
	rig.look = ""
	assert_true((rig.post_mul_material.get_shader_parameter(&"col_deep") as Color).is_equal_approx(teal))
	host.free()


func test_night_sea_glow_and_the_lamp_halo_follow_the_scene() -> void:
	var host := _scene()
	var rig := host.get_node("Rig") as UnderwaterRig
	var water := host.get_node("Water") as WaterSurface
	water.sea_glow_energy = 0.1
	rig._process(0.0)
	var strength := float((UnderwaterRig.load_data()["optics"] as Dictionary)["sea_glow_strength"])
	assert_between(
		float(rig.post_add_material.get_shader_parameter(&"sea_glow_energy")),
		0.1 * strength - 1e-5,
		0.1 * strength + 1e-5
	)
	assert_between(
		float(rig.underside_material.get_shader_parameter(&"sea_glow_energy")),
		0.1 * strength - 1e-5,
		0.1 * strength + 1e-5
	)
	var lamp := rig.post_add_material.get_shader_parameter(&"lamp_color") as Vector3
	assert_true(lamp.x > lamp.y and lamp.y > lamp.z, "the halo is the oil lamp's warm light")
	assert_true(
		(rig.post_add_material.get_shader_parameter(&"lamp_pos") as Vector3).is_equal_approx(
			rig.lantern.global_position
		)
	)
	assert_eq(rig.lantern.light_volumetric_fog_energy, 0.0, "no second, fog-absorbed halo")
	rig.active = false
	rig._process(0.0)
	assert_eq(rig.post_add_material.get_shader_parameter(&"lamp_color") as Vector3, Vector3.ZERO, "off with the rig")
	host.free()


func test_glimmer_seen_from_underwater_gets_its_path_back() -> void:
	var host := _scene()
	var rig := host.get_node("Rig") as UnderwaterRig
	var field := GlimmerField.new()
	field.name = "Motes"
	field.position = Vector3(0.0, -4.0, -6.0)
	host.add_child(field)
	var cam := Camera3D.new()
	host.add_child(cam)
	cam.global_position = Vector3(0.0, -3.0, 0.0)
	cam.make_current()
	rig._process(0.0)
	var g := UnderwaterRig.load_data()["glimmer"] as Dictionary
	var dm := field.draw_material
	assert_between(
		float(dm.get_shader_parameter(&"uw_comp_lift")),
		float(g["lift"]) - 1e-5,
		float(g["lift"]) + 1e-5,
		"released: full"
	)
	assert_between(
		float(dm.get_shader_parameter(&"uw_comp_held")),
		float(g["held"]) - 1e-5,
		float(g["held"]) + 1e-5,
		"held: partial"
	)
	assert_eq(
		float(field.process_material.get_shader_parameter(&"underwater_absorb_per_m")), 0.0, "the post absorbs, once"
	)
	field.underwater_compensation = 0.0
	rig._process(0.0)
	assert_eq(float(dm.get_shader_parameter(&"uw_comp_lift")), 0.0, "a field opts out")
	assert_true(
		float(field.process_material.get_shader_parameter(&"underwater_absorb_per_m")) > 0.0,
		"an opted-out field fades by its own absorption again"
	)
	field.underwater_compensation = 1.0
	cam.global_position = Vector3(0.0, 3.0, 0.0)
	rig._process(0.0)
	assert_true(
		float(field.process_material.get_shader_parameter(&"underwater_absorb_per_m")) > 0.0,
		"camera above water: the field's own sinking model (Ch2)"
	)
	host.free()


## A water, an environment, a lamp and the rig, in the tree (the rig builds in _ready).
func _scene() -> Node3D:
	var host := Node3D.new()
	var env := WorldEnvironment.new()
	env.name = "Env"
	env.environment = Environment.new()
	host.add_child(env)
	var water := WaterSurface.new()
	water.name = "Water"
	host.add_child(water)
	var lamp := Node3D.new()
	lamp.name = "Lamp"
	host.add_child(lamp)
	var rig := UnderwaterRig.new()
	rig.name = "Rig"
	rig.water = water
	rig.lantern_target = lamp
	host.add_child(rig)
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(host)
	return host
