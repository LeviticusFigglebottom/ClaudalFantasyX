class_name StatusGlyph
extends Control
## A status icon drawn as vector strokes on a 48-unit grid (docs/kb/art/ui.md §8): a flat tint
## backing at 0.35 behind a 2-unit stroke. Every status has its own SHAPE, so none depends on
## hue (colorblind-safe, docs/kb/tech/ui.md § Status glyphs). Polarity is coded twice: buffs use
## ui_focus on a round backing, ailments ui_danger on a diamond backing. Original glyphs.

const GRID := 48.0
const STROKE := 2.0
const TINT_ALPHA := 0.35
const SPIRAL_STEPS := 24
const BUFFS: Array[StringName] = [&"haste", &"shell", &"protect", &"regen", &"reflect"]
## Every status with a dedicated shape (the rest fall back to a plain diamond).
const DRAWN: Array[StringName] = [
	&"poison",
	&"sleep",
	&"silence",
	&"darkness",
	&"petrify",
	&"slow",
	&"haste",
	&"stop",
	&"berserk",
	&"confuse",
	&"doom",
	&"zombie",
	&"shell",
	&"protect",
	&"reflect",
	&"regen",
	&"armor_break",
	&"mental_break",
	&"power_break",
	&"magic_break",
	&"provoke",
	&"rooted",
]

var status: StringName = &""
## Regen on a Zombie harms instead of healing: drawn as a falling bar with ailment polarity.
var inverted := false


func _init(sid: StringName = &"", is_inverted: bool = false) -> void:
	status = sid
	inverted = is_inverted
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func set_status(sid: StringName, is_inverted: bool = false) -> void:
	status = sid
	inverted = is_inverted
	queue_redraw()


static func is_buff(sid: StringName) -> bool:
	return BUFFS.has(sid)


## True when `sid` has its own glyph (tests assert all 21 statuses do).
static func has_shape(sid: StringName) -> bool:
	return DRAWN.has(sid)


## The statuses whose effect flips on this combatant (Regen under Zombie).
static func inverted_for(c: BattleCombatant, sid: StringName) -> bool:
	return sid == &"regen" and c != null and c.has_status(&"zombie")


func shows_buff() -> bool:
	return is_buff(status) and not inverted


func _draw() -> void:
	if status == &"":
		return
	var col := get_theme_color(&"focus" if shows_buff() else &"danger", HymnThemeBuilder.PALETTE_TYPE)
	var s := minf(size.x, size.y) / GRID
	var w := maxf(STROKE * s * 1.5, 1.0)
	var p := func(x: float, y: float) -> Vector2: return Vector2(x, y) * s
	_draw_backing(Color(col, TINT_ALPHA))
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
			_regen_glyph(p, col, w)
		&"armor_break", &"power_break", &"mental_break", &"magic_break":
			_break_glyph(p, col, w)
		_:
			_ailment_glyph(p, col, w, s)


