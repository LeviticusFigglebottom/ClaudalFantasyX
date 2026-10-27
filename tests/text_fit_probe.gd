class_name TextFitProbe
extends RefCounted
## M2-UI-28: does every visible text on a screen fit? Walks a screen's Control tree and measures
## each visible Label, Button and RichTextLabel's text against its own rect and the box it sits
## in. The rules (docs/kb/tech/ui.md 'Pseudo-localisation'):
##   - FAIL "overflows": the text's ink (where its glyphs land, after the label grows to its
##     minimum size the way a frame would grow it) leaves its box: the nearest Panel,
##     PanelContainer or NinePatchRect around it (an ancestor, else the smallest one on the screen
##     that holds the label's centre: menus draw their panels as siblings of their labels), every
##     clipping ancestor (a ScrollContainer only across its scroll), and the 1920 x 1080 reference.
##   - FAIL "clipped": text cut with no sign of it: clip_text with no ellipsis, a wrapped label
##     whose max_lines_visible hides lines with no ellipsis, a RichTextLabel that hides lines it
##     cannot scroll to, or one word wider than a wrapping label.
##   - WARN "trimmed": text ellipsized (text_overrun_behavior). The player sees that something is
##     cut and the full text is elsewhere (a detail pane, a tooltip), so it is a warning to review,
##     never a failure.
##   - WARN "grew": a PanelContainer grew past the size it was given (it still holds its text;
##     it may cover a neighbour).
## A screen has to be laid out before it is measured: the runner never ends a frame, so settle()
## does what the end of a frame does (containers sort, controls grow to their minimum size).

## Pixels of rounding a text may stick out before it counts.
const SLACK_PX := 1.0
const SETTLE_PASSES := 3
const PANEL_CLASSES: Array[String] = ["Panel", "PanelContainer", "NinePatchRect"]

var what := ""
var failures: PackedStringArray = []
var warnings: PackedStringArray = []

var _root: Node
var _designed: Dictionary = {}
var _boxes: Array[Control] = []


func _init(screen: Node, label: String) -> void:
	_root = screen
	what = label


## Probes `screen` (settling it first) and returns the findings.
static func probe(screen: Node, label: String) -> TextFitProbe:
	var p := TextFitProbe.new(screen, label)
	p.run()
	return p


## The 1920 x 1080 reference rect (the project's base viewport size).
static func reference_rect() -> Rect2:
	return Rect2(
		Vector2.ZERO,
		Vector2(
			float(ProjectSettings.get_setting("display/window/size/viewport_width")),
			float(ProjectSettings.get_setting("display/window/size/viewport_height"))
		)
	)


func run() -> void:
	var items: Array[Control] = []
	_collect(_root, items)
	for c in items:
		_designed[c] = rect_of(c)
	for b in _boxes:
		_designed[b] = rect_of(b)
	TextFitProbe.settle(_root)
	for c in items:
		if is_instance_valid(c) and _shown(c):
			_check(c)
	for b in _boxes:
		if b is PanelContainer and is_instance_valid(b) and _shown(b):
			var was: Rect2 = _designed[b]
			var now := rect_of(b)
			if now.size.x > was.size.x + SLACK_PX or now.size.y > was.size.y + SLACK_PX:
				_check_grown(b, was, now)


## A PanelContainer its text grew: a failure when it now leaves its own box, else a warning.
func _check_grown(b: Control, was: Rect2, now: Rect2) -> void:
	var box := _box_for(b)
	if Rect2(box.position - Vector2.ONE * SLACK_PX, box.size + Vector2.ONE * SLACK_PX * 2.0).encloses(now):
		warnings.append("%s: grew: %s from %s to %s" % [what, _path(b), _wh(was.size), _wh(now.size)])
		return
	failures.append(
		(
			"%s: overflows: panel %s grew from %s to %s, its box is %s: %s"
			% [what, _path(b), _r(was), _r(now), _r(box), _short(" / ".join(_texts_in(b)))]
		)
	)


func _texts_in(n: Node) -> PackedStringArray:
	var out: PackedStringArray = []
	for c in n.find_children("*", "Label", true, false):
		if (c as Label).is_visible_in_tree() and (c as Label).text != "":
			out.append((c as Label).text)
	return out


## Everything found, failures first.
func report() -> String:
	return "\n".join(failures + warnings)


