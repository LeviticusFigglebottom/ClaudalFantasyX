extends TestCase
## M1-RND-06: shader-prewarm registry, lifecycle (completes, reports timing, frees), the
## SceneRouter hook, and a headless compile check of game/shaders/include/*.gdshaderinc.

const TEST_MATERIAL := "res://game/shaders/test/prewarm_test_material.tres"
const TEST_SHADER := "res://game/shaders/test/prewarm_test.gdshader"
const COMMON_INC := "res://game/shaders/include/common.gdshaderinc"
const GLOBALS_INC := "res://game/shaders/include/globals.gdshaderinc"
const TMP_DIR := "user://test_shader_prewarm"
const STATIC_STAGE_NODES := 4
const WATER_GRID := "res://game/world/water/prewarm/water_grid_prewarm.tres"
const SALTGRASS_GLB := "res://assets/environments/vegetation/saltgrass_clumps.glb"
const GLIMMER_PROCESS := "res://game/vfx/glimmer/materials/glimmer_motes_process.tres"
const GLIMMER_DRAW := "res://game/vfx/glimmer/materials/glimmer_motes_draw.tres"


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
	# M1-RND-22: the test material is the tests' own; registered for every transition it cost 118 ms of each.
	assert_false(paths.has(TEST_MATERIAL), "no test material in the production registry")
	for p in paths:
		assert_true(ResourceLoader.exists(p), "registered material missing: %s" % p)


## M1-RND-22: a tier variant is staged only on the presets that select its tier; untagged entries always.
func test_tier_variants_follow_the_active_preset() -> void:
	var low_skin := {"path": "x", "preset_tier": {"system": "character", "tier": "low"}}
	var high_skin := {"path": "x", "preset_tier": {"system": "character", "tier": "high"}}
	assert_true(ShaderPrewarm.entry_wanted(low_skin, "low"))
	assert_false(ShaderPrewarm.entry_wanted(low_skin, "high"))
	assert_true(ShaderPrewarm.entry_wanted(high_skin, "ultra"), "Ultra uses the high character tier")
	var body_med := {"path": "x", "preset_tier": {"system": "undertow", "tier": "medium"}}
	assert_true(ShaderPrewarm.entry_wanted(body_med, "medium"))
	assert_false(ShaderPrewarm.entry_wanted(body_med, "high"))
	var ocean_low := {"path": "x", "preset_tier": {"system": "water", "tier": "low"}}
	assert_true(ShaderPrewarm.entry_wanted(ocean_low, "low"))
	assert_false(ShaderPrewarm.entry_wanted(ocean_low, "ultra"))
	assert_true(ShaderPrewarm.entry_wanted({"path": "x"}, "high"), "untagged: every preset")
	assert_true(ShaderPrewarm.entry_wanted(low_skin, ""), "no preset known: stage everything")
	# Every tag in the registry names a tier some preset selects (a typo would never be staged).
	var reg := JSON.parse_string(FileAccess.get_file_as_string(ShaderPrewarm.REGISTRY_PATH)) as Dictionary
	for entry: Variant in reg["materials"]:
		var e := entry as Dictionary
		if not e.has("preset_tier"):
			continue
		var some := false
		for preset in ["low", "medium", "high", "ultra"]:
			some = some or ShaderPrewarm.entry_wanted(e, preset)
		assert_true(some, "no preset stages %s" % e["path"])


