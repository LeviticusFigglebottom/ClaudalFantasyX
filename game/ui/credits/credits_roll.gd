class_name CreditsRoll
extends Control
## The closing credits (M5-A3P-1700; act3_ending CR): black, and the credits' sections climbing up through the centre
## column, timed by CreditsRollModel to the credits_suite cue. At a vignette (the beach rite) the roll and its black
## fade out so the in-engine vignette Cinematics plays shows, then fade back in. Holding Confirm runs it faster; once
## the credits have been seen in full, holding Cancel skips them. When they end, the credits_seen flag is set and
## `next_scene` (the post-credits scene) or the title opens. Layout and timing: game/data/ui/credits.json.

## A vignette starts (its id): the roll is faded out and holds until it has run.
signal vignette_started(id: StringName)
## The credits have ended (run out, or skipped).
signal finished

const TITLE_SCENE := EndCard.DEFAULT_RETURN_SCENE
## The credits as a scene of their own: the ending's last cutscene (act3_ending E6) changes to it.
const SCENE := "res://game/ui/credits/credits_roll.tscn"

var model: CreditsRollModel
## How an ending changes scene: Callable(path). Unset: FlowRouting.change_scene. Tests set a recorder.
var change_scene: Callable = Callable()
## Sets a flag when the credits end: Callable(flag). Unset: Game.set_flag.
var set_flag: Callable = Callable()

var _black: ColorRect
var _column: Control
var _hint: Label
var _labels: Array[Label] = []
var _height := 0.0
var _ended := false
var _vignette: Node
## Confirm and Cancel held, from the input events (keys and pad alike).
var _fast := false
var _skip := false


## Opens the credits under `host` (the scene at the end of the game); `seen` allows the skip.
static func open_in(host: Node, seen: bool = false) -> CreditsRoll:
	var roll := CreditsRoll.new()
	roll.model = CreditsRollModel.new({}, seen)
	host.add_child(roll)
	return roll


func _ready() -> void:
	if model == null:
		model = CreditsRollModel.new({}, bool(Game.get_flag(CreditsRollModel.SEEN_FLAG)))
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	UiSettings.shared().follow(self)
	_build()
	UiFrame.centre(self)
	_apply()


func _input(event: InputEvent) -> void:
	if event.is_echo():
		return
	if event.is_action(&"ui_accept"):
		_fast = event.is_pressed()
	elif event.is_action(&"ui_cancel"):
		_skip = event.is_pressed()


func _process(delta: float) -> void:
	advance(delta, _fast, _skip)


## Steps the roll by `delta` seconds (from _process; tests call it directly).
func advance(delta: float, fast: bool = false, skip: bool = false) -> void:
	if _ended:
		return
	var started := model.advance(delta, fast, skip)
	if started != &"":
		_show_vignette(model.vignette)
		vignette_started.emit(started)
	elif model.phase != CreditsRollModel.Phase.VIGNETTE and _vignette != null:
		_vignette.queue_free()
		_vignette = null
	_apply()
	if model.is_done():
		_end()


## The text of every row, top to bottom (tests and shots).
func shown_text() -> PackedStringArray:
	var out: PackedStringArray = []
	for l in _labels:
		out.append(l.text)
	return out


## The column's offset from its rest at the top of the screen (reference pixels).
func scroll_y() -> float:
	return _column.position.y


func hint_text() -> String:
	return _hint.text


func _apply() -> void:
	var view := get_viewport_rect().size.y if is_inside_tree() else 1080.0
	_column.position.y = lerpf(view, view * 0.5 - _height, model.progress)
	var a := model.alpha()
	_column.modulate.a = a
	_hint.modulate.a = a
	# The black stays through the lead-in and the end; only a vignette lets the scene behind show.
	_black.color.a = a if model.phase == CreditsRollModel.Phase.VIGNETTE else 1.0


## The vignette on show (null when none): its scene, instanced behind the roll's black.
func vignette_node() -> Node:
	return _vignette


func _show_vignette(row: Dictionary) -> void:
	var packed := load(str(row.get("scene", ""))) as PackedScene
	if packed == null:
		return
	_vignette = packed.instantiate()
	add_child(_vignette)
	move_child(_vignette, 0)  # behind the black, which fades out to show it


func _end() -> void:
	_ended = true
	if set_flag.is_valid():
		set_flag.call(CreditsRollModel.SEEN_FLAG)
	else:
		Game.set_flag(CreditsRollModel.SEEN_FLAG)
	finished.emit()
	var next := str(model.data.get("next_scene", ""))
	var to := next if next != "" else TITLE_SCENE
	if change_scene.is_valid():
		change_scene.call(to)
	elif is_inside_tree():
		FlowRouting.change_scene(to)


func _build() -> void:
	_black = ColorRect.new()
	_black.color = Color(0, 0, 0, 1)
	_black.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_black.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_black)
	var col := model.data.get("column", {}) as Dictionary
	var r := HudLayout.rect_of(col)
	_column = Control.new()
	_column.position = r.position
	_column.size = Vector2(r.size.x, 0.0)
	_column.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_column)
	var y := 0.0
	for row in model.rows():
		y += float(row["gap_before"])
		var title: bool = row["kind"] == &"title"
		var h := float(col.get("title_height" if title else "line_height", 0.0))
		var l := Label.new()
		l.theme_type_variation = &"TitleLabel" if title else &"BodyLabel"
		l.text = tr(str(row["key"]))
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.position = Vector2(0.0, y)
		l.size = Vector2(r.size.x, h)
		l.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_column.add_child(l)
		_labels.append(l)
		y += h
	_height = y
	_hint = Label.new()
	_hint.theme_type_variation = &"HelpDimLabel"
	_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	HudLayout.place(_hint, model.data.get("hint", {}) as Dictionary)
	var keys: Array[String] = ["CREDITS_ROLL_FAST"]
	if model.seen_before:
		keys.append("CREDITS_ROLL_SKIP")
	var parts: PackedStringArray = []
	for k in keys:
		parts.append(InputNames.fill(tr(k)))
	_hint.text = " · ".join(parts)
	add_child(_hint)
