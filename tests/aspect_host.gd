class_name AspectHost
extends RefCounted
## Shared steps for the resolution and aspect audit (M2-UI-29, tests/unit/test_aspect_layouts.gd).
## The project stretches canvas items with aspect "expand" from a 1920x1080 base, so a window
## size maps to a logical viewport: 16:9 sizes to 1920x1080, 16:10 to 1920x1200, 21:9 to about
## 2560x1080. Setting the root window's size (it applies at once, even headless) is what a
## player's window change does; restore() puts the runner's size back.

## The audited window sizes: 16:9 (1920x1080, 1280x720, 3840x2160), 16:10 (1920x1200, the
## 1280x800 handheld), 21:9 (2560x1080, 3440x1440) and 4:3 (1440x1080, 1024x768; the Lead, 2026-10-29).
const WINDOWS: Array[Vector2i] = [
	Vector2i(1920, 1080),
	Vector2i(1280, 720),
	Vector2i(3840, 2160),
	Vector2i(1920, 1200),
	Vector2i(1280, 800),
	Vector2i(2560, 1080),
	Vector2i(3440, 1440),
	Vector2i(1440, 1080),
	Vector2i(1024, 768),
]
## One window per distinct logical viewport (16:9, 16:10, 21:9, 43:18, 4:3): the cheap sweep.
const ASPECTS: Array[Vector2i] = [
	Vector2i(1920, 1080),
	Vector2i(1280, 800),
	Vector2i(2560, 1080),
	Vector2i(3440, 1440),
	Vector2i(1440, 1080),
]
## Text scales the UiSettings "text_scale" option offers at its ends (100% and 130%).
const TEXT_SCALES: Array[float] = [1.0, 1.3]
## Sub-pixel slack for float rects.
const EPS := 0.5
## Layout passes settle() runs (a container inside a container needs one per level).
const SETTLE_PASSES := 4

static var _saved_size := Vector2i.ZERO


static func root() -> Window:
	return (Engine.get_main_loop() as SceneTree).root


## Resizes the root window to `size` (the first call remembers the runner's own size).
static func set_window(size: Vector2i) -> void:
	if _saved_size == Vector2i.ZERO:
		_saved_size = root().size
	root().size = size


static func restore() -> void:
	if _saved_size != Vector2i.ZERO:
		root().size = _saved_size
	_saved_size = Vector2i.ZERO


## The logical viewport rect the UI lays out in.
static func view() -> Rect2:
	return root().get_visible_rect()


## `c`'s rect in viewport coordinates (through its CanvasLayer).
static func rect_of(c: Control) -> Rect2:
	var xf := c.get_global_transform_with_canvas()
	return Rect2(xf * Vector2.ZERO, c.size * xf.get_scale())


static func label(c: Control) -> String:
	return "%s(%s)" % [c.name, c.get_class()]


## Every visible Control under `n` with a size, in tree order.
static func visible_controls(n: Node, out: Array[Control] = []) -> Array[Control]:
	for ch in n.get_children():
		if ch is CanvasLayer and not (ch as CanvasLayer).visible:
			continue
		if ch is Control:
			var c := ch as Control
			if not c.is_visible_in_tree():
				continue
			if c.size.x > EPS and c.size.y > EPS:
				out.append(c)
		visible_controls(ch, out)
	return out