## What the end of a frame does to a freshly built screen: every control placed by position grows
## to at least its minimum size (the way its grow direction says), and containers sort their
## children. Top-down and a few passes, each from the size the screen gave (never from an earlier
## pass's growth), so a wrapping label measured at a stale width cannot leave a panel too tall.
static func settle(root: Node) -> void:
	var given := {}
	_placed(root, given)
	var wrapping: Array[Control] = []
	for n in root.find_children("*", "Control", true, false):
		if (n is Label or n is RichTextLabel) and n.get(&"autowrap_mode") != TextServer.AUTOWRAP_OFF:
			wrapping.append(n as Control)
	for _pass in SETTLE_PASSES:
		for w in wrapping:
			w.update_minimum_size()  # its height follows the width the last sort gave it
		_settle(root, given)


static func _placed(n: Node, given: Dictionary) -> void:
	if n is Control and not (n.get_parent() is Container):
		given[n] = Rect2((n as Control).position, (n as Control).size)
	for c in n.get_children():
		_placed(c, given)


static func _settle(n: Node, given: Dictionary) -> void:
	if given.has(n):
		_grow(n as Control, given[n] as Rect2)
	if n is Container:
		n.notification(Container.NOTIFICATION_SORT_CHILDREN)
	for c in n.get_children():
		_settle(c, given)


## `c` at its given rect, grown to its minimum size.
static func _grow(c: Control, was: Rect2) -> void:
	var d := (c.get_combined_minimum_size() - was.size).max(Vector2.ZERO)
	var at := was.position - Vector2(d.x * _grow_share(c.grow_horizontal), d.y * _grow_share(c.grow_vertical))
	if c.size != was.size + d:
		c.size = was.size + d
	if c.position != at:
		c.position = at


static func _grow_share(dir: Control.GrowDirection) -> float:
	match dir:
		Control.GROW_DIRECTION_BEGIN:
			return 1.0
		Control.GROW_DIRECTION_BOTH:
			return 0.5
	return 0.0


## `c`'s rect on the screen (its canvas layer's coordinates, at the reference size).
static func rect_of(c: Control) -> Rect2:
	var xf := c.get_global_transform_with_canvas()
	return Rect2(xf.origin, c.size * xf.get_scale())


func _collect(n: Node, items: Array[Control]) -> void:
	if n.is_queued_for_deletion() or (n is CanvasItem and not (n as CanvasItem).visible):
		return
	if n is Label or n is Button or n is RichTextLabel:
		if _text_of(n as Control).strip_edges() != "":
			items.append(n as Control)
	if n is Control and PANEL_CLASSES.has(n.get_class()):
		if not ((n as Control).get_theme_stylebox(&"panel") is CursorStyleBox):
			_boxes.append(n as Control)
	for c in n.get_children():
		_collect(c, items)


## Visible and not faded out.
static func _shown(c: CanvasItem) -> bool:
	if not c.is_visible_in_tree():
		return false
	var n: Node = c
	while n != null:
		if n is CanvasItem and ((n as CanvasItem).modulate.a <= 0.01 or (n as CanvasItem).self_modulate.a <= 0.01):
			return false
		n = n.get_parent()
	return true


static func _text_of(c: Control) -> String:
	if c is RichTextLabel:
		return (c as RichTextLabel).get_parsed_text()
	return str(c.get(&"text"))


func _check(c: Control) -> void:
	var ink := _ink(c)
	if ink.size == Vector2.ZERO or _scrolled_away(c, ink):
		return
	var box := _box_for(c)
	var out := Rect2(box.position - Vector2.ONE * SLACK_PX, box.size + Vector2.ONE * SLACK_PX * 2.0)
	if not out.encloses(ink):
		failures.append(
			(
				"%s: overflows: %s %s needs %s, its box is %s: %s"
				% [what, _path(c), _wh(ink.size), _r(ink), _r(box), _short(_text_of(c))]
			)
		)


## Where the text's glyphs land (and records clips and trims on the way).
func _ink(c: Control) -> Rect2:
	var r := rect_of(c)
	if c is Label:
		return _label_ink(c as Label, r)
	if c is RichTextLabel:
		var t := c as RichTextLabel
		var h := float(t.get_content_height())
		if not t.fit_content and not t.scroll_active and h > t.size.y + SLACK_PX:
			failures.append(
				"%s: clipped: %s hides lines (%d px of text in %d): %s" % [what, _path(c), h, t.size.y, _short(t.text)]
			)
		return r
	var b := c as Button
	if b.clip_text or b.text_overrun_behavior != TextServer.OVERRUN_NO_TRIMMING:
		var font := b.get_theme_font(&"font")
		var w := font.get_string_size(b.text, HORIZONTAL_ALIGNMENT_LEFT, -1, b.get_theme_font_size(&"font_size")).x
		var room := b.size.x - b.get_theme_stylebox(&"normal").get_minimum_size().x
		if w > room + SLACK_PX:
			_cut(c, b.text, w, room, b.text_overrun_behavior == TextServer.OVERRUN_NO_TRIMMING)
	return r


