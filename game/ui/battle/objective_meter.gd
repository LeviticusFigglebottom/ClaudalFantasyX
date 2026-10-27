class_name ObjectiveMeter
extends Control
## A set piece's objective on the battle HUD (M3-UI-100; docs/kb/design/set_piece_battles.md): the objective's
## words ("Up the stair") and one pip per group the quota asks for, filled for each one up, with the count
## spelled out beside them, so the goal reads without colour alone. Top centre under the help line, clear of the
## timeline and the boss status (battle_hud.json "objective_meter"). It never takes input. BattleSetPieceHud
## shows it for an encounter with an `objective` and moves it as the engine's objective_count rises.

var count := 0
var quota := 0

var _m: Dictionary = {}
var _panel: Panel
var _title: Label
var _count: Label


func _ready() -> void:
	_m = HudLayout.section(&"objective_meter")
	HudLayout.place(self, _m)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel = Panel.new()
	_panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_panel)
	var pad := HudLayout.num(_m, "pad")
	_title = _label(&"SmallLabel", Rect2(pad, 0.0, HudLayout.num(_m, "title_width"), size.y))
	_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	var count_w := HudLayout.num(_m, "count_width")
	_count = _label(&"HudNumber", Rect2(size.x - pad - count_w, 0.0, count_w, size.y))
	_count.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	visible = false


## Shows `title` with `now` of `of` groups up (of = 0 hides the meter).
func show_progress(title: String, now: int, of: int) -> void:
	count = clampi(now, 0, maxi(of, 0))
	quota = of
	visible = of > 0
	_title.text = title
	UiFrame.fit_line(_title, _title.size.x)  # 130 % text stays on its line (shrinks, then trims)
	_count.text = tr("HUD_OBJECTIVE_COUNT_FMT").format({"count": count, "quota": quota})
	queue_redraw()


func title_text() -> String:
	return _title.text


func count_text() -> String:
	return _count.text


func _draw() -> void:
	if quota <= 0:
		return
	var r := HudLayout.num(_m, "pip_px") * 0.5
	var gap := HudLayout.num(_m, "pip_gap")
	var x := HudLayout.num(_m, "pad") + HudLayout.num(_m, "title_width") + r
	var y := size.y * 0.5
	var on := _theme(StringName(str(_m.get("pip_on_role", ""))))
	var off := _theme(StringName(str(_m.get("pip_off_role", ""))))
	for i in quota:
		var c := Vector2(x + i * (r * 2.0 + gap), y)
		if i < count:
			draw_circle(c, r, on)
		else:
			draw_arc(c, r - 1.0, 0.0, TAU, 24, off, HudLayout.num(_m, "pip_line_px"))


func _label(variation: StringName, rect: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.position = rect.position
	l.size = rect.size
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	add_child(l)
	return l


func _theme(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)
