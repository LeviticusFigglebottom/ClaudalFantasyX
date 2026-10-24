class_name BattlePause
extends Node
## Pauses a battle (M2-MNU-04). A child of the battle sandbox's root (BattleController, so
## FieldBattle too): the pause action (battle_pause.json "action": P, Pause, pad Start) opens
## BattlePauseMenu over the HUD, which pauses the whole tree until it closes. Input reaches this
## node before its parent, so the controller never sees the press. Nothing happens while
## no fight is on or the result panel is up ("blocked_states"), while the controller builds a
## battle, or when the tree is already paused (another menu holds it).
## Cancel at the top of the command menu (Escape, pad B, or a right click: the mouse's way in,
## M2-UI-26) opens it too: there is nothing left to back out of there.
## Presentation (claude/battle-presentation): BattleChoreo, the camera director and every tween run
## in the tree's normal process mode, so the tree pause freezes them mid-beat and they resume
## where they were.

## The pause page while it is open (null otherwise).
var menu: BattlePauseMenu

var _blocked: Array[StringName] = []


func _ready() -> void:
	var d: Dictionary = BattlePauseMenu.create().load_layout()
	FieldInput.add_actions(d.get("action", {}) as Dictionary, 0.0)
	for s: Variant in d.get("blocked_states", []):
		_blocked.append(StringName(str(s)))
	_hook_commands.call_deferred()  # the parent controller's HUD is ready after this node's _ready


## Cancel on the command menu's root page opens the pause (M2-UI-26).
func _hook_commands() -> void:
	var ctl := get_parent() as BattleController
	if ctl != null and ctl.hud != null and not ctl.hud.commands.cancelled.is_connected(_on_commands_cancelled):
		ctl.hud.commands.cancelled.connect(_on_commands_cancelled)


func _on_commands_cancelled(_page: StringName) -> void:
	var ctl := get_parent() as BattleController
	if ctl != null and ctl.state == BattleController.STATE_COMMAND and ctl.hud.commands.depth() <= 1:
		pause()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(BattlePauseMenu.PAUSE_ACTION) and pause():
		get_viewport().set_input_as_handled()


## True when the battle may pause now.
func can_pause() -> bool:
	var ctl := get_parent() as BattleController
	if ctl == null or ctl.building or _blocked.has(ctl.state):
		return false
	return is_inside_tree() and not get_tree().paused and not is_paused()


func is_paused() -> bool:
	return menu != null and menu.is_open()


## Opens the pause page. Returns true when it opened.
func pause() -> bool:
	if not can_pause():
		return false
	menu = BattlePauseMenu.open_in(self)
	menu.closed.connect(func() -> void: menu = null)
	return true
