class_name TimelineChip
extends Control
## One turn in the TurnTimeline (docs/kb/art/ui.md §6.1). Ally and enemy differ by SHAPE as well
## as fill: allies have a square left edge, enemies a chevron cut pointing left. A ghost is the
## acting fighter's predicted next turn (dashed gold frame, half alpha); a skipped turn
## (Stop/Sleep) is hatched and dimmed; `moved` draws a ▲/▼ for chips the preview shifts.

const TEAM_ENEMY := &"enemy"

var combatant_id: StringName = &""
var team: StringName = &"party"
var label_text := ""
var tint := Color.WHITE
var is_current := false
var ghost := false
var skipped := false
## -1 = moves earlier (▲), +1 = later (▼), 0 = unchanged.
var moved := 0
var targeted := false
var target_color := Color.WHITE
## The running slide/fade, killed when a newer layout arrives (TurnTimeline._move).
var move_tween: Tween

var _metrics: Dictionary = {}
var _name: Label
var _initial: Label


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_initial = Label.new()
	_initial.theme_type_variation = &"HudNumber"
	_initial.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_initial.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	add_child(_initial)
	_name = Label.new()
	_name.theme_type_variation = &"SmallLabel"
	_name.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_name.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	_name.clip_text = true
	add_child(_name)


func setup(metrics: Dictionary) -> void:
	_metrics = metrics


## Applies a slot from TurnTimeline.build_slots plus the combatant's identity.
func apply(slot: Dictionary, identity: Dictionary, current: bool) -> void:
	combatant_id = slot["id"]
	team = slot["team"]
	ghost = bool(slot["ghost"])
	skipped = bool(slot["skipped"])
	moved = int(slot["moved"])
	targeted = bool(slot.get("targeted", false))
	is_current = current
	label_text = str(identity.get("label", String(combatant_id)))
	tint = identity.get("tint", Color.WHITE)
	_name.text = label_text
	_initial.text = label_text.left(1)
	_layout_children()
	queue_redraw()


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED:
		_layout_children()


func _layout_children() -> void:
	if _metrics.is_empty():
		return
	var pad := HudLayout.num(_metrics, "pad")
	var left := _left_edge()
	var side := size.y - pad * 2.0
	_initial.position = Vector2(left + pad, pad)
	_initial.size = Vector2(side, side)
	var arrow := HudLayout.num(_metrics, "arrow_px") + pad * 2.0
	var name_x := left + pad * 2.0 + side
	_name.position = Vector2(name_x, 0.0)
	_name.size = Vector2(maxf(size.x - name_x - arrow, 0.0), size.y)
	var dim := skipped or ghost
	_name.modulate = Color(1, 1, 1, HudLayout.num(_metrics, "skipped_alpha")) if skipped else Color.WHITE
	_name.add_theme_color_override(&"font_color", _name_color() if not dim else _theme(&"text_dim"))


func _draw() -> void:
	if _metrics.is_empty():
		return
	var shape := _shape()
	var fill := _theme(&"enemy_chip") if team == TEAM_ENEMY else _theme(&"ally_chip")
	if ghost:
		fill.a *= HudLayout.num(_metrics, "ghost_alpha")
	draw_colored_polygon(shape, fill)
	_draw_portrait()
	if skipped:
		_draw_hatch()
	if ghost:
		_draw_dashed(shape, _theme(&"focus_gold"))
	elif is_current:
		_draw_loop(shape, _theme(&"focus"), float(_theme_k(&"focus_px")))
	if moved != 0:
		_draw_arrow()
	if targeted:
		var r := HudLayout.num(_metrics, "target_mark_px")
		var c := Vector2(size.x - r - HudLayout.num(_metrics, "pad"), size.y * 0.5)
		if moved != 0:
			c.x -= HudLayout.num(_metrics, "arrow_px") + r
		draw_arc(c, r, 0.0, TAU, 16, target_color, float(_theme_k(&"focus_px")))
		draw_circle(c, r * 0.35, target_color)