## The visible Controls under `n` that leave the viewport (labels for messages; [] when none).
## A Control clipped by an ancestor (clip_contents, a ScrollContainer) is judged by its clip.
## The Lead's final-quality pass (2026-10-29): every visible Control's stylebox, font and icon that falls through to
## Godot's built-in default theme, so draws Godot's own widget look. A StyleBoxEmpty or a missing item draws nothing
## and is not counted, nor is the focus style of a Control that never takes focus. "<path> (<class>) <kind> <name>"
## per hit.
static func default_theme_uses(n: Node) -> PackedStringArray:
	var bad := PackedStringArray()
	var engine := ThemeDB.get_default_theme()
	for c in visible_controls(n):
		var cls := c.get_class()
		for name in engine.get_stylebox_list(cls):
			var sb := c.get_theme_stylebox(name)
			if name == "focus" and c.focus_mode == Control.FOCUS_NONE:
				continue  # never focused, so never drawn
			if sb != null and not sb is StyleBoxEmpty and sb == engine.get_stylebox(name, cls):
				bad.append("%s (%s) stylebox %s" % [c.get_path(), cls, name])
		for name in engine.get_font_list(cls):
			if c.get_theme_font(name) == engine.get_font(name, cls) and c.get_theme_font(name) == ThemeDB.fallback_font:
				bad.append("%s (%s) font %s" % [c.get_path(), cls, name])
		for name in engine.get_icon_list(cls):
			var ic := c.get_theme_icon(name)
			if ic != null and ic == engine.get_icon(name, cls):
				bad.append("%s (%s) icon %s" % [c.get_path(), cls, name])
	return bad


static func outside(n: Node) -> PackedStringArray:
	var bad := PackedStringArray()
	var v := view().grow(EPS)
	for c in visible_controls(n):
		if _clipped_away(c):
			continue
		var r := rect_of(c)
		if not v.encloses(r):
			bad.append("%s at %s" % [label(c), r])
	return bad


## The visible Labels under `n` whose text runs out of the panel it sits on: the smallest visible
## Panel or PanelContainer holding the text's top-left corner, among the panels that share the
## label's branch (a sibling of the label or of one of its ancestors, or an ancestor). Text grown
## past its frame by a longer string or a larger text scale shows here. Labels clipped by an
## ancestor are skipped, as in outside().
static func spilling(n: Node) -> PackedStringArray:
	var bad := PackedStringArray()
	var panels: Array[Control] = []
	var all := visible_controls(n)
	for c in all:
		if c is Panel or c is PanelContainer:
			panels.append(c)
	for c in all:
		if not c is Label or _clipped_away(c) or (c as Label).text.strip_edges() == "":
			continue
		var r := ink_rect(c as Label)
		var home := Rect2()
		for p in panels:
			var pr := rect_of(p)
			if not _shares_branch(p, c) or not pr.has_point(r.position + Vector2(EPS, EPS)):
				continue
			if home.size == Vector2.ZERO or pr.get_area() < home.get_area():
				home = pr
		if home.size != Vector2.ZERO and not home.grow(EPS).encloses(r):
			bad.append("%s '%s' (text at %s) spills out of %s" % [label(c), (c as Label).text.left(24), r, home])
	return bad


## Where `l`'s text draws, in viewport coordinates: the measured width of its longest line (the
## label's own width when it wraps or trims) placed by its alignment, and the font size per line
## tall (the glyphs, not the line box's leading).
static func ink_rect(l: Label) -> Rect2:
	var r := rect_of(l)
	var font := l.get_theme_font(&"font")
	var fs := l.get_theme_font_size(&"font_size")
	var lines := l.get_line_count() if l.autowrap_mode != TextServer.AUTOWRAP_OFF else l.text.count("\n") + 1
	if l.max_lines_visible >= 0:
		lines = mini(lines, l.max_lines_visible)
	var w := r.size.x
	if l.autowrap_mode == TextServer.AUTOWRAP_OFF:
		w = font.get_multiline_string_size(l.text, l.horizontal_alignment, -1, fs).x
		if l.clip_text or l.text_overrun_behavior != TextServer.OVERRUN_NO_TRIMMING:
			w = minf(w, r.size.x)
	var line_h := font.get_height(fs) + float(l.get_theme_constant(&"line_spacing"))
	var h := line_h * float(lines - 1) + float(fs)
	var x := r.position.x
	match l.horizontal_alignment:
		HORIZONTAL_ALIGNMENT_CENTER:
			x = r.get_center().x - w * 0.5
		HORIZONTAL_ALIGNMENT_RIGHT:
			x = r.end.x - w
	var lead := (font.get_height(fs) - float(fs)) * 0.5
	var y := r.position.y + lead
	match l.vertical_alignment:
		VERTICAL_ALIGNMENT_CENTER:
			y = r.get_center().y - h * 0.5
		VERTICAL_ALIGNMENT_BOTTOM:
			y = r.end.y - lead - h
	return Rect2(x, y, w, h)


