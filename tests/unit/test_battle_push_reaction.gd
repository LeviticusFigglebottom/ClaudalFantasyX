extends TestCase
## M3-BPR-411 (the VFX audit's fill on stage): a hit that only pushes its target down the timeline (the ward shoved
## back by Rope Dive, Grip the Stair or Hand Closes; a foe caught in the Drag Net) used to play no reaction at all.
## It now staggers the target back (choreo.json reaction.push): the stage agrees with the timeline (Pillar 4).


func _hit(target: StringName, amount: int, ticks: int) -> Dictionary:
	return {
		"target_id": target, "hit": true, "crit": false, "amount": amount, "statuses_added": [], "delay_ticks": ticks
	}


func _plan(hits: Array[Dictionary]) -> Dictionary:
	var r := ActionResult.new()
	r.actor_id = &"squall_wing#1"
	r.skill_id = &"rope_dive"
	r.hits = hits
	return BattleChoreoPlan.plan_for(BattleChoreo.load_data(), null, r)


func test_a_push_with_no_damage_staggers_its_target() -> void:
	var plan := _plan([_hit(&"ward", 0, 4)])
	assert_eq((plan["reactions"] as Array).size(), 1, "one reaction")
	assert_eq(str(plan["reactions"][0]["kind"]), BattleChoreo.REACT_PUSH, "a push")
	var r := (plan["reactions"][0] as Dictionary).duplicate()
	r["dir"] = Vector3.BACK
	r["clip"] = false
	var c := float(r["at"])
	var sec := float(BattleChoreo.load_data()["reaction"]["push"]["sec"])
	var pose := BattleChoreoPlan.reaction_pose(BattleChoreo.load_data(), r, c + sec * 0.5, c, 1.0, 1.0)
	assert_true((pose[0] as Vector3).length() > 0.1, "shoved back at mid-reaction")
	assert_true(float(pose[2]) > 0.0, "a small tilt")
	var soft := BattleChoreoPlan.reaction_pose(BattleChoreo.load_data(), r, c + sec * 0.5, c, 1.0, 0.0)
	assert_eq(float(soft[2]), 0.0, "no tilt under reduced motion")


func test_damage_still_wins_and_no_push_means_no_reaction() -> void:
	assert_eq(str(_plan([_hit(&"ward", 6, 4)])["reactions"][0]["kind"]), BattleChoreo.REACT_DAMAGE, "a blow")
	assert_eq((_plan([_hit(&"ward", 0, 0)])["reactions"] as Array).size(), 0, "nothing landed: no reaction")