func _shape() -> PackedVector2Array:
	var w := size.x
	var h := size.y
	if team == TEAM_ENEMY:
		var cut := HudLayout.num(_metrics, "chevron_px")
		return PackedVector2Array([Vector2(0, h * 0.5), Vector2(cut, 0), Vector2(w, 0), Vector2(w, h), Vector2(cut, h)])
	return PackedVector2Array([Vector2(0, 0), Vector2(w, 0), Vector2(w, h), Vector2(0, h)])


func _left_edge() -> float:
	return HudLayout.num(_metrics, "chevron_px") if team == TEAM_ENEMY else 0.0


func _draw_portrait() -> void:
	var pad := HudLayout.num(_metrics, "pad")
	var side := size.y - pad * 2.0
	var r := Rect2(Vector2(_left_edge() + pad, pad), Vector2(side, side))
	var col := tint
	if ghost:
		col.a *= HudLayout.num(_metrics, "ghost_alpha")
	if team == TEAM_ENEMY:
		# Enemy portrait is a diamond, ally a square: a second shape cue.
		var c := r.get_center()
		var hs := side * 0.5
		draw_colored_polygon(
			PackedVector2Array([c + Vector2(0, -hs), c + Vector2(hs, 0), c + Vector2(0, hs), c + Vector2(-hs, 0)]), col
		)
	else:
		draw_rect(r, col)


func _draw_hatch() -> void:
	var step := HudLayout.num(_metrics, "hatch_px")
	var col := _theme(&"text_dim")
	col.a *= HudLayout.num(_metrics, "skipped_alpha")
	var x := -size.y
	while x < size.x:
		draw_line(Vector2(x, size.y), Vector2(x + size.y, 0), col, 1.0)
		x += step


func _draw_dashed(shape: PackedVector2Array, col: Color) -> void:
	var dash := HudLayout.num(_metrics, "dash_px")
	var inset := _inset(shape, 0.5)
	for i in inset.size():
		var a := inset[i]
		var b := inset[(i + 1) % inset.size()]
		var length := a.distance_to(b)
		var t := 0.0
		while t < length:
			var e := minf(t + dash, length)
			draw_line(a.lerp(b, t / length), a.lerp(b, e / length), col, 1.0)
			t += dash * 2.0


func _draw_loop(shape: PackedVector2Array, col: Color, width: float) -> void:
	var loop := _inset(shape, width * 0.5)
	loop.append(loop[0])
	draw_polyline(loop, col, width)


func _draw_arrow() -> void:
	var a := HudLayout.num(_metrics, "arrow_px")
	var pad := HudLayout.num(_metrics, "pad")
	var c := Vector2(size.x - pad - a * 0.5, size.y * 0.5)
	var hh := a * 0.5
	var pts: PackedVector2Array
	if moved < 0:
		pts = PackedVector2Array([c + Vector2(-hh, hh * 0.8), c + Vector2(hh, hh * 0.8), c + Vector2(0, -hh * 0.8)])
	else:
		pts = PackedVector2Array([c + Vector2(-hh, -hh * 0.8), c + Vector2(hh, -hh * 0.8), c + Vector2(0, hh * 0.8)])
	draw_colored_polygon(pts, _theme(&"text_dim"))


## Pulls every vertex toward the centroid's side by `d` px on each axis (good enough for
## these convex chips: keeps 1 px lines inside the shape).
func _inset(shape: PackedVector2Array, d: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	var center := Vector2(size.x * 0.5, size.y * 0.5)
	for p in shape:
		out.append(p + Vector2(signf(center.x - p.x) * d, signf(center.y - p.y) * d))
	return out


func _name_color() -> Color:
	return _theme(&"danger") if team == TEAM_ENEMY else _theme(&"text")


func _theme(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


func _theme_k(cname: StringName) -> int:
	return get_theme_constant(cname, HymnThemeBuilder.PALETTE_TYPE)
