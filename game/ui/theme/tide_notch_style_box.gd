@tool
class_name TideNotchStyleBox
extends StyleBox
## The Hymn panel (docs/kb/art/ui.md §1 and §3): a vertical deep-blue gradient, a sheen along
## the top edge, a 1 px inner white rule, a 1 px gold frame, and the "tide-notch": 45° chamfers
## on the top-left and bottom-right corners only, each carrying one gold lamp-node.
## Every number is an export so hymn_theme.tres (generated from game/data/ui/theme.json) owns it.

@export var fill_top := Color(0.04, 0.14, 0.26, 0.8)
@export var fill_bottom := Color(0.02, 0.09, 0.17, 0.86)
@export var sheen_color := Color(0.07, 0.23, 0.4, 0.25)
@export var sheen_px := 24.0
@export var frame_color := Color(0.85, 0.71, 0.35, 0.85)
@export var rule_color := Color(0.95, 0.96, 0.98, 0.18)
@export var rule_inset_px := 3.0
@export var line_px := 1.0
@export var chamfer_px := 10.0
@export var draw_rule := true
@export var draw_lamp_nodes := true
@export var lamp_node_px := 3.0
@export var lamp_node_glow_px := 4.0
@export var lamp_node_glow := Color(0.85, 0.71, 0.35, 0.3)
## The lamp-node glow is faked with concentric circles fading outward.
@export var lamp_node_glow_rings := 3
@export var lamp_node_glow_falloff := 0.6


func _draw(to_canvas_item: RID, rect: Rect2) -> void:
	var c := minf(chamfer_px, minf(rect.size.x, rect.size.y) * 0.5)
	var outline := notch_polygon(rect, c, 0.0)
	_draw_fill(to_canvas_item, rect, outline)
	_draw_sheen(to_canvas_item, rect, c)
	if draw_rule:
		var inset := rule_inset_px + line_px * 0.5
		_line_loop(to_canvas_item, notch_polygon(rect, c, inset), rule_color)
	_line_loop(to_canvas_item, notch_polygon(rect, c, line_px * 0.5), frame_color)
	if draw_lamp_nodes and c > 0.0:
		_lamp_node(to_canvas_item, rect.position + Vector2(c, c) * 0.5)
		_lamp_node(to_canvas_item, rect.end - Vector2(c, c) * 0.5)


func _get_draw_rect(rect: Rect2) -> Rect2:
	return rect


## The tide-notch outline of `rect` with chamfer `c`, offset inward by `inset` (clockwise from
## the top-left chamfer). A 45° edge offset by d moves its end points by d·(√2 − 1) along the axes.
static func notch_polygon(rect: Rect2, c: float, inset: float) -> PackedVector2Array:
	var a := rect.position + Vector2(inset, inset)
	var b := rect.end - Vector2(inset, inset)
	var k := c + inset * (sqrt(2.0) - 1.0) if c > 0.0 else 0.0
	var pts := PackedVector2Array()
	if c > 0.0:
		pts.append(Vector2(a.x, rect.position.y + k))
		pts.append(Vector2(rect.position.x + k, a.y))
	else:
		pts.append(a)
	pts.append(Vector2(b.x, a.y))
	if c > 0.0:
		pts.append(Vector2(b.x, rect.end.y - k))
		pts.append(Vector2(rect.end.x - k, b.y))
	else:
		pts.append(b)
	pts.append(Vector2(a.x, b.y))
	return pts


func _draw_fill(ci: RID, rect: Rect2, pts: PackedVector2Array) -> void:
	var colors := PackedColorArray()
	for p in pts:
		colors.append(fill_top.lerp(fill_bottom, clampf((p.y - rect.position.y) / maxf(rect.size.y, 1.0), 0.0, 1.0)))
	RenderingServer.canvas_item_add_polygon(ci, pts, colors)


func _draw_sheen(ci: RID, rect: Rect2, c: float) -> void:
	var s := minf(sheen_px, rect.size.y)
	if s <= c or sheen_color.a <= 0.0:
		return
	var top := rect.position.y
	var clear := Color(sheen_color, 0.0)
	var pts := PackedVector2Array(
		[
			Vector2(rect.position.x, top + c),
			Vector2(rect.position.x + c, top),
			Vector2(rect.end.x, top),
			Vector2(rect.end.x, top + s),
			Vector2(rect.position.x, top + s),
		]
	)
	var colors := PackedColorArray([sheen_color.lerp(clear, c / s), sheen_color, sheen_color, clear, clear])
	RenderingServer.canvas_item_add_polygon(ci, pts, colors)


func _line_loop(ci: RID, pts: PackedVector2Array, color: Color) -> void:
	var loop := pts.duplicate()
	loop.append(pts[0])
	RenderingServer.canvas_item_add_polyline(ci, loop, PackedColorArray([color]), line_px, false)


func _lamp_node(ci: RID, center: Vector2) -> void:
	var r := lamp_node_px * 0.5
	var glow := lamp_node_glow
	var rings := maxi(lamp_node_glow_rings, 1)
	for i in rings:
		var t := float(rings - i) / rings
		var a := glow.a * (1.0 - t * lamp_node_glow_falloff)
		RenderingServer.canvas_item_add_circle(ci, center, r + lamp_node_glow_px * t, Color(glow, a))
	RenderingServer.canvas_item_add_circle(ci, center, r, Color(frame_color, 1.0))
