extends TestCase
## M2-UI-11: the colour-blind palette on the timeline and status chips. Every chip and glyph colour
## is a theme role, so the palette reaches them through BattleHud.apply_settings; this checks the
## override itself. Under simulated deuteranopia and protanopia (Machado et al. 2009, severity 1,
## on linear RGB) the danger role must stay apart (Oklab distance) from every role it shares the
## HUD with, at least as well as the standard red does, and readable on the darkest panel.

const ROLES_NEAR_DANGER: Array[StringName] = [&"focus", &"hp", &"heal", &"swell", &"text", &"mp"]
const MIN_DISTANCE := 0.15
const MIN_CONTRAST := 4.5
const DEUT := [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]
const PROT := [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]
const NORMAL := [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


func test_colorblind_danger_stays_apart_under_red_green_deficiency() -> void:
	var standard := _theme(UiSettings.new())
	var cb_settings := UiSettings.new()
	assert_true(cb_settings.set_value(UiSettings.PALETTE, "colorblind"))
	var cb := _theme(cb_settings)
	var worst_cb := _worst(cb)
	var worst_std := _worst(standard)
	assert_true(worst_cb >= MIN_DISTANCE, "colour-blind danger is distinct everywhere: %.3f" % worst_cb)
	assert_true(worst_cb >= worst_std, "and no worse than the standard red (%.3f vs %.3f)" % [worst_cb, worst_std])
	var danger := cb.get_color(&"danger", HymnThemeBuilder.PALETTE_TYPE)
	var panel := cb.get_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	assert_true(_contrast(danger, Color(panel, 1.0)) >= MIN_CONTRAST, "danger text reads on the darkest panel")


func test_the_hud_takes_the_palette_live() -> void:
	var cb := UiSettings.new()
	cb.set_value(UiSettings.PALETTE, "colorblind")
	var std_danger := _theme(UiSettings.new()).get_color(&"danger", HymnThemeBuilder.PALETTE_TYPE)
	var cb_danger := _theme(cb).get_color(&"danger", HymnThemeBuilder.PALETTE_TYPE)
	assert_ne(std_danger, cb_danger, "the override swaps danger")
	var fx := BattleFixture.capture_settings(&"statuses_colorblind")
	assert_eq(fx.palette(), &"colorblind", "the colour-blind shot's fixture renders in that palette")
	assert_eq(BattleFixture.script_of(&"statuses_colorblind"), &"statuses", "and replays the statuses script")
	assert_eq(BattleFixture.capture_settings(&"statuses").palette(), &"standard")


func _theme(s: UiSettings) -> Theme:
	return HymnThemeBuilder.build(s.theme_config())


func _worst(t: Theme) -> float:
	var danger := t.get_color(&"danger", HymnThemeBuilder.PALETTE_TYPE)
	var worst := INF
	for role in ROLES_NEAR_DANGER:
		var other := t.get_color(role, HymnThemeBuilder.PALETTE_TYPE)
		for m: Array in [DEUT, PROT, NORMAL]:
			worst = minf(worst, _oklab(_sim(danger, m)).distance_to(_oklab(_sim(other, m))))
	return worst


static func _sim(c: Color, m: Array) -> Color:
	var l := c.srgb_to_linear()
	var v := [l.r, l.g, l.b]
	var out: Array[float] = []
	for row: Array in m:
		out.append(clampf(float(row[0]) * v[0] + float(row[1]) * v[1] + float(row[2]) * v[2], 0.0, 1.0))
	return Color(out[0], out[1], out[2])


## Linear RGB -> Oklab (Björn Ottosson's matrices).
static func _oklab(lin: Color) -> Vector3:
	var l := pow(0.4122214708 * lin.r + 0.5363325363 * lin.g + 0.0514459929 * lin.b, 1.0 / 3.0)
	var m := pow(0.2119034982 * lin.r + 0.6806995451 * lin.g + 0.1073969566 * lin.b, 1.0 / 3.0)
	var s := pow(0.0883024619 * lin.r + 0.2817188376 * lin.g + 0.6299787005 * lin.b, 1.0 / 3.0)
	return Vector3(
		0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
		1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
		0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
	)


## WCAG contrast ratio of two opaque sRGB colours.
static func _contrast(a: Color, b: Color) -> float:
	var la := _luma(a)
	var lb := _luma(b)
	return (maxf(la, lb) + 0.05) / (minf(la, lb) + 0.05)


static func _luma(c: Color) -> float:
	var l := c.srgb_to_linear()
	return 0.2126 * l.r + 0.7152 * l.g + 0.0722 * l.b
