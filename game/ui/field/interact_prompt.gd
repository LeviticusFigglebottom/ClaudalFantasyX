class_name InteractPrompt
extends Control
## The field interaction prompt (M2-UI-20, intro audit 1): when the player can use an interactable,
## a small plate floats over it with a keycap for the field_interact binding and the verb
## (Interactable.prompt_key: "Listen", "Look", "Browse the wares"). The keycap shows the first key,
## or the first pad button once the pad was the last thing used. Behind the camera or near the
## screen edge it docks at the bottom centre. It fades in and out, hides while the field refuses
## input (cutscenes, conversations) or a menu pauses the tree, and follows UiSettings.
## Layout: game/data/ui/interact_prompt.json.

const DATA_PATH := "res://game/data/ui/interact_prompt.json"

## The player whose reach and input state drive the prompt (null in tests and shots that set `pick`).
var controller: FieldController
## Returns the Interactable to prompt for, or null. Default: controller.nearest_interactable().
var pick: Callable
## True once the pad was the last device used (the keycap shows a pad button).
var using_pad := false
## The interactable the plate is for (null when none).
var target: Interactable
## The last placement (tests read it): {at: Vector2 (plate centre bottom), docked: bool}.
var placement: Dictionary = {}

var _d: Dictionary = {}
var _plate: PanelContainer
var _key: Label
var _verb: Label
var _alpha := 0.0


## Adds the prompt (on its own CanvasLayer) under field controller `c`, and returns it.
static func attach(c: FieldController) -> InteractPrompt:
	var layer := CanvasLayer.new()
	layer.name = &"InteractLayer"
	layer.layer = int(load_data().get("canvas_layer", 1))
	var p := InteractPrompt.new()
	p.controller = c
	layer.add_child(p)
	c.add_child(layer)
	return p


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("interact_prompt")) != TYPE_DICTIONARY:
		push_error("InteractPrompt: could not read 'interact_prompt' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["interact_prompt"] as Dictionary


func _ready() -> void:
	name = &"InteractPrompt"
	_d = load_data()
	process_mode = Node.PROCESS_MODE_ALWAYS  # so it can hide itself while a menu pauses the tree
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	UiSettings.shared().follow(self)
	using_pad = InputNames.using_pad
	_build()
	_apply()


func _input(event: InputEvent) -> void:
	note_device(event)


func _process(delta: float) -> void:
	advance(delta)


## Remembers whether the pad or the keyboard and mouse was used last (InputNames.using_pad).
func note_device(event: InputEvent) -> void:
	InputNames.note(event, HudLayout.num(_d, "pad_deadzone"))
	using_pad = InputNames.using_pad


## True while the prompt may be seen: the field takes input and no menu pauses the tree.
func allowed() -> bool:
	if controller != null and (not is_instance_valid(controller) or not controller.accepts_input):
		return false
	return not (is_inside_tree() and get_tree().paused)


## Steps the prompt by `delta` seconds: picks the target, fades, and places the plate.
func advance(delta: float) -> void:
	# Follow the shared tracking (UiInput, M2-UI-26): an event another node took first, such as a
	# right click UiInput turned into Cancel, never reaches this node's _input.
	using_pad = InputNames.using_pad
	var it: Interactable = null
	if allowed():
		it = _pick()
	if it != null:
		if it != target:
			target = it
			_verb.text = verb_text(it)
		_key.text = key_text()
	var fade := maxf(HudLayout.num(_d, "fade_sec"), 0.001)
	_alpha = clampf(_alpha + (delta / fade if it != null else -delta / fade), 0.0, 1.0)
	if it == null and _alpha <= 0.0:
		target = null
	_place()
	_apply()


func is_showing() -> bool:
	return _alpha > 0.0 and target != null


func key_text_shown() -> String:
	return _key.text


func verb_text_shown() -> String:
	return _verb.text


## The verb for `it`: its prompt_key, or the default ("Look about").
func verb_text(it: Interactable) -> String:
	var key := it.prompt_key if it.prompt_key != "" else str(_d.get("default_key", ""))
	return tr(key)


## The field_interact binding by name: its first pad button when the pad was used last, else its
## first key (InputNames).
func key_text() -> String:
	return InputNames.first_name(FieldInput.INTERACT, using_pad)


## Where the plate goes for a point at screen `screen` (`behind`: behind the camera) on a screen of
## `size` (reference pixels): over the point, or docked at the bottom centre. Pure, for tests.
func place(behind: bool, screen: Vector2, size: Vector2) -> Dictionary:
	var edge := HudLayout.num(_d, "edge_px")
	var inner := Rect2(Vector2(edge, edge), size - Vector2(edge, edge) * 2.0)
	if behind or not inner.has_point(screen):
		return {"at": Vector2(size.x * 0.5, HudLayout.num(_d, "dock_y")), "docked": true}
	return {"at": screen - Vector2(0.0, HudLayout.num(_d, "gap_px")), "docked": false}


func _pick() -> Interactable:
	if pick.is_valid():
		return pick.call() as Interactable
	if controller != null:
		return controller.nearest_interactable()
	return null


func _place() -> void:
	if target == null or not is_instance_valid(target) or not is_inside_tree():
		return
	var cam := get_viewport().get_camera_3d()
	var size := get_viewport_rect().size
	if cam == null:
		placement = place(true, Vector2.ZERO, size)
	else:
		var world := target.global_position + Vector3.UP * HudLayout.num(_d, "lift_m")
		placement = place(cam.is_position_behind(world), cam.unproject_position(world), size)


func _apply() -> void:
	if _plate == null:
		return
	_plate.visible = _alpha > 0.0 and target != null
	_plate.modulate.a = _alpha
	if placement.is_empty():
		return
	_plate.reset_size()
	var at: Vector2 = placement["at"]
	_plate.position = Vector2(at.x - _plate.size.x * 0.5, at.y - _plate.size.y).round()


func _build() -> void:
	var pm: Dictionary = _d.get("plate", {})
	_plate = PanelContainer.new()
	_plate.theme_type_variation = &"PanelSmall"
	_plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_plate)
	var row := HBoxContainer.new()
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override(&"separation", int(HudLayout.num(pm, "sep_px")))
	_plate.add_child(row)
	_key = Label.new()
	_key.theme_type_variation = &"HudNumber"
	_key.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_key.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_key.add_theme_stylebox_override(&"normal", _keycap_box())
	_key.custom_minimum_size.x = HudLayout.num(_d.get("keycap", {}), "min_width")
	_key.add_theme_color_override(&"font_color", _c(&"focus_gold"))
	row.add_child(_key)
	_verb = Label.new()
	_verb.theme_type_variation = &"SmallLabel"
	_verb.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	row.add_child(_verb)


## The keycap: a gold-ruled box on the low panel colour, at least min_width wide.
func _keycap_box() -> StyleBoxFlat:
	var km: Dictionary = _d.get("keycap", {})
	var box := StyleBoxFlat.new()
	box.bg_color = _c(&"panel_low")
	box.border_color = _c(&"line_gold")
	box.set_border_width_all(int(HudLayout.num(km, "border_px")))
	box.set_corner_radius_all(int(HudLayout.num(km, "radius_px")))
	box.content_margin_left = HudLayout.num(km, "pad_x")
	box.content_margin_right = HudLayout.num(km, "pad_x")
	return box


func _c(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)
