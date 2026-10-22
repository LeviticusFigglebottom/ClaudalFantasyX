extends TestCase
## M1-RND-06: shader-prewarm registry, lifecycle (completes, reports timing, frees), the
## SceneRouter hook, and a headless compile check of game/shaders/include/*.gdshaderinc.

const TEST_MATERIAL := "res://game/shaders/test/prewarm_test_material.tres"
const TEST_SHADER := "res://game/shaders/test/prewarm_test.gdshader"
const COMMON_INC := "res://game/shaders/include/common.gdshaderinc"
const GLOBALS_INC := "res://game/shaders/include/globals.gdshaderinc"
const TMP_DIR := "user://test_shader_prewarm"
const STATIC_STAGE_NODES := 4


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


# --- Registry ----------------------------------------------------------------------------------


func test_registry_parses_and_every_path_exists() -> void:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(ShaderPrewarm.REGISTRY_PATH))
	assert_eq(typeof(parsed), TYPE_DICTIONARY)
	var reg := parsed as Dictionary
	for key in ["frames_to_render", "measure_frames", "hitch_budget_ms", "viewport_width", "viewport_height"]:
		assert_true(reg.has(key), "registry lacks %s" % key)
	assert_true(int(reg["measure_frames"]) >= int(reg["frames_to_render"]))
	assert_between(float(reg["hitch_budget_ms"]), 1.0, 50.0, "SPEC §4.2 caps hitches at 50 ms")
	var paths: Array[String] = []
	for entry: Variant in reg["materials"]:
		paths.append(str((entry as Dictionary)["path"]))
	assert_true(paths.has(TEST_MATERIAL))
	for p in paths:
		assert_true(ResourceLoader.exists(p), "registered material missing: %s" % p)


# --- Lifecycle ---------------------------------------------------------------------------------


func test_prewarm_completes_reports_timing_and_frees() -> void:
	var node := ShaderPrewarm.spawn("res://some/battle.tscn", _host())
	var got: Array[Dictionary] = []
	node.finished.connect(func(s: Dictionary) -> void: got.append(s))
	assert_true(node.is_running())
	assert_eq(node.stage_node_count(), 1, "one quad for the test material")
	var stage := node.get_node("Viewport/Stage3D")
	assert_eq(stage.get_child_count(), STATIC_STAGE_NODES + 1)
	var frames := int(node.config["measure_frames"])
	var to_render := int(node.config["frames_to_render"])
	for i in to_render:
		node.tick(8.0)
	assert_eq(node.stage_node_count(), 0, "stage freed after frames_to_render")
	assert_eq(stage.get_child_count(), STATIC_STAGE_NODES)
	assert_true(node.is_running(), "keeps measuring the rest of the transition")
	node.tick(61.0)
	for i in frames - to_render - 1:
		node.tick(4.0)
	assert_false(node.is_running())
	assert_true(node.is_queued_for_deletion(), "frees itself when done")
	assert_eq(got.size(), 1)
	var s := got[0]
	assert_eq(s["scene_path"], "res://some/battle.tscn")
	assert_eq(s["materials"], 1)
	assert_eq(s["frames"], frames)
	assert_eq(s["max_frame_ms"], 61.0)
	assert_eq(s["over_budget"], true)
	node.tick(100.0)
	assert_eq(got.size(), 1, "no stats after finishing")


