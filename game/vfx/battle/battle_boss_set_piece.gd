class_name BattleBossSetPiece
extends Node
## M3-BPR-420 / M3-HER-1148 (ADR 0041): an Act I boss's set-piece VFX (boss_vfx.json `bosses`, kind "set_piece"):
## `gather` plays on the boss as it starts gathering a charge and on each later turn of it, `phases` plays a phase's
## moment when it changes, and `ko` plays once when the boss falls. Every value is an effects.json id that BattleVfx
## plays. The Drownbell's rig is BattleBossVfx. A view: it never writes combat state.

const KIND := "set_piece"

## The boss this plays for, and the moments played (tests): [[moment, effect id], ...].
var boss_id: StringName = &""
var played: Array = []

var _vfx: BattleVfx
var _engine: BattleEngine
var _row: Dictionary = {}
var _fell := false


## One set piece per set-piece boss in the fight (none when no foe has a row).
static func attach_all(vfx: BattleVfx, controller: BattleController, engine: BattleEngine) -> Array[BattleBossSetPiece]:
	var out: Array[BattleBossSetPiece] = []
	var rows := BattleBossVfx.load_data().get("bosses", {}) as Dictionary
	for c in engine.enemies:
		var row := rows.get(BattleVfx.base_id(c.id), {}) as Dictionary
		if str(row.get("kind", "")) != KIND:
			continue
		var sp := BattleBossSetPiece.new()
		sp.name = "SetPiece_%s" % String(c.id).replace("#", "_")
		sp.boss_id = c.id
		sp._vfx = vfx
		sp._engine = engine
		sp._row = row
		vfx.add_child(sp)
		engine.charge_started.connect(sp._on_charge_started)
		engine.turn_started.connect(sp._on_turn_started)
		engine.phase_changed.connect(sp._on_phase_changed)
		var choreo := controller.stage.choreo if controller != null else null
		if choreo != null:
			choreo.contact.connect(sp._on_action)
		else:
			engine.action_resolved.connect(sp._on_action)
		out.append(sp)
	return out


func _play(moment: String, effect: String) -> void:
	if effect == "":
		return
	_vfx.play(StringName(effect), boss_id)
	played.append([moment, effect])


func _on_charge_started(actor: BattleCombatant, _skill_id: StringName, _turns: int) -> void:
	if actor.id == boss_id:
		_play("gather", str(_row.get("gather", "")))


func _on_turn_started(actor: BattleCombatant) -> void:
	if actor.id == boss_id and actor.is_charging() and actor.charge_left > 1:
		_play("gather", str(_row.get("gather", "")))


func _on_phase_changed(enemy: BattleCombatant, phase_id: StringName) -> void:
	if enemy.id == boss_id:
		_play("phase", str((_row.get("phases", {}) as Dictionary).get(String(phase_id), "")))


func _on_action(_result: ActionResult) -> void:
	var b := _engine.find(boss_id)
	if not _fell and b != null and b.hp <= 0:
		_fell = true
		_play("ko", str(_row.get("ko", "")))
