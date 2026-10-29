class_name BattleResultPanel
extends Control
## Victory / defeat / escape screen: a scrim, a tide-notch panel with the outcome title and
## one row per fighter (XP and Lattice movement points gained), the spoils (lume, drops), and a small
## choice menu. The rows arrive in turn, and each number a row names in "count" ({cell, key, arg, n};
## BattleRewards) counts up from 0 to n, eased, as its row arrives (panel_open "count_sec"). Confirm
## while it counts shows every number at once instead of choosing; Reduced motion shows them at once.

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
var _open_tween: Tween
## The counting cells: [{label: Label, key, arg, n}].
var _counters: Array[Dictionary] = []


## act1_gpu_qa row 33: a panel freed mid count-up (the result left at once) ends its count now. A bound tween only
## notices its freed node on the tree's next step, and would step into freed rows until then.
func _notification(what: int) -> void:
	if what == NOTIFICATION_PREDELETE and _open_tween != null and _open_tween.is_valid():
		_open_tween.kill()
		_counters.clear()


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
	# A result shown again while the last open still counts (act1_gpu_qa row 33): that tween would write into
	# the rows freed below.
	if _open_tween != null and _open_tween.is_valid():
		_open_tween.kill()
	for ch in _list.get_children():
		_list.remove_child(ch)
		ch.queue_free()
	_counters.clear()
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
		if is_counting():
			finish_open()  # the first Confirm shows every number; the next one chooses
		else:
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
	h.add_theme_constant_override(&"separation", int(HudLayout.num(_m, "picture_gap")))
	h.add_child(_picture(r))
	var label := _cell(str(r.get("label", "")), &"HudName", HORIZONTAL_ALIGNMENT_LEFT)
	h.add_child(label)
	var xp := _cell(str(r.get("xp_text", "")), &"HudNumber", HORIZONTAL_ALIGNMENT_RIGHT)
	h.add_child(xp)
	var moves := _cell(str(r.get("moves_text", "")), &"HudNumber", HORIZONTAL_ALIGNMENT_RIGHT)
	for c: Variant in r.get("count", []):
		var spec := c as Dictionary
		var cell := moves if str(spec.get("cell", "")) == "moves" else xp
		_counters.append({"label": cell, "key": str(spec["key"]), "arg": str(spec["arg"]), "n": int(spec["n"])})
	var role := &"text_dim" if bool(r.get("fell", false)) else &"swell"
	moves.add_theme_color_override(&"font_color", get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE))
	if bool(r.get("fell", false)):
		label.add_theme_color_override(&"font_color", get_theme_color(&"text_dim", HymnThemeBuilder.PALETTE_TYPE))
	h.add_child(moves)
	return h


## The row's picture: a fighter's face (worried when they fell) or a drop's icon; an empty cell of the same
## width otherwise (the lume), so every name starts in one column.
func _picture(r: Dictionary) -> Control:
	var px := HudLayout.num(_m, "picture_px")
	var holder := Control.new()
	holder.custom_minimum_size = Vector2(px, px)
	holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var fighter := StringName(str(r.get("fighter", "")))
	var tex := BattlePortraits.texture(fighter, bool(r.get("fell", false))) if fighter != &"" else null
	if tex != null:
		var face := TextureRect.new()
		face.texture = tex
		face.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		face.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		face.size = Vector2(px, px)
		face.mouse_filter = Control.MOUSE_FILTER_IGNORE
		holder.add_child(face)
	elif r.has("glyph"):
		var g := MenuGlyph.for_row(r["glyph"] as Dictionary, 0.0, px)
		if g != null:
			g.position.y = 0.0
			g.size = Vector2(px, px)
			holder.add_child(g)
	return holder


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
	if UiSettings.shared().reduced_motion():
		return
	# The "parts look primitive" pass: each fighter's row arrives in turn, then the choices (panel_open).
	var row_sec := HudLayout.num(_open_m, "row_sec")
	var at := HudLayout.num(_open_m, "rows_delay_sec")
	for row in _list.get_children():
		var c := row as CanvasItem
		c.modulate.a = 0.0
		tw.tween_property(c, "modulate:a", 1.0, row_sec).set_delay(at)
		at += HudLayout.num(_open_m, "row_stagger_sec")
	var rows := _list.get_children()
	for c in _counters:
		var cell := c["label"] as Label
		var row_at := (
			HudLayout.num(_open_m, "rows_delay_sec")
			+ rows.find(cell.get_parent()) * HudLayout.num(_open_m, "row_stagger_sec")
		)
		cell.text = _count_text(c, 0)
		var count := tw.tween_method(_set_count.bind(c), 0.0, float(int(c["n"])), HudLayout.num(_open_m, "count_sec"))
		count.set_delay(row_at).set_trans(Tween.TRANS_QUAD)
	if _choices != null:
		_choices.modulate.a = 0.0
		tw.tween_property(_choices, "modulate:a", 1.0, row_sec).set_delay(at)
	_open_tween = tw


## The whole open's length (the panel, then the rows in turn and their numbers counting, then the choices).
func open_duration() -> float:
	var rows := _list.get_child_count()
	var stagger := HudLayout.num(_open_m, "rows_delay_sec") + rows * HudLayout.num(_open_m, "row_stagger_sec")
	var tail := HudLayout.num(_open_m, "row_sec")
	if not _counters.is_empty():
		tail = maxf(tail, HudLayout.num(_open_m, "count_sec"))
	return maxf(HudLayout.num(_open_m, "sec"), stagger + tail)


## True while numbers are still counting up (a defeat or escape has none to count).
func is_counting() -> bool:
	if _counters.is_empty() or _open_tween == null or not _open_tween.is_valid() or not _open_tween.is_running():
		return false
	for c in _counters:
		if is_instance_valid(c["label"]) and (c["label"] as Label).text != _count_text(c, int(c["n"])):
			return true
	return false


func _set_count(value: float, c: Dictionary) -> void:
	if not is_instance_valid(c["label"]):  # the row went with the panel (a result left quickly; row 33)
		return
	(c["label"] as Label).text = _count_text(c, roundi(value))


func _count_text(c: Dictionary, value: int) -> String:
	return tr(str(c["key"])).format({str(c["arg"]): value})


## Ends the open at rest now (tests).
func finish_open() -> void:
	if _open_tween != null and _open_tween.is_valid() and _open_tween.is_running():
		_open_tween.custom_step(open_duration() + 1.0)
