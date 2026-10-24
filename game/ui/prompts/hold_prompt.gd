class_name HoldPrompt
extends Control
## The held-input prompt (M3-C09-05; act1_ch09.md §9 UI 1, the Ebbing's "Hold to raise the staff";
## the same widget serves act3_ending E4). One small plate at the bottom centre: a keycap with the
## held action's binding for the device used last (InputNames: its first key, or its first pad
## button) and the verb. It has no meter, no count and no fail state. Holding lights the keycap;
## letting go lets the plate breathe slowly (reduced motion: it stays steady) while the scene waits.
## CutsceneHoldGate instances it; anything else that needs a no-fail held input can too:
##   var p := HoldPrompt.new(); p.action = &"field_interact"; add_child(p)
##   p.show_prompt("FIELD_PROMPT_CH09_RAISE_STAFF")   # then p.set_held(held) each frame
##   p.hide_prompt()
## Layout: game/data/ui/hold_prompt.json.

const DATA_PATH := "res://game/data/ui/hold_prompt.json"

## The held input action whose binding the keycap names.
var action: StringName = &""
## The plate's distance from the bottom of the screen (reference pixels); < 0 uses the data's.
var bottom_px := -1.0
## True while the action is held (set_held).
var held := false
## True once the pad was the last device used (the keycap names a pad button).
var using_pad := false

var _d: Dictionary = {}
var _plate: PanelContainer
var _key: Label
var _verb: Label
var _text_key := ""
var _shown := false
var _alpha := 0.0
var _breath_t := 0.0
var _rest_box: StyleBoxFlat
var _held_box: StyleBoxFlat


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("hold_prompt")) != TYPE_DICTIONARY:
		push_error("HoldPrompt: could not read 'hold_prompt' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["hold_prompt"] as Dictionary


func _ready() -> void:
	name = &"HoldPrompt"
	_d = load_data()
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	UiSettings.shared().follow(self)
	using_pad = InputNames.using_pad
	_build()
	if _text_key != "":
		_verb.text = tr(_text_key)
	_key.text = key_text()
	_apply()


func _process(delta: float) -> void:
	advance(delta)


## Shows the prompt with the verb `text_key` (a loc key). It fades in from where it is.
func show_prompt(text_key: String) -> void:
	_text_key = text_key
	_shown = true
	held = false
	_breath_t = 0.0
	if _verb != null:
		_verb.text = tr(text_key)
		_key.text = key_text()
	_apply()


## Fades the prompt out.
func hide_prompt() -> void:
	_shown = false
	held = false
	_apply()


## Whether the action is held this frame: the keycap lights while it is, and the plate breathes
## while it is not. Nothing is counted.
func set_held(on: bool) -> void:
	if on != held:
		held = on
		_breath_t = 0.0
		_apply()


## Steps the fade and the breath by `delta` seconds (from _process; tests call it directly).
func advance(delta: float) -> void:
	# Follow the shared device tracking (UiInput, M2-UI-26): the key switches with the player's hands.
	if using_pad != InputNames.using_pad:
		using_pad = InputNames.using_pad
		if _key != null:
			_key.text = key_text()
	var fade := maxf(_num("fade_sec"), 0.001)
	_alpha = clampf(_alpha + (delta / fade if _shown else -delta / fade), 0.0, 1.0)
	if _shown and not held:
		_breath_t = fmod(_breath_t + delta, maxf(_num("breath_sec"), 0.001))
	_apply()


## True while any of the plate can be seen.
func is_showing() -> bool:
	return _alpha > 0.0


func verb_text_shown() -> String:
	return _verb.text if _verb != null else ""


func key_text_shown() -> String:
	return _key.text if _key != null else ""


## The action's binding by name for the device used last ("" when unbound).
func key_text() -> String:
	return InputNames.first_name(action, using_pad) if action != &"" else ""


## The plate's alpha now: the fade times the breath (1 while held, or with reduced motion).
func plate_alpha() -> float:
	return _alpha * breath()


## The breath's factor now, breath_low..1 (a slow cosine), or 1 while held or with reduced motion.
func breath() -> float:
	if held or not _shown or UiSettings.shared().reduced_motion():
		return 1.0
	var low := clampf(_num("breath_low"), 0.0, 1.0)
	var phase := _breath_t / maxf(_num("breath_sec"), 0.001)
	return lerpf(1.0, low, 0.5 - 0.5 * cos(phase * TAU))


## The plate (tests and the layout audit read it).
func plate() -> Control:
	return _plate


func _apply() -> void:
	if _plate == null:
		return
	_plate.visible = _alpha > 0.0
	_plate.modulate.a = plate_alpha()
	_key.add_theme_stylebox_override(&"normal", _held_box if held else _rest_box)


func _build() -> void:
	var pm: Dictionary = _d.get("plate", {})
	_plate = PanelContainer.new()
	_plate.name = &"Plate"
	_plate.theme_type_variation = &"PanelSmall"
	_plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_plate)
	# Centred at the bottom at any aspect: it grows both ways from its anchor (M2-UI-29).
	_plate.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	_plate.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_plate.grow_vertical = Control.GROW_DIRECTION_BEGIN
	var lift := bottom_px if bottom_px >= 0.0 else _num("bottom_px")
	_plate.offset_top = -lift
	_plate.offset_bottom = -lift
	var row := HBoxContainer.new()
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override(&"separation", int(HudLayout.num(pm, "sep_px")))
	_plate.add_child(row)
	_key = Label.new()
	_key.name = &"Key"
	_key.theme_type_variation = &"HudNumber"
	_key.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_key.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_key.custom_minimum_size.x = HudLayout.num(_d.get("keycap", {}), "min_width")
	_key.add_theme_color_override(&"font_color", _c(&"focus_gold"))
	_rest_box = _keycap_box(false)
	_held_box = _keycap_box(true)
	row.add_child(_key)
	_verb = Label.new()
	_verb.name = &"Verb"
	_verb.theme_type_variation = &"SmallLabel"
	_verb.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	row.add_child(_verb)


## The keycap: a gold-ruled box, lit while held (the data's palette roles).
func _keycap_box(lit: bool) -> StyleBoxFlat:
	var km: Dictionary = _d.get("keycap", {})
	var box := StyleBoxFlat.new()
	box.bg_color = _c(StringName(str(_d.get("held_fill" if lit else "rest_fill", ""))))
	box.border_color = _c(StringName(str(_d.get("held_border" if lit else "rest_border", ""))))
	box.set_border_width_all(int(HudLayout.num(km, "border_px")))
	box.set_corner_radius_all(int(HudLayout.num(km, "radius_px")))
	box.content_margin_left = HudLayout.num(km, "pad_x")
	box.content_margin_right = HudLayout.num(km, "pad_x")
	return box


func _c(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


func _num(key: String) -> float:
	return HudLayout.num(_d, key)
