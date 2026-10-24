class_name HymnThemeBuilder
extends RefCounted
## Builds the project Theme from game/data/ui/theme.json and the art palette
## (docs/kb/art/palette.json), so every UI color is a named swatch and every metric is data.
## hymn_theme.tres is this builder's saved output; regenerate it with
##   godot --headless --path . --script res://game/ui/theme/build_theme.gd
## and tests/unit/test_ui_theme.gd fails if the saved file drifts from the builder.
## Runtime code reads palette roles from the theme: get_theme_color(&"focus", &"Hymn").

const CONFIG_PATH := "res://game/data/ui/theme.json"
const PALETTE_TYPE := &"Hymn"


static func load_config(path: String = CONFIG_PATH) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(parsed) != TYPE_DICTIONARY or typeof((parsed as Dictionary).get("theme")) != TYPE_DICTIONARY:
		push_error("HymnThemeBuilder: could not read 'theme' from %s" % path)
		return {}
	return (parsed as Dictionary)["theme"] as Dictionary


## Swatch name -> sRGB Color from palette.json.
static func load_swatches(path: String) -> Dictionary:
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	var out: Dictionary = {}
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("HymnThemeBuilder: could not parse palette %s" % path)
		return out
	var swatches: Dictionary = (parsed as Dictionary).get("swatches", {})
	for sname: Variant in swatches:
		out[StringName(str(sname))] = Color.html(str((swatches[sname] as Dictionary).get("hex", "#FF00FF")))
	return out


## Role name -> Color with alpha, resolving swatch names (or literal "#RRGGBB") from the palette.
static func resolve_colors(cfg: Dictionary) -> Dictionary:
	var swatches := load_swatches(str(cfg.get("palette_path", "")))
	var out: Dictionary = {}
	var roles: Dictionary = cfg.get("colors", {})
	for role: Variant in roles:
		var spec: Array = roles[role]
		var src := str(spec[0])
		var base: Color
		if src.begins_with("#"):
			base = Color.html(src)
		elif swatches.has(StringName(src)):
			base = swatches[StringName(src)]
		else:
			push_error("HymnThemeBuilder: unknown swatch '%s' for role '%s'" % [src, role])
			base = Color.MAGENTA
		out[StringName(str(role))] = Color(base, float(spec[1]))
	return out


static func build(cfg: Dictionary = {}) -> Theme:
	if cfg.is_empty():
		cfg = load_config()
	var colors := resolve_colors(cfg)
	var k: Dictionary = cfg.get("constants", {})
	var t := Theme.new()
	for role: StringName in colors:
		t.set_color(role, PALETTE_TYPE, colors[role])
	for cname: Variant in k:
		t.set_constant(StringName(str(cname)), PALETTE_TYPE, int(k[cname]))
	var fonts := _load_fonts(cfg)
	t.default_font = fonts.get(StringName(str(cfg.get("default_font", "sans"))))
	t.default_font_size = int(cfg.get("default_font_size", 0))
	_label(t, colors, k)
	_panels(t, colors, k)
	_buttons(t, colors, k)
	_gauges(t, colors, k)
	_scrollbars(t, colors, k)
	_variations(t, cfg, colors, k, fonts)
	return t


## The tide-notch panel style with this theme's colors and metrics.
static func panel_style(colors: Dictionary, k: Dictionary, chamfer: int) -> TideNotchStyleBox:
	var s := TideNotchStyleBox.new()
	s.fill_top = colors[&"panel_deep"]
	s.fill_bottom = colors[&"panel_low"]
	s.sheen_color = colors[&"panel_sheen"]
	s.sheen_px = float(k["sheen_px"])
	s.frame_color = colors[&"line_gold"]
	s.rule_color = colors[&"rule_white"]
	s.rule_inset_px = float(k["inner_rule_inset_px"])
	s.line_px = float(k["line_px"])
	s.chamfer_px = float(chamfer)
	s.lamp_node_px = float(k["lamp_node_px"])
	s.lamp_node_glow_px = float(k["lamp_node_glow_px"])
	s.lamp_node_glow = colors[&"lamp_node_glow"]
	s.set_content_margin_all(float(k["panel_margin_px"]))
	# ADR 0033 flair.
	s.glint_color = colors[&"surface_glint"]
	s.glint_span = float(k["glint_span_pct"]) / 100.0
	s.glint_inset_px = float(k["inner_rule_inset_px"])
	s.corner_tick_px = float(k["corner_tick_px"])
	s.corner_tick_inset_px = float(k["corner_tick_inset_px"])
	s.tide_color = colors[&"tide_line"]
	s.tide_lines = int(k["tide_lines"])
	s.tide_band_px = float(k["tide_band_px"])
	s.tide_amp_px = float(k["tide_amp_px"])
	s.tide_wavelength_px = float(k["tide_wavelength_px"])
	s.tide_min_height_px = float(k["tide_min_height_px"])
	return s


