extends TestCase
## M1-ENV-01: the environment shaders compile headlessly (front end: preprocessor, includes, types;
## the GPU back end is covered by the haluna_* screenshot shots), every weathering tier exposes the
## haluna.md §4 layer uniforms, and the kit materials load on their shaders.

const SHADER_DIR := "res://game/shaders/environment"
const MATERIAL_DIR := "res://assets/environments/kits/haluna/materials"
const WEATHERING_UNIFORMS: Array[String] = [
	"tex_albedo",
	"tex_normal",
	"tex_detail",
	"capillary_band_m",
	"algae_band_m",
	"barnacle_band_m",
	"salt_band_m",
	"moss_min_height_m",
	"wet_darken",
	"paint_cover",
]
const EXPECTED: Dictionary = {
	"env_ground.gdshader": ["tex_sand", "wet_band_m"],
	"env_wake_shell.gdshader": ["tex_glyph", "glyph_depth"],
	"env_sky_cumulus.gdshader": ["cloud_coverage", "cloud_steps", "col_cloud_shadow"],
	"env_sky_night.gdshader": ["star_density", "col_moon", "moon_disc_deg"],
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


static func _uniforms(path: String) -> Array:
	var sh := load(path) as Shader
	if sh == null:
		return []
	return sh.get_shader_uniform_list().map(func(u: Dictionary) -> String: return str(u["name"]))


func test_every_environment_shader_compiles() -> void:
	var shader_log := ShaderErrorLog.new()
	OS.add_logger(shader_log)
	var files: Array[String] = []
	for f in DirAccess.get_files_at(SHADER_DIR):
		if f.ends_with(".gdshader"):
			files.append(f)
	assert_true(files.size() >= 7, "4 weathering tiers + ground + shell + sky, got %d" % files.size())
	for f in files:
		var names := _uniforms(SHADER_DIR.path_join(f))
		assert_true(names.size() > 0, "%s compiled to no uniforms (shader error?)" % f)
		if f.begins_with("env_weathering"):
			for u in WEATHERING_UNIFORMS:
				assert_true(names.has(u), "%s lacks uniform %s" % [f, u])
		for u: String in EXPECTED.get(f, []):
			assert_true(names.has(u), "%s lacks uniform %s" % [f, u])
	OS.remove_logger(shader_log)
	assert_eq(shader_log.count, 0, "shader compiler errors")


func test_every_weathering_tier_exists() -> void:
	for q: int in WeatheringTide.Quality.values():
		assert_true(ResourceLoader.exists(String(WeatheringTide.WEATHERING_SHADERS[q])), "tier %d" % q)
	var presets: Variant = JSON.parse_string(
		FileAccess.get_file_as_string("res://game/data/settings/graphics_presets.json")
	)
	for p: Variant in (presets as Dictionary)["presets"]:
		var id := str((p as Dictionary)["id"])
		var tier := GraphicsSettings.preset_tier(id, WeatheringTide.PRESET_TIER_SYSTEM)
		assert_true(WeatheringTide.TIER_NAMES.has(tier), "graphics preset %s has no weathering tier" % id)


func test_low_tier_drops_triplanar() -> void:
	var low := FileAccess.get_file_as_string(SHADER_DIR.path_join("env_weathering_low.gdshader"))
	assert_true(low.contains("HYMN_QUALITY_LOW"), "low wrapper defines its tier")
	var body := FileAccess.get_file_as_string(SHADER_DIR.path_join("env_weathering_body.gdshaderinc"))
	var tri := body.find("if (base_triplanar)")
	assert_true(tri > 0, "triplanar branch present")
	var before := body.substr(0, tri)
	assert_true(
		before.rfind("#if HYMN_QUALITY >= HYMN_QUALITY_MEDIUM") > before.rfind("#endif"), "triplanar is Medium+"
	)


func test_kit_materials_load_on_their_shaders() -> void:
	var count := 0
	for f in DirAccess.get_files_at(MATERIAL_DIR):
		if not f.ends_with(".tres"):
			continue
		var mat := load(MATERIAL_DIR.path_join(f)) as Material
		assert_true(mat != null, "%s loads" % f)
		if mat is ShaderMaterial:
			assert_true((mat as ShaderMaterial).shader != null, "%s has a shader" % f)
		count += 1
	assert_true(count >= 20, "kit materials present (%d)" % count)


## M1-ENV-05: the tide moves the sea and gives it the datum; the sea publishes hymn_water_level, which
## the weathering and ground shaders read (no per-material tide uniforms).
func test_tide_drives_the_sea_that_publishes_the_water_level() -> void:
	var tide := WeatheringTide.new()
	var mat := (load(MATERIAL_DIR.path_join("kit_coral_stone.tres")) as ShaderMaterial).duplicate() as ShaderMaterial
	var water := WaterSurface.new()
	water.publishes_water_level = true
	tide.water = water
	tide.register(mat)
	tide.register(mat)
	assert_eq(tide.registered().size(), 1, "register is idempotent")
	tide.water_height_y = 0.6
	tide.tide_line_y = -0.1
	assert_between(water.position.y, 0.599, 0.601, "the sea follows the flood rig")
	assert_eq(water.tide_line_y, -0.1, "the sea carries the datum")
	assert_true(water.water_level().is_equal_approx(Vector2(0.6, -0.1)), "what hymn_water_level carries")
	assert_true(tide.water_level().is_equal_approx(water.water_level()))
	assert_eq(mat.get_shader_parameter(&"water_height_y"), null, "no per-material uniform is written")
	tide.quality = WeatheringTide.Quality.LOW
	assert_eq(mat.shader.resource_path, String(WeatheringTide.WEATHERING_SHADERS[WeatheringTide.Quality.LOW]))
	water.free()
	tide.free()


func test_weathering_shaders_read_the_water_level_global() -> void:
	for f: String in ["env_weathering_body.gdshaderinc", "env_ground.gdshader"]:
		var code := FileAccess.get_file_as_string(SHADER_DIR.path_join(f))
		assert_true(code.contains("hymn_water_level"), "%s reads hymn_water_level" % f)
		assert_false(code.contains("uniform float water_height_y"), "%s has no tide uniform" % f)
	for path: String in WeatheringTide.WEATHERING_SHADERS.values():
		assert_false(_uniforms(path).has("tide_line_y"), "%s: the datum is the global's" % path)


func test_weathering_tier_comes_from_the_presets() -> void:
	for preset: String in ["low", "medium", "high", "ultra"]:
		var tier := GraphicsSettings.preset_tier(preset, WeatheringTide.PRESET_TIER_SYSTEM)
		assert_eq(WeatheringTide.quality_for_preset(preset), WeatheringTide.TIER_NAMES[tier], preset)
	assert_eq(WeatheringTide.quality_for_preset("nonsense"), WeatheringTide.Quality.HIGH)


func test_the_haluna_sea_is_the_one_publisher() -> void:
	var zone := (load("res://game/levels/_tests/haluna_mood/haluna_mood.tscn") as PackedScene).instantiate()
	var publishers := 0
	for n: Node in zone.find_children("*", "", true, false):
		if n is WaterSurface and (n as WaterSurface).publishes_water_level:
			publishers += 1
	assert_eq(publishers, 1, "exactly one WaterSurface publishes hymn_water_level")
	assert_true((zone.get_node("Water") as WaterSurface).publishes_water_level, "the sea")
	zone.free()


func test_layout_is_valid_and_shots_use_camera_shots() -> void:
	var layout := HalunaDresser._load_json("res://game/levels/ch02/haluna/haluna_layout.json")
	assert_false(layout.is_empty(), "layout parses")
	var kit_dir := String(layout.get("kit_dir", ""))
	for spec: Dictionary in layout.get("pieces", []):
		var path := kit_dir + String(spec["piece"]) + ".glb"
		assert_true(ResourceLoader.exists(path), "piece %s exists" % path)
	for kind: Dictionary in (layout.get("plant_kinds", {}) as Dictionary).values():
		assert_true(ResourceLoader.exists(String(kind["glb"])), "plant %s exists" % kind["glb"])
	var scene := (load("res://game/levels/_tests/haluna_mood/haluna_mood.tscn") as PackedScene).instantiate()
	var cams := scene.get_node("Cameras").get_children()
	assert_eq(cams.size(), 6, "five composed noon shots (haluna.md §5.1 ◆) and H10 at night (M2-ENV-02)")
	for c: Node in cams:
		var sc := c as HalunaShotCamera
		assert_true(sc != null and sc.shot != null, "%s is driven by a CameraShot" % c.name)
	scene.free()


func test_run_along_polyline() -> void:
	var pts := PackedVector2Array([Vector2(0, 0), Vector2(10, 0), Vector2(10, 10)])
	assert_eq(HalunaDresser._along(pts, 5.0), Vector2(5, 0))
	assert_eq(HalunaDresser._along(pts, 15.0), Vector2(10, 5))
	assert_eq(HalunaDresser._along(pts, 99.0), Vector2(10, 10))
	assert_eq(HalunaDresser._nearest_segment(pts, 2.0, 10, Vector2(10.2, 7.0)), 8)


## M1-RND-12: the Haluna sky binds both baked lattices (unbound, the noise reads 0) and re-renders its
## radiance cubemap time-sliced, so a moving sun or drifting offset never re-renders it in one frame.
func test_haluna_sky_binds_its_lattices_and_slices_the_cubemap() -> void:
	var env := load("res://game/levels/ch02/haluna/haluna_noon_environment.tres") as Environment
	var mat := env.sky.sky_material as ShaderMaterial
	assert_true(mat.get_shader_parameter("cloud_lattice") is Texture3D, "3D erosion lattice")
	assert_true(mat.get_shader_parameter("cloud_lattice2") is Texture2D, "2D height-field lattice")
	var lattice2 := mat.get_shader_parameter("cloud_lattice2") as Texture2D
	assert_eq(lattice2.get_width(), 512, "bake_cloud_lattice2.py SIZE = cloud_lattice2_cells")
	assert_eq(env.sky.process_mode, Sky.PROCESS_MODE_INCREMENTAL)