func test_handles_every_material_kind_and_scene_filter() -> void:
	DirAccess.make_dir_recursive_absolute(TMP_DIR)
	var paths := {
		"particles": _save(ParticleProcessMaterial.new(), "particles.tres"),
		"canvas":
		_save(_shader_material("shader_type canvas_item;\nvoid fragment() { COLOR = vec4(1.0); }\n"), "c.tres"),
		"sky": _save(_shader_material("shader_type sky;\nvoid sky() { COLOR = vec3(0.2); }\n"), "sky.tres"),
		"fog": _save(_shader_material("shader_type fog;\nvoid fog() { DENSITY = 0.5; }\n"), "fog.tres"),
	}
	var reg := {
		"frames_to_render": 1,
		"measure_frames": 2,
		"hitch_budget_ms": 50.0,
		"viewport_width": 32,
		"viewport_height": 32,
		"quad_size": 1.0,
		"quad_distance": 1.5,
		"particle_amount": 1,
		"materials":
		[
			{"path": TEST_MATERIAL, "scenes": ["res://a.tscn"]},
			{"path": TEST_MATERIAL, "scenes": ["res://b.tscn"]},
			{"path": TEST_SHADER, "scenes": []},
			{"path": "res://does/not/exist.tres", "scenes": []},
		],
	}
	for k: String in paths:
		(reg["materials"] as Array).append({"path": paths[k], "scenes": []})
	var reg_path := TMP_DIR + "/registry.json"
	var f := FileAccess.open(reg_path, FileAccess.WRITE)
	f.store_string(JSON.stringify(reg))
	f.close()
	var node := (load(ShaderPrewarm.SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	node.registry_path = reg_path
	_host().add_child(node)
	assert_eq(node.start("res://a.tscn"), 6, "material + shader + particles + canvas + sky + fog")
	assert_eq(node.get_node("Viewport").size, Vector2i(32, 32))
	node.tick(5.0)
	node.tick(5.0)
	assert_eq(node.stats["materials"], 6)
	assert_eq(node.stats["skipped"], 1, "missing path skipped with a warning")
	assert_eq(node.stats["over_budget"], false)
	assert_true(node.is_queued_for_deletion())
	for file in DirAccess.get_files_at(TMP_DIR):
		DirAccess.remove_absolute(TMP_DIR + "/" + file)
	DirAccess.remove_absolute(TMP_DIR)


func test_install_hooks_scene_router_signal() -> void:
	var router: Node = SceneRouter
	assert_true(router.has_meta(ShaderPrewarm.HOOK_META), "SceneRouter installs the hook in _ready()")
	ShaderPrewarm.uninstall(router)  # start from a clean state; restored at the end
	var before := router.get_child_count()
	assert_true(ShaderPrewarm.install(router))
	assert_false(ShaderPrewarm.install(router), "idempotent")
	router.emit_signal(ShaderPrewarm.ROUTER_SIGNAL, "res://some/scene.tscn")
	assert_eq(router.get_child_count(), before + 1)
	var node := router.get_child(router.get_child_count() - 1) as ShaderPrewarm
	assert_true(node != null and node.is_running())
	assert_eq(node.scene_path, "res://some/scene.tscn")
	for i in int(node.config["measure_frames"]):
		node.tick(1.0)
	assert_true(node.is_queued_for_deletion())
	ShaderPrewarm.uninstall(router)
	router.emit_signal(ShaderPrewarm.ROUTER_SIGNAL, "res://other.tscn")
	assert_eq(router.get_child_count(), before + 1, "no spawn after uninstall (the finished one is only queued)")
	node.free()
	assert_eq(router.get_child_count(), before)
	ShaderPrewarm.install(router)


# --- Shader includes compile (front end) under the headless dummy renderer --------------------


func test_common_include_compiles_in_every_shader_stage() -> void:
	var shader_log := ShaderErrorLog.new()
	OS.add_logger(shader_log)
	var test_shader := load(TEST_SHADER) as Shader
	var names := test_shader.get_shader_uniform_list().map(func(u: Dictionary) -> String: return str(u["name"]))
	assert_true(names.has("col_tint") and names.has("noise_octaves"), "test shader compiled: %s" % str(names))
	var inc := '#include "%s"\n' % COMMON_INC
	var low := "#define HYMN_QUALITY HYMN_QUALITY_LOW\n" + inc
	var probe := "uniform float probe;\n"
	var sources: Array[String] = [
		(
			"shader_type canvas_item;\n"
			+ inc
			+ probe
			+ "void fragment() { COLOR.rgb = hymn_srgb_to_linear(vec3(probe)); }\n"
		),
		(
			"shader_type particles;\n"
			+ inc
			+ probe
			+ "void process() { VELOCITY = hymn_curl_fbm3(vec3(probe), 3, 2.0, 0.5); }\n"
		),
		"shader_type sky;\n" + low + probe + "void sky() { COLOR = vec3(hymn_fbm3(EYEDIR, 8, 2.0, 0.5) * probe); }\n",
		(
			"shader_type spatial;\n"
			+ inc
			+ inc
			+ probe
			+ "void fragment() { ALBEDO = vec3(hymn_value_noise3(vec3(probe))); }\n"
		),
		(
			"shader_type spatial;\n"
			+ inc
			+ '#include "%s"\n' % GLOBALS_INC
			+ probe
			+ "void fragment() { ALBEDO = hymn_glimmer.rgb * hymn_wind.w * probe; }\n"
		),
	]
	for src in sources:
		var sh := Shader.new()
		sh.code = src
		var uniforms := sh.get_shader_uniform_list().map(func(u: Dictionary) -> String: return str(u["name"]))
		assert_true(uniforms.has("probe"), "compile failed for:\n%s" % src)
	OS.remove_logger(shader_log)
	assert_eq(shader_log.count, 0, "shader compiler reported errors")


func test_compile_check_detects_a_broken_shader() -> void:
	var shader_log := ShaderErrorLog.new()
	OS.add_logger(shader_log)
	var sh := Shader.new()
	sh.code = (
		"shader_type spatial;\n"
		+ '#include "%s"\n' % COMMON_INC
		+ "uniform float probe;\nvoid fragment() { ALBEDO = vec3(hymn_no_such_fn(probe)); }\n"
	)
	# Compilation is lazy: it runs on first use (here, the uniform query), not on assignment.
	assert_eq(sh.get_shader_uniform_list().size(), 0, "a failed compile exposes no uniforms")
	OS.remove_logger(shader_log)
	assert_true(shader_log.count > 0, "the dummy renderer reports shader errors")


# --- helpers -----------------------------------------------------------------------------------


func _host() -> Node:
	# The tree root is busy while the runner scene is readying, so attach under the running scene.
	return (Engine.get_main_loop() as SceneTree).current_scene


func _shader_material(code: String) -> ShaderMaterial:
	var sh := Shader.new()
	sh.code = code
	var mat := ShaderMaterial.new()
	mat.shader = sh
	return mat


func _save(res: Resource, file_name: String) -> String:
	var path := TMP_DIR + "/" + file_name
	ResourceSaver.save(res, path)
	return path
