class_name BattleBarks
extends Node
## Battle barks (M3-C08-100; act1_ch08.md §5): a hero's word as a skill lands, or as a Vowbound is
## called. A short line floats over the speaker, whatever the damage-number setting is, because it
## is speech, not a number.
##   skills.json "bark_key"         spoken by the user when the skill resolves (Toma's "Hold." on
##                                  Hold the Stair, Liss's "Pull!" on Haul);
##   vowbound.json "call_bark_key"  spoken by the caller as the Vowbound is called (Asha: "Virel.").
## A skill or Vowbound without one stays silent (Flare Line; Virel has no line). A view: it listens to
## the engine and never writes combat state. The controller only attaches it (one line); it lives as a
## node under the HUD, so a retry's new attach replaces it.

const NODE_NAME := &"BattleBarks"

var ctl: BattleController
## Every line said this battle, oldest first: {"speaker": id, "text": String} (tests and captures).
var said: Array[Dictionary] = []
var _engine: BattleEngine


## A view of `engine` for `controller`, already attached under its HUD (replacing an earlier one). Call
## after setup().
static func attached(controller: BattleController, engine: BattleEngine) -> BattleBarks:
	var old := controller.hud.get_node_or_null(NodePath(NODE_NAME))
	if old != null:
		controller.hud.remove_child(old)
		old.queue_free()
	var view := BattleBarks.new()
	view.name = NODE_NAME
	view.ctl = controller
	controller.hud.add_child(view)
	view.attach(engine)
	return view


func attach(engine: BattleEngine) -> void:
	_engine = engine
	engine.action_resolved.connect(_on_action_resolved)
	engine.vowbound.called.connect(_on_called)


## The bark a skill's user says, translated ("" when it has none).
func skill_bark(skill_id: StringName) -> String:
	return _text(str(_engine.db.skill(skill_id).get("bark_key", ""))) if _engine.db.skills.has(skill_id) else ""


## The bark a Vowbound's caller says as it comes ("" when it has none).
func call_bark(vowbound_id: StringName) -> String:
	return _text(str(_vowbound_row(vowbound_id).get("call_bark_key", "")))


func _on_action_resolved(result: ActionResult) -> void:
	if result.ok:
		_say(result.actor_id, skill_bark(result.skill_id))


func _on_called(vowbound: BattleCombatant) -> void:
	var caller := StringName(str(_vowbound_row(vowbound.id).get("caller", "")))
	var speaker := caller if ctl.stage.has_fighter(caller) else vowbound.id
	_say(speaker, call_bark(vowbound.id))


func _say(speaker: StringName, text: String) -> void:
	if text == "":
		return
	said.append({"speaker": speaker, "text": text})
	if ctl.stage.has_fighter(speaker):
		ctl.hud.pop_info(text, ctl.head_pos(speaker, &"damage"), &"text")


func _vowbound_row(vowbound_id: StringName) -> Dictionary:
	return _engine.vowbound.rows.get(vowbound_id, {}) as Dictionary


static func _text(key: String) -> String:
	return str(TranslationServer.translate(key)) if key != "" else ""
