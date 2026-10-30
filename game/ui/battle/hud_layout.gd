class_name HudLayout
extends RefCounted
## Battle HUD metrics from game/data/ui/battle_hud.json (docs/kb/art/ui.md §6). Every UI number
## lives there; components read one section each: HudLayout.section(&"timeline").
##
## Rects are at the 1920x1080 reference (UiFrame.reference_size()). A section's optional "pin"
## names the screen edge or corner it keeps its margin to when the window is wider or taller than
## 16:9 (M2-UI-29): "top_left" (the default), "top", "top_right", "left", "center", "right",
## "bottom_left", "bottom", "bottom_right". "top" keeps the top margin and the horizontal centre.

const DATA_PATH := "res://game/data/ui/battle_hud.json"
## Anchor fractions (x, y) per pin.
const PINS := {
	"top_left": Vector2(0.0, 0.0),
	"top": Vector2(0.5, 0.0),
	"top_right": Vector2(1.0, 0.0),
	"left": Vector2(0.0, 0.5),
	"center": Vector2(0.5, 0.5),
	"right": Vector2(1.0, 0.5),
	"bottom_left": Vector2(0.0, 1.0),
	"bottom": Vector2(0.5, 1.0),
	"bottom_right": Vector2(1.0, 1.0),
}
const DEFAULT_PIN := "top_left"
## fit_label shrinks a single-line label's font to this share of its theme size at the least (the Lead's final-quality
## pass, 2026-10-29: long names at 130 % text). Past it the label's own overrun (an ellipsis) is the last resort.
const FIT_MIN_FONT_SCALE := 0.8

static var _cache: Dictionary = {}


static func data() -> Dictionary:
	if _cache.is_empty():
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
		if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("battle_hud")) != TYPE_DICTIONARY:
			push_error("HudLayout: could not read 'battle_hud' from %s" % DATA_PATH)
			return {}
		_cache = (parsed as Dictionary)["battle_hud"] as Dictionary
	return _cache


static func section(sname: StringName) -> Dictionary:
	return data().get(String(sname), {}) as Dictionary


static func rect_of(sec: Dictionary) -> Rect2:
	var r: Array = sec.get("rect", [0, 0, 0, 0])
	return Rect2(float(r[0]), float(r[1]), float(r[2]), float(r[3]))


## The anchor fractions of `sec`'s pin (DEFAULT_PIN when it names none).
static func pin_of(sec: Dictionary) -> Vector2:
	var p := str(sec.get("pin", DEFAULT_PIN))
	if not PINS.has(p):
		push_error("HudLayout: unknown pin '%s'" % p)
		p = DEFAULT_PIN
	return PINS[p] as Vector2


## Places `c` at its section's rect (1920x1080 reference coordinates), anchored to its pin: in a
## parent larger than the reference it keeps its margin to that edge (or stays centred on it).
## A Control grown past its rect by its content grows away from the pinned edge.
static func place(c: Control, sec: Dictionary) -> void:
	place_rect(c, rect_of(sec), pin_of(sec))


## Places `c` at `r` (reference coordinates) anchored at the fractions `pin` (PINS values).
static func place_rect(c: Control, r: Rect2, pin: Vector2) -> void:
	var shift := UiFrame.reference_size() * pin
	c.anchor_left = pin.x
	c.anchor_right = pin.x
	c.anchor_top = pin.y
	c.anchor_bottom = pin.y
	c.offset_left = r.position.x - shift.x
	c.offset_right = r.end.x - shift.x
	c.offset_top = r.position.y - shift.y
	c.offset_bottom = r.end.y - shift.y
	c.grow_horizontal = _grow(pin.x)
	c.grow_vertical = _grow(pin.y)


## Where `sec`'s rect lands in a parent of `parent_size` (place() puts it there), for code that
## positions or draws by hand.
static func pinned_rect(sec: Dictionary, parent_size: Vector2) -> Rect2:
	var r := rect_of(sec)
	return Rect2(r.position + (parent_size - UiFrame.reference_size()) * pin_of(sec), r.size)


## Makes `c` a reference-sized frame (1920x1080) anchored at `pin`: children at reference
## coordinates keep their margins to that corner, as place() does for one rect.
static func place_frame(c: Control, pin: String) -> void:
	place_rect(c, Rect2(Vector2.ZERO, UiFrame.reference_size()), PINS.get(pin, PINS[DEFAULT_PIN]) as Vector2)


static func num(sec: Dictionary, key: String) -> float:
	if not sec.has(key):
		push_error("HudLayout: missing metric '%s'" % key)
		return 0.0
	return float(sec[key])


static func _grow(fraction: float) -> Control.GrowDirection:
	if is_zero_approx(fraction):
		return Control.GROW_DIRECTION_END
	if is_equal_approx(fraction, 1.0):
		return Control.GROW_DIRECTION_BEGIN
	return Control.GROW_DIRECTION_BOTH


