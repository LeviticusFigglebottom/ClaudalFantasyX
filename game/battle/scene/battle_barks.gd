class_name BattleBarks
extends Node
## Battle barks (M3-C08-100; docs/kb/tech/battle_presentation.md "Barks"): a short spoken line over a fighter's head
## when it uses a skill or calls a Vowbound, from choreo.json `barks`:
## - `skills`: {skill id: {speaker, key}}. Only the speaker's own use of the skill speaks (Toma's "Hold." on Hold the
##   Stair, Liss's "Pull!" on Haul).
## - `calls`: {vowbound id: {speaker, key}}. The caller says the name as it calls (Asha's "Virel.").
## The line pops as a float (BattleHud.pop_info, the `role` colour) at the speaker's head, and `barked` fires for the
## voice blips (audio). Sincere and sparse: most skills say nothing (Flare Line, Virel herself). Listen-only.

## A bark was shown: who said it and its loc key (audio plays the speaker's voice blips on it).
signal barked(speaker: StringName, key: String)

const KEY := "barks"
const NODE_NAME := "BattleBarks"

var cfg: Dictionary = {}
## Barks shown (tests).
var shown: Array[String] = []

var _ctl: BattleController
var _engine: BattleEngine


static func attached(choreo: BattleChoreo, controller: BattleController, engine: BattleEngine) -> BattleBarks:
	var b := BattleBarks.new()
	b.name = NODE_NAME
	b.cfg = choreo.data.get(KEY, {}) as Dictionary
	b._ctl = controller
	b._engine = engine
	choreo.add_child(b)
	engine.action_resolved.connect(b._on_action)
	engine.vowbound.called.connect(b._on_called)
	return b


## The barks under `stage`'s sequencer (null when none).
static func of(stage: BattleStage) -> BattleBarks:
	if stage == null or stage.choreo == null:
		return null
	return stage.choreo.get_node_or_null(NODE_NAME) as BattleBarks


func _on_action(result: ActionResult) -> void:
	if result == null or not result.ok:
		return
	var row := (cfg.get("skills", {}) as Dictionary).get(String(result.skill_id), {}) as Dictionary
	if not row.is_empty() and StringName(str(row.get("speaker", ""))) == result.actor_id:
		_say(result.actor_id, str(row.get("key", "")))


func _on_called(vowbound: BattleCombatant) -> void:
	var row := (cfg.get("calls", {}) as Dictionary).get(String(vowbound.id), {}) as Dictionary
	if not row.is_empty():
		_say(StringName(str(row.get("speaker", ""))), str(row.get("key", "")))


func _say(speaker: StringName, key: String) -> void:
	var c := _engine.find(speaker)
	if key == "" or c == null or not c.is_alive() or _ctl == null or _ctl.hud == null:
		return
	_ctl.hud.pop_info(tr(key), _ctl.head_pos(speaker), StringName(str(cfg.get("role", "text"))))
	shown.append(key)
	barked.emit(speaker, key)
