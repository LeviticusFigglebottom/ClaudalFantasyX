extends TestCase
## M1-RND-05: graphics presets data, the pure plan() mapping, the override layer and persistence.

const TEST_CFG := "user://test_graphics_settings.cfg"
const EXPECTED_PRESETS: Array[String] = ["low", "medium", "high", "ultra"]

var gs: GraphicsSettings


func before_each() -> void:
	gs = GraphicsSettings.new()


# --- Data integrity ----------------------------------------------------------------------------


func test_data_defines_four_presets_in_order() -> void:
	assert_eq(Array(gs.preset_ids()), Array(EXPECTED_PRESETS))
	assert_eq(str(gs.data["default_preset"]), "high")
	assert_eq(gs.preset_id, "high")


func test_every_preset_is_complete_and_valid() -> void:
	var keys := (gs.data["settings"] as Dictionary).keys()
	for id in gs.preset_ids():
		var s := gs.preset_settings(id)
		assert_eq(s.size(), keys.size(), "preset %s key count" % id)
		for key: String in keys:
			assert_true(s.has(key), "preset %s lacks %s" % [id, key])
			assert_true(gs.is_valid_value(key, s.get(key)), "preset %s: bad %s=%s" % [id, key, str(s.get(key))])


func test_every_option_maps_to_a_real_engine_constant() -> void:
	var settings := gs.data["settings"] as Dictionary
	var enums := gs.data["enums"] as Dictionary
	var levels := gs.data["levels"] as Dictionary
	for key: String in enums:
		for option: Variant in (settings[key] as Dictionary)["options"]:
			assert_true((enums[key] as Dictionary).has(option), "enum %s lacks option %s" % [key, option])
		for qualified: Variant in (enums[key] as Dictionary).values():
			_assert_constant(str(qualified))
	for key: String in levels:
		for option: Variant in (settings[key] as Dictionary)["options"]:
			if str(option) != GraphicsSettings.QUALITY_OFF:
				assert_true((levels[key] as Dictionary).has(option), "levels %s lacks %s" % [key, option])
		for row: Variant in (levels[key] as Dictionary).values():
			for v: Variant in (row as Dictionary).values():
				if v is String and str(v).contains("."):
					_assert_constant(str(v))


func test_planned_engine_api_names_exist_in_this_godot() -> void:
	# Every preset, plus every single option swapped into the default preset.
	var variants: Array = Array(gs.preset_ids())
	for key: String in gs.data["settings"]:
		for option: Variant in gs.setting_options(key):
			variants.append({key: option})
	var viewport_props := _property_names("Viewport")
	var env_props := _property_names("Environment")
	var node_props := _property_names("VoxelGI")
	for v: Variant in variants:
		for op in gs.plan(v):
			var name := str(op["name"])
			match op["target"]:
				GraphicsSettings.TARGET_VIEWPORT:
					assert_true(viewport_props.has(name), "Viewport.%s missing" % name)
				GraphicsSettings.TARGET_ENVIRONMENT:
					assert_true(env_props.has(name), "Environment.%s missing" % name)
				GraphicsSettings.TARGET_GROUP:
					assert_true(node_props.has(name), "VoxelGI.%s missing" % name)
				GraphicsSettings.TARGET_SERVER:
					assert_true(ClassDB.class_has_method("RenderingServer", name), "RenderingServer.%s missing" % name)
					assert_eq((op["args"] as Array).size(), _arg_count("RenderingServer", name), "args of %s" % name)
				_:
					fail("unknown target %s" % str(op["target"]))


# --- plan() mapping ----------------------------------------------------------------------------


