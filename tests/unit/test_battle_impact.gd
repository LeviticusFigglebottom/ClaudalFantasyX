extends TestCase
## M3-BPR-401: battle feel on the contact beat (BattleImpact). A blow's strength comes from its damage against the
## target's max HP; a heavy one holds the clock (hit-stop), shakes the camera by its weight, flashes a capped light at
## the target and recoils it harder; the blow that fells the last foe slows the collapse. Reduced motion drops the
## shake and dims the flash. The controller's hand-off waits for the stretched time.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261022
const EPS := 0.001

var ctl: BattleController
var choreo: BattleChoreo
var cfg: Dictionary


func before_each() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = []
	ctl.start_battle(active, reserve, &"sandbox_reef", SEED)
	choreo = ctl.stage.choreo
	choreo.live = false
	choreo.reduced_motion = false
	choreo.skip = false
	choreo.speed = 1.0
	cfg = choreo.data["impact"]


func test_data_is_sane() -> void:
	for k in ["full_frac", "heavy_strength", "stop_fps", "shake_min_strength"]:
		assert_true(float(cfg[k]) > 0.0, k)
	var frames: Array = cfg["hit_stop_frames"]
	assert_true(int(frames[0]) >= 2 and int(frames[1]) <= 4, "2-4 frames of hit-stop")
	var fl: Dictionary = cfg["flash"]
	assert_true(float((fl["energy"] as Array)[1]) <= float(fl["energy_cap"]), "the flash stays under its cap")
	assert_eq(float(cfg["reduced_motion"]["shake_scale"]), 0.0, "no shake under reduced motion")
	_free()


func test_strength_is_damage_over_max_hp() -> void:
	var foe := ctl.engine.find(_foe())
	foe.max_hp = 1000
	var full := float(cfg["full_frac"])
	assert_eq(BattleImpact.strength(choreo.data, ctl.engine, _hit(foe.id, 0)), 0.0, "no damage")
	assert_eq(BattleImpact.strength(choreo.data, ctl.engine, _hit(foe.id, -50)), 0.0, "a heal")
	var miss := _hit(foe.id, 400)
	miss["hit"] = false
	assert_eq(BattleImpact.strength(choreo.data, ctl.engine, miss), 0.0, "a miss")
	var half := int(1000 * full * 0.5)
	assert_between(BattleImpact.strength(choreo.data, ctl.engine, _hit(foe.id, half)), 0.49, 0.51, "half way")
	assert_eq(BattleImpact.strength(choreo.data, ctl.engine, _hit(foe.id, 999)), 1.0, "clamped")
	var crit := _hit(foe.id, half)
	crit["crit"] = true
	assert_between(
		BattleImpact.strength(choreo.data, ctl.engine, crit),
		0.5 + float(cfg["crit_bonus"]) - 0.01,
		1.0,
		"a crit hits harder"
	)
	_free()


func test_a_heavier_blow_recoils_harder() -> void:
	var foe := ctl.engine.find(_foe())
	foe.max_hp = 1000
	var light := choreo.plan_for(_result([_hit(foe.id, 10)]))
	var heavy := choreo.plan_for(_result([_hit(foe.id, 900)]))
	assert_true(float(heavy["impact"]) > float(light["impact"]))
	var wl := float((light["reactions"] as Array)[0]["weight"])
	var wh := float((heavy["reactions"] as Array)[0]["weight"])
	assert_true(wh > wl, "recoil weight follows the blow (%s vs %s)" % [wl, wh])
	assert_between(wl, float(cfg["recoil_scale"][0]) - EPS, float(cfg["recoil_scale"][1]) + EPS)
	_free()


func test_a_heavy_contact_holds_the_clock_and_the_hand_off_waits() -> void:
	var foe := _heavy_foe()
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	ctl.act(&"attack", [foe.id])
	var plan := choreo.current()
	var stop := BattleImpact.hit_stop_sec(choreo.data, float(plan["impact"]))
	assert_true(stop >= 2.0 / float(cfg["stop_fps"]) - EPS, "a heavy blow stops")
	var base := float(plan["total"]) / choreo.speed
	assert_true(choreo.remaining_sec() >= base + stop - EPS, "the hand-off counts the hit-stop")
	choreo.advance(float(plan["contact"]) + EPS)
	assert_eq(choreo.impact.stops, 1, "one hit-stop on the contact")
	var t := choreo.time()
	choreo.advance(stop * 0.5)
	assert_between(choreo.time(), t - EPS, t + EPS, "the clock holds")
	choreo.advance(stop)
	assert_true(choreo.time() > t, "and runs on after")
	_free()


