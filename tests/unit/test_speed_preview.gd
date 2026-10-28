extends TestCase
## The Accessibility page's live speed previews (SpeedPreview; the options and quality-of-life pass): on the
## text speed row a sample line reveals at that setting's dialogue speed (instant shows it whole); on the battle
## speed row a pip crosses in one action's hold at that speed, with the time in words (under reduced motion only
## the words); any other row hides it. The runner runs no frames and has no after_each.

var settings: UiSettings
var page: AccessibilityMenu


func before_each() -> void:
	settings = UiSettings.new()
	page = AccessibilityMenu.new(settings, "")
	var tree := Engine.get_main_loop() as SceneTree
	(tree.current_scene if tree.current_scene != null else tree.root).add_child(page)


func test_the_text_speed_row_reveals_the_sample_at_its_speed() -> void:
	_to(UiSettings.TEXT_SPEED)
	var p := page.preview
	assert_true(p.visible and p.kind == SpeedPreview.TEXT, "shown on the text speed row")
	var box := DialogueTextSettings.load_default()
	var normal := settings.dialogue_chars_per_sec(box.chars_per_sec, box.min_chars_per_sec, box.max_chars_per_sec)
	assert_eq(p.cps, normal, "the dialogue box's own speed")
	p._process(0.1)
	assert_true(p.progress() > 0.0 and p.progress() < 1.0, "mid-reveal")
	page.model.cycle(1)  # normal -> fast
	assert_true(p.cps > normal, "a faster setting reveals faster")
	assert_eq(p.t, 0.0, "and starts again")
	settings.set_value(UiSettings.TEXT_SPEED, "instant")
	page.model.changed.emit()
	assert_eq(p.progress(), 1.0, "instant shows the whole line")
	_done()


func test_the_battle_speed_row_crosses_in_one_actions_hold() -> void:
	_to(UiSettings.BATTLE_SPEED)
	var p := page.preview
	assert_eq(p.kind, SpeedPreview.BATTLE)
	var hold := HudLayout.num(HudLayout.section(&"pacing"), "action_hold_sec")
	assert_between(p.cross_sec, hold - 0.0001, hold + 0.0001, "normal speed")
	settings.set_value(UiSettings.BATTLE_SPEED, 2.0)
	page.model.changed.emit()
	assert_between(p.cross_sec, hold * 0.5 - 0.0001, hold * 0.5 + 0.0001, "twice as fast, half the time")
	assert_true(p.get(&"_sample").text.contains("%.1f" % (hold * 0.5)), "in words")
	assert_true(p.get(&"_track").visible)
	settings.set_value(UiSettings.REDUCED_MOTION, true)
	page.model.changed.emit()
	assert_false(p.get(&"_track").visible, "reduced motion: the words only")
	_done()


func test_other_rows_hide_it() -> void:
	_to(UiSettings.REDUCED_MOTION)
	assert_false(page.preview.visible)
	assert_eq(page.preview.kind, &"")
	_done()


func _to(row: StringName) -> void:
	page.model.set_cursor(page.model.row_ids().find(row))


func _done() -> void:
	page.get_parent().remove_child(page)
	page.free()
