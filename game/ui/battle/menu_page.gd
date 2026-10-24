class_name MenuPage
extends Control
## One panel of the CommandMenu: a header tab, up to `max_rows` rows at a fixed pitch, a right
## column for costs (MP in dim text, then rank: R3 and up in the swell color), and the cursor
## (the theme's "cursor" style: a lamplit raised fill, a 2 px gold frame and a focus wick; plus
## the lamp mote). ADR 0033: a titled page draws an OrnamentRule under its header, and the row
## under the cursor nudges its text right by the theme's cursor_nudge_px.
## Rows are Dictionaries: {id, label, right, right_role, mp, enabled, skill}.

signal row_hovered(index: int)
signal row_clicked(index: int)

var page_id: StringName = &""
## Reduced motion (UiSettings): the cursor jumps instead of sliding and the mote does not breathe.
var reduced_motion := false
var rows: Array[Dictionary] = []
var cursor := 0

var _m: Dictionary = {}
var _content: Control
var _header: Label
var _row_nodes: Array[Control] = []
var _cursor_box: Panel
var _mote: LampMote
var _first := 0
var _cursor_tween: Tween
var _header_h := 0.0
var _rule: OrnamentRule
var _nudge_tweens: Dictionary = {}


## Height a page needs for `row_count` rows (header, rows, and a half-row of breathing room).
static func height_for(metrics: Dictionary, row_count: int, titled: bool = true) -> float:
	var shown := mini(row_count, int(HudLayout.num(metrics, "max_rows")))
	var header := HudLayout.num(metrics, "header_height") if titled else 0.0
	return header + HudLayout.num(metrics, "row_inset") * 2.0 + shown * HudLayout.num(metrics, "row_pitch")


func setup(metrics: Dictionary, pid: StringName, title: String, page_rows: Array[Dictionary]) -> void:
	_m = metrics
	page_id = pid
	rows = page_rows
	_header_h = HudLayout.num(_m, "header_height") if title != "" else 0.0
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var bg := Panel.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
	_content = Control.new()
	_content.set_anchors_preset(Control.PRESET_FULL_RECT)
	_content.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_content)
	_header = Label.new()
	_header.theme_type_variation = &"HeaderLabel"
	_header.text = title
	_header.visible = title != ""
	_header.position = Vector2(HudLayout.num(_m, "text_indent"), 0.0)
	_header.size = Vector2(size.x - HudLayout.num(_m, "text_indent") * 2.0, HudLayout.num(_m, "header_height"))
	_header.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
	_header.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_content.add_child(_header)
	if title != "":
		_rule = OrnamentRule.new()
		var indent := HudLayout.num(_m, "text_indent")
		var node := float(get_theme_constant(&"ornament_node_px", HymnThemeBuilder.PALETTE_TYPE))
		_rule.position = Vector2(indent - node, _header_h + 2.0 - node)
		_rule.size = Vector2(size.x - indent * 2.0 + node, node * 2.0)
		_content.add_child(_rule)
	_cursor_box = Panel.new()
	_cursor_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_cursor_box.add_theme_stylebox_override(&"panel", _cursor_style())
	_content.add_child(_cursor_box)
	_mote = LampMote.new()
	_mote.period_sec = HudLayout.num(_m, "breath_sec")
	_mote.alpha_min = HudLayout.num(_m, "breath_min")
	_mote.breathing = not reduced_motion
	var mp := HudLayout.num(_m, "mote_px")
	_mote.size = Vector2(mp, mp)
	_content.add_child(_mote)
	_build_rows()
	cursor = first_enabled(0, 1)
	_place_cursor(false)


## Replaces the rows in place, keeping the cursor on the same index when it is still enabled.
func replace_rows(page_rows: Array[Dictionary]) -> void:
	rows = page_rows
	_first = 0
	_build_rows()
	# A page set up empty hid its cursor (_place_cursor): show it again for the new rows.
	_cursor_box.visible = not rows.is_empty()
	_mote.visible = not rows.is_empty() and is_equal_approx(_content.modulate.a, 1.0)
	var keep := cursor < rows.size() and bool(rows[cursor].get("enabled", true))
	cursor = cursor if keep else first_enabled(0, 1)
	_scroll_to_cursor()
	_place_cursor(false)