func test_low_preset_mapping() -> void:
	var ops := gs.plan("low")
	assert_eq(_value(ops, "environment", "sdfgi_enabled"), false)
	assert_eq(_value(ops, "group", "visible"), false, "VoxelGI disallowed when GI is off")
	assert_eq(_value(ops, "environment", "ssr_enabled"), false)
	assert_eq(_value(ops, "environment", "ssil_enabled"), false)
	assert_eq(_value(ops, "environment", "ssao_enabled"), true)
	assert_eq(_value(ops, "environment", "volumetric_fog_enabled"), true)
	assert_eq(_args(ops, "environment_set_volumetric_fog_volume_size"), [64, 32])
	assert_eq(_args(ops, "environment_set_volumetric_fog_filter_active"), [false])
	assert_eq(_args(ops, "directional_shadow_atlas_set_size"), [2048, true])
	assert_eq(_value(ops, "viewport", "positional_shadow_atlas_size"), 2048)
	assert_eq(_args(ops, "directional_soft_shadow_filter_set_quality"), [RenderingServer.SHADOW_QUALITY_SOFT_VERY_LOW])
	assert_eq((_args(ops, "environment_set_ssao_quality") as Array)[0], RenderingServer.ENV_SSAO_QUALITY_VERY_LOW)
	assert_eq(_args(ops, "environment_set_ssil_quality"), null, "SSIL off issues no quality call")
	assert_eq(_value(ops, "viewport", "scaling_3d_mode"), Viewport.SCALING_3D_MODE_FSR)
	assert_true(is_equal_approx(float(_value(ops, "viewport", "scaling_3d_scale")), 0.77))
	assert_eq(_value(ops, "viewport", "screen_space_aa"), Viewport.SCREEN_SPACE_AA_FXAA)
	assert_eq(_value(ops, "viewport", "msaa_3d"), Viewport.MSAA_DISABLED)
	assert_eq(_value(ops, "viewport", "use_taa"), false)
	assert_eq(_value(ops, "viewport", "anisotropic_filtering_level"), Viewport.ANISOTROPY_4X)
	assert_eq(_value(ops, "viewport", "mesh_lod_threshold"), 2.0)


func test_ultra_preset_mapping() -> void:
	var ops := gs.plan("ultra")
	assert_eq(_value(ops, "environment", "sdfgi_enabled"), true)
	assert_eq(_value(ops, "environment", "sdfgi_cascades"), 8)
	assert_eq(_value(ops, "environment", "sdfgi_use_occlusion"), true)
	assert_eq(_args(ops, "environment_set_sdfgi_ray_count"), [RenderingServer.ENV_SDFGI_RAY_COUNT_64])
	assert_eq(_args(ops, "gi_set_use_half_resolution"), [false])
	assert_eq(_args(ops, "voxel_gi_set_quality"), [RenderingServer.VOXEL_GI_QUALITY_HIGH])
	assert_eq(_args(ops, "directional_shadow_atlas_set_size"), [8192, true])
	assert_eq(_value(ops, "environment", "ssr_max_steps"), 128)
	assert_eq(_args(ops, "environment_set_ssr_roughness_quality"), [RenderingServer.ENV_SSR_ROUGHNESS_QUALITY_HIGH])
	var ssil: Array = _args(ops, "environment_set_ssil_quality")
	assert_eq(ssil[0], RenderingServer.ENV_SSIL_QUALITY_HIGH)
	assert_eq(ssil[1], false, "full-size SSIL on ultra")
	assert_eq(_value(ops, "viewport", "scaling_3d_mode"), Viewport.SCALING_3D_MODE_BILINEAR)
	assert_eq(_value(ops, "viewport", "scaling_3d_scale"), 1.0)
	assert_eq(_value(ops, "viewport", "use_taa"), true)


func test_medium_allows_voxel_gi_but_not_sdfgi() -> void:
	var ops := gs.plan("medium")
	assert_eq(_value(ops, "environment", "sdfgi_enabled"), false)
	assert_eq(_value(ops, "group", "visible"), true)
	assert_eq(_group(ops), str(gs.data["voxel_gi_group"]))


