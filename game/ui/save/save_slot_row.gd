class_name SaveSlotRow
extends Control
## One row of the save menu (M1-ARC-03): slot name; chapter and location; play time and save
## time on the right. Slots without a readable record show their status line instead.
## A view only: it reads a SaveSlotInfo and never writes anything.

signal clicked

var info: SaveSlotInfo
var usable := true

var _m: Dictionary = {}
var _name: Label
var _chapter: Label
var _location: Label
var _status: Label
var _play_time: Label
var _stamp: Label
var _sep: ColorRect


func setup(metrics: Dictionary, row_size: Vector2) -> void:
	_m = metrics
	size = row_size
	mouse_filter = Control.MOUSE_FILTER_STOP
	var lh := _n("line_height")
	var y1 := _n("line1_y")
	var y2 := _n("line2_y")
	var detail_x := _n("detail_x")
	var right_w := _n("right_width")
	var right_x := size.x - _n("right_pad") - right_w
	var detail_w := right_x - detail_x
	_name = _label(&"MenuLabel", Rect2(_n("name_x"), y1, _n("name_width"), lh), HORIZONTAL_ALIGNMENT_LEFT)
	_chapter = _label(&"MenuLabel", Rect2(detail_x, y1, detail_w, lh), HORIZONTAL_ALIGNMENT_LEFT)
	_location = _label(&"HelpLabel", Rect2(detail_x, y2, detail_w, lh), HORIZONTAL_ALIGNMENT_LEFT)
	_status = _label(
		&"HelpLabel", Rect2(detail_x, y1, size.x - detail_x - _n("right_pad"), lh), HORIZONTAL_ALIGNMENT_LEFT
	)
	_play_time = _label(&"HudNumber", Rect2(right_x, y1, right_w, lh), HORIZONTAL_ALIGNMENT_RIGHT)
	_stamp = _label(&"DimLabel", Rect2(right_x, y2, right_w, lh), HORIZONTAL_ALIGNMENT_RIGHT)
	_sep = ColorRect.new()
	_sep.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_sep.color = _c(&"separator_white")
	var inset := _n("separator_inset")
	var line := float(get_theme_constant(&"line_px", HymnThemeBuilder.PALETTE_TYPE))
	_sep.position = Vector2(inset, size.y - line)
	_sep.size = Vector2(size.x - inset * 2.0, line)
	add_child(_sep)


## Fills the row. `bias_min` is the viewer's time-zone offset in minutes (SaveSlotInfo.timestamp_text).
func show_info(slot_info: SaveSlotInfo, is_usable: bool, bias_min: int, last_row: bool = false) -> void:
	info = slot_info
	usable = is_usable
	_name.text = info.slot_name()
	var readable := info.is_loadable()
	_chapter.visible = readable
	_location.visible = readable
	_play_time.visible = readable
	_stamp.visible = readable
	_status.visible = not readable
	_sep.visible = not last_row
	if readable:
		_chapter.text = info.chapter_text()
		_location.text = info.location_name()
		_play_time.text = info.play_time_text()
		_stamp.text = info.timestamp_text(bias_min)
	else:
		_status.text = info.status_text()
		_status.position.y = (size.y - _status.size.y) * 0.5
		var role := &"danger" if info.status == SaveSystem.STATUS_CORRUPT else &"text_dim"
		_status.add_theme_color_override(&"font_color", _c(role))
	var name_role := &"text" if usable else &"text_disabled"
	_name.add_theme_color_override(&"font_color", _c(name_role))
	_name.position.y = _n("line1_y") if readable else (size.y - _name.size.y) * 0.5


func text_of(part: StringName) -> String:
	var l := get(StringName("_" + String(part))) as Label
	return l.text if l != null and l.visible else ""


func _gui_input(event: InputEvent) -> void:
	var mb := event as InputEventMouseButton
	if mb != null and mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
		clicked.emit()


func _label(variation: StringName, r: Rect2, align: HorizontalAlignment) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.position = r.position
	l.size = r.size
	l.horizontal_alignment = align
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	l.clip_text = true
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l


func _n(key: String) -> float:
	return HudLayout.num(_m, key)


func _c(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)
