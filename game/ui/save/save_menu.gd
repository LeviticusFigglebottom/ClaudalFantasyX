class_name SaveMenu
extends Control
## The save/load menu (M1-ARC-03, SPEC §5.2, §6.6): a tide-notch panel listing the autosave slot
## and the manual slots (slot name, chapter, location, play time, save time), with an overwrite
## question, a result message, and a help line that explains every row (pillar 4).
## Logic lives in SaveMenuModel; this is its view plus input. Layout: game/data/ui/save_menu.json.
##
## Input (keyboard and controller through the built-in ui_* actions): ui_up / ui_down move,
## ui_accept chooses, ui_cancel backs out (ui_left / ui_right also move inside a dialog). Mouse:
## click a row or a choice.
##
## Open it with SaveMenu.open_in(host, mode) (it brings its own CanvasLayer) or instance
## save_menu.tscn, call configure(), then add it to the tree. While open it pauses the tree
## (pause_tree) and restores the previous pause state when it closes.

signal closed(outcome: SaveMenuModel.Outcome)
signal saved(slot: int)
signal loaded(slot: int)
## The close transition has finished (at once under Reduced motion): open_in's layer frees itself
## (M2-MNU-305, MenuMotion; the open keeps this menu's own panel rise, panel_open).
signal gone

const SCENE_PATH := "res://game/ui/save/save_menu.tscn"
const DATA_PATH := "res://game/data/ui/save_menu.json"
const SCRIM_SHADER := preload("res://game/ui/shaders/scrim.gdshader")
## The controls line at the right of the help row (the Lead's controller pass, 2026-10-30), by mode and phase.
const CONTROLS_KEYS := {
	SaveMenuModel.Mode.SAVE: "SAVE_CONTROLS_SAVE",
	SaveMenuModel.Mode.LOAD: "SAVE_CONTROLS_LOAD",
}
const CONTROLS_QUESTION_KEY := "SAVE_CONTROLS_QUESTION"
const CONTROLS_RESULT_KEY := "SAVE_CONTROLS_RESULT"

## Pause the tree while open (the field must not move under a menu).
@export var pause_tree := true
## Play the 180 ms open motion (captures and tests may switch it off).
@export var animate := true

var model: SaveMenuModel
## Minutes east of UTC for timestamps; captures set 0 so frames don't depend on the host.
var time_zone_bias_min := 0
## Optional loc key under the title (e.g. the shrine's "your party is restored").
var subtitle_key := ""

var _d: Dictionary = {}
var _panel: Panel
var _title: Label
var _subtitle: Label
var _help: Label
var _controls: Label
var _list: Control
var _rows: Array[SaveSlotRow] = []
var _cursor_box: Panel
var _mote: LampMote
var _cursor_tween: Tween
var _dialog: Panel
var _dialog_text: Label
var _choices: MenuPage
var _choices_phase := -1
var _scrim: ColorRect
var _dialog_scrim: ColorRect
## True when this menu paused the tree (and so must unpause it).
var _owns_pause := false
var _is_closed := false
var _motion: MenuMotion


## Instances the menu on its own CanvasLayer under `host` and opens it. The layer frees itself
## when the menu closes. Returns the menu (connect to closed / saved / loaded).
static func open_in(
	host: Node, mode: SaveMenuModel.Mode, extra_meta: Dictionary = {}, subtitle: String = "", save_system: Node = null
) -> SaveMenu:
	var menu := (load(SCENE_PATH) as PackedScene).instantiate() as SaveMenu
	menu.configure(mode, save_system, extra_meta, subtitle)
	var layer := CanvasLayer.new()
	layer.layer = int(load_data().get("canvas_layer", 1))
	layer.process_mode = Node.PROCESS_MODE_ALWAYS
	layer.add_child(menu)
	menu.gone.connect(layer.queue_free)
	host.add_child(layer)
	return menu


