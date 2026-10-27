extends TestCase
## M3-BPR-406: the Ch8 set-piece freeze-frames reach their beats headless (the renders are the PC's or the Lead's):
## Toma takes the crawler's grip for the stair at contact, Rhen's riposte lands on the crawler, and a withdrawing
## crawler holds half-way back from its mark, still visible.

const SHOTS := "res://game/battle/scene/shots/battle_ch08_%s.tscn"
const EPS := 0.01

var ctl: BattleController
var shot: Node


func _open(beat: String) -> BattleChoreo:
	ctl = (load(SHOTS % beat) as PackedScene).instantiate() as BattleController
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	shot = ctl.get_node(^"SetPieceBeatShot")
	shot.call(&"_start")
	return ctl.stage.choreo


func test_the_intercept_freezes_on_toma_at_contact() -> void:
	var choreo := _open("intercept")
	assert_true(choreo.frozen and choreo.playing(), "frozen mid-action")
	var plan := choreo.current()
	assert_eq(String(plan["actor"]).get_slice("#", 0), "tide_crawler", "the crawler strikes")
	assert_eq(plan["targets"], [&"toma"] as Array[StringName], "and the blow lands on Toma, who covers the stair")
	assert_true(absf(choreo.time() - float(plan["contact"]) - float(shot.get(&"offset_sec"))) < EPS, "at contact")
	_free()


func test_the_counter_freezes_as_the_riposte_lands() -> void:
	var choreo := _open("counter")
	var plan := choreo.current()
	var at := -1.0
	for re: Dictionary in plan["reactions"]:
		if str(re["counter_by"]) == "rhen":
			at = float(re["at"])
	assert_true(at > float(plan["strike_end"]), "the riposte comes after the claw")
	assert_true(absf(choreo.time() - at - float(shot.get(&"offset_sec"))) < EPS, "frozen on it")
	_free()


func test_the_withdrawal_holds_half_way() -> void:
	_open("withdraw")
	var foe: BattleCombatant = null
	for e in ctl.engine.enemies:
		if e.withdrawn:
			foe = e
	assert_true(foe != null, "a crawler withdrew")
	var f := ctl.stage.stand_in(foe.id)
	var moved := (f.position - ctl.stage.choreo.home_origin(foe.id)).length()
	var back := float(ctl.stage.choreo.data["withdraw"]["back_m"])
	assert_true(f.visible, "still on stage")
	assert_true(moved > 0.05 and moved < back - 0.05, "part of the way back (%.2f of %.2f m)" % [moved, back])
	_free()


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
