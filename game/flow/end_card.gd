class_name EndCard
extends Control
## The end of the first playable (M2-FP-03; docs/kb/tech/first_playable_flow.md): a black screen
## with a title, one line and a small prompt (loc keys FLOW_END_CARD_*, theme variations only).
## After first_playable.json end_card.min_hold_sec, ui_accept returns to the title (boot.tscn).
## M2-FP-26 (B12): it opens on Rhen's voice-over line alone (voice_key, held voice_sec, faded by
## voice_fade_sec), then the title and line fade in (fade_in_sec) and the short credits roll in one
## row at a time (credits: loc keys, credit_line_sec apart). The piano coda (hush_coda) is the end
## card's zone music (game/data/audio/music.json zones). Every alpha is a function of `elapsed`.
## M3-C04-04: when end_card.next_location is set (a locations.json id, with next_spawn), accept goes
## there instead (the full game's slice → Ch4); empty, it returns to the title (the M2 review build).
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
## Where accept leads when set (end_card.next_location / next_spawn; M3-C04-04): &"" = the title.
var next_location: StringName = &""
var next_spawn: StringName = &""
## True once accept has started the return (a second press does nothing).
var done := false

var _min_hold := 0.0
var _return_scene := DEFAULT_RETURN_SCENE
var _voice_sec := 0.0
var _voice_fade := 0.0
var _fade_in := 0.0
var _credit_step := 0.0
var _credit_rows: Array[Label] = []

@onready var _title: Label = %Title
@onready var _line: Label = %Line
@onready var _prompt: Label = %Prompt
@onready var _content: Control = %Content
@onready var _voice: Label = %Voice
@onready var _credits: VBoxContainer = %Credits


## Opens the end card through the router.
static func open() -> void:
	FlowRouting.change_scene(SCENE)


func _ready() -> void:
	var cfg := FirstPlayableConfig.section(FirstPlayableConfig.SECTION_END_CARD)
	_min_hold = float(cfg.get("min_hold_sec", 0.0))
	_return_scene = str(cfg.get("return_scene", DEFAULT_RETURN_SCENE))
	next_location = StringName(str(cfg.get("next_location", "")))
	next_spawn = StringName(str(cfg.get("next_spawn", "")))
	_title.text = tr("FLOW_END_CARD_TITLE")
	_line.text = tr("FLOW_END_CARD_LINE")
	_prompt.text = tr("FLOW_END_CARD_PROMPT")
	var voice_key := str(cfg.get("voice_key", ""))
	_voice.text = tr(voice_key) if voice_key != "" else ""
	_voice_sec = float(cfg.get("voice_sec", 0.0)) if voice_key != "" else 0.0
	_voice_fade = float(cfg.get("voice_fade_sec", 0.0))
	_fade_in = float(cfg.get("fade_in_sec", 0.0))
	_credit_step = float(cfg.get("credit_line_sec", 0.0))
	for key: Variant in cfg.get("credits", []):
		var row := Label.new()
		row.theme_type_variation = &"HelpLabel"
		row.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		row.text = tr(str(key))
		_credits.add_child(row)
		_credit_rows.append(row)
	_show_prompt(false)
	_pace()


func _process(delta: float) -> void:
	advance(delta)


func _unhandled_input(event: InputEvent) -> void:
	if handle_input(event):
		get_viewport().set_input_as_handled()


## Passes `delta` seconds; the prompt shows once accept is allowed (it keeps its place meanwhile).
func advance(delta: float) -> void:
	elapsed += delta
	_pace()
	_show_prompt(can_accept())


## The voice-over line alone first, then the card and the credits row by row.
func voice_alpha() -> float:
	if _voice_sec <= 0.0:
		return 0.0
	var up := _ramp(elapsed, 0.0, _voice_fade)
	var down := 1.0 - _ramp(elapsed, _voice_sec - _voice_fade, _voice_fade)
	return minf(up, down)


## How many credit rows are fully in.
func credits_shown() -> int:
	var n := 0
	for row in _credit_rows:
		if row.modulate.a >= 1.0:
			n += 1
	return n


func _pace() -> void:
	_voice.modulate.a = voice_alpha()
	_content.modulate.a = _ramp(elapsed, _voice_sec, _fade_in)
	for i in _credit_rows.size():
		_credit_rows[i].modulate.a = _ramp(elapsed, _voice_sec + _fade_in + _credit_step * i, _fade_in)


## 0 before `start`, rising to 1 over `length` seconds (a step when length is 0).
static func _ramp(t: float, start: float, length: float) -> float:
	if length <= 0.0:
		return 1.0 if t >= start else 0.0
	return clampf((t - start) / length, 0.0, 1.0)


func can_accept() -> bool:
	return not done and elapsed >= _min_hold


## ui_accept returns to the title once the hold is over. Returns true when the event was used.
func handle_input(event: InputEvent) -> bool:
	if not event.is_action_pressed(&"ui_accept") or not can_accept():
		return false
	accept()
	return true


## Returns to the title, or goes on to next_location when set (ignores the hold; handle_input enforces
## it). Returns false once done.
func accept() -> bool:
	if done:
		return false
	done = true
	if next_location != &"":
		FlowRouting.go_to(next_location, next_spawn)  # FlowRouting.record captures it in tests
		return true
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
