extends TestCase
## M1-RND-03: UndertowState (API ranges, clock, tiers, deterministic lightning, shape mirrors),
## UndertowMeshBuilder, and the UndertowStorm node (placement, tiers, parameter pushing, water hookup).

const EPS := 1e-4

var _nodes: Array[Node] = []


func _root() -> Node:
	return (Engine.get_main_loop() as SceneTree).current_scene


func _add(n: Node) -> Node:
	_root().add_child(n)
	_nodes.append(n)
	return n


func _free_nodes() -> void:
	for n in _nodes:
		if is_instance_valid(n):
			n.free()
	_nodes.clear()


# --- UndertowState -------------------------------------------------------------------------------


func test_api_values_default_and_clamp_to_data_ranges() -> void:
	var s := UndertowState.new()
	for key in ["intensity", "rotation_rad_s", "wound_intensity", "approach_distance_m", "time_scale"]:
		var r := s.range_of(key)
		assert_true(r.y > r.x, "%s has a range" % key)
		assert_between(float(s.get(key)), r.x, r.y)
		assert_eq(float(s.get(key)), s.default_of(key), "%s default" % key)
		s.set(key, r.y + 1000.0)
		assert_eq(float(s.get(key)), r.y, "%s clamps high" % key)
		s.set(key, r.x - 1000.0)
		assert_eq(float(s.get(key)), r.x, "%s clamps low" % key)


func test_clock_advances_with_time_scale() -> void:
	var s := UndertowState.new()
	s.time_s = 10.0
	s.time_scale = 2.0
	s.advance(0.5)
	assert_between(s.time_s, 11.0 - EPS, 11.0 + EPS)
	s.time_scale = 0.0
	s.advance(5.0)
	assert_between(s.time_s, 11.0 - EPS, 11.0 + EPS, "time_scale 0 pauses (cutscene hold)")
	assert_eq(s.dynamic_parameters()["storm_time_s"], s.time_s)


func test_quality_plans() -> void:
	var s := UndertowState.new()
	assert_false(s.set_quality("nonsense"))
	var low := s.quality_plan("low")
	assert_eq(low["body"], UndertowState.BODY_SHELLS, "Low draws shells, no raymarch")
	assert_eq(low["body_shader"], "")
	assert_true((low["shell_fractions"] as Array).size() >= 2, "several shells for parallax")
	assert_true(bool(low["shell_canopy"]))
	var steps := 0
	for id in ["medium", "high", "ultra"]:
		var p := s.quality_plan(id)
		assert_eq(p["body"], UndertowState.BODY_RAYMARCH, id)
		assert_true(ResourceLoader.exists(str(p["body_shader"])), "%s shader exists" % id)
		assert_true(int(p["march_steps"]) > steps, "%s marches more than the tier below" % id)
		steps = int(p["march_steps"])
		assert_eq((p["shell_fractions"] as Array).size(), 0)
	assert_true(s.set_quality("medium"))
	assert_eq(s.get_quality(), "medium")
	assert_eq(s.static_parameters()["march_steps"], s.quality_plan("medium")["march_steps"])


## M1-RND-10 tier parameters: curl_reuse within the shader's range, march_steps within each
## variant's compiled cap, and temporal jitter only on tiers whose preset resolves it temporally.
func test_tier_perf_params_parse_and_validate() -> void:
	var s := UndertowState.new()
	var presets := {}
	var gp := JSON.parse_string(FileAccess.get_file_as_string(GraphicsSettings.DATA_PATH)) as Dictionary
	var temporal_modes := (gp["rules"] as Dictionary)["temporal_upscaler_modes"] as Array
	for p: Dictionary in gp["presets"]:
		presets[p["id"]] = p["settings"]
	for id in UndertowState.QUALITY_IDS:
		var plan := s.quality_plan(id)
		var reuse := int(plan["curl_reuse"])
		assert_true(reuse >= 1 and reuse <= 8, "%s curl_reuse in the shader's hint range" % id)
		assert_true(plan["temporal_jitter"] is bool, "%s temporal_jitter is a bool" % id)
		var gs := presets[id] as Dictionary
		var temporal_aa := str(gs["aa"]) == "taa" or temporal_modes.has(str(gs["scaling_mode"]))
		if bool(plan["temporal_jitter"]):
			assert_true(temporal_aa, "%s jitters only where the preset's AA is temporal" % id)
		if str(plan["body"]) != UndertowState.BODY_RAYMARCH:
			continue
		var src := FileAccess.get_file_as_string(str(plan["body_shader"]))
		var cap := RegEx.create_from_string("#define UNDERTOW_MAX_STEPS (\\d+)").search(src)
		assert_true(cap != null, "%s variant declares its step cap" % id)
		assert_true(int(plan["march_steps"]) <= int(cap.get_string(1)), "%s march_steps <= compiled cap" % id)
	assert_true(s.set_quality("high"))
	assert_eq(s.static_parameters()["curl_reuse"], s.quality_plan("high")["curl_reuse"])


