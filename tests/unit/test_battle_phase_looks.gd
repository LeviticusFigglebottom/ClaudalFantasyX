extends TestCase
## M3-BPR-406 (ADR 0100; set_piece_battles.md §8): the set piece's phases read on stage. The Reach's Breach makes it
## untargetable (its stand-in fades to phase_looks.untargetable.alpha, then comes back) and damage-immune (a blow on
## it plays the `immune` reaction: a hard stop with no recoil, still under reduced motion).

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261027
const REACH := "undertows_reach"
const BREACH_HP_PCT := 25

var ctl: BattleController


func before_each() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_battle([&"rhen", &"asha", &"liss"] as Array[StringName], [], &"undertows_reach", SEED)


func _reach() -> BattleCombatant:
	for e in ctl.engine.enemies:
		if String(e.id).get_slice("#", 0) == REACH:
			return e
	return null


func _transparency(cid: StringName) -> float:
	var most := 0.0
	for n in ctl.stage.stand_in(cid).find_children("*", "GeometryInstance3D", true, false):
		most = maxf(most, (n as GeometryInstance3D).transparency)
	return most


func test_the_breach_veils_the_reach_and_its_end_unveils_it() -> void:
	var reach := _reach()
	assert_true(reach != null, "the Reach is on the field")
	var looks := BattlePhaseLooks.of(ctl.stage)
	assert_false(looks.veiled.has(reach.id), "targetable at the start")
	reach.hp = reach.max_hp * BREACH_HP_PCT / 100
	BossMechanics.check_phases(ctl.engine)
	assert_true(reach.untargetable, "the Breach phase")
	assert_true(looks.veiled.has(reach.id), "veiled by the phase change")
	var alpha := float(looks.cfg["untargetable"]["alpha"])
	assert_true(absf(_transparency(reach.id) - (1.0 - alpha)) < 0.001, "faded to its alpha")
	reach.untargetable = false
	looks.refresh()
	assert_false(looks.veiled.has(reach.id), "unveiled")
	assert_eq(_transparency(reach.id), 0.0, "whole again")
	_free()


func test_a_blow_on_a_damage_immune_foe_stops_dead() -> void:
	var reach := _reach()
	reach.damage_immune = true
	var r := ActionResult.new()
	r.actor_id = &"rhen"
	r.skill_id = &"attack"
	r.hits = [{"target_id": reach.id, "hit": true, "crit": false, "amount": 0, "statuses_added": []}]
	var data := BattleChoreo.load_data()
	var plan := BattleChoreoPlan.plan_for(data, ctl.engine, r)
	assert_eq(str(plan["reactions"][0]["kind"]), BattleChoreo.REACT_IMMUNE, "the immune reaction")
	var rr := (plan["reactions"][0] as Dictionary).duplicate()
	rr["dir"] = Vector3.BACK
	rr["clip"] = false
	var c := float(rr["at"])
	var sec := float(data["reaction"]["immune"]["sec"])
	var pose := BattleChoreoPlan.reaction_pose(data, rr, c + sec * 0.1, c, 1.0, 1.0)
	assert_true((pose[0] as Vector3).length() > 0.0, "a shudder")
	assert_true(absf((pose[0] as Vector3).dot(Vector3.BACK)) < 0.001, "no recoil along the blow")
	assert_eq(float(pose[2]), 0.0, "no tilt")
	var soft := BattleChoreoPlan.reaction_pose(data, rr, c + sec * 0.1, c, 1.0, 0.0)
	assert_eq((soft[0] as Vector3).length(), 0.0, "still under reduced motion")
	reach.damage_immune = false
	assert_eq((BattleChoreoPlan.plan_for(data, ctl.engine, r)["reactions"] as Array).size(), 0, "not immune: nothing")
	_free()


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
