extends TestCase
## M1-RND-01: WaterSurface (material wiring, tiers, height query in world space), the water grid
## builder, and a headless compile check of every water shader variant (front end only; the GPU
## back end is covered by the screenshot shots water_* and the parity probe).

const MATERIAL := "res://game/levels/_tests/water/water_lagoon_material.tres"
const LAGOON_WAVES := "res://game/levels/_tests/water/lagoon_waves.tres"
const TEST_SCENE := "res://game/levels/_tests/water/water_test.tscn"
const SHADER_DIR := "res://game/shaders/water"
const TEST_SHADER_DIR := "res://game/shaders/water/test"
const EXPECTED_UNIFORMS: Array[String] = [
	"water_wave_a",
	"water_wave_b",
	"water_wave_count",
	"col_deep",
	"absorption_per_m",
	"caustic_strength",
	"caustic_pattern",
	"caustic_tex",
	"caustic_view_fade_m",
	"sea_glow_energy",
	"foam_shore_width_m",
	"use_ssr",
]
const TIME_S := 12.0


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


func _root() -> Node:
	# The tree root is busy while the runner scene is readying, so attach under the running scene.
	return (Engine.get_main_loop() as SceneTree).current_scene


func _surface(q: WaterSurface.Quality = WaterSurface.Quality.HIGH) -> WaterSurface:
	var w := WaterSurface.new()
	w.core_half_extent_m = 4.0
	w.core_cell_m = 1.0
	w.outer_half_extent_m = 16.0
	w.material = (load(MATERIAL) as ShaderMaterial).duplicate() as ShaderMaterial
	w.wave_set = load(LAGOON_WAVES) as WaveSet
	w.quality = q
	return w


# --- Shaders ----------------------------------------------------------------------------------


func test_every_water_shader_variant_compiles() -> void:
	var shader_log := ShaderErrorLog.new()
	OS.add_logger(shader_log)
	var files: Array[String] = []
	for f in DirAccess.get_files_at(SHADER_DIR):
		if f.ends_with(".gdshader"):
			files.append(SHADER_DIR.path_join(f))
	for f in DirAccess.get_files_at(TEST_SHADER_DIR):
		if f.ends_with(".gdshader"):
			files.append(TEST_SHADER_DIR.path_join(f))
	assert_true(files.size() >= 9, "4 ocean tiers + 2 river + 3 test shaders, got %d" % files.size())
	for path in files:
		var sh := load(path) as Shader
		var names: Array = sh.get_shader_uniform_list().map(func(u: Dictionary) -> String: return str(u["name"]))
		assert_true(names.size() > 0, "%s compiled to no uniforms (shader error?)" % path)
		if path.get_file().begins_with("water_ocean") or path.get_file().begins_with("water_river"):
			for u in EXPECTED_UNIFORMS:
				assert_true(names.has(u), "%s lacks uniform %s" % [path, u])
		if path.get_file().begins_with("water_river"):
			assert_true(names.has("tex_flow"), "river variant samples a flowmap")
	OS.remove_logger(shader_log)
	assert_eq(shader_log.count, 0, "shader compiler errors")


func test_every_tier_has_a_shader_and_presets_map_to_tiers() -> void:
	for q: int in WaterSurface.Quality.values():
		for river in [false, true]:
			assert_true(ResourceLoader.exists(WaterSurface.shader_path(q, river)), "tier %d river %s" % [q, river])
	assert_eq(WaterSurface.quality_for_preset("low"), WaterSurface.Quality.LOW)
	assert_eq(WaterSurface.quality_for_preset("ultra"), WaterSurface.Quality.ULTRA)
	assert_eq(WaterSurface.quality_for_preset("nonsense"), WaterSurface.Quality.HIGH)
	var presets: Variant = JSON.parse_string(
		FileAccess.get_file_as_string("res://game/data/settings/graphics_presets.json")
	)
	for p: Variant in (presets as Dictionary)["presets"]:
		var id := str((p as Dictionary)["id"])
		assert_true(
			GraphicsSettings.preset_tier(id, WaterSurface.PRESET_TIER_SYSTEM) in WaterSurface.QUALITY_NAMES,
			"graphics preset %s has no water tier" % id
		)


func test_low_tier_keeps_sea_glow() -> void:
	# Color script rule 3: never cut the night sea-glow on any preset.
	var body := FileAccess.get_file_as_string(SHADER_DIR.path_join("water_surface_body.gdshaderinc"))
	var glow_at := body.find("hymn_sea_glow(world")
	assert_true(glow_at > 0, "sea-glow term present")
	var before := body.substr(0, glow_at)
	assert_eq(before.count("#if") - before.count("#endif"), 1, "sea-glow sits outside every tier #if")


