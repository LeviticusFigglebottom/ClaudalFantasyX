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
	assert_eq(storm.sea_material.get_shader_parameter(&"storm_center"), c)
	storm.approach_distance_m = 3000.0
	assert_true(storm.visuals.global_position.is_equal_approx(storm.storm_center()), "approach moves it")
	var sea_y := storm.sea_height_at(Vector2(c.x, c.z) + Vector2(1.0, 0.0))
	assert_true(sea_y < -10.0, "the eye is a funnel below sea level")
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
