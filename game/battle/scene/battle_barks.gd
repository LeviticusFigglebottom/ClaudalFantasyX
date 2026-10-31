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
## node under the HUD, so a retry's new attach replaces it. `barked` fires for audio's voice blips.
## M5-A3P-1708 (act3_ch17 B09): the called Vowbound may answer, after its caller, from
## game/data/ui/vowbound_answers.json (the first row for it whose when_flag is set). Kesh's answer changes once Asha
## has chosen the Unbinding.

## A bark was said: who said it and its loc key.
signal barked(speaker: StringName, key: String)

const NODE_NAME := &"BattleBarks"
const ANSWERS_PATH := "res://game/data/ui/vowbound_answers.json"

var ctl: BattleController
## Every line said this battle, oldest first: {"speaker": id, "text": String} (tests and captures).
var said: Array[Dictionary] = []
## Reads a story flag for the answers: Callable(flag: StringName) -> bool. Unset: the save's flags in a live battle
## (persist_progress), none in a capture or test, so a baseline never moves with a save.
var read_flag: Callable = Callable()
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
	return _text(_skill_key(skill_id))


## The bark a Vowbound's caller says as it comes ("" when it has none).
func call_bark(vowbound_id: StringName) -> String:
	return _text(_call_key(vowbound_id))


func _on_action_resolved(result: ActionResult) -> void:
	if result.ok:
		_say(result.actor_id, _skill_key(result.skill_id))


func _on_called(vowbound: BattleCombatant) -> void:
	var caller := StringName(str(_vowbound_row(vowbound.id).get("caller", "")))
	var speaker := caller if ctl.stage.has_fighter(caller) else vowbound.id
	_say(speaker, _call_key(vowbound.id))
	_say(vowbound.id, answer_key(vowbound.id))


## The loc key of what Vowbound `vowbound_id` says back as it is called ("" when nothing).
func answer_key(vowbound_id: StringName) -> String:
	for r: Variant in answer_rows():
		var row := r as Dictionary
		if StringName(str(row.get("vowbound", ""))) != vowbound_id:
			continue
		var flag := StringName(str(row.get("when_flag", "")))
		if flag == &"" or _flag(flag):
			return str(row.get("key", ""))
	return ""


static func answer_rows() -> Array:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(ANSWERS_PATH))
	var sec: Variant = (parsed as Dictionary).get("vowbound_answers") if parsed is Dictionary else null
	return (sec as Dictionary).get("rows", []) as Array if sec is Dictionary else []


func _flag(flag: StringName) -> bool:
	if read_flag.is_valid():
		return bool(read_flag.call(flag))
	return ctl != null and ctl.persist_progress and Game.get_flag(flag) == true


func _say(speaker: StringName, key: String) -> void:
	var text := _text(key)
	if text == "":
		return
	said.append({"speaker": speaker, "text": text})
	if ctl.stage.has_fighter(speaker):
		ctl.hud.pop_info(text, ctl.head_pos(speaker, &"damage"), &"text")
	barked.emit(speaker, key)


func _skill_key(skill_id: StringName) -> String:
	return str(_engine.db.skill(skill_id).get("bark_key", "")) if _engine.db.skills.has(skill_id) else ""


func _call_key(vowbound_id: StringName) -> String:
	return str(_vowbound_row(vowbound_id).get("call_bark_key", ""))


func _vowbound_row(vowbound_id: StringName) -> Dictionary:
	return _engine.vowbound.rows.get(vowbound_id, {}) as Dictionary


static func _text(key: String) -> String:
	return str(TranslationServer.translate(key)) if key != "" else ""