## The M1-CMB-02 statuses: each is a distinct silhouette, never a recolor of another glyph.
func _ailment_glyph(p: Callable, col: Color, w: float, s: float) -> void:
	match status:
		&"petrify":
			# A weathered stone block with two strata lines (Breaks own the crack stroke).
			var rock := PackedVector2Array(
				[p.call(14, 35), p.call(11, 22), p.call(19, 12), p.call(32, 13), p.call(37, 25), p.call(31, 36)]
			)
			_poly(rock, col, w, true)
			draw_line(p.call(13, 21), p.call(35, 20), col, w)
			draw_line(p.call(13, 28), p.call(35, 30), col, w)
		&"berserk":
			# Bared teeth: a hard zigzag.
			var teeth := PackedVector2Array(
				[p.call(11, 33), p.call(17, 15), p.call(24, 33), p.call(31, 15), p.call(37, 33)]
			)
			_poly(teeth, col, w)
		&"confuse":
			# An inward spiral (current pulled in circles).
			var pts := PackedVector2Array()
			for i in SPIRAL_STEPS + 1:
				var t := float(i) / SPIRAL_STEPS
				var a := t * TAU * 1.5
				pts.append(p.call(24, 24) + Vector2(cos(a), sin(a)) * (3.0 + 10.0 * t) * s)
			_poly(pts, col, w)
		&"doom":
			# An hourglass with its two caps.
			var glass := PackedVector2Array(
				[p.call(16, 13), p.call(32, 13), p.call(24, 24), p.call(32, 35), p.call(16, 35), p.call(24, 24)]
			)
			_poly(glass, col, w, true)
			draw_line(p.call(13, 12), p.call(35, 12), col, w)
			draw_line(p.call(13, 36), p.call(35, 36), col, w)
		&"zombie":
			# Regen's cross turned on its side: healing comes back as harm.
			draw_line(p.call(15, 15), p.call(33, 33), col, w)
			draw_line(p.call(33, 15), p.call(15, 33), col, w)
			draw_circle(p.call(24, 24), 3 * s, col)
		&"reflect":
			# A mirror line and the spell's bounce off it.
			draw_line(p.call(33, 11), p.call(33, 37), col, w)
			_poly(PackedVector2Array([p.call(12, 14), p.call(30, 24), p.call(12, 34)]), col, w)
			_poly(PackedVector2Array([p.call(12, 28), p.call(12, 34), p.call(18, 34)]), col, w)
		&"provoke":
			# A fish hook: the lure the provoked must strike.
			draw_line(p.call(28, 10), p.call(28, 28), col, w)
			draw_arc(p.call(22, 28), 6 * s, 0.0, PI, 10, col, w)
			_poly(PackedVector2Array([p.call(16, 28), p.call(16, 22), p.call(20, 25)]), col, w)
			draw_arc(p.call(28, 9), 2 * s, 0.0, TAU, 8, col, w)
		&"rooted":
			# Act II (M4-A2P-020/083): a stake held by roots, three spreading from its foot and one curled round it.
			draw_line(p.call(24, 10), p.call(24, 27), col, w)
			_poly(PackedVector2Array([p.call(24, 27), p.call(19, 30), p.call(15, 31), p.call(11, 36)]), col, w)
			_poly(PackedVector2Array([p.call(24, 27), p.call(29, 30), p.call(33, 31), p.call(37, 36)]), col, w)
			_poly(PackedVector2Array([p.call(24, 27), p.call(23, 32), p.call(25, 38)]), col, w)
			draw_arc(p.call(24, 19), 6 * s, PI * 0.1, PI * 0.9, 10, col, w)
		_:
			_poly(PackedVector2Array([p.call(24, 12), p.call(36, 24), p.call(24, 36), p.call(12, 24)]), col, w, true)


func _regen_glyph(p: Callable, col: Color, w: float) -> void:
	if inverted:
		# Inverted Regen (Zombie): the cross loses its upright and points down.
		draw_line(p.call(13, 20), p.call(35, 20), col, w)
		_poly(PackedVector2Array([p.call(16, 27), p.call(24, 35), p.call(32, 27)]), col, w)
		draw_line(p.call(24, 20), p.call(24, 35), col, w)
		return
	draw_line(p.call(24, 13), p.call(24, 35), col, w)
	draw_line(p.call(13, 24), p.call(35, 24), col, w)


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


## Buffs sit on a disc, ailments on a diamond: polarity without hue.
func _draw_backing(tint: Color) -> void:
	var c := size * 0.5
	var r := minf(size.x, size.y) * 0.5
	if shows_buff():
		draw_circle(c, r, tint)
		return
	draw_colored_polygon(
		PackedVector2Array([c + Vector2(0, -r), c + Vector2(r, 0), c + Vector2(0, r), c + Vector2(-r, 0)]), tint
	)


func _shield(p: Callable) -> PackedVector2Array:
	return PackedVector2Array([p.call(14, 13), p.call(34, 13), p.call(34, 25), p.call(24, 36), p.call(14, 25)])


func _poly(pts: PackedVector2Array, col: Color, w: float, closed: bool = false) -> void:
	var line := pts.duplicate()
	if closed:
		line.append(pts[0])
	draw_polyline(line, col, w, true)
