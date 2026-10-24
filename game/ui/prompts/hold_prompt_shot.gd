class_name HoldPromptShot
extends Control
## Capture driver for the cutscene_hold_prompt shot (M3-C09-05, tests/screenshots/shots.json): the
## Ebbing's held-input prompt ("Hold to raise the staff", the field_interact key) faded in and at
## rest, at the bottom margin Ch9's data gives it, over a night backdrop.

const PROMPT_KEY := "FIELD_PROMPT_CH09_RAISE_STAFF"
const CH09_FIELD := "res://game/data/flow/ch09_field.json"

var prompt: HoldPrompt


func _ready() -> void:
	var back := ColorRect.new()
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"outline", HymnThemeBuilder.PALETTE_TYPE)
	add_child(back)
	UiSettings.set_shared(UiSettings.new())
	FieldInput.ensure_actions()
	InputNames.using_pad = false
	var hold := (JSON.parse_string(FileAccess.get_file_as_string(CH09_FIELD)) as Dictionary)["hold"] as Dictionary
	prompt = HoldPrompt.new()
	prompt.action = StringName(str(hold["action"]))
	prompt.bottom_px = float(hold["bottom_px"])
	add_child(prompt)
	prompt.show_prompt(PROMPT_KEY)
	prompt.advance(float(HoldPrompt.load_data()["fade_sec"]))
	prompt.set_process(false)  # stays at rest, fully in, for the capture