func test_a_light_blow_neither_stops_nor_shakes() -> void:
	var foe := ctl.engine.find(_foe())
	foe.max_hp = 1000000
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	var shakes := ctl.stage.shakes_started
	ctl.act(&"attack", [foe.id])
	var plan := choreo.current()
	choreo.advance(float(plan["contact"]) + EPS)
	assert_eq(choreo.impact.stops, 0)
	assert_eq(ctl.stage.shakes_started, shakes, "no shake")
	_free()


func test_a_heavy_blow_shakes_and_flashes_a_capped_light() -> void:
	var foe := _heavy_foe()
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	var shakes := ctl.stage.shakes_started
	ctl.act(&"attack", [foe.id])
	choreo.advance(float(choreo.current()["contact"]) + EPS)
	assert_eq(ctl.stage.shakes_started, shakes + 1, "it shakes")
	var light := choreo.impact.light()
	assert_true(light != null and light.visible, "it flashes")
	assert_true(light.light_energy <= float(cfg["flash"]["energy_cap"]) + EPS, "capped")
	assert_eq(light.light_volumetric_fog_energy, 0.0, "no fog banding")
	choreo.seek(choreo.time() + float(cfg["flash"]["sec"]) * 0.5)
	choreo.impact._process(0.0)
	assert_true(light.visible and light.light_energy > 0.0, "a held clock holds the flash where it is (freeze-frames)")
	choreo.live = true
	choreo.impact._process(float(cfg["flash"]["sec"]) + EPS)
	assert_false(light.visible, "and is gone again")
	_free()


func test_reduced_motion_drops_the_shake_and_dims_the_flash() -> void:
	var foe := _heavy_foe()
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	choreo.reduced_motion = true
	var shakes := ctl.stage.shakes_started
	ctl.act(&"attack", [foe.id])
	choreo.advance(float(choreo.current()["contact"]) + EPS)
	assert_eq(ctl.stage.shakes_started, shakes, "no shake")
	var cap := float(cfg["flash"]["energy_cap"]) * float(cfg["reduced_motion"]["flash_scale"])
	assert_true(choreo.impact.light().light_energy <= cap + EPS, "a dimmer flash")
	_free()


func test_the_screen_shake_setting_scales_or_drops_the_shake() -> void:
	var settings := UiSettings.new()
	UiSettings.set_shared(settings)
	assert_eq(BattleStage.shake_setting(), 1.0, "full by default")
	settings.set_value(BattleStage.SETTING_SHAKE, 0.5)
	assert_eq(BattleStage.shake_setting(), 0.5, "half")
	settings.set_value(UiSettings.REDUCED_MOTION, true)
	assert_eq(BattleStage.shake_setting(), 0.0, "reduced motion: none")
	settings.set_value(UiSettings.REDUCED_MOTION, false)
	settings.set_value(BattleStage.SETTING_SHAKE, 0.0)
	var foe := _heavy_foe()
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	var shakes := ctl.stage.shakes_started
	ctl.act(&"attack", [foe.id])
	choreo.advance(float(choreo.current()["contact"]) + EPS)
	assert_eq(ctl.stage.shakes_started, shakes, "Off: a heavy blow does not shake")
	UiSettings.set_shared(null)
	_free()


