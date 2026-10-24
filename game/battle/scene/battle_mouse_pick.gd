class_name BattleMousePick
extends Node
## Battle targeting with the mouse (M2-BPR-09; the input-parity audit, ADR 0036). While the controller picks a
## target or the member to swap out, hovering a fighter that can be picked moves the cursor onto it and a left click
## confirms. Both go through BattleController.handle_input as the same actions the keyboard sends (ui_right steps
## the cursor, ui_accept confirms), so the mouse can never pick what the keyboard couldn't. A right click is Cancel:
## UiInput does that for every screen once it is in the tree; until then this does it here. BattleStage builds it,
## so the controller has no line for it. Only candidates react; in any other state the mouse does nothing here.

const PICK_STATES: Array[StringName] = [BattleController.STATE_TARGET, BattleController.STATE_SWAP_OUT]
const UI_INPUT_PATH := ^"/root/UiInput"
## A fighter's hit box on screen: its projected width (stand-in radius) times this, and this much past head and feet.
const WIDTH_SCALE := 1.25
const PAD_PX := 12.0

var _ctl: BattleController
var _stage: BattleStage


static func attached(stage: BattleStage) -> BattleMousePick:
	var p := BattleMousePick.new()
	p.name = "BattleMousePick"
	p._stage = stage
	p._ctl = stage.get_parent() as BattleController
	stage.add_child(p)
	return p


func active() -> bool:
	return _ctl != null and _ctl.engine != null and PICK_STATES.has(_ctl.state)


func _unhandled_input(event: InputEvent) -> void:
	if handle(event):
		get_viewport().set_input_as_handled()


## Routes one mouse event; true when it was used.
func handle(event: InputEvent) -> bool:
	if not active():
		return false
	var motion := event as InputEventMouseMotion
	if motion != null:
		return hover(motion.position)
	var mb := event as InputEventMouseButton
	if mb == null or not mb.pressed:
		return false
	if mb.button_index == MOUSE_BUTTON_LEFT:
		return click(mb.position)
	if mb.button_index == MOUSE_BUTTON_RIGHT and get_node_or_null(UI_INPUT_PATH) == null:
		return _send(&"ui_cancel")
	return false


## Aims at the candidate under `at` (viewport pixels); true when there is one.
func hover(at: Vector2) -> bool:
	var cid := pick_at(at)
	if cid == &"":
		return false
	var cands := _ctl.candidate_ids()
	var picked := _ctl.picked_ids()
	if picked.size() == 1 and picked[0] != cid:
		var steps := posmod(cands.find(cid) - cands.find(picked[0]), cands.size())
		for i in steps:
			_send(&"ui_right")
	return true


## Aims at the candidate under `at` and confirms; true when there was one.
func click(at: Vector2) -> bool:
	if not hover(at):
		return false
	return _send(&"ui_accept")


## The candidate whose fighter is under `at` (viewport pixels), the nearest one when two overlap; &"" for none.
func pick_at(at: Vector2) -> StringName:
	var cam := _stage.camera
	if cam == null:
		return &""
	var best: StringName = &""
	var best_dx := INF
	for cid in _ctl.candidate_ids():
		var f := _stage.stand_in(cid)
		if f == null or cam.is_position_behind(f.global_position):
			continue
		var feet := cam.unproject_position(f.global_position)
		var head := cam.unproject_position(f.head_position())
		var side := cam.global_transform.basis.x.normalized() * float(f.spec.get("radius", 0.3)) * WIDTH_SCALE
		var half := absf(cam.unproject_position(f.global_position + side).x - feet.x)
		var dx := absf(at.x - lerpf(feet.x, head.x, 0.5))
		var top := minf(head.y, feet.y) - PAD_PX
		var bottom := maxf(head.y, feet.y) + PAD_PX
		if dx <= half + PAD_PX and at.y >= top and at.y <= bottom and dx < best_dx:
			best = cid
			best_dx = dx
	return best


func _send(action: StringName) -> bool:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return _ctl.handle_input(ev)