func _label_ink(l: Label, r: Rect2) -> Rect2:
	var style := l.get_theme_stylebox(&"normal")
	var scale := r.size / l.size if l.size.x > 0.0 and l.size.y > 0.0 else Vector2.ONE
	var content := Rect2(
		r.position + Vector2(style.get_margin(SIDE_LEFT), style.get_margin(SIDE_TOP)) * scale,
		r.size - style.get_minimum_size() * scale
	)
	var font := l.get_theme_font(&"font")
	var fsize := l.get_theme_font_size(&"font_size")
	var text := l.text.to_upper() if l.uppercase else l.text
	var trims := l.text_overrun_behavior != TextServer.OVERRUN_NO_TRIMMING
	var w := 0.0
	if l.autowrap_mode == TextServer.AUTOWRAP_OFF:
		for line in text.split("\n"):
			w = maxf(w, font.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, fsize).x)
		w *= scale.x
		if w > content.size.x + SLACK_PX and (l.clip_text or trims):
			_cut(l, l.text, w, content.size.x, not trims)
			w = content.size.x
	else:
		var p := TextParagraph.new()
		p.add_string(text, font, fsize)
		p.width = l.size.x - style.get_minimum_size().x
		p.break_flags = _break_flags(l.autowrap_mode)
		w = p.get_size().x * scale.x
		if w > content.size.x + SLACK_PX:
			failures.append(
				"%s: clipped: %s has a word wider than its %d px: %s" % [what, _path(l), content.size.x, _short(l.text)]
			)
		var shown := l.get_visible_line_count()
		if shown < l.get_line_count():
			_cut(l, l.text, l.get_line_count(), shown, not trims, "lines")
		w = minf(w, content.size.x)
	var h := (l.get_combined_minimum_size().y - style.get_minimum_size().y) * scale.y
	if l.clip_text or l.max_lines_visible >= 0 or trims:
		h = minf(h, content.size.y)
	var x := content.position.x
	match l.horizontal_alignment:
		HORIZONTAL_ALIGNMENT_CENTER:
			x += (content.size.x - w) * 0.5
		HORIZONTAL_ALIGNMENT_RIGHT:
			x += content.size.x - w
	var y := content.position.y
	match l.vertical_alignment:
		VERTICAL_ALIGNMENT_CENTER:
			y += (content.size.y - h) * 0.5
		VERTICAL_ALIGNMENT_BOTTOM:
			y += content.size.y - h
	# The line boxes hold the font's whole ascent and descent, and the glyphs sit inside them: only
	# the glyphs count (a badge's line box may graze its panel's edge with its digits well inside).
	# An accent stacked over a capital may rise past the ascent, as the font intends: the line box
	# is the most a line is held to.
	var g := glyph_extent(text, font, fsize)
	var top := maxf(font.get_ascent(fsize) - g.x, 0.0) * scale.y
	var bottom := maxf(font.get_descent(fsize) - g.y, 0.0) * scale.y
	return Rect2(x, y + top, w, maxf(h - top - bottom, 0.0))


## How far `text`'s glyphs reach above (x) and below (y) the baseline, in pixels.
static func glyph_extent(text: String, font: Font, fsize: int) -> Vector2:
	var line := TextLine.new()
	line.add_string(text.replace("\n", " "), font, fsize)
	var ts := TextServerManager.get_primary_interface()
	var out := Vector2.ZERO
	for g: Dictionary in ts.shaped_text_get_glyphs(line.get_rid()):
		var rid: RID = g.get("font_rid", RID())
		if not rid.is_valid():
			continue
		var at := Vector2i(int(g.get("font_size", fsize)), 0)
		var off := ts.font_get_glyph_offset(rid, at, int(g.get("index", 0)))
		var sz := ts.font_get_glyph_size(rid, at, int(g.get("index", 0)))
		out = out.max(Vector2(-off.y, off.y + sz.y))
	return out


