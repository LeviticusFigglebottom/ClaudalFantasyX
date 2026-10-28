extends TestCase
## M3-BPR-420 / M3-HER-1148 (ADR 0041): each Act I boss besides the Drownbell has its set-piece VFX
## (boss_vfx.json kind set_piece, BattleBossSetPiece): its gather on each turn of a charge, a moment per phase, and its
## fall. The Drownbell keeps its own rig (BattleBossVfx), and no set piece doubles it.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const FIGHTS := {
	&"ch01_hullgnaw": [&"rhen"],
	&"ch04_spar_wraith": [&"rhen", &"asha", &"toma"],
	&"ch05_cinder_matron": [&"rhen", &"asha", &"toma"],
	&"ch06_inquisitor": [&"rhen", &"asha", &"toma"],
	&"undertows_reach": [&"rhen", &"asha", &"liss"],
}

var ctl: BattleController


func _start(enc: StringName, party: Array) -> BattleVfx:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var p: Array[StringName] = []
	p.assign(party)
	ctl.start_battle(p, [], enc, 20261028)
	return ctl.stage.get_node(^"BattleVfx") as BattleVfx


func test_each_boss_plays_its_gather_phases_and_fall() -> void:
	var rows := BattleBossVfx.load_data()["bosses"] as Dictionary
	for enc: StringName in FIGHTS:
		var vfx := _start(enc, FIGHTS[enc] as Array)
		var sets := vfx.find_children("SetPiece_*", "BattleBossSetPiece", false, false)
		assert_eq(sets.size(), 1, "%s has its set piece" % enc)
		var sp := sets[0] as BattleBossSetPiece
		var boss := ctl.engine.find(sp.boss_id)
		var row := rows[BattleVfx.base_id(sp.boss_id)] as Dictionary
		var want: Array = []
		if row.has("gather"):
			ctl.engine.charge_started.emit(boss, &"any_charge", 2)
			want.append(["gather", row["gather"]])
		for phase: String in row.get("phases", {}):
			ctl.engine.phase_changed.emit(boss, StringName(phase))
			want.append(["phase", row["phases"][phase]])
		if row.has("ko"):
			boss.hp = 0
			ctl.engine.action_resolved.emit(ActionResult.new())
			ctl.stage.choreo.contact.emit(ActionResult.new())
			want.append(["ko", row["ko"]])
		assert_eq(sp.played, want, "%s: its moments in order, once each" % enc)
		for m: Array in want:
			assert_true(vfx.played.has(StringName(str(m[1]))), "%s plays %s" % [enc, m[1]])
		_free()


func test_the_drownbell_keeps_its_own_rig() -> void:
	var vfx := _start(&"drownbell", [&"rhen", &"asha", &"toma"])
	assert_true(vfx.boss != null, "the Drownbell's rig")
	assert_eq(vfx.find_children("SetPiece_*", "BattleBossSetPiece", false, false).size(), 0, "no set piece doubles it")
	_free()


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