func test_audio_hears_each_weighty_blow_and_the_last_blow_slow_mo() -> void:
	var foe := _heavy_foe()
	_to_turn_of(&"rhen")
	ctl.pacing_scale = 1.0
	var heard: Array = []
	choreo.impact.landed.connect(func(tid: StringName, s: float, stop: float) -> void: heard.append([tid, s, stop]))
	ctl.act(&"attack", [foe.id])
	choreo.advance(float(choreo.current()["contact"]) + EPS)
	assert_eq(heard.size(), 1, "one landed event on the contact")
	assert_eq(heard[0][0], foe.id, "on the struck foe")
	assert_true(float(heard[0][1]) > 0.0 and float(heard[0][2]) > 0.0, "a heavy blow: its weight and its hit-stop")
	_free()
	before_each()
	_to_turn_of(&"rhen")
	for e in ctl.engine.enemies:
		e.hp = 1 if e.id == _foe() else 0
	ctl.pacing_scale = 1.0
	choreo.outro.live = false
	var slow: Array = []
	choreo.impact.slowmo_planned.connect(func(_f: float, sec: float, k: float) -> void: slow.append([sec, k]))
	ctl.act(&"attack", [_foe()])
	assert_eq(slow.size(), 1, "the last blow announces its slow-mo")
	assert_true(float(slow[0][0]) > 0.0 and float(slow[0][1]) < 1.0)
	_free()


func test_felling_the_last_foe_slows_the_collapse() -> void:
	_to_turn_of(&"rhen")
	for e in ctl.engine.enemies:
		e.hp = 1 if e.id == _foe() else 0
	var last := ctl.engine.find(_foe())
	last.max_hp = 1000000  # a light blow: only the slow-mo stretches the time
	ctl.pacing_scale = 1.0
	choreo.outro.live = false
	ctl.act(&"attack", [last.id])
	assert_eq(ctl.engine.outcome, BattleEngine.OUTCOME_VICTORY)
	var plan := choreo.current()
	var sm: Dictionary = cfg["ko_slowmo"]
	var stretch := float(sm["sec"]) * (1.0 / float(sm["factor"]) - 1.0)
	assert_between(
		choreo.remaining_sec(), float(plan["total"]) + stretch - EPS, float(plan["total"]) + stretch + EPS, "it waits"
	)
	var from := float(plan["ko_at"]) - float(sm["lead_sec"])
	choreo.seek(from + EPS)
	choreo.live = true
	var t := choreo.time()
	choreo.advance(0.1)
	assert_between(choreo.time() - t, 0.1 * float(sm["factor"]) - EPS, 0.1 * float(sm["factor"]) + EPS, "slowed")
	_free()


func test_instant_pacing_adds_nothing() -> void:
	var foe := _heavy_foe()
	_to_turn_of(&"rhen")
	ctl.act(&"attack", [foe.id])
	assert_eq(choreo.impact.stops, 0)
	assert_true(choreo.impact.light() == null, "no flash")
	_free()


func _heavy_foe() -> BattleCombatant:
	var foe := ctl.engine.find(_foe())
	foe.max_hp = 1  # any damage is a full-strength blow
	foe.hp = 100000
	return foe


func _foe() -> StringName:
	for e in ctl.engine.enemies:
		if e.is_alive():
			return e.id
	return &""


func _hit(tid: StringName, amount: int) -> Dictionary:
	return {"target_id": tid, "hit": true, "crit": false, "amount": amount, "statuses_added": []}


func _result(hits: Array[Dictionary]) -> ActionResult:
	var r := ActionResult.new()
	r.actor_id = &"rhen"
	r.skill_id = &"attack"
	r.hits = hits
	return r


func _to_turn_of(cid: StringName) -> void:
	var guard := 0
	while ctl.current_actor_id() != cid and guard < 16:
		guard += 1
		ctl.act(&"attack", [ctl.engine.living_foes_of(ctl.engine.current)[0].id])


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()


## M3-BPR-402: a melee run never puts the actor inside a target, for a hero on a creature and a creature on a hero,
## at every moment of the sequence (contact and the full lunge included).
func test_no_actor_overlaps_another_during_a_melee_run() -> void:
	ctl.pacing_scale = 1.0
	var foe := _foe()
	for pair: Array in [[&"rhen", foe], [foe, &"rhen"], [&"asha", foe], [foe, &"asha"]]:
		var actor := StringName(str(pair[0]))
		var r := _result([_hit(StringName(str(pair[1])), 1)])
		r.actor_id = actor
		choreo._on_action_resolved(r)
		var plan := choreo.current()
		assert_eq(str(plan["style"]), "melee", "%s runs in" % actor)
		var ra := choreo._radius(actor)
		var steps := 40
		for i in steps + 1:
			choreo.seek(float(plan["total"]) * i / steps)
			for c: BattleCombatant in ctl.engine.party_active + ctl.engine.enemies:
				if c.id == actor or not c.is_alive():
					continue
				# Never inside a body; one already that close on its mark (the line-up, not the run) never closer.
				var at_home := _flat_dist(choreo._home_of(actor).origin, choreo._home_of(c.id).origin)
				var need := minf(choreo._radius(c.id) + ra, at_home)
				var d := _flat_dist(ctl.stage.stand_in(actor).position, ctl.stage.stand_in(c.id).position)
				assert_true(d >= need - EPS, "%s and %s at %.2f: %.2f >= %.2f" % [actor, c.id, choreo.time(), d, need])
		choreo.finish()
	_free()


