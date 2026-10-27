extends TestCase
## M2-UI-100: narration and #vo lines read as subtitles, so the box stops covering the frame they speak over (the
## prologue's vigil): a low, faint panel over the lower letterbox band and an outlined line. Spoken lines keep the
## scene's panel. Data: dialogue_assist.json subtitles.voice_over.

const BOX := "res://game/ui/dialogue/dialogue_box.tscn"
const LINE_KEY := &"DLG_PROLOGUE_DEAD_CITY_001"
## CutsceneOverlay's letterbox at 1080 (sequencer.json letterbox_ratio 0.11).
const LETTERBOX_PX := 0.11 * 1080.0

var made: Array[Node] = []


func before_each() -> void:
	UiSettings.set_shared(UiSettings.new())


func test_narration_is_a_low_faint_subtitle_and_a_spoken_line_brings_the_panel_back() -> void:
	var box := _box()
	var panel := box.get_node(^"Panel") as Control
	var body := box.get_node(^"%Body") as Label
	var spoken := box.spoken_panel_rest()
	var vo := _vo()
	box.show_text(&"", LINE_KEY, &"", false, &"rhen")
	_settle(box)
	assert_true(box.is_voice_over(), "narration is voice-over")
	assert_eq(panel.offset_bottom, -float(vo["bottom_px"]), "near the screen's bottom edge")
	assert_eq(panel.offset_bottom - panel.offset_top, float(vo["height_px"]), "a short panel")
	assert_true(
		panel.offset_top > spoken.x, "it covers less of the frame than a spoken line's panel (%s)" % panel.offset_top
	)
	var notch := panel.get_theme_stylebox(&"panel") as TideNotchStyleBox
	assert_true(notch != null, "the theme's panel, faded")
	assert_true(is_equal_approx(notch.fill_top.a, float(vo["panel_alpha"])), "a faint panel")
	assert_true(is_equal_approx(notch.fill_bottom.a, float(vo["panel_alpha"])))
	assert_eq(body.get_theme_constant(&"outline_size"), int(vo["outline_px"]), "the line is outlined")
	box.show_text(&"asha", LINE_KEY)
	_settle(box)
	assert_false(box.is_voice_over(), "a spoken line")
	assert_eq(Vector2(panel.offset_top, panel.offset_bottom), spoken, "the scene's panel again")
	assert_false(panel.has_theme_stylebox_override(&"panel"), "the theme's panel")
	assert_false(body.has_theme_constant_override(&"outline_size"))
	_done()


func test_a_vo_tagged_line_with_a_speaker_is_a_subtitle_too() -> void:
	var box := _box()
	var step := DialogueStep.new()
	step.speaker = &"rhen"
	step.text_key = LINE_KEY
	step.tags = PackedStringArray([DialogueBox.TAG_VO])
	box.show_line(step)
	_settle(box)
	assert_true(box.is_voice_over())
	var panel := box.get_node(^"Panel") as Control
	assert_eq(panel.offset_bottom, -float(_vo()["bottom_px"]))
	_done()


func test_the_subtitle_mostly_sits_on_the_letterbox_band() -> void:
	var vo := _vo()
	var above_band := float(vo["height_px"]) + float(vo["bottom_px"]) - LETTERBOX_PX
	assert_true(above_band < float(vo["height_px"]) * 0.25, "at most a quarter of it rises above the band")
	assert_true(float(vo["panel_alpha"]) <= 0.4, "faint enough for the frame to read through")
	_done()


func test_the_box_fades_in_to_the_subtitle_place() -> void:
	var box := _box()
	box.visible = false
	box.visible = true
	box.show_text(&"", LINE_KEY, &"", false, &"rhen")
	(box.get_node(^"DialogueAssist") as DialogueAssist).step(0.0)
	box.motion().finish()
	var panel := box.get_node(^"Panel") as Control
	assert_eq(panel.offset_bottom, -float(_vo()["bottom_px"]), "the open transition lands on the subtitle's rest")
	_done()


func _vo() -> Dictionary:
	return (DialogueAssist.load_data()["subtitles"] as Dictionary)["voice_over"] as Dictionary


## What a frame does: the assist restyles on a new line, and any transition ends.
func _settle(box: DialogueBox) -> void:
	(box.get_node(^"DialogueAssist") as DialogueAssist).step(0.0)
	box.motion().finish()


func _box() -> DialogueBox:
	var box := (load(BOX) as PackedScene).instantiate() as DialogueBox
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(box)
	box.set_process(false)
	made.append(box)
	return box


func _done() -> void:
	for n in made:
		if is_instance_valid(n) and n.get_parent() != null:
			n.get_parent().remove_child(n)
			n.free()
	made.clear()
	UiSettings.set_shared(null)
