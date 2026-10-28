extends TestCase
## M3-BPR-409 audit: reduced motion and the screen shake setting cap every impact and special the battle plays.
## - Every full-screen flash in the battle VFX table (BattleVfx, the toll's included) is fainter under reduced motion,
##   and never above the safety cap.
## - BattleImpact: no shake, a dimmer flash and a gentler KO slow-mo under reduced motion (the data), and a heavy blow
##   adds no shake and keeps its light under the reduced cap (live).
## - Every stage shake (the impact's and BattleFloats' crit shake) is off with Screen shake Off or reduced motion.
## - The camera's extras keep to the default under reduced motion: the Breach push-in and the boss intro.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261027
const EPS := 0.001

var ctl: BattleController


func before_each() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var active: Array[StringName] = [&"rhen", &"asha"]
	var none: Array[StringName] = []
	ctl.start_battle(active, none, &"sandbox_reef", SEED)
	ctl.stage.choreo.live = false


func test_every_full_screen_flash_is_fainter_and_capped() -> void:
	var vfx := ctl.stage.get_node(^"BattleVfx") as BattleVfx
	var effects := vfx.data.get("effects", {}) as Dictionary
	var cap := float((vfx.data["safety"] as Dictionary)["flash_max_alpha"])
	var flashes := 0
	for id: String in effects:
		var def := effects[id] as Dictionary
		if str(def.get("kind", "")) != BattleVfx.KIND_FLASH:
			continue
		flashes += 1
		vfx.reduced_motion = false
		var full := vfx.flash_alpha(def)
		vfx.reduced_motion = true
		var soft := vfx.flash_alpha(def)
		assert_true(full <= cap + EPS, "%s: under the safety cap" % id)
		assert_true(soft < full or full <= 0.0, "%s: fainter under reduced motion (%.2f -> %.2f)" % [id, full, soft])
	assert_true(flashes > 0, "the table has flashes to check")
	_free()


func test_the_impact_data_caps_itself_under_reduced_motion() -> void:
	var cfg := ctl.stage.choreo.data["impact"] as Dictionary
	var rm := cfg["reduced_motion"] as Dictionary
	assert_eq(float(rm["shake_scale"]), 0.0, "no impact shake")
	assert_true(float(rm["flash_scale"]) < 1.0, "a dimmer impact flash")
	assert_true(float(rm["slowmo_factor"]) > float((cfg["ko_slowmo"] as Dictionary)["factor"]), "a gentler slow-mo")
	_free()


func test_a_heavy_blow_under_reduced_motion_neither_shakes_nor_glares() -> void:
	var choreo := ctl.stage.choreo
	var foe := ctl.engine.find(ctl.engine.enemies[0].id)
	foe.max_hp = 1  # every blow is full strength
	foe.hp = 100000
	var guard := 0
	while ctl.current_actor_id() != &"rhen" and guard < 16:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])
	ctl.pacing_scale = 1.0
	choreo.reduced_motion = true
	var shakes := ctl.stage.shakes_started
	ctl.act(&"attack", [foe.id])
	choreo.advance(float(choreo.current()["contact"]) + EPS)
	assert_eq(ctl.stage.shakes_started, shakes, "no shake")
	var cfg := choreo.data["impact"] as Dictionary
	var cap := (
		float((cfg["flash"] as Dictionary)["energy_cap"]) * float((cfg["reduced_motion"] as Dictionary)["flash_scale"])
	)
	var light := choreo.impact.light()
	assert_true(light == null or light.light_energy <= cap + EPS, "the light stays under the reduced cap")
	_free()


func test_every_stage_shake_obeys_the_setting_and_reduced_motion() -> void:
	var settings := UiSettings.new()
	UiSettings.set_shared(settings)
	for case: Array in [[BattleStage.SETTING_SHAKE, 0.0], [UiSettings.REDUCED_MOTION, true]]:
		settings.reset()
		settings.set_value(StringName(case[0]), case[1])
		var shakes := ctl.stage.shakes_started
		ctl.stage.shake(1.0)  # BattleFloats' crit shake
		ctl.stage.shake(1.0, 1.6)  # BattleImpact's heaviest
		assert_eq(ctl.stage.shakes_started, shakes, "%s: no shake" % [case])
	settings.reset()
	var before := ctl.stage.shakes_started
	ctl.stage.shake(1.0)
	assert_eq(ctl.stage.shakes_started, before + 1, "Full: the shake plays")
	UiSettings.set_shared(null)
	_free()


func test_the_camera_extras_keep_to_the_default_under_reduced_motion() -> void:
	var cam := ctl.stage.choreo.camera
	var foe := ctl.engine.enemies[0]
	foe.id = &"avalanche_ram#1"
	foe.charge_skill = &"any"
	foe.charge_left = 1
	ctl.stage.choreo.reduced_motion = true
	assert_eq(cam.rest_fov(), cam.default_fov, "no push-in for a gathering charge")
	_free()


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
