extends TestCase
## hymn_theme.tres (M1-UI-01): generated from game/data/ui/theme.json + docs/kb/art/palette.json.

const THEME_PATH := "res://game/ui/theme/hymn_theme.tres"
const MIN_FONT_PX := 22

var cfg: Dictionary
var theme: Theme


func before_each() -> void:
	cfg = HymnThemeBuilder.load_config()
	theme = load(THEME_PATH) as Theme


func test_saved_theme_matches_the_builder() -> void:
	assert_true(theme != null, "hymn_theme.tres loads")
	var saved := HymnThemeBuilder.fingerprint(theme)
	var fresh := HymnThemeBuilder.fingerprint(HymnThemeBuilder.build(cfg))
	assert_eq(saved.keys().size(), fresh.keys().size(), "same theme types")
	for type: String in fresh:
		assert_eq(saved.get(type), fresh[type], "type %s drifted: re-run build_theme.gd (docs/kb/tech/ui.md)" % type)


func test_palette_roles_are_palette_swatches() -> void:
	var swatches := HymnThemeBuilder.load_swatches(str(cfg["palette_path"]))
	var roles: Dictionary = cfg["colors"]
	for role: String in roles:
		var spec: Array = roles[role]
		var got := theme.get_color(StringName(role), HymnThemeBuilder.PALETTE_TYPE)
		assert_between(got.a, float(spec[1]) - 0.002, float(spec[1]) + 0.002, "%s alpha" % role)
		var src := str(spec[0])
		if not src.begins_with("#"):
			assert_true(swatches.has(StringName(src)), "%s uses a real swatch (%s)" % [role, src])
			var want: Color = swatches[StringName(src)]
			assert_eq(Color(got, 1.0).to_html(false), want.to_html(false), "%s hex" % role)


func test_ui_md_colors() -> void:
	var c := func(role: StringName) -> String: return theme.get_color(role, &"Hymn").to_html(false).to_upper()
	assert_eq(c.call(&"panel_deep"), "0A2342")
	assert_eq(c.call(&"line_gold"), "D9B45A")
	assert_eq(c.call(&"focus"), "6FE0D8")
	assert_eq(c.call(&"danger"), "E85A44")
	assert_eq(c.call(&"enemy_chip"), "2A1420")


func test_no_text_below_minimum_size() -> void:
	assert_true(theme.default_font_size >= MIN_FONT_PX)
	for type in theme.get_type_list():
		for sname in theme.get_font_size_list(type):
			assert_true(theme.get_font_size(sname, type) >= MIN_FONT_PX, "%s.%s is under 22 px" % [type, sname])


func test_fonts_are_the_ofl_pair() -> void:
	var fonts: Dictionary = cfg["fonts"]
	for fname: String in fonts:
		var path := str(fonts[fname])
		assert_true(path.begins_with("res://assets/fonts/"), "%s lives in assets/fonts" % fname)
		assert_true(ResourceLoader.exists(path), "%s exists" % path)
		var dir := path.get_base_dir()
		assert_true(FileAccess.file_exists(dir.path_join("OFL.txt")), "license next to %s" % path)


func test_hud_numbers_use_tabular_figures() -> void:
	var f := theme.get_font(&"font", &"HudNumber") as FontVariation
	assert_true(f != null)
	var tnum := TextServerManager.get_primary_interface().name_to_tag("tnum")
	assert_eq(int(f.opentype_features.get(tnum, 0)), 1)
	var size := theme.get_font_size(&"font_size", &"HudNumber")
	var w1 := f.get_string_size("1111", HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	var w8 := f.get_string_size("8888", HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	assert_between(w1, w8 - 0.5, w8 + 0.5, "digits share one width, so HP never jitters")


func test_panels_use_the_tide_notch() -> void:
	var big := theme.get_stylebox(&"panel", &"PanelContainer") as TideNotchStyleBox
	var small := theme.get_stylebox(&"panel", &"PanelSmall") as TideNotchStyleBox
	assert_true(big != null and small != null)
	assert_eq(big.chamfer_px, float(cfg["constants"]["chamfer_px"]))
	assert_eq(small.chamfer_px, float(cfg["constants"]["chamfer_small_px"]))
	var pts := TideNotchStyleBox.notch_polygon(Rect2(0, 0, 100, 50), 10.0, 0.0)
	assert_eq(pts.size(), 6, "two chamfered corners, two square ones")
	assert_eq(pts[0], Vector2(0, 10))
	assert_eq(pts[1], Vector2(10, 0))
	assert_eq(pts[2], Vector2(100, 0), "top-right stays square")
	assert_eq(pts[5], Vector2(0, 50), "bottom-left stays square")


func test_focus_style_is_two_px_gold_with_glow() -> void:
	var focus := theme.get_stylebox(&"focus", &"Button") as StyleBoxFlat
	assert_eq(focus.border_width_top, int(cfg["constants"]["focus_px"]))
	assert_eq(focus.border_color, theme.get_color(&"focus_gold", &"Hymn"))
	assert_eq(focus.shadow_size, int(cfg["constants"]["focus_glow_px"]))
	assert_eq(focus.corner_detail, 1, "the focus frame is chamfered, not rounded")
