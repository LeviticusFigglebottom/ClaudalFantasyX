class_name BattleActorMotion
extends RefCounted
## Body clips for the actors on the battle stage (M2-CRE-03). BattleStage.spawn attaches one per engine. It
## listens to the engine and asks the stage's FighterStandIns to play: the actor's clip for each action it takes
## (by skill), `hit` on every foe a landed damaging hit reaches, a boss's phase change, and its breakable part
## (the Drownbell's rim) breaking on `charge_broken` and mending on `charge_started`. KO and Petrify reach the
## actors through BattleStage.refresh_ko as before. Listens only: it never writes combat state.

var _stage: BattleStage
var _engine: BattleEngine


static func attach(stage: BattleStage, engine: BattleEngine, previous: BattleActorMotion = null) -> BattleActorMotion:
	if previous != null:
		previous.detach()
	var m := BattleActorMotion.new()
	m._stage = stage
	m._engine = engine
	engine.action_resolved.connect(m._on_action_resolved)
	engine.phase_changed.connect(m._on_phase_changed)
	engine.charge_started.connect(m._on_charge_started)
	engine.charge_broken.connect(m._on_charge_broken)
	return m


func detach() -> void:
	if _engine == null:
		return
	for pair: Array in [
		[_engine.action_resolved, _on_action_resolved],
		[_engine.phase_changed, _on_phase_changed],
		[_engine.charge_started, _on_charge_started],
		[_engine.charge_broken, _on_charge_broken],
	]:
		var sig := pair[0] as Signal
		if sig.is_connected(pair[1] as Callable):
			sig.disconnect(pair[1] as Callable)
	_engine = null


func _on_action_resolved(result: ActionResult) -> void:
	if not result.ok or not is_instance_valid(_stage):
		return
	var actor := _stage.stand_in(result.actor_id)
	if actor != null and result.skill_id != &"":
		var kind := StringName(str(_engine.db.skill(result.skill_id).get("kind", "")))
		actor.play_action(result.skill_id, kind)
	for h: Dictionary in result.hits:
		var tid := StringName(str(h.get("target_id", "")))
		if tid == result.actor_id or not bool(h.get("hit", false)) or int(h.get("amount", 0)) <= 0:
			continue
		var target := _stage.stand_in(tid)
		if target != null:
			target.play_hit()


func _on_phase_changed(enemy: BattleCombatant, phase_id: StringName) -> void:
	var f := _fighter(enemy)
	if f != null:
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
