extends TestCase
## M2-RND-02: the underwater look. Its shaders compile, its data names palette swatches and a quality row
## for every preset's tier, the rig builds every part and follows the tier (the Low fallback drops the
## waves, the god rays and the snow), switches off whole, and authors volumetric fog only where it is
## wanted.

const PALETTE := "res://docs/kb/art/palette.json"
const SHADERS := {
	"res://game/shaders/water/underwater_post_mul.gdshader": ["sigma", "water_rest_y", "use_waves", "lens_m"],
	"res://game/shaders/water/underwater_post_add.gdshader": ["col_scatter", "col_deep", "camera_light_weight"],
	"res://game/shaders/water/water_underside.gdshader": ["col_window", "col_tir", "ior", "sun_disc"],
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
