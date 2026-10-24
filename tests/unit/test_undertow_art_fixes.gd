extends TestCase
## M2-RND-10: Art's changes to the Undertow's events (M2-ART-03), on the real data: per-chapter lightning
## (exposure flash gain, bolts, the sites' glow fading with the Letting), the Letting's rise ratio, no rain
## on a submerged camera, the zone shadow's slate-teal tint (and its restore), and the rent split between a
## half-res body and the composite's full-resolution seams.

const EPS := 1e-4
const COMPOSITE := "res://game/shaders/undertow/undertow_composite.gdshader"
## Art's per-chapter lightning table (M2-RND-10 item 7): preset -> [exposure flash gain, bolts].
const FLASH_TABLE := {
	"ch01_arrival": [1.0, true],
	"ch08_seawall": [2.0, true],
	"ch08_landfall": [2.0, true],
	"ch20_interior": [1.5, true],
	"ch21_heart": [1.5, true],
	"ch21_letting": [1.0, false],
}

var _nodes: Array[Node] = []


func _cleanup() -> void:
	for n in _nodes:
		if is_instance_valid(n):
			n.free()
	_nodes.clear()


func test_presets_carry_the_per_chapter_lightning_and_the_letting_rises_twice_as_fast() -> void:
	var state := UndertowState.new()
	for id: String in FLASH_TABLE:
		var p := state.preset(id)
		assert_eq(float(p["exposure_flash_gain"]), float(FLASH_TABLE[id][0]), "%s flash gain" % id)
		assert_eq(bool(p["bolts"]), bool(FLASH_TABLE[id][1]), "%s bolts" % id)
	assert_eq(float((state.config["unbinding"] as Dictionary)["rise_ratio"]), 2.0, "colour script rule 1")
	_cleanup()


func test_a_flash_gain_of_one_or_no_bolts_keeps_the_strike_quiet() -> void:
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
	storm.exposure_flash_gain = 1.0
	storm.bolts = false
	var site := storm.site_facing(cam.global_position)
	storm.force_flash(site)
	storm.events.update()
	assert_between(env.environment.tonemap_exposure, 0.8 - EPS, 0.8 + EPS, "gain 1: no exposure flash")
	assert_false(storm.events.strike_shows_bolt(site, storm.state.time_s), "bolts off: no stroke, even forced")
	assert_false(storm.events.bolts[site].visible)
	storm.exposure_flash_gain = 1.5
	assert_between(storm.events.flash_gain(), 1.5 - EPS, 1.5 + EPS, "the chapter's gain")
	storm.exposure_flash_gain = -1.0
	var cfg := storm.state.config["exposure_flash"] as Dictionary
	assert_between(storm.events.flash_gain(), float(cfg["gain"]) - EPS, float(cfg["gain"]) + EPS, "< 0: the data's")
	_cleanup()


func test_the_lightning_sites_go_dark_as_the_letting_passes_half() -> void:
	var state := UndertowState.new()
	state.force_flash(0, state.time_s)
	var lit := state.flash_level(0, state.time_s)
	assert_true(lit > 0.0, "a forced flash lights its site")
	state.unbinding = 0.4
	assert_between(state.flash_level(0, state.time_s), lit - EPS, lit + EPS, "still held: full glow")
	state.unbinding = 1.0
	assert_eq(state.flash_level(0, state.time_s), 0.0, "released: no lightning")
	_cleanup()


func test_no_rain_on_a_camera_an_underwater_rig_has_submerged() -> void:
	var cam := Camera3D.new()
	_add(cam)
	cam.make_current()
	var water := WaterSurface.new()
	_add(water)
	var rig := UnderwaterRig.new()
	rig.water = water
	_add(rig)
	var storm := _storm("high")
	storm.approach_distance_m = 0.0
	storm.rain_amount = 0.8
	cam.global_position = Vector3(0.0, 5.0, 0.0)
	assert_false(UnderwaterRig.camera_submerged(rig.get_tree()))
	storm.events.update()
	assert_true(storm.events.rain.visible, "above water: the preset's rain")
	cam.global_position = Vector3(0.0, -3.0, 0.0)
	assert_true(UnderwaterRig.camera_submerged(rig.get_tree()))
	storm.events.update()
	assert_false(storm.events.rain.visible, "rain is a camera effect: none underwater")
	rig.active = false
	assert_false(UnderwaterRig.camera_submerged(rig.get_tree()), "an inactive rig reports nothing")
	_cleanup()


func test_the_zone_shadow_tints_toward_slate_teal_and_gives_the_zone_back() -> void:
	var sun := DirectionalLight3D.new()
	sun.light_energy = 2.0
	_add(sun)
	sun.global_basis = Basis.looking_at(Vector3(0.0, -1.0, -1.0).normalized())
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	var e := env.environment
	e.ambient_light_color = Color(0.5, 0.5, 0.5)
	e.ambient_light_sky_contribution = 1.0
	e.fog_light_color = Color(0.4, 0.4, 0.4)
	e.background_energy_multiplier = 1.0
	_add(env)
	var storm := _storm("high")
	storm.sun = sun
	storm.world_environment = env
	storm.approach_distance_m = 0.0
	storm.events.update()
	assert_between(storm.events.shadow, 1.0 - EPS, 1.0 + EPS, "under the canopy")
	assert_true(e.ambient_light_color.b > e.ambient_light_color.r, "the ambient leans teal")
	assert_true(e.fog_light_color.b > e.fog_light_color.r, "so does the fog")
	assert_true(e.ambient_light_sky_contribution < 1.0, "a sky-sourced ambient takes the tint")
	var mood := storm.mood_parameters()
	assert_true((mood["col_haze"] as Color).b > (mood["col_haze"] as Color).r, "and the storm's own haze")
	storm.events.update()
	var once := e.ambient_light_color
	storm.events.update()
	assert_true(e.ambient_light_color.is_equal_approx(once), "no compounding frame to frame")
	storm.get_parent().remove_child(storm)
	assert_true(e.ambient_light_color.is_equal_approx(Color(0.5, 0.5, 0.5)), "restored when the storm leaves")
	assert_true(e.fog_light_color.is_equal_approx(Color(0.4, 0.4, 0.4)))
	assert_between(e.ambient_light_sky_contribution, 1.0 - EPS, 1.0 + EPS)
	assert_between(e.background_energy_multiplier, 1.0 - EPS, 1.0 + EPS)
	storm.free()
	_cleanup()


func test_only_a_half_res_compute_body_hands_its_rent_cores_to_the_composite() -> void:
	var names := (load(COMPOSITE) as Shader).get_shader_uniform_list().map(
		func(u: Dictionary) -> String: return str(u["name"])
	)
	for u in ["full_res_rents", "rent_core_energy", "rent_lip_share", "front_smooth", "wound_width"]:
		assert_true(names.has(u), "the composite has %s" % u)
	var storm := _storm("high")
	assert_eq(float(storm.body_material.get_shader_parameter(&"rent_core_gain")), 1.0, "no compute body: whole")
	assert_eq(float(storm.body_material.get_shader_parameter(&"rent_lip_gain")), 1.0)
	var hr := (storm.state.config["wounds"] as Dictionary)["half_res"] as Dictionary
	assert_true(float(hr["body_core_gain"]) < 1.0 and float(hr["core_energy"]) > 0.0, "the split is in the data")
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
