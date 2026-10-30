class_name DocumentReader
extends Control
## The document reader (M4-A2P-080; docs/kb/plan/act2/ui/screens.md section 1): a record's two or three panes side
## by side in the codex's frame (one for a found record), where the player finds the lines written in the same hand.
## Words and marks: DocumentReaderModel. Layout: game/data/ui/document_reader.json (1920x1080 reference). It follows
## UiSettings (text size, palette, reduced motion) like the codex.
##
## Input (keyboard and controller through ui_*): ui_left / ui_right choose the pane, ui_up / ui_down the line (the
## pane scrolls to keep it in view), ui_accept marks the line or clears its mark, ui_page_up / ui_page_down scroll
## the pane, ui_cancel closes (the marks are kept in the model). Mouse: hover a line to put the cursor on it, click it
## to mark, the wheel scrolls the pane it is over, right click is Cancel (UiInput). The line under the panes says how
## many hands are left; a found hand's lines turn gold and a gold rule joins them across the panes. Open it with
## DocumentReader.open_in(host, model) (its own CanvasLayer; it pauses the tree while open).

signal closed
## The close transition has finished: open_in's layer frees itself.
signal gone
## A hand was found (its id); `finished` follows when it was the last.
signal hand_found(hand: StringName)
signal finished

const SCENE_PATH := "res://game/ui/codex/document_reader.tscn"
const DATA_PATH := "res://game/data/ui/document_reader.json"
const SCRIM_SHADER := preload("res://game/ui/shaders/scrim.gdshader")
const HELP_KEY := "READER_HELP"
const HELP_ONE_KEY := "READER_HELP_ONE"

## Pause the tree while open (the field must not move under it).
@export var pause_tree := true

var model: DocumentReaderModel
## The pane with the cursor, and each pane's cursor line.
var pane := 0
var cursors: Array[int] = []

var _d: Dictionary = {}
var _pm: Dictionary = {}
var _title: Label
var _hands: Label
var _help: Label
var _clips: Array[Control] = []
var _boxes: Array[Control] = []
var _frames: Array[PanelContainer] = []
var _scrolls: Array[float] = []
var _rules: Control
## Each found hand's draw-on, 0..1, in the order found.
var _rule_on: Array[float] = []
var _owns_pause := false
var _is_closed := false
var _motion: MenuMotion


