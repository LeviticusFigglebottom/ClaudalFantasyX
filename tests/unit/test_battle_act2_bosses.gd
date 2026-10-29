extends TestCase
## M3-BPR-408: the Act II bosses' camera language, keyed by enemy id because their skills are not written yet. The
## Avalanche Ram is framed low and side-on (camera.enemy_by_actor; its own style via style_by_actor once audio has
## it), and any charge it gathers closes the camera in (camera.pressure.by_enemy) and paws the ground (charge "*").
## The Lamp Engine's phase change to `opened` plays its moment: the core rises, then the party steadies in turn.
## Sandbox foes stand in for the bosses (renamed), so the data is exercised before the bosses' rows exist.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261027

var ctl: BattleController


func before_each() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	ctl.show_damage_numbers = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var active: Array[StringName] = [&"rhen", &"asha"]
	var none: Array[StringName] = []
	ctl.start_battle(active, none, &"sandbox_reef", SEED)


func test_the_ram_is_framed_low_and_side_on() -> void:
	var data := ctl.stage.choreo.data
	var pair := (data["camera"]["enemy_by_actor"] as Dictionary)["avalanche_ram"] as Dictionary
	assert_true((data["camera"]["shots"] as Dictionary).has(str(pair["lead"])), "framed on a real shot")
	# style_by_actor: an actor's own style by skill kind (the Ram's charge style waits on its sound row, M3-BPR-410).
	var tuned := data.duplicate(true)
	tuned["style_by_actor"] = {"avalanche_ram": {"physical": "toll"}}
	var r := ActionResult.new()
	r.actor_id = &"avalanche_ram#1"
	r.skill_id = &"attack"
	r.hits = [{"target_id": &"rhen", "hit": true, "crit": false, "amount": 30, "statuses_added": []}]
	assert_eq(BattleChoreoPlan.style_id_for(tuned, ctl.engine, r), "toll", "its physical blows take its own style")
	r.actor_id = &"reef_crab#1"
	assert_eq(BattleChoreoPlan.style_id_for(tuned, ctl.engine, r), "melee", "a regular foe keeps the melee")
	_free()


func test_the_rams_charge_closes_the_camera_in() -> void:
	var cam := ctl.stage.choreo.camera
	var foe := ctl.engine.enemies[0]
	foe.id = &"avalanche_ram#1"
	foe.charge_skill = &"some_future_charge"  # any skill: the row is by enemy
	foe.charge_left = 2
	var two := cam.rest_fov()
	foe.charge_left = 1
	var one := cam.rest_fov()
	assert_true(two < cam.default_fov and one < two, "a step each turn (%.2f, %.2f)" % [two, one])
	_free()


func test_the_lamp_engine_opens_with_a_moment() -> void:
	var foe := ctl.engine.enemies[0]
	var row := (ctl.stage.choreo.data["bosses"] as Dictionary)["lamp_engine"] as Dictionary
	var boss := BattleBossChoreo.new()
	boss.attach(ctl.stage.choreo, ctl.engine, foe.id, row)
	ctl.engine.phase_changed.emit(foe, &"opened")
	assert_eq(boss.moments, [&"opened"] as Array[StringName], "the opening plays its moment")
	ctl.engine.phase_changed.emit(foe, &"some_other_phase")
	assert_eq(boss.moments.size(), 1, "other phases play none")
	var ram := (ctl.stage.choreo.data["bosses"] as Dictionary)["avalanche_ram"] as Dictionary
	var rb := BattleBossChoreo.new()
	rb.attach(ctl.stage.choreo, ctl.engine, foe.id, ram)
	ctl.engine.charge_started.emit(foe, &"some_future_charge", 2)
	assert_eq(rb.moments, [&"gather"] as Array[StringName], "any charge it gathers paws the ground")
	_free()


func test_the_drowner_tears_free_with_a_moment() -> void:
	# M3-BPR-418: the Mangrove Drowner's `uprooted` phase (its creatures.json row) plays its moment, as the Lamp
	# Engine's `opened` does.
	var foe := ctl.engine.enemies[0]
	var row := (ctl.stage.choreo.data["bosses"] as Dictionary)["mangrove_drowner"] as Dictionary
	var phase_ids := (CreatureActor.row_for(&"mangrove_drowner").get("phases", {}) as Dictionary).keys()
	assert_true(phase_ids.has("uprooted"), "the creature's own phase id")
	var boss := BattleBossChoreo.new()
	boss.attach(ctl.stage.choreo, ctl.engine, foe.id, row)
	ctl.engine.phase_changed.emit(foe, &"uprooted")
	assert_eq(boss.moments, [&"uprooted"] as Array[StringName], "tearing free plays its moment")
	_free()


func test_the_wakefin_sinks_its_blade_and_the_dark_closes_in() -> void:
	# M3-BPR-418: in the dark its telegraph is the blade going under (no light added), and the camera closes in.
	var foe := ctl.engine.enemies[0]
	var row := (ctl.stage.choreo.data["bosses"] as Dictionary)["wakefin"] as Dictionary
	var gather := row["gather"] as Dictionary
	assert_true(float(gather["crouch_m"]) > 0.0 and float(gather["lift_m"]) == 0.0, "the blade goes under")
	var boss := BattleBossChoreo.new()
	boss.attach(ctl.stage.choreo, ctl.engine, foe.id, row)
	ctl.engine.charge_started.emit(foe, &"some_future_charge", 2)
	assert_eq(boss.moments, [&"gather"] as Array[StringName], "any charge it gathers")
	var cam := ctl.stage.choreo.camera
	foe.id = &"wakefin#1"
	foe.charge_skill = &"some_future_charge"
	foe.charge_left = 2
	var two := cam.rest_fov()
	foe.charge_left = 1
	assert_true(two < cam.default_fov and cam.rest_fov() < two, "a step each turn")
	_free()


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