static func load_data() -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("save_menu")) != TYPE_DICTIONARY:
		push_error("SaveMenu: could not read 'save_menu' from %s" % DATA_PATH)
		return {}
	return (parsed as Dictionary)["save_menu"] as Dictionary


## Sets the menu up before it enters the tree. `save_system` defaults to the SaveSystem autoload.
func configure(
	mode: SaveMenuModel.Mode, save_system: Node = null, extra_meta: Dictionary = {}, subtitle: String = ""
) -> void:
	_d = load_data()
	var saves := save_system if save_system != null else _autoload(&"SaveSystem")
	model = SaveMenuModel.new(mode, saves, SaveMenuModel.default_slot_ids(int(_d.get("manual_slots", 0))))
	model.extra_meta = extra_meta
	subtitle_key = subtitle
	var tz: Dictionary = Time.get_time_zone_from_system()
	time_zone_bias_min = int(tz.get("bias", 0))


func _ready() -> void:
	if model == null:
		configure(SaveMenuModel.Mode.SAVE)
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	UiSettings.shared().follow(self)  # text size and palette, as every menu (M2-ARC-06)
	_build()
	UiFrame.centre(self)  # centred at 16:10 and 21:9, the scrim full screen (M2-UI-29, UI track)
	model.changed.connect(_render)
	model.refresh()
	model.place_initial_cursor()
	if pause_tree and not get_tree().paused:
		get_tree().paused = true
		_owns_pause = true
	MenuMotion.follow_reduced_motion(self)
	_motion = MenuMotion.new(self)
	_motion.gone.connect(gone.emit)
	_animate_open()


func _exit_tree() -> void:
	_restore_pause()


func is_open() -> bool:
	return not _is_closed and model != null and model.phase != SaveMenuModel.Phase.CLOSED


func _input(event: InputEvent) -> void:
	if not is_open():
		return
	# Taken here, before the UiInput autoload sees it: let it note the device and a held d-pad first.
	var ui := get_node_or_null(^"/root/UiInput")
	if ui != null:
		ui.call(&"notice", event)
	if handle_input(event):
		get_viewport().set_input_as_handled()


## Applies one input event. Returns true when the menu used it. Tests call this directly.
func handle_input(event: InputEvent) -> bool:
	if not is_open():
		return false
	var in_dialog := model.phase != SaveMenuModel.Phase.BROWSE
	if event.is_action_pressed(&"ui_up", true) or (in_dialog and event.is_action_pressed(&"ui_left", true)):
		model.move(-1)
	elif event.is_action_pressed(&"ui_down", true) or (in_dialog and event.is_action_pressed(&"ui_right", true)):
		model.move(1)
	elif event.is_action_pressed(&"ui_accept"):
		_after(model.accept())
	elif event.is_action_pressed(&"ui_cancel"):
		_after(model.cancel())
	else:
		return false
	return true


## Changes the time zone used for save times and redraws (captures pass 0).
func set_time_zone_bias(bias_min: int) -> void:
	time_zone_bias_min = bias_min
	_render()


## The row views (tests read their text).
func rows() -> Array[SaveSlotRow]:
	return _rows


func help_text() -> String:
	return _help.text


func dialog_text() -> String:
	return _dialog_text.text if _dialog.visible else ""


func _after(outcome: SaveMenuModel.Outcome) -> void:
	match outcome:
		SaveMenuModel.Outcome.SAVED:
			saved.emit(model.last_slot)
		SaveMenuModel.Outcome.LOADED:
			loaded.emit(model.last_slot)
			_close(outcome)
		SaveMenuModel.Outcome.CLOSED:
			_close(outcome)


func _close(outcome: SaveMenuModel.Outcome) -> void:
	if _is_closed:
		return
	_is_closed = true
	if _motion != null and animate:
		_motion.play_out()  # it never takes the pointer again while it fades (M2-UI-26)
	else:
		visible = false
		gone.emit()
	_restore_pause()
	closed.emit(outcome)


