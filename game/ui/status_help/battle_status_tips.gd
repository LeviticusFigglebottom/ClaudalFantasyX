class_name BattleStatusTips
extends Control
## Status help in battle (the human's playtest FAST-TRACK, 2026-11-03), attached under the HUD by
## BattleController (one line, listen-only, like BattleBarks):
##   - The status help key opens StatusHelpPanel: on the fighter being picked (a target or a swap), else
##     the foe of an open Read panel, else the acting hero, with that fighter's statuses listed first.
##   - The first time each status lands on a party member (its met flag, StatusHelpModel.met_flag, is
##     unset), its StatusTipCard waits for the party's next command and shows then, holding the battle.
##     The flag is set when the card shows, so a status that lands in a battle's last blow still teaches
##     next time; with the Accessibility setting tutorial_tips off no card shows, but the flag is set
##     (the Codex's Afflictions entry still opens). Only a live battle teaches: fixtures, captures and
##     tests that do not persist progress never raise a card or set a flag.
## Both views hold the battle (BattleHud.holds) and never touch the engine.

const NODE_NAME := &"StatusTips"
const HOLD := &"status_help"

var ctl: BattleController
var model: StatusHelpModel
var panel: StatusHelpPanel
var card: StatusTipCard
## Live battles teach (persist_progress and no fixture).
var live := false
## [{status, hero}] waiting for the next command, oldest first.
var pending: Array[Dictionary] = []

var _engine: BattleEngine
var _is_set: Callable
var _mark: Callable
var _tips_on: Callable


static func attached(controller: BattleController, engine: BattleEngine) -> BattleStatusTips:
	var old := controller.hud.get_node_or_null(NodePath(NODE_NAME))
	if old != null:
		controller.hud.remove_child(old)
		old.queue_free()
	var view := BattleStatusTips.new()
	view.name = NODE_NAME
	view.ctl = controller
	view.live = controller.persist_progress and controller.fixture == null
	controller.hud.add_child(view)
	view.attach(engine)
	return view


## `flag_check`, `flag_mark` and `tips_enabled` default to Game's flags and the Accessibility setting.
func _init(
	with_model: StatusHelpModel = null,
	flag_check: Callable = Callable(),
	flag_mark: Callable = Callable(),
	tips_enabled: Callable = Callable()
) -> void:
	model = with_model
	_is_set = flag_check if flag_check.is_valid() else func(f: StringName) -> bool: return bool(Game.get_flag(f))
	_mark = flag_mark if flag_mark.is_valid() else func(f: StringName) -> void: Game.set_flag(f, true)
	_tips_on = (
		tips_enabled if tips_enabled.is_valid() else func() -> bool: return UiSettings.shared().tutorial_tips_enabled()
	)
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _ready() -> void:
	if model == null:
		model = StatusHelpModel.shared()
	StatusHelpModel.ensure_action()
	panel = StatusHelpPanel.new(model)
	panel.name = &"StatusHelpPanel"
	add_child(panel)
	card = StatusTipCard.new(model)
	card.name = &"StatusTipCard"
	add_child(card)
	card.closed.connect(_on_card_closed)
	panel.closed.connect(show_next)  # a card's "every status" detour, then the next card
	if ctl != null and ctl.hud != null:
		ctl.hud.holds[HOLD] = is_open
		var ms := ctl.hud.motion_scale()
		panel.motion_scale = ms
		card.motion_scale = ms if ctl.pacing_scale > 0.0 else 0.0


func attach(engine: BattleEngine) -> void:
	_engine = engine
	engine.action_resolved.connect(_on_engine_changed.unbind(1))
	engine.turn_ended.connect(_on_engine_changed.unbind(2))
	engine.turn_lost.connect(_on_engine_changed.unbind(3))
	if ctl != null:
		ctl.state_changed.connect(_on_state_changed)


func is_open() -> bool:
	return (panel != null and panel.is_open()) or (card != null and card.is_open())


## Queues a card for every status on a party member that has not been met yet (once each).
func scan() -> void:
	if not live or _engine == null:
		return
	for c in _engine.party_active:
		for sid_v: Variant in c.statuses:
			var sid := StringName(str(sid_v))
			if not model.has(sid) or bool(_is_set.call(model.met_flag(sid))) or _queued(sid):
				continue
			pending.append({"status": sid, "hero": ctl.menus.display_name(c) if ctl != null else String(c.id)})


## Shows the oldest waiting card (when tips are on; with them off, every waiting status is marked met).
func show_next() -> bool:
	if pending.is_empty() or is_open():
		return false
	if not bool(_tips_on.call()):
		for p in pending:
			_mark.call(model.met_flag(StringName(str(p["status"]))))
		pending.clear()
		return false
	var p: Dictionary = pending.pop_front()
	var sid := StringName(str(p["status"]))
	_mark.call(model.met_flag(sid))
	_to_front()
	card.show_tip(sid, str(p["hero"]))
	return true


## Opens the help panel on `bearer`'s statuses (null: every status, none marked).
func open_help(bearer: BattleCombatant = null, focus: StringName = &"") -> void:
	var ids: Array[StringName] = []
	var who := ""
	if bearer != null:
		for sid_v: Variant in bearer.statuses:
			ids.append(StringName(str(sid_v)))
		who = ctl.menus.display_name(bearer) if ctl != null else String(bearer.id)
	_open(ids, who, focus)


## The fighter the help key is about: the one being picked, else the open Read's foe, else the actor.
func subject() -> BattleCombatant:
	if ctl == null or _engine == null:
		return null
	if ctl.state in [BattleController.STATE_TARGET, BattleController.STATE_SWAP_OUT]:
		var picked := ctl.picked_ids()
		if picked.size() == 1:
			return _engine.find(picked[0])
	var rp := ctl.hud.read_panel_if_open()
	if rp != null:
		return _engine.find(StringName(str(rp.page().get("target_id", ""))))
	return _engine.current if _engine.current != null and _engine.is_party_turn() else null


func handle_input(event: InputEvent) -> bool:
	if card.handle_input(event):
		return true
	if panel.is_open():
		return false  # the panel takes its own input
	if InputMap.has_action(StatusHelpPanel.ACTION) and event.is_action_pressed(StatusHelpPanel.ACTION):
		if ctl != null and ctl.state == BattleController.STATE_RESULT:
			return false
		open_help(subject())
		return true
	return false


func _unhandled_input(event: InputEvent) -> void:
	if handle_input(event):
		get_viewport().set_input_as_handled()


func _open(ids: Array[StringName], who: String, focus: StringName) -> void:
	_to_front()
	panel.open(ids, who, focus, panel.motion_scale > 0.0)


## Over the Read panel and every other HUD overlay, and first to take input.
func _to_front() -> void:
	if get_parent() != null:
		get_parent().move_child(self, -1)


func _queued(sid: StringName) -> bool:
	for p in pending:
		if StringName(str(p["status"])) == sid:
			return true
	return false


func _on_engine_changed() -> void:
	scan()


func _on_state_changed(new_state: StringName) -> void:
	if new_state == BattleController.STATE_COMMAND:
		scan()
		show_next()
	elif new_state == BattleController.STATE_RESULT:
		pending.clear()
		card.close()
		panel.close()


func _on_card_closed(open_help_after: bool) -> void:
	if open_help_after:
		open_help(null, card.status)
		return
	show_next()