## M1-RND-11: tier parameters are clamped to the shader's ranges at runtime, both ways.
func test_tier_params_are_clamped_both_ways() -> void:
	var cfg := UndertowState.load_config()
	var high := (cfg["quality"] as Dictionary)["high"] as Dictionary
	high["curl_reuse"] = 20
	high["march_steps"] = 999
	var s := UndertowState.new(cfg)
	var plan := s.quality_plan("high")
	assert_eq(plan["curl_reuse"], UndertowState.MAX_CURL_REUSE)
	assert_eq(plan["march_steps"], UndertowState.MAX_MARCH_STEPS)
	high["curl_reuse"] = -3
	high["march_steps"] = -5
	plan = s.quality_plan("high")
	assert_eq(plan["curl_reuse"], 1)
	assert_eq(plan["march_steps"], 0)
	var body := FileAccess.get_file_as_string("res://game/shaders/undertow/undertow_body.gdshaderinc")
	assert_true(body.contains("march_steps : hint_range(4, %d)" % UndertowState.MAX_MARCH_STEPS), "march cap = hint")
	assert_true(body.contains("curl_reuse : hint_range(1, %d)" % UndertowState.MAX_CURL_REUSE), "reuse cap = hint")


## M1-RND-11: without temporal AA the jitter would crawl, so the phase stays 0.
func test_jitter_needs_temporal_aa() -> void:
	var s := UndertowState.new()
	assert_true(s.set_quality("high"))
	s.advance(1.0 / 60.0)
	assert_ne(s.jitter_phase(), 0.0, "High with TAA rotates the phase")
	s.temporal_aa = false
	assert_eq(s.jitter_phase(), 0.0, "High with FXAA or no AA: a static pattern")
	var vp := SubViewport.new()
	vp.use_taa = false
	vp.scaling_3d_mode = Viewport.SCALING_3D_MODE_BILINEAR
	assert_false(UndertowStorm.viewport_is_temporal(vp), "FXAA / none")
	vp.use_taa = true
	assert_true(UndertowStorm.viewport_is_temporal(vp), "TAA")
	vp.use_taa = false
	vp.scaling_3d_mode = Viewport.SCALING_3D_MODE_FSR2
	assert_true(UndertowStorm.viewport_is_temporal(vp), "FSR2 accumulates too")
	# M1-RND-15: MetalFX temporal (macOS) is listed beside FSR2 so the gate never drops jitter for it.
	assert_true(UndertowStorm.TEMPORAL_SCALING_MODES.has(Viewport.SCALING_3D_MODE_METALFX_TEMPORAL))
	assert_false(UndertowStorm.TEMPORAL_SCALING_MODES.has(Viewport.SCALING_3D_MODE_METALFX_SPATIAL))
	vp.free()