## True when panel `p` sits on `c`'s branch: an ancestor of `c`, or a child of one.
static func _shares_branch(p: Control, c: Control) -> bool:
	var up: Node = c
	while up != null:
		if up == p or up == p.get_parent():
			return true
		up = up.get_parent()
	return false


static func _clipped_away(c: Control) -> bool:
	var p := c.get_parent()
	while p is Control:
		var pc := p as Control
		if pc.clip_contents or pc is ScrollContainer:
			return true
		p = p.get_parent()
	return false


## True when `c` covers the whole viewport.
static func covers(c: Control) -> bool:
	return rect_of(c).grow(EPS).encloses(view())


## `c`'s distances to the viewport's edges: [left, top, right, bottom].
static func margins(c: Control) -> Array[float]:
	var r := rect_of(c)
	var v := view()
	return [r.position.x - v.position.x, r.position.y - v.position.y, v.end.x - r.end.x, v.end.y - r.end.y]


## True when `c` sits centred on the viewport horizontally (and vertically when `both`).
static func centred(c: Control, both: bool = true) -> bool:
	var m := margins(c)
	return absf(m[0] - m[2]) <= 1.0 + EPS and (not both or absf(m[1] - m[3]) <= 1.0 + EPS)


## Lays `n` out now the way the next frames would: a test never reaches a frame's end, so the
## deferred work (containers sorting their children, a wrapped Label's height following its
## width, a Control's size following its new minimum) is done here, a few passes deep.
static func settle(n: Node) -> void:
	for _pass in SETTLE_PASSES:
		var all: Array[Node] = [n]
		all.append_array(n.find_children("*", "Control", true, false))
		for c in all:
			if c is Label and (c as Label).autowrap_mode != TextServer.AUTOWRAP_OFF:
				(c as Control).update_minimum_size()
		for c in all:
			if not c is Control:
				continue
			var ctl := c as Control
			if not ctl.get_parent() is Container:
				var o := ctl.offset_right
				ctl.offset_right = o + 1.0  # re-derive the size from the anchors and the new minimum
				ctl.offset_right = o
			if ctl is Container:
				ctl.notification(Container.NOTIFICATION_SORT_CHILDREN)


## True when margins `m` (margins()) keep the reference margins `ref` on the sides `pin` (anchor
## fractions, HudLayout.PINS) names: the left or right margin for x = 0 or 1, the balance of the
## two (centred as at the reference) for x = 0.5; the same for y.
static func keeps_pin(m: Array, ref: Array, pin: Vector2) -> bool:
	return _keeps_axis(m[0], m[2], ref[0], ref[2], pin.x) and _keeps_axis(m[1], m[3], ref[1], ref[3], pin.y)


static func _keeps_axis(lo: float, hi: float, ref_lo: float, ref_hi: float, fraction: float) -> bool:
	if is_zero_approx(fraction):
		return absf(lo - ref_lo) <= 1.0 + EPS
	if is_equal_approx(fraction, 1.0):
		return absf(hi - ref_hi) <= 1.0 + EPS
	return absf((lo - hi) - (ref_lo - ref_hi)) <= 1.0 + EPS


## A UiSettings at text scale `s` (the option the Settings page offers).
static func settings_at(s: float) -> UiSettings:
	var u := UiSettings.new()
	u.set_value(UiSettings.TEXT_SCALE, s)
	return u
