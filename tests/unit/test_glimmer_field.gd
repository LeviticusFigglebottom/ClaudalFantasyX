extends TestCase
## M1-RND-02: GlimmerField (data, quality tiers, attractors, uniform packing, node build) and the
## glimmer shaders (compile checks, every pushed parameter exists, include constants vs palette).

const PALETTE := "res://docs/kb/art/palette.json"
const PROCESS_SHADER := "res://game/shaders/glimmer/glimmer_motes_process.gdshader"
const DRAW_SHADER := "res://game/shaders/glimmer/glimmer_motes_draw.gdshader"
const REFLECT_SHADER := "res://game/shaders/glimmer/glimmer_motes_reflect.gdshader"
const SEA_GLOW_SHADER := "res://game/shaders/glimmer/glimmer_sea_glow_overlay.gdshader"
const GLIMMER_INC := "res://game/shaders/include/glimmer.gdshaderinc"
const GLOBALS_INC := "res://game/shaders/include/globals.gdshaderinc"
const PRESET_IDS: Array[String] = ["low", "medium", "high", "ultra"]
const EPS := 1e-4
const LINEAR_TOL := 0.002

var cfg: Dictionary
var _nodes: Array[Node] = []


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


func before_each() -> void:
	cfg = GlimmerField.load_config()


# --- Data: the meaning rules (color_script.md narrative light rules 1-2) -----------------------


func test_colours_match_the_palette() -> void:
	var swatches := _json(PALETTE)["swatches"] as Dictionary
	var colors := cfg["colors"] as Dictionary
	var mapping := {
		"released": "glimmer_lift", "released_hi": "glimmer_lift_hi", "held": "glimmer_held", "machine": "glimmer_bound"
	}
	for key: String in mapping:
		var swatch := swatches[mapping[key]] as Dictionary
		assert_eq(str(colors[key]).to_upper(), str(swatch["hex"]).to_upper(), "colour %s" % key)


func test_motion_ranges_follow_the_colour_script() -> void:
	assert_eq(float(cfg["release_duration_s"]), 1.5, "rule 1: 1.5 s release lerp")
	var rel := (cfg["modes"] as Dictionary)["released"] as Dictionary
	var held := (cfg["modes"] as Dictionary)["held"] as Dictionary
	assert_between(float(rel["rise_min_mps"]), 0.15, 0.4)
	assert_between(float(rel["rise_max_mps"]), 0.15, 0.4)
	assert_between(float(rel["spiral_radius_min_m"]), 0.2, 0.6)
	assert_between(float(rel["spiral_radius_max_m"]), 0.2, 0.6)
	assert_between(float(held["drift_min_mps"]), 0.05, 0.2)
	assert_between(float(held["drift_max_mps"]), 0.05, 0.2)
	assert_between(float(held["down_bias_min_deg"]), 15.0, 30.0)
	assert_between(float(held["down_bias_max_deg"]), 15.0, 30.0)


func test_quality_tiers_match_presets_and_never_remove_the_motes() -> void:
	var tiers := cfg["quality"] as Dictionary
	assert_eq(tiers.keys().size(), PRESET_IDS.size())
	var presets := GraphicsSettings.new().preset_ids()
	var last := 0
	for id in PRESET_IDS:
		assert_true(tiers.has(id), "tier %s" % id)
		assert_true(presets.has(id), "GraphicsSettings preset %s" % id)
		var f := GlimmerField.new()
		assert_true(f.set_quality(id))
		var n := f.planned_amount()
		assert_true(n > last, "tier %s has more motes than the one below" % id)
		assert_true(float((tiers[id] as Dictionary)["amount_scale"]) > 0.0, "tier %s keeps the effect" % id)
		last = n
		f.free()
	assert_true(tiers.has(str(cfg["default_quality"])))


func test_unknown_quality_is_rejected() -> void:
	var f := GlimmerField.new()
	assert_true(f.set_quality("low"))
	assert_false(f.set_quality("cinematic"))
	assert_eq(f.get_quality(), "low")
	f.free()
	_cleanup()


