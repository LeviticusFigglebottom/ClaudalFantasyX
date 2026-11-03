class_name StatusTipCard
extends Control
## The first time a status lands on the party (the human's playtest FAST-TRACK, 2026-11-03): a card over
## the battle with the status's glyph, "<Status> has taken hold of <hero>" (a blessing: "<hero> is under
## <Status>"), what it does and every way it ends (StatusHelpModel.body). BattleStatusTips raises it once
## per status per save, when the party's next command opens, and holds the battle while it shows.
## Confirm or Cancel closes it; the status help key opens StatusHelpPanel on that status. A view only.

signal closed(open_help: bool)

const MODAL_ACTIONS: Array[StringName] = [&"ui_accept", &"ui_cancel", &"ui_up", &"ui_down", &"ui_left", &"ui_right"]

var model: StatusHelpModel
var status: StringName = &""
var motion_scale := 1.0

var _m: Dictionary = {}
var _panel: PanelContainer
var _glyph: StatusGlyph
var _title: Label
var _body: Label
var _hint: Label


func _init(with_model: StatusHelpModel = null) -> void:
	model = with_model


func _ready() -> void:
	if model == null:
		model = StatusHelpModel.shared()
	_m = StatusHelpModel.load_data().get("tip", {}) as Dictionary
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	gui_input.connect(_on_click)
	_panel = PanelContainer.new()
	HudLayout.place_rect(_panel, HudLayout.rect_of(_m), Vector2(0.5, 0.5))
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_panel)
	var margin := MarginContainer.new()
	margin.mouse_filter = Control.MOUSE_FILTER_IGNORE
	for side: StringName in [&"margin_left", &"margin_right", &"margin_top", &"margin_bottom"]:
		margin.add_theme_constant_override(side, int(HudLayout.num(_m, "pad")))
	_panel.add_child(margin)
	var row := HBoxContainer.new()
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override(&"separation", int(HudLayout.num(_m, "gap")))
	margin.add_child(row)
	_glyph = StatusGlyph.new()
	var gp := HudLayout.num(_m, "glyph_px")
	_glyph.custom_minimum_size = Vector2(gp, gp)
	_glyph.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	row.add_child(_glyph)
	var v := VBoxContainer.new()
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.add_theme_constant_override(&"separation", int(HudLayout.num(_m, "line_gap")))
	row.add_child(v)
	_title = _label(v, &"HeaderLabel", true)
	_body = _label(v, &"BodyLabel", true)
	# Wrapping text is measured at the column's width: at 1 px the card would grow off the screen.
	var text_w := HudLayout.rect_of(_m).size.x - HudLayout.num(_m, "pad") * 2.0 - gp - HudLayout.num(_m, "gap")
	_title.custom_minimum_size.x = text_w
	_body.custom_minimum_size.x = text_w
	_hint = _label(v, &"HelpDimLabel", false)
	_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	UiFrame.centre(self)
	visible = false


## Shows `sid` as it lands on `hero` (a display name).
func show_tip(sid: StringName, hero: String) -> void:
	if _panel == null:
		return
	status = sid
	_glyph.set_status(sid)
	var key := "STATUS_TIP_BUFF_TITLE_FMT" if model.is_buff(sid) else "STATUS_TIP_TITLE_FMT"
	_title.text = tr(key).format({"name": model.name_of(sid), "hero": hero})
	_body.text = model.body(sid)
	_hint.text = tr("STATUS_TIP_HINT_FMT").format({"key": InputNames.first_name(StatusHelpPanel.ACTION)})
	_fit()
	visible = true
	_fit.call_deferred()  # again once the wrapped labels have measured their new text
	if motion_scale > 0.0 and is_inside_tree():
		_panel.modulate.a = 0.0
		create_tween().tween_property(_panel, "modulate:a", 1.0, HudLayout.num(_m, "open_sec"))


## Shrinks the card to its text (a Control grows to its minimum size but never shrinks back by itself).
func _fit() -> void:
	if _panel != null:
		_panel.reset_size()


func close(open_help: bool = false) -> void:
	if not visible:
		return
	visible = false
	closed.emit(open_help)


func is_open() -> bool:
	return visible


func shown_text() -> PackedStringArray:
	return PackedStringArray([_title.text, _body.text, _hint.text])


func handle_input(event: InputEvent) -> bool:
	if not visible:
		return false
	if InputMap.has_action(StatusHelpPanel.ACTION) and event.is_action_pressed(StatusHelpPanel.ACTION):
		close(true)
		return true
	if event.is_action_pressed(&"ui_accept") or event.is_action_pressed(&"ui_cancel"):
		close()
		return true
	for action in MODAL_ACTIONS:
		if event.is_action(action):
			return true
	return false


func _on_click(event: InputEvent) -> void:
	var mb := event as InputEventMouseButton
	if mb != null and mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
		close()


func _label(parent: Control, variation: StringName, wrap: bool) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if wrap:
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size.x = 1.0
	parent.add_child(l)
	return l
