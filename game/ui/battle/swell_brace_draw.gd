class_name SwellBraceDraw
extends RefCounted
## Toma's tide brace on the Swell panel (M2-UI-03; SwellBrace). A track runs from the input's
## opening to the end of the counter's window: the blows hang over it as wedges at their times,
## the counter sits on it as a gold diamond inside its window band, and a playhead moves along it.
## Under the track a shield shows the hold, filled while Confirm is held and hollow when it is not
## (the panel's status line says it in words too). Draws only: the SwellBrace decides every grade.
## Blows: white outlines to come, a focus outline for the next one, filled focus once braced, a
## dim outline under a danger cross when missed. The counter takes its grade's pip mark.


static func draw(v: SwellRingView, brace: SwellBrace) -> void:
	var cv := v.canvas()
	var c := v.figure_center()
	var y := c.y - v.metric("brace_lift")
	var x0 := v.metric("pad") * 2.0
	var x1 := v.size.x - x0
	var end := maxf(brace.duration_sec(), 0.001)
	var to_x := func(t: float) -> float: return x0 + (x1 - x0) * clampf(t / end, 0.0, 1.0)
	var half := v.metric("brace_band_half")
	var good := v.color(&"focus")
	good.a = v.metric("window_alpha")
	var ct := brace.counter_time()
	var g0: float = to_x.call(ct - brace.good_sec)
	cv.draw_rect(Rect2(g0, y - half, float(to_x.call(ct + brace.good_sec)) - g0, half * 2.0), good)
	var best := v.color(&"focus_gold")
	best.a = v.metric("window_alpha")
	var p0: float = to_x.call(ct - brace.perfect_sec)
	cv.draw_rect(Rect2(p0, y - half, float(to_x.call(ct + brace.perfect_sec)) - p0, half * 2.0), best)
	cv.draw_line(Vector2(x0, y), Vector2(x1, y), v.color(&"text_dim"), v.metric("target_px"))
	var s := v.metric("note_px")
	for i in brace.impacts_at.size():
		_blow(v, brace, i, Vector2(to_x.call(brace.impact_time(i)), y - s - v.metric("blow_gap")), s)
	var counter_at := Vector2(to_x.call(ct), y)
	var last := brace.grade_count() - 1
	if brace.grades.size() > last:
		v.draw_grade(counter_at, s, brace.grades[last])
	else:
		v.outline(SwellRingView.diamond(counter_at, s), v.color(&"focus_gold"), v.metric("target_px"))
	if not brace.is_done():
		var x: float = to_x.call(brace.elapsed)
		cv.draw_line(Vector2(x, y - half - s), Vector2(x, y + half), v.color(&"text"), v.metric("target_px"))
	_shield(v, Vector2(c.x, y + v.metric("shield_drop")), brace.holding and not brace.is_done())
	v.draw_pips(v.pips_y(), true)


static func _blow(v: SwellRingView, brace: SwellBrace, i: int, at: Vector2, s: float) -> void:
	var pts := SwellRingView.arrow(at, Vector2.DOWN, s)
	if i < brace.grades.size():
		if brace.grades[i] == SwellBrace.GRADE_BRACED:
			v.canvas().draw_colored_polygon(pts, v.color(&"focus"))
		else:
			v.outline(pts, v.color(&"text_dim"), 1.0)
			v.draw_cross(at, s * v.metric("cross_scale"), v.color(&"danger"))
	elif i == brace.grades.size() and not brace.is_done():
		v.outline(pts, v.color(&"focus"), v.metric("target_px"))
	else:
		v.outline(pts, v.color(&"text"), 1.0)


## A shield: flat top, pointed foot. Filled `swell` with a gold frame while held, else hollow.
static func _shield(v: SwellRingView, at: Vector2, held: bool) -> void:
	var w := v.metric("shield_px")
	var pts := PackedVector2Array(
		[
			at + Vector2(-w, -w),
			at + Vector2(w, -w),
			at + Vector2(w, w * 0.2),
			at + Vector2(0, w * 1.2),
			at + Vector2(-w, w * 0.2),
		]
	)
	if held:
		v.canvas().draw_colored_polygon(pts, v.color(&"swell"))
		v.outline(pts, v.color(&"focus_gold"), v.metric("target_px"))
	else:
		v.outline(pts, v.color(&"text_dim"), v.metric("target_px"))
