extends TestCase
## M2-RND-04: the Drownbell's set piece on the real battle scene and data. Its data names real swatches, effects
## and skills and the haluna.md flood; it attaches only to a boss; the toll, rim hits and break, the Flood phase,
## polyps, mends and Call Ilun each play their moment; the flood rig is the scene's one water-level publisher
## (also across a retry) and resets the global when the battle leaves; the bell's motes are held; reduced
## motion slows and dims the shockwave.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const PALETTE := "res://docs/kb/art/palette.json"
const SEED := 20261023

var ctl: BattleController


func before_each() -> void:
	var packed := load(SANDBOX) as PackedScene
	ctl = packed.instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)


func test_data_names_swatches_effects_skills_and_the_haluna_flood() -> void:
	var data := BattleBossVfx.load_data()
	var swatches := (JSON.parse_string(FileAccess.get_file_as_string(PALETTE)) as Dictionary)["swatches"] as Dictionary
	var effects := BattleVfx.load_data()["effects"] as Dictionary
	var db := BattleDB.load_default()
	var bosses := data["bosses"] as Dictionary
	for boss: String in bosses:
		assert_true(db.enemies.has(StringName(boss)), "%s is an enemy" % boss)
		var row := bosses[boss] as Dictionary
		for part: String in row:
			if not row[part] is Dictionary:
				continue  # a set piece's kind, note and effect ids (M3-BPR-420; test_battle_boss_set_piece plays them)
			var block := row[part] as Dictionary
			for key: String in block.get("swatches", {}):
				var sw := str((block["swatches"] as Dictionary)[key])
				assert_true(swatches.has(sw), "%s.%s: no swatch %s" % [boss, part, sw])
				assert_eq(str(block[key]).to_upper(), str((swatches[sw] as Dictionary)["hex"]).to_upper(), part + key)
			for key in ["gather", "flash", "hit", "break", "rise", "mend"]:
				if block.has(key):
					assert_true(effects.has(str(block[key])), "%s.%s.%s is an effect" % [boss, part, key])
			for key in ["skill", "charge_skill", "mend_skill"]:
				if block.has(key):
					assert_true(db.skills.has(StringName(str(block[key]))), "%s.%s.%s is a skill" % [boss, part, key])
	var flood := (bosses["drownbell"] as Dictionary)["flood"] as Dictionary
	assert_eq([float(flood["from_m"]), float(flood["to_m"]), float(flood["rise_s"])], [-0.7, 0.6, 8.0], "haluna.md 2.2")


func test_only_a_boss_gets_a_set_piece() -> void:
	ctl.start_battle([&"rhen", &"asha"] as Array[StringName], [], &"sandbox_reef", SEED)
	assert_true(_vfx().boss == null, "no boss row: no set piece")
	_free()


func test_the_flood_rig_is_the_one_publisher_across_a_retry() -> void:
	_start()
	var boss := _vfx().boss
	assert_true(boss != null)
	assert_true(boss.water != null and boss.water.publishes_water_level)
	assert_between(boss.water_y(), -0.7 - 1e-4, -0.7 + 1e-4, "the fight opens at low tide")
	assert_false((ctl.get_node("Arena/Sea") as Node3D).visible, "the arena's flat sea gives way to the rig's")
	_start()
	assert_eq(ctl.stage.find_children("BattleVfx", "", false, false).size(), 1, "a retry replaces the view")
	assert_eq(ctl.get_tree().get_node_count_in_group(WaterSurface.LEVEL_PUBLISHERS_GROUP), 1, "one publisher")
	var tree := ctl.get_tree()
	_free()
	# Leaving, the water resets hymn_water_level (WaterSurface._exit_tree; the headless renderer keeps no globals).
	assert_eq(tree.get_node_count_in_group(WaterSurface.LEVEL_PUBLISHERS_GROUP), 0, "no publisher left behind")


