extends TestCase
## M1-ARC-15: the game applies GraphicsSettings. Boot loads the saved preset and applies its global
## part, SceneRouter's ready hook applies the per-scene part (sky_detail uniforms, Environment gates,
## vegetation groups and shader families, water, weathering, Undertow and glimmer tiers) to each new
## scene, and the settings-menu API saves and re-applies. Every expected value is read from
## graphics_presets.json (and the systems' own preset maps), never restated here.

const SKY_SHADER := "res://game/shaders/environment/env_sky_cumulus.gdshader"
const WATER_MATERIAL := "res://game/levels/_tests/water/water_lagoon_material.tres"
const LAGOON_WAVES := "res://game/world/water/lagoon_waves.tres"
const WEATHERING_SHADER := "res://game/shaders/environment/env_weathering.gdshader"
const HALUNA := "res://game/levels/ch02/haluna/haluna.tscn"
const CONFIG := "user://test_m1_arc_15_settings.cfg"
const BOOT_SCRIPT := "res://game/core/boot.gd"
const ROUTER_SCRIPT := "res://game/core/scene_router.gd"
const LOW := "low"
const HIGH := "high"
## Authored fixture values (the scaled results come from the data).
const VIS_END_M := 40.0
const MULTIMESH_COUNT := 64
## Small water grid, as in test_water_surface.gd.
const WATER_CORE_M := 4.0
const WATER_CELL_M := 1.0
const WATER_OUTER_M := 16.0

var data: Dictionary

# Fixture parts.
var sky_mat: ShaderMaterial
var env: Environment
var lod: MeshInstance3D
var small: MeshInstance3D
var mm: MultiMeshInstance3D
var foliage_mat: ShaderMaterial
var water: WaterSurface
var tide: WeatheringTide
var storm: UndertowStorm

var _viewport_snapshot: Dictionary = {}
var _nodes: Array[Node] = []


func before_each() -> void:
	data = GraphicsSettings.new().data
	_snapshot_viewport()
	_write_config(LOW)
	GraphicsRuntime.config_path = CONFIG
	GraphicsRuntime.set_settings(null)
	GraphicsRuntime.armed = false


# --- Boot ---------------------------------------------------------------------------------------


func test_boot_loads_the_saved_preset_and_applies_the_global_part() -> void:
	GraphicsRuntime.boot(_viewport())
	assert_true(GraphicsRuntime.armed, "boot arms the per-scene hook")
	assert_eq(GraphicsRuntime.settings().preset_id, LOW, "the saved preset is loaded")
	_assert_viewport_matches(LOW)
	var boot_src := (load(BOOT_SCRIPT) as GDScript).source_code
	assert_true(boot_src.contains("GraphicsRuntime.boot(get_viewport())"), "boot.gd calls it in _ready")
	_done()


func test_boot_without_a_saved_file_uses_the_default_preset() -> void:
	DirAccess.remove_absolute(ProjectSettings.globalize_path(CONFIG))
	GraphicsRuntime.set_settings(null)
	GraphicsRuntime.boot(_viewport())
	assert_eq(GraphicsRuntime.settings().preset_id, str(data["default_preset"]))
	_assert_viewport_matches(str(data["default_preset"]))
	_done()


# --- Zone load (SceneRouter's hook) -------------------------------------------------------------


func test_a_zone_load_after_boot_gets_the_low_tiers() -> void:
	GraphicsRuntime.boot(_viewport())
	var root := _fixture()
	var stats := {}
	SceneRouter.attach_graphics_hook(root, stats)
	_add(root)
	assert_true(int(stats.get("graphics_ops", 0)) > 0, "the hook ran when the scene was ready")
	_assert_scene_tiers(LOW)
	var router_src := (load(ROUTER_SCRIPT) as GDScript).source_code
	assert_true(router_src.contains("attach_graphics_hook(node, stats)"), "_swap attaches the hook")
	_done()


