extends TestCase
## M1-RND-03: the Undertow shaders compile headlessly (front end), every uniform UndertowStorm pushes
## exists in a storm shader, nothing reads TIME, constants agree with GDScript and the palette, and
## every shader is registered for prewarm.

const SHADER_DIR := "res://game/shaders/undertow"
const COMMON_INC := "res://game/shaders/undertow/undertow_common.gdshaderinc"
const PALETTE := "res://docs/kb/art/palette.json"
const PREWARM := "res://game/data/settings/prewarm_materials.json"
const PRESETS := "res://game/data/settings/graphics_presets.json"
## Uniforms every storm shader that includes undertow_common must expose.
const COMMON_UNIFORMS: Array[String] = [
	"storm_center", "storm_time_s", "storm_intensity", "rotation_rad_s", "wound_intensity", "lightning_sites"
]
const SHADER_UNIFORMS := {
	"undertow_body.gdshader":
	[
		"march_steps",
		"col_albedo",
		"erosion_contrast",
		"col_haze",
		"noise_tex",
		"noise_texels",
		"curl_reuse",
		"jitter_phase"
	],
	"undertow_body_medium.gdshader": ["march_steps", "empty_step", "noise_tex", "jitter_phase"],
	"undertow_body_ultra.gdshader": ["march_steps", "empty_step", "noise_tex", "curl_reuse", "jitter_phase"],
	"undertow_shell.gdshader": ["shell_kind", "shell_fraction", "alpha_cut"],
	"undertow_spray.gdshader": ["spray_radius_m", "spray_height_m"],
	"undertow_sea.gdshader": ["funnel_depth_m", "foam_octaves", "sea_glow_energy", "col_sea_deep"],
	"undertow_sea_lid.gdshader": ["lid_height_m"],
	"undertow_composite.gdshader": ["body_tex", "occluder_radius_m", "front_tex", "use_front"],
}
const LINEAR_TOL := 0.002


## Counts shader compiler errors reported through the engine log while a check runs.
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


func _shader_files() -> Array[String]:
	var out: Array[String] = []
	for f in DirAccess.get_files_at(SHADER_DIR):
		if f.ends_with(".gdshader"):
			out.append(SHADER_DIR.path_join(f))
	return out


func _uniform_names(path: String) -> Array:
	var sh := load(path) as Shader
	return sh.get_shader_uniform_list().map(func(u: Dictionary) -> String: return str(u["name"]))


func test_every_undertow_shader_compiles() -> void:
	var shader_log := ShaderErrorLog.new()
	OS.add_logger(shader_log)
	var files := _shader_files()
	assert_eq(files.size(), SHADER_UNIFORMS.size(), "one entry per shader: %s" % str(files))
	for path in files:
		var names := _uniform_names(path)
		assert_true(names.size() > 0, "%s compiled to no uniforms (shader error?)" % path)
		var file := path.get_file()
		assert_true(SHADER_UNIFORMS.has(file), "unexpected shader %s" % file)
		for u: String in SHADER_UNIFORMS.get(file, []):
			assert_true(names.has(u), "%s lacks uniform %s" % [file, u])
		# The lid writes depth only; the half-res composite only lays the body's texture down.
		if file not in ["undertow_sea_lid.gdshader", "undertow_composite.gdshader"]:
			for u in COMMON_UNIFORMS:
				assert_true(names.has(u), "%s lacks storm uniform %s" % [file, u])
	OS.remove_logger(shader_log)
	assert_eq(shader_log.count, 0, "shader compiler errors")


func test_every_pushed_parameter_exists_in_a_storm_shader() -> void:
	var all := {}
	for path in _shader_files():
		for n: String in _uniform_names(path):
			all[n] = true
	var state := UndertowState.new()
	var pushed := state.static_parameters()
	pushed.merge(state.dynamic_parameters())
	var storm := UndertowStorm.new()
	pushed.merge(storm.mood_parameters())
	storm.free()
	for key: String in pushed:
		assert_true(all.has(key), "pushed parameter %s has no uniform" % key)


func test_no_storm_shader_reads_time() -> void:
	var re := RegEx.create_from_string("\\bTIME\\b")
	var comment := RegEx.create_from_string("//[^\\n]*")
	for f in DirAccess.get_files_at(SHADER_DIR):
		if f.ends_with(".gdshader") or f.ends_with(".gdshaderinc"):
			var src := comment.sub(FileAccess.get_file_as_string(SHADER_DIR.path_join(f)), "", true)
			assert_true(re.search(src) == null, "%s reads TIME: drive it from storm_time_s" % f)


