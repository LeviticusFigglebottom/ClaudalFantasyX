extends TestCase
## M2-BPR-09: battle targeting with the mouse. Hovering a candidate aims the cursor at it, a left click confirms
## (the keyboard's own actions), the member to swap out is picked the same way, a right click cancels, and the
## mouse does nothing over a non-candidate or outside the pick states.

const SANDBOX := "res://game/battle/scene/battle_sandbox.tscn"
const SEED := 20261022

var ctl: BattleController
var pick: BattleMousePick


func before_each() -> void:
	ctl = (load(SANDBOX) as PackedScene).instantiate() as BattleController
	ctl.auto_start = false
	ctl.pacing_scale = 0.0
	ctl.persist_progress = false
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(ctl)
	var active: Array[StringName] = [&"rhen", &"asha"]
	var reserve: Array[StringName] = [&"toma", &"ysolde"]
	var p := LatticeProgress.new(LatticeBoard.load_board(), LatticeRules.load_file())
	for cid: StringName in [&"rhen", &"asha", &"toma", &"ysolde"]:
		p.add_character(cid)
	ctl.start_battle(active, reserve, &"sandbox_reef", SEED, p)
	pick = ctl.stage.get_node(^"BattleMousePick") as BattleMousePick


func test_the_stage_builds_it_and_it_sleeps_outside_the_pick_states() -> void:
	assert_true(pick != null)
	assert_eq(ctl.state, BattleController.STATE_COMMAND)
	assert_false(pick.active())
	assert_false(pick.handle(_motion(_point(_foes()[0]))), "a menu state ignores the mouse here")
	_free()


func test_hovering_a_foe_aims_at_it_and_a_click_confirms() -> void:
	_to_target(BattleMenus.ATTACK_SKILL)
	var cands := ctl.candidate_ids()
	assert_true(cands.size() >= 2, "several foes to choose from")
	var other := cands[1] if ctl.picked_ids()[0] == cands[0] else cands[0]
	assert_eq(pick.pick_at(_point(other)), other, "the fighter under the pointer")
	assert_true(pick.handle(_motion(_point(other))))
	assert_eq(ctl.picked_ids(), [other] as Array[StringName], "the cursor follows the hover")
	var actor := ctl.current_actor_id()
	assert_true(pick.handle(_button(_point(other), MOUSE_BUTTON_LEFT)))
	assert_ne(ctl.state, BattleController.STATE_TARGET, "the click confirmed")
	assert_true(ctl.engine.find(actor) != null)
	_free()


func test_empty_space_and_non_candidates_do_nothing() -> void:
	_to_target(BattleMenus.ATTACK_SKILL)
	var picked := ctl.picked_ids()
	assert_eq(pick.pick_at(Vector2(-500, -500)), &"")
	assert_false(pick.handle(_button(Vector2(-500, -500), MOUSE_BUTTON_LEFT)))
	assert_eq(pick.pick_at(_point(&"rhen")), &"", "an ally is not a candidate for Attack")
	assert_false(pick.handle(_button(_point(&"rhen"), MOUSE_BUTTON_LEFT)))
	assert_eq(ctl.state, BattleController.STATE_TARGET)
	assert_eq(ctl.picked_ids(), picked)
	_free()


func test_a_right_click_cancels() -> void:
	_to_target(BattleMenus.ATTACK_SKILL)
	if ctl.get_node_or_null(^"/root/UiInput") != null:  # UiInput turns it into ui_cancel for every screen
		_free()
		return
	assert_true(pick.handle(_button(Vector2.ZERO, MOUSE_BUTTON_RIGHT)))
	assert_ne(ctl.state, BattleController.STATE_TARGET)
	_free()


func test_the_member_to_swap_out_is_picked_by_click() -> void:
	ctl.hud.commands.select(BattleMenus.ROW_SWAP)
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_SWAP_IN)
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_SWAP_OUT)
	var out := &"asha" if ctl.candidate_ids().has(&"asha") else ctl.candidate_ids()[0]
	assert_true(pick.handle(_button(_point(out), MOUSE_BUTTON_LEFT)))
	assert_false(BattleIds.of(ctl.engine.party_active).has(out), "%s swapped out" % out)
	_free()


func _to_target(skill: StringName) -> void:
	ctl.hud.commands.select(skill)
	_press(&"ui_accept")
	assert_eq(ctl.state, BattleController.STATE_TARGET)


func _foes() -> Array[StringName]:
	var out: Array[StringName] = []
	for e in ctl.engine.enemies:
		out.append(e.id)
	return out


## The middle of `cid`'s fighter on screen.
func _point(cid: StringName) -> Vector2:
	var f := ctl.stage.stand_in(cid)
	var cam := ctl.stage.camera
	return (cam.unproject_position(f.global_position) + cam.unproject_position(f.head_position())) * 0.5


func _motion(at: Vector2) -> InputEventMouseMotion:
	var ev := InputEventMouseMotion.new()
	ev.position = at
	return ev


func _button(at: Vector2, button: MouseButton) -> InputEventMouseButton:
	var ev := InputEventMouseButton.new()
	ev.position = at
	ev.button_index = button
	ev.pressed = true
	return ev


func _press(action: StringName) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	ctl.handle_input(ev)


func _free() -> void:
	ctl.get_parent().remove_child(ctl)
	ctl.free()