func test_the_hook_does_nothing_before_boot() -> void:
	var root := _fixture()
	var stats := {}
	SceneRouter.attach_graphics_hook(root, stats)
	_add(root)
	assert_eq(int(stats.get("graphics_ops", -1)), 0, "disarmed: tests and captures keep authored tiers")
	assert_eq(water.quality, WaterSurface.Quality.HIGH)
	assert_eq(sky_mat.get_shader_parameter(&"cloud_steps"), null, "sky uniforms untouched")
	assert_true(env.ssr_enabled, "authored SSR untouched")
	_done()


# --- Settings menu -------------------------------------------------------------------------------


func test_selecting_a_preset_saves_and_reapplies_the_running_scene() -> void:
	GraphicsRuntime.boot(_viewport())
	var root := _fixture()
	SceneRouter.attach_graphics_hook(root, {})
	_add(root)
	_assert_scene_tiers(LOW)
	assert_true(GraphicsRuntime.select_preset(HIGH, _viewport()), "select high")
	_assert_viewport_matches(HIGH)
	_assert_scene_tiers(HIGH, false)
	var cfg := ConfigFile.new()
	assert_eq(cfg.load(CONFIG), OK)
	assert_eq(str(cfg.get_value(GraphicsSettings.CONFIG_SECTION, GraphicsSettings.KEY_PRESET, "")), HIGH, "saved")
	assert_true(GraphicsRuntime.set_override("vegetation_detail", LOW, _viewport()), "custom value")
	var veg := _level("vegetation_detail", LOW)
	assert_between(
		lod.visibility_range_end,
		VIS_END_M * float(veg["visibility_scale"]) - 0.001,
		VIS_END_M * float(veg["visibility_scale"]) + 0.001
	)
	assert_false(GraphicsRuntime.select_preset("nonsense", _viewport()), "unknown preset refused")
	_done()


# --- The real zone ---------------------------------------------------------------------------------


func test_haluna_gets_the_low_sky_water_and_weathering() -> void:
	GraphicsRuntime.boot(_viewport())
	var zone := (load(HALUNA) as PackedScene).instantiate() as HalunaZone
	var zone_env := GraphicsRuntime.scene_environment(zone)
	assert_true(zone_env != null and zone_env.sky != null, "Haluna has a sky")
	var zsky := zone_env.sky.sky_material as ShaderMaterial
	var sky_keys := _level("sky_detail", LOW).keys()
	var sky_before := {}
	for k: Variant in sky_keys:
		sky_before[k] = zsky.get_shader_parameter(StringName(str(k)))
	var env_before := _env_snapshot(zone_env)
	SceneRouter.attach_graphics_hook(zone, {})
	_add(zone)
	zone.director.auto_update = false
	zone.player.set_physics_process(false)
	for k: Variant in sky_keys:
		assert_eq(
			float(zsky.get_shader_parameter(StringName(str(k)))),
			float(_level("sky_detail", LOW)[k]),
			"Haluna sky %s" % k
		)
	var zwater := zone.get_node(^"HalunaMood/Water") as WaterSurface
	var ztide := zone.get_node(^"HalunaMood/Tide") as WeatheringTide
	assert_eq(zwater.quality, WaterSurface.quality_for_preset(LOW))
	assert_eq(
		zwater.material.shader.resource_path, WaterSurface.shader_path(WaterSurface.quality_for_preset(LOW), false)
	)
	assert_eq(ztide.quality, WeatheringTide.quality_for_preset(LOW))
	# Put the shared resources back (Environment, sky material, water and weathering materials).
	zwater.quality = WaterSurface.Quality.HIGH
	ztide.quality = WeatheringTide.Quality.HIGH
	GraphicsSettings.new().apply_tiers(zone, HIGH)
	CharacterShaderTiers.apply_to_tree(zone, CharacterShaderTiers.tier_for_preset(HIGH))
	for k: Variant in sky_keys:
		zsky.set_shader_parameter(StringName(str(k)), sky_before[k])
	_env_restore(zone_env, env_before)
	_done()


