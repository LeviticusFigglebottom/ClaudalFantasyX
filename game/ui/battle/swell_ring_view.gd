class_name SwellRingView
extends Control
## Rhen's Swell input on screen (M1-CMB-04): a lantern at the centre that flares on each beat, a
## ring closing on it (press when the ring meets the lamp's rim, at the flare's brightest), and
## one pip per beat below. A view over a SwellTimingRing: it draws the ring's state and never
## decides anything; BattleController drives the ring and reads its result.
## Grades read by shape, not hue alone: perfect = filled diamond with a halo, good = filled
## diamond, miss = a cross. Reduced motion keeps the timing but drops the flicker.

var ring: SwellTimingRing
var reduced_motion := false

var _m: Dictionary = {}
## Draws the lamp, ring and pips above the panel background (a Control draws under its children).
var _canvas: Control
var _title: Label
var _hint: Label
## The timing assist's tag (M2-UI-01), top left beside the ring; hidden while the assist is off.
var _assist: Label


func _ready() -> void:
	_m = HudLayout.section(&"swell_ring")
	HudLayout.place(self, _m)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var bg := Panel.new()
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	_canvas = Control.new()
	_canvas.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_canvas.set_anchors_preset(Control.PRESET_FULL_RECT)
	_canvas.draw.connect(_draw_ring)
	add_child(_canvas)
	var title_h := HudLayout.num(_m, "title_height")
	var hint_h := HudLayout.num(_m, "hint_height")
	_title = _label(&"HeaderLabel", Rect2(0, 0, size.x, title_h))
	_hint = _label(&"HelpLabel", Rect2(0, size.y - hint_h, size.x, hint_h))
	var pad := HudLayout.num(_m, "pad")
	_assist = _label(
		&"DimLabel", Rect2(pad, title_h, HudLayout.num(_m, "assist_width"), HudLayout.num(_m, "assist_height"))
	)
	_assist.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	_assist.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_assist.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_assist.visible = false
	visible = false


## Shows `r` under the technique's name `title_text`, with `hint` (what to press) below.
func open(r: SwellTimingRing, title_text: String, hint: String) -> void:
	ring = r
	_title.text = title_text
	_hint.text = hint
	visible = true
	refresh()


## Redraws the ring after its state changed (BattleController calls it after every tick and press).
func refresh() -> void:
	_canvas.queue_redraw()


func close() -> void:
	ring = null
	visible = false


func is_open() -> bool:
	return visible and ring != null


func set_hint(hint: String) -> void:
	_hint.text = hint


func hint_text() -> String:
	return _hint.text


## The timing assist's tag ("" hides it). BattleHud sets it from UiSettings.
func set_assist_text(text: String) -> void:
	_assist.text = text
	_assist.visible = text != ""


func assist_text() -> String:
	return _assist.text if _assist.visible else ""


## How bright the lamp is now, 0..1: it peaks with each beat (time_to_peak 0) and fades over
## flare_sec either side, flickering a little unless motion is reduced.
func brightness() -> float:
	if ring == null:
		return 0.0
	var flare := clampf(1.0 - absf(ring.time_to_peak()) / HudLayout.num(_m, "flare_sec"), 0.0, 1.0)
	var b := HudLayout.num(_m, "lamp_rest") + (1.0 - HudLayout.num(_m, "lamp_rest")) * flare * flare
	if not reduced_motion:
		var phase := ring.elapsed * HudLayout.num(_m, "flicker_hz") * TAU
		b *= 1.0 - HudLayout.num(_m, "flicker_amp") * 0.5 * (1.0 + sin(phase))
	return clampf(b, 0.0, 1.0)


## Radius of the closing ring: the outer edge when the beat opens, the lamp's rim at the peak.
func closing_radius() -> float:
	var lamp := HudLayout.num(_m, "lamp_radius")
	var outer := HudLayout.num(_m, "ring_radius")
	if ring == null:
		return outer
	var approach := maxf(ring.peak_at * ring.beat_sec, 0.001)
	return lamp + (outer - lamp) * clampf(ring.time_to_peak() / approach, 0.0, 1.0)


func ring_center() -> Vector2:
	var y := HudLayout.num(_m, "title_height") + HudLayout.num(_m, "pad") + HudLayout.num(_m, "ring_radius")
	return Vector2(size.x * 0.5, y)


func _draw_ring() -> void:
	if ring == null:
		return
	var c := ring_center()
	var lamp := HudLayout.num(_m, "lamp_radius")
	var b := brightness()
	var swell := _c(&"swell")
	var glow := swell
	glow.a = b * HudLayout.num(_m, "glow_alpha")
	_canvas.draw_circle(c, lamp + HudLayout.num(_m, "glow_radius") * b, glow)
	var core := _c(&"gauge_back").lerp(swell, b)
	_canvas.draw_circle(c, lamp, core)
	_canvas.draw_arc(c, lamp, 0.0, TAU, 48, _c(&"focus_gold"), HudLayout.num(_m, "target_px"), true)
	if not ring.is_done():
		var col := _c(&"focus")
		col.a *= clampf(HudLayout.num(_m, "ring_min_alpha") + b, 0.0, 1.0)
		_canvas.draw_arc(c, closing_radius(), 0.0, TAU, 64, col, HudLayout.num(_m, "ring_px"), true)
	_draw_pips(c.y + HudLayout.num(_m, "ring_radius") + HudLayout.num(_m, "pad"))


func _draw_pips(y: float) -> void:
	var px := HudLayout.num(_m, "pip_px")
	var gap := HudLayout.num(_m, "pip_gap")
	var x0 := size.x * 0.5 - (ring.beats - 1) * gap * 0.5
	for i in ring.beats:
		var at := Vector2(x0 + i * gap, y + px)
		if i < ring.grades.size():
			_draw_grade(at, px, ring.grades[i])
		else:
			var col := _c(&"focus") if i == ring.current_beat() and not ring.is_done() else _c(&"text_dim")
			var pts := _diamond(at, px)
			pts.append(pts[0])
			_canvas.draw_polyline(pts, col, 1.0, true)


func _draw_grade(at: Vector2, px: float, grade: StringName) -> void:
	match grade:
		SwellTimingRing.GRADE_PERFECT:
			_canvas.draw_colored_polygon(_diamond(at, px), _c(&"swell"))
			_canvas.draw_arc(at, px * 1.4, 0.0, TAU, 24, _c(&"focus_gold"), 1.0, true)
		SwellTimingRing.GRADE_GOOD:
			_canvas.draw_colored_polygon(_diamond(at, px), _c(&"focus"))
		_:
			var d := px * 0.7
			_canvas.draw_line(at + Vector2(-d, -d), at + Vector2(d, d), _c(&"danger"), 2.0, true)
			_canvas.draw_line(at + Vector2(-d, d), at + Vector2(d, -d), _c(&"danger"), 2.0, true)


static func _diamond(at: Vector2, px: float) -> PackedVector2Array:
	return PackedVector2Array([at + Vector2(0, -px), at + Vector2(px, 0), at + Vector2(0, px), at + Vector2(-px, 0)])


func _c(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


func _label(variation: StringName, r: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.position = r.position
	l.size = r.size
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l
