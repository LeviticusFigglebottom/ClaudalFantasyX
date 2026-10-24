extends TestCase
## M2-RND-05: the Undertow's events on the real data: chapter presets, the Letting (unbinding), the
## torn-rent uniforms, streamer and bolt meshes, strikes (bolts on the camera's half, the capped
## exposure flash), rain, the zone shadow and the storm in the water's reflection, and the per-tier counts.

const EPS := 1e-4
const OCEAN_MATERIAL := "res://game/levels/_tests/undertow/storm_ocean_material.tres"
const OCEAN_WAVES := "res://game/levels/_tests/undertow/storm_sea_waves.tres"

var _nodes: Array[Node] = []


func _cleanup() -> void:
	for n in _nodes:
		if is_instance_valid(n):
			n.free()
	_nodes.clear()


func test_every_preset_sets_real_storm_properties_in_range() -> void:
	var state := UndertowState.new()
	var storm := UndertowStorm.new()
	var props := {}
	for p: Dictionary in storm.get_property_list():
		props[str(p["name"])] = true
	assert_true(state.preset_ids().size() >= 5, "Ch1, Ch8, Ch20 and Ch21 presets")
	for id in state.preset_ids():
		for key: String in state.preset(id):
			assert_true(props.has(key), "%s.%s is a storm property" % [id, key])
			var v: Variant = state.preset(id)[key]
			if key in ["intensity", "rotation_rad_s", "wound_intensity", "approach_distance_m"]:
				var r := state.range_of(key)
				assert_between(float(v), r.x, r.y, "%s.%s in its range" % [id, key])
			if key == "look" and str(v) != "":
				assert_true(state.look_ids().has(str(v)), "%s: look %s exists" % [id, v])
	assert_eq(float(state.preset("ch21_letting")["unbinding"]), 1.0, "the Letting is released")
	assert_eq(float(state.preset("ch21_heart")["unbinding"]), 0.0, "the Heart is still held")
	storm.free()
	_cleanup()


func test_apply_preset_sets_the_storm() -> void:
	var storm := _storm("high")
	assert_true(storm.apply_preset("ch08_landfall"))
	var p := storm.state.preset("ch08_landfall")
	assert_between(
		storm.approach_distance_m, float(p["approach_distance_m"]) - EPS, float(p["approach_distance_m"]) + EPS
	)
	assert_eq(storm.look, str(p["look"]))
	assert_false(storm.apply_preset("no_such_preset"))
	_cleanup()


func test_unbinding_reverses_the_drift_without_a_jump_and_turns_the_light_gold() -> void:
	var state := UndertowState.new()
	state.time_s = 100.0
	var sink := float((state.config["wounds"] as Dictionary)["sink_m_s"])
	assert_between(state.wound_drift_m(), sink * 100.0 - EPS, sink * 100.0 + EPS, "held: sink x t, as before")
	var colors := state.config["colors"] as Dictionary
	var lift := Color.from_string(str(colors["lift"]), Color.MAGENTA)
	var held := Color.from_string(str(colors["held"]), Color.MAGENTA)
	assert_eq(state.dynamic_parameters()["col_held"], held, "held light is glimmer_held")
	var before := state.wound_drift_m()
	state.unbinding = 1.0
	assert_between(state.wound_drift_m(), before - EPS, before + EPS, "no jump when it changes")
	state.time_s = 110.0
	assert_true(state.wound_drift_m() < before, "released: the rents rise")
	var p := state.dynamic_parameters()
	assert_eq(p["col_held"], lift, "released light is glimmer_lift")
	assert_eq(p["col_wound"], lift)
	state.unbinding = 0.25
	assert_true(state.drift_sign() < 1.0 and state.drift_sign() > -1.0, "slowing as it turns")
	assert_eq(state.unbinding_hue(), 0.0, "the hue turns only once the direction has reversed")
	_cleanup()


func test_rent_and_drift_uniforms_reach_the_storm_shaders() -> void:
	var state := UndertowState.new()
	var params := state.static_parameters()
	for key in ["rent_lip_width", "rent_lip_dark", "rent_halo_width", "rent_halo_energy"]:
		assert_true(params.has(key), "%s pushed" % key)
	var dyn := state.dynamic_parameters()
	assert_true(dyn.has("wound_drift_m") and dyn.has("glow_drift_m"))
	for path in [
		"res://game/shaders/undertow/undertow_body.gdshader", "res://game/shaders/undertow/undertow_shell.gdshader"
	]:
		var names := _uniforms(path)
		for key in ["wound_drift_m", "rent_lip_dark", "rent_halo_energy"]:
			assert_true(names.has(key), "%s declares %s" % [path, key])
	assert_true(_uniforms("res://game/shaders/undertow/undertow_sea.gdshader").has("glow_drift_m"))
	var layout := UndertowComputeLayout.FIELDS.map(func(f: Array) -> String: return str(f[0]))
	assert_true(layout.has("wound_drift_m") and layout.has("rent_lip_dark"), "the compute body has them")
	_cleanup()


