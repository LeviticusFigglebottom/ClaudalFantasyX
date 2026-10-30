class_name CutsceneHoldGate
extends Node
## A no-fail held input inside a cutscene (M3-C09-02; act1_ch09.md B04-B07, the Ebbing's three
## movements; docs/kb/tech/cutscenes.md "Held input"). Attach it to a CutsceneSequencer with setup().
## Between <<event hold_input <prompt>>> and <<event hold_input_end>> the scene's time runs only while
## the player holds `action`: the sequencer's own _process stops, and tick() feeds it advance(delta)
## only on frames the action is held, so waits, walks and fades go on while it is held and stand still
## when it is let go. There is no timer, no score and nothing to fail: letting go only pauses, nothing
## resets, and the only way out of a gate is the scene reaching hold_input_end (or ending).
## M4-CIN-1302 (act2_ch10.md B09, the farewell-tide): <<event release_input <prompt>>> opens the other kind of
## gate, the one that ends by letting go. The scene's time stands still while the action is held, and the scene goes
## on the first frame it isn't (opened straight after a hold gate, the player is holding when it opens). No timer,
## no fail: holding longer only holds the moment.
## The prompt (a loc key from the host's data) shows for the whole gate, in UI's HoldPrompt widget
## (M3-C09-05: the held action's key or pad button and the verb; holding lights the key, letting go
## lets it breathe; no meter, no count). Data, from the host:
##   {"action": input action, "prompts": {prompt id: loc key}, "layer": the prompt's canvas layer,
##    "bottom_px": the prompt's distance from the bottom of the screen (absent: hold_prompt.json's)}

## A gate opened (the prompt id from the event).
signal gate_opened(prompt: StringName)
## The gate closed (hold_input_end, or the scene ended).
signal gate_closed

const EVENT_BEGIN := &"hold_input"
const EVENT_END := &"hold_input_end"
const EVENT_RELEASE := &"release_input"
const KEY_ACTION := "action"
const KEY_PROMPTS := "prompts"
const KEY_LAYER := "layer"
const KEY_BOTTOM := "bottom_px"

var sequencer: CutsceneSequencer
## The held action (field_input.json's interact by default data).
var action: StringName = &""
## prompt id -> loc key.
var prompts: Dictionary = {}
## True while a gate is open.
var gating := false
## True while the open gate is a release gate (release_input).
var releasing := false
## The open gate's prompt id.
var prompt_id: StringName = &""
## Seconds held in the open gate (tests and the UI read it; it never resets mid-gate).
var held_sec := 0.0
## Gates opened since setup (tests read it).
var gates := 0
## The on-screen prompt (HoldPrompt, game/ui/prompts/).
var prompt: HoldPrompt

var _layer: CanvasLayer
var _seq_processed := true


## Listens to `seq` and reads `cfg` ({action, prompts}).
func setup(seq: CutsceneSequencer, cfg: Dictionary) -> void:
	sequencer = seq
	action = StringName(str(cfg.get(KEY_ACTION, "")))
	prompts = cfg.get(KEY_PROMPTS, {})
	sequencer.event_requested.connect(_on_event)
	sequencer.finished.connect(_on_finished)
	_build_prompt(int(cfg.get(KEY_LAYER, 0)), float(cfg.get(KEY_BOTTOM, -1.0)))


func _process(delta: float) -> void:
	if gating:
		tick(delta, action != &"" and InputMap.has_action(action) and Input.is_action_pressed(action))


## One frame of an open gate: the scene's time moves by `delta` only when `held`. Returns true when
## the scene's time moved.
func tick(delta: float, held: bool) -> bool:
	if gating:
		prompt.set_held(held)
	if gating and releasing:
		if not held:
			_close()
		return false
	if not gating or not held or sequencer == null:
		return false
	held_sec += delta
	sequencer.advance(delta)
	return true


func _on_event(event_name: StringName, args: Array) -> void:
	if event_name == EVENT_BEGIN:
		_open(StringName(str(args[0])) if not args.is_empty() else &"")
	elif event_name == EVENT_END:
		_close()
	elif event_name == EVENT_RELEASE:
		_open(StringName(str(args[0])) if not args.is_empty() else &"", true)


func _on_finished(_scene_id: StringName) -> void:
	_close()


func _open(id: StringName, release := false) -> void:
	if gating:
		return
	gating = true
	releasing = release
	gates += 1
	prompt_id = id
	held_sec = 0.0
	_seq_processed = sequencer.is_processing()
	sequencer.set_process(false)
	_layer.visible = true
	prompt.show_prompt(str(prompts.get(String(id), "")))
	gate_opened.emit(id)


func _close() -> void:
	if not gating:
		return
	gating = false
	releasing = false
	prompt_id = &""
	if is_instance_valid(sequencer):
		sequencer.set_process(_seq_processed)
	prompt.hide_prompt()
	gate_closed.emit()


func _build_prompt(layer: int, bottom_px: float) -> void:
	if _layer != null:
		return
	_layer = CanvasLayer.new()
	_layer.name = "HoldPrompt"
	_layer.layer = layer
	_layer.visible = false
	add_child(_layer)
	prompt = HoldPrompt.new()
	prompt.action = action
	prompt.bottom_px = bottom_px
	_layer.add_child(prompt)
