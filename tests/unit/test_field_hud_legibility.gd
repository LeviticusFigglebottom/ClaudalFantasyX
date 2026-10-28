extends TestCase
## Lead 2026-10-28 (field HUD pass over the dressed Act I areas, shots `field_hud_over_*`): the
## overlays that show together when the field first takes input never cover each other, and the
## words that float over the world without a plate carry an outline.

const SIZES: Array[Vector2] = [
	Vector2(1920, 1080), Vector2(2560, 1080), Vector2(1920, 1200), Vector2(1440, 1080), Vector2(3440, 1440)
]


## The area title and the first tip both show on the field's first input: a long name (Corrow's
## night) ran under the tip card when it sat beside the band.
func test_the_tip_card_sits_clear_of_the_area_title_at_every_aspect() -> void:
	var tip := TutorialTips.load_data()["panel"] as Dictionary
	var title := AreaTitleCard.load_data()
	for size in SIZES:
		var card := HudLayout.pinned_rect(tip, size)
		for part: String in ["band", "name", "rule"]:
			var r := HudLayout.pinned_rect(title[part] as Dictionary, size)
			assert_false(card.intersects(r), "tip card vs title %s at %s" % [part, size])
		var line := HudLayout.pinned_rect(ObjectiveHud.load_data()["panel"] as Dictionary, size)
		assert_false(card.intersects(line), "tip card vs objective line at %s" % size)


## Every Act I location's name fits the title's name rect on one line at the title font.
func test_every_act1_location_name_fits_the_title() -> void:
	var card := AreaTitleCard.new()
	card.theme = load("res://game/ui/theme/hymn_theme.tres") as Theme
	(Engine.get_main_loop() as SceneTree).root.add_child(card)
	var width := (AreaTitleCard.load_data()["name"] as Dictionary)["rect"][2] as float
	var font := card.get_theme_font(&"font", &"TitleLabel")
	var font_size := card.get_theme_font_size(&"font_size", &"TitleLabel")
	var reg := LocationRegistry.load_default()
	var checked := 0
	for chapter in range(1, 10):
		for id: StringName in reg.location_ids():
			if String(id).begins_with("ch%02d/" % chapter):
				var w := font.get_string_size(tr(reg.name_key_of(id)), HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x
				assert_true(w <= width, "%s's name (%d px) fits %d px" % [id, w, width])
				checked += 1
	assert_true(checked > 5, "the Act I locations were read")
	card.queue_free()


## The cue's distance words float over the world with no plate: they carry the outline.
func test_the_cue_words_carry_an_outline() -> void:
	var cue := ObjectiveHud.load_data()["cue"] as Dictionary
	assert_true(HudLayout.num(cue, "label_outline_px") > 0.0, "an outline on the cue's words")
