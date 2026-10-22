class_name StatusGlyph
extends Control
## A status icon drawn as vector strokes on a 48-unit grid (docs/kb/art/ui.md §8): a flat tint
## disc at 0.35 behind a 2-unit stroke. Buffs use ui_focus, ailments ui_danger, so the shape
## carries the meaning and the hue only the polarity. Original glyphs; see docs/kb/tech/ui.md.

const GRID := 48.0
const STROKE := 2.0
const TINT_ALPHA := 0.35
const BUFFS: Array[StringName] = [&"haste", &"shell", &"protect", &"regen", &"reflect"]

var status: StringName = &""


func _init(sid: StringName = &"") -> void:
	status = sid
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func set_status(sid: StringName) -> void:
	status = sid
	queue_redraw()


static func is_buff(sid: StringName) -> bool:
	return BUFFS.has(sid)


func _draw() -> void:
	if status == &"":
		return
	var col := get_theme_color(&"focus" if is_buff(status) else &"danger", HymnThemeBuilder.PALETTE_TYPE)
	var s := minf(size.x, size.y) / GRID
	var w := maxf(STROKE * s * 1.5, 1.0)
	draw_circle(size * 0.5, minf(size.x, size.y) * 0.5, Color(col, TINT_ALPHA))
	var p := func(x: float, y: float) -> Vector2: return Vector2(x, y) * s
	match status:
		&"poison":
			draw_arc(p.call(24, 29), 9 * s, 0.0, PI, 12, col, w)
			_poly(PackedVector2Array([p.call(15, 29), p.call(24, 12), p.call(33, 29)]), col, w)
		&"sleep":
			draw_arc(p.call(24, 24), 12 * s, PI * 0.35, PI * 1.65, 16, col, w)
			draw_arc(p.call(29, 21), 9 * s, PI * 0.45, PI * 1.55, 12, col, w)
		&"silence":
			draw_arc(p.call(24, 24), 12 * s, 0.0, TAU, 20, col, w)
			draw_line(p.call(16, 32), p.call(32, 16), col, w)
		&"darkness":
			draw_circle(p.call(24, 24), 8 * s, col)
			draw_arc(p.call(24, 24), 13 * s, 0.0, TAU, 20, col, w)
		&"slow":
			_poly(PackedVector2Array([p.call(15, 12), p.call(33, 12), p.call(15, 36), p.call(33, 36)]), col, w, true)
		&"haste":
			_poly(PackedVector2Array([p.call(14, 24), p.call(24, 14), p.call(34, 24)]), col, w)
			_poly(PackedVector2Array([p.call(14, 34), p.call(24, 24), p.call(34, 34)]), col, w)
		&"stop":
			draw_rect(Rect2(p.call(16, 16), p.call(16, 16)), col, false, w)
		&"shell":
			draw_arc(p.call(24, 24), 13 * s, 0.0, TAU, 20, col, w)
			draw_arc(p.call(24, 24), 7 * s, 0.0, TAU, 16, col, w)
		&"protect":
			_poly(_shield(p), col, w, true)
		&"regen":
			draw_line(p.call(24, 13), p.call(24, 35), col, w)
			draw_line(p.call(13, 24), p.call(35, 24), col, w)
		&"armor_break", &"power_break", &"mental_break", &"magic_break":
			_break_glyph(p, col, w)
		_:
			_poly(PackedVector2Array([p.call(24, 12), p.call(36, 24), p.call(24, 36), p.call(12, 24)]), col, w, true)


func _break_glyph(p: Callable, col: Color, w: float) -> void:
	if status == &"armor_break":
		_poly(_shield(p), col, w, true)
	elif status == &"mental_break":
		draw_arc(p.call(24, 24), 12 * (p.call(1, 0) as Vector2).x, 0.0, TAU, 20, col, w)
	elif status == &"power_break":
		_poly(PackedVector2Array([p.call(14, 18), p.call(24, 28), p.call(34, 18)]), col, w)
	else:
		_poly(PackedVector2Array([p.call(24, 12), p.call(34, 24), p.call(24, 36), p.call(14, 24)]), col, w, true)
	# The crack: every Break shares it, so "broken" reads before the base shape does.
	_poly(PackedVector2Array([p.call(20, 10), p.call(27, 21), p.call(21, 27), p.call(28, 38)]), col, w)


func _shield(p: Callable) -> PackedVector2Array:
	return PackedVector2Array([p.call(14, 13), p.call(34, 13), p.call(34, 25), p.call(24, 36), p.call(14, 25)])


func _poly(pts: PackedVector2Array, col: Color, w: float, closed: bool = false) -> void:
	var line := pts.duplicate()
	if closed:
		line.append(pts[0])
	draw_polyline(line, col, w, true)