# --- Fixture -------------------------------------------------------------------------------------


## A scene with every tiered system: a cumulus sky with authored SSR and SDFGI, vegetation in the
## three vegetation groups with a foliage-family material, a sea, a weathering tide and a storm.
func _fixture() -> Node3D:
	var root := Node3D.new()
	root.name = "Arc15Fixture"
	var we := WorldEnvironment.new()
	env = Environment.new()
	env.background_mode = Environment.BG_SKY
	env.sky = Sky.new()
	sky_mat = ShaderMaterial.new()
	sky_mat.shader = load(SKY_SHADER) as Shader
	env.sky.sky_material = sky_mat
	env.ssr_enabled = true
	env.sdfgi_enabled = true
	we.environment = env
	root.add_child(we)
	var groups := data["vegetation_groups"] as Dictionary
	foliage_mat = ShaderMaterial.new()
	foliage_mat.shader = load(_family_shader("vegetation_foliage", HIGH)) as Shader
	lod = MeshInstance3D.new()
	lod.mesh = BoxMesh.new()
	lod.material_override = foliage_mat
	lod.visibility_range_end = VIS_END_M
	lod.add_to_group(StringName(str(groups["lod"])))
	root.add_child(lod)
	small = MeshInstance3D.new()
	small.mesh = BoxMesh.new()
	small.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	small.add_to_group(StringName(str(groups["small_shadows"])))
	root.add_child(small)
	mm = MultiMeshInstance3D.new()
	mm.multimesh = MultiMesh.new()
	mm.multimesh.transform_format = MultiMesh.TRANSFORM_3D
	mm.multimesh.mesh = BoxMesh.new()
	mm.multimesh.instance_count = MULTIMESH_COUNT
	mm.add_to_group(StringName(str(groups["multimesh"])))
	root.add_child(mm)
	water = WaterSurface.new()
	water.core_half_extent_m = WATER_CORE_M
	water.core_cell_m = WATER_CELL_M
	water.outer_half_extent_m = WATER_OUTER_M
	water.material = (load(WATER_MATERIAL) as ShaderMaterial).duplicate() as ShaderMaterial
	water.wave_set = load(LAGOON_WAVES) as WaveSet
	root.add_child(water)
	tide = WeatheringTide.new()
	root.add_child(tide)
	var weathering := ShaderMaterial.new()
	weathering.shader = load(WEATHERING_SHADER) as Shader
	tide.register(weathering)
	storm = UndertowStorm.new()
	root.add_child(storm)
	return root


## check_env: apply_now() targets current_scene (the test runner), whose first WorldEnvironment may be
## one an earlier test left behind, so the menu test checks the Environment part through the hook only.
func _assert_scene_tiers(preset: String, check_env: bool = true) -> void:
	var s := GraphicsSettings.new().resolve(preset)
	# Sky: every sky_detail uniform of the preset's level.
	var sky := _level("sky_detail", str(s["sky_detail"])) if check_env else {}
	for k: String in sky:
		var v: Variant = sky_mat.get_shader_parameter(StringName(k))
		assert_true(
			v != null and is_equal_approx(float(v), float(sky[k])), "%s sky %s = %s (got %s)" % [preset, k, sky[k], v]
		)
	# Environment gates (authored on in the fixture).
	if check_env:
		assert_eq(env.ssr_enabled, bool(s["ssr"]), "%s SSR gate" % preset)
		assert_eq(env.sdfgi_enabled, str(s["gi_mode"]) == GraphicsSettings.GI_SDFGI, "%s SDFGI gate" % preset)
	# Vegetation: groups and the foliage shader family.
	var veg := _level("vegetation_detail", str(s["vegetation_detail"]))
	var want_end := VIS_END_M * float(veg["visibility_scale"])
	assert_between(lod.visibility_range_end, want_end - 0.001, want_end + 0.001, "%s vegetation LOD" % preset)
	var frac := float(veg["multimesh_fraction"])
	assert_eq(
		mm.multimesh.visible_instance_count,
		-1 if frac >= 1.0 else roundi(MULTIMESH_COUNT * frac),
		"%s density" % preset
	)
	var shadows := (
		GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		if bool(veg["small_foliage_shadows"])
		else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	)
	assert_eq(small.cast_shadow, shadows, "%s small-foliage shadows" % preset)
	var veg_tier := GraphicsSettings.preset_tier(preset, "vegetation")
	assert_eq(
		foliage_mat.shader.resource_path, _family_shader("vegetation_foliage", veg_tier), "%s foliage variant" % preset
	)
	# Water, weathering, Undertow.
	assert_eq(water.quality, WaterSurface.quality_for_preset(preset), "%s water tier" % preset)
	assert_eq(
		water.material.shader.resource_path, WaterSurface.shader_path(water.quality, false), "%s water shader" % preset
	)
	assert_eq(tide.quality, WeatheringTide.quality_for_preset(preset), "%s weathering tier" % preset)
	assert_eq(storm.get_quality(), preset, "%s Undertow tier" % preset)


