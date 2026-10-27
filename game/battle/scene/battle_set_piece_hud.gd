class_name BattleSetPieceHud
extends RefCounted
## What a set piece's battle shows beyond a normal fight (M3-UI-100; M3-CMB-01, ADR 0100,
## docs/kb/design/set_piece_battles.md). A view: it reads the engine and never writes combat state.
## - Its scripted timeline entries (the Climb, the Surge, the Kirru) get timeline chips of their own, drawn apart
##   from fighters (TurnTimeline.set_entry_identity), from the start and as they join at a phase.
## - The objective's count against its quota on an ObjectiveMeter, titled with the ward entry's name (or the
##   objective's `label_key`), shown once the objective runs (a `from_phase` objective waits for its phase).
## - At an objective's end the foes still standing withdraw: each says so with a float.
## Party locks and the unavailable heroes are BattleMenus' (swap_lock_text, reserve_rows); the intercept,
## counter and Storm-Call floats are BattleFloats'.

var ctl: BattleController
var meter: ObjectiveMeter
var _engine: BattleEngine


func _init(controller: BattleController) -> void:
	ctl = controller


static func attached(controller: BattleController, engine: BattleEngine) -> BattleSetPieceHud:
	var view := BattleSetPieceHud.new(controller)
	view.attach(engine)
	return view


## Connects to `engine` (after setup). An encounter with no entries and no objective adds nothing.
func attach(engine: BattleEngine) -> void:
	_engine = engine
	if engine.entries.is_empty() and engine.objective.is_empty() and engine.pending_entries.is_empty():
		return
	for c in engine.entries:
		_name_entry(c)
	engine.combatants_joined.connect(_on_joined)
	if not engine.objective.is_empty():
		meter = ObjectiveMeter.new()
		meter.name = &"ObjectiveMeter"
		ctl.hud.add_child(meter)
		engine.action_resolved.connect(func(_r: ActionResult) -> void: refresh())
		engine.turn_started.connect(func(_c: BattleCombatant) -> void: refresh())
		engine.phase_changed.connect(func(_e: BattleCombatant, _p: StringName) -> void: refresh())
		refresh()
	engine.battle_finished.connect(_on_finished)


## Puts the meter in step with the engine's objective count.
func refresh() -> void:
	if meter == null:
		return
	var running := BattleSetPiece.objective_running(_engine)
	meter.show_progress(objective_title(), _engine.objective_count, BattleSetPiece.objective_quota(_engine))
	meter.visible = running and meter.quota > 0


## The meter's words: the objective's label_key, else the ward entry's name.
func objective_title() -> String:
	var key := str(_engine.objective.get("label_key", ""))
	if key != "":
		return tr(key)
	var ward := _engine.ward()
	return ctl.menus.display_name(ward) if ward != null else tr("HUD_OBJECTIVE_DEFAULT")


func _name_entry(c: BattleCombatant) -> void:
	var tint := Color.html(str(BattleStage.stand_in_spec(c.id).get("tint", "#A9B8CC")))
	ctl.hud.timeline.set_entry_identity(c.id, ctl.menus.display_name(c), tint)


func _on_joined(added: Array[BattleCombatant]) -> void:
	for c in added:
		if c.is_entry():
			_name_entry(c)  # after BattleBossHud named it as a foe
	refresh()


func _on_finished(_outcome: StringName) -> void:
	refresh()
	if not ctl.show_damage_numbers:
		return
	for c in _engine.enemies:
		if c.withdrawn and c.is_alive():
			ctl.hud.pop_info(tr("HUD_FLOAT_WITHDRAWN"), ctl.head_pos(c.id, &"damage"), &"text_dim")
