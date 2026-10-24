class_name GraphicsMenu
extends SettingsPage
## The Graphics settings page (M1-UI-10; graphics_settings.md, "The Graphics menu"): a
## SettingsPage over GraphicsMenuModel. Every change saves and applies at once (GraphicsRuntime).
## Opened from the Settings hub (SettingsMenu), which the title and the field menu open (M2-UI-09).
## Layout: game/data/ui/graphics_menu.json.
## A preset change with GraphicsRuntime armed spawns the resident shader warm-up (M1-RND-22), which can
## freeze a frame for over a second, so it applies behind a veil (M1-UI-11, data "apply"): fade out,
## let one opaque frame draw, select the preset, hold an "Applying" card until the warm-up is done
## (GraphicsMenuModel.warmup_done), fade back. Input and clicks are swallowed until the veil lifts
## (SettingsPage.is_busy). Disarmed (tests, captures) nothing warms, so a preset applies at once, as
## a setting row always does.

enum Phase { IDLE, FADE_OUT, SETTLE, HOLD, FADE_IN }

var model: GraphicsMenuModel

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
	page_model = model
	name = &"GraphicsMenu"


func _ready() -> void:
	if model.viewport == null:
		model.viewport = get_viewport()
	super()
	_build_veil()
	set_process(false)


## True while a preset change is behind the veil (fading out, held for the warm-up, or lifting).
func is_applying() -> bool:
	return _phase != Phase.IDLE


func is_busy() -> bool:
	return is_applying()


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
	_veil.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_veil.mouse_filter = Control.MOUSE_FILTER_STOP
	_veil.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	_veil.visible = false
	add_child(_veil)
	_card = Label.new()
	_card.theme_type_variation = &"HelpDimLabel"
	HudLayout.place(_card, _apply.get("card", {}) as Dictionary)
	_card.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_card.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_card.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_card.text = tr(str(_apply.get("card_key", "")))
	_veil.add_child(_card)


func _show_veil() -> void:
	_veil.visible = _phase != Phase.IDLE
	_veil.modulate.a = _alpha
