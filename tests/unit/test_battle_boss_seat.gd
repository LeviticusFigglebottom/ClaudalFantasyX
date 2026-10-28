extends TestCase
## M3-CRB-011 (pillar 4): a lone Act I boss with a battle_sandbox.json `boss_seats` mark stands on it at spawn, not on
## EnemySlots/Slot0, so the default camera sees the whole silhouette; a boss without a mark keeps Slot0.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
## Encounter -> its lone boss.
const SEATED := {&"ch04_spar_wraith": &"spar_wraith", &"ch05_cinder_matron": &"cinder_matron"}
const UNSEATED := {&"ch01_hullgnaw": &"hullgnaw"}
## The line-up may nudge a fighter this far off its mark (choreo.json lineup_max_shift_m 0.6).
const TOL_M := 0.65

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
