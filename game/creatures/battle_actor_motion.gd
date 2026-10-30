class_name BattleActorMotion
extends RefCounted
## Body clips for the actors on the battle stage (M2-CRE-03). BattleStage.spawn attaches one per engine. It
## listens to the engine and asks the stage's FighterStandIns to play a boss's phase change and its breakable part
## (the Drownbell's rim) breaking on `charge_broken` and mending on `charge_started`. The action and hit clips are
## BattleChoreo's (M2-BPR-01, through BattleClips: the actor's clip at its strike beat, the target's react at
## contact); they left this class at the big7 merge, as battle-presentation and creatures agreed. KO and Petrify
## reach the actors through BattleStage.refresh_ko as before. Listens only: it never writes combat state. A phase
## change waits for the action that turned it to finish playing.

var _stage: BattleStage
var _engine: BattleEngine


static func attach(stage: BattleStage, engine: BattleEngine, previous: BattleActorMotion = null) -> BattleActorMotion:
	if previous != null:
		previous.detach()
	var m := BattleActorMotion.new()
	m._stage = stage
	m._engine = engine
	engine.phase_changed.connect(m._on_phase_changed)
	engine.charge_started.connect(m._on_charge_started)
	engine.charge_broken.connect(m._on_charge_broken)
	return m


func detach() -> void:
	if _engine == null:
		return
	for pair: Array in [
		[_engine.phase_changed, _on_phase_changed],
		[_engine.charge_started, _on_charge_started],
		[_engine.charge_broken, _on_charge_broken],
	]:
		var sig := pair[0] as Signal
		if sig.is_connected(pair[1] as Callable):
			sig.disconnect(pair[1] as Callable)
	_engine = null


## The engine ends the turn that crossed the phase after the action resolved: the phase change waits for that action's
## sequence (the blow's hit reaction had cut the phase clip), so it plays under the camera's phase hold (M3-BPR-426).
func _on_phase_changed(enemy: BattleCombatant, phase_id: StringName) -> void:
	var f := _fighter(enemy)
	if f == null:
		return
	if _stage.choreo != null:
		_stage.choreo.after_sequence(func() -> void: _enter_phase(enemy, phase_id))
	else:
		f.enter_phase(phase_id)


func _enter_phase(enemy: BattleCombatant, phase_id: StringName) -> void:
	var f := _fighter(enemy)
	if f != null and enemy.is_alive():
		f.enter_phase(phase_id)


func _on_charge_started(actor: BattleCombatant, skill_id: StringName, _turns: int) -> void:
	var f := _fighter(actor)
	if f != null:
		f.set_part_broken(skill_id, false)


func _on_charge_broken(enemy: BattleCombatant, skill_id: StringName) -> void:
	var f := _fighter(enemy)
	if f != null:
		f.set_part_broken(skill_id, true)


func _fighter(c: BattleCombatant) -> FighterStandIn:
	if c == null or not is_instance_valid(_stage):
		return null
	return _stage.stand_in(c.id)