func test_jitter_phase_advances_only_with_the_clock() -> void:
	var s := UndertowState.new()
	assert_true(s.set_quality("low"))
	s.advance(0.1)
	assert_eq(s.jitter_phase(), 0.0, "no temporal jitter on a tier without it")
	assert_true(s.set_quality("high"))
	assert_true(bool(s.quality_plan()["temporal_jitter"]), "High resolves its steps temporally")
	var seen := {}
	for i in 8:
		var phase := s.jitter_phase()
		assert_true(phase >= 0.0 and phase < 1.0)
		assert_eq(s.dynamic_parameters()["jitter_phase"], phase)
		seen[snappedf(phase, 0.001)] = true
		s.advance(1.0 / 60.0)
	assert_eq(seen.size(), 8, "eight frames, eight distinct step phases")
	var held := s.jitter_phase()
	assert_eq(s.jitter_phase(), held, "a held storm (no advance) keeps its pattern")


func test_lightning_is_deterministic_and_bounded() -> void:
	var a := UndertowState.new()
	var b := UndertowState.new()
	var lt := a.config["lightning"] as Dictionary
	var peak := 1.0 + float(lt["restrike_gain"])
	var lit := 0
	for i in 400:
		var t := i * 0.37
		var la := a.flash_levels(t)
		assert_eq(la, b.flash_levels(t), "same schedule for the same time")
		for v in la:
			assert_between(v, 0.0, peak)
			if v > 0.0:
				lit += 1
	assert_true(lit > 0, "some flashes in 150 s")
	a.intensity = 0.0
	for i in 200:
		var t := i * 0.37
		for site in a.flash_site_count():
			assert_eq(a.flash_level(site, t), 0.0, "a sleeping storm does not flash")


func test_forced_flash_and_sites() -> void:
	var s := UndertowState.new()
	s.intensity = 0.0
	assert_false(s.force_flash(-1))
	assert_false(s.force_flash(UndertowState.MAX_FLASHES))
	assert_true(s.force_flash(1, 20.0))
	assert_between(s.flash_level(1, 20.0), 1.0 - EPS, 1.0 + EPS, "stroke at full level on its start")
	assert_eq(s.flash_level(1, 19.9), 0.0)
	assert_eq(s.flash_level(1, 20.0 + float((s.config["lightning"] as Dictionary)["duration_s"])), 0.0)
	s.clear_forced_flashes()
	assert_eq(s.flash_level(1, 20.0), 0.0)
	s.intensity = 1.0
	s.force_flash(0, 3.0)
	var sites := s.flash_sites(3.0)
	assert_eq(sites.size(), UndertowState.MAX_FLASHES)
	var lt := s.config["lightning"] as Dictionary
	for i in s.flash_site_count():
		var v := sites[i]
		var h := v.y / s.height_now()
		assert_between(h, float(lt["height_min"]) - EPS, float(lt["height_max"]) + EPS)
		var r := Vector2(v.x, v.z).length()
		assert_between(r, s.eye_radius(h), s.wall_radius(h), "site %d inside the eyewall" % i)
	assert_true(sites[0].w > 0.0)


func test_sea_profile_and_rotation_mirrors() -> void:
	var s := UndertowState.new()
	var sea := s.config["sea"] as Dictionary
	assert_between(s.sea_height(0.0), -float(sea["funnel_depth_m"]) - 1.0, -float(sea["funnel_depth_m"]) + 1.0)
	assert_true(s.sea_height(float(sea["lip_radius_m"])) > 0.0, "surge lip heaped against the wall")
	assert_between(s.sea_height(float(sea["radius_m"])), -0.5, 0.5, "flat at the rim")
	var deep := s.sea_height(0.0)
	s.intensity = 0.5
	assert_between(s.sea_height(0.0), deep * 0.5 - EPS, deep * 0.5 + EPS, "the funnel deepens with intensity")
	var eye := float((s.config["shape"] as Dictionary)["eye_radius_m"])
	assert_true(s.omega(eye) > s.omega(eye * 4.0), "differential rotation: fastest at the eyewall")
	assert_between(s.omega(eye), s.rotation_rad_s - EPS, s.rotation_rad_s + EPS)
	assert_true(s.wall_radius(0.5) > s.eye_radius(0.5))
	assert_true(s.eye_radius(1.0) > s.eye_radius(0.0), "the eye flares upward")
	assert_true(s.bound_radius() >= s.wall_radius(1.0))