func test_aa_and_upscaler_mapping() -> void:
	var high := gs.plan("high")
	assert_eq(_value(high, "viewport", "scaling_3d_mode"), Viewport.SCALING_3D_MODE_FSR2)
	assert_eq(_value(high, "viewport", "use_taa"), false, "FSR2 replaces TAA")
	var native := gs.plan({"preset": "high", "scaling_mode": "bilinear"})
	assert_eq(_value(native, "viewport", "use_taa"), true)
	assert_eq(_value(gs.plan({"aa": "msaa_2x"}), "viewport", "msaa_3d"), Viewport.MSAA_2X)
	assert_eq(_value(gs.plan({"aa": "msaa_4x"}), "viewport", "msaa_3d"), Viewport.MSAA_4X)
	assert_eq(_value(gs.plan({"aa": "none"}), "viewport", "screen_space_aa"), Viewport.SCREEN_SPACE_AA_DISABLED)
	assert_eq(_value(gs.plan({"aa": "smaa"}), "viewport", "screen_space_aa"), Viewport.SCREEN_SPACE_AA_SMAA)


func test_plan_is_pure_and_deterministic() -> void:
	gs.set_override("ssr", false)
	var before_overrides := gs.overrides.duplicate()
	var a := gs.plan("low")
	var b := gs.plan("low")
	assert_eq(a, b)
	assert_eq(gs.preset_id, "high")
	assert_eq(gs.overrides, before_overrides)


# --- Override layer ----------------------------------------------------------------------------


func test_override_layer_on_top_of_preset() -> void:
	assert_false(gs.is_custom())
	assert_true(gs.set_override("ssr", false))
	assert_true(gs.set_override("shadow_atlas_size", 8192.0), "JSON-style float accepted for int setting")
	assert_true(gs.is_custom())
	var s := gs.resolve()
	assert_eq(s["ssr"], false)
	assert_eq(s["shadow_atlas_size"], 8192)
	assert_eq(s["aa"], gs.preset_settings("high")["aa"], "untouched keys come from the preset")
	assert_eq(_value(gs.plan(), "environment", "ssr_enabled"), false)


func test_override_equal_to_preset_is_dropped() -> void:
	assert_true(gs.set_override("aa", "taa"))
	assert_false(gs.is_custom())
	gs.set_override("aa", "fxaa")
	gs.clear_override("aa")
	assert_false(gs.is_custom())


func test_invalid_overrides_are_rejected() -> void:
	assert_false(gs.set_override("ssr_max_steps", 999))
	assert_false(gs.set_override("ssr", "yes"))
	assert_false(gs.set_override("aa", "msaa_16x"))
	assert_false(gs.set_override("not_a_setting", true))
	assert_false(gs.is_custom())


func test_set_preset_clears_overrides_unless_kept() -> void:
	gs.set_override("ssr", false)
	assert_true(gs.set_preset("low"))
	assert_false(gs.is_custom())
	gs.set_override("aa", "taa")
	assert_true(gs.set_preset("medium", true))
	assert_false(gs.is_custom(), "override now equals the new preset's value")
	assert_false(gs.set_preset("cinematic"))
	assert_eq(gs.preset_id, "medium")


func test_resolve_accepts_names_and_dicts() -> void:
	assert_eq(gs.resolve("low"), gs.preset_settings("low"))
	assert_eq(gs.resolve(&"ultra"), gs.preset_settings("ultra"))
	var d := gs.resolve({"preset": "ultra", "aa": "fxaa", "bogus": 1})
	assert_eq(d["aa"], "fxaa")
	assert_eq(d["ssr_max_steps"], 128)
	assert_false(d.has("bogus"))
	assert_eq(gs.resolve("nope"), gs.preset_settings("high"), "unknown preset falls back to default")


# --- execute() on real engine objects (headless) -----------------------------------------------


