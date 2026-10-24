class_name GraphicsMenu
extends Control
## The Graphics settings page (M1-UI-10; graphics_settings.md, "The Graphics menu"): a modal
## page over a dark backdrop. Logic is GraphicsMenuModel; this is its view (a MenuPage whose right
## column shows each value, plus a help line) and input. Every change saves and applies at once.
## Input: ui_up / ui_down move, ui_left / ui_right (or ui_accept, forward) change the value,
## ui_cancel closes; a click on a row steps its value forward.
## Opened from the title (TitleMenu, Settings). Layout: game/data/ui/graphics_menu.json.
## A preset change with GraphicsRuntime armed spawns the resident shader warm-up (M1-RND-22), which can
## freeze a frame for over a second, so it applies behind a veil (M1-UI-11, data "apply"): fade out,
## let one opaque frame draw, select the preset, hold an "Applying" card until the warm-up is done
## (GraphicsMenuModel.warmup_done), fade back. Input and clicks are swallowed until the veil lifts.
## Disarmed (tests, captures) nothing warms, so a preset applies at once, as a setting row always does.

signal closed

enum Phase { IDLE, FADE_OUT, SETTLE, HOLD, FADE_IN }

var model: GraphicsMenuModel

var _page: MenuPage
var _help: Label
var _open := false
var _veil: ColorRect
var _card: Label
var _apply: Dictionary = {}
var _phase := Phase.IDLE
var _alpha := 0.0
var _settle := 0
var _held_sec := 0.0
var _pending_delta := 0


func _init(vp: Viewport = null) -> void:
	model = GraphicsMenuModel.new(vp)
	name = &"GraphicsMenu"


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	if model.viewport == null:
		model.viewport = get_viewport()
	var backdrop := ColorRect.new()
	backdrop.set_anchors_preset(Control.PRESET_FULL_RECT)
	backdrop.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var deep := get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	backdrop.color = Color(deep, float(model.data.get("backdrop_alpha", 1.0)))
	add_child(backdrop)
	var pm := model.data.get("page", {}) as Dictionary
	_page = MenuPage.new()
	var r := HudLayout.rect_of(pm)
	_page.position = r.position
	_page.size = Vector2(r.size.x, MenuPage.height_for(pm, model.row_ids().size()))
	add_child(_page)
	_page.setup(pm, &"graphics", tr("GFX_MENU_TITLE"), _rows())
	_page.row_clicked.connect(_on_row_clicked)
	_help = Label.new()
	_help.theme_type_variation = &"HelpLabel"
	HudLayout.place(_help, model.data.get("help", {}) as Dictionary)
	_help.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_help.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_help.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_help.add_theme_color_override(&"font_color", get_theme_color(&"text_dim", HymnThemeBuilder.PALETTE_TYPE))
	add_child(_help)
	_build_veil()
	model.changed.connect(_render)
	_open = true
	set_process(false)
	_render()


func _unhandled_input(event: InputEvent) -> void:
	if handle_input(event):
		get_viewport().set_input_as_handled()


## Applies one input event. Returns true when the page used it. Tests call this directly.
## While a preset change is behind the veil every event is swallowed (true) and nothing moves.
func handle_input(event: InputEvent) -> bool:
	if not _open:
		return false
	if is_applying():
		return true
	if event.is_action_pressed(&"ui_up", true):
		model.move(-1)
	elif event.is_action_pressed(&"ui_down", true):
		model.move(1)
	elif event.is_action_pressed(&"ui_left", true):
		_change(-1)
	elif event.is_action_pressed(&"ui_right", true) or event.is_action_pressed(&"ui_accept"):
		_change(1)
	elif event.is_action_pressed(&"ui_cancel"):
		close()
	else:
		return false
	return true


func is_open() -> bool:
	return _open


func close() -> void:
	if not _open or is_applying():
		return
	_open = false
	closed.emit()
	queue_free()