## The menu cursor (MenuPage reads it as stylebox "cursor" of the Hymn type; ADR 0033).
static func cursor_style(colors: Dictionary, k: Dictionary) -> CursorStyleBox:
	var s := CursorStyleBox.new()
	s.fill = colors[&"panel_raised"]
	s.fill_fade = float(k["cursor_fill_fade_pct"]) / 100.0
	s.wash = colors[&"cursor_wash"]
	s.wash_span = float(k["cursor_wash_span_pct"]) / 100.0
	s.frame_color = colors[&"focus_gold"]
	s.frame_px = float(k["focus_px"])
	s.glow_color = colors[&"focus_glow"]
	s.glow_px = float(k["focus_glow_px"])
	s.chamfer_px = float(k["chamfer_small_px"])
	s.wick_color = colors[&"focus"]
	s.wick_px = float(k["cursor_wick_px"])
	s.wick_inset_px = float(k["cursor_wick_inset_px"])
	return s


## A StyleBoxFlat with the tide-notch chamfer (corner_detail 1 turns a radius into a 45° cut).
static func notch_flat(fill: Color, chamfer: int) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = fill
	s.corner_detail = 1
	s.corner_radius_top_left = chamfer
	s.corner_radius_bottom_right = chamfer
	s.anti_aliasing = false
	return s


static func _label(t: Theme, colors: Dictionary, k: Dictionary) -> void:
	t.set_color(&"font_color", &"Label", colors[&"text"])
	t.set_color(&"font_shadow_color", &"Label", colors[&"shadow"])
	t.set_color(&"font_outline_color", &"Label", colors[&"outline"])
	t.set_constant(&"shadow_offset_x", &"Label", 0)
	t.set_constant(&"shadow_offset_y", &"Label", int(k["shadow_offset_y_px"]))
	t.set_constant(&"shadow_outline_size", &"Label", int(k["shadow_blur_px"]))


static func _panels(t: Theme, colors: Dictionary, k: Dictionary) -> void:
	var big := panel_style(colors, k, int(k["chamfer_px"]))
	t.set_stylebox(&"panel", &"PanelContainer", big)
	t.set_stylebox(&"panel", &"Panel", big)
	var small := panel_style(colors, k, int(k["chamfer_small_px"]))
	t.set_stylebox(&"panel", &"TooltipPanel", small)
	t.set_stylebox(&"cursor", PALETTE_TYPE, cursor_style(colors, k))
	t.set_color(&"font_color", &"TooltipLabel", colors[&"text"])
	var sep := StyleBoxLine.new()
	sep.color = colors[&"separator_white"]
	sep.thickness = int(k["line_px"])
	t.set_stylebox(&"separator", &"HSeparator", sep)
	t.set_constant(&"separation", &"HSeparator", int(k["line_px"]))


static func _buttons(t: Theme, colors: Dictionary, k: Dictionary) -> void:
	var chamfer := int(k["chamfer_small_px"])
	var normal := notch_flat(Color(colors[&"panel_raised"], 0.0), chamfer)
	var hover := notch_flat(colors[&"panel_raised"], chamfer)
	var focus := notch_flat(Color(colors[&"panel_raised"], 0.0), chamfer)
	focus.set_border_width_all(int(k["focus_px"]))
	focus.border_color = colors[&"focus_gold"]
	focus.shadow_color = colors[&"focus_glow"]
	focus.shadow_size = int(k["focus_glow_px"])
	var pressed := notch_flat(colors[&"panel_raised"], chamfer)
	pressed.set_border_width_all(int(k["focus_px"]))
	pressed.border_color = colors[&"focus_gold"]
	for s: StyleBoxFlat in [normal, hover, focus, pressed]:
		s.content_margin_left = float(k["panel_margin_px"])
		s.content_margin_right = float(k["panel_margin_px"])
	var styles := {&"normal": normal, &"hover": hover, &"pressed": pressed, &"focus": focus, &"disabled": normal}
	for sname: StringName in styles:
		t.set_stylebox(sname, &"Button", styles[sname])
	for cname: StringName in [&"font_color", &"font_hover_color", &"font_focus_color", &"font_pressed_color"]:
		t.set_color(cname, &"Button", colors[&"text"])
	t.set_color(&"font_disabled_color", &"Button", colors[&"text_disabled"])


static func _gauges(t: Theme, colors: Dictionary, k: Dictionary) -> void:
	var back := StyleBoxFlat.new()
	back.bg_color = colors[&"gauge_back"]
	back.set_border_width_all(int(k["line_px"]))
	back.border_color = colors[&"gauge_border"]
	back.anti_aliasing = false
	var fill := StyleBoxFlat.new()
	fill.bg_color = colors[&"hp"]
	fill.anti_aliasing = false
	t.set_stylebox(&"background", &"ProgressBar", back)
	t.set_stylebox(&"fill", &"ProgressBar", fill)
	t.set_color(&"font_color", &"ProgressBar", colors[&"text"])