func test_hash_is_stable_and_uniform_enough() -> void:
	var sum := 0.0
	for i in 1000:
		var v := UndertowState.hash01(i % 4, i, 3)
		assert_between(v, 0.0, 1.0)
		sum += v
	assert_between(sum / 1000.0, 0.45, 0.55)
	assert_eq(UndertowState.hash01(2, -7, 1), UndertowState.hash01(2, -7, 1))
	assert_ne(UndertowState.hash01(2, 7, 1), UndertowState.hash01(2, 8, 1))


# --- UndertowMeshBuilder -------------------------------------------------------------------------


func test_sea_disc_topology_and_winding() -> void:
	var rings := 6
	var seg := 12
	var m := UndertowMeshBuilder.sea_disc(100.0, rings, seg, 2.0)
	var arr := m.surface_get_arrays(0)
	var v := arr[Mesh.ARRAY_VERTEX] as PackedVector3Array
	var idx := arr[Mesh.ARRAY_INDEX] as PackedInt32Array
	assert_eq(v.size(), 1 + rings * seg)
	assert_eq(idx.size(), 3 * seg + 6 * seg * (rings - 1))
	assert_between(Vector2(v[v.size() - 1].x, v[v.size() - 1].z).length(), 100.0 - EPS, 100.0 + EPS)
	assert_true(Vector2(v[1].x, v[1].z).length() < 100.0 / rings, "rings packed toward the throat")
	for t in range(0, idx.size(), 3):
		var n := (v[idx[t + 1]] - v[idx[t]]).cross(v[idx[t + 2]] - v[idx[t]])
		assert_true(n.y < 0.0, "triangle %d wound like WaterMeshBuilder (front face up)" % (t / 3))


func test_unit_tube_and_proxy() -> void:
	var tube := UndertowMeshBuilder.unit_tube(8, 16)
	assert_eq(tube.height, UndertowMeshBuilder.UNIT_HEIGHT)
	assert_false(tube.cap_top or tube.cap_bottom, "open: shells and curtains have no caps")
	var proxy := UndertowMeshBuilder.proxy(500.0, 900.0, 24)
	assert_eq(proxy.top_radius, 500.0)
	assert_true(proxy.cap_top and proxy.cap_bottom, "closed: rays from inside still hit a back face")


# --- UndertowStorm -------------------------------------------------------------------------------


func test_storm_places_itself_and_builds_the_high_tier() -> void:
	var storm := UndertowStorm.new()
	storm.quality = "high"
	storm.position = Vector3(100.0, 0.0, 50.0)
	storm.approach_azimuth_deg = 90.0
	storm.approach_distance_m = 2000.0
	_add(storm)
	var c := storm.storm_center()
	assert_between(c.x, 2100.0 - EPS, 2100.0 + EPS, "azimuth 90 = east = +X")
	assert_between(c.z, 50.0 - EPS, 50.0 + EPS)
	assert_true(storm.visuals.top_level, "visuals ignore the node's transform")
	assert_true(storm.visuals.global_position.is_equal_approx(c))
	assert_true(storm.sea != null and storm.lid != null and storm.body != null and storm.body.visible)
	assert_eq(storm.body_material.shader.resource_path, storm.state.quality_plan("high")["body_shader"])
	var prio := storm.state.config["render_priority"] as Dictionary
	assert_eq(storm.body_material.render_priority, int(prio["body"]))
	assert_true(storm.lid_material.render_priority < 0, "the lid draws before the water")
	var noise := storm.body_material.get_shader_parameter(&"noise_tex") as Texture3D
	assert_true(noise != null, "the body gets the baked noise lattice")
	assert_eq(storm.body_material.get_shader_parameter(&"curl_reuse"), storm.state.quality_plan("high")["curl_reuse"])
	assert_eq(storm.sea_material.get_shader_parameter(&"storm_center"), c)
	storm.approach_distance_m = 3000.0
	assert_true(storm.visuals.global_position.is_equal_approx(storm.storm_center()), "approach moves it")
	var sea_y := storm.sea_height_at(Vector2(c.x, c.z) + Vector2(1.0, 0.0))
	assert_true(sea_y < -10.0, "the eye is a funnel below sea level")
	_free_nodes()


