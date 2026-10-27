extends TestCase
## M2-FP-1001: a cutscene's choices follow the player's text size, like every menu outside battle (M2-UI-09):
## the panel takes the scaled theme, and the configured button size scales with it.

const FONT_SIZE := 30
const LARGER := 1.3

var saved: float


func before_each() -> void:
	saved = UiSettings.shared().text_scale()


func test_choices_grow_with_the_text_size() -> void:
	var host := (Engine.get_main_loop() as SceneTree).current_scene
	assert_true(UiSettings.shared().set_value(UiSettings.TEXT_SCALE, LARGER), "130% is a text size option")
	var c := CutsceneChoices.new({"font_size": FONT_SIZE})
	host.add_child(c)
	var opt := DialogueOption.new()
	opt.text_key = "UI_OK"
	opt.index = 0
	c.show_options([opt] as Array[DialogueOption])
	var b := c.find_children("*", "Button", true, false)[0] as Button
	assert_eq(b.get_theme_font_size(&"font_size"), roundi(FONT_SIZE * LARGER), "the button at the player's size")
	assert_true(c.theme != null, "the panel follows the scaled theme")
	UiSettings.shared().set_value(UiSettings.TEXT_SCALE, saved)
	host.remove_child(c)
	c.free()
