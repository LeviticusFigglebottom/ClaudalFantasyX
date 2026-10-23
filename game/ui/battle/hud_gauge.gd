class_name HudGauge
extends Control
## A thin HP/MP bar (docs/kb/art/ui.md §6.2): dark back, 1 px border, a fill with a soft
## top-to-bottom gradient. Below `low_fraction` the fill turns to the danger role AND gains
## 2 px diagonal hatching, so low HP never depends on hue alone.

## Palette role of the fill (&"hp", &"mp", &"swell").
var fill_role: StringName = &"hp"
var low_fraction := 0.0
var hatch_px := 4.0
## Shown fraction 0..1 (animated by set_value when in the tree).
var shown := 1.0
## Lighter top edge of the fill gradient, as a lerp toward white.
var sheen := 0.25
## A full Swell gauge's glow, 0..1 (0 = none). Above 0 the fill brightens by glow x sheen and a
## frame marks the gauge as full, so "full" never depends on the pulse alone.
var glow := 0.0
## The full frame (M1-UI-05): a `full_gap_px` band in `outline` (night) around the bar, then a
## `full_frame_px` line in `text` (white). The dark gap is what keeps the frame from melting into
## a gold fill: both edges of the gap are high-contrast, whatever the fill's hue (party_row sets
## these from battle_hud.json).
var full_gap_px := 0.0
var full_frame_px := 1.0

var _value := 1.0


func _init(role: StringName = &"hp") -> void:
	fill_role = role
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func set_value(current: int, maximum: int, animate_sec: float = 0.0) -> void:
	_value = clampf(float(current) / float(maxi(maximum, 1)), 0.0, 1.0)
	if animate_sec <= 0.0 or not is_inside_tree():
		shown = _value
		queue_redraw()
		return
	var tw := create_tween()
	tw.tween_method(_set_shown, shown, _value, animate_sec).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)


func is_low() -> bool:
	return low_fraction > 0.0 and _value < low_fraction and _value > 0.0


func _set_shown(v: float) -> void:
	shown = v
	queue_redraw()


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	for band in full_frame_rects():
		draw_rect(band[0], _c(band[1]))  # filled, outer first: the bar then covers the inside
	draw_rect(r, _c(&"gauge_back"))
	var fill_w := floorf(size.x * shown)
	if fill_w > 0.0:
		var col := _c(&"danger") if is_low() else _c(fill_role)
		col = col.lerp(Color.WHITE, glow * sheen)
		var top := col.lerp(Color.WHITE, sheen)
		var pts := PackedVector2Array([Vector2.ZERO, Vector2(fill_w, 0), Vector2(fill_w, size.y), Vector2(0, size.y)])
		draw_polygon(pts, PackedColorArray([top, top, col, col]))
		if is_low():
			_hatch(fill_w, _c(&"outline"))
	draw_rect(r, _c(&"gauge_border"), false, 1.0)


## The full-gauge frame as filled [rect, palette role] bands, outer first (empty when not full):
## the frame's rect, then the gap's rect inside it, then the bar itself covers the middle. Filled
## whole-pixel rects, not strokes, so each band is exactly its px wide on every side.
func full_frame_rects() -> Array[Array]:
	var out: Array[Array] = []
	if glow <= 0.0:
		return out
	var r := Rect2(Vector2.ZERO, size)
	out.append([r.grow(full_gap_px + full_frame_px), &"text"])
	if full_gap_px > 0.0:
		out.append([r.grow(full_gap_px), &"outline"])
	return out


func _hatch(width: float, col: Color) -> void:
	# 45° strokes from (x, h) to (x + h, 0), clipped to the filled part.
	var h := size.y
	var x := -h
	while x < width:
		var t0 := maxf(0.0, -x / h)
		var t1 := minf(1.0, (width - x) / h)
		if t0 < t1:
			draw_line(Vector2(x + t0 * h, h - t0 * h), Vector2(x + t1 * h, h - t1 * h), col, 1.0)
		x += hatch_px


func _c(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)
