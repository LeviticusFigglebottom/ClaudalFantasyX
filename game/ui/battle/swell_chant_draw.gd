class_name SwellChantDraw
extends RefCounted
## Asha's verse chant on the Swell panel (M2-UI-03; SwellChant). The phrase's notes scroll from
## the right onto a gold line, each an arrow pointing at the direction it asks for, spaced by its
## time, so the rhythm reads before it sounds. A band around the line shows the good window (and,
## brighter, the perfect one), so the timing assist's wider window is seen. Draws only: the
## SwellChant decides every grade.
## Notes: later ones are white outlines; the one waiting now is a focus outline in a gold diamond
## frame; a sung note is filled (swell with a gold halo for perfect, focus for good) and a missed
## one a dim outline under a danger cross. Graded notes scroll on past the line.


static func draw(v: SwellRingView, chant: SwellChant) -> void:
	var cv := v.canvas()
	var c := v.figure_center()
	var left := v.metric("pad")
	var right := v.size.x - left
	var now_x := left + v.metric("chant_now_x")
	var pps := v.metric("chant_px_per_sec")
	var half := v.metric("chant_band_half")
	cv.draw_line(Vector2(left, c.y), Vector2(right, c.y), v.color(&"text_dim"), 1.0)
	var good := v.color(&"focus")
	good.a = v.metric("window_alpha")
	cv.draw_rect(Rect2(now_x - chant.good_sec * pps, c.y - half, chant.good_sec * pps * 2.0, half * 2.0), good)
	var best := v.color(&"focus_gold")
	best.a = v.metric("window_alpha")
	cv.draw_rect(Rect2(now_x - chant.perfect_sec * pps, c.y - half, chant.perfect_sec * pps * 2.0, half * 2.0), best)
	cv.draw_line(Vector2(now_x, c.y - half), Vector2(now_x, c.y + half), v.color(&"focus_gold"), v.metric("target_px"))
	var s := v.metric("note_px")
	for i in chant.grade_count():
		var x := now_x + (chant.note_time(i) - chant.elapsed) * pps
		if x < left + s or x > right - s:
			continue
		_note(v, chant, i, Vector2(x, c.y), s)
	v.draw_pips(v.pips_y(), false)


static func _note(v: SwellRingView, chant: SwellChant, i: int, at: Vector2, s: float) -> void:
	var cv := v.canvas()
	var pts := SwellRingView.arrow(at, SwellRingView.direction(chant.buttons[i]), s)
	if i < chant.grades.size():
		var grade := chant.grades[i]
		if grade == SwellInput.GRADE_PERFECT:
			cv.draw_colored_polygon(pts, v.color(&"swell"))
			cv.draw_arc(at, s * v.metric("halo_scale"), 0.0, TAU, 24, v.color(&"focus_gold"), 1.0, true)
		elif grade == SwellInput.GRADE_GOOD:
			cv.draw_colored_polygon(pts, v.color(&"focus"))
		else:
			v.outline(pts, v.color(&"text_dim"), 1.0)
			v.draw_cross(at, s * v.metric("cross_scale"), v.color(&"danger"))
	elif i == chant.current_note() and not chant.is_done():
		v.outline(pts, v.color(&"focus"), v.metric("target_px"))
		v.outline(SwellRingView.diamond(at, s * v.metric("frame_scale")), v.color(&"focus_gold"), 1.0)
	else:
		v.outline(pts, v.color(&"text"), 1.0)