# --- Helpers -------------------------------------------------------------------------------------


func _level(key: String, level: String) -> Dictionary:
	return ((data["levels"] as Dictionary)[key] as Dictionary)[level] as Dictionary


func _family_shader(family: String, tier: String) -> String:
	var f := (data["shader_families"] as Dictionary)[family] as Dictionary
	return str(f.get(tier, f[GraphicsSettings.FAMILY_FALLBACK_TIER]))


func _assert_viewport_matches(preset: String) -> void:
	for op in GraphicsSettings.new().plan(preset):
		if op["target"] == GraphicsSettings.TARGET_VIEWPORT:
			var got: Variant = _viewport().get(str(op["name"]))
			var want: Variant = op["value"]
			var same: bool = is_equal_approx(float(got), float(want)) if want is float else got == want
			assert_true(same, "%s viewport %s = %s (got %s)" % [preset, op["name"], want, got])


func _viewport() -> Viewport:
	return _host().get_viewport()


func _host() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _add(n: Node) -> void:
	_host().add_child(n)
	_nodes.append(n)


func _write_config(preset: String) -> void:
	var gs := GraphicsSettings.new()
	gs.set_preset(preset)
	gs.save_config(CONFIG)


func _snapshot_viewport() -> void:
	_viewport_snapshot.clear()
	for op in GraphicsSettings.new().plan():
		if op["target"] == GraphicsSettings.TARGET_VIEWPORT:
			_viewport_snapshot[str(op["name"])] = _viewport().get(str(op["name"]))


## Every Environment property the plan touches, plus whether its authored-value meta existed.
func _env_snapshot(e: Environment) -> Dictionary:
	var out := {}
	for op in GraphicsSettings.new().plan():
		if op["target"] == GraphicsSettings.TARGET_ENVIRONMENT:
			var name := str(op["name"])
			out[name] = [e.get(name), e.has_meta(StringName(GraphicsSettings.AUTHORED_META_PREFIX + name))]
	return out


func _env_restore(e: Environment, snap: Dictionary) -> void:
	for name: String in snap:
		e.set(name, (snap[name] as Array)[0])
		var meta := StringName(GraphicsSettings.AUTHORED_META_PREFIX + name)
		if not bool((snap[name] as Array)[1]) and e.has_meta(meta):
			e.remove_meta(meta)


func _done() -> void:
	for n in _nodes:
		if is_instance_valid(n):
			if n.get_parent() != null:
				n.get_parent().remove_child(n)
			n.free()
	_nodes.clear()
	for name: String in _viewport_snapshot:
		_viewport().set(name, _viewport_snapshot[name])
	GraphicsRuntime.armed = false
	GraphicsRuntime.set_settings(null)
	GraphicsRuntime.config_path = GraphicsSettings.CONFIG_PATH
	DirAccess.remove_absolute(ProjectSettings.globalize_path(CONFIG))