## The close transition (null before _ready). Tests drive it with motion().finish().
func motion() -> MenuMotion:
	return _motion


func _restore_pause() -> void:
	if _owns_pause and is_inside_tree():
		get_tree().paused = false
	_owns_pause = false


# --- Build ---------------------------------------------------------------------------------------


func _build() -> void:
	var p := _d.get("panel", {}) as Dictionary
	var rm := _d.get("rows", {}) as Dictionary
	_scrim = _make_scrim()
	_panel = Panel.new()
	HudLayout.place(_panel, p)
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_panel)
	var pad := HudLayout.num(p, "pad")
	var inner_w := _panel.size.x - pad * 2.0
	var y := pad
	_title = _label(&"BannerLabel", Rect2(pad, y, inner_w, HudLayout.num(p, "title_height")))
	_title.text = tr("SAVE_MENU_TITLE_SAVE") if model.mode == SaveMenuModel.Mode.SAVE else tr("SAVE_MENU_TITLE_LOAD")
	y += HudLayout.num(p, "title_height")
	_subtitle = _label(&"FlavorDimLabel", Rect2(pad, y, inner_w, HudLayout.num(p, "subtitle_height")))
	_subtitle.text = tr(subtitle_key) if subtitle_key != "" else ""
	y += HudLayout.num(p, "subtitle_height") + HudLayout.num(p, "gap")
	_list = Control.new()
	_list.position = Vector2(pad, y)
	_list.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.add_child(_list)
	_cursor_box = Panel.new()
	_cursor_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_cursor_box.add_theme_stylebox_override(&"panel", _cursor_style())
	_list.add_child(_cursor_box)
	var row_h := HudLayout.num(rm, "height")
	var pitch := HudLayout.num(rm, "pitch")
	for i in model.slot_ids.size():
		var row := SaveSlotRow.new()
		row.position = Vector2(0.0, i * pitch)
		_list.add_child(row)
		row.setup(rm, Vector2(inner_w, row_h))
		row.clicked.connect(_on_row_clicked.bind(i))
		row.hovered.connect(_on_row_hovered.bind(i))  # M2-UI-26: hover and wheel (input parity)
		row.wheeled.connect(_on_row_wheeled)
		_rows.append(row)
	var list_h := (model.slot_ids.size() - 1) * pitch + row_h
	_list.size = Vector2(inner_w, list_h)
	var cm := _d.get("cursor", {}) as Dictionary
	_mote = LampMote.new()
	_mote.period_sec = HudLayout.num(cm, "breath_sec")
	_mote.alpha_min = HudLayout.num(cm, "breath_min")
	var mp := HudLayout.num(rm, "mote_px")
	_mote.size = Vector2(mp, mp)
	_list.add_child(_mote)
	y += list_h + HudLayout.num(p, "gap")
	_help = _label(&"HelpDimLabel", Rect2(pad, y, inner_w, HudLayout.num(p, "help_height")))
	_controls = _label(&"HelpDimLabel", Rect2(pad, y, inner_w, HudLayout.num(p, "help_height")))
	_controls.name = &"Controls"
	_controls.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_build_dialog()


func _build_dialog() -> void:
	var dm := _d.get("dialog", {}) as Dictionary
	_dialog_scrim = _make_scrim()
	_dialog_scrim.visible = false
	_dialog = Panel.new()
	HudLayout.place(_dialog, dm)
	_dialog.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_dialog.visible = false
	add_child(_dialog)
	var pad := HudLayout.num(dm, "pad")
	_dialog_text = Label.new()
	_dialog_text.theme_type_variation = &"BodyLabel"
	_dialog_text.position = Vector2(pad, pad)
	_dialog_text.size = _dialog.size - Vector2(pad, pad) * 2.0
	_dialog_text.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_dialog_text.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_dialog_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_dialog_text.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_dialog.add_child(_dialog_text)