## The value shown on `row` (tests and captures read it).
func value_shown(row: StringName) -> String:
	var i := model.row_ids().find(row)
	return str(_page.rows[i].get("right", "")) if i >= 0 and i < _page.rows.size() else ""


func help_text() -> String:
	return _help.text


## True while a preset change is behind the veil (fading out, held for the warm-up, or lifting).
func is_applying() -> bool:
	return _phase != Phase.IDLE


## The veil's opacity (0 when lifted).
func veil_alpha() -> float:
	return _alpha


## The held card's text while the veil is up ("" otherwise).
func card_text() -> String:
	return _card.text if _veil.visible else ""


func _process(delta: float) -> void:
	advance(delta)


## Steps the veil by one frame of `delta` seconds. Called from _process; tests call it directly.
func advance(delta: float) -> void:
	match _phase:
		Phase.FADE_OUT:
			_alpha = minf(_alpha + _rate(&"fade_out_sec", delta), 1.0)
			if _alpha >= 1.0:
				_phase = Phase.SETTLE
				_settle = int(_apply.get("settle_frames", 0))
		Phase.SETTLE:
			# The opaque frame has to draw before the warm-up's first frame freezes the screen.
			_settle -= 1
			if _settle <= 0:
				model.cycle(_pending_delta)
				_phase = Phase.HOLD
				_held_sec = 0.0
		Phase.HOLD:
			_held_sec += delta
			if model.warmup_done() or _held_sec >= float(_apply.get("max_hold_sec", 0.0)):
				_phase = Phase.FADE_IN
		Phase.FADE_IN:
			_alpha = maxf(_alpha - _rate(&"fade_in_sec", delta), 0.0)
			if _alpha <= 0.0:
				_phase = Phase.IDLE
				set_process(false)
		_:
			return
	_show_veil()


func _rows() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for id in model.row_ids():
		out.append({"id": id, "label": model.label(id), "right": model.value_text(id), "right_role": &"focus_gold"})
	return out


func _render() -> void:
	_page.replace_rows(_rows())
	_page.set_cursor(model.cursor, is_inside_tree())
	_help.text = tr(model.help_key())


func _on_row_clicked(index: int) -> void:
	if is_applying():
		return
	if model.cursor == index:
		_change(1)
	else:
		model.set_cursor(index)


## Steps the current row's value. A preset change that will warm shaders goes behind the veil first.
func _change(delta: int) -> void:
	if model.current() != GraphicsMenuModel.ROW_PRESET or not _warms_on_preset():
		model.cycle(delta)
		return
	_pending_delta = delta
	_phase = Phase.FADE_OUT
	_alpha = 0.0
	_show_veil()
	set_process(true)


## Whether select_preset will spawn the resident warm-up (the condition in GraphicsRuntime.select_preset).
func _warms_on_preset() -> bool:
	return GraphicsRuntime.armed and model.viewport != null and model.viewport.is_inside_tree()


## The alpha one frame of `delta` adds or removes for a fade of data `key` seconds (instant when 0).
func _rate(key: StringName, delta: float) -> float:
	var sec := float(_apply.get(key, 0.0))
	return 1.0 if sec <= 0.0 else delta / sec


func _build_veil() -> void:
	_apply = model.data.get("apply", {}) as Dictionary
	_veil = ColorRect.new()
	_veil.name = &"ApplyVeil"
	_veil.set_anchors_preset(Control.PRESET_FULL_RECT)
	_veil.mouse_filter = Control.MOUSE_FILTER_STOP
	_veil.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	_veil.visible = false
	add_child(_veil)
	_card = Label.new()
	_card.theme_type_variation = &"HelpLabel"
	HudLayout.place(_card, _apply.get("card", {}) as Dictionary)
	_card.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_card.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_card.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_card.add_theme_color_override(&"font_color", get_theme_color(&"text_dim", HymnThemeBuilder.PALETTE_TYPE))
	_card.text = tr(str(_apply.get("card_key", "")))
	_veil.add_child(_card)


func _show_veil() -> void:
	_veil.visible = _phase != Phase.IDLE
	_veil.modulate.a = _alpha
