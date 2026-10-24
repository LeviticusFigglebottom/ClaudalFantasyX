class_name DialogueBacklogPage
extends FieldSubmenu
## The Backlog page (M2-UI-25): the session's dialogue lines (DialogueBacklog), oldest at the top,
## opened scrolled to the latest. Each line is the speaker's name in the gold header style (none
## for narration) over its text. A FieldSubmenu: scrim and caustics, a gold-ruled title, the help
## line, the tree paused while open (so a cutscene holds), and UiSettings followed (text size,
## palette). DialogueAssist opens it with the `dialogue_backlog` action.
##
## Input: ui_up / ui_down scroll a step, the page keys a page, the mouse wheel a notch; the
## backlog action again or ui_cancel closes. Layout: game/data/ui/dialogue_assist.json
## "dialogue_backlog".

## The log shown (DialogueBacklog.shared() when left null).
var backlog: DialogueBacklog

var _list: Control
var _content: Control
var _track: Control
var _help: Label
## [name Label or null, text Label] per line, oldest first.
var _entries: Array[Array] = []
var _scroll := 0.0
var _content_h := 0.0
## The top of each line in the content, oldest first.
var _tops: Array[float] = []


func data_path() -> String:
	return DialogueAssist.DATA_PATH


func data_section() -> String:
	return "dialogue_backlog"


func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	var lm := _d.get("list", {}) as Dictionary
	if event.is_action_pressed(DialogueAssist.ACTION):
		close()
	elif event.is_action_pressed(&"ui_up", true):
		scroll_by(-HudLayout.num(lm, "step_px"))
	elif event.is_action_pressed(&"ui_down", true):
		scroll_by(HudLayout.num(lm, "step_px"))
	elif event.is_action_pressed(&"ui_page_up", true):
		scroll_by(-_page_px())
	elif event.is_action_pressed(&"ui_page_down", true):
		scroll_by(_page_px())
	elif _wheel(event) != 0:
		scroll_by(float(_wheel(event)) * HudLayout.num(lm, "wheel_px"))
	else:
		return super(event)
	return true


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and handle_input(event):
		accept_event()


## How far down the list is scrolled, in pixels (0 = the oldest line at the top).
func scroll_value() -> float:
	return _scroll


## The furthest scroll (0 when everything fits): the first line top at or past the point where the
## latest line's foot meets the list's foot, so the page at its foot starts on a whole line and the
## latest line is whole too (a little room may stay under it).
func max_scroll() -> float:
	var raw := maxf(_content_h - _list.size.y, 0.0) if _list != null else 0.0
	if raw <= 0.0:
		return 0.0
	for top in _tops:
		if top >= raw:
			return top
	return raw


func scroll_to(px: float) -> void:
	_scroll = clampf(px, 0.0, max_scroll())
	if _content != null:
		_content.position.y = -roundf(_scroll)
	if _track != null:
		_track.queue_redraw()


func scroll_by(px: float) -> void:
	scroll_to(_scroll + px)


func content_height() -> float:
	return _content_h


## The shown lines as [speaker name ("" for narration), text], oldest first.
func shown_lines() -> Array[PackedStringArray]:
	var out: Array[PackedStringArray] = []
	for e: Array in _entries:
		var head := e[0] as Label
		out.append(PackedStringArray([head.text if head != null else "", (e[1] as Label).text]))
	return out


func _build_page() -> void:
	if backlog == null:
		backlog = DialogueBacklog.shared()
	var dim := ColorRect.new()
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dim.color = Color(_c(&"panel_low"), HudLayout.num(_d, "dim_alpha"))
	add_child(dim)
	_help = _framed_panel(_d.get("panel", {}), tr("BACKLOG_TITLE"))
	_help.text = tr("BACKLOG_HELP")
	var lm := _d.get("list", {}) as Dictionary
	_list = Control.new()
	_list.name = &"List"
	HudLayout.place(_list, lm)
	_list.clip_contents = true
	_list.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_list)
	_content = Control.new()
	_content.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_list.add_child(_content)
	_track = Control.new()
	_track.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_track.draw.connect(_draw_track)
	add_child(_track)
	for line: Dictionary in backlog.lines():
		var speaker := str(line.get(DialogueBacklog.KEY_SPEAKER, ""))
		var head: Label = null
		if speaker != "":
			head = _entry_label(&"HeaderLabel", speaker)
		_entries.append([head, _entry_label(&"BodyLabel", str(line.get(DialogueBacklog.KEY_TEXT, "")))])
	if _entries.is_empty():
		_entries.append([null, _entry_label(&"HelpDimLabel", tr("BACKLOG_EMPTY"))])
	_layout()
	scroll_to(max_scroll())


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED and _content != null:
		_layout()  # a new text size or palette: re-measure and re-tint
		scroll_to(_scroll)


func _entry_label(variation: StringName, text: String) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.text = text
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_content.add_child(l)
	return l


## Stacks the lines down the list's width, each label as tall as its wrapped text.
func _layout() -> void:
	var lm := _d.get("list", {}) as Dictionary
	var w := _list.size.x
	var y := 0.0
	var gold := _c(&"focus_gold")
	_tops.clear()
	for e: Array in _entries:
		_tops.append(y)
		var head := e[0] as Label
		if head != null:
			head.add_theme_color_override(&"font_color", gold)
			y += _stack(head, w, y) + HudLayout.num(lm, "name_gap_px")
		y += _stack(e[1] as Label, w, y) + HudLayout.num(lm, "entry_gap_px")
	_content_h = maxf(y - HudLayout.num(lm, "entry_gap_px"), 0.0)
	_content.size = Vector2(w, _content_h)
	var tm := _d.get("track", {}) as Dictionary
	_track.position = Vector2(_list.position.x + w + HudLayout.num(tm, "offset_px"), _list.position.y)
	_track.size = Vector2(HudLayout.num(tm, "width_px"), _list.size.y)


## Places `l` at `y`, `w` wide, and returns its height.
func _stack(l: Label, w: float, y: float) -> float:
	l.position = Vector2(0.0, y)
	l.size = Vector2(w, 0.0)
	var h := l.get_minimum_size().y
	l.size = Vector2(w, h)
	return h


func _page_px() -> float:
	return _list.size.y * HudLayout.num(_d.get("list", {}) as Dictionary, "page_fraction")


## -1 for a wheel notch up, 1 down, 0 for anything else.
static func _wheel(event: InputEvent) -> int:
	var mb := event as InputEventMouseButton
	if mb == null or not mb.pressed:
		return 0
	if mb.button_index == MOUSE_BUTTON_WHEEL_UP:
		return -1
	if mb.button_index == MOUSE_BUTTON_WHEEL_DOWN:
		return 1
	return 0


## A faint track with a gold thumb, only when the lines overflow the list.
func _draw_track() -> void:
	var most := max_scroll()
	if most <= 0.0:
		return
	var h := _track.size.y
	var thumb := clampf(h * h / (most + h), HudLayout.num(_d.get("track", {}) as Dictionary, "min_thumb_px"), h)
	var at := (h - thumb) * _scroll / most
	_track.draw_rect(Rect2(Vector2.ZERO, _track.size), _c(&"separator_white"))
	_track.draw_rect(Rect2(0.0, at, _track.size.x, thumb), _c(&"focus_gold"))
