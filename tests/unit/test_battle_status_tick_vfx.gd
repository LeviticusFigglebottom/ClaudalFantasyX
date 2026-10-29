extends TestCase
## M3-BPR-424 (the Lead: status-tick VFX for every Act I fighter): each end-of-turn effect shows on its fighter, by
## map.ticks: poison, regen (a Zombie's regen hurts: the poison tick), a Doom count and Doom falling, and a turn lost to
## Sleep or Stop. Regen is water, never glimmer; Doom never rises gold.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"

var ctl: BattleController


func _start() -> BattleVfx:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_battle([&"rhen", &"asha"] as Array[StringName], [], &"sandbox_reef", 20261028)
	var vfx := ctl.stage.get_node(^"BattleVfx") as BattleVfx
	vfx.played.clear()
	return vfx


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()


func test_each_tick_plays_on_its_fighter() -> void:
	var vfx := _start()
	var foe := ctl.engine.enemies[0]
	var hero := ctl.engine.party_active[0]
	var changes: Array[Dictionary] = [
		{"target_id": foe.id, "cause": &"poison", "amount": 12},
		{"target_id": hero.id, "cause": &"regen", "amount": -20},
		{"target_id": foe.id, "cause": &"regen", "amount": 8},  # under Zombie: it hurts
		{"target_id": hero.id, "cause": &"doom_tick", "amount": 0, "doom": 2},
		{"target_id": foe.id, "cause": &"doom", "amount": 300},
	]
	ctl.engine.turn_ended.emit(foe, changes)
	assert_eq(
		vfx.played,
		[&"tick_poison", &"tick_regen", &"tick_poison", &"tick_doom", &"tick_doom_fall"] as Array[StringName]
	)
	_free()


func test_a_lost_turn_shows_on_the_sleeper() -> void:
	var vfx := _start()
	var foe := ctl.engine.enemies[0]
	var none: Array[Dictionary] = []
	ctl.engine.turn_lost.emit(foe, &"sleep", none)
	ctl.engine.turn_lost.emit(foe, &"stop", none)
	assert_eq(vfx.played, [&"tick_sleep", &"tick_stop"] as Array[StringName])
	_free()


func test_regen_is_water_and_doom_never_rises_gold() -> void:
	var fx := JSON.parse_string(FileAccess.get_file_as_string("res://game/data/vfx/battle/effects.json")) as Dictionary
	for eid: String in ["tick_regen", "tick_doom", "tick_doom_fall"]:
		for l: Dictionary in (fx["effects"] as Dictionary)[eid]["layers"]:
			for sw: Variant in l["swatches"]:
				assert_false(str(sw).begins_with("glimmer"), "%s: no glimmer (%s)" % [eid, sw])