func test_constants_agree_with_gdscript_and_data() -> void:
	var src := FileAccess.get_file_as_string(COMMON_INC)
	assert_true(src.contains("#define UNDERTOW_MAX_FLASHES %d" % UndertowState.MAX_FLASHES), "flash count")
	assert_true(src.contains("#define UNDERTOW_AXIS_GUARD %s" % str(UndertowState.AXIS_GUARD)), "axis guard")
	var cfg := UndertowState.load_config()
	assert_true(int((cfg["lightning"] as Dictionary)["sites"]) <= UndertowState.MAX_FLASHES)
	var sea := FileAccess.get_file_as_string(SHADER_DIR.path_join("undertow_sea.gdshader"))
	assert_true(sea.contains("-funnel_depth_m / (1.0 + k * k)"), "sea profile matches UndertowState.sea_height")


## M1-RND-10: the baked noise lattice is a 3D texture of noise.texels per side, imported without
## mipmaps (they would blur the lattice), in a format that keeps 8 bits per channel.
func test_noise_lattice_matches_its_data() -> void:
	var noise := UndertowState.load_config()["noise"] as Dictionary
	var tex := load(str(noise["texture"])) as Texture3D
	assert_true(tex != null, "noise.texture loads as a Texture3D")
	var n := int(noise["texels"])
	assert_eq(tex.get_width(), n)
	assert_eq(tex.get_height(), n)
	assert_eq(tex.get_depth(), n)
	assert_false(tex.has_mipmaps(), "no mipmaps: the lattice must not be blurred")
	assert_eq(tex.get_format(), Image.FORMAT_RGBA8, "lossless RGBA8, not VRAM-compressed")


## M1-RND-09: every key of every undertow.json look is a uniform the raymarched body (and so the
## look) actually drives; colours parse.
func test_every_look_drives_body_uniforms() -> void:
	var s := UndertowState.new()
	assert_true(s.look_ids().has("day_storm"), "the daylight look exists")
	var body := _uniform_names(SHADER_DIR.path_join("undertow_body.gdshader"))
	for id in s.look_ids():
		var params := s.look_parameters(id)
		assert_true(params.size() > 0, "%s overrides something" % id)
		for key: String in params:
			assert_true(body.has(key), "%s.%s is a body uniform" % [id, key])
			if key.begins_with("col_"):
				assert_true(params[key] is Color and params[key] != Color.MAGENTA, "%s.%s parses" % [id, key])
	assert_eq(s.look_parameters("").size(), 0)
	assert_eq(s.look_parameters("nonsense").size(), 0)


func test_colours_match_the_palette() -> void:
	var pal := (JSON.parse_string(FileAccess.get_file_as_string(PALETTE)) as Dictionary)["swatches"] as Dictionary
	var colors := UndertowState.load_config()["colors"] as Dictionary
	var expect := {"wound": "spawn_wound", "held": "glimmer_held", "foam": "foam_white", "sea_deep": "abyss_navy"}
	for key: String in expect:
		var sw := pal[expect[key]] as Dictionary
		assert_eq(str(colors[key]).to_upper(), str(sw["hex"]).to_upper(), "%s = %s" % [key, expect[key]])
	var lin := (pal["spawn_wound"] as Dictionary)["linear"] as Array
	var src := FileAccess.get_file_as_string(COMMON_INC)
	var at := src.find("#define UNDERTOW_SPAWN_WOUND vec3(")
	assert_true(at >= 0)
	var nums := src.substr(at).get_slice("(", 1).get_slice(")", 0).split(",")
	for i in 3:
		assert_between(float(nums[i]), float(lin[i]) - LINEAR_TOL, float(lin[i]) + LINEAR_TOL)


func test_every_shader_is_registered_for_prewarm() -> void:
	var reg := JSON.parse_string(FileAccess.get_file_as_string(PREWARM)) as Dictionary
	var paths: Array[String] = []
	for e: Variant in reg["materials"]:
		paths.append(str((e as Dictionary)["path"]))
	for path in _shader_files():
		assert_true(paths.has(path), "%s not in prewarm_materials.json" % path)


func test_every_graphics_preset_has_a_storm_tier() -> void:
	var presets := JSON.parse_string(FileAccess.get_file_as_string(PRESETS)) as Dictionary
	var state := UndertowState.new()
	for p: Variant in presets["presets"]:
		var id := str((p as Dictionary)["id"])
		var plan := state.quality_plan(id)
		assert_eq(plan["tier"], id)
		if plan["body"] == UndertowState.BODY_RAYMARCH:
			assert_true(ResourceLoader.exists(str(plan["body_shader"])), "%s body shader" % id)