func test_low_tier_drops_trails_and_reflection_but_keeps_motes() -> void:
	var f := GlimmerField.new()
	f.still_water_reflection = true
	f.set_quality("low")
	assert_eq(float(f.draw_parameters()["trail_scale"]), 0.0)
	assert_false(f.reflection_active())
	assert_true(f.planned_amount() >= 1)
	f.set_quality("high")
	assert_true(f.reflection_active())
	f.still_water_reflection = false
	assert_false(f.reflection_active(), "reflection only for still water")
	f.free()
	_cleanup()


# --- Attractors --------------------------------------------------------------------------------


func test_attractors_add_update_remove_and_fill_up() -> void:
	var f := GlimmerField.new()
	assert_false(f.add_attractor(null))
	var nodes: Array[Node3D] = []
	for i in f.max_attractors():
		var n := _node3d(Vector3(i, 0, 0))
		nodes.append(n)
		assert_true(f.add_attractor(n))
	assert_eq(f.get_attractor_count(), f.max_attractors())
	assert_false(f.add_attractor(_node3d(Vector3.ZERO)), "full")
	assert_true(f.add_attractor(nodes[0], 0.5), "re-adding updates in place")
	assert_eq(f.get_attractor_count(), f.max_attractors())
	assert_true(f.remove_attractor(nodes[0]))
	assert_false(f.remove_attractor(nodes[0]))
	assert_eq(f.get_attractor_count(), f.max_attractors() - 1)
	f.clear_attractors()
	assert_eq(f.get_attractor_count(), 0)
	f.free()
	_cleanup()


func test_freed_attractors_are_dropped() -> void:
	var f := GlimmerField.new()
	var a := Node3D.new()
	var b := _node3d(Vector3.ONE)
	f.add_attractor(a)
	f.add_attractor(b)
	a.free()
	assert_eq(f.get_attractor_count(), 1)
	assert_eq(int(f.pack_attractors()["count"]), 1)
	f.free()
	_cleanup()


func test_pack_attractors_layout_and_defaults() -> void:
	var f := GlimmerField.new()
	var a := cfg["attractor"] as Dictionary
	var n := _node3d(Vector3(1.0, 2.0, 3.0))
	f.add_attractor(n, 0.5, 1.2, GlimmerField.USE_DEFAULT, 0.8)
	var m := _node3d(Vector3(-1.0, 0.0, 0.0))
	f.add_attractor(m)
	var packed := f.pack_attractors()
	assert_eq(int(packed["count"]), 2)
	var pr := packed["pos_radius"] as PackedVector4Array
	var params := packed["params"] as PackedVector4Array
	assert_eq(pr.size(), f.max_attractors(), "padded to the shader array length")
	assert_eq(params.size(), f.max_attractors())
	assert_eq(pr[0], Vector4(1.0, 2.0, 3.0, 1.2))
	var influence := float(a["influence_scale"])
	assert_eq(params[0], Vector4(0.5, float(a["default_swirl"]), 0.8, 1.2 * influence))
	var r := float(a["default_radius_m"])
	assert_eq(pr[1], Vector4(-1.0, 0.0, 0.0, r))
	assert_eq(params[1].x, float(a["default_strength"]))
	assert_eq(params[1].z, float(a["default_half_height_m"]))
	assert_eq(pr[2], Vector4.ZERO, "unused slots are zero")
	f.free()
	_cleanup()


func test_shader_attractor_array_matches_the_data() -> void:
	var src := FileAccess.get_file_as_string(PROCESS_SHADER)
	var re := RegEx.create_from_string("#define HYMN_GLIMMER_MAX_ATTRACTORS (\\d+)")
	var found := re.search(src)
	assert_true(found != null, "shader defines HYMN_GLIMMER_MAX_ATTRACTORS")
	if found:
		assert_eq(int(found.get_string(1)), int((cfg["attractor"] as Dictionary)["max"]))


# --- Node build and per-frame state ------------------------------------------------------------


