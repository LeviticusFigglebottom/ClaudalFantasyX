class_name StatusHelpPanel
extends Control
## The status help panel (the human's playtest FAST-TRACK, 2026-11-03): every status, how to know it and
## how to be rid of it. The list on the left (each status's glyph and name; the ones on the chosen
## fighter first, marked), the chosen status's page on the right: its glyph, name, blessing or
## affliction, what it does, how long it lasts, whether it outlasts the battle, and every item, ability,
## rest or way that removes it (StatusHelpModel). Opened by the status help key from the battle
## command menu and the Read panel (BattleHud.open_status_help), and from the field Status page.
## Modal: while it is open BattleHud.holds_battle() is true, so it costs no battle time. A view only.

signal closed

const MODAL_ACTIONS: Array[StringName] = [&"ui_accept", &"ui_cancel", &"ui_up", &"ui_down", &"ui_left", &"ui_right"]
const ACTION := &"status_help"

var model: StatusHelpModel
var motion_scale := 1.0
## The statuses in list order and the one shown.
var order: Array[StringName] = []
var current := 0
## The statuses on the fighter the panel was opened for (marked "On <name> now").
var present: Array[StringName] = []
var bearer_name := ""

var _m: Dictionary = {}
var _panel: PanelContainer
var _list: VBoxContainer
var _rows: Array[Control] = []
var _glyph: StatusGlyph
var _name: Label
var _kind: Label
var _on: Label
var _desc: Label
var _lines: VBoxContainer
var _hint: Label


func _init(with_model: StatusHelpModel = null) -> void:
	model = with_model


func _ready() -> void:
	if model == null:
		model = StatusHelpModel.from_game()
	_m = StatusHelpModel.load_data().get("panel", {}) as Dictionary
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	gui_input.connect(_on_click)
	_panel = PanelContainer.new()
	HudLayout.place_rect(_panel, HudLayout.rect_of(_m), Vector2(0.5, 0.5))
	_panel.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(_panel)
	var margin := MarginContainer.new()
	for side: StringName in [&"margin_left", &"margin_right", &"margin_top", &"margin_bottom"]:
		margin.add_theme_constant_override(side, int(HudLayout.num(_m, "pad")))
	_panel.add_child(margin)
	var outer := VBoxContainer.new()
	outer.add_theme_constant_override(&"separation", int(HudLayout.num(_m, "detail_gap")))
	margin.add_child(outer)
	var title := _label(outer, &"TitleLabel", tr("STATUS_HELP_TITLE"))
	title.custom_minimum_size.y = HudLayout.num(_m, "title_height")
	var body := HBoxContainer.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_theme_constant_override(&"separation", int(HudLayout.num(_m, "detail_gap")) * 2)
	outer.add_child(body)
	_list = VBoxContainer.new()
	_list.custom_minimum_size.x = HudLayout.num(_m, "list_width")
	_list.add_theme_constant_override(&"separation", 0)
	body.add_child(_list)
	var page := VBoxContainer.new()
	page.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	page.add_theme_constant_override(&"separation", int(HudLayout.num(_m, "line_gap")))
	body.add_child(page)
	var head := HBoxContainer.new()
	head.add_theme_constant_override(&"separation", int(HudLayout.num(_m, "detail_gap")))
	page.add_child(head)
	_glyph = StatusGlyph.new()
	var gp := HudLayout.num(_m, "detail_glyph_px")
	_glyph.custom_minimum_size = Vector2(gp, gp)
	head.add_child(_glyph)
	var names := VBoxContainer.new()
	names.alignment = BoxContainer.ALIGNMENT_CENTER
	head.add_child(names)
	_name = _label(names, &"HeaderLabel", "")
	_kind = _label(names, &"DimLabel", "")
	_on = _label(page, &"HelpLabel", "")
	_desc = _label(page, &"BodyLabel", "", true)
	_lines = VBoxContainer.new()
	_lines.add_theme_constant_override(&"separation", int(HudLayout.num(_m, "line_gap")))
	page.add_child(_lines)
	_hint = _label(outer, &"HelpDimLabel", tr("STATUS_HELP_HINT"))
	_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_hint.custom_minimum_size.y = HudLayout.num(_m, "help_height")
	UiFrame.centre(self)
	visible = false


