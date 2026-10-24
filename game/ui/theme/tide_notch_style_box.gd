@tool
class_name TideNotchStyleBox
extends StyleBox
## The Hymn panel (docs/kb/art/ui.md §1 and §3): a vertical deep-blue gradient, a sheen along
## the top edge, a 1 px inner white rule, a 1 px gold frame, and the "tide-notch": 45° chamfers
## on the top-left and bottom-right corners only, each carrying one gold lamp-node.
## Every number is an export so hymn_theme.tres (generated from game/data/ui/theme.json) owns it.
## Flair (ADR 0033, the human's direction for more character): a short gold glint under the top
## frame (lamplight caught on the surface), gold corner ticks on the two square corners, and on
## tall panels a few faint tide lines swaying across the bottom band (the water the panel sits in).
## All static and deterministic; none of it carries information, so all of it stays faint.

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
## The surface glint: a gold line just under the top frame, brightest in the middle, faded at both
## ends, spanning glint_span of the width (0 = off).
@export var glint_color := Color(0.85, 0.71, 0.35, 0.45)
@export var glint_span := 0.0
@export var glint_inset_px := 3.0
## Corner ticks: an L of gold on the top-right and bottom-left corners (0 = off).
@export var corner_tick_px := 0.0
@export var corner_tick_inset_px := 6.0
## Tide lines: faint sine strokes across the bottom band of panels at least tide_min_height_px tall.
@export var tide_color := Color(0.95, 0.96, 0.98, 0.07)
@export var tide_lines := 0
@export var tide_band_px := 44.0
@export var tide_amp_px := 3.0
@export var tide_wavelength_px := 120.0
@export var tide_min_height_px := 120.0


func _draw(to_canvas_item: RID, rect: Rect2) -> void:
	var c := minf(chamfer_px, minf(rect.size.x, rect.size.y) * 0.5)
	var outline := notch_polygon(rect, c, 0.0)
	_draw_fill(to_canvas_item, rect, outline)
	_draw_sheen(to_canvas_item, rect, c)
	_draw_tide(to_canvas_item, rect, c)
	if draw_rule:
		var inset := rule_inset_px + line_px * 0.5
		_line_loop(to_canvas_item, notch_polygon(rect, c, inset), rule_color)
	_line_loop(to_canvas_item, notch_polygon(rect, c, line_px * 0.5), frame_color)
	_draw_glint(to_canvas_item, rect, c)
	_draw_corner_ticks(to_canvas_item, rect)
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


## A gold line under the top frame: clear at both ends, glint_color in the middle.
func _draw_glint(ci: RID, rect: Rect2, c: float) -> void:
	if glint_span <= 0.0 or glint_color.a <= 0.0:
		return
	var w := (rect.size.x - c * 2.0) * glint_span
	if w <= 0.0:
		return
	var y := rect.position.y + glint_inset_px + line_px * 0.5
	var x0 := rect.position.x + (rect.size.x - w) * 0.5
	var clear := Color(glint_color, 0.0)
	var pts := PackedVector2Array([Vector2(x0, y), Vector2(x0 + w * 0.5, y), Vector2(x0 + w, y)])
	RenderingServer.canvas_item_add_polyline(ci, pts, PackedColorArray([clear, glint_color, clear]), line_px, false)


## Gold Ls on the two square corners, inset inside the inner rule.
func _draw_corner_ticks(ci: RID, rect: Rect2) -> void:
	if corner_tick_px <= 0.0:
		return
	var d := corner_tick_inset_px + line_px * 0.5
	var n := corner_tick_px
	var tr := Vector2(rect.end.x - d, rect.position.y + d)
	var bl := Vector2(rect.position.x + d, rect.end.y - d)
	var col := PackedColorArray([frame_color])
	for corner: Array in [[tr, Vector2(-n, 0), Vector2(0, n)], [bl, Vector2(n, 0), Vector2(0, -n)]]:
		var at: Vector2 = corner[0]
		var pts := PackedVector2Array([at + (corner[1] as Vector2), at, at + (corner[2] as Vector2)])
		RenderingServer.canvas_item_add_polyline(ci, pts, col, line_px, false)


## Faint sine strokes across the bottom band, each a little lower, longer-waved and offset.
func _draw_tide(ci: RID, rect: Rect2, c: float) -> void:
	if tide_lines <= 0 or rect.size.y < tide_min_height_px or tide_wavelength_px <= 0.0:
		return
	var steps := maxi(int(rect.size.x / 8.0), 2)
	var x0 := rect.position.x + line_px
	var x1 := rect.end.x - c - line_px
	for i in tide_lines:
		var t := float(i + 1) / float(tide_lines + 1)
		var y := rect.end.y - rule_inset_px * 2.0 - tide_band_px * (1.0 - t)
		var wave := tide_wavelength_px * (1.0 + 0.35 * i)
		var phase := 1.7 * i
		var col := Color(tide_color, tide_color.a * (0.5 + 0.5 * t))
		var pts := PackedVector2Array()
		var cols := PackedColorArray()
		for k in steps + 1:
			var x := lerpf(x0, x1, float(k) / steps)
			pts.append(Vector2(x, y + sin(x / wave * TAU + phase) * tide_amp_px))
			var edge := clampf(minf(x - x0, x1 - x) / (tide_wavelength_px * 0.5), 0.0, 1.0)
			cols.append(Color(col, col.a * edge))
		RenderingServer.canvas_item_add_polyline(ci, pts, cols, line_px, true)


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
