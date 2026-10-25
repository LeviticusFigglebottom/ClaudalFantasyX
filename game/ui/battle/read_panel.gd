class_name ReadPanel
extends Control
## What a Read revealed (M2-UI-02, SPEC §6.1): a tide-notch panel over the field with the foe's
## EnemyPage (as it stands: HP, MP, statuses), opened by BattleBestiary when a Read lands and
## closed on confirm (or cancel, or a click). It costs no battle time: the Read itself paid its
## rank, and while the panel is open BattleHud.holds_battle() is true, so BattleController.tick()
## holds every wait (the next turn starts only after the player has read it). The timeline on the
## right stays uncovered (pillar 4). A view only: it never touches the engine.

signal closed

## The menu actions the panel takes while it is open (other keys, e.g. the debug F-keys, pass).
const MODAL_ACTIONS: Array[StringName] = [&"ui_accept", &"ui_cancel", &"ui_up", &"ui_down", &"ui_left", &"ui_right"]

var motion_scale := 1.0

var _m: Dictionary = {}
var _open_m: Dictionary = {}
var _panel: PanelContainer
var _view: EnemyPageView
var _hint: Label


func _ready() -> void:
	_m = HudLayout.section(&"read_panel")
	_open_m = HudLayout.section(&"panel_open")
	# Built by script: the offsets must follow the anchors too, or it stays 0 x 0 and a click on
	# it never lands (M2-UI-26).
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	# Modal: the whole screen takes the mouse while open, so nothing behind it can be clicked.
	mouse_filter = Control.MOUSE_FILTER_STOP
	gui_input.connect(_on_click)
	_panel = PanelContainer.new()
	HudLayout.place(_panel, _m)
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_panel)
	var margin := MarginContainer.new()
	margin.mouse_filter = Control.MOUSE_FILTER_IGNORE
	for side: StringName in [&"margin_left", &"margin_right", &"margin_top", &"margin_bottom"]:
		margin.add_theme_constant_override(side, int(HudLayout.num(_m, "pad")))
	_panel.add_child(margin)
	var v := VBoxContainer.new()
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	margin.add_child(v)
	_view = EnemyPageView.new()
	_view.size_flags_vertical = Control.SIZE_EXPAND_FILL
	v.add_child(_view)
	_hint = Label.new()
	_hint.theme_type_variation = &"DimLabel"
	_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_hint.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_hint.text = tr("HUD_READ_CLOSE_HINT")
	v.add_child(_hint)
	visible = false


## Shows `page` (EnemyPage.from_reveal). `animate` plays the 180 ms panel open (off in captures).
func open(page: Dictionary, animate: bool = true) -> void:
	_view.show_page(page)
	visible = true
	_panel.size = Vector2(_panel.size.x, 0.0)  # fit the page (a Control never shrinks by itself)
	if animate:
		_animate_open()


func close() -> void:
	if not visible:
		return
	visible = false
	closed.emit()


func is_open() -> bool:
	return visible


func page() -> Dictionary:
	return _view.page


func shown_text() -> PackedStringArray:
	var out := _view.shown_text()
	out.append(_hint.text)
	return out


## Confirm or cancel closes it; the other menu actions are swallowed while it is open (it is
## modal). Returns true when the event was taken.
func handle_input(event: InputEvent) -> bool:
	if not visible:
		return false
	if event.is_action_pressed(&"ui_accept") or event.is_action_pressed(&"ui_cancel"):
		close()
		return true
	for action in MODAL_ACTIONS:
		if event.is_action(action):
			return true
	return false


## The HUD sits under BattleController, so its nodes see an event before the controller does.
func _unhandled_input(event: InputEvent) -> void:
	if handle_input(event):
		get_viewport().set_input_as_handled()


func _on_click(event: InputEvent) -> void:
	var mb := event as InputEventMouseButton
	if mb != null and mb.pressed and mb.button_index == MOUSE_BUTTON_LEFT:
		close()


func _animate_open() -> void:
	if not is_inside_tree():
		return
	var dur := HudLayout.num(_open_m, "sec")
	var from := HudLayout.num(_open_m, "scale_from")
	var y := _panel.position.y
	_panel.pivot_offset = _panel.size * 0.5
	_panel.scale = Vector2(from, from)
	_panel.modulate.a = 0.0
	_panel.position.y = y + HudLayout.num(_open_m, "rise_px") * motion_scale
	var tw := create_tween().set_parallel(true).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	tw.tween_property(_panel, "scale", Vector2.ONE, dur)
	tw.tween_property(_panel, "modulate:a", 1.0, dur)
	tw.tween_property(_panel, "position:y", y, dur)
