class_name SwellRingView
extends Control
## A hero's Swell input on screen (M1-CMB-04; every kind since M2-UI-03): the panel where the
## command menu was, its title (the technique), the figure for the input's kind, one pip per grade
## below it, the last grade in words (top right), and the hint. A view over a SwellInput: it draws
## the input's state and never decides anything; BattleController drives the input and reads its
## result.
##
## Figures, one per kind:
##   timing_ring  Rhen: a lantern that flares on each beat and a ring closing on it (drawn here).
##   chant        Asha: the phrase's notes scroll onto a line (SwellChantDraw).
##   brace        Toma: the blows and the counter on a track, and the hold (SwellBraceDraw).
##   glyph        Ysolde: the glyph's strokes and the window's time left (SwellGlyphDraw).
## Grades read by shape, not hue alone: the best grade (perfect, swift) is a filled diamond with a
## halo, a good one (good, braced, traced) a filled diamond, a miss a cross. A kind's final step
## (the brace's counter, the glyph's swift) waits as a hollow circle, not a diamond. Reduced
## motion keeps the timing but drops the lamp's flicker.

## The input kinds the HUD can draw (M2-CMB-01, M2-UI-03). The HUD shows a Swell gauge, and offers
## Swell, only to a hero whose input is drawn.
const DRAWN_KINDS: Array[StringName] = [
	SwellInput.KIND_TIMING_RING, SwellInput.KIND_CHANT, SwellInput.KIND_BRACE, SwellInput.KIND_GLYPH
]
## Hint loc keys per kind: [open, locked]. "Locked" drops Cancel once a step is graded.
const HINT_KEYS := {
	SwellInput.KIND_TIMING_RING: ["HUD_SWELL_RING_HINT", "HUD_SWELL_RING_HINT_LOCKED"],
	SwellInput.KIND_CHANT: ["HUD_SWELL_CHANT_HINT", "HUD_SWELL_CHANT_HINT_LOCKED"],
	SwellInput.KIND_BRACE: ["HUD_SWELL_BRACE_HINT", "HUD_SWELL_BRACE_HINT_LOCKED"],
	SwellInput.KIND_GLYPH: ["HUD_SWELL_GLYPH_HINT", "HUD_SWELL_GLYPH_HINT_LOCKED"],
}
## Grade loc keys and the palette role each grade's word is drawn in.
const GRADE_KEYS := {
	SwellInput.GRADE_PERFECT: "HUD_SWELL_GRADE_PERFECT",
	SwellInput.GRADE_GOOD: "HUD_SWELL_GRADE_GOOD",
	SwellBrace.GRADE_BRACED: "HUD_SWELL_GRADE_BRACED",
	SwellGlyph.GRADE_TRACED: "HUD_SWELL_GRADE_TRACED",
	SwellGlyph.GRADE_SWIFT: "HUD_SWELL_GRADE_SWIFT",
	SwellInput.GRADE_MISS: "HUD_SWELL_GRADE_MISS",
}
## The best grade of each step, drawn with the halo.
const BEST_GRADES: Array[StringName] = [SwellInput.GRADE_PERFECT, SwellGlyph.GRADE_SWIFT]

var ring: SwellInput
var reduced_motion := false

var _m: Dictionary = {}
## Draws the figure and pips above the panel background (a Control draws under its children).
var _canvas: Control
var _title: Label
var _hint: Label
## The timing assist's tag (M2-UI-01), top left beside the figure; hidden while the assist is off.
var _assist: Label
## The last grade in words (M2-UI-03), top right; empty until a step is graded.
var _callout: Label
## A kind's state in words under its figure (the brace's hold); empty for the others.
var _status: Label
## The action the left mouse button stands for while it is down (&"" when up, or pressed before
## this input opened, so the click that chose the target never plays a step).
var _pointer_action: StringName = &""