## M1-RND-09: sea level comes from the zone water or sea_level_y, never the node's Y.
func test_sea_level_is_decoupled_from_the_node_height() -> void:
	var storm := UndertowStorm.new()
	storm.position = Vector3(0.0, 12.0, 0.0)
	_add(storm)
	assert_between(storm.storm_center().y, -EPS, EPS, "a marker on a 12 m headland keeps the sea at 0")
	assert_between(storm.visuals.global_position.y, -EPS, EPS)
	storm.sea_level_y = -1.5
	assert_between(storm.storm_center().y, -1.5 - EPS, -1.5 + EPS, "explicit sea level")
	var water := WaterSurface.new()
	water.position = Vector3(0.0, 3.0, 0.0)
	_add(water)
	storm.water = water
	storm.refresh()
	assert_between(storm.sea_level(), 3.0 - EPS, 3.0 + EPS, "the zone water's rest plane wins")
	assert_between(storm.sea_height_at(Vector2(1.0e6, 0.0)), 3.0 - EPS, 3.0 + EPS, "far field = sea level")
	storm.sea_level_from_water = false
	assert_between(storm.storm_center().y, -1.5 - EPS, -1.5 + EPS, "the override ignores the water")
	_free_nodes()


func test_storm_is_a_tool_with_an_editor_footprint() -> void:
	for path in [
		"res://game/vfx/undertow/undertow_storm.gd",
		"res://game/vfx/undertow/undertow_state.gd",
		"res://game/vfx/undertow/undertow_mesh_builder.gd",
	]:
		assert_true((load(path) as Script).is_tool(), "%s is @tool (the storm runs in the editor)" % path)
	var radii := PackedFloat32Array([100.0, 200.0, 300.0])
	var mesh := UndertowMeshBuilder.footprint(radii, 5000.0, 32)
	var verts := mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX] as PackedVector3Array
	assert_eq(mesh.surface_get_primitive_type(0), Mesh.PRIMITIVE_LINES)
	assert_eq(verts.size(), 3 * 32 * 2 + 2, "one closed circle per radius plus the eye axis")
	assert_between(verts[0].length(), 100.0 - EPS, 100.0 + EPS)
	assert_between(verts[verts.size() - 1].y, 5000.0 - EPS, 5000.0 + EPS)
	var storm := UndertowStorm.new()
	_add(storm)
	assert_false(storm.visuals.has_node(UndertowStorm.GIZMO_NODE), "the gizmo is editor-only")
	assert_eq(storm.editor_preview_quality, "low", "the editor previews the cheap tier by default")
	_free_nodes()


func test_storm_look_overrides_and_restores_the_tunables() -> void:
	var storm := UndertowStorm.new()
	storm.quality = "high"
	_add(storm)
	var base := storm.body_material.get_shader_parameter(&"col_albedo") as Color
	var day := storm.state.look_parameters("day_storm")
	storm.look = "day_storm"
	var got := storm.body_material.get_shader_parameter(&"col_albedo") as Color
	assert_true(got.is_equal_approx(day["col_albedo"] as Color), "the look's albedo reaches the body")
	assert_eq(storm.body_material.get_shader_parameter(&"sun_low_floor"), day["sun_low_floor"])
	storm.look = ""
	got = storm.body_material.get_shader_parameter(&"col_albedo") as Color
	assert_true(got.is_equal_approx(base), "clearing the look restores the tunables")
	_free_nodes()


func test_storm_quality_setter_switches_the_tier() -> void:
	var storm := UndertowStorm.new()
	storm.quality = "high"
	_add(storm)
	assert_true(storm.body.visible)
	storm.quality = "low"
	assert_eq(storm.get_quality(), "low", "assigning quality after _ready switches the tier")
	assert_false(storm.body.visible, "Low draws shells")
	_free_nodes()