## Changes the header text. A page set up untitled has no header row to show it in.
func set_header(title: String) -> void:
	_header.text = title


## The header Label (pages that need a long title to ellipsize in its rect, M2-MNU-05).
func header_label() -> Label:
	return _header


func row_count() -> int:
	return rows.size()


func current_row() -> Dictionary:
	return rows[cursor] if cursor >= 0 and cursor < rows.size() else {}


## Moves the cursor by `delta` rows, skipping disabled ones and wrapping. Returns true if it moved.
func move(delta: int) -> bool:
	if rows.is_empty():
		return false
	var start := cursor
	var i := cursor
	for _n in rows.size():
		i = posmod(i + delta, rows.size())
		if bool(rows[i].get("enabled", true)):
			break
	if i == start or not bool(rows[i].get("enabled", true)):
		return false
	cursor = i
	_scroll_to_cursor()
	_place_cursor(true)
	return true


func set_cursor(index: int, animate: bool = true) -> void:
	if index < 0 or index >= rows.size() or not bool(rows[index].get("enabled", true)):
		return
	cursor = index
	_scroll_to_cursor()
	_place_cursor(animate)


func first_enabled(from: int, step: int) -> int:
	for n in rows.size():
		var i := posmod(from + n * step, rows.size())
		if bool(rows[i].get("enabled", true)):
			return i
	return 0


## A page under a pushed sub-menu: its text dims, its frame stays, and the cursor stays put so
## the path you took is still readable.
func set_dimmed(dim: bool) -> void:
	_content.modulate.a = HudLayout.num(_m, "submenu_dim") if dim else 1.0
	_mote.visible = not dim


## The Control of row `index` (null when out of range); input parity tests hover and click it.
func row_node(index: int) -> Control:
	return _row_nodes[index] if index >= 0 and index < _row_nodes.size() else null


func row_rect(index: int) -> Rect2:
	var inset := HudLayout.num(_m, "row_inset")
	var pitch := HudLayout.num(_m, "row_pitch")
	var y := _header_h + inset + (index - _first) * pitch
	return Rect2(inset, y, size.x - inset * 2.0, pitch)


func _build_rows() -> void:
	for n in _row_nodes:
		n.queue_free()
	_row_nodes.clear()
	var visible_rows := mini(rows.size(), int(HudLayout.num(_m, "max_rows")))
	for i in rows.size():
		var node := _build_row(rows[i], row_rect(i))
		node.visible = i < visible_rows
		node.mouse_entered.connect(_on_row_mouse.bind(i))
		node.gui_input.connect(_on_row_input.bind(i))
		_content.add_child(node)
		_row_nodes.append(node)


func _build_row(row: Dictionary, r: Rect2) -> Control:
	var node := Control.new()
	node.mouse_filter = Control.MOUSE_FILTER_STOP
	node.position = r.position
	node.size = r.size
	var indent := HudLayout.num(_m, "text_indent") - HudLayout.num(_m, "row_inset")
	var cost_w := HudLayout.num(_m, "cost_width")
	var enabled := bool(row.get("enabled", true))
	var off := _c(&"text_disabled")
	var label := _cell(
		str(row.get("label", "")), &"MenuLabel", Rect2(indent, 0.0, r.size.x - indent - cost_w, r.size.y)
	)
	label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	node.add_child(label)
	var mp_text := str(row.get("mp", ""))
	var rank_w := HudLayout.num(_m, "rank_width") if mp_text != "" else r.size.x - indent * 1.5
	var right := _cell(
		str(row.get("right", "")), &"RankLabel", Rect2(r.size.x - rank_w - indent * 0.5, 0.0, rank_w, r.size.y)
	)
	right.add_theme_color_override(&"font_color", _c(StringName(str(row.get("right_role", "text_dim")))))
	node.add_child(right)
	if mp_text != "":
		var mp := _cell(mp_text, &"RankLabel", Rect2(r.size.x - cost_w - indent * 0.5, 0.0, cost_w - rank_w, r.size.y))
		mp.add_theme_color_override(&"font_color", _c(&"text_dim"))
		node.add_child(mp)
		if not enabled:
			mp.add_theme_color_override(&"font_color", off)
	if not enabled:
		label.add_theme_color_override(&"font_color", off)
		right.add_theme_color_override(&"font_color", off)
	return node


