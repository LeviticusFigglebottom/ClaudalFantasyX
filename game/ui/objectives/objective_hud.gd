class_name ObjectiveHud
extends Control
## The objective line in the field (M2-UI-17): a small tide-notch panel at the top left that says
## what to do next (ObjectiveTracker over game/data/flow/objectives.json). It slides in when the
## objective changes, once when the field first takes input after a scene loads, and on demand
## (the remappable `field_objective` action: Tab, or the pad's Back button), holds, then fades.
## It never shows while the field controller refuses input (cutscenes, conversations) or the tree
## is paused (menus); battle is another scene. It follows UiSettings (text size, palette, reduced
## motion: a fade without the slide). It also carries the destination cue (ObjectiveCue, M2-UI-19).
## FieldController attaches it with ObjectiveHud.attach(self). Layout: game/data/ui/objective_hud.json.

enum Phase { HIDDEN, IN, HOLD, OUT }

const DATA_PATH := "res://game/data/ui/objective_hud.json"
const ACTION := &"field_objective"

## The player whose input state gates the line (null in tests that drive it directly).
var controller: FieldController
var tracker: ObjectiveTracker
var maps: ZoneMaps
## The zone the field is in (ZoneMaps id; &"" when the scene has no map).
var zone: StringName = &""
var phase := Phase.HIDDEN
## The destination cue drawn under the line.
var cue: ObjectiveCue

var _d: Dictionary = {}
var _panel: PanelContainer
var _glyph: Control
var _label: Label
var _line: Label
var _t := 0.0
var _pending := true
var _was_allowed := false
var _rest_x := 0.0


## Adds the line (on its own CanvasLayer) under field controller `c`, and returns it.
static func attach(c: FieldController) -> ObjectiveHud:
	ensure_action()
	var layer := CanvasLayer.new()
	layer.name = &"ObjectiveLayer"
	layer.layer = int(load_data().get("canvas_layer", 1))
	var hud := ObjectiveHud.new()
	hud.controller = c
	layer.add_child(hud)
	c.add_child(layer)
	return hud