## M1-RND-22: boot holds the preset's resident entries and stages them once, whatever their scenes.
func test_resident_entries_are_held_and_staged_at_boot() -> void:
	DirAccess.make_dir_recursive_absolute(TMP_DIR)
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
			{"path": TEST_MATERIAL, "scenes": ["res://only/battle.tscn"], "resident": true},
			{
				"path": "res://game/shaders/character/character_skin_low.gdshader",
				"scenes": ["res://x.tscn"],
				"resident": true,
				"preset_tier": {"system": "character", "tier": "low"},
			},
			{"path": TEST_MATERIAL, "scenes": []},
		],
	}
	var reg_path := TMP_DIR + "/registry_resident.json"
	var f := FileAccess.open(reg_path, FileAccess.WRITE)
	f.store_string(JSON.stringify(reg))
	f.close()
	var before := ShaderPrewarm.resident_count()
	ShaderPrewarm.load_resident("high", reg_path)
	assert_eq(ShaderPrewarm.resident_count(), before + 1, "High holds the test material, not the Low skin")
	ShaderPrewarm.load_resident("high", reg_path)
	assert_eq(ShaderPrewarm.resident_count(), before + 1, "held once")
	var node := (load(ShaderPrewarm.SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	node.registry_path = reg_path
	node.resident_only = true
	node.preset_id = "high"
	_host().add_child(node)
	assert_eq(node.start(""), 1, "only the resident entry the preset wants, whatever its scenes")
	node.free()
	DirAccess.remove_absolute(reg_path)
	DirAccess.remove_absolute(TMP_DIR)


# --- Lifecycle ---------------------------------------------------------------------------------


func test_prewarm_completes_reports_timing_and_frees() -> void:
	# Its own registry (M1-RND-22: the production one no longer carries the test material): the live
	# timing values, the test material for every transition, nothing else.
	var live := JSON.parse_string(FileAccess.get_file_as_string(ShaderPrewarm.REGISTRY_PATH)) as Dictionary
	live["materials"] = [{"path": TEST_MATERIAL, "scenes": []}]
	live["scene_materials"] = false
	DirAccess.make_dir_recursive_absolute(TMP_DIR)
	var reg_path := TMP_DIR + "/registry_lifecycle.json"
	var f := FileAccess.open(reg_path, FileAccess.WRITE)
	f.store_string(JSON.stringify(live))
	f.close()
	var node := (load(ShaderPrewarm.SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	node.registry_path = reg_path
	_host().add_child(node)
	node.start("res://some/battle.tscn")
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
	DirAccess.remove_absolute(reg_path)
	DirAccess.remove_absolute(TMP_DIR)


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


## M1-RND-07: entries can carry the real mesh, the MultiMesh path and a particles draw material, and
## the stage copies the game viewport's AA.
func test_entries_draw_real_meshes_multimesh_and_particle_passes() -> void:
	var quad := QuadMesh.new()
	assert_eq(ShaderPrewarm.entry_mesh({}, quad), quad, "no mesh key: the quad")
	assert_eq(ShaderPrewarm.entry_mesh({"mesh": "res://does/not/exist.tres"}, quad), quad)
	var grid := ShaderPrewarm.entry_mesh({"mesh": WATER_GRID}, quad)
	assert_true(grid is ArrayMesh, "a Mesh resource")
	var built := WaterMeshBuilder.build(1.0, 0.5, 2.0, 1.1)
	assert_eq(grid.surface_get_format(0), built.surface_get_format(0), "committed grid = the ocean's vertex format")
	var grass := ShaderPrewarm.entry_mesh({"mesh": SALTGRASS_GLB, "mesh_node": "saltgrass_a"}, quad)
	assert_ne(grass, quad, "a named MeshInstance3D inside a .glb")
	var reg := {
		"frames_to_render": 1,
		"measure_frames": 2,
		"hitch_budget_ms": 50.0,
		"viewport_width": 32,
		"viewport_height": 32,
		"quad_size": 1.0,
		"quad_distance": 1.5,
		"particle_amount": 1,
		"multimesh_instances": 2,
		"materials":
		[
			{"path": TEST_MATERIAL, "mesh": WATER_GRID, "multimesh": true, "scenes": []},
			{"path": GLIMMER_PROCESS, "draw_material": GLIMMER_DRAW, "scenes": []},
		],
	}
	DirAccess.make_dir_recursive_absolute(TMP_DIR)
	var reg_path := TMP_DIR + "/registry_mesh.json"
	var f := FileAccess.open(reg_path, FileAccess.WRITE)
	f.store_string(JSON.stringify(reg))
	f.close()
	var node := (load(ShaderPrewarm.SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	node.registry_path = reg_path
	_host().add_child(node)
	var game := node.get_viewport()
	var taa_was := game.use_taa
	game.use_taa = true
	assert_eq(node.start(""), 2)
	assert_true((node.get_node("Viewport") as SubViewport).use_taa, "the stage matches the game's TAA")
	game.use_taa = taa_was
	var stage := node.get_node("Viewport/Stage3D")
	var mmi := stage.find_children("*", "MultiMeshInstance3D", true, false)
	assert_eq(mmi.size(), 1, "multimesh entry drawn through a MultiMeshInstance3D")
	var mm := (mmi[0] as MultiMeshInstance3D).multimesh
	assert_true(mm.use_colors and mm.use_custom_data)
	assert_eq(mm.instance_count, 2)
	var parts := stage.find_children("*", "GPUParticles3D", true, false)
	assert_eq(parts.size(), 1)
	var draw := ((parts[0] as GPUParticles3D).draw_pass_1 as QuadMesh).material as ShaderMaterial
	assert_eq(draw.shader.resource_path, GlimmerField.DRAW_SHADER.resource_path, "the real draw pass")
	node.tick(5.0)
	node.tick(5.0)
	DirAccess.remove_absolute(reg_path)
	DirAccess.remove_absolute(TMP_DIR)


## M1-RND-07: with scene_materials the incoming scene's own (inline) materials are staged on their
## own meshes, MultiMeshes included, without a registry entry.
func test_scene_materials_are_harvested_from_the_incoming_scene() -> void:
	DirAccess.make_dir_recursive_absolute(TMP_DIR)
	var root := Node3D.new()
	var box := MeshInstance3D.new()
	box.mesh = BoxMesh.new()
	var inline := StandardMaterial3D.new()
	inline.albedo_color = Color.RED
	box.material_override = inline
	root.add_child(box)
	box.owner = root
	var grass := MultiMeshInstance3D.new()
	grass.multimesh = MultiMesh.new()
	grass.multimesh.transform_format = MultiMesh.TRANSFORM_3D
	grass.multimesh.use_colors = true
	var blade := QuadMesh.new()
	blade.material = StandardMaterial3D.new()
	grass.multimesh.mesh = blade
	root.add_child(grass)
	grass.owner = root
	var packed := PackedScene.new()
	packed.pack(root)
	root.free()
	var scene_path := TMP_DIR + "/harvest.tscn"
	ResourceSaver.save(packed, scene_path)
	var reg := {
		"frames_to_render": 1,
		"measure_frames": 2,
		"hitch_budget_ms": 50.0,
		"viewport_width": 32,
		"viewport_height": 32,
		"quad_size": 1.0,
		"quad_distance": 1.5,
		"particle_amount": 1,
		"multimesh_instances": 2,
		"scene_materials": true,
		"max_scene_materials": 16,
		"materials": [],
	}
	var reg_path := TMP_DIR + "/registry_harvest.json"
	var f := FileAccess.open(reg_path, FileAccess.WRITE)
	f.store_string(JSON.stringify(reg))
	f.close()
	var node := (load(ShaderPrewarm.SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	node.registry_path = reg_path
	_host().add_child(node)
	assert_eq(node.start(scene_path), 2, "the box's inline material and the grass blade's")
	var stage := node.get_node("Viewport/Stage3D")
	assert_eq(stage.find_children("*", "MultiMeshInstance3D", true, false).size(), 1, "grass through a MultiMesh")
	var boxes := stage.find_children("*", "MeshInstance3D", true, false)
	assert_true(boxes.any(func(n: Node) -> bool: return (n as MeshInstance3D).mesh is BoxMesh), "on its own mesh")
	node.tick(5.0)
	node.tick(5.0)
	for file in DirAccess.get_files_at(TMP_DIR):
		DirAccess.remove_absolute(TMP_DIR + "/" + file)
	DirAccess.remove_absolute(TMP_DIR)


## M1-RND-15 (review-sweep-I on RND-07, S1): the stage is time-sliced. At most materials_per_frame
## draws enter per frame, an over-budget frame halves the batch, the stage clears frames_to_render
## frames after the last batch, and SceneRouter can see it is still staging.
func test_stage_is_time_sliced_and_self_tunes() -> void:
	var reg := {
		"frames_to_render": 2,
		"measure_frames": 2,
		"hitch_budget_ms": 50.0,
		"materials_per_frame": 4,
		"slice_budget_ms": 33.0,
		"viewport_width": 32,
		"viewport_height": 32,
		"quad_size": 1.0,
		"quad_distance": 1.5,
		"materials": [],
	}
	for i in 11:
		(reg["materials"] as Array).append({"path": TEST_MATERIAL, "scenes": []})
	DirAccess.make_dir_recursive_absolute(TMP_DIR)
	var reg_path := TMP_DIR + "/registry_slice.json"
	var f := FileAccess.open(reg_path, FileAccess.WRITE)
	f.store_string(JSON.stringify(reg))
	f.close()
	var router := SwapHoldStub.new()
	_host().add_child(router)
	var node := (load(ShaderPrewarm.SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	node.registry_path = reg_path
	router.add_child(node)
	assert_eq(node.start(""), 11, "every draw is built at start")
	assert_eq(node.stage_node_count(), 4, "but only one batch is staged on the first frame")
	assert_eq(node.pending_count(), 7)
	assert_true(node.is_staging() and router.holders.has(node), "staging holds the parent's swap (M1-RND-23)")
	node.tick(20.0)  # under the slice budget: the next full batch goes in
	assert_eq(node.stage_node_count(), 8)
	node.tick(90.0)  # over budget: the batch halves
	assert_eq(node.batch_size(), 2)
	assert_eq(node.stage_node_count(), 10)
	node.tick(10.0)
	assert_eq(node.stage_node_count(), 11)
	assert_eq(node.pending_count(), 0)
	node.tick(10.0)
	assert_true(node.is_staging(), "the last batch still renders frames_to_render frames")
	node.tick(10.0)
	assert_false(node.is_staging())
	assert_false(router.holders.has(node), "and releases it when the stage clears")
	assert_eq(node.stage_node_count(), 0, "stage cleared")
	assert_eq(node.stats["batches"], 4)
	assert_eq(node.stats["min_batch"], 2)
	assert_eq(node.stats["materials"], 11)
	assert_true(node.is_queued_for_deletion())
	router.free()
	DirAccess.remove_absolute(reg_path)
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


## M1-RND-27 (ADR 0029 follow-up 3): a boot run draws its stage plain first and turns the game
## viewport's TAA and upscaler on one a frame before it stages anything; it holds each resident entry
## as its batch loads it, not all in the spawn frame.
## M2-RND-14: with TAA off (and no FSR2) the boot still turns Forward+'s advanced shader group on under the card:
## one frame of TAA on the stage right after the plain first frame, then TAA off again, before anything stages. With
## the group switched on lazily, a TAA-off player's first VoxelGI frame (the Shell Shrine) could deadlock 4.6.3.
func test_a_taa_off_boot_turns_the_advanced_shader_group_on_before_staging() -> void:
	var reg_path := _write_registry(
		"registry_adv.json", {"materials": [{"path": TEST_SHADER, "scenes": [], "resident": true}]}
	)
	var game := get_viewport_for_test()
	var was := [game.use_taa, game.scaling_3d_mode, game.screen_space_aa]
	game.use_taa = false
	game.scaling_3d_mode = Viewport.SCALING_3D_MODE_BILINEAR
	game.screen_space_aa = Viewport.SCREEN_SPACE_AA_FXAA
	var node := (load(ShaderPrewarm.SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	node.registry_path = reg_path
	node.resident_only = true
	node.preset_id = "high"
	_host().add_child(node)
	node.start("")
	var vp := node.get_node("Viewport") as SubViewport
	assert_false(vp.use_taa, "the first frame is plain")
	node.tick(5.0)
	assert_true(vp.use_taa, "one frame of TAA: the advanced shader group comes on under the card")
	assert_eq(node.stage_node_count(), 0, "before anything stages")
	node.tick(5.0)
	assert_false(vp.use_taa, "then the player's AA again")
	node.free()
	# With TAA on the game has motion vectors already: no extra frame.
	game.use_taa = true
	var on := (load(ShaderPrewarm.SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	on.registry_path = reg_path
	on.resident_only = true
	on.preset_id = "high"
	_host().add_child(on)
	on.start("")
	var taa_steps := on._bring_up.filter(func(step: Array) -> bool: return step[0] == &"use_taa")
	assert_eq(taa_steps.size(), 1, "TAA on: only its own TAA step, no extra frame")
	on.free()
	game.use_taa = was[0]
	game.scaling_3d_mode = was[1]
	game.screen_space_aa = was[2]
	_clean_tmp()


func test_boot_brings_the_stage_up_one_feature_a_frame_and_holds_residents_in_their_batch() -> void:
	var reg_path := _write_registry(
		"registry_boot.json",
		{"materials": [{"path": TEST_SHADER, "scenes": ["res://only/battle.tscn"], "resident": true}]}
	)
	var game := get_viewport_for_test()
	var was := [game.use_taa, game.scaling_3d_mode]
	game.use_taa = true
	game.scaling_3d_mode = Viewport.SCALING_3D_MODE_FSR2
	var before := ShaderPrewarm.resident_count()
	var node := (load(ShaderPrewarm.SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	node.registry_path = reg_path
	node.resident_only = true
	node.preset_id = "high"
	_host().add_child(node)
	assert_eq(node.start(""), 1)
	var vp := node.get_node("Viewport") as SubViewport
	assert_false(vp.use_taa, "the first frame is plain")
	assert_eq(vp.scaling_3d_mode, Viewport.SCALING_3D_MODE_BILINEAR)
	assert_eq(node.stage_node_count(), 0, "nothing staged while the viewport comes up")
	assert_eq(ShaderPrewarm.resident_count(), before, "nothing loaded in the spawn frame")
	node.tick(5.0)
	assert_true(vp.use_taa, "TAA on the second frame")
	assert_eq(vp.scaling_3d_mode, Viewport.SCALING_3D_MODE_BILINEAR, "the upscaler a frame later")
	node.tick(5.0)
	assert_eq(vp.scaling_3d_mode, Viewport.SCALING_3D_MODE_FSR2)
	assert_eq(node.stage_node_count(), 1, "then the first batch")
	assert_eq(ShaderPrewarm.resident_count(), before + 1, "held as its batch loaded it")
	node.free()
	game.use_taa = was[0]
	game.scaling_3d_mode = was[1]
	_clean_tmp()


## M1-RND-27 (RND-27 criterion 2, ADR 0028): the Undertow body's spatial shaders are marked as having a
## compute twin; without a RenderingDevice (here, headless) the spatial body is what draws, so it is
## staged as before.
func test_undertow_bodies_have_compute_twins_and_fall_back_without_a_device() -> void:
	var reg := JSON.parse_string(FileAccess.get_file_as_string(ShaderPrewarm.REGISTRY_PATH)) as Dictionary
	var twins := 0
	for e: Dictionary in reg["materials"]:
		if bool(e.get("compute_twin", false)):
			twins += 1
			var twin := UndertowBodyEffect.compute_path_for(str(e["path"]))
			assert_true(twin != "" and ResourceLoader.exists(twin), "%s has a compute twin on disk" % e["path"])
	assert_eq(twins, 3, "Medium, High and Ultra bodies")
	if RenderingServer.get_rendering_device() == null:
		assert_false(ShaderPrewarm.undertow_uses_compute("high"), "no device: the spatial body draws")
		var reg_path := _write_registry(
			"registry_twin.json",
			{
				"materials":
				[{"path": "res://game/shaders/undertow/undertow_body.gdshader", "scenes": [], "compute_twin": true}]
			}
		)
		var node := (load(ShaderPrewarm.SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
		node.registry_path = reg_path
		node.preset_id = "high"
		_host().add_child(node)
		node.start("")
		assert_eq(node.stage_node_count(), 1, "staged as a spatial draw")
		node.free()
		_clean_tmp()


## M1-RND-27 (ADR 0029 follow-up 2): the harvest reads the scene's SceneState, follows instanced scenes
## (with the instancing scene's overrides on their root), reads a PrimitiveMesh's material without
## building it, and builds every draw in its batch, not in start().
func test_harvest_reads_scene_states_and_builds_draws_in_their_batch() -> void:
	DirAccess.make_dir_recursive_absolute(TMP_DIR)
	var sub := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	var stone := StandardMaterial3D.new()
	stone.albedo_color = Color.GRAY
	cyl.material = stone
	sub.mesh = cyl
	var sub_packed := PackedScene.new()
	sub_packed.pack(sub)
	sub.free()
	var sub_path := TMP_DIR + "/harvest_sub.tscn"
	ResourceSaver.save(sub_packed, sub_path)
	var root := Node3D.new()
	var a := (load(sub_path) as PackedScene).instantiate()
	root.add_child(a)
	a.owner = root
	var b := (load(sub_path) as PackedScene).instantiate() as MeshInstance3D
	var red := StandardMaterial3D.new()
	red.albedo_color = Color.RED
	b.material_override = red
	root.add_child(b)
	b.owner = root
	var packed := PackedScene.new()
	packed.pack(root)
	root.free()
	var scene_path := TMP_DIR + "/harvest_outer.tscn"
	ResourceSaver.save(packed, scene_path)
	var reg_path := _write_registry(
		"registry_state.json", {"scene_materials": true, "max_scene_materials": 16, "materials_per_frame": 1}
	)
	var node := (load(ShaderPrewarm.SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	node.registry_path = reg_path
	_host().add_child(node)
	assert_eq(node.start(scene_path), 2, "the sub-scene's stone, and the override on the second instance")
	assert_eq(node.stage_node_count(), 1, "one batch built")
	assert_eq(node.pending_count(), 1, "the other waits, unbuilt")
	node.tick(5.0)
	var colors := node.get_node("Viewport/Stage3D").find_children("*", "MeshInstance3D", true, false).map(
		func(n: Node) -> Color: return ((n as MeshInstance3D).material_override as StandardMaterial3D).albedo_color
	)
	assert_eq(colors.size(), 2)
	assert_true(colors.has(Color.RED), "the instancing scene's override on the instance root")
	assert_true(colors.has(Color.GRAY), "the sub-scene's PrimitiveMesh material")
	node.free()
	_clean_tmp()


func get_viewport_for_test() -> Viewport:
	return (Engine.get_main_loop() as SceneTree).root


func _write_registry(file: String, extra: Dictionary) -> String:
	DirAccess.make_dir_recursive_absolute(TMP_DIR)
	var reg := {
		"frames_to_render": 1,
		"measure_frames": 2,
		"hitch_budget_ms": 50.0,
		"viewport_width": 32,
		"viewport_height": 32,
		"quad_size": 1.0,
		"quad_distance": 1.5,
		"particle_amount": 1,
		"multimesh_instances": 2,
		"materials": [],
	}
	reg.merge(extra, true)
	var path := TMP_DIR + "/" + file
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(JSON.stringify(reg))
	f.close()
	return path


func _clean_tmp() -> void:
	for file in DirAccess.get_files_at(TMP_DIR):
		DirAccess.remove_absolute(TMP_DIR + "/" + file)
	DirAccess.remove_absolute(TMP_DIR)


## A resident entry can be limited to some presets (resident_presets, data); Asha's materials are resident
## on every preset (Low measured over ADR 0029's 3 s Haluna entry without them).
func test_residency_can_be_limited_per_preset() -> void:
	var e := {"path": TEST_MATERIAL, "resident": true, "resident_presets": ["high", "ultra"]}
	assert_true(ShaderPrewarm.entry_resident(e, "high"))
	assert_false(ShaderPrewarm.entry_resident(e, "low"), "streamed on a preset the list leaves out")
	assert_true(ShaderPrewarm.entry_resident({"resident": true}, "low"), "no list: every preset")
	assert_false(ShaderPrewarm.entry_resident({"resident_presets": ["low"]}, "low"), "not resident at all")
	var reg := JSON.parse_string(FileAccess.get_file_as_string(ShaderPrewarm.REGISTRY_PATH)) as Dictionary
	for entry: Dictionary in reg["materials"]:
		if str(entry.get("path", "")).begins_with("res://assets/characters/asha/materials/"):
			for preset in ["low", "medium", "high", "ultra"]:
				assert_true(ShaderPrewarm.entry_resident(entry, preset), "%s held on %s" % [entry["path"], preset])


## M1-RND-29 gate fix: a headless boot (CI's smoke test) never runs the first-launch warm-up, and a warm-up
## freed mid-run leaves no stage nodes behind and holds its resources on a node the tree frees, not in a
## static that outlives Godot's exit check (225 resources were still in use at exit).
func test_headless_skips_the_first_run_and_an_interrupted_warm_up_leaves_nothing() -> void:
	if ShaderPrewarm.is_headless():
		assert_false(ShaderPrewarm.needs_first_run("high"), "headless: no first-launch staging or harvest")
	var reg_path := _write_registry(
		"registry_interrupt.json",
		{"materials": [{"path": TEST_SHADER, "scenes": [], "resident": true}], "materials_per_frame": 1}
	)
	var nodes_before := Performance.get_monitor(Performance.OBJECT_NODE_COUNT)
	var node := (load(ShaderPrewarm.SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	node.registry_path = reg_path
	node.resident_only = true
	node.first_run = true
	node.preset_id = "high"
	_host().add_child(node)
	node.start("")
	node.tick(5.0)
	assert_true(node.is_running(), "still mid warm-up")
	node.free()
	assert_eq(Performance.get_monitor(Performance.OBJECT_NODE_COUNT), nodes_before, "no stage node outlives it")
	var holder := (Engine.get_main_loop() as SceneTree).root.find_child(ShaderPrewarm.RESIDENT_HOLDER, false, false)
	assert_true(holder == null or holder is ShaderPrewarm.ResidentHolder, "residents live on a tree node")
	_clean_tmp()


## M2-RND-15: a first run instances each first_run_live_scenes entry on a worker thread and stages the draws its
## live instance holds (a zone's runtime-built surfaces no SceneState lists), then frees the instance.
func test_a_first_run_stages_the_draws_of_its_live_scenes_and_frees_them() -> void:
	DirAccess.make_dir_recursive_absolute(TMP_DIR)
	var mi := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color.TEAL
	mesh.material = mat
	mi.mesh = mesh
	var packed := PackedScene.new()
	packed.pack(mi)
	mi.free()
	var scene_path := TMP_DIR + "/live_scene.tscn"
	ResourceSaver.save(packed, scene_path)
	var reg_path := _write_registry(
		"registry_live.json", {"first_run_live_scenes": [scene_path], "max_live_materials": 8, "materials_per_frame": 4}
	)
	var nodes_before := Performance.get_monitor(Performance.OBJECT_NODE_COUNT)
	var node := (load(ShaderPrewarm.SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	node.registry_path = reg_path
	node.resident_only = true
	node.first_run = true
	node.preset_id = "high"
	_host().add_child(node)
	assert_eq(node.start(""), 0, "nothing listed up front: the live scene comes later")
	var got: Array[Dictionary] = []
	node.finished.connect(func(st: Dictionary) -> void: got.append(st))
	for i in 600:
		if not node.is_running():
			break
		# The live scene instances on a worker thread: let it run between ticks.
		OS.delay_msec(5)
		node.tick(4.0)
	assert_false(node.is_running(), "the first run finishes once its live scene is harvested and drawn")
	assert_eq(got.size(), 1)
	assert_eq(int(got[0]["materials"]), 1, "the live instance's material was staged")
	if is_instance_valid(node):
		node.free()
	assert_eq(Performance.get_monitor(Performance.OBJECT_NODE_COUNT), nodes_before, "the live instance is freed")
	_clean_tmp()


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


## A parent with SceneRouter's hold API (hold_swap / release_swap), without the autoload.
class SwapHoldStub:
	extends Node
	var holders: Array[Object] = []

	func hold_swap(holder: Object) -> void:
		if not holders.has(holder):
			holders.append(holder)

	func release_swap(holder: Object) -> void:
		holders.erase(holder)


## M2-ARC-08: the warm-up reports its progress to the boot card (a count that moves every tick, and a 0..1
## fraction of its staging), and cancel() stops it when the card gives up: the stage clears, the swap hold is
## released, no `finished`, and a first run writes no marker, so the next launch runs it again.
func test_progress_is_reported_and_a_cancelled_warm_up_leaves_nothing_staged() -> void:
	var marker := TMP_DIR + "/first_run_marker.cfg"
	var mats := []
	for i in 4:
		mats.append({"path": TEST_MATERIAL, "scenes": []})
	var reg_path := _write_registry(
		"registry_cancel.json", {"materials": mats, "materials_per_frame": 1, "first_run_marker": marker}
	)
	var router := SwapHoldStub.new()
	_host().add_child(router)
	var node := (load(ShaderPrewarm.SCENE_PATH) as PackedScene).instantiate() as ShaderPrewarm
	node.registry_path = reg_path
	node.first_run = true
	router.add_child(node)
	node.start("")
	var got: Array[Dictionary] = []
	node.finished.connect(func(s: Dictionary) -> void: got.append(s))
	assert_eq(node.progress_fraction(), 0.25, "one of four draws staged at start")
	var p0 := node.wait_progress()
	node.tick(16.0)
	assert_eq(node.wait_progress(), p0 + 1, "every tick is a step of a finite run")
	assert_eq(node.progress_fraction(), 0.5)
	node.cancel()
	assert_false(node.is_running(), "stopped")
	assert_eq(node.stage_node_count(), 0, "nothing left staging under the title")
	assert_eq(node.pending_count(), 0)
	assert_false(router.holders.has(node), "the swap hold is released")
	assert_true(node.is_queued_for_deletion(), "it frees itself")
	assert_eq(got.size(), 0, "no finished stats for a cut run")
	assert_false(FileAccess.file_exists(marker), "no first-run marker: the next launch warms up again")
	assert_eq(node.progress_fraction(), 1.0)
	node.cancel()
	router.free()
	_clean_tmp()
