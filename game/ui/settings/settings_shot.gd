class_name SettingsShot
extends Control
## Capture driver for the settings shots (M2-UI-09, tests/screenshots/shots.json). It opens the
## Settings hub on its own UiSettings at the defaults, so the player's settings.cfg never moves a
## baseline, and saves nothing:
##   - "hub": the hub, the cursor on Accessibility;
##   - "accessibility": the Accessibility page with the text size at 130%, the cursor on Text size
##     (the page re-themes itself, so the shot shows the larger text the setting gives).

## Which view to stage: &"hub" or &"accessibility".
@export var view: StringName = &"hub"

var hub: SettingsMenu


func _ready() -> void:
	var settings := UiSettings.new()
	UiSettings.set_shared(settings)
	var back := ColorRect.new()
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.color = get_theme_color(&"panel_low", HymnThemeBuilder.PALETTE_TYPE)
	back.color.a = 1.0
	add_child(back)
	hub = SettingsMenu.new()
	hub.ui_settings = settings
	hub.save_path = ""
	add_child(hub)
	hub.handle_input(_ev(&"ui_down"))  # Graphics -> Accessibility
	if view != &"accessibility":
		return
	hub.handle_input(_ev(&"ui_accept"))
	hub.handle_input(_ev(&"ui_down"))  # Reduced motion -> Text size
	hub.handle_input(_ev(&"ui_right"))  # 115%
	hub.handle_input(_ev(&"ui_right"))  # 130%


func _ev(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev
