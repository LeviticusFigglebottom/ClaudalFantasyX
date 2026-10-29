extends TestCase
## M3-CRB-011 (pillar 4): a lone Act I boss with a battle_sandbox.json `boss_seats` mark stands on it at spawn, not on
## EnemySlots/Slot0, so the default camera sees the whole silhouette; a boss without a mark keeps Slot0.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
## Encounter -> its lone boss.
const SEATED := {
	&"ch04_spar_wraith": &"spar_wraith", &"ch05_cinder_matron": &"cinder_matron", &"undertows_reach": &"undertows_reach"
}
const UNSEATED := {&"ch01_hullgnaw": &"hullgnaw"}
## The line-up may nudge a fighter this far off its mark (choreo.json lineup_max_shift_m 0.6).
const TOL_M := 0.65
## GPU QA row 36: the Reach's arm stays out of the party lane in every clip. Its bones below LANE_HEIGHT_M stay this far
## short of the nearest party member's mark (the mesh runs about a hand past the last digit bone).
const LANE_HEIGHT_M := 4.0
const LANE_CLEAR_M := 1.5
const LANE_SAMPLES := 16

var ctl: BattleController


func after_each() -> void:
	if ctl != null and is_instance_valid(ctl):
		ctl.get_parent().remove_child(ctl)
		ctl.free()
	ctl = null


func test_a_lone_boss_with_a_seat_stands_on_it() -> void:
	var seats := BattleStage.config().get("boss_seats", {}) as Dictionary
	for enc: StringName in SEATED:
		var boss: StringName = SEATED[enc]
		var v := seats[String(boss)] as Array
		var want := Vector3(float(v[0]), float(v[1]), float(v[2]))
		var at := _boss_local(enc, boss)
		assert_true(at.distance_to(want) <= TOL_M, "%s stands on its seat %s (at %s)" % [boss, want, at])
		after_each()


func test_a_boss_without_a_seat_keeps_slot0() -> void:
	for enc: StringName in UNSEATED:
		var boss: StringName = UNSEATED[enc]
		var at := _boss_local(enc, boss)
		var slot0 := (_slots().get_child(0) as Node3D).position
		assert_true(at.distance_to(slot0) <= TOL_M, "%s stays on Slot0 %s (at %s)" % [boss, slot0, at])
		after_each()


func test_the_reach_keeps_its_arm_out_of_the_party_lane() -> void:
	_boss_local(&"undertows_reach", &"undertows_reach")
	var party_x := INF
	for c in ctl.engine.party_active:
		party_x = minf(party_x, _slots().to_local(ctl.stage.stand_in(c.id).global_position).x)
	var a := ctl.stage.stand_in(ctl.engine.enemies[0].id).actor()
	var player := a.find_children("*", "AnimationPlayer", true, false)[0] as AnimationPlayer
	var skel := a.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	for clip in player.get_animation_list():
		var reach := -INF
		for i in LANE_SAMPLES + 1:
			player.play(clip)
			player.seek(player.current_animation_length * i / LANE_SAMPLES, true)
			skel.force_update_all_bone_transforms()
			for b in skel.get_bone_count():
				var at := _slots().to_local(skel.global_transform * skel.get_bone_global_pose(b).origin)
				if not skel.get_bone_name(b).begins_with("vfx_") and at.y < LANE_HEIGHT_M:
					reach = maxf(reach, at.x)
		assert_true(
			reach <= party_x - LANE_CLEAR_M,
			"the Reach's %s stays out of the party lane (x %.2f, party %.2f)" % [clip, reach, party_x]
		)


## The boss's stand-in position in EnemySlots space after the battle starts.
func _boss_local(enc: StringName, boss: StringName) -> Vector3:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	ctl.start_battle([&"rhen", &"asha", &"toma"] as Array[StringName], [], enc, 20261028)
	var cid := boss
	for e in ctl.engine.enemies:
		if String(e.id).get_slice("#", 0) == String(boss):
			cid = e.id
	var f := ctl.stage.stand_in(cid)
	assert_true(f != null, "%s has a stand-in" % boss)
	return _slots().to_local(f.global_position) if f != null else Vector3.INF


func _slots() -> Node3D:
	return ctl.stage.get_node("%EnemySlots") as Node3D