func _ready() -> void:
	_m = HudLayout.section(&"swell_ring")
	HudLayout.place(self, _m)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var bg := Panel.new()
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	_canvas = Control.new()
	_canvas.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_canvas.set_anchors_preset(Control.PRESET_FULL_RECT)
	_canvas.draw.connect(_draw_input)
	add_child(_canvas)
	var title_h := metric("title_height")
	var hint_h := metric("hint_height")
	_title = _label(&"HeaderLabel", Rect2(0, 0, size.x, title_h))
	_hint = _label(&"HelpLabel", Rect2(0, size.y - hint_h, size.x, hint_h))
	var pad := metric("pad")
	var side := Vector2(metric("assist_width"), metric("assist_height"))
	_assist = _label(&"DimLabel", Rect2(Vector2(pad, title_h), side))
	_assist.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	_assist.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_assist.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_assist.visible = false
	_callout = _label(&"MenuLabel", Rect2(Vector2(size.x - pad - side.x, title_h), side))
	_callout.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_callout.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	var status_h := metric("status_height")
	_status = _label(&"DimLabel", Rect2(0, metric("status_y"), size.x, status_h))
	visible = false


## True when the HUD draws swell.json input row `input`.
static func draws(input: Dictionary) -> bool:
	return DRAWN_KINDS.has(StringName(str(input.get("kind", ""))))


## True when the HUD draws hero `hero_id`'s input (the live swell.json).
static func draws_hero(hero_id: StringName) -> bool:
	return draws(BattleSwell.input_row_of(BattleSwell.load_config(), hero_id))


## The hint's loc key for an input of `kind`: what to press, with Cancel until `locked` (a step
## graded). Unknown kinds fall back to the ring's.
static func hint_key(kind: StringName, locked: bool) -> String:
	var keys: Array = HINT_KEYS.get(kind, HINT_KEYS[SwellInput.KIND_TIMING_RING])
	return str(keys[1 if locked else 0])


## The loc key naming `grade` (any kind's grade; unknown ids read as a miss).
static func grade_key(grade: StringName) -> String:
	return str(GRADE_KEYS.get(grade, GRADE_KEYS[SwellInput.GRADE_MISS]))


## Shows `r` under the technique's name `title_text`, with `hint` (what to press) below.
func open(r: SwellInput, title_text: String, hint: String) -> void:
	ring = r
	_pointer_action = &""
	_title.text = title_text
	_hint.text = hint
	visible = true
	refresh()


## Redraws the input after its state changed (BattleController calls it after every tick and
## press), and the words that follow it: the last grade and the kind's status.
func refresh() -> void:
	_callout.text = tr(grade_key(ring.grades[-1])) if ring != null and not ring.grades.is_empty() else ""
	_callout.add_theme_color_override(&"font_color", color(_grade_role(_last_grade())))
	_status.text = _status_text()
	_canvas.queue_redraw()


## The mouse playing the open input (M2-UI-26): the left button's press becomes a Confirm press, or,
## for a kind played with directions (Asha's chant, Ysolde's glyph), the direction the click lies in
## from the figure's centre (Confirm within pointer.swell_centre_px of it, for hold to confirm);
## its release becomes the same action's release, so a held click holds (Toma's brace). Every other
## event comes back as it was. BattleController feeds the result to SwellInputKeys.
func pointer_event(event: InputEvent) -> InputEvent:
	var mb := event as InputEventMouseButton
	if mb == null or mb.button_index != MOUSE_BUTTON_LEFT or ring == null:
		return event
	var action := pointer_action_at(mb.position) if mb.pressed else _pointer_action
	if action == &"":
		return event
	_pointer_action = action if mb.pressed else &""
	var a := InputEventAction.new()
	a.action = action
	a.pressed = mb.pressed
	return a


## The ui_* action a left click at `at` (viewport coordinates) plays on the open input.
func pointer_action_at(at: Vector2) -> StringName:
	var used := ring.buttons_used() if ring != null else ([] as Array[StringName])
	var d := at - get_global_transform_with_canvas() * figure_center()
	var button := SwellInput.BUTTON_ACCEPT
	var centre := HudLayout.num(HudLayout.section(&"pointer"), "swell_centre_px")
	if not used.has(SwellInput.BUTTON_ACCEPT) and d.length() > centre:
		if absf(d.x) > absf(d.y):
			button = SwellInput.BUTTON_RIGHT if d.x > 0.0 else SwellInput.BUTTON_LEFT
		else:
			button = SwellInput.BUTTON_DOWN if d.y > 0.0 else SwellInput.BUTTON_UP
	return SwellInputKeys.BUTTONS.find_key(button) as StringName


func close() -> void:
	ring = null
	visible = false


func is_open() -> bool:
	return visible and ring != null