## Opens on `focus` (or the first of `on_bearer`), with `on_bearer` listed first and marked as on
## `who`. `animate` plays the short open (off in captures and under reduced motion).
func open(on_bearer: Array[StringName] = [], who: String = "", focus: StringName = &"", animate: bool = true) -> void:
	if _list == null:
		return
	present = on_bearer.duplicate()
	bearer_name = who
	order = model.ordered(present)
	_build_rows()
	var at := order.find(focus) if focus != &"" else -1
	current = maxi(at, 0)
	visible = true
	_show_current()
	if animate and motion_scale > 0.0:
		_animate_open()


func close() -> void:
	if not visible:
		return
	visible = false
	closed.emit()


func is_open() -> bool:
	return visible


## The status whose page shows (&"" when closed or empty).
func current_status() -> StringName:
	return order[current] if current >= 0 and current < order.size() else &""


## Moves the choice by `step` (wrapping). Returns true when it moved.
func move(step: int) -> bool:
	if order.size() < 2:
		return false
	current = posmod(current + step, order.size())
	_show_current()
	return true


## Every string on the page (tests).
func shown_text() -> PackedStringArray:
	var out := PackedStringArray([_name.text, _kind.text, _on.text, _desc.text])
	for c in _lines.get_children():
		out.append((c as Label).text)
	out.append(_hint.text)
	return out


func handle_input(event: InputEvent) -> bool:
	if not visible:
		return false
	if event.is_action_pressed(&"ui_up", true) or event.is_action_pressed(&"ui_left", true):
		move(-1)
		return true
	if event.is_action_pressed(&"ui_down", true) or event.is_action_pressed(&"ui_right", true):
		move(1)
		return true
	if (
		event.is_action_pressed(&"ui_accept")
		or event.is_action_pressed(&"ui_cancel")
		or (InputMap.has_action(ACTION) and event.is_action_pressed(ACTION))
	):
		close()
		return true
	for action in MODAL_ACTIONS:
		if event.is_action(action):
			return true
	return false


func _unhandled_input(event: InputEvent) -> void:
	if handle_input(event):
		get_viewport().set_input_as_handled()


func _build_rows() -> void:
	for r in _rows:
		_list.remove_child(r)
		r.queue_free()
	_rows.clear()
	var pitch := HudLayout.num(_m, "row_pitch")
	var gp := HudLayout.num(_m, "glyph_px")
	for i in order.size():
		var sid := order[i]
		var row := HBoxContainer.new()
		row.custom_minimum_size.y = pitch
		row.add_theme_constant_override(&"separation", int(HudLayout.num(_m, "row_gap")))
		row.mouse_filter = Control.MOUSE_FILTER_STOP
		row.gui_input.connect(_on_row_input.bind(i))
		var g := StatusGlyph.new(sid)
		g.custom_minimum_size = Vector2(gp, gp)
		g.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		row.add_child(g)
		var l := _label(row, &"SmallLabel", model.name_of(sid))
		l.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_list.add_child(row)
		_rows.append(row)


func _show_current() -> void:
	var sid := current_status()
	for i in _rows.size():
		var l := _rows[i].get_child(1) as Label
		var role := &"focus_gold" if i == current else (&"text" if present.has(order[i]) else &"text_dim")
		l.add_theme_color_override(&"font_color", get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE))
	if sid == &"":
		return
	_glyph.set_status(sid)
	_name.text = model.name_of(sid)
	_kind.text = model.kind_of(sid)
	_on.text = tr("STATUS_HELP_ON_FMT").format({"name": bearer_name}) if present.has(sid) and bearer_name != "" else ""
	_on.visible = _on.text != ""
	_desc.text = model.desc_of(sid)
	for c in _lines.get_children():
		_lines.remove_child(c)
		c.queue_free()
	for line in model.removal_lines(sid):
		_label(_lines, &"HelpDimLabel", line, true)


func _on_row_input(event: InputEvent, index: int) -> void:
	var mb := event as InputEventMouseButton
	if mb != null and mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
		current = index
		_show_current()
		accept_event()


## A click outside the panel closes it (a click inside it is the panel's).
func _on_click(event: InputEvent) -> void:
	var mb := event as InputEventMouseButton
	if mb != null and mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
		if not _panel.get_global_rect().has_point(mb.global_position):
			close()


func _label(parent: Control, variation: StringName, text: String, wrap: bool = false) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.text = text
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if wrap:
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size.x = 1.0
	parent.add_child(l)
	return l


func _animate_open() -> void:
	if not is_inside_tree():
		return
	var dur := HudLayout.num(_m, "open_sec")
	_panel.modulate.a = 0.0
	create_tween().tween_property(_panel, "modulate:a", 1.0, dur)
