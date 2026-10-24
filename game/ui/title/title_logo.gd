class_name TitleLogo
extends Control
## The title's logotype (M2-UI-22): "Hymn" and "Undertow" in the title serif (the theme's TitleLabel
## font, EB Garamond), with a small-caps "of the" (BannerLabel's font) between them, flanked by gold
## rules that fade outward from a lamp-node diamond, and a tide flourish under the name: a gold wave
## and a fainter teal echo, both swelling from nothing at their ends, with a diamond above the crest.
## Built from theme fonts and draw_* calls only, no images. The waves drift slowly from the logo's
## own elapsed time (deterministic under --fixed-fps captures) and hold still under reduced motion.
## Sizes follow the theme, so the Accessibility text size scales the words. Layout: title_menu.json
## "logo"; the rect is the logo's extent at the 1920 x 1080 reference.

const WORD_KEYS: Array[String] = ["TITLE_LOGO_HYMN", "TITLE_LOGO_JOIN", "TITLE_LOGO_UNDERTOW"]

var _d: Dictionary = {}
var _t := 0.0


## Places the logo at `d`'s rect and keeps its metrics.
func setup(d: Dictionary) -> void:
	_d = d
	HudLayout.place(self, d)
	queue_redraw()


func _ready() -> void:
	name = &"TitleLogo"
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED or what == NOTIFICATION_RESIZED:
		queue_redraw()


func _process(delta: float) -> void:
	advance(delta)


## Steps the waves' drift by `delta` seconds (nothing under reduced motion). Tests call it directly.
func advance(delta: float) -> void:
	if UiSettings.shared().reduced_motion():
		return
	_t += delta
	queue_redraw()


## The waves' current phase (radians).
func wave_phase() -> float:
	return _t * _num("wave_drift_per_sec") * TAU


## The three words as shown: "Hymn", "of the", "Undertow" in the current language.
func words() -> Array[String]:
	var out: Array[String] = []
	for k in WORD_KEYS:
		out.append(tr(k))
	return out


## The font size of the big words (TitleLabel's size, scaled), and of the joining "of the".
func word_size() -> int:
	return roundi(get_theme_font_size(&"font_size", &"TitleLabel") * _num("word_scale_pct") / 100.0)


func join_size() -> int:
	return roundi(get_theme_font_size(&"font_size", &"BannerLabel") * _num("join_scale_pct") / 100.0)


## Each word's drawn width in pixels (tests check they fit the rect).
func word_widths() -> Array[float]:
	var w := words()
	var big := get_theme_font(&"font", &"TitleLabel")
	var small := get_theme_font(&"font", &"BannerLabel")
	return [_width(big, w[0], word_size()), _width(small, w[1], join_size()), _width(big, w[2], word_size())]


## The horizontal extent of the joining line (both rules, their nodes and "of the").
func join_extent() -> float:
	return word_widths()[1] + 2.0 * (_num("join_gap_px") + _num("join_rule_px"))


func _draw() -> void:
	if _d.is_empty():
		return
	var w := words()
	var widths := word_widths()
	var cx := size.x * 0.5
	var big := get_theme_font(&"font", &"TitleLabel")
	var small := get_theme_font(&"font", &"BannerLabel")
	var text := get_theme_color(&"text", HymnThemeBuilder.PALETTE_TYPE)
	var dim := get_theme_color(&"text_dim", HymnThemeBuilder.PALETTE_TYPE)
	_word(big, w[0], widths[0], _num("hymn_baseline"), word_size(), text)
	_word(small, w[1], widths[1], _num("join_baseline"), join_size(), dim)
	_word(big, w[2], widths[2], _num("undertow_baseline"), word_size(), text)
	# The join rules sit on the small caps' optical middle, a share of their ascent above the baseline.
	var rule_y := _num("join_baseline") - small.get_ascent(join_size()) * _num("join_rule_rise")
	_join_rules(cx, rule_y, widths[1] * 0.5)
	_tide(cx, _num("wave_y"))


func _word(font: Font, s: String, w: float, baseline: float, px: int, color: Color) -> void:
	var at := Vector2(floorf(size.x * 0.5 - w * 0.5), baseline)
	var shadow := _num("shadow_px")
	var sc := get_theme_color(&"shadow", HymnThemeBuilder.PALETTE_TYPE)
	draw_string(font, at + Vector2(shadow, shadow), s, HORIZONTAL_ALIGNMENT_LEFT, -1, px, sc)
	draw_string(font, at, s, HORIZONTAL_ALIGNMENT_LEFT, -1, px, color)


## Two gold rules either side of "of the": a lamp-node diamond by the word, the line fading outward.
func _join_rules(cx: float, y: float, half_word: float) -> void:
	var gold := get_theme_color(&"ornament_gold", HymnThemeBuilder.PALETTE_TYPE)
	var clear := Color(gold, 0.0)
	var node := _num("join_node_px")
	var px := _num("rule_px")
	for side: float in [-1.0, 1.0]:
		var inner := cx + side * (half_word + _num("join_gap_px"))
		var outer := inner + side * _num("join_rule_px")
		var start := Vector2(inner + side * node * 2.0, y)
		draw_polyline_colors(PackedVector2Array([start, Vector2(outer, y)]), PackedColorArray([gold, clear]), px, true)
		draw_colored_polygon(SwellRingView.diamond(Vector2(inner, y), node), gold)


## The tide flourish: a gold wave and a fainter teal echo under it, both swelling from nothing at
## their ends, with a small diamond riding above the middle crest.
func _tide(cx: float, y: float) -> void:
	var gold := get_theme_color(&"ornament_gold", HymnThemeBuilder.PALETTE_TYPE)
	var teal := get_theme_color(&"focus", HymnThemeBuilder.PALETTE_TYPE)
	teal.a *= _num("wave_echo_alpha")
	_wave(cx, y, wave_phase(), gold)
	_wave(cx, y + _num("wave_echo_dy_px"), wave_phase() + PI, teal)
	var crest := Vector2(cx, y - _num("wave_amp_px") - _num("crest_gap_px"))
	draw_colored_polygon(SwellRingView.diamond(crest, _num("crest_node_px")), gold)


func _wave(cx: float, y: float, phase: float, color: Color) -> void:
	var steps := maxi(int(_num("wave_steps")), 2)
	var half := _num("wave_span_px") * 0.5
	var amp := _num("wave_amp_px")
	var length := maxf(_num("wave_length_px"), 1.0)
	var pts := PackedVector2Array()
	var cols := PackedColorArray()
	for i in steps + 1:
		var u := float(i) / float(steps) * 2.0 - 1.0  # -1 .. 1 across the span
		var env := 1.0 - u * u
		var x := u * half
		pts.append(Vector2(cx + x, y - amp * env * cos(TAU * x / length + phase)))
		cols.append(Color(color, color.a * env))
	draw_polyline_colors(pts, cols, _num("wave_px"), true)


func _width(font: Font, s: String, px: int) -> float:
	return font.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x


func _num(key: String) -> float:
	return HudLayout.num(_d, key)