## A full-screen night_sky vignette (the battle result screen's scrim shader).
func _make_scrim() -> ColorRect:
	var scrim := ColorRect.new()
	scrim.set_anchors_preset(Control.PRESET_FULL_RECT)
	scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := ShaderMaterial.new()
	mat.shader = SCRIM_SHADER
	mat.set_shader_parameter(&"tint", _c(&"scrim"))
	scrim.material = mat
	add_child(scrim)
	return scrim


# --- Render --------------------------------------------------------------------------------------


func _render() -> void:
	if _rows.is_empty():
		return
	for i in _rows.size():
		if i < model.slots.size():
			_rows[i].show_info(model.slots[i], model.is_usable(i), time_zone_bias_min, i == _rows.size() - 1)
	var in_dialog := model.phase == SaveMenuModel.Phase.CONFIRM or model.phase == SaveMenuModel.Phase.RESULT
	_list.modulate.a = HudLayout.num(_d.get("cursor", {}) as Dictionary, "dim_behind_dialog") if in_dialog else 1.0
	_mote.visible = not in_dialog
	_help.text = tr(model.help_key()) if model.help_key() != "" and not in_dialog else ""
	_render_controls()
	_place_cursor()
	_render_dialog(in_dialog)


## The controls line on the help row's right; the help keeps the rest of the row (it shrinks before it would cross).
func _render_controls() -> void:
	var key := str(CONTROLS_KEYS.get(model.mode, ""))
	if model.phase == SaveMenuModel.Phase.CONFIRM:
		key = CONTROLS_QUESTION_KEY
	elif model.phase == SaveMenuModel.Phase.RESULT:
		key = CONTROLS_RESULT_KEY
	_controls.text = tr(key)
	var gap := HudLayout.num(_d.get("panel", {}) as Dictionary, "gap")
	var room := _controls.size.x - _controls.get_combined_minimum_size().x - gap
	_help.size.x = room
	HudLayout.fit_label(_help, room)


func controls_text() -> String:
	return _controls.text


func _render_dialog(in_dialog: bool) -> void:
	_dialog.visible = in_dialog
	_dialog_scrim.visible = in_dialog
	if not in_dialog:
		if _choices != null:
			_choices.queue_free()
			_choices = null
		_choices_phase = -1
		return
	var slot := model.current()
	_dialog_text.text = tr(model.dialog_key).format({"slot": slot.slot_name() if slot != null else ""})
	if _choices == null or _choices_phase != model.phase:
		if _choices != null:
			_choices.queue_free()
		_choices = MenuPage.new()
		var cm := _d.get("dialog_choices", {}) as Dictionary
		var dm := _d.get("dialog", {}) as Dictionary
		var ids := model.dialog_choices()
		var r := HudLayout.rect_of(cm)
		var top := HudLayout.rect_of(dm).end.y + HudLayout.num(dm, "gap")
		_choices.position = Vector2(r.position.x, top)
		_choices.size = Vector2(r.size.x, MenuPage.height_for(cm, ids.size(), false))
		add_child(_choices)
		var choice_rows: Array[Dictionary] = []
		for id in ids:
			choice_rows.append({"id": id, "label": _choice_label(id), "enabled": true})
		_choices.setup(cm, &"save_dialog", "", choice_rows)
		_choices.row_clicked.connect(_on_choice_clicked)
		_choices.row_hovered.connect(func(i: int) -> void: model.dialog_cursor = i)  # M2-UI-26 (M2-ARC-06's bug)
		_choices_phase = model.phase
	_choices.set_cursor(model.dialog_cursor, is_inside_tree())


func _choice_label(id: StringName) -> String:
	if id == SaveMenuModel.CHOICE_YES:
		return tr("SAVE_CONFIRM_YES")
	if id == SaveMenuModel.CHOICE_NO:
		return tr("SAVE_CONFIRM_NO")
	return tr("SAVE_RESULT_CONTINUE")


