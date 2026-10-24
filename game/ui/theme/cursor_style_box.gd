@tool
class_name CursorStyleBox
extends StyleBox
## The menu cursor (docs/kb/art/ui.md §3, with ADR 0033's flair): the focused row's raised fill,
## lit from the left like a lamp held at the row's start and fading toward the right, a focus wash
## over the first half, a 2 px gold frame on the small tide-notch, a soft focus glow outside it, and
## a short focus "wick" bar at the left edge. Every number is an export so hymn_theme.tres owns it.

@export var fill := Color(0.07, 0.23, 0.4, 0.85)
## The fill's alpha at the right end, as a fraction of `fill`'s.
@export var fill_fade := 0.35
@export var wash := Color(0.44, 0.88, 0.85, 0.22)
## How far across the row the wash reaches, as a fraction of its width.
@export var wash_span := 0.55
@export var frame_color := Color(0.85, 0.71, 0.35, 1.0)
@export var frame_px := 2.0
@export var glow_color := Color(0.44, 0.88, 0.85, 0.35)
@export var glow_px := 6.0
@export var chamfer_px := 6.0
@export var wick_color := Color(0.44, 0.88, 0.85, 0.9)
@export var wick_px := 3.0
@export var wick_inset_px := 6.0


func _draw(ci: RID, rect: Rect2) -> void:
	var c := minf(chamfer_px, minf(rect.size.x, rect.size.y) * 0.5)
	_glow(ci, rect, c)
	var pts := TideNotchStyleBox.notch_polygon(rect, c, 0.0)
	var faded := Color(fill, fill.a * fill_fade)
	var cols := PackedColorArray()
	for p in pts:
		cols.append(fill.lerp(faded, clampf((p.x - rect.position.x) / maxf(rect.size.x, 1.0), 0.0, 1.0)))
	RenderingServer.canvas_item_add_polygon(ci, pts, cols)
	var w := rect.size.x * wash_span
	if w > c and wash.a > 0.0:
		var clear := Color(wash, 0.0)
		var top := rect.position.y + frame_px
		var bottom := rect.end.y - frame_px
		var x0 := rect.position.x + frame_px
		var quad := PackedVector2Array(
			[
				Vector2(x0, top + c),
				Vector2(x0 + c, top),
				Vector2(x0 + w, top),
				Vector2(x0 + w, bottom),
				Vector2(x0, bottom)
			]
		)
		RenderingServer.canvas_item_add_polygon(ci, quad, PackedColorArray([wash, wash, clear, clear, wash]))
	var loop := TideNotchStyleBox.notch_polygon(rect, c, frame_px * 0.5)
	loop.append(loop[0])
	RenderingServer.canvas_item_add_polyline(ci, loop, PackedColorArray([frame_color]), frame_px, false)
	if wick_px > 0.0 and rect.size.y > wick_inset_px * 2.0:
		var wx := rect.position.x + frame_px + wick_inset_px
		var wick := Rect2(
			wx, rect.position.y + wick_inset_px + c * 0.5, wick_px, rect.size.y - wick_inset_px * 2.0 - c * 0.5
		)
		RenderingServer.canvas_item_add_rect(ci, wick, wick_color)


func _get_draw_rect(rect: Rect2) -> Rect2:
	return rect.grow(glow_px)


## A soft glow outside the frame: a few outlines stepping outward, each fainter.
func _glow(ci: RID, rect: Rect2, c: float) -> void:
	if glow_px <= 0.0 or glow_color.a <= 0.0:
		return
	var rings := 3
	for i in rings:
		var d := glow_px * float(i + 1) / rings
		var loop := TideNotchStyleBox.notch_polygon(rect.grow(d), c + d * (sqrt(2.0) - 1.0), 0.0)
		loop.append(loop[0])
		var a := glow_color.a * (1.0 - float(i) / rings) * 0.6
		RenderingServer.canvas_item_add_polyline(
			ci, loop, PackedColorArray([Color(glow_color, a)]), glow_px / rings, false
		)