func test_a_big_target_stops_the_run_further_out() -> void:
	var st := choreo.style("melee")
	var from := Vector3.ZERO
	var dir := Vector3.FORWARD
	var aim := Vector3(0.0, 0.0, -5.0)
	var small := BattleChoreoPlan.melee_gap(choreo.data, st, from, dir, aim, [[aim, 0.2]], 0.3)
	var big := BattleChoreoPlan.melee_gap(choreo.data, st, from, dir, aim, [[aim, 1.2]], 0.3)
	assert_true(big < small, "a bigger body keeps the actor further off")
	var clear := float(choreo.data["spacing"]["clearance_m"]) + float(st["lunge_m"])
	assert_between(big, 5.0 - (0.3 + 1.2 + clear) - EPS, 5.0 - (0.3 + 1.2 + clear) + EPS)
	var aside := BattleChoreoPlan.melee_gap(
		choreo.data, st, from, dir, aim, [[aim, 0.2], [Vector3(3.0, 0, -2.0), 1.0]], 0.3
	)
	assert_eq(aside, small, "a body well off the path changes nothing")
	_free()


func _flat_dist(a: Vector3, b: Vector3) -> float:
	return Vector2(a.x - b.x, a.z - b.z).length()


func test_a_creature_models_footprint_is_its_real_size() -> void:
	var foe := _foe()
	var f := ctl.stage.stand_in(foe)
	assert_true(BattleClips.creature_of(f) != null, "the sandbox's foes are models")
	var r := BattleChoreoPlan.footprint(f, choreo.data)
	assert_true(
		r > float(BattleStage.stand_in_spec(foe).get("radius", 0.0)), "%s: %.2f, bigger than its primitive" % [foe, r]
	)
	assert_true(r < 3.0, "but a sane size")
	assert_eq(choreo._radius(foe), r, "the run uses it")
	_free()


func test_a_body_beside_the_path_turns_the_run_instead_of_stopping_it() -> void:
	# M3-BPR-402: a big flier beside the crab used to stop Rhen's run 2.9 m short of it.
	var st := choreo.style("melee")
	var from := Vector3(2.0, 0.0, 0.0)
	var aim := Vector3(-2.5, 0.0, 0.0)
	var target := [aim, 0.9]
	var beside := [Vector3(-1.0, 0.0, -1.6), 1.4]
	var straight := BattleChoreoPlan.melee_gap(choreo.data, st, from, Vector3.LEFT, aim, [target, beside], 0.3)
	var run := BattleChoreoPlan.melee_approach(choreo.data, st, from, aim, [target, beside], [target], 0.3)
	var end := from + (run["dir"] as Vector3) * float(run["gap"])
	var free := BattleChoreoPlan.melee_gap(choreo.data, st, from, Vector3.LEFT, aim, [target], 0.3)
	assert_true(end.distance_to(aim) < (from + Vector3.LEFT * straight).distance_to(aim), "it gets closer than before")
	var reach := float(choreo.data["spacing"]["detour_reach_m"])
	assert_true(end.distance_to(aim) <= (from + Vector3.LEFT * free).distance_to(aim) + reach + EPS, "it reaches")
	assert_true((run["dir"] as Vector3).z > 0.0, "turning away from the body beside the path")
	var clear := float(choreo.data["spacing"]["clearance_m"])
	assert_true(end.distance_to(beside[0]) >= 0.3 + 1.4 + clear - EPS, "and never ends inside it")
	var open := BattleChoreoPlan.melee_approach(choreo.data, st, from, aim, [target], [target], 0.3)
	assert_eq(open["dir"], Vector3.LEFT, "an open path stays straight")
	_free()
