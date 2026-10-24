class_name BattleResultPanel
extends Control
## Victory / defeat / escape screen: a scrim, a tide-notch panel with the outcome title and
## one row per fighter (XP and Lattice movement points gained), and a small choice menu.

signal choice_made(choice_id: StringName)

const SCRIM_SHADER := preload("res://game/ui/shaders/scrim.gdshader")

var outcome: StringName = &""
var result_rows: Array[Dictionary] = []
## Scales the open animation's rise (UiSettings.motion_scale(); halved under reduced motion).
var motion_scale := 1.0

var _m: Dictionary = {}
var _open_m: Dictionary = {}
var _scrim: ColorRect
var _panel: PanelContainer
var _title: Label
var _subtitle: Label
var _list: VBoxContainer
var _choices: MenuPage


func _ready() -> void:
	_m = HudLayout.section(&"result")
	_open_m = HudLayout.section(&"panel_open")
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_scrim = ColorRect.new()
	_scrim.set_anchors_preset(Control.PRESET_FULL_RECT)
	_scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := ShaderMaterial.new()
	mat.shader = SCRIM_SHADER
	mat.set_shader_parameter(&"tint", get_theme_color(&"scrim", HymnThemeBuilder.PALETTE_TYPE))
	_scrim.material = mat
	add_child(_scrim)
	_panel = PanelContainer.new()
	HudLayout.place(_panel, _m)
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_panel)
	var margin := MarginContainer.new()
	for side: StringName in [&"margin_left", &"margin_right", &"margin_top", &"margin_bottom"]:
		margin.add_theme_constant_override(side, int(HudLayout.num(_m, "pad")))
	_panel.add_child(margin)
	var v := VBoxContainer.new()
	v.alignment = BoxContainer.ALIGNMENT_CENTER
	margin.add_child(v)
	_title = Label.new()
	_title.theme_type_variation = &"TitleLabel"
	_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(_title)
	_subtitle = Label.new()
	_subtitle.theme_type_variation = &"FlavorLabel"
	_subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_subtitle.add_theme_color_override(&"font_color", get_theme_color(&"text_dim", HymnThemeBuilder.PALETTE_TYPE))
	v.add_child(_subtitle)
	var sep := HSeparator.new()
	v.add_child(sep)
	_list = VBoxContainer.new()
	v.add_child(_list)
	UiFrame.centre(self)  # the panel and its choices centred at any aspect, the scrim full screen
	visible = false


## rows: [{label, xp, moves}]; choices: CommandMenu-style rows ({id, label, enabled}).
func show_result(
	result: StringName, title: String, subtitle: String, rows: Array[Dictionary], choices: Array[Dictionary]
) -> void:
	outcome = result
	result_rows = rows
	_title.text = title
	_subtitle.text = subtitle
	_subtitle.visible = subtitle != ""
	for ch in _list.get_children():
		_list.remove_child(ch)
		ch.queue_free()
	for r in rows:
		_list.add_child(_row(r))
	if _choices != null:
		_choices.queue_free()
	_choices = MenuPage.new()
	var cm := HudLayout.section(&"commands")
	var area := HudLayout.rect_of(_m)
	var gap := HudLayout.num(_m, "gap")
	var choice_h := MenuPage.height_for(cm, choices.size(), false)
	var choice_w := HudLayout.rect_of(cm).size.x
	var panel_h := _panel.get_combined_minimum_size().y
	var top := area.get_center().y - (panel_h + gap + choice_h) * 0.5
	_panel.position = Vector2(area.position.x, top)
	_panel.size = Vector2(area.size.x, panel_h)
	_choices.position = Vector2(area.get_center().x - choice_w * 0.5, top + panel_h + gap)
	_choices.size = Vector2(choice_w, choice_h)
	add_child(_choices)
	_choices.setup(cm, &"result", "", choices)
	_choices.row_clicked.connect(func(i: int) -> void: _choose(i))
	visible = true
	_animate_open()


func move_cursor(delta: int) -> void:
	if _choices != null:
		_choices.move(delta)


func accept() -> void:
	if _choices != null and visible:
		_choose(_choices.cursor)


func current_choice() -> StringName:
	return StringName(str(_choices.current_row().get("id", ""))) if _choices != null else &""


func handle_input(event: InputEvent) -> bool:
	if not visible:
		return false
	if event.is_action_pressed(&"ui_up", true):
		move_cursor(-1)
	elif event.is_action_pressed(&"ui_down", true):
		move_cursor(1)
	elif event.is_action_pressed(&"ui_accept"):
		accept()
	else:
		return false
	return true


func _choose(index: int) -> void:
	_choices.set_cursor(index, false)
	choice_made.emit(current_choice())


func _row(r: Dictionary) -> Control:
	var h := HBoxContainer.new()
	h.custom_minimum_size = Vector2(0.0, HudLayout.num(_m, "row_height"))
	h.alignment = BoxContainer.ALIGNMENT_CENTER
	var label := _cell(str(r.get("label", "")), &"HudName", HORIZONTAL_ALIGNMENT_LEFT)
	h.add_child(label)
	h.add_child(_cell(str(r.get("xp_text", "")), &"HudNumber", HORIZONTAL_ALIGNMENT_RIGHT))
	var moves := _cell(str(r.get("moves_text", "")), &"HudNumber", HORIZONTAL_ALIGNMENT_RIGHT)
	var role := &"text_dim" if bool(r.get("fell", false)) else &"swell"
	moves.add_theme_color_override(&"font_color", get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE))
	if bool(r.get("fell", false)):
		label.add_theme_color_override(&"font_color", get_theme_color(&"text_dim", HymnThemeBuilder.PALETTE_TYPE))
	h.add_child(moves)
	return h


func _cell(text: String, variation: StringName, align: HorizontalAlignment) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.text = text
	l.horizontal_alignment = align
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return l


func _animate_open() -> void:
	if not is_inside_tree():
		return
	var dur := HudLayout.num(_open_m, "sec")
	var rise := HudLayout.num(_open_m, "rise_px") * motion_scale
	var from := HudLayout.num(_open_m, "scale_from")
	_panel.pivot_offset = _panel.size * 0.5
	_panel.scale = Vector2(from, from)
	_panel.modulate.a = 0.0
	var y := _panel.position.y
	_panel.position.y = y + rise
	var tw := create_tween().set_parallel(true).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	tw.tween_property(_panel, "scale", Vector2.ONE, dur)
	tw.tween_property(_panel, "modulate:a", 1.0, dur)
	tw.tween_property(_panel, "position:y", y, dur)
	_scrim.modulate.a = 0.0
	tw.tween_property(_scrim, "modulate:a", 1.0, dur)