func test_the_toll_telegraph_fires_and_breaks() -> void:
	_start()
	var vfx := _vfx()
	var bell := ctl.engine.enemies[0]
	bell.charge_skill = &"toll"
	bell.charge_left = 2
	ctl.engine.charge_started.emit(bell, &"toll", 2)
	assert_true(vfx.played.has(&"toll_gather"), "held motes gather on the hood")
	assert_eq(vfx.boss.moments, [&"telegraph"] as Array[StringName])
	var toll := ActionResult.new()
	toll.actor_id = bell.id
	toll.skill_id = &"toll"
	ctl.engine.action_resolved.emit(toll)
	assert_true(vfx.boss.ring.visible, "the shockwave ring")
	assert_true(vfx.played.has(&"flash_toll"), "the capped pulse")
	var rim := ActionResult.new()
	rim.actor_id = &"rhen"
	rim.skill_id = &"attack"
	var rim_hit := {"target_id": bell.id, "hit": true, "crit": false, "amount": 10, "weak_point_hits": 1}
	rim.hits = [rim_hit] as Array[Dictionary]
	ctl.engine.action_resolved.emit(rim)
	assert_true(vfx.played.has(&"rim_crack"))
	ctl.engine.charge_broken.emit(bell, &"toll")
	assert_true(vfx.played.has(&"rim_break"))
	assert_eq(vfx.boss.moments.slice(1), [&"toll", &"rim_hit", &"rim_break"] as Array[StringName])
	_free()


func test_the_flood_rises_polyps_glow_and_ilun_clears_it() -> void:
	_start()
	var boss := _vfx().boss
	var bell := ctl.engine.enemies[0]
	bell.hp = bell.max_hp * 40 / 100
	BossMechanics.check_phases(ctl.engine)
	assert_true(boss.moments.has(&"flood"))
	assert_between(boss.flood_target_m, 0.6 - 1e-4, 0.6 + 1e-4, "the water rises to +0.6 m")
	var polyps := ctl.engine.enemies.slice(1)
	assert_eq(boss.polyp_lights.size(), polyps.size(), "a cyan light per polyp")
	var mend := ActionResult.new()
	mend.actor_id = polyps[0].id
	mend.skill_id = &"polyp_mend"
	mend.hits = [{"target_id": bell.id, "hit": true, "crit": false, "amount": -20}] as Array[Dictionary]
	ctl.engine.action_resolved.emit(mend)
	assert_true(_vfx().played.has(&"polyp_mend"), "held motes flow to the bell")
	ctl.engine.field_cleared.emit(&"flood", polyps as Array[BattleCombatant])
	assert_true(boss.moments.has(&"floodnet"))
	assert_true(boss.net.visible, "Ilun's bound net")
	assert_between(boss.flood_target_m, -0.7 - 1e-4, -0.7 + 1e-4, "the water falls back")
	assert_eq(boss.polyp_lights.size(), 0, "the polyps' lights go with the field")
	_free()


func test_the_bells_motes_are_held_and_reduced_motion_is_gentler() -> void:
	_start()
	var vfx := _vfx()
	var bell := ctl.engine.enemies[0]
	bell.hp = 0
	var r := ActionResult.new()
	r.actor_id = &"rhen"
	r.skill_id = &"attack"
	r.hits = [{"target_id": bell.id, "hit": true, "crit": false, "amount": 50}] as Array[Dictionary]
	var ids := vfx.effects_for(r).map(func(e: Dictionary) -> StringName: return e["effect"])
	assert_true(ids.has(&"bell_release"), "seaward, held")
	assert_false(ids.has(&"ko_release"), "never the rising release")
	assert_eq(vfx.boss._rm_scale("ring_s_scale"), 1.0)
	vfx.reduced_motion = true
	assert_true(vfx.boss._rm_scale("ring_s_scale") > 1.0, "a slower ring")
	assert_true(vfx.boss._rm_scale("ring_alpha_scale") < 1.0, "a fainter ring")
	_free()


func _start() -> void:
	ctl.start_battle([&"rhen", &"asha", &"toma"] as Array[StringName], [], &"drownbell", SEED)


func _vfx() -> BattleVfx:
	return ctl.stage.get_node("BattleVfx") as BattleVfx


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