func set_hint(hint: String) -> void:
	_hint.text = hint


func hint_text() -> String:
	return _hint.text


## The last grade's word ("" before the first grade).
func callout_text() -> String:
	return _callout.text


## The kind's state in words under its figure ("" when the kind has none).
func status_text() -> String:
	return _status.text


## The timing assist's tag ("" hides it). BattleHud sets it from UiSettings.
func set_assist_text(text: String) -> void:
	_assist.text = text
	_assist.visible = text != ""


func assist_text() -> String:
	return _assist.text if _assist.visible else ""


## A swell_ring metric from battle_hud.json (the per-kind drawers read theirs here too).
func metric(key: String) -> float:
	return HudLayout.num(_m, key)


## A theme palette role's color.
func color(role: StringName) -> Color:
	return get_theme_color(role, HymnThemeBuilder.PALETTE_TYPE)


## The control the figure is drawn on (the per-kind drawers draw here).
func canvas() -> Control:
	return _canvas


## Where the figure is centred: the ring's centre, which every kind shares.
func figure_center() -> Vector2:
	return ring_center()


## How bright the lamp is now, 0..1: it peaks with each beat (time_to_peak 0) and fades over
## flare_sec either side, flickering a little unless motion is reduced.
func brightness() -> float:
	if ring == null:
		return 0.0
	var f := flare()
	var b := metric("lamp_rest") + (1.0 - metric("lamp_rest")) * f * f
	if not reduced_motion:
		var phase := ring.elapsed * metric("flicker_hz") * TAU
		b *= 1.0 - metric("flicker_amp") * 0.5 * (1.0 + sin(phase))
	return clampf(b, 0.0, 1.0)


## The beat's flare alone, 0..1: 1 at the peak, 0 from flare_sec either side (no rest, no flicker).
func flare() -> float:
	if ring == null:
		return 0.0
	return clampf(1.0 - absf(ring.time_to_peak()) / metric("flare_sec"), 0.0, 1.0)


## The lamp core's color at brightness `b`: from a dark ember (swell darkened, opaque) to swell,
## so at rest it reads warm rather than the panel's grey (M2-UI-08, art/ui.md §10.2).
func lamp_core(b: float) -> Color:
	var swell := color(&"swell")
	var ember := swell.darkened(1.0 - metric("lamp_core_value"))
	ember.a = 1.0
	return ember.lerp(swell, b)


## Radius of the closing ring: the outer edge when the beat opens, the lamp's rim at the peak.
func closing_radius() -> float:
	var lamp := metric("lamp_radius")
	var outer := metric("ring_radius")
	var timing := ring as SwellTimingRing
	if timing == null:
		return outer
	var approach := maxf(timing.peak_at * timing.beat_sec, 0.001)
	return lamp + (outer - lamp) * clampf(timing.time_to_peak() / approach, 0.0, 1.0)


func ring_center() -> Vector2:
	var y := metric("title_height") + metric("pad") + metric("ring_radius")
	return Vector2(size.x * 0.5, y)


## One pip per grade the input holds, centred on row `y`: graded steps by grade (draw_grade), the
## step waiting now in `focus`, later ones dim. With `final_round` the last step (a counter, a
## swift) waits as a circle, so it reads as the finish rather than one more step.
func draw_pips(y: float, final_round: bool) -> void:
	var px := metric("pip_px")
	var gap := metric("pip_gap")
	var count := ring.grade_count()
	var x0 := size.x * 0.5 - (count - 1) * gap * 0.5
	for i in count:
		var at := Vector2(x0 + i * gap, y + px)
		if i < ring.grades.size():
			draw_grade(at, px, ring.grades[i])
			continue
		var col := color(&"focus") if i == ring.grades.size() and not ring.is_done() else color(&"text_dim")
		if final_round and i == count - 1:
			_canvas.draw_arc(at, px, 0.0, TAU, 24, col, 1.0, true)
		else:
			outline(diamond(at, px), col, 1.0)


## A graded step's mark at `at`: the best grade filled `swell` with a gold halo, any other grade
## that earns power filled `focus`, a miss a `danger` cross.
func draw_grade(at: Vector2, px: float, grade: StringName) -> void:
	if BEST_GRADES.has(grade):
		_canvas.draw_colored_polygon(diamond(at, px), color(&"swell"))
		_canvas.draw_arc(at, px * metric("halo_scale"), 0.0, TAU, 24, color(&"focus_gold"), 1.0, true)
	elif grade != SwellInput.GRADE_MISS and GRADE_KEYS.has(grade):
		_canvas.draw_colored_polygon(diamond(at, px), color(&"focus"))
	else:
		draw_cross(at, px * metric("cross_scale"), color(&"danger"))