func _cell(text: String, variation: StringName, r: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.text = text
	l.position = r.position
	l.size = r.size
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


func _scroll_to_cursor() -> void:
	var max_rows := int(HudLayout.num(_m, "max_rows"))
	if rows.size() <= max_rows:
		return
	var first := clampi(_first, cursor - max_rows + 1, cursor)
	if first == _first:
		return
	_first = first
	for i in _row_nodes.size():
		_row_nodes[i].position = row_rect(i).position
		_row_nodes[i].visible = i >= _first and i < _first + max_rows


func _place_cursor(animate: bool) -> void:
	if rows.is_empty():
		_cursor_box.visible = false
		_mote.visible = false
		return
	if _cursor_tween != null and _cursor_tween.is_valid():
		_cursor_tween.kill()
	_nudge_rows(animate)
	var r := row_rect(cursor)
	var mp := HudLayout.num(_m, "mote_px")
	var label_x := HudLayout.num(_m, "text_indent")
	var mote_pos := Vector2(label_x - HudLayout.num(_m, "mote_offset") - mp * 0.5, r.get_center().y - mp * 0.5)
	if not animate or reduced_motion or not is_inside_tree():
		_cursor_box.position = r.position
		_cursor_box.size = r.size
		_mote.position = mote_pos
		return
	var dur := HudLayout.num(_m, "cursor_sec")
	_cursor_tween = create_tween().set_parallel(true)
	var tw := _cursor_tween
	tw.tween_property(_cursor_box, "position", r.position, dur).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_property(_cursor_box, "size", r.size, dur).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_property(_mote, "position", mote_pos, dur).set_delay(HudLayout.num(_m, "mote_lag_sec"))


## The theme's cursor style (CursorStyleBox, ADR 0033).
func _cursor_style() -> StyleBox:
	return get_theme_stylebox(&"cursor", HymnThemeBuilder.PALETTE_TYPE)


func _c(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


func _on_row_mouse(index: int) -> void:
	if index != cursor and bool(rows[index].get("enabled", true)):
		set_cursor(index)
		row_hovered.emit(index)


func _on_row_input(event: InputEvent, index: int) -> void:
	var mb := event as InputEventMouseButton
	if mb == null or not mb.pressed:
		return
	if mb.button_index == MOUSE_BUTTON_LEFT:
		row_clicked.emit(index)
	elif mb.button_index == MOUSE_BUTTON_WHEEL_UP or mb.button_index == MOUSE_BUTTON_WHEEL_DOWN:
		# The wheel steps the cursor (M2-UI-26) and reports it like a hover, so every screen that
		# follows hover follows the wheel too.
		if move(-1 if mb.button_index == MOUSE_BUTTON_WHEEL_UP else 1):
			row_hovered.emit(cursor)
		accept_event()


## The row under the cursor shifts its text right by cursor_nudge_px; the others sit at rest. It
## slides with the cursor (cursor_sec) unless motion is reduced or the page is not shown yet.
func _nudge_rows(animate: bool) -> void:
	var nudge := float(get_theme_constant(&"cursor_nudge_px", HymnThemeBuilder.PALETTE_TYPE))
	var base := HudLayout.num(_m, "text_indent") - HudLayout.num(_m, "row_inset")
	for i in _row_nodes.size():
		var node := _row_nodes[i]
		if node.get_child_count() == 0 or node.is_queued_for_deletion():
			continue
		var label := node.get_child(0) as Control
		var x := base + (nudge if i == cursor else 0.0)
		var old_tw: Tween = _nudge_tweens.get(i)
		if old_tw != null and old_tw.is_valid():
			old_tw.kill()
		if animate and not reduced_motion and is_inside_tree() and not is_equal_approx(label.position.x, x):
			var tw := create_tween()
			tw.tween_property(label, "position:x", x, HudLayout.num(_m, "cursor_sec"))
			_nudge_tweens[i] = tw
		else:
			label.position.x = x


## The x of row `index`'s label (tests: the cursor row is nudged).
func label_x(index: int) -> float:
	var node := _row_nodes[index] if index >= 0 and index < _row_nodes.size() else null
	return (node.get_child(0) as Control).position.x if node != null and node.get_child_count() > 0 else 0.0
