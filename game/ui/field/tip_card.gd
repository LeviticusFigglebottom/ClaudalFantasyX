class_name TipCard
extends Control
## The first-time tip card in the field (M2-UI-24): a small tide-notch panel at the upper right with
## a gold lamp glyph, the tip's title and its body, the bindings it names filled in (InputNames).
## TutorialTips raises tips from field events: the first frame the field takes input, an
## interactable coming in reach, a story flag. One shows at a time: it fades in, stays long enough
## to read, and fades out; the next waits. While the field refuses input or a menu pauses the tree
## the card hides and its clock stops. Layout and timing: game/data/ui/tutorial_tips.json.

enum Phase { HIDDEN, IN, HOLD, OUT }

## The player whose input state and reach drive the tips (null in tests and shots).
var controller: FieldController
var tips: TutorialTips
var phase := Phase.HIDDEN
## The tip on show ({} when none).
var current: Dictionary = {}

var _d: Dictionary = {}
var _panel: PanelContainer
var _glyph: Control
var _title: Label
var _body: Label
var _t := 0.0
var _hold := 0.0
var _readied := false
var _near: Interactable
## Whether the body on show names pad buttons (it is filled again when the device changes).
var _body_pad := false


## Adds the card (on its own CanvasLayer) under field controller `c`, and returns it.
static func attach(c: FieldController) -> TipCard:
	var layer := CanvasLayer.new()
	layer.name = &"TipLayer"
	layer.layer = int(TutorialTips.load_data().get("canvas_layer", 1))
	var card := TipCard.new()
	card.controller = c
	layer.add_child(card)
	c.add_child(layer)
	return card


func _ready() -> void:
	name = &"TipCard"
	process_mode = Node.PROCESS_MODE_ALWAYS  # so it can hide itself while a menu pauses the tree
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	UiSettings.shared().follow(self)
	if tips == null:
		tips = TutorialTips.new()
	_d = tips.data
	_build()
	EventBus.flag_changed.connect(_on_flag_changed)
	_apply(0.0)


func _input(event: InputEvent) -> void:
	InputNames.note(event, _num("pad_deadzone"))
	if phase == Phase.IN or phase == Phase.HOLD:
		for action in TutorialTips.actions_named(current):
			if InputMap.has_action(action) and event.is_action_pressed(action):
				dismiss()
				return


## Fades the tip on show out now (the player pressed what it teaches, the Lead's first-hour pass, 2026-10-30: the
## menu tip no longer waits out a visit to the menu and then asks again for what was just done).
func dismiss() -> void:
	if phase != Phase.IN and phase != Phase.HOLD:
		return
	var v := _visibility()
	phase = Phase.OUT
	_t = (1.0 - v) * _num("fade_sec")  # from where the fade is, without a jump


func _process(delta: float) -> void:
	advance(delta)


## True while the card may be seen: the field takes input and no menu pauses the tree.
func allowed() -> bool:
	if controller != null and (not is_instance_valid(controller) or not controller.accepts_input):
		return false
	return not (is_inside_tree() and get_tree().paused)


## Steps the card by `delta` seconds (from _process; tests call it directly).
func advance(delta: float) -> void:
	if not allowed():
		_apply(0.0)
		return
	if not _readied:
		_readied = true
		tips.raise_field_ready()
	if controller != null:
		var it := controller.nearest_interactable()
		if it != _near:
			_near = it
			tips.raise_near(TutorialTips.tags_of(it))
	if phase == Phase.HIDDEN:
		_show_next()
		if phase == Phase.HIDDEN:
			_apply(0.0)
			return
	else:
		_t += delta
	if InputNames.using_pad != _body_pad:
		_fill_body()  # the names follow the last device used (M2-UI-26); the hold stays as it was
	match phase:
		Phase.IN:
			if _t >= _num("fade_sec"):
				phase = Phase.HOLD
				_t = 0.0
		Phase.HOLD:
			if _t >= _hold:
				phase = Phase.OUT
				_t = 0.0
		Phase.OUT:
			if _t >= _num("fade_sec"):
				phase = Phase.HIDDEN
				current = {}
				_t = 0.0
	_apply(_visibility())


func is_showing() -> bool:
	return phase != Phase.HIDDEN


func title_text() -> String:
	return _title.text


func body_text() -> String:
	return _body.text


## How long tip `tip` holds: hold_sec plus sec_per_char for each body character.
func hold_for(body: String) -> float:
	return _num("hold_sec") + _num("sec_per_char") * body.length()


func _show_next() -> void:
	current = tips.take()
	if current.is_empty():
		return
	_title.text = tr(str(current.get("title_key", "")))
	_fill_body()
	_hold = hold_for(_body.text)
	phase = Phase.IN
	_t = 0.0


func _fill_body() -> void:
	_body_pad = InputNames.using_pad
	_body.text = InputNames.fill(tr(str(current.get("body_key", ""))), _body_pad)


func _on_flag_changed(flag: StringName, value: Variant) -> void:
	tips.raise_flag(flag, value)


func _visibility() -> float:
	var fade := maxf(_num("fade_sec"), 0.001)
	match phase:
		Phase.IN:
			return clampf(_t / fade, 0.0, 1.0)
		Phase.HOLD:
			return 1.0
		Phase.OUT:
			return 1.0 - clampf(_t / fade, 0.0, 1.0)
	return 0.0


func _apply(v: float) -> void:
	if _panel == null:
		return
	_panel.visible = v > 0.0
	_panel.modulate.a = v


func _build() -> void:
	var pm: Dictionary = _d.get("panel", {})
	var r := HudLayout.rect_of(pm)
	_panel = PanelContainer.new()
	_panel.theme_type_variation = &"PanelSmall"
	HudLayout.place(_panel, pm)  # top right at any aspect (M2-UI-29)
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_panel)
	var box := VBoxContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.add_child(box)
	var head := HBoxContainer.new()
	head.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(head)
	_glyph = Control.new()
	var g := HudLayout.num(pm, "glyph_px")
	_glyph.custom_minimum_size = Vector2(g * 2.0, HudLayout.num(pm, "title_height"))
	_glyph.draw.connect(_draw_glyph)
	head.add_child(_glyph)
	_title = Label.new()
	_title.theme_type_variation = &"HeaderLabel"
	head.add_child(_title)
	_body = Label.new()
	_body.theme_type_variation = &"HelpLabel"
	_body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART  # no overrun trim: the panel grows
	_body.custom_minimum_size.x = r.size.x - HudLayout.num(pm, "pad") * 2.0
	box.add_child(_body)


## A lamp: a gold ring with a lit core (a tip, not an objective: the objective is the diamond).
func _draw_glyph() -> void:
	var g := HudLayout.num(_d.get("panel", {}), "glyph_px")
	var c := Vector2(g, _glyph.size.y * 0.5)
	_glyph.draw_arc(c, g * 0.7, 0.0, TAU, 24, get_theme_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE), 2.0, true)
	_glyph.draw_circle(c, g * 0.3, get_theme_color(&"focus", HymnThemeBuilder.PALETTE_TYPE))


func _num(key: String) -> float:
	return HudLayout.num(_d, key)
