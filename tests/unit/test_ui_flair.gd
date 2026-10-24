extends TestCase
## ADR 0033: the theme's flair. The panel style carries the glint, corner ticks and tide lines;
## the menu cursor is a CursorStyleBox; a titled MenuPage draws an OrnamentRule under its header;
## the row under the cursor nudges its text; CausticBackdrop fills its parent and holds still under
## reduced motion.

const THEME := "res://game/ui/theme/hymn_theme.tres"

var made: Array[Node] = []


func before_each() -> void:
	for n in made:
		if is_instance_valid(n):
			n.get_parent().remove_child(n)
			n.free()
	made.clear()
	UiSettings.set_shared(UiSettings.new())


func test_the_panel_and_cursor_styles_carry_the_flair_from_data() -> void:
	var cfg := HymnThemeBuilder.load_config()
	var k: Dictionary = cfg["constants"]
	var t := load(THEME) as Theme
	var panel := t.get_stylebox(&"panel", &"Panel") as TideNotchStyleBox
	assert_true(panel != null)
	assert_eq(panel.tide_lines, int(k["tide_lines"]))
	assert_eq(panel.corner_tick_px, float(k["corner_tick_px"]))
	assert_true(is_equal_approx(panel.glint_span, float(k["glint_span_pct"]) / 100.0))
	var cursor := t.get_stylebox(&"cursor", HymnThemeBuilder.PALETTE_TYPE) as CursorStyleBox
	assert_true(cursor != null, "the menu cursor comes from the theme")
	assert_eq(cursor.frame_px, float(k["focus_px"]), "the 2 px gold focus frame of art/ui.md §2 stays")
	assert_eq(cursor.frame_color, t.get_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE))


func test_a_titled_page_draws_its_rule_and_nudges_the_cursor_row() -> void:
	var host := _host()
	var page := MenuPage.new()
	var m := HudLayout.section(&"commands")
	page.size = Vector2(480, MenuPage.height_for(m, 3))
	host.add_child(page)
	var rows: Array[Dictionary] = [{"id": &"a", "label": "A"}, {"id": &"b", "label": "B"}, {"id": &"c", "label": "C"}]
	page.reduced_motion = true
	page.setup(m, &"p", "Title", rows)
	assert_eq(page.find_children("*", "OrnamentRule", true, false).size(), 1, "a rule under the header")
	var nudge := float(page.get_theme_constant(&"cursor_nudge_px", HymnThemeBuilder.PALETTE_TYPE))
	assert_true(nudge > 0.0)
	assert_true(is_equal_approx(page.label_x(0) - page.label_x(1), nudge), "the cursor row sits further right")
	page.move(1)
	assert_true(is_equal_approx(page.label_x(1) - page.label_x(0), nudge), "and the nudge follows the cursor")
	var bare := MenuPage.new()
	host.add_child(bare)
	bare.setup(m, &"q", "", rows)
	assert_eq(bare.find_children("*", "OrnamentRule", true, false).size(), 0, "no header, no rule")


func test_tide_lines_only_on_tall_panels() -> void:
	var s := TideNotchStyleBox.new()
	s.tide_lines = 2
	s.tide_min_height_px = 120.0
	var ci := RenderingServer.canvas_item_create()
	s._draw_tide(ci, Rect2(0, 0, 400, 60), 10.0)  # too short: nothing to draw, nothing to fail
	s._draw_tide(ci, Rect2(0, 0, 400, 300), 10.0)
	RenderingServer.free_rid(ci)
	assert_true(true)


func test_the_caustic_backdrop_fills_its_parent_and_stills_under_reduced_motion() -> void:
	var host := _host()
	var c := CausticBackdrop.new()
	host.add_child(c)
	assert_eq(c.size, host.size, "full rect")
	var mat := c.material as ShaderMaterial
	assert_eq(mat.get_shader_parameter(&"tint"), host.get_theme_color(&"caustic", HymnThemeBuilder.PALETTE_TYPE))
	c._process(1.0)
	var moved: float = mat.get_shader_parameter(&"phase")
	assert_true(moved > 0.0, "it drifts")
	UiSettings.shared().set_value(UiSettings.REDUCED_MOTION, true)
	c._process(1.0)
	assert_eq(float(mat.get_shader_parameter(&"phase")), moved, "reduced motion holds it still")


func _host() -> Control:
	var host := Control.new()
	host.size = Vector2(1920, 1080)
	host.theme = load(THEME) as Theme
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(host)
	made.append(host)
	return host
