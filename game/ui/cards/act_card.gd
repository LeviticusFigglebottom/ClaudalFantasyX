class_name ActCard
extends Control
## The title card on black (M3-C09-05; act1_ch09.md §9 UI 2, B11's "Act II: The Truth"). The screen
## goes black for as long as the card is up. The words fade in, hold, and fade out, and the black
## stays until hide_card() or the card is freed, so the next scene fades in from it. Two shapes:
##   show_act(2)                     the act's numeral line over a gold rule and its name
##   show_caption("DLG_CH01_DROP_001")  one line alone (the Prologue's "One month earlier." shape)
## A cutscene shows it from its `act_card` event (listen(seq); the event is Systems' M3-C09-09), or
## a host calls open_in(parent) and show_act() directly. Every word is a loc key; layout, timing and
## the act table are game/data/ui/act_card.json.

## The words have faded out (the black stays).
signal finished

enum Phase { IDLE, IN, HOLD, OUT, DONE }

const DATA_PATH := "res://game/data/ui/act_card.json"
## The sequencer event that shows an act card: <<event act_card <int act>>> (M3-C09-09).
const EVENT := &"act_card"

var phase := Phase.IDLE
## The act shown (0 for a caption or none).
var act := 0

var _d: Dictionary = {}
var _back: ColorRect
var _words: Control
var _label: Label
var _rule: OrnamentRule
var _title: Label
var _t := 0.0


## Adds a card on its own CanvasLayer (act_card.json canvas_layer) under `parent`, and returns it.
static func open_in(parent: Node) -> ActCard:
	var layer := CanvasLayer.new()
	layer.name = &"ActCardLayer"
	layer.layer = int(load_data().get("canvas_layer", 1))
	var card := ActCard.new()
	layer.add_child(card)
	parent.add_child(layer)
	return card


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("act_card")) != TYPE_DICTIONARY:
		push_error("ActCard: could not read 'act_card' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["act_card"] as Dictionary


## The {label_key, title_key} row for act `n` ({} when the table has none).
static func act_row(n: int) -> Dictionary:
	return (load_data().get("acts", {}) as Dictionary).get(str(n), {}) as Dictionary


func _init() -> void:
	_d = load_data()
	_build()


func _ready() -> void:
	name = &"ActCard"
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	UiSettings.shared().follow(self)
	_apply()


func _process(delta: float) -> void:
	advance(delta)


## Shows act `n`'s card: its numeral line, the rule and its name. False (and nothing shown) when
## act_card.json has no row for `n`.
func show_act(n: int) -> bool:
	var row := act_row(n)
	if row.is_empty():
		push_warning("ActCard: no act %d in %s" % [n, DATA_PATH])
		return false
	show_titled(str(row.get("label_key", "")), str(row.get("title_key", "")))
	act = n
	return true


## The act card's two-line shape for any numeral line and name (two loc keys): a chapter title card (M3-CIN-1233,
## game/flow/chapter_card.gd: "Chapter 4" over the rule, "The Pilgrim's Wake").
func show_titled(label_key: String, title_key: String) -> void:
	act = 0
	_label.text = tr(label_key)
	_title.text = tr(title_key)
	HudLayout.place(_title, _d.get("title", {}))
	_label.visible = true
	_rule.visible = true
	_start()


## Shows one line alone on black (a loc key), such as a "one month earlier" title.
func show_caption(key: String) -> void:
	act = 0
	_label.text = ""
	_title.text = tr(key)
	HudLayout.place(_title, _d.get("caption", {}))
	_label.visible = false
	_rule.visible = false
	_start()


## Takes the card and its black away at once.
func hide_card() -> void:
	phase = Phase.IDLE
	_apply()


## Listens to `seq` for the act_card event (<<event act_card 2>>) and shows that act.
func listen(seq: CutsceneSequencer) -> void:
	if not seq.event_requested.is_connected(_on_event):
		seq.event_requested.connect(_on_event)


## Steps the card by `delta` seconds (from _process; tests call it directly).
func advance(delta: float) -> void:
	if phase == Phase.IDLE or phase == Phase.DONE:
		return
	_t += delta
	match phase:
		Phase.IN:
			if _t >= _num("in_sec"):
				phase = Phase.HOLD
				_t = 0.0
		Phase.HOLD:
			if _t >= _num("hold_sec"):
				phase = Phase.OUT
				_t = 0.0
		Phase.OUT:
			if _t >= _num("out_sec"):
				phase = Phase.DONE
				finished.emit()
	_apply()


## True while the words are on screen (fading in, held, or fading out).
func is_showing() -> bool:
	return phase == Phase.IN or phase == Phase.HOLD or phase == Phase.OUT


## True while the screen is held black (from show until hide_card, including after the words go).
func is_black() -> bool:
	return phase != Phase.IDLE


## 0..1: how far the words are in.
func words_alpha() -> float:
	match phase:
		Phase.IN:
			return clampf(_t / maxf(_num("in_sec"), 0.001), 0.0, 1.0)
		Phase.HOLD:
			return 1.0
		Phase.OUT:
			return 1.0 - clampf(_t / maxf(_num("out_sec"), 0.001), 0.0, 1.0)
	return 0.0


func label_text() -> String:
	return _label.text


func title_text() -> String:
	return _title.text


## The black backing (the layout audit checks it covers the screen).
func backing() -> Control:
	return _back


## The name line (the layout audit checks it stays centred).
func title_label() -> Control:
	return _title


func _on_event(event_name: StringName, args: Array) -> void:
	if event_name == EVENT and not args.is_empty():
		show_act(int(args[0]))


func _start() -> void:
	phase = Phase.IN
	_t = 0.0
	_apply()


func _apply() -> void:
	var a := words_alpha()
	visible = phase != Phase.IDLE
	_words.modulate.a = a
	_words.visible = a > 0.0
	var rise := 0.0
	if phase == Phase.IN and is_inside_tree() and not UiSettings.shared().reduced_motion():
		rise = _num("drift_px") * (1.0 - a)
	_words.position.y = rise


func _build() -> void:
	_back = ColorRect.new()
	_back.name = &"Black"
	_back.color = Color(str(_d.get("back_color", "#000000")))
	_back.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_back.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_back)
	_words = Control.new()
	_words.name = &"Words"
	_words.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_words.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_words)
	_label = _line(&"Label", &"BannerLabel", _d.get("label", {}))
	_rule = OrnamentRule.new()
	_rule.name = &"Rule"
	_rule.centered = true
	HudLayout.place(_rule, _d.get("rule", {}))
	_words.add_child(_rule)
	_title = _line(&"Title", &"TitleLabel", _d.get("title", {}))


func _line(node_name: StringName, variation: StringName, sec: Dictionary) -> Label:
	var l := Label.new()
	l.name = node_name
	l.theme_type_variation = variation
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	HudLayout.place(l, sec)
	_words.add_child(l)
	return l


func _num(key: String) -> float:
	return HudLayout.num(_d, key)