## Instances the reader on its own CanvasLayer under `host` and opens it; the layer frees itself when it closes.
static func open_in(host: Node, with_model: DocumentReaderModel) -> DocumentReader:
	var reader := (load(SCENE_PATH) as PackedScene).instantiate() as DocumentReader
	reader.configure(with_model)
	var layer := CanvasLayer.new()
	layer.layer = int(load_data().get("canvas_layer", 1))
	layer.process_mode = Node.PROCESS_MODE_ALWAYS
	layer.add_child(reader)
	reader.gone.connect(layer.queue_free)
	host.add_child(layer)
	return reader


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("document_reader")) != TYPE_DICTIONARY:
		push_error("DocumentReader: could not read 'document_reader' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["document_reader"] as Dictionary


## Sets the model before the reader enters the tree.
func configure(with_model: DocumentReaderModel) -> void:
	model = with_model


func _ready() -> void:
	_d = load_data()
	_pm = _d.get("panes", {})
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	UiSettings.shared().follow(self)
	_build()
	UiFrame.centre(self)
	for i in model.pane_count():
		cursors.append(0)
		_scrolls.append(0.0)
	for i in model.found.size():
		_rule_on.append(1.0)
	_refresh()
	if pause_tree and not get_tree().paused:
		get_tree().paused = true
		_owns_pause = true
	MenuMotion.follow_reduced_motion(self)
	_motion = MenuMotion.new(self)
	_motion.gone.connect(gone.emit)
	_motion.play_in(false)


func _exit_tree() -> void:
	_restore_pause()


func _process(delta: float) -> void:
	var step := delta / maxf(HudLayout.num(_pm, "rule_sec"), 0.001)
	var drawing := false
	for i in _rule_on.size():
		if _rule_on[i] < 1.0:
			_rule_on[i] = minf(_rule_on[i] + step, 1.0)
			drawing = true
	if drawing:
		_rules.queue_redraw()


func is_open() -> bool:
	return not _is_closed


func title_text() -> String:
	return _title.text


func hands_text() -> String:
	return _hands.text


func help_text() -> String:
	return _help.text


## The line label `line` of pane `p` (tests and the parity walk hover and click it).
func line_label(p: int, line: int) -> Label:
	if p < 0 or p >= _boxes.size() or line < 0 or line >= _boxes[p].get_child_count():
		return null
	return _boxes[p].get_child(line) as Label


## Pane `p`'s clip (the wheel over it scrolls it).
func pane_area(p: int) -> Control:
	return _clips[p] if p >= 0 and p < _clips.size() else null


func scroll_of(p: int) -> float:
	return _scrolls[p]


func max_scroll(p: int) -> float:
	return maxf(_boxes[p].size.y - _clips[p].size.y, 0.0)


## Each found hand's rule draw-on (0..1), in the order found.
func rule_progress() -> Array[float]:
	return _rule_on.duplicate()


func _unhandled_input(event: InputEvent) -> void:
	if is_open() and handle_input(event):
		get_viewport().set_input_as_handled()


## Applies one input event. Returns true when the reader used it. Tests call this directly.
func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	if event.is_action_pressed(&"ui_up", true):
		move_line(-1)
	elif event.is_action_pressed(&"ui_down", true):
		move_line(1)
	elif event.is_action_pressed(&"ui_left", true):
		move_pane(-1)
	elif event.is_action_pressed(&"ui_right", true):
		move_pane(1)
	elif event.is_action_pressed(&"ui_page_up", true):
		scroll_by(pane, -1)
	elif event.is_action_pressed(&"ui_page_down", true):
		scroll_by(pane, 1)
	elif event.is_action_pressed(&"ui_accept"):
		mark()
	elif event.is_action_pressed(&"ui_cancel"):
		close()
	else:
		return false
	return true


func move_pane(delta: int) -> void:
	var to := clampi(pane + delta, 0, maxi(model.pane_count() - 1, 0))
	set_cursor(to, cursors[to])


func move_line(delta: int) -> void:
	set_cursor(pane, cursors[pane] + delta)


## Puts the cursor on `line` of pane `p` (clamped), scrolling the pane to keep it in view.
func set_cursor(p: int, line: int) -> void:
	if model.pane_count() == 0:
		return
	pane = clampi(p, 0, model.pane_count() - 1)
	cursors[pane] = clampi(line, 0, maxi(model.lines(pane).size() - 1, 0))
	_reveal(pane, cursors[pane])
	_paint()


## Marks the line under the cursor, or clears its mark (DocumentReaderModel.toggle).
func mark() -> void:
	var hid := model.toggle(pane, cursors[pane])
	if hid != &"":
		_rule_on.append(1.0 if UiSettings.shared().reduced_motion() else 0.0)
		hand_found.emit(hid)
		if model.all_found():
			finished.emit()
	_refresh()


## Scrolls pane `p` one step down (1) or up (-1).
func scroll_by(p: int, direction: int) -> void:
	_set_scroll(p, _scrolls[p] + direction * HudLayout.num(_pm, "scroll_step_px"))


func close() -> void:
	if _is_closed:
		return
	_is_closed = true
	_restore_pause()
	if _motion != null:
		_motion.play_out(false)
	else:
		visible = false
		gone.emit()
	closed.emit()


## The open and close transitions (null before _ready). Tests drive them with motion().finish().
func motion() -> MenuMotion:
	return _motion


func _refresh() -> void:
	_hands.text = model.hands_text()
	_paint()
	_rules.queue_redraw()


## Colours each line: the cursor's wash, a mark's bar, a found hand's gold.
func _paint() -> void:
	var gold := _c(&"focus_gold")
	for p in _boxes.size():
		for i in _boxes[p].get_child_count():
			var l := _boxes[p].get_child(i) as Label
			if model.found_hand_at(p, i) != &"":
				l.add_theme_color_override(&"font_color", gold)
			else:
				l.remove_theme_color_override(&"font_color")
			var under := l.get_node(^"Under") as ColorRect
			under.visible = p == pane and i == cursors[p]
			var bar := l.get_node(^"Mark") as ColorRect
			bar.visible = model.marks[p] == i


func _reveal(p: int, line: int) -> void:
	var l := line_label(p, line)
	if l == null:
		return
	var top := l.position.y
	var bottom := top + l.size.y
	var view := _clips[p].size.y
	if top < _scrolls[p]:
		_set_scroll(p, top)
	elif bottom > _scrolls[p] + view:
		_set_scroll(p, bottom - view)


func _set_scroll(p: int, offset: float) -> void:
	_scrolls[p] = clampf(offset, 0.0, max_scroll(p))
	_boxes[p].position.y = -_scrolls[p]
	_paint()
	_rules.queue_redraw()


## The point a found line's rule leaves from or arrives at: the line's side (right: `out`), at its middle, held
## inside its pane's view when the line is scrolled away.
func _rule_end(p: int, line: int, out: bool) -> Vector2:
	var l := line_label(p, line)
	var clip := _clips[p]
	var r := clip.get_global_rect()
	var y := r.get_center().y
	if l != null:
		y = clampf(l.get_global_rect().get_center().y, r.position.y, r.end.y)
	var frame := _frames[p].get_global_rect()
	var at := Vector2(frame.end.x if out else frame.position.x, y)
	return _rules.get_global_transform().affine_inverse() * at


func _draw_rules() -> void:
	var gold := _c(&"focus_gold")
	var w := HudLayout.num(_pm, "rule_px")
	var links := model.found_links()
	for k in links.size():
		var cells: Array = links[k]
		cells.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return a.x < b.x)
		var on := _rule_on[k] if k < _rule_on.size() else 1.0
		for j in cells.size() - 1:
			var a: Vector2i = cells[j]
			var b: Vector2i = cells[j + 1]
			var from := _rule_end(a.x, a.y, true)
			var to := _rule_end(b.x, b.y, false)
			_rules.draw_line(from, from.lerp(to, on), gold, w, true)