static func _break_flags(mode: TextServer.AutowrapMode) -> int:
	var f := TextServer.BREAK_MANDATORY
	match mode:
		TextServer.AUTOWRAP_ARBITRARY:
			f |= TextServer.BREAK_GRAPHEME_BOUND
		TextServer.AUTOWRAP_WORD:
			f |= TextServer.BREAK_WORD_BOUND
		TextServer.AUTOWRAP_WORD_SMART:
			f |= TextServer.BREAK_WORD_BOUND | TextServer.BREAK_ADAPTIVE
	return f


## A cut text: a failure when nothing shows it is cut (hard), else a "trimmed" warning.
func _cut(c: Control, text: String, need: float, room: float, hard: bool, unit: String = "px") -> void:
	var line := (
		"%s: %s: %s (%d %s for %d): %s"
		% [what, "clipped" if hard else "trimmed", _path(c), need, unit, room, _short(text)]
	)
	if hard:
		failures.append(line)
	else:
		warnings.append(line)


## The rect `c`'s text must stay inside: the reference, every clipping ancestor (not across its
## scroll), and its panel.
func _box_for(c: Control) -> Rect2:
	var box := reference_rect()
	var panel: Control = null
	var scrolled := Vector2i.ZERO
	var n := c.get_parent()
	while n != null:
		if n is Control:
			var a := n as Control
			if panel == null and _boxes.has(a):
				panel = a
			if a.clip_contents:
				var s := _scrolls(a)
				box = _clip(box, rect_of(a), s)
				scrolled = scrolled.max(s)
		n = n.get_parent()
	if panel == null:
		panel = _smallest_box_around((_designed.get(c, rect_of(c)) as Rect2).get_center(), c)
	if panel != null:
		box = _clip(box, rect_of(panel), scrolled)  # a scrolled line may pass its panel's edge too
	return box


## Which axes a clipping control scrolls (x, y: 1 when it does): a ScrollContainer's enabled
## scroll modes, or the vertical scroll of a clip inside a page that answers max_scroll() (the
## codex's text, the dialogue backlog).
static func _scrolls(a: Control) -> Vector2i:
	if a is ScrollContainer:
		var s := a as ScrollContainer
		return Vector2i(
			int(s.horizontal_scroll_mode != ScrollContainer.SCROLL_MODE_DISABLED),
			int(s.vertical_scroll_mode != ScrollContainer.SCROLL_MODE_DISABLED)
		)
	var n: Node = a
	while n != null:
		if n.has_method(&"max_scroll"):
			return Vector2i(0, 1)
		n = n.get_parent()
	return Vector2i.ZERO


## True when `c` sits in a scrolling clip and is scrolled wholly out of it (not on screen now).
func _scrolled_away(c: Control, ink: Rect2) -> bool:
	var n := c.get_parent()
	while n != null:
		if n is Control and (n as Control).clip_contents and _scrolls(n as Control) != Vector2i.ZERO:
			if not rect_of(n as Control).intersects(ink):
				return true
		n = n.get_parent()
	return false


## `box` cut by `by`, except across the axes in `scrolls`.
static func _clip(box: Rect2, by: Rect2, scrolls: Vector2i) -> Rect2:
	var out := box.intersection(by)
	if scrolls.y != 0:
		out.position.y = box.position.y
		out.size.y = box.size.y
	if scrolls.x != 0:
		out.position.x = box.position.x
		out.size.x = box.size.x
	return out


## The smallest panel on the screen whose designed rect holds `at` (not `c`'s own descendant).
func _smallest_box_around(at: Vector2, c: Control) -> Control:
	var best: Control = null
	var best_area := INF
	for b in _boxes:
		if b == c or not is_instance_valid(b) or not _shown(b) or c.is_ancestor_of(b):
			continue
		var r: Rect2 = _designed.get(b, rect_of(b))
		if r.has_point(at) and r.get_area() < best_area:
			best = b
			best_area = r.get_area()
	return best


func _path(c: Node) -> String:
	return str(_root.get_path_to(c)) if _root.is_ancestor_of(c) else str(c.get_path())


static func _r(r: Rect2) -> String:
	return "(%d, %d)-(%d, %d)" % [r.position.x, r.position.y, r.end.x, r.end.y]


static func _wh(v: Vector2) -> String:
	return "%dx%d" % [v.x, v.y]


static func _short(t: String) -> String:
	var one := t.replace("\n", " / ")
	return one if one.length() <= 90 else one.substr(0, 87) + "..."
