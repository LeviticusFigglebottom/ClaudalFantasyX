class_name SpeedPreview
extends PanelContainer
## A live preview of the speed setting under the Accessibility page's cursor (the Lead's options and
## quality-of-life pass), so the choice is seen before it is kept:
##   text_speed    a sample line reveals at the dialogue box's speed for that setting (text_box.json
##                 chars_per_sec times the option, UiSettings.dialogue_chars_per_sec; instant shows it whole),
##                 then holds and starts again;
##   battle_speed  a pip crosses a track in one action's hold (battle_hud.json pacing action_hold_sec)
##                 scaled by UiSettings.battle_time_scale, with the time in words; under reduced motion only
##                 the words.
## Hidden on every other row. Layout: graphics_menu.json "speed_preview".

const TEXT := &"text_speed"
const BATTLE := &"battle_speed"

## The setting being previewed (&"" when hidden).
var kind: StringName = &""
## The reveal's characters per second (0: instant), and the pip's crossing time in seconds.
var cps := 0.0
var cross_sec := 0.0
## Time into the current loop.
var t := 0.0

var _m: Dictionary = {}
var _settings: UiSettings
var _caption: Label
var _sample: Label
var _track: ColorRect
var _pip: ColorRect


func setup(metrics: Dictionary, settings: UiSettings) -> void:
	_m = metrics
	_settings = settings
	HudLayout.place(self, metrics)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var v := VBoxContainer.new()
	v.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(v)
	_caption = Label.new()
	_caption.theme_type_variation = &"HelpDimLabel"
	_caption.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(_caption)
	_sample = Label.new()
	_sample.theme_type_variation = &"BodyLabel"
	_sample.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(_sample)
	_track = ColorRect.new()
	_track.custom_minimum_size = Vector2(0.0, HudLayout.num(metrics, "track_px"))
	_track.color = get_theme_color(&"panel_deep", HymnThemeBuilder.PALETTE_TYPE)
	v.add_child(_track)
	_pip = ColorRect.new()
	_pip.size = Vector2.ONE * HudLayout.num(metrics, "track_px")
	_pip.color = get_theme_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE)
	_track.add_child(_pip)
	show_for(&"")


## Shows the preview for `row` (TEXT, BATTLE; anything else hides it) at the setting's current value,
## from the start of its loop.
func show_for(row: StringName) -> void:
	kind = row if row in [TEXT, BATTLE] else &""
	visible = kind != &""
	t = 0.0
	if kind == TEXT:
		var box := DialogueTextSettings.load_default()
		cps = _settings.dialogue_chars_per_sec(box.chars_per_sec, box.min_chars_per_sec, box.max_chars_per_sec)
		_caption.text = tr("SET_PREVIEW_TEXT_CAPTION")
		_sample.text = tr("SET_PREVIEW_TEXT_SAMPLE")
		_track.visible = false
	elif kind == BATTLE:
		var pacing := HudLayout.section(&"pacing")
		cross_sec = HudLayout.num(pacing, "action_hold_sec") * _settings.battle_time_scale()
		_caption.text = tr("SET_PREVIEW_BATTLE_CAPTION")
		_sample.text = tr("SET_PREVIEW_BATTLE_FMT").format({"sec": "%.1f" % cross_sec})
		_track.visible = not _settings.reduced_motion()
	_apply()


func _process(delta: float) -> void:
	if kind == &"":
		return
	t += delta
	var loop := _loop_sec()
	if loop > 0.0 and t > loop:
		t = 0.0
	_apply()


## The reveal's progress (0..1) at the current time: the text's share of characters shown, or the pip's
## share of the track crossed.
func progress() -> float:
	if kind == TEXT:
		if cps <= 0.0:
			return 1.0
		return clampf(t * cps / float(maxi(_sample.text.length(), 1)), 0.0, 1.0)
	if kind == BATTLE:
		return clampf(t / cross_sec, 0.0, 1.0) if cross_sec > 0.0 else 1.0
	return 0.0


func _loop_sec() -> float:
	var run := 0.0
	if kind == TEXT and cps > 0.0:
		run = _sample.text.length() / cps
	elif kind == BATTLE:
		run = cross_sec
	return run + HudLayout.num(_m, "hold_sec")


func _apply() -> void:
	if kind == TEXT:
		_sample.visible_ratio = progress()
	elif kind == BATTLE and _track.visible:
		var room := maxf(_track.size.x - _pip.size.x, 0.0)
		_pip.position.x = room * ease(progress(), HudLayout.num(_m, "pip_ease"))