func test_storm_tiers_switch_body_and_shells() -> void:
	var storm := UndertowStorm.new()
	storm.quality = "high"
	_add(storm)
	var tier_log: Array[String] = []
	storm.quality_changed.connect(func(t: String) -> void: tier_log.append(t))
	assert_false(storm.set_quality("potato"))
	assert_true(storm.set_quality("low"))
	assert_false(storm.body.visible, "Low draws no raymarch")
	var plan := storm.state.quality_plan("low")
	var shells := (plan["shell_fractions"] as Array).size() + 1
	assert_eq(storm.shell_materials.size(), shells)
	var spray_on := 0
	for m in storm.materials():
		assert_true(m.shader != null, "every material has a shader")
	for child in storm.visuals.get_children():
		if str(child.name).begins_with(UndertowStorm.SPRAY_NODE) and (child as Node3D).visible:
			spray_on += 1
	assert_eq(spray_on, int(plan["spray_layers"]))
	assert_eq(storm.shell_materials[shells - 1].get_shader_parameter(&"shell_kind"), 1, "last shell is the canopy")
	assert_true(storm.set_quality("ultra"))
	assert_true(storm.body.visible)
	assert_eq(storm.get_quality(), "ultra")
	assert_eq(tier_log, ["low", "ultra"] as Array[String])
	_free_nodes()


func test_storm_pushes_clock_api_and_flashes() -> void:
	var storm := UndertowStorm.new()
	storm.quality = "medium"
	storm.playing = false
	_add(storm)
	storm.intensity = 0.0
	storm.set_time(42.0)
	assert_eq(storm.get_time(), 42.0)
	assert_eq(storm.body_material.get_shader_parameter(&"storm_time_s"), 42.0)
	assert_true(storm.force_flash(2, 42.0))
	var sites := storm.body_material.get_shader_parameter(&"lightning_sites") as PackedVector4Array
	assert_true(sites[2].w > 0.0, "forced stroke reaches the shader")
	assert_eq(sites[0].w, 0.0)
	storm.wound_intensity = 9.0
	storm.set_time(43.0)
	assert_eq(storm.wound_intensity, storm.state.range_of("wound_intensity").y)
	assert_eq(storm.sea_material.get_shader_parameter(&"wound_intensity"), storm.wound_intensity)
	storm._process(1.0)
	assert_eq(storm.get_time(), 43.0, "not playing: the clock holds")
	storm.playing = true
	storm._process(0.5)
	assert_between(storm.get_time(), 43.5 - EPS, 43.5 + EPS)
	_free_nodes()


func test_storm_reuses_the_zone_water_and_key_light() -> void:
	var w := WaterSurface.new()
	w.core_half_extent_m = 4.0
	w.core_cell_m = 1.0
	w.outer_half_extent_m = 16.0
	var mat := (load("res://game/levels/_tests/undertow/storm_ocean_material.tres") as ShaderMaterial).duplicate()
	w.material = mat as ShaderMaterial
	w.wave_set = load("res://game/levels/_tests/undertow/storm_sea_waves.tres") as WaveSet
	_add(w)
	w.sea_glow_energy = 0.08
	var sun := DirectionalLight3D.new()
	sun.light_color = Color(1.0, 0.5, 0.25)
	sun.light_energy = 2.0
	_add(sun)
	var field := GlimmerField.new()
	_add(field)
	var storm := UndertowStorm.new()
	storm.quality = "high"
	storm.water = w
	storm.sun = sun
	storm.motes = field
	_add(storm)
	var deep: Variant = w.material.get_shader_parameter(&"col_deep")
	assert_eq(storm.sea_material.get_shader_parameter(&"col_sea_deep"), deep, "funnel takes the zone's deep colour")
	assert_between(float(storm.sea_material.get_shader_parameter(&"sea_glow_energy")), 0.0799, 0.0801)
	var lid_h := float(storm.lid_material.get_shader_parameter(&"lid_height_m"))
	assert_true(lid_h > w.waves().amplitude_sum, "lid clears the highest crest")
	assert_eq(storm.body_material.get_shader_parameter(&"col_sun"), sun.light_color)
	var prio := storm.state.config["render_priority"] as Dictionary
	assert_eq(field.draw_material.render_priority, int(prio["motes"]), "motes draw over the storm")
	sun.visible = false
	assert_eq(storm.mood_parameters()["sun_energy"], 0.0, "a hidden key light does not light the storm")
	_free_nodes()