func test_streamer_curtains_hang_from_the_wall_to_the_sea() -> void:
	var anchors := PackedVector3Array([Vector3(9000.0, 4000.0, 0.0), Vector3(8500.0, 3000.0, 1.0)])
	var mesh := UndertowMeshBuilder.streamers(anchors, 1400.0, 1.0, 0.15, 380.0, 8)
	var arrays := mesh.surface_get_arrays(0)
	var verts := arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array
	var uv2 := arrays[Mesh.ARRAY_TEX_UV2] as PackedVector2Array
	assert_eq(verts.size(), 2 * 9 * 2, "two vertices per step per curtain")
	assert_between(verts[0].y, 3999.0, 4001.0, "starts at its wound")
	assert_between(verts[17].y, -EPS, EPS, "ends on the sea")
	assert_true(uv2[17].y > uv2[1].y and uv2[17].y > 3999.0, "arc length runs down the curtain")
	var r0 := Vector2(verts[0].x, verts[0].z).length()
	var r1 := Vector2(verts[16].x, verts[16].z).length()
	assert_true(r1 > r0 + 1000.0, "it bulges out toward the foot")
	_cleanup()


func test_bolt_is_deterministic_and_spans_its_ends() -> void:
	var top := Vector3(9000.0, 2600.0, 0.0)
	var bottom := Vector3(9500.0, 0.0, 100.0)
	var a: PackedVector3Array = UndertowMeshBuilder.bolt(42, top, bottom, 12, 3, 0.6).surface_get_arrays(0)[
		Mesh.ARRAY_VERTEX
	]
	var b: PackedVector3Array = UndertowMeshBuilder.bolt(42, top, bottom, 12, 3, 0.6).surface_get_arrays(0)[
		Mesh.ARRAY_VERTEX
	]
	var c: PackedVector3Array = UndertowMeshBuilder.bolt(43, top, bottom, 12, 3, 0.6).surface_get_arrays(0)[
		Mesh.ARRAY_VERTEX
	]
	assert_eq(a, b, "same seed, same stroke")
	assert_ne(a, c, "another strike, another stroke")
	assert_eq(a[0], top, "from the cloud base")
	assert_eq(a[12 * 4 - 1], bottom, "to the sea")
	assert_true(a.size() > 12 * 4, "with forks")
	_cleanup()


func test_a_strike_draws_a_bolt_on_the_cameras_half_and_flashes_the_exposure_capped() -> void:
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.tonemap_exposure = 0.8
	_add(env)
	var cam := Camera3D.new()
	_add(cam)
	cam.make_current()
	var storm := _storm("high")
	storm.world_environment = env
	storm.approach_distance_m = 15000.0
	storm.approach_azimuth_deg = 90.0
	var struck := []
	storm.lightning_struck.connect(func(site: int, bolt: bool) -> void: struck.append([site, bolt]))
	var site := storm.site_facing(cam.global_position)
	storm.force_flash(site)
	storm.events.update()
	assert_eq(struck.size(), 1, "one strike")
	assert_true(bool(struck[0][1]) and storm.events.bolts[site].visible, "a forced strike in view draws a bolt")
	var cfg := storm.state.config["exposure_flash"] as Dictionary
	assert_between(env.environment.tonemap_exposure, 0.8 * float(cfg["gain"]) - EPS, 0.8 * float(cfg["gain"]) + EPS)
	for i in int(cfg["frames"]):
		storm.events.update()
	assert_between(env.environment.tonemap_exposure, 0.8 - EPS, 0.8 + EPS, "back after its frames")
	# A second strike inside min_interval_s is refused (at most two a second).
	storm.state.clear_forced_flashes()
	storm.events.update()
	storm.force_flash((site + 1) % storm.state.flash_site_count())
	storm.events.update()
	assert_eq(storm.events.flashes, 1)
	assert_eq(storm.events.flashes_suppressed, 1, "capped like battle flashes")
	assert_between(env.environment.tonemap_exposure, 0.8 - EPS, 0.8 + EPS)
	# A site behind the storm never draws a stroke (the wall would hide it).
	var far := -1
	var sites := storm.state.flash_sites(storm.state.time_s)
	var to_cam := cam.global_position - storm.storm_center()
	for i in storm.state.flash_site_count():
		if sites[i].x * to_cam.x + sites[i].z * to_cam.z < 0.0:
			far = i
	if far >= 0:
		assert_false(storm.events.strike_shows_bolt(far, storm.state.time_s), "no stroke behind the wall")
	_cleanup()