func _place_cursor() -> void:
	if model.cursor < 0 or model.cursor >= _rows.size():
		return
	var row := _rows[model.cursor]
	var rm := _d.get("rows", {}) as Dictionary
	var cm := _d.get("cursor", {}) as Dictionary
	var mp := HudLayout.num(rm, "mote_px")
	var target := row.position
	var mote_pos := Vector2(
		HudLayout.num(rm, "name_x") - HudLayout.num(rm, "mote_offset") - mp * 0.5,
		row.position.y + row.size.y * 0.5 - mp * 0.5
	)
	if _cursor_tween != null and _cursor_tween.is_valid():
		_cursor_tween.kill()
	_cursor_box.size = row.size
	if not animate or not is_inside_tree() or _cursor_box.position == target or UiSettings.shared().reduced_motion():
		_cursor_box.position = target
		_mote.position = mote_pos
		return
	var dur := HudLayout.num(cm, "sec")
	_cursor_tween = create_tween().set_parallel(true)
	_cursor_tween.tween_property(_cursor_box, "position", target, dur).set_trans(Tween.TRANS_QUAD).set_ease(
		Tween.EASE_OUT
	)
	_cursor_tween.tween_property(_mote, "position", mote_pos, dur).set_delay(HudLayout.num(cm, "mote_lag_sec"))


func _animate_open() -> void:
	if not animate or not is_inside_tree() or UiSettings.shared().reduced_motion():
		return
	var om := _d.get("panel_open", {}) as Dictionary
	var dur := HudLayout.num(om, "sec")
	var from := HudLayout.num(om, "scale_from")
	var y := _panel.position.y
	_panel.pivot_offset = _panel.size * 0.5
	_panel.scale = Vector2(from, from)
	_panel.modulate.a = 0.0
	_panel.position.y = y + HudLayout.num(om, "rise_px")
	_scrim.modulate.a = 0.0
	var tw := create_tween().set_parallel(true).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	tw.tween_property(_panel, "scale", Vector2.ONE, dur)
	tw.tween_property(_panel, "modulate:a", 1.0, dur)
	tw.tween_property(_panel, "position:y", y, dur)
	tw.tween_property(_scrim, "modulate:a", 1.0, dur)


func _on_row_clicked(index: int) -> void:
	if not is_open() or model.phase != SaveMenuModel.Phase.BROWSE:
		return
	if index != model.cursor:
		model.set_cursor(index)
		return
	_after(model.accept())


## M2-UI-26: the pointer on a slot moves the cursor there (browsing only; a dialog holds it).
func _on_row_hovered(index: int) -> void:
	if is_open() and model.phase == SaveMenuModel.Phase.BROWSE and index != model.cursor:
		model.set_cursor(index)
		_render()


## M2-UI-26: the wheel steps the cursor while browsing.
func _on_row_wheeled(step: int) -> void:
	if is_open() and model.phase == SaveMenuModel.Phase.BROWSE and model.move(step):
		_render()


func _on_choice_clicked(index: int) -> void:
	if not is_open():
		return
	model.dialog_cursor = index
	_after(model.accept())


func _cursor_style() -> StyleBoxFlat:
	var chamfer := get_theme_constant(&"chamfer_small_px", HymnThemeBuilder.PALETTE_TYPE)
	var s := HymnThemeBuilder.notch_flat(_c(&"panel_raised"), chamfer)
	s.set_border_width_all(get_theme_constant(&"focus_px", HymnThemeBuilder.PALETTE_TYPE))
	s.border_color = _c(&"focus_gold")
	s.shadow_color = _c(&"focus_glow")
	s.shadow_size = get_theme_constant(&"focus_glow_px", HymnThemeBuilder.PALETTE_TYPE)
	return s


func _label(variation: StringName, r: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.position = r.position
	l.size = r.size
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel.add_child(l)
	return l


func _c(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


static func _autoload(autoload_name: StringName) -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	return tree.root.get_node_or_null(NodePath(String(autoload_name))) if tree != null else null