func test_ready_builds_a_deterministic_emitter() -> void:
	var f := GlimmerField.new()
	f.use_fixed_seed = true
	f.fixed_seed = 42
	f.still_water_reflection = true
	f.quality = "medium"
	_host().add_child(f)
	_nodes.append(f)
	var motes := f.get_node_or_null(GlimmerField.MOTES_NODE_NAME) as GPUParticles3D
	assert_true(motes != null, "Motes child")
	if motes == null:
		return
	var emitter := cfg["emitter"] as Dictionary
	assert_eq(motes.amount, f.planned_amount())
	assert_true(motes.use_fixed_seed)
	assert_eq(motes.seed, 42)
	assert_eq(motes.preprocess, float(emitter["preprocess_s"]))
	assert_eq(motes.fixed_fps, int(emitter["fixed_fps"]))
	assert_eq(motes.lifetime, float(emitter["lifetime_s"]))
	assert_false(motes.local_coords, "world-space motes stay put when the field moves")
	assert_eq(motes.draw_passes, 2, "reflection pass on medium")
	assert_eq((motes.process_material as ShaderMaterial).shader.resource_path, PROCESS_SHADER)
	f.set_quality("low")
	assert_eq(motes.draw_passes, 1)
	assert_eq(motes.amount, f.planned_amount())
	assert_true(f.get_node_or_null(GlimmerField.LIGHT_NODE_NAME) == null, "no fill light by default")
	_cleanup()


func test_release_drives_the_shader_uniforms_over_time() -> void:
	var f := GlimmerField.new()
	var singer := _node3d(Vector3(2.0, 0.0, -1.0))
	_host().add_child(f)
	_nodes.append(f)
	var got: Array[String] = []
	f.mode_changed.connect(func(m: GlimmerState.Mode) -> void: got.append(GlimmerState.mode_name(m)))
	f.release_finished.connect(func() -> void: got.append("finished"))
	assert_true(f.release(GlimmerField.USE_DEFAULT, singer))
	assert_eq(f.get_mode(), GlimmerState.Mode.RELEASED)
	var duration := float(cfg["release_duration_s"])
	f._process(duration * 0.5)
	var dyn := f.dynamic_process_parameters()
	assert_between(float(dyn["transition_progress"]), 0.5 - EPS, 0.5 + EPS)
	assert_eq(dyn["blend_to"], 1.0)
	assert_eq(dyn["release_origin"], Vector3(2.0, 0.0, -1.0), "the wave starts at the singer")
	var mat := f.process_material
	assert_between(float(mat.get_shader_parameter("transition_progress")), 0.5 - EPS, 0.5 + EPS, "pushed")
	f._process(duration)
	assert_false(f.is_releasing())
	assert_eq(f.get_release_progress(), 1.0)
	assert_eq(got, ["released", "finished"] as Array[String])
	assert_false(f.release(), "already released")
	_cleanup()


func test_machine_mode_and_fill_light_colour() -> void:
	var f := GlimmerField.new()
	f.fill_light_energy = 0.5
	f.mode = GlimmerState.Mode.MACHINE
	_host().add_child(f)
	_nodes.append(f)
	assert_eq(f.get_mode(), GlimmerState.Mode.MACHINE, "export setter before _ready")
	var light := f.get_node_or_null(GlimmerField.LIGHT_NODE_NAME) as OmniLight3D
	assert_true(light != null, "fill light")
	if light != null:
		assert_eq(light.light_color, Color(str((cfg["colors"] as Dictionary)["machine"])))
	assert_eq(f.dynamic_process_parameters()["machine_to"], 1.0)
	_cleanup()


func test_static_parameters_follow_exports_and_config() -> void:
	var f := GlimmerField.new()
	f.emission_shape = GlimmerField.EmissionShape.DISC
	f.water_height_m = -0.5
	f.set_quality("ultra")
	var p := f.static_process_parameters()
	assert_eq(p["emission_shape"], 1)
	assert_eq(p["water_height_m"], -0.5)
	assert_eq(p["curl_octaves"], int(((cfg["quality"] as Dictionary)["ultra"] as Dictionary)["curl_octaves"]))
	assert_eq(p["col_held"], Color(str((cfg["colors"] as Dictionary)["held"])))
	assert_eq(f.reflect_parameters()["mirror_plane_y"], -0.5)
	f.free()
	_cleanup()


# --- Shaders -----------------------------------------------------------------------------------


