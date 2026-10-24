class_name BattlePointer
extends RefCounted
## The mouse on the battle stage (M2-UI-26, input parity). While a target is being picked, the
## pointer over a candidate (its fighter: a box from its marker point down to its feet; or, for a
## party member, its row on the party panel) aims at it, and a left click on it confirms, so the
## mouse picks targets the way the keys and the pad cycle them. A right click is Cancel everywhere
## (UiInput). The Swell inputs take the mouse in SwellRingView.pointer_event. A reader only: it
## answers "which candidate is under the pointer" and BattleController moves the cursor.
## Sizes: battle_hud.json "pointer".


## The index in ctl.candidate_ids() of the candidate under a mouse motion or a left press, or -1
## (no candidate there, or not such an event). Overlapping boxes go to the one centred nearest.
## The target pick's input (moved here from BattleController, which is at its line cap): hovering a
## fighter or its party row aims at it, Left / Up and Right / Down step the aim, Confirm (or a click
## on a candidate) chooses, Cancel backs out. `aim` is the controller's current target index.
## Returns true when the event was used.
static func handle_pick(ctl: BattleController, event: InputEvent, aim: int) -> bool:
	var hit := candidate_at(ctl, event)
	if hit >= 0 and hit != aim:
		ctl._cycle_target(hit - aim)
	if event.is_action_pressed(&"ui_left", true) or event.is_action_pressed(&"ui_up", true):
		ctl._cycle_target(-1)
	elif event.is_action_pressed(&"ui_right", true) or event.is_action_pressed(&"ui_down", true):
		ctl._cycle_target(1)
	elif event.is_action_pressed(&"ui_accept") or (hit >= 0 and is_click(event)):
		ctl._confirm_pick()
	elif event.is_action_pressed(&"ui_cancel"):
		ctl._cancel_pick()
	else:
		return hit >= 0
	return true


static func candidate_at(ctl: BattleController, event: InputEvent) -> int:
	if not (event is InputEventMouseMotion or is_click(event)):
		return -1
	var at := (event as InputEventMouse).position
	var ids := ctl.candidate_ids()
	var best := -1
	var best_d := INF
	for i in ids.size():
		for r in hit_rects(ctl, ids[i]):
			if r.has_point(at) and r.get_center().distance_squared_to(at) < best_d:
				best = i
				best_d = r.get_center().distance_squared_to(at)
	return best


## True for a left mouse button press.
static func is_click(event: InputEvent) -> bool:
	var mb := event as InputEventMouseButton
	return mb != null and mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT


## The boxes that aim at `cid`, in the viewport's coordinates (the HUD's and the pointer's): its
## fighter on the stage, and its party row when it has one.
static func hit_rects(ctl: BattleController, cid: StringName) -> Array[Rect2]:
	var out: Array[Rect2] = []
	var fighter := fighter_rect(ctl, cid)
	if fighter.has_area():
		out.append(fighter)
	var row := ctl.hud.party.row_for(cid)
	if row != null and row.is_visible_in_tree():
		var xf := row.get_global_transform_with_canvas()
		out.append(Rect2(xf.origin, row.size * xf.get_scale()))
	return out


## The fighter's box: from its marker point (BattleController.head_pos) down to its feet, as wide
## as half_width_of_height of that on each side (at least min_half_px). Empty without a camera.
static func fighter_rect(ctl: BattleController, cid: StringName) -> Rect2:
	var f := ctl.stage.stand_in(cid)
	if f == null or ctl.stage.camera == null:
		return Rect2()
	var m := HudLayout.section(&"pointer")
	var top := ctl.head_pos(cid)
	var foot := ctl.stage.camera.unproject_position(f.global_position)
	var h := maxf(foot.y - top.y, 0.0)
	var half := maxf(h * HudLayout.num(m, "half_width_of_height"), HudLayout.num(m, "min_half_px"))
	var mid := (top.x + foot.x) * 0.5
	return Rect2(mid - half, top.y, half * 2.0, h)