func draw_cross(at: Vector2, d: float, col: Color) -> void:
	var w := metric("cross_px")
	_canvas.draw_line(at + Vector2(-d, -d), at + Vector2(d, d), col, w, true)
	_canvas.draw_line(at + Vector2(-d, d), at + Vector2(d, -d), col, w, true)


static func diamond(at: Vector2, px: float) -> PackedVector2Array:
	return PackedVector2Array([at + Vector2(0, -px), at + Vector2(px, 0), at + Vector2(0, px), at + Vector2(-px, 0)])


## The unit vector for a SwellInput direction button (Vector2.ZERO for any other button).
static func direction(button: StringName) -> Vector2:
	match button:
		SwellInput.BUTTON_UP:
			return Vector2.UP
		SwellInput.BUTTON_DOWN:
			return Vector2.DOWN
		SwellInput.BUTTON_LEFT:
			return Vector2.LEFT
		SwellInput.BUTTON_RIGHT:
			return Vector2.RIGHT
	return Vector2.ZERO


## A triangle centred on `at` pointing along unit `dir`, `s` from the centre to the tip.
static func arrow(at: Vector2, dir: Vector2, s: float) -> PackedVector2Array:
	var side := Vector2(-dir.y, dir.x)
	return PackedVector2Array([at + dir * s, at - dir * s * 0.6 + side * s * 0.8, at - dir * s * 0.6 - side * s * 0.8])


## Draws closed polygon `pts` as an outline.
func outline(pts: PackedVector2Array, col: Color, width: float) -> void:
	var closed := pts.duplicate()
	closed.append(pts[0])
	_canvas.draw_polyline(closed, col, width, true)


## The pip row's y (under the figure), shared by every kind.
func pips_y() -> float:
	return ring_center().y + metric("ring_radius") + metric("pad")


func _draw_input() -> void:
	if ring == null:
		return
	match ring.kind:
		SwellInput.KIND_CHANT:
			SwellChantDraw.draw(self, ring as SwellChant)
		SwellInput.KIND_BRACE:
			SwellBraceDraw.draw(self, ring as SwellBrace)
		SwellInput.KIND_GLYPH:
			SwellGlyphDraw.draw(self, ring as SwellGlyph)
		_:
			_draw_ring()


func _draw_ring() -> void:
	var c := ring_center()
	var lamp := metric("lamp_radius")
	var b := brightness()
	var swell := color(&"swell")
	# The halo follows the flare only, so no grey ring shows between beats (M2-UI-08).
	var glow := swell
	glow.a = flare() * metric("glow_alpha")
	_canvas.draw_circle(c, lamp + metric("glow_radius") * b, glow)
	_canvas.draw_circle(c, lamp, lamp_core(b))
	_canvas.draw_arc(c, lamp, 0.0, TAU, 48, color(&"focus_gold"), metric("target_px"), true)
	if not ring.is_done():
		var col := color(&"focus")
		col.a *= clampf(metric("ring_min_alpha") + b, 0.0, 1.0)
		_canvas.draw_arc(c, closing_radius(), 0.0, TAU, 64, col, metric("ring_px"), true)
	draw_pips(pips_y(), false)


func _last_grade() -> StringName:
	return ring.grades[-1] if ring != null and not ring.grades.is_empty() else &""


func _grade_role(grade: StringName) -> StringName:
	if BEST_GRADES.has(grade):
		return &"swell"
	if grade == SwellInput.GRADE_MISS or grade == &"":
		return &"danger"
	return &"focus"


func _status_text() -> String:
	var brace := ring as SwellBrace
	if brace == null or brace.is_done():
		return ""
	return tr("HUD_SWELL_BRACE_HOLDING") if brace.holding else tr("HUD_SWELL_BRACE_NOT_HOLDING")


func _label(variation: StringName, r: Rect2) -> Label:
	var l := Label.new()
	l.theme_type_variation = variation
	l.position = r.position
	l.size = r.size
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l