func _restore_pause() -> void:
	if _owns_pause and is_inside_tree():
		get_tree().paused = false
	_owns_pause = false


func _c(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


func _build() -> void:
	var scrim := ColorRect.new()
	scrim.set_anchors_preset(Control.PRESET_FULL_RECT)
	scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := ShaderMaterial.new()
	mat.shader = SCRIM_SHADER
	mat.set_shader_parameter(&"tint", _c(&"scrim"))
	scrim.material = mat
	add_child(scrim)
	add_child(CausticBackdrop.new())
	var pm: Dictionary = _d.get("panel", {})
	var panel := Panel.new()
	HudLayout.place(panel, pm)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(panel)
	var pr := HudLayout.rect_of(pm)
	var pad := HudLayout.num(pm, "pad")
	var title_h := HudLayout.num(pm, "title_height")
	_title = _label(&"BannerLabel", Rect2(pr.position + Vector2(pad, pad), Vector2(pr.size.x - pad * 2.0, title_h)))
	_title.text = model.title()
	HudLayout.fit_label(_title, pr.size.x - pad * 2.0)
	var rule := OrnamentRule.new()
	var node := float(get_theme_constant(&"ornament_node_px", HymnThemeBuilder.PALETTE_TYPE))
	rule.position = Vector2(_title.position.x, _title.position.y + title_h - node)
	rule.size = Vector2(pr.size.x * 0.3, node * 2.0)
	add_child(rule)
	var help_h := HudLayout.num(pm, "help_height")
	var help_at := Vector2(pr.position.x + pad, pr.end.y - pad - help_h)
	_help = _label(&"HelpDimLabel", Rect2(help_at, Vector2(pr.size.x - pad * 2.0, help_h)))
	_help.text = tr(HELP_KEY if model.has_hands() else HELP_ONE_KEY)
	UiFrame.fit_line(_help, pr.size.x - pad * 2.0)
	var hands_h := HudLayout.num(_d, "hands_height")
	_hands = _label(&"DimLabel", Rect2(help_at - Vector2(0.0, hands_h), Vector2(pr.size.x - pad * 2.0, hands_h)))
	_build_panes()
	_rules = Control.new()
	_rules.set_anchors_preset(Control.PRESET_FULL_RECT)
	_rules.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_rules.draw.connect(_draw_rules)
	add_child(_rules)


func _build_panes() -> void:
	var area := HudLayout.rect_of(_pm)
	var n := maxi(model.pane_count(), 1)
	var gap := HudLayout.num(_pm, "gap")
	var w := (area.size.x - gap * (n - 1)) / n
	var pad := HudLayout.num(_pm, "pad")
	var title_h := HudLayout.num(_pm, "title_height")
	var sub_h := HudLayout.num(_pm, "sub_height")
	for p in model.pane_count():
		var r := Rect2(area.position + Vector2((w + gap) * p, 0.0), Vector2(w, area.size.y))
		var frame := PanelContainer.new()
		frame.theme_type_variation = &"PanelSmall"
		frame.position = r.position
		frame.size = r.size
		frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(frame)
		_frames.append(frame)
		var inner := Rect2(r.position + Vector2(pad, pad), r.size - Vector2(pad, pad) * 2.0)
		var head := _label(&"HeaderLabel", Rect2(inner.position, Vector2(inner.size.x, title_h)))
		head.text = model.pane_title(p)
		HudLayout.fit_label(head, inner.size.x)
		var sub := _label(&"DimLabel", Rect2(inner.position + Vector2(0.0, title_h), Vector2(inner.size.x, sub_h)))
		sub.text = model.pane_label(p)
		var clip := Control.new()
		clip.clip_contents = true
		clip.mouse_filter = Control.MOUSE_FILTER_STOP
		clip.position = inner.position + Vector2(0.0, title_h + sub_h)
		clip.size = Vector2(inner.size.x, inner.size.y - title_h - sub_h)
		clip.gui_input.connect(_on_clip_input.bind(p))
		add_child(clip)
		_clips.append(clip)
		# The lines stack by hand (no container: their heights are known at once, frames or not), right of the
		# mark bars' room.
		var box := Control.new()
		box.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var room := HudLayout.num(_pm, "mark_px") * 2.0
		box.position = Vector2(room, 0.0)
		clip.add_child(box)
		_boxes.append(box)
		var y := 0.0
		for text in model.lines(p):
			var l := _line(text)
			box.add_child(l)
			l.position = Vector2(0.0, y)
			l.size = Vector2(clip.size.x - room, 0.0)
			l.size.y = HudLayout.lines_height(l)
			y += l.size.y + HudLayout.num(_pm, "line_gap")
		box.size = Vector2(clip.size.x - room, maxf(y - HudLayout.num(_pm, "line_gap"), 0.0))


func _line(text: String) -> Label:
	var l := Label.new()
	l.theme_type_variation = &"FlavorLabel"
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	l.text = text
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var under := ColorRect.new()
	under.name = "Under"
	var wash := _c(&"focus")
	wash.a = HudLayout.num(_pm, "cursor_alpha")
	under.color = wash
	under.set_anchors_preset(Control.PRESET_FULL_RECT)
	under.show_behind_parent = true
	under.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_child(under)
	var bar := ColorRect.new()
	bar.name = "Mark"
	bar.color = _c(&"focus_gold")
	bar.anchor_bottom = 1.0
	bar.offset_left = -HudLayout.num(_pm, "mark_px") * 2.0
	bar.offset_right = -HudLayout.num(_pm, "mark_px")
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_child(bar)
	return l


## The line of pane `p` at `y` in its clip's space (-1: none).
func _line_at(p: int, y: float) -> int:
	for i in _boxes[p].get_child_count():
		var l := _boxes[p].get_child(i) as Label
		var top := l.position.y - _scrolls[p]
		if y >= top and y < top + l.size.y:
			return i
	return -1


func _on_clip_input(event: InputEvent, p: int) -> void:
	var mb := event as InputEventMouseButton
	if mb != null and mb.pressed:
		if mb.button_index == MOUSE_BUTTON_WHEEL_UP or mb.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			scroll_by(p, -1 if mb.button_index == MOUSE_BUTTON_WHEEL_UP else 1)
			_clips[p].accept_event()
		elif mb.button_index == MOUSE_BUTTON_LEFT:
			var at := _line_at(p, mb.position.y)
			if at >= 0:
				set_cursor(p, at)
				mark()
				_clips[p].accept_event()
		return
	var mm := event as InputEventMouseMotion
	if mm != null:
		var at := _line_at(p, mm.position.y)
		if at >= 0 and (p != pane or at != cursors[p]):
			set_cursor(p, at)


func _label(variation: StringName, r: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.position = r.position
	l.size = r.size
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l
