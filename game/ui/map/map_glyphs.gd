class_name MapGlyphs
extends RefCounted
## The zone map's marks (M2-UI-18), drawn on any CanvasItem: a glyph per kind of place, the
## objective's marker and the player's arrow. All original vector shapes in the world's own
## motifs (lamps, nets, moorings), told apart by silhouette, not hue alone (art/ui.md §8, §9):
##   shrine  a lamp flame (a filled teardrop)        shop  a crate (a square with a strap)
##   inn     a crescent moon (rest)                    talk  three dots in a row (voices)
##   path    a raised chevron over a step              door  a tall door with its ring
##   pool    two ripples                               dock  a jetty (a plank on three posts)
##   home    a house (a gable over a wall)
##   shrine_dark  the lamp flame hollow: an Order shrine gone dark for heretics (MapModel sets it; Act II)
## Every glyph sits on a dark backing disc, so it reads on sea, sand and roofs alike. The objective
## is a hollow gold diamond with a ring that swells outward from it; the player is a filled arrow
## pointing the way they face. Sizes come from zone_map_menu.json, colours from the theme.

const KIND_SHRINE := &"shrine"
const KIND_SHOP := &"shop"
const KIND_INN := &"inn"
const KIND_TALK := &"talk"
const KIND_PATH := &"path"
const KIND_DOOR := &"door"
const KIND_POOL := &"pool"
const KIND_DOCK := &"dock"
const KIND_HOME := &"home"
## Not authored in zone_maps.json: MapModel turns an `order` shrine into it once the party are heretics.
const KIND_SHRINE_DARK := &"shrine_dark"
const KINDS: Array[StringName] = [
	KIND_SHRINE, KIND_SHOP, KIND_INN, KIND_TALK, KIND_PATH, KIND_DOOR, KIND_POOL, KIND_DOCK, KIND_HOME
]
## Points along a curved stroke (ripples, the crescent).
const CURVE_POINTS := 9


## Draws the glyph for `kind` centred on `at`, in a backing disc of radius `px`.
static func draw_poi(
	ci: CanvasItem, kind: StringName, at: Vector2, px: float, line: float, ink: Color, back: Color, edge: Color
) -> void:
	ci.draw_circle(at, px, back)
	ci.draw_arc(at, px, 0.0, TAU, CURVE_POINTS * 4, edge, 1.0, true)
	var u := px * 0.5  # the glyph's half-size inside the disc
	match kind:
		KIND_SHRINE:
			ci.draw_colored_polygon(_flame(at, u), ink)
		KIND_SHRINE_DARK:
			var hollow := _flame(at, u)
			hollow.append(hollow[0])
			ci.draw_polyline(hollow, ink, line, true)
		KIND_SHOP:
			var r := Rect2(at - Vector2(u, u * 0.8), Vector2(u * 2.0, u * 1.6))
			ci.draw_rect(r, ink, false, line)
			ci.draw_line(Vector2(r.position.x, at.y - u * 0.15), Vector2(r.end.x, at.y - u * 0.15), ink, line)
		KIND_INN:
			ci.draw_circle(at, u * 0.95, ink)
			ci.draw_circle(at + Vector2(u * 0.5, -u * 0.3), u * 0.8, back)
		KIND_TALK:
			for k in [-1, 0, 1]:
				ci.draw_circle(at + Vector2(k * u * 0.75, 0.0), u * 0.26, ink)
		KIND_PATH:
			ci.draw_polyline(
				PackedVector2Array(
					[at + Vector2(-u * 0.8, u * 0.1), at + Vector2(0.0, -u * 0.75), at + Vector2(u * 0.8, u * 0.1)]
				),
				ink,
				line,
				true
			)
			ci.draw_line(at + Vector2(-u * 0.6, u * 0.7), at + Vector2(u * 0.6, u * 0.7), ink, line, true)
		KIND_DOOR:
			ci.draw_rect(Rect2(at - Vector2(u * 0.6, u), Vector2(u * 1.2, u * 2.0)), ink, false, line)
			ci.draw_circle(at + Vector2(u * 0.25, u * 0.1), line, ink)
		KIND_POOL:
			for k in [-1, 1]:
				ci.draw_polyline(_ripple(at + Vector2(0.0, k * u * 0.4), u), ink, line, true)
		KIND_DOCK:
			ci.draw_line(at + Vector2(-u, -u * 0.35), at + Vector2(u, -u * 0.35), ink, line * 1.5, true)
			for k in [-1, 0, 1]:
				ci.draw_line(at + Vector2(k * u * 0.8, -u * 0.35), at + Vector2(k * u * 0.8, u * 0.8), ink, line, true)
		KIND_HOME:
			var house := PackedVector2Array(
				[
					at + Vector2(-u * 0.8, u * 0.85),
					at + Vector2(-u * 0.8, -u * 0.05),
					at + Vector2(0.0, -u * 0.9),
					at + Vector2(u * 0.8, -u * 0.05),
					at + Vector2(u * 0.8, u * 0.85),
					at + Vector2(-u * 0.8, u * 0.85),
				]
			)
			ci.draw_polyline(house, ink, line, true)
		_:
			ci.draw_circle(at, u * 0.4, ink)