func test_every_pushed_parameter_is_a_shader_uniform() -> void:
	var shader_log := ShaderErrorLog.new()
	OS.add_logger(shader_log)
	var f := GlimmerField.new()
	f.set_quality("high")
	var process_params := f.static_process_parameters()
	process_params.merge(f.dynamic_process_parameters())
	_assert_uniforms(PROCESS_SHADER, process_params.keys())
	_assert_uniforms(DRAW_SHADER, f.draw_parameters().keys())
	_assert_uniforms(REFLECT_SHADER, f.reflect_parameters().keys())
	_assert_uniforms(SEA_GLOW_SHADER, ["zone_energy", "column_m", "depth_bias_m"])
	f.free()
	_cleanup()
	OS.remove_logger(shader_log)
	assert_eq(shader_log.count, 0, "shader compiler reported errors")


func test_glimmer_include_compiles_with_and_without_globals() -> void:
	var shader_log := ShaderErrorLog.new()
	OS.add_logger(shader_log)
	var inc := '#include "%s"\n' % GLIMMER_INC
	var probe := "uniform float probe;\n"
	var sources: Array[String] = [
		(
			"shader_type spatial;\n"
			+ inc
			+ inc
			+ probe
			+ "void fragment() { EMISSION = hymn_sea_glow(vec3(probe), probe, hymn_sea_glow_energy(probe, 1.0), 2.0); }\n"
		),
		(
			"shader_type spatial;\n"
			+ '#include "%s"\n' % GLOBALS_INC
			+ inc
			+ probe
			+ "void fragment() { EMISSION = hymn_sea_glow_global(vec3(probe), 0.08, probe) + HYMN_GLIMMER_HELD; }\n"
		),
		"shader_type particles;\n" + inc + probe + "void process() { COLOR.rgb = HYMN_GLIMMER_LIFT * probe; }\n",
	]
	for src in sources:
		var sh := Shader.new()
		sh.code = src
		var names := sh.get_shader_uniform_list().map(func(u: Dictionary) -> String: return str(u["name"]))
		assert_true(names.has("probe"), "compile failed for:\n%s" % src)
	OS.remove_logger(shader_log)
	assert_eq(shader_log.count, 0, "shader compiler reported errors")


func test_include_constants_match_palette_and_sea_glow_rule() -> void:
	var src := FileAccess.get_file_as_string(GLIMMER_INC)
	var swatches := _json(PALETTE)["swatches"] as Dictionary
	var mapping := {
		"HYMN_GLIMMER_LIFT": "glimmer_lift",
		"HYMN_GLIMMER_LIFT_HI": "glimmer_lift_hi",
		"HYMN_GLIMMER_HELD": "glimmer_held",
		"HYMN_GLIMMER_BOUND": "glimmer_bound",
		"HYMN_SEA_GLOW_COLOR": "sea_glow",
	}
	for define: String in mapping:
		var re := RegEx.create_from_string("#define %s vec3\\(([^)]*)\\)" % define)
		var m := re.search(src)
		assert_true(m != null, "%s defined" % define)
		if m == null:
			continue
		var parts := m.get_string(1).split(",")
		var lin: Array = (swatches[mapping[define]] as Dictionary)["linear"]
		for i in 3:
			assert_between(
				float(parts[i]), float(lin[i]) - LINEAR_TOL, float(lin[i]) + LINEAR_TOL, "%s[%d]" % [define, i]
			)
	assert_true(src.contains("#define HYMN_SEA_GLOW_ENERGY_MIN 0.04"), "rule 3 floor")
	assert_true(src.contains("#define HYMN_SEA_GLOW_ENERGY_MAX 0.15"), "rule 3 ceiling")
	assert_true(src.contains("#define HYMN_SEA_GLOW_MOD_AMPLITUDE 0.25"), "rule 3 modulation")


# --- Helpers -----------------------------------------------------------------------------------


func _assert_uniforms(path: String, keys: Array) -> void:
	var sh := load(path) as Shader
	var names := sh.get_shader_uniform_list().map(func(u: Dictionary) -> String: return str(u["name"]))
	assert_true(names.size() > 0, "%s compiled" % path)
	for key: Variant in keys:
		assert_true(names.has(str(key)), "%s lacks uniform %s" % [path.get_file(), key])


func _node3d(pos: Vector3) -> Node3D:
	var n := Node3D.new()
	n.position = pos
	_nodes.append(n)
	return n


func _cleanup() -> void:
	for n in _nodes:
		if is_instance_valid(n):
			n.free()
	_nodes.clear()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _json(path: String) -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string(path)) as Dictionary
