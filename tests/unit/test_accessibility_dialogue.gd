extends TestCase
## M2-UI-12: the dialogue accessibility settings. text_speed maps onto the dialogue box's range
## (DialogueTextSettings, text_box.json) and dialogue_backing onto a band alpha; both are rows on
## the Accessibility page. The box's side is M2-ARC-07 (Architect).


func test_text_speed_maps_onto_the_box_range() -> void:
	var s := UiSettings.new()
	var box := DialogueTextSettings.load_default()
	var cps := box.chars_per_sec
	assert_eq(s.get_value(UiSettings.TEXT_SPEED), "normal", "the default keeps the box's own speed")
	assert_true(is_equal_approx(s.dialogue_chars_per_sec(cps, box.min_chars_per_sec, box.max_chars_per_sec), cps))
	s.set_value(UiSettings.TEXT_SPEED, "slow")
	var slow := s.dialogue_chars_per_sec(cps, box.min_chars_per_sec, box.max_chars_per_sec)
	s.set_value(UiSettings.TEXT_SPEED, "fast")
	var fast := s.dialogue_chars_per_sec(cps, box.min_chars_per_sec, box.max_chars_per_sec)
	assert_true(slow < cps and cps < fast, "slow < normal < fast")
	assert_true(slow >= box.min_chars_per_sec and fast <= box.max_chars_per_sec, "inside the box's range")
	s.set_value(UiSettings.TEXT_SPEED, "instant")
	assert_eq(s.dialogue_chars_per_sec(cps, box.min_chars_per_sec, box.max_chars_per_sec), 0.0, "0 = instant")


func test_the_backing_alpha_follows_the_option() -> void:
	var s := UiSettings.new()
	assert_true(s.dialogue_backing_alpha() > 0.0, "a soft band by default")
	s.set_value(UiSettings.DIALOGUE_BACKING, "off")
	assert_eq(s.dialogue_backing_alpha(), 0.0)
	s.set_value(UiSettings.DIALOGUE_BACKING, "solid")
	var solid := s.dialogue_backing_alpha()
	s.set_value(UiSettings.DIALOGUE_BACKING, "soft")
	assert_true(solid > s.dialogue_backing_alpha() and solid <= 1.0)


func test_both_are_rows_on_the_accessibility_page() -> void:
	var m := AccessibilityMenuModel.new(UiSettings.new(), "")
	assert_true(m.row_ids().has(UiSettings.TEXT_SPEED))
	assert_true(m.row_ids().has(UiSettings.DIALOGUE_BACKING))
	assert_eq(m.value_text(UiSettings.TEXT_SPEED), tr("SET_TEXT_SPEED_NORMAL"))
	assert_eq(m.value_text(UiSettings.DIALOGUE_BACKING), tr("SET_BACKING_SOFT"))
	m.set_cursor(m.row_ids().find(UiSettings.TEXT_SPEED))
	assert_true(m.cycle(1))
	assert_eq(m.value_text(UiSettings.TEXT_SPEED), tr("SET_TEXT_SPEED_FAST"))
	assert_eq(m.help_key(), "SET_TEXT_SPEED_HELP")
