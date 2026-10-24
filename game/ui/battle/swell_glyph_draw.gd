class_name SwellGlyphDraw
extends RefCounted
## Ysolde's glyph trace on the Swell panel (M2-UI-03; SwellGlyph). The whole glyph is drawn as its
## strokes, one direction each, from a gold start node: traced strokes burn solid in swell, a
## missed stroke is a dashed danger line with a cross, the stroke asked for now is a dashed focus
## line ending in an arrowhead, and later strokes are dim. Under it a bar runs down with the
## window's time left, with a gold notch where the swift grade closes: the bar's part past the
## notch is swell-colored while a swift trace is still possible. Draws only: the SwellGlyph
## decides every grade.


static func draw(v: SwellRingView, glyph: SwellGlyph) -> void:
	var c := v.figure_center()
	var pts := _points(glyph, v.metric("stroke_px"))
	var box := Rect2(pts[0], Vector2.ZERO)
	for p in pts:
		box = box.expand(p)
	var shift := Vector2(c.x, c.y - v.metric("glyph_lift")) - box.get_center()
	for k in glyph.strokes.size():
		_stroke(v, glyph, k, pts[k] + shift, pts[k + 1] + shift)
	var node := v.metric("node_px")
	for k in range(1, pts.size()):
		v.canvas().draw_colored_polygon(SwellRingView.diamond(pts[k] + shift, node), v.color(&"text_dim"))
	v.canvas().draw_colored_polygon(SwellRingView.diamond(pts[0] + shift, node * 1.5), v.color(&"focus_gold"))
	_time_bar(v, glyph, c.y + v.metric("glyph_bar_drop"))
	v.draw_pips(v.pips_y(), true)


## The glyph's vertices, from the origin, one stroke of `px` per direction.
static func _points(glyph: SwellGlyph, px: float) -> PackedVector2Array:
	var pts := PackedVector2Array([Vector2.ZERO])
	for b in glyph.strokes:
		pts.append(pts[-1] + SwellRingView.direction(b) * px)
	return pts


static func _stroke(v: SwellRingView, glyph: SwellGlyph, k: int, a: Vector2, b: Vector2) -> void:
	var cv := v.canvas()
	var dash := v.metric("dash_px")
	if k < glyph.grades.size():
		if glyph.grades[k] == SwellGlyph.GRADE_TRACED:
			cv.draw_line(a, b, v.color(&"swell"), v.metric("glyph_px"), true)
		else:
			cv.draw_dashed_line(a, b, v.color(&"danger"), v.metric("target_px"), dash)
			v.draw_cross((a + b) * 0.5, v.metric("note_px") * v.metric("cross_scale"), v.color(&"danger"))
	elif k == glyph.current_stroke() and not glyph.is_done():
		cv.draw_dashed_line(a, b, v.color(&"focus"), v.metric("target_px"), dash)
		var s := v.metric("note_px")
		var dir := (b - a).normalized()
		cv.draw_colored_polygon(SwellRingView.arrow(b - dir * s * 0.4, dir, s * 0.8), v.color(&"focus"))
	else:
		cv.draw_line(a, b, v.color(&"text_dim"), 1.0, true)


## The window's time left as a bar that runs down from the right, and the swift notch.
static func _time_bar(v: SwellRingView, glyph: SwellGlyph, y: float) -> void:
	var cv := v.canvas()
	var x0 := v.metric("pad") * 3.0
	var w := v.size.x - x0 * 2.0
	var h := v.metric("bar_px")
	var window := maxf(glyph.window_sec, 0.001)
	var left := clampf((glyph.lead_in_sec + glyph.window_sec - glyph.elapsed) / window, 0.0, 1.0)
	var notch := clampf((glyph.window_sec - glyph.swift_sec) / window, 0.0, 1.0)
	cv.draw_rect(Rect2(x0, y - h * 0.5, w, h), v.color(&"gauge_back"))
	cv.draw_rect(Rect2(x0, y - h * 0.5, w * minf(left, notch), h), v.color(&"focus"))
	if left > notch:
		cv.draw_rect(Rect2(x0 + w * notch, y - h * 0.5, w * (left - notch), h), v.color(&"swell"))
	var nx := x0 + w * notch
	cv.draw_line(Vector2(nx, y - h * 1.5), Vector2(nx, y + h * 1.5), v.color(&"focus_gold"), v.metric("target_px"))
	cv.draw_colored_polygon(SwellRingView.diamond(Vector2(nx, y - h * 1.5), h * 0.6), v.color(&"focus_gold"))
