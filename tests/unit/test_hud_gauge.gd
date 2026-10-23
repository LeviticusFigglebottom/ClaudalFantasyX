extends TestCase
## M1-UI-05: a full Swell gauge's frame must read apart from its gold fill. Contrast is checked on
## the real theme colours as a WCAG ratio (relative luminance of the linearised sRGB values).

const THEME := "res://game/ui/theme/hymn_theme.tres"
## WCAG 2.x 1.4.11 (non-text contrast) asks 3:1 for the parts of a graphic that carry meaning.
const MIN_RATIO := 3.0


func _col(role: StringName) -> Color:
	return (load(THEME) as Theme).get_color(role, HymnThemeBuilder.PALETTE_TYPE)


static func _luminance(c: Color) -> float:
	var l := c.srgb_to_linear()
	return 0.2126 * l.r + 0.7152 * l.g + 0.0722 * l.b


static func _ratio(a: Color, b: Color) -> float:
	var la := _luminance(a)
	var lb := _luminance(b)
	return (maxf(la, lb) + 0.05) / (minf(la, lb) + 0.05)


func _full_gauge() -> HudGauge:
	var g := HudGauge.new(&"swell")
	g.size = Vector2(64, 4)
	g.full_gap_px = 1.0
	g.full_frame_px = 1.0
	g.glow = 1.0
	return g


func test_no_frame_until_full() -> void:
	var g := _full_gauge()
	g.glow = 0.0
	assert_eq(g.full_frame_rects().size(), 0)
	g.free()


func test_the_frame_is_a_night_gap_then_a_white_line_outside_the_bar() -> void:
	var g := _full_gauge()
	var strokes := g.full_frame_rects()
	assert_eq(strokes.size(), 2)
	assert_eq(strokes[0][1], &"text", "the frame is white (drawn first, outermost)")
	assert_eq(strokes[1][1], &"outline", "the gap is night, not gold")
	# Filled whole-pixel bands: the frame spans 2 px out, the gap 1 px out, the bar covers the rest.
	assert_eq(strokes[0][0], Rect2(-2, -2, 68, 8))
	assert_eq(strokes[1][0], Rect2(-1, -1, 66, 6))
	g.full_gap_px = 0.0
	assert_eq(g.full_frame_rects().size(), 1, "no gap band at 0 px")
	g.free()


func test_frame_and_gap_contrast_with_the_fill_and_each_other() -> void:
	var fill := _col(&"swell")
	var bright := fill.lerp(Color.WHITE, 0.5)  # the brightest top edge (glow 1, sheen) is lighter still
	var gap := _col(&"outline")
	var frame := _col(&"text")
	assert_true(_ratio(fill, gap) >= MIN_RATIO, "fill vs gap %.2f" % _ratio(fill, gap))
	assert_true(_ratio(bright, gap) >= MIN_RATIO, "bright fill vs gap %.2f" % _ratio(bright, gap))
	assert_true(_ratio(frame, gap) >= MIN_RATIO, "frame vs gap %.2f" % _ratio(frame, gap))
	# What sweep I saw: the old focus_gold frame sat right on the fill at about 1.1:1.
	assert_true(_ratio(_col(&"focus_gold"), fill) < MIN_RATIO, "the old frame really was too close")