func test_apply_sets_viewport_and_gates_environment() -> void:
	var vp := SubViewport.new()
	var env := Environment.new()
	env.ssao_enabled = true
	env.volumetric_fog_enabled = true
	env.sdfgi_enabled = true
	env.ssr_enabled = false
	gs.apply("ultra", vp, env)
	assert_eq(vp.msaa_3d, Viewport.MSAA_DISABLED)
	assert_eq(vp.use_taa, true)
	assert_eq(vp.positional_shadow_atlas_size, 8192)
	assert_eq(vp.anisotropic_filtering_level, Viewport.ANISOTROPY_16X)
	assert_eq(env.sdfgi_cascades, 8)
	assert_eq(env.sdfgi_enabled, true)
	assert_eq(env.ssr_enabled, false, "a gate never enables what the zone did not author")
	gs.apply("low", vp, env)
	assert_eq(env.sdfgi_enabled, false)
	assert_eq(env.ssil_enabled, false)
	assert_eq(vp.scaling_3d_mode, Viewport.SCALING_3D_MODE_FSR)
	assert_eq(vp.screen_space_aa, Viewport.SCREEN_SPACE_AA_FXAA)
	gs.apply("ultra", vp, env)
	assert_eq(env.sdfgi_enabled, true, "authored value restored when the setting allows it again")
	GraphicsSettings.set_authored(env, "ssr_enabled", true)
	gs.apply("ultra", vp, env)
	assert_eq(env.ssr_enabled, true)
	vp.free()


func test_apply_gates_voxel_gi_nodes_in_group() -> void:
	# The tree root is busy while the runner scene is readying, so attach under the running scene.
	var host := (Engine.get_main_loop() as SceneTree).current_scene
	var vp := SubViewport.new()
	host.add_child(vp)
	var authored_on := VoxelGI.new()
	var authored_off := VoxelGI.new()
	authored_off.visible = false
	for n: VoxelGI in [authored_on, authored_off]:
		n.add_to_group(StringName(str(gs.data["voxel_gi_group"])))
		vp.add_child(n)
	gs.apply("low", vp, null)
	assert_false(authored_on.visible)
	gs.apply("medium", vp, null)
	assert_true(authored_on.visible)
	assert_false(authored_off.visible)
	vp.free()


func test_null_targets_only_run_rendering_server_ops() -> void:
	var ops := gs.plan("high")
	var server_ops := ops.filter(func(op: Dictionary) -> bool: return op["target"] == GraphicsSettings.TARGET_SERVER)
	assert_eq(GraphicsSettings.execute(ops, null, null), server_ops.size())


# --- Persistence -------------------------------------------------------------------------------


func test_config_round_trip_preserves_other_sections() -> void:
	var other := ConfigFile.new()
	other.set_value("audio", "music_volume", 0.5)
	other.save(TEST_CFG)
	gs.set_preset("medium")
	gs.set_override("ssil_quality", "low")
	gs.set_override("render_scale", 1.0)
	assert_eq(gs.save_config(TEST_CFG), OK)
	var back := GraphicsSettings.new()
	assert_eq(back.load_config(TEST_CFG), OK)
	assert_eq(back.preset_id, "medium")
	assert_eq(back.overrides, gs.overrides)
	assert_eq(back.resolve(), gs.resolve())
	var check := ConfigFile.new()
	check.load(TEST_CFG)
	assert_eq(check.get_value("audio", "music_volume"), 0.5)
	DirAccess.remove_absolute(TEST_CFG)


func test_load_config_drops_invalid_entries_and_missing_file_errors() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value(GraphicsSettings.CONFIG_SECTION, GraphicsSettings.KEY_PRESET, "bogus")
	cfg.set_value(GraphicsSettings.CONFIG_SECTION, GraphicsSettings.KEY_OVERRIDES, {"ssr_max_steps": 999, "aa": "fxaa"})
	cfg.save(TEST_CFG)
	assert_eq(gs.load_config(TEST_CFG), OK)
	assert_eq(gs.preset_id, "high")
	assert_eq(gs.overrides, {"aa": "fxaa"})
	DirAccess.remove_absolute(TEST_CFG)
	assert_ne(gs.load_config("user://definitely_missing_settings.cfg"), OK)
	assert_eq(gs.preset_id, "high")


