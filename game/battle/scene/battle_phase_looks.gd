class_name BattlePhaseLooks
extends Node
## Phase looks (M3-BPR-406; ADR 0100, set_piece_battles.md §8): a foe whose phase makes it untargetable (the Reach's
## Breach) shows it, so the player sees why their aim is refused (Pillar 4). Its stand-in fades to choreo.json
## `phase_looks.untargetable.alpha` (every surface, model or primitive) and comes back when the phase ends. A damage-
## immune blow's own "no effect" reaction is BattleChoreoPlan's `immune` kind. Listen-only; refreshed on each phase
## change and turn.

const KEY := "phase_looks"
const NODE_NAME := "BattlePhaseLooks"

var cfg: Dictionary = {}
## Foes shown veiled now (tests).
var veiled: Array[StringName] = []

var _ctl: BattleController
var _engine: BattleEngine


static func attached(choreo: BattleChoreo, controller: BattleController, engine: BattleEngine) -> BattlePhaseLooks:
	var p := BattlePhaseLooks.new()
	p.name = NODE_NAME
	p.cfg = choreo.data.get(KEY, {}) as Dictionary
	p._ctl = controller
	p._engine = engine
	choreo.add_child(p)
	engine.phase_changed.connect(p._on_phase_changed)
	engine.turn_started.connect(p._on_turn)
	return p


## The phase looks under `stage`'s sequencer (null when none).
static func of(stage: BattleStage) -> BattlePhaseLooks:
	if stage == null or stage.choreo == null:
		return null
	return stage.choreo.get_node_or_null(NodePath(NODE_NAME)) as BattlePhaseLooks


func _on_phase_changed(_enemy: BattleCombatant, _phase_id: StringName) -> void:
	refresh()


func _on_turn(_actor: BattleCombatant) -> void:
	refresh()


## Veils every living foe that is untargetable now, and unveils the rest.
func refresh() -> void:
	var alpha := float((cfg.get("untargetable", {}) as Dictionary).get("alpha", 1.0))
	for e in _engine.enemies:
		var f := _ctl.stage.stand_in(e.id)
		if f == null or not e.is_alive():
			continue
		var on := e.untargetable
		if on == veiled.has(e.id):
			continue
		for n in f.find_children("*", "GeometryInstance3D", true, false):
			(n as GeometryInstance3D).transparency = 1.0 - alpha if on else 0.0
		if on:
			veiled.append(e.id)
		else:
			veiled.erase(e.id)