## Adds `field_objective` to the InputMap when it is missing (also called before the Controls page
## captures its defaults, so the action is remappable).
static func ensure_action() -> void:
	var d := load_data()
	FieldInput.add_actions(d.get("action", {}) as Dictionary, float(d.get("deadzone", 0.0)))


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("objective_hud")) != TYPE_DICTIONARY:
		push_error("ObjectiveHud: could not read 'objective_hud' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["objective_hud"] as Dictionary


func _ready() -> void:
	name = &"ObjectiveHud"
	ensure_action()
	_d = load_data()
	process_mode = Node.PROCESS_MODE_ALWAYS  # so it can hide itself while a menu pauses the tree
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	UiSettings.shared().follow(self)
	if tracker == null:
		tracker = ObjectiveTracker.new()
	if maps == null:
		maps = ZoneMaps.new()
	if zone == &"" and get_tree().current_scene != null:
		zone = maps.zone_for_scene(get_tree().current_scene.scene_file_path)
	_build()
	cue = ObjectiveCue.new()
	cue.hud = self
	add_child(cue)
	EventBus.flag_changed.connect(_on_flag_changed)
	_line.text = tracker.line(zone)
	_apply(0.0)


func _process(delta: float) -> void:
	advance(delta)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(ACTION) and allowed():
		show_now()
		get_viewport().set_input_as_handled()


## True while the line may be seen: the field takes input and no menu pauses the tree.
func allowed() -> bool:
	if controller != null and (not is_instance_valid(controller) or not controller.accepts_input):
		return false
	return not (is_inside_tree() and get_tree().paused)


## Shows the current objective now (from the start of the slide-in, or held if already up).
func show_now() -> void:
	_line.text = tracker.line(zone)
	_pending = false
	if phase == Phase.HOLD or phase == Phase.IN:
		_t = 0.0 if phase == Phase.HOLD else _t
		return
	phase = Phase.IN
	_t = 0.0


## Steps the line by `delta` seconds (from _process; tests call it directly).
func advance(delta: float) -> void:
	var ok := allowed()
	if not ok:
		_was_allowed = false
		phase = Phase.HIDDEN
		_apply(0.0)
		return
	if not _was_allowed:
		_was_allowed = true
		if _pending and not tracker.current(zone).is_empty():
			show_now()  # on its own only when something calls; "nothing to do" waits for the button
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
				phase = Phase.HIDDEN
				_t = 0.0
	_apply(_visibility())


func is_showing() -> bool:
	return phase != Phase.HIDDEN


func line_text() -> String:
	return _line.text


## The objective's world target (Vector3.INF when it has none or it is in another zone).
func target_position() -> Vector3:
	var t := tracker.target(zone)
	if t.is_empty() or StringName(str(t.get("zone", ""))) != zone:
		return Vector3.INF
	return maps.poi_position(zone, StringName(str(t.get("poi", ""))))


func _on_flag_changed(_flag: StringName, _value: Variant) -> void:
	var now := tracker.line(zone)
	if now == _line.text:
		return
	_line.text = now
	_pending = not tracker.current(zone).is_empty()
	if _pending and allowed():
		show_now()


## 0..1: how far the line is in.
func _visibility() -> float:
	match phase:
		Phase.IN:
			return clampf(_t / maxf(_num("in_sec"), 0.001), 0.0, 1.0)
		Phase.HOLD:
			return 1.0
		Phase.OUT:
			return 1.0 - clampf(_t / maxf(_num("out_sec"), 0.001), 0.0, 1.0)
	return 0.0


func _apply(v: float) -> void:
	if _panel == null:
		return
	_panel.visible = v > 0.0
	_panel.modulate.a = v
	var slide := 0.0 if UiSettings.shared().reduced_motion() else _num("slide_px") * (1.0 - v)
	_panel.position.x = _rest_x - slide


func _build() -> void:
	var pm: Dictionary = _d.get("panel", {})
	var r := HudLayout.rect_of(pm)
	_panel = PanelContainer.new()
	_panel.theme_type_variation = &"PanelSmall"
	_panel.position = r.position
	_panel.size = r.size
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_rest_x = r.position.x
	add_child(_panel)
	var box := VBoxContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.add_child(box)
	var head := HBoxContainer.new()
	head.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(head)
	_glyph = Control.new()
	var g := HudLayout.num(pm, "glyph_px")
	_glyph.custom_minimum_size = Vector2(g * 2.0, HudLayout.num(pm, "label_height"))
	_glyph.draw.connect(_draw_glyph)
	head.add_child(_glyph)
	_label = Label.new()
	_label.theme_type_variation = &"DimLabel"
	_label.text = tr("OBJ_LABEL")
	head.add_child(_label)
	_line = Label.new()
	_line.theme_type_variation = &"HelpLabel"
	_line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	# No overrun trim: a trimming Label asks for no height, so the panel would never grow for a
	# wrapped line. It grows (PanelContainer) up to max_lines, then the rest is cut.
	_line.max_lines_visible = int(HudLayout.num(pm, "max_lines"))
	_line.custom_minimum_size.x = r.size.x - HudLayout.num(pm, "pad") * 2.0
	box.add_child(_line)


## A small gold diamond with a lamp dot: the objective's mark (the map's marker shares the shape).
func _draw_glyph() -> void:
	var g := HudLayout.num(_d.get("panel", {}), "glyph_px")
	var c := Vector2(g, _glyph.size.y * 0.5)
	var gold := get_theme_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE)
	var pts := SwellRingView.diamond(c, g * 0.75)
	pts.append(pts[0])
	_glyph.draw_polyline(pts, gold, 2.0, true)
	_glyph.draw_circle(c, g * 0.25, get_theme_color(&"focus", HymnThemeBuilder.PALETTE_TYPE))


func _num(key: String) -> float:
	return HudLayout.num(_d, key)
