class_name ReefballHudController
extends Node
## Wires a ReefballMatch to a ReefballHud (M3-UI-01). The engine owns every rule and every roll;
## this node only listens to its signals, shows them on the HUD, and decides who acts:
##   - the player's contact: the HUD opens the choices; its action_chosen is performed here;
##   - the other side's contact: after a short think (pacing.ai_think_sec), play_ai_contact();
##   - a float brought up: the banner holds (pacing.goal_hold_sec) before the next contact opens;
##   - the end: the final banner stays, and match_over carries the outcome to the flow layer.
## `player_ai` lets the AI play the player's side too (capture drivers and tests). `pacing_scale`
## scales every wait (0: the next step runs on the next advance()). Waits run in _process, or only
## in advance() / flush() when `manual` (tests and capture drivers, which hold a picture still).

signal match_over(outcome: StringName, score: Array)

var match_state: ReefballMatch
var hud: ReefballHud
## Plays the player's side when set (null: the player chooses on the HUD).
var player_ai: ReefballAI
var pacing_scale := 1.0
## True: waits run only in advance() / flush(), never in _process (tests and capture drivers).
var manual := false

var _pacing: Dictionary = {}
var _next := Callable()
var _wait := 0.0
var _scored := false


## Starts `m` on `h`: binds the HUD, listens to the match, and kicks off.
func start(m: ReefballMatch, h: ReefballHud) -> void:
	match_state = m
	hud = h
	_pacing = ReefballHud.load_data().get("pacing", {}) as Dictionary
	m.contact_started.connect(_on_contact_started)
	m.action_resolved.connect(_on_action_resolved)
	m.divers_moved.connect(_on_divers_moved)
	m.float_scored.connect(_on_float_scored)
	m.match_finished.connect(_on_match_finished)
	h.action_chosen.connect(_on_action_chosen)
	h.bind(m)
	m.begin()


func _process(delta: float) -> void:
	if not manual:
		advance(delta)


## Counts `delta` seconds off the pending step and runs it when its wait is over.
func advance(delta: float) -> void:
	if not _next.is_valid():
		return
	_wait -= delta
	if _wait <= 0.0:
		flush()


## Runs the pending step now, whatever is left of its wait. False when nothing was pending.
func flush() -> bool:
	if not _next.is_valid():
		return false
	var step := _next
	_next = Callable()
	step.call()
	return true


## True while a step waits (the AI thinking, a goal banner holding).
func is_waiting() -> bool:
	return _next.is_valid()


func _queue(step: Callable, sec: float) -> void:
	_next = step
	_wait = sec * pacing_scale


func _on_contact_started(_holder_id: StringName, _side: int) -> void:
	hud.hide_choices()
	var player := match_state.is_player_contact() and player_ai == null
	var wait := 0.0
	if _scored:
		wait = HudLayout.num(_pacing, "goal_hold_sec")
	elif not player:
		wait = HudLayout.num(_pacing, "ai_think_sec")
	_scored = false
	_queue(_open_contact, wait)


func _open_contact() -> void:
	if match_state.finished:
		return
	hud.hide_banner()
	if match_state.is_player_contact():
		if player_ai == null:
			hud.show_choices(match_state.legal_actions())
		else:
			match_state.play_ai_contact(player_ai)
	else:
		match_state.play_ai_contact()


func _on_action_chosen(action: StringName, target: StringName) -> void:
	if not match_state.is_player_contact() or player_ai != null or is_waiting():
		return
	hud.hide_choices()
	match_state.perform(action, target)


func _on_action_resolved(result: Dictionary) -> void:
	hud.show_result(result)


func _on_divers_moved(_moves: Array) -> void:
	hud.refresh()


func _on_float_scored(side: int, score: Array) -> void:
	_scored = true
	hud.show_goal(side, score)


func _on_match_finished(outcome: StringName, score: Array) -> void:
	_next = Callable()
	hud.hide_choices()
	hud.show_final(outcome, score)
	match_over.emit(outcome, score)