static func _scrollbars(t: Theme, colors: Dictionary, k: Dictionary) -> void:
	for type: StringName in [&"VScrollBar", &"HScrollBar"]:
		var track := StyleBoxFlat.new()
		track.bg_color = colors[&"separator_white"]
		track.set_content_margin_all(float(k["scroll_px"]) * 0.5)
		var grab := StyleBoxFlat.new()
		grab.bg_color = colors[&"line_gold"]
		var grab_hi := StyleBoxFlat.new()
		grab_hi.bg_color = colors[&"focus_gold"]
		t.set_stylebox(&"scroll", type, track)
		t.set_stylebox(&"scroll_focus", type, track)
		t.set_stylebox(&"grabber", type, grab)
		t.set_stylebox(&"grabber_highlight", type, grab_hi)
		t.set_stylebox(&"grabber_pressed", type, grab_hi)


static func _variations(t: Theme, cfg: Dictionary, colors: Dictionary, k: Dictionary, fonts: Dictionary) -> void:
	var variations: Dictionary = cfg.get("variations", {})
	var embolden := float(cfg.get("serif_semibold_embolden", 0.0))
	for vname: Variant in variations:
		var v: Dictionary = variations[vname]
		var type := StringName(str(vname))
		t.set_type_variation(type, StringName(str(v.get("base", "Label"))))
		if v.has("font"):
			var base_font: FontFile = fonts.get(StringName(str(v["font"])), null)
			var fv := _variation(base_font, v, embolden)
			t.set_font(&"font", type, fv)
		if v.has("size"):
			t.set_font_size(&"font_size", type, int(v["size"]))
		if v.has("color"):
			t.set_color(&"font_color", type, colors[StringName(str(v["color"]))])
		if bool(v.get("outline", false)):
			t.set_constant(&"outline_size", type, int(k["damage_outline_px"]))
			t.set_color(&"font_outline_color", type, colors[&"outline"])
		if v.has("chamfer"):
			t.set_stylebox(&"panel", type, panel_style(colors, k, int(k[str(v["chamfer"])])))


static func _variation(base_font: FontFile, v: Dictionary, embolden: float) -> FontVariation:
	var fv := FontVariation.new()
	fv.base_font = base_font
	var features: Dictionary = {}
	var ts := TextServerManager.get_primary_interface()
	if bool(v.get("tabular", false)):
		features[ts.name_to_tag("tnum")] = 1
		features[ts.name_to_tag("lnum")] = 1
	if bool(v.get("small_caps", false)):
		features[ts.name_to_tag("smcp")] = 1
	fv.opentype_features = features
	if bool(v.get("semibold", false)):
		fv.variation_embolden = embolden
	fv.spacing_glyph = int(v.get("spacing_glyph", 0))
	return fv


static func _load_fonts(cfg: Dictionary) -> Dictionary:
	var out: Dictionary = {}
	var paths: Dictionary = cfg.get("fonts", {})
	for fname: Variant in paths:
		var f := load(str(paths[fname])) as FontFile
		if f == null:
			push_error("HymnThemeBuilder: cannot load font %s" % paths[fname])
		out[StringName(str(fname))] = f
	return out


## Plain-data summary of a theme (colors, constants, sizes, fonts, style properties) used by the
## drift test to compare the saved .tres with a fresh build.
static func fingerprint(t: Theme) -> Dictionary:
	var out: Dictionary = {"default_font_size": t.default_font_size, "default_font": _font_print(t.default_font)}
	for type: StringName in t.get_type_list():
		var row: Dictionary = {"variation": String(t.get_type_variation_base(type))}
		for cname in t.get_color_list(type):
			row["c:" + cname] = t.get_color(cname, type).to_html()
		for cname in t.get_constant_list(type):
			row["k:" + cname] = t.get_constant(cname, type)
		for cname in t.get_font_size_list(type):
			row["s:" + cname] = t.get_font_size(cname, type)
		for cname in t.get_font_list(type):
			row["f:" + cname] = _font_print(t.get_font(cname, type))
		for cname in t.get_stylebox_list(type):
			row["b:" + cname] = _style_print(t.get_stylebox(cname, type))
		out[String(type)] = row
	return out


static func _font_print(f: Font) -> String:
	if f is FontVariation:
		var fv := f as FontVariation
		var base := fv.base_font.resource_path if fv.base_font != null else ""
		var tags: Array = fv.opentype_features.keys()
		tags.sort()
		var feats := ",".join(tags.map(func(t: Variant) -> String: return "%s=%s" % [t, fv.opentype_features[t]]))
		return "%s|%s|%s|%d" % [base, feats, str(fv.variation_embolden), fv.spacing_glyph]
	return f.resource_path if f != null else ""


static func _style_print(s: StyleBox) -> String:
	var parts: PackedStringArray = [s.get_class()]
	for p in s.get_property_list():
		if int(p["usage"]) & PROPERTY_USAGE_STORAGE and String(p["name"]) != "script":
			parts.append("%s=%s" % [p["name"], str(s.get(p["name"]))])
	return ";".join(parts)
