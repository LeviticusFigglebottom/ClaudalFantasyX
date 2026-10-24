extends TestCase
## M2-UI-30: cutscene and dialogue lines read at every text size. The box follows the text size,
## the speaker's name and the line take the theme's header and body sizes, a backing at the
## "Subtitle backing" alpha sits behind them, and the party's name colours stay apart and readable
## for every colour vision (Machado et al. 2009 deuteranopia, protanopia, tritanopia, severity 1;
## Oklab distance; WCAG contrast on the darkest panel), in both palettes.

const BOX := "res://game/ui/dialogue/dialogue_box.tscn"
const LONG := (
	"Lie still, please, and keep your hands open. I would like this to stay a small conversation,"
	+ " and I would like you to stay on that sand until the tide says otherwise."
)
const MIN_DISTANCE := 0.1
const MIN_CONTRAST := 4.5
const DEUT := [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]
const PROT := [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]
const TRIT := [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.304900]]
const NORMAL := [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]

var made: Array[Node] = []


func before_each() -> void:
	InputDriver.clear_screen()
	UiSettings.set_shared(UiSettings.new())


func test_the_name_and_line_take_the_theme_sizes_at_every_text_size() -> void:
	for scale: float in [1.0, 1.15, 1.3]:
		UiSettings.shared().set_value(UiSettings.TEXT_SCALE, scale)
		var box := _box()
		box.show_text(&"toma", StringName(LONG))
		box.skip_reveal()
		var name_label := box.get_node(^"%SpeakerName") as Label
		var body := box.get_node(^"%Body") as Label
		assert_eq(name_label.get_theme_font_size(&"font_size"), box.get_theme_font_size(&"font_size", &"HeaderLabel"))
		assert_eq(body.get_theme_font_size(&"font_size"), box.get_theme_font_size(&"font_size", &"BodyLabel"))
		var panel := box.get_node(^"Panel") as Control
		panel.reset_size()
		var r := panel.get_global_rect()
		assert_true(r.position.y >= 0.0, "%.2f: the panel stays on screen (top %.0f)" % [scale, r.position.y])
		assert_true(
			body.get_line_count() <= body.get_visible_line_count() or body.max_lines_visible < 0, "every line shows"
		)
		assert_true(
			body.size.y + 0.5 >= body.get_minimum_size().y,
			"%.2f: no line is cut (%.0f < %.0f)" % [scale, body.size.y, body.get_minimum_size().y]
		)
		_free()
	_done()


func test_a_text_size_change_reaches_an_open_box() -> void:
	var box := _box()
	var body := box.get_node(^"%Body") as Label
	var before := body.get_theme_font_size(&"font_size")
	UiSettings.shared().set_value(UiSettings.TEXT_SCALE, 1.3)
	assert_true(body.get_theme_font_size(&"font_size") > before, "the line grows with the setting")
	_done()


func test_the_backing_follows_the_subtitle_backing_setting() -> void:
	var box := _box()
	var backing := box.get_node(^"Panel/SubtitleBacking") as ColorRect
	assert_true(backing != null, "the backing is in the panel, behind the text")
	assert_eq(backing.get_index(), 0)
	for option: Variant in UiSettings.shared().options(UiSettings.DIALOGUE_BACKING):
		UiSettings.shared().set_value(UiSettings.DIALOGUE_BACKING, option)
		var a := UiSettings.shared().dialogue_backing_alpha()
		assert_between(backing.color.a, a - 0.001, a + 0.001, "%s: the backing's alpha" % option)
		assert_eq(backing.visible, a > 0.0)
	_done()


func test_names_are_gold_and_lines_are_text_for_every_speaker() -> void:
	var box := _box()
	var name_label := box.get_node(^"%SpeakerName") as Label
	var body := box.get_node(^"%Body") as Label
	var assist := box.get_node(^"DialogueAssist") as DialogueAssist
	for id: StringName in [&"rhen", &"asha", &"vendor"]:
		box.show_text(id, &"...")
		assist.step(0.0)
		assert_eq(
			name_label.get_theme_color(&"font_color"), box.get_theme_color(&"focus_gold", HymnThemeBuilder.PALETTE_TYPE)
		)
		assert_eq(body.get_theme_color(&"font_color"), box.get_theme_color(&"text", HymnThemeBuilder.PALETTE_TYPE))
	_done()


func test_the_subtitle_colours_stay_apart_and_readable_for_every_colour_vision() -> void:
	var sub := DialogueAssist.load_data()["subtitles"] as Dictionary
	var roles: Array[StringName] = [StringName(str(sub["name_role"])), StringName(str(sub["body_role"]))]
	for r: Variant in (sub["speaker_roles"] as Dictionary).values():
		if not roles.has(StringName(str(r))):
			roles.append(StringName(str(r)))
	for palette: String in ["standard", "colorblind"]:
		var s := UiSettings.new()
		s.set_value(UiSettings.PALETTE, palette)
		var t := HymnThemeBuilder.build(s.theme_config())
		var night := Color(t.get_color(&"panel_deep", HymnThemeBuilder.PALETTE_TYPE), 1.0)
		for i in roles.size():
			var a := t.get_color(roles[i], HymnThemeBuilder.PALETTE_TYPE)
			var c := _contrast(Color(a, 1.0), night)
			assert_true(c >= MIN_CONTRAST, "%s %s reads on the panel (%.2f:1)" % [palette, roles[i], c])
			for j in range(i + 1, roles.size()):
				var b := t.get_color(roles[j], HymnThemeBuilder.PALETTE_TYPE)
				for m: Array in [NORMAL, DEUT, PROT, TRIT]:
					var d := _oklab(_sim(a, m)).distance_to(_oklab(_sim(b, m)))
					assert_true(d >= MIN_DISTANCE, "%s %s vs %s apart (%.3f)" % [palette, roles[i], roles[j], d])
	_done()


func _box() -> DialogueBox:
	var box := (load(BOX) as PackedScene).instantiate() as DialogueBox
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(box)
	made.append(box)
	return box


func _free() -> void:
	for n in made:
		if is_instance_valid(n) and n.get_parent() != null:
			n.get_parent().remove_child(n)
			n.free()
	made.clear()


func _done() -> void:
	_free()
	UiSettings.set_shared(null)


static func _sim(c: Color, m: Array) -> Color:
	return TestColorVision.sim(c, m)


static func _oklab(lin: Color) -> Vector3:
	return TestColorVision.oklab(lin)


static func _contrast(a: Color, b: Color) -> float:
	return TestColorVision.contrast(a, b)
