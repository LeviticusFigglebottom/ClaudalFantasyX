class_name OrnamentRule
extends Control
## A gold rule under a title or page header (ADR 0033): a lamp-node diamond at its start, then a
## 1 px gold line that fades out toward its end, where a small hollow diamond closes it. With
## `centered` the line fades out both ways from a central diamond (for centred titles). Colors and
## metrics come from the theme (ornament_gold, line_px, ornament_node_px, ornament_gap_px); the
## control's own rect is the rule's extent, its vertical middle is the line.

## True: a centred rule with the node in the middle, fading both ways.
var centered := false


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED or what == NOTIFICATION_RESIZED:
		queue_redraw()


func _draw() -> void:
	var gold := get_theme_color(&"ornament_gold", HymnThemeBuilder.PALETTE_TYPE)
	var line := float(get_theme_constant(&"line_px", HymnThemeBuilder.PALETTE_TYPE))
	var node := float(get_theme_constant(&"ornament_node_px", HymnThemeBuilder.PALETTE_TYPE))
	var gap := float(get_theme_constant(&"ornament_gap_px", HymnThemeBuilder.PALETTE_TYPE))
	var y := floorf(size.y * 0.5) + line * 0.5
	var clear := Color(gold, 0.0)
	if centered:
		var mid := floorf(size.x * 0.5)
		_fade(Vector2(mid - node - gap, y), Vector2(0.0, y), gold, clear, line)
		_fade(Vector2(mid + node + gap, y), Vector2(size.x, y), gold, clear, line)
		draw_colored_polygon(SwellRingView.diamond(Vector2(mid, y), node), gold)
		return
	draw_colored_polygon(SwellRingView.diamond(Vector2(node, y), node), gold)
	var end := Vector2(size.x - node, y)
	_fade(Vector2(node * 2.0 + gap, y), end - Vector2(node + gap, 0.0), gold, Color(gold, gold.a * 0.25), line)
	var tail := SwellRingView.diamond(end, node * 0.6)
	tail.append(tail[0])
	draw_polyline(tail, Color(gold, gold.a * 0.5), line)


func _fade(from: Vector2, to: Vector2, a: Color, b: Color, width: float) -> void:
	draw_polyline_colors(PackedVector2Array([from, to]), PackedColorArray([a, b]), width)