## M2-UI-28 (localisation readiness): makes `l`, a help or hint line sitting at the foot of its
## panel, wrap onto as many lines as its text needs and grow upward from that foot, so a longer
## language or a larger text size never runs it past the panel's side. A line that fits looks as
## it did (same rect, same alignment); only a longer one takes more lines, above, and a shorter
## text after it gives them back (a grown Control never shrinks on its own). Call it after
## placing `l`; returns `l`.
static func wrap_upward(l: Label) -> Label:
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.grow_vertical = Control.GROW_DIRECTION_BEGIN
	var h := l.size.y
	var foot := l.position.y + h
	var refit := func() -> void:
		var want := maxf(h, l.get_combined_minimum_size().y)
		if l.size.y != want:
			l.size = Vector2(l.size.x, want)
		if l.position.y != foot - l.size.y:
			l.position.y = foot - l.size.y
	l.minimum_size_changed.connect(refit)
	# A hidden label skips its minimum-size update, so a text set while hidden refits on its draw.
	l.draw.connect(refit, CONNECT_DEFERRED)
	return l


## Shrinks single-line label `l`'s font (to FIT_MIN_FONT_SCALE of its theme size at the least, or `min_scale` for a
## cell with no room to grow) until its text fits `width` px (its own width when `width` <= 0). Call it again whenever
## the text, the width or the theme changes: it starts from the theme's size each time, so a shorter text or a smaller
## text scale gets the full size back.
static func fit_label(l: Label, width: float = 0.0, min_scale: float = FIT_MIN_FONT_SCALE) -> void:
	l.remove_theme_font_size_override(&"font_size")
	var w := width if width > 0.0 else l.size.x
	if l.text == "" or w <= 0.0:
		return
	var font := l.get_theme_font(&"font")
	var fs := l.get_theme_font_size(&"font_size")
	var floor_fs := ceili(fs * min_scale)
	var size := fs
	while size > floor_fs and font.get_string_size(l.text, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x > w:
		size -= 1
	if size < fs:
		l.add_theme_font_size_override(&"font_size", size)


## The height wrapped label `l` needs for its text at its current font and width.
static func lines_height(l: Label) -> float:
	var lines := l.get_line_count()
	var spacing := float(l.get_theme_constant(&"line_spacing"))
	return lines * l.get_line_height() + maxi(lines - 1, 0) * spacing


## Shrinks wrapped label `l`'s font (to FIT_MIN_FONT_SCALE at the least) until its text's lines fit `height` px (its
## own height when `height` <= 0), as fit_label does for one line. The label keeps its size.
static func fit_lines(l: Label, height: float = 0.0) -> void:
	l.remove_theme_font_size_override(&"font_size")
	var h := height if height > 0.0 else l.size.y
	if l.text == "" or h <= 0.0:
		return
	var fs := l.get_theme_font_size(&"font_size")
	var floor_fs := ceili(fs * FIT_MIN_FONT_SCALE)
	var size := fs
	while size > floor_fs and lines_height(l) > h + 0.5:
		size -= 1
		l.add_theme_font_size_override(&"font_size", size)


## The readability pass (10-30, pillar 4): `p` (a float's start, HUD coordinates) moved out of each shown panel named
## in `m`'s avoid (node paths under `hud`) by the shortest way that stays on `size`, avoid_margin_px clear (the
## Drownbell's damage number had started under its boss read-out).
static func clear_of_panels(p: Vector2, hud: Node, m: Dictionary, size: Vector2) -> Vector2:
	var margin := num(m, "avoid_margin_px")
	for row: Variant in m.get("avoid", []):
		var r := panel_rect(row as Dictionary, hud)
		if not r.has_area():
			continue
		r = r.grow(margin)
		if not r.has_point(p):
			continue
		var best := p
		var dist := INF
		for q: Vector2 in [
			Vector2(p.x, r.end.y), Vector2(p.x, r.position.y), Vector2(r.end.x, p.y), Vector2(r.position.x, p.y)
		]:
			var on_screen := q.x >= 0.0 and q.y >= 0.0 and q.x <= size.x and q.y <= size.y
			if on_screen and q.distance_to(p) < dist:
				dist = q.distance_to(p)
				best = q
		p = best
	return p


## A damage.avoid row's shown panel (HUD coordinates): its battle_hud.json section's rect when it names one (a panel
## laid out inside a full-screen Control), else its node's own rect; an empty Rect2 when the node is hidden or absent.
static func panel_rect(row: Dictionary, hud: Node) -> Rect2:
	var c := hud.get_node_or_null(NodePath(str(row.get("node", "")))) as Control if hud != null else null
	if c == null or not c.is_visible_in_tree():
		return Rect2()
	if row.has("rect"):
		return rect_of(section(StringName(str(row["rect"]))))
	return c.get_global_rect()