## A gentle S-wave `u` either side of `at`.
static func _ripple(at: Vector2, u: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	for i in CURVE_POINTS:
		var t := float(i) / (CURVE_POINTS - 1)
		out.append(at + Vector2((t * 2.0 - 1.0) * u, sin(t * TAU) * u * 0.22))
	return out


## The objective's marker: a gold diamond of half-diagonal `px` and, while `pulse` runs 0..1, a
## second diamond that swells by `swell` px and fades. A held marker (reduced motion) passes a
## negative pulse and shows the diamond alone. `framing`: a hollow ring around its place's glyph
## (on the map); else a small solid badge, a dark diamond with a gold edge and core (the legend
## and the objective line).
static func draw_objective(
	ci: CanvasItem,
	at: Vector2,
	px: float,
	line: float,
	gold: Color,
	back: Color,
	pulse: float,
	swell: float,
	framing: bool = false
) -> void:
	if pulse >= 0.0:
		var ring := SwellRingView.diamond(at, px + swell * pulse)
		ring.append(ring[0])
		ci.draw_polyline(ring, Color(gold, gold.a * (1.0 - pulse)), line * 0.5, true)
	var shape := SwellRingView.diamond(at, px)
	if not framing:
		ci.draw_colored_polygon(shape, back)
	shape.append(shape[0])
	if framing:
		ci.draw_polyline(shape, back, line * 2.0, true)  # a dark edge, so the gold reads on sand too
	ci.draw_polyline(shape, gold, line, true)
	if not framing:
		ci.draw_colored_polygon(SwellRingView.diamond(at, px * 0.3), gold)


## The player's arrow at `at`, pointing along `dir` (a map direction), `px` from tip to tail,
## filled `fill` inside an `outline` of `edge` px.
static func draw_player(
	ci: CanvasItem, at: Vector2, dir: Vector2, px: float, edge: float, fill: Color, outline: Color
) -> void:
	var f := dir.normalized() if not dir.is_zero_approx() else Vector2.UP
	var side := Vector2(-f.y, f.x)
	var arrow := PackedVector2Array(
		[
			at + f * px * 0.6,
			at - f * px * 0.4 + side * px * 0.42,
			at - f * px * 0.18,
			at - f * px * 0.4 - side * px * 0.42
		]
	)
	var closed := arrow.duplicate()
	closed.append(arrow[0])
	ci.draw_polyline(closed, outline, edge * 2.0, true)
	ci.draw_colored_polygon(arrow, fill)


## The shrine's lamp flame: a teardrop, round end down, its tip up.
static func _flame(at: Vector2, u: float) -> PackedVector2Array:
	var flame := PackedVector2Array()
	for i in CURVE_POINTS:
		var a := PI * i / (CURVE_POINTS - 1)
		flame.append(at + Vector2(cos(a) * u * 0.62, u * 0.35 + sin(a) * u * 0.62))
	flame.append(at + Vector2(0.0, -u * 1.15))
	return flame
