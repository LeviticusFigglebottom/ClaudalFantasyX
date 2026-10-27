class_name CodexNotice
extends Control
## The record hook in the field (M3-UI-03): an Interactable whose payload is {"record": "<codex
## id>"} marks that codex record found (CodexModel.add_record, through Game.set_flag) and this
## notice says so: the TipCard look at the lower right, a gold page glyph, "Record added to the
## Codex" and the record's title. It fades in, holds, fades out; a second record waits its turn.
## A record already found, or an id that is not a record, shows nothing. While the field refuses
## input or a menu pauses the tree it hides and its clock stops. Attached by FieldHud; it listens
## on the EventBus (FieldEvents.INTERACTED) like TownServices. Layout and timing:
## game/data/ui/codex_menu.json "codex_notice".

enum Phase { HIDDEN, IN, HOLD, OUT }

const DATA_PATH := "res://game/data/ui/codex_menu.json"
const KEY_RECORD := "record"

## The player whose input state gates the notice (null in tests).
var controller: FieldController
var model: CodexModel
var phase := Phase.HIDDEN
## Records found and waiting to be announced (titles), oldest first.
var queue: Array[String] = []

var _d: Dictionary = {}
var _panel: PanelContainer
var _glyph: Control
var _head: Label
var _name: Label
var _t := 0.0


## Adds the notice (on its own CanvasLayer) under field controller `c`, and returns it.
static func attach(c: FieldController) -> CodexNotice:
	var layer := CanvasLayer.new()
	layer.name = &"CodexNoticeLayer"
	layer.layer = int(load_data().get("canvas_layer", 1))
	var notice := CodexNotice.new()
	notice.controller = c
	layer.add_child(notice)
	c.add_child(layer)
	return notice


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("codex_notice")) != TYPE_DICTIONARY:
		push_error("CodexNotice: could not read 'codex_notice' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["codex_notice"] as Dictionary


func _enter_tree() -> void:
	FieldEvents.connect_interacted(_on_interacted)


func _exit_tree() -> void:
	if EventBus.is_connected(FieldEvents.INTERACTED, _on_interacted):
		EventBus.disconnect(FieldEvents.INTERACTED, _on_interacted)


func _ready() -> void:
	name = &"CodexNotice"
	process_mode = Node.PROCESS_MODE_ALWAYS  # so it can hide itself while a menu pauses the tree
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	UiSettings.shared().follow(self)
	if model == null:
		model = CodexModel.from_game()
	_d = load_data()
	_build()
	_apply(0.0)


func _process(delta: float) -> void:
	advance(delta)


## Marks the record a payload names found and queues its notice. Returns true when it did: false
## for any other payload, an unknown or non-record id, or a record already found.
func handle(payload: Dictionary) -> bool:
	if not payload.has(KEY_RECORD):
		return false
	var id := StringName(str(payload[KEY_RECORD]))
	if not model.add_record(id):
		return false
	queue.append(model.title(id))
	return true


## True while the notice may be seen: the field takes input and no menu pauses the tree.
func allowed() -> bool:
	if controller != null and (not is_instance_valid(controller) or not controller.accepts_input):
		return false
	return not (is_inside_tree() and get_tree().paused)


## Steps the notice by `delta` seconds (from _process; tests call it directly).
func advance(delta: float) -> void:
	if not allowed():
		_apply(0.0)
		return
	if phase == Phase.HIDDEN:
		if queue.is_empty():
			_apply(0.0)
			return
		_name.text = queue.pop_front()
		phase = Phase.IN
		_t = 0.0
	else:
		_t += delta
	match phase:
		Phase.IN:
			if _t >= _num("fade_sec"):
				phase = Phase.HOLD
				_t = 0.0
		Phase.HOLD:
			if _t >= _num("hold_sec"):
				phase = Phase.OUT
				_t = 0.0
		Phase.OUT:
			if _t >= _num("fade_sec"):
				phase = Phase.HIDDEN
				_t = 0.0
	_apply(_visibility())


func is_showing() -> bool:
	return phase != Phase.HIDDEN


func head_text() -> String:
	return _head.text


func name_text() -> String:
	return _name.text


func panel_visible() -> bool:
	return _panel.visible


func _on_interacted(_id: StringName, _kind: StringName, payload: Dictionary) -> void:
	handle(payload)


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
	HudLayout.place(_panel, pm)  # lower right at any aspect, growing up for a long title (M2-UI-29)
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
	_head = Label.new()
	_head.theme_type_variation = &"HeaderLabel"
	_head.text = tr("CODEX_NOTICE_TITLE")
	head.add_child(_head)
	_name = Label.new()
	_name.theme_type_variation = &"MenuLabel"
	_name.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART  # no overrun trim: the panel grows
	_name.custom_minimum_size.x = r.size.x - HudLayout.num(pm, "pad") * 2.0
	box.add_child(_name)


## A page: a gold leaf outline with a folded corner (a record, not a tip's lamp).
func _draw_glyph() -> void:
	var g := HudLayout.num(_d.get("panel", {}), "glyph_px")
	var c := Vector2(g, _glyph.size.y * 0.5)
	var gold := get_theme_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE)
	var w := g * 0.7
	var h := g
	var fold := g * 0.35
	var pts := PackedVector2Array(
		[
			c + Vector2(-w, -h),
			c + Vector2(w - fold, -h),
			c + Vector2(w, -h + fold),
			c + Vector2(w, h),
			c + Vector2(-w, h),
			c + Vector2(-w, -h),
		]
	)
	_glyph.draw_polyline(pts, gold, 2.0, true)
	_glyph.draw_line(c + Vector2(-w * 0.5, 0.0), c + Vector2(w * 0.5, 0.0), gold, 1.5, true)
	_glyph.draw_line(c + Vector2(-w * 0.5, h * 0.45), c + Vector2(w * 0.5, h * 0.45), gold, 1.5, true)


func _num(key: String) -> float:
	return HudLayout.num(_d, key)