# --- helpers -----------------------------------------------------------------------------------


func _value(ops: Array[Dictionary], target: String, name: String) -> Variant:
	for op in ops:
		if str(op["target"]) == target and str(op["name"]) == name:
			return op["value"]
	fail("no %s op for %s" % [target, name])
	return null


func _args(ops: Array[Dictionary], method: String) -> Variant:
	for op in ops:
		if op["target"] == GraphicsSettings.TARGET_SERVER and str(op["name"]) == method:
			return op["args"]
	return null


func _group(ops: Array[Dictionary]) -> String:
	for op in ops:
		if op["target"] == GraphicsSettings.TARGET_GROUP:
			return str(op["group"])
	return ""


func _assert_constant(qualified: String) -> void:
	var parts := qualified.split(".")
	assert_eq(parts.size(), 2, "constant %s" % qualified)
	assert_true(ClassDB.class_has_integer_constant(parts[0], parts[-1]), "%s is not a 4.6 constant" % qualified)


func _property_names(cls: String) -> Array[String]:
	var out: Array[String] = []
	for p in ClassDB.class_get_property_list(cls):
		out.append(str(p["name"]))
	return out


func _arg_count(cls: String, method: String) -> int:
	for m in ClassDB.class_get_method_list(cls):
		if str(m["name"]) == method:
			return (m["args"] as Array).size()
	return -1


# --- System tiers and shader families (M1-RND-07) ----------------------------------------------


func test_every_preset_has_system_tiers() -> void:
	var gs := GraphicsSettings.new()
	for id in gs.preset_ids():
		for system in ["water", "vegetation", "weathering"]:
			assert_ne(GraphicsSettings.preset_tier(id, system), "", "%s has a %s tier" % [id, system])
	assert_eq(GraphicsSettings.preset_tier("low", "vegetation"), "low", "Low maps to vegetation_foliage_low")
	assert_eq(GraphicsSettings.preset_tier("nonsense", "water"), "")


func test_shader_family_variants_exist_and_share_uniforms() -> void:
	var gs := GraphicsSettings.new()
	var families := gs.data["shader_families"] as Dictionary
	for fam: String in families:
		if fam.begins_with("_"):
			continue
		var f := families[fam] as Dictionary
		var high := load(str(f["high"])) as Shader
		assert_true(high != null, "%s high variant loads" % fam)
		var high_names := high.get_shader_uniform_list().map(func(u: Dictionary) -> String: return str(u["name"]))
		for tier: String in f:
			if tier == "system" or tier == "high":
				continue
			var sh := load(str(f[tier])) as Shader
			assert_true(sh != null, "%s %s variant loads" % [fam, tier])
			for u: Dictionary in sh.get_shader_uniform_list():
				assert_true(high_names.has(str(u["name"])), "%s %s uniform %s exists on high" % [fam, tier, u["name"]])


func test_apply_tiers_swaps_family_materials_both_ways() -> void:
	var gs := GraphicsSettings.new()
	var f := gs.data["shader_families"]["vegetation_foliage"] as Dictionary
	var mat := ShaderMaterial.new()
	mat.shader = load(str(f["high"])) as Shader
	var root := Node3D.new()
	var a := MeshInstance3D.new()
	a.mesh = QuadMesh.new()
	a.material_override = mat
	root.add_child(a)
	var b := MultiMeshInstance3D.new()
	b.multimesh = MultiMesh.new()
	var mesh := QuadMesh.new()
	mesh.material = mat
	b.multimesh.mesh = mesh
	root.add_child(b)
	assert_eq(gs.apply_tiers(root, "low"), 1, "one shared material swapped once")
	assert_eq(mat.shader.resource_path, str(f["low"]))
	assert_eq(gs.apply_tiers(root, "low"), 0, "idempotent")
	assert_eq(gs.apply_tiers(root, "high"), 1)
	assert_eq(mat.shader.resource_path, str(f["high"]))
	root.free()