## M1-RND-08: the zone sea publishes hymn_water_level; animating its Y moves the level, the height
## query (and so foam and caustics, which live in world space on the same mesh) together.
func test_water_level_follows_the_node_and_is_registered() -> void:
	assert_true(ProjectSettings.has_setting("shader_globals/hymn_water_level"), "registered in project.godot")
	var globals := FileAccess.get_file_as_string("res://game/shaders/include/globals.gdshaderinc")
	assert_true(globals.contains("global uniform vec2 hymn_water_level;"), "declared")
	var w := WaterSurface.new()
	w.tide_line_y = 0.4
	(Engine.get_main_loop() as SceneTree).current_scene.add_child(w)
	assert_false(w.publishes_water_level, "off by default: only the zone sea opts in (M1-RND-15)")
	w.publishes_water_level = true
	var xz := Vector2(3.0, -2.0)
	var h0 := w.height_at(xz, 1.0)
	assert_eq(w.water_level(), Vector2(0.0, 0.4))
	w.position.y = 0.6  # Drownbell flood peak
	assert_eq(w.water_level(), Vector2(0.6, 0.4), "the level follows the node; the datum stays")
	assert_between(w.height_at(xz, 1.0) - h0, 0.6 - 1e-4, 0.6 + 1e-4, "the surface moved with it")
	w.free()


## M1-RND-15 (review-sweep-I S2, S3): one publisher per zone; the level resets when it leaves the
## tree (and SceneRouter resets it on every zone change), so the next zone never inherits a tide line.
func test_water_level_has_one_publisher_and_resets_on_exit() -> void:
	var host := (Engine.get_main_loop() as SceneTree).current_scene
	var pool := WaterSurface.new()
	host.add_child(pool)
	assert_false(pool.is_in_group(WaterSurface.LEVEL_PUBLISHERS_GROUP), "a pool does not publish")
	var sea := WaterSurface.new()
	sea.publishes_water_level = true
	host.add_child(sea)
	assert_true(sea.is_in_group(WaterSurface.LEVEL_PUBLISHERS_GROUP))
	assert_eq(sea.get_tree().get_node_count_in_group(WaterSurface.LEVEL_PUBLISHERS_GROUP), 1)
	sea.free()
	assert_eq(host.get_tree().get_node_count_in_group(WaterSurface.LEVEL_PUBLISHERS_GROUP), 0, "left the group")
	pool.free()
	var src := FileAccess.get_file_as_string("res://game/world/water/water_surface.gd")
	var exit := src.substr(src.find("func _exit_tree()"))
	exit = exit.substr(0, exit.find("\n\n\n"))
	assert_true(exit.contains("clear_water_level()"), "leaving the tree resets the level")
	var router := FileAccess.get_file_as_string("res://game/core/scene_router.gd")
	assert_true(router.contains("WaterSurface.clear_water_level()"), "SceneRouter resets it on a zone change")
	assert_true(router.contains("GlimmerField.clear_scene_sea_glow()"), "and the zone sea-glow")
	for scene: String in [
		"res://game/levels/_tests/water/water_test.tscn", "res://game/levels/_tests/undertow/undertow_test.tscn"
	]:
		assert_true(
			FileAccess.get_file_as_string(scene).contains("publishes_water_level = true"), "%s sea opts in" % scene
		)


func test_light_is_nan_safe_and_sss_is_view_dependent() -> void:
	# M1-RND-08: pow() of a negative base is undefined (NaN on some drivers): every Schlick base in
	# light() must be clamped, the half vector guarded (LIGHT = -VIEW), and the SSS wrap view-dependent.
	var body := FileAccess.get_file_as_string(SHADER_DIR.path_join("water_surface_body.gdshaderinc"))
	var light := body.substr(body.find("void light()"))
	assert_false(light.contains("normalize(LIGHT + VIEW)"), "half vector is guarded, not a bare normalize")
	assert_true(light.contains("float vdh = clamp(dot(VIEW, hv), 0.0, 1.0);"), "vdh clamped before pow(1 - vdh)")
	assert_true(light.contains("0.25 * wrap * toward_light"), "SSS wrap fades with the sun behind the viewer")


# --- WaterSurface ---------------------------------------------------------------------------


func test_surface_pushes_waves_and_tier_into_material() -> void:
	var w := _surface(WaterSurface.Quality.LOW)
	_root().add_child(w)
	var mat := w.material
	assert_eq(mat.shader.resource_path, WaterSurface.OCEAN_SHADERS[WaterSurface.Quality.LOW])
	assert_eq(mat.get_shader_parameter(GerstnerWaves.UNIFORM_COUNT), w.waves().count())
	var a := mat.get_shader_parameter(GerstnerWaves.UNIFORM_A) as PackedVector4Array
	assert_eq(a.size(), GerstnerWaves.MAX_WAVES)
	assert_eq(a[0], w.waves().wave_a[0])
	var deep_before: Variant = mat.get_shader_parameter(&"col_deep")
	w.quality = WaterSurface.Quality.ULTRA
	assert_eq(mat.shader.resource_path, WaterSurface.OCEAN_SHADERS[WaterSurface.Quality.ULTRA])
	assert_eq(mat.get_shader_parameter(&"col_deep"), deep_before, "authored look survives a tier change")
	w.river = true
	assert_eq(mat.shader.resource_path, WaterSurface.RIVER_SHADERS[WaterSurface.Quality.ULTRA])
	w.sea_glow_energy = 0.12
	assert_between(float(mat.get_shader_parameter(&"sea_glow_energy")), 0.1199, 0.1201)
	var surf := w.surface()
	assert_true(surf != null and surf.mesh != null, "grid built on enter")
	assert_eq(surf.cast_shadow, GeometryInstance3D.SHADOW_CASTING_SETTING_OFF, "water casts no shadow")
	assert_eq(surf.material_override, mat)
	assert_between(surf.extra_cull_margin, w.waves().amplitude_sum - 1e-5, w.waves().amplitude_sum + 1e-5)
	w.free()