func test_rain_follows_the_storm_and_stays_under_the_cloud() -> void:
	var storm := _storm("high")
	storm.approach_distance_m = 0.0
	var c := storm.storm_center()
	var rain := storm.state.config["rain"] as Dictionary
	assert_between(storm.events.rain_amount(c + Vector3(1000.0, 5.0, 0.0)), 1.0 - EPS, 1.0 + EPS, "full near the eye")
	assert_eq(storm.events.rain_amount(c + Vector3(float(rain["reach_m"]) + 1.0, 5.0, 0.0)), 0.0, "none beyond reach")
	assert_eq(storm.events.rain_amount(c + Vector3(1000.0, float(rain["ceiling_m"]) + 1.0, 0.0)), 0.0, "dry above")
	storm.intensity = 0.5
	assert_between(storm.events.rain_amount(c + Vector3(1000.0, 5.0, 0.0)), 0.5 - EPS, 0.5 + EPS)
	storm.rain_amount = 0.3
	assert_between(storm.events.rain_amount(c), 0.3 - EPS, 0.3 + EPS, "the override wins")
	_cleanup()


func test_zone_shadow_dims_the_key_and_ambient_and_restores_them() -> void:
	var sun := DirectionalLight3D.new()
	sun.light_energy = 2.0
	_add(sun)
	sun.global_basis = Basis.looking_at(Vector3(0.0, -1.0, -1.0).normalized())
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.ambient_light_energy = 1.0
	_add(env)
	var storm := _storm("high")
	storm.sun = sun
	storm.world_environment = env
	var up := Vector3(0.0, 1.0, 0.0)
	storm.approach_distance_m = 60000.0
	assert_eq(storm.events.zone_shadow_at(storm.global_position, up), 0.0, "far off, sun overhead: no shadow")
	storm.approach_distance_m = 0.0
	assert_between(storm.events.zone_shadow_at(storm.global_position, up), 1.0 - EPS, 1.0 + EPS, "under the canopy")
	storm.events.update()
	var zs := storm.state.config["zone_shadow"] as Dictionary
	assert_between(sun.light_energy, 2.0 * (1.0 - float(zs["sun_dim"])) - EPS, 2.0 * (1.0 - float(zs["sun_dim"])) + EPS)
	assert_true(env.environment.ambient_light_energy < 1.0, "the ambient dims")
	assert_between(storm.events.sun_energy(), 2.0 - EPS, 2.0 + EPS, "the storm is lit by the undimmed key")
	storm.events.update()
	assert_between(storm.events.sun_energy(), 2.0 - EPS, 2.0 + EPS, "no compounding frame to frame")
	storm.get_parent().remove_child(storm)
	assert_between(sun.light_energy, 2.0 - EPS, 2.0 + EPS, "restored when the storm leaves")
	assert_between(env.environment.ambient_light_energy, 1.0 - EPS, 1.0 + EPS)
	storm.free()
	_cleanup()


func test_the_storm_is_in_the_waters_reflection_and_leaves_with_it() -> void:
	var w := WaterSurface.new()
	w.core_half_extent_m = 4.0
	w.core_cell_m = 1.0
	w.outer_half_extent_m = 16.0
	w.material = (load(OCEAN_MATERIAL) as ShaderMaterial).duplicate()
	w.wave_set = load(OCEAN_WAVES) as WaveSet
	_add(w)
	var storm := _storm("high")
	storm.water = w
	storm.events.update()
	var p := storm.events.reflection_parameters()
	var names := _uniforms("res://game/shaders/water/water_ocean.gdshader")
	for key: StringName in p:
		assert_true(names.has(str(key)), "water_ocean declares %s" % key)
	assert_true(float(w.material.get_shader_parameter(&"storm_reflect")) > 0.0, "the sea reflects the storm")
	storm.intensity = 0.0
	assert_eq(float(storm.events.reflection_parameters()[&"storm_reflect"]), 0.0, "a sleeping storm is not reflected")
	storm.get_parent().remove_child(storm)
	assert_eq(float(w.material.get_shader_parameter(&"storm_reflect")), 0.0, "cleared on exit")
	storm.free()
	_cleanup()


func test_tiers_scale_the_event_parts() -> void:
	var state := UndertowState.new()
	var low := state.quality_plan("low")
	var high := state.quality_plan("high")
	for key in ["streamers", "rain_layers", "bolt_branches"]:
		assert_true(int(low[key]) > 0, "Low keeps %s" % key)
		assert_true(int(high[key]) >= int(low[key]), "High has at least Low's %s" % key)
	var storm := _storm("low")
	assert_true(storm.events.streamers.visible, "Low draws streamers on its shells")
	assert_eq(storm.events.rain_materials.size(), int(low["rain_layers"]))
	storm.set_quality("ultra")
	assert_eq(storm.events.rain_materials.size(), int(state.quality_plan("ultra")["rain_layers"]))
	for m in storm.events.all_materials():
		assert_true(storm.materials().has(m), "prewarm sees every event material")
	_cleanup()


func _storm(tier: String) -> UndertowStorm:
	var storm := UndertowStorm.new()
	storm.quality = tier
	storm.half_res_compute = false
	_add(storm)
	storm.refresh()
	return storm


func _add(n: Node) -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(n)
	_nodes.append(n)
	return n


static func _uniforms(path: String) -> Array:
	return (load(path) as Shader).get_shader_uniform_list().map(func(u: Dictionary) -> String: return str(u["name"]))
