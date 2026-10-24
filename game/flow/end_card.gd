class_name EndCard
extends Control
## The end of the first playable (M2-FP-03; docs/kb/tech/first_playable_flow.md): a black screen
## with a title, one line and a small prompt (loc keys FLOW_END_CARD_*, theme variations only).
## After first_playable.json end_card.min_hold_sec, ui_accept returns to the title (boot.tscn).
## Show it with EndCard.open() (or FlowRouting.change_scene(EndCard.SCENE)).

## Emitted once, when accept starts the return to the title.
signal returning(scene_path: String)

const SCENE := "res://game/flow/end_card.tscn"
const DEFAULT_RETURN_SCENE := "res://game/core/boot.tscn"

## How accept changes scene: (scene_path: String). Unset = SceneRouter.change_scene. Tests set a
## recorder.
var change_scene: Callable = Callable()
## Seconds the card has been up (advance() adds to it; _process drives it in the game).
var elapsed := 0.0
## True once accept has started the return (a second press does nothing).
var done := false

var _min_hold := 0.0
var _return_scene := DEFAULT_RETURN_SCENE

@onready var _title: Label = %Title
@onready var _line: Label = %Line
@onready var _prompt: Label = %Prompt
@onready var _content: Control = %Content


## Opens the end card through the router.
static func open() -> void:
	FlowRouting.change_scene(SCENE)


func _ready() -> void:
	var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_END_CARD)
	_min_hold = float(cfg.get("min_hold_sec", 0.0))
	_return_scene = str(cfg.get("return_scene", DEFAULT_RETURN_SCENE))
	_title.text = tr("FLOW_END_CARD_TITLE")
	_line.text = tr("FLOW_END_CARD_LINE")
	_prompt.text = tr("FLOW_END_CARD_PROMPT")
	_show_prompt(false)
	var fade := float(cfg.get("fade_in_sec", 0.0))
	if fade > 0.0:
		_content.modulate.a = 0.0
		create_tween().tween_property(_content, "modulate:a", 1.0, fade)


func _process(delta: float) -> void:
	advance(delta)


func _unhandled_input(event: InputEvent) -> void:
	if handle_input(event):
		get_viewport().set_input_as_handled()


## Passes `delta` seconds; the prompt shows once accept is allowed (it keeps its place meanwhile).
func advance(delta: float) -> void:
	elapsed += delta
	_show_prompt(can_accept())


func can_accept() -> bool:
	return not done and elapsed >= _min_hold


## ui_accept returns to the title once the hold is over. Returns true when the event was used.
func handle_input(event: InputEvent) -> bool:
	if not event.is_action_pressed(&"ui_accept") or not can_accept():
		return false
	accept()
	return true


## Returns to the title (ignores the hold; handle_input enforces it). Returns false once done.
func accept() -> bool:
	if done:
		return false
	done = true
	returning.emit(_return_scene)
	if change_scene.is_valid():
		change_scene.call(_return_scene)
	elif is_inside_tree():
		FlowRouting.change_scene(_return_scene)  # waits for an idle router: `done` never strands it
	return true


func prompt_shown() -> bool:
	return _prompt.modulate.a > 0.0


func _show_prompt(on: bool) -> void:
	_prompt.modulate.a = 1.0 if on else 0.0