func test_height_query_is_world_space() -> void:
	var w := _surface()
	_root().add_child(w)
	w.global_position = Vector3(5.0, -0.7, 3.0)  # Y = tide offset; XZ must not shift the waves.
	var xz := Vector2(10.25, -4.5)
	var want := -0.7 + w.waves().height_at(xz, TIME_S)
	assert_between(w.height_at(xz, TIME_S), want - 1e-6, want + 1e-6)
	assert_eq(w.normal_at(xz, TIME_S), w.waves().normal_at(xz, TIME_S))
	w.free()


func test_follow_target_snaps_grid_to_whole_cells() -> void:
	var w := _surface()
	var target := Node3D.new()
	_root().add_child(w)
	_root().add_child(target)
	w.follow_target = target
	target.global_position = Vector3(3.3, 9.0, -7.9)
	w._process(0.0)
	var p := w.surface().global_position
	var snap := w.core_cell_m * 2.0
	assert_between(fposmod(p.x, snap), -1e-6, 1e-6)
	assert_between(fposmod(p.z, snap), -1e-6, 1e-6)
	assert_eq(p.y, w.global_position.y, "follows in XZ only")
	w.free()
	target.free()


func test_test_scene_instances_with_rig_and_four_cameras() -> void:
	var scene := (load(TEST_SCENE) as PackedScene).instantiate()
	var rig := scene as WaterTestRig
	assert_true(rig != null, "root is the WaterTestRig")
	assert_true(rig.water != null and rig.sun != null and rig.moon != null, "node exports resolve")
	assert_eq(rig.night_nodes.size(), 3)
	for cam in ["Shallows", "Lagoon", "Horizon", "Night"]:
		assert_true(scene.get_node_or_null("Cameras/" + cam) is Camera3D, "camera %s" % cam)
	scene.free()


func test_rig_sun_direction_uses_compass_azimuth() -> void:
	var east := WaterTestRig.direction_from_angles(0.0, 90.0)
	assert_true(east.is_equal_approx(Vector3(1, 0, 0)), "az 90 = +X: %s" % east)
	var north := WaterTestRig.direction_from_angles(0.0, 0.0)
	assert_true(north.is_equal_approx(Vector3(0, 0, -1)), "az 0 = -Z: %s" % north)
	var up := WaterTestRig.direction_from_angles(90.0, 123.0)
	assert_true(up.is_equal_approx(Vector3.UP))


# --- Grid -----------------------------------------------------------------------------------


func test_grid_axis_is_symmetric_sorted_and_reaches_extent() -> void:
	var axis := WaterMeshBuilder.axis_coords(10.0, 0.5, 300.0, 1.1)
	var n := axis.size()
	assert_between(axis[0], -300.0 - 1e-3, -300.0 + 1e-3)
	assert_between(axis[n - 1], 300.0 - 1e-3, 300.0 + 1e-3)
	for i in n:
		assert_between(axis[i], -axis[n - 1 - i] - 1e-3, -axis[n - 1 - i] + 1e-3, "symmetric")
		if i > 0:
			assert_true(axis[i] > axis[i - 1], "strictly increasing")
	var mid := n / 2
	assert_between(axis[mid], -1e-6, 1e-6, "centre vertex at 0")
	assert_between(axis[mid + 1] - axis[mid], 0.5 - 1e-6, 0.5 + 1e-6, "core spacing")
	assert_true(axis[n - 1] - axis[n - 2] > 0.5, "outer cells grow")


func test_grid_mesh_counts_and_winding_face_up() -> void:
	var mesh := WaterMeshBuilder.build(2.0, 1.0, 8.0, 1.5)
	var n := WaterMeshBuilder.axis_coords(2.0, 1.0, 8.0, 1.5).size()
	var arrays := mesh.surface_get_arrays(0)
	var verts := arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array
	var idx := arrays[Mesh.ARRAY_INDEX] as PackedInt32Array
	assert_eq(verts.size(), n * n)
	assert_eq(idx.size(), (n - 1) * (n - 1) * 6)
	# Godot front faces are clockwise seen from the front: (b - a) x (c - a) points away (-Y).
	var a := verts[idx[0]]
	var b := verts[idx[1]]
	var c := verts[idx[2]]
	assert_true((b - a).cross(c - a).y < 0.0, "first triangle winds clockwise seen from above")
